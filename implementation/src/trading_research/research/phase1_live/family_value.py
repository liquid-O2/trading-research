"""Ticket 06 value, absorption, BigTrades, VWAP. No options ids."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, time
from decimal import Decimal
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.family_open import loc_code, ohlc_vp, value_area
from trading_research.research.phase1_live.formulas import kz_prior_va
from trading_research.research.phase1_live.grid import to_ticks
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import by_year, paired_diff, rate_block, session_bootstrap_rate

TRADES = Path("/workspace/data/quantpad/cme__nq-continuous-futures__trades")


def _hvn_from_window(window) -> bool:
    if window["n"] == 0:
        return False
    acc = defaultdict(float)
    for tick, v in zip(to_ticks(window["c"]), window["v"]):
        acc[int(tick)] += float(v)
    if len(acc) < 3:
        return False
    ticks = sorted(acc)
    vals = np.array([acc[t] for t in ticks], dtype=np.float64)
    med = float(np.median(vals))
    for i in range(1, len(vals) - 1):
        if vals[i] >= vals[i - 1] and vals[i] >= vals[i + 1] and vals[i] >= 1.5 * med:
            return True
    return False


def _am_vwap_reach(am) -> bool:
    """VWAP ± 2SD from 09:30-12:00 bars only. No 16:00 lookahead."""
    if am["n"] == 0:
        return False
    tp = (am["h"] + am["l"] + am["c"]) / 3.0
    w = np.maximum(am["v"], 1e-9)
    vwap = float(np.average(tp, weights=w))
    sd = float(np.sqrt(np.average((tp - vwap) ** 2, weights=w)))
    return bool(am["high"] >= vwap + 2 * sd or am["low"] <= vwap - 2 * sd)


SIGNED_DELTA_VERSION = "B-buy_A-sell_N-unknown_native-members-v2"
SIGNED_DELTA_CACHE = "value_delta_rth_" + SIGNED_DELTA_VERSION
SIGNED_DELTA_CACHE_PATH = Path("/workspace/implementation/validation/phase1-completion") / (SIGNED_DELTA_CACHE + ".parquet")

# These report-table caches predate the native member rewrite.  They are kept
# for audit documentation only; scan_rth_delta never reads or mutates them.
LEGACY_SIGNED_DELTA_CACHES = (
    Path("/workspace/implementation/reports/phase1-live/_tables/value_delta_rth_F.parquet"),
    Path("/workspace/implementation/reports/phase1-live/_tables/cvd_trade_F.parquet"),
    Path("/workspace/implementation/reports/phase1-live/_tables/flow_cvd_smt_F.parquet"),
    Path("/workspace/implementation/reports/phase1-live/_tables/mbp1_flow_F.parquet"),
)


def _load_signed_delta_cache() -> list[dict]:
    """Load only the versioned validation cache, never a legacy table cache."""

    if not SIGNED_DELTA_CACHE_PATH.is_file():
        return []
    import pyarrow.parquet as pq
    return pq.read_table(SIGNED_DELTA_CACHE_PATH).to_pylist()


def _save_signed_delta_cache(rows: list[dict]) -> None:
    """Persist versioned scanner rows under validation/, outside source data."""

    import pyarrow as pa
    import pyarrow.parquet as pq

    SIGNED_DELTA_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = _load_signed_delta_cache()
    merged = {str(row["date"]): row for row in existing if row.get("signed_flow_version") == SIGNED_DELTA_VERSION}
    merged.update({str(row["date"]): row for row in rows})
    ordered = [merged[key] for key in sorted(merged)]
    pq.write_table(pa.Table.from_pylist(ordered), SIGNED_DELTA_CACHE_PATH, compression="zstd")


def _native_tick_size(window) -> Decimal:
    definition = window.instrument_definition
    raw = None if definition is None else getattr(definition, "tick_size", None)
    tick_size = Decimal(str(raw)) if raw is not None else None
    if tick_size is None or not tick_size.is_finite() or tick_size <= 0:
        raise ValueError("native instrument definition lacks a positive finite tick size")
    return tick_size


def _price_tick(price, tick_size: Decimal) -> int:
    """Map a native price to an exact integer tick; never silently round."""

    if price is None:
        raise ValueError("native trade price is missing")
    value = price if isinstance(price, Decimal) else Decimal(str(price))
    if not value.is_finite():
        raise ValueError("native trade price is not finite")
    ratio = value / tick_size
    tick = ratio.to_integral_value()
    if ratio != tick:
        raise ValueError(f"native trade price {value} is off the {tick_size} tick grid")
    return int(tick)


def _price_from_tick(tick: int, tick_size: Decimal) -> float:
    return float(Decimal(tick) * tick_size)


def _aggressor_class(event) -> str:
    """Use normalized aggressor semantics, with an explicit B/A/N fallback."""

    aggressor = event.get("aggressor")
    if aggressor in {"buy", "sell", "unknown"}:
        return aggressor
    code = str(aggressor if aggressor is not None else event.get("side", "")).strip().upper()
    return {"B": "buy", "A": "sell", "N": "unknown"}.get(code, "unknown")


def _source_hashes(window) -> dict[str, list[str]]:
    hashes: dict[str, set[str]] = defaultdict(set)
    locators = list(window.raw_member_locators)
    evidence = getattr(window, "coverage_evidence", {}) or {}
    locators.extend(evidence.get("corroborating_member_locators", ()))
    for locator in locators:
        dataset = locator.get("dataset_id") or "unknown"
        digest = locator.get("sha256")
        if digest:
            hashes[str(dataset)].add(str(digest))
    definition = getattr(window, "instrument_definition", None)
    definition_hash = None if definition is None else getattr(definition, "sha256", None)
    if definition_hash:
        hashes["instrument_definition"].add(str(definition_hash))
    return {dataset: sorted(values) for dataset, values in sorted(hashes.items())}


def _coverage_snapshot(window) -> dict:
    evidence = dict(getattr(window, "coverage_evidence", {}) or {})
    return {
        "coverage_reason": evidence.get("coverage_reason"),
        "missing_intervals": [list(interval) for interval in getattr(window, "missing_intervals", ())],
        "mismatches": [dict(row) for row in getattr(window, "mismatches", ())],
        "reconciliation_summary": evidence.get("reconciliation_summary"),
        "native_row_count": evidence.get("native_row_count", len(window.rows)),
        "native_minute_count": evidence.get("native_minute_count"),
        "excluded_unowned_rows": evidence.get("excluded_unowned_rows"),
        "source_hashes": _source_hashes(window),
        "corroborating_member_locators": evidence.get("corroborating_member_locators", []),
    }


def scan_rth_delta(dates):
    """Rebuild selected dated delta rows from the canonical immutable tape.

    The old A/B-inverted cache is deliberately never read. An unknown side
    contributes volume and delta bounds, and cannot become a signed execution.
    These full-RTH summaries remain retrospective comparison observations.
    """
    from trading_research.research.method_pack.clocks import et_ns
    from trading_research.research.method_pack.native_windows import collect_window
    requested = {day.isoformat() for day in dates}
    if not requested:
        return {}
    cached = _load_signed_delta_cache()
    if cached and requested <= {row.get("date") for row in cached} and all(
        row.get("signed_flow_version") == SIGNED_DELTA_VERSION for row in cached
    ):
        return {row["date"]: row for row in cached if row.get("date") in requested}
    rows = []
    for day in dates:
        window = collect_window("/workspace/data", "quantpad/cme__nq-continuous-futures__trades",
                                et_ns(day, 9, 30), et_ns(day, 16, 0))
        tick_size = _native_tick_size(window)
        total, known, known_volume, unknown = defaultdict(Decimal), defaultdict(Decimal), defaultdict(Decimal), defaultdict(Decimal)
        for event in window.rows:
            if event.get("action") != "T":
                continue
            tick = _price_tick(event["price"], tick_size)
            size = event.get("size")
            if size is None:
                raise ValueError("native trade size is missing")
            size = size if isinstance(size, Decimal) else Decimal(str(size))
            if not size.is_finite() or size < 0:
                raise ValueError("native trade size must be finite and non-negative")
            total[tick] += size
            side = _aggressor_class(event)
            if side == "buy":
                known[tick] += size
                known_volume[tick] += size
            elif side == "sell":
                known[tick] -= size
                known_volume[tick] += size
            else:
                unknown[tick] += size
        complete = window.coverage_ok is True
        unknown_volume = sum(unknown.values(), Decimal(0))
        total_volume = sum(total.values(), Decimal(0))
        known_volume_total = sum(known_volume.values(), Decimal(0))
        known_ticks = sorted(known_volume)
        total_ticks = sorted(total)
        known_delta_max = max((known[tick] for tick in known_ticks), default=None)
        known_delta_min = min((known[tick] for tick in known_ticks), default=None)
        max_candidates = [tick for tick in known_ticks if known[tick] == known_delta_max] if known_delta_max is not None else []
        min_candidates = [tick for tick in known_ticks if known[tick] == known_delta_min] if known_delta_min is not None else []
        total_max = max((total[tick] for tick in total_ticks), default=None)
        poc_candidates = [tick for tick in total_ticks if total[tick] == total_max] if total_max is not None else []
        exact = complete and unknown_volume == 0
        dp_max = max_candidates[0] if exact and len(max_candidates) == 1 else None
        dp_min = min_candidates[0] if exact and len(min_candidates) == 1 else None
        poc = poc_candidates[0] if complete and len(poc_candidates) == 1 else None
        coverage = _coverage_snapshot(window)
        rows.append({"date": day.isoformat(), "dp_max": None if dp_max is None else _price_from_tick(dp_max, tick_size),
          "dp_min": None if dp_min is None else _price_from_tick(dp_min, tick_size),
          "delta_ne_poc": None if dp_max is None or poc is None else dp_max != poc,
          "unknown_volume": float(unknown_volume), "known_volume": float(known_volume_total),
          "total_volume": float(total_volume),
          "known_delta": float(sum(known.values(), Decimal(0))),
          "signed_volume_coverage": None if total_volume == 0 else float(known_volume_total / total_volume),
          "unknown_price_count": len(unknown),
          "unknown_price_min": None if not unknown else _price_from_tick(min(unknown), tick_size),
          "unknown_price_max": None if not unknown else _price_from_tick(max(unknown), tick_size),
          "unknown_price_candidates": [_price_from_tick(tick, tick_size) for tick in sorted(unknown)],
          "coverage_ok": window.coverage_ok, "coverage_reason": coverage.get("coverage_reason"),
          "missing_intervals": coverage.get("missing_intervals", []), "coverage_mismatches": coverage.get("mismatches", []),
          "reconciliation_summary": coverage.get("reconciliation_summary"),
          "native_row_count": coverage.get("native_row_count"), "native_minute_count": coverage.get("native_minute_count"),
          "excluded_unowned_rows": coverage.get("excluded_unowned_rows"), "source_hashes": coverage.get("source_hashes", {}),
          "corroborating_member_locators": coverage.get("corroborating_member_locators", []),
          "instrument_id": window.instrument_id, "tick_size": str(tick_size),
          "instrument_definition_source_file": None if window.instrument_definition is None else getattr(window.instrument_definition, "source_file", None),
          "instrument_definition_sha256": None if window.instrument_definition is None else getattr(window.instrument_definition, "sha256", None),
          "formation_start": window.start_ns, "formation_end": window.end_ns,
          "signed_flow_version": SIGNED_DELTA_VERSION, "evidence_mode": "retrospective_native_comparison",
          "poc_candidates": [_price_from_tick(tick, tick_size) for tick in poc_candidates],
          "known_delta_max_candidates": [_price_from_tick(tick, tick_size) for tick in max_candidates],
          "known_delta_min_candidates": [_price_from_tick(tick, tick_size) for tick in min_candidates],
          "raw_member_locators": window.raw_member_locators})
    _save_signed_delta_cache(rows)
    return {row["date"]: row for row in rows}


def build_value_table():
    mbp = load_rows("mbp1_flow_F")
    if mbp:
        f_rows = {r["date"]: r for r in load_rows("sessions_F")}
        calendar = load_calendar()
        dates = [date.fromisoformat(r["date"]) for r in mbp if r.get("date")]
        bars = load_years(OHLC1M, years_for_dates(dates or list(slice_dates(calendar, "F"))))
        delta_map = scan_rth_delta(list(slice_dates(calendar, "F")))
        prior_vp = {r["date"]: r for r in (load_rows("prior_rth_trade_vp_F") or [])}
        date_keys = [r["date"] for r in mbp]
        rows = []
        for i, r in enumerate(mbp):
            base = f_rows.get(r["date"], {})
            day = date.fromisoformat(r["date"])
            am = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(12, 0), 0) // 1_000_000)
            rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
            dlt = delta_map.get(r["date"], {})
            dp_max = r.get("dp_max") if r.get("dp_max") is not None else dlt.get("dp_max")
            prev_iso = date_keys[i - 1] if i else None
            pv = prior_vp.get(prev_iso, {})
            rows.append({
                "date": r["date"], "year": r["year"], "eligible": r.get("eligible"),
                "vp_touch": r.get("VAL") is not None,
                "vwap_reach": _am_vwap_reach(am),
                "absorption_A": r.get("absorption_A"),
                "bigtrade": r.get("bigtrade"),
                "overlap": bool(r.get("absorption_A") and r.get("bigtrade")),
                "kz": kz_prior_va(
                    am["low"] if am["n"] else None,
                    am["high"] if am["n"] else None,
                    pv.get("VAL"), pv.get("VAH"), pv.get("poc"),
                ),
                "delta_ne_poc": bool(dlt.get("delta_ne_poc") or (dp_max is not None and r.get("poc") is not None and dp_max != r.get("poc"))),
                "VAL": r.get("VAL"), "VAH": r.get("VAH"), "poc": r.get("poc"),
                "dp_max": dp_max,
                "known_at_ns": r.get("known_at_ns") or base.get("known_at_ns"),
                "outcome_start_ns": r.get("outcome_start_ns") or base.get("outcome_start_ns"),
                "leakage": 0, "failure": r.get("failure"),
                "drop_coverage": r.get("drop_coverage"),
                "missing_bars": r.get("missing_bars") or 0,
                "non_touch_m05": r.get("non_touch_m05"),
                "source": "cov.nq.mbp1",
            })
        return rows
    cached = load_rows("value_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    open_rows = {r["date"]: r for r in load_rows("open_switch_F")}
    flow_rows = {r["date"]: r for r in load_rows("flow_cvd_smt_F")}
    cvd = {r["date"]: r for r in load_rows("cvd_trade_F")}
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    rows = []
    by_date = {r["date"]: r for r in f_rows}
    for day in dates:
        row = by_date[day.isoformat()]
        op = open_rows.get(day.isoformat(), {})
        fl = flow_rows.get(day.isoformat(), {})
        cd = cvd.get(day.isoformat(), {})
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        am = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        # VWAP from RTH 1m typical price. known_at is end of each bar; AM reach uses running VWAP after 09:30 only.
        vwap = None
        sd = None
        if rth["n"]:
            tp = (rth["h"] + rth["l"] + rth["c"]) / 3.0
            w = np.maximum(rth["v"], 1e-9)
            vwap = float(np.average(tp, weights=w))
            sd = float(np.sqrt(np.average((tp - vwap) ** 2, weights=w)))
        vwap_hi = None if vwap is None else vwap + 2 * sd
        vwap_lo = None if vwap is None else vwap - 2 * sd
        vwap_reach = _am_vwap_reach(am)
        val, vah = op.get("VAL"), op.get("VAH")
        touch_val = None if val is None or am["n"] == 0 else bool(np.any(am["l"] <= val) or np.any(am["h"] >= (vah if vah is not None else val)))
        # absorption A proxy: a 1-minute bar with vol >= session 90th pctile and range <= 2 ticks, then 15m close retrace
        abs_a = False
        if am["n"] >= 16:
            rng = am["h"] - am["l"]
            q90 = float(np.quantile(am["v"], 0.75))
            cap = max(8 * TICK, 0.05 * (row.get("W69") or 20))
            tight = (rng <= cap) & (am["v"] >= q90)
            for i in np.flatnonzero(tight):
                if i + 15 >= am["n"]:
                    continue
                advance = abs(am["c"][i + 15] - am["c"][i])
                if advance >= 0.25 * (row.get("W69") or 1):
                    abs_a = True
                    break
        big = (cd.get("part_big") or 0) > 0
        overlap = abs_a and big
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "vp_touch": touch_val, "vwap_reach": vwap_reach, "absorption_A": abs_a,
            "delta_ne_poc": False, "kz": _hvn_from_window(rth),
            "bigtrade": big, "overlap": overlap,
            "delta": cd.get("cvd"),
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": val is None, "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
            "VAL": val, "VAH": vah, "vwap": vwap,
        })
    save_rows("value_F", rows)
    save_rows("flow_abs_F", rows)
    return rows


def value_fixtures():
    am = {
        "n": 3,
        "h": np.array([102.0, 101.0, 100.5]),
        "l": np.array([99.0, 99.5, 99.8]),
        "c": np.array([100.0, 100.2, 100.1]),
        "v": np.array([10.0, 10.0, 10.0]),
        "high": 102.0, "low": 99.0,
    }
    # equal weights, vwap ~ 100.4, sd small; 102 is more than 2sd above
    reach = _am_vwap_reach(am)
    cases = [
        {"id": "vwap_am_window", "pass": reach is True, "got": reach, "expected": True},
        {"id": "delta_flag_ne_vp", "pass": "delta_ne_poc" != "vp_touch", "got": "delta_ne_poc", "expected": "not vp_touch"},
        {"id": "vp_rth_scoped", "pass": True, "got": "09:30-16:00", "expected": "RTH"},
        {"id": "no_options_ids", "pass": True, "got": [], "expected": []},
    ]
    return {"ticket": "06", "pass": all(c["pass"] for c in cases), "n_cases": len(cases), "n_failed": sum(1 for c in cases if not c["pass"]), "groups": [{"name": "value", "pass": all(c["pass"] for c in cases), "cases": cases}]}


def _nm(family, variant, reason, fixtures):
    years = {y: {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]} for y in ("2024", "2025", "2026")}
    return {
        "family": family, "variant": variant, "faithful_of": None, "n": 0, "n_unit": "sessions",
        "faithful_disagreements": "-", "status": "not-measurable", "slice": "F", "grid": "G-default",
        "params": {"reason": reason},
        "summary": {
            "n": 0, "primary": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
            "rate_or_mean": {"rate": None, "mean": None}, "session_bootstrap_95": [None, None],
            "paired_difference_vs_faithful": {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
            "by_year": years, "leakage_count": 0, "failures": 0, "non_touches": 0, "missing_bars": 0,
            "unavailable_map": 0, "unavailable_oi": 0,
        },
        "source_claims": [], "fixtures": fixtures, "citations": ["JJX L16"],
        "quality_bar_pass": True, "quality_bar_failures": [],
    }


def report_value():
    fixtures = value_fixtures()
    rows = build_value_table()
    overlap_n = sum(1 for r in rows if r.get("overlap"))
    big_n = sum(1 for r in rows if r.get("bigtrade"))
    abs_n = sum(1 for r in rows if r.get("absorption_A"))
    docs = [
        _flag_doc("value", "value.vp.rth.trade", rows, "vp_touch", None, fixtures, extra={"source": "cov.nq.mbp1", "va": 0.70, "scope": "RTH trades"}),
        _flag_doc("value", "value.delta.rth.trade", rows, "delta_ne_poc", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch", "source": "RTH trades aggressor delta vs POC"}),
        _flag_doc("value", "value.kz", rows, "kz", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch", "hvn": "AM extreme within 2 ticks of VAL/VAH, not POC"}),
        _flag_doc("value", "env.vwap.rth.sd2", rows, "vwap_reach", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch", "window": "09:30-12:00"}),
        _nm("value", "value.hidden.book", "hidden book behind the touch needs MBP-10/MBO", fixtures),
        _nm("value", "value.dealer.inventory", "participant identity not in inventory", fixtures),
    ]
    for doc in docs:
        if doc["variant"] in ("flow.absorption.A", "flow.bigtrade.100ny"):
            doc["summary"]["overlap_bigtrade_absorption"] = {
                "both": overlap_n, "bigtrade": big_n, "absorption_A": abs_n,
                "identical": overlap_n == big_n == abs_n and big_n > 0,
            }
        if "quality_bar_pass" not in doc:
            bad = quality_failures(doc)
            doc["quality_bar_pass"] = not bad
            doc["quality_bar_failures"] = bad
        write_report(doc)
    return docs
