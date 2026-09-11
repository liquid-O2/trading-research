# Developing auction open type

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The AMT lesson distinguishes open drive, open test-drive, open rejection-reverse and open auction by the behavior after the open. These guide continuation versus rotational expectations. [AMT1] pp.10–13.

**Not a standalone trade.** The opening type does not replace local confirmation. A final classification cannot be assigned before the behavior that defines it.

**Record before use.** Cash-open price, completed observation interval, path through/away from open, test/rejection sequence, type known_at and unresolved cases.

**Phase 1 observation.** Use the actual cash-open path and only elapsed observations. Keep open type distinct from opening location and final day type.

**Existing attachments.** family_gap; formulas_jumbo open-type helpers; [FORMULAS] R-A10. Prior-VA location or skipping the first minute does not reproduce a no-through-open drive. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [09:30 cash-open price](cash-open-reference.md) · [Opening location and participation](open-location-switch.md) · [Developing auction day structure](day-type.md) · [Initial balance](initial-balance.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
