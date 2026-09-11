# Profile point of control

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

Volume POC identifies the highest-volume price under the selected construction. It can be fair-value destination, a continuation test or part of another auction reference. Saint reads failure versus efficient passage at POC; Sires's strict absorption fade excludes a middle/POC location. [VP2] pp.3–7; [AMTL] pp.8–11; [ABS] pp.5–8.

**Not a standalone trade.** POC is neither the geometric midpoint nor universally a place to fade. One branch's POC restriction does not ban its use as another branch's target.

**Record before use.** Profile_id, source scope/as_of, volume-price bins and tie rule, POC price/band, available_at and role in this candidate.

**Phase 1 observation.** Match the specific prior/current/older POC before measuring touch or passage. The after-the-fact POC/refill alignment in the clean-continuation recap cannot become a pre-entry gate. [CONT] p.9.

**Existing attachments.** [family_open.value_area](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); [mbp1_objects.vp_rth](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_jumbo.a05_poc_tell](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [FORMULAS] R-A05/A06 and P3-04. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Volume profile](value-and-profiles.md) · [Untested prior POC](naked-poc.md) · [MPOC: the profile midpoint](mpoc.md) · [POC failure versus efficient passage](poc-traversal.md) · [Sires's narrower Failed Auction setup](failed-auction-sires.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
