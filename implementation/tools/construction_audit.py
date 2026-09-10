"""Rerunnable construction-audit lever. Reads reports and tables. Writes a TSV."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live.clocks import CLOCKS
from trading_research.research.phase1_live.compute import load_rows
from trading_research.research.phase1_live.report import REPORT_ROOT

OUT = Path("/workspace/planning/phase-1-live/.audit/lever.tsv")
OPTIONS_ROW_FIELDS = (
    "product", "strike", "spot_at_t", "distance", "tagged", "near", "known_at", "OI_vintage",
)
INDEX = {"NDX", "NDXP", "SPX", "SPXW"}


def _reports():
    rows = []
    for path in sorted(REPORT_ROOT.glob("*/*.json")):
        if path.parent.name.startswith("_"):
            continue
        doc = json.loads(path.read_text())
        rows.append((path, doc))
    return rows


def _fixture(doc):
    fx = doc.get("fixtures") or {}
    if not fx:
        return "none"
    cases = [c for g in (fx.get("groups") or []) for c in (g.get("cases") or [])]
    if not cases:
        return "fail" if fx.get("pass") else "none"
    hardcoded = all(c.get("pass") is True and "got" in c for c in cases) and not any(
        isinstance(c.get("got"), (int, float)) and c.get("got") == c.get("expected") for c in cases
    )
    # A case that only restates a string as pass is not a fixture.
    real = False
    for c in cases:
        got, exp = c.get("got"), c.get("expected")
        if isinstance(got, (int, float, bool)) or (isinstance(got, list) and got and not isinstance(got[0], str)):
            real = True
            break
        if isinstance(got, dict):
            real = True
            break
    if not fx.get("pass"):
        return "fail"
    if not real:
        return "fail"
    return "pass" if fx.get("n_failed", 0) == 0 else "fail"


def _options_notes(doc):
    notes = []
    params = doc.get("params") or {}
    sample = (doc.get("summary") or {}).get("sample_nodes") or {}
    variant = doc.get("variant") or ""
    product = str(params.get("product") or sample.get("product") or "").upper()
    if "skylit" in variant:
        if doc.get("status") != "not-measurable":
            notes.append("skylit status must be not-measurable")
        return notes
    if product in INDEX or product in {"QQQ", "SPY", "NQ.OPT", "NQOPT"}:
        for key in OPTIONS_ROW_FIELDS:
            if key == "distance":
                if "distance" not in sample and "distance_points" not in sample and "distance_atr" not in sample:
                    notes.append("missing distance fields")
            elif key not in sample and key not in (sample.get("nodes") or [{}])[0]:
                if sample and key not in sample:
                    notes.append(f"missing {key}")
        if sample.get("mapped_nq") and doc.get("faithful_of") is None and "mapped_nq" not in variant:
            notes.append("mapped_nq mixed into faithful sample")
        if product in INDEX and sample.get("spot_at_t") and "QQQ" in str(sample.get("spot_source", "")):
            notes.append("QQQ labeled as index spot")
        if params.get("cash_minutes_used") is True:
            notes.append("invented cash minutes")
        if product in {"QQQ", "SPY"} and params.get("native") is False:
            notes.append("ETF marked non-native")
        if product in {"NQ.OPT", "NQOPT"} and sample.get("product") in INDEX:
            notes.append("NQ.OPT cloned from index")
    return notes


def _clock_ok(variant, doc):
    if variant not in CLOCKS:
        return None
    spec = CLOCKS[variant]
    window = doc.get("window") or {}
    if not window:
        return "no window in report"
    start = spec.start.strftime("%H:%M")
    end = spec.end.strftime("%H:%M")
    if window.get("start") and window.get("start") != start:
        return f"window start {window.get('start')} != {start}"
    if window.get("end") and window.get("end") not in (end, "vol-median"):
        return f"window end {window.get('end')} != {end}"
    return None


def main() -> int:
    lines = ["family\tid\taudit\tfixture\tleakage\tspike_flag\tnotes"]
    sessions = load_rows("sessions_F")
    leak_sessions = sum(r.get("leakage") or 0 for r in sessions)
    bar_ms = sorted({r.get("source_bar_ms") for r in sessions if r.get("eligible")})
    for path, doc in _reports():
        family = doc.get("family") or path.parent.name
        variant = doc.get("variant") or path.stem
        summary = doc.get("summary") or {}
        leakage = summary.get("leakage_count")
        fixture = _fixture(doc)
        notes = []
        if leakage not in (0, None) and doc.get("status") == "measured":
            notes.append(f"leakage_count={leakage}")
        clock_note = _clock_ok(variant, doc)
        if clock_note:
            notes.append(clock_note)
        if family == "options":
            notes.extend(_options_notes(doc))
        if variant == "flow.cvd.trade":
            notes.append("check 18:00 reset vs AM-only sum in family_flow.scan_trade_cvd")
        if variant == "value.delta.rth.trade":
            extra = (doc.get("params") or {})
            if extra.get("faithful_flag") == "vp_touch":
                notes.append("delta row aliases vp_touch")
        if variant == "env.ss.avgHL60":
            notes.append("code uses half of H-L width; wiki is one-sided 09:00 excursions")
        if family == "range" and variant == "range.6-9.published":
            if bar_ms != [1000]:
                notes.append(f"sessions_F source_bar_ms={bar_ms}")
            if leak_sessions:
                notes.append(f"sessions_F leakage={leak_sessions}")
        spike = "n/a"
        if family in {"range", "path"} and variant.startswith("range."):
            spike = "pending-1s"
        if "mapped_nq" in variant or (family == "options" and (doc.get("summary") or {}).get("sample_nodes", {}).get("mapped_nq")):
            spike = "pending-ratio"
        audit = "pass"
        if doc.get("status") == "not-measurable":
            audit = "not-measurable"
        elif doc.get("status") == "deferred" and "skylit" in variant:
            audit = "fail"
            notes.append("skylit must be not-measurable")
        elif notes and any("missing" in n or "aliases" in n or "cloned" in n or "half of" in n or "mixed" in n for n in notes):
            audit = "fail"
        elif fixture == "fail" and family in {"options", "env", "value", "gap", "block", "tpo", "fail", "flow"}:
            # hardcoded fixture is a fail unless not-measurable
            if doc.get("status") not in {"not-measurable", "deferred"}:
                audit = "fail"
                notes.append("fixture not a real synthetic/dated case")
        if "skylit" in variant:
            audit = "not-measurable" if doc.get("status") == "not-measurable" else audit
        note = "; ".join(notes) if notes else "report present"
        lines.append(f"{family}\t{variant}\t{audit}\t{fixture}\t{leakage}\t{spike}\t{note}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT} rows={len(lines)-1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
