# Fresh defense of a continuation band

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

An established HTF direction and band have prior control; a return finds the same side defending/refilling with real participation; entry follows that fresh confirmation. If buyers instead break above the short thesis's extreme with strong buying, the clean-continuation source considers a retest long toward VWAP. [NYAM] pp.4–5; [K18] pp.7, 11, 14; [CONT] pp.4–10; [ANAT] p.7.

**Not a standalone trade.** A previous defense is not permanent permission. A break of the thesis's controlling extreme cannot be ignored to keep fading it.

**Record before use.** Thesis/band_id, prior control time, same-band retest, fresh same-side executions/reload, refresh consistency, confirmation and any source flip.

**Phase 1 observation.** Require prior defense < retest ≤ fresh confirmation ≤ decision, and current control matching the live thesis. Price-change signs cannot replace executed delta. Re-entry also needs the attempt and daily-limit checks.

**Current implementation (2026-09-12).** [O130 contract](../FORMULAS.md#o130) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require prior control plus fresh defense at the same band, executed aggression, refresh, and a live matching thesis. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Zone formed by aggressive prints](refill-zone.md) · [Prior defended reaction area](prior-reaction-area.md) · [Executed passive replenishment](passive-replenishment.md) · [Thesis, validity band and death condition](thesis-lifecycle.md) · [Freshly qualified re-entry](reentry.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
