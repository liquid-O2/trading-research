# P15-18 attempt-0002 — the amended evaluation of the attempt-0001 refinement run

Evaluation-only attempt, 2026-09-17. Nothing was re-run: the refinement run
(`4f4fcccf0ed8d0e9/attempt-0001`, 53 distinct candidates and 3 executed combinations
over 1,742 declared sessions) and its combinations run root are read as they stand,
and every document bound here is pinned by sha256 in `RUN_BINDING.json`.

## Why this attempt exists

Three defects the coordinator found in attempt-0001's ledger, plus the 2026-09-17
EVALUATION.md amendment:

- **The multiplicity gate was unpassable.** At 2,000 draws the smallest attainable
  Holm-adjusted p-value for this stage was m/(B+1); draws are now 20,000, the floor
  (0.0009 for the 18-candidate decision family) is published beside every adjusted
  p-value, and a candidate that fails only Holm is `inconclusive_multiplicity`.
- **Every fold row carried the same `test_metrics`.** The promotion metric is pooled
  over the outer blocks by design (EVALUATION.md requires three supported blocks and
  60% positive over one paired series), so the fold rows repeated it. Each row now
  says `scope: pooled_outer_blocks` and carries `test_metrics.fold`, that fold's own
  outer-block mean, day count and entry counts. The fold-specific *selection*
  evidence is, as before, `SELECTED_RULES_BY_FOLD.json` (inner tuning only).
- **The combinations were promoted without their own statistics.** A combination row
  now carries its own mean, 95% interval, raw p, Holm-adjusted p and support counts
  from its own paired series; an undecided combination carries none of them rather
  than an ingredient's.
- **`support.resolved_opportunities` was null on every row.** Each row now carries
  the resolved counts on both sides of the pair, the day and block counts, the entry
  ratio, both gate outcomes and the half/nominal/twice sensitivity.
- **The support gate now applies to both sides.** A neighbour whose own baseline is
  below the gate is `inconclusive_support` with reason `baseline_support`.

## Result under the amended contract

237 ledger rows (217 neighbour proposals + 20 combination proposals), 18 candidates
at the decision stage, attainable floor 0.0009 against the .025 limit.

| disposition | rows |
| --- | --- |
| inconclusive_support | 161 |
| unsupported_owned_input | 41 |
| promoted | 20 |
| retained_baseline | 10 |
| rejected_by_evidence | 3 |
| inconclusive_multiplicity | 2 |

The 20 promoted rows are four distinct candidates over their folds:
`GB-FAIL:previous_hour:T4:shift_minutes=-15` (+5.589/day), its combination with
`GB-FAIL:previous_hour:F3:efficiency=0.5` (+3.547/day, own CI [1.670, 5.416], own
raw p 0.00015), `GB-FAIL:previous_hour:F3:efficiency=0.5` (+1.345/day) and
`JJ-TBR:judas_reversal:S4:deadline_minutes=10` (+4.899/day).
`JJ-TBR:internal_rotation:F1:minutes=90` is the one `inconclusive_multiplicity`
candidate: it passes every other gate and fails only Holm.

**`JJ-TBR:judas_reversal:S4:deadline_minutes=10` is marked
`implausible_pending_audit`**: it is a Sequence-bank candidate, and P15-17
attempt-0005's `AUDIT_S1.md` shows that every Sequence-bank entry in the breadth and
refinement runs is filled up to its own deadline before the stage that admitted it
(-60.0 s on 100% of this candidate's entries). The GB-FAIL promotions are Timing and
Formation candidates and do not carry that signature.

## Evidence

- `TRIALS.jsonl`, `SELECTED_RULES_BY_FOLD.json`, `COMBINATION_RESULTS.json`,
  `FAMILY_DISPOSITIONS.json` (now carrying the stage's multiplicity block),
  `FAMILY_REPORTS/` with both WORKFLOW tables plus the multiplicity and two-sided
  support tables.
- `SELF_CHECK.txt` from `self_check.py`, reading this attempt's results and the bound
  run root: caps respected (9 of 24 per family, 7 of 12 per bank), one inner
  improvement recomputed to 1.744505 with delta 0, one native entry traced to the
  P15-16A bytes, and 217 + 20 proposals reconciled one-to-one with the ledger.
- `RUN_BINDING.json`, `pytest.log`.

## Limits

- Same-model self-review only.
- No number here touches the blind hold-out (2026-04-01..2026-09-03, 112 days).
- The refinement cannot rescue a family whose baseline the breadth stage retained.
