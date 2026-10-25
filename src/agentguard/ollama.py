"""Standard-library client for an already installed local Ollama model.

Only 127.0.0.1 is contacted. No downloads, redirects, credentials or cloud
fallback. The local server is trusted; disable its cloud features separately.
"""

import http.client
import json


class ModelError(RuntimeError):
    """Actionable transport, configuration or protocol failure."""


def _reject_constant(value: str):
    raise ValueError(f"Non-JSON numeric constant: {value}")


class OllamaClient:
    backend = "local_ollama"
    max_response_bytes = 2 * 1024 * 1024

    def __init__(self, model: str, *, port: int = 11434, timeout: int = 60,
                 max_tokens: int = 512, context_tokens: int = 4096):
        if not isinstance(model, str) or not model.strip() or len(model) > 200:
            raise ValueError("Supply an installed local model name with --model")
        if "cloud" in model.casefold() or "://" in model:
            raise ValueError("Cloud model names and URLs are disabled")
        for name, value, maximum in (("port", port, 65535), ("timeout", timeout, 300),
                                     ("max_tokens", max_tokens, 2048), ("context_tokens", context_tokens, 8192)):
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"{name} must be an integer between 1 and {maximum}")
        self.model = model
        self.port = port
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.context_tokens = context_tokens
        self.metadata: dict = {}

    def _request(self, path: str, payload: dict | None = None) -> dict:
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=self.timeout)
        try:
            body = None if payload is None else json.dumps(payload, allow_nan=False).encode()
            connection.request("GET" if payload is None else "POST", path, body=body,
                               headers={"Content-Type": "application/json"})
            response = connection.getresponse()
            raw = response.read(self.max_response_bytes + 1)
            if len(raw) > self.max_response_bytes:
                raise ModelError("Local server response exceeded the size budget")
            if response.status != 200:
                # Do not expose untrusted server HTML or arbitrary response bodies.
                raise ModelError(f"Local Ollama returned HTTP {response.status} for {path}; check the server and installed model")
            data = json.loads(raw, parse_constant=_reject_constant)
            if not isinstance(data, dict) or "error" in data:
                raise ModelError("Local Ollama returned an error or invalid response object")
            return data
        except (OSError, http.client.HTTPException) as exc:
            raise ModelError("Cannot reach local Ollama or request timed out. Start Ollama, then run the doctor command") from exc
        except (ValueError, UnicodeError) as exc:
            raise ModelError("Local Ollama returned invalid JSON") from exc
        finally:
            connection.close()

    def preflight(self) -> dict:
        self.metadata = {}
        tags = self._request("/api/tags").get("models")
        if not isinstance(tags, list) or any(not isinstance(row, dict) for row in tags):
            raise ModelError("Invalid installed-model list from local Ollama")
        names = {self.model}
        if ":" not in self.model:
            names.add(self.model + ":latest")
        installed = next((row for row in tags if row.get("name") in names), None)
        if installed is None:
            raise ModelError("Model is not installed locally. Choose a name from 'ollama list'; no download was attempted")
        info = self._request("/api/show", {"model": installed["name"]})
        if any(row.get(key) for row in (installed, info) for key in ("remote_host", "remote_model")):
            raise ModelError("Remote-backed Ollama models are disabled, including local aliases")
        details = info.get("details")
        if (not isinstance(details, dict) or details.get("format") != "gguf"
                or not isinstance(info.get("model_info"), dict) or not info["model_info"]
                or type(installed.get("size")) is not int or installed["size"] <= 0
                or not isinstance(installed.get("digest"), str) or not installed["digest"]):
            raise ModelError("Could not verify local GGUF model metadata; inference was not started")
        capabilities = info.get("capabilities")
        if not isinstance(capabilities, list) or "tools" not in capabilities:
            raise ModelError("Selected model does not advertise tool-call support")
        self.model = installed["name"]
        self.metadata = {"model": self.model, "digest": installed["digest"],
                         "size_bytes": installed["size"], "capabilities": capabilities,
                         "details": details, "endpoint": f"http://127.0.0.1:{self.port}",
                         "max_tokens": self.max_tokens, "context_tokens": self.context_tokens,
                         "timeout_seconds": self.timeout, "temperature": 0, "seed": 0}
        return dict(self.metadata)

    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        if not self.metadata:
            self.preflight()
        return self._request("/api/chat", {
            "model": self.model, "messages": messages, "tools": tools, "stream": False,
            "options": {"temperature": 0, "seed": 0, "num_predict": self.max_tokens,
                        "num_ctx": self.context_tokens},
        })
