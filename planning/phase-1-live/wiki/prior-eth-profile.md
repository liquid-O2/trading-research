# ETH profile identity

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The source's ETH profile must be identified from its actual auction window and labels. The AMT statistics distinguish overnight extremes and the previous ETH balance; those are not automatically prior RTH value or a generic full-day profile. [MAMT] pp.14–16; [TBR] pp.16–24.

**Not a standalone trade.** Calling a profile ETH does not settle whether it is the overnight interval, prior full session or another selected auction. Its target statistic is not an entry.

**Record before use.** Source literal label, dated start/end and prior-session relationship, profile bounds/VA/POC/MPOC, as_of and known_at.

**Phase 1 observation.** Keep the 94% either-overnight-edge claim separate from the 73% open-inside-previous-ETH-balance claim. If a drawing and prose do not settle balance versus VA or exact scope, record the conflict rather than choose the convenient denominator.

**Current implementation (2026-09-12).** [O075 contract](../FORMULAS.md#o075) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Keep prior-ETH profile identity distinct and evaluate source scope, balance/value bands, and cohort eligibility at the open. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** Cohort eligibility remains unknown until source scope is resolved and the ETH profile identity is correct. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Overnight volume structure](overnight-profile.md) · [MPOC: the profile midpoint](mpoc.md) · [Profile value area](value-area.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
