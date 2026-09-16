#!/usr/bin/env python3
"""Serial before/after verification of the closed P15-09 receipt attempt 250e5aea146f3516.

"before" is the unchanged receipts.py copied from HEAD into a temporary package
($SCRATCH/verify-16a-integration-r2/beforepkg/receipts_before.py); "after" is the
live module with the three memos. Order is before -> after -> before2 (a warm
re-run of before, skipped when before already cost more than 40 minutes) so the
timing is not read off a single cold-cache run. The cProfile top-30 cumulative
table is taken from a third "after" call.

Writes _work_r3/PROFILE_VERIFY_P15-09.txt.
"""
from __future__ import annotations

import cProfile
import importlib.util
import io
import os
import pstats
import sys
import time
from pathlib import Path

ROOT = Path("/workspace")
SCRATCH = Path(os.environ["SCRATCH"])
sys.path.insert(0, str(ROOT / "implementation/src"))

RECEIPT = ROOT / "implementation/reports/research-work/P15-09/250e5aea146f3516/attempt-0001/TASK_RECEIPT.json"
OUT = Path(__file__).resolve().parent / "PROFILE_VERIFY_P15-09.txt"
BEFORE_SRC = SCRATCH / "verify-16a-integration-r2/beforepkg/receipts_before.py"


def _load_before():
    spec = importlib.util.spec_from_file_location("receipts_before", BEFORE_SRC)
    module = importlib.util.module_from_spec(spec)
    sys.modules["receipts_before"] = module
    spec.loader.exec_module(module)
    return module


def _triples(result) -> list[tuple[str, str, str]]:
    return sorted({(item.code, str(item.path), str(item.detail)) for item in result.failures})


def _timed(fn):
    started = time.perf_counter()
    result = fn(RECEIPT)
    return result, time.perf_counter() - started


def main() -> int:
    load_start = os.getloadavg()
    before_mod = _load_before()
    from trading_research.research.contracts.receipts import verify_task_receipt as after_verify

    before_result, before_wall = _timed(before_mod.verify_task_receipt)
    before_triples = _triples(before_result)

    after_result, after_wall = _timed(after_verify)
    after_triples = _triples(after_result)

    before2_wall = None
    if before_wall <= 2400.0:
        before_mod._VERIFY_CACHE.clear()
        _, before2_wall = _timed(before_mod.verify_task_receipt)

    profiler = cProfile.Profile()
    profiler.enable()
    profiled = after_verify(RECEIPT)
    profiler.disable()
    buf = io.StringIO()
    pstats.Stats(profiler, stream=buf).sort_stats("cumulative").print_stats(30)

    equivalent = before_result.ok == after_result.ok and before_triples == after_triples
    lines = [
        f"receipt={RECEIPT}",
        f"before_module={BEFORE_SRC}",
        f"loadavg_at_start={load_start}",
        f"loadavg_at_end={os.getloadavg()}",
        f"before_wall_seconds={before_wall:.3f}",
        f"after_wall_seconds={after_wall:.3f}",
        f"before_rerun_wall_seconds={'skipped' if before2_wall is None else format(before2_wall, '.3f')}",
        f"speedup_vs_before={before_wall / after_wall:.2f}x",
        f"before_ok={before_result.ok}",
        f"after_ok={after_result.ok}",
        f"profiled_after_ok={profiled.ok}",
        f"before_n_failures={len(before_result.failures)}",
        f"after_n_failures={len(after_result.failures)}",
        f"before_n_distinct_triples={len(before_triples)}",
        f"after_n_distinct_triples={len(after_triples)}",
        f"equivalent_ok_and_distinct_triples={equivalent}",
    ]
    for item in after_triples:
        lines.append(f"failure\t{item[0]}\t{item[1]}\t{item[2]}")
    only_before = [t for t in before_triples if t not in set(after_triples)]
    only_after = [t for t in after_triples if t not in set(before_triples)]
    lines.append(f"triples_only_before={len(only_before)}")
    lines.append(f"triples_only_after={len(only_after)}")
    for item in only_before:
        lines.append(f"only_before\t{item[0]}\t{item[1]}\t{item[2]}")
    for item in only_after:
        lines.append(f"only_after\t{item[0]}\t{item[1]}\t{item[2]}")
    lines.append("")
    lines.append("--- top 30 cumulative (after, profiled) ---")
    lines.append(buf.getvalue())
    OUT.write_text("\n".join(lines) + "\n")
    print(
        f"before={before_wall:.1f}s after={after_wall:.1f}s before2={before2_wall} "
        f"ok={after_result.ok} distinct={len(after_triples)} equivalent={equivalent}"
    )
    return 0 if equivalent else 2


if __name__ == "__main__":
    raise SystemExit(main())
