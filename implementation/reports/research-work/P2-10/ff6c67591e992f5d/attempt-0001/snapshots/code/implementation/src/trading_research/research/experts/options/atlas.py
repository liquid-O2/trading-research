"""Descriptive Level Atlas. Causal inputs only. Selects nothing."""

from __future__ import annotations

from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import Any
import csv
import gzip
import json

import numpy as np

from trading_research.research.contracts.identity import write_json_document
from trading_research.research.experts.options.native import load_minute_bars, peak_rss_bytes
from trading_research.research.method_pack.clocks import et_ns

NQ_TICK = 0.25
OFFSETS = (-2.0, -1.0, 1.0, 2.0)
BINS = (0.1, 0.25, 0.5, 1.0)
JOBS = Path("/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/jobs/evaluation")
NQ_1M = Path("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1m")
QQQ_1M = Path("/workspace/data/quantpad/nasdaq__qqq-etf__ohlcv-1m")


def _s_units(prior_range: float) -> float:
    return prior_range if prior_range > 0 else float("nan")


def nq_session_extremes(day: date) -> dict[str, Any] | None:
    bars = load_minute_bars(NQ_1M, day)
    if bars is None:
        return None
    account = (bars["t_ns"] >= et_ns(day, 18, 0) - 86400 * 1_000_000_000) & (bars["t_ns"] < et_ns(day, 17, 0))
    rth = (bars["t_ns"] >= et_ns(day, 9, 30)) & (bars["t_ns"] < et_ns(day, 16, 0))
    if not np.any(account):
        return None
    h = bars["h"]
    l = bars["l"]
    t = bars["t_ns"]

    def ext(mask: np.ndarray, field: str) -> dict[str, Any]:
        if not np.any(mask):
            return {"price": None, "time_ns": None}
        vals = bars[field][mask]
        times = t[mask]
        i = int(np.nanargmax(vals) if field == "h" else np.nanargmin(vals))
        return {"price": float(vals[i]), "time_ns": int(times[i])}

    prior = date.fromisoformat(day.isoformat())
    return {
        "account_high": ext(account, "h"),
        "account_low": ext(account, "l"),
        "rth_high": ext(rth, "h"),
        "rth_low": ext(rth, "l"),
        "path": bars["path"],
        "sha256": bars["sha256"],
    }


def prior_rth_range(day: date) -> float | None:
    from trading_research.research.experts.options.instruments import previous_regular_session

    prior = previous_regular_session(day)
    if prior is None:
        return None
    ext = nq_session_extremes(prior)
    if ext is None or ext["rth_high"]["price"] is None or ext["rth_low"]["price"] is None:
        return None
    return float(ext["rth_high"]["price"] - ext["rth_low"]["price"])


def map_to_nq(root: str, strike: float, day: date) -> dict[str, Any]:
    if root in ("NQ",):
        return {"nq": strike, "ratio": 1.0, "status": "native"}
    if root not in ("QQQ", "SPY"):
        return {"nq": None, "ratio": None, "status": "cash_index_intraday_unmapped_primary"}
    from trading_research.research.experts.options.instruments import previous_regular_session

    prior = previous_regular_session(day)
    if prior is None:
        return {"nq": None, "ratio": None, "status": "no_prior"}
    nq = load_minute_bars(NQ_1M, prior)
    qfolder = QQQ_1M if root == "QQQ" else Path("/workspace/data/quantpad/nyse-arca__spy-etf__ohlcv-1m")
    eq = load_minute_bars(qfolder, prior)
    if nq is None or eq is None:
        return {"nq": None, "ratio": None, "status": "missing_prior_bars"}
    t0 = et_ns(prior, 9, 30)
    t1 = et_ns(prior, 16, 0)
    mn = (nq["t_ns"] >= t0) & (nq["t_ns"] < t1)
    me = (eq["t_ns"] >= t0) & (eq["t_ns"] < t1)
    # align on equal timestamps
    nq_t = nq["t_ns"][mn]
    nq_c = nq["c"][mn]
    eq_t = eq["t_ns"][me]
    eq_c = eq["c"][me]
    if nq_t.size == 0 or eq_t.size == 0:
        return {"nq": None, "ratio": None, "status": "empty"}
    idx = np.searchsorted(eq_t, nq_t)
    ok = idx < eq_t.size
    idx = idx[ok]
    nq_c = nq_c[ok]
    nq_t = nq_t[ok]
    match = eq_t[idx] == nq_t
    if np.count_nonzero(match) < 20:
        return {"nq": None, "ratio": None, "status": "insufficient_overlap"}
    ratio = float(np.median(nq_c[match] / np.clip(eq_c[idx][match], 1e-9, None)))
    return {"nq": strike * ratio, "ratio": ratio, "status": "ok", "map_known_at_ns": int(t1)}


def control_offset(level_id: str, s: float) -> float:
    idx = int(sha256(level_id.encode()).hexdigest(), 16) % 4
    return OFFSETS[idx] * s


def proximity(level_nq: float, extreme: float, s: float) -> dict[str, Any]:
    ticks = abs(level_nq - extreme) / NQ_TICK
    s_dist = None if not np.isfinite(s) or s == 0 else abs(level_nq - extreme) / s
    return {
        "ticks": ticks,
        "s": s_dist,
        "within_4": ticks <= 4,
        "within_8": ticks <= 8,
        "within_16": ticks <= 16,
    }


def extract_levels(board: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    mapping = {
        "key_gamma": board.get("key_gamma") or {},
        "call_wall": board.get("call_wall") or {},
        "put_wall": board.get("put_wall") or {},
        "gamma_flip": board.get("gamma_flip") or {},
        "max_pain": board.get("max_pain") or {},
    }
    for kind, rec in mapping.items():
        strike = rec.get("strike")
        if strike is None:
            continue
        out.append({"kind": kind, "strike": float(strike), "rank": 1})
    for i, rec in enumerate(board.get("top_gamma") or []):
        out.append({"kind": "top_gamma", "strike": float(rec["strike"]), "rank": i + 1})
    for i, rec in enumerate(board.get("top_vanna") or []):
        out.append({"kind": "top_vanna", "strike": float(rec["strike"]), "rank": i + 1})
    for i, rec in enumerate(board.get("top_vega") or []):
        out.append({"kind": "top_vega", "strike": float(rec["strike"]), "rank": i + 1})
    return out


def load_strategy_refs(day: str) -> list[dict[str, Any]]:
    folder = JOBS / day
    if not folder.is_dir():
        return []
    rows = []
    for path in sorted(folder.glob("*.json.gz")):
        with gzip.open(path) as handle:
            payload = json.load(handle)
        for ep in payload.get("episodes") or []:
            geom = ep.get("geometry") or {}
            entry = geom.get("entry")
            if entry is None:
                continue
            outcomes = payload.get("outcomes") or []
            result = None
            for item in outcomes:
                if item.get("candidate_id") == ep.get("candidate_id"):
                    result = item.get("result")
                    break
            rows.append(
                {
                    "branch": ep.get("branch") or payload.get("branch"),
                    "coverage_id": payload.get("coverage_id"),
                    "decision_at": ep.get("decision_at"),
                    "entry": float(entry),
                    "result": result,
                    "job": str(path),
                }
            )
    return rows


def build_atlas(boards: list[dict[str, Any]], run_root: Path) -> dict[str, Any]:
    run_root.mkdir(parents=True, exist_ok=True)
    rows = []
    alignment = []
    by_root: dict[str, list[dict[str, Any]]] = {}
    for board in boards:
        day = date.fromisoformat(board["day"])
        ext = nq_session_extremes(day)
        s = prior_rth_range(day)
        asof = int(board["asof_ns"])
        if ext is None:
            continue
        for level in extract_levels(board):
            mapped = map_to_nq(board["root"], level["strike"], day)
            level_id = f"{board['root']}:{board['day']}:{level['kind']}:{level['rank']}:{level['strike']}"
            rec = {
                "level_id": level_id,
                "root": board["root"],
                "day": board["day"],
                "year": board["day"][:4],
                "kind": level["kind"],
                "rank": level["rank"],
                "strike": level["strike"],
                "mapped_nq": mapped.get("nq"),
                "map_status": mapped.get("status"),
                "ratio": mapped.get("ratio"),
                "available_at_ns": asof,
                "scenario_label": board.get("scenario_label"),
                "board_n_live": board.get("n_live"),
                "spot": board.get("spot"),
                "implied_move": board.get("implied_move"),
                "extremes_sha256": ext["sha256"],
                "s_prior_rth_range": s,
            }
            if mapped.get("nq") is not None and s:
                nq_px = float(mapped["nq"])
                rec["high"] = proximity(nq_px, ext["account_high"]["price"], s)
                rec["low"] = proximity(nq_px, ext["account_low"]["price"], s)
                rec["rth_high"] = proximity(nq_px, ext["rth_high"]["price"], s) if ext["rth_high"]["price"] else None
                rec["rth_low"] = proximity(nq_px, ext["rth_low"]["price"], s) if ext["rth_low"]["price"] else None
                rec["high_after_available"] = ext["account_high"]["time_ns"] is not None and ext["account_high"]["time_ns"] >= asof
                offset = control_offset(level_id, s)
                rec["control"] = {
                    "offset_s": offset / s,
                    "high": proximity(nq_px + offset, ext["account_high"]["price"], s),
                    "low": proximity(nq_px + offset, ext["account_low"]["price"], s),
                }
            rows.append(rec)
            by_root.setdefault(board["root"], []).append(rec)
        refs = load_strategy_refs(board["day"])
        usable = [row for row in rows if row["day"] == board["day"] and row["root"] == board["root"] and row.get("mapped_nq") is not None]
        if not s:
            continue
        for ref in refs:
            if ref["decision_at"] is None or int(ref["decision_at"]) < asof:
                continue
            for kind in ("key_gamma", "call_wall", "put_wall", "gamma_flip", "max_pain"):
                candidates = [row for row in usable if row["kind"] == kind]
                if not candidates:
                    continue
                nearest = min(candidates, key=lambda row: abs(float(row["mapped_nq"]) - ref["entry"]))
                dist_s = abs(float(nearest["mapped_nq"]) - ref["entry"]) / s
                bucket = "beyond"
                for edge in BINS:
                    if dist_s <= edge:
                        bucket = f"within_{edge}"
                        break
                alignment.append(
                    {
                        "day": board["day"],
                        "root": board["root"],
                        "branch": ref["branch"],
                        "coverage_id": ref["coverage_id"],
                        "dist_s": dist_s,
                        "bucket": bucket,
                        "result": ref["result"],
                        "job": ref["job"],
                        "level_kind": kind,
                        "level_id": nearest["level_id"],
                    }
                )
    summary = _summarize(rows, alignment)
    payload = {
        "schema_version": "research-level-atlas-v1",
        "selects_nothing": True,
        "inventory_sign_assumption": "call_positive_put_negative labelled scenario, not known dealer inventory",
        "rows": rows,
        "strategy_alignment": alignment,
        "summary": summary,
        "limitations": [
            "Cash-index roots have no native intraday spot; mapping is ETF/futures labelled comparison only.",
            "NQ/ES option boards are unsupported because Databento DBN is unparsed.",
            "Strategy alignment uses Phase 1 run-1.0.1 geometry.entry, not a P15-03 refit.",
            "Profile-family atlas cells are specified but not produced in this attempt.",
            "Intraday quotes are scoped DTE/strike feeds, not full-chain.",
        ],
        "peak_rss_bytes": peak_rss_bytes(),
    }
    write_json_document(run_root / "LEVEL_ATLAS.json", payload)
    (run_root / "LEVEL_ATLAS.md").write_text(_markdown(payload), encoding="utf-8")
    for root, items in by_root.items():
        path = run_root / f"LEVEL_ATLAS_{root}.csv"
        if not items:
            continue
        keys = sorted({k for row in items for k in _flatten(row)})
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            for row in items:
                writer.writerow(_flatten(row))
    return payload


def _flatten(row: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out = {}
    for key, value in row.items():
        name = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            out.update(_flatten(value, name))
        else:
            out[name if prefix else key] = value
    return out


def _summarize(rows: list[dict[str, Any]], alignment: list[dict[str, Any]]) -> dict[str, Any]:
    by_kind: dict[str, dict[str, int]] = {}
    for row in rows:
        kind = row["kind"]
        cell = by_kind.setdefault(kind, {"n": 0, "high_within_8": 0, "low_within_8": 0, "control_high_within_8": 0})
        cell["n"] += 1
        high = row.get("high") or {}
        low = row.get("low") or {}
        ctrl = (row.get("control") or {}).get("high") or {}
        cell["high_within_8"] += int(bool(high.get("within_8")))
        cell["low_within_8"] += int(bool(low.get("within_8")))
        cell["control_high_within_8"] += int(bool(ctrl.get("within_8")))
    align_bins: dict[str, int] = {}
    for item in alignment:
        align_bins[item["bucket"]] = align_bins.get(item["bucket"], 0) + 1
    return {"level_kinds": by_kind, "alignment_bins": align_bins, "n_levels": len(rows), "n_alignment": len(alignment)}


def _markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Level Atlas",
        "",
        "Descriptive census. This document selects nothing.",
        "",
        f"Levels counted: {s['n_levels']}. Strategy-alignment rows: {s['n_alignment']}.",
        "",
        "## Extreme proximity by level kind",
        "",
        "| kind | n | high within 8 ticks | low within 8 ticks | control high within 8 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for kind, cell in sorted(s["level_kinds"].items()):
        lines.append(f"| {kind} | {cell['n']} | {cell['high_within_8']} | {cell['low_within_8']} | {cell['control_high_within_8']} |")
    lines += [
        "",
        "## Strategy alignment distance bins",
        "",
        "| bucket | n |",
        "| --- | ---: |",
    ]
    for bucket, n in sorted(s["alignment_bins"].items()):
        lines.append(f"| {bucket} | {n} |")
    lines += ["", "## Limitations", ""]
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines += ["", "Every numeric cell in LEVEL_ATLAS.json points at `extremes_sha256` or a board field from EXPOSURE_BOARDS.json.", ""]
    return "\n".join(lines) + "\n"
