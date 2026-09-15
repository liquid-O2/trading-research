# Proposed integration for the P15-19 run step

This file is a coordinator request. It is not applied. Prep implemented `exits.py` and `test_p15_19.py` only.

## What the run still needs

P15-18 has not produced `SELECTED_RULES_BY_FOLD.json`. Prep froze B0.2 pass episodes with defined stop and objective. The run must freeze the selected-rule entries from P15-18 instead.

## `SELECTED_RULES_BY_FOLD.json` shape the run will consume

P15-18 is still planned. Until that artifact exists, treat this as the contract the run should parse, not as an observed file.

Per outer fold (one object, keyed by fold id such as `test_year=2022`):

- `fold_id`
- `test_year`
- `fit` / `tune` / `test` date lists (account-day strings)
- `outcome_exposure_cutoff_ns`
- `families`: list of
  - `family`, `branch`
  - `selected_rule_id` (B0 when nothing promotes)
  - `bank`, `parameters` (exact axis values)
  - `parent_trial_ids`
  - `disposition`
  - `all_history_recommendation` as a separately labelled field, never copied backward into earlier folds

The run maps each selected rule onto native entries on test dates only, then calls `evaluate_entries` with those frozen fills. Occupancy flags stay separate from the unchanged-entry comparison.

## Runner registration

`runner._date_job` currently falls through to `replay_date` for unknown task ids. P15-19 needs an explicit branch. Do not apply this here.

Proposed addition in `implementation/src/trading_research/research/rule_discovery/runner.py` inside `_date_job`, after the P15-16 branch:

```python
    elif task_id == "P15-19":
        from trading_research.research.rule_discovery.exits import slice_p15_19
        result = slice_p15_19(payload["date"], payload)
```

`slice_p15_19` does not exist yet. The run should add it in `exits.py` once P15-18 artifacts and the frozen manifest are real. It should:

1. Read selected rules for the fold that owns `payload["date"]`.
2. Load `build_market_view(date, full_account_day=True)` under `install_write_guard()`.
3. Emit that date's rows of `FIXED_ENTRIES.json` and `EXIT_TRIALS.jsonl`.
4. Return job counts, unsupported counts, and wall/rss fields the slice summary already expects.

`tools/run_rule_discovery.py` already accepts `--task P15-19`. No CLI change is required if `_date_job` learns the id.

A coordinator-owned shared-schema change, if `TrialRecord` becomes a dataclass in `contracts/`, belongs in a later patch. Prep does not add it.

See `_prep/proposed_runner_p15_19.patch`.

## `TrialRecord` fields for exit trials

Exit trials are an additional decision family. They do not replace the entry candidate's primary exit during P15-17/P15-18.

Append-only JSONL rows in `EXIT_TRIALS.jsonl`, one row per (entry_id, policy_id):

- `trial_id`
- `parent_trial_ids` (the entry-selection trial and the frozen entry id)
- `family`, `branch`, `outer_fold`
- `stage`: `exit`
- `bank`: `E0` | `E1` | `E2` | `E3` | `E4`
- `parameters`: policy constants (expiry minutes, +1R, trail multiple)
- `code` / `data` / `plan` hashes
- `fit` / `tune` / `calibration` windows (empty for this comparison; selection stays in inner tuning only)
- `outcome_exposure_cutoff`
- `candidate_population_counts`
- `score` / `loss`: daily net points on the frozen entry set, not used to drop policies on the outer test
- `support`
- test metrics (reason counts, occupancy-flagged count, unsupported count, net points, net dollars)
- `reason`, `disposition`
- `runtime`, `artifacts`
- `failure_attribution` when a policy is not promoted
- `replaces_attempt_id` when retrying

Final test comparisons retain every policy (SEARCH_CONTRACT). Inner tuning may choose an exit; the outer report still prints E0-E4 side by side.

## Artifacts the run must still write

- `FIXED_ENTRIES.json` from P15-18 selected entries, not from the B0.2 prep slice
- `EXIT_TRIALS.jsonl`
- `EXIT_COMPARISON.json` (paired unchanged-entry table plus occupancy-flagged population)
- `FAMILY_REPORTS/` with both PHASE and audit tables
- `TASK_RECEIPT.json`, `REPORT.md`, `EVIDENCE_MATRIX.json`

Prep outputs under `_prep/` are machinery proof. They are not those artifacts.

## Limitations the run inherits

- Native quotes today are BBO on trade prints. A full quote-tape loader is a shared-schema/native change, not done here.
- Crossed trade-time BBO rows must be skipped. `view.quotes()` raises on them.
- Green Bird MNQ quantity must not enter the one-mini benchmark.
- Geometry units still differ by family. The prep parser is operational.
