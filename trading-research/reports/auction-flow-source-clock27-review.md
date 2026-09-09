# Source clock check 27

The named `redundant_backward_snapshot_v1` source alternative passed 139 affected tests and completed the five source windows that failed in attempt 25. Each retained replay record matches every original field and exact physical row from audit 26. The policy retains raw rows, source addresses, counts and all-field fingerprints, and suppresses economic replay only for a backward A/N/168 snapshot immediately following a same-instrument A/M/C/128 row with an identical valid BBO. It does not reconstruct receive time or change original timestamps. The strict alternative remains unchanged and its failures remain retained.

Independent cases cover carried global addresses, raw bins revisited by snapshots, temporal highwater, exact economic quotes/trades, physical adjacency, invalid BBO, policy mismatch, carry tampering and strict defaults. Direct review corrected the worker's local replay-order offset and repeated-bin accumulation before the registered check. The five current results retain the exact disposed rows in bounded Parquet series. The twelve completed strict units from attempt 25 remain retained; they were not rerun or treated as measurements under the new policy.

Execution used 194.131463 CPU-seconds, 68.079298 elapsed seconds and 173,834,108 output bytes, within declared limits. This accepts the changed source component on the five audited failures. Full acquired-source extraction, auction/flow empirical family statistics and the full-project under-three-hour target remain unfinished.

[Registered execution](auction-flow-runs/b97228eab59dadcce6a269ef6b848b02174ed4cee18ec4d15da97a83c5ac4eb4/execution.json) · [Worker evidence](auction-flow-runs/b97228eab59dadcce6a269ef6b848b02174ed4cee18ec4d15da97a83c5ac4eb4/worker.json)
