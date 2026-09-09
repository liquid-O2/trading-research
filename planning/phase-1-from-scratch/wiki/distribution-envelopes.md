# Empirical excursion, range and close distributions

Family: **Jumbo**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

Keep these distributions distinct: H−O; O−L; H−L; C−O; ex-post color-conditioned opposing excursion (“manipulation”); same-side excursion (“distribution”); and maximum absolute excursion. “Manipulation” is a path label, not intent. [Daily statistical range and levels.txt, L67–125,664–864](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses different plot/stat anchors. [Session Based Statmap with closing stats.txt, L211–330](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses last 60 non-dojis; [session_statmap, L482–488](../../../sources/documents/indicators/Pinescript-indicators--main.zip) calls the midpoint of mean asymmetric bounds a “range median”. [Statmap HTF no like for like lookback.txt, L123–326,581–654](../../../sources/documents/indicators/Pinescript-indicators--main.zip) pools hours and uses nearest order statistics. [Statistical OHLC Projections HTF.txt, L161–202,313–432,488–505](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has future-HTF/first 60 and drifting-anchor problems; sum of medians is not median of sums.

[NQ Stats Price Distributions.txt, L60–239,408–428,630–811](../../../sources/documents/indicators/Pinescript-indicators--main.zip) supplies 32 anchors, 19 P5–P95 grids, net-return sigma, hardcoded claims and clipped daily-vol scaling. Ranking current net return against maximum excursions is a different statistic. [Session Statistical Levels.txt, L456–791,1096–1162](../../../sources/documents/indicators/Pinescript-indicators--main.zip) freezes prior quantiles but later counts against current-inclusive thresholds; retain that disagreement. [Session standard deviations with stats.txt, L158–227,651–755](../../../sources/documents/indicators/Pinescript-indicators--main.zip) pools bar deviations from their own session opens, weighting longer days more.

[Daily High Low probability zones.txt, L14–44,88–185](../../../sources/documents/indicators/Pinescript-indicators--main.zip) bins next-day extreme coordinates into twelve fixed 25%-width prior-range bins plus outside tails. It is not a post-touch reversal model. [ADR Levels with Stats.txt, L1–556](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has zero-filled warmup and conflicting plot/stat half/full ADR anchors. [HTF Candle Stats by Time of Day.txt, L1–316](../../../sources/documents/indicators/Pinescript-indicators--main.zip) supplies slot-specific OHLCV means with lookahead and oldest-sample issues. Other projection sources and their exact contrasts are mapped in SOURCE_MECHANISMS.

## Computability and faithful reconstruction

OHLC supports the longest honest sample. Trades distinguish ordered excursions. Daily options/IV scales only join where actually known.

Emit raw per-session distances first. Keep final color solely in outcome-conditioned tables. Preserve source formula variants, including current-inclusive and hardcoded versions, as benchmark diagnostics; future-informed values cannot enter earlier features or confirmation estimates. Recompute historical rates independently; do not reuse source fits overlapping 2024–2026.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **prior-only-rolling**, **like-for-like-clock versus pooled**, **doji-inclusive**, **linear versus nearest quantile**.
- **directional versus symmetric**, **equal-session versus pooled-bar dispersion**, **range-SD versus return-SD versus excursion-SD**, **GK/YZ/RV scale**.
- **frozen-counter thresholds**, **empirical-CDF/tail-censoring**, **actual-calendar short days**, and fixed-grid/trade/activity-bar variants.
- Quantile fitting is descriptive discovery estimation; do not train a Context predictor.

## Phase 1 outcomes

Quantile/band coverage; upper/lower/both/neither touches; signed close CDF; separately ordered tag→inner return/outer extension/close-inside; support, tail censoring and year stability. Compare unconditional, break-conditional and final-color-conditional populations explicitly.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q01 fixes common outcome horizons. Source-as-coded formulas with inconsistent labels remain separate from intended-label variants; they must not be silently repaired.

## Related

[sessionstat envelopes](sessionstat-envelopes.md), [extension projections](extension-projections.md), [realized volatility](realized-volatility.md), [timed retracements](timed-retracements.md)

Review findings: ZIP-06, ZIP-07, ZIP-14, ZIP-16, ZIP-21, ZIP-28, ZIP-29, ZIP-45, ZIP-49, ZIP-52, ZIP-55, ZIP-57, ZIP-58, ZIP-59, ZIP-62, ZIP-63, ZIP-65, ZIP-67, ZIP-68, ZIP-70, ZIP-83. [Review ledger](../REVIEW_LEDGER.md).
