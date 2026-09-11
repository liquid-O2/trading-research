"""Snapshot the existing scorer and fixtures without rebuilding or replacing inputs.

The results describe what the code currently scores, not verified source events.
All writes are restricted to the chart-audit output directory.
"""
from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live import recipe_score as score
from trading_research.research.phase1_live.compute import load_rows

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "implementation/reports/phase1-live/chart-audit"
PACKAGE = "trading_research.research.phase1_live."


def serial(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def cached(table):
    rows = load_rows(table)
    if not rows:
        raise RuntimeError(f"Required retained table absent: {table}; no rebuild permitted")
    return rows


def main():
    replacements = {
        "family_levels": {"build_level_table": "level_grid_F"},
        "family_fail": {"build_fail_table": "fail_F"},
        "family_recipes": {"build_recipe_table": "recipe_flags_F"},
        "family_tape": {"build_tape_table": "tape_flags_F", "build_f02_table": "cvd_step_F"},
        "family_gex": {"build_gex_table": "gex_qqq_F"},
    }
    for module, names in replacements.items():
        mod = importlib.import_module(PACKAGE + module)
        for name, table in names.items():
            cached(table)
            setattr(mod, name, lambda table=table: cached(table))
    score.build_level_table = lambda: cached("level_grid_F")
    joined = score._join()
    preds = score._preds()
    source = Path(score.__file__).read_text()
    expressions = {}
    pred_tree = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "_preds")
    for n in pred_tree.body:
        if isinstance(n, ast.FunctionDef):
            expressions[n.name] = {"line": n.lineno, "code": ast.get_source_segment(source, n)}
    clocks = cached("clocks_F")
    result = []
    for spec in score.catalog():
        record = dict(spec)
        pred = preds.get(spec.get("pred"))
        rows = [r for r in joined if r.get("eligible")]
        record["denominator_unit"] = "sessions"
        if spec["id"] == "R-J23":
            rows = [r for r in clocks if r.get("clock") == "range.midnight.0000-0030" and r.get("eligible")]
            pred = lambda r: r.get("path_class") == "both"
        elif spec["id"] == "R-G06":
            rows = [r for r in rows if r.get("monday")]
            pred = lambda r: bool(r.get("nwog_fill"))
        elif spec["id"] == "R-J20":
            rows = [r for r in rows if r.get("release_1000")]
            pred = lambda r: bool(r.get("j20_delayed"))
        elif spec["id"] == "R-G09":
            conditional = [r for r in rows if r.get("monday") and r.get("stacked_asia_london_pdh")]
            record["empty_condition_falls_back_to_all_sessions"] = not bool(conditional)
            if conditional:
                rows = conditional
                pred = lambda r: bool(r.get("nwog_fill"))
        if pred is not None:
            flags = [bool(pred(r)) for r in rows]
            record["positive_dates"] = [r["date"] for r, flag in zip(rows, flags) if flag]
            record["negative_dates"] = [r["date"] for r, flag in zip(rows, flags) if not flag]
            record["n"] = len(rows)
            record["k"] = sum(flags)
        else:
            record.update(n=0, k=None, positive_dates=[], negative_dates=[])
        if spec["id"] == "R-G03":
            record["denominator_unit"] = "clock-hour boxes"
            record["n"] = sum(r.get("hour_box_n") or 7 for r in rows)
            record["k"] = sum(r.get("hour_fail_n") or 0 for r in rows)
        record["rate"] = record["k"] / record["n"] if record["n"] and record["k"] is not None else None
        record["predicate_source"] = expressions.get(spec.get("pred"))
        result.append(record)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "score_snapshot.json").write_text(json.dumps(result, indent=2, default=serial))
    (OUT / "joined_snapshot.json").write_text(json.dumps(joined, default=serial))
    fixtures = {}
    for module, name in [
        ("fixtures", "run_ticket01_fixtures"), ("formulas", "formula_fixtures"),
        ("formulas_jumbo", "jumbo_fixtures"), ("formulas_flow", "flow_fixtures"),
        ("family_levels", "level_fixtures"), ("family_clocks", "clock_fixture"),
        ("family_open", "open_fixtures"), ("family_env", "env_fixtures"),
        ("family_fail", "fail_fixtures"), ("family_value", "value_fixtures"),
        ("family_flow", "flow_fixtures"), ("family_options", "options_fixtures"),
        ("mbp1_objects", "mbp1_fixtures"),
    ]:
        try:
            fixtures[module + "." + name] = getattr(importlib.import_module(PACKAGE + module), name)()
        except Exception as exc:
            fixtures[module + "." + name] = {"error": f"{type(exc).__name__}: {exc}"}
    (OUT / "fixture_snapshot.json").write_text(json.dumps(fixtures, indent=2, default=serial))
    print(json.dumps({"ids": len(result), "joined_sessions": len(joined), "fixtures": {k: {kk: vv for kk, vv in v.items() if kk in ("pass", "n_cases", "n_failed", "error")} for k, v in fixtures.items()}}, default=serial))


if __name__ == "__main__":
    main()
