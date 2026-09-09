# Jumbo: eliminate repeated predictions before the approved full fit

Implement this bounded performance change in the isolated checkout, using Cursor Grok 4.6 Extra High Fast. Read the four relevant source/test files, make one coherent implementation and test pass, and stop for supervisor review. Do not run shell commands, imports, tests, data scans or fits. Do not change protocols, targets, priors, estimators, thread settings or budgets. The supervisor handles registered execution and hardware configuration separately.

Allowed files:
- `src/trading_research/research/jumbo_models.py`
- `src/trading_research/research/jumbo_fitting.py`
- `tests/test_jumbo_models.py`
- `tests/test_jumbo_fitting.py`

The user approved the prepared 24-attempt / 20,000-total-CPU-second continuation and explicitly requested faster vectorized/compiled work and better hardware use. All prior consumption remains charged, all 116 targets and 1,000 bootstrap replicates remain required, and the memory ceiling is 4 GiB. Existing evaluation already batches date-bootstrap work into matrix products; do not reimplement that unchanged work.

## Concrete repeated work

`predict_model` returns the complete fused continuous-target tensor. `fit_domain` calls tuning, calibration, assessment and prediction publication separately for every target in the same fitted family. `evaluate_target` also repeats the empirical and selected-model prediction calls, and `_emit_predictions` predicts them again. `confirm_domain` restores a family once but repeatedly recomputes its forecasts. The existing complete-workload report projects about 1,274 CPU seconds for development predictions and 1,084 for heldout predictions, before its uncertainty margin. Preserve the numerical kernels and reuse these identical results.

## Required implementation

Add an explicit **bounded, per-family prediction reuse context**, and thread it through `choose_tuning_model`, `calibration_for`, `evaluate_target` and `_emit_predictions` as needed. Existing callers without that context remain compatible. No module-global cache. The context must bind the exact matrix and fitted model identities and the exact requested row mask. Two targets may share a result only when those inputs actually match. Keep raw and final predictions distinct. Keep intended forecast rows separate from outcome-eligible scoring rows; an eligibility mask must never erase retained forecasts.

Bound retained arrays and masks to **128 MiB per family**, counting distinct backing buffers rather than assuming views are free. An oversized result must run correctly without caching. Evict or release obsolete results and clear the context when the family changes or the operation exits. Do not retain a whole-study collection of fitted families or predictions. Avoid returning writable aliases that let calibration or a caller corrupt a later cache hit. Preserve model-record validation and feature/mask checks on reused calls; do not trust a mutable model's ID alone. No numerical rounding, new tolerance, reduced population, changed calibration, new fit, reselection or altered fallback semantics is allowed.

Expose compact reuse diagnostics (hits, misses, retained bytes and peak retained bytes) separately from scientific/model identities, so the registered run can show whether production actually reused predictions. Do not invent a speedup claim.

## Acceptance

Add focused cached-versus-uncached comparisons on existing categorical, interval and fused continuous fixtures. Cover tuning, calibration, selected assessments, published forecast populations and confirmation. Verify unchanged labels, masks, calibrated outputs, raw crossing counts, winner choices, target applicability and explicit failed-model fallbacks. Exercise different masks, changed model records, a different matrix, caller mutation and the cache capacity/cleanup behavior. Include a counted predictor fixture demonstrating removal of repeated calls for identical inputs and preserving distinct calls for differing populations.

The supervisor will review the complete diff, consolidate any repairs, and run the registered combined check before the full fit. Return a concise patch summary and remaining limitations. Do not claim runtime or performance verification.
