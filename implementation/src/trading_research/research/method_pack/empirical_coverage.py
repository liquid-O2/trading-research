"""Outcome-blind acquired coverage inventory and frozen evaluation splits.

This module is the transport boundary for the empirical extension.  It reads
Parquet footers and the timestamp/instrument columns needed to identify full
RTH sessions; it never reads prices, sizes, sides, outcomes, or selector
flags while choosing the sample.  A split is therefore selected from market
coverage and chronology before any historical result is inspected.

The implementation deliberately keeps three things separate:

* canonical file ownership and immutable file identities;
* full weekday/RTH session selection from native 1-minute OHLCV; and
* optional tape/profile availability, which may be partial or unknown.

The public helpers are intentionally usable by the phase-1 runner without
requiring a large in-memory event archive.  Tape windows contain file
identities and half-open bounds only.  The existing adapters and native
resolver remain the authority for decoding and admitting rows later.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Iterator, Mapping, Sequence
from zoneinfo import ZoneInfo

from . import adapters
from .native_resolution import NativeResolver


SCHEMA = "phase1-empirical-coverage-v1"
VERSION = "1.0.0"
ET = ZoneInfo("America/New_York")
UTC = timezone.utc
NS = 1_000_000_000
MS_NS = 1_000_000
MINUTE_NS = 60 * NS
DAY_NS = 86_400 * NS

DEFAULT_DATA_ROOT = Path("/workspace/data")
DEFAULT_WORKSPACE_ROOT = Path("/workspace")
# A complete prior calendar month can begin more than 35 days before the
# first eligible session of the following month.  Keep enough calendar room
# for that reference while retaining the exact requested bounds in each row.
DEFAULT_LOOKBACK_DAYS = 62
# The acquired continuous NQ/ES OHLCV archive starts in 2010.  Callers may
# narrow this explicitly, but the default cohort must not silently discard
# the earliest native years.
DEFAULT_STUDY_START = date(2010, 1, 1)


class CoverageError(ValueError):
    """Invalid, stale, or non-reproducible coverage evidence."""


class CoverageValidationError(CoverageError):
    """Raised by :func:`assert_valid_frozen_split` for a failed gate."""


@dataclass(frozen=True)
class DatasetSpec:
    """A native dataset expected by one method-pack observation route."""

    root: str
    key: str
    dataset_id: str
    relative_path: str
    timestamp_field: str | None
    timestamp_unit: str | None
    bar_duration_ns: int | None
    required_fields: tuple[str, ...]
    role: str = "market"


def _spec(root: str, key: str, dataset_id: str, relative_path: str,
          unit: str | None, duration: int | None, fields: Sequence[str],
          role: str = "market", timestamp_field: str | None = "t") -> DatasetSpec:
    return DatasetSpec(root, key, dataset_id, relative_path, timestamp_field,
                       unit, duration, tuple(fields), role)


_OHLCV = ("t", "o", "h", "l", "c", "v", "instrument_id")
_TRADE = ("t", "price", "size", "side", "instrument_id", "flags")
_MBP1 = adapters.MBP1_REQUIRED
_DEFINITION = ("instrument_id", "raw_symbol", "min_price_increment")


# MNQ is intentionally present as an expected method-pack root.  The actual
# acquired archive contains no quantpad MNQ directory; inventory reports that
# fact as a data hole instead of silently substituting NQ or ES.
ROOT_SPECS: dict[str, dict[str, DatasetSpec]] = {}
for _root in ("NQ", "MNQ", "ES"):
    _lower = _root.lower()
    ROOT_SPECS[_root] = {
        "ohlcv_1m": _spec(
            _root, "ohlcv_1m", f"quantpad/cme__{_lower}-continuous-futures__ohlcv-1m",
            f"quantpad/cme__{_lower}-continuous-futures__ohlcv-1m", "ms",
            60 * NS, _OHLCV),
        "ohlcv_1s": _spec(
            _root, "ohlcv_1s", f"quantpad/cme__{_lower}-continuous-futures__ohlcv-1s",
            f"quantpad/cme__{_lower}-continuous-futures__ohlcv-1s", "ms",
            NS, _OHLCV),
        "trades": _spec(
            _root, "trades", f"quantpad/cme__{_lower}-continuous-futures__trades",
            f"quantpad/cme__{_lower}-continuous-futures__trades", "ns",
            None, _TRADE),
        "mbp1": _spec(
            _root, "mbp1", f"quantpad/cme__{_lower}-continuous-futures__mbp-1",
            f"quantpad/cme__{_lower}-continuous-futures__mbp-1", "ns",
            None, _MBP1),
        "definition": _spec(
            _root, "definition", "derived/continuous-futures__instrument-and-roll-maps",
            f"derived/continuous-futures__instrument-and-roll-maps/{_lower}-instruments.parquet",
            "ns", None, _DEFINITION, role="identity",
            timestamp_field="first_definition_ns"),
    }


DATASET_KEYS = tuple(ROOT_SPECS["NQ"])
ROOTS = tuple(ROOT_SPECS)
_DATE_RE = re.compile(r"(?<!\d)(20\d{2}-\d{2}-\d{2})(?!\d)")
_PARTITION_RE = re.compile(r"^(?P<year>\d{4})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2}))?)?\.")


def _require_pyarrow():
    try:
        import pyarrow as pa  # noqa: F401
        import pyarrow.parquet as pq  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise CoverageError("acquired Parquet coverage requires pyarrow") from exc
    import pyarrow.parquet as pq
    return pq


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, default=_json_default).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _epoch_ns(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CoverageError("timestamp requires an explicit timezone")
    utc = value.astimezone(UTC)
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    delta = utc - epoch
    return delta.days * DAY_NS + delta.seconds * NS + delta.microseconds * 1_000


def _ns_to_datetime(value: int) -> datetime:
    seconds, nanos = divmod(int(value), NS)
    return datetime.fromtimestamp(seconds, tz=UTC).replace(microsecond=nanos // 1_000)


def _value_ns(value: Any, unit: str | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return _epoch_ns(value)
    if unit is None:
        return None
    return adapters.timestamp_ns(value, unit)


def _rth_bounds(day: date, start: time = time(9, 30),
                end: time = time(16, 0)) -> tuple[int, int]:
    return (_epoch_ns(datetime.combine(day, start, tzinfo=ET)),
            _epoch_ns(datetime.combine(day, end, tzinfo=ET)))


def _lookback_bounds(day: date, days: int) -> tuple[int, int]:
    if days < 0:
        raise CoverageError("lookback days cannot be negative")
    return (_epoch_ns(datetime.combine(day - timedelta(days=days), time.min, tzinfo=ET)),
            _epoch_ns(datetime.combine(day + timedelta(days=1), time.min, tzinfo=ET)))


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise CoverageError(f"source path escapes data root: {path}") from exc


def _load_canonical_rows(data_root: Path) -> tuple[Path | None, list[dict[str, Any]], str]:
    """Read the canonical file manifest without reading market payloads."""

    parquet_path = data_root / "manifests" / "files.parquet"
    if parquet_path.is_file():
        pq = _require_pyarrow()
        try:
            rows = pq.read_table(parquet_path).to_pylist()
        except Exception as exc:
            raise CoverageError(f"cannot read canonical file manifest {parquet_path}") from exc
        return parquet_path, [dict(row) for row in rows], "files.parquet"
    csv_path = data_root / "manifests" / "files.csv"
    if csv_path.is_file():
        try:
            with csv_path.open(newline="") as handle:
                return csv_path, [dict(row) for row in csv.DictReader(handle)], "files.csv"
        except (OSError, csv.Error) as exc:
            raise CoverageError(f"cannot read canonical file manifest {csv_path}") from exc
    return None, [], "absent"


def _canonical_index(rows: Iterable[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for original in rows:
        row = dict(original)
        path = str(row.get("archive_path") or "").replace("\\", "/")
        if path:
            index.setdefault(path, []).append(row)
    return index


def _schema_fields(parquet: Any) -> list[dict[str, str]]:
    return [{"name": field.name, "type": str(field.type)}
            for field in parquet.schema_arrow]


def _partition_key(path: Path) -> str | None:
    match = _PARTITION_RE.match(path.name)
    return None if match is None else match.group(0)[:-1]


def _footer_bounds(parquet: Any, spec: DatasetSpec) -> tuple[int | None, int | None, int]:
    names = parquet.schema_arrow.names
    if spec.timestamp_field is None or spec.timestamp_field not in names:
        return None, None, 0
    index = names.index(spec.timestamp_field)
    minima: list[int] = []
    maxima: list[int] = []
    missing = 0
    for group_index in range(parquet.num_row_groups):
        statistics = parquet.metadata.row_group(group_index).column(index).statistics
        if statistics is None or not statistics.has_min_max:
            missing += 1
            continue
        low = _value_ns(getattr(statistics, "min_raw", statistics.min), spec.timestamp_unit)
        high = _value_ns(getattr(statistics, "max_raw", statistics.max), spec.timestamp_unit)
        if low is not None and high is not None:
            minima.append(low)
            maxima.append(high)
    return min(minima, default=None), max(maxima, default=None), missing


def _manifest_ownership(data_root: Path, spec: DatasetSpec, path: Path,
                        canonical: Mapping[str, list[dict[str, Any]]],
                        canonical_present: bool,
                        mbp1_spans: Mapping[str, Sequence[Mapping[str, Any]]] | None) -> tuple[str, str]:
    relative = _relative_path(data_root, path)
    rows = canonical.get(relative, [])
    if spec.key == "mbp1" and spec.root == "NQ" and mbp1_spans is not None:
        owned = any(Path(span.get("path", "")).resolve() == path.resolve()
                    and span.get("status", "owned") not in {"hole", "invalid"}
                    for span in mbp1_spans.get(relative, ()))
        if owned:
            return "owned", "adapters.ownership_manifest"
        return "unowned", "adapters.ownership_manifest"
    if len(rows) == 1:
        declared = rows[0].get("bytes")
        if declared not in (None, ""):
            try:
                if int(declared) != path.stat().st_size:
                    return "stale", "canonical_manifest_bytes"
            except (TypeError, ValueError):
                return "stale", "canonical_manifest_bytes_unparseable"
        return "owned", "canonical_manifest"
    if len(rows) > 1:
        return "conflict", "canonical_manifest_duplicate"
    if not canonical_present:
        # Disposable test roots and portable snapshots may have no catalog;
        # ownership is explicit as a filesystem fallback and remains visible
        # in the report.  Production /workspace/data uses files.parquet.
        return "filesystem_fallback", "no_canonical_manifest"
    return "unowned", "absent_from_canonical_manifest"


def _file_record(data_root: Path, spec: DatasetSpec, path: Path,
                 canonical: Mapping[str, list[dict[str, Any]]],
                 canonical_present: bool,
                 mbp1_spans: Mapping[str, Sequence[Mapping[str, Any]]] | None,
                 *, include_hash: bool = False) -> dict[str, Any]:
    pq = _require_pyarrow()
    try:
        parquet = pq.ParquetFile(path)
    except Exception as exc:
        raise CoverageError(f"cannot inspect Parquet metadata {path}") from exc
    names = parquet.schema_arrow.names
    first_ns, last_ns, missing_stats = _footer_bounds(parquet, spec)
    canonical_rows = canonical.get(_relative_path(data_root, path), [])
    ownership, ownership_basis = _manifest_ownership(
        data_root, spec, path, canonical, canonical_present, mbp1_spans)
    missing_fields = [field for field in spec.required_fields if field not in names]
    instrument_ids: list[str] = []
    if spec.role == "identity" and "instrument_id" in names:
        # The definition table is tiny and its instrument identity is part of
        # the admissibility proof.  No prices, sizes, sides, or outcomes are
        # read while building this inventory.
        try:
            instrument_ids = sorted({str(value) for value in
                                     pq.read_table(path, columns=["instrument_id"])
                                     .column("instrument_id").to_pylist()
                                     if value is not None})
        except Exception as exc:
            raise CoverageError(f"cannot inspect definition identities {path}") from exc
    result: dict[str, Any] = {
        "path": _relative_path(data_root, path),
        "absolute_path": str(path.resolve()),
        "dataset_id": spec.dataset_id,
        "dataset_key": spec.key,
        "root": spec.root,
        "partition_key": _partition_key(path),
        "bytes": path.stat().st_size,
        "rows": parquet.metadata.num_rows,
        "row_groups": parquet.num_row_groups,
        "schema": _schema_fields(parquet),
        "schema_names": names,
        "required_fields": list(spec.required_fields),
        "missing_fields": missing_fields,
        "instrument_ids": instrument_ids,
        "timestamp_field": spec.timestamp_field,
        "timestamp_unit": spec.timestamp_unit,
        "bar_duration_ns": spec.bar_duration_ns,
        "observed_min_ns": first_ns,
        "observed_max_ns": last_ns,
        "observed_min_utc": None if first_ns is None else _ns_to_datetime(first_ns).isoformat().replace("+00:00", "Z"),
        "observed_max_utc": None if last_ns is None else _ns_to_datetime(last_ns).isoformat().replace("+00:00", "Z"),
        "row_groups_missing_timestamp_stats": missing_stats,
        "canonical_owner": ownership,
        "ownership_basis": ownership_basis,
        "canonical_rows": len(canonical_rows),
        "valid_metadata": bool(names) and not missing_fields and first_ns is not None and last_ns is not None,
        "source_path": canonical_rows[0].get("source_path") if len(canonical_rows) == 1 else None,
    }
    years = set()
    for stamp in (first_ns, last_ns):
        if stamp is not None:
            years.add(str(_ns_to_datetime(stamp).year))
    result["observed_years"] = sorted(years)
    if include_hash:
        result["sha256"] = sha256_file(path)
        result["hash_basis"] = "full_file_sha256"
    else:
        result["sha256"] = None
        result["hash_basis"] = "not_computed_during_metadata_inventory"
    return result


def _owned_mbp1_index(data_root: Path) -> dict[str, list[Mapping[str, Any]]]:
    """Resolve NQ MBP-1's monthly/weekly ownership through the accepted adapter."""

    result: dict[str, list[Mapping[str, Any]]] = {}
    try:
        owned = adapters.ownership_manifest(data_root).get("owned_spans", [])
    except (OSError, ValueError, RuntimeError):
        return result
    for span in owned:
        path = Path(str(span.get("path", ""))).resolve()
        try:
            relative = _relative_path(data_root, path)
        except CoverageError:
            continue
        result.setdefault(relative, []).append(dict(span))
    return result


def _spec_files(data_root: Path, spec: DatasetSpec) -> list[Path]:
    location = data_root / spec.relative_path
    if spec.role == "identity":
        return [location] if location.is_file() else []
    if not location.is_dir():
        return []
    return sorted(path for path in location.iterdir()
                  if path.is_file() and path.suffix.lower() == ".parquet")


def inventory_native(data_root: Path | str = DEFAULT_DATA_ROOT,
                     *, roots: Sequence[str] = ROOTS,
                     include_hashes: bool = False) -> dict[str, Any]:
    """Inventory actual NQ/MNQ/ES native files from metadata only.

    ``include_hashes`` hashes every discovered file and is intentionally opt-in
    because an MBP-1 inventory can span many gigabytes.  Frozen partitions
    always hash each file marked as an evaluation input.
    """

    root = Path(data_root).resolve()
    if not root.is_dir():
        raise CoverageError(f"data root does not exist: {root}")
    manifest_path, manifest_rows, manifest_format = _load_canonical_rows(root)
    canonical = _canonical_index(manifest_rows)
    canonical_present = manifest_path is not None
    manifest_info = {
        "path": None if manifest_path is None else _relative_path(root, manifest_path),
        "format": manifest_format,
        "rows": len(manifest_rows),
        "sha256": None if manifest_path is None else sha256_file(manifest_path),
        "ownership_policy": "canonical manifest row with matching bytes; NQ MBP-1 via adapters.ownership_manifest",
    }
    selected_roots = []
    for value in roots:
        key = str(value).upper()
        if key not in ROOT_SPECS:
            raise CoverageError(f"unsupported native root: {value}")
        selected_roots.append(key)
    mbp1_spans = _owned_mbp1_index(root)
    root_records: dict[str, Any] = {}
    all_files: list[dict[str, Any]] = []
    for root_name in selected_roots:
        dataset_records: dict[str, Any] = {}
        for key, spec in ROOT_SPECS[root_name].items():
            records = []
            for path in _spec_files(root, spec):
                record = _file_record(root, spec, path, canonical,
                                      canonical_present, mbp1_spans,
                                      include_hash=include_hashes)
                records.append(record)
                all_files.append(record)
            observed_years = sorted({year for record in records for year in record["observed_years"]})
            dataset_records[key] = {
                "dataset_id": spec.dataset_id,
                "relative_path": spec.relative_path,
                "role": spec.role,
                "timestamp_field": spec.timestamp_field,
                "timestamp_unit": spec.timestamp_unit,
                "bar_duration_ns": spec.bar_duration_ns,
                "required_fields": list(spec.required_fields),
                "file_count": len(records),
                "rows": sum(int(record["rows"]) for record in records),
                "bytes": sum(int(record["bytes"]) for record in records),
                "row_groups": sum(int(record["row_groups"]) for record in records),
                "observed_years": observed_years,
                "files": records,
                "status": "available" if records else "missing",
                "ownership_counts": {
                    owner: sum(record["canonical_owner"] == owner for record in records)
                    for owner in sorted({record["canonical_owner"] for record in records})
                },
                "schemas": sorted({
                    tuple((field["name"], field["type"]) for field in record["schema"])
                    for record in records
                }),
            }
            # JSON cannot encode tuple schemas, and the compact report needs
            # one deterministic representation per dataset.
            dataset_records[key]["schemas"] = [
                [{"name": name, "type": typ} for name, typ in schema]
                for schema in dataset_records[key]["schemas"]
            ]
        available = [key for key, record in dataset_records.items()
                     if record["status"] == "available"]
        root_records[root_name] = {
            "root": root_name,
            "status": "available" if available else "missing",
            "datasets": dataset_records,
            "available_dataset_keys": available,
            "missing_dataset_keys": [key for key in DATASET_KEYS if key not in available],
        }
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "data_root": str(root),
        "canonical_manifest": manifest_info,
        "roots": root_records,
        "files": all_files,
        "file_count": len(all_files),
        "outcome_blind": True,
        "outcome_fields_examined": False,
        "inventory_basis": "Parquet footer metadata plus timestamp/instrument columns only for session-date discovery",
        "limitations": [
            "Footer extrema and row counts do not prove event continuity.",
            "A file's observed bounds do not establish full market coverage.",
            "MNQ is absent from the acquired QuantPad root and is not substituted with NQ or ES.",
        ],
    }


def _date_from_value(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.astimezone(ET).date() if value.tzinfo else value.date()
    if isinstance(value, date):
        return value
    if value is None:
        return None
    match = _DATE_RE.search(str(value))
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def _collect_keyed_dates(value: Any, *, key_name: str = "") -> set[date]:
    result: set[date] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in {"date", "trade_date", "session_date", "calendar_date"}:
                parsed = _date_from_value(child)
                if parsed is not None:
                    result.add(parsed)
            result.update(_collect_keyed_dates(child, key_name=key_text))
    elif isinstance(value, list):
        for child in value:
            result.update(_collect_keyed_dates(child, key_name=key_name))
    return result


def discover_prior_inspected_dates(workspace_root: Path | str = DEFAULT_WORKSPACE_ROOT) -> dict[str, Any]:
    """Return dates exposed by prior auditable diagnostics.

    The ledger is intentionally conservative and incomplete: files from old
    workers or interactive sessions cannot prove non-exposure.  Every frozen
    row therefore retains ``prior_exposure_status='unknown'`` even when this
    function identifies dates to exclude.
    """

    workspace = Path(workspace_root).resolve()
    base = workspace / "implementation" / "reports" / "phase1-live"
    dates: set[date] = set()
    sources: dict[str, int] = {}

    # These are retained, reviewable date-bearing ledgers.  We avoid parsing
    # broad report text so outcome labels cannot influence the sample.
    json_paths = [
        base / "chart-audit" / "source_date_plot_results.json",
        base / "chart-audit" / "fresh_tape_selected.json",
        base / "chart-audit" / "fresh_assembly_selected_tape.json",
        base / "coverage-audit" / "coverage-audit.json",
    ]
    for path in json_paths:
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        found = _collect_keyed_dates(payload)
        if found:
            dates.update(found)
            sources[str(path)] = len(found)

    plot_dir = base / "chart-audit" / "plots"
    if plot_dir.is_dir():
        found: set[date] = set()
        for path in plot_dir.iterdir():
            found.update(date.fromisoformat(match.group(1))
                         for match in _DATE_RE.finditer(path.name))
        if found:
            dates.update(found)
            sources[str(plot_dir)] = len(found)

    # Retained selected-output tables are read through their date column only.
    # The ``sessions_L`` table is a full coverage census used to establish the
    # archive's dimensions; treating every row in that census as a previously
    # inspected evaluation date would erase the retrospective cohort.  The F
    # tables and the explicit value-delta output are selected audit products.
    tables = base / "_tables"
    if tables.is_dir():
        pq = _require_pyarrow()
        selected_tables = sorted(tables.glob("*_F.parquet"))
        selected_tables += sorted(tables.glob("value_delta_*.parquet"))
        for path in selected_tables:
            try:
                names = pq.ParquetFile(path).schema_arrow.names
                if "date" not in names:
                    continue
                values = pq.read_table(path, columns=["date"]).column("date").to_pylist()
            except Exception:
                continue
            found = {parsed for parsed in (_date_from_value(value) for value in values) if parsed is not None}
            if found:
                dates.update(found)
                sources[str(path)] = len(found)

    return {
        "dates": sorted(day.isoformat() for day in dates),
        "date_count": len(dates),
        "sources": sources,
        "status": "partial_ledger_exposure_unknown",
        "untouched_claim_supported": False,
        "note": "Only dates detectable in retained manifests/tables were excluded; prior interactive or unrecorded inspection remains unknown.",
    }


def calibration_dates(catalog_path: Path | str | None = None) -> dict[str, Any]:
    """Collect source/calibration dates from the retained method-pack cases."""

    path = Path(catalog_path) if catalog_path else Path(__file__).with_name("source_cases_v2.json")
    dates: set[date] = set()
    sources: dict[str, int] = {}
    if not path.is_file():
        return {"dates": [], "date_count": 0, "sources": {}, "status": "catalog_missing"}
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise CoverageError(f"cannot read source case catalog {path}") from exc
    for case in payload.get("cases", []):
        setting = case.get("date", {})
        parsed = _date_from_value(setting.get("value")) if isinstance(setting, Mapping) else None
        if parsed is not None:
            dates.add(parsed)
        for window in case.get("native_control_windows", []):
            if not isinstance(window, Mapping):
                continue
            parsed = _date_from_value(window.get("start_et"))
            if parsed is not None:
                dates.add(parsed)
    sources[str(path)] = len(dates)
    return {
        "dates": sorted(day.isoformat() for day in dates),
        "date_count": len(dates),
        "sources": sources,
        "status": "retained_source_case_and_native_control_dates",
    }


def _session_batches(path: Path, spec: DatasetSpec,
                     start_date: date, end_date: date | None) -> Iterator[tuple[Any, Any]]:
    pq = _require_pyarrow()
    parquet = pq.ParquetFile(path)
    names = parquet.schema_arrow.names
    if "t" not in names or "instrument_id" not in names:
        return
    for batch in parquet.iter_batches(columns=["t", "instrument_id"], batch_size=131_072):
        times = batch.column("t").to_pylist()
        instruments = batch.column("instrument_id").to_pylist()
        for raw, instrument in zip(times, instruments, strict=True):
            if instrument is None:
                continue
            at = _value_ns(raw, spec.timestamp_unit)
            if at is None:
                continue
            local = _ns_to_datetime(at).astimezone(ET)
            if local.weekday() >= 5:
                continue
            if local.date() < start_date or (end_date is not None and local.date() > end_date):
                continue
            if local.second != 0 or local.microsecond != 0:
                # A minute bucket with an offset timestamp is not an exact
                # native minute start and cannot prove the 390-start gate.
                continue
            yield local, instrument


def full_rth_sessions(data_root: Path | str, root: str = "NQ", *,
                      start_date: date = DEFAULT_STUDY_START,
                      end_date: date | None = None,
                      inventory: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Find complete 09:30–16:00 ET weekday sessions from native OHLCV.

    Only ``t`` and ``instrument_id`` are read.  A session is full exactly when
    its 390 distinct RTH minute starts are present for one native contract.
    """

    root_name = str(root).upper()
    if root_name not in ROOT_SPECS:
        raise CoverageError(f"unsupported native root: {root}")
    inv = inventory or inventory_native(data_root, roots=[root_name])
    dataset = inv["roots"][root_name]["datasets"]["ohlcv_1m"]
    if dataset["status"] == "missing":
        return []
    stats: dict[tuple[date, str], dict[str, Any]] = {}
    first_rth_instrument: dict[date, str] = {}
    spec = ROOT_SPECS[root_name]["ohlcv_1m"]
    data_root_path = Path(data_root).resolve()
    for record in dataset["files"]:
        if record["canonical_owner"] not in {"owned", "filesystem_fallback"}:
            continue
        path = data_root_path / record["path"]
        for local, instrument in _session_batches(path, spec, start_date, end_date):
            minute = local.hour * 60 + local.minute
            if not 570 <= minute < 960:
                continue
            if minute == 570 and local.date() not in first_rth_instrument:
                # The source row order at the first cash-open minute is the
                # contract choice.  No volume or price ranking is used.
                first_rth_instrument[local.date()] = str(instrument)
            key = (local.date(), str(instrument))
            row = stats.setdefault(key, {"count": 0, "minutes": set(), "files": set()})
            row["count"] += 1
            row["minutes"].add(minute)
            row["files"].add(record["path"])
    complete: list[dict[str, Any]] = []
    expected = set(range(570, 960))
    for (day, instrument), row in sorted(stats.items()):
        complete_session = row["count"] == 390 and row["minutes"] == expected
        if not complete_session:
            continue
        start_ns, end_ns = _rth_bounds(day)
        complete.append({
            "date": day.isoformat(),
            "year": day.year,
            "month": day.month,
            "weekday": day.strftime("%A"),
            "instrument_id": instrument,
            "first_rth_instrument_id": first_rth_instrument.get(day),
            "session_start_ns": start_ns,
            "session_end_ns": end_ns,
            "session_start_et": datetime.fromtimestamp(start_ns / NS, tz=UTC).astimezone(ET).isoformat(),
            "session_end_et": datetime.fromtimestamp(end_ns / NS, tz=UTC).astimezone(ET).isoformat(),
            "rth_minute_count": row["count"],
            "rth_minutes_distinct": len(row["minutes"]),
            "ohlcv_files": sorted(row["files"]),
            "eligibility_basis": "native 1m OHLCV t/instrument_id; exact 390 distinct 09:30–16:00 ET starts; contract fixed from first 09:30 row",
        })
    return complete


def _record_overlaps(record: Mapping[str, Any], start_ns: int, end_ns: int) -> bool:
    low, high = record.get("observed_min_ns"), record.get("observed_max_ns")
    if low is None or high is None:
        return False
    finish = int(high) + int(record.get("bar_duration_ns") or 1)
    return int(low) < end_ns and finish > start_ns


def _identity(record: Mapping[str, Any], *, data_root: Path, hash_files: bool,
              hash_cache: dict[str, str]) -> dict[str, Any]:
    path = data_root / str(record["path"])
    result = {
        "path": str(record["path"]),
        "dataset_id": record["dataset_id"],
        "dataset_key": record["dataset_key"],
        "root": record["root"],
        "bytes": record["bytes"],
        "rows": record["rows"],
        "row_groups": record["row_groups"],
        "schema_names": list(record["schema_names"]),
        "timestamp_unit": record["timestamp_unit"],
        "canonical_owner": record["canonical_owner"],
        "ownership_basis": record["ownership_basis"],
        "observed_min_ns": record["observed_min_ns"],
        "observed_max_ns": record["observed_max_ns"],
        "used_for_evaluation": True,
    }
    if hash_files:
        key = str(path.resolve())
        digest = hash_cache.get(key)
        if digest is None:
            digest = sha256_file(path)
            hash_cache[key] = digest
        result["sha256"] = digest
        result["hash_basis"] = "full_file_sha256"
    else:
        result["sha256"] = None
        result["hash_basis"] = "deferred"
    return result


def _dataset_window(key: str, lookback_start_ns: int, session_start_ns: int,
                    session_end_ns: int, *, tape_start_ns: int | None = None) -> tuple[int | None, int | None]:
    if key in {"ohlcv_1m", "ohlcv_1s"}:
        return lookback_start_ns, session_end_ns
    if key in {"trades", "mbp1"}:
        # Tape-required branches may build a previous complete RTH profile
        # before observing the evaluation session.  Use the prior weekday's
        # clock window (weekends are skipped; exchange holidays remain an
        # explicit missing reference for the runner to retain).
        return tape_start_ns or session_start_ns, session_end_ns
    return None, None


def _prior_weekday(day: date) -> date:
    prior = day - timedelta(days=1)
    while prior.weekday() >= 5:
        prior -= timedelta(days=1)
    return prior


def _prior_rth_start_ns(day: date) -> int:
    return _rth_bounds(_prior_weekday(day))[0]


def _owned_record(record: Mapping[str, Any]) -> bool:
    return record.get("canonical_owner") in {"owned", "filesystem_fallback"}


def _window_records(dataset_records: Mapping[str, Any], key: str,
                    start_ns: int | None, end_ns: int | None,
                    instrument_id: Any) -> list[Mapping[str, Any]]:
    """Return owned metadata records intersecting one frozen input window.

    This is deliberately a metadata operation.  It does not imply complete
    event coverage: event-level adapters still have to prove every requested
    member interval when the runner loads a partition.
    """

    records = dataset_records.get(key, {}).get("files", [])
    selected: list[Mapping[str, Any]] = []
    for record in records:
        if not _owned_record(record):
            continue
        if key == "definition":
            identities = record.get("instrument_ids")
            if identities is not None and identities and str(instrument_id) not in {
                    str(value) for value in identities}:
                continue
            if identities == [] and "instrument_ids" in record:
                # A readable identity file with no instrument rows cannot
                # satisfy a contract definition prerequisite.
                continue
            selected.append(record)
            continue
        if start_ns is None or end_ns is None or _record_overlaps(record, start_ns, end_ns):
            selected.append(record)
    return selected


def _session_dataset_availability(
    root_name: str,
    session: Mapping[str, Any],
    dataset_records: Mapping[str, Any],
    lookback_start_ns: int,
    required: Sequence[str],
    required_groups: Sequence[Sequence[str]],
) -> tuple[dict[str, tuple[int | None, int | None, list[Mapping[str, Any]]]],
           dict[str, str], list[dict[str, Any]], bool]:
    """Resolve file-level prerequisites for one session without payload reads."""

    windows: dict[str, tuple[int | None, int | None, list[Mapping[str, Any]]]] = {}
    statuses: dict[str, str] = {}
    session_start_ns = int(session["session_start_ns"])
    session_end_ns = int(session["session_end_ns"])
    instrument_id = session["instrument_id"]
    tape_start_ns = _prior_rth_start_ns(date.fromisoformat(str(session["date"])))
    for key in DATASET_KEYS:
        start_ns, end_ns = _dataset_window(key, lookback_start_ns,
                                            session_start_ns, session_end_ns,
                                            tape_start_ns=tape_start_ns)
        files = _window_records(dataset_records, key, start_ns, end_ns, instrument_id)
        windows[key] = (start_ns, end_ns, files)
        if key in required:
            statuses[key] = "available" if files else "missing"
    group_statuses: list[dict[str, Any]] = []
    for index, group in enumerate(required_groups):
        available_keys = [key for key in group if windows[key][2]]
        group_statuses.append({
            "group_id": f"any_of_{index + 1}",
            "keys": list(group),
            "available_keys": available_keys,
            "status": "available" if available_keys else "missing",
        })
    required_ok = all(statuses.get(key) == "available" for key in required)
    required_ok = required_ok and all(item["status"] == "available"
                                     for item in group_statuses)
    return windows, statuses, group_statuses, required_ok


def _source_exclusion_sets(data_root: Path, workspace_root: Path | None,
                           source_dates: Iterable[date] | None,
                           prior_dates: Iterable[date] | None) -> tuple[set[date], set[date], dict[str, Any]]:
    source = set(source_dates or ())
    source_evidence: dict[str, Any]
    if source_dates is None:
        source_evidence = calibration_dates()
        source = {date.fromisoformat(value) for value in source_evidence["dates"]}
    else:
        source_evidence = {"dates": sorted(day.isoformat() for day in source),
                           "date_count": len(source), "status": "caller_supplied"}
    if prior_dates is None:
        prior_evidence = discover_prior_inspected_dates(workspace_root or data_root.parent)
        prior = {date.fromisoformat(value) for value in prior_evidence["dates"]}
    else:
        prior = set(prior_dates)
        prior_evidence = {"dates": sorted(day.isoformat() for day in prior),
                          "date_count": len(prior), "status": "caller_supplied",
                          "untouched_claim_supported": False}
    return source, prior, {"source_calibration": source_evidence, "prior_inspection": prior_evidence}


def build_frozen_split(
    data_root: Path | str = DEFAULT_DATA_ROOT,
    *,
    roots: Sequence[str] = ("NQ", "ES", "MNQ"),
    start_date: date = DEFAULT_STUDY_START,
    end_date: date | None = None,
    lookback_calendar_days: int = DEFAULT_LOOKBACK_DAYS,
    required_dataset_keys: Sequence[str] = ("ohlcv_1m", "definition"),
    required_dataset_groups: Sequence[Sequence[str]] = (),
    selection_frequency: str = "monthly",
    required_data_policy: str = "annotate",
    source_dates: Iterable[date] | None = None,
    prior_inspected_dates: Iterable[date] | None = None,
    workspace_root: Path | str | None = None,
    include_hashes: bool = True,
    inventory: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a chronological, outcome-blind monthly or annual evaluation manifest.

    For each root and selected calendar period, the selected date is the first
    full weekday 09:30–16:00 ET OHLCV session remaining after known source and
    prior-inspection exclusions.  Required file prerequisites can either be
    annotated as data holes or used to filter the first eligible session.  The
    selection does not inspect prices, trades, labels, candidates, or later
    sequence outcomes.
    """

    if lookback_calendar_days < 0 or lookback_calendar_days > DEFAULT_LOOKBACK_DAYS:
        raise CoverageError("lookback must be between 0 and 62 calendar days")
    frequency_aliases = {"month": "monthly", "monthly": "monthly",
                         "year": "annual", "annual": "annual"}
    try:
        frequency = frequency_aliases[str(selection_frequency).lower()]
    except KeyError as exc:
        raise CoverageError("selection_frequency must be monthly or annual") from exc
    policy = str(required_data_policy).lower()
    if policy not in {"annotate", "filter"}:
        raise CoverageError("required_data_policy must be annotate or filter")
    data_root_path = Path(data_root).resolve()
    if not data_root_path.is_dir():
        raise CoverageError(f"data root does not exist: {data_root_path}")
    root_names = tuple(str(value).upper() for value in roots)
    if len(set(root_names)) != len(root_names) or any(value not in ROOT_SPECS for value in root_names):
        raise CoverageError("roots must be a unique subset of NQ, MNQ, and ES")
    required = tuple(dict.fromkeys(str(value) for value in required_dataset_keys))
    unknown_keys = set(required) - set(DATASET_KEYS)
    if unknown_keys:
        raise CoverageError(f"unsupported required dataset keys: {sorted(unknown_keys)}")
    normalized_groups: list[tuple[str, ...]] = []
    for raw_group in required_dataset_groups:
        if isinstance(raw_group, str):
            raise CoverageError("required dataset groups must be sequences of keys")
        group = tuple(dict.fromkeys(str(value) for value in raw_group))
        if not group:
            raise CoverageError("required dataset groups cannot be empty")
        unknown_group_keys = set(group) - set(DATASET_KEYS)
        if unknown_group_keys:
            raise CoverageError(f"unsupported required dataset group keys: {sorted(unknown_group_keys)}")
        normalized_groups.append(group)
    workspace = Path(workspace_root).resolve() if workspace_root else data_root_path.parent
    inv = inventory or inventory_native(data_root_path, roots=root_names, include_hashes=False)
    source_set, prior_set, exposure = _source_exclusion_sets(
        data_root_path, workspace, source_dates, prior_inspected_dates)
    excluded = source_set | prior_set
    hash_cache: dict[str, str] = {}
    partitions: list[dict[str, Any]] = []
    root_summary: dict[str, Any] = {}
    exclusion_rows: list[dict[str, Any]] = []

    for root_name in root_names:
        sessions = full_rth_sessions(data_root_path, root_name,
                                     start_date=start_date, end_date=end_date,
                                     inventory=inv)
        by_month: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for session in sessions:
            by_month.setdefault((session["year"], session["month"]), []).append(session)
        chosen: list[dict[str, Any]] = []
        period_sessions: dict[tuple[int, ...], list[dict[str, Any]]] = {}
        for month_key, session_rows in by_month.items():
            period_key = month_key if frequency == "monthly" else (month_key[0],)
            period_sessions.setdefault(period_key, []).extend(session_rows)
        dataset_records = inv["roots"][root_name]["datasets"]
        for period_key in sorted(period_sessions):
            eligible = period_sessions[period_key]
            # A date with two complete native contracts is resolved by the
            # smallest immutable instrument ID, keeping chronology primary.
            by_day: dict[str, list[dict[str, Any]]] = {}
            for session in eligible:
                by_day.setdefault(session["date"], []).append(session)
            selected = None
            for day_text in sorted(by_day):
                day = date.fromisoformat(day_text)
                if day in excluded:
                    reasons = []
                    if day in source_set:
                        reasons.append("source_or_calibration_date")
                    if day in prior_set:
                        reasons.append("prior_inspection_date_detected")
                    exclusion_rows.append({"root": root_name, "date": day_text,
                                           "reasons": reasons,
                                           "selection_stage": f"full_session_{frequency}_candidate"})
                    continue
                day_sessions = sorted(by_day[day_text],
                                      key=lambda row: str(row["instrument_id"]))
                first_open_ids = {str(candidate["first_rth_instrument_id"])
                                  for candidate in day_sessions
                                  if candidate.get("first_rth_instrument_id") is not None}
                if first_open_ids:
                    anchored = [candidate for candidate in day_sessions
                                if str(candidate["instrument_id"]) in first_open_ids]
                    if anchored:
                        day_sessions = anchored
                    else:
                        exclusion_rows.append({
                            "root": root_name,
                            "date": day_text,
                            "reasons": ["first_open_contract_not_full_session"],
                            "selection_stage": f"full_session_{frequency}_candidate",
                        })
                        continue
                if policy == "filter":
                    lookback_start_ns, _ = _lookback_bounds(day, lookback_calendar_days)
                    day_sessions = [candidate for candidate in day_sessions
                                    if _session_dataset_availability(
                                        root_name, candidate, dataset_records,
                                        lookback_start_ns, required,
                                        normalized_groups)[3]]
                    if not day_sessions:
                        exclusion_rows.append({
                            "root": root_name,
                            "date": day_text,
                            "reasons": ["required_data_unavailable"],
                            "selection_stage": f"required_metadata_{frequency}_candidate",
                        })
                        continue
                selected = day_sessions[0]
                break
            if selected is not None:
                chosen.append(selected)
        root_summary[root_name] = {
            "full_rth_session_count": len(sessions),
            "eligible_period_count": len(chosen),
            "selection_frequency": frequency,
            "selected_dates": [row["date"] for row in chosen],
            "source_or_calibration_exclusions": sum(
                row["date"] in {day.isoformat() for day in source_set} for row in exclusion_rows
                if row["root"] == root_name),
            "prior_inspection_exclusions": sum(
                row["date"] in {day.isoformat() for day in prior_set} for row in exclusion_rows
                if row["root"] == root_name),
            "missing_ohlcv": not bool(sessions),
        }
        for session in chosen:
            day = date.fromisoformat(session["date"])
            lookback_start_ns, lookback_end_ns = _lookback_bounds(day, lookback_calendar_days)
            windows, required_status, required_groups_status, required_ok = _session_dataset_availability(
                root_name, session, dataset_records, lookback_start_ns,
                required, normalized_groups)
            dataset_windows: dict[str, Any] = {}
            input_identities: list[dict[str, Any]] = []
            for key, spec in ROOT_SPECS[root_name].items():
                start_ns, end_ns, files = windows[key]
                is_required = key in required or any(key in group for group in normalized_groups)
                available = bool(files)
                identities = []
                for record in files:
                    if is_required:
                        identities.append(_identity(record, data_root=data_root_path,
                                                    hash_files=include_hashes,
                                                    hash_cache=hash_cache))
                dataset_windows[key] = {
                    "dataset_id": spec.dataset_id,
                    "required": is_required,
                    "status": "available" if available else "missing_or_unowned",
                    "window_start_ns": start_ns,
                    "window_end_ns": end_ns,
                    "window_start_et": None if start_ns is None else _ns_to_datetime(start_ns).astimezone(ET).isoformat(),
                    "window_end_et": None if end_ns is None else _ns_to_datetime(end_ns).astimezone(ET).isoformat(),
                    "files": identities,
                    "candidate_file_count": len(files),
                    "hashes_included": bool(identities and include_hashes),
                    "selection_note": "definition identity file" if key == "definition" else
                    "OHLCV lookback" if key in {"ohlcv_1m", "ohlcv_1s"} else
                    "prior-weekday RTH plus evaluation-session tape window",
                }
                input_identities.extend(identities)
            partition_id = f"{root_name}-{day.isoformat()}-{session['instrument_id']}"
            partitions.append({
                "partition_id": partition_id,
                "root": root_name,
                "instrument_id": session["instrument_id"],
                "date": session["date"],
                "year": session["year"],
                "month": session["month"],
                "weekday": session["weekday"],
                "session": {
                    "timezone": "America/New_York",
                    "start_et": session["session_start_et"],
                    "end_et": session["session_end_et"],
                    "start_ns": session["session_start_ns"],
                    "end_ns": session["session_end_ns"],
                    "duration_minutes": 390,
                },
                "lookback": {
                    "calendar_days": lookback_calendar_days,
                    "start_et": _ns_to_datetime(lookback_start_ns).astimezone(ET).isoformat(),
                    "end_et": _ns_to_datetime(lookback_end_ns).astimezone(ET).isoformat(),
                    "purpose": "prior monthly/reference profile inputs; not an outcome window",
                },
                "required_dataset_keys": list(required),
                "required_dataset_status": required_status,
                "required_dataset_groups": required_groups_status,
                "status": "eligible" if required_ok else "data_hole",
                "full_session_basis": session["eligibility_basis"],
                "dataset_windows": dataset_windows,
                "input_identities": sorted(input_identities,
                                             key=lambda row: (row["dataset_key"], row["path"])),
                "exposure": {
                    "source_or_calibration_excluded": False,
                    "prior_inspection_date_detected": False,
                    "prior_exposure_status": "unknown",
                    "untouched_claim": False,
                },
                "outcome_blind": True,
                "outcome_fields_examined": False,
            })

    partitions.sort(key=lambda row: (row["date"], row["root"], str(row["instrument_id"])))
    for index, row in enumerate(partitions):
        row["chronological_index"] = index
    identity_hash = sha256_bytes(_canonical_json([
        {"partition_id": row["partition_id"],
         "inputs": row["input_identities"]} for row in partitions
    ]))
    core = {
        "schema": SCHEMA,
        "version": VERSION,
        "data_root": str(data_root_path),
        "roots": list(root_names),
        "study_start_date": start_date.isoformat(),
        "study_end_date": None if end_date is None else end_date.isoformat(),
        "selection_rule": f"first eligible full weekday 09:30–16:00 ET native 1m OHLCV session per {frequency} after known exclusions",
        "selection_frequency": frequency,
        "required_dataset_keys": list(required),
        "required_dataset_groups": [list(group) for group in normalized_groups],
        "required_data_policy": policy,
        "lookback_calendar_days": lookback_calendar_days,
        "outcome_blind": True,
        "outcome_fields_examined": False,
        "exposure_policy": "exclude detectable source/calibration and prior-inspection dates; retain unknown exposure for every included row",
        "source_calibration_exposure": exposure["source_calibration"],
        "prior_inspection_exposure": exposure["prior_inspection"],
        "root_summary": root_summary,
        "excluded_candidates": sorted(exclusion_rows, key=lambda row: (row["date"], row["root"])),
        "partitions": partitions,
        "input_identity_hash": identity_hash,
        "inventory_manifest_sha256": inv["canonical_manifest"].get("sha256"),
    }
    manifest_hash = sha256_bytes(_canonical_json(core))
    return {**core,
            "manifest_id": f"{SCHEMA}:{manifest_hash[:16]}",
            "manifest_sha256": manifest_hash,
            "built_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "inventory_summary": {
                "file_count": inv["file_count"],
                "roots": {name: {
                    key: {field: dataset[field] for field in ("status", "file_count", "rows", "observed_years")}
                    for key, dataset in inv["roots"][name]["datasets"].items()
                } for name in root_names},
            },
    }


_FORBIDDEN_OUTCOME_KEYS = frozenset({
    "outcomes", "outcome", "pnl", "return", "returns", "profit", "loss",
    "win", "target", "label", "verdict", "candidate_count", "selected_signal",
})


def _find_forbidden_keys(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in _FORBIDDEN_OUTCOME_KEYS:
                found.append(f"{path}.{key_text}" if path else key_text)
            found.extend(_find_forbidden_keys(child, f"{path}.{key_text}" if path else key_text))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_find_forbidden_keys(child, f"{path}[{index}]"))
    return found


def _manifest_core(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items()
            if key not in {"manifest_id", "manifest_sha256", "built_at_utc", "inventory_summary"}}


def validate_frozen_split(manifest: Mapping[str, Any], *, data_root: Path | str | None = None,
                         verify_hashes: bool = True) -> dict[str, Any]:
    """Validate reproducibility, chronology, ownership, identity, and leakage controls."""

    errors: list[str] = []
    warnings: list[str] = []
    if manifest.get("schema") != SCHEMA:
        errors.append("unsupported coverage manifest schema")
    if manifest.get("version") != VERSION:
        errors.append("unsupported coverage manifest version")
    if manifest.get("outcome_blind") is not True or manifest.get("outcome_fields_examined") is not False:
        errors.append("manifest does not prove outcome-blind construction")
    if manifest.get("prior_inspection_exposure", {}).get("untouched_claim_supported") is True:
        errors.append("prior inspection ledger cannot support an untouched claim")
    frequency = str(manifest.get("selection_frequency", "monthly")).lower()
    if frequency not in {"monthly", "annual"}:
        errors.append("unsupported selection frequency")
    policy = str(manifest.get("required_data_policy", "annotate")).lower()
    if policy not in {"annotate", "filter"}:
        errors.append("unsupported required data policy")
    required_keys = manifest.get("required_dataset_keys", [])
    if not isinstance(required_keys, list) or any(key not in DATASET_KEYS for key in required_keys):
        errors.append("manifest has unsupported required dataset keys")
        required_keys = []
    groups = manifest.get("required_dataset_groups", [])
    if not isinstance(groups, list):
        errors.append("required_dataset_groups must be a list")
        groups = []
    normalized_groups: list[tuple[str, ...]] = []
    for group in groups:
        if not isinstance(group, list) or not group or any(key not in DATASET_KEYS for key in group):
            errors.append("manifest has invalid required dataset group")
            continue
        normalized_groups.append(tuple(str(key) for key in group))
    partitions = manifest.get("partitions")
    if not isinstance(partitions, list):
        errors.append("partitions must be a list")
        partitions = []
    ids: set[str] = set()
    root_dates: dict[str, list[str]] = {}
    root_periods: dict[str, list[tuple[int, ...]]] = {}
    source_dates = set(manifest.get("source_calibration_exposure", {}).get("dates", []))
    prior_dates = set(manifest.get("prior_inspection_exposure", {}).get("dates", []))
    for row in partitions:
        if not isinstance(row, Mapping):
            errors.append("partition is not an object")
            continue
        partition_id = str(row.get("partition_id", ""))
        if not partition_id or partition_id in ids:
            errors.append(f"duplicate or missing partition_id: {partition_id!r}")
        ids.add(partition_id)
        day_text = str(row.get("date", ""))
        try:
            parsed_day = date.fromisoformat(day_text)
        except ValueError:
            errors.append(f"invalid partition date: {day_text}")
            continue
        root = str(row.get("root", ""))
        if root not in ROOT_SPECS:
            errors.append(f"partition {partition_id} has unsupported root")
        root_dates.setdefault(root, []).append(day_text)
        period = (parsed_day.year, parsed_day.month) if frequency == "monthly" else (parsed_day.year,)
        root_periods.setdefault(root, []).append(period)
        if day_text in source_dates or day_text in prior_dates:
            errors.append(f"excluded exposure date entered manifest: {root}/{day_text}")
        exposure = row.get("exposure", {})
        if exposure.get("prior_exposure_status") != "unknown" or exposure.get("untouched_claim") is not False:
            errors.append(f"partition {partition_id} does not preserve unknown prior exposure")
        session = row.get("session", {})
        expected_start, expected_end = _rth_bounds(parsed_day)
        if session.get("start_ns") != expected_start or session.get("end_ns") != expected_end:
            errors.append(f"partition {partition_id} has noncanonical ET session bounds")
        if session.get("duration_minutes") != 390:
            errors.append(f"partition {partition_id} has non-390-minute session")
        try:
            lookback_days = int(row.get("lookback", {}).get("calendar_days", -1))
        except (AttributeError, TypeError, ValueError):
            lookback_days = -1
            errors.append(f"partition {partition_id} has invalid lookback")
        if lookback_days < 0 or lookback_days > DEFAULT_LOOKBACK_DAYS:
            errors.append(f"partition {partition_id} has invalid 0–62-day lookback")
        if not row.get("outcome_blind") or row.get("outcome_fields_examined") is not False:
            errors.append(f"partition {partition_id} outcome-blind flags invalid")
        required = row.get("required_dataset_keys", [])
        if not isinstance(required, list):
            errors.append(f"partition {partition_id} required dataset keys must be a list")
            required = []
        if required != list(required_keys):
            errors.append(f"partition {partition_id} required dataset keys differ from manifest")
        statuses = row.get("required_dataset_status", {})
        if not isinstance(statuses, Mapping):
            errors.append(f"partition {partition_id} required dataset status must be an object")
            statuses = {}
        for key in required:
            if statuses.get(key) not in {"available", "missing"}:
                errors.append(f"partition {partition_id} lacks explicit status for {key}")
        row_groups = row.get("required_dataset_groups", [])
        if not isinstance(row_groups, list):
            errors.append(f"partition {partition_id} required dataset groups must be a list")
            row_groups = []
        if len(row_groups) != len(normalized_groups):
            errors.append(f"partition {partition_id} required dataset group count differs")
        for index, group in enumerate(row_groups):
            if not isinstance(group, Mapping):
                errors.append(f"partition {partition_id} has invalid required dataset group")
                continue
            expected_group = list(normalized_groups[index]) if index < len(normalized_groups) else []
            if group.get("keys") != expected_group or group.get("status") not in {"available", "missing"}:
                errors.append(f"partition {partition_id} required dataset group is invalid")
        identities = row.get("input_identities", [])
        if not isinstance(identities, list):
            errors.append(f"partition {partition_id} input identities must be a list")
            identities = []
        for identity in identities:
            if not isinstance(identity, Mapping):
                errors.append(f"partition {partition_id} identity is not an object")
                continue
            if identity.get("used_for_evaluation") is not True:
                errors.append(f"partition {partition_id} identity is not marked used")
            if identity.get("canonical_owner") not in {"owned", "filesystem_fallback"}:
                errors.append(f"partition {partition_id} uses unowned input {identity.get('path')}")
            if verify_hashes:
                digest = identity.get("sha256")
                if not isinstance(digest, str) or len(digest) != 64 or identity.get("hash_basis") != "full_file_sha256":
                    errors.append(f"partition {partition_id} lacks full input hash: {identity.get('path')}")
    for root, periods in root_periods.items():
        if periods != sorted(periods):
            errors.append(f"periods are not chronological for {root}")
        if len(periods) != len(set(periods)):
            errors.append(f"duplicate evaluation period for {root}")
    for root, dates in root_dates.items():
        if dates != sorted(dates):
            errors.append(f"partitions are not chronological for {root}")
        if len(dates) != len(set(dates)):
            errors.append(f"duplicate evaluation date for {root}")
    forbidden = _find_forbidden_keys(manifest)
    if forbidden:
        errors.append("outcome-bearing keys present: " + ", ".join(sorted(set(forbidden))[:10]))
    expected_hash = manifest.get("manifest_sha256")
    actual_hash = sha256_bytes(_canonical_json(_manifest_core(manifest)))
    if expected_hash != actual_hash:
        errors.append("manifest_sha256 does not match canonical manifest content")
    expected_identity_hash = sha256_bytes(_canonical_json([
        {"partition_id": row.get("partition_id"), "inputs": row.get("input_identities", [])}
        for row in partitions if isinstance(row, Mapping)
    ]))
    if manifest.get("input_identity_hash") != expected_identity_hash:
        errors.append("input_identity_hash does not match evaluation identities")
    physical_root = Path(data_root).resolve() if data_root is not None else None
    if physical_root is not None:
        for row in partitions:
            if not isinstance(row, Mapping):
                continue
            partition_id = str(row.get("partition_id", ""))
            for identity in row.get("input_identities", []):
                raw_path = str(identity.get("path", ""))
                path = Path(raw_path)
                if path.is_absolute():
                    errors.append(f"partition {partition_id} identity path is absolute: {raw_path}")
                    continue
                try:
                    resolved = (physical_root / path).resolve()
                    resolved.relative_to(physical_root)
                except ValueError:
                    errors.append(f"partition {partition_id} identity path escapes data root: {raw_path}")
                    continue
                if not resolved.is_file():
                    errors.append(f"missing frozen input: {resolved}")
                    continue
                expected_bytes = identity.get("bytes")
                if expected_bytes not in (None, ""):
                    try:
                        if resolved.stat().st_size != int(expected_bytes):
                            errors.append(f"frozen input byte size changed: {resolved}")
                    except (TypeError, ValueError):
                        errors.append(f"invalid frozen input byte size: {raw_path}")
                if verify_hashes:
                    digest = identity.get("sha256")
                    if isinstance(digest, str) and len(digest) == 64:
                        if sha256_file(resolved) != digest:
                            errors.append(f"frozen input changed: {resolved}")
    return {
        "schema": "phase1-empirical-coverage-validation-v1",
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "manifest_sha256": actual_hash,
        "partition_count": len(partitions),
        "root_counts": {root: len(values) for root, values in sorted(root_dates.items())},
        "outcome_blind": not forbidden and manifest.get("outcome_fields_examined") is False,
        "full_hash_count": sum(
            1 for row in partitions if isinstance(row, Mapping)
            for identity in row.get("input_identities", [])
            if identity.get("hash_basis") == "full_file_sha256"),
    }


def assert_valid_frozen_split(manifest: Mapping[str, Any], *, data_root: Path | str | None = None,
                              verify_hashes: bool = True) -> dict[str, Any]:
    result = validate_frozen_split(manifest, data_root=data_root, verify_hashes=verify_hashes)
    if not result["valid"]:
        raise CoverageValidationError("; ".join(result["errors"]))
    return result


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.pending")
    temporary.write_bytes(payload)
    temporary.replace(path)


def write_json(path: Path | str, document: Mapping[str, Any]) -> str:
    payload = json.dumps(document, indent=2, sort_keys=True, default=_json_default).encode("utf-8")
    _atomic_write(Path(path), payload)
    return sha256_bytes(payload)


def _inventory_markdown(inventory: Mapping[str, Any], split: Mapping[str, Any],
                       validation: Mapping[str, Any]) -> str:
    lines = [
        "# Empirical native coverage and frozen evaluation split",
        "",
        "This report was selected from native Parquet metadata and timestamp/instrument columns. "
        "Outcome fields were not examined while choosing dates.",
        "",
        f"- schema: `{inventory.get('schema')}`",
        f"- data root: `{inventory.get('data_root')}`",
        f"- canonical manifest: `{inventory.get('canonical_manifest', {}).get('path')}` "
        f"sha256=`{inventory.get('canonical_manifest', {}).get('sha256')}`",
        f"- frozen manifest: `{split.get('manifest_id')}`",
        f"- selection frequency: `{split.get('selection_frequency')}`; required-data policy: `{split.get('required_data_policy')}`",
        f"- validation: `{'PASS' if validation.get('valid') else 'FAIL'}`",
        "",
        "## Native dimensions",
        "",
        "root | dataset | status | files | rows | years | schema",
        "--- | --- | --- | ---: | ---: | --- | ---",
    ]
    for root, root_record in inventory.get("roots", {}).items():
        for key, dataset in root_record.get("datasets", {}).items():
            schema = "; ".join(
                ",".join(field["name"] for field in schema_row)
                for schema_row in dataset.get("schemas", [])
            ) or "—"
            lines.append(f"{root} | {key} | {dataset.get('status')} | {dataset.get('file_count', 0)} | "
                         f"{dataset.get('rows', 0)} | {','.join(dataset.get('observed_years', [])) or '—'} | {schema}")
    lines.extend(["", "## Frozen selection", "",
                  "root | date | instrument | status | required data | lookback", 
                  "--- | --- | --- | --- | --- | ---"])
    for row in split.get("partitions", []):
        lines.append(f"{row['root']} | {row['date']} | {row['instrument_id']} | {row['status']} | "
                     f"{json.dumps(row['required_dataset_status'], sort_keys=True)} | "
                     f"{row['lookback']['calendar_days']} calendar days")
    lines.extend(["", "## Exposure and limitations", "",
                  f"- selected partitions: `{len(split.get('partitions', []))}`",
                  f"- excluded full-session candidates: `{len(split.get('excluded_candidates', []))}`",
                  f"- input identity hash: `{split.get('input_identity_hash')}`",
                  "- previous exposure remains unknown; no untouched-sample claim is made.",
                  "- MBP-1 and standalone trades are represented as prior-weekday-RTH plus evaluation-session windows; they are not loaded during date selection.",
                  "- MNQ is absent from the acquired archive and is retained as an explicit missing root.",
                  "",
                  "## Reproduction",
                  "",
                  "```bash",
                  "PYTHONPATH=implementation/src python -m trading_research.research.method_pack.empirical_coverage freeze \\",
                  "  --data-root /workspace/data \\",
                  "  --output-dir /workspace/implementation/reports/phase1-live/empirical/coverage",
                  "```",
                  ""])
    return "\n".join(lines)


def write_coverage_artifacts(
    data_root: Path | str = DEFAULT_DATA_ROOT,
    output_dir: Path | str = Path("/workspace/implementation/reports/phase1-live/empirical/coverage"),
    *, roots: Sequence[str] = ("NQ",),
    required_dataset_keys: Sequence[str] = ("ohlcv_1m", "definition"),
    required_dataset_groups: Sequence[Sequence[str]] = (),
    selection_frequency: str = "monthly",
    required_data_policy: str = "annotate",
    include_hashes: bool = True,
) -> dict[str, Any]:
    """Write the reviewable inventory, frozen split, and validation artifacts."""

    root = Path(data_root).resolve()
    out = Path(output_dir).resolve()
    if out == root or out.is_relative_to(root):
        raise CoverageError("coverage artifacts must be outside the read-only data root")
    inv = inventory_native(root, roots=roots, include_hashes=False)
    split = build_frozen_split(root, roots=roots,
                               required_dataset_keys=required_dataset_keys,
                               required_dataset_groups=required_dataset_groups,
                               selection_frequency=selection_frequency,
                               required_data_policy=required_data_policy,
                               include_hashes=include_hashes, inventory=inv)
    validation = validate_frozen_split(split, data_root=root, verify_hashes=include_hashes)
    if not validation["valid"]:
        raise CoverageValidationError("; ".join(validation["errors"]))
    artifacts = {}
    artifacts["inventory.json"] = {"path": str(out / "inventory.json"),
                                    "sha256": write_json(out / "inventory.json", inv)}
    artifacts["evaluation-split.json"] = {"path": str(out / "evaluation-split.json"),
                                           "sha256": write_json(out / "evaluation-split.json", split)}
    artifacts["validation.json"] = {"path": str(out / "validation.json"),
                                     "sha256": write_json(out / "validation.json", validation)}
    report_text = _inventory_markdown(inv, split, validation)
    _atomic_write(out / "README.md", report_text.encode("utf-8"))
    artifacts["README.md"] = {"path": str(out / "README.md"),
                              "sha256": sha256_bytes(report_text.encode("utf-8"))}
    result = {
        "schema": "phase1-empirical-coverage-report-v1",
        "status": "passed",
        "inventory": inv,
        "split": split,
        "validation": validation,
        "artifacts": artifacts,
    }
    write_json(out / "report.json", result)
    return result


# Names used by the runner/review scripts.  Keep the descriptive primary APIs
# above while retaining short aliases for callers that predate this module.
build_coverage_inventory = inventory_native
build_evaluation_manifest = build_frozen_split
validate_split = validate_frozen_split


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inventory", "freeze", "validate"))
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--output-dir", type=Path,
                        default=Path("/workspace/implementation/reports/phase1-live/empirical/coverage"))
    parser.add_argument("--root", dest="roots", action="append",
                        help="native root (repeat for NQ, MNQ, and/or ES)")
    parser.add_argument("--required-dataset", dest="required_datasets", action="append",
                        help="required dataset key for freeze (repeat as needed)")
    parser.add_argument("--frequency", choices=("monthly", "annual"), default="monthly",
                        help="evaluation partition frequency for freeze")
    parser.add_argument("--required-data-policy", choices=("annotate", "filter"),
                        default="annotate", help="annotate or filter missing required files")
    parser.add_argument("--split", type=Path, help="split JSON for validate")
    parser.add_argument("--no-hashes", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "inventory":
            value = inventory_native(args.data_root, roots=tuple(args.roots or ROOTS),
                                     include_hashes=not args.no_hashes)
            write_json(args.output_dir / "inventory.json", value)
            print(json.dumps({"status": "passed", "file_count": value["file_count"],
                              "output": str(args.output_dir / "inventory.json")}, sort_keys=True))
            return 0
        if args.command == "freeze":
            result = write_coverage_artifacts(args.data_root, args.output_dir,
                                              roots=tuple(args.roots or ("NQ",)),
                                              required_dataset_keys=tuple(
                                                  args.required_datasets or ("ohlcv_1m", "definition")),
                                              selection_frequency=args.frequency,
                                              required_data_policy=args.required_data_policy,
                                              include_hashes=not args.no_hashes)
            print(json.dumps({"status": result["status"],
                              "manifest_id": result["split"]["manifest_id"],
                              "partitions": len(result["split"]["partitions"]),
                              "output_dir": str(args.output_dir)}, sort_keys=True))
            return 0
        if args.split is None:
            parser.error("validate requires --split")
        split = json.loads(args.split.read_text())
        result = validate_frozen_split(split, data_root=args.data_root,
                                       verify_hashes=not args.no_hashes)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["valid"] else 1
    except (CoverageError, OSError, ValueError, TypeError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - exercised by CLI smoke tests
    raise SystemExit(_cli())


__all__ = [
    "SCHEMA", "VERSION", "DatasetSpec", "ROOT_SPECS", "CoverageError",
    "CoverageValidationError", "inventory_native", "build_coverage_inventory",
    "full_rth_sessions", "calibration_dates", "discover_prior_inspected_dates",
    "build_frozen_split", "build_evaluation_manifest", "validate_frozen_split",
    "validate_split", "assert_valid_frozen_split", "write_coverage_artifacts",
    "sha256_file",
]
