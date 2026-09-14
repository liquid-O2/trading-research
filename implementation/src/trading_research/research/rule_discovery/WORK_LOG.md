# B0.1 baseline repairs work log

Worktree `/workspace/.worktrees/baseline-repair`, branch `fix/baseline-repairs`. Frozen `method_pack` files were not edited. No writes under `/workspace/data`, `/workspace/sources`, or `implementation/reports/phase1-live`. No git commit/push/checkout/reset/stash.

Python: `/workspace/implementation/.venv/bin/python`. Commands below used `cwd=implementation` and `PYTHONPATH=src` unless noted.

## Decisions

- **REPAIRS branch IDs** come from run-1.0.1 `coverage.json` as `{method}:branch:{branch}`. Extra units are not repaired.
- **Dispatcher.** A coverage id in any REPAIRS entry goes to the family scanner that includes every applicable repair for that branch. Other branches call `native_discovery.scan_branch` and get `baseline_version=B0`. Repaired records keep the frozen `scanner` identity and add `baseline_version=B0.1-2026-09-14`.
- **D1.** Do not rebind `continuation_context`. Line 308's breakout-context conjunct stays. The retest conjunct is rebound onto `retest_at`/`retest_low`/`retest_high` with the original "no later VWAP retest" operation. Missing retest therefore stays unknown via `breakout_at < retest_at`, not a failed context.
- **P2 + D1 on f2.** FINDINGS expected `continuation_context is None` if line 314 called a repaired `absent()`. Combined with D1, line 314 no longer writes `continuation_context`, so the breakout conjunct stays True and unknown comes from the retest operand / zero-length stage. Direct `absent(m,t,t) is False` vs `absent_repaired is None` still exhibits P2.
- **P2 scanners.** `absent_repaired` is used by corrected `scan_saint`, `scan_member`, `scan_keani`, `scan_green_vwap`, `_ob`/`scan_jumbo`, and `_control_absence`. JJ-TBR `judas_outbound` does not call `absent()` and is not in REPAIRS (parity target).
- **P4.** Empty sweep path appends `kind=availability` omission, binds `sweep_high`/`sweep_low`/`stop` as None, and still emits the episode. Verdict is unknown on the f4 tape.
- **P1 empty chunks.** Empty 5-second windows are recorded with `opposing=0`. `low`/`high` are inverted band bounds (`hi+Q`,`lo-Q`) so frozen `flow_stages` comparisons stay defined and do not count a phantom contact. Extra key `empty_window=True`.
- **P6.** Dedup key is `(ref.id or hash(bounds, kind), side)`. On the exact f3 tape, kg1-b's first bar-contact spans `[120,120.5]` because the 100.25 coverage print shares the 150-print minute, so `exact_contact` is None and no kg1-b episode is emitted even after the key fix. Tests keep the fixture tape for frozen collapse, and add a 09:31 120.25 print on a second market so repaired emits both ids. Reconstruction census still has one KG1 level, so the 40-date preview shows no extra kg1 episodes.
- **Census dates.** `extract_b.py` JSON was absent. Dates were rebuilt with the same formula: 1742 `jobs/evaluation` session dirs, `idx=round(i*(N-1)/39)` for i in 0..39. List starts 2020-01-01, includes 2023-12-08, 2026-05-01, 2026-07-02, ends 2026-09-03.
- **Preview harness.** `event_cache.build_event_window` is blocked only in `repair-preview/run_preview.py` via `install_write_guard`. `HistoricalFeatures(day, records=hr._records(registry))` with `load_registry(..., check_software=False)`. Eight worker processes.
- **Copied helpers.** Unchanged helpers stay imported from the frozen modules. Copied function bodies rewrite in-function relative imports to absolute `trading_research.research.method_pack.*` paths.

## Commands

```
# compile after generating the module
/workspace/implementation/.venv/bin/python -m py_compile implementation/src/trading_research/research/rule_discovery/baseline_repairs.py
# exit 0
```

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider -q tests/rule_discovery/test_baseline_repairs.py --tb=short
# final: 10 passed in 7.67s, exit 0
```

Earlier pytest iterations: 3 failed then 1 failed (P1 dict-of-triples, P6 kg1-b exact-contact, D1 retest on mixed 100/105 tape, D1 `operand_derivations` looked up on `values`). All fixed in the test file; last run is the one above.

```
PYTHONPATH=src /workspace/implementation/.venv/bin/python \
  planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview/run_preview.py
# first run exit 0 but SIRES footprint_confirmed_reaction NameError: defaultdict
# after `from collections import defaultdict`: exit 0, 40/40 dates ok, orchestrator_wall_s 637.3658
```

Timing probe (2023-12-08, four branches) exit 0: GB-VWAP fail 1 → unknown 1 under B0.1, matching D1.

## Preview result (not a receipt)

On the 40-date pool, verdict changes are only:

- GB-VWAP source_long: 17 fail→unknown (all census GB-VWAP rejections; no-setup→data_unavailable).
- SAINT-AMT continuation_retest 1, failed_auction_return 1, poc_traversal 2 fail→unknown (4 total, matching the rejection audit's decisive P2 count).
- P1, P4, P6, JJ-TBR, MEMBER, KEANI, remaining GB-FAIL/SIRES: 0 verdict changes on this tape.

## Not done

- No real-data pytest for `repro_d1.py` / `repro_p2_saint.py` against `/workspace/data` (write guard). Those dates are in the in-process preview.
- P3/P5/P7 were out of scope.
- Generator script used to copy frozen bodies was not kept.
