"""Date aggregates, candidate-definition statistics and the readable OI report.

Source-clock timing and position-date assumptions are descriptive. They are not
actual predictive evaluation. Cuts and contract observations are not treated as
independent dates. All candidate first/last and position-clock definitions are
reported; this module does not choose a winner.

OI zero is a valid observation. Absence, missing publication and listing-unknown
stay missing (estimate None), never coerced to zero. Coverage, missing and censor
fractions use intended-eligible denominators, not only positive observations.
"""
from __future__ import annotations

from collections import defaultdict

from trading_research.errors import ContractError
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.scoring import quantile


VERSION = "options-oi-report-lifecycle-statistics-v1"
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)


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


def _mean(num, den):
    return _ratio(num, den)


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


def _cells_from_dates(dates, values):
    return {day: values.get(day) for day in dates if values.get(day) is not None}


def _summarize(metrics, dates, cfg, *, ratios=None, estimator="date_mean"):
    if not metrics or all(not any(cell is not None for cell in values.values()) for values in metrics.values()):
        return {
            "schema": "observed-date-statistics-v1",
            "intended_dates": list(dates),
            "intended_date_count": len(dates),
            "metrics": {name: empty_metric(dates) for name in (metrics or {"undefined": {}})},
            "ratios": {},
            "all_values_missing": True,
        }
    filled = {}
    for name, values in metrics.items():
        filled[name] = {day: values[day] for day in dates if day in values and values[day] is not None}
        if not filled[name]:
            filled[name] = {}
    present = {name: cells for name, cells in filled.items() if cells}
    if not present:
        return {
            "schema": "observed-date-statistics-v1",
            "intended_dates": list(dates),
            "intended_date_count": len(dates),
            "metrics": {name: empty_metric(dates) for name in metrics},
            "ratios": {},
            "all_values_missing": True,
        }
    result = observed_date_statistics(
        present, dates, ratios=ratios, estimator=estimator,
        seed=cfg["seed"], block_length=cfg["block_length"], replicates=cfg["replicates"],
        confidence=cfg["confidence"], minimum_independent_dates=cfg["minimum_dates"],
        minimum_events=cfg["minimum_events"], _retain_replicate_estimates=False,
    )
    for name, payload in result["metrics"].items():
        series = [present[name][day] for day in dates if day in present[name]]
        payload["date_quantiles"] = date_quantiles(series, cfg["quantiles"])
        payload["missing_date_count"] = len(dates) - payload.get("actual_valid_date_count", 0)
    result["all_values_missing"] = False
    return result


def _date_maps(rows, chain, policy):
    """Build per-date scalar maps from sufficient aggregates. Missing stays absent."""
    oi_mean, oi_zero, seconds = {}, {}, {}
    coverage, missing_oi = {}, {}
    oi_sum, oi_n = {}, {}
    update_frac, update_diff = {}, {}
    common_first, common_last, paired = {}, {}, {}
    life = {
        "delta": {}, "abs_delta": {}, "pos": {}, "zero": {}, "neg": {},
        "censor_missing": {}, "censor_expired": {}, "censor_boundary": {},
        "first_observed": {},
    }
    asof = defaultdict(lambda: {"available": {}, "stale": {}, "rejected": {}})
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
        if acc["seconds_n"]:
            seconds[day] = acc["seconds_sum"] / acc["seconds_n"]
        if row["listing_denominator_known"] and row["listing_count"] not in (None, 0):
            coverage[day] = row["coverage_listed_with_oi"]
            missing_oi[day] = None if row["listed_without_oi"] is None else row["listed_without_oi"] / row["listing_count"]
        usable = row["usable_report_count"]
        if usable:
            update_frac[day] = row["update_candidate_count"] / usable
        diffs = []
        # update difference is not stored as a sum on the date row; leave absent unless usable reports exist
        if acc["common_n"]:
            common_first[day] = acc["common_first_sum"] / acc["common_n"]
            common_last[day] = acc["common_last_sum"] / acc["common_n"]
            paired[day] = acc["paired_diff_sum"] / acc["common_n"]
        life_acc = row["lifecycle_first_first" if policy == "first" else "lifecycle_last_last"]
        attempts = life_acc["n_attempts"]
        if life_acc["n"]:
            life["delta"][day] = life_acc["delta_sum"] / life_acc["n"]
            life["abs_delta"][day] = life_acc["abs_sum"] / life_acc["n"]
            life["pos"][day] = life_acc["n_pos"] / life_acc["n"]
            life["zero"][day] = life_acc["n_zero"] / life_acc["n"]
            life["neg"][day] = life_acc["n_neg"] / life_acc["n"]
        if attempts:
            life["censor_missing"][day] = life_acc["n_censor_missing"] / attempts
            life["censor_expired"][day] = life_acc["n_censor_expired"] / attempts
            life["censor_boundary"][day] = life_acc["n_censor_boundary"] / attempts
            life["first_observed"][day] = life_acc["n_first_observed"] / attempts
        for cut, payload in row.get("asof", {}).items():
            den = payload["available"] + payload["rejected_today"]
            if payload["available"]:
                asof[cut]["available"][day] = payload["available"] / den if den else None
                asof[cut]["stale"][day] = payload["stale"] / payload["available"]
            if den:
                asof[cut]["rejected"][day] = payload["rejected_today"] / den
        del diffs
    return {
        "oi_level_date": oi_mean, "oi_zero_fraction": oi_zero, "report_seconds": seconds,
        "coverage_fraction": coverage, "missing_oi_fraction": missing_oi,
        "oi_sum": oi_sum, "oi_n": oi_n, "update_candidate_fraction": update_frac,
        "common_first": common_first, "common_last": common_last, "first_minus_last": paired,
        "life": life, "asof": asof,
    }


def _slice_maps(maps, dates):
    def keep(values):
        return {day: values[day] for day in dates if day in values}

    life = {name: keep(values) for name, values in maps["life"].items()}
    asof = {}
    for cut, payload in maps["asof"].items():
        asof[cut] = {name: keep(values) for name, values in payload.items()}
    return {
        "oi_level_date": keep(maps["oi_level_date"]),
        "oi_zero_fraction": keep(maps["oi_zero_fraction"]),
        "report_seconds": keep(maps["report_seconds"]),
        "coverage_fraction": keep(maps["coverage_fraction"]),
        "missing_oi_fraction": keep(maps["missing_oi_fraction"]),
        "oi_sum": keep(maps["oi_sum"]),
        "oi_n": keep(maps["oi_n"]),
        "update_candidate_fraction": keep(maps["update_candidate_fraction"]),
        "common_first": keep(maps["common_first"]),
        "common_last": keep(maps["common_last"]),
        "first_minus_last": keep(maps["first_minus_last"]),
        "life": life,
        "asof": asof,
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
    }
    for cut, payload in maps["asof"].items():
        tag = cut.replace(":", "")
        metrics[f"asof_{tag}_available_fraction"] = payload["available"]
        metrics[f"asof_{tag}_stale_fraction"] = payload["stale"]
        metrics[f"asof_{tag}_rejected_fraction"] = payload["rejected"]
    ratios = {
        "oi_level_event_weighted": ("oi_mass", "oi_width"),
        "common_first_over_last": ("common_support_first", "common_support_last"),
    }
    return metrics, ratios


def _right_dte_maps(rows, chain, policy, *, kind, name):
    oi_mean, oi_n, oi_sum = {}, {}, {}
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
    return {"oi_level_date_mean": oi_mean, "oi_mass": oi_sum, "oi_width": oi_n}


def build_group_statistics(date_aggregates, *, protocol, intended_all, chains, stages, selected_dates=None):
    cfg = _cfg(protocol)
    dates_all = list(selected_dates or intended_all)
    years = sorted({label[:4] for label in dates_all})
    groups = {}
    for chain in chains:
        for policy in ("first", "last"):
            maps = _date_maps(date_aggregates, chain, policy)
            universes = [("all_period", dates_all)]
            for year in years:
                universes.append((f"year_{year}", [d for d in dates_all if d.startswith(year)]))
            for stage in stages:
                universes.append((f"stage_{stage}", universe_dates(dates_all, stage=stage, stages=stages)))
            for uname, udates in universes:
                if not udates:
                    groups[f"{chain}|{uname}|{policy}|all|all"] = {
                        "group": {"chain": chain, "universe": uname, "policy": policy, "right": "all", "dte": "all"},
                        "statistics": _summarize({}, udates, cfg),
                    }
                    continue
                sliced = _slice_maps(maps, udates)
                metrics, ratios = _metric_bundle(sliced)
                groups[f"{chain}|{uname}|{policy}|all|all"] = {
                    "group": {"chain": chain, "universe": uname, "policy": policy, "right": "all", "dte": "all"},
                    "statistics": _summarize(metrics, udates, cfg, ratios=ratios),
                }
            rights = sorted({
                right for row in date_aggregates if row["chain"] == chain
                for right in row.get("by_right", {})
            })
            buckets = sorted({
                bucket for row in date_aggregates if row["chain"] == chain
                for bucket in row.get("by_dte", {})
            })
            for right in rights:
                metrics = _right_dte_maps(date_aggregates, chain, policy, kind="right", name=right)
                groups[f"{chain}|all_period|{policy}|{right}|all"] = {
                    "group": {"chain": chain, "universe": "all_period", "policy": policy, "right": right, "dte": "all"},
                    "statistics": _summarize(metrics, dates_all, cfg, ratios={"oi_level_event_weighted": ("oi_mass", "oi_width")}),
                }
            for bucket in buckets:
                metrics = _right_dte_maps(date_aggregates, chain, policy, kind="dte", name=bucket)
                groups[f"{chain}|all_period|{policy}|all|{bucket}"] = {
                    "group": {"chain": chain, "universe": "all_period", "policy": policy, "right": "all", "dte": bucket},
                    "statistics": _summarize(metrics, dates_all, cfg, ratios={"oi_level_event_weighted": ("oi_mass", "oi_width")}),
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


def _metric_row(payload):
    boot = payload.get("bootstrap") or {}
    support = payload.get("support") or {}
    return [
        _fmt(payload.get("estimate")), _fmt(boot.get("lower")), _fmt(boot.get("upper")),
        payload.get("actual_valid_date_count"), payload.get("missing_date_count"),
        support.get("independent_dates"), support.get("sparse"),
        _fmt(payload.get("event_weighted_estimate")),
    ]


def write_results_md(outputs, *, protocol, groups, cfg, counts, selected_dates):
    clocks = protocol["clocks"]
    lines = [
        "# Options OI report/lifecycle results",
        "",
        "This report contains candidate definitions only. No first/last, cut, or position-date assumption is selected as the winner.",
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
        "## Remaining dependencies",
        "",
        "- Quotes, IV, flow, Greek exposures and futures-options sources stay on separate branches.",
        "- No dealer ownership, settlement timestamp or multiplier is applied to counts.",
        "- Daily listings are observed snapshots, not a certified as-known universe.",
        "- No Context fit.",
        "",
        "## Group estimates",
        "",
        "| group | metric | estimate | ci_low | ci_high | valid_dates | missing_dates | support_dates | sparse | event_weighted |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in sorted(groups):
        block = groups[name]["statistics"]
        metrics = block.get("metrics") or {}
        for metric, payload in metrics.items():
            if metric in {"oi_mass", "oi_width"}:
                continue
            ratio = (block.get("ratios") or {}).get("oi_level_event_weighted")
            if metric == "oi_level_date_mean" and ratio:
                payload = dict(payload)
                payload["event_weighted_estimate"] = ratio.get("estimate")
            row = _metric_row(payload)
            lines.append(
                f"| {name} | {metric} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} |"
            )
        for ratio_name, payload in (block.get("ratios") or {}).items():
            row = _metric_row(payload)
            lines.append(
                f"| {name} | ratio:{ratio_name} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} |"
            )
    lines.extend([
        "",
        "## Date-weighted quantiles of date-level series",
        "",
        "Event-weighted points use the mass/count ratio (equal-date means are not reweighted by that ratio).",
        "Contract observations are not additional independent dates.",
        "",
    ])
    for name in sorted(groups):
        metrics = groups[name]["statistics"].get("metrics") or {}
        if groups[name]["statistics"].get("all_values_missing"):
            lines.append(f"- `{name}`: all metrics undefined; missing_date_count="
                         f"{groups[name]['statistics']['intended_date_count']}")
            continue
        for metric, payload in metrics.items():
            q = payload.get("date_quantiles") or {}
            if not q or all(value is None for value in q.values()):
                continue
            parts = ", ".join(f"q{level}={_fmt(value)}" for level, value in q.items())
            lines.append(f"- `{name}` `{metric}`: {parts}")
    lines.extend(["", f"Statistics version: {VERSION}", ""])
    payload = ("\n".join(lines)).encode()
    with outputs.create("results.md") as stream:
        stream.write(payload)
    return outputs.reference("results.md", kind="options_oi_results_md_v1")


def run_statistics(date_aggregates, *, protocol, outputs, intended_all, selected_dates, chains, stages,
                   read_counts=None):
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
        "groups": groups,
    }, kind="options_oi_statistics_v1")
    dist_ref = outputs.json("distributions.json", {
        "kind": "options_oi_date_distributions_v1",
        "quantiles": list(cfg["quantiles"]),
        "note": "Date-weighted quantiles of date-level series. Event-weighted points are mass/count ratios.",
        "groups": {name: {
            metric: payload.get("date_quantiles")
            for metric, payload in (block["statistics"].get("metrics") or {}).items()
        } for name, block in groups.items()},
    }, kind="options_oi_distributions_v1")
    md_ref = write_results_md(
        outputs, protocol=protocol, groups=groups, cfg=cfg,
        counts=counts, selected_dates=selected_dates,
    )
    return {"refs": {"statistics": stats_ref, "distributions": dist_ref, "results_md": md_ref},
            "groups": groups, "configuration": cfg}


def date_balanced_point(date_values):
    """Equal-date mean of supplied date values. Independent of implementation internals."""
    present = [value for value in date_values.values() if value is not None]
    if not present:
        return None
    return sum(present) / len(present)


__all__ = [
    "VERSION", "build_group_statistics", "date_balanced_point", "date_quantiles",
    "empty_metric", "run_statistics", "universe_dates",
]
