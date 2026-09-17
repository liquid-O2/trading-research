# Adapter-population full-history work log

- Run id: `823273eba4b9ec50`
- Manifest sha256: `823273eba4b9ec5039725ebca1a864259e9279525932c0266c965f200c763746`
- Baseline: `B0.2-2026-09-15`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 4
- Jobs: 6968
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
