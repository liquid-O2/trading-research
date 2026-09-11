# Aggressive effort versus price-response efficiency

Object in [jetbundle — participation and auction states](method-jetbundle-auction-states.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

jetbundle compares participation with actual price response and whether opposite liquidity persists. Efficient aggressive displacement is discovery; large executions with little response and persistent refill support absorption. The Sires/Saint flow reads likewise compare effort with result without inheriting the guest's exact state model. [MATH] pp.6–8; [ABS] pp.8–13; [WIC] pp.4–6.

**Not a standalone trade.** High volume alone is not absorption, and efficient discovery is not an automatic fade.

**Record before use.** Local interval, native aggressive volume, price/mid response, opposing liquidity behavior, source metric/qualitative definition and known_at.

**Phase 1 observation.** Use the same local interval and evidence available by the state/decision. Keep an invented response-per-volume ratio named; do not choose the future reversal as the efficiency window.

**Existing attachments.** [mbp1_objects.absorption_a/absorption_b](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_flow.aggressive_at_level/r_f06_dom_absorption](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F06/F07. Full source efficiency and depth measures are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Provide, withdraw and consume events](order-participation-events.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Executed passive replenishment](passive-replenishment.md) · [B–A–D–E–W auction-state alphabet](auction-state.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
