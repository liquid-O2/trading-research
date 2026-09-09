"""Date aggregates, block-bootstrap groups and the readable quote-quality report.

Every fraction uses one named population for numerator and denominator.
Equal-date means stay distinct from event-weighted raw means and from exact
raw-value quantiles. Absence, missing files and undefined OI-weighted
fractions stay missing, never zero. Shared moving-block weights are cached
per exact date universe. Fixtures do not mark the scientific family complete.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import json
import math
import time as pytime

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.scoring import quantile


VERSION = "options-quote-quality-support-statistics-v2"
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
CLASS_FRACTIONS = (
    "usable_fraction", "conflict_fraction", "all_zero_fraction",
    "one_sided_fraction", "crossed_fraction", "locked_fraction",
    "two_sided_fraction", "invalid_fraction",
)
FLAG_NAMES = (
    "condition_zero", "nonpositive_size", "negative_size", "zero_bid", "zero_ask",
    "negative_price", "nonfinite_price", "session_outside", "request_date_mismatch",
)
BASE_CLASS_NAMES = (
    "invalid_identity", "invalid_clock", "invalid_numeric", "conflict",
    "all_zero", "one_sided", "crossed", "locked", "two_sided",
)
PRESPECIFIED = (
    "quoted_fraction", "listed_unquoted_fraction", "quoted_unlisted_fraction",
    "usable_fraction", "conflict_fraction", "all_zero_fraction",
    "one_sided_fraction", "crossed_fraction", "locked_fraction", "two_sided_fraction",
    "invalid_fraction",
    "raw_invalid_identity_fraction", "raw_invalid_clock_fraction",
    "raw_invalid_numeric_fraction", "raw_conflict_fraction",
    "raw_all_zero_fraction", "raw_one_sided_fraction", "raw_crossed_fraction",
    "raw_locked_fraction", "raw_two_sided_fraction",
    "unique_invalid_identity_fraction", "unique_invalid_clock_fraction",
    "unique_invalid_numeric_fraction", "unique_conflict_fraction",
    "unique_all_zero_fraction", "unique_one_sided_fraction", "unique_crossed_fraction",
    "unique_locked_fraction", "unique_two_sided_fraction",
    "raw_condition_zero_fraction", "raw_nonpositive_size_fraction",
    "raw_negative_size_fraction", "raw_zero_bid_fraction", "raw_zero_ask_fraction",
    "raw_negative_price_fraction", "raw_nonfinite_price_fraction",
    "raw_session_outside_fraction", "raw_request_date_mismatch_fraction",
    "unique_condition_zero_fraction", "unique_nonpositive_size_fraction",
    "unique_negative_size_fraction", "unique_zero_bid_fraction",
    "unique_zero_ask_fraction", "unique_negative_price_fraction",
    "unique_nonfinite_price_fraction", "unique_session_outside_fraction",
    "unique_request_date_mismatch_fraction",
    "mean_bid", "mean_ask", "mean_mid", "mean_spread",
    "mean_relative_spread", "mean_sample_age_s", "mean_payload_age_s",
    "sample_stale_60_fraction", "sample_stale_300_fraction", "sample_stale_900_fraction",
    "payload_stale_60_fraction", "payload_stale_300_fraction", "payload_stale_900_fraction",
    "oi_covered_fraction", "oi_weighted_quoted_fraction",
    "missing_file_fraction", "empty_marker_fraction", "no_sample_fraction",
    "etf_present_fraction", "cash_present_fraction", "fred_present_fraction",
    "action_present_fraction", "near_broad_agree_fraction", "near_broad_conflict_fraction",
    "unmatched_sample_clock_fraction",
    "raw_row_count", "unique_event_count",
    "mean_bid_raw", "mean_ask_raw", "mean_mid_raw",
    "mean_bid_unique", "mean_ask_unique", "mean_mid_unique",
)
RATIO_SPECS = {
    "usable_over_quoted": ("usable_quotes", "quoted_contracts"),
    "quoted_over_listed": ("quoted_listed", "listed_contracts"),
}
METRIC_UNITS = {
    "mean_bid": "price", "mean_ask": "price", "mean_mid": "price",
    "mean_spread": "price", "mean_relative_spread": "fraction",
    "mean_sample_age_s": "seconds", "mean_payload_age_s": "seconds",
    "mean_bid_raw": "price", "mean_ask_raw": "price", "mean_mid_raw": "price",
    "mean_bid_unique": "price", "mean_ask_unique": "price", "mean_mid_unique": "price",
    "raw_row_count": "count", "unique_event_count": "count",
}
HIST_FOR_METRIC = {
    "mean_bid": ("bid", "cut"),
    "mean_ask": ("ask", "cut"),
    "mean_mid": ("mid", "cut"),
    "mean_spread": ("spread", "cut"),
    "mean_sample_age_s": ("sample_age_s", "cut"),
    "mean_payload_age_s": ("payload_age_s", "cut"),
    "mean_bid_raw": ("bid", "raw_source"),
    "mean_ask_raw": ("ask", "raw_source"),
    "mean_mid_raw": ("mid", "raw_source"),
    "mean_bid_unique": ("bid", "unique_source"),
    "mean_ask_unique": ("ask", "unique_source"),
    "mean_mid_unique": ("mid", "unique_source"),
}


def _cfg(protocol):
    stats = protocol["statistics"]
    return {
        "seed": int(stats["seed"]),
        "block_length": int(stats["block_length"]),
        "replicates": int(stats["replicates"]),
        "confidence": float(stats["confidence"]),
        "minimum_dates": int(stats["minimum_dates"]),
        "minimum_events": int(stats["minimum_events"]),
        "quantiles": tuple(stats.get("quantiles") or QUANTILE_LEVELS),
    }


def _ratio(num, den):
    if den in (None, 0) or num is None:
        return None
    return num / den


def empty_metric(intended_dates, *, units=None):
    n = len(intended_dates)
    return {
        "estimate": None,
        "actual_valid_date_count": 0,
        "actual_valid_event_count": 0,
        "valid_date_count": 0,
        "valid_event_count": 0,
        "missing_date_count": n,
        "estimator": "date_mean",
        "units": units,
        "support": {
            "independent_dates": 0,
            "events": 0,
            "minimum_independent_dates": None,
            "minimum_events": None,
            "sparse": True,
            "reasons": ["all_values_missing"],
        },
        "bootstrap": None,
        "date_quantiles": {str(level): None for level in QUANTILE_LEVELS},
        "raw_quantiles": {str(level): None for level in QUANTILE_LEVELS},
        "event_weighted_estimate": None,
        "raw_mean": None,
    }


def empty_ratio(intended_dates, numerator, denominator):
    payload = empty_metric(intended_dates)
    payload["numerator"] = numerator
    payload["denominator"] = denominator
    return payload


def date_quantiles(values, levels):
    if not values:
        return {str(level): None for level in levels}
    ordered = tuple(sorted(values))
    return {str(level): float(quantile(ordered, level)) for level in levels}


def exact_quantiles_from_values(values, levels):
    """Exact empirical quantiles from typed values. No approximation."""
    present = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return date_quantiles(present, levels)


def _typed_histogram(values, counts):
    import numpy as np
    if len(values) != len(counts):
        raise ContractError('histogram values and counts differ')
    if not len(values):
        return np.empty(0, dtype=np.float64), np.empty(0, dtype=np.int64)
    try:
        vv = np.asarray(values, dtype=np.float64)
        cc = np.asarray(counts, dtype=np.int64)
    except (TypeError, ValueError, OverflowError):
        pairs = [(float(v), int(c)) for v, c in zip(values, counts)
                 if v is not None and c is not None and math.isfinite(float(v)) and int(c) > 0]
        if any(c > 2**63 - 1 for _, c in pairs):
            raise ContractError('histogram frequency exceeds exact signed integer capacity')
        vv = np.asarray([v for v, _ in pairs], dtype=np.float64)
        cc = np.asarray([c for _, c in pairs], dtype=np.int64)
    valid = np.isfinite(vv) & (cc > 0)
    return (vv, cc) if bool(np.all(valid)) else (vv[valid], cc[valid])


def _histogram_total(values, counts):
    import numpy as np
    vv, cc = _typed_histogram(values, counts)
    n = int(np.sum(cc, dtype=np.int64))
    if n < 0:
        raise ContractError('histogram frequency sum overflow')
    return float(np.sum(vv * cc, dtype=np.float64)), n


def exact_quantiles_from_histogram(values, counts, levels):
    """Exact empirical ranks in sorted weighted bins; never expand observations."""
    import numpy as np
    vv, cc = _typed_histogram(values, counts)
    if not len(vv):
        return {str(level): None for level in levels}
    order = np.argsort(vv, kind='stable')
    xs = vv[order]
    cdf = np.cumsum(cc[order], dtype=np.int64)
    if np.any(cdf <= 0) or np.any(cdf[1:] < cdf[:-1]):
        raise ContractError('histogram cumulative frequency overflow')
    total = int(cdf[-1])
    out = {}
    for level in levels:
        index = (total - 1) * float(level)
        lo, hi = math.floor(index), math.ceil(index)
        a, b = np.searchsorted(cdf, [lo + 1, hi + 1], side='left')
        vlo, vhi = float(xs[a]), float(xs[b])
        out[str(level)] = vlo + (vhi - vlo) * (index - lo)
    return out


def universe_dates(intended_all, *, year=None, stage=None, stages=None):
    out = []
    for label in intended_all:
        if year is not None and not label.startswith(str(year)):
            continue
        if stage is not None:
            bounds = stages[stage]
            if not (bounds[0] <= label < bounds[1]):
                continue
        out.append(label)
    return out


def date_balanced_point(date_values):
    present = [value for value in date_values.values() if value is not None]
    if not present:
        return None
    return sum(present) / len(present)


def raw_mean(sum_value, count):
    if not count:
        return None
    return sum_value / count


_BLOCK_CACHE = {}


def _bootstrap_state(dates, cfg):
    """Cache shared moving-block weights per exact date universe."""
    from trading_research.research.date_statistics import _moving_weights, _numpy
    key = (tuple(dates), cfg["seed"], cfg["block_length"], cfg["replicates"])
    hit = _BLOCK_CACHE.get(key)
    if hit is not None:
        return hit
    np = _numpy()
    weights, starts = _moving_weights(
        np, len(dates), seed=cfg["seed"], block_length=cfg["block_length"],
        replicates=cfg["replicates"],
    )
    state = (np, weights, starts)
    _BLOCK_CACHE[key] = state
    return state


def _overlay_raw_support(payload, dates, cells, raw_events, cfg, raw_mean_value=None):
    events = 0
    for day in dates:
        if day in cells and cells[day] is not None:
            events += int(raw_events.get(day) or 0)
    payload["actual_valid_event_count"] = events
    payload["valid_event_count"] = events
    payload["raw_mean"] = raw_mean_value
    payload["event_weighted_estimate"] = raw_mean_value
    support = payload.setdefault("support", {})
    support["events"] = events
    dates_n = int(payload.get("actual_valid_date_count") or 0)
    reasons = []
    if dates_n < cfg["minimum_dates"]:
        reasons.append("fewer_than_minimum_independent_dates")
    if events < cfg["minimum_events"]:
        reasons.append("fewer_than_minimum_events")
    support["independent_dates"] = dates_n
    support["minimum_independent_dates"] = cfg["minimum_dates"]
    support["minimum_events"] = cfg["minimum_events"]
    support["sparse"] = bool(reasons)
    support["reasons"] = reasons
    return payload


def _summarize(metrics, dates, cfg, *, ratios=None, event_counts=None, raw_means=None,
               estimator="date_mean", raw_quantiles=None, units=None):
    names = list(metrics)
    filled = {}
    for name, values in metrics.items():
        filled[name] = {day: values[day] for day in dates if day in values and values[day] is not None}
    present = {name: cells for name, cells in filled.items() if cells}
    ratio_specs = dict(ratios or {})
    send_ratios = {name: pair for name, pair in ratio_specs.items()
                   if pair[0] in present and pair[1] in present}
    if present:
        result = observed_date_statistics(
            present, dates, ratios=send_ratios or None, estimator=estimator,
            seed=cfg["seed"], block_length=cfg["block_length"], replicates=cfg["replicates"],
            confidence=cfg["confidence"], minimum_independent_dates=cfg["minimum_dates"],
            minimum_events=cfg["minimum_events"], _retain_replicate_estimates=False,
            _bootstrap_state=_bootstrap_state(dates, cfg),
        )
        result["all_values_missing"] = False
    else:
        result = {
            "schema": "observed-date-statistics-v1",
            "intended_dates": list(dates),
            "intended_date_count": len(dates),
            "metrics": {},
            "ratios": {},
            "all_values_missing": True,
        }
    metrics_out = {}
    raw = event_counts or {}
    raw_means = raw_means or {}
    raw_quantiles = raw_quantiles or {}
    units = units or {}
    for name in names:
        if name in result.get("metrics", {}):
            payload = result["metrics"][name]
            series = [present[name][day] for day in dates if day in present[name]]
            payload["date_quantiles"] = date_quantiles(series, cfg["quantiles"])
            payload["raw_quantiles"] = raw_quantiles.get(name) or {
                str(level): None for level in cfg["quantiles"]
            }
            payload["missing_date_count"] = len(dates) - payload.get("actual_valid_date_count", 0)
            payload["units"] = units.get(name, METRIC_UNITS.get(name, "fraction" if name.endswith("_fraction") else None))
            _overlay_raw_support(payload, dates, present[name], raw.get(name, {}), cfg,
                                 raw_mean_value=raw_means.get(name))
            metrics_out[name] = payload
        else:
            metrics_out[name] = empty_metric(
                dates, units=units.get(name, METRIC_UNITS.get(name, "fraction" if name.endswith("_fraction") else None)),
            )
    ratios_out = {}
    for name, pair in ratio_specs.items():
        if name in result.get("ratios", {}):
            payload = result["ratios"][name]
            num_events = sum(int((raw.get(pair[0]) or {}).get(day) or 0)
                             for day in dates if day in present.get(pair[0], {}))
            den_events = sum(int((raw.get(pair[1]) or {}).get(day) or 0)
                             for day in dates if day in present.get(pair[1], {}))
            events = min(num_events, den_events)
            payload["actual_valid_event_count"] = events
            payload["valid_event_count"] = events
            payload.setdefault("support", {})
            payload["support"]["events"] = events
            reasons = []
            dates_n = int(payload.get("actual_valid_date_count") or 0)
            if dates_n < cfg["minimum_dates"]:
                reasons.append("fewer_than_minimum_independent_dates")
            if events < cfg["minimum_events"]:
                reasons.append("fewer_than_minimum_events")
            payload["support"]["sparse"] = bool(reasons)
            payload["support"]["reasons"] = reasons
            ratios_out[name] = payload
        else:
            ratios_out[name] = empty_ratio(dates, pair[0], pair[1])
    result["metrics"] = metrics_out
    result["ratios"] = ratios_out
    return result


def _mean_frac(items, num_key, den_key):
    values = []
    events = 0
    num_sum = den_sum = 0
    for item in items:
        den = item.get(den_key)
        num = item.get(num_key)
        frac = _ratio(num, den)
        if frac is None:
            continue
        values.append(frac)
        events += int(den or 0)
        num_sum += int(num or 0)
        den_sum += int(den or 0)
    if not values:
        return None, 0, None
    return sum(values) / len(values), events, (num_sum, den_sum)


def _mean_level(items, sum_key, n_key):
    means = []
    total_s = 0.0
    total_n = 0
    for item in items:
        count = item.get(n_key) or 0
        total = item.get(sum_key)
        if not count or total is None:
            continue
        means.append(total / count)
        total_s += total
        total_n += count
    if not means:
        return None, 0, None
    return sum(means) / len(means), total_n, (total_s, total_n)


def _canonical_family(rows):
    families = {row.get("source_family") for row in rows}
    if "union" in families:
        return "union"
    if "vix_full" in families:
        return "vix_full"
    if "near" in families:
        return "near"
    if "broad" in families:
        return "broad"
    return None


def _filter_coverage(rows, *, family, cut):
    out = []
    canon = _canonical_family(rows) if family in (None, "all") else family
    for row in rows:
        if not row.get("intended"):
            continue
        if not row.get("cut_applicable"):
            continue
        if family in (None, "all"):
            if row.get("source_family") != canon:
                continue
        elif row.get("source_family") != family:
            continue
        if cut not in (None, "all") and row.get("cut_label") != cut:
            continue
        out.append(row)
    return out


def _coverage_maps(coverage_rows, *, family="all", cut="all"):
    by_date = defaultdict(list)
    for row in coverage_rows:
        by_date[row["request_date"]].append(row)
    metrics = defaultdict(dict)
    events = defaultdict(dict)
    sums = {}
    extras = defaultdict(dict)
    for day, raw_items in by_date.items():
        items = _filter_coverage(raw_items, family=family, cut=cut)
        if not items:
            continue
        usable, ev, raw = _mean_frac(items, "usable_count", "quoted_count")
        metrics["usable_fraction"][day] = usable
        events["usable_fraction"][day] = ev
        conflict, ev, _ = _mean_frac(items, "conflict_count", "quoted_count")
        metrics["conflict_fraction"][day] = conflict
        events["conflict_fraction"][day] = ev
        for name, key in (
            ("all_zero_fraction", "all_zero_count"),
            ("one_sided_fraction", "one_sided_count"),
            ("crossed_fraction", "crossed_count"),
            ("locked_fraction", "locked_count"),
            ("two_sided_fraction", "two_sided_count"),
            ("invalid_fraction", "invalid_count"),
            ("quoted_unlisted_fraction", "quoted_unlisted"),
        ):
            value, ev, _ = _mean_frac(items, key, "quoted_count")
            metrics[name][day] = value
            events[name][day] = ev
        listed_items = [item for item in items if item.get("listing_known") and item.get("listed_count") is not None]
        qf, ev, _ = _mean_frac(listed_items, "quoted_listed", "listed_count")
        metrics["quoted_fraction"][day] = qf
        events["quoted_fraction"][day] = ev
        lu, ev, _ = _mean_frac(listed_items, "listed_unquoted", "listed_count")
        metrics["listed_unquoted_fraction"][day] = lu
        events["listed_unquoted_fraction"][day] = ev
        extras["quoted_listed"][day] = sum(int(item.get("quoted_listed") or 0) for item in listed_items)
        extras["listed_contracts"][day] = sum(int(item.get("listed_count") or 0) for item in listed_items)
        extras["usable_quotes"][day] = sum(int(item.get("usable_count") or 0) for item in items)
        extras["quoted_contracts"][day] = sum(int(item.get("quoted_count") or 0) for item in items)
        for name, key in (
            ("sample_stale_60_fraction", "sample_stale_60_count"),
            ("sample_stale_300_fraction", "sample_stale_300_count"),
            ("sample_stale_900_fraction", "sample_stale_900_count"),
            ("payload_stale_60_fraction", "payload_stale_60_count"),
            ("payload_stale_300_fraction", "payload_stale_300_count"),
            ("payload_stale_900_fraction", "payload_stale_900_count"),
        ):
            value, ev, _ = _mean_frac(items, key, "quoted_with_age")
            metrics[name][day] = value
            events[name][day] = ev
        for metric, sum_key, n_key in (
            ("mean_bid", "bid_sum", "bid_n"),
            ("mean_ask", "ask_sum", "ask_n"),
            ("mean_mid", "mid_sum", "mid_n"),
            ("mean_spread", "spread_sum", "spread_n"),
            ("mean_relative_spread", "rel_spread_sum", "rel_spread_n"),
            ("mean_sample_age_s", "sample_age_sum", "quoted_with_age"),
            ("mean_payload_age_s", "payload_age_sum", "quoted_with_age"),
        ):
            value, ev, raw = _mean_level(items, sum_key, n_key)
            metrics[metric][day] = value
            events[metric][day] = ev
            sums.setdefault(metric, {})[day] = raw
        covered, ev, _ = _mean_frac(items, "oi_quoted_available_count", "quoted_count")
        metrics["oi_covered_fraction"][day] = covered
        events["oi_covered_fraction"][day] = ev
        weights = [item.get("oi_weighted_quoted_fraction") for item in items
                   if item.get("oi_weighted_quoted_fraction") is not None]
        metrics["oi_weighted_quoted_fraction"][day] = None if not weights else sum(weights) / len(weights)
        events["oi_weighted_quoted_fraction"][day] = len(weights)
        n_cuts = len(items)
        metrics["missing_file_fraction"][day] = sum(1 for item in items if item.get("missing_file")) / n_cuts
        events["missing_file_fraction"][day] = n_cuts
        metrics["empty_marker_fraction"][day] = sum(1 for item in items if item.get("empty_marker")) / n_cuts
        events["empty_marker_fraction"][day] = n_cuts
        metrics["no_sample_fraction"][day] = sum(1 for item in items if item.get("cut_status") == "no_sample") / n_cuts
        events["no_sample_fraction"][day] = n_cuts
    return {"metrics": metrics, "events": events, "sums": sums, "extras": extras}


def _quality_maps(quality_rows, *, family="all", right="all", dte="all"):
    by_date = defaultdict(list)
    for row in quality_rows:
        if family not in (None, "all") and row.get("source_family") != family:
            continue
        if right not in (None, "all") and (row.get("right") or "unknown") != right:
            continue
        if dte not in (None, "all") and (row.get("dte_bucket") or "unknown") != dte:
            continue
        by_date[row["request_date"]].append(row)
    metrics = defaultdict(dict)
    events = defaultdict(dict)
    for day, items in by_date.items():
        raw_items = [item for item in items if item['source_family'] != 'union'] if family in (None, 'all') else items
        unique_items = [item for item in items if item['source_family'] == 'union'] if family in (None, 'all') else items
        if not unique_items:
            unique_items = raw_items
        raw = sum(int(item.get("raw_rows") or 0) for item in raw_items)
        uniq = sum(int(item.get("unique_events") or 0) for item in unique_items)
        metrics["raw_row_count"][day] = raw
        events["raw_row_count"][day] = raw
        metrics["unique_event_count"][day] = uniq
        events["unique_event_count"][day] = uniq
        for name in BASE_CLASS_NAMES:
            metrics[f"raw_{name}_fraction"][day] = _ratio(
                sum(int(item.get(f"raw_{name}") or 0) for item in raw_items), raw)
            events[f"raw_{name}_fraction"][day] = raw
            metrics[f"unique_{name}_fraction"][day] = _ratio(
                sum(int(item.get(f"unique_{name}") or 0) for item in unique_items), uniq)
            events[f"unique_{name}_fraction"][day] = uniq
        for name in FLAG_NAMES:
            metrics[f"raw_{name}_fraction"][day] = _ratio(
                sum(int(item.get(f"raw_{name}") or 0) for item in raw_items), raw)
            events[f"raw_{name}_fraction"][day] = raw
            metrics[f"unique_{name}_fraction"][day] = _ratio(
                sum(int(item.get(f"unique_{name}") or 0) for item in unique_items), uniq)
            events[f"unique_{name}_fraction"][day] = uniq
    return {"metrics": metrics, "events": events}


def _support_maps(support_rows, *, cut="all"):
    by_date = defaultdict(list)
    for row in support_rows:
        if cut not in (None, "all") and row.get("cut_label") != cut:
            continue
        by_date[row["request_date"]].append(row)
    metrics = defaultdict(dict)
    events = defaultdict(dict)
    for day, items in by_date.items():
        n = len(items)
        if not n:
            continue
        metrics["etf_present_fraction"][day] = sum(1 for item in items if item.get("etf_present")) / n
        events["etf_present_fraction"][day] = n
        metrics["cash_present_fraction"][day] = sum(
            1 for item in items if item.get("cash_close") is not None) / n
        events["cash_present_fraction"][day] = n
        metrics["fred_present_fraction"][day] = sum(1 for item in items if item.get("fred_present")) / n
        events["fred_present_fraction"][day] = n
        metrics["action_present_fraction"][day] = sum(
            1 for item in items if (item.get("action_event_count") or 0) > 0) / n
        events["action_present_fraction"][day] = n
    return {"metrics": metrics, "events": events}


def _paired_maps(paired):
    metrics = defaultdict(dict)
    events = defaultdict(dict)
    if not paired:
        return {"metrics": metrics, "events": events}
    day = None
    # paired is stored per date-aggregate row; caller passes {date: payload}
    for day, payload in paired.items():
        common = payload.get("common") or 0
        metrics["near_broad_agree_fraction"][day] = _ratio(payload.get("agree"), common)
        events["near_broad_agree_fraction"][day] = common
        metrics["near_broad_conflict_fraction"][day] = _ratio(payload.get("conflict"), common)
        events["near_broad_conflict_fraction"][day] = common
        clocks = (payload.get("near_only") or 0) + (payload.get("broad_only") or 0) + common
        unmatched = payload.get("unmatched_sample_clocks")
        metrics["unmatched_sample_clock_fraction"][day] = _ratio(unmatched, clocks) if clocks else None
        events["unmatched_sample_clock_fraction"][day] = clocks
    return {"metrics": metrics, "events": events}


def _slice_maps(slices_by_date, *, family="all", cut="all", right="all", dte="all"):
    metrics = defaultdict(dict)
    events = defaultdict(dict)
    sums = defaultdict(dict)
    for day, slices in slices_by_date.items():
        items = []
        for key, bag in slices.items():
            fam, cut_label, right_label, dte_label = key.split("|")
            if family not in (None, "all") and fam != family:
                continue
            if family in (None, "all") and fam not in {"union", "vix_full", "near", "broad"}:
                continue
            if family in (None, "all") and fam not in {"union", "vix_full"}:
                continue
            if cut not in (None, "all") and cut_label != cut:
                continue
            if right not in (None, "all") and right_label != right:
                continue
            if dte not in (None, "all") and dte_label != dte:
                continue
            items.append(bag)
        if not items:
            continue
        quoted = sum(item["quoted"] for item in items)
        if not quoted:
            continue
        metrics["usable_fraction"][day] = sum(item["usable"] for item in items) / quoted
        events["usable_fraction"][day] = quoted
        for name in ("conflict", "all_zero", "one_sided", "crossed", "locked", "two_sided", "invalid"):
            metrics[f"{name}_fraction"][day] = sum(item[name] for item in items) / quoted
            events[f"{name}_fraction"][day] = quoted
        bid_n = sum(item["bid_n"] for item in items)
        if bid_n:
            bid_s = sum(item["bid_sum"] for item in items)
            metrics["mean_bid"][day] = bid_s / bid_n
            events["mean_bid"][day] = bid_n
            sums["mean_bid"][day] = (bid_s, bid_n)
        age_n = sum(item["age_n"] for item in items)
        if age_n:
            metrics["mean_sample_age_s"][day] = sum(item["sample_age_sum"] for item in items) / age_n
            metrics["mean_payload_age_s"][day] = sum(item["payload_age_sum"] for item in items) / age_n
            events["mean_sample_age_s"][day] = age_n
            events["mean_payload_age_s"][day] = age_n
            for thresh in (60, 300, 900):
                metrics[f"sample_stale_{thresh}_fraction"][day] = sum(
                    item[f"sample_stale_{thresh}"] for item in items) / age_n
                metrics[f"payload_stale_{thresh}_fraction"][day] = sum(
                    item[f"payload_stale_{thresh}"] for item in items) / age_n
                events[f"sample_stale_{thresh}_fraction"][day] = age_n
                events[f"payload_stale_{thresh}_fraction"][day] = age_n
    return {"metrics": metrics, "events": events, "sums": sums}


def _merge_maps(*parts):
    metrics = defaultdict(dict)
    events = defaultdict(dict)
    extras = defaultdict(dict)
    acc_s = defaultdict(float)
    acc_n = defaultdict(int)
    for part in parts:
        if not part:
            continue
        for name, cells in (part.get("metrics") or {}).items():
            for day, value in cells.items():
                metrics[name][day] = value
        for name, cells in (part.get("events") or {}).items():
            for day, value in cells.items():
                events[name][day] = (events[name].get(day) or 0) + (value or 0) if day in events[name] else value
        for name, cells in (part.get("extras") or {}).items():
            extras[name].update(cells)
        for name, cells in (part.get("sums") or {}).items():
            for day, raw in cells.items():
                if isinstance(raw, tuple):
                    acc_s[name] += float(raw[0] or 0)
                    acc_n[name] += int(raw[1] or 0)
                elif raw is not None:
                    acc_s[name] += float(raw)
                    acc_n[name] += 1
    raw_means = {name: raw_mean(acc_s[name], acc_n[name]) for name in acc_n if acc_n[name]}
    return metrics, events, raw_means, extras


@lru_cache(maxsize=65536)
def _hist_key_parts(key):
    parts = str(key).split("|")
    if len(parts) != 6:
        return None
    return {
        "metric": parts[0], "population": parts[1], "source_family": parts[2],
        "cut": parts[3], "right": parts[4], "dte": parts[5],
    }


def _histograms_for(rows, dates, metric, population, family, cut, right, dte):
    values, counts = [], []
    for row in rows:
        if row["request_date"] not in dates:
            continue
        available = {p['source_family'] for key in (row.get('histograms') or {})
                     if (p := _hist_key_parts(key)) is not None and p['population'] == population}
        canonical = next((name for name in ('union', 'vix_full', 'near', 'broad') if name in available), None)
        for key, hist in (row.get("histograms") or {}).items():
            parts = _hist_key_parts(key)
            if parts is None:
                continue
            if parts["metric"] != metric or parts["population"] != population:
                continue
            if family not in (None, "all") and parts["source_family"] != family:
                continue
            if family in (None, "all") and parts["source_family"] == "union" and population == "raw_source":
                continue
            if family in (None, 'all') and population in ('cut', 'unique_source') and parts['source_family'] != canonical:
                continue
            if cut not in (None, "all") and parts["cut"] not in {cut, "all", "-"}:
                continue
            if right not in (None, "all") and parts["right"] != right:
                continue
            if dte not in (None, "all") and parts["dte"] != dte:
                continue
            values.extend(hist.get("v") or [])
            counts.extend(hist.get("c") or [])
    return values, counts



def _row_histograms(row):
    from trading_research.research.auction_flow_storage import read_json_artifact
    if 'histograms_ref' not in row:
        return row.get('histograms') or {}
    payload = read_json_artifact(row['histograms_ref'])
    if (payload.get('kind') != 'options_quote_daily_histograms_v1'
            or payload.get('chain') != row['chain']
            or payload.get('request_date') != row['request_date']):
        raise IntegrityError('quote histogram identity differs from daily aggregate')
    return payload['histograms']


def freeze_date_aggregate(outputs, row, ordinal):
    """Persist the large daily payload immediately; retain only daily metadata."""
    if 'histograms_ref' in row or 'pooled_histograms_ref' in row:
        return row
    metadata = {key: value for key, value in row.items() if key != 'histograms'}
    metadata['histograms_ref'] = outputs.json_compressed(
        f'date-histograms-{ordinal:05d}.json.zst',
        {'kind': 'options_quote_daily_histograms_v1', 'chain': row['chain'],
         'request_date': row['request_date'], 'histograms': row.get('histograms') or {}},
        kind='options_quote_daily_histograms_v1', measurement_fast_path=True)
    return metadata


def _merge_exact_histograms(left, right):
    """Coalesce identical binary64 values, retaining exact integer frequencies."""
    import numpy as np
    if left is None:
        vv, cc = right
    else:
        vv = np.concatenate((left[0], right[0]))
        cc = np.concatenate((left[1], right[1]))
    if not len(vv):
        return vv, cc
    order = np.argsort(vv, kind='stable')
    vv, cc = vv[order], cc[order]
    starts = np.r_[0, np.flatnonzero(vv[1:] != vv[:-1]) + 1]
    merged = np.add.reduceat(cc, starts)
    if np.any(merged <= 0):
        raise ContractError('coalesced histogram frequency overflow')
    return vv[starts], merged


class HistogramUniverse:
    """Exact pooled bins and per-date moments; only one chain universe in memory."""
    def __init__(self, rows=(), dates=None, levels=QUANTILE_LEVELS):
        self.levels = levels
        self.pool = {}
        self.daily = defaultdict(dict)
        self.cache = {}
        self.dates = set()
        self.loaded_days = 0
        self.input_bins = 0
        self.peak_pooled_bins = 0
        included_pools = set()
        allowed = set(dates) if dates is not None else {row['request_date'] for row in rows}
        for row in rows:
            if row['request_date'] not in allowed:
                continue
            reference = row.get('pooled_histograms_ref')
            if reference is None:
                self.add_row(row)
            elif reference['sha256'] not in included_pools:
                self.add_pool(reference, allowed_dates=allowed, chain=row['chain'])
                included_pools.add(reference['sha256'])

    def add_row(self, row):
        day = row['request_date']
        if day in self.dates:
            raise IntegrityError('histogram universe repeats a source date')
        self.dates.add(day)
        histograms = _row_histograms(row)
        available = defaultdict(set)
        for key in histograms:
            parts = _hist_key_parts(key)
            if parts is not None:
                available[parts['population']].add(parts['source_family'])
        canonical = {pop: next((fam for fam in ('union', 'vix_full', 'near', 'broad')
                               if fam in families), None)
                     for pop, families in available.items()}
        day_totals = defaultdict(lambda: [0.0, 0])
        for key, hist in histograms.items():
            parts = _hist_key_parts(key)
            if parts is None:
                continue
            metric, pop, fam, cut, right, dte = (parts[k] for k in
                ('metric', 'population', 'source_family', 'cut', 'right', 'dte'))
            vv, cc = _typed_histogram(hist.get('v', ()), hist.get('c', ()))
            self.input_bins += len(vv)
            is_canonical = fam == canonical.get(pop)
            pool_key = (metric, pop, fam, cut, right, dte, is_canonical)
            self.pool[pool_key] = _merge_exact_histograms(self.pool.get(pool_key), (vv, cc))
            if pop not in ('raw_source', 'unique_source'):
                continue
            total, n = _histogram_total(vv, cc)
            families = [fam]
            if (pop == 'raw_source' and fam != 'union') or (pop == 'unique_source' and is_canonical):
                families.append('all')
            for f in families:
                for r in (right, 'all'):
                    for d in (dte, 'all'):
                        cell = day_totals[(metric, pop, f, r, d)]
                        cell[0] += total
                        cell[1] += n
        for key, value in day_totals.items():
            self.daily[key][day] = tuple(value)
        self.loaded_days += 1
        self.peak_pooled_bins = max(self.peak_pooled_bins,
                                   sum(len(hist[0]) for hist in self.pool.values()))
        del histograms

    def add_pool(self, reference, *, allowed_dates, chain):
        from trading_research.research.auction_flow_storage import read_json_artifact
        payload = read_json_artifact(reference)
        if payload.get('kind') != 'options_quote_pooled_histograms_v1' or payload.get('chain') != chain:
            raise IntegrityError('pooled quote histogram identity differs')
        dates = set(payload['dates'])
        if len(dates) != len(payload['dates']) or not dates <= allowed_dates:
            raise IntegrityError('histogram pool cannot substitute a partial date universe')
        if self.dates & dates:
            raise IntegrityError('histogram pools repeat a date')
        pooled_bins = 0
        for part in payload['parts']:
            piece = read_json_artifact(part)
            if piece.get('kind') != 'options_quote_pooled_histogram_part_v1' or piece.get('chain') != chain:
                raise IntegrityError('pooled quote histogram part identity differs')
            for item in piece['histograms']:
                key = tuple(item['key'])
                if len(key) != 7 or type(key[-1]) is not bool:
                    raise IntegrityError('pooled quote histogram key is invalid')
                vv, cc = _typed_histogram(item['v'], item['c'])
                pooled_bins += len(vv)
                self.pool[key] = _merge_exact_histograms(self.pool.get(key), (vv, cc))
        if pooled_bins != payload['pooled_bins']:
            raise IntegrityError('pooled quote histogram bin count differs')
        for key, cells in payload['daily_totals'].items():
            parts = tuple(key.split('|'))
            if len(parts) != 5 or not set(cells) <= dates:
                raise IntegrityError('pooled quote daily moments escaped their universe')
            self.daily[parts].update({day: tuple(value) for day, value in cells.items()})
        self.dates.update(dates)
        self.loaded_days += len(dates)
        self.input_bins += payload['input_bins']
        self.peak_pooled_bins = max(self.peak_pooled_bins, sum(len(hist[0]) for hist in self.pool.values()))

    def write_pool(self, outputs, *, chain, name, maximum_part_bins=250_000):
        """Retain every exact rank frequency once for a complete chain/date shard."""
        parts = []
        records = []
        bins = total_bins = 0
        def flush():
            nonlocal records, bins
            if not records:
                return
            part = outputs.json_compressed(f'{name}-part-{len(parts):04d}.json.zst',
                {'kind': 'options_quote_pooled_histogram_part_v1', 'chain': chain, 'histograms': records},
                kind='options_quote_pooled_histogram_part_v1', measurement_fast_path=True)
            parts.append(part)
            records, bins = [], 0
        for key, (values, counts) in sorted(self.pool.items()):
            for begin in range(0, len(values), maximum_part_bins):
                end = min(len(values), begin + maximum_part_bins)
                if bins and bins + end - begin > maximum_part_bins:
                    flush()
                records.append({'key': list(key), 'v': values[begin:end].tolist(), 'c': counts[begin:end].tolist()})
                bins += end - begin
                total_bins += end - begin
        flush()
        ref = outputs.json_compressed(f'{name}.json.zst', {
            'kind': 'options_quote_pooled_histograms_v1', 'chain': chain,
            'dates': sorted(self.dates), 'parts': parts,
            'daily_totals': {'|'.join(key): cells for key, cells in self.daily.items()},
            'input_bins': self.input_bins, 'pooled_bins': total_bins,
            'semantics': 'Exact binary64 values and integer frequencies; canonical-family membership fixed separately for each original day; equal-date raw/unique moments retained. Use only whole declared date shards.',
        }, kind='options_quote_pooled_histograms_v1', measurement_fast_path=True)
        return {**ref, 'input_bins': self.input_bins, 'pooled_bins': total_bins,
                'total_output_bytes': ref['size_bytes'] + sum(part['size_bytes'] for part in parts)}

    def summary(self, metric, population, family, cut, right, dte):
        import numpy as np
        # Raw/unique source histograms have the protocol's '-' cut key.
        query_cut = 'all' if population in ('raw_source', 'unique_source') else cut
        key = (metric, population, family, query_cut, right, dte)
        if key not in self.cache:
            values, counts = [], []
            for (m, p, f, c, r, d, canonical), hist in self.pool.items():
                if m != metric or p != population:
                    continue
                if family not in (None, 'all') and f != family:
                    continue
                if family in (None, 'all'):
                    if population == 'raw_source' and f == 'union':
                        continue
                    if population in ('cut', 'unique_source') and not canonical:
                        continue
                if query_cut not in (None, 'all') and c not in (query_cut, 'all', '-'):
                    continue
                if right not in (None, 'all') and r != right:
                    continue
                if dte not in (None, 'all') and d != dte:
                    continue
                values.append(hist[0])
                counts.append(hist[1])
            vv = np.concatenate(values) if values else np.empty(0, dtype=np.float64)
            cc = np.concatenate(counts) if counts else np.empty(0, dtype=np.int64)
            self.cache[key] = (exact_quantiles_from_histogram(vv, cc, self.levels),
                               _histogram_total(vv, cc))
        return self.cache[key]

    def daily_totals(self, metric, population, family, right, dte):
        return self.daily.get((metric, population, family or 'all', right or 'all', dte or 'all'), {})

def _group_key(chain, universe, cut, family, right, dte):
    return f"{chain}|{universe}|{cut}|{family}|{right}|{dte}"


def _observed(rows):
    cuts, families, rights, dtes, combos = set(), set(), set(), set(), set()
    for row in rows:
        for item in row.get("coverage") or []:
            if item.get("cut_label"):
                cuts.add(item["cut_label"])
            if item.get("source_family"):
                families.add(item["source_family"])
        for item in row.get("quality") or []:
            rights.add(item.get("right") or "unknown")
            dtes.add(item.get("dte_bucket") or "unknown")
            if item.get("source_family"):
                families.add(item["source_family"])
        for key in row.get("slices") or {}:
            fam, cut, right, dte = key.split("|")
            cuts.add(cut)
            families.add(fam)
            rights.add(right)
            dtes.add(dte)
            combos.add((cut, fam, right, dte))
    return cuts, families, rights, dtes, combos


def _bundle_for(chain_rows, dates, *, family, cut, right, dte, cfg, histograms=None):
    coverage = []
    quality = []
    support = []
    paired = {}
    for row in chain_rows:
        if row["request_date"] not in dates:
            continue
        coverage.extend(row.get("coverage") or [])
        quality.extend(row.get("quality") or [])
        for item in row.get("support") or []:
            support.append({**item, "request_date": row["request_date"]})
        if cut not in (None, "all"):
            by_cut = row.get("paired_by_cut") or {}
            if cut in by_cut:
                paired[row["request_date"]] = by_cut[cut]
        elif row.get("paired_near_broad"):
            paired[row["request_date"]] = row["paired_near_broad"]
    slices_by_date = {
        row["request_date"]: row.get("slices") or {}
        for row in chain_rows if row["request_date"] in dates
    }
    use_slices = right not in (None, "all") or dte not in (None, "all")
    cov = _coverage_maps(coverage, family=family, cut=cut) if not use_slices else None
    slc = _slice_maps(slices_by_date, family=family, cut=cut, right=right, dte=dte) if use_slices else None
    qual = _quality_maps(quality, family=family, right=right, dte=dte)
    sup = _support_maps(support, cut=cut)
    pair = _paired_maps(paired) if family in (None, "all", "union") and right in (None, 'all') and dte in (None, 'all') else None
    metrics, events, raw_means, extras = _merge_maps(cov, slc, qual, sup, pair)
    for name in ("usable_quotes", "quoted_contracts", "quoted_listed", "listed_contracts"):
        if name in extras:
            metrics[name] = extras[name]
            events[name] = extras[name]
    raw_q = {}
    histograms = histograms or HistogramUniverse(chain_rows, dates, cfg['quantiles'])
    for metric, spec in HIST_FOR_METRIC.items():
        hist_name, population = spec
        raw_q[metric], (total, n) = histograms.summary(
            hist_name, population, family, cut, right, dte)
        if population in ('raw_source', 'unique_source'):
            totals = histograms.daily_totals(hist_name, population, family, right, dte)
            for row in chain_rows:
                day = row['request_date']
                if day not in dates:
                    continue
                total_day, nday = totals.get(day, (0.0, 0))
                metrics[metric][day] = None if not nday else total_day / nday
                events[metric][day] = nday
        if metric not in raw_means and n:
            raw_means[metric] = raw_mean(total, n)
    selected = {name: metrics[name] for name in PRESPECIFIED if name in metrics}
    selected.update({name: metrics[name] for name in extras})
    return selected, events, raw_means, raw_q


def build_group_statistics(date_aggregates, *, protocol, intended_all, chains, stages,
                           selected_dates=None):
    cfg = _cfg(protocol)
    dates_all = list(selected_dates or intended_all)
    years = sorted({label[:4] for label in dates_all})
    groups = {}
    for chain in chains:
        chain_rows = [row for row in date_aggregates if row["chain"] == chain]
        universes = [("all_period", dates_all)]
        for year in years:
            universes.append((f"year_{year}", [day for day in dates_all if day.startswith(year)]))
        for stage in stages:
            universes.append((f"stage_{stage}", universe_dates(dates_all, stage=stage, stages=stages)))
        cuts, families, rights, dtes, combos = _observed(chain_rows)
        targets = {("all", "all", "all", "all")}
        for cut in cuts:
            targets.add((cut, "all", "all", "all"))
        for family in families:
            targets.add(("all", family, "all", "all"))
        for right in rights:
            targets.add(("all", "all", right, "all"))
        for dte in dtes:
            targets.add(("all", "all", "all", dte))
        for family in families:
            for right in rights:
                targets.add(("all", family, right, "all"))
            for dte in dtes:
                targets.add(("all", family, "all", dte))
        for cut in cuts:
            for family in families:
                targets.add((cut, family, "all", "all"))
        for cut, family, right, dte in combos:
            targets.add((cut, family, right, dte))
        universe_cache = {}
        for uname, udates in universes:
            if not udates:
                groups[_group_key(chain, uname, "all", "all", "all", "all")] = {
                    "group": {"chain": chain, "universe": uname, "cut": "all",
                              "source_family": "all", "right": "all", "dte": "all"},
                    "statistics": {
                        "schema": "observed-date-statistics-v1",
                        "intended_dates": [], "intended_date_count": 0,
                        "metrics": {name: empty_metric([]) for name in PRESPECIFIED},
                        "ratios": {name: empty_ratio([], pair[0], pair[1]) for name, pair in RATIO_SPECS.items()},
                        "all_values_missing": True,
                    },
                }
                continue
            date_key = tuple(udates)
            duplicate = any(key[0] == date_key for key in universe_cache)
            histograms = None if duplicate else HistogramUniverse(chain_rows, set(udates), cfg['quantiles'])
            emit = targets
            for cut, family, right, dte in sorted(emit):
                cache_key = (tuple(udates), cut, family, right, dte)
                summary = universe_cache.get(cache_key)
                if summary is None:
                    metrics, events, raw_means, raw_q = _bundle_for(
                        chain_rows, set(udates), family=family, cut=cut, right=right, dte=dte, cfg=cfg,
                        histograms=histograms)
                    summary = _summarize(metrics, udates, cfg, ratios=RATIO_SPECS,
                        event_counts=events, raw_means=raw_means, raw_quantiles=raw_q)
                    universe_cache[cache_key] = summary
                groups[_group_key(chain, uname, cut, family, right, dte)] = {
                    "group": {"chain": chain, "universe": uname, "cut": cut,
                              "source_family": family, "right": right, "dte": dte},
                    "statistics": summary,
                }
            del histograms
    return groups, cfg


def _fmt(value):
    if value is None:
        return "undefined"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _md_cell(value):
    return str(value).replace("|", "\\|")


def write_results_md(outputs, *, protocol, groups, cfg, counts, selected_dates, output_refs=None,
                     chain_group_refs=None):
    group_items = (iter_group_statistics({'refs': {'chain_groups': chain_group_refs}})
                   if chain_group_refs else iter(sorted(groups.items())))
    lines = [
        "# Options quote quality / support",
        "",
        f"Family: `{protocol.get('family')}`",
        f"Statistics version: `{VERSION}`",
        "Scope: acquired quote-minute quality, coverage, ages and underlier/rate/action support.",
        "IV, Greeks and surfaces are not computed.",
        "causal_feature_eligible is FALSE. received_at, published_at, known_at and last_actual_update are NULL.",
        "actual update age is unknown. Missing, invalid and conflicting quotes are never treated as prices.",
        "The scientific family is not complete from this execution alone.",
        "",
        "Full metric tables for every constructed group are written below and in the streamed "
        "`groups-*.json` artifacts. This report is not a 10-metric subset.",
        "",
        "## Accounting",
        "",
        f"- source files read: {counts.get('source_files_read')}",
        f"- raw quotation rows: {counts.get('source_rows_read')}",
        f"- unique timestamps / events: {counts.get('unique_events')}",
        f"- cut-board rows: {counts.get('cut_board_rows')}",
        f"- listed contracts (observed): {counts.get('listed_contracts')}",
        f"- quoted contracts: {counts.get('quoted_contracts')}",
        f"- OI-matched contracts: {counts.get('oi_matched_contracts')}",
        f"- support files read: {counts.get('support_files_read')}",
        f"- support rows: {counts.get('support_rows_read')}",
        f"- independent intended dates in this selection: {len(selected_dates or [])}",
        f"- intended chain-date units: {counts.get('intended_chain_date_units')}",
        "",
        "Classes are complete, censored or missing as labeled. Absence is not zero.",
        f"Moving-block bootstrap: {cfg['replicates']} replicates, block length {cfg['block_length']}, "
        f"seed {cfg['seed']}, {cfg['confidence']} interval. Sparse if fewer than "
        f"{cfg['minimum_dates']} independent dates or {cfg['minimum_events']} events.",
        "",
        "## Streamed references",
        "",
    ]
    if output_refs:
        for name, ref in output_refs.items():
            lines.append(f"- `{name}`: `{_md_cell(ref)}`")
        lines.append("")
    lines.extend([
        "## Groups",
        "",
        f"Group count: {counts['group_count']}.",
        "",
    ])
    stream = outputs.create('results.md')
    stream.write(('\n'.join(lines) + '\n').encode())
    lines.clear()
    for name, block in group_items:
        stats = block.get("statistics") or {}
        metrics = stats.get("metrics") or {}
        lines.append(f"### `{_md_cell(name)}`")
        lines.append("")
        lines.append(f"- intended dates: {stats.get('intended_date_count')}")
        lines.append(f"- all values missing: {_fmt(stats.get('all_values_missing'))}")
        for metric in PRESPECIFIED:
            payload = metrics.get(metric)
            if not payload:
                continue
            support = payload.get("support") or {}
            boot = payload.get("bootstrap") or {}
            lines.append(
                f"- `{metric}` date-mean={_fmt(payload.get('estimate'))} "
                f"raw-mean={_fmt(payload.get('raw_mean'))} "
                f"dates={payload.get('actual_valid_date_count')} "
                f"events={payload.get('actual_valid_event_count')} "
                f"missing={payload.get('missing_date_count')} "
                f"units={_fmt(payload.get('units'))} "
                f"sparse={_fmt(support.get('sparse'))}"
            )
            if boot:
                lines.append(
                    f"  - bootstrap {_fmt(boot.get('confidence'))} "
                    f"[{_fmt(boot.get('lower'))}, {_fmt(boot.get('upper'))}] "
                    f"valid_replicates={boot.get('valid_replicates')} "
                    f"method={_fmt(boot.get('method'))}"
                )
            reasons = support.get("reasons") or []
            if payload.get("estimate") is None or reasons:
                why = reasons or ["undefined"]
                lines.append(f"  - undefined/sparse reasons: {', '.join(str(item) for item in why)}")
            q = payload.get("date_quantiles") or {}
            if q and any(value is not None for value in q.values()):
                parts = ", ".join(f"q{level}={_fmt(value)}" for level, value in q.items())
                lines.append(f"  - date quantiles: {parts}")
            rq = payload.get("raw_quantiles") or {}
            if rq and any(value is not None for value in rq.values()):
                parts = ", ".join(f"q{level}={_fmt(value)}" for level, value in rq.items())
                lines.append(f"  - raw quantiles: {parts}")
        ratios = stats.get("ratios") or {}
        for name, payload in ratios.items():
            boot = payload.get("bootstrap") or {}
            lines.append(
                f"- ratio `{name}`={_fmt(payload.get('estimate'))} "
                f"{payload.get('numerator')}/{payload.get('denominator')} "
                f"dates={payload.get('actual_valid_date_count')}"
            )
            if boot:
                lines.append(
                    f"  - bootstrap [{_fmt(boot.get('lower'))}, {_fmt(boot.get('upper'))}]"
                )
            reasons = (payload.get("support") or {}).get("reasons") or []
            if payload.get("estimate") is None or reasons:
                lines.append(f"  - undefined/sparse reasons: {', '.join(str(item) for item in reasons) or 'undefined'}")
        lines.append("")
        stream.write(('\n'.join(lines) + '\n').encode())
        lines.clear()
    lines.append(f"Statistics version: {VERSION}")
    lines.append("")
    stream.write(('\n'.join(lines)).encode())
    stream.close()
    return outputs.reference("results.md", kind="options_quote_results_md_v1")


def load_group_statistics(result):
    """Materialize small results on explicit caller request."""
    return dict(iter_group_statistics(result))


def iter_group_statistics(result):
    """Authenticate and release each chain file before loading the next."""
    from trading_research.operations.artifacts import file_digest
    refs = (result.get("refs") or {}).get("chain_groups") or {}
    if isinstance(refs, dict):
        for ref in refs.values():
            if isinstance(ref, dict) and ref.get("path"):
                path = Path(ref['path'])
                if path.stat().st_size != ref['size_bytes'] or file_digest(path) != ref['sha256']:
                    raise IntegrityError('quote statistics artifact changed')
                from trading_research.research.auction_flow_storage import read_json_artifact
                payload = read_json_artifact(ref)
                if isinstance(payload, dict):
                    yield from payload.items()
                del payload
    if result.get("groups"):
        yield from result['groups'].items()


def run_statistics(date_aggregates, *, protocol, outputs, intended_all, selected_dates, chains, stages,
                   read_counts=None, output_refs=None, group_refs=None):
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError("registered BoundedOutputs required")
    if type(date_aggregates) is not list:
        raise ContractError("date aggregates list required")
    cfg = _cfg(protocol)
    chain_group_files = {}
    dist_files = {}
    group_count = 0
    md_groups = {}
    for chain in chains:
        chain_rows = [row for row in date_aggregates if row["chain"] == chain]
        groups, cfg = build_group_statistics(
            chain_rows, protocol=protocol, intended_all=intended_all,
            chains=[chain], stages=stages, selected_dates=selected_dates,
        )
        group_count += len(groups)
        chain_group_files[chain] = outputs.json_compressed(
            f"groups-{chain.lower()}.json.zst", groups, kind="options_quote_chain_groups_v1",
            measurement_fast_path=True)
        dist_files[chain] = outputs.json(
            f"distributions-{chain.lower()}.json",
            {
                "kind": "options_quote_date_distributions_v1",
                "quantiles": list(cfg["quantiles"]),
                "groups": {name: {
                    metric: {
                        "date_quantiles": payload.get("date_quantiles"),
                        "raw_quantiles": payload.get("raw_quantiles"),
                    }
                    for metric, payload in (block["statistics"].get("metrics") or {}).items()
                } for name, block in groups.items()},
            },
            kind="options_quote_distributions_v1",
        )
        if len(chains) == 1:
            md_groups = groups
        else:
            del groups
    counts = {
        "group_count": group_count,
        "source_files_read": None if not read_counts else read_counts.get("source_files_read"),
        "source_rows_read": None if not read_counts else read_counts.get("source_rows_read"),
        "source_bytes_read": None if not read_counts else read_counts.get("source_bytes_read"),
        "support_files_read": None if not read_counts else read_counts.get("support_files_read"),
        "support_rows_read": None if not read_counts else read_counts.get("support_rows_read"),
        "support_bytes_read": None if not read_counts else read_counts.get("support_bytes_read"),
        "cut_board_rows": None if not read_counts else read_counts.get("cut_board_rows"),
        "unique_events": None if not read_counts else read_counts.get("unique_events"),
        "listed_contracts": None if not read_counts else read_counts.get("listed_contracts"),
        "quoted_contracts": None if not read_counts else read_counts.get("quoted_contracts"),
        "oi_matched_contracts": None if not read_counts else read_counts.get("oi_matched_contracts"),
        "source_files_unique": None if not read_counts else read_counts.get("source_files_unique"),
        "support_files_unique": None if not read_counts else read_counts.get("support_files_unique"),
        "intended_chain_date_units": (
            read_counts.get("intended_chain_date_units") if read_counts
            else (None if selected_dates is None else len(selected_dates) * len(chains))
        ),
    }
    stats_payload = {
        "kind": VERSION,
        "configuration": cfg,
        "full_family_complete": False,
        "group_count": group_count,
        "chain_group_refs": chain_group_files,
        "partition_group_refs": group_refs,
        "note": "Complete metric tables are in groups-*.json; iterate with load_group_statistics.",
    }
    stats_ref = outputs.json("statistics.json", stats_payload, kind="options_quote_statistics_v1")
    dist_ref = outputs.json("distributions.json", {
        "kind": "options_quote_date_distributions_v1",
        "quantiles": list(cfg["quantiles"]),
        "note": "Date quantiles are equal-date. Raw quantiles use exact typed histograms or rank interpolation.",
        "parts": dist_files,
        "group_count": group_count,
    }, kind="options_quote_distributions_v1")
    md_ref = write_results_md(
        outputs, protocol=protocol, groups=md_groups, cfg=cfg,
        counts=counts, selected_dates=selected_dates, output_refs=output_refs,
        chain_group_refs=chain_group_files,
    )
    return {"refs": {"statistics": stats_ref, "distributions": dist_ref, "results_md": md_ref,
                     "chain_groups": chain_group_files},
            "groups": None, "configuration": cfg, "group_count": group_count}


def write_date_aggregates(outputs, rows):
    parts = []
    for ordinal, row in enumerate(rows):
        row = freeze_date_aggregate(outputs, row, ordinal)
        part = outputs.json_compressed(f'date-aggregate-{ordinal:05d}.json.zst', row,
            kind='options_quote_date_aggregate_v1', measurement_fast_path=True)
        parts.append({**part, 'chain':row['chain'], 'request_date':row['request_date']})
    return outputs.json('date-aggregates.json',
        {'kind':'options_quote_date_aggregate_parts_v1', 'parts':parts, 'rows':len(parts)},
        kind='options_quote_date_aggregates_v1')


def load_date_aggregates(reference, *, materialize_histograms=True):
    from trading_research.research.auction_flow_storage import read_json_artifact
    payload = read_json_artifact(reference)
    if isinstance(payload, list):
        return payload
    if payload.get('kind') != 'options_quote_date_aggregate_parts_v1':
        raise IntegrityError('invalid quote aggregate manifest')
    rows = []
    for part in payload['parts']:
        row = read_json_artifact(part)
        if row['chain'] != part['chain'] or row['request_date'] != part['request_date']:
            raise IntegrityError('quote daily aggregate identity differs')
        if materialize_histograms and 'histograms_ref' in row:
            row = {**row, 'histograms': _row_histograms(row)}
        rows.append(row)
    if len(rows) != payload['rows']:
        raise IntegrityError('quote aggregate row count differs')
    return rows


def finish_quote_outputs(
    outputs, *, spec, calendar_ref, admit_w, except_w, alias_w, board_w, quality_w,
    support_w, fred_w, action_w, ident_w, coverage_rows, date_aggregates, consumed,
    required_ids, manifest, files_read, rows_read, bytes_read, support_files,
    support_rows, support_bytes, source_dates, selected_dates, selected_chains,
    intended_all, intended_labels, chains, started_cpu, started_wall,
    reconstruction_payload, family, version, remaining, sci_hash, impl_hashes, binding,
    oi_identity, admit_id, parse_cpu, oi_support_cpu, listing_unknown_chains,
    joined_coverage_complete, max_worker_bytes, max_source_file,
    oi_listing_files_read=0, oi_listing_rows_read=0, oi_listing_bytes_read=0, phase_cpu=None,
):
    identity_refs = ident_w.finish()
    exception_refs = except_w.finish()
    alias_refs = alias_w.finish()
    admission_refs = admit_w.finish()
    board_refs = board_w.finish()
    quality_refs = quality_w.finish()
    support_refs = support_w.finish()
    fred_refs = fred_w.finish()
    action_refs = action_w.finish()
    import pyarrow.parquet as pq
    pa = __import__("pyarrow")
    from trading_research.research.options_quote_measurements import coverage_schema
    schema = coverage_schema()
    coverage_table = schema.empty_table() if not coverage_rows else pa.table(
        {field.name: [row.get(field.name) for row in coverage_rows] for field in schema},
        schema=schema,
    )
    stream = outputs.create("coverage.parquet")
    try:
        pq.write_table(coverage_table, stream, compression="zstd")
    finally:
        stream.close()
    coverage_ref = {**outputs.reference("coverage.parquet", kind="options_quote_coverage_v1"),
                    "rows": len(coverage_table)}
    aggregates_ref = write_date_aggregates(outputs, date_aggregates)
    reconstruction_ref = outputs.json("reconstruction.json", reconstruction_payload,
                                      kind=reconstruction_payload["kind"])
    manifest_ref = outputs.json("source-manifest.json", {
        "kind": "options_quote_source_path_hash_lookup_v1",
        "note": "file_id+row_index recover provenance; source bytes stay in the authenticated root",
        "files": manifest,
    }, kind="options_quote_source_manifest_v1")
    intended_units = len(selected_dates or intended_labels) * len(chains)
    unique_events = sum(int(row.get("unique_events") or 0) for row in date_aggregates)
    listed_contracts = sum(int(row.get("listed_contracts") or 0) for row in date_aggregates)
    quoted_contracts = sum(int(row.get("quoted_contracts") or 0) for row in date_aggregates)
    oi_matched = sum(int(row.get("oi_matched_contracts") or 0) for row in date_aggregates)
    output_refs = {
        "admission": admission_refs, "exceptions": exception_refs,
        "alias_conflict": alias_refs, "cut_board": board_refs,
        "source_quality": quality_refs, "underlier_support": support_refs,
        "fred_support": fred_refs, "action_support": action_refs,
        "identity_match": identity_refs, "coverage": coverage_ref,
        "reconstruction": reconstruction_ref, "source_manifest": manifest_ref,
    }
    statistics_start_cpu = pytime.process_time()
    statistics_start_output = outputs.written
    production_cpu_seconds = statistics_start_cpu - started_cpu
    pools = {row['pooled_histograms_ref']['sha256']: row['pooled_histograms_ref']
             for row in date_aggregates if row.get('pooled_histograms_ref')}
    histogram_resources = {
        'input_bins': sum(ref['input_bins'] for ref in pools.values()),
        'pooled_bins': sum(ref['pooled_bins'] for ref in pools.values()),
        'pool_output_bytes': sum(ref['total_output_bytes'] for ref in pools.values()),
        'pool_count': len(pools),
    }
    measurement_counters_ref = outputs.json('measurement-counters.json', {
        'kind': 'options_quote_measurement_phase_counters_v1',
        'source_files_read': files_read, 'source_rows_read': rows_read,
        'source_bytes_read': bytes_read, 'support_files_read': support_files,
        'support_rows_read': support_rows, 'support_bytes_read': support_bytes,
        'production_cpu_seconds': production_cpu_seconds,
        'source_parse_dedup_board_cpu_seconds': parse_cpu,
        'oi_support_load_cpu_seconds': oi_support_cpu,
        'production_output_bytes': statistics_start_output,
        'source_phase_cpu_seconds': phase_cpu, 'histogram_resources': histogram_resources,
    }, kind='options_quote_measurement_phase_counters_v1')
    stats = run_statistics(
        date_aggregates, protocol=spec, outputs=outputs,
        intended_all=[day.isoformat() if hasattr(day, "isoformat") else day for day in intended_all],
        selected_dates=selected_dates, chains=list(chains), stages=spec["population"]["stages"],
        read_counts={
            "source_files_read": files_read, "source_rows_read": rows_read,
            "source_bytes_read": bytes_read, "intended_chain_date_units": intended_units,
            "cut_board_rows": board_w.rows, "unique_events": unique_events,
            "listed_contracts": listed_contracts, "quoted_contracts": quoted_contracts,
            "oi_matched_contracts": oi_matched,
            "support_files_read": support_files, "support_rows_read": support_rows,
            "support_bytes_read": support_bytes,
            "oi_listing_files_read": oi_listing_files_read,
            "oi_listing_rows_read": oi_listing_rows_read,
        },
        output_refs=output_refs,
    )
    cpu = pytime.process_time() - started_cpu
    wall = pytime.perf_counter() - started_wall
    refs = {
        "calendar": calendar_ref, "source_manifest": manifest_ref,
        "admission": admission_refs, "exceptions": exception_refs,
        "alias_conflict": alias_refs, "cut_board": board_refs,
        "source_quality": quality_refs, "underlier_support": support_refs,
        "fred_support": fred_refs, "action_support": action_refs,
        "identity_match": identity_refs, "coverage": coverage_ref,
        "date_aggregates": aggregates_ref, "measurement_counters": measurement_counters_ref,
        "reconstruction": reconstruction_ref,
        "statistics": stats["refs"]["statistics"], "distributions": stats["refs"]["distributions"],
        "results_md": stats["refs"]["results_md"],
        "chain_groups": stats["refs"].get("chain_groups"),
    }
    return {
        "passed": True,
        "full_family_complete": False,
        "joined_coverage_complete": bool(joined_coverage_complete),
        "family": family,
        "version": version,
        "protocol_scientific_hash": sci_hash,
        "implementation_hashes": impl_hashes,
        "selected_dates": selected_dates,
        "selected_chains": list(selected_chains),
        "admitted_identity": {
            "kind": binding.get("admitted_kind"),
            "source_files": binding.get("admitted_source_files"),
            "digest": admit_id,
        },
        "oi_population_identity": oi_identity,
        "refs": refs,
        "counts": {
            "source_files_read": files_read, "source_rows_read": rows_read,
            "source_bytes_read": bytes_read, "intended_chain_date_units": intended_units,
            "coverage_rows": len(coverage_table), "cut_board_rows": board_w.rows,
            "exception_rows": except_w.rows, "alias_conflict_rows": alias_w.rows,
            "identity_rows": ident_w.rows, "unique_events": unique_events,
            "listed_contracts": listed_contracts, "quoted_contracts": quoted_contracts,
            "oi_matched_contracts": oi_matched,
            "support_files_read": support_files, "support_rows_read": support_rows,
            "support_bytes_read": support_bytes,
            "oi_listing_files_read": oi_listing_files_read,
            "oi_listing_rows_read": oi_listing_rows_read,
            "oi_listing_bytes_read": oi_listing_bytes_read,
            "alias_conflict_rows": alias_w.rows, "identity_rows": ident_w.rows,
            "listing_unknown_chains": listing_unknown_chains, "chains": list(chains),
        },
        "resources": {
            "cpu_seconds": cpu, "wall_seconds": wall, "output_bytes": outputs.written,
            "source_parse_dedup_board_cpu_seconds": parse_cpu,
            "source_phase_cpu_seconds": phase_cpu,
            "histogram_resources": histogram_resources,
            "oi_support_load_cpu_seconds": oi_support_cpu,
            "statistics_cpu_seconds": pytime.process_time() - statistics_start_cpu,
            "fixture_cpu_seconds": 0.0,
            "production_cpu_seconds": production_cpu_seconds,
            "production_output_bytes": statistics_start_output,
            "statistics_output_bytes": outputs.written - statistics_start_output,
            "source_bytes_read": bytes_read, "source_files_read": files_read,
            "source_rows_read": rows_read, "intended_chain_date_units": intended_units,
            "memory_bound_bytes": max_worker_bytes, "source_file_bound_bytes": max_source_file,
            "full_gate_projection": "computed by registered supervisor from admitted full rows/files/dates and measured pilot; not inferred from this selection",
        },
        "source_dates_processed": sorted(set(source_dates)),
        "remaining_dependencies": list(remaining),
        "groups": None,
        "clock_interpretation": {
            "ts_event_ns": "exact recorded sampling/source clock",
            "known_at_ns": None, "received_at_ns": None, "published_at_ns": None,
            "last_actual_update_ns": None, "causal_feature_eligible": False,
            "actual_update_age_unknown": True,
            "reconstruction": reconstruction_payload.get("predicate"),
        },
    }


__all__ = [
    "VERSION", "PRESPECIFIED", "build_group_statistics", "date_balanced_point",
    "date_quantiles", "empty_metric", "empty_ratio", "exact_quantiles_from_histogram",
    "exact_quantiles_from_values", "finish_quote_outputs", "iter_group_statistics",
    "load_group_statistics", "raw_mean",
    "run_statistics", "universe_dates",
]
