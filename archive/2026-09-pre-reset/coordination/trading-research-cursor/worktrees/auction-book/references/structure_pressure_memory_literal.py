"""Independent primitive equations; no production measurement imports."""

from fractions import Fraction
from itertools import permutations, product


def disagreement(a, b, side, price_scale, flow_scale, tolerance=0):
    dp, df = Fraction(b[0]-a[0]), Fraction(b[1]-a[1])
    tie = abs(dp) <= tolerance or df == 0
    regular = (dp>0 and df<0) if side == "high" else (dp<0 and df>0)
    hidden = (dp<0 and df>0) if side == "high" else (dp>0 and df<0)
    return {"price": dp/price_scale, "flow": df/flow_scale, "discrepancy": dp/price_scale-df/flow_scale,
            "tie": tie, "regular": bool(regular and not tie), "hidden": bool(hidden and not tie)}


def breach(path, times, reference, *, high=True, supported=True):
    if not supported:
        return None, None
    at = [t for p, t in zip(path, times) if p>reference if high] if high else [t for p, t in zip(path, times) if p<reference]
    return bool(at), min(at) if at else None


def pivots(bars, left=1, right=1, ties="strict", cut=10**30):
    # Primitive bar rows: (start,end,high,low,published,complete).
    result = []
    available = [b for b in bars if b[4] <= cut]
    for index, center in enumerate(available):
        if index < left or index+right >= len(available):
            continue
        group = available[index-left:index+right+1]
        if not all(b[5] for b in group) or any(a[1] != b[0] for a, b in zip(group, group[1:])):
            continue
        for column, side in ((2, "high"), (3, "low")):
            values = [b[column] for b in group]
            target = max(values) if side == "high" else min(values)
            equal = [j for j, value in enumerate(values) if value == target]
            if center[column] != target:
                continue
            include = len(equal)==1 if ties=="strict" else equal[0]==left if ties=="earliest" else equal[-1]==left if ties=="latest" else True
            if include:
                result.append((side, center[column], center[0], max(b[4] for b in group)))
    return tuple(result)


def directional(prices, times, threshold, complete=None):
    segment, output, trend = [], [], 0
    complete = [True]*len(prices) if complete is None else complete
    for p, t, supported in zip(prices, times, complete):
        if not supported:
            segment, trend = [], 0
            continue
        segment.append((p, t))
        if len(segment)<2:
            continue
        high = max(segment, key=lambda item: item[0])
        low = min(segment, key=lambda item: item[0])
        extreme = high if trend>=0 and high[0]-p>=threshold else low if trend<=0 and p-low[0]>=threshold else None
        if extreme is not None:
            side = "high" if extreme == high else "low"
            output.append((side, extreme[0], extreme[1], t))
            trend = -1 if side == "high" else 1
            segment = [(p, t)]
    return tuple(output)


def quote(previous, current):
    b0, a0, qb0, qa0 = map(Fraction, previous)
    b, a, qb, qa = map(Fraction, current)
    valid = b<=a and qb>0 and qa>0
    if not valid:
        return None
    bid = qb-qb0 if b==b0 else qb if b>b0 else -qb0
    ask = qa0-qa if a==a0 else qa0 if a>a0 else -qa
    same = (qb-qb0 if b==b0 else 0)+(qa0-qa if a==a0 else 0)
    return {"ofi": bid+ask, "same": same, "price": bid+ask-same,
            "imbalance": (qb-qa)/(qb+qa), "microprice": (a*qb+b*qa)/(qb+qa), "spread": a-b}


def clusters(trades, price_radius, time_radius):
    # (id,time,price,size,side); BFS is deliberately distinct from union/find.
    remaining = set(range(len(trades)))
    groups = []
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        component, pending = {first}, [first]
        while pending:
            a = trades[pending.pop()]
            joined = [i for i in remaining if trades[i][4] == a[4] and abs(trades[i][1]-a[1])<=time_radius
                      and abs(trades[i][2]-a[2])<=price_radius]
            for i in joined:
                remaining.remove(i)
                component.add(i)
                pending.append(i)
        rows = [trades[i] for i in component]
        size = sum(t[3] for t in rows)
        groups.append((tuple(sorted(t[0] for t in rows)), size, Fraction(sum(t[2]*t[3] for t in rows), size)))
    return tuple(sorted(groups))


def triangular(price, size, grid, radius=1):
    weights = {p: max(0, radius+1-abs(p-price)) for p in range(price-radius, price+radius+1)}
    mass = sum(weights.values())
    return tuple(Fraction(size*weights.get(p, 0), mass) for p in grid)


def markout(origin, side, prices):
    path = [Fraction(0)]+[side*(Fraction(p)-origin) for p in prices]
    return path[-1], max(path), min(path)


def ridge_one_dim(x, y, ridge):
    return Fraction(sum(a*b for a, b in zip(x, y)), sum(a*a for a in x)+ridge)


def nearest(query, episodes, query_start, episode, k):
    eligible = [(abs(Fraction(row[1])-query), row[0], row[3]) for row in episodes
                if row[2] < query_start and row[4] != episode]
    eligible.sort()
    chosen = eligible[:k]
    return tuple(row[1] for row in chosen), tuple(row[0] for row in chosen), sum(row[2] for row in chosen)/len(chosen) if chosen else None
