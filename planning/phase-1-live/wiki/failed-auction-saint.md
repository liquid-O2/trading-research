# Saint's failed auction and return to value

Object in [Saint — AMT on live markets](method-saint-amt.md).

Saint reads attempted acceptance in lower/older value, its failure, return into the original balance, and renewed POC/control evidence. The live sequence can dip deeply and take time to confirm. [AMTL] pp.8–12.

**Not a standalone trade.** This is Saint's route within HTF/LTF alignment. Sires's instant rejection at an older POC is not mandatory for every Saint example.

**Record before use.** Original and tested value IDs, prior known times, exploration/rejection/reacceptance events, local control, POC read and chosen objective.

**Phase 1 observation.** Require the original balance to be actually reaccepted and the local control to confirm the return. Do not merge the authors' differing failed-auction definitions into a single trigger.

**Existing attachments.** [formulas_jumbo.a08_reaccept/a05_poc_tell](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) and profile ingredients; [FORMULAS] R-A03/A05/A08. The complete Saint event sequence is missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Re-acceptance into value](value-reacceptance.md) · [POC failure versus efficient passage](poc-traversal.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md) · [Sires's narrower Failed Auction setup](failed-auction-sires.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
