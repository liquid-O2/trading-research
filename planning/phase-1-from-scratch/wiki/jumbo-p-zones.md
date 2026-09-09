# Jumbo distance/filter probability regions

Family: **Jumbo**. Measure now when Q05 resolves; specify and compare named approximations in Phase 1. Learned reversal grading is deferred to Phase 3.

## Evidence and source rules

[xfcmg2.pdf, p.30; post 2005418003593363762](../../../sources/documents/jumbo/xfcmg2.pdf#page=30) describes per-ticker distance-based support/resistance regions filtered by volume and volatility. [xfcmg2.pdf, pp.34–39; posts 1987966234349187569,1985520929984639330](../../../sources/documents/jumbo/xfcmg2.pdf#page=34) adds session history, live volatility scaling, volume scans and extended zones on high-activity days. The UI shows a 500-session learning window, percentile scaling, T1/T2 and optional T3/T4, invalidation deletion, NY/London/Asia frameworks and a 09–18 engine. It does not disclose distance, filter or invalidation formulas. 09:00, 09:30 and 10:00 examples remain distinct.

[jjumbo-findings.pdf, pp.7–8,12–13](../../../sources/documents/jumbo/jjumbo-findings.pdf#page=7) proposes open/mid anchoring, similar-volatility history and VP-node snapping. This is a secondary approximation, not the original construction. The user asks for upgrades and improved probability regions. [conversation_raw_log.md, L17,40–47,113–126](../../../sources/documents/conversations/conversation_raw_log.md).

## Computability and faithful reconstruction

Historical price, volume and volatility inputs are available on family-specific samples. A faithful numerical region cannot be reconstructed from an undisclosed formula. The screenshot proves appearance and settings, not an algorithm or timestamped historical level feed.

Record the known parameter interface and source images. Mark exact faithful construction **blocked-definition Q05**, never silently substitute an extension or a learned reversal grader. Once formula/code or a user definition is supplied, freeze it and log every created, extended and invalidated region with known_at.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **distance-quantile-session-memory**: prior-session distance distributions with discovery-frozen percentile settings.
- **vol-scaled-distance**: compare GK/YZ/RV/HAR descriptors as scales, with and without a volume filter.
- **open-anchor / range-mid-anchor**, **history-500 / shorter rolling history**, **node-snap-ablation**, **fixed-clock/trade/activity-bar** formation. These are explicit experimental approximations. None earns the faithful label without Q05.
- The learned adaptive reversal model mixing rails, profiles and gamma is Phase 3.

## Phase 1 outcomes

Same zone table for benchmark and experiments: creation coverage, width/density, touch, reject, overshoot, breakout/continuation, invalidation before touch, non-touch and year stability. Compare at matched density and distance. No backtested P&L or winner declaration while the benchmark is missing.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q05: exact distance anchor/function, history sample, percentile calculation, volatility/volume filters, T1–T4, invalidation and session rules. Missing source code is a definition blocker, not permission to invent trading semantics.

## Related

[extension projections](extension-projections.md), [sessionstat envelopes](sessionstat-envelopes.md), [value profiles](value-profiles.md), [options node lifecycle](options-node-lifecycle.md), [deferred context location](deferred-context-location.md)

Review findings: J-X-03, J-X-05, J-X-10, J-X-11, J-X-12, J-X-14, J-SECONDARY-01. [Review ledger](../REVIEW_LEDGER.md).
