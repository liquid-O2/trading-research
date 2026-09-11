# VIX and volatility context

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The VIX lesson uses volatility levels, expected-range examples, completion, events and curve changes to adjust ambition and risk. Those examples frame the trade environment; they do not select a local entry. [VIX4] pp.3–9.

**Not a standalone trade.** A VIX threshold is not a universal direction or stop rule. A later daily VIX close is unavailable to a morning decision.

**Record before use.** Source VIX observation and publication time, pre-decision reference, relevant instrument/range example, event context and selected risk interpretation.

**Phase 1 observation.** Use the last actually available source observation. Keep the source's illustrated point ranges and threshold descriptions scoped rather than replacing all account/structure risk with a VIX lookup.

**Existing attachments.** [formulas.vix_preopen/vix_band](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); family_vol; [FORMULAS] R-R02. Source-compatible time/vintage and exact regime mapping are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Volatility-implied daily-move estimate](expected-daily-move.md) · [Volatility term structure and event change](volatility-curve.md) · [VVIX context](vvix-context.md) · [Scheduled news and changing information](news-event-context.md) · [Exposure fitted to source risk constraints](position-sizing.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VIX4]: </workspace/sources/documents/discretionary/vix-lesson-4.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
