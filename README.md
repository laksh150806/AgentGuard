# AgentGuard

**Tool-boundary authorization research for AI support agents.**

**[Open the deployed mobile demo →](https://agentguard-laksh-mobile.lakshnagori1508.chatgpt.site)**

Private access: sign in with the owner's ChatGPT account. No installation or
model API key is needed. The demo shows a scripted policy replay and saved
real-model results; it does not run live AI inference.

AgentGuard investigates how much unauthorized agent behavior can be prevented
without blocking legitimate work, including when retrieved content changes
during a session.

**Current status: first real local-model pilot completed, with mixed results.**
This release has a synthetic support environment, enforcement engine, scripted
experiments, an Ollama adapter, a bounded agent loop, and automated tests.
The paired evaluation harness now implements a baseline, prompt-only defense,
enforced permissions and an optional stricter policy. A mobile-friendly static
viewer now provides a scripted replay, recorded results and an explanation guide.
AgentDojo integration now includes a separate, pinned single-pair pilot adapter (see
[AGENTDOJO.md](docs/AGENTDOJO.md)); broader benchmark coverage remains pending.
Qwen3 1.7B passed all three support smoke tasks. On one custom attack, all modes
resisted it, so no defense advantage was shown. The AgentDojo pilot failed all
six runs with zero tool calls; it provides no evidence of attack resistance.
See [the measured pilot artifacts](reports/2026-10-25/) for results and limits.
Automated unit tests use synthetic responses and remain separate from real model runs.

## Mobile research console

The viewer needs no model, API key or backend. It replays output from the Python
policy engine and displays original saved experiment reports. It does not run
live inference or enforce permissions in a production system.

```bash
python scripts/build_mobile.py
python -m http.server 8000 --directory artifacts/mobile
```

Open `http://localhost:8000` on the same computer. Static source lives in `web/`.
The private hosted preview link is recorded in [MOBILE.md](docs/MOBILE.md).

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

Generated reports are ignored by Git. Model experiments will be a separate,
explicit step. The project enables no paid services or hosted CI workflows.

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
there is no automatic download or paid fallback. See the [local setup guide](docs/LOCAL_MODEL.md)
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
See [the comparison protocol](docs/COMPARISON.md) for metrics, budgets and limits.
Measured pilot results are recorded separately from the development unit tests.

## What the demo proves

1. Retrieve version 1 of a public refund guide.
2. Replace its content with a synthetic malicious instruction; retrieve version 2.
3. Replay a **scripted** request to refund 9900 paise (INR 99).
4. Compare an unprotected environment with a protected one capped at 2000 paise.
5. Attempt a legitimate 500-paise follow-up refund.

The protected environment rejects the unauthorized request and accepts the
legitimate one. The unprotected environment records the unauthorized refund;
the subsequent request exceeds the remaining order balance. This demonstrates
policy behavior, not that a model was persuaded by the document. All refunds
are in-memory synthetic records; no money moves.

## Trusted boundary

```text
Host-supplied session + policy ───────────────────┐
                                                v
Untrusted documents -> agent proposal -> validation + authorization -> tool
                           ^                         |
             local model or labeled replay          v
                                               audit event
```

Exactly three model-facing tools are defined:

| Tool | Boundary enforced |
| --- | --- |
| `search_documents` | Internal documents are filtered before results are returned |
| `read_customer` | A customer can access only their own synthetic record |
| `request_refund` | Order ownership, cumulative refund cap, paid balance and retry safety |

Money is integer paise. A lock makes policy checking and ledger updates atomic
within one sandbox. Duplicate request IDs cannot create duplicate refunds.
Unknown tools, extra fields, and malformed arguments fail closed.

The host constructs identity and policy; the model cannot supply or replace
them through tool arguments. These controls do **not** establish whether the
user intended every action that is otherwise within policy.

## Scripted checks

`check` runs four legitimate workflows and five adversarial action sequences
against three configurations. Each scenario starts with a fresh sandbox:

| Configuration | Enforcement | Refund cap |
| --- | --- | --- |
| Unprotected | Authorization deliberately disabled | Not enforced |
| Enforced | Ownership, confidentiality, cumulative cap | 2000 paise |
| Strict | Same controls with lower cap | 500 paise |

The strict setting deliberately blocks a valid 1500-paise request. This makes
lost utility visible instead of rewarding a defense that simply blocks all
actions. Violation predicates use fixed ground truth across configurations.
The included cases are development smoke checks, not a held-out dataset.

## Project map

- `src/agentguard/core.py`: trusted policy, state, dispatch and audit events.
- `src/agentguard/experiments.py`: scripted demo and evaluation scaffolding.
- `src/agentguard/cli.py`: JSON command-line interface.
- `src/agentguard/ollama.py`: local-only transport and installed-model checks.
- `src/agentguard/agent.py`: bounded tool loop and execution traces.
- `src/agentguard/smoke.py`: executed-outcome checks for three legitimate tasks.
- `src/agentguard/evaluation.py`: paired comparisons, fixed scoring rules and experiment fingerprints.
- `tests/`: authorization, concurrency, replay, data-isolation and CLI tests.
- [Threat model](docs/THREAT_MODEL.md): assumptions and uncovered risks.
- [Evaluation plan](docs/EVALUATION.md): controls, metrics and public benchmarks.
- [Roadmap](docs/ROADMAP.md): milestones and next steps.
- [Learning guide](docs/LEARNING.md): what the student should understand and own.
- [Cost policy](docs/COSTS.md): zero-cost defaults and future model constraints.

## Research positioning

Tool-boundary controls and security–utility analysis are established ideas.
This project claims no novel defense or benchmark result yet. Its proposed
contribution is a reproducible study of authorization controls with changing
retrieved content, followed by honest comparison with prior work.

Starting references (review and pin versions before formal experiments):

- [AgentDojo](https://github.com/ethz-spylab/agentdojo)
- [InjecAgent](https://github.com/uiuc-kang-lab/InjecAgent)
- [CaMeL](https://arxiv.org/abs/2503.18813)
- [LlamaFirewall](https://github.com/meta-llama/PurpleLlama/tree/main/LlamaFirewall)
- [OWASP Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)

Use only synthetic data and agents/environments you own or are authorized to test.
