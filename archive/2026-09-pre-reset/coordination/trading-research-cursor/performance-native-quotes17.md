Implement one bounded performance change: fused chronological native quote-exposure reduction.
Read /workspace/AGENTS.md and /workspace/trading-research/AGENTS.md; this is authorized performance work, not a request to resume an old assignment.
Workspace: /workspace/coordination/trading-research-cursor/worktrees/performance-native-quotes17. You may change only:
src/trading_research/data/compact_native.py
src/trading_research/research/auction_flow_native_bins.py
tests/test_auction_flow_native_bins.py
Relevant baseline hashes:
{
  "src/trading_research/data/compact_native.py": "b506778d471b2b52aa18edb95a6bb2719197b1676bd48c59cbcdb1433f8cf551",
  "src/trading_research/research/auction_flow_native_bins.py": "f7bf3be013433a05e0befbbe8bd5f2607c89832115c83477b9d69f38b360f9f1",
  "tests/test_auction_flow_native_bins.py": "7bf0374967a5b65b22959e5d3aa1696fff2ff5585504ed605b9b45c121d721a7",
  "src/trading_research/research/auction_flow_quotes.py": "fa035fd50ffd2a119a689f823129bc84b21befcbf55b5fabcb1440fa36344606",
  "tests/test_auction_flow_quotes.py": "fd5cf867ddff95548676ce5a7fad77cf241ccdfad16ca39faafc2885662b5f0f",
  "tests/test_compact.py": "ea8c077cdfda7762b6d2de8a44e3596c98a06797d3bba1ca6b2cafce69997c2a",
  "pyproject.toml": "a5af978e4dd058b45bc9f25ba05cda541e323931e3bf4ea798fd527a0618c000"
}
Measured bottleneck: quote consumers 13.854 CPU seconds across benchmark16 nine complete windows; native quote_exposure 0.622 cumulative seconds in one profiled full NQ window. It expands intervals with repeat/concatenate/argsort and recalculates ratios. Deliver a no-expanded-temporary C++ chronological interval-to-cell reducer through the EXISTING compact_native.py registered compiled library; do not add Numba/dependencies or a new build system. Python retains all quote_exposure input checks and poisoning semantics. Keep current NumPy code as exact reference/fallback when the library is not enabled. Extend execution_counts to record compiled exposure calls/intervals/cells so parent can prove use. Do not alter compiled source projection or its counters.
Interface: validated starts,ends,bid,ask,bid_size,ask_size int64 arrays + grid start/end/width and output standing_ns int64, duration_imbalance_ns and duration_spread_ticks_ns NumPy longdouble arrays. Use ctypes.ndpointer with explicit dtype, ndim, contiguous/aligned/writeable flags as appropriate; validate shapes/lengths and ABI compatibility before native calls. Avoid unsafe pointer assumptions. Python helper may return False if compiled path unavailable; return True when actually applied. No candidate imports/tests/compiler from this worker.
Semantics: half-open intervals; sorted nonoverlap and economic-age/invalidations already validated; exact duration and int64 domain; no fast math; long-double ratio and accumulation. Existing published float64 integrals tolerate at most 1e-6 absolute/1e-12 relative versus complete source reference. Bound every native write by the declared grid; no Python-row loops as the accelerated path; zero-length safe. Validation rejection must not partially mutate native output. Keep integer arithmetic safe near int64 clock endpoints. The current library is compiled once inside registered attempt with -O3 -std=c++17 -fno-fast-math -ffp-contract=off; parent owns build/registration/actual-data execution.
Tests: add independently calculated small exact interval-overlap cases for crossings, gaps, partial final cell, standing nanoseconds, spread and imbalance; compare fallback with compiled when available by temporarily selecting existing backend, without compiling from tests. Existing large/continuation/equal-clock/invalid-input cases remain. No huge synthetic benchmark or broad unrelated tests.
Return concise changed files, mechanism, API, tests added and remaining concerns. Do not claim tests passed; parent will run registered benchmark. Finish implementation promptly; no architecture/review subagents or proposals-only response.
