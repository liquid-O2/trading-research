# Profile shelf

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

A shelf is a shelf-like accepted volume structure; the body and its transition must be distinguished from the ledge at the edge. It is a location/read used with acceptance, rejection or continuation. [VP2] pp.4–5; [MATH] p.13; [RTVP] pp.7–8.

**Not a standalone trade.** A hand-drawn shelf rectangle is not proof of a computed absorption event, and it is not interchangeable with the value-area boundary.

**Record before use.** Profile_id/as_of, shelf body/band, taper or neighboring low-volume transition, source drawing/construction, known_at and edge identity.

**Phase 1 observation.** Preserve whether the source means the accepted body or transition band. Do not infer a fixed thickness or turn every local volume decline into the same object.

**Existing attachments.** [formulas_jumbo.profile_ledges/profile_nodes](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [FORMULAS] R-A02/A16/A17, R-J17 and P3-07. Source thickness and automatic shelf selection remain partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Profile ledge](profile-ledge.md) · [Low-volume node](lvn.md) · [High-volume node](hvn.md) · [Accepted break and defended boundary retest](break-retest.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
