# REFILL-STUDY plausibility

| family | branch | sessions | episodes | pass/fail/unknown | pass_rate | eps_bound | rate_bound | in/out |
|---|---|---|---|---|---|---|---|---|
| REFILL-STUDY | touch_record | 15 | 3890 | 184/3706/0 | 0.047 | [80, 350] | [0.25, 0.6] | out |

## Per-date touches

| date | touches | hold | broke | hold_rate |
|---|---|---|---|---|
| 2020-01-02 | 92 | 14 | 78 | 0.152 |
| 2020-06-01 | 94 | 17 | 77 | 0.181 |
| 2020-11-02 | 592 | 24 | 568 | 0.041 |
| 2021-06-01 | 72 | 2 | 70 | 0.028 |
| 2021-11-01 | 257 | 0 | 257 | 0.000 |
| 2022-01-03 | 114 | 20 | 94 | 0.175 |
| 2022-06-01 | 6 | 0 | 6 | 0.000 |
| 2023-01-03 | 48 | 0 | 48 | 0.000 |
| 2023-11-06 | 492 | 18 | 474 | 0.037 |
| 2024-03-05 | 266 | 18 | 248 | 0.068 |
| 2024-11-01 | 428 | 6 | 422 | 0.014 |
| 2025-01-02 | 76 | 5 | 71 | 0.066 |
| 2025-06-02 | 278 | 8 | 270 | 0.029 |
| 2026-01-02 | 520 | 28 | 492 | 0.054 |
| 2026-06-01 | 555 | 24 | 531 | 0.043 |

REF pp.5-8: REF p.8 prints 42% hold on 41152 NQ and MNQ touches over 235 RTH sessions Dec 24-Nov 25. The hold tick cutoff is not printed. Phase 1.5 labels hold with OD HOLD_BOUNDARY_TICKS=8 inside 30 minutes on NQ only, on 15 calendar sessions that are not that 235-session window. The bound stays at 175 and 42%. The observed hold rate is the OD label on this slice, not a rewrite of the paper.
