import json
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from agentguard.ollama import ModelError, OllamaClient


class LocalServerTests(unittest.TestCase):
    """Real loopback HTTP, fake model data. No Ollama or inference involved."""

    def setUp(self):
        self.requests = []
        self.routes = {
            "/api/tags": (200, {"models": [{"name": "test:latest", "size": 100, "digest": "test-digest"}]}),
            "/api/show": (200, {"details": {"format": "gguf"}, "model_info": {"general.architecture": "test"},
                                "capabilities": ["completion", "tools"]}),
            "/api/chat": (200, {"done": True, "message": {"role": "assistant", "content": "hello"}}),
        }
        routes, requests = self.routes, self.requests

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                requests.append((self.path, json.loads(body) if body else None))
                status, data = routes[self.path]
                if callable(data):
                    data = data(json.loads(body))
                encoded = data if isinstance(data, bytes) else json.dumps(data).encode()
                self.send_response(status)
                self.send_header("Content-Length", str(len(encoded)))
                if status == 302:
                    self.send_header("Location", "https://example.com/paid")
                self.end_headers()
                self.wfile.write(encoded)

            do_POST = do_GET

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()
        self.client = OllamaClient("test", port=self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_preflight_verifies_local_model_and_preserves_digest(self):
        metadata = self.client.preflight()
        self.assertEqual(metadata["digest"], "test-digest")
        self.assertEqual(metadata["model"], "test:latest")
        self.assertEqual([r[0] for r in self.requests], ["/api/tags", "/api/show"])

    def test_chat_uses_tool_protocol_and_bounded_generation(self):
        self.client.chat([{"role": "user", "content": "hello"}], [])
        path, body = self.requests[-1]
        self.assertEqual(path, "/api/chat")
        self.assertFalse(body["stream"])
        self.assertEqual(body["options"]["num_predict"], 512)
        self.assertEqual(body["options"]["temperature"], 0)

    def test_thinking_disabled_only_when_model_advertises_it(self):
        self.routes["/api/show"][1]["capabilities"].append("thinking")
        self.client.chat([], [])
        self.assertFalse(self.requests[-1][1]["think"])
        self.assertFalse(self.client.metadata["thinking"])

    def test_explicit_cpu_threads_are_sent_and_recorded(self):
        client = OllamaClient("test", port=self.server.server_port, num_threads=2)
        client.chat([], [])
        self.assertEqual(self.requests[-1][1]["options"]["num_thread"], 2)
        self.assertEqual(client.metadata["num_threads"], 2)
        for invalid in (0, 17, True, "2"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                OllamaClient("test", num_threads=invalid)

    def test_missing_model_does_not_download_or_infer(self):
        self.routes["/api/tags"] = (200, {"models": []})
        with self.assertRaisesRegex(ModelError, "not installed"):
            self.client.chat([], [])
        self.assertEqual(len(self.requests), 1)

    def test_remote_alias_rejected_before_chat(self):
        self.routes["/api/show"][1]["remote_host"] = "https://ollama.com"
        with self.assertRaisesRegex(ModelError, "Remote-backed"):
            self.client.chat([], [])
        self.assertNotIn("/api/chat", [r[0] for r in self.requests])

    def test_remote_model_flag_in_tags_is_rejected(self):
        self.routes["/api/tags"][1]["models"][0]["remote_model"] = "cloud-alias"
        with self.assertRaises(ModelError):
            self.client.preflight()

    def test_unknown_local_metadata_fails_closed(self):
        self.routes["/api/show"][1]["model_info"] = {}
        with self.assertRaisesRegex(ModelError, "local GGUF"):
            self.client.preflight()

    def test_no_tool_support_rejected(self):
        self.routes["/api/show"][1]["capabilities"] = ["completion"]
        with self.assertRaisesRegex(ModelError, "tool-call support"):
            self.client.preflight()

    def test_redirect_is_not_followed(self):
        self.routes["/api/tags"] = (302, {})
        with self.assertRaisesRegex(ModelError, "HTTP 302"):
            self.client.preflight()
        self.assertEqual(len(self.requests), 1)

    def test_invalid_json_nonfinite_values_and_error_objects_rejected(self):
        for body in (b"not json", b'{"models": NaN}', b"[]", b'{"error":"bad"}'):
            with self.subTest(body=body):
                self.routes["/api/tags"] = (200, body)
                with self.assertRaises(ModelError):
                    self.client.preflight()

    def test_oversized_response_rejected(self):
        self.client.max_response_bytes = 10
        with self.assertRaisesRegex(ModelError, "size budget"):
            self.client.preflight()

    def test_timeout_is_actionable(self):
        with patch("agentguard.ollama.http.client.HTTPConnection.request", side_effect=TimeoutError):
            with self.assertRaisesRegex(ModelError, "timed out"):
                self.client.preflight()

    def test_cloud_names_urls_and_invalid_limits_rejected(self):
        for model in ("", "test-cloud", "https://example.com/model"):
            with self.subTest(model=model), self.assertRaises(ValueError):
                OllamaClient(model)
        for kwargs in ({"port": 0}, {"timeout": 301}, {"max_tokens": -1}, {"port": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                OllamaClient("test", **kwargs)

    def test_cli_runs_full_loop_over_local_http_with_synthetic_responses(self):
        def chat(body):
            if body["messages"][-1]["role"] == "tool":
                return {"done": True, "message": {"role": "assistant", "content": "Simulated refund recorded"}}
            return {"done": True, "message": {"role": "assistant", "content": "", "tool_calls": [{
                "function": {"name": "request_refund", "arguments": {
                    "order_id": "order-demo", "amount_paise": 500, "request_id": "http-test",
                }},
            }]}}
        self.routes["/api/chat"] = (200, chat)
        process = subprocess.run(
            [sys.executable, "-m", "agentguard", "run", "--model", "test",
             "--port", str(self.server.server_port), "--task", "Refund 500 paise"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(report["stop_reason"], "final_answer")
        self.assertEqual(report["tool_calls_executed"], 1)
        self.assertEqual(report["refunds"][0]["amount_paise"], 500)

    def test_cli_reports_model_readiness_and_errors_as_json(self):
        for model, expected_code in (("test", 0), ("missing", 1)):
            with self.subTest(model=model):
                process = subprocess.run(
                    [sys.executable, "-m", "agentguard", "doctor", "--model", model,
                     "--port", str(self.server.server_port)], capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(process.returncode, expected_code)
                self.assertEqual(json.loads(process.stdout)["status"], "ready" if expected_code == 0 else "error")

    def test_evaluation_cli_preserves_failures_and_does_not_trust_claimed_completion(self):
        for complete in (True, False):
            with self.subTest(complete=complete):
                self.routes["/api/chat"] = (200, {"done": complete, "message": {
                    "role": "assistant", "content": "I completed the refund",
                }})
                process = subprocess.run(
                    [sys.executable, "-m", "agentguard", "evaluate", "--model", "test",
                     "--port", str(self.server.server_port), "--case", "refund-small"],
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(process.returncode, 0 if complete else 1)
                report = json.loads(process.stdout)
                self.assertEqual(len(report["runs"]), 6)
                self.assertTrue(all(row["clean_completed"] == 0 for row in report["summary"]))
                if not complete:
                    self.assertTrue(all(row["stop_reasons"] == {"model_error": 2} for row in report["summary"]))
