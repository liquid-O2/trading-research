"""Fast, byte-identical paths for the event-time window, installed at import.

This module is deliberately outside ``event_cache.transform_identity`` (which pins
event_time.py, event_cache.py, mbp1_views.py, adapters.py, native_resolution.py,
empirical_tape.py and objects/profiles.py by content): nothing here changes an event
cache key. Every function reproduces the pinned implementation's result exactly and
is tested against it (tests/method_pack/test_event_time_fast.py):

* ``file_digest`` memoizes full-file sha256 digests of inputs of 8 MiB or more by
  (absolute path, size, mtime_ns, inode, device), in-process and in an append-only
  store shared across processes; an entry is only ever a digest this function computed
  for the same signature. Smaller files are always hashed.
* ``contract_at`` parses and digests the roll map once per file signature.
* ``profile_payload`` is ``empirical_tape._profile_payload`` with the flat, immutable
  ``PriceRow`` rendered without ``dataclasses.asdict``'s deepcopy.
* ``canonical_manifest`` parses the canonical file manifest once per file signature.
* ``FastEventWindow`` memoizes ``coverage`` (the per-minute state depends on ``end``
  only through ``known_at > end``) and accumulates footprint prefixes incrementally for
  ``profile`` and ``vwap`` (every sum is exact, so the order of addition is immaterial).

``install()`` rebinds ``file_digest`` in event_time and event_cache and ``contract_at``
in event_cache, the same way ``rule_discovery.native.install_write_guard`` rebinds
``build_event_window``.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import fields
from decimal import Decimal
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from . import event_cache, event_time
from .empirical_tape import _canonical_manifest as _pinned_canonical_manifest, _d, _value_area_tie_both
from .event_time import EventWindow, MINUTE, VERSION, interval_state
from .native_resolution import NativeEvidenceError
from .native_resolution import file_digest as _full_file_digest
from .objects import profiles

# ---------------------------------------------------------------------------- digests
DIGEST_MEMO_MIN_BYTES = 8 * 1024 * 1024
_DIGEST_MEMO: dict[tuple, str] = {}
_DIGEST_STORE_OFFSETS: dict[Path, int] = {}


def digest_store_dir() -> Path | None:
    setting = os.environ.get('TR_FILE_DIGEST_CACHE', '/workspace/.cache/file-digests')
    return None if setting in ('', 'off', '0') else Path(setting)


def _digest_store_load(store: Path) -> None:
    """Read every line any process appended since this process last looked."""
    try:
        names = sorted(p for p in store.iterdir() if p.suffix == '.jsonl')
    except OSError:
        return
    for name in names:
        offset = _DIGEST_STORE_OFFSETS.get(name, 0)
        try:
            with name.open('rb') as stream:
                stream.seek(offset)
                chunk = stream.read()
        except OSError:
            continue
        lines = chunk.split(b'\n')
        complete = chunk.endswith(b'\n')
        consumed = len(chunk) if complete else len(chunk) - len(lines[-1])
        _DIGEST_STORE_OFFSETS[name] = offset + consumed
        for line in (lines if complete else lines[:-1]):
            if not line:
                continue
            try:
                row = json.loads(line)
                _DIGEST_MEMO[(row['path'], row['size'], row['mtime_ns'], row['ino'], row['dev'])] = row['sha256']
            except (ValueError, KeyError, TypeError):
                continue


def _digest_store_append(store: Path, key: tuple, value: str) -> None:
    try:
        store.mkdir(parents=True, exist_ok=True)
        row = {'path': key[0], 'size': key[1], 'mtime_ns': key[2], 'ino': key[3], 'dev': key[4], 'sha256': value}
        with (store / f'{os.uname().nodename}-{os.getpid()}.jsonl').open('ab') as stream:
            stream.write(json.dumps(row, separators=(',', ':')).encode() + b'\n')
    except OSError:
        pass


def file_digest(path):
    """Full-file sha256, equal to native_resolution.file_digest; large inputs memoized."""
    path = Path(path)
    try:
        stat = path.stat()
    except OSError:
        return _full_file_digest(path)
    if stat.st_size < DIGEST_MEMO_MIN_BYTES:
        return _full_file_digest(path)
    key = (os.path.abspath(path), stat.st_size, stat.st_mtime_ns, stat.st_ino, stat.st_dev)
    value = _DIGEST_MEMO.get(key)
    if value is None:
        store = digest_store_dir()
        if store is not None:
            _digest_store_load(store)
            value = _DIGEST_MEMO.get(key)
        if value is None:
            value = _full_file_digest(path)
            _DIGEST_MEMO[key] = value
            if store is not None:
                _digest_store_append(store, key, value)
    return value


# ---------------------------------------------------------------------------- roll map
_ROLL_MAP_MEMO: dict[tuple, tuple] = {}


_ROLL_MAP_RECHECK_SECONDS = 30.0


def _roll_map(path: Path) -> tuple[list, str]:
    """Rows and digest of the roll map, re-read whenever the file's stat signature changes
    (the signature is re-checked at most every 30 s: the file is an acquired input)."""
    import pyarrow.parquet as pq
    import time
    recent = _ROLL_MAP_MEMO.get("recent")
    now = time.monotonic()
    if recent is not None and recent[0] == str(path) and now - recent[1] < _ROLL_MAP_RECHECK_SECONDS:
        return recent[2]
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns, stat.st_ino)
    hit = _ROLL_MAP_MEMO.get(key)
    if hit is None:
        hit = (pq.read_table(path).to_pylist(), file_digest(path))
        _ROLL_MAP_MEMO.clear()
        _ROLL_MAP_MEMO[key] = hit
    _ROLL_MAP_MEMO["recent"] = (str(path), now, hit)
    return hit


def contract_at(data_root, at):
    """Equal to event_cache.contract_at; the roll map is parsed once per file signature."""
    path = Path(data_root) / 'derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet'
    rows, digest = _roll_map(path)
    selected = [r for r in rows if r['segment_start_ms'] * 1_000_000 <= at
                and (r['segment_end_exclusive_ms'] is None or at < r['segment_end_exclusive_ms'] * 1_000_000)]
    if len(selected) != 1:
        raise NativeEvidenceError('no unique acquired continuous-contract identity for date')
    return {**selected[0], 'roll_source_path': str(path), 'roll_source_sha256': digest,
            'identity_use': 'acquired continuous membership only, not a tradable roll forecast'}


# ---------------------------------------------------------------------------- profile payload
_PRICE_ROW_FIELDS = tuple(f.name for f in fields(profiles.PriceRow))


def _row_payload(row: profiles.PriceRow) -> dict[str, Any]:
    """Equal to dataclasses.asdict(row): the row is flat and every value is immutable."""
    return {name: getattr(row, name) for name in _PRICE_ROW_FIELDS}


def profile_payload(accum: Mapping[Decimal, Sequence[Decimal]], *, tick: Decimal,
                     tie_policy: str | None,
                     value_area: profiles.ValueAreaConfig | Mapping[str, Any] | None,
                     complete: bool | None) -> dict[str, Any]:
    if tick <= 0:
        raise NativeEvidenceError("native instrument tick must be positive")
    rows: list[profiles.PriceRow] = []
    for price in sorted(accum):
        if price / tick != (price / tick).to_integral_value():
            raise NativeEvidenceError(f"price {price} is not aligned to native tick {tick}")
        buy, sell, unknown = map(Decimal, accum[price])
        delta = buy - sell
        rows.append(profiles.PriceRow(price, buy, sell, unknown,
                                      buy + sell + unknown, delta,
                                      delta if unknown == 0 else None,
                                      delta - unknown, delta + unknown))
    if complete is True and rows:
        by_price = {row.price: row for row in rows}
        price = rows[0].price
        while price <= rows[-1].price:
            by_price.setdefault(price, profiles.PriceRow(
                price, Decimal(0), Decimal(0), Decimal(0), Decimal(0),
                Decimal(0), Decimal(0), Decimal(0), Decimal(0)))
            price += tick
        rows = [by_price[price] for price in sorted(by_price)]
    poc, candidates, tie_state = profiles._poc(rows, tie_policy)
    if isinstance(value_area, Mapping):
        fraction = _d(value_area["fraction"])
        val, vah, inside, achieved = _value_area_tie_both(rows, poc, fraction)
        va_id = "empirical-m08-va70-tie-both"
        va_algorithm = "contiguous_larger_adjacent_volume_tie_both"
        va_tie = "both"
    else:
        val, vah, inside, achieved = profiles._value_area(rows, poc, value_area)
        fraction = None if value_area is None else value_area.fraction
        va_id = None if value_area is None else value_area.config_id
        va_algorithm = None if value_area is None else value_area.algorithm
        va_tie = None if value_area is None else value_area.tie_policy
    return {
        "rows": [_row_payload(row) for row in rows],
        "total_volume": sum((row.total_volume for row in rows), Decimal(0)),
        "H": rows[-1].price if rows else None,
        "L": rows[0].price if rows else None,
        "poc": poc,
        "poc_candidates": list(candidates),
        "poc_tie_state": tie_state,
        "val": val,
        "vah": vah,
        "value_area_fraction": fraction,
        "value_area_config_id": va_id,
        "value_area_algorithm": va_algorithm,
        "value_area_tie_policy": va_tie,
        "volume_inside_value": inside,
        "achieved_value_fraction": achieved,
        "bin_width": tick,
        "bin_origin": Decimal(0),
        "bin_membership": "native_tick",
    }


# ---------------------------------------------------------------------------- window
def _intersects(span, lo, hi):
    a, b = (span.get('start_ns'), span.get('end_ns')) if isinstance(span, dict) else span
    return a is not None and b is not None and a < hi and b > lo


_ZERO = Decimal(0)


class Prefix:
    """A footprint prefix: exact per-price volume sums plus the minute members."""

    __slots__ = ("window", "index", "state", "members")

    def __init__(self, window, index, state, members):
        self.window, self.index, self.state, self.members = window, index, state, members

    @property
    def volume(self):
        return self.state["volume"]

    @property
    def pv(self):
        return self.state["pv"]

    @property
    def p2v(self):
        return self.state["p2v"]

    def accum(self):
        """The pinned accumulator mapping price -> [buy, sell, unknown] Decimal sums."""
        if not self.index["vectorised"]:
            return self.state["accum"]
        acc, keys = self.state["acc"], self.index["keys"]
        return {keys[t]: [Decimal(int(acc[t, 0])), Decimal(int(acc[t, 1])), Decimal(int(acc[t, 2]))]
                for t in np.flatnonzero(self.state["seen"]).tolist()}

    def payload(self, *, tick, tie_policy, value_area, complete):
        """Equal to empirical_tape._profile_payload(self.accum(), ...)."""
        if not (self.index["vectorised"] and tie_policy == "lowest" and isinstance(value_area, Mapping)):
            return profile_payload(self.accum(), tick=tick, tie_policy=tie_policy,
                                   value_area=value_area, complete=complete)
        return _payload_arrays(self.window, self.index, self.state, tick=tick, value_area=value_area,
                               complete=complete)


def _sorted_keys(window, index, tick):
    """Per window and tick: the price keys in sorted order and their tick alignment."""
    cache = window.__dict__.setdefault("_sorted_keys", {})
    hit = cache.get(tick)
    if hit is None:
        keys = index["keys"]
        order = sorted(range(len(keys)), key=keys.__getitem__)
        aligned = [(keys[t] / tick) == (keys[t] / tick).to_integral_value() for t in order]
        hit = cache[tick] = (np.asarray(order, dtype=np.int64), np.asarray(aligned, dtype=bool))
    return hit


def _row_dict(cache, key, price, buy, sell, unknown):
    """The pinned row rendering for one (price, buy, sell, unknown), shared when repeated.

    ``key`` identifies the price spelling: the window's key index for an observed price,
    or ("fill", str(price)) for a tick-grid fill price, whose object is kept in the cache."""
    key = (key, buy, sell, unknown)
    row = cache.get(key)
    if row is None:
        b, s, u = Decimal(buy), Decimal(sell), Decimal(unknown)
        delta = b - s
        row = cache[key] = {
            "price": price, "buy_volume": b, "sell_volume": s, "unknown_volume": u,
            "total_volume": b + s + u, "known_delta": delta,
            "full_delta": delta if u == 0 else None,
            "delta_low": delta - u, "delta_high": delta + u,
        }
    return row


def _payload_arrays(window, index, state, *, tick, value_area, complete):
    if tick <= 0:
        raise NativeEvidenceError("native instrument tick must be positive")
    keys = index["keys"]
    order, aligned = _sorted_keys(window, index, tick)
    seen = state["seen"]
    present = order[seen[order]]
    bad = present[~aligned[seen[order]]]
    if bad.size:
        price = keys[int(bad[0])]
        raise NativeEvidenceError(f"price {price} is not aligned to native tick {tick}")
    acc = state["acc"]
    sel = present.tolist()
    volumes = acc[present]
    totals = volumes.sum(axis=1) if sel else np.zeros(0, dtype=np.int64)
    prices = [keys[t] for t in sel]
    row_keys = sel
    cache = window.__dict__.setdefault("_row_dicts", {})
    if complete is True and sel:
        low = prices[0]
        steps = [int(((price - low) / tick).to_integral_value()) for price in prices]
        grid = steps[-1] + 1
        if grid != len(sel):
            fills = window.__dict__.setdefault("_fill_prices", {})
            full_prices = [None] * grid
            full_keys = [None] * grid
            full_volumes = np.zeros((grid, 3), dtype=np.int64)
            for position, step in enumerate(steps):
                full_prices[step] = prices[position]
                full_keys[step] = sel[position]
                full_volumes[step] = volumes[position]
            for step in range(grid):
                if full_prices[step] is None:
                    price = low + tick * step
                    spelling = ("fill", str(price))
                    full_prices[step] = fills.setdefault(spelling, price)
                    full_keys[step] = spelling
            prices, volumes, row_keys = full_prices, full_volumes, full_keys
            totals = volumes.sum(axis=1)
    rows = []
    for position, price in enumerate(prices):
        buy, sell, unknown = volumes[position].tolist()
        rows.append(_row_dict(cache, row_keys[position], price, buy, sell, unknown))
    # POC with tie policy "lowest" (objects/profiles._poc)
    total_int = int(totals.sum()) if len(prices) else 0
    if not prices or total_int == 0 and not np.any(totals):
        poc, candidates, tie_state = None, (), "empty"
    else:
        maximum = int(totals.max())
        candidate_positions = np.flatnonzero(totals == maximum).tolist()
        candidates = tuple(prices[position] for position in candidate_positions)
        poc = candidates[0]
        tie_state = "unique" if len(candidates) == 1 else "resolved"
    # value area, both equal neighbours (empirical_tape._value_area_tie_both)
    fraction = _d(value_area["fraction"])
    if not 0 < fraction <= 1:
        raise NativeEvidenceError("value-area fraction must be in (0,1]")
    val = vah = inside = achieved = None
    if prices and poc is not None and total_int > 0:
        numerator, denominator = fraction.as_integer_ratio()
        totals_list = totals.tolist()
        position = candidate_positions[0]
        lowest = highest = position
        inside_int = totals_list[position]
        low, high = position - 1, position + 1
        count = len(totals_list)
        while inside_int * denominator < numerator * total_int and (low >= 0 or high < count):
            low_volume = totals_list[low] if low >= 0 else None
            high_volume = totals_list[high] if high < count else None
            if low_volume is None:
                chosen = (high,)
            elif high_volume is None:
                chosen = (low,)
            elif low_volume > high_volume:
                chosen = (low,)
            elif high_volume > low_volume:
                chosen = (high,)
            else:
                chosen = (low, high)
            for item in chosen:
                inside_int += totals_list[item]
                lowest = min(lowest, item)
                highest = max(highest, item)
            if low in chosen:
                low -= 1
            if high in chosen:
                high += 1
        inside = Decimal(inside_int)
        val, vah, achieved = prices[lowest], prices[highest], inside / Decimal(total_int)
    return {
        "rows": rows,
        "total_volume": Decimal(total_int) if prices else _ZERO,
        "H": prices[-1] if prices else None,
        "L": prices[0] if prices else None,
        "poc": poc,
        "poc_candidates": list(candidates),
        "poc_tie_state": tie_state,
        "val": val,
        "vah": vah,
        "value_area_fraction": fraction,
        "value_area_config_id": "empirical-m08-va70-tie-both",
        "value_area_algorithm": "contiguous_larger_adjacent_volume_tie_both",
        "value_area_tie_policy": "both",
        "volume_inside_value": inside,
        "achieved_value_fraction": achieved,
        "bin_width": tick,
        "bin_origin": Decimal(0),
        "bin_membership": "native_tick",
    }


class FastEventWindow(EventWindow):
    """EventWindow with memoized coverage and incremental footprint prefixes."""

    def coverage(self, start, end):
        if start < self.start or end > self.end:
            return {"observed_scope_complete": False, "market_coverage_complete": None,
                    "unknown_intervals": [[start, end]], "states": {}}
        memo = self.__dict__.setdefault("_coverage_memo", {})
        hit = memo.get((start, end))
        if hit is not None:
            return {"observed_scope_complete": hit[0], "market_coverage_complete": None,
                    "unknown_intervals": [list(hole) for hole in hit[1]], "states": dict(hit[2])}
        base = self.__dict__.setdefault("_minute_base", {})
        series = self.series.get(60, {})
        unowned = self.document.get('plan', {}).get('unowned_intervals', [])
        states = defaultdict(int)
        holes = []
        for at in range(start // MINUTE * MINUTE, end, MINUTE):
            lo, hi = max(start, at), min(at + MINUTE, end)
            row = series.get(at)
            if lo == at and hi == at + MINUTE:
                entry = base.get(at)
                if entry is None:
                    state = interval_state(lo, hi, [] if row is None else [row],
                                           schedule=self.schedule, continuity=self.continuity)
                    if state != 'scheduled_closure' and (any(_intersects(span, lo, hi) for span in unowned)
                            or row is not None and not row['observed_complete']):
                        state = 'unknown_coverage'
                    entry = base[at] = (state, None if row is None else row['known_at'])
                state, known_at = entry
                if state != 'scheduled_closure' and known_at is not None and known_at > end:
                    state = 'unknown_coverage'
            else:
                state = interval_state(lo, hi, [] if row is None else [row],
                                       schedule=self.schedule, continuity=self.continuity)
                if state != 'scheduled_closure' and (any(_intersects(span, lo, hi) for span in unowned)
                        or lo != at or hi != at + MINUTE
                        or row is not None and (not row['observed_complete'] or row['known_at'] > end)):
                    state = 'unknown_coverage'
            states[state] += 1
            if state == "unknown_coverage":
                holes.append([lo, hi])
        memo[(start, end)] = (not holes, tuple(tuple(hole) for hole in holes), dict(states))
        return {"observed_scope_complete": not holes, "market_coverage_complete": None,
                "unknown_intervals": holes, "states": dict(states)}

    def _prefix_index(self):
        """Per-window arrays built once: minute order, membership thresholds, flat rows."""
        index = self.__dict__.get("_prefix_cache")
        if index is not None:
            return index
        order = list(self.footprints.items())
        thresholds = [max(row["end"], row["known_at"]) for _, row in order]
        by_threshold = sorted(range(len(order)), key=thresholds.__getitem__)
        keys: list[Decimal] = []
        key_index: dict[Decimal, int] = {}
        key_text: dict[Decimal, str] = {}
        offsets = [0]
        price_idx: list[int] = []
        vols: list[int] = []
        vectorised = True
        for _, row in order:
            for price, buy, sell, unknown in row["rows"]:
                key = _d(price)
                t = key_index.get(key)
                if t is None:
                    t = key_index[key] = len(keys)
                    keys.append(key)
                    key_text[key] = str(key)
                elif key_text[key] != str(key):
                    vectorised = False  # two spellings of one price: the key object matters
                if not (type(buy) is int and type(sell) is int and type(unknown) is int):
                    vectorised = False
                price_idx.append(t)
                vols.extend((buy, sell, unknown))
            offsets.append(len(price_idx))
        minute_pv = [_d(row["pv"]) for _, row in order]
        minute_p2v = [_d(row["p2v"]) for _, row in order]
        index = {
            "order": order, "thresholds": thresholds, "by_threshold": by_threshold,
            "keys": keys, "offsets": np.asarray(offsets, dtype=np.int64),
            "price_idx": np.asarray(price_idx, dtype=np.int64),
            "vols": np.asarray(vols, dtype=np.int64).reshape(-1, 3),
            "minute_pv": minute_pv, "minute_p2v": minute_p2v, "vectorised": vectorised,
        }
        self._prefix_cache = index
        return index

    def _prefix(self, start, end):
        """Footprint minutes with start <= at, end <= end and known_at <= end.

        Membership grows monotonically with ``end`` for a fixed ``start``, so the per-price
        accumulators and the volume, pv and p2v sums are extended from the previous call
        instead of rebuilt. Volumes are integers, so the per-price sums are exact int64
        sums, equal to the pinned Decimal sums; pv and p2v are exact Decimal sums.
        Returns a ``Prefix``."""
        index = self._prefix_index()
        order, thresholds, by_threshold = index["order"], index["thresholds"], index["by_threshold"]
        states = self.__dict__.setdefault("_prefix_states", {})
        state = states.get(start)
        temporary = state is not None and state["end"] > end
        if state is None or temporary:
            state = {"end": end, "pointer": 0, "members": [], "accum": {},
                     "volume": 0, "pv": Decimal(0), "p2v": Decimal(0),
                     "acc": np.zeros((len(index["keys"]), 3), dtype=np.int64),
                     "seen": np.zeros(len(index["keys"]), dtype=bool)}
            if not temporary:
                states[start] = state
        members, pointer = state["members"], state["pointer"]
        volume, pv, p2v = state["volume"], state["pv"], state["p2v"]
        accum, acc, seen = state["accum"], state["acc"], state["seen"]
        offsets, price_idx, vols = index["offsets"], index["price_idx"], index["vols"]
        vectorised = index["vectorised"]
        while pointer < len(by_threshold) and thresholds[by_threshold[pointer]] <= end:
            i = by_threshold[pointer]
            pointer += 1
            at, row = order[i]
            if start <= at:
                members.append(i)
                lo, hi = int(offsets[i]), int(offsets[i + 1])
                if vectorised:
                    if hi > lo:
                        idx = price_idx[lo:hi]
                        np.add.at(acc, idx, vols[lo:hi])
                        seen[idx] = True
                else:
                    for price, buy, sell, unknown in row["rows"]:
                        key = _d(price)
                        cell = accum.get(key)
                        if cell is None:
                            cell = accum[key] = [Decimal(0), Decimal(0), Decimal(0)]
                        cell[0] += _d(buy)
                        cell[1] += _d(sell)
                        cell[2] += _d(unknown)
                volume += row["volume"]
                pv += index["minute_pv"][i]
                p2v += index["minute_p2v"][i]
        state.update(end=end, pointer=pointer, volume=volume, pv=pv, p2v=p2v)
        return Prefix(self, index, state, [order[i][0] for i in sorted(members)])

    def profile(self, start, end, *, tick=Decimal(".25"), kind="selected_range"):
        prefix = self._prefix(start, end)
        coverage = self.coverage(start, end)
        result = prefix.payload(tick=tick, tie_policy="lowest",
            value_area={"fraction": Decimal(".70"), "algorithm": "contiguous_larger_adjacent_volume_tie_both", "tie_policy": "both"},
            complete=coverage["observed_scope_complete"])
        result.update(profile_id=f"{VERSION}:{self.instrument_id}:{start}:{end}",
            kind=kind, formation_start=start, formation_end=end, known_at=end,
            instrument_id=self.instrument_id, coverage=coverage, minute_members=prefix.members)
        return result

    def vwap(self, start, end):
        prefix = self._prefix(start, end)
        volume, pv, p2v = prefix.volume, prefix.pv, prefix.p2v
        price = pv / volume if volume else None
        variance = max(Decimal(0), p2v / volume - price * price) if volume else None
        return {"price": price, "variance": variance, "sd": variance.sqrt() if variance is not None else None,
                "volume": volume, "reset_at": start, "known_at": end,
                "basis": "execution_price_volume_event_time", "coverage": self.coverage(start, end)}


_CANONICAL_MEMO: dict[tuple, dict] = {}


def canonical_manifest(root):
    """Equal to empirical_tape._canonical_manifest; parsed once per manifest file signature."""
    root = Path(root)
    signature = [str(root)]
    for name in ("files.parquet", "files.csv"):
        path = root / "manifests" / name
        try:
            stat = path.stat()
            signature.append((name, stat.st_size, stat.st_mtime_ns, stat.st_ino))
        except OSError:
            signature.append((name, None))
    key = tuple(signature)
    hit = _CANONICAL_MEMO.get(key)
    if hit is None:
        hit = _pinned_canonical_manifest(root)
        _CANONICAL_MEMO.clear()
        _CANONICAL_MEMO[key] = hit
    return hit


#: The pinned implementations, kept for the equality tests.
PINNED = {
    "file_digest": _full_file_digest,
    "contract_at": event_cache.contract_at,
    "canonical_manifest": _pinned_canonical_manifest,
    "profile_payload": event_time._profile_payload,
    "EventWindow": EventWindow,
}


def install() -> None:
    """Rebind the pinned modules' digest, roll-map and manifest lookups to the memoized twins."""
    event_time.file_digest = file_digest
    event_cache.file_digest = file_digest
    event_cache.contract_at = contract_at
    event_time._canonical_manifest = canonical_manifest


install()
