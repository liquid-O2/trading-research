# Research specification for every family

Version: **2026-09-07-research-v2**. This is the single detailed specification supporting [PLAN.md](PLAN.md). Every family below receives explicit definitions, timing/data treatment, statistical questions, model comparisons, failure checks and outputs. Volatility has the same standing as the other families. These sections describe research content; they are not separate mandatory engineering pipelines.

The [unit catalogue](UNIT_CATALOG.md) retains all previous parent and child definitions, source alternatives, local cases and upgrade references. Consult a mechanism's exact retained definition when implementing it. The current research roles and shared acceptance rules here supersede the historical full-trading workflow. A linked source example or proposed improvement remains a hypothesis until measured.

**Quality is not negotiable for speed.** Each eligible required mechanism retains its actual computational definition, input/clock/unit conventions, state and update logic, numerical assumptions, interfaces, source-specific cases and applicable improvement comparisons. The family sections organize that work; they do not replace the detailed mechanism contracts. A working proxy, one representative child or synthetic positive control cannot certify the intended full measurement/model. Preserve good necessary work and remove redundant orchestration, repeated reading and unrelated gates. A blocked exact mechanism remains explicitly blocked even if a separately labelled proxy is useful elsewhere.

## Shared data, statistics and evaluation

**Observable population.** For each study identify the raw instrument/contract, data version, date/session, formation window, observation cut, source publication/receipt assumptions and label endpoint. Retain event time, known-at time and revision lineage separately. Report source coverage before examining the outcome. A missing record, invalid quote or incomplete window is not zero flow, quiet activity or a failed event. The population is the actual eligible 2020-onward data for that question; older Jumbo/OHLC experiments have separate declared cohorts.

**Data actually needed.** Validate critical fields and whole intended windows/partitions for the selected cohort after a bounded pilot. Preserve native values and versions. Use validated MBP-1 trade and best-quote projections with explicit action, side, flags, source sequence and correction handling. A trade and the last update of a book event are different conditions; preserve combined flags and multiplicity. Reconcile against standalone trades on relevant source/cohort cases. An acquired continuous contract identifies the observed instrument sequence; do not invent unacquired competitor volumes or compare price jumps across an unhandled roll. A study of that observed sequence is distinct from a volume-selected-universe study. A best-quote dataset cannot establish full-depth queue behavior. Reuse the detailed [source contract](../trading-model/MARKET_DATA_SOURCE_CONTRACT.md) and [data capability audit](../trading-model/DATA_CAPABILITY_AUDIT.md) for exact fields and limitations.

**One reusable evidence path.** Store admitted observations, measurement/feature tables, a candidate/episode table where relevant, matured labels, chronological splits and model outputs with readable provenance. Share identical computations. Different targets or clocks keep their own identity and score. Use existing readers, reducers, labels, folds and evidence tools when they serve this path; a new general-purpose service is not a prerequisite.

**Statistical report.** Include counts of independent dates/episodes/reports, eligible and excluded observations with reasons, descriptive distributions and tails, conditional frequencies/path distributions, timing curves, effect sizes and uncertainty. Treat repeated minute prefixes or retests from one day/contract/idea as dependent. Compare paired variants on the same eligible samples. Where support is sparse, pool/shrink appropriately or report inconclusive results. Descriptive correlations are not causal effects.

**Timing and search.** Preserve disclosed source clocks and thresholds as named baselines. Use a bounded development search for formation, activity, lag, normalization, decay, smoothing and prediction-horizon choices. State the scientific reason for candidates; avoid a full Cartesian product. Compare information gained against the later availability of a longer window. Fit choices and transforms only on training/development data, then assess them on held-out chronological dates. Account for overlap and label publication/maturity when purging; never reuse the final test to keep improving a winner.

**Model quality.** Use the target-appropriate baseline and primary score. Probability forecasts need proper scores and calibration; continuous/distribution forecasts need error or distribution/quantile scores and interval coverage; duration/reach forecasts need censoring-aware assessment; exact calculators need independent arithmetic/data fidelity. Compare error by session, year, volatility, coverage and age where supported. Use learning curves, residuals and a stronger information-matched learner when diagnosing a poor result. Assess whether an added input provides useful information or a prespecified interaction; lack of isolated gain does not prove no joint value. State practical-effect and uncertainty rules before confirmation.

**Combining Context.** Preserve distinct targets such as terminal return, integrated variance, first passage and node migration. Only compatible targets, horizons, cuts and receiver instruments can be blended directly. Train mixtures/calibration on legitimate held-out or out-of-fold predictions and score the final outputs. Compare a transparent blend with independently trained specialists and justified shared representations. Do not count duplicated sources or model names as independent evidence. Missing-expert masks and fallback behavior are part of the evaluated input set.

**Controlled updating.** Once a frozen baseline exists, compare justified historical refit windows, recalibration and retirement rules on the same chronological populations. Select update rules on development dates and preserve an incumbent/fallback; do not use future drift labels to decide an earlier update. Diagnose changed data quality, calibration and predictive relationships separately. These are evaluated research alternatives, not prerequisites to building a live monitoring platform.

**Research and later trading.** Current comparisons establish measurement fidelity, predictive support and conditional Location quality. They do not require broker/order/account machinery. A simple outcome sensitivity calculation may clarify practical relevance, but it must retain its assumptions and cannot be called a complete trading result. Subsequent trading-policy selection, execution economics and prospective operations have separate requirements.

## 1. Jumbo, ranges and session paths

Retained core: C01–C06, C21 and their children; range-related M12 and L01–L04 definitions. Preserve every disclosed source clock and range variant in the catalogue, including prior-RTH, overnight/premarket, 06:00–09:00, source-specific weekly/combined windows and timing/event-delayed alternatives. A convenient first experiment does not narrow this family to one range.

### Measurements and timing

| Mechanism | Definition and required distinctions |
|---|---|
| Formation and geometry | Preserve calendar/timezone, half-open interval, raw contract, completed/partial state and first available publication. Record O/H/L/C, width, open position and prior-known scale. A range whose final bar has not arrived is unfinished. |
| Internal and extension coordinates | Keep EQ, range quarters, source body quarters and range open distinct. With width W=H−L, an edge extension H+kW differs from the normalized coordinate L+kW. Preserve source ratios and tie rules explicitly. |
| Multiple anchors | Record prior-RTH versus full-session range/value, build-window identity, overlap/nesting, relative widths and shared formation observations. Relate ranges without merging their clocks or double-counting ancestry. |
| Ordered paths | At each observed prefix record breaks, sweeps, reclaims, order, elapsed duration and unresolved state. Keep no-break, one-sided break, both-side break, ambiguous order and incomplete observation separate. |
| Opening/session state | Use information available at the open or later stated cut. Open above/below/inside prior structures and a subsequently observed open-type path have different availability. Preserve transition, opening-drive/failure and delayed-event branches. |
| Historical statistics | Distinguish absolute historic price levels from excursions anchored to today's reference. Mean, median, dispersion, disclosed weights and conditional quantiles are distinct constructions. An undisclosed vendor formula remains unresolved. |

### Statistical questions

Measure the distribution of formation width, normalized width and opening position; internal versus extension travel; single/double/no-break frequencies; ordered sweep/reclaim paths; time to first/second boundary; maximum favorable/adverse excursion; and remaining movement from each cut. Preserve internal continuation, internal reversal, extension continuation, failed break and delayed-event outcomes rather than forcing every session into one eventual day type.

Compare the source formation clocks, the source 09:40–09:50 timing hypotheses where specified, neighboring phase shifts, activity-completed windows and auction-completed windows. A later cut gets only the information available at that cut and a correspondingly shorter remaining horizon. Include unsuccessful/no-event dates in timing curves. Control width, day/session, prior volatility and source overlap so a clock improvement cannot be explained solely by selecting narrower ranges or more opportunities.

Test whether relationships between multiple ranges improve the same path target beyond each range alone. Separate geometry, timing, contextual path classification and Location quality in the comparisons. Report stability across years, ordinary/event days, width regimes and relevant roll/session cases.

### Models and comparisons

| Question | Baseline and justified challengers | Individual evidence |
|---|---|---|
| Ordered path and internal/extension branch | Source finite-state rules and shrunken transition frequencies; regularized multinomial or discrete-time duration models; compact sequence model if prefixes contain additional information | Proper scores/calibration by branch and elapsed time; order consistency; independent date support |
| Formation window | Disclosed clocks; seasonal activity threshold and bounded clock perturbation; train-only activity/change-point/boundary-hazard discovery | Same-target gain, completion delay, phase stability, missing-window rate and candidate density |
| Conditional excursions/P-zones | Seasonal empirical mean/median/quantiles; regularized quantile/distributional model; boosted or compact temporal challenger | Quantile coverage, tail calibration, dependence of upside/downside excursions and conditional Location quality |
| Session transitions | Time-of-day transition table; state-and-duration model; supported event-conditioned challenger | Held-out timing/path improvement beyond the ordinary session clock |

Do not infer barrier order from a terminal-return distribution. Distinguish a daily aggregate forecast from its prefix-conditioned update and fixed-end remaining-horizon forecast. If a joint path model is used, compare coherent joint outputs with simple separate baselines without importing future path features.

### Fixtures and failure checks

Independently check zero width, missing early extreme, late final trade, incomplete formation, DST, cross-midnight windows, holiday-shortened sessions, prior-RTH revisions, roll-coordinate boundaries, body/range quarter differences and the extension-coordinate identity. Remove future data and verify that earlier ranges and predictions do not change. Preserve ambiguity when OHLC cannot resolve event order. Do not backdate a confirmed break/reclaim or a final open-type label.

### Evidence and outputs

Deliver a range/path/timing report, a reusable table of available range states and matured path outcomes, independently scored range/session Context outputs, and evaluated internal/edge/statistical locations. The first practical study may use the already implemented geometry; the completed family report must account for every retained meaningful range/path variant. Link exact source definitions and justified exclusions, rather than reproducing all original material in each report.

## 2. Auction, profiles, footprint and reference structure

Retained core: M04–M07, M12–M13, C07–C08; L05–L07, L11–L12 and relevant prior-session definitions. This family covers the full auction representation, not just a POC number or one value-area formula.

### Measurements and timing

| Mechanism | Definition and required distinctions |
|---|---|
| Volume and delta profiles | Aggregate actual eligible trade-at-price volume. Keep bid/sell, ask/buy and unknown-side mass; signed delta is not a nonnegative probability distribution. Preserve exact source/bar-allocation comparators separately. |
| Formation anchors | Session, calendar, swing/leg, explicit Jumbo and causal event anchors remain distinct. An anchor selected after a reversal cannot make its retrospective profile available before selection. Preserve source accumulation windows and source display rules separately. |
| Geometry and topology | Fix tick/grid origin, row width, overflow, smoothing, value-area rule, tie/plateau policy, POC, nodes, shelves and valleys. Preserve raw mass before transformations. Distinguish prominence across smoothing scales from persistence across time. |
| Time-at-price | TPO bracket occupancy, executed-trade dwell and displayed-quote occupancy are different observations. Keep initial balance, single prints, tails and naked references with explicit bracket and completeness conventions. |
| VWAP and dispersion | Compute volume-weighted price and declared dispersion/quantiles from the eligible tape. Preserve source anchors, moving-anchor residuals, band conventions and zero-volume cases. A weighted price band is not automatically a calibrated future path interval. |
| Footprint | Preserve per-price side mass, diagonal/stacked imbalance rules, row adjacency, within-bar structure and true timestamps. Bar candle shape, trade footprint and full book depth have different information. |
| Opens/gaps/references | Distinguish observed session open, official settlement, prior close, cash open, futures open, period open and source-specific print. Preserve release time, raw coordinate and contract/adjustment mapping. |

### Statistical questions

Measure profile-shape distributions, node prominence/width, side concentration, value migration, acceptance/rejection and repair. Compare newly added mass, actual corrections, rebinning and normalization effects so apparent migration is not attributed automatically to new trading. Analyze POC/value relationships across anchors while accounting for shared input mass.

For nonnegative profile mass v on a fixed grid, record total mass and normalized shape separately. A one-dimensional cumulative-mass distance can summarize shape displacement only on compatible support with overflow reported. For future-profile questions, separate future added volume, no-new-volume and the distribution of added mass; derive future POC/value from that law rather than leaking a completed-session profile.

Study future contact/reaction at shelves, valleys, side-delta concentrations, TPO structures and VWAP bands; gaps filling or extending; departure from opens/settlements; and value acceptance versus discovery. Include no-contact, traversal and failed repair. Test binning, smoothing, bracket length, anchor age and update cadence jointly with their availability and geometry consequences.

### Models and comparisons

| Question | Baseline and justified challengers | Individual evidence |
|---|---|---|
| Auction state and migration | Source categorical rules and seasonal frequencies; regularized state/duration model; shape features or compact profile representation | Proper scores, observed transition/duration calibration and increment over price/range alone |
| Profile representation | Source bar proxy, exact unsmoothed trade profile, weighted landmarks, multiscale topology and compact spatial basis | Mass fidelity, robustness to grids/anchors, conditional path and Location increment |
| Developing profile | Historical prefix-matched reference; model of added volume plus conditional mass shape; compact spatial/temporal challenger if supported | Added-volume error, no-volume calibration, shape/overflow score and derived POC/value accuracy |
| VWAP/reference behavior | Distance/age/time baseline; conditional excursion or duration model; joint auction/flow challenger | Band coverage and reach/reaction beyond distance, time and volatility |
| Footprint information | Price/OHLC and ordinary flow baseline; side geometry/stacked structure; compact multiscale channels | Increment on the same windows and paths, with source-resolution and row-width sensitivity |

Keep learned shape or forecast improvements separate from changes in the number/width of Location candidates. A model that forecasts a future computed profile is assessed against that declared profile definition; this is not evidence of hidden inventory or price control.

### Fixtures and failure checks

Check volume and side-mass conservation; duplicate/corrected trades; POC ties and plateaus; grid boundaries; signed versus unsigned mass; empty/partial brackets; a price crossing without an observed trade; causal swing-anchor confirmation; zero volume; irregular sessions; moving-anchor revisions; and settlement publication after its position date. Demonstrate that source display toggles do not alter numeric measurements. Preserve incomplete coverage instead of creating synthetic dwell or profile tails.

### Evidence and outputs

Deliver a profile/auction/reference statistics report; reusable raw and transformed shape measurements with clock/anchor provenance; independently scored auction/migration/reference Context; and conditional quality for profile, delta, TPO, VWAP and reference Locations. Report the contribution of exact trade-derived information relative to retained source proxies without assuming either wins beforehand.

## 3. Order flow, participation, structure and aggression memory

Retained core: M01–M03 and M08–M11, C18, L08–L10/L19. The observable definitions and descriptive questions from R01–R18/R20–R22 also belong here where they inform statistics, Context or Locations; their complete Response entry/exit policies remain later. Retain discretionary-source mechanisms with exact observable definitions, including failed and quiet branches.

### Measurements and timing

| Mechanism | Definition and required distinctions |
|---|---|
| Ordinary CVD | Sum signed eligible executed size with explicit source-side mapping, unknown-side treatment, reset/anchor and correction policy. Preserve exact increments and the available prefix. |
| Cohort CVD | Keep disclosed hard-size bins, adaptive train-only bins, overlaps and justified continuous/soft cohorts distinct. For a partition, weights/mass must reconcile. Trade size is an observation, not participant identity. |
| True cohort OHLC | Compute each cohort's cumulative path open/high/low/close from its actual ordered within-bar updates, including the opening value. Close-only aggregates cannot reconstruct those extrema. |
| Divergence/SMT | Freeze the two endpoints, causal confirmation, scales and alignment. Keep price/CVD, inter-cohort and cross-instrument comparisons distinct. Compare slopes/extrema and reference breaches without selecting future favorable pivots. |
| Quote pressure | Preserve the validated best-quote state, OFI/imbalance, price changes, displayed net recovery and source-event rates. Quote-side changes, executed flow and inferred replenishment have different semantics. No full-depth support/layering claim follows from MBP-1. |
| Intensity/effort/progress | Separate event count, executed size, signed pressure, elapsed covered time, price displacement, path variation and lagged markout. Low exposure/coverage, zero effort and no progress are explicit cases. |
| Swings and structure | Confirm pivots/directional changes only when their rules become observable. Keep multiscale swing trees, retracements, displacement, FVG/imbalance, order-block and rejection-block definitions distinct and source-specific. |
| Memory and origin | Store actual effort/price origin, side/cohort, known confirmation, decay clock, price support, visits and matured markouts. Time, volume and visit decay are separate variants. Historical aggression is not observed surviving inventory. |

### Statistical questions

Measure ordinary and cohort flow distributions, persistence/reversal, cross-cohort disagreement, within-bar excursions and incremental information in true OHLC. Compare fixed source cohorts with train-only adaptive/soft alternatives and report both count-weighted and size-weighted cohort occupancy.

For quote/tape studies, compare trade-only, quote-only and combined observations on matched covered windows. Analyze pressure versus progress, delayed price response and net recovery after depletion under the actual event semantics. Estimate timing curves for activity/response horizons, quote lags, burst thresholds and memory decay. Keep unknown signs and absent coverage visible.

Translate absorption, exhaustion, climax/stopping burst, refill/resqueeze, balance break/retest/failure, POC flip, imbalance defense, rewarded-side memory, minor-node defense and repeated retests into observable prefixes and outcomes. Include no-retest, quiet failure, failed squeeze and renewed same-direction squeeze. If a description is ambiguous, retain a small explicit source-variant comparison or targeted blinded annotation; a compelling example chart does not establish frequency or participant intent.

### Models and comparisons

| Question | Baseline and justified challengers | Individual evidence |
|---|---|---|
| Flow surprise | Raw totals and seasonal/time-exposure baseline; regularized count/intensity or expected-state residual model; marked point-process challenger when data supports it | Likelihood/calibration, residual stability and incremental path information |
| Effort versus progress | Source thresholds and normalized effort/displacement; regularized conditional response surface; bounded nonlinear challenger | Forward markout/path score, scale/lag sensitivity and increment over price plus ordinary flow |
| Cohort/control Context | Ordinary CVD and hard-cohort closes; true cohort OHLC and divergence; soft/adaptive cohort features or compact temporal model | Same-target score, calibration, effective date support and information-matched ablations |
| Sequence prefixes | Source finite-state definitions and shrunken duration frequencies; duration/hazard model; compact sequence challenger | Branch-specific proper scores, timing and known-prefix availability, including failure/no-event cases |
| Memory/structural value | Fixed source filters and price-only clusters; conditional decay/retest/markout model; supported learned representation | Location reach/reaction/lifetime and increment beyond current flow, distance and age |

Expected-intensity residuals condition by default on pre-window state plus known exposure/time; an effort-versus-progress description may use completed-window effort when explicitly declared. Fit all baselines/scales inside the chronological closure. Learned residuals are descriptive/predictive features, not automatically martingale innovations or causal effects. Do not replace a deterministic CVD calculation with an opaque estimate.

### Fixtures and failure checks

Check buy/sell mapping against source semantics; corrections and duplicate identity; gap/snapshot combinations; trades lacking a book-event completion flag; full cohort partition mass; unknown-side channels; weighted OHLC extrema; reset boundaries; zero/near-zero normalization; delayed quote availability; standing-quote eligibility; swing confirmation; anchor revision; memory expiration; and repeated-visit identity. Full-depth hypotheses retain a data dependency, with any top-of-book proxy named separately. Future successful markout must not select an initial memory object or confer protection retrospectively.

### Evidence and outputs

Deliver order-flow/cohort/structure/memory statistics and timing results, independently scored participation/control Context, and evaluated structural/aggression-memory Locations. The current milestone includes the statistics of relevant discretionary patterns. It does not require building a complete Response trading policy or validating broker fills. Preserve the ability to use those observations in later Response comparisons without forcing confirmation on current Context/Location opportunities.

## 4. Physical volatility, implied volatility and remaining movement

Retained core: C09–C16, C19, C23–C24 and every named child, with compatible G02 combination and L04 use. Preserve the complete previous volatility depth within this shared specification; the equal-depth treatment of other families does not reduce it.

### Measurements and timing

| Mechanism | Definition and required distinctions |
|---|---|
| Seasonal range/variance | Keep price range, percentage range, return variance and extrema distinct. Separate overnight jump, session variation and time-of-day seasonality with declared calendars/annualization. |
| OHLC estimators | Preserve Parkinson, Garman–Klass and Yang–Zhang as distinct measurements and forecasting inputs. State price/log-return conventions, sample windows, opening-jump treatment and assumptions; do not choose the label that favors an estimator. |
| Realized variation | Preserve sampling frequency, microstructure-noise treatment, realized variance, positive/negative semivariance, jump/discontinuity and burst measures. Missing tape cannot become low variance. |
| Conditional dynamics | Compare seasonal persistence, multiscale/HAR lag summaries, smooth distributed lags and declared ARFIMA long-memory alternatives; preserve ARCH/GARCH and asymmetric/RV-augmented alternatives with valid domains. |
| Implied features | Retain ATM, smile/moneyness shape, delta skew, curvature, expiry term structure, event variance, model-free comparisons, physical/implied gaps, intraday changes, leverage/asymmetry, 0DTE remainder and cross-chain IV. |
| Volatility complex | Keep forward construction, VIX-option surface, volatility-of-volatility/VVIX information, observed VX curve, joint stress and separately available VX-option features. VIX and VX option underliers/payoff conventions must not be interchanged. |
| Remaining movement | From a stated cut predict the distribution of remaining upside/downside excursion, integrated variation and reach/duration where supported. A daily variance scalar cannot supply all of these targets. |

### Statistical questions

Study sampling/estimator sensitivity, seasonal persistence, opening jumps, asymmetry and scale dependence on matched observation intervals. Report variation, terminal-return dispersion and extrema separately. Examine whether jump, implied shape, event and volatility-complex information improves forecasts beyond the same historical-volatility baseline.

For each implied feature record quote age, bid/ask inversion interval, underlying/forward, expiry, rates/dividends where relevant, support and interpolation/extrapolation. Compare intraday surface dynamics with a frozen prior surface and mechanical spot/time repricing. A changing computed surface is not automatically new independent information. Keep sparse wings, 0DTE and event maturities visible in the cohort.

Compare formation/lookback/update windows, forward horizons and fixed-end remaining-session cuts. Do not subtract realized variance from a daily expectation and call the result a valid conditional remaining-path law without deriving/testing that model. Terminal-return aggregation must retain covariance unless the declared model justifies an approximation. Implied-to-physical conversion is an empirically tested forecast relationship.

### Models and comparisons

| Question | Baseline and justified challengers | Individual evidence |
|---|---|---|
| Forward physical variation | Seasonal/persistence and OHLC measures; HAR/distributed lag, GARCH/asymmetric or realized-measurement augmentation; declared ARFIMA and nonlinear challenger | Appropriate variance loss, tail/interval calibration, target sensitivity and time/regime support |
| Jump/asymmetric risk | Seasonal event frequencies and semivariance; jump occurrence plus conditional size/scale model | Probability calibration, tail separation and incremental information beyond total variation |
| Implied information | Physical-only baseline; ATM then shape/term/event/complex input additions with fixed model class | Matched-horizon information gain, coverage/age sensitivity and residual dependence |
| Remaining movement | Seasonal remaining-range table; prefix-conditioned quantile/distribution/duration model; compatible joint path challenger | Upside/downside quantile coverage, remaining-room/reach calibration and Location-quality improvement |
| Coherent combination | Single specialist and transparent compatible blend; target-specific shared/residual or nonlinear combination | Held-out final-output score, calibration, missing-input fallback and duplication sensitivity |

Every source estimator remains independently checked, but shared feature kernels and a common evaluation runner serve them. Separate variance forecasts from standard deviation/log-scale targets and integrate a declared predictive law when retransformation requires it; exponentiating a mean on a log scale is a different functional. A long-memory model needs an exact order/domain/filter/initialization definition before execution. Larger neural architectures remain justified challengers rather than mandatory milestones.

### Fixtures and failure checks

Check units/annualization, open/close ordering, zero/negative input domains, discontinuous sessions, missing windows, noise and estimator bias controls, forward/expiry identity, calendar-time versus remaining-time Greek signs, quote intervals, invalid surface support, log retransformation, noncrossing quantiles and horizon compatibility. A quantile band does not imply reversal probability, and integrated variance does not identify first barrier order. Keep index-option and futures-option conventions distinct.

### Evidence and outputs

Deliver the full volatility/IV/complex statistics and timing report, independently scored specialists for their own targets, evaluated final combinations and calibrated remaining-movement outputs for Context and statistical Locations. Retain the complete ATM/skew/curvature/term/event/VRP/model-free/intraday/leverage/0DTE/cross-IV and VIX/VX subprograms with exact support or dependency dispositions. No single volatility model substitutes for the rest of the family.

## 5. Options, open interest, exposures, flow and nodes

Retained core: all O01–O23 and their children, supporting C15/C16 and L13/L14. Preserve strike × expiry × chain × asset × time and observable support. A single net GEX sign or total OI number is insufficient to represent this family.

### Measurements and timing

| Mechanism | Definition and required distinctions |
|---|---|
| Chain/valuation domain | Assemble point-in-time contracts with underlying, style, settlement, multiplier, expiry and listed/quoted/OI support. Separate price/Greek eligibility, flow eligibility and executable quotation. Missing wings or contracts remain explicit. |
| Price, IV and surface | Validate prices and quotes, invert supported bid/ask intervals, fit declared arbitrage-aware shapes and retain uncertainty/extrapolation. Forward/underlier mapping is a dependency where needed; trade-sign work can proceed on valid observations independently of IV. |
| Greeks | Preserve delta, gamma, vega, vanna and charm units, scaling and time/sign convention. Finite-difference checks use the same contract/valuation domain. Do not mix per-volatility-unit and per-percentage-point measures. |
| Reported OI | Keep position date, first availability, report revision and contract lifecycle separately. Define first-report versus revision targets explicitly. An intraday prefix repeated many times does not create independent next-report truth. |
| Holdings scenarios | Keep last-known OI, volume heuristics, model-predicted next-report OI and uncertain current holdings separate. Dealer ownership/sign and the true intraday holdings path are not directly established by an aggregate endpoint report. |
| Exposure boards | Declare signed/gross scenario holdings, multiplier and Greek convention before aggregation. Separate static prior-OI, mechanical repricing, flow/holdings updates, surface change and universe/coverage change. |
| Options flow | Retain contracts, premium and delta/gamma/vega/vanna/charm-weighted signed channels. Event-frozen Greek weights and later revaluation are separate paths. Keep unknown signs, multi-leg ambiguity and grouping uncertainty. |
| Nodes and topology | Extract concentration geometry, width/prominence, stable identity, lifetime, migration, thickening/thinning, corridors, weighted centers and source-pattern structure. Preserve small and large nodes and expiry contributions. |
| Futures options/max pain | Use each futures option's actual underlier/style/settlement. Keep per-expiry settlement-payoff/max-pain calculations as clearly defined observable-holdings benchmarks, without importing a predictive guarantee. |

### Statistical questions

First establish which quotes, reports and source clocks are available and how coverage changes by chain, expiry, moneyness and session. Study OI report changes and revision distributions, conditional on prior OI, activity, listing age and expiry state. Separate newly listed, non-expiring, adjusted and expiring/0DTE populations. Missing terminal reports and contract expiry need explicit outcome treatment rather than automatic negative OI.

For exposure dynamics, freeze the convention and change one driver at a time, then account for interactions using joint scenarios. The sum of attributions must reconcile with the actual board change under the selected decomposition; shared spot/surface/holdings uncertainty cannot be treated as independent simply for convenience. Sensitivity to holdings/sign priors is part of the result. A future scenario board is an observable computed target only under its frozen definition, not observed dealer inventory.

Measure node persistence/migration, first reach, departure/reversal/continuation, node-to-node movement and remaining room. Control distance, width, size, expiry, source age, uncertainty and candidate density. Compare static, mechanically repriced, flow-proxy and learned-OI scenarios on identical covered dates. Direct price/flow-to-path models provide an alternative to inferring an unidentifiable latent holdings path.

Analyze flow breadth/concentration and OI-relative activity with explicit denominators; unstable tiny/missing OI must not create artificial extreme signals. Separate net/gross and signed/magnitude channels. Test all retained Greek-weighted CVD paths and their event-frozen versus repriced alternatives, rather than only delta flow. Multi-leg/sweep labels describe observed grouping evidence and uncertainty, not identified trader intent.

### Models and comparisons

| Question | Baseline and justified challengers | Individual evidence |
|---|---|---|
| Next reported OI | Persistence; fixed-volume-fraction proxy; regularized/hierarchical count or signed-change model; supported boosted/sequence challenger | Held-out report/count/change accuracy, predictive interval calibration, expiry/listing cohorts and independent report support |
| Current aggregate holdings | Frozen OI and volume scenarios; constrained filtering/assimilation; conditional opening-fraction model only with declared uncertainty | Endpoint consistency and prior sensitivity; no claim of intraday truth from endpoint supervision alone |
| Exposure information | Static OI board; mechanical repricing; flow and learned-update scenarios; direct observable-input path model | Increment beyond price/volatility and static exposures, convention/coverage sensitivity and conditional Location quality |
| Node behavior | Geometry/age/distance frequencies; migration/persistence/duration model; compact spatial or sequence challenger | Node identity fidelity, persistence/movement scores, reach/ordered-reaction calibration and effective episode support |
| Strike/expiry representation | Transparent pooled summaries; preserved strike/expiry features; set/graph/temporal challenger on the same information | Predictive increment, uncertainty and compute cost, including small-node and sparse-expiry cases |
| Flow/multi-leg information | Contracts/premium and simple sign baseline; Greek-weighted/breadth features; uncertain-grouping challenger | Same-date path/node increment, unknown-sign robustness and sensitivity to grouping errors |

Keep OI endpoint accuracy separate from improvement in an exposure board and from improvement in price/path/Location forecasts. A good next-report model may add no useful current context; a static board may remain better supported. No empirical OI or GEX result is assumed because the formula has been implemented.

### Fixtures and failure checks

Check style/settlement/underlier identity, multipliers and Greek scales; same-day AM/PM expiries; stale/crossed quotes and inversion domains; sparse/missing wings; unknown trade signs; corrected/duplicated prints; report publication after position date; revised reports; expiry without a next report; duplicate OI assimilation; contract-universe changes; mechanical-versus-flow reconciliation; node split/merge identity; zero signed center denominator; and missing source-to-receiver mapping. Verify finite differences and explicit payoff examples before scoring inferred features. Preserve unavailable proprietary formulas as dependencies rather than inventing their numbers.

### Evidence and outputs

Deliver a complete options/OI/Greek-flow/exposure/node statistics and timing report; independently scored report-OI, node and observable path specialists; scenario-aware Context with support/uncertainty; and evaluated small/large node, center/band and corridor Locations. Each chain and futures-options branch receives actual coverage evidence and a tested or exact blocked disposition. None is silently represented by the most convenient chain.

## 6. Cross-market context, events and regimes

Retained core: X01–X10 and all children, C17/C20/C22, with links to the relevant range, flow, volatility and options outputs. Information from a source asset can matter without the receiver touching a corresponding local level.

### Measurements and timing

| Mechanism | Definition and required distinctions |
|---|---|
| Asynchronous alignment | Align by information actually available at the receiver cut. Retain source/receiver calendars, quote age, publication lag, missing masks and update frequency. A later source timestamp cannot be backfilled into an earlier decision. |
| Coordinate mapping | Separate contemporaneous price/forward/basis conversion from predictive transmission. Keep absolute/normalized coordinates, contract units, residual uncertainty and known-at time. Cash-index daily values cannot certify intraday touches. |
| Nasdaq/S&P chains | Compare NDX/NDXP/QQQ and SPX/SPXW/SPY individually and in combinations on matched support. Preserve source-only cross-family effects, including S&P information for an NQ receiver. |
| Relative strength/SMT | Preserve price and flow SMT, divergence, lead/lag and common-driver residuals. Source clocks, causal swing anchors and receiver differences remain explicit. |
| Broader markets | Retain supported YM/RTY, NKD/FX, HG/FX, SI, rates, GC/USD and other acquired global futures/currency/commodity inputs with their own calendars and normalization. |
| Events and slow context | Distinguish scheduled known announcements, observed releases/surprises and later revisions; ETF/constituent/earnings context; COT, SHFE inventories and SLV/fund-flow information. Position date is not necessarily publication time. |
| Regimes and origination | Regime state and distribution shift are inferred from the observed prefix. Keep Context-originated opportunities and support/missingness conditions; a hidden-state smoother using the full sequence is unavailable online. |

### Statistical questions

Measure mapping error and its conditional variation separately from whether source changes predict receiver outcomes. Compare source-event timing, receiver reaction delay, common-driver effects and persistence by session overlap, volatility and coverage. A direct cross-source event may create an opportunity without a local node; include all eligible source events, failed transmissions and no receiver reaction.

Compare the Nasdaq chains, S&P chains, their combinations and futures-only baselines on identical supported dates, with mapping and quote/OI coverage uncertainty held visible. Compare observed pointwise summaries with joint strike/expiry/chain/asset/time information. A richer representation does not establish a cross-market effect unless an input-matched comparison supports it.

Study event-before/event-after behavior using what was actually known at each cut. If historical release vintages or surprise expectations are absent, isolate the supported scheduled-event study and record the unavailable surprise/revision question. Handle TRF/constituent print completeness, delayed reports and corrections explicitly; a selected print screenshot is insufficient coverage. Older slow-context dates cannot enter the primary cohort merely because that source is longer.

### Models and comparisons

| Question | Baseline and justified challengers | Individual evidence |
|---|---|---|
| Mapping/basis | Fixed qualified relation and causal rolling estimate; regularized conditional mapping | Held-out coordinate error/intervals and stability by age/session; distinct from transmission scores |
| Source-to-receiver response | Receiver price/time baseline and simple source-return/event rule; conditional lag/duration model; compact cross-source challenger | Proper/path scores, causal lag stability, time-placebo/common-driver controls and no-local-touch cases |
| Multi-chain information | Futures-only, each chain alone and transparent combinations; information-matched pooled/set/graph model | Same-cohort incremental score, mask sensitivity, node/path calibration and compute cost |
| Relative flow/strength | Own-market baseline; price SMT, flow SMT and residualized cross-inputs separately; justified joint interaction | Independent date support, overlap effects and increment beyond common market movement |
| Events/regimes | Session/seasonal baseline and known calendar state; observed-release or filtered regime model; supported nonlinear challenger | Pre/post-event and regime-conditional score/calibration, causal availability and shift robustness |

Keep a model's source sensitivity or attention weights separate from a causal influence claim. Train lag selection, mapping parameters, residualization and regime classification only on permissible data. An input family that helps only in a prespecified interaction receives that joint test; an unsupported post-hoc story is exploratory.

### Fixtures and failure checks

Check reversed update order, unequal holidays/timezones, stale source values, first available macro release, revised calendars, unavailable historical constituents, wrong strike/forward mapping, roll-coordinate jumps, mismatched quote/OI ages, source event without receiver touch, delayed/failed transmission, and future-informed regime smoothing. Every optional feed disables only its affected comparison. Do not manufacture intraday index paths, complete prints or publication vintages from daily data.

### Evidence and outputs

Deliver cross-market/event/regime statistics and timing results, independently scored mapping/transmission/context models, and evaluated source-originated receiver opportunities. Preserve each retained chain and broader-market/slow-data child in the coverage report, including precise missing-data dependencies. The output includes what the source adds beyond the receiver's own information and where that conclusion is supported.

## 7. Location generation, conditional quality and lifecycle

Retained core: all L01–L19 and their children; G04/G05, research aspects of G07/G08, and compatible G01/G03/G09 support. This section integrates the complete Location catalogue; upstream families still produce their own independently tested Context and candidate geometry.

### Measurements and timing

Every candidate records its family, source/ancestor identity, raw receiver coordinate, center/bounds/width, formation and first available time, candidate-definition version, context cut, horizon, revision/invalidation state and eligibility. Preserve geometric relations without merging independent origins or counting common ancestry as independent confluence. A forecast-conditioned location uses only available or legitimate out-of-fold upstream predictions.

| Families | Required retained geometry and roles |
|---|---|
| L01–L04 | Range quarters/EQ/open, edges and edge-relative extensions, prior-RTH/full-session structures, statistical/P-zone bounds. Preserve internal continuation and reversal as distinct outcomes. |
| L05–L07 | Volume shelves/nodes/valleys, side/delta concentrations, TPO/initial-balance/single-print/tail structures, with actual formation anchors and grid definitions. |
| L08–L10 | Causally confirmed swings/retracements/dynamic ranges, different FVG/imbalance/displacement geometries, order-block versus rejection-block regions and confirmation times. |
| L11–L12 | VWAP and anchored dispersion, period/session opens, settlements, gaps and supported special prints. Moving geometry and original fixed geometry have distinct labels. |
| L13–L15 | Small and large options nodes, exposure centers/bands/corridors, and source-event opportunities without a receiver touch or matching local node. |
| L16–L19 | Bounded learned proposals/refinements, lifetime/retest/invalidation rules, candidate-set ancestry/dependence, and large-print/origin/aggression-memory locations. |

### Statistical questions

For fixed candidate geometry and horizon, measure probability/time of reach; at a separately identified contact, measure ordered favorable/adverse departure, bounce/retrace/continuation/traversal, excursion tails and occupied duration. Preserve no-contact and censoring. Report forecast at the original cut separately from a model updated at actual arrival; future arrival features cannot enter a pre-touch forecast.

Compare width, quantile, offset, snapping, smoothing and lifetime choices on development dates with a controlled candidate budget. A wider region or more numerous objects can increase apparent success mechanically. Match distance, width, count, time, age and source uncertainty in placebo and comparator sets. Preserve a candidate's initial failure even if it is later revised or retired.

Evaluate first and later visits, time away, accumulated pressure, novelty and observed invalidation. Repeated flicker is not automatically an independent retest. Compare original source delete-on-sweep/one-retest rules with supported lifetime models; no future survival status may determine current eligibility. For source-only opportunities, use an explicit receiver event/time origin without fabricating a local touch.

### Models and comparisons

| Question | Baseline and justified challengers | Individual evidence |
|---|---|---|
| Candidate generator | Exact disclosed source geometry, simple grid/nearest existing level; train-only width/offset or profile-based refinement; bounded learned proposal when supported | Quality at fixed scorer, count/width/distance controls, failed/no-contact population and creation delay |
| Reach and arrival | Distance/time/volatility frequencies; discrete-time duration/first-passage model; compatible joint path challenger | Horizon-aware calibration, duration and censoring-aware scores, ambiguity support |
| Conditional departure/runner | Source role frequencies; conditional excursion/ordered-path/duration model; supported nonlinear challenger | Continuation/reversal/traversal score, runner duration, adverse tails and remaining-room calibration |
| Retest/lifetime | Fixed source retirement and age rules; pooled visit hazards; conditional recurrent-event/lifetime model | Held-out survival/retest quality, retained historical failures and support across repeated visits |
| Candidate comparison | Transparent research quality ranking; calibrated target-compatible scorer; justified ancestry-aware combination | Same-candidate improvement, redundancy and subgroup reliability; full account-state action selection remains later |

Evaluate a better scorer on the same candidates and a better generator with the same scorer before assessing their joint change. Distinguish a simple raw probability or conditional excursion estimate from an executable action-value model. Waiting for a deeper location or more information can be studied through reach, delay, changed information and remaining movement; complete act/wait/entry/exit policy value is a later trading experiment.

### Fixtures and failure checks

Check body/range and edge/coordinate distinctions; source publication after touch; unfinished anchors; width/tick boundaries; equal/simultaneous contact; ambiguous within-bar order; gap-through with unknown crossing details; no-contact versus missing future observations; fixed versus moving barriers; revisions and split/merge ancestry; duplicate source evidence; rejected candidates; repeated-visit grouping; and model predictions unavailable at object creation. Do not select locations using future HOD/LOD or successful examples. A quantile location is not inherently a reversal node.

### Evidence and outputs

Deliver the complete candidate/outcome table and a Location-quality report with generator, scorer and Context contributions separated. Every intended Location family receives actual tested coverage or an exact dependency. Outputs include calibrated reach/path/room/lifetime where supported, clearly stated failure/uncertainty regimes and recommended research variants. Context and Locations may originate opportunities; universal confluence and compulsory Response confirmation are not eligibility rules.

## Common delivery format and retained detail

Each family report uses the same compact format: question and definitions; actual cohort/coverage; named comparisons; statistical/timing findings; individual Context/model results; Location results where applicable; selected/rejected/inconclusive/dependency disposition with exact evidence. One family report can contain many independently scored targets. Shared source passages, kernels and checks are referenced once where their definitions match.

The [catalogue](UNIT_CATALOG.md) and [scope map](scope_map.json) retain all 153 parent and 191 refinement IDs, with links to the full original definitions, specific cases and improvement constructions. Supporting F/V requirements remain shared data/evaluation work. P and complete R trading-policy work remains later; observable discretionary-pattern measurements relevant to the three current deliverables remain active as described above. The archive is a reference library, and its eight-phase rows are not the current work queue.
