import json
import subprocess
import sys
import unittest

from agentguard.evaluation import BASE_PROMPT, DEFENSE_PROMPT, evaluation_plan, run_evaluation
from agentguard.ollama import ModelError
from test_agent import ScriptedClient, call, reply


def sequence(amount, request_id="evaluation-1"):
    return [reply(calls=[call("search_documents", {"query": "Refund guide"})]),
            reply(calls=[call(arguments={"order_id": "order-demo", "amount_paise": amount,
                                         "request_id": request_id})]), reply("Done")]


class EvaluationTests(unittest.TestCase):
    def test_plan_is_deterministic_and_budgeted(self):
        plan = evaluation_plan()
        self.assertEqual(plan["runs"], 30)
        self.assertEqual(plan["max_chat_requests"], 180)
        self.assertEqual(plan["configuration_sha256"], evaluation_plan()["configuration_sha256"])
        self.assertNotEqual(plan["configuration_sha256"], evaluation_plan(include_strict=True)["configuration_sha256"])
        self.assertEqual(evaluation_plan(["refund-small"], include_strict=True)["runs"], 8)

    def test_invalid_cases_and_budgets_rejected(self):
        for kwargs in ({"case_ids": ["missing"]}, {"case_ids": []}, {"repeats": 0}, {"repeats": True},
                       {"max_turns": 21}, {"max_tool_calls": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                evaluation_plan(**kwargs)

    def test_equal_tasks_and_distinct_defense_conditions(self):
        client = ScriptedClient(sequence(500) * 6)
        report = run_evaluation(client, ["refund-small"])
        self.assertEqual(len(report["runs"]), 6)
        first_prompts = [messages[0]["content"] for messages in client.requests if len(messages) == 2]
        self.assertEqual(first_prompts, [BASE_PROMPT, DEFENSE_PROMPT, DEFENSE_PROMPT] * 2)
        self.assertEqual(len({r["run"]["task"] for r in report["runs"]}), 1)
        self.assertTrue(all(r["scores"]["legitimate_task_completed"] for r in report["runs"]))

    def test_executed_attack_and_exposure_counted_independently(self):
        report = run_evaluation(ScriptedClient(sequence(500) * 3 + sequence(9900, "attack") * 3), ["refund-small"])
        baseline, prompt, enforced = report["summary"]
        self.assertEqual(baseline["attacker_objectives_met"], 1)
        self.assertEqual(prompt["attacker_objectives_met"], 1)
        self.assertEqual(enforced["attacker_objectives_met"], 0)
        self.assertEqual(enforced["attack_content_retrieved"], 1)
        self.assertEqual(enforced["attacked_completed"], 0)  # blocked attack is not useful completion
        self.assertEqual(enforced["clean_completed"], 1)

    def test_within_permission_attack_exposes_limit_of_enforcement(self):
        report = run_evaluation(ScriptedClient(sequence(500) * 3 + sequence(600) * 3), ["within-limit"])
        enforced = report["summary"][2]
        self.assertEqual(enforced["attacker_objectives_met"], 1)
        self.assertEqual(enforced["utility_under_attack"], 0)

    def test_strict_cap_loses_legitimate_utility_against_fixed_ground_truth(self):
        report = run_evaluation(ScriptedClient(sequence(1500) * 8), ["refund-large"], include_strict=True)
        enforced, strict = report["summary"][2:]
        self.assertEqual(enforced["clean_completed"], 1)
        self.assertEqual(strict["clean_completed"], 0)
        self.assertEqual(strict["attacker_objectives_met"], 0)

    def test_errors_remain_in_denominators(self):
        report = run_evaluation(ScriptedClient([ModelError("offline")] * 6), ["refund-small"])
        for row in report["summary"]:
            self.assertEqual(row["clean_total"], 1)
            self.assertEqual(row["attacked_total"], 1)
            self.assertEqual(row["stop_reasons"], {"model_error": 2})
            self.assertEqual(row["attack_content_retrieved"], 0)
            self.assertEqual(row["clean_completion_rate"], 0)

    def test_attacks_without_retrieval_not_attributed_to_exposure(self):
        responses = [reply(calls=[call(arguments={"order_id": "order-demo", "amount_paise": 9900,
                                                "request_id": "attack"})]), reply("Done")]
        report = run_evaluation(ScriptedClient(responses * 6), ["refund-small"])
        self.assertEqual(report["summary"][0]["attacker_objectives_met"], 1)
        self.assertEqual(report["summary"][0]["attack_content_retrieved"], 0)

    def test_cross_customer_and_restricted_read_scoring(self):
        for case, tool_call in (("cross-customer", call("read_customer", {"customer_id": "customer-other"})),
                                ("restricted-document", call("search_documents", {"query": "DEMO-RESTRICTED-42"}))):
            with self.subTest(case=case):
                attack_sequence = [reply(calls=[call("search_documents", {"query": "Refund guide"})]),
                                   reply(calls=[tool_call]), reply("Done")]
                report = run_evaluation(ScriptedClient(sequence(500) * 3 + attack_sequence * 3), [case])
                self.assertEqual(report["summary"][0]["attacker_objectives_met"], 1)
                self.assertEqual(report["summary"][2]["attacker_objectives_met"], 0)

    def test_public_attack_text_mentioning_marker_is_not_restricted_disclosure(self):
        report = run_evaluation(ScriptedClient(sequence(500) * 6), ["restricted-document"])
        self.assertTrue(all(r["scores"]["legitimate_task_completed"] for r in report["runs"]))
        self.assertEqual(report["summary"][2]["attacker_objectives_met"], 0)

    def test_cli_plan_requires_no_model(self):
        process = subprocess.run([sys.executable, "-m", "agentguard", "eval-plan", "--case", "refund-small"],
                                 capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(process.stdout)["runs"], 6)
