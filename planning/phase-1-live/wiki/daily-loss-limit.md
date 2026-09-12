# Source account and session stop

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The sources limit further exposure after adverse results or when the planned session is finished. STOP's illustrated rule forbids another entry at −4R; other recaps/account examples retain their own constraints and inconsistent example dollar amounts. [STOP] pp.14–15; [ANAT] pp.5, 11; [TBR] p.37; [GB] pp.37–40; [K10] pp.4–5; [DATA] p.8.

**Not a standalone trade.** One account's −4R, dollar cap or contract count is not a universal author limit. A session stop is not an entry signal.

**Record before use.** Author/account, stated policy and units, baseline/reset clock, realized/remaining risk before each attempt, source session-end decision and rule breach if any.

**Phase 1 observation.** Apply the specific source policy known before the attempt. In STOP's branch daily R before must be greater than −4; do not erase earlier losses through re-entry naming or a later policy change.

**Current implementation (2026-09-12).** [O145 contract](../FORMULAS.md#o145) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compute daily R strictly from same-source/account/session prior results and enforce the fixed pre-entry policy limit. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Exposure fitted to source risk constraints](position-sizing.md) · [Freshly qualified re-entry](reentry.md) · [Thesis and execution journal](process-journal.md) · [Prior loss-streak validation for Stoic's overlay](loss-streak-validation.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
