"""Month-chunked NQ MBP-1 extract into retained session tables.

Keeps trades from 18:00–16:00 and every MBP-1 row in 09:30–12:00.
Does not load a month file into memory. Row groups only.
"""

from __future__ import annotations

import json
import resource
import time
from datetime import date, time as dtime, timedelta
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import ZONE
from trading_research.research.phase1_live.compute import TABLE_ROOT
from trading_research.research.phase1_live.slice import load_calendar, slice_dates

MBP1 = Path("/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1")
OUT = TABLE_ROOT / "mbp1"
COLS = ["t", "action", "side", "price", "size", "bid_px", "ask_px", "bid_sz", "ask_sz"]
CPU_SOFT = 180
WALL_SOFT = 330
SCHEMA = pa.schema([
    pa.field("session", pa.string()),
    pa.field("t", pa.int64()),
    pa.field("price", pa.float64()),
    pa.field("size", pa.int32()),
    pa.field("side", pa.int8()),
    pa.field("bid", pa.float64()),
    pa.field("ask", pa.float64()),
    pa.field("bid_sz", pa.int32()),
    pa.field("ask_sz", pa.int32()),
    pa.field("is_trade", pa.bool_()),
])


def _ns(day: date, clock: dtime, offset: int = 0) -> int:
    return local_timestamp(day + timedelta(days=offset), clock, ZONE)


def session_windows(day: date) -> dict:
    return {
        "session": day.isoformat(),
        "globex": _ns(day, dtime(18, 0), -1),
        "rth_end": _ns(day, dtime(16, 0), 0),
        "am0": _ns(day, dtime(9, 30), 0),
        "am1": _ns(day, dtime(12, 0), 0),
    }


def month_chunks(year: int, month: int) -> list[tuple[date, date]]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    chunks = []
    cur = start
    while cur <= end:
        last = min(cur + timedelta(days=6), end)
        chunks.append((cur, last))
        cur = last + timedelta(days=1)
    return chunks


def _decode(col):
    chunk = col.combine_chunks()
    if pa.types.is_dictionary(chunk.type):
        chunk = chunk.dictionary_decode()
    return np.asarray(chunk.to_numpy(zero_copy_only=False))


def _side_code(side) -> np.ndarray:
    out = np.zeros(side.shape[0], dtype=np.int8)
    s = side.astype(str)
    out[np.isin(s, ("A", "a"))] = 1
    out[np.isin(s, ("B", "b"))] = -1
    return out


def _files_for_span(start: date, end: date) -> list[Path]:
    months = set()
    d = start - timedelta(days=1)
    while d <= end:
        months.add((d.year, d.month))
        d += timedelta(days=1)
    paths = []
    for y, m in sorted(months):
        p = MBP1 / f"{y:04d}-{m:02d}.parquet"
        if p.is_file():
            paths.append(p)
    return paths


def chunk_id(start: date, end: date) -> str:
    return f"{start.isoformat()}_{end.isoformat()}"


def chunk_paths(start: date, end: date) -> tuple[Path, Path]:
    name = chunk_id(start, end)
    return OUT / f"{name}.parquet", OUT / f"{name}.json"


def extract_chunk(start: date, end: date, *, calendar=None) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    data_path, meta_path = chunk_paths(start, end)
    if meta_path.is_file() and data_path.is_file():
        meta = json.loads(meta_path.read_text())
        if meta.get("status") == "complete":
            return meta
    calendar = calendar or load_calendar()
    f_dates = slice_dates(calendar, "F")
    days = [d for d in f_dates if start <= d <= end]
    if not days:
        meta = {"chunk": chunk_id(start, end), "status": "complete", "n_rows": 0, "n_sessions": 0, "note": "no F dates"}
        meta_path.write_text(json.dumps(meta))
        return meta
    wins = [session_windows(d) for d in days]
    globex0 = min(w["globex"] for w in wins)
    rth1 = max(w["rth_end"] for w in wins)
    am0 = min(w["am0"] for w in wins)
    am1 = max(w["am1"] for w in wins)
    sess = np.array([w["session"] for w in wins])
    g0 = np.array([w["globex"] for w in wins], dtype=np.int64)
    r1 = np.array([w["rth_end"] for w in wins], dtype=np.int64)
    a0 = np.array([w["am0"] for w in wins], dtype=np.int64)
    a1 = np.array([w["am1"] for w in wins], dtype=np.int64)
    t0 = time.perf_counter()
    cpu0 = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    parts = []
    n_rows = 0
    files = _files_for_span(start, end)
    try:
        for path in files:
            pf = pq.ParquetFile(path, memory_map=False)  # parquet already; not DBN
            t_idx = pf.schema_arrow.names.index("t")
            for i in range(pf.num_row_groups):
                wall = time.perf_counter() - t0
                cpu = resource.getrusage(resource.RUSAGE_SELF).ru_utime - cpu0
                if wall > WALL_SOFT or cpu > CPU_SOFT:
                    meta = {
                        "chunk": chunk_id(start, end),
                        "status": "budget",
                        "n_rows": n_rows,
                        "n_sessions": len(days),
                        "wall_s": wall,
                        "cpu_s": cpu,
                        "split": True,
                    }
                    meta_path.write_text(json.dumps(meta))
                    if parts:
                        _write_parts(data_path, parts)
                    return meta
                st = pf.metadata.row_group(i).column(t_idx).statistics
                if st is not None and (st.max < globex0 or st.min >= rth1):
                    continue
                tbl = pf.read_row_group(i, columns=COLS)
                t = tbl.column("t").to_numpy()
                act = _decode(tbl.column("action")).astype(str)
                is_trade = act == "T"
                idx = np.searchsorted(g0, t, side="right") - 1
                valid = (idx >= 0) & (idx < len(days))
                idxc = np.clip(idx, 0, len(days) - 1)
                in_globex = valid & (t >= g0[idxc]) & (t < r1[idxc])
                in_am = in_globex & (t >= a0[idxc]) & (t < a1[idxc])
                keep = in_globex & (is_trade | in_am)
                if not np.any(keep):
                    continue
                side = _side_code(_decode(tbl.column("side"))[keep])
                part = pa.table({
                    "session": sess[idxc[keep]],
                    "t": t[keep],
                    "price": tbl.column("price").to_numpy()[keep].astype(np.float64),
                    "size": tbl.column("size").to_numpy()[keep].astype(np.int32),
                    "side": side,
                    "bid": tbl.column("bid_px").to_numpy()[keep].astype(np.float64),
                    "ask": tbl.column("ask_px").to_numpy()[keep].astype(np.float64),
                    "bid_sz": tbl.column("bid_sz").to_numpy()[keep].astype(np.int32),
                    "ask_sz": tbl.column("ask_sz").to_numpy()[keep].astype(np.int32),
                    "is_trade": is_trade[keep],
                }, schema=SCHEMA)
                n_rows += part.num_rows
                parts.append(part)
        _write_parts(data_path, parts)
        meta = {
            "chunk": chunk_id(start, end),
            "status": "complete",
            "n_rows": n_rows,
            "n_sessions": len(days),
            "sessions": [d.isoformat() for d in days],
            "wall_s": time.perf_counter() - t0,
            "cpu_s": resource.getrusage(resource.RUSAGE_SELF).ru_utime - cpu0,
            "files": [str(p) for p in files],
        }
        meta_path.write_text(json.dumps(meta))
        print(f"mbp1 chunk {meta['chunk']} rows={n_rows} wall={meta['wall_s']:.1f} cpu={meta['cpu_s']:.1f}", flush=True)
        return meta
    except Exception as exc:
        meta = {
            "chunk": chunk_id(start, end),
            "status": "failed",
            "n_rows": n_rows,
            "error": f"{type(exc).__name__}: {exc}",
            "wall_s": time.perf_counter() - t0,
        }
        meta_path.write_text(json.dumps(meta))
        raise


def _write_parts(path: Path, parts: list):
    if not parts:
        pq.write_table(pa.table({n: [] for n in SCHEMA.names}, schema=SCHEMA), path, compression="zstd")
        return
    table = pa.concat_tables(parts)
    pq.write_table(table, path, compression="zstd")


def extract_month(year: int, month: int) -> list[dict]:
    out = []
    for start, end in month_chunks(year, month):
        meta = extract_chunk(start, end)
        out.append(meta)
        if meta.get("status") == "budget":
            # split the remaining days of this week into single days
            days = [date.fromisoformat(s) for s in _f_days(start, end)]
            done_n = meta.get("n_rows") or 0
            print(f"budget on {start}..{end} after {done_n} rows; splitting to days", flush=True)
            for d in days:
                out.append(extract_chunk(d, d))
    return out


def _f_days(start, end):
    calendar = load_calendar()
    return [d.isoformat() for d in slice_dates(calendar, "F") if start <= d <= end]


def incomplete_spans(slice_id: str = "F") -> list[tuple[date, date]]:
    calendar = load_calendar()
    dates = list(slice_dates(calendar, slice_id))
    months = sorted({(d.year, d.month) for d in dates})
    missing = []
    for y, m in months:
        for start, end in month_chunks(y, m):
            _, meta_path = chunk_paths(start, end)
            if meta_path.is_file():
                body = json.loads(meta_path.read_text())
                if body.get("status") == "complete":
                    continue
            missing.append((start, end))
    return missing


def _extract_span(pair):
    start, end = pair
    return extract_chunk(start, end)


def extract_F(workers: int = 8) -> list[dict]:
    missing = incomplete_spans("F")
    if not missing:
        print("mbp1 F extract complete", flush=True)
        return []
    print(f"mbp1 parallel extract n_chunks={len(missing)} workers={workers}", flush=True)
    from concurrent.futures import ProcessPoolExecutor, as_completed
    out = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_extract_span, pair) for pair in missing]
        for fut in as_completed(futs):
            meta = fut.result()
            out.append(meta)
            print(f"done {meta.get('chunk')} {meta.get('status')} rows={meta.get('n_rows')}", flush=True)
    return out


def list_complete_chunks() -> list[Path]:
    if not OUT.is_dir():
        return []
    paths = []
    for meta in sorted(OUT.glob("*.json")):
        body = json.loads(meta.read_text())
        parquet = meta.with_suffix(".parquet")
        if body.get("status") == "complete" and parquet.is_file():
            paths.append(parquet)
    return paths


def list_extracted_sessions() -> list[str]:
    dates = []
    if not OUT.is_dir():
        return dates
    for meta in sorted(OUT.glob("*.json")):
        body = json.loads(meta.read_text())
        if body.get("status") == "complete":
            dates.extend(body.get("sessions") or [])
    return sorted(set(dates))
