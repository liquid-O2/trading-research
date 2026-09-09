# Current validation implementation: lossless cross-column storage

The user now requires validation of every intended framework first, then Context, then Location. This assignment advances validation extraction only. Do not change or work on Context code.

Work only in this isolated checkout. Edit exactly:
- src/trading_research/research/auction_flow_structural_encoding.py
- tests/test_auction_flow_storage.py

No shell, imports/tests, benchmarks, raw data reads, source scans, fits, protocols, budgets, references or other files. Return the complete patch and candid limitations. Codex will review and execute the existing registered check. Use as many file/tool calls as needed to finish this coherent patch; do not stop after a plan.

Measured bottleneck: check7 source-only storage projection is 447,435,723,012 bytes, including 216,355,848,779 native-cell bytes and 41,258,985,708 exact-report bytes (each already with its 1.5 margin). The busiest native unit uses 45.634 bytes per 100 ms cell. Projected CPU remains 211,218 seconds. This patch may improve the frontier but need not solve it alone; do not claim a speed or compression gain without a run.

Implement exact column-reference differences through the EXISTING v1 integer codec. Preserve VERSION, public API, logical/physical Arrow field types, column order, nullability, schema metadata, operation keys and every scalar/validity bit. Existing v1 descriptors must still decode. Existing ParquetSeries already validates complete logical hashes after every row group and handles all storage limits. Do not change its writer or compression level.

Useful deterministic correlated references:
- Quote events: ask relative to bid when both are int64; preserve arbitrary signed int64 values and fallback on subtraction overflow.
- Native price: first_price_ticks stays the base; last_price_ticks/high_price_ticks/low_price_ticks can be relative to it.
- Native clocks: restore event_end_ns and known_at_ns as today, then first_trade_at_ns relative to event_start_ns. Last trade/price-extreme clocks and trade-cohort high/low clocks can reference original first_trade_at_ns rather than repeating their absolute offset. Native quote-only OFI clocks must retain event_start_ns when a valid trade reference is absent.
- Native orders: restore first_trade_source_order (including its -1 sentinel), then last-trade/price-extreme and trade-cohort extrema orders can reference original first_trade_source_order.

Avoid making a missing reference expand a present value into a huge epoch/order residual. A column/group can fall back to the existing event-start or sentinel-only encoding when a nonmissing target lacks a usable trade reference. Preserve the ENTIRE input domain: the fallback is a storage choice, never exclusion or coercion. Nullable logical columns with actual nulls retain their original exact nulls; do not confuse an original null with the physical encoding of -1. No floating-point intermediate, Python row/scalar loops, price rounding, economic deduplication, removal of native cells or altered definitions.

Every subtraction uses ORIGINAL input reference values. Emit inverse operations in dependency order, even when the source schema order differs; a reference that is transformed must be restored before a dependent column. Retain bounded Arrow/vector operations and the existing checked-int64 fallback. Do not select a predictor based on future observations or output quality. This is exact physical compression only.

Tests should independently specify correlated timestamp/order/price values, missing and no-trade/quote-only cells, real nulls, negative/extreme int64, >2**53 clocks, overflow fallback and shuffled schema order. Verify complete decode equality and unchanged metadata/nullability. Exercise multi-row-group/files through read_series_tables and compare_series, including descriptor tampering and older descriptors. Keep existing tests and float payload checks. Compression acceptance will use all nine retained real-source units and continuation comparisons under the registered runner; do not add a synthetic timing threshold.
