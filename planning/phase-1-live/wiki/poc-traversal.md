# POC failure versus efficient passage

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

Repeated failure to cross and hold POC favors rotational chop. Efficient passage, with the held retest where the source shows it, supports travel toward the other accepted area or far edge. [AMTL] pp.8–11; [RTVP] pp.5–8; [MAMT] p.12.

**Not a standalone trade.** A POC touch or a candle merely beyond it does not by itself establish control or far-side continuation.

**Record before use.** Profile/POC_id, prior reacceptance context, local attempts, passage side/effort, source hold/retest, known_at and next objective.

**Phase 1 observation.** Keep unsuccessful tests distinct from aggressive passage. Measure initial POC behavior before any later far-edge result; the future result cannot decide which interpretation was live.

**Current implementation (2026-09-12).** [O095 contract](../FORMULAS.md#o095) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Count distinct failed POC tests through as-of, preserve efficient-passage interpretation, and admit a held retest only when available. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Unknown test identity or a future retest remains a hole; failure and efficient passage stay distinct reads. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Profile point of control](profile-poc.md) · [Re-acceptance into value](value-reacceptance.md) · [Rotation within accepted balance](balance-rotation.md) · [Executed aggressor-side trades](aggressor-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
