# VWAP anchors and deviation bands

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[vwap-lesson-10.pdf, pp.3–8](../../../sources/documents/discretionary/vwap-lesson-10.pdf#page=3) uses volume-weighted mean and ±1/2/2.5(optional3) bands, visible HLC3 source, session and swing/event/weekly/monthly anchors. Calling the mean “median/POC” or reversing band signs does not change its math. Bands can be walked in expansion. The user explicitly wants all-session VWAP and 2/2.5 sigma comparisons. [conversation_raw_log.md, L113–129](../../../sources/documents/conversations/conversation_raw_log.md).

[Statistical VWAP study Session and RTH VWAP.txt, L238–265,373–449,498–571](../../../sources/documents/indicators/Pinescript-indicators--main.zip) resets the06–09 VWAP on each new high, then continues to exchange-day change; RTH VWAP is separate. Its two-VWAP midpoint residual RMS is not centered SD, and median absolute residual from zero is not median-centered MAD. Source “win” is an ex-post close association, not P&L.

## Computability and faithful reconstruction

Trade price×size yields actual VWAP. HLC3×bar volume is the faithful approximate branch. Event/swing anchors need availability; daily calendar inputs cannot be backdated.

Name each anchor and reset rule, price source, weighting and dispersion formula. Preserve dynamic-high anchor separately from fixed06 and RTH. Store VWAP and bands as time-varying versions; a touch uses the version known at arrival.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **trade-VWAP versus HLC3**, **full exchange session / RTH / fixed06 / dynamic-high / dynamic-low**, **confirmed swing/event anchors**.
- **centered weighted SD**, **median-centered MAD**, **signed RMS**, **empirical residual quantiles**; moving versus frozen anchor residuals.
- **departure/rearm** and clock/bar sampling variants.

## Phase 1 outcomes

Band touch, rejection, reversion to mean/inner band, overshoot, band walking, accepted crossing, retests and untouched coverage by year/session/volatility.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q03 fixes all-session day boundary; Q11 fixes anchor events and source dispersion interpretation where unavailable. Proposed robust estimators remain experiments.

## Related

[value profiles](value-profiles.md), [cvd divergence](cvd-divergence.md), [realized volatility](realized-volatility.md)

Review findings: D-VWAP-01, D-VWAP-02, USER-02, ZIP-69. [Review ledger](../REVIEW_LEDGER.md).
