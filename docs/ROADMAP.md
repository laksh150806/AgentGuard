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

## Progress review — 2026-11-08

The foundation checklist below has **13 of 16 items complete**. This counts
foundation deliverables, not overall research completion; the ten weekly
milestones have different sizes and several are only partially validated.

| Area | Verified status |
| --- | --- |
| Support sandbox, policy engine and local agent loop | Implemented; original Qwen3 1.7B support smoke evidence is 3/3 |
| Paired evaluation and prompt-only comparison | Implemented; the saved single-scenario pilot shows no defense advantage |
| Public benchmark | Pinned adapter implemented; broader clean-task competence remains a prerequisite |
| Demo | Published static replay and saved results; live inference/ingestion remain open |
| Implementation checks | 68 core and 10 optional integration tests pass; static exporter also builds |
| Research completion | Related-work review, broader policy comparisons, held-out repeated experiments and final report/video remain |

The next step is clean benchmark validation. The runner now preserves full
configuration in initial and partial checkpoints, fingerprints experiment
sources/dependencies, and fails clean-only validation unless every planned run
passes official utility with retrieved evidence and a final answer.

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
- [x] Mobile static viewer: Python-generated policy replay, saved model results,
  original JSON downloads and project explanation guide. See [MOBILE.md](MOBILE.md).
- [ ] Live inference and live document ingestion in the demo interface (the current viewer is a recorded replay).
- [ ] Public-benchmark clean-task competence: the initial small-model pilot failed utility in all six runs.
- [x] Real-model legitimate task validation: Qwen3 1.7B passed all three smoke tasks on CPU.
- [x] GitHub destination accessible and local origin configured.
- [ ] Related-work review completed (links are a reading list, not a completed survey).

## Immediate next milestone

The recovered [clean-task diagnosis](../reports/2026-10-25-tool-use/README.md)
shows that prompt clarification and evidence reminders can lead to tool use,
but the small model still fails the official task through incorrect accounting
or missing evidence. At recovery, the implementation passed 67 core and 7 optional
integration tests. Current verification is listed above; implementation tests
are separate from real-model competence.

The [2026-11-08 follow-up](../reports/2026-11-08-clean-validation/README.md)
completed the previously interrupted Qwen3 4B download and attempted two clean
baseline runs on a 2-CPU/8-GiB container. Both timed out at 300 seconds without a
completed response or tool call. Two earlier runtime-setup failures are also
preserved. Clean competence remains open; no attacks were expanded.

Diagnose the long generation/runtime behavior or select a local configuration
that completes within a declared budget. Then validate clean-task competence
across defense modes before expanding attacks. Preserve every failed run and
document prompt/model revisions; do not tune on future held-out cases.

No paid APIs, GPU rentals, hosted database or deployment subscription is needed
for the current foundation. Check hackathon rules before reusing prebuilt work.
