# P-zones and EVRange: what the printed frames say (2026-09-17)

Status note by the coordinator. Answers two questions the owner asked on 2026-09-17: were these two proprietary JJumboFX objects reverse-engineered in Phase 1.5, and is the EVRange the same object as a P-zone.

## 1. What Phase 1.5 actually did

- P15-04 (`planning/phase-1-5/reconstruction.py`, rows L006–L008) marks the P-zone recipe `not_identifiable` (percentiles, delete-invalidated rule, session end) and task card A03 states "No P-zone/forward-volatility optimizer is added in Phase 1.5". The Phase-1 inferred v1 (`method_pack/strategy_pzones.py`: quantiles .70/.80 of the excursion normalised by the pre-anchor 60-minute range, 500 sessions) was never compared with a printed frame.
- Compared today against the four printed P-zone frames (2025-12-30, 2026-01-02, 2026-01-09, 2026-02-24; `PZONE_FIXTURES` in the rebuilt `jumbo.py`): v1 places its zones 5 to 8 times farther from the anchor than the author's. v1 is disproved and must not be used.
- So: the reverse-engineering was not done in Phase 1.5; it was explicitly excluded there. The rebuilt adapter is honest about it (`timed_pzone_reversal` runs on the printed fixtures only, otherwise `pzone_generator_unknown`).

## 2. What the printed zones are consistent with

Setup: excursion from the anchor price (the last 1-minute close before 09:00) to the session's highs and lows over 09:00→16:00, one value up and one down per prior session, ranked over the prior 250–500 sessions.

| tier | percentile rank of the printed zone (raw points, 09:00 anchor) | zone width |
| --- | --- | --- |
| T1 | 0.12–0.23 | 6–10 points |
| T2 | 0.33–0.45 | 6–10 points |
| T3 | 0.54–0.59 (01-09); 02-24 sits lower on the same rank | 10 points |

- Normalising the excursion by a rolling average range (ATR5/10/20 of the RTH or full-session range) does not tighten the tiers beyond the raw-point ranks (T1 spread 0.11–0.16, T2 0.13–0.21); VXN-near, volume-above-median and same-range-bin conditioning worsen them. A 12:00 window moves every tier up (T1 0.16–0.28, T2 0.41–0.55, T3 0.64–0.72) and fits no better.
- The author anchors the zones by discretion per day: "9am p-zones", "9:30 pzone", "10am pzone", "6pm P-zones" on gold (archive pp.34, 42, 53, 58, 59), and the owner confirms windows of 9–10, 9–12, 6–9 and 10–x. Any fit must therefore take the anchor from the chart, and the scan must offer every anchor the author uses with the day read choosing, as the plays do.
- Not pinned: the exact percentiles, the lookback length, the volume/volatility filter the author names ("distances that are filtered by volume and volatility", archive p.55) and the delete-invalidated rule. Four frames are too few to pin a recipe; more printed frames (the 10:00-anchor zones on 01-02 and 01-09, any further dated charts) are the only way to narrow it.

## 3. EVRange

Two readouts: 2026-08-28 band 29,590–29,724 (width 134); 2026-09-01 band 29,058–29,195 (width 137) with a "+50%" line at 29,290.

| readout | 09:00 price | band mid − 09:00 price | half-width | edge rank in the 09:00→16:00 excursion (N=250–400) | +50% line rank |
| --- | --- | --- | --- | --- | --- |
| 08-28 | 29,659.00 | −2.00 | 67 | 0.23–0.29 (up and down) | — |
| 09-01 | 29,125.75 | +0.75 | 68.5 | 0.23–0.29 (up and down) | 0.52–0.60 of the up-excursion |

- The band is centred on the 09:00 anchor price, the same anchor the P-zones use, on both days (18:00, 09:30, 10:00 and the prior close are all far off).
- Its edges sit at the same percentile rank on both days (about the first quartile of the excursion distribution) and the +50% line sits near the median of the up-excursion. The conventional options expected move (spot × VXN/100 × √t: ±148 for one hour, ±378 for a day) does not reproduce either readout.
- Conclusion: the EVRange is the same object family as the P-zones (a percentile-of-excursion band from the 09:00 anchor), drawn as one symmetric band at a low percentile with a median line instead of tiered zones. This is consistent with the owner's reading. Two readouts cannot pin the exact percentile or lookback; it stays a fixture in the adapter.

## 4. What would pin the recipes

A bounded fitting task, after the JJ/GB replay passes: collect every printed P-zone and EVRange frame (with its anchor label), fit one percentile-of-excursion recipe per anchor over lookback ∈ {250, 400, 500}, score by the fraction of printed zones reproduced within their own width, and report the fit honestly. Until then both objects remain unsupported inputs, admissible as misses only where a printed frame is absent.
