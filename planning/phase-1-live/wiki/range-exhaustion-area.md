# Range exhaustion and mean-reversal area

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The manual draws mean-reversal levels and a shaded exhaustion area beyond each range edge, commonly involving 0.1/0.2/0.3 and the half-width area. Source charts include shallower sweeps and overshoot. [TBR] pp.5, 8–11, 20, 27–30; [JR] pp.53–57.

**Not a standalone trade.** An exact half-width touch is neither compulsory in every raw reversal nor sufficient for one. Location and confirmed rejection are different observations.

**Record before use.** Parent range_id and own W, swept side, chosen source ladder/band, exact depth and overshoot, known_at, first eligible touch and later confirmation.

**Phase 1 observation.** Bind the reversal to its first eligible source sequence rather than the eventual high/low. Keep printed statistical claims scoped; an ambiguous reversal definition cannot be promoted to a method win rate.

**Current implementation (2026-09-12).** [O014 contract](../FORMULAS.md#o014) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Project the configured exhaustion ladder from one frozen range and measure observed sweep depth independently of the source-selected reversal band. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** The ladder is formulaic; author-selected reversal band and coordinate convention are not auto-discovered. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Jumbo reversal and action windows](reversal-time-window.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md) · [Jumbo orderblocks](sweep-cisd-blocks.md) · [Jumbo rejection blocks](rejection-block.md) · [Jumbo failure signatures and three attempts](jumbo-failure-attempts.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
