# P15-19 — rehearsal-0001 (rehearsal)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`.

## Result card

**Question.** With the entries frozen, does any of E1-E4 beat the E0 baseline management (structural objective, 60-minute or source expiry) on the selected rules?

| headline | value | unit / support | artifact |
| --- | --- | --- | --- |
| frozen entries compared | 9562 | entries over 1680 account days and 17 selected rules | `rehearsal-0001/FIXED_ENTRIES.json` |
| policies promoted over E0 | 0 | of 68 policy-by-rule comparisons / Holm across the exit stage, block bootstrap segmented by calendar year | `rehearsal-0001/EXIT_TRIALS.jsonl` |
| best comparison | 18.8214 | net points per common complete day against E0 / 14 days / [3.8214, 33.8214] / KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | `rehearsal-0001/EXIT_RESULTS.json#comparisons` |
| mean improvement by policy | {'E1': 0.0386, 'E2': 0.3837, 'E3': 0.42, 'E4': -0.1351} | net points per day, mean over rules | `rehearsal-0001/EXIT_RESULTS.json#comparisons` |
| E0 reproduced from the frozen entries | True | zero mismatches against the entry run's own E0 record | `rehearsal-0001/SELF_CHECK.txt` |

**Target.** OUTCOMES.md unchanged-entry exit experiment: compare exactly E0-E4 on frozen entries with the shared promotion gates, choosing only inside tuning and retaining every policy  
**Met:** partial

**Verdict.** `needs_upgrade` — All five policies ran on every frozen entry and the comparison is clean (E0 reproduces the entry run exactly), but no alternative policy clears the gates, so the baseline management stands.

**Smallest lever.** the exits differ only where price reaches +1R or the expiry binds; raise the share of entries that travel that far -- better locations or a later entry -- before asking a management policy to add value

**Evidence it worked.** the share of entries whose exit reason differs between E0 and E4 rises materially above its current level, and E4's interval separates from zero

**Limits.** A bounded baseline study on the entries the selected rules produced, not a learned management system; it cannot promote or rescue an entry candidate, and no hold-out date enters any comparison.
