"""Profile one whole-bank session (load + warm + all candidates + stage B overhead)."""
import cProfile, pstats, sys, io, time
from pathlib import Path

day = sys.argv[1]
out = Path(sys.argv[2])
tag = sys.argv[3] if len(sys.argv) > 3 else "BEFORE"

from trading_research.research.rule_discovery import search, search_run

resolved = search.resolve_bank()
pr = cProfile.Profile()
started = time.perf_counter()
pr.enable()
result = search_run.evaluate_session(day, resolved=resolved, run_root=None)
pr.disable()
wall = time.perf_counter() - started
s = io.StringIO()
st = pstats.Stats(pr, stream=s).sort_stats("cumulative")
st.print_stats(40)
sess = result["session"]
head = (
    f"# P15-17 {tag} profile {day}\n"
    f"# wall_seconds={wall:.3f} load_seconds={sess['load_seconds']:.3f} "
    f"candidates={sess['candidates']} supported={sess['supported']} tape_batches={sess['tape_batches']}\n"
)
out.write_text(head + s.getvalue())
print(f"{tag} {day} wall={wall:.2f} load={sess['load_seconds']:.2f} rows={len(result['rows'])}")
