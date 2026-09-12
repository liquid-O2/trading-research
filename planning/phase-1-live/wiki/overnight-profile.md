# Overnight volume structure

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The overnight profile describes accepted volume, bridge LVNs, shelves and POC before the cash open. Sires then reads whether the opening auction holds or aggressively breaks the relevant shelf. [MAMT] pp.14–16; [TBR] pp.16–24.

**Not a standalone trade.** A final-RTH POC cannot be part of the preopen overnight read. An overnight shelf is not a fixed buy/sell level without current confirmation.

**Record before use.** Overnight window/source identity, H/L/POC/VA, bridge and shelf bands, signed inventory evidence, complete profile known_at and opening location.

**Phase 1 observation.** Preserve the profile shown by the source. Do not change an older POC aligned with an overnight LVN into a developing RTH POC chosen after the fact.

**Current implementation (2026-09-12).** [O073 contract](../FORMULAS.md#o073) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Bind overnight profile structure to the exact Sires O011 window, preserve older-POC identity and optional opening response, and never auto-select an LVN. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** The Sires clock is enforceable, while unpublished LVN selection and value-area expansion remain holes. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Overnight directional inventory](overnight-inventory.md) · [Overnight high, low and width](overnight-range.md) · [ETH profile identity](prior-eth-profile.md) · [MPOC: the profile midpoint](mpoc.md) · [Opening location and participation](open-location-switch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>


### September 12 source binding

**Required O011 binding (2026-09-12):** For the [MAMT] p.14 illustrated Sires overnight profile, bind the same dated instrument/window as O011: previous-day 18:00 through current-day 09:30 America/New_York. Preserve this profile separately from prior ETH, prior RTH and developing current RTH. Its VA construction still requires source-specific price-grid and expansion/tie configuration; the clock does not fill those fields.
