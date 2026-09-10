"""path.6-9.published and judas.depth.-0.5."""

from __future__ import annotations

from collections import Counter

import numpy as np

from trading_research.research.phase1_live.family_range import _eligible, _path_counts, _width_tables, ensure_tables
from trading_research.research.phase1_live.fixtures import run_ticket01_fixtures
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.stats import by_year, paired_diff, rate_block, session_bootstrap_rate, status_from_intervals


def _day_type_counts(rows):
    c = Counter(r.get("day_type") for r in rows)
    return {
        "judas": c.get("judas", 0),
        "single-extended": c.get("single-extended", 0),
        "single-purged": c.get("single-purged", 0),
        "neither": c.get("neither", 0),
        "unmatched": c.get("unmatched", 0),
        "n": len(rows),
    }


def path_documents(f_rows, fixtures) -> list[dict]:
    elig = _eligible(f_rows)
    dates = [r["date"] for r in elig]
    both = np.array([1.0 if r.get("path_class") == "both" else 0.0 for r in elig], dtype=np.float64)
    primary = rate_block(int(both.sum()), len(elig))
    primary["session_bootstrap_95"] = session_bootstrap_rate(both)
    mid = np.array([1.0 if r.get("midretrace") else 0.0 for r in elig], dtype=np.float64)
    mid_block = rate_block(int(mid.sum()), len(elig))
    mid_block["session_bootstrap_95"] = session_bootstrap_rate(mid)
    counts = _path_counts(elig)
    faithful = {
        "family": "path",
        "variant": "path.6-9.published",
        "faithful_of": None,
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": 0,
        "status": "measured",
        "slice": "F",
        "grid": "G-default",
        "window": {"start": "09:30", "end": "12:00", "outcome_start": "09:30", "outcome_end": "12:00"},
        "params": {"break": "b.c1", "width": "w.pct.0859close"},
        "summary": {
            "n": len(elig),
            "primary": primary,
            "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]},
            "by_year": by_year(dates, both),
            "leakage_count": int(sum(r.get("leakage") or 0 for r in elig)),
            "failures": int(sum(1 for r in f_rows if r.get("failure"))),
            "non_touches": int(sum(1 for r in elig if r.get("non_touch_m05"))),
            "missing_bars": int(sum(r.get("missing_1s") or 0 for r in f_rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "path_class_counts": counts,
            "path_class_sum_equals_n": counts["sum"] == counts["n"],
            "day_type_counts": _day_type_counts(elig),
            "width_tables": _width_tables(elig),
            "midretrace": mid_block,
            "source_claim_midretrace_0604": {
                "quoted": 0.604,
                "recomputed": mid_block,
                "quoted_is_pass_threshold": False,
            },
        },
        "source_claims": [{
            "id": "XF p.23 mid-retrace 60.4%",
            "quoted": 0.604,
            "recomputed": mid_block["rate"],
            "n": mid_block["n"],
            "wilson_95": mid_block["wilson_95"],
            "quoted_is_pass_threshold": False,
        }],
        "fixtures": fixtures,
        "citations": ["XF p.24", "XF p.23", "TBR p.6", "TBR p.12"],
    }
    judas = np.array([1.0 if r.get("judas_m05") else 0.0 for r in elig], dtype=np.float64)
    judas_any = np.array([1.0 if r.get("judas") else 0.0 for r in elig], dtype=np.float64)
    j_primary = rate_block(int(judas.sum()), len(elig))
    j_primary["session_bootstrap_95"] = session_bootstrap_rate(judas)
    any_block = rate_block(int(judas_any.sum()), len(elig))
    any_block["session_bootstrap_95"] = session_bootstrap_rate(judas_any)
    disagree = int(np.sum(judas != judas_any))
    status = status_from_intervals(
        *(j_primary["session_bootstrap_95"] or [None, None]),
        *(any_block["session_bootstrap_95"] or [None, None]),
    )
    upgrade = {
        "family": "path",
        "variant": "judas.depth.-0.5",
        "faithful_of": "path.6-9.published",
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": disagree,
        "status": status if elig else "null",
        "slice": "F",
        "grid": "G-default",
        "window": {"start": "09:30", "end": "12:00", "outcome_start": "09:30", "outcome_end": "12:00"},
        "params": {"judas": "reach -0.5 then close through EQ"},
        "summary": {
            "n": len(elig),
            "primary": j_primary,
            "rate_or_mean": {"rate": j_primary["rate"], "mean": j_primary["rate"]},
            "session_bootstrap_95": j_primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": paired_diff(judas, judas_any),
            "by_year": by_year(dates, judas),
            "leakage_count": int(sum(r.get("leakage") or 0 for r in elig)),
            "failures": int(sum(1 for r in f_rows if r.get("failure"))),
            "non_touches": int(sum(1 for r in elig if r.get("non_touch_m05"))),
            "missing_bars": int(sum(r.get("missing_1s") or 0 for r in f_rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "day_type_counts": _day_type_counts(elig),
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["TBR p.6", "TBR p.8"],
    }
    for doc in (faithful, upgrade):
        bad = quality_failures(doc)
        doc["quality_bar_pass"] = not bad
        doc["quality_bar_failures"] = bad
    return [faithful, upgrade]


def report_path():
    fixtures = run_ticket01_fixtures()
    f_rows, _, _ = ensure_tables(with_l=False)
    docs = path_documents(f_rows, fixtures)
    from trading_research.research.phase1_live.family_levels import report_levels
    docs.extend(report_levels())
    for doc in docs:
        write_report(doc)
    return docs
