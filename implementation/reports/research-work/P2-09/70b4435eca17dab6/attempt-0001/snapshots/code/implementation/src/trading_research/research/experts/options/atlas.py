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

def write_json_document(path: Path, document: object, *, compact: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def default(obj: object) -> object:
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    text = json.dumps(
        document,
        indent=None if compact else 2,
        sort_keys=True,
        default=default,
        separators=(",", ":") if compact else None,
    )
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text + "\n", encoding="utf-8")
    tmp.replace(path)
from trading_research.research.experts.options.instruments import REQUIRED_ROOTS
from trading_research.research.experts.options.native import load_minute_bars, peak_rss_bytes
from trading_research.research.method_pack.clocks import et_ns

NQ_TICK = 0.25
OFFSETS = (-2.0, -1.0, 1.0, 2.0)
BINS = (0.1, 0.25, 0.5, 1.0)
JOBS = Path("/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/jobs/evaluation")
CENSUS_ROOT = Path("/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7")
P15_03_RECEIPT = Path("/workspace/implementation/reports/research-work/P15-03/b957ec04d76e9c71/attempt-0001/TASK_RECEIPT.json")
NQ_1M = Path("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1m")
QQQ_1M = Path("/workspace/data/quantpad/nasdaq__qqq-etf__ohlcv-1m")
ES_1M = Path("/workspace/data/quantpad/cme__es-continuous-futures__ohlcv-1m")
SUPERSEDED_20DATE = Path(__file__).resolve().parents[5] / "reports/research-work/phase2-early/P2-10-20date-superseded"
HEADLINE_ROOTS = ("QQQ", "SPY")
DEGENERATE_ROOTS = ("NQ", "ES")
DEGENERATE_LABEL = "degenerate board (median n_live 2 / 7)"
DEGENERATE_NOTE = (
    "NQ and ES rows are not evidence for the futures-option levels thesis until a BBO or MBP "
    "schema for those roots is owned. Owned NQ/ES option DBN has no BBO; only ohlcv-1m last-trade "
    "midpoints pass the 60 s age rule, so boards collapse to a median of 2 (NQ) and 7 (ES) live contracts."
)


def _s_units(prior_range: float) -> float:
    return prior_range if prior_range > 0 else float("nan")


def census_status() -> dict[str, Any]:
    complete = CENSUS_ROOT / "RUN_COMPLETE.json"
    manifest = CENSUS_ROOT / "MANIFEST.json"
    dates = []
    if manifest.is_file():
        dates = list(json.loads(manifest.read_text()).get("dates") or [])
    preview = preview_dates(dates) if dates else []
    return {
        "run_complete": complete.is_file(),
        "census_root": str(CENSUS_ROOT),
        "n_dates": len(dates),
        "dates": dates,
        "preview_dates": preview,
        "provisional": not complete.is_file(),
    }


def preview_dates(dates: list[str]) -> list[str]:
    if not dates:
        return []
    if len(dates) <= 40:
        return list(dates)
    idx = [round(i * (len(dates) - 1) / 39) for i in range(40)]
    return [dates[i] for i in idx]


def market_view_trade_prices(day: date) -> dict[str, Any] | None:
    """P15-02 NativeMarketView trade prints for the account day (trades-only load)."""
    import pyarrow as pa

    from trading_research.research.method_pack.event_cache import ownership
    from trading_research.research.method_pack.mbp1_views import plan_window
    from trading_research.research.rule_discovery.native import (
        DATA_ROOT,
        account_day_window,
        contract_selection,
        load_span_arrow,
        stitch_monthly_seams,
        memoized_file_digest,
    )

    start_ns, end_ns = account_day_window(day)
    selection = contract_selection(day)
    instrument_id = selection["archive"]["instrument_id"]
    plan = plan_window(DATA_ROOT, start_ns, end_ns, ownership=ownership(str(DATA_ROOT)))
    stitch_monthly_seams(plan)
    t_parts: list[np.ndarray] = []
    p_parts: list[np.ndarray] = []
    sources: list[str] = []
    for span in plan.get("owned_spans") or []:
        path = Path(span["path"])
        table, _offsets = load_span_arrow(
            path,
            int(span["start_ns"]),
            int(span["end_ns"]),
            instrument_id=instrument_id,
            trades_only=True,
        )
        if table.num_rows == 0:
            continue
        names = set(table.column_names)
        time_name = "t" if "t" in names else "ts_event"
        times = table.column(time_name)
        if pa.types.is_timestamp(times.type):
            times = times.cast(pa.timestamp("ns", tz=times.type.tz)).cast(pa.int64())
        t_ns = np.asarray(times.to_numpy(), dtype=np.int64)
        price_name = "price" if "price" in names else None
        if price_name is None:
            continue
        raw = table.column(price_name).fill_null(0)
        try:
            px = np.asarray(raw.cast(pa.float64()).to_numpy(), dtype=np.float64)
        except Exception:
            px = np.asarray(raw.to_numpy(zero_copy_only=False), dtype=np.float64)
        valid = np.isfinite(px) & (px > 0)
        if not np.any(valid):
            continue
        t_parts.append(t_ns[valid])
        p_parts.append(px[valid])
        sources.append(str(path))
    if not t_parts:
        return None
    t_ns = np.concatenate(t_parts)
    order = np.argsort(t_ns, kind="mergesort")
    return {
        "t_ns": t_ns[order],
        "price": np.concatenate(p_parts)[order],
        "path": sources[0],
        "sha256": memoized_file_digest(sources[0]),
        "instrument_id": str(instrument_id),
        "source": "p15_02_market_view_trades",
    }


_EXTREMES_SLIM: dict[str, dict[str, Any] | None] = {}


def nq_session_extremes(day: date, *, with_trades: bool = True) -> dict[str, Any] | None:
    key = day.isoformat()
    if key in _EXTREMES_SLIM and not with_trades:
        slim = _EXTREMES_SLIM[key]
        return None if slim is None else dict(slim)
    trades = market_view_trade_prices(day)
    if trades is None:
        _EXTREMES_SLIM[key] = None
        return None
    t = trades["t_ns"]
    px = trades["price"]
    account = (t >= et_ns(day, 18, 0) - 86400 * 1_000_000_000) & (t < et_ns(day, 17, 0))
    rth = (t >= et_ns(day, 9, 30)) & (t < et_ns(day, 16, 0))
    if not np.any(account):
        _EXTREMES_SLIM[key] = None
        return None

    def ext(mask: np.ndarray, high: bool) -> dict[str, Any]:
        if not np.any(mask):
            return {"price": None, "time_ns": None}
        vals = px[mask]
        times = t[mask]
        i = int(np.nanargmax(vals) if high else np.nanargmin(vals))
        return {"price": float(vals[i]), "time_ns": int(times[i])}

    slim = {
        "account_high": ext(account, True),
        "account_low": ext(account, False),
        "rth_high": ext(rth, True),
        "rth_low": ext(rth, False),
        "path": trades["path"],
        "sha256": trades["sha256"],
        "source": trades["source"],
    }
    _EXTREMES_SLIM[key] = slim
    if not with_trades:
        return dict(slim)
    out = dict(slim)
    out["trades"] = trades
    return out


def prior_rth_range(day: date) -> float | None:
    from trading_research.research.experts.options.instruments import previous_regular_session

    prior = previous_regular_session(day)
    if prior is None:
        return None
    ext = nq_session_extremes(prior, with_trades=False)
    if ext is None or ext["rth_high"]["price"] is None or ext["rth_low"]["price"] is None:
        return None
    return float(ext["rth_high"]["price"] - ext["rth_low"]["price"])


def map_to_nq(root: str, strike: float, day: date) -> dict[str, Any]:
    if root in ("NQ",):
        return {"nq": strike, "ratio": 1.0, "status": "native"}
    if root == "ES":
        from trading_research.research.experts.options.instruments import previous_regular_session

        prior = previous_regular_session(day)
        if prior is None:
            return {"nq": None, "ratio": None, "status": "no_prior"}
        nq = load_minute_bars(NQ_1M, prior)
        es = load_minute_bars(ES_1M, prior)
        if nq is None or es is None:
            return {"nq": None, "ratio": None, "status": "missing_prior_bars"}
        t0 = et_ns(prior, 9, 30)
        t1 = et_ns(prior, 16, 0)
        nq_t = nq["t_ns"][(nq["t_ns"] >= t0) & (nq["t_ns"] < t1)]
        nq_c = nq["c"][(nq["t_ns"] >= t0) & (nq["t_ns"] < t1)]
        es_t = es["t_ns"][(es["t_ns"] >= t0) & (es["t_ns"] < t1)]
        es_c = es["c"][(es["t_ns"] >= t0) & (es["t_ns"] < t1)]
        if nq_t.size == 0 or es_t.size == 0:
            return {"nq": None, "ratio": None, "status": "empty"}
        idx = np.searchsorted(es_t, nq_t)
        ok = idx < es_t.size
        idx = idx[ok]
        nq_c = nq_c[ok]
        nq_t = nq_t[ok]
        match = es_t[idx] == nq_t
        if np.count_nonzero(match) < 20:
            return {"nq": None, "ratio": None, "status": "insufficient_overlap"}
        ratio = float(np.median(nq_c[match] / np.clip(es_c[idx][match], 1e-9, None)))
        return {"nq": strike * ratio, "ratio": ratio, "status": "ok", "map_known_at_ns": int(t1)}
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
        out.append({"kind": kind, "strike": float(strike), "rank": 1, "signed_gamma": rec.get("signed_gamma"), "pain": rec.get("pain")})
    for i, rec in enumerate(board.get("top_gamma") or []):
        out.append({"kind": "top_gamma", "strike": float(rec["strike"]), "rank": i + 1, "value": rec.get("value")})
    for i, rec in enumerate(board.get("top_vanna") or []):
        out.append({"kind": "top_vanna", "strike": float(rec["strike"]), "rank": i + 1, "value": rec.get("value")})
    for i, rec in enumerate(board.get("top_vega") or []):
        out.append({"kind": "top_vega", "strike": float(rec["strike"]), "rank": i + 1, "value": rec.get("value")})
    return out


def session_bucket(time_ns: int | None, day: date) -> str:
    if time_ns is None:
        return "unknown"
    rth0 = et_ns(day, 9, 30)
    rth1 = et_ns(day, 16, 0)
    if rth0 <= time_ns < rth1:
        return "rth"
    acct0 = et_ns(day, 18, 0) - 86400 * 1_000_000_000
    if acct0 <= time_ns < rth0:
        return "overnight_or_pre"
    return "other"


def vol_regime(implied_move: float | None, spot: float | None) -> str:
    if implied_move is None or spot in (None, 0):
        return "unknown"
    ratio = float(implied_move) / float(spot)
    if ratio < 0.008:
        return "low"
    if ratio < 0.015:
        return "mid"
    return "high"


def _side_int(value: object) -> int | None:
    if value in (1, -1):
        return int(value)
    text = str(value).lower()
    if text in {"long", "buy", "1"}:
        return 1
    if text in {"short", "sell", "-1"}:
        return -1
    return None


def p15_03_first_passage(
    *,
    t_ns: np.ndarray,
    price: np.ndarray,
    start_ns: int,
    end_ns: int,
    side: int,
    entry: float,
    stop: float,
    target: float,
) -> str:
    if side * (entry - stop) <= 0 or side * (target - entry) <= 0:
        return "invalid_geometry"
    if end_ns <= start_ns:
        return "missing_future"
    mask = (t_ns > start_ns) & (t_ns <= end_ns)
    if not np.any(mask):
        return "neither"
    tt = t_ns[mask]
    pp = price[mask]
    hit_target = side * (pp - target) >= 0
    hit_stop = side * (pp - stop) <= 0
    hit = hit_target | hit_stop
    if not np.any(hit):
        return "neither"
    first = int(np.flatnonzero(hit)[0])
    same = tt == tt[first]
    hits_target = bool(np.any(hit_target[same]))
    hits_stop = bool(np.any(hit_stop[same]))
    if hits_target and hits_stop:
        return "same_batch_ambiguous"
    if hits_target:
        return "target_first"
    return "stop_first"


def load_strategy_refs(day: str, *, census_root: Path | None = None, trades: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    folder = (census_root / "jobs" / day) if census_root is not None else JOBS / day
    if not folder.is_dir():
        folder = JOBS / day
    if not folder.is_dir():
        return []
    rows = []
    account_end = None
    t_ns = None
    px = None
    if trades is not None:
        t_ns = trades["t_ns"]
        px = trades["price"]
        if t_ns.size:
            account_end = int(t_ns[-1])
    for path in sorted(folder.glob("*.json.gz")):
        with gzip.open(path) as handle:
            payload = json.load(handle)
        for ep in payload.get("episodes") or []:
            geom = ep.get("geometry") or {}
            entry = geom.get("entry")
            if entry is None:
                continue
            side = _side_int(ep.get("side"))
            stop = geom.get("stop")
            target = geom.get("target")
            decision = ep.get("decision_at")
            result = None
            if t_ns is not None and px is not None and side is not None and stop is not None and target is not None and decision is not None:
                end_ns = account_end if account_end is not None else int(decision) + 6 * 3600 * 1_000_000_000
                result = p15_03_first_passage(
                    t_ns=t_ns,
                    price=px,
                    start_ns=int(decision),
                    end_ns=int(end_ns),
                    side=side,
                    entry=float(entry),
                    stop=float(stop),
                    target=float(target),
                )
            if result is None:
                outcomes = payload.get("outcomes") or []
                for item in outcomes:
                    if item.get("candidate_id") == ep.get("candidate_id"):
                        result = item.get("result")
                        break
            rows.append(
                {
                    "branch": ep.get("branch") or payload.get("branch"),
                    "coverage_id": payload.get("coverage_id"),
                    "decision_at": decision,
                    "entry": float(entry),
                    "result": result,
                    "job": str(path),
                    "baseline_version": payload.get("baseline_version"),
                    "outcome_source": "p15_03_first_passage" if t_ns is not None else "job_file",
                }
            )
    return rows


def preserve_20date_atlas(source: Path) -> Path | None:
    if not (source / "LEVEL_ATLAS.json").is_file():
        return None
    if SUPERSEDED_20DATE.exists() and (SUPERSEDED_20DATE / "LEVEL_ATLAS.json").is_file():
        return SUPERSEDED_20DATE
    SUPERSEDED_20DATE.mkdir(parents=True, exist_ok=True)
    for path in source.glob("LEVEL_ATLAS*"):
        dest = SUPERSEDED_20DATE / path.name
        dest.write_bytes(path.read_bytes())
    note = SUPERSEDED_20DATE / "SUPERSEDED.md"
    note.write_text(
        "20-date Level Atlas pipeline proof from the early Phase 2 draft. "
        "Superseded by the census atlas. Descriptive; selects nothing.\n",
        encoding="utf-8",
    )
    return SUPERSEDED_20DATE


def missing_date_record(day_text: str, *, had_board: bool) -> dict[str, Any]:
    """Name the absent input that kept a census date out of atlas rows."""
    from trading_research.research.method_pack.session_policy import NQSessionPolicy

    day = date.fromisoformat(day_text)
    pol = NQSessionPolicy().day(day)
    if day_text == "2026-09-03":
        reason = "partial_session_2026-09-03; P15-02 complete account-day tape and 10:00 boards absent"
        absent = "partial_session_and_no_boards"
    elif day_text == "2026-06-19" or (pol.get("state") == "unverified_holiday" and pol.get("reason") == "juneteenth"):
        reason = "P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=juneteenth"
        absent = "p15_02_market_view_trades"
    elif pol.get("state") == "unverified_holiday":
        reason = f"P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason={pol.get('reason')}"
        absent = "p15_02_market_view_trades"
    elif pol.get("state") == "closed_rth":
        reason = f"NQSessionPolicy closed_rth: {pol.get('reason')}"
        absent = "session_closed"
    elif had_board:
        reason = "boards present; nq_session_extremes returned None (P15-02 market-view trades absent)"
        absent = "p15_02_market_view_trades"
    else:
        reason = "no 10:00 exposure board for QQQ/SPY/NQ/ES and no atlas rows"
        absent = "no_exposure_board"
    return {"day": day_text, "reason": reason, "had_board": had_board, "absent_input": absent, "policy_state": pol.get("state"), "policy_reason": pol.get("reason")}


def board_depth_by_root(boards: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[int]] = {}
    for board in boards:
        grouped.setdefault(board["root"], []).append(int(board.get("n_live") or 0))
    out: dict[str, Any] = {}
    for root, vals in grouped.items():
        ordered = sorted(vals)

        def pct(p: int) -> float:
            if not ordered:
                return float("nan")
            k = max(0, min(len(ordered) - 1, int(round((p / 100) * (len(ordered) - 1)))))
            return float(ordered[k])

        out[root] = {
            "n_boards": len(vals),
            "n_live": {"median": pct(50), "p10": pct(10), "p90": pct(90), "min": float(min(vals) if vals else 0), "max": float(max(vals) if vals else 0)},
        }
    return out


def compute_full_history_chain_coverage(*, atlas_boards: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Days with an OI vintage, days with quotes, days with a 10:00 board, per root and year."""
    from trading_research.research.experts.options.instruments import theta_path
    from trading_research.research.experts.options.instruments import root_spec as spec_of
    from trading_research.research.method_pack.clocks import et_ns

    census = census_status()
    dates = list(census.get("dates") or [])
    years = sorted({d[:4] for d in dates}) or [str(y) for y in range(2020, 2027)]
    board_days: dict[str, set[str]] = {root: set() for root in REQUIRED_ROOTS}
    fresh_days: dict[str, set[str]] = {root: set() for root in REQUIRED_ROOTS}
    for board in atlas_boards or []:
        root = board["root"]
        day = board["day"]
        board_days.setdefault(root, set()).add(day)
        n_fresh = board.get("n_with_fresh_quote")
        if n_fresh is None:
            n_fresh = int(board.get("n_contracts") or 0) - int(board.get("n_rejected") or 0)
        if int(n_fresh) > 0 or int(board.get("n_live") or 0) > 0 or int(board.get("n_contracts") or 0) > 0:
            fresh_days.setdefault(root, set()).add(day)

    def parquet_stems(folder: Path | None) -> set[str]:
        if folder is None or not folder.is_dir():
            return set()
        out: set[str] = set()
        for path in folder.glob("*.parquet"):
            try:
                date.fromisoformat(path.stem)
            except ValueError:
                continue
            out.add(path.stem)
        return out

    def decoded_days(root: str, kind: str) -> set[str]:
        from trading_research.research.experts.options.databento_decode import oi_table, quotes_table

        table = oi_table(root) if kind == "oi" else quotes_table(root)
        if table.num_rows == 0 or "ts_event" not in table.column_names:
            return set()
        ns = np.asarray(table.column("ts_event").to_numpy(), dtype=np.int64)
        ns.sort()
        found: set[str] = set()
        for text in dates:
            day = date.fromisoformat(text)
            lo = et_ns(day, 0, 0)
            hi = et_ns(day, 0, 0) + 86400 * 1_000_000_000
            i0 = int(np.searchsorted(ns, lo, side="left"))
            i1 = int(np.searchsorted(ns, hi, side="left"))
            if i1 > i0:
                found.add(text)
        return found

    def decoded_fresh(root: str) -> set[str]:
        from trading_research.research.experts.options.databento_decode import quotes_table

        table = quotes_table(root)
        if table.num_rows == 0 or "ts_event" not in table.column_names:
            return set()
        ns = np.asarray(table.column("ts_event").to_numpy(), dtype=np.int64)
        ns.sort()
        found: set[str] = set()
        for text in dates:
            day = date.fromisoformat(text)
            lo = et_ns(day, 9, 59)
            hi = et_ns(day, 10, 0)
            i0 = int(np.searchsorted(ns, lo, side="left"))
            i1 = int(np.searchsorted(ns, hi, side="left"))
            if i1 > i0:
                found.add(text)
        return found

    by_root: dict[str, Any] = {}
    for root in REQUIRED_ROOTS:
        spec = spec_of(root)
        if spec.databento_prefix:
            oi_set = decoded_days(root, "oi")
            quote_set = decoded_days(root, "quotes")
            fresh_set = decoded_fresh(root) | fresh_days.get(root, set())
        else:
            oi_set = parquet_stems(theta_path(spec, "oi"))
            quote_set = parquet_stems(theta_path(spec, "quote_dte14"))
            fresh_set = fresh_days.get(root, set())
        board_set = board_days.get(root, set())
        year_rows = []
        for year in years:
            year_rows.append(
                {
                    "year": year,
                    "n_days_oi_vintage": sum(1 for d in oi_set if d.startswith(year)),
                    "n_days_with_quotes": sum(1 for d in quote_set if d.startswith(year)),
                    "n_days_fresh_quote": sum(1 for d in fresh_set if d.startswith(year)),
                    "n_days_board": sum(1 for d in board_set if d.startswith(year)),
                }
            )
        by_root[root] = {
            "n_days_oi_vintage": len(oi_set),
            "n_days_with_quotes": len(quote_set),
            "n_days_fresh_quote": len(fresh_set),
            "n_days_board": len(board_set),
            "by_year": year_rows,
        }
    return {
        "schema_version": "research-chain-coverage-full-history-v1",
        "n_census_dates": len(dates),
        "roots": by_root,
        "note": "OI vintage = unique OI session dates. Quotes = unique quote-file or decoded-quote dates. Fresh quote = 10:00 snapshot under the 60 s age rule (OPRA: days that produced a board snapshot; NQ/ES: 09:59 ohlcv-1m bar or a board snapshot). Board = ATLAS_BOARDS entry.",
    }


def build_atlas(
    boards: list[dict[str, Any]],
    run_root: Path,
    *,
    coverage: list[dict[str, Any]] | None = None,
    slice_dates: list[str] | None = None,
    census_root: Path | None = None,
    provisional: bool = False,
    chain_coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_root.mkdir(parents=True, exist_ok=True)
    rows = []
    alignment = []
    by_root: dict[str, list[dict[str, Any]]] = {root: [] for root in REQUIRED_ROOTS}
    missing_dates: list[dict[str, Any]] = []
    board_days = {b["day"] for b in boards}
    skipped_no_extremes: list[str] = []
    by_day_root: dict[tuple[str, str], dict[str, Any]] = {}
    census = census_root if census_root is not None else (CENSUS_ROOT if (CENSUS_ROOT / "jobs").is_dir() else None)
    boards_by_day: dict[str, list[dict[str, Any]]] = {}
    for board in boards:
        by_day_root[(board["root"], board["day"])] = board
        boards_by_day.setdefault(board["day"], []).append(board)
    for day_text, day_boards in sorted(boards_by_day.items()):
        day = date.fromisoformat(day_text)
        try:
            ext_full = nq_session_extremes(day)
        except Exception:
            ext_full = None
        trades = None if ext_full is None else ext_full.pop("trades", None)
        ext = ext_full
        s = prior_rth_range(day)
        refs = load_strategy_refs(day_text, census_root=census, trades=trades)
        trades = None
        if ext is None:
            skipped_no_extremes.append(day_text)
            continue
        for board in day_boards:
            asof = int(board["asof_ns"])
            regime = vol_regime(board.get("implied_move"), board.get("spot"))
            high_bucket = session_bucket(ext["account_high"].get("time_ns"), day)
            low_bucket = session_bucket(ext["account_low"].get("time_ns"), day)
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
                    "signed_gamma": level.get("signed_gamma"),
                    "expiry_bucket": board.get("front_bucket"),
                    "vol_regime": regime,
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
                    "high_session_bucket": high_bucket,
                    "low_session_bucket": low_bucket,
                    "high_time_ns": ext["account_high"].get("time_ns"),
                    "low_time_ns": ext["account_low"].get("time_ns"),
                    "abs_gamma_sum": board.get("abs_gamma_sum"),
                    "oi_sum": board.get("oi_sum"),
                }
                if mapped.get("nq") is not None and s:
                    nq_px = float(mapped["nq"])
                    rec["high"] = proximity(nq_px, ext["account_high"]["price"], s)
                    rec["low"] = proximity(nq_px, ext["account_low"]["price"], s)
                    rec["rth_high"] = proximity(nq_px, ext["rth_high"]["price"], s) if ext["rth_high"]["price"] else None
                    rec["rth_low"] = proximity(nq_px, ext["rth_low"]["price"], s) if ext["rth_low"]["price"] else None
                    rec["high_after_available"] = ext["account_high"]["time_ns"] is not None and ext["account_high"]["time_ns"] >= asof
                    rec["low_after_available"] = ext["account_low"]["time_ns"] is not None and ext["account_low"]["time_ns"] >= asof
                    rec["high"]["extreme_time_ns"] = ext["account_high"].get("time_ns")
                    rec["low"]["extreme_time_ns"] = ext["account_low"].get("time_ns")
                    rec["high"]["dt_after_available_ns"] = None if ext["account_high"].get("time_ns") is None else int(ext["account_high"]["time_ns"]) - asof
                    rec["low"]["dt_after_available_ns"] = None if ext["account_low"].get("time_ns") is None else int(ext["account_low"]["time_ns"]) - asof
                    offset = control_offset(level_id, s)
                    rec["control"] = {
                        "offset_s": offset / s,
                        "high": proximity(nq_px + offset, ext["account_high"]["price"], s),
                        "low": proximity(nq_px + offset, ext["account_low"]["price"], s),
                    }
                rows.append(rec)
                by_root.setdefault(board["root"], []).append(rec)
            if not s:
                continue
            usable = [row for row in rows if row["day"] == board["day"] and row["root"] == board["root"] and row.get("mapped_nq") is not None]
            for ref in refs:
                if ref["decision_at"] is None or int(ref["decision_at"]) < asof:
                    continue
                for kind in ("key_gamma", "call_wall", "put_wall", "gamma_flip", "max_pain"):
                    candidates = [row for row in usable if row["kind"] == kind]
                    if not candidates:
                        continue
                    nearest = min(candidates, key=lambda row: abs(float(row["mapped_nq"]) - ref["entry"]))
                    signed = (float(nearest["mapped_nq"]) - ref["entry"]) / s
                    dist_s = abs(signed)
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
                            "signed_dist_s": signed,
                            "dist_s": dist_s,
                            "bucket": bucket,
                            "result": ref["result"],
                            "job": ref["job"],
                            "level_kind": kind,
                            "level_id": nearest["level_id"],
                        }
                    )
    agreement = _root_agreement(rows)
    changes = _change_features(rows, by_day_root)
    summary = _summarize(rows, alignment, agreement, changes)
    row_days = {r["day"] for r in rows}
    wanted = list(slice_dates) if slice_dates else sorted(board_days)
    missing_dates = []
    seen_missing: set[str] = set()
    for day_text in wanted:
        if day_text in row_days or day_text in seen_missing:
            continue
        rec = missing_date_record(day_text, had_board=day_text in board_days)
        missing_dates.append(rec)
        seen_missing.add(day_text)
    for day_text in skipped_no_extremes:
        if day_text in row_days or day_text in seen_missing:
            continue
        missing_dates.append(missing_date_record(day_text, had_board=True))
        seen_missing.add(day_text)
    missing_dates.sort(key=lambda item: item["day"])
    depth = board_depth_by_root(boards)
    if chain_coverage is None and boards:
        chain_coverage = compute_full_history_chain_coverage(atlas_boards=boards)
    census_meta = census_status()
    n_census = len(wanted) if slice_dates else int(census_meta.get("n_dates") or 0)
    payload = {
        "schema_version": "research-level-atlas-v1",
        "selects_nothing": True,
        "inventory_sign_assumption": "call_positive_put_negative labelled scenario, not known dealer inventory",
        "deviations": {
            "b0_1_and_p15_03": "B0.1 job geometry.entry/decision_at with P15-03 first-passage labels on market-view trades",
            "extremes_source": "P15-02 NativeMarketView trade prints (trades-only load_span_arrow)",
            "missing_slice_dates": missing_dates,
            "n_row_days": len(row_days),
            "n_census_dates": n_census,
            "reconciliation": {
                "n_row_days": len(row_days),
                "n_missing": len(missing_dates),
                "n_census": n_census,
                "identity": len(row_days) + len(missing_dates) == n_census,
            },
            "provisional": provisional,
            "superseded_20date": str(SUPERSEDED_20DATE) if SUPERSEDED_20DATE.is_dir() else None,
            "p15_03_receipt": str(P15_03_RECEIPT) if P15_03_RECEIPT.is_file() else None,
            "census_root": None if census is None else str(census),
        },
        "profile_family": "deferred_phase_3",
        "rows": rows,
        "strategy_alignment": alignment,
        "root_agreement": agreement,
        "change_features": changes,
        "summary": summary,
        "coverage": coverage or [],
        "chain_coverage_full_history": chain_coverage,
        "board_depth": depth,
        "limitations": _atlas_limitations(provisional=provisional, coverage=coverage, chain_coverage=chain_coverage, depth=depth, summary=summary),
        "peak_rss_bytes": peak_rss_bytes(),
    }
    write_json_document(run_root / "LEVEL_ATLAS.json", payload, compact=True)
    (run_root / "LEVEL_ATLAS.md").write_text(_markdown(payload), encoding="utf-8")
    _write_root_csvs(run_root, by_root, boards)
    _write_headline_csv(run_root, payload)
    _write_atlas_summary(run_root, payload)
    return payload


def refresh_atlas_artifacts(
    run_root: Path,
    *,
    coverage: list[dict[str, Any]] | None = None,
    atlas_boards: list[dict[str, Any]] | None = None,
    chain_coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Rewrite summary/markdown/CSVs from an existing LEVEL_ATLAS.json. Does not duplicate the JSON."""
    path = run_root / "LEVEL_ATLAS.json"
    payload = json.loads(path.read_text())
    rows = payload.get("rows") or []
    alignment = payload.get("strategy_alignment") or []
    boards = atlas_boards
    if boards is None:
        cache = run_root / "ATLAS_BOARDS.json"
        boards = list(json.loads(cache.read_text()).get("boards") or []) if cache.is_file() else []
    by_day_root = {(b["root"], b["day"]): b for b in boards}
    agreement = payload.get("root_agreement") or _root_agreement(rows)
    changes = payload.get("change_features") or _change_features(rows, by_day_root)
    summary = _summarize(rows, alignment, agreement, changes)
    row_days = {r["day"] for r in rows}
    board_days = {b["day"] for b in boards}
    census_meta = census_status()
    census_dates = list(census_meta.get("dates") or [])
    missing_dates = []
    for day_text in census_dates:
        if day_text in row_days:
            continue
        missing_dates.append(missing_date_record(day_text, had_board=day_text in board_days))
    depth = board_depth_by_root(boards)
    if chain_coverage is None:
        chain_coverage = compute_full_history_chain_coverage(atlas_boards=boards)
    deviations = dict(payload.get("deviations") or {})
    deviations["missing_slice_dates"] = missing_dates
    deviations["n_row_days"] = len(row_days)
    deviations["n_census_dates"] = len(census_dates)
    deviations["reconciliation"] = {
        "n_row_days": len(row_days),
        "n_missing": len(missing_dates),
        "n_census": len(census_dates),
        "identity": len(row_days) + len(missing_dates) == len(census_dates),
    }
    payload["summary"] = summary
    payload["deviations"] = deviations
    payload["chain_coverage_full_history"] = chain_coverage
    payload["board_depth"] = depth
    payload["coverage"] = coverage if coverage is not None else payload.get("coverage") or []
    payload["limitations"] = _atlas_limitations(
        provisional=bool(deviations.get("provisional")),
        coverage=payload["coverage"],
        chain_coverage=chain_coverage,
        depth=depth,
        summary=summary,
    )
    write_json_document(path, payload, compact=True)
    (run_root / "LEVEL_ATLAS.md").write_text(_markdown(payload), encoding="utf-8")
    by_root: dict[str, list[dict[str, Any]]] = {root: [] for root in REQUIRED_ROOTS}
    for row in rows:
        by_root.setdefault(row["root"], []).append(row)
    _write_root_csvs(run_root, by_root, boards)
    _write_headline_csv(run_root, payload)
    _write_atlas_summary(run_root, payload)
    avail_path = run_root.parent / "P2-09" / "OPTIONS_AVAILABILITY.json"
    if avail_path.is_file():
        avail = json.loads(avail_path.read_text())
        avail["chain_coverage_full_history"] = chain_coverage
        write_json_document(avail_path, avail)
    return {
        "refreshed": True,
        "n_row_days": len(row_days),
        "n_missing": len(missing_dates),
        "n_census": len(census_dates),
        "reconciliation": deviations["reconciliation"],
        "n_levels": summary.get("n_levels"),
    }


def _block_bootstrap(day_values: dict[str, list[int]], *, n_boot: int = 399, seed: int = 15022026) -> dict[str, Any]:
    days = sorted(day_values)
    if not days:
        return {"n": 0, "rate": None, "interval_95": [None, None], "n_boot": n_boot}
    rates = []
    rng = np.random.default_rng(seed)
    n_days = len(days)
    for _ in range(n_boot):
        draw = rng.integers(0, n_days, size=n_days)
        vals = []
        for i in draw:
            vals.extend(day_values[days[int(i)]])
        rates.append(float(np.mean(vals)) if vals else 0.0)
    flat = [v for d in days for v in day_values[d]]
    lo, hi = np.percentile(rates, [2.5, 97.5])
    return {
        "n": len(flat),
        "rate": float(np.mean(flat)) if flat else None,
        "interval_95": [float(lo), float(hi)],
        "n_boot": n_boot,
        "block": "day",
    }


def _cell(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    by_day: dict[str, list[int]] = {}
    for row in rows:
        flag = row.get(key)
        if flag is None:
            continue
        by_day.setdefault(row["day"], []).append(int(bool(flag)))
    return _block_bootstrap(by_day)


def _flags(rows: list[dict[str, Any]], getter) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        val = getter(row)
        if val is None:
            continue
        out.append({"day": row["day"], "flag": val})
    return out


def _proximity_block(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Headline high/low/control rates use only extremes that print after the level's availability clock."""
    out: dict[str, Any] = {"n": len(rows)}
    for side in ("high", "low"):
        out[f"{side}_after_available"] = _cell(_flags(rows, lambda r, s=side: r.get(f"{s}_after_available")), "flag")
        for ticks in (4, 8, 16):
            out[f"{side}_within_{ticks}"] = _cell(
                _flags(
                    rows,
                    lambda r, s=side, t=ticks: None
                    if not r.get(f"{s}_after_available")
                    else (r.get(s) or {}).get(f"within_{t}"),
                ),
                "flag",
            )
            out[f"{side}_within_{ticks}_unrestricted"] = _cell(
                _flags(rows, lambda r, s=side, t=ticks: (r.get(s) or {}).get(f"within_{t}")),
                "flag",
            )
            out[f"control_{side}_within_{ticks}"] = _cell(
                _flags(
                    rows,
                    lambda r, s=side, t=ticks: None
                    if not r.get(f"{s}_after_available")
                    else ((r.get("control") or {}).get(s) or {}).get(f"within_{t}"),
                ),
                "flag",
            )
            out[f"control_{side}_within_{ticks}_unrestricted"] = _cell(
                _flags(rows, lambda r, s=side, t=ticks: ((r.get("control") or {}).get(s) or {}).get(f"within_{t}")),
                "flag",
            )
    return out


def _group(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(str(row.get(field) or "unknown"), []).append(row)
    return {key: _proximity_block(items) for key, items in sorted(buckets.items())}


def _root_agreement(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    by_day_kind: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("mapped_nq") is None or not row.get("s_prior_rth_range"):
            continue
        by_day_kind.setdefault((row["day"], row["kind"]), []).append(row)
    for (day, kind), items in by_day_kind.items():
        agreeing_ids = set()
        for i, a in enumerate(items):
            partners = []
            for b in items:
                if a["root"] == b["root"]:
                    continue
                if abs(float(a["mapped_nq"]) - float(b["mapped_nq"])) / float(a["s_prior_rth_range"]) <= 0.25:
                    partners.append(b["root"])
            if len(partners) >= 1:
                agreeing_ids.add(a["level_id"])
                out.append(
                    {
                        "day": day,
                        "kind": kind,
                        "root": a["root"],
                        "partners": partners,
                        "level_id": a["level_id"],
                        "mapped_nq": a["mapped_nq"],
                        "high": a.get("high"),
                        "low": a.get("low"),
                        "control": a.get("control"),
                        "agreeing": True,
                    }
                )
        for a in items:
            if a["level_id"] in agreeing_ids:
                continue
            out.append(
                {
                    "day": day,
                    "kind": kind,
                    "root": a["root"],
                    "partners": [],
                    "level_id": a["level_id"],
                    "mapped_nq": a["mapped_nq"],
                    "high": a.get("high"),
                    "low": a.get("low"),
                    "control": a.get("control"),
                    "agreeing": False,
                }
            )
    return out


def _change_features(rows: list[dict[str, Any]], by_day_root: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    by_root_kind: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        by_root_kind.setdefault((row["root"], row["kind"]), []).append(row)
    for (root, kind), items in by_root_kind.items():
        ordered = sorted(items, key=lambda r: r["day"])
        prev = None
        for rec in ordered:
            if prev is not None and rec["rank"] == prev["rank"]:
                d_strike = None if rec["strike"] is None or prev["strike"] is None else rec["strike"] - prev["strike"]
                d_g = None
                if rec.get("signed_gamma") is not None and prev.get("signed_gamma") is not None:
                    d_g = float(rec["signed_gamma"]) - float(prev["signed_gamma"])
                out.append(
                    {
                        "root": root,
                        "kind": kind,
                        "day": rec["day"],
                        "prior_day": prev["day"],
                        "strike_change": d_strike,
                        "signed_gamma_change": d_g,
                        "intraday_gamma_rate": None,
                        "intraday_volume_rate": None,
                        "intraday_status": "unavailable_single_10et_snapshot",
                        "high": rec.get("high"),
                        "low": rec.get("low"),
                    }
                )
            prev = rec
    return out


def _coverage_lines(coverage: list[dict[str, Any]] | None, chain_coverage: dict[str, Any] | None = None) -> list[str]:
    lines: list[str] = []
    if chain_coverage and chain_coverage.get("roots"):
        lines.append("Chain coverage per root and year over the full B0.1 census (days with an OI vintage, days with quotes, days with a fresh 10:00 quote under the 60 s age rule, days with a board):")
        for root, rec in sorted(chain_coverage["roots"].items()):
            lines.append(
                f"{root} all-years: oi_vintage={rec.get('n_days_oi_vintage')} quotes={rec.get('n_days_with_quotes')} fresh_quote={rec.get('n_days_fresh_quote')} board={rec.get('n_days_board')}"
            )
            for year_row in rec.get("by_year") or []:
                lines.append(
                    f"{root} {year_row['year']}: oi_vintage={year_row['n_days_oi_vintage']} quotes={year_row['n_days_with_quotes']} fresh_quote={year_row['n_days_fresh_quote']} board={year_row['n_days_board']}"
                )
        if chain_coverage.get("note"):
            lines.append(str(chain_coverage["note"]))
    elif not coverage:
        lines.append("Chain coverage per root and year was not passed into the atlas.")
    if coverage:
        from collections import defaultdict

        tab: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"n": 0, "complete": 0, "partial": 0, "unsupported": 0})
        for row in coverage:
            key = (row["root"], row["day"][:4])
            tab[key]["n"] += 1
            disp = row.get("disposition")
            if disp == "complete_observed_scope":
                tab[key]["complete"] += 1
            elif disp == "unsupported_owned_input":
                tab[key]["unsupported"] += 1
            else:
                tab[key]["partial"] += 1
        lines.append("20-date OPTIONS_AVAILABILITY slice (superseded as the coverage table; retained as the producing-slice disposition log):")
        for root, year in sorted(tab):
            c = tab[(root, year)]
            lines.append(f"{root} {year}: n={c['n']} complete_observed_scope={c['complete']} partial={c['partial']} unsupported_owned_input={c['unsupported']}")
    return lines


def _atlas_limitations(
    *,
    provisional: bool,
    coverage: list[dict[str, Any]] | None,
    chain_coverage: dict[str, Any] | None,
    depth: dict[str, Any] | None,
    summary: dict[str, Any] | None,
) -> list[str]:
    lines = [
        "The atlas is descriptive. It selects nothing.",
        "Inventory-sign assumption: call-positive/put-negative labelled scenario, not known dealer inventory.",
        "Strategy references come from the B0.1 corrected-baseline job files when present; otherwise run-1.0.1 evaluation jobs.",
        "P15-03 outcomes are ordered first-passage labels on P15-02 market-view trade prints from decision_at through the last trade of the loaded account day. Coverage gaps are not re-injected into that scan.",
        "Account-day and RTH extremes are max/min P15-02 market-view trade prints, not 1-minute OHLC and not BBO midpoints.",
        "Profile-family atlas cells are specified and deferred to Phase 3. They are not produced in this attempt.",
        "Intraday rate-of-change of aggregate gamma and executed volume is unavailable. This atlas freezes one 10:00 ET board per day.",
        "OPRA quotes are scoped DTE/strike feeds, not full chain. NQ/ES quotes are owned DBN ohlcv-1m last-trade mids, not BBO.",
        "Continuous NQ/ES 1-minute series is the underlier proxy for futures-option boards; the option definition underlying_id is preserved separately.",
        "Headline proximity cells are after-availability rates: a level can only mark an extreme it was known before. Unrestricted rates (all extremes, ignoring the availability clock) are the superseded diagnostic column.",
        DEGENERATE_LABEL + ". " + DEGENERATE_NOTE,
        "Alignment headline tables exclude NQ and ES; those rows are reported separately under the degenerate-board label.",
    ]
    if depth:
        for root in ("QQQ", "SPY", "NQ", "ES"):
            rec = depth.get(root) or {}
            live = rec.get("n_live") or {}
            lines.append(
                f"Board depth {root}: n_boards={rec.get('n_boards')} n_live median={live.get('median')} p10={live.get('p10')} p90={live.get('p90')} min={live.get('min')} max={live.get('max')}."
            )
    overall = (summary or {}).get("overall") or {}
    unres = overall.get("high_within_8_unrestricted") or {}
    if unres.get("rate") is not None:
        lo, hi = unres.get("interval_95") or [None, None]
        lines.append(
            f"Superseded diagnostic (unrestricted high-within-8 over headline roots): {unres['rate']:.3f} [{lo:.3f}, {hi:.3f}] n={unres['n']}."
        )
    if provisional:
        lines.append("RUN_COMPLETE.json was absent; atlas dates are the B0.1 40-date preview. Labelled provisional.")
    lines.extend(_coverage_lines(coverage, chain_coverage))
    return lines


def _csv_row(row: dict[str, Any]) -> dict[str, Any]:
    out = _flatten(row)
    high = row.get("high") or {}
    low = row.get("low") or {}
    ctrl_h = ((row.get("control") or {}).get("high") or {})
    after_h = bool(row.get("high_after_available"))
    after_l = bool(row.get("low_after_available"))
    for ticks in (4, 8, 16):
        out[f"high_headline_within_{ticks}"] = high.get(f"within_{ticks}") if after_h else None
        out[f"low_headline_within_{ticks}"] = low.get(f"within_{ticks}") if after_l else None
        out[f"high_unrestricted_within_{ticks}"] = high.get(f"within_{ticks}")
        out[f"low_unrestricted_within_{ticks}"] = low.get(f"within_{ticks}")
    out["control_high_headline_within_8"] = ctrl_h.get("within_8") if after_h else None
    out["control_high_unrestricted_within_8"] = ctrl_h.get("within_8")
    out["degenerate_board_label"] = DEGENERATE_LABEL if row.get("root") in DEGENERATE_ROOTS else ""
    return out


def _write_root_csvs(run_root: Path, by_root: dict[str, list[dict[str, Any]]], boards: list[dict[str, Any]]) -> None:
    present = {b["root"] for b in boards}
    for root in REQUIRED_ROOTS:
        path = run_root / f"LEVEL_ATLAS_{root}.csv"
        items = by_root.get(root) or []
        if not items:
            reason = "no_mapped_levels" if root in ("NQ", "ES") else "no_native_intraday_spot_or_no_board"
            if root in present:
                reason = "board_present_but_no_mapped_levels"
            if root in DEGENERATE_ROOTS:
                reason = f"{reason}; {DEGENERATE_LABEL}"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["root", "status", "reason", "n_rows", "degenerate_board_label"])
                writer.writeheader()
                writer.writerow(
                    {
                        "root": root,
                        "status": "unavailable",
                        "reason": reason,
                        "n_rows": 0,
                        "degenerate_board_label": DEGENERATE_LABEL if root in DEGENERATE_ROOTS else "",
                    }
                )
            continue
        flat_rows = [_csv_row(row) for row in items]
        keys = sorted({k for row in flat_rows for k in row})
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            for row in flat_rows:
                writer.writerow(row)


def _write_atlas_summary(run_root: Path, payload: dict[str, Any]) -> None:
    write_json_document(
        run_root / "LEVEL_ATLAS_SUMMARY.json",
        {
            "schema_version": "research-level-atlas-summary-v1",
            "selects_nothing": True,
            "summary": payload.get("summary"),
            "deviations": payload.get("deviations"),
            "limitations": payload.get("limitations"),
            "board_depth": payload.get("board_depth"),
            "chain_coverage_full_history": payload.get("chain_coverage_full_history"),
        },
    )


def _write_headline_csv(run_root: Path, payload: dict[str, Any]) -> None:
    summary = payload.get("summary") or {}
    path = run_root / "LEVEL_ATLAS_HEADLINE.csv"
    fieldnames = [
        "section",
        "group",
        "label",
        "n",
        "high_4",
        "high_8",
        "high_16",
        "low_4",
        "low_8",
        "low_16",
        "control_high_8",
        "unrestricted_high_8",
        "unrestricted_low_8",
        "high_after_available",
        "low_after_available",
    ]

    def cells(block: dict[str, Any]) -> dict[str, Any]:
        return {
            "n": block.get("n"),
            "high_4": _fmt_cell(block.get("high_within_4")),
            "high_8": _fmt_cell(block.get("high_within_8")),
            "high_16": _fmt_cell(block.get("high_within_16")),
            "low_4": _fmt_cell(block.get("low_within_4")),
            "low_8": _fmt_cell(block.get("low_within_8")),
            "low_16": _fmt_cell(block.get("low_within_16")),
            "control_high_8": _fmt_cell(block.get("control_high_within_8")),
            "unrestricted_high_8": _fmt_cell(block.get("high_within_8_unrestricted")),
            "unrestricted_low_8": _fmt_cell(block.get("low_within_8_unrestricted")),
            "high_after_available": _fmt_cell(block.get("high_after_available")),
            "low_after_available": _fmt_cell(block.get("low_after_available")),
        }

    rows_out: list[dict[str, Any]] = []
    rows_out.append({"section": "headline_qqq_spy", "group": "all", "label": "after_availability", **cells(summary.get("overall") or {})})
    for name, block in (summary.get("by_root") or {}).items():
        label = DEGENERATE_LABEL if name in DEGENERATE_ROOTS else "after_availability"
        section = "degenerate_nq_es" if name in DEGENERATE_ROOTS else "headline_by_root"
        rows_out.append({"section": section, "group": name, "label": label, **cells(block)})
    degen = summary.get("degenerate") or {}
    rows_out.append({"section": "degenerate_nq_es", "group": "NQ+ES", "label": DEGENERATE_LABEL, **cells(degen.get("overall") or {})})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows_out:
            writer.writerow(row)


def _flatten(row: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out = {}
    for key, value in row.items():
        name = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            out.update(_flatten(value, name))
        else:
            out[name if prefix else key] = value
    return out


def _alignment_outcomes(alignment: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(alignment)
    n_na = sum(1 for item in alignment if item.get("result") == "not_applicable")
    overall = {}
    for item in alignment:
        overall[item.get("result") or "missing"] = overall.get(item.get("result") or "missing", 0) + 1
    unconditional = {k: v / n if n else None for k, v in overall.items()}
    by_branch: dict[str, dict[str, Any]] = {}
    for item in alignment:
        key = f"{item.get('branch')}|{item.get('level_kind')}"
        cell = by_branch.setdefault(key, {"branch": item.get("branch"), "level_kind": item.get("level_kind"), "n": 0, "results": {}, "bins": {}})
        cell["n"] += 1
        res = item.get("result") or "missing"
        cell["results"][res] = cell["results"].get(res, 0) + 1
        bucket = item.get("bucket") or "beyond"
        bin_cell = cell["bins"].setdefault(bucket, {"n": 0, "results": {}})
        bin_cell["n"] += 1
        bin_cell["results"][res] = bin_cell["results"].get(res, 0) + 1
    for cell in by_branch.values():
        cell["unconditional"] = {k: v / cell["n"] for k, v in cell["results"].items()}
        for bucket, bin_cell in cell["bins"].items():
            bin_cell["conditional"] = {k: v / bin_cell["n"] for k, v in bin_cell["results"].items()}
    return {
        "n": n,
        "n_not_applicable": n_na,
        "not_applicable_rate": None if n == 0 else n_na / n,
        "unconditional": unconditional,
        "unconditional_counts": overall,
        "by_branch_and_level": list(by_branch.values()),
    }


def _summarize(
    rows: list[dict[str, Any]],
    alignment: list[dict[str, Any]],
    agreement: list[dict[str, Any]],
    changes: list[dict[str, Any]],
) -> dict[str, Any]:
    equity = [r for r in rows if r.get("root") in HEADLINE_ROOTS]
    degen = [r for r in rows if r.get("root") in DEGENERATE_ROOTS]
    other = [r for r in rows if r.get("root") not in HEADLINE_ROOTS + DEGENERATE_ROOTS]
    headline_rows = equity if equity else other if not degen else equity
    if not headline_rows and rows:
        headline_rows = [r for r in rows if r.get("root") not in DEGENERATE_ROOTS] or rows
    align_has_root = any(item.get("root") for item in alignment)
    align_eq = [a for a in alignment if a.get("root") in HEADLINE_ROOTS] if align_has_root else alignment
    align_degen = [a for a in alignment if a.get("root") in DEGENERATE_ROOTS] if align_has_root else []
    agreeing = [r for r in agreement if r.get("agreeing") and r.get("root") in HEADLINE_ROOTS]
    single = [r for r in agreement if (not r.get("agreeing")) and r.get("root") in HEADLINE_ROOTS]
    if not agreement:
        agreeing, single = [], []
    elif not any(r.get("root") in HEADLINE_ROOTS for r in agreement):
        agreeing = [r for r in agreement if r.get("agreeing")]
        single = [r for r in agreement if not r.get("agreeing")]
    return {
        "n_levels": len(rows),
        "n_levels_headline": len(headline_rows),
        "n_levels_degenerate": len(degen),
        "n_alignment": len(align_eq),
        "n_alignment_degenerate": len(align_degen),
        "headline_roots": list(HEADLINE_ROOTS),
        "degenerate_roots": list(DEGENERATE_ROOTS),
        "degenerate_label": DEGENERATE_LABEL,
        "headline_definition": "after_availability_qqq_spy",
        "overall": _proximity_block(headline_rows),
        "overall_including_degenerate": _proximity_block(rows),
        "by_kind": _group(headline_rows, "kind"),
        "by_root": _group(rows, "root"),
        "by_year": _group(headline_rows, "year"),
        "by_expiry_bucket": _group(headline_rows, "expiry_bucket"),
        "by_session_bucket_high": _group(headline_rows, "high_session_bucket"),
        "by_session_bucket_low": _group(headline_rows, "low_session_bucket"),
        "by_vol_regime": _group(headline_rows, "vol_regime"),
        "alignment_outcomes": _alignment_outcomes(align_eq),
        "degenerate": {
            "label": DEGENERATE_LABEL,
            "note": DEGENERATE_NOTE,
            "overall": _proximity_block(degen),
            "by_root": _group(degen, "root"),
            "by_kind": _group(degen, "kind"),
            "alignment_outcomes": _alignment_outcomes(align_degen),
        },
        "root_agreement": {
            "n_agreeing": len(agreeing),
            "n_single": len(single),
            "agreeing": _proximity_block(agreeing),
            "single_root": _proximity_block(single),
        },
        "change_features": {
            "n": len(changes),
            "intraday_status": "unavailable_single_10et_snapshot",
            "one_day": _proximity_block(changes),
        },
    }


def _fmt_cell(cell: dict[str, Any] | None) -> str:
    if not cell or cell.get("rate") is None:
        return "n/a"
    lo, hi = cell.get("interval_95") or [None, None]
    return f"{cell['rate']:.3f} [{lo:.3f}, {hi:.3f}] n={cell['n']}"


def _group_name(name: str) -> str:
    if name in DEGENERATE_ROOTS:
        return f"{name} ({DEGENERATE_LABEL})"
    return name


def _table(title: str, grouped: dict[str, dict[str, Any]], *, degenerate: bool = False) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, block in grouped.items():
        label = _group_name(name) if (degenerate or name in DEGENERATE_ROOTS) else name
        lines.append(
            "| {name} | {n} | {h4} | {h8} | {h16} | {l4} | {l8} | {l16} | {c8} | {u8} | {ha} | {la} |".format(
                name=label,
                n=block.get("n"),
                h4=_fmt_cell(block.get("high_within_4")),
                h8=_fmt_cell(block.get("high_within_8")),
                h16=_fmt_cell(block.get("high_within_16")),
                l4=_fmt_cell(block.get("low_within_4")),
                l8=_fmt_cell(block.get("low_within_8")),
                l16=_fmt_cell(block.get("low_within_16")),
                c8=_fmt_cell(block.get("control_high_within_8")),
                u8=_fmt_cell(block.get("high_within_8_unrestricted")),
                ha=_fmt_cell(block.get("high_after_available")),
                la=_fmt_cell(block.get("low_after_available")),
            )
        )
    lines.append("")
    return lines


def _alignment_table(align: dict[str, Any]) -> list[str]:
    lines = [
        f"Rows: {align['n']}. result=not_applicable: {align['n_not_applicable']} ({align['not_applicable_rate']}).",
        "",
        "Unconditional result mix: " + ", ".join(f"{k}={v}" for k, v in sorted((align.get("unconditional_counts") or {}).items())) + ".",
        "",
        "| branch | level kind | n | unconditional | bucket | bucket n | conditional |",
        "| --- | --- | ---: | --- | --- | ---: | --- |",
    ]
    for cell in align.get("by_branch_and_level") or []:
        unc = ", ".join(f"{k}:{v:.3f}" for k, v in sorted(cell.get("unconditional", {}).items()))
        bins = cell.get("bins") or {}
        if not bins:
            lines.append(f"| {cell.get('branch')} | {cell.get('level_kind')} | {cell['n']} | {unc} |  |  |  |")
            continue
        first = True
        for bucket, bin_cell in sorted(bins.items()):
            cond = ", ".join(f"{k}:{v:.3f}" for k, v in sorted(bin_cell.get("conditional", {}).items()))
            branch = cell.get("branch") if first else ""
            kind = cell.get("level_kind") if first else ""
            n = cell["n"] if first else ""
            unc_cell = unc if first else ""
            lines.append(f"| {branch} | {kind} | {n} | {unc_cell} | {bucket} | {bin_cell['n']} | {cond} |")
            first = False
    lines.append("")
    return lines


def _markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    align = s["alignment_outcomes"]
    recon = (payload.get("deviations") or {}).get("reconciliation") or {}
    lines = [
        "# Level Atlas",
        "",
        "Descriptive census. This document selects nothing.",
        "",
        f"Levels counted: {s['n_levels']} (headline QQQ+SPY: {s.get('n_levels_headline')}; NQ+ES degenerate: {s.get('n_levels_degenerate')}). Strategy-alignment rows (headline QQQ+SPY): {s['n_alignment']}.",
        "",
        "Headline proximity rates are after-availability: a level marks an extreme only if that extreme printed at or after the 10:00 ET availability clock. Unrestricted rates (all extremes) are the diagnostic column `unrestricted high 8`. Rates are day-block bootstrap means with 95 percent intervals (399 resamples, seed 15022026).",
        "",
        "Headline tables use QQQ and SPY only. NQ and ES are reported separately under "
        + DEGENERATE_LABEL
        + ". "
        + DEGENERATE_NOTE,
        "",
    ]
    lines += _table("Extreme proximity overall (QQQ+SPY, after availability)", {"all": s["overall"]})
    lines += _table("By level kind (QQQ+SPY, after availability)", s["by_kind"])
    headline_roots = {k: v for k, v in (s.get("by_root") or {}).items() if k in HEADLINE_ROOTS}
    lines += _table("By root (headline QQQ+SPY, after availability)", headline_roots)
    lines += _table("By year (QQQ+SPY, after availability)", s["by_year"])
    lines += _table("By expiry bucket (QQQ+SPY, after availability)", s["by_expiry_bucket"])
    lines += _table("By session bucket of the account-day high (QQQ+SPY, after availability)", s["by_session_bucket_high"])
    lines += _table("By session bucket of the account-day low (QQQ+SPY, after availability)", s["by_session_bucket_low"])
    lines += _table("By volatility regime (QQQ+SPY, after availability)", s["by_vol_regime"])
    ra = s["root_agreement"]
    lines += _table("Root agreement versus single-root (QQQ+SPY)", {"agreeing": ra["agreeing"], "single_root": ra["single_root"]})
    degen = s.get("degenerate") or {}
    lines += [
        f"Agreeing levels: {ra['n_agreeing']}. Single-root levels: {ra['n_single']}.",
        "",
        f"## NQ and ES {DEGENERATE_LABEL}",
        "",
        DEGENERATE_NOTE,
        "",
    ]
    lines += _table(f"NQ and ES extreme proximity ({DEGENERATE_LABEL})", {"NQ+ES": degen.get("overall") or {}}, degenerate=True)
    lines += _table(f"NQ and ES by root ({DEGENERATE_LABEL})", degen.get("by_root") or {}, degenerate=True)
    lines += _table(f"NQ and ES by level kind ({DEGENERATE_LABEL})", degen.get("by_kind") or {}, degenerate=True)
    lines += [
        "## Strategy alignment outcomes (QQQ+SPY headline; NQ/ES excluded)",
        "",
    ]
    lines += _alignment_table(align)
    lines += [
        f"## Strategy alignment outcomes for NQ and ES ({DEGENERATE_LABEL})",
        "",
        "Not evidence for the futures-option levels thesis until a BBO or MBP schema is owned.",
        "",
    ]
    lines += _alignment_table(degen.get("alignment_outcomes") or {"n": 0, "n_not_applicable": 0, "not_applicable_rate": None, "unconditional_counts": {}, "by_branch_and_level": []})
    missing = payload["deviations"].get("missing_slice_dates") or []
    missing_fmt = []
    for item in missing:
        if isinstance(item, dict):
            missing_fmt.append(f"{item.get('day')}: {item.get('reason')}")
        else:
            missing_fmt.append(str(item))
    lines += [
        "## Change features",
        "",
        f"One-day matched level rows: {s['change_features']['n']}. Intraday gamma/volume rate: {s['change_features']['intraday_status']}.",
        "",
        "## Deviations from LEVEL_ATLAS.md",
        "",
        f"- B0.1 / P15-03: {payload['deviations']['b0_1_and_p15_03']}",
        f"- Extremes source: {payload['deviations']['extremes_source']}",
        f"- Census reconciliation: {recon.get('n_row_days')} row-days + {recon.get('n_missing')} listed missing = {recon.get('n_census')} census dates; identity={recon.get('identity')}.",
        f"- Missing slice dates ({len(missing_fmt)}):",
    ]
    for line in missing_fmt:
        lines.append(f"  - {line}")
    lines += [
        "",
        "## Limitations",
        "",
    ]
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines += ["", "Every numeric cell points at LEVEL_ATLAS.json rows, `extremes_sha256`, or EXPOSURE_BOARDS.json.", ""]
    return "\n".join(lines) + "\n"
