# Passive Origin-of-the-Move variant

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The passive example's squeeze fails without aggressive orders at that failure as tape speed dies. The illustrated long enters above the buyers' area with a stop below the aggression and a 1R–3R scalp objective. The source calls it a passive version of the same model. [OFM] p.14.

**Not a standalone trade.** This branch must not inherit a requirement for aggressive failure prints. The replay does not publish a universal gamma condition or a mirrored short rule.

**Record before use.** Source squeeze/failure, local dying-tape and no-aggression evidence, buyer area known_at, trigger above it, structural stop and chosen scalp objective.

**Phase 1 observation.** Check source failure < entry trigger ≤ decision, with the demonstrated area/stop relationship. Preserve unpublished quantitative pace thresholds as unknown rather than borrowing the aggressive branch's test.

**Current implementation (2026-09-12).** [O127 contract](../FORMULAS.md#o127) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Audit the long-only passive OFM failure, dying tape, buyer area, entry, stop, and one-to-three-R geometry without automatic selection. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Origin-of-the-Move catalyst](ofm-catalyst.md) · [Speed of tape](tape-speed.md) · [Entry-side structural invalidation](structural-risk.md) · [Aggressive Origin of the Move](ofm-aggressive-branch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
