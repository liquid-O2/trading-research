"""Cross-market descriptive measurements, compact tables, and date-weighted statistics.

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
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_series_tables
from trading_research.research.cross_market_alignment import (
    DIRECTED_PAIRS, FAMILY, FUTURE_HORIZONS, GRID_MINUTES,
    LATENCY_AFTER_END_S, LOOKBACKS, MAPPING_CHAINS, PROTOCOL_KIND, REFERENCE_LOOKBACKS,
    VERSION as ALIGN_VERSION, PriorCarry, UnitBars, canonical_partitions_for_year,
    backward_join_indices, ceil_to_minute, contemporaneous_ratio, directed_unit_pairs,
    economic_minute_volumes, freeze_previous_closing_ratio, futures_session_bounds,
    grid_cuts, intended_cash_dates, join_status_name, lagged_mapping_residual,
    last_available, load_canonical_unit, load_cash_calendar, load_daily_observational,
    load_raw_unit, lookup_future_window, ny_wall_minute,
    prepare_unit, priced_ok, previous_intended_date, selected_year_list, session_label,
    session_log_rv, stage_of, stages_aligned_for_ci, unit_quality_row, unit_stable_key,
    year_date_bounds,
)
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.physical_ohlc_volatility import excursion_down_log, excursion_up_log
from trading_research.research.scoring import quantile


VERSION = "cross-market-descriptive-acquired-v1"
PURPOSE = (
    "acquired-minute-price-alignment-and-descriptive-timing; "
    "not a Context forecast or Location/node evaluation"
)
STAT_QUANTILES = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
STAT_SEED = 20260908
STAT_BLOCK = 5
STAT_REPLICATES = 1000
STAT_CONFIDENCE = 0.95
STAT_MIN_DATES = 100
STAT_MIN_EVENTS = 20
CHUNK = 65536
SESSIONS = ("cash_rth", "pre_rth", "other_futures")
EVENT_KINDS = ("running_high", "running_low", "pivot_high", "pivot_low")
PATH_METRICS = ("terminal_log", "up_log", "down_log", "path_range_log",
                "past_formation_log", "past_preavailability_log")
LIFE_METRICS = ("zero_reaction", "no_priced", "no_receiver", "missing", "stale",
                "roll", "censor", "source_events_total", "concordant_nonzero", "zero_receiver")
FEATURE_METRICS = ("lookback_logret", "relative_volume", "coverage_own_eligible",
                   "coverage_own_observed", "coverage_own_stale", "coverage_common")
SMT_METRICS = ("smt_source_only", "smt_receiver_only", "smt_both", "smt_neither",
               "smt_unknown", "smt_source_excursion")

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
    path_range = log_ratio(future_high, future_low)
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
    """One date-mean float per date. Restore raw event counts after CI."""
    cells = {}
    for day, total in date_sums.items():
        count = int(date_counts.get(day, 0))
        if count <= 0 or total is None:
            continue
        cells[day] = float(total) / float(count)
    return cells


def restore_event_counts(metric: dict, date_counts: dict) -> dict:
    raw_events = int(sum(int(count) for count in date_counts.values()))
    raw_dates = int(sum(1 for count in date_counts.values() if int(count) > 0))
    metric["actual_valid_event_count"] = raw_events
    metric["actual_valid_date_count"] = raw_dates
    support = metric.get("support")
    if isinstance(support, dict):
        support["events"] = raw_events
        support["independent_dates"] = raw_dates
        reasons = []
        if raw_dates < STAT_MIN_DATES:
            reasons.append("fewer_than_minimum_independent_dates")
        if raw_events < STAT_MIN_EVENTS:
            reasons.append("fewer_than_minimum_events")
        support["sparse"] = bool(reasons)
        support["reasons"] = reasons
    return metric


def independent_date_support(variant_dates: dict) -> dict:
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


def future_window(unit: UnitBars, label_start_ns: int, horizon_minutes: int,
                  *, reference_contract_key=None, prepared=None):
    if prepared is None:
        prepared = prepare_unit(unit)
    return lookup_future_window(
        unit, prepared.futures, label_start_ns, horizon_minutes,
        reference_contract_key=reference_contract_key,
    )


def pair_timing_rows(left, right):
    identity = (
        ("event_id", "different_event"),
        ("horizon_minutes", "different_horizon"),
        ("source_symbol", "different_source"),
        ("receiver_symbol", "different_receiver"),
        ("source_variant", "different_source_variant"),
        ("receiver_variant", "different_receiver_variant"),
        ("source_contract_key", "different_source_contract"),
        ("receiver_contract_key", "different_receiver_contract"),
        ("anchor_ns", "different_anchor"),
        ("source_start_ns", "different_source_bar"),
        ("maturity_ns", "different_maturity"),
    )
    for field, reason in identity:
        if left.get(field) != right.get(field):
            return {"pairing": "unpaired", "reason": reason}
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


def group_key(*, metric, source, receiver, source_variant, receiver_variant,
              year, stage, session, lookback, event_kind, lag, horizon):
    return (
        metric, source or "", receiver or "", source_variant or "", receiver_variant or "",
        year, stage, session, lookback, event_kind, lag, horizon,
    )


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
        _str(pa, "source_symbol"), _str(pa, "receiver_symbol"),
        _str(pa, "source_variant"), _str(pa, "receiver_variant"),
        _i64(pa, "cut_ns"), _i64(pa, "lag_s"),
        _i64(pa, "source_start_ns"), _i64(pa, "source_end_ns"),
        _i64(pa, "source_known_at_ns"), _i64(pa, "source_age_ns"),
        _str(pa, "source_join"), _f64(pa, "source_close"),
        _f64(pa, "source_volume"), _i64(pa, "source_instrument_id"),
        _str(pa, "source_contract_key"), _i64(pa, "source_file_id"),
        _i64(pa, "receiver_start_ns"), _i64(pa, "receiver_known_at_ns"),
        _i64(pa, "receiver_age_ns"), _str(pa, "receiver_join"),
        _f64(pa, "receiver_close"), _i64(pa, "receiver_instrument_id"),
        _str(pa, "receiver_contract_key"),
        _bool(pa, "own_eligible"), _bool(pa, "own_observed"), _bool(pa, "own_stale"),
        _bool(pa, "common_coverage"), _bool(pa, "definition_certified"),
        _i64(pa, "actual_received_at_ns"),
    ])


def lookback_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "symbol"), _str(pa, "variant"), _i64(pa, "cut_ns"), _i64(pa, "lag_s"),
        _i64(pa, "lookback_minutes"), _i64(pa, "bar_start_ns"),
        _f64(pa, "log_return"), _f64(pa, "intervening_high"), _f64(pa, "intervening_low"),
        _f64(pa, "relative_volume"), _f64(pa, "prior_rth_sqrt_rv"),
        _str(pa, "status"), _str(pa, "volume_unit"), _i64(pa, "file_id"),
        _str(pa, "contract_key"),
    ])


def smt_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "source_symbol"), _str(pa, "receiver_symbol"),
        _str(pa, "source_variant"), _str(pa, "receiver_variant"),
        _i64(pa, "cut_ns"), _i64(pa, "lag_s"), _i64(pa, "lookback_minutes"),
        _str(pa, "kind"),
        _bool(pa, "source_own_breach_high"), _bool(pa, "source_own_breach_low"),
        _bool(pa, "receiver_own_breach_high"), _bool(pa, "receiver_own_breach_low"),
        _f64(pa, "source_prior_high"), _f64(pa, "source_prior_low"),
        _f64(pa, "receiver_prior_high"), _f64(pa, "receiver_prior_low"),
        _f64(pa, "source_close"), _f64(pa, "receiver_close"),
        _str(pa, "breach_state"), _bool(pa, "common_cut"),
        _f64(pa, "source_relative_excursion"),
    ])


def mapping_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "futures_symbol"), _str(pa, "etf_symbol"),
        _str(pa, "futures_variant"), _str(pa, "etf_variant"),
        _i64(pa, "cut_ns"), _i64(pa, "lag_s"),
        _f64(pa, "contemporaneous_ratio"), _f64(pa, "contemporaneous_inverse"),
        _f64(pa, "prior_ratio"), _f64(pa, "predicted_receiver"),
        _f64(pa, "residual_receiver_points"), _str(pa, "status"), _str(pa, "reason"),
        _bool(pa, "prior_ratio_frozen"),
        _str(pa, "futures_contract_key"), _str(pa, "etf_contract_key"),
        _i64(pa, "prior_cut_ns"),
    ])


def source_event_schema():
    pa = _pa()
    return pa.schema([
        _i64(pa, "event_id"), _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"),
        _str(pa, "session"), _str(pa, "source_symbol"), _str(pa, "source_variant"),
        _str(pa, "event_kind"), _i64(pa, "lookback_minutes"), _i64(pa, "direction"),
        _i64(pa, "source_start_ns"), _i64(pa, "source_end_ns"),
        _i64(pa, "source_known_at_0"), _i64(pa, "source_known_at_60"),
        _i64(pa, "source_known_at_120"),
        _i64(pa, "formation_start_ns"), _i64(pa, "formation_end_ns"),
        _i64(pa, "anchor_ns"), _f64(pa, "source_close"),
        _i64(pa, "source_file_id"), _i64(pa, "source_instrument_id"),
        _str(pa, "source_contract_key"), _i64(pa, "actual_received_at_ns"),
    ])


def receiver_label_schema():
    pa = _pa()
    return pa.schema([
        _i64(pa, "label_id"), _str(pa, "receiver_symbol"), _str(pa, "receiver_variant"),
        _i64(pa, "lag_s"), _i64(pa, "horizon_minutes"), _i64(pa, "label_start_ns"),
        _i64(pa, "maturity_ns"), _str(pa, "future_status"), _str(pa, "future_reasons"),
        _f64(pa, "open"), _f64(pa, "high"), _f64(pa, "low"), _f64(pa, "close"),
        _i64(pa, "instrument_id"), _str(pa, "contract_key"), _i64(pa, "file_id"),
        _i64(pa, "actual_received_at_ns"),
    ])


def event_link_schema():
    pa = _pa()
    return pa.schema([
        _i64(pa, "event_id"), _i64(pa, "label_id"),
        _str(pa, "receiver_symbol"), _str(pa, "receiver_variant"),
        _i64(pa, "lag_s"), _i64(pa, "horizon_minutes"),
        _i64(pa, "receiver_ref_start_ns"), _f64(pa, "receiver_ref_close"),
        _str(pa, "receiver_ref_join"), _i64(pa, "receiver_instrument_id"),
        _str(pa, "receiver_contract_key"),
        _f64(pa, "past_formation_log"), _f64(pa, "past_preavailability_log"),
        _f64(pa, "terminal_log"), _f64(pa, "up_log"), _f64(pa, "down_log"),
        _f64(pa, "path_range_log"), _i64(pa, "terminal_sign"),
        _str(pa, "concordance"), _str(pa, "future_status"),
        _bool(pa, "zero_reaction"), _bool(pa, "no_receiver"),
        _bool(pa, "ci_eligible"), _str(pa, "local_node_presence"),
        _i64(pa, "maturity_ns"), _i64(pa, "actual_received_at_ns"),
    ])


def contrast_schema():
    pa = _pa()
    return pa.schema([
        _i64(pa, "event_id"), _str(pa, "date"),
        _str(pa, "source_symbol"), _str(pa, "receiver_symbol"),
        _str(pa, "source_variant"), _str(pa, "receiver_variant"),
        _str(pa, "source_contract_key"), _str(pa, "receiver_contract_key"),
        _i64(pa, "horizon_minutes"), _i64(pa, "maturity_ns"),
        _i64(pa, "lag_a_s"), _i64(pa, "lag_b_s"), _str(pa, "pairing"),
        _str(pa, "reason"), _bool(pa, "reference_change"), _bool(pa, "common_reference"),
        _f64(pa, "terminal_a"), _f64(pa, "terminal_b"), _f64(pa, "terminal_contrast"),
        _str(pa, "kind"), _i64(pa, "lookback_minutes"),
    ])


def date_aggregate_schema():
    pa = _pa()
    return pa.schema([
        _str(pa, "date"), _i64(pa, "year"), _str(pa, "stage"), _str(pa, "session"),
        _str(pa, "source_symbol"), _str(pa, "receiver_symbol"),
        _str(pa, "source_variant"), _str(pa, "receiver_variant"),
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
        _str(pa, "source_sha256"), _bool(pa, "date_order_ok"),
        _bool(pa, "duplicate"), _bool(pa, "gap_not_compressed"),
        _i64(pa, "actual_received_at_ns"),
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

    def extend(self, rows: list[dict]):
        for row in rows:
            self.add(row)

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
    if value is None:
        return
    try:
        number = float(value)
    except (TypeError, ValueError):
        return
    if not math.isfinite(number):
        return
    store[key]["sum"][day] += number
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
    for metric in (result.get("metrics") or {}).values():
        bootstrap = metric.get("bootstrap") if isinstance(metric, dict) else None
        if isinstance(bootstrap, dict):
            bootstrap.pop("replicate_estimates", None)
    for ratio in (result.get("ratios") or {}).values():
        bootstrap = ratio.get("bootstrap") if isinstance(ratio, dict) else None
        if isinstance(bootstrap, dict):
            bootstrap.pop("replicate_estimates", None)
    return result


def summarize_groups(groups: dict, intended_by_key: dict) -> dict:
    buckets = defaultdict(list)
    for key, payload in groups.items():
        intended = intended_by_key.get(key)
        if not intended:
            continue
        buckets[tuple(intended)].append((key, payload, intended))
    out = {}
    for _, items in buckets.items():
        metrics = {}
        names = {}
        for key, payload, intended in items:
            name = "|".join("" if part is None else str(part) for part in key)
            names[name] = (key, payload)
            cells = date_cells_for_ci(payload["sum"], payload["count"])
            if cells:
                metrics[name] = cells
            else:
                out[key] = {
                    "status": "undefined",
                    "reason": "no_matches",
                    "actual_valid_event_count": 0,
                    "actual_valid_date_count": 0,
                }
        if not metrics:
            continue
        stats = _compact_stat(observed_date_statistics(
            metrics, items[0][2],
            estimator="date_mean", seed=STAT_SEED, block_length=STAT_BLOCK,
            replicates=STAT_REPLICATES, confidence=STAT_CONFIDENCE,
            minimum_independent_dates=STAT_MIN_DATES, minimum_events=STAT_MIN_EVENTS,
            _retain_replicate_estimates=False,
        ))
        for name, metric in stats["metrics"].items():
            key, payload = names[name]
            restore_event_counts(metric, payload["count"])
            means = []
            for day in items[0][2]:
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


def _bool_or_none(known, flag):
    if not known:
        return None
    return bool(flag)


def _breach_state(src_known, rcv_known, src_high, src_low, rcv_high, rcv_low) -> str:
    if not src_known or not rcv_known:
        return "unknown"
    source = bool(src_high or src_low)
    receiver = bool(rcv_high or rcv_low)
    if source and receiver:
        return "both"
    if source:
        return "source_only"
    if receiver:
        return "receiver_only"
    return "neither"


def _join_view(prep, index, status_code, cut_ns, lag):
    unit = prep.unit
    if index < 0:
        return {
            "index": None, "join": join_status_name(int(status_code)),
            "start_ns": None, "end_ns": None, "known_at_ns": None, "age_ns": None,
            "close": None, "volume": None, "instrument_id": None,
            "high": None, "low": None, "contract_key": None, "valid": False, "priced": False,
        }
    known = int(unit.known_for(lag)[index])
    end = int(unit.end_ns[index])
    status = join_status_name(int(status_code))
    valid = bool(unit.valid[index])
    close = float(unit.close[index]) if math.isfinite(float(unit.close[index])) else None
    return {
        "index": int(index),
        "join": status,
        "start_ns": int(unit.start_ns[index]),
        "end_ns": end,
        "known_at_ns": known,
        "age_ns": int(cut_ns) - end,
        "close": close,
        "volume": float(unit.volume[index]) if valid else None,
        "instrument_id": int(unit.instrument_id[index]),
        "high": float(unit.high[index]) if valid else None,
        "low": float(unit.low[index]) if valid else None,
        "contract_key": prep.contract_key[index],
        "valid": valid,
        "priced": status == "fresh" and valid and close is not None and close > 0.0,
    }


def year_cash_days(calendar, year: int, fixture_dates):
    if fixture_dates is not None:
        wanted = {item if type(item) is date else date.fromisoformat(str(item)[:10])
                  for item in fixture_dates}
        days = []
        for cash in intended_cash_dates(calendar, *year_date_bounds(year)):
            if cash.day in wanted:
                days.append(cash)
        return days
    return list(intended_cash_dates(calendar, *year_date_bounds(year)))


def _ensure_pair_groups(groups, source, receiver, year, stage, session):
    for lag in LATENCY_AFTER_END_S:
        groups[group_key(
            metric="coverage_common", source=source.symbol, receiver=receiver.symbol,
            source_variant=source.variant, receiver_variant=receiver.variant,
            year=year, stage=stage, session=session, lookback=None,
            event_kind=None, lag=lag, horizon=None)]
        for kind in ("running", "pivot"):
            lookbacks = REFERENCE_LOOKBACKS if kind == "running" else (15,)
            for length in lookbacks:
                for metric in SMT_METRICS:
                    groups[group_key(
                        metric=metric, source=source.symbol, receiver=receiver.symbol,
                        source_variant=source.variant, receiver_variant=receiver.variant,
                        year=year, stage=stage, session=session, lookback=length,
                        event_kind=kind, lag=lag, horizon=None)]
        for length in REFERENCE_LOOKBACKS:
            groups[group_key(
                metric="running_vs_pivot", source=source.symbol, receiver=receiver.symbol,
                source_variant=source.variant, receiver_variant=receiver.variant,
                year=year, stage=stage, session=session, lookback=length,
                event_kind="running_vs_pivot", lag=lag, horizon=None)]
        for kind in EVENT_KINDS:
            for length in REFERENCE_LOOKBACKS:
                if kind.startswith("pivot") and length != 15:
                    continue
                for horizon in FUTURE_HORIZONS:
                    for metric in PATH_METRICS + LIFE_METRICS + ("lag_contrast",):
                        groups[group_key(
                            metric=metric, source=source.symbol, receiver=receiver.symbol,
                            source_variant=source.variant, receiver_variant=receiver.variant,
                            year=year, stage=stage, session=session, lookback=length,
                            event_kind=kind, lag=lag, horizon=horizon)]


def _ensure_own_groups(groups, unit, year, stage, session):
    for lag in LATENCY_AFTER_END_S:
        for metric in ("coverage_own_eligible", "coverage_own_observed", "coverage_own_stale"):
            groups[group_key(
                metric=metric, source=unit.symbol, receiver="",
                source_variant=unit.variant, receiver_variant="",
                year=year, stage=stage, session=session, lookback=None,
                event_kind=None, lag=lag, horizon=None)]
        for length in LOOKBACKS:
            groups[group_key(
                metric="lookback_logret", source=unit.symbol, receiver="",
                source_variant=unit.variant, receiver_variant="",
                year=year, stage=stage, session=session, lookback=length,
                event_kind=None, lag=lag, horizon=None)]
            groups[group_key(
                metric="relative_volume", source=unit.symbol, receiver="",
                source_variant=unit.variant, receiver_variant="",
                year=year, stage=stage, session=session, lookback=length,
                event_kind=None, lag=lag, horizon=None)]


def process_year(*, year: int, units: dict, calendar, writers: dict, groups: dict,
                 intended_dates: list, carry: dict, variant_dates: dict,
                 fixture_dates=None, event_seq: list, label_ids: dict):
    prepared = {key: prepare_unit(unit) for key, unit in units.items()}
    by_obj = {id(unit): key for key, unit in units.items()}
    cash_days = year_cash_days(calendar, year, fixture_dates)
    intended_day_list = [cash.day for cash in cash_days]
    year_dates = [day.isoformat() for day in intended_day_list]
    pairs = list(directed_unit_pairs(units))
    prior_calendar_days = [date.fromisoformat(d) for d in intended_dates]
    history_days = sorted(set(prior_calendar_days + intended_day_list))
    previous_by_day = {d: history_days[i - 1] if i else None for i, d in enumerate(history_days)}
    for cash in cash_days:
        next_label_id = label_ids.get("_next", 1)
        label_ids.clear()
        label_ids["_next"] = next_label_id
        prior_dates = history_days[max(0, history_days.index(cash.day) - 20):history_days.index(cash.day)]
        intended_dates.append(cash.day.isoformat())
        day = cash.day.isoformat()
        stage = stage_of(cash.day) or "outside_primary"
        sess_start, sess_end, _ = futures_session_bounds(cash, calendar.zone)
        cuts = grid_cuts(int(sess_start), int(sess_end), GRID_MINUTES)
        cut_list = [int(value) for value in cuts.tolist()]
        session_by_cut = [session_label(cut, cash, calendar.zone) for cut in cut_list]
        joins = {}
        for key, prep in prepared.items():
            for lag in LATENCY_AFTER_END_S:
                joins[(key, lag)] = backward_join_indices(
                    prep.unit.known_for(lag), cuts, prep.unit.end_ns)
        for session in SESSIONS:
            for unit in units.values():
                _ensure_own_groups(groups, unit, year, stage, session)
            for source, receiver in pairs:
                _ensure_pair_groups(groups, source, receiver, year, stage, session)
            for futures_symbol, etf_symbol in MAPPING_CHAINS:
                futs = [unit for unit in units.values() if unit.symbol == futures_symbol]
                etfs = [unit for unit in units.values() if unit.symbol == etf_symbol]
                for fut in futs:
                    for etf in etfs:
                        for lag in LATENCY_AFTER_END_S:
                            groups[group_key(
                                metric="mapping_residual", source=etf.symbol, receiver=fut.symbol,
                                source_variant=etf.variant, receiver_variant=fut.variant,
                                year=year, stage=stage, session=session, lookback=None,
                                event_kind=None, lag=lag, horizon=None)]
        for cut_i, cut in enumerate(cut_list):
            session = session_by_cut[cut_i]
            views = {}
            for key, prep in prepared.items():
                for lag in LATENCY_AFTER_END_S:
                    idx, status = joins[(key, lag)]
                    views[(key, lag)] = _join_view(prep, int(idx[cut_i]), int(status[cut_i]), cut, lag)
            for key, unit in units.items():
                for lag in LATENCY_AFTER_END_S:
                    src = views[(key, lag)]
                    _add_cell(groups, group_key(
                        metric="coverage_own_eligible", source=unit.symbol, receiver="",
                        source_variant=unit.variant, receiver_variant="",
                        year=year, stage=stage, session=session, lookback=None,
                        event_kind=None, lag=lag, horizon=None), day, 1.0 if src["priced"] else 0.0)
                    _add_cell(groups, group_key(
                        metric="coverage_own_observed", source=unit.symbol, receiver="",
                        source_variant=unit.variant, receiver_variant="",
                        year=year, stage=stage, session=session, lookback=None,
                        event_kind=None, lag=lag, horizon=None), day,
                              1.0 if src["join"] in ("fresh", "stale") else 0.0)
                    _add_cell(groups, group_key(
                        metric="coverage_own_stale", source=unit.symbol, receiver="",
                        source_variant=unit.variant, receiver_variant="",
                        year=year, stage=stage, session=session, lookback=None,
                        event_kind=None, lag=lag, horizon=None), day,
                              1.0 if src["join"] == "stale" else 0.0)
            for source, receiver in pairs:
                source_key = by_obj[id(source)]
                receiver_key = by_obj[id(receiver)]
                variant_dates.setdefault(source.variant, set()).add(day)
                variant_dates.setdefault(receiver.variant, set()).add(day)
                src_prep = prepared[source_key]
                rcv_prep = prepared[receiver_key]
                for lag in LATENCY_AFTER_END_S:
                    src = views[(source_key, lag)]
                    rcv = views[(receiver_key, lag)]
                    own_eligible = src["priced"]
                    own_observed = src["join"] in ("fresh", "stale")
                    own_stale = src["join"] == "stale"
                    common = src["priced"] and rcv["priced"]
                    writers["cuts"].add({
                        "date": day, "year": year, "stage": stage, "session": session,
                        "source_symbol": source.symbol, "receiver_symbol": receiver.symbol,
                        "source_variant": source.variant, "receiver_variant": receiver.variant,
                        "cut_ns": cut, "lag_s": lag,
                        "source_start_ns": src["start_ns"], "source_end_ns": src["end_ns"],
                        "source_known_at_ns": src["known_at_ns"], "source_age_ns": src["age_ns"],
                        "source_join": src["join"],
                        "source_close": src["close"] if own_observed else None,
                        "source_volume": src["volume"] if own_eligible else None,
                        "source_instrument_id": src["instrument_id"],
                        "source_contract_key": src["contract_key"],
                        "source_file_id": source.file_id,
                        "receiver_start_ns": rcv["start_ns"],
                        "receiver_known_at_ns": rcv["known_at_ns"],
                        "receiver_age_ns": rcv["age_ns"], "receiver_join": rcv["join"],
                        "receiver_close": rcv["close"] if rcv["join"] in ("fresh", "stale") else None,
                        "receiver_instrument_id": rcv["instrument_id"],
                        "receiver_contract_key": rcv["contract_key"],
                        "own_eligible": own_eligible, "own_observed": own_observed,
                        "own_stale": own_stale, "common_coverage": common,
                        "definition_certified": source.definition_certified,
                        "actual_received_at_ns": None,
                    })
                    _add_cell(groups, group_key(
                        metric="coverage_common", source=source.symbol, receiver=receiver.symbol,
                        source_variant=source.variant, receiver_variant=receiver.variant,
                        year=year, stage=stage, session=session, lookback=None,
                        event_kind=None, lag=lag, horizon=None), day, 1.0 if common else 0.0)
                    for kind, state_src, state_rcv, lookbacks in (
                        ("running", src_prep.running, rcv_prep.running, REFERENCE_LOOKBACKS),
                        ("pivot", None, None, (15,)),
                    ):
                        for length in lookbacks:
                            if kind == "running":
                                src_state = state_src[length]
                                rcv_state = state_rcv[length]
                                src_known = src["priced"] and src["index"] is not None and bool(src_state["defined"][src["index"]])
                                rcv_known = rcv["priced"] and rcv["index"] is not None and bool(rcv_state["defined"][rcv["index"]])
                                src_h = bool(src_known and src_state["high_breach"][src["index"]])
                                src_l = bool(src_known and src_state["low_breach"][src["index"]])
                                rcv_h = bool(rcv_known and rcv_state["high_breach"][rcv["index"]])
                                rcv_l = bool(rcv_known and rcv_state["low_breach"][rcv["index"]])
                                sph = _finite(src_state["prior_high"][src["index"]]) if src_known else None
                                spl = _finite(src_state["prior_low"][src["index"]]) if src_known else None
                                rph = _finite(rcv_state["prior_high"][rcv["index"]]) if rcv_known else None
                                rpl = _finite(rcv_state["prior_low"][rcv["index"]]) if rcv_known else None
                            else:
                                src_p = src_prep.pivot
                                rcv_p = rcv_prep.pivot
                                src_known = src["priced"] and src["index"] is not None and (
                                    int(src_p["high_known_end_ns"][src["index"]]) >= 0
                                    and int(src_p["low_known_end_ns"][src["index"]]) >= 0)
                                rcv_known = rcv["priced"] and rcv["index"] is not None and (
                                    int(rcv_p["high_known_end_ns"][rcv["index"]]) >= 0
                                    and int(rcv_p["low_known_end_ns"][rcv["index"]]) >= 0)
                                src_h = bool(src_known and src_p["high_breach"][src["index"]])
                                src_l = bool(src_known and src_p["low_breach"][src["index"]])
                                rcv_h = bool(rcv_known and rcv_p["high_breach"][rcv["index"]])
                                rcv_l = bool(rcv_known and rcv_p["low_breach"][rcv["index"]])
                                sph = _finite(src_p["high_level"][src["index"]]) if src_known else None
                                spl = _finite(src_p["low_level"][src["index"]]) if src_known else None
                                rph = _finite(rcv_p["high_level"][rcv["index"]]) if rcv_known else None
                                rpl = _finite(rcv_p["low_level"][rcv["index"]]) if rcv_known else None
                            state = _breach_state(src_known, rcv_known, src_h, src_l, rcv_h, rcv_l)
                            excursion = None
                            if src_known:
                                high_excursion = max(0.0, math.log(src["high"] / sph)) if src_h and sph and sph > 0 else 0.0
                                low_excursion = max(0.0, math.log(spl / src["low"])) if src_l and spl and src["low"] > 0 else 0.0
                                excursion = max(high_excursion, low_excursion)
                            writers["smt"].add({
                                "date": day, "year": year, "stage": stage, "session": session,
                                "source_symbol": source.symbol, "receiver_symbol": receiver.symbol,
                                "source_variant": source.variant, "receiver_variant": receiver.variant,
                                "cut_ns": cut, "lag_s": lag, "lookback_minutes": length,
                                "kind": kind,
                                "source_own_breach_high": _bool_or_none(src_known, src_h),
                                "source_own_breach_low": _bool_or_none(src_known, src_l),
                                "receiver_own_breach_high": _bool_or_none(rcv_known, rcv_h),
                                "receiver_own_breach_low": _bool_or_none(rcv_known, rcv_l),
                                "source_prior_high": sph, "source_prior_low": spl,
                                "receiver_prior_high": rph, "receiver_prior_low": rpl,
                                "source_close": src["close"] if src["priced"] else None,
                                "receiver_close": rcv["close"] if rcv["priced"] else None,
                                "breach_state": state,
                                "common_cut": bool(src_known and rcv_known),
                                "source_relative_excursion": excursion,
                            })
                            gk = dict(source=source.symbol, receiver=receiver.symbol,
                                      source_variant=source.variant, receiver_variant=receiver.variant,
                                      year=year, stage=stage, session=session, lookback=length,
                                      event_kind=kind, lag=lag, horizon=None)
                            _add_cell(groups, group_key(metric="smt_source_only", **gk), day, 1.0 if state == "source_only" else 0.0)
                            _add_cell(groups, group_key(metric="smt_receiver_only", **gk), day, 1.0 if state == "receiver_only" else 0.0)
                            _add_cell(groups, group_key(metric="smt_both", **gk), day, 1.0 if state == "both" else 0.0)
                            _add_cell(groups, group_key(metric="smt_neither", **gk), day, 1.0 if state == "neither" else 0.0)
                            _add_cell(groups, group_key(metric="smt_unknown", **gk), day, 1.0 if state == "unknown" else 0.0)
                            _add_cell(groups, group_key(metric="smt_source_excursion", **gk), day, excursion)
                    if src_prep.running and rcv_prep.running:
                        for length in REFERENCE_LOOKBACKS:
                            src_idx = src["index"]
                            rcv_idx = rcv["index"]
                            src_known = src["priced"] and src_idx is not None and bool(src_prep.running[length]["defined"][src_idx]) and (int(src_prep.pivot["high_known_end_ns"][src_idx]) >= 0 and int(src_prep.pivot["low_known_end_ns"][src_idx]) >= 0)
                            rcv_known = rcv["priced"] and rcv_idx is not None and bool(rcv_prep.running[length]["defined"][rcv_idx]) and (int(rcv_prep.pivot["high_known_end_ns"][rcv_idx]) >= 0 and int(rcv_prep.pivot["low_known_end_ns"][rcv_idx]) >= 0)
                            if not (src_known and rcv_known):
                                continue
                            run_h = bool(src_prep.running[length]["high_breach"][src_idx])
                            piv_h = bool(src_prep.pivot["high_breach"][src_idx])
                            run_l = bool(src_prep.running[length]["low_breach"][src_idx])
                            piv_l = bool(src_prep.pivot["low_breach"][src_idx])
                            writers["contrasts"].add({
                                "event_id": None, "date": day,
                                "source_symbol": source.symbol, "receiver_symbol": receiver.symbol,
                                "source_variant": source.variant, "receiver_variant": receiver.variant,
                                "source_contract_key": src["contract_key"],
                                "receiver_contract_key": rcv["contract_key"],
                                "horizon_minutes": None, "maturity_ns": None,
                                "lag_a_s": lag, "lag_b_s": lag,
                                "pairing": "common_cut" if src_known and rcv_known else "own_only",
                                "reason": None, "reference_change": False,
                                "common_reference": True,
                                "terminal_a": 1.0 if (run_h or run_l) else 0.0,
                                "terminal_b": 1.0 if (piv_h or piv_l) else 0.0,
                                "terminal_contrast": (1.0 if (run_h or run_l) else 0.0) - (1.0 if (piv_h or piv_l) else 0.0),
                                "kind": "running_vs_pivot", "lookback_minutes": length,
                            })
                            _add_cell(groups, group_key(
                                metric="running_vs_pivot", source=source.symbol, receiver=receiver.symbol,
                                source_variant=source.variant, receiver_variant=receiver.variant,
                                year=year, stage=stage, session=session, lookback=length,
                                event_kind="running_vs_pivot", lag=lag, horizon=None),
                                      day, 1.0 if ((run_h or run_l) == (piv_h or piv_l)) else 0.0)
            for key, unit in units.items():
                prep = prepared[key]
                carry_unit = carry.setdefault("rel", {}).setdefault(unit_stable_key(unit), PriorCarry())
                for lag in LATENCY_AFTER_END_S:
                    row = views[(key, lag)]
                    for length in LOOKBACKS:
                        status = row["join"]
                        log_ret = hi = lo = rel = scale = None
                        if row["index"] is None:
                            status = row["join"]
                        elif not row["priced"]:
                            status = row["join"] if row["join"] != "fresh" else "invalid"
                        else:
                            index = row["index"]
                            ret, ok = prep.logret[length]
                            xhi, xlo, xok = prep.intervening[length]
                            if ok[index]:
                                log_ret = _finite(ret[index])
                            if xok[index]:
                                hi = _finite(xhi[index])
                                lo = _finite(xlo[index])
                            rel, rel_reason = carry_unit.relative_volume(
                                ny_wall_minute(int(unit.start_ns[index]), calendar.zone),
                                float(unit.volume[index]), prior_dates)
                            if rel is None and rel_reason:
                                status = rel_reason
                            elif log_ret is not None:
                                status = "defined"
                            else:
                                status = "undefined"
                            scale = carry_unit.prior_rth_scale(prep.contract_key[index], prior_dates)
                        writers["lookbacks"].add({
                            "date": day, "year": year, "stage": stage, "session": session,
                            "symbol": unit.symbol, "variant": unit.variant, "cut_ns": cut,
                            "lag_s": lag, "lookback_minutes": length,
                            "bar_start_ns": row["start_ns"],
                            "log_return": log_ret, "intervening_high": hi, "intervening_low": lo,
                            "relative_volume": rel, "prior_rth_sqrt_rv": scale,
                            "status": status, "volume_unit": unit.volume_unit,
                            "file_id": unit.file_id,
                            "contract_key": row["contract_key"],
                        })
                        _add_cell(groups, group_key(
                            metric="lookback_logret", source=unit.symbol, receiver="",
                            source_variant=unit.variant, receiver_variant="",
                            year=year, stage=stage, session=session, lookback=length,
                            event_kind=None, lag=lag, horizon=None), day, log_ret)
                        _add_cell(groups, group_key(
                            metric="relative_volume", source=unit.symbol, receiver="",
                            source_variant=unit.variant, receiver_variant="",
                            year=year, stage=stage, session=session, lookback=length,
                            event_kind=None, lag=lag, horizon=None), day, rel)
            _write_mapping_cuts(
                units, prepared, by_obj, views, cash, day, year, stage, session, cut,
                writers, groups, carry, previous_by_day)
        _emit_source_events(
            units, prepared, by_obj, cash, day, year, stage, writers, groups,
            calendar, event_seq, label_ids)
        for key, unit in units.items():
            prep = prepared[key]
            volumes = economic_minute_volumes(unit, int(sess_start), int(sess_end), calendar.zone)
            rth_start = rth_end = None
            if cash.state != "closed":
                rth_start, rth_end = cash.open_at, cash.close_at
            rv, complete = (None, False)
            if rth_start is not None:
                rv, complete = session_log_rv(
                    unit.close, unit.start_ns, unit.instrument_id, unit.valid, rth_start, rth_end,
                    run=prep.run, defined_1=prep.defined_1, prefix_sq=prep.prefix_sq,
                    contract_key=prep.contract_key)
            contract = None
            if complete and rth_start is not None:
                lo, _ = unit.slice_session(int(rth_start), int(rth_end))
                if 0 <= lo < len(unit):
                    contract = prep.contract_key[lo]
            carry.setdefault("rel", {}).setdefault(unit_stable_key(unit), PriorCarry()).push_day(
                cash.day, volumes, rv, complete, contract)
        _freeze_mapping_day(units, cash, carry, intended_day_list)
    return year_dates


def _write_mapping_cuts(units, prepared, by_obj, views, cash, day, year, stage, session, cut,
                        writers, groups, carry, intended_days):
    prior_day = intended_days.get(cash.day) if isinstance(intended_days, dict) else previous_intended_date(intended_days, cash.day)
    for futures_symbol, etf_symbol in MAPPING_CHAINS:
        futs = [unit for unit in units.values() if unit.symbol == futures_symbol]
        etfs = [unit for unit in units.values() if unit.symbol == etf_symbol]
        for fut in futs:
            for etf in etfs:
                for lag in LATENCY_AFTER_END_S:
                    fut_view = views[(by_obj[id(fut)], lag)]
                    etf_view = views[(by_obj[id(etf)], lag)]
                    ratio = None
                    mapped = {
                        "ratio": None, "predicted_receiver": None,
                        "residual_receiver_points": None, "status": "undefined",
                        "reason": "previous_day_missing",
                    }
                    prior = None
                    if prior_day is not None:
                        prior = (carry.get("ratio") or {}).get(
                            (futures_symbol, etf_symbol, fut.variant, etf.variant, lag), {}
                        ).get(prior_day)
                    if fut_view["priced"] and etf_view["priced"]:
                        ratio = contemporaneous_ratio(fut_view["close"], etf_view["close"])
                        if prior is None:
                            mapped["reason"] = (
                                "previous_day_missing" if prior_day is not None else "no_prior_intended_date")
                        elif prior.get("cut_ns") is not None and int(prior["cut_ns"]) >= int(cut):
                            mapped["reason"] = "prior_ratio_not_before_cut"
                        elif not same_map_contracts(prior, fut_view, etf_view):
                            mapped["reason"] = "new_contract"
                        else:
                            mapped = lagged_mapping_residual(
                                prior_receiver_close=prior["receiver_close"],
                                prior_source_close=prior["source_close"],
                                current_source=etf_view["close"],
                                current_receiver=fut_view["close"],
                            )
                    else:
                        mapped["reason"] = "current_missing_or_stale"
                    writers["mapping"].add({
                        "date": day, "year": year, "stage": stage, "session": session,
                        "futures_symbol": futures_symbol, "etf_symbol": etf_symbol,
                        "futures_variant": fut.variant, "etf_variant": etf.variant,
                        "cut_ns": cut, "lag_s": lag,
                        "contemporaneous_ratio": None if ratio is None else ratio["ratio"],
                        "contemporaneous_inverse": None if ratio is None else ratio["inverse"],
                        "prior_ratio": mapped.get("ratio"),
                        "predicted_receiver": mapped.get("predicted_receiver"),
                        "residual_receiver_points": mapped.get("residual_receiver_points"),
                        "status": mapped.get("status"), "reason": mapped.get("reason"),
                        "prior_ratio_frozen": True,
                        "futures_contract_key": fut_view["contract_key"],
                        "etf_contract_key": etf_view["contract_key"],
                        "prior_cut_ns": None if prior is None else prior.get("cut_ns"),
                    })
                    _add_cell(groups, group_key(
                        metric="mapping_residual", source=etf.symbol, receiver=fut.symbol,
                        source_variant=etf.variant, receiver_variant=fut.variant,
                        year=year, stage=stage, session=session, lookback=None,
                        event_kind=None, lag=lag, horizon=None),
                              day, mapped.get("residual_receiver_points"))


def same_map_contracts(prior, fut_view, etf_view) -> bool:
    return (
        prior.get("receiver_contract_key") == fut_view.get("contract_key")
        and prior.get("source_contract_key") == etf_view.get("contract_key")
        and prior.get("source_version") is not None
    )


def _freeze_mapping_day(units, cash, carry, intended_days):
    store = carry.setdefault("ratio", {})
    for futures_symbol, etf_symbol in MAPPING_CHAINS:
        futs = [unit for unit in units.values() if unit.symbol == futures_symbol]
        etfs = [unit for unit in units.values() if unit.symbol == etf_symbol]
        for fut in futs:
            for etf in etfs:
                for lag in LATENCY_AFTER_END_S:
                    key = (futures_symbol, etf_symbol, fut.variant, etf.variant, lag)
                    store.setdefault(key, {})[cash.day] = freeze_previous_closing_ratio(
                        etf, fut, cash, latency_after_end_s=lag)


def _past_receiver(prep, cut_ns, lag):
    index, status = last_available(prep.unit, int(cut_ns), latency_after_end_s=lag)
    if not priced_ok(prep.unit, index, status):
        return None, None, status
    return index, float(prep.unit.close[index]), status


def _emit_source_events(units, prepared, by_obj, cash, day, year, stage, writers, groups,
                        calendar, event_seq, label_ids):
    sess_start, sess_end, _ = futures_session_bounds(cash, calendar.zone)
    receivers = [unit for unit in units.values() if unit.symbol in ("NQ", "ES")]
    for source in units.values():
        source_key = by_obj[id(source)]
        prep = prepared[source_key]
        lo, hi = source.slice_session(int(sess_start), int(sess_end))
        clocks = source.ensure_clocks()
        for index in range(lo, hi):
            if not source.valid[index]:
                continue
            session = session_label(int(source.start_ns[index]), cash, calendar.zone)
            events = []
            for length in REFERENCE_LOOKBACKS:
                running = prep.running[length]
                if running["high_breach"][index]:
                    events.append(("running_high", 1, int(source.start_ns[index]), length,
                                   int(source.start_ns[index]) - length * MINUTE, int(source.start_ns[index])))
                if running["low_breach"][index]:
                    events.append(("running_low", -1, int(source.start_ns[index]), length,
                                   int(source.start_ns[index]) - length * MINUTE, int(source.start_ns[index])))
            pivot = prep.pivot
            if pivot["high_breach"][index]:
                formed = int(pivot["high_formed_ns"][index])
                events.append(("pivot_high", 1, formed, 15, formed - 2 * MINUTE, formed + 3 * MINUTE))
            if pivot["low_breach"][index]:
                formed = int(pivot["low_formed_ns"][index])
                events.append(("pivot_low", -1, formed, 15, formed - 2 * MINUTE, formed + 3 * MINUTE))
            for kind, direction, anchor_ns, lookback, formation_start, formation_end in events:
                event_id = event_seq[0]
                event_seq[0] += 1
                writers["source_events"].add({
                    "event_id": event_id, "date": day, "year": year, "stage": stage,
                    "session": session, "source_symbol": source.symbol,
                    "source_variant": source.variant, "event_kind": kind,
                    "lookback_minutes": lookback, "direction": direction,
                    "source_start_ns": int(source.start_ns[index]),
                    "source_end_ns": int(source.end_ns[index]),
                    "source_known_at_0": int(clocks[0][index]),
                    "source_known_at_60": int(clocks[60][index]),
                    "source_known_at_120": int(clocks[120][index]),
                    "formation_start_ns": formation_start,
                    "formation_end_ns": formation_end,
                    "anchor_ns": anchor_ns,
                    "source_close": float(source.close[index]),
                    "source_file_id": source.file_id,
                    "source_instrument_id": int(source.instrument_id[index]),
                    "source_contract_key": prep.contract_key[index],
                    "actual_received_at_ns": None,
                })
                _add_cell(groups, group_key(
                    metric="source_events_total", source=source.symbol, receiver="",
                    source_variant=source.variant, receiver_variant="",
                    year=year, stage=stage, session=session, lookback=lookback,
                    event_kind=kind, lag=None, horizon=None), day, 1.0)
                if not receivers:
                    for lag in LATENCY_AFTER_END_S:
                        for horizon in FUTURE_HORIZONS:
                            writers["event_links"].add(_empty_link(
                                event_id, lag, horizon, "no_receiver"))
                            _record_life(groups, source, None, year, stage, session,
                                         lookback, kind, lag, horizon, day, "no_receiver")
                    continue
                for receiver in receivers:
                    if (source.symbol, receiver.symbol) not in DIRECTED_PAIRS:
                        continue
                    if source.symbol == receiver.symbol and source.variant == receiver.variant:
                        continue
                    rcv_key = by_obj[id(receiver)]
                    rcv_prep = prepared[rcv_key]
                    lag_rows = {}
                    for lag in LATENCY_AFTER_END_S:
                        event_known = int(clocks[lag][index])
                        event_start = int(source.start_ns[index])
                        label_start = ceil_to_minute(event_known)
                        ref_i, ref_close, ref_st = _past_receiver(rcv_prep, event_known, lag)
                        ref_start = None if ref_i is None else int(receiver.start_ns[ref_i])
                        ref_key = None if ref_i is None else rcv_prep.contract_key[ref_i]
                        no_ref = (
                            ref_i is None or ref_st != "fresh" or ref_close is None
                            or ref_start is None or ref_start >= event_known
                        )
                        form_i, form_close, _ = _past_receiver(rcv_prep, formation_start, lag)
                        mid_i, mid_close, _ = _past_receiver(rcv_prep, formation_end, lag)
                        past_formation = log_ratio(mid_close, form_close) if (
                            form_close and mid_close and form_i is not None and mid_i is not None
                            and form_i != mid_i
                            and rcv_prep.run_id[form_i] == rcv_prep.run_id[mid_i]
                            and rcv_prep.contract_key[form_i] == rcv_prep.contract_key[mid_i]) else None
                        past_pre = log_ratio(ref_close, mid_close) if (
                            ref_close and mid_close and mid_i is not None and not no_ref
                            and ref_i is not None
                            and rcv_prep.run_id[mid_i] == rcv_prep.run_id[ref_i]
                            and rcv_prep.contract_key[mid_i] == ref_key
                            and (ref_start is None or ref_start < event_known)) else None
                        for horizon in FUTURE_HORIZONS:
                            maturity = label_start + horizon * MINUTE
                            ci_ok = stages_aligned_for_ci(
                                formation_start, label_start, maturity, cash.day, calendar.zone)
                            raw_window = lookup_future_window(receiver, rcv_prep.futures, label_start, horizon)
                            window = dict(raw_window)
                            if no_ref:
                                window.update(status="no_receiver", high=None, low=None, close=None)
                            elif raw_window.get("contract_key") != ref_key:
                                window.update(status="roll", high=None, low=None, close=None)
                            label_key = (receiver.symbol, receiver.variant, lag, horizon, label_start)
                            label_id = label_ids.get(label_key)
                            if label_id is None:
                                label_id = label_ids["_next"]
                                label_ids["_next"] = label_id + 1
                                label_ids[label_key] = label_id
                                writers["receiver_labels"].add({
                                    "label_id": label_id, "receiver_symbol": receiver.symbol,
                                    "receiver_variant": receiver.variant, "lag_s": lag,
                                    "horizon_minutes": horizon, "label_start_ns": label_start,
                                    "maturity_ns": maturity,
                                    "future_status": raw_window["status"],
                                    "future_reasons": "|".join(raw_window.get("reasons") or ()),
                                    "open": raw_window.get("open"), "high": raw_window.get("high"),
                                    "low": raw_window.get("low"), "close": raw_window.get("close"),
                                    "instrument_id": raw_window.get("instrument_id"),
                                    "contract_key": raw_window.get("contract_key"),
                                    "file_id": receiver.file_id,
                                    "actual_received_at_ns": None,
                                })
                            bundle = excursion_bundle(
                                None if no_ref else ref_close, window.get("high"),
                                window.get("low"), window.get("close"))
                            future_status = "no_receiver" if no_ref else window["status"]
                            row = {
                                "event_id": event_id, "label_id": label_id,
                                "receiver_symbol": receiver.symbol,
                                "receiver_variant": receiver.variant,
                                "lag_s": lag, "horizon_minutes": horizon,
                                "receiver_ref_start_ns": ref_start,
                                "receiver_ref_close": None if no_ref else ref_close,
                                "receiver_ref_join": ref_st,
                                "receiver_instrument_id": None if ref_i is None else int(receiver.instrument_id[ref_i]),
                                "receiver_contract_key": ref_key,
                                "past_formation_log": past_formation,
                                "past_preavailability_log": past_pre,
                                "terminal_log": bundle["terminal_log"] if ci_ok else None,
                                "up_log": bundle["up_log"] if ci_ok else None,
                                "down_log": bundle["down_log"] if ci_ok else None,
                                "path_range_log": bundle["path_range_log"] if ci_ok else None,
                                "terminal_sign": bundle["terminal_sign"] if ci_ok else None,
                                "concordance": concordance(direction, bundle["terminal_sign"] if ci_ok else None),
                                "future_status": future_status,
                                "zero_reaction": bundle["zero_reaction"],
                                "no_receiver": future_status == "no_receiver",
                                "ci_eligible": ci_ok and future_status == "complete",
                                "local_node_presence": None,
                                "maturity_ns": maturity,
                                "actual_received_at_ns": None,
                                "source_symbol": source.symbol,
                                "source_variant": source.variant,
                                "source_contract_key": prep.contract_key[index],
                                "anchor_ns": anchor_ns,
                                "source_start_ns": int(source.start_ns[index]),
                                "event_kind": kind,
                                "lookback_minutes": lookback,
                                "direction": direction,
                            }
                            writers["event_links"].add({k: row[k] for k in (
                                "event_id", "label_id", "receiver_symbol", "receiver_variant",
                                "lag_s", "horizon_minutes", "receiver_ref_start_ns",
                                "receiver_ref_close", "receiver_ref_join", "receiver_instrument_id",
                                "receiver_contract_key", "past_formation_log",
                                "past_preavailability_log", "terminal_log", "up_log", "down_log",
                                "path_range_log", "terminal_sign", "concordance", "future_status",
                                "zero_reaction", "no_receiver", "ci_eligible",
                                "local_node_presence", "maturity_ns", "actual_received_at_ns")})
                            lag_rows.setdefault(horizon, {})[lag] = row
                            _record_event_metrics(
                                groups, source, receiver, year, stage, session, lookback,
                                kind, lag, horizon, day, row, future_status, ci_ok)
                    for horizon, by_lag in lag_rows.items():
                        for left, right in ((60, 0), (60, 120)):
                            if left in by_lag and right in by_lag:
                                paired = pair_timing_rows(by_lag[left], by_lag[right])
                                writers["contrasts"].add({
                                    "event_id": event_id, "date": day,
                                    "source_symbol": source.symbol,
                                    "receiver_symbol": receiver.symbol,
                                    "source_variant": source.variant,
                                    "receiver_variant": receiver.variant,
                                    "source_contract_key": by_lag[left].get("source_contract_key"),
                                    "receiver_contract_key": by_lag[left].get("receiver_contract_key"),
                                    "horizon_minutes": horizon,
                                    "maturity_ns": by_lag[left].get("maturity_ns"),
                                    "lag_a_s": left, "lag_b_s": right,
                                    "pairing": paired["pairing"],
                                    "reason": paired.get("reason"),
                                    "reference_change": bool(paired.get("reference_change")),
                                    "common_reference": bool(paired.get("common_reference")),
                                    "terminal_a": by_lag[left].get("terminal_log"),
                                    "terminal_b": by_lag[right].get("terminal_log"),
                                    "terminal_contrast": paired.get("terminal_contrast"),
                                    "kind": "timing_lag",
                                    "lookback_minutes": lookback,
                                })
                                _add_cell(groups, group_key(
                                    metric="lag_contrast", source=source.symbol,
                                    receiver=receiver.symbol, source_variant=source.variant,
                                    receiver_variant=receiver.variant, year=year, stage=stage,
                                    session=session, lookback=lookback, event_kind=kind,
                                    lag=left, horizon=horizon),
                                          day, paired.get("terminal_contrast"))


def _empty_link(event_id, lag, horizon, status):
    return {
        "event_id": event_id, "label_id": None,
        "receiver_symbol": None, "receiver_variant": None,
        "lag_s": lag, "horizon_minutes": horizon,
        "receiver_ref_start_ns": None, "receiver_ref_close": None,
        "receiver_ref_join": "missing", "receiver_instrument_id": None,
        "receiver_contract_key": None, "past_formation_log": None,
        "past_preavailability_log": None, "terminal_log": None, "up_log": None,
        "down_log": None, "path_range_log": None, "terminal_sign": None,
        "concordance": "undefined", "future_status": status,
        "zero_reaction": False, "no_receiver": True, "ci_eligible": False,
        "local_node_presence": None, "maturity_ns": None, "actual_received_at_ns": None,
    }


def _record_life(groups, source, receiver, year, stage, session, lookback, kind, lag, horizon, day, status):
    recv = "" if receiver is None else receiver.symbol
    recv_var = "" if receiver is None else receiver.variant
    _add_cell(groups, group_key(
        metric="no_receiver", source=source.symbol, receiver=recv,
        source_variant=source.variant, receiver_variant=recv_var,
        year=year, stage=stage, session=session, lookback=lookback,
        event_kind=kind, lag=lag, horizon=horizon), day, 1.0 if status == "no_receiver" else 0.0)


def _record_event_metrics(groups, source, receiver, year, stage, session, lookback, kind,
                          lag, horizon, day, row, future_status, ci_ok):
    base = dict(source=source.symbol, receiver=receiver.symbol,
                source_variant=source.variant, receiver_variant=receiver.variant,
                year=year, stage=stage, session=session, lookback=lookback,
                event_kind=kind, lag=lag, horizon=horizon)
    if ci_ok:
        for metric in PATH_METRICS:
            _add_cell(groups, group_key(metric=metric, **base), day, row.get(metric))
    if ci_ok and row.get("terminal_log") is not None:
        _add_cell(groups, group_key(metric="zero_reaction", **base), day, 1.0 if row.get("zero_reaction") else 0.0)
    _add_cell(groups, group_key(metric="no_priced", **base), day, 1.0 if row.get("terminal_log") is None else 0.0)
    _add_cell(groups, group_key(metric="no_receiver", **base), day, 1.0 if row.get("no_receiver") else 0.0)
    _add_cell(groups, group_key(metric="missing", **base), day, 1.0 if future_status == "no_receiver" else 0.0)
    _add_cell(groups, group_key(metric="stale", **base), day, 1.0 if row.get("receiver_ref_join") == "stale" else 0.0)
    _add_cell(groups, group_key(metric="roll", **base), day, 1.0 if future_status == "roll" else 0.0)
    _add_cell(groups, group_key(metric="censor", **base), day, 1.0 if future_status == "censored" else 0.0)
    concord = row.get("concordance")
    if concord in ("concordant", "discordant"):
        _add_cell(groups, group_key(metric="concordant_nonzero", **base), day, 1.0 if concord == "concordant" else 0.0)
    if ci_ok and row.get("terminal_log") is not None:
        _add_cell(groups, group_key(metric="zero_receiver", **base), day, 1.0 if concord == "zero_receiver" else 0.0)
    _add_cell(groups, group_key(metric="source_events_total", **base), day, 1.0)


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
            "file_id": row.get("file_id"), "source_sha256": row.get("source_sha256"),
            "date_order_ok": row.get("date_order_ok"), "duplicate": row.get("duplicate"),
            "gap_not_compressed": row.get("gap_not_compressed"),
            "actual_received_at_ns": None,
        })
    for row in action_rows:
        writer.add({
            "date": row["date"], "symbol": row["symbol"], "role": "corporate_actions",
            "close": None, "adjusted_close": None, "raw_log_return": None,
            "adjusted_log_return": None, "dividend": row.get("dividend"),
            "split_ratio": row.get("split_ratio"), "action_labels": row.get("action_labels"),
            "known_at_ns": None, "causal_feature_eligible": False,
            "clock": "date_only", "in_primary_cohort": row.get("in_primary_cohort"),
            "file_id": row.get("file_id"), "source_sha256": row.get("source_sha256"),
            "date_order_ok": row.get("date_order_ok"), "duplicate": row.get("duplicate"),
            "gap_not_compressed": False, "actual_received_at_ns": None,
        })


def _write_date_aggregates(writer, groups):
    for key, payload in groups.items():
        (metric, source, receiver, source_variant, receiver_variant,
         year, stage, session, lookback, kind, lag, horizon) = key
        days = set(payload["sum"]) | set(payload["count"])
        for day in sorted(days):
            count = int(payload["count"].get(day, 0))
            total = payload["sum"].get(day, 0.0)
            writer.add({
                "date": day, "year": year, "stage": stage, "session": session,
                "source_symbol": source, "receiver_symbol": receiver,
                "source_variant": source_variant, "receiver_variant": receiver_variant,
                "metric": metric, "sum": total, "event_count": count,
                "date_mean": None if count == 0 else total / count,
                "horizon_minutes": horizon, "lag_s": lag, "lookback_minutes": lookback,
                "event_kind": kind,
            })


def _group_intended(groups, all_dates, calendar_dates_by_year_stage):
    intended = {}
    for key in groups:
        year, stage = key[5], key[6]
        universe = calendar_dates_by_year_stage.get((year, stage))
        if universe is None:
            universe = [day for day in all_dates if stage_of(date.fromisoformat(day)) == stage
                        and date.fromisoformat(day).year == year]
        intended[key] = universe
    return intended


def _metric_class(key) -> str:
    metric = key[0] if isinstance(key, tuple) else str(key)
    if metric.startswith("coverage") or metric in (
            "lookback_logret", "relative_volume", "daily_raw_log_return", "daily_adjusted_log_return"):
        return "feature/activity"
    if metric.startswith("smt") or metric == "running_vs_pivot":
        return "SMT"
    if metric.startswith("mapping"):
        return "mapping"
    if metric in PATH_METRICS or metric in LIFE_METRICS:
        return "event paths"
    if metric in ("lag_contrast",):
        return "delay/source comparisons"
    return "other"


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
        "## Distinct counts",
        "",
        f"- Raw source rows: {counts.get('raw_source_rows')}",
        f"- Source events: {counts.get('source_events')}",
        f"- Event-receiver links: {counts.get('event_links')}",
        f"- Receiver future labels: {counts.get('receiver_labels')}",
        f"- Aligned cuts: {counts.get('aligned_cuts')}",
        f"- Lookback rows: {counts.get('lookbacks')}",
        f"- Price SMT rows: {counts.get('smt')}",
        f"- Mapping rows: {counts.get('mapping')}",
        f"- Timing/pivot contrast rows: {counts.get('contrasts')}",
        f"- Daily observational rows: {counts.get('daily')}",
        f"- Valid minute bars: {counts.get('valid_bars')}",
        f"- Invalid/quarantined minute bars: {counts.get('invalid_bars')}",
        "",
    ]
    if quality:
        lines.append("## Source quality and identity")
        lines.append("")
        for row in quality:
            lines.append(
                f"- `{row['symbol']}` {row['variant']} {row['year']} file_id={row['file_id']}: "
                f"{row['valid_rows']}/{row['rows']} valid; unit={row['volume_unit']}")
        lines.append("")
    lines.append("## Prespecified findings by metric class")
    lines.append("")
    lines.append("Each class reports date-mean estimate, bootstrap interval, and restored event/date support.")
    lines.append("Coverage-only groups are not a substitute for SMT, mapping, path, or delay classes.")
    lines.append("")
    class_order = (
        "feature/activity", "SMT", "mapping", "event paths", "delay/source comparisons", "other",
    )
    by_class = {name: [] for name in class_order}
    for key, payload in statistics.items():
        by_class.setdefault(_metric_class(key), []).append((key, payload))
    for class_name in class_order:
        rows = by_class.get(class_name) or []
        lines.append(f"### {class_name}")
        lines.append("")
        if not rows:
            lines.append("- No groups in this class.")
            lines.append("")
            continue
        defined = 0
        undefined = 0
        for key, payload in rows:
            metric = key[0] if isinstance(key, tuple) else key
            if payload.get("status") == "undefined":
                undefined += 1
                continue
            defined += 1
            stats = payload.get("statistics") or {}
            grp_support = payload.get("support") or stats.get("support") or {}
            boot = stats.get("bootstrap") or {}
            lines.append(
                f"- `{metric}` {key[1] if isinstance(key, tuple) else ''}"
                f"->{key[2] if isinstance(key, tuple) else ''} "
                f"variants={key[3:5] if isinstance(key, tuple) else None} "
                f"year/stage/session={key[5:8] if isinstance(key, tuple) else None} "
                f"kind={key[9] if isinstance(key, tuple) else None} "
                f"lag={key[10] if isinstance(key, tuple) else None} "
                f"horizon={key[11] if isinstance(key, tuple) else None} "
                f"lookback={key[8] if isinstance(key, tuple) else None}: "
                f"estimate={stats.get('estimate')} "
                f"CI=[{boot.get('lower')}, {boot.get('upper')}] "
                f"events={grp_support.get('events')} dates={grp_support.get('independent_dates')} "
                f"sparse={grp_support.get('sparse')}"
            )
        lines.append(f"- Class groups defined={defined} undefined={undefined} total={len(rows)}")
        lines.append("")
    if support:
        lines.append("## Independent date support")
        lines.append("")
        lines.append(f"- Primary dates: {support.get('primary_dates')}")
        lines.append(f"- original_nq2024 dates: {support.get('original_nq2024_dates')}")
        lines.append(f"- Doubled if pooled: {support.get('independent_support_if_doubled')}")
        lines.append(f"- Doubled flag: {support.get('doubled')}")
        lines.append("")
    lines.append("## Resources")
    lines.append("")
    lines.append(f"- CPU seconds: {resources.get('cpu_seconds')}")
    lines.append(f"- Wall seconds: {resources.get('wall_seconds')}")
    lines.append(f"- Output bytes: {resources.get('output_bytes')}")
    lines.append("")
    lines.append(f"Readable refs: {sorted(refs)}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    return value


def _concat_series(ref):
    pa = _pa()
    tables = list(read_series_tables(ref))
    if not tables:
        return None
    return pa.concat_tables(tables)


def reconstruct_joint_event_rows(refs) -> list[dict]:
    events = _concat_series(refs["source_events"])
    labels = _concat_series(refs["receiver_labels"])
    links = _concat_series(refs["event_links"])
    if events is None or links is None:
        return []
    event_by_id = {int(row["event_id"]): row for row in events.to_pylist()}
    label_by_id = {}
    if labels is not None:
        for row in labels.to_pylist():
            if row.get("label_id") is not None:
                label_by_id[int(row["label_id"])] = row
    out = []
    for link in links.to_pylist():
        event = dict(event_by_id.get(int(link["event_id"]), {}))
        label = dict(label_by_id.get(int(link["label_id"]), {})) if link.get("label_id") is not None else {}
        out.append({**event, **label, **link})
    return out


def run(*, protocol: dict, admitted: dict, store, outputs: BoundedOutputs,
        selected_years: list[int] | None = None, fixture_units: dict | None = None,
        fixture_daily=None, fixture_dates=None) -> dict:
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
        "source_events": _SeriesWriter(outputs, "source-events", source_event_schema()),
        "receiver_labels": _SeriesWriter(outputs, "receiver-labels", receiver_label_schema()),
        "event_links": _SeriesWriter(outputs, "event-links", event_link_schema()),
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
    valid_bars = invalid_bars = raw_source_rows = 0
    event_seq = [1]
    label_ids = {}
    if fixture_daily is None and fixture_units is None:
        cash_rows, action_rows = load_daily_observational(
            admitted, maximum_bytes=maximum_bytes, calendar=calendar)
    else:
        cash_rows, action_rows = fixture_daily or ([], [])
    _write_daily(writers["daily"], cash_rows, action_rows)
    for row in cash_rows:
        if not row.get("in_primary_cohort") or int(row["date"][:4]) not in years:
            continue
        day = date.fromisoformat(row["date"])
        stage = stage_of(day) or "outside_primary"
        for metric, field in (
            ("daily_raw_log_return", "raw_log_return"),
            ("daily_adjusted_log_return", "adjusted_log_return"),
        ):
            key = group_key(
                metric=metric, source=row["symbol"], receiver="",
                source_variant="primary_corrected", receiver_variant="",
                year=day.year, stage=stage, session="cash_rth",
                lookback=None, event_kind=None, lag=None, horizon=None)
            groups[key]
            _add_cell(groups, key, row["date"], row.get(field))
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
                if source["symbol"] in ("NQ", "ES"):
                    continue
                unit = load_raw_unit(item, maximum_bytes=maximum_bytes)
                units[(unit.symbol, unit.variant, unit.year)] = unit
        if not units:
            if fixture_dates is None:
                for cash in year_cash_days(calendar, year, None):
                    intended_all.append(cash.day.isoformat())
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
            raw_source_rows += len(unit)
        process_year(
            year=year, units=units, calendar=calendar, writers=writers, groups=groups,
            intended_dates=intended_all, carry=carry, variant_dates=variant_dates,
            fixture_dates=fixture_dates, event_seq=event_seq, label_ids=label_ids,
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
        "raw_source_rows": raw_source_rows,
        "daily_cash": len(cash_rows),
        "corporate_actions": len(action_rows),
    }
    for name, writer in writers.items():
        refs[name] = writer.finish()
        counts[{
            "cuts": "aligned_cuts", "date_agg": "date_aggregates",
            "source_events": "source_events", "event_links": "event_links",
            "receiver_labels": "receiver_labels",
        }.get(name, name)] = writer.rows
    date_support = independent_date_support(variant_dates)
    resources = {
        "cpu_seconds": time_mod.process_time() - started_cpu,
        "wall_seconds": time_mod.perf_counter() - started_wall,
        "output_bytes": outputs.written,
        "per_year": partition_measurements,
    }
    file_lookup = [
        {
            "file_id": row["file_id"], "symbol": row["symbol"], "variant": row["variant"],
            "year": row["year"], "source_sha256": row["source_sha256"],
            "source_version": row["source_version"], "instrument_kind": row["instrument_kind"],
            "contract_names": row["contract_names"],
        }
        for row in quality
    ]
    report = write_results_md(counts, statistics, resources, refs, quality, date_support)
    with outputs.create("results.md") as stream:
        stream.write(report.encode())
    refs["results_md"] = outputs.reference("results.md", kind="cross_market_results_markdown_v1")
    refs["statistics"] = outputs.json("statistics.json", _jsonable({
        "kind": "cross_market_date_statistics_v1",
        "seed": STAT_SEED, "block_length": STAT_BLOCK, "replicates": STAT_REPLICATES,
        "confidence": STAT_CONFIDENCE, "groups": {str(k): v for k, v in statistics.items()},
        "independent_date_support": date_support,
    }), kind="cross_market_statistics_v1")
    refs["source_quality"] = outputs.json("source-quality.json", quality, kind="cross_market_source_quality_v1")
    refs["file_lookup"] = outputs.json("file-lookup.json", file_lookup, kind="cross_market_file_lookup_v1")
    refs["completeness"] = outputs.json("completeness.json", {
        "kind": "cross_market_completeness_manifest_v1",
        "family": FAMILY,
        "alignment_version": ALIGN_VERSION,
        "descriptive_version": VERSION,
        "full_family_complete": False,
        "scope": "observed-minute-price-branch",
        "purpose": PURPOSE,
        "years": years,
        "intended_dates": unique_dates,
        "counts": {
            "raw_source_rows": raw_source_rows,
            "source_events": counts.get("source_events"),
            "event_links": counts.get("event_links"),
            "receiver_labels": counts.get("receiver_labels"),
        },
        "local_node_presence": None,
        "daily_known_at": None,
        "actual_received_at_ns": None,
        "original_nq2024_not_doubled": True,
        "independent_date_support": date_support,
        "reconstruction": "reconstruct_joint_event_rows",
    }, kind="cross_market_completeness_manifest_v1")
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
    "group_key", "independent_date_support", "pair_timing_rows",
    "reconstruct_joint_event_rows", "restore_event_counts", "run",
    "stages_aligned_for_ci", "summarize_groups",
)
