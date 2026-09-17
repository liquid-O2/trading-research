# Adapter-population full-history work log

- Run id: `1e13829f2c88f1e1`
- Manifest sha256: `1e13829f2c88f1e19d09704094213260080b14095b0ecce9ed3fd27ad6b30bc7`
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
- Jobs are jobs/<date>/<branch>.json.gz. Branch names in this population do not collide.
- cpu_quota reads cgroup v1 cpu.cfs_quota_us/period first, then v2 cpu.max.
- default_workers is floor(quota/period)-5, at least 1 (12 on this machine).
- install_write_guard is on. A cache miss fails the date.
- load_registry(..., check_software=False) because this runner sits beside frozen baseline_repairs.py.
- SIRES and REFILL-STUDY B0.2 use the R3 NativeMarketView array plane attached once per date.
- Resume skips a date with a valid completion.json. Existing job gz files are kept.
- SUMMARY.json and RUN_COMPLETE.json are written only when all 1742 dates have a valid completion.

## Integration decisions (2026-09-15)

- Applied RR-02 EQ two-sided contacts in `changed_reference_scan`; q1 long / q3 short stay the default pair.
- Applied F18 by dropping JJ-TBR from CLOCK_ZONE_UNVERIFIED_FAMILIES (TBR p.4/p.6 New York clock). GB names stay in the frozenset so frozen B0/B0.1 dual-scan flags do not move.
- Refused changing `common.golden_pocket` (F06 lives in `green_b02.pocket_in_leg_direction`; B0.1 identity gate).
- Refused putting `scan_b02` inside default `dual_scan`. Third slot is `include_b02=False` by default.
- Deleted runner copies of `_scan_gb_fail_0930`, `_scan_overnight`, `_scan_golden_pocket`, `_golden_episode`, `_gb_fail_sweep`. Redirects call family `scan_b02`.
- `--baseline B0.2` runs 39 family branches x 1742 dates. B0/B0.1 are not recomputed.
- Replay skips dates outside the native calendar and ES examples without touching the derived cache.
- Bare `stage(..., "pass", time)` calls on jumbo/greenbird now carry the operand values they were decided on.
- Guarded SAINT-AMT `_scan_poc` OHLC/delta through `_bar_px`. A bar with None/non-numeric open is not a close-above-open push (2026-07-07 ConversionSyntax). The tell is not widened.
- RR-02 recorded as partial: EQ two-sided is in; q1 long / q3 short stay the default pair.
- F18 recorded as partial: JJ-TBR dropped from CLOCK_ZONE_UNVERIFIED_FAMILIES; GB-FAIL/GB-VWAP/GB-SCALP remain so frozen B0/B0.1 dual-scan flags do not move. file_line is `common.py:CLOCK_ZONE_UNVERIFIED_FAMILIES`.
- SIRES `match_branch_only` with opposite side is `match_branch_only;miss:side our=... author=...` (SI-2026-07-08).
- Resumed B0.2 without `--dates`. 2026-07-07 completed (65.9s); RUN_COMPLETE.json written; failed_dates empty; 1742/1742 dates, 67938 jobs.
- Receipt rewrite: PLAN_SNAPSHOT adds SOURCE_ADDITIONS and astra REVIEW; CODE_SNAPSHOT carries owned directory entries; pytest -v so evidence selectors resolve; RULES annotation dropped; S01/S03 status unsupported (probes unproduced); B02_SUMMARY.md and AUTHOR_EXAMPLE_REPLAY.md in the manifest.
- KEANI-OPEN-ABOVE-VALUE B0.2 is not measured. Job path `jobs/<date>/<branch>.json.gz` collides with GB-VWAP `source_long`. Distinct gzip files: 66196, not 67938. The KEANI summary row is marked not_measured rather than repeating GB-VWAP numbers.

