# Ordered implementation backlog

This is work to build after the planning task. Existing `review/` scripts performed bounded source/data audits only; the proposed `trading_research` commands below **do not exist yet and have not been run**. They specify reproducible CLI contracts to implement. No task here authorizes trades, purchases, external account changes or materially costly jobs.

The [complete handoff](IMPLEMENTATION_HANDOFF.md) and [versioned scope](IMPLEMENTATION_SCOPE.md) cover this entire B00–B10 backlog in one continuing implementation thread. Import all 153 parents, 191 refinements, source clauses and [specific upgrade bindings](UPGRADE_PATHS.md) at B00. Apply the [construction contracts](UPGRADE_CONSTRUCTIONS.md), exact local phases and definition refinements in every milestone; E0 is an early checkpoint. Keep implementation/evaluation/disposition evidence in a separate durable ledger that scope regeneration never overwrites.

Use a research package with independently importable `foundations`, `measurements`, `context`, `options`, `cross_asset`, `locations`, `gates`, `policy`, `execution`, `risk`, `response`, `validation` and `operations` modules. Start with a transparent Python reference implementation and columnar partition interfaces; compile/vectorize measured hot paths only after parity fixtures exist. A model ID is not a separate process. Keep schemas, units, clocks and reference arithmetic independent of a particular learner library. Pin toolchain/dependencies in the eventual repository and record them in every artifact manifest.

Proposed durable artifacts: immutable raw-source references; versioned instrument/calendar/availability tables; deterministic measurements; market-object event log; all-candidate decision tables; matured labels; chronological folds; OOF forecasts; calibrated models/gates; full order/day/account ledgers; trial registry; validation reports and promotion decisions. All paths are content/version addressed and have a readable manifest. Models consume only declared schemas/versions, never arbitrary full dataframes with unknown future columns.

## Milestone B00 — Contracts and verification skeleton

Prerequisites: this plan and final decisions ledger. Suggested effort: 3–7 engineer-days, high uncertainty; CPU-only, negligible compared with raw replay. Exit: executable schema/reference fixtures and registry, with no strategy outcome claims.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B00.1 | CC schemas with typed units/IDs/time/quality; F02 registry skeleton; exact arithmetic fixtures | `python -m trading_research.verify contracts --suite all` |
| B00.2 | Component/child registry containing every F/M/C/O/X/L/G/P/R/V card, target, owner, baseline, applicability and ten-part reference | `python -m trading_research.verify registry --require-traceability` |
| B00.3 | V01/V02 label/fold manifests and tiny causal reference generator, including ambiguous/censored outcomes | `python -m trading_research.verify labels --fixtures hand_checked` |
| B00.4 | V03 trial/change registry and V08 hash/cache/resource accounting; no hidden experiments | `python -m trading_research.verify provenance --fixtures mutation_and_restart` |

## Milestone B01 — Certify the usable data cohorts

Prerequisites: B00. Budget initially one-day/one-hour partitions and metadata scans with ≤48 GiB process RAM. Suggested effort 1–3 engineer-weeks; pilot CPU-hours measured before expansion. Exit: explicit usable/missing/estimated cohorts and zero critical semantic defects, not blanket archive certification.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B01.1 | F01/02/05 decoders with all supplied MBP fields and raw/decoded flags; derived BBO/trades, exact side/action semantics, sentinels and instrument/exercise/settlement registry; audit DBN outright versus spread | `python -m trading_research.audit instruments --manifest <approved_manifest> --report <path>` |
| B01.2 | F03/08 calendar/DST/session/roll/adjustment engine; historical and product-specific cutoff versions | `python -m trading_research.verify calendar --suite dst_holiday_roll` |
| B01.3 | F04/06/07 availability, quality and as-of join engine; future/stale quote/OI/macro fixtures | `python -m trading_research.verify availability --suite future_revision_stale` |
| B01.4 | Expand NQ/ES MBP-action-T versus standalone reconciliation by year, session, roll, auction and flag cohort; include T without F_LAST, combined gap/snapshot flags, multiplicity and side mismatches | `python -m trading_research.audit trade_streams --cohort <stratified_small> --max-memory-gib 48` |
| B01.5 | Full intended-partition key/gap/sentinel metadata audit and critical-column streaming checks; no full feature grid | `python -m trading_research.audit partitions --cohort <registered> --columns <critical_schema>` |
| B01.6 | O01/F07 chain listing/OI/quote joins, coverage masks and same-date NQ/ES/Nasdaq/S&P experiment cohorts | `python -m trading_research.audit chain_coverage --cuts <registered_cuts> --report <path>` |

Data acquisition tickets are outputs of this milestone, not automatic purchases. Prioritize missing information by the value of the dependent experiment: live receipt/queue telemetry, intraday cash-index price, additional quoted strikes/expiries, ES BBO gaps, PIT macro/earnings/constituents and optional depth. A unavailable expert must not prevent unrelated supported research.

## Milestone B02 — Deterministic measurements and faithful source objects

Prerequisites: B01 certified small cohorts. Suggested effort 2–4 engineer-weeks for tested measurement/object framework; full Pine port is not required. Initial CPU streaming budget 4–24 hours across selected partitions, revise from pilot. Exit: causal reference objects and reproducible all-candidate logs.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B02.1 | F09/F10/F11 bars/object revisions; M01/02 ordinary and size-cohort CVD true OHLC with exact partition sums | `python -m trading_research.verify measurements --suite cvd_cohort_ohlc` |
| B02.2 | M04–07/13 true volume/delta/TPO/footprint/VWAP and faithful bar-allocation comparator; calendar, leg, range and explicit Jumbo profile anchors | `python -m trading_research.verify profiles --suite anchors_bins_ties_volume` |
| B02.3 | M03/08/09/10/11/12 swings/SMT, native MBP action/side event rates and OFI, effort, aggression memory, opens/settlements and validity; trade-only/quote-only/combined input comparisons | `python -m trading_research.verify measurements --suite swing_flow_reference` |
| B02.4 | C01–04/21 exact Jumbo source clocks/path variants; L01–03/05–12/19 causal generators, no display-toggle numeric dependency | `python -m trading_research.verify objects --suite jumbo_profile_structural` |
| B02.5 | Faithful source-rule registry with explicit corrected-causal variants and benchmark-only defective Pine examples | `python -m trading_research.verify source_benchmarks --require-variant-provenance` |

For each Pine member, implement only justified formulas/mechanisms routed by traceability. The reviewed source itself remains the benchmark definition. Hardcoded unsupported probabilities, leaky HTF drawing behavior and truncated tails are not production requirements.

## Milestone B03 — E0 complete one-mini baseline early

Prerequisites: minimum B01, B02 C/L objects, B00 labels/splits. Can begin as soon as those minimal dependencies pass; do not wait for every specialist. Suggested effort 2–4 engineer-weeks, CPU replay and simple statistical trials; initial 8–40 CPU-hour research budget subject to measured throughput. Exit: a complete reproducible baseline report, even if results are negative.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B03.1 | P01/02/05/06/08/10/11 reference simulator with one-unit state, conservative marketable fills, full exits, costs, daily loss and boundary | `python -m trading_research.verify policy --suite one_mini_fill_day_risk` |
| B03.2 | Simple conditional-frequency/logistic path/value baselines, G03 calibration and G08 transparent selection; always-flat and simple time/range competitor | `python -m trading_research.experiment run --id E0 --stage inner --budget <registered>` |
| B03.3 | Simple end-to-end regularized tabular competitor with same information/cohort/search budget, full candidate logging | `python -m trading_research.experiment compare --id E0 --paired-by trading_date` |
| B03.4 | V06 prefix/restart parity, V07 failure report, V04 promotion/inconclusive/no-go decision with target gap | `python -m trading_research.report build --id E0 --require-ledgers --require-uncertainty` |

Negative E0 does not prove the full ambition impossible; it establishes the baseline and identifies data/selection/economic bottlenecks. It also prevents months of unintegrated specialist development without a complete economic check.

## Milestone B04 — Context and rich volatility E1/E3

Prerequisites: B03, OOF contracts and certified relevant data. Suggested effort 3–6 research/engineering weeks; initial CPU tabular/statistical trials, measured 1–8 GiB/trial target. Exit: independent expert metrics, common-target mixtures and economic ablations.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B04.1 | C03/05/06 Jumbo conditional paths, adaptive time/activity/auction windows and P-zone distributions; discovery inside folds | `python -m trading_research.experiment run --id E1 --stage nested` |
| B04.2 | C07/08/18/20/21 auction migration, participation, regime and session transitions; source hard-gate challengers | `python -m trading_research.verify forecasts --family context --check-availability` |
| B04.3 | C09–17/19/23/24 historical GK/YZ/Parkinson/RV/HAR/GARCH/jump/IV/VX/event/remaining-room specialists and G02 calibrated ensemble | `python -m trading_research.experiment run --id E3 --stage nested` |
| B04.4 | Translate forecast improvements into L04 width/location and G reach/payoff decisions, not just better variance error | `python -m trading_research.experiment ablate --id E3 --families <registered>` |

Unavailable macro vintages/intraday vol inputs stay masked/deferred. Train-free measures are shared; each forecast child/horizon has a separate score/calibration result. No forced equal gate weight or compulsory neural model.

## Milestone B05 — Options measurements, OI and dynamic actionable boards

Prerequisites: B01 chain/time gates and B03 complete harness. Suggested effort 4–8 research/engineering weeks for a tested first options stack; complex full-universe models extend this. Initial one-minute boards on a bounded common cohort; small GPU trials only after CPU baselines. Exit: validated units/coverage/OI labels and transparent dynamic-node E2 results with uncertainty.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B05.1 | O02–06 prices/sign/IV/surface/Greeks/reported-OI state, exercise/settlement-aware and missing-wing masks | `python -m trading_research.verify options --suite price_greek_surface_oi` |
| B05.2 | O15/16/18/20 contracts/premium/Greek-weighted CVD, flow breadth and multi-leg uncertainty; no next-IV lookahead | `python -m trading_research.verify options_flow --suite units_sign_group_time` |
| B05.3 | O07/08 aggregate next-OI models, expiry-aware labels, uncertainty and frozen/volume/learned holdings scenarios | `python -m trading_research.experiment run --id E2_OI --stage nested` |
| B05.4 | O09–14/17/21/22 exposure decomposition, stable node identity/topology, weighted centers and action-role experts; L13/14 | `python -m trading_research.experiment run --id E2_nodes --stage nested` |
| B05.5 | O19 separate NQ/ES futures-options contribution with definition/stat-publication/UDS gates | `python -m trading_research.experiment run --id E2_futures_options --stage nested` |

Do not require an OI forecast gain to imply economic gain. Test that propagation explicitly. Static observed OI may remain preferable if holdings uncertainty or quote coverage makes intraday updating unreliable. Unpublished Skylit/KG1 projections remain inspiration/benchmarks where observable, not reproduced formulas.

## Milestone B06 — Broad cross-asset transmission and joint boards

Prerequisites: B04/05 supported individual specialists and exact as-of joins. Suggested effort 3–6 research/engineering weeks plus any separately approved data dependencies. Resource class C for sparse set/graph trials: start within 4–14 GiB GPU, record actual throughput before scaling. Exit: fair NDX/QQQ and source-only receiver tests, then justified joint-model evidence.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B06.1 | X01/02 asynchronous alignment and related-coordinate mapping with cash-proxy/synthetic-forward uncertainty | `python -m trading_research.verify cross_asset --suite asof_mapping_basis` |
| B06.2 | X03/04 matched NDX/NDXP/QQQ and SPX/SPXW/SPY comparisons, instrument selection P12 on development only | `python -m trading_research.experiment run --id E2_chain_comparison --stage nested` |
| B06.3 | X05/L15 source reaction → NQ/ES opportunity without receiver touch; delay/common-driver/time-placebo controls | `python -m trading_research.experiment run --id E2_transmission --stage nested` |
| B06.4 | X06/O14 strike×expiry×chain×asset×time set/graph/temporal models against tabular pooled summaries on identical masks/targets | `python -m trading_research.experiment compare --id E2_joint --match-information-and-budget` |
| B06.5 | X07–10 cross-flow SMT, global futures/FX/metals/rates and supported slow context; explicit dependencies for constituents/COT/SHFE/SLV publication and X08.TRF/L12.PRINT receipt/correction/complete-print coverage. TRF research is deferred until its separate data gate; acquisition requires later authorization | `python -m trading_research.experiment ablate --id E2_joint --by source_family` |

## Milestone B07 — Location improvement, mixtures and sequential opportunity selection

Prerequisites: B03 plus relevant B04–06 specialist outputs. Suggested effort 3–6 research/engineering weeks; CPU models first and compact candidate tables. Exit: E1–E4 integrated ablations and full-stack improvement or documented rejection relative to E0/simple competitor.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B07.1 | L16–18 proposal refinement, object lifecycle/identity, correlated evidence groups and complete candidate sets | `python -m trading_research.verify locations --suite revision_lifecycle_density` |
| B07.2 | G01–05 compatible mixtures/calibration/reach/conditional path, missing-expert patterns and disagreement | `python -m trading_research.verify mixtures --suite oof_targets_masks_calibration` |
| B07.3 | G06–09 action value, nearer/deeper/wait/confirm/abstain comparison, P02 geometry and all rejected candidates | `python -m trading_research.experiment run --id E_selection --stage nested` |
| B07.4 | E4 exact profile/cohort-CVD contribution and matched placebos; keep Jumbo original profile anchors and delta variants | `python -m trading_research.experiment run --id E4 --stage nested` |
| B07.5 | G10/V05 controlled per-expert refit/retirement with frozen incumbent challenger | `python -m trading_research.verify adaptation --suite prequential_no_future` |

## Milestone B08 — Operational/account harness and conservative management

Prerequisites: B03 state/risk reference implementation; actual account choice is needed only for deployment-specific certification. Suggested effort 2–5 engineer-weeks plus broker/firm clarification. No external order is required for deterministic fault tests. Exit: full P03/04/07/09/10 simulation/parity drills and versioned rule scenarios.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B08.1 | P03 full-exit/trail/target variants and P04 cumulative re-entry lineage, tested separately from new entry alpha | `python -m trading_research.experiment run --id E_management --stage nested` |
| B08.2 | P07 deterministic broker-state adapter contract with simulated events, durable IDs/OCO/ack/fill/cancel reconciliation | `python -m trading_research.verify orders --suite races_reconnect_unknown` |
| B08.3 | P09 current product-version rule reference paths, P11 trading versus business cash and pending-payout accounting | `python -m trading_research.verify accounts --suite selected_rule_scenarios` |
| B08.4 | Independent risk/boundary/outage tests and V06 historical/live calculation parity | `python -m trading_research.verify faults --suite feed_order_boundary_restart` |

## Milestone B09 — Detailed Response later

Prerequisites: user's current C/L development sequence completed sufficiently for frozen opportunity comparisons, B07 candidate logs and relevant M/P measurements. Suggested effort assessed per R family after opportunity-decay/sample evidence; do not reserve a large neural program by default. Exit: E5 preserves all registered variants and promotes only incremental economic contributions.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B09.1 | R22 blinded observable annotation and ambiguous source-variant adjudication; no image-implied fills/identity | `python -m trading_research.verify annotations --suite provenance_and_blinding` |
| B09.2 | R01–10 approach/absorption/exhaustion/burst/top resilience/footprint/CVD measurements and finite-state baselines; R06 full-depth remains dependency-gated | `python -m trading_research.verify response --suite measurement_prefixes` |
| B09.3 | R11–18/20/21 distinct sequence branches and common-target mixtures, including no-retest, failed-resqueeze, quiet failure and Jumbo block variants | `python -m trading_research.verify response --suite branch_timing_failures` |
| B09.4 | R19/P03 entry versus exit refinement, same initial C/L opportunities and missed-winner/non-fill/delay accounting | `python -m trading_research.experiment run --id E5 --stage nested` |

## Milestone B10 — Frozen future evaluation and later decision

Prerequisites: V1–V3 evidence, frozen selected instrument/model/policy, quality/receipt/operational readiness and any needed read-only feed authorization. The elapsed future period cannot be compressed by faster compute. Choose the fixed future endpoint and power/precision assumptions before collection (≥60 eligible days is an initial planning scale, not an adequacy guarantee), or separately preregister a valid sequential-inference procedure with its dependence/process assumptions. Do not extend an ordinary-confidence-interval test until significance or a preferred precision/result appears. Actual account cash evaluation can take longer.

| Task | Deliverable and dependency | Verification command/interface to build |
|---|---|---|
| B10.1 | Freeze hashes, eligibility/denominator, thresholds, future start, stop/change rules and exact accounts/cost scenarios | `python -m trading_research.promotion freeze --experiment <id> --stage shadow` |
| B10.2 | Collect permitted live receipt/shadow candidate outputs, track parity/latency/drift; no unapproved orders | `python -m trading_research.shadow run --config <authorized_read_only>` |
| B10.3 | Evaluate matured future predictions, conservative simulated economics and operational faults without test-driven changes | `python -m trading_research.report build --id <future_id> --frozen-only` |
| B10.4 | V04 feasibility/inconclusive/no-go decision, objective gap and next evidence; prepare concrete later deployment review only if warranted | `python -m trading_research.promotion assess --id <future_id> --require-all-gates` |

## Resource expansion and cost estimation

Effort ranges above are planning estimates for an engineer/researcher working with reviewed source specifications, not commitments or measured throughput. They overlap in dependencies; do not sum them into a promised delivery date. Complex discoveries, missing data and negative experiments can extend the program. First complete B00–B03 and update estimates from actual bottlenecks.

For each expanded run calculate `CPU_hours = rows_to_scan / measured_rows_per_CPU_second / 3600`, adjusted for decompression, sorting, I/O and effective concurrency; GPU cost is measured trial-hours × registered trial count × quoted hourly rate. Storage is retained rows × measured compressed/uncompressed bytes per row × horizons/versions plus checkpoints; avoid multiplying the raw archive by every trial. Report ranges from liquid/stressed pilot days and cold/warm cache runs. The inspected pod offers ~17.85 CPU quota, ~77.3 GiB RAM and 16 GiB GPU, not the host's advertised full resources. Use 48 GiB streaming RAM cap initially and leave GPU margin.

A provisional additional 1–3 TB research-storage envelope is unverified and needs the user's actual quota/cost context before allocation. Scale to larger-memory/multiple workers only for measured partition/replay bottlenecks; larger GPUs are optional for justified joint/sequence models after small-model evidence. Obtain current prices at procurement time, present a bounded run and expected artifacts, and seek authorization for purchases/materially costly work. Routine document planning and bounded audits here did not constitute that approval.

## Binding corrections from the second design review

Before B01 feature/forecast integration, add the port registry and `T-DAG` compiler/OOF negative fixtures specified in [COMPUTATION_SCHEDULE.md](components/COMPUTATION_SCHEDULE.md). This is a B00/B01 prerequisite, not a later cleanup task. Build X02 raw-parity bootstrap before O02 IV; keep O03 sign usable independently of IV. B04 volatility comparisons include C23 Parkinson and C24 ARCH/GARCH. Options and M09 implementation must include the second-review sign, timing and net-recovery fixtures in VALIDATION_PLAN.md. No command for these future modules has been run during planning.

The final source-clause audit adds O23’s per-expiry settlement-payoff benchmark to B05/B07, C04.OPEN_TYPE prefix/label fixtures to B04, and R11.FA_POC/FA_VALUE distinct prior-balance sequences to deferred B09. They inherit the same evidence gates; source naming does not imply profitable behavior.

## Third-review additions within the existing milestones

These are binding elaborations of B00–B10, not a second implementation track. All commands and trading tests remain future work.

| Task | Concrete deliverable and prerequisite | Required evidence |
|---|---|---|
| B00.5 | Import all 153 parent and 191 named refinement contracts with their eight phase records; expand each listed local case into named expected assertions | Registry/source/target coverage; explicit applicable/inapplicable fields; no empty name-only tests |
| B00.6 | Implement capability, fixed-end horizon, incremental/macroaction reward, standing-quote, geometry and duplicate-assimilation reference fixtures | T-CAPABILITY/T-HORIZON/T-REWARD/T-STANDING-QUOTE/T-GEOMETRY/T-OI-ASSIMILATION |
| B01.7 | Certify VIX/VIXW product/venue/condition/clock/rate rules and broaden the bounded VIX quote/OI audit; distinguish UX data dependency | Quote/OI expiry support, parity inconsistency, IV intervals and historical source rules |
| B01.8 | Dataset/field/cohort readiness ledger covering all 111 catalog datasets; preserve completed audit depth, unresolved semantics and each dependent expert | F01/F05/F06/F07; apply MARKET_DATA_SOURCE_CONTRACT and the family readiness matrix; no family becomes certified from inventory alone |
| B03.5 | Implement the exact E0_REFERENCE_EXPERIMENT, including minute decision/contact semantics, full-unit brackets and frozen cost/feed/order-delay scenarios | Complete causal label/order/day/account reference and always-flat/simple/model comparisons |
| B04.5 | Run individual range, auction, physical-volatility, IV/skew/term/event/VIX and remainder experiments, then prespecified mixtures/interactions | Per-unit P0–P6 artifacts and matched information/model capacity; no variance-to-path shortcut |
| B05.6 | Restore all Greek-flow channels including vega; fit primitive joint surface scenarios before dependent node dynamics; test uncertainty and one-time evidence assimilation | Per-channel units/OOF/ablation; acyclic C15.SCENARIO port; node/runner increment |
| B06.6 | Test broad source families, price/cohort-flow SMT and source-only transmission with actual per-source cadence | Same-date/common/full cohorts, lag/placebo and native-unit checks; missing-data gates |
| B07.6 | Compare every Location generator/refinement and target-matched selector; separate candidate/scorer tests, model sharing and exact in-set diagnostics | Density/width/age controls, input lineage, reward/occupancy parity and whole-policy ablation |
| B08.5 | Implement independent scheduler/atomic risk reservations and boundary-truncated late-session plans | Overload/timeout/duplicate-intent/restart/late-forecast fixtures and measured latency |
| B09.5 | Decompose each Response sequence into observed prefixes, failed branches and source variants; compare entry and exit contributions separately | Same initial C/L population, stage/delay/non-fill/management attribution; all detailed R work remains later |
| B10.5 | Produce component quality scorecards, learning curves, planted/null controls, useful-effect/power plans and fixed-endpoint future protocol | Supported/not met/inconclusive decisions, complete trial ledger, no ordinary-CI optional stopping |

## Complete-scope continuation and evidence

The [implementation handoff](IMPLEMENTATION_HANDOFF.md) and [full scope](IMPLEMENTATION_SCOPE.md) bind all milestones to one continuing implementation workflow. Import the exact component, child, source, requirement, dataset and task IDs; maintain a separate append-only implementation/evidence ledger. B00–B03 is the opening sequence and E0 the early economic checkpoint. B04–B09 remain required research scope; B10 remains required future evidence when its elapsed-time and access dependencies are available. An unavailable branch receives a specific dependency and next action while independent work continues.

| Task | Concrete deliverable and prerequisite | Required evidence |
|---|---|---|
| B00.7 | Import the versioned complete scope manifest; create separate per-unit/phase implementation, verification, evaluation and disposition records; resolve later scope deltas explicitly | Exact-ID diff against all parent/child/source/requirement/dataset/backlog registries; omission negative fixture; regenerating scope cannot overwrite empirical status |
| B10.6 | Reconcile the entire scope and dependency graph before declaring completion, preserving unresolved future or data-dependent work | No missing/unstarted work silently counted complete; supported/rejected/inconclusive/blocked outcomes carry artifacts, reasons and next actions; report engineering and economic evidence separately |
