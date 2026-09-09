# Auction/flow source check 3: verified measurements and limits

All 235 relevant tests and all **nine acquisition-window measurements across seven registered cohorts** passed. The [execution](auction-flow-runs/18938c03cf632e3be4d56221f1c2c25b9ce33185efe922aac334feccc585856c/execution.json) consumed **267.630915 CPU seconds**, took 312.91 wall seconds, peaked at 1,050,808,320 bytes RSS, and retained 448,041,535 bytes. The [structured review](auction-flow-source-check3-review.json) joins each actual source, physical population, reference comparison and output. This establishes the implemented source/atomic/native/storage path on these windows; it does not complete either research family.

## What the actual source comparisons establish

The NQ 2020-03-16 cash window and the NQ 2021-02-14 flagged hour each occur in a monthly and a shorter acquisition. Both pairs have identical ordered values and multiplicity in all eleven original fields over the compared window. Each physical acquisition was read and measured separately. The result permits an address-preserving alias for that exact population; it does not establish global source supersession or create additional independent dates.

| Source window / acquisition | Selected raw rows | Observed trades | Volume | Unknown-side volume | Gap-flag rows | Pipeline CPU s | Exact measurement/cache MB |
|---|---:|---:|---:|---:|---:|---:|---:|
| NQ stressed_pipeline_cost; 2020-03-16.parquet | 1,484,342 | 155,066 | 200,682 | 287 | 0 | 10.285 | 40.926 |
| NQ stressed_pipeline_cost; 2020-03.parquet | 1,484,342 | 155,066 | 200,682 | 287 | 0 | 10.374 | 41.011 |
| NQ ordinary_pipeline_cost; 2024-03.parquet | 3,667,827 | 156,709 | 217,360 | 0 | 0 | 16.673 | 60.143 |
| ES stressed_pipeline_cost; 2020-03.parquet | 3,450,647 | 411,548 | 987,248 | 4,696 | 0 | 16.036 | 59.983 |
| ES ordinary_pipeline_cost; 2024-03.parquet | 4,271,130 | 151,224 | 509,029 | 0 | 0 | 18.172 | 62.374 |
| NQ previously_observed_gap_flag_case; 2021-02-08.parquet | 16,624 | 2,222 | 3,527 | 116 | 16,623 | 0.943 | 1.455 |
| NQ previously_observed_gap_flag_case; 2021-02.parquet | 16,624 | 2,222 | 3,527 | 116 | 16,623 | 1.183 | 1.455 |
| NQ full_observed_futures_clock_cost; 2024-03.parquet | 4,534,492 | 224,387 | 314,245 | 83 | 74,341 | 27.365 | 87.278 |
| ES full_observed_futures_clock_cost; 2024-03.parquet | 5,574,880 | 224,556 | 715,550 | 76 | 91,327 | 28.604 | 90.507 |

Pipeline CPU includes complete event/native Parquet writing and all-field read-back comparison. Measurement JSON serialization and independent reference work are timed separately in the structured review. Duplicate acquisitions are displayed separately and are not summed as independent market observations.

## Integrity and failure populations

Every retained trade, quote/invalidation and excluded-trade field, and every native cell, passed complete Parquet round-trip comparison. The independently specified literal event reducer also matched native cumulative paths, extrema clocks and order on up to 32,768 original rows per acquisition; only cells whose full observation prefix was available were compared. Integer fields were exact. Floating duration integrals stayed within the declared absolute 1e-6 / relative 1e-12 tolerances; the largest absolute difference was 1.49e-8. This is bounded real-source reference evidence, not an all-cohort eventwise proof.

The four cash cohorts have no gap-flagged rows in their selected windows. The flagged NQ hour retains 2,222 trades and 3,527 volume, including 116 unknown-side volume; its continuous flow and trusted book histories are incomplete. Both full 23-hour windows retain substantial overnight gap flags: 74,341 NQ and 91,327 ES rows. Under the existing conservative recovery rule, neither full window has eligible trusted quote-pressure cells. Later locally reset flow windows can describe their own observed volume, but cannot repair the earlier gap or certify an uninterrupted original anchor. Separately initialized cash-window quote results must not be promoted as continuous-book recovery evidence.

## Resource projection correction and next phase

The original worker projection is retained, but **is not valid for authorizing full extraction**. It divides each entire pipeline and all output by raw rows, selects the maximum from the sparse flagged window, then adds fixed/native-cell work again. Its 1,287,491 CPU-second and 2.30 TB estimates confound distinct workloads. The measured unit costs are useful; that extrapolation is not. No optimization or resource expansion should be based solely on it.

The next consolidated change must carry invalidation, prior standing age and original source order across extraction cuts; construct the complete source-variant schedule; measure lossless cache/storage alternatives; and produce a component-based cost estimate. Full anchor, annual statistics, individual model/calibration and Location workloads still require their own actual cost evidence before scaling.

The two prior failed checks remain counted, bringing this same family to **3 attempts, 343.772452 CPU seconds and 448,510,840 bytes**. Its registered limits are unchanged. The separate exhausted Jumbo study remains subject to its pending same-family amendment. No Jumbo execution occurred in this check.
