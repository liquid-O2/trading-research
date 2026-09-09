"""Complete E0 candidate populations and two-clock fixed-end labels."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import groupby
from types import MappingProxyType
from typing import Any, Mapping

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.experiments.e0.candidates import Contact, E0Object, VisitTracker
from trading_research.foundations.contracts import Band, Capability, Target
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import Ticks, Unit
from trading_research.execution.venue import VenuePath
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.object_labels import ExactPoint, ObjectTarget, reference_object_label
from trading_research.research.labels import ObservationWindow, PathLabel, PathPoint, reference_path_label


def _as_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    raise ContractError("E0 observation prices require exact integer/Fraction ticks")


def _text(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise ContractError(f"{label} requires a nonempty identity")
    return value


@dataclass(frozen=True)
class E0CandidateRow:
    id: str
    decision_set_id: str
    cut: int
    object_id: str
    object_version: str
    instrument: str
    side: int
    price: Fraction | None
    band: Band | None
    born_at: int
    known_at: int
    source_version: str
    distance: Fraction | None
    state: str
    reason: str
    order_key: tuple
    observation_process: str
    contact: Contact | None = None
    visit: int | None = None
    approach: int | None = None
    fade_side: int | None = None
    range_width: Fraction | None = None

    def __post_init__(self) -> None:
        for value, label in ((self.id, "candidate"), (self.decision_set_id, "decision set"),
                             (self.object_id, "object"), (self.object_version, "object version"),
                             (self.instrument, "instrument"), (self.source_version, "source"),
                             (self.reason, "reason"), (self.observation_process, "observation process")):
            _text(value, label)
        timestamp(self.cut); timestamp(self.born_at); timestamp(self.known_at)
        if self.born_at > self.known_at or self.known_at > self.cut:
            raise ContractError("candidate birth/availability is future relative to its cut")
        if type(self.side) is not int or self.side not in (-1, 0, 1):
            raise ContractError("candidate side must be long, short, or background")
        if self.side == 0:
            if self.object_id != "none" or self.price is not None or self.band is not None:
                raise ContractError("background row cannot carry an object or price")
        elif not isinstance(self.price, Fraction) or type(self.band) is not Band:
            raise ContractError("object candidate requires exact price and contact band")
        if self.distance is not None and not isinstance(self.distance, Fraction):
            raise ContractError("candidate distance must retain exact ticks")
        if self.contact is not None and self.side == 0:
            raise ContractError("background row cannot be contacted")

    @property
    def version(self) -> str:
        return digest(self)

    @property
    def decision_at(self) -> int:
        return self.cut


@dataclass(frozen=True)
class E0DecisionSet:
    id: str
    cut: int
    instrument: str
    rows: tuple[E0CandidateRow, ...]
    source_versions: tuple[str, ...]
    population_hash: str
    prepared_descriptor_sha256: str
    policy_id: str

    def __post_init__(self) -> None:
        _text(self.id, "decision set")
        _text(self.instrument, "instrument")
        timestamp(self.cut)
        if type(self.rows) is not tuple or any(type(row) is not E0CandidateRow for row in self.rows):
            raise ContractError("decision set rows must be immutable E0 candidate rows")
        if type(self.source_versions) is not tuple or any(type(v) is not str or not v for v in self.source_versions):
            raise ContractError("decision set source versions are required")
        for value, label in ((self.population_hash, "population hash"),
                             (self.prepared_descriptor_sha256, "prepared descriptor hash"),
                             (self.policy_id, "policy")):
            _text(value, label)
        if any(row.decision_set_id != self.id or row.cut != self.cut for row in self.rows):
            raise ContractError("candidate row points at another decision set")

    @property
    def version(self) -> str:
        return digest(self)


class E0Population(tuple):
    """Tuple-compatible population return with indexed decision-set metadata."""

    def __new__(cls, rows: tuple[E0CandidateRow, ...], decision_sets: tuple[E0DecisionSet, ...],
                *, population_hash: str, prepared_descriptor_sha256: str):
        value = tuple.__new__(cls, rows)
        value.decision_sets = decision_sets
        value.population_hash = population_hash
        value.prepared_descriptor_sha256 = prepared_descriptor_sha256
        value.version = digest((rows, decision_sets, population_hash, prepared_descriptor_sha256))
        return value

    @property
    def rows(self) -> tuple[E0CandidateRow, ...]:
        return tuple(self)

    def by_cut(self, cut: int) -> E0DecisionSet:
        for value in self.decision_sets:
            if value.cut == cut:
                return value
        raise KeyError(cut)


def _context_objects(frozen_context: Any, object_versions: Any) -> tuple[E0Object, ...]:
    source = object_versions if object_versions is not None else getattr(frozen_context, "objects", None)
    if source is None and isinstance(frozen_context, Mapping):
        source = frozen_context.get("objects", frozen_context.get("e0_objects"))
    if source is None:
        raise ContractError("E0 candidate population requires source-backed object versions")
    values = []
    for row in tuple(source):
        if type(row) is E0Object:
            values.append(row)
            continue
        if isinstance(row, Mapping):
            try:
                values.append(E0Object(
                    id=str(row["id"]), type=str(row.get("type", "E0:object")),
                    instrument=str(row.get("instrument", row.get("instrument_id"))),
                    price=_as_fraction(row.get("price", row.get("price_ticks"))),
                    band=row.get("band") if isinstance(row.get("band"), Band) else Band(
                        _as_fraction(row.get("price", row.get("price_ticks"))) - 1,
                        _as_fraction(row.get("price", row.get("price_ticks"))) + 1),
                    born_at=int(row.get("born_at", row.get("known_at"))),
                    source_version=str(row["source_version"]),
                    range_width=(_as_fraction(row["range_width"]) if row.get("range_width") is not None else None),
                    known_at=int(row.get("known_at", row.get("born_at"))),
                ))
            except KeyError as exc:
                raise ContractError("candidate object mapping lacks its frozen source fields") from exc
            continue
        raise ContractError("candidate population cannot rebuild an object from a name-only row")
    if len({row.id for row in values}) != len(values):
        raise ContractError("duplicate object identity in E0 population")
    return tuple(values)


def _context_instrument(frozen_context: Any, objects: tuple[E0Object, ...]) -> str:
    value = getattr(frozen_context, "instrument", None)
    if value is None and isinstance(frozen_context, Mapping):
        value = frozen_context.get("instrument", frozen_context.get("instrument_id"))
    value = value or (objects[0].instrument if objects else None)
    if value is None:
        raise ContractError("E0 population has no selected raw instrument")
    return str(value)


def _context_sources(frozen_context: Any) -> tuple[str, ...]:
    values = getattr(frozen_context, "source_versions", None)
    if values is None and isinstance(frozen_context, Mapping):
        values = frozen_context.get("source_versions", ())
    values = tuple(values or ())
    if any(type(v) is not str or not v for v in values):
        raise ContractError("population source versions must be explicit")
    if not values:
        raise ContractError("population requires retained source version lineage")
    return values


def _sampled_value(values: Any, cut: int) -> Fraction | None:
    if values is None:
        return None
    if isinstance(values, Mapping):
        value = values.get(cut)
        if value is None:
            value = values.get(str(cut))
        if value is None:
            # Accept the literal cut used by fixtures as an ISO key only when
            # its value is unambiguous; do not infer between nearby cuts.
            for key, candidate in values.items():
                if isinstance(key, Mapping) and key.get("utc_ns") == cut:
                    value = candidate
                    break
    else:
        value = None
    if isinstance(value, Mapping):
        value = value.get("midpoint", value.get("midpoint_ticks", value.get("price")))
    return None if value is None else _as_fraction(value)


def _cut_values(completed_cuts: Any) -> tuple[int, ...]:
    if type(completed_cuts) not in (tuple, list) or not completed_cuts:
        raise ContractError("E0 population needs a nonempty immutable completed-cut sequence")
    cuts = tuple(timestamp(c) for c in completed_cuts)
    if tuple(sorted(cuts)) != cuts or len(set(cuts)) != len(cuts):
        raise ContractError("completed decision cuts must be strictly chronological")
    return cuts


def build_e0_decision_population(*, frozen_context: Any, completed_cuts: tuple[int, ...],
                                 sampled_midpoints: Any, object_versions: Any = None,
                                 path_coverage: Any = None, account_state: Any = None,
                                 policy_id: str = "declared-e0-population-v1",
                                 maximum_gap_ns: int = 60_000_000_000) -> E0Population:
    """Materialize every object-side row and one background row per cut.

    The return is tuple-compatible with the registered API while exposing
    ``decision_sets`` for runners that need one hash per minute.  ``account_state``
    is deliberately ignored when constructing the population; risk/outcome
    annotations cannot alter candidate eligibility.
    """
    cuts = _cut_values(completed_cuts)
    objects = _context_objects(frozen_context, object_versions)
    instrument = _context_instrument(frozen_context, objects)
    if any(obj.instrument != instrument for obj in objects):
        raise ContractError("E0 candidate population mixes admitted raw instruments")
    if any(obj.available_at > cuts[-1] for obj in objects):
        raise ContractError("object known_at exceeds decision cut")
    sources = _context_sources(frozen_context)
    _text(policy_id, "policy")
    if type(maximum_gap_ns) is not int or maximum_gap_ns <= 0:
        raise ContractError("sampled midpoint gap tolerance must be a positive integer")
    if path_coverage is not None and isinstance(path_coverage, Mapping):
        if path_coverage.get("same_time_ordering") in (None, "ambiguous") and path_coverage.get("source_order_known") is False:
            # Candidate order is still deterministic, but an unproved native
            # path is retained as label uncertainty rather than selected here.
            pass
    tracker = VisitTracker(maximum_gap_ns=maximum_gap_ns)
    all_rows: list[E0CandidateRow] = []
    sets: list[E0DecisionSet] = []
    for cut in cuts:
        available = tuple(sorted((obj for obj in objects if obj.instrument == instrument
                                  and obj.available_at <= cut), key=lambda obj: (obj.born_at, obj.id)))
        midpoint = _sampled_value(sampled_midpoints, cut)
        contacts = tracker.observe(cut=cut, price=midpoint, candidates=available)
        by_object = {contact.object_id: contact for contact in contacts}
        descriptors = tuple((obj.id, obj.version, obj.instrument, obj.price, obj.band,
                             obj.born_at, obj.available_at, obj.source_version, obj.observation_process)
                            for obj in available)
        # Side rows are a population contract: the future label or policy is
        # never consulted in deciding whether a row exists.
        population_descriptor = (instrument, cut, descriptors, sources, policy_id,
                                 midpoint, tracker.checkpoint())
        decision_id = "ds:" + digest(population_descriptor)
        rows: list[E0CandidateRow] = []
        for obj in available:
            contact = by_object.get(obj.id)
            distance = None if midpoint is None else abs(midpoint - obj.price)
            state = "contact" if contact is not None else "no_touch"
            reason = "sampled_midpoint_contact" if contact is not None else (
                "missing_midpoint_at_cut" if midpoint is None else "no_object_band_contact")
            for side in (1, -1):
                # The source object identity is the stable candidate identity;
                # the decision-set/cut remains a separate row binding.
                candidate_id = f"{obj.id}:{'long' if side == 1 else 'short'}"
                rows.append(E0CandidateRow(
                    id=candidate_id, decision_set_id=decision_id, cut=cut,
                    object_id=obj.id, object_version=obj.version, instrument=instrument,
                    side=side, price=obj.price, band=obj.band, born_at=obj.born_at,
                    known_at=obj.available_at, source_version=obj.source_version,
                    distance=distance, state=state, reason=reason,
                    order_key=(distance is None, distance if distance is not None else Fraction(0),
                               obj.born_at, obj.id, 0 if side == 1 else 1),
                    observation_process=obj.observation_process, contact=contact,
                    visit=None if contact is None else contact.visit,
                    approach=None if contact is None else contact.approach,
                    fade_side=None if contact is None else contact.fade_side,
                    range_width=obj.range_width,
                ))
        rows.append(E0CandidateRow(
            id=f"background:{cut}", decision_set_id=decision_id, cut=cut,
            object_id="none", object_version="background", instrument=instrument,
            side=0, price=None, band=None, born_at=cut, known_at=cut,
            source_version=sources[0], distance=None, state="background",
            reason="background_no_candidate_contact" if not contacts else "background_population_row",
            order_key=(True, Fraction(0), cut, "", 2), observation_process="clock_population",
        ))
        rows.sort(key=lambda row: row.order_key)
        immutable_rows = tuple(rows)
        population_hash = digest((decision_id, immutable_rows, sources, policy_id))
        prepared = digest(tuple((row.id, row.object_id, row.side, row.price,
                                 row.source_version, row.born_at, row.known_at)
                                for row in immutable_rows))
        sets.append(E0DecisionSet(decision_id, cut, instrument, immutable_rows, sources,
                                  population_hash, prepared, policy_id))
        all_rows.extend(immutable_rows)
    full_hash = digest(tuple((row.decision_set_id, row.id, row.object_version, row.side,
                              row.price, row.source_version, row.cut) for row in all_rows))
    prepared_hash = digest(tuple((row.id, row.object_id, row.side, row.price,
                                  row.source_version, row.cut) for row in all_rows))
    return E0Population(tuple(all_rows), tuple(sets), population_hash=full_hash,
                        prepared_descriptor_sha256=prepared_hash)


@dataclass(frozen=True)
class E0LabelBundle:
    candidate_id: str
    target: ObjectTarget
    sampled_contact: Contact | None
    label: Mapping[str, Any]
    coverage: ObservationWindow
    native_event_ids: tuple[str, ...]
    rejected_event_ids: tuple[str, ...]
    sampled_observation_version: str
    version: str = ""
    sampled_contacts: tuple[Contact, ...] = ()

    def __post_init__(self) -> None:
        _text(self.candidate_id, "candidate")
        if type(self.target) is not ObjectTarget or not isinstance(self.label, Mapping):
            raise ContractError("label bundle requires typed target and immutable label mapping")
        if type(self.coverage) is not ObservationWindow:
            raise ContractError("label bundle requires typed observation coverage")
        for values in (self.native_event_ids, self.rejected_event_ids):
            if type(values) is not tuple or any(type(v) is not str or not v for v in values):
                raise ContractError("label event IDs must be immutable")
        _text(self.sampled_observation_version, "sampled observation")
        if (type(self.sampled_contacts) is not tuple
                or any(type(contact) is not Contact for contact in self.sampled_contacts)
                or self.sampled_contact != (self.sampled_contacts[0] if self.sampled_contacts else None)):
            raise ContractError("sampled contact must be the first retained sampled visit")
        object.__setattr__(self, "label", MappingProxyType(dict(self.label)))
        expected = digest({"candidate_id": self.candidate_id, "target": self.target,
                           "sampled_contact": self.sampled_contact, "label": dict(self.label),
                           "coverage": self.coverage, "native_event_ids": self.native_event_ids,
                           "rejected_event_ids": self.rejected_event_ids,
                           "sampled_observation_version": self.sampled_observation_version,
                           "sampled_contacts": self.sampled_contacts})
        if self.version and self.version != expected:
            raise IntegrityError("label bundle was mutated after publication")
        object.__setattr__(self, "version", expected)

    @property
    def visit_count(self) -> int:
        return len(self.sampled_contacts)

    @property
    def coverage_annotation(self) -> Mapping:
        """Future coverage remains distinct from a missing initial midpoint."""
        return MappingProxyType({"status": "censored" if self.coverage.gaps or self.coverage.end < self.target.end
                                 else "observed", "gap": self.coverage.gaps,
                                 "maturity_at": self.coverage.certified_through})

    def __getitem__(self, key: str) -> Any:
        if key in self.label:
            return self.label[key]
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default


def _row_value(row: Any, name: str, default: Any = None) -> Any:
    if isinstance(row, Mapping):
        return row.get(name, default)
    return getattr(row, name, default)


def _native_rows(path: VenuePath, native_observation: str) -> tuple[tuple[str, int, int, Fraction, int | None, int], ...]:
    """Retain native venue time independently of strategy availability."""
    if type(path) is not VenuePath:
        raise ContractError("E0 native labels require a typed venue path")
    if native_observation not in ("bbo_midpoint", "eligible_trade"):
        raise ContractError("E0 native label must select its declared midpoint or eligible-trade stream")
    result = []
    if native_observation == "eligible_trade":
        for row in path.trades:
            result.append((row.id, row.event_at, row.event_at, Fraction(row.ticks), row.sequence, 0))
    else:
        for row in path.quotes:
            if not row.book_valid or row.market_state != "continuous":
                continue
            result.append((row.id, row.event_at, row.known_at, Fraction(row.bid + row.ask, 2), row.sequence, 1))
    # A trade retains its original known clock in the canonical source sidecar.
    sources = {event.id: event for event in getattr(path, "canonical_events", ())}
    known_clocks = dict(getattr(path, "known_clocks", ()))
    if native_observation == "eligible_trade" and any(row[0] not in sources for row in result):
        raise DependencyUnavailable("eligible-trade label needs its retained canonical availability clocks")
    result = [(*row[:2], known_clocks.get(row[0], sources[row[0]].clocks.known_at), *row[3:])
              if row[5] == 0 and row[0] in sources else row for row in result]
    return tuple(sorted(result, key=lambda row: (row[1], row[4] if row[4] is not None else -1,
                                                row[5], row[0])))


def _coverage_for(path: VenuePath, cut: int, target_end: int, points: tuple, native_observation: str) -> ObservationWindow:
    if type(path) is not VenuePath or not path.complete_intervals or not path.coverage_version:
        raise DependencyUnavailable("fixed-end label requires an explicit native coverage receipt")
    intervals = path.complete_intervals
    observed_end = min(target_end, max(end for _, end in intervals))
    if observed_end <= cut:
        raise DependencyUnavailable("native observation ended before the original decision cut")
    gaps = []
    cursor = cut
    for start, end in intervals:
        start, end = max(start, cut), min(end, observed_end)
        if end <= start:
            continue
        if start > cursor:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < observed_end:
        gaps.append((cursor, observed_end))
    # An invalid or noncontinuous quote state cannot certify unseen prices.
    unavailable = None
    state_quotes = path.quotes if native_observation == "bbo_midpoint" else ()
    for quote in state_quotes:
        if quote.event_at > observed_end:
            break
        valid = quote.book_valid and quote.market_state == "continuous"
        if not valid and unavailable is None:
            unavailable = max(cut, quote.event_at)
        elif valid and unavailable is not None:
            if unavailable < quote.event_at:
                gaps.append((unavailable, min(quote.event_at, observed_end)))
            unavailable = None
    if unavailable is not None and unavailable < observed_end:
        gaps.append((unavailable, observed_end))
    merged = []
    for start, end in sorted(gaps):
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    retained = tuple(point for point in points if cut < point[1] <= observed_end)
    known = max((observed_end, *(point[2] for point in retained),
                 *(quote.known_at for quote in state_quotes if quote.event_at <= observed_end)))
    receipt = getattr(path, "coverage", None)
    ordered = bool(getattr(receipt, "source_order_known", True)) and all(point[4] is not None for point in retained)
    return ObservationWindow(cut, observed_end, max(observed_end, known), tuple(merged), ordered,
                             digest((path.coverage_version, tuple(merged), observed_end)))


def _label_inputs(candidate_row, sampled_midpoints, venue_path, target_end, source_order_policy, native_observation):
    if type(candidate_row) is not E0CandidateRow or candidate_row.side not in (-1, 1):
        raise ContractError("native label requires an actual object-side E0 candidate row")
    if type(venue_path) is not VenuePath or venue_path.instrument != candidate_row.instrument:
        raise ContractError("native label path changed the admitted raw instrument")
    if not isinstance(sampled_midpoints, Mapping):
        raise ContractError("sampled observations need exact completed-cut values")
    timestamp(target_end)
    if target_end <= candidate_row.cut:
        raise ContractError("E0 target end must remain after its decision cut")
    if source_order_policy not in ("event_at_then_source_order_when_supported", "known", "ambiguous", "require"):
        raise ContractError("unregistered native source-order policy")
    rows = _native_rows(venue_path, native_observation)
    coverage = _coverage_for(venue_path, candidate_row.cut, target_end, rows, native_observation)
    if source_order_policy == "ambiguous":
        coverage = ObservationWindow(coverage.start, coverage.end, coverage.certified_through,
                                     coverage.gaps, False, coverage.version)
    # 'known'/'require' cannot turn absent provider ordering into a fact.
    accepted = tuple(row for row in rows if candidate_row.cut < row[1] <= coverage.end
                     and not any(start <= row[1] < end for start, end in coverage.gaps))
    rejected = tuple(row[0] for row in rows if row not in accepted)
    sampled = []
    for key, value in sampled_midpoints.items():
        at = timestamp(int(key))
        if not candidate_row.cut <= at <= target_end:
            continue
        if at % 60_000_000_000:
            raise ContractError("sampled contact observations must use completed one-minute cuts")
        if isinstance(value, Mapping):
            value = value.get("midpoint_ticks", value.get("midpoint", value.get("price")))
        sampled.append((at, None if value is None else _as_fraction(value)))
    sampled.sort()
    if len({at for at, _ in sampled}) != len(sampled):
        raise ContractError("duplicate sampled decision cut")
    return accepted, rejected, coverage, tuple(sampled)


def label_e0_candidate(*, candidate_row: E0CandidateRow, sampled_midpoints: Mapping,
                       venue_path: VenuePath, target_end: int,
                       observation_process: str,
                       native_observation: str = "bbo_midpoint",
                       source_order_policy: str = "event_at_then_source_order_when_supported",
                       favorable_distance: Fraction = Fraction(8),
                       adverse_distance: Fraction = Fraction(8)) -> E0LabelBundle:
    """Join future sampled-contact diagnostics to a separate native object label.

    Future sampled visits belong to this matured label artifact.  They never
    change the already published candidate or cause an entry at a native touch.
    """
    rows, rejected, coverage, sampled = _label_inputs(candidate_row, sampled_midpoints, venue_path,
                                                     target_end, source_order_policy, native_observation)
    _text(observation_process, "observation process")
    favorable_distance, adverse_distance = _as_fraction(favorable_distance), _as_fraction(adverse_distance)
    target = ObjectTarget(candidate_row.id, candidate_row.object_version, candidate_row.cut,
        target_end, candidate_row.band, candidate_row.side, favorable_distance, adverse_distance,
        observation_process + ":" + native_observation)
    obj = E0Object(candidate_row.object_id, "label-sampled-contact", candidate_row.instrument,
        candidate_row.price, candidate_row.band, candidate_row.born_at, candidate_row.source_version,
        candidate_row.range_width, known_at=candidate_row.known_at)
    tracker = VisitTracker(maximum_gap_ns=60_000_000_000)
    contacts = []
    for at, midpoint in sampled:
        for contact in tracker.observe(cut=at, price=midpoint, candidates=(obj,)):
            # Retain the exact original object version, not the diagnostic
            # wrapper used to share the public sampled-visit reducer.
            contacts.append(Contact(candidate_row.object_id, candidate_row.object_version,
                contact.visit, contact.at, contact.price, contact.approach, contact.fade_side))
    initial = dict(sampled).get(candidate_row.cut)
    if initial is None:
        label = {"target_version": target.version, "object_version": target.object_version,
            "observation_version": coverage.version, "observed_end": coverage.end,
            "maturity_at": coverage.certified_through, "reach_status": "no_midpoint",
            "contact_at": None, "contact_price": None, "departure": "flat_or_wait",
            "fixed_end": target_end, "reason": "missing_midpoint_at_cut", "status": "unavailable"}
    else:
        points = tuple(ExactPoint(at, sequence if sequence is not None else index, price, known)
                       for index, (_, at, known, price, sequence, _) in enumerate(rows))
        label = reference_object_label(target, initial=initial, points=points, coverage=coverage)
        if coverage.end < target_end or coverage.gaps:
            status, reason = "censored", "observation ended before fixed endpoint or crossed a declared gap"
        elif label["departure"] == "ambiguous":
            status, reason = "ambiguous", "source order is unknown; favorable order cannot be invented"
        elif label["reach_status"] == "no_contact" and label["gap_crossings"]:
            status, reason = "observed", "price jumped over the frozen band; crossing is not contact"
        else:
            status, reason = "observed", "complete fixed-end object observation"
        label = {**label, "status": status, "reason": reason}
    return E0LabelBundle(candidate_row.id, target, contacts[0] if contacts else None,
        label, coverage, tuple(row[0] for row in rows), rejected,
        digest(sampled), sampled_contacts=tuple(contacts))


@dataclass(frozen=True)
class E0PricePathLabelBundle:
    """A typed price-path control does not contain an object-departure label."""
    candidate_id: str
    target: Target
    label: PathLabel
    coverage: ObservationWindow
    native_event_ids: tuple[str, ...]
    rejected_event_ids: tuple[str, ...]
    rejection_reasons: tuple[tuple[str, str], ...]
    target_definition: bytes
    control_type: str = "typed_price_path_control"

    def __post_init__(self):
        if (type(self.target) is not Target or type(self.label) is not PathLabel
                or self.label.target_signature != self.target.signature
                or type(self.target_definition) is not bytes
                or self.target.definition_version != digest(self.target_definition)
                or self.control_type != "typed_price_path_control"):
            raise ContractError("price-path control must retain its actual typed target and label")

    @property
    def version(self):
        return digest(self)


def label_e0_price_path(*, candidate_row: E0CandidateRow, sampled_midpoints: Mapping,
                       venue_path: VenuePath, target_end: int, observation_process: str,
                       native_observation: str = "bbo_midpoint",
                       source_order_policy: str = "event_at_then_source_order_when_supported",
                       up_ticks: int = 8, down_ticks: int = 8) -> E0PricePathLabelBundle:
    rows, rejected, coverage, sampled = _label_inputs(candidate_row, sampled_midpoints, venue_path,
                                                     target_end, source_order_policy, native_observation)
    initial = dict(sampled).get(candidate_row.cut)
    if initial is None:
        raise DependencyUnavailable("typed price-path control needs its original midpoint")
    if initial.denominator != 1 or any(row[3].denominator != 1 for row in rows):
        raise ContractError("typed integer-tick price-path control cannot round fractional midpoints")
    definition = canonical_json({"schema": "E0FixedPricePathV1", "initial_ticks": initial,
        "up_ticks": up_ticks, "down_ticks": down_ticks, "decision_at": candidate_row.cut,
        "horizon_end": target_end, "native_observation": native_observation,
        "source_order_policy": source_order_policy})
    target = Target(candidate_row.id + ":price-path", digest(definition), candidate_row.instrument,
        candidate_row.cut, target_end, observation_process + ":" + native_observation, candidate_row.decision_set_id, Unit.TICKS,
        frozenset({Capability.FIRST_PASSAGE, Capability.EXCURSIONS, Capability.TERMINAL_RETURN}))
    points = tuple(PathPoint(at, sequence if sequence is not None else index, Ticks(int(price)), known)
                   for index, (_, at, known, price, sequence, _) in enumerate(rows))
    label = reference_path_label(target, initial=Ticks(int(initial)), points=points, coverage=coverage,
                                 up_ticks=up_ticks, down_ticks=down_ticks)
    source = {row[0]: row for row in _native_rows(venue_path, native_observation)}
    reasons = tuple((identity, "event_at is beyond the frozen target end" if source[identity][1] > target_end
                     else "event is outside the actual future observation window") for identity in rejected)
    return E0PricePathLabelBundle(candidate_row.id, target, label, coverage, tuple(row[0] for row in rows),
                                 rejected, reasons, definition)


__all__ = [
    "E0CandidateRow", "E0DecisionSet", "E0Population", "E0LabelBundle",
    "build_e0_decision_population", "label_e0_candidate",
    "E0PricePathLabelBundle", "label_e0_price_path",
]
