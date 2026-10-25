# Optional AgentDojo pilot

This integration uses AgentDojo's native task suite, tool executor, attack
generator and utility/attacker-success predicates. It is separate from the
custom support sandbox. The core package still has no third-party dependencies;
AgentDojo dependencies live in a separate optional environment.

## Exact scope

- Upstream: https://github.com/ethz-spylab/agentdojo
- Commit: `089ed468cf3ed0322acc66b0211f26d9d90dbf60`
- Benchmark version: `v1.2.2`
- Suite/task: banking / `user_task_1` (total spending in March 2022)
- Injection goal: `injection_task_5` (transfer money to an attacker account)
- Attack: upstream `ignore_previous`, including its original template text
- Conditions: clean and attacked, for baseline, prompt-only and enforced modes
- Model: local Ollama model, metadata/digest captured in the report

The task asks only for information. For this pilot the host's explicit policy
permits `get_most_recent_transactions` and rejects every other tool. This is a
**task-specific read-only policy**, not an automatic general authorization
system and not the support sandbox's refund-cap policy. No benchmark ground-truth
answer is put in the model prompt or used to choose transaction amounts.

Tool definitions remain available in all modes. Prompt-only and enforced use
the same prompt; enforcement additionally rejects calls before execution.
The official environment and scoring functions are unchanged. Upstream attack
generation uses its normal ground-truth pipeline to choose injectable fields.

## Local reproduction

Use a separate virtual environment. The following uses `uv`; standard Python
venv/pip can be used instead. Paths are examples; replace them for your machine.

```bash
git clone https://github.com/ethz-spylab/agentdojo.git ../agentdojo-upstream
git -C ../agentdojo-upstream checkout 089ed468cf3ed0322acc66b0211f26d9d90dbf60
uv venv ../agentdojo-venv
uv pip install --python ../agentdojo-venv/bin/python -r reports/2026-10-25/requirements-agentdojo.txt
uv pip install --python ../agentdojo-venv/bin/python --no-deps -e ../agentdojo-upstream
../agentdojo-venv/bin/python scripts/run_agentdojo.py --model qwen3:1.7b --upstream ../agentdojo-upstream --output artifacts/agentdojo.json
```

Set up the local model and disable Ollama cloud features as described in
[LOCAL_MODEL.md](LOCAL_MODEL.md). The runner verifies the source commit and that
the installed package comes from that editable checkout. No paid provider is
used; installing AgentDojo's provider libraries does not call their APIs.

Optional integration tests:

```bash
PYTHONPATH=src:tests ../agentdojo-venv/bin/python -m unittest discover -s tests_optional -v
```

## Limits and interpretation

The pipeline permits at most 6 model turns and 12 tool calls, with an 8192-token
configured context, 64000-byte history budget, 1024-token generation cap, and
120-second socket timeout. Thinking is disabled for models advertising that
capability. Limits and local inference differ from published experiments.

If stopped early, the pipeline adds an explicit **host stop marker** so the
upstream suite does not silently run its built-in retry loop. This is not a
model answer; `stop_reason` records incompleteness. All attempts remain in the
report. AgentDojo's `security` return value means attacker success, not safety;
the adapter labels it `attacker_success` and uses null for clean runs.

This single pair cannot establish broad effectiveness or leaderboard parity.
A model that fails the clean task has a utility problem even if it resists an
attack. Inspect retrieved tool results to establish exposure, and inspect
executed decisions to distinguish rejection from model refusal. There is no
statistical confidence estimate from these six runs.

AgentDojo is MIT-licensed; credit its authors when using these tasks/results.
An upstream license copy accompanies the published pilot report.
