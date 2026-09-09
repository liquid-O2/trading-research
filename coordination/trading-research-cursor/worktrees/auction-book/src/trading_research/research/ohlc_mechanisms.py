"""Special Jumbo source mechanisms with explicit OHLC observation limits.

Target construction never requires complete future coverage. These functions
operate on supplied, versioned windows; the caller binds their source-clock
recipes. Source branch priorities are descriptive comparators, not market order.
"""
from __future__ import annotations

from datetime import date
from fractions import Fraction

from trading_research.errors import ContractError
from trading_research.research.ohlc_ranges import MINUTE, OhlcWindow, _level_observations, _level_result

VERSION = "jumbo-special-ohlc-mechanisms-v1"


def _rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _context(value):
    if type(value) is not int or value < 0:
        raise ContractError("context known-at must be an exact nonnegative nanosecond clock")


def _probability(value):
    if type(value) is not Fraction or not 0 <= value <= 1:
        raise ContractError("source retracement fraction must be exact and between zero and one")


def _window(value):
    if not isinstance(value, OhlcWindow):
        raise ContractError("an admitted OHLC window is required")


def _known(window):
    return window.available_at_ns


def _reasons(window, contract):
    reasons = list(window.reasons)
    if window.count and window.contract_key != contract and "different_raw_contract" not in reasons:
        reasons.append("different_raw_contract")
    return reasons


def _base(mechanism, formation, context_known_at_ns):
    _window(formation)
    _context(context_known_at_ns)
    result = {"mechanism": mechanism, "version": VERSION,
              "formation": formation.summary(), "candidate_available": formation.complete,
              "candidate_availability_scope": "Constructible from admitted required inputs at inputs_known_at_ns; not presumed known at nominal origin.",
              "inputs_known_at_ns": None, "context_known_at_ns": context_known_at_ns,
              "clock_scope": "Caller supplies the separately frozen source-clock windows."}
    if not formation.complete:
        return {**result, "status": "formation_unavailable"}
    return {**result, "status": "candidate_available",
            "inputs_known_at_ns": max(_known(formation), context_known_at_ns),
            "contract_key": formation.contract_key}


def _following(formation, forecast):
    _window(forecast)
    if forecast.start < formation.end:
        raise ContractError("future window must not overlap formation")


def _contact(window, level, contract):
    reasons = _reasons(window, contract)
    base = {"origin_ns": window.start, "endpoint_ns": window.end,
            "window_version": window.version, "target": _rational(level),
            "observed_minutes": window.count, "exclusion_reasons": reasons,
            "maturity_at_ns": None, "compatible_reach": None,
            "definite_print": None, "compatible_bar_count": None,
            "definite_print_bar_count": None}
    if reasons:
        return {**base, "status": "censored"}
    s, a, b = window.series, window.left, window.right
    observations = _level_observations(window, level)
    first, _, definite, compatible_count, definite_count, _ = observations
    return {**base, "status": "complete", "maturity_at_ns": _known(window),
            "compatible_reach": first is not None, "definite_print": definite is not None,
            "compatible_bar_count": compatible_count, "definite_print_bar_count": definite_count,
            "origin_open_equals_target": level.denominator == 1 and s.open[a] == level.numerator,
            "exact_integer_tick_print_possible": level.denominator == 1,
            "first_compatible_interval_ns": None if first is None else [s.start[first], s.end[first]],
            "first_definite_interval_ns": None if definite is None else [s.start[definite], s.end[definite]],
            "contact_evidence": _level_result(window, level=level, side=1, observations=observations)}


def _delayed_window(forecast, known_at, contract):
    origin = max(forecast.start, ((known_at + MINUTE - 1) // MINUTE) * MINUTE)
    if origin >= forecast.end:
        return None, {"status": "no_remaining_horizon", "origin_ns": origin,
                      "endpoint_ns": forecast.end, "inputs_known_at_ns": known_at,
                      "compatible_reach": None, "definite_print": None}
    delayed = forecast.series.window(origin, forecast.end, contract_key=contract,
                                     available_at=forecast.observation_cut_ns)
    return delayed, None


def _delayed_contact(forecast, known_at, contract, target):
    window, absent = _delayed_window(forecast, known_at, contract)
    return absent if window is None else {**_contact(window, target, contract),
        "inputs_known_at_ns": known_at,
        "target_version": "same_target_fixed_endpoint_after_input_availability"}


def three_stage_outcome(formation: OhlcWindow, conditioning: OhlcWindow,
                        forecast: OhlcWindow, *, p=Fraction(1, 2),
                        context_known_at_ns=0) -> dict:
    """PIN073 inclusive edge strata and an independent later midpoint reach."""
    _probability(p)
    _following(formation, conditioning)
    _following(conditioning, forecast)
    base = _base("three_stage_midpoint_return_v1", formation, context_known_at_ns)
    if not formation.complete:
        return base
    g = formation.geometry()
    target = Fraction(g.low) + p * g.width
    reasons = _reasons(conditioning, formation.contract_key)
    condition = {"window_version": conditioning.version, "origin_ns": conditioning.start,
                 "endpoint_ns": conditioning.end, "exclusion_reasons": reasons,
                 "status": "censored" if reasons else "complete", "stratum": None,
                 "high_taken": None, "low_taken": None, "known_at_ns": None}
    result = {**base, "target": _rational(target), "p": _rational(p),
              "target_known_at_ns": base["inputs_known_at_ns"],
              "conditioning": condition, "conditional_candidate_available": not reasons,
              "nominal": _contact(forecast, target, formation.contract_key),
              "departure_required": False, "edge_rule": "inclusive_reach"}
    if reasons:
        return {**result, "status": "conditioning_censored", "inputs_known_at_ns": None,
                "availability_delayed": {"status": "conditioning_censored",
                                         "compatible_reach": None, "definite_print": None}}
    s, a, b = conditioning.series, conditioning.left, conditioning.right
    upper, lower = max(s.high[a:b]) >= g.high, min(s.low[a:b]) <= g.low
    known = max(base["inputs_known_at_ns"], _known(conditioning))
    condition.update({"high_taken": upper, "low_taken": lower, "known_at_ns": known,
                      "stratum": "both" if upper and lower else "high_only" if upper else "low_only" if lower else "neither"})
    return {**result, "inputs_known_at_ns": known,
            "nominal_origin_precedes_input_known_at": forecast.start < known,
            "availability_delayed": _delayed_contact(forecast, known, formation.contract_key, target),
            "marginal_denominator_rule": "A both-edge date belongs to both taken marginals but is one distinct date."}


def open_to_open_outcome(reference: OhlcWindow, forecast: OhlcWindow, *,
                         p=Fraction(1, 2), context_known_at_ns=0) -> dict:
    """PIN074/076 first-slot open anchors, including unavailable future paths."""
    _probability(p)
    _following(reference, forecast)
    if reference.end - reference.start != MINUTE:
        raise ContractError("reference open requires its exact one-minute anchor slot")
    base = _base("open_to_open_retracement_v1", reference, context_known_at_ns)
    if not reference.complete:
        return {**base, "status": "reference_open_unavailable"}
    first = forecast.series.window(forecast.start, forecast.start + MINUTE,
                                   contract_key=reference.contract_key,
                                   available_at=forecast.observation_cut_ns)
    reasons = _reasons(first, reference.contract_key)
    if reasons:
        return {**base, "status": "forecast_open_unavailable", "candidate_available": False,
                "inputs_known_at_ns": None, "forecast_anchor": first.summary(),
                "exclusion_reasons": reasons}
    ref_open, forecast_open = reference.series.open[reference.left], first.series.open[first.left]
    target = (1 - p) * forecast_open + p * ref_open
    distance = p * abs(forecast_open - ref_open)
    known = max(base["inputs_known_at_ns"], _known(first))
    return {**base, "reference_open_ticks": ref_open, "forecast_open_ticks": forecast_open,
            "forecast_anchor": first.summary(), "target": _rational(target), "p": _rational(p),
            "retracement_distance_ticks": _rational(distance), "inputs_known_at_ns": known,
            "zero_displacement": forecast_open == ref_open,
            "displacement_sign": 0 if forecast_open == ref_open else 1 if forecast_open > ref_open else -1,
            "source_PIN076_stratum": "above_reference" if target > ref_open else "below_reference",
            "target_direction_from_forecast": "equal" if target == forecast_open else "above" if target > forecast_open else "below",
            "nominal_origin_precedes_input_known_at": forecast.start < known,
            "nominal": _contact(forecast, target, reference.contract_key),
            "availability_delayed": _delayed_contact(forecast, known, reference.contract_key, target),
            "source_comparator": "Includes forecast anchor bar; equality assigned below reference. Corrected one-minute PIN07407 anchor is not literal07:00-05:01 session reproduction."}


def _first_break(window, low, high):
    s = window.series
    for i in range(window.left, window.right):
        up, down = s.high[i] > high, s.low[i] < low
        if up or down:
            if s.open[i] > high:
                sides = ("upper",)
            elif s.open[i] < low:
                sides = ("lower",)
            else:
                sides = ("upper", "lower") if up and down else ("upper",) if up else ("lower",)
            return i, sides
    return None, ()


def _pending_events(s, i, side, eq_floor, eq_ceiling, inv_floor, inv_ceiling, *, first=False,
                    break_at_open=False, both_first=False):
    upper = side == "upper"
    target = s.low[i] <= eq_floor if upper else s.high[i] >= eq_ceiling
    invalid = s.high[i] >= inv_ceiling if upper else s.low[i] <= inv_floor
    open_target = s.open[i] <= eq_floor if upper else s.open[i] >= eq_ceiling
    open_invalid = s.open[i] >= inv_ceiling if upper else s.open[i] <= inv_floor
    if open_invalid:
        return {"invalidation"}
    if not first and open_target:
        return {"midpoint"}
    if first:
        # The first-break bar's target-side extreme can precede the break.
        # A close beyond EQ, an opening break, or the opposite strict breach
        # conditional on this being the first side proves later threshold reach.
        close_target = s.close[i] <= eq_floor if upper else s.close[i] >= eq_ceiling
        target_guaranteed = target and (break_at_open or close_target or both_first)
    else:
        target_guaranteed = target
    events = set()
    if target:
        events.add("midpoint")
    if invalid:
        events.add("invalidation")
    if not invalid and not target_guaranteed:
        events.add("pending")
    return events or {"pending"}


def _magic_branch(window, first, side, low, high, q):
    s, end = window.series, window.right
    width, eq_numerator = high - low, high + low
    eq_floor, eq_ceiling = eq_numerator // 2, -(-eq_numerator // 2)
    qn, qd = q.numerator, q.denominator
    inv_numerator = high * qd + qn * width if side == "upper" else low * qd - qn * width
    inv_floor, inv_ceiling = inv_numerator // qd, -(-inv_numerator // qd)
    inv = Fraction(inv_numerator, qd)
    opening_break = s.open[first] > high if side == "upper" else s.open[first] < low
    both = s.high[first] > high and s.low[first] < low
    states = _pending_events(s, first, side, eq_floor, eq_ceiling, inv_floor, inv_ceiling, first=True,
                             break_at_open=opening_break, both_first=both and not opening_break)
    if qn * width <= qd:
        # All observed prices are integer ticks. The first strict breach is
        # already at/beyond this invalidation, including a jump at the break.
        states = {"invalidation"}
    terminals = [(state, first) for state in states if state != "pending"]
    pending = "pending" in states
    for i in range(first + 1, end):
        if not pending:
            break
        states = _pending_events(s, i, side, eq_floor, eq_ceiling, inv_floor, inv_ceiling)
        terminals.extend((state, i) for state in states if state != "pending")
        pending = "pending" in states
    if pending:
        terminals.append(("pending", end - 1))
    names = {"midpoint": "midpoint_before_invalidation",
             "invalidation": "invalidation_before_midpoint",
             "pending": "break_then_neither_by_horizon"}
    possible = sorted({names[state] for state, _ in terminals})
    earliest, latest = min(i for _, i in terminals), max(i for _, i in terminals)
    def extent(i):
        return max(0, s.high[i] - high if side == "upper" else low - s.low[i])
    before_end = end if all(state == "pending" for state, _ in terminals) else earliest
    lower_peak = max((extent(i) for i in range(first, before_end)), default=0)
    upper_peak = max(extent(i) for i in range(first, latest + 1))
    compatible = any(s.low[i] <= eq_floor and s.high[i] >= eq_ceiling for i in range(first, end))
    definite = eq_numerator % 2 == 0 and (
        any(eq_floor in (s.open[i], s.high[i], s.low[i], s.close[i]) for i in range(first + 1, end))
        or s.close[first] == eq_floor or opening_break and eq_floor in (
            s.high[first], s.low[first], s.close[first]))
    return {"side": side, "invalidation": _rational(inv),
            "possible_terminal_states": possible,
            "state": possible[0] if len(possible) == 1 else "competing_order_ambiguous",
            "first_break_at_open": opening_break,
            "terminal_event_intervals_ns": [{"state": names[state], "interval": [s.start[i], s.end[i]],
                                             "known_at_ns": s.known[i]} for state, i in terminals],
            "pre_resolution_peak_extension_W_lower": _rational(Fraction(lower_peak, width)),
            "pre_resolution_peak_extension_W_upper": _rational(Fraction(upper_peak, width)),
            "post_break_horizon_EQ_compatible": compatible,
            "post_break_horizon_EQ_definite_print": bool(definite),
            "EQ_scope": "First-break-bar straddle is only possible after break; definite flag requires close/opening-break evidence or later-bar equality. These contacts retain fixed horizon even after invalidation."}


def _magic_source_comparator(window, first, low, high, q):
    s = window.series
    side = "upper" if s.high[first] > high else "lower"
    eq_numerator, width = high + low, high - low
    eq_floor, eq_ceiling = eq_numerator // 2, -(-eq_numerator // 2)
    qn, qd = q.numerator, q.denominator
    inv_numerator = high * qd + qn * width if side == "upper" else low * qd - qn * width
    inv_floor, inv_ceiling = inv_numerator // qd, -(-inv_numerator // qd)
    for i in range(first + 1, window.right):
        invalid = s.high[i] >= inv_ceiling if side == "upper" else s.low[i] <= inv_floor
        target = s.low[i] <= eq_floor if side == "upper" else s.high[i] >= eq_ceiling
        if invalid or target:
            return {"side": side, "state": "invalidation_before_midpoint" if invalid else "midpoint_before_invalidation",
                    "resolution_interval_ns": [s.start[i], s.end[i]]}
    return {"side": side, "state": "break_then_neither_by_horizon", "resolution_interval_ns": None}


def _magic_window(window, contract, low, high, q):
    reasons = _reasons(window, contract)
    base = {"origin_ns": window.start, "endpoint_ns": window.end,
            "window_version": window.version, "exclusion_reasons": reasons,
            "maturity_at_ns": None}
    if reasons:
        return {**base, "status": "censored", "state": "future_censored"}
    # Formation extrema originate in immutable integer minute columns. Keep
    # the per-bar scan in that exact domain; only displayed levels are rational.
    low, high = int(low), int(high)
    first, sides = _first_break(window, low, high)
    base.update({"maturity_at_ns": _known(window), "status": "complete"})
    if first is None:
        return {**base, "state": "no_break_by_horizon", "first_side": "neither",
                "possible_terminal_states": ["no_break_by_horizon"]}
    branches = [_magic_branch(window, first, side, low, high, q) for side in sides]
    possible = sorted({state for branch in branches for state in branch["possible_terminal_states"]})
    return {**base, "state": "first_side_ambiguous" if len(sides) > 1 else branches[0]["state"],
            "first_side": "ambiguous" if len(sides) > 1 else sides[0],
            "first_break_interval_ns": [window.series.start[first], window.series.end[first]],
            "first_break_known_at_ns": window.series.known[first], "branches": branches,
            "possible_terminal_states": possible,
            "source_branch_priority_comparator": {
                **_magic_source_comparator(window, first, low, high, q),
                "label": "Source branch order applied to supplied minute bars: upper first, skip first-break bar, invalidation first thereafter.",
                "not_observed_order": True, "not_whole_Pine_reproduction": True,
                "endpoint_scope": "Uses this declared half-open endpoint, not source bar_index endpoint extension."}}


def magic_outcome(formation: OhlcWindow, forecast: OhlcWindow, *,
                  invalidation=Fraction(1), context_known_at_ns=0) -> dict:
    """Strict first breach and conservative competing threshold event sets."""
    if type(invalidation) is not Fraction or invalidation not in (Fraction(3, 4), Fraction(1)):
        raise ContractError("source magic invalidation must be exact3/4W or1W")
    _following(formation, forecast)
    base = _base("magic_break_midpoint_competing_extension_v1", formation, context_known_at_ns)
    if not formation.complete:
        return base
    g = formation.geometry()
    result = {**base, "target": _rational(Fraction(g.high + g.low, 2)),
              "invalidation_W": _rational(invalidation),
              "nominal_origin_precedes_input_known_at": forecast.start < base["inputs_known_at_ns"],
              "threshold_scope": "Directional EQ inequality is separate from exact EQ print; gaps can reach threshold without contact."}
    if not g.width:
        return {**result, "status": "zero_width_geometry_without_normalized_extension",
                "nominal": {"status": "zero_width", "state": "zero_width"},
                "availability_delayed": {"status": "zero_width", "state": "zero_width"}}
    known, contract = base["inputs_known_at_ns"], formation.contract_key
    delayed, absent = _delayed_window(forecast, known, contract)
    return {**result, "nominal": _magic_window(forecast, contract, g.low, g.high, invalidation),
            "availability_delayed": absent if delayed is None else {
                **_magic_window(delayed, contract, g.low, g.high, invalidation),
                "target_version": "new_first_break_search_after_input_availability_same_fixed_endpoint"}}


def daily_range_outcome(formation: OhlcWindow, forecast: OhlcWindow, *,
                        date_key: str, context_known_at_ns=0) -> dict:
    """PIN078 individual daily range, not combined Monday/Tuesday extrema."""
    _following(formation, forecast)
    if type(date_key) is not str:
        raise ContractError("UTC close date must be an ISO date string")
    try:
        day = date.fromisoformat(date_key)
    except ValueError as exc:
        raise ContractError("UTC close date must be an ISO date string") from exc
    base = _base("source_mon_tue_daily_range_v1", formation, context_known_at_ns)
    base.update({"date_key": date_key, "weekday": day.weekday(),
                 "date_semantics": "Explicit UTC close-date correction; exact Pine overnight daytags are not certified.",
                 "range_scope": "One formation session; not combined weekly IB."})
    if day.weekday() not in (0, 1):
        return {**base, "status": "not_source_weekday", "candidate_available": False}
    if not formation.complete:
        return base
    g = formation.geometry()
    levels = {"high": Fraction(g.high), "low": Fraction(g.low),
              "midpoint": Fraction(g.high + g.low, 2),
              "fib1_actual_30pct": Fraction(g.high) - Fraction(3, 10) * g.width,
              "fib2_actual_70pct": Fraction(g.high) - Fraction(7, 10) * g.width}
    return {**base, "levels": {name: _rational(level) for name, level in levels.items()},
            "nominal_origin_precedes_input_known_at": forecast.start < base["inputs_known_at_ns"],
            "nominal": {name: _contact(forecast, level, formation.contract_key) for name, level in levels.items()},
            "availability_delayed": {name: _delayed_contact(forecast, base["inputs_known_at_ns"], formation.contract_key, level)
                                     for name, level in levels.items()},
            "source_comparator": "Every straddling bar counts separately; static21.4/29.3 plot names do not override actual30/70 defaults.",
            "horizon_scope": "Supplied postformation horizon is a separately named study construction."}


def daily_hit_statistics(outcomes) -> dict:
    """Unique-date rates and repeated-bar shares with explicit denominators."""
    if not isinstance(outcomes, (list, tuple)):
        raise ContractError("bounded explicit outcome collection required")
    if len(outcomes) > 10000:
        raise ContractError("daily mechanism summary exceeds10000 observations")
    dates = set()
    for outcome in outcomes:
        if (type(outcome) is not dict or outcome.get("mechanism") != "source_mon_tue_daily_range_v1"
                or type(outcome.get("date_key")) is not str):
            raise ContractError("daily summaries require named daily mechanism outputs")
        if outcome["date_key"] in dates:
            raise ContractError("duplicate formation date would double-count the daily denominator")
        dates.add(outcome["date_key"])
    names = sorted({name for outcome in outcomes for name in outcome.get("nominal", {})})
    summaries = {}
    for name in names:
        eligible = [(outcome["date_key"], outcome["nominal"][name]) for outcome in outcomes
                    if outcome.get("candidate_available") is True and name in outcome.get("nominal", {})
                    and outcome["nominal"][name]["status"] == "complete"]
        hit_days = sum(bool(value["compatible_reach"]) for _, value in eligible)
        print_days = sum(bool(value["definite_print"]) for _, value in eligible)
        hits = sum(value["compatible_bar_count"] for _, value in eligible)
        summaries[name] = {"eligible_dates": len(eligible), "excluded_dates": len(outcomes) - len(eligible),
                           "unique_compatible_hit_dates": hit_days, "unique_definite_print_dates": print_days,
                           "compatible_bar_hits": hits,
                           "unique_day_compatible_rate": None if not eligible else _rational(Fraction(hit_days, len(eligible))),
                           "unique_day_definite_print_rate": None if not eligible else _rational(Fraction(print_days, len(eligible))),
                           "repeated_hit_share_by_formation_date": {key: None if not hits else _rational(Fraction(value["compatible_bar_count"], hits))
                                                                   for key, value in eligible}}
    return {"version": VERSION, "observations": len(outcomes), "levels": summaries,
            "share_scope": "Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability."}


def overnight_pivot(formation: OhlcWindow, *, variant: str,
                    context_known_at_ns=0) -> dict:
    """JTR overnight anchor identity and ordinary wick geometry only."""
    if variant not in ("ONS03", "ONS20"):
        raise ContractError("overnight pivot variant must beONS03 orONS20")
    base = _base("overnight_pivot_range_v1", formation, context_known_at_ns)
    base.update({"variant": variant, "opening_range_identity": False,
                 "formula_scope": "Ordinary wick range and midpoint; no classical floor-trader pivot formula or undisclosed reversal rule."})
    if not formation.complete:
        return base
    g = formation.geometry()
    return {**base, "midpoint": _rational(Fraction(g.high + g.low, 2)),
            "zero_width": not bool(g.width)}
