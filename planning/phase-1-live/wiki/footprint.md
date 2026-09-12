# Native candle footprint

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Keani — open above value](method-keani-open-above-value.md).

A footprint locates executed buy/sell participation at prices inside the actual source candle. Sires uses it for local effort/result and imbalance reads; Saint's confirmed short has repeated selling inside candle bodies with DOM agreement. Jumbo's raw display can highlight only the top 35% of transactions. [FP8] pp.3–7; [TRAP] pp.8–10; [JR] pp.48–50; [AVG] pp.21–22.

**Not a standalone trade.** A footprint is evidence, not one shared entry rule. Saint's body selling does not make Sires's diagonal-stack threshold mandatory for him.

**Record before use.** Instrument, native candle/bar definition, price rows, executed side/size, body/wick membership, display filters, as_of and known_at.

**Phase 1 observation.** Keep filters and units with the display. The required pattern must occur at the chosen retest/location before entry; a final-AM delta total cannot replace repeated local body aggression.

**Current implementation (2026-09-12).** [O120 contract](../FORMULAS.md#o120) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Build a complete tick-row footprint from same-candle executions, preserving unknown volume, POC ties, body/wick delta, as-of, and display settings. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source execution bars](execution-bars.md) · [Executed aggressor-side trades](aggressor-trades.md) · [Diagonal footprint imbalance stacks](footprint-imbalance-zones.md) · [POC relocation within a candle](candle-poc-flip.md) · [Trapped aggression at an auction extreme](trapped-buyers.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[FP8]: </workspace/sources/documents/discretionary/fp-lesson-8.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
