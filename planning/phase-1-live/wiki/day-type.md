# Developing auction day structure

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

Sires discusses trend, normal, normal variation, neutral and nontrend behavior, with different permitted tactics. MAMT's IB-based day categories have another definition. Saint waits for a new balance in an unbalanced trending profile. [AMT1] pp.10–13; [MAMT] pp.18–20; [RTVP] p.9.

**Not a standalone trade.** A final-day label is not an entry-time filter, and distinct source taxonomies cannot be pooled into one directional switch.

**Record before use.** Author/taxonomy, observation time, elapsed balance/extension evidence, provisional type and final descriptive type in a separate field.

**Phase 1 observation.** Reassess after impulses. Keep the evidence available at each decision; do not substitute a final trend-day label for the earlier thesis or override Saint's rebalance requirement.

**Existing attachments.** family_gap; [FORMULAS] R-A10/A11/A15. Generic daily labels do not implement source-specific evolving permissions. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Developing auction open type](open-type.md) · [Initial balance](initial-balance.md) · [Profile shape and trade permission](profile-shape.md) · [Auction balance](auction-balance.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
