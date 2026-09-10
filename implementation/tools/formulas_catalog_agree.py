#!/usr/bin/env python3
"""Fail unless FORMULAS.md Code bullets agree with recipe_score.catalog().

Expected mapping:
  blocked -> blocked
  missing (input) -> gap
  match / match with named departure / match on ... -> pass
  mismatch / invented / missing / stand-in -> must not be catalog pass
    until the Code bullet is updated after a recode.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/workspace")
FORMULAS = ROOT / "planning/phase-1-live/FORMULAS.md"
sys.path.insert(0, str(ROOT / "implementation/src"))

from trading_research.research.phase1_live.recipe_score import catalog  # noqa: E402


BLOCK_RE = re.compile(r"^### (R-[A-Z]\d+) ")
CODE_RE = re.compile(r"^- \*\*Code\.\*\* \*\*([^*]+)\*\*")


def formulas_verdicts() -> dict[str, str]:
    out: dict[str, str] = {}
    rid = None
    for line in FORMULAS.read_text(encoding="utf-8").splitlines():
        m = BLOCK_RE.match(line)
        if m:
            rid = m.group(1)
            continue
        if rid is None:
            continue
        c = CODE_RE.match(line)
        if not c:
            continue
        raw = c.group(1).strip().lower()
        if raw.startswith("blocked") or raw == "blocked":
            out[rid] = "blocked"
        elif "missing (input)" in raw:
            out[rid] = "gap"
        elif any(w in raw for w in ("mismatch", "invented", "stand-in", "stand in", "placeholder")):
            out[rid] = "recode"
        elif raw.startswith("missing"):
            out[rid] = "recode"
        elif raw.startswith("match"):
            out[rid] = "pass"
        else:
            out[rid] = "recode"
        rid = None
    return out


def expected(fid: str) -> str:
    return fid


def main() -> int:
    fv = formulas_verdicts()
    cat = {r["id"]: r["impl_fidelity"] for r in catalog()}
    rows = []
    for rid in sorted(cat, key=lambda x: (x[2], int(x[3:]))) if False else cat:
        pass
    ids = [r["id"] for r in catalog()]
    print("id\tformulas\tcatalog\tok")
    n_bad = 0
    for rid in ids:
        f = fv.get(rid, "missing-block")
        c = cat[rid]
        if f == "pass" and c == "pass":
            ok = True
        elif f == "blocked" and c == "blocked":
            ok = True
        elif f == "gap" and c == "gap":
            ok = True
        elif f == "recode" and c in ("gap", "blocked"):
            ok = True
        else:
            ok = False
        if f == "recode" and c == "pass":
            ok = False
        if f == "pass" and c != "pass":
            ok = False
        if f == "blocked" and c != "blocked":
            ok = False
        mark = "ok" if ok else "DISAGREE"
        if not ok:
            n_bad += 1
        print(f"{rid}\t{f}\t{c}\t{mark}")
        rows.append((rid, f, c, ok))
    print(f"disagree={n_bad} n={len(ids)} formulas_blocks={len(fv)}")
    missing = [i for i in ids if i not in fv]
    extra = [i for i in fv if i not in cat]
    if missing:
        print("no Code bullet", missing)
        n_bad += 1
    if extra:
        print("Code without catalog", extra)
    return 1 if n_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
