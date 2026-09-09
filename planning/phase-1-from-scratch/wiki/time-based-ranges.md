# Time-based ranges and internal rails

Family: **Jumbo**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Time-Based ranges Framework (JJumbo).pdf, pp.4–7,32–35](../../../sources/documents/jumbo/Time-Based%20ranges%20Framework%20%28JJumbo%29.pdf#page=4) defines NY formation clocks 20:00–20:30, 00:00–00:30, 03:00–03:30, 06:00–09:00, 09:30–10:00, 10:00–10:30, 12:00–12:30 and 15:00–15:30. Store H/L, O/C, midpoint and 25/75% rails. Prior RTH is 09:30–16:00. Separate liquidity windows are 03:00–07:00 and 20:00–00:00. ETH does not purge an RTH-only rail in that source branch.

[xfcmg2.pdf, pp.8,40–41; posts 2082205480877781167,1977848592091033789](../../../sources/documents/jumbo/xfcmg2.pdf#page=8) supplies open-relative-to-value context and a London analogy. It does not disclose that London formation clock. The manual p.24 prints “6am–9pm”; this conflicts with its repeated 06:00–09:00 rule.

Other clocks retain separate identities: [DTT Time Based Ranges.txt, L1–507,982–1014](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has 13 fixed windows; [Time based ranges with stats.txt, L48–59,293–401](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has 12 irregular NY windows and distinguishes band occupancy from endpoint hits. [6 to 9 Session and Levels.txt, L255–317](../../../sources/documents/indicators/Pinescript-indicators--main.zip) includes the just-completed range in 60-sample statistics; its v2 is identical. [Pre-market session levels and stats.txt, L6–8,123–184](../../../sources/documents/indicators/Pinescript-indicators--main.zip) separates 06–09 formation from 09–12 outcomes. [Session First Bar Range.txt, L10–11,63–112](../../../sources/documents/indicators/Pinescript-indicators--main.zip) and [Session Opening Bar Range.txt, L12–27,99–125](../../../sources/documents/indicators/Pinescript-indicators--main.zip) form first-15m/first-5m ranges; developing HTF display is not early availability. [Session highs lows and opens.txt, L8–34,238–285,435–685](../../../sources/documents/indicators/Pinescript-indicators--main.zip) adds earlier session and higher-period rails with mixed clock conventions.

## Computability and faithful reconstruction

[Session-fail boxes](session-fail-boxes.md) adds GB-NYAM 09–10, GB-10-11, the last completed 60 minutes, GB-Asia 20–00 (**INFERRED**) and GB-London 02–05 (**INFERRED**) to the same clock grid. Each becomes eligible only after formation ends. GB 9–10 is a completed hour box used after 10:00, not the cash opening range; 09:45 is early. Jumbo 6–9 and Jumbo London TBR/extensions keep their existing identities. OR/IB remains secondary.

NQ/ES minute history supports long samples. Trades and NQ MBP-1 support exact formation extrema and event order on their own shorter samples. Volume/dollar bars need trades. No full book is required.

Keep every published clock immutable in its benchmark identity. Persist formation start/end and known_at. H/L are break/liquidity rails. Internal fractions are distinct objects. Freeze completed ranges; retain developing snapshots with later availability. Preserve source clock and NY-calendar versions separately where they disagree.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **clock-grid-15m**: neighboring starts/ends on a 15-minute grid, within 60 minutes of the published ends. Proposed search bounds must freeze before confirmation. Penalize distance from the source clock; retain it in every report.
- **trade-formed**, **volume-bar-formed**, **dollar-bar-formed**: fixed clock intervals, boundary-split activity bars, comparable realized widths. Thresholds use prior discovery history. Do not invent a daily free-form box.
- **prior-only-60**, **pooled-versus-weekday**, **median/quantile-width**: compare stable estimates with source current-inclusive means. Report every variant, including irregular source clocks.

## Phase 1 outcomes

Eligible sessions; missing formation bars; H/L width; clean-edge state; first/both/neither breaks and order; internal rail revisits; touch, overshoot and time to return. Compare per session, year and day class on matched populations, then show each variant’s full coverage.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q01 fixes event boundaries. Q03 resolves the London formation interval. Do not turn the printed p.24 conflict into a 15-hour benchmark.

## Related

[range break paths](range-break-paths.md), [jumbo day classes](jumbo-day-classes.md), [extension projections](extension-projections.md), [opening range and ib](opening-range-and-ib.md), [session geometry](session-geometry.md)

Review findings: J-TBR-01, J-TBR-10, J-X-03, J-X-13, ZIP-03, ZIP-04, ZIP-12, ZIP-52, ZIP-58, ZIP-59, ZIP-64, ZIP-75. [Review ledger](../REVIEW_LEDGER.md).
