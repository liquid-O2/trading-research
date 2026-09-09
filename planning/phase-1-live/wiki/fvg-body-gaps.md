# FVG and body gaps

Not a Green Bird object. Do not add this family to [session-fail-boxes](session-fail-boxes.md).

## Definition
A **wick gap / FVG** is a three-bar imbalance: bar 1 and bar 3 wicks do not overlap. A **body gap** is a gap between consecutive bodies (source “volume imbalance” that does not use volume). **First-presented FVG** is the first such wick gap per clock. Geometric gaps do not prove zero traded volume `[TBR p.32–35]` `[PINE First presented FVG (with stats) with statistical hourly ranges & bias.txt:81–85,148–170]`.

## Citations
- Jumbo manual retains first-presented FVG and H1/M15 imbalances `[TBR p.32–35]`.
- First three-bar wick gap per hour on 1/3/5/15m; W1 code includes all 09 hour despite a 09:30–10 label; hardcoded effectiveness rates are claims to recompute `[PINE First presented FVG…:254–304,342–353]`.
- Outer-wick gaps and adjacent body gaps called “volume imbalance” without volume; shared-edge dedup bugs `[PINE Sweep, CISD, MTF FVG & Key Levels.txt:551–638,985–999]`.
- Consecutive-body gap ≥ 4 ticks and near-edge fill `[PINE 8020 System.txt]`.

## Faithful object
`gap.fvg.first.clock`: first three-bar wick gap per ET hour on 1-minute NQ OHLC, known at the close of bar 3. Bounds = [max(bar1.low, bar3.low), min(bar1.high, bar3.high)] inverted for bear/bull as the source geometry. `gap.body.adjacent`: body-to-body gap on consecutive completed minutes.

## Upgrades
- Clocks: hourly (faithful), 6–9 only, RTH only, 5m/15m HTF.
- Wick vs body vs trade-volume-empty (last is a comparison: bins with zero trades inside the geometric gap).
- Shared-edge independent IDs vs source dedup.
- Size: native ticks vs vol-scaled.
- First-per-clock vs all gaps.

## Outcomes
Formation coverage; first touch; near-edge / partial / far-edge fill; reject vs accept; time to fill; no-FVG sessions; invalidation. Shared grid. Confirmation of the third bar precedes every counted outcome.

## Links
[sweep-cisd-blocks](sweep-cisd-blocks.md) · [tbr-6-9-range](tbr-6-9-range.md) · [touch-reject-hold-break-grid](touch-reject-hold-break-grid.md)
