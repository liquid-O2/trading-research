# Cumulative volume delta and its source reference

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Trade CVD accumulates signed executed volume under a chosen reset. Sires checks its direction/reference with local absorption, reward and retest; a price move and opposing CVD can weaken that reading. The plotted CVD median/reference is not fully defined. [ABS] pp.5, 8–13; [STOP] pp.6–8, 12–14; [BIG] pp.7–14.

**Not a standalone trade.** CVD divergence alone is not an entry, and an OHLC sign proxy is not known aggressor delta. A price-unit median cannot be compared with CVD units.

**Record before use.** Trade-side provenance, accumulation/reset clock, as_of, CVD value, source reference-line construction/unknown flag and local candidate association.

**Phase 1 observation.** Use only pre-decision trades and a like-unit reference. Keep alternative resets or estimated delta explicitly named; missing CVD confirmation remains unknown rather than silently true.

**Existing attachments.** [mbp1_objects.cvd_from_trades](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); family_flow; formulas_flow; [FORMULAS] R-F02/F08/F09/F15 and P3-08. Source reference-line construction and some sign/retest joins are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Executed aggressor-side trades](aggressor-trades.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Four-check absorption reversal](absorption-reward-retest.md) · [Aggressive Origin of the Move](ofm-aggressive-branch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
