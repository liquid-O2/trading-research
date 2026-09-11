#!/usr/bin/env python3
"""Set each FORMULAS.md Code verdict to match recipe_score.catalog()."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/workspace")
FORMULAS = ROOT / "planning/phase-1-live/FORMULAS.md"
sys.path.insert(0, str(ROOT / "implementation/src"))
from trading_research.research.phase1_live.recipe_score import catalog

HEAD = re.compile(r"^### (R-[A-Z]\d+) ")
CODE = re.compile(r"^(- \*\*Code\.\*\* \*\*)([^*]+)(\*\*)")

WORD = {
    "pass": "match",
    "blocked": "blocked",
    "gap": "missing (input)",
}


def main() -> int:
    cat = {r["id"]: r["impl_fidelity"] for r in catalog()}
    lines = FORMULAS.read_text(encoding="utf-8").splitlines(True)
    rid = None
    n = 0
    out = []
    for line in lines:
        m = HEAD.match(line)
        if m:
            rid = m.group(1)
            out.append(line)
            continue
        c = CODE.match(line)
        if c and rid in cat:
            word = WORD[cat[rid]]
            line = CODE.sub(rf"\g<1>{word}\g<3>", line, count=1)
            n += 1
            rid = None
        out.append(line)
    FORMULAS.write_text("".join(out), encoding="utf-8")
    print(f"patched {n} Code bullets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
