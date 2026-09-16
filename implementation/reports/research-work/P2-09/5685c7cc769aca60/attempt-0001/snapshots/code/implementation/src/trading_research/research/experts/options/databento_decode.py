"""Official Databento DBN decoder for owned NQ/ES option files.

Writes columnar parquet beside the Phase 2 early reports. Never writes under
/workspace/data. A root is never labelled unsupported while this decoder exists.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
import json
import time
import traceback

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.research.contracts.identity import file_digest
from trading_research.research.experts.options.instruments import (
    DATABENTO,
    FUTURES_OPTION_ROOTS,
    RIGHT_CALL,
    root_spec,
)

PRICE_SCALE = 1_000_000_000.0
UNDEF_I64 = 9223372036854775807
STAT_OPEN_INTEREST = 9
INSTALL_COMMAND = "uv pip install databento --python /workspace/implementation/.venv/bin/python"
DECODE_VERSION = "phase2-futures-option-dbn-v1"
SCHEMAS = ("definition", "statistics", "ohlcv-1m", "trades")
OPTION_CLASSES = {b"C", b"P", "C", "P"}


def decoder_identity() -> dict[str, Any]:
    try:
        import databento as db
    except ImportError as exc:
        return {
            "package": "databento",
            "version": None,
            "import_ok": False,
            "error": str(exc),
            "command": INSTALL_COMMAND,
        }
    return {
        "package": "databento",
        "version": str(db.__version__),
        "import_ok": True,
        "command": INSTALL_COMMAND,
    }


def decoded_root_dir() -> Path:
    return Path(__file__).resolve().parents[5] / "reports/research-work/phase2-early/decoded"


def decoded_path(root: str, kind: str) -> Path:
    return decoded_root_dir() / root / f"{kind}.parquet"


def decode_log_path() -> Path:
    return decoded_root_dir() / "DECODE_LOG.json"


def _as_str(value: object) -> str:
    if isinstance(value, bytes):
        return value.split(b"\x00", 1)[0].decode("ascii", "replace")
    if value is None:
        return ""
    return str(value)


def _as_bytes_key(value: object) -> bytes:
    if isinstance(value, bytes):
        return value.split(b"\x00", 1)[0]
    return str(value).encode("ascii", "replace")


def _pretty_px(raw: int | np.integer) -> float:
    value = int(raw)
    if value == UNDEF_I64 or value <= 0:
        return float("nan")
    return value / PRICE_SCALE


def inventory(root: str) -> dict[str, Any]:
    spec = root_spec(root)
    prefix = spec.databento_prefix
    found = []
    for schema in SCHEMAS:
        folder = DATABENTO / f"{prefix}__{schema}"
        files = sorted(folder.glob("*.dbn.zst")) if folder.is_dir() else []
        meta = folder / "metadata.json"
        found.append(
            {
                "schema": schema,
                "path": str(folder),
                "exists": folder.is_dir(),
                "metadata": str(meta) if meta.is_file() else None,
                "metadata_sha256": file_digest(meta) if meta.is_file() else None,
                "file_count": len(files),
                "files": [str(path) for path in files],
            }
        )
    ident = decoder_identity()
    return {
        "root": root,
        "decoder": ident,
        "owned": found,
        "disposition": "decoded" if ident["import_ok"] else "decoder_import_failed",
    }


def _open_store(path: Path):
    import databento as db

    return db.DBNStore.from_file(path)


def _decode_definition_array(arr: np.ndarray) -> dict[str, np.ndarray]:
    klass = np.array([_as_bytes_key(x) for x in arr["instrument_class"]], dtype="S1")
    keep = (klass == b"C") | (klass == b"P")
    if "security_type" in arr.dtype.names:
        stype = np.array([_as_bytes_key(x) for x in arr["security_type"]], dtype="S7")
        keep = keep & (stype == b"OOF")
    sub = arr[keep]
    if sub.size == 0:
        return _empty_definition()
    right = np.where(np.array([_as_bytes_key(x) for x in sub["instrument_class"]]) == b"C", RIGHT_CALL, -RIGHT_CALL).astype(np.int8)
    cfi = np.array([_as_str(x) for x in sub["cfi"]], dtype=object)
    american = np.array([(c[2] == "A") if len(c) > 2 else False for c in cfi], dtype=np.bool_)
    strike = np.array([_pretty_px(x) for x in sub["strike_price"]], dtype=np.float64)
    strike_millis = np.rint(strike * 1000.0).astype(np.int64)
    strike_millis = np.where(np.isfinite(strike), strike_millis, -1)
    multiplier = np.array([_pretty_px(x) for x in sub["unit_of_measure_qty"]], dtype=np.float64)
    raw_symbol = np.array([_as_str(x) for x in sub["raw_symbol"]], dtype=object)
    underlying = np.array([_as_str(x) for x in sub["underlying"]], dtype=object)
    action = np.array([_as_str(x) for x in sub["security_update_action"]], dtype=object)
    return {
        "instrument_id": np.asarray(sub["instrument_id"], dtype=np.int64),
        "ts_event": np.asarray(sub["ts_event"], dtype=np.int64),
        "raw_symbol": raw_symbol,
        "underlying": underlying,
        "underlying_id": np.asarray(sub["underlying_id"], dtype=np.int64),
        "right": right,
        "strike_millis": strike_millis,
        "expiry_ns": np.asarray(sub["expiration"], dtype=np.int64),
        "activation_ns": np.asarray(sub["activation"], dtype=np.int64),
        "cfi": cfi,
        "american": american,
        "multiplier": multiplier,
        "security_update_action": action,
    }


def _empty_definition() -> dict[str, np.ndarray]:
    return {
        "instrument_id": np.zeros(0, dtype=np.int64),
        "ts_event": np.zeros(0, dtype=np.int64),
        "raw_symbol": np.zeros(0, dtype=object),
        "underlying": np.zeros(0, dtype=object),
        "underlying_id": np.zeros(0, dtype=np.int64),
        "right": np.zeros(0, dtype=np.int8),
        "strike_millis": np.zeros(0, dtype=np.int64),
        "expiry_ns": np.zeros(0, dtype=np.int64),
        "activation_ns": np.zeros(0, dtype=np.int64),
        "cfi": np.zeros(0, dtype=object),
        "american": np.zeros(0, dtype=np.bool_),
        "multiplier": np.zeros(0, dtype=np.float64),
        "security_update_action": np.zeros(0, dtype=object),
    }


def _decode_oi_array(arr: np.ndarray) -> dict[str, np.ndarray]:
    mask = arr["stat_type"] == STAT_OPEN_INTEREST
    sub = arr[mask]
    qty = np.asarray(sub["quantity"], dtype=np.int64)
    qty = np.where(qty == UNDEF_I64, -1, qty)
    return {
        "instrument_id": np.asarray(sub["instrument_id"], dtype=np.int64),
        "ts_event": np.asarray(sub["ts_event"], dtype=np.int64),
        "ts_recv": np.asarray(sub["ts_recv"], dtype=np.int64),
        "open_interest": qty,
    }


def _decode_ohlcv_array(arr: np.ndarray) -> dict[str, np.ndarray]:
    close = np.array([_pretty_px(x) for x in arr["close"]], dtype=np.float64)
    return {
        "instrument_id": np.asarray(arr["instrument_id"], dtype=np.int64),
        "ts_event": np.asarray(arr["ts_event"], dtype=np.int64),
        "open": np.array([_pretty_px(x) for x in arr["open"]], dtype=np.float64),
        "high": np.array([_pretty_px(x) for x in arr["high"]], dtype=np.float64),
        "low": np.array([_pretty_px(x) for x in arr["low"]], dtype=np.float64),
        "close": close,
        "volume": np.asarray(arr["volume"], dtype=np.int64),
    }


def _decode_trades_array(arr: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "instrument_id": np.asarray(arr["instrument_id"], dtype=np.int64),
        "ts_event": np.asarray(arr["ts_event"], dtype=np.int64),
        "ts_recv": np.asarray(arr["ts_recv"], dtype=np.int64),
        "price": np.array([_pretty_px(x) for x in arr["price"]], dtype=np.float64),
        "size": np.asarray(arr["size"], dtype=np.int64),
    }


def _table_from_columns(columns: dict[str, np.ndarray]) -> pa.Table:
    arrays = {}
    for name, values in columns.items():
        if values.dtype == object:
            arrays[name] = pa.array(values.tolist(), type=pa.string())
        elif values.dtype == np.bool_:
            arrays[name] = pa.array(values, type=pa.bool_())
        elif values.dtype == np.int8:
            arrays[name] = pa.array(values, type=pa.int8())
        elif values.dtype == np.int64:
            arrays[name] = pa.array(values, type=pa.int64())
        else:
            arrays[name] = pa.array(values, type=pa.float64())
    return pa.table(arrays)


def _concat(parts: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    if not parts:
        return {}
    out = {}
    for key in parts[0]:
        out[key] = np.concatenate([part[key] for part in parts])
    return out


def decode_file(path: Path, schema: str) -> tuple[dict[str, np.ndarray] | None, dict[str, Any]]:
    started = time.monotonic()
    record: dict[str, Any] = {
        "path": str(path),
        "schema": schema,
        "ok": False,
        "rows": 0,
        "seconds": None,
        "error": None,
        "sha256": file_digest(path) if path.is_file() else None,
    }
    try:
        store = _open_store(path)
        arr = store.to_ndarray()
        if schema == "definition":
            columns = _decode_definition_array(arr)
        elif schema == "statistics":
            columns = _decode_oi_array(arr)
        elif schema == "ohlcv-1m":
            columns = _decode_ohlcv_array(arr)
        elif schema == "trades":
            columns = _decode_trades_array(arr)
        else:
            raise ValueError(f"unknown schema {schema}")
        n = int(next(iter(columns.values())).size) if columns else 0
        record["ok"] = True
        record["rows"] = n
        record["seconds"] = time.monotonic() - started
        return columns, record
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc(limit=8)
        record["seconds"] = time.monotonic() - started
        return None, record


def decode_root(root: str, *, force: bool = False) -> dict[str, Any]:
    spec = root_spec(root)
    out_dir = decoded_root_dir() / root
    out_dir.mkdir(parents=True, exist_ok=True)
    ident = decoder_identity()
    log = {
        "root": root,
        "decoder": ident,
        "decode_version": DECODE_VERSION,
        "prefix": spec.databento_prefix,
        "files": [],
        "outputs": {},
        "ok": False,
    }
    if not ident["import_ok"]:
        log["error"] = ident.get("error")
        return log
    existing = decode_log_path()
    if existing.is_file() and not force:
        payload = json.loads(existing.read_text())
        prior = (payload.get("roots") or {}).get(root)
        if (
            prior
            and prior.get("ok")
            and prior.get("decoder", {}).get("version") == ident["version"]
            and prior.get("decode_version") == DECODE_VERSION
            and all((out_dir / f"{kind}.parquet").is_file() for kind in ("definitions", "open_interest", "quotes_ohlcv1m", "trades"))
        ):
            return prior
    buckets: dict[str, list[dict[str, np.ndarray]]] = {
        "definition": [],
        "statistics": [],
        "ohlcv-1m": [],
        "trades": [],
    }
    inv = inventory(root)
    for item in inv["owned"]:
        schema = item["schema"]
        if not item["exists"]:
            log["files"].append({"path": item["path"], "schema": schema, "ok": False, "error": "folder_missing", "rows": 0})
            continue
        if item["file_count"] == 0:
            log["files"].append({"path": item["path"], "schema": schema, "ok": False, "error": "no_dbn_zst_files", "rows": 0})
            continue
        for path_text in item["files"]:
            columns, record = decode_file(Path(path_text), schema)
            log["files"].append(record)
            if columns is not None and record["ok"]:
                buckets[schema].append(columns)
    kind_map = {
        "definition": "definitions",
        "statistics": "open_interest",
        "ohlcv-1m": "quotes_ohlcv1m",
        "trades": "trades",
    }
    for schema, kind in kind_map.items():
        parts = buckets[schema]
        path = decoded_path(root, kind)
        if not parts:
            empty = {
                "definition": _empty_definition(),
                "statistics": {"instrument_id": np.zeros(0, np.int64), "ts_event": np.zeros(0, np.int64), "ts_recv": np.zeros(0, np.int64), "open_interest": np.zeros(0, np.int64)},
                "ohlcv-1m": {
                    "instrument_id": np.zeros(0, np.int64),
                    "ts_event": np.zeros(0, np.int64),
                    "open": np.zeros(0, np.float64),
                    "high": np.zeros(0, np.float64),
                    "low": np.zeros(0, np.float64),
                    "close": np.zeros(0, np.float64),
                    "volume": np.zeros(0, np.int64),
                },
                "trades": {
                    "instrument_id": np.zeros(0, np.int64),
                    "ts_event": np.zeros(0, np.int64),
                    "ts_recv": np.zeros(0, np.int64),
                    "price": np.zeros(0, np.float64),
                    "size": np.zeros(0, np.int64),
                },
            }[schema]
            table = _table_from_columns(empty)
        else:
            table = _table_from_columns(_concat(parts))
        pq.write_table(table, path, compression="zstd")
        log["outputs"][kind] = {
            "path": str(path),
            "rows": int(table.num_rows),
            "sha256": file_digest(path),
        }
    failed = [row for row in log["files"] if not row.get("ok")]
    log["ok"] = ident["import_ok"] and not any(
        row.get("error") in {"folder_missing", "decoder_import_failed"} for row in log["files"]
    )
    log["failed_files"] = failed
    log["n_files"] = len(log["files"])
    log["n_failed"] = len(failed)
    _merge_log(root, log)
    return log


def _merge_log(root: str, log: dict[str, Any]) -> None:
    path = decode_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": "research-databento-decode-log-v1", "decoder": decoder_identity(), "roots": {}}
    if path.is_file():
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            payload = {"schema_version": "research-databento-decode-log-v1", "decoder": decoder_identity(), "roots": {}}
    payload.setdefault("roots", {})[root] = log
    payload["decoder"] = decoder_identity()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def ensure_decoded(root: str) -> dict[str, Any]:
    return decode_root(root, force=False)


def decode_all_futures_roots(*, force: bool = False) -> dict[str, Any]:
    logs = {root: decode_root(root, force=force) for root in FUTURES_OPTION_ROOTS}
    return {"decoder": decoder_identity(), "roots": logs}


@lru_cache(maxsize=8)
def _read(root: str, kind: str) -> pa.Table:
    ensure_decoded(root)
    path = decoded_path(root, kind)
    if not path.is_file():
        return pa.table({})
    return pq.read_table(path)


def definitions_table(root: str) -> pa.Table:
    return _read(root, "definitions")


def oi_table(root: str) -> pa.Table:
    return _read(root, "open_interest")


def quotes_table(root: str) -> pa.Table:
    return _read(root, "quotes_ohlcv1m")


def trades_table(root: str) -> pa.Table:
    return _read(root, "trades")


def _utc_day_bounds(day: date) -> tuple[int, int]:
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    from datetime import timedelta

    return int(start.timestamp() * 1_000_000_000), int((end + timedelta(days=1)).timestamp() * 1_000_000_000)


def coverage_by_year(root: str) -> dict[str, Any]:
    ensure_decoded(root)
    defs = definitions_table(root)
    oi = oi_table(root)
    quotes = quotes_table(root)
    years = {str(y): {"definition_rows": 0, "oi_rows": 0, "quote_rows": 0, "oi_days": 0, "quote_days": 0} for y in range(2020, 2027)}

    def year_of(ns_col: pa.Array) -> np.ndarray:
        if ns_col is None or len(ns_col) == 0:
            return np.zeros(0, dtype=np.int32)
        ns = np.asarray(ns_col.to_numpy(), dtype=np.int64)
        return (ns // 1_000_000_000).astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970

    if defs.num_rows:
        for year, count in zip(*np.unique(year_of(defs.column("ts_event")), return_counts=True)):
            key = str(int(year))
            if key in years:
                years[key]["definition_rows"] = int(count)
    if oi.num_rows:
        y = year_of(oi.column("ts_event"))
        days = (np.asarray(oi.column("ts_event").to_numpy(), dtype=np.int64) // 86_400_000_000_000).astype(np.int64)
        for year in years:
            mask = y == int(year)
            years[year]["oi_rows"] = int(np.count_nonzero(mask))
            years[year]["oi_days"] = int(len(np.unique(days[mask]))) if np.any(mask) else 0
    if quotes.num_rows:
        y = year_of(quotes.column("ts_event"))
        days = (np.asarray(quotes.column("ts_event").to_numpy(), dtype=np.int64) // 86_400_000_000_000).astype(np.int64)
        for year in years:
            mask = y == int(year)
            years[year]["quote_rows"] = int(np.count_nonzero(mask))
            years[year]["quote_days"] = int(len(np.unique(days[mask]))) if np.any(mask) else 0
    for year, rec in years.items():
        if rec["definition_rows"] > 0 and rec["oi_rows"] > 0:
            rec["disposition"] = "complete_observed_scope" if rec["quote_rows"] > 0 else "definitions_and_oi_quotes_sparse"
        elif rec["definition_rows"] > 0 or rec["oi_rows"] > 0:
            rec["disposition"] = "partial"
        else:
            rec["disposition"] = "missing"
    return years
