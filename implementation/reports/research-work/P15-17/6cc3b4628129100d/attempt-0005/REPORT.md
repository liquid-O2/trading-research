# P15-17 — attempt-0005 (the amended evaluation of the attempt-0003 and attempt-0004 runs)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`. Run provenance: `RUN_BINDING.json`.

This attempt re-evaluates an existing run under the 2026-09-17 amendment to EVALUATION.md,
WORKFLOW.md and DELIVERABLES.md: 20,000 bootstrap draws, the attainable Holm floor m/(B+1)
reported beside every adjusted p-value, the support gate applied to both sides of each pair,
`inconclusive_multiplicity` for a candidate that fails only Holm, and a plausibility section in
the result card. No candidate and no exit was re-run.

## Result card

**Question.** Does any registered one-axis candidate, including the 2026-09-16 profile supplement, beat the source-faithful baseline B0.2 well enough to replace it as a family's entry rule?

| headline | value | unit | interval / support | artifact |
| --- | --- | --- | --- | --- |
| candidates promoted | 2 | candidates of 164 in the Holm family | 164 | `BREADTH_RESULTS.json` |
| best mean paired improvement | 5.5885 | net points per common complete day (GB-FAIL:previous_hour:T4) | [3.39926603432701, 7.877156729900631] | `BREADTH_RESULTS.json` |
| candidates left inconclusive on support | 108 | candidates | 880 | `TRIALS.jsonl` |
| attainable Holm floor at 20,000 draws | 0.0082 | m/(B+1) for the 164-candidate family; the gate needs it at or under .025 | 164 | `BREADTH_RESULTS.json` |
| declared jobs reconciled | 278560 | job documents written, plus 160 absent on the retained failure date | 278720 | `RUN_COMPLETE.json` |

**Plausibility.**

| check | observed | expected | verdict |
| --- | --- | --- | --- |
| strongest promoted headline, GB-FAIL:previous_hour:T4: the five outer-fold means against their sampling error | 4.42, 7.39, 3.87, 7.06, 4.06 net points/day; spread 3.51 against a mean standard error of 3.19 (1.1 sems) | a spread of about one to two standard errors if the folds differ only by sampling error | `plausible` |
| second promoted candidate, JJ-TBR:judas_reversal:S4 (Sequence bank): entry timing against its own trigger stage, and fold spread against sampling error | confirmation_delay_s = -60.0 s on 100% of its entries (the fill precedes the stage that admitted it) and a fold spread of 5.81 against a mean standard error of 1.47 (3.9 sems) | a non-negative delay (a decision cannot precede its evidence) and a spread of one to two standard errors | `implausible_pending_audit` |
| largest raw improvement in the screen, SIRES:absorption_reward_retest:S1, +25.78 net points/day | 10,325 candidate entries against 19 baseline entries over the same 1,094 days (ratio 543.4) and every entry filled up to 600 s before its own trigger stage; AUDIT_S1.md concludes artefact | both sides of a paired comparison above the support gate of 100 resolved opportunities, and entries filled at or after the evidence that admitted them | `implausible_pending_audit` |
| the multiplicity gate is passable by construction at the declared family size | attainable Holm floor m/(B+1) = 0.0082 at 20,000 draws for 164 candidates (it was 0.0820 at the superseded 2,000 draws, above the .05 threshold) | at or under .025 (EVALUATION.md, amended 2026-09-17) | `plausible` |

**Target.** EVALUATION.md promotion gates (amended 2026-09-17): paired mean improvement with a 95% lower bound above zero, Holm-adjusted p <= .05 with the attainable floor m/(B+1) at or under .025, support of 100 resolved opportunities on 30 days in 3 blocks on BOTH sides of the pair, positive in 60% of supported blocks, no cost-stress reversal, no unexplained coverage loss  
**Met:** partial

**Verdict.** `needs_upgrade` — Two of 164 candidates clear every amended gate, but one of them (JJ-TBR:judas_reversal:S4) is a Sequence-bank candidate whose entries are filled before the stage that admitted them, so only GB-FAIL:previous_hour:T4 survives as a usable result; 108 candidates are inconclusive because one side of the pair is below the support gate.

**Smallest lever.** carry the replaced stage's at_ns into the episode's decision_at in search.py::_replace_stage, so a Sequence-bank entry can no longer be filled before the bars that admitted it, and re-run the 52 Sequence candidates

**Evidence it worked.** confirmation_delay_s is non-negative on every Sequence entry and the Sequence candidates' improvements survive the corrected entry time

**Limits.**
- Mean daily net points in the deterministic one-mini benchmark on an isolated family under a fixed scheduler; not a portfolio and not a claim about the user's daily target.
- No number here touches the blind hold-out (2026-04-01 to 2026-09-03).
- JJ-TBR:judas_reversal:S4 and every other Sequence-bank result is implausible pending the entry-timing fix (AUDIT_S1.md): 52 of the 160 frozen candidates are affected.
- SIRES:absorption_reward_retest:S1's +25.78 points/day is an artefact of an unsupported baseline (19 entries) and the same entry-timing defect; it is not a result.
- The pairing is bound to P15-16A's verified receipt a931349e71b6ee2f and, inside the run, to each job document's own path and sha256.
