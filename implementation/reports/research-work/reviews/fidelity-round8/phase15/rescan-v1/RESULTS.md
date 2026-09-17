# Rescan candidates v1 (one axis each), judged against B0.3 on the year folds

Queue: `run_rescan_queue.sh planning/phase-1-5/candidates/rescan_candidates_v1.json` (about 30 minutes a candidate on 8 workers); each candidate's run is merged into the baseline sessions by `evaluate_variants.py --rescan` and scored like a selection variant (mean daily difference of the executed list, frozen block bootstrap, Holm across the family's candidates in a fold).

| candidate | axis | mean daily diff (points) | folds promoted | reading |
| --- | --- | ---: | --- | --- |
| JJ-T2-judas-to-1000 (Judas window ends 10:00, from 10:15) | timing | -0.6 | none; -0.2 to -1.3 on every fold | the last quarter hour of the window carries a little; the window is not where the result is |
| JJ-T1-judas-to-1030 (Judas window ends 10:30, from 10:15) | timing | +0.1 | none; -1.1 to +0.8 on the folds | the window's end does not move the result either way |
| GB-O-major (objective rungs restricted to the prior day and week extremes, the Asia and London boxes, the 9-10 box; the sourced target rule of section 12) | objective | -4.8 | none; worse on every fold (-0.3 to -9.4) | the farther targets are reached less often on the pool (win rate 0.259 to 0.250, median R at target 5.5 to 5.8): his 200-point rewards come with his selection of the level, not from aiming farther on every admitted opportunity |
