# Report preview

The complete report is preserved in [window-measurement-statistics-report.md.gz](window-measurement-statistics-report.md.gz). Use the root restoration script to restore it byte for byte. The excerpt below is for navigation; it is not the complete report.

---

# Auction/flow window, formation and event-timing statistics

Descriptive formation-length, availability-delay, forward-label and scheduled-event timing measurements. This does not complete the auction/flow family, select a source or clock winner, or claim causal news impact.

- family_complete: false
- complete_family_statistics: false
- population_source_windows: 3589
- processed_source_windows: 3589
- unavailable_source_windows: 37
- feature_rows: 4092200
- label_rows: 12276600
- eligible_feature_rows: 3946193
- eligible_joined_rows: 37732905
- censored_feature_rows: 62780
- unassigned_stage_rows: 48
- out_of_primary_year_rows: 6912
- independent_economic_dates: 2436
- reused_partitions: 13
- new_partitions: 0
- selected_partitions: 13
- declared_partitions: 13
- cpu_seconds: 43.049015357
- output_bytes: 697238970

Date means give one weight per economic date. Multiple cuts or overlapping windows on the same date are dependent observations, not extra independent dates. Monthly and weekly acquisitions keep separate primary inference. Sample quantiles below are the equal-weight date-mean distribution; event mean/min/max stay separate.

Price units are raw ticks (0.25 index point). Variance is ticks squared. Cohort fractions are dimensionless. Volume intensity is contracts/second. CVD, OFI and signed flow are contracts. Labels store absolute future prices; displacements are derived from each feature reference. A complete quiet window is no-new-trade = 1 with a null price, not a zero return. Missing coverage stays missing.

True CVD/OFI path range uses high-low, never close extrema. Hard cohort volumes overlap and are not a partition. Standing and pressure metrics use their own eligible masks.

Directional concordance is the paired observed frequency that sign(formation all-CVD close) matches sign(terminal return), only when both signs are nonzero. Zero-past and zero-future are separate denominators from their own validities. This is not model accuracy or predictive gain.

Scheduled event labels are retrospective: known_at is NULL and causal_feature_eligible is false. Dates without an event record are unknown coverage. Events with no eligible receiver or no nearby window remain in the event denominator. Global no-receiver counts an event once if no selected relevant partition had a receiver.

## Source, year and stage coverage

| collection | root | year | stage | intended_dates | groups |
|---|---|---|---|---|---|
| monthly_acquisitions | ES | 2020 | training | 366 | undefined |
| monthly_acquisitions | ES | 2020 | development | 0 | undefined |
| monthly_acquisitions | ES | 2020 | calibration | 0 | undefined |
| monthly_acquisitions | ES | 2020 | confirmation | 0 | undefined |
| monthly_acquisitions | ES | 2020 | unassigned | 0 | undefined |
| monthly_acquisitions | ES | 2021 | training | 0 | undefined |
| monthly_acquisitions | ES | 2021 | development | 0 | undefined |
| monthly_acquisitions | ES | 2021 | calibration | 0 | undefined |
| monthly_acquisitions | ES | 2021 | confirmation | 0 | undefined |
| monthly_acquisitions | ES | 2021 | unassigned | 365 | undefined |
| monthly_acquisitions | ES | 2023 | training | 0 | undefined |
| monthly_acquisitions | ES | 2023 | development | 184 | undefined |
| monthly_acquisitions | ES | 2023 | calibration | 0 | undefined |
| monthly_acquisitions | ES | 2023 | confirmation | 0 | undefined |
| monthly_acquisitions | ES | 2023 | unassigned | 181 | undefined |
| monthly_acquisitions | ES | 2024 | training | 0 | undefined |
| monthly_acquisitions | ES | 2024 | development | 0 | undefined |
| monthly_acquisitions | ES | 2024 | calibration | 91 | undefined |
| monthly_acquisitions | ES | 2024 | confirmation | 153 | undefined |
| monthly_acquisitions | ES | 2024 | unassigned | 122 | undefined |
| monthly_acquisitions | NQ | 2020 | training | 366 | undefined |
| monthly_acquisitions | NQ | 2020 | development | 0 | undefined |
| monthly_acquisitions | NQ | 2020 | calibration | 0 | undefined |
| monthly_acquisitions | NQ | 2020 | confirmation | 0 | undefined |
| monthly_acquisitions | NQ | 2020 | unassigned | 0 | undefined |
| monthly_acquisitions | NQ | 2021 | training | 365 | undefined |
| monthly_acquisitions | NQ | 2021 | development | 0 | undefined |
| monthly_acquisitions | NQ | 2021 | calibration | 0 | undefined |
| monthly_acquisitions | NQ | 2021 | confirmation | 0 | undefined |
| monthly_acquisitions | NQ | 2021 | unassigned | 0 | undefined |
| monthly_acquisitions | NQ | 2022 | training | 365 | undefined |
| monthly_acquisitions | NQ | 2022 | development | 0 | undefined |
| monthly_acquisitions | NQ | 2022 | calibration | 0 | undefined |
| monthly_acquisitions | NQ | 2022 | confirmation | 0 | undefined |
| monthly_acquisitions | NQ | 2022 | unassigned | 0 | undefined |
| monthly_acquisitions | NQ | 2023 | training | 0 | undefined |
| monthly_acquisitions | NQ | 2023 | development | 365 | undefined |
| monthly_acquisitions | NQ | 2023 | calibration | 0 | undefined |
| monthly_acquisitions | NQ | 2023 | confirmation | 0 | undefined |
| monthly_acquisitions | NQ | 2023 | unassigned | 0 | undefined |
| monthly_acquisitions | NQ | 2024 | training | 0 | undefined |
| monthly_acquisitions | NQ | 2024 | development | 0 | undefined |
| monthly_acquisitions | NQ | 2024 | calibration | 366 | undefined |
| monthly_acquisitions | NQ | 2024 | confirmation | 0 | undefined |
| monthly_acquisitions | NQ | 2024 | unassigned | 0 | undefined |
| monthly_acquisitions | NQ | 2025 | training | 0 | undefined |
| monthly_acquisitions | NQ | 2025 | development | 0 | undefined |
| monthly_acquisitions | NQ | 2025 | calibration | 0 | undefined |
| monthly_acquisitions | NQ | 2025 | confirmation | 365 | undefined |
| monthly_acquisitions | NQ | 2025 | unassigned | 0 | undefined |
| monthly_acquisitions | NQ | 2026 | training | 0 | undefined |
| monthly_acquisitions | NQ | 2026 | development | 0 | undefined |
| monthly_acquisitions | NQ | 2026 | calibration | 0 | undefined |
| monthly_acquisitions | NQ | 2026 | confirmation | 246 | undefined |
| monthly_acquisitions | NQ | 2026 | unassigned | 1 | undefined |
| weekly_acquisitions | NQ | 2020 | training | 366 | undefined |
| weekly_acquisitions | NQ | 2020 | development | 0 | undefined |
| weekly_acquisitions | NQ | 2020 | calibration | 0 | undefined |
| weekly_acquisitions | NQ | 2020 | confirmation | 0 | undefined |
| weekly_acquisitions | NQ | 2020 | unassigned | 0 | undefined |
| weekly_acquisitions | NQ | 2021 | training | 365 | undefined |
| weekly_acquisitions | NQ | 2021 | development | 0 | undefined |
| weekly_acquisitions | NQ | 2021 | calibration | 0 | undefined |
| weekly_acquisitions | NQ | 2021 | confirmation | 0 | undefined |
| weekly_acquisitions | NQ | 2021 | unassigned | 0 | undefined |

## Event coverage

- source_event_rows: 4755
- unique_semantic_events: 925
- events_with_receiver: 698
- events_without_receiver: 227
- events_without_window: 4
- date_only_events: 220
- unknown_event_coverage_dates: 3364
- inconsistent_event_clock_rows: 2

## Representative feature measurements

| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| feature | ES | 2020 | training | cash_rth | 15 | undefined | undefined | undefined | undefined | undefined | formationvolume_per_second | contracts_per_second | 47.86668731621112 | 48.70874335181591 | 231 | 17674 | 135 | [43.32951919816381, 53.15149210869917] |
| feature | ES | 2020 | training | cash_rth | 15 | undefined | undefined | undefined | undefined | undefined | unknown_volume_fraction | dimensionless | 0.0001589962615748999 | 0.00011405531772624006 | 231 | 17674 | 135 | [1.574363505841915e-05, 0.00035995385649206275] |
| feature | ES | 2020 | training | cash_rth | 15 | undefined | undefined | undefined | undefined | undefined | formation_price_range_ticks | quarter_point_ticks | 40.832508761080184 | 39.65259703519294 | 231 | 17674 | 135 | [34.77167623372873, 48.375560101248105] |
| feature | ES | 2020 | training | cash_rth | 15 | undefined | undefined | undefined | undefined | undefined | VWAP_variance_ticks_squared | ticks_squared | 180.68182362947766 | 174.07960929059064 | 231 | 17674 | 135 | [119.71081180861422, 258.4365603127958] |
| feature | ES | 2020 | training | cash_rth | 15 | undefined | undefined | undefined | undefined | undefined | OFI_path_range_on_pressureeligible | contracts | 5732.134012922287 | 5775.471223969774 | 148 | 11381 | 218 | [5260.16560045016, 6157.221594807271] |
| feature | ES | 2020 | training | cash_rth | 15 | undefined | undefined | undefined | undefined | undefined | ny_ge100_volume_fraction | dimensionless | 0.05375714298562944 | 0.05477303731089276 | 231 | 17674 | 135 | [0.04296442931893973, 0.0641247742746551] |
| feature | ES | 2020 | training | cash_rth | 15 | undefined | undefined | undefined | undefined | undefined | ny_ge100_true_CVD_path_range | contracts | 851.859299430728 | 868.0688016295122 | 231 | 17674 | 135 | [725.8829542184728, 974.7535313800051] |
| feature | ES | 2020 | training | cash_rth | 240 | undefined | undefined | undefined | undefined | undefined | formationvolume_per_second | contracts_per_second | 38.520953655031036 | 39.23755568443288 | 231 | 17674 | 135 | [34.776717477860934, 42.70089062851499] |
| feature | ES | 2020 | training | cash_rth | 240 | undefined | undefined | undefined | undefined | undefined | unknown_volume_fraction | dimensionless | 0.000226218667763201 | 0.0002151074564857379 | 231 | 17674 | 135 | [2.0831946263542547e-05, 0.0005183377687900782] |
| feature | ES | 2020 | training | cash_rth | 240 | undefined | undefined | undefined | undefined | undefined | formation_price_range_ticks | quarter_point_ticks | 148.96749282463568 | 148.3345026592735 | 231 | 17674 | 135 | [128.1390650056549, 175.66763925046786] |
| feature | ES | 2020 | training | cash_rth | 240 | undefined | undefined | undefined | undefined | undefined | VWAP_variance_ticks_squared | ticks_squared | 2040.0035097003488 | 2027.4683121561652 | 231 | 17674 | 135 | [1438.308038433452, 2864.9416982106345] |
| feature | ES | 2020 | training | cash_rth | 240 | undefined | undefined | undefined | undefined | undefined | OFI_path_range_on_pressureeligible | contracts | 24995.57920198764 | 25261.058683511856 | 147 | 10923 | 219 | [22516.772036747858, 27774.06056181745] |
| feature | ES | 2020 | training | cash_rth | 240 | undefined | undefined | undefined | undefined | undefined | ny_ge100_volume_fraction | dimensionless | 0.047874906882372954 | 0.048688916604348174 | 231 | 17674 | 135 | [0.03872048211300056, 0.05674119584667281] |
| feature | ES | 2020 | training | cash_rth | 240 | undefined | undefined | undefined | undefined | undefined | ny_ge100_true_CVD_path_range | contracts | 4329.064459350174 | 4411.5578816340385 | 231 | 17674 | 135 | [3708.7610205339533, 4923.48045653571] |
| feature | ES | 2020 | training | cash_rth | 5 | undefined | undefined | undefined | undefined | undefined | formationvolume_per_second | contracts_per_second | 48.9844339522911 | 49.80571875825148 | 231 | 17674 | 135 | [44.391524835340626, 54.3622230095907] |
| feature | ES | 2020 | training | cash_rth | 5 | undefined | undefined | undefined | undefined | undefined | unknown_volume_fraction | dimensionless | 0.00010909801735237601 | 5.033061646971004e-05 | 231 | 17661 | 135 | [7.516423882842678e-06, 0.0002689959018336421] |
| feature | ES | 2020 | training | cash_rth | 5 | undefined | undefined | undefined | undefined | undefined | formation_price_range_ticks | quarter_point_ticks | 24.388710242442297 | 23.23050789875998 | 231 | 17661 | 135 | [20.717592783783353, 29.050273097516513] |
| feature | ES | 2020 | training | cash_rth | 5 | undefined | undefined | undefined | undefined | undefined | VWAP_variance_ticks_squared | ticks_squared | 68.8349338442105 | 60.77503349508824 | 231 | 17661 | 135 | [44.761499711697596, 99.39731975113982] |
| feature | ES | 2020 | training | cash_rth | 5 | undefined | undefined | undefined | undefined | undefined | OFI_path_range_on_pressureeligible | contracts | 3194.204617062719 | 3215.7604596088063 | 148 | 11401 | 218 | [2920.303141847682, 3425.5422606749976] |
| feature | ES | 2020 | training | cash_rth | 5 | undefined | undefined | undefined | undefined | undefined | ny_ge100_volume_fraction | dimensionless | 0.05110879292859434 | 0.05210509310493922 | 231 | 17661 | 135 | [0.040529726338514996, 0.0613396516694561] |
| feature | ES | 2020 | training | cash_rth | 5 | undefined | undefined | undefined | undefined | undefined | ny_ge100_true_CVD_path_range | contracts | 393.2397919540777 | 400.74685979404774 | 231 | 17674 | 135 | [330.36115825409536, 453.6215392091954] |
| feature | ES | 2020 | training | cash_rth | 60 | undefined | undefined | undefined | undefined | undefined | formationvolume_per_second | contracts_per_second | 45.33635210688783 | 46.159106943029826 | 231 | 17674 | 135 | [41.01220903966594, 50.30938384163661] |
| feature | ES | 2020 | training | cash_rth | 60 | undefined | undefined | undefined | undefined | undefined | unknown_volume_fraction | dimensionless | 0.00018209076903440168 | 0.00015765855508079914 | 231 | 17674 | 135 | [2.6599459496728766e-05, 0.0004139125669742042] |
| feature | ES | 2020 | training | cash_rth | 60 | undefined | undefined | undefined | undefined | undefined | formation_price_range_ticks | quarter_point_ticks | 78.4622520336806 | 77.85815321941836 | 231 | 17674 | 135 | [67.37989343751147, 92.98544044815397] |
| feature | ES | 2020 | training | cash_rth | 60 | undefined | undefined | undefined | undefined | undefined | VWAP_variance_ticks_squared | ticks_squared | 622.2464349047839 | 623.7841120738647 | 231 | 17674 | 135 | [420.0459822893645, 884.639231523395] |

[Download the complete report](window-measurement-statistics-report.md.gz).
