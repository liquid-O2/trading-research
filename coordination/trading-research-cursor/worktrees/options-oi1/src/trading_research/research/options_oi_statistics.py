"""Date aggregates, candidate-definition statistics and the readable OI report.

Source-clock timing and position-date assumptions are descriptive. They are not
actual predictive evaluation. Cuts and contract observations are not treated as
independent dates. All candidate first/last and position-clock definitions are
reported; this module does not choose a winner.

OI zero is a valid observation. Absence, missing publication and listing-unknown
stay missing (estimate None), never coerced to zero. Coverage, missing and censor
fractions use intended-eligible denominators, not only positive observations.

Date-mean uncertainty uses one weight per date. support.events and
actual_valid_event_count are raw contract/observation counts, not date-cell
counts. After registered execution these are source-derived estimates, not a
completed family.
"""
from __future__ import annotations

from collections import defaultdict
import time as pytime

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.scoring import quantile


VERSION = "options-oi-report-lifecycle-statistics-v2"
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
PRESPECIFIED = (
    "oi_level_date_mean", "oi_zero_fraction", "report_seconds_after_eastern_midnight",
    "coverage_fraction", "missing_oi_fraction", "oi_mass", "oi_width",
    "update_candidate_fraction", "update_difference_mean",
    "common_support_first", "common_support_last", "common_support_first_minus_last",
    "next_delta", "next_abs_delta", "next_positive_fraction", "next_zero_fraction",
    "next_negative_fraction", "censor_missing_fraction", "censor_expired_fraction",
    "censor_boundary_fraction", "first_observed_fraction",
    "position_mapping_agree_fraction", "event_local_mismatch_fraction",
    "future_clock_flag_fraction", "late_clock_flag_fraction",
    "asof_0930_available_fraction", "asof_0930_stale_fraction", "asof_0930_future_today_fraction",
    "asof_1000_available_fraction", "asof_1000_stale_fraction", "asof_1000_future_today_fraction",
    "asof_1500_available_fraction", "asof_1500_stale_fraction", "asof_1500_future_today_fraction",
)
RATIO_SPECS = {
    "oi_level_event_weighted": ("oi_mass", "oi_width"),
    "common_first_over_last": ("common_support_first", "common_support_last"),
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


def empty_metric(intended_dates):
    """Explicit undefined metric: estimate is None, not zero."""
    n = len(intended_dates)
    return {
        "estimate": None,
        "actual_valid_date_count": 0,
        "actual_valid_event_count": 0,
        "valid_date_count": 0,
        "valid_event_count": 0,
        "missing_date_count": n,
        "estimator": "date_mean",
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
        "event_weighted_estimate": None,
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


def _overlay_raw_support(payload, dates, cells, raw_events, cfg):
    events = 0
    for day in dates:
        if day in cells and cells[day] is not None:
            events += int(raw_events.get(day, 1))
    payload["actual_valid_event_count"] = events
    payload["valid_event_count"] = events
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


def _summarize(metrics, dates, cfg, *, ratios=None, event_counts=None, estimator="date_mean"):
    """Keep every prespecified metric. Only send present keys/ratios to ODS."""
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
    for name in names:
        if name in result.get("metrics", {}):
            payload = result["metrics"][name]
            series = [present[name][day] for day in dates if day in present[name]]
            payload["date_quantiles"] = date_quantiles(series, cfg["quantiles"])
            payload["missing_date_count"] = len(dates) - payload.get("actual_valid_date_count", 0)
            _overlay_raw_support(payload, dates, present[name], raw.get(name, {}), cfg)
            metrics_out[name] = payload
        else:
            metrics_out[name] = empty_metric(dates)
    ratios_out = {}
    for name, pair in ratio_specs.items():
        if name in result.get("ratios", {}):
            payload = result["ratios"][name]
            num_events = sum(int(raw.get(pair[0], {}).get(day, 1))
                             for day in dates if day in present.get(pair[0], {}))
            den_events = sum(int(raw.get(pair[1], {}).get(day, 1))
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


def _life_bag(uname):
    if uname == "all_period":
        return "lifecycle_all"
    if uname.startswith("stage_"):
        return "lifecycle_within_stage"
    if uname.startswith("year_"):
        return "lifecycle_within_year"
    return "lifecycle_all"


def _asof_cell(payload, key, den):
    if not den:
        return None
    return payload.get(key, 0) / den


def _date_maps(rows, chain, policy, life_bag):
    """Build per-date scalar maps. Zero availability is 0, not missing. Missing stays absent."""
    oi_mean, oi_zero, seconds = {}, {}, {}
    coverage, missing_oi = {}, {}
    oi_sum, oi_n = {}, {}
    update_frac, update_diff = {}, {}
    common_first, common_last, paired = {}, {}, {}
    mapping, mismatch, future, late = {}, {}, {}, {}
    life = {
        "delta": {}, "abs_delta": {}, "pos": {}, "zero": {}, "neg": {},
        "censor_missing": {}, "censor_expired": {}, "censor_boundary": {},
        "first_observed": {},
    }
    events = defaultdict(dict)
    asof = defaultdict(lambda: {"available": {}, "stale": {}, "future_today": {}})
    asof_events = defaultdict(lambda: {"available": {}, "stale": {}, "future_today": {}})
    for row in rows:
        if row["chain"] != chain or not row.get("intended") or not row.get("primary"):
            continue
        day = row["request_date"]
        acc = row[policy]
        if acc["oi_n"]:
            oi_mean[day] = acc["oi_sum"] / acc["oi_n"]
            oi_zero[day] = acc["zero_n"] / acc["oi_n"]
            oi_sum[day] = acc["oi_sum"]
            oi_n[day] = acc["oi_n"]
            events["oi_level_date_mean"][day] = acc["oi_n"]
            events["oi_zero_fraction"][day] = acc["oi_n"]
            events["oi_mass"][day] = acc["oi_n"]
            events["oi_width"][day] = acc["oi_n"]
        if acc["seconds_n"]:
            seconds[day] = acc["seconds_sum"] / acc["seconds_n"]
            events["report_seconds_after_eastern_midnight"][day] = acc["seconds_n"]
        if row["listing_denominator_known"] and row["listing_count"] not in (None, 0):
            coverage[day] = row["coverage_listed_with_oi"]
            missing_oi[day] = None if row["listed_without_oi"] is None else row["listed_without_oi"] / row["listing_count"]
            events["coverage_fraction"][day] = row["listing_count"]
            events["missing_oi_fraction"][day] = row["listing_count"]
        usable = row["usable_report_count"]
        if usable:
            update_frac[day] = row["update_candidate_count"] / usable
            events["update_candidate_fraction"][day] = usable
        if row["update_n"]:
            update_diff[day] = row["update_diff_sum"] / row["update_n"]
            events["update_difference_mean"][day] = row["update_n"]
        if acc["common_n"]:
            common_first[day] = acc["common_first_sum"] / acc["common_n"]
            common_last[day] = acc["common_last_sum"] / acc["common_n"]
            paired[day] = acc["paired_diff_sum"] / acc["common_n"]
            events["common_support_first"][day] = acc["common_n"]
            events["common_support_last"][day] = acc["common_n"]
            events["common_support_first_minus_last"][day] = acc["common_n"]
        if acc["own_n"] and acc["common_n"]:
            pass
        if row["position_mapping_count"]:
            mapping[day] = row["position_mapping_agree_count"] / row["position_mapping_count"]
            events["position_mapping_agree_fraction"][day] = row["position_mapping_count"]
        source_n = row["position_mapping_count"] or row.get("usable_report_count") or 0
        if source_n:
            mismatch[day] = row["event_local_mismatch_count"] / source_n
            future[day] = row["future_flag_count"] / source_n
            late[day] = row["late_flag_count"] / source_n
            events["event_local_mismatch_fraction"][day] = source_n
            events["future_clock_flag_fraction"][day] = source_n
            events["late_clock_flag_fraction"][day] = source_n
        life_acc = row.get(life_bag, row.get("lifecycle_all", {})).get(policy, {})
        attempts = life_acc.get("n_attempts", 0)
        if life_acc.get("n"):
            life["delta"][day] = life_acc["delta_sum"] / life_acc["n"]
            life["abs_delta"][day] = life_acc["abs_sum"] / life_acc["n"]
            life["pos"][day] = life_acc["n_pos"] / life_acc["n"]
            life["zero"][day] = life_acc["n_zero"] / life_acc["n"]
            life["neg"][day] = life_acc["n_neg"] / life_acc["n"]
            for name in ("next_delta", "next_abs_delta", "next_positive_fraction",
                         "next_zero_fraction", "next_negative_fraction"):
                events[name][day] = life_acc["n"]
        if attempts:
            life["censor_missing"][day] = life_acc["n_censor_missing"] / attempts
            life["censor_expired"][day] = life_acc["n_censor_expired"] / attempts
            life["first_observed"][day] = life_acc["n_first_observed"] / attempts
            for name in ("censor_missing_fraction", "censor_expired_fraction",
                         "first_observed_fraction"):
                events[name][day] = attempts
        # Source boundaries have their own endpoint population; do not double
        # the denominator of the ordinary adjacent-date changes.
        boundary = row.get("lifecycle_boundary", {}).get(policy, {}).get("n_attempts", 0)
        if boundary:
            life["censor_boundary"][day] = 1.0
            events["censor_boundary_fraction"][day] = boundary
        for cut, payload in row.get("asof", {}).items():
            universe = payload.get("universe")
            tag = cut.replace(":", "")
            if universe:
                asof[cut]["available"][day] = payload["available"] / universe
                asof[cut]["stale"][day] = payload["stale"] / universe
                asof[cut]["future_today"][day] = payload["future_today"] / universe
                asof_events[cut]["available"][day] = universe
                asof_events[cut]["stale"][day] = universe
                asof_events[cut]["future_today"][day] = universe
                events[f"asof_{tag}_available_fraction"][day] = universe
                events[f"asof_{tag}_stale_fraction"][day] = universe
                events[f"asof_{tag}_future_today_fraction"][day] = universe
    return {
        "oi_level_date": oi_mean, "oi_zero_fraction": oi_zero, "report_seconds": seconds,
        "coverage_fraction": coverage, "missing_oi_fraction": missing_oi,
        "oi_sum": oi_sum, "oi_n": oi_n, "update_candidate_fraction": update_frac,
        "update_difference_mean": update_diff,
        "common_first": common_first, "common_last": common_last, "first_minus_last": paired,
        "position_mapping_agree_fraction": mapping,
        "event_local_mismatch_fraction": mismatch,
        "future_clock_flag_fraction": future,
        "late_clock_flag_fraction": late,
        "life": life, "asof": asof, "events": events,
    }


def _slice_maps(maps, dates):
    def keep(values):
        return {day: values[day] for day in dates if day in values}

    life = {name: keep(values) for name, values in maps["life"].items()}
    asof = {}
    for cut, payload in maps["asof"].items():
        asof[cut] = {name: keep(values) for name, values in payload.items()}
    events = {name: keep(values) for name, values in maps["events"].items()}
    return {
        "oi_level_date": keep(maps["oi_level_date"]),
        "oi_zero_fraction": keep(maps["oi_zero_fraction"]),
        "report_seconds": keep(maps["report_seconds"]),
        "coverage_fraction": keep(maps["coverage_fraction"]),
        "missing_oi_fraction": keep(maps["missing_oi_fraction"]),
        "oi_sum": keep(maps["oi_sum"]),
        "oi_n": keep(maps["oi_n"]),
        "update_candidate_fraction": keep(maps["update_candidate_fraction"]),
        "update_difference_mean": keep(maps["update_difference_mean"]),
        "common_first": keep(maps["common_first"]),
        "common_last": keep(maps["common_last"]),
        "first_minus_last": keep(maps["first_minus_last"]),
        "position_mapping_agree_fraction": keep(maps["position_mapping_agree_fraction"]),
        "event_local_mismatch_fraction": keep(maps["event_local_mismatch_fraction"]),
        "future_clock_flag_fraction": keep(maps["future_clock_flag_fraction"]),
        "late_clock_flag_fraction": keep(maps["late_clock_flag_fraction"]),
        "life": life,
        "asof": asof,
        "events": events,
    }


def _metric_bundle(maps):
    metrics = {
        "oi_level_date_mean": maps["oi_level_date"],
        "oi_zero_fraction": maps["oi_zero_fraction"],
        "report_seconds_after_eastern_midnight": maps["report_seconds"],
        "coverage_fraction": maps["coverage_fraction"],
        "missing_oi_fraction": maps["missing_oi_fraction"],
        "oi_mass": maps["oi_sum"],
        "oi_width": maps["oi_n"],
        "update_candidate_fraction": maps["update_candidate_fraction"],
        "update_difference_mean": maps["update_difference_mean"],
        "common_support_first": maps["common_first"],
        "common_support_last": maps["common_last"],
        "common_support_first_minus_last": maps["first_minus_last"],
        "next_delta": maps["life"]["delta"],
        "next_abs_delta": maps["life"]["abs_delta"],
        "next_positive_fraction": maps["life"]["pos"],
        "next_zero_fraction": maps["life"]["zero"],
        "next_negative_fraction": maps["life"]["neg"],
        "censor_missing_fraction": maps["life"]["censor_missing"],
        "censor_expired_fraction": maps["life"]["censor_expired"],
        "censor_boundary_fraction": maps["life"]["censor_boundary"],
        "first_observed_fraction": maps["life"]["first_observed"],
        "position_mapping_agree_fraction": maps["position_mapping_agree_fraction"],
        "event_local_mismatch_fraction": maps["event_local_mismatch_fraction"],
        "future_clock_flag_fraction": maps["future_clock_flag_fraction"],
        "late_clock_flag_fraction": maps["late_clock_flag_fraction"],
    }
    for cut, payload in maps["asof"].items():
        tag = cut.replace(":", "")
        metrics[f"asof_{tag}_available_fraction"] = payload["available"]
        metrics[f"asof_{tag}_stale_fraction"] = payload["stale"]
        metrics[f"asof_{tag}_future_today_fraction"] = payload["future_today"]
    for name in PRESPECIFIED:
        metrics.setdefault(name, {})
    return metrics, dict(RATIO_SPECS), maps["events"]


def _right_dte_maps(rows, chain, policy, *, kind, name):
    oi_mean, oi_n, oi_sum = {}, {}, {}
    events = {"oi_level_date_mean": {}, "oi_mass": {}, "oi_width": {}}
    for row in rows:
        if row["chain"] != chain or not row.get("intended") or not row.get("primary"):
            continue
        bag = row["by_right" if kind == "right" else "by_dte"].get(name)
        if not bag:
            continue
        acc = bag[policy]
        day = row["request_date"]
        if acc["oi_n"]:
            oi_mean[day] = acc["oi_sum"] / acc["oi_n"]
            oi_n[day] = acc["oi_n"]
            oi_sum[day] = acc["oi_sum"]
            events["oi_level_date_mean"][day] = acc["oi_n"]
            events["oi_mass"][day] = acc["oi_n"]
            events["oi_width"][day] = acc["oi_n"]
    return {"oi_level_date_mean": oi_mean, "oi_mass": oi_sum, "oi_width": oi_n}, events


def build_group_statistics(date_aggregates, *, protocol, intended_all, chains, stages, selected_dates=None):
    cfg = _cfg(protocol)
    dates_all = list(selected_dates or intended_all)
    years = sorted({label[:4] for label in dates_all})
    groups = {}
    for chain in chains:
        for policy in ("first", "last"):
            universes = [("all_period", dates_all)]
            for year in years:
                universes.append((f"year_{year}", [d for d in dates_all if d.startswith(year)]))
            for stage in stages:
                universes.append((f"stage_{stage}", universe_dates(dates_all, stage=stage, stages=stages)))
            for uname, udates in universes:
                maps = _date_maps(date_aggregates, chain, policy, _life_bag(uname))
                if not udates:
                    groups[f"{chain}|{uname}|{policy}|all|all"] = {
                        "group": {"chain": chain, "universe": uname, "policy": policy, "right": "all", "dte": "all"},
                        "statistics": {
                            "schema": "observed-date-statistics-v1",
                            "intended_dates": [],
                            "intended_date_count": 0,
                            "metrics": {name: empty_metric([]) for name in PRESPECIFIED},
                            "ratios": {name: empty_ratio([], pair[0], pair[1]) for name, pair in RATIO_SPECS.items()},
                            "all_values_missing": True,
                        },
                    }
                    continue
                sliced = _slice_maps(maps, udates)
                metrics, ratios, events = _metric_bundle(sliced)
                groups[f"{chain}|{uname}|{policy}|all|all"] = {
                    "group": {"chain": chain, "universe": uname, "policy": policy, "right": "all", "dte": "all"},
                    "statistics": _summarize(metrics, udates, cfg, ratios=ratios, event_counts=events),
                }
            rights = sorted({
                right for row in date_aggregates if row["chain"] == chain
                for right in row.get("by_right", {})
            })
            buckets = sorted({
                bucket for row in date_aggregates if row["chain"] == chain
                for bucket in row.get("by_dte", {})
            })
            base_maps = _date_maps(date_aggregates, chain, policy, "lifecycle_all")
            del base_maps
            for right in rights:
                metrics, events = _right_dte_maps(date_aggregates, chain, policy, kind="right", name=right)
                groups[f"{chain}|all_period|{policy}|{right}|all"] = {
                    "group": {"chain": chain, "universe": "all_period", "policy": policy, "right": right, "dte": "all"},
                    "statistics": _summarize(metrics, dates_all, cfg,
                                             ratios={"oi_level_event_weighted": ("oi_mass", "oi_width")},
                                             event_counts=events),
                }
            for bucket in buckets:
                metrics, events = _right_dte_maps(date_aggregates, chain, policy, kind="dte", name=bucket)
                groups[f"{chain}|all_period|{policy}|all|{bucket}"] = {
                    "group": {"chain": chain, "universe": "all_period", "policy": policy, "right": "all", "dte": bucket},
                    "statistics": _summarize(metrics, dates_all, cfg,
                                             ratios={"oi_level_event_weighted": ("oi_mass", "oi_width")},
                                             event_counts=events),
                }
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


def _metric_row(payload):
    boot = payload.get("bootstrap") or {}
    support = payload.get("support") or {}
    return [
        _fmt(payload.get("estimate")), _fmt(boot.get("lower")), _fmt(boot.get("upper")),
        payload.get("actual_valid_date_count"), payload.get("missing_date_count"),
        support.get("independent_dates"), support.get("events"), support.get("sparse"),
        _fmt(payload.get("event_weighted_estimate")),
    ]


def _findings(groups):
    lines = []
    for name in sorted(groups):
        block = groups[name]["statistics"]
        if block.get("all_values_missing"):
            continue
        for metric in ("oi_level_date_mean", "next_delta", "asof_0930_available_fraction",
                       "coverage_fraction", "update_difference_mean"):
            payload = (block.get("metrics") or {}).get(metric)
            if not payload or payload.get("estimate") is None:
                continue
            boot = payload.get("bootstrap") or {}
            support = payload.get("support") or {}
            unit = {
                "oi_level_date_mean": "contracts (equal-date mean of daily mean OI)",
                "next_delta": "contracts (equal-date mean of adjacent first/last delta)",
                "asof_0930_available_fraction": "fraction of unique-contract universe",
                "coverage_fraction": "listed contracts with OI / listed contracts",
                "update_difference_mean": "contracts (last-first within request date)",
            }[metric]
            lines.append(
                f"- `{_md_cell(name)}` `{metric}`: {_fmt(payload['estimate'])} {unit}; "
                f"CI [{_fmt(boot.get('lower'))}, {_fmt(boot.get('upper'))}] at "
                f"{_fmt(boot.get('confidence'))}; support {support.get('independent_dates')} dates / "
                f"{support.get('events')} raw observations; sparse={support.get('sparse')}"
            )
            if len(lines) >= 12:
                return lines
    return lines


def write_results_md(outputs, *, protocol, groups, cfg, counts, selected_dates, output_refs=None):
    clocks = protocol["clocks"]
    lines = [
        "# Options OI report/lifecycle results",
        "",
        "Source-derived candidate estimates from admitted OI/listing files. "
        "No first/last, cut, or position-date assumption is selected as the winner. "
        "The family is not complete.",
        "Verified known_at_ns, received_at_ns, published_at_ns and position_date are NULL. causal_feature_eligible is FALSE.",
        "Source-clock as-of rows are retrospective scenarios (ts_event_ns <= cut). They are not actual predictive evaluation.",
        "Dates with no OI rows are unknown, not zero. VIX listing denominators are unknown. Absence is never filled.",
        "Typed OIReport/oi_endpoint/OIReportChanges helpers were not used; certified clocks and supersedes are unavailable.",
        "",
        "## Population and clocks",
        "",
        f"- Family: {protocol['family']}",
        f"- Chains: {', '.join(protocol['population']['chains'])}",
        f"- Inclusive dates: {protocol['population']['first_date']} through {protocol['population']['last_date']}",
        f"- Stages (half-open): {protocol['population']['stages']}",
        f"- As-of cuts (Eastern): {', '.join(clocks['asof_cuts_local'])}",
        f"- Position assumptions: {clocks['assumptions']}",
        f"- Primary clock note: {clocks['source_document']['paraphrase']}",
        f"- Operational selection: {'pilot ' + ','.join(selected_dates) if selected_dates else 'full admitted population'}",
        f"- Bootstrap: seed {cfg['seed']}, block {cfg['block_length']}, replicates {cfg['replicates']}, "
        f"confidence {cfg['confidence']}, min dates {cfg['minimum_dates']}, min events {cfg['minimum_events']}",
        f"- Source files/rows/bytes read: {counts.get('source_files_read')}/"
        f"{counts.get('source_rows_read')}/{counts.get('source_bytes_read')}",
        f"- Intended chain-date units: {counts.get('intended_chain_date_units')}",
        "",
        "## Output artifacts",
        "",
    ]
    for key, ref in (output_refs or {}).items():
        if isinstance(ref, list):
            paths = ", ".join(f"[{item.get('path')}]({item.get('path')})" for item in ref[:4])
            lines.append(f"- {key}: {paths}")
        elif isinstance(ref, dict) and ref.get("path"):
            lines.append(f"- {key}: [{ref['path']}]({ref['path']})")
    lines.extend([
        "",
        "## Numeric findings",
        "",
        "Equal-date means (one weight per date). CI is the moving-block date bootstrap. "
        "Raw support is contract/observation counts, not the number of date cells.",
        "",
    ])
    findings = _findings(groups)
    lines.extend(findings or ["- No defined numeric estimates in this operational selection."])
    lines.extend([
        "",
        "## Remaining dependencies",
        "",
        "- Quotes, IV, flow, Greek exposures and futures-options sources stay on separate branches.",
        "- No dealer ownership, settlement timestamp or multiplier is applied to counts.",
        "- Daily listings are observed snapshots, not a certified as-known universe.",
        "- No Context fit. Full-family completion is not claimed.",
        "",
        "## Group estimates",
        "",
        "| group | metric | estimate | ci_low | ci_high | valid_dates | missing_dates | support_dates | support_events | sparse | event_weighted |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for name in sorted(groups):
        block = groups[name]["statistics"]
        metrics = block.get("metrics") or {}
        group_cell = _md_cell(name)
        for metric, payload in metrics.items():
            if metric in {"oi_mass", "oi_width"}:
                continue
            ratio = (block.get("ratios") or {}).get("oi_level_event_weighted")
            if metric == "oi_level_date_mean" and ratio:
                payload = dict(payload)
                payload["event_weighted_estimate"] = ratio.get("estimate")
            row = _metric_row(payload)
            lines.append(
                f"| {group_cell} | {metric} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]} |"
            )
        for ratio_name, payload in (block.get("ratios") or {}).items():
            row = _metric_row(payload)
            lines.append(
                f"| {group_cell} | ratio:{ratio_name} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]} |"
            )
    lines.extend([
        "",
        "## Equal-date empirical quantiles of the date-level series",
        "",
        "Each date has one weight. These are not event-weighted quantiles. "
        "Event-weighted points use the mass/count ratio separately. "
        "Contract observations are not additional independent dates. "
        "censor_boundary_fraction uses only the separately retained source-boundary endpoint population; "
        "its event support reports that boundary count.",
        "",
    ])
    for name in sorted(groups):
        metrics = groups[name]["statistics"].get("metrics") or {}
        if groups[name]["statistics"].get("all_values_missing"):
            lines.append(f"- `{_md_cell(name)}`: all metrics undefined; missing_date_count="
                         f"{groups[name]['statistics']['intended_date_count']}")
            continue
        for metric, payload in metrics.items():
            q = payload.get("date_quantiles") or {}
            if not q or all(value is None for value in q.values()):
                continue
            parts = ", ".join(f"q{level}={_fmt(value)}" for level, value in q.items())
            lines.append(f"- `{_md_cell(name)}` `{metric}`: {parts}")
    lines.extend(["", f"Statistics version: {VERSION}", ""])
    payload = ("\n".join(lines)).encode()
    with outputs.create("results.md") as stream:
        stream.write(payload)
    return outputs.reference("results.md", kind="options_oi_results_md_v2")


def run_statistics(date_aggregates, *, protocol, outputs, intended_all, selected_dates, chains, stages,
                   read_counts=None, output_refs=None):
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError("registered BoundedOutputs required")
    if type(date_aggregates) is not list:
        raise ContractError("date aggregates list required")
    groups, cfg = build_group_statistics(
        date_aggregates, protocol=protocol, intended_all=intended_all,
        chains=chains, stages=stages, selected_dates=selected_dates,
    )
    counts = {
        "group_count": len(groups),
        "source_files_read": None if not read_counts else read_counts.get("source_files_read"),
        "source_rows_read": None if not read_counts else read_counts.get("source_rows_read"),
        "source_bytes_read": None if not read_counts else read_counts.get("source_bytes_read"),
        "intended_chain_date_units": (
            read_counts.get("intended_chain_date_units") if read_counts
            else (None if selected_dates is None else len(selected_dates) * len(chains))
        ),
    }
    stats_ref = outputs.json("statistics.json", {
        "kind": VERSION,
        "configuration": cfg,
        "candidate_definitions": [
            "first_sourceclock", "last_sourceclock",
            "position_date_by_request_previous_cash",
            "position_date_by_event_previous_cash",
            "asof_0930", "asof_1000", "asof_1500",
            "next_first_first", "next_last_last",
        ],
        "winner": None,
        "full_family_complete": False,
        "groups": groups,
    }, kind="options_oi_statistics_v2")
    dist_ref = outputs.json("distributions.json", {
        "kind": "options_oi_date_distributions_v2",
        "quantiles": list(cfg["quantiles"]),
        "note": "Equal-date empirical quantiles of the date-level series. Event-weighted points are mass/count ratios.",
        "groups": {name: {
            metric: payload.get("date_quantiles")
            for metric, payload in (block["statistics"].get("metrics") or {}).items()
        } for name, block in groups.items()},
    }, kind="options_oi_distributions_v2")
    md_ref = write_results_md(
        outputs, protocol=protocol, groups=groups, cfg=cfg,
        counts=counts, selected_dates=selected_dates, output_refs=output_refs,
    )
    return {"refs": {"statistics": stats_ref, "distributions": dist_ref, "results_md": md_ref},
            "groups": groups, "configuration": cfg}


def date_balanced_point(date_values):
    """Equal-date mean of supplied date values. Independent of implementation internals."""
    present = [value for value in date_values.values() if value is not None]
    if not present:
        return None
    return sum(present) / len(present)


def finish_measurement_outputs(
    outputs, *, spec, calendar_ref, identity_w, except_w, member_w, report_w, life_w,
    interval_w, asof_agg_w, coverage_table, coverage_kind, date_aggregates, consumed,
    required_ids, manifest, files_read, rows_read, bytes_read, source_dates, selected_dates,
    intended_all, intended_labels, chains, listing_unknown_chains, started_cpu, started_wall,
    reconstruction_payload, family, version, remaining, interval_reconstruction,
    max_worker_bytes, max_source_file,
):
    """Shared measurement closeout so the columnar runner stays one-pass."""
    if consumed != set(required_ids):
        raise IntegrityError("membership does not match all selected admitted records")
    identity_refs = identity_w.finish()
    exception_refs = except_w.finish()
    membership_refs = member_w.finish()
    report_refs = report_w.finish()
    life_refs = life_w.finish()
    interval_refs = interval_w.finish()
    asof_agg_refs = asof_agg_w.finish()
    import pyarrow.parquet as pq
    stream = outputs.create("coverage.parquet")
    try:
        pq.write_table(coverage_table, stream, compression="zstd")
    finally:
        stream.close()
    coverage_ref = {**outputs.reference("coverage.parquet", kind=coverage_kind), "rows": len(coverage_table)}
    aggregates_ref = outputs.json("date-aggregates.json", date_aggregates, kind="options_oi_date_aggregates_v2")
    reconstruction_ref = outputs.json("reconstruction.json", reconstruction_payload,
                                     kind=reconstruction_payload["kind"])
    manifest_ref = outputs.json("source-manifest.json", {
        "kind": "options_oi_source_path_hash_lookup_v2",
        "note": "file_id+row_index recover provenance; source bytes stay in /workspace/data",
        "files": manifest,
    }, kind="options_oi_source_manifest_v2")
    intended_units = len(selected_dates or intended_labels) * len(chains)
    output_refs = {
        "identity_map": identity_refs, "exceptions": exception_refs, "membership": membership_refs,
        "reports": report_refs, "lifecycle": life_refs, "asof_intervals": interval_refs,
        "asof_aggregates": asof_agg_refs, "coverage": coverage_ref,
        "reconstruction": reconstruction_ref,
    }
    statistics_start_cpu = pytime.process_time()
    statistics_start_output = outputs.written
    production_cpu_seconds = statistics_start_cpu - started_cpu
    stats = run_statistics(
        date_aggregates, protocol=spec, outputs=outputs,
        intended_all=[d.isoformat() if hasattr(d, "isoformat") else d for d in intended_all],
        selected_dates=selected_dates, chains=chains, stages=spec["population"]["stages"],
        read_counts={
            "source_files_read": files_read, "source_rows_read": rows_read,
            "source_bytes_read": bytes_read, "intended_chain_date_units": intended_units,
        },
        output_refs=output_refs,
    )
    cpu = pytime.process_time() - started_cpu
    wall = pytime.perf_counter() - started_wall
    full_files = sum(item["source_file_count"] for item in spec["source_datasets"])
    full_units = len(intended_all) * len(chains)
    refs = {
        "calendar": calendar_ref, "source_manifest": manifest_ref,
        "identity_map": identity_refs, "exceptions": exception_refs, "membership": membership_refs,
        "reports": report_refs, "coverage": coverage_ref, "asof_intervals": interval_refs,
        "asof_aggregates": asof_agg_refs, "lifecycle": life_refs,
        "date_aggregates": aggregates_ref, "reconstruction": reconstruction_ref,
        "statistics": stats["refs"]["statistics"], "distributions": stats["refs"]["distributions"],
        "results_md": stats["refs"]["results_md"],
    }
    return {
        "passed": True,
        "full_family_complete": False,
        "family": family,
        "version": version,
        "refs": refs,
        "counts": {
            "source_files_read": files_read, "source_rows_read": rows_read,
            "source_bytes_read": bytes_read, "intended_chain_date_units": intended_units,
            "coverage_rows": len(coverage_table), "report_rows": report_w.rows,
            "lifecycle_rows": life_w.rows, "interval_rows": interval_w.rows,
            "exception_rows": except_w.rows, "identity_rows": identity_w.rows,
            "listing_unknown_chains": listing_unknown_chains, "chains": list(chains),
        },
        "resources": {
            "cpu_seconds": cpu, "wall_seconds": wall, "output_bytes": outputs.written,
            "production_cpu_seconds": production_cpu_seconds,
            "statistics_cpu_seconds": pytime.process_time() - statistics_start_cpu,
            "production_output_bytes": statistics_start_output,
            "statistics_output_bytes": outputs.written - statistics_start_output,
            "source_bytes_read": bytes_read, "source_files_read": files_read,
            "source_rows_read": rows_read, "intended_chain_date_units": intended_units,
            "memory_bound_bytes": max_worker_bytes, "source_file_bound_bytes": max_source_file,
            "full_gate_projection": "computed by registered supervisor from admitted full rows/files/dates and measured pilot; not inferred from this selection",
        },
        "source_dates_processed": sorted(set(source_dates)),
        "selected_dates": selected_dates,
        "remaining_dependencies": list(remaining),
        "clock_interpretation": {
            "known_at_ns": None, "received_at_ns": None, "published_at_ns": None,
            "position_date": None, "causal_feature_eligible": False,
            "assumptions": spec["clocks"]["assumptions"],
            "asof": spec["clocks"]["asof"],
            "reconstruction": interval_reconstruction,
        },
    }


__all__ = [
    "VERSION", "build_group_statistics", "date_balanced_point", "date_quantiles",
    "empty_metric", "empty_ratio", "finish_measurement_outputs", "run_statistics",
    "universe_dates",
]
