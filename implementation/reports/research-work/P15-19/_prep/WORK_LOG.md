# P15-19 engineering prep work log

Commands, exit codes, and decisions. Not a research result.

## Environment

- Worktree: `/workspace/.worktrees/p15-19-exits-prep`
- Python: `/workspace/implementation/.venv/bin/python`
- cwd: `/workspace/.worktrees/p15-19-exits-prep/implementation`
- PYTHONPATH: `src`

## Commands

```
cd /workspace/.worktrees/p15-19-exits-prep/implementation && PYTHONPATH=src /workspace/implementation/.venv/bin/python -c "import trading_research, pathlib; p=pathlib.Path(trading_research.__file__).resolve(); print(p); assert str(p).startswith('/workspace/.worktrees/p15-19-exits-prep/'), p"
```

Exit code: 0. Path: `/workspace/.worktrees/p15-19-exits-prep/implementation/src/trading_research/__init__.py`

```
# native view probe under install_write_guard
```

Exit code: 0. `build_market_view` loads. `list(view.quotes())` raises `ContractError: ask must be at least bid`. On 2020-01-02: 190809 timestamp batches, 190807 usable, 2 crossed.

```
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_19.py -q --tb=short -k 'not native_chronological'
```

Exit code: 0. 12 passed, 1 deselected.

```
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_19.py::test_native_chronological_slice_reconciliation -q --tb=short
```

Exit code: 0. 1 passed in 155.51s.

```
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_19.py tests/contracts -q --tb=short
```

Exit code: 0. 18 passed in 175.35s (13 in test_p15_19.py, 5 in tests/contracts).

```
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_19.py -q --tb=short -k 'not native_chronological'
```

Exit code: 0. 15 passed, 1 deselected (accounting fixes).

```
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_19.py tests/contracts -q --tb=short
```

Exit code: 0. 21 passed in 174.62s (16 in test_p15_19.py, 5 in tests/contracts). Regenerated SLICE_EXITS.json and RECONCILIATION.json.

```
git -C /workspace/.worktrees/p15-19-exits-prep status --short
```

Exit code: 0. Untracked: `implementation/reports/research-work/P15-19/`, `exits.py`, `test_p15_19.py`.

## Decisions

1. Do not call `replay_family` for E0-E4. Occupancy would change. Trailing and break-even are absent there.
2. Quote age is 1 second (`MAX_QUOTE_AGE_NS`). The 5-second figure is the search window after trigger plus 250 ms (`ENTRY_WINDOW_NS`).
3. Same-timestamp batches keep every bid, ask, and trade price via extrema. If stop and objective both hit, the exit reason is the stop family. `first_passage` is unchanged.
4. Frozen B0.2 fill time is `decision_at`. Fill price is stated geometry. Quantity is always 1 NQ mini.
5. Geometry integers with magnitude >= 30000, or field names ending `_ticks`, convert with `ticks_to_decimal`.
6. Break-even stop is `entry + side * (round_trip_dollars / 20)` then tightened. Default round-trip dollars `5.00`.
7. Native jobs path: `/workspace/implementation/reports/research-work/P15-16A/1e13829f2c88f1e1/jobs`.
8. Slice dates: 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-03, 2023-11-06, 2024-01-02, 2024-07-01, 2025-01-02, 2026-01-02, 2026-09-03.
9. Flatten on the slice is `account_day_window` end minus 60 seconds.
10. `install_write_guard()` before every `build_market_view`.
11. Architect arena skipped. Live-agent cap of two, one reserved for the code writer. The writer stalled on reads. The lead implemented against the locked sketch.
12. Source deadline on B0.2 episodes is `geometry.objective_horizon_ns` or `geometry.cancel_ns` when present.
13. Native quotes are BBO on trade prints. Crossed last-row BBO is skipped.
14. Cross-model trail review skipped. Same agent cap.

15. `UnsupportedRecord` is only undefined initial R on E3/E4. A missing executable quote is `IncompleteExit` (`incomplete_no_quote`). Reconciliation keeps those as two fields.
16. Slice `account_day` is the loop date, not `episode["session_date"]`.
17. `StopUpdate` stores the effective batch id and `available_at_ns`. An auditor can check effective time is after trigger time.

## Notes

Slice net points and reason counts are descriptive machinery output. They are not a research result.

## Corrected per-policy table (descriptive)

1330 entries. `reason_sum + unsupported_undefined_r + incomplete_no_quote == 1330` on every policy. E0–E2 have `unsupported_undefined_r == 0`.

| Policy | stop | objective | expiry | source deadline | account-day close | break-even | trailing | undefined R | incomplete no quote | net points |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 157 | 47 | 14 | 1108 | 0 |  |  | 0 | 4 | 2977.75 |
| E1 | 146 | 43 | 29 | 1108 | 0 |  |  | 0 | 4 | 2985.75 |
| E2 | 160 | 48 | 9 | 1108 | 1 |  |  | 0 | 4 | 2666.75 |
| E3 | 89 | 44 | 0 | 1108 | 2 | 80 |  | 0 | 7 | 2903.25 |
| E4 | 89 | 33 | 0 | 1108 | 1 |  | 96 | 0 | 3 | 3153.25 |
