"""Bounded streaming readers. Container fingerprints are explicitly metadata-only."""

from dataclasses import dataclass
import io
from pathlib import Path
from typing import Iterator

from trading_research.data.events import MBP_EXPORT_FIELDS, LatencyScenario, SourceAddress, normalize_mbp
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import digest


# Primary provider common-fields rtype table; unknown additions need an explicit
# schema mapping. A single-schema header cannot silently become a mixed stream.
_DBN_SCHEMA_RTYPE = {
    "trades": 0, "mbp-1": 1, "tbbo": 1, "mbp-10": 10, "status": 18,
    "definition": 19, "imbalance": 20, "statistics": 24,
    "ohlcv-1s": 32, "ohlcv-1m": 33, "ohlcv-1h": 34, "ohlcv-1d": 35,
    "mbo": 160, "cmbp-1": 177, "cbbo-1s": 192, "cbbo-1m": 193,
    "tcbbo": 194, "bbo-1s": 195, "bbo-1m": 196,
}


def _stamp(path: Path) -> dict:
    stat = path.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns, "inode": stat.st_ino}


def _safe_source(path: Path, root: Path) -> tuple[Path, str]:
    root, path = Path(root).resolve(), Path(path).resolve()
    if not path.is_relative_to(root) or path.is_relative_to(Path("/workspace/archive")):
        raise ContractError("source must be inside the declared, non-excluded data root")
    return path, str(path.relative_to(root))


def parquet_mbp(path: Path, *, data_root: Path, dataset_id: str, acquisition_version: str,
                scenario: LatencyScenario, max_rows: int = 4096,
                row_groups: tuple[int, ...] = (0,), batch_size: int = 4096,
                expected_schema=None) -> Iterator:
    """Diagnostic bounded prefix; this API does not accept a complete partition.

    Supply the registered Arrow schema to reject field, type or metadata drift
    before yielding records. Its absence does not certify a new schema.
    """
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise DependencyUnavailable("install the pinned data extra to read Parquet") from exc
    path, relative = _safe_source(path, data_root)
    if type(max_rows) is not int or max_rows <= 0 or not 1 <= batch_size <= 65536:
        raise ContractError("reader requires positive bounded rows and a bounded batch size")
    before = _stamp(path)
    pf = None
    try:
        pf = pq.ParquetFile(path)
        if expected_schema is not None:
            if not isinstance(expected_schema, pa.Schema):
                raise ContractError("expected schema must be the registered Arrow schema")
            if not pf.schema_arrow.equals(expected_schema, check_metadata=True):
                raise ContractError("source schema differs from its declared field/type/metadata contract")
        if not MBP_EXPORT_FIELDS.issubset(pf.schema_arrow.names):
            raise ContractError("source MBP schema omits required fields, including in an empty container")
        from trading_research.data.arrow_fields import schema_identity
        schema = schema_identity(pf.schema_arrow)
        if str(pf.schema_arrow.field("t").type) != "int64":
            raise ContractError("QuantPad MBP t requires the certified int64-nanosecond profile")
        if pf.metadata.num_row_groups == 0 and pf.metadata.num_rows == 0 and row_groups in {(0,), ()}:
            return
        if (not row_groups or len(set(row_groups)) != len(row_groups)
                or any(type(g) is not int or not 0 <= g < pf.metadata.num_row_groups for g in row_groups)):
            raise ContractError("explicit unique row groups required")
        if list(row_groups) != sorted(row_groups):
            raise ContractError("source row-group order must be preserved")
        version = digest({"relative_path": relative, "stamp": before, "schema": schema,
                          "identity_basis": "metadata_only_with_per_row_content_hash"})
        count = 0
        for group in row_groups:
            row = 0
            for batch in pf.iter_batches(batch_size=batch_size, row_groups=[group], use_threads=False):
                remaining = max_rows - count
                for fields in batch.slice(0, min(batch.num_rows, remaining)).to_pylist():
                    address = SourceAddress(dataset_id, acquisition_version, relative, version,
                                            f"row_group:{group}", row, schema)
                    yield normalize_mbp(fields, address, native=False, scenario=scenario)
                    row += 1
                    count += 1
                if count >= max_rows:
                    return
    except (pa.ArrowInvalid, OSError) as exc:
        raise IntegrityError("Parquet container could not be decoded intact within the attempted read") from exc
    finally:
        if pf is not None:
            pf.close()
        if _stamp(path) != before:
            raise IntegrityError("source container changed during its bounded read")


@dataclass(frozen=True)
class NativeRecord:
    address: SourceAddress
    kind: str
    raw_bytes: bytes
    fields: dict
    dbn_version: int | None = None
    layout_id: str | None = None


class _BudgetedSource(io.RawIOBase):
    """Bound compressed read-ahead; reaching a budget is not source EOF."""

    def __init__(self, source, *, budget: int, source_size: int):
        super().__init__()
        self.source, self.budget, self.source_size = source, budget, source_size
        self.bytes_read = 0
        self.budget_exhausted = False

    def readable(self):
        return True

    def read(self, size=-1):
        if self.bytes_read >= self.source_size:
            return b""
        remaining = self.budget - self.bytes_read
        if remaining <= 0:
            self.budget_exhausted = True
            raise DependencyUnavailable("compressed-byte budget ended before source EOF or requested record prefix")
        amount = min(65536 if size < 0 else size, remaining)
        payload = self.source.read(amount)
        self.bytes_read += len(payload)
        return payload

    def readinto(self, buffer):
        payload = self.read(len(buffer))
        buffer[:len(payload)] = payload
        return len(payload)


def native_records(path: Path, *, data_root: Path, dataset_id: str, acquisition_version: str,
                   max_records: int = 4096, max_compressed_bytes: int = 16 * 1024 * 1024,
                   max_decompressed_bytes: int = 64 * 1024 * 1024,
                   expected_schema: str | None = None, expected_version: int | None = None) -> Iterator[NativeRecord]:
    """Read a bounded native prefix, checking compressed EOF when reached.

    A record-count or byte bound does not certify the unread suffix. Arrow's
    streaming decompressor verifies frame termination; DBNDecoder alone may
    have an empty *decoded* buffer despite a truncated compressed frame.
    """
    try:
        import databento_dbn as dbn
        import pyarrow as pa
    except ImportError as exc:
        raise DependencyUnavailable("install the pinned data extra to read native DBN") from exc
    path, relative = _safe_source(path, data_root)
    if (type(max_records) is not int or max_records <= 0 or type(max_compressed_bytes) is not int
            or max_compressed_bytes < 65536 or type(max_decompressed_bytes) is not int
            or max_decompressed_bytes < 65536):
        raise ContractError("native reader requires explicit row, compressed and decompressed byte bounds")
    before = _stamp(path)
    version = digest({"relative_path": relative, "stamp": before,
                      "identity_basis": "metadata_only_with_per_record_raw_bytes"})
    decoder = dbn.DBNDecoder(compression=dbn.Compression.NONE, upgrade_policy=dbn.VersionUpgradePolicy.AS_IS)
    count, decoded_bytes = 0, 0
    metadata_version = None
    metadata_ts_out = False
    metadata_prefix = bytearray()
    metadata_length = None
    schema_rtype = None
    bounded = None
    try:
        with path.open("rb") as stream:
            bounded = _BudgetedSource(stream, budget=max_compressed_bytes, source_size=before["size"])
            with pa.CompressedInputStream(bounded, "zstd") as inflated:
                while True:
                    if decoded_bytes >= max_decompressed_bytes:
                        raise DependencyUnavailable("decompressed-byte budget ended before source EOF or requested prefix")
                    chunk = inflated.read(min(65536, max_decompressed_bytes - decoded_bytes))
                    if not chunk:
                        if metadata_version is None:
                            raise IntegrityError("native input ended without complete DBN metadata")
                        if decoder.buffer():
                            raise IntegrityError("native input ended with an incomplete decoded record")
                        return
                    decoded_bytes += len(chunk)
                    if metadata_version is None:
                        metadata_prefix.extend(chunk)
                        if len(metadata_prefix) >= 8:
                            if metadata_prefix[:3] != b"DBN":
                                raise IntegrityError("native metadata is missing its DBN magic header")
                            metadata_length = 8 + int.from_bytes(metadata_prefix[4:8], "little")
                            if metadata_length > max_decompressed_bytes:
                                raise DependencyUnavailable("complete native metadata exceeds the decompressed-byte budget")
                    for record in decoder.write_and_decode(chunk):
                        if isinstance(record, dbn.Metadata):
                            if metadata_version is not None:
                                raise IntegrityError("unexpected replacement DBN metadata in one source stream")
                            metadata_version = int(record.version)
                            if metadata_version not in {1, 2, 3}:
                                raise ContractError("native source version needs explicit layout registration")
                            metadata_ts_out = bool(record.ts_out)
                            if record.symbol_cstr_len != (22 if metadata_version == 1 else 71):
                                raise ContractError("native symbol width differs from the registered version layout")
                            if metadata_length is None or len(metadata_prefix) < metadata_length:
                                raise IntegrityError("decoded metadata has no complete original byte extent")
                            original_metadata = bytes(metadata_prefix[:metadata_length])
                            metadata_prefix.clear()
                            schema_name = None if record.schema is None else str(record.schema)
                            if schema_name is not None:
                                if schema_name not in _DBN_SCHEMA_RTYPE:
                                    raise ContractError("native schema needs an explicit record-type mapping")
                                schema_rtype = _DBN_SCHEMA_RTYPE[schema_name]
                            if ((expected_version is not None and metadata_version != expected_version)
                                    or (expected_schema is not None and str(record.schema) != expected_schema)):
                                raise ContractError("native schema/version differs from its declared contract")
                            # Metadata is retained too; it does not consume the market-record limit.
                            address = SourceAddress(dataset_id, acquisition_version, relative, version, "metadata", 0,
                                                    f"dbn-v{metadata_version}-as-is")
                            fields = {key: getattr(record, key) for key in
                                      ("version", "dataset", "start", "end", "limit", "ts_out", "symbol_cstr_len",
                                       "symbols", "partial", "not_found", "mappings")}
                            fields.update(schema=schema_name,
                                          stype_in=None if record.stype_in is None else str(record.stype_in),
                                          stype_out=str(record.stype_out))
                            # Metadata.encode() reconstructs and zeroes padding.
                            # Retain the actual uncompressed source slice instead.
                            yield NativeRecord(address, "Metadata", original_metadata, fields, metadata_version)
                            continue
                        if metadata_version is None:
                            raise IntegrityError("DBN records arrived without source metadata")
                        if schema_rtype is not None and int(record.rtype) != schema_rtype:
                            raise IntegrityError("record type changed inside a declared single-schema DBN source")
                        from trading_research.data.native_fields import decode_record_fields
                        raw, kind = bytes(record), type(record).__name__
                        fields, layout_id = decode_record_fields(raw, kind=kind, dbn_version=metadata_version,
                                                               ts_out=metadata_ts_out)
                        address = SourceAddress(dataset_id, acquisition_version, relative, version, "native_record", count,
                                                f"dbn-v{metadata_version}-as-is:{layout_id}")
                        yield NativeRecord(address, kind, raw, fields, metadata_version, layout_id)
                        count += 1
                        if count >= max_records:
                            return
    except (dbn.DBNError, pa.ArrowInvalid, OSError) as exc:
        if bounded is not None and bounded.budget_exhausted:
            raise DependencyUnavailable("compressed-byte budget ended before the requested prefix") from exc
        raise IntegrityError("native container is corrupt or truncated in the attempted read") from exc
    finally:
        if _stamp(path) != before:
            raise IntegrityError("source container changed during its bounded read")


def native_mbp(record: NativeRecord, *, scenario: LatencyScenario):
    if record.kind != "MBP1Msg":
        raise ContractError("non-MBP native record must remain in its own raw/metadata channel")
    from trading_research.data.native_fields import reassemble_native_fields
    reassemble_native_fields(record)
    return normalize_mbp(record.fields, record.address, native=True, scenario=scenario, raw_record=record.raw_bytes)
