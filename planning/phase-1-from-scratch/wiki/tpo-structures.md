# TPO single prints, excess and poor extremes

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[tpo-lesson-3.pdf, pp.3–10](../../../sources/documents/discretionary/tpo-lesson-3.pdf#page=3) uses 30m letters A09:30–10:00 and B10–10:30; POC is maximum time-at-price count. Single prints are rows visited by one period. Excess has at least two tail rows of the same letter. Poor extremes show weak/no completed tail; NQ single-row-tail and flat two-letter examples differ. Some source images/text are clipped at the page boundary. [code-3-orderflow.pdf, p.6](../../../sources/documents/discretionary/code-3-orderflow.pdf#page=6) treats unfilled single prints as possible destinations.

## Computability and faithful reconstruction

OHLC can mark rows visited within a period but does not observe every transacted tick; trade-derived TPO is a named comparison. Row size and confirmation govern known_at.

Keep interior single prints separate from tail excess and poor-extreme geometry. Store period membership, row size, completion time, fill/repair history and first-hour IB. Do not retroactively label a developing tail as completed excess.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **trade-visited versus OHLC-spanned rows**, **tick/volatility-scaled row widths**, **15/30/60m periods**, **tail-length/plateau variants**, **VP/TPO agreement ablation**.

## Phase 1 outcomes

First-test excess hold, poor-extreme revisit, single-print partial/full fill, time to repair, IB extension, untouched and yearly stability.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q08 defines exact row size, equal-count POC choice and poor/excess operational boundaries.

## Related

[value profiles](value-profiles.md), [opening range and ib](opening-range-and-ib.md), [cross asset object arrivals](cross-asset-object-arrivals.md)

Review findings: D-TPO-01, D-TPO-02, D-VP-03. [Review ledger](../REVIEW_LEDGER.md).
