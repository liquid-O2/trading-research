# Prior loss-streak validation for Stoic's overlay

Object in [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md).

Before the overlay, Stoic asks for at least 100 trades, known win rate and average R:R, and a Monte Carlo estimate of maximum consecutive losses. If these are unknown, the source does not admit the overlay. [DATA] p.8.

**Not a standalone trade.** A win streak alone is not a trade or permission to increase risk. Generic bootstrap output is not automatically the source's loss-streak validation.

**Record before use.** Underlying process/version, prior sample and closing times, win-rate/average-RR definitions, supplied Monte Carlo design/result and availability before overlay use.

**Phase 1 observation.** Check sample_n≥100 and all three required metrics known before the risk decision. If no compatible supplied simulation/result exists, validation is unknown; no new simulation is run here.

**Existing attachments.** stats offers generic summaries; [FORMULAS] and current objects have no source-complete validation/overlay state. Exact Monte Carlo construction is unpublished. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Frozen observation cohort](research-cohort.md) · [Outcome distribution of a declared process](outcome-metrics.md) · [Stoic's printed asymmetric risk ladder](asymmetric-risk-state.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
