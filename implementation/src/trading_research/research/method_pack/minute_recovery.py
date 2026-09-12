"""Recover explicitly identified NQ minute-format gaps from native second bars."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Iterable, Mapping

from .adapters import NS
from .mbp1_views import TapeError, _json, _source_signature

SECOND_DATASET = "quantpad/cme__nq-continuous-futures__ohlcv-1s"
MINUTE_DATASET = "quantpad/cme__nq-continuous-futures__ohlcv-1m"


def gap_requests(document: Any) -> list[dict[str, Any]]:
    """Accept the audit's explicit ns schema or an explicit native-ms key list."""
    rows = document.get("missing_keys") if isinstance(document, Mapping) else document
    if not isinstance(rows, list):
        raise ValueError("gap manifest must contain a key list or the audit missing_keys array")
    result = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("each missing key must be an object")
        if "minute_start_ns" in row:
            at = row["minute_start_ns"]
            if type(at) is not int or at % (60 * NS):
                raise ValueError("minute_start_ns must be an exact UTC-ns minute boundary")
            native_ms = at // 1_000_000
            if "t" in row and row["t"] != native_ms:
                raise ValueError("conflicting millisecond and nanosecond gap keys")
        else:
            native_ms = row.get("t")
        result.append({"t": native_ms, "instrument_id": row.get("instrument_id")})
    return result


def _selected_rows(paths: Iterable[Path], times: set[int], *, values: bool):
    """Keep exact physical row references while filtering selected minute keys."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    wanted = pa.array(sorted(times), type=pa.int64())
    columns = ["t", "instrument_id"] + (["o", "h", "l", "c", "v"] if values else [])
    for path in paths:
        parquet = pq.ParquetFile(path)
        field_index = parquet.schema_arrow.names.index("t")
        offset = 0
        for group in range(parquet.num_row_groups):
            n = parquet.metadata.row_group(group).num_rows
            stats = parquet.metadata.row_group(group).column(field_index).statistics
            if stats is not None and stats.has_min_max:
                lo = int(stats.min_raw) // 60_000 * 60_000
                hi = int(stats.max_raw) // 60_000 * 60_000
                if not any(lo <= t <= hi for t in times):
                    offset += n
                    continue
            batch_offset = offset
            for batch in parquet.iter_batches(batch_size=65_536, row_groups=[group], columns=columns):
                bucket = pc.multiply(pc.divide(batch.column(0), 60_000), 60_000)
                mask = pc.is_in(bucket, value_set=wanted)
                indices = pc.indices_nonzero(mask).to_pylist()
                for index, row in zip(indices, batch.filter(mask).to_pylist()):
                    yield path, batch_offset + index, row
                batch_offset += batch.num_rows
            offset += n


def recover_minutes(
    data_root: Path | str, output_root: Path | str,
    requested: Iterable[Mapping[str, Any]], *, gap_manifest: str | None = None,
) -> dict[str, Any]:
    """Rebuild missing native-instrument minute keys, with no acquired writes.

    Requests use ``t`` (UTC milliseconds) and ``instrument_id``.  Native second
    bars retain the provider's aggregation clock, avoiding an implicit switch to
    the exchange-event clock used by the MBP-1-derived view.
    """
    root, output = Path(data_root).resolve(), Path(output_root).resolve()
    if output == root or output.is_relative_to(root):
        raise ValueError("recovery outputs must be outside the acquired data root")
    keys = set()
    for row in requested:
        t, instrument = row.get("t"), row.get("instrument_id")
        if type(t) is not int or t % 60_000 or instrument is None or isinstance(instrument, bool):
            raise ValueError("each gap requires an aligned integer millisecond t and native instrument_id")
        keys.add((t, str(instrument)))
    if not keys:
        raise ValueError("the gap manifest contains no missing minute keys")
    times = {key[0] for key in keys}
    seconds = sorted((root / SECOND_DATASET).glob("*.parquet"))
    minutes = sorted((root / MINUTE_DATASET).glob("*.parquet"))
    if not seconds:
        raise TapeError("native NQ one-second source files are absent")
    paths = seconds + minutes
    before = [_source_signature(path) for path in paths]
    already_present = set()
    for _, _, row in _selected_rows(minutes, times, values=False):
        key = (int(row["t"]), str(row["instrument_id"]))
        if key in keys:
            already_present.add(key)
    pending = keys - already_present
    bars: dict[tuple[int, str], dict[str, Any]] = {}
    seen_seconds = set()
    for path, source_row, row in _selected_rows(seconds, {t for t, _ in pending}, values=True):
        at = int(row["t"])
        key = (at // 60_000 * 60_000, str(row["instrument_id"]))
        if key not in pending:
            continue
        if at % 1_000:
            raise TapeError("native one-second source t is not second-aligned")
        second_key = (at, str(row["instrument_id"]))
        if second_key in seen_seconds:
            raise TapeError(f"duplicate native second bar {second_key}; no volume deduplication was guessed")
        seen_seconds.add(second_key)
        try:
            values = {field: Decimal(str(row[field.lower()])) for field in "OHLCV"}
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise TapeError(f"missing or non-numeric native second-bar values at {path}:{source_row}") from exc
        if any(not value.is_finite() for value in values.values()) or values["V"] < 0:
            raise TapeError(f"invalid native second-bar values at {path}:{source_row}")
        if values["L"] > min(values["O"], values["C"]) or values["H"] < max(values["O"], values["C"]) or values["L"] > values["H"]:
            raise TapeError(f"invalid native second OHLC envelope at {path}:{source_row}")
        bar = bars.setdefault(key, {
            "instrument_id": row["instrument_id"], "t": key[0], "start_ns": key[0] * 1_000_000,
            "end_ns": (key[0] + 60_000) * 1_000_000, "first_t": at, "last_t": at,
            "O": values["O"], "H": values["H"], "L": values["L"], "C": values["C"],
            "V": Decimal(0), "observed_second_count": 0, "source_row_ranges": {},
        })
        if at < bar["first_t"]:
            bar["first_t"], bar["O"] = at, values["O"]
        if at >= bar["last_t"]:
            bar["last_t"], bar["C"] = at, values["C"]
        bar["H"], bar["L"] = max(bar["H"], values["H"]), min(bar["L"], values["L"])
        bar["V"] += values["V"]
        bar["observed_second_count"] += 1
        reference = bar["source_row_ranges"].setdefault(str(path), {"path": str(path), "first_row": source_row, "last_row": source_row, "rows": 0})
        reference["first_row"], reference["last_row"] = min(reference["first_row"], source_row), max(reference["last_row"], source_row)
        reference["rows"] += 1
    output.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="nq-minutes-", dir=output))
    artifact = run / "ohlcv-1m.jsonl"
    digest = hashlib.sha256()
    with artifact.open("x") as handle:
        for key, bar in sorted(bars.items()):
            bar["source_row_ranges"] = list(bar["source_row_ranges"].values())
            bar.update({"known_at": bar["end_ns"], "source_dataset": SECOND_DATASET,
                        "derivation": "clock minute OHLCV from native one-second bars",
                        "aggregation_timestamp": "native source bar-start timestamp",
                        "complete": None, "coverage_basis": "observed native one-second rows; no empty seconds invented"})
            line = _json(bar) + "\n"
            handle.write(line)
            digest.update(line.encode())
    if before != [_source_signature(path) for path in paths]:
        (run / "FAILED.json").write_text(_json({"reason": "raw source signature changed during read"}) + "\n")
        raise TapeError("source size or mtime changed during recovery")
    result = {
        "status": "complete", "output_dir": str(run), "gap_manifest": gap_manifest,
        "requested_keys": len(keys), "already_present_keys": len(already_present), "recovered_keys": len(bars),
        "unresolved_keys": [{"t": t, "instrument_id": instrument} for t, instrument in sorted(pending - bars.keys())],
        "raw_source_signatures_unchanged": True, "sources": before,
        "artifact": {"path": str(artifact), "rows": len(bars), "sha256": digest.hexdigest()},
        "conventions": "Use native minute bars first and only these absent keys as fallback. Preserve native instrument IDs. This closes a format gap without asserting event-level feed continuity.",
    }
    (run / "manifest.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result
