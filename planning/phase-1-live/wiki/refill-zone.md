# Zone formed by aggressive prints

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

The Refill study first constructs an area from clustered large aggressive orders, then observes departure and a later return. Sires uses such areas as remembered control/refill locations within a thesis. This zone construction is distinct from proving passive order-book replenishment at a later test. [REF] pp.5–9; [OFM] pp.3–13; [CONT] pp.4–10.

**Not a standalone trade.** A burst or the zone's existence is not an automatic entry. Its later hold cannot be included in the features used to grade that same touch.

**Record before use.** Zone_id, instrument and side, source per-print/burst threshold, formation events and band, known_at, departure and each distinct later touch.

**Phase 1 observation.** Require formation < departure < current return, with frozen bounds. Keep touches separate and link fresh local defense before any claimed confirmed entry.

**Existing attachments.** [mbp1_objects.on_touch_refill](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_flow.r_f17_refill_zone](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F17/P3-08. Source clustering, NQ/MNQ normalization and full order lifecycle are missing; ≥100/2-minute/2-tick is a variant. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Memory of earlier zone tests](zone-touch-memory.md) · [Executed passive replenishment](passive-replenishment.md) · [Origin-of-the-Move catalyst](ofm-catalyst.md) · [Fresh defense of a continuation band](defended-band-continuation.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
