# Full implementation scope

This is the coverage index for **one continuing B00–B10 implementation workflow**. Read the [handoff](IMPLEMENTATION_HANDOFF.md) for the starting message, sequencing and evidence rules. E0 is an early checkpoint. Detailed Response, later management and prospective evaluation remain in the same scope.

The current version covers **153 parents, 191 named refinements, 344 units and 2,752 P0–P7 phase records**; **712 supplied-source findings, 119 external findings, 68 prompt/DTM/active requirements, 111 datasets and 64 backlog tasks**. These are planned obligations, not completed implementations or demonstrated improvements.

Binding upgrades add **153 authored parent paths and 191 specific child instructions** inside those same units. Their exact constructions, comparisons and cases are included for every unit in the machine scope, alongside three focused method-reference entries. They do not inflate the count of experiments or certify empirical improvement.

The [machine manifest](review/implementation_scope.json) contains every exact ID, target, local case, source route, milestone and phase reference. Its version is `0d7fff8cba9a2201a30ea140cfa7f012556405c8c8a7416ef2802c109c6d7a95`; the [immutable snapshot](review/system-refinement/scope_snapshots/0d7fff8cba9a2201a30ea140cfa7f012556405c8c8a7416ef2802c109c6d7a95.json) preserves that definition. Rebuilding this index updates no implementation status.

## Binding interpretation

Read the full ten-part contract and all linked child/local-phase definitions before implementing a parent. Preserve the original source idea and its conversation upgrade path; every listed variant needs a named implementation/comparison or an explicit dependency/disposition. Shared machinery is encouraged, but shared code does not remove independent semantic tests or target/horizon scorecards. A simpler measurement or deterministic construction can be the right upgrade. A new model is not mandatory.

Use the [quality rules](MODEL_QUALITY_AND_STOPPING_RULES.md) to determine what is best supported within tested data, challengers and budgets. Initial screening may close a branch only with its registered rule and evidence; record downstream phases as inapplicable with reasons. An unsupported model is not silently dropped, and every proposal is not forced into production. Keep source-clause, cohort and decision evidence distinct from document-coverage counts.

The actual implementation ledger is separate and append-only. It records engineering state, evaluation state and disposition independently, with artifacts, exact dependencies and next actions. At completion reconcile exact IDs/clauses/phases, not only totals. Unavailable data, unelapsed future evaluation and inconclusive research stay visible. The machine manifest contains the ledger fields and allowed states.

Binding additional detail: [SYSTEM_REFINEMENT.md](SYSTEM_REFINEMENT.md).

Binding additional detail: [UPGRADE_PATHS.md](UPGRADE_PATHS.md).

Binding additional detail: [UPGRADE_CONSTRUCTIONS.md](UPGRADE_CONSTRUCTIONS.md).

## Every parent and its named refinements

Milestones are routing indexes; the ordered backlog and actual dependency graph govern readiness. All families also inherit common contracts and validation. The parent link gives the full definition; each child link gives its individual P0–P7 record.

### Foundations

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [F01 — Immutable ingestion and schema decoding](components/FOUNDATIONS.md:6); [parent phases](experiments/F.md#f01); [upgrade path](UPGRADE_PATHS.md#up-f01) | [F01.DECODER](experiments/F.md#f01-decoder) | B00, B01, B02, B08, B10 |
| [F02 — Instrument, option contract and settlement registry](components/FOUNDATIONS.md:19); [parent phases](experiments/F.md#f02); [upgrade path](UPGRADE_PATHS.md#up-f02) | [F02.PAYOFF](experiments/F.md#f02-payoff) | B00, B01, B02, B08, B10 |
| [F03 — Trading calendar, session and boundary engine](components/FOUNDATIONS.md:32); [parent phases](experiments/F.md#f03); [upgrade path](UPGRADE_PATHS.md#up-f03) | [F03.SESSION_CASES](experiments/F.md#f03-session_cases) | B00, B01, B02, B08, B10 |
| [F04 — Availability ledger and causal replay clock](components/FOUNDATIONS.md:45); [parent phases](experiments/F.md#f04); [upgrade path](UPGRADE_PATHS.md#up-f04) | [F04.SCHEDULER](experiments/F.md#f04-scheduler) | B00, B01, B02, B08, B10 |
| [F05 — Event identity, trade conditions and side normalization](components/FOUNDATIONS.md:58); [parent phases](experiments/F.md#f05); [upgrade path](UPGRADE_PATHS.md#up-f05) | [F05.CROSS_VENDOR](experiments/F.md#f05-cross_vendor) | B00, B01, B02, B08, B10 |
| [F06 — Quality, gaps, stale data and quarantine](components/FOUNDATIONS.md:71); [parent phases](experiments/F.md#f06); [upgrade path](UPGRADE_PATHS.md#up-f06) | [F06.GAP_RECOVERY](experiments/F.md#f06-gap_recovery) | B00, B01, B02, B08, B10 |
| [F07 — As-of joins and coverage tensor](components/FOUNDATIONS.md:84); [parent phases](experiments/F.md#f07); [upgrade path](UPGRADE_PATHS.md#up-f07) | [F07.AGE_SUPPORT](experiments/F.md#f07-age_support) | B00, B01, B02, B08, B10 |
| [F08 — Futures rolls and equity adjustments](components/FOUNDATIONS.md:97); [parent phases](experiments/F.md#f08); [upgrade path](UPGRADE_PATHS.md#up-f08) | [F08.ROLL_PARITY](experiments/F.md#f08-roll_parity) | B00, B01, B02, B08, B10 |
| [F09 — Causal bars and multiresolution aggregation](components/FOUNDATIONS.md:110); [parent phases](experiments/F.md#f09); [upgrade path](UPGRADE_PATHS.md#up-f09) | [F09.ACTIVITY_BARS](experiments/F.md#f09-activity_bars) | B00, B01, B02, B08, B10 |
| [F10 — Versioned market-object and event registry](components/FOUNDATIONS.md:123); [parent phases](experiments/F.md#f10); [upgrade path](UPGRADE_PATHS.md#up-f10) | [F10.LINEAGE](experiments/F.md#f10-lineage) | B00, B01, B02, B08, B10 |
| [F11 — Feature, prediction and fold artifact store](components/FOUNDATIONS.md:136); [parent phases](experiments/F.md#f11); [upgrade path](UPGRADE_PATHS.md#up-f11) | [F11.INPUT_AUDIT](experiments/F.md#f11-input_audit) | B00, B01, B02, B08, B10 |
| [F12 — Historical/live adapter and receipt telemetry](components/FOUNDATIONS.md:149); [parent phases](experiments/F.md#f12); [upgrade path](UPGRADE_PATHS.md#up-f12) | [F12.PARITY](experiments/F.md#f12-parity) | B00, B01, B02, B08, B10 |

### Measurements

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [M01 — Ordinary traded CVD](components/MEASUREMENTS.md:6); [parent phases](experiments/M.md#m01); [upgrade path](UPGRADE_PATHS.md#up-m01) | [M01.SIGN_RESET](experiments/M.md#m01-sign_reset) | B02, B07, B09 |
| [M02 — Size-cohort CVD with true within-bar OHLC](components/MEASUREMENTS.md:19); [parent phases](experiments/M.md#m02); [upgrade path](UPGRADE_PATHS.md#up-m02) | [M02.ADAPT_COHORT](experiments/M.md#m02-adapt_cohort), [M02.FIXED_COHORT](experiments/M.md#m02-fixed_cohort), [M02.OHLC](experiments/M.md#m02-ohlc) | B02, B07, B09 |
| [M03 — Divergence and SMT measurement family](components/MEASUREMENTS.md:32); [parent phases](experiments/M.md#m03); [upgrade path](UPGRADE_PATHS.md#up-m03) | [M03.COHORT_SMT](experiments/M.md#m03-cohort_smt), [M03.PRICE_CVD](experiments/M.md#m03-price_cvd) | B02, B07, B09 |
| [M04 — Trade-at-price volume profiles and value geometry](components/MEASUREMENTS.md:45); [parent phases](experiments/M.md#m04); [upgrade path](UPGRADE_PATHS.md#up-m04) | [M04.ANCHORS](experiments/M.md#m04-anchors), [M04.PROXY](experiments/M.md#m04-proxy), [M04.TOPOLOGY](experiments/M.md#m04-topology) | B02, B07, B09 |
| [M05 — Delta profiles and side-separated auction geometry](components/MEASUREMENTS.md:58); [parent phases](experiments/M.md#m05); [upgrade path](UPGRADE_PATHS.md#up-m05) | [M05.SIDE_TOPOLOGY](experiments/M.md#m05-side_topology) | B02, B07, B09 |
| [M06 — TPO and time-at-price auction measurements](components/MEASUREMENTS.md:71); [parent phases](experiments/M.md#m06); [upgrade path](UPGRADE_PATHS.md#up-m06) | [M06.DWELL](experiments/M.md#m06-dwell) | B02, B07, B09 |
| [M07 — Price VWAP, anchored VWAP and dispersion](components/MEASUREMENTS.md:84); [parent phases](experiments/M.md#m07); [upgrade path](UPGRADE_PATHS.md#up-m07) | [M07.ROBUST_BANDS](experiments/M.md#m07-robust_bands) | B02, B07, B09 |
| [M08 — Causal swings, structure and retracement anchors](components/MEASUREMENTS.md:97); [parent phases](experiments/M.md#m08); [upgrade path](UPGRADE_PATHS.md#up-m08) | [M08.MULTISCALE](experiments/M.md#m08-multiscale) | B02, B07, B09 |
| [M09 — Best-quote OFI, imbalance and replenishment proxies](components/MEASUREMENTS.md:110); [parent phases](experiments/M.md#m09); [upgrade path](UPGRADE_PATHS.md#up-m09) | [M09.RECOVERY](experiments/M.md#m09-recovery) | B02, B07, B09 |
| [M10 — Tape intensity, effort, progress and response efficiency](components/MEASUREMENTS.md:123); [parent phases](experiments/M.md#m10); [upgrade path](UPGRADE_PATHS.md#up-m10) | [M10.EFFICIENCY](experiments/M.md#m10-efficiency), [M10.INTENSITY](experiments/M.md#m10-intensity) | B02, B07, B09 |
| [M11 — Aggression memory and subsequent markout ledger](components/MEASUREMENTS.md:136); [parent phases](experiments/M.md#m11); [upgrade path](UPGRADE_PATHS.md#up-m11) | [M11.MEMORY_DECAY](experiments/M.md#m11-memory_decay) | B02, B07, B09 |
| [M12 — Opens, gaps, settlements and reference-price measurements](components/MEASUREMENTS.md:149); [parent phases](experiments/M.md#m12); [upgrade path](UPGRADE_PATHS.md#up-m12) | [M12.REFERENCE_TYPES](experiments/M.md#m12-reference_types) | B02, B07, B09 |
| [M13 — Footprint and within-bar aggression geometry](components/MEASUREMENTS.md:162); [parent phases](experiments/M.md#m13); [upgrade path](UPGRADE_PATHS.md#up-m13) | [M13.FOOTPRINT_CHANNELS](experiments/M.md#m13-footprint_channels) | B02, B07, B09 |

### Context

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [C01 — Source-faithful range and session geometry](components/CONTEXT.md:6); [parent phases](experiments/C.md#c01); [upgrade path](UPGRADE_PATHS.md#up-c01) | [C01.RANGE_GEOMETRY](experiments/C.md#c01-range_geometry) | B02, B03, B04, B07 |
| [C02 — Ordered break, sweep and reclaim state](components/CONTEXT.md:19); [parent phases](experiments/C.md#c02); [upgrade path](UPGRADE_PATHS.md#up-c02) | [C02.ORDERED_PATH](experiments/C.md#c02-ordered_path) | B02, B03, B04, B07 |
| [C03 — Jumbo path and internal-versus-extension forecast experts](components/CONTEXT.md:32); [parent phases](experiments/C.md#c03); [upgrade path](UPGRADE_PATHS.md#up-c03) | [C03.BRANCHES](experiments/C.md#c03-branches) | B02, B03, B04, B07 |
| [C04 — Open location relative to prior auction structure](components/CONTEXT.md:45); [parent phases](experiments/C.md#c04); [upgrade path](UPGRADE_PATHS.md#up-c04) | [C04.OPEN_TYPE](experiments/C.md#c04-open_type) | B02, B03, B04, B07 |
| [C05 — Adaptive clock, activity and auction-range discovery](components/CONTEXT.md:58); [parent phases](experiments/C.md#c05); [upgrade path](UPGRADE_PATHS.md#up-c05) | [C05.ACTIVITY](experiments/C.md#c05-activity), [C05.AUCTION](experiments/C.md#c05-auction), [C05.CLOCK_SEARCH](experiments/C.md#c05-clock_search) | B04, B07 |
| [C06 — Conditional excursion and P-zone distribution](components/CONTEXT.md:71); [parent phases](experiments/C.md#c06); [upgrade path](UPGRADE_PATHS.md#up-c06) | [C06.CONDITIONAL](experiments/C.md#c06-conditional), [C06.JOINT](experiments/C.md#c06-joint), [C06.PREFIX](experiments/C.md#c06-prefix) | B04, B07 |
| [C07 — Auction acceptance, rejection, balance and discovery](components/CONTEXT.md:84); [parent phases](experiments/C.md#c07); [upgrade path](UPGRADE_PATHS.md#up-c07) | [C07.ACCEPTANCE](experiments/C.md#c07-acceptance) | B04, B07 |
| [C08 — Value migration and multiscale auction relationships](components/CONTEXT.md:97); [parent phases](experiments/C.md#c08); [upgrade path](UPGRADE_PATHS.md#up-c08) | [C08.MIGRATION](experiments/C.md#c08-migration) | B04, B07 |
| [C09 — Historical range and seasonal volatility baseline](components/CONTEXT.md:110); [parent phases](experiments/C.md#c09); [upgrade path](UPGRADE_PATHS.md#up-c09) | [C09.SEASONAL](experiments/C.md#c09-seasonal) | B04, B07 |
| [C10 — Garman–Klass measurement and forecast specialist](components/CONTEXT.md:123); [parent phases](experiments/C.md#c10); [upgrade path](UPGRADE_PATHS.md#up-c10) | [C10.GK_ROBUST](experiments/C.md#c10-gk_robust) | B04, B07 |
| [C11 — Yang–Zhang opening-jump-aware specialist](components/CONTEXT.md:136); [parent phases](experiments/C.md#c11); [upgrade path](UPGRADE_PATHS.md#up-c11) | [C11.YZ_JUMP](experiments/C.md#c11-yz_jump) | B04, B07 |
| [C12 — Multiscale realized variance and semivariance](components/CONTEXT.md:149); [parent phases](experiments/C.md#c12); [upgrade path](UPGRADE_PATHS.md#up-c12) | [C12.NOISE](experiments/C.md#c12-noise), [C12.SEMIVARIANCE](experiments/C.md#c12-semivariance) | B04, B07 |
| [C13 — HAR and multiscale forward-volatility expert](components/CONTEXT.md:162); [parent phases](experiments/C.md#c13); [upgrade path](UPGRADE_PATHS.md#up-c13) | [C13.HAR_VARIANTS](experiments/C.md#c13-har_variants) | B04, B07 |
| [C14 — Jump, discontinuity and burst-volatility expert](components/CONTEXT.md:175); [parent phases](experiments/C.md#c14); [upgrade path](UPGRADE_PATHS.md#up-c14) | [C14.JUMP_SPLIT](experiments/C.md#c14-jump_split) | B04, B07 |
| [C15 — Implied-volatility, skew and term-structure forecast specialist](components/CONTEXT.md:188); [parent phases](experiments/C.md#c15); [upgrade path](UPGRADE_PATHS.md#up-c15) | [C15.ATM](experiments/C.md#c15-atm), [C15.CROSS_IV](experiments/C.md#c15-cross_iv), [C15.CURVATURE](experiments/C.md#c15-curvature), [C15.DELTA_SKEW](experiments/C.md#c15-delta_skew), [C15.EVENT](experiments/C.md#c15-event), [C15.INTRADAY](experiments/C.md#c15-intraday), [C15.LEVERAGE](experiments/C.md#c15-leverage), [C15.MODELFREE](experiments/C.md#c15-modelfree), [C15.SMILE](experiments/C.md#c15-smile), [C15.TERM](experiments/C.md#c15-term), [C15.VRP](experiments/C.md#c15-vrp), [C15.ZERO_DTE](experiments/C.md#c15-zero_dte) | B04, B07 |
| [C16 — VX, volatility-complex and cross-market stress expert](components/CONTEXT.md:201); [parent phases](experiments/C.md#c16); [upgrade path](UPGRADE_PATHS.md#up-c16) | [C16.FORWARD](experiments/C.md#c16-forward), [C16.JOINT_STRESS](experiments/C.md#c16-joint_stress), [C16.VIX_SURFACE](experiments/C.md#c16-vix_surface), [C16.VVIX](experiments/C.md#c16-vvix), [C16.VX_CURVE](experiments/C.md#c16-vx_curve), [C16.VX_OPTIONS](experiments/C.md#c16-vx_options) | B04, B07 |
| [C17 — Scheduled events, announcements and publication state](components/CONTEXT.md:214); [parent phases](experiments/C.md#c17); [upgrade path](UPGRADE_PATHS.md#up-c17) | [C17.PRE_POST_EVENT](experiments/C.md#c17-pre_post_event) | B04, B07 |
| [C18 — Participation, control and effort-progress forecast specialists](components/CONTEXT.md:227); [parent phases](experiments/C.md#c18); [upgrade path](UPGRADE_PATHS.md#up-c18) | [C18.CONTROL](experiments/C.md#c18-control) | B04, B07 |
| [C19 — Remaining-session movement and opportunity budget](components/CONTEXT.md:240); [parent phases](experiments/C.md#c19); [upgrade path](UPGRADE_PATHS.md#up-c19) | [C19.REMAINING_ROOM](experiments/C.md#c19-remaining_room) | B04, B07 |
| [C20 — Regime and distribution-shift conditioning](components/CONTEXT.md:253); [parent phases](experiments/C.md#c20); [upgrade path](UPGRADE_PATHS.md#up-c20) | [C20.REGIME](experiments/C.md#c20-regime), [C20.REVERSION](experiments/C.md#c20-reversion) | B04, B07 |
| [C21 — Session transition and time-dependent path expert](components/CONTEXT.md:266); [parent phases](experiments/C.md#c21); [upgrade path](UPGRADE_PATHS.md#up-c21) | [C21.TRANSITIONS](experiments/C.md#c21-transitions) | B02, B03, B04, B07 |
| [C22 — Context originator and applicability contract](components/CONTEXT.md:279); [parent phases](experiments/C.md#c22); [upgrade path](UPGRADE_PATHS.md#up-c22) | [C22.ORIGINATION](experiments/C.md#c22-origination) | B02, B03, B04, B07 |
| [C23 — Parkinson high-low variance specialist](components/CONTEXT.md:292); [parent phases](experiments/C.md#c23); [upgrade path](UPGRADE_PATHS.md#up-c23) | [C23.PARKINSON_SCALE](experiments/C.md#c23-parkinson_scale) | B04, B07 |
| [C24 — ARCH/GARCH conditional-variance challenger](components/CONTEXT.md:305); [parent phases](experiments/C.md#c24); [upgrade path](UPGRADE_PATHS.md#up-c24) | [C24.GARCH_ASYMMETRY](experiments/C.md#c24-garch_asymmetry) | B04, B07 |

### Options

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [O01 — Chain assembly, eligibility and coverage accounting](components/OPTIONS.md:6); [parent phases](experiments/O.md#o01); [upgrade path](UPGRADE_PATHS.md#up-o01) | [O01.COVERAGE](experiments/O.md#o01-coverage) | B01, B05, B07 |
| [O02 — Option price validation and IV inversion](components/OPTIONS.md:19); [parent phases](experiments/O.md#o02); [upgrade path](UPGRADE_PATHS.md#up-o02) | [O02.BIDASK_IV](experiments/O.md#o02-bidask_iv) | B01, B05, B07 |
| [O03 — Options trade-sign uncertainty](components/OPTIONS.md:32); [parent phases](experiments/O.md#o03); [upgrade path](UPGRADE_PATHS.md#up-o03) | Parent-local phases cover this unit; no extra child is required. | B01, B05, B07 |
| [O04 — Arbitrage-aware volatility surface and uncertainty](components/OPTIONS.md:45); [parent phases](experiments/O.md#o04); [upgrade path](UPGRADE_PATHS.md#up-o04) | [O04.SURFACE_FIT](experiments/O.md#o04-surface_fit), [O04.TEMPORAL_SURFACE](experiments/O.md#o04-temporal_surface) | B01, B05, B07 |
| [O05 — Greeks and unit-consistent sensitivities](components/OPTIONS.md:58); [parent phases](experiments/O.md#o05); [upgrade path](UPGRADE_PATHS.md#up-o05) | [O05.HIGHER_GREEKS](experiments/O.md#o05-higher_greeks) | B01, B05, B07 |
| [O06 — Reported OI state and next-report label service](components/OPTIONS.md:71); [parent phases](experiments/O.md#o06); [upgrade path](UPGRADE_PATHS.md#up-o06) | [O06.REPORT_COHORTS](experiments/O.md#o06-report_cohorts) | B01, B05, B07 |
| [O07 — Aggregate next-reported-OI forecast experts](components/OPTIONS.md:84); [parent phases](experiments/O.md#o07); [upgrade path](UPGRADE_PATHS.md#up-o07) | [O07.HIERARCHICAL_OI](experiments/O.md#o07-hierarchical_oi) | B05, B07 |
| [O08 — Intraday aggregate-holdings scenario updater](components/OPTIONS.md:97); [parent phases](experiments/O.md#o08); [upgrade path](UPGRADE_PATHS.md#up-o08) | [O08.ASSIMILATION](experiments/O.md#o08-assimilation) | B05, B07 |
| [O09 — Exposure scenarios and concentration boards](components/OPTIONS.md:110); [parent phases](experiments/O.md#o09); [upgrade path](UPGRADE_PATHS.md#up-o09) | [O09.SCENARIO_CURVES](experiments/O.md#o09-scenario_curves) | B05, B07 |
| [O10 — Mechanical-versus-flow exposure-change decomposition](components/OPTIONS.md:123); [parent phases](experiments/O.md#o10); [upgrade path](UPGRADE_PATHS.md#up-o10) | [O10.JOINT_DECOMPOSITION](experiments/O.md#o10-joint_decomposition) | B05, B07 |
| [O11 — Node extraction, width and stable identity](components/OPTIONS.md:136); [parent phases](experiments/O.md#o11); [upgrade path](UPGRADE_PATHS.md#up-o11) | [O11.NODE_GEOMETRY](experiments/O.md#o11-node_geometry) | B05, B07 |
| [O12 — Node persistence, migration and thickening/thinning experts](components/OPTIONS.md:149); [parent phases](experiments/O.md#o12); [upgrade path](UPGRADE_PATHS.md#up-o12) | [O12.MIGRATION](experiments/O.md#o12-migration), [O12.PERSISTENCE](experiments/O.md#o12-persistence) | B05, B07 |
| [O13 — Exposure topology and source pattern grammar](components/OPTIONS.md:162); [parent phases](experiments/O.md#o13); [upgrade path](UPGRADE_PATHS.md#up-o13) | [O13.GRAMMAR](experiments/O.md#o13-grammar) | B05, B07 |
| [O14 — Within-chain strike-by-expiry pattern experts](components/OPTIONS.md:175); [parent phases](experiments/O.md#o14); [upgrade path](UPGRADE_PATHS.md#up-o14) | [O14.CHAIN_ENCODER](experiments/O.md#o14-chain_encoder) | B05, B07 |
| [O15 — Signed options contracts and premium-flow ledger](components/OPTIONS.md:188); [parent phases](experiments/O.md#o15); [upgrade path](UPGRADE_PATHS.md#up-o15) | [O15.FLOW_CHANNELS](experiments/O.md#o15-flow_channels) | B05, B07 |
| [O16 — Delta-, gamma-, vega-, vanna- and charm-weighted flow/CVD](components/OPTIONS.md:201); [parent phases](experiments/O.md#o16); [upgrade path](UPGRADE_PATHS.md#up-o16) | [O16.DELTA](experiments/O.md#o16-delta), [O16.FROZEN_REPRICED](experiments/O.md#o16-frozen_repriced), [O16.GAMMA](experiments/O.md#o16-gamma), [O16.VANNA_CHARM](experiments/O.md#o16-vanna_charm), [O16.VEGA](experiments/O.md#o16-vega) | B05, B07 |
| [O17 — Exposure-weighted strike center and bands](components/OPTIONS.md:214); [parent phases](experiments/O.md#o17); [upgrade path](UPGRADE_PATHS.md#up-o17) | [O17.CENTER_BANDS](experiments/O.md#o17-center_bands) | B05, B07 |
| [O18 — Flow breadth, concentration and OI-relative activity experts](components/OPTIONS.md:227); [parent phases](experiments/O.md#o18); [upgrade path](UPGRADE_PATHS.md#up-o18) | [O18.RATIOS_BREADTH](experiments/O.md#o18-ratios_breadth) | B05, B07 |
| [O19 — Futures-options-specific information experts](components/OPTIONS.md:240); [parent phases](experiments/O.md#o19); [upgrade path](UPGRADE_PATHS.md#up-o19) | [O19.FUTURES_OPTION_STYLE](experiments/O.md#o19-futures_option_style) | B05, B07 |
| [O20 — Multi-leg, sweep and large-print ambiguity specialist](components/OPTIONS.md:253); [parent phases](experiments/O.md#o20); [upgrade path](UPGRADE_PATHS.md#up-o20) | [O20.TRADE_AMBIGUITY](experiments/O.md#o20-trade_ambiguity) | B05, B07 |
| [O21 — Options uncertainty and applicability propagation](components/OPTIONS.md:266); [parent phases](experiments/O.md#o21); [upgrade path](UPGRADE_PATHS.md#up-o21) | [O21.SENSITIVITY](experiments/O.md#o21-sensitivity) | B01, B05, B07 |
| [O22 — Options node/path and actionable-role forecast experts](components/OPTIONS.md:279); [parent phases](experiments/O.md#o22); [upgrade path](UPGRADE_PATHS.md#up-o22) | [O22.RUNNER](experiments/O.md#o22-runner) | B05, B07 |
| [O23 — Per-expiry max-pain settlement-payoff benchmark](components/OPTIONS.md:292); [parent phases](experiments/O.md#o23); [upgrade path](UPGRADE_PATHS.md#up-o23) | [O23.PAYOFF_SET](experiments/O.md#o23-payoff_set) | B05, B07 |

### Cross-market information

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [X01 — Asynchronous cross-market alignment](components/CROSS_ASSET.md:6); [parent phases](experiments/X.md#x01); [upgrade path](UPGRADE_PATHS.md#up-x01) | [X01.ASYNC](experiments/X.md#x01-async) | B06, B07 |
| [X02 — Related-instrument coordinate and sensitivity mapping](components/CROSS_ASSET.md:19); [parent phases](experiments/X.md#x02); [upgrade path](UPGRADE_PATHS.md#up-x02) | [X02.PARITY_BASIS](experiments/X.md#x02-parity_basis) | B06, B07 |
| [X03 — Nasdaq-chain comparison and NDX hypothesis](components/CROSS_ASSET.md:32); [parent phases](experiments/X.md#x03); [upgrade path](UPGRADE_PATHS.md#up-x03) | [X03.NDX_QQQ](experiments/X.md#x03-ndx_qqq) | B06, B07 |
| [X04 — S&P-chain comparison and fair ES alternative](components/CROSS_ASSET.md:45); [parent phases](experiments/X.md#x04); [upgrade path](UPGRADE_PATHS.md#up-x04) | [X04.SPX_SPY](experiments/X.md#x04-spx_spy) | B06, B07 |
| [X05 — Source reaction to receiver opportunity transmission](components/CROSS_ASSET.md:58); [parent phases](experiments/X.md#x05); [upgrade path](UPGRADE_PATHS.md#up-x05) | [X05.SOURCE_ONLY](experiments/X.md#x05-source_only) | B06, B07 |
| [X06 — Joint multi-chain, multi-asset temporal pattern model](components/CROSS_ASSET.md:71); [parent phases](experiments/X.md#x06); [upgrade path](UPGRADE_PATHS.md#up-x06) | [X06.SET_GRAPH_TIME](experiments/X.md#x06-set_graph_time) | B06, B07 |
| [X07 — Relative strength, cross-flow SMT and lead-lag experts](components/CROSS_ASSET.md:84); [parent phases](experiments/X.md#x07); [upgrade path](UPGRADE_PATHS.md#up-x07) | [X07.FLOW_SMT](experiments/X.md#x07-flow_smt), [X07.PRICE_SMT](experiments/X.md#x07-price_smt) | B06, B07 |
| [X08 — ETF and constituent-event context](components/CROSS_ASSET.md:97); [parent phases](experiments/X.md#x08); [upgrade path](UPGRADE_PATHS.md#up-x08) | [X08.CONSTITUENTS](experiments/X.md#x08-constituents), [X08.TRF](experiments/X.md#x08-trf) | B06, B07 |
| [X09 — Global futures, currency and commodity transmission](components/CROSS_ASSET.md:110); [parent phases](experiments/X.md#x09); [upgrade path](UPGRADE_PATHS.md#up-x09) | [X09.GC_USD](experiments/X.md#x09-gc_usd), [X09.HG_FX](experiments/X.md#x09-hg_fx), [X09.NKD_FX](experiments/X.md#x09-nkd_fx), [X09.RATES](experiments/X.md#x09-rates), [X09.SI](experiments/X.md#x09-si), [X09.YM_RTY](experiments/X.md#x09-ym_rty) | B06, B07 |
| [X10 — Slow positioning, inventories and fund-flow context](components/CROSS_ASSET.md:133); [parent phases](experiments/X.md#x10); [upgrade path](UPGRADE_PATHS.md#up-x10) | [X10.COT](experiments/X.md#x10-cot), [X10.SHFE](experiments/X.md#x10-shfe), [X10.SLV](experiments/X.md#x10-slv) | B06, B07 |

### Locations

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [L01 — Internal range quarters, EQ and range-open locations](components/LOCATION.md:12); [parent phases](experiments/L.md#l01); [upgrade path](UPGRADE_PATHS.md#up-l01) | [L01.INTERNAL_ROLES](experiments/L.md#l01-internal_roles) | B02, B03, B07 |
| [L02 — Range edges and edge-relative extensions](components/LOCATION.md:25); [parent phases](experiments/L.md#l02); [upgrade path](UPGRADE_PATHS.md#up-l02) | [L02.PROJECTION_ROLES](experiments/L.md#l02-projection_roles) | B02, B03, B07 |
| [L03 — Previous-RTH and full-session structure](components/LOCATION.md:38); [parent phases](experiments/L.md#l03); [upgrade path](UPGRADE_PATHS.md#up-l03) | [L03.RTH_ETH](experiments/L.md#l03-rth_eth) | B02, B03, B07 |
| [L04 — Statistical bounds and improved P-zones](components/LOCATION.md:51); [parent phases](experiments/L.md#l04); [upgrade path](UPGRADE_PATHS.md#up-l04) | [L04.WIDTH_SNAP](experiments/L.md#l04-width_snap), [L04.ZONE_DEFINITION](experiments/L.md#l04-zone_definition) | B02, B07 |
| [L05 — Volume-profile value, nodes, shelves and valleys](components/LOCATION.md:64); [parent phases](experiments/L.md#l05); [upgrade path](UPGRADE_PATHS.md#up-l05) | [L05.PROFILE_ROLES](experiments/L.md#l05-profile_roles) | B02, B03, B07 |
| [L06 — Delta-profile and side-concentration locations](components/LOCATION.md:77); [parent phases](experiments/L.md#l06); [upgrade path](UPGRADE_PATHS.md#up-l06) | [L06.DELTA_ROLES](experiments/L.md#l06-delta_roles) | B02, B07 |
| [L07 — TPO, initial balance, single prints and auction tails](components/LOCATION.md:90); [parent phases](experiments/L.md#l07); [upgrade path](UPGRADE_PATHS.md#up-l07) | [L07.IB_TPO](experiments/L.md#l07-ib_tpo) | B02, B07 |
| [L08 — Swing, retracement and dynamic-range locations](components/LOCATION.md:103); [parent phases](experiments/L.md#l08); [upgrade path](UPGRADE_PATHS.md#up-l08) | [L08.SWING_REFINEMENT](experiments/L.md#l08-swing_refinement) | B02, B07 |
| [L09 — FVG, imbalance and displacement-origin zones](components/LOCATION.md:116); [parent phases](experiments/L.md#l09); [upgrade path](UPGRADE_PATHS.md#up-l09) | [L09.GAP_TYPES](experiments/L.md#l09-gap_types) | B02, B07 |
| [L10 — Order-block and rejection-block entry regions](components/LOCATION.md:129); [parent phases](experiments/L.md#l10); [upgrade path](UPGRADE_PATHS.md#up-l10) | [L10.ENTRY_GEOMETRY](experiments/L.md#l10-entry_geometry) | B02, B07 |
| [L11 — VWAP and anchored-dispersion locations](components/LOCATION.md:142); [parent phases](experiments/L.md#l11); [upgrade path](UPGRADE_PATHS.md#up-l11) | [L11.DYNAMIC_BANDS](experiments/L.md#l11-dynamic_bands) | B02, B03, B07 |
| [L12 — Opens, settlement, gaps and reference-price locations](components/LOCATION.md:155); [parent phases](experiments/L.md#l12); [upgrade path](UPGRADE_PATHS.md#up-l12) | [L12.PRINT](experiments/L.md#l12-print) | B02, B03, B07 |
| [L13 — Options concentration nodes mapped to execution](components/LOCATION.md:168); [parent phases](experiments/L.md#l13); [upgrade path](UPGRADE_PATHS.md#up-l13) | [L13.SMALL_SCENARIO_NODES](experiments/L.md#l13-small_scenario_nodes) | B05, B06, B07 |
| [L14 — Exposure centers, bands and topology corridors](components/LOCATION.md:181); [parent phases](experiments/L.md#l14); [upgrade path](UPGRADE_PATHS.md#up-l14) | [L14.CORRIDORS](experiments/L.md#l14-corridors) | B05, B06, B07 |
| [L15 — Source-event receiver opportunities without local touch](components/LOCATION.md:194); [parent phases](experiments/L.md#l15); [upgrade path](UPGRADE_PATHS.md#up-l15) | [L15.IMMEDIATE_WAIT](experiments/L.md#l15-immediate_wait) | B05, B06, B07 |
| [L16 — Learned location proposal and bounded price refinement](components/LOCATION.md:207); [parent phases](experiments/L.md#l16); [upgrade path](UPGRADE_PATHS.md#up-l16) | [L16.GRID_OFFSETS](experiments/L.md#l16-grid_offsets) | B02, B07 |
| [L17 — Location lifecycle, retest and invalidation hazard](components/LOCATION.md:220); [parent phases](experiments/L.md#l17); [upgrade path](UPGRADE_PATHS.md#up-l17) | [L17.RETEST_HAZARD](experiments/L.md#l17-retest_hazard) | B02, B07 |
| [L18 — Correlated objects, provenance groups and candidate-set assembly](components/LOCATION.md:233); [parent phases](experiments/L.md#l18); [upgrade path](UPGRADE_PATHS.md#up-l18) | [L18.DEPENDENCE](experiments/L.md#l18-dependence) | B02, B07 |
| [L19 — Large-print, origin-of-move and aggression-memory locations](components/LOCATION.md:246); [parent phases](experiments/L.md#l19); [upgrade path](UPGRADE_PATHS.md#up-l19) | [L19.ORIGIN_MEMORY](experiments/L.md#l19-origin_memory) | B02, B03, B07 |

### Mixtures and selection

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [G01 — Target-specific Context and path mixtures](components/GATES_AND_SELECTION.md:6); [parent phases](experiments/G.md#g01); [upgrade path](UPGRADE_PATHS.md#up-g01) | [G01.DIVERSITY](experiments/G.md#g01-diversity) | B03, B07, B10 |
| [G02 — Rich volatility and excursion ensembles](components/GATES_AND_SELECTION.md:19); [parent phases](experiments/G.md#g02); [upgrade path](UPGRADE_PATHS.md#up-g02) | [G02.MULTITARGET](experiments/G.md#g02-multitarget) | B07, B10 |
| [G03 — Forecast calibration and uncertainty service](components/GATES_AND_SELECTION.md:32); [parent phases](experiments/G.md#g03); [upgrade path](UPGRADE_PATHS.md#up-g03) | [G03.CONDITIONAL](experiments/G.md#g03-conditional) | B03, B07, B10 |
| [G04 — Level reach and first-passage expert](components/GATES_AND_SELECTION.md:45); [parent phases](experiments/G.md#g04); [upgrade path](UPGRADE_PATHS.md#up-g04) | [G04.ORDER](experiments/G.md#g04-order) | B03, B07, B10 |
| [G05 — Conditional departure, continuation and runner-quality experts](components/GATES_AND_SELECTION.md:58); [parent phases](experiments/G.md#g05); [upgrade path](UPGRADE_PATHS.md#up-g05) | [G05.RUNNER_DURATION](experiments/G.md#g05-runner_duration) | B03, B07, B10 |
| [G06 — Executable action-value and cost model](components/GATES_AND_SELECTION.md:71); [parent phases](experiments/G.md#g06); [upgrade path](UPGRADE_PATHS.md#up-g06) | [G06.COST_DEPENDENCE](experiments/G.md#g06-cost_dependence) | B03, B07, B10 |
| [G07 — Value of waiting, deeper levels and additional information](components/GATES_AND_SELECTION.md:84); [parent phases](experiments/G.md#g07); [upgrade path](UPGRADE_PATHS.md#up-g07) | [G07.DURATION](experiments/G.md#g07-duration), [G07.INFORMATION](experiments/G.md#g07-information) | B03, B07, B10 |
| [G08 — Candidate ranking and constrained action selection](components/GATES_AND_SELECTION.md:97); [parent phases](experiments/G.md#g08); [upgrade path](UPGRADE_PATHS.md#up-g08) | [G08.RANKING](experiments/G.md#g08-ranking) | B03, B07, B10 |
| [G09 — Applicability, disagreement and abstention gate](components/GATES_AND_SELECTION.md:110); [parent phases](experiments/G.md#g09); [upgrade path](UPGRADE_PATHS.md#up-g09) | [G09.SUPPORT](experiments/G.md#g09-support) | B03, B07, B10 |
| [G10 — Per-expert adaptation, recalibration and retirement policy](components/GATES_AND_SELECTION.md:123); [parent phases](experiments/G.md#g10); [upgrade path](UPGRADE_PATHS.md#up-g10) | [G10.ADAPTATION](experiments/G.md#g10-adaptation) | B07, B10 |

### Policy, execution and risk

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [P01 — Action state and complete sequential policy](components/POLICY_EXECUTION_RISK.md:6); [parent phases](experiments/P.md#p01); [upgrade path](UPGRADE_PATHS.md#up-p01) | [P01.ACTION_STATE](experiments/P.md#p01-action_state) | B03, B08 |
| [P02 — Structural stop and full-position destination choice](components/POLICY_EXECUTION_RISK.md:19); [parent phases](experiments/P.md#p02); [upgrade path](UPGRADE_PATHS.md#up-p02) | [P02.BRACKETS](experiments/P.md#p02-brackets) | B03, B08 |
| [P03 — Full-position exits, protected structure and trailing value](components/POLICY_EXECUTION_RISK.md:32); [parent phases](experiments/P.md#p03); [upgrade path](UPGRADE_PATHS.md#up-p03) | [P03.EXIT_VALUE](experiments/P.md#p03-exit_value) | B03, B08, B09 |
| [P04 — Re-entry, idea memory and cumulative risk](components/POLICY_EXECUTION_RISK.md:45); [parent phases](experiments/P.md#p04); [upgrade path](UPGRADE_PATHS.md#up-p04) | [P04.REENTRY](experiments/P.md#p04-reentry) | B03, B08, B09 |
| [P05 — Event replay and passive-fill uncertainty](components/POLICY_EXECUTION_RISK.md:58); [parent phases](experiments/P.md#p05); [upgrade path](UPGRADE_PATHS.md#up-p05) | [P05.CLOCKS](experiments/P.md#p05-clocks), [P05.PASSIVE](experiments/P.md#p05-passive) | B03, B08 |
| [P06 — Routing, latency, cost and adverse-selection experts](components/POLICY_EXECUTION_RISK.md:71); [parent phases](experiments/P.md#p06); [upgrade path](UPGRADE_PATHS.md#up-p06) | [P06.SHORTFALL](experiments/P.md#p06-shortfall) | B03, B08 |
| [P07 — Broker order state, idempotency and reconciliation](components/POLICY_EXECUTION_RISK.md:84); [parent phases](experiments/P.md#p07); [upgrade path](UPGRADE_PATHS.md#up-p07) | [P07.IDEMPOTENCY](experiments/P.md#p07-idempotency) | B03, B08 |
| [P08 — Independent daily USD risk and pre-trade reservations](components/POLICY_EXECUTION_RISK.md:97); [parent phases](experiments/P.md#p08); [upgrade path](UPGRADE_PATHS.md#up-p08) | [P08.RESERVATION](experiments/P.md#p08-reservation) | B03, B08 |
| [P09 — Firm product and account lifecycle constraints](components/POLICY_EXECUTION_RISK.md:110); [parent phases](experiments/P.md#p09); [upgrade path](UPGRADE_PATHS.md#up-p09) | [P09.ACCOUNT_PATHS](experiments/P.md#p09-account_paths) | B03, B08 |
| [P10 — Day boundary, outage and emergency flattening](components/POLICY_EXECUTION_RISK.md:123); [parent phases](experiments/P.md#p10); [upgrade path](UPGRADE_PATHS.md#up-p10) | [P10.REMAINDER](experiments/P.md#p10-remainder) | B03, B08 |
| [P11 — Trading net, business cash and objective accounting](components/POLICY_EXECUTION_RISK.md:136); [parent phases](experiments/P.md#p11); [upgrade path](UPGRADE_PATHS.md#up-p11) | [P11.CASH](experiments/P.md#p11-cash) | B03, B08 |
| [P12 — Execution-instrument research selection](components/POLICY_EXECUTION_RISK.md:149); [parent phases](experiments/P.md#p12); [upgrade path](UPGRADE_PATHS.md#up-p12) | [P12.FAIR_INSTRUMENT](experiments/P.md#p12-fair_instrument) | B03, B06, B08 |

### Later Response

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [R01 — Approach speed, aggression and progress](components/RESPONSE_DEFERRED.md:10); [parent phases](experiments/R.md#r01); [upgrade path](UPGRADE_PATHS.md#up-r01) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R02 — High-effort stall and absorption proxy](components/RESPONSE_DEFERRED.md:23); [parent phases](experiments/R.md#r02); [upgrade path](UPGRADE_PATHS.md#up-r02) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R03 — Diminishing-effort exhaustion](components/RESPONSE_DEFERRED.md:36); [parent phases](experiments/R.md#r03); [upgrade path](UPGRADE_PATHS.md#up-r03) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R04 — Stopping burst and climax hypothesis](components/RESPONSE_DEFERRED.md:49); [parent phases](experiments/R.md#r04); [upgrade path](UPGRADE_PATHS.md#up-r04) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R05 — At-touch replenishment and resilience sequence](components/RESPONSE_DEFERRED.md:62); [parent phases](experiments/R.md#r05); [upgrade path](UPGRADE_PATHS.md#up-r05) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R06 — Depth-wide support, pulling and layering dependency](components/RESPONSE_DEFERRED.md:75); [parent phases](experiments/R.md#r06); [upgrade path](UPGRADE_PATHS.md#up-r06) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R07 — Candle/footprint effort-result disagreement](components/RESPONSE_DEFERRED.md:88); [parent phases](experiments/R.md#r07); [upgrade path](UPGRADE_PATHS.md#up-r07) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R08 — Diagonal imbalance and stacked-flow defense](components/RESPONSE_DEFERRED.md:101); [parent phases](experiments/R.md#r08); [upgrade path](UPGRADE_PATHS.md#up-r08) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R09 — Developing POC flip and footprint-mode migration](components/RESPONSE_DEFERRED.md:114); [parent phases](experiments/R.md#r09); [upgrade path](UPGRADE_PATHS.md#up-r09) | Parent-local phases cover this unit; no extra child is required. | B09 |
| [R10 — CVD-relative control and multiscale divergence](components/RESPONSE_DEFERRED.md:127); [parent phases](experiments/R.md#r10); [upgrade path](UPGRADE_PATHS.md#up-r10) | [R10.CVD_CASES](experiments/R.md#r10-cvd_cases) | B09 |
| [R11 — Balance break, retest and failed-retest reversal](components/RESPONSE_DEFERRED.md:140); [parent phases](experiments/R.md#r11); [upgrade path](UPGRADE_PATHS.md#up-r11) | [R11.FA_POC](experiments/R.md#r11-fa_poc), [R11.FA_VALUE](experiments/R.md#r11-fa_value) | B09 |
| [R12 — Failed squeeze, refill and renewed same-direction squeeze](components/RESPONSE_DEFERRED.md:153); [parent phases](experiments/R.md#r12); [upgrade path](UPGRADE_PATHS.md#up-r12) | [R12.SQUEEZE_BRANCHES](experiments/R.md#r12-squeeze_branches) | B09 |
| [R13 — Quiet failure and passive-reversion alternative](components/RESPONSE_DEFERRED.md:166); [parent phases](experiments/R.md#r13); [upgrade path](UPGRADE_PATHS.md#up-r13) | [R13.QUIET_ENTRY](experiments/R.md#r13-quiet_entry) | B09 |
| [R14 — Opposing absorption, reward, refresh and lift-off sequence](components/RESPONSE_DEFERRED.md:179); [parent phases](experiments/R.md#r14); [upgrade path](UPGRADE_PATHS.md#up-r14) | [R14.PREFIXES](experiments/R.md#r14-prefixes) | B09 |
| [R15 — Rewarded-side memory and protected structure](components/RESPONSE_DEFERRED.md:192); [parent phases](experiments/R.md#r15); [upgrade path](UPGRADE_PATHS.md#up-r15) | [R15.PROTECTION](experiments/R.md#r15-protection) | B09 |
| [R16 — Minor-node and intra-wick repeated reactions](components/RESPONSE_DEFERRED.md:205); [parent phases](experiments/R.md#r16); [upgrade path](UPGRADE_PATHS.md#up-r16) | [R16.ANCHOR_DETAIL](experiments/R.md#r16-anchor_detail) | B09 |
| [R17 — First, second and later defended retests](components/RESPONSE_DEFERRED.md:218); [parent phases](experiments/R.md#r17); [upgrade path](UPGRADE_PATHS.md#up-r17) | [R17.VISITS](experiments/R.md#r17-visits) | B09 |
| [R18 — Jumbo sweep, order-block and rejection-block entries](components/RESPONSE_DEFERRED.md:231); [parent phases](experiments/R.md#r18); [upgrade path](UPGRADE_PATHS.md#up-r18) | [R18.STOP_INTERPRETATIONS](experiments/R.md#r18-stop_interpretations) | B09 |
| [R19 — Response-to-action and residual-management adapter](components/RESPONSE_DEFERRED.md:244); [parent phases](experiments/R.md#r19); [upgrade path](UPGRADE_PATHS.md#up-r19) | [R19.ENTRY_EXIT](experiments/R.md#r19-entry_exit) | B09 |
| [R20 — Pine structural and oscillator timing hypotheses](components/RESPONSE_DEFERRED.md:257); [parent phases](experiments/R.md#r20); [upgrade path](UPGRADE_PATHS.md#up-r20) | [R20.CAUSAL_VARIANTS](experiments/R.md#r20-causal_variants) | B09 |
| [R21 — Context-conditioned sequence alternatives](components/RESPONSE_DEFERRED.md:270); [parent phases](experiments/R.md#r21); [upgrade path](UPGRADE_PATHS.md#up-r21) | [R21.SOFT_CONTEXT](experiments/R.md#r21-soft_context) | B09 |
| [R22 — Blinded visual/source annotation and mechanism adjudication](components/RESPONSE_DEFERRED.md:283); [parent phases](experiments/R.md#r22); [upgrade path](UPGRADE_PATHS.md#up-r22) | [R22.BLINDED_DEFINITION](experiments/R.md#r22-blinded_definition) | B09 |

### Research and operations

| Parent and definition | Named refinements with local phases | Milestones |
|---|---|---|
| [V01 — Label, opportunity and evidence artifact service](components/RESEARCH_AND_OPERATIONS.md:6); [parent phases](experiments/V.md#v01); [upgrade path](UPGRADE_PATHS.md#up-v01) | [V01.LABEL_COVERAGE](experiments/V.md#v01-label_coverage) | B00, B03, B07, B08, B10 |
| [V02 — Chronological splits, purging and OOF dependency builder](components/RESEARCH_AND_OPERATIONS.md:19); [parent phases](experiments/V.md#v02); [upgrade path](UPGRADE_PATHS.md#up-v02) | [V02.LINEAGE](experiments/V.md#v02-lineage) | B00, B03, B07, B08, B10 |
| [V03 — Hypothesis, search-budget and multiple-testing registry](components/RESEARCH_AND_OPERATIONS.md:32); [parent phases](experiments/V.md#v03); [upgrade path](UPGRADE_PATHS.md#up-v03) | [V03.SEARCH](experiments/V.md#v03-search) | B00, B03, B07, B08, B10 |
| [V04 — Evidence gates and economic feasibility decision](components/RESEARCH_AND_OPERATIONS.md:45); [parent phases](experiments/V.md#v04); [upgrade path](UPGRADE_PATHS.md#up-v04) | [V04.POWER](experiments/V.md#v04-power) | B00, B03, B07, B08, B10 |
| [V05 — Drift, calibration monitoring and controlled adaptation](components/RESEARCH_AND_OPERATIONS.md:58); [parent phases](experiments/V.md#v05); [upgrade path](UPGRADE_PATHS.md#up-v05) | [V05.DRIFT](experiments/V.md#v05-drift) | B00, B03, B07, B08, B10 |
| [V06 — Historical/live parity, restart and deterministic replay](components/RESEARCH_AND_OPERATIONS.md:71); [parent phases](experiments/V.md#v06); [upgrade path](UPGRADE_PATHS.md#up-v06) | [V06.PREFIX_RESTART](experiments/V.md#v06-prefix_restart) | B00, B03, B07, B08, B10 |
| [V07 — Failure attribution and controlled diagnostic interventions](components/RESEARCH_AND_OPERATIONS.md:84); [parent phases](experiments/V.md#v07); [upgrade path](UPGRADE_PATHS.md#up-v07) | [V07.ORACLE_SCOPE](experiments/V.md#v07-oracle_scope), [V07.PLANTED_SIGNAL](experiments/V.md#v07-planted_signal) | B00, B03, B07, B08, B10 |
| [V08 — Resource-aware reproducible experiment orchestration](components/RESEARCH_AND_OPERATIONS.md:97); [parent phases](experiments/V.md#v08); [upgrade path](UPGRADE_PATHS.md#up-v08) | [V08.RESOURCE_FRONTIER](experiments/V.md#v08-resource_frontier) | B00, B03, B07, B08, B10 |

## Full-program backlog

| Milestone | Exact tasks |
|---|---|
| B00 | [B00.1](IMPLEMENTATION_BACKLOG.md:17), [B00.2](IMPLEMENTATION_BACKLOG.md:18), [B00.3](IMPLEMENTATION_BACKLOG.md:19), [B00.4](IMPLEMENTATION_BACKLOG.md:20), [B00.5](IMPLEMENTATION_BACKLOG.md:168), [B00.6](IMPLEMENTATION_BACKLOG.md:169), [B00.7](IMPLEMENTATION_BACKLOG.md:187) |
| B01 | [B01.1](IMPLEMENTATION_BACKLOG.md:28), [B01.2](IMPLEMENTATION_BACKLOG.md:29), [B01.3](IMPLEMENTATION_BACKLOG.md:30), [B01.4](IMPLEMENTATION_BACKLOG.md:31), [B01.5](IMPLEMENTATION_BACKLOG.md:32), [B01.6](IMPLEMENTATION_BACKLOG.md:33), [B01.7](IMPLEMENTATION_BACKLOG.md:170), [B01.8](IMPLEMENTATION_BACKLOG.md:171) |
| B02 | [B02.1](IMPLEMENTATION_BACKLOG.md:43), [B02.2](IMPLEMENTATION_BACKLOG.md:44), [B02.3](IMPLEMENTATION_BACKLOG.md:45), [B02.4](IMPLEMENTATION_BACKLOG.md:46), [B02.5](IMPLEMENTATION_BACKLOG.md:47) |
| B03 | [B03.1](IMPLEMENTATION_BACKLOG.md:57), [B03.2](IMPLEMENTATION_BACKLOG.md:58), [B03.3](IMPLEMENTATION_BACKLOG.md:59), [B03.4](IMPLEMENTATION_BACKLOG.md:60), [B03.5](IMPLEMENTATION_BACKLOG.md:172) |
| B04 | [B04.1](IMPLEMENTATION_BACKLOG.md:70), [B04.2](IMPLEMENTATION_BACKLOG.md:71), [B04.3](IMPLEMENTATION_BACKLOG.md:72), [B04.4](IMPLEMENTATION_BACKLOG.md:73), [B04.5](IMPLEMENTATION_BACKLOG.md:173) |
| B05 | [B05.1](IMPLEMENTATION_BACKLOG.md:83), [B05.2](IMPLEMENTATION_BACKLOG.md:84), [B05.3](IMPLEMENTATION_BACKLOG.md:85), [B05.4](IMPLEMENTATION_BACKLOG.md:86), [B05.5](IMPLEMENTATION_BACKLOG.md:87), [B05.6](IMPLEMENTATION_BACKLOG.md:174) |
| B06 | [B06.1](IMPLEMENTATION_BACKLOG.md:97), [B06.2](IMPLEMENTATION_BACKLOG.md:98), [B06.3](IMPLEMENTATION_BACKLOG.md:99), [B06.4](IMPLEMENTATION_BACKLOG.md:100), [B06.5](IMPLEMENTATION_BACKLOG.md:101), [B06.6](IMPLEMENTATION_BACKLOG.md:175) |
| B07 | [B07.1](IMPLEMENTATION_BACKLOG.md:109), [B07.2](IMPLEMENTATION_BACKLOG.md:110), [B07.3](IMPLEMENTATION_BACKLOG.md:111), [B07.4](IMPLEMENTATION_BACKLOG.md:112), [B07.5](IMPLEMENTATION_BACKLOG.md:113), [B07.6](IMPLEMENTATION_BACKLOG.md:176) |
| B08 | [B08.1](IMPLEMENTATION_BACKLOG.md:121), [B08.2](IMPLEMENTATION_BACKLOG.md:122), [B08.3](IMPLEMENTATION_BACKLOG.md:123), [B08.4](IMPLEMENTATION_BACKLOG.md:124), [B08.5](IMPLEMENTATION_BACKLOG.md:177) |
| B09 | [B09.1](IMPLEMENTATION_BACKLOG.md:132), [B09.2](IMPLEMENTATION_BACKLOG.md:133), [B09.3](IMPLEMENTATION_BACKLOG.md:134), [B09.4](IMPLEMENTATION_BACKLOG.md:135), [B09.5](IMPLEMENTATION_BACKLOG.md:178) |
| B10 | [B10.1](IMPLEMENTATION_BACKLOG.md:143), [B10.2](IMPLEMENTATION_BACKLOG.md:144), [B10.3](IMPLEMENTATION_BACKLOG.md:145), [B10.4](IMPLEMENTATION_BACKLOG.md:146), [B10.5](IMPLEMENTATION_BACKLOG.md:179), [B10.6](IMPLEMENTATION_BACKLOG.md:188) |

## Source, requirement and data obligations

- [Supplied-source routes](traceability/SOURCE_TO_DESIGN.md) and [findings](SOURCE_FINDINGS_AND_CONFLICTS.md): all 712 exact IDs, including every routed correction/exception and source-specific future fixture. The five DTM user requirements are included separately with the current prompt and active clarifications.
- [Conversation upgrade lineage](CONVERSATION_RECHECK.md): all 122 conversation table rows retain their experiment routes; review the substantive sequence of user question, proposed upgrade and corrected definition rather than only the final model name.
- [Requirements](REQUIREMENTS_TRACEABILITY.md), [external findings](EXTERNAL_RESEARCH.md) and [third-review primary checks](THIRD_REVIEW_RESEARCH.md): exact rows are also enumerated in the machine manifest.
- [Data capability audit](DATA_CAPABILITY_AUDIT.md): all 111 catalog dataset IDs appear in the manifest with source/schema/identity metadata. At B01 attach field/cohort eligibility, observed audit depth, critical defects, dependent units and resolution actions. A complete catalog entry does not mean usable or certified data.
- [Ordered backlog](IMPLEMENTATION_BACKLOG.md): every task above has an explicit deliverable and verification interface to build. Future example commands are not existing runnable modules.

## Coverage check and resumption

Build/check the plan manifest with `python review/system-refinement/build_scope.py`. This is a document utility. The future B00.7 implementation audit must fail on a missing unit, child, source clause, dataset eligibility record, task or required phase; on a stale definition hash; or on a claimed verified/evaluated state without evidence. Include deliberate omission, duplicate-ID, changed-contract and ledger-preservation fixtures. Cross-check actual dependency edges and clause assertions because a correct row count alone cannot establish coverage.

At each checkpoint preserve what is built, exact passing/failed results, selected/rejected/inconclusive branches, outstanding dependencies and the next eligible work. Continue from that record in the same implementation thread. Completing a checkpoint is not a reason to abandon the rest of the manifest.
