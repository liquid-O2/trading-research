# Preserved Response mechanisms and later experiments

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
Detailed Response development follows the user's current Context/Location program. These cards preserve distinct mechanisms now and define their observation/label dependencies. They do not make Response confirmation a prerequisite for entry. [Common contracts](COMMON_CONTRACTS.md), particularly CC-01/04/05/07/10, apply to every numbered card.

For all R cards, publish `ResponseState(mechanism_id,version,source_object_ids,direction,stage,event_times,observed_features,coverage,ambiguities,failed_stage,expires_at)` and optionally a calibrated `Forecast`. Stage events have their own `known_at`; a final pattern cannot be backdated to its first stage. Targets are common `PATH/DEPART/VALUE` definitions with explicit 1/5/15/30-second, 1/5/15-minute and remaining-session variants where timing coverage supports them. Pattern completion is an observable event, not the future success label. Each variant/horizon is separately registered and scored. Thresholds on effort, time, distance and persistence are training-fold choices unless explicitly labeled a source benchmark. Failed, timed-out, no-retest and unfinished sequences stay in the denominator.

Initial sequence models compare causal finite-state rules with logistic/hazard models using stage-duration/continuous features; compact temporal models are candidates only if event coverage and learning curves justify them. No true participant identity, reserve inventory or off-touch depth is supplied by MBP-1. Class E resources mean bounded event buffers around **all causal candidate events**, including rejected candidates, not buffers chosen after seeing winners.

## R01 — Approach speed, aggression and progress

1. **Purpose/sources.** Resolve fast-approach break-versus-exhaustion ambiguity in WIC-02, DM5-03, AUT-09 and FP8-05.
2. **Inputs.** M10 signed trade pace/volume, quote motion/spread, distance to frozen L object, past volatility and approach direction; trade-event updates, with receipt uncertainty.
3. **Definition.** Define approach start by first inward crossing of an outer distance band; compute elapsed distance/time, acceleration, cumulative signed effort, progress per unit effort and pauses. Separate source-side and expected trade-side orientation. Reset only by declared leave/return/timeout rules. Binding local refinement: [SR-R01](../SYSTEM_REFINEMENT.md#sr-r01).
4. **Outputs/labels.** Continuous approach state; competing break, stall, reject and no-contact hazards after the current cut, calibrated by side/context.
5. **Dependencies.** M09/10, C06/18, L17; G05/06 can use the prefix before a complete sequence.
6. **Comparators.** Source fast/slow rule variants, seasonal speed bins, regularized interaction hazard, boosted model; no hard universal direction. Binding further upgrade and child comparisons: [UP-R01](../UPGRADE_PATHS.md#up-r01).
7. **Learning.** Scale against preceding same-session activity; include slow/non-arriving approaches and date/object clustering.
8. **Tests.** T-R01: mirrored approaches, zero elapsed time, quote move without trade, halt, late prints and identical speed with different effort.
9. **Acceptance.** Proper scores and conditional calibration; incremental net value after detection/entry delay and spread stress.
10. **Ablation/fallback/resources.** Speed-only, effort-only, no context and time-shift controls. Missing tape leaves price-only explicitly tagged challenger. Class E/A, rolling bounded accumulators.

## R02 — High-effort stall and absorption proxy

1. **Purpose/sources.** Preserve DM6-01/04/05, YMA-04, FP9-01 and OBT-02 without converting effort into inventory identity.
2. **Inputs.** Signed trades/size cohorts, at-touch quotes, local adverse/favorable displacement, object width and price volatility; event-level within frozen approach/interaction window.
3. **Definition.** High intended-direction aggression plus small progress/retreat defines a stall prefix. Later opposite displacement is a separate transition. Measure executed volume per touched price, progress distribution and dwell; distinguish passive-book evidence from print-only proxy. Binding local refinement: [SR-R02](../SYSTEM_REFINEMENT.md#sr-r02).
4. **Outputs/labels.** Stall magnitude and competing resume/reverse/persist outcomes. The future reversal is never part of the time-t feature.
5. **Dependencies.** M02/09/10/13, R01 and L objects; L19 may also originate an aggression object from the measured stall.
6. **Comparators.** Volume/displacement rule, logistic/hazard model, local event sequence model; side symmetry is tested, not imposed blindly. Binding further upgrade and child comparisons: [UP-R02](../UPGRADE_PATHS.md#up-r02).
7. **Learning.** Natural-prior event/background samples; training-only effort quantiles, separate known/unknown-side volume and tick coverage cohorts.
8. **Tests.** T-R02: many small trades versus one large print, high effort with high progress, stall then continuation, reversed side and bar-close leakage.
9. **Acceptance.** Calibration across location/regime and economic value from each observed prefix; no imported 27% failure statistic.
10. **Ablation/fallback/resources.** Remove book, cohorts or location; compare simple price stall. If side unreliable publish uncertainty or abstain. Class E, bounded footprint and event history.

## R03 — Diminishing-effort exhaustion

1. **Purpose/sources.** Keep declining activity distinct from absorption/stopping bursts; DM6-05, OFM-06, NYA-05, OBT-06.
2. **Inputs.** Trade-count/volume intensity, size distribution, signed effort, successive push distances, spread and quote motion; all size cohorts, not only displayed 30–60 prints.
3. **Definition.** Segment causal pushes using confirmed local reversals or a registered event threshold; estimate effort/pace and displacement decay over successive pushes. A quiet tape with continuing quote-driven progress differs from a failed push. Binding local refinement: [SR-R03](../SYSTEM_REFINEMENT.md#sr-r03).
4. **Outputs/labels.** Decay features and pause/reversal/continued-low-effort path probabilities. Observed absence of filtered bubbles is not zero aggregate aggression.
5. **Dependencies.** M02/08/10 and R01; G05 and later R13 use the state.
6. **Comparators.** Source declining-digits rule, robust trend/intensity regression, point-process/hazard model and compact sequence challenger. Binding further upgrade and child comparisons: [UP-R03](../UPGRADE_PATHS.md#up-r03).
7. **Learning.** Seasonal normalized rates; preserve auctions/halts as distinct quality states, not extreme exhaustion labels.
8. **Tests.** T-R03: excluded-size trades, thinning volume with rising efficiency, no-trade quote drift, zero-volume gap and final push later revised by swing confirmation.
9. **Acceptance.** Distinguish conditional pause from reversal and test added net value over price-only deceleration.
10. **Ablation/fallback/resources.** Compare rate, size and push structure separately; missing prints invalidates exhaustion claim. Class E/A, compact causal push ledger.

## R04 — Stopping burst and climax hypothesis

1. **Purpose/sources.** Preserve huge-delta/no-extension called “exhaustion print” in FP9-05, separately from R03 and DM6 terminology.
2. **Inputs.** M01/02/10 burst magnitude, local price progress/retreat, location and prior effort, event-time seasonal baselines.
3. **Definition.** Detect extreme signed/absolute trade-volume burst with limited extension over an explicitly completed observation window. Publish burst at detection; track subsequent continuation/rejection without hindsight selecting the turning print. Binding local refinement: [SR-R04](../SYSTEM_REFINEMENT.md#sr-r04).
4. **Outputs/labels.** Burst/stall state and competing path distribution over registered horizons; 1–2-bar turn is a source benchmark, not guaranteed outcome.
5. **Dependencies.** M flow, R02 stall, C18 context and L19 origin memory; can update forecasts without waiting for reversal.
6. **Comparators.** Quantile threshold rule, robust tail-score regression, marked-intensity model; compare to R02 continuous effort baseline. Binding further upgrade and child comparisons: [UP-R04](../UPGRADE_PATHS.md#up-r04).
7. **Learning.** Burst thresholds fold-only by instrument/session, with natural frequency recalibration and count/volume distinction.
8. **Tests.** T-R04: one late aggregated print, spread widening, multiple bursts, burst followed by stronger continuation and matched-volume non-extreme location.
9. **Acceptance.** Reliable tail-event uncertainty and incremental calibration/economics; unsupported rare cohorts remain pooled or abstained.
10. **Ablation/fallback/resources.** Remove extremeness, stall or context separately; no automatic fade. Class E/A, short rolling tail-statistic state.

## R05 — At-touch replenishment and resilience sequence

1. **Purpose/sources.** Preserve RFE-02, K18-06, DM6-03/04, DM7-01/05, SRE-03 without hidden-order labels.
2. **Inputs.** Ordered BBO prices/sizes and executed trades at that best price, feed action semantics, sequence/receipt quality and elapsed time. Off-touch state is unavailable.
3. **Definition.** At unchanged best price, estimate net displayed-size recovery adjusted for known executions under F05 semantics. Track execution/displayed ratio, recovery delay, repeat variability/decay, survival under pressure and price loss/reclaim. Batching prevents exact gross additions/cancels: retain bounds/unknown state. Binding local refinement: [SR-R05](../SYSTEM_REFINEMENT.md#sr-r05).
4. **Outputs/labels.** `ResilienceProxy` plus hold/break hazards. “Three ticks refill” yields separate price-distance and update-count benchmark variants where source wording is ambiguous.
5. **Dependencies.** M09 reconciliation and R02 effort; R14/R15 later consume sequence, G may use measured state earlier.
6. **Comparators.** Hold/recovery rule, linear hazard, marked sequence model; print-only and book-only baselines required. Binding further upgrade and child comparisons: [UP-R05](../UPGRADE_PATHS.md#up-r05).
7. **Learning.** Use timing-supported cohorts; no training label “same defender” or “true iceberg.” Normalize execution and duration by recent activity.
8. **Tests.** T-R05: quote price changes, aggregate cancellation plus trade, duplicate update, auction, size recovery from multiple agents and exhausted then renewed defense.
9. **Acceptance.** Algebra/replay correctness, conditional path calibration and executable prefix benefit; no authenticity classification claim.
10. **Ablation/fallback/resources.** Drop quote proxy, decay or execution adjustment; fallback print/price-only tagged model. Class E/A, per-best-price state only.

## R06 — Depth-wide support, pulling and layering dependency

1. **Purpose/sources.** Preserve distinct unavailable DM6-03, DM7-02–04 remote support/stacking/layering mechanisms.
2. **Inputs.** Future verified multi-level/MBO feed with depth, update order and receipt times; current MBP-1 supports only realized successive best prices and side-imbalance oscillation.
3. **Definition.** Full variant measures multi-level size changes, coordinated cancellation and support within two price ticks. Current challenger measures only BBO turnover, observed best-state persistence and successive-price resilience. Neither infers legal spoofing intent or participant identity. Binding local refinement: [SR-R06](../SYSTEM_REFINEMENT.md#sr-r06).
4. **Outputs/labels.** Separate `depth_supported` and `bbo_proxy` applicability; future liquidity loss, shortfall and path labels, not “fake order” ground truth.
5. **Dependencies.** F01/F05 verified new schema and replay; R05 baseline. Full-depth variant explicitly deferred until acquisition is justified/authorized.
6. **Comparators.** Sustained-liquidity rule, calibrated adverse-selection model; no classifier trained on narrative spoof labels. Binding further upgrade and child comparisons: [UP-R06](../UPGRADE_PATHS.md#up-r06).
7. **Learning.** Same-date common BBO/depth cohort if richer data becomes available; avoid treating depth-feed availability as implicit performance advantage.
8. **Tests.** T-R06: off-touch update invisible to MBP-1, benign cancellation, batch simultaneity, dropped level and depth truncation.
9. **Acceptance.** Observable definitions first; require incremental risk/economic information beyond BBO before paying for production depth.
10. **Ablation/fallback/resources.** Full versus BBO versus trades-only on common set. Current full variant abstains by design. Class E/D, depth storage/rates must be measured before resource approval.

## R07 — Candle/footprint effort-result disagreement

1. **Purpose/sources.** Preserve FP9-01/02, OFM-01, OBT-02 and bar-absorption Pine/JTR-20 baselines.
2. **Inputs.** M13 bid/ask footprint and bar OHLC, M01 delta, explicit bar type/timeframe and finalization time; partial-candle features have separate version.
3. **Definition.** Compute candle return sign, net signed volume, body/wick volume geography and excursion path. Positive candle/negative delta and its mirror are observed disagreement, not universal reversal signs. Classify final body membership only at close; event-time challenger uses current geometry. Binding local refinement: [SR-R07](../SYSTEM_REFINEMENT.md#sr-r07).
4. **Outputs/labels.** Disagreement strength and future path forecasts by local versus higher-timeframe trend; complete-bar and partial-bar predictions remain distinguishable.
5. **Dependencies.** F09, M13, C07/18; R09 and R10 may add information without independent-vote multiplication.
6. **Comparators.** Source sign rule and small-body/high-volume proxy; interaction logistic model; local tensor/sequence challenger. Binding further upgrade and child comparisons: [UP-R07](../UPGRADE_PATHS.md#up-r07).
7. **Learning.** Separate time/range/volume bars and size cohorts; training-only normalization and no current bar's eventual OHLC.
8. **Tests.** T-R07: same final OHLC/delta with different event order, bar boundary, future wick enlargement and unknown trade side.
9. **Acceptance.** Causal timing and calibrated conditional sign/continuation behavior; entry delay and full net economics required.
10. **Ablation/fallback/resources.** Price-only, total-volume-only, delta-only, trajectory; fallback to supported completed-bar baseline. Class E/A, reusable M13 aggregates.

## R08 — Diagonal imbalance and stacked-flow defense

1. **Purpose/sources.** Preserve FP8-02–04, OBT-02 and F23-02 arithmetic/threshold distinctions.
2. **Inputs.** Trade-at-price buy `A(p)` and sell `B(p)` contracts, valid tick grid, bar/event window and minimum-count quality; available as events arrive or completed footprint.
3. **Definition.** Buy diagonal ratio `A(p)/B(p−tick)` and mirrored sell ratio; same-price ratio remains separate. Define zero-denominator state/minimum-volume smoothing; compare ratio 3/3.5/4/4.5 and stacked length 2/3 as labeled source variants. Create immutable stack zone only after causal threshold crossings; track partial repair, retest and failure. Binding local refinement: [SR-R08](../SYSTEM_REFINEMENT.md#sr-r08).
4. **Outputs/labels.** Continuous smoothed log ratios, run lengths, total effort and zone lifecycle; reach/depart/traverse labels.
5. **Dependencies.** M13, L09/L19 and L17; G assesses zone relevance independently of profile confluence.
6. **Comparators.** Source thresholds, beta/binomial-style shrinkage of side share or regularized local model, small footprint tensor model. Binding further upgrade and child comparisons: [UP-R08](../UPGRADE_PATHS.md#up-r08).
7. **Learning.** Fold-only thresholds and density controls; price-adjacent counts are not independent simultaneous counterpart trades.
8. **Tests.** T-R08: verbal/diagram contradiction fixture, missing tick rows, zero/low denominator, spread wider than tick and 350%-of versus 350%-greater arithmetic.
9. **Acceptance.** Correct orientation and calibrated downstream outcomes; matched density/width placebo and complete policy value.
10. **Ablation/fallback/resources.** Same-price versus diagonal, run length versus effort and zone-only versus confirmation. Class E/A, sparse tick map with bounded anchor lifetime.

## R09 — Developing POC flip and footprint-mode migration

1. **Purpose/sources.** Preserve FP9-03/06 after-close absorption→POC flip→DOM sequence without backdating.
2. **Inputs.** M04/M13 causal volume-at-price snapshots within current bar/interaction, fixed price rows, tie rule and mode confidence.
3. **Definition.** Track argmax mode position relative to current range, dominance margin, flip count/persistence and mass centroid. A POC flip changes the maximum's identity; prior volume does not physically move. Separate intra-bar flip from successive-bar POC migration. Binding local refinement: [SR-R09](../SYSTEM_REFINEMENT.md#sr-r09).
4. **Outputs/labels.** Flip timestamp, direction, margin, persistence and following path distribution; mode ambiguity explicit at ties.
5. **Dependencies.** R07 disagreement prefix, M04/13 and optional R05; R19 evaluates value of waiting for each added stage.
6. **Comparators.** Lower-to-upper POC rule, continuous mode/mass regression, profile transportation/tensor challenger. Binding further upgrade and child comparisons: [UP-R09](../UPGRADE_PATHS.md#up-r09).
7. **Learning.** Include fleeting flips and no-flip cases; same candidate cohorts for ordered-sequence comparisons and fold-only persistence threshold.
8. **Tests.** T-R09: tied mode, single print switching maximum, evolving range denominator, current-bar final-mode leakage and changed bin width.
9. **Acceptance.** Stable causal mode semantics, conditional predictive lift and net value after delay; no “two tells means trade” axiom.
10. **Ablation/fallback/resources.** Centroid versus argmax, persistence, absorption/DOM stages individually. Missing trades invalidate footprint mode. Class E/A, reuse sparse profile state.

## R10 — CVD-relative control and multiscale divergence

1. **Purpose/sources.** Preserve YMA-02/05, FP9-04, RDL-03/07, SRE-02/05 and user cohort CVD ambition.
2. **Inputs.** M01/02 ordinary/cohort CVD OHLC, M03 causal swing/SMT features, price trend, anchor/reset and own-CVD median/smoother. Options-weighted series use O16 with separate units.
3. **Definition.** Compare CVD to its own causal rolling median/trend; never compare price numerically with contract-valued CVD. Retain local candle disagreement, price-high/CVD-lower-high, price-lower-high/CVD-higher-high, slope mismatch, inter-cohort and cross-market SMT as distinct child features. Confirmation waits for actual swing availability. Binding local refinement: [SR-R10](../SYSTEM_REFINEMENT.md#sr-r10).
4. **Outputs/labels.** Scope/direction-specific divergence state and shared future path/value forecasts; no unconditional bearish sign for every rising-price/falling-CVD observation.
5. **Dependencies.** M03 and C18/X07; R14 optional delta turn and R19 action evaluation.
6. **Comparators.** Explicit source median/slope variants, multi-scale regression, calibrated sequence/mixture using common targets. Binding further upgrade and child comparisons: [UP-R10](../UPGRADE_PATHS.md#up-r10).
7. **Learning.** Fold-only smoothing/scales; compare ordinary versus cohort close-only versus cohort true OHLC. Paired dates and coverage masks required.
8. **Tests.** T-R10: CVD reset, price-unit mismatch, future swing, divergent scales and unchanged close with different within-bar extremes.
9. **Acceptance.** Incremental conditional scores/economics and disagreement diagnostics; largest delta is not necessarily rewarded side.
10. **Ablation/fallback/resources.** Remove each CVD construction/source independently; missing side/chain disables affected feature only under validated gate. Class E/B, shared causal streams.

## R11 — Balance break, retest and failed-retest reversal

1. **Purpose/sources.** Preserve WIC-01/03/05, CCS-02/07, AUT-06 and the distinct MAV-05/06 versus ALM-03/04 failed-auction definitions, including continuation without retest.
2. **Inputs.** Frozen prior/current balance edges, C07 acceptance, trade/quote path, R01/02/10 flow and explicit overshoot/dwell tolerances.
3. **Definition.** Generic branches: hold/bounce; break→continue without retest; break→outside retest→same-side progress; break→failed retest/acceptance back inside. Separate child R11.FA_POC: leave established balance A→reach/reject distinct prior balance B’s causally known POC→return toward/re-enter A, then forecast A’s far edge versus internal ranging/failure. R11.FA_VALUE replaces the B-POC requirement with the broader prior-value reference in ALM; it cannot be labeled the identical setup. A/B identities, POC versus other reference, each event time and unfinished traversal remain explicit. These chains are not collapsed into any generic failed break; belief revision does not automatically authorize an opposite entry. Binding local refinement: [SR-R11](../SYSTEM_REFINEMENT.md#sr-r11).
4. **Outputs/labels.** Stage and competing branch hazards, no-retest/time-out included; labels preserve edge order and frozen object band.
5. **Dependencies.** L03/05/07, C07, L17 and R19; Context/Location may trade the initial edge before sequence completion.
6. **Comparators.** Source break/retest rule, branch-frequency/logistic hazard, multistate survival model. Binding further upgrade and child comparisons: [UP-R11](../UPGRADE_PATHS.md#up-r11).
7. **Learning.** Start every comparison from same initial balance opportunity; adjust repeated visits by object/date and do not train only completed retests.
8. **Tests.** T-R11: deep overshoot, repeated boundary crosses, no-retest runner, failed reclaim and developing/prior-value distinction. For FA_POC/FA_VALUE test distinct A/B lineage, unconfirmed or later-drawn B profile, POC versus non-POC touch, B acceptance instead of rejection, return to A without far-edge traversal, and identical initial cohorts for the two definitions.
9. **Acceptance.** Branch calibration and complete economic comparison of early break, first retest and failed-retest actions.
10. **Ablation/fallback/resources.** Price-only versus flow-conditioned, hard HTF alignment versus soft conditioning. Timeout returns neutral/expired state. Class E/A, small finite-state record per active object.

## R12 — Failed squeeze, refill and renewed same-direction squeeze

1. **Purpose/sources.** Preserve OFM-02–05, CCS-07 and OBT-03 full sequence; do not misread “other side of failure” as always opposite direction.
2. **Inputs.** L19 initial aggressive origin/catalyst, squeeze displacement, pullback through catalyst, newer aggression pockets, R02/05 and causal structural extrema.
3. **Definition.** Track initial squeeze→failure/reclaim through origin→return/defense near prior or lower/higher origin→renewed original-direction progress. Also retain plain squeeze/no-failure branch and failed-squeeze fade as competing separate policies. Original catalyst, intermediate strip and final entry pocket remain different IDs. Binding local refinement: [SR-R12](../SYSTEM_REFINEMENT.md#sr-r12).
4. **Outputs/labels.** Branch/stage, timestamps, distance/effort and future continuation/reversal/value distribution. No selected successful squeeze becomes retrospective origin definition.
5. **Dependencies.** L19, R01/02/05/11; P02 stops and P04 repeats, R19 entry-time comparison.
6. **Comparators.** Explicit finite-state branches, multistate hazard, compact event sequence model with prefix outputs. Binding further upgrade and child comparisons: [UP-R12](../UPGRADE_PATHS.md#up-r12).
7. **Learning.** Sample all origin events before branch known; define expiry by causal time/price horizon. Include repeated failures and non-completing sequences.
8. **Tests.** T-R12: bullish→failure→bullish resqueeze versus bearish fade, catalyst overshoot, no retest, stop-limit trigger without fill and changed pocket.
9. **Acceptance.** Branch discrimination plus full early/refill/resqueeze policy value under conservative fills; source numerical results unvalidated.
10. **Ablation/fallback/resources.** Construction, memory, context and flow independently; source RFE data claims are one provenance family. Class E, bounded event/state history.

## R13 — Quiet failure and passive-reversion alternative

1. **Purpose/sources.** Preserve OFM-06, OBT-06/08 and NYA-05 alternatives requiring no large own-side burst.
2. **Inputs.** C07 balance state, L19 prior-control zone, R03 opposing effort decay, full-size flow coverage, R01 progress and price reclaim.
3. **Definition.** Observe opposing push losing efficiency/pace at eligible zone; track stall/reclaim without requiring own-side aggression. Compare direct C/L fade, failure-only action and subsequent own-flow confirmation. Missing filtered bubbles alone cannot complete the quiet state. Binding local refinement: [SR-R13](../SYSTEM_REFINEMENT.md#sr-r13).
4. **Outputs/labels.** Quiet-failure prefix and competing resume/reversion probabilities; later aggression can update hold/target value separately.
5. **Dependencies.** R03 and C/L; P03 full-position management; no gamma sign gate is mandatory.
6. **Comparators.** Source passive-reversion rule, price/pace logistic model, joint context/effort hazard. Binding further upgrade and child comparisons: [UP-R13](../UPGRADE_PATHS.md#up-r13).
7. **Learning.** Include balanced and directional regimes with soft interactions; all failed quiet signals/no-flow trends retained.
8. **Tests.** T-R13: no 30–60 prints but many larger prints, quote withdrawal rally, thin inactive market, gamma sign uncertainty and source-side annotation ambiguity.
9. **Acceptance.** Incremental path calibration and net value relative to direct C/L entry and waiting; no prior screenshot winner labels.
10. **Ablation/fallback/resources.** Balance, decay and own-flow added separately. Unknown tape activity means unavailable quiet evidence. Class E/A, simple prefix state.

## R14 — Opposing absorption, reward, refresh and lift-off sequence

1. **Purpose/sources.** Preserve YMA-04, SRE-03/05, DM5-04 and DM7-02 as distinct optional stage chain.
2. **Inputs.** R02 high effort/stall, R05 recovery, R03 shrinking opposing flow, R10 CVD hold/turn, bid/ask displacement and zone geometry, all timestamped.
3. **Definition.** Stage chain: high-volume hold→observable recovery→opposite effort shrinks or delta turns→intended-direction progress→optional reward-area retest/refresh. Register source three-price-tick versus three-update recovery; minimum two/up to four price upticks; within 1–2 versus 6–8 ticks of entry displacement as benchmarks. Do not silently equate trades, updates and price ticks. Binding local refinement: [SR-R14](../SYSTEM_REFINEMENT.md#sr-r14).
4. **Outputs/labels.** Prefix state plus remaining trade distribution at every stage; failed, skipped and timed-out stages explicit. More stages do not automatically mean independent confirmation.
5. **Dependencies.** R02/03/05/10, L object, P02/05/06; R19 compares each prefix action on common initial opportunity.
6. **Comparators.** Source conjunctions, additive conditional model, multistate/sequence hazard allowing alternative paths. Binding further upgrade and child comparisons: [UP-R14](../UPGRADE_PATHS.md#up-r14).
7. **Learning.** No training on only fully confirmed winners; rebalance classes only with held-out recalibration. Timing-supported NQ/ES cohorts kept separate.
8. **Tests.** T-R14: recovery without progress, progress before delta turn, late entry, missing stage, failed return and ambiguous source tick meaning.
9. **Acceptance.** Demonstrated incremental net benefit per added stage including missed moves and entry deterioration; no imported 27%/14pp improvement.
10. **Ablation/fallback/resources.** Prefix and leave-one-stage ablations; incomplete sequence does not veto independently valid C/L policy. Class E, bounded stage/event buffer.

## R15 — Rewarded-side memory and protected structure

1. **Purpose/sources.** Preserve RDL-02–06, K18-04/06, F23-04 and NYA-04 control-switch/protection claims as observables.
2. **Inputs.** M11 aggression origins/markouts, M08 confirmed extrema, R05 resilience, current price relative to prior concentrated delta and causal displacement.
3. **Definition.** Record signed effort followed by observed displacement; retain survival/violation of its origin band. Define a protected low/high only after registered displacement plus elapsed/closed-bar/swing confirmation. Track repeat defense, failure and role reversal separately; confirmation never means knowing price will not return. Binding local refinement: [SR-R15](../SYSTEM_REFINEMENT.md#sr-r15).
4. **Outputs/labels.** Protection candidate/version, confirmation delay, control-transition probabilities and remaining downside/upside distribution.
5. **Dependencies.** L19/M11 and L17; P03 may tighten full-position protection only once event is known, P04 owns retry risk.
6. **Comparators.** Source protected-swing rule, price-only swing trail, continuous effort/markout survival model. Binding further upgrade and child comparisons: [UP-R15](../UPGRADE_PATHS.md#up-r15).
7. **Learning.** All aggression pockets and failures, not only those that survive; same-day object grouping and retention-decay variants trained causally.
8. **Tests.** T-R15: sign error in source defense narrative, two control switches, largest delta unrewarded, confirmed swing later broken and gap through protected stop.
9. **Acceptance.** Causal state precision and incremental management/entry economics; no claim same traders still hold positions.
10. **Ablation/fallback/resources.** Flow memory versus price memory, delta concentration definitions separately. Fallback existing validated price protection. Class E/A, bounded state plus immutable archive.

## R16 — Minor-node and intra-wick repeated reactions

1. **Purpose/sources.** Preserve RDL-06, YMA-03, OBT-04/05, TBR-02/03 and CCS-03/06 exact anchored profile distinctions.
2. **Inputs.** M04/05 causal leg/dealing-range/calendar profiles, L05/06 minor nodes/LVNs/ledges, delta concentration, repeated local contacts and bar finalization state.
3. **Definition.** Detect an observed interaction with frozen profile region, overshoot/reclaim, prior reaction count/age and current flow/displacement. Keep upper/lower neighboring regions separate; final wick membership is known only at close. Developing profiles revise forward and cannot justify an earlier trade retrospectively. Binding local refinement: [SR-R16](../SYSTEM_REFINEMENT.md#sr-r16).
4. **Outputs/labels.** Node-interaction state and hold/traverse/stall probabilities, width and contact definition attached.
5. **Dependencies.** L05/06/17, R02/10 and C07/08; can refine an existing L candidate but does not require absolute range extreme.
6. **Comparators.** Node-only and signed-flow-only rules, joint logistic/hazard, spatial profile model. Binding further upgrade and child comparisons: [UP-R16](../UPGRADE_PATHS.md#up-r16).
7. **Learning.** Predeclared causal profile anchors, all touches and matched density/distance/width/time placebo regions; fold-only bin/smoothing choices.
8. **Tests.** T-R16: post-trade profile anchor, small node beside LVN, repeated wick selected after outcome, changing bin width and lower zone confused with upper.
9. **Acceptance.** Incremental economics over profile-only baseline and placebos, uncertainty clustered by object/day.
10. **Ablation/fallback/resources.** Volume versus delta, minor versus major node, calendar versus leg anchor. Missing profile disables this mechanism. Class E/A, shared profile cache.

## R17 — First, second and later defended retests

1. **Purpose/sources.** Preserve WIC-07, RFE-01/03, K18-03, ALS-03, SRE and TBR-03 visit-order claims without universal second-test superiority.
2. **Inputs.** L17 visit IDs, origin/zone width, approach/leave timestamps, prior penetration/reclaim/failure, R05/15 defense and P04 loss history.
3. **Definition.** A new visit requires a declared exit-distance/time condition before return. Estimate durability versus depletion from cumulative testing, age, overshoot and changed evidence. First/second counts are observed prefix values, never total eventual touches. Binding local refinement: [SR-R17](../SYSTEM_REFINEMENT.md#sr-r17).
4. **Outputs/labels.** Visit-specific hold/break/value forecast and selected prefix; no-retest runner remains a competing outcome from initial eligibility.
5. **Dependencies.** L17 owns lifecycle, P04 owns cumulative risk; R19 compares early versus waited actions.
6. **Comparators.** First-only, second-only and age/count rules; hierarchical repeat hazard and nonlinear interactions with effort/resilience. Binding further upgrade and child comparisons: [UP-R17](../UPGRADE_PATHS.md#up-r17).
7. **Learning.** Group entire object/date, account for survival/selection into later visits and compare policies from common origin population.
8. **Tests.** T-R17: repeated ticks within one visit, deep overshoot, fresh object alias, second visit after first loss and never-returning breakout.
9. **Acceptance.** Conditional calibration plus total initial-opportunity/day value; later-touch win rate alone insufficient.
10. **Ablation/fallback/resources.** Count, age, penetration and current defense separately; uncertain visit state disables repeat-specific prediction. Class E/A, compact visit ledger.

## R18 — Jumbo sweep, order-block and rejection-block entries

1. **Purpose/sources.** Preserve JTR-16/17/20/24 and OSF/Pine structural timing variants while allowing direct internal/extension entries.
2. **Inputs.** C01–03 exact source range/path, L08/10 causal sweep block, completed candle sequence and actual trades/BBO for entry replay.
3. **Definition.** Operational bullish sequence `L2<L1` then completed `C3>H2`, bearish mirror `H2>H1` then `C3<L2`. L10 explicitly registers full-range/body order-block geometry where original drawings omit numeric bounds. Compare confirmation entry/midpoint stop, confirmation/extreme stop, and midpoint retracement entry/extreme stop. Swept-wick rejection blocks retain midpoint/extreme stop interpretations. Preserve failure-through momentum and event-delayed branches; fills occur only after confirmation is available. Binding local refinement: [SR-R18](../SYSTEM_REFINEMENT.md#sr-r18).
4. **Outputs/labels.** Block confirmation time, candidate stop/entry variants, no-retrace/non-fill and competing path/value outcomes.
5. **Dependencies.** L10/F09 and P02/05; R19 evaluates remaining opportunity against C/L entry at same origin.
6. **Comparators.** Faithful 2/3/5-minute source variants, simple price confirmation, event-time sweep/reclaim model. Binding further upgrade and child comparisons: [UP-R18](../UPGRADE_PATHS.md#up-r18).
7. **Learning.** Tune timeframe/penetration only in folds; no unoffset HTF lookahead, eventual wick low or final day class as input.
8. **Tests.** T-R18: third candle incomplete, wick-midpoint versus low conflict, internal EQ long versus EQ short, extension continuation and failed confirmation/news delay.
9. **Acceptance.** Exact availability/geometry plus full net value including missed retracements; drawing RR is not fill evidence.
10. **Ablation/fallback/resources.** Confirmation, retracement and stop geometry independently. Failed sequence expires/updates belief; does not imply mandatory opposite trade. Class E/A, small bar/state buffer.

## R19 — Response-to-action and residual-management adapter

1. **Purpose/sources.** Prevent excellent pattern classification from hiding destroyed trade value; user C/L scope, RFE-05, SRE-05, K18/NYA trailing distinctions.
2. **Inputs.** Frozen initial opportunity and every R prefix timestamp, contemporaneous executable price/costs, updated target room, position/budget and G06/07 forecasts.
3. **Definition.** At each observable prefix compare act now, wait for next stage, use deeper limit, cancel or abstain; after entry compare P03 hold/exit/protect. Recompute payoff from actual candidate entry and remaining horizon, not original ideal entry. Optional Response can filter, refine timing or manage exit independently. Binding local refinement: [SR-R19](../SYSTEM_REFINEMENT.md#sr-r19).
4. **Outputs/labels.** `VALUE` per feasible prefix/action with non-fill, missed-move and delay distributions, linked to common initial candidate ID.
5. **Dependencies.** R01–18/20–21 provide causal observations/compatible forecasts. The augmented variant uses frozen baseline G forecasts and one ordered R19→augmented G06/07/08 pass, with distinct forecast IDs and no feedback to baseline producers. P01–06 retain action/execution/management; no duplicate OMS/risk.
6. **Comparators.** Direct C/L, simple price confirmation, individual Response stages, calibrated residual-value model; sequence transformer not required. Binding further upgrade and child comparisons: [UP-R19](../UPGRADE_PATHS.md#up-r19).
7. **Learning.** OOF upstream states/forecasts, complete candidate population and nested policy selection. Counterfactual values remain simulation-dependent.
8. **Tests.** T-R19: confirmation after target, non-fill, changed spread, daily stop while waiting, reversed target room and signal arriving before receipt.
9. **Acceptance.** Paired whole-day net/risk plus decomposition into rescued losses, lost winners, entry shortfall and management gain. Classification-only improvement rejected for promotion.
10. **Ablation/fallback/resources.** Entry refinement versus exit refinement separately; absent Response leaves validated C/L policy eligible. Class E/B/D, event-level replay dominates training.

## R20 — Pine structural and oscillator timing hypotheses

1. **Purpose/sources.** Preserve MVF, OSF, PIN071/072 and other Pine sweep/CISD/FVG/divergence mechanisms as distinct benchmark children, not an undifferentiated confirmation vote.
2. **Inputs.** Exact member-specific OHLC/volume/HTF inputs and causal completion times from traceability; actual ticks for economics. Drawing controls must not affect numeric state.
3. **Definition.** Register member-specific children for standard/expansive/pro-trend sweeps, silver-window variant, opposite-candle-run CISD, pivot-confirmed zones, FVG/volume-imbalance geometry, oscillator pivot divergence, inside/outside-bar close breaks and PIN005 repair/fork/cross-section patterns. Preserve the exact source row’s candle inequalities, thresholds, formation time and mitigation rules; similarly named variants are not merged without a paired comparison. Use source formulas recorded in PIN findings, correct explicitly identified availability/reset/arithmetic defects in a separately named causal variant. Do not invent unseen source tails. Binding local refinement: [SR-R20](../SYSTEM_REFINEMENT.md#sr-r20).
4. **Outputs/labels.** Variant ID, observed stage/confirmation and target-specific path/value forecasts; retrospective plot location distinct from known_at.
5. **Dependencies.** F09/M08, L08–10, C clocks; R19 tests timing increment beyond causal location itself.
6. **Comparators.** Faithful computable source, corrected causal rule, continuous feature/statistical model; learned sequence only with registered incremental hypothesis. Binding further upgrade and child comparisons: [UP-R20](../UPGRADE_PATHS.md#up-r20).
7. **Learning.** Fold-only pivot widths/time windows and threshold tuning; retain identical-value consecutive HTF bars, unresolved confirmations and parameter search count.
8. **Tests.** T-R20: lookahead-on unfinished HTF, backplotted pivot, missing reset, same-price consecutive candles, clock mismatch, display toggle dependence and truncated source.
9. **Acceptance.** Semantic correctness first, then common-cohort predictive/economic evidence and density/time placebos. Known leaky source is benchmark illustration only, never live candidate.
10. **Ablation/fallback/resources.** Each child separately scored; source branch not replicable remains unresolved rather than guessed. Class E/A/B, shared bars and compact states.

## R21 — Context-conditioned sequence alternatives

1. **Purpose/sources.** Preserve AUT-06, CCS-08, OBT-07/08, JTR transitions and competing HTF/LTF interpretations.
2. **Inputs.** OOF C auction/day-prefix/event forecasts, O21 exposure uncertainty, L hierarchy and R stage states, all from same information cut.
3. **Definition.** Common-target mixture weights different sequence experts by current context and coverage. Balance fade, directional break/retest, local pullback within HTF continuation and transition failure remain separate. Hard HTF alignment/long-gamma-balance/short-gamma-OFM gates are source comparison policies, not facts or requirements. Binding local refinement: [SR-R21](../SYSTEM_REFINEMENT.md#sr-r21).
4. **Outputs/labels.** Calibrated shared path/value distribution, expert weights/disagreement and missingness; no averaging of unrelated pattern classes.
5. **Dependencies.** G01/03/09 mixture contracts; R19 consumes compatible forecasts. Context can update after observed failure rather than preserve a fixed thesis indefinitely.
6. **Comparators.** Source hard gates, uniform mixture, regularized soft gate and shallow interaction model. Binding further upgrade and child comparisons: [UP-R21](../UPGRADE_PATHS.md#up-r21).
7. **Learning.** OOF forecasts, same-date splits, calibration after combination; no eventual day-type labels used as gate inputs.
8. **Tests.** T-R21: intraday regime transition, conflicting gamma scenarios, all experts missing, hard-gate missed opportunity and correlated duplicate evidence.
9. **Acceptance.** Conditional calibration, expert collapse/diversity diagnostics and complete economic improvement over direct C/L and simple Response.
10. **Ablation/fallback/resources.** Remove each context source, compare soft versus hard alignment; fallback validated available-data mixture or C/L. Class E/B, small gate plus shared specialists.

## R22 — Blinded visual/source annotation and mechanism adjudication

1. **Purpose/sources.** Retain diagram detail without treating annotated screenshots as fills or identities; SRE-04, OFM-04/06, F23-03, AUT-07 and full source findings.
2. **Inputs.** Immutable source/page ID, as-of replay snapshot with future hidden, numerical feature/event log and optional authorized human annotations. Screenshot time, scale and instrument uncertainty explicit.
3. **Definition.** Annotation schema records visible geometry, observable sequence stage, label uncertainty, claimed mechanism and contradiction separately. Two blinded annotations/adjudication on a stratified sample test definitional reliability; no performance label recovered from a pending order drawing. Human intent/identity narratives remain hypothesis text. Binding local refinement: [SR-R22](../SYSTEM_REFINEMENT.md#sr-r22).
4. **Outputs/labels.** Versioned annotation dataset with provenance, agreement and unresolved fields. Future market/economic labels come from numeric replay, not annotator recollection of winners.
5. **Dependencies.** V01 label definitions/F10 snapshots and each R specification; used to refine definitions before detailed model work, not as required live human gate.
6. **Comparators.** Numeric rule annotation, blinded human agreement, optional image-assisted extraction audited against structured data; no LLM authority over exact prices/side. Binding further upgrade and child comparisons: [UP-R22](../UPGRADE_PATHS.md#up-r22).
7. **Learning.** Separate annotation-development examples from frozen evaluation; selected source illustrations cannot represent deployment prevalence.
8. **Tests.** T-R22: swapped dates, open versus realized P&L, image/caption sign conflict, cropped legend, revised bracket and future chart portion.
9. **Acceptance.** Report agreement/error by field and unresolved scope; no invented minimum reliability score. Material ambiguity resolved or modeled as alternatives before promotion.
10. **Ablation/fallback/resources.** Numeric-only versus annotation-assisted research; missing source pixels/hidden formulas remain unavailable. Class E/D, modest curated artifacts; no demand for unprovided videos to complete current plan.
