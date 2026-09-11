# Time-price-opportunity profile

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Keani — open above value](method-keani-open-above-value.md).

TPO records which source letter periods visited each price and shows the time structure of the auction. It provides value context, single prints, excess, poor extremes and opening-period information. Keani's whole-A-period requirement uses this object. [TPO] pp.3–9; [AVG] pp.21–22.

**Not a standalone trade.** A TPO shape or label is not an entry. A trade-visited approximation is not automatically the same as the source's letter construction.

**Record before use.** Profile/session_id, price step, period duration/labels, per-price period membership, as_of, completed periods and known_at.

**Phase 1 observation.** Retain letter identity, not just counts. A period is complete at its end; final-day tails and single prints cannot qualify a morning entry.

**Existing attachments.** [mbp1_objects.tpo_trade_visited](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); family_gap; [FORMULAS] R-A04/A14/A15 and R-S09, P3-04. Period identity and developing structure are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [TPO single-print structure](single-prints.md) · [TPO excess at auction extremes](excess.md) · [TPO poor high and poor low](poor-extremes.md) · [Initial balance](initial-balance.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
