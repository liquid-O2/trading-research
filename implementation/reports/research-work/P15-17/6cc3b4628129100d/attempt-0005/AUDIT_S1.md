# Audit — SIRES:absorption_reward_retest:S1 (+25.78 net points/day)

Ordered on 2026-09-17 before the number is used anywhere. Evidence: attempt-0003's
own per-date job documents (`jobs/<date>/SIRES--absorption_reward_retest--S1.json.gz`,
per-entry records) and daily shards, 1,107 account days from 2022-01-01 with the
blind hold-out (2026-04-01..2026-09-03) removed. Audit script:
`scratchpad/p1517b/audit_s1.py`.

**Finding: artefact. Two separate defects, both mechanical, both now demonstrated.**

## 1. The pair is not an upgrade of a supported rule

| quantity | candidate | B0.2 baseline |
| --- | --- | --- |
| entries over 1,094 common complete days | 10,325 | 19 |
| days on which it traded at all | 1,090 | 19 |
| episodes offered (sample of 28 days) | 355 | 355 |
| entries taken from those episodes | 259 (73.0%) | 3 (0.85%) |
| mean net points per entry | +2.732 | +0.276 |

Both sides see the same opportunities; the candidate converts 73% of them and the
baseline 0.85%. The paired mean of +25.78 points/day is therefore not a comparison
of two rules on the same events: on 1,075 of 1,094 days the baseline term is exactly
zero, so the headline is the candidate's own gross daily P&L. Under the amended
EVALUATION.md the support gate applies to both sides, and this pair is now
`inconclusive_support` with reason `baseline_support` (candidate 10,325 resolved
opportunities, baseline 19, ratio 543.4, gate 100).

## 2. Every Sequence-bank entry is filled before the evidence that admitted it

Per-entry `confirmation_delay_s` = `decision_at - trigger.at_ns`:

| bank | candidates | entries sampled | mean delay (s) | negative share |
| --- | --- | --- | --- | --- |
| Sequence | 52 | 91 | -511.3 | 0.989 |
| Formation | 25 | 24 | +150.0 | 0.000 |
| Timing | 14 | 19 | +180.0 | 0.000 |
| Memory | 23 | 38 | +0.1 | 0.000 |
| Profile | 20 | 32 | 0.0 | 0.000 |
| Delta | 16 | 26 | 0.0 | 0.000 |
| Reference | 10 | 3 | +480.0 | 0.000 |

For S1 every one of the 10,325 entries has a delay in [-600.0, -0.0] s, and the
recipe's own parameter is `deadline_s: 600`. The same signature scales with the
parameter on the other Sequence recipes: S3 (`cohort_s: 120`) lies in [-120, -64],
S4 (`pressure_s: 120`) is exactly -60.0 on every entry.

Mechanism, in the code: `search.py::_sequence_stage` decides the stage by scanning
minute bars over `[issue_ns, issue_ns + deadline]` and sets `out["at_ns"] =
rows[-1]["end"]`, the end of that window. The episode's `decision_at` is left at the
baseline adapter's confirmation time (`source_adapters/confirmation.py`), and
`daily_benchmark` fills the entry at `decision_at + latency`. So the entry is filled
up to `deadline_s` **before** the bars that made the stage pass exist. The scan only
emits the episode because the reclaim later happened; entering ahead of it is
hindsight, not a rule. `contracts/types.py` already requires
`issue_at_ns <= decision_at_ns`, but the candidate override path never re-derives
`decision_at` from the replaced stage.

This is why the fill rate is 73% against the baseline's 0.85% and why the edge
survives cost: the entry sits in front of a move that the evidence window has
already observed.

Blast radius: the Sequence bank, 52 of the 160 frozen candidates (and the
supplement adds none). Formation, Timing, Reference, Memory, Profile and Delta
candidates show non-negative delays and are not implicated.

Fix (not applied here; it changes the scan and requires a new population run,
which this evaluation was explicitly not authorised to do): in
`search.py::_replace_stage`, carry the replaced stage's `at_ns` into the episode's
`decision_at` whenever it is later, and let `check_causal_parameters` reject an
episode whose decision precedes any stage it depends on.

## 3. The per-year stability is *not* the anomaly

| fold | days | mean diff/day | sd | sem | entries | points/entry |
| --- | --- | --- | --- | --- | --- | --- |
| 2022 | 258 | 26.332 | 18.175 | 1.132 | 2,426 | 2.800 |
| 2023 | 257 | 25.413 | 14.205 | 0.886 | 2,408 | 2.712 |
| 2024 | 259 | 26.406 | 16.016 | 0.995 | 2,411 | 2.837 |
| 2025 | 257 | 25.011 | 16.978 | 1.059 | 2,460 | 2.613 |
| 2026 (to 2026-03-31) | 63 | 25.575 | 16.021 | 2.018 | 620 | 2.599 |

The spread of the five fold means is 1.40 points against a mean standard error of
1.22 points (1.15 sems); per entry the spread is 0.253 against a mean sem of 0.157
(1.6 sems). With ~2,400 entries a year at sd 6.6 points per entry that stability is
exactly what sampling error predicts. The stability is therefore consistent, and it
is not evidence of an artefact by itself — the artefact is the look-ahead that makes
every year's entries good.

Per-entry shape: mean +2.732, sd 6.611, median -1.250, win rate 45.6%, mean win
+9.26, mean loss -2.74, max +172.25; exits 4,595 objective, 5,715 stop, 15 expiry.
Cost is applied on every entry (round-trip $5.00 = 0.25 NQ points at $2.50/side);
the cost stress (500 ms, 2 ticks, $3.50/side) moves the daily mean from +25.780 to
+22.836, a 2.94-point reduction that matches 9.44 entries/day x $7/entry / $20 per
point = 3.3 points. Nothing is uncosted.

## Verdict

`implausible_pending_audit` → **artefact confirmed**. The number must not appear in
any headline or recommendation. Two consequences carried into this attempt:

1. S1 is `inconclusive_support` (reason `baseline_support`) in
   `BREADTH_RESULTS.json`; it stays in the retention set with its own frequency,
   the 543.4 ratio and its unpaired mean recorded.
2. `JJ-TBR:judas_reversal:S4`, one of the two candidates that now clear every gate,
   is a Sequence-bank candidate with the same signature (-60.0 s on every entry), so
   it is marked `implausible_pending_audit` in `RESULT_CARD.json` and cannot be
   presented as a promotion until the ordering defect is fixed and its family is
   re-run. `GB-FAIL:previous_hour:T4` (Timing bank, delays +180 to +300 s) does not
   carry the signature.
