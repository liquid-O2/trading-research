"""C03 acquired-data adapters and coverage inventory.

The adapters in this module are intentionally small and explicit about native
units.  QuantPad bars use UTC milliseconds; QuantPad trades and MBP-1 events
use UTC nanoseconds.  A missing optional dependency or manifest is reported as
an inventory hole instead of being replaced with a production assumption.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Iterator, Mapping, Sequence
from zoneinfo import ZoneInfo

from trading_research.foundations.time import datetime_ns
from trading_research.research.method_pack.logic import dec
from trading_research.research.method_pack.clocks import ns_to_et

DATA_ROOT_DEFAULT = Path("/workspace/data")
NS = 1_000_000_000
MS_NS = 1_000_000
DAY_NS = 86_400 * NS
I64_MIN = -(2**63)
I64_MAX = 2**63 - 1
ET_ZONE = ZoneInfo("America/New_York")

_PARTITION_SUFFIX = r"(?:parquet|csv|tsv|json|jsonl)"
MONTHLY_NAME = re.compile(rf"^(\d{{4}})-(\d{{2}})\.{_PARTITION_SUFFIX}$")
WEEKLY_NAME = re.compile(rf"^(\d{{4}})-(\d{{2}})-(\d{{2}})\.{_PARTITION_SUFFIX}$")
MBP1_RELATIVE = Path("quantpad/cme__nq-continuous-futures__mbp-1")
MBP1_REQUIRED = (
    "t",
    "action",
    "side",
    "price",
    "size",
    "bid_px",
    "ask_px",
    "bid_sz",
    "ask_sz",
    "instrument_id",
    "flags",
)


def _as_int(value: Any, *, field: str = "integer") -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} cannot be boolean")
    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if isinstance(value, float) and value != result:
        raise ValueError(f"{field} cannot lose fractional precision")
    if isinstance(value, Decimal) and value != result:
        raise ValueError(f"{field} cannot lose fractional precision")
    return result


def _checked_ns(value: Any) -> int:
    result = _as_int(value, field="timestamp")
    if not I64_MIN <= result <= I64_MAX:
        raise ValueError("timestamp is outside signed int64 nanoseconds")
    return result


def _text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def decode_aggressor(side: str | None) -> dict[str, Any]:
    """Decode Databento/QuantPad trade side (B buy, A sell, N unknown)."""

    code = _text(side)
    if code is None:
        return {"aggressor": "unknown", "sign": None, "known": False}
    code = code.upper()
    if code == "B":
        return {"aggressor": "buy", "sign": 1, "known": True}
    if code == "A":
        return {"aggressor": "sell", "sign": -1, "known": True}
    if code == "N":
        return {"aggressor": "unknown", "sign": None, "known": False}
    return {"aggressor": "unknown", "sign": None, "known": False}


def signed_size(side: str | None, size: int | None) -> dict[str, Any]:
    """Return signed/unknown executed size without interpreting book updates."""

    info = decode_aggressor(side)
    if size is None:
        return {**info, "signed": None, "unknown_size": None, "executed_size": None}
    executed = _as_int(size, field="size")
    if executed < 0:
        raise ValueError("trade size cannot be negative")
    if info["sign"] is None:
        return {
            **info,
            "signed": None,
            "unknown_size": executed,
            "executed_size": executed,
        }
    return {
        **info,
        "signed": info["sign"] * executed,
        "unknown_size": 0,
        "executed_size": executed,
    }


def is_trade_action(action: Any) -> bool:
    return (_text(action) or "").upper() == "T"


def native_timestamp_unit(dataset_id: str | None, field: str = "t") -> str | None:
    """Return the declared native unit for a known acquired dataset field."""

    dataset = (dataset_id or "").lower()
    field = field.lower()
    if "ohlcv-1m" in dataset or "ohlcv-1s" in dataset:
        return "ms" if field in {"t", "bar_start_ms"} else None
    # QuantPad definition rows are stored as timezone-naive int64 epoch
    # nanoseconds.  Keep this branch ahead of the generic continuous-futures
    # rule because bar datasets also contain a native ``t`` field, in ms.
    if "quantpad" in dataset and "definition" in dataset:
        if field in {"t", "ts_event", "ts_recv", "ts_ref", "activation", "expiration"}:
            return "ns"
    if "quantpad" in dataset and ("trades" in dataset or "mbp-1" in dataset):
        return "ns" if field in {"t", "ts_event", "ts_recv", "ts_ref"} else None
    if "databento" in dataset:
        return "ns" if field.startswith("ts_") or field in {"t", "ts_event"} else None
    if "thetadata" in dataset or "opra" in dataset:
        return "ns" if field.startswith("ts_") else None
    if "instrument-and-roll-maps" in dataset:
        if field.endswith("_ms") or field in {"first_bar_ms", "last_bar_ms", "segment_start_ms", "segment_end_exclusive_ms"}:
            return "ms"
        if field.endswith("_ns") or field in {"activation", "expiration", "first_definition_ns", "last_definition_ns"}:
            return "ns"
    return None


def timestamp_ns(value: Any, unit: str = "ns") -> int:
    """Convert an exact native timestamp to signed UTC nanoseconds."""

    unit = unit.lower()
    factors = {"ns": 1, "us": 1_000, "ms": MS_NS, "s": NS}
    if unit in factors:
        if isinstance(value, datetime):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("timestamp datetime must carry an explicit zone")
            return _checked_ns(datetime_ns(value.astimezone(timezone.utc)))
        if isinstance(value, str):
            # An ISO string carries its own calendar unit/precision.  The
            # native integer unit argument must not be applied a second time.
            text_value = value.strip()
            if re.fullmatch(r"[+-]?\d+", text_value):
                return _checked_ns(int(text_value) * factors[unit])
            return _checked_ns(_parse_iso_ns(text_value))
        return _checked_ns(_as_int(value, field="timestamp") * factors[unit])
    raise ValueError(f"unsupported timestamp unit {unit!r}")


def _parse_iso_ns(value: str, *, default_zone: timezone | ZoneInfo | None = None) -> int:
    """Parse an ISO-like timestamp while retaining up to nine digits.

    A naive value is accepted only when the caller supplies a documented
    source zone.  This keeps local-provider timestamps usable without turning
    an arbitrary wall clock into UTC by guesswork.
    """

    original = str(value).strip()
    text = original
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"invalid ISO timestamp {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        if default_zone is None:
            raise ValueError("ISO timestamp must carry an explicit zone")
        parsed = parsed.replace(tzinfo=default_zone)
    # datetime preserves six fractional digits. Parse the original suffix so
    # an inventory bound with up to nine digits remains exact. The fractional
    # part is independent of the offset sign, so a simple regex avoids
    # treating the ``-05:00`` offset as fractional digits.
    base = datetime_ns(parsed.astimezone(timezone.utc).replace(microsecond=0))
    match = re.search(r"\.(\d+)", original)
    digits = (match.group(1) if match else "")[:9].ljust(9, "0")
    return base + (int(digits) if digits else 0)


def bar_start_ns_from_ms(t_ms: int) -> int:
    """QuantPad OHLCV ``t`` is UTC milliseconds, with no price rescaling."""

    return timestamp_ns(t_ms, "ms")


def bar_end_ns_from_ms(t_ms: int, duration_ms: int = 60_000) -> int:
    duration = _as_int(duration_ms, field="duration_ms")
    if duration <= 0:
        raise ValueError("bar duration must be positive")
    return _checked_ns(bar_start_ns_from_ms(t_ms) + duration * MS_NS)


def _row_value(row: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in row:
            return row[name]
    return None


def _normalized_receive_timestamp(row: Mapping[str, Any], dataset_id: str) -> int | None:
    """Return a receive/ingest timestamp when the source actually supplies one.

    ``known_at`` is the later of the market event and the provider receive
    timestamp.  A missing receive field stays missing; using ``event_ns`` as a
    synthetic receive value would erase the distinction between exchange time
    and when the record became available to the consumer.
    """

    raw_recv = _row_value(
        row,
        "ts_recv",
        "recv_ns",
        "receive_ts",
        "received_ts",
        "received_at",
    )
    if raw_recv in (None, ""):
        return None
    unit = native_timestamp_unit(dataset_id, "ts_recv") or native_timestamp_unit(dataset_id, "t")
    if unit is None:
        unit = _field_unit("ts_recv")
    if isinstance(raw_recv, str) and not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", raw_recv.strip()):
        # ISO receive fields must carry a zone.  This is intentionally the
        # same conservative rule as event timestamps.
        parsed = _parse_explicit_timestamp(raw_recv, "ts_recv", dataset_id)
        if parsed is None:
            raise ValueError("provided receive timestamp is malformed or lacks a documented zone")
        return parsed
    if unit is None:
        raise ValueError("provided receive timestamp has no known native unit")
    try:
        numeric: Any = raw_recv
        if isinstance(raw_recv, str) and "." in raw_recv:
            numeric = Decimal(raw_recv)
        return timestamp_ns(numeric, unit)
    except (TypeError, ValueError, OverflowError, InvalidOperation) as exc:
        raise ValueError("provided receive timestamp is malformed") from exc


def _known_at(event_ns: int, recv_ns: int | None) -> int:
    """Compute causal availability without inventing a receive timestamp."""

    return event_ns if recv_ns is None else max(event_ns, recv_ns)


def _bar_id(source_file: str, source_row: int | None, instrument_id: Any) -> str:
    source = source_file or "<memory>"
    row = "?" if source_row is None else str(source_row)
    return f"{source}:{row}:{instrument_id if instrument_id is not None else '?'}"


def normalize_ohlcv_row(
    row: Mapping[str, Any],
    *,
    dataset_id: str = "quantpad/cme__nq-continuous-futures__ohlcv-1m",
    source_file: str = "",
    source_row: int | None = None,
    duration_ms: int | None = None,
) -> dict[str, Any]:
    """Normalize a QuantPad OHLCV row while retaining source precision."""

    timestamp_value = _row_value(row, "t", "bar_start_ms")
    if timestamp_value is None:
        raise ValueError("OHLCV row lacks native t/bar_start_ms")
    unit = native_timestamp_unit(dataset_id, "t")
    if unit is None:
        raise ValueError(f"unknown OHLCV timestamp unit for {dataset_id}")
    start_ns = timestamp_ns(timestamp_value, unit)
    if duration_ms is None:
        duration_ms = 1_000 if "ohlcv-1s" in dataset_id else 60_000
    duration_ms = _as_int(duration_ms, field="duration_ms")
    if duration_ms <= 0:
        raise ValueError("duration_ms must be positive")
    end_ns = bar_end_ns_from_ms(timestamp_value, duration_ms)
    instrument_id = _row_value(row, "instrument_id", "instrument")
    fields = {
        "O": _row_value(row, "O", "o", "open"),
        "H": _row_value(row, "H", "h", "high"),
        "L": _row_value(row, "L", "l", "low"),
        "C": _row_value(row, "C", "c", "close"),
        "V": _row_value(row, "V", "v", "volume"),
    }
    missing = [name for name, value in fields.items() if value is None]
    complete = not missing
    values = {name: (None if value is None else dec(value)) for name, value in fields.items()}
    return {
        "bar_id": _bar_id(source_file, source_row, instrument_id),
        "instrument_id": instrument_id,
        "kind": "time",
        "size": "1s" if duration_ms == 1_000 else "1m" if duration_ms == 60_000 else f"{duration_ms}ms",
        "start": start_ns,
        "end": end_ns,
        "O": values["O"],
        "H": values["H"],
        "L": values["L"],
        "C": values["C"],
        "V": values["V"],
        "volume": values["V"],
        "complete": complete,
        "coverage_state": "complete" if complete else "missing_field",
        "known_at": end_ns if complete else None,
        "source_precision": "milliseconds",
        "ordering_basis": "bar_clock",
        "source_file": source_file,
        "source_row": source_row,
        "raw_timestamp": timestamp_value,
        "missing_fields": missing,
    }


def normalize_trade_row(
    row: Mapping[str, Any],
    *,
    dataset_id: str = "quantpad/cme__nq-continuous-futures__trades",
    source_file: str = "",
    source_row: int | None = None,
) -> dict[str, Any]:
    """Normalize a standalone executed trade (all rows are executions)."""

    raw_t = _row_value(row, "t", "ts_event")
    if raw_t is None:
        raise ValueError("trade row lacks native event timestamp")
    unit = native_timestamp_unit(dataset_id, "t")
    if unit is None:
        raise ValueError(f"unknown trade timestamp unit for {dataset_id}")
    event_ns = timestamp_ns(raw_t, unit)
    instrument_id = _row_value(row, "instrument_id", "instrument")
    side = _text(_row_value(row, "side"))
    size_raw = _row_value(row, "size", "quantity")
    signed = signed_size(side, None if size_raw is None else size_raw)
    sequence = _row_value(row, "exchange_sequence", "sequence", "seq")
    recv_ns = _normalized_receive_timestamp(row, dataset_id)
    return {
        "event_id": _bar_id(source_file, source_row, instrument_id),
        "dataset_id": dataset_id,
        "source_file": source_file,
        "source_row": source_row,
        "instrument_id": instrument_id,
        "raw_symbol": _row_value(row, "raw_symbol", "symbol"),
        "root": _row_value(row, "root"),
        "event_ns": event_ns,
        "source_precision": "nanoseconds",
        "action": "T",
        "aggressor": signed["aggressor"],
        "side": side,
        "price": None if _row_value(row, "price") is None else dec(_row_value(row, "price")),
        "size": None if size_raw is None else _as_int(size_raw, field="size"),
        "signed_size": signed["signed"],
        "signed": signed["signed"],
        "unknown_size": signed["unknown_size"],
        "executed_size": signed["executed_size"],
        "bid": None if _row_value(row, "bid_px", "bid") is None else dec(_row_value(row, "bid_px", "bid")),
        "ask": None if _row_value(row, "ask_px", "ask") is None else dec(_row_value(row, "ask_px", "ask")),
        "bid_size": _row_value(row, "bid_sz", "bid_size"),
        "ask_size": _row_value(row, "ask_sz", "ask_size"),
        "flags": _row_value(row, "flags"),
        "ordering_basis": "exchange_sequence" if sequence is not None else "timestamp_only",
        "exchange_sequence": sequence,
        # Keep the optional receive clock visible.  ``None`` means the source
        # did not provide it; it is not equivalent to an event-time receive.
        "ts_recv": recv_ns,
        "recv_ns": recv_ns,
        "known_at": _known_at(event_ns, recv_ns),
    }


def normalize_mbp1_row(
    row: Mapping[str, Any],
    *,
    dataset_id: str = "quantpad/cme__nq-continuous-futures__mbp-1",
    source_file: str = "",
    source_row: int | None = None,
) -> dict[str, Any]:
    """Normalize one MBP-1 row; only action ``T`` contributes executed flow."""

    raw_t = _row_value(row, "t", "ts_event")
    if raw_t is None:
        raise ValueError("MBP-1 row lacks event timestamp")
    unit = native_timestamp_unit(dataset_id, "t")
    if unit is None:
        raise ValueError(f"unknown MBP-1 timestamp unit for {dataset_id}")
    event_ns = timestamp_ns(raw_t, unit)
    action = (_text(_row_value(row, "action")) or "").upper()
    side = _text(_row_value(row, "side"))
    size_raw = _row_value(row, "size")
    size = None if size_raw is None else _as_int(size_raw, field="size")
    if action == "T":
        signed = signed_size(side, size)
        aggressor = signed["aggressor"]
        signed_value = signed["signed"]
        unknown_size = signed["unknown_size"]
        executed_size = signed["executed_size"]
    else:
        # A/M/C side identifies the resting book side.  F is a fill message,
        # but it is not another T aggressor record for volume accounting.
        aggressor = "unknown"
        signed_value = None
        unknown_size = None
        executed_size = None
    sequence = _row_value(row, "exchange_sequence", "sequence", "seq")
    instrument_id = _row_value(row, "instrument_id", "instrument")
    recv_ns = _normalized_receive_timestamp(row, dataset_id)
    return {
        "event_id": _bar_id(source_file, source_row, instrument_id),
        "dataset_id": dataset_id,
        "source_file": source_file,
        "source_row": source_row,
        "instrument_id": instrument_id,
        "raw_symbol": _row_value(row, "raw_symbol", "symbol"),
        "root": _row_value(row, "root"),
        "event_ns": event_ns,
        "source_precision": "nanoseconds",
        "action": action,
        "is_trade": action == "T",
        "side": side,
        "resting_side": side if action != "T" else None,
        "aggressor": aggressor,
        "price": None if _row_value(row, "price") is None else dec(_row_value(row, "price")),
        "size": size,
        "signed_size": signed_value,
        "signed": signed_value,
        "unknown_size": unknown_size,
        "executed_size": executed_size,
        "bid": None if _row_value(row, "bid_px", "bid") is None else dec(_row_value(row, "bid_px", "bid")),
        "ask": None if _row_value(row, "ask_px", "ask") is None else dec(_row_value(row, "ask_px", "ask")),
        "bid_size": _row_value(row, "bid_sz", "bid_size"),
        "ask_size": _row_value(row, "ask_sz", "ask_size"),
        "flags": _row_value(row, "flags"),
        "ordering_basis": "exchange_sequence" if sequence is not None else "timestamp_only",
        "exchange_sequence": sequence,
        "ts_recv": recv_ns,
        "recv_ns": recv_ns,
        "known_at": _known_at(event_ns, recv_ns),
    }


def _flatten_schema(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        out: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, list):
                out.extend(_flatten_schema(item))
            elif isinstance(item, dict) and "name" in item:
                out.append(item)
        return out
    if isinstance(value, dict):
        return [value] if "name" in value else []
    return []


def _safe_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError, TypeError):
        return default


def _manifest_rows(data_root: Path) -> list[dict[str, str]]:
    path = data_root / "manifests" / "files.csv"
    if not path.is_file():
        return []
    try:
        with path.open(newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except (OSError, csv.Error):
        return []


def load_catalog(data_root: Path | str = DATA_ROOT_DEFAULT) -> dict[str, Any]:
    """Load whatever manifests exist below ``data_root``.

    A disposable fixture root may contain no manifests.  The returned empty
    collections are intentional and do not fall back to ``/workspace/data``.
    """

    root = Path(data_root)
    manifests = root / "manifests"
    catalog = _safe_json(manifests / "dataset-catalog.json", {})
    timestamps = _safe_json(manifests / "timestamp-conventions.json", {})
    schemas = _safe_json(manifests / "schema-catalog.json", {})
    exclusions = _safe_json(manifests / "exclusions-and-gaps.json", {})
    if not isinstance(catalog, dict):
        catalog = {}
    if not isinstance(timestamps, dict):
        timestamps = {}
    if not isinstance(schemas, dict):
        schemas = {}
    if not isinstance(exclusions, dict):
        exclusions = {}
    return {
        "data_root": str(root),
        "catalog": catalog,
        "timestamps": timestamps,
        "schemas": schemas,
        "exclusions": exclusions,
        "files": _manifest_rows(root),
        "archive_root_note": "resolve archive_path below the supplied data_root",
    }


def _manifest_index(data_root: Path) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in _manifest_rows(data_root):
        archive = row.get("archive_path") or ""
        if archive:
            index[archive.replace("\\", "/")] = row
    return index


def instrument_tick(data_root: Path | str, instrument_id: int | str, root: str = "nq") -> Decimal | None:
    """Read the positive instrument definition tick size; never infer it."""

    base = Path(data_root) / "derived" / "continuous-futures__instrument-and-roll-maps"
    candidates = [base / f"{root}-instruments.parquet", base / f"{root}-instruments.json", base / f"{root}-instruments.csv"]
    path = next((item for item in candidates if item.is_file()), None)
    if path is None:
        return None
    rows: Iterable[Mapping[str, Any]]
    try:
        rows = list(iter_source_rows(path))
    except Exception:
        return None
    for row in rows:
        got_id = _row_value(row, "instrument_id", "instrument")
        if got_id is None or str(got_id) != str(instrument_id):
            continue
        for field_name in ("min_price_increment", "tick_size", "price_increment"):
            raw = _row_value(row, field_name)
            if raw is None:
                continue
            try:
                value = dec(raw)
            except (TypeError, ValueError, InvalidOperation):
                return None
            return value if value is not None and value > 0 else None
    # If pyarrow is installed, parquet rows were read above.  Otherwise a
    # manifest-only root cannot prove a per-instrument q and remains unknown.
    return None


def _json_records(value: Any) -> Iterator[dict[str, Any]]:
    """Yield row-like mappings from common provider JSON envelopes.

    This helper intentionally keeps the parsed object in the caller's JSON
    memory only.  It does not build a second list of rows, which matters for
    inventories of large observation responses.
    """

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                yield item
        return
    if not isinstance(value, dict):
        return
    # FRED acquisitions can wrap the API response a second time alongside
    # series metadata.  The observation rows, rather than the wrapper or the
    # series catalogue, carry the historical dates and values.
    observations = value.get("observations")
    if isinstance(observations, (list, dict)):
        yield from _json_records(observations)
        return
    nested = [item for item in value.values()
              if isinstance(item, list) and any(isinstance(row, dict) for row in item)]
    if nested:
        for rows in nested:
            for row in rows:
                if isinstance(row, dict):
                    yield row
        return
    yield value


def _header_score(fields: Sequence[Any], dataset_id: str = "") -> int:
    """Score a delimited record as a likely observation header."""

    keys = [_field_key(field) for field in fields]
    if not any(keys):
        return -100
    known_exact = {
        "date", "datetime", "timestamp", "time", "year", "month", "day", "days",
        "t", "ts_event", "ts_recv", "event_date", "event_ts_utc", "reference_month",
        "open", "high", "low", "close", "volume", "price", "size", "side",
        "instrument_id", "value", "status", "release_name", "time_et",
    }
    score = sum(2 if key in known_exact else 0 for key in keys)
    score += sum(1 for key in keys if any(token in key.split("_") for token in ("date", "timestamp", "datetime")))
    if "date" in keys:
        score += 8
    # CFTC's fixed-width exports use descriptive date headers such as
    # ``As of Date in Form YYMMDD`` and ``Report Date as YYYY-MM-DD``.  Their
    # normalized keys do not equal ``date`` but are still strong evidence of a
    # legal header; recognizing them prevents a full-file fallback scan.
    if any(re.search(r"(?:^|_)yymmdd$", key) for key in keys):
        score += 4
    if any(re.search(r"(?:^|_)yyyy_mm_dd$", key) for key in keys):
        score += 4
    if "cboe" in dataset_id.lower() and "date" in keys:
        score += 20
    if {"year", "month", "days"} <= set(keys):
        score += 20
    # A prose preamble can contain the word ``date`` incidentally but has one
    # very long cell and almost no identifier-like fields.
    if any(len(str(field)) > 160 for field in fields):
        score -= 20
    if all(not re.search(r"[A-Za-z_]", str(field)) for field in fields if str(field).strip()):
        score -= 10
    return score


def _is_preamble_record(fields: Sequence[Any], dataset_id: str = "") -> bool:
    """Recognize provider prose/comments before a legal CSV header."""

    if not any(str(field).strip() for field in fields):
        return True
    first = str(fields[0]).strip().lower() if fields else ""
    if first.startswith("#") or first.startswith("//"):
        return True
    score = _header_score(fields, dataset_id)
    nonempty = sum(bool(str(v).strip()) for v in fields)
    # Short prose preambles often have a zero score rather than a negative
    # score because their first cell contains a word such as ``data``.  A
    # sentence-like first cell with only a few populated columns is still
    # prose; a compact unknown-schema header such as ``foo,bar`` is not.
    sentence_like = len(first.split()) >= 3
    return len(first) > 160 or (
        score <= 0 and nonempty <= 3 and sentence_like
    )


def _iter_delimited_rows(source: Path, *, delimiter: str, dataset_id: str = "") -> Iterator[dict[str, Any]]:
    """Yield rows after skipping comments/preambles and locating the header."""

    with source.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        header: list[str] | None = None
        for record in reader:
            if not any(str(value).strip() for value in record):
                continue
            # The first non-prose record is the header.  Provider-specific
            # headers already score highly; treating a weak but identifier-
            # shaped first record as the header avoids mistaking a later data
            # row for the schema.  Preambles are skipped by the bounded,
            # sentence-aware predicate above.
            if _is_preamble_record(record, dataset_id):
                continue
            header = [str(value).strip() for value in record]
            break
        if header is None:
            return
        # Empty header cells are legal in a provider export; preserve them for
        # schema auditing but avoid a ``None`` key in row mappings.
        for record in reader:
            if not any(str(value).strip() for value in record):
                continue
            row: dict[str, Any] = {}
            for index, name in enumerate(header):
                if name:
                    row[name] = record[index] if index < len(record) else None
            yield row


def iter_source_rows(path: Path | str, *, dataset_id: str = "") -> Iterator[dict[str, Any]]:
    """Stream rows from optional Arrow Parquet or simple JSON/CSV fixtures."""

    source = Path(path)
    if source.suffix == ".parquet":
        try:
            import pyarrow as pa  # type: ignore
            import pyarrow.parquet as pq  # type: ignore
        except ImportError as exc:
            raise RuntimeError("pyarrow is required to read Parquet rows") from exc
        parquet = pq.ParquetFile(source)
        def exact_rows(batch):
            # Python datetime cannot retain nanoseconds. Convert Arrow UTC
            # timestamp columns to exact ns integers before materialization.
            units = {}
            for index, field in enumerate(batch.schema):
                if pa.types.is_timestamp(field.type):
                    units[field.name] = {'source_unit': field.type.unit, 'timezone': field.type.tz,
                                         'normalized_unit': 'ns'}
                    column = batch.column(index).cast(pa.timestamp('ns', tz=field.type.tz)).cast(pa.int64())
                    batch = batch.set_column(index, field.name, column)
            for row in batch.to_pylist():
                if units:
                    row['_timestamp_units'] = units
                yield row
        # Keep row materialization bounded even when a provider writes a very
        # large row group.  ``iter_batches`` is available on Arrow's
        # ParquetFile; the fallback keeps this adapter usable with small test
        # doubles that only expose ``read_row_group``.
        if hasattr(parquet, "iter_batches"):
            for batch in parquet.iter_batches(batch_size=65_536):
                yield from exact_rows(batch)
        else:
            for group_index in range(parquet.num_row_groups):
                table = parquet.read_row_group(group_index)
                yield from exact_rows(table)
        return
    suffix = source.suffix.lower()
    if suffix in {".json", ".jsonl"}:
        if suffix == '.jsonl':
            with source.open() as handle:
                for line in handle:
                    if line.strip():
                        item = json.loads(line)
                        if isinstance(item, dict):
                            yield item
            return
        try:
            value = json.loads(source.read_text())
        except json.JSONDecodeError:
            with source.open() as handle:
                for line in handle:
                    if line.strip():
                        item = json.loads(line)
                        if isinstance(item, dict):
                            yield item
            return
        # Provider JSON responses commonly wrap row records under
        # ``observations``, ``data`` or ``results``.  Flatten only lists that
        # actually contain mappings; metadata dictionaries remain one row.
        yield from _json_records(value)
        return
    if suffix in {".csv", ".tsv", ".txt"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        yield from _iter_delimited_rows(source, delimiter=delimiter, dataset_id=dataset_id)
        return
    raise RuntimeError(f"unsupported source format: {source}")


@dataclass(frozen=True)
class OwnedSpan:
    path: str
    start_ns: int
    end_ns: int
    kind: str
    dataset: str
    status: str = "owned"
    reason: str | None = None
    source_start_ns: int | None = None
    source_end_ns: int | None = None
    timestamp_unit: str = "ns"


def _month_bounds_utc(year: int, month: int) -> tuple[int, int]:
    start = datetime_ns(datetime(year, month, 1, tzinfo=timezone.utc))
    if month == 12:
        end = datetime_ns(datetime(year + 1, 1, 1, tzinfo=timezone.utc))
    else:
        end = datetime_ns(datetime(year, month + 1, 1, tzinfo=timezone.utc))
    return start, end


def _iso_bound(value: Any, *, end: bool = False) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float, Decimal)):
        # Manifest epoch fields are not used by the current inventory, but an
        # explicit integer is interpreted as native nanoseconds here.
        try:
            return _checked_ns(value)
        except ValueError:
            return None
    try:
        parsed = _parse_iso_ns(str(value))
    except ValueError:
        return None
    return parsed + (1 if end else 0)


def _observation_end_ns(dataset_id: str, point_end_ns: int) -> int:
    """Turn an inclusive point bound into a half-open observation bound."""

    # ``point_end_ns`` is one nanosecond after the final native timestamp.
    # OHLCV's native t is a bar *start*, so the final bar is available at its
    # close.  Other event records are points and retain their one-nanosecond
    # half-open envelope.
    lower = dataset_id.lower()
    if "ohlcv-1m" in lower:
        return point_end_ns - 1 + 60 * NS
    if "ohlcv-1s" in lower:
        return point_end_ns - 1 + NS
    if "thetadata" in lower or "opra" in lower:
        return point_end_ns - 1 + 1_000_000
    return point_end_ns


def _dataset_for_path(root: Path, path: Path) -> str:
    try:
        rel = path.relative_to(root).as_posix().split("/")
    except ValueError:
        rel = path.as_posix().split("/")
    return "/".join(rel[:2]) if len(rel) >= 2 else (rel[0] if rel else "")


def _required_fields(dataset_id: str) -> tuple[str, ...]:
    lower = dataset_id.lower()
    if "mbp-1" in lower:
        return MBP1_REQUIRED
    if "ohlcv" in lower:
        return ("t", "o", "h", "l", "c", "v")
    if "trades" in lower:
        return ("t", "price", "size", "side", "instrument_id")
    if "instrument-and-roll-maps" in lower and "instruments" in lower:
        return ("instrument_id", "min_price_increment")
    return ()


_EVENT_FIELD_PRIORITY = (
    "event_ts_utc",
    "earnings_ts_utc",
    "release_ts_utc",
    "published_ts_utc",
    "available_ts_utc",
    "ts_event",
    "trade_ts_utc",
    "quote_ts_utc",
    "timestamp_utc",
    "datetime_utc",
    "event_timestamp",
    "timestamp",
    "datetime",
    "t",
)

_CALENDAR_FIELD_PRIORITY = (
    "date",
    "trade_date",
    "event_date",
    "observation_date",
    "reference_date",
    "report_date",
    "release_date",
    "earnings_date_et",
    "as_of_date",
    "mpm_date",
)

_AVAILABILITY_FIELD_NAMES = {
    "available_at", "availability_at", "availability_ts", "available_ts",
    "published_at", "published_ts", "released_at", "release_ts",
    "received_at", "received_ts", "known_at", "knowledge_at",
    # Databento/QuantPad definitions expose the provider receive clock as a
    # native ``ts_recv`` field.  It is availability evidence, not a second
    # market event.
    "ts_recv", "recv_ns", "receive_ts", "received_ts_ns",
}

_SCHEDULE_FIELD_NAMES = {
    "scheduled_at", "scheduled_ts", "schedule_at", "schedule_ts",
}

_CLOCK_FIELD_NAMES = {
    "time", "time_et", "event_time", "event_time_et", "release_time",
    "release_time_et", "scheduled_time", "scheduled_time_et",
}


def _field_key(name: Any) -> str:
    """Normalize a source column name for conservative semantic matching."""

    text = str(name).strip().lower()
    # A small explicit mapping keeps the acquired Sina daily export usable
    # without treating arbitrary non-ASCII text as a timestamp.  The source
    # manifest identifies these columns as civil dates and OHLC fields.
    chinese = {
        "日期": "date",
        "时间": "time",
        "开盘价": "open",
        "最高价": "high",
        "最低价": "low",
        "收盘价": "close",
        "成交量": "volume",
        "持仓量": "open_interest",
        "动态结算价": "settlement",
    }
    if text in chinese:
        return chinese[text]
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def _field_unit(field: str) -> str | None:
    key = _field_key(field)
    for suffix, unit in (("_nanoseconds", "ns"), ("_nanos", "ns"), ("_ns", "ns"),
                         ("_microseconds", "us"), ("_micros", "us"), ("_us", "us"),
                         ("_milliseconds", "ms"), ("_millis", "ms"), ("_ms", "ms"),
                         ("_seconds", "s"), ("_secs", "s"), ("_s", "s")):
        if key.endswith(suffix):
            return unit
    return None


def _is_explicit_event_field(field: str, dataset_id: str = "") -> bool:
    key = _field_key(field)
    if dataset_id == "free-sources/context__event-calendar__normalized" and key == "event_ts_utc":
        # This acquired calendar labels records scheduled_or_observed and
        # includes conventional release/closing clocks. It is not proof of
        # an actual release or a market-tape observation.
        return False
    if key in _AVAILABILITY_FIELD_NAMES or key in _SCHEDULE_FIELD_NAMES or _is_clock_field(field):
        return False
    if key in {"expiration_ts_utc", "expiry_ts_utc", "activation_ts_utc",
               "contract_expiration_ts_utc", "segment_start_ts_utc",
               "segment_end_exclusive_ts_utc", "first_bar_ts_utc",
               "last_bar_ts_utc", "first_definition_ts_utc",
               "last_definition_ts_utc", "first_bar_ms", "last_bar_ms",
               "first_definition_ns", "last_definition_ns",
               "segment_start_ms", "segment_end_exclusive_ms"}:
        return False
    if key in {_field_key(item) for item in _EVENT_FIELD_PRIORITY}:
        return True
    if key.startswith(("event_", "trade_", "quote_", "earnings_")) and (
            "time" in key or "timestamp" in key or key.endswith("_ts_utc")):
        return True
    if (key.endswith(("_timestamp", "_datetime", "_ts", "_ts_utc"))
            and "expiration" not in key and "expiry" not in key
            and "activation" not in key):
        return True
    # ``t`` is a native market timestamp for the known tape datasets.  Keep
    # that knowledge here because a free-source column named ``t`` is also a
    # perfectly valid explicit event key when its value carries a unit.
    return key == "t" and native_timestamp_unit(dataset_id, "t") is not None


def _is_calendar_field(field: str) -> bool:
    key = _field_key(field)
    if key in {_field_key(item) for item in _CALENDAR_FIELD_PRIORITY}:
        return True
    if key in {"period", "reference_period", "reporting_period"}:
        return True
    # Provider exports often spell the same civil date as a descriptive
    # header (for example ``As of Date in Form YYYY-MM-DD``).  Keep the
    # matching conservative at the token level and let ``_date_value`` reject
    # non-date values; reference/snapshot fields are removed by
    # ``_classify_fields`` below.
    # Match a date token, rather than the substring (``update`` contains
    # ``date`` and is a common non-temporal definition field).
    tokens = set(key.split("_"))
    return "date" in tokens or key.endswith("_day")


def _is_reference_field(field: str) -> bool:
    key = _field_key(field)
    return ("expiration" in key or "expiry" in key or key in {
        "reference_month", "reference_date", "reference_day", "period", "reference_period", "realtime_start",
        "realtime_end", "vintage_date", "vintage_start", "vintage_end",
    } or "snapshot" in key or "capture" in key or key.startswith("retrieved_"))


def _is_vintage_field(field: str) -> bool:
    key = _field_key(field)
    return (key.startswith("realtime_") or "vintage" in key
            or key in {"revision_date", "revision_at", "revision_ts"})


def _is_availability_field(field: str) -> bool:
    key = _field_key(field)
    return key in _AVAILABILITY_FIELD_NAMES or key.endswith(("_available_at", "_published_at", "_released_at"))


def _is_schedule_field(field: str) -> bool:
    key = _field_key(field)
    return key in _SCHEDULE_FIELD_NAMES or key.endswith(("_scheduled_at", "_schedule_at"))


def _is_clock_field(field: str) -> bool:
    return _field_key(field) in _CLOCK_FIELD_NAMES


def _date_value(value: Any) -> date | None:
    """Parse a civil date without assigning it an intraday release clock."""

    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text or text in {".", "NA", "N/A", "null", "None", "-"}:
        return None
    # Keep date-only parsing strict enough that a six-digit CFTC YYMMDD field
    # is not mistaken for a year 26 date.  ISO datetime text is accepted only
    # when it begins with an unambiguous civil date.
    match = re.match(r"^(\d{4})[-/]?(\d{2})[-/]?(\d{2})(?:[T ]|$)", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    match = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?:$|\s)", text)
    if match:
        try:
            return date(int(match.group(3)), int(match.group(1)), int(match.group(2)))
        except ValueError:
            return None
    # Month labels are useful reference-period coverage, but are never
    # promoted to a release timestamp.
    match = re.match(r"^(\d{4})[-/](\d{2})$", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), 1)
        except ValueError:
            return None
    # BLS reference periods are written as ``October 2020`` (and a few
    # mirrors use ``2020 October``).  Keep the first day as the reference
    # period's civil anchor; callers retain this in the reference lane.
    month_names = {
        "jan": 1, "january": 1, "feb": 2, "february": 2,
        "mar": 3, "march": 3, "apr": 4, "april": 4,
        "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
        "oct": 10, "october": 10, "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }
    match = re.match(r"^([A-Za-z]+)\s+(\d{4})$", text)
    if match:
        month = month_names.get(match.group(1).lower())
        if month is not None:
            try:
                return date(int(match.group(2)), month, 1)
            except ValueError:
                return None
    match = re.match(r"^(\d{4})\s+([A-Za-z]+)$", text)
    if match:
        month = month_names.get(match.group(2).lower())
        if month is not None:
            try:
                return date(int(match.group(1)), month, 1)
            except ValueError:
                return None
    return None


def _date_ns(day: date, *, zone: timezone | ZoneInfo = timezone.utc) -> int | None:
    try:
        return _checked_ns(datetime_ns(datetime.combine(day, time.min, tzinfo=zone)))
    except (OverflowError, ValueError, TypeError):
        return None


def _parse_clock(value: Any) -> time | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.timetz().replace(tzinfo=None)
    if isinstance(value, time):
        return value.replace(tzinfo=None)
    text = str(value).strip().upper().replace(".", "")
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M:%S %p", "%I:%M %p"):
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


def _parse_explicit_timestamp(
    value: Any,
    field: str,
    dataset_id: str = "",
    *,
    default_zone: timezone | ZoneInfo | None = None,
) -> int | None:
    """Parse an event/availability key only when its timezone or unit is known."""

    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            if default_zone is None:
                return None
            value = value.replace(tzinfo=default_zone)
        try:
            return _checked_ns(datetime_ns(value.astimezone(timezone.utc)))
        except (OverflowError, ValueError, TypeError):
            return None
    unit = native_timestamp_unit(dataset_id, field) or _field_unit(field)
    if isinstance(value, (int, float, Decimal)):
        if unit is None:
            return None
        try:
            return timestamp_ns(value, unit)
        except (TypeError, ValueError, OverflowError):
            return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
        if unit is None:
            return None
        try:
            # ``timestamp_ns`` deliberately rejects float precision for
            # integer-like values; parse decimal text exactly instead.
            numeric: Any = int(text) if "." not in text else Decimal(text)
            return timestamp_ns(numeric, unit)
        except (TypeError, ValueError, OverflowError, InvalidOperation):
            return None
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        if default_zone is None:
            return None
        parsed = parsed.replace(tzinfo=default_zone)
    try:
        return _checked_ns(_parse_iso_ns(text, default_zone=default_zone))
    except (TypeError, ValueError, OverflowError):
        return None


def _is_cftc_short_date_field(field: str) -> bool:
    key = _field_key(field)
    return bool(re.search(r"(?:^|_)yymmdd$|(?:^|_)yy_mm_dd$", key))


def _parse_cftc_yymmdd(value: Any, corroborating_day: date | None) -> date | None:
    """Parse CFTC YYMMDD only when the same row supplies the ISO date.

    The six-digit form is deliberately not century-guessed.  CFTC exports
    include an equivalent ``YYYY-MM-DD`` field; requiring it to agree both
    resolves the century and catches a shifted/malformed row.
    """

    if corroborating_day is None or value in (None, ""):
        return None
    text = str(value).strip()
    if not re.fullmatch(r"\d{6}", text):
        return None
    try:
        candidate = date(
            corroborating_day.year,
            int(text[2:4]),
            int(text[4:6]),
        )
    except ValueError:
        return None
    # The year is taken from the corroborating ISO field, then all three
    # components must match.  This rejects a tempting but unjustified
    # ``20YY`` conversion when the two source columns disagree.
    if int(text[:2]) != candidate.year % 100:
        return None
    return candidate if candidate == corroborating_day else None


def _documented_source_zone(path: Path, dataset_id: str) -> tuple[timezone | ZoneInfo | None, str | None]:
    """Return a source zone only for a dataset with explicit documentation."""

    dataset = _field_key(dataset_id)
    name = path.name.lower()
    # The acquired SHFE CU minute exports are the only Sina wall-clock files
    # with a source-zone statement.  The caveat is recorded in
    # ``data/free-sources/cross-asset__copper/MANIFEST.tsv``; keep this exact
    # five-file allowlist so unrelated Sina/Nikkei/COMEX files remain
    # date-only or timezone-unknown.
    shfe_cu_minute_files = {
        "shfe_cu_main_1min_sina.csv",
        "shfe_cu_main_5min_sina.csv",
        "shfe_cu_main_15min_sina.csv",
        "shfe_cu_main_30min_sina.csv",
        "shfe_cu_main_60min_sina.csv",
    }
    if dataset == "free_sources_cross_asset_copper" and name in shfe_cu_minute_files:
        return ZoneInfo("Asia/Shanghai"), (
            "documented_manifest:Asia/Shanghai:"
            "data/free-sources/cross-asset__copper/MANIFEST.tsv"
        )
    return None, None


def _update_date_bounds(info: dict[str, Any], first: date, last: date) -> None:
    """Merge a civil date interval into the calendar lane."""

    first_ns = _date_ns(first)
    last_ns = _date_ns(last)
    if first_ns is not None:
        info["calendar_start_ns"] = (
            first_ns if info.get("calendar_start_ns") is None
            else min(int(info["calendar_start_ns"]), first_ns)
        )
    if last_ns is not None:
        end_ns = _checked_ns(last_ns + DAY_NS)
        info["calendar_end_ns"] = (
            end_ns if info.get("calendar_end_ns") is None
            else max(int(info["calendar_end_ns"]), end_ns)
        )
    old_min, old_max = info.get("date_min"), info.get("date_max")
    if old_min is None or first.isoformat() < str(old_min):
        info["date_min"] = first.isoformat()
    if old_max is None or last.isoformat() > str(old_max):
        info["date_max"] = last.isoformat()


def _month_number(value: Any) -> int | None:
    if value in (None, ""):
        return None
    text = str(value).strip().lower()
    names = {
        "jan": 1, "january": 1, "feb": 2, "february": 2,
        "mar": 3, "march": 3, "apr": 4, "april": 4,
        "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
        "oct": 10, "october": 10, "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }
    if text in names:
        return names[text]
    try:
        month = int(text)
    except (TypeError, ValueError):
        return None
    return month if 1 <= month <= 12 else None


def _calendar_parts_interval(row: Mapping[str, Any], fields: Sequence[str]) -> tuple[date, date] | None:
    """Build an inclusive meeting interval from split year/month/days fields."""

    by_key = {_field_key(key): key for key in row}
    keys = {_field_key(field): field for field in fields}
    year_field = keys.get("year") or by_key.get("year")
    month_field = keys.get("month") or by_key.get("month")
    days_field = keys.get("days") or keys.get("day") or by_key.get("days") or by_key.get("day")
    if year_field is None or month_field is None or days_field is None:
        return None
    try:
        year = int(str(row.get(year_field)).strip())
    except (TypeError, ValueError):
        return None
    raw_month = str(row.get(month_field) or "").strip()
    month_tokens = [token for token in re.split(r"[/\\-]", raw_month) if token.strip()]
    months = [_month_number(token) for token in month_tokens]
    if not months or any(month is None for month in months):
        return None
    raw_days = str(row.get(days_field) or "").strip()
    if not raw_days:
        return None
    numbers = [int(value) for value in re.findall(r"\d{1,2}", raw_days)]
    if not numbers:
        return None
    first_day, last_day = numbers[0], numbers[-1]
    try:
        first = date(year, int(months[0]), first_day)
        last = date(year, int(months[-1]), last_day)
    except ValueError:
        return None
    if last < first:
        return None
    return first, last


def _minmax_add(current: tuple[Any, Any] | None, value: Any) -> tuple[Any, Any]:
    """Merge one value into a streaming min/max pair."""

    if current is None:
        return value, value
    return min(current[0], value), max(current[1], value)


def _temporal_template() -> dict[str, Any]:
    return {
        "event_field": None,
        "calendar_fields": [],
        "reference_fields": [],
        "vintage_fields": [],
        "availability_fields": [],
        "schedule_fields": [],
        "clock_fields": [],
        "event_start_ns": None,
        "event_end_ns": None,
        "calendar_start_ns": None,
        "calendar_end_ns": None,
        "reference_start_ns": None,
        "reference_end_ns": None,
        "vintage_start_ns": None,
        "vintage_end_ns": None,
        "definition_start_ns": None,
        "definition_end_ns": None,
        "roll_start_ns": None,
        "roll_end_ns": None,
        "metadata_start_ns": None,
        "metadata_end_ns": None,
        "scheduled_start_ns": None,
        "scheduled_end_ns": None,
        "available_start_ns": None,
        "available_end_ns": None,
        "timestamp_unit": None,
        "precision": None,
        "date_only": False,
        "temporal_basis": None,
        "source_timezone": None,
        "timezone_basis": None,
        "calendar_component_fields": [],
        "temporal_holes": [],
    }


def _bound_update(info: dict[str, Any], start_key: str, end_key: str, at: int, *, end: int | None = None) -> None:
    info[start_key] = at if info[start_key] is None else min(info[start_key], at)
    finish = at + 1 if end is None else end
    info[end_key] = finish if info[end_key] is None else max(info[end_key], finish)


def _field_candidates(fields: Sequence[str], predicate) -> list[str]:
    return [field for field in fields if predicate(field)]


def _choose_event_field(fields: Sequence[str], dataset_id: str) -> str | None:
    by_key = {_field_key(field): field for field in fields}
    for preferred in _EVENT_FIELD_PRIORITY:
        field = by_key.get(_field_key(preferred))
        if field is not None and _is_explicit_event_field(field, dataset_id):
            return field
    candidates = _field_candidates(fields, lambda field: _is_explicit_event_field(field, dataset_id))
    return sorted(candidates, key=lambda field: (_field_key(field), field))[0] if candidates else None


def _classify_fields(fields: Sequence[str], dataset_id: str) -> dict[str, Any]:
    info = _temporal_template()
    event_field = _choose_event_field(fields, dataset_id)
    info["event_field"] = event_field
    info["calendar_fields"] = [field for field in fields if _is_calendar_field(field)
                                and not _is_reference_field(field)
                                and field != event_field]
    by_key = {_field_key(field): field for field in fields}
    split_fields = [
        by_key.get("year"),
        by_key.get("month"),
        by_key.get("days") or by_key.get("day"),
    ]
    if all(field is not None for field in split_fields):
        # These are one civil meeting interval, not three independent date
        # observations.  Keep the source columns visible and parse them as a
        # composite in ``_infer_text_temporal``.
        info["calendar_component_fields"] = [field for field in split_fields if field is not None]
        for field in info["calendar_component_fields"]:
            if field not in info["calendar_fields"] and field != event_field:
                info["calendar_fields"].append(field)
    info["reference_fields"] = [field for field in fields if _is_reference_field(field)]
    info["vintage_fields"] = [field for field in fields if _is_vintage_field(field)]
    info["availability_fields"] = [field for field in fields if _is_availability_field(field)]
    info["schedule_fields"] = [field for field in fields if _is_schedule_field(field)]
    if dataset_id == "free-sources/context__event-calendar__normalized":
        info["schedule_fields"].extend(field for field in fields if _field_key(field) == "event_ts_utc")
    info["clock_fields"] = [field for field in fields if _is_clock_field(field)]
    # A timestamp receive key is an availability clock even though it is not
    # a publication timestamp.  ``_is_availability_field`` handles this
    # semantically; this branch only removes duplicate field labels.
    info["availability_fields"] = list(dict.fromkeys(info["availability_fields"]))
    info["reference_fields"] = list(dict.fromkeys(info["reference_fields"]))
    return info


def _temporal_holes(info: Mapping[str, Any], fields: Sequence[str], *, dataset_id: str, artifact_role: str = "data") -> list[dict[str, Any]]:
    """Return explicit temporal limitations while preserving known date scope."""

    if artifact_role in {"manifest", "raw_provenance", "provenance"}:
        parser_reason = "observation_parser_not_applicable" if artifact_role == "manifest" else "parser_not_applied"
        return [
            {"reason": "provenance_artifact_not_observation_data", "missing_fields": []},
            {"reason": parser_reason, "missing_fields": ["parser"]},
            {"reason": "observation_datafields_unavailable", "missing_fields": ["datafields"]},
        ]
    if artifact_role in {"contract_definition", "roll_metadata"}:
        # Definition and roll files describe the contract/segment mapping.
        # Their timestamps are useful metadata evidence but they are not tape
        # observations, so a missing event lane is not a market-data hole.
        metadata_start = info.get("metadata_start_ns")
        metadata_end = info.get("metadata_end_ns")
        if metadata_start is None or metadata_end is None:
            return [{"reason": "metadata_bounds_unavailable", "missing_fields": ["metadata_interval"]}]
        return []
    event = info.get("event_start_ns") is not None and info.get("event_end_ns") is not None
    calendar = info.get("calendar_start_ns") is not None and info.get("calendar_end_ns") is not None
    scheduled = info.get("scheduled_start_ns") is not None and info.get("scheduled_end_ns") is not None
    available = info.get("available_start_ns") is not None and info.get("available_end_ns") is not None
    holes: list[dict[str, Any]] = []
    if not event and not calendar and not scheduled and not available:
        holes.append({"reason": "observation_time_or_date_field_unavailable", "missing_fields": ["event_timestamp", "date"]})
    if calendar and not event and not available and not scheduled:
        holes.extend([
            {"reason": "date_only_observation_no_intraday_time", "missing_fields": ["event_timestamp"]},
            {"reason": "publication_time_unknown", "missing_fields": ["publication_time", "available_at"]},
            {"reason": "vintage_or_revision_time_unknown", "missing_fields": ["vintage", "revision_time"]},
        ])
    if scheduled and not available:
        holes.extend([
            {"reason": "scheduled_calendar_is_not_actual_release", "missing_fields": ["released_at"]},
            {"reason": "released_value_or_vintage_unavailable", "missing_fields": ["released_value", "vintage"]},
        ])
    if (event or scheduled) and info.get("availability_fields") and not available:
        holes.append({"reason": "availability_timestamp_unavailable", "missing_fields": ["available_at"]})
    if not fields:
        holes.append({"reason": "schema_unavailable", "missing_fields": ["schema"]})
    return holes


def _infer_text_temporal(path: Path, dataset_id: str = "", *, artifact_role: str = "data") -> tuple[list[str], dict[str, Any], int | None, list[str]]:
    """Stream text rows and infer schema plus separately labeled time bounds."""

    fields_seen: set[str] = set()
    rows = 0
    info: dict[str, Any] | None = None
    date_bounds: tuple[date, date] | None = None
    reference_bounds: tuple[date, date] | None = None
    vintage_bounds: tuple[date, date] | None = None
    event_bounds: tuple[int, int] | None = None
    scheduled_bounds: tuple[int, int] | None = None
    available_bounds: tuple[int, int] | None = None
    parse_failures: set[str] = set()
    date_field: str | None = None
    clock_field: str | None = None
    default_zone, timezone_basis = _documented_source_zone(path, dataset_id)
    for row in iter_source_rows(path, dataset_id=dataset_id):
        rows += 1
        row_fields = [str(key) for key in row]
        fields_seen.update(row_fields)
        if info is None:
            info = _classify_fields(row_fields, dataset_id)
            info["source_timezone"] = str(default_zone) if default_zone is not None else None
            info["timezone_basis"] = timezone_basis
            # A paired wall clock is only meaningful with a real civil date,
            # not a split year/month/days meeting representation.
            date_field = next(
                (field for field in info["calendar_fields"]
                 if field not in info.get("calendar_component_fields", [])),
                None,
            )
            clock_field = next(iter(info["clock_fields"]), None)
        # A provider occasionally changes capitalization between partitions;
        # resolve values case-insensitively without copying the row.
        lookup = {_field_key(key): key for key in row}
        if info["event_field"] is not None:
            field = info["event_field"]
            actual = lookup.get(_field_key(field), field)
            at = _parse_explicit_timestamp(
                row.get(actual), field, dataset_id, default_zone=default_zone,
            )
            if at is not None:
                event_bounds = _minmax_add(event_bounds, at)
            elif row.get(actual) not in (None, ""):
                parse_failures.add(field)
        # FOMC's legacy calendar stores year/month/days separately.  Parse one
        # inclusive civil meeting interval and keep it in the calendar lane.
        component_fields = info.get("calendar_component_fields") or []
        if component_fields:
            interval = _calendar_parts_interval(row, component_fields)
            if interval is not None:
                date_bounds = _minmax_add(date_bounds, interval[0])
                date_bounds = (date_bounds[0], max(date_bounds[1], interval[1]))
            elif any(row.get(lookup.get(_field_key(field), field)) not in (None, "")
                     for field in component_fields):
                parse_failures.add("calendar_components")
        for field in info["calendar_fields"]:
            if field in component_fields or _is_cftc_short_date_field(field):
                continue
            actual = lookup.get(_field_key(field), field)
            day = _date_value(row.get(actual))
            if day is not None:
                date_bounds = _minmax_add(date_bounds, day)
            elif row.get(actual) not in (None, ""):
                parse_failures.add(field)
        # CFTC rows provide a six-digit YYMMDD beside an explicit ISO date.
        # Resolve the short form only when every component corroborates that
        # same-row ISO value.  This avoids a silent century assumption.
        iso_days = [
            _date_value(row.get(lookup.get(_field_key(field), field)))
            for field in info["calendar_fields"]
            if field not in component_fields and not _is_cftc_short_date_field(field)
        ]
        iso_day = next((day for day in iso_days if day is not None), None)
        for field in info["calendar_fields"]:
            if not _is_cftc_short_date_field(field):
                continue
            actual = lookup.get(_field_key(field), field)
            raw = row.get(actual)
            if raw in (None, ""):
                continue
            short_day = _parse_cftc_yymmdd(raw, iso_day)
            if short_day is None:
                parse_failures.add(field)
            else:
                date_bounds = _minmax_add(date_bounds, short_day)
        for field in info["reference_fields"]:
            actual = lookup.get(_field_key(field), field)
            day = _date_value(row.get(actual))
            if day is not None:
                reference_bounds = _minmax_add(reference_bounds, day)
            elif row.get(actual) not in (None, ""):
                # Explicit reference timestamps remain reference bounds, not
                # event bounds.  They may still be useful for expiry metadata.
                at = _parse_explicit_timestamp(
                    row.get(actual), field, dataset_id, default_zone=default_zone,
                )
                if at is not None:
                    _bound_update(info, "reference_start_ns", "reference_end_ns", at)
                else:
                    parse_failures.add(field)
        for field in info["vintage_fields"]:
            actual = lookup.get(_field_key(field), field)
            day = _date_value(row.get(actual))
            if day is not None:
                vintage_bounds = _minmax_add(vintage_bounds, day)
            elif row.get(actual) not in (None, ""):
                at = _parse_explicit_timestamp(
                    row.get(actual), field, dataset_id, default_zone=default_zone,
                )
                if at is not None:
                    _bound_update(info, "vintage_start_ns", "vintage_end_ns", at)
                else:
                    parse_failures.add(field)
        for field in info["availability_fields"]:
            actual = lookup.get(_field_key(field), field)
            raw = row.get(actual)
            at = _parse_explicit_timestamp(
                raw, field, dataset_id, default_zone=default_zone,
            )
            if at is not None:
                available_bounds = _minmax_add(available_bounds, at)
            elif raw not in (None, ""):
                parse_failures.add(field)
        for field in info["schedule_fields"]:
            actual = lookup.get(_field_key(field), field)
            at = _parse_explicit_timestamp(
                row.get(actual), field, dataset_id, default_zone=default_zone,
            )
            if at is not None:
                scheduled_bounds = _minmax_add(scheduled_bounds, at)
            elif row.get(actual) not in (None, ""):
                parse_failures.add(field)
        # BLS and similar calendars carry an ET wall-clock in a separate
        # column.  Pairing it with a civil date gives a scheduled key only;
        # it does not become an actual released/available timestamp.
        if date_field is not None and clock_field is not None:
            day = _date_value(row.get(lookup.get(_field_key(date_field), date_field)))
            wall = _parse_clock(row.get(lookup.get(_field_key(clock_field), clock_field)))
            if day is not None and wall is not None:
                try:
                    scheduled_bounds = _minmax_add(
                        scheduled_bounds,
                        _checked_ns(datetime_ns(datetime.combine(day, wall, tzinfo=ET_ZONE))),
                    )
                except (OverflowError, ValueError, TypeError):
                    parse_failures.add(clock_field)
    fields = sorted(fields_seen)
    if info is None:
        info = _classify_fields(fields, dataset_id)
    if event_bounds is not None:
        info["event_start_ns"] = event_bounds[0]
        info["event_end_ns"] = _observation_end_ns(dataset_id, event_bounds[1] + 1)
        event_key = _field_key(info["event_field"] or "")
        info["precision"] = "nanoseconds" if event_key.endswith("ns") else "source_timestamp"
        info["timestamp_unit"] = native_timestamp_unit(dataset_id, info["event_field"] or "") or _field_unit(info["event_field"] or "") or "timestamp"
    if date_bounds is not None:
        _update_date_bounds(info, date_bounds[0], date_bounds[1])
        info["precision"] = info.get("precision") or "calendar_day"
    if reference_bounds is not None:
        first, last = reference_bounds
        info["reference_start_ns"] = _date_ns(first)
        last_ns = _date_ns(last)
        info["reference_end_ns"] = None if last_ns is None else _checked_ns(last_ns + DAY_NS)
    if vintage_bounds is not None:
        first, last = vintage_bounds
        info["vintage_start_ns"] = _date_ns(first)
        last_ns = _date_ns(last)
        info["vintage_end_ns"] = None if last_ns is None else _checked_ns(last_ns + DAY_NS)
    if scheduled_bounds is not None:
        info["scheduled_start_ns"] = scheduled_bounds[0]
        info["scheduled_end_ns"] = scheduled_bounds[1] + 1
    if available_bounds is not None:
        info["available_start_ns"] = available_bounds[0]
        info["available_end_ns"] = available_bounds[1] + 1
    # A civil date without an actual event key is date-only.  A paired wall
    # clock is a scheduled calendar key, so it must remain distinguishable
    # from a date-only observation even though neither proves publication.
    info["date_only"] = bool(
        info.get("calendar_start_ns") is not None
        and info.get("event_start_ns") is None
        and info.get("scheduled_start_ns") is None
    )
    info["temporal_basis"] = (
        "event_timestamp" if info.get("event_start_ns") is not None else
        "scheduled_calendar" if info.get("scheduled_start_ns") is not None else
        "calendar_date" if info.get("calendar_start_ns") is not None else None
    )
    holes = _temporal_holes(info, fields, dataset_id=dataset_id, artifact_role=artifact_role)
    for field in sorted(parse_failures):
        holes.append({"reason": f"temporal_value_unparseable:{field}", "missing_fields": [field]})
    return fields, info, rows, holes


def _infer_text_schema(path: Path, dataset_id: str = "") -> tuple[list[str], int | None, int | None, int | None]:
    """Backward-compatible text schema helper with labeled date bounds.

    Existing callers receive the same tuple shape.  For date-only inputs the
    returned bounds are calendar-day bounds; callers that need causal release
    timing must use the richer fields returned by :func:`_infer_text_temporal`.
    """

    fields, info, rows, _holes = _infer_text_temporal(path, dataset_id)
    start = info.get("event_start_ns") or info.get("calendar_start_ns")
    end = info.get("event_end_ns") or info.get("calendar_end_ns")
    return fields, start, end, rows


def _schema_from_manifest(dataset_id: str, catalog: dict[str, Any]) -> list[dict[str, Any]]:
    return _flatten_schema((catalog.get("schemas") or {}).get(dataset_id, []))


def _artifact_role(path: Path, dataset_id: str) -> str:
    """Classify transport artifacts before attempting observation parsing."""

    name = path.name.lower()
    dataset = dataset_id.lower()
    if name.startswith("manifest") or name.endswith("manifest.tsv") or "manifest_notes" in name:
        return "manifest"
    if name.startswith(("fetch_receipt", "fetch_log")):
        return "raw_provenance"
    if name.startswith("verify") or "verification" in name:
        return "raw_provenance"
    # These files carry contract identity and segment boundaries.  They are
    # intentionally separate from market observations so their intervals can
    # be used as mapping evidence without creating fake tape coverage holes.
    if "continuous-futures__instrument-and-roll-maps" in dataset:
        if "roll" in name:
            return "roll_metadata"
        if "instrument" in name:
            return "contract_definition"
    if "definition" in dataset or "/definition" in dataset:
        return "contract_definition"
    # HTML/PDF/XML/checksum/script copies are retained as provenance.  Raw
    # CSV/JSON/Parquet files remain data even when their dataset name contains
    # ``raw``; their observations are inspected below.
    if path.suffix.lower() in {".htm", ".html", ".pdf", ".xml", ".sha256", ".py", ".zip"}:
        return "raw_provenance"
    if "acquisition-metadata" in dataset and path.suffix.lower() in {".txt", ".json"}:
        return "raw_provenance"
    return "data"


def _manifest_temporal_bounds(manifest_row: Mapping[str, str], dataset_id: str) -> dict[str, Any]:
    """Read manifest bounds without confusing a civil date with availability."""

    info = _temporal_template()
    minimum = manifest_row.get("observed_time_min")
    maximum = manifest_row.get("observed_time_max")
    if minimum in (None, "") or maximum in (None, ""):
        return info
    # Full ISO values with an offset are event bounds.  YYYY-MM-DD values are
    # calendar scope only and are stored as a day interval.
    min_at = _parse_explicit_timestamp(minimum, manifest_row.get("primary_time_field", ""), dataset_id)
    max_at = _parse_explicit_timestamp(maximum, manifest_row.get("primary_time_field", ""), dataset_id)
    if min_at is not None and max_at is not None:
        info["event_start_ns"] = min_at
        info["event_end_ns"] = _observation_end_ns(dataset_id, max_at + 1)
        info["temporal_basis"] = "manifest_event_bounds"
        return info
    min_day, max_day = _date_value(minimum), _date_value(maximum)
    if min_day is not None and max_day is not None:
        info["calendar_start_ns"] = _date_ns(min_day)
        max_ns = _date_ns(max_day)
        info["calendar_end_ns"] = None if max_ns is None else _checked_ns(max_ns + DAY_NS)
        info["date_min"], info["date_max"] = min_day.isoformat(), max_day.isoformat()
        info["date_only"] = True
        info["temporal_basis"] = "manifest_calendar_bounds"
    return info


def _field_documented_zone(field: str) -> timezone | None:
    """Infer UTC only from an explicit UTC field name."""

    return timezone.utc if _field_key(field).endswith("_utc") else None


def _parquet_field_bounds(
    parquet: Any,
    schema_names: Sequence[str],
    field: str,
    field_type: Any,
    dataset_id: str,
) -> tuple[int | date | Any, int | date | Any] | None:
    """Read exact row-group bounds for one Arrow field.

    For typed timestamps, ``Statistics.min``/``max`` are Python datetime
    accessors and can truncate nanoseconds.  ``min_raw``/``max_raw`` retain
    the physical integer in the Arrow unit, so they are always preferred.
    """

    try:
        import pyarrow as pa  # type: ignore
    except ImportError:
        return None
    try:
        index = list(schema_names).index(field)
    except ValueError:
        return None
    lower_value: int | date | Any | None = None
    upper_value: int | date | Any | None = None
    default_zone = _field_documented_zone(field)
    for group_index in range(parquet.num_row_groups):
        stats = parquet.metadata.row_group(group_index).column(index).statistics
        if stats is None or getattr(stats, "has_min_max", True) is False:
            continue
        try:
            if pa.types.is_timestamp(field_type):
                raw_min = getattr(stats, "min_raw", None)
                raw_max = getattr(stats, "max_raw", None)
                if raw_min is not None and raw_max is not None:
                    lower = timestamp_ns(raw_min, field_type.unit)
                    upper = timestamp_ns(raw_max, field_type.unit)
                else:
                    # Some Arrow test doubles expose only min/max.  Preserve
                    # exact values where possible and refuse naive local
                    # clocks unless the field/documented source says UTC.
                    lower = _parse_explicit_timestamp(
                        stats.min, field, dataset_id, default_zone=default_zone,
                    )
                    upper = _parse_explicit_timestamp(
                        stats.max, field, dataset_id, default_zone=default_zone,
                    )
            elif pa.types.is_date(field_type):
                lower = _date_value(stats.min)
                upper = _date_value(stats.max)
                if lower is None or upper is None:
                    # Arrow date32's raw physical value is days from epoch.
                    epoch = date(1970, 1, 1)
                    raw_min = getattr(stats, "min_raw", None)
                    raw_max = getattr(stats, "max_raw", None)
                    if raw_min is not None and raw_max is not None:
                        lower = epoch + timedelta(days=int(raw_min))
                        upper = epoch + timedelta(days=int(raw_max))
            else:
                raw_min, raw_max = getattr(stats, "min_raw", None), getattr(stats, "max_raw", None)
                stat_min = stats.min if raw_min is None else raw_min
                stat_max = stats.max if raw_max is None else raw_max
                unit = native_timestamp_unit(dataset_id, field) or _field_unit(field)
                if unit is not None:
                    lower = timestamp_ns(stat_min, unit)
                    upper = timestamp_ns(stat_max, unit)
                else:
                    lower, upper = stat_min, stat_max
        except (TypeError, ValueError, OverflowError, InvalidOperation):
            continue
        if lower is None or upper is None:
            continue
        lower_value = lower if lower_value is None else min(lower_value, lower)
        upper_value = upper if upper_value is None else max(upper_value, upper)
    if lower_value is None or upper_value is None:
        return None
    return lower_value, upper_value


def _metadata_pair_bounds(
    parquet: Any,
    schema_names: Sequence[str],
    field_types: Mapping[str, Any],
    start_fields: Sequence[str],
    end_fields: Sequence[str],
    dataset_id: str,
    *,
    end_is_exclusive: bool = False,
) -> tuple[int, int] | None:
    """Combine a start/end metadata pair without mixing unrelated columns."""

    starts: list[int] = []
    ends: list[int] = []
    for field in start_fields:
        if field not in schema_names or field not in field_types:
            continue
        bounds = _parquet_field_bounds(parquet, schema_names, field, field_types[field], dataset_id)
        if bounds is None or not isinstance(bounds[0], int):
            continue
        starts.append(int(bounds[0]))
    for field in end_fields:
        if field not in schema_names or field not in field_types:
            continue
        bounds = _parquet_field_bounds(parquet, schema_names, field, field_types[field], dataset_id)
        if bounds is None or not isinstance(bounds[1], int):
            continue
        ends.append(int(bounds[1]))
    if not starts or not ends:
        return None
    lower, upper = min(starts), max(ends)
    if not end_is_exclusive:
        upper += 1
    return lower, upper


def _parquet_temporal(
    parquet: Any,
    schema_names: Sequence[str],
    dataset_id: str,
    *,
    artifact_role: str = "data",
) -> tuple[dict[str, Any], list[str]]:
    """Read exact Arrow bounds while keeping event/calendar/metadata lanes separate."""

    info = _classify_fields(schema_names, dataset_id)
    holes: list[dict[str, Any]] = []
    try:
        import pyarrow as pa  # type: ignore
    except ImportError:
        return info, _temporal_holes(info, schema_names, dataset_id=dataset_id, artifact_role=artifact_role)
    field_types = {field.name: field.type for field in parquet.schema_arrow}
    info["calendar_fields"] = list(dict.fromkeys(info.get("calendar_fields", [])))
    info["reference_fields"] = list(dict.fromkeys(info.get("reference_fields", [])))
    info["vintage_fields"] = list(dict.fromkeys(info.get("vintage_fields", [])))
    info["availability_fields"] = list(dict.fromkeys(info.get("availability_fields", [])))
    # Typed Arrow date columns are authoritative calendar fields even when a
    # provider uses an unfamiliar name.  A typed timestamp remains an event
    # candidate only when its field name is not a reference/metadata clock.
    for field, field_type in field_types.items():
        if pa.types.is_date(field_type) and field not in info["calendar_fields"] and not _is_reference_field(field):
            info["calendar_fields"].append(field)
        if pa.types.is_timestamp(field_type) and _is_reference_field(field) and field not in info["reference_fields"]:
            info["reference_fields"].append(field)
        elif pa.types.is_timestamp(field_type) and info.get("event_field") is None and _is_explicit_event_field(field, dataset_id):
            info["event_field"] = field

    event_field = info.get("event_field")
    event_values: tuple[int, int] | None = None
    if event_field is not None and event_field in field_types:
        field_bounds = _parquet_field_bounds(
            parquet, schema_names, event_field, field_types[event_field], dataset_id,
        )
        if field_bounds is not None and isinstance(field_bounds[0], int):
            event_values = int(field_bounds[0]), int(field_bounds[1])
            info["event_start_ns"] = event_values[0]
            info["event_end_ns"] = _observation_end_ns(dataset_id, event_values[1] + 1)
            info["timestamp_unit"] = native_timestamp_unit(dataset_id, event_field) or _field_unit(event_field) or "timestamp"
            info["precision"] = "source_timestamp"
        else:
            index = schema_names.index(event_field)
            groups = [parquet.metadata.row_group(i) for i in range(parquet.num_row_groups)]
            all_null = bool(groups) and all(
                group.column(index).statistics is not None
                and group.column(index).statistics.null_count == group.num_rows
                for group in groups)
            reason = "event_timestamp_not_supplied" if all_null else "timestamp_statistics_unavailable"
            holes.append({"reason": f"{reason}:{event_field}", "missing_fields": [event_field]})

    # Calendar, reference and vintage statistics stay in their own lanes.
    for category, fields, start_key, end_key in (
        ("calendar", info.get("calendar_fields", []), "calendar_start_ns", "calendar_end_ns"),
        ("reference", info.get("reference_fields", []), "reference_start_ns", "reference_end_ns"),
        ("vintage", info.get("vintage_fields", []), "vintage_start_ns", "vintage_end_ns"),
    ):
        date_bounds: tuple[date, date] | None = None
        for field in fields:
            if field not in field_types:
                continue
            bounds = _parquet_field_bounds(parquet, schema_names, field, field_types[field], dataset_id)
            if bounds is None:
                continue
            lower, upper = bounds
            if isinstance(lower, date) and not isinstance(lower, datetime):
                date_bounds = _minmax_add(date_bounds, lower)
                date_bounds = (date_bounds[0], max(date_bounds[1], upper))
                continue
            # Timestamp references may be exact UTC instants; retain them as
            # reference/vintage bounds rather than promoting them to events.
            if isinstance(lower, int) and isinstance(upper, int):
                _bound_update(info, start_key, end_key, lower, end=upper + 1)
                continue
            parsed_lower, parsed_upper = _date_value(lower), _date_value(upper)
            if parsed_lower is not None and parsed_upper is not None:
                date_bounds = _minmax_add(date_bounds, parsed_lower)
                date_bounds = (date_bounds[0], max(date_bounds[1], parsed_upper))
        if date_bounds is not None:
            lower, upper = date_bounds
            lower_ns, upper_ns = _date_ns(lower), _date_ns(upper)
            if lower_ns is not None:
                info[start_key] = lower_ns if info.get(start_key) is None else min(info[start_key], lower_ns)
            if upper_ns is not None:
                end_ns = _checked_ns(upper_ns + DAY_NS)
                info[end_key] = end_ns if info.get(end_key) is None else max(info[end_key], end_ns)
            if category == "calendar":
                _update_date_bounds(info, lower, upper)
            info["precision"] = info.get("precision") or "calendar_day"

    # Availability and explicit schedule columns use exact typed timestamp
    # bounds.  They never replace an event or calendar observation.
    for fields, start_key, end_key in (
        (info.get("availability_fields", []), "available_start_ns", "available_end_ns"),
        (info.get("schedule_fields", []), "scheduled_start_ns", "scheduled_end_ns"),
    ):
        for field in fields:
            if field not in field_types:
                continue
            bounds = _parquet_field_bounds(parquet, schema_names, field, field_types[field], dataset_id)
            if bounds is not None and isinstance(bounds[0], int):
                _bound_update(info, start_key, end_key, bounds[0], end=bounds[1] + 1)

    # Derived continuous futures metadata has two interval families.  The
    # roll pair is already half-open in both native ms and UTC companion
    # fields; instrument maps carry first/last bar and definition evidence.
    field_keys = {_field_key(field): field for field in schema_names}
    roll_start = [field_keys[key] for key in ("segment_start_ms", "segment_start_ts_utc") if key in field_keys]
    roll_end = [field_keys[key] for key in ("segment_end_exclusive_ms", "segment_end_exclusive_ts_utc") if key in field_keys]
    if roll_start and roll_end:
        info["metadata_field"] = roll_start[0]
        info["metadata_timestamp_unit"] = native_timestamp_unit(dataset_id, roll_start[0]) or _field_unit(roll_start[0]) or "timestamp"
        roll_bounds = _metadata_pair_bounds(
            parquet, schema_names, field_types, roll_start, roll_end, dataset_id,
            end_is_exclusive=True,
        )
        if roll_bounds is not None:
            info["roll_start_ns"], info["roll_end_ns"] = roll_bounds
            info["metadata_start_ns"], info["metadata_end_ns"] = roll_bounds
            info["metadata_basis"] = "roll_segment_interval"
        # The last live segment has no end in the acquired roll maps.  The
        # maximum of the closed segments must not be presented as the end of
        # the whole map (which would falsely truncate the current contract).
        pair = parquet.read(columns=[roll_start[0], roll_end[0]])
        start_type = field_types[roll_start[0]]
        unit = start_type.unit if pa.types.is_timestamp(start_type) else native_timestamp_unit(dataset_id, roll_start[0])
        factor = {"s": NS, "ms": MS_NS, "us": 1_000, "ns": 1}.get(unit)
        if factor is not None:
            starts = pair.column(0).cast(pa.int64()).to_pylist()
            end_nulls = pair.column(1).is_null().to_pylist()
            present_starts = [int(value) * factor for value in starts if value is not None]
            open_starts = [int(value) * factor for value, is_null in zip(starts, end_nulls)
                           if value is not None and is_null]
            if present_starts and open_starts:
                last_start = max(present_starts)
                info["roll_unknown_end_count"] = sum(value != last_start for value in open_starts)
                if last_start in open_starts:
                    info["roll_open_ended"] = True
                    info["roll_open_segment_start_ns"] = last_start
                    info["roll_closed_end_ns"] = info.get("roll_end_ns")
                    info["roll_start_ns"] = min(present_starts)
                    info["roll_end_ns"] = None
                    info["metadata_start_ns"] = min(present_starts)
                    info["metadata_end_ns"] = max(info.get("metadata_end_ns") or 0, last_start + 1)
                    info["metadata_basis"] = "observed_segment_starts_and_closed_ends; latest_segment_open_ended"
                if info["roll_unknown_end_count"]:
                    holes.append({"reason": "nonterminal_roll_segment_end_unknown", "missing_fields": roll_end})
    definition_start = [field_keys[key] for key in ("first_definition_ns", "first_definition_ts_utc") if key in field_keys]
    definition_end = [field_keys[key] for key in ("last_definition_ns", "last_definition_ts_utc") if key in field_keys]
    definition_bounds = None
    if definition_start and definition_end:
        info["metadata_field"] = info.get("metadata_field") or definition_start[0]
        info["metadata_timestamp_unit"] = info.get("metadata_timestamp_unit") or native_timestamp_unit(dataset_id, definition_start[0]) or _field_unit(definition_start[0]) or "timestamp"
        definition_bounds = _metadata_pair_bounds(
            parquet, schema_names, field_types, definition_start, definition_end, dataset_id,
        )
    if event_values is not None and artifact_role == "contract_definition":
        definition_bounds = (
            event_values[0],
            _observation_end_ns(dataset_id, event_values[1] + 1),
        ) if definition_bounds is None else definition_bounds
    if definition_bounds is not None:
        info["definition_start_ns"], info["definition_end_ns"] = definition_bounds
        if info.get("metadata_start_ns") is None:
            info["metadata_start_ns"], info["metadata_end_ns"] = definition_bounds
        else:
            info["metadata_start_ns"] = min(info["metadata_start_ns"], definition_bounds[0])
            info["metadata_end_ns"] = max(info["metadata_end_ns"], definition_bounds[1])
        info["metadata_basis"] = info.get("metadata_basis") or "contract_definition_interval"
    bar_start = [field_keys[key] for key in ("first_bar_ms", "first_bar_ts_utc") if key in field_keys]
    bar_end = [field_keys[key] for key in ("last_bar_ms", "last_bar_ts_utc") if key in field_keys]
    bar_bounds = None
    if bar_start and bar_end:
        info["metadata_field"] = info.get("metadata_field") or bar_start[0]
        info["metadata_timestamp_unit"] = info.get("metadata_timestamp_unit") or native_timestamp_unit(dataset_id, bar_start[0]) or _field_unit(bar_start[0]) or "timestamp"
        bar_bounds = _metadata_pair_bounds(
            parquet, schema_names, field_types, bar_start, bar_end, dataset_id,
        )
    if bar_bounds is not None:
        if info.get("metadata_start_ns") is None:
            info["metadata_start_ns"], info["metadata_end_ns"] = bar_bounds
        else:
            info["metadata_start_ns"] = min(info["metadata_start_ns"], bar_bounds[0])
            info["metadata_end_ns"] = max(info["metadata_end_ns"], bar_bounds[1])
        info["metadata_basis"] = info.get("metadata_basis") or "instrument_observation_interval"

    info["date_only"] = bool(
        info.get("calendar_start_ns") is not None
        and info.get("event_start_ns") is None
        and info.get("scheduled_start_ns") is None
    )
    info["temporal_basis"] = (
        "event_timestamp" if info.get("event_start_ns") is not None else
        "roll_metadata_interval" if info.get("roll_start_ns") is not None else
        "contract_definition_interval" if info.get("definition_start_ns") is not None else
        "scheduled_calendar" if info.get("scheduled_start_ns") is not None else
        "calendar_date" if info.get("calendar_start_ns") is not None else None
    )
    holes.extend(_temporal_holes(info, schema_names, dataset_id=dataset_id, artifact_role=artifact_role))
    return info, holes


def _inspect_file(
    data_root: Path,
    path: Path,
    *,
    dataset_id: str,
    manifest_row: Mapping[str, str] | None = None,
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = catalog or load_catalog(data_root)
    manifest_row = manifest_row or {}
    artifact_role = _artifact_role(path, dataset_id)
    schema_items = _schema_from_manifest(dataset_id, catalog)
    schema_names = [str(item.get("name")) for item in schema_items if item.get("name")]
    rows: int | None = None
    start_ns: int | None = None
    end_ns: int | None = None
    bounds_source: str | None = None
    temporal = _manifest_temporal_bounds(manifest_row, dataset_id)
    temporal_holes: list[dict[str, Any]] = []
    format_name = manifest_row.get("format") or path.suffix.lower().lstrip(".")
    errors: list[str] = []
    if path.is_file() and path.suffix.lower() == ".parquet" and artifact_role not in {"manifest", "raw_provenance", "provenance"}:
        try:
            import pyarrow.parquet as pq  # type: ignore
        except ImportError:
            if not schema_names:
                errors.append("schema_unavailable:pyarrow")
        else:
            try:
                parquet = pq.ParquetFile(path)
                rows = parquet.metadata.num_rows
                schema_names = list(parquet.schema_arrow.names)
                temporal, temporal_holes = _parquet_temporal(
                    parquet, schema_names, dataset_id, artifact_role=artifact_role)
                if temporal.get("event_start_ns") is not None and temporal.get("event_end_ns") is not None:
                    start_ns = temporal["event_start_ns"]
                    end_ns = temporal["event_end_ns"]
                    bounds_source = "parquet_statistics"
                elif temporal.get("metadata_start_ns") is not None and temporal.get("metadata_end_ns") is not None:
                    start_ns = temporal["metadata_start_ns"]
                    end_ns = temporal["metadata_end_ns"]
                    bounds_source = "parquet_metadata_statistics"
            except Exception as exc:  # malformed/partial file is a coverage hole
                errors.append(f"parquet_unreadable:{type(exc).__name__}")
    elif path.is_file() and path.suffix.lower() in {".csv", ".tsv", ".txt", ".json", ".jsonl"} and artifact_role == "data":
        try:
            actual_fields, actual_temporal, actual_rows, temporal_holes = _infer_text_temporal(path, dataset_id, artifact_role=artifact_role)
            if actual_fields:
                schema_names = actual_fields
            rows = actual_rows
            temporal = actual_temporal
            if temporal.get("event_start_ns") is not None and temporal.get("event_end_ns") is not None:
                start_ns, end_ns, bounds_source = temporal["event_start_ns"], temporal["event_end_ns"], "rows"
        except Exception as exc:
            errors.append(f"text_unreadable:{type(exc).__name__}")
    elif artifact_role == "data":
        # A retained archive/provenance extension can still have manifest
        # bounds, but it is not parsed as an observation source here.
        temporal_holes = _temporal_holes(temporal, schema_names, dataset_id=dataset_id, artifact_role=artifact_role)
    else:
        temporal_holes = _temporal_holes(temporal, schema_names, dataset_id=dataset_id, artifact_role=artifact_role)

    # If a manifest supplies only a calendar span and the parser cannot read
    # the source, retain that scope as calendar metadata.  Never copy it into
    # ``observed_*`` or ``available_*`` fields.
    if artifact_role == "data":
        if temporal.get("event_start_ns") is None and temporal.get("calendar_start_ns") is None:
            for key in ("calendar_start_ns", "calendar_end_ns", "date_min", "date_max", "date_only", "temporal_basis"):
                if temporal.get(key) is None and _manifest_temporal_bounds(manifest_row, dataset_id).get(key) is not None:
                    temporal[key] = _manifest_temporal_bounds(manifest_row, dataset_id)[key]
    if rows is None and manifest_row.get("rows") not in (None, ""):
        try:
            rows = int(manifest_row["rows"])
        except ValueError:
            rows = None
    event_field = temporal.get("event_field")
    calendar_fields = temporal.get("calendar_fields") or []
    metadata_field = temporal.get("metadata_field")
    timestamp_field = event_field or metadata_field or (
        calendar_fields[0]
        if calendar_fields and not temporal.get("calendar_component_fields")
        else None
    )
    unit = None
    if event_field:
        unit = native_timestamp_unit(dataset_id, event_field) or _field_unit(event_field) or "timestamp"
    elif metadata_field:
        unit = temporal.get("metadata_timestamp_unit") or native_timestamp_unit(dataset_id, metadata_field) or _field_unit(metadata_field) or "timestamp"
    elif timestamp_field and _is_calendar_field(timestamp_field):
        unit = None
    required = _required_fields(dataset_id)
    missing_fields = [name for name in required if name not in schema_names and name.upper() not in schema_names]
    valid = path.is_file() and path.stat().st_size > 0 and not errors and not missing_fields
    if required and unit is None and "t" in required:
        valid = False
        errors.append("timestamp_unit_unknown")
    if required and (start_ns is None or end_ns is None):
        valid = False
        errors.append("time_bounds_unavailable")
    if end_ns is not None and start_ns is not None and end_ns <= start_ns:
        valid = False
        errors.append("invalid_time_bounds")
    event_bounds = temporal.get("event_start_ns") is not None and temporal.get("event_end_ns") is not None
    calendar_bounds = temporal.get("calendar_start_ns") is not None and temporal.get("calendar_end_ns") is not None
    scheduled_bounds = temporal.get("scheduled_start_ns") is not None and temporal.get("scheduled_end_ns") is not None
    available_bounds = temporal.get("available_start_ns") is not None and temporal.get("available_end_ns") is not None
    if artifact_role in {"manifest", "raw_provenance", "provenance"}:
        coverage_status = "provenance_only"
        coverage_valid: bool | None = False
    elif artifact_role == "contract_definition":
        coverage_status = "contract_definition_metadata"
        coverage_valid = None
    elif artifact_role == "roll_metadata":
        coverage_status = "roll_metadata"
        coverage_valid = None
    elif event_bounds:
        coverage_status = "timed_observations"
        coverage_valid = True
    elif scheduled_bounds:
        coverage_status = "scheduled_calendar_only"
        coverage_valid = None
    elif calendar_bounds:
        coverage_status = "calendar_date_only"
        coverage_valid = None
    else:
        coverage_status = "no_temporal_bounds"
        coverage_valid = False
    temporal["temporal_holes"] = [*temporal.get("temporal_holes", []), *temporal_holes]
    # Stable de-duplication keeps one clear reason per source field while
    # allowing different holes (publication, vintage, parser) to coexist.
    unique_holes: list[dict[str, Any]] = []
    seen_holes: set[tuple[str, tuple[str, ...]]] = set()
    for hole in temporal["temporal_holes"]:
        key = (str(hole.get("reason")), tuple(sorted(str(v) for v in hole.get("missing_fields", []))))
        if key not in seen_holes:
            unique_holes.append({"reason": key[0], "missing_fields": list(key[1])})
            seen_holes.add(key)
    temporal["temporal_holes"] = unique_holes
    coverage_missing_fields = sorted({field for hole in unique_holes for field in hole.get("missing_fields", [])})
    date_start_ns = temporal.get("calendar_start_ns")
    date_end_ns = temporal.get("calendar_end_ns")
    return {
        "path": str(path),
        "archive_path": str(path.relative_to(data_root)) if path.is_relative_to(data_root) else str(path),
        "dataset_id": dataset_id,
        "artifact_role": artifact_role,
        "source_role": artifact_role,
        "format": format_name,
        "bytes": path.stat().st_size if path.is_file() else 0,
        "rows": rows,
        "schema": schema_names,
        "required_fields": list(required),
        "missing_fields": missing_fields,
        "coverage_missing_fields": coverage_missing_fields,
        "missing_temporal_fields": coverage_missing_fields,
        "timestamp_field": timestamp_field,
        "timestamp_unit": unit,
        "metadata_timestamp_field": metadata_field,
        "metadata_timestamp_unit": temporal.get("metadata_timestamp_unit"),
        "observed_start_ns": start_ns,
        "observed_end_ns": end_ns,
        "bounds_source": bounds_source,
        "event_start_ns": temporal.get("event_start_ns"),
        "event_end_ns": temporal.get("event_end_ns"),
        "definition_start_ns": temporal.get("definition_start_ns"),
        "definition_end_ns": temporal.get("definition_end_ns"),
        "roll_start_ns": temporal.get("roll_start_ns"),
        "roll_end_ns": temporal.get("roll_end_ns"),
        "roll_closed_end_ns": temporal.get("roll_closed_end_ns"),
        "roll_open_ended": temporal.get("roll_open_ended", False),
        "roll_open_segment_start_ns": temporal.get("roll_open_segment_start_ns"),
        "roll_unknown_end_count": temporal.get("roll_unknown_end_count", 0),
        "metadata_start_ns": temporal.get("metadata_start_ns"),
        "metadata_end_ns": temporal.get("metadata_end_ns"),
        "metadata_basis": temporal.get("metadata_basis"),
        "calendar_start_ns": date_start_ns,
        "calendar_end_ns": date_end_ns,
        "date_start_ns": date_start_ns,
        "date_end_ns": date_end_ns,
        "observed_date_start_ns": date_start_ns,
        "observed_date_end_ns": date_end_ns,
        "reference_start_ns": temporal.get("reference_start_ns"),
        "reference_end_ns": temporal.get("reference_end_ns"),
        "vintage_start_ns": temporal.get("vintage_start_ns"),
        "vintage_end_ns": temporal.get("vintage_end_ns"),
        "scheduled_start_ns": temporal.get("scheduled_start_ns"),
        "scheduled_end_ns": temporal.get("scheduled_end_ns"),
        "available_start_ns": temporal.get("available_start_ns"),
        "available_end_ns": temporal.get("available_end_ns"),
        "availability_start_ns": temporal.get("available_start_ns"),
        "availability_end_ns": temporal.get("available_end_ns"),
        "available_at": temporal.get("available_start_ns"),
        "available_at_min_ns": temporal.get("available_start_ns"),
        "available_at_max_ns": temporal.get("available_end_ns"),
        "date_min": temporal.get("date_min"),
        "date_max": temporal.get("date_max"),
        "temporal_fields": {
            "event": temporal.get("event_field"),
            "calendar": list(temporal.get("calendar_fields") or []),
            "reference": list(temporal.get("reference_fields") or []),
            "vintage": list(temporal.get("vintage_fields") or []),
            "availability": list(temporal.get("availability_fields") or []),
            "schedule": list(temporal.get("schedule_fields") or []),
            "clock": list(temporal.get("clock_fields") or []),
            "calendar_components": list(temporal.get("calendar_component_fields") or []),
        },
        "temporal_basis": temporal.get("temporal_basis"),
        "temporal_precision": temporal.get("precision"),
        "source_timezone": temporal.get("source_timezone"),
        "timezone_basis": temporal.get("timezone_basis"),
        "date_only": temporal.get("date_only") is True,
        "coverage_status": coverage_status,
        "coverage_valid": coverage_valid,
        "coverage_holes": temporal["temporal_holes"],
        "valid": valid,
        "errors": errors,
    }


def _relevant_dataset(dataset_id: str) -> bool:
    lower = dataset_id.lower()
    if lower.startswith("quantpad/cme__") and any(token in lower for token in ("ohlcv-1m", "ohlcv-1s", "trades", "mbp-1")):
        return True
    if lower.startswith("derived/continuous-futures__instrument-and-roll-maps"):
        return True
    if lower.startswith("thetadata-opra/") or lower.startswith("free-sources/"):
        return True
    if lower.startswith("databento/cme__") and any(token in lower for token in ("trades", "mbp-1", "ohlcv")):
        return True
    return False


def _relevant_for_method(dataset_id: str, method_id: str | None) -> bool:
    """Apply the C03 transport inventory to the selected method's inputs."""

    if method_id is None:
        return _relevant_dataset(dataset_id)
    lower = dataset_id.lower()
    if method_id == 'STOIC-RISK':
        return False  # The acquired tape is not a prior account/process journal.
    if method_id == 'STOIC-DATA':
        return lower.startswith('free-sources/')
    if method_id == 'SIRES':
        return (lower.startswith('quantpad/cme__') and 'continuous-futures' in lower
                or lower.startswith('derived/continuous-futures__instrument-and-roll-maps')
                or lower.startswith('free-sources/')
                or lower.startswith('thetadata-opra/opra__') and any(f'__{symbol}-' in lower for symbol in ('qqq', 'spy')))
    # M01 names continuous futures, instrument/roll definitions and optional
    # normalized calendar/volatility context.  Avoid sweeping unrelated
    # options and native reference archives into its inventory.
    return (
        lower.startswith("quantpad/cme__")
        and "continuous-futures" in lower
        or lower.startswith("derived/continuous-futures__instrument-and-roll-maps")
        or method_id in {'JJ-TBR', 'GB-FAIL', 'GB-SCALP'} and lower.startswith("free-sources/context__")
    )


def _discover_relevant_paths(data_root: Path, *, method_id: str | None = None, manifest_rows: Sequence[Mapping[str, str]] = ()) -> list[tuple[Path, str]]:
    paths: dict[str, tuple[Path, str]] = {}
    if manifest_rows:
        # The manifest gives us an explicit file list and avoids recursively
        # walking a multi-terabyte acquired root on every method pass.
        for row in manifest_rows:
            archive = row.get("archive_path") or ""
            dataset_id = row.get("dataset_id") or "/".join(archive.split("/")[:2])
            if not archive or not _relevant_for_method(dataset_id, method_id):
                continue
            path = data_root / archive
            if path.is_file():
                paths[str(path)] = (path, dataset_id)
        # Continue with a bounded directory scan so a newly acquired file is
        # visible even when the inventory CSV predates it.  The method filter
        # keeps this to the relevant dataset directories rather than walking
        # every provider archive.
    providers = ("quantpad", "derived", "thetadata-opra", "free-sources", "databento")
    for provider in providers:
        base = data_root / provider
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if not child.is_dir():
                continue
            dataset_id = f"{provider}/{child.name}"
            if not _relevant_for_method(dataset_id, method_id):
                continue
            for path in child.rglob("*"):
                if path.is_file() and path.suffix.lower() in {
                    ".parquet", ".csv", ".tsv", ".txt", ".json", ".jsonl", ".zst",
                    ".htm", ".html", ".pdf", ".xml", ".zip", ".sha256", ".py",
                }:
                    paths[str(path)] = (path, dataset_id)
    return sorted(paths.values(), key=lambda item: str(item[0]))


def _date_year(ns: int) -> int:
    seconds, _nanos = divmod(int(ns), NS)
    return datetime.fromtimestamp(seconds, tz=timezone.utc).year


def _record_bounds(record: Mapping[str, Any]) -> tuple[int | None, int | None, str | None]:
    """Choose the primary coverage interval without promoting dates to events."""

    metadata_start, metadata_end = record.get("metadata_start_ns"), record.get("metadata_end_ns")
    if (record.get("artifact_role") in {"contract_definition", "roll_metadata"}
            and metadata_start is not None and metadata_end is not None):
        return int(metadata_start), int(metadata_end), "metadata_interval"
    event_start = record.get("event_start_ns")
    event_end = record.get("event_end_ns")
    if event_start is not None and event_end is not None:
        return int(event_start), int(event_end), "event_timestamp"
    calendar_start = record.get("calendar_start_ns", record.get("date_start_ns"))
    calendar_end = record.get("calendar_end_ns", record.get("date_end_ns"))
    if calendar_start is not None and calendar_end is not None:
        return int(calendar_start), int(calendar_end), "calendar_date"
    scheduled_start, scheduled_end = record.get("scheduled_start_ns"), record.get("scheduled_end_ns")
    if scheduled_start is not None and scheduled_end is not None:
        return int(scheduled_start), int(scheduled_end), "scheduled_calendar"
    if metadata_start is not None and metadata_end is not None:
        return int(metadata_start), int(metadata_end), "metadata_interval"
    # Compatibility with records constructed by older callers that only have
    # the generic observed lane.  Do not let a present-but-null event key hide
    # these verified file bounds.
    observed_start, observed_end = record.get("observed_start_ns"), record.get("observed_end_ns")
    if observed_start is not None and observed_end is not None:
        return int(observed_start), int(observed_end), "observed_file_bounds"
    return None, None, None


def _record_year_bounds(record: Mapping[str, Any], start: int, end: int, basis: str) -> tuple[int, int]:
    # Civil date fields are labeled source dates.  Derive their years from the
    # labels themselves rather than converting UTC midnight through ET, which
    # would put New Year's Day at the prior ET year.
    if basis == "calendar_date":
        try:
            lower = date.fromisoformat(str(record.get("date_min")))
            upper = date.fromisoformat(str(record.get("date_max")))
            return lower.year, upper.year
        except (TypeError, ValueError):
            pass
    return ns_to_et(int(start)).year, ns_to_et(int(max(start, end - 1))).year


def _year_rows(
    records: Sequence[Mapping[str, Any]],
    *,
    requested_manifest: Sequence[Mapping[str, Any]] = (),
    data_root: Path | None = None,
    method_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    years: dict[str, dict[str, Any]] = {}
    for record in records:
        start, end, basis = _record_bounds(record)
        if start is None or end is None:
            continue
        first_year, last_year = _record_year_bounds(record, start, end, basis or "")
        for year in range(first_year, last_year + 1):
            key = str(year)
            row = years.setdefault(key, {"status": "partial", "file_count": 0, "datasets": [], "holes": [],
                                         "coverage_basis": basis or "observed_file_bounds_only",
                                         "coverage_statuses": [], "calendar_file_count": 0,
                                         "timed_file_count": 0})
            row["file_count"] += 1
            if basis == "calendar_date":
                row["calendar_file_count"] += 1
            else:
                row["timed_file_count"] += 1
            if basis and basis not in row["coverage_basis"].split(","):
                row["coverage_basis"] = f"{row['coverage_basis']},{basis}"
            status = record.get("coverage_status")
            if status and status not in row["coverage_statuses"]:
                row["coverage_statuses"].append(status)
            if record.get("dataset_id") not in row["datasets"]:
                row["datasets"].append(record.get("dataset_id"))
            record_holes = [str(hole.get("reason")) if isinstance(hole, Mapping) else str(hole)
                            for hole in (record.get("coverage_holes") or [])]
            record_holes.extend(str(value) for value in (record.get("errors") or record.get("missing_fields") or []))
            metadata_only = record.get("artifact_role") in {"contract_definition", "roll_metadata"}
            if metadata_only:
                # Mapping metadata spans identify contracts/segments; they do
                # not claim that market observations fill the represented
                # years.  Keep this visible in the year ledger.
                if row["status"] == "partial" and row["file_count"] == 1:
                    row["status"] = "metadata_only"
            if record.get("valid") is not True or record.get("coverage_valid") is not True:
                if metadata_only and not record_holes:
                    continue
                row["status"] = "partial"
                for hole in record_holes:
                    if hole not in row["holes"]:
                        row["holes"].append(hole)
            else:
                # A file min/max pair proves that records were observed at its
                # endpoints only.  It never proves an entire civil year is
                # continuously covered.
                if not metadata_only:
                    row["status"] = "partial"
                    if "bounds_do_not_prove_continuity" not in row["holes"]:
                        row["holes"].append("bounds_do_not_prove_continuity")
    # A manifest is a requested inventory, not proof that the corresponding
    # archive file is present.  Preserve years named only by missing manifest
    # rows as uncovered so a min/max span cannot manufacture all-year coverage.
    for manifest_row in requested_manifest:
        dataset_id = manifest_row.get("dataset_id", "")
        if not _relevant_for_method(dataset_id, method_id):
            continue
        manifest_temporal = _manifest_temporal_bounds(manifest_row, dataset_id)
        start, end, basis = _record_bounds(manifest_temporal)
        if start is None or end is None:
            continue
        first_year, last_year = _record_year_bounds(manifest_temporal, start, end, basis or "")
        for year in range(first_year, last_year + 1):
            key = str(year)
            row = years.setdefault(key, {"status": "uncovered", "file_count": 0, "datasets": [], "holes": [],
                                         "coverage_basis": "manifest_request_only", "coverage_statuses": [],
                                         "calendar_file_count": 0, "timed_file_count": 0})
            archive = manifest_row.get("archive_path") or ""
            exists = data_root is not None and (data_root / archive).is_file()
            if exists:
                # Existing rows were already measured above.  Keep the actual
                # row's partial status and only add the dataset identity.
                if dataset_id not in row["datasets"]:
                    row["datasets"].append(dataset_id)
            else:
                row["status"] = "uncovered" if row["file_count"] == 0 else "partial"
                if dataset_id not in row["datasets"]:
                    row["datasets"].append(dataset_id)
                if "manifest_file_missing" not in row["holes"]:
                    row["holes"].append("manifest_file_missing")
    for row in years.values():
        row["continuity_checked"] = False
        if row["status"] == "uncovered":
            row["reason"] = "Requested manifest files have no observed inventory for this year"
        elif "manifest_file_missing" in row["holes"]:
            row["status"] = "missing_files"
            row["reason"] = "At least one requested source file is absent"
        elif row["status"] != "metadata_only":
            row["status"] = "observed_bounds_only"
            row["reason"] = "Observed file bounds; continuity is not established by this inventory"
        if "bounds_do_not_prove_continuity" in row["holes"]:
            row["holes"].remove("bounds_do_not_prove_continuity")
    return years


def _span_bounds(records: Sequence[Mapping[str, Any]], kind: str) -> list[tuple[int, int]]:
    if kind == "event":
        keys = ("event_start_ns", "event_end_ns")
    elif kind == "calendar":
        keys = ("calendar_start_ns", "calendar_end_ns")
    elif kind == "scheduled":
        keys = ("scheduled_start_ns", "scheduled_end_ns")
    elif kind == "availability":
        keys = ("available_start_ns", "available_end_ns")
    elif kind == "definition":
        keys = ("definition_start_ns", "definition_end_ns")
    elif kind == "roll":
        keys = ("roll_start_ns", "roll_end_ns")
    elif kind == "metadata":
        keys = ("metadata_start_ns", "metadata_end_ns")
    else:
        keys = ("observed_start_ns", "observed_end_ns")
    return [(int(row[keys[0]]), int(row[keys[1]])) for row in records
            if row.get(keys[0]) is not None and row.get(keys[1]) is not None]


def _span_from_bounds(bounds: Sequence[tuple[int, int]], basis: str) -> dict[str, Any]:
    if not bounds:
        return {"min": None, "max": None, "min_ns": None, "max_ns": None, "basis": "no_verified_bounds"}
    lo, hi = min(start for start, _ in bounds), max(end for _, end in bounds)
    return {"min": lo, "max": hi, "min_ns": lo, "max_ns": hi, "basis": basis}


def _span_summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize actual dates while exposing event/schedule/availability lanes."""

    event = _span_from_bounds(_span_bounds(records, "event"), "observed_event_bounds")
    calendar = _span_from_bounds(_span_bounds(records, "calendar"), "calendar_date_bounds")
    scheduled = _span_from_bounds(_span_bounds(records, "scheduled"), "scheduled_calendar_bounds")
    availability = _span_from_bounds(_span_bounds(records, "availability"), "available_at_bounds")
    definition = _span_from_bounds(_span_bounds(records, "definition"), "contract_definition_bounds")
    roll = _span_from_bounds(_span_bounds(records, "roll"), "roll_metadata_bounds")
    metadata = _span_from_bounds(_span_bounds(records, "metadata"), "metadata_bounds")
    # Preserve true event precision when present.  Date-only records use a
    # separately labeled civil-day span; scheduled clocks are a fallback only
    # for sources with no independent date field.
    if event["min_ns"] is not None:
        primary = dict(event)
        primary["basis"] = "observed_event_bounds"
    elif calendar["min_ns"] is not None:
        primary = dict(calendar)
        primary["basis"] = "calendar_date_bounds"
    elif scheduled["min_ns"] is not None:
        primary = dict(scheduled)
    elif metadata["min_ns"] is not None:
        primary = dict(metadata)
    else:
        primary = _span_from_bounds(_span_bounds(records, "observed"), "observed_file_bounds")
    primary.update({"event": event, "calendar": calendar, "scheduled": scheduled, "availability": availability,
                    "definition": definition, "roll": roll, "metadata": metadata,
                    "event_min_ns": event["min_ns"], "event_max_ns": event["max_ns"],
                    "calendar_min_ns": calendar["min_ns"], "calendar_max_ns": calendar["max_ns"],
                    "scheduled_min_ns": scheduled["min_ns"], "scheduled_max_ns": scheduled["max_ns"],
                    "available_min_ns": availability["min_ns"], "available_max_ns": availability["max_ns"],
                    "definition_min_ns": definition["min_ns"], "definition_max_ns": definition["max_ns"],
                    "roll_min_ns": roll["min_ns"], "roll_max_ns": roll["max_ns"],
                    "metadata_min_ns": metadata["min_ns"], "metadata_max_ns": metadata["max_ns"]})
    return primary


def _instrument_roots(records: Sequence[Mapping[str, Any]]) -> list[str]:
    roots: set[str] = set()
    pattern = re.compile(r"cme__([a-z0-9]+)-continuous-futures(?:__|/)", re.I)
    for record in records:
        match = pattern.search(str(record.get("dataset_id", "")))
        if match:
            roots.add(match.group(1).upper())
    return sorted(roots)


def _instrument_definitions(data_root: Path, records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Read actual instrument-definition rows when the source is readable."""

    result: list[dict[str, Any]] = []
    for record in records:
        dataset_id = str(record.get("dataset_id", ""))
        path = Path(str(record.get("path", "")))
        if "instrument-and-roll-maps" not in dataset_id or "instruments" not in path.name:
            continue
        try:
            rows = list(iter_source_rows(path))
        except Exception as exc:
            result.append({"path": str(path), "status": "unavailable", "reason": f"schema_or_reader:{type(exc).__name__}"})
            continue
        for row in rows:
            instrument_id = _row_value(row, "instrument_id", "instrument")
            if instrument_id is None:
                continue
            tick = _row_value(row, "min_price_increment", "tick_size", "price_increment")
            result.append({
                "path": str(path),
                "status": "available",
                "instrument_id": instrument_id,
                "raw_symbol": _row_value(row, "raw_symbol", "symbol"),
                "root": _row_value(row, "root"),
                "min_price_increment": None if tick is None else str(dec(tick)),
                "contract_multiplier": _row_value(row, "contract_multiplier"),
            })
    return result


def _file_instrument_stats(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Expose per-file instrument identity without guessing a contract."""

    stats: list[dict[str, Any]] = []
    for record in records:
        if "instrument_id" not in record.get("schema", []):
            continue
        path = Path(record["path"])
        try:
            if path.suffix == '.parquet':
                import pyarrow.parquet as pq
                parquet = pq.ParquetFile(path)
                index = list(parquet.schema_arrow.names).index('instrument_id')
                bounds, ids, complete = [], set(), True
                for group in range(parquet.num_row_groups):
                    column = parquet.metadata.row_group(group).column(index)
                    stat = column.statistics
                    if stat is None or stat.min is None or stat.max is None:
                        complete = False
                        continue
                    bounds.append({'row_group': group, 'min': stat.min, 'max': stat.max})
                    ids.update([str(stat.min), str(stat.max)])
                    complete = complete and stat.min == stat.max and stat.null_count == 0
                stats.append({'path': str(path), 'instrument_ids': sorted(ids),
                              'complete_inventory': complete, 'row_group_bounds': bounds,
                              'status': 'exact_from_constant_row_groups' if complete else 'partial_metadata_bounds'})
                continue
            ids = sorted({str(_row_value(row, "instrument_id", "instrument")) for row in iter_source_rows(path) if _row_value(row, "instrument_id", "instrument") is not None})
            stats.append({"path": str(path), "instrument_ids": ids, "status": "available"})
        except Exception as exc:
            stats.append({"path": str(path), "instrument_ids": [], "status": "unavailable", "reason": f"schema_or_reader:{type(exc).__name__}"})
    return stats


def _coverage_hole(
    *,
    method_id: str | None,
    dataset_id: str | None,
    path: str | None,
    reason: str,
    missing_fields: Sequence[str] = (),
    start_ns: int | None = None,
    end_ns: int | None = None,
) -> dict[str, Any]:
    method = method_id or "acquired"
    dataset = dataset_id or "unknown"
    digest = hashlib.sha1(f"{method}|{dataset}|{path}|{reason}|{start_ns}|{end_ns}".encode()).hexdigest()[:16]
    return {
        "hole_id": f"HOLE:O001:{method}:{digest}",
        "recipe_id": "O001",
        "method_id": method_id,
        "branch": "all",
        "candidate_id": None,
        "kind": "data_coverage",
        "missing_fields": list(missing_fields),
        "source_ref": "C03",
        "affected_output": "coverage",
        "reason": reason,
        "dataset_id": dataset_id,
        "path": path,
        "start_ns": start_ns,
        "end_ns": end_ns,
    }


def inventory_acquired(data_root: Path | str = DATA_ROOT_DEFAULT, method_id: str | None = None) -> dict[str, Any]:
    """Inventory actual relevant files under a caller-supplied data root.

    The result is deliberately method-neutral at the transport layer; the
    optional ``method_id`` is retained for the report seam.  File rows include
    physical paths, schema, native timestamp units, actual bounds, and holes.
    """

    root = Path(data_root)
    catalog = load_catalog(root)
    manifest_index = _manifest_index(root)
    manifest_rows = catalog.get("files") or []
    discovered = _discover_relevant_paths(root, method_id=method_id, manifest_rows=manifest_rows)
    discovered_keys = {str(item[0]) for item in discovered}
    for archive, row in manifest_index.items():
        dataset = row.get("dataset_id") or "/".join(archive.split("/")[:2])
        if not _relevant_for_method(dataset, method_id):
            continue
        path = root / archive
        if path.is_file() and str(path) not in discovered_keys:
            discovered.append((path, dataset))
            discovered_keys.add(str(path))
    discovered.sort(key=lambda item: str(item[0]))
    def inspect(item):
        path, dataset_id = item
        archive = path.relative_to(root).as_posix()
        row = manifest_index.get(archive)
        return _inspect_file(root, path, dataset_id=dataset_id, manifest_row=row, catalog=catalog)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as readers:
        files = list(readers.map(inspect, discovered))
    ownership = ownership_manifest(root)
    holes: list[dict[str, Any]] = []
    for record in files:
        if record.get("valid") is not True:
            holes.append(_coverage_hole(
                method_id=method_id,
                dataset_id=record.get("dataset_id"),
                path=record.get("path"),
                missing_fields=record.get("missing_fields", []),
                reason=";".join(record.get("errors") or ["invalid_file"]),
                start_ns=record.get("observed_start_ns"),
                end_ns=record.get("observed_end_ns"),
            ))
        for temporal_hole in record.get("coverage_holes", []):
            if isinstance(temporal_hole, Mapping):
                reason = str(temporal_hole.get("reason", "coverage_unknown"))
                missing = temporal_hole.get("missing_fields", [])
            else:
                reason, missing = str(temporal_hole), []
            start, end, _basis = _record_bounds(record)
            holes.append(_coverage_hole(
                method_id=method_id,
                dataset_id=record.get("dataset_id"),
                path=record.get("path"),
                missing_fields=missing,
                reason=reason,
                start_ns=start,
                end_ns=end,
            ))
    for ownership_hole in ownership.get("holes", []):
        holes.append(_coverage_hole(
            method_id=method_id,
            dataset_id=ownership.get("dataset_id"),
            path=ownership_hole.get("path"),
            missing_fields=ownership_hole.get("missing_fields", []),
            reason=ownership_hole.get("reason", "HOLE:DATA_OVERLAP"),
            start_ns=ownership_hole.get("start_ns"),
            end_ns=ownership_hole.get("end_ns"),
        ))
    datasets: dict[str, dict[str, Any]] = {}
    for record in files:
        summary = datasets.setdefault(record["dataset_id"], {
            "files": [], "schema": record["schema"], "timestamp_unit": record["timestamp_unit"],
            "missing_fields": [], "coverage_missing_fields": [], "artifact_roles": [],
            "coverage_statuses": [], "coverage_valid": True,
        })
        summary["files"].append(record["path"])
        if record.get("artifact_role") not in summary["artifact_roles"]:
            summary["artifact_roles"].append(record.get("artifact_role"))
        if record.get("coverage_status") not in summary["coverage_statuses"]:
            summary["coverage_statuses"].append(record.get("coverage_status"))
        if record.get("coverage_valid") is not True:
            summary["coverage_valid"] = False
        for field in record.get("missing_fields", []):
            if field not in summary["missing_fields"]:
                summary["missing_fields"].append(field)
        for field in record.get("coverage_missing_fields", []):
            if field not in summary["coverage_missing_fields"]:
                summary["coverage_missing_fields"].append(field)
    span = _span_summary(files)
    event_span = _span_from_bounds(_span_bounds(files, "event"), "observed_event_bounds")
    calendar_span = _span_from_bounds(_span_bounds(files, "calendar"), "calendar_date_bounds")
    availability_span = _span_from_bounds(_span_bounds(files, "availability"), "available_at_bounds")
    definition_span = _span_from_bounds(_span_bounds(files, "definition"), "contract_definition_bounds")
    roll_span = _span_from_bounds(_span_bounds(files, "roll"), "roll_metadata_bounds")
    metadata_span = _span_from_bounds(_span_bounds(files, "metadata"), "metadata_bounds")
    definitions = _instrument_definitions(root, files)
    identity_stats = _file_instrument_stats(files)
    # Requested is an inventory scope, not a claim of continuous data.  When
    # manifests are absent this remains explicitly empty rather than borrowing
    # the production catalog's dates.
    requested_records = []
    for row in manifest_rows:
        dataset_id = row.get("dataset_id", "")
        if not _relevant_for_method(dataset_id, method_id):
            continue
        temporal = _manifest_temporal_bounds(row, dataset_id)
        requested_records.append(temporal)
    requested_bounds = _span_summary(requested_records) if manifest_rows else span
    data_files = [record for record in files if record.get("artifact_role") == "data"]
    aggregate_coverage_valid = bool(data_files) and all(record.get("coverage_valid") is True for record in data_files)
    if not data_files:
        aggregate_coverage_status = "provenance_only"
    elif aggregate_coverage_valid:
        aggregate_coverage_status = "timed_data"
    else:
        aggregate_coverage_status = "partial_or_unknown"
    return {
        "data_root": str(root),
        "method_id": method_id,
        "requested_date_span": requested_bounds,
        "actual_date_span": span,
        "event_time_span": event_span,
        "calendar_date_span": calendar_span,
        "availability_span": availability_span,
        "definition_time_span": definition_span,
        "roll_time_span": roll_span,
        "metadata_time_span": metadata_span,
        "coverage_valid": aggregate_coverage_valid,
        "coverage_status": aggregate_coverage_status,
        "native_instruments": _instrument_roots(files),
        "instrument_definitions": definitions,
        "instrument_id_stats": identity_stats,
        "files": files,
        "datasets": datasets,
        "ownership": ownership.get("owned_spans", []),
        "ownership_holes": [
            _coverage_hole(
                method_id=method_id,
                dataset_id=ownership.get("dataset_id"),
                path=hole.get("path"),
                missing_fields=hole.get("missing_fields", []),
                reason=hole.get("reason", "HOLE:DATA_OVERLAP"),
                start_ns=hole.get("start_ns"),
                end_ns=hole.get("end_ns"),
            )
            for hole in ownership.get("holes", [])
        ],
        "timestamp_units": {record["dataset_id"]: record["timestamp_unit"] for record in files if record.get("timestamp_unit")},
        "years": _year_rows(files, requested_manifest=manifest_rows, data_root=root, method_id=method_id),
        "holes": holes,
        "relevant_file_count": len(files),
    }


def _subtract(interval: tuple[int, int], cutters: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    pieces = [interval]
    for cut_start, cut_end in cutters:
        next_pieces: list[tuple[int, int]] = []
        for start, end in pieces:
            if cut_end <= start or cut_start >= end:
                next_pieces.append((start, end))
                continue
            if start < cut_start:
                next_pieces.append((start, min(end, cut_start)))
            if cut_end < end:
                next_pieces.append((max(start, cut_end), end))
        pieces = [(start, end) for start, end in next_pieces if end > start]
    return pieces


def _overlap(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int] | None:
    start, end = max(a[0], b[0]), min(a[1], b[1])
    return (start, end) if end > start else None


def _file_overlap_fingerprint(path: Path, start_ns: int, end_ns: int, dataset_id: str) -> str | None:
    """Hash ordered overlap rows when a source is readable.

    This is used only to prove identical fallback partitions.  If a source
    cannot be read, returning ``None`` is conservative and creates a conflict
    hole rather than silently double-counting.
    """

    try:
        unit = native_timestamp_unit(dataset_id, "t")
        if unit is None:
            return None
        digest = hashlib.sha256()
        for row in iter_source_rows(path):
            raw_t = _row_value(row, "t", "ts_event")
            if raw_t is None:
                continue
            at = timestamp_ns(raw_t, unit)
            if start_ns <= at < end_ns:
                encoded = json.dumps(row, sort_keys=True, default=str, separators=(",", ":")).encode()
                # Include a length prefix so concatenated JSON rows cannot
                # collide through ambiguous boundaries.  The physical row
                # number is intentionally omitted: it is not market order.
                digest.update(len(encoded).to_bytes(8, "big"))
                digest.update(encoded)
        return digest.hexdigest()
    except Exception:
        return None


def ownership_manifest(root: Path | str = DATA_ROOT_DEFAULT) -> dict[str, Any]:
    """Freeze NQ MBP-1 monthly/weekly ownership and preserve conflict holes."""

    data_root = Path(root)
    directory = data_root / MBP1_RELATIVE
    catalog = load_catalog(data_root)
    if not directory.is_dir():
        return {"dataset_id": "quantpad/cme__nq-continuous-futures__mbp-1", "owned_spans": [], "holes": [], "files": []}
    manifest_index = _manifest_index(data_root)
    candidates: list[dict[str, Any]] = []
    holes: list[dict[str, Any]] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        match = MONTHLY_NAME.match(path.name) or WEEKLY_NAME.match(path.name)
        if match is None:
            continue
        record = _inspect_file(
            data_root,
            path,
            dataset_id="quantpad/cme__nq-continuous-futures__mbp-1",
            manifest_row=manifest_index.get(path.relative_to(data_root).as_posix()),
            catalog=catalog,
        )
        match_monthly = MONTHLY_NAME.match(path.name)
        record["partition_kind"] = "monthly" if match_monthly else "weekly"
        if record.get("valid") is not True or record.get("observed_start_ns") is None or record.get("observed_end_ns") is None:
            holes.append({
                "kind": "data_coverage",
                "path": str(path),
                "missing_fields": record.get("missing_fields", []),
                "reason": ";".join(record.get("errors") or ["invalid_file"]),
            })
            continue
        candidates.append(record)
    monthly_by_key: dict[tuple[int, int], list[dict[str, Any]]] = {}
    weekly: list[dict[str, Any]] = []
    for record in candidates:
        match_monthly = MONTHLY_NAME.match(Path(record["path"]).name)
        if match_monthly:
            monthly_by_key.setdefault((int(match_monthly.group(1)), int(match_monthly.group(2))), []).append(record)
        else:
            weekly.append(record)
    monthly_spans: list[OwnedSpan] = []
    for (year, month), records in sorted(monthly_by_key.items()):
        if len(records) != 1:
            paths = [record["path"] for record in records]
            holes.append({
                "kind": "data_coverage",
                "path": "|".join(paths),
                "missing_fields": [],
                "reason": "HOLE:DATA_OVERLAP:duplicate_monthly_partition",
            })
            continue
        record = records[0]
        month_start, month_end = _month_bounds_utc(year, month)
        start = max(int(record["observed_start_ns"]), month_start)
        end = min(int(record["observed_end_ns"]), month_end)
        if end <= start:
            holes.append({"kind": "data_coverage", "path": record["path"], "missing_fields": [], "reason": "monthly_partition_outside_named_month"})
            continue
        monthly_spans.append(OwnedSpan(record["path"], start, end, "monthly", "nq-mbp-1", source_start_ns=record["observed_start_ns"], source_end_ns=record["observed_end_ns"]))
    monthly_intervals = [(span.start_ns, span.end_ns) for span in monthly_spans]
    weekly_parts: list[tuple[dict[str, Any], int, int]] = []
    for record in weekly:
        source_interval = (int(record["observed_start_ns"]), int(record["observed_end_ns"]))
        for start, end in _subtract(source_interval, monthly_intervals):
            weekly_parts.append((record, start, end))
    # Resolve fallback overlaps only after monthly spans have been removed.
    accepted: list[tuple[dict[str, Any], int, int]] = []
    for record, start, end in sorted(weekly_parts, key=lambda item: (item[1], item[2], item[0]["path"])):
        pending = [(start, end)]
        updated: list[tuple[dict[str, Any], int, int]] = []
        for old_record, old_start, old_end in accepted:
            old_parts = [(old_start, old_end)]
            for part_start, part_end in pending:
                overlap = _overlap((part_start, part_end), (old_start, old_end))
                if overlap is None:
                    continue
                new_fingerprint = _file_overlap_fingerprint(Path(record["path"]), overlap[0], overlap[1], record["dataset_id"])
                old_fingerprint = _file_overlap_fingerprint(Path(old_record["path"]), overlap[0], overlap[1], old_record["dataset_id"])
                same = new_fingerprint is not None and new_fingerprint == old_fingerprint
                if same:
                    # A verified identical overlap is safe to assign to one
                    # deterministic owner.  Preserve either file's non-overlap
                    # pieces instead of dropping an entire weekly partition.
                    if record["path"] < old_record["path"]:
                        old_parts = _subtract((old_start, old_end), [overlap])
                    else:
                        pending = _subtract((part_start, part_end), [overlap])
                else:
                    holes.append({
                        "kind": "data_coverage",
                        "path": f"{old_record['path']}|{record['path']}",
                        "missing_fields": [],
                        "start_ns": overlap[0],
                        "end_ns": overlap[1],
                        "reason": "HOLE:DATA_OVERLAP:unverified_fallback_overlap",
                    })
                    old_parts = _subtract((old_start, old_end), [overlap])
                    pending = _subtract((part_start, part_end), [overlap])
            updated.extend((old_record, part_start, part_end) for part_start, part_end in old_parts if part_end > part_start)
        updated.extend((record, part_start, part_end) for part_start, part_end in pending if part_end > part_start)
        accepted = updated
    owned = list(monthly_spans)
    owned.extend(
        OwnedSpan(record["path"], start, end, "weekly_gap", "nq-mbp-1", source_start_ns=record["observed_start_ns"], source_end_ns=record["observed_end_ns"])
        for record, start, end in accepted
    )
    owned.sort(key=lambda span: (span.start_ns, span.end_ns, span.path))
    return {
        "dataset_id": "quantpad/cme__nq-continuous-futures__mbp-1",
        "owned_spans": ownership_as_dicts(owned),
        "holes": holes,
        "files": candidates,
    }


def freeze_mbp1_ownership(root: Path | str = DATA_ROOT_DEFAULT) -> list[OwnedSpan]:
    """Compatibility API returning owned spans plus explicit conflict holes."""

    manifest = ownership_manifest(root)
    spans = [OwnedSpan(**row) for row in manifest.get("owned_spans", [])]
    for hole in manifest.get("holes", []):
        start = int(hole.get("start_ns") or 0)
        end = int(hole.get("end_ns") or start)
        if end > start:
            spans.append(
                OwnedSpan(
                    path=str(hole.get("path", "")),
                    start_ns=start,
                    end_ns=end,
                    kind="conflict_hole",
                    dataset="nq-mbp-1",
                    status="hole",
                    reason=str(hole.get("reason", "HOLE:DATA_OVERLAP")),
                )
            )
    return sorted(spans, key=lambda span: (span.start_ns, span.end_ns, span.path))


def ownership_as_dicts(spans: Sequence[OwnedSpan]) -> list[dict[str, Any]]:
    return [asdict(span) for span in spans]


_C03_SYNTHETIC_ROWS = (
    (1785708000010094835, "A", "28565.00", 2, "28565.00", "28565.50"),
    (1785708000012065051, "B", "28565.00", 1, "28562.50", "28565.00"),
    (1785708000064473453, "B", "28565.00", 3, "28562.50", "28565.00"),
    (1785708000064473453, "B", "28565.50", 1, "28562.50", "28565.00"),
    (1785708000064473453, "B", "28566.50", 1, "28562.50", "28565.00"),
    (1785708000114275709, "A", "28560.50", 1, "28560.50", "28568.00"),
    (1785708000137317581, "A", "28565.25", 1, "28565.25", "28567.75"),
    (1785708000149312667, "B", "28565.50", 1, "28562.00", "28565.50"),
)


def _c03_result(rows: Sequence[Mapping[str, Any]], *, path: str | None, q: Decimal | None, available: bool = True, reason: str | None = None) -> dict[str, Any]:
    normalized = [normalize_mbp1_row(row, source_file=path or "<synthetic>", source_row=row.get('_source_row', index)) for index, row in enumerate(rows)]
    qualifying = [row for row in normalized if row.get("is_trade") and row.get("side") in {"A", "B"}]
    first = qualifying[:8]
    buy = sum(int(row["size"] or 0) for row in first if row["aggressor"] == "buy")
    sell = sum(int(row["size"] or 0) for row in first if row["aggressor"] == "sell")
    unknown = sum(int(row["size"] or 0) for row in first if row["aggressor"] == "unknown")
    tie_at = 1785708000064473453
    tie = [row for row in first if row["event_ns"] == tie_at]
    expected = [
        (1785708000010094835, "A", Decimal("28565.00"), 2, -2),
        (1785708000012065051, "B", Decimal("28565.00"), 1, 1),
        (1785708000064473453, "B", Decimal("28565.00"), 3, 3),
        (1785708000064473453, "B", Decimal("28565.50"), 1, 1),
        (1785708000064473453, "B", Decimal("28566.50"), 1, 1),
        (1785708000114275709, "A", Decimal("28560.50"), 1, -1),
        (1785708000137317581, "A", Decimal("28565.25"), 1, -1),
        (1785708000149312667, "B", Decimal("28565.50"), 1, 1),
    ]
    matches = len(first) == 8 and all(
        (row["event_ns"], row["side"], row["price"], row["size"], row["signed_size"]) == exp
        for row, exp in zip(first, expected)
    )
    spread_ticks = None
    if first and q is not None and first[0].get("bid") is not None and first[0].get("ask") is not None:
        spread_ticks = (first[0]["ask"] - first[0]["bid"]) / q
    return {
        "available": available,
        "path": path,
        "reason": reason,
        "instrument_id": 42004177,
        "q": q,
        "rows": [
            {
                "source_file": row['source_file'], "source_row": row['source_row'],
                "instrument_id": row['instrument_id'],
                "t": row["event_ns"],
                "side": row["side"],
                "price": str(row["price"]) if row["price"] is not None else None,
                "size": row["size"],
                "bid": str(row["bid"]) if row.get("bid") is not None else None,
                "ask": str(row["ask"]) if row.get("ask") is not None else None,
            }
            for row in first
        ],
        "signed": [row["signed_size"] for row in first],
        "buy_volume": buy,
        "sell_volume": sell,
        "unknown_volume": unknown,
        "total": buy + sell + unknown,
        "delta": buy - sell if unknown == 0 else None,
        "first_spread_ticks": str(spread_ticks) if spread_ticks is not None else None,
        "tie_batch_size": sum(int(row["size"] or 0) for row in tie),
        "tie_count": len(tie),
        "tie_order": "unknown_order" if len(tie) > 1 else "unique_timestamp",
        "price_is_not_rescaled": bool(first and first[0]["price"] == Decimal("28565")),
        "matches_printed_table": matches and buy == 7 and sell == 4 and unknown == 0 and (buy + sell) == 11 and (buy - sell) == 3 and q == Decimal("0.25") and spread_ticks == 2 and len(tie) == 3,
    }


def c03_raw_audit(data_root: Path | str = DATA_ROOT_DEFAULT) -> dict[str, Any]:
    """Optionally audit the acquired raw C03 fixture at an explicit root."""

    root = Path(data_root)
    path = root / MBP1_RELATIVE / "2026-08.parquet"
    q = instrument_tick(root, 42004177, "nq")
    if not path.is_file():
        return {"available": False, "path": str(path), "reason": "HOLE:data_coverage", "matches_printed_table": False}
    if q is None:
        return {"available": False, "path": str(path), "reason": "HOLE:instrument_tick_size", "matches_printed_table": False}
    try:
        rows = []
        for source_row, row in enumerate(iter_source_rows(path)):
            if _row_value(row, "instrument_id", "instrument") != 42004177:
                continue
            if not is_trade_action(_row_value(row, "action")):
                continue
            if _text(_row_value(row, "side")) not in {"A", "B"}:
                continue
            rows.append({**row, '_source_row': source_row})
            if len(rows) == 8:
                break
        return _c03_result(rows, path=str(path), q=q, available=True)
    except Exception as exc:
        return {"available": False, "path": str(path), "reason": f"HOLE:raw_read:{type(exc).__name__}", "matches_printed_table": False}


def c03_f1(data_root: Path | str | None = None, *, raw: bool = False) -> dict[str, Any]:
    """Return the printed C03-F1 fixture without touching production data.

    ``raw=True`` is an explicit opt-in to :func:`c03_raw_audit`; ordinary core
    fixture execution remains fully synthetic even when a production-looking
    data root is passed by the runner.
    """

    if raw:
        return c03_raw_audit(data_root or DATA_ROOT_DEFAULT)
    rows = [
        {
            "t": t,
            "action": "T",
            "side": side,
            "price": Decimal(price),
            "size": size,
            "bid_px": Decimal(bid),
            "ask_px": Decimal(ask),
            "instrument_id": 42004177,
        }
        for t, side, price, size, bid, ask in _C03_SYNTHETIC_ROWS
    ]
    return _c03_result(rows, path=None, q=Decimal("0.25"), available=True)
