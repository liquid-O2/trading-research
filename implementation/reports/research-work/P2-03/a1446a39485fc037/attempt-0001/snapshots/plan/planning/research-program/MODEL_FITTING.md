# Exact first-release model recipes

Owner `P2-02`; Phase 1.5 may reuse quantiles/ridge only where its registered candidate requires them. Proposed module `research/experts/fitting.py`. The first release uses the existing pinned NumPy float64 stack, with no network model service. Different experts have different fitted artifacts. The joint volatility expert has one fit interface and one multihead artifact containing all historical and IV features.

## Preprocessing

Fit every transformation on the current fit partition only. For each feature: convert nonfinite values to missing with a reason, append a binary missing mask, impute the training median, and standardize by training mean and population standard deviation. If a column has no observed training values, impute 0, leave scale 1 and flag unsupported; do not claim it contributed. A constant column uses scale1. Clip standardized values to [-10,10], preserving a clipped flag for diagnostics. Categorical values use a frozen domain vocabulary plus `unknown`; no full-dataset category fitting. Do not impute targets.

Quantile implementation is linear interpolation: sorted `x`, `a=(n-1)p`, `i=floor(a)`, `Q=x[i]+(a-i)*(x[min(i+1,n-1)]-x[i])`. Empty returns unavailable; n=1 returns the only value. Fixture `[0,10,20,30]`, p=.25 gives7.5. Fitted transformations persist ordered columns, medians, means, scales, vocabulary, knots, training IDs and hashes.

## Ridge and nonlinear challenger

`fit_ridge(X, Y, target_mask, row_weight, alpha, transform) -> ModelArtifact`; `predict(artifact, X) -> float64[n,h]`. Add intercept column1. For each output h within the same artifact solve `(X_h.T W_h X_h + alpha D) b_h = X_h.T W_h y_h`, where `D=diag(0,1,...,1)`, available-target rows only, and weights sum to1 per head. Use `numpy.linalg.solve`, falling back to `lstsq` only on a recorded singularity. One shared preprocessing/feature matrix, one alpha chosen across supported heads, and one serialized coefficient matrix constitute the joint fit. Separate GK/YZ/HAR models are ablations, not the production architecture.

Alpha grid `{.001,.01,.1,1,10}`; default `.1` if tuning is unsupported. Equalize account-day weight: each row gets `1/n_rows_on_its_day`, then normalize within available targets. Multiple heads get equal tuning weight after the shared evaluation normalization. Prediction fixture: X=[0,1,2], y=[1,3,5], alpha0 must produce intercept1,slope2 within 1e-10.

Nonlinear challenger `hinge_ridge`: take standardized continuous features, append `max(0,x-k)` at each training .25/.5/.75 quantile knot, removing duplicate knots. Retain the original linear and missing-mask columns; do not hinge masks or categorical one-hot columns. Append pairwise products only for the explicit feature-pair list in each expert contract, at most 12 pairs. Same ridge solver and alpha grid. This is a specified nonlinear function basis, not an invitation to an unbounded model zoo. Tune linear versus hinge once per expert/outer origin. If tied within 1%, choose linear.

## Probabilities

`fit_softmax(X, y, class_names, row_weight, l2) -> ModelArtifact`. Stable logits `z=X B`, `p_k=exp(z_k-max z)/sum exp(z-max z)`. Minimize weighted mean negative log likelihood plus `(l2/2)*sum(nonintercept B**2)`. Gradient `X.T@(w[:,None]*(p-onehot)) + l2*D@B`. Initialize B=0; use full-batch gradient descent, learning rate `1/(.5*||sqrt(W)X||_2**2+l2+1e-12)`, maximum 5,000 iterations, stop when relative objective change <=1e-9 for 10 consecutive iterations. Log objective trace; nonfinite or increasing loss beyond1e-10 is a solver failure. L2 grid `{.001,.01,.1,1}`, default.1. Use the same linear/hinge basis choice as the declared expert candidate.

Calibrate probabilities with one temperature T in `{.5,.75,1,1.5,2,3}` minimizing calibration log loss; ties choose T closest to1, then lower. Apply softmax(z/T). Calibration does not change feature coefficients. For unsupported fits, output Laplace-smoothed historical class probabilities `(n_k+1)/(n+K)`, support=`low_support`, fit cutoff and counts. For an absent required class this is a fallback, not a successfully learned classifier.

Binary Brier=`mean((p-y)**2)`; multiclass Brier=`mean(sum_k(p_k-onehot_k)**2)`; log loss clips p to[1e-12,1-1e-12] only for evaluation. Reliability bins use fixed probability edges0,.1,...,1 and report bin counts; do not average empty bins as zero error. Constant-probability and session-frequency baselines use training labels only.

## Quantiles, positive means and intervals

For nonnegative variance targets fit `z=log(y+1e-12)`. A mean variance forecast is `max(1e-12, exp(pred_z)*mean_train(exp(residual))-1e-12)`, where residuals are chronological training predictions, never in-sample residuals or test residuals. If fewer than 100 causal residuals on30 days, smearing=1 and mark calibration low-support. QLIKE=`y/v+log(v)` for v>0 including y=0; compare differences to avoid irrelevant additive constants. Fixture y=4: v4 gives1+ln4; v2 gives2+ln2, which is worse.

For excursion/time quantiles use linear/hinge quantile regression, minimizing weighted pinball `rho_tau(u)=u*(tau-1[u<0])` plus `(l2/2)||b_nonintercept||²`. Implement deterministic Adam with initial b=0, lr.01, betas(.9,.999), epsilon1e-8, 5,000 steps, full-batch gradient `-X.T@(w*(tau-(y<Xb)))+l2*D b`; at exact equality set that row's residual subgradient to0 before multiplying by X. Adam bias correction uses the one-based step. Keep the best objective iterate, require relative improvement<1e-7 across last 200 steps or flag convergence failure. L2 `{.001,.01,.1}`, default.01; taus .1,.5,.9. Sort predicted quantiles per row to remove crossing and report the raw crossing rate. Nonnegative targets clip quantiles at 0; do not alter signed-return targets.

For calibrated 80% intervals around a point forecast, use absolute residuals on the disjoint calibration block. `k=min(n,ceil((n+1)*.8))`; radius is kth smallest absolute residual (one-based). Bounds=`pred±radius`, lower floored0 only for nonnegative targets. For log-variance intervals calibrate absolute log residuals then exponentiate; distinguish mean estimate from median/log-center. Minimum 100 residuals on30 days. Report empirical coverage, width and coverage by session/horizon; no exchangeability or guaranteed coverage claim under market drift.

## Adaptation and artifact checks

Every estimator implements `fit(dataset, split, config)`, `predict(snapshot_batch, artifact)`, `serialize`, `load` and `explain_inputs`. Loading validates schema, hashes, feature order, target units and training/availability cutoffs. Round-trip predictions must agree at absolute/relative1e-10; parallelism may not change candidate selection. Do not pickle untrusted arbitrary code; use JSON metadata plus NumPy arrays with `allow_pickle=False`.

Required discriminating checks: reverse labels and observe changed predictions; remove an actually used input and observe the declared ablation matrix change; append future rows and prove all earlier transforms/predictions unchanged; permute input columns with correct names and recover identical predictions; rename/miss a required column and fail; insert a never-observed IV group and obtain a mask/fallback rather than a fabricated contribution. Positive-control synthetic data has a known signal only in an IV feature and must favor the joint model over the historical-only ablation on held-out synthetic rows.
