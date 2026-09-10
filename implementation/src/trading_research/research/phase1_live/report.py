"""Quality-bar JSON + Markdown twin + PHASE line."""

from __future__ import annotations

from pathlib import Path

from trading_research.operations.artifacts import canonical_json
from trading_research.research.phase1_live import FAMILIES, STATUSES, VERSION

REPORT_ROOT = Path("/workspace/implementation/reports/phase1-live")
QUALITY_KEYS = (
    "n", "n_unit", "faithful_row", "upgrade_rows", "rate_or_mean",
    "session_bootstrap_95", "paired_difference_vs_faithful", "by_year",
    "leakage_count", "failures", "non_touches", "missing_bars",
    "unavailable_map", "unavailable_oi", "fixtures",
)


def report_path(family: str, variant: str) -> Path:
    return REPORT_ROOT / family / f"{variant}.json"


def write_report(doc: dict) -> Path:
    family, variant = doc["family"], doc["variant"]
    path = report_path(family, variant)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(doc)
    path.write_bytes(payload)
    md = path.with_suffix(".md")
    md.write_text(_markdown(doc), encoding="utf-8")
    return path


def phase_line(doc: dict) -> str:
    rel = f"trading-research/reports/phase1-live/{doc['family']}/{doc['variant']}.json"
    return (
        f"{doc['family']} | {doc['variant']} | {doc['n']} | "
        f"{doc['faithful_disagreements']} | {doc['status']} | {rel}"
    )


def quality_failures(doc: dict) -> list[str]:
    bad = []
    if doc.get("family") not in FAMILIES:
        bad.append("unknown family")
    if doc.get("status") not in STATUSES:
        bad.append("unknown status")
    if "n" not in doc or "n_unit" not in doc:
        bad.append("missing n or n_unit")
    if doc.get("n_unit") not in ("sessions", "events"):
        bad.append("n_unit must be sessions or events")
    summary = doc.get("summary") or {}
    if "session_bootstrap_95" not in summary:
        bad.append("missing session_bootstrap_95")
    if "paired_difference_vs_faithful" not in summary:
        bad.append("missing paired_difference_vs_faithful")
    years = (summary.get("by_year") or {})
    for y in ("2024", "2025", "2026"):
        if y not in years:
            bad.append(f"missing by-year {y}")
    if summary.get("leakage_count") not in (0, None) and doc.get("status") == "measured":
        if summary.get("leakage_count") != 0:
            bad.append("leakage_count must be 0")
    for key in ("failures", "non_touches", "missing_bars", "unavailable_map", "unavailable_oi"):
        if key not in summary:
            bad.append(f"missing {key}")
    if "fixtures" not in doc:
        bad.append("missing fixtures")
    if "faithful_of" not in doc:
        bad.append("missing faithful_of")
    if doc.get("status") == "measured" and not (doc.get("summary") or {}).get("rate_or_mean"):
        if doc.get("n", 0) > 0 and "rate" not in (summary.get("primary") or {}) and "mean" not in (summary.get("primary") or {}):
            if summary.get("primary") is None:
                bad.append("missing primary rate or mean")
    source = doc.get("source_claims") or []
    for claim in source:
        if "quoted" in claim and "recomputed" not in claim:
            bad.append("source claim missing recomputed cell")
        if claim.get("quoted_is_pass_threshold"):
            bad.append("source percentage used as pass threshold")
    return bad


def _markdown(doc: dict) -> str:
    lines = [
        f"# {doc['family']} / {doc['variant']}",
        "",
        phase_line(doc),
        "",
        f"n = {doc.get('n')} {doc.get('n_unit')}. status = {doc.get('status')}.",
        f"leakage = {(doc.get('summary') or {}).get('leakage_count')}.",
        f"fixtures pass = {(doc.get('fixtures') or {}).get('pass')}.",
        "",
    ]
    return "\n".join(lines) + "\n"
