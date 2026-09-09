# Context: independently scored specialists

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
Every card incorporates [COMMON_CONTRACTS](COMMON_CONTRACTS.md). Context is a set of observable states and conditional forecasts, not an irreversible daily 'bull/bear' vote. Asset/session/horizon variants remain separately scored. C-series outputs condition Location formation and selection and may originate opportunities without Response confirmation.

## C01 — Source-faithful range and session geometry

1. **Purpose/provenance.** Preserve Jumbo and Pine distinctions before improving them; JTR-02/03/21/22, JSS, JXA/JFN and PIN001–083.
2. **Inputs.** F09 eligible trade bars/tape, F03 named windows and previous-RTH state. NQ/ES first, all supported assets as separate cohorts. Publish provisional builds, freeze final range only after build end/watermark.
3. **Definition.** `O=first eligible trade,H=max p,L=min p,C=last,W=H−L`; internal `L+fW`, f=.25/.5/.75; upper/lower extensions `H+kW,L−kW`. Keep source label k versus normalized coordinate x=(p−L)/W distinct. Baseline 06–09 NY; previous RTH09:30–16; original 20–20:30,00–00:30,03–03:30,09:30–10,10–10:30,12–12:30,15–15:30; 5/15-minute OR and all additional Pine windows live in the source benchmark registry. London H4/02:00-end visual interpretation and 03:00 alternative remain distinct where start is unresolved. Binding local refinement: [SR-C01](../SYSTEM_REFINEMENT.md#sr-c01).
4. **Output.** Range object, width in ticks/price%/prior-vol units, open location, geometry and complete/coverage flags. No eventual day type or win rate embedded.
5. **Dependencies/use.** F03/09/10, M04 prior-RTH value; C02/C03 and L01–03. Zero-width/incomplete ranges abstain from divisions/projections.
6. **Comparisons.** Exact disclosed source geometry; corrected causal implementation versus source repaint/proxy benchmark; learned/adaptive windows belong to C05 and conditional bounds C06. Binding further upgrade and child comparisons: [UP-C01](../UPGRADE_PATHS.md#up-c01).
7. **Rules.** Preserve each source's wick range, session O/C body, candle-body envelope, average range and SD population as different definitions. Undisclosed minimum-average/P-zone formulas are not invented.
8. **Tests.** W=100 gives EQ L+50 and upper1.33 H+133; first15m cannot freeze at session open; missing final bar, DST, body25 versus range25, London clock ambiguity and prior-RTH/6–9 anchor parity.
9. **Acceptance.** Exact hand geometry and prefix invariance; source table replication only with clearly defined denominators. No calibrated use of reported 86.46%.
10. **Ablation/fallback/resources.** Anchor, clock, width normalization and source variant comparisons; no usable range means no dependent projection. Class A, small state per registered window.

## C02 — Ordered break, sweep and reclaim state

1. **Purpose.** Preserve no/single/double breaks, order and original sequence exceptions; JTR-05–12, JXA-14/23, JFN-05, PIN sweep/stat findings.
2. **Inputs.** Frozen C01 objects, M08 known prior extrema, available trade path. Observe 09–12 and source-specific horizons separately; all sessions/asset variants.
3. **Algorithm.** Track first high breach, first low breach, breach depth, return inside, EQ/quarter crossings and sequence timestamps. Use source strict breach then a training-registered tick/vol tolerance challenger. State includes none/high-only/low-only/high-then-low/low-then-high plus ordered reclaim/retest flags. 'Sweep' means observable breach+return, not observed stop orders. A gap crossing is distinct from traded contact. Binding local refinement: [SR-C02](../SYSTEM_REFINEMENT.md#sr-c02).
4. **Output.** Causal prefix state and duration; final path class at horizon maturity only. High-only does not equal bullish trade; eventual double-break is never known in advance.
5. **Dependencies.** C01/F10/M08; C03 forecasts remaining transitions, L range roles and optional R sequences.
6. **Comparisons.** Exact rule state machine; empirical transition/competing-risk frequencies; multinomial/logistic survival, HSMM or temporal model for future transitions. Binding further upgrade and child comparisons: [UP-C02](../UPGRADE_PATHS.md#up-c02).
7. **Rules.** Count denominator only when observation horizon matures or censor explicitly. Same-bar unknown order is ambiguous; do not infer favorable ordering from candle color.
8. **Tests.** Both edges same coarse bar, extended high-only mean reversion, compressed lower break continuation, sweep before action window, reclaim then second break, no-break and horizon-end censor.
9. **Acceptance.** State transitions match ordered fixtures and source chart interpretations. Calibrated next-transition probabilities, including none, beat pooled frequency on held-out dates.
10. **Ablation/fallback/resources.** Unordered versus ordered, no reclaim/depth/duration, source-event delay. Missing path produces censored state, not no-break. Class A/B with bounded per-object history.

## C03 — Jumbo path and internal-versus-extension forecast experts

1. **Purpose.** Make Jumbo Context predictive without flattening its two single-break scenarios; JTR-04/06/07/08/12/14/23, DRF-U07/11.
2. **Inputs.** C01 width/open geometry, C02 prefix, prior-RTH value M04, prior sweeps/SMT M03, time/event state and C volatility forecasts available as of decision. Issue at build completion, RTH open and material transition/1-minute updates.
3. **Definition.** Separate expert heads for (a) wide-range internal/EQ-to-edge opportunity, (b) compressed/purged internal continuation toward extensions, (c) first open-to-projection leg, (d) later reversal/return through range, (e) projection partial retrace then continuation, (f) no useful move. Fit conditional `PATH/REACH/DEPART` distributions for 15/30/60-minute and named-session horizons; a head's applicability is a soft observed feature, not a future day label. Binding local refinement: [SR-C03](../SYSTEM_REFINEMENT.md#sr-c03).
4. **Output.** Common-target distributions and branch probabilities with uncertainty, no mandatory direction/confluence. Contradictory branches can coexist; G01 combines target-matched forecasts.
5. **Dependencies.** C01/02/04/06/17, M03; L01/02/03 role and G selection. Upstream learned forecasts must be OOF.
6. **Comparisons.** Source branch rules; stratified frequency with shrinkage; regularized multinomial/quantile models; boosted trees and duration-aware temporal specialist. Compare against one simple pooled model to justify subdivision. Binding further upgrade and child comparisons: [UP-C03](../UPGRADE_PATHS.md#up-c03).
7. **Training.** Same-date grouping, nested thresholds, all eligible prefixes including losers/no-trade/no-touch. Weight repeated daily updates to avoid treating one path as many independent days.
8. **Tests.** DRF inside-EQ continuation versus mistaken edge-fade, source-only SMT, large range with shallow target room, two reversals, no local gamma node and delayed 10:00 event branch.
9. **Acceptance.** Log/Brier/pinball and conditional calibration; improved pre-touch selection and net/day over faithful branch rules and pooled challenger, with sufficient independent dates per branch.
10. **Ablation/fallback/resources.** Remove width, order, prior value, timing, cross-assets, options; compare each branch contribution. Shrink rare branches to pooled baseline. Class B; small tabular/temporal models, minute cadence.

## C04 — Open location relative to prior auction structure

1. **Purpose/sources.** Preserve prior-value and prior-range distinctions in Jumbo and AMT; JXA-06/07/10, JFN-05, AM1/VP2/MAV.
2. **Inputs.** Prior completed RTH/ETH profiles/ranges, current known session open, gaps/settlement M12 and available preopen path. RTH and other named session starts; update subsequent re-entry/acceptance state.
3. **Definition.** Encode below/inside/above prior value and prior full range separately; distances to VAH/VAL/POC/PDH/PDL in ticks/prior-vol units, prior shape, gap and observed hold/re-entry duration. Opening above value does not fix direction. Named child C04.OPEN_TYPE preserves open-drive/test-drive/rejection-reverse/auction hypotheses: define an opening band, displacement d, persistence τ, prior reference R and evaluation horizon before prediction. Drive = qualifying directional departure with no opening-band revisit through the defined persistence window; test-drive = touch R before a qualifying drive opposite the O→R direction; rejection-reverse = qualified initial departure then cross back through the opening band and qualify the opposite drive; auction = repeated opening-band visits/low efficiency without qualifying drive. These are overlapping observable path attributes, not forced mutually exclusive truth; record their order. Candidate 5/15/30-minute horizons and tick/prior-vol thresholds are fold-selected operational definitions, not claimed proprietary source formulas. Live features use only the prefix; completed type is a matured label. Forecast traversal, acceptance/rejection and excursions alongside type attributes. Binding local refinement: [SR-C04](../SYSTEM_REFINEMENT.md#sr-c04).
4. **Output.** Open-location measurement plus target-specific transition distributions with uncertainty and insufficient-history mask.
5. **Dependencies.** Measurement port uses M04/06/12 and C02. Forecast port may use C07.measure, never the current C07.forecast. L prior-value candidates and G01 consume its outputs. Previous full-day profile excludes today’s later trades.
6. **Comparisons.** Source open-location tables; shrunken contingency/Markov model; logistic survival/boosted interactions. Separate data-derived probability estimates from unknown-sample source percentages. Binding further upgrade and child comparisons: [UP-C04](../UPGRADE_PATHS.md#up-c04).
7. **Rules.** Condition on known opening state and forward horizon, not eventual day shape. Preserve exchange calendar and profile algorithm cohort; missing profile cannot be assigned inside-value.
8. **Tests.** Above VAH but below PDH followed by short, below VAL inside range/below both, gap over value, source-specific ETH freshness and same open/different prior shape. OPEN_TYPE fixtures separate reference test before drive, drive then rejection through open, later return after early apparent drive, two-way auction and undefined reference; do not know “never returns” at the first minute.
9. **Acceptance.** Transition calibration and incremental value beyond open-gap/price-only model; matched opening-state cohorts and dependence-aware intervals.
10. **Ablation/fallback/resources.** RTH versus ETH, value versus range, POC/shape, subsequent acceptance. Fall back to price/range-only available model. Class A/B, small opening feature table.

## C05 — Adaptive clock, activity and auction-range discovery

1. **Purpose/sources.** Improve source windows rather than copy TradingView limits; user ambition, JXA-04/21/22, CRL-02, PIN075–083 unusual windows.
2. **Inputs.** Prior/training price/volume/volatility/calendar histories and current causal activity. All supported assets/sessions, with comparable baseline windows; discovery only inside each training fold.
3. **Algorithm.** Compare fixed source windows; constrained grid of start/end times with minimum duration; volume/event-quantile completion; volatility-clock accumulation; and auction state transition boundaries. Require a stopping rule computable from the prefix. Score candidate windows using nested predictive/economic objective with complexity penalty, instability penalty and registered search budget. Freeze chosen window/stop rule for outer test; no daily hindsight optimum. Binding local refinement: [SR-C05](../SYSTEM_REFINEMENT.md#sr-c05).
4. **Output.** Versioned `RangeDefinition`, realized causal completion event and formation uncertainty; downstream C01 object schema unchanged. Can return no range when minimum coverage/activity absent.
5. **Dependencies.** Offline F03/09/V03 search; live frozen window rules use M10/C07.measure and observed prefix only. C01/C03/L consume chosen definitions; same-cut future path forecasts cannot decide a range’s historical formation.
6. **Comparisons.** 06–09 and original windows; seasonal activity threshold; change-point/optimal stopping candidate; compact learned boundary hazard. Many source minute-specific windows are hypotheses with unknown selection history. Binding further upgrade and child comparisons: [UP-C05](../UPGRADE_PATHS.md#up-c05).
7. **Training.** Nested same-date folds; no boundary optimization on outer outcomes; each search attempt logged. Normalization and activity thresholds use earlier days; enforce bounded selection count.
8. **Tests.** Prefix stopping, event occurring after proposed boundary, shortened holiday, high-volume news burst, unchanged price with volume surge, same test date selecting different future-dependent window must fail.
9. **Acceptance.** Stable selected boundaries, coverage/sufficiency and gain over faithful windows after multiplicity and execution costs; reject brittle minute precision unsupported by adjacent-window sensitivity.
10. **Ablation/fallback/resources.** Shift windows, random matched windows, clock versus activity, no complexity penalty. Fall back to predeclared fixed windows. Class B/D; discovery on aggregates, not repeated raw-tape scans.

## C06 — Conditional excursion and P-zone distribution

1. **Purpose/sources.** Improve statistical/P-zone ideas transparently; JSS-01–07, JFN-07, JXA-19/22, DRF-U08, PIN statistical forecasts.
2. **Inputs.** As-of C01/02 range/path, C04.measure open location, C07/08 auction measurements, primitive C09–18/23/24 forecasts and G02.V variance mixture, observed participation and calendar. Issue at formation completion and predefined updates; current C03/C19 forecasts are excluded.
3. **Definition.** Predict joint upward/downward remaining excursions `U=max(0,max_{t<u≤t+h}(p_u−p_t))`, `D=max(0,max_{t<u≤t+h}(p_t−p_u))` and ordered touch outcomes. Zero anchors the excursion at the decision price; no valid future observations means censored/unavailable, not a zero-excursion outcome. Compare anchor-relative session O→H/O→L and edge-relative overshoot as distinct targets. Quantile bands q=.1/.25/.5/.75/.9/.95 are initial registered grid, not win probabilities. Source mean/median/weighted/minimum-average and SD populations are retained distinctly when disclosed; proprietary P-zone formula is not claimed. Binding local refinement: [SR-C06](../SYSTEM_REFINEMENT.md#sr-c06).
4. **Output.** Noncrossing excursion quantiles/joint samples and coverage intervals; L04 converts them to candidate zones and can select width conditional on forecast. Forecast range is not a hard cap or reversal probability.
5. **Dependencies.** C01/02/04.measure, primitive C09–18/23/24 and G02.V; F11 OOF. Outputs feed C03 then C19, G02.PATH, L04 and G reach. No current C03/C19/G02.PATH output feeds back into C06.
6. **Comparisons.** Seasonal empirical/weighted quantiles; quantile linear/GAM and distributional regression; boosted quantiles, copula/joint distribution and compact temporal model. Match target, sample and known inputs. Binding further upgrade and child comparisons: [UP-C06](../UPGRADE_PATHS.md#up-c06).
7. **Training.** Shrink sparse weekday/session/regime cells; use causal nearest-history matching, not current final realized vol. Quantile calibration uses separate chronological data; no exchangeability guarantee under drift.
8. **Tests.** Bear-side up/down swap, mean versus median-sum identity error, warmup, quantile crossing, current observation included in past distribution, no-touch, holiday and horizon mismatch.
9. **Acceptance.** Pinball/CRPS, joint coverage and reach calibration by asset/regime/coverage; improved zone utility after density and width placebos. A better excursion forecast must also improve selection or risk.
10. **Ablation/fallback/resources.** Remove regime/volume/IV, mean versus robust quantile, fixed versus adaptive windows, snap-to-profile versus free zone. Fall back to shrunken seasonal distribution. Class B; per-minute inference and cached training summaries.

## C07 — Auction acceptance, rejection, balance and discovery

1. **Purpose/sources.** Make AMT state observable and probabilistic; AM1/ALM/MAV/MAT/WIC, JTR-23, SKY core failures.
2. **Inputs.** M04/06 value areas, M07 VWAP, price path, traded volume, M10 effort/progress and active levels. Causal rolling and named-session windows, 1-minute/event updates.
3. **Definition.** Measure time/volume outside prior value, repeated closes/visits, net displacement, overlap, range expansion, failed returns and value migration. Define acceptance/rejection event thresholds as benchmark parameters; 'discovery' estimate uses only prefix features. Predict persistence, return-to-value, traversal and expansion distributions. Eventual session profile shape is a label, not a contemporaneous regime. Binding local refinement: [SR-C07](../SYSTEM_REFINEMENT.md#sr-c07).
4. **Output.** Continuous auction state, rule-state flags, calibrated next-state/path forecasts and uncertainty. No hard ban on using options in discovery or on reversals in trends.
5. **Dependencies.** Measurement port uses M04/06/07/10 and C04.measure. Forecast port may use primitive C volatility outputs; it does not require C04.forecast or current downstream Location forecasts. L roles and G consume its outputs.
6. **Comparisons.** Source balance/discovery rules; logistic transition/GAM; HMM/HSMM with causal filtering (never smoothing over future), boosted/temporal model. HMM assumptions are tested rather than dismissed universally. Binding further upgrade and child comparisons: [UP-C07](../UPGRADE_PATHS.md#up-c07).
7. **Training.** State labels distinguish deterministic observable states from inferred latent states; latent states evaluated by forward prediction, not visually pleasing naming. Fit train-only, align state identity across versions.
8. **Tests.** Brief wick outside value versus sustained trade, high volume/no progress, strong breakout with no retest, balance→discovery→failed traverse, late profile revision and causal filter versus hindsight smoother.
9. **Acceptance.** Transition likelihood/calibration, stability and incremental selection value; reject latent complexity if simple continuous features perform equally well.
10. **Ablation/fallback/resources.** Remove volume/time/order, RTH versus ETH, hard versus soft state. Fall back to continuous observed state. Class A/B, optional small sequence model.

## C08 — Value migration and multiscale auction relationships

1. **Purpose/sources.** Preserve developing/prior/composite profile relationships; VP2/MAV/RVP, JXA-09/16, CRL-06.
2. **Inputs.** M04/05/06 versioned profiles at RTH, full-session, swing and multi-session scales; current price and volume. Update after measured profile changes.
3. **Definition.** Track POC/VA center/boundary displacement, distribution distance/overlap, emerging secondary modes, valley filling and side-delta migration. Align raw contract/tick grids before comparison. Compare developing profile only with compatible elapsed-duration historical prefixes to avoid maturity bias. Binding local refinement: [SR-C08](../SYSTEM_REFINEMENT.md#sr-c08).
4. **Output.** Migration vector, balance split/merge events and forecasts of subsequent acceptance/traversal/continuation; uncertainty includes bin/anchor sensitivity.
5. **Dependencies.** M04–06/F08/F10; C07, L05/06 profile candidates and G same-target path forecast.
6. **Comparisons.** POC slope/overlap rules; regression/transition model; Wasserstein-style distribution features, multichannel profile CNN/TCN. Avoid assuming normal distributions or fixed 70% probability meaning. Binding further upgrade and child comparisons: [UP-C08](../UPGRADE_PATHS.md#up-c08).
7. **Training.** Fold-local bin/smoothing choices, same elapsed session and coverage, no final profile projection backward. Large grids use sparse standardized coordinates.
8. **Tests.** Same POC/different bimodal shape, grid shift, valley fills without POC change, new high-volume node, roll and mismatched elapsed-duration snapshots.
9. **Acceptance.** Distribution/geometry invariants and robustness to one-row shifts; incremental predictive/economic value beyond current price distance and simple POC slope.
10. **Ablation/fallback/resources.** Single scale versus multiscale, volume versus delta/TPO, migration versus static profile. Fall back to static valid objects. Class A/B; incremental sparse histograms and small embeddings.

## C09 — Historical range and seasonal volatility baseline

1. **Purpose.** Provide a strong interpretable floor for all richer volatility claims; JSS/PIN statistics, user rich-volatility ambition.
2. **Inputs.** Causal completed session OHLC, ranges, true ranges, return data and elapsed-time seasonality. Asset/session-specific, daily fit/update plus minute remaining-range forecasts.
3. **Definition.** True range `max(H−L,abs(H−Cprev),abs(L−Cprev))`; compare trailing mean/median/quantiles, EWMA and seasonal elapsed-time scaling. Separate price-point range from return variance; initial lookbacks 20/60/120 sessions are a registered grid, not inherited truth. Forecast future upper/lower excursions, not just average historic range. Binding local refinement: [SR-C09](../SYSTEM_REFINEMENT.md#sr-c09).
4. **Output.** Seasonal range distribution/quantiles and variance proxy with units/coverage; unknown warmup mask.
5. **Dependencies.** F08/09/C01; C06/19 and G02. Serves as missing-IV fallback if validated.
6. **Comparisons.** Previous range/ATR; seasonal robust distribution; linear/GAM/boosted regression with same lag features. More complex model must beat this baseline. Binding further upgrade and child comparisons: [UP-C09](../UPGRADE_PATHS.md#up-c09).
7. **Training.** Use prior completed sessions only; no zero-filled empty days or unfinished current day in historical mean. Normalize by contemporaneously known price/scale.
8. **Tests.** Holiday short session, overnight gap, no-price-change day, missing previous close, warmup and current-zero mean bias documented in Pine.
9. **Acceptance.** Proper forecast loss/calibration and remaining-room utility; sample-sufficient session/asset cohorts with date-block intervals.
10. **Ablation/fallback/resources.** Mean/median/quantile, seasonality, gap and decay. Sparse cell shrinks to asset pooled history. Class A/B minimal CPU/RAM.

## C10 — Garman–Klass measurement and forecast specialist

1. **Purpose/sources.** Preserve requested historical OHLC estimator as one expert, not a forward-vol answer by itself; dictated interpretation, TECH-03.
2. **Inputs.** Positive O/H/L/C over explicit completed intervals, actual contracts adjusted for roll returns; daily/session cadence.
3. **Definition.** Benchmark per-interval GK variance `0.5[ln(H/L)]²−(2ln2−1)[ln(C/O)]²`; aggregate consistently over n intervals. Keep jump/open assumptions and any negative numeric result flagged; independently verify original formula during implementation because external full text was unavailable here. Feed lagged measures to a forward variance/excursion forecast. Binding local refinement: [SR-C10](../SYSTEM_REFINEMENT.md#sr-c10).
4. **Output.** Measured variance in log-return², forecast target distribution, estimator quality/assumption flags. Annualization only for comparable display and explicitly declared trading intervals.
5. **Dependencies.** F08/09, C09 and G02/C06; no OI/options dependency.
6. **Comparisons.** Close-to-close/EWMA; lagged GK regression; quantile/boosted nonlinear specialist. Information held constant for model comparison. Binding further upgrade and child comparisons: [UP-C10](../UPGRADE_PATHS.md#up-c10).
7. **Training.** Log/robust scaling fitted in training; no full-session GK before close. Overnight jumps separately represented rather than silently claimed captured.
8. **Tests.** Constant price, known OHLC arithmetic, multiplicative price-scale invariance, malformed H/L, roll jump and unfinished interval.
9. **Acceptance.** Formula and units fixtures; QLIKE/variance error plus excursion calibration and incremental economic use versus C09.
10. **Ablation/fallback/resources.** GK versus close-to-close/YZ/RV on common dates; ignore uncertain interval and use baseline. Class A/B negligible feature cost, modest regressions.

## C11 — Yang–Zhang opening-jump-aware specialist

1. **Purpose/sources.** Preserve requested estimator with explicit session-open treatment; TECH-02, user volatility ensemble.
2. **Inputs.** At least n completed consecutive OHLC intervals plus previous closes; n>1, explicit close/open boundary and roll handling.
3. **Definition.** Let `o=ln(O/Cprev)`, `c=ln(C/O)`, `u=ln(H/O)`, `d=ln(L/O)`. Compute sample variances of o/c and mean Rogers–Satchell `u(u−c)+d(d−c)`. Benchmark `YZ=var(o)+k var(c)+(1−k)mean(RS)` with `k=.34/[1.34+(n+1)/(n−1)]`; verify source equation in implementation fixture. Forecast future variance using causal lags; do not assume a long cash-market overnight applies to every futures session. Binding local refinement: [SR-C11](../SYSTEM_REFINEMENT.md#sr-c11).
4. **Output.** Component variances, YZ measurement and forward forecast with warmup/coverage and gap interpretation.
5. **Dependencies.** F03/08/09, C09/G02/C06; session definition version required.
6. **Comparisons.** Close-to-close, GK and RS; linear/EWMA lag model; quantile/boosted specialist. Separate estimator value from nonlinear-model value. Binding further upgrade and child comparisons: [UP-C11](../UPGRADE_PATHS.md#up-c11).
7. **Training.** Choose n and session definition in training; contiguous valid intervals and explicit missing-gap policy. Scaling/correction never uses outer future data.
8. **Tests.** Opening-only jump, drift without range expansion, constant price, n=1 rejection, 23-hour futures versus RTH and roll transition.
9. **Acceptance.** Mathematical fixture/parity, QLIKE and conditional interval coverage; economic gain or useful risk improvement over C09/C10 with paired intervals.
10. **Ablation/fallback/resources.** Remove opening component, vary close boundary, matched GK/RV comparison. Fall back to validated available estimator. Class A/B small state and regressions.

## C12 — Multiscale realized variance and semivariance

1. **Purpose/sources.** Use richer tape to measure volatility and directional variation; user rich-volatility request, TECH-01/04, DA futures capability.
2. **Inputs.** Positive trade or valid midpoint prices at causal regular grids, F04/06 gap/quote quality and F08 returns. Multiple assets/sessions; update after 1s/1m/5m aggregates where data support them.
3. **Definition.** `RV=sum r_i²`, downside/upside semivariance `sum r_i²1[r_i<0/>=0]`; compare sampling grids, subsampling/pre-averaging and noise-robust estimators as registered variants. Zero returns due to stale carry are tagged, not mistaken for calm. Measurement window and forward target window differ. Binding local refinement: [SR-C12](../SYSTEM_REFINEMENT.md#sr-c12).
4. **Output.** RV/semivariances, sampling/noise diagnostics and a lag-based future variance/excursion forecast; units log-return² and covered duration.
5. **Dependencies.** F04/06/08/09, M09; C13/14/19/G02. Exact grid/price process remains in target ID.
6. **Comparisons.** Close-to-close and 5m RV; multigrid average and linear forecast; boosted/temporal lag model. Noise-robust complexity must improve real forecast loss beyond a well-chosen coarse grid. Binding further upgrade and child comparisons: [UP-C12](../UPGRADE_PATHS.md#up-c12).
7. **Training.** Sampling frequency and noise tuning train-only; same-date common cohorts. No final daily RV used in a morning forecast. Normalize causal intraday seasonality separately.
8. **Tests.** Alternating bid/ask bounce, constant midpoint, gap/stale feed, multiplicative price scaling, semivariance sum=RV, rollover and different observation grids.
9. **Acceptance.** Algebra/coverage exact; stable volatility-signature diagnostics; QLIKE/CRPS and economic width/risk utility on held-out dates.
10. **Ablation/fallback/resources.** Midpoint versus trade, sampling grid, semivariance split and noise correction. Fall back to C09/YZ when tape poor. Class A/B streaming return sums and modest models.

## C13 — HAR and multiscale forward-volatility expert

1. **Purpose/sources.** Convert realized measures into interpretable forecasts; TECH-01, earlier HAR ideas retained with evidence limits.
2. **Inputs.** Prior completed C12/C10/11 daily/session volatility, average preceding 5 and22 sessions, optional causal intraday prefix and overnight terms. Forecast daily and remaining named-session horizons separately.
3. **Definition.** Fit `y_next=β0+βd y_prev+βw mean5(y)+βm mean22(y)+ε`; compare variance, volatility and log-variance target versions with correct inverse transform/distribution calibration. Extend with signed returns/semivariance/events only as registered inputs; no copied coefficients. Binding local refinement: [SR-C13](../SYSTEM_REFINEMENT.md#sr-c13).
4. **Output.** Forward variance distribution/quantiles, residual uncertainty, horizon/version and insufficient-history flag. Do not transform a variance quantile directly into a claimed level reversal probability.
5. **Dependencies.** C09–12/F11; G02 common variance mixture, C06/L04 opportunity bands.
6. **Comparisons.** Persistence/EWMA; OLS/ridge HAR; HAR-quantile, boosted interactions and compact sequence model under matched lags. Long-memory marketing alone is not acceptance evidence. Binding further upgrade and child comparisons: [UP-C13](../UPGRADE_PATHS.md#up-c13).
7. **Training.** Chronological rolling/expanding training comparison, robust/log-normal residual options, separate calibration period and OOF outputs. No current final daily target leakage.
8. **Tests.** Lag alignment, holidays/five trading days not calendar days, 22-session warmup, log retransformation, same-date asset grouping and missing prior session.
9. **Acceptance.** QLIKE, calibration, tail error, stable coefficients/residuals and better downstream reach/width/risk utility than persistence; report performance by regime/year.
10. **Ablation/fallback/resources.** Remove weekly/monthly/prefix/extra channels; different training decay. Fall back to seasonal EWMA. Class B CPU minutes–hours depending grid, millisecond inference.

## C14 — Jump, discontinuity and burst-volatility expert

1. **Purpose/sources.** Distinguish continuous variation from rare jumps/bursts; TECH-04, JTR news-delay and discretionary event failures.
2. **Inputs.** C12 return grids, C17 known calendar, gaps/quality, M10 intensity and optional implied/VX inputs. Native and minute event views; forecast future jump/range tails.
3. **Definition.** Benchmark bipower `BV=(π/2)sum |r_i||r_{i−1}|` with explicit finite-sample correction convention; jump variation proxy `max(RV−BV,0)`. Add threshold exceedances normalized by preceding local scale and observed gap/volume burst. A noise artifact is not automatically a market jump; include data-quality distinction. Forecast event probability, signed tail and post-burst decay. Binding local refinement: [SR-C14](../SYSTEM_REFINEMENT.md#sr-c14).
4. **Output.** Measured jump proxy plus calibrated jump/tail/remaining-vol distribution; unknown when sampling is inadequate. Labels occur after burst/horizon maturity.
5. **Dependencies.** C12/C17/F06, M10; G02, C19 and P risk sensitivity.
6. **Comparisons.** Large-return threshold; logistic count/hazard and jump-augmented HAR; regime/temporal distribution model. Avoid assuming rare-jump asymptotics hold at every microsecond grid. Binding further upgrade and child comparisons: [UP-C14](../UPGRADE_PATHS.md#up-c14).
7. **Training.** Rare-event shrinkage, event/background samples with prevalence correction, train-only thresholds and sampling. No post-release value before published_at.
8. **Tests.** Single true price gap, spread bounce, stale-feed recovery, consecutive jumps, opening jump and scheduled release with no realized jump.
9. **Acceptance.** Tail calibration/precision-recall with natural base rate, proper scores and value in risk/remaining opportunity; stress sparse-event intervals and no-go on unsupported tails.
10. **Ablation/fallback/resources.** Remove calendar, pace, BV correction; matched event time/placebo dates. Fall back to broader uncertainty/seasonal volatility. Class A/B, bounded return buffers.

## C15 — Implied-volatility, skew and term-structure forecast specialist

1. **Purpose/sources.** Use options beyond broad GEX; user/DRF-U04, SKY Heatseeker, TECH-05. Predict physical future movement from risk-neutral information without conflating them.
2. **Inputs.** O02/O04 validated surfaces and uncertainty, ATM IV, fixed-delta/log-moneyness skew, curvature, term structure, forward-price estimate, coverage masks and C12 history. Each index/ETF/futures-options family separately, at 1-minute board cadence when observed.
3. **Definition.** Construct consistent-tenor total variance/interpolated ATM and downside/upside wing features, short-versus-long tenor slopes and IV-minus-prior-realized gap. Fit a mapping to future realized variance, directional excursions and tails; distinguish risk premium from forecast error. Equal-calendar DTE can differ in remaining trading minutes/settlement. The binding VOLATILITY_RESEARCH_SPEC adds individually registered smile/skew/curvature, total/forward/event variance, intraday surface-change, 0DTE and cross-IV targets. IV-minus-lagged-RV is a descriptive comparator; a forward variance-gap feature uses a same-horizon OOF physical forecast. C15.LEVERAGE owns early output port C15.SCENARIO: it uses completed O04 and permitted current measurements/preceding C20 state only, excluding current O10/O12/C19/O22/X06 and final G forecasts. Later physical heads are distinct outputs. Binding local refinement: [SR-C15](../SYSTEM_REFINEMENT.md#sr-c15).
4. **Output.** Common physical `PATH/variance` forecasts with surface/coverage uncertainty and no implied-certainty claim. Unquoted wings remain estimated inputs.
5. **Dependencies.** O02/O04/F07, C12; G02/C06, L options/statistical width selection. Use OOF surface-derived learned forecasts where applicable.
6. **Comparisons.** ATM IV scale rule; linear/GAM calibration against future movement; multitenor/skew regularized and boosted/set-feature experts. Compare to same-date C13 before claiming richness helps. Binding further upgrade and child comparisons: [UP-C15](../UPGRADE_PATHS.md#up-c15).
7. **Training.** Scale per asset/tenor and fit only training; calibrated uncertainty by observed/estimated coverage. Do not use end-of-day/next IV enrichment at an earlier time.
8. **Tests.** IV fraction/percent, short expiry, crossing tenor, missing wings, stale quote, AM/PM expiry and source-only SPX information for NQ. Also test the explicit skew/butterfly/total-variance arithmetic, delta-convention changes, same-contract versus rolling-tenor changes, event expiry straddles, near-zero return leverage and scenario-port cycles in the individual C15 experiments.
9. **Acceptance.** Proper variance/excursion scores, tail coverage and improved level/remaining-room decisions; identical coverage opportunity sets and cost stress.
10. **Ablation/fallback/resources.** ATM-only, no skew/term, individual chains, estimated-wing removal. Missing IV uses validated historical expert. Class B/C, reuse surface cache, minute inference.

## C16 — VX, volatility-complex and cross-market stress expert

1. **Purpose/sources.** Preserve VIX/VX information and limitations; VX4, GXF, user rich-volatility ensemble, DA-10.
2. **Inputs.** Actual acquired VX/other volatility futures and supported VIX option/daily index data, curve maturities, C12 price vol, equity/rates/currency context. Only available granularities; no assumed intraday VIX index stream. The audited VIX archive supplies minute option quotes and daily OI, while acquired VX futures are daily; these do not establish signed VIX trade flow or an intraday cash VIX print. Distinct options on VX futures require their own verified stream.
3. **Definition.** Build as-of front/second/constant-maturity curve levels/slopes/roll distance, changes and equity-return residual relationships. Calendar-adjust maturity and separate contract roll from stress. Fit forecasts for NQ/ES future tails/variance and directional transmission; a high VIX level is not a reversal command. Independently construct VIX-option-implied forwards, supported IV smiles/right tails and internal VVIX-style measures, then forecast their own evolution and physical receiver tails in separate heads. Actual historical methodology/venue/rate/expiry filters govern any official replication. The bounded three-date audit is feasibility evidence with unresolved quote/parity assumptions, not surface certification; C16.JOINT_STRESS consumes primitive measurements rather than current X06 fusion. Binding local refinement: [SR-C16](../SYSTEM_REFINEMENT.md#sr-c16).
4. **Output.** Stress/curve measurements and calibrated future-path distributions with coverage/age. Daily index input remains the last legitimately published daily observation with age and expected next publication; it is not a fabricated intraday print or automatically invalid merely because unchanged.
5. **Dependencies.** F02/07/08, C12 and X01 aligned measurements; optional X08/09/10 measurement ports only after their availability certification. It does not consume current X03–06 learned fusion. Outputs feed G02.V/C19/L and risk.
6. **Comparisons.** Prior VX return/curve rules; linear vector regression/GAM; boosted interaction/temporal expert. Compare against equity realized-vol only. Binding further upgrade and child comparisons: [UP-C16](../UPGRADE_PATHS.md#up-c16).
7. **Training.** Same-date cross-market grouping, train-only mapping/seasonality, fixed tenor conventions. Sparse futures/option history forms separate cohort, not imputed full history.
8. **Tests.** VX roll, contango/backwardation, missing front quote, daily VIX used before its close, divergent equity/VX moves and event-driven curve change.
9. **Acceptance.** Incremental calibrated tail/variance information and sequential risk/value gain after receiver latency; year/session/event stability.
10. **Ablation/fallback/resources.** Remove curve, level, options, non-equity channels and lag structure. Fall back to historical-vol experts. Class B; minute/as-available update, small cross-asset vector.

## C17 — Scheduled events, announcements and publication state

1. **Purpose/sources.** Preserve event-delayed Jumbo cycles and macro/earnings ideas without hindsight values; JTR-09/13/14, CRL-10, DA-11/TECH-12.
2. **Inputs.** Historically known release calendars and revisions, event family/expected time, actual publication/receipt when available, supported earnings schedule, settlement/OPEX/holiday dates. All sessions/assets; event and minute countdown updates.
3. **Definition.** Features: time-to/from known CPI/payroll/FOMC statement/press conference and other documented releases, overlapping events, scheduled uncertainty and instrument exposure. Source weekday tables are benchmark rules only. Surprise requires actual release and contemporaneous consensus vintage; absent here means unavailable. Separate calendar anticipation, immediate observed reaction and post-event decay. Binding local refinement: [SR-C17](../SYSTEM_REFINEMENT.md#sr-c17).
4. **Output.** Event state and conditional future volatility/path distribution; unknown schedule/actual values flagged. Event risk is a policy input; firm-specific news bans are P09 hard rules.
5. **Dependencies.** F03/04/07; C03/14/19/21 and X source effects. No guessed historical earnings timestamp.
6. **Comparisons.** Calendar-only bins; shrunken event-family regression/hazard; boosted interaction/temporal model after sufficient events. News text/fundamental valuation models deferred until timestamped data and incremental hypothesis exist. Binding further upgrade and child comparisons: [UP-C17](../UPGRADE_PATHS.md#up-c17).
7. **Training.** Event days/background matched by time/regime; group all same-date assets; no today's revised FRED values in past features. Rare events pooled with uncertainty.
8. **Tests.** 08:30 release inflating formation range, 10:00 delayed cycle, FOMC multi-stage event, rescheduled announcement, missing consensus, holiday and scheduled event with no move.
9. **Acceptance.** Event-conditioned calibration/utility over time-of-day-only model; false abstention/lost opportunity and tail-loss effects measured separately.
10. **Ablation/fallback/resources.** Remove weekday prior, actual surprise, exact timing; matched placebo event times. With only known calendar, return calendar-only state. Class A/B; low compute; future vintage acquisition is a named dependency.

## C18 — Participation, control and effort-progress forecast specialists

1. **Purpose/sources.** Give ordinary flow, cohorts, footprint and visible liquidity separate contextual responsibilities; RDL/WIC/YMA/RFE, CRL-14–17, user CVD breadth.
2. **Inputs.** M01 ordinary CVD, M02 cohort OHLC, M03 divergences, M09 OFI, M10 pace/efficiency, M11 memory and M13 footprint. Native/1s measurements aggregated to 1/5-minute Context cuts; all supported futures, receiver context via X.
3. **Definition.** Separate heads forecast (a) continuation after efficient aggression, (b) failed effort/reversal hazard, (c) side/control persistence, (d) volatility/participation expansion, (e) cross-cohort disagreement consequences. Each head uses declared feature subset and common future `PATH` targets; no claim of hidden participant inventory. Maturity-based outcomes never enter current state as labels. Binding local refinement: [SR-C18](../SYSTEM_REFINEMENT.md#sr-c18).
4. **Output.** Head-specific path distributions, applicability/uncertainty, and observed control features. G01 combines only shared-target predictions; L memory/range roles can act without a fine Response pattern.
5. **Dependencies.** M-series/F11 and C07.measure; X01/X07 measurement ports may provide aligned flow. No current X05/06 fusion or C07 current forecast is required. G01/L/P consume forecasts; fine ordered triggers remain deferred R-series.
6. **Comparisons.** CVD/OFI slope rules; ridge/logistic/GAM/HSMM; boosted and compact temporal models. Ordinary CVD, cohort close-only and true OHLC receive separate input ablations. Binding further upgrade and child comparisons: [UP-C18](../UPGRADE_PATHS.md#up-c18).
7. **Training.** Include background/no-trade states, same-date blocks, causal rolling normalization and unknown-sign masks. Avoid thousands of unregularized cohort×session cells; partial pooling then specialist where supported.
8. **Tests.** Positive delta/no upward progress, efficient small trades, opposite cohorts, no refresh after burst, same close delta/different extrema, absent MBP and late source flow.
9. **Acceptance.** Proper scores/calibration, contextual failure attribution and net/day lift over price/vol-only model; support measured per head, not all claimed from aggregate performance.
10. **Ablation/fallback/resources.** Remove each flow family and event order, compare price-only and equal-compute pooled models. Missing MBP retains trade-only expert if validated. Class B/E; initial minute decisions, compact models.

## C19 — Remaining-session movement and opportunity budget

1. **Purpose/sources.** Address unreachable levels, late confirmation and target chasing; JSS-07, JTR-06/12/23, JXA-12, SKY decoy/reach concepts.
2. **Inputs.** Elapsed session, observed excursions/realized variation, C06/C09–18 forecasts, active object topology, boundary time and liquidity. Update each decision/material event.
3. **Definition.** Predict remaining upper/lower extrema, time-to-move and probability of completing a candidate payoff path before the **earliest required boundary**. Model realized prefix and future remainder jointly/conditionally; do not subtract realized range from a point forecast of total range and assume the remainder cannot expand. Distinguish volatility opportunity from signed tradable payoff after entry costs. Binding local refinement: [SR-C19](../SYSTEM_REFINEMENT.md#sr-c19).
4. **Output.** Remaining `PATH` distribution, horizon truncation, reach/room probabilities and opportunity-cost features. Lower uncertainty/room can favor a nearer trade; it need not force abstention.
5. **Dependencies.** C06 then C03, G02.V, primitive C09–18/23/24, observable O11/O12/O13.measure geometry, optional O14.base forecast, and X01/02 measurements. F03/P09 provide frozen calendar/account boundary state. No current O13.forecast/O22/X03–06/G02.PATH output returns here; G04/06/07 and P consume C19.
6. **Comparisons.** Seasonal remaining-range table; survival/quantile regression conditioned on prefix; distributional boosted/temporal expert. Compare fixed daily ADR hard cap as a benchmark likely to miss expansion, not an imposed rule. Binding further upgrade and child comparisons: [UP-C19](../UPGRADE_PATHS.md#up-c19).
7. **Training.** Sample fixed decision cuts plus candidate events, weight each day appropriately, censor at actual session/boundary and handle holidays. Forecast inputs OOF.
8. **Tests.** Early exhausted range later expands, quiet AM/active PM, news after apparent clock window, target reachable only after flatten deadline, far large gamma node and near modest candidate.
9. **Acceptance.** Conditional reach/time calibration and sequential near-versus-deep selection value; report costly premature stops and futile waiting separately.
10. **Ablation/fallback/resources.** Remove prefix, IV/events, boundary truncation and object topology. Fall back to seasonal remaining distribution with wider uncertainty. Class B, per-decision small model.

## C20 — Regime and distribution-shift conditioning

1. **Purpose/sources.** Allow experts to specialize without one opaque Context label; CRL-08/09/17, user granular MoE requirement, source regime indicators.
2. **Inputs.** Causal price/volatility/liquidity/auction/event/coverage features, preceding model residuals only after label maturity. Asset/session/date scope; minute state updates, separate parameter refit schedule.
3. **Definition.** Compare interpretable continuous axes (trend efficiency, vol percentile, liquidity, balance, event proximity), rule regimes, causal HMM/HSMM filtering and change-point state. Output a soft state distribution and drift diagnostics; eventual trend-day or high/low is a future label. Coverage regime is explicitly separate from market regime to detect acquisition artifacts. Binding local refinement: [SR-C20](../SYSTEM_REFINEMENT.md#sr-c20).
4. **Output.** State probabilities/features, duration, model uncertainty and unsupported-state flag; no forced universal label vocabulary or mandatory expert shutdown on every change.
5. **Dependencies.** C07.measure/C09/C12/C17, M participation measurements and F07; V05 supplies only preceding matured residual state. This filtered state may condition primitive forecasts/gates without consuming their current predictions. Learned state models and parameters remain versioned.
6. **Comparisons.** No-regime pooled model; fixed thresholds and logistic interactions; HMM/HSMM/change-point or compact learned state. Evaluate by downstream forecast/decision gain, not retrospective visual fit. Binding further upgrade and child comparisons: [UP-C20](../UPGRADE_PATHS.md#up-c20).
7. **Training.** Inner folds for state model and gate, OOF states/predictions; freeze regime normalization. Assess rare-state support; filtered online inference only, no future smoothing.
8. **Tests.** Gradual trend change, sudden event, feed coverage drop with stable market, label permutation across refits, state oscillation and only post-maturity residual updates.
9. **Acceptance.** Stable incremental forecast/economic value, calibrated occupancy and sufficient effective dates; reject regime complexity if it only partitions noise or data eras.
10. **Ablation/fallback/resources.** No regime, no coverage indicators, duration versus memoryless and hard versus soft gating. Fall back to pooled validated expert; drift triggers review, not automatic retrain. Class B, small state.

## C21 — Session transition and time-dependent path expert

1. **Purpose/sources.** Preserve Asia/London/AM/lunch/PM relationships and Jumbo cycle exceptions; JTR-08/09/23, JXA London cases, PIN session/body/return studies.
2. **Inputs.** Completed previous-session ranges/shape/flow, current session open/prefix, C17 events, C19 room, source clock and overlap masks. All sessions allowed; no default lunch or overnight information ban.
3. **Definition.** Forecast next-session range/shape, return to previous open/body25/EQ/edges, reversal versus continuation and transition timing conditional on observed prior path. Source AM-balance→PM-expansion and AM-expansion→PM-balance are hypotheses. London body25, session range quadrant and O→O retracement are different targets. Preserve ordered versus unordered touches and precise check windows. Binding local refinement: [SR-C21](../SYSTEM_REFINEMENT.md#sr-c21).
4. **Output.** Transition/common-path distributions, explicit formation/check horizons, censoring and clock uncertainty; not an automatic directional trade at a named time.
5. **Dependencies.** C01/02/06/17/19/M12; L session references and G selection. Overlapping sessions only use prior information actually complete.
6. **Comparisons.** Source time-window hit tables; shrunken conditional frequency and survival model; boosted/duration temporal model. Correct source current-inclusive counts before any probability benchmark. Binding further upgrade and child comparisons: [UP-C21](../UPGRADE_PATHS.md#up-c21).
7. **Training.** Same-date/adjacent-session dependence handled as blocks; trade-date reset, holidays and missing windows explicit. Fold-local timing/window search; no retrospectively best session selection.
8. **Tests.** London close unavailable at NY open due overlap, Asia midnight crossing, event-delayed turn, no hit by check-end, wrong weekday timezone and source 07:00–05:01 typo.
9. **Acceptance.** Calibrated transition/time/target outcomes and economic value across sessions including zero-trade days; distinguish source touch rate from trade expectancy.
10. **Ablation/fallback/resources.** No prior session, no events, static timing and window shifts. Fall back to seasonal current-session model. Class B with small session-state tables.

## C22 — Context originator and applicability contract

1. **Purpose/sources.** Ensure Context can create actionable opportunities independently of fine Response; current user scope, DRF-U07/09/11, JTR internal continuation and cross-source reactions.
2. **Inputs.** Calibrated C/X/O common-path forecasts, active objects or causal source events, current executable receiver price, C19 remaining room and quality/risk state. Decision/event cadence.
3. **Algorithm.** Translate a forecast into an `Opportunity` only with explicit side, entry now or conditional future state, invalidation/stop/target/horizon and provenance. A receiver can have no local level if a qualified source event supports its opportunity. Pure context-originated proposals use current price or a bounded forecast-derived entry band, not retrospectively selected best price. No threshold bypasses G/P selection and risk. Binding local refinement: [SR-C22](../SYSTEM_REFINEMENT.md#sr-c22).
4. **Output.** Context-originated candidate with value inputs and confidence/applicability, or reasoned no-proposal; not an order.
5. **Dependencies.** F10, C19, X transmission and the L object protocol produce initial proposals before G04–08/P score and select them. The current proposal cannot require its own G score. Response evidence may later revise value, but absent Response is not a categorical veto.
6. **Comparisons.** No-context-originated candidates; simple context rule; calibrated statistical forecast threshold; learned conditional candidate proposal/ranker under same action set. Binding further upgrade and child comparisons: [UP-C22](../UPGRADE_PATHS.md#up-c22).
7. **Training.** Register proposal thresholds and negative/background candidate logging; downstream labels tied to birth cut; OOF predictions and search control. Separate generator coverage from selection quality.
8. **Tests.** NQ opportunity after SPX source touch with no NQ node, inside-EQ continuation, no valid stop/target room, conflicting context experts, stale receiver BBO and optional Response absent.
9. **Acceptance.** Causal feasible proposals, increment over level-only universe in sequential replay, density-matched background/price proposal controls and complete rejected-candidate accounting.
10. **Ablation/fallback/resources.** Remove source events/context-only proposals, require Response as explicit comparison, vary bounded entry offset. Missing critical execution inputs means no candidate. Class B per decision; keep all proposals on disk.

## C23 — Parkinson high-low variance specialist

1. **Purpose/sources.** Preserve the explicit CEX-06 range-estimator alternative as an independently scored comparator; TECH-17.
2. **Inputs.** Positive completed interval high/low, exact session duration, F06 quality and F08 roll handling. Daily/session measurement, causal intraday-prefix variants separately named.
3. **Definition.** `v_P=mean([ln(H/L)]²)/(4 ln 2)` over the registered window. This diffusion-based range estimator omits an unobserved close-to-open jump; keep gap/duration assumptions explicit. Feed only prior measurements to a separate forward variance/excursion regression. Binding local refinement: [SR-C23](../SYSTEM_REFINEMENT.md#sr-c23).
4. **Outputs/labels.** Historical log-return variance, assumption/coverage flags and calibrated future variance/path forecast; historical efficiency claims are not predicted trading improvement.
5. **Dependencies.** F03/08/09, C09, G02/C06. No options feed required.
6. **Comparators.** Close-to-close/EWMA, GK/YZ/RS on common intervals, linear lag forecast and regularized nonlinear challenger. Binding further upgrade and child comparisons: [UP-C23](../UPGRADE_PATHS.md#up-c23).
7. **Learning.** Lookback/interval choice in inner folds, as-of scale and no completed-day range before close. Missing bars do not count as zero range.
8. **Tests.** T-C23: constant price, multiplicative scale invariance, opening-only gap, nonzero drift, incomplete interval and synthetic diffusion/finite-grid bias.
9. **Acceptance.** Exact equation fixtures; QLIKE/calibration and incremental remaining-room/width utility, uncertainty grouped by date. Reject unsupported advantage under jumps/noise.
10. **Ablation/fallback/resources.** Range versus close data, gap channel and seasonal duration; fallback C09. Class A/B, negligible streaming cost and small regression trials.

## C24 — ARCH/GARCH conditional-variance challenger

1. **Purpose/sources.** Preserve DTM-A03/CEX-06 statistical forecasting proposal, independently compared with HAR and richer ensembles; TECH-18.
2. **Inputs.** Causal completed return/residual series with explicit mean model, session/grid, F08 roll treatment and missingness; daily/session or declared intraday step.
3. **Definition.** Baseline GARCH(1,1): `h_t=ω+α ε_(t−1)²+β h_(t−1)`, nonnegative coefficients and positive ω; stationary variant imposes α+β<1. ARCH removes lagged h. Fit constrained likelihood/quasi-likelihood; initialize from training history and forecast multi-step variance with explicit horizon aggregation. Student-t innovations are a separate research variant, not assumed Gaussian tail adequacy. Binding local refinement: [SR-C24](../SYSTEM_REFINEMENT.md#sr-c24).
4. **Outputs/labels.** Conditional forward variance/distribution, persistence/fit diagnostics and instability/abstention flag. Excursion/reversal probabilities require a separately calibrated path model.
5. **Dependencies.** F09/F11, C09/C12 targets and G02 common variance mixture; independent target score versus C13 HAR.
6. **Comparators.** Constant/EWMA, low-order ARCH/GARCH, HAR, optional asymmetric volatility model only with registered equation/reference/complexity budget before use. Binding further upgrade and child comparisons: [UP-C24](../UPGRADE_PATHS.md#up-c24).
7. **Learning.** Mean/variance parameters and innovation distribution fit in chronological training; convergence/persistence checked per fold. No smoothed future variance used as a historical feature.
8. **Tests.** T-C24: positive variance, zero/large residual, near-unit persistence, failed optimizer, holiday gaps, missing return and multi-step recursion.
9. **Acceptance.** QLIKE, distribution calibration, residual serial-dependence diagnostics and downstream value under same information/cohort. Better in-sample likelihood alone insufficient.
10. **Ablation/fallback/resources.** ARCH versus lagged variance, innovation tails, mean model and extra predictors; unstable fit falls back to EWMA. Class B, CPU seconds–minutes per small fit, grid/repeated folds dominate.
