"""range.6-9.published and range.6-9.vol-elapsed."""

from __future__ import annotations

from collections import Counter

import numpy as np

from trading_research.research.phase1_live.compute import add_vol_elapsed, build_slice, load_rows, save_rows
from trading_research.research.phase1_live.fixtures import run_ticket01_fixtures
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.sessions import XF_WIDTH_BINS, _bin_label
from trading_research.research.phase1_live.stats import (
    by_year, paired_diff, rate_block, session_bootstrap_rate, status_from_intervals,
)

XF_P24 = {
    "quoted_n": 3249,
    "rows": {
        "0-0.3": {"n": 1034, "double": 55.5, "single_high": 23.7, "single_low": 20.3, "none": 0.5},
        "0.3-0.5": {"n": 1053, "double": 48.1, "single_high": 25.6, "single_low": 25.7, "none": 0.5},
        "0.5-0.8": {"n": 705, "double": 34.8, "single_high": 34.9, "single_low": 29.5, "none": 0.9},
        "0.8-1.2": {"n": 288, "double": 34.0, "single_high": 31.2, "single_low": 33.0, "none": 1.7},
        "1.2+": {"n": 169, "double": 17.8, "single_high": 35.5, "single_low": 38.5, "none": 8.3},
        "all": {"n": 3249, "double": 44.8, "single_high": 28.0, "single_low": 26.1, "none": 1.1},
    },
}
TBR_P30 = {"quoted_reversal_share_m05_0940_0950": 86.46, "sample_days": 4537}


def _eligible(rows):
    return [r for r in rows if r.get("eligible")]


def _path_counts(rows):
    c = Counter(r.get("path_class") for r in rows)
    n = len(rows)
    return {
        "high-only": c.get("high-only", 0),
        "low-only": c.get("low-only", 0),
        "both": c.get("both", 0),
        "neither": c.get("neither", 0),
        "n": n,
        "sum": c.get("high-only", 0) + c.get("low-only", 0) + c.get("both", 0) + c.get("neither", 0),
    }


def _width_tables(rows):
    w69 = [r["W69"] for r in rows if r.get("W69") is not None]
    wprior = [r["WpriorRTH"] for r in rows if r.get("WpriorRTH") is not None]
    pct = {}
    rel = {}
    for lo, hi in XF_WIDTH_BINS:
        lab = _bin_label(lo, hi)
        pct_rows = [r for r in rows if r.get("width_bin_pct") == lab]
        rel_rows = [r for r in rows if r.get("width_bin_rel") == lab]
        pct[lab] = _path_share_block(pct_rows)
        rel[lab] = _path_share_block(rel_rows)
    pct["all"] = _path_share_block(rows)
    rel["all"] = _path_share_block(rows)
    return {
        "W69_points": {"n": len(w69), "mean": None if not w69 else float(np.mean(w69)), "p50": None if not w69 else float(np.median(w69))},
        "WpriorRTH_points": {"n": len(wprior), "mean": None if not wprior else float(np.mean(wprior)), "p50": None if not wprior else float(np.median(wprior))},
        "w_pct_0859close": pct,
        "w_rel_prior_rth": rel,
        "note": "w_rel_prior_rth bins are not the XF p.24 price-% table",
    }


def _path_share_block(rows):
    n = len(rows)
    counts = _path_counts(rows)
    def share(key):
        k = counts[key]
        block = rate_block(k, n)
        flags = np.array([1.0 if r.get("path_class") == key else 0.0 for r in rows], dtype=np.float64)
        block["session_bootstrap_95"] = session_bootstrap_rate(flags) if n else [None, None]
        return block
    return {
        "n": n,
        "double": share("both"),
        "single_high": share("high-only"),
        "single_low": share("low-only"),
        "none": share("neither"),
    }


def _xf_recompute(rows, slice_id):
    table = _width_tables(rows)["w_pct_0859close"]
    cells = []
    for lab, quoted in XF_P24["rows"].items():
        got = table.get(lab) or _path_share_block([])
        cells.append({
            "bin": lab,
            "quoted": quoted,
            "recomputed": {
                "n": got["n"],
                "double": got["double"]["rate"],
                "single_high": got["single_high"]["rate"],
                "single_low": got["single_low"]["rate"],
                "none": got["none"]["rate"],
                "double_wilson_95": got["double"]["wilson_95"],
            },
            "slice": slice_id,
            "quoted_is_pass_threshold": False,
        })
    return cells


def _reversal_claim(rows, slice_id):
    touched = [r for r in rows if r.get("m05_touch_ms") is not None]
    in_bin = [r for r in touched if r.get("reversal_bin") == "bin.0940-0950"]
    block = rate_block(len(in_bin), len(touched))
    flags = np.array([1.0 if r.get("reversal_bin") == "bin.0940-0950" else 0.0 for r in touched], dtype=np.float64)
    block["session_bootstrap_95"] = session_bootstrap_rate(flags) if touched else [None, None]
    return {
        "quoted": TBR_P30["quoted_reversal_share_m05_0940_0950"] / 100.0,
        "recomputed": block,
        "slice": slice_id,
        "quoted_is_pass_threshold": False,
        "n_touches": len(touched),
        "n_sessions": len(rows),
    }


def _primary_flags(rows, key="path_class", value="both"):
    return np.array([1.0 if r.get(key) == value else 0.0 for r in rows], dtype=np.float64)


def range_documents(f_rows, l_rows, vol_rows, fixtures) -> list[dict]:
    elig = _eligible(f_rows)
    dates = [r["date"] for r in elig]
    both = _primary_flags(elig)
    primary = rate_block(int(both.sum()), len(elig))
    primary["session_bootstrap_95"] = session_bootstrap_rate(both)
    leakage = int(sum(r.get("leakage") or 0 for r in elig))
    failures = int(sum(1 for r in f_rows if r.get("failure")))
    non_touches = int(sum(1 for r in elig if r.get("non_touch_m05")))
    missing_bars = int(sum(r.get("missing_1s") or 0 for r in f_rows))
    counts = _path_counts(elig)
    faithful = {
        "family": "range",
        "variant": "range.6-9.published",
        "faithful_of": None,
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": 0,
        "status": "measured",
        "slice": "F",
        "grid": "G-default",
        "window": {"start": "06:00", "end": "09:00", "outcome_start": "09:30", "outcome_end": "12:00"},
        "params": {"tick": 0.25, "coverage_max_missing": 0.10, "break": "b.c1"},
        "summary": {
            "n": len(elig),
            "primary": primary,
            "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]},
            "by_year": by_year(dates, both),
            "leakage_count": leakage,
            "failures": failures,
            "non_touches": non_touches,
            "missing_bars": missing_bars,
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "path_class_counts": counts,
            "path_class_sum_equals_n": counts["sum"] == counts["n"],
            "width_tables": _width_tables(elig),
            "dropped_sessions": [r["date"] for r in f_rows if not r.get("eligible")],
            "tables": {
                "xf_p24_F": _xf_recompute(elig, "F"),
                "xf_p24_L": _xf_recompute(_eligible(l_rows), "L") if l_rows else [],
                "tbr_p30_F": _reversal_claim(elig, "F"),
                "tbr_p30_L": _reversal_claim(_eligible(l_rows), "L") if l_rows else {},
            },
        },
        "source_claims": _xf_recompute(elig, "F") + [_reversal_claim(elig, "F")],
        "fixtures": fixtures,
        "citations": ["TBR p.30", "TBR p.12", "XF p.24", "XF p.23"],
    }
    elig_u = [r for r in vol_rows if r.get("eligible")]
    by_date_f = {r["date"]: r for r in elig}
    aligned_f, aligned_u = [], []
    disagree = 0
    for u in elig_u:
        f = by_date_f.get(u["date"])
        if f is None:
            continue
        aligned_f.append(1.0 if f.get("path_class") == "both" else 0.0)
        aligned_u.append(1.0 if u.get("path_class") == "both" else 0.0)
        if f.get("path_class") != u.get("path_class"):
            disagree += 1
    af = np.array(aligned_f, dtype=np.float64)
    au = np.array(aligned_u, dtype=np.float64)
    up_primary = rate_block(int(au.sum()) if au.size else 0, int(au.size))
    up_primary["session_bootstrap_95"] = session_bootstrap_rate(au)
    f_primary = rate_block(int(af.sum()) if af.size else 0, int(af.size))
    f_primary["session_bootstrap_95"] = session_bootstrap_rate(af)
    status = status_from_intervals(
        *(up_primary["session_bootstrap_95"] or [None, None]),
        *(f_primary["session_bootstrap_95"] or [None, None]),
    )
    u_dates = [r["date"] for r in elig_u]
    upgrade = {
        "family": "range",
        "variant": "range.6-9.vol-elapsed",
        "faithful_of": "range.6-9.published",
        "n": len(elig_u),
        "n_unit": "sessions",
        "faithful_disagreements": disagree,
        "status": status if elig_u else "null",
        "slice": "F",
        "grid": "G-default",
        "window": {"start": "06:00", "end": "vol-median", "outcome_start": "09:30", "outcome_end": "12:00"},
        "params": {"volume_lookback_sessions": 60},
        "summary": {
            "n": len(elig_u),
            "primary": up_primary,
            "rate_or_mean": {"rate": up_primary["rate"], "mean": up_primary["rate"]},
            "session_bootstrap_95": up_primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": paired_diff(au, af) if af.size and au.size == af.size else {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
            "by_year": by_year(u_dates, au) if elig_u else by_year([], np.array([])),
            "leakage_count": int(sum(r.get("leakage") or 0 for r in elig_u)),
            "failures": int(sum(1 for r in vol_rows if r.get("failure"))),
            "non_touches": int(sum(1 for r in elig_u if r.get("non_touch_m05"))),
            "missing_bars": int(sum(r.get("missing_1s") or 0 for r in vol_rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "path_class_counts": _path_counts(elig_u),
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["TBR p.7", "BRIEF derived ranges"],
    }
    for doc in (faithful, upgrade):
        bad = quality_failures(doc)
        doc["quality_bar_pass"] = not bad
        doc["quality_bar_failures"] = bad
    return [faithful, upgrade]


def ensure_tables(*, with_l: bool = True):
    f_rows = load_rows("sessions_F")
    if not f_rows:
        print("building F session table", flush=True)
        f_rows = build_slice("F", use_1s=True)
        save_rows("sessions_F", f_rows)
    l_rows = load_rows("sessions_L")
    if with_l and not l_rows:
        print("building L session table (1m)", flush=True)
        l_rows = build_slice("L", use_1s=False)
        save_rows("sessions_L", l_rows)
    vol_rows = load_rows("range_vol_elapsed_F")
    if not vol_rows:
        print("building vol-elapsed upgrade", flush=True)
        vol_rows = add_vol_elapsed(f_rows, "F")
        save_rows("range_vol_elapsed_F", vol_rows)
    return f_rows, l_rows, vol_rows


def report_range():
    fixtures = run_ticket01_fixtures()
    f_rows, l_rows, vol_rows = ensure_tables(with_l=True)
    docs = range_documents(f_rows, l_rows, vol_rows, fixtures)
    from trading_research.research.phase1_live.family_clocks import report_clocks
    docs.extend(report_clocks(f_rows, fixtures))
    for doc in docs:
        write_report(doc)
    return docs
