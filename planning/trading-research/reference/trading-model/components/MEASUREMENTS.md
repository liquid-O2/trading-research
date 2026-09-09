# Market measurements: flow, auction and price structure

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
Binding [common contracts](COMMON_CONTRACTS.md) apply. Measurement accuracy is tested separately from predictive/economic value. Each asset/anchor/cohort variant gets a stable child ID. TradingView proxies are retained as named benchmarks, not treated as equivalent to event-derived measurements.

## M01 — Ordinary traded CVD

1. **Purpose/sources.** Preserve ordinary aggressor flow; USR-20260905-02, VW10, RDL, CRL-06/15, SKY089 and DA-12.
2. **Inputs.** F05 eligible futures trades `(price ticks,size contracts,reported side)` and reset anchor; all supported futures cohorts. Update per trade, publish event/1s/1m/decision states after F04 availability.
3. **Definition.** `D_i=s_i q_i` for known aggressor `s∈{−1,+1}`; `CVD_t=sum D_i` since anchor. Track total buy/sell/unknown volume separately. Unknown contributes zero to the signed estimate, with uncertainty bound ±unknown volume, not a claim of neutral activity. Session-reset and continuous/rolling differences are distinct series. Binding local refinement: [SR-M01](../SYSTEM_REFINEMENT.md#sr-m01).
4. **Output.** Measurement of cumulative signed contracts, buy/sell/unknown totals, known-side fraction, increments/slopes by causal window, reset/version. Exact arithmetic has no probability target; downstream directional/price-progress targets begin after availability.
5. **Dependencies/use.** F03–05/F09; M02/M03/M10, Context participation and deferred Response use the same stream. Never combine standalone trades and MBP Trade actions without deduplication/reconciliation.
6. **Comparisons.** Rule baseline reported trade signs; statistical baseline signed-volume rate/seasonal z-score; quote/tick-rule and OHLC-sign volume are separately named source proxies. Learned interpretation is C/G/R, not a new definition of CVD. Binding further upgrade and child comparisons: [UP-M01](../UPGRADE_PATHS.md#up-m01).
7. **Rules.** Scale by prior same-session volume or training quantiles, not final daily volume. Corrections produce a current correction event; historic decision CVD remains replayable.
8. **Tests.** Known sequence +5,−2,+4 gives final +7; resets, unknown-only bar, simultaneous ties, correction and split input batches. Total buy+sell+unknown equals eligible volume.
9. **Acceptance.** Exact trade-stream reconciliation; no artificial price-bar dependency. Score subsequent path forecasts and economic incremental value versus volume alone on common opportunities.
10. **Ablation/fallback/resources.** Remove sign, shuffle signs within matched windows, compare reset anchors; monitor unknown fraction/drift. Missing stream returns unavailable. Class A, constant state/anchor, raw trade archive shared.

## M02 — Size-cohort CVD with true within-bar OHLC

1. **Purpose/sources.** Preserve separate trade-size cohorts and their intrabar high/low divergences; user clarification, CEX/CRL flow ideas, JXA-13/15. Cohorts are participant-size **proxies**, not identities.
2. **Inputs.** M01 trade sequence including size, timestamps and quality; chosen bar/session anchor. Native trades required for exact extrema. Every supported futures asset/session has its own cohort calibration.
3. **Definition.** For cohort `b`, `C_b(t)=sum s_i q_i 1[q_i∈b]`. Bar open is cumulative value immediately before first event; high/low are max/min over the entire cumulative path including open; close is final value. Also emit bar-relative OHLC by subtracting open. Start with fixed count buckets and train-only size quantiles as competing definitions; retain source large-print 100 NY/75 London and top-35% filters as benchmark variants, not universal thresholds. Binding local refinement: [SR-M02](../SYSTEM_REFINEMENT.md#sr-m02).
4. **Output.** Per-cohort CVD OHLC, high/low timestamps, volume/print counts, unknown bounds, cumulative and reset identity. For incomplete/tie-ambiguous ordering emit provisional or extrema bounds. No extrapolation of minute totals into tick extrema.
5. **Dependencies/use.** M01/F09; M03 divergence, C participation, L aggression and R sequences. Cohort thresholds fixed before the evaluation period and versioned.
6. **Comparisons.** All-flow CVD; cohort close-only summaries; full cohort OHLC. Statistical regularized interaction model versus compact sequence model downstream tests whether intrabar extrema add information. Binding further upgrade and child comparisons: [UP-M02](../UPGRADE_PATHS.md#up-m02).
7. **Training.** Compare equal-count versus equal-volume quantile bins on training only. Rare cohorts shrink/merge only by a registered rule. Never assign trade size to an institutional identity or use future volume percentile.
8. **Tests.** Sequence +10,−20,+10 has zero close change but nonzero extremes; opposite cohorts cancelling aggregate delta; empty cohort; changed bucket threshold; event-order ties; sum cohort closes equals known-side total.
9. **Acceptance.** OHLC ordering/mass identities exact; per-cohort sample sufficiency and coverage; incremental future-path calibration and one-mini value over close-only features with date-block intervals.
10. **Ablation/fallback/resources.** Collapse cohorts, remove extrema, shuffle event order preserving final delta, test adjacent cutoffs. Fall back to ordinary CVD if cohort support fails. Class A; O(number cohorts×anchors), no per-cohort raw tape copy.

## M03 — Divergence and SMT measurement family

1. **Purpose/sources.** Preserve ordinary, cohort, OHLC-extreme and cross-market trade-level divergence constructions; USR-02, JTR SMT, CRL-11/19, OSF/TTM source variants.
2. **Inputs.** Causal confirmed swing anchors M08, current provisional extrema, M01/M02 flow, synchronized as-of receiver/source prices and quality. NQ/ES plus supported flow assets; update at anchor confirmation or decision time.
3. **Algorithm.** Define anchor pair `(a,b)` and comparison interval before testing divergence. Record price new-high/low versus CVD failure/excess at the same anchors; include regular and hidden direction variants as separate flags. For cohorts compare each CVD high/low/close and inter-cohort disagreement. Cross-asset SMT compares whether source/receiver breach their own previously known reference extrema within a declared lag window; it does not require equal price scales or simultaneous touches. Trade-level running extremes and confirmed-pivot variants stay separate. Binding local refinement: [SR-M03](../SYSTEM_REFINEMENT.md#sr-m03).
4. **Output.** Anchor IDs, comparator types, signed normalized differences, first known_at, lag, confirmation/provisional status and uncertainty. Pattern flags are measurements; subsequent continuation/reversal is a separate label.
5. **Dependencies.** M01/02/08, F04/07, X synchronization. C/L/R consume continuous differences and flags, not an automatic reversal instruction.
6. **Comparisons.** Exact source pivot divergence; simple differences/slopes with logistic path prediction; duration-aware or compact temporal model. Compare within-bar extrema versus final close and trade-level versus coarse bars on identical anchors. Binding further upgrade and child comparisons: [UP-M03](../UPGRADE_PATHS.md#up-m03).
7. **Rules.** Anchor search and tolerance selected in training; no retrospective pairing of the two most visually convincing extremes. Normalize by preceding volatility/flow scale, retain missing source as unavailable.
8. **Tests.** Backplotted pivot detectable only after right bars, delayed ES feed, aggregate no-divergence but large-cohort divergence, hidden continuation divergence, no new reference breach, mismatched dates and tie ambiguity.
9. **Acceptance.** Zero early confirmation; event counts and lag distributions stable across replay; incremental proper score/net value over price structure alone, with false-discovery control across many variants.
10. **Ablation/fallback/resources.** Swap source asset/date within matched regime, lag-shift, remove cohort identity/sequence order. No common stream means no SMT assertion. Class A/B event-window comparisons; cap anchor history by explicit horizon.

## M04 — Trade-at-price volume profiles and value geometry

1. **Purpose/sources.** Preserve Jumbo's actual VP anchors and auction value rather than replacing them with a generic rolling profile; JXA-06/09/13/16, JFN-08, VP2/MAV/RVP, PIN066, SKY090.
2. **Inputs.** Eligible trade price/size and F03/F10 anchors. Separate previous RTH 09:30–16:00 NY, developing RTH, full futures session, 06–09 formation, source-specific fixed/visible/swing/composite windows. Price-row resolution in exact ticks; no inferred volume at untraded prices.
3. **Definition.** `V_k=sum q_i 1[p_i in row k]`; POC maximizes V. Freeze row grid/anchor at formation or explicitly version adaptive grid. Deterministic tie rule initially lower price. Contiguous value area starts at POC and expands toward larger neighboring volume with declared tie rule until target fraction reached; store achieved fraction/boundaries. Source 68%/70% and alternative algorithms are distinct benchmarks. Identify local maxima/minima/valleys from a causal smoothed histogram with training-fixed bandwidth. Binding local refinement: [SR-M04](../SYSTEM_REFINEMENT.md#sr-m04).
4. **Output.** Profile vector, POC/VAH/VAL, mass, modes/shelves/gaps, shape metrics, row/anchor/version. Developing profile is provisional; completed prior-RTH becomes available at close, not next morning by necessity.
5. **Dependencies.** F05/F09/F10; C auction state, L profile locations and M05. Delta and total profiles must share exact anchor/grid when compared.
6. **Comparisons.** Faithful Pine/Atlas OHLC-range allocation, exact trade histogram, robust KDE/multiscale profile. Statistical shape features before CNN/TCN embedding. Bar allocation is an estimate even when total buy/sell volume is real. Binding further upgrade and child comparisons: [UP-M04](../UPGRADE_PATHS.md#up-m04).
7. **Rules.** Anchor selection and smoothing learned only in training. Visible-range profile requires a declared algorithmic viewport known at t; a human final chart viewport is inadmissible historic input.
8. **Tests.** Volume conservation, flat candles/trades, untraded gap, POC ties, value-area ties, 68 versus70%, high-volume tail, window boundary, bin shift and current-future viewport leak.
9. **Acceptance.** Exact mass and anchor parity; hand fixtures reproduce source geometry where specified. Profile predictive/economic lift must exceed matched density/width/distance/time placebo levels.
10. **Ablation/fallback/resources.** Anchor, bin width, smoothing, volume weights and proxy-vs-real comparisons. Missing tape yields unavailable or separately tagged bar proxy. Class A/D sparse per-price maps; expire hot anchors explicitly.

## M05 — Delta profiles and side-separated auction geometry

1. **Purpose/sources.** Preserve Jumbo delta profiles, Reading Delta and flow shelves; JFN-08, RDL, CRL-06/13/19, user VP emphasis.
2. **Inputs.** Same anchor/grid as M04 plus M01 signs/cohorts. Futures tick coverage; per-trade updates and decision snapshots.
3. **Definition.** `B_k=sum buy q`, `S_k=sum sell q`, `U_k=sum unknown q`, `Delta_k=B_k−S_k`. Store signed and absolute-delta mass, peak positive/negative rows, delta/total ratio where denominator valid, cumulative side distributions and cohort channels. Signed delta is not a nonnegative density; do not feed it directly to a probability/KDE routine. Side KDEs are nonnegative and differenced afterward if desired. Binding local refinement: [SR-M05](../SYSTEM_REFINEMENT.md#sr-m05).
4. **Output.** Side profiles, delta shelves/extrema, imbalance vector and unknown fraction. Interpret as executed aggression history, not held inventory or proof of trapped traders.
5. **Dependencies.** M01/02/04; C control/efficiency, L aggression/profile candidate generators and R reading-delta branches.
6. **Comparisons.** Total-volume-only profile; source bar-signed proxy; actual side-separated profile. Statistical side/price interactions versus multichannel profile CNN/TCN under common opportunity sets. Binding further upgrade and child comparisons: [UP-M05](../UPGRADE_PATHS.md#up-m05).
7. **Rules.** Normalize by prior volume or within-profile observed total, retaining age/formation coverage. Thresholds/cluster distances fit in training; no future markout used to create a historic 'winning delta' shelf.
8. **Tests.** Buy/sell cancellation at POC, unknown side, nonnegative side conservation, negative delta peaks, same profile totals with different signs, cohort channel summation and grid changes.
9. **Acceptance.** Exact side mass reconciliation; separate gains from density and sign; calibration/utility improvement versus M04 alone with paired date-block intervals.
10. **Ablation/fallback/resources.** Sign shuffle preserving total histogram, cohort collapse, peak-only versus full shape, old versus developing anchors. Fall back to total profile only when validated. Class A, constant extra channels per row.

## M06 — TPO and time-at-price auction measurements

1. **Purpose/sources.** Preserve TPO initial balance, value, single prints, tails and naked references; TP3, MAT, MAV, SKY091.
2. **Inputs.** Price visits/trades and fixed time brackets (source 30-minute benchmark, alternatives separately), tick-row grid and RTH/full-session anchor.
3. **Definition.** TPO count is number of distinct brackets visiting each row, not volume and not exact dwell time. Exact trade-visit versus OHLC-high-low-filled rows are distinct constructions. Dwell-time estimate uses explicit interpolation/last-observation rule and stale-gap cap. POC/value area use declared tie/expansion rules; single prints/tails require completed brackets/session and a minimum bracket count defined per benchmark. Binding local refinement: [SR-M06](../SYSTEM_REFINEMENT.md#sr-m06).
4. **Output.** TPO profile, bracket matrix, developing/final POC/value/single-print/tail/IB objects and exact known_at. Prior naked POC is untouched since its confirmed birth, not retroactively 'naked' based on future non-touch.
5. **Dependencies.** F03/09/10, M04 grid; C balance/discovery and L profile/IB candidates.
6. **Comparisons.** Faithful source bracket TPO; exact visits; continuous dwell and volume profile. Statistical shape/path models before image/network encoders; no universal Gaussian auction assumption. Binding further upgrade and child comparisons: [UP-M06](../UPGRADE_PATHS.md#up-m06).
7. **Rules.** Session completion and single-print confirmation enforced. Auto row resolution learned from earlier ranges only; daily composites keep all constituent session provenance.
8. **Tests.** Untraded gap inside bar range, repeated visits same bracket, single print later filled before session ends, naked level touched at next open, short holiday, missing bracket and source display hiding far levels.
9. **Acceptance.** Bracket counts and causal availability exact; test incremental path/value beyond volume profile on identical anchors and placebos.
10. **Ablation/fallback/resources.** Time-versus-volume, bracket length, exact-vs-OHLC visits, IB inclusion. Missing tape can use labelled bar proxy only. Class A/D bracket bitsets and sparse rows; no intrabar dwell certainty from OHLC.

## M07 — Price VWAP, anchored VWAP and dispersion

1. **Purpose/sources.** Preserve RTH/ETH and anchored VWAP/bands; VW10, CRL-06, PIN069, SKY088. Exposure-weighted strike center is O17 and is not price VWAP.
2. **Inputs.** Eligible trade prices/volume and anchor registry: RTH, futures session, week/month/quarter/year, causal event/swing anchor. Scope all traded-volume assets with exact timestamps; index volume proxy explicitly tagged.
3. **Definition.** `VWAP=sum pq/sum q`; weighted variance `sum q(p−VWAP)^2/sum q`, stable online moment calculation. Bands use k×weighted SD or declared percentage; 2/2.5/3 are source benchmarks. OHLC3/close×bar-volume approximation is separate. Reset, event anchor and rolling VWAP are different series. A source reanchor on every 06–09 new high is preserved as a distinct PIN069 benchmark. Binding local refinement: [SR-M07](../SYSTEM_REFINEMENT.md#sr-m07).
4. **Output.** VWAP, dispersion, band levels, slope, price distance, anchor/version and mass. No confidence interval interpretation unless a separate forecast calibrates it.
5. **Dependencies.** F03/05/10, M08 for confirmed event anchors; C auction and L VWAP objects.
6. **Comparisons.** Exact traded-price baseline, bar proxy, anchored variants, robust quantile bands versus SD/percentage. Statistical forecast of return/reclaim and learned contextual selection remain downstream. Binding further upgrade and child comparisons: [UP-M07](../UPGRADE_PATHS.md#up-m07).
7. **Rules.** Anchor known_at may be later than geometric swing time; pre-confirmation trade cannot use a newly anchored retrospective VWAP. Index borrowed ES volume is a proxy and cannot claim true SPX traded VWAP.
8. **Tests.** Known weighted mean/variance, zero volume, reset jump, same trades different bar sizes, high-reanchor stale first bar, confirmation delay and numerical cancellation at large prices.
9. **Acceptance.** Mass/moment parity; exact known_at; conditional reach/departure tests control location density and distance. Source win rates not accepted as calibration.
10. **Ablation/fallback/resources.** Anchor, k, true/bar volume and dispersion definition; monitor reset/coverage. No reliable volume means unavailable or explicit price-only mean challenger. Class A O(1)/anchor.

## M08 — Causal swings, structure and retracement anchors

1. **Purpose/sources.** Preserve confirmed and provisional swing structure, BOS/CISD inputs, fib/OB/FVG source anchors; OSF, JTR/JXA, PIN sweep family.
2. **Inputs.** F09 final/provisional bars or trade path, pivot left/right lengths, minimum move and session/roll boundaries. Update on bar completion/event threshold.
3. **Definition.** A k-left/k-right pivot at bar i becomes confirmed only at close/availability of i+k. Event directional-change swings confirm after an observed reversal threshold; running extreme remains provisional until then. Record extreme time and confirmation time separately. Retracement center `L+f(H−L)` for f=.25/.5/.75 or declared source ratio; direction/open-to-close body anchors separate from full range. Binding local refinement: [SR-M08](../SYSTEM_REFINEMENT.md#sr-m08).
4. **Output.** Swing graph, leg IDs, extremum/confirmation events, running/provisional ranges, structural break/reclaim measurements. No hindsight redrawing of live decision history.
5. **Dependencies.** F03/08/09/10; M03 divergence, L swing/imbalance and R CISD/structure.
6. **Comparisons.** Source fractal lookbacks, fixed reversal ticks, volatility-scaled directional changes; statistical duration/transition models and compact sequence model downstream. A complex swing detector must improve targets after its delay. Binding further upgrade and child comparisons: [UP-M08](../UPGRADE_PATHS.md#up-m08).
7. **Rules.** Threshold normalization uses prior volatility. Tune pivot size in nested training; keep right-bar delay in both labels and costs.
8. **Tests.** Equal highs, nested swings, confirmation invalidated by new high, incomplete right bar, gap, roll jump, no pivot in trend and bar-size sensitivity.
9. **Acceptance.** Prefix invariance and exact backplot-versus-available distinction; test anchor stability and incremental forecast/economic value over raw lagged prices.
10. **Ablation/fallback/resources.** Confirmed versus provisional, different threshold scales, anchor randomization. Unconfirmed points do not masquerade as confirmed; fallback running-extreme features retain provisional flag. Class A bounded deque/graph.

## M09 — Best-quote OFI, imbalance and replenishment proxies

1. **Purpose/sources.** Extract observable MBP-1 pressure without inventing depth; DM5–7, DEN, RFE, CRL-02/15, TECH-06.
2. **Inputs.** Consecutive validated MBP-1 best bid/ask states, prices/sizes, action, resting side, reported trade aggressor and decoded flags; native order/receipt fields only where actually supplied. NQ and common ES cohort, other supported futures. Preserve separate add/modify/cancel/trade event-rate channels; exclude replay initialization from fresh liquidity activity.
3. **Definition.** With bid pB/qB and ask pA/qA, event OFI is `1[pB>=pBprev]qB−1[pB<=pBprev]qBprev−1[pA<=pAprev]qA+1[pA>=pAprev]qAprev`; aggregate over causal windows. Queue imbalance `(qB−qA)/(qB+qA)`; microprice `(pA*qB+pB*qA)/(qB+qA)`. At unchanged best price, only when feed ordering reconciles the interval, estimate net displayed non-trade change `q_new−q_old+E`, where E is eligible executed quantity depleting that same side between those snapshots. Positive/negative values estimate net additions/cancellations, not gross refill/cancel or trader identity; unknown ordering/hidden execution yields an ambiguity flag. Track depletion, observed best-price/size-state persistence and spread flicker separately; these are not individual order lifetimes, and off-touch depth remains unavailable. Binding local refinement: [SR-M09](../SYSTEM_REFINEMENT.md#sr-m09).
4. **Output.** OFI/contracts, depth/imbalance/microprice, action/side event rates, visible replenishment/depletion/best-state-persistence features, quality and timing bounds. Book state is the provider-normalized MBP view, with no extra trade-size subtraction before applying its subsequent quote changes. Future markout labels start after feature cut, unlike contemporaneous impact regressions.
5. **Dependencies.** F04–06; C liquidity/control, P fills/adverse selection, R replenishment/absorption.
6. **Comparisons.** Quote-state-only, trade-only and combined action/side/flow channels at identical cuts; linear OFI/impact regression, lagged ridge/logistic forecast, Hawkes or compact sequence model if sufficient events. Vary decision cadence separately. Compare against trade delta, not assume OFI superiority transfers from equities. Binding further upgrade and child comparisons: [UP-M09](../UPGRADE_PATHS.md#up-m09).
7. **Rules.** Normalize by prior depth/seasonal activity; exclude invalid crossed BBO from executable features; preserve auction cohort separately. Receipt uncertainty constrains short-horizon conclusions.
8. **Tests.** Bid/ask price improves/worsens/unchanged, zero depth, same-sequence batch, trade without quote change, crossed auction, execution counted twice, price changes inside interval, replenishment offset by cancellation and quote refresh without identity. Require net-recovery conservation only in supported reconciled bundles.
9. **Acceptance.** Formula fixtures exact; no future BBO; forecast gain after latency and spread. Report errors by missing-ES/auction/session cohort.
10. **Ablation/fallback/resources.** Remove quote updates, remove price-changing OFI, lag shuffle and depth normalize. Missing MBP yields unavailable, not inferred full book. Class A high event-rate hot path; profile before full replay.

## M10 — Tape intensity, effort, progress and response efficiency

1. **Purpose/sources.** Measure pace and effort-progress mismatch underlying absorption/control; FP8/9, YMA, RDL, RFE, CRL-15/16.
2. **Inputs.** M01/02 trades, M09 BBO, price path; causal clock-time and event/volume windows. Cadence 100 ms–1s for supported tape, slower aggregates for Context.
3. **Definition.** Trades/sec, contracts/sec, signed volume/sec, interarrival quantiles, same-side run lengths, size distribution, tick movement/sec, spread/depth change and signed price progress per unit effort. Use `progress/(epsilon+effort)` with scale-aware epsilon frozen in training; emit numerator/denominator separately. Compare observed markout after a completed effort burst only once its horizon matures; no future 'failed effort' label as current input. Binding local refinement: [SR-M10](../SYSTEM_REFINEMENT.md#sr-m10).
4. **Output.** Continuous pace/efficiency vectors and optional threshold-event alphabet with known_at/duration. Future absorption/continuation outcomes are R/C labels, not facts about trader intent.
5. **Dependencies.** M01/02/09, F09; C participation, L memory, R ordered sequences.
6. **Comparisons.** Rolling counts and robust seasonal z-scores; Poisson/negative-binomial intensity and linear efficiency; Hawkes, HSMM/compact temporal net. Select based on calibration and causal predictive improvement, not model fashion. Binding further upgrade and child comparisons: [UP-M10](../UPGRADE_PATHS.md#up-m10).
7. **Rules.** Time-of-day normalization trained on preceding sessions; include quiet background windows and non-events. Heavy tails/zero effort use robust distributions and explicit missing flags.
8. **Tests.** High effort/no progress, low effort/large gap, same volume/different pace, delayed quote, one giant trade, alternating sides and window boundary reset.
9. **Acceptance.** Count/scale invariants; intensity likelihood/calibration and forward-path score; economic test accounts for recognition time. No claim that slow price proves absorption.
10. **Ablation/fallback/resources.** Volume-only, price-only, no pace/order, fixed versus adaptive windows; monitor seasonality and burst drift. Class A/B, E for sequence candidates; bounded ring buffers.

## M11 — Aggression memory and subsequent markout ledger

1. **Purpose/sources.** Preserve origin-of-move, protected prints, large-trade shelves and delta memory without claiming held inventory; OFM, RDL, WIC, TBR, JXA-08/15, MVF/CRL-19.
2. **Inputs.** Trade/cohort bursts, price zones, M04/05 profiles and subsequent available prices. Every memory object has birth/threshold version; source benchmark filters distinct.
3. **Definition.** Cluster observed same-side effort by tick distance/time window; record volume-weighted price, dispersion, side, cohort, duration and subsequent adverse/favorable markouts. Maintain current distance, age, retests, reclaim and observed failure/success to extend. Decay weights by elapsed time/volume/retests as registered alternatives. 'Protected' requires a defined subsequent test holding a level and is known only then; 'trapped' remains a behavioral hypothesis. Binding local refinement: [SR-M11](../SYSTEM_REFINEMENT.md#sr-m11).
4. **Output.** Memory-object measurements and matured markout labels with no inventory identity. Unresolved clusters retain unknown outcome; two opposing cohorts can coexist at one price.
5. **Dependencies.** M01/02/04/05/08/10 and F10; L aggression candidates, C control and R retest branches.
6. **Comparisons.** Source fixed-size/shelf rules; online KDE/DBSCAN with train-defined metric; regularized survival/markout models; multichannel profile/sequence embedding. Hindsight HOD/LOD selection is not the baseline. Binding further upgrade and child comparisons: [UP-M11](../UPGRADE_PATHS.md#up-m11).
7. **Rules.** Clusters formed from observed prefix only; merging/splitting creates versions. Thresholds standardized by prior asset/session activity; signed weights separated into nonnegative channels.
8. **Tests.** Large print followed by no continuation, later reclaim, opposing same-price clusters, cluster merge after decision, false institutional label, initial protection later broken and delayed markout maturity.
9. **Acceptance.** Exact event provenance and no future-cluster membership; predictive/economic value above density-matched price-only clusters with interval uncertainty.
10. **Ablation/fallback/resources.** Remove size/cohort/sign/decay/retest history, match random clusters. Expire by predeclared lifecycle; preserve archive. Class A/B sparse active clusters; optional E sequence buffers.

## M12 — Opens, gaps, settlements and reference-price measurements

1. **Purpose/sources.** Preserve source-specific opens, prior settlement and gap families; CRL-06, JTR, PIN019/064/066/074, INV statistics.
2. **Inputs.** First eligible print of named session, prior actual session close/high/low, official settlement statistics after publication, weekly/monthly starts and actual contracts.
3. **Definition.** Separate session first trade, bar open, official settlement, midpoint and VWAP. Gap is declared reference difference (e.g. current RTH open minus prior RTH close or settlement), with direction/size normalized by prior volatility. Record gap fill as ordered first passage to frozen reference, not unconditional high/low exceedance. Body-25 `0.75C+0.25O` differs from `L+.25(H−L)`; retain both when sources use them. Binding local refinement: [SR-M12](../SYSTEM_REFINEMENT.md#sr-m12).
4. **Output.** Reference-price object and gap measurements, publication/anchor type, incomplete-open flag, no-fill/censor outcomes for later models.
5. **Dependencies.** F02–04/08/09/F10; C open-location context, L reference targets and P boundary accounting.
6. **Comparisons.** Source clock/reference benchmark; empirical gap-fill frequency; logistic/survival conditional model. Never substitute a learned synthetic 'settlement' for the official price. Binding further upgrade and child comparisons: [UP-M12](../UPGRADE_PATHS.md#up-m12).
7. **Rules.** First print may be late/auction; document availability and quality. Settlement ts_ref is observation date, not known_at. No eventual gap-fill label at session open.
8. **Tests.** Missing opening tick, no RTH holiday, revised settlement, prior calendar versus trading day, midnight clock, body-vs-range quarter, roll gap and gap past target without trade.
9. **Acceptance.** Exact reference reproduction; conditional probabilities distinguish touched/closed-through/held and include unresolved denominators; downstream comparison on common dates.
10. **Ablation/fallback/resources.** Alternative source anchors with provenance; no settlement fallback masquerading as official. Class A small state; monitor publication delay and unexpected reference jumps.

## M13 — Footprint and within-bar aggression geometry

1. **Purpose/sources.** Preserve stacked/diagonal imbalance, delta peaks, unfinished auctions, tails and effort location; FP8/FP9/RDL/YMA/MAV, JTR absorption proxy and OSF/MVF.
2. **Inputs.** Ordered eligible trades with side, M09 BBO where available, frozen price rows and bar/range anchor. Exact footprint needs trade-at-price allocation, not candle body/wick volume distribution.
3. **Definition.** Build buy/sell/unknown volume at each tick or registered row. Same-price imbalance compares B_k/S_k; diagonal compares B_k against S_{k−1} (mirror sells against B_{k+1}), with explicit zero-denominator and minimum-volume rules. Stacked imbalance requires consecutive qualifying rows, separately from a single peak. Record terminal print size, tails, delta extrema location and price/CVD close versus excursion. OHLC wick+relative-volume 'absorption' remains a separate source proxy. Binding local refinement: [SR-M13](../SYSTEM_REFINEMENT.md#sr-m13).
4. **Output.** Footprint channels, imbalance runs, peak/tail objects and exact availability; no automatic absorption/iceberg label. Sparse edge zeros are not proof all business completed.
5. **Dependencies.** M01/02/04/05/F09; C participation and R footprint/control sequences, L protected-print locations.
6. **Comparisons.** Faithful source footprint thresholds and bar proxies; statistical row contrasts; compact multichannel CNN/sequence encoding after exact measurements. Compare data granularity separately from model class. Binding further upgrade and child comparisons: [UP-M13](../UPGRADE_PATHS.md#up-m13).
7. **Rules.** Row width/minimum volume/ratio thresholds fit only training; class balance includes ordinary background bars. Preserve within-bar order when available and mark ambiguous timestamps.
8. **Tests.** Diagonal versus same-price imbalance, zero opposing prints, price gaps, stacked run interrupted by one row, high delta at low of bullish bar, same OHLC/volume with different footprint and incomplete candle.
9. **Acceptance.** Side/total conservation and fixture geometry; useful prediction after completion delay; false-positive and context-conditioned outcome rates with date-level uncertainty.
10. **Ablation/fallback/resources.** Remove sign, price-row order, stack length, cohort or wick detail; compare bar proxy on identical dates. Class A/D sparse row buffers; fallback only to explicitly labelled coarse features.
