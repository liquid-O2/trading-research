"""One fresh session, one process, timed by component. Prints one JSON line."""
import json, sys, time

day, tag = sys.argv[1], sys.argv[2]
from trading_research.research.rule_discovery import exits, search, search_run

_tape = {"seconds": 0.0}
_compact = exits.compact_from_view
def _timed_compact(view):
    t = time.perf_counter()
    out = _compact(view)
    _tape["seconds"] += time.perf_counter() - t
    return out
exits.compact_from_view = _timed_compact
search_run.exits.compact_from_view = _timed_compact

_warm = {"data_plane": 0.0, "prepay": 0.0}
_ws = search.warm_session
def _timed_warm(market, **kw):
    out = _ws(market, **kw)
    _warm["data_plane"] = float(out.get("data_plane_seconds") or 0.0)
    _warm["prepay"] = float(out.get("branch_prepay_seconds") or 0.0)
    return out
search.warm_session = _timed_warm

resolved = search.resolve_bank()
started = time.perf_counter()
result = search_run.evaluate_session(day, resolved=resolved, run_root=None)
wall = time.perf_counter() - started
session = result["session"]
bank = sum(float(row.get("seconds") or 0.0) for row in result["rows"])
load = float(session["load_seconds"])
row = {
    "tag": tag,
    "date": day,
    "end_to_end": wall,
    "load": load,
    "data_plane": _warm["data_plane"],
    "prepay": _warm["prepay"],
    "tape_compaction": _tape["seconds"],
    "market_open": load - _warm["data_plane"] - _warm["prepay"] - _tape["seconds"],
    "whole_bank": bank,
    "stage_b_overhead": wall - load - bank,
    "rows": len(result["rows"]),
    "tape_batches": session["tape_batches"],
}
print("MEASURE " + json.dumps(row, sort_keys=True), flush=True)
