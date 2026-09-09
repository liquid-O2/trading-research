# Auction/flow core measurement statistics

Descriptive full core measurements. Source collections pool only nonoverlapping physical windows; acquisition alternatives stay separate. This does not complete the auction/flow family, adaptive cohorts, anchor geometry, causal structure, or Context/Location.

- complete_family_statistics: false
- population_source_windows: 3589
- processed_source_windows: 3589
- processed_observations: 5115250
- independent_economic_dates: 2436
- no_instrument_source_windows: 37
- cpu_seconds: 27.769014165
- output_bytes: 22649699
- cash_calendar: {'kind': 'cash_rth_calendar', 'path': '/workspace/trading-research/configs/cash-rth-calendar-research-v1.json', 'sha256': 'f069df0ccbb8318f1c675a05d9deed64ad681ebe1e47dd8573a6b18266665818', 'size_bytes': 6922}

## Completeness

- archive_window_complete observations: 5058951
- source_coverage_complete observations: 4983629
- flow_history_complete observations: 4983629
- price_history_complete observations: 4957678
- quote_coverage_complete observations: 4983629
- coordinate_complete observations: 5037092
- calendar_state_counts: {'closed': 1522080, 'early_close': 25920, 'regular': 3567250}

True zero complete flow is retained. Missing or partial coverage is excluded, not replaced with zero.

## True OHLC versus close-only

| source collection | root | year | stage | session | cohort | loss date-mean | close date-mean | dates | obs |
|---|---|---|---|---|---|---|---|---|---|
| monthly_acquisitions | ES | 2020 | training | cash_rth | all | 197.4515230800945 | 327.3443001443001 | 231 | 89910 |
| monthly_acquisitions | ES | 2020 | training | cash_rth | ny_ge100 | 26.206290534861967 | 93.28539397110826 | 231 | 89910 |
| monthly_acquisitions | ES | 2020 | training | cash_rth | london_ge75 | 41.85568558425702 | 124.58485799914371 | 231 | 89910 |
| monthly_acquisitions | ES | 2020 | training | cash_rth | inclusive30_through60 | 62.092431378145655 | 108.07945229373802 | 231 | 89910 |
| monthly_acquisitions | ES | 2020 | training | cash_rth | ofi | 605.9800390789566 | 728.5689670215642 | 147 | 57076 |
| monthly_acquisitions | ES | 2020 | training | futures_wallclock_18_17 | all | 24.938855465041772 | 45.49495581897727 | 324 | 281016 |
| monthly_acquisitions | ES | 2020 | training | futures_wallclock_18_17 | ny_ge100 | 0.9948115831735346 | 4.231895787200954 | 324 | 281016 |
| monthly_acquisitions | ES | 2020 | training | futures_wallclock_18_17 | london_ge75 | 1.5033513904840239 | 6.332672523564642 | 324 | 281016 |
| monthly_acquisitions | ES | 2020 | training | futures_wallclock_18_17 | inclusive30_through60 | 3.0654333554615345 | 11.292161735866863 | 324 | 281016 |
| monthly_acquisitions | ES | 2020 | training | futures_wallclock_18_17 | ofi | 77.40996551254486 | 99.74217425299213 | 212 | 185610 |
| monthly_acquisitions | ES | 2020 | training | off_session | all | 0.0 | 0.0 | 315 | 18889 |
| monthly_acquisitions | ES | 2020 | training | off_session | ny_ge100 | 0.0 | 0.0 | 315 | 18889 |
| monthly_acquisitions | ES | 2020 | training | off_session | london_ge75 | 0.0 | 0.0 | 315 | 18889 |
| monthly_acquisitions | ES | 2020 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 315 | 18889 |
| monthly_acquisitions | ES | 2020 | training | off_session | ofi | 0.03390492361415602 | 0.4453888115305488 | 207 | 10972 |
| monthly_acquisitions | ES | 2020 | training | pre_rth | all | 41.3693171608266 | 71.71126085654387 | 318 | 66780 |
| monthly_acquisitions | ES | 2020 | training | pre_rth | ny_ge100 | 0.519257262653489 | 7.562938005390835 | 318 | 66780 |
| monthly_acquisitions | ES | 2020 | training | pre_rth | london_ge75 | 1.3612458820005988 | 12.55717280622941 | 318 | 66780 |
| monthly_acquisitions | ES | 2020 | training | pre_rth | inclusive30_through60 | 7.3423030847559145 | 24.457487271638215 | 318 | 66780 |
| monthly_acquisitions | ES | 2020 | training | pre_rth | ofi | 114.75004814462322 | 141.9928587402803 | 211 | 44276 |
| monthly_acquisitions | ES | 2021 | unassigned | futures_wallclock_18_17 | all | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2021 | unassigned | futures_wallclock_18_17 | ny_ge100 | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2021 | unassigned | futures_wallclock_18_17 | london_ge75 | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2021 | unassigned | futures_wallclock_18_17 | inclusive30_through60 | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2021 | unassigned | futures_wallclock_18_17 | ofi | None | None | 0 | 0 |
| monthly_acquisitions | ES | 2023 | development | cash_rth | all | 170.79386592243733 | 306.71143961858246 | 126 | 48780 |
| monthly_acquisitions | ES | 2023 | development | cash_rth | ny_ge100 | 8.084772370486657 | 46.461611140182576 | 126 | 48780 |
| monthly_acquisitions | ES | 2023 | development | cash_rth | london_ge75 | 18.09205186348043 | 79.20070934356649 | 126 | 48780 |
| monthly_acquisitions | ES | 2023 | development | cash_rth | inclusive30_through60 | 55.12720507006222 | 102.28443514157802 | 126 | 48780 |
| monthly_acquisitions | ES | 2023 | development | cash_rth | ofi | 590.9842971993318 | 703.6173179061312 | 124 | 47999 |
| monthly_acquisitions | ES | 2023 | development | futures_wallclock_18_17 | all | 17.173430283889292 | 34.384478757973504 | 176 | 155032 |
| monthly_acquisitions | ES | 2023 | development | futures_wallclock_18_17 | ny_ge100 | 0.5312419080624817 | 4.654339497531175 | 176 | 155032 |
| monthly_acquisitions | ES | 2023 | development | futures_wallclock_18_17 | london_ge75 | 0.7995223716519306 | 6.110271523242983 | 176 | 155032 |
| monthly_acquisitions | ES | 2023 | development | futures_wallclock_18_17 | inclusive30_through60 | 1.9490427786429156 | 9.076514295584628 | 176 | 155032 |
| monthly_acquisitions | ES | 2023 | development | futures_wallclock_18_17 | ofi | 70.22947834992446 | 92.42190865537845 | 174 | 154448 |
| monthly_acquisitions | ES | 2023 | development | off_session | all | 0.0 | 0.0 | 172 | 10320 |
| monthly_acquisitions | ES | 2023 | development | off_session | ny_ge100 | 0.0 | 0.0 | 172 | 10320 |
| monthly_acquisitions | ES | 2023 | development | off_session | london_ge75 | 0.0 | 0.0 | 172 | 10320 |
| monthly_acquisitions | ES | 2023 | development | off_session | inclusive30_through60 | 0.0 | 0.0 | 172 | 10320 |
| monthly_acquisitions | ES | 2023 | development | off_session | ofi | 0.024832178908120596 | 0.5314163697577047 | 170 | 9081 |
| monthly_acquisitions | ES | 2023 | development | pre_rth | all | 37.21349206349207 | 68.89838533114394 | 174 | 36540 |
| monthly_acquisitions | ES | 2023 | development | pre_rth | ny_ge100 | 0.19258347016967708 | 3.5785714285714287 | 174 | 36540 |
| monthly_acquisitions | ES | 2023 | development | pre_rth | london_ge75 | 0.570607553366174 | 7.547345374931582 | 174 | 36540 |
| monthly_acquisitions | ES | 2023 | development | pre_rth | inclusive30_through60 | 6.984428024083197 | 24.386535303776682 | 174 | 36540 |
| monthly_acquisitions | ES | 2023 | development | pre_rth | ofi | 133.00032840722497 | 172.4631636562671 | 174 | 36540 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | all | 167.78692728036987 | 285.4113913408995 | 61 | 23790 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | ny_ge100 | 11.287599831862128 | 53.1764186633039 | 61 | 23790 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | london_ge75 | 21.022362337116434 | 86.0199663724254 | 61 | 23790 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | inclusive30_through60 | 54.35212274064734 | 98.36031946195881 | 61 | 23790 |
| monthly_acquisitions | ES | 2024 | calibration | cash_rth | ofi | 609.9527472527473 | 743.2315018315019 | 7 | 2730 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | all | 16.3769811556805 | 34.40463880116584 | 89 | 78326 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | ny_ge100 | 0.5504152813975609 | 7.16801133588849 | 89 | 78326 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | london_ge75 | 0.9316308547432721 | 8.571140765435414 | 89 | 78326 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | inclusive30_through60 | 2.047046396951801 | 8.981736120449616 | 89 | 78326 |
| monthly_acquisitions | ES | 2024 | calibration | futures_wallclock_18_17 | ofi | 56.03361564047582 | 74.28719366960328 | 13 | 12353 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | all | 0.0 | 0.0 | 88 | 5280 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | ny_ge100 | 0.0 | 0.0 | 88 | 5280 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | london_ge75 | 0.0 | 0.0 | 88 | 5280 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | inclusive30_through60 | 0.0 | 0.0 | 88 | 5280 |
| monthly_acquisitions | ES | 2024 | calibration | off_session | ofi | 0.0 | 0.2311965811965812 | 13 | 720 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | all | 36.03528138528139 | 64.11006493506494 | 88 | 18480 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | ny_ge100 | 0.22510822510822512 | 3.8274891774891775 | 88 | 18480 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | london_ge75 | 0.7046536796536796 | 7.073376623376623 | 88 | 18480 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | inclusive30_through60 | 7.129004329004329 | 23.97440476190476 | 88 | 18480 |
| monthly_acquisitions | ES | 2024 | calibration | pre_rth | ofi | 119.5076923076923 | 168.7076923076923 | 13 | 2730 |
| monthly_acquisitions | ES | 2024 | confirmation | cash_rth | all | 165.7877409195166 | 280.0458731299853 | 107 | 41550 |
| monthly_acquisitions | ES | 2024 | confirmation | cash_rth | ny_ge100 | 5.116370545342509 | 37.42064290849338 | 107 | 41550 |
| monthly_acquisitions | ES | 2024 | confirmation | cash_rth | london_ge75 | 10.887261648009314 | 62.55465406867276 | 107 | 41550 |
| monthly_acquisitions | ES | 2024 | confirmation | cash_rth | inclusive30_through60 | 48.97446852213208 | 100.8074732121461 | 107 | 41550 |
| monthly_acquisitions | ES | 2024 | confirmation | cash_rth | ofi | 605.9676983474441 | 703.4929397681799 | 57 | 22048 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | all | 16.320705899613706 | 30.92687914872377 | 149 | 130283 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | ny_ge100 | 0.32204800757337876 | 3.9071663162851915 | 149 | 130283 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | london_ge75 | 0.5855299614818396 | 4.941529633596304 | 149 | 130283 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | inclusive30_through60 | 1.6756911478843222 | 7.449353381783225 | 149 | 130283 |
| monthly_acquisitions | ES | 2024 | confirmation | futures_wallclock_18_17 | ofi | 64.85387524756842 | 81.32156885162257 | 80 | 71138 |
| monthly_acquisitions | ES | 2024 | confirmation | off_session | all | 0.0 | 0.0 | 146 | 8760 |
| monthly_acquisitions | ES | 2024 | confirmation | off_session | ny_ge100 | 0.0 | 0.0 | 146 | 8760 |
| monthly_acquisitions | ES | 2024 | confirmation | off_session | london_ge75 | 0.0 | 0.0 | 146 | 8760 |
| monthly_acquisitions | ES | 2024 | confirmation | off_session | inclusive30_through60 | 0.0 | 0.0 | 146 | 8760 |
| monthly_acquisitions | ES | 2024 | confirmation | off_session | ofi | 0.006143402016342068 | 0.23274759171071827 | 79 | 4164 |
| monthly_acquisitions | ES | 2024 | confirmation | pre_rth | all | 34.998873873873876 | 60.44095881595883 | 148 | 31080 |
| monthly_acquisitions | ES | 2024 | confirmation | pre_rth | ny_ge100 | 0.10283140283140282 | 3.0743886743886746 | 148 | 31080 |
| monthly_acquisitions | ES | 2024 | confirmation | pre_rth | london_ge75 | 0.39517374517374515 | 5.703314028314028 | 148 | 31080 |
| monthly_acquisitions | ES | 2024 | confirmation | pre_rth | inclusive30_through60 | 5.1988416988417 | 19.70620978120978 | 148 | 31080 |
| monthly_acquisitions | ES | 2024 | confirmation | pre_rth | ofi | 114.14541666666669 | 138.26315476190476 | 80 | 16800 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | all | 51.674825970841916 | 90.11766268260293 | 251 | 97530 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | ny_ge100 | 0.001031770354479518 | 0.2749923383389519 | 251 | 97530 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | london_ge75 | 0.013106548166309124 | 0.8262379055207741 | 251 | 97530 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | inclusive30_through60 | 0.6952045298658844 | 4.620126089050392 | 251 | 97530 |
| monthly_acquisitions | NQ | 2020 | training | cash_rth | ofi | 141.18251116704354 | 147.07539743545757 | 167 | 64686 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | all | 8.726546299571051 | 14.492208495379451 | 353 | 307383 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.0368090361008208 | 353 | 307383 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | london_ge75 | 0.0 | 0.08145783021617768 | 353 | 307383 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.011151498549635706 | 0.341858141507854 | 353 | 307383 |
| monthly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ofi | 27.503755697558947 | 33.35891552358357 | 241 | 211986 |
| monthly_acquisitions | NQ | 2020 | training | off_session | all | 0.0 | 0.0 | 344 | 20629 |
| monthly_acquisitions | NQ | 2020 | training | off_session | ny_ge100 | 0.0 | 0.0 | 344 | 20629 |
| monthly_acquisitions | NQ | 2020 | training | off_session | london_ge75 | 0.0 | 0.0 | 344 | 20629 |
| monthly_acquisitions | NQ | 2020 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 344 | 20629 |
| monthly_acquisitions | NQ | 2020 | training | off_session | ofi | 0.02476510429006131 | 0.11665799680596432 | 236 | 13153 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | all | 13.346836832715796 | 20.986839577329487 | 347 | 72870 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | ny_ge100 | 0.0 | 0.07966241251543844 | 347 | 72870 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | london_ge75 | 0.0013585837793330588 | 0.1491148620831618 | 347 | 72870 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | inclusive30_through60 | 0.1792781665980513 | 0.9181418965280637 | 347 | 72870 |
| monthly_acquisitions | NQ | 2020 | training | pre_rth | ofi | 34.74492962502289 | 41.021310488595894 | 240 | 50368 |
| monthly_acquisitions | NQ | 2021 | training | cash_rth | all | 54.82180504680504 | 93.60140996569568 | 252 | 98100 |
| monthly_acquisitions | NQ | 2021 | training | cash_rth | ny_ge100 | 0.0010175010175010174 | 0.16195563695563694 | 252 | 98100 |
| monthly_acquisitions | NQ | 2021 | training | cash_rth | london_ge75 | 0.005850630850630851 | 0.47165242165242166 | 252 | 98100 |
| monthly_acquisitions | NQ | 2021 | training | cash_rth | inclusive30_through60 | 0.19044566544566544 | 3.790200011628583 | 252 | 98100 |
| monthly_acquisitions | NQ | 2021 | training | cash_rth | ofi | 178.2117069151805 | 210.32025145316805 | 134 | 52078 |
| monthly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | all | 7.131672570898879 | 13.093136117332573 | 354 | 310123 |
| monthly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.010980556123469286 | 354 | 310123 |
| monthly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | london_ge75 | 0.0005649717514124294 | 0.035604397130311036 | 354 | 310123 |
| monthly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.01035125474120507 | 0.32428374383803 | 354 | 310123 |
| monthly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | ofi | 27.764718239898045 | 33.50613895605534 | 192 | 170049 |
| monthly_acquisitions | NQ | 2021 | training | off_session | all | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2021 | training | off_session | ny_ge100 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2021 | training | off_session | london_ge75 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2021 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2021 | training | off_session | ofi | 0.009727866820883106 | 0.06447462760682973 | 189 | 10434 |
| monthly_acquisitions | NQ | 2021 | training | pre_rth | all | 12.117850340136055 | 21.244312925170068 | 350 | 73500 |
| monthly_acquisitions | NQ | 2021 | training | pre_rth | ny_ge100 | 0.0 | 0.02414965986394558 | 350 | 73500 |
| monthly_acquisitions | NQ | 2021 | training | pre_rth | london_ge75 | 0.0010884353741496598 | 0.08303401360544219 | 350 | 73500 |
| monthly_acquisitions | NQ | 2021 | training | pre_rth | inclusive30_through60 | 0.028789115646258502 | 0.6081496598639455 | 350 | 73500 |
| monthly_acquisitions | NQ | 2021 | training | pre_rth | ofi | 42.16758717342599 | 48.150734554188496 | 192 | 40319 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | all | 64.24505494505495 | 106.29581746274974 | 251 | 97710 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | ny_ge100 | 0.001031770354479518 | 0.43907447134538763 | 251 | 97710 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | london_ge75 | 0.005444887118193891 | 0.8054872086744596 | 251 | 97710 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | inclusive30_through60 | 0.1907447134538768 | 3.615386074748625 | 251 | 97710 |
| monthly_acquisitions | NQ | 2022 | training | cash_rth | ofi | 210.1000557413601 | 234.10624303233 | 46 | 17940 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | all | 8.880393505445335 | 14.977850563037823 | 354 | 308173 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.015025136078957264 | 354 | 308173 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | london_ge75 | 0.0 | 0.03470347970198471 | 354 | 308173 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.007929916723542275 | 0.26988449013184357 | 354 | 308173 |
| monthly_acquisitions | NQ | 2022 | training | futures_wallclock_18_17 | ofi | 28.309922168241595 | 37.208949715568124 | 72 | 65357 |
| monthly_acquisitions | NQ | 2022 | training | off_session | all | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2022 | training | off_session | ny_ge100 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2022 | training | off_session | london_ge75 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2022 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2022 | training | off_session | ofi | 0.007130180259077295 | 0.08918674334384427 | 72 | 4114 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | all | 16.01126530612245 | 25.819482993197276 | 350 | 73500 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | ny_ge100 | 0.0013605442176870747 | 0.01959183673469388 | 350 | 73500 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | london_ge75 | 0.0013605442176870747 | 0.07089795918367348 | 350 | 73500 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | inclusive30_through60 | 0.019414965986394556 | 0.5020544217687075 | 350 | 73500 |
| monthly_acquisitions | NQ | 2022 | training | pre_rth | ofi | 46.265283157388424 | 56.67390604035341 | 72 | 15118 |
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
| monthly_acquisitions | NQ | 2024 | calibration | cash_rth | all | 62.04735744622963 | 106.57150856662136 | 252 | 97739 |
| monthly_acquisitions | NQ | 2024 | calibration | cash_rth | ny_ge100 | 0.00876068376068376 | 1.0196595732310016 | 252 | 97739 |
| monthly_acquisitions | NQ | 2024 | calibration | cash_rth | london_ge75 | 0.012148962148962147 | 1.4835949764521195 | 252 | 97739 |
| monthly_acquisitions | NQ | 2024 | calibration | cash_rth | inclusive30_through60 | 0.13413134484563058 | 3.331212939107676 | 252 | 97739 |
| monthly_acquisitions | NQ | 2024 | calibration | cash_rth | ofi | 200.89859846178265 | 193.5922559811361 | 125 | 48385 |
| monthly_acquisitions | NQ | 2024 | calibration | futures_wallclock_18_17 | all | 7.364005118418026 | 13.944110741481179 | 355 | 310755 |
| monthly_acquisitions | NQ | 2024 | calibration | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.03917631366017137 | 355 | 310755 |
| monthly_acquisitions | NQ | 2024 | calibration | futures_wallclock_18_17 | london_ge75 | 0.0005742145178764897 | 0.08412421426106448 | 355 | 310755 |
| monthly_acquisitions | NQ | 2024 | calibration | futures_wallclock_18_17 | inclusive30_through60 | 0.007206867039409854 | 0.2826599581512628 | 355 | 310755 |
| monthly_acquisitions | NQ | 2024 | calibration | futures_wallclock_18_17 | ofi | 31.9460514143725 | 37.23129371075158 | 178 | 157890 |
| monthly_acquisitions | NQ | 2024 | calibration | off_session | all | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2024 | calibration | off_session | ny_ge100 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2024 | calibration | off_session | london_ge75 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2024 | calibration | off_session | inclusive30_through60 | 0.0 | 0.0 | 347 | 20820 |
| monthly_acquisitions | NQ | 2024 | calibration | off_session | ofi | 0.012994045832023488 | 0.053123342585077 | 173 | 9461 |
| monthly_acquisitions | NQ | 2024 | calibration | pre_rth | all | 14.873382173382174 | 25.843101343101345 | 351 | 73710 |
| monthly_acquisitions | NQ | 2024 | calibration | pre_rth | ny_ge100 | 0.0 | 0.16742640075973406 | 351 | 73710 |
| monthly_acquisitions | NQ | 2024 | calibration | pre_rth | london_ge75 | 0.0010446343779677112 | 0.3077872744539411 | 351 | 73710 |
| monthly_acquisitions | NQ | 2024 | calibration | pre_rth | inclusive30_through60 | 0.01409578076244743 | 0.6994844661511328 | 351 | 73710 |
| monthly_acquisitions | NQ | 2024 | calibration | pre_rth | ofi | 47.22420888789901 | 53.61724420858069 | 178 | 37379 |
| monthly_acquisitions | NQ | 2025 | confirmation | cash_rth | all | 57.71348397252012 | 88.08336054842079 | 249 | 96750 |
| monthly_acquisitions | NQ | 2025 | confirmation | cash_rth | ny_ge100 | 0.009329626197096076 | 1.9479544551833707 | 249 | 96750 |
| monthly_acquisitions | NQ | 2025 | confirmation | cash_rth | london_ge75 | 0.024302337555349603 | 2.727519602218397 | 249 | 96750 |
| monthly_acquisitions | NQ | 2025 | confirmation | cash_rth | inclusive30_through60 | 0.11912264442384925 | 3.073567530194036 | 249 | 96750 |
| monthly_acquisitions | NQ | 2025 | confirmation | cash_rth | ofi | 214.29195452371678 | 220.71335355221015 | 245 | 95174 |
| monthly_acquisitions | NQ | 2025 | confirmation | futures_wallclock_18_17 | all | 7.844123307130048 | 14.225762238377671 | 352 | 310546 |
| monthly_acquisitions | NQ | 2025 | confirmation | futures_wallclock_18_17 | ny_ge100 | 0.0007830710955710956 | 0.1629017240079258 | 352 | 310546 |
| monthly_acquisitions | NQ | 2025 | confirmation | futures_wallclock_18_17 | london_ge75 | 0.002352855477855478 | 0.22883711278674052 | 352 | 310546 |
| monthly_acquisitions | NQ | 2025 | confirmation | futures_wallclock_18_17 | inclusive30_through60 | 0.006694347319347319 | 0.32714710007716036 | 352 | 310546 |
| monthly_acquisitions | NQ | 2025 | confirmation | futures_wallclock_18_17 | ofi | 36.44335553742131 | 43.80291004882186 | 345 | 305016 |
| monthly_acquisitions | NQ | 2025 | confirmation | off_session | all | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2025 | confirmation | off_session | ny_ge100 | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2025 | confirmation | off_session | london_ge75 | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2025 | confirmation | off_session | inclusive30_through60 | 0.0 | 0.0 | 343 | 20580 |
| monthly_acquisitions | NQ | 2025 | confirmation | off_session | ofi | 0.020367773210512825 | 0.10910499334448506 | 335 | 18270 |
| monthly_acquisitions | NQ | 2025 | confirmation | pre_rth | all | 13.472071702244115 | 21.765120415982484 | 348 | 73001 |
| monthly_acquisitions | NQ | 2025 | confirmation | pre_rth | ny_ge100 | 0.0 | 0.31443623426382045 | 348 | 73001 |
| monthly_acquisitions | NQ | 2025 | confirmation | pre_rth | london_ge75 | 0.0 | 0.4696086480569239 | 348 | 73001 |
| monthly_acquisitions | NQ | 2025 | confirmation | pre_rth | inclusive30_through60 | 0.013984674329501914 | 0.5814449917898193 | 348 | 73001 |
| monthly_acquisitions | NQ | 2025 | confirmation | pre_rth | ofi | 51.8468870378907 | 61.29177575280696 | 344 | 72227 |
| monthly_acquisitions | NQ | 2026 | confirmation | cash_rth | all | 57.65551972977123 | 92.96787962536466 | 167 | 65130 |
| monthly_acquisitions | NQ | 2026 | confirmation | cash_rth | ny_ge100 | 0.013127590971902348 | 2.3770766159987713 | 167 | 65130 |
| monthly_acquisitions | NQ | 2026 | confirmation | cash_rth | london_ge75 | 0.049669890987256264 | 3.430968831567634 | 167 | 65130 |
| monthly_acquisitions | NQ | 2026 | confirmation | cash_rth | inclusive30_through60 | 0.18682634730538925 | 3.8392292338400127 | 167 | 65130 |
| monthly_acquisitions | NQ | 2026 | confirmation | cash_rth | ofi | 234.896189377108 | 254.56154512536628 | 164 | 63949 |
| monthly_acquisitions | NQ | 2026 | confirmation | futures_wallclock_18_17 | all | 9.633603661510197 | 17.64126341552546 | 238 | 210360 |
| monthly_acquisitions | NQ | 2026 | confirmation | futures_wallclock_18_17 | ny_ge100 | 0.0005548373195432019 | 0.21036864956440499 | 238 | 210360 |
| monthly_acquisitions | NQ | 2026 | confirmation | futures_wallclock_18_17 | london_ge75 | 0.0005548373195432019 | 0.3185192969777755 | 238 | 210360 |
| monthly_acquisitions | NQ | 2026 | confirmation | futures_wallclock_18_17 | inclusive30_through60 | 0.008685822888907721 | 0.4148134606339225 | 238 | 210360 |
| monthly_acquisitions | NQ | 2026 | confirmation | futures_wallclock_18_17 | ofi | 54.85043453850944 | 67.3320910830766 | 233 | 205560 |
| monthly_acquisitions | NQ | 2026 | confirmation | off_session | all | 0.0 | 0.0 | 233 | 13972 |
| monthly_acquisitions | NQ | 2026 | confirmation | off_session | ny_ge100 | 0.0 | 0.0 | 233 | 13972 |
| monthly_acquisitions | NQ | 2026 | confirmation | off_session | london_ge75 | 0.0 | 0.0 | 233 | 13972 |
| monthly_acquisitions | NQ | 2026 | confirmation | off_session | inclusive30_through60 | 0.0 | 0.0 | 233 | 13972 |
| monthly_acquisitions | NQ | 2026 | confirmation | off_session | ofi | 0.018804211893995514 | 0.07117054135744715 | 227 | 12549 |
| monthly_acquisitions | NQ | 2026 | confirmation | pre_rth | all | 13.951773049645391 | 22.84008105369807 | 235 | 49350 |
| monthly_acquisitions | NQ | 2026 | confirmation | pre_rth | ny_ge100 | 0.002127659574468085 | 0.3566970618034448 | 235 | 49350 |
| monthly_acquisitions | NQ | 2026 | confirmation | pre_rth | london_ge75 | 0.003850050658561297 | 0.5498074974670719 | 235 | 49350 |
| monthly_acquisitions | NQ | 2026 | confirmation | pre_rth | inclusive30_through60 | 0.015845997973657548 | 0.7258156028368794 | 235 | 49350 |
| monthly_acquisitions | NQ | 2026 | confirmation | pre_rth | ofi | 67.29238957290904 | 83.1104974163074 | 231 | 48502 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | all | 51.674825970841916 | 90.11766268260293 | 251 | 97530 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | ny_ge100 | 0.001031770354479518 | 0.2749923383389519 | 251 | 97530 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | london_ge75 | 0.013106548166309124 | 0.8262379055207741 | 251 | 97530 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | inclusive30_through60 | 0.6952045298658844 | 4.620126089050392 | 251 | 97530 |
| weekly_acquisitions | NQ | 2020 | training | cash_rth | ofi | 142.51613983912435 | 147.15326009786148 | 246 | 95492 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | all | 8.531946883798666 | 14.1699160465782 | 361 | 316842 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.036016740643277895 | 361 | 316842 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | london_ge75 | 0.0 | 0.07969976857496643 | 361 | 316842 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.010911106778383133 | 0.33444753847776215 | 361 | 316842 |
| weekly_acquisitions | NQ | 2020 | training | futures_wallclock_18_17 | ofi | 27.291489957970086 | 32.61327397157943 | 352 | 307989 |
| weekly_acquisitions | NQ | 2020 | training | off_session | all | 0.0 | 0.0 | 357 | 21409 |
| weekly_acquisitions | NQ | 2020 | training | off_session | ny_ge100 | 0.0 | 0.0 | 357 | 21409 |
| weekly_acquisitions | NQ | 2020 | training | off_session | london_ge75 | 0.0 | 0.0 | 357 | 21409 |
| weekly_acquisitions | NQ | 2020 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 357 | 21409 |
| weekly_acquisitions | NQ | 2020 | training | off_session | ofi | 0.027464227658913515 | 0.12009234973687877 | 347 | 19332 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | all | 13.046063044936286 | 20.513896713615026 | 355 | 74550 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | ny_ge100 | 0.0 | 0.07786720321931588 | 355 | 74550 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | london_ge75 | 0.0013279678068410462 | 0.14575452716297788 | 355 | 74550 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | inclusive30_through60 | 0.17523809523809525 | 0.8974513749161636 | 355 | 74550 |
| weekly_acquisitions | NQ | 2020 | training | pre_rth | ofi | 34.76739771799568 | 40.586715879411024 | 351 | 73676 |
| weekly_acquisitions | NQ | 2021 | training | cash_rth | all | 52.90728744939272 | 94.54966261808367 | 38 | 14820 |
| weekly_acquisitions | NQ | 2021 | training | cash_rth | ny_ge100 | 0.0 | 0.2092442645074224 | 38 | 14820 |
| weekly_acquisitions | NQ | 2021 | training | cash_rth | london_ge75 | 0.0 | 0.5215249662618083 | 38 | 14820 |
| weekly_acquisitions | NQ | 2021 | training | cash_rth | inclusive30_through60 | 0.15641025641025638 | 3.3702429149797566 | 38 | 14820 |
| weekly_acquisitions | NQ | 2021 | training | cash_rth | ofi | 161.0176113360324 | 153.64251012145752 | 38 | 14820 |
| weekly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | all | 7.623161236743126 | 13.292837640766688 | 60 | 54017 |
| weekly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | ny_ge100 | 0.0 | 0.004423076923076923 | 60 | 54017 |
| weekly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | london_ge75 | 0.001623931623931624 | 0.03779404944934232 | 60 | 54017 |
| weekly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | inclusive30_through60 | 0.025899358425065366 | 0.3442840539470477 | 60 | 54017 |
| weekly_acquisitions | NQ | 2021 | training | futures_wallclock_18_17 | ofi | 27.043195907681095 | 31.74961445224277 | 60 | 53481 |
| weekly_acquisitions | NQ | 2021 | training | off_session | all | 0.0 | 0.0 | 59 | 3540 |
| weekly_acquisitions | NQ | 2021 | training | off_session | ny_ge100 | 0.0 | 0.0 | 59 | 3540 |
| weekly_acquisitions | NQ | 2021 | training | off_session | london_ge75 | 0.0 | 0.0 | 59 | 3540 |
| weekly_acquisitions | NQ | 2021 | training | off_session | inclusive30_through60 | 0.0 | 0.0 | 59 | 3540 |
| weekly_acquisitions | NQ | 2021 | training | off_session | ofi | 0.011499854851510876 | 0.08046715063498106 | 59 | 3334 |
| weekly_acquisitions | NQ | 2021 | training | pre_rth | all | 11.685472154963682 | 18.98232445520581 | 59 | 12390 |
| weekly_acquisitions | NQ | 2021 | training | pre_rth | ny_ge100 | 0.0 | 0.061824051654560126 | 59 | 12390 |
| weekly_acquisitions | NQ | 2021 | training | pre_rth | london_ge75 | 0.0 | 0.14051654560129134 | 59 | 12390 |
| weekly_acquisitions | NQ | 2021 | training | pre_rth | inclusive30_through60 | 0.041000807102502014 | 0.5092009685230023 | 59 | 12390 |
| weekly_acquisitions | NQ | 2021 | training | pre_rth | ofi | 38.20218998961193 | 41.52266490571575 | 59 | 12389 |

## Source aliases and disagreement

- alias groups: 3170
- matched equal measurements: 589376
- matched different measurements: 0
- mismatched contracts not joined: 0
- incompatible coordinates: 16448
- no source winner is selected from these descriptive counts.

## Groups

- root/source/year/stage/session groups: 13

Overlapping hard cohorts are occupancy fractions, not a partition. OFI analogs use only full pressure-eligible windows; the observed OFI subset is separate. Futures 18:00-17:00 is an observed wall clock, not a certified venue calendar.

