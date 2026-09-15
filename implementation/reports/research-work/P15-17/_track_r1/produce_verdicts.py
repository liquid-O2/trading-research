#!/usr/bin/env python3
"""Measure candidate vs B0.1 verdicts on the 9-date engineering slice."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

from trading_research.research.rule_discovery.source_adapters.common import (  # noqa: E402
    PRIMARY_BRANCH,
    changed_axis_spec,
    changed_formation_scan,
    changed_reference_scan,
    install_write_guard,
    load_source_market,
    population_counts,
)
from trading_research.research.rule_discovery.source_adapters.confirmation import CONFIRMATION_RULE  # noqa: E402

SLICE = [
    "2020-01-02",
    "2021-01-04",
    "2022-01-03",
    "2023-01-03",
    "2023-11-06",
    "2024-01-02",
    "2025-01-02",
    "2026-01-02",
    "2026-09-03",
]
OUT = Path(__file__).resolve().parent


def _tally(episodes):
    counts = population_counts({"episodes": episodes})
    verdicts = Counter(str(ep.get("research_verdict") or "") for ep in episodes)
    counts["pass"] = int(verdicts.get("pass", 0))
    counts["fail"] = int(verdicts.get("fail", 0))
    if counts["pass"] == 0 and counts["fail"] == 0:
        counts["pass"] = int(counts.get("setup", 0))
        counts["fail"] = int(counts.get("no_setup", 0) + counts.get("rejected", 0))
    return counts


def main() -> int:
    install_write_guard()
    families = {}
    f1_total = Counter()
    r_total = Counter()
    b01_total = Counter()
    for day in SLICE:
        market = load_source_market(day)
        for _task, (family, branch) in PRIMARY_BRANCH.items():
            row = families.setdefault(
                family,
                {
                    "family": family,
                    "branch": branch,
                    "rule": CONFIRMATION_RULE.get(family, {}),
                    "b01": Counter(),
                    "f1": Counter(),
                    "r": Counter(),
                    "candidate": Counter(),
                },
            )
            formation = changed_formation_scan(market, None, changed_axis_spec(family, branch, "Formation", recipe="F1"))
            reference = changed_reference_scan(market, None, changed_axis_spec(family, branch, "Reference", recipe="R-quadrant"))
            f1_eps = list(formation.get("episodes") or [])
            r_eps = list(reference.get("episodes") or [])
            b01_pop = dict((formation.get("populations") or {}).get("B0.1") or {})
            for dest, tallied in (
                (row["b01"], b01_pop),
                (row["f1"], _tally(f1_eps)),
                (row["r"], _tally(r_eps)),
            ):
                for key in ("episodes", "setup", "no_setup", "unknown", "pass", "fail"):
                    dest[key] += int(tallied.get(key, 0) or 0)
            f1_t = _tally(f1_eps)
            r_t = _tally(r_eps)
            f1_total.update({"episodes": f1_t["episodes"], "unknown": f1_t["unknown"], "setup": f1_t["setup"], "no_setup": f1_t["no_setup"]})
            r_total.update({"episodes": r_t["episodes"], "unknown": r_t["unknown"], "setup": r_t["setup"], "no_setup": r_t["no_setup"]})
            b01_total.update({"episodes": int(b01_pop.get("episodes") or 0), "unknown": int(b01_pop.get("unknown") or 0), "setup": int(b01_pop.get("setup") or 0), "no_setup": int(b01_pop.get("no_setup") or 0)})
    for row in families.values():
        for key in ("b01", "f1", "r"):
            row[key] = dict(row[key])
        cand = Counter(row["f1"]) + Counter(row["r"])
        row["candidate"] = dict(cand)
        b01_n = row["b01"].get("episodes") or 0
        cand_n = row["candidate"].get("episodes") or 0
        row["b01_unknown_share"] = (row["b01"].get("unknown") or 0) / b01_n if b01_n else 0.0
        row["candidate_unknown_share"] = (row["candidate"].get("unknown") or 0) / cand_n if cand_n else 0.0
    payload = {
        "schema_version": "track-r1-verdicts-v1",
        "slice": SLICE,
        "families": families,
        "f1_changed_formation": dict(f1_total),
        "r_changed_reference": dict(r_total),
        "b01_primary_jj": dict(b01_total),
        "confirmation_rules": CONFIRMATION_RULE,
    }
    (OUT / "VERDICTS.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Track R1 candidate verdicts",
        "",
        "family | branch | B0.1 n | B0.1 unknown | cand n | cand unknown | B0.1 share | cand share | rule",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for family, row in families.items():
        rule = row["rule"]
        loc = f"{rule.get('file', '')}:{rule.get('line', '')} {rule.get('name', '')}"
        lines.append(
            f"{family} | {row['branch']} | {row['b01'].get('episodes', 0)} | {row['b01'].get('unknown', 0)} | "
            f"{row['candidate'].get('episodes', 0)} | {row['candidate'].get('unknown', 0)} | "
            f"{row['b01_unknown_share']:.3f} | {row['candidate_unknown_share']:.3f} | {loc}"
        )
    lines.extend(
        [
            "",
            "## F1 and R counts by verdict",
            "",
            f"All-family F1 {dict(f1_total)}",
            f"All-family R {dict(r_total)}",
            f"All-family B0.1 {dict(b01_total)}",
            "",
            "JJ-TBR primary (orchestrator cited 84 F1 and 156 R against B0.1 10):",
            f"F1 {families.get('JJ-TBR', {}).get('f1')}",
            f"R {families.get('JJ-TBR', {}).get('r')}",
            f"B0.1 {families.get('JJ-TBR', {}).get('b01')}",
            "",
            "Measured counts restated by verdict. Unknown share uses strategy_assessment status.",
        ]
    )
    (OUT / "VERDICTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
