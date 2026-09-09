# Trading research status — stopped September 9, 2026, 07:14 UTC

**Stopped at the user’s request: “just stop everything please.”** All research processes and Cursor workers have exited. Completed evidence, partial quote outputs, and unfinished drafts are preserved. Deliverable 1 remains incomplete. No automatic continuation; resume only on a new user instruction. Quote run 18 was interrupted by this request, with 10,439.458832 CPU-seconds charged. The earlier status below is retained as historical context.

# Trading research status — September 9, 2026, 06:38 UTC

Current Deliverable 1: the full observed minute-price cross-market branch is accepted across 2020–2026, with 1,677 primary dates, 4,502,953 source events, 110,377,785 directed links and 368,258 statistical groups. All 47 checks pass; 97 identical SPY source aliases retain their original row addresses. [Full cross-market results](/workspace/trading-research/reports/cross-market-runs/e19257df9a42e38318d38aa6fe58e52f0ab93a7ec00da5330c27fa56dc94faec/outputs/results.md). Broader flow, event and regime mechanisms remain open.

Profile pilot 68 passed all 57 checks but failed while decoding a measurement JSON at the 4 GiB address-space limit after 2,025 CPU seconds. A bounded input/state diagnosis is next; no profile population is accepted. Quote pilot 16 passed 53 checks and complete parity across ten tables and 3,773 groups; source measurement now takes 107.37 CPU seconds. The unchanged 1.5-margin full estimate is 99,557 CPU seconds. The initial quote compute estimate has been amended to 120,000 cumulative CPU seconds, retaining all usage, with 105,000 allocated to the full run. Full 17 passed the gate and checks but failed before source IO on inherited child limits; full 18 applies the launch correction.

The full OI report/lifecycle population is accepted: 1,677 dates across seven chains, 21,789 input files, 93,352,457 reports and 93,417,173 retrospective as-of intervals. All 45 checks pass; 280 groups report date support, distributions and uncertainty. The full run used 2,697 CPU seconds and 1.12 GB peak memory. [Full OI results](/workspace/trading-research/reports/options-oi-runs/123bf7bd0f4e0f7a7d8b917edb1e91b3bb8b6ff692c2917db394b0497c38fff6/outputs/results.md). Actual publication/receipt clocks and the VIX listing denominator remain unknown.

European/American valuation numerics passed all 44 independent checks in 5.7 CPU seconds. Historical option valuation and adaptive-cohort measurement remain pending. Grok is implementing the historical valuation consumer and one consolidated correction to the cohort consumer; neither draft is verified.

Full window statistics 49, core statistics 42, and the accepted physical volatility, daily volatility, and scheduled-event populations remain retained. Deliverable 1 is incomplete; Context has not started. Exact evidence, remaining mechanisms, failures, and budgets are in [CURRENT.json](state/CURRENT.json). Historical figures below do not override current state.

## Completed evidence and pending work

| Family | Completed/admitted evidence | Remaining validation | Context / Location |
|---|---|---|---|
| Jumbo, ranges, session paths | Complete NQ/ES 2020–2024 original development extraction plus separate NQ2024 source correction; 202,266 formations, 1,081,778 path rows, 53,822 source-specific observations. Fourteen admitted annual partitions total 4,651,730 rows through 2026-09-02; the corrected-source sensitivity has 4,646,473 valid minutes and 5,257 excluded. | Later descriptive confirmation19 is accepted: 418cashdates/root in2025-26,67,214formations359,478paths17,890source-specific rows, noContextfits. Controlled same-target andJTR-relative transition comparisons are nowinimplementation; exactsource dependencies remain. | 116 intended targets inventoried and actual bounded optimizer costs checked; full fitting and independent confirmation unrun. Location candidates/labels/model code exist; complete evaluated quality unrun. |
| Auction, profiles, footprint, references | Latest benchmark23:121affected tests, nine complete source/measurement comparisons, three continuation cuts. Check17:338tests and full anchor/cohort checks; downstream20 reproduced18complete payloads in130.973elapsed seconds. Complete source extraction and fullobservation39 accepted:167files,3,589windows,5,115,250atomicrows;35​52measured/37unavailable windows. Fullconversion7.3minutes; corestatistics42accepted; causalformation/labelpopulation46complete; fullwindowstatistics49running. | Source cohort complete. Complete anchor/rolling/causal structure populations, distributions/timing/stability/uncertainty and exact source comparisons remain required. | Full auction/migration predictive comparison and controlled Location study unrun. |
| Flow, participation, structure, aggression memory | Whole/minute hard/soft cohort arithmetic on nine full units; raw fields, event multiplicity, native 100ms paths and source carry preserved. Prepared quote/trade batches and fused source projection verified for their exact scopes. | Full annual calibration/cohort distributions, divergence/streaming structural populations, memory/protection/revisit rules and discretionary patterns. Book/structure/memory draft kernels and stopped actual-source probes are unverified. | Participation, structure and memory Context results and complete evaluated Location results unrun. |
| Physical / implied volatility and remaining movement | Shared data/label/evaluation infrastructure; unequal field/inventory and bounded VIX evidence. | Full distinct OHLC estimators, sampling/noise/RV/semivariance/jump/seasonal/long-memory dynamics; implied shape/term/event/VRP/intraday/0DTE/cross-IV, VIX/VX complex; actual support, timing, sensitivity and uncertainty. Preserve every source sibling in the specification. | No completed family predictive comparison or conditional statistical-zone study. |
| Options / OI / exposures / flow / nodes | OI report/label utilities, contract/payoff support, native/Parquet prefix/catalogue evidence. | Full point-in-time chain/underlier/expiry/publication domain; IV/Greek conventions and inversion; reported OI vs uncertain holdings; exposure driver decomposition; signed/unknown/grouped flow; complete node/corridor/max-pain studies and source-specific support. | No complete OI/exposure/node predictive comparison or evaluated node/corridor catalogue. |
| Cross-market / events / regimes | Shared as-of and coordinate tools, source definitions and unequal coverage/publication evidence. | Actual supported source/receiver studies, chain comparisons, relative price/flow/SMT, mapping vs transmission, broad-market and slow/event context; exact missing-vintage/feed dispositions without suppressing independent supported work. | No completed mapping/transmission/regime comparison or source-originated opportunity evaluation. |
| Locations and lifecycle | Range/internal/extension/prior-session generators and measurement-derived helpers; candidate/label infrastructure. | Exact basic geometry can support validation; full catalogue still required after upstream phases. | Complete eligible candidates, reach/first-order paths, retests/invalidation, context conditions, geometry/placebo/count/width/distance/age controls and independent generator/scorer contributions unrun. |
| Shared foundations | Readers, clocks, units, provenance, coordinates, measurement kernels, folds/labels and fitting/scoring have substantial scoped tests. The historical combined measurement suite passed 851 tests. All 111 datasets inventoried. | Actual source eligibility and end-to-end efficiency remain cohort-specific. Inventory or a passing reference fixture does not close the outstanding scientific family. | Reuse shared tools; do not reopen full B00–B10, E0 or live-trading machinery as research prerequisites. |

Every detailed child, source comparison, mathematical requirement and failure case remains in [RESEARCH_SPEC.md](RESEARCH_SPEC.md), [UNIT_CATALOG.md](UNIT_CATALOG.md) and their preserved source references. This table does not replace them or reduce the catalogue.

## Exact evidence to reuse

- [Latest accepted source/replay/fusion and downstream performance](/workspace/trading-research/reports/auction-flow-performance23-review.md).

- [Jumbo complete development extraction](/workspace/trading-research/reports/jumbo-complete-development-extraction13-review.md).
- [Jumbo corrected-source sensitivity](/workspace/trading-research/reports/jumbo-nq2024-source-resolution-v2.md).
- [Jumbo complete resource check 16](/workspace/trading-research/reports/jumbo-check16-complete-resource-review.md).
- [Approved same-family Jumbo continuation](/workspace/trading-research/validation/JUMBO_COMPLETE_WORKLOAD_AMENDMENT_V2_AUTHORIZED.json).
- [Auction/flow broader anchor/cohort/source check 9](/workspace/trading-research/reports/auction-flow-parallel-cohorts-check9-review.md).
- [Historical focused benchmark 16 execution](/workspace/trading-research/reports/auction-flow-runs/5af1c04dc985e41054fcfe2d4f14f1d0131f1c74d5b5d8ccc0a32ce11c9f0316/execution.json) and [complete worker report](/workspace/trading-research/reports/auction-flow-runs/5af1c04dc985e41054fcfe2d4f14f1d0131f1c74d5b5d8ccc0a32ce11c9f0316/worker.json).
- [Provider-flag versus missing-download clarification](/workspace/trading-research/reports/auction-flow-data-quality-clarification.md).
- [All auction attempts, including failures](state/AUCTION_ATTEMPTS.json).
- [Detailed pre-consolidation engineering history](history/2026-09-08-consolidation/implementation/STATUS.md).

## Resources and efficiency

Auction/flow: **36/36 attempts, 71,701.255619/192,000 CPU-seconds, 55,928,815,964 retained output bytes** against 256 GiB. Jumbo remains16/24attempts and1,473.051801/20,000CPU-seconds. Read live ledgers before execution; all failure/deviation records remain retained.

[Accepted performance23review](/workspace/trading-research/reports/auction-flow-performance23-review.md): source-only allowance152,641.745CPU seconds /261.16GB, versus160,866.336CPU seconds /419.01GB in18. The separate dual-count quote estimate134,722.304CPU seconds is a frozen empirical cost recalibration awaiting17-window holdout validation, not an additional algorithmic speedup. The121-test full correctness benchmark took398.110elapsed seconds; downstream20took130.973seconds with all18payloads unchanged. Full annual source extraction is complete; all-family scientific validation, Context and Location execution remain unfinished, so under-three-hour end-to-end feasibility remains unestablished.

C++ source/quote/native kernels, NumPy reductions, exact structural storage, independently verified quote replay, profile-extrema hoisting and cohort interval indexing are accepted for their measured scopes. V14 now supports the registered17-worker source throughput holdout under existing family limits. Do not rerun unchanged broad checks or treat the holdout as full empirical family completion.

## Deferred research continuation

1. Keep the current accepted source implementation and read the exact dependency/draft references in [state/DEPENDENCIES.json](state/DEPENDENCIES.json). Do not rerun its benchmark simply because context changed.
2. Resolve complete auction/flow extraction/consumer feasibility and finish actual required validation, including the still-unverified book/structure/memory mechanisms. Stopped probes need deliberate completion/review; do not resume their workers or adopt their output automatically.
3. Complete the other validation families with the full depth above and exact unsupported dispositions. Unimplemented work is pending, not unsupported.
4. Once all-family validation is complete, use the approved Jumbo continuation and shared evaluation path for independently assessed Context. The prediction-reuse draft has known review defects and is not accepted.
5. Complete the full Location catalogue and controlled quality/lifecycle evaluations. If the user creates a new task for that phase, transfer this same durable entry point and current state.

The latest user explicitly resumed full Deliverable1 measurement/statistics/timing at20:41UTC. The source timestamp repair remains verified and integrated; its exceeded earlier20:11 cutoff and all elapsed/resources remain recorded. Current active work is listed above and in CURRENT.json.

### Latest source production evidence

The current source result is **3,589 complete windows across 167 files, zero failures and zero pending windows**. Four sub-second clock-uncertainty intervals retain explicit conditional timing eligibility. [Verified source timestamp repair](/workspace/trading-research/reports/auction-flow-reset-clock-repair36-review.md). Earlier failed attempts are retained. Downstream cohort and anchor drafts remain stopped and unverified.
