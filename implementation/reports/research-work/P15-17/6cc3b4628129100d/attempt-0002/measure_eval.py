"""Bounded cost measurement of the P15-17 evaluation pass before scaling it.

AGENTS.md: measure runtime and peak memory before scaling a run. This measures
the evaluation (a read-only pass over an existing run root), not the engine.
"""
import json, resource, sys, time
from pathlib import Path

from trading_research.research.rule_discovery import search_run as m

root = Path(sys.argv[1])
n = int(sys.argv[2])
dates = json.loads((root / "MANIFEST.json").read_text())["dates"][:n]


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


t0 = time.perf_counter()
series, coverage = m.stream_run(root, dates)
t_stream = time.perf_counter() - t0
rss_stream = rss_gb()

t0 = time.perf_counter()
report = m.reconcile_jobs(root, dates=dates)
t_jobs = time.perf_counter() - t0
rss_jobs = rss_gb()

print(
    json.dumps(
        {
            "dates": len(dates),
            "candidates_seen": coverage["candidates_seen"],
            "stream_seconds": round(t_stream, 2),
            "stream_seconds_per_date": round(t_stream / max(len(dates), 1), 4),
            "peak_rss_gb_after_stream": round(rss_stream, 3),
            "reconcile_seconds": round(t_jobs, 2),
            "reconcile_seconds_per_date": round(t_jobs / max(len(dates), 1), 4),
            "documents_read": report["documents_read"],
            "peak_rss_gb_after_reconcile": round(rss_jobs, 3),
            "a04_violations": len(report["a04_violations"]),
        },
        indent=1,
    )
)
