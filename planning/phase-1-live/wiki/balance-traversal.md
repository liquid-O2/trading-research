# Whole-balance traversal with one side in control

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Price traverses a whole established balance without holding; later retests can then be read with the controlling side until contradicted. This is one route in the broader auction loop. [MAMT] p.12.

**Not a standalone trade.** A fast move or the eventual side of the session is not enough. The source does not prescribe the compiler's universal maximum traversal duration.

**Record before use.** Frozen balance, entry/exit boundaries, direction, complete traversal path, any internal acceptance, later retest and control evidence.

**Phase 1 observation.** Record traversal, absence of source-defined hold and later same-structure retest as ordered events. A whole-AM range or final close cannot reconstruct them.

**Existing attachments.** [formulas_jumbo.a09_traverse_nohold](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [FORMULAS] R-A09. The helper's fixed time limits are measurement variants, not the full source rule. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Auction balance](auction-balance.md) · [Accepted break and defended boundary retest](break-retest.md) · [Thesis, validity band and death condition](thesis-lifecycle.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
