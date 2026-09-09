"""Thin F03/F09/F10 range adapters, with no shadow bar or object registry."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import Calendar, FormationWindow
from trading_research.foundations.intervals import IntervalGraph
from trading_research.foundations.multiresolution import SharedBarEngine
from trading_research.foundations.object_graph import (
    AnchorVersion, AtomicBatch, Eligibility, EvidenceVersion, Instrument,
    ObjectGraph, ObjectRevision, PublicationClock, RelationKind, RelationVersion, Support,
)
from trading_research.foundations.range_primitives import (
    ClockSelection, FIELDS, FieldSupport, RangePrimitive, _integer, _name,
)
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


_CLOCK_TOKEN = object()
_PRIMITIVE_TOKEN = object()
_LINK_TOKEN = object()
_MEMBER_TOKEN = object()

# A role declares the formula's input fields, not an opinion about its efficacy.
# Generator names are frozen in the registered C01/L01 and M12/L02/L03 protocols.
FORMULA_REQUIREMENTS = MappingProxyType({
    "C01-range-geometry-v1": MappingProxyType({
        "range_geometry": ("high", "low"),
    }),
    "L01-internal-ranges-v1": MappingProxyType({
        "range_high": ("high",), "range_low": ("low",),
        "range_open": ("open",), "range_close": ("close",),
        "range_eq": ("high", "low"), "range_quarter25": ("high", "low"),
        "range_quarter75": ("high", "low"),
        "upper_edge_extension": ("high", "low"),
        "lower_edge_extension": ("high", "low"),
    }),
    "L02-edge-extensions-v1": MappingProxyType({
        "upper_edge_extension": ("high", "low"),
        "lower_edge_extension": ("high", "low"),
        "upper_edge_region": ("high", "low"),
        "lower_edge_region": ("high", "low"),
    }),
    "L03-prior-session-v1": MappingProxyType({
        "prior_open": ("open",), "prior_high": ("high",),
        "prior_low": ("low",), "prior_close": ("close",),
    }),
})


def select_clock(*, calendar: Calendar, interval_graph: IntervalGraph, interval_name: str,
                 trading_date: date, instrument_root: str, instrument: Instrument,
                 cut: int) -> ClockSelection:
    if (type(calendar) is not Calendar or type(interval_graph) is not IntervalGraph
            or type(instrument) is not Instrument or type(trading_date) is not date):
        raise ContractError("actual calendar, interval graph, date and raw instrument required")
    timestamp(cut)
    _name(interval_name)
    _name(instrument_root)
    session = calendar.resolve(trading_date, instrument_root, cut=cut)
    if interval_graph.known_at > cut:
        raise DependencyUnavailable("interval graph was unavailable at selected cut")
    node = interval_graph.intervals.get(interval_name)
    if node is None or node.known_at > cut:
        raise DependencyUnavailable("named source formation is unavailable")
    if len(node.spans) != 1 or node.trading_dates != (trading_date,):
        raise ContractError("source formation needs one exact span and trading date")
    span = node.spans[0]
    window = FormationWindow(node.name, trading_date, span.start, span.end,
                             node.clock_variant, node.version)
    value = ClockSelection(instrument, window, session, cut, None, interval_graph, node)
    object.__setattr__(value, "_calendar_receipt", (_CLOCK_TOKEN, calendar, instrument_root, value.version_id))
    return value


def _require_clock(selection):
    if type(selection) is not ClockSelection:
        raise ContractError("resolved clock selection required")
    receipt = selection._calendar_receipt
    if (type(receipt) is not tuple or len(receipt) != 4 or receipt[0] is not _CLOCK_TOKEN
            or type(receipt[1]) is not Calendar or receipt[3] != selection.version_id):
        raise ContractError("clock lacks its actual calendar selection receipt")
    selection.__post_init__()
    if receipt[1].resolve(selection.window.trading_date, receipt[2], cut=selection.selected_at) != selection.session:
        raise IntegrityError("selected calendar prefix changed")


def _project(selection, bar, request, predecessor):
    _require_clock(selection)
    if (bar.definition.kind != "time" or bar.state not in ("provisional", "final")
            or bar.definition.domain.instrument != selection.instrument.raw_symbol
            or bar.definition.calendar_id != selection.interval_graph.version
            or bar.definition.reset_id != selection.clock_id
            or bar.reset_epoch != selection.clock_id
            or bar.interval != (selection.formation_start, selection.formation_end)
            or request.definition_id != bar.definition.id
            or (request.start, request.end) != bar.interval):
        raise ContractError("source bar clock/reset/raw-domain does not match selected formation")
    summary = bar.summary
    observed = (summary.open_ticks, summary.high_ticks, summary.low_ticks, summary.close_ticks)
    spans = request.coverage.observed_intervals
    opening_observed = (summary.first_at is not None and bool(spans)
        and spans[0][0] == selection.formation_start and summary.first_at < spans[0][1])
    closing_observed = (summary.last_at is not None and bool(spans)
        and spans[-1][0] <= summary.last_at and spans[-1][1] == selection.formation_end)
    supports, prices = [], []
    complete = bar.final and bar.coverage_complete
    provenance = tuple(dict.fromkeys((bar.version_id, *summary.content_versions,
                                      bar.coverage_version, *(() if bar.watermark_version is None else (bar.watermark_version,)))))
    for name, price in zip(FIELDS, observed):
        if not summary.prints:
            status, reason = "empty", "no_observed_trades"
        elif not bar.final:
            status, reason = "partial", "forming_prefix"
        elif not complete and not (summary.history_complete and
                ((name == "open" and opening_observed) or (name == "close" and closing_observed))):
            status = "partial"
            reason = ("incomplete_open" if name == "open" and not opening_observed else
                      "incomplete_close" if name == "close" and not closing_observed else
                      "incomplete_price_coverage")
        elif price is None:
            status, reason = ("ambiguous", "ambiguous_" + name) if name in ("open", "close") else ("unavailable", "unpriced_" + name)
        else:
            status, reason = "observed", ("complete_exact_" if complete else "certified_endpoint_") + name
        supports.append(FieldSupport(name, status, reason, provenance))
        prices.append(price if status == "observed" else None)
    status = ("empty" if not summary.prints else "provisional" if not bar.final else
              "final" if complete else "incomplete")
    body = dict(id="range-source:" + digest((selection.clock_id, bar.definition.id, bar.reset_epoch)),
                selection=selection, publication_version_id=bar.version_id,
                source_definition_id=bar.definition.id, reset_epoch=bar.reset_epoch,
                revision=bar.revision, supersedes=predecessor,
                observation_cut=bar.observation_cut, minimum_known_at=bar.minimum_known_at,
                published_at=bar.published_at,
                complete_observation_at=bar.minimum_known_at if complete else None,
                open_ticks=prices[0], high_ticks=prices[1], low_ticks=prices[2], close_ticks=prices[3],
                observed_ohlc=observed, first_event_at=summary.first_at, last_event_at=summary.last_at,
                coverage_complete=bar.coverage_complete, observed_duration=bar.observed_duration,
                coverage_version=bar.coverage_version, watermark_version=bar.watermark_version,
                source_event_ids=summary.event_ids, source_content_versions=summary.content_versions,
                correction_ids=bar.correction_ids, field_support=tuple(supports), status=status)
    identity_body = {**body, "selection": selection.record()}
    return {**body, "version_id": "range-version:" + digest(identity_body)}


def primitive_from_shared_bar(*, selection: ClockSelection, engine: SharedBarEngine,
                              publication_version_id: str, cut: int) -> RangePrimitive:
    if type(engine) is not SharedBarEngine:
        raise ContractError("range primitive requires actual shared-bar factory")
    timestamp(cut)
    _require_clock(selection)
    if selection.selected_at > cut:
        raise DependencyUnavailable("clock selection occurs after requested primitive cut")
    bar, request = engine.window_publication(publication_version_id)
    if not bar.available(cut, final_only=False):
        raise DependencyUnavailable("source publication has not completed")
    predecessor = engine.window_publication_predecessor(publication_version_id)
    value = RangePrimitive(**_project(selection, bar, request, predecessor))
    object.__setattr__(value, "_factory_receipt", (_PRIMITIVE_TOKEN, engine, digest(value.record())))
    return value


def _require_primitive(value, *, cut=None):
    if type(value) is not RangePrimitive:
        raise ContractError("typed range primitive required")
    receipt = value._factory_receipt
    if (type(receipt) is not tuple or len(receipt) != 3 or receipt[0] is not _PRIMITIVE_TOKEN
            or type(receipt[1]) is not SharedBarEngine or receipt[2] != digest(value.record())):
        raise ContractError("primitive lacks its unaltered retained-factory receipt")
    engine = receipt[1]
    bar, request = engine.window_publication(value.publication_version_id)
    predecessor = engine.window_publication_predecessor(value.publication_version_id)
    expected = RangePrimitive(**_project(value.selection, bar, request, predecessor))
    if expected != value:
        raise IntegrityError("primitive differs from actual source publication")
    if cut is not None and (timestamp(cut) < value.published_at or cut < value.selection.selected_at):
        raise DependencyUnavailable("range primitive was unavailable at required cut")
    return engine, bar, request


@dataclass(frozen=True)
class RangeRegistryLinks:
    source_id: str
    evidence_version_id: str
    anchor_id: str
    anchor_version_id: str
    primitive_version: str
    registry_revision: int
    evidence_predecessor: str | None
    anchor_predecessor: str | None
    _receipt: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        for value, prefix in ((self.source_id, "s:"), (self.evidence_version_id, "e:"),
                              (self.anchor_id, "a:"), (self.anchor_version_id, "av:")):
            _name(value)
            if not value.startswith(prefix):
                raise ContractError("incorrect registry lineage namespace")
        _name(self.primitive_version)
        _integer(self.registry_revision, minimum=0)
        if (self.registry_revision == 0) != (self.evidence_predecessor is None and self.anchor_predecessor is None):
            raise ContractError("registry ordinal needs exact paired predecessors")
        for value, prefix in ((self.evidence_predecessor, "e:"), (self.anchor_predecessor, "av:")):
            if value is not None and (not _name(value).startswith(prefix)):
                raise ContractError("incorrect predecessor namespace")

    def record(self):
        return {"source_id": self.source_id, "evidence_version_id": self.evidence_version_id,
                "anchor_id": self.anchor_id, "anchor_version_id": self.anchor_version_id,
                "primitive_version": self.primitive_version, "registry_revision": self.registry_revision,
                "evidence_predecessor": self.evidence_predecessor, "anchor_predecessor": self.anchor_predecessor}


def _link_values(primitive, previous):
    source_id = "s:" + digest(primitive.id)
    anchor_id = "a:" + digest((primitive.id, "formation"))
    revision = 0 if previous is None else previous.registry_revision + 1
    ep = None if previous is None else previous.evidence_version_id
    ap = None if previous is None else previous.anchor_version_id
    identity = (primitive.version_id, revision, ep, ap)
    return dict(source_id=source_id, evidence_version_id="e:" + digest(("measurement", identity)),
                anchor_id=anchor_id, anchor_version_id="av:" + digest(("formation", identity)),
                primitive_version=primitive.version_id, registry_revision=revision,
                evidence_predecessor=ep, anchor_predecessor=ap)


def _require_links(links, primitive):
    if type(links) is not RangeRegistryLinks:
        raise ContractError("exact registry links required")
    receipt = links._receipt
    if (type(receipt) is not tuple or len(receipt) != 4 or receipt[0] is not _LINK_TOKEN
            or receipt[1] != primitive or receipt[3] != digest(links.record())):
        raise ContractError("registry links lost their immutable primitive receipt")
    previous = receipt[2]
    if links.record() != _link_values(primitive, previous):
        raise IntegrityError("registry links changed source/revision lineage")
    if previous is not None:
        previous_primitive = previous._receipt[1]
        if (previous.source_id != links.source_id or previous.anchor_id != links.anchor_id
                or primitive.id != previous_primitive.id
                or primitive.revision != previous_primitive.revision + 1
                or primitive.supersedes != previous_primitive.publication_version_id
                or primitive.published_at < previous_primitive.published_at):
            raise ContractError("source stream regressed or skipped a retained publication")
    return previous


def primitive_registry_links(primitive: RangePrimitive, *, previous: RangeRegistryLinks | None = None) -> RangeRegistryLinks:
    _require_primitive(primitive)
    if previous is not None:
        if type(previous) is not RangeRegistryLinks or type(previous._receipt) is not tuple:
            raise ContractError("previous links require their retained immutable receipt")
        old_primitive = previous._receipt[1]
        _require_primitive(old_primitive)
        _require_links(previous, old_primitive)
        if primitive == old_primitive:
            return previous
    value = RangeRegistryLinks(**_link_values(primitive, previous))
    object.__setattr__(value, "_receipt", (_LINK_TOKEN, primitive, previous, digest(value.record())))
    _require_links(value, primitive)
    return value


@dataclass(frozen=True)
class DerivedRangeMember:
    member: ObjectRevision | RelationVersion
    requirements: tuple[tuple[str, tuple[str, ...]], ...]
    _receipt: object = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        if type(self.member) not in (ObjectRevision, RelationVersion) or type(self.requirements) is not tuple:
            raise ContractError("typed derived object/relation and immutable field bindings required")
        seen = set()
        for pair in self.requirements:
            if type(pair) is not tuple or len(pair) != 2:
                raise ContractError("each required field set binds an exact primitive version")
            primitive, names = pair
            _name(primitive)
            if (primitive in seen or type(names) is not tuple or not names
                    or any(name not in FIELDS for name in names)
                    or tuple(name for name in FIELDS if name in names) != names):
                raise ContractError("required field bindings must be unique and canonical")
            seen.add(primitive)
        if isinstance(self.member, RelationVersion) and self.requirements:
            raise ContractError("relation metadata cannot declare object activation support")
        if isinstance(self.member, ObjectRevision) and not self.requirements:
            raise ContractError("derived object needs its exact formula support bindings")


def _derived_member(member, requirements, *, horizon_end=None, range_value=None):
    value = DerivedRangeMember(member, requirements)
    if horizon_end is not None:
        timestamp(horizon_end)
    object.__setattr__(value, "_receipt", (_MEMBER_TOKEN,
        digest((member, requirements, horizon_end,
                None if range_value is None else range_value.version_id)), horizon_end, range_value))
    return value


def _require_derived_member(value):
    receipt = value._receipt
    if (type(receipt) is not tuple or len(receipt) != 4 or receipt[0] is not _MEMBER_TOKEN
            or receipt[1] != digest((value.member, value.requirements, receipt[2],
                                    None if receipt[3] is None else receipt[3].version_id))):
        raise ContractError("derived member lacks its unaltered formula-factory receipt")
    value.__post_init__()
    return receipt[2]


@dataclass(frozen=True)
class RangePublicationReceipt:
    batch_id: str
    batch_version: str
    committed_head: str
    changed: bool
    primitive_versions: tuple[str, ...]
    object_versions: tuple[str, ...]
    known_at: int
    registry_links: tuple[RangeRegistryLinks, ...]


def _current_source_matches(engine, bar, primitive, cut):
    # This is actual F09 prefix reconstruction, not a free provenance check.
    # SharedBarEngine.work exposes its admission/source visits. One capture is
    # reused for every primitive from this engine in publish_range_batch.
    latest = engine.asof(bar_id=bar.bar_id, cut=cut.cut, final_only=False)
    if latest is None or latest.version_id != bar.version_id:
        raise DependencyUnavailable("selected source publication is not current at decision cut")
    summary, _, _ = engine.query(cut, start=primitive.formation_start, end=primitive.formation_end)
    if (summary.event_ids != bar.summary.event_ids or summary.content_versions != bar.summary.content_versions
            or summary.id != bar.summary.id):
        raise DependencyUnavailable("known forming input or correction lacks a current publication")
    relevant = tuple(c.id for c in cut.corrections if any(i == engine.domain.instrument and at is not None
        and primitive.formation_start <= at < primitive.formation_end for i, at in
        ((c.before_instrument, c.before_event_at), (c.after_instrument, c.after_event_at))))
    if relevant != primitive.correction_ids:
        raise DependencyUnavailable("known correction lineage was skipped by selected publication")


def publish_range_batch(*, range_retention=None, **kwargs):
    if range_retention is not None:
        from trading_research.context.ranges import RangeRetention
        if type(range_retention) is not RangeRetention:
            raise ContractError('actual bounded range retention state required')
        with range_retention._lock:
            return _publish_range_batch(range_retention=range_retention, **kwargs)
    return _publish_range_batch(range_retention=None, **kwargs)


def _publish_range_batch(*, graph: ObjectGraph, primitives: tuple[RangePrimitive, ...],
                        registry_links: tuple[RangeRegistryLinks, ...],
                        derived_members: tuple[DerivedRangeMember, ...], batch_id: str,
                        batch_sequence: int, clocks: PublicationClock,
                        expected_head: str | None, range_retention) -> RangePublicationReceipt:
    if (type(graph) is not ObjectGraph or type(clocks) is not PublicationClock
            or type(primitives) is not tuple or not primitives
            or type(registry_links) is not tuple or len(registry_links) != len(primitives)
            or type(derived_members) is not tuple or any(type(v) is not DerivedRangeMember for v in derived_members)):
        raise ContractError("actual registry and complete immutable range batch envelope required")
    _integer(batch_sequence, minimum=1)
    if len(primitives) * 2 + len(derived_members) > graph.definition.batch_members_max:
        raise DependencyUnavailable("range atomic batch exceeds registry member bound")
    by_version, by_evidence, captures, source_members = {}, {}, {}, []
    for primitive, links in zip(primitives, registry_links):
        engine, bar, _ = _require_primitive(primitive, cut=clocks.input_known_at)
        previous = _require_links(links, primitive)
        if primitive.version_id in by_version or links.source_id in {v[1].source_id for v in by_version.values()}:
            raise ContractError("one current primitive per source stream in an atomic range batch")
        if previous is not None:
            ev = graph.get_version(previous.evidence_version_id)
            av = graph.get_version(previous.anchor_version_id)
            old_primitive = previous._receipt[1]
            if (type(ev) is not EvidenceVersion or type(av) is not AnchorVersion
                    or ev.source_id != links.source_id or av.anchor_id != links.anchor_id
                    or ev.revision != previous.registry_revision or av.revision != previous.registry_revision
                    or ev.content_digest != digest(old_primitive.record())
                    or max(ev.known_at, av.known_at) > clocks.input_known_at):
                raise ContractError("actual registry predecessor does not certify supplied receipt")
        key = id(engine)
        if key not in captures:
            captures[key] = engine.capture(clocks.decision_cut)
        _current_source_matches(engine, bar, primitive, captures[key])
        by_version[primitive.version_id] = primitive, links
        by_evidence[links.evidence_version_id] = primitive.version_id
        available_at = max(primitive.published_at, primitive.selection.selected_at,
                           primitive.selection.session.known_at, primitive.selection.interval_graph.known_at)
        evidence = EvidenceVersion(links.source_id, links.evidence_version_id, links.registry_revision,
            links.evidence_predecessor, primitive.last_event_at if primitive.last_event_at is not None else primitive.formation_start,
            available_at, Support.OBSERVED if primitive.source_event_ids else Support.MISSING,
            primitive.instrument, digest(primitive.record()))
        end = primitive.formation_end if bar.final else min(primitive.formation_end, primitive.observation_cut)
        anchor = AnchorVersion(links.anchor_id, links.anchor_version_id, links.registry_revision,
            links.anchor_predecessor, (links.evidence_version_id,), primitive.formation_start, end,
            max(end, primitive.minimum_known_at), available_at)
        source_members.extend((evidence, anchor))
    objects = {v.member.version_id: v.member for v in derived_members
               if type(v.member) is ObjectRevision}
    range_values = []
    for wrapped in derived_members:
        horizon_end = _require_derived_member(wrapped)
        obj = wrapped.member
        if isinstance(obj, RelationVersion):
            # Only the actual object-to-source-anchor relation is admitted by
            # these factories. Direct wrappers cannot manufacture extra edges.
            endpoints = (obj.left, obj.right)
            matched = [(o, links) for primitive, links in by_version.values()
                for o in objects.values() if links.evidence_version_id in o.evidence_versions
                and {e.id for e in endpoints} == {o.version_id, links.anchor_version_id}]
            if (len(matched) != 1 or obj.kind != RelationKind.SHARED_EVIDENCE
                    or obj.known_at != matched[0][0].known_at):
                raise ContractError("relation does not bind an exact derived object and source anchor")
            continue
        if obj.known_at != clocks.known_at:
            raise ContractError("derived object completion differs from atomic publication")
        if obj.birth.generator == 'C01-range-geometry-v1':
            from trading_research.context.ranges import validate_range_version
            range_value = validate_range_version(wrapped._receipt[3])
            if range_retention is None:
                raise ContractError('C01 publication requires its configured retention state')
            range_values.append(range_value)
        if horizon_end is not None:
            ttl = graph.definition.ttl_ns
            if ttl is None:
                raise ContractError("finite location horizon requires actual registry TTL")
            born_at = clocks.known_at
            if obj.supersedes is not None:
                old = graph.object_asof(obj.object_id, clocks.decision_cut)
                if old is None or old.object.version_id != obj.supersedes:
                    raise ContractError("location correction lacks its actual current predecessor")
                born_at = old.born_at
            if horizon_end != born_at + ttl or clocks.known_at >= horizon_end:
                raise ContractError("location horizon must preserve original registry birth and expiry")
        table = FORMULA_REQUIREMENTS.get(obj.birth.generator)
        roles = [] if table is None else [role for role in obj.roles if role in table]
        if len(roles) != 1:
            raise ContractError("object formula role is absent or ambiguous in frozen capability table")
        needed = table[roles[0]]
        bound = set()
        for vid, names in wrapped.requirements:
            if vid not in by_version or names != needed:
                raise ContractError("declared support understates or substitutes registered formula dependencies")
            primitive, links = by_version[vid]
            if primitive.instrument != obj.birth.instrument:
                raise ContractError("range object crossed an unproved raw contract")
            if obj.eligibility == Eligibility.ELIGIBLE and not primitive.supports(*names):
                raise DependencyUnavailable("unsupported range field cannot activate dependent geometry")
            bound.add(links.source_id)
            if links.evidence_version_id not in obj.evidence_versions:
                raise ContractError("derived object must bind exact primitive measurement evidence")
        if bound != set(obj.birth.source_origins) or any(eid not in by_evidence for eid in obj.evidence_versions):
            raise ContractError("range formula source/evidence closure differs from its bindings")
    staged_retention = None if range_retention is None else range_retention._stage(tuple(range_values))
    members = tuple(source_members) + tuple(v.member for v in derived_members)
    batch = AtomicBatch(batch_id, batch_sequence, graph.definition.version, clocks, members, len(members))
    committed_head, changed = graph.commit_batch(batch, expected_head=expected_head)
    if staged_retention is not None:
        range_retention._adopt(staged_retention)
    return RangePublicationReceipt(batch_id, batch.version, committed_head, changed,
        tuple(p.version_id for p in primitives),
        tuple(v.member.version_id for v in derived_members if isinstance(v.member, ObjectRevision)),
        clocks.known_at, registry_links)
