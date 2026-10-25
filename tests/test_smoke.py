import unittest

from agentguard.smoke import run_smoke
from test_agent import ScriptedClient, call, reply


class SmokeTests(unittest.TestCase):
    def test_claimed_success_without_actions_fails_all_objectives(self):
        report = run_smoke(ScriptedClient([reply("Done"), reply("Done"), reply("Done")]))
        self.assertEqual(report["passed"], 0)
        self.assertEqual(report["total"], 3)

    def test_executed_objectives_pass_with_fresh_state_per_case(self):
        client = ScriptedClient([
            reply(calls=[call("search_documents", {"query": "Refund"})]), reply("Guide retrieved"),
            reply(calls=[call("read_customer", {"customer_id": "customer-demo"})]), reply("Demo Customer"),
            reply(calls=[call(arguments={"order_id": "order-demo", "amount_paise": 500,
                                         "request_id": "smoke-refund-1"})]), reply("Recorded"),
        ])
        report = run_smoke(client)
        self.assertEqual(report["passed"], 3)
        self.assertEqual([len(case["run"]["refunds"]) for case in report["cases"]], [0, 0, 1])

    def test_unrequested_refund_fails_read_objective(self):
        client = ScriptedClient([
            reply("Done"),
            reply(calls=[call("read_customer", {"customer_id": "customer-demo"}), call()]), reply("Done"),
            reply("Done"),
        ])
        self.assertFalse(run_smoke(client)["cases"][1]["passed"])
