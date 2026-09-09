"""Literal, complete and atomic MBP partition admission (F01 / SR-F01).

Registered boundary: validation/F01_PARTITION_PROTOCOL.md. This intentionally
small reference snapshots bounded input bytes. It is not the full-history or
incremental materializer, and admission does not certify market eligibility.
"""

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
from typing import Iterator

from trading_research.data.events import (
    DECODER_VERSION, MBP_EXPORT_FIELDS, CanonicalEvent, LatencyScenario, SourceAddress,
    decode_fields, normalize_mbp,
)
from trading_research.data.readers import _safe_source, _stamp
from trading_research.data.arrow_fields import schema_identity
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import (
    ArtifactRef, ArtifactStore, artifact_ref, canonical_json, code_manifest, digest, publish_new,
)

_PACKAGE_ROOT = Path(__file__).resolve().parents[3]


def _code_version() -> str:
    # Conservative reference invalidation. A narrower optimized dependency
    # closure needs its own transitive-input parity evidence.
    return digest(code_manifest(_PACKAGE_ROOT))


@dataclass(frozen=True)
class PartitionBudget:
    max_source_bytes: int
    max_rows: int
    max_output_bytes: int
    chunk_rows: int

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in asdict(self).values()) or self.chunk_rows > 65536:
            raise ContractError("partition admission requires positive bounded bytes, rows and chunk size")


class PartitionStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.artifacts = ArtifactStore(self.root / "artifacts")
        self.index = self.root / "manifests"
        self.locator_index = self.root / "locators"

    def manifests(self) -> list[ArtifactRef]:
        import json
        return [artifact_ref(json.loads(p.read_bytes())) for p in sorted(self.index.glob("*.json"))]

    def manifest(self, reference: ArtifactRef) -> dict:
        import json
        if reference.kind != "partition_manifest":
            raise ContractError("consumer requires a committed partition manifest")
        pointer = self.index / f"{reference.sha256}.json"
        if not pointer.exists():
            raise DependencyUnavailable("partition has no atomic admission record")
        if artifact_ref(json.loads(pointer.read_bytes())) != reference:
            raise IntegrityError("partition admission pointer differs from its manifest")
        return self.artifacts.read_json(reference)

    def locators(self, reference: ArtifactRef) -> list[dict]:
        import json
        source = self.manifest(reference)["source"]
        result = []
        for path in sorted(self.locator_index.glob("*.json")):
            ref = artifact_ref(json.loads(path.read_bytes()))
            item = self.artifacts.read_json(ref)
            if item["source"] == source:
                result.append(item)
        return result

    def ingest_parquet(self, path: Path, *, data_root: Path, dataset_id: str,
                       acquisition_version: str, expected_schema, scenario: LatencyScenario,
                       budget: PartitionBudget, fault_hook=None) -> ArtifactRef:
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise DependencyUnavailable("partition admission needs the pinned Arrow dependency") from exc
        if not isinstance(expected_schema, pa.Schema) or not MBP_EXPORT_FIELDS.issubset(expected_schema.names):
            raise ContractError("register the complete MBP Arrow schema before partition admission")
        if len(expected_schema.names) != len(set(expected_schema.names)):
            raise ContractError("duplicate physical field names are not an admissible schema")
        if not isinstance(budget, PartitionBudget):
            raise ContractError("partition admission requires an explicit resource budget")
        if not dataset_id or not acquisition_version or not isinstance(scenario, LatencyScenario):
            raise ContractError("partition admission requires source versions and a named availability scenario")
        code_version = _code_version()
        path, relative = _safe_source(path, data_root)
        if path.suffix != ".parquet":
            raise ContractError("a partial download is not a completed Parquet source")
        before = _stamp(path)
        if before["size"] > budget.max_source_bytes:
            raise DependencyUnavailable("complete source exceeds the registered snapshot-byte limit")
        with path.open("rb") as stream:
            payload = stream.read(budget.max_source_bytes + 1)
        if _stamp(path) != before or len(payload) != before["size"]:
            raise IntegrityError("source changed while taking the immutable bounded snapshot")
        if len(payload) > budget.max_source_bytes:
            raise DependencyUnavailable("complete source exceeds the registered snapshot-byte limit")
        raw_source = self.artifacts.put_bytes(payload, kind="immutable_source_partition")
        source = {"dataset_id": dataset_id, "acquisition_version": acquisition_version,
                  "sha256": raw_source.sha256, "size_bytes": raw_source.size_bytes}
        locator = self.artifacts.put_json({"source": source, "data_root": str(Path(data_root).resolve()),
                                           "relative_path": relative, "observed_stamp": before}, kind="source_locator")
        publish_new(self.locator_index / f"{locator.sha256}.json", canonical_json(asdict(locator)))
        chunks, pending, output_bytes, accepted, rejected, ordinal = [], [], 0, 0, 0, 0

        def put(payload: bytes, kind: str) -> ArtifactRef:
            nonlocal output_bytes
            if output_bytes + len(payload) > budget.max_output_bytes:
                raise DependencyUnavailable("partition output exceeds the registered byte limit")
            output_bytes += len(payload)
            return self.artifacts.put_bytes(payload, kind=kind)

        def flush():
            if pending:
                chunks.append(asdict(put(canonical_json(pending), "partition_rows")))
                pending.clear()
                if fault_hook:
                    fault_hook("after_chunk")

        try:
            with pq.ParquetFile(pa.BufferReader(payload)) as pf:
                if not pf.schema_arrow.equals(expected_schema, check_metadata=True):
                    raise ContractError("complete source differs from the registered schema")
                if str(pf.schema_arrow.field("t").type) != "int64":
                    raise ContractError("declared MBP profile requires int64 nanosecond event time")
                count = pf.metadata.num_rows
                if count > budget.max_rows:
                    raise DependencyUnavailable("complete source exceeds the registered row limit")
                schema_version = schema_identity(pf.schema_arrow)
                schema_bytes = pf.schema_arrow.serialize().to_pybytes()
                group_sizes = [pf.metadata.row_group(g).num_rows for g in range(pf.metadata.num_row_groups)]
                for group, group_size in enumerate(group_sizes):
                    row = 0
                    for batch in pf.iter_batches(row_groups=[group], batch_size=budget.chunk_rows, use_threads=False):
                        for batch_row, fields in enumerate(batch.to_pylist()):
                            address = SourceAddress(dataset_id, acquisition_version, relative, raw_source.sha256,
                                                    f"row_group:{group}", row, schema_version, raw_source.sha256)
                            record = {"ordinal": ordinal, "row_group": group, "row": row}
                            try:
                                event = normalize_mbp(fields, address, native=False, scenario=scenario)
                                record.update(status="decoded", event_id=event.id, raw_fields=event.raw_fields.hex())
                                accepted += 1
                            except ContractError as exc:
                                # Arrow retains physical types and all columns even if a
                                # newly supplied scalar type has no canonical mapping yet.
                                sink = pa.BufferOutputStream()
                                with pa.ipc.new_stream(sink, batch.schema) as writer:
                                    writer.write_batch(batch.slice(batch_row, 1))
                                raw_row = put(sink.getvalue().to_pybytes(), "rejected_arrow_row")
                                record.update(status="rejected", reason_code="decode_contract_violation",
                                              detail=str(exc), raw_arrow_row=asdict(raw_row))
                                rejected += 1
                            pending.append(record)
                            row += 1
                            ordinal += 1
                            if len(pending) >= budget.chunk_rows:
                                flush()
                    if row != group_size:
                        raise IntegrityError("decoded physical row group is incomplete")
                if ordinal != count or accepted + rejected != count:
                    raise IntegrityError("accepted and rejected rows do not reconcile to the complete source")
                flush()
        except InterruptedError:
            raise
        except pa.ArrowInvalid as exc:
            raise IntegrityError("complete Parquet source could not be decoded intact") from exc
        except OSError as exc:
            if exc.errno is not None:
                raise  # Storage/OS failure is not evidence that the source is corrupt.
            raise IntegrityError("complete Parquet source could not be decoded intact") from exc

        if _code_version() != code_version:
            raise IntegrityError("implementation changed during partition admission")
        manifest = {"format_version": "literal-mbp-partition-v1", "code_version": code_version, "source": source,
                    "raw_source": asdict(raw_source), "schema_version": schema_version,
                    "schema_arrow": schema_bytes.hex(), "decoder_version": DECODER_VERSION,
                    "scenario": asdict(scenario), "source_rows": count, "row_group_sizes": group_sizes,
                    "accepted_rows": accepted, "rejected_rows": rejected,
                    "status": "quarantined" if rejected else "accepted",
                    "acceptance_extent": "complete source/schema decoding; market-operation eligibility remains separate",
                    "chunks": chunks, "chunk_rows": budget.chunk_rows,
                    "row_payload_bytes": output_bytes, "source_snapshot_bytes": len(payload)}
        manifest_payload = canonical_json(manifest)
        reference = ArtifactRef(hashlib.sha256(manifest_payload).hexdigest(), len(manifest_payload), "partition_manifest")
        pointer = canonical_json(asdict(reference))
        if output_bytes + len(manifest_payload) + len(pointer) > budget.max_output_bytes:
            raise DependencyUnavailable("complete manifest exceeds the registered output-byte limit")
        if fault_hook:
            fault_hook("before_manifest")
        self.artifacts.put_bytes(manifest_payload, kind=reference.kind)
        publish_new(self.index / f"{reference.sha256}.json", pointer)
        return reference

    def _checked_rows(self, reference: ArtifactRef) -> tuple[dict, list[dict]]:
        manifest = self.manifest(reference)
        if manifest["format_version"] != "literal-mbp-partition-v1":
            raise ContractError("partition storage format needs an explicit migration")
        if manifest["decoder_version"] != DECODER_VERSION or manifest["code_version"] != _code_version():
            raise ContractError("decoder version changed; explicit partition replay/migration required")
        raw_source = artifact_ref(manifest["raw_source"])
        if (raw_source.sha256 != manifest["source"]["sha256"]
                or raw_source.size_bytes != manifest["source"]["size_bytes"]):
            raise IntegrityError("partition source and immutable snapshot identity disagree")
        payload = self.artifacts.read(raw_source)
        import pyarrow as pa
        import pyarrow.parquet as pq
        with pq.ParquetFile(pa.BufferReader(payload)) as pf:
            actual_sizes = [pf.metadata.row_group(g).num_rows for g in range(pf.metadata.num_row_groups)]
            field_names = pf.schema_arrow.names
            if (pf.metadata.num_rows != manifest["source_rows"] or actual_sizes != manifest["row_group_sizes"]
                    or pf.schema_arrow.serialize().to_pybytes().hex() != manifest["schema_arrow"]
                    or schema_identity(pf.schema_arrow) != manifest["schema_version"]):
                raise IntegrityError("manifest counts or schema differ from the complete immutable source")
        rows = []
        for chunk in manifest["chunks"]:
            rows.extend(self.artifacts.read_json(artifact_ref(chunk)))
        expected = [(g, row) for g, size in enumerate(manifest["row_group_sizes"]) for row in range(size)]
        if (len(rows) != manifest["source_rows"] or len(rows) != len(expected)
                or [(r["row_group"], r["row"]) for r in rows] != expected
                or [r["ordinal"] for r in rows] != list(range(len(rows)))):
            raise IntegrityError("partition chunks contain missing, duplicate or reordered physical rows")
        accepted = sum(r["status"] == "decoded" for r in rows)
        rejected = sum(r["status"] == "rejected" for r in rows)
        if (accepted + rejected != len(rows) or accepted != manifest["accepted_rows"]
                or rejected != manifest["rejected_rows"]
                or manifest["status"] != ("quarantined" if rejected else "accepted")):
            raise IntegrityError("partition decode/rejection counts or disposition disagree")
        for row in rows:
            if row["status"] == "rejected":
                self.artifacts.read(artifact_ref(row["raw_arrow_row"]))
            elif list(decode_fields(bytes.fromhex(row["raw_fields"]))) != field_names:
                raise IntegrityError("materialized event omits, adds or reorders declared raw fields")
        return manifest, rows

    def rejections(self, reference: ArtifactRef) -> list[dict]:
        _, rows = self._checked_rows(reference)
        return [r for r in rows if r["status"] == "rejected"]

    def events(self, reference: ArtifactRef) -> Iterator[CanonicalEvent]:
        manifest, rows = self._checked_rows(reference)
        if manifest["status"] != "accepted":
            raise DependencyUnavailable("partition has rejected rows and is quarantined for consumers")
        source, scenario = manifest["source"], LatencyScenario(**manifest["scenario"])
        events = []
        for row in rows:
            address = SourceAddress(source["dataset_id"], source["acquisition_version"],
                                    f"content/{source['sha256']}", source["sha256"],
                                    f"row_group:{row['row_group']}", row["row"],
                                    manifest["schema_version"], source["sha256"])
            event = normalize_mbp(decode_fields(bytes.fromhex(row["raw_fields"])), address,
                                  native=False, scenario=scenario)
            if event.id != row["event_id"]:
                raise IntegrityError("reconstructed event differs from its committed identity")
            events.append(event)
        # Complete validation precedes the first consumer-visible event.
        yield from events
