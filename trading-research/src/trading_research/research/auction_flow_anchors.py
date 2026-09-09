"""Named scientific formations, separate from extraction and prediction clocks.

The anchor records define membership and availability. The registered caller
binds their source lineage and actual raw coordinate to admitted observations;
constructing an anchor does not certify that the requested tape was acquired.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, time, timedelta

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import zone_version
from trading_research.operations.artifacts import digest


VERSION = 'auction-flow-scientific-anchor-membership-v1'
CONTRACT_SHA256 = '890c5949abc03312ccfc4a2e69eccc8efb2a5d9f9f3f8ad54740d03bee9cb89c'
DETAIL_SHA256 = '7b8596612b075683d94c6a00101271252325421fcaa95ea0cb18bab6aee861e0'
MINUTE_NS = 60_000_000_000
ROLLING_MINUTES = (5, 15, 60, 240)
KINDS = ('rth', 'prior_rth', 'overnight', 'jumbo_named_range', 'day', 'week',
         'month', 'quarter', 'year', 'rolling', 'event', 'swing', 'composite')


def union_spans(spans):
    if (type(spans) is not tuple or not 1 <= len(spans) <= 64
            or any(type(pair) is not tuple or len(pair) != 2
                or any(type(x) is not int for x in pair) or not 0 <= pair[0] < pair[1] < 2**63 - 1_000_000_000
                for pair in spans)):
        raise ContractError('bounded exact nonempty half-open formation intervals required')
    result = []
    for start, end in sorted(spans):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], end))
        else:
            result.append((start, end))
    return tuple(result)


@dataclass(frozen=True)
class AuctionAnchor:
    variant: str
    kind: str
    root: str
    instrument_id: int
    contract_key: str
    source_lineage: str
    spans: tuple
    selection_known_at_ns: int
    source_versions: tuple
    members: tuple = ()
    revision_of: str | None = None
    selection_evidence: str | None = None
    start_source_order: int | None = None

    def __post_init__(self):
        if (type(self.variant) is not str or not self.variant or self.kind not in KINDS
                or self.root not in ('NQ', 'ES') or type(self.instrument_id) is not int or self.instrument_id <= 0
                or type(self.contract_key) is not str or not self.contract_key.startswith(self.root + ':')
                or type(self.source_lineage) is not str or not self.source_lineage
                or type(self.selection_known_at_ns) is not int or not 0 <= self.selection_known_at_ns < 2**63
                or type(self.source_versions) is not tuple or not self.source_versions
                or any(type(s) is not str or not s for s in self.source_versions)
                or type(self.members) is not tuple or len(self.members) > 64
                or any(type(s) is not str or not s for s in self.members)
                or any(v is not None and (type(v) is not str or not v) for v in (self.revision_of, self.selection_evidence))
                or self.start_source_order is not None and (type(self.start_source_order) is not int or self.start_source_order < 0)):
            raise ContractError('anchor requires explicit identity, exact selection clock and preserved source evidence')
        if union_spans(self.spans) != self.spans:
            raise ContractError('anchor membership must be an explicit sorted disjoint union')
        if self.kind in ('swing', 'event', 'composite') and self.selection_evidence is None:
            raise ContractError('selected anchor needs its actual later selection evidence')
        if self.start_source_order is not None and len(self.spans) != 1:
            raise ContractError('an event cursor requires one explicit ordered formation interval')

    @property
    def id(self):
        return digest({'version': VERSION, 'contract_sha256': CONTRACT_SHA256, 'detail_sha256': DETAIL_SHA256, **asdict(self)})

    @property
    def start_ns(self):
        return self.spans[0][0]

    @property
    def end_ns(self):
        return self.spans[-1][1]

    def prefix_spans(self, event_end_ns):
        if type(event_end_ns) is not int or not 0 <= event_end_ns < 2**63:
            raise ContractError('exact observation endpoint required')
        return tuple((a, min(b, event_end_ns)) for a, b in self.spans if a < event_end_ns)

    def publication_at(self, event_end_ns, *, latency_ns):
        if (type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000
                or type(event_end_ns) is not int or not self.start_ns <= event_end_ns <= self.end_ns):
            raise ContractError('anchor publication needs an explicit supported source-delay scenario')
        return max(self.selection_known_at_ns, event_end_ns + latency_ns)

    def record(self):
        return {'version': VERSION, 'anchor_id': self.id, **asdict(self),
            'contract_sha256': CONTRACT_SHA256, 'detail_sha256': DETAIL_SHA256,
            'formation_exposure_ns': sum(b - a for a, b in self.spans),
            'membership_rule': 'time-interval union within the same explicit source lineage and physical coordinate',
            'prediction_horizon': None, 'source_coverage_certified_by_anchor': False}


def _month_after(day):
    return date(day.year + int(day.month == 12), day.month % 12 + 1, 1)


def named_clock_anchors(*, day, cut_ns, calendar, root, instrument_id, contract_key, source_lineage):
    """Return all applicable registered clock anchors and exact local failures.

    Cash dates use the retained publication-aware calendar. Other session
    clocks are explicitly observed wall windows, without a venue-status claim.
    A closed cash date does not manufacture a cash session or a zero outcome.
    """
    if type(day) is not date or type(cut_ns) is not int or cut_ns < 0:
        raise ContractError('explicit civil date and actual decision cut required')
    anchors, unavailable = [], []
    scope = dict(root=root, instrument_id=instrument_id, contract_key=contract_key, source_lineage=source_lineage)

    def add(variant, kind, spans, known, versions):
        anchors.append(AuctionAnchor(variant=variant, kind=kind, spans=union_spans(spans),
            selection_known_at_ns=known, source_versions=versions, **scope))

    try:
        cash = calendar.resolve(day, cut=cut_ns)
        if cash.state == 'closed':
            unavailable.append({'variant': 'cash_rth', 'reason': 'published_closed_cash_date', 'calendar_version': cash.version})
        else:
            add('cash_rth', 'rth', ((cash.open_at, cash.close_at),), cash.known_at, (cash.version,))
    except DependencyUnavailable as exc:
        unavailable.append({'variant': 'cash_rth', 'reason': str(exc)})
    try:
        for distance in range(1, 371):
            previous = calendar.resolve(day - timedelta(days=distance), cut=cut_ns)
            if previous.state != 'closed':
                add('prior_cash_rth', 'prior_rth', ((previous.open_at, previous.close_at),),
                    previous.known_at, (previous.version,))
                break
        else:
            raise DependencyUnavailable('no prior nonclosed cash date inside the declared 370-day calendar bound')
    except DependencyUnavailable as exc:
        unavailable.append({'variant': 'prior_cash_rth', 'reason': str(exc)})

    clocks = (
        ('observed_futures_18_17', 'day', 'America/New_York', -1, '18:00', 0, '17:00', None),
        ('overnight_18_0930', 'overnight', 'America/New_York', -1, '18:00', 0, '09:30', None),
        ('morning_06_09_ny', 'jumbo_named_range', 'America/New_York', 0, '06:00', 0, '09:00', None),
        ('source_06_09_fixed_utc_minus4', 'jumbo_named_range', 'Etc/GMT+4', 0, '06:00', 0, '09:00', None),
        ('source_monday_22_21_utc', 'jumbo_named_range', 'UTC', 0, '22:00', 1, '21:00', 0),
        ('source_tuesday_22_21_utc', 'jumbo_named_range', 'UTC', 0, '22:00', 1, '21:00', 1),
    )
    for variant, kind, zone, first_day, opened, last_day, closed, weekday in clocks:
        if weekday is not None and day.weekday() != weekday:
            continue
        start = local_timestamp(day + timedelta(days=first_day), time.fromisoformat(opened), zone)
        end = local_timestamp(day + timedelta(days=last_day), time.fromisoformat(closed), zone)
        rule = digest({'version': VERSION, 'variant': variant, 'zone': zone, 'zone_version': zone_version(zone),
                       'start_day_offset': first_day, 'end_day_offset': last_day, 'open': opened, 'close': closed})
        add(variant, kind, ((start, end),), 0, (rule,))
    periods = {
        'week': (day - timedelta(days=day.weekday()), day - timedelta(days=day.weekday()) + timedelta(days=7)),
        'month': (day.replace(day=1), _month_after(day)),
        'quarter': (date(day.year, 1 + 3 * ((day.month - 1) // 3), 1),
                    date(day.year + int(day.month >= 10), 1 if day.month >= 10 else 1 + 3 * ((day.month - 1) // 3 + 1), 1)),
        'year': (date(day.year, 1, 1), date(day.year + 1, 1, 1)),
    }
    for kind, (first, last) in periods.items():
        spans = ((local_timestamp(first, time(0), 'America/New_York'), local_timestamp(last, time(0), 'America/New_York')),)
        add('civil_ny_' + kind, kind, spans, 0, (digest({'version': VERSION, 'period': kind,
            'zone_version': zone_version('America/New_York'), 'start_wall': '00:00', 'week_start': 'Monday'}),))
    return {'anchors': tuple(anchors), 'unavailable': tuple(unavailable),
            'clock_scope': 'scientific formations, separate from source-file partitions and forward horizons',
            'or15_default_anchor': False}


def rolling_anchor(*, minutes, event_end_ns, selection_known_at_ns, source_versions, **scope):
    if minutes not in ROLLING_MINUTES or type(minutes) is not int:
        raise ContractError('registered rolling formation length required')
    return AuctionAnchor(variant=f'rolling_{minutes}m', kind='rolling',
        spans=((event_end_ns - minutes * MINUTE_NS, event_end_ns),),
        selection_known_at_ns=selection_known_at_ns, source_versions=source_versions, **scope)


def composite_anchor(members, *, variant, selection_known_at_ns, selection_evidence, revision_of=None):
    if type(members) is not tuple or not 1 <= len(members) <= 64 or any(type(a) is not AuctionAnchor for a in members):
        raise ContractError('bounded explicit constituent anchors required')
    first = members[0]
    fields = ('root', 'instrument_id', 'contract_key', 'source_lineage')
    if any(any(getattr(a, f) != getattr(first, f) for f in fields) for a in members):
        raise ContractError('composite cannot merge acquisition variants or physical roll coordinates')
    if type(selection_known_at_ns) is not int or selection_known_at_ns < max(a.selection_known_at_ns for a in members):
        raise ContractError('composite membership cannot be available before its constituents are selected')
    if any(a.start_source_order is not None for a in members):
        raise ContractError('event-cursor composites require a separately explicit ordered member-union rule')
    return AuctionAnchor(variant=variant, kind='composite', spans=union_spans(tuple(p for a in members for p in a.spans)),
        selection_known_at_ns=selection_known_at_ns, selection_evidence=selection_evidence,
        source_versions=tuple(sorted({v for a in members for v in a.source_versions})), members=tuple(a.id for a in members),
        revision_of=revision_of, **{f: getattr(first, f) for f in fields})
