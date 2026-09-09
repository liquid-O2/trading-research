# Cross-session containment, balance and open position

Family: **day-type**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[xfcmg2.pdf, pp.7,10–12,17–18](../../../sources/documents/jumbo/xfcmg2.pdf#page=7) relates single/double breaks to overnight geometry and next open versus prior value. [NQ Statistical Mapper.txt, L201–369](../../../sources/documents/indicators/Pinescript-indicators--main.zip) and identical nq_stats_mapper define Asia20–02/London02–08/NY08–16 NY, London open versus Asia midpoint, NY open versus London midpoint, and four containment/partial-overlap classes. [NQ Hourly Retracement Levels.txt, L126–216,279–401](../../../sources/documents/indicators/Pinescript-indicators--main.zip) adds hourly opens/mids and hardcoded visits; hourly_stats_levels is its shorter prefix. [NQ Stats ALN profiler.txt, L55–82,178–209](../../../sources/documents/indicators/Pinescript-indicators--main.zip) omits first-bar volume and labels mean bar range “ATR”.

[NQ Stats all in one.txt, L578–701](../../../sources/documents/indicators/Pinescript-indicators--main.zip) joins by array position and uses a session’s later high as an opening proxy. That is noncausal. [NY vs Asia Statistical Levels.txt, L111–194,275–435](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses Asia19–02 and four NY-open buckets; whole-session high-minus-low is not an ordered reversal. [Session Range Candles + 25% Level.txt, L483–486,802–953](../../../sources/documents/indicators/Pinescript-indicators--main.zip) defines a body rail O+.75(C−O), distinct from a range quartile. [Statistcal Daily Profile & Ranges.txt, L260–275,390–480](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses strict containment with equality outside its four classes.

## Computability and faithful reconstruction

OHLC permits long samples. Trade flow/VP conditions have their own overlaps. Calendar joins use session identity, never positional arrays or later-session proxies.

Retain each source clock, geometry equality convention, body/range midpoint and conditional population. Store full four-way geometry plus equality/partial/unavailable states. Capture next open before its later high/low is observed. Treat published lookup rates as claims with unknown training dates.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **NY-calendar/date-joined** with exact opens and full first-bar participation.
- **range-quartile versus body-quartile**.
- **08-open versus 09:30-open**, **prior-value**, **width/volatility-normalized geometry**, and fixed-grid/trade/activity-bar formation variants.
- **ordered-extension-return** replaces whole-session range subtraction only as a named experimental event.

## Phase 1 outcomes

Joint and conditional edge visits; first/next break order; hourly-rail visits; body-rail touch and close-back; open/range/volume distributions. Show all cells and n, including unclassified equality and no-touch sessions.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Use Q01–Q03. Source-specific clocks are computable as written; choosing a single intended London benchmark remains blocked.

## Related

[time based ranges](time-based-ranges.md), [range break paths](range-break-paths.md), [timed retracements](timed-retracements.md), [value profiles](value-profiles.md)

Review findings: J-X-02, J-X-04, J-X-06, ZIP-39, ZIP-41, ZIP-42, ZIP-47, ZIP-49, ZIP-61, ZIP-67, ZIP-80, ZIP-82. [Review ledger](../REVIEW_LEDGER.md).
