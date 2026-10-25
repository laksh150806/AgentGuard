# Ten-week roadmap

| Week | Milestone | Acceptance evidence |
| --- | --- | --- |
| 1 | Threat model, related work, evaluation plan | Reviewed scope and explicit contribution limits |
| 2 | Support sandbox and agent adapter | Real local-model legitimate tasks with saved traces |
| 3 | Enforcement layer | Ownership, cap, retry and concurrency tests |
| 4 | Model evaluation harness and prompt-only baseline | Repeatable runs with budgets and real outcome predicates |
| 5 | AgentDojo subset | Pinned public benchmark conditions and reproducible results |
| 6 | Live retrieval and demo interface | Hackathon checkpoint with real model behavior clearly distinguished from replay |
| 7 | Policy comparisons | Security–utility curves using fixed ground truth |
| 8 | Held-out experiments | Frozen configuration, repeated trials and uncertainty |
| 9 | Reproducibility and packaging | Independent setup from README |
| 10 | Report, demo video and interview preparation | Claims linked to measured evidence |

## Foundation completed

- [x] Zero-dependency Python package and cross-platform launch scripts.
- [x] Three synthetic support tools with trusted host identity.
- [x] Fail-closed enforcement, cumulative caps and idempotency.
- [x] Versioned document update simulation.
- [x] Scripted comparison with explicit non-benchmark labeling.
- [x] Local automated tests and documentation.
- [x] Local-only Ollama adapter with installed-model checks and no paid fallback.
- [x] Bounded agent loop, tool traces and legitimate-task smoke checks.
- [x] Paired clean/poisoned development evaluation with baseline, prompt-only,
  enforced and optional strict conditions; fixed outcome scoring and budget preview.
- [x] Actual local-model pilot and pinned AgentDojo single-pair execution, with all outcomes published.
- [ ] Public-benchmark clean-task competence: the initial small-model pilot failed utility in all six runs.
- [x] Real-model legitimate task validation: Qwen3 1.7B passed all three smoke tasks on CPU.
- [x] GitHub destination accessible and local origin configured.
- [ ] Related-work review completed (links are a reading list, not a completed survey).

## Immediate next milestone

Diagnose why the small model calls tools on support tasks but not on the full
AgentDojo banking schema. Validate clean-task competence with a documented prompt
or model revision before expanding attacks. Retain the failed pilot alongside
new results; do not tune on future held-out cases.

No paid APIs, GPU rentals, hosted database or deployment subscription is needed
for the current foundation. Check hackathon rules before reusing prebuilt work.
