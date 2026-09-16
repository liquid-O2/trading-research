# CLOSURE REPORT — P15-16A B0.2 repair, Green Bird track

Worktree `/workspace/.worktrees/b02r-greenbird` branch `p15/b02r-greenbird`. No git commit. No receipts. No wiki. No writes under `/workspace/data` from this track's after-tape path.

## (a) Stages measured

Every B0.2 branch in STAGE_AUDIT_GB-FAIL / GB-VWAP / GB-SCALP has all eight stages measured. Gate `_audit_unmeasured` is empty.

| branch | unmeasured |
| --- | --- |
| london_box, asia_box, asia_tdo_case, prior_day_level, nyam_box, previous_hour, nwog, cash_open_reclaim_case, golden_pocket, ny_session_extreme, source_long, golden_pocket_continuation | none |

`ny_session_extreme` is new: 09:30–11:00 NY range frozen at 11:00, at-level sweep-and-fail after 11:00, objective the opposite frozen edge. Fixture `test_ny_session_extreme_afternoon_sweep_fail` uses the 10:55 low / 15:35 sweep.

London risk has two dated placements, not one formula: retest higher-low (2026-09-14) and sweep-extreme + 11.75 buffer (2026-09-15). Ladder author spacing 8–33.

## (b) Fifteen-date density

Slice: 2020-01-02 … 2026-06-01 (15 sessions). Bounds unchanged. No `observed_rate_justification`.

| branch | eps/session | n | pass | fail | unk | pass_rate | sess-with-pass | bound | in/out |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| london_box | 1.00 | 15 | 2 | 13 | 0 | 0.133 | 2/15 | eps [0,2] pr [0,0.55] | in |
| asia_box | 1.00 | 15 | 8 | 7 | 0 | 0.533 | 8/15 | eps [0,2] pr [0,0.70] | in |
| asia_tdo_case | 1.00 | 15 | 4 | 11 | 0 | 0.267 | 4/15 | eps [0,2] pr [0,0.65] | in |
| prior_day_level | 2.00 | 30 | 12 | 18 | 0 | 0.400 | 10/15 | eps [0,4] pr [0,0.60] | in |
| nyam_box | 2.60 | 39 | 10 | 29 | 0 | 0.256 | 8/15 | eps [0,12] pr [0,0.40] | in |
| previous_hour | 4.00 | 60 | 8 | 52 | 0 | 0.133 | 8/15 | eps [0,16] pr [0,0.35] | in |
| nwog | 1.40 | 21 | 4 | 16 | 1 | 0.191 | 4/15 | eps [0,4] pr [0,0.25] | in |
| cash_open_reclaim_case | 1.00 | 15 | 3 | 12 | 0 | 0.200 | 3/15 | eps [0,2] pr [0,0.50] | in |
| golden_pocket | 1.00 | 15 | 4 | 11 | 0 | 0.267 | 4/15 | eps [0,2] pr [0,0.30] | in |
| ny_session_extreme | 2.00 | 30 | 5 | 25 | 0 | 0.167 | 5/15 | eps [0,2] pr [0,0.20] | in |
| GB-VWAP source_long | 1.00 | 15 | 1 | 14 | 0 | 0.067 | 1/15 | eps [0,1] pr [0,0.50] | in |
| GB-SCALP golden_pocket_continuation | 1.00 | 15 | 1 | 14 | 0 | 0.067 | 1/15 | eps [0,2] pr [0,0.35] | in |

Across london/asia/nyam/previous_hour: 28 passes / 15 = **1.867** bound [0,2] **in**.

Mutated-bound self-test: copy family JSON, set `asia_box.pass_rate=[0,0]`, drop any justification. Measured asia pass_rate 0.533 is out of bound and `_human_justification` is None. **PASSED**.

## (c) Author examples

| id | reached_location | detected | failing_operand | divergence |
| --- | --- | --- | --- | --- |
| GB-2025-11-20 | yes | no | no_close_back_inside_fail_window | miss_after_location:confirmation:… |
| GB-2025-11-19 | yes | no | window_or_branch_mismatch | miss_after_location:detection:… |
| GB-2026-04-23 | yes | no | no_close_back_inside_fail_window | miss_after_location:confirmation:… |
| GB-2026-04-28 | yes | no | no_close_back_inside_fail_window | miss_after_location:confirmation:… |
| GB-2026-07-13 | yes | no | no_close_back_inside_fail_window | miss_after_location:confirmation:… |
| GB-2026-07-29-30 | yes | no | no_close_back_inside_fail_window | miss_after_location:confirmation:… |
| GB-2026-08-11-12 | yes | no | no_reclaim_close_above_open | miss_after_location:confirmation:… |
| GB-2026-08-13 | yes | no | no_close_back_inside_fail_window | miss_after_location:confirmation:… |
| GB-2026-08-27 … GB-2026-09-14 | n/a | None | n/a (data_unavailable) | date outside the tape |
| GB-2026-09-15 | n/a | None | n/a (data_unavailable) | date outside the tape |

Every `detected=False` row names `failing_operand`. After-tape returns before any market view. GB-2026-09-15 in the worktree examples file is object-equal to main.

## (d) Tests

| command | result |
| --- | --- |
| `pytest -p no:cacheprovider tests/rule_discovery/test_p15_16a_greenbird.py -k "not nine_date and not author_example_replay"` | 26 passed, 1 deselected |
| `pytest -p no:cacheprovider tests/rule_discovery/test_p15_16a_plausibility_greenbird.py::test_p15_16a_plausibility_greenbird_gate` | 1 passed in 157.90s |
| `pytest -p no:cacheprovider tests/rule_discovery/test_p15_16a_plausibility_greenbird.py -k "not test_p15_16a_plausibility_greenbird_gate"` | 3 passed (mutation, replay operands, after-tape monkeypatch) |
| `pytest -p no:cacheprovider tests/rule_discovery` | **473 passed, 0 failed** in 1959.62s |
| B0/B0.1 hashes on 2020-01-02 and 2021-01-04 | asserted inside the gate and `test_b0_b01_byte_identity_two_slice_dates` |
| `test_direct_reclaim_stop_is_sweep_buffer_not_retest_low` | pass; applying retest-HL stop fails |
| `test_retest_stop_is_not_sweep_buffer` | pass; applying sweep-buffer stop fails |
| `test_mutated_asia_box_bound_fails_the_gate` | pass |
| `test_after_tape_replay_does_not_call_build_event_window` | pass |

## (e) MERGE_NOTES

`runner.py` is a two-hunk restore of main (drop `directory_listing_digest`, `code_files = {rel: file_digest(...)}`). Keep main's file. Other tracks' hunks on the same lines differ; this track's reason is import breakage of `load_source_market`, not a family feature. No `common.py` / `confirmation.py` edits. New GB-FAIL branch `ny_session_extreme`. Two dated London stops. Ladder 8–33. Do not add `observed_rate_justification` to silence the gate.

## (f) Remaining limitations

- Inside-tape author fills still miss after location because at-level confirmation is the sweep's 5-minute clock bar plus the next 1-minute hold (RR-13 / GB p.58). The November 20 print is at the high; the scanner records `no_close_back_inside_fail_window`.
- GB-2026-07-13 is an Asia-session PDL long; F06 A2 baseline is Asia-high short. Not moved to make the fill pass.
- F07 bias is reported, not a scanner cap.
- Grey 10:00–11:00 is painted live on Sep-2026 charts and listed in RR-11 variants; it is not an independent fail scan (it was producing more A+ than the green 9–10 box).
- After-tape examples stay `data_unavailable` until tape after 2026-08-19 is owned.
- Concurrent sibling tracks wrote derived-cache entries at 00:10 UTC for 2026-05-29 and 2026-09-14. This track's after-tape replay does not call `build_event_window` (monkeypatch). The full suite after the freeze did not add newer derived entries.

## (g) git status --short

```
 M implementation/src/trading_research/research/rule_discovery/families/green_failure.json
 M implementation/src/trading_research/research/rule_discovery/families/green_vwap_scalp.json
 M implementation/src/trading_research/research/rule_discovery/runner.py
 M implementation/src/trading_research/research/rule_discovery/source_adapters/green_b02.py
 M implementation/tests/rule_discovery/test_p15_16a_greenbird.py
 M planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json
?? implementation/reports/research-work/P15-16A/_repair_greenbird/
?? implementation/tests/rule_discovery/test_p15_16a_plausibility_greenbird.py
```

AUTHOR_EXAMPLES diff is only the added `GB-2026-09-15` object, equal to main's entry.

## Restored `_track_greenbird` sha256

| file | sha256 |
| --- | --- |
| FUNNEL_GB-FAIL.json | `415af2eef2e8d2af5eb7b9dbb2f242ec4ba5e334962e2b620688fdfff683fd59` |
| FUNNEL_GB-SCALP.json | `35e65593fd20c0f931a2eaa82d31dd6cc9b2385fe8b2a997ac8ca892b0928d74` |
| FUNNEL_GB-VWAP.json | `d2ad319aaeb64b18735f9c0d2bfade672bb10a4c5fe55edd113cf473d1757756` |
| REPLAY_GB.json | `96fb13cf707de73cec6657df4828989f830d64875de6874c214d66e4dfd6124e` |
| RULES_GB.json | `fb6abaf6988425a259dc7c2d1efbf18ba63efa8600958ac9812183439e57f735` |
