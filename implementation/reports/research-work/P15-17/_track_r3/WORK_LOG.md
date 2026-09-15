# P15-17 track R3 work log

Owned worktree: `/workspace/.worktrees/stage-a-r3` (branch `p15/stage-a-r3`).
No git mutations. No edits under `/workspace` itself, `/workspace/data`, or `/workspace/sources`.

## Playbook

figure-it-out. The PERFORMANCE.md data plane is already specified, so architect/arena is skipped (laziness protocol: the shape is concrete).

## Definition of done

1. `census_reader.py` verifies pinned `manifest_sha256` and `summary_sha256` before serving B0.1 and B0. A tampered SUMMARY byte refuses.
2. Stateful loops listed in the R3 ruling run as `@njit` kernels over int64 arrays, with a plain-Python reference in tests. Integer/Decimal outputs match exactly. Float outputs stay within 1e-12 relative. Tests fail if a reference is removed.
3. Family-adapter call signatures stay. Verdict functions listed as R1-owned are not edited.
4. 20-session single-core measurement of one candidate-branch (full account-day view plus every applicable bank primitive). Targets: p90 at most 5 s, mean at most about 0.96 s (3x vs Phase 1 ~2.9 s). A miss stops with the profile. Coverage, dates, and the bank are not reduced.
5. FAMILY_THROUGHPUT.json records 04 dual-scan seconds and plane-primitive seconds as incomparable columns. It does not claim a per-family speedup.
6. Write guard, cgroup-or-affinity workers, per-job wall seconds and peak RSS, and baseline-delegation parity over every date in `stratified_parity_dates()`.
7. CLOSURE REPORT with modules, commands, throughput, census hash check, R1 merge notes, and `git status --short`.

## Decisions

See `decisions.tsv` in this directory.

Pinned B0.1 root: `/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7`
Pinned hashes: manifest `20def36e065c13d75d738fbce475cf7ea5425255488861c58a1b5fbbbe8b488f`, summary `073f270c5a5f454f4a338219eca9421e43bd3440f4ed42252dfb19f5f4d7838d`.
B0 jobs: `/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/jobs/evaluation`.

## Results

20-session candidate-branch (SAINT-AMT continuation_retest, single core): median 1.020 s, p90 1.484 s, mean 1.066 s.
- 5 s p90 gate: pass.
- 3x vs Phase 1 mean 2.886 s (target mean 0.962 s): miss. Mean is 2.71x, not 3x. Remaining time is parquet `read_row_group` plus pyarrow casts in `load_span_arrow`. Bank, dates, and coverage were not reduced.

FAMILY_THROUGHPUT.json v2 does not compare those columns as a speedup. The plane column is account-day view plus applicable bank primitives. The 04 column is HistoricalFeatures dual-scan. They are different work. `scan_family_date` still loads HistoricalFeatures.

S2 and S3 now have `@njit` kernels. Scan path: `engine_slice.py` `run_candidate_branch_session` calls `s2_machine_kernel` / `s3_machine_kernel` over bar arrays after contact, and `sequences.advance_on_bars` for applicable Sequence recipes. `advance_sequence` remains the per-batch object API for P15-07 tests. It is not the scan loop.

Round-1 bound fix: `enumerate_lifecycle_contacts` converts bars and reference bounds with `price_to_units` (0.0001). `price_to_ticks` still requires a whole 0.25 tick for event prices.

Warm 2024-03-05 cProfile after: 1.28 s. Top remaining: `load_span_arrow`, `pyarrow.compute.cast`, `ParquetFile.read_row_group`.

Census hash check: ok, both pinned hashes match.

## Merge notes for R1

- Do not edit `evaluate_family_rule_at_contact`, `_episodes_from_contacts`, or family confirmation-stage functions. This track did not.
- `enumerate_lifecycle_contacts` keeps the same signature and still returns list[dict]. Internals use `contact_lifecycle_kernel` with 4-tick rearm matching `distinct_contacts`.
- `dual_scan` still runs live scanners so 04 adapter tests and family transforms keep working. P15-17 search must read B0 and B0.1 from `census_reader.open_census()`, never from `dual_scan` / `load_source_market`.
- `scan_family_date` still loads `HistoricalFeatures`. R4 owns the adapter-bound full-history run on that path.
- New public APIs: `census_reader.CensusReader`, `kernels.*`, `native.bars_arrays`, `runner.replay_parity_sample`.
