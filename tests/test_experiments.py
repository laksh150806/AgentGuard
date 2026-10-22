import json
import subprocess
import sys
import unittest

from agentguard.experiments import run_demo, run_policy_checks


class ExperimentTests(unittest.TestCase):
    def test_demo_shows_document_update_block_and_legitimate_followup(self):
        report = run_demo()
        self.assertEqual(report["experiment_kind"], "scripted_policy_demo")
        baseline, protected = report["runs"]
        self.assertTrue(baseline["scripted_unauthorized_proposal"]["allowed"])
        self.assertFalse(protected["scripted_unauthorized_proposal"]["allowed"])
        self.assertTrue(protected["legitimate_followup"]["allowed"])
        self.assertEqual(protected["retrieval_after_update"]["data"][0]["version"], 2)

    def test_checks_measure_both_violations_and_lost_utility(self):
        report = run_policy_checks()
        baseline, enforced, strict = report["results"]
        self.assertEqual(baseline["scripted_violations"], 5)
        self.assertEqual(enforced["scripted_violations"], 0)
        self.assertEqual(enforced["legitimate_completed"], 4)
        self.assertEqual(strict["scripted_violations"], 0)
        self.assertEqual(strict["legitimate_completed"], 3)
        self.assertIsNone(report["model"])
        self.assertEqual(report["network_requests"], 0)

    def test_cli_emits_valid_labelled_json(self):
        for command in ("demo", "check"):
            with self.subTest(command=command):
                process = subprocess.run(
                    [sys.executable, "-m", "agentguard", command],
                    capture_output=True, text=True, check=True,
                )
                self.assertIn("scripted", json.loads(process.stdout)["experiment_kind"])

    def test_invalid_cli_command_fails(self):
        process = subprocess.run(
            [sys.executable, "-m", "agentguard", "deploy"], capture_output=True, text=True,
        )
        self.assertNotEqual(process.returncode, 0)


if __name__ == "__main__":
    unittest.main()
