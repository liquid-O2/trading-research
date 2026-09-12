#!/usr/bin/env python3
"""Rerun object F1 + C08 mutations. Exit 1 on any fail."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_research.research.method_pack.catalog import METHOD_OBJECTS
from trading_research.research.method_pack.objects import FIXTURES, RECIPES, c08_mutations, run_fixture_spec


def main() -> int:
    wanted = sys.argv[1:]
    if not wanted:
        wanted = sorted({oid for ids in METHOD_OBJECTS.values() for oid in ids})
    missing = [oid for oid in wanted if oid not in RECIPES]
    rows = []
    for spec in FIXTURES:
        if spec["recipe"] not in wanted:
            continue
        rows.append(run_fixture_spec(spec))
        rows.extend(c08_mutations(spec))
    fails = [r for r in rows if r.get("status") != "pass"]
    print(f"recipes={len(RECIPES)} missing={len(missing)} fixtures={len(rows)} fails={len(fails)}")
    for oid in missing:
        print(f"missing {oid}")
    for row in fails[:50]:
        print(f"fail {row.get('id')} {row.get('failures')}")
    return 1 if missing or fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
