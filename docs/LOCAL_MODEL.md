# Free local-model setup

The application uses only Python's standard library. Real inference additionally
needs Ollama and local model weights on your own machine. The scripts neither
install software nor download models. No API key or subscription is required.

## 1. Prepare Ollama

Install from [Ollama's official download page](https://ollama.com/download).
Choose a local model with tool-call support that fits available RAM/VRAM and
disk space. Model size alone does not determine memory use: context and runtime
overhead also matter. This milestone does not prescribe a model without knowing
the target hardware. Small models may fail legitimate tool tasks.

Disable cloud features on the **Ollama server**, not just in AgentGuard:
set `OLLAMA_NO_CLOUD=1` in the server's environment and restart it. For a manually
started Linux/macOS server, after stopping any existing Ollama instance:

```bash
OLLAMA_NO_CLOUD=1 ollama serve
```

For a manually started PowerShell server:

```powershell
$env:OLLAMA_NO_CLOUD="1"
ollama serve
```

For an installed desktop app or service, configure its environment and restart
that app/service. See [Ollama's FAQ](https://docs.ollama.com/faq) for platform-specific
configuration. Keep the service bound to loopback.

Download chosen local weights yourself using `ollama pull MODEL_NAME` only after
checking the model's license, download size and hardware requirements. This is a
download, not an inference charge, but it uses bandwidth and disk space. Do not
select a cloud model or configure a remote proxy. Confirm the name with `ollama list`.

## 2. Verify readiness

From the AgentGuard repository, replace `YOUR_LOCAL_MODEL` with that installed name:

```bash
python scripts/run.py doctor --model YOUR_LOCAL_MODEL
```

The client verifies a local GGUF model, recorded digest, nonempty model metadata
and advertised tool support before inference. Remote model metadata is rejected,
even when exposed under a seemingly local alias. Readiness is not evidence that
the model can complete our tasks. The local Ollama server remains a trusted
component; client metadata checks do not independently prove server isolation.

## 3. Run a task and inspect effects

```bash
python scripts/run.py run --model YOUR_LOCAL_MODEL --task "Request a simulated refund of 500 paise for order-demo using request_id demo-1."
python scripts/run.py smoke --model YOUR_LOCAL_MODEL
```

The three smoke tasks ask for document search, a customer read, and a refund.
They inspect successful tool results and ledger effects rather than trusting
the model's claims. They do not evaluate final-answer quality, held-out
generalization or injection resistance. Failed/unfinished tasks remain failures.

The `run` command returns exit code 0 when the model produces a final answer;
it does not have a generic task-success oracle. The `smoke` command returns 0
only when all three known tool objectives pass and each run reaches a final answer.

After legitimate tasks work, use `eval-plan` and `evaluate` to compare defenses.
See [COMPARISON.md](COMPARISON.md); start with one case to limit local compute.

## Limits and traces

Defaults: 6 model turns, 12 tool calls, 512 generated tokens per turn, a configured
4096-token model context, 12000 bytes of serialized conversation plus tool schemas,
60 seconds per socket operation, and a 2 MiB response limit. Use `--help` for
bounded overrides. The byte budget is not a tokenizer and does not guarantee
the server will never truncate input. A larger model/context needs more memory.
Socket timeouts are not a hard end-to-end wall-clock deadline.

There are no automatic retries. A malformed batch executes no tools. A batch
that exceeds the remaining call budget also executes no tools. A valid batch
can include both allowed and denied actions; it is not an all-or-nothing transaction.
Execution that occurred in earlier turns remains visible even if a later turn fails.

JSON traces include task text, model output, tool arguments/results, stops, model
metadata and any token counts reported by the server. These traces are for this
synthetic sandbox only. Store generated reports in the ignored `artifacts/` folder.

## Troubleshooting

- **Cannot reach local Ollama:** start the server; use `--port` if it is on a different
  loopback port. AgentGuard does not accept a remote host.
- **Model not installed:** select an exact name from `ollama list`; the app never pulls it.
- **No tool-call support:** choose a local model advertising the `tools` capability.
- **Generation budget exhausted / empty answer:** inspect the trace; a model may use
  its budget without issuing a call. Select a suitable model or adjust `--max-tokens`.
- **Turn/call/history limit:** this is an unfinished run, not a successful defense.

## Verification status

Transport tests use an actual loopback HTTP server with fake responses, including
an end-to-end CLI/tool/ledger check. They cover missing models, remote aliases,
redirects, malformed/oversized responses and errors. Real Qwen3 1.7B inference has now passed the three-task legitimate smoke check;
see reports/2026-10-25 for measured artifacts, including the failed AgentDojo
pilot. Unit tests are not model-accuracy evidence.

Protocol references: [chat API](https://docs.ollama.com/api/chat),
[installed models API](https://docs.ollama.com/api/tags), and
[official API types](https://github.com/ollama/ollama/blob/main/api/types.go).
