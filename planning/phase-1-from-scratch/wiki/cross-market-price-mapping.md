# Cross-product price and exposure mapping

Family: **options-data**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[gex-framework.pdf, pp.14–16](../../../sources/documents/discretionary/gex-framework.pdf#page=14) proposesQQQ nodes forNQ andSPY forES without a mapping formula. The user wants futures-options and related cash/ETF reactions as information while executingNQ. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md) [conversation_export (1).md, Turns7,11,12,15–19](../../../sources/documents/conversations/conversation_export%20%281%29.md). [DATA_INVENTORY.md, L249–264,702–745](../../../sources/documents/inventory/DATA_INVENTORY.md) proves QQQ/SPY minute data from 2018 and NDX/SPX cash daily data, not cash-index minute histories; roll maps have incomplete latest coverage.

## Computability and faithful reconstruction

Contemporaneous ETF/futures observations support an explicitly named basis/ratio map. Daily cash marks can support daily measures only. Futures contract units and roll selection must remain explicit.

Retain native underlying price/strike and separate mapped NQ price, mapping-known time, basis uncertainty and source. Never treat mapped futures as observed intraday NDX/SPX cash. NQ is the sole execution target; Phase 1 emits information, not multi-asset trades.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **lagged rolling ratio / additive basis**, **same-time ETF/futures proxy**, **mapping uncertainty bands**, **native-price event versus mapped NQ event**, **expiry/product-specific exposure units**.

## Phase 1 outcomes

Mapping coverage/error, native versus mapped touch disagreement, sister-arrival lag, NQ path after information events and sensitivity by year/session/roll.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q22 fixes mapping and unit conventions. No missing intraday cash or roll history may be fabricated.

## Related

[options chain availability](options-chain-availability.md), [options exposure nodes](options-exposure-nodes.md), [cross asset object arrivals](cross-asset-object-arrivals.md), [inventory and availability](inventory-and-availability.md)

Review findings: D-GEX-01, USER-01, USER-04, USER-05, DATA-02, DATA-04. [Review ledger](../REVIEW_LEDGER.md).
