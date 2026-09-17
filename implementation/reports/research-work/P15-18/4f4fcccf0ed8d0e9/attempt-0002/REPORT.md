# P15-18 — attempt-0002 (the amended evaluation of the attempt-0001 refinement run)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`. Run provenance: `RUN_BINDING.json`.

This attempt re-evaluates an existing run under the 2026-09-17 amendment to EVALUATION.md,
WORKFLOW.md and DELIVERABLES.md: 20,000 bootstrap draws, the attainable Holm floor m/(B+1)
reported beside every adjusted p-value, the support gate applied to both sides of each pair,
`inconclusive_multiplicity` for a candidate that fails only Holm, and a plausibility section in
the result card. No candidate and no exit was re-run.

## Result card

**Question.** Inside the two mechanism banks each family kept, does a neighbouring parameter value, or the one permitted combination of two, beat the value the breadth screen selected?

| headline | value | unit | interval / support | artifact |
| --- | --- | --- | --- | --- |
| neighbours attempted | 186 | of 217 proposals, 31 duplicates | 217 | `REFINEMENT_BANK.json` |
| distinct neighbour candidates executed | 53 | candidates over 1,742 declared sessions | 53 | `REFINEMENT_BANK.json` |
| refined mechanisms selected | 45 | fold-family roles over 5 outer folds | 45 | `SELECTED_RULES_BY_FOLD.json` |
| combinations attempted | 10 | of 20 proposals; the rest pair mechanisms on different branches | 20 | `COMBINATION_RESULTS.json` |
| trials promoted | 20 | of 237 ledger rows | 237 | `TRIALS.jsonl` |

**Plausibility.**

| check | observed | expected | verdict |
| --- | --- | --- | --- |
| the promoted trials' per-fold outer-block means against their sampling error, under the 20,000-draw evaluation | GB-FAIL:previous_hour:T4:shift_minutes=-15 4.42/7.39/3.87/7.06/4.06 (spread 1.10 sems), GB-FAIL:previous_hour:F3:efficiency=0.5 1.81/2.20/1.09/0.29/1.34 (1.48), the GB-FAIL combination 2.82/4.23/3.40/5.18/-2.29 (2.84), JJ-TBR:judas_reversal:S4:deadline_minutes=10 4.60/3.13/4.72/6.31/8.27 (3.76) | a max-min range of about 2.3 standard errors for five estimates if the folds differ only by sampling error | `plausible` |
| JJ-TBR:judas_reversal:S4:deadline_minutes=10 (Sequence bank) entry timing against its own trigger stage | every entry of the Sequence bank is filled up to its own deadline before the stage that admitted it (confirmation_delay_s = -60.0 s on 100% of this candidate's entries); see P15-17 attempt-0005 AUDIT_S1.md | a non-negative delay: the decision cannot precede the bars that made the stage pass | `implausible_pending_audit` |
| the multiplicity gate is passable at this stage's family size | 18 candidates at the decision stage, attainable Holm floor m/(B+1) = 0.0009 at 20,000 draws | at or under .025 (EVALUATION.md, amended 2026-09-17) | `plausible` |
| every promoted trial carries its own paired evidence in the ledger | each promoted row, combinations included, carries its own mean, 95% interval, raw p and support counts on both sides, plus that fold's own outer-block metric beside the pooled decision metric | a promoted trial without its own mean, interval and raw p is not a promotion | `plausible` |

**Target.** SEARCH_CONTRACT refinement stage: at most 12 neighbours per bank and 24 per family from the registered neighbourhoods, one combination per family only when each ingredient beats B0.2 on inner tuning, and the shared promotion gates for anything that replaces a baseline  
**Met:** partial

**Verdict.** `needs_upgrade` — The bounded round ran exactly as specified and a few refined mechanisms clear the gates, but they rest on an entry population whose first attribution is still support or location, so the gain is small and fold-dependent.

**Smallest lever.** give the refinement a larger resolved-entry population per fold, by re-running the same registered neighbourhoods on Phase 3 locations, rather than adding neighbours the contract caps

**Evidence it worked.** the selected refined mechanism's 95% lower bound stays above zero when the entry population roughly doubles, instead of moving with the fold

**Limits.**
- Refinement moves a parameter inside a mechanism the breadth screen already chose; it cannot rescue a family whose baseline is retained.
- No number here touches the blind hold-out (2026-04-01 to 2026-09-03).
- JJ-TBR:judas_reversal:S4:deadline_minutes=10 is a Sequence-bank candidate and its promotion is implausible pending the entry-timing fix named in P15-17's AUDIT_S1.md.
- The promotion metric is pooled over the five outer blocks by design (EVALUATION.md); the fold-specific evidence is in each ledger row's test_metrics.fold and the selection evidence is SELECTED_RULES_BY_FOLD.json.
