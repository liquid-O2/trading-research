# Initial balance

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The initial balance is the early completed opening range used to read later range extension and day structure. Its eventual relationship to the whole day is descriptive context. [TPO] pp.3–9; [MAMT] pp.18–23.

**Not a standalone trade.** An IB statistic alone is not an entry edge or permission to trade before the initial interval has finished.

**Record before use.** Source session and initial interval, H/L/W, period membership, completion/known_at and later extension/return times.

**Phase 1 observation.** Use the source initial interval; distinguish its high/low from a prior day's IB. A final-day extension cannot label the initial opening decision.

**Existing attachments.** family_gap and clock/range ingredients; [FORMULAS] R-A10/A14/A15. Later day-type classification remains an outcome. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Time-price-opportunity profile](tpo-ib-auction.md) · [Developing auction day structure](day-type.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
