# Evaluation protocol

## Present evidence

The foundation runs handwritten policy smoke checks. There is no model and no
prompt-only condition. These checks validate intended controls and illustrate
the cost of stricter policy, but cannot support a claim about real prompt
injection success or defense generalization.

The JSON report includes raw case outcomes, denominators and local execution
timings. Its `scripted_violation_rate` is not an LLM attack success rate. Local
timing excludes model inference and is not end-to-end agent latency.

## Next experimental stages

1. Add a local model adapter with explicit, validated tool schemas and a bounded
   tool loop. Run legitimate tasks first; report any model capability floor.
2. Implement no-defense, prompt-only and enforced conditions with the same
   task specification, model, sampling parameters, tool budget and data.
3. Define legitimate success and attacker success with task-specific predicates
   over executed outcomes, independently of defense decisions. An approved
   proposed call is not necessarily an executed or successful attack.
4. Test a documented subset of AgentDojo using its supported extension points.
   Pin its commit, suite, task IDs, attack IDs, model version and configuration.
   Preserve benchmark semantics. Report any modification explicitly and avoid
   claiming direct comparability when conditions differ.
5. Keep custom support scenarios separate from public benchmark scores.
   Do not imply the custom refund tool is part of an official benchmark suite.
6. Split development and held-out scenarios before tuning. Reserve document
   templates and attack families where feasible; never tune on final results.
7. Evaluate policy strictness against fixed task/violation ground truth. Stricter
   defenses must not redefine inconvenient legitimate tasks as unauthorized.
8. Repeat runs across seeds where supported. Include counts, uncertainty,
   incomplete runs, timeouts, token usage, hardware and cost limits.

## Metrics for actual model runs

| Metric | Definition |
| --- | --- |
| Legitimate completion | Completed legitimate tasks / attempted legitimate tasks |
| Attacker success | Runs meeting the attack's executed-outcome predicate / attack runs |
| Legitimate false blocks | Legitimate action requests incorrectly rejected / legitimate action requests |
| Utility under attack | Legitimate tasks completed while attacked / attacked tasks |
| Latency | End-to-end elapsed time per attempted task, with timeout reporting |
| Cost | Inference time, tokens and any actual provider charges (paid usage is disabled by default) |

Do not equate every task failure with a false block. A model can fail while all
its actions are allowed. Include raw outcomes and representative failure traces.

## Questions to investigate

- Do permission controls preserve useful behavior under document updates?
- What legitimate tasks are lost when the refund threshold decreases?
- Which within-permission harmful actions survive the enforcement boundary?
- How do results change across models and unseen attack templates?

Adaptive attackers, a YAML policy language, and broad framework support are
deferred until a credible baseline and independent benchmark run exist.
