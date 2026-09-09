# Jumbo complete resource check

The consolidated check passed **442 tests**, validated the complete unchanged development extraction and completed the full workload projection. It used **41.656813 CPU seconds**, **1,525,514,240 bytes peak RSS** and **28,878,107 derived bytes**. [The exact resource review](jumbo-check16-complete-resource-review.json) retains the receipt, component totals and all prior-unit attributions. The failed checks remain failed.

The full declared model workload exceeds the currently approved limits:

| Stage/resource | Measured conservative projection | Approved ceiling |
|---|---:|---:|
| Full fit CPU | 8,670.08 seconds | 6,000 seconds |
| Confirmation CPU, including source extraction/reports | 5,355.31 seconds | 3,600 seconds |
| Fit derived output | 403,558,415 bytes | 536,870,912 bytes |
| Confirmation derived output | 590,527,625 bytes | 536,870,912 bytes |
| Peak model memory | 3,809,953,331 bytes | 4,294,967,296 bytes |
| Remaining fit + confirmation CPU | 14,025.39 seconds | 10,526.95 seconds remaining |

All **sixteen attempts** and **1,473.051801 CPU seconds** are retained. Fitting and confirmation have not started. The original 2020–2024 development extraction, separate corrected NQ2024 population, exact annual parity and completed resource units remain reusable.

The projection measures classification and quantile trees at two row counts/iteration caps, continuous reporting separately from categorical calibration, and complete production model storage/restore/prediction. It preserves all **116 targets**, declared alternatives and **1,000 date-block bootstrap replicates**. Fixed reporting overhead is separated from row/date growth. Before the 1.5 uncertainty factor, the main fit terms are 1,315.82 seconds of linear fitting, 1,525.26 of boosted fitting, 1,073.76 of selection reports and 1,274.40 of production tuning/selection prediction. Confirmation includes 2,223.53 seconds of reports and 1,084.23 of predictions. These are measurements scaled to the actual intended workload, not observed full-stage runtimes.

The production path currently evaluates each fused continuous target independently and repeats some shared predictions. Its actual measured cost is included. Avoiding those repetitions is a possible later optimization; no reduced estimate or weakened comparison is assumed here.

This check establishes numerical and resource evidence, not predictive quality. The full fit/confirmation need an explicit resource amendment. The separately declared complete Location-quality study and all other research families remain required.
