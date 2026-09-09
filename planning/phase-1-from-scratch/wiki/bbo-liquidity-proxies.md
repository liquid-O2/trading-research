# Best-book resilience, withdrawal and replenishment proxies

Family: **auction-order-flow**. Measure MBP-1 proxies now. Exact all-depth stacking, iceberg reserve and intent claims are not computable; do not add MBP-10/MBO prerequisites.

## Evidence and source rules

[dom-lesson-5.pdf, pp.3–7](../../../sources/documents/discretionary/dom-lesson-5.pdf#page=3) separates aggressive executions and passive displayed liquidity. [dom-lesson-6.pdf, pp.3–7](../../../sources/documents/discretionary/dom-lesson-6.pdf#page=3) defines stacking/pulling and effort without progress. [dom-lesson-7.pdf, pp.3–7](../../../sources/documents/discretionary/dom-lesson-7.pdf#page=3) describes hidden reserve, reload/hold, vanishing size and spoof/layer/flip narratives. [the-math-behind-auction-market-theory.pdf, pp.5–11](../../../sources/documents/discretionary/the-math-behind-auction-market-theory.pdf#page=5) distinguishes provide/withdraw/consume and response efficiency. The user prefers MBP-1 and asks for useful inference from it. [conversation_raw_log.md, L45–58](../../../sources/documents/conversations/conversation_raw_log.md).

## Computability and faithful reconstruction

MBP-1 observes the best bid/ask, updates and executions. It does not observe the full ladder, common order owner, canceled-order intent or total hidden reserve. Missing depth is not zero depth.

Emit best-price size before/after executions, same-price duration, replacement size, quote disappearance with/without prints, spread and price response. Handle best-price movement separately from same-price replenishment. Label outputs as observable proxies, not identified iceberg/spoof events.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **execution-conditioned refill ratio**, **time-normalized renewal**, **same-best-price survival**, **spread/volatility-normalized resilience**, **quote-only vanish versus executed depletion**.
- Compare time/event/volume windows and lagged baselines; retain raw fields for sequence measurement.

## Phase 1 outcomes

Proxy coverage, persistence, price hold/breach, depletion-to-move delay and transition frequencies. Report missing sequence/quote-side records and no-event periods.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q15 fixes what the source means by replenishment “ticks”. Full-book/identity mechanisms are unidentifiable with this schema; their best-book proxies remain measurable.

## Related

[absorption stages](absorption-stages.md), [auction state transitions](auction-state-transitions.md), [refill memory](refill-memory.md)

Review findings: D-DOM-01, D-DOM-02, D-DOM-03, D-STATE-01, USER-02. [Review ledger](../REVIEW_LEDGER.md).
