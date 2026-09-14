# Source: the Pine archive (indicators/Pinescript-indicators--main.zip)

**Historical background — scope clarified 2026-09-12.** This retained note predates the current M01–M12 / O001–O166 contracts and is outside empirical v1. Its “faithful object,” upgrade and outcome sections describe earlier proposals; they do not report current implementation acceptance or measured results. Source/Pine constructions and old statistics remain distinct from author rules. See the [current method map](index.md), [status](current-status.md), [source catalog](source-catalog.md) and [historical review ledger](/workspace/planning/phase-1-from-scratch/REVIEW_LEDGER.md).

## Definition
84 files, 51,601 lines, unpacked from `sources/documents/indicators/Pinescript-indicators--main.zip`. Authors: `lucymatos`, `npg` / `notprofessorgreen`, unattributed. Two kinds of content: geometry restatements of Jumbo / session objects (construction references) and **hardcoded statistics tables** typed into the scripts (tier-2 claims with unknown provenance; comparison rows to recompute on F and L, never numbers to store as truth). Every file was read line by line; the full classification of all 84 is in [historical review ledger](/workspace/planning/phase-1-from-scratch/REVIEW_LEDGER.md). `README.md` inside the zip contains only a title. Exactly one byte-identical duplicate pair (`6 to 9 Session and Levels.txt` = `6 to 9 session & levels v2.txt`).

## Citations
What each mechanism-relevant file contributes:
| file | contributes to | anchor |
|---|---|---|
| `6 to 9 Session and Levels.txt` | 6–9 geometry: 25/50/75, ±0.5/1.0/2.0 deviations, 1.33/1.66, prior RTH H/L, 9:40–9:50 zone, 60-session mean/median extension, z-score | [tbr-6-9-range](tbr-6-9-range.md) |
| `AM TBR - NQ Stats.txt` | σ-band (20-day daily % stdev) touch ±0.25σ, reversion to open by 12:00; hardcoded: hour-8 touch 78.4% n=732, hour-9 69.7% n=492, cumulative by 09/10/11/12 = 27.9/68.2/76.1/78.4 | [ev-range-expected-move](ev-range-expected-move.md) |
| `NQ Stats Price Distributions.txt` | 15-year 1-minute study (2010-06-06 → 2025-03-14, 3,804 sessions); sigma per anchor; 75.2% inside ±1 SD; conditional fade 44.8–58.8% flat in k | [ev-range-expected-move](ev-range-expected-move.md), [vol-estimators](vol-estimators.md) |
| `Pre-market session levels and stats.txt`, `session_statmap` | levels 06:00–09:00, stats 09:00–12:00, σ-levels, fibs, per-weekday first-hit counts | [sessionstat-9-12-envelope](sessionstat-9-12-envelope.md) |
| `Session Statistical Levels.txt` | Asia 19–02, London 02–08, NYAM 08–12, NYPM 12–17 percentile bands P10–P90, MFE/MAE | [ev-range-expected-move](ev-range-expected-move.md) |
| `Statistical OHLC Projections HTF.txt`, `Daily statistical range and levels.txt`, `Statmap HTF no like for like lookback.txt`, `Session Based Statmap with closing stats.txt` | manipulation / distribution average, median, percentiles from the open (like-for-like slot filter) | [ev-range-expected-move](ev-range-expected-move.md), [p-zones-benchmark](p-zones-benchmark.md) |
| `Range Projections Statistical Levels.txt`, `Session Range Projections with stats.txt`, `Range Prob.txt` | per-DOW percentile levels; RE×1…6; LUT-string range probabilities from 18:00 | [p-zones-benchmark](p-zones-benchmark.md) |
| `Expected Volatility .txt` | VIX/16 and VIX/√365 log-space bands | [vol-estimators](vol-estimators.md) |
| `NQ Stats RTH Breaks with stats.txt` | open vs prior RTH: above → 84.11% no break of prior low; below → 81.82% no break of prior high; inside → 14.30 / 72.66 / 13.04 | [open-location-switch](open-location-switch.md) |
| `Daily Floor Pivots.txt` (L804–988, L1159–1196) | 2,482-day floor-pivot touch / close / continue / reject / first-touch tables; gap context: open above PDH 20.5%, below PDL 11.3%, within 68.2%; its "GZ" is the daily Golden Zone 0.5–0.618 of the prior day range (L321–330), not a gap | [open-location-switch](open-location-switch.md) (context rows only; pivots not a family) |
| `NY vs Asia Statistical Levels.txt`, `NQ Stats ALN profiler.txt`, `Statistcal Daily Profile & Ranges.txt`, `NQ Statistical Mapper.txt` / `nq_stats_mapper` (L282–369), `NQ Stats all in one.txt`, `Session Range Candles + 25% Level.txt` | London-vs-Asia / NY-vs-London engulfment patterns and first-hit rates (e.g. London opens above Asia mid → Asia high first 73.84% n=1785; NY opens above London mid → London high first 76.68% n=1775; Asia high hit in NY 78.41% if hit in London else 59.69%; Asia low 78.54% / 54.64%) | [clock-grid-and-bars](clock-grid-and-bars.md), [session-fail-boxes](session-fail-boxes.md) |
| `NQ Hourly Retracement Levels.txt` / `hourly_stats_levels` (L279–401) | hit rates of overnight hourly opens / mids during NY 08:00–16:00 (07 mid 94.19 … 00 open 73.67; pattern-conditioned tables; MAE 0.25–0.50%) | [session-fail-boxes](session-fail-boxes.md) (TDO row), [clock-grid-and-bars](clock-grid-and-bars.md) |
| `NQ Hourly Retracements 12y Stats with Levels.txt` (L185–313) | per-NY-hour sweep of prior-hour H/L, both, none; extension percentiles; retrace-to-swept ≈ 90–95% | [session-fail-boxes](session-fail-boxes.md) (GB-hour) |
| `magic_hours` (L55–103) | hour box break → mid target win rates 07:00 82.8 … 23:00 68.5; zones by extension %; time-to-target p25/p50/p75/p90 | [session-fail-boxes](session-fail-boxes.md), [clock-grid-and-bars](clock-grid-and-bars.md) |
| `4H HOD LOD Checkpoint Analysis.txt` (L556–730) | P(HOD / LOD already in) by 4H checkpoint and elimination structure (e.g. 10:00 checkpoint, 0 eliminations: HOD in 68.90% n=582) | column `hod_lod_time` in `../SPEC.md` §7 |
| `4h Candle Curves.txt`, `NQ Stats Noon Curve.txt` | 4H curve vs continuation %, AM/PM likely H/L % | reference only |
| `Initial Balance Statistical Mapping.txt`, `IB ORB Statistical Mapper hardcoded.txt`, `NQ Stats Initial Balance.txt`, `NY 5m and & 15m Orb Statistics & LTF Candle structure.txt` (L141–144, L873–1189), `IB ORB Live Stats.txt`, `Initial Balance & …` (3 files) | IB / ORB break, extension and retest tables (e.g. ORB-5 median extension +0.411% / −0.450%; midpoint retest 81.8–88.4%; the IB file's midpoint retest is a 0.1 %-of-price leave-and-return band, L279–286) | comparison rows `range.or.*`, `range.ib`; expected null per `[XF p.8]`; TPO/AMT labels on [tpo-ib-auction](tpo-ib-auction.md) |
| `Session Raid Stats.txt`, `HTF Sweep Model with CISD Table.txt`, `HTF Sweeps & Liquidity Levels with CISD.txt`, `Sweep, CISD, MTF FVG & Key Levels.txt`, `CISD with fib or range extensions and stats.txt` | sweep / raid / close-back definitions; body vs wick variants | [touch-reject-hold-break-grid](touch-reject-hold-break-grid.md), [sweep-cisd-blocks](sweep-cisd-blocks.md), [fvg-body-gaps](fvg-body-gaps.md) |
| `Sessions & VP with prev session VP & daily weekly opens.txt`, `VP History Widget.txt` | bar-distributed VP construction, 70% VA; 18:00 daily open and Sunday 18:00 weekly open lines | [value-and-profiles](value-and-profiles.md), [session-fail-boxes](session-fail-boxes.md) (NWOG) |
| `Statistical VWAP study Session and RTH VWAP.txt`, `Confluence Suite.txt` (L243–255), `Key levels, MTF swing highs, lows & 4h candle boxes.txt` (L150–164) | session / RTH VWAP bands; OHLC delta proxy; fractal swing definition | [cvd-variants](cvd-variants.md), [smt-divergence](smt-divergence.md) |
| `DTT Time Based Ranges.txt`, `Time based ranges with stats.txt`, `Time based Range Retracement…` (3 files), `Weekly Initial Balance.txt`, `Historical High and Lows … 30min bins.txt`, `Hourly Time Levels.txt`, `Session highs lows and opens.txt`, `Session First Bar Range.txt`, `Session Opening Bar Range.txt`, `Session standard deviations with stats.txt`, `Deviation based reversion with Stats.txt`, `ADR Levels with Stats.txt`, `Daily close stats.txt`, `Daily High Low probability zones.txt`, `MTF OHLC retracement stats.txt`, `HTF Candle Stats by Time of Day.txt`, `MTF HTF market analysis toolkit.txt` | named-session grids and live-computed hit frameworks | grid candidates only; not measured unless listed in [clock-grid-and-bars](clock-grid-and-bars.md) |
| `First presented FVG…` | first-per-clock wick gap | [fvg-body-gaps](fvg-body-gaps.md) |
| `8020 System.txt`, `ATR Breakout.txt`, `Adaptive Volatility Adjusted Momentum Score.txt`, `HMM Enhanced Regime Probability.txt`, `Inside and Outside bar stats.txt`, `Leptokurtic Directional Bias.txt`, `MTF Bollinger Bands Trend Stop.txt`, `MTF OHLC Lines with Breakout & Retracement Labels.txt`, `MTF Swing Highs and Lows.txt`, `Oscillator Suite.txt`, `Pivot Order Blocks.txt`, `Reversal Breakout System…`, `TTM Squeeze Divergence.txt`, `confluence_suite` | generic TA / level drawing | out of scope |

## Faithful object
None. This page is evidence, not an object. Hardcoded tables are quoted as `[PINE file:lines]` comparison rows with status `measured` after recompute; they never seed a parameter.

## Upgrades
None.

## Outcomes
- Each quoted table gets a recompute row on F and L with the same bucket definitions; the absolute cell difference is reported next to the quoted number.

## Links
[index](index.md) · [historical review ledger](/workspace/planning/phase-1-from-scratch/REVIEW_LEDGER.md)
