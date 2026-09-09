# Trading-model research and implementation plan

Completed planning baseline: **2026-09-06**. This package contains the exhaustive supplied-source review, proportionate market-data audit, external research, implementation specifications, validation protocol, ordered backlog, three design reviews and the subsequent full-system refinement/upgrade pass. It does not contain a production strategy, trained model, backtest result or demonstrated trading edge.

The primary experiment remains **one account, flat or one outright NQ/ES mini, preferably NQ; at least $2,000 average daily net across eligible days including zero-trade days; daily loss objective no greater than $1,000; flat at the required trading-day boundary**. No account copying, added units, partial exits or micro replacement can be used to satisfy that experiment. Feasibility is an empirical question.

## Read the design

For implementation, start with the [complete handoff](IMPLEMENTATION_HANDOFF.md), [full scope index](IMPLEMENTATION_SCOPE.md) and binding [MBP-1 source contract](MARKET_DATA_SOURCE_CONTRACT.md). One continuing implementation thread covers all B00–B10 milestones; E0 is an early checkpoint. The versioned scope enumerates every component, refinement, phase, source, requirement, dataset and backlog task, while the future implementation ledger preserves actual evidence separately. Futures BBO means the best-quote state derived from the full eligible MBP-1 event stream; preserve actions, reported sides and flags. The [data audit](DATA_CAPABILITY_AUDIT.md) distinguishes completed checks from remaining work for each major family.

For the latest complete pass, read [153 definition/interaction refinements](SYSTEM_REFINEMENT.md), [153 substantive upgrade paths with 191 specific child bindings](UPGRADE_PATHS.md), their [implementation constructions](UPGRADE_CONSTRUCTIONS.md), and [how we judge signal/model quality](MODEL_QUALITY_AND_STOPPING_RULES.md). Every component retains starting idea → existing conversation/plan improvement → remaining weakness → further upgrade → comparison/evidence/use. Stronger measurements and engineering methods can qualify without a new model. The earlier [third design review](THIRD_DESIGN_REVIEW.md) remains part of the preserved progression.

The [specialist program](SPECIALIST_EXPERIMENT_PROGRAM.md) still provides **191 named refinements alongside 153 parent contracts**, each with **eight explicit phases**: 344 experiment units and 2,752 proposed phase records. The new upgrades extend these units' local definitions, cases, comparisons and interactions. They are not counts of trained models or passing trading tests, and one representative variant cannot satisfy a whole family.

The [individual family experiments](experiments/README.md), [conversation recheck](CONVERSATION_RECHECK.md), [exact E0 reference](E0_REFERENCE_EXPERIMENT.md) and [runtime scheduler](components/RUNTIME_SCHEDULER.md) supply the local detail. The [volatility/IV/skew/VIX specification](VOLATILITY_RESEARCH_SPEC.md) is one detailed family specification within the full system.

Use [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the full architecture, then the [common contracts](components/COMMON_CONTRACTS.md) and [explicit computation schedule](components/COMPUTATION_SCHEDULE.md). The schedule separates measurements, local forecasts, joint forecasts, candidate generation, action value and independent risk so that no current forecast recursively depends on itself.

The design retains Context → Location → Response as market reasoning, with separate data, selection, policy, execution, management, risk and evaluation services. **Context and Location may originate entries.** Detailed Response development follows later; its source mechanisms and dependencies are preserved now. The neutral execution/risk harness is specified now because Context/Location improvements must ultimately be measured as complete one-mini outcomes.

There are **153 ten-part component cards**, with binding common time, units, schemas, learning, calibration, tests, fallback and resource contracts. Asset/horizon/variant children receive separate metrics, local fixtures, challengers and explicit P0–P7 phases in the experiment program. Component boundaries are for independent testing and diagnosis, not a requirement for 153 separate processes or neural networks.

| Component document | Cards | Responsibility |
|---|---:|---|
| [Foundations](components/FOUNDATIONS.md) | 12 | Instrument identity, calendars, availability, quality, replay and provenance |
| [Measurements](components/MEASUREMENTS.md) | 13 | Traded/cohort CVD and true within-bar OHLC, profiles, VWAP, swings and observable top-book flow |
| [Context](components/CONTEXT.md) | 24 | Jumbo paths, auction state, adaptive ranges, volatility specialists, events and remaining opportunity |
| [Options](components/OPTIONS.md) | 23 | Chains/surfaces/Greeks, uncertain OI updating, flow, exposure scenarios and dynamic node/path forecasts |
| [Cross-asset](components/CROSS_ASSET.md) | 10 | Coordinate mapping, NDX/QQQ and S&P comparisons, source transmission, joint patterns and broader context |
| [Location](components/LOCATION.md) | 19 | Causal level/zone families, revisions, retests, learned proposals and complete candidate sets |
| [Gates and selection](components/GATES_AND_SELECTION.md) | 10 | Common-target mixtures, calibration, reach/path/value, waiting and ranking |
| [Policy, execution and risk](components/POLICY_EXECUTION_RISK.md) | 12 | Full-position plans, fills/costs, independent risk, orders, boundaries and cash accounting |
| [Deferred Response](components/RESPONSE_DEFERRED.md) | 22 | Distinct ordered mechanisms, alternatives/failures and later prefix-value comparisons |
| [Research and operations](components/RESEARCH_AND_OPERATIONS.md) | 8 | Labels/OOF, trials, promotion, drift, parity, diagnosis and resource controls |

## Build and evaluate

[IMPLEMENTATION_BACKLOG.md](IMPLEMENTATION_BACKLOG.md) specifies B00–B10 deliverables, prerequisites, tests/interfaces to build, resource estimates and exit criteria. Its future CLI examples are not existing implemented commands. E0 is an early complete causal one-mini benchmark; E1–E4 isolate range, options/joint-market, volatility and flow/profile improvements. E5 evaluates added Response value after the current Context/Location program.

[VALIDATION_PLAN.md](VALIDATION_PLAN.md) separates semantic/causality gates, predictive calibration, sequential economics, prospective frozen shadow evidence and later deployment approval. It includes nested chronological tuning/OOF, same-date grouping, matched placebo levels, complete rejected-candidate/non-fill accounting, conservative cost/fill scenarios, account paths and failure attribution. No proposed trading-system test is reported as passed.

[SECOND_DESIGN_REVIEW.md](SECOND_DESIGN_REVIEW.md) preserves the preceding review; [THIRD_DESIGN_REVIEW.md](THIRD_DESIGN_REVIEW.md) records the current expansion and corrections. The review fixed forecast cycles, unit/sign ambiguities, arrival-versus-event valuation, locked-quote signs, nonnegative excursions, risk double-counting and under-linked source mechanisms. The reproducible [document audit](review/document_qa.json) checks card structure, exact-ID coverage, local links, recorded review extents and source preservation; it does not run the proposed trading tests.

## Evidence and traceability

| Artifact | Completed scope / purpose |
|---|---|
| [SOURCE_REVIEW_LEDGER.md](SOURCE_REVIEW_LEDGER.md) | 52 supplied files reconciled; all 580 pages of 39 PDFs read and actually viewed; five conversations/6,256 lines; two standalone indicators/2,009 lines; all 83 ZIP text/source members/51,659 lines; standalone image and enlarged panels |
| [SOURCE_FINDINGS_AND_CONFLICTS.md](SOURCE_FINDINGS_AND_CONFLICTS.md) | Exact original rules, visual additions, all conversation ideas/questions, contradictions, corrections, source limits and dispositions |
| [REQUIREMENTS_TRACEABILITY.md](REQUIREMENTS_TRACEABILITY.md) | 46 prompt requirements, active clarifications, all 712 supplied-source table findings and the earlier 114 external findings mapped to components and future cases |
| [DATA_CAPABILITY_AUDIT.md](DATA_CAPABILITY_AUDIT.md) | 111 dataset directories, 80,198 files and 322,136,177,617 bytes reconciled; bounded schema/row/timing/coverage audits, actual capability gaps and hardware envelope; not every market row inspected |
| [EXTERNAL_RESEARCH.md](EXTERNAL_RESEARCH.md) | All 96 indexed Skylit pages accounted: 41 full text reads, 55 focused generated-API semantic reviews and 87 images actually viewed; 18 focused primary-method/provider findings with exact read scope; [five third-review primary checks](THIRD_REVIEW_RESEARCH.md) bring external finding records to 119 |
| [ACCOUNT_CONSTRAINTS.md](ACCOUNT_CONSTRAINTS.md) | Official CME/Tradeify/Lucid references, product/version differences, conflicting public guidance and implications for later selected-account verification |

The plan improves the source methods through explicit conditional range/path forecasts, trade-derived profile/cohort flow, richer strike/expiry/chain/time representations, calibrated next-report OI scenarios, node dynamics and sequential act/wait value. These are falsifiable improvement proposals, not demonstrated 10–20× gains. Hidden inventory/identity, proprietary formulas, screenshot profit claims and mandatory confluence are not treated as observed truth.

Completed additional review evidence: [261,970-row bounded VIX feasibility audit](review/third-review/VIX_FEASIBILITY.md), [27 finite design-example assertions](review/third-review/DESIGN_EXAMPLES.md), [experiment/traceability audit](review/third-review/review_qa.json), and [full-system scope/upgrade audit](review/system-refinement/refinement_qa.json). The upgrade registry also records three focused method references with their actual read limits. These establish limited arithmetic/data/document facts; every proposed trading-system phase remains unrun.

## Remaining decisions and limits

[OPEN_QUESTIONS_AND_RISKS.md](OPEN_QUESTIONS_AND_RISKS.md) lists exact missing/cropped source material, unsupported data fields and resolution paths. All supplied passages/pages/members were reviewed; missing original videos, clipped text, degraded quantitative labels and two truncated Pine tails cannot be reconstructed. Intraday cash-index prices, complete quoted wings, true participant/dealer identity and full-depth queue behavior are not invented.

One accounting choice remains open: whether the $2,000 target refers to trading net after execution costs or withdrawable business cash after firm fees/splits/buffers. The recommendation is to use trading net as primary and report both ledgers. Actual product/terms, broker, live permissions and compute budget are needed before dependent deployment/procurement work; they do not block this plan. Source/raw data were preserved, and no trades, purchases, messages to others or production implementation were performed.
