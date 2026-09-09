# Requirements and source-to-design traceability

The current prompt and active user clarifications govern scope. Prior assistant plans are evidence/ideas to assess, not approved architectures. Every row below identifies an implementation destination and a verification route; a proposed experiment is not a validated result. A source can contribute several mechanisms while its performance claim, identity narrative or mandatory restriction is rejected.

The complete source matrix is split for readability:

- [SOURCE_TO_DESIGN.md](traceability/SOURCE_TO_DESIGN.md): **712 distinct supplied-source table findings**, each with original idea/observation, exact evidence location, full clause-specific disposition/correction, component destinations and a distinct future `T-SRC-<ID>` case. This includes all five conversations, 39 PDFs, the standalone image, inventory/pull-list and all indicator members.
- [EXTERNAL_TO_DESIGN.md](traceability/EXTERNAL_TO_DESIGN.md): **96 Skylit findings and 18 primary-method/provider findings**, each linked to its exact source, reviewed scope/disposition and components/tests.
- [SOURCE_FINDINGS_AND_CONFLICTS.md](SOURCE_FINDINGS_AND_CONFLICTS.md): original mechanisms, every substantive chart/diagram addition, disputed interpretations, prior-conversation questions/ideas and detailed reasons. The matrix incorporates these clauses, including explicitly unavailable content; it does not replace them with a blanket approval tag.
- [component_registry.json](review/component_registry.json) and [source_design_routing.json](review/source_design_routing.json): machine-readable cross-reference used for coverage checks. The **153 component cards** each have ten numbered specification fields plus the binding common contracts. Child asset/horizon/variant IDs inherit the stated contract and receive separate metrics/ablations.

`T-<component>-...` means the applicable unit/property/synthetic/integration/predictive/economic/ablation cases in CC-07. `T-SRC-...` is a source-specific case to build: it must exercise **each** mechanism, exception, timing/units issue and exclusion in that finding, with named assertions. Evidence-only claims get provenance/arithmetic/non-adoption checks, not fictitious trading labels. All tests below remain proposed except the explicitly completed source/document/data-audit checks.

## Current prompt requirements

Component IDs link through the master [specification navigation](IMPLEMENTATION_PLAN.md). Validation families and acceptance gates are defined in [VALIDATION_PLAN.md](VALIDATION_PLAN.md); backlog IDs identify concrete build tasks.

| Requirement ID / prompt location | Required intent and design decision | Components / deliverables | Verification / milestone |
|---|---|---|---|
| U01 §1/§7 scope | Deliver an implementation-ready research/engineering plan; preserve sources/raw data; no production implementation, large training or trades | This package; V03/V08 | Source hashes/reconciliation; document QA; B00 |
| U02 §1 architecture | Retain Context/Location/Response reasoning but separate data, selection, policy, execution, management, independent risk and monitoring; explain changes | IMPLEMENTATION_PLAN; F/M/C/L/G/P/R/V | Directed schedule/interface review; V06/V07; B00/B03 |
| U03 §1/§5 granular experts | Every meaningful subproblem independently defined, benchmarked, calibrated where learned and diagnosable; no forced minimal taxonomy or novelty | 153 cards; CC-01–10; G01–03/09; V07 | Ten-field/card registry; target compatibility/OOF/ablation; B00.2/B07 |
| U04 §1/§6 objective | One-account one-mini mean net ≥$2,000 per eligible day including zero-trade days; daily loss objective ≤$1,000; feasibility unproven | P01/08/11, V04; ACCOUNT_CONSTRAINTS | T-ACCOUNT; complete eligible-day ledger and uncertainty; E0/V3–V4 |
| U05 §1 execution | Choose NQ or ES, prefer NQ; do not restrict information to execution asset or select asset by realized test-day profit | P12, X03/04/09; DATA_CAPABILITY_AUDIT | Matched-date/cost/coverage comparison, selection inside folds; B06.2 |
| U06 §1 sessions | All sessions allowed, flat at required day boundary; clocks/DST/holidays explicit | F03, C01/21, P10 | T-TIME/T-ACCOUNT/T-RESTART; B01.2/B08.4 |
| U07 §1 firm setting | Verify current official Tradeify/Lucid rules without choosing one restrictive product as architecture | ACCOUNT_CONSTRAINTS; P09–11 | Versioned reference account paths; actual terms before deployment; B08.3 |
| U08 §2 inventory | Enumerate actual supplied directory recursively, reconcile README/manifest, account for added/missing files, safely extract ZIP, no bundled-code execution | SOURCE_REVIEW_LEDGER; review inventories | Completed 52-file source reconciliation, 83-member static review |
| U09 §2/§3 exhaustive reading | Every supplied page/text/image/chart/table/annotation; original images enlarged; all passages to end; track actual viewed ranges | SOURCE_REVIEW_LEDGER and findings | Completed 580/580 PDF text and visual pages; five full conversations, all text/source lines and standalone image; local unreadability recorded |
| U10 §2 prior chats | Both DTM user messages and every other conversation; preserve questions and useful prior ideas while rejecting unapproved-plan authority | DTM/JCV/CEX/CRL/DRF rows; this matrix | 122 conversation table rows plus five DTM-U bullets; source-specific cases; second review |
| U11 §2/§3 synthesis | Cross-check Jumbo synthesis against original manuals/tweets; preserve distinctions lost in summaries and archive incompleteness | JSS/JTR/JXA/JFN, C01–06, M04/05 | Original visual/source citations, T-JUMBO/T-PROFILE; E1 |
| U12 §3 traceability/evidence | Every distinct idea/rule/exception has retained/modified/merged/benchmark/rejected/deferred/unresolved disposition; no invented text/formulas/results | 712-row matrix, external matrix, OPEN_QUESTIONS | Exact-ID coverage and source-specific clause cases; no orphan cards/findings review |
| U13 §2 data truth | Acquired inventory differs from request list; verify actual data proportionately, do not claim every row read | DATA_CAPABILITY_AUDIT; F01–08 | Completed path/size plus bounded audits; broader T-DATA certification B01 |
| U14 §4 Jumbo hidden branches | Single/double/no breaks, different single breaks, order/depth, EQ/quadrants, internal reversal/continuation versus extensions, hunts, prior RTH, transitions and news delays | C01–04/21, L01–03, R18 | T-JUMBO synthetic branch fixtures, faithful/corrected benchmarks and E1 |
| U15 §4 improve ranges/P-zones | Alternative time/activity/auction windows and calibrated conditional zones across assets/sessions/regimes, discovered inside folds | C05/06/20/21, L04/16 | T-RANGE/T-PLACEBO/T-OOF; E1/B04.1 |
| U16 §4 exact clocks/formulas | Source-specific anchors, range-multiple versus true SD, maturity, resets and availability remain distinct | F03/04/09, C01/06, M04–08/12, PIN cases | T-TIME/T-CAUSAL/T-RANGE; B01/B02 |
| U17 §4 rich volatility | Historical GK/YZ/Parkinson/RV, HAR/GARCH forecasts, jumps, IV/skew/term structure, VX/events and remaining room as ensemble research | C09–19/23/24, G02, O04 | T-RANGE/T-OPTIONS and E3 predictive plus economic ablations; B04.3 |
| U18 §4 auction/participation | Acceptance/rejection, balance/discovery, value migration, control, effort, aggression memory and cross-market relationships | C07/08/18, M04–06/09–11, X07–10 | T-PROFILE/T-CVD; E4 and source branch cases |
| U19 §4 full options universe | NDX/NDXP/QQQ, SPX/SPXW/SPY, futures options, VIX and other supported information, strikes/expiries retained with coverage | F02/07, O01–23, X03/04/06/09 | T-UNIVERSE/T-OPTIONS; DA appendix; E2/B05/B06 |
| U20 §4 dynamic dots/nodes | Screenshot OI initialization/flow update is a hypothesis; improve node identity, strength, persistence/migration, width and causal revisions | O06–14/17/22, L13/14/17 | T-NODES; static/mechanical/volume/learned-update factorial E2 |
| U21 §4 OI learning | Predict next reported aggregate OI from causal past observations; future report is label only; distinguish dealer positioning and expiry | O06–10/20/21, V01 | T-ASOF/T-OPTIONS; OI proper loss/calibration and board economics; B05.3 |
| U22 §4 surfaces/Greeks | Validate quotes, IV, no-arbitrage domain, exercise/settlement, skew/tenors and explicit Greek units; propagate uncertainty | O01–05/21, C15, X02 | Price/Greek finite-difference/surface/AM-PM/sentinel fixtures; B05.1 |
| U23 §4 separate flow meanings | Ordinary futures CVD; options contracts/premium/delta/gamma/vega/vanna/charm flow; unknown signs/multi-leg activity; no cross-unit merging | M01–03, O03/15/16/18/20 | T-CVD/T-OPTIONS; partition/unit/event-frozen versus repriced checks; E4/E2 |
| U24 §4 cohort flow/SMT | Size-proxy CVD per cohort, true within-bar OHLC highs/lows, inter-cohort divergence and trade-level cross-market SMT preserved | M02/03, X07, R10 | Same-close/different-extrema and aggregation reconciliation fixtures; E4 |
| U25 §4 exposure decomposition | Separate price/IV/time/holdings-assumption/expiry/universe/coverage change and interactions; no mechanical thickening=flow inference | O09/10/12, X06 | Exact change reconciliation and single-factor synthetic shocks; E2 |
| U26 §4 joint patterns | Joint strike×expiry×chain×asset×time representations, per-family experts/interactions/targets; no three-board ceiling | O13/14, X06, G01 | Set permutation, masks/coordinate features, pooled/set/graph/temporal fair comparison; B06.4 |
| U27 §4 NDX hypothesis | Explicit NDX/NDXP versus QQQ and combination for NQ; parallel S&P/ES test | X02–04, O21, P12 | Same-date/coverage/latency/uncertainty controls; E2/B06.2 |
| U28 §4 source-only event | SPX/SPY touch/reaction can originate NQ opportunity with no local QQQ/NQ node; mapping differs from transmission | X01/02/05, L15, C22 | T-CROSS, time/common-driver placebos and executable latency; E2/B06.3 |
| U29 §4 Skylit research | Heatseeker/core/patterns, Flowseeker, Atlas and relevant indicators/API semantics/images comprehensively accounted | EXTERNAL_RESEARCH and 96-row mapping | 41 full text +55 focused API semantic reviews; 87 images actually viewed; no proprietary reproduction/access claim |
| U30 §4 location families | Range/statistical/profile/swing/FVG/block/VWAP/settlement/aggression/options locations with causal identity, width, revision, map error, retest and expiry | L01–19, F10, M04–13 | T-PROFILE/T-NODES/T-CAUSAL, per-generator fixtures; B02/B07 |
| U31 §4 select now | Many competing levels: nearer now, deeper later, confirmation, wait/abstain; reach/response/payoff/fill/target room/opportunity cost | G04–09, L18, P01/02/05/06 | T-SELECT/T-FILL; same candidate population, non-fills and density controls; B07.3 |
| U32 §4 C/L origination | Context and Location both select and may originate reversals/continuations; no universal confluence/touch/Response gate | C22, L15/16/18, G08, R19 | Internal EQ continuation/source-only event/absent Response fixtures; E0/E1/E2/E5 |
| U33 §4 Response breadth | Preserve all observable ordered mechanisms, failures, alternatives and re-entry conditions; detailed development later | R01–22, M09–13, L19, P04 | T-RESPONSE/T-SRC; B09 after C/L; no-retest and quiet-failure alternatives explicit |
| U34 §4 observability | MBP-1 does not supply off-touch depth, queue identity, hidden inventory or dealer/participant labels | M09, O20/21, R05/06, P05 | Unavailable-depth and equivalent-observation fixtures; dependency masking |
| U35 §4 execution | Market/passive/wait/cancel/stop-limit, latency/adverse selection, stop/target/trail/duration/re-entry; whole mini only | P01–08, R19 | T-FILL/T-ACCOUNT, races/shortfall/budget; B03/B08/B09 |
| U36 §4 safety/operations | Freshness, replay/restart, duplicate handling, position reconciliation, monitoring/drift/fallback/kill switches | F04–12, P07–10, V05/06/08 | T-RESTART/T-SHADOW and fault injection; B08/B10 |
| U37 §5 ten-part contract | Every deterministic, statistical, learned, mixture, ranker and policy has inputs/math/outputs/dependencies/baselines/training/tests/acceptance/ablations/resources | CC and 153 component cards | Structural ten-field check plus actual semantic second review; B00 registry |
| U38 §5 genuine MoE | Common targets, diversity, masks/disagreement, calibration, missing expert behavior and downstream OOF predictions | CC-05/06, G01–03/09/10, R21 | T-OOF and mixture failure fixtures; B07.2 |
| U39 §6 causal validation | Future-tail removal invariant across features/objects/models/decisions, revisions and timestamps | F04/F11, V01/02/06 | T-CAUSAL/T-ASOF/T-RESTART; zero unexplained violations |
| U40 §6 chronology/search | Walk-forward/nested tuning, interval-aware purge/embargo, same-date asset grouping, trial control and actual frozen future | V02–04 | T-OOF/T-SEARCH/T-SHADOW; B00/B03/B10 |
| U41 §6 fair comparisons | Proper prediction/calibration metrics separated from decision/economics; simpler complete competitor; matched placebos; counterfactual limits | V01/03/04/07, G06–08, P05 | T-PLACEBO/T-SELECT/T-FILL; E0–E5 common-cohort ablations |
| U42 §6 uncertainty/diagnosis | Dependence-aware intervals by date/block, regime/year/session/coverage; failure ownership for all layers | V04/05/07 | Paired complete-path reports; no independent-touch t-test or oracle performance claim |
| U43 §6 conservative economy | Fees/spread/slippage/latency/impact/non-fill/cancel/outage/gap/daily/firm constraints and indivisible position | P01–11 | T-FILL/T-ACCOUNT/T-RESTART; gross-to-net and account reference paths |
| U44 §6 no-go | Evidence before research integration/shadow/later live; no guaranteed perfection/profit or hidden budget-driven success | V03/04; VALIDATION_PLAN gates | Frozen useful effects/budgets; fail/inconclusive decisions and retained trial history |
| U45 §7 early complete experiments | Early end-to-end benchmark alongside full specialist program, resource estimates from actual pod, scalable choices | E0–E5; B00–B10; V08 | E0 before complete complex stack; pilot throughput before large expansion |
| U46 §7 deliverables/coverage | Required durable files, exact review totals, remaining unavailable content and second gap/coherence review | README, all required files, SECOND_DESIGN_REVIEW | Document/reference/coverage QA plus substantive fixes; no claim unrun tests passed |

## DTM user messages and active clarifications

The five DTM-U bullets are requirements extracted from the **two** user messages at original lines 15–27 and 266–272. They are additional to the 712 table findings, not omitted by table parsing.

| Source ID | Requirement disposition / final destination | Verification |
|---|---|---|
| DTM-U01 | Retain C/L/R refinement, exhaustive review, Jumbo both Context/Location, hidden path distinctions and improved windows/P-zones: U02/09/14/15, C01–06, L01–04 | T-JUMBO/T-RANGE, source completeness |
| DTM-U02 | Retain independent synthesis, actual inventory audit, richer options/next-OI/screenshot/NDX/source-only events: U13/19–22/25/27/28, O01–23/X02–06 | T-DATA/T-OPTIONS/T-CROSS, E2 |
| DTM-U03 | Preserve all CVD constructions, likely GK/YZ/HAR interpretation, IV/VX/skew ensemble, granular MoE and broader joint boards: U03/17/23/24/26/29 | T-CVD/T-OOF/E3/E4; Q07 wording remains explicit |
| DTM-U04 | Retain contemporaneous competing-level selection, source-event transmission and additional PDFs beyond original attachment limit: U09/28/31 | T-SELECT/T-CROSS, all 39 PDFs accounted |
| DTM-U05 | Retain average across trading days, daily loss interpretation, one chosen NQ/ES, broad information, sessions/boundary and full detail: U04–07/37 | P08–12/T-ACCOUNT; user later resolves one account/zero-trade days |
| USR-20260905-01 | One account, one mini, eligible zero-trade days included; flat allowed; no copies/micros/partials/pyramiding in primary action set | P01/08/11/12 and position/account invariants |
| USR-20260905-02 | Ordinary/cohort trade and OHLC CVD, gamma/options CVD and trade-level SMT all retained; size proxies explicit; improve P-zones/absorption instead of importing accuracy | M01–03/O15/16/X07/R10; E1/E2/E4 |
| USR-20260905-03 | Current detailed focus C/L and supporting layers; detailed Response/management strategy development later. Preserve R mechanisms and neutral downstream evaluation interfaces now | C/L/M/F/G/O/X; P reference harness and R01–22 deferred; B09 dependency |
| USR-20260905-04 | Exhaustive all-chat/detail review still required; every expert testable; “perfect” translated to falsifiable evidence | SOURCE_REVIEW_LEDGER; CC/V04/V07 and ten-field check |
| USR-20260905-05 | Older plans crude but informative; rich actual chains including NDXP/SPXW explicitly retained; no old narrow scope ceiling | O01/X03/04/06; DA scope appendix and E2 |
| USR-20260905-06 | C/L may originate entries; Response can improve timing/filter/exits without universal prerequisite; compare waiting opportunity cost | C22/L15/G07/08/R19; E0/E5 and source-only fixture |
| USR-20260905-07 | Jumbo exact volume-profile anchors/delta profiles and second design review required; justified complexity | M04/05/L05/06; E4; SECOND_DESIGN_REVIEW |
| USR-20260905-08 | Preserve every historical question/doubt and propose substantial data-enabled improvements; 10–20× is aspiration, not validated magnitude | Full conversation matrix and per-card alternatives/ablations; V03/04 |
| USR-20260905-09 | Exclude old failed workspace archive from further inspection/adoption; supplied DRF discussion remains source with explicit exclusion | DRF-U10/A25 and prior numerical claims not used as premises; source boundary in findings |

## Third-review user requirements (2026-09-06)

| Source ID | Requirement disposition / final destination | Verification |
|---|---|---|
| USR-20260906-01 | Review the entire existing plan again, find omissions and improve it: THIRD_DESIGN_REVIEW and all component families | Full authored-design/coherence review; preserved baseline and document QA |
| USR-20260906-02 | IV/VIX illustrated the required depth of feature and model improvement across the entire system; it was not a request to center the program on a new execution asset or isolated asset audit | All F/M/C/O/X/L/G/P/R/V definitions, challengers and local phases; VOLATILITY_RESEARCH_SPEC is one family specification within that program |
| USR-20260906-03 | Improve every layer, including ideas not explicitly repeated in the latest messages | F/M/C/O/X/L/G/P/R/V experiment files and conversation recheck; parent/source coverage audit |
| USR-20260906-04 | Explain how to establish strong/best-supported signals for every Context/Location component | MODEL_QUALITY_AND_STOPPING_RULES; input fidelity, causal tests, proper scores, calibration, learning curves, matched challengers, interactions and complete-policy value |
| USR-20260906-05 | User places trust in model judgment; external claims of unique trading ability do not substitute for evidence | V03/V04 quality/inference gates; no adopted reputation-based edge or perfection claim |
| USR-20260906-06 | Use richer acquired MBP-1 events, aggressor side and flags; explain BBO terminology, audit breadth and implementation thread choice | MARKET_DATA_SOURCE_CONTRACT; E0/F01/F05/F06/M09/P05 corrections; all-167 MBP footer and bounded five-family audit; DATA_CAPABILITY_AUDIT readiness matrix; IMPLEMENTATION_HANDOFF |
| USR-20260906-07 | Make the complete implementation scope explicit as one continuing thread: all components, children, source clauses, datasets and B00–B10 milestones; E0 and asset/phase boundaries are checkpoints | IMPLEMENTATION_HANDOFF; IMPLEMENTATION_SCOPE; versioned machine scope and future evidence-ledger contract; exact-ID coverage and omission checks |
| USR-20260906-08 | Refine every small part of the plan, then perform a broad substantive upgrade pass; volume profiles, CVD/flow, Gamma and Context are examples. Preserve the source idea → existing improvement → further upgrade path, including the HAR/ARFI illustration; stronger measurement/representation may suffice without a learned model | SYSTEM_REFINEMENT covers all 153 parents; UPGRADE_PATHS adds 153 authored paths and 191 specific child scopes/comparisons/cases; UPGRADE_CONSTRUCTIONS registers shared algorithms/targets/ports. All 344 units retain P0–P7, exact source clauses and conversation lineage in the full handoff/scope; refinement_qa verifies document/ID binding, not empirical gains |

The [conversation recheck](CONVERSATION_RECHECK.md) explicitly routes all 122 conversation table findings to experiment units. The [third-review primary research](THIRD_REVIEW_RESEARCH.md) adds five focused entries to the earlier 114 external findings; these five use distinct R3-TECH IDs and their own declared read scope. The original supplied-source total remains 712.

## Data-audit and account-research consequences

| Evidence ID | Final design consequence / owner | Required verification |
|---|---|---|
| DA-01 | Earlier NQ trades potentially reconstructed from MBP Trade actions; two audited hours do not certify archive — F05/06, M01/02 | Expanded T-DATA reconciliation; B01.4 |
| DA-02 | ES BBO discontinuity creates common-cohort requirement — F07, P05/12 | Same-date execution comparison, no invented quotes |
| DA-03 | Missing receipts/sequence require partial ordering/arrival scenarios — F04/05/12, V06 | T-TIME/T-RESTART; later telemetry |
| DA-04 | Crossed/locked/zero and future/stale paired quotes need quality gates — F06/07, O02/03, P05 | T-DATA future/stale/auction fixtures |
| DA-05 | Listing/OI/quote coverage differs by expiry/strike/time — O01/21, F07 | T-UNIVERSE and coverage numerator/denominator audit |
| DA-06 | Sparse wings are estimates, not live observations; NDX/QQQ fair comparison — O04/21, X03 | Surface/coverage uncertainty and common-cohort E2 |
| DA-07 | OI effective date differs from known_at; next report label only — O06–08, F04 | T-ASOF/T-OPTIONS expiry/report fixtures |
| DA-08 | Native futures options lack BBO; definitions/sentinels/UDS require registry — F02/05, O19 | T-OPTIONS unit/instrument/stat-time fixtures |
| DA-09 | Typed sentinel/clock-skew handling precedes joins — F01/04/06 | Sentinel/reference-time and clock uncertainty fixtures |
| DA-10 | Broad actual assets allowed but intraday cash/ETF flow/constituents cannot be assumed — X01–10, C16 | Explicit information masks and unsupported-feature abstention |
| DA-11 | Current macro/earnings vintages do not certify PIT features — C17/X08/X10 | T-ASOF/T-UNIVERSE and D07 dependency |
| DA-12 | Observable flow/profile/top-book versus latent depth/identity boundary — M01–13/O21/R06/P05 | Invariant observability checks and correct proxy naming |
| ACC-01 contract math | Actual NQ/ES tick/point units and one-mini objective arithmetic — F02/P02/P11 | Exact USD/tick fixture; source CME links in ACCOUNT_CONSTRAINTS |
| ACC-02 Tradeify | Product/date-specific daily loss, trailing floor, boundary, holding, automation and payout rules remain separate — P09/10/11 | Versioned official-rule reference paths and actual terms before deployment |
| ACC-03 Lucid | Product/broker/version-specific boundary, news, automation conflict, payout/consistency/drawdown — P09/10/11 | Explicit conflicting-doc/actual-contract dependency; T-ACCOUNT |
| ACC-04 economics | One-mini strategy net differs from account eligibility/received business cash; pending payout and all failed fees retained — P11/V04 | Exact ledger reconciliation and Q01 accounting choice |

## Final source-synthesis decisions that apply across rows

Retain observable source mechanisms as research hypotheses and faithful **causal** baselines. Correct demonstrable arithmetic/side/time/availability defects in separately named variants. A leaky original can illustrate the defect but cannot supply a deployable baseline or an out-of-sample prior. Numerical author claims remain unverified unless a new registered experiment supplies independent evidence.

Reject universal requirements that every level be an extreme, that every asset touch its own node, that three indicators be independent confirmations, that gamma sign deterministically fixes day type, that a response stage guarantees a reversal, or that price/CVD/mean/median/mode can be interchanged. The sources themselves contain counterexamples. Keep these as explicitly named comparison policies only where the exact rule is observable and compatible with the primary action set.

Exclude multi-account replication, fractional/micro substitution, partial exits and adding contracts from the primary economic action set. Preserve their historical rationale in source rows and compare the corresponding **full-position** exit/hold/selection alternatives where meaningful. Reject current profit need, missed money or prior loss as a market target. Retain independent idea/day/account budgets and complete cash accounting.

Unpublished KG1/C-score/minimum-average/projection/trailing formulas, missing source videos/frames, remote-depth identities and old excluded-archive results remain unresolved/excluded as stated. Historical export, purchase and tool-execution requests quoted in conversations are provenance, not new operational authorization. Named outside methods with no supplied executable rule, including the Pax/Nick references in CRL-04, remain bounded source-definition research tickets; the observable opening-range/activity hypotheses are covered by C01/C05/L12. No unseen proprietary detail is invented.

All formal acceptance claims await implementation and the specified evidence. The completed second review checks that every source ID, requirement, component, test family and dependency has a destination and that the package is internally coherent; it does not certify trading performance.
