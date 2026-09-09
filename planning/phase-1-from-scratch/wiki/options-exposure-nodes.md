# Gamma exposure, walls, flips and settlement nodes

Family: **options-data**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[gex-framework.pdf, pp.6–16,20](../../../sources/documents/discretionary/gex-framework.pdf#page=6) hypothesizes positive gamma stabilization, negative gamma amplification, pinning and flip crossings. Call wall is largest call gamma above; put wall largest put gamma below. Max pain minimizes option settlement value. The source favorsQQQ0DTE forNQ andSPY forES. Call/put right is not actual position sign, and a per-strike sign cross is not necessarily an aggregate zero-gamma root. The source acknowledges assumptions.

[zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp, full image, SPX main and QQQ/SPY companion panels](../../../sources/documents/reference-images/zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp) shows0DTE positive/negative colored nodes, strengths, persistence and disappearance; no formula or causal level log is supplied. The user asks for improved nodes, intraday revision and reactions at modest nodes. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md) [Design robust feature levels.md, user turns L11–16,180–191,320–332,461–463,682–700](../../../sources/documents/conversations/Design%20robust%20feature%20levels.md).

## Computability and faithful reconstruction

OI, scoped quotes, trades and underlying inputs support scenario-based Greeks/exposure. Product multiplier and NQ mapping are explicit. Dealer inventory is not observed.

Emit per-contract/per-strike exposure under named position-sign scenarios and separate OI/volume bases. Gamma units and spot-shock convention must be versioned. A total-GEX flip solves aggregate exposure as spot changes under the chosen scenario; never substitute a sign change across strike rows. Store call/put walls, high-OI nodes, max-pain settlement value and expiry buckets as distinct objects.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **OI-static versus intraday-flow-revised**, **net versus gross/unsigned gamma**, **0DTE/front-week/longer buckets**, **multiple local nodes versus largest wall**, **strength/density normalization**.
- **pricing/sign-model sensitivity**, **quote-coverage sensitivity**, **smaller-node inclusion**. Compare modest and dominant nodes on identical outcomes.

## Phase 1 outcomes

Node creation/coverage, price/strength, approach/touch, dwell/pin, reject/overshoot, crossing/acceleration, no-touch, disappearance and year stability. GEX sign is a scenario descriptor, not observed dealer positioning or a Phase 1 trade rule.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q22 fixes pricing and sign conventions; Q23 defines the faithful node formula/smoothing/width from the otherwise undisclosed screenshot. A proprietary visual cannot be claimed reproduced.

## Related

[options chain availability](options-chain-availability.md), [options node lifecycle](options-node-lifecycle.md), [options flow oi calibration](options-flow-oi-calibration.md), [options higher greeks](options-higher-greeks.md), [cross market price mapping](cross-market-price-mapping.md)

Review findings: D-GEX-01, D-GEX-02, IMAGE-01, USER-01, USER-04. [Review ledger](../REVIEW_LEDGER.md).
