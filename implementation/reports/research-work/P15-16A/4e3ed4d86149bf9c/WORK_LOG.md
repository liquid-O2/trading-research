# Adapter-population full-history work log

- Run id: `4e3ed4d86149bf9c`
- Manifest sha256: `4e3ed4d86149bf9c8c228c3d5d2dda15b92cc80222477552f4aaf09e133e9fdb`
- Baseline: `B0.2-2026-09-15`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 39
- Jobs: 67938
- Workers requested: 12
- default_workers: 12
- cgroup_worker_count: 17
- cpu quota: {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'cpu_quota_cpus': 17.85}
- census_run_id: `20def36e065c13d7`

## Decisions

- Default --baseline B0.1 keeps the frozen BRANCH_RECORDS table and does not recompute B0/B0.1.
- --baseline B0.2 dispatches every family's scan_b02; B0 and B0.1 rows are read from run-1.0.1 and census 20def36e065c13d7.
- gb_fail_0930/overnight redirect to green_failure.scan_b02; golden_pocket redirects to green_vwap_scalp.scan_b02.
- Jobs are jobs/<date>/<coverage_id with ':' replaced by '--'>.json.gz (JOB_PATH_SCHEME=coverage_id--json.gz). Branch names may collide across families.
- cpu_quota reads cgroup v1 cpu.cfs_quota_us/period first, then v2 cpu.max.
- default_workers is floor(quota/period)-5, at least 1 (12 on this machine).
- install_write_guard is on. A cache miss fails the date.
- load_registry(..., check_software=False) because this runner sits beside frozen baseline_repairs.py.
- SIRES and REFILL-STUDY B0.2 use the R3 NativeMarketView array plane attached once per date.
- Resume skips a date with a valid completion.json. Existing job gz files are kept.
- SUMMARY.json and RUN_COMPLETE.json are written only when all 1742 dates have a valid completion.

## Round 2 decisions (2026-09-15)

- Job path scheme is `coverage_id--json.gz` (`:` → `--`). KEANI and GB-VWAP `source_long` no longer collide. Recorded in MANIFEST.json and RUN_META.json as `job_path_scheme`.
- Previous run `1e13829f2c88f1e1` is left untouched as evidence of the collision (66196 distinct files).
- B0.1 run `dd386316321ee58d` readers use recorded completion paths, not the new scheme.
- identity.py is not edited (closed bytes da3cb303…). receipts.py index/de-dup/directory-owned inventory only.
- AUTHOR_EXAMPLE_REPLAY copied from 79fb63c5a6a7dc90; no adapter files changed this round.
- S01/S03 remain accepted-limit until `--probes`.
