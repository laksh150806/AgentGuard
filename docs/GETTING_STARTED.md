# Run AgentGuard locally

For the project overview and illustrated workflows, see the [README](../README.md).
Run these commands from the repository root with Python 3.11 or newer.

## Run for free

Requires Python 3.11 or newer. Runtime uses only Python's standard library.
No API key, cloud account, GPU, package download or network access is needed.
From the repository directory:

```bash
python scripts/check.py
python scripts/run.py demo
python scripts/run.py check
```

Commands produce JSON. To save a local report:

```bash
mkdir artifacts
python scripts/run.py check > artifacts/policy-checks.json
```

Generated reports in `artifacts/` are ignored by Git. Local model experiments
are an explicit step and need installed weights. No paid model API is used.
The public viewer is hosted separately on Render; it performs no inference.

## Connect a free local model

After installing Ollama and a local model with tool-call support, replace
`YOUR_LOCAL_MODEL` below with its exact name from `ollama list`:

```bash
python scripts/run.py doctor --model YOUR_LOCAL_MODEL
python scripts/run.py run --model YOUR_LOCAL_MODEL --task "Request a simulated refund of 500 paise for order-demo using request_id demo-1."
python scripts/run.py smoke --model YOUR_LOCAL_MODEL
```

`doctor` checks installed-model metadata without generating text. `run` performs
local inference and returns tool decisions and the final ledger. `smoke` checks
three legitimate tool objectives with a fresh sandbox per task. A final answer
does not itself establish task success.

Only `127.0.0.1` is supported. Remote-backed models and redirects are rejected;
there is no automatic download or paid fallback. See the [local setup guide](LOCAL_MODEL.md)
for cloud-disable settings, resource limits and troubleshooting.

## Compare defenses

Preview the experiment without installing or calling a model:

```bash
python scripts/run.py eval-plan --case refund-small
```

With a verified local model, run the same task against clean and poisoned
documents for each defense condition:

```bash
python scripts/run.py evaluate --model YOUR_LOCAL_MODEL --case refund-small
```

This selection makes six fresh runs (three modes, two document conditions).
Omitting `--case` selects five development scenarios and makes 30 runs. Add
`--include-strict` to explore utility lost under a lower refund cap. Save JSON
reports in `artifacts/` and inspect both the summaries and individual traces.
See [the comparison protocol](COMPARISON.md) for metrics, budgets and limits.
Measured pilot results are recorded separately from the development unit tests.

## Preview the mobile console

```bash
python scripts/build_mobile.py
python -m http.server 8000 --directory artifacts/mobile
```

Open `http://localhost:8000` on the same computer. This exports the Python
policy replay and copies the saved reports into a static viewer; it does not
start an inference service. See [hosting details](MOBILE.md).

## Optional public benchmark

AgentDojo has a separate environment and pinned upstream checkout. Follow
[the AgentDojo guide](AGENTDOJO.md); its dependencies are not required for the
core policy demo. Inspect official utility and traces, not just the exit code.
