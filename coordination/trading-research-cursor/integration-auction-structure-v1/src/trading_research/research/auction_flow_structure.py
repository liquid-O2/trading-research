"""Streaming full-source directional changes and finalized-bar pivots.

This unpublished arithmetic kernel repeats the scalar DirectionalChanges and
pivot_reference recurrences on one bounded prepared source stream and on
append-only finalized CausalBar cadence. It does not authenticate F09
producer recipes, certify venue completeness, admit a scale-training
result, or complete M03/M08. History completeness is a controller-supplied
segment mask, not a venue certificate. Adaptive mid-leg threshold updates
are not implemented.
"""
from __future__ import annotations

from collections import deque
from copy import copy
from dataclasses import dataclass
from fractions import Fraction

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.bars import CausalBar
from trading_research.measurements.structure import Swing
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_windows import PreparedTradeBatch


VERSION = "auction-flow-unpublished-causal-structure-arithmetic-v1"
_F09 = "This arithmetic layer does not authenticate F09 producer recipes."
_VENUE = "history_complete is a controller segment mask, not a venue completeness certificate."
_FAILED_SWING = "a failed directional-change stream cannot resume partial state"
_FAILED_PIVOT = "a failed final-bar pivot stream cannot resume partial state"
_PROJECTION = "the actual unreleased PreparedTradeBatch and proper slice bounds are required"
_MAX_DEFINITIONS = 32
_MAX_SOURCE_ROWS = 50_000_000
_MAX_EMITTED_SWINGS = 500_000
_MAX_BARS = 100_000
_MAX_EMITTED_PIVOTS = 200_000
_MAX_PIVOT_LENGTH = 1000
_CLOCK_END = 2 ** 63 - 1_000_000_000
_TIES = frozenset({"strict", "earliest", "latest", "ambiguous"})
_NUMERIC = ("t", "known_at_ns", "price", "price_valid", "instrument_id",
            "source_row", "source_order", "raw_flags", "side")
_FIXED_KIND = "fixed_threshold_directional_change"
_PIVOT_STREAM_KIND = "final_bar_pivot_stream_definition"


def _exact_int(value, *, name, minimum=None, maximum=None):
    if type(value) is not int:
        raise ContractError(f"{name} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ContractError(f"{name} is outside its finite bound")
    if maximum is not None and value > maximum:
        raise ContractError(f"{name} is outside its finite bound")
    return value


def _exact_bool(value, *, name):
    if type(value) is not bool:
        raise ContractError(f"{name} must be an exact boolean")
    return value


def _nonempty_str(value, *, name):
    if type(value) is not str or not value:
        raise ContractError(f"{name} must be a nonempty string")
    return value


def _row_index(value):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise IntegrityError(_PROJECTION)
    return int(value)


def _clock_pair(start, end):
    _exact_int(start, name="start", minimum=0, maximum=_CLOCK_END - 1)
    _exact_int(end, name="end", minimum=1, maximum=_CLOCK_END - 1)
    if not start < end:
        raise ContractError("exact half-open event interval required")
    return start, end


def _positive_threshold(value):
    if type(value) is int:
        if value < 1:
            raise ContractError("directional-change threshold needs a positive exact tick size")
        return Fraction(value)
    if type(value) is Fraction:
        if value <= 0:
            raise ContractError("directional-change threshold needs a positive exact tick size")
        return value
    raise ContractError("directional-change threshold must be a positive int or Fraction")


def _normalized_ticks(value):
    ticks = Fraction(value)
    return ticks.numerator, ticks.denominator


def _fixed_threshold_id(version, reversal_ticks, frozen_at):
    numerator, denominator = _normalized_ticks(reversal_ticks)
    return digest({"frozen_at": frozen_at, "kind": _FIXED_KIND,
                   "reversal_ticks": [numerator, denominator], "version": version})


def _pivot_stream_id(version, left, right, ties, frozen_at):
    return digest({"frozen_at": frozen_at, "kind": _PIVOT_STREAM_KIND, "left": left,
                   "right": right, "ties": ties, "version": version})


def _point_record(point):
    if point is None:
        return None
    return {"event_at": point.event_at, "known_at": point.known_at, "ticks": point.ticks,
            "source_order": point.source_order, "source_row": point.source_row,
            "source_key": point.source_key}


def _reference_pivot_definition(*, left, right, ties):
    return digest({"left": left, "right": right, "ties": ties, "kind": "final_bar_pivot"})


def _validate_owned_source_key(prepared, left, count, source_key):
    import pyarrow as pa
    import pyarrow.compute as pc

    owned = getattr(prepared, "_source_key", None)
    if owned is None:
        raise IntegrityError(_PROJECTION)
    piece = owned.slice(left, count)
    if piece.null_count:
        raise IntegrityError("mixed acquired source or wrong source_key")
    equal = pc.all(pc.equal(pc.cast(piece, pa.string()), pa.scalar(source_key, type=pa.string())))
    if equal.as_py() is not True:
        raise IntegrityError("mixed acquired source or wrong source_key")


@dataclass(frozen=True)
class FixedThresholdDefinition:
    """Frozen fixed-threshold identity. The threshold does not update mid-leg."""

    version: str
    reversal_ticks: int | Fraction
    frozen_at: int

    def __post_init__(self):
        _nonempty_str(self.version, name="definition version")
        _exact_int(self.frozen_at, name="frozen_at", minimum=0, maximum=2 ** 63 - 1)
        _positive_threshold(self.reversal_ticks)

    @property
    def threshold(self):
        return Fraction(self.reversal_ticks)

    @property
    def id(self):
        return _fixed_threshold_id(self.version, self.reversal_ticks, self.frozen_at)


@dataclass(frozen=True)
class SourcePoint:
    """One selected source print retained as live extreme/origin/last state."""

    event_at: int
    known_at: int
    ticks: int | None
    source_order: int
    source_row: int
    source_key: str


@dataclass(frozen=True)
class StreamedSwing:
    """Append-only unpublished swing. Origin is the first post-reset point, then the previous extreme."""

    unpublished_arithmetic: bool
    side: str
    price_ticks: int
    extreme_event_at: int
    extreme_known_at: int
    extreme_source_order: int
    extreme_source_row: int
    extreme_source_key: str
    confirmation_event_at: int
    confirmation_known_at: int
    confirmation_source_order: int
    confirmation_source_row: int
    confirmation_source_key: str
    origin_event_at: int
    origin_known_at: int
    origin_ticks: int
    origin_source_order: int
    origin_source_row: int
    origin_source_key: str
    origin_kind: str
    threshold: Fraction
    definition_id: str
    definition_version: str
    instrument_id: int
    delay_ns: int
    status: str

    @property
    def extreme_start(self):
        return self.extreme_event_at

    @property
    def extreme_end(self):
        return self.extreme_event_at

    @property
    def confirmed_at(self):
        return self.confirmation_known_at

    @property
    def confirmation_delay_ns(self):
        return self.confirmation_known_at - self.extreme_event_at


@dataclass(frozen=True)
class FinalBarPivotDefinition:
    version: str
    left: int
    right: int
    ties: str
    frozen_at: int

    def __post_init__(self):
        _nonempty_str(self.version, name="pivot definition version")
        _exact_int(self.left, name="left", minimum=1, maximum=_MAX_PIVOT_LENGTH)
        _exact_int(self.right, name="right", minimum=1, maximum=_MAX_PIVOT_LENGTH)
        _exact_int(self.frozen_at, name="frozen_at", minimum=0, maximum=2 ** 63 - 1)
        if type(self.ties) is not str or self.ties not in _TIES:
            raise ContractError("bounded pivot lengths and explicit equality convention required")

    @property
    def id(self):
        return _pivot_stream_id(self.version, self.left, self.right, self.ties, self.frozen_at)

    @property
    def reference_definition_id(self):
        return _reference_pivot_definition(left=self.left, right=self.right, ties=self.ties)


@dataclass(frozen=True)
class StreamedPivot:
    unpublished_arithmetic: bool
    f09_producer_authenticated: bool
    id: str
    instrument: str
    side: str
    price_ticks: int
    extreme_start: int
    extreme_end: int
    confirmed_at: int
    source_versions: tuple
    definition_version: str
    status: str
    center_start: int
    center_end: int
    support_version_ids: tuple
    max_published_at: int
    definition_id: str
    left: int
    right: int
    ties: str
    interval_ns: int
    version: str

    def reference_swing(self):
        return Swing(self.id, self.instrument, self.side, self.price_ticks, self.extreme_start,
                     self.extreme_end, self.confirmed_at, self.source_versions,
                     self.definition_version, self.status)


class _ScaleState:
    __slots__ = ("definition", "threshold", "direction", "high", "low", "last", "origin",
                 "visits", "resets", "confirmed_high", "confirmed_low", "complete", "incomplete")

    def __init__(self, definition):
        self.definition = definition
        self.threshold = definition.threshold
        self.direction = 0
        self.high = self.low = self.last = self.origin = None
        self.visits = self.resets = self.confirmed_high = self.confirmed_low = 0
        self.complete = self.incomplete = 0

    def clone(self):
        other = _ScaleState(self.definition)
        other.direction = self.direction
        other.high, other.low, other.last, other.origin = self.high, self.low, self.last, self.origin
        other.visits, other.resets = self.visits, self.resets
        other.confirmed_high, other.confirmed_low = self.confirmed_high, self.confirmed_low
        other.complete, other.incomplete = self.complete, self.incomplete
        return other


def _reset_scale(state, last):
    state.direction = 0
    state.high = state.low = state.origin = None
    state.last = last
    state.visits += 1
    state.resets += 1
    state.incomplete += 1


def _emit_swing(*, instrument_id, delay_ns, state, extreme, confirmation, origin, side, origin_kind):
    return StreamedSwing(
        True, side, extreme.ticks, extreme.event_at, extreme.known_at, extreme.source_order,
        extreme.source_row, extreme.source_key, confirmation.event_at,
        max(extreme.known_at, confirmation.known_at), confirmation.source_order,
        confirmation.source_row, confirmation.source_key, origin.event_at, origin.known_at,
        origin.ticks, origin.source_order, origin.source_row, origin.source_key, origin_kind,
        state.threshold, state.definition.id, state.definition.version, instrument_id,
        delay_ns, "confirmed")


def _apply_scale(state, point):
    """Literal DirectionalChanges recurrence; high reversal is tested before low.

    Returns a pending confirmation tuple without constructing StreamedSwing.
    """
    state.visits += 1
    state.complete += 1
    state.last = point
    if state.high is None:
        state.high = state.low = state.origin = point
        return None
    if point.ticks > state.high.ticks:
        state.high = point
    if point.ticks < state.low.ticks:
        state.low = point
    threshold = state.threshold
    if state.direction >= 0 and state.high.ticks - point.ticks >= threshold:
        extreme = state.high
        origin_kind = "segment_first" if state.direction == 0 else "previous_extreme"
        origin = state.origin
        state.direction = -1
        state.origin = extreme
        state.high = state.low = point
        state.confirmed_high += 1
        return "high", extreme, origin, origin_kind
    if state.direction <= 0 and point.ticks - state.low.ticks >= threshold:
        extreme = state.low
        origin_kind = "segment_first" if state.direction == 0 else "previous_extreme"
        origin = state.origin
        state.direction = 1
        state.origin = extreme
        state.high = state.low = point
        state.confirmed_low += 1
        return "low", extreme, origin, origin_kind
    return None


class DirectionalChangeStream:
    """One acquired source, one instrument window, many frozen fixed thresholds."""

    def __init__(self, *, instrument_id, source_key, start, end, delay_ns, definitions,
                 max_source_rows=_MAX_SOURCE_ROWS, max_emitted_rows=_MAX_EMITTED_SWINGS):
        _exact_int(instrument_id, name="instrument_id", minimum=1)
        _nonempty_str(source_key, name="source_key")
        start, end = _clock_pair(start, end)
        _exact_int(delay_ns, name="delay_ns", minimum=0, maximum=1_000_000_000)
        _exact_int(max_source_rows, name="max_source_rows", minimum=1, maximum=_MAX_SOURCE_ROWS)
        _exact_int(max_emitted_rows, name="max_emitted_rows", minimum=1, maximum=_MAX_EMITTED_SWINGS)
        if type(definitions) is not tuple or not 1 <= len(definitions) <= _MAX_DEFINITIONS:
            raise ContractError("a nonempty tuple of at most 32 distinct frozen definitions is required")
        if any(type(item) is not FixedThresholdDefinition for item in definitions):
            raise ContractError("typed frozen directional-change definitions required")
        identities = tuple(item.id for item in definitions)
        if len(set(identities)) != len(identities):
            raise ContractError("directional-change definitions must be distinct")
        labels = tuple(item.version for item in definitions)
        if len(set(labels)) != len(labels):
            raise ContractError("conflicting human version reuse")
        if any(item.frozen_at > start for item in definitions):
            raise ContractError("swing rule must be frozen before the measured path")
        self.instrument_id = instrument_id
        self.source_key = source_key
        self.start = start
        self.end = end
        self.delay_ns = delay_ns
        self.definitions = definitions
        self.max_source_rows = max_source_rows
        self.max_emitted_rows = max_emitted_rows
        self._states = tuple(_ScaleState(item) for item in definitions)
        self._last_event_at = self._last_source_order = self._last_source_row = None
        self._rows = self._slices = self._emitted = 0
        self._reasons = {"rows": 0, "slices": 0, "priced_complete": 0, "unpriced": 0,
                         "flag4": 0, "incomplete_segment": 0, "resets": 0,
                         "unknown_aggressor": 0, "confirmed_high": 0, "confirmed_low": 0,
                         "emitted_rows": 0}
        self._work = {"slices_attempted": 0, "rows_attempted": 0,
                      "definition_visits_attempted": 0, "emissions_attempted": 0,
                      "resets_attempted": 0}
        self._failed = False

    def add_prepared(self, prepared, left=0, right=None, *, history_complete=True):
        if self._failed:
            raise IntegrityError(_FAILED_SWING)
        try:
            return self._add_prepared(prepared, left, right, history_complete=history_complete)
        except BaseException:
            self._failed = True
            raise

    def record(self):
        if self._failed:
            raise IntegrityError(_FAILED_SWING)
        try:
            return self._record()
        except BaseException:
            self._failed = True
            raise

    def snapshot(self):
        if self._failed:
            raise IntegrityError(_FAILED_SWING)
        try:
            return self._snapshot()
        except BaseException:
            self._failed = True
            raise

    def work(self):
        """Read-only attempt counters. Usable after scientific-state failure."""
        return {"failed": self._failed, **dict(self._work)}

    def _add_prepared(self, prepared, left, right, *, history_complete):
        import numpy as np

        _exact_bool(history_complete, name="history_complete")
        if type(prepared) is not PreparedTradeBatch or prepared.released:
            raise IntegrityError(_PROJECTION)
        left = _row_index(left)
        right = len(prepared) if right is None else _row_index(right)
        if not 0 <= left <= right <= len(prepared):
            raise IntegrityError(_PROJECTION)
        self._work["slices_attempted"] += 1
        if left == right:
            self._slices += 1
            self._reasons["slices"] = self._slices
            return ()
        values = prepared.values
        if any(name not in values for name in _NUMERIC):
            raise IntegrityError(_PROJECTION)
        view = {name: values[name][left:right] for name in _NUMERIC}
        if any(column.ndim != 1 or column.dtype.kind not in "iu" or len(column) != right - left
                for column in view.values()):
            raise IntegrityError(_PROJECTION)
        t, known, price, valid, instrument, rows, order, flags, side = (
            view[name] for name in _NUMERIC)
        n = right - left
        priced = valid == 1
        if (np.any(instrument != self.instrument_id) or np.any(t < self.start) or np.any(t >= self.end)
                or np.any(known != t + self.delay_ns) or np.any(t[1:] < t[:-1])
                or np.any(order[1:] <= order[:-1]) or np.any(rows[1:] <= rows[:-1])
                or np.any(order < 0)):
            raise IntegrityError("source identity, window, delay or retained order disagrees")
        if (np.any(~np.isin(valid, (0, 1))) or np.any(flags < 0) or np.any(flags > 255)
                or np.any(~np.isin(side, (-1, 0, 1)))):
            raise IntegrityError("trade validity, side or raw_flags left the admitted domain")
        if np.any(priced & ((price <= 0) | (price >= 2 ** 53))):
            raise ContractError("valid raw prices must retain positive exact tick coordinates")
        _validate_owned_source_key(prepared, left, n, self.source_key)
        first_event, first_order, first_row = int(t[0]), int(order[0]), int(rows[0])
        if self._last_event_at is not None and (
                first_event < self._last_event_at or first_order <= self._last_source_order
                or first_row <= self._last_source_row):
            raise IntegrityError("out-of-order or repeated source rows cannot confirm a directional change")
        if self._rows + n > self.max_source_rows:
            raise ContractError("directional-change source-row capacity exhausted")
        states = tuple(state.clone() for state in self._states)
        reasons = dict(self._reasons)
        emitted = []
        last_event = last_order = last_row = None
        for index in range(n):
            event_at = int(t[index])
            known_at = int(known[index])
            source_order = int(order[index])
            source_row = int(rows[index])
            is_priced = bool(priced[index])
            ticks = int(price[index]) if is_priced else None
            flag4 = int(flags[index]) & 4 != 0
            unknown = int(side[index]) == 0
            self._work["rows_attempted"] += 1
            reasons["rows"] += 1
            if not history_complete:
                reasons["incomplete_segment"] += 1
            if flag4:
                reasons["flag4"] += 1
            if not is_priced:
                reasons["unpriced"] += 1
            if unknown:
                reasons["unknown_aggressor"] += 1
            point = SourcePoint(event_at, known_at, ticks, source_order, source_row, self.source_key)
            last_event, last_order, last_row = event_at, source_order, source_row
            incomplete = (not history_complete) or flag4 or not is_priced
            if incomplete:
                reasons["resets"] += 1
                self._work["resets_attempted"] += 1
                for state in states:
                    _reset_scale(state, point)
                    self._work["definition_visits_attempted"] += 1
                continue
            reasons["priced_complete"] += 1
            for state in states:
                pending = _apply_scale(state, point)
                self._work["definition_visits_attempted"] += 1
                if pending is None:
                    continue
                self._work["emissions_attempted"] += 1
                if self._emitted + len(emitted) >= self.max_emitted_rows:
                    raise ContractError("directional-change emitted-row capacity exhausted")
                side, extreme, origin, origin_kind = pending
                emitted.append(_emit_swing(
                    instrument_id=self.instrument_id, delay_ns=self.delay_ns, state=state,
                    extreme=extreme, confirmation=point, origin=origin, side=side,
                    origin_kind=origin_kind))
        reasons["slices"] = self._slices + 1
        reasons["emitted_rows"] = self._emitted + len(emitted)
        reasons["confirmed_high"] = sum(state.confirmed_high for state in states)
        reasons["confirmed_low"] = sum(state.confirmed_low for state in states)
        self._states = states
        self._reasons = reasons
        self._rows += n
        self._slices += 1
        self._emitted += len(emitted)
        self._last_event_at = last_event
        self._last_source_order = last_order
        self._last_source_row = last_row
        return tuple(emitted)

    def _record(self):
        return {
            "version": VERSION,
            "unpublished_arithmetic": True,
            "f09_producer_authenticated": False,
            "venue_completeness_certificate": False,
            "history_complete_note": _VENUE,
            "f09_note": _F09,
            "instrument_id": self.instrument_id,
            "source_key": self.source_key,
            "start": self.start,
            "end": self.end,
            "delay_ns": self.delay_ns,
            "max_source_rows": self.max_source_rows,
            "max_emitted_rows": self.max_emitted_rows,
            "rows": self._rows,
            "slices": self._slices,
            "emitted_rows": self._emitted,
            "reason_counts": dict(self._reasons),
            "definitions": tuple({
                "id": state.definition.id,
                "version": state.definition.version,
                "threshold": state.threshold,
                "frozen_at": state.definition.frozen_at,
                "visits": state.visits,
                "resets": state.resets,
                "confirmed_high": state.confirmed_high,
                "confirmed_low": state.confirmed_low,
                "complete": state.complete,
                "incomplete": state.incomplete,
            } for state in self._states),
        }

    def _snapshot(self):
        record = self._record()
        record["provisional"] = tuple({
            "id": state.definition.id,
            "version": state.definition.version,
            "threshold": state.threshold,
            "direction": state.direction,
            "high": _point_record(state.high),
            "low": _point_record(state.low),
            "last": _point_record(state.last),
            "origin": _point_record(state.origin),
            "complete": state.complete,
            "incomplete": state.incomplete,
        } for state in self._states)
        return record


def _pivot_window_records(window, *, definition, interval_ns):
    if any(not bar.final or not bar.coverage_complete or bar.high_ticks is None
            or bar.low_ticks is None for bar in window):
        return (), False
    if any(left.end != right.start for left, right in zip(window, window[1:])):
        return (), False
    center = window[definition.left]
    known = max(bar.published_at for bar in window)
    versions = tuple(bar.version_id for bar in window)
    reference = definition.reference_definition_id
    output = []
    for side, field, best in (("high", "high_ticks", max), ("low", "low_ticks", min)):
        prices = [getattr(bar, field) for bar in window]
        level = getattr(center, field)
        if level != best(prices):
            continue
        equal = [index for index, price in enumerate(prices) if price == level]
        if definition.ties == "strict" and len(equal) > 1:
            continue
        if definition.ties == "earliest" and equal[0] != definition.left:
            continue
        if definition.ties == "latest" and equal[-1] != definition.left:
            continue
        status = "ambiguous_equal_extremum" if definition.ties == "ambiguous" and len(equal) > 1 else "confirmed"
        identity = digest([center.bar_id, side, reference])
        output.append(StreamedPivot(
            True, False, identity, center.instrument, side, level, center.start, center.end,
            known, versions, reference, status, center.start, center.end, versions, known,
            definition.id, definition.left, definition.right, definition.ties, interval_ns,
            definition.version))
    return tuple(output), True


class FinalBarPivotStream:
    """Append-only finalized cadence. Revisions require the as-of pivot_reference replay."""

    def __init__(self, *, instrument, interval_ns, definition,
                 max_bars=_MAX_BARS, max_emitted_rows=_MAX_EMITTED_PIVOTS):
        _nonempty_str(instrument, name="instrument")
        _exact_int(interval_ns, name="interval_ns", minimum=1)
        if type(definition) is not FinalBarPivotDefinition:
            raise ContractError("typed frozen final-bar pivot definition required")
        _exact_int(max_bars, name="max_bars", minimum=1, maximum=_MAX_BARS)
        _exact_int(max_emitted_rows, name="max_emitted_rows", minimum=1, maximum=_MAX_EMITTED_PIVOTS)
        self.instrument = instrument
        self.interval_ns = interval_ns
        self.definition = definition
        self.max_bars = max_bars
        self.max_emitted_rows = max_emitted_rows
        self._window = definition.left + definition.right + 1
        self._bars = deque(maxlen=self._window)
        self._seen = set()
        self._bar_definition = None
        self._last = None
        self._bar_visits = self._valid = self._invalid = self._emitted = 0
        self._failed = False

    def add(self, bar):
        if self._failed:
            raise IntegrityError(_FAILED_PIVOT)
        try:
            return self._add(bar)
        except BaseException:
            self._failed = True
            raise

    def record(self):
        if self._failed:
            raise IntegrityError(_FAILED_PIVOT)
        try:
            return self._record()
        except BaseException:
            self._failed = True
            raise

    def snapshot(self):
        if self._failed:
            raise IntegrityError(_FAILED_PIVOT)
        try:
            payload = self._record()
            payload["deque_length"] = len(self._bars)
            payload["deque_capacity"] = self._window
            payload["last_interval"] = None if self._last is None else (self._last.start, self._last.end)
            return payload
        except BaseException:
            self._failed = True
            raise

    def _add(self, bar):
        if type(bar) is not CausalBar:
            raise ContractError("final-bar pivots require an actual CausalBar")
        if bar.instrument != self.instrument:
            raise ContractError("pivots cannot span a raw contract transition")
        if not bar.final:
            raise ContractError("this streaming path accepts only one final available version per bar")
        if bar.published_at is None:
            raise ContractError("final-bar publication clock is required")
        if bar.published_at < bar.end:
            raise ContractError("publication earlier than the final bar end is rejected")
        if bar.end - bar.start != self.interval_ns:
            raise ContractError("bar width must match the bound cadence")
        if self._bar_definition is None:
            if self.definition.frozen_at > bar.start:
                raise ContractError("pivot rule must be frozen before the supporting window")
            self._bar_definition = bar.definition_version
        elif bar.definition_version != self._bar_definition:
            raise ContractError("pivot cadence cannot change bar definition mid-stream")
        if bar.bar_id in self._seen:
            raise ContractError(
                "duplicate or revised bar identities require the separately replayed as-of "
                "pivot_reference; earlier streamed outputs are preserved and this path will not rewrite them")
        if self._last is not None:
            if bar.start < self._last.start:
                raise ContractError("backward bars are rejected on the append-only pivot path")
            if bar.start < self._last.end:
                raise ContractError("overlapping bars are rejected on the append-only pivot path")
        if self._bar_visits >= self.max_bars:
            raise ContractError("final-bar pivot bar capacity exhausted")
        staged = copy(self._bars)
        staged.append(bar)
        emitted = ()
        valid = None
        if len(staged) == self._window:
            if self.definition.frozen_at > staged[0].start:
                raise ContractError("pivot rule must be frozen before the supporting window")
            emitted, valid = _pivot_window_records(tuple(staged), definition=self.definition,
                                                   interval_ns=self.interval_ns)
            if self._emitted + len(emitted) > self.max_emitted_rows:
                raise ContractError("final-bar pivot emitted-row capacity exhausted")
        self._bars = staged
        self._seen.add(bar.bar_id)
        self._last = bar
        self._bar_visits += 1
        if valid is True:
            self._valid += 1
        elif valid is False:
            self._invalid += 1
        self._emitted += len(emitted)
        return emitted

    def _record(self):
        return {
            "version": VERSION,
            "unpublished_arithmetic": True,
            "f09_producer_authenticated": False,
            "f09_note": _F09,
            "instrument": self.instrument,
            "interval_ns": self.interval_ns,
            "definition_id": self.definition.id,
            "definition_version": self.definition.version,
            "reference_definition_id": self.definition.reference_definition_id,
            "left": self.definition.left,
            "right": self.definition.right,
            "ties": self.definition.ties,
            "bar_visits": self._bar_visits,
            "valid_support_windows": self._valid,
            "invalid_support_windows": self._invalid,
            "emitted_rows": self._emitted,
            "deque_capacity": self._window,
            "max_bars": self.max_bars,
            "max_emitted_rows": self.max_emitted_rows,
        }
