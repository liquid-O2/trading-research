#!/bin/bash
# Exact measurement protocol: each session is ONE process alone on ONE core
# (taskset), fresh per session (first scan after load), before and after
# interleaved before-after-before-after per date. The 20 dates are split across
# five cores so the wall is bearable; a core is never shared by two
# measurements, and BEFORE and AFTER for a date always share the same core.
set -u
S=/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad
OUT=/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-17/_fast/throughput_raw.jsonl
run() {  # core tag src day
  env -i PATH=/usr/bin:/bin HOME="$HOME" \
      OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 \
      PYTHONPATH="$3/src" taskset -c "$1" \
      /workspace/implementation/.venv/bin/python "$S/measure_session.py" "$4" "$2" 2>/dev/null \
    | grep '^MEASURE ' | sed 's/^MEASURE //' >> "$OUT"
}
lane() {  # core day...
  local core=$1; shift
  for d in "$@"; do
    for rep in 1 2; do
      run "$core" BEFORE /workspace/.worktrees/p15-17-stage-a/implementation "$d"
      run "$core" AFTER  /workspace/.worktrees/p15-17-fast/implementation  "$d"
    done
    echo "lane$core done $d $(date -u +%H:%M:%S)" >&2
  done
}
: > "$OUT"
lane 100 2020-01-02 2020-06-01 2020-11-02 2021-01-04 &
lane 101 2021-06-01 2021-11-01 2022-01-03 2022-06-01 &
lane 102 2022-11-01 2023-01-03 2023-06-01 2023-11-06 &
lane 103 2024-01-02 2024-06-03 2024-11-01 2025-01-02 &
lane 104 2025-06-02 2025-11-03 2026-01-02 2026-06-01 &
wait
echo "THROUGHPUT_COMPLETE" >&2
