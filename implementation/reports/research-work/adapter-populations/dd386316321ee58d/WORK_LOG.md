# Adapter-population full-history work log

- Run id: `dd386316321ee58d`
- Manifest sha256: `dd386316321ee58d42dc70a612181ed365f727eb0f8d6a82c53a2afbff33164d`
- Baseline: `B0.1-2026-09-14`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 9
- Jobs: 15678
- Workers requested: 12
- default_workers: 12
- cgroup_worker_count: 17
- cpu quota: {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'cpu_quota_cpus': 17.85}
- census_run_id: `20def36e065c13d7`

## Decisions

- Population is the frozen BRANCH_RECORDS table (family, branch, coverage_id, scan_kind).
- Persist adapter B0.1 only. dual_scan B0 is not written.
- Jobs are jobs/<date>/<branch>.json.gz. Branch names in this population do not collide.
- cpu_quota reads cgroup v1 cpu.cfs_quota_us/period first, then v2 cpu.max.
- default_workers is floor(quota/period)-5, at least 1 (12 on this machine).
- install_write_guard is on. A cache miss fails the date.
- load_registry(..., check_software=False) because this runner sits beside frozen baseline_repairs.py.
- london_box/asia_box copy the repaired GB-FAIL sweep/reclaim loop from max(09:30, known_at).
- overnight_scan concatenates overnight_scan_branches() with begin max(window start, known_at), not 09:30.
- golden_pocket_continuation is operational overnight-impulse geometry assembled without HistoricalEpisode.bind.
- SAINT dual_scan binds C7 stages after ensure_transforms imports saint.
- GB-VWAP joins census B0.1 jobs on candidate_id and counts unknown that become pass or fail.
- Resume skips a date with a valid completion.json. Existing job gz files are kept.
- SUMMARY.json and RUN_COMPLETE.json are written only when all 1742 dates have a valid completion.
