"""The break-and-retest cycle on a level, as the authors trade it and as the
accepted ticket replay matched it (Sires K2345 p.7, NYAM p.9; Saint TRAP
pp.6-7: "wait for a breakout of the intraday range, then wait again for price
to come back and retest it").

A break is a bar whose extreme trades through the level after a close on the
inside. After it, price must first depart (twenty-five points, half the
spacing of Saint's intraday levels) and then the first bar that comes back
within fifteen points of the level from the broken side, without any close
back through it by more than a point, is a retest; each new departure allows
one more retest, three at most. A close back through the level by more than
FAIL_MARGIN ends the cycle, and the next break needs a close back on the
inside first (2026-08-10: the 29,740 break at 18:31, the 19:0x retest, the
19:23 departure and the 19:47 retest that is the ticket).

Shared by the Saint scanner and ``tools/replay_sires.py`` so the population
scans the rule the ticket replay was accepted on.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping, Sequence

FAIL_MARGIN = Decimal("1")
RETEST_INSIDE = Decimal("2")
DEPARTURE_POINTS = RETEST_INSIDE * 12
RETEST_POINTS = RETEST_INSIDE * 7
MAX_RETESTS = 3


def break_retest_cycles(rows: Sequence[Mapping[str, Any]], level: Decimal, side: str, *, max_breaks: int = 30, retest_window: int = 90) -> list[dict[str, Any]]:
    """Cycles of ``{"index", "break", "retests": [{"index", "bar", "extreme", "retest"}]}``
    on ``rows`` (bars with O/H/L/C), ``side`` the direction of the break."""
    level = Decimal(str(level))
    out: list[dict[str, Any]] = []
    n = 0
    i = 0
    while i < len(rows) and n < max_breaks:
        bar = rows[i]
        inside_before = i == 0 or ((rows[i - 1]["C"] <= level) if side == "long" else (rows[i - 1]["C"] >= level))
        through = (bar["H"] > level) if side == "long" else (bar["L"] < level)
        if not (inside_before and through):
            i += 1
            continue
        cycle = {"index": i, "break": bar, "retests": []}
        departed = False
        for j in range(i + 1, min(len(rows), i + 1 + retest_window)):
            b = rows[j]
            back_through = (b["C"] < level - FAIL_MARGIN) if side == "long" else (b["C"] > level + FAIL_MARGIN)
            if back_through:
                break
            away = (b["H"] >= level + DEPARTURE_POINTS) if side == "long" else (b["L"] <= level - DEPARTURE_POINTS)
            if away:
                departed = True
            near = departed and ((b["L"] <= level + RETEST_POINTS) if side == "long" else (b["H"] >= level - RETEST_POINTS))
            if near:
                cycle["retests"].append({"index": j, "bar": b, "extreme": b["L"] if side == "long" else b["H"], "retest": len(cycle["retests"])})
                departed = False
                if len(cycle["retests"]) >= MAX_RETESTS:
                    break
        out.append(cycle)
        n += 1
        i += 1
        while i < len(rows) and not ((rows[i]["C"] <= level) if side == "long" else (rows[i]["C"] >= level)):
            i += 1
    return out
