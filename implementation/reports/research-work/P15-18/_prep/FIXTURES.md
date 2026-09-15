# P15-18 synthetic fixtures

Every fixture is labelled `synthetic: True`. No native market row was read. No parquet, quote, or `/workspace/data` path was opened.

Helpers in `tests/rule_discovery/test_p15_18.py` always set that flag. `_fold`, `_candidate`, `_diag`, `_inner_candidate`, and `_promo_candidate` overwrite `synthetic` to `True` after kwargs merge.

## Fold windows

`_fold()` is a 2022 outer fold with inner windows from EVALUATION.md.

- `fit_window`: 2020-01-01 to 2021-06-30
- `tune_window`: 2021-07-01 to 2021-09-30
- `calibration_window`: 2021-10-01 to 2021-12-31
- `fit_cutoff_ns` and `issue_at_ns`: `100 * MINUTE_NS`
- `outcome_exposure_cutoff`: 2021-12-31

Timing tests reuse those clocks. A T2 formation fixture sets `formation_available_at_ns` to `90 * MINUTE_NS` so shifts of -15 and -30 minutes issue before the formation exists.

## Neighborhood parents

Each parent is a P15-08-shaped dict plus `parameters` and `synthetic: True`.

- F1 parent minutes 60. Neighbors 30 and 90 are new. 60 is `duplicate`.
- F2 parent keeps `median_sessions` 20 while sweeping the volume multiplier.
- F3 parent `width_mult` 0.75 and `efficiency` 0.35. Width sweep freezes efficiency 0.35. Efficiency sweep uses width 0.75.
- P1 bandwidth 0, P2 bandwidth 2. Prominence sweep uses the parent bandwidth.
- R2 parent has no numeric axis. The only row is `not_applicable` / `no_numeric_refinement`.
- S3/S4 parents expand deadline then ticks. Six rows, not a 3-by-3 product.
- Overflow parent uses unregistered recipe_id `OVERFLOW` with `refinement_axis=cap_value` and 15 `refinement_values`. That path overflows the 12/24 attempted caps without a key in `NEIGHBORHOODS`.
- Unregistered fallback parent carries `refinement_axis` and `refinement_values`.

Attempted-set fixtures reuse an F1 parent plus an already-attempted 30-minute tuple so 30 and 60 are `duplicate` and 90 is `attempted`.

## Inner scores for bank selection

`_inner_candidate` stores scores only under `inner_tuning`.

- Formation `cA` mean 5.0, improvement 1.0
- Profile `cB` mean 4.0, improvement 1.0
- Delta `cC` mean 3.0 or 3.5, improvement 1.0, with a large `outer` payload that selection must ignore
- Memory `cD` mean -1.0, improvement -1.0 (does not qualify)
- Formation `cA` with `inner_support_ok=False` and positive opportunity counts (must not be selected)

Simplicity fixtures use scores 100 vs 101 (exactly 1 percent, simple wins) and 100 vs 101.1 (complex wins).

## Promotion and bootstrap

`_promo_candidate` is 30 paired daily differences of 1.0, 100 resolved opportunities, 30 eligible days, 3 outer blocks, block improvements `[1.0, 1.0, 1.0]`, 80 candidate entries vs 100 baseline entries, and software/causality passing.

Stage-trial overlays used with it:

- Holm success. One trial `t-main` with `p_raw` 0.001.
- A04 / Holm negative control. `t-main` `p_raw` 0.04 plus two unsuccessful trials at 1.0.
- Frequency floor. `candidate_entries` 40, `baseline_entries` 100.
- Six-example inconclusive. `resolved_opportunities` 6, six positive daily diffs, 6 days, 1 block.
- Missing day. `[2.0, None, 2.0]`. Mean stays 2.0.
- Zero-opportunity day. `[2.0, 0.0]` plus 28 ones. The 0.0 stays in the mean.

Bootstrap spies record `seed=15022026`, `draws=2000`, `block=5`.

## Failure diagnostics

`_diag()` defaults to passing support and frequency, objective reached, and no cost or coverage failure.

The all-reasons fixture fires every `ATTRIBUTION_ORDER` entry. Single-reason fixtures flip one field. Runtime and timeout copies of the all-reasons fixture must return `[]`.

## Ledger rows

`make_trial_record` fills every `TRIAL_RECORD_FIELDS` key. The first row is `trial_id=t1`, stage `refinement`, F1 minutes 30. The retry is `t1-retry` with `replaces_attempt_id=t1`. Both rows stay on disk.

## Selected rules and dispositions

Fold role 2022 uses `candidate_id=fold-2022-rule` and cutoff 2021-06-30. The all-history descriptive object is `all-history-winner` and is stored under a separate key.

Retention rows are `active_selected` (empty attribution), `active_baseline` (`support`), and `inactive_retained` (`location_miss` then `coverage`).
