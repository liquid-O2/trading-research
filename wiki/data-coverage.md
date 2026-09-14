# Evidence and data coverage

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md) · [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md) · [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md).

An observation is usable only if its evidence supports what the method asks. An executed trade, a displayed quote, a full-depth cancellation and a drawn chart annotation are different observations. The auction-state source uses submissions, cancellations and executions; the data-engine source requires consistent collection. [MATH] pp.4–8; [DATA] pp.3–4.

**Not a standalone trade.** Coverage supplies evidence for a decision; it does not supply the decision rule. A BBO reload hypothesis cannot certify hidden reserve or off-touch depth.

**Record before use.** Source file/page/post, figure identity, author, instrument and contract, tick size, clock, event coverage, missing fields, and the available depth/side schema.

**Phase 1 observation.** Keep pass / fail / unknown separate. Unknown aggressor, missing depth, missing intrabar order or an undefined source setting cannot become a negative or a passing setup. This page makes no new claim that a dataset has been acquired.

**Source-object implementation snapshot (2026-09-12).** [O001 contract](/workspace/planning/phase-1-live/FORMULAS.md#o001) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Resolve every physical row in the exact half-open window; certify minute coverage by interval membership and trade coverage against independently retained native minute OHLCV. Missing minutes and cross-source volume discrepancies remain explicit unknown coverage. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/native_boundary.py).

**Source-specific evidence limits.** Native retained files lack receive timestamps and exchange sequence. June 12 adjacent-minute reconciliation mismatches cannot be repaired by cancelling their net volume; native-clock-coverage.json preserves evidence. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source clocks and availability](clock-grid-and-bars.md) · [Executed aggressor-side trades](aggressor-trades.md) · [Provide, withdraw and consume events](order-participation-events.md) · [Frozen observation cohort](research-cohort.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>

## What "unknown" means in the accepted census, audited 2026-09-14

All 17,037 distinct unknown minutes were checked against the raw parquet ([audit](/workspace/planning/research-program/reviews/unknown-audit-2026-09-14/UNKNOWN_AUDIT.md)). 16,938 have no rows of any kind: exchange closures, holiday evenings and the archive end on 2026-09-03. 96 sit on the hairline gap between two monthly files that neither file owns, and 3 are quote-only minutes that the rules refuse to read as trades. Candidate-level `data_unavailable` (421 of 101,710 candidates) arises mostly from same-nanosecond prints at two prices with no sequence column, which the rules refuse to order. About 22,600 branch-session labels concern inputs the project never owned. "Zero unknown minutes" means the archive file demonstrably covers the interval, not that a trade printed in every minute. The new Phase 1.5 engine treats adjacent monthly files as contiguous when the seam gap holds no rows, as a labelled rule recorded in its coverage receipts.
