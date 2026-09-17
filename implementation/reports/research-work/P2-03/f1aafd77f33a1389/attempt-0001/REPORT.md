# P2-03 — planning/phase-2/tasks/P2-03.md

Attempt `/workspace/.worktrees/phase2-early/implementation/reports/research-work/P2-03/f1aafd77f33a1389/attempt-0001`. Native slice on 20 engineering dates (2020-01-02 to 2026-09-03), run through `tools/run_context_experts.py slice`.

## Commands

0. `/workspace/implementation/.venv/bin/python -m pytest tests/context_experts/test_p2_03.py -q -p no:cacheprovider` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 13.0s (log `pytest.log`).
1. `/workspace/implementation/.venv/bin/python tools/run_context_experts.py slice --run-root reports/research-work/phase2-early/run-2026-09-16/P2-03 --manifest reports/research-work/phase2-early/freeze/ENGINEERING_DATES.json --dates 2020-01-02,2020-03-02,2020-03-13,2020-04-01,2020-06-01,2021-01-04,2021-03-01,2021-04-01,2022-01-03,2022-03-01,2022-04-01,2023-01-03,2023-03-13,2023-11-06,2024-01-02,2024-03-01,2025-01-02,2025-03-03,2026-01-02,2026-09-03 --task P2-03` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 136.9s (log `slice.log`).
2. `/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt /workspace/implementation/reports/research-work/P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 39.6s (log `predecessor_verify.log`).
3. `/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt /workspace/.worktrees/phase2-early/implementation/reports/research-work/P2-10/e39e05c1a0029051/attempt-0001/TASK_RECEIPT.json` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 44.1s (log `predecessor_verify_P2-10.log`).

## Inspected output

- target row 2020-01-02 issued at 1577977200000000000 with sampling bbo_midpoint_age_le_5s: head rv_15m status ok value 2.0536418203011475e-06 over [1577977200000000000, 1577978100000000000], known at None.

## Forgery probes

The receipt as issued verifies (control ok=True). 12 of 12 single-gate forgeries are rejected with their intended failure code: remove_artifact -> ARTIFACT_MISSING, substitute_file -> SCHEMA, row_count -> INVENTORY, invalid_json -> JSON_PARSE, plan_digest -> IDENTITY, code_digest -> IDENTITY, run_id -> IDENTITY, omit_owned_file -> INVENTORY, command_log -> ARTIFACT_HASH, predecessor_digest -> PREDECESSOR_HASH, matrix_evidence -> ARTIFACT_HASH, matrix_status -> ACCEPTANCE.

## Limitations

- Features and targets are built on 20 engineering dates, not the full history.
- Realized variance uses native BBO midpoints with age<=5s; a missing boundary makes the target incomplete rather than bridged, and the minute-close series is kept only as a labelled comparison.
- No forecast is fitted here; the joint volatility fit, its ablations and its horizons are P2-04.
- Headline rows whose interval is [value, value] are deterministic identity checks against the contract's literal worked example: the inputs are fixed, so the interval is the value itself and not a sampling interval.
- Nothing here is fitted, tuned, ranked or selected, so the blind hold-out 2026-04-01..2026-09-03 is not consumed; 2026-09-03 appears only as a slice date.

## Result card

**Question.** Do the volatility estimators reproduce their literal fixtures, and do the multi-horizon targets come from native midpoints without crossing a close, a roll or an unavailable boundary?

| headline | value | unit | support or interval | note |
| --- | --- | --- | --- | --- |
| Garman-Klass fixture variance | 0.020134364008631726 | interval log-return variance | interval [0.020134364008631726, 0.020134364008631726] | deterministic identity against the VOLATILITY.md worked example .5*ln(110/90)^2 |
| realized-variance fixture | 0.00019801816817500913 | interval log-return variance | interval [0.00019801816817500913, 0.00019801816817500913] | deterministic identity against the worked example 2*ln(1.01)^2 |
| slice days with a complete target row | 19 | days | support 20 | 1 incomplete day rows, each with a reason |
| target heads complete | 139 | heads | support 152 | 8 named heads on 19 complete days; incomplete: {'remaining_account_day/missing_boundary_midpoint': 13}; horizons unsupported for crossing a close or roll: none |
| IV feature groups requested with a disposition | 3 | groups | support 10 | VOLATILITY.md names ten IV groups (NDX/NDXP, SPX/SPXW, QQQ, SPY, NQ, ES boards and the VIX, VX, VVIX, VXN series); this build requests three and each carries a disposition |

**Plausibility.**

- the Garman-Klass fixture against the contract's worked example: observed 0.020134364008631726; expected 0.5*ln(110/90)^2 = 0.020134364008631726 (plausible)
- the 2020-01-02 rv_15m head against an independent recomputation from the raw NQ MBP-1 parquet: observed 2.0536418203011475e-06; expected 2.0536418203011475e-06 from 16 one-minute boundaries, last midpoint with age<=5s; sqrt is 0.14% of price over 15 minutes, which is ordinary for NQ at 10:00 ET (plausible)
- where the incomplete target heads fall: observed 13 of 152 heads, all ['remaining_account_day/missing_boundary_midpoint']; expected only the account-day head, whose end boundary at the 17:00 ET close has no midpoint within 5 seconds; the fixed 15/30/60/120-minute heads are complete (plausible)

**Target.** Card P2-03 A01-A08: GK/YZ/RV worked examples, separated variance units, unsupported rather than truncated horizons, a disposition for every requested IV group, and no future price in a current feature. **Met:** partial.

**Verdict.** needs_upgrade — The estimators reproduce every literal fixture to 1e-15 and 139 of 152 heads are built from native BBO midpoints with explicit incomplete records for the rest, but the feature side is the arithmetic core only: 3 IV groups are requested where VOLATILITY.md names ten, and session seasonality and the rolling historical feature bank are not built yet.

**Lever.** Extend the feature builder to request every IV group named in VOLATILITY.md with a per-group disposition, and add the session-bucket and rolling GK/YZ features, before P2-04 fits the joint model. Evidence that it worked: VOLATILITY_FEATURES rows would carry ten group dispositions instead of three, and the A3 (IV-only) and A5 (joint) ablations in P2-04 would then be separable.

**Limits.**

- Features and targets are built on 20 engineering dates, not the full history.
- Realized variance uses native BBO midpoints with age<=5s; a missing boundary makes the target incomplete rather than bridged, and the minute-close series is kept only as a labelled comparison.
- No forecast is fitted here; the joint volatility fit, its ablations and its horizons are P2-04.
- Headline rows whose interval is [value, value] are deterministic identity checks against the contract's literal worked example: the inputs are fixed, so the interval is the value itself and not a sampling interval.
- Nothing here is fitted, tuned, ranked or selected, so the blind hold-out 2026-04-01..2026-09-03 is not consumed; 2026-09-03 appears only as a slice date.
