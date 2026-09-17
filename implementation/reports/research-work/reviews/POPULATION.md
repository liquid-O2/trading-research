# Population, source-faithful Jumbo and Green Bird (B0.3-2026-09-17)

- sessions: 1742 of 1742 (failures: 0)
- wall: 1464.6s on 10 workers; 8.35s per session per worker
- worker peak RSS: 2.24 GB
- causality violations (decision_at < max stage at_ns): 0
- omissions recorded: 8701 (GB-FAIL:full_session_scope_unmeasured=1742, GB-FAIL:prior_day_unavailable=26, GB-FAIL:prior_full_session_unavailable=28, GB-FAIL:reference_window_unavailable=512, GB-SCALP:full_session_scope_unmeasured=1742, GB-SCALP:prior_day_unavailable=26, GB-SCALP:prior_full_session_unavailable=28, GB-SCALP:reference_window_unavailable=512)
- SessionStat envelope computed: False

## Branch population

An opportunity is one (side, reference, cycle) that passed; the entry modes are
alternative fills of the same opportunity, not separate setups.

| family | branch | episodes | pass | fail | unknown | pass/session | opportunities/session |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | asia_box | 106651 | 75812 | 30839 | 0 | 43.52 | 8.98 |
| GB-FAIL | asia_tdo_case | 98767 | 65753 | 33014 | 0 | 37.75 | 13.22 |
| GB-FAIL | cash_open_reclaim_case | 66903 | 40137 | 26766 | 0 | 23.04 | 1.89 |
| GB-FAIL | continuation | 17150 | 8271 | 8879 | 0 | 4.75 | 4.75 |
| GB-FAIL | golden_pocket | 7546 | 5129 | 2417 | 0 | 2.94 | 0.84 |
| GB-FAIL | london_box | 103467 | 70797 | 32670 | 0 | 40.64 | 8.90 |
| GB-FAIL | nyam_box | 184727 | 141203 | 43524 | 0 | 81.06 | 21.61 |
| GB-FAIL | previous_hour | 224724 | 147734 | 76990 | 0 | 84.81 | 15.59 |
| GB-FAIL | prior_day_level | 74920 | 50455 | 24465 | 0 | 28.96 | 8.76 |
| GB-FAIL | prior_week_level | 42891 | 23116 | 19775 | 0 | 13.27 | 4.10 |
| GB-SCALP | golden_pocket_continuation | 7546 | 5129 | 2417 | 0 | 2.94 | 0.84 |
| GB-VWAP | source_long | 1721 | 604 | 1117 | 0 | 0.35 | 0.35 |
| JJ-TBR | extension_reaction | 3436 | 746 | 2690 | 0 | 0.43 | 0.43 |
| JJ-TBR | internal_rotation | 327308 | 220322 | 106986 | 0 | 126.48 | 43.02 |
| JJ-TBR | judas_outbound | 13467 | 5921 | 7546 | 0 | 3.40 | 3.40 |
| JJ-TBR | judas_reversal | 165024 | 70938 | 94086 | 0 | 40.72 | 13.78 |
| JJ-TBR | other_session | 101229 | 39384 | 61845 | 0 | 22.61 | 20.58 |
| JJ-TBR | single_extended | 185496 | 137167 | 48329 | 0 | 78.74 | 26.57 |
| JJ-TBR | single_purged | 76735 | 65094 | 11641 | 0 | 37.37 | 11.82 |
| JJ-TBR | timed_pzone_reversal | 49 | 40 | 9 | 0 | 0.02 | 0.00 |

## Selected trade list (the author's frequency)

| family | entries/session mean | distribution | outcomes |
| --- | --- | --- | --- |
| JJ-TBR | 2.12 | {0: 22, 1: 515, 2: 445, 3: 760} | {'target': 951, 'stop': 2633, 'ambiguous': 27, 'open': 74} |
| GB-FAIL | 2.50 | {0: 20, 3: 1176, 1: 263, 2: 283} | {'stop': 3601, 'open': 175, 'target': 572, 'ambiguous': 9} |
| GB-VWAP | 0.35 | {0: 1138, 1: 604} | {'target': 276, 'open': 19, 'stop': 309} |
| GB-SCALP | 0.94 | {0: 431, 1: 993, 2: 318} | {'target': 291, 'stop': 1182, 'open': 155, 'ambiguous': 1} |

## Risk and reward on the selected trades

| family | stop points (min/p25/median/p75/p90/max) | R:R at target |
| --- | --- | --- |
| JJ-TBR | 0.25 / 6.75 / 12.0 / 23.75 / 43.25 / 715.4375 | median 3.671232876712329 |
| GB-FAIL | 2.0 / 6.25 / 10.25 / 18.75 / 35.0 / 474.5 | median 10.16326530612245 |
| GB-VWAP | 30.0 / 30.0 / 30.0 / 30.0 / 30.0 / 30.0 | median 1.175 |
| GB-SCALP | 2.0 / 21.2635 / 30.615 / 42.9165 / 61.3835 / 259.771 | median 3.9770284380566303 |

## Day reads

- Jumbo classification: {'unknown': 53, 'single_break': 816, 'double_break': 873}
- Jumbo range bins: {None: 26, '0-0.3': 347, '0.5-0.8': 455, '0.3-0.5': 531, '0.8-1.2': 230, '1.2+': 153}
- Jumbo open locations: {None: 53, 'below_val': 217, 'above_vah': 315, 'above_pdh': 371, 'inside_value': 555, 'below_pdl': 228, 'inside_range': 3}
- Green Bird day model: {'sweep_and_fail': 989, 'pullback_continuation': 753}
- primary play: {'JJ-TBR': {'double_break': 926, 'single_break': 816}, 'GB-FAIL': {'ny_box_fail': 28, 'asia_fade': 960, 'overnight_reclaim': 752, 'pocket_continuation': 2}, 'GB-VWAP': {'ny_box_fail': 28, 'asia_fade': 960, 'overnight_reclaim': 752, 'pocket_continuation': 2}, 'GB-SCALP': {'ny_box_fail': 28, 'asia_fade': 960, 'overnight_reclaim': 752, 'pocket_continuation': 2}}
