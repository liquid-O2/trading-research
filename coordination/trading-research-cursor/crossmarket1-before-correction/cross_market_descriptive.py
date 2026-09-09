"""Cross-market descriptive measurements, tables, and date-weighted statistics.

Source events are selected before outcomes. Receiver futures are labelled
only after source availability. This is an observed minute-price branch:
not Context, not Location/node quality, and not a full-family claim.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
import math
import resource
import time as time_mod

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import MINUTE
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries
from trading_research.research.cross_market_alignment import (
    BASELINE_LATENCY_S, CANONICAL_ROOTS, DIRECTED_PAIRS, FAMILY,
    LATENCY_AFTER_END_S, LOOKBACKS, PROTOCOL_KIND, REFERENCE_LOOKBACKS,
    VERSION as ALIGN_VERSION, PriorCarry, UnitBars, canonical_partitions_for_year,
    ceil_to_minute, close_to_close_logreturn, confirmed_pivots, contemporaneous_ratio,
    freeze_previous_closing_ratio, futures_session_bounds, grid_cuts,
    intended_cash_dates, lagged_mapping_residual, last_available,
    load_canonical_unit, load_cash_calendar, load_daily_observational,
    load_raw_unit, lookback_extrema, mapping_chain_for, ny_wall_minute,
    running_breaches, running_references, selected_year_list, session_label,
    session_log_rv, stage_of, unit_quality_row, year_date_bounds,
)
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.physical_ohlc_volatility import excursion_down_log, excursion_up_log
from trading_research.research.scoring import quantile


VERSION = "cross-market-descriptive-acquired-v1"
PURPOSE = (
    "acquired-minute-price-alignment-and-descriptive-timing; "
    "not a Context forecast or Location/node evaluation"
)
FUTURE_HORIZONS = (1, 5, 15, 30, 60)
STAT_QUANTILES = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
STAT_SEED = 20260908
STAT_BLOCK = 5
STAT_REPLICATES = 1000
STAT_CONFIDENCE = 0.95
STAT_MIN_DATES = 100
STAT_MIN_EVENTS = 20
CHUNK = 65536

_NP = None


def _np():
    global _NP
    if _NP is None:
        import numpy as np
        _NP = np
    return _NP


def _pa():
    import pyarrow as pa
    return pa


def require_protocol(protocol):
    if not isinstance(protocol, dict):
        raise ContractError("protocol must be the frozen cross-market contract")
    if protocol.get("kind") != PROTOCOL_KIND or protocol.get("version") != 1:
        raise IntegrityError("frozen cross-market contract kind/version changed")
    if protocol.get("family") != FAMILY:
        raise IntegrityError("frozen cross-market family identity changed")
    return protocol


def require_admitted(admitted):
    if not isinstance(admitted, dict) or admitted.get("kind") != "cross_market_admitted_sources_v1":
        raise ContractError("admitted sources must be kind cross_market_admitted_sources_v1")
    if not isinstance(admitted.get("sources"), list):
        raise ContractError("admitted sources list required")
    return admitted


def log_ratio(numerator, denominator):
    if numerator is None or denominator is None:
        return None
    if not (numerator > 0.0 and denominator > 0.0):
        return None
    if not (math.isfinite(numerator) and math.isfinite(denominator)):
        return None
    return math.log(numerator / denominator)


def excursion_bundle(reference, future_high, future_low, future_close):
    terminal = log_ratio(future_close, reference)
    up = excursion_up_log(future_high, reference)
    down = excursion_down_log(future_low, reference)
    path_range = None
    if up is not None and down is not None:
        path_range = up + down
    return {
        "terminal_log": terminal,
        "up_log": up,
        "down_log": down,
        "path_range_log": path_range,
        "terminal_sign": None if terminal is None else (0 if terminal == 0.0 else (1 if terminal > 0.0 else -1)),
        "zero_reaction": terminal == 0.0 if terminal is not None else False,
    }


def concordance(source_direction: int, terminal_sign):
    if terminal_sign is None or source_direction == 0:
        return "undefined"
    if terminal_sign == 0:
        return "zero_receiver"
    if source_direction == terminal_sign:
        return "concordant"
    return "discordant"


def date_cells_for_ci(date_sums: dict, date_counts: dict) -> dict:
    cells = {}
    for day, total in date_sums.items():
        count = int(date_counts.get(day, 0))
        if count <= 0 or total is None:
            continue
        mean = float(total) / float(count)
        cells[day] = (mean,) * count
    return cells


def independent_date_support(variant_dates: dict) -> dict:
    """Primary and original NQ2024 keep separate universes; dates are not doubled."""
    primary = set()
    original = set()
    for variant, dates in variant_dates.items():
        bucket = original if variant == "original_nq2024_sensitivity" else primary
        bucket.update(dates)
    return {
        "primary_dates": len(primary),
        "original_nq2024_dates": len(original),
        "union_if_wrongly_pooled": len(primary | original),
        "independent_support_if_doubled": len(primary) + len(original),
        "doubled": False,
    }


def future_window(unit: UnitBars, label_start_ns: int, horizon_minutes: int):
    np = _np()
    end_ns = label_start_ns + int(horizon_minutes) * MINUTE
    lo = int(np.searchsorted(unit.start_ns, label_start_ns, side="left"))
    hi = int(np.searchsorted(unit.start_ns, end_ns, side="left"))
    expected = int(horizon_minutes)
    reasons = []
    if hi <= lo:
        return {"status": "no_receiver", "reasons": ("missing_all_minutes",), "open": None,
                "high": None, "low": None, "close": None, "count": 0}
    if int(unit.start_ns[lo]) != label_start_ns:
        reasons.append("missing_first_minute")
    if hi - lo != expected:
        reasons.append("minute_count_mismatch")
    if not bool(np.all(unit.valid[lo:hi])):
        reasons.append("invalid_source_minutes")
    if hi - lo > 1:
        if not bool(np.all(unit.start_ns[lo + 1:hi] == unit.start_ns[lo:hi - 1] + MINUTE)):
            reasons.append("missing_interior_minutes")
        if not bool(np.all(unit.instrument_id[lo:hi] == unit.instrument_id[lo])):
            reasons.append("raw_contract_transition")
    if lo > 0 and int(unit.instrument_id[lo]) != int(unit.instrument_id[lo - 1]):
        if "raw_contract_transition" not in reasons and hi > lo:
            pass
    status = "complete" if not reasons else "censored"
    if "raw_contract_transition" in reasons:
        status = "roll"
    if "missing_all_minutes" in reasons or (not reasons and hi <= lo):
        status = "no_receiver"
    if reasons and status == "complete":
        status = "censored"
    if not reasons:
        return {
            "status": "complete",
            "reasons": (),
            "open": float(unit.open[lo]),
            "high": float(np.max(unit.high[lo:hi])),
            "low": float(np.min(unit.low[lo:hi])),
            "close": float(unit.close[hi - 1]),
            "count": hi - lo,
            "instrument_id": int(unit.instrument_id[lo]),
        }
    return {
        "status": status,
        "reasons": tuple(reasons),
        "open": None, "high": None, "low": None, "close": None,
        "count": hi - lo,
        "instrument_id": int(unit.instrument_id[lo]) if hi > lo else None,
    }


def pair_timing_rows(left, right):
    """Pair lag scenarios only when the same event, anchor, and receiver reference match."""
    if left["event_id"] != right["event_id"]:
        return {"pairing": "unpaired", "reason": "different_event"}
    if left["horizon_minutes"] != right["horizon_minutes"]:
        return {"pairing": "unpaired", "reason": "different_horizon"}
    if left.get("receiver_variant") != right.get("receiver_variant"):
        return {"pairing": "unpaired", "reason": "different_receiver_variant"}
    if left.get("anchor_ns") != right.get("anchor_ns"):
        return {"pairing": "unpaired", "reason": "different_anchor"}
    if left.get("source_start_ns") != right.get("source_start_ns"):
        return {"pairing": "unpaired", "reason": "different_source_bar"}
    left_ref = left.get("receiver_ref_start_ns")
    right_ref = right.get("receiver_ref_start_ns")
    if left_ref is None or right_ref is None:
        return {
            "pairing": "own_only",
            "reason": "missing_receiver_reference",
            "reference_change": left_ref != right_ref,
        }
    if left_ref != right_ref:
        return {
            "pairing": "reference_change",
            "reason": "lag_changed_receiver_reference",
            "reference_change": True,
            "common_reference": False,
        }
    contrast = None
    if left.get("terminal_log") is not None and right.get("terminal_log") is not None:
        contrast = right["terminal_log"] - left["terminal_log"]
    return {
        "pairing": "common_reference",
        "reason": None,
        "reference_change": False,
        "common_reference": True,
        "terminal_contrast": contrast,
    }


def _i64(pa, name, nullable=True):
    return pa.field(name, pa.int64(), nullable=nullable)


def _f64(pa, name, nullable=True):
    return pa.field(name, pa.float64(), nullable=nullable)


def _str(pa, name, nullable=True):
    return pa.field(name, pa.string(), nullable=nullable)


def _bool(pa, name, nullable=True):
    return pa.field(name, pa.bool_(), nullable=nullable)


def aligned_cut_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "source_symbol"), _str(pa, "receiver_symbol"), _str(pa, "source_variant"),
        _str(pa, "receiver_variant"), _i64(pa, "cut_ns"), _i64(pa, "lag_s"),
        _i64(pa, "source_start_ns"), _i64(pa, "source_end_ns"), _i64(pa, "source_known_at_ns"),
        _i64(pa, "source_age_ns"), _str(pa, "source_join"), _f64(pa, "source_close"),
        _f64(pa, "source_volume"), _str(pa, "source_volume_unit"), _i64(pa, "source_instrument_id"),
        _i64(pa, "source_file_id"), _i64(pa, "receiver_start_ns"), _i64(pa, "receiver_known_at_ns"),
        _i64(pa, "receiver_age_ns"), _str(pa, "receiver_join"), _f64(pa, "receiver_close"),
        _i64(pa, "receiver_instrument_id"), _bool(pa, "own_coverage"), _bool(pa, "common_coverage"),
        _bool(pa, "definition_certified"),
    ])


def lookback_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "symbol"), _str(pa, "variant"), _i64(pa, "cut_ns"), _i64(pa, "lag_s"),
        _i64(pa, "lookback_minutes"), _i64(pa, "bar_start_ns"), _f64(pa, "log_return"),
        _f64(pa, "intervening_high"), _f64(pa, "intervening_low"),
        _f64(pa, "relative_volume"), _f64(pa, "prior_rth_sqrt_rv"),
        _str(pa, "status"), _str(pa, "volume_unit"), _i64(pa, "file_id"),
    ])


def smt_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "source_symbol"), _str(pa, "receiver_symbol"),
        _str(pa, "source_variant"), _str(pa, "receiver_variant"),
        _i64(pa, "cut_ns"), _i64(pa, "lag_s"), _i64(pa, "lookback_minutes"),
        _str(pa, "kind"), _bool(pa, "source_own_breach_high"), _bool(pa, "source_own_breach_low"),
        _bool(pa, "receiver_own_breach_high"), _bool(pa, "receiver_own_breach_low"),
        _f64(pa, "source_prior_high"), _f64(pa, "source_prior_low"),
        _f64(pa, "receiver_prior_high"), _f64(pa, "receiver_prior_low"),
        _f64(pa, "source_close"), _f64(pa, "receiver_close"),
        _str(pa, "breach_state"), _bool(pa, "common_cut"),
    ])


def mapping_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "futures_symbol"), _str(pa, "etf_symbol"), _str(pa, "variant"),
        _i64(pa, "cut_ns"), _i64(pa, "lag_s"),
        _f64(pa, "contemporaneous_ratio"), _f64(pa, "contemporaneous_inverse"),
        _f64(pa, "prior_ratio"), _f64(pa, "predicted_receiver"),
        _f64(pa, "residual_receiver_points"), _str(pa, "status"), _str(pa, "reason"),
        _bool(pa, "prior_ratio_frozen"),
    ])


def event_label_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "event_id"), _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"),
        _str(pa, "session"), _str(pa, "source_symbol"), _str(pa, "receiver_symbol"),
        _str(pa, "source_variant"), _str(pa, "receiver_variant"),
        _str(pa, "event_kind"), _i64(pa, "lookback_minutes"), _i64(pa, "direction"),
        _i64(pa, "source_start_ns"), _i64(pa, "source_end_ns"), _i64(pa, "source_known_at_ns"),
        _i64(pa, "anchor_ns"), _i64(pa, "label_start_ns"), _i64(pa, "horizon_minutes"),
        _i64(pa, "lag_s"), _i64(pa, "receiver_ref_start_ns"), _f64(pa, "receiver_ref_close"),
        _f64(pa, "source_close"), _f64(pa, "past_receiver_log"),
        _f64(pa, "terminal_log"), _f64(pa, "up_log"), _f64(pa, "down_log"),
        _f64(pa, "path_range_log"), _i64(pa, "terminal_sign"), _str(pa, "concordance"),
        _str(pa, "future_status"), _str(pa, "future_reasons"),
        _bool(pa, "zero_reaction"), _bool(pa, "no_receiver"),
        _str(pa, "local_node_presence"), _i64(pa, "source_file_id"),
        _i64(pa, "source_instrument_id"), _i64(pa, "receiver_instrument_id"),
    ])


def contrast_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "event_id"), _str(pa, "date"), _str(pa, "source_symbol"),
        _str(pa, "receiver_symbol"), _i64(pa, "horizon_minutes"),
        _i64(pa, "lag_a_s"), _i64(pa, "lag_b_s"), _str(pa, "pairing"),
        _str(pa, "reason"), _bool(pa, "reference_change"), _bool(pa, "common_reference"),
        _f64(pa, "terminal_a"), _f64(pa, "terminal_b"), _f64(pa, "terminal_contrast"),
        _str(pa, "kind"),
    ])


def date_aggregate_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "source_symbol"), _str(pa, "receiver_symbol"), _str(pa, "variant"),
        _str(pa, "metric"), _f64(pa, "sum"), _i64(pa, "event_count"), _f64(pa, "date_mean"),
        _i64(pa, "horizon_minutes"), _i64(pa, "lag_s"), _i64(pa, "lookback_minutes"),
        _str(pa, "event_kind"),
    ])


def daily_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _str(pa, "symbol"), _str(pa, "role"),
        _f64(pa, "close"), _f64(pa, "adjusted_close"),
        _f64(pa, "raw_log_return"), _f64(pa, "adjusted_log_return"),
        _f64(pa, "dividend"), _f64(pa, "split_ratio"), _str(pa, "action_labels"),
        _i64(pa, "known_at_ns"), _bool(pa, "causal_feature_eligible"),
        _str(pa, "clock"), _bool(pa, "in_primary_cohort"), _i64(pa, "file_id"),
    ])


class _SeriesWriter:
    def __init__(self, outputs: BoundedOutputs, name: str, schema):
        self.schema = schema
        self.columns = {field.name: [] for field in schema}
        self.series = ParquetSeries(outputs, name, maximum_rows_per_file=CHUNK)
        self.rows = 0

    def add(self, row: dict):
        for name, values in self.columns.items():
            values.append(row.get(name))
        self.rows += 1
        if len(self.columns[self.schema[0].name]) >= CHUNK:
            self.flush()

    def flush(self):
        pa = _pa()
        n = len(self.columns[self.schema[0].name])
        if n == 0:
            return
        arrays = []
        for field in self.schema:
            arrays.append(pa.array(self.columns[field.name], type=field.type))
            self.columns[field.name].clear()
        self.series.append(pa.Table.from_arrays(arrays, schema=self.schema))

    def finish(self):
        self.flush()
        if self.rows == 0:
            pa = _pa()
            empty = pa.Table.from_arrays(
                [pa.array([], type=field.type) for field in self.schema], schema=self.schema)
            self.series.append(empty)
        return self.series.finish()


def _empty_group():
    return {"sum": defaultdict(float), "count": defaultdict(int)}


def _add_cell(store, key, day: str, value):
    if value is None or not math.isfinite(float(value)):
        return
    store[key]["sum"][day] += float(value)
    store[key]["count"][day] += 1


def _finite(value):
    if value is None:
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _distribution(values):
    numbers = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not numbers:
        return {"count": 0, "mean": None, **{f"q{int(q * 100):02d}": None for q in STAT_QUANTILES}}
    return {
        "count": len(numbers),
        "mean": math.fsum(numbers) / len(numbers),
        **{f"q{int(q * 100):02d}": quantile(numbers, q) for q in STAT_QUANTILES},
    }


def _compact_stat(result):
    for metric in result.get("metrics", {}).values():
        metric.get("bootstrap", {}).pop("replicate_estimates", None)
    for ratio in result.get("ratios", {}).values():
        ratio.get("bootstrap", {}).pop("replicate_estimates", None)
    return result


def summarize_groups(groups: dict, intended_by_key: dict) -> dict:
    out = {}
    for key, payload in groups.items():
        intended = intended_by_key.get(key)
        if not intended:
            continue
        cells = date_cells_for_ci(payload["sum"], payload["count"])
        if not cells:
            out[key] = {
                "status": "undefined",
                "reason": "no_matches",
                "actual_valid_event_count": 0,
                "actual_valid_date_count": 0,
            }
            continue
        stats = _compact_stat(observed_date_statistics(
            {"value": cells}, intended,
            estimator="date_mean", seed=STAT_SEED, block_length=STAT_BLOCK,
            replicates=STAT_REPLICATES, confidence=STAT_CONFIDENCE,
            minimum_independent_dates=STAT_MIN_DATES, minimum_events=STAT_MIN_EVENTS,
            _retain_replicate_estimates=False,
        ))
        metric = stats["metrics"]["value"]
        means = []
        for day in intended:
            count = payload["count"].get(day, 0)
            if count:
                means.append(payload["sum"][day] / count)
        out[key] = {
            "statistics": metric,
            "distribution_date_means": _distribution(means),
            "actual_valid_event_count": metric["actual_valid_event_count"],
            "actual_valid_date_count": metric["actual_valid_date_count"],
            "support": metric["support"],
        }
    return out


def _event_id(symbol, variant, start_ns, kind, lookback, direction, anchor_ns):
    return f"{symbol}|{variant}|{start_ns}|{kind}|{lookback}|{direction}|{anchor_ns}"


def _bar_state(unit: UnitBars):
    lookbacks = {}
    for length in LOOKBACKS:
        ret, ret_ok = close_to_close_logreturn(unit.close, unit.start_ns, unit.instrument_id, unit.valid, length)
        hi, lo, ext_ok = None, None, None
        if length in REFERENCE_LOOKBACKS or length in LOOKBACKS:
            hi, lo, ext_ok = running_references(
                unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, length
            ) if length in REFERENCE_LOOKBACKS else (None, None, None)
        xhi, xlo, xok = lookback_extrema(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, length)
        lookbacks[length] = {
            "log_return": ret, "log_defined": ret_ok,
            "prior_high": hi, "prior_low": lo, "prior_defined": ext_ok,
            "intervening_high": xhi, "intervening_low": xlo, "intervening_defined": xok,
        }
    running = {}
    for length in REFERENCE_LOOKBACKS:
        prior_high, prior_low, defined = running_references(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, length)
        high_b, low_b = running_breaches(unit.high, unit.low, prior_high, prior_low, defined)
        running[length] = {
            "prior_high": prior_high, "prior_low": prior_low, "defined": defined,
            "high_breach": high_b, "low_breach": low_b,
        }
    return {
        "lookbacks": lookbacks,
        "running": running,
        "pivot": confirmed_pivots(
            unit.high, unit.low, unit.start_ns, unit.instrument_id, unit.valid, unit.known_at_ns),
    }


def _join_row(unit: UnitBars, cut_ns: int, lag_s: int):
    index, status = last_available(unit, cut_ns, latency_after_end_s=lag_s)
    if index is None:
        return {
            "index": None, "join": status, "start_ns": None, "end_ns": None,
            "known_at_ns": None, "age_ns": None, "close": None, "volume": None,
            "instrument_id": None, "high": None, "low": None,
        }
    known = int(unit.known_for(lag_s)[index])
    end = int(unit.end_ns[index])
    return {
        "index": index,
        "join": status,
        "start_ns": int(unit.start_ns[index]),
        "end_ns": end,
        "known_at_ns": known,
        "age_ns": int(cut_ns) - end,
        "close": float(unit.close[index]) if unit.valid[index] else None,
        "volume": float(unit.volume[index]) if unit.valid[index] else None,
        "instrument_id": int(unit.instrument_id[index]),
        "high": float(unit.high[index]) if unit.valid[index] else None,
        "low": float(unit.low[index]) if unit.valid[index] else None,
    }


def _breach_state(src_high, src_low, rcv_high, rcv_low) -> str:
    source = bool(src_high or src_low)
    receiver = bool(rcv_high or rcv_low)
    if source and receiver:
        return "both"
    if source:
        return "source_only"
    if receiver:
        return "receiver_only"
    return "neither"


def overlapping_cash_days(units: dict, calendar, year: int):
    days = intended_cash_dates(calendar, *year_date_bounds(year))
    spans = [(int(unit.start_ns[0]), int(unit.start_ns[-1]) + MINUTE)
             for unit in units.values() if len(unit)]
    if not spans:
        return days
    lo = min(span[0] for span in spans)
    hi = max(span[1] for span in spans)
    out = []
    for cash in days:
        start, end, _ = futures_session_bounds(cash, calendar.zone)
        if start is None or end is None:
            continue
        if end > lo and start < hi:
            out.append(cash)
    return out


def process_year(*, year: int, units: dict, calendar, writers: dict, groups: dict,
                 intended_dates: list, carry: dict, variant_dates: dict):
    states = {key: _bar_state(unit) for key, unit in units.items()}
    cash_days = overlapping_cash_days(units, calendar, year)
    year_dates = [cash.day.isoformat() for cash in cash_days]
    for cash in cash_days:
        intended_dates.append(cash.day.isoformat())
        day = cash.day.isoformat()
        stage = stage_of(cash.day) or "outside_primary"
        sess_start, sess_end, _ = futures_session_bounds(cash, calendar.zone)
        cuts = grid_cuts(int(sess_start), int(sess_end), GRID_MINUTES)
        day_volumes = {key: {} for key in units}
        for cut in cuts.tolist():
            cut = int(cut)
            session = session_label(cut, cash, calendar.zone)
            joined = {}
            for key, unit in units.items():
                for lag in LATENCY_AFTER_END_S:
                    joined[(key, lag)] = _join_row(unit, cut, lag)
            for (source_symbol, receiver_symbol) in DIRECTED_PAIRS:
                for source_key, source in units.items():
                    if source.symbol != source_symbol:
                        continue
                    for receiver_key, receiver in units.items():
                        if receiver.symbol != receiver_symbol:
                            continue
                        if source.variant == "original_nq2024_sensitivity" and receiver.variant != source.variant:
                            if receiver.symbol not in CANONICAL_ROOTS:
                                continue
                        if (receiver.variant == "original_nq2024_sensitivity"
                                and source.variant != receiver.variant
                                and source.symbol in CANONICAL_ROOTS):
                            continue
                        variant_dates.setdefault(source.variant, set()).add(day)
                        for lag in LATENCY_AFTER_END_S:
                            src = joined[(source_key, lag)]
                            rcv = joined[(receiver_key, lag)]
                            own = src["join"] in ("fresh", "stale")
                            common = src["join"] == "fresh" and rcv["join"] == "fresh"
                            writers["cuts"].add({
                                "date": day, "year": year, "stage": stage, "session": session,
                                "source_symbol": source.symbol, "receiver_symbol": receiver.symbol,
                                "source_variant": source.variant, "receiver_variant": receiver.variant,
                                "cut_ns": cut, "lag_s": lag,
                                "source_start_ns": src["start_ns"], "source_end_ns": src["end_ns"],
                                "source_known_at_ns": src["known_at_ns"], "source_age_ns": src["age_ns"],
                                "source_join": src["join"], "source_close": src["close"],
                                "source_volume": src["volume"], "source_volume_unit": source.volume_unit,
                                "source_instrument_id": src["instrument_id"], "source_file_id": source.file_id,
                                "receiver_start_ns": rcv["start_ns"], "receiver_known_at_ns": rcv["known_at_ns"],
                                "receiver_age_ns": rcv["age_ns"], "receiver_join": rcv["join"],
                                "receiver_close": rcv["close"], "receiver_instrument_id": rcv["instrument_id"],
                                "own_coverage": own, "common_coverage": common,
                                "definition_certified": source.definition_certified,
                            })
                            _add_cell(groups, ("coverage_own", year, stage, session, source.symbol,
                                               source.variant, None, lag, None, None),
                                      day, 1.0 if own else 0.0)
                            _add_cell(groups, ("coverage_common", year, stage, session, source.symbol,
                                               receiver.symbol, source.variant, lag, None, None),
                                      day, 1.0 if common else 0.0)
                            chain = mapping_chain_for(source.symbol, receiver.symbol)
                            if chain and src["join"] == "fresh" and rcv["join"] == "fresh":
                                futures_symbol, etf_symbol = chain
                                fut = rcv if receiver.symbol == futures_symbol else src
                                etf = src if source.symbol == etf_symbol else rcv
                                if receiver.symbol == futures_symbol and source.symbol == etf_symbol:
                                    fut, etf = rcv, src
                                elif source.symbol == futures_symbol and receiver.symbol == etf_symbol:
                                    fut, etf = src, rcv
                                else:
                                    fut = etf = None
                                if fut is not None and etf["close"] and fut["close"]:
                                    ratio = contemporaneous_ratio(fut["close"], etf["close"])
                                    prior = carry.get("ratio", {}).get((futures_symbol, etf_symbol, source.variant))
                                    mapped = lagged_mapping_residual(
                                        prior_receiver_close=None if prior is None else prior["receiver_close"],
                                        prior_source_close=None if prior is None else prior["source_close"],
                                        current_source=etf["close"],
                                        current_receiver=fut["close"],
                                    ) if prior is not None else {
                                        "ratio": None, "predicted_receiver": None,
                                        "residual_receiver_points": None, "status": "undefined",
                                        "reason": "previous_day_missing",
                                    }
                                    writers["mapping"].add({
                                        "date": day, "year": year, "stage": stage, "session": session,
                                        "futures_symbol": futures_symbol, "etf_symbol": etf_symbol,
                                        "variant": source.variant, "cut_ns": cut, "lag_s": lag,
                                        "contemporaneous_ratio": None if ratio is None else ratio["ratio"],
                                        "contemporaneous_inverse": None if ratio is None else ratio["inverse"],
                                        "prior_ratio": mapped.get("ratio"),
                                        "predicted_receiver": mapped.get("predicted_receiver"),
                                        "residual_receiver_points": mapped.get("residual_receiver_points"),
                                        "status": mapped.get("status"), "reason": mapped.get("reason"),
                                        "prior_ratio_frozen": True,
                                    })
                                    _add_cell(groups, ("mapping_residual", year, stage, session,
                                                       futures_symbol, etf_symbol, source.variant,
                                                       lag, None, None),
                                              day, mapped.get("residual_receiver_points"))
                            for length in REFERENCE_LOOKBACKS:
                                src_idx = src["index"]
                                rcv_idx = rcv["index"]
                                src_run = states[source_key]["running"][length]
                                rcv_run = states[receiver_key]["running"][length]
                                src_h = bool(src_idx is not None and src_run["high_breach"][src_idx])
                                src_l = bool(src_idx is not None and src_run["low_breach"][src_idx])
                                rcv_h = bool(rcv_idx is not None and rcv_run["high_breach"][rcv_idx])
                                rcv_l = bool(rcv_idx is not None and rcv_run["low_breach"][rcv_idx])
                                writers["smt"].add({
                                    "date": day, "year": year, "stage": stage, "session": session,
                                    "source_symbol": source.symbol, "receiver_symbol": receiver.symbol,
                                    "source_variant": source.variant, "receiver_variant": receiver.variant,
                                    "cut_ns": cut, "lag_s": lag, "lookback_minutes": length,
                                    "kind": "running",
                                    "source_own_breach_high": src_h, "source_own_breach_low": src_l,
                                    "receiver_own_breach_high": rcv_h, "receiver_own_breach_low": rcv_l,
                                    "source_prior_high": None if src_idx is None else _finite(src_run["prior_high"][src_idx]),
                                    "source_prior_low": None if src_idx is None else _finite(src_run["prior_low"][src_idx]),
                                    "receiver_prior_high": None if rcv_idx is None else _finite(rcv_run["prior_high"][rcv_idx]),
                                    "receiver_prior_low": None if rcv_idx is None else _finite(rcv_run["prior_low"][rcv_idx]),
                                    "source_close": src["close"], "receiver_close": rcv["close"],
                                    "breach_state": _breach_state(src_h, src_l, rcv_h, rcv_l),
                                    "common_cut": src["join"] == "fresh" and rcv["join"] == "fresh",
                                })
            for key, unit in units.items():
                for lag in LATENCY_AFTER_END_S:
                    row = joined[(key, lag)]
                    if row["index"] is None:
                        continue
                    index = row["index"]
                    day_volumes[key][ny_wall_minute(int(unit.start_ns[index]), calendar.zone)] = float(unit.volume[index])
                    carry_unit = carry.setdefault("rel", {}).setdefault(key, PriorCarry())
                    for length in LOOKBACKS:
                        lb = states[key]["lookbacks"][length]
                        rel, rel_reason = (None, "not_fresh")
                        if row["join"] == "fresh":
                            rel, rel_reason = carry_unit.relative_volume(
                                ny_wall_minute(int(unit.start_ns[index]), calendar.zone),
                                float(unit.volume[index]))
                        writers["lookbacks"].add({
                            "date": day, "year": year, "stage": stage, "session": session,
                            "symbol": unit.symbol, "variant": unit.variant, "cut_ns": cut,
                            "lag_s": lag, "lookback_minutes": length,
                            "bar_start_ns": row["start_ns"],
                            "log_return": _finite(lb["log_return"][index]) if lb["log_defined"][index] else None,
                            "intervening_high": _finite(lb["intervening_high"][index]) if lb["intervening_defined"][index] else None,
                            "intervening_low": _finite(lb["intervening_low"][index]) if lb["intervening_defined"][index] else None,
                            "relative_volume": rel,
                            "prior_rth_sqrt_rv": carry_unit.prior_rth_scale(),
                            "status": "defined" if lb["log_defined"][index] else (rel_reason or "undefined"),
                            "volume_unit": unit.volume_unit, "file_id": unit.file_id,
                        })
        _emit_source_events(
            units, states, cash, day, year, stage, writers, groups, carry, calendar,
        )
        for key, unit in units.items():
            rth_start, rth_end, reason = None, None, None
            if cash.state != "closed":
                rth_start, rth_end, reason = cash.open_at, cash.close_at, None
            rv, complete = (None, False)
            if rth_start is not None:
                rv, complete = session_log_rv(
                    unit.close, unit.start_ns, unit.instrument_id, unit.valid, rth_start, rth_end)
            carry.setdefault("rel", {}).setdefault(key, PriorCarry()).push_day(
                cash.day, day_volumes.get(key, {}), rv, complete)
            for receiver_key, receiver in units.items():
                chain = mapping_chain_for(unit.symbol, receiver.symbol)
                if chain is None:
                    continue
                futures_symbol, etf_symbol = chain
                src = unit if unit.symbol == etf_symbol else receiver
                rcv = receiver if receiver.symbol == futures_symbol else unit
                if src.symbol != etf_symbol or rcv.symbol != futures_symbol:
                    continue
                frozen = freeze_previous_closing_ratio(src, rcv, cash)
                if frozen is not None:
                    carry.setdefault("ratio", {})[(futures_symbol, etf_symbol, unit.variant)] = frozen
    return year_dates


def _emit_source_events(units, states, cash, day, year, stage, writers, groups, carry, calendar):
    sess_start, sess_end, _ = futures_session_bounds(cash, calendar.zone)
    pending = []
    for source_key, source in units.items():
        lo, hi = source.slice_session(int(sess_start), int(sess_end))
        state = states[source_key]
        for index in range(lo, hi):
            if not source.valid[index]:
                continue
            session = session_label(int(source.start_ns[index]), cash, calendar.zone)
            for length in REFERENCE_LOOKBACKS:
                running = state["running"][length]
                pivot = state["pivot"]
                events = []
                if running["high_breach"][index]:
                    events.append(("running_high", 1, int(source.start_ns[index]), length))
                if running["low_breach"][index]:
                    events.append(("running_low", -1, int(source.start_ns[index]), length))
                if pivot["high_breach"][index] and length == 15:
                    events.append(("pivot_high", 1, int(pivot["high_formed_ns"][index]), length))
                if pivot["low_breach"][index] and length == 15:
                    events.append(("pivot_low", -1, int(pivot["low_formed_ns"][index]), length))
                for kind, direction, anchor_ns, lookback in events:
                    source_known = int(source.known_at_ns[index])
                    event_id = _event_id(source.symbol, source.variant, int(source.start_ns[index]),
                                         kind, lookback, direction, anchor_ns)
                    for receiver_key, receiver in units.items():
                        if receiver.symbol not in ("NQ", "ES"):
                            continue
                        if source.symbol == receiver.symbol and source.variant == receiver.variant:
                            if (source.symbol, receiver.symbol) not in DIRECTED_PAIRS:
                                continue
                        if (source.symbol, receiver.symbol) not in DIRECTED_PAIRS:
                            continue
                        if source.variant == "original_nq2024_sensitivity" and receiver.variant != source.variant:
                            if receiver.symbol not in CANONICAL_ROOTS:
                                continue
                        lag_rows = {}
                        for lag in LATENCY_AFTER_END_S:
                            event_known = int(source.known_for(lag)[index])
                            label_start = ceil_to_minute(event_known)
                            rcv_i, rcv_st = last_available(receiver, event_known, latency_after_end_s=lag)
                            ref_start = ref_close = past = None
                            no_receiver = rcv_i is None or rcv_st != "fresh"
                            if rcv_i is not None and rcv_st == "fresh":
                                ref_start = int(receiver.start_ns[rcv_i])
                                ref_close = float(receiver.close[rcv_i])
                                past_i, _ = last_available(
                                    receiver, int(source.start_ns[index]), latency_after_end_s=lag)
                                if past_i is not None and receiver.close[past_i] > 0 and ref_close > 0:
                                    past = log_ratio(ref_close, float(receiver.close[past_i]))
                            for horizon in FUTURE_HORIZONS:
                                window = {"status": "no_receiver", "reasons": ("no_receiver",),
                                          "high": None, "low": None, "close": None}
                                if not no_receiver:
                                    window = future_window(receiver, label_start, horizon)
                                bundle = excursion_bundle(ref_close, window.get("high"), window.get("low"),
                                                          window.get("close"))
                                future_status = window["status"] if not no_receiver else "no_receiver"
                                if no_receiver:
                                    future_status = "no_receiver"
                                row = {
                                    "event_id": event_id, "date": day, "year": year, "stage": stage,
                                    "session": session, "source_symbol": source.symbol,
                                    "receiver_symbol": receiver.symbol, "source_variant": source.variant,
                                    "receiver_variant": receiver.variant, "event_kind": kind,
                                    "lookback_minutes": lookback, "direction": direction,
                                    "source_start_ns": int(source.start_ns[index]),
                                    "source_end_ns": int(source.end_ns[index]),
                                    "source_known_at_ns": event_known, "anchor_ns": anchor_ns,
                                    "label_start_ns": label_start, "horizon_minutes": horizon,
                                    "lag_s": lag, "receiver_ref_start_ns": ref_start,
                                    "receiver_ref_close": ref_close, "source_close": float(source.close[index]),
                                    "past_receiver_log": past,
                                    "terminal_log": bundle["terminal_log"], "up_log": bundle["up_log"],
                                    "down_log": bundle["down_log"], "path_range_log": bundle["path_range_log"],
                                    "terminal_sign": bundle["terminal_sign"],
                                    "concordance": concordance(direction, bundle["terminal_sign"]),
                                    "future_status": future_status,
                                    "future_reasons": "|".join(window.get("reasons") or ()),
                                    "zero_reaction": bundle["zero_reaction"],
                                    "no_receiver": bool(no_receiver or future_status == "no_receiver"),
                                    "local_node_presence": None,
                                    "source_file_id": source.file_id,
                                    "source_instrument_id": int(source.instrument_id[index]),
                                    "receiver_instrument_id": None if rcv_i is None else int(receiver.instrument_id[rcv_i]),
                                }
                                writers["events"].add(row)
                                lag_rows.setdefault(horizon, {})[lag] = row
                                _add_cell(groups, ("terminal_log", year, stage, session, source.symbol,
                                                   receiver.symbol, source.variant, lag, horizon, kind),
                                          day, bundle["terminal_log"])
                                _add_cell(groups, ("concordant", year, stage, session, source.symbol,
                                                   receiver.symbol, source.variant, lag, horizon, kind),
                                          day, 1.0 if row["concordance"] == "concordant" else (
                                              0.0 if row["concordance"] in ("discordant", "zero_receiver") else None))
                        for horizon, by_lag in lag_rows.items():
                            if 60 in by_lag and 0 in by_lag:
                                paired = pair_timing_rows(by_lag[60], by_lag[0])
                                writers["contrasts"].add({
                                    "event_id": event_id, "date": day, "source_symbol": source.symbol,
                                    "receiver_symbol": receiver.symbol, "horizon_minutes": horizon,
                                    "lag_a_s": 60, "lag_b_s": 0, "pairing": paired["pairing"],
                                    "reason": paired.get("reason"),
                                    "reference_change": bool(paired.get("reference_change")),
                                    "common_reference": bool(paired.get("common_reference")),
                                    "terminal_a": by_lag[60].get("terminal_log"),
                                    "terminal_b": by_lag[0].get("terminal_log"),
                                    "terminal_contrast": paired.get("terminal_contrast"),
                                    "kind": "timing_lag",
                                })
                            if 60 in by_lag and 120 in by_lag:
                                paired = pair_timing_rows(by_lag[60], by_lag[120])
                                writers["contrasts"].add({
                                    "event_id": event_id, "date": day, "source_symbol": source.symbol,
                                    "receiver_symbol": receiver.symbol, "horizon_minutes": horizon,
                                    "lag_a_s": 60, "lag_b_s": 120, "pairing": paired["pairing"],
                                    "reason": paired.get("reason"),
                                    "reference_change": bool(paired.get("reference_change")),
                                    "common_reference": bool(paired.get("common_reference")),
                                    "terminal_a": by_lag[60].get("terminal_log"),
                                    "terminal_b": by_lag[120].get("terminal_log"),
                                    "terminal_contrast": paired.get("terminal_contrast"),
                                    "kind": "timing_lag",
                                })
                    if source.symbol in ("NQ", "ES"):
                        continue
            pivot = state["pivot"]
            running15 = state["running"][15]
            if (running15["high_breach"][index] or running15["low_breach"][index]
                    or pivot["high_breach"][index] or pivot["low_breach"][index]):
                pending.append(index)
    return pending


def _write_daily(writer, cash_rows, action_rows):
    for row in cash_rows:
        writer.add({
            "date": row["date"], "symbol": row["symbol"], "role": "daily_cash",
            "close": row.get("close"), "adjusted_close": row.get("adjusted_close"),
            "raw_log_return": row.get("raw_log_return"),
            "adjusted_log_return": row.get("adjusted_log_return"),
            "dividend": None, "split_ratio": None, "action_labels": None,
            "known_at_ns": None, "causal_feature_eligible": False,
            "clock": "date_only", "in_primary_cohort": row.get("in_primary_cohort"),
            "file_id": row.get("file_id"),
        })
    for row in action_rows:
        writer.add({
            "date": row["date"], "symbol": row["symbol"], "role": "corporate_actions",
            "close": None, "adjusted_close": None, "raw_log_return": None,
            "adjusted_log_return": None, "dividend": row.get("dividend"),
            "split_ratio": row.get("split_ratio"), "action_labels": row.get("action_labels"),
            "known_at_ns": None, "causal_feature_eligible": False,
            "clock": "date_only", "in_primary_cohort": row.get("in_primary_cohort"),
            "file_id": row.get("file_id"),
        })


def _write_date_aggregates(writer, groups):
    for key, payload in groups.items():
        metric, year, stage, session, source, receiver, variant, lag, horizon, kind = key
        days = set(payload["sum"]) | set(payload["count"])
        for day in sorted(days):
            count = int(payload["count"].get(day, 0))
            total = payload["sum"].get(day, 0.0)
            writer.add({
                "date": day, "year": year, "stage": stage, "session": session,
                "source_symbol": source, "receiver_symbol": receiver, "variant": variant,
                "metric": metric, "sum": total, "event_count": count,
                "date_mean": None if count == 0 else total / count,
                "horizon_minutes": horizon, "lag_s": lag, "lookback_minutes": None,
                "event_kind": kind,
            })


def _group_intended(groups, all_dates, calendar_dates_by_year_stage):
    intended = {}
    for key in groups:
        year, stage = key[1], key[2]
        universe = calendar_dates_by_year_stage.get((year, stage))
        if universe is None:
            universe = [day for day in all_dates if stage_of(date.fromisoformat(day)) == stage
                        and date.fromisoformat(day).year == year]
        intended[key] = universe
    return intended


def write_results_md(counts, statistics, resources, refs, quality, support) -> str:
    lines = [
        "# Cross-market alignment descriptive results",
        "",
        "Observed minute-price branch only. `full_family_complete` is false.",
        "No Context fit, Location evaluation, or node-quality claim.",
        "",
        "## Scope",
        "",
        f"- Family: `{FAMILY}`",
        f"- Alignment: `{ALIGN_VERSION}`; descriptive: `{VERSION}`",
        f"- Purpose: {PURPOSE}",
        f"- Years processed: {counts.get('years')}",
        f"- Intended cash dates: {counts.get('intended_dates')}",
        f"- Directed pairs: {len(DIRECTED_PAIRS)}",
        f"- Latency scenarios after bar end (seconds): {list(LATENCY_AFTER_END_S)}",
        "",
        "## Selected numeric findings",
        "",
        f"- Minute units: {counts.get('units')}",
        f"- Aligned cut rows: {counts.get('aligned_cuts')}",
        f"- Lookback rows: {counts.get('lookbacks')}",
        f"- Price SMT rows: {counts.get('smt')}",
        f"- Mapping rows: {counts.get('mapping')}",
        f"- Source-event/receiver-label rows: {counts.get('events')}",
        f"- Timing/pivot contrast rows: {counts.get('contrasts')}",
        f"- Daily observational rows: {counts.get('daily')}",
        f"- Valid minute bars: {counts.get('valid_bars')}",
        f"- Invalid/quarantined minute bars: {counts.get('invalid_bars')}",
        "",
    ]
    if quality:
        lines.append("## Source quality")
        lines.append("")
        for row in quality:
            lines.append(
                f"- `{row['symbol']}` {row['variant']} {row['year']}: "
                f"{row['valid_rows']}/{row['rows']} valid; unit={row['volume_unit']}; "
                f"definition_certified={row['definition_certified']}"
            )
        lines.append("")
    lines.append("## Date-weighted statistics")
    lines.append("")
    lines.append("Each date has weight one. Event counts remain the raw observation counts.")
    lines.append("Unsupported cells stay undefined; they are not filled with artificial support.")
    lines.append("")
    shown = 0
    for key, block in statistics.items():
        if shown >= 24:
            break
        metric = block.get("statistics") or {}
        support_row = block.get("support") or {}
        estimate = metric.get("estimate")
        events = block.get("actual_valid_event_count")
        dates_n = block.get("actual_valid_date_count")
        lower = (metric.get("bootstrap") or {}).get("lower")
        upper = (metric.get("bootstrap") or {}).get("upper")
        sparse = support_row.get("sparse")
        lines.append(
            f"- `{key}`: estimate={estimate}; dates={dates_n}; events={events}; "
            f"CI=[{lower}, {upper}]; sparse={sparse}"
        )
        shown += 1
    if not statistics:
        lines.append("- No grouped statistic met a defined cell.")
    lines.append("")
    lines.append("## Resources")
    lines.append("")
    for row in resources.get("per_year") or ():
        lines.append(
            f"- Year {row['year']}: cpu_s={row['cpu_seconds']:.6f}; "
            f"wall_s={row['wall_seconds']:.6f}; output_bytes={row['output_bytes']}"
        )
    lines.append(
        f"- Total cpu_s={resources.get('cpu_seconds')}; wall_s={resources.get('wall_seconds')}; "
        f"output_bytes={resources.get('output_bytes')}"
    )
    lines.append("")
    lines.append("## Full tables")
    lines.append("")
    for name, ref in refs.items():
        if isinstance(ref, dict) and "path" in ref:
            lines.append(f"- `{name}`: `{ref['path']}` sha256=`{ref.get('sha256')}` bytes={ref.get('size_bytes')}")
        elif isinstance(ref, dict) and ref.get("files"):
            lines.append(f"- `{name}`: {ref.get('rows')} rows in {len(ref['files'])} parquet files")
        else:
            lines.append(f"- `{name}`: retained")
    lines.append("")
    lines.append("## Explicit non-claims")
    lines.append("")
    lines.append("- Daily cash/actions have null verified known_at; next-open availability is not invented.")
    lines.append("- `local_node_presence` is null because a node catalog is not an input.")
    lines.append("- Bar close is not an execution fill.")
    lines.append("- Current-ratio zero residual is not mapping validation.")
    lines.append("- Original NQ 2024 is a separate paired sensitivity, not doubled independent dates.")
    lines.append("- Options, flow SMT, NKD/HG/SI, Context, and Location remain separate branches.")
    lines.append("")
    return "\n".join(lines) + "\n"


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (date,)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    return value


def run(*, protocol: dict, admitted: dict, store, outputs: BoundedOutputs,
        selected_years: list[int] | None = None, fixture_units: dict | None = None,
        fixture_daily=None) -> dict:
    started_cpu = time_mod.process_time()
    started_wall = time_mod.perf_counter()
    protocol = require_protocol(protocol)
    if fixture_units is None:
        admitted = require_admitted(admitted)
    calendar = load_cash_calendar(protocol)
    years = selected_year_list(selected_years)
    maximum_bytes = int((protocol.get("resources") or {}).get("maximum_source_file_bytes") or 67_108_864)
    writers = {
        "cuts": _SeriesWriter(outputs, "aligned-cuts", aligned_cut_schema()),
        "lookbacks": _SeriesWriter(outputs, "lookbacks", lookback_schema()),
        "smt": _SeriesWriter(outputs, "price-smt", smt_schema()),
        "mapping": _SeriesWriter(outputs, "mapping-errors", mapping_schema()),
        "events": _SeriesWriter(outputs, "source-event-labels", event_label_schema()),
        "contrasts": _SeriesWriter(outputs, "lag-contrasts", contrast_schema()),
        "date_agg": _SeriesWriter(outputs, "date-aggregates", date_aggregate_schema()),
        "daily": _SeriesWriter(outputs, "daily-cash-actions", daily_schema()),
    }
    groups = defaultdict(_empty_group)
    quality = []
    intended_all = []
    variant_dates = {}
    carry = {"rel": {}, "ratio": {}}
    partition_measurements = []
    valid_bars = invalid_bars = 0
    if fixture_daily is None and fixture_units is None:
        cash_rows, action_rows = load_daily_observational(admitted, maximum_bytes=maximum_bytes)
    else:
        cash_rows, action_rows = fixture_daily or ([], [])
    _write_daily(writers["daily"], cash_rows, action_rows)
    for year in years:
        year_cpu = time_mod.process_time()
        year_wall = time_mod.perf_counter()
        written0 = outputs.written
        units = {}
        if fixture_units is not None:
            for key, unit in fixture_units.items():
                if unit.year is None or int(unit.year) == int(year):
                    units[key] = unit
        else:
            for partition in canonical_partitions_for_year(protocol, year):
                unit = load_canonical_unit(store, partition)
                units[(unit.symbol, unit.variant, unit.year)] = unit
            for item in require_admitted(admitted)["sources"]:
                source = item["source"]
                if source.get("role") != "minute_ohlcv" or source.get("year") != year:
                    continue
                if source["symbol"] in CANONICAL_ROOTS:
                    continue
                unit = load_raw_unit(item, maximum_bytes=maximum_bytes)
                units[(unit.symbol, unit.variant, unit.year)] = unit
        if not units:
            partition_measurements.append({
                "year": year, "cpu_seconds": time_mod.process_time() - year_cpu,
                "wall_seconds": time_mod.perf_counter() - year_wall,
                "output_bytes": outputs.written - written0, "units": 0,
            })
            continue
        for unit in units.values():
            quality.append(unit_quality_row(unit))
            valid_bars += int(unit.valid.sum())
            invalid_bars += int((~unit.valid).sum())
        process_year(
            year=year, units=units, calendar=calendar, writers=writers, groups=groups,
            intended_dates=intended_all, carry=carry, variant_dates=variant_dates,
        )
        partition_measurements.append({
            "year": year,
            "cpu_seconds": time_mod.process_time() - year_cpu,
            "wall_seconds": time_mod.perf_counter() - year_wall,
            "output_bytes": outputs.written - written0,
            "units": len(units),
            "max_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        })
    _write_date_aggregates(writers["date_agg"], groups)
    calendar_dates_by_year_stage = {}
    unique_dates = sorted(set(intended_all))
    for day in unique_dates:
        parsed = date.fromisoformat(day)
        key = (parsed.year, stage_of(parsed) or "outside_primary")
        calendar_dates_by_year_stage.setdefault(key, []).append(day)
    intended_map = _group_intended(groups, unique_dates, calendar_dates_by_year_stage)
    statistics = summarize_groups(groups, intended_map)
    refs = {}
    counts = {
        "years": years,
        "intended_dates": len(unique_dates),
        "units": len(quality),
        "valid_bars": valid_bars,
        "invalid_bars": invalid_bars,
        "daily_cash": len(cash_rows),
        "corporate_actions": len(action_rows),
    }
    for name, writer in writers.items():
        refs[name] = writer.finish()
        counts[{"cuts": "aligned_cuts", "date_agg": "date_aggregates"}.get(name, name)] = writer.rows
    support = independent_date_support(variant_dates)
    resources = {
        "cpu_seconds": time_mod.process_time() - started_cpu,
        "wall_seconds": time_mod.perf_counter() - started_wall,
        "output_bytes": outputs.written,
        "per_year": partition_measurements,
    }
    report = write_results_md(counts, statistics, resources, refs, quality, support)
    with outputs.create("results.md") as stream:
        stream.write(report.encode())
    refs["results_md"] = outputs.reference("results.md", kind="cross_market_results_markdown_v1")
    stats_ref = outputs.json("statistics.json", _jsonable({
        "kind": "cross_market_date_statistics_v1",
        "seed": STAT_SEED, "block_length": STAT_BLOCK, "replicates": STAT_REPLICATES,
        "confidence": STAT_CONFIDENCE, "groups": {str(k): v for k, v in statistics.items()},
        "independent_date_support": support,
    }), kind="cross_market_statistics_v1")
    refs["statistics"] = stats_ref
    quality_ref = outputs.json("source-quality.json", quality, kind="cross_market_source_quality_v1")
    refs["source_quality"] = quality_ref
    manifest = {
        "kind": "cross_market_completeness_manifest_v1",
        "family": FAMILY,
        "alignment_version": ALIGN_VERSION,
        "descriptive_version": VERSION,
        "full_family_complete": False,
        "scope": "observed-minute-price-branch",
        "purpose": PURPOSE,
        "years": years,
        "intended_dates": unique_dates,
        "tables": {name: ({"rows": ref.get("rows"), "files": len(ref.get("files") or ())}
                          if isinstance(ref, dict) and "files" in ref else ref)
                   for name, ref in refs.items()},
        "excluded_branches": [
            "options_chain_flow_greeks", "flow_smt", "native_NKD_HG_SI",
            "slow_publication", "Context_models", "Location_node_quality",
        ],
        "local_node_presence": None,
        "daily_known_at": None,
        "original_nq2024_not_doubled": True,
        "independent_date_support": support,
    }
    refs["completeness"] = outputs.json(
        "completeness.json", manifest, kind="cross_market_completeness_manifest_v1")
    return {
        "passed": True,
        "refs": refs,
        "counts": counts,
        "resources": resources,
        "partition_measurements": partition_measurements,
        "full_family_complete": False,
        "family": FAMILY,
        "version": VERSION,
        "purpose": PURPOSE,
    }


__all__ = (
    "FAMILY", "FUTURE_HORIZONS", "PURPOSE", "VERSION",
    "concordance", "date_cells_for_ci", "excursion_bundle", "future_window",
    "independent_date_support", "pair_timing_rows", "run", "summarize_groups",
)
