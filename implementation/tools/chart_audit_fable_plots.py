"""Chart audit (Fable pass): draw the retained implementation's geometry per RULES.md section B id.

One canvas per family (Jumbo / Green Bird / AMT / flow / regime / Sires / Pine), reusing the
family drawing methods of chart_audit_plots.py, so nothing but that family's retained objects is
drawn. Dates: case A = a session the author's own chart shows (when it lies inside slice F) or the
first code-positive session; case B = the opposite scorer result. Scorer results come from the
current recipe_score predicates (scorer_fire_dates.json, written by the same pass).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chart_audit_plots as cap  # noqa: E402

OUT = cap.ROOT / "implementation/reports/phase1-live/chart-audit-fable"
cap.PLOTS = OUT / "plots"
FIRE = json.loads((OUT / "scorer_fire_dates.json").read_text())

# Sessions on which the author's own chart (v2 archive / media zip / greenbirdtrader-complete.pdf)
# shows the setup. Only dates inside slice F (2024-01-02 .. 2026-08-31) are listed.
AUTHOR_DATES = {
    "R-J01": ["2025-10-14", "2025-10-01", "2025-01-28", "2025-10-13", "2026-06-09"],
    "R-J02": ["2025-10-14", "2025-01-28", "2025-10-01"],
    "R-J03": ["2026-07-27", "2026-07-16"],
    "R-J04": ["2026-07-07", "2026-07-28"],
    "R-J05": ["2026-07-27", "2026-07-16", "2025-10-03"],
    "R-J06": ["2026-07-10", "2026-07-28", "2026-07-07"],
    "R-J07": ["2026-06-08", "2026-07-07"],
    "R-J08": ["2025-09-09", "2025-09-12", "2025-11-25", "2026-07-06", "2025-10-14", "2025-11-18"],
    "R-J09": ["2025-10-08", "2025-10-13", "2025-10-06", "2025-10-07", "2026-06-05", "2026-06-12", "2025-05-23"],
    "R-J10": ["2025-12-30", "2026-01-02", "2025-09-09"],
    "R-J11": ["2026-07-06", "2025-09-09", "2025-05-29", "2025-05-23"],
    "R-J12": ["2026-01-02", "2026-01-09", "2025-11-10", "2025-12-30"],
    "R-J13": ["2026-08-28"],
    "R-J14": ["2026-01-09", "2025-05-23"],
    "R-J15": ["2026-07-23", "2026-06-09", "2026-05-19"],
    "R-J16": ["2026-06-08", "2026-07-16"],
    "R-J17": ["2026-06-08"],
    "R-J18": ["2025-10-14", "2025-01-28"],
    "R-J19": ["2025-04-01", "2025-01-28", "2025-10-03"],
    "R-J21": ["2026-07-07", "2026-07-10"],
    "R-J22": ["2025-10-13"],
    "R-J24": ["2025-10-14", "2025-01-28"],
    "R-J25": ["2026-01-14"],
    "R-G01": ["2026-08-28", "2026-08-12", "2025-11-20"],
    "R-G02": ["2026-07-14", "2026-08-12", "2026-04-23"],  # the "13 Jul" Asia chart is trade date 14 Jul (the 20:00-00:00 box belongs to the next session)
    "R-G03": ["2026-08-27"],
    "R-G04": ["2026-08-31"],
    "R-G05": ["2026-08-28", "2026-04-23", "2026-08-27"],
    "R-G06": ["2026-08-17", "2026-08-03", "2026-07-27"],
    "R-G07": ["2026-07-30", "2026-08-12"],
    "R-G08": ["2026-07-14", "2025-11-19"],
    "R-G09": ["2026-07-27"],
    "R-G10": ["2026-08-20"],
    "R-G11": ["2026-08-28", "2026-08-13"],
    "R-S01": ["2026-07-14"],  # NYAM p.10 DeepCharts stamp 14/07/2026 10:36 ET; same bands as p.4-5 (trade 1 at ~09:37)
    "R-S02": ["2026-07-14"],  # NYAM p.6-7, same session (third retest ~10:13-10:15)
    "R-S07": ["2026-07-23"],  # ANAT cover: "NQ / 23 JULY 2026"
    "R-F09": ["2026-07-15"],  # STOP p.8-9 DeepCharts timestamps 15/07/2026 01:01 and 03:04 (overnight)
    "R-F13": ["2026-07-15"],  # STOP p.9 trapped buyers at the highs, same clip
}


# Blocked ids have no scorer result. Their canvases use the retained diagnostic flag named here
# (case A = flag true, case B = flag false) and are titled UNSCORED.
BLOCKED_DIAG = {
    "R-F02": ("cvd_step_F", "f02_divergence"),
    "R-F07": ("mbp1_flow_F", "iceberg_touch"),
    "R-R04": ("flow_cvd_smt_F", "smt_ohlc"),
    "R-P18": ("flow_cvd_smt_F", "cvd_agree_ohlc"),
}


def _blocked_dates(rid):
    import pyarrow.parquet as pq
    table, col = BLOCKED_DIAG[rid]
    df = pq.read_table(cap.ROOT / "implementation/reports/phase1-live/_tables" / f"{table}.parquet").to_pandas()
    df = df[df[col].notna()]
    pos = [str(d)[:10] for d in df[df[col].astype(bool)]["date"]]
    neg = [str(d)[:10] for d in df[~df[col].astype(bool)]["date"]]
    return pos, neg


def _available(iso):
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        return False
    if iso not in cap.TABLES["sessions_F"]:
        return False
    if cap.window(d, 9.5, 16)["n"] < 300:
        return False
    prev = cap.PREV.get(iso)
    return bool(prev) and cap.window(date.fromisoformat(prev), 9.5, 16)["n"] >= 300


def specs():
    out = []
    for s in cap.SCORES:
        rid = s["id"]
        f = FIRE.get(rid, {})
        pos, neg = f.get("pos", []) or [], f.get("neg", []) or []
        blocked = rid in BLOCKED_DIAG
        if blocked:
            pos, neg = _blocked_dates(rid)
        author = [d for d in AUTHOR_DATES.get(rid, []) if _available(d)]
        a = next((d for d in author), None)
        selection_a = "author-dated session" if a else None
        if a is None:
            a = next((d for d in pos if _available(d)), None)
            selection_a = "code-positive" if a else None
        if a is None:
            a = next((d for d in neg if _available(d)), None)
            selection_a = "code-negative (no positive exists)" if a else "diagnostic"
        a_pos = a in pos
        pool = neg if a_pos else pos
        b = next((d for d in author if d != a and (d in pool)), None)
        selection_b = "author-dated session" if b else None
        if b is None:
            b = next((d for d in pool if d != a and _available(d)), None)
            selection_b = ("code-negative" if a_pos else "code-positive") if b else None
        if b is None:
            b = next((d for d in author + pos + neg if d != a and _available(d)), None)
            selection_b = "same-result fallback (no opposite result exists)"
        for role, iso, sel in (("A", a, selection_a), ("B", b, selection_b)):
            if iso is None:
                continue
            out.append({
                "id": rid, "case": role, "date": iso,
                "code_result": None if blocked else True if iso in pos else False if iso in neg else None,
                "blocked_diag": (f"{BLOCKED_DIAG[rid][1]}={'true' if iso in pos else 'false'}" if blocked else None),
                "selection": sel, "author_dated": iso in AUTHOR_DATES.get(rid, []),
                "positive_count": len(pos), "negative_count": len(neg),
            })
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ids", nargs="*")
    args = p.parse_args()
    # Fresh scorer results replace the previous audit's snapshot inside the shared drawing module.
    fresh = []
    for s in cap.SCORES:
        f = FIRE.get(s["id"], {})
        s2 = dict(s)
        s2["positive_dates"] = f.get("pos", []) or []
        s2["negative_dates"] = f.get("neg", []) or []
        if f.get("event"):
            s2["event"] = f["event"]
        fresh.append(s2)
    cap.SCORES = fresh
    cases = specs()
    (OUT / "chart_cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    results = []
    for spec in cases:
        if args.ids and spec["id"] not in args.ids:
            continue
        try:
            draw_spec = dict(spec)
            if spec.get("blocked_diag"):
                draw_spec["code_result"] = f"blocked · diagnostic {spec['blocked_diag']}"
            r = cap.draw(draw_spec)
            r["code_result"] = spec["code_result"]
            r["blocked_diag"] = spec.get("blocked_diag")
            r["author_dated"] = spec["author_dated"]
            results.append(r)
            print(spec["id"], spec["case"], spec["date"], "written", flush=True)
        except Exception as e:  # keep going; the audit records the failure
            import traceback
            traceback.print_exc()
            results.append({**spec, "error": f"{type(e).__name__}: {e}"})
    if args.ids and (OUT / "plot_results.json").exists():
        # Partial rerun: replace only the rerun ids, keep every other canvas record.
        kept = [r for r in json.loads((OUT / "plot_results.json").read_text()) if r["id"] not in args.ids]
        results = kept + results
        order = {(c["id"], c["case"]): i for i, c in enumerate(cases)}
        results.sort(key=lambda r: order.get((r["id"], r["case"]), 10**6))
    (OUT / "plot_results.json").write_text(json.dumps(results, indent=2, default=str) + "\n")


if __name__ == "__main__":
    main()
