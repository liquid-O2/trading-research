"""Independent primitive arithmetic for frozen M01/M02/M10 engineering cases.

No imports from the candidate package. No source data acquisition or fitting.
"""

from fractions import Fraction
import hashlib
from itertools import groupby, permutations, product
import json


def wire(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(wire(value)).hexdigest()


def flow(rows, *, complete=True):
    buy = sum(r["size"] for r in rows if r["side"] == 1)
    sell = sum(r["size"] for r in rows if r["side"] == -1)
    unknown = sum(r["size"] for r in rows if r["side"] is None)
    return {"buy": buy, "sell": sell, "unknown": unknown, "signed": buy - sell,
            "total": buy + sell + unknown, "prints": len(rows),
            "true_bounds": (buy - sell - unknown, buy - sell + unknown) if complete else None}


def paths(rows, opening=0):
    groups = []
    for _, group in groupby(sorted(rows, key=lambda r: r["event_at"]), key=lambda r: r["event_at"]):
        batch = tuple(group)
        if len(batch) > 8:
            raise ValueError("literal enumeration bound")
        ordered = len(batch) <= 1 or (all(r["order"] is not None for r in batch)
                                     and len({r["order"] for r in batch}) == len(batch))
        groups.append((tuple(sorted(batch, key=lambda r: r["order"] or 0)),) if ordered else tuple(permutations(batch)))
    if sum(len(g) for g in groups) > 4096:
        raise ValueError("literal path bound")
    extremes = []
    for sequence in product(*groups):
        value = opening
        values = [value]
        for group in sequence:
            for row in group:
                value += (row["side"] or 0) * row["size"]
                values.append(value)
        extremes.append((max(values), min(values), value))
        if len(extremes) > 4096:
            raise ValueError("literal path bound")
    return {"open": opening, "close": extremes[0][2],
            "high_bounds": (min(r[0] for r in extremes), max(r[0] for r in extremes)),
            "low_bounds": (min(r[1] for r in extremes), max(r[1] for r in extremes))}


def legacy_envelope(rows, request):
    """Independent full common-window bytes for exact capacity/identity tests."""
    rows = sorted(rows, key=lambda r: (r["event_at"], -1 if r["order"] is None else r["order"], r["id"]))
    coverage = request["coverage"]
    duration = sum(b - a for a, b in coverage["observed_intervals"])
    history = duration == request["end"] - request["start"] and all(r["history_complete"] for r in rows)
    totals = flow(rows)
    ties = {}
    for row in rows:
        ties.setdefault(row["event_at"], []).append(row["order"])
    ordered = all(len(g) <= 1 or None not in g and len(set(g)) == len(g) for g in ties.values())
    window = {**request, "source_kind": "legacy_trade", "source_domains": [],
              "source_versions": sorted((r["id"], r["source_content_version"]) for r in rows),
              "correction_ids": [], "contribution_hash": sha(rows), "coverage_id": sha(coverage),
              "observed_duration_ns": duration,
              "support_status": "unobserved" if not duration else "complete" if history else "partial",
              "history_complete": history, "eligible_volume": totals["total"], "excluded_volume": 0,
              "buy_volume": totals["buy"], "sell_volume": totals["sell"], "unknown_volume": totals["unknown"],
              "unpriced_volume": sum(r["size"] for r in rows if r["price"] is None),
              "print_count": len(rows), "order_exact": ordered, "covered_print_count": len(rows), "source_bar_version": None}
    return {"window": window, "trades": rows}


def exact_byte_capacity(rows, request):
    limit = 0
    for _ in range(20):
        next_limit = len(wire(legacy_envelope(rows, {**request, "max_bytes": limit})))
        if next_limit == limit:
            return limit
        limit = next_limit
    raise ValueError("literal envelope size did not stabilize")


def weighted_quantile(sizes, p, *, volume=False):
    total = sum(sizes) if volume else len(sizes)
    cumulative = 0
    for value in sorted(sizes):
        cumulative += value if volume else 1
        if Fraction(cumulative, total) >= p:
            return value
    raise ValueError("empty distribution")


def flow_baseline(rows, exposure):
    total_exposure = sum(r[0] for r in rows)
    return tuple(sum(r[j] for r in rows) * Fraction(exposure, total_exposure) for j in (1, 2, 3))
