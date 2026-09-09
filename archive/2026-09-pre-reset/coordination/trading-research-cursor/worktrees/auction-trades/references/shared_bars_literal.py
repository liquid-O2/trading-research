"""Independent scalar F09 oracle on primitive source dictionaries.

No candidate summary, merge, publication, restore or selection helper is used.
Each requested clock traverses the original rows from the start.
"""

from collections import defaultdict


def literal_summary(records):
    rows = sorted(records, key=lambda r: (r["event_at"], -1 if r["order"] is None else r["order"], r["id"]))
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("repeated literal source identity")
    groups = defaultdict(list)
    for row in rows:
        groups[row["event_at"]].append(row)
    exact = all(len(group) == 1 or (all(r["order"] is not None for r in group)
                   and len({r["order"] for r in group}) == len(group)) for group in groups.values())

    def endpoint(group, last=False):
        if len(group) == 1 or (all(r["order"] is not None for r in group)
                              and len({r["order"] for r in group}) == len(group)):
            return sorted(group, key=lambda r: -1 if r["order"] is None else r["order"])[-1 if last else 0]["price"]
        values = {r["price"] for r in group}
        return next(iter(values)) if len(values) == 1 else None

    volume = priced_volume = unpriced_volume = pv = p2v = buy = sell = unknown = 0
    cumulative = high = low = 0
    prices = []
    for r in rows:
        q = r["size"]
        volume += q
        if r["price"] is None:
            unpriced_volume += q
        else:
            prices.append(r["price"])
            priced_volume += q
            pv += r["price"] * q
            p2v += r["price"] ** 2 * q
        if r["side"] == 1:
            buy += q
            cumulative += q
        elif r["side"] == -1:
            sell += q
            cumulative -= q
        else:
            unknown += q
        high, low = max(high, cumulative), min(low, cumulative)
    history = all(r["history_complete"] for r in rows)
    first = groups[rows[0]["event_at"]] if rows else []
    last = groups[rows[-1]["event_at"]] if rows else []
    return {
        "event_ids": tuple(r["id"] for r in rows),
        "content_versions": tuple(r["source_content_version"] for r in rows),
        "first_at": rows[0]["event_at"] if rows else None,
        "last_at": rows[-1]["event_at"] if rows else None,
        "open_ticks": endpoint(first) if first else None,
        "high_ticks": max(prices, default=None), "low_ticks": min(prices, default=None),
        "close_ticks": endpoint(last, True) if last else None,
        "volume": volume, "priced_volume": priced_volume, "unpriced_volume": unpriced_volume,
        "sum_pv": pv, "sum_p2v": p2v, "buy": buy, "sell": sell, "unknown": unknown,
        "signed": buy - sell, "prints": len(rows), "history_complete": history, "order_exact": exact,
        "signed_bounds": (buy - sell - unknown, buy - sell + unknown) if history else None,
        "cvd_high": high if exact and history and not unknown else None,
        "cvd_low": low if exact and history and not unknown else None,
        "minimum_known_at": max((r["known_at"] for r in rows), default=None),
    }


def literal_windows(records, windows, *, cut):
    results, source_visits = [], 0
    for start, end in windows:
        selected = []
        for row in records:
            source_visits += 1
            if start <= row["event_at"] < end and row["event_at"] <= cut and row["known_at"] <= cut:
                selected.append(row)
        results.append(literal_summary(selected))
    return tuple(results), source_visits


def literal_activity(records, *, kind, threshold, initial_epoch, resets=(), opening=0):
    rows = sorted(records, key=lambda r: (r["event_at"], -1 if r["order"] is None else r["order"], r["id"]))
    all_summary = literal_summary(rows)
    if not all_summary["order_exact"] or not all_summary["history_complete"]:
        return {"available": False, "reason": "unordered_or_missing_history", "completed": [], "forming": None}
    if kind == "range" and any(r["price"] is None for r in rows):
        return {"available": False, "reason": "unpriced_range_threshold", "completed": [], "forming": None}
    events = [(r["event_at"], 1, i, r) for i, r in enumerate(rows)]
    boundaries = [(r["event_at"], 0, i, r) for i, r in enumerate(resets)]
    schedule = sorted(events + boundaries, key=lambda r: r[:3])
    completed, pending, epoch, carry = [], [], initial_epoch, opening
    reset_known = None

    def close(state, reached, endpoint=None):
        summary = literal_summary(pending)
        amount = len(pending) if kind == "events" else (summary["volume"] if kind == "volume"
                 else max(r["price"] for r in pending) - min(r["price"] for r in pending))
        return {"event_ids": tuple(r["id"] for r in pending), "summary": summary, "state": state,
                "threshold_reached": reached, "overshoot": amount - threshold if reached else None,
                "opening_cvd": carry, "reset_epoch": epoch, "index": len(completed),
                "interval": (pending[0]["event_at"], pending[-1]["event_at"] + 1 if endpoint is None else endpoint),
                "minimum_known_at": max([r["known_at"] for r in pending] + ([] if reset_known is None else [reset_known]))}

    for _, type_order, _, r in schedule:
        if type_order == 0:
            reset_known = max(r["event_at"], r["known_at"])
            if pending:
                completed.append(close("reset_partial", False, r["event_at"]))
            pending, carry, epoch = [], 0, r["new_epoch_id"]
            continue
        pending.append(r)
        amount = len(pending) if kind == "events" else (sum(v["size"] for v in pending) if kind == "volume"
                 else max(v["price"] for v in pending) - min(v["price"] for v in pending))
        if amount >= threshold:
            completed.append(close("threshold", True))
            carry = None if carry is None or any(v["side"] is None for v in pending) else carry + sum(v["side"] * v["size"] for v in pending)
            pending = []
    forming = close("forming", False) if pending else None
    return {"available": True, "reason": None, "completed": completed, "forming": forming}


def literal_coarse(bars):
    rows = sorted(bars, key=lambda r: r["start"])
    body = [r["body_envelope"] for r in rows]
    return {"ohlc": (rows[0]["ohlc"][0], max(r["ohlc"][1] for r in rows),
                     min(r["ohlc"][2] for r in rows), rows[-1]["ohlc"][3]),
            "body_envelope": (min(b[0] for b in body), max(b[1] for b in body)) if all(b is not None for b in body) else None}
