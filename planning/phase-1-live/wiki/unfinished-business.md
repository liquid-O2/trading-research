# Remaining auction objectives

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md).

An untouched or still-relevant prior/session extreme, POC, poor extreme, single-print area or other source reference can remain a destination. The source method determines when that objective is consumed. [TBR] pp.11–15, 32–35; [JR] pp.23–26, 33–39; [AMT1] pp.12–13; [TPO] pp.5–9; [GB] pp.30–39.

**Not a standalone trade.** The nearest level is not automatically the remaining draw. A later hit cannot choose the pre-entry target, and all methods do not share one purge rule.

**Record before use.** Objective_id, type/bounds, original known_at, source scope, qualifying visit/consumption rule, active state at decision and preselected priority.

**Phase 1 observation.** Freeze identity and priority before entry. In Jumbo's RTH-only application preserve ETH hits without retiring the RTH objective; in the purged-overnight branch retain actual earlier sweeps.

**Current implementation (2026-09-12).** [O087 contract](../FORMULAS.md#o087) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Freeze objective priority and retirement from actual covered visits under the declared RTH/ETH scope and consumption rule. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Absence of a visit requires covered history; ETH visits cannot retire an RTH-only objective. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Chronological liquidity purges](overnight-purge.md) · [PD RTH Range+ destinations](pd-rth-range-plus.md) · [Untested prior POC](naked-poc.md) · [TPO single-print structure](single-prints.md) · [TPO poor high and poor low](poor-extremes.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
