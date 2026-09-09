"""Independent literal profile, TPO, side and moment equations."""

from fractions import Fraction


def mass_profile(trades, origin, width, low, high):
    rows = {i: [Fraction(0)]*3 for i in range(low, high+1)}
    overflow = [Fraction(0)]*3
    for price, size, side in trades:
        channel = 0 if side==1 else 1 if side==-1 else 2
        if price is None:
            overflow[2] += size
            continue
        index = (price-origin)//width
        if index<low:
            overflow[0] += size
        elif index>high:
            overflow[1] += size
        else:
            rows[index][channel] += size
    return tuple((i, *v) for i, v in rows.items()), tuple(overflow)


def value_area(mass, fraction, *, poc_tie="lower", value_tie="upper", stop_empty=False):
    if not sum(mass):
        return (), None, (), Fraction(0)
    modes = tuple(i for i, value in enumerate(mass) if value==max(mass))
    center = modes[0] if poc_tie=="lower" else modes[-1]
    selected = {center}
    achieved = mass[center]
    while achieved < fraction*sum(mass):
        left, right = min(selected)-1, max(selected)+1
        candidates = {i: mass[i] for i in (left, right) if 0<=i<len(mass)}
        if not candidates or stop_empty and not sum(candidates.values()):
            break
        maximum = max(candidates.values())
        equal = [i for i, value in candidates.items() if value==maximum]
        take = equal if value_tie=="both" else [min(equal) if value_tie=="lower" else max(equal)]
        selected.update(take)
        achieved += sum(mass[i] for i in take)
    return modes, center, tuple(sorted(selected)), achieved


def smooth(mass, radius=1):
    weights = tuple(Fraction(radius+1-abs(i), (radius+1)**2) for i in range(-radius, radius+1))
    return tuple(sum(mass[j]*weights[i-j+radius] for j in range(len(mass)) if abs(i-j)<=radius) for i in range(len(mass)))


def transport(a, b, width=1):
    if not sum(a) or not sum(b):
        return None
    return sum(abs(sum(Fraction(v, sum(a)) for v in a[:i])-sum(Fraction(v, sum(b)) for v in b[:i]))*width
               for i in range(1, len(a)+1))


def moments(trades):
    mass = sum(q for p, q in trades)
    if not mass:
        return 0, 0, 0, None, None
    pv = sum(p*q for p, q in trades)
    p2v = sum(p*p*q for p, q in trades)
    mean = Fraction(pv, mass)
    # Direct centered recomputation is independent of the production moment identity.
    variance = sum(q*(p-mean)**2 for p, q in trades)/mass
    return mass, pv, p2v, mean, variance


def weighted_rank(trades, probability):
    if not trades:
        return None
    values = sorted(trades)
    remaining = probability*sum(q for _, q in values)
    for p, q in values:
        remaining -= q
        if remaining <= 0:
            return p
    return values[-1][0]


def body_wicks(ohlc, volume, boundaries):
    o, h, l, c = map(Fraction, ohlc)
    denom = abs(o-c)+2*(h-max(o, c))+2*(min(o, c)-l)
    output = []
    for a, b in boundaries:
        parts = [(min(o,c), max(o,c), 0 if c>=o else 1, Fraction(1)),
                 (l, min(o,c), 0, Fraction(1)), (l, min(o,c), 1, Fraction(1)),
                 (max(o,c), h, 0, Fraction(1)), (max(o,c), h, 1, Fraction(1))]
        sides = [Fraction(0), Fraction(0)]
        for start, end, side, weight in parts:
            if denom:
                sides[side] += max(Fraction(0), min(b,end)-max(a,start))*volume*weight/denom
        output.append(tuple(sides))
    return tuple(output)


def tpo(events, brackets):
    rows = sorted({p for t, p in events})
    return tuple((p, tuple(i for i, (a,b) in enumerate(brackets) if any(a<=t<b and price==p for t,price in events))) for p in rows)


def dwell(events, end, stale_cap):
    output = {}
    for index, (at, price) in enumerate(events):
        stop = min(end, at+stale_cap, events[index+1][0] if index+1<len(events) else end)
        output[price] = output.get(price, 0)+max(0, stop-at)
    return tuple(sorted(output.items())), end-sum(output.values())


def side_rows(buy, sell, unknown, lam):
    return tuple({"delta": b-s, "bounds": (b-s-u,b-s+u), "ratio": Fraction(b,s) if s else None,
                  "contrast": Fraction(b-s,b+s+u+2*lam) if b+s+u+2*lam else None}
                 for b,s,u in zip(buy,sell,unknown))


def haar(values):
    values = tuple(Fraction(v) for v in values)
    return tuple((values[i]+values[i+1])/2 for i in range(0,len(values),2)), tuple((values[i]-values[i+1])/2 for i in range(0,len(values),2))


def source_quantiles(values, probabilities):
    values = sorted(map(Fraction, values))
    if len(values)<2:
        return None
    out = []
    for p in probabilities:
        rank = p*(len(values)-1)
        i = rank.numerator//rank.denominator
        out.append(values[i] if i==len(values)-1 else values[i]*(i+1-rank)+values[i+1]*(rank-i))
    return tuple(out)
