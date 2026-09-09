# Jumbo timing and window descriptives

Study-local observables from retained formation/path tables. The common 10:01→actual-cash-close target is identical across declared clocks on a date; target-mean gaps are not clock gain. No Context increment, Location quality, clock ranking, or 86.46% replication is claimed.

## Source hypothesis limits

Declared study-local observables only. JTR-04 retains both the open-to-projection leg and a 09:40–09:50 mean/-0.5 opportunity; reported points are not a sample definition. JTR-07 compressed continuation and JTR-08 reversal share the same 09:40–09:50 clock; the window does not decide which path occurred. JTR-09 marks a failed apparent turn and a 10:00 news delay. Contact with EQ or a half-range extension is not a reversal, stop hunt, or inventory event. A 10-minute turn_* formation is not the full source pattern. Intra-minute sequence cannot be recovered from these three formed windows.

## Checks actually passed

10/10 recorded checks passed. Failed: none.

- `common_adapter_identity_reused`: pass
- `identical_common_target_no_clock_gain`: pass
- `missing_clock_preserves_intended_date`: pass
- `train_quantile_thresholds_independent_of_confirmation`: pass
- `source_variants_not_concatenated`: pass
- `paired_rates_same_dates_zero_event_retained`: pass
- `no_clock_ranking_emitted`: pass
- `context_increment_not_assessed`: pass
- `no_86_46_replication`: pass
- `jtr_hypothesis_limited_by_10m_ohlc`: pass

## Variants and denominators

### primary_corrected

Intended root/date counts: NQ=0, ES=1676.
Shards retained: 7. Original and corrected NQ2024 are never pooled.

#### Common-clock geometry — training_2020_2022

- ES: 756 intended dates. Width × prior-vol controls keep the common target and date universe fixed.
  - `JTR_fixed_04`: 719 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR5`: 726 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR15`: 724 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `turn_source`: 724 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `turn_earlier`: 724 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `turn_later`: 727 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `JTR_fixed_04__shift_-10m`: 719 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `JTR_fixed_04__shift_+10m`: 719 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR5__shift_-10m`: 723 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR5__shift_+10m`: 724 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR15__shift_-10m`: 722 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR15__shift_+10m`: 724 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `prior_RTH_preopen`: 727 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR_activity_1_2`: 672 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR_activity_1_1`: 647 feature dates, 726 target dates, terminal mean -0.007469255568323531.
  - `OR_activity_3_2`: 458 feature dates, 726 target dates, terminal mean -0.007469255568323531.

| Clock / width-to-prior-range bin | Eligible dates | Mean up | Mean down | Mean terminal | Terminal 95% interval |
|---|---:|---:|---:|---:|---|
| JTR_fixed_04 / 0-0.25 | 140 | 0.36856 | 0.41529 | -0.012716 | [-0.11161, 0.084752] |
| JTR_fixed_04 / 0.25-0.5 | 366 | 0.42023 | 0.50075 | -0.020625 | [-0.088944, 0.042279] |
| JTR_fixed_04 / 0.5-1 | 175 | 0.6134 | 0.68018 | 0.050376 | [-0.06886, 0.18359] |
| JTR_fixed_04 / 1-2 | 32 | 0.77911 | 1.0024 | -0.13285 | not claimed |
| JTR_fixed_04 / 2-inf | 6 | 1.1126 | 1.2693 | 0.0067115 | not claimed |
| JTR_fixed_04 / missing_own_geometry | 7 | 0.4948 | 0.39558 | -0.099754 | not claimed |
| OR5 / 0-0.25 | 510 | 0.41164 | 0.46122 | 0.0010312 | [-0.047236, 0.048299] |
| OR5 / 0.25-0.5 | 191 | 0.59061 | 0.74794 | -0.030444 | [-0.16069, 0.097206] |
| OR5 / 0.5-1 | 23 | 1.0207 | 0.95636 | 0.065751 | not claimed |
| OR5 / 1-2 | 1 | 1.0787 | 2.5169 | -1.3596 | not claimed |
| OR5 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / missing_own_geometry | 1 | 0.52129 | 0.3153 | -0.28654 | not claimed |
| OR15 / 0-0.25 | 248 | 0.3551 | 0.42209 | -0.032015 | [-0.09971, 0.037331] |
| OR15 / 0.25-0.5 | 390 | 0.48533 | 0.57655 | 0.0015107 | [-0.072332, 0.080425] |
| OR15 / 0.5-1 | 80 | 0.76816 | 0.77043 | 0.072068 | not claimed |
| OR15 / 1-2 | 5 | 1.4634 | 1.924 | -0.37478 | not claimed |
| OR15 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / missing_own_geometry | 3 | 0.5688 | 0.70732 | -0.65458 | not claimed |
| turn_source / 0-0.25 | 441 | 0.4221 | 0.45269 | 0.011651 | [-0.039904, 0.063904] |
| turn_source / 0.25-0.5 | 259 | 0.52617 | 0.69935 | -0.062931 | [-0.16244, 0.040404] |
| turn_source / 0.5-1 | 22 | 1.0152 | 0.89919 | 0.2902 | not claimed |
| turn_source / 1-2 | 1 | 1.3529 | 0.23529 | 1.3176 | not claimed |
| turn_source / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / missing_own_geometry | 3 | 0.5688 | 0.70732 | -0.65458 | not claimed |
| turn_earlier / 0-0.25 | 350 | 0.37325 | 0.43811 | -0.022994 | [-0.083878, 0.03319] |
| turn_earlier / 0.25-0.5 | 315 | 0.5149 | 0.62141 | 0.0031882 | [-0.08789, 0.096665] |
| turn_earlier / 0.5-1 | 54 | 0.86837 | 0.83205 | 0.062891 | not claimed |
| turn_earlier / 1-2 | 4 | 1.5971 | 1.6929 | 0.047147 | not claimed |
| turn_earlier / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / missing_own_geometry | 3 | 0.5688 | 0.70732 | -0.65458 | not claimed |
| turn_later / 0-0.25 | 525 | 0.43034 | 0.47013 | 0.0052845 | [-0.047601, 0.058294] |
| turn_later / 0.25-0.5 | 174 | 0.52881 | 0.74796 | -0.080362 | [-0.20532, 0.050816] |
| turn_later / 0.5-1 | 23 | 1.1702 | 0.873 | 0.31745 | not claimed |
| turn_later / 1-2 | 4 | 0.74039 | 1.467 | -0.37885 | not claimed |
| turn_later / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| JTR_fixed_04__shift_-10m / 0-0.25 | 154 | 0.34984 | 0.4209 | -0.029133 | [-0.11179, 0.054623] |
| JTR_fixed_04__shift_-10m / 0.25-0.5 | 370 | 0.44866 | 0.49972 | 0.0083749 | [-0.056168, 0.071613] |
| JTR_fixed_04__shift_-10m / 0.5-1 | 158 | 0.59234 | 0.71872 | -0.0057952 | [-0.13905, 0.13256] |
| JTR_fixed_04__shift_-10m / 1-2 | 31 | 0.78102 | 0.94355 | -0.079395 | not claimed |
| JTR_fixed_04__shift_-10m / 2-inf | 6 | 1.1126 | 1.2693 | 0.0067115 | not claimed |
| JTR_fixed_04__shift_-10m / missing_own_geometry | 7 | 0.4948 | 0.39558 | -0.099754 | not claimed |
| JTR_fixed_04__shift_+10m / 0-0.25 | 134 | 0.33448 | 0.41981 | -0.058884 | [-0.15276, 0.032438] |
| JTR_fixed_04__shift_+10m / 0.25-0.5 | 365 | 0.43358 | 0.48887 | 0.0090183 | [-0.058342, 0.075059] |
| JTR_fixed_04__shift_+10m / 0.5-1 | 179 | 0.5985 | 0.69652 | 0.010333 | [-0.11646, 0.14298] |
| JTR_fixed_04__shift_+10m / 1-2 | 34 | 0.78068 | 0.89127 | 0.001384 | not claimed |
| JTR_fixed_04__shift_+10m / 2-inf | 7 | 1.0863 | 1.4948 | -0.28889 | not claimed |
| JTR_fixed_04__shift_+10m / missing_own_geometry | 7 | 0.4948 | 0.39558 | -0.099754 | not claimed |
| OR5__shift_-10m / 0-0.25 | 718 | 0.47369 | 0.55111 | -0.0088001 | [-0.058862, 0.044687] |
| OR5__shift_-10m / 0.25-0.5 | 4 | 1.3565 | 1.2392 | 0.63547 | not claimed |
| OR5__shift_-10m / 0.5-1 | 1 | 0.57647 | 0.12941 | 0.31765 | not claimed |
| OR5__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / missing_own_geometry | 3 | 0.5688 | 0.70732 | -0.65458 | not claimed |
| OR5__shift_+10m / 0-0.25 | 611 | 0.44665 | 0.50912 | 0.0012866 | [-0.047252, 0.051781] |
| OR5__shift_+10m / 0.25-0.5 | 110 | 0.64665 | 0.79188 | -0.034111 | [-0.24489, 0.17589] |
| OR5__shift_+10m / 0.5-1 | 2 | 1.0393 | 1.3029 | -0.24644 | not claimed |
| OR5__shift_+10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / missing_own_geometry | 3 | 0.5688 | 0.70732 | -0.65458 | not claimed |
| OR15__shift_-10m / 0-0.25 | 459 | 0.40354 | 0.44258 | 0.0048237 | [-0.043383, 0.053162] |
| OR15__shift_-10m / 0.25-0.5 | 231 | 0.55895 | 0.71006 | -0.021352 | [-0.12498, 0.088507] |
| OR15__shift_-10m / 0.5-1 | 30 | 0.98749 | 0.92 | 0.090107 | not claimed |
| OR15__shift_-10m / 1-2 | 2 | 0.68218 | 2.9638 | -2.0905 | not claimed |
| OR15__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / missing_own_geometry | 4 | 0.62154 | 0.55296 | -0.30666 | not claimed |
| OR15__shift_+10m / 0-0.25 | 325 | 0.40752 | 0.42596 | 0.017116 | [-0.041095, 0.071843] |
| OR15__shift_+10m / 0.25-0.5 | 344 | 0.49949 | 0.60985 | -0.024295 | [-0.096097, 0.052235] |
| OR15__shift_+10m / 0.5-1 | 48 | 0.57658 | 0.97737 | -0.22378 | not claimed |
| OR15__shift_+10m / 1-2 | 6 | 2.3612 | 0.94096 | 1.6795 | not claimed |
| OR15__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / missing_own_geometry | 3 | 0.5688 | 0.70732 | -0.65458 | not claimed |
| prior_RTH_preopen / 0-0.25 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 1-2 | 726 | 0.47909 | 0.55497 | -0.0074693 | [-0.059032, 0.046546] |
| prior_RTH_preopen / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 0-0.25 | 402 | 0.38799 | 0.4572 | -0.024988 | [-0.078954, 0.028538] |
| OR_activity_1_2 / 0.25-0.5 | 240 | 0.57902 | 0.66091 | 0.012156 | [-0.1034, 0.12233] |
| OR_activity_1_2 / 0.5-1 | 27 | 0.90606 | 0.91049 | 0.12689 | not claimed |
| OR_activity_1_2 / 1-2 | 3 | 0.75914 | 2.0628 | -1.2705 | not claimed |
| OR_activity_1_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / missing_own_geometry | 54 | 0.48413 | 0.55039 | 0.03871 | not claimed |
| OR_activity_1_1 / 0-0.25 | 219 | 0.35132 | 0.40736 | -0.016042 | [-0.083064, 0.050297] |
| OR_activity_1_1 / 0.25-0.5 | 350 | 0.49561 | 0.58478 | -0.016697 | [-0.096628, 0.066868] |
| OR_activity_1_1 / 0.5-1 | 74 | 0.75107 | 0.74126 | 0.10425 | not claimed |
| OR_activity_1_1 / 1-2 | 4 | 1.5971 | 1.6929 | 0.047147 | not claimed |
| OR_activity_1_1 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_1 / missing_own_geometry | 79 | 0.44873 | 0.59999 | -0.050241 | not claimed |
| OR_activity_3_2 / 0-0.25 | 92 | 0.34307 | 0.41639 | -0.056727 | not claimed |
| OR_activity_3_2 / 0.25-0.5 | 269 | 0.41185 | 0.52826 | -0.035313 | [-0.10291, 0.037425] |
| OR_activity_3_2 / 0.5-1 | 88 | 0.68461 | 0.75899 | -0.028062 | not claimed |
| OR_activity_3_2 / 1-2 | 9 | 1.2141 | 1.1006 | 0.1692 | not claimed |
| OR_activity_3_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_3_2 / missing_own_geometry | 268 | 0.50111 | 0.54404 | 0.038217 | [-0.04391, 0.11813] |

| Paired clocks | Common eligible dates | Width difference (ticks) | Availability difference (minutes) |
|---|---:|---:|---:|
| JTR_fixed_04 minus JTR_fixed_04__shift_-10m | 719 | 2.129346314325452 | 10.0 |
| JTR_fixed_04 minus JTR_fixed_04__shift_+10m | 719 | -1.4867872044506258 | -10.0 |
| JTR_fixed_04 minus OR_activity_1_2 | 668 | 42.49550898203593 | -36.98203592814371 |
| JTR_fixed_04 minus OR_activity_1_1 | 644 | 25.847826086956523 | -45.50931677018634 |
| JTR_fixed_04 minus OR_activity_3_2 | 456 | 15.640350877192983 | -51.53728070175438 |
| OR5 minus OR5__shift_-10m | 723 | 28.471645919778698 | 10.0 |
| OR5 minus OR5__shift_+10m | 724 | 7.933701657458563 | -10.0 |
| OR5 minus OR_activity_1_2 | 672 | -5.150297619047619 | -1.9776785714285714 |
| OR5 minus OR_activity_1_1 | 647 | -21.290571870170016 | -10.513137557959814 |
| OR5 minus OR_activity_3_2 | 458 | -36.299126637554586 | -16.554585152838428 |
| OR15 minus OR15__shift_-10m | 722 | 17.094182825484765 | 10.0 |
| OR15 minus OR15__shift_+10m | 724 | 5.459944751381215 | -10.0 |
| OR15 minus OR_activity_1_2 | 671 | 16.95827123695976 | 8.019374068554397 |
| OR15 minus OR_activity_1_1 | 647 | 0.8871715610510046 | -0.5131375579598145 |
| OR15 minus OR_activity_3_2 | 458 | -11.102620087336245 | -6.554585152838428 |

#### Common-clock geometry — development_2023_2024

- ES: 502 intended dates. Width × prior-vol controls keep the common target and date universe fixed.
  - `JTR_fixed_04`: 481 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR5`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR15`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `turn_source`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `turn_earlier`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `turn_later`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `JTR_fixed_04__shift_-10m`: 481 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `JTR_fixed_04__shift_+10m`: 481 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR5__shift_-10m`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR5__shift_+10m`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR15__shift_-10m`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR15__shift_+10m`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `prior_RTH_preopen`: 486 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR_activity_1_2`: 466 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR_activity_1_1`: 451 feature dates, 486 target dates, terminal mean 0.0035822265841963224.
  - `OR_activity_3_2`: 330 feature dates, 486 target dates, terminal mean 0.0035822265841963224.

| Clock / width-to-prior-range bin | Eligible dates | Mean up | Mean down | Mean terminal | Terminal 95% interval |
|---|---:|---:|---:|---:|---|
| JTR_fixed_04 / 0-0.25 | 109 | 0.32669 | 0.39748 | -0.01892 | [-0.11216, 0.080572] |
| JTR_fixed_04 / 0.25-0.5 | 222 | 0.45884 | 0.55074 | -0.00024232 | [-0.097959, 0.087776] |
| JTR_fixed_04 / 0.5-1 | 123 | 0.62013 | 0.73528 | -0.05238 | [-0.2586, 0.13516] |
| JTR_fixed_04 / 1-2 | 25 | 0.93419 | 0.58121 | 0.39596 | not claimed |
| JTR_fixed_04 / 2-inf | 2 | 0.86411 | 1.3185 | 0.28442 | not claimed |
| JTR_fixed_04 / missing_own_geometry | 5 | 0.31537 | 0.68952 | -0.0336 | not claimed |
| OR5 / 0-0.25 | 364 | 0.45274 | 0.50066 | 0.020497 | [-0.062557, 0.10392] |
| OR5 / 0.25-0.5 | 115 | 0.5802 | 0.7811 | -0.091471 | [-0.25136, 0.075003] |
| OR5 / 0.5-1 | 6 | 1.2789 | 0.68229 | 0.79484 | not claimed |
| OR5 / 1-2 | 1 | 1.2121 | 0.48485 | 0.030303 | not claimed |
| OR5 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / 0-0.25 | 214 | 0.38549 | 0.42905 | 0.0083933 | [-0.073698, 0.098528] |
| OR15 / 0.25-0.5 | 233 | 0.5483 | 0.64852 | -0.0077075 | [-0.14209, 0.1225] |
| OR15 / 0.5-1 | 36 | 0.69945 | 0.85661 | -0.026372 | not claimed |
| OR15 / 1-2 | 3 | 1.6589 | 0.96118 | 0.89668 | not claimed |
| OR15 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 0-0.25 | 341 | 0.44769 | 0.49319 | 0.012312 | [-0.070628, 0.085399] |
| turn_source / 0.25-0.5 | 131 | 0.58895 | 0.69523 | -0.0084317 | [-0.1548, 0.14391] |
| turn_source / 0.5-1 | 13 | 0.73926 | 1.1421 | -0.12567 | not claimed |
| turn_source / 1-2 | 1 | 0.98246 | 2.5439 | 0.2807 | not claimed |
| turn_source / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / 0-0.25 | 289 | 0.42294 | 0.45075 | 0.036633 | [-0.038786, 0.11482] |
| turn_earlier / 0.25-0.5 | 173 | 0.57157 | 0.72645 | -0.065088 | [-0.2245, 0.08492] |
| turn_earlier / 0.5-1 | 22 | 0.77723 | 0.80333 | 0.095602 | not claimed |
| turn_earlier / 1-2 | 2 | 1.0973 | 1.5144 | 0.1555 | not claimed |
| turn_earlier / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 0-0.25 | 364 | 0.45278 | 0.51153 | 0.024212 | [-0.043164, 0.092298] |
| turn_later / 0.25-0.5 | 110 | 0.57259 | 0.7575 | -0.11934 | [-0.36361, 0.087035] |
| turn_later / 0.5-1 | 12 | 1.0508 | 0.59356 | 0.5046 | not claimed |
| turn_later / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| JTR_fixed_04__shift_-10m / 0-0.25 | 114 | 0.33709 | 0.41174 | -0.016366 | [-0.1206, 0.086312] |
| JTR_fixed_04__shift_-10m / 0.25-0.5 | 222 | 0.46354 | 0.53866 | 0.01443 | [-0.076542, 0.099869] |
| JTR_fixed_04__shift_-10m / 0.5-1 | 117 | 0.63253 | 0.74799 | -0.059998 | [-0.2737, 0.13139] |
| JTR_fixed_04__shift_-10m / 1-2 | 26 | 0.837 | 0.63548 | 0.27009 | not claimed |
| JTR_fixed_04__shift_-10m / 2-inf | 2 | 0.86411 | 1.3185 | 0.28442 | not claimed |
| JTR_fixed_04__shift_-10m / missing_own_geometry | 5 | 0.31537 | 0.68952 | -0.0336 | not claimed |
| JTR_fixed_04__shift_+10m / 0-0.25 | 106 | 0.33364 | 0.39848 | -0.0079673 | [-0.10129, 0.094045] |
| JTR_fixed_04__shift_+10m / 0.25-0.5 | 220 | 0.44919 | 0.54118 | -0.0063376 | [-0.10278, 0.086587] |
| JTR_fixed_04__shift_+10m / 0.5-1 | 126 | 0.61587 | 0.72599 | -0.033441 | [-0.24576, 0.13753] |
| JTR_fixed_04__shift_+10m / 1-2 | 27 | 0.93759 | 0.65877 | 0.28861 | not claimed |
| JTR_fixed_04__shift_+10m / 2-inf | 2 | 0.86411 | 1.3185 | 0.28442 | not claimed |
| JTR_fixed_04__shift_+10m / missing_own_geometry | 5 | 0.31537 | 0.68952 | -0.0336 | not claimed |
| OR5__shift_-10m / 0-0.25 | 481 | 0.48926 | 0.56615 | 0.0053437 | [-0.066339, 0.076648] |
| OR5__shift_-10m / 0.25-0.5 | 5 | 1.0148 | 0.86554 | -0.16588 | not claimed |
| OR5__shift_-10m / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 0-0.25 | 443 | 0.48039 | 0.53798 | 0.016887 | [-0.061908, 0.093826] |
| OR5__shift_+10m / 0.25-0.5 | 39 | 0.58885 | 0.85511 | -0.21636 | not claimed |
| OR5__shift_+10m / 0.5-1 | 3 | 1.2155 | 0.80876 | 0.80566 | not claimed |
| OR5__shift_+10m / 1-2 | 1 | 0.98246 | 2.5439 | 0.2807 | not claimed |
| OR5__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 0-0.25 | 317 | 0.44033 | 0.47112 | 0.032553 | [-0.040284, 0.10648] |
| OR15__shift_-10m / 0.25-0.5 | 151 | 0.56091 | 0.74367 | -0.066596 | [-0.24442, 0.10279] |
| OR15__shift_-10m / 0.5-1 | 17 | 0.87729 | 0.85406 | 0.085137 | not claimed |
| OR15__shift_-10m / 1-2 | 1 | 1.2121 | 0.48485 | 0.030303 | not claimed |
| OR15__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / 0-0.25 | 270 | 0.40733 | 0.45831 | 0.0085185 | [-0.068751, 0.079512] |
| OR15__shift_+10m / 0.25-0.5 | 183 | 0.57259 | 0.69278 | -0.028201 | [-0.18382, 0.1014] |
| OR15__shift_+10m / 0.5-1 | 30 | 0.78375 | 0.74019 | 0.1296 | not claimed |
| OR15__shift_+10m / 1-2 | 3 | 0.7107 | 1.3053 | 0.23796 | not claimed |
| OR15__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0-0.25 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 1-2 | 486 | 0.49466 | 0.56923 | 0.0035822 | [-0.067176, 0.074255] |
| prior_RTH_preopen / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 0-0.25 | 325 | 0.42512 | 0.48994 | 0.0037631 | [-0.070783, 0.078012] |
| OR_activity_1_2 / 0.25-0.5 | 126 | 0.59025 | 0.69457 | -0.012274 | [-0.15662, 0.14004] |
| OR_activity_1_2 / 0.5-1 | 14 | 0.91949 | 0.76864 | 0.39715 | not claimed |
| OR_activity_1_2 / 1-2 | 1 | 1.2121 | 0.48485 | 0.030303 | not claimed |
| OR_activity_1_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / missing_own_geometry | 20 | 0.68935 | 0.93268 | -0.1763 | not claimed |
| OR_activity_1_1 / 0-0.25 | 193 | 0.37963 | 0.43546 | -0.0077623 | [-0.097611, 0.085985] |
| OR_activity_1_1 / 0.25-0.5 | 218 | 0.53434 | 0.62316 | 0.0026488 | [-0.10398, 0.11122] |
| OR_activity_1_1 / 0.5-1 | 38 | 0.74677 | 0.69667 | 0.11616 | not claimed |
| OR_activity_1_1 / 1-2 | 2 | 1.0973 | 1.5144 | 0.1555 | not claimed |
| OR_activity_1_1 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_1 / missing_own_geometry | 35 | 0.57368 | 0.77859 | -0.05895 | not claimed |
| OR_activity_3_2 / 0-0.25 | 95 | 0.33033 | 0.38242 | -0.025626 | not claimed |
| OR_activity_3_2 / 0.25-0.5 | 187 | 0.50266 | 0.57675 | 0.0020789 | [-0.111, 0.11352] |
| OR_activity_3_2 / 0.5-1 | 46 | 0.6828 | 0.68754 | 0.061002 | not claimed |
| OR_activity_3_2 / 1-2 | 2 | 1.8824 | 1.1993 | 1.3299 | not claimed |
| OR_activity_3_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_3_2 / missing_own_geometry | 156 | 0.51189 | 0.63101 | -0.010764 | [-0.17617, 0.13296] |

| Paired clocks | Common eligible dates | Width difference (ticks) | Availability difference (minutes) |
|---|---:|---:|---:|
| JTR_fixed_04 minus JTR_fixed_04__shift_-10m | 481 | 0.9958419958419958 | 10.0 |
| JTR_fixed_04 minus JTR_fixed_04__shift_+10m | 481 | -1.3305613305613306 | -10.0 |
| JTR_fixed_04 minus OR_activity_1_2 | 462 | 40.625541125541126 | -36.85064935064935 |
| JTR_fixed_04 minus OR_activity_1_1 | 448 | 27.200892857142858 | -45.58705357142857 |
| JTR_fixed_04 minus OR_activity_3_2 | 327 | 21.798165137614678 | -51.97553516819572 |
| OR5 minus OR5__shift_-10m | 486 | 21.90740740740741 | 10.0 |
| OR5 minus OR5__shift_+10m | 486 | 7.065843621399177 | -10.0 |
| OR5 minus OR_activity_1_2 | 466 | -2.718884120171674 | -1.8562231759656653 |
| OR5 minus OR_activity_1_1 | 451 | -16.254988913525498 | -10.596452328159645 |
| OR5 minus OR_activity_3_2 | 330 | -28.536363636363635 | -17.027272727272727 |
| OR15 minus OR15__shift_-10m | 486 | 11.25925925925926 | 10.0 |
| OR15 minus OR15__shift_+10m | 486 | 4.872427983539095 | -10.0 |
| OR15 minus OR_activity_1_2 | 466 | 13.714592274678111 | 8.143776824034335 |
| OR15 minus OR_activity_1_1 | 451 | 0.22838137472283815 | -0.5964523281596452 |
| OR15 minus OR_activity_3_2 | 330 | -9.56060606060606 | -7.027272727272727 |

#### Common-clock geometry — confirmation_2025_2026

- ES: 418 intended dates. Width × prior-vol controls keep the common target and date universe fixed.
  - `JTR_fixed_04`: 397 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR5`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR15`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `turn_source`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `turn_earlier`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `turn_later`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `JTR_fixed_04__shift_-10m`: 397 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `JTR_fixed_04__shift_+10m`: 397 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR5__shift_-10m`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR5__shift_+10m`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR15__shift_-10m`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR15__shift_+10m`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `prior_RTH_preopen`: 400 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR_activity_1_2`: 384 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR_activity_1_1`: 376 feature dates, 399 target dates, terminal mean 0.004569211729867734.
  - `OR_activity_3_2`: 293 feature dates, 399 target dates, terminal mean 0.004569211729867734.

| Clock / width-to-prior-range bin | Eligible dates | Mean up | Mean down | Mean terminal | Terminal 95% interval |
|---|---:|---:|---:|---:|---|
| JTR_fixed_04 / 0-0.25 | 81 | 0.32182 | 0.38516 | -0.037523 | not claimed |
| JTR_fixed_04 / 0.25-0.5 | 200 | 0.46848 | 0.50073 | 0.047815 | [-0.04759, 0.14645] |
| JTR_fixed_04 / 0.5-1 | 90 | 0.55154 | 0.67844 | -0.060157 | not claimed |
| JTR_fixed_04 / 1-2 | 24 | 0.72339 | 0.84347 | -0.005858 | not claimed |
| JTR_fixed_04 / 2-inf | 1 | 0.92806 | 0.52518 | 0.58273 | not claimed |
| JTR_fixed_04 / missing_own_geometry | 3 | 0.33437 | 0.088627 | 0.090458 | not claimed |
| OR5 / 0-0.25 | 286 | 0.4009 | 0.49341 | -0.027151 | [-0.094696, 0.040637] |
| OR5 / 0.25-0.5 | 104 | 0.62041 | 0.62525 | 0.07535 | [-0.066126, 0.26935] |
| OR5 / 0.5-1 | 9 | 1.0572 | 0.81061 | 0.19464 | not claimed |
| OR5 / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / 0-0.25 | 149 | 0.36143 | 0.38158 | 0.0112 | [-0.065198, 0.075573] |
| OR15 / 0.25-0.5 | 199 | 0.47775 | 0.58773 | -0.022255 | [-0.12471, 0.094367] |
| OR15 / 0.5-1 | 49 | 0.76479 | 0.75838 | 0.11093 | not claimed |
| OR15 / 1-2 | 2 | 1.1477 | 1.2317 | -0.42632 | not claimed |
| OR15 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15 / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 0-0.25 | 221 | 0.39493 | 0.4405 | -0.0068158 | [-0.079919, 0.06104] |
| turn_source / 0.25-0.5 | 161 | 0.54093 | 0.62531 | 0.018262 | [-0.086188, 0.1411] |
| turn_source / 0.5-1 | 17 | 0.84273 | 0.90662 | 0.022892 | not claimed |
| turn_source / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_source / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / 0-0.25 | 218 | 0.36408 | 0.44562 | -0.02457 | [-0.089691, 0.032708] |
| turn_earlier / 0.25-0.5 | 150 | 0.54307 | 0.61679 | 0.0074162 | [-0.13088, 0.16141] |
| turn_earlier / 0.5-1 | 30 | 0.86454 | 0.7487 | 0.22041 | not claimed |
| turn_earlier / 1-2 | 1 | 1.9293 | 1.3131 | -0.54545 | not claimed |
| turn_earlier / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_earlier / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 0-0.25 | 247 | 0.38223 | 0.45451 | -0.02733 | [-0.10088, 0.043788] |
| turn_later / 0.25-0.5 | 138 | 0.57959 | 0.65957 | 0.034368 | [-0.090581, 0.18412] |
| turn_later / 0.5-1 | 14 | 1.0215 | 0.72521 | 0.27362 | not claimed |
| turn_later / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| turn_later / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| JTR_fixed_04__shift_-10m / 0-0.25 | 89 | 0.31803 | 0.40539 | -0.069655 | not claimed |
| JTR_fixed_04__shift_-10m / 0.25-0.5 | 198 | 0.47382 | 0.50011 | 0.058943 | [-0.037881, 0.16477] |
| JTR_fixed_04__shift_-10m / 0.5-1 | 86 | 0.55487 | 0.70021 | -0.070443 | not claimed |
| JTR_fixed_04__shift_-10m / 1-2 | 22 | 0.76928 | 0.78757 | 0.070717 | not claimed |
| JTR_fixed_04__shift_-10m / 2-inf | 1 | 0.92806 | 0.52518 | 0.58273 | not claimed |
| JTR_fixed_04__shift_-10m / missing_own_geometry | 3 | 0.33437 | 0.088627 | 0.090458 | not claimed |
| JTR_fixed_04__shift_+10m / 0-0.25 | 75 | 0.33238 | 0.37428 | -0.021679 | not claimed |
| JTR_fixed_04__shift_+10m / 0.25-0.5 | 203 | 0.45297 | 0.50086 | 0.028302 | [-0.063825, 0.12673] |
| JTR_fixed_04__shift_+10m / 0.5-1 | 94 | 0.57656 | 0.68166 | -0.021777 | not claimed |
| JTR_fixed_04__shift_+10m / 1-2 | 23 | 0.68202 | 0.81847 | -0.04797 | not claimed |
| JTR_fixed_04__shift_+10m / 2-inf | 1 | 0.92806 | 0.52518 | 0.58273 | not claimed |
| JTR_fixed_04__shift_+10m / missing_own_geometry | 3 | 0.33437 | 0.088627 | 0.090458 | not claimed |
| OR5__shift_-10m / 0-0.25 | 396 | 0.46867 | 0.53603 | 4.9196e-05 | [-0.059392, 0.075966] |
| OR5__shift_-10m / 0.25-0.5 | 3 | 1.0336 | 0.3896 | 0.60121 | not claimed |
| OR5__shift_-10m / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 0-0.25 | 334 | 0.43812 | 0.4974 | 0.0060084 | [-0.05757, 0.07753] |
| OR5__shift_+10m / 0.25-0.5 | 63 | 0.64842 | 0.68443 | 0.015137 | not claimed |
| OR5__shift_+10m / 0.5-1 | 2 | 0.75603 | 2.0946 | -0.56866 | not claimed |
| OR5__shift_+10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR5__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 0-0.25 | 245 | 0.37581 | 0.45751 | -0.024007 | [-0.097058, 0.050608] |
| OR15__shift_-10m / 0.25-0.5 | 137 | 0.59882 | 0.63762 | 0.042041 | [-0.083624, 0.20454] |
| OR15__shift_-10m / 0.5-1 | 17 | 0.85781 | 0.82326 | 0.11442 | not claimed |
| OR15__shift_-10m / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_-10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / 0-0.25 | 162 | 0.36136 | 0.38521 | 0.016327 | [-0.056744, 0.087811] |
| OR15__shift_+10m / 0.25-0.5 | 194 | 0.51961 | 0.60967 | -0.0013772 | [-0.10302, 0.1141] |
| OR15__shift_+10m / 0.5-1 | 42 | 0.67479 | 0.76308 | -0.0053498 | not claimed |
| OR15__shift_+10m / 1-2 | 1 | 1.01 | 0.71 | -0.33 | not claimed |
| OR15__shift_+10m / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR15__shift_+10m / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0-0.25 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.25-0.5 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 0.5-1 | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / 1-2 | 399 | 0.47292 | 0.53493 | 0.0045692 | [-0.055122, 0.080427] |
| prior_RTH_preopen / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| prior_RTH_preopen / missing_own_geometry | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 0-0.25 | 246 | 0.38937 | 0.4582 | -0.019547 | [-0.093628, 0.049505] |
| OR_activity_1_2 / 0.25-0.5 | 118 | 0.60368 | 0.60335 | 0.10118 | [-0.017192, 0.25354] |
| OR_activity_1_2 / 0.5-1 | 19 | 0.84617 | 0.85839 | 0.095773 | not claimed |
| OR_activity_1_2 / 1-2 | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_2 / missing_own_geometry | 16 | 0.34998 | 0.82597 | -0.44542 | not claimed |
| OR_activity_1_1 / 0-0.25 | 134 | 0.36419 | 0.39626 | -0.0014545 | [-0.080251, 0.072846] |
| OR_activity_1_1 / 0.25-0.5 | 195 | 0.48082 | 0.54653 | 0.014168 | [-0.085841, 0.12314] |
| OR_activity_1_1 / 0.5-1 | 44 | 0.81997 | 0.79377 | 0.1851 | not claimed |
| OR_activity_1_1 / 1-2 | 2 | 1.043 | 1.6626 | -1.2426 | not claimed |
| OR_activity_1_1 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_1_1 / missing_own_geometry | 24 | 0.332 | 0.64647 | -0.26683 | not claimed |
| OR_activity_3_2 / 0-0.25 | 61 | 0.33247 | 0.3867 | -0.011334 | not claimed |
| OR_activity_3_2 / 0.25-0.5 | 160 | 0.46036 | 0.4819 | 0.012932 | [-0.093566, 0.11922] |
| OR_activity_3_2 / 0.5-1 | 67 | 0.72142 | 0.64948 | 0.16747 | not claimed |
| OR_activity_3_2 / 1-2 | 5 | 0.74592 | 1.4383 | -0.49105 | not claimed |
| OR_activity_3_2 / 2-inf | 0 | unavailable | unavailable | unavailable | not claimed |
| OR_activity_3_2 / missing_own_geometry | 106 | 0.40275 | 0.58527 | -0.078489 | [-0.20017, 0.061017] |

| Paired clocks | Common eligible dates | Width difference (ticks) | Availability difference (minutes) |
|---|---:|---:|---:|
| JTR_fixed_04 minus JTR_fixed_04__shift_-10m | 397 | 0.7304785894206549 | 10.0 |
| JTR_fixed_04 minus JTR_fixed_04__shift_+10m | 397 | -1.0 | -10.0 |
| JTR_fixed_04 minus OR_activity_1_2 | 383 | 53.485639686684074 | -36.54308093994778 |
| JTR_fixed_04 minus OR_activity_1_1 | 375 | 31.485333333333333 | -45.16 |
| JTR_fixed_04 minus OR_activity_3_2 | 292 | 14.945205479452055 | -51.3013698630137 |
| OR5 minus OR5__shift_-10m | 400 | 36.3575 | 10.0 |
| OR5 minus OR5__shift_+10m | 400 | 8.815 | -10.0 |
| OR5 minus OR_activity_1_2 | 384 | -4.838541666666667 | -1.5390625 |
| OR5 minus OR_activity_1_1 | 376 | -27.074468085106382 | -10.15691489361702 |
| OR5 minus OR_activity_3_2 | 293 | -46.515358361774744 | -16.30716723549488 |
| OR15 minus OR15__shift_-10m | 400 | 21.2775 | 10.0 |
| OR15 minus OR15__shift_+10m | 400 | 3.1075 | -10.0 |
| OR15 minus OR_activity_1_2 | 384 | 24.15625 | 8.4609375 |
| OR15 minus OR_activity_1_1 | 376 | 1.9680851063829787 | -0.15691489361702127 |
| OR15 minus OR_activity_3_2 | 293 | -14.040955631399317 | -6.30716723549488 |

#### JTR transition windows — training_2020_2022

- ES: 756 dates. Source-window identification {'compatible_ambiguous': 417, 'no_event': 301, 'definite_print': 17, 'jtr_not_known_before_turn': 8, 'contract_identity_unresolved': 13}. Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous.

#### JTR transition windows — development_2023_2024

- ES: 502 dates. Source-window identification {'compatible_ambiguous': 257, 'no_event': 220, 'definite_print': 12, 'contract_identity_unresolved': 8, 'jtr_not_known_before_turn': 5}. Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous.

#### JTR transition windows — confirmation_2025_2026

- ES: 418 dates. Source-window identification {'compatible_ambiguous': 243, 'no_event': 152, 'contract_identity_unresolved': 10, 'definite_print': 10, 'jtr_not_known_before_turn': 3}. Definite print requires literal O/H/L/C; range intersection alone is compatible/ambiguous.

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

- CPU seconds: 60.575472712
- Peak RSS bytes: 959131648
- Output bytes: 19398667
- Table reads: 14; prepare_paths: 7; common adapter: 7
- Conditional groups: 6690; bootstrap metrics: 22360

Family statistics, Context, and Location remain incomplete. This report is not an all-family completion.

