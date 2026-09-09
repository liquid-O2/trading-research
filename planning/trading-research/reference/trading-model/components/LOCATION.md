# Location: causal objects and opportunity generators

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
[Common contracts](COMMON_CONTRACTS.md) apply. A location is a versioned market object with geometry, formation/availability, possible roles, uncertainty and lifecycle—not a guaranteed reversal line. Every family below is independently benchmarked and scored. Shared learned reach/path/payoff/selection functions are G04–G08; each family also has an independently measured role forecast so failures remain attributable.

## Shared location geometry and lifecycle

Store `geometric_band`, `estimation_uncertainty`, `mapping_uncertainty` and `entry_tolerance` separately. A source line is a point object; initial executable contact tolerance is a registered one-tick/half-spread alternative, not a retrospective enlarged zone. A mapped object uses the scenario distribution from X02; test conservative union and calibrated quantile bands, matched for width in placebos. Labels attach to the frozen band at decision time. Later revisions create new forecast versions and cannot make a prior miss into a hit.

A new object needs a causal anchor and an explicit formation-completion rule. A contact is a trade/declared price observation entering its band; a gap over it is separate. A sweep is breach+reclaim; acceptance requires declared time/volume/close evidence. Invalidation and expiry are distinct. Register all active/invalidated/rejected candidates. No source-only, small, internal or non-confluent object is categorically excluded. Action plans must have a feasible full-position invalidation/stop, target/horizon, current receiver price and risk/cost estimate before G/P can authorize an order.

## L01 — Internal range quarters, EQ and range-open locations

1. **Purpose/sources.** Preserve internal entries, including continuation without gamma; JTR-02/06/07/11, JXA-06/13/23, DRF-U07/11.
2. **Inputs.** C01 completed/provisional range with availability, C02 break/reclaim order, C03/04 path forecast and current price. Separate 06–09, prior-RTH and other source window IDs; decision updates.
3. **Definition.** Generate `L+.25W`, `L+.5W`, `L+.75W`, range open and source-specific open separately. Assign possible reversal/continuation/target roles from observed path, width/prior value/sweeps and remaining room. Wide single-break internal→edge differs from compressed/purged internal→extension continuation. No mandatory range-edge first touch. Binding local refinement: [SR-L01](../SYSTEM_REFINEMENT.md#sr-l01).
4. **Output.** Point/band objects and side/role proposals with parent range, frozen geometry and `REACH/DEPART/PATH` targets. Incomplete range is provisional and cannot use final future extremes.
5. **Dependencies.** C01–04/C19/F10; G04–08/P; R optional refinement.
6. **Comparisons.** Faithful quarter/EQ rules; conditional-frequency/logistic role model; boosted contextual role/ranker. Compare internal roles separately from extension roles. Binding further upgrade and child comparisons: [UP-L01](../UPGRADE_PATHS.md#up-l01).
7. **Training.** All internal candidates, including no-touch; OOF Context forecasts, nested width/role thresholds. Never select the day's best quarter after seeing its path.
8. **Tests.** Inside-EQ continuation, EQ reversal with later failed extension, wide range limited room, range open≠EQ, no gamma and future-final range.
9. **Acceptance.** Geometry/causality exact; reach/path calibration and net value above equally dense internal placebo grid and simple range benchmark.
10. **Ablation/fallback/resources.** Quarter/EQ/open individually, Context role, prior-RTH/6–9 distinction, Response required/on-off comparison. Fall back unranked benchmark or no action. Class A/B small object count.

## L02 — Range edges and edge-relative extensions

1. **Purpose/sources.** Preserve edges, half/full extensions and R/R region alternatives; JTR-05/12/21/22, JXA London/P-zone cases, PIN grids.
2. **Inputs.** C01 range and source projection convention, C02 path, C06/19 excursions/room and current price. At range freeze and contextual revisions.
3. **Definition.** Edges H/L; projections H+kW/L−kW for source k=.5,1,1.33,1.66,2,3,4 and other disclosed benchmark ratios. Maintain source ratio semantics; normalized internal x=1.33 is not upper edge+1.33W. 1.33–1.66 can support partial retrace/continuation or full reversal; predict role rather than hardcode fade. Binding local refinement: [SR-L02](../SYSTEM_REFINEMENT.md#sr-l02).
4. **Output.** Extension objects/regions, source ratio, reach/departure/target role distribution and invalidation/horizon. Far unreachable node remains logged, not removed from denominator after failure.
5. **Dependencies.** C01/02/06/19/F10; G04–08/P.
6. **Comparisons.** Faithful projection rule and nearest/strongest selection; conditional logistic/survival model; boosted interaction/learned width/role. Compare source fixed ratios against learned excursion quantiles L04. Binding further upgrade and child comparisons: [UP-L02](../UPGRADE_PATHS.md#up-l02).
7. **Training.** Ratio search train-only, multiplicity counted, no favorable density expansion on test. Include no-reach and gap-cross outcomes.
8. **Tests.** W100 edge+133, upper/lower mirror, extension touched but no reversal, partial retrace then−4, statistical bound not hard cap and coarse-bar jump over zone.
9. **Acceptance.** Exact projection fixtures and source geometry; reach/path/calibration and sequential utility versus matched-distance extension placebos.
10. **Ablation/fallback/resources.** Each ratio/region, Context, width scaling and room; fallback source fixed grid with conservative selection. Class A/B.

## L03 — Previous-RTH and full-session structure

1. **Purpose/sources.** Preserve Jumbo's separate prior-RTH framework and broader-session challenger; JTR-21/22, JFN-04/08/10, JXA profile charts.
2. **Inputs.** Completed prior RTH high/low/open/close and M04/05 value/delta profiles, full-session equivalents, current C04 open state and overnight sweep history. Activate only after prior formation completes.
3. **Definition.** Generate prior-RTH extrema/value references with their true 09:30–16:00 NY anchor; source faithful variant disregards ETH sweep when deciding RTH target freshness. Challenger tracks ETH touches/reclaims without globally erasing the object. Keep current 06–09 inner references and prior-RTH outer references distinct; optional source M15/H1 imbalance objects route L09. Binding local refinement: [SR-L03](../SYSTEM_REFINEMENT.md#sr-l03).
4. **Output.** Prior-session objects with untouched/swept/reclaimed state under each declared interpretation and contextual target/entry role forecasts.
5. **Dependencies.** M04/05/12/C01/04/F10; G/L interactions and P target construction.
6. **Comparisons.** Faithful RTH-only rule; full-session touch-aware model; logistic/boosted state-conditioned roles. Do not replace source anchor with rolling VP. Binding further upgrade and child comparisons: [UP-L03](../UPGRADE_PATHS.md#up-l03).
7. **Training.** Same-date paired RTH/ETH alternatives, OOF context, all prior references. Session completion/holiday rules explicit.
8. **Tests.** ETH sweep then RTH retest, prior VAH inside prior full range, RTH high differs from6–9 high, shortened session and contract roll.
9. **Acceptance.** Source chart anchor parity plus causal state; economic increment over simple previous high/low and matched density controls.
10. **Ablation/fallback/resources.** RTH/ETH, value/delta, overnight freshness and inner/outer hierarchy. Missing profile preserves known range only. Class A/B.

## L04 — Statistical bounds and improved P-zones

1. **Purpose/sources.** Turn richer conditional forecasts into locations while retaining undisclosed-formula uncertainty; JSS, JXA-19/22, JFN-07, C06/PIN statistical families.
2. **Inputs.** C06 calibrated excursion/joint-path distributions, C01 anchor, observed prefix, M04/05 topology and O/X scenarios if supported. Formation and predefined minute revisions.
3. **Definition.** Candidate centers/bands from registered excursion quantiles/density modes or expected overshoot beyond anchor edges. Distinguish open-relative future high/low, formation-range mean±SD, close-offset SD and edge extension; never collapse their units/denominators. Compare free statistical zone, snapped-to-profile/node and soft distance-to-node feature. Keep geometric support, forecast-estimation uncertainty, mapping uncertainty and entry tolerance separate; any combined contact region has an explicit scenario/coverage definition, not an automatic addition of widths. No invented proprietary P-zone formula. Binding local refinement: [SR-L04](../SYSTEM_REFINEMENT.md#sr-l04).
4. **Output.** Statistical objects with distribution/quantile/anchor provenance, coverage and possible reversal/continuation/target roles; reversal probability comes from G05, not quantile level.
5. **Dependencies.** C06/C19/M/O/X/F10; G04–08/P.
6. **Comparisons.** Source disclosed mean/median/SD geometry; conditional quantile linear/GAM; boosted distribution/learned density with fold-local zone selection. Undisclosed source components remain hypothesis benchmarks, not exact replications. Binding further upgrade and child comparisons: [UP-L04](../UPGRADE_PATHS.md#up-l04).
7. **Training.** Quantile/zone count/width/snap selected inner folds, OOF forecasts; all candidates and no-reach included. Don't choose comparables by today's final volume/volatility.
8. **Tests.** Bear upper/lower swap, current-inclusive mean, quantile crossing, too-wide zone raising hit rate, low-vol unreachable mean, and expected high versus future extension distinction.
9. **Acceptance.** Forecast coverage and calibrated response; utility above matched-width/density/distance placebo and fixed range extensions. Better touch rate alone fails.
10. **Ablation/fallback/resources.** Conditional versus pooled, mean/median/tails, volume/IV and snapping. Fall back seasonal fixed distribution. Class B, reuse C06 outputs.

## L05 — Volume-profile value, nodes, shelves and valleys

1. **Purpose/sources.** Preserve full auction/profile location family; VP2/MAV/RVP/MAT, Jumbo VP/delta emphasis, SKY090 and PIN VP audits.
2. **Inputs.** M04 exact trade profile at each declared anchor, C07/08 auction/migration state, price path and coverage. Developing and completed versions distinct.
3. **Definition.** Generate POC, VA edges, local HVN/LVN/valley/shelf boundaries, multimodal separators and composite references. Use explicit smoothing/prominence/min-volume choices; retain unsmoothed baseline. A valley suggests lower historic traded volume, not necessarily current thin order-book liquidity. POC can be target or transition reference; no blanket ban inherited from prior assistant. Binding local refinement: [SR-L05](../SYSTEM_REFINEMENT.md#sr-l05).
4. **Output.** Profile objects with row membership/anchor, geometry, mass/prominence, age and contextual role forecast. Retests reference frozen versions.
5. **Dependencies.** M04/C07/08/F10; G04–08/P. Correlated POC/VA/HVN evidence linked by L18.
6. **Comparisons.** Source profile rules/POC-VA only; statistical role model; KDE/online density and multichannel profile encoder. True trade versus bar allocation compared on same dates. Binding further upgrade and child comparisons: [UP-L05](../UPGRADE_PATHS.md#up-l05).
7. **Training.** Bin/smoothing/prominence inner-only; equal candidate density/width in key tests; profile completion causal and current viewport fixed algorithmically.
8. **Tests.** Bimodal profile, empty valley, low-volume tail, POC tie, same-price different anchor, developing node moves after entry and true/bar allocation discrepancy.
9. **Acceptance.** Profile mass/identity fixtures, stable locations to bin perturbation, predictive/economic value over random density-matched shelves and raw high/low grid.
10. **Ablation/fallback/resources.** Each location type, anchor, volume weights/migration and true/proxy profile. Missing profile yields no family candidate. Class A/B sparse peak extraction.

## L06 — Delta-profile and side-concentration locations

1. **Purpose/sources.** Keep delta-location logic distinct from total volume and later control inference; RDL/CRL-06/13, JFN-08, user delta-profile requirement.
2. **Inputs.** M05 buy/sell/unknown/cohort profiles on exact source anchors, M10 effort-progress, C18 and current price. Event/decision updates.
3. **Definition.** Generate positive/negative delta peaks, side-weighted centers, opposing-side shelves and delta/volume transition regions. Source 'winning/trapped/protected' interpretation requires subsequent observed price behavior and is a separate state, not a label inferred from delta sign. Signed density handled as side channels; no automatic cancellation of two meaningful opposing shelves. Binding local refinement: [SR-L06](../SYSTEM_REFINEMENT.md#sr-l06).
4. **Output.** Side-concentration objects, sign/mass/unknown uncertainty, observed protection/reclaim history and role forecast.
5. **Dependencies.** M05/10/11/C18/F10; G05–08 and R reading-delta branches; L19 handles discrete large-print memory separately.
6. **Comparisons.** Total-volume nodes, source bar-delta shelf, actual delta peaks, conditional logistic/boosted side-role model and multichannel profile representation. Binding further upgrade and child comparisons: [UP-L06](../UPGRADE_PATHS.md#up-l06).
7. **Training.** Prior-volume normalization, train-only peak threshold; include failed/untouched shelves and OOF context. Future markout cannot determine birth.
8. **Tests.** Large positive delta later loses, equal total VP/different delta, unknown-heavy profile, opposing peaks, protected level known only after test and price crosses shelf before formation completes.
9. **Acceptance.** Side/mass correctness and causal protection; incremental economic/path value beyond L05 with sign-shuffle and density-matched nulls.
10. **Ablation/fallback/resources.** Sign/cohort/protection/history and total-VP combination; fallback L05 if sign unsupported. Class A/B sparse profile channels.

## L07 — TPO, initial balance, single prints and auction tails

1. **Purpose/sources.** Preserve TPO/IB hypotheses even where a source dismisses them; TP3/MAV, JXA-05, SKY091, PIN weekly IB.
2. **Inputs.** M06 bracket profiles, completed first bracket/hour/weekly initial balance as individually defined, current path and session calendar. Availability at completion/confirmation.
3. **Definition.** Generate TPO POC/VA, single-print/tail zones, excess/poor-extreme proxies, naked prior POC and IB high/low/mid/extensions. A poor extreme requires a declared observable bracket/row criterion; no unobserved auction-completion certainty. Weekly IB source window differs from daily IB and is a separate object. Binding local refinement: [SR-L07](../SYSTEM_REFINEMENT.md#sr-l07).
4. **Output.** TPO/IB objects with bracket counts, confirmation and unfilled/touched state, role forecasts and incomplete-data masks.
5. **Dependencies.** M06/C07/F10; G/P. Source Atlas next-session-display behavior is a separate benchmark from earliest valid confirmation.
6. **Comparisons.** Source bracket rules; empirical conditional traversal/return; logistic/survival/boosted role model. Compare TPO versus exact dwell versus volume profiles. Binding further upgrade and child comparisons: [UP-L07](../UPGRADE_PATHS.md#up-l07).
7. **Training.** Bracket/grid/minimum-count choices inner folds; no future session shape/single-print status. Unfilled/naked evaluated only since object birth.
8. **Tests.** Single print later filled before close, IB break after known hour, weekly partial holiday, naked POC touched on next open, OHLC gap falsely filling rows.
9. **Acceptance.** Correct bracket/confirmation and role calibration; incremental utility over L05 and matched-price grid, not presumed IB edge or presumed absence of edge.
10. **Ablation/fallback/resources.** IB/TPO/tails, bracket length, exact visits and naked-state history. Missing bracket coverage blocks dependent object. Class A/B.

## L08 — Swing, retracement and dynamic-range locations

1. **Purpose/sources.** Preserve look-left swings, swing midpoints and dynamic fibs distinct from static time-range extensions; JXA-16/20, CRL-06, OSF and Pine fractals.
2. **Inputs.** M08 confirmed/provisional swing graph, causal leg high/low/open, C path and prior vol; per confirmation and decision updates.
3. **Definition.** Generate confirmed swing extrema, `L+fW` retracements and directional leg extensions with exact parent-leg identity; source Fibonacci ratios and ordinary .25/.5/.75 are separate benchmarks. Provisional running-leg objects explicitly move; confirmed objects do not acquire earlier availability when backplotted. Tick/volatility reversal anchors compete with fixed left/right pivots. Binding local refinement: [SR-L08](../SYSTEM_REFINEMENT.md#sr-l08).
4. **Output.** Swing/leg objects, confirmation delay, geometric role and conditional path forecast; no future-selected anchor.
5. **Dependencies.** M08/C03/07/F10; G/P and R structure timing.
6. **Comparisons.** Source fractal/fib rule; fixed move/vol-scaled swing; logistic/boosted role model and bounded learned offset proposal. Model must account for confirmation cost. Binding further upgrade and child comparisons: [UP-L08](../UPGRADE_PATHS.md#up-l08).
7. **Training.** Pivot/reversal/ratio choices inner folds; all eligible legs including unresolved trends; OOF upstream forecasts and horizon-aware purging.
8. **Tests.** Equal highs, nested swing, late confirmation, no reversal in trend, leg replacement, log-price versus arithmetic fib and roll artifact.
9. **Acceptance.** Prefix availability, stable geometry and utility over matched-distance/age swing placebos and simple running extrema.
10. **Ablation/fallback/resources.** Confirmed/provisional, ratio, anchor scale and Context. Missing confirmed swing may retain separately labelled running-extreme candidate. Class A/B.

## L09 — FVG, imbalance and displacement-origin zones

1. **Purpose/sources.** Preserve source FVG/VI/imbalance families with exact causal formation; JTR-21/22, OSF, PIN sweep/FVG variants and CRL.
2. **Inputs.** Final multi-timeframe bars F09/M08, source-specific gap/overlap rules and actual trade/footprint M13 when volume imbalance is claimed.
3. **Definition.** Standard bullish three-bar FVG exists when bar3 low>bar1 high after bar3 closes; bearish mirror. Zone is between those bounds, with mid/edge and partial/full fill states. Keep body-gap/overlap ('VI' in some Pine) separate from measured volume imbalance; CISD-associated displacement zones reference confirmed originating sequence R20, not future swing extremes. Multi-timeframe values keyed by bar identity, not value-change alone. Binding local refinement: [SR-L09](../SYSTEM_REFINEMENT.md#sr-l09).
4. **Output.** Zone object with formation bars/time, wick/body/volume type, mid/edges, fill/flip/invalidation history and role forecast.
5. **Dependencies.** F09/M08/13/F10; G/P and R sequences. Higher-timeframe completion required even if chart draws zone earlier.
6. **Comparisons.** Exact source rule; gap-size/age/path logistic model; boosted zone-role model and true footprint imbalance challenger. A price gap is not proof institutional inefficiency. Binding further upgrade and child comparisons: [UP-L09](../UPGRADE_PATHS.md#up-l09).
7. **Training.** Minimum gap/displacement/timeframe and mitigation definitions registered inner folds; no last-1000-chart-bars or display toggle changing the economic universe.
8. **Tests.** Identical consecutive HTF OHLC, future HTF leak, partial/full fill, inverse/flip zone only after observed break, price-only VI versus volume imbalance and same-bar formation/contact.
9. **Acceptance.** Exact source causal fixtures, no duplicate/repaint zones, calibrated role and economic value above gap-size/density-matched placebos.
10. **Ablation/fallback/resources.** Wick/body/volume, timeframe, displacement, mitigation/flip and source sequence. Incomplete bar yields no final zone. Class A/B bounded active zones.

## L10 — Order-block and rejection-block entry regions

1. **Purpose/sources.** Preserve the source's distinct entry/stop alternatives and drawing-caption conflict; JTR-16/17, OSF/PIN order-block mechanisms.
2. **Inputs.** Known candle/sequence and sweep confirmation, M08 structure, C/L context; source 2/3/5-minute variants with exact completion times.
3. **Definition.** Operational sweep-confirmation baseline: bullish `L2<L1` followed by completed `C3>H2`; bearish `H2>H1` then `C3<L2`. This makes “closes above/below candle two” explicit. Because the original grey order-block drawings do not publish complete numerical boundaries, register candle-two full range and O/C body as separately named geometric interpretations, not claimed identical reproductions. For each, compare confirmed entry with midpoint stop, confirmed entry with extreme stop, and midpoint retracement entry with extreme stop. Rejection block uses the swept lower/upper wick; midpoint-stop versus wick-extreme-stop remains separate due caption/drawing conflict. Other Pine variants retain member-specific definitions. Binding local refinement: [SR-L10](../SYSTEM_REFINEMENT.md#sr-l10).
4. **Output.** Confirmed region and feasible entry/stop alternatives, delay/non-fill risk, invalidation/time expiry and role forecast.
5. **Dependencies.** M08/F09/F10, R18/R20 later richer structure, G/P. Fine confirmation is optional for other Location families, mandatory only to call this particular object confirmed.
6. **Comparisons.** Exact source sequence; simple conditional-frequency/logistic role; boosted/temporal quality score. Compare entry alternatives after actual confirmation price and midpoint non-fills. Binding further upgrade and child comparisons: [UP-L10](../UPGRADE_PATHS.md#up-l10).
7. **Training.** Source variants/stop interpretations registered, OOF Context, all formed blocks not only winners. No hindsight best stop or post-formation low redefining original risk.
8. **Tests.** Sweep without confirmation, delayed third close, midpoint not revisited, stop caption conflict, same-bar entry/stop ambiguity and wick versus body geometry.
9. **Acceptance.** Semantic/causal parity and conservative fill/P&L; compare against simple price confirmation and matched candle regions. High R:R alone is not acceptance.
10. **Ablation/fallback/resources.** Entry/stop alternatives, sweep/close conditions, contextual quality and timing. No confirmed region means no L10 object. Class A/B/E later sequences.

## L11 — VWAP and anchored-dispersion locations

1. **Purpose/sources.** Preserve RTH/ETH/anchored VWAP and2/2.5σ ideas; VW10, CRL-06, SKY088, PIN069.
2. **Inputs.** M07 exact/proxy VWAP/bands, anchor/coverage, C07 auction state and C19 room; per trade/decision or minute publication.
3. **Definition.** Generate VWAP, source SD/percentage bands and causal anchor-specific lines; distinguish mean reversion, acceptance/cross/retest continuation and targets. Dynamic lines create versions at prediction cuts. An exit/target can deliberately track updated VWAP only under a declared management policy; labels of a frozen level do not silently move. Binding local refinement: [SR-L11](../SYSTEM_REFINEMENT.md#sr-l11).
4. **Output.** Price/dispersion objects with units, anchor, dynamic/frozen status and conditional role/path distributions.
5. **Dependencies.** M07/C07/19/F10; G/P. GEX strike center remains L14/O17.
6. **Comparisons.** Source band touch/hold rules, historical conditional model, logistic/survival/boosted contextual role; true trade VWAP versus bar proxy and robust quantile bands. Binding further upgrade and child comparisons: [UP-L11](../UPGRADE_PATHS.md#up-l11).
7. **Training.** Anchor/band choices and retest definition inner folds; no future swing anchor or first-postsession-close target leak. All crossings/no-touches included.
8. **Tests.** Reset jump, first retest versus repeated cross, moving target, zero volume, RTH versus ETH, index borrowed-volume proxy and final-session bar skipped.
9. **Acceptance.** Exact moment/availability; incremental utility above comparable moving average and matched-distance bands under same execution rules.
10. **Ablation/fallback/resources.** Anchor, dispersion, k, slope, exact/proxy volume. Missing VWAP no candidate; class A/B reuse M07.

## L12 — Opens, settlement, gaps and reference-price locations

1. **Purpose/sources.** Preserve distinct reference levels and return-to-open setups; CRL-06, PIN gap/opens/retracement families, C21; EXT-078 print-reference hypotheses are a separately deferred `L12.PRINT` child.
2. **Inputs.** M12 published settlement and named opens/closes/gap measurements, prior known session shape, C21 transition forecast. All supported sessions/assets. L12.PRINT requires certified X08.TRF receipt/correction data; the current acquired archive does not establish it.
3. **Definition.** Generate official settlement, previous close/open, day/week/month opens, gap boundaries and source open-to-open fractional targets `(1−f)O_action+f O_reference`. Preserve source body25 versus range-quarter alternatives. Gap fill/hold/continuation roles are conditional; no fixed assumption all gaps fill. Futures contract roll gaps excluded or separately labelled. L12.PRINT births an unsigned price-reference object only when an eligible print is received, never at an earlier event time or from a later daily ranking. Preserve single-print versus causal same-price-window cluster identities. Width starts at one source tick; volatility/spread/mapping-aware alternatives are frozen trials. Freeze 5/15/60-minute or session-end expiry at birth; corrections append invalidation/revision, and cluster updates create versions. A print shows a reported trade price, not guaranteed support/resistance; distant source prices require X02 related-coordinate mapping or X05 predictive transmission rather than arbitrary level conversion. Binding local refinement: [SR-L12](../SYSTEM_REFINEMENT.md#sr-l12).
4. **Output.** Reference objects, publication/anchor IDs, direction-neutral geometry, touch/reclaim/expiry state and path forecast. L12.PRINT retains source/receiver coordinates, receipt lag, mapping uncertainty and direction-neutral touch/departure labels; no inferred trade-side role.
5. **Dependencies.** M12/C17/21/F10; G/P. Unknown official settlement remains unavailable rather than replaced with a different reference under its name. L12.PRINT is unavailable unless X08.TRF passes its separate acquisition/coverage gate; F10 preserves correction lineage.
6. **Comparisons.** Source fixed clock/fraction rules; shrunken conditional gap/return frequencies; survival/boosted role model. Compare print price, round-number/prior-price and time/distance/size-matched placebo references; use simple conditional frequencies before a learned print-role model. Binding further upgrade and child comparisons: [UP-L12](../UPGRADE_PATHS.md#up-l12).
7. **Training.** All eligible days and no-hit censored outcomes; freeze fraction/check-window and previous-trading-day logic; no current-day stale reference carried from yesterday. For print objects use complete causal candidate sets, train-only size/cluster thresholds and date-grouped OOF; no retrospective largest-print selection.
8. **Tests.** 00/08 timezone difference, faulty07–05 source string, late settlement, Friday/Monday, open above previous range, no opening trade and gap jump over price; delayed/corrected print, same-price cluster revision, daily-rank lookahead and unavailable mapping fixtures for L12.PRINT.
9. **Acceptance.** Reference parity and calibrated conditional outcomes/economic utility versus simple round-number/previous-close benchmark. Print-derived objects must separately improve reach/path/value after actual receipt delay and costs; selected chart examples do not establish utility.
10. **Ablation/fallback/resources.** Reference type/fraction/window, calendar/transition conditioning and gap sign. Fallback valid raw reference only; class A/B. L12.PRINT separately ablates size, width, horizon, clustering and receiver transmission, and falls back to no print object when data are absent.

## L13 — Options concentration nodes mapped to execution

1. **Purpose/sources.** Make individual/per-expiry options nodes actionable for NQ/ES; user NDX preference, DRF-U03/07/09, O11/O22.
2. **Inputs.** O11 node object, O22 role/path forecasts, X02 mapping/scenarios, receiver current price and C19 room. Every supported chain/expiry and minute revision.
3. **Definition.** Map source node center/band with explicit uncertainty; retain local receiver and source coordinate separately. Candidate sides/targets depend on observed context/role; small nodes remain eligible. Use density/coverage-preserving node universe; no top2/king-only ceiling. Unknown precise cash touch means proxy-supported mapping, not fabricated source event. Binding local refinement: [SR-L13](../SYSTEM_REFINEMENT.md#sr-l13).
4. **Output.** Mapped node object/opportunity with chain/expiry/Greek/holdings scenario, reach/path/value inputs and mapping age. Uncertain mapping can make zone too broad to trade and must be reported.
5. **Dependencies.** O11/21/22/X02–04/C19/F10; G/P. Cross-index source-only opportunities are L15.
6. **Comparisons.** Static prior-OI nearest/strongest node, mechanically repriced nodes, learned OI/dynamics, direct O22 path model and context-conditioned role. Same supported sample/candidate-density comparisons. Binding further upgrade and child comparisons: [UP-L13](../UPGRADE_PATHS.md#up-l13).
7. **Training.** OOF upstreams, nested node/width thresholds, frozen mapping, no hindsight best expiry selection. Keep no-reach and invalidated versions.
8. **Tests.** NDXP versus QQQ, SPXW versus SPY, small node wins, largest too far, map drift, expiry changes, missing wing and no local gamma confirmation.
9. **Acceptance.** Unit/coordinate/availability, calibrated reach/path and conservative one-mini net increment over price-only and matched-strike/placebo objects.
10. **Ablation/fallback/resources.** Each chain/expiry/Greek/holdings/dynamics/mapping uncertainty, observed-only universe. Fall back supported static node or no object. Class B/C shared board/map cache.

## L14 — Exposure centers, bands and topology corridors

1. **Purpose/sources.** Preserve Atlas GEX VWAP and multi-node corridors as locations; SKY087/015–020, O13/O17, user actionable options levels.
2. **Inputs.** O17 centers/envelopes, O13 ordered node topology, optional O23 max-pain minimizer set, X02 mapping and C19 opportunity budget. Per valid board/report snapshot; max-pain intervals retain their own formula/expiry identity.
3. **Definition.** Generate exposure-weighted center/upper/lower bands, opening envelopes and bounded corridors between meaningful nodes. Corridor midpoints are eligible hypotheses despite vendor blanket midrange-avoidance language. Width/domain follow observed topology and uncertainty; source projection beta formula undisclosed, so own excursion/corridor forecast is explicitly a new model. Binding local refinement: [SR-L14](../SYSTEM_REFINEMENT.md#sr-l14).
4. **Output.** Composite options-location objects with constituent-node lineage and target/reversal/continuation role forecasts. No multiple independent votes from one board-derived corridor and its nodes.
5. **Dependencies.** O13/17/21 and optional O23, X02/F10; G/L18/P. O23 minimizers are a distinct benchmark location type, not silently merged with a GEX-weighted center or a guaranteed attraction target.
6. **Comparisons.** Source center/envelope, simple node midpoint/nearest corridor, conditional logistic/quantile role and graph/set context. Compare against ordinary VWAP and random compatible corridors. Binding further upgrade and child comparisons: [UP-L14](../UPGRADE_PATHS.md#up-l14).
7. **Training.** Expiry/filter/envelope/corridor selection inner folds, OOF forecasts; opening envelope unavailable until required observations. No visual radius input.
8. **Tests.** Center not spot, threshold fraction not percentile, opposing nodes, empty side, changing expiry selector, early envelope use and node/corridor duplicate evidence.
9. **Acceptance.** Formula/lineage and causal formation; predictive/economic gain above constituent nodes alone with density/width control.
10. **Ablation/fallback/resources.** Center/bands/envelope/corridor, expiry set and mapping. Missing board no object; class A/B/C reuse O17.

## L15 — Source-event receiver opportunities without local touch

1. **Purpose/sources.** Preserve core SPX/SPY→NQ observation and Context-originated action; DRF-U09/11, SKY020, C22/X05.
2. **Inputs.** X05 source-event forecast at known_at, receiver current BBO/path, C19 remaining room, independent risk and optional local structure. Native/interval-supported source event.
3. **Definition.** Form receiver opportunity at first actionable cut using current receiver price or a bounded pullback band, with invalidation from receiver structure/volatility and source-failure condition. Source-level touch is required only to name this source event; receiver need not touch a local mapped node. Compare immediate, pullback-wait and simple confirmation alternatives; none may use receiver movement already realized before source availability as future reward. Binding local refinement: [SR-L15](../SYSTEM_REFINEMENT.md#sr-l15).
4. **Output.** Source-linked receiver object/opportunity, no-local-node flag, stop/target/horizon alternatives, mapping-independent provenance and uncertainty.
5. **Dependencies.** X01/05/C22/C19/M08/F10; G/P, Response optional.
6. **Comparisons.** No source channel; source-return/simple event rule; calibrated regression/boosted transmission value model. Local-touch-required is an explicit ablation, not eligibility law. Binding further upgrade and child comparisons: [UP-L15](../UPGRADE_PATHS.md#up-l15).
7. **Training.** All source events including failed/no receiver response, OOF source forecasts, same-date grouping and interval-order ambiguity. No selected screenshot hindsight.
8. **Tests.** NQ turns before its own node, source fails, receiver already moved, late ETF minute, contradictory source event, no safe receiver stop and source outage.
9. **Acceptance.** Positive incremental executable value after source/receiver lag and conservative fills; fail if apparent lead exists only before event is knowable.
10. **Ablation/fallback/resources.** Local-touch condition, source-return versus level event, lag/date/placebo, immediate versus pullback. Missing source stops new L15 proposals. Class B/E sparse events.

## L16 — Learned location proposal and bounded price refinement

1. **Purpose/sources.** Improve dense generators and allow useful in-between prices without hindsight extremum selection; CRL-11/19, DRF-U10, MVF/OSF/PIN benchmarks.
2. **Inputs.** Causal price/volume/delta/option spatial features, active objects, C forecasts and coverage. Predefined decision cuts; all proposed locations logged.
3. **Algorithm.** Compare online KDE/DBSCAN-style positive/negative density peaks, fixed-grid conditional outcome density and learned proposal/offset model. Predict spatial distribution of future contact/departure utility on a bounded current-price-relative grid; constrain offsets to declared geometric/uncertainty neighborhood or issue a new generator object. Candidate count/width budget frozen; label map includes no-reach/unresolved, not just HOD/LOD. Geometry learned from training prefixes only. Binding local refinement: [SR-L16](../SYSTEM_REFINEMENT.md#sr-l16).
4. **Output.** Proposal objects with density/utility/width uncertainty, source parents or independent origin, known_at and rejection reasons. No claim every future extreme was actionable.
5. **Dependencies.** M04/05/11/O/C/F10/11 and existing base objects; proposal model parameters/outputs are fixed before current G04–08 scoring. A later refinement variant is a separate one-pass producer and cannot repeatedly use its own current score to move its geometry. Faithful generators remain comparators.
6. **Comparisons.** Fixed source/grid and nearest existing level; KDE/regularized grid regression; boosted offset/distribution model, profile CNN or set decoder. Complexity justified by better selected opportunity value, not coverage alone. Binding further upgrade and child comparisons: [UP-L16](../UPGRADE_PATHS.md#up-l16).
7. **Training.** Nested grid/bandwidth/count/normalization, same-date weighting and spatial negatives; OOF context. Avoid signed-weight density and hindsight optimal level labels as live targets.
8. **Tests.** Dense levels cover every extreme but rank poorly, outside-bound offset, cluster merge after prediction, current range scaling leak, no true contact and exact same candidate count placebo.
9. **Acceptance.** Proposal causal/width/count invariants; improved utility at matched density/width/distance and equal compute versus source families. HOD/LOD coverage alone fails.
10. **Ablation/fallback/resources.** Fixed versus learned location, all input families, offset/width/count and ranking held constant. Fall back to existing valid objects. Class B/C sparse spatial grids, no raw-tape neural expansion by default.

## L17 — Location lifecycle, retest and invalidation hazard

1. **Purpose/sources.** Improve deletion/freshness rules without erasing failures; JXA/JFN, OFM/TBR/SRE, O12, PIN stale-state defects.
2. **Inputs.** F10 object history, age/touches/sweeps/reclaims, displacement/volume/time, C state and O node revisions. Per object/event.
3. **Definition.** Deterministic registry events remain facts. Forecast remaining useful lifetime, next retest/hold/fail and transition from reversal reference to continuation/target. Compare first-touch-only, touch-count/time expiry, volume-decay and calibrated survival/competing-risk lifecycle. A failure does not automatically make repeated same-thesis entry rational; P04 per-idea budget governs it. Binding local refinement: [SR-L17](../SYSTEM_REFINEMENT.md#sr-l17).
4. **Output.** Lifecycle/path distributions and recommended active/limited/retired applicability, with rule version and uncertainty. Historic objects/outcomes always preserved.
5. **Dependencies.** F10/M11/C/O12; G09 applicability, G selection and P04/management.
6. **Comparisons.** Source delete-on-sweep/one-retest rules; shrunken retest hazard; survival/boosted/duration model. Retirement policy evaluated as an economic choice, not post-hoc data cleaning. Binding further upgrade and child comparisons: [UP-L17](../UPGRADE_PATHS.md#up-l17).
7. **Training.** Censor at data/boundary/expiry; repeated retests clustered by idea/date, OOF context; no future survival status as current feature.
8. **Tests.** Sweep then profitable reclaim, first retest fails/second succeeds, duplicate touch inside same episode, refreshed node, time expiry without touch and replay of later-deleted object.
9. **Acceptance.** Causal transition record and calibrated hazard; net/risk value versus static lifecycle with all rejected/re-entry opportunities counted.
10. **Ablation/fallback/resources.** Age/touch/order/refresh/Context, first-touch-only and perpetual-level baselines. Unsupported lifecycle falls back deterministic TTL. Class B sparse object hazard.

## L18 — Correlated objects, provenance groups and candidate-set assembly

1. **Purpose/sources.** Solve many competing levels without inventing independent confluence; user level selection, CRL-19, DRF-U03, SKY board correlation.
2. **Inputs.** All F10 active object versions from L01–19/C22, lineage, price bands, forecast targets and quality. At every decision cut.
3. **Algorithm.** Build complete candidate set; link identical parent/source evidence and overlapping geometry using a declared graph. Keep distinct object identity even when visually merged. Compare no merge, deterministic overlap groups and learned set aggregation; group features include disagreement and independent-source count, not raw indicator count. Create feasible side/entry/stop/target alternatives before ranking; reject unsupported geometry/critical data with reasons. Binding local refinement: [SR-L18](../SYSTEM_REFINEMENT.md#sr-l18).
4. **Output.** Immutable decision set and correlated-evidence groups, each member/provenance, feasible actions, duplicate reasons and no-local-level/source-event candidates.
5. **Dependencies.** F10 and L01–17/19 plus C22 create the base object set. L18.groups exposes provenance/geometry before G04/05; P02 then enumerates feasible plans, and L18.plans freezes those alternatives before G06–08. No current selected action or value output is required to create its input set.
6. **Comparisons.** Independent source list, simple overlap grouping, regularized set ranker; graph aggregation only with incremental value. Confluence count is a benchmark feature, not admission criterion. Binding further upgrade and child comparisons: [UP-L18](../UPGRADE_PATHS.md#up-l18).
7. **Training.** Group distance/overlap settings inner folds; all rejected candidates retained. OOF forecasts and same-date grouping; no outcome-based merging.
8. **Tests.** POC=VWAP from same source, multiple expiries at same strike, truly distinct cross-source evidence, conflicting roles, overlapping widths, no local node and duplicated generator output.
9. **Acceptance.** Every object accounted once with exact lineage, no missing alternatives, no false independence; economic improvement over simple nearest/strongest and list-only models.
10. **Ablation/fallback/resources.** No merge, provenance removed, raw count versus group count, set model and conflict features. Fall back deterministic complete set. Class A/B sparse spatial graph; active-set limits explicit, overflow logged not silently top-k truncated.

## L19 — Large-print, origin-of-move and aggression-memory locations

1. **Purpose/sources.** Preserve discrete effort-origin/protected-print/retest locations separately from delta profiles; OFM/RDL/TBR/WIC/RFE, JXA-08/15, MVF/CRL-19.
2. **Inputs.** M11 causal aggression clusters/markouts, M02 size cohorts, M10 pace, C18 control and price structure. Source100NY/75London/top35% versus train-normalized filters distinct; per event.
3. **Definition.** Generate cluster price/weighted center, origin-range edges and causally confirmed protected-print bands. Record first subsequent reward/failed extension/retest state when it happens, without claiming inventory remains trapped. Origin of price move is a defined preceding burst/leg, not hindsight whichever print preceded HOD/LOD. Re-entry uses a new decision with refreshed evidence/risk. Binding local refinement: [SR-L19](../SYSTEM_REFINEMENT.md#sr-l19).
4. **Output.** Memory objects with executed-side/cohort/mass, origin/confirmation times, retest status, uncertainty and continuation/reversal/target forecasts.
5. **Dependencies.** M11/M02/10/C18/F10; G/P and R protected-print/refill mechanisms.
6. **Comparisons.** Source fixed filters/one-retest rules; price-only burst clusters; conditional survival/markout model; boosted/sequence role model. Binding further upgrade and child comparisons: [UP-L19](../UPGRADE_PATHS.md#up-l19).
7. **Training.** All causal clusters, unknown signs, date/idea grouped; OOF control forecasts and train-only cluster metric. Future successful markout cannot decide initial eligibility.
8. **Tests.** Large print with no reward, later protection, opposing cluster, first retest already consumed, new pressure after failed idea, and bar proxy source versus exact tape.
9. **Acceptance.** Provenance and confirmation fixtures; incremental value over L06/price-only clusters under density/size/sign/time placebos and conservative fills.
10. **Ablation/fallback/resources.** Cohort/size/sign/reward/retest/decay, fixed versus normalized filters. Unsupported flow produces no memory object. Class A/B/E bounded active clusters and future sequence buffers.
