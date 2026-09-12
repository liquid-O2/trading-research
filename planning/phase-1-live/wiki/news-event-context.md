# Scheduled news and changing information

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md).

News and range conditions change target ambition or thesis validity. Jumbo discusses reduced expectations and delayed cycles; Sires maps the news plan and treats new information as a possible thesis death. [TBR] pp.24, 36–37; [C1] pp.3–6; [AVG] pp.27–29. Green Bird's calendar/bias commentary is context, not an extra trigger. [GB] pp.30–40.

**Not a standalone trade.** A release date or the first touch after a release is not the source's reversal signal. A past macro conclusion is not a current recommendation.

**Record before use.** Event identity, planned time/timezone, schedule known_at, release arrival time and vintage, stated source response, thesis/target adjustment and decision time.

**Phase 1 observation.** Only information already released can kill or revise a thesis at a decision. Do not hard-code news_change=false or assume a full calendar from a dated event file.

**Current implementation (2026-09-12).** [O029 contract](../FORMULAS.md#o029) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Separate schedule publication, actual release, vintage, source response, and thesis revision by their real availability times. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** No news-impact response is inferred before release or from a schedule without vintage identity. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Thesis, validity band and death condition](thesis-lifecycle.md) · [Economic observation and release vintage](economic-release-vintage.md) · [Range width and expectations](range-width-context.md) · [VIX and volatility context](vix-context.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[C1]: </workspace/sources/documents/discretionary/code-1-thesis.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
