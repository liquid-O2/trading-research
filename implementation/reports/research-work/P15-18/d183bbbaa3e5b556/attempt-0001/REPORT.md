# P15-18 — attempt-0001 (rehearsal)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`.

## Result card

**Question.** Inside the two mechanism banks each family kept, does a neighbouring parameter value -- or the one combination of two -- beat the value the breadth screen selected?

| headline | value | unit / support | artifact |
| --- | --- | --- | --- |
| neighbours proposed / attempted / duplicate | [190, 165, 25] | rows | `attempt-0001/REFINEMENT_BANK.json#counts` |
| distinct neighbour candidates executed | 46 | candidates over 1,742 sessions | `attempt-0001/RUN_COMPLETE.json` |
| refined mechanisms selected | 42 | fold-family roles over 5 folds | `attempt-0001/SELECTED_RULES_BY_FOLD.json` |
| combinations attempted / not applicable | [10, 10] | proposals | `attempt-0001/COMBINATION_RESULTS.json` |
| trials promoted | 22 | of 210 ledger rows / Holm across the refinement stage, same gates as the breadth screen | `attempt-0001/TRIALS.jsonl` |

**Target.** SEARCH_CONTRACT refinement stage: at most 12 neighbours per bank and 24 per family from the registered neighbourhoods, one combination per family when each ingredient beats B0.2 on inner tuning, and the shared promotion gates for anything that replaces a baseline  
**Met:** partial

**Verdict.** `needs_upgrade` — The bounded round ran exactly as specified and a few refined mechanisms and one combination clear the gates, but the result rests on an entry population whose first attribution is still support or location, so the gain is small and fragile.

**Smallest lever.** give the refinement a larger resolved-entry population per fold -- the same neighbourhoods on the Phase 3 locations -- rather than more neighbours, which the contract caps for a reason

**Evidence it worked.** the selected refined mechanism's 95% lower bound stays above zero when the entry population doubles, instead of moving with the fold

**Limits.** Refinement can only move a parameter inside a mechanism the breadth screen already chose; it cannot rescue a family whose baseline is retained, and no number here touches the blind hold-out.
