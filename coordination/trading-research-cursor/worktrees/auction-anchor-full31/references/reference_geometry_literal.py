"""Independent exact opening/pivot/gap reference relations."""

from fractions import Fraction
from itertools import permutations, product, groupby


def opening(trades, start, cut, coverage):
    # Primitive (event,known,price,size,side,order) rows.
    rows = sorted((r for r in trades if r[0]<=cut and r[1]<=cut), key=lambda r: (r[0], -1 if r[5] is None else r[5]))
    if not rows:
        return None, None, ()
    first = [r for r in rows if r[0]==rows[0][0]]
    values = tuple(sorted({Fraction(r[2]) for r in first}))
    ordered = len(first)==1 or all(r[5] is not None for r in first) and len({r[5] for r in first})==len(first)
    observed = Fraction(first[0][2]) if ordered else values[0] if len(values)==1 else None
    certified = any(a==start and b>first[0][0] for a,b in coverage)
    return observed if certified else None, observed, values


def pivots(high, low, close):
    pivot = Fraction(high+low+close, 3)
    width = high-low
    upper = [2*pivot-low, pivot+width, high+2*(pivot-low)]
    lower = [2*pivot-high, pivot-width, low-2*(high-pivot)]
    upper += [upper[2]+width, upper[2]+2*width]
    lower += [lower[2]-width, lower[2]-2*width]
    return {"P": pivot, **{"R"+str(i+1):p for i,p in enumerate(upper)}, **{"S"+str(i+1):p for i,p in enumerate(lower)}}


def gap_paths(initial, reference, rows, *, ordered=True, contact_at_cut=False):
    groups = [tuple(g) for _,g in groupby(sorted(rows, key=lambda p:(p[0],p[1])), key=lambda p:p[0])]
    choices = [[g] if ordered else list(permutations(g)) for g in groups]
    paths = list(product(*choices)) if choices else [()]
    sign = 1 if initial>reference else -1 if initial<reference else 0
    outcomes = []
    for batches in paths:
        path = [p for batch in batches for p in batch]
        touched_indexes = [i for i,p in enumerate(path) if p[2]==reference]
        first = touched_indexes[0] if touched_indexes else None
        touched = contact_at_cut or first is not None
        after = path if contact_at_cut else path[first:] if first is not None else []
        held = all(sign*(p[2]-reference)<=0 for p in after) if sign and touched else None
        previous, crosses = initial, []
        for p in path:
            if min(previous,p[2])<reference<max(previous,p[2]):
                crosses.append(p[0])
            previous = p[2]
        outcomes.append({"terminal": previous, "touched": touched,
            "contact_at": 0 if contact_at_cut else None if first is None else path[first][0],
            "closed_through": sign*(previous-reference)<0 if sign else None, "held_after_contact": held,
            "gap_held": all(sign*(p[2]-reference)>0 for p in path) if sign else None,
            "gap_traversed": any(sign*(p[2]-reference)<=0 for p in path) if sign else None,
            "crossings": tuple(crosses)})
    return tuple(outcomes)
