"""Exercise the real CLI and official scorer with explicitly scripted responses."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

import agentdojo

from test_agent import ScriptedClient, call, reply


class BenchmarkCliTests(unittest.TestCase):
    def test_clean_exit_code_requires_evidence_and_report_cannot_be_overwritten(self):
        root = Path(__file__).resolve().parents[1]
        upstream = Path(agentdojo.__file__).resolve().parents[2]
        for with_evidence in (False, True):
            with self.subTest(with_evidence=with_evidence), TemporaryDirectory() as directory:
                output = Path(directory) / "report.json"
                responses = [reply("Your total spending was 1,050.")]
                if with_evidence:
                    responses.insert(0, reply(calls=[call("get_most_recent_transactions", {"n": 100})]))
                client = ScriptedClient(responses)
                client.preflight = Mock()
                argv = [str(root / "scripts/run_agentdojo.py"), "--model", "test_stub_not_a_model",
                        "--upstream", str(upstream), "--output", str(output),
                        "--clean-only", "--mode", "baseline"]
                with patch.object(sys, "argv", argv), patch("agentguard.ollama.OllamaClient", return_value=client), \
                        redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    if with_evidence:
                        runpy.run_path(argv[0], run_name="__main__")
                    else:
                        with self.assertRaises(SystemExit) as failure:
                            runpy.run_path(argv[0], run_name="__main__")
                        self.assertEqual(failure.exception.code, 1)
                    original = output.read_bytes()
                    report = json.loads(original)
                    self.assertTrue(report["complete"])
                    self.assertTrue(report["runs"][0]["utility"])
                    self.assertEqual(report["clean_validation"]["passed"], with_evidence)
                    self.assertIn("scripts/run_agentdojo.py", report["provenance"]["source_sha256"])
                    client.preflight.reset_mock()
                    with self.assertRaises(SystemExit) as overwrite:
                        runpy.run_path(argv[0], run_name="__main__")
                    self.assertEqual(overwrite.exception.code, 2)
                    self.assertEqual(output.read_bytes(), original)
                    client.preflight.assert_not_called()
