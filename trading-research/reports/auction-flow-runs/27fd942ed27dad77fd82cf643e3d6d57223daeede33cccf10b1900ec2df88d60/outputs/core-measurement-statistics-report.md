# Auction/flow core measurement statistics

Descriptive pilot core measurements. Source collections pool only nonoverlapping physical windows; acquisition alternatives stay separate. This does not complete the auction/flow family, adaptive cohorts, anchor geometry, causal structure, or Context/Location.

- complete_family_statistics: false
- population_source_windows: 3589
- processed_source_windows: 458
- processed_observations: 648000
- independent_economic_dates: 458
- no_instrument_source_windows: 8
- cpu_seconds: 552.3696292879999
- output_bytes: 8230850
- cash_calendar: {'kind': 'cash_rth_calendar', 'path': '/workspace/trading-research/configs/cash-rth-calendar-research-v1.json', 'sha256': 'f069df0ccbb8318f1c675a05d9deed64ad681ebe1e47dd8573a6b18266665818', 'size_bytes': 6922}

## Completeness

- archive_window_complete observations: 640478
- source_coverage_complete observations: 629079
- flow_history_complete observations: 629079
- price_history_complete observations: 623493
- quote_coverage_complete observations: 629079
- coordinate_complete observations: 631553
- calendar_state_counts: {'regular': 455160, 'closed': 189960, 'early_close': 2880}

True zero complete flow is retained. Missing or partial coverage is excluded, not replaced with zero.

## True OHLC versus close-only

| source collection | root | year | stage | session | cohort | loss date-mean | close date-mean | dates | obs |
|---|---|---|---|---|---|---|---|---|---|
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | all | 142.7520512820513 | 234.5874358974359 | 20 | 7800 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | ny_ge100 | 10.576153846153847 | 46.33923076923078 | 20 | 7800 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | london_ge75 | 18.206153846153846 | 70.13128205128206 | 20 | 7800 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | inclusive30_through60 | 42.235 | 79.89089743589743 | 20 | 7800 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | ofi | 658.5461538461539 | 731.5487179487179 | 1 | 390 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | all | 13.795008367077212 | 28.18256937082389 | 30 | 25709 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | ny_ge100 | 0.4831456220851214 | 5.738104392323793 | 30 | 25709 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | london_ge75 | 0.8171913322087175 | 6.900635996929461 | 30 | 25709 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | inclusive30_through60 | 1.5787984022493757 | 7.0558123494493445 | 30 | 25709 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | ofi | 42.007881316643484 | 46.89151599443672 | 3 | 3059 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | all | 0.0 | 0.0 | 29 | 1740 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | ny_ge100 | 0.0 | 0.0 | 29 | 1740 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | london_ge75 | 0.0 | 0.0 | 29 | 1740 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | inclusive30_through60 | 0.0 | 0.0 | 29 | 1740 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | ofi | 0.0 | 0.005555555555555556 | 3 | 180 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | all | 28.776683087027916 | 49.76535303776683 | 29 | 6090 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | ny_ge100 | 0.09211822660098523 | 2.5614121510673233 | 29 | 6090 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | london_ge75 | 0.29014778325123153 | 4.344827586206897 | 29 | 6090 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | inclusive30_through60 | 4.354187192118226 | 16.74646962233169 | 29 | 6090 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | ofi | 61.542857142857144 | 78.31587301587301 | 3 | 630 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | all | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | ny_ge100 | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | london_ge75 | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | inclusive30_through60 | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | ofi | None | None | 0 | 0 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | all | 48.90069930069931 | 84.05804195804195 | 22 | 8580 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | ny_ge100 | 0.0 | 0.38846153846153847 | 22 | 8580 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | london_ge75 | 0.0 | 0.8265734265734266 | 22 | 8580 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | inclusive30_through60 | 0.14090909090909093 | 2.918414918414918 | 22 | 8580 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | ofi | 137.367313690378 | 157.61208632146767 | 21 | 8118 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | all | 11.327313079077785 | 17.825925447101916 | 30 | 24359 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.16525641025641027 | 30 | 24359 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | london_ge75 | 0.0 | 0.30183760683760685 | 30 | 24359 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.01299145299145299 | 0.4958974358974359 | 30 | 24359 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ofi | 34.20788795355481 | 48.193345417254555 | 29 | 23735 |
| monthly_acquisitions | NQ | 2020 | training | off_session | all | 0.0 | 0.0 | 28 | 1680 |
| monthly_acquisitions | NQ | 2020 | training | off_session | ny_ge100 | 0.0 | 0.0 | 28 | 1680 |
| monthly_acquisitions | NQ | 2020 | training | off_session | london_ge75 | 0.0 | 0.0 | 28 | 1680 |
| monthly_acquisitions | NQ | 2020 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 28 | 1680 |
| monthly_acquisitions | NQ | 2020 | training | off_session | ofi | 0.017479754226094154 | 0.1250311248216201 | 27 | 1518 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | all | 14.923809523809524 | 23.22210884353742 | 28 | 5880 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | ny_ge100 | 0.0 | 0.3916666666666667 | 28 | 5880 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | london_ge75 | 0.0 | 0.5918367346938777 | 28 | 5880 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | inclusive30_through60 | 0.04319727891156462 | 0.83656462585034 | 28 | 5880 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | ofi | 37.547717562634816 | 54.73330026898189 | 28 | 5853 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | all | 47.412454212454215 | 83.24395604395603 | 21 | 8190 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | ny_ge100 | 0.0 | 0.10085470085470086 | 21 | 8190 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | london_ge75 | 0.0 | 0.1796092796092796 | 21 | 8190 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | inclusive30_through60 | 0.11245421245421243 | 2.2427350427350428 | 21 | 8190 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | ofi | 196.19871794871796 | 212.75 | 2 | 780 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | all | 5.83897975029995 | 10.205906273531324 | 29 | 24389 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.005349248452696729 | 29 | 24389 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | london_ge75 | 0.0 | 0.005349248452696729 | 29 | 24389 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.006852343059239611 | 0.12268581883588357 | 29 | 24389 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | ofi | 21.08697449210053 | 23.21683812383838 | 4 | 3838 |
| monthly_acquisitions | NQ | 2022 | training | off_session | all | 0.0 | 0.0 | 27 | 1620 |
| monthly_acquisitions | NQ | 2022 | training | off_session | ny_ge100 | 0.0 | 0.0 | 27 | 1620 |
| monthly_acquisitions | NQ | 2022 | training | off_session | london_ge75 | 0.0 | 0.0 | 27 | 1620 |
| monthly_acquisitions | NQ | 2022 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 27 | 1620 |
| monthly_acquisitions | NQ | 2022 | training | off_session | ofi | 0.0 | 0.01818181818181818 | 4 | 235 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | all | 13.010374149659865 | 22.977040816326525 | 28 | 5880 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | ny_ge100 | 0.0 | 0.0 | 28 | 5880 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | london_ge75 | 0.0 | 0.029761904761904764 | 28 | 5880 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | inclusive30_through60 | 0.0039115646258503405 | 0.2780612244897959 | 28 | 5880 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | ofi | 41.34588174982912 | 43.96948621553885 | 4 | 839 |
| monthly_acquisitions | NQ | 2023 | development | cash_rth | all | 61.72126886446886 | 116.66864322344321 | 250 | 97140 |
| monthly_acquisitions | NQ | 2023 | development | cash_rth | ny_ge100 | 0.0 | 1.076020512820513 | 250 | 97140 |
| monthly_acquisitions | NQ | 2023 | development | cash_rth | london_ge75 | 0.006758974358974358 | 1.6074080586080586 | 250 | 97140 |
| monthly_acquisitions | NQ | 2023 | development | cash_rth | inclusive30_through60 | 0.2615179487179487 | 4.662435164835165 | 250 | 97140 |
| monthly_acquisitions | NQ | 2023 | development | cash_rth | ofi | 206.41658908420777 | 223.36422900881175 | 246 | 95577 |
| monthly_acquisitions | NQ | 2023 | development | futures_wallclock_18_17 | all | 7.443017538882319 | 13.609217158877557 | 351 | 309254 |
| monthly_acquisitions | NQ | 2023 | development | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.03880240135829198 | 351 | 309254 |
| monthly_acquisitions | NQ | 2023 | development | futures_wallclock_18_17 | london_ge75 | 0.0002775951493900212 | 0.07632162428717809 | 351 | 309254 |
| monthly_acquisitions | NQ | 2023 | development | futures_wallclock_18_17 | inclusive30_through60 | 0.006308726294224943 | 0.2753622601128396 | 351 | 309254 |
| monthly_acquisitions | NQ | 2023 | development | futures_wallclock_18_17 | ofi | 27.717072061183803 | 33.00889975981788 | 344 | 304328 |
| monthly_acquisitions | NQ | 2023 | development | off_session | all | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2023 | development | off_session | ny_ge100 | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2023 | development | off_session | london_ge75 | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2023 | development | off_session | inclusive30_through60 | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2023 | development | off_session | ofi | 0.014050411772741942 | 0.08898584898881415 | 335 | 18721 |
| monthly_acquisitions | NQ | 2023 | development | pre_rth | all | 15.272114724852475 | 26.601056676272812 | 347 | 72870 |
| monthly_acquisitions | NQ | 2023 | development | pre_rth | ny_ge100 | 0.0 | 0.14717990942774803 | 347 | 72870 |
| monthly_acquisitions | NQ | 2023 | development | pre_rth | london_ge75 | 0.0023191985728008785 | 0.2521751063537807 | 347 | 72870 |
| monthly_acquisitions | NQ | 2023 | development | pre_rth | inclusive30_through60 | 0.02043364896390833 | 0.6434335117332235 | 347 | 72870 |
| monthly_acquisitions | NQ | 2023 | development | pre_rth | ofi | 48.99174819978063 | 56.762359718005364 | 344 | 72235 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | all | 16.224615384615387 | 31.557948717948722 | 5 | 1950 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | ny_ge100 | 0.0 | 0.0 | 5 | 1950 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | london_ge75 | 0.0 | 0.08256410256410256 | 5 | 1950 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | inclusive30_through60 | 0.0 | 0.2246153846153846 | 5 | 1950 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | ofi | 98.53751045476906 | 122.76647328808816 | 4 | 1525 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | all | 3.31978709074385 | 8.565299099679558 | 7 | 4018 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 1.9271847200418628 | 7 | 4018 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | london_ge75 | 0.0 | 2.0862128906657795 | 7 | 4018 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.0 | 0.4374196439402188 | 7 | 4018 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ofi | 18.860388731227324 | 40.402279342550514 | 5 | 3673 |
| weekly_acquisitions | NQ | 2020 | training | off_session | all | 0.0 | 0.0 | 5 | 300 |
| weekly_acquisitions | NQ | 2020 | training | off_session | ny_ge100 | 0.0 | 0.0 | 5 | 300 |
| weekly_acquisitions | NQ | 2020 | training | off_session | london_ge75 | 0.0 | 0.0 | 5 | 300 |
| weekly_acquisitions | NQ | 2020 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 5 | 300 |
| weekly_acquisitions | NQ | 2020 | training | off_session | ofi | 0.04255952380952381 | 0.1787681598062954 | 4 | 235 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | all | 3.9361904761904762 | 6.935238095238096 | 5 | 1050 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | ny_ge100 | 0.0 | 0.0 | 5 | 1050 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | london_ge75 | 0.0 | 0.0 | 5 | 1050 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | inclusive30_through60 | 0.0 | 0.07523809523809524 | 5 | 1050 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | ofi | 19.19560975609756 | 31.733612078977927 | 5 | 1040 |

## Source aliases and disagreement

- alias groups: 3170
- matched equal measurements: 6570
- matched different measurements: 0
- mismatched contracts not joined: 0
- incompatible coordinates: 4140
- no source winner is selected from these descriptive counts.

## Groups

- root/source/year/stage/session groups: 5

Overlapping hard cohorts are occupancy fractions, not a partition. OFI analogs use only full pressure-eligible windows; the observed OFI subset is separate. Futures 18:00-17:00 is an observed wall clock, not a certified venue calendar.

