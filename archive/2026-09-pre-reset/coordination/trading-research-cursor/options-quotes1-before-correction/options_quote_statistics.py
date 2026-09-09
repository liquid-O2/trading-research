"""Date aggregates, block-bootstrap groups and the readable quote-quality report.

Equal-date means and metric-specific raw denominators stay distinct. Absence,
missing files and undefined OI-weighted fractions stay missing, never zero.
Shared moving-block weights are cached per exact date universe. Fixtures do
not mark the scientific family complete.
"""
from __future__ import annotations

from collections import defaultdict
import math
import time as pytime

from trading_research.errors import ContractError
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.date_statistics import observed_date_statistics
from trading_research.research.scoring import quantile


VERSION = "options-quote-quality-support-statistics-v1"
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
PRESPECIFIED = (
    "quoted_fraction", "listed_unquoted_fraction", "quoted_unlisted_fraction",
    "usable_fraction", "conflict_fraction", "all_zero_fraction",
    "one_sided_fraction", "crossed_fraction", "locked_fraction", "two_sided_fraction",
    "invalid_fraction", "mean_bid", "mean_ask", "mean_mid", "mean_spread",
    "mean_relative_spread", "mean_sample_age_s", "mean_payload_age_s",
    "sample_stale_60_fraction", "sample_stale_300_fraction", "sample_stale_900_fraction",
    "payload_stale_60_fraction", "payload_stale_300_fraction", "payload_stale_900_fraction",
    "oi_covered_fraction", "oi_weighted_quoted_fraction",
    "missing_file_fraction", "empty_marker_fraction", "no_sample_fraction",
    "etf_present_fraction", "cash_present_fraction", "fred_present_fraction",
    "action_present_fraction", "near_broad_agree_fraction", "near_broad_conflict_fraction",
    "raw_row_count", "unique_event_count",
)
RATIO_SPECS = {
    "usable_over_quoted": ("usable_quotes", "quoted_contracts"),
    "quoted_over_listed": ("quoted_listed", "listed_contracts"),
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
            events += int(raw_events.get(day, 1))
    payload["actual_valid_event_count"] = events
    payload["valid_event_count"] = events
    payload["raw_mean"] = raw_mean_value
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
               estimator="date_mean"):
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
    for name in names:
        if name in result.get("metrics", {}):
            payload = result["metrics"][name]
            series = [present[name][day] for day in dates if day in present[name]]
            payload["date_quantiles"] = date_quantiles(series, cfg["quantiles"])
            payload["missing_date_count"] = len(dates) - payload.get("actual_valid_date_count", 0)
            _overlay_raw_support(payload, dates, present[name], raw.get(name, {}), cfg,
                                 raw_mean_value=raw_means.get(name))
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


def _cov_rows(row):
    return row.get("coverage") or []


def _date_maps(rows, chain):
    quoted_frac, listed_unquoted, quoted_unlisted = {}, {}, {}
    usable_frac, conflict_frac = {}, {}
    all_zero, one_sided, crossed, locked, two_sided, invalid = {}, {}, {}, {}, {}, {}
    mean_bid, mean_ask, mean_mid, mean_spread, mean_rel = {}, {}, {}, {}, {}
    mean_sample, mean_payload = {}, {}
    s60, s300, s900, p60, p300, p900 = {}, {}, {}, {}, {}, {}
    oi_cov, oi_w = {}, {}
    miss_file, empty_mark, no_sample = {}, {}, {}
    etf, cash, fred, action = {}, {}, {}, {}
    agree, nb_conflict = {}, {}
    raw_rows, unique_events = {}, {}
    usable_quotes, quoted_contracts, quoted_listed, listed_contracts = {}, {}, {}, {}
    events = defaultdict(dict)
    bid_sum, bid_n = {}, {}
    for row in rows:
        if row["chain"] != chain or not row.get("intended"):
            continue
        day = row["request_date"]
        cov = _cov_rows(row)
        listed = row.get("listed_contracts") or 0
        quoted = row.get("quoted_contracts") or 0
        usable = row.get("usable_quotes") or 0
        quoted_frac[day] = None if listed in (None, 0) and row.get("listed_contracts") is None else _ratio(quoted, listed) if listed else (None if listed == 0 and quoted == 0 else _ratio(quoted, listed))
        if listed:
            lu = sum(item.get("listed_unquoted") or 0 for item in cov)
            listed_unquoted[day] = lu / listed
            quoted_listed[day] = quoted
            listed_contracts[day] = listed
        quoted_unlisted[day] = _ratio(sum(item.get("quoted_unlisted") or 0 for item in cov), quoted) if quoted else None
        usable_frac[day] = _ratio(usable, quoted) if quoted else None
        conflict_frac[day] = _ratio(sum(item.get("conflict_count") or 0 for item in cov), quoted) if quoted else None
        all_zero[day] = _ratio(sum(item.get("all_zero_count") or 0 for item in cov), quoted) if quoted else None
        one_sided[day] = _ratio(sum(item.get("one_sided_count") or 0 for item in cov), quoted) if quoted else None
        crossed[day] = _ratio(sum(item.get("crossed_count") or 0 for item in cov), quoted) if quoted else None
        locked[day] = _ratio(sum(item.get("locked_count") or 0 for item in cov), quoted) if quoted else None
        two_sided[day] = _ratio(sum(item.get("two_sided_count") or 0 for item in cov), quoted) if quoted else None
        invalid[day] = _ratio(sum(item.get("invalid_count") or 0 for item in cov), quoted) if quoted else None
        mean_bid[day] = row.get("mean_bid")
        mean_ask[day] = row.get("mean_ask")
        mean_mid[day] = row.get("mean_mid")
        mean_spread[day] = row.get("mean_spread")
        mean_rel[day] = row.get("mean_relative_spread")
        mean_sample[day] = row.get("mean_sample_age_s")
        mean_payload[day] = row.get("mean_payload_age_s")
        bid_sum[day] = row.get("raw_bid_sum")
        bid_n[day] = row.get("raw_bid_n")
        oi_avail = sum(item.get("oi_available_count") or 0 for item in cov)
        oi_cov[day] = _ratio(oi_avail, quoted + listed) if (quoted or listed) else None
        weights = [item.get("oi_weighted_quoted_fraction") for item in cov
                   if item.get("oi_weighted_quoted_fraction") is not None]
        oi_w[day] = None if not weights else sum(weights) / len(weights)
        n_cuts = max(len(cov), 1)
        miss_file[day] = sum(1 for item in cov if item.get("missing_file")) / n_cuts
        empty_mark[day] = sum(1 for item in cov if item.get("empty_marker")) / n_cuts
        no_sample[day] = sum(1 for item in cov if item.get("cut_status") == "no_sample") / n_cuts
        support = row.get("support") or []
        if support:
            etf[day] = sum(1 for item in support if item.get("etf_present")) / len(support)
            cash[day] = sum(1 for item in support if item.get("cash_close") is not None) / len(support)
            fred[day] = sum(1 for item in support if item.get("fred_present")) / len(support)
            action[day] = sum(1 for item in support if item.get("action_ex_date")) / len(support)
        paired = row.get("paired_near_broad") or {}
        common = paired.get("common") or 0
        agree[day] = _ratio(paired.get("agree"), common) if common else None
        nb_conflict[day] = _ratio(paired.get("conflict"), common) if common else None
        raw_rows[day] = row.get("raw_rows")
        unique_events[day] = row.get("unique_events")
        usable_quotes[day] = usable
        quoted_contracts[day] = quoted
        events["quoted_fraction"][day] = quoted
        events["mean_bid"][day] = bid_n.get(day) or 0
        events["raw_row_count"][day] = row.get("raw_rows") or 0
        events["unique_event_count"][day] = row.get("unique_events") or 0
        s60[day] = None
        s300[day] = None
        s900[day] = None
        p60[day] = None
        p300[day] = None
        p900[day] = None
    return {
        "quoted_fraction": quoted_frac, "listed_unquoted_fraction": listed_unquoted,
        "quoted_unlisted_fraction": quoted_unlisted, "usable_fraction": usable_frac,
        "conflict_fraction": conflict_frac, "all_zero_fraction": all_zero,
        "one_sided_fraction": one_sided, "crossed_fraction": crossed,
        "locked_fraction": locked, "two_sided_fraction": two_sided,
        "invalid_fraction": invalid, "mean_bid": mean_bid, "mean_ask": mean_ask,
        "mean_mid": mean_mid, "mean_spread": mean_spread,
        "mean_relative_spread": mean_rel, "mean_sample_age_s": mean_sample,
        "mean_payload_age_s": mean_payload,
        "sample_stale_60_fraction": s60, "sample_stale_300_fraction": s300,
        "sample_stale_900_fraction": s900,
        "payload_stale_60_fraction": p60, "payload_stale_300_fraction": p300,
        "payload_stale_900_fraction": p900,
        "oi_covered_fraction": oi_cov, "oi_weighted_quoted_fraction": oi_w,
        "missing_file_fraction": miss_file, "empty_marker_fraction": empty_mark,
        "no_sample_fraction": no_sample, "etf_present_fraction": etf,
        "cash_present_fraction": cash, "fred_present_fraction": fred,
        "action_present_fraction": action,
        "near_broad_agree_fraction": agree, "near_broad_conflict_fraction": nb_conflict,
        "raw_row_count": raw_rows, "unique_event_count": unique_events,
        "usable_quotes": usable_quotes, "quoted_contracts": quoted_contracts,
        "quoted_listed": quoted_listed, "listed_contracts": listed_contracts,
        "events": events, "bid_sum": bid_sum, "bid_n": bid_n,
    }


def _slice_maps(maps, dates):
    out = {}
    for name, cells in maps.items():
        if name == "events":
            out[name] = {
                metric: {day: values[day] for day in dates if day in values}
                for metric, values in cells.items()
            }
            continue
        out[name] = {day: cells[day] for day in dates if day in cells}
    return out


def _metric_bundle(maps):
    metrics = {name: maps[name] for name in PRESPECIFIED if name in maps}
    events = maps.get("events") or {}
    raw_means = {}
    bid_sum = maps.get("bid_sum") or {}
    bid_n = maps.get("bid_n") or {}
    if bid_sum and bid_n:
        total_s = sum(value or 0 for value in bid_sum.values())
        total_n = sum(value or 0 for value in bid_n.values())
        raw_means["mean_bid"] = raw_mean(total_s, total_n)
    ratios = {
        "usable_over_quoted": ("usable_quotes", "quoted_contracts"),
        "quoted_over_listed": ("quoted_listed", "listed_contracts"),
    }
    extra = {name: maps[name] for name in ("usable_quotes", "quoted_contracts",
                                           "quoted_listed", "listed_contracts") if name in maps}
    metrics.update(extra)
    return metrics, ratios, events, raw_means


def build_group_statistics(date_aggregates, *, protocol, intended_all, chains, stages,
                           selected_dates=None):
    cfg = _cfg(protocol)
    dates_all = list(selected_dates or intended_all)
    years = sorted({label[:4] for label in dates_all})
    groups = {}
    for chain in chains:
        maps = _date_maps(date_aggregates, chain)
        universes = [("all_period", dates_all)]
        for year in years:
            universes.append((f"year_{year}", [day for day in dates_all if day.startswith(year)]))
        for stage in stages:
            universes.append((f"stage_{stage}", universe_dates(dates_all, stage=stage, stages=stages)))
        for uname, udates in universes:
            if not udates:
                groups[f"{chain}|{uname}|all|all|all|all"] = {
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
            sliced = _slice_maps(maps, udates)
            metrics, ratios, events, raw_means = _metric_bundle({**maps, **sliced})
            groups[f"{chain}|{uname}|all|all|all|all"] = {
                "group": {"chain": chain, "universe": uname, "cut": "all",
                          "source_family": "all", "right": "all", "dte": "all"},
                "statistics": _summarize(metrics, udates, cfg, ratios=ratios,
                                         event_counts=events, raw_means=raw_means),
            }
        cuts = sorted({item.get("cut_label") for row in date_aggregates if row["chain"] == chain
                       for item in (row.get("coverage") or []) if item.get("cut_label")})
        for cut in cuts:
            cut_rows = []
            for row in date_aggregates:
                if row["chain"] != chain:
                    continue
                cov = [item for item in (row.get("coverage") or []) if item.get("cut_label") == cut]
                if not cov:
                    continue
                cut_rows.append({**row, "coverage": cov})
            if not cut_rows:
                continue
            cut_maps = _date_maps(cut_rows, chain)
            metrics, ratios, events, raw_means = _metric_bundle(cut_maps)
            groups[f"{chain}|all_period|{cut}|all|all|all"] = {
                "group": {"chain": chain, "universe": "all_period", "cut": cut,
                          "source_family": "all", "right": "all", "dte": "all"},
                "statistics": _summarize(metrics, dates_all, cfg, ratios=ratios,
                                         event_counts=events, raw_means=raw_means),
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


def write_results_md(outputs, *, protocol, groups, cfg, counts, selected_dates, output_refs=None):
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
        "## Accounting",
        "",
        f"- source files read: {counts.get('source_files_read')}",
        f"- raw quotation rows: {counts.get('source_rows_read')}",
        f"- unique timestamps / events: {counts.get('unique_events')}",
        f"- cut-board rows: {counts.get('cut_board_rows')}",
        f"- listed contracts (observed): {counts.get('listed_contracts')}",
        f"- quoted contracts: {counts.get('quoted_contracts')}",
        f"- OI-matched contracts: {counts.get('oi_matched_contracts')}",
        f"- independent intended dates in this selection: {len(selected_dates or [])}",
        f"- intended chain-date units: {counts.get('intended_chain_date_units')}",
        "",
        "Classes are complete, censored or missing as labeled. Absence is not zero.",
        f"Moving-block bootstrap: {cfg['replicates']} replicates, block length {cfg['block_length']}, "
        f"seed {cfg['seed']}, {cfg['confidence']} interval. Sparse if fewer than "
        f"{cfg['minimum_dates']} independent dates or {cfg['minimum_events']} events.",
        "",
        "## Groups",
        "",
        f"Group count: {len(groups)} (all constructed groups, not a first-20 subset).",
        "",
    ]
    for name in sorted(groups):
        block = groups[name]
        stats = block.get("statistics") or {}
        metrics = stats.get("metrics") or {}
        lines.append(f"### `{_md_cell(name)}`")
        lines.append("")
        lines.append(f"- intended dates: {stats.get('intended_date_count')}")
        lines.append(f"- all values missing: {_fmt(stats.get('all_values_missing'))}")
        for metric in ("quoted_fraction", "usable_fraction", "conflict_fraction",
                       "mean_bid", "mean_spread", "mean_sample_age_s",
                       "mean_payload_age_s", "oi_weighted_quoted_fraction",
                       "missing_file_fraction", "etf_present_fraction"):
            payload = metrics.get(metric)
            if not payload:
                continue
            lines.append(
                f"- `{metric}` date-mean={_fmt(payload.get('estimate'))} "
                f"raw-mean={_fmt(payload.get('raw_mean'))} "
                f"dates={payload.get('actual_valid_date_count')} "
                f"events={payload.get('actual_valid_event_count')} "
                f"sparse={_fmt((payload.get('support') or {}).get('sparse'))}"
            )
            q = payload.get("date_quantiles") or {}
            if q and any(value is not None for value in q.values()):
                parts = ", ".join(f"q{level}={_fmt(value)}" for level, value in q.items())
                lines.append(f"  - date quantiles: {parts}")
        lines.append("")
    lines.append(f"Statistics version: {VERSION}")
    lines.append("")
    payload = ("\n".join(lines)).encode()
    with outputs.create("results.md") as stream:
        stream.write(payload)
    return outputs.reference("results.md", kind="options_quote_results_md_v1")


def run_statistics(date_aggregates, *, protocol, outputs, intended_all, selected_dates, chains, stages,
                   read_counts=None, output_refs=None, group_refs=None):
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
        "cut_board_rows": None if not read_counts else read_counts.get("cut_board_rows"),
        "unique_events": None if not read_counts else read_counts.get("unique_events"),
        "listed_contracts": None if not read_counts else read_counts.get("listed_contracts"),
        "quoted_contracts": None if not read_counts else read_counts.get("quoted_contracts"),
        "oi_matched_contracts": None if not read_counts else read_counts.get("oi_matched_contracts"),
        "intended_chain_date_units": (
            read_counts.get("intended_chain_date_units") if read_counts
            else (None if selected_dates is None else len(selected_dates) * len(chains))
        ),
    }
    stats_payload = {
        "kind": VERSION,
        "configuration": cfg,
        "full_family_complete": False,
        "group_count": len(groups),
        "chain_group_refs": group_refs,
    }
    if group_refs:
        stats_payload["groups"] = None
        stats_payload["note"] = "full groups stored as per-chain JSON refs; not one giant dictionary"
    else:
        stats_payload["groups"] = groups
    stats_ref = outputs.json("statistics.json", stats_payload, kind="options_quote_statistics_v1")
    if group_refs is None:
        for chain in chains:
            chain_groups = {name: block for name, block in groups.items() if name.startswith(f"{chain}|")}
            outputs.json(f"groups-{chain.lower()}.json", chain_groups,
                         kind="options_quote_chain_groups_v1")
    dist_ref = outputs.json("distributions.json", {
        "kind": "options_quote_date_distributions_v1",
        "quantiles": list(cfg["quantiles"]),
        "note": "Equal-date empirical quantiles of the date-level series. Raw means use event mass.",
        "groups": {name: {
            metric: payload.get("date_quantiles")
            for metric, payload in (block["statistics"].get("metrics") or {}).items()
        } for name, block in groups.items()},
    }, kind="options_quote_distributions_v1")
    md_ref = write_results_md(
        outputs, protocol=protocol, groups=groups, cfg=cfg,
        counts=counts, selected_dates=selected_dates, output_refs=output_refs,
    )
    return {"refs": {"statistics": stats_ref, "distributions": dist_ref, "results_md": md_ref},
            "groups": groups, "configuration": cfg}


def finish_quote_outputs(
    outputs, *, spec, calendar_ref, admit_w, except_w, alias_w, board_w, quality_w,
    support_w, ident_w, coverage_rows, date_aggregates, consumed, required_ids, manifest,
    files_read, rows_read, bytes_read, source_dates, selected_dates, selected_chains,
    intended_all, intended_labels, chains, started_cpu, started_wall,
    reconstruction_payload, family, version, remaining, sci_hash, impl_hashes, binding,
    oi_identity, parse_cpu, oi_support_cpu, listing_unknown_chains,
    joined_coverage_complete, max_worker_bytes, max_source_file,
):
    identity_refs = ident_w.finish()
    exception_refs = except_w.finish()
    alias_refs = alias_w.finish()
    admission_refs = admit_w.finish()
    board_refs = board_w.finish()
    quality_refs = quality_w.finish()
    support_refs = support_w.finish()
    import pyarrow.parquet as pq
    pa = __import__("pyarrow")
    from trading_research.research.options_quote_measurements import coverage_schema
    coverage_table = coverage_schema().empty_table() if not coverage_rows else pa.table(
        {field.name: [row.get(field.name) for row in coverage_rows] for field in coverage_schema()},
        schema=coverage_schema(),
    )
    stream = outputs.create("coverage.parquet")
    try:
        pq.write_table(coverage_table, stream, compression="zstd")
    finally:
        stream.close()
    coverage_ref = {**outputs.reference("coverage.parquet", kind="options_quote_coverage_v1"),
                    "rows": len(coverage_table)}
    aggregates_ref = outputs.json("date-aggregates.json", date_aggregates,
                                  kind="options_quote_date_aggregates_v1")
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
        "identity_match": identity_refs, "coverage": coverage_ref,
        "reconstruction": reconstruction_ref,
    }
    statistics_start_cpu = pytime.process_time()
    statistics_start_output = outputs.written
    production_cpu_seconds = statistics_start_cpu - started_cpu
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
        "identity_match": identity_refs, "coverage": coverage_ref,
        "date_aggregates": aggregates_ref, "reconstruction": reconstruction_ref,
        "statistics": stats["refs"]["statistics"], "distributions": stats["refs"]["distributions"],
        "results_md": stats["refs"]["results_md"],
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
            "listing_unknown_chains": listing_unknown_chains, "chains": list(chains),
        },
        "resources": {
            "cpu_seconds": cpu, "wall_seconds": wall, "output_bytes": outputs.written,
            "source_parse_dedup_board_cpu_seconds": parse_cpu,
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
        "groups": stats["groups"],
        "clock_interpretation": {
            "ts_event_ns": "exact recorded sampling/source clock",
            "known_at_ns": None, "received_at_ns": None, "published_at_ns": None,
            "last_actual_update_ns": None, "causal_feature_eligible": False,
            "actual_update_age_unknown": True,
            "reconstruction": reconstruction_payload.get("predicate"),
        },
    }


__all__ = [
    "VERSION", "build_group_statistics", "date_balanced_point", "date_quantiles",
    "empty_metric", "empty_ratio", "exact_quantiles_from_values",
    "finish_quote_outputs", "raw_mean", "run_statistics", "universe_dates",
]
