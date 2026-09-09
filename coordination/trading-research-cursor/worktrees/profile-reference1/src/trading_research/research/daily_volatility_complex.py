"""Acquired daily VX/VIX complex measurement.

Date-only observations. This is not official VIX or VVIX replication, not a
variance interpolator, and not Context. Monthly and weekly curves stay separate.
Unknown duration originals stay separate. Combined FRED is a comparison copy.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, time, timedelta
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.operations.artifacts import artifact_ref
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.scoring import quantile

VERSION = "daily-volatility-complex-measurement-v1"
PRIMARY_START = date(2020, 1, 1)
PRIMARY_END = date(2026, 9, 3)
STAGE_BOUNDS = {
    "training": (date(2020, 1, 1), date(2023, 1, 1)),
    "development": (date(2023, 1, 1), date(2025, 1, 1)),
    "confirmation": (date(2025, 1, 1), date(2026, 9, 4)),
}
PRICE_BASES = ("settlement", "close")
TENORS = (30, 60, 90)
QUANTILES = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
STAT_SEED = 20260908
STAT_BLOCK = 5
STAT_REPS = 1000
STAT_CONFIDENCE = 0.95
STAT_MIN_DATES = 100
STAT_MIN_EVENTS = 20
KNOWN_CURVE_FAMILIES = frozenset({"monthly", "weekly"})
MONTHLY_LABELS = frozenset({
    "m", "monthly", "month", "standard", "standard_monthly", "standard monthly",
})
WEEKLY_LABELS = frozenset({"w", "weekly", "week"})
PRIMARY_INDEX_FILES = frozenset({"VIX.parquet", "VIX3M.parquet", "VVIX.parquet", "VXN.parquet"})
INDEX_SYMBOLS = ("VIX", "VIX3M", "VXN", "VVIX")
PROXY = "vx_futures_price_not_variance_or_official_vix"
INDEX_SOURCE_FACTS = {
    "VIX.parquet": {"publisher": "FRED", "independent_of_combined_fred": False},
    "VIX3M.parquet": {"publisher": "FRED", "independent_of_combined_fred": False},
    "VXN.parquet": {"publisher": "FRED", "independent_of_combined_fred": False},
    "VVIX.parquet": {"publisher": "Cboe", "independent_of_combined_fred": True},
    "fred-volatility.parquet": {
        "publisher": "FRED", "role": "comparison_copy", "independent_history": False,
    },
}


def normalize_duration(label):
    if label is None:
        return {"family": None, "original": None}
    original = label if type(label) is str else str(label)
    key = original.strip().lower()
    if key in MONTHLY_LABELS:
        return {"family": "monthly", "original": original}
    if key in WEEKLY_LABELS:
        return {"family": "weekly", "original": original}
    return {"family": "unexpected", "original": original}


def duration_curve_key(label):
    parsed = normalize_duration(label)
    if parsed["family"] in KNOWN_CURVE_FAMILIES:
        return parsed["family"]
    if parsed["original"] is None:
        return None
    return "unexpected:" + parsed["original"]


def as_date(value):
    if value is None or value == "":
        return None
    if type(value) is date:
        return value
    if hasattr(value, "date") and callable(value.date) and not isinstance(value, str):
        try:
            return value.date()
        except Exception:
            return None
    if type(value) is str:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def as_float(value):
    if value is None or isinstance(value, bool) or isinstance(value, (str, bytes)):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def finite_positive(value):
    number = as_float(value)
    return number is not None and number > 0.0


def calendar_dte(trade_date, expiration):
    trade = as_date(trade_date)
    exp = as_date(expiration)
    if trade is None or exp is None:
        return None
    return (exp - trade).days


def contract_identity(row):
    expiration = as_date(row.get("contract_expiration"))
    return (
        row.get("root"),
        expiration,
        row.get("duration_type"),
        row.get("contract_label"),
        row.get("product_display"),
        row.get("source_sha256"),
    )


def identity_record(row):
    expiration = as_date(row.get("contract_expiration"))
    return {
        "root": row.get("root"),
        "contract_expiration": None if expiration is None else expiration.isoformat(),
        "duration_type": row.get("duration_type"),
        "contract_label": row.get("contract_label"),
        "product_display": row.get("product_display"),
        "source_path": row.get("source_path"),
        "source_sha256": row.get("source_sha256"),
    }


def encode_json(value):
    if value is None:
        return None
    return json.dumps(_json_safe(value), sort_keys=True, allow_nan=False)


def observation_clock(observed_date, realtime_start=None, realtime_end=None):
    return {
        "observed_date": as_date(observed_date),
        "known_at_ns": None,
        "causal_feature_eligible": False,
        "usable_as_known_feature": False,
        "expected_next_publication": None,
        "close_clock": None,
        "next_day_availability": None,
        "fred_realtime_start": as_date(realtime_start),
        "fred_realtime_end": as_date(realtime_end),
        "fred_vintage_is_not_pre_event_availability": True,
        "clock": "date_only",
    }


def previous_intended_date(intended, day):
    if not intended:
        return None
    target = as_date(day)
    if target is None:
        return None
    lo, hi, found = 0, len(intended), None
    while lo < hi:
        mid = (lo + hi) // 2
        if intended[mid] < target:
            found = intended[mid]
            lo = mid + 1
        else:
            hi = mid
    return found


def population_window(observed):
    day = as_date(observed)
    if day is None:
        return "unknown_date"
    if day < PRIMARY_START:
        return "older_than_primary"
    if day > PRIMARY_END:
        return "after_primary_end"
    return "primary"


def stage_of(day):
    day = as_date(day)
    if day is None:
        return None
    for name, (start, end) in STAGE_BOUNDS.items():
        if start <= day < end:
            return name
    return None


def intended_universe(intended, *, year="all", stage="all"):
    selected = []
    for day in intended:
        if year != "all" and day.year != year:
            continue
        if stage != "all" and stage_of(day) != stage:
            continue
        selected.append(day)
    return tuple(selected)


def group_denominators(intended, year, stage, observed_dates):
    universe = intended_universe(intended, year=year, stage=stage)
    universe_set = set(universe)
    observed = {day for day in observed_dates if day in universe_set}
    return {"intended": len(universe), "observed": len(observed), "missing": len(universe) - len(observed)}


def nullable_int64(values):
    import pyarrow as pa
    return pa.array(list(values), type=pa.int64())


def resolve_levels(raw_values, *, conflict="conflict"):
    labeled = []
    for value in raw_values:
        if value is None or value == "":
            labeled.append(("missing", None))
            continue
        number = as_float(value)
        if number is None:
            labeled.append(("nonfinite", None))
        elif number <= 0:
            labeled.append(("nonpositive", number))
        else:
            labeled.append(("valid", number))
    valids = [number for status, number in labeled if status == "valid"]
    invalids = [status for status, _number in labeled if status != "valid"]
    if valids and invalids:
        return {
            "level": None, "disposition": "mixed_invalid_valid", "alias_count": 0, "usable": False,
            "conflict_values": sorted({number for status, number in labeled if number is not None}),
        }
    if not valids:
        reasons = {status for status, _number in labeled}
        disposition = next(iter(reasons)) if len(reasons) == 1 else "invalid"
        return {"level": None, "disposition": disposition, "alias_count": 0, "usable": False, "conflict_values": []}
    distinct = set(valids)
    if len(distinct) > 1:
        return {
            "level": None, "disposition": conflict, "alias_count": 0, "usable": False,
            "conflict_values": sorted(distinct),
        }
    return {
        "level": valids[0],
        "disposition": "alias" if len(valids) > 1 else "unique",
        "alias_count": len(valids),
        "usable": True,
        "conflict_values": [],
    }


def resolve_index_levels(rows, *, field="value"):
    return resolve_levels([row.get(field) for row in rows], conflict="conflict_symbol_date")


def equal_date_values(date_map):
    values = []
    for value in date_map.values():
        if type(value) is list:
            finite = [item for item in value if as_float(item) is not None]
            if finite:
                values.append(math.fsum(finite) / len(finite))
        else:
            number = as_float(value)
            if number is not None:
                values.append(number)
    return values


def event_values(date_map):
    values = []
    for value in date_map.values():
        if type(value) is list:
            values.extend(item for item in value if as_float(item) is not None)
        else:
            number = as_float(value)
            if number is not None:
                values.append(number)
    return values


def front_source_key(observed, family, source, root, basis, path, sha):
    return (observed, family, source, root, basis, path, sha)


def _point_from_row(row, basis):
    trade = as_date(row.get("trade_date") or row.get("observed_date"))
    expiration = as_date(row.get("contract_expiration"))
    duration = normalize_duration(row.get("duration_type"))
    level = as_float(row.get(basis))
    dte = calendar_dte(trade, expiration)
    return {
        "trade_date": trade,
        "expiration": expiration,
        "dte": dte,
        "level": level,
        "basis": basis,
        "duration_family": duration["family"],
        "duration_curve_key": duration_curve_key(row.get("duration_type")),
        "duration_type": duration["original"],
        "identity": contract_identity(row),
        "identity_record": identity_record(row),
        "contract_label": row.get("contract_label"),
        "product_display": row.get("product_display"),
        "root": row.get("root"),
        "source_path": row.get("source_path"),
        "source_sha256": row.get("source_sha256"),
        "source_field": row.get("source_field") or row.get("source"),
        "eligible_level": finite_positive(level),
        "expiration_after_trade": trade is not None and expiration is not None and expiration > trade,
        "expired_dte0": dte == 0,
    }


def collect_curve_points(rows, *, basis, duration_family=None):
    expired, ineligible, unknown, candidates = [], [], [], []
    for row in rows:
        point = _point_from_row(row, basis)
        if duration_family is not None and point["duration_curve_key"] != duration_family:
            continue
        if point["trade_date"] is None or point["expiration"] is None or point["dte"] is None:
            point["disposition"] = "unknown_date_or_domain"
            unknown.append(point)
            continue
        if point["expired_dte0"]:
            point["disposition"] = "expired_dte0"
            expired.append(point)
            continue
        if not point["eligible_level"] or not point["expiration_after_trade"]:
            raw = row.get(basis)
            if as_float(raw) is None and raw is not None:
                point["disposition"] = "nonfinite"
            elif as_float(raw) is not None and as_float(raw) <= 0:
                point["disposition"] = "nonpositive"
            else:
                point["disposition"] = "ineligible"
            ineligible.append(point)
            continue
        point["disposition"] = "candidate"
        candidates.append(point)
    return {"expired": expired, "ineligible": ineligible, "unknown": unknown, "candidates": candidates}


def rank_curve(candidates):
    identity_groups = defaultdict(list)
    for point in candidates:
        identity_groups[point["identity"]].append(point)
    identity_conflicts, remaining = [], []
    for points in identity_groups.values():
        levels = {point["level"] for point in points}
        if len(levels) > 1:
            for point in points:
                item = dict(point)
                item["disposition"] = "conflict_identity"
                identity_conflicts.append(item)
        else:
            remaining.extend(points)
    maturity_groups = defaultdict(list)
    for point in remaining:
        maturity_groups[point["expiration"]].append(point)
    maturity_conflicts, kept, aliases = [], [], []
    for expiration, points in maturity_groups.items():
        levels = {point["level"] for point in points}
        if len(levels) > 1:
            for point in points:
                item = dict(point)
                item["disposition"] = "conflict_maturity"
                maturity_conflicts.append(item)
            continue
        ordered = sorted(points, key=lambda point: (
            point["expiration"], point.get("contract_label") or "", point.get("product_display") or "",
            point["identity"],
        ))
        chosen = dict(ordered[0])
        chosen["alias_count"] = len(points)
        chosen["alias_identities"] = [point["identity_record"] for point in ordered]
        chosen["disposition"] = "ranked"
        kept.append(chosen)
        if len(points) > 1:
            aliases.append({
                "expiration": None if expiration is None else expiration.isoformat(),
                "level": chosen["level"],
                "alias_count": len(points),
                "identities": chosen["alias_identities"],
            })
    ranked = sorted(kept, key=lambda point: (
        point["dte"], point["expiration"], point.get("contract_label") or "",
        point.get("product_display") or "", point["identity"],
    ))
    for index, point in enumerate(ranked, start=1):
        point["rank"] = index
    return {
        "ranked": ranked,
        "identity_conflicts": identity_conflicts,
        "maturity_conflicts": maturity_conflicts,
        "aliases": aliases,
        "excluded_conflicts": identity_conflicts + maturity_conflicts,
    }


def front_second(ranked):
    empty = {
        "front_level": None, "second_level": None, "front_dte": None, "second_dte": None,
        "front_identity": None, "second_identity": None, "spread": None, "ratio_minus_one": None,
        "tenor_spacing": None, "structure": None, "disposition": "no_chain",
    }
    if not ranked:
        return dict(empty)
    front = ranked[0]
    result = dict(empty)
    result.update({
        "front_level": front["level"], "front_dte": front["dte"],
        "front_identity": front["identity_record"],
        "disposition": "front_only" if len(ranked) == 1 else "front_second",
    })
    if len(ranked) == 1:
        return result
    second = ranked[1]
    spread = second["level"] - front["level"]
    ratio = (second["level"] / front["level"]) - 1.0
    spacing = second["dte"] - front["dte"]
    structure = "contango" if ratio > 0 else ("backwardation" if ratio < 0 else "flat")
    result.update({
        "second_level": second["level"], "second_dte": second["dte"],
        "second_identity": second["identity_record"], "spread": spread,
        "ratio_minus_one": ratio, "tenor_spacing": spacing, "structure": structure,
    })
    return result


def curve_disposition(collected, ranked, conflicts):
    if ranked and conflicts:
        return "partial_curve"
    if ranked:
        return "observed"
    if conflicts:
        return "missing_front"
    if collected["candidates"] or collected["expired"] or collected["ineligible"] or collected["unknown"]:
        return "no_chain"
    return "no_chain"


def interpolate_constant_maturity(ranked, tenor):
    payload = {
        "tenor_dte": tenor, "price": None, "method": None, "weight_left": None, "weight_right": None,
        "left_dte": None, "right_dte": None, "left_price": None, "right_price": None,
        "left_identity": None, "right_identity": None, "missing_bracket_reason": None,
        "proxy": PROXY,
    }
    if type(tenor) is not int or tenor <= 0:
        payload["missing_bracket_reason"] = "invalid_tenor"
        return payload
    if not ranked:
        payload["missing_bracket_reason"] = "no_positive_curve"
        return payload
    exact = [point for point in ranked if point["dte"] == tenor]
    if exact:
        point = exact[0]
        payload.update({
            "price": point["level"], "method": "exact_observed", "weight_left": 1.0, "weight_right": 0.0,
            "left_dte": point["dte"], "right_dte": point["dte"], "left_price": point["level"],
            "right_price": point["level"], "left_identity": point["identity_record"],
            "right_identity": point["identity_record"],
        })
        return payload
    left = right = None
    for point in ranked:
        if point["dte"] < tenor:
            left = point
        elif point["dte"] > tenor and right is None:
            right = point
            break
    if left is None and right is None:
        payload["missing_bracket_reason"] = "missing_both"
        return payload
    if left is None:
        payload["missing_bracket_reason"] = "missing_left"
        return payload
    if right is None:
        payload["missing_bracket_reason"] = "missing_right"
        return payload
    span = right["dte"] - left["dte"]
    if span <= 0:
        payload["missing_bracket_reason"] = "nonpositive_bracket_span"
        return payload
    weight_right = (tenor - left["dte"]) / span
    weight_left = 1.0 - weight_right
    payload.update({
        "price": weight_left * left["level"] + weight_right * right["level"],
        "method": "linear_price", "weight_left": weight_left, "weight_right": weight_right,
        "left_dte": left["dte"], "right_dte": right["dte"],
        "left_price": left["level"], "right_price": right["level"],
        "left_identity": left["identity_record"], "right_identity": right["identity_record"],
    })
    return payload


def build_dated_curve(rows, *, basis="settlement", duration_family=None):
    collected = collect_curve_points(rows, basis=basis, duration_family=duration_family)
    ranking = rank_curve(collected["candidates"])
    ranked = ranking["ranked"]
    structure = front_second(ranked)
    interpolations = {tenor: interpolate_constant_maturity(ranked, tenor) for tenor in TENORS}
    disposition = curve_disposition(collected, ranked, ranking["excluded_conflicts"])
    if disposition == "missing_front":
        structure["front_level"] = None
        structure["disposition"] = "missing_front"
    elif disposition == "no_chain":
        structure["disposition"] = "no_chain"
    elif disposition == "partial_curve":
        structure["disposition"] = "partial_curve"
    return {
        "collected": collected,
        "ranking": ranking,
        "structure": structure,
        "interpolations": interpolations,
        "disposition": disposition,
        "basis": basis,
        "duration_family": duration_family,
    }


def contract_change(previous_level, current_level, previous_observed):
    if not previous_observed:
        return None
    previous = as_float(previous_level)
    current = as_float(current_level)
    if previous is None or current is None:
        return None
    return current - previous


def identity_change(current, previous):
    if previous is None:
        return {"change": None, "reason": "previous_missing", "previous_observed": False}
    if not current.get("usable") or not previous.get("usable"):
        return {"change": None, "reason": "conflict_or_invalid", "previous_observed": True}
    return {"change": current["level"] - previous["level"], "reason": None, "previous_observed": True}


def decompose_front_change(previous_front, current_front):
    if previous_front is None or current_front is None:
        return {"same_contract_change": None, "rank_roll_gap": None, "reason": "missing_front_or_previous"}
    if previous_front.get("usable") is False or current_front.get("usable") is False:
        return {"same_contract_change": None, "rank_roll_gap": None, "reason": "conflict_or_invalid"}
    prev_id, curr_id = previous_front.get("identity"), current_front.get("identity")
    prev_level, curr_level = as_float(previous_front.get("level")), as_float(current_front.get("level"))
    if prev_id is None or curr_id is None or prev_level is None or curr_level is None:
        return {"same_contract_change": None, "rank_roll_gap": None, "reason": "missing_front_or_previous"}
    if prev_id == curr_id:
        return {"same_contract_change": curr_level - prev_level, "rank_roll_gap": None, "reason": None}
    return {"same_contract_change": None, "rank_roll_gap": curr_level - prev_level, "reason": None}


def resolve_identity_levels(rows, *, basis):
    groups = defaultdict(list)
    for row in rows:
        day = as_date(row.get("trade_date") or row.get("observed_date_value") or row.get("observed_date"))
        if day is None:
            continue
        groups[(contract_identity(row), day, basis)].append(row)
    resolved = {}
    for key, group in groups.items():
        payload = resolve_levels([row.get(basis) for row in group], conflict="conflict_identity")
        sample = group[0]
        payload.update({
            "rows": group,
            "identity": key[0],
            "date": key[1],
            "basis": basis,
            "identity_record": identity_record(sample),
            "source_path": sample.get("source_path"),
            "source_sha256": sample.get("source_sha256"),
            "source": sample.get("source_field") or sample.get("source"),
            "root": sample.get("root") or "VX",
            "duration_curve_key": duration_curve_key(sample.get("duration_type")),
        })
        resolved[key] = payload
    return resolved


def build_identity_changes(rows, intended, *, basis="settlement"):
    resolved = resolve_identity_levels(rows, basis=basis)
    changes = []
    for (identity, day, _basis), current in resolved.items():
        previous_day = previous_intended_date(intended, day)
        previous = None if previous_day is None else resolved.get((identity, previous_day, basis))
        delta = identity_change(current, previous)
        changes.append({
            "date_value": day,
            "previous_intended_date": previous_day,
            "identity": identity,
            "identity_record": current["identity_record"],
            "current_level": current["level"],
            "previous_level": None if previous is None else previous["level"],
            "current_disposition": current["disposition"],
            "previous_disposition": None if previous is None else previous["disposition"],
            "alias_count": current["alias_count"],
            "same_contract_change": delta["change"],
            "change_reason": delta["reason"],
            "previous_observed": delta["previous_observed"],
            "usable_current": current["usable"],
            "usable_previous": False if previous is None else previous["usable"],
            "source_path": current["source_path"],
            "source_sha256": current["source_sha256"],
            "source": current["source"],
            "root": current["root"],
            "duration_curve_key": current["duration_curve_key"],
            "price_basis": basis,
        })
    return changes


def index_relationship(left, right):
    if not finite_positive(left) or not finite_positive(right):
        return {"difference": None, "ratio_minus_one": None, "missing": True}
    return {
        "difference": left - right,
        "ratio_minus_one": (left / right) - 1.0,
        "missing": False,
    }


def compare_source_values(primary, comparison):
    dates = sorted(set(primary) | set(comparison), key=lambda day: (day is None, day))
    equal = differ = only_primary = only_comparison = both_invalid = 0
    differences = []
    for day in dates:
        left, right = primary.get(day), comparison.get(day)
        left_ok, right_ok = finite_positive(left), finite_positive(right)
        if left_ok and right_ok:
            if left == right:
                equal += 1
            else:
                differ += 1
                differences.append({
                    "date": None if day is None else day.isoformat(),
                    "primary": left, "comparison": right, "difference": left - right,
                })
        elif left_ok:
            only_primary += 1
        elif right_ok:
            only_comparison += 1
        else:
            both_invalid += 1
    return {
        "union_dates": len(dates),
        "matched_valid_dates": equal + differ,
        "equal_values": equal,
        "different_values": differ,
        "only_primary_valid": only_primary,
        "only_comparison_valid": only_comparison,
        "both_invalid": both_invalid,
        "independent_primary_dates": len(independent_dates(primary)),
        "treat_as_independent": False,
        "combined_is_comparison_copy": True,
        "differences": differences,
    }


def independent_dates(*series):
    dates = set()
    for mapping in series:
        for day, value in mapping.items():
            if finite_positive(value) and day is not None:
                dates.add(day)
    return sorted(dates)


def distribution_summary(values, *, intended=0, observed=None, weighting="equal_date"):
    finite = [float(value) for value in values if as_float(value) is not None]
    observed_count = len(finite) if observed is None else observed
    return {
        "count": len(finite),
        "intended": intended,
        "observed": observed_count,
        "missing": None if not intended else intended - observed_count,
        "weighting": weighting,
        "quantiles": {str(level): None if not finite else quantile(finite, level) for level in QUANTILES},
    }


def source_role(path):
    name = Path(path).name
    if name == "all-contracts.parquet":
        return "vx"
    if name == "fred-volatility.parquet":
        return "fred_comparison"
    if name in PRIMARY_INDEX_FILES:
        return "primary_index"
    return "unexpected_source"


def _json_safe(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _read_json(store, ref):
    payload = store.read(artifact_ref({key: ref[key] for key in ("sha256", "size_bytes", "kind")}))
    return json.loads(payload)


def _read_admission(packet, protocol, root, store):
    predecessor = (packet.get("configuration") or {}).get("predecessor")
    if not isinstance(predecessor, dict) or not predecessor.get("path") or not predecessor.get("sha256"):
        raise IntegrityError("measure packet.configuration.predecessor must be the admission execution")
    path = Path(predecessor["path"])
    path = path if path.is_absolute() else Path(root) / path
    path = path.resolve()
    if (not path.is_relative_to(Path(root).resolve()) or "archive" in path.parts or not path.is_file()
            or path.stat().st_size > 64 * 1024 ** 2):
        raise IntegrityError("bounded retained admission execution required")
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != predecessor["sha256"]:
        raise IntegrityError("admission execution hash does not match packet.configuration.predecessor")
    if predecessor.get("size_bytes") is not None and len(raw) != predecessor["size_bytes"]:
        raise IntegrityError("admission execution size does not match packet.configuration.predecessor")
    execution = json.loads(raw)
    protocol_path = Path(root) / "validation" / "DAILY_VOLATILITY_COMPLEX_MEASUREMENT_V1.json"
    protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    if protocol_sha != packet.get("protocol_sha256"):
        raise IntegrityError("packet protocol_sha256 does not match the frozen protocol file")
    if (execution.get("success") is not True or execution.get("mode") != "admit"
            or execution.get("family") != protocol.get("family")):
        raise IntegrityError("predecessor is not a successful own admission execution")
    if (execution.get("protocol") or {}).get("sha256") != packet.get("protocol_sha256"):
        raise IntegrityError("admission execution protocol sha does not match the frozen protocol")
    worker_ref = execution.get("worker")
    if not isinstance(worker_ref, dict):
        raise IntegrityError("admission execution lacks a CAS worker reference")
    worker = _read_json(store, worker_ref)
    if (worker.get("success") is not True or worker.get("attempt_id") != execution.get("attempt_id")
            or worker.get("mode") != "admit" or worker.get("protocol_sha256") != packet.get("protocol_sha256")):
        raise IntegrityError("admission worker success, attempt_id, or protocol sha failed")
    actual_ref = worker.get("actual")
    required = ("kind", "sha256", "size_bytes")
    if not isinstance(actual_ref, dict) or any(key not in actual_ref for key in required):
        raise IntegrityError("admission worker.actual fields are incomplete")
    if actual_ref.get("kind") != "daily_volatility_admitted_sources_v1":
        raise IntegrityError("admission worker.actual is not daily_volatility_admitted_sources_v1")
    admitted = _read_json(store, actual_ref)
    sources = admitted.get("sources")
    if (admitted.get("kind") != "daily_volatility_admitted_sources_v1" or admitted.get("source_files") != 6
            or not isinstance(sources, list) or len(sources) != 6):
        raise IntegrityError("admitted metadata is not the six-source daily_volatility_admitted_sources_v1 record")
    protocol_sources = {(item["path"], item["size_bytes"]) for item in protocol["source_files"]}
    for record in sources:
        source = record.get("source") or {}
        raw_ref = record.get("raw") or {}
        if ((source.get("path"), source.get("size_bytes")) not in protocol_sources
                or any(key not in raw_ref for key in required)
                or raw_ref.get("kind") != "daily_volatility_original_source"
                or any(key not in record for key in ("rows", "columns", "schema", "sample"))):
            raise IntegrityError("admitted source metadata does not match the frozen protocol")
    return {
        "execution_path": str(path),
        "execution_sha256": sha,
        "attempt_id": execution["attempt_id"],
        "worker_ref": {key: worker_ref[key] for key in required},
        "actual_ref": {key: actual_ref[key] for key in required},
        "admitted": admitted,
        "protocol_sha256": protocol_sha,
    }


def _load_cash_calendar(root, reference):
    if not isinstance(reference, dict) or "path" not in reference:
        raise IntegrityError("cash_calendar path/sha256 reference required")
    path = Path(reference["path"])
    path = path if path.is_absolute() else Path(root) / path
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if reference.get("sha256") and sha != reference["sha256"]:
        raise IntegrityError("cash calendar bytes changed")
    if reference.get("size_bytes") is not None and len(raw) != reference["size_bytes"]:
        raise IntegrityError("cash calendar size changed")
    return CashCalendar(path), {"path": str(path), "sha256": sha, "size_bytes": len(raw)}


def intended_cash_dates(calendar, start, end):
    cut = local_timestamp(date(2026, 9, 4), time(0), calendar.zone)
    dates = []
    day = start
    while day <= end:
        if calendar.resolve(day, cut=cut).state != "closed":
            dates.append(day)
        day += timedelta(days=1)
    return tuple(dates)


def _decode_admitted_tables(store, admitted):
    import pyarrow.parquet as pq
    from pyarrow import BufferReader
    tables = []
    total = 0
    for record in admitted["sources"]:
        raw_ref = record["raw"]
        raw = store.read(artifact_ref({key: raw_ref[key] for key in ("sha256", "size_bytes", "kind")}))
        if hashlib.sha256(raw).hexdigest() != raw_ref["sha256"] or len(raw) != raw_ref["size_bytes"]:
            raise IntegrityError(f"admitted raw source bytes changed: {record['source']['path']}")
        total += len(raw)
        if total >= 1024 * 1024:
            raise IntegrityError("admitted daily-volatility sources exceeded the one-megabyte read bound")
        table = pq.read_table(BufferReader(raw))
        if record.get("rows") is not None and table.num_rows != record["rows"]:
            raise IntegrityError(f"admitted parquet row count changed: {record['source']['path']}")
        tables.append({
            "path": record["source"]["path"],
            "size_bytes": record["source"]["size_bytes"],
            "sha256": raw_ref["sha256"],
            "role": source_role(record["source"]["path"]),
            "rows": table.to_pylist(),
            "columns": list(table.column_names),
        })
    if len(tables) != 6:
        raise IntegrityError("each of the six admitted sources must be read exactly once")
    return tables, total


def _own_test_suite():
    path = Path(__file__).resolve().parents[3] / "tests" / "test_daily_volatility_complex.py"
    if not path.is_file():
        raise IntegrityError(f"own unit-test file is missing: {path}")
    spec = importlib.util.spec_from_file_location("test_daily_volatility_complex", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def run_own_unit_tests():
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(_own_test_suite())
    report = {
        "tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "passed": result.wasSuccessful(),
        "output": stream.getvalue(),
    }
    if not result.wasSuccessful():
        raise IntegrityError(
            "daily-volatility unit tests failed; stop without population or retry:\n" + stream.getvalue()
        )
    return report


def _pa_types():
    import pyarrow as pa
    return {
        "s": pa.string(), "f": pa.float64(), "i": pa.int64(), "b": pa.bool_(),
    }


def _schema(spec):
    types = _pa_types()
    return tuple((name, types[code]) for name, code in spec)


ACQUIRED_SCHEMA = (
    ("source_path", "s"), ("source_sha256", "s"), ("source_size_bytes", "i"), ("source_role", "s"),
    ("source_field", "s"), ("row_index", "i"), ("observed_date", "s"), ("population", "s"),
    ("on_intended_cash_date", "b"), ("known_at_ns", "i"), ("causal_feature_eligible", "b"),
    ("usable_as_known_feature", "b"), ("expected_next_publication", "s"),
    ("fred_realtime_start", "s"), ("fred_realtime_end", "s"), ("record_kind", "s"),
    ("root", "s"), ("contract_expiration", "s"), ("duration_type", "s"), ("duration_family", "s"),
    ("duration_curve_key", "s"), ("contract_label", "s"), ("product_display", "s"),
    ("open", "f"), ("high", "f"), ("low", "f"), ("close", "f"), ("settlement", "f"), ("change", "f"),
    ("total_volume", "i"), ("efp", "i"), ("open_interest", "i"), ("symbol", "s"),
    ("index_value", "f"), ("series_id", "s"), ("disposition", "s"),
)
CURVE_SCHEMA = (
    ("date", "s"), ("root", "s"), ("source", "s"), ("source_path", "s"), ("source_sha256", "s"),
    ("duration_family", "s"), ("price_basis", "s"), ("population", "s"), ("on_intended_cash_date", "b"),
    ("stage", "s"), ("year", "i"), ("disposition", "s"), ("ranked_count", "i"), ("alias_groups", "i"),
    ("identity_conflicts", "i"), ("maturity_conflicts", "i"), ("expired_dte0", "i"), ("ineligible", "i"),
    ("front_level", "f"), ("second_level", "f"), ("front_dte", "i"), ("second_dte", "i"),
    ("spread", "f"), ("ratio_minus_one", "f"), ("tenor_spacing", "i"), ("structure", "s"),
    ("front_identity", "s"), ("second_identity", "s"), ("alias_identities", "s"),
    ("maturity_conflict_identities", "s"), ("identity_conflict_identities", "s"),
    ("known_at_ns", "i"), ("causal_feature_eligible", "b"), ("proxy", "s"),
)
INTERP_SCHEMA = (
    ("date", "s"), ("root", "s"), ("source", "s"), ("source_path", "s"), ("source_sha256", "s"),
    ("duration_family", "s"), ("price_basis", "s"), ("population", "s"), ("stage", "s"), ("year", "i"),
    ("on_intended_cash_date", "b"), ("tenor_dte", "i"), ("price", "f"), ("method", "s"),
    ("weight_left", "f"), ("weight_right", "f"), ("left_dte", "i"), ("right_dte", "i"),
    ("left_price", "f"), ("right_price", "f"), ("left_identity", "s"), ("right_identity", "s"),
    ("missing_bracket_reason", "s"), ("curve_disposition", "s"), ("proxy", "s"),
    ("known_at_ns", "i"), ("causal_feature_eligible", "b"),
)
CHANGE_SCHEMA = (
    ("date", "s"), ("previous_intended_date", "s"), ("root", "s"), ("source", "s"),
    ("source_path", "s"), ("source_sha256", "s"), ("duration_family", "s"), ("price_basis", "s"),
    ("population", "s"), ("stage", "s"), ("year", "i"), ("identity", "s"),
    ("current_level", "f"), ("previous_level", "f"), ("current_disposition", "s"),
    ("previous_disposition", "s"), ("alias_count", "i"), ("usable_current", "b"),
    ("usable_previous", "b"), ("same_contract_change", "f"), ("change_reason", "s"),
    ("previous_observed", "b"), ("front_same_contract_change", "f"), ("front_rank_roll_gap", "f"),
    ("front_change_reason", "s"), ("front_partial_curve", "b"), ("gap_not_compressed", "b"),
    ("known_at_ns", "i"), ("causal_feature_eligible", "b"),
)
INDEX_OBS_SCHEMA = (
    ("family", "s"), ("source", "s"), ("symbol", "s"), ("date", "s"), ("population", "s"),
    ("stage", "s"), ("year", "i"), ("value", "f"), ("disposition", "s"), ("alias_count", "i"),
    ("conflict_values", "s"), ("source_lineage", "s"), ("vintages", "s"),
    ("known_at_ns", "i"), ("causal_feature_eligible", "b"),
)
INDEX_REL_SCHEMA = (
    ("family", "s"), ("source", "s"), ("date", "s"), ("population", "s"), ("stage", "s"), ("year", "i"),
    ("vix", "f"), ("vix3m", "f"), ("vxn", "f"), ("vvix", "f"),
    ("vix3m_minus_vix", "f"), ("vix3m_over_vix_minus_one", "f"),
    ("vxn_minus_vix", "f"), ("vxn_over_vix_minus_one", "f"), ("vvix_change", "f"), ("vix_change", "f"),
    ("missing_vix", "b"), ("missing_vix3m", "b"), ("missing_vxn", "b"), ("missing_vvix", "b"),
    ("no_forward_fill", "b"), ("source_lineage", "s"), ("vintages", "s"),
    ("known_at_ns", "i"), ("causal_feature_eligible", "b"),
)


def _write_parquet(outputs, name, rows, *, kind, schema_spec):
    import pyarrow as pa
    import pyarrow.parquet as pq
    schema = _schema(schema_spec)
    arrays = {}
    for column, typ in schema:
        values = [row.get(column) for row in rows]
        if column.endswith("_ns"):
            arrays[column] = nullable_int64(values)
            continue
        if pa.types.is_string(typ):
            coerced = []
            for value in values:
                if value is None:
                    coerced.append(None)
                elif type(value) is str:
                    coerced.append(value)
                else:
                    raise IntegrityError(f"{name}.{column} requires an explicit JSON string, not {type(value).__name__}")
            arrays[column] = pa.array(coerced, type=pa.string())
        elif pa.types.is_floating(typ):
            coerced = []
            for value in values:
                if value is None:
                    coerced.append(None)
                else:
                    number = as_float(value)
                    if number is None:
                        raise IntegrityError(f"{name}.{column} is not a finite float")
                    coerced.append(number)
            arrays[column] = pa.array(coerced, type=pa.float64())
        elif pa.types.is_integer(typ):
            coerced = []
            for value in values:
                if value is None or value is False:
                    if value is False:
                        raise IntegrityError(f"{name}.{column} boolean is not an int64 field")
                    coerced.append(None)
                elif isinstance(value, int) and not isinstance(value, bool):
                    coerced.append(int(value))
                else:
                    raise IntegrityError(f"{name}.{column} is not an int64 value")
            arrays[column] = pa.array(coerced, type=pa.int64())
        elif pa.types.is_boolean(typ):
            coerced = []
            for value in values:
                if value is None:
                    coerced.append(None)
                elif type(value) is bool:
                    coerced.append(value)
                else:
                    raise IntegrityError(f"{name}.{column} is not boolean")
            arrays[column] = pa.array(coerced, type=pa.bool_())
        else:
            raise IntegrityError(f"{name}.{column} has an unsupported parquet type")
    table = pa.table(arrays)
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="zstd", compression_level=3)
    with outputs.create(name) as stream:
        stream.write(buffer.getvalue())
    ref = outputs.reference(name, kind=kind)
    stored = pq.read_table(ref["path"]).cast(table.schema)
    if not stored.equals(table, check_metadata=False):
        raise IntegrityError(f"{name} failed parquet population round trip")
    for column, typ in schema:
        if column.endswith("_ns"):
            if stored.schema.field(column).type != pa.int64():
                raise IntegrityError(f"{name}.{column} lost nullable int64")
            if stored.column(column).null_count != table.column(column).null_count:
                raise IntegrityError(f"{name}.{column} null count changed")
    return {**ref, "rows": table.num_rows, "roundtrip_exact": True}


def _compact_statistics(summary):
    compact = {
        "schema": summary.get("schema"),
        "intended_date_count": summary.get("intended_date_count"),
        "configuration": summary.get("configuration"),
        "metrics": {},
    }
    for name, metric in summary.get("metrics", {}).items():
        bootstrap = dict(metric.get("bootstrap") or {})
        bootstrap.pop("replicate_estimates", None)
        compact["metrics"][name] = {
            "estimate": metric.get("estimate"),
            "actual_valid_date_count": metric.get("actual_valid_date_count"),
            "actual_valid_event_count": metric.get("actual_valid_event_count"),
            "valid_date_count": metric.get("valid_date_count"),
            "valid_event_count": metric.get("valid_event_count"),
            "missing_date_count": metric.get("missing_date_count"),
            "estimator": metric.get("estimator"),
            "support": metric.get("support"),
            "bootstrap": {
                "lower": bootstrap.get("lower"), "upper": bootstrap.get("upper"),
                "confidence": bootstrap.get("confidence"), "replicates": bootstrap.get("replicates"),
                "valid_replicates": bootstrap.get("valid_replicates"),
                "invalid_denominator_replicates": bootstrap.get("invalid_denominator_replicates"),
                "seed": bootstrap.get("seed"), "block_length": bootstrap.get("block_length"),
                "method": bootstrap.get("method"),
            },
        }
    return compact


def _put_metric(metrics, name, day, value, intended, *, events=False):
    number = as_float(value)
    if number is None or day not in intended:
        return
    bucket = metrics.setdefault(name, {})
    if events:
        current = bucket.get(day)
        if current is None:
            bucket[day] = [number]
        elif type(current) is list:
            current.append(number)
        else:
            bucket[day] = [current, number]
        return
    if day not in bucket:
        bucket[day] = number


def _metric_name(*parts):
    return "|".join("" if part is None else str(part) for part in parts)


def _stat_groups():
    groups = [("all", "all")]
    groups.extend((year, "all") for year in range(2020, 2027))
    groups.extend(("all", stage) for stage in STAGE_BOUNDS)
    return tuple(groups)


def _compile(tables, intended):
    intended_set = set(intended)
    acquired, vx_rows, index_rows = [], [], []
    duration_originals = Counter()
    for table in tables:
        for index, raw in enumerate(table["rows"]):
            clock = observation_clock(
                raw.get("trade_date") or raw.get("date"),
                raw.get("realtime_start"), raw.get("realtime_end"),
            )
            observed = clock["observed_date"]
            duration = normalize_duration(raw.get("duration_type")) if table["role"] == "vx" else {
                "family": None, "original": None,
            }
            if table["role"] == "vx":
                duration_originals[duration["original"]] += 1
            row = {
                "source_path": table["path"],
                "source_sha256": table["sha256"],
                "source_size_bytes": table["size_bytes"],
                "source_role": table["role"],
                "source_field": raw.get("source"),
                "row_index": index,
                "observed_date": None if observed is None else observed.isoformat(),
                "observed_date_value": observed,
                "population": population_window(observed),
                "on_intended_cash_date": observed in intended_set,
                "known_at_ns": None,
                "causal_feature_eligible": False,
                "usable_as_known_feature": False,
                "expected_next_publication": None,
                "fred_realtime_start": None if clock["fred_realtime_start"] is None else clock["fred_realtime_start"].isoformat(),
                "fred_realtime_end": None if clock["fred_realtime_end"] is None else clock["fred_realtime_end"].isoformat(),
                "duration_type": duration["original"],
                "duration_family": duration["family"],
                "duration_curve_key": duration_curve_key(raw.get("duration_type")) if table["role"] == "vx" else None,
            }
            if table["role"] == "vx":
                row.update({
                    "record_kind": "vx_contract",
                    "root": raw.get("root"),
                    "contract_expiration": None if as_date(raw.get("contract_expiration")) is None else as_date(raw.get("contract_expiration")).isoformat(),
                    "contract_label": raw.get("contract_label"),
                    "product_display": raw.get("product_display"),
                    "open": as_float(raw.get("open")), "high": as_float(raw.get("high")),
                    "low": as_float(raw.get("low")), "close": as_float(raw.get("close")),
                    "settlement": as_float(raw.get("settlement")), "change": as_float(raw.get("change")),
                    "total_volume": raw.get("total_volume"), "efp": raw.get("efp"),
                    "open_interest": raw.get("open_interest"),
                    "symbol": None, "index_value": None, "series_id": None,
                    "disposition": "acquired_vx",
                })
                vx_rows.append({
                    **row, **raw, "source_path": table["path"], "source_sha256": table["sha256"],
                    "source_field": raw.get("source"), "duration_family": duration["family"],
                    "duration_curve_key": row["duration_curve_key"],
                    "duration_type": duration["original"],
                })
            else:
                row.update({
                    "record_kind": "index", "root": None, "contract_expiration": None,
                    "contract_label": None, "product_display": None,
                    "open": None, "high": None, "low": None, "close": None, "settlement": None,
                    "change": None, "total_volume": None, "efp": None, "open_interest": None,
                    "symbol": raw.get("symbol"), "index_value": as_float(raw.get("value")),
                    "series_id": raw.get("series_id"), "disposition": "acquired_index",
                })
                index_rows.append({
                    "family": "fred_comparison" if table["role"] == "fred_comparison" else "primary_individual",
                    "source": raw.get("source"),
                    "symbol": raw.get("symbol"),
                    "date": observed,
                    "value": raw.get("value"),
                    "path": table["path"],
                    "sha256": table["sha256"],
                    "realtime_start": clock["fred_realtime_start"],
                    "realtime_end": clock["fred_realtime_end"],
                    "population": row["population"],
                    "file_name": Path(table["path"]).name,
                })
            acquired.append(row)
    return acquired, vx_rows, index_rows, duration_originals


def _vx_curves(vx_rows, intended):
    intended_set = set(intended)
    grouped = defaultdict(list)
    for row in vx_rows:
        observed = as_date(row.get("trade_date") or row.get("observed_date_value") or row.get("observed_date"))
        family = row.get("duration_curve_key") or duration_curve_key(row.get("duration_type"))
        if observed is None or family is None:
            continue
        grouped[(observed, family, row.get("source_field") or row.get("source"), row.get("root") or "VX",
                 row.get("source_path"), row.get("source_sha256"))].append(row)
    curves, interpolations, fronts = [], [], {}
    for (observed, family, source, root, path, sha), rows in grouped.items():
        for basis in PRICE_BASES:
            built = build_dated_curve(rows, basis=basis, duration_family=family)
            structure = built["structure"]
            ranking = built["ranking"]
            usable_front = built["disposition"] in {"observed", "partial_curve"} and structure["front_level"] is not None
            fronts[front_source_key(observed, family, source, root, basis, path, sha)] = None if not usable_front else {
                "identity": ranking["ranked"][0]["identity"],
                "level": ranking["ranked"][0]["level"],
                "usable": True,
                "partial_curve": built["disposition"] == "partial_curve",
                "disposition": built["disposition"],
            }
            curves.append({
                "date": observed.isoformat(), "date_value": observed, "root": root, "source": source,
                "source_path": path, "source_sha256": sha, "duration_family": family, "price_basis": basis,
                "population": population_window(observed), "on_intended_cash_date": observed in intended_set,
                "stage": stage_of(observed), "year": observed.year, "disposition": built["disposition"],
                "ranked_count": len(ranking["ranked"]), "alias_groups": len(ranking["aliases"]),
                "identity_conflicts": len(ranking["identity_conflicts"]),
                "maturity_conflicts": len(ranking["maturity_conflicts"]),
                "expired_dte0": len(built["collected"]["expired"]),
                "ineligible": len(built["collected"]["ineligible"]),
                "front_level": structure["front_level"], "second_level": structure["second_level"],
                "front_dte": structure["front_dte"], "second_dte": structure["second_dte"],
                "spread": structure["spread"], "ratio_minus_one": structure["ratio_minus_one"],
                "tenor_spacing": structure["tenor_spacing"], "structure": structure["structure"],
                "front_identity": encode_json(structure["front_identity"]),
                "second_identity": encode_json(structure["second_identity"]),
                "alias_identities": encode_json(ranking["aliases"]),
                "maturity_conflict_identities": encode_json([point["identity_record"] for point in ranking["maturity_conflicts"]]),
                "identity_conflict_identities": encode_json([point["identity_record"] for point in ranking["identity_conflicts"]]),
                "known_at_ns": None, "causal_feature_eligible": False, "proxy": PROXY,
            })
            for tenor, item in built["interpolations"].items():
                interpolations.append({
                    "date": observed.isoformat(), "date_value": observed, "root": root, "source": source,
                    "source_path": path, "source_sha256": sha, "duration_family": family, "price_basis": basis,
                    "population": population_window(observed), "stage": stage_of(observed), "year": observed.year,
                    "on_intended_cash_date": observed in intended_set, "tenor_dte": tenor,
                    "price": item["price"], "method": item["method"],
                    "weight_left": item["weight_left"], "weight_right": item["weight_right"],
                    "left_dte": item["left_dte"], "right_dte": item["right_dte"],
                    "left_price": item["left_price"], "right_price": item["right_price"],
                    "left_identity": encode_json(item["left_identity"]),
                    "right_identity": encode_json(item["right_identity"]),
                    "missing_bracket_reason": item["missing_bracket_reason"],
                    "curve_disposition": built["disposition"], "proxy": PROXY,
                    "known_at_ns": None, "causal_feature_eligible": False,
                })
    return curves, interpolations, fronts


def _vx_changes(vx_rows, intended, fronts):
    changes = []
    for basis in PRICE_BASES:
        for item in build_identity_changes(vx_rows, intended, basis=basis):
            day = item["date_value"]
            previous = item["previous_intended_date"]
            key = front_source_key(
                day, item["duration_curve_key"], item["source"], item["root"], basis,
                item["source_path"], item["source_sha256"],
            )
            prev_key = None if previous is None else front_source_key(
                previous, item["duration_curve_key"], item["source"], item["root"], basis,
                item["source_path"], item["source_sha256"],
            )
            current_front = fronts.get(key)
            previous_front = None if prev_key is None else fronts.get(prev_key)
            roll = decompose_front_change(previous_front, current_front)
            changes.append({
                "date": day.isoformat(), "date_value": day,
                "previous_intended_date": None if previous is None else previous.isoformat(),
                "root": item["root"], "source": item["source"],
                "source_path": item["source_path"], "source_sha256": item["source_sha256"],
                "duration_family": item["duration_curve_key"], "price_basis": basis,
                "population": population_window(day), "stage": stage_of(day), "year": day.year,
                "identity": encode_json(item["identity_record"]),
                "current_level": item["current_level"], "previous_level": item["previous_level"],
                "current_disposition": item["current_disposition"],
                "previous_disposition": item["previous_disposition"],
                "alias_count": item["alias_count"],
                "usable_current": item["usable_current"], "usable_previous": item["usable_previous"],
                "same_contract_change": item["same_contract_change"],
                "change_reason": item["change_reason"],
                "previous_observed": item["previous_observed"],
                "front_same_contract_change": roll["same_contract_change"],
                "front_rank_roll_gap": roll["rank_roll_gap"],
                "front_change_reason": roll["reason"],
                "front_partial_curve": bool((current_front or {}).get("partial_curve") or (previous_front or {}).get("partial_curve")),
                "gap_not_compressed": item["same_contract_change"] is None,
                "known_at_ns": None, "causal_feature_eligible": False,
            })
    return changes


def _index_ref(row):
    return {
        "path": row.get("path"),
        "sha256": row.get("sha256"),
        "source": row.get("source"),
        "file_name": row.get("file_name"),
        "realtime_start": None if row.get("realtime_start") is None else row["realtime_start"].isoformat(),
        "realtime_end": None if row.get("realtime_end") is None else row["realtime_end"].isoformat(),
    }


def _index_tables(index_rows, intended):
    grouped = defaultdict(list)
    for row in index_rows:
        grouped[(row["family"], row["source"], row["symbol"], row["date"])].append(row)
    observations, conflicts, values = [], [], {}
    for key, rows in grouped.items():
        family, source, symbol, day = key
        resolved = resolve_index_levels(rows)
        vintages = sorted({
            (None if row.get("realtime_start") is None else row["realtime_start"].isoformat(),
             None if row.get("realtime_end") is None else row["realtime_end"].isoformat())
            for row in rows
        })
        lineage = [_index_ref(row) for row in rows]
        record = {
            "family": family, "source": source, "symbol": symbol,
            "date": None if day is None else day.isoformat(), "date_value": day,
            "population": population_window(day), "stage": stage_of(day),
            "year": None if day is None else day.year,
            "value": resolved["level"], "disposition": resolved["disposition"],
            "alias_count": resolved["alias_count"],
            "conflict_values": encode_json(resolved.get("conflict_values") or None),
            "source_lineage": encode_json(lineage),
            "vintages": encode_json([{"realtime_start": start, "realtime_end": end} for start, end in vintages]),
            "known_at_ns": None, "causal_feature_eligible": False,
        }
        if not resolved["usable"]:
            conflicts.append(record)
        else:
            values[(family, source, symbol, day)] = {
                "value": resolved["level"], "lineage": lineage, "vintages": vintages,
            }
        observations.append(record)
    relations = []
    groups = {(family, source) for family, source, _symbol, _day in values}
    for family, source in groups:
        dates = {day for item_family, item_source, _symbol, day in values
                 if item_family == family and item_source == source and day is not None}
        for day in dates:
            cells = {symbol: values.get((family, source, symbol, day)) for symbol in INDEX_SYMBOLS}
            levels = {symbol: None if cell is None else cell["value"] for symbol, cell in cells.items()}
            previous = previous_intended_date(intended, day)
            prev_vvix = None if previous is None else values.get((family, source, "VVIX", previous))
            prev_vix = None if previous is None else values.get((family, source, "VIX", previous))
            vix3m = index_relationship(levels["VIX3M"], levels["VIX"])
            vxn = index_relationship(levels["VXN"], levels["VIX"])
            lineage, vintages = [], []
            for cell in cells.values():
                if cell is None:
                    continue
                lineage.extend(cell["lineage"])
                vintages.extend(cell["vintages"])
            relations.append({
                "family": family, "source": source,
                "date": day.isoformat(), "date_value": day,
                "population": population_window(day), "stage": stage_of(day), "year": day.year,
                "vix": levels["VIX"], "vix3m": levels["VIX3M"], "vxn": levels["VXN"], "vvix": levels["VVIX"],
                "vix3m_minus_vix": vix3m["difference"],
                "vix3m_over_vix_minus_one": vix3m["ratio_minus_one"],
                "vxn_minus_vix": vxn["difference"],
                "vxn_over_vix_minus_one": vxn["ratio_minus_one"],
                "vvix_change": (
                    None if prev_vvix is None or levels["VVIX"] is None
                    else identity_change({"usable": True, "level": levels["VVIX"]},
                                         {"usable": True, "level": prev_vvix["value"]})["change"]
                ),
                "vix_change": (
                    None if prev_vix is None or levels["VIX"] is None
                    else identity_change({"usable": True, "level": levels["VIX"]},
                                         {"usable": True, "level": prev_vix["value"]})["change"]
                ),
                "missing_vix": levels["VIX"] is None, "missing_vix3m": levels["VIX3M"] is None,
                "missing_vxn": levels["VXN"] is None, "missing_vvix": levels["VVIX"] is None,
                "no_forward_fill": True,
                "source_lineage": encode_json(lineage),
                "vintages": encode_json([{"realtime_start": start, "realtime_end": end} for start, end in sorted(set(vintages))]),
                "known_at_ns": None, "causal_feature_eligible": False,
            })
    primary, comparison = defaultdict(dict), defaultdict(dict)
    for (family, _source, symbol, day), cell in values.items():
        if family == "primary_individual":
            primary[symbol][day] = cell["value"]
        elif family == "fred_comparison":
            comparison[symbol][day] = cell["value"]
    comparisons = {}
    for symbol in INDEX_SYMBOLS:
        comparisons[symbol] = compare_source_values(primary[symbol], comparison[symbol])
        comparisons[symbol]["independent_dates_not_doubled"] = len(independent_dates(primary[symbol], comparison[symbol]))
        comparisons[symbol]["not_independent_history"] = symbol != "VVIX"
        comparisons[symbol]["individual_publisher"] = "Cboe" if symbol == "VVIX" else "FRED"
    return observations, relations, conflicts, comparisons, values


def _known_curve(row):
    return row.get("duration_family") in KNOWN_CURVE_FAMILIES


def _statistics(curves, interpolations, changes, relations, intended):
    groups = {}
    for year, stage in _stat_groups():
        universe = intended_universe(intended, year=year, stage=stage)
        universe_set = set(universe)
        metrics = {}
        for curve in curves:
            if curve["population"] != "primary" or not curve["on_intended_cash_date"] or not _known_curve(curve):
                continue
            day = curve["date_value"]
            prefix = (curve["root"], curve["source"], curve["source_path"], curve["duration_family"], curve["price_basis"])
            for name in ("front_level", "second_level", "spread", "ratio_minus_one", "tenor_spacing"):
                _put_metric(metrics, _metric_name("vx", *prefix, name), day, curve[name], universe_set)
        for item in interpolations:
            if item["population"] != "primary" or not item["on_intended_cash_date"] or not _known_curve(item):
                continue
            _put_metric(
                metrics,
                _metric_name("vx", item["root"], item["source"], item["source_path"], item["duration_family"],
                             item["price_basis"], f"interp_{item['tenor_dte']}"),
                item["date_value"], item["price"], universe_set,
            )
        front_keys = set()
        for item in changes:
            if item["population"] != "primary" or not _known_curve(item):
                continue
            day = item["date_value"]
            prefix = (item["root"], item["source"], item["source_path"], item["duration_family"], item["price_basis"])
            _put_metric(metrics, _metric_name("vx", *prefix, "same_contract_change"), day,
                        item["same_contract_change"], universe_set, events=True)
            front_key = (day, *prefix)
            if front_key in front_keys:
                continue
            front_keys.add(front_key)
            _put_metric(metrics, _metric_name("vx", *prefix, "front_same_contract_change"),
                        day, item["front_same_contract_change"], universe_set)
            _put_metric(metrics, _metric_name("vx", *prefix, "front_rank_roll_gap"),
                        day, item["front_rank_roll_gap"], universe_set)
        for item in relations:
            if item["population"] != "primary":
                continue
            prefix = (item["family"], item["source"])
            for name in ("vix", "vix3m", "vxn", "vvix", "vix3m_minus_vix", "vix3m_over_vix_minus_one",
                         "vxn_minus_vix", "vxn_over_vix_minus_one", "vvix_change"):
                _put_metric(metrics, _metric_name("index", *prefix, name), item["date_value"], item[name], universe_set)
        label = f"year={year}|stage={stage}"
        if not metrics or not universe:
            groups[label] = {"metrics": {}, "intended_date_count": len(universe), "empty": True}
            continue
        summary = observed_date_statistics(
            metrics, universe, estimator="date_mean", seed=STAT_SEED, block_length=STAT_BLOCK,
            replicates=STAT_REPS, confidence=STAT_CONFIDENCE, minimum_independent_dates=STAT_MIN_DATES,
            minimum_events=STAT_MIN_EVENTS, include_weights=False, _retain_replicate_estimates=False,
        )
        groups[label] = _compact_statistics(summary)
    return {"kind": "daily_volatility_date_statistics_v1", "groups": groups}


def _dedup_front_changes(changes):
    seen, rows = set(), []
    for item in changes:
        key = (item["date"], item["root"], item["source"], item["source_path"], item["source_sha256"],
               item["duration_family"], item["price_basis"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(item)
    return rows


def _add_dist(store, name, date_map, intended, year, stage, *, event_map=None):
    den = group_denominators(intended, year, stage, date_map)
    store[name] = distribution_summary(
        equal_date_values(date_map), intended=den["intended"], observed=den["observed"], weighting="equal_date",
    )
    store[name]["denominators"] = den
    if event_map is not None:
        store[name + "|event_weighted"] = distribution_summary(
            event_values(event_map), intended=den["intended"], observed=den["observed"], weighting="event",
        )


def _distributions(curves, interpolations, changes, relations, intended):
    store = {}
    front_changes = _dedup_front_changes(changes)
    for year, stage in _stat_groups():
        universe = set(intended_universe(intended, year=year, stage=stage))
        curve_maps, interp_maps, change_maps, front_maps, index_maps = (
            defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict),
        )
        for curve in curves:
            if (curve["population"] != "primary" or not curve["on_intended_cash_date"]
                    or not _known_curve(curve) or curve["date_value"] not in universe):
                continue
            prefix = _metric_name(
                "vx", curve["source"], curve["source_path"], curve["duration_family"],
                curve["price_basis"], year, stage,
            )
            for field in ("front_level", "second_level", "spread", "ratio_minus_one"):
                if as_float(curve[field]) is not None:
                    curve_maps[(prefix, field)][curve["date_value"]] = curve[field]
        for item in interpolations:
            if (item["population"] != "primary" or not item["on_intended_cash_date"]
                    or not _known_curve(item) or item["date_value"] not in universe):
                continue
            prefix = _metric_name(
                "vx", item["source"], item["source_path"], item["duration_family"],
                item["price_basis"], year, stage, f"tenor_{item['tenor_dte']}",
            )
            if as_float(item["price"]) is not None:
                interp_maps[(prefix, "interp")][item["date_value"]] = item["price"]
        for item in changes:
            if item["population"] != "primary" or not _known_curve(item) or item["date_value"] not in universe:
                continue
            prefix = _metric_name(
                "vx", item["source"], item["source_path"], item["duration_family"],
                item["price_basis"], year, stage,
            )
            if as_float(item["same_contract_change"]) is not None:
                change_maps[(prefix, "same_contract_change")].setdefault(item["date_value"], []).append(
                    item["same_contract_change"]
                )
        for item in front_changes:
            if item["population"] != "primary" or not _known_curve(item) or item["date_value"] not in universe:
                continue
            prefix = _metric_name(
                "vx", item["source"], item["source_path"], item["duration_family"],
                item["price_basis"], year, stage,
            )
            if as_float(item["front_rank_roll_gap"]) is not None:
                front_maps[(prefix, "front_rank_roll_gap")][item["date_value"]] = item["front_rank_roll_gap"]
            if as_float(item["front_same_contract_change"]) is not None:
                front_maps[(prefix, "front_same_contract_change")][item["date_value"]] = item["front_same_contract_change"]
        for item in relations:
            if item["population"] != "primary" or item["date_value"] not in universe:
                continue
            prefix = _metric_name("index", item["family"], item["source"], year, stage)
            for field in ("vix", "vix3m", "vxn", "vvix", "vix3m_over_vix_minus_one",
                          "vxn_over_vix_minus_one", "vvix_change"):
                if as_float(item[field]) is not None:
                    index_maps[(prefix, field)][item["date_value"]] = item[field]
        for (prefix, field), date_map in curve_maps.items():
            _add_dist(store, prefix + "|" + field, date_map, intended, year, stage)
        for (prefix, field), date_map in interp_maps.items():
            _add_dist(store, prefix + "|" + field, date_map, intended, year, stage)
        for (prefix, field), date_map in change_maps.items():
            _add_dist(store, prefix + "|" + field, date_map, intended, year, stage, event_map=date_map)
        for (prefix, field), date_map in front_maps.items():
            _add_dist(store, prefix + "|" + field, date_map, intended, year, stage)
        for (prefix, field), date_map in index_maps.items():
            _add_dist(store, prefix + "|" + field, date_map, intended, year, stage)
    return store


def _counts(acquired, curves, interpolations, changes, observations, relations, conflicts, comparisons,
            duration_originals, intended, source_bytes):
    populations = Counter(row["population"] for row in acquired)
    roles = Counter(row["source_role"] for row in acquired)
    curve_disp = Counter(row["disposition"] for row in curves)
    interp_missing = Counter(row["missing_bracket_reason"] or "observed" for row in interpolations)
    change_disp = Counter(row["current_disposition"] for row in changes)
    index_disp = Counter(row["disposition"] for row in observations)
    return {
        "acquired_rows": len(acquired),
        "acquired_by_population": dict(populations),
        "acquired_by_role": dict(roles),
        "older_than_primary": populations["older_than_primary"],
        "after_primary_end": populations["after_primary_end"],
        "primary_rows": populations["primary"],
        "outside_intended_cash_date": sum(1 for row in acquired if not row["on_intended_cash_date"]),
        "intended_cash_dates": len(intended),
        "duration_original_labels": dict(duration_originals),
        "unexpected_duration_curve_keys": sorted({
            row["duration_family"] for row in curves if row["duration_family"] not in KNOWN_CURVE_FAMILIES
        }),
        "curves": len(curves),
        "curve_dispositions": dict(curve_disp),
        "interpolations": len(interpolations),
        "interpolation_reasons": dict(interp_missing),
        "changes": len(changes),
        "change_dispositions": dict(change_disp),
        "change_gaps": sum(1 for row in changes if row["gap_not_compressed"]),
        "index_observations": len(observations),
        "index_dispositions": dict(index_disp),
        "index_conflicts": len(conflicts),
        "index_relations": len(relations),
        "source_comparisons": {symbol: {key: value for key, value in payload.items() if key != "differences"}
                               for symbol, payload in comparisons.items()},
        "index_source_facts": INDEX_SOURCE_FACTS,
        "source_bytes_read": source_bytes,
        "prior_history_used_as_primary_support": False,
        "official_vix_or_vvix_replicated": False,
        "nq_es_joined": False,
        "combined_fred_independent_history": False,
    }


def _md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join("" if cell is None else str(cell) for cell in row) + " |")
    return lines


def _fmt(value, digits=4):
    number = as_float(value)
    if number is None:
        return ""
    return f"{number:.{digits}g}"


def _stat_cells(groups, group, metric):
    payload = ((groups.get(group) or {}).get("metrics") or {}).get(metric) or {}
    bootstrap = payload.get("bootstrap") or {}
    support = payload.get("support") or {}
    return [
        _fmt(payload.get("estimate")), _fmt(bootstrap.get("lower")), _fmt(bootstrap.get("upper")),
        payload.get("actual_valid_date_count"), payload.get("missing_date_count"),
        support.get("independent_dates"), support.get("sparse"),
    ]


def _pick_metric(groups, group, suffix):
    metrics = ((groups.get(group) or {}).get("metrics") or {})
    matches = [name for name in metrics if name.endswith("|" + suffix)]
    if not matches:
        return None
    for name in matches:
        if suffix == "vvix" and "Cboe" in name:
            return name
        if suffix != "vvix" and "monthly" in name and "settlement" in name:
            return name
        if suffix != "vvix" and name.startswith("index|") and "FRED" in name:
            return name
    return matches[0]


def _write_report(outputs, *, admission, calendar_ref, counts, distributions, comparisons, statistics, tests, refs):
    groups = statistics.get("groups") or {}
    primary = f"{PRIMARY_START.isoformat()} through {PRIMARY_END.isoformat()}"
    comparison_rows = []
    for symbol, payload in comparisons.items():
        comparison_rows.append([
            symbol, payload.get("individual_publisher"), payload.get("matched_valid_dates"),
            payload.get("equal_values"), payload.get("different_values"),
            payload.get("independent_primary_dates"), payload.get("not_independent_history"),
        ])
    highlight = [
        ("front_level", "front"),
        ("spread", "spread F2-F1"),
        ("ratio_minus_one", "ratio F2/F1-1"),
        ("interp_30", "F30 price"),
        ("interp_60", "F60 price"),
        ("interp_90", "F90 price"),
    ]
    all_rows, stage_rows = [], []
    for suffix, label in highlight:
        metric = _pick_metric(groups, "year=all|stage=all", suffix)
        if metric is None:
            continue
        all_rows.append([label, * _stat_cells(groups, "year=all|stage=all", metric)])
        for stage in STAGE_BOUNDS:
            stage_metric = _pick_metric(groups, f"year=all|stage={stage}", suffix)
            if stage_metric is None:
                continue
            stage_rows.append([stage, label, * _stat_cells(groups, f"year=all|stage={stage}", stage_metric)])
    index_rows = []
    for suffix, label in (
        ("vix", "VIX"), ("vix3m_over_vix_minus_one", "VIX3M/VIX-1"),
        ("vxn_over_vix_minus_one", "VXN/VIX-1"), ("vvix", "VVIX"),
    ):
        metric = _pick_metric(groups, "year=all|stage=all", suffix)
        if metric is None:
            continue
        index_rows.append([label, * _stat_cells(groups, "year=all|stage=all", metric)])
    dist_rows = []
    for name, payload in sorted(distributions.items()):
        if "|event_weighted" in name or "|all|all|" not in name:
            continue
        if any(part in name for part in ("front_level", "spread", "interp", "vix3m_over_vix", "vvix")):
            quantiles = payload.get("quantiles") or {}
            den = payload.get("denominators") or {}
            dist_rows.append([
                name, payload.get("weighting"), den.get("intended"), den.get("observed"), den.get("missing"),
                _fmt(quantiles.get("0.5")), _fmt(quantiles.get("0.05")), _fmt(quantiles.get("0.95")),
            ])
    lines = [
        "# Daily VX/VIX complex measurement",
        "",
        "This is the acquired daily branch only. It does not complete C16, does not replicate official VIX or VVIX,",
        "does not interpolate variance, and does not fit Context or join NQ/ES.",
        "",
        "## Definitions and units",
        "",
        "- VX levels are futures prices in index points on the chosen price basis (`settlement` or `close`).",
        "- DTE is calendar days `contract_expiration - trade_date`. Expiry-day DTE 0 is retained and excluded from the positive-time curve.",
        "- Front/second rank distinct positive DTE within one duration-curve key. Spread is F2-F1. Ratio is F2/F1-1.",
        "- A maturity-price conflict does not silently promote a remaining contract to front unless the curve is marked `partial_curve`.",
        "- Constant 30/60/90 DTE values are linear **price** interpolation between nearest same-duration brackets, or the exact observed tenor.",
        "- Same-contract changes require a unique finite positive level on both the current and previous intended cash date. Conflicts/nonpositive/nonfinite block the change.",
        "- Index units are published index points and require finite positive levels. Combined FRED is a comparison copy.",
        "",
        "## Clocks",
        "",
        "- Every row is date-only: `known_at_ns` is null and `causal_feature_eligible` is false.",
        "- FRED `realtime_start` / `realtime_end` vintages are retained in lineage; they are not pre-event availability.",
        "- Expected next publication is unknown.",
        "",
        "## Source identities",
        "",
        "- Individual `VIX.parquet`, `VIX3M.parquet`, and `VXN.parquet` are FRED series, not independent Cboe histories.",
        "- Those individual FRED files share the admitted 2026-09-03 `realtime_start` / `realtime_end` vintage with `fred-volatility.parquet`.",
        "- `VVIX.parquet` is Cboe. Combined FRED is a comparison copy and does not add independent date support.",
        "",
        "## Coverage",
        "",
        f"- Primary population: {primary}. Older acquired rows are counted and excluded from primary support.",
        f"- Intended cash dates: {counts['intended_cash_dates']}.",
        f"- Acquired rows: {counts['acquired_rows']} (primary {counts['primary_rows']}, older {counts['older_than_primary']}, after {counts['after_primary_end']}, outside intended cash {counts['outside_intended_cash_date']}).",
        f"- Duration labels retained as observed: {counts['duration_original_labels']}. Unexpected originals stay on separate curve keys: {counts['unexpected_duration_curve_keys']}.",
        "",
        "## Individual vs combined FRED comparison",
        "",
        "- Exact same-symbol/date comparison only. No merge or winner. Aliases do not add independent dates.",
        "",
        * _md_table(
            ["symbol", "individual_publisher", "matched_valid", "equal", "different", "primary_dates", "not_independent"],
            comparison_rows,
        ),
        "",
        "## Date-mean and 95% block CI (all-period intended universe)",
        "",
        * _md_table(
            ["metric", "mean", "ci_low", "ci_high", "valid_dates", "missing_dates", "support_dates", "sparse"],
            all_rows,
        ),
        "",
        "## Chronological stages (training / development / confirmation)",
        "",
        "Each stage uses only that stage's intended cash dates as the denominator.",
        "",
        * _md_table(
            ["stage", "metric", "mean", "ci_low", "ci_high", "valid_dates", "missing_dates", "support_dates", "sparse"],
            stage_rows,
        ),
        "",
        "## Index levels and ratios (all-period, not pooled across publishers)",
        "",
        * _md_table(
            ["metric", "mean", "ci_low", "ci_high", "valid_dates", "missing_dates", "support_dates", "sparse"],
            index_rows,
        ),
        "",
        "## Equal-date distributions (all-period groups, not pooled aliases)",
        "",
        * _md_table(
            ["group", "weighting", "intended", "observed", "missing", "median", "q05", "q95"],
            dist_rows[:40],
        ),
        "",
        "## Counts and retained raw dispositions",
        "",
        f"- Curves: {counts['curves']} dispositions {counts['curve_dispositions']}",
        f"- Interpolations: {counts['interpolations']} reasons {counts['interpolation_reasons']}",
        f"- Contract changes: {counts['changes']} dispositions {counts['change_dispositions']} gaps {counts['change_gaps']}",
        f"- Index observations: {counts['index_observations']} dispositions {counts['index_dispositions']} unused/conflict {counts['index_conflicts']}",
        f"- Index relations: {counts['index_relations']}",
        f"- Unit tests: {tests['tests']} passed={tests['passed']}",
        "",
        "Full grouped date-mean/CI tables and per-group distributions are in `date-statistics.json` and `distributions.json`.",
        "",
        "## Exact result paths",
        "",
    ]
    for name, ref in refs.items():
        lines.append(f"- {name}: `{ref.get('path')}` sha256={ref.get('sha256')} bytes={ref.get('size_bytes')}")
    lines.extend([
        "",
        f"- Admission execution: `{admission['execution_path']}` sha256={admission['execution_sha256']}",
        f"- Cash calendar: `{calendar_ref['path']}` sha256={calendar_ref['sha256']}",
        "",
        "## Family status",
        "",
        "- `family_complete` is false. This file reports the acquired daily measurement branch after actual data, not the full C16 parent.",
        "",
    ])
    payload = ("\n".join(lines) + "\n").encode()
    with outputs.create("results.md") as stream:
        stream.write(payload)
    return outputs.reference("results.md", kind="daily_volatility_results_report_v1")


def run(*, packet, protocol, root, store):
    if not isinstance(packet, dict) or not isinstance(protocol, dict):
        raise ContractError("run requires packet and protocol mappings")
    tests = run_own_unit_tests()
    admission = _read_admission(packet, protocol, root, store)
    tables, source_bytes = _decode_admitted_tables(store, admission["admitted"])
    calendar, calendar_ref = _load_cash_calendar(root, protocol.get("cash_calendar"))
    intended = intended_cash_dates(calendar, PRIMARY_START, PRIMARY_END)
    acquired, vx_rows, index_rows, duration_originals = _compile(tables, intended)
    curves, interpolations, fronts = _vx_curves(vx_rows, intended)
    changes = _vx_changes(vx_rows, intended, fronts)
    observations, relations, conflicts, comparisons, _values = _index_tables(index_rows, intended)
    counts = _counts(
        acquired, curves, interpolations, changes, observations, relations, conflicts,
        comparisons, duration_originals, intended, source_bytes,
    )
    distributions = _distributions(curves, interpolations, changes, relations, intended)
    statistics = _statistics(curves, interpolations, changes, relations, intended)
    run_folder = Path(root) / "reports" / "daily-volatility-runs" / packet["attempt_id"]
    outputs = BoundedOutputs(
        run_folder / "outputs",
        maximum_total_bytes=128 * 1024 ** 2 - 16 * 1024 ** 2,
        maximum_file_bytes=128 * 1024 ** 2 - 16 * 1024 ** 2,
    )
    drop_runtime = ("observed_date_value", "date_value")
    acquired_out = [{key: value for key, value in row.items() if key not in drop_runtime} for row in acquired]
    curve_out = [{key: value for key, value in row.items() if key not in drop_runtime} for row in curves]
    interp_out = [{key: value for key, value in row.items() if key not in drop_runtime} for row in interpolations]
    change_out = [{key: value for key, value in row.items() if key not in drop_runtime} for row in changes]
    observation_out = [{key: value for key, value in row.items() if key not in drop_runtime} for row in observations]
    relation_out = [{key: value for key, value in row.items() if key not in drop_runtime} for row in relations]
    refs = {
        "acquired_rows": _write_parquet(outputs, "acquired-rows.parquet", acquired_out,
                                       kind="daily_volatility_acquired_rows_v1", schema_spec=ACQUIRED_SCHEMA),
        "vx_curves": _write_parquet(outputs, "vx-curves.parquet", curve_out,
                                   kind="daily_volatility_vx_curves_v1", schema_spec=CURVE_SCHEMA),
        "vx_interpolations": _write_parquet(outputs, "vx-interpolations.parquet", interp_out,
                                            kind="daily_volatility_vx_interpolations_v1", schema_spec=INTERP_SCHEMA),
        "vx_changes": _write_parquet(outputs, "vx-changes.parquet", change_out,
                                     kind="daily_volatility_vx_changes_v1", schema_spec=CHANGE_SCHEMA),
        "index_observations": _write_parquet(outputs, "index-observations.parquet", observation_out,
                                             kind="daily_volatility_index_observations_v1", schema_spec=INDEX_OBS_SCHEMA),
        "index_relations": _write_parquet(outputs, "index-relations.parquet", relation_out,
                                          kind="daily_volatility_index_relations_v1", schema_spec=INDEX_REL_SCHEMA),
        "population_counts": outputs.json("population-counts.json", _json_safe(counts), kind="daily_volatility_population_counts_v1"),
        "source_comparison": outputs.json("source-comparison.json", _json_safe(comparisons), kind="daily_volatility_source_comparison_v1"),
        "distributions": outputs.json("distributions.json", _json_safe(distributions), kind="daily_volatility_distributions_v1"),
        "date_statistics": outputs.json("date-statistics.json", _json_safe(statistics), kind="daily_volatility_date_statistics_v1"),
    }
    refs["results_md"] = _write_report(
        outputs, admission=admission, calendar_ref=calendar_ref, counts=counts,
        distributions=distributions, comparisons=comparisons, statistics=statistics, tests=tests, refs=refs,
    )
    return {
        "kind": "daily_volatility_measurement_results_v1",
        "version": VERSION,
        "success": True,
        "output_bytes": outputs.written,
        "refs": refs,
        "counts": counts,
        "tests": {key: tests[key] for key in ("tests", "failures", "errors", "skipped", "passed", "output")},
        "resources": {
            "source_bytes_read": source_bytes,
            "sources_read": 6,
            "output_bytes": outputs.written,
            "intended_cash_dates": len(intended),
            "bootstrap": {
                "seed": STAT_SEED, "block_length": STAT_BLOCK, "replicates": STAT_REPS,
                "confidence": STAT_CONFIDENCE, "minimum_dates": STAT_MIN_DATES, "minimum_events": STAT_MIN_EVENTS,
                "estimator": "date_mean",
            },
        },
        "family_complete": False,
        "full_family_complete": False,
        "context_models_complete": False,
        "model_fits": 0,
        "admission": {key: admission[key] for key in (
            "execution_path", "execution_sha256", "attempt_id", "worker_ref", "actual_ref", "protocol_sha256",
        )},
        "cash_calendar": calendar_ref,
        "scope": "Acquired daily VX/VIX complex measurement for C16.VX_CURVE/C16.VVIX/C16.VOL_COMPLEX/C15.TERM daily branch only. Not official replication. Not Context.",
    }