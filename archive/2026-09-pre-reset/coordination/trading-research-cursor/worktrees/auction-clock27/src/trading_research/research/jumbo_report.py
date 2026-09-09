"""Date-aware descriptive results from the reusable Jumbo outcome tables."""
from collections import Counter, defaultdict
from datetime import date
import json
import math

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.date_statistics import _moving_weights, _numpy, observed_date_statistics

CONTINUOUS = (
    "maximum_up_W", "maximum_down_W", "terminal_W", "remaining_range_W",
    "upper_overshoot_W", "lower_overshoot_W", "first_lower_minutes",
    "first_upper_minutes", "second_lower_minutes", "second_upper_minutes",
    "maximum_up_ticks", "maximum_down_ticks", "terminal_ticks", "squared_close_returns_ticks2",
)
BINARY = ("upper_breach", "lower_breach", "both_breach", "no_breach", "reclaim_observed",
          "inclusive_upper_reach", "inclusive_lower_reach", "inclusive_both_reach")
PATHS = ("no_break", "high_only", "low_only", "high_then_low", "low_then_high", "ambiguous")


def _intended(clock, dates):
    return tuple(day for day in dates if clock != "PIN078_daily_not_combined" or date.fromisoformat(day).weekday() in (0, 1))


def _date_population(actual, intended):
    if len(actual) != len(intended) or len(set(actual)) != len(actual) or set(actual) != set(intended):
        raise IntegrityError("intended source date population changed")


def _compact(value):
    value["bootstrap"].pop("replicate_estimates", None)
    return value


def metric_intervals(metrics, dates, settings):
    """Bound numerical workspace while retaining common seeded date weights."""
    result = {}
    names = sorted(metrics)
    if not names:
        return result
    np = _numpy()
    shared_weights, shared_starts = _moving_weights(
        np, len(dates), seed=settings["bootstrap_seed"],
        block_length=settings["block_length"], replicates=settings["replicates"],
    )
    bootstrap_state = (np, shared_weights, shared_starts)
    for at in range(0, len(names), 1024):
        chosen = names[at:at + 1024]
        batch = observed_date_statistics(
            {name: metrics[name] for name in chosen}, dates,
            seed=settings["bootstrap_seed"], block_length=settings["block_length"],
            replicates=settings["replicates"], confidence=settings["confidence"],
            minimum_independent_dates=settings["minimum_dates"], minimum_events=settings["minimum_events"],
            _bootstrap_state=bootstrap_state,
            _retain_replicate_estimates=False,
        )
        # Compact batches are produced without replicate-estimate lists, so
        # there is no post-hoc list allocation and pop to perform here.
        result.update(batch["metrics"])
    return result


def _descriptive(values, levels):
    values = tuple(float(v) for v in values if v is not None)
    if not values:
        return {"count": 0, "mean": None, "minimum": None, "maximum": None,
                "quantiles": {str(q): None for q in levels}}
    ordered = sorted(values)

    def percentile(level):
        if not 0 <= level <= 1:
            raise ContractError("invalid empirical quantile")
        index = (len(ordered) - 1) * level
        lo = math.floor(index)
        hi = math.ceil(index)
        return ordered[lo] + (ordered[hi] - ordered[lo]) * (index - lo)

    return {"count": len(values), "mean": sum(values) / len(values), "minimum": min(values),
            "maximum": max(values), "quantiles": {str(q): percentile(q) for q in levels}}


def _timing_value(row, horizon):
    if horizon > row["planned_minutes"]:
        return None
    if row["prefix_first_upper_minutes"] is not None and row["prefix_first_upper_minutes"] <= horizon:
        return 1.0
    if row["observed_prefix_minutes"] >= horizon:
        return 0.0
    return None


def path_statistics(rows, dates, *, plan):
    """Every row is retained; metric denominators identify observed truth."""
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        key = (row["clock"], row["horizon"], row["date"])
        if key in seen:
            raise IntegrityError("duplicate date/clock/horizon would increase independent support")
        seen.add(key)
        groups[key[:2]].append(row)
    settings = plan["statistics"]
    if "expected_formation_clock_ids" in plan:
        expected = {(clock, horizon) for clock in plan["expected_formation_clock_ids"]
                    for horizon in [*(f"after_{n}m" for n in plan["horizons_minutes"]), "to_actual_cash_close"]}
        expected.update((clock, f"prefix_{n}m_to_actual_cash_close") for clock in plan["prefix_clocks"] for n in plan["prefix_delays_minutes"])
        expected.update((clock, "common_1001_to_actual_cash_close") for clock in plan["matched_clock_comparison"]["clocks"])
        if set(groups) != expected:
            raise IntegrityError("intended clock/horizon population changed")
    results, metrics_by_calendar = {}, {"cash": {}, "mon_tue": {}}
    metadata = {}
    for (clock, horizon), observations in sorted(groups.items()):
        name = clock + "|" + horizon
        intended = _intended(clock, dates)
        _date_population([r["date"] for r in observations], intended)
        complete = [r for r in observations if r["status"] in ("observed", "ambiguous")]
        eligible = [r for r in observations if r["x_width_ticks"] is not None]
        reasons = Counter(reason for r in observations for reason in r["exclusion_reasons"].split(";") if reason)
        result = {"clock": clock, "horizon": horizon, "intended_dates": len(intended),
                  "actual_candidate_rows": len(observations), "available_formation_dates": len(eligible),
                  "complete_target_dates": len(complete), "unavailable_or_zero_width_dates": len(observations) - len(complete),
                  "status_counts": dict(Counter(r["status"] for r in observations)),
                  "path_counts": dict(Counter(r["path"] for r in observations)),
                  "exclusion_reason_counts": dict(reasons),
                  "metric_scope": "Full-horizon path means condition on complete observed outcomes; first-event curves use every observed prefix. Missing truth is never a negative event.",
                  "metrics": {}, "distributions": {field: _descriptive([r[field] for r in observations], settings["descriptive_quantiles"]) for field in CONTINUOUS}}
        if len(observations) != len(intended):
            raise IntegrityError("intended source clock population lost or added dates")
        values = {}
        for field in (*BINARY, *CONTINUOUS):
            values[field] = {r["date"]: None if r[field] is None else float(r[field]) for r in observations}
        for path in PATHS:
            values["path_" + path] = {r["date"]: float(r["path"] == path) for r in complete}
        for minute in (1, 5, 15, 30, 60, 180):
            values[f"first_breach_by_{minute}m"] = {r["date"]: _timing_value(r, minute) for r in observations}
        # The same formed-date population supplies all three sides.  Build it
        # once instead of repeating the row scan for upper, lower and both.
        formed = [r for r in observations if r["x_width_ticks"] is not None and r["x_width_ticks"] > 0 and r["planned_minutes"] > 0]
        for side in ("upper", "lower", "both"):
            # Identified population bounds over formed nonzero-width ranges:
            # event observed before censoring is 1; unresolved truth lies0..1.
            values[side + "_full_population_rate_lower"] = {r["date"]: float(bool(r["prefix_" + side + "_breach"])) for r in formed}
            values[side + "_full_population_rate_upper"] = {r["date"]: float(r[side + "_breach"]) if r[side + "_breach"] is not None else 1.0 for r in formed}
        bucket = "mon_tue" if clock == "PIN078_daily_not_combined" else "cash"
        for field, cells in values.items():
            key = name + "|" + field
            metrics_by_calendar[bucket][key] = cells
            metadata[key] = (name, field)
        results[name] = result
    for bucket, metrics in metrics_by_calendar.items():
        if not metrics:
            continue
        intended = tuple(dates) if bucket == "cash" else _intended("PIN078_daily_not_combined", dates)
        for key, value in metric_intervals(metrics, intended, settings).items():
            name, field = metadata[key]
            if field in BINARY or field.startswith("path_") or field.startswith("first_breach_by_"):
                observed = [v for v in metrics[key].values() if v is not None]
                positives = int(sum(observed))
                negatives = len(observed) - positives
                value.update(positive_events=positives, negative_events=negatives,
                             event_support_sparse=min(positives, negatives) < settings["minimum_events"])
            results[name]["metrics"][field] = value
    return list(results.values())


def formation_statistics(rows, dates, *, plan):
    groups = defaultdict(list)
    for row in rows:
        groups[row["clock"]].append(row)
    if "expected_formation_clock_ids" in plan and set(groups) != set(plan["expected_formation_clock_ids"]):
        raise IntegrityError("intended formation clock population changed")
    settings, output = plan["statistics"], []
    for clock, observations in sorted(groups.items()):
        intended = _intended(clock, dates)
        _date_population([r["date"] for r in observations], intended)
        complete = [r for r in observations if r["status"] == "complete"]
        output.append({"clock": clock, "intended_dates": len(intended),
                       "available_dates": len(complete), "zero_width_dates": sum(r["zero_width"] is True for r in complete),
                       "exclusion_reason_counts": dict(Counter(reason for r in observations for reason in r["exclusion_reasons"].split(";") if reason)),
                       "distributions": {key: _descriptive([r[key] for r in complete], settings["descriptive_quantiles"])
                                         for key in ("width_ticks", "volume", "open_position", "formation_up_ticks", "formation_down_ticks",
                                                     "x_width_prior_ratio", "x_formation_minutes", "x_prior_20_mean_width_ticks")}})
    return output


def special_statistics(rows, dates, *, plan):
    groups = defaultdict(list)
    for row in rows:
        groups[row["clock"]].append((row["date"], json.loads(row["payload"])))
    if "expected_special_clock_ids" in plan and set(groups) != set(plan["expected_special_clock_ids"]):
        raise IntegrityError("intended special-mechanism population changed")
    output = []
    for clock, observations in sorted(groups.items()):
        intended = _intended(clock, dates)
        _date_population([day for day, _ in observations], intended)
        record = {"clock": clock, "intended_dates": len(intended),
                  "candidate_available_dates": sum(v.get("candidate_available") is True for _, v in observations),
                  "status_counts": dict(Counter(v["status"] for _, v in observations)), "outcomes": {}, "conditional": {}}
        metrics = {}
        if clock == "PIN078_daily_not_combined":
            from trading_research.research.ohlc_mechanisms import daily_hit_statistics
            record["daily_hit_statistics"] = daily_hit_statistics([v for _, v in observations])
        for branch in ("nominal", "availability_delayed"):
            path_counts = Counter()
            for day, value in observations:
                target = value.get(branch, {})
                if "state" in target:
                    path_counts[target["state"]] += 1
                    if target.get("status") == "complete":
                        possible = target["possible_terminal_states"]
                        for name in ("midpoint_before_invalidation", "invalidation_before_midpoint", "no_break_by_horizon", "break_then_neither_by_horizon"):
                            metrics.setdefault(branch + "|" + name + "_lower", {})[day] = float(possible == [name])
                            metrics.setdefault(branch + "|" + name + "_upper", {})[day] = float(name in possible)
                for field in ("compatible_reach", "definite_print"):
                    if field in target:
                        metrics.setdefault(branch + "|" + field, {})[day] = None if target[field] is None else float(target[field])
                stratum = value.get("conditioning", {}).get("stratum")
                if stratum is not None:
                    record["conditional"].setdefault(stratum, {"dates": 0})
                    if branch == "nominal":
                        record["conditional"][stratum]["dates"] += 1
                    for field in ("compatible_reach", "definite_print"):
                        if field in target:
                            metrics.setdefault(branch + "|stratum=" + stratum + "|" + field, {})[day] = None if target[field] is None else float(target[field])
            record["outcomes"][branch] = dict(path_counts)
        if metrics:
            # Bootstrap chronology is the declared intended population, even
            # when retained payload rows happen to arrive in another order.
            record["metrics"] = metric_intervals(metrics, intended, plan["statistics"])
        output.append(record)
    return output


def year_statistics(batch, dates, *, plan):
    return {"kind": "jumbo_observed_year_statistics_v1", "intended_cash_dates": len(dates),
            "formations": formation_statistics(batch["formations"], dates, plan=plan),
            "paths": path_statistics(batch["paths"], dates, plan=plan),
            "special_mechanisms": special_statistics(batch["specials"], dates, plan=plan),
            "uncertainty_scope": "Descriptive per-year date-block intervals. No familywise winner or final-test selection is inferred from individual intervals.",
            "model_fits": 0, "location_quality_complete": False,
            "family_statistics_complete": False}
