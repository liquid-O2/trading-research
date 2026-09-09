# Jumbo range and path statistics: NQ 2020–2022 checkpoint

Three complete annual tables and statistical reports were saved during the registered development extraction. The overall attempt was interrupted when measured runtime projected the full cohort above its CPU cap. The run remains interrupted; these are reusable partial results, not full-family completion.

| Year | Formation | Complete / intended dates | Both strict breaches in next 180 minutes | 95% date-block interval |
|---:|---|---:|---:|---|
|2020|JTR 06:00–09:00 NY|239 / 253|42.3%|35.2%–49.0%|
|2020|ONS03 source window|238 / 253|23.5%|18.4%–28.8%|
|2020|Opening 15 minutes|246 / 253|38.6%|32.8%–45.6%|
|2020|09:40–09:50 NY|246 / 253|51.2%|45.4%–57.7%|
|2021|JTR 06:00–09:00 NY|244 / 252|44.3%|38.3%–49.8%|
|2021|ONS03 source window|243 / 252|26.7%|20.7%–32.3%|
|2021|Opening 15 minutes|248 / 252|34.7%|29.4%–40.7%|
|2021|09:40–09:50 NY|248 / 252|50.0%|44.2%–56.5%|
|2022|JTR 06:00–09:00 NY|244 / 251|39.3%|33.6%–45.9%|
|2022|ONS03 source window|244 / 251|25.8%|20.4%–32.0%|
|2022|Opening 15 minutes|247 / 251|38.9%|32.8%–45.5%|
|2022|09:40–09:50 NY|247 / 251|53.0%|47.6%–59.3%|

Each forecast begins when the completed formation is available under the declared minute-bar publication scenario. A strict breach requires a later high above the formation high or a low below the formation low. The two breaches can occur in either order; intraminute order stays ambiguous where OHLC cannot establish it. Missing, invalid and contract-transition windows retain explicit exclusions. The complete JSON reports also retain bounds over the full formed population, including censored outcomes.

Intervals use 1,000 resamples of five consecutive intended cash dates with the frozen seed 20260907. The opening-range both-breach frequency is 35–39% in these three years. The clock rows have different widths and forecast origins, so their raw frequency differences do not select a better clock. Common-cut comparisons and independent Context/Location evaluations remain required.

The linked tables cover every declared source clock and named timing comparison for each completed year, with geometry, causal features, complete/partial paths and source-specific mechanisms. The excerpt uses four clocks chosen before this run. NQ2023–2024, all ES development years and reserved2025 onward confirmation remain outstanding.

| Completed year | Exact table/statistics manifest |
|---|---|
|NQ 2020|[Manifest](NQ-2020-shard.json)|
|NQ 2021|[Manifest](NQ-2021-shard.json)|
|NQ 2022|[Manifest](NQ-2022-shard.json)|

[Registered interruption and exact resource record](interruption-review.json). Five of ten attempts have been consumed, totaling420.642858 of2,400 CPU seconds. No budgets have been reset.
