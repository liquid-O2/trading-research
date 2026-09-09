# Verified performance repair, September 8, 2026

The carry and redundant-snapshot repairs are integrated and verified. They recovered **611 of the 650 previously blocked source/date windows (94%)**, increasing complete retained output from **2,939 to 3,550 of 3,589 windows (98.91%)**. All 167 physical file chains were processed; 163 finished completely. The two repair continuations took **19.71 minutes combined** and reused authenticated completed prefixes. These counts retain separate physical acquisitions, including overlapping monthly and weekly variants.

The remaining **39 windows** are precisely accounted for: four source reset-clock failures and 35 subsequent windows without valid same-file carry. Both production attempts retain their unsuccessful full-extraction status. This result closes the two diagnosed code defects; it does not establish complete extraction or the under-three-hour full research pipeline target.

| Registered run | Work completed | Elapsed | CPU-seconds | New output |
|---|---|---:|---:|---:|
| 30, original source attempt | 2,939 complete, 650 incomplete | 61.10 min | 49,746.324 | 41.451 GB |
| 33, lossless carry repair | 358 new, 2,939 reused | 10.73 min | 6,163.023 | 4.660 GB |
| 34, snapshot correction | 253 new, 3,297 reused | 8.98 min | 4,784.717 | 2.447 GB |

These runs have different remaining workloads, so the timings are **not a like-for-like speedup benchmark**. The direct performance gain is productive continuation without recomputing completed windows. Run34 used the existing 17-worker limit, reaped all 167 children, had complete CPU accounting and stayed inside every declared limit. Its peak observed aggregate RSS was 14.73 GB. The prior dispatch-order estimate remains an estimate; it is not promoted into a measured speedup.

The repair preserves original data and required contracts:

- Nonfinite terminal raw floats are serialized by exact IEEE-754 bits. Hashes are checked before decoding; finite legacy carries keep their existing representation. Audit32 retained all 33 original NaN cases and reproduced full ES/NQ failures with authenticated incoming carry before implementation. Run33 eliminated that failure class.
- A backward A/N/168 snapshot may follow a flags132 predecessor only when its finite BBO and sizes are identical, its instrument matches, and the physical rows are adjacent in the same source. The predecessor gap still invalidates the book and persists in carry. All original rows, clocks, flags and raw occupancy remain retained. Strict default handling and reset rejection remain unchanged.
- Retained output reuse permits only the two explicitly pinned prior producer implementations and the current implementation. Runtime, source coordinates, artifact hashes and carry adjacency still must match. Exact quote replay value and source-manifest checks remain mandatory.

Run33 passed 75 checks. Run34 ran 88 checks with zero failures/errors: **86 passed and two pre-existing compiled-backend checks were skipped** because the test phase precedes activation of that backend. The new lossless-float, malformed-encoding, gap-invalidation, split-batch, carry and identity-rejection checks all ran. Production then compiled and used the existing native backend and validated every newly completed window's quote replay. The native kernel itself was unchanged.

| Source acquisition | Failed date | Clock reversal | Later carry-dependent windows |
|---|---|---:|---:|
| ES `2020-06.parquet` | 2020-06-30 | C → R, 396,342,941 ns | 0 |
| ES `2020-07.parquet` | 2020-07-01 | R → A, 903,843 ns | 30 (July 2–31) |
| NQ `2020-06-29.parquet` | 2020-06-30 | A → R, 499,920,433 ns | 5 (July 1–5) |
| NQ `2020-06.parquet` | 2020-06-30 | A → R, 499,920,433 ns | 0 |

These resets change book state, so they cannot use the redundant-snapshot rule. The two NQ acquisitions preserve the same event pair as separate source variants. Original all-field neighbors and exact physical row addresses are retained in run34. An independent Cursor reset review found no treatment that preserves exact chronology, state and carry by simply dropping, sorting or clamping these rows. A second timeboxed code review ended without a final verdict; it is not counted as passed review evidence. Supervisor review and the registered tests/production checks support the accepted repair.

The current [resume catalog](/workspace/trading-research/validation/AUCTION_FLOW_RETAINED_PRODUCTION_RECEIPTS_34.json) contains 3,550 unique, hash-checked success receipts. The runner now selects [V24](/workspace/trading-research/validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V24.json), which updates only that operational receipt catalog from the verified V23 execution configuration. Source producer code is unchanged after run34. No extra production retry is needed for the four known source contradictions.

Cumulative family usage is **34 of 36 explicitly authorized attempts**, **69,782.960226 of 192,000 CPU-seconds**, and **55,004,606,386 bytes of 256 GiB**. Prior failures and consumption remain retained. The user-authorized delivery deadline is 20:11:07 UTC. Downstream scientific family completion, Context and Location remain outside this performance repair; their missing work prevents an honest full-pipeline timing claim.

Evidence: [original production](/workspace/trading-research/reports/auction-flow-runs/eea751045b15bf143265901beda8afb8efade7074129706ebeb86417f79b73b7/execution.json), [original NaN diagnosis](/workspace/trading-research/reports/auction-flow-runs/a32c24c00e1698c484c315273f6ce0a282d67bd3f75010d664483c5067bdec52/worker.json), [carry verification](/workspace/trading-research/reports/auction-flow-runs/5a7c99b17c59e7423d0a0c5d4347b385d5539965c007e5117fadc53cccdbb615/execution.json), [snapshot verification](/workspace/trading-research/reports/auction-flow-runs/3f40daa9e281e30be879fbd6caf268cc667e7f4008be8e373b2e6d6a1cac9c84/execution.json), [complete run34 outcome](/workspace/trading-research/reports/auction-flow-runs/3f40daa9e281e30be879fbd6caf268cc667e7f4008be8e373b2e6d6a1cac9c84/worker.json), [current checkpoint](/workspace/planning/trading-research/state/CURRENT.json).
