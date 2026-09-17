# JJ-TBR plausibility (15 stratified dates)

Sessions loaded: 15 / 15.

| branch | sessions | episodes | pass | fail | unknown | pass_rate | eps | sessions_with_pass | bound eps | bound pass_rate | in_bound |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| judas_outbound | 15 | 120 | 58 | 62 | 0 | 0.483 | 8.000 | 10/15 | [0, 2] | [0, 0.7] | out |
| judas_reversal | 15 | 1700 | 806 | 894 | 0 | 0.474 | 113.333 | 15/15 | [0, 4] | [0, 0.9] | out |
| single_extended | 15 | 1773 | 1215 | 558 | 0 | 0.685 | 118.200 | 15/15 | [0, 6] | [0, 0.5] | out |
| single_purged | 15 | 433 | 347 | 86 | 0 | 0.801 | 28.867 | 8/15 | [0, 6] | [0, 0.5] | out |
| internal_rotation | 15 | 3264 | 2002 | 1262 | 0 | 0.613 | 217.600 | 15/15 | [0, 8] | [0, 0.4] | out |
| extension_reaction | 15 | 30 | 9 | 21 | 0 | 0.300 | 2.000 | 8/15 | [0, 2] | [0, 0.5] | in |
| other_session | 15 | 856 | 374 | 482 | 0 | 0.437 | 57.067 | 15/15 | [0, 12] | [0, 0.5] | out |
| timed_pzone_reversal | 15 | 18 | 18 | 0 | 0 | 1.000 | 1.200 | 1/15 | [0, 6] | None | in |

## judas_outbound

violations=['episodes_per_session', 'session_frequency'] hottest_stage=context. This note is not a waiver.

Time-of-entry (pass, 30-minute ET): 09:30=58

## judas_reversal

violations=['episodes_per_session', 'session_frequency'] hottest_stage=context. This note is not a waiver.

Time-of-entry (pass, 30-minute ET): 09:00=145, 09:30=333, 10:00=198, 10:30=58, 11:00=26, 11:30=46

## single_extended

violations=['episodes_per_session', 'pass_rate', 'session_frequency'] hottest_stage=context. This note is not a waiver.

Time-of-entry (pass, 30-minute ET): 09:00=230, 09:30=565, 10:00=407, 10:30=13

## single_purged

violations=['episodes_per_session', 'pass_rate'] hottest_stage=context. This note is not a waiver.

Time-of-entry (pass, 30-minute ET): 09:30=163, 10:00=77, 10:30=43, 11:00=45, 11:30=18, 12:00=1

## internal_rotation

violations=['episodes_per_session', 'pass_rate', 'session_frequency'] hottest_stage=context. This note is not a waiver.

Time-of-entry (pass, 30-minute ET): 09:30=709, 10:00=454, 10:30=352, 11:00=167, 11:30=67, 12:00=59, 12:30=53, 13:00=28, 13:30=25, 14:00=30, 14:30=16, 15:00=6, 15:30=31, 16:00=5

## other_session

violations=['episodes_per_session', 'session_frequency', 'passes_per_side'] hottest_stage=context. This note is not a waiver.

Time-of-entry (pass, 30-minute ET): 02:00=18, 02:30=35, 03:00=112, 03:30=90, 04:00=60, 04:30=30, 05:00=18, 05:30=7, 06:00=4

