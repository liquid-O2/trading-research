# Options flow, intraday revisions and delayed OI calibration

Family: **options-data**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md) asks to start from prior OI and revise with intraday options volume. [Design robust feature levels.md, user turns L827–834,904–924,1090–1106,1300–1310,1560–1854](../../../sources/documents/conversations/Design%20robust%20feature%20levels.md) requests delayed next-day OI calibration and diagnostic tests. Next-day net OI does not identify each trade’s open/close or dealer side. [gex-framework.pdf, pp.3–5,7,15,20](../../../sources/documents/discretionary/gex-framework.pdf#page=3) shows volume-GEX/net flow but assumes a dealer opposite every trade; this is a scenario, not observation. [DATA_INVENTORY.md, L295–556](../../../sources/documents/inventory/DATA_INVENTORY.md) provides scoped trade_quote paired with NBBO, not pre-signed flow.

## Computability and faithful reconstruction

Quotes/trades enable signing with uncertainty. OI requires release-known time, settlement and revisions. Intraday point-in-time state cannot use next-day OI as if already known.

Store trade sign/confidence, signed/unsigned size, delta/gamma-equivalent units, previous available OI and cumulative scenario revisions. Keep delayed OI in a later observation/validation table. Reconcile aggregate changes without claiming unique trade attribution.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **quote-sign / tick-sign / unknown-sign**, **signed-volume / unsigned-turnover**, **static-OI / capped-flow-revision / uncertainty-band revision**.
- **expiry-bucket and product-specific calibration residuals**, **vendor-overlap**, **time/volume aggregation**. Parameter choice is discovery-only; no dealer-position predictor training.

## Phase 1 outcomes

Flow coverage/unknown mass, next-available OI aggregate residual, revision magnitude and subsequent node-response changes. Compare static versus revised node touch/reject/overshoot and density at matched times.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q20 defines gamma CVD. Q22 defines signing, OI release lag, revisions and intraday update rule; delayed OI is validation data, never contemporaneous truth.

## Related

[options exposure nodes](options-exposure-nodes.md), [cvd constructions](cvd-constructions.md), [options chain availability](options-chain-availability.md)

Review findings: USER-01, USER-04, USER-05, D-GEX-02, DATA-03, CHAT-03, CHAT-04. [Review ledger](../REVIEW_LEDGER.md).
