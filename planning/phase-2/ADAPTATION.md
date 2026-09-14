# Refit, intraday adaptation and replay release

Owners `P2-23` adaptation and `P2-24` final chronological release. Use the four schedules in the [evaluation contract](/workspace/planning/research-program/EVALUATION.md), on identical snapshots, features, target definitions and costs. Model complexity and upstream selection stay frozen for the outer year. Each expert has its own artifact/cadence and evidence; a faster cadence is not automatically better.

## Exact intraday update

Only the monthly-plus-intraday arm changes parameters during a session. Base feature transformations and slopes remain fixed until monthly refit. At each quarter-hour, collect labels that became available since the last update, deduplicate target row IDs, and update intercept residual bias only. For a continuous/log target with raw prediction z, update `b <- .98*b + .02*(y-z)` once per newly matured account-day-normalized batch: first average residuals within each `(label_day, head, update_clock)` so dense overlapping signals do not create hundreds of updates. Apply `prediction=z+b` on the next issue, never earlier.

For probabilities update a class-logit offset vector `a <- .98*a + .02*(onehot(y)-p)` on the same grouped schedule, then center a to mean0 and add it to base logits before frozen temperature calibration. Include only supported observed labels; no imputed outcomes, unfinished horizons, unpublished OI or future day types. Default b/a=0 at the start of the outer evaluation, carry across account days, reset to0 at each monthly refit because the base fit incorporates prior data. This is a bounded online residual correction, not unrestricted intraday retraining.

Store update ID, previous/new artifact offsets, consumed label IDs and availability, actual compute finish time and first affected snapshot. A matured label arriving exactly at an issue time becomes usable only after update computation completes; the issue may use the prior artifact. Simulated runtime uses measured engineering median plus p95 sensitivity, not zero-cost hindsight fitting.

## Drift and retirement

At each monthly boundary report population stability on continuous standardized features using fixed training decile bins: `PSI=sum((p_new-p_train)*ln(p_new/p_train))`, with each count smoothed by.5 then renormalized. Report missingness change and recent42-day loss relative to its causal baseline. PSI>.2 or loss worsening>20% on at least 30 supported days creates a diagnostic flag, not an automatic unexplained veto.

Retire a fitted head to its declared baseline for the next month only if recent loss is worse than baseline in two consecutive monthly reports and its paired day-block95% improvement interval is entirely below0, or a schema/causality defect invalidates it immediately. Keep the artifact and failure receipt. Re-entry requires a newly versioned verified fit using only then-available evidence. Do not choose a retirement date backward from a test equity curve.

## Release checks

Replay every declared test-year snapshot and opportunity with dependency order: raw/as-of data -> shared primitives -> upstream forecasts -> method forecasts -> conditional plans -> comparison-only selector -> unchanged execution benchmark. The code path must reject a forecast trained/selected after issue time. Use causal stacking for training rows too, including the intraday OI artifact and Phase 1.5 selected rules.

Required release artifacts: feature/target dictionaries and matrices; availability by root/year/session; split/exposure manifests; all attempted models and ablations; calibrated forecasts and support; plan/revision/death records; baseline/selector daily replays; errors/censoring/zero days; runtime/cache receipts; task/subphase receipts; deterministic charts; a full dependency graph; and `PHASE2_RELEASE.json` with downstream allowlist and prohibited interpretations.

Compare annual/monthly/weekly/monthly-plus-intraday on paired days and loss/utility, using the shared multiple-trial accounting. Choose cadence using only the inner tuning available at each outer origin; outer results assess that policy. A final all-history cadence recommendation is descriptive and cannot replace the causal outer record.

The Phase 3 handoff lists each expert output, units, horizon, availability, confidence/support, fallback, model identity, measured incremental contribution and input limitations. It explicitly reserves native actionable location extraction/arrival-reaction evaluation for Phase 3, final response/entry integration for Phase 4, and later learned management for a separately planned milestone. Missing native NDX/SPX inputs yield `closed_with_limits` and exact restricted downstream scope, never a false complete-native release.
