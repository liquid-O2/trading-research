"""Independent finite F08 algebra on primitive records; no market replay."""

from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable


def select_volume(universe, definitions, volumes, *, cut, previous_interval):
    """Dictionary records are deliberate oracle inputs, not implementation objects."""
    eligible = []
    examined = 0
    for identity in universe:
        rows = [d for d in definitions if d['id'] == identity and d['known_at'] <= cut]
        if len(rows) != 1: raise DependencyUnavailable('missing or ambiguous literal definition')
        definition = rows[0]
        if definition['expiry'] <= cut: continue
        candidates = []
        for volume in volumes:
            examined += 1
            if volume['id'] == identity and volume['known_at'] <= cut:
                candidates.append(volume)
        if not candidates: raise DependencyUnavailable('missing literal competitor volume')
        receipt = max(v['known_at'] for v in candidates)
        latest = [v for v in candidates if v['known_at'] == receipt]
        unique = {}
        for row in latest:
            if any(type(row.get(key)) is not str or not row[key] for key in ('receipt_id', 'source_version')):
                raise ContractError('literal volume needs explicit receipt/source identity')
            receipt_identity = (row['receipt_id'], row['source_version'])
            content = tuple(row[key] for key in ('id', 'known_at', 'contracts', 'complete', 'interval', 'receipt_id', 'source_version'))
            if receipt_identity in unique and unique[receipt_identity][0] != content:
                raise DependencyUnavailable('conflicting literal volume receipt')
            unique[receipt_identity] = (content, row)
        candidates = [row for _, row in unique.values()]
        if len(candidates) != 1 or not candidates[0]['complete']:
            raise DependencyUnavailable('incomplete or conflicting literal volume')
        row = candidates[0]
        if row['interval'] != previous_interval: raise ContractError('literal session mismatch')
        eligible.append((identity, row['contracts'], definition['expiry']))
    if not eligible: raise DependencyUnavailable('no literal eligible competitor')
    best = sorted(eligible, key=lambda row: (-row[1], row[2], row[0]))[0]
    return {'selected': best[0], 'volume_rows_examined': examined}


def bridge(previous_old, current_new, old_quote, new_quote):
    spread = new_quote-old_quote
    translated = previous_old+spread
    return {'spread': spread, 'translated': translated, 'point_change': current_new-translated,
            'operations': {'subtract': 2, 'add': 1}}


def profile(nodes, *, spread):
    values = []
    operations = 0
    for price, mass in nodes:
        values.append((price+spread, mass))
        operations += 1
    return {'nodes': tuple(values), 'mass': sum(mass for _, mass in values), 'additions': operations}


def split(price, quantity, factor):
    return {'price': price*factor, 'quantity': quantity/factor, 'notional': price*quantity}


def dividend(previous, ex_price, cash):
    return {'raw_point_change': ex_price-previous, 'total_return_cash_change': ex_price+cash-previous}


def fills(legs, multiplier, fees_per_side, *, currency):
    if type(currency) is not str or len(currency) != 3:
        raise ContractError('literal cash needs one declared currency')
    gross = Fraction(0)
    for entry, exit, side, contracts in legs:
        gross += side*(exit-entry)*multiplier*contracts
    fees = len(legs)*2*fees_per_side
    return {'gross': gross, 'fees': fees, 'net': gross-fees, 'currency': currency}
