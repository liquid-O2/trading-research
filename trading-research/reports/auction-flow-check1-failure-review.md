# Auction/flow first check: source adaptation and storage repairs

The [first registered check](auction-flow-runs/67c89e640a7ca799cd5fd1302e712959a07c365d7f07a48a280c96075ca36dba/execution.json) ran 233 tests: 217 passed and 16 errored. It used 37.490009 CPU seconds, peaked at 205,410,304 bytes RSS and retained 257,418 output bytes. No market resource window ran. The attempt remains failed and counted.

Fifteen errors came from Arrow Boolean arrays: record-batch arrays require an explicit copy for NumPy conversion. The native ownership and time-at-price adapters now request that conversion. One error came from comparing Arrow IPC storage bytes across a Parquet round trip of a sliced table with nulls. Buffer offsets and unused bytes can differ even when the logical values agree.

The prepared storage check hashes column types/order, validity masks and every valid value. Integer clocks retain all bits; floating values preserve signed zero and NaN payloads. It retains complete row-group comparisons and file hashes. A focused test distinguishes shifted large integers, null versus empty string, signed zero and two NaN payloads, while requiring equal hashes for equal sliced/copied values. This is an explicit change to the verification representation; it does not relax source values, row counts, multiplicity or source lineage.

The same registered protocol, source variants, resource limits and family budget apply to the next consolidated check. These repairs are not yet verified. [Machine-readable review](auction-flow-check1-failure-review.json).
