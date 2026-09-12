# Memory of earlier zone tests

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

The Refill study grades a newly encountered touch using earlier defense history, construction, location and incoming flow. Current-touch outcome must not supply its own memory. [REF] pp.6–10, 16; [OFM] pp.15–18.

**Not a standalone trade.** Remembered defenses are inputs to a read/grade, not an established automatic positive entry edge.

**Record before use.** Zone_id, distinct touch_id, earlier resolved touch times/outcomes, pre-touch features and their max known_at, current touch time and later label.

**Phase 1 observation.** Every memory event must be earlier than the current touch and resolved by its feature time. Retain unselected touches; later-day selection cannot enter a historical decision.

**Current implementation (2026-09-12).** [O117 contract](../FORMULAS.md#o117) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Count only prior resolved touches known by the feature clock and keep current touch and unresolved history outside causal memory. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Zone formed by aggressive prints](refill-zone.md) · [Supplied refill-touch grade](touch-grader.md) · [Frozen observation cohort](research-cohort.md) · [Prior defended reaction area](prior-reaction-area.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
