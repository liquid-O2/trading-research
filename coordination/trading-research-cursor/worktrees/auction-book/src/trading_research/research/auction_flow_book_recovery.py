"""Reported local BBO reinitialization candidate after a completed ordinary quote.

This is an unpublished validation candidate. It asks whether the provider-reported
MBP-1 top-of-book prices and aggregate sizes may restart current displayed-BBO
trust from a clean completed ordinary A/M/C record after bit-4, clear, or
unknown-action invalidation. LAST is required for that restart. SNAPSHOT alone
does not complete an event. A later local restart does not repair cumulative
observed-flow history and does not certify venue sequence or exchange order.

The accepted projection is unchanged. Input buffers are never mutated. Only the
derived candidate book_valid values are replaced on a newly returned table that
keeps the original schema.
"""
from __future__ import annotations

import hashlib

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import canonical_json
from trading_research.research.auction_flow_quotes import REQUIRED


VERSION = "auction-flow-reported-bbo-reinitialization-candidate-v1"
CARRY_VERSION = "auction-flow-reported-bbo-reinitialization-carry-v1"
POLICY = "reported_bbo_reinitialize_on_completed_ordinary_full_bbo"
SOURCE_ASSUMPTION_NAME = "provider_reported_mbp1_bbo_reinitialization"
SOURCE_ASSUMPTION = (
    "MBP-1 carries the complete reported top bid/ask prices and aggregate sizes "
    "with each top-of-book update. After bit-4, clear, or unknown-action "
    "invalidation, this candidate restarts current reported-BBO trust only on a "
    "later A/M/C record with bit 4 unset, SNAPSHOT unset, LAST set, and a valid "
    "full two-sided BBO in the admitted quarter-tick/size domain. Snapshot replay "
    "or a later local restart does not certify a completed venue event, repair "
    "prefix flow history, or restore exchange order."
)
BATCH_ROWS = 65_536
MAX_ROWS = 50_000_000
MAX_EPISODES = 50_000
MAX_CARRY_BYTES = 32 * 1024 * 1024
MAX_SOURCE_KEY = 4096
MAX_ACTION = 64
_ADDRESS_FIELDS = ("source_key", "source_row", "source_order", "t", "known_at",
                   "raw_flags", "raw_action")
_EPISODE_FIELDS = ("episode_index", "invalidation", "recovery", "unresolved",
                   "provider_flagged_records")
_KNOWN = ("A", "M", "C", "R", "T", "N")
_UPDATES = ("A", "M", "C")
_NUMERIC = ("t", "source_order", "instrument_id", "bid", "ask", "bid_size",
            "ask_size", "book_valid", "snapshot", "raw_flags", "known_at_ns",
            "source_row")
_CARRY_PAYLOAD_KEYS = (
    "version", "completed", "policy", "policy_version", "instrument_id",
    "source_key", "latency_ns", "event_start_ns", "event_end_ns", "next_start_ns",
    "prefix_start_ns", "maximum_rows", "maximum_episodes", "rows",
    "candidate_valid_rows", "candidate_invalid_rows", "changed_book_valid_rows",
    "original_valid_rows", "provider_flagged_records", "clear_rows",
    "unknown_action_rows", "blocked", "observed_history_complete",
    "cumulative_coverage_complete", "first_unresolved_invalidation",
    "last_source_address", "last_t", "last_source_order", "last_source_row",
    "episodes", "previous_continuation_sha256",
)
_CARRY_KEYS = frozenset(_CARRY_PAYLOAD_KEYS) | {"sha256"}
_COUNT_NAMES = ("rows", "candidate_valid_rows", "candidate_invalid_rows",
                "changed_book_valid_rows", "original_valid_rows",
                "provider_flagged_records", "clear_rows", "unknown_action_rows")
_FAILED = "a failed reported-BBO reinitialization cannot publish or resume"
_PROJECTION = "open reported-BBO reinitialization and complete source-bound projection required"
_IDENTITY = "reported-BBO identity, information cut or retained order disagrees"
_CARRY = "reported-BBO continuation is changed, nonadjacent, uncompleted or from another source"
_NULL = "required quote coordinate or clock is null"
_TRUST = "trusted projected BBO is outside the exact admitted domain"
_SIZE_LIMIT = 2**32 - 1
_PRICE_LIMIT = 2**53


def _combine(array):
    return array.combine_chunks() if hasattr(array, "combine_chunks") else array


def _text(value, *, limit=MAX_SOURCE_KEY):
    if isinstance(value, bytes):
        if len(value) > limit:
            raise IntegrityError(_IDENTITY)
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IntegrityError(_IDENTITY) from exc
    if type(value) is not str or not value or len(value) > limit:
        raise IntegrityError(_IDENTITY)
    return value


def _action_text(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        if len(value) > MAX_ACTION:
            raise IntegrityError(_IDENTITY)
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IntegrityError(_IDENTITY) from exc
    if type(value) is not str or len(value) > MAX_ACTION:
        raise IntegrityError(_IDENTITY)
    return value


def _clone_address(value):
    return {name: value[name] for name in _ADDRESS_FIELDS}


def _clone_episode(value):
    return {
        "episode_index": int(value["episode_index"]),
        "invalidation": _clone_address(value["invalidation"]),
        "recovery": None if value["recovery"] is None else _clone_address(value["recovery"]),
        "unresolved": bool(value["unresolved"]),
        "provider_flagged_records": int(value["provider_flagged_records"]),
    }


def _require_categorical(array, *, allow_null):
    import pyarrow as pa

    array = _combine(array)
    typ = array.type
    value_type = typ.value_type if pa.types.is_dictionary(typ) else typ
    if not (pa.types.is_string(value_type) or pa.types.is_large_string(value_type)
            or pa.types.is_binary(value_type) or pa.types.is_large_binary(value_type)):
        raise IntegrityError(_IDENTITY)
    if array.null_count and not allow_null:
        raise IntegrityError(_NULL)
    return array


def _as_text_array(array):
    import pyarrow as pa
    import pyarrow.compute as pc

    return pc.cast(_combine(array), pa.string())


def _invalidation_address(address):
    return bool(address["raw_flags"] & 4) or address["raw_action"] == "R" or address["raw_action"] not in _KNOWN


def _recovery_address(address):
    flags = address["raw_flags"]
    return (address["raw_action"] in _UPDATES and not (flags & 4)
            and not (flags & 32) and bool(flags & 128))


def _address_before(left, right):
    return (left["t"] <= right["t"] and left["source_order"] < right["source_order"]
            and left["source_row"] < right["source_row"])


def _address_at_or_before(left, right):
    return (left["t"] <= right["t"] and left["source_order"] <= right["source_order"]
            and left["source_row"] <= right["source_row"])


def _parse_address(value, *, delay, before_ns, after_ns):
    if (not isinstance(value, dict) or set(value) != set(_ADDRESS_FIELDS)
            or any(type(value[name]) is not int for name in
                   ("source_row", "source_order", "t", "known_at", "raw_flags"))):
        raise IntegrityError(_CARRY)
    key = value["source_key"]
    action = value["raw_action"]
    if (type(key) is not str or not key or len(key) > MAX_SOURCE_KEY
            or (action is not None and (type(action) is not str or len(action) > MAX_ACTION))):
        raise IntegrityError(_CARRY)
    parsed = {name: value[name] for name in ("source_row", "source_order", "t", "known_at", "raw_flags")}
    if (parsed["source_row"] < 0 or parsed["source_order"] < 0
            or not 0 <= parsed["raw_flags"] <= 255
            or parsed["known_at"] != parsed["t"] + delay
            or not after_ns <= parsed["t"] < before_ns):
        raise IntegrityError(_CARRY)
    return {"source_key": key, "raw_action": action, **parsed}


def _parse_episode(value, *, delay, before_ns, after_ns):
    if (not isinstance(value, dict) or set(value) != set(_EPISODE_FIELDS)
            or type(value["episode_index"]) is not int or value["episode_index"] < 1
            or type(value["unresolved"]) is not bool
            or type(value["provider_flagged_records"]) is not int
            or value["provider_flagged_records"] < 0):
        raise IntegrityError(_CARRY)
    invalidation = _parse_address(value["invalidation"], delay=delay,
                                  before_ns=before_ns, after_ns=after_ns)
    if not _invalidation_address(invalidation):
        raise IntegrityError(_CARRY)
    if (invalidation["raw_flags"] & 4) and value["provider_flagged_records"] < 1:
        raise IntegrityError(_CARRY)
    if value["unresolved"]:
        if value["recovery"] is not None:
            raise IntegrityError(_CARRY)
        recovery = None
    else:
        recovery = _parse_address(value["recovery"], delay=delay,
                                  before_ns=before_ns, after_ns=after_ns)
        if not _recovery_address(recovery) or not _address_before(invalidation, recovery):
            raise IntegrityError(_CARRY)
    return {
        "episode_index": value["episode_index"],
        "invalidation": invalidation,
        "recovery": recovery,
        "unresolved": value["unresolved"],
        "provider_flagged_records": value["provider_flagged_records"],
    }


def _bound_carry(carry, *, maximum_episodes):
    if type(carry) is not dict:
        raise ContractError("completed reported-BBO continuation record required")
    if set(carry) != _CARRY_KEYS:
        raise IntegrityError(_CARRY)
    episodes = carry.get("episodes")
    if (type(episodes) not in (list, tuple) or len(episodes) > min(maximum_episodes, MAX_EPISODES)
            or type(carry.get("source_key")) not in (str, type(None))
            or (isinstance(carry.get("source_key"), str)
                and not (0 < len(carry["source_key"]) <= MAX_SOURCE_KEY))):
        raise IntegrityError(_CARRY)
    weight = 1024 + (0 if carry["source_key"] is None else len(carry["source_key"]))
    weight += len(episodes) * 384
    if weight > MAX_CARRY_BYTES:
        raise IntegrityError(_CARRY)
    for item in episodes:
        if not isinstance(item, dict) or len(item) > len(_EPISODE_FIELDS):
            raise IntegrityError(_CARRY)
        for name in ("invalidation", "recovery"):
            address = item.get(name)
            if address is None:
                continue
            if not isinstance(address, dict) or len(address) > len(_ADDRESS_FIELDS):
                raise IntegrityError(_CARRY)
            key = address.get("source_key")
            action = address.get("raw_action")
            if (type(key) is not str or len(key) > MAX_SOURCE_KEY
                    or (action is not None and (type(action) is not str or len(action) > MAX_ACTION))):
                raise IntegrityError(_CARRY)
            weight += len(key) + (0 if action is None else len(action))
            if weight > MAX_CARRY_BYTES:
                raise IntegrityError(_CARRY)
    previous = carry.get("previous_continuation_sha256")
    digest_value = carry.get("sha256")
    if ((previous is not None and (type(previous) is not str or len(previous) != 64))
            or type(digest_value) is not str or len(digest_value) != 64):
        raise IntegrityError(_CARRY)
    payload = {key: carry[key] for key in _CARRY_PAYLOAD_KEYS}
    encoded = canonical_json(payload)
    if len(encoded) > MAX_CARRY_BYTES:
        raise IntegrityError(_CARRY)
    if digest_value != hashlib.sha256(encoded).hexdigest():
        raise IntegrityError(_CARRY)
    return payload


def _replace_book_valid(table, values):
    import pyarrow as pa

    index = table.schema.get_field_index("book_valid")
    field = table.schema.field(index)
    return table.set_column(index, field, pa.array(values, type=field.type))


def _state_changes(inv_idx, rec_idx, start_blocked):
    changes = []
    i = r = 0
    blocked = start_blocked
    last = -1
    while True:
        if blocked:
            while r < rec_idx.size and rec_idx[r] <= last:
                r += 1
            if r >= rec_idx.size:
                break
            last = int(rec_idx[r])
            changes.append((last, "close"))
            blocked = False
            r += 1
        else:
            while i < inv_idx.size and inv_idx[i] <= last:
                i += 1
            if i >= inv_idx.size:
                break
            last = int(inv_idx[i])
            changes.append((last, "open"))
            blocked = True
            i += 1
    return changes


class ReportedBBOReinitializer:
    """Candidate local BBO restart for one raw instrument and one source_key."""

    def __init__(self, *, instrument_id, start_ns, end_ns, latency_ns,
                 maximum_rows=MAX_ROWS, maximum_episodes=MAX_EPISODES, continuation=None):
        if (type(instrument_id) is not int or instrument_id <= 0
                or type(start_ns) is not int or type(end_ns) is not int
                or not 0 <= start_ns < end_ns < 2**63 - 1_000_000_000
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000
                or type(maximum_rows) is not int or not 1 <= maximum_rows <= MAX_ROWS
                or type(maximum_episodes) is not int or not 1 <= maximum_episodes <= MAX_EPISODES):
            raise ContractError(
                "bounded raw instrument, event interval, delay and finite episode/row capacities required")
        self.instrument_id = instrument_id
        self.start = start_ns
        self.end = end_ns
        self.delay = latency_ns
        self.maximum_rows = maximum_rows
        self.maximum_episodes = maximum_episodes
        self.source_key = None
        self.episode_transition_visits = 0
        self._prefix_start = start_ns
        self._rows = 0
        self._valid_rows = 0
        self._invalid_rows = 0
        self._changed_rows = 0
        self._original_valid_rows = 0
        self._provider_flagged = 0
        self._clear_rows = 0
        self._unknown_rows = 0
        self._blocked = False
        self._history_complete = True
        self._cumulative_coverage = True
        self._episodes = []
        self._first_unresolved = None
        self._last_address = None
        self._last_t = None
        self._last_source_order = None
        self._last_source_row = None
        self._previous_continuation_sha256 = None
        self._closed = False
        self._failed = False
        if continuation is not None:
            self._restore(continuation)

    def _restore(self, carry):
        payload = _bound_carry(carry, maximum_episodes=self.maximum_episodes)
        if (payload["version"] != CARRY_VERSION or payload["completed"] is not True
                or payload["policy"] != POLICY or payload["policy_version"] != VERSION
                or payload["instrument_id"] != self.instrument_id
                or payload["latency_ns"] != self.delay
                or payload["maximum_rows"] != self.maximum_rows
                or payload["maximum_episodes"] != self.maximum_episodes
                or type(payload["event_start_ns"]) is not int
                or type(payload["event_end_ns"]) is not int
                or type(payload["prefix_start_ns"]) is not int
                or type(payload["next_start_ns"]) is not int
                or not 0 <= payload["prefix_start_ns"] <= payload["event_start_ns"]
                or not payload["event_start_ns"] < payload["event_end_ns"]
                or payload["event_end_ns"] != payload["next_start_ns"]
                or payload["next_start_ns"] != self.start):
            raise IntegrityError(_CARRY)
        key = payload["source_key"]
        if key is not None:
            key = _text(key)
        counts = {name: payload[name] for name in _COUNT_NAMES}
        if (any(type(counts[name]) is not int or counts[name] < 0 for name in _COUNT_NAMES)
                or counts["rows"] > self.maximum_rows
                or any(counts[name] > counts["rows"] for name in _COUNT_NAMES if name != "rows")
                or counts["candidate_valid_rows"] + counts["candidate_invalid_rows"] != counts["rows"]
                or type(payload["blocked"]) is not bool
                or type(payload["observed_history_complete"]) is not bool
                or type(payload["cumulative_coverage_complete"]) is not bool):
            raise IntegrityError(_CARRY)
        if payload["observed_history_complete"] and (
                counts["provider_flagged_records"] or counts["unknown_action_rows"]):
            raise IntegrityError(_CARRY)
        if ((not payload["observed_history_complete"])
                and counts["provider_flagged_records"] == 0 and counts["unknown_action_rows"] == 0):
            raise IntegrityError(_CARRY)
        prefix = payload["prefix_start_ns"]
        parsed = [_parse_episode(item, delay=self.delay, before_ns=self.start, after_ns=prefix)
                  for item in payload["episodes"]]
        if any(parsed[i]["episode_index"] != i + 1 for i in range(len(parsed))):
            raise IntegrityError(_CARRY)
        if any(item["unresolved"] for item in parsed[:-1]):
            raise IntegrityError(_CARRY)
        last = payload["last_source_address"]
        last_t, last_order, last_row = payload["last_t"], payload["last_source_order"], payload["last_source_row"]
        if counts["rows"] == 0:
            if (last is not None or last_t is not None or last_order is not None or last_row is not None
                    or parsed or any(counts[name] for name in _COUNT_NAMES) or payload["blocked"]
                    or not payload["observed_history_complete"]):
                raise IntegrityError(_CARRY)
        else:
            last = _parse_address(last, delay=self.delay, before_ns=self.start, after_ns=prefix)
            if (type(last_t) is not int or type(last_order) is not int or type(last_row) is not int
                    or last_t != last["t"] or last_order != last["source_order"]
                    or last_row != last["source_row"]
                    or key is None or last["source_key"] != key):
                raise IntegrityError(_CARRY)
        if key is not None:
            for item in parsed:
                if item["invalidation"]["source_key"] != key:
                    raise IntegrityError(_CARRY)
                if item["recovery"] is not None and item["recovery"]["source_key"] != key:
                    raise IntegrityError(_CARRY)
        if last is not None:
            for item in parsed:
                if not _address_at_or_before(item["invalidation"], last):
                    raise IntegrityError(_CARRY)
                if item["recovery"] is not None and not _address_at_or_before(item["recovery"], last):
                    raise IntegrityError(_CARRY)
        for left, right in zip(parsed, parsed[1:]):
            edge = left["invalidation"] if left["recovery"] is None else left["recovery"]
            if not _address_before(edge, right["invalidation"]):
                raise IntegrityError(_CARRY)
        if sum(item["provider_flagged_records"] for item in parsed) != counts["provider_flagged_records"]:
            raise IntegrityError(_CARRY)
        unresolved = payload["first_unresolved_invalidation"]
        if payload["blocked"]:
            if not parsed or not parsed[-1]["unresolved"] or unresolved is None:
                raise IntegrityError(_CARRY)
            unresolved = _parse_address(unresolved, delay=self.delay, before_ns=self.start, after_ns=prefix)
            if unresolved != parsed[-1]["invalidation"]:
                raise IntegrityError(_CARRY)
            if key is not None and unresolved["source_key"] != key:
                raise IntegrityError(_CARRY)
        elif unresolved is not None or (parsed and parsed[-1]["unresolved"]):
            raise IntegrityError(_CARRY)
        self.source_key = key
        self._prefix_start = prefix
        self._rows = counts["rows"]
        self._valid_rows = counts["candidate_valid_rows"]
        self._invalid_rows = counts["candidate_invalid_rows"]
        self._changed_rows = counts["changed_book_valid_rows"]
        self._original_valid_rows = counts["original_valid_rows"]
        self._provider_flagged = counts["provider_flagged_records"]
        self._clear_rows = counts["clear_rows"]
        self._unknown_rows = counts["unknown_action_rows"]
        self._blocked = payload["blocked"]
        self._history_complete = payload["observed_history_complete"]
        self._cumulative_coverage = payload["cumulative_coverage_complete"]
        self._episodes = parsed
        self._first_unresolved = unresolved
        self._last_address = None if last is None else _clone_address(last)
        self._last_t = last_t
        self._last_source_order = last_order
        self._last_source_row = last_row
        self._previous_continuation_sha256 = carry["sha256"]

    def _guard(self, fn, *args, **kwargs):
        if self._failed:
            raise IntegrityError(_FAILED)
        try:
            return fn(*args, **kwargs)
        except BaseException:
            self._failed = True
            raise

    def add(self, table):
        return self._guard(self._add, table)

    def finish(self, *, coverage_complete):
        return self._guard(self._finish, coverage_complete)

    def carry(self):
        return self._guard(self._carry)

    def _bind_source_key(self, table):
        import pyarrow.compute as pc

        keys = pc.unique(_combine(table["source_key"]))
        if keys.null_count or len(keys) != 1:
            raise IntegrityError("a reported-BBO window cannot join distinct acquired source streams")
        key = _text(keys[0].as_py())
        if self.source_key is not None and key != self.source_key:
            raise IntegrityError("a reported-BBO window cannot join distinct acquired source streams")
        self.source_key = key
        return key

    def _address_at(self, index, *, t, order, row, flags, known_at, actions, source_key):
        return {
            "source_key": source_key,
            "source_row": int(row[index]),
            "source_order": int(order[index]),
            "t": int(t[index]),
            "known_at": int(known_at[index]),
            "raw_flags": int(flags[index]),
            "raw_action": _action_text(actions[index].as_py()),
        }

    def _open_episode(self, address):
        if len(self._episodes) >= self.maximum_episodes:
            raise ContractError("reported-BBO reinitialization exceeds its finite episode capacity")
        episode = {
            "episode_index": len(self._episodes) + 1,
            "invalidation": address,
            "recovery": None,
            "unresolved": True,
            "provider_flagged_records": 0,
        }
        self._episodes.append(episode)
        self._first_unresolved = address
        self._blocked = True
        return episode

    def _close_episode(self, address):
        self._episodes[-1]["recovery"] = address
        self._episodes[-1]["unresolved"] = False
        self._first_unresolved = None
        self._blocked = False

    def _project(self, *, original, invalidation, recovery_marker, candidate_valid,
                 bit4, unknown, address_at):
        import numpy as np

        n = len(original)
        if np.any(bit4) or np.any(unknown):
            self._history_complete = False
        start_blocked = self._blocked
        inv_idx = np.flatnonzero(invalidation)
        rec_idx = np.flatnonzero(recovery_marker)
        if start_blocked and rec_idx.size == 0:
            self._episodes[-1]["provider_flagged_records"] += int(np.count_nonzero(bit4))
            return np.zeros(n, dtype=np.uint8)
        if not start_blocked and inv_idx.size == 0:
            if self._episodes:
                return candidate_valid.astype(np.uint8, copy=True)
            return original.astype(np.uint8, copy=True)

        changes = _state_changes(inv_idx, rec_idx, start_blocked)
        out = np.empty(n, dtype=np.uint8)
        blocked = start_blocked
        original_mode = not self._episodes
        prev = 0
        segments = []
        for index, kind in changes:
            self.episode_transition_visits += 1
            if blocked:
                out[prev:index] = 0
            elif original_mode:
                out[prev:index] = original[prev:index]
            else:
                out[prev:index] = candidate_valid[prev:index]
            if kind == "open":
                out[index] = 0
                episode = self._open_episode(address_at(index))
                segments.append([episode, index, n])
                blocked = True
                original_mode = False
            else:
                out[index] = 1
                self._close_episode(address_at(index))
                if segments:
                    segments[-1][2] = index
                elif start_blocked:
                    self._episodes[-1]["provider_flagged_records"] += int(np.count_nonzero(bit4[:index]))
                blocked = False
                original_mode = False
            prev = index + 1
        if blocked:
            out[prev:] = 0
        elif original_mode:
            out[prev:] = original[prev:]
        else:
            out[prev:] = candidate_valid[prev:]
        for episode, left, right in segments:
            episode["provider_flagged_records"] += int(np.count_nonzero(bit4[left:right]))
        self._blocked = blocked
        return out

    def _add(self, table):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc

        if self._closed or not set(REQUIRED).issubset(getattr(table, "schema", pa.schema([])).names):
            raise IntegrityError(_PROJECTION)
        if len(table) > BATCH_ROWS:
            raise ContractError(_PROJECTION)
        if self._rows + len(table) > self.maximum_rows:
            raise ContractError("reported-BBO reinitialization exceeds its registered row capacity")
        _require_categorical(table["raw_action"], allow_null=True)
        _require_categorical(table["raw_side"], allow_null=True)
        _require_categorical(table["source_key"], allow_null=False)
        if not len(table):
            return _replace_book_valid(table, [])
        if any(table[name].null_count for name in REQUIRED if name not in ("raw_action", "raw_side")):
            raise IntegrityError(_NULL)
        source_key = self._bind_source_key(table)
        values = {}
        for name in _NUMERIC:
            array = _combine(table[name]).to_numpy(zero_copy_only=False)
            if array.ndim != 1 or array.dtype.kind not in "iu":
                raise IntegrityError(_IDENTITY)
            values[name] = array
        t, order, row = values["t"], values["source_order"], values["source_row"]
        flags, original, snapshot = values["raw_flags"], values["book_valid"], values["snapshot"]
        bid, ask, qb, qa = values["bid"], values["ask"], values["bid_size"], values["ask_size"]
        if (np.any(values["instrument_id"] != self.instrument_id)
                or np.any(t < self.start) or np.any(t >= self.end)
                or np.any(values["known_at_ns"] != t + self.delay)
                or np.any(order < 0) or np.any(row < 0)
                or np.any(t[1:] < t[:-1]) or np.any(order[1:] <= order[:-1]) or np.any(row[1:] <= row[:-1])
                or self._last_t is not None and int(t[0]) < self._last_t
                or self._last_source_order is not None and int(order[0]) <= self._last_source_order
                or self._last_source_row is not None and int(row[0]) <= self._last_source_row):
            raise IntegrityError(_IDENTITY)
        if (np.any(~np.isin(original, (0, 1))) or np.any(~np.isin(snapshot, (0, 1)))
                or np.any(flags < 0) or np.any(flags > 255)
                or np.any(snapshot != ((flags & np.int64(32)) != 0))):
            raise IntegrityError("quote projection flags or validity bits changed")
        actions = _as_text_array(table["raw_action"])
        updates = pc.fill_null(pc.is_in(actions, value_set=pa.array(list(_UPDATES))), False).to_numpy(zero_copy_only=False)
        clears = pc.fill_null(pc.equal(actions, "R"), False).to_numpy(zero_copy_only=False)
        known = pc.fill_null(pc.is_in(actions, value_set=pa.array(list(_KNOWN))), False).to_numpy(zero_copy_only=False)
        unknown = ~known
        bit4 = (flags & np.int64(4)) != 0
        last_bit = (flags & np.int64(128)) != 0
        snap_bit = (flags & np.int64(32)) != 0
        invalidation = bit4 | clears | unknown
        domain = ((bid > 0) & (ask < _PRICE_LIMIT) & (bid <= ask)
                  & (qb > 0) & (qa > 0) & (qb < _SIZE_LIMIT) & (qa < _SIZE_LIMIT))
        valid_update = updates & ~bit4 & domain
        if np.any(original.astype(bool) & ~valid_update):
            raise IntegrityError(_TRUST)
        recovery_marker = updates & ~bit4 & ~snap_bit & last_bit & domain
        candidate_valid = valid_update.astype(np.uint8, copy=False)

        def address_at(index):
            return self._address_at(index, t=t, order=order, row=row, flags=flags,
                                    known_at=values["known_at_ns"], actions=actions, source_key=source_key)

        out = self._project(original=original, invalidation=invalidation, recovery_marker=recovery_marker,
                            candidate_valid=candidate_valid, bit4=bit4, unknown=unknown, address_at=address_at)
        self._rows += len(out)
        self._valid_rows += int(np.count_nonzero(out))
        self._invalid_rows += int(np.count_nonzero(out == 0))
        self._changed_rows += int(np.count_nonzero(out != original.astype(np.uint8, copy=False)))
        self._original_valid_rows += int(np.count_nonzero(original))
        self._provider_flagged += int(np.count_nonzero(bit4))
        self._clear_rows += int(np.count_nonzero(clears))
        self._unknown_rows += int(np.count_nonzero(unknown))
        self._last_address = address_at(len(out) - 1)
        self._last_t = self._last_address["t"]
        self._last_source_order = self._last_address["source_order"]
        self._last_source_row = self._last_address["source_row"]
        return _replace_book_valid(table, out)

    def _report(self, coverage_complete):
        if self._valid_rows + self._invalid_rows != self._rows:
            raise IntegrityError("candidate validity counts do not reconcile with observed rows")
        if self._blocked != (self._first_unresolved is not None):
            raise IntegrityError("blocked reported-BBO state lost its first unresolved invalidation")
        if self._blocked != (bool(self._episodes) and self._episodes[-1]["unresolved"]):
            raise IntegrityError("terminal unresolved episode disagrees with retained addresses")
        if self._history_complete and (self._provider_flagged or self._unknown_rows):
            raise IntegrityError("observed-history completeness cannot survive a flagged or unknown prefix")
        return {
            "version": VERSION,
            "policy": POLICY,
            "policy_version": VERSION,
            "source_assumption_name": SOURCE_ASSUMPTION_NAME,
            "source_assumption": SOURCE_ASSUMPTION,
            "publication_status": "unpublished_validation_candidate",
            "admitted_for_serving": False,
            "venue_history_certified": False,
            "exchange_order_certified": False,
            "instrument_id": self.instrument_id,
            "event_start_ns": self.start,
            "event_end_ns": self.end,
            "known_at_ns": self.end + self.delay,
            "latency_scenario_ns": self.delay,
            "prefix_start_ns": self._prefix_start,
            "source_key": self.source_key,
            "coverage_complete": coverage_complete,
            "cumulative_coverage_complete": self._cumulative_coverage,
            "empty_observed_window": self._rows == 0,
            "empty_window_is_not_market_completeness": True,
            "observed_history_complete": self._history_complete,
            "blocked": self._blocked,
            "terminal_episode_unresolved": self._blocked,
            "rows": self._rows,
            "candidate_valid_rows": self._valid_rows,
            "candidate_invalid_rows": self._invalid_rows,
            "changed_book_valid_rows": self._changed_rows,
            "original_valid_rows": self._original_valid_rows,
            "provider_flagged_records": self._provider_flagged,
            "clear_rows": self._clear_rows,
            "unknown_action_rows": self._unknown_rows,
            "episode_count": len(self._episodes),
            "resolved_episode_count": sum(1 for item in self._episodes if not item["unresolved"]),
            "unresolved_episode_count": int(self._blocked),
            "episodes": [_clone_episode(item) for item in self._episodes],
            "first_unresolved_invalidation": None if self._first_unresolved is None
            else _clone_address(self._first_unresolved),
            "last_source_address": None if self._last_address is None else _clone_address(self._last_address),
            "maximum_rows": self.maximum_rows,
            "maximum_episodes": self.maximum_episodes,
            "order_basis": "retained single-source storage order; provider sequence and strategy receipt absent",
            "ordering_scope": "one original source_key; cross-file joins are unsupported",
            "book_recovery": (
                "reported local BBO reinitialization candidate after a clean completed "
                "ordinary full-BBO record; not a source-certified venue recovery"
            ),
        }

    def _finish(self, coverage_complete):
        if self._closed or type(coverage_complete) is not bool:
            raise IntegrityError("reported-BBO publication requires one explicit completed coverage decision")
        self._cumulative_coverage = self._cumulative_coverage and coverage_complete
        report = self._report(coverage_complete)
        self._closed = True
        return report

    def _carry_payload(self):
        return {
            "version": CARRY_VERSION,
            "completed": True,
            "policy": POLICY,
            "policy_version": VERSION,
            "instrument_id": self.instrument_id,
            "source_key": self.source_key,
            "latency_ns": self.delay,
            "event_start_ns": self.start,
            "event_end_ns": self.end,
            "next_start_ns": self.end,
            "prefix_start_ns": self._prefix_start,
            "maximum_rows": self.maximum_rows,
            "maximum_episodes": self.maximum_episodes,
            "rows": self._rows,
            "candidate_valid_rows": self._valid_rows,
            "candidate_invalid_rows": self._invalid_rows,
            "changed_book_valid_rows": self._changed_rows,
            "original_valid_rows": self._original_valid_rows,
            "provider_flagged_records": self._provider_flagged,
            "clear_rows": self._clear_rows,
            "unknown_action_rows": self._unknown_rows,
            "blocked": self._blocked,
            "observed_history_complete": self._history_complete,
            "cumulative_coverage_complete": self._cumulative_coverage,
            "first_unresolved_invalidation": None if self._first_unresolved is None
            else _clone_address(self._first_unresolved),
            "last_source_address": None if self._last_address is None else _clone_address(self._last_address),
            "last_t": self._last_t,
            "last_source_order": self._last_source_order,
            "last_source_row": self._last_source_row,
            "episodes": [_clone_episode(item) for item in self._episodes],
            "previous_continuation_sha256": self._previous_continuation_sha256,
        }

    def _carry(self):
        if not self._closed:
            raise IntegrityError("partial or failed reported-BBO intervals cannot provide continuation")
        payload = self._carry_payload()
        encoded = canonical_json(payload)
        if len(encoded) > MAX_CARRY_BYTES:
            raise IntegrityError(_CARRY)
        return {**payload, "sha256": hashlib.sha256(encoded).hexdigest()}
