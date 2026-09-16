# Merge notes, Green Bird repair track

Ownership. `source_adapters/green_b02.py`, `green_failure.py` (scan_b02 forward only, unchanged logic), `green_vwap_scalp.py` (scan_b02 forward only), `families/green_failure.json`, `families/green_vwap_scalp.json`, `tests/rule_discovery/test_p15_16a_greenbird.py`, `tests/rule_discovery/test_p15_16a_plausibility_greenbird.py`, and `reports/research-work/P15-16A/_repair_greenbird/`.

## Shared-file edits

### `implementation/src/trading_research/research/rule_discovery/runner.py`

Reason. The worktree copy imported `directory_listing_digest` from `trading_research.research.contracts.identity`. That name does not exist in this tree. `contracts/*.py` is frozen for this track. The import broke `common.load_source_market` and therefore every Green Bird test.

This is a restore of the two main hunks, not a family feature.

```diff
--- a/implementation/src/trading_research/research/rule_discovery/runner.py
+++ b/implementation/src/trading_research/research/rule_discovery/runner.py
@@ -19,7 +19,6 @@
     canonical_value,
     code_snapshot_document,
     digest,
-    directory_listing_digest,
     file_digest,
     make_task_receipt,
     plan_snapshot_document,
@@ -573,10 +572,7 @@
     import sys
 
     plan_files = {rel: file_digest(ROOT / rel) for rel in plan_paths}
-    code_files = {}
-    for rel in code_paths:
-        path = ROOT / rel
-        code_files[rel] = directory_listing_digest(path) if path.is_dir() else file_digest(path)
+    code_files = {rel: file_digest(ROOT / rel) for rel in code_paths}
```

Integration. Keep main's `runner.py`. Do not take a `directory_listing_digest` import from this branch.

### `common.py` and `confirmation.py`

No edits.

## Integration step must do

1. Re-run `pytest -p no:cacheprovider tests/rule_discovery/test_p15_16a_plausibility_greenbird.py tests/rule_discovery/test_p15_16a_greenbird.py` on the merged tree.
2. Re-run the corrected full-history B0.2 scan. cash_open_reclaim_case should no longer be structurally zero. nyam_box and previous_hour pass counts should drop because at-level confirmation now requires a close back through the edge inside the fail window.
3. VWAP objective is entry+150 with 100 recorded as the OD variant. Do not switch it back to 100 without quoting GB p.34 as the baseline.
4. GB-SCALP `golden_pocket_continuation` is the up-leg NY pullback only. Down-leg overnight pocket remains GB-FAIL `golden_pocket`.
5. Family-level A+ cap is a plausibility diagnosis, not a scan filter (F07).
6. B0/B0.1 hashes are in `_repair_greenbird/B0_B01_HASHES_START.json`.
7. `ny_session_extreme` is new on GB-FAIL. Freeze the 09:30-11:00 range at 11:00; do not take a running-extreme loop from another track.
8. Two London stop placements are dated literals (2026-09-14 retest HL, 2026-09-15 sweep+buffer 11.75). Do not collapse them to one formula.
9. RR-12 ladder author spacing is 8-33, not 8-25.
10. Family JSON `plausibility` has no `observed_rate_justification` on any branch. Do not add one to silence the gate.
11. This track's `runner.py` hunk is a restore of main's identity imports (`directory_listing_digest` removed). Keep main's `runner.py`. The other three tracks may have different hunks on the same lines; this one is the two-hunk restore only (import drop + `code_files = {rel: file_digest(...)}`).
