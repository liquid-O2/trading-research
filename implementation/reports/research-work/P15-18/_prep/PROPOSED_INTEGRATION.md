# P15-18 proposed integration

Engineering-prep only. P15-17 has not run. No predecessor receipt hashes exist. Do not treat this note as a native result.

`refinement.py` is a pure library. `search.py` (P15-17) does not exist yet. Runner registration is coordinator-owned and is not applied here.

## Assumed `BREADTH_RESULTS.json`

P15-17 writes one object per outer fold per family. Selection reads `inner_tuning` only.

```json
{
  "schema_version": "research-breadth-results-v1",
  "folds": [
    {
      "outer_fold": 2022,
      "family": "JJ-TBR",
      "fit_window": {"start": "2020-01-01", "end": "2021-06-30"},
      "tune_window": {"start": "2021-07-01", "end": "2021-09-30"},
      "calibration_window": {"start": "2021-10-01", "end": "2021-12-31"},
      "fit_cutoff_ns": 0,
      "outcome_exposure_cutoff": "2021-12-31",
      "candidates": [
        {
          "candidate_id": "JJ-TBR:judas_reversal:F1:minutes=60",
          "family": "JJ-TBR",
          "branch": "judas_reversal",
          "bank": "Formation",
          "recipe_id": "F1",
          "parameters": {"minutes": 60},
          "changed_axis": "minutes",
          "changed_axes": 1,
          "required_stages": ["formation"],
          "beats_b02": true,
          "inner_tuning": {
            "mean_daily_net_points": 0.0,
            "improvement_vs_b02": 0.0,
            "support_opportunities": 0,
            "support_days": 0,
            "inner_support_ok": false
          },
          "outer": {
            "mean_daily_net_points": 0.0,
            "improvement_vs_b02": 0.0
          }
        }
      ]
    }
  ]
}
```

`select_banks` and `rank_inner` copy `inner_tuning` and drop `outer`, `outer_score`, `test`, and `test_metrics`.

## Assumed `REFINEMENT_ALLOWLIST.json`

At most two selected banks per family per fold. Those parents are the `selected_banks` argument to `generate_neighbors`.

```json
{
  "schema_version": "research-refinement-allowlist-v1",
  "folds": [
    {
      "outer_fold": 2022,
      "family": "JJ-TBR",
      "selected_banks": [
        {
          "candidate_id": "JJ-TBR:judas_reversal:F1:minutes=60",
          "family": "JJ-TBR",
          "branch": "judas_reversal",
          "bank": "Formation",
          "recipe_id": "F1",
          "parameters": {"minutes": 60},
          "changed_axis": "minutes",
          "required_stages": ["formation"],
          "beats_b02": true,
          "trial_id": "breadth-f1"
        }
      ]
    }
  ]
}
```

Past-only is enforced inside `generate_neighbors` (`required_available_at_ns > fit_cutoff_ns`). The allowlist is already fold-scoped. Neighbors still carry the check.

## `search.py` call points

P15-17 owns `search.py`. When that module exists, P15-18 should be called as follows.

1. After the allowlist is written, for each fold/family call `generate_neighbors(family, fold, selected_banks, attempted=ledger_rows, enforce_past_only=True)`.
2. Score those neighbors on inner fit/tune only. Keep unsuccessful, duplicate, not-applicable, unsupported, timed-out, and rejected rows in the ledger.
3. Pick two refined ingredients with nonnegative inner improvement. Call `combine_candidates(..., source_dependencies_causal=True, refined_count=len(attempted_refined))`. A `None` return is a ledger row with `combination_ingredients_failed` or `combination_not_causal`, not a silent skip.
4. Call `select_banks` on inner fields only if a later inner re-rank is needed. Outer blocks stay unused for membership.
5. At the decision stage call `evaluate_promotion(candidate, stage_trials, apply_holm=True, apply_frequency_floor=True)` with every trial in `stage_trials`, including unsuccessful ones. Missing `p_raw` is 1.0.
6. Persist with `TrialLedger(path).append(make_trial_record(...))`. Retries use `replace_attempt`.
7. Write `SELECTED_RULES_BY_FOLD.json` from `selected_rules_by_fold(fold_roles, descriptive_recommendation)`. Do not copy the all-history winner into a fold role.
8. Write `FAMILY_DISPOSITIONS.json` from `family_dispositions(rows)` with statuses `active_selected`, `active_baseline`, or `inactive_retained`.

Expected P15-18 artifacts after a real run (not produced here):

- `REFINEMENT_BANK.json`
- `TRIALS.jsonl`
- `SELECTED_RULES_BY_FOLD.json`
- `FAMILY_DISPOSITIONS.json`
- `TASK_RECEIPT.json` and `REPORT.md`

## Runner registration (coordinator-owned)

Do not apply this patch in the P15-18 worktree. `search.py` must exist first and must expose `slice_p15_18`.

See `_prep/proposed-runner.patch`. The intended `_date_job` branch is:

```
elif task_id == "P15-18":
    from trading_research.research.rule_discovery.search import slice_p15_18
    result = slice_p15_18(payload["date"])
```

Place it next to the P15-08 branch in `implementation/src/trading_research/research/rule_discovery/runner.py`. The CLI in `tools/run_rule_discovery.py` already forwards `--task`.

No shared-schema patch is proposed. Trial records, selected-rule documents, and family dispositions use schema versions emitted by this module. If DATA_CONTRACTS later lists those versions, that is a coordinator edit.

## Remaining work (not this prep)

- Native engineering slice via `run_rule_discovery.py slice --task P15-18` after P15-17 receipts exist.
- `TASK_RECEIPT.json` with actual predecessor hashes.
- P15-17 `BREADTH_RESULTS.json` and `REFINEMENT_ALLOWLIST.json` hashes.
- Full-run `run` / `resume` / `summarize` on the frozen manifest.
- Evidence matrix and GATE_REVIEW, which require the native slice.
