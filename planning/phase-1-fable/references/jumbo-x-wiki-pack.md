# JJumboFX 2026 operating system (wiki ingest)

Read the May–Sep 2026 timeline first. Older manuals and the 66-post xfcmg2 archive still exist as history. If 2026 tweets contradict an old indicator name, keep the 2026 use.

This is not a complete scrape. It is every trading post that showed up paging his timeline from Sep 2026 back through Apr 2026, plus the charts on those posts. Off-topic posts dropped.

Wiki job: patch pages. Do not open a new ticket catalog.

## What he is actually running now

Context, then location, then confirmation.

The 28 Aug 2026 recap is the current frame (2093335135789719861):

- range double-break expectancy split in-value vs in-range
- overnight high / low
- AM vol expected range (EV range)
- then confluence with levels

Charts from Aug–Sep label EVrange and EQ, plus overnight H/L and a right-hand RTH volume profile. That is the stack.

### EV range (missing as its own wiki page)

Expected AM move envelope. Teal upper/lower lines. Sometimes tagged EVrange -60%.

2 Sep 2026 (2095172969035096454): scalps EVrange to EQ. On a big 6-9, long/short the EQ. He ate two losses chasing the high.

Treat EV range as a statistical stretch band, not a P-zone and not 1.33/1.66.
Faithful-ish measurement: pre-open / prior-session vol to expected AM high and low.
Variants: SessionStat 9-12 H/L, RV, GK/YZ, lookback quantiles.
Outcomes: reach, overshoot, reject, time-to-touch, whether the tag sits in prior value.

### When he throws out mean reversion

28 Jul 2026 (2082104746077245851): discard mean reversion and range double breaks when these things align. +138.
Follow-up (2082205480877781167): the aligners are RTH open vs prior-day value/range and vs current 6-9.

10 Jul 2026 (2075602926215561312): open inside prior value/range = mean-reversion morning, fade breakouts, scalp the range.

9 Jul 2026 (2075238880060571966): open outside prior value and prior range, with RVOL above average. He claims about 76% of A-period (9:30-10:00) stays one-way and does not return to OR low, 15y sample. Recompute. Do not store 76% as truth.

Open location is a switch:
- inside prior value/range = fade / EQ / EV mean-revert
- outside both + size/vol = do not run the double-break fade

### Range size (27 Aug 2026, 2093020177696755878)

- Size matters. Balanced vs imbalanced overnight matters.
- Any window 5:00-9:00 behaves like 6-9.
- Small ranges print high double-break %. He calls that skewed, not edge.
- About 45% of premarket ranges single-break in the AM. Breakouts can hold.

8 Jun 2026 (2064008375751311653) still used:
- 1.2% width = double-break rare; combined single-break >74% on his sample; mid retrace about 60%.
- Absorption at mid, taper at lows.
- Footprint filtered to top 35%.

### What he does at the open

27 Jul 2026 (2081737561265893419): done at the open. Single-break through A-period. Range mid was the entry. +124.

21 Jul 2026 (2079574963640512677): adapting to current conditions = 6-9 + OR mid retracements, 50-70 point wins, not chasing continuations.

19 May 2026 (2056797248604815569): he does not really use ORs. Sometimes 5m or 15m as reference. The box on the chart is a time-based range, not an OR. Demote OR/IB as a core object.

28 Jul 2026 (2082134071702860091): sarcastic "random projection level to reverse from". Chart still shows -133% / -166% under the low. Extensions are live.

### Order flow on the 2026 charts

- NinjaTrader, RTH profile, BigTrades bubbles, 6-9 box.
- Bubbles are not absorption. They are BigTrades (2056792694878314750).
- Filter: 100 NQ NY, 75 London. Below 100 NY is noise to him (2056794762049421618).
- 15 May 2026 (2055344660986364371): same ranges, different layers.

### Management leak

1 Sep 2026 (2094806188734951817): thesis reached, still lost. Diabolical BEs. Then flipped long on a pullback. Phase 1 does not model BEs.

## Still alive but not the 2026 headline

- P-zones still get one-liners in Jul-Aug. Formula unpublished. Approximation plus upgrades.
- London TBR and London 1.33-1.66 (Jun 2026).
- SessionStat 9-12 as extremity confluence. Compatible with EV range, not the same object.
- 9:40-9:50 still prints on some days.

## Demote

- Always fade 6-9.
- IB-stat / OR as the main box.
- Premium/discount painted box as a standalone signal.
- Calling BigTrades bubbles absorption.
- Treating small-range double-break percent as edge.

## Karpathy check on Astra wiki

Has index.md, log.md, one file per mechanism, some citations.
Fails: 57 pages is a dump; no ev-range page; PRD tone leaked into wiki; open-location switch weaker than 2026 tweets; OR/IB and AMT pages heavier than current use.
Lint, do not rebuild.

## Allowed edits (one tree only)

1. Add wiki/ev-range-expected-move.md
2. Link it from wiki/index.md under Jumbo, beside SessionStat, not under P-zones
3. Append wiki/log.md with this pack and the tweet IDs above
4. Day-class / range-path pages: open-in-value vs open-outside switch; in-value vs in-range double-break expectancy; 5-9 clock note
5. OR/IB page: secondary 5m/15m reference, not his main box
6. Big-print page: 100 NY / 75 London / not absorption
7. No new tickets. No new QUESTIONS rows.

Stop.
