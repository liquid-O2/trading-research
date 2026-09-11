# Source gamma regime

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Sires's framework uses the relevant 0DTE complex to frame balance/responsive behavior versus aggressive continuation. BIG explicitly restricts aggressive OFM to short gamma and its failure-of-aggression balance fade to long gamma. Other recaps preserve their own regime evidence, including disagreement near the flip. [GEX] pp.4–20; [BIG] pp.14–18; [K18] p.4.

**Not a standalone trade.** A generic sign scenario is not the source's dealer map, and it does not impose one unanimously signed gamma gate on every historical Sires trade.

**Record before use.** Native product/expiry cohort, option snapshot timestamp, source sign/position assumptions, regime label and available_at, selected branch and later reread.

**Phase 1 observation.** Bind the regime available before the branch choice. Preserve uncertainty near the flip and source-specific permissions; price response/confirmation is still required.

**Existing attachments.** [family_gex._gex_day/build_gex_table](/workspace/implementation/src/trading_research/research/phase1_live/family_gex.py); family_options; [FORMULAS] R-R01. Pooled 0–14DTE assumed-sign output is not an author-exact 0DTE regime. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Native options-chain identity](options-nodes.md) · [Gamma-flip reference](gex-flip.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Aggressive Origin of the Move](ofm-aggressive-branch.md) · [Failure of aggression in long-gamma balance](balance-failure-fade.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
