# Validation and implementation status

The current user-directed phase order is **validation across all intended families and discretionary frameworks, then Context, then Location**. See the [active family delivery table](/workspace/planning/trading-research/STATUS.md). Prepared Context work and the approved Jumbo continuation remain checkpointed for the later phase.

The latest accepted [auction/flow check 8](/workspace/trading-research/reports/auction-flow-prepared-trades-storage-check8-review.md) passed 278 tests, all nine complete retained-value comparisons and three complete split-window comparisons. Eight attempts retain 2,809.745475 cumulative CPU seconds. The current source-only projection is 191,375 CPU seconds and 421.28 GB; downstream complete-cohort work is still missing, and full extraction has not started. Parallel source-unit execution and adaptive/soft cohort calculations are under implementation/review for the next combined registered check. They are not yet accepted evidence.

[Jumbo check 16](/workspace/trading-research/reports/jumbo-check16-complete-resource-review.md) passed 442 tests. All sixteen attempts and 1,473.051801 CPU seconds remain charged. The [complete continuation amendment](/workspace/trading-research/reports/jumbo-complete-workload-continuation-proposal-v2.md) was explicitly approved on September 8 at 08:18 UTC; full Context fitting and confirmation are deferred by the subsequent phase-order instruction. The [complete 2020–2024 descriptive extraction](/workspace/trading-research/reports/jumbo-complete-development-extraction13-review.md) remains available. No held-out predictive quality or complete all-family validation is claimed.

Active scope: **2026-09-07-research-v2**. The [research delivery table](../planning/trading-research/STATUS.md)
now tracks family statistics/timings, independently evaluated Context models and
Location quality. The next result is an actual-data Jumbo range/path/timing study.
The historical B00–B10 scope and evidence below remain intact; full E0/account/live
completion is later work under the [revised handoff](../planning/trading-research/IMPLEMENTATION_INSTRUCTIONS.md).

The [transition checkpoint](reports/research-scope-transition-checkpoint-v1.json)
retains the current source bytes, 27 review/repair reports, both execution-deviation
records and all registered budgets. The current 901-method source inventory has
not been executed as a shared run. The last accepted complete suite remains the
851-test measurement run. No actual family market-model evaluation is complete.

Historical engineering status: **B00–B03 are not complete.** The
[conformance audit](CONFORMANCE_AUDIT.md) records incomplete source review,
skipped gates and the corrected work order. Source-backed foundation extensions
are progressing; market and economic eligibility remain separate requirements.

| Evidence category | Current result |
|---|---|
| Definition/source closure | Incomplete for implemented units; original passages, source alternatives and named expected cases remain to be reconciled. |
| Engineering fixtures | All 851 assertions passed with no errors, failures or skips in the third registered combined measurement run, including the 563 earlier baseline assertions. Both failed attempts remain recorded. [Execution and limits](validation/ALL_MEASUREMENTS_EXECUTION.md) |
| Primary model period | 2020 onward through actually available eligible observations. Older data is optional for selected Jumbo/OHLC uses. [Policy](RESEARCH_PERIOD.md) |
| E0 integration candidate | Current source, labels, fitting, policy, replay and account changes are preserved at the research transition. Static reviews and repairs do not establish runtime correctness. The candidate is paused and unverified; E0 is outside the current research completion gates. [Checkpoint](reports/research-scope-transition-checkpoint-v1.json) |
| E0 execution deviations and budget | Both private execution deviations remain recorded, with passing output rejected and unknown resource use explicit. A separately registered one-attempt engineering amendment is unused; the original E0 family cannot be reused through the batch contract. No budgets were reset by the research revision. [First deviation](reports/e0-unregistered-execution-deviation.json), [second deviation](reports/e0-policy-account-execution-deviation-v2.json), [amendment](reports/e0-integration-amendment-registration-v1.json) |
| F02 registry/payoffs | Retirement, disjoint reused IDs, exact ticks/currency and conditional cash/share/future expiration obligations pass fixed examples. Dated product admission and full consumer integration remain open. [Case evidence](reports/f02-kernel-case-coverage.json) |
| F03 calendars/timers | Immutable calendar versions, named interval intersections, separate clock variants and durable internal timer applications pass fixed boundary/revision/restart cases. Dated venue and all-consumer integration remain open. [Case evidence](reports/f03-interval-case-coverage.json) |
| F04 replay/scheduling | Bounded durable domain merges, explicit ties, field/lineage invalidation and optional deadline/cost policies pass fixed cases. All-source consumer/data closure remains open. [Case evidence](reports/f04-replay-case-coverage.json) |
| F05 transactions | Immutable acquisition/correction lineage, atomic resolution batches, exact reversible reducers and conservative cross-vendor matching pass fixed cases. Native source mapping, condition semantics and cohort reconciliation remain explicit gates. [Case evidence](reports/f05-case-coverage.json) |
| F06/F07 quality and joins | Positive coverage spans, separate freshness clocks, field/operation eligibility and declared quote/OI roles pass fixed cases and literal-reference comparisons. Actual source quality thresholds and complete consumers remain open. [Case evidence](reports/f06-f07-case-coverage.json) |
| F08 coordinates and rolls | Point-in-time selection, coordinate lifetimes, immutable adjustment lineage and qualified cash arithmetic pass fixed cases. Native selected-contract cohorts and roll economics remain open. [Case evidence](reports/f08-case-coverage.json) |
| F09 shared bars | Exact shared trade summaries, whole-event activity clocks, correction prefixes, causal publications and legacy restore integrity pass fixed cases. Construction, lineage-copy and checkpoint costs are measured separately; this Python reference does not establish a total-runtime speedup. [Case evidence](reports/f09-case-coverage.json) |
| F10 object lineage | Atomic immutable versions, complete candidate ancestry, bounded history, targeted invalidation and int64 lifetime boundaries pass fixed cases. Exact source generators and full consumer integration remain open. [Case evidence](reports/f10-case-coverage.json) |
| F11 artifact/input closure | Committed semantic DAGs, actual read/fit provenance, chronological OOF routes, restored model serving and crash/concurrent publication boundaries pass fixed cases. Market model quality and arbitrary consumer coverage remain open. [Case evidence](reports/f11-case-coverage.json) |
| F12 arrival traces | Deterministic callback replay, raw-before-decode durability, clock/control identity, restart and fault traces pass fixed cases. Local resource measurements and synthetic latency arithmetic are distinct; actual live capture remains unrun. [Case evidence](reports/f12-case-coverage.json) |
| Native field validation | 882 prior-field assertions passed on 72 records in 24 fixed prefixes, with exact record/metadata bytes retained. Native file suffixes remain uncertified. [Report](reports/f01-native-prefixes.json) |
| Parquet physical fields | All 22 profiles have prefix evidence across two executions: 64 distinct rows and 719 fixed field expectations. The missing calendar profile passed a separate 103-check supplement. [Combined evidence](reports/f01-arrow-profile-coverage.json) |
| Data reconciliation | Seven nonempty paired NQ/ES hours matched. One ES hour had 112,476 standalone trades and no MBP rows. [Report](reports/trade-reconciliation-eight-hours.json) |
| Selected definition files | All 2,579 rows in ten NQ/ES 2021–2025 partitions decoded; every row lacked a raw multiplier. [Report](reports/definitions-ten-partitions.json) |
| Compact replay pilot | 1,444,105 MBP rows; 56,077 trades and 75,760 contracts, matching the earlier hour's trade totals. 1.26 CPU seconds and 563.93 MiB peak RSS. [Report](reports/compact-one-hour.json) |
| Dataset readiness | All 111 datasets inventoried; field/cohort audits have unequal depths. Inventory is not complete eligibility. [Report](reports/data-readiness-inventory.json) |
| Market prediction / E0 economics | Unrun. Learned-model and planted/null checks are synthetic. No market edge or $2,000/day result is established. |
| Scope | 4,173 exact obligations retained. Only B00.7 scope/evidence import is verified. [Checkpoint](reports/current-checkpoint.json) |

Current modules are partial references for clocks, units, data, measurements,
objects, learning diagnostics, runtime and neutral one-unit execution/accounting.
Their existence does not establish complete parent, child or phase implementation.
Original source/data/planning files remain inputs; the excluded archive has not
been adopted.

The [F01 source/case review](validation/F01_SOURCE_CASES.md) records original
passages, expected outcomes, failed runs and the remaining cases. Native
truncation/empty-input detection, schema checks and verified content-alias
identity are repaired. Bounded complete MBP Parquet admission survives process
death and rejects partial output. Native fields now retain versioned layouts,
sentinels, unknown bytes and original metadata. Wider schema/native admission,
domain semantics and complete source/cohort validation remain opening requirements.
The [consolidated review](validation/BATCH_REVIEW_2026_09_06.md) records all 27
cases, exact assertions and both post-repair verification results.
The direct handoff documents, full refinement/upgrade text, all 712 source
routes, all 122 conversation routes, and the 119 external findings have now
been reviewed at the governing-document level. The
[reading record](reports/governing-reading-progress.json) preserves exact file
hashes and reading extents. Each unit still needs its own original-passage,
expected-assertion and executed-evidence closure.

Published Tradovate Free and Tradeify-through-Rithmic fees are recorded in
[the fee configuration](configs/fee-scenarios.json). The
[cash RTH calendar](configs/cash-rth-calendar.json) preserves announcement-time
revisions; it is not a CME or broker deadline certification. A
[dated NQ multiplier reference](configs/product-terms.json) is explicit external
evidence; other missing contract/universe facts remain unresolved. The
[opening gate review](validation/E0_MINIMUM_GATE_REVIEW.md) now records a
specific exact-E0 dependency: supplied `NQ.c.0` follows calendar expiry rank,
while E0 selects by preceding-session volume over a complete eligible
outright universe. The catalog does not supply that parent outright cohort.
The [23 F02 cases](validation/F02_SOURCE_CASES.md) distinguish existing partial
assertions from the remaining identity, option/payoff and mapping work.
The subsequent [F02 kernel batch](validation/F02_KERNEL_BATCH_REVIEW.md)
extends those cases with exact reference kernels. It passed in one combined
execution using 27.25 CPU seconds and 161.32 MiB peak RSS; this is engineering
evidence, with no new market tape or economic run.

The [F03 source catalogue](validation/F03_SOURCE_CASES.md) retains all 74 assigned
findings, 47 original static files, 41 visually inspected PDF pages, the original
image and conversation passage. The [interval/timer review](validation/F03_INTERVAL_BATCH_REVIEW.md)
collected twelve findings before one consolidated repair. All 288 methods passed
on the first registered run, using 29.71 CPU seconds and 160.26 MiB peak RSS.
The journal atomically applies internal JSON state; complete runtime/consumer
integration and external order effects remain separate contracts. No historical
venue cohort or economic result is admitted by these synthetic cases.

The [F04 review](validation/F04_REPLAY_BATCH_REVIEW.md) collected ten findings before one consolidated repair. Three Astra agents at the user's requested low effort split tests and review, then prepared subsequent source units in parallel. All 321 methods passed on the first run in 30.40 CPU seconds, 60.51 wall seconds and 151.00 MiB peak RSS. The seven-cut arithmetic comparison retained identical values and lineage while reducing operations from 20 to 12; this is a synthetic engineering result. The [58-source case record](validation/F04_SOURCE_CASES.md) preserves original confirmation, display, OI and receipt limitations.

Current next action: admit the exact OHLC/range/path windows needed for the Jumbo
study, validate its definitions and outcomes, measure a bounded actual-data pilot,
then expand to its declared eligible cohort. Reuse shared evidence and keep
calendar, roll, missing-window and OHLC-order limitations local to the study.
Historical E0 and B10 dependencies remain recorded for their later trading purpose.

Historical evidence remains available: [49 tests](reports/initial-verification.json),
[96 tests](reports/runtime-measurements-verification.json), and
[147 tests](reports/quality-objects-execution-verification.json).

The [F05–F08 batch review](validation/F05_F08_BATCH_REVIEW.md) collected 36 findings before one consolidated repair. Its first shared execution passed all 417 methods using 34.69 CPU seconds, 72.74 wall seconds and 161.85 MiB peak RSS. One physical run was conservatively charged to its three registered families; duplicate family telemetry is not summed. Immutable review, coverage, code, assertions and lifecycle artifacts were attached through one idempotent ledger transaction. No native market, model fit or economic run occurred in that batch.

The [F09–F12 execution record](validation/F09_F12_EXECUTION.md) adds 146 methods over that baseline and passes all 563 in one run: 59.22 CPU seconds, 106.15 wall seconds and 219.55 MiB peak RSS. All 125 frozen cases and 102 prepared case bindings are retained.

The [combined measurement execution](validation/ALL_MEASUREMENTS_EXECUTION.md) adds 288 assertions for M01–M13, C01/L01, M12/L02/L03, V01/V02 and B00 decision contracts. All 851 passed in 97.73 CPU seconds, 217.32 wall seconds and 225.18 MiB peak RSS. Eight families share one physical run and one attachment transaction; their duplicated telemetry is not summed. The complete review and initial consolidated repair were followed by two measured failures and two post-execution repairs. Subsequent E0 and primary-period changes are preserved but unverified at the research transition. The unacquired parent-volume universe remains a dependency of exact E0 selection; it does not prohibit a properly admitted study of the supplied contract sequence.


## 2026-09-07 actual Jumbo admission result under research-v2

The distinct `Research-Jumbo-acquired-contract-OHLC-v1` study now has three
registered, accepted attempts: focused check (97 tests; 2.525918 CPU seconds),
pilot (33.249486 CPU seconds), and full admission (116.996028 CPU seconds).
Total consumption is 152.771432 of 2,400 CPU seconds; three of ten attempts
used. These do not run, reset or retroactively accept any old E0 attempt.

- Check: `reports/jumbo-runs/fd4e878de9bfbe03abce830783ad469db92faf79e5ca8a81559c9fbb2effd7f8/execution.json`.
- Pilot: `reports/jumbo-runs/aca57a5813fb5c66cb9e9a7ce67b1601da8fe4c406c2f495245c2cf9cc50abe4/execution.json`.
- Full admission: `reports/jumbo-runs/168628c5d54259758b23057fba9d1c69098f6bc8ab83711c2acf625718b15fc9/execution.json`.

All 14 declared NQ/ES OHLC yearly partitions cover 4,651,730 primary-period
rows, ending at the actual 2026-09-02 15:20 UTC endpoint. 4,613,232 rows pass
the declared observation/contract checks; 38,498 retain invalid reasons.
NQ 2024 contributes 33,241 activation-definition conflicts. No unknown minute
or contradictory lifetime was converted to observed flat activity. The actual
NQ March 11, 2024 trade hour matches all 60 OHLCV minutes exactly. Complete
source and canonical-table identities are in the execution's worker artifact.
Peak full-admission RSS was 804,847,616 bytes. Three pilot partitions were
reused after exact source/definition-hash and causal-domain checks.

The immutable admitted code snapshot is
`a88d1edace03df482d50aefbd5a7c5639183ac2cd8237f52475b97b5e270f50d`.
Subsequent statistics/model implementation will receive a new registered
check before execution. No market model fit or range/path statistics has
yet been delivered. The active family-level status is
`/workspace/planning/trading-research/STATUS.md`.


2026-09-07 Jumbo development checkpoint: registered check4 passed140 selected checks in3.614074CPU seconds. Registered extraction5 was interrupted after264.257352 observedCPU seconds (2,062,733,312-byte peakRSS) when measured yearly runtime projected the full10 root-years above the unchanged480CPU-second mode cap. Complete NQ2020–2022 annual tables/statistics are preserved at [partial-report.md](reports/jumbo-runs/f716b22e901d4f6cc9e21a21e1ab1a9493bab62deb73b66f5b1c97721bdbf847/partial-report.md), with immutable manifests and [interruption review](reports/jumbo-runs/f716b22e901d4f6cc9e21a21e1ab1a9493bab62deb73b66f5b1c97721bdbf847/interruption-review.json). The registry remains interrupted, with no retroactive acceptance. Total5 attempts/420.642858CPU consumed;5 attempts/1979.357142CPU remain. Exact checked reference source has been preserved. Static optimization and checkpoint continuation now await a registered actual-data parity/performance check; no additional tests, data runs or fits have yet executed. Active all-family delivery table remains [/workspace/planning/trading-research/STATUS.md](/workspace/planning/trading-research/STATUS.md).

2026-09-07 later Jumbo checkpoint: [registered check6](reports/jumbo-runs/4c5e09291a2ace060ed08f8dd9417ed91b19140060060f8dad18b5ace01ed66e/execution.json) passed 142 selected checks plus actual reference/current/saved/resumed table and statistics comparisons on 60 NQ cash dates. Zero error was observed across 2,508,090 floating and 5,674,466 exact comparisons. It used 53.391626 CPU seconds and 872,112,128-byte peak RSS. The run's per-date projection exceeded the extraction cap, so no extraction followed. The forecast will be corrected by measuring an entire annual report's fixed and variable work. Six attempts have consumed 474.034484 CPU seconds; four attempts and 1,925.965516 CPU seconds remain in the unchanged family allowance. New target/model/Location implementation is unexecuted and must pass the next registered check. The earlier interruption and all accepted evidence remain unchanged.


## Research audit continuation: completed annual stage in failed check9

The active family table is [research status](../planning/trading-research/STATUS.md). Check9 passed 399 focused tests and complete 253-date NQ2020 table/statistics equality, then failed on unavailable source-special formation metadata. Whole-annual extraction/statistics/serialization cost 51.375205854 CPU seconds; the full attempt used 81.368804 CPU seconds. At that point, nine attempts had consumed 565.945249 of 2,400 CPU seconds, with one attempt remaining. The original three annual shards, prior failures and exclusions remain unchanged. The [failure review](reports/jumbo-consolidated-check9-failure-review.json) and [explicit V5 verification/resource allocation](validation/JUMBO_EXECUTION_V5.json) retain those boundaries.

## Research continuation: check10 results and proposed allowance

The [tenth attempt](reports/jumbo-consolidated-check10-failure-review.json) passed 407 focused checks and reused the complete annual parity/resource evidence under its exact dependency contract. It saved the [question-based NQ2020–2022 report](reports/jumbo-runs/d90648bacac87a863f1d524cf667387ae4fa97734b3c3593237a71029664a0ee/research-report.md), covering all 81 formations and 433 clock/horizon combinations. Its [actual NQ2024 source supplement](reports/jumbo-nq2024-source-resolution-v2.md) recovered all 33,241 ambiguous-definition minutes without changing observed values or other exclusions. Corrected valid minutes total 4,646,473 of 4,651,730; the original admission remains immutable and 5,257 minutes remain excluded. Full-window sensitivity has not yet run.

Six optimizer resource units completed. The tree-provider unit then failed on unsupported wrapper metadata passed to its estimator constructor; the overall attempt remains failed. The correction and provider integration test are written but unexecuted. Ten attempts have consumed 624.511356 CPU seconds; the attempt allowance is exhausted despite 1,775.488644 CPU seconds remaining. The [same-family continuation allowance](reports/jumbo-continuation-amendment-proposal-v1.md) is proposed and awaits user authorization. No Context predictive-quality or Location-quality result is claimed. Independent auction/flow preparation continues under the active research plan.


## Research continuation: approved allowance and successful check 12

The user approved the [same-family continuation](reports/jumbo-continuation-amendment-applied-v1.md) on 2026-09-07. The earlier proposed/exhausted-budget paragraphs above describe their historical checkpoints. The current limit is sixteen attempts and 12,000 cumulative CPU seconds, retaining every prior cost and failure. [Check 12 succeeded](reports/jumbo-consolidated-check12-resource-review.md) with 432 tests in 73.970215 CPU seconds. Exact annual equality, source-correction provenance and lossless grouped-evaluation parity passed. Twelve completed attempts have consumed 788.671450 CPU seconds. Attempt 13 is extracting the remaining full development cohort within its measured 900-second / 512-MiB limits. Current model projections exceed their phase caps and require correction of measured reporting/storage workload assumptions before fitting or confirmation. No Context predictive-quality or Location-quality result is complete. The [active family table](../planning/trading-research/STATUS.md) carries current delivery status.


2026-09-08 complete Jumbo development extraction: [attempt 13 succeeded](reports/jumbo-complete-development-extraction13-review.md) with all ten NQ/ES 2020–2024 original annual shards and a separate corrected NQ2024 sensitivity. It retained 202,266 formations, 1,081,778 path rows and 53,822 source-specific observations, using 522.268499 CPU seconds and 360,861,744 derived bytes. Cumulative consumption is 1,310.939949 CPU seconds across thirteen attempts. Consolidated check 14 is running; fitting and heldout confirmation retain the last two approved attempts. No Context or Location-quality result is claimed before those evaluations.


2026-09-08 Jumbo check 14 correction: [the recorded attempt](reports/jumbo-check14-dispatch-deviation-review.md) passed 435 tests and legacy parity, but an implementation routing error skipped the intended new model-resource measurement. Its successful receipt remains within its actual scope. Fourteen attempts have consumed 1,366.469830 CPU seconds; two approved attempts remain. The dispatch repair and regressions are written. [One additional attempt](validation/JUMBO_CHECK_DISPATCH_AMENDMENT_V1_PROPOSED.json), retaining the 12,000 CPU-second total and all phase/memory/output caps, is awaiting user approval. No model-resource feasibility or predictive-quality result is inferred from check 14. Independent auction/flow implementation continues.
