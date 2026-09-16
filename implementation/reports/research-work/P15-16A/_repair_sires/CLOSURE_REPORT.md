# CLOSURE REPORT — P15-16A B0.2 repair, track sires

Worktree `/workspace/.worktrees/b02r-sires`. Branch `p15/b02r-sires`. No receipts. No wiki. No bound widened.

## (a) Stages measured

A stage is measured if its verdict depends on a market operand compared with a source predicate and can fail on real data.

| branch | context | reference | location | trigger | confirmation | risk | objective | management | unmeasured |
|---|---|---|---|---|---|---|---|---|---|
| dom_rejection | measured | measured | measured | measured | measured | measured | measured | measured | daily_r, new_information named; do not unknown the episode |
| absorption_reward_retest | measured | measured | measured | opposite_absorbed | 3-tick reward then distinct origin retest | measured | measured | measured | same named unobservables |
| stop_four_stage | measured | measured | measured | replenishment ≥ 3 | reward ≥ 3 | measured | measured | measured | same |
| footprint_confirmed_reaction | measured | measured | measured | footprint 3–4x | opposite_absorbed | measured | measured | measured | same |
| vwap_deviation_fade | measured | measured | measured | beyond 1-band + absorption | opposite_absorbed | measured | measured | measured | same |
| ofm_aggressive | **unmeasured** | not emitted | not emitted | not emitted | not emitted | not emitted | not emitted | not emitted | gamma_regime (BIG p.14); one session_unknown |
| ofm_passive | measured | measured | measured | failure and no aggression | squeeze_failed | measured | measured | measured | same named unobservables |
| clean_squeeze | measured | measured | measured | F02 no retest | opposite_absorbed | measured | measured | measured | same |
| balance_failure_fade | **unmeasured** | not emitted | not emitted | not emitted | not emitted | not emitted | not emitted | not emitted | gamma_regime (BIG p.14); one session_unknown |
| defended_band_continuation | measured | measured | measured | replenishment ≥ 3 | reward ≥ 3 | measured | measured | measured | same |
| kg1_retest | omitted | omitted | omitted | omitted | omitted | omitted | omitted | omitted | no supplied KG1 record |
| microbalance_break | empty on this slice | empty | empty | empty | empty | empty | empty | empty | no F3 microbalance contact |
| REFILL touch_record | n/a | measured | measured | departure then return | hold vs broke | measured | measured | n/a | hold window unknown only when unobservable |

Before this repair, population `scan_b02` read author-context from `rec` and emitted two synthetic episodes per session, unknown at location. After, `rec` is identity-only. Confirmation on absorption is no longer reward-only (always-pass given trigger). Confirmation on defended_band is no longer replenishment OR absorption (tautological with trigger).

## (b) Fifteen-date population

Slice: 2020-01-02, 2020-06-01, 2020-11-02, 2021-06-01, 2021-11-01, 2022-01-03, 2022-06-01, 2023-01-03, 2023-11-06, 2024-03-05, 2024-11-01, 2025-01-02, 2025-06-02, 2026-01-02, 2026-06-01. n=15 sessions.

| family | branch | episodes | pass/fail/unknown | pass_rate | eps | bound eps | bound pr | in/out | diagnosis |
|---|---|---|---|---|---|---|---|---|---|
| SIRES | dom_rejection | 220 | 0/210/10 | 0.000 | 14.667 | [0,16] | [0.0,0.20] | in | — |
| SIRES | absorption_reward_retest | 220 | 0/220/0 | 0.000 | 14.667 | [0,16] | [0.0,0.20] | in | — |
| SIRES | stop_four_stage | 220 | 35/185/0 | 0.159 | 14.667 | [0,16] | [0.0,0.20] | in | — |
| SIRES | footprint_confirmed_reaction | 220 | 0/101/119 | 0.000 | 14.667 | [0,16] | [0.0,0.20] | in | — |
| SIRES | vwap_deviation_fade | 220 | 0/159/61 | 0.000 | 14.667 | [0,16] | [0.0,0.20] | in | — |
| SIRES | ofm_aggressive | 15 | 0/0/15 | 0.000 | 1.000 | [1,1] | [0.0,0.0] | in | — |
| SIRES | ofm_passive | 220 | 0/220/0 | 0.000 | 14.667 | [0,16] | [0.0,0.15] | in | — |
| SIRES | clean_squeeze | 220 | 0/220/0 | 0.000 | 14.667 | [0,16] | [0.0,0.15] | in | — |
| SIRES | balance_failure_fade | 15 | 0/0/15 | 0.000 | 1.000 | [1,1] | [0.0,0.0] | in | — |
| SIRES | defended_band_continuation | 220 | 34/80/106 | 0.155 | 14.667 | [0,16] | [0.0,0.20] | in | — |
| SIRES | kg1_retest | 0 | 0/0/0 | 0.000 | 0.000 | [0,1] | [0.0,0.20] | in | — |
| SIRES | microbalance_break | 0 | 0/0/0 | 0.000 | 0.000 | [0,16] | [0.0,0.20] | in | — |
| REFILL-STUDY | touch_record | 3890 | 184/3706/0 | 0.047 | 259.333 | [80,350] | [0.25,0.60] | out | family JSON `observed_rate_justification` quoting REF pp.5-8 |

Stage confirmation on the two repaired branches: absorption 0 pass / 4 fail (all four trigger-pass contacts lack a distinct origin retest). defended_band 140 pass / 15 fail (same 15 reward failures as stop_four_stage).

## (c) Author examples

| id | reached_location | detected | failing operand |
|---|---|---|---|
| SI-2026-07-08 | no | no | context unknown, gamma_regime |
| SI-2026-07-09 | no | no | context unknown, gamma_regime |
| SI-2026-07-10 | no | no | context unknown, gamma_regime |
| SI-2026-07-14 | no | no | location fail, inside_balance |
| SI-2026-07-15-OVERNIGHT | no | no | trigger fail, opposite_absorbed=false; miss:level |
| SI-2026-07-23 | yes | no | trigger fail, replenishment_ticks=1 |
| SI-2026-07-31 | no | no | context unknown, gamma_regime |
| SI-2026-08-04 | no | no | context unknown, gamma_regime |
| SI-2026-08-06 | no | no | context unknown, gamma_regime |
| SI-2026-08-19 | no | no | context unknown, gamma_regime |

OFM examples are one session_unknown (gamma). No rule was changed to force a detect.

## (d) Test commands

```
cd /workspace/.worktrees/b02r-sires/implementation && PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest tests/rule_discovery -q -p no:cacheprovider --tb=line
```

exit 0, 469 passed in 2078.97s (0:34:38). 0 failed. 0 collection errors.

`test_mutated_stop_four_stage_bound_fails_the_gate`: passed. Copies `stop_four_stage.pass_rate` to `[0.0, 0.0]`, pops `observed_rate_justification`, measured pass_rate=0.159, `_in_bound` is False, `_human_justification` is None. A generated diagnosis string cannot save it.

`test_after_tape_replay_does_not_call_build_event_window`: passed. Monkeypatches `event_cache.build_event_window` to raise; every after-tape SIRES and REFILL example returns `detected=None`, `divergence="date outside the tape"`.

`test_track_sires_round1_files_byte_identical`: passed. Committed `_track_sires` sha256 unchanged.

## (e) MERGE_NOTES summary

Shared files: `common.py` lazy-imports `peak_rss_bytes` (additive). `runner.py` drops `directory_listing_digest` and digests code paths with `file_digest`. Contracts stay frozen. The other three tracks have their own hunks on the same `runner.py` lines; the integrator must keep one version. Confirmation edits are `sires_b02.py` only.

## (f) Remaining limitations

- Gamma is unobservable in Phase 1.5. ofm_aggressive and balance_failure_fade are one unknown per session until Phase 2 options boards exist.
- KG1 engine unpublished; kg1_retest is empty.
- CVD filter on absorption is not a Phase 1.5 tape operand; it is not defaulted to pass.
- Daily R is not on the tape; named omitted, does not unknown every episode.
- REFILL hold rate 4.7% vs paper 42% is the OD 8-tick / 30-minute NQ-only label, not a rewrite of REF p.8. Bound stays at the paper.
- Touches per session on this slice range from 6 to 592. The definition is stable; zone count is not. See (h).
- Full-history 1,742-session B0.2 run is integration's job.

## (g) git status

```
git -C /workspace/.worktrees/b02r-sires status --short
```

See the live listing in the chat close. Expected: modified adapters, families, runner, tests; untracked `_repair_sires/` and `test_p15_16a_plausibility_sires.py`. `_track_sires` not modified.

## (h) REFILL per-date touches

| date | touches | hold | broke | hold_rate |
|---|---|---|---|---|
| 2020-01-02 | 92 | 14 | 78 | 0.152 |
| 2020-06-01 | 94 | 17 | 77 | 0.181 |
| 2020-11-02 | 592 | 24 | 568 | 0.041 |
| 2021-06-01 | 72 | 2 | 70 | 0.028 |
| 2021-11-01 | 257 | 0 | 257 | 0.000 |
| 2022-01-03 | 114 | 20 | 94 | 0.175 |
| 2022-06-01 | 6 | 0 | 6 | 0.000 |
| 2023-01-03 | 48 | 0 | 48 | 0.000 |
| 2023-11-06 | 492 | 18 | 474 | 0.037 |
| 2024-03-05 | 266 | 18 | 248 | 0.068 |
| 2024-11-01 | 428 | 6 | 422 | 0.014 |
| 2025-01-02 | 76 | 5 | 71 | 0.066 |
| 2025-06-02 | 278 | 8 | 270 | 0.029 |
| 2026-01-02 | 520 | 28 | 492 | 0.054 |
| 2026-06-01 | 555 | 24 | 531 | 0.043 |
| **15-date** | **3890** | **184** | **3706** | **0.047** |

15-date aggregate: 259.3 touches/session, 4.7% hold. Driver three-date subset: 58.0 touches/session, 10.9% hold. Both can be true on this table: three quiet dates sit near 50–90 touches, three busy dates sit near 500.

The gap against REF p.8 (175 touches, 42% hold) is **zone construction first, then the hold label, then market window**. Touch definition is stable (leave 4 ticks, return). Cluster size ≥ 60 (REF p.5) produces 6 zones-worth of touches on 2022-06-01 and 592 on 2020-11-02, so the per-session count is not a property of the touch rule. Hold is OD HOLD_BOUNDARY_TICKS=8 inside 30 minutes on NQ only; the paper does not print a tick cutoff and mixes NQ and MNQ over 235 RTH sessions Dec 24–Nov 25, which is not this 15-date slice. HOLD_BOUNDARY_TICKS was not moved to chase 42%. Bound stays `[80,350]` / `[0.25,0.60]` with the human justification in `processes.json`.

## (i) SIRES episode / bound reasoning

An episode is a **contact at a source-literal location**, not an A+ trade. Locations are overnight and session extremes, overnight LVN / shelf / ledge / minor node, one VWAP-band snapshot, F3 / control-zone edges, and a capped set of swing pivots. Never POC. One contact per location (B0.1 4-tick departure). One side per location (low → long, else short). Cap 16 locations. That is the `[0,16]` bound. It is the source's own location list (ABS p.6; F09), not a number chosen so 624 contacts would fit.

Pass is the setup among those contacts. Source frequency language is "an A++ a handful of times a month" (CONT p.11, OFM p.14) and at most one or two A+ trades per session. Pass_rate `[0.0, 0.20]` (OFM/CONT `[0.0, 0.15]`) is that share, not a fitted envelope around the measurement.

| branch | episode_kind | why that bound |
|---|---|---|
| ten contact branches | contact_at_source_literal_location | `[0,16]` contacts from the F09 location list; pass_rate from one or two A+ among them |
| kg1_retest | contact_at_source_literal_location | `[0,1]`; KG1 unpublished, scan empty |
| ofm_aggressive | session_unknown | `[1,1]` eps, `[0,0]` pass; short-gamma unobservable; one unknown-with-reason per session, not per contact |
| balance_failure_fade | session_unknown | same; long-gamma unobservable; BIG p.14 "80%" is a regime share, not a pass rate |

No branch carries `[0,800]` or source_claim `"unstated"`.
