# Profile value area

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

VAH and VAL bound the selected profile's value area. They are not the whole price range and can migrate in a developing profile. The lessons commonly discuss 70% value, while Sires's order-flow discussion also uses a 40% intraday setting; the source setting must travel with the object. [VP2] pp.4–6; [C3] pp.6–7; [AMT1] pp.6–9. Saint separately describes 68% value; retain that source fraction rather than importing the other lesson settings. [RTVP] p.4.

**Not a standalone trade.** A VA edge touch is not acceptance, rejection or entry. One source's value fraction is not a global replacement for every profile.

**Record before use.** Profile_id and as_of, VA fraction, construction/tie convention, VAH/VAL, price-range H/L and known_at; fixed prior versus developing identity.

**Phase 1 observation.** Use the profile actually referenced. A prior fixed VA boundary and today's moving VA boundary cannot be exchanged; opening inside balance is not automatically opening inside its VA.

**Existing attachments.** [family_open.value_area](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); [formulas_flow.developing_va](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-A01/A03/A04/A08 and R-S09, P3-04. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Volume profile](value-and-profiles.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [Re-acceptance into value](value-reacceptance.md) · [Opening location and participation](open-location-switch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[C3]: </workspace/sources/documents/discretionary/code-3-orderflow.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
