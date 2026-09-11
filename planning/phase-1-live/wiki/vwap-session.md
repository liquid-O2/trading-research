# Session VWAP

Object in [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

VWAP is the auction's volume-weighted average under the selected reset and price basis. Green Bird's explicit continuation returns to VWAP after closing above both session highs; Sires uses VWAP as fair-value location or destination within a thesis. [GB] p.33, posts 2026329904690712970 / 2026386393820283204; [VWAP] pp.3–8; [CONT] p.5.

**Not a standalone trade.** A VWAP touch is not a trade. Green Bird's continuation does not inherit Sires's fade or tape-confirmation rule, and the session reset is not universally established from a settings label.

**Record before use.** Instrument, source reset/anchor and confidence, event price/volume basis, cumulative sums/as_of, VWAP_at_touch and known_at.

**Phase 1 observation.** Only pre-touch volume may define the average. Do not use 18:00 or 09:30 as author-exact without verifying the source; record the reset variant and keep unresolved fidelity unknown.

**Existing attachments.** [formulas_flow.running_vwap](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); family_value; [FORMULAS] R-F01/F03 and partial GB level ingredients. HLC3/bar-volume VWAP is a named approximation; Green Bird's exact reset is unpublished. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Anchored VWAP](vwap-anchored.md) · [VWAP deviation bands](vwap-deviations.md) · [Green Bird's finished session references](session-fail-boxes.md) · [Accepted break and defended boundary retest](break-retest.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
