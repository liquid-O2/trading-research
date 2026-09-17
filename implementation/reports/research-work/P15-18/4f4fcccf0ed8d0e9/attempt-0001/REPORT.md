# P15-18 — attempt-0001 (definitive)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`.

## Result card

**Question.** Inside the two mechanism banks each family kept, does a neighbouring parameter value, or the one permitted combination of two, beat the value the breadth screen selected?

| headline | value | unit | interval / support | artifact |
| --- | --- | --- | --- | --- |
| neighbours attempted | 186 | of 217 proposals, 31 duplicates | 217 | `REFINEMENT_BANK.json` |
| distinct neighbour candidates executed | 53 | candidates over 1,742 declared sessions | 53 | `REFINEMENT_BANK.json` |
| refined mechanisms selected | 45 | fold-family roles over 5 outer folds | 45 | `SELECTED_RULES_BY_FOLD.json` |
| combinations attempted | 10 | of 20 proposals; the rest pair mechanisms on different branches | 20 | `COMBINATION_RESULTS.json` |
| trials promoted | 22 | of 237 ledger rows | 237 | `TRIALS.jsonl` |

**Target.** SEARCH_CONTRACT refinement stage: at most 12 neighbours per bank and 24 per family from the registered neighbourhoods, one combination per family only when each ingredient beats B0.2 on inner tuning, and the shared promotion gates for anything that replaces a baseline  
**Met:** partial

**Verdict.** `needs_upgrade` — The bounded round ran exactly as specified and a few refined mechanisms clear the gates, but they rest on an entry population whose first attribution is still support or location, so the gain is small and fold-dependent.

**Smallest lever.** give the refinement a larger resolved-entry population per fold, by re-running the same registered neighbourhoods on Phase 3 locations, rather than adding neighbours the contract caps

**Evidence it worked.** the selected refined mechanism's 95% lower bound stays above zero when the entry population roughly doubles, instead of moving with the fold

**Limits.**
- Refinement moves a parameter inside a mechanism the breadth screen already chose; it cannot rescue a family whose baseline is retained.
- No number here touches the blind hold-out (2026-04-01 to 2026-09-03).
