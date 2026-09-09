# Options chain scope and as-of availability

Family: **options-data**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[DATA_INVENTORY.md, L41–136,295–556](../../../sources/documents/inventory/DATA_INVENTORY.md) lists CME NQ/ES options definitions/statistics/trades/1m OHLC from 2020, with no acquired option-MBP1 established. Theta full-chain daily contracts/EOD/OI start2016 forQQQ/NDX/SPX/SPXW/SPY and 2018 forNDXP; intraday starts2020. Quoted DTE≤14 strike filters are±42QQQ/±70NDX,NDXP/±90SPX,SPXW/±45SPY; DTE≤60 surfaces use ATM±10. Trade_quote is DTE≤7 with the wider symbol filters. VIX quote/OI scope is full chain DTE≤60. MonthlyNDX/SPX last observed2026-08-20; September empty markers do not prove data. Legacy ATM±3/QuantPad overlaps must not double-count. [databento_pull_list.md, L1–91](../../../sources/documents/inventory/databento_pull_list.md) is requested acquisition, not evidence of possession. [conversation_export (1).md, Turns28,37](../../../sources/documents/conversations/conversation_export%20%281%29.md) accepts vendor combination subject to quality and distinguishes daily full-chain from scoped intraday.

## Computability and faithful reconstruction

Compute per-product/expiry/strike coverage, contracts, quote/trade timestamps, release lag and stale/missing fields. Daily full-chain OI does not supply unquoted intraday Greeks automatically.

Canonical contract identity retains source vendor, underlying, right, expiry/settlement, strike, multiplier and correction/version. Partition extrema are clues, not gap-free coverage. A zero-row partition is missing data. Use per-family availability; requested data cannot become a dependency without evidence.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **vendor-overlap agreement/dedup**, **quote-age filters**, **maturity/strike-coverage strata**, **full-daily versus quoted-intraday exposure scenario**.
- Compare limited-quote interpolation only as an explicit experiment with out-of-support masks; do not invent missing Greeks.

## Phase 1 outcomes

Coverage tables and same-time vendor disagreements; valid quote fraction, stale/missing mass, contract completeness and exposure sensitivity to missing strikes. These accompany every node/flow report.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q22 fixes contract/pricing/release conventions where inventory is silent. New purchases or pulls are outside this planning task.

## Related

[options exposure nodes](options-exposure-nodes.md), [options flow oi calibration](options-flow-oi-calibration.md), [implied vx curve](implied-vx-curve.md), [cross market price mapping](cross-market-price-mapping.md)

Review findings: DATA-01, DATA-03, DATA-04, DATA-05, USER-05. [Review ledger](../REVIEW_LEDGER.md).
