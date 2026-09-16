# P15-17 — attempt-0003 (definitive)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`.

## Result card

**Question.** Does any of the 160 registered one-axis candidates beat the source-faithful baseline B0.2 well enough to replace it as a family's entry rule?

| headline | value | unit / support | artifact |
| --- | --- | --- | --- |
| candidates promoted | 0 | candidates of 148 supported / 5 outer folds, Holm across the stage | `attempt-0003/BREADTH_RESULTS.json#decisions` |
| best mean paired improvement | 25.7799 | net points per common complete day / 1094 days, 10325 resolved entries / [24.7714, 26.7971] / SIRES:absorption_reward_retest:S1 | `attempt-0003/BREADTH_RESULTS.json#decisions` |
| dispositions | {'retained_baseline': 44, 'rejected_by_evidence': 19, 'inconclusive_support': 101} | candidates | `attempt-0003/TRIALS.jsonl` |
| declared jobs reconciled | True | 278560 written + 160 absent = 278720 declared | `attempt-0003/RUN_COMPLETE.json` |
| hold-out days excluded | 112 | account days, 2026-04-01..2026-09-03 | `attempt-0003/BREADTH_RESULTS.json#holdout_excluded` |

**Target.** EVALUATION.md promotion gates: paired mean improvement with a 95% lower bound above zero, Holm-adjusted p <= .05, support (100 resolved opportunities, 30 days, 3 blocks), positive in 60% of supported blocks, no cost-stress reversal, no unexplained coverage loss  
**Met:** no

**Verdict.** `not_reaching_target` — No candidate clears the gates: 91 of 148 fail support outright and the rest fall at Holm, coverage or the cost stress, so the source-faithful baseline is retained in every family.

**Smallest lever.** raise the entry count of the location-limited candidates before re-screening: the most common first attribution is location_miss (54 candidates), which Phase 3's improved locations address directly under the bounded-revisit rule

**Evidence it worked.** the same breadth screen, re-run on the retained candidates with Phase 3 locations, moves candidates out of inconclusive_support into a decided disposition and at least one clears the support gate

**Limits.** Mean daily net points in the one-mini benchmark on an isolated family under a fixed scheduler; not a portfolio, not a claim about the user's daily target, and no statement about the blind hold-out, which no number here touches.
