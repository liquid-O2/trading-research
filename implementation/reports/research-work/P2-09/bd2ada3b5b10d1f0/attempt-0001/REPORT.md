# P2-09 — planning/phase-2/tasks/P2-09.md

Attempt `/workspace/implementation/reports/research-work/P2-09/bd2ada3b5b10d1f0/attempt-0001`. Native slice on 20 engineering dates (2020-01-02 to 2026-09-03), run through `tools/run_context_experts.py slice`.

## Commands

0. `/workspace/implementation/.venv/bin/python -m pytest tests/context_experts/test_p2_09.py -q -p no:cacheprovider` in `/workspace/implementation` exited 0 in 13.7s (log `pytest.log`).
1. `/workspace/implementation/.venv/bin/python tools/run_context_experts.py slice --run-root reports/research-work/phase2-early/run-2026-09-16/P2-09 --manifest reports/research-work/phase2-early/freeze/ENGINEERING_DATES.json --dates 2020-01-02,2020-03-02,2020-03-13,2020-04-01,2020-06-01,2021-01-04,2021-03-01,2021-04-01,2022-01-03,2022-03-01,2022-04-01,2023-01-03,2023-03-13,2023-11-06,2024-01-02,2024-03-01,2025-01-02,2025-03-03,2026-01-02,2026-09-03 --task P2-09` in `/workspace/.worktrees/phase2-early/implementation` exited 0 in 156.2s (log `slice.log`).
2. `/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt /workspace/implementation/reports/research-work/P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json` in `/workspace/implementation` exited 0 in 37.1s (log `predecessor_verify.log`).

## Inspected output

- row /workspace/data/thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42/2024-01-02.parquet:1 of /workspace/data/thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42/2024-01-02.parquet (file sha256 22cf9741ae79784a43b9252ca64da09d9e756e626b36cd65b30f1cd3ac40af3f) replays as QQQ   240111P00422000 bid 15.73 ask 16.38 event_ns 1704205860000000000 available_at_ns 1704205920000000000, synthetic=False. Reading that parquet row directly with pyarrow gives bid 15.73, ask 16.38, ts_event 2024-01-02 14:31:00+00:00.

## Forgery probes

The receipt as issued verifies (control ok=True). 12 of 12 single-gate forgeries are rejected with their intended failure code: remove_artifact -> ARTIFACT_MISSING, substitute_file -> SCHEMA, row_count -> INVENTORY, invalid_json -> JSON_PARSE, plan_digest -> IDENTITY, code_digest -> IDENTITY, run_id -> IDENTITY, omit_owned_file -> INVENTORY, command_log -> ARTIFACT_HASH, predecessor_digest -> PREDECESSOR_HASH, matrix_evidence -> ARTIFACT_HASH, matrix_status -> ACCEPTANCE.

## Limitations

- Slice of 20 engineering dates, not full history; the frozen engineering dates are a subset.
- Exchange-feed completeness is unknown; scoped feeds are labelled scoped, never treated as full chains.
- NQ/ES option quotes are ohlcv-1m last trade as bid=ask mid (no owned option BBO), labelled in the artifact.
- Cash-index intraday spot is not owned, so native NDX/SPX intraday exposure stays unsupported.
- Nothing here is fitted, tuned, ranked or selected, so the blind hold-out 2026-04-01..2026-09-03 is not consumed; 2026-09-03 appears only as a slice date.

## Result card

**Question.** Does every required option root get a dated instrument definition, a causally clocked quote/spot/OI snapshot and an explicit disposition for what is not owned?

| headline | value | unit | support or interval | note |
| --- | --- | --- | --- | --- |
| required option roots with a dated instrument definition | 8 | roots | support 8 | the 8 roots OPTIONS.md requires: NDX, NDXP, SPX, SPXW, QQQ, SPY, NQ, ES |
| root-days with a complete observed-scope disposition | 152 | root-days | support 160 | denominator is every root-day attempted in the slice |
| snapshot quote rows kept by the freshness and crossed filters | 170111 | quote rows | support 215142 | 45031 rejected rows are retained as rejection records, never zero prices |
| slices that used open interest before its publication clock | 0 | slices | support 160 | the assumed clock is the next regular session at 12:00 ET |
| root-days without native intraday spot | 80 | root-days | support 160 | NDX/NDXP/SPX/SPXW cash index, explicitly unsupported |

**Plausibility.**

- the native quote row in SURFACE_INPUT_SLICE replays to its own parquet row: observed QQQ 2024-01-11 P422 bid 15.73 ask 16.38 at event_ns 1704205860000000000; expected bid 15.73, ask 16.38, ts_event 2024-01-02 14:31:00+00:00 read straight from the file with pyarrow (plausible)
- the OI vintage used at the 10:00 ET asof was published before it: observed effective session 2023-12-28, available_at_ns 1703869200000000000; expected the 2023-12-28 session published 2023-12-29 12:00 ET, before the 2024-01-02 10:00 ET asof (plausible)
- the share of snapshot quote rows rejected by the freshness and crossed filters: observed 0.2093; expected 0.05 to 0.35 for a scoped one-minute option feed snapshotted at 10:00 ET, where far strikes are stale (plausible)

**Target.** Card P2-09 A01-A08: distinct expiry clocks, no pre-publication OI, no look-ahead strikes, rejections rather than zero prices, reconciled coverage denominators, and bound evidence. **Met:** yes.

**Verdict.** needs_upgrade — The adapters carry every owned input with dated definitions and explicit dispositions, but two of the six required underlyings have no owned two-sided option quote (NQ/ES use a one-minute last-trade mid) and the cash indices have no owned intraday spot, so the surface inputs are thin where the contract wants a chain.

**Lever.** Own an option BBO or MBP schema for NQ and ES, and an intraday NDX/SPX print. Evidence that it worked: The same 20-date slice would show live contracts per board in the tens or hundreds for NQ and ES instead of 1 and 6, in OPTIONS_AVAILABILITY.board_depth_20date and EXPOSURE_BOARDS.depth_by_root.

**Limits.**

- Slice of 20 engineering dates, not full history; the frozen engineering dates are a subset.
- Exchange-feed completeness is unknown; scoped feeds are labelled scoped, never treated as full chains.
- NQ/ES option quotes are ohlcv-1m last trade as bid=ask mid (no owned option BBO), labelled in the artifact.
- Cash-index intraday spot is not owned, so native NDX/SPX intraday exposure stays unsupported.
- Nothing here is fitted, tuned, ranked or selected, so the blind hold-out 2026-04-01..2026-09-03 is not consumed; 2026-09-03 appears only as a slice date.
