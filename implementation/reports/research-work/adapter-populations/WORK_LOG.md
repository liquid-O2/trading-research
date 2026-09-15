# Adapter-population runner (track R4) work log

Coordinator session. Stage A of 05-finite-search. Branch `p15/stage-a-r4`.

## Playbook

Feature. `how` ran as three explorers on the census runner, the 04 adapters, and the census SUMMARY. `architect` arena skipped: this host only exposes grok-4.6, and the user required one code writer. Two sketches are below. Git, receipts, wiki, and Opening a PR are skipped because the user forbade git commands and wiki or handoff edits.

## Cgroup

Read `/sys/fs/cgroup/cpu/cpu.cfs_quota_us` = 1785000 and `/sys/fs/cgroup/cpu/cpu.cfs_period_us` = 100000. Ratio 17.85. `floor(quota/period) - 5` = 12 workers.

## Branch enumeration

Census 39 are the repaired coverage ids in `/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7/SUMMARY.md`.

04 adapters register `FAMILY_BRANCHES` (48 names) plus source additions. Branches 04 introduced that the census does not contain, plus the bound census rows the ruling names:

| family | branch | why it is in this run |
| --- | --- | --- |
| GB-FAIL | london_box | A1. `scan_addition`. No coverage row. |
| GB-FAIL | asia_box | A2. `scan_addition`. No coverage row. |
| GB-FAIL | overnight_scan | A3. Window policy over `overnight_scan_branches()`, reported as one branch. |
| GB-SCALP | golden_pocket_continuation | A4. Helper only in 04. Operational impulse defined below. |
| SAINT-AMT | continuation_retest | Census row. Adapter transform binds C7 stages. |
| SAINT-AMT | trapped_buyers_retest | same |
| SAINT-AMT | failed_auction_return | same |
| SAINT-AMT | poc_traversal | same |
| GB-VWAP | source_long | Census row. D1 retest window is in `scan_green_vwap_repaired`. |

Not jobs: GB-FAIL `golden_pocket` and `entry_on_retracement` (named in `SOURCE_ADDITIONS`, `scan_addition` raises). Jumbo `quadrant_entry` / `outbound_exit_09:40` / `single_purged_add_09:40-09:50` (not branch ids). GB-SCALP `bearish_small_scalp` / `bullish_discount_pullback`, JETBUNDLE `B/A/D/E/W`, STOIC-RISK `first/second/reset_after_second_win` (Phase 1 branches, not 04 additions).

Expected jobs: 1742 dates × 9 branches = 15678.

## Architect sketches

**Sketch A (chosen).** Clone the census runner’s manifest / per-date completion / resume / SUMMARY / RUN_COMPLETE machine. Population is a frozen list of branch records (family, branch, coverage_id, scan_kind). Registry branches call `dual_scan` after importing adapters and persist only `b01`. Additions use a GB-FAIL window scan copied from `scan_green_failure_repaired` with explicit refs and begin. One date is one process-pool job. Run root is the worktree `implementation/reports/research-work/adapter-populations/<run-id>/`.

**Sketch B (rejected).** Thin CLI that shells `slice_family` per family and concatenates engineering-slice summaries. Rejected because `scan_family_date` drops episode payloads, `dual_scan` cannot see london_box, and A3 is not a `dual_scan` parameter.

## Decisions

- Run root lives in this worktree, not `/workspace/implementation/reports`. The census runner hardcoded `ROOT = Path("/workspace")`. Writing there would touch `/workspace` and collide with sibling tracks.
- Manifest `worker_count` is 12. Same census identity rule: workers are inside the hashed manifest.
- `cpu_quota()` reads cgroup v1 first (`cpu.cfs_quota_us` / `cpu.cfs_period_us`), then v2 `cpu.max`. The census helper only read v2 and reported null here.
- Jobs are `jobs/<date>/<branch>.json.gz` as specified, not the census `coverage_id` with colons replaced. Branch names in this population do not collide.
- Persist adapter B0.1 only. Do not write B0 jobs. Do not rescan frozen `scan_branch` for SUMMARY columns. Census B0.1 counts come from census `SUMMARY.json`.
- Registry branches: import every adapter module so transforms bind, then `dual_scan(market, family, branch)["b01"]`. That is dual_scan’s B0.1 document. Dual_scan still builds B0 internally; we do not store it.
- `london_box`: reference `market.range(at(02:00), at(05:00), "london-box")`. Scan from `max(09:30, known_at)` for the named branch (accepted 09:30-start). Same sweep/reclaim bind keys as `scan_green_failure_repaired`. `tdo_required=False`.
- `asia_box`: reference `market.range(at(20:00, -1), at(00:00), "asia-box")`. 09:30-start. `tdo_required=False`.
- `overnight_scan`: one job. For each name in `overnight_scan_branches()`, scan from `max(window_start, ref.known_at)` to account-day end. Existing names use `_gb_refs`. `asia_box` / `london_box` use the addition refs. Tag `values` cannot take unregistered operands through `HistoricalEpisode.bind`; store `overnight_of` on the finished episode dict and on geometry after `finish()`. Prefix `candidate_id` with the sub-branch if a collision appears.
- `golden_pocket_continuation`: operational impulse is the overnight span `range(at(18:00, -1), at(09:30), "overnight-impulse")`. Side is long if close > open, short otherwise. Pocket from `golden_pocket(low, high)`. NY session first complete five-minute close back out of the pocket in that direction. Label operational. Assemble episode dicts; do not `bind` unregistered GB-SCALP operands.
- SAINT: per episode record `arrival_read_recorded`, `alignment_ok`, `profile_allows_trade` as True, False, or None. `branch_stats` counts False and None per stage. SUMMARY repeats those counts per branch.
- GB-VWAP: during the date job, read the census B0.1 file `20def36e065c13d7/jobs/<date>/GB-VWAP--branch--source_long.json.gz` and count census-unknown candidate_ids that are pass or fail in the adapter job. SUMMARY states those two totals against the census 628 unknowns.
- `_finish_document` pattern from the census runner (outcomes, setup measurements, session accounting, wall_seconds, peak_rss_bytes, baseline_version).
- Resume: skip a date when `completion.json` matches schema, manifest sha256, full branch set, and per-job sha256. Keep existing job gz files. Retry failed dates once by unlinking `completion.json` only.
- `--dates` subset still lists all 1742 in the manifest. SUMMARY and RUN_COMPLETE only after every calendar date has a valid completion.
- Pytest runs three dates in-process (`workers<=1` sequential after `_init_worker`) against `tmp_path`. Dates: `2021-01-04`, `2022-06-15`, `2023-12-08`.
- Full run: `setsid nohup` with 12 workers, stdout/stderr under the run root, PID in `runner.pid` and the scratchpad path.
- `install_write_guard` on. Cache miss fails the date.

## Architect rationale (synthesis)

Chosen sketch A. Public surface is one module plus CLI flags copied from the census runner (`--workers`, `--dates`, `--skip-run`, `--summarize-only`). Complexity of addition scans stays behind `scan_kind` on the branch record. Sketch B would leak slice summaries and miss A1–A4.

## Open

GB-VWAP adapter B0.1 is the same repaired scanner the census already ran, so the 628 unknowns may all stay unknown. Report the measured split anyway.

## Verification

Pytest: `tests/rule_discovery/test_run_adapter_populations.py::test_adapter_populations_three_native_dates PASSED` in 103.79s.

Three-date CLI on the hashed run root `dd386316321ee58d` with 12 workers: 2021-01-04 (37.8s), 2023-12-08 (41.3s), 2022-06-15 (46.2s). Jobs carry `baseline_version`, `wall_seconds`, `peak_rss_bytes`. SAINT episodes expose the three C7 stage fields. `overnight_scan` tags `overnight_of`. London box produced pass episodes. GB-VWAP 2023-12-08 is unknown with 0 census-unknown resolutions on those dates.

Detached full run PID 2302062. Resume pending 1739. First new completion `2020-01-01` at 25.0s. PROGRESS completed 4, remaining 1738, failed 0. The process was left running.

## Command

cwd `/workspace/.worktrees/stage-a-r4/implementation`

`setsid nohup env PYTHONPATH=src /workspace/implementation/.venv/bin/python src/trading_research/research/rule_discovery/run_adapter_populations.py --workers 12 > <run-root>/run.stdout 2> <run-root>/run.stderr &`

## Implementation (R4 writer)

- Golden-pocket unknown side (impulse open or close is None) emits one `unknown` episode instead of skipping, so an impulse without a side is visible in counts.
- `run_dates` includes already-complete dates as `resumed` rows in `date_results`. Scanning still submits only dates that are not `_completion_ok`.
- Pytest `test_adapter_populations_three_native_dates` passed in 109.45s.
