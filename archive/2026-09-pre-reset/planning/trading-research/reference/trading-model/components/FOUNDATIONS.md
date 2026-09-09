# Foundations: deterministic services

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
All cards incorporate [COMMON_CONTRACTS](COMMON_CONTRACTS.md). Data findings DA-01–12 are binding. These services own correctness and availability; a learned model must not redefine an instrument, clock, quote or fill to improve results.

## F01 — Immutable ingestion and schema decoding

1. **Purpose/provenance.** Reconcile acquired bytes with a versioned research catalog; INV, CEX acquisition discussions, DA-01/08/09. Keep Parquet and native DBN supported without executing supplied indicators.
2. **Inputs/scope/time.** All 111 catalog datasets, file path/size/hash where supplied, schema/version, original event/receipt fields; batch on manifest changes, live adapter later. Source bytes remain unchanged.
3. **Definition.** Decode by declared schema; convert fixed-point fields using field-specific scale; map each sentinel by integer type and schema; retain every supplied field and original payload. MBP-1 is the primary supported futures event source; BBO/trades are derived views under the [source contract](../MARKET_DATA_SOURCE_CONTRACT.md), not a silent coarse-schema replacement. Native action/side enums normalize to documented characters; unknown values retain raw representation. Produce a stable source-row address and ingestion version. Compare expected/observed schemas before accepting a partition. Binding local refinement: [SR-F01](../SYSTEM_REFINEMENT.md#sr-f01).
4. **Output.** `CanonicalEvent` candidates plus partition manifest, counts, schema fingerprints and rejected-row reason codes. No predictive label/calibration; missing required schema yields quarantine.
5. **Dependencies/use.** F02 supplies instrument meaning, F05 normalizes events, F06 validates; V01 records artifacts. Readers never overwrite raw files.
6. **Baselines/candidates.** Reference Python/Arrow/DBN decoder versus optimized streaming reader, with byte/field parity. Statistical anomaly counts are diagnostics; learned decoding is inappropriate because semantics must be exact. Binding further upgrade and child comparisons: [UP-F01](../UPGRADE_PATHS.md#up-f01).
7. **Training/missingness.** No training. Version migrations require explicit mapping and previous-version fixtures; unknown enum remains unknown rather than guessed.
8. **Tests.** Golden rows from every sampled schema; int64/uint64 null sentinels; negative spread prices; empty files; partial row groups; schema drift; corrupted/truncated file; duplicate ingestion of same partition produces identical IDs.
9. **Metrics/acceptance.** Zero unexplained unit/schema/hash drift; reconcile accepted+rejected counts to source counts. Benchmark rows/s, peak RAM and spill bytes. Quarantine rather than drop unexplained records.
10. **Ablation/failure/resources.** Compare projected-column and full decode outputs. Alert on new schemas/sentinels/count changes; fallback to reference decoder. Class D, bounded chunks; no complete 37B-row materialization.

## F02 — Instrument, option contract and settlement registry

1. **Purpose/provenance.** Prevent mixed strikes, multipliers, expiries and spread instruments; DA-06/08, DRF-U04, TECH-05/16.
2. **Inputs/scope/time.** Definitions and publication/receipt times, symbol maps, contract lists, corporate actions and official CME/index/ETF specs. All acquired instruments; updates only when definitions become known.
3. **Definition.** Bitemporal key `(venue,instrument_id,valid interval,definition version)` resolves underlying, strike, right, multiplier, tick schedule, exercise style, settlement type/time and legs. For an option-on-future, link the specific underlying future. Do not parse NQ `C0000` as zero strike. Unknown fields block dependent valuation/order construction. Binding local refinement: [SR-F02](../SYSTEM_REFINEMENT.md#sr-f02).
4. **Output.** Typed instrument registry and `valuation_eligible`, `execution_eligible`, `outright/spread/unknown` flags; no learned target. Uncertainty is unresolved metadata, never a probability of identity.
5. **Dependencies/use.** F01 decoded definitions; F03 calendars; O01/O02 chain valuation and P06 execution consume exact versions.
6. **Alternatives.** Explicit curated registry plus as-of definitions is baseline; automated cross-source reconciliation is challenger. Statistical consistency checks may flag conflicts; learned entity matching can suggest reviews but cannot authorize ambiguous contract trades. Binding further upgrade and child comparisons: [UP-F02](../UPGRADE_PATHS.md#up-f02).
7. **Training/missingness.** No core training. Historical listings cannot be inferred from today's symbols; metadata learned later is usable for labels/audits only unless original publication is established.
8. **Tests.** Same strike with AM/PM settlement, monthly/weekly symbols, stock split, expiry-day time, variable option ticks, UDS spread, reused IDs, missing multiplier, official NQ/ES tick-to-dollar conversion and negative-price spread fixture.
9. **Acceptance.** Every actionable instrument has an unambiguous known definition; exact arithmetic identities and valid interval joins; unknown definitions explicitly excluded from dependent features with coverage reported.
10. **Fallback/resources.** Drop only unresolved contract valuations; preserve raw flow in an unknown bucket. Monitor unmatched IDs and metadata age. Class A registry, O(log definitions) lookup; modest RAM, append-only versions.

## F03 — Trading calendar, session and boundary engine

1. **Purpose/provenance.** Preserve Jumbo/Pine clock differences and prop flattening; JTR-03/09, JFN-03, PIN clock findings, ACCOUNT_CONSTRAINTS.
2. **Inputs.** Versioned exchange holidays/hours, `America/New_York` zone database, instrument/firm/platform calendar, explicit source window definitions. All sessions; events in UTC, local dates derived.
3. **Definition.** Half-open formation intervals `[start,end)` with separate observation/label horizons. Spanning-midnight windows belong to a named trading date. Store NY-wall-time and fixed-EST source sensitivity as distinct variants. Never reset by naïve UTC midnight. Firm boundary may precede exchange close; effective flatten time is earliest applicable constraint minus measured execution margin. Binding local refinement: [SR-F03](../SYSTEM_REFINEMENT.md#sr-f03).
4. **Output.** `SessionKey`, open/close/holiday/transition events, eligible-day calendar, time-to-boundary and source-clock variants; no trained labels.
5. **Dependencies/use.** F02 instrument, account-rule P09; F09 bars, C01 ranges, M anchors and P10 flatten use the same calendar version.
6. **Alternatives.** Deterministic timezone-aware calendar baseline; vendor calendar cross-check. Learned clocks are inappropriate; learned session-opportunity is C-series. Binding further upgrade and child comparisons: [UP-F03](../UPGRADE_PATHS.md#up-f03).
7. **Rules.** Freeze eligibility before results. A missing first/last bar is not an absent session; record observed coverage separately. New holiday announcements become effective only once known historically.
8. **Tests.** US DST spring/fall, Sunday open, midnight windows, early close, 09:30 versus 09:00, missing boundary tick, holiday rollover, fixed-GMT versus NY source variants, Lucid platform deadline difference.
9. **Acceptance.** Zero conflicting date assignment/double-counted boundary events; every position has a scheduled flatten event independent of market ticks. Compare calendar rows against official selected-year samples.
10. **Fallback/resources.** Unknown current boundary means no new entries and conservative flatten/reconcile policy; never extend hours by assumption. Class A, precomputed calendar and timers; monitor rule/version expiry.

## F04 — Availability ledger and causal replay clock

1. **Purpose.** Enforce information ordering; DTM causality requirements, DA-03/07/11, all visual/source repaint findings.
2. **Inputs.** Canonical events, source receipt/publication clocks, computation durations, explicit lag assumptions and revision links. Every provider and derived object.
3. **Algorithm.** Maintain an availability-priority stream; release records when known_at permits. Preserve event-time windows separately. Late records update current state under declared revision policy but cannot rewrite historic decisions. For unordered same-time records, evaluate admissible conservative orderings or mark ambiguous. Missing receipt uses a tagged scenario, never invented precision. The separate runtime scheduler defines native-event, minute-option/Context, slow-publication and independent order/risk lanes, atomic completed-version publication, age/deadline expiry, coalescing and pre-dispatch version checks. The computation DAG is not a requirement to recompute every producer on every tick. Binding local refinement: [SR-F04](../SYSTEM_REFINEMENT.md#sr-f04).
4. **Output.** Reproducible ordered event batches, watermarks, availability provenance, delay/clock-uncertainty flags and replay hashes. No predictive target.
5. **Dependencies.** F01/F03; every producer/consumer must pass F04. V06 runs parity and prefix tests.
6. **Alternatives.** Simple single-thread reference replay versus partitioned event merge. Statistical delay distributions are empirical scenario inputs; learned latency model optional after real receipt samples, not used to alter observed order. Binding further upgrade and child comparisons: [UP-F04](../UPGRADE_PATHS.md#up-f04).
7. **Training.** Delay estimates fit only prior live/held-out calibration telemetry by source/session; stress larger tails. Historical event-only cohorts remain labelled hypothetical-latency.
8. **Tests.** Future OI report, revised CPI, confirmed pivot, delayed quote, asynchronous chain snapshot, watermark stall, reordering across files, equal timestamps, injected compute delay and prefix deletion invariant.
9. **Acceptance.** Zero future-dependent decisions and reproducible replay/checkpoint hashes; report decision sensitivity across admissible latency/tie scenarios. Short-horizon edge unsupported when timing uncertainty exceeds its useful lifetime.
10. **Fallback/resources.** Stop dependent forecasts on watermark/freshness failure; preserve independent experts. Class A/D merge with bounded buffers/spill; log backlog, lateness and decision age.

## F05 — Event identity, trade conditions and side normalization

1. **Purpose.** Separate trades from quotes/corrections and true aggressor information from inference; DA-03/04/09, TECH-15/16, CVD requests.
2. **Inputs.** Action/type/side, raw flags, trade conditions/valid-for-volume, available sequence/channel/instrument, price/size and associated quote. Futures and options streams at native cadence; preserve source-specific missing columns instead of inventing them from a generic schema.
3. **Algorithm.** For Databento Trade action, map B→+1, A→−1, N→unknown; use separate resting-side mapping for non-trade actions. Decode flags bitwise under the provider/schema/version contract. Never require F_LAST for trade inclusion or reapply MBO-only event buffering to normalized MBP-1. Apply versioned official condition rules to volume eligibility; corrections/cancels link to original events. Deduplicate ingestion copies, including embedded/standalone trade overlap, not distinct same-time identical prints. Options inferred sign is O03, not this decoder. Binding local refinement: [SR-F05](../SYSTEM_REFINEMENT.md#sr-f05).
4. **Output.** Eligible trade and normalized book-event views with raw/decoded flags, reported aggressor or unknown, source order, inclusion/exclusion reason, correction lineage and stable event ID. Unknown volume remains in total and separate uncertainty counters. Flagged flow coverage and trusted book validity are separate fields.
5. **Dependencies.** F01/F02/F04 and F06.RAW prechecks; normalized outputs then feed F06.SEMANTIC and F07 operation eligibility. M01/M02/VP and options flow consume explicitly eligible events. The computation schedule separates these ports to prevent F05↔F06 recursion.
6. **Alternatives.** Vendor-reported sign baseline; quote/tick-inferred sign is a separately tagged challenger on overlap, never silent replacement. Learned sign belongs in O03 when evidence supports calibration. Binding further upgrade and child comparisons: [UP-F05](../UPGRADE_PATHS.md#up-f05).
7. **Rules.** No learned filtering on future profitability. Condition mapping version tied to provider/date; unknown conditions quarantine directional statistics while retaining provenance.
8. **Tests.** A/B meaning by action; N trade, correction, auction, duplicate file, separate identical trade, same-sequence multi-instrument statistics, zero/negative invalid outright size, spread transaction; native enum versus character, valid T without F_LAST, combined flags 132/168, snapshot versus new activity and embedded/standalone duplication. Preserve quote semantics without subtracting a trade and its later book update twice.
9. **Acceptance.** Reconcile total/signed/unknown volume and correction counts with source; sampled futures trade-stream equality expands by cohort. No unexplained double counting.
10. **Fallback/resources.** Unknown-sign bucket; no CVD directional claim for unsupported cohort. Class A constant work/event; monitor sign-known fraction, condition drift and reconciliation mismatch.

## F06 — Quality, gaps, stale data and quarantine

1. **Purpose.** Turn audited weaknesses into explicit eligibility; DA-01–12, source warnings about false precision.
2. **Inputs.** Events/partitions, expected session coverage, tick/price constraints, last known observation, provider masks. Event and daily audits.
3. **Algorithm.** Deterministic checks for schema, sentinels, impossible OHLC, negative outright size, crossed/locked/one-sided markets, ordering and stale age. Propagate decoded MBP gap, snapshot and receipt-quality flags through the [source contract](../MARKET_DATA_SOURCE_CONTRACT.md). A flag indicating a book gap blocks trusted book/execution state until documented recovery; missing trade history remains incomplete after book recovery. Classify auction/closed/stale/corrupt separately. Gap means absence relative to a declared expected observation stream, not merely no trades in an illiquid option. Maintain affected interval and feature lineage. Binding local refinement: [SR-F06](../SYSTEM_REFINEMENT.md#sr-f06).
4. **Output.** Quality mask and severity `informational/dependent-feature-block/execution-block`, incident record, coverage durations. Statistical anomaly score is advisory with its own uncertainty.
5. **Dependencies.** F06.RAW uses F01 decoding and F02/F03/F04 bootstrap metadata before F05 normalization. F06.SEMANTIC uses normalized F05 outputs afterward; F07 propagates operation-specific masks and P08/P10 independent risk reacts to critical failures. These are distinct acyclic ports.
6. **Alternatives.** Fixed schema/market invariants, robust rolling median/MAD rates, optional isolation/change-point model for novel anomalies. Learned detector cannot override a hard invalid quote. Binding further upgrade and child comparisons: [UP-F06](../UPGRADE_PATHS.md#up-f06).
7. **Training.** Fit anomaly baselines on prior same-session/asset history; no current-day full-sample normalization. Missing expected stream is not imputed into valid execution.
8. **Tests.** Stale NDXP quote, future-paired quote, opening crossed auction, locked-quote sign ambiguity versus separately defined execution eligibility, missing minutes, genuine quiet option, partial chain dropout and deliberate sentinel explosion.
9. **Acceptance.** All known audit defects detected with correct downstream propagation; false alarms measured on reviewed samples; chosen freshness cutoffs frozen from lag/error sensitivity, not P&L-maximized on test.
10. **Fallback/resources.** Isolate dependent experts or block new orders; preserve diagnosis. Class A/B; no giant raw scan required per decision. Track covered-time denominators and outage-related P&L.

## F07 — As-of joins and coverage tensor

1. **Purpose.** Join heterogeneous feeds without future or survivorship leakage; DA-05–07/10, DRF joint-chain ambition.
2. **Inputs.** Versioned event/definition/OI/quote/underlying/curve/calendar streams and requested decision cuts. All chains/assets; native timestamps plus masks.
3. **Algorithm.** Backward availability join constrained by instrument, definition validity, maximum age and compatible session. For overlapping quote acquisitions, compare payload/version and select deterministically; never add duplicate OI/volume. Construct coverage across asset×expiry×moneyness×field; represent estimated wings separately. Binding local refinement: [SR-F07](../SYSTEM_REFINEMENT.md#sr-f07).
4. **Output.** Joined snapshot with every input row/version and age; `CoverageMask`, observed-OI fractions and invalid/missing reasons. No assumption that absent contract equals zero.
5. **Dependencies.** F02/F04/F06; O01 surfaces/boards, X models and G missing-expert routing consume masks directly.
6. **Alternatives.** Exact backward join baseline; prior-value carry within TTL; learned imputation only as a separately masked feature candidate. Nearest-timestamp join is prohibited if it can select the future. Binding further upgrade and child comparisons: [UP-F07](../UPGRADE_PATHS.md#up-f07).
7. **Training.** Imputation/moneyness bins from train-only data; same-date coverage cohorts for comparisons. Universe known_at retained, not selected from all contracts traded later in the day.
8. **Tests.** Next-morning OI, quote just after trade, same-date late OI, holiday previous-calendar-day trap, duplicated near/broad contracts, changed expiry filter, missing 61+ DTE quotes and future listed symbol.
9. **Acceptance.** Zero forward joins; exact union/dedup counts; coverage metrics reproduce audited snapshots. Downstream gains must survive matched-coverage comparisons.
10. **Fallback/resources.** Missing/stale values masked; branch to validated available-data model. Class A/C sparse sorted joins; monitor join age, dropped contracts and coverage shifts.

## F08 — Futures rolls and equity adjustments

1. **Purpose.** Preserve economically meaningful levels and histories; INV roll map, DA-01/02/10, Jumbo prior-level requirements.
2. **Inputs.** Actual contract tapes, as-of roll policy/calendar/liquidity, source continuous-series map, equity corporate-action factors. Daily and contract-transition cadence.
3. **Algorithm.** Keep fills/raw levels in contract coordinates. Construct return-continuous series with a declared causal roll rule; prohibit retrospectively best-volume contract selection. On roll, expire contract-specific objects or translate by an observed simultaneous spread with mapping uncertainty, retaining old/new IDs. Raw option strikes join raw underlying prices, not hindsight-adjusted closes. Binding local refinement: [SR-F08](../SYSTEM_REFINEMENT.md#sr-f08).
4. **Output.** Contract mapping, return series, roll event, adjusted display series, object translation record. No future target except downstream returns.
5. **Dependencies.** F02/F03/F04; M histories, C volatility and P order contract selection.
6. **Alternatives.** Fixed-calendar roll, prior-day-volume roll, provider map replication. Compare reset versus spread-translation objects; a learned roll chooser is unnecessary for primary one-mini research until simple rules fail. Binding further upgrade and child comparisons: [UP-F08](../UPGRADE_PATHS.md#up-f08).
7. **Rules.** Roll thresholds freeze in training; adjustment publication known_at required. Do not allow a manufactured roll gap to become a sweep or volatility jump label.
8. **Tests.** Quarterly rollover, last-day low liquidity, simultaneous spread missing, back-adjusted price versus actual strike, stock split, dividend adjustment and old profile carried into new contract.
9. **Acceptance.** Fill P&L reconstructs actual contracts exactly; no artificial return jump from the chosen adjustment; translated-level performance separately scored and uncertainty reported.
10. **Fallback/resources.** Reset affected objects when mapping is unavailable; flat before unresolved contract transition. Class A; sparse registry, negligible compute compared with tape.

## F09 — Causal bars and multiresolution aggregation

1. **Purpose.** Common trade-derived observations for source benchmarks and learned models; JSS timeframe caveats, PIN future-HTF defects, M CVD extrema.
2. **Inputs.** F05 eligible trades/quotes and F03 windows; price ticks, volume contracts, signs; event-native updates plus closed 1s/1m/5m/15m/session outputs where supported.
3. **Algorithm.** Maintain open/high/low/last/volume over half-open intervals; publish provisional and final versions separately. Final bar known after interval close and required watermark. Empty intervals carry no fictitious traded high/low; stale price carry is flagged. Build volume/event bars using a frozen threshold and record their completion time. Binding local refinement: [SR-F09](../SYSTEM_REFINEMENT.md#sr-f09).
4. **Output.** Bar schema with interval, observed-duration/volume, final/provisional flag, reset and quality; quote bars distinct from trade bars. CVD bar extrema derive from ordered cumulative trades, not price candles.
5. **Dependencies.** F03–06; M/C/L and Pine benchmark adapters. Any higher-timeframe request is reaggregated from causal data.
6. **Alternatives.** Native supplied bars versus recomputed bars; time, volume and event bars are separate registered measurement choices. Learned bar thresholds are C05 discovery, not hidden here. Binding further upgrade and child comparisons: [UP-F09](../UPGRADE_PATHS.md#up-f09).
7. **Training.** None for arithmetic; activity thresholds estimated only from prior/training periods. No future-completed HTF OHLC may appear at its open.
8. **Tests.** Boundary tick, missing first print, empty bar, DST, coarse bar spanning formation end, same-timestamp order ambiguity, late correction, 15-minute range frozen before completion and trade-vs-bar CVD extrema.
9. **Acceptance.** Aggregate volume/mass conservation, source/recomputed reconciliation within documented filtering differences, prefix invariance and final/provisional parity.
10. **Fallback/resources.** Emit incomplete/unknown rather than fabricated bar. Class A O(1) per active aggregation; cap configured resolutions and cache shared outputs.

## F10 — Versioned market-object and event registry

1. **Purpose.** Preserve formation, retests, invalidation and all rejected candidates; JXA/JFN deletion critique, CRL-19, all Location families.
2. **Inputs.** Generator events, parent anchors, mapping revisions, contacts/reclaims and expiry rules; event/decision cadence.
3. **Algorithm.** Append object versions with stable identity; distinguish born, provisional, active, contacted, swept, reclaimed, invalidated, expired and superseded. State transitions are generator-specific; invalidation does not erase history. Geometric overlap creates a relationship, not automatic identity or independent confirmation. Binding local refinement: [SR-F10](../SYSTEM_REFINEMENT.md#sr-f10).
4. **Output.** `MarketObject`, immutable transition log and active-set query as-of time; every revision references prior version. Unknown formation prevents activation.
5. **Dependencies.** F04/F07/F08; M/C/O/L produce objects, G ranks, V labels original versions.
6. **Alternatives.** Deterministic IDs/transition machine baseline; spatial clustering only for display/feature groups. Learned lifecycle hazards are L-series forecasts and cannot rewrite registry facts. Binding further upgrade and child comparisons: [UP-F10](../UPGRADE_PATHS.md#up-f10).
7. **Rules.** No training in storage. Object TTL and invalidation definitions are versioned experiment parameters; no deleting failed candidates from training or diagnostics.
8. **Tests.** Same price/different anchor, shifting gamma node, split/merge node, repeated retest, roll translation, future-invalidated object in historical query, restart and event duplicate.
9. **Acceptance.** Exact historic active set and lineage reconstruction; no orphan parent, retroactive object or duplicate transition; all scored candidates retrievable.
10. **Fallback/resources.** Invalid version blocks dependent action; use previous still-valid version only if policy allows. Class A, O(log active set), archived history on disk; cap hot active state by explicit expiry, not hindsight.

## F11 — Feature, prediction and fold artifact store

1. **Purpose.** Prevent downstream in-sample leakage and irreproducible experimentation; CRL-17, DTM validation ideas, TECH-10.
2. **Inputs.** Measurements/objects/forecasts, data hashes, feature definitions, split intervals, model/scaler/calibrator versions and labels with maturity. Batch research plus live prediction append.
3. **Algorithm.** Content-address artifacts by data+definition+availability+fold+code. Maintain separate raw features, OOF predictions, final-fit predictions and labels. Join downstream training only to time-honest OOF predictions; reject mismatched target/horizon or model trained on that outcome date. Record the exact feature columns and transformations actually used by each fitted/served model and reconcile them against its registered design. An omitted rich feature or a later-state census must be detectable before diagnosing the original information hypothesis. Binding local refinement: [SR-F11](../SYSTEM_REFINEMENT.md#sr-f11).
4. **Output.** Reproducible feature/prediction tables and manifests with row keys, upstream lineage and permissible training intervals. Missing artifact returns explicit failure, not automatic stale cache reuse.
5. **Dependencies.** F04/F10/V01/V02; all learned components and gates. V03 registers trials.
6. **Alternatives.** Simple immutable Parquet manifests first; database/catalog only if concurrency/scale demands. Learned cache routing is inappropriate. Binding further upgrade and child comparisons: [UP-F11](../UPGRADE_PATHS.md#up-f11).
7. **Training.** Every scaler/model gets fit interval and feature availability provenance. Derived labels may be stored beside features only with access controls/views that prevent accidental selection as input.
8. **Tests.** OOF swapped with fitted predictions, wrong horizon, overlapping purge intervals, revised data hash, cache collision, interrupted write, deterministic rerun and future normalization contamination. Registered-but-unused input family, unintended future field, stale fold cache and changed transformation under the same model name require explicit lineage failures.
9. **Acceptance.** Every forecast traceable to permissible training rows and exact artifacts; zero unexplained cache drift; reconstruct an experiment from manifest alone.
10. **Fallback/resources.** Fail closed on provenance mismatch; rebuild bounded partitions. Class D, compressed columnar features; report artifact growth by version and remove only explicitly obsolete generated caches with preservation policy.

## F12 — Historical/live adapter and receipt telemetry

1. **Purpose.** Make the eventual deployed calculation testable against research assumptions; DA timing limitations, source live/replay differences, no live work authorized now.
2. **Inputs.** Authorized future live feed subscriptions, exchange/provider heartbeat/receipt events, broker positions/orders and matched historical adapter. Same canonical schemas; append monotonic local receive time and UTC clock diagnostics.
3. **Algorithm.** Separate transport from semantic decoding; capture raw feed before transformation; watermark each source; compare online feature/object hashes with replay of the captured data. Subscribe only to the approved universe/rights, preserving missing-source states. Binding local refinement: [SR-F12](../SYSTEM_REFINEMENT.md#sr-f12).
4. **Output.** Receipt-latency distributions, raw live archive, canonical stream, parity reports and quality incidents. No live trading implied by read-only shadow capture.
5. **Dependencies.** F01–11, P07 broker adapter, V06 parity. Required before short-horizon execution claims and shadow promotion.
6. **Alternatives.** Polling/minute snapshots versus streamed updates on common information cuts; choose by measured signal lifetime/cost. Predictive delay models are optional telemetry research, not substituted for actual receipt. Binding further upgrade and child comparisons: [UP-F12](../UPGRADE_PATHS.md#up-f12).
7. **Training.** The baseline future shadow freezes all learned parameters; telemetry calibrates later versions after evaluation. A separately registered adaptive-policy trial may update only under its frozen rule using labels actually matured by that update. Its complete adaptive trajectory is the evaluated policy; no unregistered reset or choice of the better realized branch is allowed. No retrospective reduction of assumed latency to make results match.
8. **Tests.** Disconnect/reconnect, duplicate reconnect replay, clock jump, dropped chain, delayed BBO, restart while position open, stale order state, subscription-limit denial and matching historical calculation.
9. **Acceptance.** Zero unexplained semantic divergence; measured p50/p95/p99 latency and drop rates within predeclared horizon budgets; all account and data permissions resolved before activation.
10. **Fallback/resources.** Degrade dependent experts and stop entries on critical feed loss; independent position protection/reconciliation survives. Class A/D; capture volume measured before retention budget. Deferred external connection and feed-cost choices are explicit deployment dependencies.
