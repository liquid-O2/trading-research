"""Unpublished full-source historical-effort clusters and spatial fields.

This kernel repeats measurements.memory.build_memory cluster connectivity and
raw/decayed spatial arithmetic on one acquired PreparedTradeBatch stream. It is
resource/calculation output only. It does not admit F05, F10 or F11, invent
held inventory or protection, recover missing prints, or replace the existing
visit, markout, protection or retrieval producers.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.auction_flow_windows import PreparedTradeBatch


VERSION = "auction-flow-unpublished-historical-aggression-memory-v1"
_UNPUBLISHED = "unpublished resource/calculation output"
_FAILED = "a failed historical-aggression accumulator cannot publish or resume partial state"
_SEALED = "a sealed historical-aggression window cannot accept further source rows"
_PROJECTION = "the actual unreleased PreparedTradeBatch and proper slice bounds are required"
_MAPPING = "source identity, window, delay or retained order disagrees"
_VISIT = ("visit decay is unsupported in this unpublished kernel; "
          "the actual visit producer is a separate mechanism")
_VENUE = "history_complete is a controller segment mask, not a venue completeness certificate."
_QUANTITY = "bounded equal exact arrays of eligible reported-side trades required"
_CLOCK_END = 2 ** 63 - 1_000_000_000
_BATCH_ROWS = 65_536
_MAX_INPUT = 50_000_000
_MAX_SELECTED = 2_000_000
_MAX_CLUSTERS = 1_000_000
_MAX_CELLS = 65_536
_MAX_RADIUS = 64
_MAX_RESULT_BYTES = 512 * 1024 * 1024
_DEFAULT_SELECTED = 500_000
_DEFAULT_CLUSTERS = 100_000
_DEFAULT_RESULT_BYTES = 64 * 1024 * 1024
_CHANNEL_INDEX = {1: 0, -1: 1, 0: 2}
_IDENTITY_KEYS = (
    "version", "unpublished_arithmetic", "publication_status", "output_kind",
    "admitted_for_serving", "f05_admitted", "f10_admitted", "f11_admitted",
    "instrument_id", "source_key", "event_start_ns", "event_end_ns",
    "known_at_ns", "source_delay_ns", "definition", "definition_id",
    "clusters", "field_cells", "overflow", "raw_mass", "decayed_mass",
    "decay_clock", "decay_clock_convention", "history_complete", "order_exact",
    "input_prints", "input_volume", "selected_prints", "selected_volume",
    "excluded_prints", "excluded_volume", "unknown_side_prints", "unknown_side_volume",
    "unpriced_prints", "unpriced_volume", "older_than_max_age_prints",
    "older_than_max_age_volume", "below_filter_prints", "below_filter_volume",
    "flag_prints", "flag4_prints", "first_print", "last_print", "empty_observed_window",
)
_MEMBER_CONTENT = (
    "source_key", "source_row", "source_order", "event_at", "known_at_ns",
    "price", "size", "raw_flags", "raw_action", "raw_side", "side",
)


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


def _row_index(value):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise IntegrityError(_PROJECTION)
    return int(value)


def _array_int(value, *, name):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ContractError(f"{name} must be an exact integer")
    return int(value)


def _source_address(value, *, name):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ContractError(f"{name} must be an exact nonnegative source address")
    if isinstance(value, np.unsignedinteger):
        return int(value)
    result = int(value)
    if result < 0:
        raise ContractError(f"{name} must be an exact nonnegative source address")
    return result


def _clock_pair(start, end):
    _exact_int(start, name="start_ns", minimum=0, maximum=_CLOCK_END - 1)
    _exact_int(end, name="end_ns", minimum=1, maximum=_CLOCK_END - 1)
    if not start < end:
        raise ContractError("exact half-open event interval required")
    return start, end


def _capacity(value, *, name, minimum, maximum):
    return _exact_int(value, name=name, minimum=minimum, maximum=maximum)


def _size_ok_array(size, *, minimum_size, strict_size):
    return size > minimum_size if strict_size else size >= minimum_size


def _channel(side):
    return _CHANNEL_INDEX[side]


def _empty_channels(zero):
    return [zero, zero, zero]


def _spatial_weight(price, support, radius):
    denominator = (radius + 1) ** 2
    return Fraction(radius + 1 - abs(support - price), denominator)


def _decay_weight(age, *, scale, kernel):
    if kernel == "box":
        return int(age <= scale)
    return 2 ** (-float(Fraction(age, scale)))


def _exact_sum(values):
    if values is None or len(values) == 0:
        return 0
    return sum(int(value) for value in values)


def _identity_record(report):
    return {key: report[key] for key in _IDENTITY_KEYS}


def _member_content(member):
    return tuple(member[key] for key in _MEMBER_CONTENT)


def _arrow_all_equal(column, value):
    import pyarrow as pa
    import pyarrow.compute as pc

    if column.null_count:
        return False
    return bool(pc.all(pc.equal(pc.cast(column, pa.string()), value)).as_py())


def _expected_sides(raw_side):
    import pyarrow as pa
    import pyarrow.compute as pc

    text = pc.cast(raw_side, pa.string())
    expected = pc.if_else(pc.equal(text, "B"), 1, pc.if_else(pc.equal(text, "A"), -1, 0))
    return pc.fill_null(expected, 0).to_numpy(zero_copy_only=False)


@dataclass(frozen=True)
class AuctionFlowMemoryDefinition:
    """Frozen whole-print selection, connectivity and spatial/decay recipe.

    Radii, size cutoffs and decay scales stay caller-declared. This object does
    not choose a winning threshold or infer participant identity. Visit decay is
    rejected because the visit producer is a separate existing mechanism.
    """

    version: str
    minimum_size: int = 1
    strict_size: bool = False
    price_radius_ticks: int = 0
    time_radius_ns: int = 0
    max_age_ns: int = 86_400_000_000_000
    spatial_grid: tuple = ()
    spatial_kernel: str = "point"
    spatial_radius_ticks: int = 1
    decay_clock: str = "time"
    decay_scale: int | Fraction = Fraction(1)
    decay_kernel: str = "half_life"
    frozen_at: int = 0

    def __post_init__(self):
        bounded_name(self.version)
        positive_limit(self.minimum_size)
        positive_limit(self.max_age_ns)
        timestamp(self.frozen_at)
        if type(self.strict_size) is not bool:
            raise ContractError("memory requires an explicit size-threshold convention")
        for name, value, limit in (("price_radius_ticks", self.price_radius_ticks, _MAX_RADIUS),
                                   ("time_radius_ns", self.time_radius_ns, None),
                                   ("spatial_radius_ticks", self.spatial_radius_ticks, _MAX_RADIUS)):
            if type(value) is not int or value < 0:
                raise ContractError("memory radii must be exact nonnegative units")
            if limit is not None and value > limit:
                raise ContractError("memory neighbor or spatial radius exceeds its finite bound")
        bounded_rows(self.spatial_grid, _MAX_CELLS, name="memory spatial grid")
        if (type(self.spatial_grid) is not tuple
                or tuple(sorted(set(self.spatial_grid))) != self.spatial_grid
                or any(type(price) is not int for price in self.spatial_grid)):
            raise ContractError("memory requires an immutable increasing exact grid")
        if self.spatial_grid and any(b - a != 1 for a, b in zip(self.spatial_grid, self.spatial_grid[1:])):
            raise ContractError("memory triangular grid is a contiguous raw-tick grid")
        if self.decay_clock == "visits":
            raise DependencyUnavailable(_VISIT)
        if (self.spatial_kernel not in ("point", "triangular")
                or self.decay_clock not in ("time", "volume")
                or self.decay_kernel not in ("half_life", "box")
                or type(self.decay_scale) not in (int, Fraction)
                or self.decay_scale <= 0):
            raise ContractError("memory requires an explicit supported whole-print metric and decay recipe")

    @property
    def id(self):
        return digest(self)


class AuctionFlowMemoryWindow:
    """Closed one-source window for unpublished historical-aggression arithmetic."""

    def __init__(self, *, definition, instrument_id, source_key, start_ns, end_ns,
                 latency_ns=250_000_000, max_input_rows=_MAX_INPUT,
                 max_selected_prints=_DEFAULT_SELECTED, max_clusters=_DEFAULT_CLUSTERS,
                 max_cells=_MAX_CELLS, max_result_bytes=_DEFAULT_RESULT_BYTES):
        if type(definition) is not AuctionFlowMemoryDefinition:
            raise ContractError("typed frozen historical-aggression definition required")
        definition.__post_init__()
        _exact_int(instrument_id, name="instrument_id", minimum=1)
        bounded_name(source_key)
        start_ns, end_ns = _clock_pair(start_ns, end_ns)
        _exact_int(latency_ns, name="latency_ns", minimum=0, maximum=1_000_000_000)
        max_input_rows = _capacity(max_input_rows, name="max_input_rows", minimum=1, maximum=_MAX_INPUT)
        max_selected_prints = _capacity(max_selected_prints, name="max_selected_prints",
                                        minimum=1, maximum=_MAX_SELECTED)
        max_clusters = _capacity(max_clusters, name="max_clusters", minimum=1, maximum=_MAX_CLUSTERS)
        max_cells = _capacity(max_cells, name="max_cells", minimum=1, maximum=_MAX_CELLS)
        max_result_bytes = _capacity(max_result_bytes, name="max_result_bytes",
                                     minimum=1, maximum=_MAX_RESULT_BYTES)
        if len(definition.spatial_grid) > max_cells:
            raise ContractError("memory spatial grid exceeds the window cell capacity")
        if 2 * definition.spatial_radius_ticks + 1 > max_cells:
            raise ContractError("memory kernel support exceeds its spatial capacity")
        if definition.frozen_at > start_ns:
            raise ContractError("memory rule must be frozen before the measured window")
        self.definition = definition
        self.instrument_id = instrument_id
        self.source_key = source_key
        self.start = start_ns
        self.end = end_ns
        self.delay = latency_ns
        self.max_input_rows = max_input_rows
        self.max_selected_prints = max_selected_prints
        self.max_clusters = max_clusters
        self.max_cells = max_cells
        self.max_result_bytes = max_result_bytes
        self._definition_id = definition.id
        self._failed = False
        self._closed = False
        self._report = None
        self._last_event_at = self._last_source_order = self._last_source_row = None
        self._first = self._last = None
        self._slices = 0
        self.input_prints = 0
        self.input_volume = 0
        self.selected_prints = 0
        self.selected_volume = 0
        self.unknown_side_prints = 0
        self.unknown_side_volume = 0
        self.unpriced_prints = 0
        self.unpriced_volume = 0
        self.older_than_max_age_prints = 0
        self.older_than_max_age_volume = 0
        self.below_filter_prints = 0
        self.below_filter_volume = 0
        self.flag_prints = 0
        self.flag4_prints = 0
        self.history_complete = True
        self.order_exact = True
        self.price_lookups = 0
        self.union_attempts = 0
        self.union_merges = 0
        self.unions = 0
        self.visited_selected_prints = 0
        self.kernel_operations = 0
        self.volume_groups = 0
        self.cluster_count = 0
        self.cluster_inspected = 0
        self._parent = []
        self._latest = {}
        self._sel_t = []
        self._sel_known = []
        self._sel_price = []
        self._sel_size = []
        self._sel_side = []
        self._sel_order = []
        self._sel_row = []
        self._sel_flags = []
        self._sel_action = []
        self._sel_raw_side = []
        self._sel_group_end = []
        self._volume_total = 0
        self._pending_time = None
        self._pending_selected = []

    def add_prepared(self, prepared, left=0, right=None, *, history_complete=True):
        if self._failed:
            raise IntegrityError(_FAILED)
        if self._closed:
            raise IntegrityError(_SEALED)
        try:
            self._add_prepared(prepared, left, right, history_complete=history_complete)
        except BaseException:
            self._failed = True
            raise

    def finish(self):
        if self._failed:
            raise IntegrityError(_FAILED)
        if self._closed:
            return deepcopy(self._report)
        try:
            report = self._finish()
            self._report = report
            self._closed = True
            return deepcopy(report)
        except BaseException:
            self._failed = True
            raise

    def _add_prepared(self, prepared, left, right, *, history_complete):
        import numpy as np

        _exact_bool(history_complete, name="history_complete")
        if type(prepared) is not PreparedTradeBatch or prepared.released:
            raise IntegrityError(_PROJECTION)
        left = _row_index(left)
        right = len(prepared) if right is None else _row_index(right)
        if not 0 <= left <= right <= len(prepared):
            raise IntegrityError(_PROJECTION)
        width = right - left
        if width > _BATCH_ROWS:
            raise ContractError("prepared historical-aggression slices cannot exceed 65536 rows")
        if not history_complete:
            self.history_complete = False
        self._slices += 1
        if width == 0:
            return
        values = prepared.values
        required = ("t", "known_at_ns", "price", "price_valid", "size", "side",
                    "instrument_id", "source_order", "source_row", "raw_flags")
        if any(name not in values for name in required):
            raise IntegrityError(_PROJECTION)
        view = {name: values[name][left:right] for name in required}
        if any(column.ndim != 1 or column.dtype.kind not in "iu" or len(column) != width
                for column in view.values()):
            raise IntegrityError(_PROJECTION)
        t, known, price, valid, size, side, instrument, order, rows, flags = (
            view[name] for name in required)
        if (np.any(instrument != self.instrument_id) or np.any(t < self.start) or np.any(t >= self.end)
                or np.any(known != t + self.delay) or np.any(t[1:] < t[:-1])
                or np.any(order[1:] <= order[:-1]) or np.any(rows[1:] <= rows[:-1])):
            raise IntegrityError(_MAPPING)
        if (np.any(size <= 0) or np.any(size >= 2 ** 32 - 1)):
            raise ContractError(_QUANTITY)
        if (np.any(~np.isin(valid, (0, 1))) or np.any(flags < 0) or np.any(flags > 255)
                or np.any(~np.isin(side, (-1, 0, 1)))):
            raise IntegrityError("trade validity, side or raw_flags left the admitted domain")
        if np.any(flags & 32):
            raise IntegrityError(_MAPPING)
        priced = valid != 0
        if np.any(price[priced] <= 0) or np.any(price[priced] >= 2 ** 53):
            raise ContractError("valid raw prices must retain positive exact tick coordinates")
        first_event = _array_int(t[0], name="t")
        first_order = _source_address(order[0], name="source_order")
        first_row = _source_address(rows[0], name="source_row")
        if self._last_event_at is not None and (
                first_event < self._last_event_at or first_order <= self._last_source_order
                or first_row <= self._last_source_row):
            raise IntegrityError(_MAPPING)
        if prepared._source_key is None or prepared._raw_action is None:
            raise IntegrityError(_PROJECTION)
        keys = prepared._source_key.slice(left, width)
        actions = prepared._raw_action.slice(left, width)
        raw_sides = prepared._raw_side.slice(left, width)
        if not _arrow_all_equal(keys, self.source_key):
            raise IntegrityError("mixed acquired source or wrong source_key")
        if not _arrow_all_equal(actions, "T"):
            raise IntegrityError(_MAPPING)
        if not np.array_equal(_expected_sides(raw_sides), np.asarray(side)):
            raise IntegrityError(_MAPPING)
        definition = self.definition
        age_ok = (self.end - t) <= definition.max_age_ns
        size_ok = _size_ok_array(size, minimum_size=definition.minimum_size,
                                 strict_size=definition.strict_size)
        chosen = priced & age_ok & size_ok
        selected_n = int(np.count_nonzero(chosen))
        overflow_input = self.input_prints + width > self.max_input_rows
        overflow_selected = self.selected_prints + selected_n > self.max_selected_prints
        self._charge_arrays(t, size, side, valid, flags, size_ok)
        if overflow_input or overflow_selected:
            self.selected_prints += selected_n
            self.selected_volume += _exact_sum(size[chosen])
            if overflow_input:
                raise ContractError("memory input-row capacity exhausted")
            raise ContractError("memory selected-print capacity exhausted")
        volume_clock = definition.decay_clock == "volume"
        radius = definition.price_radius_ticks
        time_radius = definition.time_radius_ns
        last = width - 1
        if self._first is None:
            self._first = self._lineage_at(
                prepared, left, 0, t, known, order, rows, flags, side)
        self._last = self._lineage_at(
            prepared, left, last, t, known, order, rows, flags, side)
        self._last_event_at = _array_int(t[last], name="t")
        self._last_source_order = _source_address(order[last], name="source_order")
        self._last_source_row = _source_address(rows[last], name="source_row")
        for i in range(width):
            event = _array_int(t[i], name="t")
            quantity = _array_int(size[i], name="size")
            if volume_clock:
                self._advance_volume_group(event)
            if chosen[i]:
                index = self._retain_selected(
                    prepared, left, i, t, known, price, size, side, order, rows, flags)
                if volume_clock:
                    self._pending_selected.append(index)
                sign = self._sel_side[index]
                ticks = self._sel_price[index]
                for support in range(ticks - radius, ticks + radius + 1):
                    self.price_lookups += 1
                    latest = self._latest.get((sign, support))
                    if latest is None:
                        continue
                    other, other_at = latest
                    if event - other_at <= time_radius:
                        self._union(index, other)
                self._latest[(sign, ticks)] = (index, event)
            if volume_clock:
                self._volume_total += quantity

    def _lineage_at(self, prepared, left, i, t, known, order, rows, flags, side):
        index = left + i
        return {
            "event_at": _array_int(t[i], name="t"),
            "known_at_ns": _array_int(known[i], name="known_at_ns"),
            "source_order": _source_address(order[i], name="source_order"),
            "source_row": _source_address(rows[i], name="source_row"),
            "source_key": prepared.source_key(index),
            "raw_flags": _array_int(flags[i], name="raw_flags"),
            "raw_action": prepared._raw_action[index].as_py(),
            "raw_side": prepared._raw_side[index].as_py(),
            "side": _array_int(side[i], name="side"),
        }

    def _retain_selected(self, prepared, left, i, t, known, price, size, side, order, rows, flags):
        index = len(self._sel_t)
        if index != self.visited_selected_prints:
            raise IntegrityError("selected membership drifted from its visited-print counter")
        quantity = _array_int(size[i], name="size")
        self._parent.append(index)
        self._sel_t.append(_array_int(t[i], name="t"))
        self._sel_known.append(_array_int(known[i], name="known_at_ns"))
        self._sel_price.append(_array_int(price[i], name="price"))
        self._sel_size.append(quantity)
        self._sel_side.append(_array_int(side[i], name="side"))
        self._sel_order.append(_source_address(order[i], name="source_order"))
        self._sel_row.append(_source_address(rows[i], name="source_row"))
        self._sel_flags.append(_array_int(flags[i], name="raw_flags"))
        self._sel_action.append(prepared._raw_action[left + i].as_py())
        self._sel_raw_side.append(prepared._raw_side[left + i].as_py())
        if self.definition.decay_clock == "volume":
            self._sel_group_end.append(None)
        self.visited_selected_prints += 1
        self.selected_prints += 1
        self.selected_volume += quantity
        return index

    def _advance_volume_group(self, event):
        if self._pending_time is None:
            self._pending_time = event
            return
        if event == self._pending_time:
            return
        self._close_volume_group()
        self._pending_time = event

    def _close_volume_group(self):
        if self._pending_time is None:
            return
        for index in self._pending_selected:
            self._sel_group_end[index] = self._volume_total
        self.volume_groups += 1
        self._pending_selected = []
        self._pending_time = None

    def _charge_arrays(self, t, size, side, valid, flags, size_ok):
        import numpy as np

        width = len(t)
        unknown = side == 0
        unpriced = valid == 0
        older = (self.end - t) > self.definition.max_age_ns
        flagged = flags != 0
        flag4 = (flags & 4) != 0
        self.input_prints += width
        self.input_volume += _exact_sum(size)
        self.unknown_side_prints += int(np.count_nonzero(unknown))
        self.unknown_side_volume += _exact_sum(size[unknown])
        self.unpriced_prints += int(np.count_nonzero(unpriced))
        self.unpriced_volume += _exact_sum(size[unpriced])
        self.older_than_max_age_prints += int(np.count_nonzero(older))
        self.older_than_max_age_volume += _exact_sum(size[older])
        self.below_filter_prints += int(np.count_nonzero(~size_ok))
        self.below_filter_volume += _exact_sum(size[~size_ok])
        self.flag_prints += int(np.count_nonzero(flagged))
        self.flag4_prints += int(np.count_nonzero(flag4))
        if np.any(flag4):
            self.history_complete = False

    def _root(self, index):
        parent = self._parent
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def _union(self, left, right):
        self.union_attempts += 1
        self.unions += 1
        a, b = self._root(left), self._root(right)
        if a != b:
            self._parent[max(a, b)] = min(a, b)
            self.union_merges += 1

    def _group_selected(self, n):
        components = {}
        inspected = 0
        for index in range(n):
            inspected += 1
            root = self._root(index)
            members = components.get(root)
            if members is None:
                if len(components) >= self.max_clusters:
                    self.cluster_count = len(components) + 1
                    self.cluster_inspected = inspected
                    raise ContractError("memory cluster capacity exhausted")
                components[root] = [index]
            else:
                members.append(index)
        self.cluster_count = len(components)
        self.cluster_inspected = inspected
        return components

    def _build_cluster(self, members):
        quantity = 0
        priced = 0
        low = high = None
        first_at = last_at = None
        records = []
        for index in members:
            size = self._sel_size[index]
            ticks = self._sel_price[index]
            event = self._sel_t[index]
            quantity += size
            priced += int(ticks) * int(size)
            low = ticks if low is None or ticks < low else low
            high = ticks if high is None or ticks > high else high
            first_at = event if first_at is None or event < first_at else first_at
            last_at = event if last_at is None or event > last_at else last_at
            records.append({
                "source_key": self.source_key,
                "source_row": self._sel_row[index],
                "source_order": self._sel_order[index],
                "event_at": event,
                "known_at_ns": self._sel_known[index],
                "price": ticks,
                "size": size,
                "raw_flags": self._sel_flags[index],
                "raw_action": self._sel_action[index],
                "raw_side": self._sel_raw_side[index],
                "side": self._sel_side[index],
            })
        records.sort(key=lambda row: (row["source_key"], row["source_row"], row["source_order"]))
        content = tuple(_member_content(row) for row in records)
        return {
            "id": digest((self._definition_id, content)),
            "members": tuple(records),
            "side": self._sel_side[members[0]],
            "center_ticks": Fraction(priced, quantity),
            "low_ticks": low,
            "high_ticks": high,
            "first_at": first_at,
            "last_at": last_at,
            "gross": quantity,
            "raw_count": len(members),
        }

    def _accumulate_bytes(self, acc, value):
        acc += len(canonical_json(value))
        if acc > self.max_result_bytes:
            raise ContractError("memory retained result bytes exhausted")
        return acc

    def _finish(self):
        definition = self.definition
        n = len(self._sel_t)
        if n != self.selected_prints or n != self.visited_selected_prints:
            raise IntegrityError("selected print counters disagree with staged membership")
        if definition.decay_clock == "volume":
            self._close_volume_group()
            if len(self._sel_group_end) != n:
                raise IntegrityError("volume group-end staging disagrees with selected membership")
            if any(end is None for end in self._sel_group_end):
                raise IntegrityError("a selected print is missing its timestamp-group volume total")
            if self._volume_total != self.input_volume:
                raise IntegrityError("volume accumulation disagrees with charged input volume")
        volume_available = definition.decay_clock != "volume" or (
            self.history_complete and self.order_exact)
        components = self._group_selected(n)
        clusters = [self._build_cluster(members) for members in components.values()]
        clusters.sort(key=lambda cluster: (cluster["first_at"], cluster["low_ticks"], cluster["id"]))
        raw = _empty_channels(0)
        decayed = _empty_channels(0)
        cells = {price: [_empty_channels(Fraction(0)), _empty_channels(0)]
                 for price in definition.spatial_grid}
        overflow = [_empty_channels(Fraction(0)), _empty_channels(0)]
        radius = 0 if definition.spatial_kernel == "point" else definition.spatial_radius_ticks
        for index in range(n):
            channel = _channel(self._sel_side[index])
            size = self._sel_size[index]
            ticks = self._sel_price[index]
            event = self._sel_t[index]
            raw[channel] += size
            if definition.decay_clock == "time":
                age = self.end - event
            elif volume_available:
                age = self._volume_total - self._sel_group_end[index]
            else:
                age = None
            weight = None if age is None else _decay_weight(
                age, scale=definition.decay_scale, kernel=definition.decay_kernel)
            if weight is None:
                decayed[channel] = None
            elif decayed[channel] is not None:
                decayed[channel] += size * weight
            for support in range(ticks - radius, ticks + radius + 1):
                self.kernel_operations += 1
                spatial = _spatial_weight(ticks, support, radius)
                target = cells[support] if support in cells else overflow
                target[0][channel] += size * spatial
                if weight is None:
                    target[1][channel] = None
                elif target[1][channel] is not None:
                    target[1][channel] += size * spatial * weight
        if any(sum((cell[0][i] for cell in cells.values()), Fraction(0)) + overflow[0][i] != raw[i]
               for i in range(3)):
            raise IntegrityError("memory spatial kernel failed raw-mass conservation")
        if definition.decay_clock == "time":
            convention = "time_age = event_end_ns - event_at; inclusive max_age uses the same cut"
        else:
            convention = ("volume_age = final eligible volume minus the end-of-timestamp-group "
                          "cumulative total; same-time ties do not contribute")
        field_cells = tuple((price, tuple(values[0]), tuple(values[1]))
                            for price, values in cells.items())
        overflow_record = (tuple(overflow[0]), tuple(overflow[1]))
        acc = 0
        for cluster in clusters:
            acc = self._accumulate_bytes(acc, cluster)
        acc = self._accumulate_bytes(acc, field_cells)
        acc = self._accumulate_bytes(acc, overflow_record)
        report = {
            "version": VERSION,
            "unpublished_arithmetic": True,
            "publication_status": "unpublished",
            "output_kind": _UNPUBLISHED,
            "admitted_for_serving": False,
            "f05_admitted": False,
            "f10_admitted": False,
            "f11_admitted": False,
            "history_complete_note": _VENUE,
            "instrument_id": self.instrument_id,
            "source_key": self.source_key,
            "event_start_ns": self.start,
            "event_end_ns": self.end,
            "known_at_ns": self.end + self.delay,
            "source_delay_ns": self.delay,
            "definition": {
                "version": definition.version,
                "minimum_size": definition.minimum_size,
                "strict_size": definition.strict_size,
                "price_radius_ticks": definition.price_radius_ticks,
                "time_radius_ns": definition.time_radius_ns,
                "max_age_ns": definition.max_age_ns,
                "spatial_grid": definition.spatial_grid,
                "spatial_kernel": definition.spatial_kernel,
                "spatial_radius_ticks": definition.spatial_radius_ticks,
                "decay_clock": definition.decay_clock,
                "decay_scale": definition.decay_scale,
                "decay_kernel": definition.decay_kernel,
                "frozen_at": definition.frozen_at,
                "id": self._definition_id,
            },
            "definition_id": self._definition_id,
            "clusters": tuple(clusters),
            "field_cells": field_cells,
            "overflow": overflow_record,
            "raw_mass": tuple(raw),
            "decayed_mass": tuple(decayed),
            "decay_clock": definition.decay_clock,
            "decay_clock_convention": convention,
            "history_complete": self.history_complete,
            "order_exact": self.order_exact,
            "input_prints": self.input_prints,
            "input_volume": self.input_volume,
            "selected_prints": self.selected_prints,
            "selected_volume": self.selected_volume,
            "excluded_prints": self.input_prints - self.selected_prints,
            "excluded_volume": self.input_volume - self.selected_volume,
            "unknown_side_prints": self.unknown_side_prints,
            "unknown_side_volume": self.unknown_side_volume,
            "unpriced_prints": self.unpriced_prints,
            "unpriced_volume": self.unpriced_volume,
            "older_than_max_age_prints": self.older_than_max_age_prints,
            "older_than_max_age_volume": self.older_than_max_age_volume,
            "below_filter_prints": self.below_filter_prints,
            "below_filter_volume": self.below_filter_volume,
            "flag_prints": self.flag_prints,
            "flag4_prints": self.flag4_prints,
            "first_print": None if self._first is None else dict(self._first),
            "last_print": None if self._last is None else dict(self._last),
            "empty_observed_window": self.history_complete and self.input_prints == 0,
            "slices": self._slices,
            "work": (
                ("visited_selected_prints", self.visited_selected_prints),
                ("price_lookups", self.price_lookups),
                ("union_attempts", self.union_attempts),
                ("union_merges", self.union_merges),
                ("unions", self.unions),
                ("kernel_operations", self.kernel_operations),
                ("volume_groups", self.volume_groups),
                ("cluster_inspected", self.cluster_inspected),
            ),
        }
        report["id"] = digest(_identity_record(report))
        encoded = canonical_json(report)
        if len(encoded) > self.max_result_bytes:
            raise ContractError("memory retained result bytes exhausted")
        return report
