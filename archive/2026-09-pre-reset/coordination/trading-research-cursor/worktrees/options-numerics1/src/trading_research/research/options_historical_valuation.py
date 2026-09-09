"""Historical option valuation consumer: join, invert, ATM/term/coverage, report.

Research-Options-Historical-Valuation-v1. Named scenario conventions only;
this module does not certify F02 product/series identity (DRF-A06). Consumes
accepted quote cut boards plus underlier/FRED/action support and the accepted
Black/American API. No new solver, surface, Context, flow, node, or PnL.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import date, time
from hashlib import sha256
from json import dumps
from math import exp as math_exp
from math import isfinite, log

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.calendar import local_timestamp
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.options_valuation_numerics import (
    FLAG_ASK_ONLY, FLAG_UNSTABLE_GREEK, FLAG_WEAK_VEGA, MODEL_VERSION,
    STATUS_CONVERGED, STATUS_CROSSED_QUOTES, STATUS_ENDPOINT_LOWER,
    STATUS_ENDPOINT_UPPER, STATUS_FAILED_BRACKET, STATUS_INVALID_INPUT,
    STATUS_NATIVE_UNAVAILABLE, STATUS_UNBOUNDED_SIDE, STATUS_UNDEFINED_POINT,
    STATUS_ZERO_T, apply_contract_multiplier, american_greeks, black_greeks,
    has_flag, invert_american_quote_interval, invert_quote_interval,
    primary_status, years_from_nanoseconds,
)

STUDY_ID = "Research-Options-Historical-Valuation-v1"
VERSION = "options_historical_valuation_v1"
SCENARIO_VERSION = "options_historical_valuation_scenario_v1"
MODEL_ASOF = "cut"
ZONE = "America/New_York"
MAX_BOARD_ROWS = 250_000
AMERICAN_NUMERICAL_N_SPACE = 128
MULTIPLIER_SCENARIO = 100.0
STATISTICS_SEED = 20260908
STATISTICS_BLOCK = 5
STATISTICS_REPLICATES = 1000
STATISTICS_MIN_DATES = 100
STATISTICS_MIN_EVENTS = 20
OUTPUT_SCHEMAS = {
    "contract_cut": "options_historical_valuation_contract_cut_v1",
    "expiry_cut": "options_historical_valuation_expiry_cut_v1",
    "coverage": "options_historical_valuation_coverage_v1",
    "cross_chain": "options_historical_valuation_cross_chain_cut_v1",
}
EXPIRY_CLOCK_WALL = {"osi_date_0930_et": (9, 30), "osi_date_1600_et": (16, 0)}
INDEX_CHAINS = ("SPX", "NDX", "SPXW", "NDXP")
ETF_CHAINS = ("QQQ", "SPY")
ETF_SYMBOL = {"QQQ": "QQQ", "SPY": "SPY"}
CROSS_FAMILIES = (
    ("nasdaq_family", ("NDX", "NDXP", "QQQ")),
    ("spx_family", ("SPX", "SPXW", "SPY")),
)
STAGES = {
    "training": ("2020-01-01", "2023-01-01"),
    "development": ("2023-01-01", "2025-01-01"),
    "confirmation": ("2025-01-01", "2026-09-04"),
}
K_BINS = ("le_0.02", "0.02_to_0.10", "gt_0.10")
BASE_CLASSES = (
    "invalid_identity", "invalid_clock", "invalid_numeric", "conflict",
    "all_zero", "one_sided", "crossed", "locked", "two_sided",
)
GROUP_KEYS = ("chain", "request_date", "cut_label", "source_family")
IDENTIFIED_STATUSES = (STATUS_CONVERGED, STATUS_ENDPOINT_LOWER, STATUS_ENDPOINT_UPPER)
RATE_ASSUMPTIONS = (
    "fred_closest_tenor_percent_to_decimal", "zero_rate_named",
    "fred_linear_tenor_percent_to_decimal",
)
DIVIDEND_ASSUMPTIONS = ("exdate_schedule_not_announcement_pit", "q0_no_dividend")
REQUIRED_BOARD = (
    "chain", "request_date", "cut_label", "cut_ns", "source_family", "contract_id",
    "osi_symbol", "expiration", "millistrike", "right", "bid", "ask",
    "usable", "quoted", "conflict",
)
NAMED_SCENARIO_PRESETS = (
    "base", "zero_rate", "linear_tenor", "q0_no_dividend",
    "am_index_pm_clock", "multiplier_post_solver",
)
_SCENARIO_KEYS = frozenset({
    "version", "study", "certification_claimed", "time_basis", "zone",
    "expiry_clock_by_chain", "expiry_clock_overrides", "style_by_chain",
    "coordinate_by_chain", "settlement_class_by_chain", "rate_assumption",
    "dividend_assumption", "european_dividend_assumption",
    "european_forward_assumption", "parity_forward_assumption",
    "multiplier_assumption", "apply_multiplier", "american_n_space",
    "vix_spot_policy", "vix_external_join", "index_preclose_cash_policy",
    "index_cash_close_policy", "etf_underlier_policy", "max_board_rows",
    "group_keys", "base_assumption", "changed_assumption",
})
_CLOCKS = (
    ("known_at_ns", pa.int64()), ("received_at_ns", pa.int64()),
    ("published_at_ns", pa.int64()), ("last_actual_update_ns", pa.int64()),
    ("causal_feature_eligible", pa.bool_()),
)
GREEK_NAMES = ("delta", "gamma", "vega", "vanna", "charm", "volga", "theta")


def default_scenario_contract():
    clocks = {
        "SPX": "osi_date_0930_et", "NDX": "osi_date_0930_et",
        "SPXW": "osi_date_1600_et", "NDXP": "osi_date_1600_et",
        "QQQ": "osi_date_1600_et", "SPY": "osi_date_1600_et",
        "VIX": "osi_date_0930_et",
    }
    euro = {c: "european_black" for c in (*INDEX_CHAINS, "VIX")}
    return {
        "version": SCENARIO_VERSION, "study": STUDY_ID,
        "certification_claimed": False, "time_basis": "actual_365_fixed",
        "zone": ZONE, "expiry_clock_by_chain": clocks, "expiry_clock_overrides": {},
        "style_by_chain": {**euro, "QQQ": "american_spot_fd", "SPY": "american_spot_fd"},
        "coordinate_by_chain": {
            **{c: "forward" for c in (*INDEX_CHAINS, "VIX")},
            "QQQ": "spot", "SPY": "spot",
        },
        "settlement_class_by_chain": {
            "SPX": "cash_index_am_class", "NDX": "cash_index_am_class",
            "SPXW": "cash_index_pm_class", "NDXP": "cash_index_pm_class",
            "QQQ": "american_etf", "SPY": "american_etf",
            "VIX": "cash_vix_options_not_vx_futures",
        },
        "rate_assumption": "fred_closest_tenor_percent_to_decimal",
        "dividend_assumption": "exdate_schedule_not_announcement_pit",
        "european_dividend_assumption": "q0_named",
        "european_forward_assumption": "F_spotcarry_S_exp_rT_q0_named",
        "parity_forward_assumption": "F_parity_K_plus_C_minus_P_over_D_x02_bootstrap",
        "multiplier_assumption": "scenario_equity_100", "apply_multiplier": False,
        "american_n_space": AMERICAN_NUMERICAL_N_SPACE,
        "vix_spot_policy": "vix_spot_unavailable_no_vx_replacement",
        "vix_external_join": False,
        "index_preclose_cash_policy": "prior_available_cash_date_close",
        "index_cash_close_policy": "retrospective_same_date_close_at_or_after_declared_close",
        "etf_underlier_policy": "latest_complete_one_minute_bar_end_at_or_before_cut",
        "max_board_rows": MAX_BOARD_ROWS, "group_keys": list(GROUP_KEYS),
        "base_assumption": "default_scenario_contract", "changed_assumption": None,
    }


def validate_scenario_contract(scenario_contract):
    if not isinstance(scenario_contract, dict):
        raise ContractError("scenario_contract must be a dict")
    extra = set(scenario_contract) - _SCENARIO_KEYS
    missing = _SCENARIO_KEYS - set(scenario_contract)
    if extra:
        raise ContractError(f"scenario_contract has unknown keys {sorted(extra)}")
    if missing:
        raise ContractError(f"scenario_contract missing keys {sorted(missing)}")
    c = scenario_contract
    if c["version"] != SCENARIO_VERSION or c["study"] != STUDY_ID:
        raise ContractError("scenario identity is not the frozen consumer")
    if c["certification_claimed"] is not False:
        raise ContractError("this consumer must not claim certification")
    if c["time_basis"] != "actual_365_fixed" or c["zone"] != ZONE:
        raise ContractError("only Actual/365 Fixed America/New_York clocks are implemented")
    if c["american_n_space"] != AMERICAN_NUMERICAL_N_SPACE:
        raise ContractError("american_n_space is the frozen numerical default 128")
    if c["vix_external_join"] is not False:
        raise ContractError("this consumer does not join a VIX external series")
    if int(c["max_board_rows"]) > MAX_BOARD_ROWS:
        raise ContractError("max_board_rows exceeds the documented batch cap")
    if c["rate_assumption"] not in RATE_ASSUMPTIONS:
        raise ContractError("rate_assumption is not a named scenario")
    if c["dividend_assumption"] not in DIVIDEND_ASSUMPTIONS:
        raise ContractError("dividend_assumption is not a named scenario")
    if c["european_dividend_assumption"] != "q0_named":
        raise ContractError("European q=0 is a named assumption")
    if type(c["apply_multiplier"]) is not bool:
        raise ContractError("apply_multiplier must be an explicit boolean")
    clocks, overrides = c["expiry_clock_by_chain"], c["expiry_clock_overrides"]
    if not isinstance(clocks, dict) or not isinstance(overrides, dict):
        raise ContractError("expiry clock maps must be dicts")
    for name, value in {**clocks, **overrides}.items():
        if value not in EXPIRY_CLOCK_WALL:
            raise ContractError(f"unknown expiry clock {value!r} for {name}")
    for chain, style in c["style_by_chain"].items():
        if style not in ("european_black", "american_spot_fd"):
            raise ContractError(f"unknown style {style!r} for {chain}")
    if tuple(c["group_keys"]) != GROUP_KEYS:
        raise ContractError("group_keys must remain chain/request_date/cut/source_family")
    return c


def scenario_identity(scenario_contract):
    validate_scenario_contract(scenario_contract)
    payload = dumps(scenario_contract, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


def named_scenario_contract(name="base"):
    if name not in NAMED_SCENARIO_PRESETS:
        raise ContractError(f"unknown named scenario {name!r}")
    base = default_scenario_contract()
    if name == "base":
        return validate_scenario_contract(base)
    if name == "zero_rate":
        return _with_change(base, rate_assumption="zero_rate_named")
    if name == "linear_tenor":
        return _with_change(base, rate_assumption="fred_linear_tenor_percent_to_decimal")
    if name == "q0_no_dividend":
        return _with_change(base, dividend_assumption="q0_no_dividend")
    if name == "am_index_pm_clock":
        return _with_change(base, expiry_clock_overrides={"SPX": "osi_date_1600_et", "NDX": "osi_date_1600_et"})
    return _with_change(base, apply_multiplier=True)


def _with_change(base, **changes):
    out = deepcopy(base)
    labels = []
    for key, value in changes.items():
        if key not in _SCENARIO_KEYS:
            raise ContractError(f"cannot change unknown scenario key {key}")
        out[key] = value
        labels.append(key if isinstance(value, dict) else f"{key}={value!r}")
    out["base_assumption"] = "default_scenario_contract"
    out["changed_assumption"] = ",".join(labels)
    return validate_scenario_contract(out)


def quote_dte_bucket(days):
    if days is None:
        return None
    if days < 0:
        return "expired"
    if days == 0:
        return "0"
    if days == 1:
        return "1"
    if days <= 7:
        return "2-7"
    if days <= 14:
        return "8-14"
    if days <= 30:
        return "15-30"
    if days <= 60:
        return "31-60"
    return "61+"


def stage_of(request_date):
    if request_date is None:
        return None
    label = request_date if isinstance(request_date, str) else request_date.isoformat()
    hits = [name for name, bounds in STAGES.items() if bounds[0] <= label < bounds[1]]
    return hits[0] if len(hits) == 1 else None


def k_bin_of(abs_k):
    if abs_k is None or not isfinite(abs_k):
        return None
    if abs_k <= 0.02:
        return "le_0.02"
    if abs_k <= 0.10:
        return "0.02_to_0.10"
    return "gt_0.10"


def expiry_clock_id(chain, scenario_contract):
    overrides = scenario_contract.get("expiry_clock_overrides") or {}
    if chain in overrides:
        return overrides[chain]
    return scenario_contract["expiry_clock_by_chain"].get(chain)


def expiry_nanoseconds(expiration, clock_id):
    """Civil OSI date plus named ET wall. Not an official SOQ."""
    if clock_id not in EXPIRY_CLOCK_WALL:
        raise ContractError(f"unknown expiry clock {clock_id!r}")
    hour, minute = EXPIRY_CLOCK_WALL[clock_id]
    return local_timestamp(_as_date(expiration), time(hour, minute), ZONE)


def _as_date(value):
    if type(value) is date:
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ContractError(f"expiration/request_date is not a civil date: {value!r}")


def _as_iso(value):
    if value is None:
        return None
    if type(value) is date:
        return value.isoformat()
    return str(value)


def _fields(*pairs):
    return pa.schema([*pairs, *_CLOCKS])


def contract_cut_schema():
    s, i64, f64, b, i32 = pa.string(), pa.int64(), pa.float64(), pa.bool_(), pa.int32()
    return _fields(
        ("contract_id", i64), ("chain", s), ("osi_symbol", s), ("expiration", s),
        ("millistrike", i64), ("right", s), ("request_date", s), ("cut_label", s),
        ("cut_ns", i64), ("source_family", s), ("dte", i64), ("dte_bucket", s),
        ("bid", f64), ("mid", f64), ("ask", f64), ("ts_event_ns", i64),
        ("sample_age_ns", i64), ("usable", b), ("quoted", b), ("conflict", b),
        ("base_class", s), ("listed", b), ("listing_known", b), ("oi", i64),
        ("oi_available", b), ("oi_ambiguous", b), ("oi_missing", b),
        ("oi_stale", b), ("oi_expired", b), ("oi_zero", b), ("style", s),
        ("coordinate", s), ("expiry_clock_id", s), ("settlement_class", s),
        ("underlier_assumption", s), ("rate_assumption", s),
        ("dividend_assumption", s), ("multiplier_assumption", s),
        ("model_version", s), ("model_asof", s), ("model_asof_ns", i64),
        ("scenario_id", s), ("scenario_version", s), ("base_assumption", s),
        ("changed_assumption", s), ("scientific_dependencies", s),
        ("group_seal", s), ("group_seal_owner", s), ("S", f64), ("F_used", f64),
        ("F_spotcarry", f64), ("F_parity", f64), ("F_parity_lower", f64),
        ("F_parity_upper", f64), ("F_parity_contributors", i64), ("r", f64),
        ("discount", f64), ("T", f64), ("expiry_ns", i64), ("dt_ns", i64),
        ("iv_bid", f64), ("iv_mid", f64), ("iv_ask", f64), ("iv_lower", f64),
        ("iv_upper", f64), ("residual_bid", f64), ("residual_mid", f64),
        ("residual_ask", f64), ("status", i32), ("status_bid", i32),
        ("status_mid", i32), ("status_ask", i32), ("status_reason", s),
        ("greek_status", i32), ("valuation_input_ok", b), ("valuation_eligible", b),
        ("underlier_ok", b), ("rate_ok", b), ("T_ok", b), ("style_supported", b),
        ("price_admissible", b), ("solver_converged", b), ("iv_identified", b),
        ("iv_bid_identified", b), ("iv_ask_identified", b), ("ask_only", b),
        ("zero_bid", b), ("one_sided", b), ("unbounded", b), ("weak_vega", b),
        ("greek_stable", b), ("crossed_quotes", b),
        *[(n, f64) for n in GREEK_NAMES],
        *[(f"{n}_per_contract", f64) for n in GREEK_NAMES],
        ("k", f64), ("k_bin", s), ("stage", s), ("year", s),
    )


def expiry_cut_schema():
    s, i64, f64 = pa.string(), pa.int64(), pa.float64()
    return _fields(
        ("chain", s), ("request_date", s), ("cut_label", s), ("source_family", s),
        ("expiration", s), ("expiry_ns", i64), ("expiry_clock_id", s),
        ("dte", i64), ("dte_bucket", s), ("T", f64), ("stage", s), ("year", s),
        ("style", s), ("coordinate", s), ("underlier_assumption", s),
        ("rate_assumption", s), ("dividend_assumption", s), ("scenario_id", s),
        ("base_assumption", s), ("changed_assumption", s), ("group_seal", s),
        ("group_seal_owner", s), ("S", f64), ("F_used", f64), ("r", f64),
        ("discount", f64), ("atm_contract_id", i64), ("atm_millistrike", i64),
        ("atm_right", s), ("atm_k", f64), ("atm_abs_kf", f64),
        ("atm_abs_logkf", f64), ("atm_iv", f64), ("atm_w", f64),
        ("atm_call_contract_id", i64), ("atm_call_millistrike", i64),
        ("atm_call_iv", f64), ("atm_put_contract_id", i64),
        ("atm_put_millistrike", i64), ("atm_put_iv", f64),
        ("k_le_0_02_iv_median", f64), ("k_0_02_to_0_10_iv_median", f64),
        ("k_gt_0_10_iv_median", f64), ("k_le_0_02_n", i64),
        ("k_0_02_to_0_10_n", i64), ("k_gt_0_10_n", i64), ("F_parity", f64),
        ("F_parity_lower", f64), ("F_parity_upper", f64),
        ("F_parity_contributors", i64), ("F_parity_admissible", i64),
        ("F_parity_nonpositive", i64), ("F_parity_inadmissible", i64),
        ("n_board_rows", i64), ("n_quoted", i64), ("n_listed_unquoted", i64),
        ("n_usable", i64), ("n_valuation_input_ok", i64),
        ("n_valuation_eligible", i64), ("n_iv_identified", i64),
        ("n_iv_bid_identified", i64), ("n_iv_ask_identified", i64),
        ("n_one_sided", i64), ("n_unbounded", i64), ("n_weak_vega", i64),
        ("n_greek_stable", i64), ("n_greek_unstable", i64),
        ("n_call_identified", i64), ("n_put_identified", i64),
    )


def valuation_coverage_schema():
    s, i64, f64 = pa.string(), pa.int64(), pa.float64()
    fields = [
        ("chain", s), ("request_date", s), ("cut_label", s), ("source_family", s),
        ("right", s), ("dte_bucket", s), ("stage", s), ("year", s),
        ("scenario_id", s), ("base_assumption", s), ("changed_assumption", s),
        ("group_seal", s), ("group_seal_owner", s),
        ("n_board_rows", i64), ("n_quoted", i64), ("n_listed", i64),
        ("n_listed_unquoted", i64), ("n_usable", i64),
        ("n_valuation_input_ok", i64), ("n_valuation_eligible", i64),
        ("n_underlier_ok", i64), ("n_rate_ok", i64), ("n_T_ok", i64),
        ("n_style_supported", i64), ("n_price_admissible", i64),
        ("n_solver_converged", i64), ("n_iv_identified", i64),
        ("n_iv_bid_identified", i64), ("n_iv_ask_identified", i64),
        ("n_one_sided", i64), ("n_unbounded", i64), ("n_weak_vega", i64),
        ("n_greek_stable", i64), ("n_greek_unstable", i64),
        ("n_oi_available", i64), ("n_oi_missing", i64), ("n_oi_ambiguous", i64),
        ("n_oi_stale", i64), ("n_oi_expired", i64), ("n_oi_zero", i64),
        ("n_vix_listing_unknown", i64), ("n_missing_underlier", i64),
        ("n_missing_rate", i64), ("n_conflict", i64), ("n_crossed", i64),
        ("n_ask_only", i64), ("n_zero_bid", i64), ("oi_total_available", i64),
        ("oi_weighted_quoted_fraction", f64),
    ]
    fields.extend((f"n_base_{name}", i64) for name in BASE_CLASSES)
    return _fields(*fields)


def cross_chain_schema():
    s, i64, f64, b = pa.string(), pa.int64(), pa.float64(), pa.bool_()
    fields = [
        ("family_id", s), ("request_date", s), ("cut_label", s),
        ("source_family", s), ("expiration", s), ("scenario_id", s),
        ("base_assumption", s), ("changed_assumption", s),
        ("clock_class_compatible", b), ("exact_T_compatible", b),
        ("cross_comparable", b), ("T_class", s), ("undefined_reason", s),
    ]
    for p in ("ndx", "ndxp", "qqq", "spx", "spxw", "spy"):
        fields.extend([
            (f"{p}_present", b), (f"{p}_T", f64), (f"{p}_expiry_ns", i64),
            (f"{p}_expiry_clock_id", s), (f"{p}_atm_iv", f64),
            (f"{p}_atm_w", f64), (f"{p}_atm_k", f64), (f"{p}_n_iv_identified", i64),
        ])
    return _fields(*fields)


def empty_valuation_tables():
    return {
        "contract_cut": contract_cut_schema().empty_table(),
        "expiry_cut": expiry_cut_schema().empty_table(),
        "coverage": valuation_coverage_schema().empty_table(),
    }


def _table(schema, rows):
    return schema.empty_table() if not rows else pa.Table.from_pylist(rows, schema=schema)


def _require_columns(table, names, label):
    if not isinstance(table, pa.Table):
        raise ContractError(f"{label} must be an Arrow table")
    missing = [name for name in names if name not in table.column_names]
    if missing:
        raise ContractError(f"{label} missing columns {missing}")


def _str_col(table, name, required=True):
    n = len(table)
    if name not in table.column_names:
        if required:
            raise ContractError(f"missing column {name}")
        return np.array([None] * n, dtype=object)
    col = table.column(name)
    if pa.types.is_dictionary(col.type):
        col = col.dictionary_decode()
    values = pc.strftime(col, format="%Y-%m-%d").to_pylist() if pa.types.is_date(col.type) else col.to_pylist()
    out = np.empty(n, dtype=object)
    out[:] = [_as_iso(v) if type(v) is date else v for v in values]
    return out


def _bool_col(table, name, default=False):
    n = len(table)
    if name not in table.column_names:
        return np.full(n, default, dtype=bool)
    col = table.column(name).combine_chunks()
    valid = np.asarray(col.is_valid().to_numpy(zero_copy_only=False), dtype=bool)
    vals = np.asarray(col.fill_null(default).to_numpy(zero_copy_only=False), dtype=bool)
    return np.where(valid, vals, True) if default else vals & valid


def _f64_col(table, name):
    n = len(table)
    if name not in table.column_names:
        return np.full(n, np.nan, dtype=np.float64)
    return np.asarray(table.column(name).combine_chunks().to_numpy(zero_copy_only=False), dtype=np.float64)


def _i64_col(table, name):
    n = len(table)
    if name not in table.column_names:
        return np.zeros(n, dtype=np.int64), np.zeros(n, dtype=bool)
    col = table.column(name).combine_chunks()
    if pa.types.is_floating(col.type):
        raise ContractError(f"{name} must remain int64; float clocks are rejected")
    valid = np.asarray(col.is_valid().to_numpy(zero_copy_only=False), dtype=bool)
    vals = np.asarray(col.fill_null(0).cast(pa.int64()).to_numpy(zero_copy_only=False), dtype=np.int64)
    return vals, valid


def _finite(value):
    return value is not None and isfinite(float(value))


def _median(values):
    present = [float(v) for v in values if v is not None and isfinite(float(v))]
    return None if not present else float(np.median(np.asarray(present, dtype=np.float64)))


def _null_clock_fields():
    return {
        "known_at_ns": None, "received_at_ns": None, "published_at_ns": None,
        "last_actual_update_ns": None, "causal_feature_eligible": False,
    }


def _group_seal(chain, request_date, cut_label, source_family, scenario_id):
    return f"{chain}|{request_date}|{cut_label}|{source_family}|{scenario_id}"


def _style_of(chain, scenario):
    return scenario["style_by_chain"].get(chain)


def _pick_underlier(chain, request_date, cut_label, cut_ns, support, scenario):
    """Named cash/ETF conventions. Future or unpublished same-date cash is rejected."""
    if chain == "VIX":
        return {"S": None, "ok": False, "assumption": "vix_spot_unavailable", "reason": "vix_spot_unavailable"}
    if support is None or len(support) == 0:
        return {"S": None, "ok": False, "assumption": "missing_underlier_support", "reason": "missing_underlier"}
    chains, dates, cuts = _str_col(support, "chain"), _str_col(support, "request_date"), _str_col(support, "cut_label")
    hit = np.flatnonzero((chains == chain) & (dates == request_date) & (cuts == cut_label))
    if hit.size == 0:
        return {"S": None, "ok": False, "assumption": "missing_underlier_support", "reason": "missing_underlier"}
    if chain in ETF_CHAINS:
        if cut_ns is None:
            return {"S": None, "ok": False, "assumption": "missing_cut_clock", "reason": "missing_underlier"}
        present, close = _bool_col(support, "etf_present"), _f64_col(support, "etf_close")
        end_ns, end_ok = _i64_col(support, "etf_bar_end_ns")
        assumption = _str_col(support, "etf_assumption", required=False)
        chosen = None
        for i in hit.tolist():
            if not present[i] or not _finite(close[i]):
                continue
            if not end_ok[i] or int(end_ns[i]) > int(cut_ns):
                continue
            if assumption[i] not in (None, scenario["etf_underlier_policy"]):
                continue
            if chosen is not None and float(close[chosen]) != float(close[i]):
                return {"S": None, "ok": False, "assumption": "underlier_support_ambiguous", "reason": "missing_underlier"}
            chosen = i
        if chosen is None:
            return {"S": None, "ok": False, "assumption": "missing_etf_bar", "reason": "missing_underlier"}
        return {"S": float(close[chosen]), "ok": True, "assumption": scenario["etf_underlier_policy"], "reason": None}
    if chain not in INDEX_CHAINS:
        return {"S": None, "ok": False, "assumption": "style_unsupported", "reason": "style_unsupported"}
    close, cash_date = _f64_col(support, "cash_close"), _str_col(support, "cash_date", required=False)
    same, assumption = _bool_col(support, "cash_same_date"), _str_col(support, "cash_assumption", required=False)
    chosen, want_close = None, cut_label == "cash_close"
    for i in hit.tolist():
        if not _finite(close[i]) or cash_date[i] is None or str(cash_date[i]) > str(request_date):
            continue
        if want_close:
            if not (same[i] and str(cash_date[i]) == str(request_date)):
                continue
            if assumption[i] not in (None, scenario["index_cash_close_policy"]):
                continue
        else:
            if same[i] or str(cash_date[i]) == str(request_date):
                continue
            if assumption[i] not in (None, scenario["index_preclose_cash_policy"]):
                continue
        if chosen is not None and float(close[chosen]) != float(close[i]):
            return {"S": None, "ok": False, "assumption": "underlier_support_ambiguous", "reason": "missing_underlier"}
        chosen = i
    named = scenario["index_cash_close_policy"] if want_close else scenario["index_preclose_cash_policy"]
    if chosen is None:
        return {"S": None, "ok": False, "assumption": named, "reason": "missing_underlier"}
    return {"S": float(close[chosen]), "ok": True, "assumption": named, "reason": None}


def _pick_rate(request_date, cut_label, chain, T, support, scenario):
    named = scenario["rate_assumption"]
    if named == "zero_rate_named":
        return {"r": 0.0, "ok": True, "assumption": named, "reason": None}
    if support is None or len(support) == 0 or T is None or not isfinite(T):
        return {"r": None, "ok": False, "assumption": named, "reason": "missing_rate"}
    dates, cuts = _str_col(support, "request_date"), _str_col(support, "cut_label")
    chains, obs = _str_col(support, "chain", required=False), _str_col(support, "obs_date", required=False)
    tenor, tenor_ok = _i64_col(support, "tenor_days")
    rate, missing, series = _f64_col(support, "rate_pct"), _bool_col(support, "missing_rate"), _str_col(support, "series_id", required=False)
    target, rows = float(T) * 365.0, []
    for i in range(len(support)):
        if dates[i] != request_date:
            continue
        if chains[i] not in (chain, None):
            continue
        if named == "fred_closest_tenor_percent_to_decimal" and cuts[i] not in (cut_label, None):
            continue
        if obs[i] is not None and str(obs[i]) > str(request_date):
            continue
        if missing[i] or not _finite(rate[i]) or not tenor_ok[i]:
            continue
        rows.append((abs(int(tenor[i]) - target), int(tenor[i]), str(series[i] or ""), i))
    if not rows:
        return {"r": None, "ok": False, "assumption": named, "reason": "missing_rate"}
    if named == "fred_closest_tenor_percent_to_decimal":
        rows.sort()
        return {"r": float(rate[rows[0][3]]) / 100.0, "ok": True, "assumption": named, "reason": None}
    tenors = np.array([item[1] for item in rows], dtype=np.float64)
    rates = np.array([float(rate[item[3]]) / 100.0 for item in rows], dtype=np.float64)
    order = np.argsort(tenors, kind="stable")
    uniq_t, uniq_r = [], []
    for t, r in zip(tenors[order].tolist(), rates[order].tolist()):
        if uniq_t and t == uniq_t[-1]:
            continue
        uniq_t.append(t)
        uniq_r.append(r)
    if len(uniq_t) < 2:
        return {"r": None, "ok": False, "assumption": named, "reason": "missing_rate"}
    if target <= uniq_t[0]:
        return {"r": uniq_r[0], "ok": True, "assumption": named, "reason": None}
    if target >= uniq_t[-1]:
        return {"r": uniq_r[-1], "ok": True, "assumption": named, "reason": None}
    i = int(np.searchsorted(np.asarray(uniq_t), target))
    t0, t1 = uniq_t[i - 1], uniq_t[i]
    w = (target - t0) / (t1 - t0)
    return {"r": uniq_r[i - 1] + w * (uniq_r[i] - uniq_r[i - 1]), "ok": True, "assumption": named, "reason": None}


def _dividends(chain, request_date, expiration, cut_ns, expiry_ns, support, scenario):
    if _style_of(chain, scenario) == "european_black":
        return [], [], "q0_named"
    named = scenario["dividend_assumption"]
    if named == "q0_no_dividend" or support is None or len(support) == 0:
        return [], [], named
    symbol = ETF_SYMBOL.get(chain)
    chains, dates = _str_col(support, "chain", required=False), _str_col(support, "request_date", required=False)
    symbols, ex_dates = _str_col(support, "symbol", required=False), _str_col(support, "ex_date", required=False)
    amounts, times, cash = _f64_col(support, "dividend"), [], []
    for i in range(len(support)):
        if dates[i] not in (None, request_date) or chains[i] not in (None, chain):
            continue
        if symbol is not None and symbols[i] not in (None, symbol):
            continue
        ex = ex_dates[i]
        if ex is None or not (str(request_date) < str(ex) <= str(expiration)):
            continue
        if not _finite(amounts[i]) or float(amounts[i]) <= 0.0:
            continue
        ex_ns = local_timestamp(_as_date(ex), time(9, 30), ZONE)
        if cut_ns is None or expiry_ns is None or ex_ns <= int(cut_ns) or ex_ns > int(expiry_ns):
            continue
        times.append(float(years_from_nanoseconds(int(ex_ns) - int(cut_ns))))
        cash.append(float(amounts[i]))
    return times, cash, named


def _reason(order):
    for name, flag in order:
        if flag:
            return name
    return "ok"


def _identified_side(value, status):
    return bool(_finite(value) and status is not None and primary_status(status) in IDENTIFIED_STATUSES)


def _atm_pick(candidates):
    return None if not candidates else min(candidates, key=lambda row: (row[0], row[1], row[2], row[3]))


def _parity_pair(call, put, K, discount):
    if not _finite(discount) or discount <= 0.0 or not _finite(K):
        return None
    c_bid, c_mid, c_ask = call
    p_bid, p_mid, p_ask = put
    mid = K + (c_mid - p_mid) / discount if _finite(c_mid) and _finite(p_mid) else None
    lo = K + (c_bid - p_ask) / discount if _finite(c_bid) and _finite(p_ask) else None
    hi = K + (c_ask - p_bid) / discount if _finite(c_ask) and _finite(p_bid) else None
    return {"mid": mid, "lower": lo, "upper": hi}


def _blank_iv(status=STATUS_UNDEFINED_POINT):
    return {
        "iv_bid": None, "iv_mid": None, "iv_ask": None, "iv_lower": None, "iv_upper": None,
        "residual_bid": None, "residual_mid": None, "residual_ask": None,
        "status": int(status), "status_bid": int(status), "status_mid": int(status),
        "status_ask": int(status), "point_defined": False,
    }


def _invert_key(bid, mid, ask, K, right, T, coord, r, discount, style, div_key, sid):
    pack = lambda x: None if not _finite(x) else float(x)
    return (pack(bid), pack(mid), pack(ask), pack(K), right, pack(T), pack(coord),
            pack(r), pack(discount), style, div_key, sid)


def _cache_result(got, local):
    def side(arr):
        value = arr.reshape(-1)[local]
        return float(value) if np.isfinite(value) else None
    return {
        "iv_bid": side(got.iv_bid), "iv_mid": side(got.iv_mid), "iv_ask": side(got.iv_ask),
        "iv_lower": side(got.iv_lower), "iv_upper": side(got.iv_upper),
        "residual_bid": side(got.residual_bid), "residual_mid": side(got.residual_mid),
        "residual_ask": side(got.residual_ask),
        "status": int(got.status.reshape(-1)[local]),
        "status_bid": int(got.status_bid.reshape(-1)[local]),
        "status_mid": int(got.status_mid.reshape(-1)[local]),
        "status_ask": int(got.status_ask.reshape(-1)[local]),
        "point_defined": bool(got.point_defined.reshape(-1)[local]),
    }


def _div_args(div_t, div_a, n):
    if not div_t:
        return None, None
    if n == 1:
        return list(div_t), list(div_a)
    return [list(div_t) for _ in range(n)], [list(div_a) for _ in range(n)]


def build_valuation_tables(board, underlier_support, fred_support, action_support, *, scenario_contract):
    """Stream one complete chain/date (or mergeable groups). Cap MAX_BOARD_ROWS."""
    scenario = validate_scenario_contract(deepcopy(scenario_contract))
    sid = scenario_identity(scenario)
    _require_columns(board, REQUIRED_BOARD, "board")
    if len(board) > int(scenario["max_board_rows"]):
        raise ContractError(
            f"board batch has {len(board)} rows; cap is {scenario['max_board_rows']} "
            "(root must partition whole chain/date groups)"
        )
    if len(board) == 0:
        return empty_valuation_tables()
    n = len(board)
    chain, request_date = _str_col(board, "chain"), _str_col(board, "request_date")
    cut_label, source_family = _str_col(board, "cut_label"), _str_col(board, "source_family")
    expiration, osi = _str_col(board, "expiration"), _str_col(board, "osi_symbol", required=False)
    right, base_class = _str_col(board, "right"), _str_col(board, "base_class", required=False)
    dte_bucket = _str_col(board, "dte_bucket", required=False)
    cut_ns, cut_ok = _i64_col(board, "cut_ns")
    contract_id, cid_ok = _i64_col(board, "contract_id")
    millistrike, ms_ok = _i64_col(board, "millistrike")
    dte_raw, dte_ok = _i64_col(board, "dte")
    ts_ns, ts_ok = _i64_col(board, "ts_event_ns")
    age_ns, age_ok = _i64_col(board, "sample_age_ns")
    oi, oi_ok = _i64_col(board, "oi")
    bid, ask, mid = _f64_col(board, "bid"), _f64_col(board, "ask"), _f64_col(board, "mid")
    quoted, usable, conflict = _bool_col(board, "quoted"), _bool_col(board, "usable"), _bool_col(board, "conflict")
    listed, listing_known = _bool_col(board, "listed"), _bool_col(board, "listing_known")
    oi_available, oi_ambiguous = _bool_col(board, "oi_available"), _bool_col(board, "oi_ambiguous")
    oi_missing, oi_stale = _bool_col(board, "oi_missing"), _bool_col(board, "oi_stale")
    oi_expired, oi_zero = _bool_col(board, "oi_expired"), _bool_col(board, "oi_zero")
    zero_bid_flag = _bool_col(board, "zero_bid")
    bid_ok, ask_ok, mid_ok = np.isfinite(bid), np.isfinite(ask), np.isfinite(mid)
    mid = np.where(
        mid_ok, mid,
        np.where(bid_ok & ask_ok & (bid > 0.0) & (ask >= bid), 0.5 * (bid + ask), np.nan),
    )
    mid_ok = np.isfinite(mid)
    crossed = bid_ok & ask_ok & (bid > ask)
    ask_only = (~bid_ok | (bid == 0.0) | zero_bid_flag) & ask_ok & (ask > 0.0) & ~crossed & ~conflict
    zero_bid = (bid_ok & (bid == 0.0)) | zero_bid_flag
    valuation_input_ok = quoted & ~conflict & ~crossed & (usable | ask_only)
    listed_unquoted = (~quoted) & listed & listing_known
    groups = np.unique(np.rec.fromarrays([chain, request_date, cut_label, source_family]))
    owner = "caller_complete_group" if len(groups) == 1 else "caller_batch_mergeable"
    underlier_cache, rate_cache, invert_cache = {}, {}, {}
    contract_rows, expiry_rows, coverage_rows = [], [], []
    flags = {name: np.zeros(n, dtype=bool) for name in (
        "iv_identified", "iv_bid_identified", "iv_ask_identified", "underlier_ok",
        "rate_ok", "T_ok", "style_supported", "price_admissible", "solver_converged",
        "one_sided", "unbounded", "weak_vega", "greek_stable", "valuation_eligible",
    )}
    for g in groups:
        g_chain, g_date, g_cut, g_family = str(g[0]), str(g[1]), str(g[2]), str(g[3])
        gmask = (chain == g_chain) & (request_date == g_date) & (cut_label == g_cut) & (source_family == g_family)
        g_cut_ns = int(cut_ns[np.flatnonzero(gmask & cut_ok)[0]]) if np.any(gmask & cut_ok) else None
        style = _style_of(g_chain, scenario)
        coordinate = scenario["coordinate_by_chain"].get(g_chain)
        settlement = scenario["settlement_class_by_chain"].get(g_chain)
        clock_id = expiry_clock_id(g_chain, scenario)
        style_ok = style in ("european_black", "american_spot_fd") and clock_id is not None
        european = style == "european_black"
        ukey = (g_chain, g_date, g_cut, g_cut_ns)
        underlier_cache.setdefault(ukey, _pick_underlier(g_chain, g_date, g_cut, g_cut_ns, underlier_support, scenario))
        underlier, S = underlier_cache[ukey], underlier_cache[ukey]["S"]
        seal = _group_seal(g_chain, g_date, g_cut, g_family, sid)
        stage, year = stage_of(g_date), (g_date[:4] if g_date else None)
        seen_exp = []
        for label in expiration[gmask].tolist():
            if label is not None and label not in seen_exp:
                seen_exp.append(label)
        for exp_label in seen_exp:
            emask = gmask & (expiration == exp_label)
            if np.any(emask & dte_ok):
                dte_val = int(dte_raw[np.flatnonzero(emask & dte_ok)[0]])
            else:
                try:
                    dte_val = (_as_date(exp_label) - _as_date(g_date)).days
                except ContractError:
                    dte_val = None
            bucket = quote_dte_bucket(dte_val) if dte_val is not None else None
            T = expiry_ns = dt_ns = None
            T_is_ok = False
            if clock_id is not None and g_cut_ns is not None:
                expiry_ns = expiry_nanoseconds(exp_label, clock_id)
                dt_ns = int(expiry_ns) - int(g_cut_ns)
                T = float(years_from_nanoseconds(dt_ns))
                T_is_ok = isfinite(T) and T > 0.0
            rkey = (g_date, g_cut, g_chain, None if T is None else float(T), scenario["rate_assumption"])
            rate_cache.setdefault(rkey, _pick_rate(g_date, g_cut, g_chain, T, fred_support, scenario))
            rate, r = rate_cache[rkey], rate_cache[rkey]["r"]
            discount = float(math_exp(-float(r) * float(T))) if rate["ok"] and T_is_ok else None
            F_spot = float(S) * float(math_exp(float(r) * float(T))) if underlier["ok"] and _finite(S) and rate["ok"] and T_is_ok else None
            F_used = F_spot if european else (float(S) if underlier["ok"] and _finite(S) else None)
            div_t, div_a, div_named = _dividends(g_chain, g_date, exp_label, g_cut_ns, expiry_ns, action_support, scenario)
            if european:
                div_named = "q0_named"
            quoted_e, qidx, pair_map = emask & quoted, np.flatnonzero(emask & quoted), {}
            if european and rate["ok"] and T_is_ok:
                sides = {}
                for i in np.flatnonzero(emask & valuation_input_ok & usable).tolist():
                    if ms_ok[i]:
                        sides.setdefault(int(millistrike[i]), {})[str(right[i])] = i
                for strike, pair in sides.items():
                    if "CALL" in pair and "PUT" in pair:
                        ci, pi = pair["CALL"], pair["PUT"]
                        got = _parity_pair((bid[ci], mid[ci], ask[ci]), (bid[pi], mid[pi], ask[pi]), strike / 1000.0, discount)
                        if got is not None:
                            pair_map[strike] = got
            parity_mids, parity_lo, parity_hi = [], [], []
            n_parity = n_parity_adm = n_parity_np = n_parity_bad = 0
            for pair in pair_map.values():
                n_parity += 1
                lo, hi, pmid = pair["lower"], pair["upper"], pair["mid"]
                interval_ok = _finite(lo) and _finite(hi)
                if interval_ok and lo > hi:
                    n_parity_bad += 1
                    continue
                if _finite(pmid) and pmid <= 0.0:
                    n_parity_np += 1
                if interval_ok and (lo <= 0.0 or hi <= 0.0):
                    n_parity_np += 1
                if interval_ok and lo <= hi:
                    n_parity_adm += 1
                    parity_lo.append(lo)
                    parity_hi.append(hi)
                    if _finite(pmid):
                        parity_mids.append(pmid)
                elif _finite(pmid) and pmid > 0.0:
                    n_parity_adm += 1
                    parity_mids.append(pmid)
            flags["style_supported"][emask] = style_ok
            flags["underlier_ok"][emask] = bool(underlier["ok"])
            flags["rate_ok"][emask] = bool(rate["ok"])
            flags["T_ok"][emask] = bool(T_is_ok)
            flags["valuation_eligible"][emask] = (
                valuation_input_ok[emask] & flags["style_supported"][emask]
                & flags["underlier_ok"][emask] & flags["rate_ok"][emask] & flags["T_ok"][emask]
            )
            invert_idx = np.flatnonzero(quoted_e & flags["valuation_eligible"]).tolist()
            greek_out = {}
            inv = np.asarray(invert_idx, dtype=np.int64)
            if inv.size and style_ok:
                rights = right[inv]
                right_ok = np.array([
                    v is not None and str(v).strip().lower() in ("c", "call", "1", "+1", "p", "put", "-1")
                    for v in rights.tolist()
                ], dtype=bool)
                for j, i in enumerate(inv.tolist()):
                    if not right_ok[j]:
                        invert_cache[_invert_key(bid[i], mid[i], ask[i], float(millistrike[i]) / 1000.0 if ms_ok[i] else None, str(right[i]), T, F_used, r, discount, style, tuple(div_t), sid)] = _blank_iv(STATUS_INVALID_INPUT)
                inv = inv[right_ok]
                rights = rights[right_ok]
            if inv.size and style_ok:
                bids, mids, asks = bid[inv], mid[inv], ask[inv]
                Ks = np.where(ms_ok[inv], millistrike[inv].astype(np.float64) / 1000.0, np.nan)
                Ts = np.full(inv.size, float(T)); rs = np.full(inv.size, float(r))
                Ds = np.full(inv.size, float(discount)); coords = np.full(inv.size, float(F_used))
                Ss = np.full(inv.size, float(S))
                keys = [_invert_key(bids[j], mids[j], asks[j], Ks[j], str(rights[j]), Ts[j], coords[j], rs[j], Ds[j], style, tuple(div_t), sid) for j in range(inv.size)]
                need = [j for j, key in enumerate(keys) if key not in invert_cache]
                try:
                    if need:
                        nj = np.asarray(need, dtype=np.int64)
                        dt, da = _div_args(div_t, div_a, nj.size)
                        got = invert_quote_interval(bids[nj], mids[nj], asks[nj], coords[nj], Ks[nj], Ts[nj], Ds[nj], rights[nj]) if european else invert_american_quote_interval(
                            bids[nj], mids[nj], asks[nj], Ss[nj], Ks[nj], Ts[nj], rs[nj], rights[nj],
                            dividend_times=dt, dividend_amounts=da, n_space=AMERICAN_NUMERICAL_N_SPACE,
                        )
                        for local, src in enumerate(need):
                            invert_cache[keys[src]] = _cache_result(got, local)
                    greeks_need, greeks_sigma = [], []
                    for j, i in enumerate(inv.tolist()):
                        payload, st = invert_cache[keys[j]], invert_cache[keys[j]]["status"]
                        flags["iv_bid_identified"][i] = _identified_side(payload["iv_bid"], payload["status_bid"])
                        flags["iv_ask_identified"][i] = _identified_side(payload["iv_ask"], payload["status_ask"])
                        flags["iv_identified"][i] = bool(payload["point_defined"] and _finite(payload["iv_mid"]))
                        flags["solver_converged"][i] = primary_status(st) == STATUS_CONVERGED
                        flags["price_admissible"][i] = primary_status(st) not in (STATUS_FAILED_BRACKET, STATUS_INVALID_INPUT, STATUS_CROSSED_QUOTES)
                        flags["unbounded"][i] = primary_status(st) == STATUS_UNBOUNDED_SIDE
                        flags["one_sided"][i] = has_flag(st, FLAG_ASK_ONLY) or (ask_only[i] and not flags["iv_identified"][i])
                        flags["weak_vega"][i] = has_flag(st, FLAG_WEAK_VEGA)
                        if flags["iv_identified"][i]:
                            greeks_need.append(i)
                            greeks_sigma.append(float(payload["iv_mid"]))
                    if greeks_need:
                        gi = np.asarray(greeks_need, dtype=np.int64)
                        sig, Kg = np.asarray(greeks_sigma, dtype=np.float64), np.where(ms_ok[gi], millistrike[gi].astype(np.float64) / 1000.0, np.nan)
                        dt, da = _div_args(div_t, div_a, gi.size)
                        gres = black_greeks(np.full(gi.size, float(F_used)), Kg, np.full(gi.size, float(T)), sig, np.full(gi.size, float(discount)), right[gi], np.full(gi.size, float(r))) if european else american_greeks(
                            np.full(gi.size, float(S)), Kg, np.full(gi.size, float(T)), sig, np.full(gi.size, float(r)), right[gi],
                            dividend_times=dt, dividend_amounts=da, n_space=AMERICAN_NUMERICAL_N_SPACE,
                        )
                        for local, i in enumerate(greeks_need):
                            stg = int(gres.status.reshape(-1)[local])
                            unstable = primary_status(stg) != STATUS_CONVERGED or has_flag(stg, FLAG_WEAK_VEGA) or has_flag(stg, FLAG_UNSTABLE_GREEK)
                            vals = {}
                            for name in GREEK_NAMES:
                                raw = float(getattr(gres, name).reshape(-1)[local])
                                vals[name] = raw if isfinite(raw) and not unstable else None
                            flags["greek_stable"][i] = (not unstable) and all(vals[name] is not None for name in GREEK_NAMES)
                            greek_out[i] = (stg, vals)
                except DependencyUnavailable:
                    for key in keys:
                        invert_cache[key] = _blank_iv(STATUS_NATIVE_UNAVAILABLE)
                    greek_out = {}
            atm_pool, call_pool, put_pool, k_iv = [], [], [], {name: [] for name in K_BINS}
            for i in qidx.tolist():
                K = float(millistrike[i]) / 1000.0 if ms_ok[i] else None
                pair = pair_map.get(int(millistrike[i])) if ms_ok[i] else None
                payload = None
                if flags["valuation_eligible"][i]:
                    payload = invert_cache.get(_invert_key(bid[i], mid[i], ask[i], K, str(right[i]), T, F_used, r, discount, style, tuple(div_t), sid))
                if payload is None:
                    payload = _blank_iv(STATUS_CROSSED_QUOTES if (conflict[i] or crossed[i]) else (STATUS_ZERO_T if (not T_is_ok and T == 0.0) else STATUS_UNDEFINED_POINT))
                gstat, gvals = greek_out.get(i, (STATUS_UNDEFINED_POINT, {name: None for name in GREEK_NAMES}))
                k = float(log(K / float(F_used))) if _finite(K) and _finite(F_used) and F_used > 0.0 and K > 0.0 else None
                k_bin = k_bin_of(None if k is None else abs(k))
                if flags["iv_identified"][i] and k_bin is not None and _finite(payload["iv_mid"]):
                    k_iv[k_bin].append(float(payload["iv_mid"]))
                if flags["iv_identified"][i] and _finite(K) and _finite(F_used):
                    item = (abs(k) if k is not None else abs(K - float(F_used)), abs(K - float(F_used)), K, int(contract_id[i]) if cid_ok[i] else 1 << 62, payload["iv_mid"], str(right[i]), int(millistrike[i]) if ms_ok[i] else None)
                    atm_pool.append(item)
                    (call_pool if str(right[i]) == "CALL" else put_pool if str(right[i]) == "PUT" else []).append(item)
                g_pc = {name: (float(apply_contract_multiplier(gvals[name], MULTIPLIER_SCENARIO)) if scenario["apply_multiplier"] and gvals[name] is not None else None) for name in GREEK_NAMES}
                reason = _reason((
                    ("conflict", conflict[i]), ("crossed_quotes", crossed[i]),
                    ("style_unsupported", not style_ok), ("T_nonpositive", not T_is_ok),
                    ("missing_rate", not rate["ok"]),
                    (underlier["reason"] or "missing_underlier", not underlier["ok"]),
                    ("native_unavailable", payload["status"] == STATUS_NATIVE_UNAVAILABLE),
                    ("price_inadmissible", not flags["price_admissible"][i] and flags["valuation_eligible"][i]),
                    ("unbounded_side", flags["unbounded"][i]),
                    ("iv_unidentified", not flags["iv_identified"][i]),
                    ("weak_vega", flags["weak_vega"][i]),
                    ("greek_unstable", flags["iv_identified"][i] and not flags["greek_stable"][i]),
                    ("ask_only", ask_only[i]), ("zero_bid", zero_bid[i]),
                ))
                contract_rows.append({
                    "contract_id": int(contract_id[i]) if cid_ok[i] else None,
                    "chain": g_chain, "osi_symbol": osi[i], "expiration": exp_label,
                    "millistrike": int(millistrike[i]) if ms_ok[i] else None,
                    "right": right[i], "request_date": g_date, "cut_label": g_cut,
                    "cut_ns": int(cut_ns[i]) if cut_ok[i] else g_cut_ns,
                    "source_family": g_family,
                    "dte": dte_val if dte_val is not None else (int(dte_raw[i]) if dte_ok[i] else None),
                    "dte_bucket": dte_bucket[i] or bucket,
                    "bid": float(bid[i]) if bid_ok[i] else None,
                    "mid": float(mid[i]) if mid_ok[i] else None,
                    "ask": float(ask[i]) if ask_ok[i] else None,
                    "ts_event_ns": int(ts_ns[i]) if ts_ok[i] else None,
                    "sample_age_ns": int(age_ns[i]) if age_ok[i] else None,
                    "usable": bool(usable[i]), "quoted": True, "conflict": bool(conflict[i]),
                    "base_class": base_class[i], "listed": bool(listed[i]),
                    "listing_known": bool(listing_known[i]),
                    "oi": int(oi[i]) if oi_ok[i] else None,
                    "oi_available": bool(oi_available[i]), "oi_ambiguous": bool(oi_ambiguous[i]),
                    "oi_missing": bool(oi_missing[i]), "oi_stale": bool(oi_stale[i]),
                    "oi_expired": bool(oi_expired[i]), "oi_zero": bool(oi_zero[i]),
                    "style": style, "coordinate": coordinate, "expiry_clock_id": clock_id,
                    "settlement_class": settlement, "underlier_assumption": underlier["assumption"],
                    "rate_assumption": rate["assumption"], "dividend_assumption": div_named,
                    "multiplier_assumption": scenario["multiplier_assumption"],
                    "model_version": MODEL_VERSION, "model_asof": MODEL_ASOF,
                    "model_asof_ns": g_cut_ns, "scenario_id": sid,
                    "scenario_version": SCENARIO_VERSION,
                    "base_assumption": scenario["base_assumption"],
                    "changed_assumption": scenario["changed_assumption"],
                    "scientific_dependencies": (
                        f"time_basis=actual_365_fixed;style={style};coordinate={coordinate};"
                        f"expiry_clock={clock_id};underlier={underlier['assumption']};"
                        f"rate={rate['assumption']};dividend={div_named};model_asof=cut"
                    ),
                    "group_seal": seal, "group_seal_owner": owner, "S": S,
                    "F_used": F_used, "F_spotcarry": F_spot,
                    "F_parity": None if pair is None else pair["mid"],
                    "F_parity_lower": None if pair is None else pair["lower"],
                    "F_parity_upper": None if pair is None else pair["upper"],
                    "F_parity_contributors": 0 if pair is None else 1,
                    "r": r, "discount": discount, "T": T, "expiry_ns": expiry_ns, "dt_ns": dt_ns,
                    **{k: payload[k] for k in ("iv_bid", "iv_mid", "iv_ask", "iv_lower", "iv_upper", "residual_bid", "residual_mid", "residual_ask", "status", "status_bid", "status_mid", "status_ask")},
                    "status_reason": reason, "greek_status": gstat,
                    "valuation_input_ok": bool(valuation_input_ok[i]),
                    "valuation_eligible": bool(flags["valuation_eligible"][i]),
                    "underlier_ok": bool(flags["underlier_ok"][i]),
                    "rate_ok": bool(flags["rate_ok"][i]), "T_ok": bool(flags["T_ok"][i]),
                    "style_supported": bool(flags["style_supported"][i]),
                    "price_admissible": bool(flags["price_admissible"][i]),
                    "solver_converged": bool(flags["solver_converged"][i]),
                    "iv_identified": bool(flags["iv_identified"][i]),
                    "iv_bid_identified": bool(flags["iv_bid_identified"][i]),
                    "iv_ask_identified": bool(flags["iv_ask_identified"][i]),
                    "ask_only": bool(ask_only[i]), "zero_bid": bool(zero_bid[i]),
                    "one_sided": bool(flags["one_sided"][i]), "unbounded": bool(flags["unbounded"][i]),
                    "weak_vega": bool(flags["weak_vega"][i]),
                    "greek_stable": bool(flags["greek_stable"][i]),
                    "crossed_quotes": bool(crossed[i]),
                    **gvals, **{f"{name}_per_contract": g_pc[name] for name in GREEK_NAMES},
                    "k": k, "k_bin": k_bin, "stage": stage, "year": year,
                    **_null_clock_fields(),
                })
            atm, atm_call, atm_put = _atm_pick(atm_pool), _atm_pick(call_pool), _atm_pick(put_pool)
            atm_k = float(log(atm[2] / float(F_used))) if atm is not None and _finite(F_used) and F_used > 0 else None
            expiry_rows.append({
                "chain": g_chain, "request_date": g_date, "cut_label": g_cut,
                "source_family": g_family, "expiration": exp_label, "expiry_ns": expiry_ns,
                "expiry_clock_id": clock_id, "dte": dte_val, "dte_bucket": bucket, "T": T,
                "stage": stage, "year": year, "style": style, "coordinate": coordinate,
                "underlier_assumption": underlier["assumption"], "rate_assumption": rate["assumption"],
                "dividend_assumption": div_named, "scenario_id": sid,
                "base_assumption": scenario["base_assumption"],
                "changed_assumption": scenario["changed_assumption"],
                "group_seal": seal, "group_seal_owner": owner, "S": S, "F_used": F_used,
                "r": r, "discount": discount,
                "atm_contract_id": None if atm is None else atm[3],
                "atm_millistrike": None if atm is None else atm[6],
                "atm_right": None if atm is None else atm[5], "atm_k": atm_k,
                "atm_abs_kf": None if atm is None else atm[1],
                "atm_abs_logkf": None if atm is None else atm[0],
                "atm_iv": None if atm is None else atm[4],
                "atm_w": None if atm is None or not _finite(T) or not _finite(atm[4]) else float(atm[4]) ** 2 * float(T),
                "atm_call_contract_id": None if atm_call is None else atm_call[3],
                "atm_call_millistrike": None if atm_call is None else atm_call[6],
                "atm_call_iv": None if atm_call is None else atm_call[4],
                "atm_put_contract_id": None if atm_put is None else atm_put[3],
                "atm_put_millistrike": None if atm_put is None else atm_put[6],
                "atm_put_iv": None if atm_put is None else atm_put[4],
                "k_le_0_02_iv_median": _median(k_iv["le_0.02"]),
                "k_0_02_to_0_10_iv_median": _median(k_iv["0.02_to_0.10"]),
                "k_gt_0_10_iv_median": _median(k_iv["gt_0.10"]),
                "k_le_0_02_n": len(k_iv["le_0.02"]), "k_0_02_to_0_10_n": len(k_iv["0.02_to_0.10"]),
                "k_gt_0_10_n": len(k_iv["gt_0.10"]), "F_parity": _median(parity_mids),
                "F_parity_lower": _median(parity_lo), "F_parity_upper": _median(parity_hi),
                "F_parity_contributors": n_parity, "F_parity_admissible": n_parity_adm,
                "F_parity_nonpositive": n_parity_np, "F_parity_inadmissible": n_parity_bad,
                "n_board_rows": int(emask.sum()), "n_quoted": int(quoted_e.sum()),
                "n_listed_unquoted": int((emask & listed_unquoted).sum()),
                "n_usable": int((emask & usable).sum()),
                "n_valuation_input_ok": int((emask & valuation_input_ok).sum()),
                "n_valuation_eligible": int((emask & flags["valuation_eligible"]).sum()),
                "n_iv_identified": int((emask & flags["iv_identified"]).sum()),
                "n_iv_bid_identified": int((emask & flags["iv_bid_identified"]).sum()),
                "n_iv_ask_identified": int((emask & flags["iv_ask_identified"]).sum()),
                "n_one_sided": int((emask & flags["one_sided"]).sum()),
                "n_unbounded": int((emask & flags["unbounded"]).sum()),
                "n_weak_vega": int((emask & flags["weak_vega"]).sum()),
                "n_greek_stable": int((emask & flags["greek_stable"]).sum()),
                "n_greek_unstable": int((emask & flags["iv_identified"] & ~flags["greek_stable"]).sum()),
                "n_call_identified": int((emask & flags["iv_identified"] & (right == "CALL")).sum()),
                "n_put_identified": int((emask & flags["iv_identified"] & (right == "PUT")).sum()),
                **_null_clock_fields(),
            })
        gidx = np.flatnonzero(gmask)
        right_vals = np.array(["unknown" if v is None else str(v) for v in right[gmask].tolist()], dtype=object)
        buckets = np.array([
            dte_bucket[i] or (quote_dte_bucket(int(dte_raw[i])) if dte_ok[i] else None) or "unknown"
            for i in gidx.tolist()
        ], dtype=object)
        seen_rb = []
        for key in zip(right_vals.tolist(), buckets.tolist()):
            if key not in seen_rb:
                seen_rb.append(key)
        for rgt, bkt in seen_rb:
            smask = np.zeros(n, dtype=bool)
            for j, i in enumerate(gidx.tolist()):
                if right_vals[j] == rgt and buckets[j] == bkt:
                    smask[i] = True
            oi_total = int(oi[smask & oi_available & oi_ok].sum()) if np.any(smask & oi_available & oi_ok) else 0
            oi_quoted = int(oi[smask & oi_available & oi_ok & quoted].sum()) if np.any(smask & oi_available & oi_ok & quoted) else 0
            row = {
                "chain": g_chain, "request_date": g_date, "cut_label": g_cut,
                "source_family": g_family, "right": rgt, "dte_bucket": bkt,
                "stage": stage, "year": year, "scenario_id": sid,
                "base_assumption": scenario["base_assumption"],
                "changed_assumption": scenario["changed_assumption"],
                "group_seal": seal, "group_seal_owner": owner,
                "n_board_rows": int(smask.sum()), "n_quoted": int((smask & quoted).sum()),
                "n_listed": int((smask & listed & listing_known).sum()),
                "n_listed_unquoted": int((smask & listed_unquoted).sum()),
                "n_usable": int((smask & usable).sum()),
                "n_valuation_input_ok": int((smask & valuation_input_ok).sum()),
                "n_valuation_eligible": int((smask & flags["valuation_eligible"]).sum()),
                "n_underlier_ok": int((smask & flags["underlier_ok"]).sum()),
                "n_rate_ok": int((smask & flags["rate_ok"]).sum()),
                "n_T_ok": int((smask & flags["T_ok"]).sum()),
                "n_style_supported": int((smask & flags["style_supported"]).sum()),
                "n_price_admissible": int((smask & flags["price_admissible"]).sum()),
                "n_solver_converged": int((smask & flags["solver_converged"]).sum()),
                "n_iv_identified": int((smask & flags["iv_identified"]).sum()),
                "n_iv_bid_identified": int((smask & flags["iv_bid_identified"]).sum()),
                "n_iv_ask_identified": int((smask & flags["iv_ask_identified"]).sum()),
                "n_one_sided": int((smask & flags["one_sided"]).sum()),
                "n_unbounded": int((smask & flags["unbounded"]).sum()),
                "n_weak_vega": int((smask & flags["weak_vega"]).sum()),
                "n_greek_stable": int((smask & flags["greek_stable"]).sum()),
                "n_greek_unstable": int((smask & flags["iv_identified"] & ~flags["greek_stable"]).sum()),
                "n_oi_available": int((smask & oi_available).sum()),
                "n_oi_missing": int((smask & oi_missing).sum()),
                "n_oi_ambiguous": int((smask & oi_ambiguous).sum()),
                "n_oi_stale": int((smask & oi_stale).sum()),
                "n_oi_expired": int((smask & oi_expired).sum()),
                "n_oi_zero": int((smask & oi_zero).sum()),
                "n_vix_listing_unknown": int((smask & (chain == "VIX") & ~listing_known).sum()),
                "n_missing_underlier": int((smask & ~flags["underlier_ok"]).sum()),
                "n_missing_rate": int((smask & ~flags["rate_ok"]).sum()),
                "n_conflict": int((smask & conflict).sum()),
                "n_crossed": int((smask & crossed).sum()),
                "n_ask_only": int((smask & ask_only).sum()),
                "n_zero_bid": int((smask & zero_bid).sum()),
                "oi_total_available": oi_total,
                "oi_weighted_quoted_fraction": None if oi_total <= 0 else oi_quoted / oi_total,
                **_null_clock_fields(),
            }
            for name in BASE_CLASSES:
                row[f"n_base_{name}"] = int((smask & (base_class == name)).sum())
            coverage_rows.append(row)
    return {
        "contract_cut": _table(contract_cut_schema(), contract_rows),
        "expiry_cut": _table(expiry_cut_schema(), expiry_rows),
        "coverage": _table(valuation_coverage_schema(), coverage_rows),
    }


def build_cross_chain_table(expiry_tables, *, scenario_contract):
    """Native-expiry comparators. Exact T or same clock class only; else undefined."""
    scenario = validate_scenario_contract(deepcopy(scenario_contract))
    sid = scenario_identity(scenario)
    if expiry_tables is None:
        return cross_chain_schema().empty_table()
    tables = [expiry_tables] if isinstance(expiry_tables, pa.Table) else list(expiry_tables)
    rows = []
    for table in tables:
        if table is not None and len(table):
            rows.extend(table.to_pylist())
    if not rows:
        return cross_chain_schema().empty_table()
    by_key = defaultdict(dict)
    for row in rows:
        if row.get("scenario_id") not in (None, sid):
            continue
        key = (row.get("request_date"), row.get("cut_label"), row.get("source_family"), row.get("expiration"))
        by_key[key][row.get("chain")] = row
    prefix = {"NDX": "ndx", "NDXP": "ndxp", "QQQ": "qqq", "SPX": "spx", "SPXW": "spxw", "SPY": "spy"}
    out = []
    for (req, cut, family, expiration), present in sorted(by_key.items()):
        for family_id, members in CROSS_FAMILIES:
            clocks = [present[c]["expiry_clock_id"] for c in members if c in present]
            Ts = [present[c]["expiry_ns"] for c in members if c in present and present[c].get("expiry_ns") is not None]
            exact_T = len(Ts) >= 2 and len(set(Ts)) == 1
            clock_ok = len(clocks) >= 2 and len(set(clocks)) == 1
            missing = [c for c in members if c not in present]
            complete = not missing
            if exact_T and complete:
                t_class, comparable, reason = "exact_T", True, None
            elif clock_ok and complete:
                t_class, comparable, reason = "native_expiry_clock_class", True, None
            else:
                t_class, comparable = "undefined", False
                if clocks and len(set(clocks)) > 1:
                    reason = "incompatible_clock_class"
                elif missing:
                    reason = "incomplete_pair"
                elif Ts and len(set(Ts)) > 1:
                    reason = "inexact_T"
                else:
                    reason = "undefined_incompatible"
            rec = {
                "family_id": family_id, "request_date": req, "cut_label": cut,
                "source_family": family, "expiration": expiration, "scenario_id": sid,
                "base_assumption": scenario["base_assumption"],
                "changed_assumption": scenario["changed_assumption"],
                "clock_class_compatible": clock_ok, "exact_T_compatible": exact_T,
                "cross_comparable": comparable, "T_class": t_class,
                "undefined_reason": reason, **_null_clock_fields(),
            }
            for name in prefix.values():
                rec.update({
                    f"{name}_present": False, f"{name}_T": None, f"{name}_expiry_ns": None,
                    f"{name}_expiry_clock_id": None, f"{name}_atm_iv": None,
                    f"{name}_atm_w": None, f"{name}_atm_k": None, f"{name}_n_iv_identified": None,
                })
            for chain_name in members:
                p = prefix[chain_name]
                rec[f"{p}_present"] = chain_name in present
                if chain_name not in present:
                    continue
                src = present[chain_name]
                rec[f"{p}_T"] = src.get("T")
                rec[f"{p}_expiry_ns"] = src.get("expiry_ns")
                rec[f"{p}_expiry_clock_id"] = src.get("expiry_clock_id")
                rec[f"{p}_n_iv_identified"] = src.get("n_iv_identified")
                rec[f"{p}_atm_iv"] = src.get("atm_iv") if comparable else None
                rec[f"{p}_atm_w"] = src.get("atm_w") if comparable else None
                rec[f"{p}_atm_k"] = src.get("atm_k") if comparable else None
            out.append(rec)
    return _table(cross_chain_schema(), out)


def build_valuation_report(contract_cut, expiry_cut, coverage, *, intended_dates, scenario_contract=None):
    """Equal-date means, block-5 bootstrap 1000, seed 20260908. Descriptive only."""
    if not intended_dates:
        raise ContractError("report requires an explicit intended date sequence")
    dates = tuple(day if isinstance(day, str) else _as_iso(day) for day in intended_dates)
    cfg = dict(seed=STATISTICS_SEED, block_length=STATISTICS_BLOCK, replicates=STATISTICS_REPLICATES,
               minimum_independent_dates=STATISTICS_MIN_DATES, minimum_events=STATISTICS_MIN_EVENTS)
    sid = None if scenario_contract is None else scenario_identity(scenario_contract)
    contracts = [] if contract_cut is None or len(contract_cut) == 0 else contract_cut.to_pylist()
    expiries = [] if expiry_cut is None or len(expiry_cut) == 0 else expiry_cut.to_pylist()
    covers = [] if coverage is None or len(coverage) == 0 else coverage.to_pylist()
    if sid is not None:
        contracts = [row for row in contracts if row.get("scenario_id") in (None, sid)]
        expiries = [row for row in expiries if row.get("scenario_id") in (None, sid)]
        covers = [row for row in covers if row.get("scenario_id") in (None, sid)]

    def _cells(rows, field, pred=None):
        cells = {day: [] for day in dates}
        for row in rows:
            day = row.get("request_date")
            if day not in cells or (pred is not None and not pred(row)):
                continue
            value = row.get(field)
            if value is not None and _finite(value):
                cells[day].append(float(value))
        return {day: (values or None) for day, values in cells.items()}

    def _frac(rows, pred_num, pred_den):
        cells = {day: [] for day in dates}
        for row in rows:
            day = row.get("request_date")
            if day not in cells or not pred_den(row):
                continue
            cells[day].append(1.0 if pred_num(row) else 0.0)
        return {day: (values or None) for day, values in cells.items()}

    def _stats(metrics):
        clean = {name: cells for name, cells in metrics.items() if any(v is not None for v in cells.values())}
        return observed_date_statistics(clean or {"empty": {day: None for day in dates}}, dates, **cfg)

    groups = {"overall": _stats({
        "identified_iv_mid": _cells(contracts, "iv_mid", lambda r: r.get("iv_identified")),
        "residual_mid": _cells(contracts, "residual_mid", lambda r: r.get("iv_identified")),
        "atm_iv": _cells(expiries, "atm_iv"), "atm_w": _cells(expiries, "atm_w"),
        "dte0_T": _cells(expiries, "T", lambda r: r.get("dte") == 0),
        "dte0_iv": _cells(expiries, "atm_iv", lambda r: r.get("dte") == 0),
        "monotonic_iv_fraction": _frac(
            contracts,
            lambda r: bool(r.get("iv_identified") and _finite(r.get("iv_bid")) and _finite(r.get("iv_mid")) and _finite(r.get("iv_ask")) and r["iv_bid"] <= r["iv_mid"] <= r["iv_ask"]),
            lambda r: bool(r.get("iv_identified")),
        ),
        "failure_fraction": _frac(contracts, lambda r: not r.get("iv_identified"), lambda r: True),
        "listed_unquoted_fraction": _frac(covers, lambda r: (r.get("n_listed_unquoted") or 0) > 0, lambda r: (r.get("n_board_rows") or 0) > 0),
    })}
    for dim, getter in (
        ("chain", lambda r: r.get("chain")), ("source_family", lambda r: r.get("source_family")),
        ("cut_label", lambda r: r.get("cut_label")), ("right", lambda r: r.get("right")),
        ("dte_bucket", lambda r: r.get("dte_bucket")), ("k_bin", lambda r: r.get("k_bin")),
        ("stage", lambda r: r.get("stage")), ("year", lambda r: r.get("year")),
    ):
        values = sorted({getter(row) for row in contracts + expiries + covers if getter(row) is not None})
        for value in values:
            groups[f"{dim}={value}"] = _stats({
                "identified_iv_mid": _cells(contracts, "iv_mid", lambda r, v=value: r.get("iv_identified") and getter(r) == v),
                "atm_iv": _cells(expiries, "atm_iv", lambda r, v=value: getter(r) == v),
            })
    near_broad = {}
    by_id = defaultdict(dict)
    for row in contracts:
        if row.get("iv_identified"):
            by_id[(row.get("contract_id"), row.get("request_date"), row.get("cut_label"))][row.get("source_family")] = row
    for key, fams in by_id.items():
        if "near" in fams and "broad" in fams:
            near_broad.setdefault(key[1], []).append(float(fams["near"]["iv_mid"]) - float(fams["broad"]["iv_mid"]))
    groups["near_minus_broad_same_contract_cut"] = _stats({
        "iv_mid_diff": {day: (near_broad.get(day) or None) for day in dates},
    })
    return {
        "study": STUDY_ID, "schema": "options_historical_valuation_report_v1",
        "scenario_id": sid, "certification_claimed": False,
        "statistics": {
            "seed": STATISTICS_SEED, "block_length": STATISTICS_BLOCK,
            "replicates": STATISTICS_REPLICATES, "confidence": 0.95,
            "minimum_dates": STATISTICS_MIN_DATES, "minimum_events": STATISTICS_MIN_EVENTS,
            "estimator": "date_mean",
        },
        "groups": groups,
        "exclusions": (
            "no_context_forecast", "no_vrp_oof", "no_svi", "no_flow",
            "no_holdings_nodes_maxpain", "no_pnl", "no_location",
        ),
    }