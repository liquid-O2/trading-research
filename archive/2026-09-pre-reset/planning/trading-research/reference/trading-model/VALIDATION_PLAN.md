# Validation designed before implementation

Status: **protocol specified; proposed trading-system tests have not been run**. The completed evidence consists of the supplied-source review, public-document research, archive reconciliation and bounded data audits described in their ledgers. No backtest, trained expert, live/shadow strategy or profitability result is claimed.

All component cards incorporate CC-07 and own `T-<ID>-UNIT/PROP/SYN/INT/PRED/ECON/ABL` as applicable. Deterministic services do not need meaningless prediction tests; they need exact semantic and fault invariants. A predictive specialist needs proper-score/calibration evidence. An actionable component additionally needs complete sequential economic evidence. The test registry must state each applicability decision rather than silently omit a test type.

The [344-unit experiment program](SPECIALIST_EXPERIMENT_PROGRAM.md) elaborates every parent and named refinement into P0–P7 with local fixtures, targets, challengers and metrics. The [quality framework](MODEL_QUALITY_AND_STOPPING_RULES.md) adds input-lineage checks, controlled positive/null tests, learning curves, interaction-only contributor tests and correctly scoped oracle diagnostics. These are proposed implementation tests; the finite review examples and bounded VIX audit have separate evidence labels.

The [153 upgrade paths and 191 specific child instructions](UPGRADE_PATHS.md) and [shared constructions](UPGRADE_CONSTRUCTIONS.md) add binding comparisons to those same units. Preserve each original/corrected/prior-upgraded/further-candidate variant and all source exceptions. Register new target/port/fit dependencies before code; test information, representation and model changes separately. Location comparisons control width/count/delay, policy comparisons use full common-boundary trajectories, and engineering improvements retain exact semantic/action parity. Reconcile every exact scope ID, child and required phase with an evidence-backed disposition; one successful representative does not complete a family.

## 1. Evidence gates and stopping rules

| Gate | Required evidence | No-go / inconclusive condition |
|---|---|---|
| V0 specification | Inputs, units, time/coverage, algorithm, outputs, baseline, labels, tests and disposition complete; source ambiguities encoded as variants/dependencies | Engineer must invent a major mechanism, hidden formula or unsupported input |
| V1 data and semantics | Reconciled partitions, instrument/side/price units, clock/availability, exact deterministic fixtures and independent reference calculations | Unresolved critical sign/scale/time error, future-derived feature, unsafe executable quote or position state |
| V2 prediction | Nested chronological comparison on identical eligible observations; proper score, calibration, applicability and dependence-aware uncertainty; logged search history | Apparent gain comes from changed sample/coverage, leakage or test-driven tuning; insufficient effective data yields inconclusive |
| V3 integrated economics | Full one-mini sequential policy with rejected candidates/non-fills, realistic costs, daily/account/boundary risk; simpler complete competitors; paired ablations | Advantage disappears under plausible conservative fills/costs, unauthorized exposure, account-rule failure or no positive net evidence |
| V4 frozen shadow and operations | Untouched future period, frozen promotion/stop rules, actual receipt telemetry, parity/restart/reconciliation/fault evidence; live market observations without unauthorized trades | Changed model on same future test, unexplained parity divergence, unresolved active-account terms, unverified passive fill assumption or unsafe outage response |
| V5 later deployment decision | Separately authorized execution, chosen product/contract/rules, approved data permissions and resource budget, documented risk/operational acceptance | This plan grants no deployment/trading/purchase authorization; any critical defect remains unresolved |

There are two separate economic questions. **Incremental research value** asks whether a component improves the incumbent's net/risk tradeoff under a frozen materially useful margin. **Primary feasibility** asks whether the complete selected one-account/one-mini policy supports at least $2,000 mean daily net over all eligible days while respecting the daily loss objective and actual account constraints. A component can earn research integration even when the whole system has not met the target; report that gap explicitly. Exact services are judged on invariants/risk roles, and a prespecified interaction-only contributor may qualify through a neither/A/B/A+B held-out comparison. Standalone predictive superiority is not a universal gate, while semantic/causal integrity remains mandatory.

Recommended confirmatory convention: a one-sided 95% dependence-aware lower confidence bound on mean daily trading net must exceed $2,000 before labeling that numerical objective statistically supported under the tested assumptions. This is a proposed evidence threshold, not a user requirement or guarantee. A point estimate above $2,000 with a bound below it is **inconclusive**, not success. Report two-sided intervals and the full daily distribution as well. If the user chooses withdrawable business cash as the primary net definition, run the same declared objective on P11's cash ledger with its longer timing horizon. Report both ledgers throughout.

For daily loss, require zero unauthorized **planned** risk-budget violations and report realized overshoots due to gaps/latency/outages, their magnitude, frequency and uncertainty. A finite sample with no overshoot does not prove a hard future loss bound. The acceptability of residual tail risk is an explicit later deployment decision; do not silently reinterpret $1,000 as a trailing peak-to-trough limit or promise that stops guarantee it.

Stop or downgrade a research branch when a critical causal/semantic defect is found, its registered compute/search budget is exhausted without useful evidence, learning curves show unsupported complexity, or conservative economics repeatedly fail its frozen useful-effect criterion. Keep the failed experiment and reason. Do not continue parameter search until a desired answer appears. Safety incidents can halt shadow/operations at any time; they cannot justify erasing unfavorable days or restarting a favorable test clock.

## 2. Data, time and instrument fixtures

Implement small hand-checkable fixtures before large scans. Preserve known observed archive anomalies as regression inputs without publishing sensitive credentials or altering raw files.

| Test family | Concrete fixtures and invariant | Owning components |
|---|---|---|
| T-DATA schema/scale | DBN fixed-point 1e-9 prices, option multiplier/tick sentinels, null versus integer missing sentinel, negative spread-stat price versus invalid negative outright quote, empty RTY partition | F01/02/06, O01/02/19 |
| T-DATA trade side | Databento trade B=buyer/A=seller, N unknown, passive action semantics distinct; same-size/time genuine repeated trades not blindly deduplicated | F05, M01/02/09, O03/15 |
| T-DATA quality | Crossed opening auction versus continuous market; locked/zero quotes; archive future-paired option quote; four-hour stale paired quote; unknown receipt time; provider clock skew | F04/06/07, O02/03, P05 |
| T-DATA stream | Reconcile MBP action-T and standalone trades by instrument/time/price/size/side/flags with multiplicity; duplicate corrections and late events; broaden audited two hours before treating early NQ reconstruction as certified | F05/06, M01/02, V06 |
| T-MBP semantics | Preserve every supplied field; native enum/character parity; T without F_LAST; bitwise flags 132/168; snapshot versus new activity; publisher-specific flags; gap/book recovery versus lost flow history; pre-trade quote and subsequent update without double depletion | F01.DECODER, F05.CROSS_VENDOR, F06.GAP_RECOVERY, M09.RECOVERY, P05.CLOCKS; MARKET_DATA_SOURCE_CONTRACT |
| T-TIME calendar | NY spring/fall DST, ambiguous/nonexistent local times, cross-midnight 18:00 session, 06–09 versus 09–12 versus 09:30 RTH, half-day and broker-specific earlier boundary | F03, C01/21, P08–10 |
| T-TIME bar availability | Incomplete 5/15-minute/HTF bar requested at opening; pivot requiring right bars; final candle body/wick; gap over missing session-end bar | F04/09, M08/13, C01/02, R07/18/20 |
| T-ROLL | Actual contract switch, split signal/execute symbols, prior absolute levels translated or invalidated under recorded rule, roll gaps not returns, option contract aliases/UDS spreads | F02/08, M12, O19, P12 |
| T-UNIVERSE | Contract known then versus full-day traded list; expired/missing report versus zero OI; American/European settlement, AM/PM expiry, corporate action and PIT membership | F02/07/08, O01/06/19, X08 |
| T-DATA TRF / T-PRINT | Late/corrected/cancelled off-exchange print; missing receipt; same-price cluster revision; capped/full-day largest-print leakage; no side/BBO; shares/notional units; mapped-source uncertainty and matched reference-price placebos | F04/05/12, X08.TRF, L12.PRINT |
| T-ASOF | Latest available report ≤ decision cut; nearest snapshot that lies in future rejected; receipt/publication delays, OI effective date versus report date, macro revised value unavailable earlier | F04/07, O06/08, C17, X10 |
| T-GAP | Missing whole ES months, NQ standalone trades pre-2021 absent but MBP potential, sparse monthly index chains versus outage, coverage mask changing during day | F06/07, O21, G09, P10 |

Chain quality testing must reconcile listed eligible contracts, OI-covered contracts and valid as-of quotes by chain/expiry/moneyness at the same cut. Report count-weighted and OI-weighted fractions; neither certifies dealer exposure coverage. Full-chain OI with restricted strike quotes does not justify imputing a complete intraday surface with zero uncertainty. Audit join error by contract key rather than merely matching underlying/date.

Trade-sign fixtures preserve unknowns. Options trade classification must use a legitimately prior quote, quote-age/condition rules and uncertainty, not today's later quote or a vendor “next IV” field. Multi-leg/sweep grouping known only after its grouping window gets that later availability. Size cohorts are print-size proxies; tests must ensure the total of cohort signed contract flow reconciles to known-side ordinary CVD when cohorts partition all sizes, while unknown-side volume remains separately accounted.

## 3. Causality and replay invariant

`T-CAUSAL` is a property test over many decision prefixes: remove or perturb **all** events, versions, labels and model artifacts available only after t; replay; require identical t-time inputs, object versions, forecasts, candidate set, risk state and decision hashes. Just checking a model feature column for obvious future names is insufficient.

Apply explicitly to:

- Swing right-side confirmation; bar high/low/close; current candle body/wick classification; within-bar cohort CVD highs/lows; event-order ambiguity.
- Fixed versus developing profiles, source/chart viewport anchors, retrospective dealing-range choice, adaptive window/cluster discovery, current-inclusive statistics and level revisions.
- OI next-report labels, report revisions, expiry disappearance, daily IV/contract-traded lists, nearest future board snapshots, current-day baseline percentiles and later multi-leg classification.
- Macro/earnings schedules and release vintages, current constituent weights, equity adjustments, settlement publication, futures roll selection and synthetic mapping calibration.
- Normalization, feature selection, models, calibrators, gates, selected instrument, stop/target policy and retraining schedule.

`T-RESTART/T-OOF` adds uninterrupted versus checkpoint replay; duplicate/late/revised events; lost acknowledgements; source timestamp collisions with admissible order permutations; nested OOF regeneration and prohibition on replacing downstream training inputs with in-sample fitted upstream predictions. A deterministic tolerance must reflect source units/solver accuracy, not be widened to conceal a changed decision. Where missing receive times make exact historical ordering unknowable, report results under declared arrival scenarios and label that cohort approximate.

## 4. Mechanism and model fixtures

| Family | Required discriminating synthetic cases | Tests/components |
|---|---|---|
| Jumbo path | Same eventual range but opposite break order; no break; extended single break/internal EQ; compressed single break/internal entry then extensions; double break; pre-existing overnight sweep; 10:00 delayed turn; prior-RTH target unchanged by source-specific ETH sweep | T-JUMBO, C01–06/21, L01–04, R18 |
| Statistical range | Range multiple versus return SD versus pooled displacement SD; current sample excluded/included deliberately; maturity denominator; gap crossing versus touch; mean versus median; asymmetric conditional excursions and incomplete sessions | T-RANGE, C06/09–14, L04, PIN benchmarks |
| Profiles | Real trade-at-price versus bar-range allocation; zero-range bar volume; POC ties; disconnected VA/two empty bins; local small node beside dominant node; 40/68/70% value; causal calendar/leg/range anchors; weekly signed profile versus yearly volume profile | T-PROFILE, M04–06, L05–07/19, R16 |
| CVD/SMT | Same close but different within-bar cohort extrema; cohort partition reconciliation; session reset; scale-sensitive divergence; true source-level touch with no receiver touch; asynchronous asset peaks | T-CVD, M01–03, X07, O15/16, R10 |
| Options/OI | Frozen OI mechanical price/IV/time change; actual report change; unobserved opening/closing combinations giving same tape; 0DTE expiry censoring; restricted strikes; stale/future quote; surface wing uncertainty; UDS option spreads | T-OPTIONS, O01–23 |
| Exposure nodes | Stable node thickens mechanically; genuine model holdings update with uncertainty; split/merge/migration identity; center weight by magnitude; upper/lower split at center; threshold fraction of king versus percentile; unavailable node not zero | T-NODES, O09–14/17/22, L13/14 |
| Mapping/transmission | NDX option strike to NQ with uncertain intraday cash proxy; ETF basis change; SPX source reaction before NQ response without local QQQ node; stale source “leads” from timestamp error; common market driver | T-CROSS, X01–07, L15 |
| Selection | Nearby modest value now versus unreachable deeper high payoff; correlated co-located objects; no independent confirmations; target room exhausted by wait; missing expert; failed calibration and abstention | T-SELECT, G01–09, L18, P01/02 |
| Response later | Quiet failure versus high-effort stall; no-retest continuation; failed squeeze then same-direction resqueeze; protected low later fails; second retest selection; ambiguous three ticks; footprint ratio arithmetic and body-close delay | T-RESPONSE, R01–22 |

Mathematical fixtures include Greek signs/units against finite differences, IV solver repricing residuals within declared price precision, surface arbitrage constraints within supported domains, gamma-weighted flow versus mechanically repriced exposure, and independently recomputed weighted center/profile/CVD values. Statistical forecasts must be compared on a common target: historical variance estimators are measurements, forward variance is a forecast, excursion is a path distribution, and touch/conditional reversal/action value are different labels.

## 5. Chronological experimental design

Use the data-capability cohorts rather than pretending every family spans the entire archive. Proposed starting outer schedule for long futures cohorts: expanding or rolling training ending before each six-month test block from 2022 onward, with inner chronological tuning/calibration. For options common-cohort experiments, choose start dates only after chain/quote quality gates establish support. Compare 12/24/36-month training windows in development if sample sufficiency allows. These are initial protocol candidates, not fixed empirical optima; freeze the selected schedule before reporting confirmatory outer results.

All already inspected historical periods are development/retrospective evidence, including the recent September 2026 archive. Do not relabel a recent known dataset as “untouched future.” A genuine shadow interval begins only after the pipeline/model/policy and stopping rules are frozen, on a prospectively recorded future eligible date. Baseline: choose the final observation count and end rule before launch using development precision/power calculations; 60 eligible days is a planning starting point, not an adequacy claim. Evaluate once at that fixed endpoint, and report inconclusive if uncertainty or regime coverage is inadequate. Extending until an ordinary 95% interval clears a target changes its inferential properties even if the extension criterion was written down. A sequential alternative needs a prespecified group-sequential or time-uniform procedure with explicit estimand, tail/dependence assumptions and error allocation; no generic confidence-sequence guarantee is asserted for heavy-tailed trading P&L. Longer business-cash evaluation is a separately planned cohort. Risk halts remain allowed at any time and retain the complete record. See [third-review research](THIRD_REVIEW_RESEARCH.md).

Nested procedure:

1. Freeze eligible dates, data quality masks, target/observation process and baseline policies. Group all same-date related assets/contracts, objects and opportunities together.
2. Construct interval dependencies including label horizons, OI report maturity and state carryover. Purge overlaps with evaluation cuts; justify any embargo by those spans and measured dependence. Keep legitimate past-history features available.
3. Fit transformations/discovery/upstream experts in inner training; generate chronological OOF predictions. Fit downstream experts/gates on those outputs, then calibrate on separate chronological predictions. Recompute this chain for each outer fold.
4. Select model/hyperparameters/policy with inner validation only, including instrument selection, node/window discovery, fill scenarios and exit policy. Record all attempts in V03.
5. Evaluate outer block once for the frozen chain. Report common-cohort fair comparisons plus clearly separate expanded-coverage opportunity value.
6. After development decisions, freeze final future/shadow plan and versions. Any substantive change starts a new experiment; the previous future record remains visible.

No shuffled train/test split, reverse split, random touch-level cross-validation or future-trained fold demonstrates deployable forward performance. Same-day cross-asset samples are dependent even if asset symbols differ. Sample sufficiency is assessed by effective date/block count, learning curves, label prevalence, interval width and minimum useful effect. Sparse chain/expiry/regime cohorts receive shrinkage or an unsupported designation.

## 6. Metrics, uncertainty and multiple testing

Prediction: log/Brier score and reliability for binary/multiclass outcomes; pinball/CRPS and coverage/width for distributions; QLIKE and robust scale error for variance; MAE/deviance for OI counts; cumulative-incidence calibration for competing event times. Report conditional metrics by year/session/volatility/event/chain/expiry/coverage and source age. Exclude censored examples only under declared survival/label rules, not because their results are inconvenient.

Decision: candidate recall/coverage, reachable versus unreachable proposals, selected versus rejected predicted value, calibration among selected and all candidates, abstention rate, wait cost, source-event transmission delay, price/room at confirmation and rank sensitivity. A ranker's AUC is not a level generator's opportunity quality.

Economics: all-eligible-day mean/median/quantiles, net and gross P&L, zero-trade rate, trade count distribution, daily loss overshoot, maximum observed and expected-shortfall-like tail measures with uncertainty, account-floor breaches, time-to-payout/actual cash, fees/slippage, fill/non-fill rates, duration, all-trade MFE/MAE/giveback, turnover and concentration of profits. Report dollars for one actual mini, not only R, normalized return, copied totals or points.

Use paired date/block bootstrap or other dependence-aware intervals over complete daily/weekly paths; choose block-length sensitivity in development based on serial dependence and overlapping horizons. Preserve within-day event/position sequence for risk/account simulation. Resampling terminal daily P&L alone cannot establish intraday trailing-floor survival. Evaluate regime and year sensitivity; aggregate positive results cannot conceal a structurally unsupported cohort. Confidence intervals are conditional on the data/model/simulator assumptions and do not cover unidentified queue behavior automatically.

Control search through nested evaluation, registered family-level experiments and held-out confirmation. Record all tried windows/levels/experts/policies, including abandoned versions. Use selection-adjusted diagnostics such as DSR where its assumptions apply; do not treat one adjusted statistic or a pretty stability surface as proof of strategy validity. If many subgroup claims are reported, predeclare family-wise/FDR treatment or label them exploratory; do not pick isolated favorable p-values after searching.

## 7. Fair controls and component ablations

`T-PLACEBO`: generate null locations matched within the **same pre-decision state** on density, distance from current price, width, time/session, side, lifetime, volatility and candidate-generator conditions. Compare randomized position within an admissible band, shifted source timing, matched unrelated levels and price-only controls. Do not shift a source event into the future then use it as available. Rebuild the full causal pipeline for leak controls; shuffling final labels alone may leave upstream leakage intact.

`T-SEARCH/T-SELECT`: compare faithful source formulas, corrected causal versions, simple statistical challengers and learned models on identical opportunity populations. A corrected formula can change candidate count; separately report (a) common opportunity quality and (b) whole-policy generator value with density controls. Preserve rejected/untraded candidates, late confirmations, passive non-fills and source-only events lacking a receiver level.

Required experiments E0–E5 are defined in the master plan. Minimum factorial ablations:

- Jumbo formation window versus path context versus level placement versus ranker; original versus fold-discovered windows and P-zones.
- Futures-only, QQQ, NDX/NDXP, combined Nasdaq, S&P source events and full supported joint boards; same dates/masks first, broader coverage second.
- Frozen OI, mechanical repricing, volume proxy, learned aggregate OI update; surface quality, expiries, chain topology and node migration individually.
- Seasonal range, Parkinson/GK/YZ, ARCH/GARCH and realized/HAR, jumps, IV/skew/term structure, VX/events and calibrated ensemble; variance score and economic use separately.
- Price/profile, volume profile, delta profile, ordinary CVD, cohort close, cohort true OHLC, options contract/premium/delta/gamma/vanna/charm flows, SMT; exact definitions and units preserved.
- Direct C/L, simple price confirmation, each Response prefix, wait/deeper-limit alternatives; entry versus management refinement separately.
- Each common-target expert/gate, missingness treatment, calibration and correlated-object grouping; simpler complete end-to-end competitor on the same information and search budget.

Counterfactual replay remains a simulation: our hypothetical passive order could change queue priority or later market state, and observed-policy data lack support for some alternative actions. Mark such actions unsupported or show bounds. Doubly robust/off-policy methods require defensible propensity/support and outcome assumptions; they cannot recover hidden queue truth merely by being sophisticated.

## 8. Execution, account and failure drills

`T-FILL` uses one-unit event replay with side-correct bid/ask fills, order arrival delay, fee schedule, stop-trigger-versus-fill, conservative passive bounds, slippage/impact stress, adverse selection, cancellations and unknown-order state. With one mini there is no fractional fill/partial exit; simulate broker messages about unknown/partial state conservatively and reconcile before any new order. Avoid double charging spread already embedded in fill price.

`T-ACCOUNT` uses independent hand-calculated intraday paths covering day loss with open liquidation/fees, reserved pending risk, EOD trailing floor updated at the proper time but enforced under actual product rules, withdrawal/floor locks, consistency formulas, activity/news/holding constraints, boundary buffers and trading-date reset. Risk exits cannot be delayed to satisfy a firm's profitable-hold metric. If abstention conflicts with an activity requirement, assess product suitability rather than force a trade.

`T-RESTART/T-SHADOW` injects feed stalls, dropped packets, duplicated corrections, stale options boards, clock offsets, memory/disk exhaustion, model timeout, lost broker ack, fill during cancel, OCO race, rejected flatten, restart at cutoff and account mismatch. Verify fallback semantics: unavailable expert is masked; critical market/position state prevents entries; valid protection/reconciliation/flatten paths remain independent of learned gates.

Attribution follows V07. Use the first divergent invariant and paired baseline interventions to distinguish wrong data, wrong labels, bad Context forecast, unavailable/irrelevant Location, poor ranking/waiting, delayed Response, fill costs, management, account restriction or distribution shift. Oracle knowledge may diagnose a ceiling but must be labeled impossible information and never reported as deployable results.

## 9. Evidence package required at each milestone

Each milestone delivers code/data/model hashes, exact source and target definitions, fold/coverage/eligible-day counts, registered trials, applicable tests and failures, prediction/calibration tables, complete daily/order/account ledgers, ablations, uncertainty, resource measurements and a promotion/reject/inconclusive decision. Every reported number states whether it is source claim, completed audit observation, simulated result, paper/shadow measurement or live observation. Current deliverables contain source claims and completed bounded audits only.

## Additional fixtures from the second design review

The binding [computation schedule](components/COMPUTATION_SCHEDULE.md) adds `T-DAG`: compile named measurement/forecast/state ports, reject current-batch cycles and verify topological OOF generation. Test the explicitly listed negative and positive graphs. All are proposed implementation tests, not executed strategy tests.

Extend `T-OPTIONS` with gamma versus total delta-dollar derivative, opposite hypothetical hedge sign, spot/future Greek coordinate, vanna/charm IV/time units, strictly positive-spread sign rules, locked-quote unknown status, IV-unidentifiable raw flow, and a Greek snapshot whose event time is after the trade despite arriving before the trade receipt. Extend `T-CVD` with event-frozen versus arrival-repriced weighted paths; extend `T-PROFILE/T-RESPONSE` with quote-size recovery net conservation and double-counted executions. Extend excursion fixtures with all-up/all-down future paths yielding one zero side, and absent future data yielding censoring rather than zero.

`T-MAPPING-UNITS` uses a hypothetical ETF at 500 with receiver future at 20,000 and declared local slope b=40 receiver points per ETF dollar. One 100-share option with delta .5 has D_u=50 USD per ETF dollar; at a receiver point value of $20, exposure is 50/(40×20)=.0625 mini-equivalents. This is an information feature, not an executable fraction. Test the inverse/Jacobian, futures-option own-underlying case, opposite hedge sign, and changing-b terms. `T-ACCOUNT` also verifies N_t plus incremental mark-to-stop risk against B_day+N_t, so marked losses and accrued fees are counted exactly once.

`T-SRC-MAV-05/T-SRC-ALM-03` distinguish established balance A, prior balance B, the specific B-POC versus broader value reference, rejection/acceptance, re-entry and unfinished far-edge traversal. `T-SRC-AM1-08` tests causal opening-type attributes versus their matured labels. `T-O23` verifies exact max-pain payoff/minimizer sets, mixed-settlement/coverage failures and incremental value versus full-node/round-strike controls; it never validates pinning by construction.

## Third-review contracts to test explicitly

| Case | Required invariant and outcome | Owners |
|---|---|---|
| T-CAPABILITY / T-ORDER | Same terminal return and excursions can have opposite barrier order; reject a variance/excursion-only forecast at a trajectory-required port | CC-03/04, C06.JOINT, G04.ORDER |
| T-HORIZON | Pre-contact prediction ends at t+h; a later contact prediction ending at contact+h is a different target; no-contact with full observation differs from censoring | V01, G04/05 |
| T-REWARD | Incremental net rewards telescope; macroaction continuation starts at its actual terminal time/state; fees and complete-trade P&L are charged once | G06/07, P01/11 |
| T-STANDING-QUOTE | Marketable fills use valid standing venue BBO at arrival, including unseen-yet venue updates only in outcome replay; no mandatory wait for a new quote update | P05.CLOCKS, F04 |
| T-OI-ASSIMILATION | O07's flow-conditioned forecast and the same flow are not independent repeated observations; duplicate-evidence input cannot create spurious certainty | O07/08/21 |
| T-GEOMETRY | Physical band, estimation/mapping uncertainty and entry tolerance remain distinct; changing the labeled region creates a new target | O11, L04/13/16, F10 |
| T-VEGA-FLOW | Distinct vega-weighted CVD, USD/unit-IV versus USD/vol-point conversion, event-frozen eligibility, true OHLC and sold-trade sign | O05/16 |
| T-SCHEDULER | Slow optional work cannot block independent risk/boundary handling; expired forecasts retain their original horizon; pre-dispatch state/risk reservation is atomic | F04/11/12, P07/08/10 |
| T-QUALITY | Controlled planted signal recovered; future-only field rejected; information/model/generator/scorer tests separated; approximate oracle never called a proven bound | V02/03/04/07 |
| T-FUTURE-END | Fixed endpoint baseline; any sequential extension requires a valid declared inference method; risk halt retains the full record | V03/04/05 |
