# P15-18 engineering-prep design

Reference for `refinement.py`. This is not a research result. P15-17 has not run.

## Organizing structure

A **neighborhood registry** keyed by `recipe_id`. Each row is an ordered list of one-axis sweeps. Two-stage rows (F3, P) run the first-stage axis with the other parameter frozen, then the second-stage axis at the chosen first-stage value. Sequence deadline and reclaim are two independent one-axis sweeps, never a cartesian product.

A **TrialRecord** is a plain dict with a frozen field list. The ledger is an append-only JSONL file: inserting a duplicate `trial_id` raises; a retry writes a new id and `replaces_attempt_id`.

Selection, gates, attribution and the ledger all consume the same dicts. No dataclasses are required at the public boundary.

## Do not

- Reimplement `holm`, `moving_block_bootstrap`, `build_evaluation_splits`, `purge_future_labels`.
- Import or read market data.
- Edit `contracts/*.py`, `method_pack`, `baseline_repairs.py`, `search.py`, `runner.py`, or any other task's files.
- Claim a native run, receipt, or research winner.

Import evaluation symbols from `trading_research.research.contracts.evaluation`.

## Candidate record (P15-08)

Required keys: `candidate_id`, `family`, `branch`, `bank`, `recipe_id`, `parameters`, `changed_axis`, `required_stages`.

Neighbors copy the parent and change exactly one axis unless the record is the explicit combination.

## Neighborhood table (SEARCH_CONTRACT.md)

Parameter names stay aligned with P15-08 `RECIPES` where they already exist. New axes use the contract names below.

| recipe_id | axis key | values | notes |
| --- | --- | --- | --- |
| F1 | `minutes` | 30, 60, 90 | parent default 60 |
| F2 | `volume_threshold_multiplier` | 0.75, 1.0, 1.25 | times the prior 20-session median; keep `median_sessions` |
| F3 | `width_S` then `efficiency` | width 0.5, 0.75, 1.0 at efficiency 0.35; then efficiency 0.2, 0.35, 0.5 at the parent's chosen width | parent `width_mult` 0.75 maps to `width_S` |
| P1/P2 | `bandwidth` then `prominence` | b 0, 2, 4 at prominence 0.20; then prominence 0.10, 0.20, 0.30 at the parent's chosen b | `bandwidth` is b |
| R1 | `dispersion` | 0.5, 1.0, 1.5 | |
| R2 | none | empty | status `not_applicable`, reason `no_numeric_refinement` |
| C1 | `window_minutes` | 2, 5, 10 | |
| C2 | `half_life_s` | 120, 300, 600 | |
| C3 | `history_sessions` | 10, 20, 40 | |
| S1 | `deadline_minutes` | 5, 10, 15 | also set `deadline_s` = minutes * 60 |
| S2 | `favorable_ticks` | 1, 2, 4 | |
| S3/S4 | both S axes, one at a time | deadline then ticks, no product | |
| M1 | `max_prior_contacts` | 0, 1, 2 | |
| M2 | `prior_reaction_S` | 0.1, 0.25, 0.5 | |
| T1/T2/T3/T4 | `shift_minutes` | -30, -15, 0, 15, 30 | availability still required; T2 with incomplete formation is `not_applicable` |

Caps: 12 new neighbors per selected bank, 24 per family, 25 including the one combination. New means status `attempted`. Duplicate, not-applicable, unsupported, timed-out and rejected rows are still written and do not expand the attempted set past the cap. Overflow rows get reason `cap_per_bank` or `cap_per_family`.

Past-only: a neighbor with `required_available_at_ns` greater than the fold `fit_cutoff_ns` is `not_applicable` with reason `past_only_allowlist`. Default `enforce_past_only=True`. T issue offsets still require formation availability at the shifted issue.

Duplicate: same `(family, branch, recipe_id, parameters)` as an already-attempted candidate, including the parent. Reason `duplicate`.

## Combination

Exactly one combined candidate per family per fold.

Create it only when:

1. both refined ingredients have `beats_b02` true on inner tuning
2. `source_dependencies_causal` is true
3. refined-plus-combined count stays <= 25

Otherwise return `None` and, if attempted then rejected, keep a ledger row with reason `combination_ingredients_failed` or `combination_not_causal`.

The record stores `vs_ingredient_a`, `vs_ingredient_b`, `vs_b02` (score deltas) and `interaction`:

- `synergistic` if combo score > both ingredients
- `antagonistic` if combo score < both ingredients
- `additive` otherwise

`changed_axis` is `combination`. `changed_axes` is 2. Parameters are the union of both one-axis changes.

## Selection

Rank on inner `mean_daily_net_points` (primary daily net-point improvement vs B0.2 lives in `improvement_vs_b02`).

1% simplicity: the simpler candidate wins unless the more complex one improves by **more than** 1% relative to the simpler score. Exactly 1% keeps the simpler one. Complexity is `changed_axes` (baseline 0, one-axis 1, combination 2), then fewer differing parameter keys, then lower `candidate_id` lexically. Relative delta uses `max(abs(simple_score), 1e-12)` as the denominator.

Pick at most two mechanism banks per family with `improvement_vs_b02 >= 0` and inner support (`inner_support_ok` true, or opportunities > 0 and days > 0). If none qualify, selected banks are empty and the family retains B0 / B0.2.

`select_banks` and `rank_inner` must not read keys `outer`, `outer_score`, `test_metrics` that belong to the outer fold. Copy only inner fields before ranking.

## Promotion gates

Reuse `holm` and `moving_block_bootstrap`. Pass seed, draws and block explicitly:

- seed `BOOTSTRAP_SEED` (15022026)
- draws `BOOTSTRAP_DRAWS` (2000)
- block `BLOCK_LENGTH` (5)

Centered bootstrap p-value on paired daily differences `diff`:

`d = mean(diff)`
`draws = moving_block_bootstrap(diff, block=5, draws=2000, seed=15022026)`
`p = (1 + count(draw - d >= d)) / (B + 1)`

95% lower bound is the 2.5th percentile of `draws`. Promotion needs mean(diff) > 0 and that lower bound > 0.

Holm runs across **every candidate at the decision stage**, including unsuccessful, duplicate, not-applicable, unsupported, timed-out and rejected trials (A04). Supply one p-value per trial; missing p for a failed trial is 1.0.

Support gate (Phase 1.5 upgrade): >= 100 resolved opportunities, >= 30 eligible test days, >= 3 supported outer blocks. A six-example perfect result is `inconclusive_support`.

Support sensitivity (reported, not used to manufacture a pass):

- half: 50 opportunities, 15 days
- twice: 200 opportunities, 60 days
- outer-block count stays 3

Also required: software/causality pass; Holm-adjusted p <= 0.05; positive difference in >= 60% of supported blocks; no cost-stress sign reversal; no unexplained coverage loss.

Frequency floor: `candidate_entries < 0.5 * baseline_entries` cannot replace the baseline. It may be labelled `high_selectivity` if every other check passes. Keep the baseline when nothing clears.

Density-matched control offsets stay `(-2, -1, 1, 2)` for `{-2S,-S,+S,+2S}`. Re-export them. Do not reimplement SHA256 cycling; P15-08 already owns `control_offset`.

## Failure attribution

Ordered vocabulary (fixed):

1. `frequency`
2. `location_miss`
3. `confirmation_delay`
4. `adverse_before_target`
5. `cost_sensitivity`
6. `support`
7. `coverage`

Thresholds are module constants, never read from a candidate result:

- frequency: entries < 50% of baseline entries
- location_miss: objective not reached AND (nearest approach <= 0.25 S OR adverse excursion >= 0.5 S before any favorable 0.5 S)
- confirmation_delay: missed-move share > family median
- adverse_before_target: stop-first share > family baseline
- cost_sensitivity: cost-stress sign reversal
- support: below the support gate
- coverage: unexplained input coverage loss

Runtime failure or timeout returns `[]` and never a data-rejection reason. `reason` stays `runtime` / `timed_out`.

Required for every deselected, inconclusive, or not-promoted candidate.

## TrialRecord fields

Every row includes:

`trial_id`, `parent_trial_ids`, `family`, `branch`, `outer_fold`, `stage`, `bank`, `parameters`, `code_hash`, `data_hash`, `plan_hash`, `fit_window`, `tune_window`, `calibration_window`, `outcome_exposure_cutoff`, `candidate_population_counts`, `score`, `loss`, `support`, `test_metrics`, `reason`, `disposition`, `runtime`, `artifacts`, `failure_attribution`

Also store `candidate_id`, `recipe_id`, `status`, `replaces_attempt_id` (null unless a retry).

`status` in `attempted`, `duplicate`, `not_applicable`, `unsupported`, `timed_out`, `rejected`.

`stage` is `refinement` (or `combination` for the combo). Breadth rows are out of scope here.

Windows are `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`.

## Public API

```
NEIGHBORHOODS
MAX_NEIGHBORS_PER_BANK = 12
MAX_NEIGHBORS_PER_FAMILY = 24
MAX_REFINED_PLUS_COMBINED = 25
SIMPLICITY_THRESHOLD = 0.01
FREQUENCY_FLOOR_FRACTION = 0.5
SUPPORT_GATE_OPPORTUNITIES = 100
SUPPORT_GATE_DAYS = 30
SUPPORT_GATE_OUTER_BLOCKS = 3
BLOCK_POSITIVE_FRACTION = 0.6
ATTRIBUTION_ORDER
RETENTION_STATUSES = ("active_selected", "active_baseline", "inactive_retained")
TRIAL_RECORD_FIELDS
CONTROL_OFFSETS = (-2, -1, 1, 2)
HOLM_ALPHA = 0.05

neighborhood_values(recipe_id, parameters) -> list[dict]
generate_neighbors(family, fold, selected_banks, *, attempted=(), enforce_past_only=True) -> list[dict]
combine_candidates(...) -> dict | None
changed_axes(candidate) -> int
simpler_wins(simple, complex, *, enforce_simplicity=True) -> dict
rank_inner(candidates, *, enforce_simplicity=True) -> list[dict]
select_banks(family, candidates, *, max_banks=2, enforce_simplicity=True) -> list[dict]
centered_bootstrap_pvalue(daily_diff, *, bootstrap_fn=moving_block_bootstrap) -> dict
evaluate_promotion(candidate, stage_trials, *, holm_fn=holm, bootstrap_fn=moving_block_bootstrap, apply_holm=True, apply_frequency_floor=True) -> dict
support_sensitivity(opportunities, days, blocks) -> dict
attribute_failure(diagnostics) -> list[str]
make_trial_record(...) -> dict
class TrialLedger  # append, replace_attempt, read
selected_rules_by_fold(fold_roles, descriptive_recommendation) -> dict
family_dispositions(rows) -> dict  # ContractError unless status in RETENTION_STATUSES
```

Guard flags default on. Tests turn them off for negative controls. Changing a default to off must fail the corresponding default-path test.

## Assumed P15-17 shapes (not consumed from disk)

`BREADTH_RESULTS.json`: per fold per family a list of candidate dicts with `inner_tuning` (`mean_daily_net_points`, `improvement_vs_b02`, `support_opportunities`, `support_days`, `inner_support_ok`) and optional `outer` that selection must ignore.

`REFINEMENT_ALLOWLIST.json`: per fold per family at most two `selected_banks` with parent candidate_id, recipe_id, parameters, branch, `beats_b02`.

Document these in `PROPOSED_INTEGRATION.md`. Do not invent a P15-17 receipt.

## Tests (`test_p15_18.py`)

All fixtures labelled `synthetic: True`. No market files.

Required behaviors, each with a literal expected value:

1. Literal neighborhood values for every table row (F1 through T).
2. Caps 12 / 24 / 25.
3. Duplicate and inapplicable marking, including R2.
4. Past-only reject when `required_available_at_ns` > `fit_cutoff_ns`.
5. Simplicity at exactly 1% (simple wins) and just above (complex wins).
6. Outer-outcome independence: mutating `outer` cannot change `select_banks`.
7. Holm and bootstrap called with seed 15022026 and draws 2000 (spy on the injected fn).
8. Frequency floor blocks replacement below 50% of baseline entries.
9. Support sensitivity at half and twice; six-example perfect stays `inconclusive_support`.
10. Every attribution reason on a synthetic diagnostics fixture, in vocabulary order.
11. Runtime failure yields empty attribution.
12. Ledger append-only: rewrite of the same `trial_id` raises; `replace_attempt` adds a row and keeps the old one.
13. Negative controls: `enforce_past_only=False`, `enforce_simplicity=False`, `apply_holm=False`, `apply_frequency_floor=False` each admit a case the default path rejects.
14. Combination only when both beat B0.2; interaction labels; combined count <= 25.
15. Unsuccessful trials inflate Holm m (A04).
16. Missing daily values stay unknown, not zero (S11). Complete zero-opportunity days stay 0.
17. Shuffling input candidate order does not change selected bank ids after sorting (S15/S24).
18. New neighbors are new parameter tuples, not a filter of parent ids (S22).
19. `SELECTED_RULES_BY_FOLD` is fold-scoped; the all-history recommendation is a separate labelled object (A05).
20. Retention statuses `active_selected`, `active_baseline`, `inactive_retained` with first attributions.

Do not import production functions and assert they equal themselves. Call the public API with a concrete fixture and assert literals.

## Files

Allowed writes:

- `implementation/src/trading_research/research/rule_discovery/refinement.py`
- `implementation/tests/rule_discovery/test_p15_18.py`
- `implementation/reports/research-work/P15-18/_prep/` (`WORK_LOG.md`, `FIXTURES.md`, `PROPOSED_INTEGRATION.md`, this file)

A needed shared-schema change is a proposed patch under `_prep/`, not applied.
