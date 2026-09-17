# Population, source-faithful Jumbo and Green Bird (B0.3-2026-09-17)

- sessions: 1742 of 1742 (failures: 0)
- wall: 1324.2s on 10 workers; 7.54s per session per worker
- worker peak RSS: 2.11 GB
- causality violations (decision_at < max stage at_ns): 0
- SessionStat envelope computed: False

## Branch population

An opportunity is one (side, reference, cycle) that passed; the entry modes are
alternative fills of the same opportunity, not separate setups.

| family | branch | episodes | pass | fail | unknown | pass/session | opportunities/session |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | asia_box | 50354 | 43172 | 7182 | 0 | 24.78 | 7.25 |
| GB-FAIL | asia_tdo_case | 81123 | 55906 | 25217 | 0 | 32.09 | 12.37 |
| GB-FAIL | cash_open_reclaim_case | 32820 | 13584 | 19236 | 0 | 7.80 | 1.61 |
| GB-FAIL | continuation | 7510 | 3550 | 3960 | 0 | 2.04 | 2.04 |
| GB-FAIL | golden_pocket | 3444 | 1486 | 1958 | 0 | 0.85 | 0.77 |
| GB-FAIL | london_box | 44124 | 38385 | 5739 | 0 | 22.04 | 7.11 |
| GB-FAIL | nyam_box | 47496 | 41965 | 5531 | 0 | 24.09 | 8.28 |
| GB-FAIL | previous_hour | 420183 | 360164 | 60019 | 0 | 206.75 | 21.74 |
| GB-FAIL | prior_day_level | 58087 | 36884 | 21203 | 0 | 21.17 | 6.84 |
| GB-FAIL | prior_week_level | 29267 | 16242 | 13025 | 0 | 9.32 | 3.08 |
| GB-SCALP | golden_pocket_continuation | 3444 | 1486 | 1958 | 0 | 0.85 | 0.77 |
| GB-VWAP | source_long | 753 | 256 | 497 | 0 | 0.15 | 0.15 |
| JJ-TBR | extension_reaction | 3378 | 737 | 2641 | 0 | 0.42 | 0.42 |
| JJ-TBR | internal_rotation | 46862 | 21000 | 25862 | 0 | 12.06 | 12.06 |
| JJ-TBR | judas_outbound | 8313 | 0 | 8313 | 0 | 0.00 | 0.00 |
| JJ-TBR | judas_reversal | 112628 | 50489 | 62139 | 0 | 28.98 | 13.59 |
| JJ-TBR | other_session | 89648 | 34701 | 54947 | 0 | 19.92 | 17.89 |
| JJ-TBR | single_extended | 18657 | 3224 | 15433 | 0 | 1.85 | 1.85 |
| JJ-TBR | single_purged | 16409 | 7942 | 8467 | 0 | 4.56 | 4.56 |
| JJ-TBR | timed_pzone_reversal | 26 | 20 | 6 | 0 | 0.01 | 0.00 |

## Selected trade list (the author's frequency)

| family | entries/session mean | distribution | outcomes |
| --- | --- | --- | --- |
| JJ-TBR | 1.82 | {0: 22, 3: 455, 2: 543, 1: 722} | {'stop': 1952, 'target': 1055, 'open': 119, 'ambiguous': 47} |
| GB-FAIL | 2.16 | {0: 20, 1: 491, 3: 813, 2: 418} | {'target': 905, 'open': 156, 'stop': 2690, 'ambiguous': 15} |
| GB-VWAP | 0.15 | {0: 1486, 1: 256} | {'target': 100, 'stop': 146, 'open': 10} |
| GB-SCALP | 0.74 | {0: 575, 1: 1046, 2: 121} | {'target': 794, 'stop': 486, 'ambiguous': 7, 'open': 1} |

## Risk and reward on the selected trades

| family | stop points (min/p25/median/p75/p90/max) | R:R at target |
| --- | --- | --- |
| JJ-TBR | 0.25 / 5.6175 / 12.75 / 25.75 / 44.0 / 192.0 | median 4.090909090909091 |
| GB-FAIL | 2.25 / 5.5 / 10.0 / 19.25 / 35.5 / 334.25 | median 6.55 |
| GB-VWAP | 30.0 / 30.0 / 30.0 / 30.0 / 30.0 / 30.0 | median 1.775 |
| GB-SCALP | 4.433 / 11.6645 / 18.033 / 28.614 / 46.0665 / 257.627 | median 0.5093724531377343 |

## Day reads

- Jumbo classification: {'unknown': 53, 'single_break': 816, 'double_break': 873}
- Jumbo range bins: {None: 26, '0-0.3': 347, '0.5-0.8': 455, '0.3-0.5': 531, '0.8-1.2': 230, '1.2+': 153}
- Jumbo open locations: {None: 53, 'below_val': 217, 'inside_value': 555, 'above_vah': 315, 'above_pdh': 371, 'below_pdl': 228, 'inside_range': 3}
- Green Bird day model: {'sweep_and_fail': 989, 'pullback_continuation': 753}
- primary play: {'JJ-TBR': {'london': 53, 'single_break': 816, 'double_break': 873}, 'GB-FAIL': {'ny_box_fail': 28, 'asia_fade': 960, 'overnight_reclaim': 752, 'pocket_continuation': 2}, 'GB-VWAP': {'ny_box_fail': 28, 'asia_fade': 960, 'overnight_reclaim': 752, 'pocket_continuation': 2}, 'GB-SCALP': {'ny_box_fail': 28, 'asia_fade': 960, 'overnight_reclaim': 752, 'pocket_continuation': 2}}
