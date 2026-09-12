# Iceberg evidence and added participation

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The DOM lesson refines defense through executed depletion, continuing replenishment and additional participants joining in the illustrated two-tick area, then entry behind the defended structure. [DOM7] pp.3–7. The auction-state discussion likewise requires persistent liquidity rather than a static wall. [MATH] pp.6–8.

**Not a standalone trade.** A hidden-order hypothesis is not proof of hidden reserve and is not a standalone entry. Spoof-like displayed size without executions fails the evidence read.

**Record before use.** Executed consumption, displayed refill at the same price, persistent defense, added participant events, local price response and source-known timing.

**Phase 1 observation.** Require actual execution before inferring replenishment. Missing source depth makes the faithful hidden-liquidity claim unknown; the specific lesson's two-tick refinement is not a universal detector setting.

**Current implementation (2026-09-12).** [O103 contract](../FORMULAS.md#o103) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compare executed and displayed quantities within the declared area while refusing to infer participant identity or hidden reserve from BBO alone. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Executed passive replenishment](passive-replenishment.md) · [DOM at a planned location](dom.md) · [At-level DOM rejection](dom-rejection-branch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM7]: </workspace/sources/documents/discretionary/dom-lesson-7.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
