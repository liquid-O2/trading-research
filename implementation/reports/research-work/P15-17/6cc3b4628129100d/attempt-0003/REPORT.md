# P15-17 — attempt-0003 (definitive)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`.

Code identity: this attempt's `CODE_SNAPSHOT.json` pins 65 files: the runtime and test modules it owns, the 29 drifted files it executed, and 27 identity-only pins carried on the coordinator's 2026-09-17 integration patch so that the closed receipts of P15-00 to P15-16 and P15-16A resolve at the live digests; the split is tabulated in `WORK_LOG.md`.

## Result card

**Question.** Does any registered one-axis candidate, including the 2026-09-16 profile supplement, beat the source-faithful baseline B0.2 well enough to replace it as a family's entry rule?

| headline | value | unit | interval / support | artifact |
| --- | --- | --- | --- | --- |
| candidates promoted | 0 | candidates of 164 in the Holm family | 164 | `BREADTH_RESULTS.json` |
| best mean paired improvement | 25.7799 | net points per common complete day (SIRES:absorption_reward_retest:S1) | [24.771400822669104, 26.79708638025594] | `BREADTH_RESULTS.json` |
| candidates left inconclusive on support | 101 | candidates | 880 | `TRIALS.jsonl` |
| declared jobs reconciled | 278560 | job documents written, plus 160 absent on the retained failure date | 278720 | `RUN_COMPLETE.json` |
| hold-out days excluded | 112 | account days, 2026-04-01 to 2026-09-03 | 112 | `BREADTH_RESULTS.json` |

**Target.** EVALUATION.md promotion gates: paired mean improvement with a 95% lower bound above zero, Holm-adjusted p <= .05, support of 100 resolved opportunities on 30 days in 3 blocks, positive in 60% of supported blocks, no cost-stress reversal, no unexplained coverage loss  
**Met:** no

**Verdict.** `not_reaching_target` — No candidate clears the gates: most fail support outright and the rest fall at Holm, coverage or the cost stress, so the source-faithful baseline is retained in every family. The finite screen is complete and its result is a verified negative.

**Smallest lever.** re-screen the retained candidates whose first attribution is location_miss on Phase 3's improved locations, under the bounded-revisit rule, rather than widening the bank

**Evidence it worked.** candidates move out of inconclusive_support into a decided disposition and at least one clears the support gate with its 95% lower bound above zero

**Limits.**
- Mean daily net points in the deterministic one-mini benchmark on an isolated family under a fixed scheduler; not a portfolio and not a claim about the user's daily target.
- No number here touches the blind hold-out (2026-04-01 to 2026-09-03).
- The pairing is bound to P15-16A's verified receipt a931349e71b6ee2f and, inside the run, to each job document's own path and sha256.
