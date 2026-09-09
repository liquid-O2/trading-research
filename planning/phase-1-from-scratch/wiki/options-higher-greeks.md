# Vanna, charm, vega and expiry-conditioned descriptors

Family: **options-data**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[gex-framework.pdf, p.17](../../../sources/documents/discretionary/gex-framework.pdf#page=17) defines vanna as delta sensitivity to IV and charm as delta change with time. Its directional IV-fall/expiry narrative lacks a specified position model. [Design robust feature levels.md, user turns L180–191,461–463,682–700](../../../sources/documents/conversations/Design%20robust%20feature%20levels.md) asks for richer IV/vanna/vega/skew features. [conversation_raw_log.md, L88–96](../../../sources/documents/conversations/conversation_raw_log.md) supports options-surface work.

## Computability and faithful reconstruction

Valid quotes/IV and contract conventions support derivative calculations under named pricing and position scenarios. Vanna/charm sign and units depend on the time/IV parameter convention; actual dealer hedging is unobserved.

Emit unsigned and scenario-signed sensitivities, expiry bucket, spot/IV/time inputs and known_at. Separate per-contract Greeks, aggregated exposure and observed price/flow response. Do not encode universal “falling IV means buying”.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **pricing/sign scenario**, **0DTE versus other expiries**, **spot/IV shock sensitivity**, **static versus flow-revised weights**, **surface/quote coverage strata**.

## Phase 1 outcomes

Descriptor coverage and numerical sensitivity, conditional node paths and response during IV/time changes, yearly stability and missingness. Context prediction remains Phase 2.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q22 fixes pricing, carry/dividends, Greek sign/time convention and expiry boundaries.

## Related

[implied vx curve](implied-vx-curve.md), [options exposure nodes](options-exposure-nodes.md), [options flow oi calibration](options-flow-oi-calibration.md)

Review findings: D-GEX-03, USER-04, USER-02. [Review ledger](../REVIEW_LEDGER.md).
