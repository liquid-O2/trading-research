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
from trading_research.operations.artifacts import canonical_json
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_series_tables
from trading_research.research.cross_market_alignment import (
    DIRECTED_PAIRS, FAMILY, FUTURE_HORIZONS, GRID_MINUTES, JOIN_STATUS,
    LATENCY_AFTER_END_S, LOOKBACKS, MAPPING_CHAINS, PROTOCOL_KIND, REFERENCE_LOOKBACKS,
    VERSION as ALIGN_VERSION, PriorCarry, UnitBars, canonical_partitions_for_year,
    backward_join_indices, ceil_to_minute, ceil_to_minute_array, contemporaneous_ratio,
    directed_unit_pairs, economic_minute_volumes, freeze_previous_closing_ratio,
    futures_session_bounds, grid_cuts, intended_cash_dates, join_status_name,
    lagged_mapping_residual, last_available, load_canonical_unit, load_cash_calendar,
    load_daily_observational, load_raw_unit, lookup_future_window, lookup_future_windows,
    ny_wall_minute, prepare_unit, priced_ok, previous_intended_date, selected_year_list,
    session_label, session_log_rv, stage_of, stages_aligned_for_ci, stages_aligned_many,
    unit_quality_row, unit_stable_key, year_date_bounds,
)
from trading_research.research.date_statistics import observed_date_statistics, _moving_weights
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
STAT_METRIC_BATCH = 128
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


def _arrow_kind(field):
    pa = _pa()
    typ = field.type
    if pa.types.is_int64(typ):
        return "i64"
    if pa.types.is_float64(typ):
        return "f64"
    if pa.types.is_boolean(typ):
        return "bool"
    if pa.types.is_string(typ) or pa.types.is_large_string(typ):
        return "str"
    raise ContractError(f"unsupported writer field type {typ}")


class _SeriesWriter:
    """Typed columnar buffers. Scalar add remains for fixtures and tiny classes."""

    def __init__(self, outputs: BoundedOutputs, name: str, schema):
        self.schema = schema
        self.kinds = tuple(_arrow_kind(field) for field in schema)
        self.names = tuple(field.name for field in schema)
        self.series = ParquetSeries(outputs, name, maximum_rows_per_file=CHUNK)
        self.rows = 0
        self._n = 0
        self._cap = 0
        self._values = {}
        self._null = {}
        self._str = {}
        self._reserve(4096)

    def _reserve(self, cap: int):
        np = _np()
        if cap <= self._cap:
            return
        for name, kind in zip(self.names, self.kinds):
            if kind == "str":
                prev = self._str.get(name) or []
                extra = [None] * (cap - len(prev))
                self._str[name] = prev + extra
                continue
            dtype = np.int64 if kind == "i64" else (np.bool_ if kind == "bool" else np.float64)
            old = self._values.get(name)
            buf = np.empty(cap, dtype=dtype)
            mask = np.ones(cap, dtype=np.bool_)
            if old is not None and self._cap:
                buf[: self._cap] = old
                mask[: self._cap] = self._null[name]
            self._values[name] = buf
            self._null[name] = mask
        self._cap = cap

    def _grow(self, extra: int):
        need = self._n + extra
        if need <= self._cap:
            return
        cap = max(self._cap * 2, 4096)
        while cap < need:
            cap *= 2
        self._reserve(cap)

    def add(self, row: dict):
        self._grow(1)
        i = self._n
        for name, kind in zip(self.names, self.kinds):
            value = row.get(name)
            if kind == "str":
                self._str[name][i] = None if value is None else str(value)
                continue
            if value is None:
                self._null[name][i] = True
                continue
            self._null[name][i] = False
            if kind == "i64":
                if isinstance(value, float):
                    raise ContractError("int64 clocks cannot be stored through float")
                self._values[name][i] = int(value)
            elif kind == "bool":
                self._values[name][i] = bool(value)
            else:
                number = float(value)
                if not math.isfinite(number):
                    self._null[name][i] = True
                else:
                    self._values[name][i] = number
        self._n += 1
        self.rows += 1
        if self._n >= CHUNK:
            self.flush()

    def extend(self, rows: list[dict]):
        for row in rows:
            self.add(row)

    def add_columns(self, data: dict, *, length: int, nulls: dict | None = None):
        """Bounded typed batch. int64 clocks stay int64; NULL is an explicit mask."""
        if length <= 0:
            return
        np = _np()
        self._grow(length)
        start = self._n
        stop = start + length
        nulls = nulls or {}
        for name, kind in zip(self.names, self.kinds):
            column = data.get(name)
            mask = nulls.get(name)
            if kind == "str":
                dest = self._str[name]
                if column is None:
                    for i in range(length):
                        dest[start + i] = None
                    continue
                if mask is None and isinstance(column, np.ndarray) and column.dtype == object:
                    for i, value in enumerate(column.tolist()):
                        dest[start + i] = None if value is None else str(value)
                    continue
                values = column.tolist() if isinstance(column, np.ndarray) else list(column)
                for i, value in enumerate(values):
                    missing = value is None if mask is None else bool(mask[i])
                    dest[start + i] = None if missing else str(value)
                continue
            dest = self._values[name]
            dest_null = self._null[name]
            if column is None:
                dest_null[start:stop] = True
                continue
            if kind == "i64":
                arr = np.asarray(column)
                if arr.dtype.kind == "f":
                    raise ContractError("int64 clocks cannot be stored through float")
                dest[start:stop] = np.asarray(arr, dtype=np.int64)
            elif kind == "bool":
                dest[start:stop] = np.asarray(column, dtype=np.bool_)
            else:
                dest[start:stop] = np.asarray(column, dtype=np.float64)
            if mask is None:
                if kind == "f64":
                    dest_null[start:stop] = ~np.isfinite(dest[start:stop])
                else:
                    dest_null[start:stop] = False
            else:
                dest_null[start:stop] = np.asarray(mask, dtype=np.bool_)
                if kind == "f64":
                    dest_null[start:stop] |= ~np.isfinite(dest[start:stop])
        self._n = stop
        self.rows += length
        while self._n >= CHUNK:
            self.flush()

    def add_arrays(self, data: dict, *, length: int, nulls: dict | None = None):
        """Typed columnar emit used by date aggregates. Same contract as add_columns."""
        self.add_columns(data, length=length, nulls=nulls)

    def flush(self):
        pa = _pa()
        n = self._n
        if n == 0:
            return
        take = min(n, CHUNK)
        arrays = []
        for name, kind, field in zip(self.names, self.kinds, self.schema):
            if kind == "str":
                arrays.append(pa.array(self._str[name][:take], type=field.type))
                self._str[name] = self._str[name][take:] + [None] * take
            else:
                arrays.append(pa.array(self._values[name][:take].copy(), mask=self._null[name][:take], type=field.type))
                if n > take:
                    self._values[name][: n - take] = self._values[name][take:n]
                    self._null[name][: n - take] = self._null[name][take:n]
        self.series.append(pa.Table.from_arrays(arrays, schema=self.schema))
        self._n = n - take

    def finish(self):
        while self._n:
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


def add_day_values(store, key, day: str, values, *, missing=None):
    """One day reduction. None/non-finite omitted from both sum and count."""
    np = _np()
    if values is None:
        return
    arr = np.asarray(values, dtype=np.float64)
    if arr.size == 0:
        return
    ok = np.isfinite(arr)
    if missing is not None:
        ok &= ~np.asarray(missing, dtype=np.bool_)
    if not np.any(ok):
        return
    taken = arr[ok]
    payload = store[key]
    payload["sum"][day] += float(taken.sum())
    payload["count"][day] += int(taken.size)


def add_day_flags(store, key, day: str, flags):
    """0/1 (or bool) flags; every element counts, including zeros."""
    np = _np()
    arr = np.asarray(flags, dtype=np.float64)
    if arr.size == 0:
        return
    payload = store[key]
    payload["sum"][day] += float(arr.sum())
    payload["count"][day] += int(arr.size)


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


def _group_has_date_cells(payload: dict) -> bool:
    counts = payload.get("count") or {}
    return any(int(count) > 0 for count in counts.values())


def _undefined_group():
    return {
        "status": "undefined",
        "reason": "no_matches",
        "actual_valid_event_count": 0,
        "actual_valid_date_count": 0,
    }


def _metric_name(key) -> str:
    return "|".join("" if part is None else str(part) for part in key)


def _finish_metric_payload(metric, payload, intended):
    restore_event_counts(metric, payload["count"])
    means = []
    for day in intended:
        count = payload["count"].get(day, 0)
        if count:
            means.append(payload["sum"][day] / count)
    return {
        "statistics": metric,
        "distribution_date_means": _distribution(means),
        "actual_valid_event_count": metric["actual_valid_event_count"],
        "actual_valid_date_count": metric["actual_valid_date_count"],
        "support": metric["support"],
    }


def summarize_groups(groups: dict, intended_by_key: dict, *, batch_size: int = STAT_METRIC_BATCH) -> dict:
    if type(batch_size) is not int or batch_size < 1:
        raise ContractError("statistic metric batch size must be a positive integer")
    buckets = defaultdict(list)
    out = {}
    for key, payload in groups.items():
        if key not in intended_by_key:
            out[key] = _undefined_group()
            continue
        intended = intended_by_key[key]
        if not intended:
            continue
        buckets[tuple(intended)].append((key, payload, intended))
    np = _np()
    weight_cache = {}
    for universe, items in buckets.items():
        nonempty = []
        for key, payload, intended in items:
            if _group_has_date_cells(payload):
                nonempty.append((key, payload, intended))
            else:
                out[key] = _undefined_group()
        if not nonempty:
            continue
        state = weight_cache.get(universe)
        if state is None:
            weights, starts = _moving_weights(
                np, len(universe), seed=STAT_SEED, block_length=STAT_BLOCK,
                replicates=STAT_REPLICATES)
            state = (np, weights, starts)
            weight_cache[universe] = state
        intended_dates = nonempty[0][2]
        for start in range(0, len(nonempty), batch_size):
            batch = nonempty[start:start + batch_size]
            metrics = {}
            names = {}
            for key, payload, _intended in batch:
                name = _metric_name(key)
                names[name] = (key, payload)
                metrics[name] = date_cells_for_ci(payload["sum"], payload["count"])
            stats = _compact_stat(observed_date_statistics(
                metrics, intended_dates,
                estimator="date_mean", seed=STAT_SEED, block_length=STAT_BLOCK,
                replicates=STAT_REPLICATES, confidence=STAT_CONFIDENCE,
                minimum_independent_dates=STAT_MIN_DATES, minimum_events=STAT_MIN_EVENTS,
                _bootstrap_state=state,
                _retain_replicate_estimates=False,
            ))
            for name, metric in stats["metrics"].items():
                key, payload = names[name]
                out[key] = _finish_metric_payload(metric, payload, intended_dates)
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


_JOIN_NAMES = None


def _join_names():
    global _JOIN_NAMES
    if _JOIN_NAMES is None:
        _JOIN_NAMES = _np().asarray(JOIN_STATUS, dtype=object)
    return _JOIN_NAMES


def _join_columns(prep, indices, statuses, cuts, lag):
    np = _np()
    unit = prep.unit
    indices = np.asarray(indices, dtype=np.int64)
    statuses = np.asarray(statuses, dtype=np.int8)
    cuts = np.asarray(cuts, dtype=np.int64)
    n = int(cuts.size)
    present = indices >= 0
    start = np.zeros(n, dtype=np.int64)
    end = np.zeros(n, dtype=np.int64)
    known = np.zeros(n, dtype=np.int64)
    age = np.zeros(n, dtype=np.int64)
    close = np.full(n, np.nan, dtype=np.float64)
    high = np.full(n, np.nan, dtype=np.float64)
    low = np.full(n, np.nan, dtype=np.float64)
    volume = np.full(n, np.nan, dtype=np.float64)
    inst = np.full(n, -1, dtype=np.int64)
    valid = np.zeros(n, dtype=np.bool_)
    ckey = np.empty(n, dtype=object)
    ckey[:] = None
    join = np.empty(n, dtype=object)
    names = _join_names()
    ok_status = (statuses >= 0) & (statuses < names.size)
    join[:] = "undefined"
    join[ok_status] = names[statuses[ok_status]]
    if np.any(present):
        take = indices[present]
        clock = unit.known_for(lag)
        start[present] = unit.start_ns[take]
        end[present] = unit.end_ns[take]
        known[present] = clock[take]
        age[present] = cuts[present] - unit.end_ns[take]
        close[present] = unit.close[take]
        high[present] = unit.high[take]
        low[present] = unit.low[take]
        valid[present] = unit.valid[take]
        inst[present] = unit.instrument_id[take]
        ckey[present] = prep.contract_key[take]
        finite = present & np.isfinite(close)
        close[~finite] = np.nan
        vol_ok = present & valid
        if np.any(vol_ok):
            volume[vol_ok] = unit.volume[indices[vol_ok]]
    priced = (join == "fresh") & valid & (close > 0.0) & np.isfinite(close)
    observed = (join == "fresh") | (join == "stale")
    return {
        "index": indices, "join": join, "start_ns": start, "end_ns": end,
        "known_at_ns": known, "age_ns": age, "close": close, "high": high,
        "low": low, "volume": volume, "instrument_id": inst, "contract_key": ckey,
        "valid": valid, "priced": priced, "observed": observed, "missing": ~present,
        "stale": join == "stale",
    }


def _object_fill(n, value):
    np = _np()
    out = np.empty(n, dtype=object)
    out[:] = value
    return out


def _gather_bool(table, indices, present):
    np = _np()
    out = np.zeros(indices.size, dtype=np.bool_)
    if np.any(present):
        out[present] = table[indices[present]]
    return out


def _gather_f64(table, indices, present):
    np = _np()
    out = np.full(indices.size, np.nan, dtype=np.float64)
    if np.any(present):
        out[present] = table[indices[present]]
    return out


def _gather_i64(table, indices, present, fill=-1):
    np = _np()
    out = np.full(indices.size, fill, dtype=np.int64)
    if np.any(present):
        out[present] = table[indices[present]]
    return out


def _session_splits(session_arr):
    splits = []
    for session in SESSIONS:
        sel = session_arr == session
        if sel.any():
            splits.append((session, sel))
    return splits


def _carry_lookback_extras(carry_unit, unit, prep, indices, prior_dates, zone):
    np = _np()
    rel = np.full(indices.size, np.nan, dtype=np.float64)
    reason = np.empty(indices.size, dtype=object)
    reason[:] = None
    scale = np.full(indices.size, np.nan, dtype=np.float64)
    present = indices >= 0
    if not np.any(present):
        return rel, reason, scale
    take = indices[present]
    uniq, inverse = np.unique(take, return_inverse=True)
    rel_u = np.full(uniq.size, np.nan, dtype=np.float64)
    reason_u = np.empty(uniq.size, dtype=object)
    reason_u[:] = None
    scale_u = np.full(uniq.size, np.nan, dtype=np.float64)
    scale_by_key = {}
    for i, raw in enumerate(uniq.tolist()):
        index = int(raw)
        value, why = carry_unit.relative_volume(
            ny_wall_minute(int(unit.start_ns[index]), zone),
            float(unit.volume[index]), prior_dates)
        if value is not None:
            rel_u[i] = float(value)
        reason_u[i] = why
        key = prep.contract_key[index]
        if key not in scale_by_key:
            scale_by_key[key] = carry_unit.prior_rth_scale(key, prior_dates)
        sc = scale_by_key[key]
        if sc is not None:
            scale_u[i] = float(sc)
    rel[present] = rel_u[inverse]
    reason[present] = reason_u[inverse]
    scale[present] = scale_u[inverse]
    return rel, reason, scale


def _smt_payload(kind, src, rcv, src_prep, rcv_prep, length):
    np = _np()
    src_i = src["index"]
    rcv_i = rcv["index"]
    src_present = ~src["missing"]
    rcv_present = ~rcv["missing"]
    if kind == "running":
        src_state = src_prep.running[length]
        rcv_state = rcv_prep.running[length]
        src_def = _gather_bool(src_state["defined"], src_i, src_present)
        rcv_def = _gather_bool(rcv_state["defined"], rcv_i, rcv_present)
        src_known = src["priced"] & src_def
        rcv_known = rcv["priced"] & rcv_def
        src_h = src_known & _gather_bool(src_state["high_breach"], src_i, src_present)
        src_l = src_known & _gather_bool(src_state["low_breach"], src_i, src_present)
        rcv_h = rcv_known & _gather_bool(rcv_state["high_breach"], rcv_i, rcv_present)
        rcv_l = rcv_known & _gather_bool(rcv_state["low_breach"], rcv_i, rcv_present)
        sph = _gather_f64(src_state["prior_high"], src_i, src_known)
        spl = _gather_f64(src_state["prior_low"], src_i, src_known)
        rph = _gather_f64(rcv_state["prior_high"], rcv_i, rcv_known)
        rpl = _gather_f64(rcv_state["prior_low"], rcv_i, rcv_known)
    else:
        src_p = src_prep.pivot
        rcv_p = rcv_prep.pivot
        src_hk = _gather_i64(src_p["high_known_end_ns"], src_i, src_present)
        src_lk = _gather_i64(src_p["low_known_end_ns"], src_i, src_present)
        rcv_hk = _gather_i64(rcv_p["high_known_end_ns"], rcv_i, rcv_present)
        rcv_lk = _gather_i64(rcv_p["low_known_end_ns"], rcv_i, rcv_present)
        src_known = src["priced"] & (src_hk >= 0) & (src_lk >= 0)
        rcv_known = rcv["priced"] & (rcv_hk >= 0) & (rcv_lk >= 0)
        src_h = src_known & _gather_bool(src_p["high_breach"], src_i, src_present)
        src_l = src_known & _gather_bool(src_p["low_breach"], src_i, src_present)
        rcv_h = rcv_known & _gather_bool(rcv_p["high_breach"], rcv_i, rcv_present)
        rcv_l = rcv_known & _gather_bool(rcv_p["low_breach"], rcv_i, rcv_present)
        sph = _gather_f64(src_p["high_level"], src_i, src_known)
        spl = _gather_f64(src_p["low_level"], src_i, src_known)
        rph = _gather_f64(rcv_p["high_level"], rcv_i, rcv_known)
        rpl = _gather_f64(rcv_p["low_level"], rcv_i, rcv_known)
    state = np.empty(src_known.size, dtype=object)
    unknown = ~src_known | ~rcv_known
    source = src_h | src_l
    receiver = rcv_h | rcv_l
    state[unknown] = "unknown"
    both = ~unknown & source & receiver
    src_only = ~unknown & source & ~receiver
    rcv_only = ~unknown & ~source & receiver
    neither = ~unknown & ~source & ~receiver
    state[both] = "both"
    state[src_only] = "source_only"
    state[rcv_only] = "receiver_only"
    state[neither] = "neither"
    excursion = np.zeros(src_known.size, dtype=np.float64)
    high_ok = src_known & src_h & (sph > 0.0) & np.isfinite(sph) & (src["high"] > 0.0)
    low_ok = src_known & src_l & (spl > 0.0) & np.isfinite(spl) & (src["low"] > 0.0)
    if np.any(high_ok):
        excursion[high_ok] = np.maximum(0.0, np.log(src["high"][high_ok] / sph[high_ok]))
    if np.any(low_ok):
        low_exc = np.maximum(0.0, np.log(spl[low_ok] / src["low"][low_ok]))
        excursion[low_ok] = np.maximum(excursion[low_ok], low_exc)
    return {
        "src_known": src_known, "rcv_known": rcv_known,
        "src_h": src_h, "src_l": src_l, "rcv_h": rcv_h, "rcv_l": rcv_l,
        "sph": sph, "spl": spl, "rph": rph, "rpl": rpl,
        "state": state, "excursion": excursion, "exc_missing": ~src_known,
    }


def _emit_cut_grid(*, year, units, prepared, by_obj, pairs, cuts, session_arr, day,
                   stage, writers, groups, carry, previous_by_day, cash, calendar,
                   prior_dates):
    np = _np()
    n_cuts = int(cuts.size)
    if n_cuts == 0:
        return
    joins = {}
    for key, prep in prepared.items():
        for lag in LATENCY_AFTER_END_S:
            idx, status = backward_join_indices(prep.unit.known_for(lag), cuts, prep.unit.end_ns)
            joins[(key, lag)] = _join_columns(prep, idx, status, cuts, lag)
    splits = _session_splits(session_arr)
    for session, sel in splits:
        for unit in units.values():
            for lag in LATENCY_AFTER_END_S:
                src = joins[(by_obj[id(unit)], lag)]
                add_day_flags(groups, group_key(
                    metric="coverage_own_eligible", source=unit.symbol, receiver="",
                    source_variant=unit.variant, receiver_variant="",
                    year=year, stage=stage, session=session, lookback=None,
                    event_kind=None, lag=lag, horizon=None), day, src["priced"][sel])
                add_day_flags(groups, group_key(
                    metric="coverage_own_observed", source=unit.symbol, receiver="",
                    source_variant=unit.variant, receiver_variant="",
                    year=year, stage=stage, session=session, lookback=None,
                    event_kind=None, lag=lag, horizon=None), day, src["observed"][sel])
                add_day_flags(groups, group_key(
                    metric="coverage_own_stale", source=unit.symbol, receiver="",
                    source_variant=unit.variant, receiver_variant="",
                    year=year, stage=stage, session=session, lookback=None,
                    event_kind=None, lag=lag, horizon=None), day, src["stale"][sel])
    n_pairs = len(pairs)
    n_lags = len(LATENCY_AFTER_END_S)
    if n_pairs:
        stride = n_pairs * n_lags
        n_cut_rows = n_cuts * stride
        dest_base = np.arange(n_cuts, dtype=np.int64) * stride
        cut_out = {
            "date": _object_fill(n_cut_rows, day),
            "year": np.full(n_cut_rows, year, dtype=np.int64),
            "stage": _object_fill(n_cut_rows, stage),
            "session": np.empty(n_cut_rows, dtype=object),
            "source_symbol": np.empty(n_cut_rows, dtype=object),
            "receiver_symbol": np.empty(n_cut_rows, dtype=object),
            "source_variant": np.empty(n_cut_rows, dtype=object),
            "receiver_variant": np.empty(n_cut_rows, dtype=object),
            "cut_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "lag_s": np.zeros(n_cut_rows, dtype=np.int64),
            "source_start_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "source_end_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "source_known_at_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "source_age_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "source_join": np.empty(n_cut_rows, dtype=object),
            "source_close": np.full(n_cut_rows, np.nan, dtype=np.float64),
            "source_volume": np.full(n_cut_rows, np.nan, dtype=np.float64),
            "source_instrument_id": np.full(n_cut_rows, -1, dtype=np.int64),
            "source_contract_key": np.empty(n_cut_rows, dtype=object),
            "source_file_id": np.zeros(n_cut_rows, dtype=np.int64),
            "receiver_start_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "receiver_known_at_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "receiver_age_ns": np.zeros(n_cut_rows, dtype=np.int64),
            "receiver_join": np.empty(n_cut_rows, dtype=object),
            "receiver_close": np.full(n_cut_rows, np.nan, dtype=np.float64),
            "receiver_instrument_id": np.full(n_cut_rows, -1, dtype=np.int64),
            "receiver_contract_key": np.empty(n_cut_rows, dtype=object),
            "own_eligible": np.zeros(n_cut_rows, dtype=np.bool_),
            "own_observed": np.zeros(n_cut_rows, dtype=np.bool_),
            "own_stale": np.zeros(n_cut_rows, dtype=np.bool_),
            "common_coverage": np.zeros(n_cut_rows, dtype=np.bool_),
            "definition_certified": np.zeros(n_cut_rows, dtype=np.bool_),
            "actual_received_at_ns": np.zeros(n_cut_rows, dtype=np.int64),
        }
        cut_nulls = {
            "source_start_ns": np.ones(n_cut_rows, dtype=np.bool_),
            "source_end_ns": np.ones(n_cut_rows, dtype=np.bool_),
            "source_known_at_ns": np.ones(n_cut_rows, dtype=np.bool_),
            "source_age_ns": np.ones(n_cut_rows, dtype=np.bool_),
            "source_close": np.ones(n_cut_rows, dtype=np.bool_),
            "source_volume": np.ones(n_cut_rows, dtype=np.bool_),
            "source_instrument_id": np.ones(n_cut_rows, dtype=np.bool_),
            "receiver_start_ns": np.ones(n_cut_rows, dtype=np.bool_),
            "receiver_known_at_ns": np.ones(n_cut_rows, dtype=np.bool_),
            "receiver_age_ns": np.ones(n_cut_rows, dtype=np.bool_),
            "receiver_close": np.ones(n_cut_rows, dtype=np.bool_),
            "receiver_instrument_id": np.ones(n_cut_rows, dtype=np.bool_),
            "actual_received_at_ns": np.ones(n_cut_rows, dtype=np.bool_),
        }
        smt_slots = (("running", 15), ("running", 60), ("pivot", 15))
        n_smt_slots = len(smt_slots)
        n_smt = n_cut_rows * n_smt_slots
        smt_dest_base = dest_base * n_smt_slots
        smt_out = {
            "date": _object_fill(n_smt, day),
            "year": np.full(n_smt, year, dtype=np.int64),
            "stage": _object_fill(n_smt, stage),
            "session": np.empty(n_smt, dtype=object),
            "source_symbol": np.empty(n_smt, dtype=object),
            "receiver_symbol": np.empty(n_smt, dtype=object),
            "source_variant": np.empty(n_smt, dtype=object),
            "receiver_variant": np.empty(n_smt, dtype=object),
            "cut_ns": np.zeros(n_smt, dtype=np.int64),
            "lag_s": np.zeros(n_smt, dtype=np.int64),
            "lookback_minutes": np.zeros(n_smt, dtype=np.int64),
            "kind": np.empty(n_smt, dtype=object),
            "source_own_breach_high": np.zeros(n_smt, dtype=np.bool_),
            "source_own_breach_low": np.zeros(n_smt, dtype=np.bool_),
            "receiver_own_breach_high": np.zeros(n_smt, dtype=np.bool_),
            "receiver_own_breach_low": np.zeros(n_smt, dtype=np.bool_),
            "source_prior_high": np.full(n_smt, np.nan, dtype=np.float64),
            "source_prior_low": np.full(n_smt, np.nan, dtype=np.float64),
            "receiver_prior_high": np.full(n_smt, np.nan, dtype=np.float64),
            "receiver_prior_low": np.full(n_smt, np.nan, dtype=np.float64),
            "source_close": np.full(n_smt, np.nan, dtype=np.float64),
            "receiver_close": np.full(n_smt, np.nan, dtype=np.float64),
            "breach_state": np.empty(n_smt, dtype=object),
            "common_cut": np.zeros(n_smt, dtype=np.bool_),
            "source_relative_excursion": np.full(n_smt, np.nan, dtype=np.float64),
        }
        smt_nulls = {
            "source_own_breach_high": np.ones(n_smt, dtype=np.bool_),
            "source_own_breach_low": np.ones(n_smt, dtype=np.bool_),
            "receiver_own_breach_high": np.ones(n_smt, dtype=np.bool_),
            "receiver_own_breach_low": np.ones(n_smt, dtype=np.bool_),
            "source_prior_high": np.ones(n_smt, dtype=np.bool_),
            "source_prior_low": np.ones(n_smt, dtype=np.bool_),
            "receiver_prior_high": np.ones(n_smt, dtype=np.bool_),
            "receiver_prior_low": np.ones(n_smt, dtype=np.bool_),
            "source_close": np.ones(n_smt, dtype=np.bool_),
            "receiver_close": np.ones(n_smt, dtype=np.bool_),
            "source_relative_excursion": np.ones(n_smt, dtype=np.bool_),
        }
        contrast_blocks = []
        for pair_i, (source, receiver) in enumerate(pairs):
            source_key = by_obj[id(source)]
            receiver_key = by_obj[id(receiver)]
            src_prep = prepared[source_key]
            rcv_prep = prepared[receiver_key]
            for lag_i, lag in enumerate(LATENCY_AFTER_END_S):
                dest = dest_base + pair_i * n_lags + lag_i
                src = joins[(source_key, lag)]
                rcv = joins[(receiver_key, lag)]
                cut_out["session"][dest] = session_arr
                cut_out["source_symbol"][dest] = source.symbol
                cut_out["receiver_symbol"][dest] = receiver.symbol
                cut_out["source_variant"][dest] = source.variant
                cut_out["receiver_variant"][dest] = receiver.variant
                cut_out["cut_ns"][dest] = cuts
                cut_out["lag_s"][dest] = lag
                cut_out["source_start_ns"][dest] = src["start_ns"]
                cut_out["source_end_ns"][dest] = src["end_ns"]
                cut_out["source_known_at_ns"][dest] = src["known_at_ns"]
                cut_out["source_age_ns"][dest] = src["age_ns"]
                cut_out["source_join"][dest] = src["join"]
                cut_out["source_close"][dest] = src["close"]
                cut_out["source_volume"][dest] = src["volume"]
                cut_out["source_instrument_id"][dest] = src["instrument_id"]
                cut_out["source_contract_key"][dest] = src["contract_key"]
                cut_out["source_file_id"][dest] = source.file_id
                cut_out["receiver_start_ns"][dest] = rcv["start_ns"]
                cut_out["receiver_known_at_ns"][dest] = rcv["known_at_ns"]
                cut_out["receiver_age_ns"][dest] = rcv["age_ns"]
                cut_out["receiver_join"][dest] = rcv["join"]
                cut_out["receiver_close"][dest] = rcv["close"]
                cut_out["receiver_instrument_id"][dest] = rcv["instrument_id"]
                cut_out["receiver_contract_key"][dest] = rcv["contract_key"]
                cut_out["own_eligible"][dest] = src["priced"]
                cut_out["own_observed"][dest] = src["observed"]
                cut_out["own_stale"][dest] = src["stale"]
                common = src["priced"] & rcv["priced"]
                cut_out["common_coverage"][dest] = common
                cut_out["definition_certified"][dest] = source.definition_certified
                cut_nulls["source_start_ns"][dest] = src["missing"]
                cut_nulls["source_end_ns"][dest] = src["missing"]
                cut_nulls["source_known_at_ns"][dest] = src["missing"]
                cut_nulls["source_age_ns"][dest] = src["missing"]
                cut_nulls["source_close"][dest] = ~src["observed"]
                cut_nulls["source_volume"][dest] = ~src["priced"]
                cut_nulls["source_instrument_id"][dest] = src["missing"]
                cut_nulls["receiver_start_ns"][dest] = rcv["missing"]
                cut_nulls["receiver_known_at_ns"][dest] = rcv["missing"]
                cut_nulls["receiver_age_ns"][dest] = rcv["missing"]
                cut_nulls["receiver_close"][dest] = ~rcv["observed"]
                cut_nulls["receiver_instrument_id"][dest] = rcv["missing"]
                for session, sel in splits:
                    add_day_flags(groups, group_key(
                        metric="coverage_common", source=source.symbol, receiver=receiver.symbol,
                        source_variant=source.variant, receiver_variant=receiver.variant,
                        year=year, stage=stage, session=session, lookback=None,
                        event_kind=None, lag=lag, horizon=None), day, common[sel])
                for slot_i, (kind, length) in enumerate(smt_slots):
                    payload = _smt_payload(kind, src, rcv, src_prep, rcv_prep, length)
                    sdest = smt_dest_base + (pair_i * n_lags + lag_i) * n_smt_slots + slot_i
                    smt_out["session"][sdest] = session_arr
                    smt_out["source_symbol"][sdest] = source.symbol
                    smt_out["receiver_symbol"][sdest] = receiver.symbol
                    smt_out["source_variant"][sdest] = source.variant
                    smt_out["receiver_variant"][sdest] = receiver.variant
                    smt_out["cut_ns"][sdest] = cuts
                    smt_out["lag_s"][sdest] = lag
                    smt_out["lookback_minutes"][sdest] = length
                    smt_out["kind"][sdest] = kind
                    smt_out["source_own_breach_high"][sdest] = payload["src_h"]
                    smt_out["source_own_breach_low"][sdest] = payload["src_l"]
                    smt_out["receiver_own_breach_high"][sdest] = payload["rcv_h"]
                    smt_out["receiver_own_breach_low"][sdest] = payload["rcv_l"]
                    smt_out["source_prior_high"][sdest] = payload["sph"]
                    smt_out["source_prior_low"][sdest] = payload["spl"]
                    smt_out["receiver_prior_high"][sdest] = payload["rph"]
                    smt_out["receiver_prior_low"][sdest] = payload["rpl"]
                    smt_out["source_close"][sdest] = src["close"]
                    smt_out["receiver_close"][sdest] = rcv["close"]
                    smt_out["breach_state"][sdest] = payload["state"]
                    smt_out["common_cut"][sdest] = payload["src_known"] & payload["rcv_known"]
                    smt_out["source_relative_excursion"][sdest] = payload["excursion"]
                    smt_nulls["source_own_breach_high"][sdest] = ~payload["src_known"]
                    smt_nulls["source_own_breach_low"][sdest] = ~payload["src_known"]
                    smt_nulls["receiver_own_breach_high"][sdest] = ~payload["rcv_known"]
                    smt_nulls["receiver_own_breach_low"][sdest] = ~payload["rcv_known"]
                    smt_nulls["source_prior_high"][sdest] = ~payload["src_known"]
                    smt_nulls["source_prior_low"][sdest] = ~payload["src_known"]
                    smt_nulls["receiver_prior_high"][sdest] = ~payload["rcv_known"]
                    smt_nulls["receiver_prior_low"][sdest] = ~payload["rcv_known"]
                    smt_nulls["source_close"][sdest] = ~src["priced"]
                    smt_nulls["receiver_close"][sdest] = ~rcv["priced"]
                    smt_nulls["source_relative_excursion"][sdest] = payload["exc_missing"]
                    for session, sel in splits:
                        base = dict(source=source.symbol, receiver=receiver.symbol,
                                    source_variant=source.variant, receiver_variant=receiver.variant,
                                    year=year, stage=stage, session=session, lookback=length,
                                    event_kind=kind, lag=lag, horizon=None)
                        add_day_flags(groups, group_key(metric="smt_source_only", **base), day, payload["state"][sel] == "source_only")
                        add_day_flags(groups, group_key(metric="smt_receiver_only", **base), day, payload["state"][sel] == "receiver_only")
                        add_day_flags(groups, group_key(metric="smt_both", **base), day, payload["state"][sel] == "both")
                        add_day_flags(groups, group_key(metric="smt_neither", **base), day, payload["state"][sel] == "neither")
                        add_day_flags(groups, group_key(metric="smt_unknown", **base), day, payload["state"][sel] == "unknown")
                        add_day_values(groups, group_key(metric="smt_source_excursion", **base), day,
                                       payload["excursion"][sel], missing=payload["exc_missing"][sel])
                if src_prep.running and rcv_prep.running:
                    for length in REFERENCE_LOOKBACKS:
                        src_idx = src["index"]
                        rcv_idx = rcv["index"]
                        src_present = ~src["missing"]
                        rcv_present = ~rcv["missing"]
                        src_run = src_prep.running[length]
                        rcv_run = rcv_prep.running[length]
                        src_known = src["priced"] & _gather_bool(src_run["defined"], src_idx, src_present)
                        src_known &= (_gather_i64(src_prep.pivot["high_known_end_ns"], src_idx, src_present) >= 0)
                        src_known &= (_gather_i64(src_prep.pivot["low_known_end_ns"], src_idx, src_present) >= 0)
                        rcv_known = rcv["priced"] & _gather_bool(rcv_run["defined"], rcv_idx, rcv_present)
                        rcv_known &= (_gather_i64(rcv_prep.pivot["high_known_end_ns"], rcv_idx, rcv_present) >= 0)
                        rcv_known &= (_gather_i64(rcv_prep.pivot["low_known_end_ns"], rcv_idx, rcv_present) >= 0)
                        keep = src_known & rcv_known
                        if not np.any(keep):
                            continue
                        run_h = _gather_bool(src_run["high_breach"], src_idx, src_present)
                        run_l = _gather_bool(src_run["low_breach"], src_idx, src_present)
                        piv_h = _gather_bool(src_prep.pivot["high_breach"], src_idx, src_present)
                        piv_l = _gather_bool(src_prep.pivot["low_breach"], src_idx, src_present)
                        run_any = run_h | run_l
                        piv_any = piv_h | piv_l
                        agree = (run_any == piv_any).astype(np.float64)
                        n_keep = int(keep.sum())
                        contrast_blocks.append({
                            "n": n_keep,
                            "date": _object_fill(n_keep, day),
                            "source_symbol": _object_fill(n_keep, source.symbol),
                            "receiver_symbol": _object_fill(n_keep, receiver.symbol),
                            "source_variant": _object_fill(n_keep, source.variant),
                            "receiver_variant": _object_fill(n_keep, receiver.variant),
                            "source_contract_key": src["contract_key"][keep],
                            "receiver_contract_key": rcv["contract_key"][keep],
                            "lag_s": np.full(n_keep, lag, dtype=np.int64),
                            "terminal_a": np.where(run_any[keep], 1.0, 0.0),
                            "terminal_b": np.where(piv_any[keep], 1.0, 0.0),
                            "terminal_contrast": np.where(run_any[keep], 1.0, 0.0) - np.where(piv_any[keep], 1.0, 0.0),
                            "lookback_minutes": np.full(n_keep, length, dtype=np.int64),
                            "keep": keep,
                        })
                        for session, sel in splits:
                            take = keep & sel
                            if np.any(take):
                                add_day_flags(groups, group_key(
                                    metric="running_vs_pivot", source=source.symbol, receiver=receiver.symbol,
                                    source_variant=source.variant, receiver_variant=receiver.variant,
                                    year=year, stage=stage, session=session, lookback=length,
                                    event_kind="running_vs_pivot", lag=lag, horizon=None),
                                              day, agree[take])
        writers["cuts"].add_columns(cut_out, length=n_cut_rows, nulls=cut_nulls)
        writers["smt"].add_columns(smt_out, length=n_smt, nulls=smt_nulls)
        if contrast_blocks:
            # Preserve cut-major pair/lag/length order: blocks were appended in that order
            # but each block is all cuts for one pair/lag/length. Re-emit cut-major.
            _write_running_vs_pivot_cut_major(
                writers["contrasts"], contrast_blocks, n_cuts, pairs, n_lags)
    unit_items = list(units.items())
    n_units = len(unit_items)
    n_look = len(LOOKBACKS)
    n_lb = n_cuts * n_units * n_lags * n_look
    if n_lb:
        lb_stride = n_units * n_lags * n_look
        lb_base = np.arange(n_cuts, dtype=np.int64) * lb_stride
        lb_out = {
            "date": _object_fill(n_lb, day),
            "year": np.full(n_lb, year, dtype=np.int64),
            "stage": _object_fill(n_lb, stage),
            "session": np.empty(n_lb, dtype=object),
            "symbol": np.empty(n_lb, dtype=object),
            "variant": np.empty(n_lb, dtype=object),
            "cut_ns": np.zeros(n_lb, dtype=np.int64),
            "lag_s": np.zeros(n_lb, dtype=np.int64),
            "lookback_minutes": np.zeros(n_lb, dtype=np.int64),
            "bar_start_ns": np.zeros(n_lb, dtype=np.int64),
            "log_return": np.full(n_lb, np.nan, dtype=np.float64),
            "intervening_high": np.full(n_lb, np.nan, dtype=np.float64),
            "intervening_low": np.full(n_lb, np.nan, dtype=np.float64),
            "relative_volume": np.full(n_lb, np.nan, dtype=np.float64),
            "prior_rth_sqrt_rv": np.full(n_lb, np.nan, dtype=np.float64),
            "status": np.empty(n_lb, dtype=object),
            "volume_unit": np.empty(n_lb, dtype=object),
            "file_id": np.zeros(n_lb, dtype=np.int64),
            "contract_key": np.empty(n_lb, dtype=object),
        }
        lb_nulls = {
            "bar_start_ns": np.ones(n_lb, dtype=np.bool_),
            "log_return": np.ones(n_lb, dtype=np.bool_),
            "intervening_high": np.ones(n_lb, dtype=np.bool_),
            "intervening_low": np.ones(n_lb, dtype=np.bool_),
            "relative_volume": np.ones(n_lb, dtype=np.bool_),
            "prior_rth_sqrt_rv": np.ones(n_lb, dtype=np.bool_),
        }
        for unit_i, (key, unit) in enumerate(unit_items):
            prep = prepared[key]
            carry_unit = carry.setdefault("rel", {}).setdefault(unit_stable_key(unit), PriorCarry())
            for lag_i, lag in enumerate(LATENCY_AFTER_END_S):
                row = joins[(key, lag)]
                rel, rel_reason, scale = _carry_lookback_extras(
                    carry_unit, unit, prep, row["index"], prior_dates, calendar.zone)
                for look_i, length in enumerate(LOOKBACKS):
                    dest = lb_base + ((unit_i * n_lags + lag_i) * n_look + look_i)
                    ret, ok = prep.logret[length]
                    xhi, xlo, xok = prep.intervening[length]
                    present = ~row["missing"]
                    log_ret = _gather_f64(ret, row["index"], present & row["priced"])
                    log_ok = _gather_bool(ok, row["index"], present & row["priced"])
                    log_ret = np.where(log_ok, log_ret, np.nan)
                    hi = _gather_f64(xhi, row["index"], present & row["priced"])
                    lo = _gather_f64(xlo, row["index"], present & row["priced"])
                    x_ok = _gather_bool(xok, row["index"], present & row["priced"])
                    hi = np.where(x_ok, hi, np.nan)
                    lo = np.where(x_ok, lo, np.nan)
                    status = np.array(row["join"], copy=True)
                    invalid = present & ~row["priced"] & (row["join"] == "fresh")
                    status[invalid] = "invalid"
                    priced = row["priced"]
                    has_reason = np.fromiter((item is not None for item in rel_reason), dtype=np.bool_, count=rel_reason.size)
                    rel_missing = priced & ~np.isfinite(rel) & has_reason
                    status[rel_missing] = rel_reason[rel_missing]
                    defined = priced & ~rel_missing & np.isfinite(log_ret)
                    undefined = priced & ~rel_missing & ~np.isfinite(log_ret)
                    status[defined] = "defined"
                    status[undefined] = "undefined"
                    lb_out["session"][dest] = session_arr
                    lb_out["symbol"][dest] = unit.symbol
                    lb_out["variant"][dest] = unit.variant
                    lb_out["cut_ns"][dest] = cuts
                    lb_out["lag_s"][dest] = lag
                    lb_out["lookback_minutes"][dest] = length
                    lb_out["bar_start_ns"][dest] = row["start_ns"]
                    lb_out["log_return"][dest] = log_ret
                    lb_out["intervening_high"][dest] = hi
                    lb_out["intervening_low"][dest] = lo
                    lb_out["relative_volume"][dest] = np.where(row["priced"], rel, np.nan)
                    lb_out["prior_rth_sqrt_rv"][dest] = np.where(row["priced"], scale, np.nan)
                    lb_out["status"][dest] = status
                    lb_out["volume_unit"][dest] = unit.volume_unit
                    lb_out["file_id"][dest] = unit.file_id
                    lb_out["contract_key"][dest] = row["contract_key"]
                    lb_nulls["bar_start_ns"][dest] = row["missing"]
                    lb_nulls["log_return"][dest] = ~np.isfinite(log_ret)
                    lb_nulls["intervening_high"][dest] = ~np.isfinite(hi)
                    lb_nulls["intervening_low"][dest] = ~np.isfinite(lo)
                    lb_nulls["relative_volume"][dest] = ~row["priced"] | ~np.isfinite(rel)
                    lb_nulls["prior_rth_sqrt_rv"][dest] = ~row["priced"] | ~np.isfinite(scale)
                    for session, sel in splits:
                        add_day_values(groups, group_key(
                            metric="lookback_logret", source=unit.symbol, receiver="",
                            source_variant=unit.variant, receiver_variant="",
                            year=year, stage=stage, session=session, lookback=length,
                            event_kind=None, lag=lag, horizon=None), day, log_ret[sel])
                        add_day_values(groups, group_key(
                            metric="relative_volume", source=unit.symbol, receiver="",
                            source_variant=unit.variant, receiver_variant="",
                            year=year, stage=stage, session=session, lookback=length,
                            event_kind=None, lag=lag, horizon=None), day, rel[sel], missing=~row["priced"][sel])
        writers["lookbacks"].add_columns(lb_out, length=n_lb, nulls=lb_nulls)
    _emit_mapping_grid(
        units, prepared, by_obj, joins, cash, day, year, stage, session_arr, cuts,
        writers, groups, carry, previous_by_day, splits)


def _write_running_vs_pivot_cut_major(writer, blocks, n_cuts, pairs, n_lags):
    np = _np()
    # Each block is (pair, lag, length) over all cuts. Original order is cut, pair, lag, length.
    keyed = {}
    for block in blocks:
        # recover pair/lag/length from constant fields
        key = (
            str(block["source_symbol"][0]), str(block["receiver_symbol"][0]),
            str(block["source_variant"][0]), str(block["receiver_variant"][0]),
            int(block["lag_s"][0]), int(block["lookback_minutes"][0]),
        )
        keyed[key] = block
    order = []
    for source, receiver in pairs:
        for lag in LATENCY_AFTER_END_S:
            for length in REFERENCE_LOOKBACKS:
                key = (source.symbol, receiver.symbol, source.variant, receiver.variant, lag, length)
                if key in keyed:
                    order.append(keyed[key])
    if not order:
        return
    # Interleave kept rows in cut-major order
    keeps = [block["keep"] for block in order]
    stacked = np.stack(keeps, axis=1)
    take = stacked.ravel(order="C")
    if not np.any(take):
        return
    n = int(take.sum())
    def _stack_field(name, dtype=None):
        parts = []
        for block in order:
            parts.append(np.asarray(block[name]))
        # rebuild cut-major by placing into (n_cuts, n_blocks) then ravel
        return parts
    n_blocks = len(order)
    def _cut_major(name, dtype=object, fill=None):
        grid = np.empty((n_cuts, n_blocks), dtype=dtype)
        if fill is not None:
            grid.fill(fill)
        for j, block in enumerate(order):
            values = np.asarray(block[name])
            grid[block["keep"], j] = values
        return grid.ravel(order="C")[take]
    data = {
        "event_id": np.zeros(n, dtype=np.int64),
        "date": _cut_major("date"),
        "source_symbol": _cut_major("source_symbol"),
        "receiver_symbol": _cut_major("receiver_symbol"),
        "source_variant": _cut_major("source_variant"),
        "receiver_variant": _cut_major("receiver_variant"),
        "source_contract_key": _cut_major("source_contract_key"),
        "receiver_contract_key": _cut_major("receiver_contract_key"),
        "horizon_minutes": np.zeros(n, dtype=np.int64),
        "maturity_ns": np.zeros(n, dtype=np.int64),
        "lag_a_s": _cut_major("lag_s", dtype=np.int64, fill=0),
        "lag_b_s": _cut_major("lag_s", dtype=np.int64, fill=0),
        "pairing": _object_fill(n, "common_cut"),
        "reason": _object_fill(n, None),
        "reference_change": np.zeros(n, dtype=np.bool_),
        "common_reference": np.ones(n, dtype=np.bool_),
        "terminal_a": _cut_major("terminal_a", dtype=np.float64, fill=np.nan),
        "terminal_b": _cut_major("terminal_b", dtype=np.float64, fill=np.nan),
        "terminal_contrast": _cut_major("terminal_contrast", dtype=np.float64, fill=np.nan),
        "kind": _object_fill(n, "running_vs_pivot"),
        "lookback_minutes": _cut_major("lookback_minutes", dtype=np.int64, fill=0),
    }
    writer.add_columns(data, length=n, nulls={
        "event_id": np.ones(n, dtype=np.bool_),
        "horizon_minutes": np.ones(n, dtype=np.bool_),
        "maturity_ns": np.ones(n, dtype=np.bool_),
        "reason": np.ones(n, dtype=np.bool_),
    })


def _emit_mapping_grid(units, prepared, by_obj, joins, cash, day, year, stage, session_arr, cuts,
                       writers, groups, carry, intended_days, splits):
    np = _np()
    prior_day = intended_days.get(cash.day) if isinstance(intended_days, dict) else previous_intended_date(intended_days, cash.day)
    slots = []
    for futures_symbol, etf_symbol in MAPPING_CHAINS:
        futs = [unit for unit in units.values() if unit.symbol == futures_symbol]
        etfs = [unit for unit in units.values() if unit.symbol == etf_symbol]
        for fut in futs:
            for etf in etfs:
                for lag in LATENCY_AFTER_END_S:
                    slots.append((futures_symbol, etf_symbol, fut, etf, lag))
    n_slots = len(slots)
    n_cuts = int(cuts.size)
    if n_slots == 0 or n_cuts == 0:
        return
    n = n_cuts * n_slots
    dest_base = np.arange(n_cuts, dtype=np.int64) * n_slots
    out = {
        "date": _object_fill(n, day),
        "year": np.full(n, year, dtype=np.int64),
        "stage": _object_fill(n, stage),
        "session": np.empty(n, dtype=object),
        "futures_symbol": np.empty(n, dtype=object),
        "etf_symbol": np.empty(n, dtype=object),
        "futures_variant": np.empty(n, dtype=object),
        "etf_variant": np.empty(n, dtype=object),
        "cut_ns": np.zeros(n, dtype=np.int64),
        "lag_s": np.zeros(n, dtype=np.int64),
        "contemporaneous_ratio": np.full(n, np.nan, dtype=np.float64),
        "contemporaneous_inverse": np.full(n, np.nan, dtype=np.float64),
        "prior_ratio": np.full(n, np.nan, dtype=np.float64),
        "predicted_receiver": np.full(n, np.nan, dtype=np.float64),
        "residual_receiver_points": np.full(n, np.nan, dtype=np.float64),
        "status": np.empty(n, dtype=object),
        "reason": np.empty(n, dtype=object),
        "prior_ratio_frozen": np.ones(n, dtype=np.bool_),
        "futures_contract_key": np.empty(n, dtype=object),
        "etf_contract_key": np.empty(n, dtype=object),
        "prior_cut_ns": np.zeros(n, dtype=np.int64),
    }
    nulls = {
        "contemporaneous_ratio": np.ones(n, dtype=np.bool_),
        "contemporaneous_inverse": np.ones(n, dtype=np.bool_),
        "prior_ratio": np.ones(n, dtype=np.bool_),
        "predicted_receiver": np.ones(n, dtype=np.bool_),
        "residual_receiver_points": np.ones(n, dtype=np.bool_),
        "prior_cut_ns": np.ones(n, dtype=np.bool_),
    }
    for slot_i, (futures_symbol, etf_symbol, fut, etf, lag) in enumerate(slots):
        dest = dest_base + slot_i
        fut_view = joins[(by_obj[id(fut)], lag)]
        etf_view = joins[(by_obj[id(etf)], lag)]
        prior = None
        if prior_day is not None:
            prior = (carry.get("ratio") or {}).get(
                (futures_symbol, etf_symbol, fut.variant, etf.variant, lag), {}
            ).get(prior_day)
        ratio_ok = fut_view["priced"] & etf_view["priced"]
        ratio = np.full(n_cuts, np.nan, dtype=np.float64)
        inverse = np.full(n_cuts, np.nan, dtype=np.float64)
        if np.any(ratio_ok):
            ratio[ratio_ok] = fut_view["close"][ratio_ok] / etf_view["close"][ratio_ok]
            inverse[ratio_ok] = etf_view["close"][ratio_ok] / fut_view["close"][ratio_ok]
        status = _object_fill(n_cuts, "undefined")
        reason = _object_fill(n_cuts, "current_missing_or_stale")
        pred = np.full(n_cuts, np.nan, dtype=np.float64)
        resid = np.full(n_cuts, np.nan, dtype=np.float64)
        prior_ratio = np.full(n_cuts, np.nan, dtype=np.float64)
        prior_cut = np.zeros(n_cuts, dtype=np.int64)
        prior_cut_null = np.ones(n_cuts, dtype=np.bool_)
        if prior is not None and prior.get("cut_ns") is not None:
            prior_cut[:] = int(prior["cut_ns"])
            prior_cut_null[:] = False
        if np.any(ratio_ok):
            if prior_day is None:
                reason[ratio_ok] = "no_prior_intended_date"
            elif prior is None:
                reason[ratio_ok] = "previous_day_missing"
            else:
                late = np.zeros(n_cuts, dtype=np.bool_)
                if prior.get("cut_ns") is not None:
                    late = cuts <= np.int64(int(prior["cut_ns"]))
                same = np.zeros(n_cuts, dtype=np.bool_)
                if prior.get("source_version") is not None:
                    same = (
                        (fut_view["contract_key"] == prior.get("receiver_contract_key"))
                        & (etf_view["contract_key"] == prior.get("source_contract_key"))
                    )
                usable = ratio_ok & ~late & same
                reason[ratio_ok] = "new_contract"
                reason[ratio_ok & late] = "prior_ratio_not_before_cut"
                mapped = lagged_mapping_residual(
                    prior_receiver_close=prior.get("receiver_close"),
                    prior_source_close=prior.get("source_close"),
                    current_source=1.0,
                    current_receiver=1.0,
                )
                pr = mapped["ratio"]
                if pr is not None and np.any(usable):
                    prior_ratio[usable] = pr
                    pred[usable] = pr * etf_view["close"][usable]
                    resid[usable] = fut_view["close"][usable] - pred[usable]
                    status[usable] = mapped.get("status") or "defined"
                    reason[usable] = mapped.get("reason")
        out["session"][dest] = session_arr
        out["futures_symbol"][dest] = futures_symbol
        out["etf_symbol"][dest] = etf_symbol
        out["futures_variant"][dest] = fut.variant
        out["etf_variant"][dest] = etf.variant
        out["cut_ns"][dest] = cuts
        out["lag_s"][dest] = lag
        out["contemporaneous_ratio"][dest] = ratio
        out["contemporaneous_inverse"][dest] = inverse
        out["prior_ratio"][dest] = prior_ratio
        out["predicted_receiver"][dest] = pred
        out["residual_receiver_points"][dest] = resid
        out["status"][dest] = status
        out["reason"][dest] = reason
        out["futures_contract_key"][dest] = fut_view["contract_key"]
        out["etf_contract_key"][dest] = etf_view["contract_key"]
        out["prior_cut_ns"][dest] = prior_cut
        nulls["contemporaneous_ratio"][dest] = ~np.isfinite(ratio)
        nulls["contemporaneous_inverse"][dest] = ~np.isfinite(inverse)
        nulls["prior_ratio"][dest] = ~np.isfinite(prior_ratio)
        nulls["predicted_receiver"][dest] = ~np.isfinite(pred)
        nulls["residual_receiver_points"][dest] = ~np.isfinite(resid)
        nulls["prior_cut_ns"][dest] = prior_cut_null
        for session, sel in splits:
            add_day_values(groups, group_key(
                metric="mapping_residual", source=etf.symbol, receiver=fut.symbol,
                source_variant=etf.variant, receiver_variant=fut.variant,
                year=year, stage=stage, session=session, lookback=None,
                event_kind=None, lag=lag, horizon=None), day, resid[sel])
    writers["mapping"].add_columns(out, length=n, nulls=nulls)


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
        session_arr = _np().asarray(
            [session_label(int(cut), cash, calendar.zone) for cut in cuts.tolist()],
            dtype=object)
        for source, receiver in pairs:
            variant_dates.setdefault(source.variant, set()).add(day)
            variant_dates.setdefault(receiver.variant, set()).add(day)
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
        _emit_cut_grid(
            year=year, units=units, prepared=prepared, by_obj=by_obj, pairs=pairs,
            cuts=cuts, session_arr=session_arr, day=day, stage=stage, writers=writers,
            groups=groups, carry=carry, previous_by_day=previous_by_day, cash=cash,
            calendar=calendar, prior_dates=prior_dates)
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


def _join_event_cuts(prep, cuts, lag):
    np = _np()
    unit = prep.unit
    known = unit.known_for(lag)
    idx, status = backward_join_indices(known, cuts, unit.end_ns)
    n = int(np.asarray(cuts).size)
    present = idx >= 0
    close = np.full(n, np.nan, dtype=np.float64)
    start = np.zeros(n, dtype=np.int64)
    inst = np.full(n, -1, dtype=np.int64)
    valid = np.zeros(n, dtype=np.bool_)
    run_id = np.full(n, -1, dtype=np.int32)
    ckey = np.empty(n, dtype=object)
    ckey[:] = None
    join = np.empty(n, dtype=object)
    names = _join_names()
    ok_status = (status >= 0) & (status < names.size)
    join[:] = "undefined"
    join[ok_status] = names[status[ok_status]]
    if np.any(present):
        take = idx[present]
        close[present] = unit.close[take]
        start[present] = unit.start_ns[take]
        inst[present] = unit.instrument_id[take]
        valid[present] = unit.valid[take]
        run_id[present] = prep.run_id[take]
        ckey[present] = prep.contract_key[take]
        close[present & ~np.isfinite(close)] = np.nan
    priced = (join == "fresh") & valid & (close > 0.0) & np.isfinite(close)
    idx = np.where(priced, idx, -1)
    close[~priced] = np.nan
    ckey[~priced] = None
    return {
        "index": idx, "join": join, "priced": priced, "missing": ~priced,
        "close": close, "start_ns": start, "instrument_id": inst,
        "contract_key": ckey, "run_id": run_id, "valid": valid,
    }


def _collect_source_events(source, prep, lo, hi):
    np = _np()
    indexes = []
    kinds = []
    directions = []
    lookbacks = []
    anchors = []
    form_starts = []
    form_ends = []
    orders = []
    order = 0
    sl = slice(lo, hi)
    valid = source.valid[sl]
    for length in REFERENCE_LOOKBACKS:
        running = prep.running[length]
        for kind, direction, breach in (
            ("running_high", 1, running["high_breach"][sl]),
            ("running_low", -1, running["low_breach"][sl]),
        ):
            at = np.flatnonzero(valid & breach) + lo
            if at.size:
                start = source.start_ns[at]
                indexes.append(at)
                kinds.append(np.full(at.size, kind, dtype=object))
                directions.append(np.full(at.size, direction, dtype=np.int64))
                lookbacks.append(np.full(at.size, length, dtype=np.int64))
                anchors.append(start.copy())
                form_starts.append(start - np.int64(length * MINUTE))
                form_ends.append(start.copy())
                orders.append(np.full(at.size, order, dtype=np.int64))
            order += 1
    pivot = prep.pivot
    for kind, direction, breach, formed in (
        ("pivot_high", 1, pivot["high_breach"][sl], pivot["high_formed_ns"][sl]),
        ("pivot_low", -1, pivot["low_breach"][sl], pivot["low_formed_ns"][sl]),
    ):
        at = np.flatnonzero(valid & breach) + lo
        if at.size:
            formed_at = formed[at - lo]
            indexes.append(at)
            kinds.append(np.full(at.size, kind, dtype=object))
            directions.append(np.full(at.size, direction, dtype=np.int64))
            lookbacks.append(np.full(at.size, 15, dtype=np.int64))
            anchors.append(formed_at.copy())
            form_starts.append(formed_at - np.int64(2 * MINUTE))
            form_ends.append(formed_at + np.int64(3 * MINUTE))
            orders.append(np.full(at.size, order, dtype=np.int64))
        order += 1
    if not indexes:
        return None
    idx = np.concatenate(indexes)
    order_arr = np.concatenate(orders)
    rank = np.lexsort((order_arr, idx))
    return {
        "index": idx[rank],
        "kind": np.concatenate(kinds)[rank],
        "direction": np.concatenate(directions)[rank],
        "lookback": np.concatenate(lookbacks)[rank],
        "anchor_ns": np.concatenate(anchors)[rank],
        "formation_start_ns": np.concatenate(form_starts)[rank],
        "formation_end_ns": np.concatenate(form_ends)[rank],
    }


def _log_ratio_arr(num, den, ok):
    np = _np()
    out = np.full(num.size, np.nan, dtype=np.float64)
    good = ok & np.isfinite(num) & np.isfinite(den) & (num > 0.0) & (den > 0.0)
    if np.any(good):
        out[good] = np.log(num[good] / den[good])
    return out


def _pair_lag_arrays(left, right):
    np = _np()
    n = left["maturity_ns"].size
    pairing = np.empty(n, dtype=object)
    reason = np.empty(n, dtype=object)
    pairing[:] = "common_reference"
    reason[:] = None
    ref_change = np.zeros(n, dtype=np.bool_)
    common = np.ones(n, dtype=np.bool_)
    contrast = np.full(n, np.nan, dtype=np.float64)
    checks = (
        (left["source_contract_key"] != right["source_contract_key"], "different_source_contract"),
        (left["receiver_contract_key"] != right["receiver_contract_key"], "different_receiver_contract"),
        (left["anchor_ns"] != right["anchor_ns"], "different_anchor"),
        (left["source_start_ns"] != right["source_start_ns"], "different_source_bar"),
        (left["maturity_ns"] != right["maturity_ns"], "different_maturity"),
    )
    claimed = np.zeros(n, dtype=np.bool_)
    for mask, label in checks:
        take = mask & ~claimed
        if np.any(take):
            pairing[take] = "unpaired"
            reason[take] = label
            common[take] = False
            claimed[take] = True
    left_ref = left["receiver_ref_start_ns"]
    right_ref = right["receiver_ref_start_ns"]
    left_miss = left["ref_start_null"]
    right_miss = right["ref_start_null"]
    missing = ~claimed & (left_miss | right_miss)
    pairing[missing] = "own_only"
    reason[missing] = "missing_receiver_reference"
    ref_change[missing] = (left_miss != right_miss)[missing]
    common[missing] = False
    claimed |= missing
    changed = ~claimed & (left_ref != right_ref)
    pairing[changed] = "reference_change"
    reason[changed] = "lag_changed_receiver_reference"
    ref_change[changed] = True
    common[changed] = False
    claimed |= changed
    both = ~claimed & np.isfinite(left["terminal_log"]) & np.isfinite(right["terminal_log"])
    contrast[both] = right["terminal_log"][both] - left["terminal_log"][both]
    return {
        "pairing": pairing, "reason": reason, "reference_change": ref_change,
        "common_reference": common, "terminal_contrast": contrast,
    }


def _emit_event_groups(groups, source, receiver, year, stage, day, session, lookback, kind,
                       lag, horizon, terminal, up, down, path, past_f, past_p,
                       zero_reaction, no_receiver, future_status, ref_join, concordance, ci_ok):
    np = _np()
    base = dict(source=source.symbol, receiver=receiver.symbol,
                source_variant=source.variant, receiver_variant=receiver.variant,
                year=year, stage=stage, session=session, lookback=int(lookback),
                event_kind=kind, lag=lag, horizon=horizon)
    path_ok = ci_ok
    add_day_values(groups, group_key(metric="terminal_log", **base), day, terminal, missing=~path_ok)
    add_day_values(groups, group_key(metric="up_log", **base), day, up, missing=~path_ok)
    add_day_values(groups, group_key(metric="down_log", **base), day, down, missing=~path_ok)
    add_day_values(groups, group_key(metric="path_range_log", **base), day, path, missing=~path_ok)
    add_day_values(groups, group_key(metric="past_formation_log", **base), day, past_f, missing=~path_ok)
    add_day_values(groups, group_key(metric="past_preavailability_log", **base), day, past_p, missing=~path_ok)
    term_ok = path_ok & np.isfinite(terminal)
    if np.any(term_ok):
        add_day_flags(groups, group_key(metric="zero_reaction", **base), day, zero_reaction[term_ok])
        add_day_flags(groups, group_key(metric="zero_receiver", **base), day, concordance[term_ok] == "zero_receiver")
    add_day_flags(groups, group_key(metric="no_priced", **base), day, ~np.isfinite(terminal))
    add_day_flags(groups, group_key(metric="no_receiver", **base), day, no_receiver)
    add_day_flags(groups, group_key(metric="missing", **base), day, future_status == "no_receiver")
    add_day_flags(groups, group_key(metric="stale", **base), day, ref_join == "stale")
    add_day_flags(groups, group_key(metric="roll", **base), day, future_status == "roll")
    add_day_flags(groups, group_key(metric="censor", **base), day, future_status == "censored")
    signed = (concordance == "concordant") | (concordance == "discordant")
    if np.any(signed):
        add_day_flags(groups, group_key(metric="concordant_nonzero", **base), day,
                      concordance[signed] == "concordant")
    add_day_flags(groups, group_key(metric="source_events_total", **base), day, np.ones(terminal.size))


def _emit_source_events(units, prepared, by_obj, cash, day, year, stage, writers, groups,
                        calendar, event_seq, label_ids):
    np = _np()
    sess_start, sess_end, _ = futures_session_bounds(cash, calendar.zone)
    receivers = [unit for unit in units.values() if unit.symbol in ("NQ", "ES")]
    zone = calendar.zone
    for source in units.values():
        source_key = by_obj[id(source)]
        prep = prepared[source_key]
        lo, hi = source.slice_session(int(sess_start), int(sess_end))
        clocks = source.ensure_clocks()
        collected = _collect_source_events(source, prep, lo, hi)
        if collected is None:
            continue
        n_ev = int(collected["index"].size)
        event_ids = np.arange(event_seq[0], event_seq[0] + n_ev, dtype=np.int64)
        event_seq[0] += n_ev
        idx = collected["index"]
        uniq, inverse = np.unique(idx, return_inverse=True)
        sessions_u = np.empty(uniq.size, dtype=object)
        for i, bar in enumerate(uniq.tolist()):
            sessions_u[i] = session_label(int(source.start_ns[int(bar)]), cash, zone)
        session = sessions_u[inverse]
        writers["source_events"].add_columns({
            "event_id": event_ids,
            "date": _object_fill(n_ev, day),
            "year": np.full(n_ev, year, dtype=np.int64),
            "stage": _object_fill(n_ev, stage),
            "session": session,
            "source_symbol": _object_fill(n_ev, source.symbol),
            "source_variant": _object_fill(n_ev, source.variant),
            "event_kind": collected["kind"],
            "lookback_minutes": collected["lookback"],
            "direction": collected["direction"],
            "source_start_ns": source.start_ns[idx],
            "source_end_ns": source.end_ns[idx],
            "source_known_at_0": clocks[0][idx],
            "source_known_at_60": clocks[60][idx],
            "source_known_at_120": clocks[120][idx],
            "formation_start_ns": collected["formation_start_ns"],
            "formation_end_ns": collected["formation_end_ns"],
            "anchor_ns": collected["anchor_ns"],
            "source_close": source.close[idx],
            "source_file_id": np.full(n_ev, source.file_id, dtype=np.int64),
            "source_instrument_id": source.instrument_id[idx],
            "source_contract_key": prep.contract_key[idx],
            "actual_received_at_ns": np.zeros(n_ev, dtype=np.int64),
        }, length=n_ev, nulls={"actual_received_at_ns": np.ones(n_ev, dtype=np.bool_)})
        for session_name in SESSIONS:
            sel = session == session_name
            if not np.any(sel):
                continue
            kinds = collected["kind"][sel]
            looks = collected["lookback"][sel]
            for kind in np.unique(kinds):
                for lookback in np.unique(looks[kinds == kind]):
                    take = (kinds == kind) & (looks == lookback)
                    add_day_flags(groups, group_key(
                        metric="source_events_total", source=source.symbol, receiver="",
                        source_variant=source.variant, receiver_variant="",
                        year=year, stage=stage, session=session_name, lookback=int(lookback),
                        event_kind=str(kind), lag=None, horizon=None), day, np.ones(int(take.sum())))
        if not receivers:
            n_empty = n_ev * len(LATENCY_AFTER_END_S) * len(FUTURE_HORIZONS)
            writers["event_links"].add_columns({
                "event_id": np.repeat(event_ids, len(LATENCY_AFTER_END_S) * len(FUTURE_HORIZONS)),
                "label_id": np.zeros(n_empty, dtype=np.int64),
                "receiver_symbol": _object_fill(n_empty, None),
                "receiver_variant": _object_fill(n_empty, None),
                "lag_s": np.tile(np.repeat(np.asarray(LATENCY_AFTER_END_S, dtype=np.int64), len(FUTURE_HORIZONS)), n_ev),
                "horizon_minutes": np.tile(np.asarray(FUTURE_HORIZONS, dtype=np.int64), n_ev * len(LATENCY_AFTER_END_S)),
                "receiver_ref_start_ns": np.zeros(n_empty, dtype=np.int64),
                "receiver_ref_close": np.full(n_empty, np.nan, dtype=np.float64),
                "receiver_ref_join": _object_fill(n_empty, "missing"),
                "receiver_instrument_id": np.zeros(n_empty, dtype=np.int64),
                "receiver_contract_key": _object_fill(n_empty, None),
                "past_formation_log": np.full(n_empty, np.nan, dtype=np.float64),
                "past_preavailability_log": np.full(n_empty, np.nan, dtype=np.float64),
                "terminal_log": np.full(n_empty, np.nan, dtype=np.float64),
                "up_log": np.full(n_empty, np.nan, dtype=np.float64),
                "down_log": np.full(n_empty, np.nan, dtype=np.float64),
                "path_range_log": np.full(n_empty, np.nan, dtype=np.float64),
                "terminal_sign": np.zeros(n_empty, dtype=np.int64),
                "concordance": _object_fill(n_empty, "undefined"),
                "future_status": _object_fill(n_empty, "no_receiver"),
                "zero_reaction": np.zeros(n_empty, dtype=np.bool_),
                "no_receiver": np.ones(n_empty, dtype=np.bool_),
                "ci_eligible": np.zeros(n_empty, dtype=np.bool_),
                "local_node_presence": _object_fill(n_empty, None),
                "maturity_ns": np.zeros(n_empty, dtype=np.int64),
                "actual_received_at_ns": np.zeros(n_empty, dtype=np.int64),
            }, length=n_empty, nulls={
                "label_id": np.ones(n_empty, dtype=np.bool_),
                "receiver_ref_start_ns": np.ones(n_empty, dtype=np.bool_),
                "receiver_instrument_id": np.ones(n_empty, dtype=np.bool_),
                "terminal_sign": np.ones(n_empty, dtype=np.bool_),
                "maturity_ns": np.ones(n_empty, dtype=np.bool_),
                "actual_received_at_ns": np.ones(n_empty, dtype=np.bool_),
            })
            for session_name in SESSIONS:
                sel = session == session_name
                if not np.any(sel):
                    continue
                for kind in np.unique(collected["kind"][sel]):
                    for lookback in np.unique(collected["lookback"][sel][collected["kind"][sel] == kind]):
                        for lag in LATENCY_AFTER_END_S:
                            for horizon in FUTURE_HORIZONS:
                                add_day_flags(groups, group_key(
                                    metric="no_receiver", source=source.symbol, receiver="",
                                    source_variant=source.variant, receiver_variant="",
                                    year=year, stage=stage, session=session_name,
                                    lookback=int(lookback), event_kind=str(kind), lag=lag,
                                    horizon=horizon), day, np.ones(int(((collected["kind"][sel] == kind) & (collected["lookback"][sel] == lookback)).sum())))
            continue
        src_contract = prep.contract_key[idx]
        src_start = source.start_ns[idx]
        pending_label_keys = set()
        eligible_receivers = [r for r in receivers if (source.symbol, r.symbol) in DIRECTED_PAIRS
                              and not (source.symbol == r.symbol and source.variant == r.variant)]
        label_starts_by_lag = {lag: ceil_to_minute_array(clocks[lag][idx]) for lag in LATENCY_AFTER_END_S}
        for event_i in range(n_ev):
            for target in eligible_receivers:
                for lag in LATENCY_AFTER_END_S:
                    label_start = int(label_starts_by_lag[lag][event_i])
                    for horizon in FUTURE_HORIZONS:
                        key = (target.symbol, target.variant, lag, horizon, label_start)
                        if key not in label_ids:
                            label_ids[key] = label_ids['_next']
                            label_ids['_next'] += 1
                            pending_label_keys.add(key)
        for receiver in receivers:
            if (source.symbol, receiver.symbol) not in DIRECTED_PAIRS:
                continue
            if source.symbol == receiver.symbol and source.variant == receiver.variant:
                continue
            rcv_key = by_obj[id(receiver)]
            rcv_prep = prepared[rcv_key]
            lag_payloads = {}
            new_labels = []
            link_blocks = []
            for lag in LATENCY_AFTER_END_S:
                event_known = clocks[lag][idx]
                label_start = ceil_to_minute_array(event_known)
                ref = _join_event_cuts(rcv_prep, event_known, lag)
                form = _join_event_cuts(rcv_prep, collected["formation_start_ns"], lag)
                mid = _join_event_cuts(rcv_prep, collected["formation_end_ns"], lag)
                no_ref = (~ref["priced"]) | ((~ref["missing"]) & (ref["start_ns"] >= event_known))
                past_formation = _log_ratio_arr(
                    mid["close"], form["close"],
                    form["priced"] & mid["priced"] & (form["index"] != mid["index"])
                    & (form["run_id"] == mid["run_id"])
                    & (form["contract_key"] == mid["contract_key"]))
                past_pre = _log_ratio_arr(
                    ref["close"], mid["close"],
                    (~no_ref) & mid["priced"] & (~ref["missing"])
                    & (mid["run_id"] == ref["run_id"])
                    & (mid["contract_key"] == ref["contract_key"])
                    & (ref["start_ns"] < event_known))
                lag_payloads[lag] = {
                    "event_known": event_known, "label_start": label_start, "ref": ref,
                    "no_ref": no_ref, "past_formation": past_formation, "past_pre": past_pre,
                }
                for horizon in FUTURE_HORIZONS:
                    maturity = label_start + np.int64(horizon * MINUTE)
                    ci_ok = stages_aligned_many(
                        collected["formation_start_ns"], label_start, maturity, cash.day, zone)
                    raw = lookup_future_windows(receiver, rcv_prep.futures, label_start, horizon)
                    raw_status = raw["status"]
                    window_status = np.array(raw_status, copy=True)
                    window_high = np.array(raw["high"], copy=True)
                    window_low = np.array(raw["low"], copy=True)
                    window_close = np.array(raw["close"], copy=True)
                    roll = (~no_ref) & (raw["contract_key"] != ref["contract_key"])
                    window_status[no_ref] = "no_receiver"
                    window_high[no_ref | roll] = np.nan
                    window_low[no_ref | roll] = np.nan
                    window_close[no_ref | roll] = np.nan
                    window_status[roll] = "roll"
                    future_status = np.array(window_status, copy=True)
                    future_status[no_ref] = "no_receiver"
                    terminal = _log_ratio_arr(window_close, ref["close"], (~no_ref) & ci_ok)
                    up = np.full(n_ev, np.nan, dtype=np.float64)
                    down = np.full(n_ev, np.nan, dtype=np.float64)
                    path = _log_ratio_arr(window_high, window_low, ci_ok)
                    ref_ok = (~no_ref) & ci_ok & np.isfinite(ref["close"]) & (ref["close"] > 0.0)
                    high_ok = ref_ok & np.isfinite(window_high) & (window_high > 0.0)
                    low_ok = ref_ok & np.isfinite(window_low) & (window_low > 0.0)
                    if np.any(high_ok):
                        up[high_ok] = np.maximum(0.0, np.log(window_high[high_ok] / ref["close"][high_ok]))
                    if np.any(low_ok):
                        down[low_ok] = np.maximum(0.0, np.log(ref["close"][low_ok] / window_low[low_ok]))
                    # excursion_up/down clamp already via max(0, log). Missing window → nan, not 0.
                    up[~ci_ok] = np.nan
                    down[~ci_ok] = np.nan
                    path[~ci_ok] = np.nan
                    sign = np.zeros(n_ev, dtype=np.int64)
                    sign_null = ~np.isfinite(terminal)
                    sign[np.isfinite(terminal) & (terminal > 0.0)] = 1
                    sign[np.isfinite(terminal) & (terminal < 0.0)] = -1
                    concordance = np.empty(n_ev, dtype=object)
                    concordance[:] = "undefined"
                    direction = collected["direction"]
                    zero = np.isfinite(terminal) & (terminal == 0.0)
                    pos = np.isfinite(terminal) & (terminal > 0.0)
                    neg = np.isfinite(terminal) & (terminal < 0.0)
                    concordance[zero] = "zero_receiver"
                    concordance[pos & (direction == 1)] = "concordant"
                    concordance[neg & (direction == -1)] = "concordant"
                    concordance[pos & (direction == -1)] = "discordant"
                    concordance[neg & (direction == 1)] = "discordant"
                    concordance[direction == 0] = "undefined"
                    zero_reaction = np.isfinite(window_close) & (~no_ref) & np.isfinite(ref["close"]) & (terminal == 0.0)
                    # bundle zero_reaction uses terminal before ci mask; recompute without ci
                    raw_terminal = _log_ratio_arr(window_close, ref["close"], ~no_ref)
                    zero_reaction = np.isfinite(raw_terminal) & (raw_terminal == 0.0)
                    link_blocks.append({
                        "lag": lag, "horizon": horizon,
                        "event_id": event_ids,
                        "label_id": np.zeros(n_ev, dtype=np.int64),
                        "label_start": label_start,
                        "raw": raw,
                        "raw_status": raw_status,
                        "receiver_ref_start_ns": ref["start_ns"],
                        "ref_start_null": ref["missing"],
                        "inst_null": ref["missing"],
                        "receiver_ref_close": np.where(no_ref, np.nan, ref["close"]),
                        "receiver_ref_join": ref["join"],
                        "receiver_instrument_id": ref["instrument_id"],
                        "receiver_contract_key": ref["contract_key"],
                        "past_formation_log": past_formation,
                        "past_preavailability_log": past_pre,
                        "terminal_log": terminal,
                        "up_log": up,
                        "down_log": down,
                        "path_range_log": path,
                        "terminal_sign": sign,
                        "sign_null": sign_null,
                        "concordance": concordance,
                        "future_status": future_status,
                        "zero_reaction": zero_reaction,
                        "no_receiver": future_status == "no_receiver",
                        "ci_eligible": ci_ok & (future_status == "complete"),
                        "maturity_ns": maturity,
                        "source_contract_key": src_contract,
                        "anchor_ns": collected["anchor_ns"],
                        "source_start_ns": src_start,
                        "ci_ok": ci_ok,
                    })
                    for session_name in SESSIONS:
                        sel = session == session_name
                        if not np.any(sel):
                            continue
                        for kind in np.unique(collected["kind"][sel]):
                            for lookback in np.unique(collected["lookback"][sel][collected["kind"][sel] == kind]):
                                take = sel & (collected["kind"] == kind) & (collected["lookback"] == lookback)
                                if not np.any(take):
                                    continue
                                _emit_event_groups(
                                    groups, source, receiver, year, stage, day, session_name,
                                    lookback, str(kind), lag, horizon,
                                    terminal[take], up[take], down[take], path[take],
                                    past_formation[take], past_pre[take],
                                    zero_reaction[take], future_status[take] == "no_receiver",
                                    future_status[take], ref["join"][take], concordance[take],
                                    ci_ok[take])
            by = {(block["lag"], block["horizon"]): block for block in link_blocks}
            for event_i in range(n_ev):
                for lag in LATENCY_AFTER_END_S:
                    for horizon in FUTURE_HORIZONS:
                        block = by[(lag, horizon)]
                        key = (receiver.symbol, receiver.variant, lag, horizon, int(block["label_start"][event_i]))
                        label_id = label_ids[key]
                        if key in pending_label_keys:
                            pending_label_keys.remove(key)
                            raw = block["raw"]
                            new_labels.append({
                                "label_id": label_id,
                                "receiver_symbol": receiver.symbol,
                                "receiver_variant": receiver.variant,
                                "lag_s": lag,
                                "horizon_minutes": horizon,
                                "label_start_ns": int(block["label_start"][event_i]),
                                "maturity_ns": int(block["maturity_ns"][event_i]),
                                "future_status": str(block["raw_status"][event_i]),
                                "future_reasons": "|".join(raw["reasons"][event_i] or ()),
                                "open": None if not math.isfinite(float(raw["open"][event_i])) else float(raw["open"][event_i]),
                                "high": None if not math.isfinite(float(raw["high"][event_i])) else float(raw["high"][event_i]),
                                "low": None if not math.isfinite(float(raw["low"][event_i])) else float(raw["low"][event_i]),
                                "close": None if not math.isfinite(float(raw["close"][event_i])) else float(raw["close"][event_i]),
                                "instrument_id": None if int(raw["index"][event_i]) < 0 else int(raw["instrument_id"][event_i]),
                                "contract_key": raw["contract_key"][event_i],
                                "file_id": receiver.file_id,
                                "actual_received_at_ns": None,
                            })
                        block["label_id"][event_i] = label_id
            if new_labels:
                writers["receiver_labels"].extend(new_labels)
            n_links = n_ev * len(LATENCY_AFTER_END_S) * len(FUTURE_HORIZONS)
            ordered = [by[(lag, horizon)] for lag in LATENCY_AFTER_END_S for horizon in FUTURE_HORIZONS]
            def _stack(name):
                return np.stack([block[name] for block in ordered], axis=1).reshape(n_ev, -1).ravel()
            writers["event_links"].add_columns({
                "event_id": _stack("event_id"),
                "label_id": _stack("label_id"),
                "receiver_symbol": _object_fill(n_links, receiver.symbol),
                "receiver_variant": _object_fill(n_links, receiver.variant),
                "lag_s": np.tile(np.repeat(np.asarray(LATENCY_AFTER_END_S, dtype=np.int64), len(FUTURE_HORIZONS)), n_ev),
                "horizon_minutes": np.tile(np.asarray(FUTURE_HORIZONS, dtype=np.int64), n_ev * len(LATENCY_AFTER_END_S)),
                "receiver_ref_start_ns": _stack("receiver_ref_start_ns"),
                "receiver_ref_close": _stack("receiver_ref_close"),
                "receiver_ref_join": _stack("receiver_ref_join"),
                "receiver_instrument_id": _stack("receiver_instrument_id"),
                "receiver_contract_key": _stack("receiver_contract_key"),
                "past_formation_log": _stack("past_formation_log"),
                "past_preavailability_log": _stack("past_preavailability_log"),
                "terminal_log": _stack("terminal_log"),
                "up_log": _stack("up_log"),
                "down_log": _stack("down_log"),
                "path_range_log": _stack("path_range_log"),
                "terminal_sign": _stack("terminal_sign"),
                "concordance": _stack("concordance"),
                "future_status": _stack("future_status"),
                "zero_reaction": _stack("zero_reaction"),
                "no_receiver": _stack("no_receiver"),
                "ci_eligible": _stack("ci_eligible"),
                "local_node_presence": _object_fill(n_links, None),
                "maturity_ns": _stack("maturity_ns"),
                "actual_received_at_ns": np.zeros(n_links, dtype=np.int64),
            }, length=n_links, nulls={
                "receiver_ref_start_ns": _stack("ref_start_null"),
                "receiver_instrument_id": _stack("inst_null"),
                "terminal_sign": _stack("sign_null"),
                "actual_received_at_ns": np.ones(n_links, dtype=np.bool_),
            })

            for horizon in FUTURE_HORIZONS:
                left60 = by[(60, horizon)]
                for right_lag in (0, 120):
                    right = by[(right_lag, horizon)]
                    paired = _pair_lag_arrays(
                        {**left60, "source_contract_key": src_contract, "anchor_ns": collected["anchor_ns"],
                         "source_start_ns": src_start},
                        {**right, "source_contract_key": src_contract, "anchor_ns": collected["anchor_ns"],
                         "source_start_ns": src_start},
                    )
                    writers["contrasts"].add_columns({
                        "event_id": event_ids,
                        "date": _object_fill(n_ev, day),
                        "source_symbol": _object_fill(n_ev, source.symbol),
                        "receiver_symbol": _object_fill(n_ev, receiver.symbol),
                        "source_variant": _object_fill(n_ev, source.variant),
                        "receiver_variant": _object_fill(n_ev, receiver.variant),
                        "source_contract_key": src_contract,
                        "receiver_contract_key": left60["receiver_contract_key"],
                        "horizon_minutes": np.full(n_ev, horizon, dtype=np.int64),
                        "maturity_ns": left60["maturity_ns"],
                        "lag_a_s": np.full(n_ev, 60, dtype=np.int64),
                        "lag_b_s": np.full(n_ev, right_lag, dtype=np.int64),
                        "pairing": paired["pairing"],
                        "reason": paired["reason"],
                        "reference_change": paired["reference_change"],
                        "common_reference": paired["common_reference"],
                        "terminal_a": left60["terminal_log"],
                        "terminal_b": right["terminal_log"],
                        "terminal_contrast": paired["terminal_contrast"],
                        "kind": _object_fill(n_ev, "timing_lag"),
                        "lookback_minutes": collected["lookback"],
                    }, length=n_ev, nulls={
                        "terminal_a": ~np.isfinite(left60["terminal_log"]),
                        "terminal_b": ~np.isfinite(right["terminal_log"]),
                        "terminal_contrast": ~np.isfinite(paired["terminal_contrast"]),
                    })
                    for session_name in SESSIONS:
                        sel = session == session_name
                        if not np.any(sel):
                            continue
                        for kind in np.unique(collected["kind"][sel]):
                            for lookback in np.unique(collected["lookback"][sel][collected["kind"][sel] == kind]):
                                take = sel & (collected["kind"] == kind) & (collected["lookback"] == lookback)
                                if np.any(take):
                                    add_day_values(groups, group_key(
                                        metric="lag_contrast", source=source.symbol,
                                        receiver=receiver.symbol, source_variant=source.variant,
                                        receiver_variant=receiver.variant, year=year, stage=stage,
                                        session=session_name, lookback=int(lookback),
                                        event_kind=str(kind), lag=60, horizon=horizon),
                                                  day, paired["terminal_contrast"][take])

    return


def _emit_source_events_reference(units, prepared, by_obj, cash, day, year, stage, writers, groups,
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


def _repeat_i64(np, value, n: int):
    arr = np.zeros(n, dtype=np.int64)
    null = np.zeros(n, dtype=np.bool_)
    if value is None:
        null[:] = True
    else:
        arr[:] = int(value)
    return arr, null


def _write_date_aggregates(writer, groups):
    np = _np()
    emit = getattr(writer, "add_arrays", None) or writer.add_columns
    for key, payload in groups.items():
        (metric, source, receiver, source_variant, receiver_variant,
         year, stage, session, lookback, kind, lag, horizon) = key
        days = sorted(set(payload["sum"]) | set(payload["count"]))
        n = len(days)
        if n == 0:
            continue
        counts = np.zeros(n, dtype=np.int64)
        totals = np.zeros(n, dtype=np.float64)
        means = np.zeros(n, dtype=np.float64)
        mean_null = np.zeros(n, dtype=np.bool_)
        for i, day in enumerate(days):
            count = int(payload["count"].get(day, 0))
            total = float(payload["sum"].get(day, 0.0))
            counts[i] = count
            totals[i] = total
            if count == 0:
                mean_null[i] = True
            else:
                means[i] = total / count
        years, year_null = _repeat_i64(np, year, n)
        horizons, horizon_null = _repeat_i64(np, horizon, n)
        lags, lag_null = _repeat_i64(np, lag, n)
        lookbacks, lookback_null = _repeat_i64(np, lookback, n)
        emit({
            "date": days,
            "year": years,
            "stage": [stage] * n,
            "session": [session] * n,
            "source_symbol": [source] * n,
            "receiver_symbol": [receiver] * n,
            "source_variant": [source_variant] * n,
            "receiver_variant": [receiver_variant] * n,
            "metric": [metric] * n,
            "sum": totals,
            "event_count": counts,
            "date_mean": means,
            "horizon_minutes": horizons,
            "lag_s": lags,
            "lookback_minutes": lookbacks,
            "event_kind": [None if kind is None else str(kind)] * n,
        }, length=n, nulls={
            "year": year_null,
            "date_mean": mean_null,
            "horizon_minutes": horizon_null,
            "lag_s": lag_null,
            "lookback_minutes": lookback_null,
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


def _calendar_dates_by_year_stage(unique_dates):
    out = {}
    for day in unique_dates:
        parsed = date.fromisoformat(day)
        key = (parsed.year, stage_of(parsed) or "outside_primary")
        out.setdefault(key, []).append(day)
    return out


def _add_daily_groups_for_year(groups, cash_rows, year: int):
    year = int(year)
    for row in cash_rows:
        if not row.get("in_primary_cohort"):
            continue
        try:
            row_year = int(row["date"][:4])
        except (TypeError, ValueError, KeyError):
            continue
        if row_year != year:
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


def _phase_mark():
    return time_mod.process_time(), time_mod.perf_counter()


def _phase_elapsed(started):
    return {
        "cpu_seconds": time_mod.process_time() - started[0],
        "wall_seconds": time_mod.perf_counter() - started[1],
    }


def _add_phase(store, name, delta):
    slot = store.setdefault(name, {"cpu_seconds": 0.0, "wall_seconds": 0.0})
    slot["cpu_seconds"] += float(delta["cpu_seconds"])
    slot["wall_seconds"] += float(delta["wall_seconds"])


def _statistics_json_header():
    return b"".join((
        b'{"kind":"cross_market_date_statistics_v1"',
        b',"seed":', canonical_json(STAT_SEED),
        b',"block_length":', canonical_json(STAT_BLOCK),
        b',"replicates":', canonical_json(STAT_REPLICATES),
        b',"confidence":', canonical_json(STAT_CONFIDENCE),
        b',"groups":{',
    ))


def _statistics_json_append(stream, statistics, first: bool) -> bool:
    for key, payload in statistics.items():
        if not first:
            stream.write(b",")
        first = False
        stream.write(canonical_json(str(key)))
        stream.write(b":")
        stream.write(canonical_json(_jsonable(payload)))
    return first


def _statistics_json_footer(date_support):
    return b',"independent_date_support":' + canonical_json(_jsonable(date_support)) + b"}\n"


def _tally_statistic_classes(statistics, tallies):
    for key, payload in statistics.items():
        name = _metric_class(key)
        slot = tallies.setdefault(name, {"defined": 0, "undefined": 0, "total": 0})
        slot["total"] += 1
        if payload.get("status") == "undefined":
            slot["undefined"] += 1
        else:
            slot["defined"] += 1
    return tallies


def _results_md_group_lines(statistics) -> list[str]:
    class_order = (
        "feature/activity", "SMT", "mapping", "event paths", "delay/source comparisons", "other",
    )
    by_class = {name: [] for name in class_order}
    for key, payload in statistics.items():
        by_class.setdefault(_metric_class(key), []).append((key, payload))
    lines = []
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
    return lines


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
    lines.extend(_results_md_group_lines(statistics))
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


def _results_md_stream_header(years) -> bytes:
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
        f"- Years processed: {list(years)}",
        f"- Directed pairs: {len(DIRECTED_PAIRS)}",
        f"- Latency scenarios after bar end (seconds): {list(LATENCY_AFTER_END_S)}",
        "",
        "## Prespecified findings by metric class",
        "",
        "Each class reports date-mean estimate, bootstrap interval, and restored event/date support.",
        "Coverage-only groups are not a substitute for SMT, mapping, path, or delay classes.",
        "",
    ]
    return ("\n".join(lines) + "\n").encode()


def _results_md_stream_footer(counts, resources, refs, quality, support, class_tallies) -> bytes:
    lines = []
    if quality:
        lines.extend(["## Source quality and identity", ""])
        for row in quality:
            lines.append(
                f"- `{row['symbol']}` {row['variant']} {row['year']} file_id={row['file_id']}: "
                f"{row['valid_rows']}/{row['rows']} valid; unit={row['volume_unit']}")
        lines.append("")
    lines.extend([
        "## Distinct counts",
        "",
        f"- Intended cash dates: {counts.get('intended_dates')}",
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
    ])
    if class_tallies:
        lines.extend(["## Class totals", ""])
        for name, slot in class_tallies.items():
            lines.append(
                f"- {name}: defined={slot['defined']} undefined={slot['undefined']} "
                f"total={slot['total']}")
        lines.append("")
    if support:
        lines.extend([
            "## Independent date support",
            "",
            f"- Primary dates: {support.get('primary_dates')}",
            f"- original_nq2024 dates: {support.get('original_nq2024_dates')}",
            f"- Doubled if pooled: {support.get('independent_support_if_doubled')}",
            f"- Doubled flag: {support.get('doubled')}",
            "",
        ])
    lines.extend([
        "## Resources",
        "",
        f"- CPU seconds: {resources.get('cpu_seconds')}",
        f"- Wall seconds: {resources.get('wall_seconds')}",
        f"- Output bytes: {resources.get('output_bytes')}",
        "",
        f"Readable refs: {sorted(refs)}",
        "",
    ])
    return ("\n".join(lines) + "\n").encode()


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
    phase_totals = {}
    valid_bars = invalid_bars = raw_source_rows = 0
    event_seq = [1]
    label_ids = {}
    class_tallies = {}
    if fixture_daily is None and fixture_units is None:
        cash_rows, action_rows = load_daily_observational(
            admitted, maximum_bytes=maximum_bytes, calendar=calendar)
    else:
        cash_rows, action_rows = fixture_daily or ([], [])
    _write_daily(writers["daily"], cash_rows, action_rows)
    stats_stream = outputs.create("statistics.json")
    md_stream = outputs.create("results.md")
    first_stat = True
    try:
        stats_stream.write(_statistics_json_header())
        md_stream.write(_results_md_stream_header(years))
        for year in years:
            year_cpu = time_mod.process_time()
            year_wall = time_mod.perf_counter()
            written0 = outputs.written
            t_read = _phase_mark()
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
            source_read = _phase_elapsed(t_read)
            _add_phase(phase_totals, "source_read", source_read)
            t_meas = _phase_mark()
            _add_daily_groups_for_year(groups, cash_rows, year)
            if units:
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
            elif fixture_dates is None:
                for cash in year_cash_days(calendar, year, None):
                    intended_all.append(cash.day.isoformat())
            measurement = _phase_elapsed(t_meas)
            _add_phase(phase_totals, "measurement", measurement)
            n_units = len(units)
            n_groups = len(groups)
            n_date_rows = 0
            for payload in groups.values():
                n_date_rows += len(set(payload["sum"]) | set(payload["count"]))
            t_out = _phase_mark()
            _write_date_aggregates(writers["date_agg"], groups)
            date_output = _phase_elapsed(t_out)
            _add_phase(phase_totals, "date_output", date_output)
            t_stats = _phase_mark()
            unique_year_dates = sorted(set(intended_all))
            intended_map = _group_intended(
                groups, unique_year_dates, _calendar_dates_by_year_stage(unique_year_dates))
            year_stats = summarize_groups(groups, intended_map)
            first_stat = _statistics_json_append(stats_stream, year_stats, first_stat)
            _tally_statistic_classes(year_stats, class_tallies)
            md_stream.write(f"## Year {year}\n\n".encode())
            md_stream.write(("\n".join(_results_md_group_lines(year_stats)) + "\n").encode())
            n_stat_groups = len(year_stats)
            year_stats.clear()
            intended_map.clear()
            groups.clear()
            units.clear()
            stats = _phase_elapsed(t_stats)
            _add_phase(phase_totals, "stats", stats)
            partition_measurements.append({
                "year": year,
                "cpu_seconds": time_mod.process_time() - year_cpu,
                "wall_seconds": time_mod.perf_counter() - year_wall,
                "output_bytes": outputs.written - written0,
                "units": n_units,
                "max_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "source_read": source_read,
                "measurement": measurement,
                "date_output": date_output,
                "stats": stats,
                "groups": n_groups,
                "date_aggregate_rows": n_date_rows,
                "statistic_groups": n_stat_groups,
            })
        unique_dates = sorted(set(intended_all))
        date_support = independent_date_support(variant_dates)
        stats_stream.write(_statistics_json_footer(date_support))
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
        t_report = _phase_mark()
        for name, writer in writers.items():
            refs[name] = writer.finish()
            counts[{
                "cuts": "aligned_cuts", "date_agg": "date_aggregates",
                "source_events": "source_events", "event_links": "event_links",
                "receiver_labels": "receiver_labels",
            }.get(name, name)] = writer.rows
        resources = {
            "cpu_seconds": time_mod.process_time() - started_cpu,
            "wall_seconds": time_mod.perf_counter() - started_wall,
            "output_bytes": outputs.written,
            "per_year": partition_measurements,
            "phases": phase_totals,
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
        md_stream.write(_results_md_stream_footer(
            counts, resources, refs, quality, date_support, class_tallies))
    finally:
        stats_stream.close()
        md_stream.close()
    refs["results_md"] = outputs.reference("results.md", kind="cross_market_results_markdown_v1")
    refs["statistics"] = outputs.reference("statistics.json", kind="cross_market_statistics_v1")
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
    report = _phase_elapsed(t_report)
    _add_phase(phase_totals, "report", report)
    resources["cpu_seconds"] = time_mod.process_time() - started_cpu
    resources["wall_seconds"] = time_mod.perf_counter() - started_wall
    resources["output_bytes"] = outputs.written
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
    "add_day_flags", "add_day_values", "concordance", "date_cells_for_ci",
    "excursion_bundle", "future_window", "group_key", "independent_date_support",
    "pair_timing_rows", "reconstruct_joint_event_rows", "restore_event_counts",
    "run", "source_event_schema", "stages_aligned_for_ci", "summarize_groups",
)


def process_year_reference(*, year: int, units: dict, calendar, writers: dict, groups: dict,
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
        _emit_source_events_reference(
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

