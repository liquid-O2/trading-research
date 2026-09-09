"""Literal flat Arrow fields without Python datetime or numeric coercion (F01)."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterator

from trading_research.data.events import SourceAddress
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import canonical_json, digest

RAW_ARROW_VERSION = "arrow-flat-fields-v1"


def schema_identity(schema) -> str:
    """Hash the full field/type/nullability/metadata representation, never display text."""
    return hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()


def validate_flat_schema(schema) -> None:
    import pyarrow as pa
    if not isinstance(schema, pa.Schema) or len(schema.names) != len(set(schema.names)):
        raise ContractError("raw Arrow requires a complete schema with unique field names")
    if pa.__version__ != "25.0.1":
        raise ContractError("Arrow provider version changed; review raw scalar and IPC compatibility")
    ordinary = {"int8", "int16", "int32", "int64", "uint32", "double", "bool", "null",
                "string", "large_string", "date32[day]", "timestamp[ns, tz=UTC]", "timestamp[us, tz=UTC]",
                "dictionary<values=string, indices=uint32, ordered=0>",
                "dictionary<values=string, indices=int8, ordered=0>"}
    for field in schema:
        if str(field.type) not in ordinary:
            raise ContractError(f"unregistered raw Arrow physical type for {field.name}: {field.type}")


def physical_row_fields(batch, row: int) -> bytes:
    """All logical column values with exact physical types and float bits.

    The complete dictionary and index buffers also remain in the row IPC.
    Dictionary values in this view make identities independent of batch layout.
    Underlying padding and invalid-slot buffers have no claimed scalar meaning.
    """
    import pyarrow as pa
    validate_flat_schema(batch.schema)
    if type(row) is not int or not 0 <= row < batch.num_rows:
        raise ContractError("raw field extraction needs an actual batch row")
    result = []
    for field, array in zip(batch.schema, batch.columns, strict=True):
        scalar = array[row]
        if not scalar.is_valid:
            value = None
        elif pa.types.is_floating(field.type):
            offset = (array.offset+row)*8
            value = {"bits_le": memoryview(array.buffers()[1])[offset:offset+8].tobytes().hex()}
        elif pa.types.is_timestamp(field.type) or pa.types.is_date(field.type):
            value = scalar.value  # Exact physical integer; ns need not fit datetime microseconds.
        else:
            value = scalar.as_py()
        result.append([field.name, {"type": str(field.type), "value": value}])
    return canonical_json(result)


@dataclass(frozen=True)
class RawArrowRow:
    address: SourceAddress
    raw_fields: bytes
    raw_ipc: bytes
    decoder_version: str = RAW_ARROW_VERSION

    @property
    def content_hash(self) -> str:
        return digest({"decoder": self.decoder_version, "schema": self.address.schema_version,
                       "fields": self.raw_fields})

    @property
    def id(self) -> str:
        return digest({"source_row_id": self.address.id, "content": self.content_hash})

    def values(self) -> dict:
        self.checked_batch()
        return dict(json.loads(self.raw_fields))

    def checked_batch(self):
        import pyarrow as pa
        if self.decoder_version != RAW_ARROW_VERSION:
            raise ContractError("raw Arrow decoder changed; replay under the new identity")
        try:
            with pa.ipc.open_stream(pa.BufferReader(self.raw_ipc)) as reader:
                batches = list(reader)
        except pa.ArrowInvalid as exc:
            raise ContractError("raw Arrow IPC cannot be decoded intact") from exc
        if len(batches) != 1 or batches[0].num_rows != 1:
            raise ContractError("raw row IPC must contain exactly one complete record")
        batch = batches[0]
        if (schema_identity(batch.schema) != self.address.schema_version
                or physical_row_fields(batch, 0) != self.raw_fields):
            raise ContractError("raw Arrow row schema or fields differ from the retained IPC")
        return batch


def parquet_raw_rows(path: Path, *, data_root: Path, dataset_id: str, acquisition_version: str,
                     expected_schema, max_rows: int = 4096, row_groups: tuple[int, ...] = (0,),
                     batch_size: int = 4096, max_output_bytes: int = 64*1024**2,
                     max_batch_bytes: int = 64*1024**2) -> Iterator[RawArrowRow]:
    """Diagnostic prefix retaining every column; no partition admission claim."""
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise DependencyUnavailable("raw Arrow decoding requires the pinned data extra") from exc
    from trading_research.data.readers import _safe_source, _stamp
    validate_flat_schema(expected_schema)
    if (any(type(v) is not int or v <= 0 for v in (max_rows, batch_size, max_output_bytes, max_batch_bytes))
            or batch_size > 65536 or not dataset_id or not acquisition_version):
        raise ContractError("raw Arrow prefix requires source versions and positive row/output/batch bounds")
    path, relative = _safe_source(path, data_root)
    if path.suffix != ".parquet":
        raise ContractError("unfinished or unregistered source suffix cannot be a Parquet input")
    before = _stamp(path)
    count, output_bytes = 0, 0
    try:
        with pq.ParquetFile(path) as pf:
            if not pf.schema_arrow.equals(expected_schema, check_metadata=True):
                raise ContractError("raw source differs from its declared complete Arrow schema")
            schema_version = schema_identity(expected_schema)
            source_version = digest({"relative_path": relative, "stamp": before, "schema": schema_version,
                                     "identity_basis": "metadata_only_with_per_row_content"})
            if pf.metadata.num_rows == 0 and pf.metadata.num_row_groups == 0 and row_groups in {(0,), ()}:
                return
            if (not row_groups or len(set(row_groups)) != len(row_groups)
                    or any(type(g) is not int or not 0 <= g < pf.metadata.num_row_groups for g in row_groups)
                    or tuple(sorted(row_groups)) != row_groups):
                raise ContractError("raw prefix requires ordered unique physical row groups")
            for group in row_groups:
                physical_row = 0
                for batch in pf.iter_batches(row_groups=[group], batch_size=batch_size, use_threads=False):
                    if batch.nbytes > max_batch_bytes:
                        raise DependencyUnavailable("decoded raw Arrow batch exceeds its declared byte bound")
                    for row in range(min(batch.num_rows, max_rows-count)):
                        raw_fields = physical_row_fields(batch, row)
                        sink = pa.BufferOutputStream()
                        with pa.ipc.new_stream(sink, batch.schema) as writer:
                            writer.write_batch(batch.slice(row, 1))
                        raw_ipc = sink.getvalue().to_pybytes()
                        output_bytes += len(raw_fields)+len(raw_ipc)
                        if output_bytes > max_output_bytes:
                            raise DependencyUnavailable("raw Arrow prefix exceeds its declared decoded-output bound")
                        address = SourceAddress(dataset_id, acquisition_version, relative, source_version,
                                                f"row_group:{group}", physical_row, schema_version)
                        yield RawArrowRow(address, raw_fields, raw_ipc)
                        count += 1
                        physical_row += 1
                    if count >= max_rows:
                        return
    except pa.ArrowInvalid as exc:
        raise IntegrityError("Parquet source is corrupt within the attempted raw-field read") from exc
    except OSError as exc:
        if exc.errno is not None:
            raise
        raise IntegrityError("Parquet source could not be decoded intact") from exc
    finally:
        if _stamp(path) != before:
            raise IntegrityError("source changed during raw Arrow prefix decoding")
