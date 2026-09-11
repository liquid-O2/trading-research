# Scheduled news and changing information

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md).

News and range conditions change target ambition or thesis validity. Jumbo discusses reduced expectations and delayed cycles; Sires maps the news plan and treats new information as a possible thesis death. [TBR] pp.24, 36–37; [C1] pp.3–6; [AVG] pp.27–29. Green Bird's calendar/bias commentary is context, not an extra trigger. [GB] pp.30–40.

**Not a standalone trade.** A release date or the first touch after a release is not the source's reversal signal. A past macro conclusion is not a current recommendation.

**Record before use.** Event identity, planned time/timezone, schedule known_at, release arrival time and vintage, stated source response, thesis/target adjustment and decision time.

**Phase 1 observation.** Only information already released can kill or revise a thesis at a decision. Do not hard-code news_change=false or assume a full calendar from a dated event file.

**Existing attachments.** [family_levels.load_red_folder](/workspace/implementation/src/trading_research/research/phase1_live/family_levels.py); [formulas_jumbo.j21_class/j21_targets](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_r03_thesis](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-J20/J21/R-R03. Date-only calendar entries do not provide complete event times or release information. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Thesis, validity band and death condition](thesis-lifecycle.md) · [Economic observation and release vintage](economic-release-vintage.md) · [Range width and expectations](range-width-context.md) · [VIX and volatility context](vix-context.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[C1]: </workspace/sources/documents/discretionary/code-1-thesis.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
