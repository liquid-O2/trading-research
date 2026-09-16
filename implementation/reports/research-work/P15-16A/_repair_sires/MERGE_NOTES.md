# MERGE_NOTES — track sires repair (P15-16A B0.2)

Integration owns the four-track merge, the corrected full-history run, summaries, and the receipt. This track does not write receipts.

## Shared-file edit

### `source_adapters/common.py`

Reason: `common.py` imported `peak_rss_bytes` from `runner.py` at module load. `runner.py` imports `directory_listing_digest` from `contracts/identity.py`, which this worktree does not export. That made `import sires` fail before any scan ran. The change is additive: a local `peak_rss_bytes()` wrapper that imports the runner on call.

```diff
--- a/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
+++ b/implementation/src/trading_research/research/rule_discovery/source_adapters/common.py
@@ -41,8 +41,13 @@ from trading_research.research.rule_discovery.native import (
     ticks_to_decimal,
 )
 from trading_research.research.rule_discovery.registry import expand_candidate_bank
-from trading_research.research.rule_discovery.runner import peak_rss_bytes
+
+
+def peak_rss_bytes() -> int:
+    from trading_research.research.rule_discovery.runner import peak_rss_bytes as _peak_rss_bytes
+
+    return int(_peak_rss_bytes())
```

No reformat of the rest of the file. `confirmation.py` was not edited.

### `rule_discovery/runner.py`

Reason: `runner.py` imported `directory_listing_digest` from `contracts/identity.py`, which this tree does not export. That aborted collection of `test_engine_hygiene.py`, `test_p15_02.py`, `test_p15_16a_greenbird.py`, and `test_p15_16a_jumbo.py`. Contracts stay frozen. The other three tracks have their own hunks on the same lines. The integrator must keep one version: drop the name that identity.py does not export, and digest files with `file_digest`.

```diff
--- a/implementation/src/trading_research/research/rule_discovery/runner.py
+++ b/implementation/src/trading_research/research/rule_discovery/runner.py
@@ -19,7 +19,6 @@ from trading_research.research.contracts.identity import (
     code_snapshot_document,
     digest,
-    directory_listing_digest,
     file_digest,
     make_task_receipt,
@@ -574,10 +573,7 @@ def write_task_identity(
     import sys
 
     plan_files = {rel: file_digest(ROOT / rel) for rel in plan_paths}
-    code_files = {}
-    for rel in code_paths:
-        path = ROOT / rel
-        code_files[rel] = directory_listing_digest(path) if path.is_dir() else file_digest(path)
+    code_files = {rel: file_digest(ROOT / rel) for rel in code_paths}
```

## Integration must do

1. Re-run B0.2 over all 1,742 sessions after merging the four family tracks. First-round job files under `1e13829f2c88f1e1` used a fixture evaluator for SIRES (two synthetic episodes per session, all unknown at location). Those counts are not the repaired population.
2. Re-run `tests/rule_discovery/test_p15_16a_plausibility_sires.py` as the population gate. It writes `PLAUSIBILITY_SIRES.json/.md` and `PLAUSIBILITY_REFILL-STUDY.json/.md`.
3. Re-run author-example replay. Detection uses the population scan on the date. `reached_location` and `detected` are separate keys.
4. Do not recompute B0 or B0.1. Byte-identity hashes for 2021-01-04 and 2022-01-03 are in `_repair_sires/B0_B01_HASHES.json` and are re-checked by `test_b0_b01_byte_identity_two_slice_dates`.
5. JETBUNDLE-STATES and STOIC scans in `processes.py` were not changed. `form_refill_zones` in `processes.py` is unchanged. B0.2 REFILL zone formation lives in `refill_b02.form_b02_zones`.

## Ownership (this branch)

- `source_adapters/sires_b02.py`, `sires.py` (re-export only)
- `source_adapters/refill_b02.py`
- `families/sires.json`, `families/processes.json` (plausibility blocks)
- `tests/rule_discovery/test_p15_16a_sires.py`
- `tests/rule_discovery/test_p15_16a_plausibility_sires.py`
- `_repair_sires/` artifacts

Confirmation predicates live only in `sires_b02.py`. They are not a shared-file hunk. `absorption_reward_retest` confirmation is the ABS pp.5-13 retest after 3-tick reward. `defended_band_continuation` confirmation is `reward_ok` (STAGE_AUDIT), not replenishment.
