# Zone formed by aggressive prints

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

The Refill study first constructs an area from clustered large aggressive orders, then observes departure and a later return. Sires uses such areas as remembered control/refill locations within a thesis. This zone construction is distinct from proving passive order-book replenishment at a later test. [REF] pp.5–9; [OFM] pp.3–13; [CONT] pp.4–10.

**Not a standalone trade.** A burst or the zone's existence is not an automatic entry. Its later hold cannot be included in the features used to grade that same touch.

**Record before use.** Zone_id, instrument and side, source per-print/burst threshold, formation events and band, known_at, departure and each distinct later touch.

**Phase 1 observation.** Require formation < departure < current return, with frozen bounds. Keep touches separate and link fresh local defense before any claimed confirmed entry.

**Current implementation (2026-09-12).** [O116 contract](../FORMULAS.md#o116) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Freeze the source-defined zone, formation identities, departure, and distinct return touch without letting later highs redefine it. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Memory of earlier zone tests](zone-touch-memory.md) · [Executed passive replenishment](passive-replenishment.md) · [Origin-of-the-Move catalyst](ofm-catalyst.md) · [Fresh defense of a continuation band](defended-band-continuation.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
