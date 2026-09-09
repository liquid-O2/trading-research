"""Bounded, literal QuantPad one-minute OHLC admission.

This adapter is deliberately narrower than the MBP partition materializer.  It
reads one complete, bounded Parquet source, keeps the original file identity in
the manifest, and emits a nullable canonical table.  A bad source row remains a
row with a quality reason; a source that cannot be located, ordered, or decoded
is rejected before a table is returned.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import hashlib
import math
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from trading_research.data.definitions import futures_definition
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


BAR_MILLISECONDS = 60_000
NANOSECONDS_PER_MILLISECOND = 1_000_000
BAR_NANOSECONDS = BAR_MILLISECONDS * NANOSECONDS_PER_MILLISECOND
BAR_END_PLUS_60S_NANOSECONDS = BAR_NANOSECONDS + 60 * 1_000_000_000
QUARTER_TICK = Decimal("0.25")
DEFINITION_LATENCY_NS = 250_000_000
DEFINITION_LATENCY_SCENARIO = "definition-provider-plus-250ms"
OHLC_FORMAT_VERSION = "quantpad-ohlcv-1m-admission-v1"
DEFINITION_INDEX_VERSION = "quantpad-futures-definition-index-v1"
MAX_OHLC_ROWS = 600_000
DEFAULT_OHLC_FILE_BYTES = 16 * 1024 * 1024
MAX_OHLC_FILE_BYTES = 256 * 1024 * 1024
MAX_DEFINITION_ROWS = 12_000
MAX_DEFINITION_FILE_BYTES = 64 * 1024 * 1024

_OHLC_FIELDS = ("t", "o", "h", "l", "c", "v", "instrument_id")
_DEFINITION_FIELDS = frozenset({
    "t", "ts_recv", "raw_symbol", "instrument_id", "instrument_class",
    "security_update_action", "activation", "expiration",
    "min_price_increment", "contract_multiplier",
})
_OUTPUT_FIELDS = (
    "start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
    "low_ticks", "close_ticks", "volume", "instrument_id", "contract_key",
    "definition_version", "source_row", "valid", "reasons",
)


def _pa():
    """Load the pinned optional Arrow dependency only when a reader is used."""
    try:
        import pyarrow as pa
        import pyarrow.ipc as ipc
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - exercised without data extra
        raise DependencyUnavailable("OHLC admission requires the pinned PyArrow data extra") from exc
    if getattr(pa, "__version__", None) != "25.0.1":
        raise ContractError("OHLC admission requires the pinned PyArrow 25.0.1 provider")
    return pa, ipc, pq


def _validate_bound(value: Any, *, name: str, maximum: int) -> int:
    if type(value) is not int or value <= 0 or value > maximum:
        raise ContractError(f"{name} must be a positive bounded integer <= {maximum}")
    return value


def _safe_source(path: Path, data_root: Path) -> tuple[Path, str]:
    root = Path(data_root).resolve()
    source = Path(path).resolve()
    excluded = Path("/workspace/archive").resolve()
    if not source.is_relative_to(root) or source.is_relative_to(excluded):
        raise ContractError("OHLC source must be inside the declared data root and outside /workspace/archive")
    if source.suffix != ".parquet":
        raise ContractError("OHLC admission requires a completed .parquet source")
    return source, str(source.relative_to(root))


def _stamp(path: Path) -> tuple[int, int, int]:
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ino


def _read_bounded_source(path: Path, maximum_file_bytes: int) -> tuple[bytes, str, tuple[int, int, int]]:
    try:
        before = _stamp(path)
    except OSError as exc:
        raise DependencyUnavailable("complete OHLC source is unavailable at the declared path") from exc
    if before[0] > maximum_file_bytes:
        raise DependencyUnavailable("complete OHLC source exceeds the declared byte bound")
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise IntegrityError("OHLC source could not be read as an immutable complete file") from exc
    if len(payload) != before[0] or len(payload) > maximum_file_bytes:
        raise IntegrityError("OHLC source changed or exceeded its declared byte bound while being read")
    return payload, hashlib.sha256(payload).hexdigest(), before


def _source_unchanged(path: Path, before: tuple[int, int, int], expected_hash: str,
                      maximum_file_bytes: int | None = None) -> None:
    try:
        current = _stamp(path)
    except OSError as exc:
        raise IntegrityError("OHLC source disappeared after the bounded read") from exc
    if current != before:
        raise IntegrityError("OHLC source changed during the bounded read")
    if maximum_file_bytes is not None and before[0] > maximum_file_bytes:
        raise IntegrityError("OHLC source exceeded its declared byte bound after the bounded read")
    try:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise IntegrityError("OHLC source disappeared after the bounded read") from exc
    if actual != expected_hash:
        raise IntegrityError("OHLC source bytes changed during the bounded read")


def _schema_identity(schema: Any) -> str:
    return hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()


def _ipc_identity(table: Any, ipc: Any) -> str:
    sink = None
    try:
        sink = __import__("pyarrow").BufferOutputStream()
        with ipc.new_stream(sink, table.schema) as writer:
            writer.write_table(table)
        return hashlib.sha256(sink.getvalue().to_pybytes()).hexdigest()
    except Exception as exc:
        if isinstance(exc, (ContractError, IntegrityError, DependencyUnavailable)):
            raise
        raise IntegrityError("complete Arrow IPC identity could not be retained") from exc


def _validate_ohlc_schema(schema: Any, pa: Any) -> None:
    if tuple(schema.names) != _OHLC_FIELDS:
        raise ContractError("QuantPad OHLC schema must contain exactly t,o,h,l,c,v,instrument_id in source order")
    expected = {
        "t": pa.int64(),
        "o": pa.float64(),
        "h": pa.float64(),
        "l": pa.float64(),
        "c": pa.float64(),
        "v": pa.float64(),
        "instrument_id": pa.int32(),
    }
    for name in _OHLC_FIELDS:
        if schema.field(name).type != expected[name]:
            raise ContractError(f"OHLC field {name} has an unregistered physical type")


def _validate_definition_schema(schema: Any) -> None:
    missing = sorted(_DEFINITION_FIELDS - set(schema.names))
    if missing:
        raise ContractError(f"definition source omits required fields: {missing}")


def _finite_decimal(value: Any, *, name: str) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool) or type(value) not in (float, int):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    try:
        result = Decimal.from_float(value) if isinstance(value, float) else Decimal(value)
    except (InvalidOperation, ValueError, OverflowError):
        return None
    return result if result.is_finite() else None


def _quarter_ticks(value: Any, *, name: str) -> tuple[int | None, str | None]:
    decimal = _finite_decimal(value, name=name)
    if decimal is None:
        return None, f"nonfinite_{name}"
    scaled = decimal / QUARTER_TICK
    if scaled != scaled.to_integral_value():
        return None, f"off_tick_{name}"
    result = int(scaled)
    if not -(2**63) <= result < 2**63:
        return None, f"out_of_range_{name}"
    return result, None


def _positive_integral_volume(value: Any) -> tuple[int | None, str | None]:
    decimal = _finite_decimal(value, name="volume")
    if decimal is None:
        return None, "nonfinite_volume"
    if decimal != decimal.to_integral_value():
        return None, "nonintegral_volume"
    result = int(decimal)
    if result <= 0:
        return None, "nonpositive_volume"
    if result >= 2**63:
        return None, "out_of_range_volume"
    return result, None


def _instrument_id(value: Any) -> tuple[int | None, str | None]:
    if type(value) is not int or value <= 0:
        return None, "invalid_instrument_id"
    return int(value), None


def _reason_string(reasons: Iterable[str]) -> str:
    return "|".join(dict.fromkeys(str(reason) for reason in reasons if reason))


@dataclass(frozen=True)
class DefinitionRecord:
    """One source definition with the exact lifetime and bitemporal clocks."""

    definition: InstrumentDefinition
    root: str
    source_path: str
    source_row: int
    source_sha256: str
    instrument_id: int
    raw_symbol: str
    contract_key: str
    lifetime_id: str
    definition_version: str
    known_at_ns: int
    valid_from_ns: int
    valid_until_ns: int
    tick_size: Decimal | None
    eligible: bool
    reason: str
    raw_fields_sha256: str

    def __post_init__(self) -> None:
        if self.root not in {"NQ", "ES"} or type(self.source_row) is not int or self.source_row < 0:
            raise ContractError("definition record requires an exact root and source row")
        if type(self.instrument_id) is not int or self.instrument_id <= 0:
            raise ContractError("definition record requires a positive raw instrument ID")
        if not all(isinstance(value, str) and value for value in (
                self.source_path, self.source_sha256, self.raw_symbol, self.contract_key,
                self.lifetime_id, self.definition_version, self.reason, self.raw_fields_sha256)):
            raise ContractError("definition record requires source and lifetime identities")
        if any(type(value) is not int for value in (self.known_at_ns, self.valid_from_ns, self.valid_until_ns)):
            raise ContractError("definition record clocks must be nanosecond integers")
        if self.valid_until_ns <= self.valid_from_ns:
            raise ContractError("definition lifetime is not a positive interval")
        timestamp(self.known_at_ns)
        timestamp(self.valid_from_ns)
        timestamp(self.valid_until_ns)
        if self.tick_size is not None and (not self.tick_size.is_finite() or self.tick_size <= 0):
            raise ContractError("definition tick size must be finite and positive")
        if type(self.eligible) is not bool:
            raise ContractError("definition eligibility must be explicit")

    @property
    def available_at_ns(self) -> int:
        return self.known_at_ns

    def covers(self, start_ns: int, end_ns: int) -> bool:
        return (self.known_at_ns <= start_ns and self.valid_from_ns <= start_ns
                and end_ns <= self.valid_until_ns)


@dataclass(frozen=True)
class DefinitionBlock:
    """Known-time invalid/deleted update that blocks an earlier raw ID."""

    root: str
    source_path: str
    source_row: int
    source_sha256: str
    instrument_id: int
    raw_symbol: str | None
    known_at_ns: int
    reason: str
    raw_fields_sha256: str

    def __post_init__(self) -> None:
        if self.root not in {"NQ", "ES"} or type(self.source_row) is not int or self.source_row < 0:
            raise ContractError("definition block requires an exact root and source row")
        if type(self.instrument_id) is not int or self.instrument_id <= 0:
            raise ContractError("definition block requires a positive raw instrument ID")
        if self.raw_symbol is not None and (not isinstance(self.raw_symbol, str) or not self.raw_symbol):
            raise ContractError("definition block raw symbol must be explicit text when supplied")
        if not all(isinstance(value, str) and value for value in (
                self.source_path, self.source_sha256, self.reason, self.raw_fields_sha256)):
            raise ContractError("definition block requires source and reason identities")
        if type(self.known_at_ns) is not int:
            raise ContractError("definition block known-at clock must be an integer")
        timestamp(self.known_at_ns)


@dataclass(frozen=True)
class DefinitionIndex:
    """Immutable, source-backed definition lookup used by the OHLC adapter."""

    root: str
    records: tuple[DefinitionRecord, ...]
    manifest: dict[str, Any]
    blocks: tuple[DefinitionBlock, ...] = ()
    unknown_instrument_ids: tuple[int, ...] = ()
    _by_instrument: dict[int, tuple[DefinitionRecord, ...]] = field(init=False, repr=False, compare=False)
    _blocks_by_instrument: dict[int, tuple[DefinitionBlock, ...]] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if (self.root not in {"NQ", "ES"} or not isinstance(self.records, tuple)
                or not isinstance(self.manifest, dict) or not isinstance(self.blocks, tuple)
                or not isinstance(self.unknown_instrument_ids, tuple)):
            raise ContractError("definition index requires a typed root, records and manifest")
        if any(not isinstance(record, DefinitionRecord) or record.root != self.root for record in self.records):
            raise ContractError("definition index contains an incompatible record")
        if any(not isinstance(block, DefinitionBlock) or block.root != self.root for block in self.blocks):
            raise ContractError("definition index contains an incompatible known-time block")
        if (any(type(instrument_id) is not int or instrument_id <= 0
                for instrument_id in self.unknown_instrument_ids)
                or len(set(self.unknown_instrument_ids)) != len(self.unknown_instrument_ids)):
            raise ContractError("definition index unknown-ID quarantine must be explicit and distinct")
        grouped: dict[int, list[DefinitionRecord]] = {}
        for record in self.records:
            grouped.setdefault(record.instrument_id, []).append(record)
        object.__setattr__(
            self,
            "_by_instrument",
            {instrument_id: tuple(sorted(values, key=lambda record: (
                record.valid_from_ns, record.known_at_ns, record.source_path, record.source_row,
            ))) for instrument_id, values in grouped.items()},
        )
        blocked: dict[int, list[DefinitionBlock]] = {}
        for block in self.blocks:
            blocked.setdefault(block.instrument_id, []).append(block)
        object.__setattr__(
            self,
            "_blocks_by_instrument",
            {instrument_id: tuple(sorted(values, key=lambda block: (
                block.known_at_ns, block.source_path, block.source_row,
            ))) for instrument_id, values in blocked.items()},
        )

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[DefinitionRecord]:
        return iter(self.records)

    def resolve(self, instrument_id: int, at: int) -> DefinitionRecord | None:
        """Resolve the latest known lifetime at a bar start.

        Records with unresolved tick terms are returned so the OHLC row can
        retain its identity while reporting the explicit term failure.
        """
        if type(instrument_id) is not int or instrument_id <= 0:
            raise ContractError("definition lookup requires a positive raw instrument ID")
        timestamp(at)
        if instrument_id in self.unknown_instrument_ids:
            return None
        known_records = [record for record in self._by_instrument.get(instrument_id, ())
                         if record.known_at_ns <= at]
        blocks = [block for block in self._blocks_by_instrument.get(instrument_id, ())
                  if block.known_at_ns <= at]
        if blocks:
            latest_block = max(block.known_at_ns for block in blocks)
            known_records = [record for record in known_records if record.known_at_ns > latest_block]
        if not known_records:
            return None
        newest = max(record.known_at_ns for record in known_records)
        latest = [record for record in known_records if record.known_at_ns == newest]
        if len(latest) != 1:
            raise IntegrityError("same-time definition corrections for one bar are ambiguous")
        if not latest[0].valid_from_ns <= at < latest[0].valid_until_ns:
            # A newer known update making the ID inactive cannot resurrect
            # an older, contradictory active lifetime. No roll mapping is
            # inferred for an ID reserved ahead of another activation.
            return None
        candidates = [record for record in known_records
                      if record.valid_from_ns <= at < record.valid_until_ns]
        lifetimes = {record.lifetime_id for record in candidates}
        if len(lifetimes) != 1:
            raise IntegrityError("overlapping definition lifetimes for one raw instrument ID are ambiguous")
        latest_known = max(record.known_at_ns for record in candidates)
        selected = [record for record in candidates if record.known_at_ns == latest_known]
        if len(selected) != 1:
            raise IntegrityError("same-time definition corrections for one bar are ambiguous")
        return selected[0]

    def is_blocked(self, instrument_id: int, at: int) -> bool:
        """Return whether an unresolved update quarantines this ID at a cut."""
        if type(instrument_id) is not int or instrument_id <= 0:
            raise ContractError("definition lookup requires a positive raw instrument ID")
        timestamp(at)
        if instrument_id in self.unknown_instrument_ids:
            return True
        blocks = [block for block in self._blocks_by_instrument.get(instrument_id, ())
                  if block.known_at_ns <= at]
        if not blocks:
            return False
        candidates = [record for record in self._by_instrument.get(instrument_id, ())
                      if record.known_at_ns <= at and record.valid_from_ns <= at
                      and at < record.valid_until_ns]
        return not candidates or max(block.known_at_ns for block in blocks) >= max(record.known_at_ns for record in candidates)


def _contract_key(root: str, instrument_id: int, raw_symbol: str, activation: int, expiration: int) -> str:
    return f"{root}:{raw_symbol}:{instrument_id}:{activation}:{expiration}"


def _definition_manifest_record(record: DefinitionRecord) -> dict[str, Any]:
    return {
        "source_path": record.source_path,
        "source_row": record.source_row,
        "source_sha256": record.source_sha256,
        "raw_fields_sha256": record.raw_fields_sha256,
        "instrument_id": record.instrument_id,
        "raw_symbol": record.raw_symbol,
        "contract_key": record.contract_key,
        "lifetime_id": record.lifetime_id,
        "definition_version": record.definition_version,
        "known_at_ns": record.known_at_ns,
        "valid_from_ns": record.valid_from_ns,
        "valid_until_ns": record.valid_until_ns,
        "tick_size": None if record.tick_size is None else str(record.tick_size),
        "eligible": record.eligible,
        "reason": record.reason,
    }


def _definition_block_manifest_record(block: DefinitionBlock) -> dict[str, Any]:
    return {
        "source_path": block.source_path,
        "source_row": block.source_row,
        "source_sha256": block.source_sha256,
        "raw_fields_sha256": block.raw_fields_sha256,
        "instrument_id": block.instrument_id,
        "raw_symbol": block.raw_symbol,
        "known_at_ns": block.known_at_ns,
        "reason": block.reason,
        "blocks_prior_lifetime": True,
    }


def _definition_record_from_row(row: dict[str, Any], *, root: str, source_path: str,
                               source_row: int, source_sha256: str) -> DefinitionRecord:
    if type(row.get("instrument_id")) is not int or row["instrument_id"] <= 0:
        raise ContractError("definition raw instrument ID must be an exact positive integer")
    if row.get("security_update_action") not in ("A", "M"):
        raise DependencyUnavailable("deleted or unsupported definition update needs a known-time block")
    raw_fields = repr(sorted(row.items(), key=lambda item: item[0])).encode("utf-8")
    raw_fields_sha256 = hashlib.sha256(raw_fields).hexdigest()
    source_id = f"{source_path}:row:{source_row}"
    definition = futures_definition(
        row,
        root=root,
        source_id=source_id,
        source_version=source_sha256,
        latency_ns=DEFINITION_LATENCY_NS,
        latency_scenario=DEFINITION_LATENCY_SCENARIO,
    )
    instrument_id = int(row["instrument_id"])
    raw_symbol = str(row["raw_symbol"])
    activation = int(row["activation"])
    expiration = int(row["expiration"])
    tick_size = definition.tick_size
    eligible = tick_size == QUARTER_TICK
    reason = "known_tick_0.25" if eligible else "missing_or_nonquarter_tick"
    lifetime_id = instrument_identity(definition)
    return DefinitionRecord(
        definition=definition,
        root=root,
        source_path=source_path,
        source_row=source_row,
        source_sha256=source_sha256,
        instrument_id=instrument_id,
        raw_symbol=raw_symbol,
        contract_key=_contract_key(root, instrument_id, raw_symbol, activation, expiration),
        lifetime_id=lifetime_id,
        definition_version=definition.key.definition_version,
        known_at_ns=definition.clocks.known_at,
        valid_from_ns=definition.clocks.valid_from,  # type: ignore[arg-type]
        valid_until_ns=definition.clocks.valid_until,  # type: ignore[arg-type]
        tick_size=tick_size,
        eligible=eligible,
        reason=reason,
        raw_fields_sha256=raw_fields_sha256,
    )


def _definition_block_from_row(row: dict[str, Any], *, root: str, source_path: str,
                               source_row: int, source_sha256: str,
                               reason: str) -> DefinitionBlock | None:
    instrument_id = row.get("instrument_id")
    event_at, provider_at = row.get("t"), row.get("ts_recv")
    if (type(instrument_id) is not int or instrument_id <= 0
            or any(type(value) is not int or not 0 < value < 2**63 for value in (event_at, provider_at))):
        return None
    known_at = max(event_at, provider_at) + DEFINITION_LATENCY_NS
    if known_at >= 2**63:
        return None
    raw_symbol = row.get("raw_symbol")
    return DefinitionBlock(
        root=root,
        source_path=source_path,
        source_row=source_row,
        source_sha256=source_sha256,
        instrument_id=instrument_id,
        raw_symbol=raw_symbol if isinstance(raw_symbol, str) and raw_symbol else None,
        known_at_ns=known_at,
        reason=reason,
        raw_fields_sha256=hashlib.sha256(
            repr(sorted(row.items(), key=lambda item: item[0])).encode("utf-8")
        ).hexdigest(),
    )


def read_definition_index(paths: Sequence[Path | str], *, data_root: Path, root: str,
                          maximum_rows: int = MAX_DEFINITION_ROWS) -> DefinitionIndex:
    """Read complete supplied definition files into a bounded bitemporal index.

    A definition with missing terms is retained in the manifest but is not an
    eligible lookup record.  The reader supplies only a tick-size requirement;
    multiplier evidence is intentionally outside this tick-only range adapter.
    """
    pa, ipc, pq = _pa()
    root = str(root).upper()
    if root not in {"NQ", "ES"}:
        raise ContractError("OHLC definition index supports NQ or ES only")
    _validate_bound(maximum_rows, name="maximum_rows", maximum=MAX_DEFINITION_ROWS)
    if not paths:
        raise ContractError("definition index requires at least one complete supplied file")

    records: list[DefinitionRecord] = []
    files: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    blocks: list[DefinitionBlock] = []
    unknown_instrument_ids: set[int] = set()
    total_rows = 0
    for raw_path in paths:
        source, relative = _safe_source(Path(raw_path), data_root)
        payload, source_sha256, before = _read_bounded_source(source, MAX_DEFINITION_FILE_BYTES)
        parquet = None
        try:
            parquet = pq.ParquetFile(pa.BufferReader(payload))
            _validate_definition_schema(parquet.schema_arrow)
            source_rows = int(parquet.metadata.num_rows)
            if source_rows < 0 or total_rows + source_rows > maximum_rows:
                raise DependencyUnavailable("definition files exceed the declared complete row bound")
            table = parquet.read()
            if table.num_rows != source_rows:
                raise IntegrityError("definition footer row count differs from the complete Arrow read")
            all_row_ipc_sha256 = _ipc_identity(table, ipc)
            schema_sha256 = _schema_identity(parquet.schema_arrow)
            source_schema = str(parquet.schema_arrow)
            file_unresolved: list[dict[str, Any]] = []
            for ordinal, row in enumerate(table.to_pylist()):
                try:
                    record = _definition_record_from_row(row, root=root, source_path=relative,
                                                         source_row=ordinal, source_sha256=source_sha256)
                    records.append(record)
                    if not record.eligible:
                        file_unresolved.append(_definition_manifest_record(record))
                except (ContractError, DependencyUnavailable, IntegrityError, KeyError, TypeError,
                        ValueError, ArithmeticError) as exc:
                    reason = type(exc).__name__ + ":" + str(exc)
                    issue = {"source_path": relative, "source_row": ordinal,
                             "source_sha256": source_sha256, "reason": reason}
                    block = _definition_block_from_row(
                        row, root=root, source_path=relative, source_row=ordinal,
                        source_sha256=source_sha256, reason=reason,
                    )
                    if block is not None:
                        blocks.append(block)
                        issue.update({"known_at_ns": block.known_at_ns,
                                      "blocks_prior_lifetime": True})
                    elif type(row.get("instrument_id")) is int and row["instrument_id"] > 0:
                        unknown_instrument_ids.add(int(row["instrument_id"]))
                        issue.update({"unknown_instrument_id": int(row["instrument_id"]),
                                      "blocks_at_unknown_clock": True})
                    else:
                        raise IntegrityError("unresolved definition has no exact raw ID; affected source domain cannot be bounded") from exc
                    unresolved.append(issue)
                    file_unresolved.append(issue)
            total_rows += source_rows
            files.append({
                "source_path": relative,
                "source_sha256": source_sha256,
                "size_bytes": len(payload),
                "source_rows": source_rows,
                "schema_sha256": schema_sha256,
                "schema": source_schema,
                "all_row_ipc_sha256": all_row_ipc_sha256,
                "unresolved_rows": file_unresolved,
            })
        except (pa.ArrowInvalid, pa.ArrowException) as exc:
            raise IntegrityError("definition Parquet source is corrupt within the complete bounded read") from exc
        finally:
            if parquet is not None:
                parquet.close()  # type: ignore[union-attr]
        _source_unchanged(source, before, source_sha256, MAX_DEFINITION_FILE_BYTES)

    records.sort(key=lambda record: (record.instrument_id, record.valid_from_ns,
                                     record.known_at_ns, record.source_path, record.source_row))
    manifest: dict[str, Any] = {
        "format_version": DEFINITION_INDEX_VERSION,
        "root": root,
        "latency_ns": DEFINITION_LATENCY_NS,
        "latency_scenario": DEFINITION_LATENCY_SCENARIO,
        "source_rows": total_rows,
        "indexed_records": sum(1 for record in records if record.eligible),
        "retained_records": len(records),
        "unresolved_rows": len(unresolved),
        "files": files,
        "records": [_definition_manifest_record(record) for record in records],
        "blocks": [_definition_block_manifest_record(block) for block in blocks],
        "unknown_instrument_ids": sorted(unknown_instrument_ids),
        "unresolved": unresolved,
        "scope": "complete supplied definition files; tick-only OHLC identity; no multiplier eligibility claim",
    }
    return DefinitionIndex(root=root, records=tuple(records), manifest=manifest,
                           blocks=tuple(blocks),
                           unknown_instrument_ids=tuple(sorted(unknown_instrument_ids)))


def _output_schema(pa: Any) -> Any:
    return pa.schema([
        pa.field("start_ns", pa.int64()),
        pa.field("end_ns", pa.int64()),
        pa.field("known_at_ns", pa.int64()),
        pa.field("open_ticks", pa.int64()),
        pa.field("high_ticks", pa.int64()),
        pa.field("low_ticks", pa.int64()),
        pa.field("close_ticks", pa.int64()),
        pa.field("volume", pa.int64()),
        pa.field("instrument_id", pa.int64()),
        pa.field("contract_key", pa.string()),
        pa.field("definition_version", pa.string()),
        pa.field("source_row", pa.int64()),
        pa.field("valid", pa.bool_()),
        pa.field("reasons", pa.string()),
    ])


def _output_table(rows: list[dict[str, Any]], pa: Any) -> Any:
    schema = _output_schema(pa)
    return pa.Table.from_arrays(
        [pa.array([row[name] for row in rows], type=schema.field(name).type)
         for name in _OUTPUT_FIELDS],
        schema=schema,
    )


def read_ohlc_partition(path: Path, *, data_root: Path, root: str,
                        definition_index: DefinitionIndex,
                        maximum_rows: int = MAX_OHLC_ROWS,
                        maximum_file_bytes: int = DEFAULT_OHLC_FILE_BYTES) -> tuple[Any, dict[str, Any]]:
    """Read one complete bounded QuantPad 1-minute OHLC Parquet source.

    The returned table contains one row for every source row.  Semantic faults
    are represented by ``valid=False`` and compact reason codes.  A corrupt,
    incomplete, unlocatable, or unsorted source raises before a table is
    returned, because no source row provenance can safely be assigned then.
    """
    pa, ipc, pq = _pa()
    root = str(root).upper()
    if root not in {"NQ", "ES"}:
        raise ContractError("OHLC admission supports NQ or ES only")
    if not isinstance(definition_index, DefinitionIndex) or definition_index.root != root:
        raise ContractError("OHLC admission requires a matching typed definition index")
    _validate_bound(maximum_rows, name="maximum_rows", maximum=MAX_OHLC_ROWS)
    _validate_bound(maximum_file_bytes, name="maximum_file_bytes", maximum=MAX_OHLC_FILE_BYTES)
    source, relative = _safe_source(Path(path), data_root)
    payload, source_sha256, before = _read_bounded_source(source, maximum_file_bytes)
    parquet = None
    try:
        try:
            parquet = pq.ParquetFile(pa.BufferReader(payload))
            _validate_ohlc_schema(parquet.schema_arrow, pa)
            source_rows = int(parquet.metadata.num_rows)
            if source_rows < 0 or source_rows > maximum_rows:
                raise DependencyUnavailable("OHLC source exceeds the declared complete row bound")
            raw_table = parquet.read()
            if raw_table.num_rows != source_rows:
                raise IntegrityError("OHLC footer row count differs from the complete Arrow read")
            raw_schema_sha256 = _schema_identity(parquet.schema_arrow)
            all_row_ipc_sha256 = _ipc_identity(raw_table, ipc)
            source_schema = str(parquet.schema_arrow)
        except (pa.ArrowInvalid, pa.ArrowException) as exc:
            raise IntegrityError("OHLC Parquet source is corrupt within the complete bounded read") from exc
    finally:
        if parquet is not None:
            parquet.close()
    _source_unchanged(source, before, source_sha256, maximum_file_bytes)

    output_rows: list[dict[str, Any]] = []
    previous_t: int | None = None
    reason_counts: Counter[str] = Counter()
    raw_rows = raw_table.to_pylist()
    for ordinal, raw in enumerate(raw_rows):
        if type(raw.get("t")) is not int or not 0 <= raw["t"] < 2**63:
            raise IntegrityError("OHLC source contains an unlocatable int64 millisecond timestamp")
        t_ms = int(raw["t"])
        if previous_t is not None and t_ms <= previous_t:
            raise IntegrityError("OHLC source timestamps are not strictly ordered")
        previous_t = t_ms

        start_ns = t_ms * NANOSECONDS_PER_MILLISECOND
        if start_ns > 2**63 - 1 or start_ns < -(2**63):
            raise IntegrityError("OHLC millisecond timestamp cannot be represented as int64 nanoseconds")
        end_ns = start_ns + BAR_NANOSECONDS
        if end_ns > 2**63 - 1:
            raise IntegrityError("OHLC bar end cannot be represented as int64 nanoseconds")
        known_at_ns = end_ns + 60 * 1_000_000_000
        if known_at_ns > 2**63 - 1:
            raise IntegrityError("OHLC availability timestamp cannot be represented as int64 nanoseconds")
        reasons: list[str] = []
        if t_ms % BAR_MILLISECONDS != 0:
            reasons.append("off_minute_grid")

        open_ticks, open_reason = _quarter_ticks(raw.get("o"), name="open")
        high_ticks, high_reason = _quarter_ticks(raw.get("h"), name="high")
        low_ticks, low_reason = _quarter_ticks(raw.get("l"), name="low")
        close_ticks, close_reason = _quarter_ticks(raw.get("c"), name="close")
        for reason in (open_reason, high_reason, low_reason, close_reason):
            if reason:
                reasons.append(reason)
        volume, volume_reason = _positive_integral_volume(raw.get("v"))
        if volume_reason:
            reasons.append(volume_reason)
        instrument_id, instrument_reason = _instrument_id(raw.get("instrument_id"))
        if instrument_reason:
            reasons.append(instrument_reason)

        if not any(value is None for value in (open_ticks, high_ticks, low_ticks, close_ticks)):
            assert open_ticks is not None and high_ticks is not None and low_ticks is not None and close_ticks is not None
            if high_ticks < max(open_ticks, close_ticks, low_ticks):
                reasons.append("high_below_ohlc_envelope")
            if low_ticks > min(open_ticks, close_ticks, high_ticks):
                reasons.append("low_above_ohlc_envelope")

        definition: DefinitionRecord | None = None
        resolution_failed = False
        if instrument_id is not None:
            try:
                definition = definition_index.resolve(instrument_id, start_ns)
            except (ContractError, IntegrityError) as exc:
                resolution_failed = True
                reasons.append("ambiguous_definition")
                reason_counts[type(exc).__name__] += 1
            if definition is None and not resolution_failed:
                reasons.append(
                    "definition_blocked_by_unresolved_update"
                    if definition_index.is_blocked(instrument_id, start_ns)
                    else "definition_not_available_at_bar_start"
                )
            if definition is not None:
                if not definition.covers(start_ns, end_ns):
                    reasons.append("definition_not_active_through_bar_end")
                elif definition.tick_size != QUARTER_TICK:
                    reasons.append("definition_tick_not_quarter")

        compact_reasons = _reason_string(reasons)
        valid = not compact_reasons
        reason_counts.update(reasons)
        output_rows.append({
            "start_ns": start_ns,
            "end_ns": end_ns,
            "known_at_ns": known_at_ns if definition is None else max(known_at_ns, definition.known_at_ns),
            "open_ticks": open_ticks,
            "high_ticks": high_ticks,
            "low_ticks": low_ticks,
            "close_ticks": close_ticks,
            "volume": volume,
            "instrument_id": instrument_id,
            "contract_key": None if definition is None else definition.contract_key,
            "definition_version": None if definition is None else definition.definition_version,
            "source_row": ordinal,
            "valid": valid,
            "reasons": compact_reasons,
        })

    output = _output_table(output_rows, pa)
    output_schema_sha256 = _schema_identity(output.schema)
    valid_rows = sum(1 for row in output_rows if row["valid"])
    manifest: dict[str, Any] = {
        "format_version": OHLC_FORMAT_VERSION,
        "dataset_id": f"quantpad/cme__{root.lower()}-continuous-futures__ohlcv-1m",
        "root": root,
        "source_path": relative,
        "source_rows": source_rows,
        "output_rows": len(output_rows),
        "valid_rows": valid_rows,
        "invalid_rows": len(output_rows) - valid_rows,
        "source_bytes": len(payload),
        "source_sha256": source_sha256,
        "raw_file_sha256": source_sha256,
        "raw_file_retained": True,
        "source_schema": source_schema,
        "source_schema_sha256": raw_schema_sha256,
        "all_row_ipc_sha256": all_row_ipc_sha256,
        "all_row_ipc_rows": source_rows,
        "output_schema_sha256": output_schema_sha256,
        "source_row_provenance": "zero-based complete-source physical row ordinal; raw source file hash binds every ordinal",
        "definition_index_manifest_sha256": digest(definition_index.manifest),
        "bar_interval_ms": BAR_MILLISECONDS,
        "price_tick": "0.25",
        "availability_assumption": "bar_end_plus_60s",
        "known_at_rule": "end_ns + 60_000_000_000; max with definition known_at_ns when a definition is associated",
        "quality_counts": dict(sorted(reason_counts.items())),
        "status": "accepted" if valid_rows == source_rows else "quarantined",
        "semantic_scope": "valid rows only; invalid rows remain quality records and affected windows must be censored",
    }
    return output, manifest
