"""Read-only, bounded views of the canonical acquired NQ MBP-1 tape.

Only T records are executions.  File order never resolves equal exchange
timestamps, and observed bounds never certify that an exchange feed is complete.
Exports go outside the acquired root and retain the source file and physical row.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Iterable, Iterator, Mapping, Sequence

from .adapters import (
    MBP1_RELATIVE, NS, _checked_ns, _subtract, iter_source_rows,
    normalize_mbp1_row, ownership_manifest,
)
from .clocks import ns_to_et

DATASET = MBP1_RELATIVE.as_posix()
VIEWS = ("trades", "bbo", "ohlcv-1s", "ohlcv-1m")


class TapeError(ValueError):
    """The requested tape cannot be assembled without unresolved evidence."""


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))


def _bounds(start_ns: int, end_ns: int) -> tuple[int, int]:
    start_ns, end_ns = _checked_ns(start_ns), _checked_ns(end_ns)
    if end_ns <= start_ns:
        raise ValueError("a positive half-open UTC interval is required")
    return start_ns, end_ns


def _source_signature(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {"path": str(path), "size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def plan_window(
    data_root: Path | str, start_ns: int, end_ns: int,
    *, ownership: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Clip frozen, disjoint ownership to a request; retain every unowned span."""
    start_ns, end_ns = _bounds(start_ns, end_ns)
    root = Path(data_root).resolve()
    manifest = ownership_manifest(root) if ownership is None else dict(ownership)
    spans: list[dict[str, Any]] = []
    for original in manifest.get("owned_spans", []):
        a, b = max(start_ns, int(original["start_ns"])), min(end_ns, int(original["end_ns"]))
        if b <= a:
            continue
        path = Path(original["path"]).resolve()
        if not path.is_relative_to(root / MBP1_RELATIVE):
            raise TapeError("ownership path lies outside the requested NQ MBP-1 dataset")
        if original.get("status", "owned") not in {"owned", "valid", "ok"}:
            raise TapeError("an invalid ownership span cannot supply a tape")
        spans.append({**original, "path": str(path), "start_ns": a, "end_ns": b})
    spans.sort(key=lambda x: (x["start_ns"], x["end_ns"], x["path"]))
    for left, right in zip(spans, spans[1:]):
        if left["end_ns"] > right["start_ns"]:
            raise TapeError("ownership spans overlap; refusing to double count")
    holes = []
    for hole in manifest.get("holes", []):
        a, b = hole.get("start_ns"), hole.get("end_ns")
        if a is None or b is None or (int(a) < end_ns and int(b) > start_ns):
            holes.append(hole)
    uncovered = _subtract((start_ns, end_ns), [(s["start_ns"], s["end_ns"]) for s in spans])
    frozen = {"dataset_id": DATASET, "owned_spans": spans, "holes": holes}
    return {
        **frozen, "data_root": str(root), "start_ns": start_ns, "end_ns": end_ns,
        "ownership_sha256": hashlib.sha256(_json(frozen).encode()).hexdigest(),
        "unowned_intervals": [{"start_ns": a, "end_ns": b} for a, b in uncovered],
        "coverage_basis": "canonical file ownership and observed bounds",
        "market_coverage_complete": None,
        "coverage_note": "An unowned interval may be a market closure or missing data; bounds alone do not decide this.",
        "sources": [_source_signature(Path(p)) for p in sorted({s["path"] for s in spans})],
    }


def _window_rows(path: Path, start_ns: int, end_ns: int, *, trades_only: bool) -> Iterator[tuple[int, dict[str, Any]]]:
    """Prune Parquet row groups and filter Arrow batches before Python decoding."""
    if path.suffix.lower() != ".parquet":
        for index, row in enumerate(iter_source_rows(path)):
            at = row.get("t", row.get("ts_event"))
            if at is not None and start_ns <= int(at) < end_ns:
                if not trades_only or str(row.get("action", "")).upper() == "T":
                    yield index, row
        return
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    parquet = pq.ParquetFile(path)
    field_name = "t" if "t" in parquet.schema_arrow.names else "ts_event"
    if field_name not in parquet.schema_arrow.names:
        raise TapeError(f"missing event timestamp in {path}")
    timestamp_index = parquet.schema_arrow.names.index(field_name)
    native_type = parquet.schema_arrow.field(field_name).type
    factor = {"s": NS, "ms": 1_000_000, "us": 1_000, "ns": 1}.get(getattr(native_type, "unit", "ns"))
    if factor is None or (pa.types.is_timestamp(native_type) and not native_type.tz):
        raise TapeError("Arrow event timestamps require an explicit zone and supported unit")
    row_offset = 0
    for group in range(parquet.num_row_groups):
        group_rows = parquet.metadata.row_group(group).num_rows
        statistics = parquet.metadata.row_group(group).column(timestamp_index).statistics
        if statistics is not None and statistics.has_min_max:
            lo, hi = statistics.min_raw, statistics.max_raw
            if int(hi) * factor < start_ns or int(lo) * factor >= end_ns:
                row_offset += group_rows
                continue
        batch_offset = row_offset
        for batch in parquet.iter_batches(batch_size=65_536, row_groups=[group]):
            times = batch.column(timestamp_index)
            if pa.types.is_timestamp(native_type):
                times = times.cast(pa.timestamp("ns", tz=native_type.tz)).cast(pa.int64())
            mask = pc.and_(pc.greater_equal(times, start_ns), pc.less(times, end_ns))
            if trades_only:
                actions = pc.cast(batch.column(batch.schema.get_field_index("action")), pa.string())
                mask = pc.and_(mask, pc.equal(actions, "T"))
            indices = pc.indices_nonzero(mask).to_pylist()
            selected = batch.filter(mask)
            for index, typed_field in enumerate(selected.schema):
                if pa.types.is_timestamp(typed_field.type):
                    column = selected.column(index).cast(pa.timestamp("ns", tz=typed_field.type.tz)).cast(pa.int64())
                    selected = selected.set_column(index, typed_field.name, column)
            for offset, row in zip(indices, selected.to_pylist()):
                yield batch_offset + offset, row
            batch_offset += batch.num_rows
        row_offset += group_rows


def iter_mbp1_window(
    plan: Mapping[str, Any], *, trades_only: bool = False,
    instrument_id: int | str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield canonical normalized events, preserving duplicates and tie batches."""
    previous: int | None = None
    for span in plan["owned_spans"]:
        path = Path(span["path"])
        for index, raw in _window_rows(path, span["start_ns"], span["end_ns"], trades_only=trades_only):
            if instrument_id is not None and str(raw.get("instrument_id")) != str(instrument_id):
                continue
            row = normalize_mbp1_row(raw, dataset_id=DATASET, source_file=str(path), source_row=index)
            at = row["event_ns"]
            if previous is not None and at < previous:
                raise TapeError(f"exchange timestamps are out of order at {path}:{index}; no ordering was invented")
            previous = at
            if row["instrument_id"] is None:
                raise TapeError(f"missing native instrument identity at {path}:{index}")
            row["t"] = at
            yield row


def trade_view(row: Mapping[str, Any]) -> dict[str, Any]:
    if row["action"] != "T":
        raise ValueError("only T events can supply a trade view")
    return dict(row)


def bbo_view(row: Mapping[str, Any]) -> dict[str, Any]:
    fields = ("event_id", "dataset_id", "source_file", "source_row", "instrument_id", "raw_symbol",
              "event_ns", "t", "known_at", "ts_recv", "action", "side", "resting_side", "bid", "ask", "bid_size", "ask_size",
              "flags", "exchange_sequence", "ordering_basis")
    return {**{key: row.get(key) for key in fields}, "book_depth": 1, "observation_kind": "source_bbo"}


def _endpoint(rows: Sequence[tuple[Decimal, int | None]], *, last: bool) -> Decimal | None:
    prices = {price for price, _ in rows}
    if len(prices) == 1:
        return next(iter(prices))
    sequence = [seq for _, seq in rows]
    if any(seq is None for seq in sequence) or len(set(sequence)) != len(sequence):
        return None
    ordered = sorted(rows, key=lambda row: row[1])
    return ordered[-1 if last else 0][0]


@dataclass
class _Bar:
    instrument_id: Any
    start_ns: int
    end_ns: int
    first_ns: int | None = None
    last_ns: int | None = None
    first: list = field(default_factory=list)
    last: list = field(default_factory=list)
    high: Decimal | None = None
    low: Decimal | None = None
    volume: int = 0
    buy: int = 0
    sell: int = 0
    unknown: int = 0
    count: int = 0
    known_at: int = 0
    invalid: int = 0
    source_ranges: dict = field(default_factory=dict)

    def add(self, row: Mapping[str, Any]) -> None:
        at, price, size = row["event_ns"], row["price"], row["size"]
        self.count += 1
        self.known_at = max(self.known_at, row["known_at"])
        path, physical_row = row["source_file"], row["source_row"]
        old = self.source_ranges.setdefault(path, [physical_row, physical_row, 0])
        old[0], old[1], old[2] = min(old[0], physical_row), max(old[1], physical_row), old[2] + 1
        if price is None or not price.is_finite() or size is None or size < 0:
            self.invalid += 1
            return
        sample = (price, row.get("exchange_sequence"))
        if self.first_ns is None:
            self.first_ns, self.first = at, [sample]
        elif at == self.first_ns:
            self.first.append(sample)
        if self.last_ns != at:
            self.last_ns, self.last = at, [sample]
        else:
            self.last.append(sample)
        self.high = price if self.high is None else max(self.high, price)
        self.low = price if self.low is None else min(self.low, price)
        self.volume += size
        if row["aggressor"] == "buy":
            self.buy += size
        elif row["aggressor"] == "sell":
            self.sell += size
        else:
            self.unknown += size

    def record(self, request_start: int, request_end: int) -> dict[str, Any]:
        opening = _endpoint(self.first, last=False) if self.first else None
        closing = _endpoint(self.last, last=True) if self.last else None
        valid = self.invalid == 0
        return {
            "instrument_id": self.instrument_id, "t": self.start_ns // 1_000_000,
            "start_ns": self.start_ns, "end_ns": self.end_ns,
            "start_et": ns_to_et(self.start_ns).isoformat(), "end_et": ns_to_et(self.end_ns).isoformat(),
            "O": opening if valid else None, "H": self.high if valid else None,
            "L": self.low if valid else None, "C": closing if valid else None,
            "V": self.volume if valid else None, "buy_volume": self.buy if valid else None,
            "sell_volume": self.sell if valid else None, "unknown_volume": self.unknown if valid else None,
            "delta_known": self.buy - self.sell,
            "delta": self.buy - self.sell if valid and self.unknown == 0 else None,
            "trade_count": self.count, "invalid_trade_count": self.invalid,
            "known_at": max(self.end_ns, self.known_at),
            "first_trade_ns": self.first_ns, "last_trade_ns": self.last_ns,
            "open_order_known": opening is not None, "close_order_known": closing is not None,
            "full_bar_requested": request_start <= self.start_ns and self.end_ns <= request_end,
            "complete": None, "coverage_basis": "observed canonical MBP-1 T records",
            "aggregation_timestamp": "event_ns", "vendor_bar_equivalence": "not_asserted",
            "source_row_ranges": [
                {"path": path, "first_row": bounds[0], "last_row": bounds[1], "trade_rows": bounds[2]}
                for path, bounds in sorted(self.source_ranges.items())
            ],
        }


class TradeBars:
    """Stream 1-second or 1-minute trade bars without mixing native contracts."""

    def __init__(self, seconds: int, start_ns: int, end_ns: int):
        if seconds not in {1, 60}:
            raise ValueError("supported source views are 1-second and 1-minute bars")
        self.duration = seconds * NS
        self.start_ns, self.end_ns = _bounds(start_ns, end_ns)
        self.bars: dict[Any, _Bar] = {}
        self.bucket: int | None = None

    def add(self, row: Mapping[str, Any]) -> list[dict[str, Any]]:
        if row["action"] != "T":
            return []
        bucket = row["event_ns"] // self.duration * self.duration
        finished = []
        if self.bucket is not None and bucket < self.bucket:
            raise TapeError("bars require chronological event batches")
        if self.bucket is not None and bucket != self.bucket:
            finished = self.finish()
        self.bucket = bucket
        key = row["instrument_id"]
        bar = self.bars.setdefault(key, _Bar(key, bucket, bucket + self.duration))
        bar.add(row)
        return finished

    def finish(self) -> list[dict[str, Any]]:
        result = [bar.record(self.start_ns, self.end_ns) for _, bar in sorted(self.bars.items(), key=lambda x: str(x[0]))]
        self.bars = {}
        return result


def export_views(
    data_root: Path | str, output_root: Path | str, start_ns: int, end_ns: int,
    *, views: Sequence[str] = VIEWS, instrument_id: int | str | None = None,
    ownership: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an immutable JSONL bundle outside raw data, with hashes/provenance."""
    root, out = Path(data_root).resolve(), Path(output_root).resolve()
    if out == root or out.is_relative_to(root):
        raise ValueError("derived outputs must be outside the read-only acquired data root")
    selected = tuple(dict.fromkeys(views))
    if not selected or any(view not in VIEWS for view in selected):
        raise ValueError(f"views must be selected from {VIEWS}")
    plan = plan_window(root, start_ns, end_ns, ownership=ownership)
    if not plan["owned_spans"]:
        raise TapeError("no canonical MBP-1 records own the requested window")
    if any("DATA_OVERLAP" in str(hole.get("reason")) for hole in plan["holes"]):
        raise TapeError("the requested ownership has an unresolved source overlap")
    out.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="mbp1-", dir=out))
    counts = {view: 0 for view in selected}
    digests = {view: hashlib.sha256() for view in selected}
    writers = {view: (run / f"{view}.jsonl").open("x") for view in selected}
    bars = {view: TradeBars(1 if view == "ohlcv-1s" else 60, start_ns, end_ns)
            for view in selected if view.startswith("ohlcv-")}

    def write(view: str, row: Mapping[str, Any]):
        line = _json(row) + "\n"
        writers[view].write(line)
        digests[view].update(line.encode())
        counts[view] += 1

    try:
        for row in iter_mbp1_window(plan, trades_only="bbo" not in selected, instrument_id=instrument_id):
            if "bbo" in writers:
                write("bbo", bbo_view(row))
            if row["action"] == "T":
                if "trades" in writers:
                    write("trades", trade_view(row))
                for view, accumulator in bars.items():
                    for record in accumulator.add(row):
                        write(view, record)
        for view, accumulator in bars.items():
            for record in accumulator.finish():
                write(view, record)
        for writer in writers.values():
            writer.close()
        after = [_source_signature(Path(source["path"])) for source in plan["sources"]]
        if after != plan["sources"]:
            raise TapeError("source file size or mtime changed during the read; export cannot be certified")
        result = {
            "status": "complete", "view_version": "canonical-mbp1-v1", "output_dir": str(run),
            "plan": plan, "instrument_filter": instrument_id, "raw_source_signatures_unchanged": True,
            "artifacts": {view: {"path": str(run / f"{view}.jsonl"), "rows": counts[view],
                                 "sha256": digests[view].hexdigest()} for view in selected},
            "conventions": {
                "executions": "T only; B buy, A sell, N unknown; no event-value deduplication",
                "prices": "native price units, exact decimal text in JSON",
                "ordering": "equal timestamps remain unresolved unless source exchange sequence proves order",
                "bars": "half-open clock buckets, one native instrument per row; empty buckets omitted",
                "bar_timestamp_basis": "stored exchange event time; vendor receive-time aggregates can differ",
                "coverage": "computed observed values retained; completeness requires separate coverage evidence",
                "bbo": "source depth-one fields retained with action/side; no additional depth or order identities reconstructed",
            },
        }
        (run / "manifest.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
        return result
    except BaseException as exc:
        for writer in writers.values():
            writer.close()
        (run / "FAILED.json").write_text(_json({"status": "failed", "reason": str(exc), "plan": plan}) + "\n")
        raise
