# Dated source-fit reconstructions

**Later interpretation correction:** the [September 12 coverage audit](../PROFILE_COVERAGE_CHECK.md) records the November 20 short-position line in the high-sweep area. The delayed MSS/FVG entry below is a rejected reconstruction hypothesis, not the author's entry requirement. Further basis, timeframe and entry searches are deferred.

These are our explicit reconstructions of two published examples using acquired NQ data. The source figures were used to choose and calibrate them. There is no held-out validation, automatic historical cohort or demonstrated trading edge here.

## GB VWAP — February 24, 2026

![Source and NQ VWAP reconstruction](/workspace/implementation/reports/phase1-live/methods/reconstructions/GB-VWAP-2026-02-24.png)

The retained figure is Green Bird p.33, post `2026329904690712970`. The data is native NQH6, instrument 42002475, tick 0.25. The common opening selloff, recovery, VWAP pullback and continuation are visible in both charts.

| Reset / price basis | Readable points covered | RMSE (points) | Maximum absolute error |
|---|---:|---:|---:|
| Previous 18:00 / OHLC4 | 13/13 | 1.390 | 2.736 |
| Previous 18:00 / HLC3 | 13/13 | 1.485 | 3.005 |
| Previous 18:00 / native trades | 13/13 | 1.508 | 3.281 |
| Midnight / HLC3 | 13/13 | 3.495 | 5.190 |
| 02:00 / HLC3 | 13/13 | 3.516 | 7.586 |
| 09:30 / HLC3 | 8/13 | 23.416 | 58.195 |

All 16 tested combinations are retained in [the fit grid](vwap-fit-grid.csv). The cash-open fit has a different sample and fails full-figure coverage. HLC3 with an 18:00 New York reset is a plausible working reconstruction, not a verified author setting. OHLC4's small advantage does not identify the basis: one pixel is about 0.76 points, with approximately one bar of clock-alignment uncertainty. Four preselected columns were occluded and excluded by the recorded pixel mask. No favorable points were manually substituted after seeing residuals.

Using Asia 20–00 and any of the tested London windows (02–05, 03–05, 02–08), the completed 09:44 bar first closes above both highs. The first later touch of the prior completed HLC3 VWAP occurs in the 10:00 minute, against 24837.614. The OHLC evidence becomes available at 10:01. That reconstructs the sequence, not an entry fill.

[Case details and source provenance](GB-VWAP-2026-02-24.json) · [Digitized points](vwap-source-points.csv) · [All curves](vwap-curves.csv)

## GB failure — November 20, 2025

![Source and NQ two-minute reconstruction](/workspace/implementation/reports/phase1-live/methods/reconstructions/GB-FAIL-2025-11-20.png)

The raw post is `1991589280142315537` on p.31; the figure is p.43. Its toolbar and instrument header specify **MNQZ2025, two minutes**. Our acquired native instrument is NQZ5, 158704. The source names the later high sweep, failure, MSS/FVG entry and opposing lows. The earlier generic five-minute diagnostic described the first failure and did not reconstruct that intended attempt.

The 09–10 NQ range is [25146.00, 25291.50], available at 10:00. The annotated later high test peaks at 25310.00 in the 10:38 bar. The 10:40 bar closes back below the range high, available at 10:42. A one-left/one-right local-low hypothesis identifies 25267.00 at 10:40, confirmed at 10:44; the first subsequent close below it is available at 10:50. That is our explicit MSS approximation.

| Three-candle bearish FVG | Available at | NQ band | Approximate MNQ figure band |
|---|---|---|---|
| Bar opening 10:48 | 10:50 | 25270.25–25287.00 | 25269.88–25285.54 |
| Bar opening 10:50 | 10:52 | 25238.50–25261.75 | 25237.35–25261.45 |
| Bar opening 10:52 | 10:54 | 25226.00–25228.75 | 25225.30–25227.71 |

The largest boundary difference is about 1.46 points. Pixel uncertainty is roughly 0.60 points per pixel, and NQ/MNQ prices are not identical. Each band is formed by `high[i] < low[i−2]` and begins only after candle `i` closes. All three source bands are closely reproduced.

**The delayed limit-entry hypothesis does not explain the source trade.** After the first gap and the comparison MSS are complete at 10:50, price does not revisit any part of that first gap by 11:02. A midpoint limit therefore receives no touch. The opposing 09–10 low is subsequently crossed in the 11:00 bar. That move is not credited as a filled winning trade. The source's final 11:02 bar is partial at its screenshot clock, so it is excluded from full-bar calculations.

[Case details and source provenance](GB-FAIL-2025-11-20.json) · [Two-minute geometry](fail-two-minute-geometry.csv) · [Gap comparisons](fail-gap-comparisons.csv)

## Process record

Stoic's p.3 process is usable: define the steps, record cases uniformly, compare results, refine. This pass records two calibration cases with their source intent, tested hypotheses, disagreements and unresolved execution fields. The [source-case ledger](source-case-ledger.jsonl) contains zero actual execution records. Its post-publication annotations must not be used as causal historical selection inputs.

Further source comparisons can refine hypotheses under new versions. A historical hypothesis study would first freeze its complete selector, fill model and outcomes, then run on dates not used for calibration. These two examples cannot supply its win rate or the 100+ closed trades required by the source risk discussion.

## PHASE

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---:|---|---|---|
| GB-VWAP | source-fit-v1 | 0 | N/A; research reconstruction | 1 calibration case; close VWAP fit | [Case](GB-VWAP-2026-02-24.json) |
| GB-FAIL | source-fit-v1 | 0 | N/A; research reconstruction | 1 calibration case; geometry close, delayed entry unfilled | [Case](GB-FAIL-2025-11-20.json) |

Here `n` retains the historical method denominator. The 13 source pixels and three gaps are comparison measurements, not 16 trades.

## Audit

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|
| GB-VWAP | M03 | reconstruction only | none used as data | source case used for calibration; no causal selector claimed | 0 | Four resets × four bases; full grid retained; no fill |
| GB-FAIL | M02 | reconstruction only | none used as data | retrospective source window explicit; geometry end-known | 0 | MNQ source versus native NQ; no inferred winning fill |

[Source reread and corrections](../SOURCE_RECHECK.md) · [Manifest](manifest.json) · [Builder](/workspace/implementation/tools/reconstruct_source_cases.py)
