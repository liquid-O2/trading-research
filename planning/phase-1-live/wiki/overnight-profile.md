# Overnight volume structure

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The overnight profile describes accepted volume, bridge LVNs, shelves and POC before the cash open. Sires then reads whether the opening auction holds or aggressively breaks the relevant shelf. [MAMT] pp.14–16; [TBR] pp.16–24.

**Not a standalone trade.** A final-RTH POC cannot be part of the preopen overnight read. An overnight shelf is not a fixed buy/sell level without current confirmation.

**Record before use.** Overnight window/source identity, H/L/POC/VA, bridge and shelf bands, signed inventory evidence, complete profile known_at and opening location.

**Phase 1 observation.** Preserve the profile shown by the source. Do not change an older POC aligned with an overnight LVN into a developing RTH POC chosen after the fact.

**Existing attachments.** [family_open.value_area](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); family_value; [FORMULAS] R-A12/A13, R-J06 and P3-04. Exact source band selection and some POC-alignment joins are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Overnight directional inventory](overnight-inventory.md) · [Overnight high, low and width](overnight-range.md) · [ETH profile identity](prior-eth-profile.md) · [MPOC: the profile midpoint](mpoc.md) · [Opening location and participation](open-location-switch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
