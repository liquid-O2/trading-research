# Implied volatility, skew and daily VX descriptors

Family: **volatility**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[vix-lesson-4.pdf, pp.3–9](../../../sources/documents/discretionary/vix-lesson-4.pdf#page=3) uses VIX/√252 as an approximate daily return move, regime thresholds, ES/VIX nonconfirmation, pre-news rise/crush, VX contango/backwardation and VVIX-leading hypotheses. Its ES point examples are not universal NQ high-low thresholds. [gex-framework.pdf, pp.7,13,15](../../../sources/documents/discretionary/gex-framework.pdf#page=7) displays ATM IV and IV−RV without all formulas. The user wants IV/surface inputs across NDX/QQQ/SPY and futures. [conversation_raw_log.md, L88–96](../../../sources/documents/conversations/conversation_raw_log.md).

[Expected Volatility .txt, L11–13,30–100](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses priorNASDAQ:VOLI, IV/16 versus IV/√365 log-price bands. VOLI is not proved acquired. [DATA_INVENTORY.md, L560–737](../../../sources/documents/inventory/DATA_INVENTORY.md) proves daily VIX/VXN/VIX 3M/VVIX and daily monthly/weekly VX curves, not intraday VX or cash VIX. Option quotes provide scoped intraday IV reconstruction.

## Computability and faithful reconstruction

Use only previous-available daily descriptors intraday. Chain IV/skew requires valid quote, underlying, rates, dividend/carry, expiry and pricing convention. Missing/stale IV is not zero.

Preserve source VIX and annualization bands; mark VOLI-dependent benchmark data-blocked. Named VXN/chain-IV replacements cannot be called VOLI. Retain spot/curve product and maturity identity.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **trading/calendar-time annualization**, **linear/log bands**, **VXN versus VIX**, **chain ATM IV/skew/term structure**, **IV−GK/YZ/RV**, **VX curve slope/curvature**, **lagged VVIX**.
- Fixed sampling/maturity buckets and matched-calendar comparisons; no forecast fitting.

## Phase 1 outcomes

Band coverage, vol-gap and curve-state support, conditional price-path/zone response, estimator stability and missingness. News conditioning uses only known releases.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q22 fixes pricing/IV conventions and expiry buckets. Unsupported VOLI/intraday VX stays unavailable, with a named available proxy experiment.

## Related

[realized volatility](realized-volatility.md), [options chain availability](options-chain-availability.md), [event calendar conditioning](event-calendar-conditioning.md)

Review findings: D-VIX-01, D-VIX-02, D-GEX-02, USER-02, DATA-04, ZIP-18. [Review ledger](../REVIEW_LEDGER.md).
