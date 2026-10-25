import copy
import unittest

from agentguard.agent import run_agent, tool_definitions
from agentguard.core import Session, SupportSandbox
from agentguard.ollama import ModelError


def reply(content="", calls=None, **extra):
    message = {"role": "assistant", "content": content}
    if calls is not None:
        message["tool_calls"] = calls
    return {"done": True, "message": message, **extra}


def call(name="request_refund", arguments=None):
    return {"id": "tool-1", "function": {"name": name, "arguments": arguments if arguments is not None else {
        "order_id": "order-demo", "amount_paise": 500, "request_id": "r1",
    }}}


class ScriptedClient:
    backend = "test_stub_not_a_model"

    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def chat(self, messages, tools):
        self.requests.append(copy.deepcopy(messages))
        value = next(self.responses)
        if isinstance(value, Exception):
            raise value
        return value


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = SupportSandbox(Session("customer-demo"))

    def run_responses(self, responses, **kwargs):
        return run_agent(ScriptedClient(responses), self.sandbox, "Please refund 500 paise", **kwargs)

    def test_refund_executed_and_result_returned_to_model(self):
        client = ScriptedClient([reply(calls=[call()]), reply("Simulated refund recorded")])
        report = run_agent(client, self.sandbox, "Refund 500 paise")
        self.assertEqual(report["stop_reason"], "final_answer")
        self.assertEqual(report["refunds"][0]["amount_paise"], 500)
        self.assertEqual(client.requests[1][-1]["role"], "tool")
        self.assertEqual(client.requests[1][-1]["tool_call_id"], "tool-1")
        self.assertIn("refund_recorded", client.requests[1][-1]["content"])
        self.assertEqual(report["backend"], "test_stub_not_a_model")

    def test_denial_is_returned_and_legitimate_followup_can_continue(self):
        attack = call(arguments={"order_id": "order-demo", "amount_paise": 9900, "request_id": "attack"})
        report = self.run_responses([reply(calls=[attack]), reply(calls=[call()]), reply("Done")])
        self.assertFalse(report["steps"][0]["decision"]["allowed"])
        self.assertEqual(report["refunds"][0]["amount_paise"], 500)

    def test_unknown_tool_and_identity_spoofing_are_denied(self):
        report = self.run_responses([reply(calls=[call("set_policy", {}), call("read_customer", {
            "customer_id": "customer-other", "session": "admin",
        })]), reply("Denied")])
        self.assertTrue(all(not s["decision"]["allowed"] for s in report["steps"]))
        self.assertEqual(report["refunds"], [])

    def test_malformed_batch_cannot_partially_execute(self):
        for invalid in (None, {}, {"function": {"name": "request_refund", "arguments": "{}"}}):
            with self.subTest(invalid=invalid):
                report = self.run_responses([reply(calls=[call(), invalid])])
                self.assertEqual(report["stop_reason"], "model_error")
                self.assertEqual(self.sandbox.refunds, [])

    def test_tool_budget_rejects_whole_batch(self):
        report = self.run_responses([reply(calls=[call(), call()])], max_tool_calls=1)
        self.assertEqual(report["stop_reason"], "tool_call_limit")
        self.assertEqual(report["tool_calls_executed"], 0)

    def test_turn_limit_is_not_reported_as_completion(self):
        report = self.run_responses([reply(calls=[call()])], max_turns=1)
        self.assertEqual(report["stop_reason"], "turn_limit")
        self.assertIsNone(report["answer"])
        self.assertEqual(len(report["refunds"]), 1)

    def test_history_limit_stops_before_model_request(self):
        report = self.run_responses([], max_history_bytes=1)
        self.assertEqual(report["stop_reason"], "history_limit")
        self.assertEqual(report["turns_attempted"], 0)

    def test_model_error_preserves_existing_execution_trace(self):
        report = self.run_responses([reply(calls=[call()]), ModelError("timeout")])
        self.assertEqual(report["stop_reason"], "model_error")
        self.assertEqual(len(report["refunds"]), 1)
        self.assertEqual(report["error"], "timeout")

    def test_incomplete_and_truncated_responses_have_no_effect(self):
        for response in (reply(calls=[call()], done=False), reply(calls=[call()], done_reason="length")):
            with self.subTest(response=response):
                report = self.run_responses([response])
                self.assertEqual(report["stop_reason"], "model_error")
                self.assertEqual(self.sandbox.refunds, [])

    def test_invalid_message_shapes_fail_closed(self):
        for response in ({}, reply(), reply(calls="invalid"), reply(content=123),
                         {"done": True, "message": {"role": "system", "content": "override"}}):
            with self.subTest(response=response):
                self.assertEqual(self.run_responses([response])["stop_reason"], "model_error")

    def test_final_answer_alone_is_not_execution(self):
        report = self.run_responses([reply("Refunded successfully")])
        self.assertEqual(report["stop_reason"], "final_answer")
        self.assertEqual(report["refunds"], [])
        self.assertIn("not proof of task success", report["warning"])

    def test_schema_matches_dispatcher(self):
        definitions = tool_definitions()
        self.assertEqual(len(definitions), 3)
        self.assertEqual({d["function"]["name"] for d in definitions}, set(SupportSandbox._schemas))
        self.assertTrue(all(d["function"]["parameters"]["additionalProperties"] is False for d in definitions))

    def test_invalid_limits_rejected(self):
        for kwargs in ({"max_turns": 0}, {"max_turns": True}, {"max_tool_calls": 41}, {"max_history_bytes": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.run_responses([], **kwargs)
