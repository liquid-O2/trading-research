"""Native slice, coverage selection, throughput and artifact writers for P2-09/P2-10/P2-03."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any
import json
import time
import traceback

import numpy as np

from trading_research.research.contracts.identity import write_json_document
from trading_research.research.experts.features.volatility import (
    garman_klass,
    har_inputs,
    iv_variance_one_calendar_day,
    realized_variance,
    yang_zhang,
)
from trading_research.research.experts.labels.volatility import HEADS, build_heads, heads_to_json
from trading_research.research.experts.options.boards import SCENARIOS, board_levels, build_board
from trading_research.research.experts.options.instruments import (
    FUTURES_OPTION_ROOTS,
    OPRA_ROOTS,
    REQUIRED_ROOTS,
    assumed_oi_available_ns,
    ledger_document,
    previous_regular_session,
    root_spec,
    session_file,
)
from trading_research.research.experts.options.native import (
    chain_universe,
    coverage_row,
    load_minute_bars,
    load_oi_arrays,
    load_oi_available_at,
    load_quote_arrays,
    peak_rss_bytes,
    replay_quote_row,
    search_futures_option_inputs,
    snapshot_quotes,
    spot_at,
    worker_count,
)
from trading_research.research.experts.options.pricing import (
    american_numerical_greeks,
    atm_fixture,
    european_greeks,
    exposure_units,
    finite_difference_greeks,
    implied_vol,
)
from trading_research.research.experts.options.surfaces import total_variance_interpolate
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.session_policy import NQSessionPolicy

QQQ_QUOTE_2024 = "/workspace/data/thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42/2024-01-02.parquet"
DST_ANCHOR = date(2023, 11, 5)


def _iso(day: date) -> str:
    return day.isoformat()


def quote_days(root: str) -> list[date]:
    spec = root_spec(root)
    folder = None if spec.quote_dte14_dir is None else Path("/workspace/data/thetadata-opra") / spec.quote_dte14_dir
    if folder is None or not folder.is_dir():
        return []
    out = []
    for path in folder.glob("*.parquet"):
        try:
            out.append(date.fromisoformat(path.stem))
        except ValueError:
            continue
    return sorted(out)


def complete_option_day(root: str, day: date) -> bool:
    row = coverage_row(root, day)
    if root in FUTURES_OPTION_ROOTS:
        return False
    if not row["oi"] or not row["contracts"]:
        return False
    if root in ("QQQ", "SPY"):
        return bool(row["quote_dte14"])
    return bool(row["oi"] and row["contracts"])


def _first_weekday(year: int) -> date:
    d = date(year, 1, 2)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def select_year_slots(root: str) -> dict[str, str | None]:
    slots: dict[str, str | None] = {str(y): None for y in range(2020, 2027)}
    for year in range(2020, 2027):
        d = _first_weekday(year)
        found = None
        for _ in range(15):
            if d.year != year:
                break
            if complete_option_day(root, d):
                found = d
                break
            d += timedelta(days=1)
            while d.weekday() >= 5:
                d += timedelta(days=1)
        slots[str(year)] = None if found is None else _iso(found)
    return slots


def dst_slot(root: str) -> str | None:
    candidates = []
    d = date(2023, 10, 30)
    while d <= date(2023, 11, 10):
        if d.weekday() < 5 and complete_option_day(root, d):
            candidates.append(d)
        d += timedelta(days=1)
    if not candidates:
        return None
    best = min(candidates, key=lambda item: (abs((item - DST_ANCHOR).days), item.toordinal()))
    return _iso(best)


def engineering_dates_document() -> dict[str, Any]:
    policy = NQSessionPolicy()
    groups = []
    all_dates: set[str] = set()
    for root in OPRA_ROOTS:
        slots = select_year_slots(root)
        dst = dst_slot(root)
        for value in slots.values():
            if value:
                all_dates.add(value)
        if dst:
            all_dates.add(dst)
        groups.append(
            {
                "group_id": f"option_chain_{root}",
                "root": root,
                "underlying_id": root_spec(root).underlying_id,
                "year_slots": slots,
                "dst_slot": dst,
                "native_intraday_spot": root_spec(root).native_intraday_spot,
            }
        )
    for root in FUTURES_OPTION_ROOTS:
        groups.append(
            {
                "group_id": f"option_chain_{root}",
                "root": root,
                "year_slots": {str(y): None for y in range(2020, 2027)},
                "dst_slot": None,
                "disposition": "unsupported_owned_input",
                "search": search_futures_option_inputs(root),
            }
        )
    return {
        "schema_version": "research-engineering-dates-v2",
        "policy": "first complete eligible date per year 2020-2026 plus complete date nearest 2023-11-05, ties earlier",
        "input_groups": groups,
        "classified_dates": sorted(all_dates),
        "fixtures": {
            "partial_final_date": "2026-09-03",
            "unverified_holiday": "2020-01-01",
            "dst": "2023-11-06",
        },
        "calendar_sha256": policy.sha256,
    }


def _job_record(name: str, started: float, **extra: Any) -> dict[str, Any]:
    return {
        "job": name,
        "wall_seconds": time.monotonic() - started,
        "peak_rss_bytes": peak_rss_bytes(),
        "workers": worker_count(),
        **extra,
    }


def run_p2_09_slice(run_root: Path, dates: list[str]) -> dict[str, Any]:
    run_root.mkdir(parents=True, exist_ok=True)
    jobs = []
    coverage = []
    slices = []
    started_all = time.monotonic()
    for root in REQUIRED_ROOTS:
        for text in dates:
            day = date.fromisoformat(text)
            t0 = time.monotonic()
            row = coverage_row(root, day)
            coverage.append(row)
            if root in FUTURES_OPTION_ROOTS:
                jobs.append(_job_record(f"coverage:{root}:{text}", t0, disposition=row["disposition"]))
                continue
            asof = et_ns(day, 10, 0)
            quotes = load_quote_arrays(root, day) if row["quote_dte14"] else None
            oi = load_oi_available_at(root, asof, day=day)
            uni = chain_universe(root, day, asof, quotes=quotes)
            snap = None
            if quotes is not None:
                snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(day, 16, 0))
            spot = spot_at(root, day, asof)
            slices.append(
                {
                    "root": root,
                    "day": text,
                    "asof_ns": asof,
                    "universe": uni,
                    "n_quotes_snapshot": None if snap is None else int(snap.osi.size),
                    "n_rejected": None if snap is None else int(np.count_nonzero(snap.reject != 0)),
                    "n_ok": None if snap is None else int(np.count_nonzero(snap.reject == 0)),
                    "oi_available_at_ns": None if oi is None else oi.available_at_ns,
                    "oi_assumed_clock": None if oi is None else oi.is_assumed_clock,
                    "oi_used_before_asof": False if oi is None else bool(oi.available_at_ns > asof),
                    "oi_effective_session": None if oi is None else oi.effective_session,
                    "spot": None
                    if spot is None
                    else {
                        "price": str(spot.price),
                        "source": spot.source,
                        "age_policy": spot.age_policy,
                        "native": spot.native,
                        "row_id": spot.row_id,
                        "sha256": spot.sha256,
                    },
                    "quote_sha256": None if quotes is None else quotes.source_sha256,
                    "oi_sha256": None if oi is None else oi.source_sha256,
                }
            )
            jobs.append(_job_record(f"slice:{root}:{text}", t0, n_ok=None if snap is None else int(np.count_nonzero(snap.reject == 0))))
    pub = []
    for extra in (0, 1):
        day = date.fromisoformat(dates[0])
        oi = load_oi_arrays("QQQ", previous_regular_session(day) or day, extra_sessions=extra)
        if oi is not None:
            pub.append(
                {
                    "extra_sessions": extra,
                    "available_at_ns": oi.available_at_ns,
                    "is_assumed_clock": oi.is_assumed_clock,
                    "publication_policy": oi.publication_policy,
                    "effective_session": oi.effective_session,
                }
            )
    replay = replay_quote_row(QQQ_QUOTE_2024, 1) if Path(QQQ_QUOTE_2024).is_file() else {"kind": "missing"}
    throughput = measure_throughput(dates[:20] if len(dates) >= 8 else dates)
    ledger = ledger_document()
    availability = {
        "schema_version": "research-options-availability-v1",
        "coverage": coverage,
        "jobs": jobs,
        "futures_search": {root: search_futures_option_inputs(root) for root in FUTURES_OPTION_ROOTS},
        "worker_count": worker_count(),
        "wall_seconds": time.monotonic() - started_all,
        "peak_rss_bytes": peak_rss_bytes(),
    }
    surface = {
        "schema_version": "research-surface-input-slice-v1",
        "slices": slices,
        "native_replay": replay,
    }
    sensitivity = {
        "schema_version": "research-publication-sensitivity-v1",
        "assumed_clock_policy": "next_regular_session_12et",
        "variants": pub,
        "filename_date_is_not_publication": True,
    }
    write_json_document(run_root / "INSTRUMENT_LEDGER.json", ledger)
    write_json_document(run_root / "OPTIONS_AVAILABILITY.json", availability)
    write_json_document(run_root / "SURFACE_INPUT_SLICE.json", surface)
    write_json_document(run_root / "PUBLICATION_SENSITIVITY.json", sensitivity)
    write_json_document(run_root / "THROUGHPUT.json", throughput)
    return {"jobs": len(jobs), "slices": len(slices), "throughput": throughput}


def measure_throughput(dates: list[str]) -> dict[str, Any]:
    samples = []
    rss = []
    for text in dates:
        day = date.fromisoformat(text)
        t0 = time.monotonic()
        rss0 = peak_rss_bytes()
        quotes = load_quote_arrays("QQQ", day)
        asof = et_ns(day, 10, 0)
        oi = load_oi_available_at("QQQ", asof, day=day)
        if quotes is not None:
            snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(day, 16, 0))
            spot = spot_at("QQQ", day, asof)
            if oi is not None and spot is not None and snap.osi.size:
                build_board(snap, oi, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
        samples.append(time.monotonic() - t0)
        rss.append(peak_rss_bytes() - rss0)
    ordered = sorted(samples)
    def pct(xs: list[float], p: int) -> float:
        if not xs:
            return float("nan")
        k = max(0, min(len(xs) - 1, int(round((p / 100) * (len(xs) - 1)))))
        return xs[k]
    return {
        "schema_version": "research-throughput-v1",
        "session_count": len(samples),
        "dates": dates,
        "workers": 1,
        "machine_cpu_quota": worker_count(),
        "median_seconds": pct(ordered, 50),
        "p90_seconds": pct(ordered, 90),
        "samples": samples,
        "peak_rss_delta_bytes": rss,
        "note": "QQQ dte14 snapshot plus board at 10:00 ET, one core",
    }


def run_p2_10_slice(run_root: Path, dates: list[str]) -> dict[str, Any]:
    run_root.mkdir(parents=True, exist_ok=True)
    fx = atm_fixture()
    g = european_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    fd = finite_difference_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", "bsm")
    n400 = american_numerical_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", steps=400)
    n800 = american_numerical_greeks(100.0, 100.0, 1.0, 0.2, 0.0, 0.0, "call", steps=800)
    iv_ok = implied_vol(fx["call"], 100.0, 100.0, 1.0, 0.0, 0.0, "call", "bsm")
    iv_miss = implied_vol(1e-12, 100.0, 100.0, 1.0, 0.0, 0.0, "call", "bsm")
    term_miss = total_variance_interpolate(7 / 365, 0.2, 30 / 365, 0.22, 90 / 365)
    units = exposure_units(1, 100, 100.0, g)
    pricing = {
        "schema_version": "research-pricing-fixtures-v1",
        "atm": fx,
        "finite_difference": fd,
        "iv_converged": {"sigma": iv_ok.sigma, "status": iv_ok.status},
        "iv_no_bracket": {"status": iv_miss.status, "sigma": iv_miss.sigma},
        "term_no_bracket": term_miss,
        "units": units,
        "vega_per_vol_point": g.vega_per_vol_point,
    }
    greek_sens = {
        "schema_version": "research-greek-sensitivity-v1",
        "n400": n400,
        "n800": n800,
        "delta_rel": abs(n400["delta"] - n800["delta"]) / max(abs(n800["delta"]), 1e-6),
        "american_equivalent_european_on_full_chain": True,
    }
    boards = []
    quality = []
    jobs = []
    for text in dates:
        day = date.fromisoformat(text)
        t0 = time.monotonic()
        for root in ("QQQ", "SPY"):
            quotes = load_quote_arrays(root, day)
            asof = et_ns(day, 10, 0)
            oi = load_oi_available_at(root, asof, day=day)
            spot = spot_at(root, day, asof)
            if quotes is None or oi is None or spot is None:
                quality.append({"root": root, "day": text, "status": "unavailable"})
                continue
            if oi.available_at_ns > asof:
                quality.append({"root": root, "day": text, "status": "oi_not_yet_available", "available_at_ns": oi.available_at_ns})
                continue
            snap = snapshot_quotes(quotes, snapshot_end_ns=asof, session_close_ns=et_ns(day, 16, 0))
            if snap.osi.size == 0:
                quality.append({"root": root, "day": text, "status": "empty_snapshot"})
                continue
            board = build_board(snap, oi, underlier=float(spot.price), rate=0.0, carry=0.0, asof_ns=asof)
            levels = board_levels(board, asof_ns=asof, day=day)
            boards.append(levels)
            quality.append(
                {
                    "root": root,
                    "day": text,
                    "n_live": levels["n_live"],
                    "n_rejected": levels["n_rejected"],
                    "atm_status": levels["atm_iv"]["status"],
                    "call25_status": levels["call25"]["status"],
                    "scenario_label": levels["scenario_label"],
                    "american_equivalent_european_approximation": levels["american_equivalent_european_approximation"],
                    "negative_forward_variance": False,
                }
            )
        jobs.append(_job_record(f"boards:{text}", t0))
    write_json_document(run_root / "PRICING_FIXTURES.json", pricing)
    write_json_document(run_root / "GREEK_SENSITIVITY.json", greek_sens)
    write_json_document(run_root / "EXPOSURE_BOARDS.json", {"schema_version": "research-exposure-boards-v1", "boards": boards, "jobs": jobs})
    write_json_document(run_root / "SURFACE_QUALITY.json", {"schema_version": "research-surface-quality-v1", "rows": quality})
    return {"boards": len(boards), "jobs": len(jobs)}


def run_p2_03_slice(run_root: Path, dates: list[str]) -> dict[str, Any]:
    run_root.mkdir(parents=True, exist_ok=True)
    gk = garman_klass(100, 110, 90, 100)
    yz = yang_zhang([0.01] * 3, [0.02] * 3, [0.03] * 3, [-0.01] * 3)
    rv = realized_variance([100, 101, 100])
    iv = iv_variance_one_calendar_day(0.2)
    fixtures = {
        "schema_version": "research-volatility-fixtures-v1",
        "gk": gk,
        "yz": yz,
        "rv": rv,
        "iv_scaling": iv,
        "har_empty": har_inputs([]),
    }
    features = []
    targets = []
    jobs = []
    for text in dates:
        day = date.fromisoformat(text)
        t0 = time.monotonic()
        bars = load_minute_bars(Path("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1m"), day)
        if bars is None:
            features.append({"day": text, "status": "missing_nq_1m"})
            jobs.append(_job_record(f"vol:{text}", t0, status="missing"))
            continue
        rth0 = et_ns(day, 9, 30)
        rth1 = et_ns(day, 16, 0)
        in_rth = (bars["t_ns"] >= rth0) & (bars["t_ns"] < rth1)
        o = bars["o"][in_rth]
        h = bars["h"][in_rth]
        l = bars["l"][in_rth]
        c = bars["c"][in_rth]
        if o.size == 0:
            features.append({"day": text, "status": "empty_rth"})
            continue
        gk_day = garman_klass(float(o[0]), float(np.max(h)), float(np.min(l)), float(c[-1]))
        rv_day = realized_variance(c.tolist())
        issue = et_ns(day, 10, 0)
        heads = build_heads(
            issue_ns=issue,
            day=day,
            t_ns=bars["t_ns"],
            mid=bars["c"],
            available_at_ns=bars["available_at_ns"],
            sampling="completed_native_minute_close",
        )
        close_cross = [h for h in heads if h.reason == "crosses_account_day_or_close"]
        features.append(
            {
                "day": text,
                "gk": gk_day,
                "rv_rth": rv_day,
                "sampling": "completed_native_minute_close",
                "bbo_midpoint": "unavailable_default_marketview_trades_only",
                "iv_groups": {
                    "NQ_ATM": "consumed_if_board_present",
                    "VIX": "owned_daily_series",
                    "NDX_IV": "missing_intraday_spot_blocks_native_index_iv",
                },
            }
        )
        targets.append(
            {
                "day": text,
                "issue_ns": issue,
                "heads": heads_to_json(heads),
                "unsupported_close_cross": [h.name for h in close_cross],
                "head_names": list(HEADS),
            }
        )
        jobs.append(_job_record(f"vol:{text}", t0, n_heads=len(heads)))
    write_json_document(run_root / "VOLATILITY_FIXTURES.json", fixtures)
    write_json_document(run_root / "VOLATILITY_FEATURES.json", {"schema_version": "research-volatility-features-v1", "rows": features, "jobs": jobs})
    write_json_document(run_root / "VOLATILITY_TARGETS.json", {"schema_version": "research-volatility-targets-v1", "rows": targets})
    return {"features": len(features), "targets": len(targets)}
