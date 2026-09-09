# Research, validation and operational services

Binding additions: the [specialist experiment program](../SPECIALIST_EXPERIMENT_PROGRAM.md) supplies per-parent and per-child phases; [runtime scheduling](RUNTIME_SCHEDULER.md) fixes publication and state behavior. These elaborate the cards without declaring any trading test passed.
[Common contracts](COMMON_CONTRACTS.md) apply. These services make every specialist independently testable while preventing local model scores from substituting for complete sequential economics. Deterministic evidence handling is preferred; learned anomaly models are optional challengers, not authorities over provenance, splits or risk.

## V01 — Label, opportunity and evidence artifact service

1. **Purpose/sources.** Implement CC-04 targets and immutable candidate/outcome linkage; DEN-01, AUT-07, RFE/OFM causality lessons and prompt validation requirements.
2. **Inputs.** F10 objects/versions, full decision sets including rejected/untraded candidates, F04 information cuts, future observation streams used only after maturity, P05 scenario and account paths. Store event/known/label-maturity times separately.
3. **Definition.** Version each label by target, horizon, observation process, barrier/width, tie/censor and subsequent policy. Generate reach, ordered departure, path, next-report OI and simulated economic labels using frozen decision geometry. Label revisions append versions. Candidate omissions are detectable by matching generator event counts and hashes. Binding local refinement: [SR-V01](../SYSTEM_REFINEMENT.md#sr-v01).
4. **Outputs.** `Outcome` tables, dataset/label manifests, censor/ambiguity counts and provenance graph. No-training target exists for exact bookkeeping; analytic reference fixtures validate labels.
5. **Dependencies.** F01–11, C/L opportunity generation and P replay; V02 partitions interval spans, every learned card consumes versioned labels.
6. **Comparators.** Independent transparent reference labeler versus optimized implementation. Statistical annotation quality model optional; cannot redefine labels after seeing test performance. Binding further upgrade and child comparisons: [UP-V01](../UPGRADE_PATHS.md#up-v01).
7. **Learning.** Label horizon is selected in development; outer/future labels may mature later but never change earlier inputs. Store incomplete/expired/non-filled examples and OI publication gaps.
8. **Tests.** T-V01: both barriers inside coarse bar, gap across level, object revision, censored close, future OI report, disappearing 0DTE, rejected candidate and changed management policy.
9. **Acceptance.** Exact reference agreement where observable; bounded/ambiguous outputs where not. Candidate and label coverage reconcile by day/model/family; no silent dropping.
10. **Ablation/fallback/resources.** Label-definition sensitivity registered separately from model tuning. Invalid labels quarantined with reason, never silently zero-filled. Class D; columnar event/decision tables and content-addressed caches.

## V02 — Chronological splits, purging and OOF dependency builder

1. **Purpose/sources.** Make all granular mixtures and downstream learning time honest; CC-05/06, RFE-09/10 and the trial-selection limitations in TECH-10; the chronological/OOF protocol below is this plan’s engineering design, not a claim established by the offline-policy paper TECH-11.
2. **Inputs.** Eligible-date registry, feature availability/state intervals, label spans/maturity, instrument/parent-object IDs, coverage cohorts and model dependency DAG. Split specification itself has version/hash.
3. **Definition.** Group all correlated assets and same-date opportunities in one chronological fold. Purge training examples whose future outcome/label span or fitted-state dependencies overlap evaluation decisions/outcomes in a way that transfers held-out information. Embargo must account for label maturity, carried state and repeated parent opportunities. A causal evaluation feature may legitimately reuse earlier raw observations also used by training features; shared past lookback alone is not leakage and does not trigger blanket purging. Record the exact forbidden overlap rule and use horizon/state-aware embargo when dependence warrants it. Create inner OOF predictions for every learned upstream dependency before fitting downstream/calibration/gates. Keep train/tune/calibrate/outer-test roles explicit. Binding local refinement: [SR-V02](../SYSTEM_REFINEMENT.md#sr-v02).
4. **Outputs.** Fold manifests, excluded-row reasons, upstream OOF prediction keys and leakage-audit report. Same row cannot have both training and evaluation roles for the same fitted decision chain.
5. **Dependencies.** V01/F11 and all learned components; V03 registers split changes and V04 consumes untouched evaluations.
6. **Comparators.** Simple expanding/rolling walk-forward; blocked sensitivity analysis. Reverse-time or rotating future-trained folds are diagnostics only, never deployable forward evidence. Binding further upgrade and child comparisons: [UP-V02](../UPGRADE_PATHS.md#up-v02).
7. **Learning.** Scalers, feature discovery, cluster definitions, node mapping, selected windows, gates and calibrators refit inside appropriate folds. Historical lookback into past training data is permitted; future labels are not.
8. **Tests.** T-V02: overlapping horizons across midnight, same-date NQ/SPX split, stale OOF replaced with in-sample predictions, longer-lived swing/OI dependency and normalization leakage.
9. **Acceptance.** Zero unexplained interval/role violations; report exact dates/counts and effective blocks. No arbitrary fixed embargo percentage substitutes for span analysis.
10. **Ablation/fallback/resources.** Compare window length/embargo sensitivity on development only. Invalid DAG/fold stops training. Class D/B; cache predictions by fold/model/input hash, not model name alone.

## V03 — Hypothesis, search-budget and multiple-testing registry

1. **Purpose/sources.** Retain ambitious expert discovery without tiny-sample winner chasing; AUT-04, PIN hardcoded probabilities, RFE-09/10 and TECH-10. TECH-11 separately informs the limited counterfactual-policy estimators in G06/G07; it is not support for trial correction.
2. **Inputs.** Source finding/requirement IDs, component/child ID, target/data cohort, expected contribution, baseline, parameter search space, compute budget, primary metric, minimum useful effect and stopping rule before evaluation.
3. **Definition.** Register every attempted feature/window/threshold/model/selection policy, including failed/abandoned runs. Distinguish information gain, representation gain and policy gain experiments. Maintain family-level discovery and confirmation; correct/select using nested validation and dependence-aware uncertainty, with DSR/selection diagnostics as supporting evidence, not a proof of edge. Binding local refinement: [SR-V03](../SYSTEM_REFINEMENT.md#sr-v03).
4. **Outputs.** Trial manifest, search history, paired comparison report, selected/frozen configuration and rejection/deferral reason. Report known missing prior trial history as a limitation.
5. **Dependencies.** V02 splits and V08 scheduler; all component `-ABL/-PRED/-ECON` tests reference registry IDs.
6. **Comparators.** Prespecified small grids/random search and regularized baselines; more complex optimization gets matched budgets and an incremental justification. Binding further upgrade and child comparisons: [UP-V03](../UPGRADE_PATHS.md#up-v03).
7. **Learning.** Early stopping uses training/inner validation only; never stop a future test at a favorable equity peak. Rare subgroup exploration remains exploratory until independently confirmed.
8. **Tests.** T-V03: repeated configuration with different name, unlogged failed run, test-driven threshold change, future-selected asset and search-count omission.
9. **Acceptance.** Reproducible selection record and untouched confirmatory period; report uncertainty in effect and trial dependence. No fixed “100 trades enough” criterion.
10. **Ablation/fallback/resources.** Compare discovery benefit under equal information/search budgets. Exhausted budget means documented unresolved/reject decision, not hidden additional search. Class B/D, small registry plus metric artifacts.

## V04 — Evidence gates and economic feasibility decision

1. **Purpose/sources.** Translate perfection/10–20× ambitions and $2,000/day into falsifiable promotion criteria; prompt, RFE/OFM conflicts and current account research.
2. **Inputs.** Semantic/causality/fault reports, outer/future predictions, paired end-to-end net/day/risk paths, uncertainty, trial registry, coverage and selected account assumptions.
3. **Definition.** Gate in order: specification→data/semantic integrity→predictive validity→integrated economic/risk benefit→frozen shadow/operational parity→separately authorized deployment. Feasibility labels are “supported at declared uncertainty,” “not met,” or “inconclusive.” A profitable local experiment cannot skip an earlier gate. Binding local refinement: [SR-V04](../SYSTEM_REFINEMENT.md#sr-v04).
4. **Outputs.** Signed/versioned research decision with effect intervals, failure ownership, required next evidence, no-go conditions and objective gap. Explicitly distinguish proposed tests from completed ones.
5. **Dependencies.** V01–03/05–07, P11/12 accounting and firm-rule verification. A component can be retained for an exact invariant/risk benefit with stated return tradeoff.
6. **Comparators.** Always-flat, faithful source benchmark, simple end-to-end model, incremental complete stack and constrained account scenarios. Economic confidence procedure is predeclared. Binding further upgrade and child comparisons: [UP-V04](../UPGRADE_PATHS.md#up-v04).
7. **Learning.** Promotion thresholds/minimum useful effects chosen using development economics/measurement uncertainty and frozen; future/shadow interval start fixed before outcomes are inspected.
8. **Tests.** T-V04: good AUC/negative net, favorable mean with risk breach, partial-cost report, excluded flat days, uncertainty crossing target and missing passive-fill evidence.
9. **Acceptance.** Zero critical integrity defects; economic evidence must satisfy [validation gates](../VALIDATION_PLAN.md). $2,000/day is a research target, never guaranteed by source win rates or a point estimate.
10. **Ablation/fallback/resources.** Simplify or reject components failing incremental value; stop deployment promotion on unresolved critical data/risk/operational defects. Class B/D; uncertainty resampling over complete dependent blocks, not individual touches.

## V05 — Drift, calibration monitoring and controlled adaptation

1. **Purpose/sources.** Support granular diagnosis/adaptation without opportunistic retraining; CRL ensemble ideas, RFE Q4 weakness and CC-08.
2. **Inputs.** Live/shadow feature masks/age, forecast distributions, matured labels, execution costs, expert weights and eligibility/exposure states. Monitor fast integrity continuously and statistical drift at declared daily/weekly maturities.
3. **Definition.** Track schema/missingness/latency, feature distribution, conditional calibration/proper scores, residual dependence, gate occupancy and economic residuals. Distinguish changed input availability, concept drift and normal variance. Predeclare alert, abstain, rollback, recalibrate and retrain actions; drift detection cannot authorize new model deployment. Binding local refinement: [SR-V05](../SYSTEM_REFINEMENT.md#sr-v05).
4. **Outputs.** Component-specific health state, alert evidence/window, fallback choice and proposed research ticket. Delayed labels remain pending; no future performance proxy substituted as truth.
5. **Dependencies.** F06/F12 quality, G09/10 applicability, V03 change control and P independent risk. Matured no-trade/shadow candidates included.
6. **Comparators.** Fixed seasonal bands, sequential score/coverage monitors, regularized multivariate anomaly model. Calibrate false-alert behavior on development streams. Binding further upgrade and child comparisons: [UP-V05](../UPGRADE_PATHS.md#up-v05).
7. **Learning.** Only past matured labels; refits evaluated prequentially and compared with frozen incumbent. Online state updates are distinct from parameter learning.
8. **Tests.** T-V05: feed outage versus true volatility shift, delayed OI labels, recurring session change, gate collapse, false-positive bursts and adverse execution drift with stable prediction score.
9. **Acceptance.** Report detection delay, false-alarm cost, fallback coverage and risk/net impact, not an arbitrary drift p-value alone.
10. **Ablation/fallback/resources.** Monitor family ablations and frozen-model challenger. Critical integrity invokes deterministic halt; statistical uncertainty invokes validated fallback. Class A/B, aggregated telemetry with capped retention.

## V06 — Historical/live parity, restart and deterministic replay

1. **Purpose/sources.** Prevent Pine repainting, board hindsight and restart inconsistencies from entering production; PIN findings, SKY nearest-snapshot issue and CC-01.
2. **Inputs.** Same canonical event stream, received-time replay profiles, model/definition versions, checkpoints and live computation logs; explicit missing receipt assumptions for historical cohorts.
3. **Definition.** Run shared deterministic calculation kernels behind historical and live adapters. Compare event-prefix hashes of measurements, objects, forecasts and decisions; replay with suffix removed, delayed or revised. Checkpoint plus suffix must equal uninterrupted state. Computation completion latency is part of availability, especially options surfaces/boards. Binding local refinement: [SR-V06](../SYSTEM_REFINEMENT.md#sr-v06).
4. **Outputs.** Parity report with first divergent event/component, numerical tolerance, artifact hashes and arrival-model scenario. Exact real historical arrival cannot be claimed where receipt times are absent.
5. **Dependencies.** F04/F09/F12, F11 artifacts and P07 state; every component is covered transitively.
6. **Comparators.** Transparent reference replay versus optimized streaming kernel; no separate formula implementation whose differences remain unexplained. Binding further upgrade and child comparisons: [UP-V06](../UPGRADE_PATHS.md#up-v06).
7. **Learning.** Model weights/scalers/calibrators frozen per replay; random seeds and nondeterministic hardware tolerances recorded. Do not “repair” past outputs using later corrected data.
8. **Tests.** T-V06: future-tail deletion, reordered equal-time batch, revision, DST/midnight, unfinished bar, nearest future snapshot, restart after order send and missed checkpoint write.
9. **Acceptance.** Zero unexplained semantic/state divergence; declared numeric tolerances justified by solver/unit error. Timing uncertainty quantified, not called exact parity.
10. **Ablation/fallback/resources.** Compare optimistic versus conservative arrival profiles; invalid parity blocks promotion. Class D, bounded replay plus checksums; use sampled deep traces and full daily decision hashes to manage storage.

## V07 — Failure attribution and controlled diagnostic interventions

1. **Purpose/sources.** Fulfill user's independently measurable expert ambition and distinguish component failure from whole-system failure; DTM/CRL/DRF lessons.
2. **Inputs.** Full provenance DAG, candidate/rejection logs, forecasts/labels, fills/costs, management/account paths and coverage/cohort identifiers.
3. **Definition.** Attribute first incorrect invariant separately from prediction error. Decompose economics into opportunity generation, reach/path calibration, ranking/waiting, fill/shortfall, management and risk constraints. Re-run paired frozen interventions replacing one component with its baseline on the same causal inputs. Oracle replacements are diagnostic ceilings only and never deployable performance. Binding local refinement: [SR-V07](../SYSTEM_REFINEMENT.md#sr-v07).
4. **Outputs.** Per-component/family/date failure report, candidate-density/missingness changes, paired effect intervals and unresolved interactions. Losses alone do not prove a process fault.
5. **Dependencies.** F11/V01 provenance, G/P logs, V02/03 fair comparisons; V05 drift context.
6. **Comparators.** Deterministic reconciliation and baseline replacement; additive error model or interaction attribution as diagnostic summary, not causal truth from correlated inputs. Binding further upgrade and child comparisons: [UP-V07](../UPGRADE_PATHS.md#up-v07).
7. **Learning.** Train diagnostic predictors on past held-out errors; do not fit explanations to the frozen future set then claim confirmation.
8. **Tests.** T-V07: calibrated signal losing from costs, correct level unreachable, missed runner from waiting, false duplicate confluence, wrong data sign and daily halt foregone winner.
9. **Acceptance.** Every material loss/defect class has traceable owner or explicit uncertainty; intervention deltas reconcile with full rerun, with interactions reported rather than forced additive blame.
10. **Ablation/fallback/resources.** One-at-a-time plus selected factorial family ablations under registry budget. Unknown attribution prompts experiment, not automatic model complexity. Class B/D; cache shared replay features.

## V08 — Resource-aware reproducible experiment orchestration

1. **Purpose/sources.** Make the full ambition feasible on measured hardware and scalable beyond it without launching unauthorized heavy work; the data audit’s resource envelope and prompt constraints.
2. **Inputs.** Hashed task DAG, data partitions/row estimates, measured throughput, RAM/GPU/storage caps, authorized compute budget and CC-09 resource class.
3. **Definition.** Execute read-only research pipelines by day/instrument/coverage cohort; materialize shared causal features once, then compact candidate tables and OOF predictions. Bound sorting/replay memory, spill to approved workspace, checkpoint resumable jobs and reserve headroom for OS/other tasks. No raw 37B-row dense feature cross-product. Binding local refinement: [SR-V08](../SYSTEM_REFINEMENT.md#sr-v08).
4. **Outputs.** Job manifest, provenance, resource telemetry, peak memory, throughput, compressed/uncompressed storage, success/failure checkpoint and estimated remaining cost with uncertainty.
5. **Dependencies.** F01/F11, V02/03 registered experiments; costly jobs and procurement remain later authorization decisions.
6. **Comparators.** CPU streaming and vectorized partition pipelines; GPU only for justified surface/set/sequence trials. Scale-out versus larger-node choice follows measured bottleneck. Binding further upgrade and child comparisons: [UP-V08](../UPGRADE_PATHS.md#up-v08).
7. **Learning.** N/A for scheduling semantics; extrapolate pilot throughput with explicit I/O/cache/concurrency limits, not host-core count or theoretical GPU throughput.
8. **Tests.** T-V08: memory cap, disk-full/partial artifact, interrupted job resume, input hash change, duplicate trial, GPU unavailable and stale cached fold output.
9. **Acceptance.** Reproducible outputs and measured resource bounds; per-stage budget estimate updated before expansion. Out-of-budget work remains proposed, not quietly executed.
10. **Ablation/fallback/resources.** Benchmark representative partitions before full scan; use compact CPU baselines while complex models await evidence/resources. Class D, inspected pod ~17.85 CPU quota/~77.3 GiB RAM/16 GiB GPU, actual budgets in the resource section of DATA_CAPABILITY_AUDIT.md.
