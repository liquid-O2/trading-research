"""Independent raw-tuple arithmetic for registered M12/L02/L03 cases.

This module imports no production types or helpers and performs no fitting.
"""
from fractions import Fraction


def sealed_fields(rows, start, end, coverage, *, order_known=True):
    """rows: (id, event_at, price, sequence); coverage: half-open pairs."""
    rows = tuple(r for r in rows if start <= r[1] < end)
    if not rows:
        return (None, None, None, None), (), None, None
    first_time = min(r[1] for r in rows)
    last_time = max(r[1] for r in rows)
    first = tuple(r for r in rows if r[1] == first_time)
    last = tuple(r for r in rows if r[1] == last_time)
    def covered(a, b):
        cursor = a
        for lo, hi in sorted(coverage):
            if lo <= cursor < hi:
                cursor = max(cursor, hi)
            if cursor >= b:
                return True
        return False
    def endpoint(group, choose_first):
        values = {r[2] for r in group}
        sequences = [r[3] for r in group]
        if len(values) == 1:
            return group[0][2]
        if (not order_known or None in sequences or len(set(sequences)) != len(sequences)):
            return None
        ordered = sorted(group, key=lambda r: r[3])
        return ordered[0 if choose_first else -1][2]
    complete = covered(start, end)
    o = endpoint(first, True) if covered(start, first_time + 1) else None
    c = endpoint(last, False) if covered(last_time, end) else None
    return (o, max(r[2] for r in rows) if complete else None,
            min(r[2] for r in rows) if complete else None, c), tuple(r[0] for r in rows), first_time, last_time


def prior_row(rows, current_day):
    """rows ordered consecutive civil-day facts: (day, eligible, id, OHLC)."""
    before = [row for row in rows if row[0] < current_day]
    if not before:
        return None
    for row in reversed(sorted(before)):
        if row[1]:
            return row[2], row[3]
    return None


def ladder(low, high, ratios):
    low, high = Fraction(low), Fraction(high)
    if high < low:
        raise ValueError('inverted range')
    if high == low:
        return ()
    width = high - low
    out = []
    for side in ('upper', 'lower'):
        for ratio in ratios:
            ratio = Fraction(ratio)
            price = high + ratio * width if side == 'upper' else low - ratio * width
            out.append((side, ratio, price))
    return tuple(out)


def regions(low, high, ratios):
    rows = ladder(low, high, ratios)
    return tuple(tuple(sorted(row[2] for row in rows if row[0] == side))
                 for side in ('upper', 'lower'))


def body_and_range(open_, high, low, close):
    return Fraction(3 * close + open_, 4), Fraction(low) + Fraction(high - low, 4)


def gaps(current, close, settlement, high):
    return tuple(Fraction(current) - Fraction(value) for value in (close, settlement, high))


def official_at(messages, cut):
    rows = [row for row in messages if row[1] <= cut]
    return None if not rows else rows[-1][2]


def contacts(prices, lower, upper):
    contacts_, gaps_ = [], []
    previous = None
    for event_id, price in prices:
        if lower <= price <= upper:
            contacts_.append(event_id)
        if previous is not None and ((previous < lower and price > upper)
                                     or (previous > upper and price < lower)):
            gaps_.append(event_id)
        previous = price
    return tuple(contacts_), tuple(gaps_)


def freshness(rows, price, cut, *, rth_only=False, side=1):
    touches, breaches, returns = [], [], []
    crossed = False
    for event_id, at, known_at, value, session in sorted(rows, key=lambda row: row[1]):
        if known_at > cut or rth_only and session != 'RTH':
            continue
        displacement = side * (value - price)
        if displacement == 0:
            touches.append(event_id)
        elif displacement > 0:
            breaches.append(event_id); crossed = True
        elif crossed:
            returns.append(event_id)
    return tuple(touches), tuple(breaches), tuple(returns)


def e0_sources(current, prior):
    _, high, low, _ = current
    width = high - low
    inner = (('low', None, Fraction(low)), ('high', None, Fraction(high)),
             ('EQ', Fraction(1, 2), Fraction(low) + Fraction(width, 2)),
             ('quarter', Fraction(1, 4), Fraction(low) + Fraction(width, 4)),
             ('quarter', Fraction(3, 4), Fraction(low) + Fraction(3 * width, 4)))
    out = [('current_06_09', role, ratio, value) for role, ratio, value in inner]
    for side, ratio, value in ladder(low, high, (Fraction(1, 2), Fraction(1))):
        out.append(('current_06_09', side + '_edge_extension', ratio, value))
    for field, value in zip(('open', 'high', 'low', 'close'), prior):
        out.append(('prior_RTH', field, None, Fraction(value)))
    return tuple(out)


def points(values, tick):
    return tuple(Fraction(value) * Fraction(tick) for value in values)
