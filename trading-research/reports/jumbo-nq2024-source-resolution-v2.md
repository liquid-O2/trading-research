# NQ2024 definition conflict: actual source resolution

The registered tenth check recovered **33,241 NQZ4 minutes**, exactly the original ambiguous-definition population. It changed no observed OHLCV values, raw identifiers, ordering or other exclusions. Across all 14 admitted partitions, valid minutes increase from **4,613,232 to 4,646,473 of 4,651,730** under this separately retained correction. The **5,257 unavailable-definition minutes remain excluded**. This is price-row admission; the effect on complete research windows still requires the corrected NQ2024 annual extraction.

The full source audit read all eight registered NQ definition files and the NQ2024 OHLC source. It found 65 NQZ4 definition records marked A and none M. Their common raw ID 106364, symbol NQZ4, expiry and 0.25 price tick identify one physical contract; historical activation metadata changes do not create another physical price coordinate.

[Databento documents](https://databento.com/docs/schemas-and-data-formats/instrument-definitions) active-definition snapshots at weekday UTC midnights and treats definitions as point-in-time data. [QuantPad's public API](https://api.quantpad.ai/external/openapi.json) documents a Databento-backed reference stream. The retained acquisition record binds GLBX.MDP3/NQ.c.0/definition to the downloaded 2024 file; the downloader writes Arrow batches directly into Parquet. The registered supplement checked each target action, receipt, source hash and physical metadata. Snapshot interpretation is an inference from that combined evidence, not an invented M action.

The supplement selects only the latest state already known at each bar, using max(t,ts_recv)+250ms under the declared latency scenario. It retains the earliest known physical contract key and the selected original definition version. A future state cannot rewrite an earlier bar. The numeric publisher ID was omitted by the export and remains unknown; the exact QuantPad source namespace and file hash provide the binding. The snapshot timestamp and 250ms delay do not establish measured historical receipt by a strategy.

The original admission, M-only unresolved audit and all excluded rows remain intact. The corrected canonical table is an explicit supplement. The source stage passed within an overall check that later failed on the tree-provider configuration, so this source result does not promote that check or establish predictive quality.

Evidence:

- [Source/acquisition binding](../validation/JUMBO_NQ2024_SNAPSHOT_SOURCE_V1.json).
- [Actual source and price validation](../evidence/trials/artifacts/ed/eda4ac35bec2cefd74802ce2dbed544a12fe21cd15d8d03aff65283b9815997d).
- [Check10 execution](jumbo-runs/d90648bacac87a863f1d524cf667387ae4fa97734b3c3593237a71029664a0ee/execution.json) and [failure/stage review](jumbo-consolidated-check10-failure-review.json).
- Raw definition source SHA-256: `2191a05b4ec619ac90bf9c676ecef0485d00f5dda6aaec437b9d1e31173f9bf7`.
