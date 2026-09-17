# P15-19 definitive-0002 — the amended evaluation of the definitive-0001 exit study

Evaluation-only attempt, 2026-09-17. The exit study itself was not re-run: the
9,575 frozen entries of `definitive-0001` and their per-day exit shards are read as
they stand, and every bound document is pinned by sha256 in `RUN_BINDING.json`.

## Why this attempt exists

The 2026-09-17 EVALUATION.md amendment reaches this family too:

- 20,000 bootstrap draws instead of 2,000. The attainable Holm floor for the
  72-comparison family is now 0.0036 (it was 0.0360 at 2,000 draws, close enough to
  the .05 threshold to make the gate nearly unpassable), and the floor is published
  in `EXIT_COMPARISON.json` and in every family report.
- A comparison that fails only the Holm step is `inconclusive_multiplicity`, not
  `rejected_by_evidence`.
- The support gate applies to both sides of the pair. Here the two sides are E0 and
  the policy on the *same* frozen entries and the same common complete days, so the
  rule is symmetric by construction; the row now declares the baseline's resolved
  count explicitly instead of letting the gate fall back to an entry total.
- Each ledger row carries the support counts on both sides, the attainable floor
  beside the adjusted p-value, and each fold's own block mean.

## Result

72 comparisons (18 selected entry rules x E1..E4), 9,575 frozen entries, 0 E0
reproduction mismatches, 112 hold-out days excluded.

| disposition | comparisons |
| --- | --- |
| retained_baseline | 47 |
| rejected_by_evidence | 12 |
| inconclusive_support | 12 |
| inconclusive_multiplicity | 1 |
| promoted | 0 |

No exit policy replaces E0. The best supported comparison,
`GB-FAIL:previous_hour:T4:shift_minutes=-15 | E2`, is +1.238 net points/day with a
95% CI of [0.359, 2.169] and a raw p of 0.0048; its Holm-adjusted p is 0.331 in a
family of 72, so it is `inconclusive_multiplicity` — it stays in the retention set to
be re-tested under a pre-declared smaller family, and it is not evidence against E2.
The largest raw difference in the family
(`KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | E3`, +18.82/day) rests on
14 resolved entries over 14 days and is `inconclusive_support`; it is not a result.

## Evidence

- `EXIT_COMPARISON.json` / `EXIT_RESULTS.json`, `EXIT_TRIALS.jsonl` (72 rows, each
  with its entry-stage disposition and `entry_rescued: false`), `FAMILY_REPORTS/`.
- `SELF_CHECK.txt` from `self_check.py`: a paired improvement recomputed to 0.016425
  with delta 0, one exit traced from the study shard to the entry run's own record
  and on to the P15-16A pairing bytes, 72 = 18 x 4 separation confirmed, and zero E0
  mismatches.
- `RUN_BINDING.json`, `pytest.log`.

## Limits

- A separately counted decision family: it cannot promote or rescue an entry.
- The entry rules come from P15-18 attempt-0002, one of which
  (`JJ-TBR:judas_reversal:S4:deadline_minutes=10`) is implausible pending the
  Sequence-bank entry-timing fix named in P15-17 attempt-0005's `AUDIT_S1.md`; its
  exit comparisons inherit that limit.
- Same-model self-review only. No hold-out date enters any comparison.
