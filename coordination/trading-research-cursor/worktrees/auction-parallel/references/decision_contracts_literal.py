"""Independent exact arithmetic for the finite B00.6 examples.

All inputs are primitive tuples/scalars. No production contract, forecast,
object-label, venue or accounting helper is imported.
"""
from fractions import Fraction


def path_statistics(initial, values, upper, lower):
    deltas = [0] + [value-initial for value in values]
    first = 'neither'
    for value in deltas[1:]:
        if value >= upper:
            first = 'upper'; break
        if value <= -lower:
            first = 'lower'; break
    return deltas[-1], max(deltas), -min(deltas), first


def fixed_contact(initial, points, *, cut, end, band, favorable, adverse, contact_at_cut=False, observed_end=None):
    if observed_end is not None and observed_end < end:
        return 'censored', None, 'censored', None
    contact = (cut, initial) if contact_at_cut else None
    outcome, hit = ('unresolved' if contact_at_cut else 'no_contact'), None
    for at, price in points:
        if not cut < at <= end:
            continue
        if contact is None and band[0] <= price <= band[1]:
            contact = at, price; outcome = 'unresolved'
        elif contact is not None:
            if price-contact[1] >= favorable:
                outcome, hit = 'favorable_first', at; break
            if price-contact[1] <= -adverse:
                outcome, hit = 'adverse_first', at; break
    return ('no_contact' if contact is None else 'contact'), contact, outcome, hit


def net_marks(marks):
    """marks: (at, gross, ((fee_id, amount), ...))."""
    values, totals = [], []
    previous = {}
    last_at = None
    for at, gross, charges in marks:
        if last_at is not None and at <= last_at:
            raise ValueError('unordered marks')
        cash = {}
        for identity, amount in charges:
            if identity in cash and cash[identity] != amount:
                raise ValueError('conflicting cash fee')
            cash[identity] = Fraction(amount)
        if any(cash.get(key) != amount for key, amount in previous.items()):
            raise ValueError('lost fee history')
        fee = sum(cash.values(), Fraction(0))
        values.append(Fraction(gross)-fee); totals.append(fee)
        previous, last_at = cash, at
    return tuple(values), tuple(b-a for a,b in zip(values,values[1:])), values[-1]-values[0], totals[-1], totals[-1]-totals[0]


def compose(segments):
    """segments: (initial full state tuple, terminal full state tuple, net, fee IDs)."""
    previous = None; fees = set(); result = Fraction(0)
    for initial, terminal, net, ids in segments:
        if previous is not None and previous != initial:
            raise ValueError('inexact continuation')
        if fees & set(ids):
            raise ValueError('overlapping fee charge')
        previous = terminal; fees.update(ids); result += Fraction(net)
    return result


def normal_posterior(mean, variance, admitted_observations):
    precision = Fraction(1)/Fraction(variance)
    weighted = Fraction(mean)*precision
    for value, noise in admitted_observations:
        precision += Fraction(1)/Fraction(noise)
        weighted += Fraction(value)/Fraction(noise)
    return weighted/precision, Fraction(1)/precision


def admission(seed_atoms, factors):
    """factors are immutable (id, atom tuple, payload) records; outcome only."""
    consumed = set(seed_atoms); seen = {}; outcomes = []
    for identity, atoms, payload in factors:
        current = atoms, payload
        if identity in seen:
            if seen[identity] != current:
                raise ValueError('factor identity conflict')
            outcomes.append('duplicate'); continue
        overlap = consumed.intersection(atoms)
        if overlap and overlap != set(atoms):
            raise ValueError('partial overlap')
        outcome = 'redundant_evidence' if overlap else 'accepted'
        seen[identity] = current; consumed.update(atoms); outcomes.append(outcome)
    return tuple(outcomes), tuple(sorted(consumed))


def standing_ask(quotes, arrival, *, ordering='venue_first', coverage=((0,20),)):
    segment = next(((a,b) for a,b in coverage if a <= arrival < b),None)
    if segment is None:
        return None
    if ordering == 'ambiguous' and any(at == arrival for _,at,_,_,_ in quotes):
        return None
    eligible = [q for q in quotes if q[1] < arrival or ordering != 'order_first' and q[1] == arrival]
    if not eligible:
        return None
    q = sorted(eligible,key=lambda q:q[1])[-1]
    return q[4] if q[1] >= segment[0] else None
