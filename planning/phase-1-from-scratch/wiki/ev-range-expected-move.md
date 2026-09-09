# EV range: expected AM move

Family: **Jumbo**. EV range is a statistical AM stretch envelope with its own identity. Keep it separate from P-zones, 1.33/1.66 range extensions and SessionStat.

## Evidence and source rules

The supplied `jumbo-x-wiki-pack.md` adds the May–September 2026 usage context; it is a partial timeline. On [28 August](https://x.com/JJumboFX/status/2093335135789719861), Jumbo combines in-value/in-range double-break expectancy, overnight H/L and an AM volatility expected range, then context → location → confirmation. On [2 September](https://x.com/JJumboFX/status/2095172969035096454), he describes EVrange-to-EQ scalps and working the EQ of a large 6–9 range, including losing attempts at the highs.

These posts establish use, not the envelope's numerical construction. The pack's SessionStat, RV, GK/YZ and quantile recipes are proposed reconstructions. Neither a chart label nor an envelope touch establishes a reversal or trading edge.

## Computability and disclosed variants

Minute OHLC supports historical AM excursions and prior-session volatility. Trades resolve ordered contacts on their available sample. Freeze bounds at their stated creation time; the outcome session cannot enter its own historical estimate.

The disclosed benchmark is `ev-am-mean-60`: a 09:00 NY anchor plus/minus the mean upper/lower excursions of the last 60 completed 09:00–12:00 sessions. Compare separately named median/75th/90th-percentile envelopes and prior-session RV/GK/YZ scaling. This uses a SessionStat-style historical H/L construction as an approximation; it does not establish that EV range is SessionStat. Exact formulas and matching columns are in [SPEC](../SPEC.md#ev-range-and-open-location-switch).

Keep the envelope midpoint and the completed 6–9 EQ as separate target IDs. This prevents the September example from silently supplying an unpublished anchor formula. All variants use the existing common G1–G3 reaction grid; no source decoding or new question is required.

## Outcomes and open location

Count upper/lower/both/neither reach, time to first touch, overshoot, rejection, hold/break, ordered return to each EQ target, nonreturn and censoring. Retain tag position inside/on/outside prior value and range, width and starting distance. Compare full populations and matched open-location cells, with support and yearly stability.

The [open-location switch](jumbo-day-classes.md#2026-open-location-switch) is a descriptive conditioning object: inside prior value/range favors the source's mean-reversion hypothesis; outside both with aligned range/volume evidence favors its continuation hypothesis. Measure both outcomes in every cell rather than treating either hypothesis as a guaranteed direction. The [range-path page](range-break-paths.md#2026-conditional-break-expectancy) preserves the distinct denominators.

## Related

[SessionStat envelopes](sessionstat-envelopes.md) · [Time-based ranges](time-based-ranges.md) · [Timed retracements](timed-retracements.md) · [Ticket 51](../tickets/51-ev-range-and-open-location-switch.md)
