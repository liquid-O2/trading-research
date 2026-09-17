# P15-19 — definitive-0002 (the amended evaluation of the definitive-0001 exit study)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`. Run provenance: `RUN_BINDING.json`.

This attempt re-evaluates an existing run under the 2026-09-17 amendment to EVALUATION.md,
WORKFLOW.md and DELIVERABLES.md: 20,000 bootstrap draws, the attainable Holm floor m/(B+1)
reported beside every adjusted p-value, the support gate applied to both sides of each pair,
`inconclusive_multiplicity` for a candidate that fails only Holm, and a plausibility section in
the result card. No candidate and no exit was re-run.

## Result card

**Question.** With the entries frozen by the entry stage, does any of E1 to E4 beat the E0 baseline management on the selected rules?

| headline | value | unit | interval / support | artifact |
| --- | --- | --- | --- | --- |
| policies promoted over E0 | 0 | of 72 policy-by-rule comparisons | 72 | `EXIT_TRIALS.jsonl` |
| frozen entries compared | 9575 | entries over 1680 account days and 18 selected rules | 9575 | `FIXED_ENTRIES.json` |
| best supported comparison | 1.2379 | net points per common complete day against E0 (GB-FAIL:previous_hour:T4:shift_minutes=-15|E2) | [0.3589238845144357, 2.168971456692913] | `EXIT_COMPARISON.json` |
| E0 reproduction mismatches | 0 | entries where the recomputed E0 differs from the entry run's own E0 | 9575 | `EXIT_COMPARISON.json` |
| hold-out days excluded | 112 | account days, 2026-04-01 to 2026-09-03 | 112 | `EXIT_COMPARISON.json` |

**Plausibility.**

| check | observed | expected | verdict |
| --- | --- | --- | --- |
| the largest raw difference in the family against its own support | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 shows 18.82 net points/day on 14 common complete days and 14 resolved entries, with block means [30.0, 1.5, 0.0] | at least 100 resolved opportunities on 30 days in 3 blocks before a difference is read as a result (EVALUATION.md) | `plausible` |
| the best supported comparison's interval and multiplicity | GB-FAIL:previous_hour:T4:shift_minutes=-15|E2 1.238 points/day, 95% CI [0.359, 2.169], raw p 0.0048, Holm-adjusted 0.3312 in a family of 72 | Holm-adjusted p <= .05 for a promotion; a candidate that fails only Holm is inconclusive_multiplicity, not rejected | `plausible` |
| the multiplicity gate is passable at this family's size | attainable Holm floor m/(B+1) = 0.0036 for 72 comparisons at 20,000 draws | at or under .025 (EVALUATION.md, amended 2026-09-17) | `plausible` |
| E0 is reproduced exactly on the frozen entries | 0 mismatches over 9575 entries | zero: the same entries under the same E0 policy must reproduce the entry stage's own numbers | `plausible` |

**Target.** OUTCOMES.md unchanged-entry exit experiment: compare exactly E0 to E4 on frozen entries with the shared promotion gates, choosing only inside tuning, retaining every policy, and never rescuing an entry candidate  
**Met:** partial

**Verdict.** `needs_upgrade` — All five policies ran on every frozen entry and the comparison is clean, but no alternative policy clears the gates: the best supported difference fails only the Holm step and is recorded inconclusive_multiplicity, so the E0 baseline management stands.

**Smallest lever.** raise the share of entries that travel far enough for the policies to differ (better locations or a later entry) before asking a management policy to add value

**Evidence it worked.** the share of entries whose exit reason differs between E0 and E4 rises well above its current level and E4's interval separates from zero

**Limits.**
- A bounded baseline study on the entries the selected rules produced, not a learned management system.
- It is a separately counted decision family: it cannot promote or rescue an entry.
- No hold-out date enters any comparison.
- The entry rules come from the refinement stage, one of which (JJ-TBR:judas_reversal:S4) is implausible pending the Sequence-bank entry-timing fix; its exit comparisons inherit that limit.
