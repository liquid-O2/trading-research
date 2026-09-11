# Source max-pain reference

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The source gamma panels include a max-pain reference alongside walls. A panel's put wall and max pain can coincide in an example; that does not establish universal identity. [GEX] pp.13–19.

**Not a standalone trade.** Max pain is a contextual reference, not a standalone pinning trade or an automatic terminal-price prediction.

**Record before use.** Source product/expiry, printed label/value, snapshot/known_at, calculation convention if supplied and relation to separately labeled walls.

**Phase 1 observation.** Keep the literal source reference distinct from a named payout/OI approximation. Do not derive an entry or guaranteed expiry target from a displayed level.

**Existing attachments.** family_options and [FORMULAS] R-R01/P3-05 have related options inputs. The exact source construction and entry-linked use are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Native options-chain identity](options-nodes.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Source gamma regime](gex-regime.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
