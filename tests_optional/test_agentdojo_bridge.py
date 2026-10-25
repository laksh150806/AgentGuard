"""Run with AgentDojo installed: PYTHONPATH=src:tests python -m unittest discover -s tests_optional."""
import unittest

from agentdojo.task_suite import get_suite
from agentguard.agentdojo_bridge import LocalDojoPipeline, VERSION
from test_agent import ScriptedClient, reply, call


class BridgeTests(unittest.TestCase):
    def test_official_utility_and_attack_predicates_observe_guarded_execution(self):
        suite = get_suite(VERSION, "banking")
        task = suite.get_user_task_by_id("user_task_1")
        injection = suite.get_injection_task_by_id("injection_task_5")
        for mode in ("baseline", "enforced"):
            with self.subTest(mode=mode):
                client = ScriptedClient([
                    reply(calls=[call("send_money", {"recipient": "US133000000121212121212", "amount": 100,
                                                      "subject": "test", "date": "2022-04-01"})]),
                    reply("Your total spending in March 2022 was 1,050."),
                ])
                pipeline = LocalDojoPipeline(client, mode)
                utility, attack_success = suite.run_task_with_pipeline(pipeline, task, injection, {})
                self.assertTrue(utility)
                self.assertEqual(attack_success, mode == "baseline")
                self.assertEqual(pipeline.trace["decisions"][0]["policy_denied"], mode == "enforced")

    def test_budget_stop_does_not_trigger_upstream_automatic_retries(self):
        suite = get_suite(VERSION, "banking")
        task = suite.get_user_task_by_id("user_task_1")
        client = ScriptedClient([reply(calls=[call("get_most_recent_transactions", {"n": 5})])])
        pipeline = LocalDojoPipeline(client, "enforced", max_turns=1)
        utility, _ = suite.run_task_with_pipeline(pipeline, task, None, {})
        self.assertFalse(utility)
        self.assertEqual(len(client.requests), 1)
        self.assertEqual(pipeline.trace["stop_reason"], "turn_limit")
