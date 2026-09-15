# B0.1 full-history measurement work log

- Run id: `20def36e065c13d7`
- Manifest sha256: `20def36e065c13d75d738fbce475cf7ea5425255488861c58a1b5fbbbe8b488f`
- Baseline: `B0.1-2026-09-14`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 39
- Jobs: 67938
- Workers requested: 10
- cgroup_worker_count: 17
- cpu quota: {'cpu_quota_cpus': None}

## Decisions

- B0 columns are read from run-1.0.1 jobs/evaluation/<date>/<coverage>.json.gz; native scan_branch is not re-run.
- judas_reversal_deferred has no B0 job; B0 counts are zeros. B0.1 comes from scan_branch_repaired on the cloned coverage row.
- Worker count is 10 by instruction (other runs share the machine), not the cgroup default floor(quota/period).
- install_write_guard patches event_cache.build_event_window; a cache miss fails the date instead of writing under /workspace/data.
- load_registry(..., check_software=False) because this runner is new code beside frozen baseline_repairs.py.
- Job files use the run-1.0.1 measurement job keys plus baseline_version, wall_seconds, peak_rss_bytes.
- domain_observations store recipe_id and content sha256 only; the domain/ tree is not written.
- Each affected branch is dispatched through scan_branch_repaired, matching the 40-date preview.
- peak_rss_bytes is Linux ru_maxrss (kB) * 1024 at job end: worker high-water mark, not an isolated per-job reset.
- Resume skips a date with a valid completion.json; otherwise existing job files are kept and missing branches are scanned.
- If any date remains failed after one retry, SUMMARY.json, RUN_COMPLETE.json, wiki/current-status.md and PROJECT_HANDOFF.md are not updated; wiki/log.md names the failed dates.
- Subphase 03 is not started.
## Smoke 2020-01-02

- Exit 0 in 92.48 s orchestrator; date wall 86.3866 s; 39/39 jobs; job-file hashes match completion.json.
- Job keys include run-1.0.1 measurement fields plus baseline_version, wall_seconds, peak_rss_bytes.
- judas_reversal_deferred B0 episodes=0 (no run-1.0.1 file). Strict judas_reversal B0 pass=1 became B0.1 fail/no_setup (entry window).
- cgroup v1 quota 1785000/100000 = 17.85 CPUs; cpu.max is absent so RUN_COMPLETE.cpu_quota_cpus may be null and is recorded from v1 files instead.
- Full run starts next under the same manifest; 2020-01-02 will be skipped.

## Full run started

- PID 2218572, 10 workers, pending 1741 dates (2020-01-02 already complete).
- Log: run.log. Heartbeat + PROGRESS.json updated per date.
- Watcher: /home/arun/.grok/long-running-background-tasks/watch_baseline_repair.sh stall 1800s.

