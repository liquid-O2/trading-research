# Performance diagnostic — unchanged full-day replay

The isolated April 15, 2024 replay ran all 57 daily jobs with cProfile. Its episodes, original outcomes, setup measurements, session accounting, native input identity and execution counts match the retained census day exactly. Diagnostic output is excluded from the census.

The instrumented run recorded about 756 million function calls in 384 seconds. Profiling changes runtime; this is not an uninstrumented throughput benchmark and does not establish an achievable speedup.

Largest actionable costs include repeated native-row iteration/normalization (local windows: 98 seconds cumulative), recursive conversion/serialization (serializable: 63 seconds cumulative), and evidence writing (84 seconds cumulative). Deep copying took 33 seconds cumulative. These cumulative categories overlap and must not be added. About 307 million isinstance calls illustrate the Python object-handling overhead.

A future performance change should first remove repeated normalization and object traversal, keep native numerical data in typed arrays, reuse deterministic features and immutable evidence by reference, and separate numerical kernels from record assembly. Vectorization or Numba can then target the measured numerical loops; converting the whole object-oriented pipeline to Cython is not established as the best first step. Every optimized path would need exact native ownership, clock, coverage, tie, and semantic-equivalence checks before a new measured run.

The active census implementation was not modified. Full execution, reconciliation and chart review remain the current task.
