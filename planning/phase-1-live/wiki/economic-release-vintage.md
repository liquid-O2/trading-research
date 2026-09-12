# Economic observation and release vintage

Object in [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The data engine compares macro evidence through time; thesis/news reads depend on information actually available when used. A historical series value, its first release and a later revision need separate availability records for a causal Phase 1 observation. [DATA] pp.3–6; [C1] pp.3–6; [TBR] pp.24, 36–37.

**Not a standalone trade.** A date-only calendar is not the released value, and a revised series cannot be treated as information available at the original decision.

**Record before use.** Series/event_id, reference period, scheduled/released_at, vintage/revision timestamp, value/units and knowledge time at the decision.

**Phase 1 observation.** Use released_at/available_at, not merely the economic period label. Missing historical vintages leave author-faithful historical inputs unknown; this is a compilation requirement for causal records, not a newly attributed author formula.

**Current implementation (2026-09-12).** [O162 contract](../FORMULAS.md#o162) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Resolve the chosen series/reference-period initial or latest available vintage at the cutoff; preserve release history and reject impossible release ordering or ambiguous ties. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/process_observations.py).

**Evidence limits.** Missing observed availability stays unknown; publication-as-availability remains an explicit assumption. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Scheduled news and changing information](news-event-context.md) · [Stoic's macro indicator set](macro-indicators.md) · [Thesis, validity band and death condition](thesis-lifecycle.md) · [Frozen observation cohort](research-cohort.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[C1]: </workspace/sources/documents/discretionary/code-1-thesis.pdf>
[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
