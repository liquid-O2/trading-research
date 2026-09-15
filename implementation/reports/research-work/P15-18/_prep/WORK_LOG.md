# P15-18 engineering-prep work log

Engineering preparation only. No receipt, no native run, no research result.

## Environment

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -c "import trading_research; print(trading_research.__file__)"
```

Exit 0. File is `/workspace/.worktrees/p15-18-refinement-prep/implementation/src/trading_research/__init__.py`.

Without `PYTHONPATH=src` the venv resolves `/workspace/implementation/src/trading_research/__init__.py`. Always set `PYTHONPATH=src` and cwd `implementation`.

## Design decisions

- Neighborhoods live in a recipe-keyed registry, not per-family if/else chains.
- TrialRecord is a plain dict. Ledger is append-only JSONL.
- `holm` and `moving_block_bootstrap` are imported from `trading_research.research.contracts.evaluation` and never copied.
- Guard flags default on so negative-control tests can disable one behaviour at a time.
- P15-17 artifacts do not exist. Input shapes are assumed in `PROPOSED_INTEGRATION.md`.
- architect skipped: agent cap of one code writer; SEARCH_CONTRACT already specifies the table, caps, fields and vocabulary. Design is this directory, not a silent implementation choice.
- Opening a PR skipped: the task forbids git commands.
- how skipped: DESIGN.md and SEARCH_CONTRACT.md already specify the one new module. There is no existing refinement runtime to walk.
- no-comments skipped: single-writer constraint. Comments kept only for the `_CAP` overflow why.

## Commands

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -c "import trading_research; print(trading_research.__file__); assert '/workspace/.worktrees/p15-18-refinement-prep/' in trading_research.__file__"
```

Exit 0. Printed `/workspace/.worktrees/p15-18-refinement-prep/implementation/src/trading_research/__init__.py`.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_18.py -q --tb=short
```

Exit 1. 3 failed, 36 passed. T1/T2 parent `shift_minutes` matched a neighborhood value and those rows were `duplicate` instead of `past_only_allowlist` / `formation_unavailable`. Fixtures were changed so parent parameters do not include a grid shift.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_18.py -q --tb=short
```

Exit 0. 39 passed in 2.21s.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/contracts -q --tb=short
```

Exit 0. 5 passed in 18.64s.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_18.py -q --tb=short
```

Exit 0. 39 passed in 2.02s. Re-run after moving `_CAP` to the end of `NEIGHBORHOODS`.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -c "import trading_research; print(trading_research.__file__); assert '/workspace/.worktrees/p15-18-refinement-prep/' in trading_research.__file__"
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_18.py tests/contracts -q --tb=short
```

Exit 0. 44 passed in 20.08s (39 P15-18 + 5 contracts, before the inner-support test).

Decision: `_inner_support_ok` treated a missing-or-false flag as a fall-through to opportunity counts, so `inner_support_ok=False` with positive counts still selected the bank. The helper now honors an explicit flag.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_18.py -q --tb=short
```

Exit 1. `test_inner_support_ok_false_excludes_bank` expected `["cB", "cC"]` but `select_banks` sorts the kept banks by bank name, so Delta then Profile (`["cC", "cB"]`).

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_18.py -q --tb=short
```

Exit 0. 40 passed in 2.16s.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/contracts -q --tb=short
```

Exit 0. 5 passed in 18.52s.

## Defect fixes (test-only `_CAP`, retention vocabulary, Holm-adjusted p)

Removed `_CAP` from `NEIGHBORHOODS`. Cap overflow uses the `refinement_axis` / `refinement_values` fallback. `family_dispositions` now requires `RETENTION_STATUSES`. `p_holm` is derived from `holm_fn` rows (`p * alpha / threshold` with a running maximum). `_holm_adjusted` is deleted.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -c "import trading_research; assert '/workspace/.worktrees/p15-18-refinement-prep/' in trading_research.__file__; from trading_research.research.rule_discovery.refinement import NEIGHBORHOODS; print(sorted(NEIGHBORHOODS)); print(len(NEIGHBORHOODS))"
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/rule_discovery/test_p15_18.py -q --tb=short
```

Exit 0. Printed the 20 contract recipe ids. 42 passed in 2.16s.

```
cd /workspace/.worktrees/p15-18-refinement-prep/implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider tests/contracts -q --tb=short
```

Exit 0. 5 passed in 21.43s.
