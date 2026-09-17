# Population, source-faithful Jumbo and Green Bird (B0.3-2026-09-17)

- sessions: 1742 of 1742 (failures: 0)
- wall: 1384.9s on 10 workers; 7.89s per session per worker
- worker peak RSS: 3.87 GB
- causality violations (decision_at < max stage at_ns): 66
- scan errors (each attributable): 0
- omissions recorded: 9102 (GB-FAIL:full_session_scope_unmeasured=1742, GB-FAIL:prior_day_unavailable=26, GB-FAIL:prior_full_session_unavailable=28, GB-FAIL:reference_window_unavailable=512, GB-SCALP:full_session_scope_unmeasured=1742, GB-SCALP:prior_day_unavailable=26, GB-SCALP:prior_full_session_unavailable=28, GB-SCALP:reference_window_unavailable=512)
- SessionStat envelope computed: False

## Branch population

An opportunity is one (side, reference, cycle) that passed; the entry modes are
alternative fills of the same opportunity, not separate setups.

| family | branch | episodes | pass | fail | unknown | pass/session | opportunities/session |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | asia_box | 40688 | 33333 | 7355 | 0 | 19.13 | 4.05 |
| GB-FAIL | asia_tdo_case | 74058 | 55958 | 18100 | 0 | 32.12 | 7.92 |
| GB-FAIL | cash_open_reclaim_case | 24846 | 15507 | 9339 | 0 | 8.90 | 1.76 |
| GB-FAIL | continuation | 17150 | 7908 | 9242 | 0 | 4.54 | 4.54 |
| GB-FAIL | golden_pocket | 31569 | 24139 | 7430 | 0 | 13.86 | 1.68 |
| GB-FAIL | london_box | 86792 | 67996 | 18796 | 0 | 39.03 | 5.72 |
| GB-FAIL | nyam_box | 150850 | 117354 | 33496 | 0 | 67.37 | 12.93 |
| GB-FAIL | previous_hour | 170811 | 125328 | 45483 | 0 | 71.94 | 18.82 |
| GB-FAIL | prior_day_level | 52863 | 38591 | 14272 | 0 | 22.15 | 4.80 |
| GB-FAIL | prior_week_level | 24402 | 17635 | 6767 | 0 | 10.12 | 2.18 |
| GB-SCALP | golden_pocket_continuation | 31569 | 24139 | 7430 | 0 | 13.86 | 1.68 |
| GB-VWAP | source_long | 1721 | 713 | 1008 | 0 | 0.41 | 0.41 |
| JJ-TBR | extension_reaction | 3436 | 746 | 2690 | 0 | 0.43 | 0.43 |
| JJ-TBR | internal_rotation | 140659 | 134205 | 6454 | 0 | 77.04 | 16.88 |
| JJ-TBR | judas_outbound | 298 | 268 | 30 | 0 | 0.15 | 0.15 |
| JJ-TBR | judas_reversal | 63311 | 62812 | 499 | 0 | 36.06 | 8.14 |
| JJ-TBR | other_session | 80143 | 79517 | 626 | 0 | 45.65 | 12.81 |
| JJ-TBR | single_extended | 21950 | 21774 | 176 | 0 | 12.50 | 2.60 |
| JJ-TBR | single_purged | 121858 | 120256 | 1602 | 0 | 69.03 | 15.01 |
| JJ-TBR | timed_pzone_reversal | 21448 | 17342 | 4106 | 0 | 9.96 | 3.55 |

## Selected trade list (the author's frequency)

| family | entries/session mean | distribution | outcomes |
| --- | --- | --- | --- |
| JJ-TBR | 9.61 | {7: 177, 0: 22, 9: 183, 10: 140, 5: 57, 12: 686, 1: 2, 8: 211, 6: 98, 4: 20, 3: 3, 11: 142, 2: 1} | {'target': 6988, 'stop': 9547, 'open': 166, 'ambiguous': 33} |
| GB-FAIL | 15.51 | {17: 220, 0: 20, 15: 325, 14: 252, 18: 440, 12: 18, 13: 128, 10: 5, 16: 297, 11: 9, 8: 2, 6: 23, 7: 3} | {'stop': 19040, 'target': 6771, 'open': 1172, 'ambiguous': 36} |
| GB-VWAP | 0.00 | {0: 1742} | None |
| GB-SCALP | 1.35 | {0: 577, 1: 496, 2: 352, 4: 93, 3: 176, 5: 39, 6: 9} | {'stop': 1596, 'open': 323, 'target': 429, 'ambiguous': 1} |

## Risk and reward on the selected trades

| family | stop points (min/p25/median/p75/p90/max) | R:R at target |
| --- | --- | --- |
| JJ-TBR | 0.25 / 6.75 / 10.375 / 21.0 / 42.0 / 522.875 | median 2.9574468085106385 |
| GB-FAIL | 2.0 / 7.0 / 12.5 / 24.25 / 49.25 / 1500.25 | median 5.458333333333333 |
| GB-SCALP | 2.0 / 16.7205 / 24.508 / 34.7445 / 47.8425 / 259.771 | median 3.4410673180814584 |

## Day reads

- Jumbo classification: {'single_break': 511, 'unknown': 53, 'double_break': 1178}
- Jumbo range bins: {'0.5-0.8': 455, None: 26, '0.3-0.5': 531, '0-0.3': 347, '0.8-1.2': 230, '1.2+': 153}
- Jumbo open locations: {'below_val': 217, None: 53, 'above_vah': 315, 'above_pdh': 371, 'inside_value': 555, 'below_pdl': 228, 'inside_range': 3}
- Green Bird day model: {'sweep_and_fail': 989, 'pullback_continuation': 753}
- primary play: {'JJ-TBR': {'single_break': 511, None: 53, 'double_break': 1178}, 'GB-FAIL': {'overnight_reclaim': 696, 'ny_box_fail': 34, 'asia_fade': 1010, 'pocket_continuation': 2}, 'GB-VWAP': {'overnight_reclaim': 696, 'ny_box_fail': 34, 'asia_fade': 1010, 'pocket_continuation': 2}, 'GB-SCALP': {'overnight_reclaim': 696, 'ny_box_fail': 34, 'asia_fade': 1010, 'pocket_continuation': 2}}


## Executed-list results by selection variant (points a contract, no costs)

| variant | family | sessions | net points / session | trades / session | win rate | round trips | open |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B0.3 | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| B0.3 | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| B0.3 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| B0.3 | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-anyadds | GB-FAIL | 1742 | 0.687 | 22.34 | 0.252 | 24281 | 1956 |
| GB-anyadds | GB-SCALP | 1742 | -7.609 | 1.35 | 0.212 | 2046 | 324 |
| GB-anyadds | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-anyadds | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-line1 | GB-FAIL | 1742 | -3.518 | 14.11 | 0.258 | 23744 | 972 |
| GB-line1 | GB-SCALP | 1742 | -6.315 | 1.16 | 0.213 | 2015 | 257 |
| GB-line1 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-line1 | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-noadds | GB-FAIL | 1742 | -2.619 | 14.13 | 0.272 | 24611 | 1013 |
| GB-noadds | GB-SCALP | 1742 | -6.311 | 1.18 | 0.214 | 2051 | 262 |
| GB-noadds | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-noadds | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-noflips | GB-FAIL | 1742 | 1.07 | 14.15 | 0.217 | 17946 | 1382 |
| GB-noflips | GB-SCALP | 1742 | -6.293 | 1.2 | 0.215 | 1968 | 274 |
| GB-noflips | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-noflips | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-noreenter | GB-FAIL | 1742 | 27.172 | 14.4 | 0.297 | 23828 | 1151 |
| GB-noreenter | GB-SCALP | 1742 | -5.575 | 1.18 | 0.223 | 2022 | 277 |
| GB-noreenter | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-noreenter | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-rt1 | GB-FAIL | 1742 | -4.388 | 3.96 | 0.222 | 5110 | 294 |
| GB-rt1 | GB-SCALP | 1742 | -3.96 | 0.7 | 0.212 | 1165 | 132 |
| GB-rt1 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-rt1 | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-rt2 | GB-FAIL | 1742 | 1.198 | 7.29 | 0.251 | 9910 | 572 |
| GB-rt2 | GB-SCALP | 1742 | -5.168 | 1.06 | 0.219 | 1741 | 224 |
| GB-rt2 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-rt2 | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| GB-rt3 | GB-FAIL | 1742 | -0.157 | 10.13 | 0.258 | 14236 | 787 |
| GB-rt3 | GB-SCALP | 1742 | -6.093 | 1.2 | 0.219 | 1967 | 264 |
| GB-rt3 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| GB-rt3 | JJ-TBR | 1742 | 67.654 | 11.46 | 0.442 | 15692 | 212 |
| JJ-line1 | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-line1 | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-line1 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-line1 | JJ-TBR | 1742 | 23.72 | 9.81 | 0.365 | 15305 | 185 |
| JJ-noadds | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-noadds | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-noadds | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-noadds | JJ-TBR | 1742 | 26.584 | 9.12 | 0.379 | 15881 | 137 |
| JJ-noflips | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-noflips | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-noflips | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-noflips | JJ-TBR | 1742 | 68.767 | 11.66 | 0.431 | 14205 | 258 |
| JJ-rt1 | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-rt1 | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-rt1 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-rt1 | JJ-TBR | 1742 | 18.36 | 2.8 | 0.434 | 3421 | 24 |
| JJ-rt2 | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-rt2 | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-rt2 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-rt2 | JJ-TBR | 1742 | 31.034 | 4.11 | 0.433 | 5064 | 51 |
| JJ-rt3 | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-rt3 | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-rt3 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-rt3 | JJ-TBR | 1742 | 42.342 | 6.32 | 0.432 | 8258 | 70 |
| JJ-rt4 | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-rt4 | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-rt4 | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-rt4 | JJ-TBR | 1742 | 49.882 | 7.28 | 0.436 | 9522 | 98 |
| JJ-timeorder | GB-FAIL | 1742 | 3.484 | 17.22 | 0.259 | 24480 | 1297 |
| JJ-timeorder | GB-SCALP | 1742 | -6.532 | 1.25 | 0.215 | 2051 | 282 |
| JJ-timeorder | GB-VWAP | 1742 | 0.0 | 0.0 | None | 0 | 0 |
| JJ-timeorder | JJ-TBR | 1742 | 67.94 | 11.46 | 0.442 | 15698 | 210 |