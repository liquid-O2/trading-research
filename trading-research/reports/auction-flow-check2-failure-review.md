# Auction/flow second check: one source-interface repair

The [second registered check](auction-flow-runs/383c81a1dac20c8ae11e7601f27be8295b82ce64f2a23fabbc20d8ceaa0086ab/execution.json) passed 233 of 234 tests and stopped before market measurements. It used 38.651528 CPU seconds and 194,514,944-byte peak RSS. Both failed attempts remain counted: 76.141537 CPU seconds in total.

The Boolean conversion, native trade/quote paths, time-at-price, profile geometry and complete storage round trips passed. The remaining error exposed an interface mismatch: raw and excluded projections were Arrow RecordBatches, while complete-source concatenation and retention consume Tables. The source producer now standardizes those projections as Tables, as it already did for trades/quotes. It hashes the original raw batch before conversion and preserves every value, address and ordering field. An explicit all-projection interface assertion accompanies this repair.

No market population, source variant, scientific parameter or registered budget changes. The next consolidated check must verify the common interface and then execute all declared real-data resource units. [Detailed retained review](auction-flow-check2-failure-review.json).
