"""Exact TPO bracket visits and initial balance over source-bound trade atoms."""
from __future__ import annotations

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_anchors import AuctionAnchor, MINUTE_NS
from trading_research.research.auction_flow_anchor_trades import AtomicTrades, _integer, _intervals, missing_intervals


VERSION = 'auction-flow-exact-anchor-tpo-v1'
BRACKET_MINUTES = (15, 30, 60)
IB_MINUTES = (30, 60)


def required_atom_cuts(anchor, *, event_end_ns, bracket_minutes=BRACKET_MINUTES):
    if (type(anchor) is not AuctionAnchor or not _integer(event_end_ns)
            or not anchor.start_ns <= event_end_ns <= anchor.end_ns
            or type(bracket_minutes) is not tuple or not bracket_minutes
            or any(type(m) is not int or m not in BRACKET_MINUTES for m in bracket_minutes)):
        raise ContractError('exact selected anchor and supported TPO bracket cuts required')
    cuts = {event_end_ns}
    if any(sum((b - a + minutes * MINUTE_NS - 1) // (minutes * MINUTE_NS)
               for a, b in anchor.prefix_spans(event_end_ns)) > 40000 for minutes in bracket_minutes):
        raise ContractError('scientific atom-cut schedule exceeds its registered bracket bound')
    for start, end in anchor.prefix_spans(event_end_ns):
        cuts.update((start, end))
        for minutes in bracket_minutes:
            cuts.update(range(start, end, minutes * MINUTE_NS))
    for minutes in IB_MINUTES:
        end = anchor.start_ns + minutes * MINUTE_NS
        if end <= min(event_end_ns, anchor.spans[0][1]):
            cuts.add(end)
    return tuple(sorted(cuts))


class AnchorTPO:
    def __init__(self, anchor, *, bracket_minutes=30, row_ticks=1, origin_ticks=0,
                 representation='whole_trade_visits', maximum_brackets=40000,
                 maximum_price_rows=250000, maximum_incidences=2_000_000, maximum_atoms=1_000_000):
        if (type(anchor) is not AuctionAnchor or type(bracket_minutes) is not int or bracket_minutes not in BRACKET_MINUTES
                or not _integer(row_ticks, minimum=1) or row_ticks > 1024
                or type(origin_ticks) is not int or abs(origin_ticks) >= 2**53
                or representation not in ('whole_trade_visits', 'ohlc_range_proxy')
                or not _integer(maximum_brackets, minimum=1) or maximum_brackets > 40000
                or not _integer(maximum_price_rows, minimum=1) or maximum_price_rows > 1_000_000
                or not _integer(maximum_incidences, minimum=1) or maximum_incidences > 2_000_000
                or not _integer(maximum_atoms, minimum=1) or maximum_atoms > 1_000_000):
            raise ContractError('registered exact TPO definition and finite work bounds required')
        self.anchor, self.width = anchor, bracket_minutes * MINUTE_NS
        self.bracket_minutes, self.row_ticks, self.origin_ticks = bracket_minutes, row_ticks, origin_ticks
        self.representation = representation
        self.maximum_price_rows, self.maximum_incidences = maximum_price_rows, maximum_incidences
        self.maximum_atoms = maximum_atoms
        self.spans = []
        offset = 0
        for a, b in anchor.spans:
            count = (b - a + self.width - 1) // self.width
            if offset + count > maximum_brackets:
                raise ContractError('TPO anchor exceeds its registered bracket count')
            self.spans.append((a, b, offset, count))
            offset += count
        self.incidence, self.bracket_ranges = {}, {}
        self.incidences = 0
        self.supplied, self.incomplete = [], []
        self.members = []
        self.ib = {m: {'high': None, 'low': None} for m in IB_MINUTES}
        self.known_at = 0
        self.delay = self.last_order = None
        self._failed = False

    def add(self, atom):
        if self._failed:
            raise IntegrityError('a failed TPO calculation cannot resume or publish')
        try:
            if (type(atom) is not AtomicTrades or len(self.members) >= self.maximum_atoms or any(getattr(atom, k) != getattr(self.anchor, k)
                    for k in ('root', 'contract_key', 'instrument_id', 'source_lineage'))
                    or self.supplied and atom.start_ns < self.supplied[-1][1]
                    or self.delay is not None and atom.known_at_ns - atom.end_ns != self.delay
                    or atom.first is not None and self.last_order is not None and atom.first[1] <= self.last_order):
                raise IntegrityError('TPO atom identity, source order, interval or delay changed')
            span = next((s for s in self.spans if s[0] <= atom.start_ns < atom.end_ns <= s[1]), None)
            if span is None:
                raise IntegrityError('TPO atom crosses or lies outside selected anchor membership')
            number = (atom.start_ns - span[0]) // self.width
            end = min(span[1], span[0] + (number + 1) * self.width)
            cursor = self.anchor.start_source_order if atom.start_ns == self.anchor.start_ns else None
            if atom.end_ns > end or atom.start_source_order != cursor:
                raise IntegrityError('TPO atom crosses a bracket or misses the exact causal source-order cut')
            for minutes in IB_MINUTES:
                ib_end = self.anchor.start_ns + minutes * MINUTE_NS
                if ib_end <= self.anchor.spans[0][1] and atom.start_ns < ib_end < atom.end_ns:
                    raise IntegrityError('initial-balance boundary needs an exact split of original events')
            bid = span[2] + number
            rows = {(r[0] - self.origin_ticks) // self.row_ticks for r in atom.rows}
            if rows:
                prior = self.bracket_ranges.get(bid)
                self.bracket_ranges[bid] = (min(rows) if prior is None else min(min(rows), prior[0]),
                                           max(rows) if prior is None else max(max(rows), prior[1]))
                if self.representation == 'whole_trade_visits':
                    bit = 1 << bid
                    for row in rows:
                        previous = self.incidence.get(row, 0)
                        if not previous & bit:
                            if self.incidences >= self.maximum_incidences:
                                raise ContractError('TPO incidence capacity exhausted')
                            if not previous and len(self.incidence) >= self.maximum_price_rows:
                                raise ContractError('TPO exact price-row capacity exhausted')
                            self.incidence[row] = previous | bit
                            self.incidences += 1
            self.supplied.append((atom.start_ns, atom.end_ns))
            if not atom.source_complete or not atom.coordinate_complete or atom.unpriced_prints:
                self.incomplete.append((atom.start_ns, atom.end_ns))
            self.members.append(atom.evidence_id)
            self.known_at = max(self.known_at, atom.known_at_ns)
            self.delay = atom.known_at_ns - atom.end_ns
            if atom.last is not None:
                self.last_order = atom.last[1]
            for minutes in IB_MINUTES:
                if atom.end_ns <= min(self.anchor.start_ns + minutes * MINUTE_NS, self.anchor.spans[0][1]):
                    for field, better in (('high', lambda a, b: a > b), ('low', lambda a, b: a < b)):
                        point = getattr(atom, field)
                        old = self.ib[minutes][field]
                        if point is not None and (old is None or better(point[0], old[0])):
                            self.ib[minutes][field] = point
        except BaseException:
            self._failed = True
            raise

    def record(self, *, event_end_ns, decision_cut_ns, latency_ns):
        if self._failed:
            raise IntegrityError('a failed TPO calculation cannot publish partial state')
        known_at = max(self.known_at, self.anchor.publication_at(event_end_ns, latency_ns=latency_ns))
        if (not _integer(decision_cut_ns) or decision_cut_ns < known_at
                or self.supplied and event_end_ns < self.supplied[-1][1]
                or self.delay is not None and latency_ns != self.delay):
            raise ContractError('TPO constituent, selection or observation cut is unavailable')
        supplied = _intervals(self.supplied)
        incomplete = _intervals(self.incomplete)
        def covered(start, end):
            return (start < end and not missing_intervals(((start, end),), supplied)
                    and not any(a < end and start < b for a, b in incomplete))
        brackets = []
        for start, end, offset, _ in self.spans:
            for number, a in enumerate(range(start, min(event_end_ns, end), self.width)):
                b = min(a + self.width, end)
                observed_end = min(b, event_end_ns)
                status = ('complete' if b <= event_end_ns else 'provisional') if covered(a, observed_end) else 'incomplete_observation'
                brackets.append((offset + number, a, b, status))
        incidence = self.incidence
        if self.representation == 'ohlc_range_proxy':
            incidence, count = {}, 0
            for bid, (low, high) in self.bracket_ranges.items():
                if high - low + 1 > self.maximum_price_rows:
                    raise ContractError('TPO OHLC proxy row span exceeds its finite bound')
                for row in range(low, high + 1):
                    count += 1
                    if count > self.maximum_incidences or row not in incidence and len(incidence) >= self.maximum_price_rows:
                        raise ContractError('TPO OHLC proxy incidence/row capacity exhausted')
                    incidence[row] = incidence.get(row, 0) | (1 << bid)
        complete_count = sum(b[-1] == 'complete' for b in brackets)
        intended = self.anchor.prefix_spans(event_end_ns)
        complete = bool(intended) and not missing_intervals(intended, supplied) and not incomplete
        final = event_end_ns == self.anchor.end_ns
        single = tuple(row for row, bits in sorted(incidence.items()) if bits.bit_count() == 1)
        tails = []
        for at, step in ((min(incidence, default=0), 1), (max(incidence, default=0), -1)):
            tail = []
            while at in incidence and incidence[at].bit_count() == 1:
                tail.append(at)
                at += step
            tails.append(tuple(sorted(tail)))
        ib = {}
        for minutes, values in self.ib.items():
            end = self.anchor.start_ns + minutes * MINUTE_NS
            supported = end <= self.anchor.spans[0][1]
            complete_ib = supported and end <= event_end_ns and covered(self.anchor.start_ns, end)
            ib[str(minutes)] = {**values, 'origin_ns': self.anchor.start_ns, 'end_ns': end,
                'supported_first_span': supported, 'complete': complete_ib,
                'provisional': supported and event_end_ns < end,
                'complete_high_low_ticks': (values['high'][0], values['low'][0])
                    if complete_ib and values['high'] is not None and values['low'] is not None else None,
                'empty_observed_initial_balance': complete_ib and values['high'] is None}
        return {'version': VERSION, 'anchor_id': self.anchor.id, 'representation': self.representation,
            'bracket_minutes': self.bracket_minutes, 'row_ticks': self.row_ticks, 'origin_ticks': self.origin_ticks,
            'observation_end_ns': event_end_ns, 'known_at_ns': known_at,
            'rows': tuple((row, bits.bit_count(), bits) for row, bits in sorted(incidence.items())),
            'membership_encoding': 'bit j is exact bracket ordinal j in the retained bracket schedule',
            'bracket_schedule': tuple(brackets), 'bracket_clock': 'restart at each disjoint declared formation span',
            'complete_brackets': complete_count, 'observed_nonempty_brackets': len(self.bracket_ranges),
            'formation_final': final, 'price_history_complete': complete,
            'provisional_single_print_rows': single,
            'final_single_print_rows': single if final and complete and complete_count >= 2 else None,
            'minimum_completed_brackets_for_geometric_final_single_prints': 2,
            'legacy_source_five_bracket_display_ready': complete_count >= 5,
            'legacy_source_five_bracket_final_single_print_rows': single if final and complete and complete_count >= 5 else None,
            'low_tail_rows': tails[0], 'high_tail_rows': tails[1],
            'low_tail_same_bracket': len({incidence[r] for r in tails[0]}) == 1 if tails[0] else None,
            'high_tail_same_bracket': len({incidence[r] for r in tails[1]}) == 1 if tails[1] else None,
            'initial_balance': ib, 'members': tuple(self.members),
            'visit_chronology': 'replay exact retained addressed events; price-row incidence does not encode within-bracket visit order'}
