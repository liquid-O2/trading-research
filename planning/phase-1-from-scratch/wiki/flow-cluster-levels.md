# OHLC flow clusters and anomaly reception zones

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[momentum-volume-flow-levels.txt, L1–190,199–488](../../../sources/documents/indicators/momentum-volume-flow-levels.txt) detects abs(delta)>max(6×SMA 50(abs(delta)),3000), current bar included. Anomaly volume>2.5×SMA 20 creates0.2%-wide close zones;0.5% merge retains greater volume, cap50. Signed detections anchor to min/max(O,C), weighted by abs(delta). Separate-side kmeans k4/12iterations uses quantile starts, min/max cluster edges padded to0.4ATR14, keeps≥45% strongest and caps3000/side. No daily reset or decay. Retrospective drawings and plot toggles affect apparent history. Seven correlated votes with hysteresis4 form a descriptive state; same-bar direction can follow array order. The user reports useful but overly dense QQQ NYAM reception levels. [conversation_raw_log.md, L201–212](../../../sources/documents/conversations/conversation_raw_log.md).

## Computability and faithful reconstruction

OHLC reproduces the source flow proxy and clustering on long samples. Trade delta gives a shorter actual-aggression variant. Historical cluster versions need causal reconstruction.

Keep source anomaly zones, positive/negative cluster edges and votes distinct. Record membership, bounds, first-known time, revision and deletion. Earlier constituent time is not cluster availability. Source same-bar order stays a flagged diagnostic.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **true-trade anchors**, **session-reset/age decay**, **prior-only thresholds**, **density-adaptive clustering**, **volume/dollar-bar observations**.
- **fixed-density** and **matched-width/distance** reaction comparisons address excessive levels. Learned selection of which zone deserves action is Phase 3.

## Phase 1 outcomes

Zone density, coverage, first/repeated touch, rejection/overshoot/continuation, node persistence, vote-state duration and disagreements. Compare QQQ and NQ explicitly on their samples.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q01 defines touch/rearm. All literal source formulas can be benchmarked; causal and density upgrades remain separately named.

## Related

[cvd constructions](cvd-constructions.md), [nodes shelves ledges](nodes-shelves-ledges.md), [options node lifecycle](options-node-lifecycle.md), [adaptive indicator states](adaptive-indicator-states.md)

Review findings: PINE-BIAS-01, PINE-BIAS-02, PINE-BIAS-03, USER-02. [Review ledger](../REVIEW_LEDGER.md).
