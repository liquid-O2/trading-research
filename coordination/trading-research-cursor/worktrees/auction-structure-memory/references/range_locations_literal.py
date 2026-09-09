"""Independent literal oracle for registered C01/L01 engineering vectors.

No candidate/foundation imports, serializers, geometry helpers or reducers are
used here. The tiny lists and exact Fractions are deliberately direct.
"""
from fractions import Fraction


def q(value):
    if type(value) is int:
        return Fraction(value)
    if type(value) is Fraction:
        return value
    raise ValueError("oracle expects exact rational ticks")


def literal_range(ohlc):
    opening, high, low, close = (None if v is None else q(v) for v in ohlc)
    if high is None or low is None or high < low:
        raise ValueError("oracle needs ordered H/L")
    width = high-low
    point = lambda x: low+x*width if width else None
    return {"open": opening, "high": high, "low": low, "close": close, "width": width,
            "quarter25": point(Fraction(1, 4)), "eq": point(Fraction(1, 2)),
            "quarter75": point(Fraction(3, 4)), "range_open": opening,
            "upper_half": high+width/2 if width else None,
            "lower_half": low-width/2 if width else None,
            "upper_one": high+width if width else None,
            "lower_one": low-width if width else None,
            "upper_edge_133": high+Fraction(133, 100)*width if width else None,
            "lower_edge_133": low-Fraction(133, 100)*width if width else None,
            "normalized_133": point(Fraction(133, 100)),
            "source_body25": None if opening is None or close is None else (3*close+opening)/4,
            "session_body_lower25": None if opening is None or close is None else min(opening, close)+abs(close-opening)/4,
            "price_percent": width/opening if opening not in (None, 0) else None}


def literal_ohlc(rows, *, start, end, cut):
    visible = [r for r in rows if r["known_s"] <= cut and start <= r["event_s"] < end]
    visible.sort(key=lambda r: (r["event_s"], -1 if r.get("order", 1) is None else r.get("order", 1), r["id"]))
    if not visible:
        return {"ids": (), "ohlc": (None, None, None, None), "first": None, "last": None}
    def edge(at, terminal):
        candidates = [r for r in visible if r["event_s"] == at]
        orders = [r.get("order", 1) for r in candidates]
        if len(candidates) == 1 or None not in orders and len(set(orders)) == len(orders):
            candidates.sort(key=lambda r: -1 if r.get("order", 1) is None else r.get("order", 1))
            return candidates[-1 if terminal else 0].get("ticks")
        prices = {r.get("ticks") for r in candidates}
        return next(iter(prices)) if len(prices) == 1 else None
    priced = [r["ticks"] for r in visible if r.get("ticks") is not None]
    first, last = visible[0]["event_s"], visible[-1]["event_s"]
    return {"ids": tuple(r["id"] for r in visible),
            "ohlc": (edge(first, False), max(priced) if priced else None,
                     min(priced) if priced else None, edge(last, True)), "first": first, "last": last}


def literal_relation(left, right):
    a0, a1 = left["formation_s"]
    b0, b1 = right["formation_s"]
    s, e = max(a0, b0), min(a1, b1)
    shared = ((s, e),) if s < e else ()
    def unique(x0, x1):
        if not shared:
            return ((x0, x1),)
        return tuple((x, y) for x, y in ((x0, s), (e, x1)) if x < y)
    al, ah, bl, bh = map(q, (left["low"], left["high"], right["low"], right["high"]))
    pr = ("equal" if (al, ah) == (bl, bh) else "B_inside_A" if al <= bl <= bh <= ah else
          "A_inside_B" if bl <= al <= ah <= bh else "disjoint" if ah < bl or bh < al else
          "touching" if ah == bl or bh == al else "overlap")
    tr = ("equal" if (a0, a1) == (b0, b1) else "B_inside_A" if a0 <= b0 and b1 <= a1 else
          "A_inside_B" if b0 <= a0 and a1 <= b1 else "overlap" if shared else "disjoint")
    return {"shared": shared, "a_unique": unique(a0, a1), "b_unique": unique(b0, b1),
            "price_relation": pr, "time_relation": tr, "overlap_width": max(Fraction(0), min(ah, bh)-max(al, bl)),
            "relative_width": (bh-bl)/(ah-al) if ah != al else None}


def literal_e0(current, prior):
    r = literal_range(current)
    current_result = [] if not r["width"] else [r[n] for n in ("high", "low", "eq", "quarter25", "quarter75",
                                                               "upper_half", "lower_half", "upper_one", "lower_one")]
    return tuple(current_result), tuple(None if v is None else q(v) for v in (prior[1], prior[2], prior[0], prior[3]))


def literal_profile(histogram):
    expanded = sorted(price for price, count in histogram for _ in range(count))
    n = len(expanded)
    counts = {price: expanded.count(price) for price in set(expanded)}
    peak = max(counts.values())
    modes = [p for p, count in counts.items() if count == peak]
    return {"POC": q(modes[0]) if len(modes) == 1 else None,
            "median": Fraction(expanded[(n-1)//2]+expanded[n//2], 2),
            "VWAP": Fraction(sum(expanded), n)}


def literal_comparators(sessions, current_open, weights, dispersion):
    high = [q(row["high"]) for row in sessions]
    excursions = [q(row["high"])-q(row["open"]) for row in sessions]
    mass = sum(weights)
    data = [q(v) for v in dispersion]
    average = sum(data)/len(data)
    sumsquares = sum((v-average)**2 for v in data)
    return {"absolute_high_mean": sum(high)/len(high),
            "anchored_high_excursion_mean": q(current_open)+sum(excursions)/len(excursions),
            "illustrative_weighted_absolute_high_mean": sum(v*w for v, w in zip(high, weights))/mass,
            "illustrative_weighted_anchored_excursion_mean": q(current_open)+sum(v*w for v, w in zip(excursions, weights))/mass,
            "population_variance": sumsquares/len(data), "sample_variance": sumsquares/(len(data)-1)}


def literal_diagnostic(observations, *, point, decision, end, extension):
    rows = [(at, q(p)) for at, p in observations if decision <= at < end]
    contacts = [at for at, p in rows if p == point]
    first = min(contacts) if contacts else None
    after = [p for at, p in rows if first is not None and at >= first]
    extensions = [at for at, p in rows if p >= extension]
    return {"first": first, "extension": min(extensions) if extensions else None,
            "maximum": max(after) if after else None, "minimum": min(after) if after else None}


def literal_sampled(grid, observations, point, tolerance):
    return tuple(t for t in grid if any(at == t and abs(q(p)-q(point)) <= tolerance for at, p in observations))


def literal_horizon_status(decision, end, intervals, contact):
    # Direct tiny-fixture coverage union; endpoint is fixed independently of contact.
    missing = [(decision, end)]
    for lo, hi in intervals:
        next_missing = []
        for a, b in missing:
            if hi <= a or b <= lo:
                next_missing.append((a, b))
            else:
                if a < lo:
                    next_missing.append((a, lo))
                if hi < b:
                    next_missing.append((hi, b))
        missing = next_missing
    return "censored" if missing else "observed_no_contact" if contact is None else "observed_contact"
