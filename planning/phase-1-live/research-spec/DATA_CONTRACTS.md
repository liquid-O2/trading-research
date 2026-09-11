# Data contracts

## 1. Inventory and evidence

The frozen archive catalog is `data/manifests/dataset-catalog.json`; its 111 dataset entries describe approximately 322 GB. Catalog coverage is an outer bound, not proof that every session is complete. Read Parquet metadata and a bounded sample before writing an adapter. Keep the archive read-only and all derived data under ignored `data/derived/research-v1/`. Do not commit data.

The following paths are relative to `/workspace/data`. `*` identifies partitions to enumerate from the manifest; it is not permission to load an entire tick archive into memory.

| Input ID | Stored source | Build and availability contract |
|---|---|---|
| D01 bars | `quantpad/cme__nq-continuous-futures__ohlcv-1m/*.parquet`, corresponding ES/YM/RTY datasets | `t` is UTC epoch **milliseconds**, interval start. Fields `o,h,l,c,v,instrument_id`. A one-minute close/high/low/volume is available at start + 60 seconds. Rebuild from D02 where possible and compare. Historical NQ bars extend to 2010; inspected inventory ends during 2026-09-02. |
| D02 executions | `quantpad/cme__nq-continuous-futures__trades/*.parquet`; NQ MBP-1 trade actions for earlier coverage; matching ES/YM/RTY trades | `t` is UTC epoch **nanoseconds**. Fields `price,size,side,instrument_id,flags`. NQ standalone trades begin in September 2021; MBP-1 begins in 2020. Pick one canonical trade stream per date, never concatenate equivalent feeds and double count. |
| D03 BBO | `quantpad/cme__nq-continuous-futures__mbp-1/*.parquet` | Sampled fields are `t,action,side,price,size,bid_px,ask_px,bid_sz,ask_sz,instrument_id,flags`. The stored sample lacks receive timestamps, exchange sequence and order IDs. Do not invent them. NQ extends through part of 2026-09-03. ES BBO stops in August 2024, although ES trades continue into September 2026. |
| D04 contracts | `derived/continuous-futures__instrument-and-roll-maps/*-{rolls,instruments}.parquet`; corresponding QuantPad `__definition` datasets | Bind each event to raw `instrument_id`, tick size, multiplier and roll segment. Inspect the actual file set; the catalog describes NQ/ES/YM and may not cover every RTY segment. Build missing mappings from definitions and bar IDs. |
| D05 options | `thetadata-opra/opra__{ndx,ndxp,spx,spxw,qqq,spy}-options__{contracts,eod,open-interest}/*` | Full **daily** chain coverage; contract key includes root, expiration, strike, right and OSI symbol. OI has `ts_event` in sampled files; retain it instead of reducing OI to request date. |
| D06 option quotes | matching `__quote-1m__dte14__strike-range*`, `__quote-1m__dte60__atm10`, `__trade-quote__dte7__strike-range*` | Intraday quotes/trade-quotes cover scoped expirations and strikes, not the entire chain. Preserve acquisition scope in every result. Minute quote timestamps need the endpoint convention verified below. Zero bid/ask-size placeholders are unavailable quotes. |
| D07 native spot | QQQ and SPY QuantPad minute bars; `free-sources/yahoo__cash-daily__normalized/*` for NDX/SPX daily cash | ETF minute closes are available only at minute end. The stored NDX/SPX cash series is daily; it cannot supply same-day intraday spot. Use the explicitly specified parity-forward branch for European index options, or acquire historical native cash minutes. Never copy NQ to NDX or ES to SPX. |
| D08 volatility/rates | `free-sources/context__volatility__normalized/*`, `fred__usd-rates__normalized/*`, `cboe__vx-futures__normalized/*` | Store observation date separately from publication/availability timestamp and revision vintage. A FRED realtime date that reflects the archive download is not proof of historical intraday availability. Baseline daily VIX/rates use the previous completed session's published value; unsupported intraday vintages remain unavailable. |
| D09 events/calendar | `free-sources/context__event-calendar__normalized/*`, BLS, BEA/FOMC and exchange-calendar source files | Normalize actual scheduled release UTC time, event name, agency, announcement vintage and URL. A FRED update date is not automatically a 10:00 release. Unknown-time events cannot enter a time-specific release cohort. |
| D10 corporate actions | `free-sources/yahoo__corporate-actions__normalized/*` plus option contract specifications | Needed for ETF American-option pricing and adjusted contract identity. Ex-dates alone do not establish announcement timestamps. E10 uses conservatively lagged trailing ex-dividends; future-date exclusions require a documented announcement vintage. Do not merge adjusted and standard multipliers. |

Databento's native MBP-1 represents trades and top-of-book updates. Its native schema may have more fields than the stored QuantPad projection. Trade action side B/A means buy/sell aggressor, whereas non-trade side describes the affected book side; N is unknown. The adapters must use both `action` and `side`. [MBP-1 schema](https://databento.com/docs/schemas-and-data-formats/mbp-1?historical=python&live=raw), [field conventions](https://databento.com/docs/standards-and-conventions).

The input adapter must never infer hidden participant identity from MBP-1. It can measure displayed replenishment and adverse price response. MBO/order IDs could support a stronger order-level detector if acquired; even that does not establish a dealer's total hidden inventory.

## 2. Canonical event schema

Persist `events.parquet` partitions by raw instrument and exchange session. Required fields:

```
instrument_key: string           # provider-independent raw contract identity
source_dataset, source_file_hash: string
source_row_ordinal: uint64       # provenance only; not a fabricated exchange sequence
event_ts_ns: int64               # UTC
available_at_ns: int64           # UTC, >= event_ts_ns
ordering_group: string          # instrument + identical timestamp when sequence absent
event_type: enum(trade, quote, halt, reset, correction)
trade_price_ticks: int64?        # exact integer tick units
trade_size: uint64?
aggressor: enum(buy, sell, unknown)?
bid_ticks, ask_ticks: int64?
bid_size, ask_size: uint64?
source_flags: string
quality: enum(valid, ambiguous_order, invalid, gap)
```

1. Parse timestamp units from the dataset contract; never infer seconds versus milliseconds from a convenience conversion. Convert exchange clocks with `zoneinfo.ZoneInfo('America/New_York')`, retaining UTC internally. Assert round-trip winter and summer fixtures.
2. Convert prices to integer ticks using instrument metadata. Require absolute reconstruction error <= 1e-6 tick. Negative/nonfinite sizes or impossible OHLC values fail normalization. Do not silently round an off-grid trade onto a valid price.
3. Trades with side N contribute to total volume and unknown volume, never signed delta. Signed-volume coverage is `(buy_volume+sell_volume)/total_volume`; require >=0.95 for a flow signal. This quality threshold is fixed, not a performance-tuned parameter. Report coverage by date and time bucket.
4. Preserve source order and equal-timestamp groups. Without a reliable sequence, do not decide which of two different trade prices occurred first inside that group. Aggregate commutative statistics normally. Any within-group trigger/stop/target ordering is ambiguous; use the conservative execution rule in ENGINES. Do not remove two identical trades merely because their timestamp, size and price match: they can be separate executions. Deduplicate only byte-identical source overlap with proven record identity.
5. `available_at=event_ts` is an **event-time research assumption** for the stored projection, since receive time is absent. It does not measure real vendor latency. Add the explicit execution delay only after signal availability. If native receive timestamps are later acquired, a separate receive-time run uses them and never backdates them.
6. Canonical trade source priority is the standalone trade dataset when coverage-qualified, then MBP-1 action T for a whole missing partition/date. Do not switch streams inside a session without a recorded nonoverlap boundary and reconciliation. Compare overlapping streams by sorted timestamp/price/size/side groups and daily volumes. A discrepancy is a quality issue to investigate, not an invitation to sum them.
7. Reconcile derived minute volume with stored minute volume. Require exact tick OHLC agreement and relative volume difference <=0.001 on at least 99.9% of covered minutes; flag every exception. Do not erase legitimate exchange corrections to hit the threshold. If a documented feed convention explains exceptions, create a versioned adapter and retain both results. Otherwise the affected session is unavailable for the relevant cross-feed test.

## 3. Coverage and contract continuity

Build `coverage.parquet` with instrument, interval start/end, expected market-open intervals, event/bar counts, missing subintervals, invalid-book intervals, side coverage and contract transitions. A silent interval with a healthy feed is different from a missing interval. Raw absence without feed-health evidence is unknown, not zero volume.

For one-minute recipes require every expected minute in the formation and all minutes up to decision. Completed outcomes require every expected minute through the named horizon; an interrupted outcome is censored. For tick/order-flow recipes require a coverage-qualified execution stream and BBO only when that module needs BBO. ES BBO absence after August 2024 does not prevent price-based ES SMT from trades/bars.

Reference formation uses the actual tradable schedule, including documented holidays and early closes. A required full 06:00–09:00 window that overlaps an exceptional halt is unavailable; do not shorten it and retain the same ID. An outcome can end at the documented early close, with `horizon_kind=early_close`, and must be reported separately from a normal horizon. No Friday-to-Sunday nonexistent minutes are treated as missing trading.

Baseline cross-session price references require the **same raw contract**. At a roll, do not carry an unadjusted old-contract high/low, POC or gap into the new contract. Mark it `contract_transition`. A separately registered translation variant may use the median simultaneous old/new-contract mid-price difference in the last complete 30 minutes before the switch, requiring >=100 paired quotes within one second; store the spread and its availability. If those two-contract quotes are not available, do not fabricate the mapping. Width/return histories can span contracts only after recording that each sample is internally single-contract and normalized as specified.

## 4. Option and daily-data availability

Theta OI is normally disseminated in the morning for the prior day's positions. The actual historical timestamp wins over a hardcoded clock. Store `position_date`, `published_at`, `received_at_if_present` and `available_at=max(published_at,received_at)` separately. If only a date is available, baseline availability is the next verified publication timestamp; without one, exclude from intraday scenarios. A 06:30 assumption is permitted only as the explicitly labelled `oi_clock_assumed_0630` sensitivity run, never the baseline. [Theta OI documentation](https://http-docs.thetadata.us/operations/get-snapshot-option-open_interest.html).

For every quote adapter, inspect the endpoint documentation and ingestion metadata to establish whether `ts_event` names a sampling instant or an interval start. Baseline when the convention is unresolved: conservatively assign `available_at=ts_event+60s`, mark `quote_clock_assumed_end`, and do not claim subminute timeliness. When verified as an instantaneous NBBO snapshot, use its actual event timestamp. Use as-of joins only; no nearest-future quote. Require a positive uncrossed market, both displayed sizes >0, age <=120 seconds, and relative spread `(ask-bid)/max(mid,0.01) <=0.30`. Keep excluded-contract counts and OI weight, not just surviving counts.

Daily spot, rates and volatility values have `observation_date` and `available_at`. Baseline prior-close context becomes usable at the following scheduled session open only when the source's historical value is established. Do not use today's eventual daily high/low/close to infer an intraday flip. Date-only future revisions are not permissible features.

Native option contract metadata must identify exercise style, multiplier, settlement clock, underlying and expiration UTC instant. American and European contracts require different pricing treatment. Do not assign Black-76 to an entire CME parent chain by root. [CME exercise procedures](https://www.cmegroup.com/clearing/contrary-option-exercise-instructions.html).

## 5. Derived input products and acquisition alternatives

Build these derived products once and share them: clock-aligned bars; frozen reference ledger; snapshot VP/TPO; volume-weighted price moments; footprints and CVD; flow baselines; level-interaction episodes; confirmed swings/FVGs; scheduled event calendar; native option snapshots/scenarios. Every row carries `available_at`, `input_manifest_hash` and `recipe_version`.

Additional inputs are alternatives with exact contracts, not indefinite clarification requests:

- Native SPX/NDX intraday cash: acquire `symbol,event_ts_utc,available_at,bid/ask or last,source,condition`; validate against the corresponding daily cash close. Until then, the European-index parity-forward model specified in ENGINES is the native-coordinate scenario branch. It must be named as a forward model, not cash spot.
- Order-level replenishment: acquire MBO with order ID, add/modify/cancel/trade, sequence and feed resets for the same raw NQ contracts. Until then, implement D03 displayed-reload inference with its stated uncertainty.
- Missing event schedules: parse official archived BLS, BEA, Census, ISM, University of Michigan, Conference Board and FOMC schedules into D09. A current revised calendar without historical announcement vintage supports event-study grouping, but not a claim that a changed appointment was known before the change. [BLS calendar](https://www.bls.gov/schedule/news_release/), [BEA calendar](https://www.bea.gov/news/schedule).
- Expanded option strikes/expiries: acquire the missing scope only if the preregistered coverage criterion fails. Until then, call the output a scoped-chain scenario and compare only on its qualified universe.

No acquisition is required to implement and test the price/profile/flow baseline suite. A missing stronger input never justifies renaming its weaker observable substitute as the original hidden quantity.
