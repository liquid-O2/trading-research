#!/usr/bin/env python3
"""Build missing recipe objects, write reports, write RULES_SCORES.md."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_research.research.phase1_live.family_clocks import report_clocks
from trading_research.research.phase1_live.family_env import report_env
from trading_research.research.phase1_live.family_fail import report_fail
from trading_research.research.phase1_live.family_levels import report_levels
from trading_research.research.phase1_live.family_range import ensure_tables
from trading_research.research.phase1_live.fixtures import run_ticket01_fixtures
from trading_research.research.phase1_live.recipe_score import catalog, score_all
from trading_research.research.phase1_live.report import write_report


def main() -> int:
    f_rows, _, _ = ensure_tables(with_l=False)
    fixtures = run_ticket01_fixtures()
    for doc in report_clocks(f_rows, fixtures):
        write_report(doc)
    report_env()
    report_fail()
    report_levels()
    cat, path = score_all()
    n = len(cat)
    n_pass = sum(1 for r in cat if r["impl_fidelity"] == "pass")
    n_gap = sum(1 for r in cat if r["impl_fidelity"] == "gap")
    n_blocked = sum(1 for r in cat if r["impl_fidelity"] == "blocked")
    print(f"wrote {path} recipes={n} pass={n_pass} gap={n_gap} blocked={n_blocked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
