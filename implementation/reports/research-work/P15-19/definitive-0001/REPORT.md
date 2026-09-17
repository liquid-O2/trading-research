# P15-19 — definitive-0001 (definitive)

Decision trail: `WORK_LOG.md`. Self-check: `SELF_CHECK.txt`.

## Result card

**Question.** With the entries frozen by the entry stage, does any of E1 to E4 beat the E0 baseline management on the selected rules?

| headline | value | unit | interval / support | artifact |
| --- | --- | --- | --- | --- |
| policies promoted over E0 | 0 | of 72 policy-by-rule comparisons | 72 | `EXIT_TRIALS.jsonl` |
| frozen entries compared | 9575 | entries over 1680 account days and 18 selected rules | 9575 | `FIXED_ENTRIES.json` |
| best comparison | 18.8214 | net points per common complete day against E0 (KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3) | [3.8214285714285716, 33.82142857142857] | `EXIT_COMPARISON.json` |
| E0 reproduction mismatches | 0 | entries where the recomputed E0 differs from the entry run's own E0 | 9575 | `EXIT_COMPARISON.json` |
| hold-out days excluded | 112 | account days, 2026-04-01 to 2026-09-03 | 112 | `EXIT_COMPARISON.json` |

**Target.** OUTCOMES.md unchanged-entry exit experiment: compare exactly E0 to E4 on frozen entries with the shared promotion gates, choosing only inside tuning, retaining every policy, and never rescuing an entry candidate  
**Met:** partial

**Verdict.** `needs_upgrade` — All five policies ran on every frozen entry and the comparison is clean, but no alternative policy clears the gates, so the E0 baseline management stands.

**Smallest lever.** raise the share of entries that travel far enough for the policies to differ (better locations or a later entry) before asking a management policy to add value

**Evidence it worked.** the share of entries whose exit reason differs between E0 and E4 rises well above its current level and E4's interval separates from zero

**Limits.**
- A bounded baseline study on the entries the selected rules produced, not a learned management system.
- It is a separately counted decision family: it cannot promote or rescue an entry.
- No hold-out date enters any comparison.
