# Engine performance and parity contract

Applies to all new Phase 1.5 and Phase 2 engine code under `implementation/src/trading_research/research/rule_discovery/`, `research/contracts/` and `research/experts/`, and to any separately versioned runtime that re-executes accepted `method_pack` scanners. Accepted Phase 1 code, the frozen run `run-1.0.1` and the warm event cache under `/workspace/data/derived/phase1-event-time-v2` are unchanged inputs. This contract adds engineering acceptance; it changes no research formula, budget or gate.

## Measured baseline, 2026-09-14 profile of run-1.0.1

Per-job durations were never stored; these are mtime proxies at one-second resolution plus one in-process cProfile of session 2024-03-05.

| Measure | Value |
| --- | --- |
| Job phase wall clock | 5.72 h for 1,742 dates × 57 branches |
| Branch CPU time, summed | 79.6 h; median 1 s, p90 6 s, p99 31 s, max 434 s per branch-day |
| Concurrency | 48 workers on 17.85 effective cgroup CPUs; achieved 13.9× (78%) |
| Per-worker startup | 10–17 s (142 parquet footers, registry and software-tree hashing) × 1,742 = 5–8 CPU-h |
| JETBUNDLE:B | 13.9 CPU-h (17.5% of total); 43.5 s of 59.6 s per session is `deepcopy` of 213k event dicts plus re-serialising them for `content_hash` |
| SIRES:vwap_deviation_fade | 17.9 s per session; 10.0 s is `EventWindow.coverage` rescanning minutes (393 calls), 4.1 s is per-row MBP-1 dict decode |
| Market load | 10.5 s per session before any scanner runs |
| Output layout | 315,655 content-addressed files in one flat `domain/` directory |

Conclusion: the census is dominated by redundant copying, hashing, per-minute rescans and per-row dict decoding, then by oversubscription. Numeric loops are second-order. A Numba or Cython port of scanner arithmetic alone would not fix it.

## Why it matters now

Breadth search runs up to 160 candidates on their eligible branches over all 1,742 sessions. At Phase 1 efficiency (79.6 CPU-h / 57 branches ≈ 1.4 CPU-h per branch-census) with about three eligible branches per candidate, breadth costs roughly 670 CPU-h ≈ 38 h wall on 17 workers, above the 24-hour stage budget in WORKFLOW.md. The new engine must be at least 3× more efficient per branch-session, measured, before P15-17 is dispatched.

## Required properties of new engine code

1. **Columnar session data plane.** Decode each MBP-1 window once into NumPy arrays: `t_ns int64`, `price_ticks int64` (price/0.25 exactly), `size int64`, `side int8`, `action int8`, `bid_ticks`, `ask_ticks`, `bid_sz`, `ask_sz`, `flags`, plus `row_id` preserving `f"{source_file}:{source_row}"`. Every primitive consumes arrays. `Decimal` appears only at serialization, constructed from integer ticks, never from floats. The out-of-order timestamp check and the equal-timestamp batch boundaries are computed once as index arrays.
2. **Per-minute state tables once per window.** Bar-present, observed-complete, known-at, schedule state and unowned-interval overlap are arrays over the window's minutes. `coverage(start, end)` is a slice plus `np.bincount`; `unknown_intervals` is a run over a boolean mask. Session policy state is memoized per minute bucket. No per-minute `datetime` construction inside hot paths.
3. **Prefix sums and reduceat.** VWAP, dispersion, CVD variants and cohort aggregates use cumulative sums of `p·v`, `v`, `p²·v` and signed `q` with `searchsorted` window bounds. Bars use `np.add.reduceat` / `np.maximum.reduceat` on boundary indices. Profiles use `np.bincount` over tick bins and `np.convolve` for the triangular kernel. First passage scans batch-grouped arrays and checks target/stop crossings per batch for ambiguity.
4. **State machines on the contact subset only.** S1–S4 and book-observation machines run in Numba `@njit` over arrays, or in plain Python over the small subset of batches after a contact. Never per-event Python over a full session.
5. **No copying or re-hashing of inputs.** Producers read event arrays without `deepcopy`. Content hashes and canonical manifests are computed once per object identity and memoized per process. Bytes fed to any existing hash function are unchanged.
6. **Process hygiene.** Worker count defaults to `floor(cpu.cfs_quota_us / cpu.cfs_period_us)` when a cgroup quota exists, else `os.cpu_count()`, never a hard-coded 48. A pool initializer loads the registry, ownership manifest and calendars once per process. Unit of work is one session date. Content-addressed outputs are sharded by the first two hex characters of the hash. Per-job wall seconds and peak RSS are written into every job record and receipt.
7. **Cache identity is frozen.** `event_time.py`, `event_cache.py`, `mbp1_views.py`, `adapters.py`, `native_resolution.py`, `empirical_tape.py` and `objects/profiles.py` define the event-cache transform identity. Phase 1.5 engine work does not edit them. New views are new modules with their own versioned identity that read the parquet and the warm cache.

## Parity protocol

- **Baseline delegation parity.** For a stratified sample of at least 40 dates (eight per year 2020–2025 plus 2026, including both DST transitions, an early close, a roll week and the partial 2026-09-03), replay whole dates in manifest order 0..57 through the new runtime and compare each `jobs/evaluation/<date>/<branch>.json.gz` byte-for-byte with `run-1.0.1`. Byte inequality is a failure; a differing `input_receipts` list caused by branch order is a harness bug, not an accepted difference.
- **Primitive parity.** Every vectorized primitive has a plain-Python reference in tests built from the specification's literal fixtures plus randomized arrays with ambiguous batches, gaps and unknown aggressors. Integer and Decimal outputs must be exactly equal; float outputs within 1e-12 relative. Tests fail if the reference is removed.
- **Write guard.** Tests and parity harnesses monkeypatch `event_cache.build_event_window` to raise, so a cache miss can never write under `/workspace/data`. Nothing writes into `run-1.0.1`.

## Throughput acceptance

- Before P15-17 runs, measure the new engine on 20 sessions: full account-day view plus all applicable bank primitives for one candidate-branch, single core. Record median and p90 seconds per session per candidate-branch.
- Project breadth cost as `candidates × eligible branches × 1,742 × p90 seconds / (workers × 3600)`. The runner refuses to start a stage whose projection exceeds the 24-hour budget and prints the projection; it does not reduce coverage or dates.
- Target: at most 5 s per session per candidate-branch at p90 on one core, at least 3× the Phase 1 branch-session average. Report measured values; a miss is an engineering finding to fix, never a reason to shrink the bank.
