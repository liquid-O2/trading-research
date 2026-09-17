# P2-03 — planning/phase-2/tasks/P2-03.md

Attempt `/workspace/.worktrees/phase2-early/implementation/reports/research-work/P2-03/a1446a39485fc037/attempt-0001`. Native slice on 20 engineering dates (2020-01-02 to 2026-09-03), run through `tools/run_context_experts.py slice`.

## Commands

0. `/workspace/implementation/.venv/bin/python -m pytest tests/context_experts/test_p2_03.py -q -p no:cacheprovider` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 8.2s (log `pytest.log`).
1. `/workspace/implementation/.venv/bin/python tools/run_context_experts.py slice --run-root reports/research-work/phase2-early/run-2026-09-16/P2-03 --manifest reports/research-work/phase2-early/freeze/ENGINEERING_DATES.json --dates 2020-01-02,2020-03-02,2020-03-13,2020-04-01,2020-06-01,2021-01-04,2021-03-01,2021-04-01,2022-01-03,2022-03-01,2022-04-01,2023-01-03,2023-03-13,2023-11-06,2024-01-02,2024-03-01,2025-01-02,2025-03-03,2026-01-02,2026-09-03 --task P2-03` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 136.9s (log `slice.log`).
2. `/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt /workspace/implementation/reports/research-work/P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 37.4s (log `predecessor_verify.log`).
3. `/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt /workspace/.worktrees/phase2-early/implementation/reports/research-work/P2-10/84b565a87314716d/attempt-0001/TASK_RECEIPT.json` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 42.6s (log `predecessor_verify_P2-10.log`).

## Inspected output

- target row 2020-01-02 issued at 1577977200000000000 with sampling bbo_midpoint_age_le_5s: head rv_15m status ok value 2.0536418203011475e-06 over [1577977200000000000, 1577978100000000000], known at None.

## Forgery probes

The receipt as issued verifies (control ok=True). 12 of 12 single-gate forgeries are rejected with their intended failure code: remove_artifact -> ARTIFACT_MISSING, substitute_file -> SCHEMA, row_count -> INVENTORY, invalid_json -> JSON_PARSE, plan_digest -> IDENTITY, code_digest -> IDENTITY, run_id -> IDENTITY, omit_owned_file -> INVENTORY, command_log -> ARTIFACT_HASH, predecessor_digest -> PREDECESSOR_HASH, matrix_evidence -> ARTIFACT_HASH, matrix_status -> ACCEPTANCE.

## Limitations

- Features and targets are built on 20 engineering dates, not the full history.
- Realized variance uses native BBO midpoints with age<=5s; a missing boundary makes the target incomplete rather than bridged, and the minute-close series is kept only as a labelled comparison.
- No forecast is fitted here; the joint volatility fit, its ablations and its horizons are P2-04.
- 2026-09-03 lies inside the blind hold-out 2026-04-01..2026-09-03 and appears only as an incomplete-target record; nothing here is fitted, tuned, ranked or selected.

## Result card

**Question.** Do the volatility estimators reproduce their literal fixtures, and do the multi-horizon targets come from native midpoints without crossing a close, a roll or an unavailable boundary?

| headline | value | unit | support |
| --- | --- | --- | --- |
| Garman-Klass fixture variance | 0.020134364008631726 | interval log-return variance | contract worked example .5*ln(110/90)^2 |
| realized-variance fixture | 0.00019801816817500913 | interval log-return variance | contract worked example 2*ln(1.01)^2 |
| days with a complete target row | 19 | days | 20 slice days, 1 incomplete with a reason |
| target heads complete | 139 | heads | 152 heads on 19 complete days (8 named heads per day); incomplete: {'remaining_account_day/missing_boundary_midpoint': 13}; horizons unsupported for crossing a close or roll: none |
| IV feature groups with a disposition | 3 | groups | each requested group is consumed or carries a missing-group record |

**Target.** Card P2-03 A01-A08: GK/YZ/RV worked examples, separated variance units, unsupported rather than truncated horizons, a disposition for every requested IV group, and no future price in a current feature. **Met:** partial.

**Verdict.** needs_upgrade — The estimators reproduce every literal fixture to 1e-15 and 139 of 152 heads are built from native BBO midpoints with explicit incomplete records for the rest, but the feature side is the arithmetic core only: 3 IV groups are requested where VOLATILITY.md names six root board groups plus the VIX family, and session seasonality and the rolling historical feature bank are not built yet.

**Lever.** Extend the feature builder to request every IV group named in VOLATILITY.md with a per-group disposition and add the session-bucket and rolling GK/YZ features, before P2-04 fits the joint model; VOLATILITY_FEATURES rows would then carry a disposition per named group rather than three.

**Limits.**

- Features and targets are built on 20 engineering dates, not the full history.
- Realized variance uses native BBO midpoints with age<=5s; a missing boundary makes the target incomplete rather than bridged, and the minute-close series is kept only as a labelled comparison.
- No forecast is fitted here; the joint volatility fit, its ablations and its horizons are P2-04.
- 2026-09-03 lies inside the blind hold-out 2026-04-01..2026-09-03 and appears only as an incomplete-target record; nothing here is fitted, tuned, ranked or selected.
