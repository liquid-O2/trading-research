"""Adapters from certified context/source records into the E0 representations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from trading_research.data.book import BookReducer, RecoveryCertificate
from trading_research.data.events import CanonicalEvent, Flags, LatencyScenario
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.execution.venue import VenuePath, VenueQuote, VenueTrade
from trading_research.experiments.e0.admission import E0DayAdmission, require_selected_identity
from trading_research.experiments.e0.candidates import E0Object, FrozenRange, objects
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.range_primitives import RangePrimitive
from trading_research.foundations.time import AvailabilityBasis, timestamp
from trading_research.location.edge_extensions import LocationSet, validate_locations
from trading_research.operations.artifacts import digest
from trading_research.context.ranges import RangeVersion, validate_range_version


@dataclass(frozen=True)
class NativeCoverageReceipt:
    """Immutable proof that a canonical native stream is actually retained.

    A complete interval and a version label alone are metadata.  This record
    binds the bytes represented by the canonical rows to their schema, raw
    instrument, source order, coverage window, and any recovery evidence.
    """

    source_id: str
    schema_version: str
    instrument_id: str
    window_start: int
    window_end: int
    row_count: int
    source_orders: tuple[int | None, ...]
    source_versions: tuple[str, ...]
    raw_bytes: bytes
    raw_sha256: str
    complete_intervals: tuple[tuple[int, int], ...]
    source_order_known: bool
    recovery_event_ids: tuple[str, ...] = ()
    recovery_certificate_ids: tuple[str, ...] = ()
    recovery_complete: bool = True
    coverage_version: str = ""

    def __post_init__(self) -> None:
        _name(self.source_id, "native source ID")
        _name(self.schema_version, "native schema version")
        _name(self.instrument_id, "native instrument ID")
        timestamp(self.window_start)
        timestamp(self.window_end)
        if self.window_start >= self.window_end:
            raise ContractError("native coverage window must be positive")
        if type(self.row_count) is not int or self.row_count <= 0:
            raise ContractError("native coverage row count must be a positive integer")
        if type(self.source_orders) is not tuple or len(self.source_orders) != self.row_count:
            raise ContractError("native source order count must equal retained row count")
        if type(self.source_order_known) is not bool:
            raise ContractError("native source-order availability must be explicit")
        if self.source_order_known:
            if any(type(value) is not int or value < 0 for value in self.source_orders):
                raise ContractError("known native source order must retain nonnegative integer sequences")
            if tuple(sorted(self.source_orders)) != self.source_orders or len(set(self.source_orders)) != len(self.source_orders):
                raise ContractError("known native source order must be strictly increasing")
        elif any(value is not None and type(value) is not int for value in self.source_orders):
            raise ContractError("unknown native source order may contain only integers or None")
        if type(self.source_versions) is not tuple or not self.source_versions:
            raise ContractError("native source versions are required")
        for value in self.source_versions:
            _name(value, "native source version")
        if type(self.raw_bytes) is not bytes or not self.raw_bytes:
            raise ContractError("native coverage must retain nonempty raw source bytes")
        if type(self.raw_sha256) is not str or self.raw_sha256 != sha256(self.raw_bytes).hexdigest():
            raise ContractError("native raw bytes and SHA-256 do not agree")
        if type(self.complete_intervals) is not tuple or not self.complete_intervals:
            raise ContractError("native coverage needs retained complete intervals")
        previous_end = None
        for start, end in self.complete_intervals:
            timestamp(start)
            timestamp(end)
            if start >= end or previous_end is not None and start < previous_end:
                raise ContractError("native complete intervals must be ordered positive half-open spans")
            previous_end = end
        if self.complete_intervals[0][0] > self.window_start or self.complete_intervals[-1][1] < self.window_end:
            raise ContractError("native complete intervals must enclose the retained source window")
        for value, label in ((self.recovery_event_ids, "recovery event"),
                             (self.recovery_certificate_ids, "recovery certificate")):
            if type(value) is not tuple or any(type(item) is not str or not item for item in value):
                raise ContractError(f"native {label} identities must be an immutable tuple")
            if len(set(value)) != len(value):
                raise ContractError(f"native {label} identities must be unique")
        if len(self.recovery_event_ids) != len(self.recovery_certificate_ids):
            raise ContractError("native recovery events and certificate evidence must have matching cardinality")
        if type(self.recovery_complete) is not bool:
            raise ContractError("native recovery completeness must be explicit")
        if self.coverage_version:
            _name(self.coverage_version, "native coverage version")

    @property
    def version(self) -> str:
        return digest(self)

    @classmethod
    def from_events(cls, events: tuple[CanonicalEvent, ...], *, source_id: str,
                    schema_version: str, instrument_id: str,
                    complete_intervals: tuple[tuple[int, int], ...],
                    source_order_known: bool = True,
                    recovery_event_ids: tuple[str, ...] = (),
                    recovery_certificate_ids: tuple[str, ...] = (),
                    recovery_complete: bool = True,
                    coverage_version: str = "") -> "NativeCoverageReceipt":
        if type(events) is not tuple or not events:
            raise ContractError("native receipt construction requires a nonempty canonical event tuple")
        if any(event.address.dataset_id != source_id for event in events):
            raise IntegrityError("native receipt source ID does not match every canonical event address")
        event_times = tuple(
            event.clocks.event_at if event.clocks.event_at is not None else event.clocks.known_at
            for event in events
        )
        raw_bytes = b"".join(event.raw_record if event.raw_record is not None else event.raw_fields for event in events)
        return cls(
            source_id=source_id,
            schema_version=schema_version,
            instrument_id=instrument_id,
            window_start=min(event_times),
            window_end=max(event_times) + 1,
            row_count=len(events),
            source_orders=tuple(event.provider_sequence for event in events),
            source_versions=tuple(dict.fromkeys(event.address.source_version for event in events)),
            raw_bytes=raw_bytes,
            raw_sha256=sha256(raw_bytes).hexdigest(),
            complete_intervals=complete_intervals,
            source_order_known=source_order_known,
            recovery_event_ids=recovery_event_ids,
            recovery_certificate_ids=recovery_certificate_ids,
            recovery_complete=recovery_complete,
            coverage_version=coverage_version,
        )


def _name(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise ContractError(f"{label} requires a nonempty identity")
    return value


def _fraction_tick(value: Any, *, tick_size: Decimal = Decimal("0.25")) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        ratio = Fraction(value) / Fraction(tick_size)
    elif isinstance(value, Fraction):
        ratio = value / Fraction(tick_size)
    else:
        raise ContractError("source prices must retain exact Decimal/Fraction values")
    if ratio.denominator != 1:
        raise ContractError("source event price is off the selected raw contract tick grid")
    return ratio.numerator


def _instrument_id(value: Any) -> str:
    if isinstance(value, E0DayAdmission):
        return value.selected_instrument_id
    if isinstance(value, InstrumentDefinition):
        return value.key.instrument_id
    if isinstance(value, Mapping):
        raw = value.get("instrument_id", value.get("id", value.get("raw_id")))
        if raw is None:
            raise ContractError("selected instrument mapping lacks raw instrument ID")
        return str(raw)
    if hasattr(value, "key") and hasattr(value.key, "instrument_id"):
        return str(value.key.instrument_id)
    if hasattr(value, "raw_id"):
        return str(value.raw_id)
    if type(value) in (str, int):
        return str(value)
    raise ContractError("selected raw instrument identity is required")


def _instrument_lifetime(value: Any) -> str | None:
    if isinstance(value, E0DayAdmission):
        return value.selected_lifetime
    if isinstance(value, InstrumentDefinition):
        return instrument_identity(value)
    if isinstance(value, Mapping):
        return value.get("instrument_lifetime", value.get("lifetime"))
    if hasattr(value, "instrument_lifetime"):
        return value.instrument_lifetime
    return None


def _tick_size(value: Any, explicit: Decimal | None = None) -> Decimal:
    if explicit is not None:
        if not isinstance(explicit, Decimal) or explicit <= 0:
            raise ContractError("positive exact tick size required")
        return explicit
    for source in (value, getattr(value, "selected_definition", None)):
        if isinstance(source, InstrumentDefinition) and source.tick_size is not None:
            return source.tick_size
        if isinstance(source, Mapping) and source.get("tick_size") is not None:
            raw = source["tick_size"]
            return raw if isinstance(raw, Decimal) else Decimal(str(raw))
        if hasattr(source, "tick_size") and isinstance(source.tick_size, Decimal):
            return source.tick_size
    # The synthetic and E0 NQ fixtures use the registered NQ quarter-point
    # coordinate.  A caller with another contract must bind its tick explicitly.
    return Decimal("0.25")


@dataclass(frozen=True)
class E0FrozenContext:
    selected_day: E0DayAdmission
    range_06_09: FrozenRange | None
    prior_rth: FrozenRange | None
    e0_objects: tuple[E0Object, ...]
    cut: int
    source_versions: tuple[str, ...]
    range_lineage: tuple[tuple[str, str, str | None], ...] = ()
    sidecars: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if type(self.selected_day) is not E0DayAdmission:
            raise ContractError("frozen E0 context requires the admitted raw day")
        timestamp(self.cut)
        if type(self.e0_objects) is not tuple or any(type(o) is not E0Object for o in self.e0_objects):
            raise ContractError("E0 objects must be an immutable typed tuple")
        for row in (self.range_06_09, self.prior_rth):
            if row is not None:
                self.selected_day.require_instrument(row.instrument)
                if row.known_at > self.cut:
                    raise DependencyUnavailable("future range publication cannot enter a decision cut")
        if type(self.source_versions) is not tuple or not self.source_versions:
            raise ContractError("E0 context needs source version lineage")
        if any(o.instrument != self.selected_day.selected_instrument_id for o in self.e0_objects):
            raise ContractError("E0 object tuple mixes raw instrument identities")

    @property
    def objects(self) -> tuple[E0Object, ...]:
        return self.e0_objects

    @property
    def instrument(self) -> str:
        return self.selected_day.selected_instrument_id

    @property
    def version(self) -> str:
        return digest(self)

    def require_instrument(self, value: Any) -> None:
        self.selected_day.require_instrument(value)


def _range_fields(value: RangeVersion, *, role: str) -> tuple[str, int, int, int, int, int, str, str | None, str | None, str | None]:
    if type(value) is not RangeVersion:
        raise ContractError("E0 ranges must come from an actual RangeVersion factory result")
    validate_range_version(value)
    if not value.usable_e0 or value.geometry is None:
        raise DependencyUnavailable("E0 range requires a final certified positive exact geometry")
    geometry = value.geometry
    if geometry.open is None or geometry.close is None:
        raise DependencyUnavailable("E0 range requires exact open and close fields")
    primitive = value.primitive
    selection = primitive.selection
    raw_id = selection.instrument.raw_id
    source_identity = selection.instrument.definition_version
    process = f"{role}:{value.definition.id}:{value.definition.version}"
    return (
        raw_id,
        primitive.formation_start,
        primitive.formation_end,
        value.known_at,
        primitive.revision,
        geometry.low,
        geometry.high,
        geometry.open,
        geometry.close,
        value.version_id,
        primitive.supersedes,
        process,
        source_identity,
    )


def _frozen_from_range(value: RangeVersion, *, role: str, cut: int,
                       selected_day: E0DayAdmission,
                       prior_selection: Any = None) -> FrozenRange:
    fields = _range_fields(value, role=role)
    (raw_id, start, end, known_at, revision, low, high, opened, closed,
     publication, supersedes, process, source_identity) = fields
    selected_day.require_instrument(raw_id)
    if known_at > cut:
        raise DependencyUnavailable("range publication is after the requested E0 decision cut")
    if role == "prior_rth":
        if prior_selection is None:
            raise ContractError("prior_RTH requires actual calendar predecessor selection")
        if isinstance(prior_selection, Mapping):
            selected = prior_selection.get("instrument_id", prior_selection.get("selected_instrument_id"))
            if selected is not None and str(selected) != selected_day.selected_instrument_id:
                raise DependencyUnavailable("prior contract levels need an explicit known-time roll mapping before E0 contact comparison")
            predecessor = prior_selection.get("preceding_session", prior_selection.get("session_id"))
            if predecessor is None:
                raise ContractError("prior_RTH predecessor identity is missing")
        else:
            selected = getattr(prior_selection, "selected_instrument_id", None)
            if selected is not None and str(selected) != selected_day.selected_instrument_id:
                raise DependencyUnavailable("prior contract levels need an explicit known-time roll mapping before E0 contact comparison")
    selection = value.primitive.selection
    clock_id = getattr(selection, "clock_id", None)
    return FrozenRange(
        id=value.id,
        instrument=raw_id,
        start=start,
        end=end,
        known_at=known_at,
        low=low,
        high=high,
        open=opened,
        close=closed,
        observation_process=process,
        source_version=publication,
        complete=True,
        instrument_lifetime=selected_day.selected_lifetime,
        clock_id=clock_id,
        selection_version=getattr(selection, "version_id", None),
        publication_version=publication,
        supersedes=supersedes,
        source_identity=source_identity,
    )


def _frozen_from_locations(prior_rth: LocationSet, *, cut: int,
                           selected_day: E0DayAdmission,
                           prior_selection: Any) -> FrozenRange:
    if type(prior_rth) is not LocationSet:
        raise ContractError("prior-RTH bridge requires RangeVersion or certified LocationSet")
    validate_locations(prior_rth)
    if prior_selection is None:
        raise ContractError("prior_RTH requires actual calendar predecessor selection")
    if not prior_rth.available(cut):
        raise DependencyUnavailable("prior-RTH location set is unavailable at the selected cut")
    if prior_rth.semantic != "prior_RTH":
        raise ContractError("prior location set uses another semantic")
    values = {loc.role.removeprefix("prior_"): loc.geometry.lower for loc in prior_rth.locations}
    if set(values) != {"open", "high", "low", "close"}:
        raise DependencyUnavailable("prior-RTH source lacks an exact complete OHLC set")
    primitive = prior_rth.primitive
    raw_id = primitive.selection.instrument.raw_id
    selected_day.require_instrument(raw_id)
    if isinstance(prior_selection, Mapping):
        selected = prior_selection.get("instrument_id", prior_selection.get("selected_instrument_id"))
        if selected is not None and str(selected) != selected_day.selected_instrument_id:
            raise DependencyUnavailable("prior contract levels need an explicit known-time roll mapping before E0 contact comparison")
    return FrozenRange(
        id="prior-rth:" + prior_rth.version,
        instrument=raw_id,
        start=primitive.formation_start,
        end=primitive.formation_end,
        known_at=prior_rth.clocks.known_at,
        low=values["low"], high=values["high"], open=values["open"], close=values["close"],
        observation_process="prior_rth:" + prior_rth.generator,
        source_version=prior_rth.version,
        complete=True,
        instrument_lifetime=selected_day.selected_lifetime,
        clock_id=getattr(primitive.selection, "clock_id", None),
        selection_version=getattr(primitive.selection, "version_id", None),
        publication_version=prior_rth.version,
        source_identity=primitive.selection.instrument.definition_version,
    )


def freeze_e0_ranges(*, selected_day: E0DayAdmission, range_06_09: RangeVersion,
                     prior_rth: RangeVersion | LocationSet,
                     prior_selection: Any, cut: int) -> E0FrozenContext:
    """Bind certified C01 and prior-RTH outputs without rebuilding OHLC."""
    if type(selected_day) is not E0DayAdmission:
        raise ContractError("selected_day must be an admitted E0 raw day")
    timestamp(cut)
    if type(range_06_09) is not RangeVersion:
        raise ContractError("range_06_09 must be the typed RangeVersion output")
    current = _frozen_from_range(range_06_09, role="06_09", cut=cut, selected_day=selected_day)
    if type(prior_rth) is RangeVersion:
        previous = _frozen_from_range(prior_rth, role="prior_rth", cut=cut,
                                      selected_day=selected_day, prior_selection=prior_selection)
    elif type(prior_rth) is LocationSet:
        previous = _frozen_from_locations(prior_rth, cut=cut, selected_day=selected_day,
                                          prior_selection=prior_selection)
    else:
        raise ContractError("prior_RTH requires an actual RangeVersion/LocationSet source")
    if current.instrument != previous.instrument:
        raise DependencyUnavailable("prior contract levels need an explicit known-time roll mapping before E0 contact comparison")
    admitted = objects(current, previous, cut=cut)
    versions = tuple(dict.fromkeys((current.source_version, previous.source_version,
                                    current.selection_version or "selection-unavailable",
                                    previous.selection_version or "selection-unavailable")))
    lineage = ((current.id, current.source_version, current.supersedes),
               (previous.id, previous.source_version, previous.supersedes))
    sidecars = (
        ("range_06_09_definition", current.observation_process),
        ("prior_rth_definition", previous.observation_process),
        ("selected_lifetime", selected_day.selected_lifetime),
    )
    return E0FrozenContext(selected_day, current, previous, admitted, cut, versions, lineage, sidecars)


def freeze_e0_context(*args, **kwargs) -> E0FrozenContext:
    """Compatibility alias used by older orchestration drafts."""
    return freeze_e0_ranges(*args, **kwargs)


def _coverage(value: Any) -> NativeCoverageReceipt:
    """Accept only a retained typed receipt, never a boolean/label shortcut."""
    if isinstance(value, NativeCoverageReceipt):
        return value
    if not isinstance(value, Mapping):
        raise ContractError("venue coverage requires a NativeCoverageReceipt")
    receipt = value.get("source_receipt")
    if not isinstance(receipt, NativeCoverageReceipt):
        raise ContractError("venue coverage must retain a typed source receipt")
    rows = value.get("complete_intervals", value.get("intervals"))
    version = value.get("version", value.get("coverage_version", ""))
    if rows is not None and tuple(rows) != receipt.complete_intervals:
        raise IntegrityError("coverage metadata does not match the retained source receipt")
    if version and version != receipt.coverage_version:
        raise IntegrityError("coverage version does not match the retained source receipt")
    if "source_order_known" in value and value["source_order_known"] is not receipt.source_order_known:
        raise IntegrityError("source-order metadata does not match the retained source receipt")
    if "source_versions" in value and tuple(value["source_versions"]) != receipt.source_versions:
        raise IntegrityError("source-version metadata does not match the retained source receipt")
    return receipt


def _validate_coverage_against_events(receipt: NativeCoverageReceipt,
                                      events: tuple[CanonicalEvent, ...],
                                      instrument: str) -> None:
    if receipt.instrument_id != instrument:
        raise ContractError("native receipt instrument does not match the admitted raw instrument")
    if receipt.row_count != len(events):
        raise IntegrityError("native receipt row count does not match retained canonical events")
    if not events:
        raise ContractError("venue path cannot be built from an empty native source")
    addresses = tuple(event.address for event in events)
    if any(address.dataset_id != receipt.source_id for address in addresses):
        raise IntegrityError("native event source IDs do not match the retained source receipt")
    if any(address.schema_version != receipt.schema_version for address in addresses):
        raise IntegrityError("native event schema versions do not match the retained source receipt")
    source_versions = tuple(dict.fromkeys(address.source_version for address in addresses))
    if source_versions != receipt.source_versions:
        raise IntegrityError("native event source versions do not match the retained source receipt")
    orders = tuple(event.provider_sequence for event in events)
    if orders != receipt.source_orders:
        raise IntegrityError("native event order does not match the retained source receipt")
    event_bytes = b"".join(event.raw_record if event.raw_record is not None else event.raw_fields for event in events)
    if sha256(event_bytes).hexdigest() != receipt.raw_sha256 or event_bytes != receipt.raw_bytes:
        raise IntegrityError("native event bytes do not match the retained source receipt hash")
    for event in events:
        event_at = event.clocks.event_at if event.clocks.event_at is not None else event.clocks.known_at
        if not any(start <= event_at < end for start, end in receipt.complete_intervals):
            raise DependencyUnavailable("native event lies outside the retained complete coverage intervals")
    event_ids = {event.id for event in events}
    if not set(receipt.recovery_event_ids).issubset(event_ids):
        raise IntegrityError("native recovery receipt names an event absent from the retained source")


def _validated_recovery_certificates(receipt: NativeCoverageReceipt,
                                     events: tuple[CanonicalEvent, ...],
                                     certificates: Any) -> tuple[RecoveryCertificate, ...]:
    """Bind supplied recovery certificates exactly to the retained receipt.

    A certificate list is evidence for the receipt's declared recovery claims,
    not an independent optional sidecar.  Mapping keys may use either the
    canonical event ID or its source-address ID, but the certificate's own
    recovery event identity must still agree with that key.
    """
    event_by_identity = {}
    for event in events:
        for identity in (event.id, event.address.id):
            if identity in event_by_identity and event_by_identity[identity] != event.id:
                raise IntegrityError("native recovery event identities are ambiguous")
            event_by_identity[identity] = event.id
    if certificates is None:
        certificates = ()
    if isinstance(certificates, Mapping):
        rows = []
        for key, certificate in certificates.items():
            event_id = event_by_identity.get(key)
            if event_id is None:
                raise IntegrityError("supplied recovery certificate key names an unused event")
            if type(certificate) is not RecoveryCertificate:
                raise ContractError("book recovery evidence must use RecoveryCertificate")
            if certificate.recovery_event_id != event_id:
                raise IntegrityError("recovery certificate key contradicts its event identity")
            rows.append(certificate)
        certificates = tuple(rows)
    elif type(certificates) is not tuple:
        certificates = tuple(certificates)
    if any(type(certificate) is not RecoveryCertificate for certificate in certificates):
        raise ContractError("book recovery evidence must use RecoveryCertificate")
    if len({certificate.recovery_event_id for certificate in certificates}) != len(certificates):
        raise IntegrityError("supplied recovery certificates contain duplicate event claims")
    if len({certificate.evidence_id for certificate in certificates}) != len(certificates):
        raise IntegrityError("supplied recovery certificates contain duplicate evidence claims")
    expected = set(zip(receipt.recovery_event_ids, receipt.recovery_certificate_ids))
    supplied = {(certificate.recovery_event_id, certificate.evidence_id)
                for certificate in certificates}
    if supplied != expected or len(certificates) != len(expected):
        raise IntegrityError("supplied recovery certificates do not exactly match the native receipt evidence")
    event_by_id = {event.id: event for event in events}
    for certificate in certificates:
        event = event_by_id.get(certificate.recovery_event_id)
        if event is None:
            raise IntegrityError("supplied recovery certificate names an event absent from the retained source")
        if certificate.instrument_id != event.instrument_id:
            raise IntegrityError("supplied recovery certificate changes the recovered instrument")
    return tuple(certificates)


def _recovery_for(event: CanonicalEvent, certificates: Any) -> RecoveryCertificate | None:
    if certificates is None:
        return None
    if isinstance(certificates, Mapping):
        value = certificates.get(event.id, certificates.get(event.address.id))
        if value is None:
            return None
        certificates = (value,)
    if type(certificates) is not tuple:
        certificates = tuple(certificates)
    for cert in certificates:
        if type(cert) is not RecoveryCertificate:
            raise ContractError("book recovery evidence must use RecoveryCertificate")
        if cert.recovery_event_id == event.id:
            return cert
    return None


def _event_state(market_state: Any, event: CanonicalEvent) -> str:
    if isinstance(market_state, Mapping):
        value = market_state.get(event.id, market_state.get(event.address.id))
    elif callable(market_state):
        value = market_state(event)
    else:
        value = market_state
    if value is None:
        raise ContractError("market state must be retained explicitly for every native event")
    if value not in ("continuous", "auction", "halted", "closed", "unknown"):
        raise ContractError("market state must use the registered venue state vocabulary")
    return value


def venue_path_from_mbp(*, canonical_events: tuple[CanonicalEvent, ...],
                        selected_instrument: Any, coverage: Any,
                        recovery_certificates: Any = (), market_state: Any = None,
                        latency_scenario: Any = None, source_manifest: Any = None,
                        tick_size: Decimal | None = None) -> VenuePath:
    """Normalize one canonical MBP stream through BookReducer and VenuePath."""
    if type(canonical_events) not in (tuple, list) or any(type(e) is not CanonicalEvent for e in canonical_events):
        raise ContractError("venue path requires canonical normalized event records")
    instrument = _instrument_id(selected_instrument)
    expected_numeric = int(instrument) if instrument.isdigit() else None
    receipt = _coverage(coverage)
    _validate_coverage_against_events(receipt, tuple(canonical_events), instrument)
    validated_recovery_certificates = _validated_recovery_certificates(
        receipt, tuple(canonical_events), recovery_certificates,
    )
    if not receipt.recovery_complete:
        raise DependencyUnavailable("native recovery evidence is incomplete")
    if type(latency_scenario) is not LatencyScenario:
        raise ContractError("venue path requires a typed LatencyScenario; receipt latency cannot be coerced")
    source_mapping = source_manifest if isinstance(source_manifest, Mapping) else {}
    source_version = source_mapping.get("source_version", source_mapping.get("version"))
    tick = _tick_size(selected_instrument, tick_size)
    reducer = BookReducer()
    quotes: list[VenueQuote] = []
    trades: list[VenueTrade] = []
    quality = {
        "event_count": 0,
        "duplicate_rows": 0,
        "book_invalid_rows": 0,
        "snapshot_rows": 0,
        "bad_receive_rows": 0,
        "unpriced_flow": 0,
        "unknown_side_volume": 0,
        "trade_volume": 0,
        "flow_complete": True,
        "recovered_rows": 0,
    }
    seen_ids: set[str] = set()
    known_clocks: list[tuple[str, int]] = []
    receipt_claims: list[tuple[str, str]] = []
    for event in canonical_events:
        quality["event_count"] += 1
        if expected_numeric is not None and event.instrument_id != expected_numeric:
            raise ContractError("mixed raw contracts in venue path")
        if event.id in seen_ids:
            # BookReducer handles exact source-address duplicates; a repeated
            # immutable record must not become a second economic event.
            quality["duplicate_rows"] += 1
        seen_ids.add(event.id)
        if event.flags & Flags.MAYBE_BAD_BOOK:
            quality["book_invalid_rows"] += 1
        if event.flags & Flags.SNAPSHOT:
            quality["snapshot_rows"] += 1
        if event.flags & Flags.BAD_TS_RECV:
            quality["bad_receive_rows"] += 1
            receipt_claims.append((event.id, "uncertain_due_to_F_BAD_TS_RECV"))
        event_at = event.clocks.event_at
        if event_at is None:
            raise DependencyUnavailable("native venue replay requires its actual event clock")
        anchor = event_at if latency_scenario.anchor == "event" else event.clocks.provider_received_at
        if anchor is None:
            raise DependencyUnavailable("latency scenario requires a retained provider-receive clock")
        if (latency_scenario.anchor == "provider_received" and event.flags & Flags.BAD_TS_RECV
                and latency_scenario.uncertainty_ns == 0):
            raise DependencyUnavailable("unreliable provider receive time requires an explicit uncertainty scenario")
        assumed_known_at = timestamp(anchor + latency_scenario.delay_ns)
        # A newly declared scenario replaces an earlier historical assumption.
        # It can never make an actual strategy receipt arrive sooner.
        known_at = (max(event.clocks.known_at, assumed_known_at)
                    if event.clocks.basis is not AvailabilityBasis.ASSUMED else assumed_known_at)
        known_clocks.append((event.id, known_at))
        recovery = _recovery_for(event, validated_recovery_certificates)
        transition = reducer.apply(event, recovery=recovery)
        if transition.duplicate:
            # Keep the duplicate in quality evidence, but never make it a
            # second economic quote/trade row.
            quality["flow_complete"] = quality["flow_complete"] and transition.after.flow_complete
            continue
        if recovery is not None:
            quality["recovered_rows"] += 1
        if event.trade_eligible:
            quantity = event.size
            quality["trade_volume"] += quantity
            if event.aggressor is None:
                quality["unknown_side_volume"] += quantity
            if event.price is None:
                quality["unpriced_flow"] += quantity
            else:
                trades.append(VenueTrade(
                    id=event.id,
                    instrument=instrument,
                    event_at=event.clocks.event_at if event.clocks.event_at is not None else event.clocks.known_at,
                    sequence=event.provider_sequence,
                    ticks=_fraction_tick(event.price, tick_size=tick),
                    quantity=quantity,
                    aggressor=event.aggressor,
                    source_version=event.address.source_version,
                ))
        if event.action in {"A", "M", "C"} and transition.after.quote is not None:
            quote = transition.after.quote
            if quote.bid is None or quote.ask is None or quote.bid_size is None or quote.ask_size is None:
                continue
            event_at = event.clocks.event_at if event.clocks.event_at is not None else event.clocks.known_at
            quotes.append(VenueQuote(
                id=event.id,
                instrument=instrument,
                event_at=event_at,
                known_at=known_at,
                sequence=event.provider_sequence,
                bid=_fraction_tick(quote.bid, tick_size=tick),
                ask=_fraction_tick(quote.ask, tick_size=tick),
                bid_size=quote.bid_size,
                ask_size=quote.ask_size,
                book_valid=transition.after.trusted,
                market_state=_event_state(market_state, event),
                source_version=event.address.source_version,
            ))
        quality["flow_complete"] = quality["flow_complete"] and transition.after.flow_complete
    path = VenuePath(instrument=instrument, quotes=tuple(quotes), trades=tuple(trades),
                     complete_intervals=receipt.complete_intervals,
                     coverage_version=receipt.coverage_version)
    path.quality = MappingProxyType(dict(quality))
    path.source_version = source_version or digest(tuple(e.id for e in canonical_events))
    path.latency_scenario = latency_scenario
    path.event_ids = tuple(e.id for e in canonical_events)
    path.selected_lifetime = _instrument_lifetime(selected_instrument)
    path.raw_flags = tuple((e.id, int(e.flags)) for e in canonical_events)
    path.canonical_events = tuple(canonical_events)
    path.selected_day = selected_instrument
    path.coverage = receipt
    path.recovery_certificates = validated_recovery_certificates
    path.tick_size = tick
    path.market_state = market_state
    path.source_schema_version = receipt.schema_version
    path.source_row_count = receipt.row_count
    path.source_sha256 = receipt.raw_sha256
    path.known_clocks = tuple(known_clocks)
    path.receipt_latency_claims = tuple(receipt_claims)
    path.version = digest((path.version, receipt.version, latency_scenario,
                           path.known_clocks, path.receipt_latency_claims,
                           path.recovery_certificates, path.selected_lifetime))
    return path


def _trade_key(value: Any, tick_size: Decimal) -> tuple:
    if isinstance(value, VenueTrade):
        return value.instrument, value.event_at, value.ticks, value.quantity, value.aggressor
    if isinstance(value, CanonicalEvent):
        if not value.trade_eligible:
            raise ContractError("trade reconciliation received an ineligible native row")
        price = None if value.price is None else _fraction_tick(value.price, tick_size=tick_size)
        return str(value.instrument_id), value.clocks.event_at, price, value.size, value.aggressor
    if isinstance(value, Mapping):
        instrument = value.get("instrument_id", value.get("instrument"))
        at = value.get("event_at", value.get("t"))
        price = value.get("price_ticks", value.get("price"))
        quantity = value.get("size", value.get("quantity"))
        side = value.get("aggressor", value.get("side"))
        if side in ("B", "A", "N"):
            side = {"B": 1, "A": -1, "N": None}[side]
        if (type(instrument) not in (str, int) or not str(instrument) or type(at) is not int
                or price is not None and type(price) is not int
                or type(quantity) is not int or quantity <= 0 or side not in (-1, 1, None)):
            raise ContractError("standalone reconciliation needs exact raw identity, clock, ticks and volume")
        return str(instrument), at, price, quantity, side
    raise ContractError("trade reconciliation requires typed source rows")


@dataclass(frozen=True)
class TradeReconciliation:
    primary: tuple[Any, ...]
    duplicate_standalone: tuple[Any, ...]
    distinct_standalone: tuple[Any, ...]
    unknown_unpriced: tuple[Any, ...]
    primary_volume: int
    duplicate_volume: int
    distinct_volume: int
    unknown_volume: int

    @property
    def version(self) -> str:
        return digest(self)


def reconcile_trade_streams(*, primary: tuple[Any, ...], standalone: tuple[Any, ...],
                            canonical_events: tuple[CanonicalEvent, ...] = (),
                            tick_size: Decimal = Decimal("0.25")) -> TradeReconciliation:
    """Reconcile explicit embedded identities without unioning alternate prints.

    Missing aggressor metadata can match a proven embedded row. It is never
    enough, by itself, to deduplicate a coincident price/time/size tuple.
    """
    if type(primary) is not tuple or type(standalone) is not tuple or type(canonical_events) is not tuple:
        raise ContractError("trade reconciliation requires immutable retained source tuples")
    if any(type(event) is not CanonicalEvent for event in canonical_events):
        raise ContractError("embedded row links require retained canonical source addresses")
    keyed = tuple((_trade_key(row,tick_size),row) for row in primary)
    sources = {event.id:event for event in canonical_events}
    for row in primary:
        if type(row) is CanonicalEvent:
            sources[row.id] = row
    links = {}
    for key,row in keyed:
        event = sources.get(getattr(row,"id",None))
        if event is not None:
            if _trade_key(event,tick_size) != key:
                raise IntegrityError("primary trade differs from its retained canonical source row")
            links.setdefault(event.address.row,[]).append((key,row))
    keys = {key for key,_ in keyed}
    duplicate,distinct,unknown = [],[],[]
    for row in standalone:
        key = _trade_key(row,tick_size)
        if key[2] is None:
            unknown.append(row)
            continue
        embedded = row.get("embedded_row_id") if isinstance(row,Mapping) else None
        if embedded is not None:
            matches = links.get(embedded,())
            if len(matches) != 1:
                raise DependencyUnavailable("standalone embedded identity lacks one retained primary source row")
            primary_key,_ = matches[0]
            if key[:4] != primary_key[:4] or key[4] is not None and key[4] != primary_key[4]:
                raise IntegrityError("standalone copy contradicts its exact embedded source identity")
            duplicate.append(row)
        elif key in keys and key[4] is not None:
            duplicate.append(row)
        else:
            distinct.append(row)
    volume = lambda rows: sum(_trade_key(row,tick_size)[3] for row in rows)
    return TradeReconciliation(primary,tuple(duplicate),tuple(distinct),tuple(unknown),
                               volume(primary),volume(duplicate),volume(distinct),volume(unknown))


deduplicate_trade_streams = reconcile_trade_streams


__all__ = [
    "E0FrozenContext", "freeze_e0_ranges", "freeze_e0_context",
    "NativeCoverageReceipt", "venue_path_from_mbp", "TradeReconciliation", "reconcile_trade_streams",
    "deduplicate_trade_streams",
]
