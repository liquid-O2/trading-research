# Timed returns to opens, midpoints and earlier rails

Family: **Jumbo**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[xfcmg2.pdf, pp.14–16,21–22,26–29](../../../sources/documents/jumbo/xfcmg2.pdf#page=14) contains midpoint, range-open and opposite-edge returns, including a segment table for low sweeps. [Time based Range Retracement with Stats.txt, L15–89,148–414](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has five distinct formation/intermediate/later-return clocks; its conditional midpoint visit does not require departure. [Time based level retracement - stats.txt, L16–75,137–201](../../../sources/documents/indicators/Pinescript-indicators--main.zip) projects fractions from 08:00 open toward earlier opens, including literal fifth interval 0700–0501. [Time based retracement by DOW - stats.txt, L12–41,157–227](../../../sources/documents/indicators/Pinescript-indicators--main.zip) adds midnight→08 and 08→09:30 pairs with side labels tied to the earlier anchor.

[Hourly Time Levels.txt, L1–155](../../../sources/documents/indicators/Pinescript-indicators--main.zip) draws triggering-bar open and close rails, despite open-only labels. [MTF OHLC retracement stats.txt, L145–236](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses endpoint crossings, not necessarily touches or sweep-returns. [NQ Hourly Retracements 12y Stats with Levels.txt, L105–313](../../../sources/documents/indicators/Pinescript-indicators--main.zip) reports hardcoded return rates to broken edge/mid/current open/opposite edge. [Pre-market session levels and stats.txt, L789–1073](../../../sources/documents/indicators/Pinescript-indicators--main.zip) calls a return only when close is within 0.0001 price of the 06:00 open. [AM TBR - NQ Stats.txt, L1–700](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has first-touch and return-to-08-open statistics with same-minute order ambiguity.

## Computability and faithful reconstruction

OHLC and trade samples support separate ordered and ambiguous counts. Known_at for a close rail is bar close; an open rail is available at the first eligible observation.

Each event identity includes formation clock, trigger, target, return window, departure rule and censoring. Preserve unconditional target visit versus trigger-conditioned return. A bar touching target before breaking the rail is not a post-break return.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **trade-ordered**, **close-only versus range-contact**, **departure/rearm**, **zero-distance-separated**.
- **25/50/75/100-percent target**, **fixed-grid-neighbor clocks**, **time/trade/volume/dollar-bar formations**, and **prior-only distance-normalized** comparisons.

## Phase 1 outcomes

Target visit, first passage, time from trigger, overshoot before return, opposite edge after return, nonreturn, timeout and ambiguous order. Report each source window independently and preserve all eligible sessions.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q01 defines event mechanics. Q03 asks whether the literal fifth clock 0700–0501 is intended; preserve source-as-coded pending an answer.

## Related

[range break paths](range-break-paths.md), [session raid and return](session-raid-and-return.md), [extension projections](extension-projections.md)

Review findings: J-X-05, J-X-07, J-X-10, ZIP-07, ZIP-25, ZIP-36, ZIP-37, ZIP-39, ZIP-40, ZIP-52, ZIP-63, ZIP-73, ZIP-74, ZIP-76, ZIP-80, ZIP-81. [Review ledger](../REVIEW_LEDGER.md).
