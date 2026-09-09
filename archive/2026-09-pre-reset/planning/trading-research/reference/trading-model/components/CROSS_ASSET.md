# Cross-asset mappings, transmission and joint recognition

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
[Common contracts](COMMON_CONTRACTS.md) apply. Coordinate conversion, correlated movement and incremental predictive transmission are different tasks. None establishes a causal effect of one market on another without additional identification. The execution universe remains one NQ or ES mini; the information universe follows the full acquired catalog.

## X01 — Asynchronous cross-market alignment

1. **Purpose/sources.** Make broad simultaneous analysis time honest; user joint-asset ambition, DA-03/10, SKY replay/derived-board limitations.
2. **Inputs.** F04/F07 price/flow/chain snapshots, event/receipt/publication times and quality. NQ/ES/YM/RTY/NKD/HG/SI tape where available, QQQ/SPY minute bars, daily cash/volatility and other catalog streams at actual cadence.
3. **Definition.** Create decision-time snapshots by backward availability join; retain per-source ages and uncertain ordering. Compare regular decision grids with source-event-triggered grids. A completed ETF minute candle can identify a contact only after its close and cannot establish its exact within-minute order relative to NQ ticks. Missing intraday NDX/SPX cash is not synthesized as an observed index print. Binding local refinement: [SR-X01](../SYSTEM_REFINEMENT.md#sr-x01).
4. **Output.** Aligned masked cross-market state with source freshness and event-time intervals; unsupported synchronization returns unavailable/ambiguous.
5. **Dependencies/use.** F04/07/09; X02–10/C/G. Source events retain the first receiver-actionable known_at.
6. **Comparisons.** Coarse common-minute baseline, event-availability merge, latency-scenario alignment. Statistical lag estimates are downstream; a learned alignment cannot select future data. Binding further upgrade and child comparisons: [UP-X01](../UPGRADE_PATHS.md#up-x01).
7. **Rules.** Same-date grouping across every asset; train-only lag/scaler choices. Carry-forward only within validated source TTL.
8. **Tests.** Delayed ES, missing ETF minute, daily cash before close, two source events in same bar, source update future-nearest match and asynchronous expiry boards.
9. **Acceptance.** Zero future joins; sensitivity to lag/tie uncertainty; no claimed subsecond source edge when data only support minute intervals.
10. **Ablation/fallback/resources.** Coarser grids, extra lag, each source removed; retain independent current sources or abstain. Class A/B sparse aligned state, minute/event cadence.

## X02 — Related-instrument coordinate and sensitivity mapping

1. **Purpose/sources.** Map NDX/NDXP/QQQ levels to NQ and SPX/SPXW/SPY to ES with uncertainty; explicit user requirement, SKY085 derived levels.
2. **Inputs.** X01 aligned related prices and raw eligible O01 bid/ask quotes, F02 multipliers/contract class, as-of carry/dividend/discount/calendar/roll. Cash index intraday prices are absent in audited free data; ETF minute and futures proxies carry explicit age and uncertainty.
3. **Definition.** The bootstrap port compares fixed ratio, causal affine `P_future=a_t+b_t P_source` and filtered basis models using preceding synchronized observations. For eligible European options at one expiry, raw-quote parity estimates forward `F=K+(C−P)/D`, with D the known discount factor and bid/ask interval bounds; neither IV inversion nor an already fitted surface is needed. This estimates a forward, not an observed cash strike touch; converting maturity/spot coordinates needs explicit carry/dividend assumptions and uncertainty. Prior daily cash basis plus ETF proxy is a separate lower-confidence model. Keep Jacobian/residual distribution, map center and both edges, and round only executable orders. Optional valuation-aware refinement is a later distinct or lagged port, never a feedback prerequisite for the same IV inversion. Binding local refinement: [SR-X02](../SYSTEM_REFINEMENT.md#sr-x02).
4. **Output.** Mapped object/scenario band, both Jacobian directions explicitly tagged, residual uncertainty, source-known interval and model version. If `b=∂F_receiver/∂u_source`, then source sensitivity `D_u=∂V_USD/∂u_source` corresponds locally to `N_receiver=D_u/(b*point_value_receiver)` mini-equivalent exposure; its offsetting hedge has opposite sign. b’s units and validity domain are mandatory. Fractional equivalent exposure is a feature, not permission to trade fractional minis.
5. **Dependencies.** X01/F02/08/O01 raw quotes/F11 for bootstrap; no current O02/O04 requirement. O02 IV, O16 sensitivity conversion, L mappings and X03/04 consume bootstrap outputs. Later refinement has a separately compiled dependency path.
6. **Comparisons.** Daily fixed ratio, rolling affine, carry/basis Kalman model and nonlinear mapping only if residual evidence warrants. Cross-index SPX→NQ is not treated as mere coordinate identity; X05 handles transmission. Binding further upgrade and child comparisons: [UP-X02](../UPGRADE_PATHS.md#up-x02).
7. **Training.** Rolling mapping fitted only prior samples; OOF mapping outputs downstream. No future day's best ratio or final close calibration used intraday.
8. **Tests.** Basis drift, ETF dividend/split, roll, stale cash, synthetic-forward spread uncertainty, index/ETF unit mismatch, inverse consistency and negative/zero slope rejection.
9. **Acceptance.** Held-out mapping error/coverage relative to zone width and executable tick size; node effects survive mapping perturbation. Unsupported true source touch labelled proxy/ambiguous.
10. **Ablation/fallback/resources.** Ratio versus affine/basis, direct cash versus proxy, stale age and uncertainty width. No defensible mapping means source-event-only channel or no mapped level. Class B, small state/OLS/Kalman, minute cadence.

## X03 — Nasdaq-chain comparison and NDX hypothesis

1. **Purpose/sources.** Test the user's observation that NDX-derived levels can be more useful for NQ; DRF-U01/07/09, original prompt, DA-05/06.
2. **Inputs.** Separate O-series NDX, NDXP, QQQ and NQ futures-options outputs, X02 maps, NQ path/execution data and coverage. Same-date/expiry/moneyness cohorts; minute/pre-touch/source-event decisions.
3. **Algorithm.** Maintain individual-chain experts and a target-matched combined Nasdaq expert. Compare NDX monthly, NDXP, QQQ and futures-options alone, pairs and full family for `PATH/REACH/DEPART/VALUE`; include no-local-node events and small nodes. Report full supported sample and fixed common-coverage intersection; equalize candidate density and mapping uncertainty in key comparisons. Binding local refinement: [SR-X03](../SYSTEM_REFINEMENT.md#sr-x03).
4. **Output.** Chain-specific and combined forecasts, contribution/coverage diagnostics and instrument-family applicability. User preference remains hypothesis until held-out evidence.
5. **Dependencies.** O22/X01/02/F11; G mixtures and L options/source opportunities.
6. **Comparisons.** Futures-only and QQQ-only, transparent weighted/regularized fusion, set/graph interaction model. Compare information gains separately from model capacity gains. Binding further upgrade and child comparisons: [UP-X03](../UPGRADE_PATHS.md#up-x03).
7. **Training.** Same trading dates grouped, OOF chain predictions; all variants registered/multiplicity-controlled. No selecting NDX-favorable dates or equalizing by dropping its losses.
8. **Tests.** NDX monthly no near expiry, 2026 thinner wings, NDXP0DTE, QQQ absent node, different ATM references, estimated index forward and source-only receiver turn.
9. **Acceptance.** Paired proper-score/net utility and interval comparisons, subgroup consistency and sufficient independent dates; conclusion can be conditional by session/regime/coverage rather than one global winner.
10. **Ablation/fallback/resources.** Every chain/expiry/mapping/OI-update removed; density/coverage-matched nulls. Fall back supported individual/simple combination. Class B/C shared board cache; no duplicate model per contract unless justified.

## X04 — S&P-chain comparison and fair ES alternative

1. **Purpose/sources.** Parallel Nasdaq research for SPX/SPXW/SPY and ES, while respecting ES execution-data gaps; user execution choice, DA-02/06.
2. **Inputs.** O-series SPX/SPXW/SPY/ES futures-options, X02 mappings, common NQ/ES tape dates and same source families. Minute/event decisions.
3. **Algorithm.** Individual and joint S&P common-target experts; compare monthly AM-settled and weekly/PM-settled products explicitly. For execution choice, run identical one-mini economic policy/fees assumptions on common eligible dates with appropriate point values and liquidity; select using development, freeze outer test. Broader NQ history is a separate result. Binding local refinement: [SR-X04](../SYSTEM_REFINEMENT.md#sr-x04).
4. **Output.** S&P family distributions, source-node roles and fair execution-comparison evidence, including data-unavailable dates. No daily hindsight instrument choice.
5. **Dependencies.** O22/X01/02/F11, P execution/risk and V evaluation; X05 source-to-NQ transmission can use these events independently of ES execution.
6. **Comparisons.** SPY-only, SPX/SPXW-only, ES futures-options, transparent combined and nonlinear joint models; same-date NQ/ES end-to-end baseline. Binding further upgrade and child comparisons: [UP-X04](../UPGRADE_PATHS.md#up-x04).
7. **Training.** Purged same-date folds, OOF upstreams, separate clocks/settlement and coverage. Missing ES BBO never replaced by assumed free fill.
8. **Tests.** AM/PM same date, sparse monthly chain, ES2021 missing MBP, source SPX event during valid NQ cohort and point-value normalization.
9. **Acceptance.** Proper forecasts and net/day/account-survival intervals under identical day cohorts; apparent superiority from missing losing dates fails.
10. **Ablation/fallback/resources.** Chain/expiry/local futures data and mapping removed; use supported simple S&P model. Class B/C; reuse common data and policy engine.

## X05 — Source reaction to receiver opportunity transmission

1. **Purpose/sources.** Make SPX/SPY reaction actionable in NQ even without a receiver-level touch; DRF-U09/11, SKY020, JTR/JXA SMT examples.
2. **Inputs.** Source level/contact/reclaim/departure events with known_at, X01 receiver price/flow, C context/remaining room and local-node-presence flag. Directed pairs NQ↔ES and index/ETF family→receiver; only actual/proxy-supported source events.
3. **Definition.** At source event availability, predict receiver return/excursions/feasible payoff over 1/5/15/30min and supported finer horizons. Include elapsed source movement, receiver movement already realized, residual spread/beta and lag. Compare no receiver local node, receiver not yet touched, receiver already reacted and contradictory source events as distinct cohorts. The entry time is after source observation+processing+order latency. Binding local refinement: [SR-X05](../SYSTEM_REFINEMENT.md#sr-x05).
4. **Output.** Directed source-event forecast and C22/L15 opportunity with source/receiver provenance, uncertainty and remaining executable room. Predictive increment is not causal attribution.
5. **Dependencies.** X01–04, O22/C19/M03, G/P. Mapping optional; source event can be meaningful without a mapped receiver price.
6. **Comparisons.** Receiver price/flow/context only; simple lagged source-return/event regression; matched event survival/boosted model; directed temporal/graph expert. Compare event information against contemporaneous common-market movement. Binding further upgrade and child comparisons: [UP-X05](../UPGRADE_PATHS.md#up-x05).
7. **Training.** Same-date grouping, all source events/failed reactions/background controls, OOF upstreams. No sample selected for eventual receiver reversal. Proxy index contacts separated from observed ETF contacts.
8. **Tests.** SPY touch then NQ turn with no NQ node, source signal arrives after receiver move, source fails through level, contradictory SPX/QQQ, stale source and bar-order ambiguity.
9. **Acceptance.** Incremental proper score and executable one-mini net value after conservative lags; lead/lag direction/placebo tests and uncertainty. No-go if effect vanishes at first actionable receiver price.
10. **Ablation/fallback/resources.** Local-node requirement on/off as comparison, source event versus return, source/date/lag placebo, common-shock controls. Missing source returns no transmission forecast. Class B/E, sparse event scoring.

## X06 — Joint multi-chain, multi-asset temporal pattern model

1. **Purpose/sources.** Address the central broad simultaneous pattern-recognition ambition; user prompt/DRF-U05/09, SKY Trinity patterns, TECH-08.
2. **Inputs.** O14 within-chain representations, O11 nodes/O12 histories, C market state, X01 masks/age and directed X05 events. All supported chains plus non-option context assets; no fixed three-board ceiling.
3. **Algorithm.** Hierarchy: contracts/strikes→expiry sets→chain sets→asset-family sets→joint temporal state. Compare pooled calibrated chain forecasts; regularized cross-chain interactions; permutation-invariant set model; graph with economically justified same-underlying/expiry/directed-event edges; sparse attention temporal model. Edge weights learned only from past data; preserve source coordinates/units/masks, not visual dot size. Heads predict receiver `PATH`, object outcomes and optional coherent multi-asset return distribution. Binding local refinement: [SR-X06](../SYSTEM_REFINEMENT.md#sr-x06).
4. **Output.** Common-target forecast distributions, source/edge contribution diagnostics, disagreement and missing-pattern applicability. Related boards are correlated evidence, not three independent confirmations.
5. **Dependencies.** O14/21/22/X01–05/F11; G/L selection. Upstream learned embeddings/predictions must follow OOF or jointly nested training without test leakage.
6. **Comparisons.** Additive summaries, per-chain experts+linear gate, interaction trees, set/graph/attention. Equal information/compute budgets and a simpler end-to-end competitor are mandatory. Binding further upgrade and child comparisons: [UP-X06](../UPGRADE_PATHS.md#up-x06).
7. **Training.** Group same date across assets; temporal masks/purge; prior-only normalization; structured missing-chain dropout matching actual coverage; rare regimes use shared parameters and uncertainty. Node counts cannot encode future universe membership.
8. **Tests.** Permuted input order, missing entire chain, identical aggregate GEX/different spatial pattern, unrelated graph edge, future time token, shared underlying shock and no local node source transmission.
9. **Acceptance.** Learning curves and paired predictive/economic increment beyond additive combination; stability by year/session/coverage/asset and attribution supported by ablation, not attention maps alone.
10. **Ablation/fallback/resources.** Remove each asset/chain/expiry/time/edge family, random compatible graph, summed versus joint boards. Fall back additive available-data ensemble. Class C, compact model first; larger GPU only after measured scaling/value evidence.

## X07 — Relative strength, cross-flow SMT and lead-lag experts

1. **Purpose/sources.** Preserve SMT and trade-level cross-market divergence beyond price correlation; JTR-07/JXA-23, user cohort/SMT clarification, CRL flow ideas.
2. **Inputs.** X01 aligned returns, M03 reference breaches, M01/02 CVD/cohort OHLC and M10 activity across supported futures; QQQ/SPY bars are price/volume proxies without true aggressor CVD.
3. **Definition.** Fit prior rolling beta/residual returns and lagged cross-covariance; encode own-reference breach order, relative excursion, standardized flow imbalance and cohort divergence. Different contract sizes/volumes normalized by prior asset/session scales; absolute NQ/ES CVD counts are not directly comparable. Forecast receiver future path after alignment latency. Binding local refinement: [SR-X07](../SYSTEM_REFINEMENT.md#sr-x07).
4. **Output.** Relative strength/SMT measurement plus target-specific calibrated forecast, lag/timing uncertainty and coverage mask.
5. **Dependencies.** M01–03/08/10/X01/F11; C03/18/X05/G. Confirmed-pivot and running-reference variants remain separate.
6. **Comparisons.** Price ratio/difference and rule SMT; linear VAR/ridge/Granger-style predictive regression; boosted/duration temporal model. Predictive lead-lag does not establish structural causation. Binding further upgrade and child comparisons: [UP-X07](../UPGRADE_PATHS.md#up-x07).
7. **Training.** Lag/normalization fits train-only; same-date grouping and source-specific timing stress. No selecting favorable cross-asset pairs from outer results without counting trials.
8. **Tests.** Asynchronous fake lead, equal close delta/different cohort extrema, source new high receiver no high, opposite beta sign, missing ES cohort and unknown sides.
9. **Acceptance.** Incremental future-path/calibration/net value above receiver-only and price-only SMT, robust to added lag and matched placebo pairs.
10. **Ablation/fallback/resources.** Price versus flow/cohort/OHLC, lag direction, source permutation and normalization. Missing flow keeps price-only expert if validated. Class B/E small directed-pair models; no all-pairs raw-tape explosion.

## X08 — ETF and constituent-event context

1. **Purpose/sources.** Retain supported cash/ETF and mega-cap event information; CRL-10, user broad information universe, DA-10/11; EXT-077/078 retain a separate deferred `X08.TRF` off-exchange-print child.
2. **Inputs.** Acquired QQQ/SPY one-minute OHLCV and daily cash index/ETF prices, corporate actions, timestamp-supported earnings calendar. Individual-constituent intraday tapes/complete historical weights are **not established by this archive**. X08.TRF additionally requires a separately acquired, complete equity TRF print stream with source/receipt times, canonical IDs, corrections, price, shares, venue and currency; it is not established as acquired here.
3. **Definition.** ETF returns/relative volume/gaps and QQQ-versus-SPY breadth proxy; known mega-cap event proximity and aggregate event concentration only with historical availability. True constituent advance/decline/weight contribution is a distinct deferred extension requiring constituent prices and point-in-time membership/weights. Daily index observations available only after their publication/close. X08.TRF keeps shares, price×shares notional and receipt-time intensity separate; correct/cancel by print ID, and compare actual event-time lag with reporting-time information. Reporting through TRF does not identify a dark pool, aggressor side, a parent order or opening inventory. Do not derive signed CVD from the unpaired prints. Large-print thresholds use past/training data; a full-day largest-print list is not a morning feature. Binding local refinement: [SR-X08](../SYSTEM_REFINEMENT.md#sr-x08).
4. **Output.** Supported ETF/event features and calibrated receiver path forecast, with proxy/missing granularity flags; no invented tick aggressor CVD for ETFs. The TRF child emits unsigned, lag/coverage-tagged features and independent 5/15/60-minute receiver-path forecasts; L12.PRINT consumes available print references. Each child is scored separately before optional X06 fusion.
5. **Dependencies.** F07/08/09/C17/X01; C/G/X06. Future breadth extension uses the same contract and explicit new data gate. The TRF child is disabled until F05/F12 certify receipt/correction/pagination and historical coverage; no paid integration is authorized by this specification.
6. **Comparisons.** Futures-only; ETF lag/relative volume linear model; boosted interaction with known events. Broad fundamental valuation/P-E models remain deferred unless timestamped data and an incremental short-horizon hypothesis are supplied. TRF comparisons are no-print context, simple lagged notional/intensity regression, then regularized tabular interactions; any learned print grouping is a separate trial without asserted common identity. Binding further upgrade and child comparisons: [UP-X08](../UPGRADE_PATHS.md#up-x08).
7. **Training.** Bar-close availability, prior seasonal volume and corporate-action versions; no revised earnings surprise or current constituent list as historical input. TRF thresholds/normalization fit only past eligible prints; label horizons start after receipt and compute latency. Include delayed/corrected prints and unselected candidates, not only the endpoint’s capped winners.
8. **Tests.** ETF split/dividend, partial minute, daily index preclose leak, future earnings value, missing weight and ETF volume-direction proxy mistaken for traded CVD; TRF late reporting, duplicate/cancel, full-day top-list leakage, no side/BBO, truncated pagination and notional-unit fixtures.
9. **Acceptance.** Proper score/economic increment over futures-only on common dates; event and non-event cohorts, and lost opportunities due coarse timing. TRF needs its own common-date incremental score/economics and delay sensitivity, with complete raw coverage certified before interpreting absence as zero activity.
10. **Ablation/fallback/resources.** Each ETF, price/volume/events, adjusted/raw mapping and delayed close. Fall back futures-only. Class B; modest minute tables, no new acquisition implicit. Ablate TRF separately by receipt lag, size threshold, venue grouping and price-reference versus contextual information; the supported core falls back without TRF.

## X09 — Global futures, currency and commodity transmission

1. **Purpose/sources.** Investigate supported broader markets without assuming their usefulness; original universe request, inventory cross-asset acquisitions, CRL-10.
2. **Inputs.** Actual NKD/HG/SI trades/MBP where available, YM/RTY trade/bar data, acquired Nikkei/USDJPY, copper/USDCNY/rates and commodity daily context at recorded granularity. Separate named child experts `X09.NKD_FX`, `X09.HG_FX`, `X09.SI`, `X09.YM_RTY`, `X09.RATES`; each inherits this ten-part contract and keeps separate metrics.
3. **Definition.** Per child, compute causal returns/volatility/relative activity, session-open and spread/basis proxies with currency/unit conversions; predict NQ/ES future path/tails at compatible horizons. Use directed lagged effects and known common-event controls, not an unexplained global risk-on score. Slower inputs condition sessions/days and cannot certify subsecond transmission. Binding local refinement: [SR-X09](../SYSTEM_REFINEMENT.md#sr-x09).
4. **Output.** Child common-target distributions, native-unit features, update age and applicability; X06 may combine them after independent scoring.
5. **Dependencies.** F02–09/M/X01/F11 and primitive C measurement/forecast ports only; no current X06 feedback. Child inputs and deferred publication conditions are binding in the table below. Their independently scored forecasts can feed later X06/G01; measurement ports can condition primitive C without a forecast cycle.
6. **Comparisons.** Receiver-only; single-source linear lag model; shrinkage multivariate regression; boosted/temporal child specialist. Retain only incremental supported sources, with broad initial universe and explicit exclusions. Binding further upgrade and child comparisons: [UP-X09](../UPGRADE_PATHS.md#up-x09).
7. **Training.** Same-date global-event blocks, timezone/holiday alignment, FX quote availability and train-only pair/lag selection. Sparse source history gets separate cohort.
8. **Tests.** Japan/US holiday mismatch, BOJ/FOMC event, currency conversion sign, delayed daily rates, commodity roll and stable NQ with source-only shock.
9. **Acceptance.** Child predictive/calibration and sequential economic/tail-risk increment with multiplicity control; missing child cannot be hidden inside joint model average.
10. **Ablation/fallback/resources.** Every child/source/FX adjustment/lag, random matched market; fall back receiver-only. Class B/E using aggregates first, existing tape features reused.

The X09 child contracts additionally fix these distinct units and limits. Each child retains its own common-target model, ten-part parent contract, validation and resource record; they are not pooled into an undocumented index.

| Child | Native information and permitted role | Initial horizons and explicit dependency |
|---|---|---|
| X09.NKD_FX | NKD/Nikkei native index points and USDJPY currency returns; compare local equity and currency context separately, then interactions. Index points are not a cash notional to multiply blindly by FX. | 15/60-minute and next-session tails only at supported data cadence; separate Japan/US calendars and NKD tick/point contract registry. |
| X09.HG_FX | HG copper prices/flow, supported SHFE copper context and USDCNY; preserve weight, currency, contract grade and delivery units before any spread proxy. No guaranteed cross-exchange arbitrage identity. | 15/60-minute if native streams support it; session/day for daily inventory/FX fields. Lagged publication required for reports. |
| X09.SI | SI native silver trade/quote features, with slow SLV/SHFE state supplied only by certified X10 measurement ports. | 15/60-minute native-flow and session/day slow-context heads separately; missing slow context does not invent intraday inventory. |
| X09.YM_RTY | Actual YM/RTY trade-price/activity and bar relative strength; MBP-dependent imbalance exists only if separately acquired and verified. | 5/15/60-minute price/flow heads; no unverified best-quote or hidden-depth inputs. |
| X09.RATES | Recorded yields/rates levels/changes and curve spreads with observation date, release time and vintage. Distinguish actual market-price streams from revised economic series. | Session/day unless an acquired intraday stream is verified; uncertified historical publication/vintage disables that field/head until F04 certification. |

## X10 — Slow positioning, inventories and fund-flow context

1. **Purpose/sources.** Account for acquired CFTC, SHFE and SLV inputs rather than losing them silently; full inventory requirement and cross-asset research suggestions.
2. **Inputs.** CFTC positioning reports, SHFE silver/copper inventory, SLV fund history, release/observation/receipt dates and revisions. Child experts `X10.COT`, `X10.SHFE`, `X10.SLV`, each separately scored; these are slow context sources, not dealer options books.
3. **Definition.** Build publication-lagged levels/changes/percentiles and report-age features; distinguish positions-as-of date from report date (do not assume a Tuesday observation was known Tuesday). Predict subsequent session/day volatility or cross-asset stress conditional on market state. Unknown historical publication/vintage disables that child until certified; no synthetic intraday update. Binding local refinement: [SR-X10](../SYSTEM_REFINEMENT.md#sr-x10).
4. **Output.** Slow-state measurements and optional common-target forecasts, publication uncertainty and applicability. No short-term directional certainty from weekly inventory.
5. **Dependencies.** F04/07/C17 and X09 measurement ports/F11; publication certification is explicit. C20 may consume slow measurements; later X06/G consumes slow forecasts. X09 may not consume current X10 forecasts if X10 consumes its current forecasts. Initial E0–E4 do not wait for unavailable publication data.
6. **Comparisons.** No slow data; last-published level/change with shrinkage regression; simple nonlinear interactions only if sufficient reports. Granular child models require effective report counts, not duplicated minute rows. Binding further upgrade and child comparisons: [UP-X10](../UPGRADE_PATHS.md#up-x10).
7. **Training.** Group by report vintage/release interval and same-date assets; train-only normalization, no current revised history. Weight one report's repeated intraday observations appropriately.
8. **Tests.** Observation-versus-release lag, revised report, missing release, holiday delay, unit conversion and copying one weekly value into thousands of falsely independent samples.
9. **Acceptance.** Publication certification plus incremental held-out session/day score or risk/value benefit; otherwise benchmark/defer/reject with recorded reason, preserving provenance.
10. **Ablation/fallback/resources.** Each slow source and lag, report-date placebo and level/change comparison. Fall back without the child. Class B tiny tables; acquisition/vintage uncertainty is a research dependency, not permission to guess.
