#!/usr/bin/env python3
"""Serial "after" verification of the closed P15-09 receipt attempt 250e5aea146f3516.

The "before" side is the driver's round-2 output
$SCRATCH/verify-16a-integration-r2/verify_before_P15-09.json (unchanged
receipts.py, ok false, 39 raw failures, 3702.7 s under load). This runs only the
memoized verifier and compares the distinct (code, path, detail) sets.
"""
from __future__ import annotations

import cProfile
import io
import json
import os
import pstats
import sys
import time
from pathlib import Path

ROOT = Path("/workspace")
SCRATCH = Path(os.environ["SCRATCH"])
sys.path.insert(0, str(ROOT / "implementation/src"))

from trading_research.research.contracts.receipts import verify_task_receipt  # noqa: E402

RECEIPT = ROOT / "implementation/reports/research-work/P15-09/250e5aea146f3516/attempt-0001/TASK_RECEIPT.json"
BEFORE = SCRATCH / "verify-16a-integration-r2/verify_before_P15-09.json"
OUT = Path(__file__).resolve().parent / "PROFILE_VERIFY_P15-09.txt"


def _triples_from_result(result):
    return sorted({(str(item.code), str(item.path), str(item.detail)) for item in result.failures})


def _triples_from_json(payload):
    out = set()
    for item in payload.get("failures") or []:
        if isinstance(item, dict):
            out.add((str(item.get("code")), str(item.get("path")), str(item.get("detail"))))
        elif isinstance(item, (list, tuple)) and len(item) >= 3:
            out.add((str(item[0]), str(item[1]), str(item[2])))
    return sorted(out)


def main() -> int:
    before = json.loads(BEFORE.read_text())
    before_triples = _triples_from_json(before)
    load_start = os.getloadavg()

    started = time.perf_counter()
    result = verify_task_receipt(RECEIPT)
    wall = time.perf_counter() - started
    after_triples = _triples_from_result(result)

    profiler = cProfile.Profile()
    profiler.enable()
    profiled = verify_task_receipt(RECEIPT)
    profiler.disable()
    buf = io.StringIO()
    pstats.Stats(profiler, stream=buf).sort_stats("cumulative").print_stats(30)

    equivalent = bool(result.ok) == bool(before.get("ok")) and after_triples == before_triples
    lines = [
        f"receipt={RECEIPT}",
        f"before_source={BEFORE}",
        "before_module=$SCRATCH/verify-16a-integration-r2/receipts_before.py (unchanged receipts.py, round-2 driver run)",
        f"loadavg_at_start={load_start}",
        f"loadavg_at_end={os.getloadavg()}",
        f"before_wall_seconds={before.get('wall_seconds')}",
        f"after_wall_seconds={wall:.3f}",
        f"speedup_vs_before={(float(before.get('wall_seconds') or 0) / wall):.2f}x" if wall else "speedup_vs_before=n/a",
        f"before_ok={before.get('ok')}",
        f"after_ok={result.ok}",
        f"profiled_after_ok={profiled.ok}",
        f"before_n_failures={before.get('n_failures')}",
        f"after_n_failures={len(result.failures)}",
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
    print(f"after_wall={wall:.1f}s ok={result.ok} distinct={len(after_triples)} equivalent={equivalent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
