"""Causal, complete-population OHLC research tables for disclosed source clocks.

Each intended cash date/clock survives unavailable formation or future data.
Prices are raw-contract quarter-point ticks. An OHLC open is available only
when its containing minute bar is published. No future open enters a feature.
The source-specific mechanism payload is kept beside the common path targets;
the latter does not certify an undisclosed or different source mechanism.
"""
from __future__ import annotations

from bisect import bisect_left
from collections import deque
from datetime import date, time, timedelta
from fractions import Fraction
import json
from statistics import median

from trading_research.errors import ContractError
from trading_research.foundations.calendar import local_timestamp
from trading_research.operations.artifacts import digest
from trading_research.research.ohlc_ranges import (
    MINUTE, MinuteBars, OhlcWindow, range_path, wall_endpoint, wall_interval,
)

VERSION = "jumbo-causal-date-tables-v1"
FEATURES = (
    "width_ticks", "formation_minutes", "log_volume", "open_position",
    "close_position", "body_fraction", "up_fraction", "down_fraction",
    "last_close_position", "last_close_age_minutes", "weekday", "month",
    "cut_ny_minutes", "early_close", "prior_width_ticks", "width_prior_ratio",
    "last_close_in_prior_position", "prior_last_close_displacement_ticks", "observed_cash_open_gap_ticks", "prior_age_minutes",
    "prior_5_mean_width_ticks", "prior_20_mean_width_ticks",
    "asia_width_ratio", "asia_price_overlap_fraction", "asia_shared_time_fraction",
    "asia_last_close_position", "morning_width_ratio", "morning_price_overlap_fraction",
    "morning_shared_time_fraction", "morning_last_close_position",
    "opening_width_ratio", "opening_price_overlap_fraction", "opening_shared_time_fraction",
    "opening_last_close_position", "prefix_minutes", "prefix_upper_breach",
    "prefix_lower_breach", "prefix_up_W", "prefix_down_W", "prefix_return_W",
    "prefix_order_ambiguous", "activity_threshold", "activity_reference_dates",
)
PATH_NUMBERS = (
    "label_origin_open_ticks", "terminal_ticks", "maximum_up_ticks", "maximum_down_ticks",
    "upper_overshoot_ticks", "lower_overshoot_ticks", "first_interval_start_ns",
    "first_interval_end_ns", "second_interval_start_ns", "second_interval_end_ns",
    "close_confirmed_reclaim_at_ns", "reclaim_known_at_ns", "maturity_at_ns",
    "first_lower_minutes", "first_upper_minutes", "second_lower_minutes", "second_upper_minutes",
    "maximum_up_W", "maximum_down_W", "terminal_W", "remaining_range_W",
    "upper_overshoot_W", "lower_overshoot_W", "squared_close_returns_ticks2",
    "prefix_first_lower_minutes", "prefix_first_upper_minutes", "prefix_maturity_at_ns",
)
PATH_FLAGS = (
    "upper_breach", "lower_breach", "both_breach", "no_breach", "reclaim_observed",
    "inclusive_upper_reach", "inclusive_lower_reach", "inclusive_both_reach",
    "prefix_upper_breach", "prefix_lower_breach", "prefix_both_breach",
)


def table_schema(kind):
    """Fixed nullable Arrow types survive all-missing years and first rows."""
    import pyarrow as pa
    types = {}
    def add(names, dtype):
        for name in names:
            if name in types:
                raise ContractError("duplicate research table schema field")
            types[name] = dtype
    if kind == "formations":
        add(("date", "clock", "definition", "source_ids", "variant_role", "source_version", "window_version",
             "cash_state", "contract_key", "status", "exclusion_reasons", "formation_id", "root"), pa.string())
        add(("year", "formation_start_ns", "formation_end_ns", "origin_ns", "available_at_ns", "calendar_known_at_ns",
             "cash_close_ns", "expected_minutes", "observed_minutes", "open_ticks", "high_ticks", "low_ticks", "close_ticks",
             "width_ticks", "volume", "formation_up_ticks", "formation_down_ticks", "activity_reference_dates",
             "activity_threshold_numerator", "activity_threshold_denominator"), pa.int64())
        add(("body25_ticks", "lower_body25_ticks", "wick_quarter_ticks", "open_position", "activity_threshold"), pa.float64())
        add(("zero_width",), pa.bool_())
    elif kind == "paths":
        add(("date", "root", "clock", "formation_id", "horizon", "status", "path", "inclusive_path", "first_side",
             "prefix_path", "prefix_first_side", "exclusion_reasons", "contract_key", "label_version", "row_id", "prefix_input_status"), pa.string())
        add(("year", "origin_ns", "endpoint_ns", "planned_minutes", "observed_prefix_minutes"), pa.int64())
        add(("zero_width", *PATH_FLAGS), pa.bool_())
        integer_values = {name for name in PATH_NUMBERS if name.endswith("_ns") or name.endswith("_ticks") or name == "squared_close_returns_ticks2"}
        add(integer_values, pa.int64())
        add((name for name in PATH_NUMBERS if name not in integer_values), pa.float64())
    elif kind == "specials":
        add(("date", "root", "clock", "formation_id", "payload"), pa.string())
        add(("year",), pa.int64())
    else:
        raise ContractError("unknown research table kind")
    if kind in ("formations", "paths"):
        add(("x_" + name for name in FEATURES), pa.float64())
    return pa.schema([(name, types[name]) for name in sorted(types)])


def cash_dates(calendar, first: date, last: date):
    """Resolve the cash-date population using facts known by each civil midnight."""
    result = []
    day = first
    while day <= last:
        cash = calendar.resolve(day, cut=local_timestamp(day, time(0), calendar.zone))
        if cash.state != "closed":
            result.append(cash)
        day += timedelta(days=1)
    return tuple(result)


def _ceil_minute(at):
    return ((at + MINUTE - 1) // MINUTE) * MINUTE


def _available(window):
    if not window.complete:
        return None
    return window.available_at_ns


def observed_prefix(window: OhlcWindow, *, available_cut: int):
    """Longest observed contiguous prefix in the original raw coordinate.

    The complete-window target stays censored if any later minute is absent.
    An event already observed in this prefix still contributes to the duration
    risk set, with a one-minute event-time interval.
    """
    if window.observation_cut_ns is not None:
        available_cut = min(available_cut, window.observation_cut_ns)
    s = window.series
    end = window.start
    contract = None
    for i in range(window.left, window.right):
        if (s.start[i] != end or s.bad[i + 1] != s.bad[i]
                or s.known[i] > available_cut):
            break
        if contract is None:
            contract = s.contract[i]
        if s.contract[i] != contract:
            break
        end = s.end[i]
    if end == window.start:
        return None
    prefix = s.window(window.start, end, contract_key=window.contract_key, available_at=available_cut)
    # A differently requested coordinate is recorded in the parent reasons;
    # it cannot supply even a partial path in that coordinate.
    if "different_raw_contract" in window.reasons or not prefix.complete:
        return None
    return prefix


def _summary(window, *, origin, cash, recipe, source_version):
    summary = window.summary()
    row = {
        "date": cash.day.isoformat(), "year": cash.day.year, "clock": recipe["id"],
        "definition": recipe["output_definition"], "source_ids": ";".join(recipe["source_ids"]),
        "variant_role": recipe.get("variant_role", "source_or_explicit_corrected_recipe"),
        "source_version": source_version, "window_version": summary["window_version"],
        "formation_start_ns": window.start, "formation_end_ns": window.end,
        "origin_ns": origin, "available_at_ns": None, "calendar_known_at_ns": cash.known_at,
        "cash_close_ns": cash.close_at, "cash_state": cash.state,
        "contract_key": window.contract_key, "status": summary["status"],
        "exclusion_reasons": ";".join(summary["exclusion_reasons"]),
        "expected_minutes": window.expected_minutes, "observed_minutes": window.count,
        "open_ticks": None, "high_ticks": None, "low_ticks": None, "close_ticks": None,
        "width_ticks": None, "volume": None, "body25_ticks": None,
        "lower_body25_ticks": None, "wick_quarter_ticks": None, "open_position": None,
        "formation_up_ticks": None, "formation_down_ticks": None, "zero_width": None,
        "activity_threshold": recipe.get("activity_threshold"),
        "activity_threshold_numerator": recipe.get("activity_threshold_numerator"),
        "activity_threshold_denominator": recipe.get("activity_threshold_denominator"),
        "activity_reference_dates": recipe.get("activity_reference_dates"),
    }
    if window.complete:
        row.update({k: summary[k] for k in row if k in summary and k not in ("exclusion_reasons",)})
        row["available_at_ns"] = max(summary["available_at_ns"], cash.known_at)
    row["formation_id"] = digest((VERSION, recipe, source_version, cash.version, window.version))
    return row


def _relation(features, name, target, other, *, origin, last_close):
    if (other is None or not other.complete or other.contract_key != target.contract_key
            or _available(other) > origin):
        return
    a, b = target.geometry(), other.geometry()
    if not a.usable or not b.usable:
        return
    features[name + "_width_ratio"] = float(b.width / a.width)
    features[name + "_price_overlap_fraction"] = float(max(Fraction(0), min(a.high, b.high) - max(a.low, b.low)) / a.width)
    features[name + "_shared_time_fraction"] = max(0, min(target.end, other.end) - max(target.start, other.start)) / (target.end - target.start)
    if last_close is not None:
        features[name + "_last_close_position"] = float(b.normalized_position(last_close))


def features_at(window, *, origin, cash, prior, prior_widths, anchors, recipe, prefix=None):
    import math
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    features = dict.fromkeys(FEATURES)
    stamp = datetime.fromtimestamp(origin // 1_000_000_000, timezone.utc).astimezone(ZoneInfo("America/New_York"))
    features.update(weekday=cash.day.weekday(), month=cash.day.month,
                    cut_ny_minutes=stamp.hour * 60 + stamp.minute,
                    early_close=int(cash.state == "early_close"), prefix_minutes=0 if prefix is None else None,
                    activity_threshold=recipe.get("activity_threshold"),
                    activity_reference_dates=recipe.get("activity_reference_dates"))
    if not window.complete or _available(window) > origin:
        return {"x_" + k: v for k, v in features.items()}
    s, g = window.series, window.geometry()
    features.update(width_ticks=int(g.width), formation_minutes=window.expected_minutes,
                    log_volume=math.log1p(window.volume))
    if g.usable:
        features.update(open_position=float(g.normalized_position(g.open)),
                        close_position=float(g.normalized_position(g.close)),
                        body_fraction=float((g.close - g.open) / g.width),
                        up_fraction=float((g.high - g.open) / g.width),
                        down_fraction=float((g.open - g.low) / g.width))
    # Every admitted bar has the declared end-plus-one-minute availability.
    # The last known close is a feature; the future origin open is a label.
    latest = s.window(origin - 2 * MINUTE, origin - MINUTE,
                      contract_key=window.contract_key, available_at=origin)
    last_close = s.close[latest.right - 1] if latest.complete else int(g.close)
    last_time = latest.end if latest.complete else window.end
    features["last_close_age_minutes"] = (origin - last_time) / MINUTE
    if g.usable:
        features["last_close_position"] = float(g.normalized_position(last_close))
    usable_prior = (prior is not None and prior.complete and prior.contract_key == window.contract_key
                    and _available(prior) <= origin)
    if usable_prior:
        pg = prior.geometry()
        features.update(prior_width_ticks=int(pg.width), prior_last_close_displacement_ticks=last_close - int(pg.close),
                        prior_age_minutes=(origin - prior.end) / MINUTE)
        cash_open = s.window(cash.open_at, cash.open_at + MINUTE, contract_key=window.contract_key, available_at=origin)
        if cash_open.complete:
            features["observed_cash_open_gap_ticks"] = s.open[cash_open.left] - int(pg.close)
        if pg.usable:
            features.update(width_prior_ratio=float(g.width / pg.width),
                            last_close_in_prior_position=float(pg.normalized_position(last_close)))
    # Historical scales are from completed prior cash sessions in this raw
    # coordinate only. Missing earlier sessions remain missing in the deque.
    for length in (5, 20):
        recent = tuple(prior_widths)[-length:]
        if len(recent) == length and all(v is not None and v[0] == window.contract_key and v[2] <= origin for v in recent):
            features[f"prior_{length}_mean_width_ticks"] = sum(v[1] for v in recent) / length
    for name, other in anchors.items():
        _relation(features, name, window, other, origin=origin, last_close=last_close)
    if prefix is not None and prefix.complete and _available(prefix) <= origin and prefix.contract_key == window.contract_key and g.usable:
        p = range_path(prefix, low=int(g.low), high=int(g.high))
        features.update(prefix_minutes=prefix.expected_minutes,
                        prefix_upper_breach=int(p["upper_reached"]), prefix_lower_breach=int(p["lower_reached"]),
                        prefix_order_ambiguous=int(p["first_side"] == "ambiguous"),
                        prefix_up_W=p["maximum_up_ticks"] / int(g.width),
                        prefix_down_W=p["maximum_down_ticks"] / int(g.width),
                        prefix_return_W=p["terminal_ticks"] / int(g.width))
    return {"x_" + k: None if v is None else float(v) for k, v in features.items()}


def path_row(formation, *, origin, endpoint, horizon, features, available_cut, root):
    row, window = formation
    result = {"date": row["date"], "year": row["year"], "root": root,
              "clock": row["clock"], "formation_id": row["formation_id"], "horizon": horizon,
              "origin_ns": origin, "endpoint_ns": endpoint,
              "planned_minutes": max(0, (endpoint - origin) // MINUTE),
              "status": "censored", "path": "censored", "inclusive_path": "censored",
              "first_side": None, "prefix_path": None, "prefix_first_side": None,
              "exclusion_reasons": row["exclusion_reasons"], "observed_prefix_minutes": 0,
              "contract_key": row["contract_key"], "zero_width": row["zero_width"],
              "label_version": VERSION, **dict.fromkeys(PATH_NUMBERS),
              **dict.fromkeys(PATH_FLAGS), **features}
    result["row_id"] = digest((row["formation_id"], origin, endpoint, horizon))
    if not window.complete or row["available_at_ns"] > origin:
        result["exclusion_reasons"] = row["exclusion_reasons"] or "formation_not_available_at_cut"
        return result
    if endpoint <= origin:
        result["exclusion_reasons"] = "empty_remaining_horizon"
        return result
    if row["zero_width"]:
        result.update(status="zero_width", path="zero_width", inclusive_path="zero_width")
        result["exclusion_reasons"] = "undefined_width_normalized_path"
        return result
    future = window.series.window(origin, endpoint, contract_key=window.contract_key, available_at=available_cut)
    strict = range_path(future, low=row["low_ticks"], high=row["high_ticks"])
    result.update(status=strict["status"], path=strict["path"],
                  exclusion_reasons=";".join(strict["exclusion_reasons"]))
    prefix = future if future.complete else observed_prefix(future, available_cut=available_cut)
    if prefix is not None:
        p = strict if future.complete else range_path(prefix, low=row["low_ticks"], high=row["high_ticks"])
        result.update(observed_prefix_minutes=prefix.expected_minutes, prefix_path=p["path"],
                      prefix_first_side=p["first_side"], prefix_maturity_at_ns=p["maturity_at_ns"],
                      prefix_upper_breach=p["upper_reached"], prefix_lower_breach=p["lower_reached"],
                      prefix_both_breach=p["upper_reached"] and p["lower_reached"])
        if p["first_interval_start_ns"] is not None:
            result["prefix_first_lower_minutes"] = (p["first_interval_start_ns"] - origin) / MINUTE
            result["prefix_first_upper_minutes"] = (p["first_interval_end_ns"] - origin) / MINUTE
    if not future.complete:
        return result
    inclusive = range_path(future, low=row["low_ticks"], high=row["high_ticks"], strict=False)
    result.update({k: strict[k] for k in PATH_NUMBERS if k in strict})
    result.update(first_side=strict["first_side"], inclusive_path=inclusive["path"],
                  upper_breach=strict["upper_reached"], lower_breach=strict["lower_reached"],
                  both_breach=strict["upper_reached"] and strict["lower_reached"],
                  no_breach=not (strict["upper_reached"] or strict["lower_reached"]),
                  reclaim_observed=None if strict["first_side"] == "ambiguous" else strict["close_confirmed_reclaim_at_ns"] is not None,
                  inclusive_upper_reach=inclusive["upper_reached"], inclusive_lower_reach=inclusive["lower_reached"],
                  inclusive_both_reach=inclusive["upper_reached"] and inclusive["lower_reached"])
    width = row["width_ticks"]
    for source, target in (("maximum_up_ticks", "maximum_up_W"), ("maximum_down_ticks", "maximum_down_W"),
                           ("terminal_ticks", "terminal_W"), ("upper_overshoot_ticks", "upper_overshoot_W"),
                           ("lower_overshoot_ticks", "lower_overshoot_W")):
        result[target] = strict[source] / width
    result["remaining_range_W"] = (strict["maximum_up_ticks"] + strict["maximum_down_ticks"]) / width
    for name in ("first", "second"):
        if strict[name + "_interval_start_ns"] is not None:
            result[name + "_lower_minutes"] = (strict[name + "_interval_start_ns"] - origin) / MINUTE
            result[name + "_upper_minutes"] = (strict[name + "_interval_end_ns"] - origin) / MINUTE
    s, a, b = future.series, future.left, future.right
    # Defined close-to-close tick quadratic variation; first origin-open to
    # first close is included, with interbar jumps, never called trade RV.
    result["squared_close_returns_ticks2"] = (s.close[a] - s.open[a]) ** 2 + sum((s.close[i] - s.close[i - 1]) ** 2 for i in range(a + 1, b))
    return result


def _special(window, cash, recipe, *, evaluation_cut):
    from trading_research.research.ohlc_mechanisms import (
        daily_range_outcome, magic_outcome, open_to_open_outcome, overnight_pivot, three_stage_outcome,
    )
    kind = recipe["output_definition"]
    if kind not in ("magic_break_midpoint_competing_extension_v1", "three_stage_midpoint_return_v1",
                    "open_to_open_retracement_v1", "overnight_pivot_range_v1", "source_mon_tue_daily_range_v1"):
        return None
    s, zone = window.series, recipe["local_zone"]
    kw = {"context_known_at_ns": cash.known_at}
    # All target windows retain their planned endpoints and observation cut.
    # Mechanism functions distinguish nominal source and delayed causal cuts.
    def future(a, b):
        return s.window(a, b, contract_key=window.contract_key, available_at=evaluation_cut)
    if kind == "magic_break_midpoint_competing_extension_v1":
        a, b = wall_interval(cash.day, recipe["check_local"], zone)
        return magic_outcome(window, future(a, b), invalidation=Fraction(str(recipe["invalidation_W"])), **kw)
    if kind == "three_stage_midpoint_return_v1":
        a, b = wall_interval(cash.day, recipe["conditioning_local"], zone)
        c, d = wall_interval(cash.day, recipe["forecast_local"], zone)
        return three_stage_outcome(window, future(a, b), future(c, d), **kw)
    if kind == "open_to_open_retracement_v1":
        a = wall_endpoint(cash.day, recipe["forecast_origin_local"], zone)
        b = wall_endpoint(cash.day, recipe["forecast_end_local"], zone)
        return open_to_open_outcome(window, future(a, b), p=Fraction(*recipe["p_exact"]), **kw)
    if kind == "overnight_pivot_range_v1":
        return overnight_pivot(window, variant=recipe["id"], **kw)
    if kind == "source_mon_tue_daily_range_v1":
        # The supported source keeps a daily range; the next daily interval
        # is a separately declared research horizon, never a combined week.
        return daily_range_outcome(window, future(window.end + MINUTE, window.end + 180 * MINUTE + MINUTE),
                                   date_key=cash.day.isoformat(), **kw)
    return None


def extract_dates(series: MinuteBars, dates, *, root, recipes, plan, evaluation_cut,
                  emit_first_date: date | None = None):
    """Yield bounded per-date records; reuse the same tables for all outcomes."""
    from copy import deepcopy
    if root not in ("NQ", "ES") or len(recipes) != 69:
        raise ContractError("declared root and exact 69-clock population required")
    if emit_first_date is not None and type(emit_first_date) is not date:
        raise ContractError("checkpoint continuation requires an exact civil date")
    recipe_map = {r["id"]: r for r in recipes}
    if len(recipe_map) != len(recipes):
        raise ContractError("duplicate source clock identity")
    prior = None
    prior_widths = deque(maxlen=20)
    activity_volumes = deque(maxlen=plan["activity"]["lookback_dates"])
    for cash in dates:
        day = cash.day
        if emit_first_date is not None and day < emit_first_date:
            # Reconstruct the exact causal state needed after an immutable
            # annual checkpoint. Other ranges and targets are not state
            # inputs, so recomputing their saved outcomes is unnecessary.
            prior = series.window(cash.open_at, cash.close_at, available_at=evaluation_cut)
            prior_widths.append((prior.contract_key, int(prior.geometry().width), _available(prior))
                                if prior.complete else None)
            recipe = recipe_map["OR15"]
            start, end = wall_interval(day, recipe["local"], recipe["local_zone"])
            or15 = series.window(start, end, available_at=evaluation_cut)
            activity_volumes.append(or15.volume if or15.complete else None)
            continue
        formations, paths, specials = [], [], []
        specs = []
        for recipe in recipes:
            if recipe["id"] == "PIN078_daily_not_combined" and day.weekday() not in (0, 1):
                continue
            start, end = wall_interval(day, recipe["local"], recipe["local_zone"])
            specs.append((recipe, start, end, None))
        for parent in plan["neighbor_clocks"]:
            for shift in plan["neighbor_shifts_minutes"]:
                recipe = deepcopy(recipe_map[parent])
                recipe.update(id=parent + f"__shift_{shift:+d}m", variant_role="prespecified_neighbor_clock", parent_clock=parent)
                start, end = wall_interval(day, recipe["local"], recipe["local_zone"])
                specs.append((recipe, start + shift * MINUTE, end + shift * MINUTE, None))
        actual_recipe = {"id": "RTH_actual", "output_definition": "actual_published_cash_RTH_v1", "source_ids": ["PIN083-01", "M12"], "variant_role": "actual_cash_close_comparator"}
        specs.append((actual_recipe, cash.open_at, cash.close_at, None))
        if prior is None:
            # Before the first primary cash date, no pre-2020 price is loaded.
            # Keep an unavailable explicitly bounded prior-session placeholder.
            prior_window = series.window(cash.open_at - 1440 * MINUTE, cash.close_at - 1440 * MINUTE)
            prior_window = OhlcWindow(series, prior_window.start, prior_window.end, prior_window.left,
                                      prior_window.right, prior_window.expected_minutes,
                                      ("prior_actual_cash_session_outside_primary_admitted_history",), evaluation_cut)
        else:
            prior_window = prior
        for suffix, delay in (("preopen", 0), ("open_observed", 2)):
            recipe = {"id": "prior_RTH_" + suffix, "output_definition": "prior_actual_cash_RTH_v1", "source_ids": ["JTR-21", "JTR-22", "L03", "M12"], "variant_role": "prior_actual_cash_session", "origin_delay_minutes": delay}
            specs.append((recipe, prior_window.start, prior_window.end, cash.open_at + delay * MINUTE))
        valid_activity = [v for v in activity_volumes if v is not None]
        for num, den in plan["activity"]["threshold_multiples_exact"]:
            recipe = {"id": f"OR_activity_{num}_{den}", "output_definition": "causal_rolling_volume_completed_range_v1",
                      "source_ids": ["C01"], "variant_role": "prespecified_activity_comparator",
                      "activity_reference_dates": len(valid_activity), "activity_threshold": None}
            end = cash.open_at + plan["activity"]["maximum_minutes"] * MINUTE
            if len(valid_activity) >= plan["activity"]["minimum_reference_dates"]:
                threshold = median([Fraction(v) for v in valid_activity]) * Fraction(num, den)
                recipe["activity_threshold"] = float(threshold)
                recipe["activity_threshold_numerator"] = threshold.numerator
                recipe["activity_threshold_denominator"] = threshold.denominator
                volume, expected, key = 0, cash.open_at, None
                left = bisect_left(series.start, cash.open_at)
                for i in range(left, min(len(series.start), left + plan["activity"]["maximum_minutes"])):
                    if series.start[i] != expected or series.bad[i + 1] != series.bad[i]:
                        break
                    key = series.contract[i] if key is None else key
                    if key != series.contract[i]:
                        break
                    volume += series.volume[i]
                    expected = series.end[i]
                    if volume >= threshold:
                        end = expected
                        recipe["activity_completed"] = True
                        break
            specs.append((recipe, cash.open_at, end, None))
        windows = {}
        for recipe, start, end, chosen_origin in specs:
            if recipe["id"].startswith("prior_RTH_"):
                window = prior_window
            else:
                window = series.window(start, end, available_at=evaluation_cut)
            if recipe["id"].startswith("OR_activity_") and not recipe.get("activity_completed"):
                reasons = (*window.reasons, "insufficient_prior_activity_history" if recipe["activity_threshold"] is None else "activity_threshold_not_completed_before_cap")
                window = OhlcWindow(series, start, end, window.left, window.right, window.expected_minutes, reasons, evaluation_cut)
            windows[recipe["id"]] = window
            formation_available = _available(window)
            origin = chosen_origin if chosen_origin is not None else _ceil_minute(max(cash.known_at, formation_available if formation_available is not None else end + MINUTE))
            summary = _summary(window, origin=origin, cash=cash, recipe=recipe, source_version=series.source_version)
            summary["root"] = root
            formations.append((summary, window, recipe))
        anchors = {"asia": windows["Asia20"], "morning": windows["JTR_fixed_04"], "opening": windows["OR15"]}
        for summary, window, recipe in formations:
            origin = summary["origin_ns"]
            features = features_at(window, origin=origin, cash=cash, prior=prior, prior_widths=prior_widths,
                                   anchors=anchors, recipe=recipe)
            summary.update(features)
            horizons = [(f"after_{n}m", origin + n * MINUTE) for n in plan["horizons_minutes"]]
            horizons.append(("to_actual_cash_close", cash.close_at))
            for horizon, endpoint in horizons:
                paths.append(path_row((summary, window), origin=origin, endpoint=endpoint, horizon=horizon,
                                      features=features, available_cut=evaluation_cut, root=root))
            if recipe["id"] in plan["matched_clock_comparison"]["clocks"]:
                common_cut = local_timestamp(day, time.fromisoformat(plan["matched_clock_comparison"]["origin_local"]), "America/New_York")
                matched_features = features_at(window, origin=common_cut, cash=cash, prior=prior,
                                               prior_widths=prior_widths, anchors=anchors, recipe=recipe)
                paths.append(path_row((summary, window), origin=common_cut, endpoint=cash.close_at,
                                      horizon="common_1001_to_actual_cash_close", features=matched_features,
                                      available_cut=evaluation_cut, root=root))
            if recipe["id"] in plan["prefix_clocks"]:
                for delay in plan["prefix_delays_minutes"]:
                    cut = origin + delay * MINUTE
                    prefix = series.window(origin, cut - MINUTE, contract_key=window.contract_key, available_at=cut)
                    pf = features_at(window, origin=cut, cash=cash, prior=prior, prior_widths=prior_widths,
                                     anchors=anchors, recipe=recipe, prefix=prefix)
                    value = path_row((summary, window), origin=cut, endpoint=cash.close_at,
                                     horizon=f"prefix_{delay}m_to_actual_cash_close", features=pf,
                                     available_cut=evaluation_cut, root=root)
                    value["prefix_input_status"] = "complete" if prefix.complete else "unavailable"
                    paths.append(value)
            if recipe.get("variant_role") != "prespecified_neighbor_clock":
                payload = _special(window, cash, recipe, evaluation_cut=evaluation_cut)
                if payload is not None:
                    specials.append({"date": summary["date"], "year": day.year, "root": root, "clock": recipe["id"],
                                     "formation_id": summary["formation_id"], "payload": json.dumps(payload, sort_keys=True, allow_nan=False)})
        yield {"cash_date": cash, "formations": [r for r, _, _ in formations], "paths": paths, "specials": specials}
        # Update only after every row on this cash date has been formed. Even
        # pre-open clocks never see today's completed cash range or activity.
        prior = windows["RTH_actual"]
        prior_widths.append((prior.contract_key, int(prior.geometry().width), _available(prior)) if prior.complete else None)
        or15 = windows["OR15"]
        activity_volumes.append(or15.volume if or15.complete else None)
