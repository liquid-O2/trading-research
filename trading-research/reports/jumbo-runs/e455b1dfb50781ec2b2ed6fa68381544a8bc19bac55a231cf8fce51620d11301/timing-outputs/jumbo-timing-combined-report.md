# Jumbo common-clock geometry and transition statistics

Complete declared roots: NQ.
Common-clock/source/date observations: 30848; JTR transition observations: 5784.
The original NQ2024 acquisition is reported separately from the corrected primary population. Each date contributes once within its source variant. Existing annual formation/path statistics are reused.
These are descriptive timing and geometry results. Predictive Context and Location quality remain later.

## NQ

# Jumbo timing and window descriptives

Study-local observables from retained formation/path tables. The common 10:01→actual-cash-close target is identical across declared clocks on a date; target-mean gaps are not clock gain. No Context increment, Location quality, clock ranking, or 86.46% replication is claimed.

## Source hypothesis limits

Declared study-local observables only. JTR-04 retains both the open-to-projection leg and a 09:40–09:50 mean/-0.5 opportunity; reported points are not a sample definition. JTR-07 compressed continuation and JTR-08 reversal share the same 09:40–09:50 clock; the window does not decide which path occurred. JTR-09 marks a failed apparent turn and a 10:00 news delay. Contact with EQ or a half-range extension is not a reversal, stop hunt, or inventory event. A 10-minute turn_* formation is not the full source pattern. Intra-minute sequence cannot be recovered from these three formed windows.

## Checks actually passed

13/13 recorded checks passed. Failed: none.

- `common_adapter_identity_reused`: pass
- `identical_common_target_no_clock_gain`: pass
- `missing_clock_preserves_intended_date`: pass
- `train_quantile_thresholds_independent_of_confirmation`: pass
- `common_adapter_identity_reused`: pass
- `identical_common_target_no_clock_gain`: pass
- `missing_clock_preserves_intended_date`: pass
- `source_variants_not_concatenated`: pass
- `paired_rates_same_dates_zero_event_retained`: pass
- `no_clock_ranking_emitted`: pass
- `context_increment_not_assessed`: pass
- `no_86_46_replication`: pass
- `jtr_hypothesis_limited_by_10m_ohlc`: pass

## Variants and denominators

### primary_corrected

Intended root/date counts: NQ=1676, ES=0.
Shards retained: 7. Original and corrected NQ2024 are never pooled.

#### Common-clock geometry — training_2020_2022

- NQ: 756 intended dates. Width × prior-vol controls keep the common target and date universe fixed.
  - `JTR_fixed_04`: 711 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR5`: 725 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR15`: 724 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `turn_source`: 724 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `turn_earlier`: 724 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `turn_later`: 727 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `JTR_fixed_04__shift_-10m`: 711 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `JTR_fixed_04__shift_+10m`: 712 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR5__shift_-10m`: 723 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR5__shift_+10m`: 724 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR15__shift_-10m`: 723 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR15__shift_+10m`: 724 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `prior_RTH_preopen`: 727 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR_activity_1_2`: 678 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR_activity_1_1`: 643 feature dates, 725 target dates, terminal mean -0.014774207951673965.
  - `OR_activity_3_2`: 519 feature dates, 725 target dates, terminal mean -0.014774207951673965.

| Clock / width-to-prior-range bin | Eligible dates | Mean up | Mean down | Mean terminal | Terminal 95% interval |
|---|---:|---:|---:|---:|---|
| JTR_fixed_04 / 0-0.25 | 183 | 0.37823 | 0.41685 | 0.014091 | [-0.076751, 0.10214] |
| JTR_fixed_04 / 0.25-0.5 | 374 | 0.41679 | 0.5156 | -0.029467 | [-0.091639, 0.027587] |
| JTR_fixed_04 / 0.5-1 | 127 | 0.60886 | 0.69531 | 0.030644 | [-0.11307, 0.1793] |
| JTR_fixed_04 / 1-2 | 23 | 0.66531 | 0.81516 | -0.14155 | not claimed |
| JTR_fixed_04 / 2-inf | 4 | 1.3522 | 0.90238 | 0.59191 | not claimed |
| JTR_fixed_04 / missing_own_geometry | 14 | 0.40316 | 0.83938 | -0.37664 | not claimed |
| OR5 / 0-0.25 | 422 | 0.3715 | 0.43111 | -0.016809 | [-0.067672, 0.03282] |
| OR5 / 0.25-0.5 | 266 | 0.55992 | 0.64077 | 0.029249 | [-0.071448, 0.12206] |
| OR5 / 0.5-1 | 34 | 0.61616 | 1.0501 | -0.26189 | not claimed |
| OR5 / 1-2 | 1 | 0.96706 | 2.4424 | -1.5129 | not claimed |
| OR5 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / missing_own_geometry | 2 | 0.57334 | 0.50607 | -0.49032 | not claimed |
| OR15 / 0-0.25 | 154 | 0.31025 | 0.37999 | -0.049795 | [-0.12502, 0.029319] |
| OR15 / 0.25-0.5 | 438 | 0.44438 | 0.51839 | 0.0051156 | [-0.05538, 0.06289] |
| OR15 / 0.5-1 | 126 | 0.65373 | 0.76452 | 0.00068847 | [-0.16917, 0.17693] |
| OR15 / 1-2 | 4 | 0.52128 | 1.9143 | -0.86657 | not claimed |
| OR15 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / missing_own_geometry | 3 | 0.63337 | 0.65807 | -0.63467 | not claimed |
| turn_source / 0-0.25 | 398 | 0.39104 | 0.43051 | 0.013094 | [-0.04096, 0.067845] |
| turn_source / 0.25-0.5 | 290 | 0.48998 | 0.64387 | -0.053719 | [-0.14094, 0.033612] |
| turn_source / 0.5-1 | 34 | 0.85723 | 0.92636 | 0.045884 | not claimed |
| turn_source / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / missing_own_geometry | 3 | 0.63337 | 0.65807 | -0.63467 | not claimed |
| turn_earlier / 0-0.25 | 228 | 0.33741 | 0.38078 | -0.0091948 | [-0.070979, 0.057383] |
| turn_earlier / 0.25-0.5 | 406 | 0.46557 | 0.55424 | -0.001148 | [-0.068837, 0.060379] |
| turn_earlier / 0.5-1 | 85 | 0.70068 | 0.83612 | -0.029544 | not claimed |
| turn_earlier / 1-2 | 3 | 0.45543 | 2.2167 | -1.2445 | not claimed |
| turn_earlier / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / missing_own_geometry | 3 | 0.63337 | 0.65807 | -0.63467 | not claimed |
| turn_later / 0-0.25 | 495 | 0.39586 | 0.44819 | 0.0021787 | [-0.045366, 0.051629] |
| turn_later / 0.25-0.5 | 200 | 0.5489 | 0.71521 | -0.068666 | [-0.18449, 0.067338] |
| turn_later / 0.5-1 | 27 | 0.76853 | 0.84917 | 0.15144 | not claimed |
| turn_later / 1-2 | 3 | 0.7653 | 1.2365 | -0.71522 | not claimed |
| turn_later / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| JTR_fixed_04__shift_-10m / 0-0.25 | 189 | 0.38145 | 0.41468 | 0.0053908 | [-0.085896, 0.094888] |
| JTR_fixed_04__shift_-10m / 0.25-0.5 | 377 | 0.42378 | 0.5138 | -0.010244 | [-0.06926, 0.045077] |
| JTR_fixed_04__shift_-10m / 0.5-1 | 118 | 0.56904 | 0.74319 | -0.041452 | [-0.1993, 0.11588] |
| JTR_fixed_04__shift_-10m / 1-2 | 23 | 0.8137 | 0.71293 | -0.0031084 | not claimed |
| JTR_fixed_04__shift_-10m / 2-inf | 4 | 1.3522 | 0.90238 | 0.59191 | not claimed |
| JTR_fixed_04__shift_-10m / missing_own_geometry | 14 | 0.40316 | 0.83938 | -0.37664 | not claimed |
| JTR_fixed_04__shift_+10m / 0-0.25 | 175 | 0.3574 | 0.39042 | 0.015504 | [-0.062452, 0.094488] |
| JTR_fixed_04__shift_+10m / 0.25-0.5 | 375 | 0.42285 | 0.52555 | -0.027322 | [-0.09357, 0.034889] |
| JTR_fixed_04__shift_+10m / 0.5-1 | 135 | 0.61714 | 0.67654 | 0.037641 | [-0.10267, 0.18731] |
| JTR_fixed_04__shift_+10m / 1-2 | 23 | 0.61642 | 0.85673 | -0.19854 | not claimed |
| JTR_fixed_04__shift_+10m / 2-inf | 4 | 1.3522 | 0.90238 | 0.59191 | not claimed |
| JTR_fixed_04__shift_+10m / missing_own_geometry | 13 | 0.36636 | 0.88328 | -0.46625 | not claimed |
| OR5__shift_-10m / 0-0.25 | 720 | 0.45107 | 0.5401 | -0.014744 | [-0.061304, 0.034222] |
| OR5__shift_-10m / 0.25-0.5 | 2 | 1.0532 | 0.34186 | 0.90433 | not claimed |
| OR5__shift_-10m / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / missing_own_geometry | 3 | 0.63337 | 0.65807 | -0.63467 | not claimed |
| OR5__shift_+10m / 0-0.25 | 592 | 0.42495 | 0.49553 | 0.00041401 | [-0.045608, 0.050522] |
| OR5__shift_+10m / 0.25-0.5 | 128 | 0.56801 | 0.7406 | -0.086221 | [-0.23005, 0.073864] |
| OR5__shift_+10m / 0.5-1 | 2 | 1.3004 | 0.70425 | 0.99192 | not claimed |
| OR5__shift_+10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / missing_own_geometry | 3 | 0.63337 | 0.65807 | -0.63467 | not claimed |
| OR15__shift_-10m / 0-0.25 | 373 | 0.37667 | 0.41046 | 0.012547 | [-0.037726, 0.065477] |
| OR15__shift_-10m / 0.25-0.5 | 307 | 0.51653 | 0.62812 | -0.016498 | [-0.10207, 0.07028] |
| OR15__shift_-10m / 0.5-1 | 40 | 0.66614 | 0.95516 | -0.11305 | not claimed |
| OR15__shift_-10m / 1-2 | 2 | 0.57741 | 2.7089 | -1.9503 | not claimed |
| OR15__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / missing_own_geometry | 3 | 0.63337 | 0.65807 | -0.63467 | not claimed |
| OR15__shift_+10m / 0-0.25 | 266 | 0.37317 | 0.39235 | 0.024802 | [-0.04244, 0.094272] |
| OR15__shift_+10m / 0.25-0.5 | 378 | 0.45633 | 0.56949 | -0.035377 | [-0.10425, 0.033914] |
| OR15__shift_+10m / 0.5-1 | 75 | 0.69085 | 0.90393 | -0.059756 | not claimed |
| OR15__shift_+10m / 1-2 | 3 | 1.1015 | 0.71032 | 0.81658 | not claimed |
| OR15__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / missing_own_geometry | 3 | 0.63337 | 0.65807 | -0.63467 | not claimed |
| prior_RTH_preopen / 0-0.25 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 1-2 | 725 | 0.45348 | 0.54005 | -0.014774 | [-0.060516, 0.033833] |
| prior_RTH_preopen / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 0-0.25 | 292 | 0.36159 | 0.39037 | 0.0038435 | [-0.05426, 0.064065] |
| OR_activity_1_2 / 0.25-0.5 | 340 | 0.50331 | 0.59809 | -0.010363 | [-0.087525, 0.066776] |
| OR_activity_1_2 / 0.5-1 | 43 | 0.64765 | 0.95972 | -0.11717 | not claimed |
| OR_activity_1_2 / 1-2 | 3 | 0.91186 | 2.0111 | -0.77587 | not claimed |
| OR_activity_1_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / missing_own_geometry | 47 | 0.45708 | 0.57221 | -0.020088 | not claimed |
| OR_activity_1_1 / 0-0.25 | 132 | 0.32413 | 0.33406 | 0.009227 | [-0.05968, 0.074999] |
| OR_activity_1_1 / 0.25-0.5 | 388 | 0.44344 | 0.52263 | -0.0084764 | [-0.075002, 0.053225] |
| OR_activity_1_1 / 0.5-1 | 120 | 0.64901 | 0.74974 | 0.0058626 | [-0.1707, 0.19404] |
| OR_activity_1_1 / 1-2 | 3 | 0.45543 | 2.2167 | -1.2445 | not claimed |
| OR_activity_1_1 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_1 / missing_own_geometry | 82 | 0.42304 | 0.58582 | -0.068419 | not claimed |
| OR_activity_3_2 / 0-0.25 | 48 | 0.30031 | 0.26216 | 0.051815 | not claimed |
| OR_activity_3_2 / 0.25-0.5 | 310 | 0.40763 | 0.46432 | 0.0059149 | [-0.058366, 0.065848] |
| OR_activity_3_2 / 0.5-1 | 153 | 0.53542 | 0.79048 | -0.1043 | [-0.23875, 0.046277] |
| OR_activity_3_2 / 1-2 | 8 | 1.1077 | 0.73379 | 0.57638 | not claimed |
| OR_activity_3_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_3_2 / missing_own_geometry | 206 | 0.47191 | 0.52523 | -0.01789 | [-0.10075, 0.078192] |

| Paired clocks | Common eligible dates | Width difference (ticks) | Availability difference (minutes) |
|---|---:|---:|---:|
| JTR_fixed_04 minus JTR_fixed_04__shift_-10m | 711 | 8.40787623066104 | 10.0 |
| JTR_fixed_04 minus JTR_fixed_04__shift_+10m | 711 | -5.732770745428973 | -10.0 |
| JTR_fixed_04 minus OR_activity_1_2 | 674 | 111.76706231454006 | -37.089020771513354 |
| JTR_fixed_04 minus OR_activity_1_1 | 642 | 33.38473520249221 | -45.004672897196265 |
| JTR_fixed_04 minus OR_activity_3_2 | 518 | -25.963320463320464 | -52.6988416988417 |
| OR5 minus OR5__shift_-10m | 723 | 158.61825726141078 | 10.0 |
| OR5 minus OR5__shift_+10m | 724 | 47.668508287292816 | -10.0 |
| OR5 minus OR_activity_1_2 | 678 | -33.23746312684366 | -2.1371681415929205 |
| OR5 minus OR_activity_1_1 | 643 | -107.41213063763608 | -10.001555209953343 |
| OR5 minus OR_activity_3_2 | 519 | -174.77263969171483 | -17.695568400770714 |
| OR15 minus OR15__shift_-10m | 723 | 93.70124481327801 | 10.0 |
| OR15 minus OR15__shift_+10m | 724 | 47.05939226519337 | -10.0 |
| OR15 minus OR_activity_1_2 | 678 | 77.79941002949853 | 7.8628318584070795 |
| OR15 minus OR_activity_1_1 | 643 | 3.9020217729393467 | -0.0015552099533437014 |
| OR15 minus OR_activity_3_2 | 519 | -54.714836223506744 | -7.695568400770713 |

#### Common-clock geometry — development_2023_2024

- NQ: 502 intended dates. Width × prior-vol controls keep the common target and date universe fixed.
  - `JTR_fixed_04`: 481 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR5`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR15`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `turn_source`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `turn_earlier`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `turn_later`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `JTR_fixed_04__shift_-10m`: 481 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `JTR_fixed_04__shift_+10m`: 481 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR5__shift_-10m`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR5__shift_+10m`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR15__shift_-10m`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR15__shift_+10m`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `prior_RTH_preopen`: 486 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR_activity_1_2`: 467 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR_activity_1_1`: 453 feature dates, 486 target dates, terminal mean 0.01722750950217691.
  - `OR_activity_3_2`: 352 feature dates, 486 target dates, terminal mean 0.01722750950217691.

| Clock / width-to-prior-range bin | Eligible dates | Mean up | Mean down | Mean terminal | Terminal 95% interval |
|---|---:|---:|---:|---:|---|
| JTR_fixed_04 / 0-0.25 | 117 | 0.36716 | 0.33817 | 0.076181 | [-0.012985, 0.15778] |
| JTR_fixed_04 / 0.25-0.5 | 230 | 0.43765 | 0.52393 | -0.029915 | [-0.11875, 0.066549] |
| JTR_fixed_04 / 0.5-1 | 116 | 0.59766 | 0.73153 | -0.032223 | [-0.22434, 0.13676] |
| JTR_fixed_04 / 1-2 | 15 | 1.0947 | 0.43269 | 0.66469 | not claimed |
| JTR_fixed_04 / 2-inf | 3 | 0.91745 | 0.79471 | 0.24316 | not claimed |
| JTR_fixed_04 / missing_own_geometry | 5 | 0.49421 | 0.92427 | -0.12443 | not claimed |
| OR5 / 0-0.25 | 320 | 0.4187 | 0.44055 | 0.034786 | [-0.02575, 0.099089] |
| OR5 / 0.25-0.5 | 144 | 0.5915 | 0.63406 | 0.033849 | [-0.099559, 0.17096] |
| OR5 / 0.5-1 | 22 | 0.70125 | 1.1882 | -0.34697 | not claimed |
| OR5 / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / 0-0.25 | 152 | 0.38424 | 0.35251 | 0.061702 | [-0.017226, 0.13443] |
| OR15 / 0.25-0.5 | 247 | 0.50413 | 0.52568 | 0.039954 | [-0.047752, 0.13936] |
| OR15 / 0.5-1 | 79 | 0.55926 | 0.87165 | -0.16557 | not claimed |
| OR15 / 1-2 | 8 | 0.93519 | 0.76734 | 0.2757 | not claimed |
| OR15 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 0-0.25 | 275 | 0.42272 | 0.43313 | 0.034341 | [-0.043972, 0.113] |
| turn_source / 0.25-0.5 | 183 | 0.51789 | 0.67536 | -0.056601 | [-0.18718, 0.066725] |
| turn_source / 0.5-1 | 27 | 0.85078 | 0.53814 | 0.38091 | not claimed |
| turn_source / 1-2 | 1 | 0.59579 | 1.1916 | -0.99766 | not claimed |
| turn_source / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / 0-0.25 | 212 | 0.39291 | 0.3595 | 0.063835 | [-0.011294, 0.12936] |
| turn_earlier / 0.25-0.5 | 220 | 0.54497 | 0.58806 | 0.032036 | [-0.063057, 0.1539] |
| turn_earlier / 0.5-1 | 50 | 0.5482 | 1.0005 | -0.2614 | not claimed |
| turn_earlier / 1-2 | 4 | 0.9969 | 0.70254 | 0.21543 | not claimed |
| turn_earlier / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 0-0.25 | 330 | 0.42804 | 0.46211 | 0.02124 | [-0.046606, 0.091041] |
| turn_later / 0.25-0.5 | 143 | 0.55755 | 0.69051 | -0.037527 | [-0.1991, 0.11189] |
| turn_later / 0.5-1 | 13 | 1.0466 | 0.55252 | 0.51767 | not claimed |
| turn_later / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| JTR_fixed_04__shift_-10m / 0-0.25 | 118 | 0.3615 | 0.34212 | 0.066906 | [-0.022704, 0.1478] |
| JTR_fixed_04__shift_-10m / 0.25-0.5 | 231 | 0.44657 | 0.526 | -0.019871 | [-0.10516, 0.077368] |
| JTR_fixed_04__shift_-10m / 0.5-1 | 114 | 0.59344 | 0.72412 | -0.036854 | [-0.23007, 0.13925] |
| JTR_fixed_04__shift_-10m / 1-2 | 15 | 1.0598 | 0.46601 | 0.6108 | not claimed |
| JTR_fixed_04__shift_-10m / 2-inf | 3 | 0.91745 | 0.79471 | 0.24316 | not claimed |
| JTR_fixed_04__shift_-10m / missing_own_geometry | 5 | 0.49421 | 0.92427 | -0.12443 | not claimed |
| JTR_fixed_04__shift_+10m / 0-0.25 | 108 | 0.34905 | 0.35313 | 0.028119 | [-0.064211, 0.11722] |
| JTR_fixed_04__shift_+10m / 0.25-0.5 | 233 | 0.44158 | 0.5093 | 0.0021119 | [-0.085208, 0.10136] |
| JTR_fixed_04__shift_+10m / 0.5-1 | 121 | 0.58918 | 0.72717 | -0.051068 | [-0.23768, 0.11557] |
| JTR_fixed_04__shift_+10m / 1-2 | 16 | 1.093 | 0.41398 | 0.68222 | not claimed |
| JTR_fixed_04__shift_+10m / 2-inf | 3 | 0.91745 | 0.79471 | 0.24316 | not claimed |
| JTR_fixed_04__shift_+10m / missing_own_geometry | 5 | 0.49421 | 0.92427 | -0.12443 | not claimed |
| OR5__shift_-10m / 0-0.25 | 485 | 0.48149 | 0.53221 | 0.015283 | [-0.048813, 0.080613] |
| OR5__shift_-10m / 0.25-0.5 | 1 | 1.0667 | 0.29932 | 0.96054 | not claimed |
| OR5__shift_-10m / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 0-0.25 | 407 | 0.44413 | 0.48267 | 0.028412 | [-0.030342, 0.090913] |
| OR5__shift_+10m / 0.25-0.5 | 71 | 0.64717 | 0.78616 | -0.088782 | not claimed |
| OR5__shift_+10m / 0.5-1 | 8 | 0.98475 | 0.76973 | 0.38907 | not claimed |
| OR5__shift_+10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 0-0.25 | 277 | 0.39349 | 0.42553 | 0.019906 | [-0.044956, 0.082675] |
| OR15__shift_-10m / 0.25-0.5 | 179 | 0.5738 | 0.61173 | 0.03348 | [-0.083761, 0.1467] |
| OR15__shift_-10m / 0.5-1 | 30 | 0.76272 | 1.035 | -0.10448 | not claimed |
| OR15__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / 0-0.25 | 198 | 0.37972 | 0.40582 | 0.015632 | [-0.060872, 0.093478] |
| OR15__shift_+10m / 0.25-0.5 | 239 | 0.50906 | 0.6201 | -0.014278 | [-0.12018, 0.08905] |
| OR15__shift_+10m / 0.5-1 | 45 | 0.79986 | 0.58933 | 0.2233 | not claimed |
| OR15__shift_+10m / 1-2 | 4 | 0.4363 | 0.83652 | -0.33969 | not claimed |
| OR15__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0-0.25 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 1-2 | 486 | 0.48269 | 0.53173 | 0.017228 | [-0.046788, 0.082048] |
| prior_RTH_preopen / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 0-0.25 | 259 | 0.40316 | 0.40619 | 0.033586 | [-0.034575, 0.10221] |
| OR_activity_1_2 / 0.25-0.5 | 179 | 0.55251 | 0.62435 | 0.0151 | [-0.10257, 0.13693] |
| OR_activity_1_2 / 0.5-1 | 27 | 0.72373 | 0.86907 | 0.02824 | not claimed |
| OR_activity_1_2 / 1-2 | 2 | 0.82124 | 1.0224 | 0.16003 | not claimed |
| OR_activity_1_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / missing_own_geometry | 19 | 0.53089 | 0.83955 | -0.21639 | not claimed |
| OR_activity_1_1 / 0-0.25 | 127 | 0.37967 | 0.34218 | 0.049854 | [-0.042076, 0.14021] |
| OR_activity_1_1 / 0.25-0.5 | 244 | 0.47841 | 0.54106 | 0.014265 | [-0.077189, 0.10721] |
| OR_activity_1_1 / 0.5-1 | 77 | 0.63471 | 0.72141 | 0.00077811 | not claimed |
| OR_activity_1_1 / 1-2 | 5 | 0.42253 | 0.88981 | -0.41833 | not claimed |
| OR_activity_1_1 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_1 / missing_own_geometry | 33 | 0.56523 | 0.69538 | 0.017945 | not claimed |
| OR_activity_3_2 / 0-0.25 | 54 | 0.30706 | 0.33364 | -0.030399 | not claimed |
| OR_activity_3_2 / 0.25-0.5 | 185 | 0.46148 | 0.4626 | 0.071607 | [-0.016206, 0.15783] |
| OR_activity_3_2 / 0.5-1 | 102 | 0.52518 | 0.70328 | -0.05485 | [-0.226, 0.11826] |
| OR_activity_3_2 / 1-2 | 11 | 0.85516 | 0.68908 | 0.14646 | not claimed |
| OR_activity_3_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_3_2 / missing_own_geometry | 134 | 0.51984 | 0.56351 | 0.0056013 | [-0.14677, 0.15034] |

| Paired clocks | Common eligible dates | Width difference (ticks) | Availability difference (minutes) |
|---|---:|---:|---:|
| JTR_fixed_04 minus JTR_fixed_04__shift_-10m | 481 | 5.536382536382536 | 10.0 |
| JTR_fixed_04 minus JTR_fixed_04__shift_+10m | 481 | -5.388773388773389 | -10.0 |
| JTR_fixed_04 minus OR_activity_1_2 | 467 | 135.18201284796575 | -36.845824411134906 |
| JTR_fixed_04 minus OR_activity_1_1 | 453 | 56.78587196467991 | -45.434878587196465 |
| JTR_fixed_04 minus OR_activity_3_2 | 352 | -3.4857954545454546 | -52.92897727272727 |
| OR5 minus OR5__shift_-10m | 486 | 138.54320987654322 | 10.0 |
| OR5 minus OR5__shift_+10m | 486 | 41.94855967078189 | -10.0 |
| OR5 minus OR_activity_1_2 | 467 | -22.074946466809422 | -1.8458244111349036 |
| OR5 minus OR_activity_1_1 | 453 | -101.84547461368653 | -10.434878587196469 |
| OR5 minus OR_activity_3_2 | 352 | -164.39772727272728 | -17.928977272727273 |
| OR15 minus OR15__shift_-10m | 486 | 77.31481481481481 | 10.0 |
| OR15 minus OR15__shift_+10m | 486 | 35.275720164609055 | -10.0 |
| OR15 minus OR_activity_1_2 | 467 | 75.593147751606 | 8.154175588865096 |
| OR15 minus OR_activity_1_1 | 453 | -3.335540838852097 | -0.434878587196468 |
| OR15 minus OR_activity_3_2 | 352 | -59.11079545454545 | -7.9289772727272725 |

#### Common-clock geometry — confirmation_2025_2026

- NQ: 418 intended dates. Width × prior-vol controls keep the common target and date universe fixed.
  - `JTR_fixed_04`: 381 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR5`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR15`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `turn_source`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `turn_earlier`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `turn_later`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `JTR_fixed_04__shift_-10m`: 381 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `JTR_fixed_04__shift_+10m`: 382 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR5__shift_-10m`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR5__shift_+10m`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR15__shift_-10m`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR15__shift_+10m`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `prior_RTH_preopen`: 393 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR_activity_1_2`: 378 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR_activity_1_1`: 369 feature dates, 392 target dates, terminal mean -0.005835604756712882.
  - `OR_activity_3_2`: 283 feature dates, 392 target dates, terminal mean -0.005835604756712882.

| Clock / width-to-prior-range bin | Eligible dates | Mean up | Mean down | Mean terminal | Terminal 95% interval |
|---|---:|---:|---:|---:|---|
| JTR_fixed_04 / 0-0.25 | 80 | 0.32547 | 0.36344 | 0.020321 | not claimed |
| JTR_fixed_04 / 0.25-0.5 | 202 | 0.43898 | 0.5043 | 0.0053764 | [-0.089615, 0.10763] |
| JTR_fixed_04 / 0.5-1 | 82 | 0.5712 | 0.57651 | 0.053449 | not claimed |
| JTR_fixed_04 / 1-2 | 15 | 0.5575 | 1.0717 | -0.33683 | not claimed |
| JTR_fixed_04 / 2-inf | 1 | 0.88492 | 0.013408 | 0.41788 | not claimed |
| JTR_fixed_04 / missing_own_geometry | 12 | 0.29832 | 0.84195 | -0.39562 | not claimed |
| OR5 / 0-0.25 | 211 | 0.36681 | 0.4213 | -0.003684 | [-0.07542, 0.059171] |
| OR5 / 0.25-0.5 | 160 | 0.51786 | 0.62589 | -0.026972 | [-0.15297, 0.11272] |
| OR5 / 0.5-1 | 20 | 0.68239 | 0.64869 | 0.23931 | not claimed |
| OR5 / 1-2 | 1 | 0.47506 | 2.4014 | -1.981 | not claimed |
| OR5 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / 0-0.25 | 84 | 0.31023 | 0.36099 | 0.0080899 | not claimed |
| OR15 / 0.25-0.5 | 222 | 0.41777 | 0.50098 | -0.02177 | [-0.11575, 0.066078] |
| OR15 / 0.5-1 | 78 | 0.63157 | 0.71344 | 0.0019089 | not claimed |
| OR15 / 1-2 | 8 | 0.78873 | 0.90269 | 0.21462 | not claimed |
| OR15 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 0-0.25 | 183 | 0.37652 | 0.35979 | 0.049127 | [-0.011614, 0.10851] |
| turn_source / 0.25-0.5 | 175 | 0.47461 | 0.63403 | -0.05901 | [-0.16822, 0.054421] |
| turn_source / 0.5-1 | 34 | 0.6593 | 0.81217 | -0.027975 | not claimed |
| turn_source / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / 0-0.25 | 122 | 0.34749 | 0.37537 | 0.025787 | [-0.06148, 0.10341] |
| turn_earlier / 0.25-0.5 | 213 | 0.44705 | 0.54136 | -0.036115 | [-0.13531, 0.066806] |
| turn_earlier / 0.5-1 | 53 | 0.63597 | 0.74973 | 0.049087 | not claimed |
| turn_earlier / 1-2 | 4 | 0.76386 | 0.89276 | -0.085654 | not claimed |
| turn_earlier / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 0-0.25 | 218 | 0.36436 | 0.41691 | -0.0055948 | [-0.091922, 0.065702] |
| turn_later / 0.25-0.5 | 153 | 0.51147 | 0.63386 | -0.023548 | [-0.13851, 0.10059] |
| turn_later / 0.5-1 | 21 | 0.79481 | 0.78779 | 0.12071 | not claimed |
| turn_later / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| JTR_fixed_04__shift_-10m / 0-0.25 | 89 | 0.31485 | 0.3743 | -0.016783 | not claimed |
| JTR_fixed_04__shift_-10m / 0.25-0.5 | 198 | 0.44203 | 0.51742 | 0.0095923 | [-0.098544, 0.11291] |
| JTR_fixed_04__shift_-10m / 0.5-1 | 77 | 0.58554 | 0.56561 | 0.060385 | not claimed |
| JTR_fixed_04__shift_-10m / 1-2 | 15 | 0.61874 | 0.99863 | -0.20088 | not claimed |
| JTR_fixed_04__shift_-10m / 2-inf | 1 | 0.88492 | 0.013408 | 0.41788 | not claimed |
| JTR_fixed_04__shift_-10m / missing_own_geometry | 12 | 0.29832 | 0.84195 | -0.39562 | not claimed |
| JTR_fixed_04__shift_+10m / 0-0.25 | 76 | 0.32951 | 0.36908 | 0.012952 | not claimed |
| JTR_fixed_04__shift_+10m / 0.25-0.5 | 202 | 0.44144 | 0.48716 | 0.021756 | [-0.073498, 0.11988] |
| JTR_fixed_04__shift_+10m / 0.5-1 | 85 | 0.53866 | 0.60839 | 0.0011621 | not claimed |
| JTR_fixed_04__shift_+10m / 1-2 | 16 | 0.63136 | 0.91251 | -0.10413 | not claimed |
| JTR_fixed_04__shift_+10m / 2-inf | 2 | 0.49087 | 0.98552 | -0.74189 | not claimed |
| JTR_fixed_04__shift_+10m / missing_own_geometry | 11 | 0.29935 | 0.87914 | -0.41959 | not claimed |
| OR5__shift_-10m / 0-0.25 | 391 | 0.44344 | 0.52138 | -0.0069819 | [-0.069201, 0.061468] |
| OR5__shift_-10m / 0.25-0.5 | 1 | 0.99096 | 0.55087 | 0.44235 | not claimed |
| OR5__shift_-10m / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 0-0.25 | 302 | 0.40723 | 0.44675 | 0.015929 | [-0.053235, 0.087174] |
| OR5__shift_+10m / 0.25-0.5 | 88 | 0.57057 | 0.7752 | -0.087026 | not claimed |
| OR5__shift_+10m / 0.5-1 | 2 | 0.59217 | 0.63732 | 0.28004 | not claimed |
| OR5__shift_+10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 0-0.25 | 177 | 0.34951 | 0.39899 | 0.0069296 | [-0.068031, 0.075363] |
| OR15__shift_-10m / 0.25-0.5 | 180 | 0.51909 | 0.58536 | -0.009351 | [-0.12314, 0.1001] |
| OR15__shift_-10m / 0.5-1 | 34 | 0.54711 | 0.76536 | 0.004414 | not claimed |
| OR15__shift_-10m / 1-2 | 1 | 0.47506 | 2.4014 | -1.981 | not claimed |
| OR15__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / 0-0.25 | 121 | 0.32187 | 0.36353 | 0.0065978 | [-0.057541, 0.067528] |
| OR15__shift_+10m / 0.25-0.5 | 212 | 0.44393 | 0.55487 | -0.027526 | [-0.12425, 0.067165] |
| OR15__shift_+10m / 0.5-1 | 57 | 0.71112 | 0.7171 | 0.063646 | not claimed |
| OR15__shift_+10m / 1-2 | 2 | 0.3922 | 0.95877 | -0.43905 | not claimed |
| OR15__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0-0.25 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 1-2 | 392 | 0.44484 | 0.52146 | -0.0058356 | [-0.06704, 0.062862] |
| prior_RTH_preopen / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 0-0.25 | 167 | 0.35161 | 0.39093 | 0.018182 | [-0.05853, 0.080799] |
| OR_activity_1_2 / 0.25-0.5 | 181 | 0.51412 | 0.56656 | 0.014384 | [-0.10351, 0.13324] |
| OR_activity_1_2 / 0.5-1 | 28 | 0.61309 | 0.83803 | -0.048606 | not claimed |
| OR_activity_1_2 / 1-2 | 1 | 0.49257 | 0.75743 | 0.16337 | not claimed |
| OR_activity_1_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / missing_own_geometry | 15 | 0.32953 | 0.82372 | -0.44867 | not claimed |
| OR_activity_1_1 / 0-0.25 | 65 | 0.30813 | 0.36945 | 0.00072367 | not claimed |
| OR_activity_1_1 / 0.25-0.5 | 228 | 0.40855 | 0.47469 | 0.012842 | [-0.047743, 0.080801] |
| OR_activity_1_1 / 0.5-1 | 70 | 0.7119 | 0.77301 | 0.0086147 | not claimed |
| OR_activity_1_1 / 1-2 | 5 | 0.71668 | 0.79279 | -0.048059 | not claimed |
| OR_activity_1_1 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_1 / missing_own_geometry | 24 | 0.32432 | 0.58721 | -0.23439 | not claimed |
| OR_activity_3_2 / 0-0.25 | 28 | 0.27246 | 0.33373 | -0.045237 | not claimed |
| OR_activity_3_2 / 0.25-0.5 | 147 | 0.36375 | 0.46258 | -0.017845 | [-0.10353, 0.062453] |
| OR_activity_3_2 / 0.5-1 | 98 | 0.57969 | 0.67675 | 0.004475 | not claimed |
| OR_activity_3_2 / 1-2 | 9 | 0.77794 | 0.8686 | 0.14546 | not claimed |
| OR_activity_3_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_3_2 / missing_own_geometry | 110 | 0.44968 | 0.48117 | -0.0013223 | [-0.12222, 0.12205] |

| Paired clocks | Common eligible dates | Width difference (ticks) | Availability difference (minutes) |
|---|---:|---:|---:|
| JTR_fixed_04 minus JTR_fixed_04__shift_-10m | 381 | 6.296587926509186 | 10.0 |
| JTR_fixed_04 minus JTR_fixed_04__shift_+10m | 381 | -8.561679790026247 | -10.0 |
| JTR_fixed_04 minus OR_activity_1_2 | 376 | 184.10638297872342 | -36.726063829787236 |
| JTR_fixed_04 minus OR_activity_1_1 | 369 | 59.50406504065041 | -45.200542005420054 |
| JTR_fixed_04 minus OR_activity_3_2 | 283 | -56.8339222614841 | -51.908127208480565 |
| OR5 minus OR5__shift_-10m | 393 | 249.42493638676845 | 10.0 |
| OR5 minus OR5__shift_+10m | 393 | 76.62595419847328 | -10.0 |
| OR5 minus OR_activity_1_2 | 378 | -34.21164021164021 | -1.7936507936507937 |
| OR5 minus OR_activity_1_1 | 369 | -160.56639566395663 | -10.200542005420054 |
| OR5 minus OR_activity_3_2 | 283 | -272.1519434628975 | -16.908127208480565 |
| OR15 minus OR15__shift_-10m | 393 | 129.3969465648855 | 10.0 |
| OR15 minus OR15__shift_+10m | 393 | 50.89821882951654 | -10.0 |
| OR15 minus OR_activity_1_2 | 378 | 130.65608465608466 | 8.206349206349206 |
| OR15 minus OR_activity_1_1 | 369 | 5.2411924119241196 | -0.2005420054200542 |
| OR15 minus OR_activity_3_2 | 283 | -92.29681978798587 | -6.908127208480566 |

#### JTR transition windows — training_2020_2022

- NQ: 756 dates. Source-window identification {'compatible_ambiguous': 461, 'no_event': 263, 'jtr_not_known_before_turn': 16, 'contract_identity_unresolved': 13, 'definite_print': 3}. Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous.

#### JTR transition windows — development_2023_2024

- NQ: 502 dates. Source-window identification {'compatible_ambiguous': 301, 'no_event': 184, 'contract_identity_unresolved': 8, 'definite_print': 4, 'jtr_not_known_before_turn': 5}. Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous.

#### JTR transition windows — confirmation_2025_2026

- NQ: 418 dates. Source-window identification {'no_event': 140, 'compatible_ambiguous': 246, 'contract_identity_unresolved': 15, 'jtr_not_known_before_turn': 12, 'definite_print': 5}. Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous.

### original_nq2024_sensitivity

Intended root/date counts: NQ=252, ES=0.
Shards retained: 1. Original and corrected NQ2024 are never pooled.

#### Common-clock geometry — development_2023_2024

- NQ: 252 intended dates. Width × prior-vol controls keep the common target and date universe fixed.
  - `JTR_fixed_04`: 219 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR5`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR15`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `turn_source`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `turn_earlier`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `turn_later`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `JTR_fixed_04__shift_-10m`: 219 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `JTR_fixed_04__shift_+10m`: 219 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR5__shift_-10m`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR5__shift_+10m`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR15__shift_-10m`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR15__shift_+10m`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `prior_RTH_preopen`: 221 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR_activity_1_2`: 214 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR_activity_1_1`: 210 feature dates, 221 target dates, terminal mean 0.005670497338368639.
  - `OR_activity_3_2`: 147 feature dates, 221 target dates, terminal mean 0.005670497338368639.

| Clock / width-to-prior-range bin | Eligible dates | Mean up | Mean down | Mean terminal | Terminal 95% interval |
|---|---:|---:|---:|---:|---|
| JTR_fixed_04 / 0-0.25 | 51 | 0.38664 | 0.30944 | 0.11228 | not claimed |
| JTR_fixed_04 / 0.25-0.5 | 101 | 0.40729 | 0.53222 | -0.066615 | [-0.19621, 0.080669] |
| JTR_fixed_04 / 0.5-1 | 58 | 0.58372 | 0.74009 | -0.01967 | not claimed |
| JTR_fixed_04 / 1-2 | 8 | 1.0158 | 0.4957 | 0.62505 | not claimed |
| JTR_fixed_04 / 2-inf | 1 | 1.2437 | 0.36041 | 0.083756 | not claimed |
| JTR_fixed_04 / missing_own_geometry | 2 | 0.31917 | 1.5848 | -0.84423 | not claimed |
| OR5 / 0-0.25 | 151 | 0.41132 | 0.44521 | 0.01324 | [-0.083124, 0.11802] |
| OR5 / 0.25-0.5 | 59 | 0.61624 | 0.69398 | 0.038873 | not claimed |
| OR5 / 0.5-1 | 11 | 0.56828 | 1.0714 | -0.27632 | not claimed |
| OR5 / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / 0-0.25 | 78 | 0.39276 | 0.3659 | 0.04891 | not claimed |
| OR15 / 0.25-0.5 | 103 | 0.51072 | 0.54118 | 0.014222 | [-0.14114, 0.16143] |
| OR15 / 0.5-1 | 37 | 0.52138 | 0.89636 | -0.1065 | not claimed |
| OR15 / 1-2 | 3 | 0.72957 | 0.83667 | -0.028672 | not claimed |
| OR15 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 0-0.25 | 121 | 0.39183 | 0.42567 | -0.0040013 | [-0.12166, 0.11693] |
| turn_source / 0.25-0.5 | 89 | 0.53293 | 0.69949 | -0.015714 | not claimed |
| turn_source / 0.5-1 | 11 | 0.89799 | 0.5633 | 0.28508 | not claimed |
| turn_source / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / 0-0.25 | 107 | 0.38535 | 0.38347 | 0.015042 | [-0.10225, 0.1223] |
| turn_earlier / 0.25-0.5 | 87 | 0.57573 | 0.59238 | 0.055775 | not claimed |
| turn_earlier / 0.5-1 | 25 | 0.50598 | 1.0007 | -0.15178 | not claimed |
| turn_earlier / 1-2 | 2 | 0.37451 | 1.1854 | -0.7072 | not claimed |
| turn_earlier / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 0-0.25 | 150 | 0.43784 | 0.43164 | 0.046891 | [-0.042716, 0.15327] |
| turn_later / 0.25-0.5 | 66 | 0.51 | 0.81517 | -0.13752 | not claimed |
| turn_later / 0.5-1 | 5 | 1.0765 | 0.28206 | 0.65918 | not claimed |
| turn_later / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| JTR_fixed_04__shift_-10m / 0-0.25 | 50 | 0.37852 | 0.30636 | 0.093694 | not claimed |
| JTR_fixed_04__shift_-10m / 0.25-0.5 | 103 | 0.42396 | 0.53461 | -0.03964 | [-0.17913, 0.1163] |
| JTR_fixed_04__shift_-10m / 0.5-1 | 56 | 0.57083 | 0.73652 | -0.044522 | not claimed |
| JTR_fixed_04__shift_-10m / 1-2 | 9 | 0.91966 | 0.53318 | 0.5277 | not claimed |
| JTR_fixed_04__shift_-10m / 2-inf | 1 | 1.2437 | 0.36041 | 0.083756 | not claimed |
| JTR_fixed_04__shift_-10m / missing_own_geometry | 2 | 0.31917 | 1.5848 | -0.84423 | not claimed |
| JTR_fixed_04__shift_+10m / 0-0.25 | 50 | 0.36284 | 0.33955 | 0.053619 | not claimed |
| JTR_fixed_04__shift_+10m / 0.25-0.5 | 100 | 0.42352 | 0.50935 | -0.01835 | [-0.14797, 0.1402] |
| JTR_fixed_04__shift_+10m / 0.5-1 | 60 | 0.57029 | 0.74248 | -0.049807 | not claimed |
| JTR_fixed_04__shift_+10m / 1-2 | 8 | 1.0158 | 0.4957 | 0.62505 | not claimed |
| JTR_fixed_04__shift_+10m / 2-inf | 1 | 1.2437 | 0.36041 | 0.083756 | not claimed |
| JTR_fixed_04__shift_+10m / missing_own_geometry | 2 | 0.31917 | 1.5848 | -0.84423 | not claimed |
| OR5__shift_-10m / 0-0.25 | 221 | 0.47384 | 0.54279 | 0.0056705 | [-0.083922, 0.10225] |
| OR5__shift_-10m / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 0-0.25 | 186 | 0.43598 | 0.49696 | 0.0077101 | [-0.086386, 0.11816] |
| OR5__shift_+10m / 0.25-0.5 | 34 | 0.67455 | 0.78845 | -0.018857 | not claimed |
| OR5__shift_+10m / 0.5-1 | 1 | 0.69157 | 0.71566 | 0.46024 | not claimed |
| OR5__shift_+10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 0-0.25 | 129 | 0.38806 | 0.41852 | -0.0043592 | [-0.10326, 0.099214] |
| OR15__shift_-10m / 0.25-0.5 | 76 | 0.58675 | 0.66829 | 0.041036 | not claimed |
| OR15__shift_-10m / 0.5-1 | 16 | 0.62917 | 0.94861 | -0.081451 | not claimed |
| OR15__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / 0-0.25 | 97 | 0.3773 | 0.4008 | 0.0047195 | not claimed |
| OR15__shift_+10m / 0.25-0.5 | 101 | 0.50073 | 0.66419 | -0.021376 | [-0.17337, 0.13327] |
| OR15__shift_+10m / 0.5-1 | 22 | 0.76682 | 0.6123 | 0.12338 | not claimed |
| OR15__shift_+10m / 1-2 | 1 | 0.67785 | 0.52517 | 0.23993 | not claimed |
| OR15__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0-0.25 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 1-2 | 221 | 0.47384 | 0.54279 | 0.0056705 | [-0.083922, 0.10225] |
| prior_RTH_preopen / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 0-0.25 | 122 | 0.38925 | 0.41956 | -0.0065123 | [-0.12043, 0.10386] |
| OR_activity_1_2 / 0.25-0.5 | 76 | 0.57044 | 0.63915 | 0.050567 | not claimed |
| OR_activity_1_2 / 0.5-1 | 14 | 0.67475 | 0.92738 | 0.019991 | not claimed |
| OR_activity_1_2 / 1-2 | 2 | 0.82124 | 1.0224 | 0.16003 | not claimed |
| OR_activity_1_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / missing_own_geometry | 7 | 0.39824 | 0.7381 | -0.34219 | not claimed |
| OR_activity_1_1 / 0-0.25 | 63 | 0.39109 | 0.35748 | 0.054582 | not claimed |
| OR_activity_1_1 / 0.25-0.5 | 110 | 0.47216 | 0.55844 | -0.008311 | [-0.15145, 0.13705] |
| OR_activity_1_1 / 0.5-1 | 35 | 0.55784 | 0.74743 | -0.037777 | not claimed |
| OR_activity_1_1 / 1-2 | 2 | 0.37451 | 1.1854 | -0.7072 | not claimed |
| OR_activity_1_1 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_1 / missing_own_geometry | 11 | 0.71537 | 0.67961 | 0.13321 | not claimed |
| OR_activity_3_2 / 0-0.25 | 26 | 0.34802 | 0.38732 | -0.057333 | not claimed |
| OR_activity_3_2 / 0.25-0.5 | 67 | 0.43867 | 0.49481 | 0.02549 | not claimed |
| OR_activity_3_2 / 0.5-1 | 51 | 0.54019 | 0.70957 | -0.020364 | not claimed |
| OR_activity_3_2 / 1-2 | 3 | 0.60455 | 0.82471 | -0.35421 | not claimed |
| OR_activity_3_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_3_2 / missing_own_geometry | 74 | 0.49887 | 0.51449 | 0.042394 | not claimed |

| Paired clocks | Common eligible dates | Width difference (ticks) | Availability difference (minutes) |
|---|---:|---:|---:|
| JTR_fixed_04 minus JTR_fixed_04__shift_-10m | 219 | 3.598173515981735 | 10.0 |
| JTR_fixed_04 minus JTR_fixed_04__shift_+10m | 219 | -4.068493150684931 | -10.0 |
| JTR_fixed_04 minus OR_activity_1_2 | 214 | 159.1728971962617 | -36.94859813084112 |
| JTR_fixed_04 minus OR_activity_1_1 | 210 | 72.15714285714286 | -45.92857142857143 |
| JTR_fixed_04 minus OR_activity_3_2 | 147 | 11.537414965986395 | -52.93877551020408 |
| OR5 minus OR5__shift_-10m | 221 | 147.92307692307693 | 10.0 |
| OR5 minus OR5__shift_+10m | 221 | 42.470588235294116 | -10.0 |
| OR5 minus OR_activity_1_2 | 214 | -25.7803738317757 | -1.9485981308411215 |
| OR5 minus OR_activity_1_1 | 210 | -113.46190476190476 | -10.928571428571429 |
| OR5 minus OR_activity_3_2 | 147 | -186.4625850340136 | -17.93877551020408 |
| OR15 minus OR15__shift_-10m | 221 | 84.1447963800905 | 10.0 |
| OR15 minus OR15__shift_+10m | 221 | 39.660633484162894 | -10.0 |
| OR15 minus OR_activity_1_2 | 214 | 80.85046728971963 | 8.051401869158878 |
| OR15 minus OR_activity_1_1 | 210 | -6.5476190476190474 | -0.9285714285714286 |
| OR15 minus OR_activity_3_2 | 147 | -66.3265306122449 | -7.938775510204081 |

#### JTR transition windows — development_2023_2024

- NQ: 252 dates. Source-window identification {'compatible_ambiguous': 136, 'no_event': 84, 'definite_print': 3, 'jtr_not_known_before_turn': 2, 'contract_identity_unresolved': 27}. Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous.

## Existing annual reports

Per-year path/formation statistics already exist on the extract shards and are not rerun.

- development narrative
- development source_sensitivity_narrative
- development NQ 2020: retained year statistics artifact
- development NQ 2021: retained year statistics artifact
- development NQ 2022: retained year statistics artifact
- development NQ 2023: retained year statistics artifact
- development NQ 2024: retained year statistics artifact
- development ES 2020: retained year statistics artifact
- development ES 2021: retained year statistics artifact
- development ES 2022: retained year statistics artifact
- development ES 2023: retained year statistics artifact
- development ES 2024: retained year statistics artifact
- confirmation narrative
- confirmation NQ 2025: retained year statistics artifact
- confirmation NQ 2026: retained year statistics artifact
- confirmation ES 2025: retained year statistics artifact
- confirmation ES 2026: retained year statistics artifact

## Remaining Deliverable 1 source dependencies

- **event_label_absent**: JTR-09 10:00 news delay and ordinary/event-day labels are not in the retained Jumbo tables; timing is not event-conditioned.
- **undisclosed_86_46_criteria**: JTR-18/JTR-19 86.46% reversal criteria, denominators and timestamps are undisclosed. This module does not invent a replication.
- **auction_completed_windows_waiting_auction_block**: Activity-completed OR15 comparators are OHLC-volume clocks, not auction-completion certificates. Auction-completed windows remain blocked on the auction family.

## Resources

- CPU seconds: 71.118367831
- Peak RSS bytes: 958726144
- Output bytes: 23281580
- Table reads: 16; prepare_paths: 8; common adapter: 8
- Conditional groups: 8028; bootstrap metrics: 26832

Family statistics, Context, and Location remain incomplete. This report is not an all-family completion.



