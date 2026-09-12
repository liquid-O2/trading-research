"""Bounded native tape aggregation and the frozen M09 comparison.

The helpers in this module never treat a file extent as tape coverage.  They
admit only canonically owned physical files, hash the complete file bytes,
retain exact physical row membership, and reconcile every requested minute
against the independent native one-minute OHLCV archive.  Trade payloads are
streamed in bounded Arrow batches; a session retains aggregates and compact
row ranges, not the full execution tape.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from decimal import Decimal
from hashlib import sha256
import csv
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

from . import adapters
from .empirical_protocol import Opportunity, ReplayResult, content_hash
from .native_resolution import (
    NativeEvidenceError, NativeResolver, _selected_source_rows,
    _stat_signature, file_digest, ns,
)
from .native_windows import _group_ranges
from .objects import profiles
from .protocol import jsonable

MINUTE = 60_000_000_000
SECOND = 1_000_000_000
MAX_TAPE_WINDOW = 48 * 60 * MINUTE


def _d(value: Any, label: str = "value") -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception as exc:
        raise NativeEvidenceError(f"{label} must be numeric") from exc
    if not result.is_finite():
        raise NativeEvidenceError(f"{label} must be finite")
    return result


def _canonical_manifest(root: Path) -> dict[str, Mapping[str, Any]]:
    """Load unique canonical physical membership from CSV or Parquet."""
    directory = root / "manifests"
    rows: list[Mapping[str, Any]] = []
    csv_path = directory / "files.csv"
    parquet_path = directory / "files.parquet"
    if parquet_path.is_file():
        try:
            import pyarrow.parquet as pq
            rows = pq.read_table(parquet_path).to_pylist()
        except Exception as exc:
            raise NativeEvidenceError("cannot read canonical files.parquet") from exc
    elif csv_path.is_file():
        try:
            with csv_path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
        except (OSError, csv.Error) as exc:
            raise NativeEvidenceError("cannot read canonical files.csv") from exc
    else:
        raise NativeEvidenceError("canonical file manifest is required for empirical tape")
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        relative = str(row.get("archive_path") or "").replace("\\", "/")
        if relative:
            grouped[relative].append(row)
    duplicates = [path for path, members in grouped.items() if len(members) != 1]
    if duplicates:
        raise NativeEvidenceError("duplicate canonical file ownership")
    return {path: members[0] for path, members in grouped.items()}


def _frozen_index(frozen_inputs: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
                  dataset: str) -> dict[str, Mapping[str, Any]] | None:
    if frozen_inputs is None:
        return None
    value: Any = frozen_inputs
    if isinstance(value, Mapping):
        if "path" in value and "sha256" in value:
            value = [value]
        elif "files" in value:
            if value.get("dataset_id") not in {None, dataset}:
                raise NativeEvidenceError("frozen tape dataset identity mismatch")
            value = value["files"]
        elif "input_identities" in value:
            value = [row for row in value["input_identities"]
                     if row.get("dataset_id") == dataset]
        else:
            value = list(value.values())
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise NativeEvidenceError("frozen inputs must contain file identities")
    result: dict[str, Mapping[str, Any]] = {}
    for row in value:
        if not isinstance(row, Mapping) or row.get("dataset_id") not in {None, dataset}:
            continue
        path = str(row.get("path", row.get("source_file", ""))).replace("\\", "/")
        digest = row.get("sha256")
        if not path or not isinstance(digest, str) or len(digest) != 64:
            raise NativeEvidenceError("frozen input lacks path/full sha256")
        if row.get("hash_basis") not in {None, "full_file_sha256"}:
            raise NativeEvidenceError("frozen input is not a full-file hash")
        if path in result:
            raise NativeEvidenceError("duplicate frozen input identity")
        result[path] = row
    if not result:
        raise NativeEvidenceError("frozen inputs omit requested dataset")
    return result


@dataclass(frozen=True)
class NativeFileIdentity:
    path: str
    dataset_id: str
    sha256: str
    bytes: int
    hash_basis: str = "full_file_sha256"
    canonical_owner: str = "canonical_manifest"


class NativeTradeStream:
    """Single-use bounded iterator with immutable physical source identities."""

    def __init__(self, data_root: Path | str, dataset: str, start: int, end: int,
                 instrument_id: int | str,
                 *, frozen_inputs: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None):
        self.root = Path(data_root).resolve()
        self.dataset = str(dataset)
        self.start = ns(start, "start")
        self.end = ns(end, "end")
        if self.end <= self.start or instrument_id is None:
            raise NativeEvidenceError("positive identified tape interval required")
        if self.end - self.start > MAX_TAPE_WINDOW:
            raise NativeEvidenceError("empirical tape window exceeds bounded 48-hour batch")
        if "trades" not in self.dataset and "mbp-1" not in self.dataset:
            raise NativeEvidenceError("empirical tape requires native trades or MBP-1")
        self.instrument_id = instrument_id
        directory = (self.root / self.dataset).resolve()
        if not directory.is_relative_to(self.root) or not directory.is_dir():
            raise NativeEvidenceError("native tape dataset is absent or escapes data root")
        canonical = _canonical_manifest(self.root)
        frozen = _frozen_index(frozen_inputs, self.dataset)
        candidates: list[tuple[Path, list[tuple[int, int]], NativeFileIdentity]] = []
        for path in sorted(directory.iterdir()):
            if path.suffix.lower() not in {".parquet", ".json", ".jsonl", ".csv", ".tsv"}:
                continue
            ranges = _group_ranges(path, self.dataset, self.start, self.end)
            if not ranges:
                continue
            relative = path.relative_to(self.root).as_posix()
            owner = canonical.get(relative)
            if owner is None:
                raise NativeEvidenceError(f"tape file is absent from canonical manifest: {relative}")
            declared = owner.get("bytes")
            if declared not in {None, ""}:
                try:
                    if int(declared) != path.stat().st_size:
                        raise NativeEvidenceError(f"canonical tape size changed: {relative}")
                except (TypeError, ValueError) as exc:
                    raise NativeEvidenceError("canonical tape byte count is invalid") from exc
            signature = _stat_signature(path)
            digest = file_digest(path)
            if _stat_signature(path) != signature:
                raise NativeEvidenceError("native tape changed while hashing")
            if frozen is not None:
                frozen_row = frozen.get(relative)
                if frozen_row is None or frozen_row["sha256"] != digest:
                    raise NativeEvidenceError(f"native tape differs from frozen manifest: {relative}")
                frozen_bytes = frozen_row.get("bytes")
                if frozen_bytes not in {None, ""}:
                    try:
                        if int(frozen_bytes) != path.stat().st_size:
                            raise NativeEvidenceError(f"native tape size differs from frozen manifest: {relative}")
                    except (TypeError, ValueError) as exc:
                        raise NativeEvidenceError("frozen tape byte count is invalid") from exc
            identity = NativeFileIdentity(relative, self.dataset, digest,
                                          path.stat().st_size)
            candidates.append((path, ranges, identity))
        if frozen is not None:
            used = {identity.path for _, _, identity in candidates}
            # Frozen manifests often include whole lookback files.  Every file
            # that can intersect this exact interval must be used; nonoverlap
            # identities remain frozen inputs but are not tape members.
            absent = [path for path in used if path not in frozen]
            if absent:
                raise NativeEvidenceError("intersecting native file omitted from frozen manifest")
        if not candidates:
            raise NativeEvidenceError("no canonical native tape file overlaps requested interval")
        self._candidates = tuple(candidates)
        self.file_identities = tuple(identity for _, _, identity in candidates)
        self._used = False
        self.row_count = 0
        self.physical_members: list[dict[str, Any]] = []

    def __iter__(self) -> Iterator[Mapping[str, Any]]:
        if self._used:
            raise NativeEvidenceError("native trade stream is single-use")
        self._used = True
        previous_time: int | None = None
        for path, ranges, identity in self._candidates:
            signature = _stat_signature(path)
            run: list[int] | None = None
            for index, raw in _selected_source_rows(path, self.dataset, ranges):
                normalize = (adapters.normalize_mbp1_row if "mbp-1" in self.dataset
                             else adapters.normalize_trade_row)
                row = normalize(raw, dataset_id=self.dataset,
                                source_file=str(path), source_row=index)
                if row.get("action") != "T":
                    continue
                at = row.get("event_ns")
                if at is None or at < self.start or at >= self.end:
                    continue
                if str(row.get("instrument_id")) != str(self.instrument_id):
                    continue
                if previous_time is not None and at < previous_time:
                    raise NativeEvidenceError("canonical tape is out of chronological order")
                previous_time = at
                for key in ("price",):
                    value = row.get(key)
                    if value is None or not value.is_finite():
                        raise NativeEvidenceError("native execution lacks finite price")
                size = row.get("executed_size", row.get("size"))
                if type(size) is not int or size < 0:
                    raise NativeEvidenceError("native execution lacks nonnegative integer size")
                row["dataset_id"] = self.dataset
                if run is not None and run[1] == index:
                    run[1] += 1
                else:
                    run = [index, index + 1]
                    self.physical_members.append({
                        "source_file": identity.path,
                        "dataset_id": self.dataset,
                        "sha256": identity.sha256,
                        "row_start": index,
                        "row_end": index + 1,
                    })
                self.physical_members[-1]["row_end"] = run[1]
                self.row_count += 1
                yield row
            if _stat_signature(path) != signature:
                raise NativeEvidenceError("native tape changed while streaming")


def stream_native_trades(data_root: Path | str, dataset: str, start: int, end: int,
                         instrument_id: int | str, *, frozen_inputs=None) -> NativeTradeStream:
    """Return a bounded stream of accepted normalized native executions."""
    return NativeTradeStream(data_root, dataset, start, end, instrument_id,
                             frozen_inputs=frozen_inputs)


def _stream_ohlcv(root: Path, dataset: str, start: int, end: int,
                  instrument_id: int | str, *, frozen_inputs=None):
    canonical = _canonical_manifest(root)
    frozen = _frozen_index(frozen_inputs, dataset) if frozen_inputs is not None else None
    directory = (root / dataset).resolve()
    if not directory.is_dir() or not directory.is_relative_to(root):
        return [], [], []
    bars, identities, locators = [], [], []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in {".parquet", ".json", ".jsonl", ".csv", ".tsv"}:
            continue
        ranges = _group_ranges(path, dataset, start, end)
        if not ranges:
            continue
        relative = path.relative_to(root).as_posix()
        owner = canonical.get(relative)
        if owner is None:
            raise NativeEvidenceError("OHLCV corroborating file is not canonical")
        declared = owner.get("bytes")
        if declared not in {None, ""} and int(declared) != path.stat().st_size:
            raise NativeEvidenceError("canonical OHLCV size changed")
        signature = _stat_signature(path)
        digest = file_digest(path)
        if frozen is not None:
            frozen_row = frozen.get(relative)
            if frozen_row is None or frozen_row.get("sha256") != digest:
                raise NativeEvidenceError("OHLCV file differs from frozen manifest")
        identities.append(asdict(NativeFileIdentity(relative, dataset, digest,
                                                     path.stat().st_size)))
        indices = []
        for index, raw in _selected_source_rows(path, dataset, ranges):
            bar = adapters.normalize_ohlcv_row(raw, dataset_id=dataset,
                                               source_file=str(path), source_row=index)
            if bar["start"] < start or bar["end"] > end:
                continue
            if str(bar.get("instrument_id")) != str(instrument_id):
                continue
            bar["dataset_id"] = dataset
            bars.append(bar)
            indices.append(index)
        for index in indices:
            if locators and locators[-1]["source_file"] == relative and locators[-1]["row_end"] == index:
                locators[-1]["row_end"] += 1
            else:
                locators.append({"source_file": relative, "dataset_id": dataset,
                                 "sha256": digest, "row_start": index,
                                 "row_end": index + 1})
        if _stat_signature(path) != signature:
            raise NativeEvidenceError("OHLCV file changed while reconciling")
    bars.sort(key=lambda row: row["start"])
    return bars, identities, locators


def _value_area_tie_both(rows: Sequence[profiles.PriceRow], poc: Decimal | None,
                         fraction: Decimal):
    """M08's explicit comparison expansion: include both equal neighbors."""
    if not 0 < fraction <= 1:
        raise NativeEvidenceError("value-area fraction must be in (0,1]")
    if not rows or poc is None:
        return None, None, None, None
    total = sum((row.total_volume for row in rows), Decimal(0))
    if total <= 0:
        return None, None, None, None
    index = next(i for i, row in enumerate(rows) if row.price == poc)
    selected = {index}
    inside = rows[index].total_volume
    low, high = index - 1, index + 1
    while inside / total < fraction and (low >= 0 or high < len(rows)):
        low_volume = rows[low].total_volume if low >= 0 else None
        high_volume = rows[high].total_volume if high < len(rows) else None
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
            selected.add(item)
            inside += rows[item].total_volume
        if low in chosen:
            low -= 1
        if high in chosen:
            high += 1
    return (rows[min(selected)].price, rows[max(selected)].price,
            inside, inside / total)


def _profile_payload(accum: Mapping[Decimal, Sequence[Decimal]], *, tick: Decimal,
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
        "rows": [asdict(row) for row in rows],
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


def load_tape_session(data_root: Path | str, dataset: str, start: int, end: int,
                      instrument_id: int | str, *, frozen_inputs=None,
                      ohlcv_dataset: str | None = None, tick_size: Any = None,
                      profile_kind: str = "selected_range",
                      session_date: str | None = None,
                      value_area_fraction: Any = None,
                      value_area_tie_policy: str = "lower",
                      poc_tie_policy: str | None = None) -> dict[str, Any]:
    """Aggregate one bounded tape window and independently audit its clock.

    The returned mapping is serializable through the method-pack ``jsonable``
    adapter and is suitable as the actual evidence envelope for previous-session
    profiles (M06/M08) and executed five-minute delta snapshots (M06).
    ``known_at`` is the maximum
    native member availability and never precedes ``formation_end``.
    """
    root = Path(data_root).resolve()
    start, end = ns(start, "start"), ns(end, "end")
    if profile_kind not in profiles.PROFILE_KINDS - {"composite"}:
        raise NativeEvidenceError("unsupported empirical profile kind")
    if session_date is not None:
        try:
            from datetime import date
            session_date = date.fromisoformat(str(session_date)).isoformat()
        except ValueError as exc:
            raise NativeEvidenceError("profile session_date must be ISO civil date") from exc
    stream = stream_native_trades(root, dataset, start, end, instrument_id,
                                  frozen_inputs=frozen_inputs)
    resolver = NativeResolver(root)
    definition = resolver._definition(instrument_id, [dataset], end)
    if tick_size is None:
        if definition is None:
            raise NativeEvidenceError("native instrument definition/tick is required")
        if definition.known_at is None:
            raise NativeEvidenceError("native instrument definition availability is unknown")
        definition_path = Path(definition.source_file).resolve()
        definition_relative = definition_path.relative_to(root).as_posix()
        canonical_definition = _canonical_manifest(root).get(definition_relative)
        if canonical_definition is None:
            raise NativeEvidenceError("native instrument definition is not canonical")
        declared = canonical_definition.get("bytes")
        if declared not in {None, ""} and int(declared) != definition_path.stat().st_size:
            raise NativeEvidenceError("canonical instrument definition size changed")
        if frozen_inputs is not None:
            supplied = _frozen_index(
                frozen_inputs, "derived/continuous-futures__instrument-and-roll-maps")
            frozen_definition = supplied.get(definition_relative)
            if frozen_definition is None or frozen_definition.get("sha256") != definition.sha256:
                raise NativeEvidenceError("instrument definition differs from frozen manifest")
        tick = definition.tick_size
        definition_identity = {
            "definition_id": definition.definition_id,
            "source_file": definition_relative,
            "sha256": definition.sha256,
            "known_at": definition.known_at,
        }
    else:
        # Explicit tick injection exists for disposable tests only; production
        # callers should resolve the frozen native definition.
        tick = _d(tick_size, "tick_size")
        definition_identity = None
    profile_accum: dict[Decimal, list[Decimal]] = {}
    minute_accum: dict[int, dict[str, Any]] = {}
    membership = sha256()
    known_at = end
    for row in stream:
        price = _d(row["price"], "price")
        size = Decimal(row["executed_size"])
        side = str(row.get("side") or "").upper()
        if side not in profiles.SIDE_CODES:
            raise NativeEvidenceError("canonical execution side must be B, A, or N")
        bucket = profile_accum.setdefault(price, [Decimal(0), Decimal(0), Decimal(0)])
        bucket[{"B": 0, "A": 1, "N": 2}[side]] += size
        minute = (row["event_ns"] // MINUTE) * MINUTE
        agg = minute_accum.setdefault(minute, {
            "minute_start": minute, "minute_end": minute + MINUTE,
            "buy_volume": Decimal(0), "sell_volume": Decimal(0),
            "unknown_volume": Decimal(0), "trade_count": 0,
            "high": None, "low": None, "first_ns": row["event_ns"],
            "last_ns": row["event_ns"], "opening_prices": set(),
            "closing_prices": set(), "first_count": 0, "last_count": 0,
            "known_at": minute + MINUTE,
        })
        agg[{"B": "buy_volume", "A": "sell_volume", "N": "unknown_volume"}[side]] += size
        agg["trade_count"] += 1
        agg["high"] = price if agg["high"] is None else max(agg["high"], price)
        agg["low"] = price if agg["low"] is None else min(agg["low"], price)
        if row["event_ns"] == agg["first_ns"]:
            agg["opening_prices"].add(price)
            agg["first_count"] += 1
        elif row["event_ns"] < agg["first_ns"]:
            agg["first_ns"], agg["opening_prices"] = row["event_ns"], {price}
            agg["first_count"] = 1
        if row["event_ns"] == agg["last_ns"]:
            agg["closing_prices"].add(price)
            agg["last_count"] += 1
        elif row["event_ns"] > agg["last_ns"]:
            agg["last_ns"], agg["closing_prices"] = row["event_ns"], {price}
            agg["last_count"] = 1
        if row.get("known_at") is None:
            raise NativeEvidenceError("native execution availability is unknown")
        agg["known_at"] = max(agg["known_at"], row["known_at"])
        known_at = max(known_at, row["known_at"])
        membership.update(json.dumps(jsonable({
            "file": Path(row["source_file"]).resolve().relative_to(root).as_posix(),
            "sha256": next(identity.sha256 for identity in stream.file_identities
                           if identity.path == Path(row["source_file"]).resolve().relative_to(root).as_posix()),
            "row": row["source_row"], "instrument_id": row["instrument_id"],
            "event_ns": row["event_ns"], "price": row["price"],
            "size": row["executed_size"], "side": side,
        }), sort_keys=True, separators=(",", ":")).encode())
        membership.update(b"\n")

    ohlcv_dataset = ohlcv_dataset or dataset.rsplit("__", 1)[0] + "__ohlcv-1m"
    frozen_ohlcv = frozen_inputs
    bars, bar_identities, bar_locators = _stream_ohlcv(
        root, ohlcv_dataset, start, end, instrument_id,
        frozen_inputs=frozen_ohlcv)
    bar_index: dict[int, Mapping[str, Any]] = {}
    mismatches: list[dict[str, Any]] = []
    for bar in bars:
        if bar["start"] in bar_index:
            mismatches.append({"minute_start": bar["start"],
                               "reason": "duplicate_native_minute"})
        else:
            bar_index[bar["start"]] = bar
        if (bar.get("complete") is not True or bar.get("V") is None or bar["V"] < 0
                or bar["H"] < max(bar["O"], bar["L"], bar["C"])
                or bar["L"] > min(bar["O"], bar["H"], bar["C"])):
            mismatches.append({"minute_start": bar["start"],
                               "reason": "invalid_native_ohlcv"})
    missing: list[list[int]] = []
    reconciliation: list[dict[str, Any]] = []
    if start % MINUTE or end % MINUTE:
        mismatches.append({"reason": "partial_minute_window_not_independently_verifiable"})
    for minute in range(start, end, MINUTE):
        bar = bar_index.get(minute)
        if bar is None or bar.get("complete") is not True or bar.get("end") != minute + MINUTE:
            missing.append([minute, min(minute + MINUTE, end)])
            continue
        agg = minute_accum.get(minute)
        volume = Decimal(0) if agg is None else agg["buy_volume"] + agg["sell_volume"] + agg["unknown_volume"]
        reasons = []
        if volume != bar["V"]:
            reasons.append("executed_volume_mismatch")
        if agg is not None:
            if agg["high"] != bar["H"] or agg["low"] != bar["L"]:
                reasons.append("trade_high_low_mismatch")
            if bar["O"] not in agg["opening_prices"] or bar["C"] not in agg["closing_prices"]:
                reasons.append("trade_open_close_mismatch")
        elif bar["V"] != 0:
            reasons.append("no_executed_trades_for_active_minute")
        check = {"minute_start": minute,
                 "executed_volume": volume, "ohlcv_volume": bar["V"],
                 "trade_count": 0 if agg is None else agg["trade_count"],
                 "matched": not reasons,
                 "endpoint_order": "no_executions" if agg is None else
                 "unique_timestamp" if agg["first_count"] == 1 and agg["last_count"] == 1
                 else "unknown_order"}
        reconciliation.append(check)
        mismatches.extend({"minute_start": minute, "reason": reason} for reason in reasons)
    coverage_ok = True if bars and not missing and not mismatches else None
    minutes = []
    for minute in range(start, end, MINUTE):
        agg = minute_accum.get(minute)
        if agg is None:
            matched_zero = (minute in bar_index and bar_index[minute].get("complete") is True
                            and bar_index[minute]["V"] == 0)
            minutes.append({
                "minute_start": minute, "minute_end": min(minute + MINUTE, end),
                "known_at": min(minute + MINUTE, end), "instrument_id": instrument_id,
                "buy_volume": Decimal(0), "sell_volume": Decimal(0),
                "unknown_volume": Decimal(0), "known_volume": Decimal(0),
                "total_volume": Decimal(0), "known_delta": Decimal(0),
                "delta": Decimal(0) if matched_zero else None,
                "delta_low": Decimal(0), "delta_high": Decimal(0),
                "trade_count": 0, "coverage_ok": True if matched_zero else None,
            })
            continue
        known_delta = agg["buy_volume"] - agg["sell_volume"]
        unknown = agg["unknown_volume"]
        minute_matched = any(row["minute_start"] == minute and row["matched"]
                             for row in reconciliation)
        minutes.append({
            "minute_start": minute, "minute_end": minute + MINUTE,
            "known_at": agg["known_at"], "instrument_id": instrument_id,
            "buy_volume": agg["buy_volume"], "sell_volume": agg["sell_volume"],
            "unknown_volume": unknown,
            "known_volume": agg["buy_volume"] + agg["sell_volume"],
            "total_volume": agg["buy_volume"] + agg["sell_volume"] + unknown,
            "known_delta": known_delta,
            "delta": known_delta if unknown == 0 else None,
            "delta_low": known_delta - unknown,
            "delta_high": known_delta + unknown,
            "trade_count": agg["trade_count"],
            "coverage_ok": True if minute_matched else None,
        })
    va = None
    if value_area_fraction is not None:
        if value_area_tie_policy == "both":
            va = {"fraction": _d(value_area_fraction),
                  "algorithm": "contiguous_larger_adjacent_volume_tie_both",
                  "tie_policy": "both"}
        else:
            va = profiles.ValueAreaConfig(
                "empirical-native-va", _d(value_area_fraction), "adjacent_single",
                value_area_tie_policy)
    profile = _profile_payload(profile_accum, tick=tick,
                               tie_policy=poc_tie_policy, value_area=va,
                               complete=coverage_ok)
    profile.update({
        "profile_id": f"native:{instrument_id}:{start}:{end}",
        "snapshot_id": f"native:{instrument_id}:{end}:{membership.hexdigest()[:16]}",
        "kind": profile_kind, "session_date": session_date,
        "instrument_id": instrument_id, "tick_size": tick,
        "poc_tie_policy": poc_tie_policy,
        "formation_start": start, "formation_end": end,
        "as_of": end, "known_at": known_at,
        "coverage": {"state": "complete" if coverage_ok is True else "unavailable",
                     "ok": coverage_ok,
                     "holes": [] if coverage_ok is True else ["HOLE:native_tape_coverage"]},
        "profile_definition": {
            "kind": profile_kind, "session_date": session_date,
            "formation_start": start, "formation_end": end,
            "poc_tie_policy": poc_tie_policy,
            "value_area_fraction": None if va is None else _d(value_area_fraction),
            "value_area_algorithm": None if va is None else
                "contiguous_larger_adjacent_volume_tie_both" if isinstance(va, Mapping)
                else va.algorithm,
            "value_area_tie_policy": None if va is None else
                "both" if isinstance(va, Mapping) else va.tie_policy,
        },
    })
    window_buy = sum((row["buy_volume"] for row in minutes), Decimal(0))
    window_sell = sum((row["sell_volume"] for row in minutes), Decimal(0))
    window_unknown = sum((row["unknown_volume"] for row in minutes), Decimal(0))
    window_delta = window_buy - window_sell
    source_files = [asdict(identity) for identity in stream.file_identities]
    input_identity = {
        "dataset_id": dataset, "instrument_id": instrument_id,
        "formation_start": start, "formation_end": end,
        "membership_sha256": membership.hexdigest(),
        "source_files": source_files,
        "corroborating_source_files": bar_identities,
        "instrument_definition": definition_identity,
    }
    return {
        "schema": "phase1-empirical-tape-session-v1",
        "dataset_id": dataset, "instrument_id": instrument_id,
        "formation_start": start, "formation_end": end, "known_at": known_at,
        "row_count": stream.row_count,
        "membership_sha256": membership.hexdigest(),
        "evidence_sha256": content_hash(input_identity),
        "raw_member_locators": stream.physical_members,
        "source_files": source_files,
        "instrument_definition": definition_identity,
        "profile": profile,
        "minutes": minutes,
        "flow": {
            "formation_start": start, "formation_end": end, "known_at": known_at,
            "buy_volume": window_buy, "sell_volume": window_sell,
            "unknown_volume": window_unknown,
            "known_volume": window_buy + window_sell,
            "total_volume": window_buy + window_sell + window_unknown,
            "known_delta": window_delta,
            "delta": window_delta if window_unknown == 0 else None,
            "delta_low": window_delta - window_unknown,
            "delta_high": window_delta + window_unknown,
            "coverage_ok": coverage_ok,
        },
        "coverage": {
            "coverage_ok": coverage_ok,
            "coverage_reason": "verified" if coverage_ok is True else
                               "missing_native_intervals" if missing else
                               "cross_source_reconciliation_mismatch",
            "method": "all_native_rows_plus_independent_minute_volume_ohlc_reconciliation",
            "missing_intervals": missing,
            "mismatches": mismatches,
            "reconciliation": reconciliation,
            "corroborating_source_files": bar_identities,
            "corroborating_member_locators": bar_locators,
            "native_minute_count": len(bar_index),
        },
    }


@dataclass(frozen=True)
class M09Zone:
    zone_id: str
    instrument_id: int | str
    aggressor: str
    side: str
    low: Decimal
    high: Decimal
    formed_at: int
    known_at: int
    expires_at: int
    formation_event_ids: tuple[str, str]

    def reference(self) -> dict[str, Any]:
        return {"reference_id": self.zone_id, "instrument_id": self.instrument_id,
                "known_at": self.known_at, "low": self.low, "high": self.high,
                "aggressor": self.aggressor, "formation_event_ids": list(self.formation_event_ids),
                "formed_at": self.formed_at, "expires_at": self.expires_at,
                "immutable": True}


def _validate_m09_trade(row: Mapping[str, Any], instrument_id: int | str,
                        tick: Decimal) -> None:
    if str(row.get("instrument_id")) != str(instrument_id):
        raise NativeEvidenceError("M09 tape contains a foreign instrument")
    if row.get("action") != "T" or row.get("event_ns") is None or row.get("known_at") is None:
        raise NativeEvidenceError("M09 requires timestamped native executions")
    if row["known_at"] < row["event_ns"]:
        raise NativeEvidenceError("M09 execution availability precedes event")
    price = _d(row.get("price"), "M09 price")
    if price / tick != (price / tick).to_integral_value():
        raise NativeEvidenceError("M09 price is off the native tick grid")


def _m09_opportunity(zone: M09Zone, touch: Mapping[str, Any], *, rule: Mapping[str, Any],
                     partition: Mapping[str, Any], registry_sha256: str,
                     opportunity_index: int, expiry_at: int) -> Opportunity:
    event = touch["event_ns"]
    identity = {"rule_id": rule["rule_id"], "registry_sha256": registry_sha256,
                "partition_id": partition["partition_id"], "zone_id": zone.zone_id,
                "touch_event_id": touch["event_id"], "opportunity_index": opportunity_index}
    available = max(event + 1, touch["known_at"])
    trigger = {"event_id": touch["event_id"], "instrument_id": zone.instrument_id,
               "event_ns": event, "known_at": available,
               "price": touch["price"], "size": touch["executed_size"],
               "zone_id": zone.zone_id}
    if touch.get("member_event_ids") is not None:
        trigger["member_event_ids"] = list(touch["member_event_ids"])
        trigger["prices"] = list(touch["prices"])
    session_date = partition.get("session_date", partition.get("date"))
    return Opportunity(
        opportunity_id="opp-" + content_hash(identity)[:24],
        rule_id=rule["rule_id"], method_id="REFILL-STUDY", branch="touch_record",
        partition_id=partition["partition_id"], instrument_id=zone.instrument_id,
        session_date=session_date, side=zone.side,
        occurrence_start=event, occurrence_end=event + 1,
        available_at=available,
        reference_id=zone.zone_id, reference_known_at=zone.known_at,
        reference=zone.reference(), trigger=trigger,
        expiry_at=max(available, expiry_at),
        assumption_ids=tuple(rule["assumption_ids"]),
        registry_sha256=registry_sha256,
        observation_unit=rule.get("transport_observation_unit", "zone_touch"),
    ).validate()


def m09_research_comparison(trades: Iterable[Mapping[str, Any]], *,
                            rule: Mapping[str, Any], partition: Mapping[str, Any],
                            registry_sha256: str, tick_size: Any,
                            coverage_ok: bool | None,
                            session_end: int | None = None) -> dict[str, Any]:
    """Run the frozen M09 large-execution-zone comparison in one pass.

    Qualifying formations use non-overlapping chronological pairs.  A pair at
    one timestamp has no knowable second event and is retained as an ambiguous
    formation diagnostic.  Equal-timestamp response endpoints are evaluated as
    a batch; competing target/trade-through observations produce ``unknown``.
    """
    if rule.get("method_id") != "REFILL-STUDY" or rule.get("branch") != "touch_record":
        raise ValueError("M09 comparison requires the frozen touch_record rule")
    if rule.get("evidence_mode") != "research_comparison" or not rule.get("assumption_ids"):
        raise ValueError("M09 comparison lacks explicit research assumptions")
    tick = _d(tick_size, "tick_size")
    if tick <= 0:
        raise ValueError("M09 comparison requires a positive native tick")
    if coverage_ok not in {True, None}:
        raise ValueError("M09 coverage must be independently verified or unknown")
    if not isinstance(registry_sha256, str) or len(registry_sha256) != 64:
        raise ValueError("M09 comparison lacks frozen registry identity")
    params = rule.get("parameters", {})
    if int(params.get("min_events", 2)) != 2:
        raise ValueError("M09 frozen formation requires exactly two qualifying events")
    minimum = int(params.get("min_event_quantity", 100))
    formation_ns = int(params.get("formation_seconds", 120)) * SECOND
    span = _d(params.get("span_ticks", 2)) * tick
    departure = _d(params.get("departure_ticks", 4)) * tick
    response = _d(params.get("response_ticks", 4)) * tick
    horizon = int(params.get("horizon_minutes", 15)) * MINUTE
    instrument_id = partition["instrument_id"]
    if session_end is None:
        session_end = partition.get("session", {}).get("end_ns")
    if type(session_end) is not int:
        raise ValueError("M09 comparison requires an explicit session end")

    pending: dict[str, Mapping[str, Any] | None] = {"buy": None, "sell": None}
    zones: list[dict[str, Any]] = []
    opportunities: list[Opportunity] = []
    results: dict[str, ReplayResult] = {}
    ambiguities: list[dict[str, Any]] = []
    seen_members: set[tuple[str, int]] = set()
    previous_ns: int | None = None
    group: list[Mapping[str, Any]] = []

    def process(batch: list[Mapping[str, Any]]) -> None:
        if not batch:
            return
        stamp = batch[0]["event_ns"]
        if stamp >= session_end:
            return
        # Resolve already active response paths from the whole timestamp batch.
        prices = [_d(row["price"]) for row in batch]
        for opportunity in opportunities:
            if opportunity.opportunity_id in results or stamp < opportunity.available_at:
                continue
            zone = next(item["zone"] for item in zones
                        if item["zone"].zone_id == opportunity.reference_id)
            if stamp > opportunity.expiry_at:
                continue
            target = (zone.high + response if zone.side == "long" else zone.low - response)
            adverse = (zone.low - response if zone.side == "long" else zone.high + response)
            reached = any(price >= target for price in prices) if zone.side == "long" else any(price <= target for price in prices)
            failed = any(price <= adverse for price in prices) if zone.side == "long" else any(price >= adverse for price in prices)
            if reached or failed:
                endpoint_known = max(row["known_at"] for row in batch)
                if endpoint_known > opportunity.expiry_at:
                    results[opportunity.opportunity_id] = ReplayResult(
                        opportunity.opportunity_id, "unknown", opportunity.expiry_at,
                        None, "endpoint_available_after_horizon", censored=True,
                    ).validate(opportunity)
                    continue
                endpoint = {"instrument_id": instrument_id, "known_at": endpoint_known,
                            "event_ns": stamp, "prices": prices,
                            "zone_id": zone.zone_id, "target": target,
                            "opposite_trade_through": adverse,
                            "timestamp_order": "unknown_order" if len(batch) > 1 else "unique_timestamp"}
                if reached and failed:
                    results[opportunity.opportunity_id] = ReplayResult(
                        opportunity.opportunity_id, "unknown", endpoint_known, endpoint,
                        "same_timestamp_competing_outcomes", ambiguous=True).validate(opportunity)
                else:
                    passed = reached
                    results[opportunity.opportunity_id] = ReplayResult(
                        opportunity.opportunity_id, "pass" if passed else "fail", endpoint_known,
                        endpoint, "formation_side_displacement" if passed else
                        "opposite_edge_trade_through",
                        selected_signal_at=endpoint_known if passed else None).validate(opportunity)

        # Existing immutable zones advance departure/return lifecycle.
        for state in zones:
            zone: M09Zone = state["zone"]
            if stamp <= zone.formed_at or stamp < zone.known_at:
                continue
            departed = (any(price >= zone.high + departure for price in prices)
                        if zone.side == "long" else
                        any(price <= zone.low - departure for price in prices))
            if not state["armed"]:
                if departed:
                    state["armed"] = True
                    state["departed_at"] = stamp
                continue
            touched_rows = [row for row in batch if zone.low <= _d(row["price"]) <= zone.high]
            if touched_rows:
                if len(touched_rows) > 1 and all(row.get("exchange_sequence") is None for row in touched_rows):
                    member_ids = sorted(row["event_id"] for row in touched_rows)
                    touch = {
                        "event_id": "touch-batch-" + content_hash(member_ids)[:24],
                        "instrument_id": instrument_id, "event_ns": stamp,
                        "known_at": max(row["known_at"] for row in touched_rows),
                        "price": min(_d(row["price"]) for row in touched_rows),
                        "prices": [_d(row["price"]) for row in touched_rows],
                        "executed_size": sum(row["executed_size"] for row in touched_rows),
                        "member_event_ids": member_ids,
                    }
                    ambiguities.append({"zone_id": zone.zone_id, "event_ns": stamp,
                                        "reason": "multiple_same_timestamp_return_members",
                                        "member_ids": member_ids})
                else:
                    touch = min(touched_rows, key=lambda row: (
                        row.get("exchange_sequence") is None,
                        row.get("exchange_sequence") or 0, str(row["event_id"])))
                expiry = min(stamp + horizon, session_end)
                opp = _m09_opportunity(zone, touch, rule=rule, partition=partition,
                                       registry_sha256=registry_sha256,
                                       opportunity_index=state["touch_count"],
                                       expiry_at=expiry)
                opportunities.append(opp)
                state["touch_count"] += 1
                state["armed"] = False
                state["departed_at"] = None

        # Form new zones after existing lifecycle processing, so the formation
        # batch cannot also serve as its own departure or return.
        by_side = {"buy": [], "sell": []}
        for row in batch:
            aggressor = row.get("aggressor")
            if aggressor in by_side and row["executed_size"] >= minimum:
                by_side[aggressor].append(row)
        for aggressor, qualifying in by_side.items():
            if len(qualifying) > 1:
                ambiguities.append({
                    "event_ns": stamp, "aggressor": aggressor,
                    "reason": "same_timestamp_formation_order_unknown",
                    "member_ids": sorted(row["event_id"] for row in qualifying),
                    "skipped_member_count": len(qualifying),
                })
                # The entire same-side batch is excluded from formation.  A
                # previously pending strictly earlier event remains pending
                # until it ages out or a later singleton replaces/consumes it.
                continue
            for row in qualifying:
                first = pending[aggressor]
                if first is None or stamp - first["event_ns"] > formation_ns:
                    pending[aggressor] = row
                    continue
                lo, hi = sorted((_d(first["price"]), _d(row["price"])))
                if hi - lo <= span:
                    identity = {"instrument_id": instrument_id, "aggressor": aggressor,
                                "first": first["event_id"], "second": row["event_id"],
                                "formed_at": stamp, "low": lo, "high": hi}
                    zone = M09Zone("zone-" + content_hash(identity)[:24], instrument_id,
                                   aggressor, "long" if aggressor == "buy" else "short",
                                   lo, hi, stamp, max(first["known_at"], row["known_at"], stamp),
                                   session_end,
                                   (first["event_id"], row["event_id"]))
                    zones.append({"zone": zone, "armed": False,
                                  "departed_at": None, "touch_count": 0})
                    pending[aggressor] = None
                else:
                    pending[aggressor] = row

    for row in trades:
        _validate_m09_trade(row, instrument_id, tick)
        key = (str(row.get("source_file")), row.get("source_row"))
        if key in seen_members:
            raise NativeEvidenceError("duplicate physical execution in M09 denominator")
        seen_members.add(key)
        at = row["event_ns"]
        if previous_ns is not None and at < previous_ns:
            raise NativeEvidenceError("M09 tape is out of chronological order")
        if group and at != group[0]["event_ns"]:
            process(group)
            group = []
        group.append(row)
        previous_ns = at
    process(group)

    for opportunity in opportunities:
        if opportunity.opportunity_id in results:
            continue
        completion = min(opportunity.expiry_at, session_end)
        if coverage_ok is not True:
            results[opportunity.opportunity_id] = ReplayResult(
                opportunity.opportunity_id, "unknown", completion, None,
                "native_tape_coverage_unverified", censored=True).validate(opportunity)
        else:
            results[opportunity.opportunity_id] = ReplayResult(
                opportunity.opportunity_id, "fail", completion, None,
                "no_formation_side_response_before_horizon").validate(opportunity)
    records = [{"opportunity": opportunity.to_dict(),
                "replay": results[opportunity.opportunity_id].to_dict(opportunity)}
               for opportunity in opportunities]
    formation_ambiguities = [row for row in ambiguities
                             if row["reason"] == "same_timestamp_formation_order_unknown"]
    return {
        "schema": "phase1-m09-research-comparison-v1",
        "evidence_mode": "research_comparison", "faithful_eligible": False,
        "rule_id": rule["rule_id"], "registry_sha256": registry_sha256,
        "observation_unit": rule.get("observation_unit", "zone_return"),
        "transport_observation_unit": rule.get("transport_observation_unit", "zone_touch"),
        "instrument_id": instrument_id,
        "zones": [dict(jsonable(asdict(state["zone"])), immutable=True,
                       return_count=state["touch_count"]) for state in zones],
        "records": records, "ambiguities": ambiguities,
        "ambiguous_formation_batch_count": len(formation_ambiguities),
        "ambiguous_formation_event_count": sum(
            row["skipped_member_count"] for row in formation_ambiguities),
        "physical_member_count": len(seen_members),
        "coverage_ok": coverage_ok,
    }


__all__ = ["NativeFileIdentity", "NativeTradeStream", "M09Zone",
           "stream_native_trades", "load_tape_session", "m09_research_comparison"]
