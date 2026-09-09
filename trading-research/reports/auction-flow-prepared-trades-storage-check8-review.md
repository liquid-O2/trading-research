# Auction/flow check 8: exact trade preparation and cross-column storage

The combined registered check **passed**. All 278 tests, all nine complete retained source/event/native/measurement comparisons and all three complete split-window comparisons passed. This verifies the named calculation/storage changes on their declared domain; it does not complete full-cohort family statistics or predictive evaluation.

[Execution receipt](/workspace/trading-research/reports/auction-flow-runs/ddf0d2c136a6cd4048045f53448fd96fff40f4d67096e221f0a3de1d13367455/execution.json), [worker and projection](/workspace/trading-research/reports/auction-flow-runs/ddf0d2c136a6cd4048045f53448fd96fff40f4d67096e221f0a3de1d13367455/worker.json), [complete retained-value comparison](/workspace/trading-research/reports/auction-flow-runs/ddf0d2c136a6cd4048045f53448fd96fff40f4d67096e221f0a3de1d13367455/outputs/retained-source-value-reuse-comparison.json). The comparison preserves all eleven original source fields, event order and multiplicity, native extrema and clocks, logical Arrow values and exact measurement/continuation records. Frozen check-7 windows and their separately frozen arithmetic support the prepared-trade tests; the wider market comparisons retain the successful check-4 original values.

The prepared trade batch converts an owned bounded integer projection once for whole and atomic windows and shares validated arrays across the four flow channels. Public larger tables are internally sliced without narrowing the previous domain. Unsigned source addresses remain exact. Original cumulative kernels, sparse profiles, no-price adjacency breaks, source filtering, failure poisoning and native calculations remain unchanged. New storage uses checked original-value integer references and the existing v1 inverse, preserving real nulls, -1 sentinels, overflow fallback, original schemas and prior descriptors.

## Measured effects relative to check 7

These are paired sums across the same nine resource units, not a general speed guarantee.

| Measured region | Check 7 | Check 8 | Change |
|---|---:|---:|---:|
| Atomic trade consumers | 12.633455 CPU s | 3.666546 CPU s | 70.98% less |
| Whole-trade preparation and native consumers | 2.053014 CPU s | 2.138497 CPU s | 4.16% more, including preparation |
| Complete source pipelines including event storage | 112.028516 CPU s | 105.586550 CPU s | 5.75% less |
| Native cell files | 55,916,405 bytes | 47,362,458 bytes | 15.30% less |
| Quote event files | 136,640,202 bytes | 137,520,166 bytes | 0.64% more |

The native cross-column encoding reduced total native bytes. Ask-minus-bid encoding increased quote bytes across these units; it is not a supported compression improvement and will be removed from the next candidate while the v1 decoder remains compatible with this retained run. No original or intermediate output is deleted.

## Remaining cost and scope

The revised source-only projection is **191,375.080 CPU seconds** and **421,283,430,015 bytes** (421.28 GB), including its existing 1.5 margin and failure-output reserve. This covers ten nonempty root/year partitions. It still excludes complete downstream causal-structure/sequence/anchor populations, annual/date-block validation statistics, full packing and later model/report work. The remaining CPU balance is 189,190.254525 seconds, already below the source-only projection, and the existing study-output ceiling remains 256 GiB. Full extraction has not started.

This attempt used 660.998495 CPU seconds, 715.686 wall seconds, 1,248,403,456 bytes peak RSS and 411,606,389 retained output bytes. All **eight attempts and 2,809.745475 cumulative CPU seconds** remain counted, including failures. Retained attempts currently occupy 2,301,640,159 bytes under their accounting. The parallel-source draft is separate and unverified; it may reduce wall time but cannot make cumulative CPU or bytes disappear.

The active user phase order remains: complete validation across all intended families/frameworks, then Context, then Location. Previously prepared Jumbo Context code and its approval stay checkpointed for that later phase.
