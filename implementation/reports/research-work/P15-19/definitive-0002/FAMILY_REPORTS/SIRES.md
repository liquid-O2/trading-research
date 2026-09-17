# P15-19 exit study (E0 baseline) — SIRES

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001`. Every number below is a cell of `EXIT_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| SIRES | SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E1 | 870 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E2 | 898 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E3 | 833 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E4 | 801 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:clean_squeeze:M1:max_prior_contacts=0|E1 | 385 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:clean_squeeze:M1:max_prior_contacts=0|E2 | 389 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:clean_squeeze:M1:max_prior_contacts=0|E3 | 378 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:clean_squeeze:M1:max_prior_contacts=0|E4 | 372 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:defended_band_continuation:R1:dispersion=0.5|E1 | 277 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:defended_band_continuation:R1:dispersion=0.5|E2 | 277 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:defended_band_continuation:R1:dispersion=0.5|E3 | 277 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:defended_band_continuation:R1:dispersion=0.5|E4 | 277 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/SIRES.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| SIRES | P15-17 | retained_baseline | pass | 28 | 0 | support 2069 opps / 870 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 2128 opps / 898 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | rejected_by_evidence | pass | 71 | 0 | support 1979 opps / 833 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | rejected_by_evidence | pass | 106 | 0 | support 1883 opps / 801 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 4 | 0 | support 461 opps / 385 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 465 opps / 389 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 12 | 0 | support 451 opps / 378 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 18 | 0 | support 444 opps / 372 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 0 | 0 | support 293 opps / 277 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 0 | 0 | support 293 opps / 277 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 0 | 0 | support 293 opps / 277 days / 5 blocks; first attribution None; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 0 | 0 | support 293 opps / 277 days / 5 blocks; first attribution None; baseline retained |

## Multiplicity

Holm family of this decision stage: 72 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.003600 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E1 | 0.768462 | 1.000000 | 0.003600 | retained_baseline |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E2 | 0.191340 | 1.000000 | 0.003600 | rejected_by_evidence |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E3 | 0.026099 | 1.000000 | 0.003600 | rejected_by_evidence |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E4 | 0.265137 | 1.000000 | 0.003600 | rejected_by_evidence |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E1 | 0.577721 | 1.000000 | 0.003600 | retained_baseline |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E2 | 0.105745 | 1.000000 | 0.003600 | rejected_by_evidence |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E3 | 1.000000 | 1.000000 | 0.003600 | retained_baseline |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E4 | 1.000000 | 1.000000 | 0.003600 | retained_baseline |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E1 | 1.000000 | 1.000000 | 0.003600 | retained_baseline |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E2 | 1.000000 | 1.000000 | 0.003600 | retained_baseline |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E3 | 0.853357 | 1.000000 | 0.003600 | retained_baseline |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E4 | 0.901155 | 1.000000 | 0.003600 | retained_baseline |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E1 | 2069 | 2069 | 870 | 5 | pass | pass | 1.00 |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E2 | 2128 | 2128 | 898 | 5 | pass | pass | 1.00 |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E3 | 1979 | 1979 | 833 | 5 | pass | pass | 1.00 |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E4 | 1883 | 1883 | 801 | 5 | pass | pass | 1.00 |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E1 | 461 | 461 | 385 | 5 | pass | pass | 1.00 |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E2 | 465 | 465 | 389 | 5 | pass | pass | 1.00 |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E3 | 451 | 451 | 378 | 5 | pass | pass | 1.00 |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E4 | 444 | 444 | 372 | 5 | pass | pass | 1.00 |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E1 | 293 | 293 | 277 | 5 | pass | pass | 1.00 |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E2 | 293 | 293 | 277 | 5 | pass | pass | 1.00 |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E3 | 293 | 293 | 277 | 5 | pass | pass | 1.00 |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E4 | 293 | 293 | 277 | 5 | pass | pass | 1.00 |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E3 | EXIT | 0.2302 | 2290 | 2290 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E1 | absorption_reward_retest | EXIT | inactive_retained |  | no_improvement |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E2 | absorption_reward_retest | EXIT | inactive_retained |  | holm |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E3 | absorption_reward_retest | EXIT | inactive_retained |  | holm |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0|E4 | absorption_reward_retest | EXIT | inactive_retained |  | holm |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E1 | clean_squeeze | EXIT | inactive_retained |  | no_improvement |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E2 | clean_squeeze | EXIT | inactive_retained |  | holm |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E3 | clean_squeeze | EXIT | inactive_retained |  | no_improvement |
| SIRES:clean_squeeze:M1:max_prior_contacts=0|E4 | clean_squeeze | EXIT | inactive_retained |  | no_improvement |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E1 | defended_band_continuation | EXIT | inactive_retained |  | no_improvement |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E2 | defended_band_continuation | EXIT | inactive_retained |  | no_improvement |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E3 | defended_band_continuation | EXIT | inactive_retained |  | no_improvement |
| SIRES:defended_band_continuation:R1:dispersion=0.5|E4 | defended_band_continuation | EXIT | inactive_retained |  | no_improvement |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
