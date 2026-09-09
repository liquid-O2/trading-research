# Auction/flow source check 4

The registered check passed all 245 tests, nine actual source-window units, complete retained-value comparisons with check 3, and three split-window comparisons. This verifies the stated extraction and storage mechanisms; full family statistics, independently scored Context and Location quality remain outstanding.

The attempt used 424.402538 CPU seconds, 495.446 wall seconds and 1,248,612,352 bytes peak RSS. All four attempts, including the two failures, remain counted: 768.174990 CPU seconds and 1,043,308,790 output bytes. No resource limit changed.

## What was established

All ordered trade, quote/invalidation and native values were compared with the retained successful check 3 outputs. Integer clocks, source addresses, values and multiplicity match exactly. The two native floating exposure integrals use the already declared absolute tolerance of 1e-6 and relative tolerance of 1e-12. Compressed measurement JSON restores the complete original canonical bytes. The original outputs remain unchanged.

The ordinary NQ cash window also matches a midpoint split, and both NQ/ES 23-hour windows match a split at UTC midnight. Each comparison reads every retained row and field. Source invalidation, actual quote age and ownership carry across the cuts. A partition boundary supplies neither book recovery nor a scientific formation anchor. These real-data comparisons each contain one observed instrument; the separate multiple-instrument fixtures have their own stated scope.

| Source window | Raw rows | Trades | Retained MB | Pipeline CPU s |
|---|---:|---:|---:|---:|
| NQ 2020-03-16 (2020-03-16) | 1,484,342 | 155,066 | 30.059 | 10.294 |
| NQ 2020-03-16 (2020-03) | 1,484,342 | 155,066 | 30.042 | 10.104 |
| NQ 2024-03-11 (2024-03) | 3,667,827 | 156,709 | 47.838 | 16.405 |
| ES 2020-03-16 (2020-03) | 3,450,647 | 411,548 | 51.426 | 15.992 |
| ES 2024-03-11 (2024-03) | 4,271,130 | 151,224 | 52.040 | 17.984 |
| NQ 2021-02-14 18:00–19:00 NY (2021-02-08) | 16,624 | 2,222 | 0.578 | 1.055 |
| NQ 2021-02-14 18:00–19:00 NY (2021-02) | 16,624 | 2,222 | 0.578 | 1.115 |
| NQ 2024-03-10 18:00–Mar 11 17:00 NY (2024-03) | 4,534,492 | 224,387 | 57.807 | 27.667 |
| ES 2024-03-10 18:00–Mar 11 17:00 NY (2024-03) | 5,574,880 | 224,556 | 64.092 | 28.378 |

Retained MB includes event/native projections and the primary compressed measurement record. Pipeline CPU excludes the separately charged literal reference and integrity-only comparisons. All actual attempt costs remain in the execution receipt. Neither overlapping acquisition pair becomes an independent economic date or a global source alias.

## Complete-source workload and limits

The inventory checked 167 original files and 59,345 row groups. Every instrument set was established from constant, non-null identity footers, requiring no supplementary identity-column scan. There are 129 one-instrument files and 38 two-instrument files. The schedule retains all 3,589 physical source/day windows and both overlapping acquisitions.

The disjoint source projection is 311,098.798 CPU seconds and 801.073 GB, including the declared 1.5 margin and fixed failure-output reserves. It exceeds the unchanged 192,000 CPU-second and 256 GiB study limits, before full scientific anchors, models and final reporting. Full extraction has not started. The array bound plus observed nonarray RSS is 1,630,040,928 bytes, within the 4 GiB memory limit.

| Root/year | Source/day windows | Source CPU allowance | Output GB allowance |
|---|---:|---:|---:|
| ES 2020 | 332 | 29,144.3 | 74.156 |
| ES 2023 | 180 | 16,178.8 | 41.789 |
| ES 2024 | 242 | 20,626.9 | 53.409 |
| NQ 2020 | 728 | 52,763.8 | 131.968 |
| NQ 2021 | 420 | 34,374.9 | 87.230 |
| NQ 2022 | 361 | 32,637.3 | 84.258 |
| NQ 2023 | 359 | 31,657.0 | 81.281 |
| NQ 2024 | 363 | 32,478.5 | 83.706 |
| NQ 2025 | 361 | 35,149.7 | 92.365 |
| NQ 2026 | 243 | 26,087.7 | 70.911 |

This replaces the quarantined check 3 whole-window/raw-row extrapolation. It separates physical reading/projection, instrument batches, atomic consumers, native cells and serialization. It is a conservative empirical allowance, not a complexity theorem: the current schedule budgets every file instrument for every day, and measured dense native-byte rates are applied across the cadence. These explicit workload bounds can be tightened only with applicable ownership evidence or a verified implementation change.

Dense native tables account for 320.730 GB before the margin; event projections account for 174.838 GB and compressed measurement JSON 34.901 GB. Exact integer relationships and sparse missing-value columns are the next storage candidates. Raw atomic reduction and exact serialization are measured processing costs that warrant consolidation. No market population, field, source variant or failure row may be dropped to fit the budget.

The measured units contain no excluded trade rows. Their future frequency and storage cost therefore remain unmeasured; the separate 512 MiB per root/year allowance is a failure-output reserve, not a zero-prevalence assumption. The overnight book-gap recovery dependency remains unresolved.

## Evidence

- [Execution receipt](auction-flow-runs/3676833c2a818d870cf2970b566dc896b7d7d2e109b21fbc22faf6547459f7f2/execution.json)
- [Complete worker results](auction-flow-runs/3676833c2a818d870cf2970b566dc896b7d7d2e109b21fbc22faf6547459f7f2/worker.json)
- [Machine-readable review](auction-flow-source-check4-review.json)
- [Study definition](../validation/AUCTION_FLOW_STUDY_V1.md)
- [Previous source check](auction-flow-source-check3-review.md)
