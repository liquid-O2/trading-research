"""Native local order-flow observations for O098--O120.

The functions in this module are registration overrides.  They keep immutable
execution, quote, candle and band identities in their payloads and deliberately
leave proprietary source interpretations nullable.  MBP-1 is treated as BBO
evidence only; it can never certify off-touch depth or hidden reserve.
"""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from functools import wraps
from typing import Any, Callable, Iterable, Mapping

from trading_research.research.method_pack.contracts import OutputField
from trading_research.research.method_pack.logic import dec, kleene_and
from trading_research.research.method_pack.native_resolution import NativeEvidenceError
from trading_research.research.method_pack.protocol import RecipeResult, guard


LOCAL_FLOW_SCHEMAS: dict[str, tuple[str, ...]] = {
    "O098": ("event_records", "buy", "sell", "unknown", "total", "delta", "delta_interval", "ordering_quality", "aggressor_convention"),
    "O099": ("marker_events", "markers", "threshold", "comparator", "aggregation_mode", "mode", "source_display_known", "source_setting_id", "same_as_other_mode"),
    "O100": ("band", "local_quote_snapshots", "local_executions", "spread", "display_changes", "display_change", "consumption_evidence", "execution_evidence", "consumed_and_replenished", "defense_interpretation", "depth_coverage", "verified_hidden_reserve"),
    "O101": ("band", "branch_id", "aggressive_buy_volume", "aggressive_sell_volume", "aggressive_unknown_volume", "effort", "price_progress_points", "price_progress_ticks", "progress", "passive_defense", "source_absorption", "absorption", "later_decline_repairs", "later_decline"),
    "O102": ("price", "passive_side", "consumption_events", "refresh_events", "observed_same_price_size_changes", "consumption", "refresh", "final_display", "net", "bbo_reload_inference", "verified_replenishment", "hold"),
    "O103": ("area", "width", "executed_total", "displayed", "replenishment_hypothesis", "verified_hidden_reserve", "participant_events", "participant_count", "depth_coverage"),
    "O104": ("origin", "origin_band", "selected_edge", "direction", "reward_price", "reward_at", "reward_points", "reward_ticks", "directional_reward", "return_at", "renewed_defense_at", "retest_is_reward"),
    "O105": ("reset_id", "reset_at", "as_of", "event_ids", "cvd", "known_cvd", "delta_interval", "reference", "reference_unit", "difference", "directional_relation", "automatic_reference"),
    "O106": ("candle_id", "price_change", "price_sign", "delta", "delta_sign", "delta_bounds", "opposed_signs", "event_ids"),
    "O107": ("band", "extreme", "buy_volume", "sell_volume", "unknown_volume", "delta", "total", "fraction", "fraction_interval", "price_response", "source_spike"),
    "O108": ("candle_id", "candle_definition", "snapshot_ids", "snapshot_count", "poc_before", "poc_after", "poc", "change", "flip_at", "same_candle"),
    "O109": ("candle_id", "ratio_min", "row_count", "zero_rule", "buy_comparisons", "sell_comparisons", "buy_runs", "sell_runs", "ratios", "consecutive", "qualifies", "stack_band", "printed_ratio", "automatic_settings"),
    "O110": ("price", "buy_volume", "sell_volume", "buy_multiple", "sell_multiple", "buy_relation", "sell_relation", "percent_of", "percent_more", "source_350_flag", "meets_of", "meets_more", "rule", "zero_rule"),
    "O111": ("window_start", "window_end", "event_ids", "print_count", "contracts", "duration_seconds", "prints_per_second", "contracts_per_second", "source_panel_value", "automatic_speed"),
    "O112": ("quote_id", "bid", "ask", "bid_size", "ask_size", "spread_points", "spread_ticks", "locked", "crossed", "stale", "depth_coverage"),
    "O113": ("path_event_ids", "from_price", "to_price", "from_at", "to_at", "duration_seconds", "net_distance", "path_distance", "net_speed", "aggressive_buy_volume", "aggressive_sell_volume", "aggressive_unknown_volume", "aggressive_arrival", "touch_at", "post_touch_included"),
    "O114": ("event_ids", "sizes", "digit_counts", "groups", "declining", "source_classification", "window_start", "window_end"),
    "O115": ("origin", "direction", "stage_ledger", "defender_aggression_events", "reward_price", "reward_points", "reward_ticks", "entry_distance_ticks", "directional_reward", "geometry_ok", "order_ok"),
    "O116": ("zone_id", "zone", "zone_known_at", "source_setting_id", "formation_event_ids", "departure_at", "touch_ids", "later_touches", "automatic_zone", "later_high_replaces_origin", "zone_definition_recorded", "zone_frozen", "instrument_and_threshold_preserved", "departure_observed", "distinct_touch_id", "touch_at"),
    "O117": ("zone_id", "prior_touch_count", "resolved_defense_count", "prior_resolved_defense_count", "eligible_history_ids", "unresolved_history_ids", "max_feature_known_at", "memory_causal", "current_counts_as_prior", "memory_uses_only_prior_resolved_touches"),
    "O118": ("origin_id", "origin", "side", "stage_ledger", "linked", "branch_ok", "missing_stages", "failed_push_count", "later_high_replaces_origin"),
    "O119": ("band_id", "extreme", "prior_failure_ids", "distinct_failures", "historical_failures_known", "current_stage_ledger", "current_evidence_complete", "order_ok", "body_selling", "control_side", "two_distinct_prior_failures", "prior_failures_known_at"),
    "O120": ("candle_id", "candle_definition", "instrument_id", "tick_size", "O", "H", "L", "C", "formation_start", "formation_end", "as_of", "rows", "buy_by_price", "sell_by_price", "unknown_by_price", "total_by_price", "event_ids", "total_volume", "known_delta", "delta", "delta_interval", "body_prices", "wick_low", "wick_high", "body_delta", "poc", "poc_candidates", "poc_tie_state", "display_config", "marker_event_ids", "later_price_in_earlier_asof"),
}


LEGACY_REQUIRED = {
    "O098": ("events",), "O099": ("trades", "threshold"),
    "O100": ("bid_size_before", "bid_size_after"),
    "O101": ("effort_size", "progress"), "O102": ("known_at",),
    "O103": ("q", "area_ticks", "executed_total", "displayed"),
    "O104": ("origin",), "O105": ("trades",), "O106": ("O", "C"),
    "O107": ("B", "A"), "O108": ("snapshots",), "O109": ("rows",),
    "O110": ("B", "S"), "O111": ("interval_s", "n_prints", "contracts"),
    "O112": ("bid",), "O113": ("from_px", "to_px", "from_at", "to_at"),
    "O114": ("sizes",), "O115": ("origin",), "O116": ("known_at",),
    "O117": ("cutoff", "priors"),
    "O118": ("origin", "failed_pushes", "release_at", "failure_at", "entry_at"),
    "O119": ("prior_failures", "fail_at", "breakdown_at", "retest_at", "confirm_at", "entry_at"),
    "O120": ("O", "H", "L", "C"),
}


RICH_MARKERS = {
    "O098": {"formation_start", "raw_member_locators"},
    "O099": {"source_setting", "source_setting_id", "aggregation_mode"},
    "O100": {"band", "quotes", "events", "reset_at"},
    "O101": {"band", "events", "response_start_price", "passive_defense"},
    "O102": {"consumption_events", "refresh_events", "passive_side"},
    "O103": {"area", "participant_events", "depth_coverage"},
    "O104": {"direction", "reward_price", "reward_at", "return_at"},
    "O105": {"reset_at", "as_of", "reset_id"},
    "O106": {"candle_id", "events"}, "O107": {"band", "events", "unknown_volume"},
    "O108": {"snapshot_ids"}, "O109": {"footprint_rows", "zero_rule"},
    "O110": {"buy_volume", "sell_volume", "zero_rule"}, "O111": {"events", "window_start"},
    "O112": {"quote", "instrument_definition"}, "O113": {"events", "touch_at"},
    "O114": {"events", "groups", "window_start"}, "O115": {"direction", "stage_ledger"},
    "O116": {"zone_id", "formation_event_ids", "source_setting_id"},
    "O117": {"zone_id"}, "O118": {"origin_id", "stage_ledger"},
    "O119": {"band_id", "current_evidence", "body_selling"},
    "O120": {"candle_id", "events", "tick_size", "formation_start"},
}


def _schema(rid: str, **values: Any) -> dict[str, Any]:
    out = {key: None for key in LOCAL_FLOW_SCHEMAS[rid]}
    out.update(values)
    return out


def _result(rid: str, state: str, values: dict[str, Any] | None = None, **kwargs: Any) -> RecipeResult:
    return RecipeResult(rid, state, _schema(rid, **(values or {})), **kwargs)


def _holes(rid: str, names: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(f"HOLE:{rid}:{name}" for name in names))


def _override(rid: str) -> Callable:
    def decorate(fn: Callable[[dict], RecipeResult]) -> Callable[[dict], RecipeResult]:
        @wraps(fn)
        def wrapped(inp: dict) -> RecipeResult:
            rich = any(key in inp for key in RICH_MARKERS[rid])
            blocked = guard(inp, rid, () if rich else LEGACY_REQUIRED[rid])
            if blocked is not None:
                if blocked.reason in {"dependency available after use", "dependency available after claimed snapshot"}:
                    try:
                        observed = fn(inp)
                    except (ArithmeticError, KeyError, TypeError, ValueError):
                        observed = _result(rid, "invalid", {}, base_ok=False)
                    observed.state, observed.base_ok = "invalid", False
                    observed.hole_ids = list(dict.fromkeys(observed.hole_ids + blocked.hole_ids))
                    observed.reason = blocked.reason
                    return observed
                return _result(rid, blocked.state, blocked.value, hole_ids=blocked.hole_ids,
                               known_at=blocked.known_at, base_ok=blocked.base_ok,
                               coverage_ok=blocked.coverage_ok, reason=blocked.reason)
            try:
                return fn(inp)
            except (ArithmeticError, KeyError, TypeError, ValueError) as exc:
                return _result(rid, "invalid", {}, base_ok=False, coverage_ok=None,
                               hole_ids=_holes(rid, ["input_type"]),
                               known_at=inp.get("known_at"), reason=f"invalid local-flow input: {exc}")
        return wrapped
    return decorate


def _at(row: Mapping[str, Any]) -> int | None:
    for key in ("known_at", "event_ns", "at", "t", "time"):
        if type(row.get(key)) is int:
            return row[key]
    return None


def _event_at(row: Mapping[str, Any]) -> int | None:
    for key in ("event_ns", "at", "t", "time"):
        if type(row.get(key)) is int:
            return row[key]
    return None


def _side(row: Mapping[str, Any]) -> str:
    raw = str(row.get("side", row.get("aggressor", "N"))).strip().upper()
    if raw in {"B", "BUY", "BID_LIFT", "LIFT"}:
        return "B"
    if raw in {"A", "S", "SELL", "ASK_HIT", "HIT"}:
        return "A"
    return "N"


def _is_trade(row: Mapping[str, Any]) -> bool:
    action = row.get("action")
    return action is None or str(action).upper() == "T"


def _trade_records(rows: Iterable[Mapping[str, Any]], *, strict_identity: bool = False,
                   as_of: int | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    missing: list[str] = []
    seen: set[str] = set()
    for index, source in enumerate(rows):
        if not _is_trade(source):
            continue
        size = dec(source.get("executed_size", source.get("size")))
        price = dec(source.get("price"))
        if size is None or size <= 0:
            missing.append("executed_size")
            continue
        if price is None or not price.is_finite():
            missing.append("price")
        event_at = _event_at(source)
        known_at = _at(source)
        if event_at is None:
            missing.append("event_at")
        if known_at is None:
            missing.append("event_availability")
        if as_of is not None and ((event_at is not None and event_at > as_of) or
                                  (known_at is not None and known_at > as_of)):
            continue
        event_id = source.get("event_id", source.get("trade_id"))
        if event_id is None:
            missing.append("event_id")
        else:
            event_id = str(event_id)
        if event_id is not None and event_id in seen:
            raise ValueError("duplicate executed event identity")
        if event_id is not None:
            seen.add(event_id)
        side = _side(source)
        records.append({
            "event_id": event_id, "instrument_id": source.get("instrument_id"),
            "event_key": event_at, "known_at": known_at, "price": price,
            "executed_size": size, "aggressor": {"B": "buy", "A": "sell", "N": "unknown"}[side],
            "side": side, "signed_known_size": size if side == "B" else -size if side == "A" else None,
            "unknown_size": size if side == "N" else Decimal(0),
            "exchange_sequence": source.get("exchange_sequence"),
            "ordering_basis": source.get("ordering_basis", "timestamp_only"),
            "candle_id": source.get("candle_id"), "band_id": source.get("band_id"),
        })
    return records, list(dict.fromkeys(missing))


def _volumes(records: Iterable[Mapping[str, Any]]) -> tuple[Decimal, Decimal, Decimal]:
    buy = sum((r["executed_size"] for r in records if r["side"] == "B"), Decimal(0))
    sell = sum((r["executed_size"] for r in records if r["side"] == "A"), Decimal(0))
    unknown = sum((r["executed_size"] for r in records if r["side"] == "N"), Decimal(0))
    return buy, sell, unknown


def _known(rows: Iterable[Mapping[str, Any]], fallback: int | None = None) -> int | None:
    times = [_at(row) for row in rows]
    values = [t for t in times if t is not None]
    if fallback is not None:
        values.append(fallback)
    return max(values) if values else None


def _strict_times(rid: str, stages: list[tuple[str, Any]], *, allow_equal: bool = False) -> tuple[bool | None, list[str]]:
    missing = [name for name, at in stages if at is None]
    if missing:
        return None, missing
    values = [at for _, at in stages]
    if any(type(at) is not int for at in values):
        raise ValueError("stage times must be integer event keys")
    ordered = all(a <= b if allow_equal else a < b for a, b in zip(values, values[1:]))
    return ordered, []


@_override("O098")
def o098(inp: dict) -> RecipeResult:
    rows = inp.get("events", inp.get("trades", [])) or []
    records, missing = _trade_records(rows, strict_identity=any(k in inp for k in RICH_MARKERS["O098"]), as_of=inp.get("as_of"))
    buy, sell, unknown = _volumes(records)
    known_delta = buy - sell
    tied: dict[int, list[dict[str, Any]]] = {}
    for record in records:
        if record["event_key"] is not None:
            tied.setdefault(record["event_key"], []).append(record)
    unresolved = any(len(batch) > 1 and (any(r["exchange_sequence"] is None for r in batch) or
                                          len({r["exchange_sequence"] for r in batch}) != len(batch))
                     for batch in tied.values())
    ordering = "timestamp_ties_unordered" if unresolved else "exchange_sequence" if records and all(
        r["exchange_sequence"] is not None for r in records) else "timestamp_only"
    if not records and inp.get("coverage_ok") is not True: missing.append("execution_coverage")
    holes = _holes("O098", missing + (["coverage"] if inp.get("coverage_ok") is not True and any(k in inp for k in ("formation_start", "raw_member_locators")) else []))
    return _result("O098", "hole" if holes else "computed", {
        "event_records": records, "buy": buy, "sell": sell, "unknown": unknown,
        "total": buy + sell + unknown, "delta": known_delta if unknown == 0 else None,
        "delta_interval": [known_delta - unknown, known_delta + unknown],
        "ordering_quality": ordering, "aggressor_convention": "B_buy_A_sell_N_unknown",
    }, hole_ids=holes, known_at=_known(records, inp.get("known_at")),
       coverage_ok=True if not holes else None)


SOURCE_BIG_TRADE_SETTINGS = {
    ("jumbo", "NQ", "new_york"): (Decimal(100), ">=", "per_print"),
    ("jumbo", "NQ", "london"): (Decimal(75), ">=", "per_print"),
}


@_override("O099")
def o099(inp: dict) -> RecipeResult:
    setting = inp.get("source_setting") if isinstance(inp.get("source_setting"), dict) else {}
    author = str(setting.get("author", inp.get("author", ""))).lower()
    instrument = str(setting.get("instrument", inp.get("instrument", inp.get("instrument_id", "")))).upper()
    session = str(setting.get("session", inp.get("session", ""))).lower().replace(" ", "_")
    printed = SOURCE_BIG_TRADE_SETTINGS.get((author, instrument, session))
    threshold = dec(setting.get("threshold", inp.get("threshold", printed[0] if printed else None)))
    comparator = setting.get("comparator", inp.get("comparator", printed[1] if printed else ">=" if "threshold" in inp else None))
    mode = setting.get("aggregation_mode", inp.get("aggregation_mode", inp.get("mode", printed[2] if printed else None)))
    rows = inp.get("events", inp.get("trades", [])) or []
    records, missing = _trade_records(rows, strict_identity=bool(setting))
    source_known = threshold is not None and comparator in {">", ">="} and mode in {"per_print", "cluster"}
    if mode == "cluster" and not setting.get("cluster_rule"):
        source_known = False
        missing.append("cluster_rule")
    markers: list[dict[str, Any]] = []
    if source_known and mode == "per_print":
        for record in records:
            qualifies = record["executed_size"] >= threshold if comparator == ">=" else record["executed_size"] > threshold
            if qualifies:
                markers.append({"marker_id": f"marker:{record['event_id']}", "event_ids": [record["event_id"]],
                                "price": record["price"], "side": record["side"],
                                "marker_volume": record["executed_size"], "known_at": record["known_at"]})
    elif source_known and mode == "cluster":
        key_name = setting["cluster_rule"]
        grouped: dict[Any, list[dict[str, Any]]] = {}
        for record in records:
            source = next((r for r in rows if str(r.get("event_id", r.get("trade_id"))) == record["event_id"]), {})
            grouped.setdefault(source.get(key_name), []).append(record)
        if None in grouped:
            missing.append("cluster_membership")
        for cluster_id, batch in grouped.items():
            if cluster_id is None:
                continue
            volume = sum((r["executed_size"] for r in batch), Decimal(0))
            qualifies = volume >= threshold if comparator == ">=" else volume > threshold
            if qualifies:
                sides = {r["side"] for r in batch}
                markers.append({"marker_id": f"cluster:{cluster_id}", "event_ids": [r["event_id"] for r in batch],
                                "price": batch[-1]["price"], "side": next(iter(sides)) if len(sides) == 1 else "N",
                                "marker_volume": volume, "known_at": _known(batch)})
    if threshold is None: missing.append("threshold")
    if comparator not in {">", ">="}: missing.append("comparator")
    if mode not in {"per_print", "cluster"}: missing.append("aggregation_mode")
    if setting.get("setting_id", inp.get("source_setting_id")) is None: missing.append("source_setting_id")
    holes = _holes("O099", missing)
    return _result("O099", "hole" if holes else "computed", {
        "marker_events": markers, "markers": len(markers), "threshold": threshold,
        "comparator": comparator, "aggregation_mode": mode, "mode": mode,
        "source_display_known": True if source_known and not holes else None if holes else False,
        "source_setting_id": setting.get("setting_id", inp.get("source_setting_id")),
        "same_as_other_mode": False,
    }, hole_ids=holes, known_at=_known(markers, inp.get("known_at")), coverage_ok=None if holes else True)


def _quote_record(source: Mapping[str, Any], index: int) -> dict[str, Any]:
    bid, ask = dec(source.get("bid")), dec(source.get("ask"))
    quote_id = source.get("quote_id", source.get("event_id"))
    return {"quote_id": None if quote_id is None else str(quote_id),
            "at": _event_at(source), "known_at": _at(source), "bid": bid, "ask": ask,
            "bid_size": dec(source.get("bid_size", source.get("bid_sz"))),
            "ask_size": dec(source.get("ask_size", source.get("ask_sz"))),
            "depth_level": int(source.get("depth_level", 1))}


@_override("O100")
def o100(inp: dict) -> RecipeResult:
    band = inp.get("band")
    bounds = None if band is None else [dec(band[0]), dec(band[1])] if isinstance(band, (list, tuple)) else [dec(band), dec(band)]
    quotes = [_quote_record(row, i) for i, row in enumerate(inp.get("quotes", []))]
    records, missing = _trade_records(inp.get("events", []), strict_identity=True)
    changes = []
    for first, second in zip(quotes, quotes[1:]):
        for side_name in ("bid", "ask"):
            size_key = f"{side_name}_size"
            if first[side_name] is not None and first[side_name] == second[side_name] and first[size_key] is not None and second[size_key] is not None:
                changes.append({"side": side_name, "price": first[side_name], "from_quote_id": first["quote_id"],
                                "to_quote_id": second["quote_id"], "change": second[size_key] - first[size_key]})
    spread = None
    if quotes and quotes[-1]["bid"] is not None and quotes[-1]["ask"] is not None:
        spread = quotes[-1]["ask"] - quotes[-1]["bid"]
    local_exec = [r for r in records if bounds is None or (r["price"] is not None and bounds[0] <= r["price"] <= bounds[1])]
    consumption = True if local_exec else False if inp.get("execution_coverage_ok") is True else None
    local_changes = [row for row in changes if bounds is None or bounds[0] <= row["price"] <= bounds[1]]
    display_change = local_changes[-1]["change"] if local_changes else None
    if display_change is None and inp.get("bid_size_before") is not None and inp.get("bid_size_after") is not None:
        display_change = dec(inp["bid_size_after"]) - dec(inp["bid_size_before"])
    # A BBO size increase can be recorded as an inference, never hidden reserve.
    bbo_reload = None if consumption is None else consumption and any(row["change"] > 0 for row in changes)
    depth = inp.get("depth_coverage", "bbo" if quotes else "none")
    holes = list(missing)
    if quotes and any(row["quote_id"] is None for row in quotes): holes.append("quote_id")
    if quotes and any(row["at"] is None or row["known_at"] is None for row in quotes): holes.append("quote_availability")
    if inp.get("executed_sell") is not None and not records: holes.append("execution_identity")
    if inp.get("reset_at") is None and any(k in inp for k in RICH_MARKERS["O100"]): holes.append("reset")
    if depth not in {"bbo", "full_depth"}: holes.append("quote_coverage")
    defense = inp.get("defense_interpretation")
    return _result("O100", "hole" if holes or defense is None else "supplied", {
        "band": bounds, "local_quote_snapshots": quotes, "local_executions": local_exec,
        "spread": spread, "display_changes": changes, "display_change": display_change,
        "consumption_evidence": consumption, "execution_evidence": consumption,
        "consumed_and_replenished": bbo_reload, "defense_interpretation": defense,
        "depth_coverage": depth, "verified_hidden_reserve": None,
    }, hole_ids=_holes("O100", holes + ([] if defense is not None else ["source_interpretation"])),
       known_at=_known([*quotes, *local_exec], inp.get("known_at")), coverage_ok=None if holes else True)


@_override("O101")
def o101(inp: dict) -> RecipeResult:
    records, missing = _trade_records(inp.get("events", []), strict_identity=True)
    buy, sell, unknown = _volumes(records)
    effort = dec(inp.get("effort_size"))
    direction = inp.get("aggressive_side", inp.get("direction"))
    if effort is None:
        effort = buy if str(direction).lower() in {"buy", "long", "b"} else sell if str(direction).lower() in {"sell", "short", "a", "s"} else buy + sell
    start = dec(inp.get("response_start_price", inp.get("origin")))
    end = dec(inp.get("response_end_price", inp.get("later_px")))
    progress = dec(inp.get("progress"))
    sign = Decimal(1) if str(direction).lower() in {"buy", "long", "b"} else Decimal(-1) if str(direction).lower() in {"sell", "short", "a", "s"} else None
    if progress is None and start is not None and end is not None and sign is not None:
        progress = sign * (end - start)
    q = dec(inp.get("q", inp.get("tick_size")))
    passive = inp.get("passive_defense", inp.get("hold"))
    source = inp.get("source_absorption")
    absorption = source if source is False else True if source is True and passive is True else None
    if not records: missing.append("effort_observations")
    holes = missing + [name for name, value in (("direction", direction), ("passive_defense", passive), ("source_detector", source)) if value is None]
    return _result("O101", "hole" if holes else "supplied", {
        "band": deepcopy(inp.get("band")), "branch_id": inp.get("branch_id", inp.get("branch")),
        "aggressive_buy_volume": buy, "aggressive_sell_volume": sell,
        "aggressive_unknown_volume": unknown, "effort": effort,
        "price_progress_points": progress, "price_progress_ticks": None if progress is None or q in (None, 0) else progress / q,
        "progress": progress, "passive_defense": passive, "source_absorption": absorption,
        "absorption": absorption, "later_decline_repairs": False,
        "later_decline": dec(inp.get("later_decline")),
    }, hole_ids=_holes("O101", holes), known_at=_known(records, inp.get("known_at")), coverage_ok=None if holes else True)


@_override("O102")
def o102(inp: dict) -> RecipeResult:
    consumption_rows = deepcopy(inp.get("consumption_events", []))
    refresh_rows = deepcopy(inp.get("refresh_events", []))
    lifecycle = inp.get("lifecycle") if isinstance(inp.get("lifecycle"), dict) else None
    if lifecycle is not None:
        consumed, refresh, final = (dec(lifecycle.get(k)) for k in ("consumed", "refresh", "final_display"))
        return _result("O102", "hole", {
            "price": dec(inp.get("price")), "passive_side": inp.get("passive_side"),
            "consumption_events": consumption_rows, "refresh_events": refresh_rows,
            "observed_same_price_size_changes": [], "consumption": consumed, "refresh": refresh,
            "final_display": final, "net": None, "bbo_reload_inference": None,
            "verified_replenishment": None, "hold": inp.get("hold"),
        }, hole_ids=_holes("O102", ["consumption_events", "refresh_events", "event_identity"]),
           known_at=inp.get("known_at"), coverage_ok=None)
    first, last = dec(inp.get("first_display")), dec(inp.get("last_display"))
    net = None if first is None or last is None else last - first
    consumption = sum((dec(r.get("size", r.get("executed_size", 0))) for r in consumption_rows), Decimal(0))
    refresh = sum((dec(r.get("size", r.get("change", 0))) for r in refresh_rows), Decimal(0))
    price = dec(inp.get("price"))
    passive_side = inp.get("passive_side")
    hold = inp.get("hold")
    complete = bool(consumption_rows and refresh_rows)
    order_ok, missing = _strict_times("O102", [("consumption_at", _event_at(consumption_rows[0]) if consumption_rows else None),
                                                  ("refresh_at", _event_at(refresh_rows[-1]) if refresh_rows else None)])
    same_price = all(price is None or dec(row.get("price")) == price for row in [*consumption_rows, *refresh_rows])
    verified = None if not complete or hold is None else bool(order_ok and same_price and consumption > 0 and refresh > 0 and hold)
    bbo = None if not complete else bool(order_ok and same_price and consumption > 0 and refresh > 0)
    if any(row.get("event_id") is None for row in [*consumption_rows,*refresh_rows]): missing.append("event_identity")
    holes = missing + [name for name, value in (("price", price), ("passive_side", passive_side), ("hold", hold)) if value is None]
    return _result("O102", "hole" if holes else "computed", {
        "price": price, "passive_side": passive_side, "consumption_events": consumption_rows,
        "refresh_events": refresh_rows, "observed_same_price_size_changes": refresh_rows,
        "consumption": consumption if consumption_rows else None, "refresh": refresh if refresh_rows else None,
        "final_display": last, "net": net, "bbo_reload_inference": bbo,
        "verified_replenishment": verified, "hold": hold,
    }, hole_ids=_holes("O102", holes), known_at=_known([*consumption_rows, *refresh_rows], inp.get("known_at")), coverage_ok=None if holes else True)


@_override("O103")
def o103(inp: dict) -> RecipeResult:
    q, ticks = dec(inp.get("q", inp.get("tick_size"))), dec(inp.get("area_ticks"))
    area = deepcopy(inp.get("area"))
    width = None if q is None or ticks is None else q * ticks
    executed, displayed = dec(inp.get("executed_total")), dec(inp.get("displayed"))
    participants = deepcopy(inp.get("participant_events", []))
    identities = {row.get("participant_id") for row in participants if row.get("participant_id") is not None}
    hypothesis = None if executed is None or displayed is None else executed > displayed
    depth = inp.get("depth_coverage")
    verified = inp.get("verified_hidden_reserve") if depth == "full_order_lifecycle" else None
    holes = []
    if verified is None: holes.append("verification")
    if verified is True and not participants: holes.append("participant_events")
    if participants and len(identities) != len(participants): holes.append("participant_identity")
    return _result("O103", "hole" if holes else "computed", {
        "area": area, "width": width, "executed_total": executed, "displayed": displayed,
        "replenishment_hypothesis": hypothesis, "verified_hidden_reserve": verified,
        "participant_events": participants, "participant_count": len(identities) if participants else None,
        "depth_coverage": depth,
    }, hole_ids=_holes("O103", holes), known_at=_known(participants, inp.get("known_at")), coverage_ok=None if holes else True)


@_override("O104")
def o104(inp: dict) -> RecipeResult:
    origin = dec(inp.get("origin")); band = inp.get("origin_band")
    selected = inp.get("selected_edge")
    direction = str(inp.get("direction", inp.get("side", ""))).lower()
    reward_price = dec(inp.get("reward_price", inp.get("later_px")))
    q = dec(inp.get("q", inp.get("tick_size", Decimal("0.25"))))
    reference = origin
    holes = []
    if band is not None:
        if selected not in {"low", "high"}: holes.append("selected_edge")
        else: reference = dec(band[0 if selected == "low" else 1])
    sign = Decimal(1) if direction in {"long", "buy", "b", "1"} else Decimal(-1) if direction in {"short", "sell", "a", "s", "-1"} else None
    raw = None if reference is None or reward_price is None else reward_price - reference
    directional = None if raw is None or sign is None else sign * raw
    # Compatibility measurement remains unsigned; qualification uses directional_reward.
    reward_points = None if raw is None else abs(raw) if sign is None else directional
    if sign is None: holes.append("direction")
    if reward_price is None: holes.append("reward_price")
    if q is None or q <= 0: raise ValueError("tick size must be positive")
    return _result("O104", "hole" if holes else "computed", {
        "origin": origin, "origin_band": deepcopy(band), "selected_edge": selected,
        "direction": direction or None, "reward_price": reward_price, "reward_at": inp.get("reward_at"),
        "reward_points": reward_points, "reward_ticks": None if reward_points is None else reward_points / q,
        "directional_reward": None if directional is None else directional > 0,
        "return_at": inp.get("return_at"), "renewed_defense_at": inp.get("renewed_defense_at"),
        "retest_is_reward": False,
    }, hole_ids=_holes("O104", holes), known_at=inp.get("reward_at", inp.get("known_at")), coverage_ok=None if holes else True)


@_override("O105")
def o105(inp: dict) -> RecipeResult:
    reset_at, as_of = inp.get("reset_at"), inp.get("as_of", inp.get("known_at"))
    records, missing = _trade_records(inp.get("events", inp.get("trades", [])), strict_identity=False, as_of=as_of)
    if reset_at is not None:
        records = [r for r in records if r["event_key"] is not None and r["event_key"] >= reset_at]
    buy, sell, unknown = _volumes(records); known_cvd = buy - sell
    reference = dec(inp.get("reference")); unit = inp.get("reference_unit", "contracts")
    if reference is not None and unit != "contracts":
        return _result("O105", "invalid", {"cvd": known_cvd if unknown == 0 else None,
            "known_cvd": known_cvd, "delta_interval": [known_cvd-unknown, known_cvd+unknown],
            "reference": reference, "reference_unit": unit, "event_ids": [r["event_id"] for r in records]},
            base_ok=False, coverage_ok=None, reason="reference units differ from CVD contracts")
    exact = known_cvd if unknown == 0 else None
    diff = None if exact is None or reference is None else exact - reference
    relation = None if diff is None else "above" if diff > 0 else "below" if diff < 0 else "equal"
    holes = missing
    rich = any(k in inp for k in RICH_MARKERS["O105"])
    if reset_at is None: holes.append("reset")
    if as_of is None: holes.append("as_of")
    if unknown: holes.append("unknown_side")
    if reference is None: holes.append("reference")
    if inp.get("reset_verified") is False: holes.append("reset")
    return _result("O105", "hole" if holes else "computed", {
        "reset_id": inp.get("reset_id"), "reset_at": reset_at, "as_of": as_of,
        "event_ids": [r["event_id"] for r in records], "cvd": exact,
        "known_cvd": known_cvd, "delta_interval": [known_cvd-unknown, known_cvd+unknown],
        "reference": reference, "reference_unit": unit, "difference": diff,
        "directional_relation": relation, "automatic_reference": None,
    }, hole_ids=_holes("O105", holes), known_at=_known(records, inp.get("known_at")), coverage_ok=None if holes else True)


@_override("O106")
def o106(inp: dict) -> RecipeResult:
    o, c = dec(inp.get("O")), dec(inp.get("C")); candle_id = inp.get("candle_id")
    records, missing = _trade_records(inp.get("events", inp.get("trades", [])), strict_identity=False)
    if candle_id is not None and any(r["candle_id"] not in {None, candle_id} for r in records):
        return _result("O106", "invalid", {"candle_id": candle_id, "event_ids": [r["event_id"] for r in records]}, base_ok=False, reason="trade belongs to another candle")
    buy, sell, unknown = _volumes(records); known_delta = buy-sell
    change = None if o is None or c is None else c-o
    exact = known_delta if records and unknown == 0 else None
    price_sign = None if change is None else 1 if change > 0 else -1 if change < 0 else 0
    delta_sign = None if exact is None else 1 if exact > 0 else -1 if exact < 0 else 0
    opposed = None if price_sign is None or delta_sign is None else price_sign * delta_sign == -1
    if not records: missing.append("candle_executions")
    if unknown: missing.append("aggressor_side")
    return _result("O106", "hole" if missing else "computed", {
        "candle_id": candle_id, "price_change": change, "price_sign": price_sign,
        "delta": exact, "delta_sign": delta_sign, "delta_bounds": [known_delta-unknown, known_delta+unknown],
        "opposed_signs": opposed, "event_ids": [r["event_id"] for r in records],
    }, hole_ids=_holes("O106", missing), known_at=_known(records, inp.get("known_at")), coverage_ok=None if missing else True)


@_override("O107")
def o107(inp: dict) -> RecipeResult:
    records, missing = _trade_records(inp.get("events", []), strict_identity=False)
    if records: buy, sell, unknown = _volumes(records)
    else: buy, sell, unknown = dec(inp.get("B", 0)), dec(inp.get("A", 0)), dec(inp.get("N", inp.get("unknown_volume", 0)))
    total = buy+sell+unknown; delta=buy-sell
    fraction = None if total == 0 or unknown else delta/total
    bounds = None if total == 0 else [(delta-unknown)/total, (delta+unknown)/total]
    spike = inp.get("source_spike")
    if spike is not None and not records and inp.get("source_observation_id") is None: missing.append("source_observation_id")
    holes = missing + (["unknown_side"] if unknown else []) + ([] if spike is not None else ["classifier"])
    return _result("O107", "hole" if holes else "supplied", {
        "band": deepcopy(inp.get("band")), "extreme": inp.get("extreme"),
        "buy_volume": buy, "sell_volume": sell, "unknown_volume": unknown,
        "delta": delta, "total": total, "fraction": fraction, "fraction_interval": bounds,
        "price_response": dec(inp.get("price_response")), "source_spike": spike,
    }, hole_ids=_holes("O107", holes), known_at=_known(records, inp.get("known_at")), coverage_ok=None if holes else True)


def _snapshot_poc(snapshot: Mapping[str, Any]) -> Decimal | None:
    if snapshot.get("poc") is not None: return dec(snapshot["poc"])
    rows = snapshot.get("rows") or []
    if not rows: return None
    totals = [(dec(row["price"]), dec(row.get("total_volume", row.get("total", 0)))) for row in rows]
    maximum = max(v for _, v in totals); candidates = [p for p, v in totals if v == maximum]
    return candidates[0] if len(candidates) == 1 else None


@_override("O108")
def o108(inp: dict) -> RecipeResult:
    candle_id, use_at = inp.get("candle_id"), inp.get("use_at")
    supplied = inp.get("snapshots", []) or []
    if candle_id is None and supplied: candle_id = supplied[0].get("candle_id")
    if any(row.get("candle_id") not in {None, candle_id} for row in supplied):
        return _result("O108", "invalid", {"candle_id": candle_id, "same_candle": False,
            "snapshot_ids": [str(r.get("snapshot_id", i)) for i,r in enumerate(supplied)], "snapshot_count": len(supplied)}, base_ok=False, reason="POC snapshots cross candle identity")
    definitions=[row.get("candle_definition") for row in supplied]
    present_definitions=[item for item in definitions if item is not None]
    if present_definitions and any(item!=present_definitions[0] for item in present_definitions[1:]):
        return _result("O108","invalid",{"candle_id":candle_id,"candle_definition":None,
            "snapshot_ids":[str(r.get("snapshot_id",i)) for i,r in enumerate(supplied)],
            "snapshot_count":len(supplied),"same_candle":False},base_ok=False,
            reason="POC snapshots use different full candle definitions")
    visible = [row for row in supplied if use_at is None or _at(row) is None or _at(row) <= use_at]
    visible.sort(key=lambda row: (_at(row) if _at(row) is not None else -1, str(row.get("snapshot_id", ""))))
    pocs = [_snapshot_poc(row) for row in visible]
    first, last = (pocs[0] if pocs else None), (pocs[-1] if pocs else None)
    holes=[]
    if len(visible) < 2: holes.append("two_snapshots")
    if visible and any(row.get("candle_definition") is None for row in visible): holes.append("candle_definition")
    if any(p is None for p in pocs): holes.append("poc_tie")
    flip_at = next((_at(row) for row, poc in zip(visible[1:], pocs[1:]) if poc is not None and first is not None and poc != first), None)
    return _result("O108", "hole" if holes else "computed", {
        "candle_id": candle_id, "candle_definition":deepcopy(present_definitions[0]) if present_definitions else None,
        "snapshot_ids": [str(r.get("snapshot_id", i)) for i,r in enumerate(visible)],
        "snapshot_count": len(visible), "poc_before": first, "poc_after": last,
        "poc": last, "change": None if first is None or last is None or len(visible)<2 else last-first,
        "flip_at": flip_at, "same_candle": None if visible and any(row.get("candle_definition") is None for row in visible) else True,
    }, hole_ids=_holes("O108", holes), known_at=_known(visible, inp.get("known_at")), coverage_ok=None if holes else True)


def _ratio(numerator: Decimal, denominator: Decimal, zero_rule: str | None) -> tuple[Decimal | None, bool | None, str]:
    if denominator != 0:
        return numerator / denominator, None, "finite"
    if numerator == 0:
        return None, False if zero_rule == "does_not_qualify" else None, "undefined"
    flag = True if zero_rule == "qualifies" else False if zero_rule == "does_not_qualify" else None
    return None, flag, "unbounded"


def _runs(comparisons: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    runs=[]; current=[]
    for row in comparisons:
        if row["qualifies"] is True:
            current.append(row)
        else:
            if len(current)>=n: runs.append({"prices":[r["price"] for r in current], "band":[current[0]["price"],current[-1]["price"]], "length":len(current)})
            current=[]
    if len(current)>=n: runs.append({"prices":[r["price"] for r in current], "band":[current[0]["price"],current[-1]["price"]], "length":len(current)})
    return runs


@_override("O109")
def o109(inp: dict) -> RecipeResult:
    q=dec(inp.get("q", inp.get("tick_size", Decimal("0.25")))); threshold=dec(inp.get("ratio_min")); n=inp.get("row_count")
    zero_rule=inp.get("zero_rule")
    rows=inp.get("footprint_rows", inp.get("rows", [])) or []
    # Accept full B/A price rows or the legacy already-paired shape.
    levels={dec(r["price"]): (dec(r.get("B", r.get("buy_volume",0))),dec(r.get("A",r.get("sell_volume",0)))) for r in rows if r.get("price") is not None}
    buy_comp=[]; sell_comp=[]
    if levels:
        for price in sorted(levels):
            buy=levels[price][0]; lower_sell=levels.get(price-q,(Decimal(0),Decimal(0)))[1]
            ratio,zero_flag,relation=_ratio(buy,lower_sell,zero_rule); qualifies=zero_flag if ratio is None else None if threshold is None else ratio>=threshold
            buy_comp.append({"price":price,"numerator":buy,"denominator_price":price-q,"denominator":lower_sell,"ratio":ratio,"relation":relation,"qualifies":qualifies})
            sell=levels[price][1]; upper_buy=levels.get(price+q,(Decimal(0),Decimal(0)))[0]
            ratio,zero_flag,relation=_ratio(sell,upper_buy,zero_rule); qualifies=zero_flag if ratio is None else None if threshold is None else ratio>=threshold
            sell_comp.append({"price":price,"numerator":sell,"denominator_price":price+q,"denominator":upper_buy,"ratio":ratio,"relation":relation,"qualifies":qualifies})
    else:
        for row in sorted(rows,key=lambda r:dec(r["ask_px"])):
            num,den=dec(row["ask"]),dec(row["bid"]); ratio,zero_flag,relation=_ratio(num,den,zero_rule)
            qual=zero_flag if ratio is None else None if threshold is None else ratio>=threshold
            buy_comp.append({"price":dec(row["ask_px"]),"numerator":num,"denominator_price":dec(row.get("bid_px")),"denominator":den,"ratio":ratio,"relation":relation,"qualifies":qual})
    n_int=int(n) if n is not None else 1
    buy_runs=_runs(buy_comp,n_int); sell_runs=_runs(sell_comp,n_int)
    all_prices=[r["price"] for r in buy_comp]
    consecutive=all(b-a==q for a,b in zip(all_prices,all_prices[1:]))
    holes=[]
    if threshold is None or n is None: holes.append("settings")
    if zero_rule is None and any(r["denominator"]==0 for r in [*buy_comp,*sell_comp]): holes.append("zero_rule")
    ratios=[r["ratio"] for r in buy_comp]
    qualifies=None if threshold is None or n is None else bool(buy_runs or sell_runs)
    printed=None
    if inp.get("printed_ask") is not None and inp.get("printed_bid") is not None and dec(inp["printed_bid"])!=0: printed=dec(inp["printed_ask"])/dec(inp["printed_bid"])
    bands=[r["band"] for r in [*buy_runs,*sell_runs]]
    return _result("O109","hole" if holes else "computed",{
        "candle_id":inp.get("candle_id"),"ratio_min":threshold,"row_count":n,"zero_rule":zero_rule,
        "buy_comparisons":buy_comp,"sell_comparisons":sell_comp,"buy_runs":buy_runs,"sell_runs":sell_runs,
        "ratios":ratios,"consecutive":consecutive,"qualifies":qualifies,"stack_band":bands[0] if len(bands)==1 else None,
        "printed_ratio":printed,"automatic_settings":None,
    },hole_ids=_holes("O109",holes),known_at=inp.get("known_at"),coverage_ok=None if holes else True)


@_override("O110")
def o110(inp: dict) -> RecipeResult:
    b=dec(inp.get("buy_volume",inp.get("B"))); s=dec(inp.get("sell_volume",inp.get("S")))
    rule=inp.get("rule"); zero=inp.get("zero_rule")
    br,bflag,brel=_ratio(b,s,zero); sr,sflag,srel=_ratio(s,b,zero)
    pct=None if br is None else br*100; more=None if br is None else (br-1)*100
    flag=bflag
    if br is not None:
        flag=br>=Decimal("3.5") if rule=="350_of" else br>=Decimal("4.5") if rule=="350_more" else None
    holes=[] if rule in {"350_of","350_more"} else ["convention"]
    if (b==0 or s==0) and zero is None: holes.append("zero_rule")
    return _result("O110","hole" if holes else "computed",{
        "price":dec(inp.get("price")),"buy_volume":b,"sell_volume":s,"buy_multiple":br,"sell_multiple":sr,
        "buy_relation":brel,"sell_relation":srel,"percent_of":pct,"percent_more":more,"source_350_flag":flag,
        "meets_of":None if pct is None else pct==350,"meets_more":None if more is None else more>=350,
        "rule":rule,"zero_rule":zero,
    },hole_ids=_holes("O110",holes),known_at=inp.get("known_at"),coverage_ok=None if holes else True)


@_override("O111")
def o111(inp: dict) -> RecipeResult:
    rows=inp.get("events",[]) or []; records,missing=_trade_records(rows,strict_identity=False)
    start,end=inp.get("window_start"),inp.get("window_end")
    if records:
        records=[r for r in records if (start is None or r["event_key"] is None or r["event_key"]>=start) and (end is None or r["event_key"] is None or r["event_key"]<end)]
        count=Decimal(len(records)); contracts=sum((r["executed_size"] for r in records),Decimal(0))
        sec=None if start is None or end is None else Decimal(end-start)/Decimal(1_000_000_000)
    else:
        sec=dec(inp.get("interval_s")); count=dec(inp.get("n_prints")); contracts=dec(inp.get("contracts"))
    if sec is None or sec<=0: raise ValueError("tape window must have positive duration")
    panel=inp.get("source_panel_value")
    holes=missing+([] if panel is not None else ["panel"])
    return _result("O111","hole" if holes else "supplied",{
        "window_start":start,"window_end":end,"event_ids":[r["event_id"] for r in records],"print_count":int(count),
        "contracts":contracts,"duration_seconds":sec,"prints_per_second":count/sec,"contracts_per_second":contracts/sec,
        "source_panel_value":dec(panel),"automatic_speed":None,
    },hole_ids=_holes("O111",holes),known_at=_known(records,inp.get("known_at")),coverage_ok=None if holes else True)


@_override("O112")
def o112(inp: dict) -> RecipeResult:
    quote=inp.get("quote") if isinstance(inp.get("quote"),dict) else inp
    bid,ask=dec(quote.get("bid")),dec(quote.get("ask")); q=dec(inp.get("q",inp.get("tick_size")))
    definition=inp.get("instrument_definition")
    if q is None and definition is not None: q=dec(getattr(definition,"tick_size",None) if not isinstance(definition,dict) else definition.get("tick_size"))
    if q is None: q=Decimal("0.25") if not any(k in inp for k in RICH_MARKERS["O112"]) else None
    holes=[]
    if bid is None or ask is None: holes.append("quote")
    if q is None: holes.append("tick_size")
    if q is not None and q<=0: raise ValueError("tick size must be positive")
    spread=None if bid is None or ask is None else ask-bid
    crossed=None if spread is None else spread<0; locked=None if spread is None else spread==0
    stale=inp.get("stale")
    state="invalid" if crossed else "hole" if holes else "computed"
    return _result("O112",state,{"quote_id":quote.get("quote_id",quote.get("event_id")),"bid":bid,"ask":ask,
        "bid_size":dec(quote.get("bid_size")),"ask_size":dec(quote.get("ask_size")),"spread_points":spread,
        "spread_ticks":None if spread is None or q is None else spread/q,"locked":locked,"crossed":crossed,"stale":stale,
        "depth_coverage":"bbo"},hole_ids=_holes("O112",holes),known_at=_at(quote) or inp.get("known_at"),
        base_ok=False if crossed else None if holes else True,coverage_ok=None if holes else True,reason="crossed quote" if crossed else None)


@_override("O113")
def o113(inp: dict) -> RecipeResult:
    rows=inp.get("events",[]) or []; touch=inp.get("touch_at")
    filtered=[r for r in rows if touch is None or _event_at(r) is None or _event_at(r)<=touch]
    prices=[dec(r.get("price")) for r in filtered if r.get("price") is not None]
    times=[_event_at(r) for r in filtered if _event_at(r) is not None]
    p0=dec(inp.get("from_px",prices[0] if prices else None)); p1=dec(inp.get("to_px",prices[-1] if prices else None))
    t0=inp.get("from_at",times[0] if times else None); t1=inp.get("to_at",times[-1] if times else None)
    if t0 is None or t1 is None or t1<=t0: raise ValueError("approach endpoints are not ordered")
    sec=Decimal(t1-t0)/Decimal(1_000_000_000); net=abs(p1-p0)
    path=sum((abs(b-a) for a,b in zip(prices,prices[1:])),Decimal(0)) if len(prices)>1 else net
    records,missing=_trade_records(filtered,strict_identity=False); buy,sell,unknown=_volumes(records)
    arrival=inp.get("source_arrival"); holes=missing+([] if arrival is not None else ["interpretation"])
    return _result("O113","hole" if holes else "supplied",{
        "path_event_ids":[str(r.get("event_id",i)) for i,r in enumerate(filtered)],"from_price":p0,"to_price":p1,
        "from_at":t0,"to_at":t1,"duration_seconds":sec,"net_distance":net,"path_distance":path,"net_speed":net/sec,
        "aggressive_buy_volume":buy,"aggressive_sell_volume":sell,"aggressive_unknown_volume":unknown,"aggressive_arrival":arrival,
        "touch_at":touch,"post_touch_included":False,
    },hole_ids=_holes("O113",holes),known_at=t1,coverage_ok=None if holes else True)


@_override("O114")
def o114(inp: dict) -> RecipeResult:
    events=inp.get("events",[]) or []
    sizes=[int(r.get("size",r.get("executed_size"))) for r in events if _is_trade(r)] if events else [int(s) for s in inp.get("sizes",[])]
    if not sizes or any(s<=0 for s in sizes): raise ValueError("execution sizes must be positive")
    digits=[len(str(abs(s))) for s in sizes]; groups=deepcopy(inp.get("groups",inp.get("grouping")))
    declining=all(a>b for a,b in zip(digits,digits[1:]))
    classification=None if groups is None else declining
    holes=[] if groups is not None else ["threshold"]
    if events and any(not isinstance(r, Mapping) or r.get("event_id") is None for r in events): holes.append("event_id")
    if events and any(not isinstance(r, Mapping) or _event_at(r) is None or _at(r) is None for r in events): holes.append("event_availability")
    return _result("O114","hole" if holes else "supplied",{"event_ids":[str(r["event_id"]) for r in events if r.get("event_id") is not None],
        "sizes":sizes,"digit_counts":digits,"groups":groups,"declining":declining,"source_classification":classification,
        "window_start":inp.get("window_start"),"window_end":inp.get("window_end")},hole_ids=_holes("O114",holes),known_at=_known(events,inp.get("known_at")),coverage_ok=None if holes else True)


@_override("O115")
def o115(inp: dict) -> RecipeResult:
    origin=dec(inp.get("origin")); q=dec(inp.get("q",inp.get("tick_size")))
    if q is not None and q <= 0: raise ValueError("tick size must be positive")
    direction=str(inp.get("direction",inp.get("side",""))).lower(); sign=Decimal(1) if direction in {"long","buy","b"} else Decimal(-1) if direction in {"short","sell","a","s"} else None
    stage_map=inp.get("stage_ledger") if isinstance(inp.get("stage_ledger"),dict) else {"defense":inp.get("defense_at"),"replenishment":inp.get("refresh_at"),"exhaustion":inp.get("exhaustion_at"),"liftoff":inp.get("reward_at"),"entry":inp.get("entry_at")}
    stages=[(name,stage_map.get(name)) for name in ("defense","replenishment","exhaustion","liftoff","entry")]
    order,missing=_strict_times("O115",stages)
    reward=dec(inp.get("reward_price",inp.get("reward_px"))); raw=None if origin is None or reward is None else reward-origin
    points=None if raw is None else sign*raw if sign is not None else abs(raw)
    entry,confirm=dec(inp.get("entry")),dec(inp.get("confirm_px",reward)); distance=None if entry is None or confirm is None or q is None else abs(entry-confirm)/q
    geometry=None if distance is None else distance<=2
    defender_events = inp.get("defender_aggression_events", []) or []
    holes=missing+([] if sign is not None else ["direction"])+([] if defender_events else ["defender_aggression"])
    if q is None: holes.append("tick_size")
    if any(not isinstance(row, Mapping) or row.get("event_id") is None or _event_at(row) is None for row in defender_events):
        holes.append("defender_aggression_identity")
    return _result("O115","invalid" if order is False else "hole" if holes else "supplied",{"origin":origin,"direction":direction or None,
        "stage_ledger":stage_map,"defender_aggression_events":deepcopy(inp.get("defender_aggression_events",[])),"reward_price":reward,
        "reward_points":points,"reward_ticks":None if points is None or q is None else points/q,"entry_distance_ticks":distance,
        "directional_reward":None if points is None or sign is None else points>0,"geometry_ok":geometry,"order_ok":order},
        hole_ids=_holes("O115",holes),known_at=stage_map.get("entry",inp.get("known_at")),base_ok=False if order is False else None if holes else True,coverage_ok=None if holes else True,reason="stage order is reversed or tied" if order is False else None)


@_override("O116")
def o116(inp: dict) -> RecipeResult:
    zone=inp.get("zone"); zone_id=inp.get("zone_id")
    if zone is None: return _result("O116","hole",{"zone_id":zone_id,"automatic_zone":None},hole_ids=_holes("O116",["construction"]),known_at=inp.get("known_at"),coverage_ok=None)
    lo,hi=dec(zone[0]),dec(zone[1])
    if lo>hi: return _result("O116","invalid",{"zone_id":zone_id,"zone":[lo,hi]},base_ok=False,reason="zone bounds reversed")
    formed=inp.get("formed_at",inp.get("known_at")); dep=inp.get("departure_at"); departure=dec(inp.get("departure_price"))
    if dep is None or departure is None: return _result("O116","hole",{"zone_id":zone_id,"zone":[lo,hi],"zone_known_at":formed,"automatic_zone":None},hole_ids=_holes("O116",["departure"]),coverage_ok=None)
    if (formed is not None and dep<=formed) or lo<=departure<=hi: return _result("O116","invalid",{"zone_id":zone_id,"zone":[lo,hi],"zone_known_at":formed,"departure_at":dep,"later_touches":0,"automatic_zone":None},base_ok=False,reason="no actual departure outside formed zone")
    touch_ids=[]; touch_times=[]; inside=False; latest=dep; missing_touch_identity=False
    for i,row in enumerate(sorted(inp.get("touches",[]),key=lambda r:r.get("t",r.get("at",0)))):
        at=_event_at(row); px=dec(row.get("price"));
        if at is None or at<=dep: continue
        if inp.get("instrument_id") is not None and row.get("instrument_id",inp.get("instrument_id"))!=inp.get("instrument_id"): return _result("O116","invalid",{"zone_id":zone_id,"zone":[lo,hi]},base_ok=False,reason="touch instrument mismatch")
        latest=max(latest,at)
        if lo<=px<=hi:
            if not inside:
                touch_id=row.get("touch_id")
                if touch_id is None:
                    missing_touch_identity=True
                else:
                    touch_ids.append(str(touch_id))
                touch_times.append(at)
            inside=True
        else: inside=False
    holes=[] if inp.get("source_setting_id") is not None else ["construction"]
    if missing_touch_identity: holes.append("touch_identity")
    if not inp.get("formation_event_ids"): holes.append("formation_identity")
    if inp.get("departure_event_id") is None: holes.append("departure_identity")
    setting=inp.get("source_setting") if isinstance(inp.get("source_setting"),dict) else {}
    current_threshold=inp.get("threshold")
    if current_threshold is None and isinstance(inp.get("display_config"),dict): current_threshold=inp["display_config"].get("threshold")
    preserved=None
    if setting.get("instrument_id") is not None and setting.get("threshold") is not None and inp.get("instrument_id") is not None and current_threshold is not None:
        preserved=str(setting["instrument_id"])==str(inp["instrument_id"]) and dec(setting["threshold"])==dec(current_threshold)
    definition_recorded=all(value is not None for value in (zone_id,formed,inp.get("source_setting_id"))) and bool(inp.get("formation_event_ids"))
    return _result("O116","hole" if holes else "supplied",{"zone_id":zone_id,"zone":[lo,hi],"zone_known_at":formed,
        "source_setting_id":inp.get("source_setting_id"),"formation_event_ids":list(inp.get("formation_event_ids",[])),"departure_at":dep,
        "touch_ids":touch_ids,"later_touches":None if missing_touch_identity else len(touch_ids),"automatic_zone":None,"later_high_replaces_origin":False,
        "zone_definition_recorded":definition_recorded,"zone_frozen":True if definition_recorded else None,
        "instrument_and_threshold_preserved":preserved,"departure_observed":True if inp.get("departure_event_id") is not None else None,
        "distinct_touch_id":len(touch_ids)==len(set(touch_ids)) and bool(touch_ids),
        "touch_at":touch_times[0] if touch_times else None},hole_ids=_holes("O116",holes),known_at=latest,coverage_ok=None if holes else True)


@_override("O117")
def o117(inp: dict) -> RecipeResult:
    cutoff=inp.get("cutoff"); current_at=inp.get("current_touch_at"); current_id=inp.get("current_touch_id"); zone_id=inp.get("zone_id")
    invalid=[]; missing=[]; eligible=[]; unresolved=[]; identities=[]; starts=set(); latest=None
    if current_at is None: missing.append("current_touch_at")
    if current_id is None: missing.append("current_touch_id")
    if zone_id is None: missing.append("zone_id")
    if inp.get("history_coverage_complete") is not True: missing.append("history_coverage")
    elif cutoff is None: missing.append("cutoff")
    elif cutoff>=current_at: invalid.append("feature cutoff must precede current touch")
    for row in inp.get("priors",[]):
        pid=row.get("id",row.get("touch_id")); start=row.get("start",row.get("t")); resolved=row.get("defense_at")
        if pid is None or start is None: missing.append("prior_touch_identity"); continue
        if zone_id is not None and row.get("zone_id",zone_id)!=zone_id: invalid.append("history belongs to another zone"); continue
        if pid==current_id or current_at is not None and start>=current_at or cutoff is not None and start>cutoff: continue
        if pid in identities or start in starts: continue
        identities.append(pid); starts.add(start)
        if resolved is not None and cutoff is not None and resolved<=cutoff: eligible.append(pid); latest=max(latest or resolved,resolved)
        else: unresolved.append(pid)
    claimed=inp.get("selected_history_ids")
    if claimed is not None and not set(claimed)<=set(eligible): invalid.append("memory includes unresolved or unavailable touch")
    return _result("O117","invalid" if invalid else "hole" if missing else "computed",{"zone_id":zone_id,
        "prior_touch_count":len(identities),"resolved_defense_count":len(eligible),"prior_resolved_defense_count":len(eligible),
        "eligible_history_ids":eligible,"unresolved_history_ids":unresolved,"max_feature_known_at":latest,
        "memory_causal":False if invalid else None if missing else True,"current_counts_as_prior":False,
        "memory_uses_only_prior_resolved_touches":False if invalid else None if missing else True},
        hole_ids=_holes("O117",missing+(["ordering_identity"] if invalid else [])),known_at=latest or cutoff,
        base_ok=False if invalid else None if missing else True,coverage_ok=None if missing else True,reason="; ".join(invalid) or None)


@_override("O118")
def o118(inp: dict) -> RecipeResult:
    origin=inp.get("origin"); origin_id=inp.get("origin_id"); side=inp.get("side")
    if origin is None: return _result("O118","hole",{"origin_id":origin_id,"linked":None},hole_ids=_holes("O118",["origin"]),coverage_ok=None)
    ledger=deepcopy(inp.get("stage_ledger",{}))
    if not ledger: ledger={name:inp.get(f"{name}_at") for name in ("release","failure","refill","drive","hold","retest","reward","entry")}
    required=inp.get("required_stages"); aliases={"refill":"refill","drive":"drive","hold":"hold"}
    missing=[]
    if not isinstance(required,list) or not required:
        missing.append("required_stage_definition"); required=[]
    missing.extend(name for name in required if ledger.get(aliases.get(name,name)) is None)
    present=[(name,ledger.get(name)) for name in ("release","failure","refill","drive","hold","retest","reward","entry") if ledger.get(name) is not None]
    rich = any(k in inp for k in RICH_MARKERS["O118"])
    order=None if len(present)<2 or missing else all(a[1]<b[1] for a,b in zip(present,present[1:]))
    branch_ok=kleene_and(order, False if any(name in missing for name in required) else None if missing else True)
    holes=[]
    if origin_id is None: holes.append("origin_id")
    holes.extend(missing)
    return _result("O118","invalid" if order is False else "hole" if holes else "supplied",{"origin_id":origin_id,"origin":[dec(origin[0]),dec(origin[1])],"side":side,
        "stage_ledger":ledger,"linked":True if origin_id is not None else None,"branch_ok":branch_ok,
        "missing_stages":missing,"failed_push_count":inp.get("failed_pushes"),"later_high_replaces_origin":False},
        hole_ids=_holes("O118",holes),known_at=inp.get("entry_at",inp.get("known_at")),base_ok=False if order is False else None if holes else True,coverage_ok=None if holes else True,reason="stage identity/order conflict" if order is False else None)


@_override("O119")
def o119(inp: dict) -> RecipeResult:
    fail_at=inp.get("fail_at"); ids=[]; resolved_times=set(); history=inp.get("history_coverage_complete") is True
    for row in inp.get("prior_failures",[]):
        fid=row.get("id"); at=row.get("known_at",row.get("t"))
        if inp.get("band_id") is not None and row.get("band_id",inp.get("band_id"))!=inp.get("band_id"): return _result("O119","invalid",{"band_id":inp.get("band_id"),"order_ok":False},base_ok=False,reason="historical failure band identity mismatch")
        if at is not None and fail_at is not None and at>=fail_at: return _result("O119","invalid",{"band_id":inp.get("band_id"),"order_ok":False},base_ok=False,reason="historical failure is not prior")
        if fid is None or at is None: history=False
        if fid is not None and fid not in ids and at not in resolved_times: ids.append(fid)
        if at is not None: resolved_times.add(at)
    ledger={"failure":fail_at,"breakdown":inp.get("breakdown_at"),"retest":inp.get("retest_at"),"confirmation":inp.get("confirm_at"),"entry":inp.get("entry_at")}
    order,missing=_strict_times("O119",list(ledger.items()))
    current=inp.get("current_evidence",{})
    body=inp.get("body_selling",current.get("body_selling")); control=inp.get("control_side",current.get("control_side"))
    for name,value in (("current_failed_aggression",current.get("failed_aggression")),("body_selling",body),("control_side",control)):
        if value is None: missing.append(name)
    holes=([] if history else ["prior_failure_history"])+missing
    prior_known_at=max(resolved_times) if resolved_times else None
    return _result("O119","invalid" if order is False else "hole" if holes else "supplied",{"band_id":inp.get("band_id"),"extreme":inp.get("extreme"),
        "prior_failure_ids":ids,"distinct_failures":len(ids),"historical_failures_known":history and bool(ids),"current_stage_ledger":ledger,
        "current_evidence_complete":None if holes else True,"order_ok":order,"body_selling":body,"control_side":control,
        "two_distinct_prior_failures":history and len(ids)>=2,"prior_failures_known_at":prior_known_at},
        hole_ids=_holes("O119",holes),known_at=inp.get("confirm_at",inp.get("known_at")),base_ok=False if order is False else None if holes else True,coverage_ok=None if holes else True,reason="current stage order is incomplete or reversed" if order is False else None)


def _tick_rows(lo: Decimal, hi: Decimal, q: Decimal) -> list[Decimal]:
    span=(hi-lo)/q
    if span != span.to_integral_value(): raise ValueError("candle bounds are off tick grid")
    return [lo+q*i for i in range(int(span)+1)]


def _price_key(value: Decimal) -> str:
    """Stable JSON map key without scale artifacts from tick iteration."""
    normalized = value.normalize()
    return format(normalized, "f")


@_override("O120")
def o120(inp: dict) -> RecipeResult:
    o,h,l,c=(dec(inp.get(k)) for k in ("O","H","L","C")); q=dec(inp.get("tick_size",inp.get("q")))
    if None in (o,h,l,c) or h<max(o,l,c) or l>min(o,h,c): raise ValueError("invalid candle OHLC")
    if q is None:
        return _result("O120", "hole", {"candle_id": inp.get("candle_id"), "instrument_id": inp.get("instrument_id"),
                       "O": o, "H": h, "L": l, "C": c}, hole_ids=_holes("O120", ["tick_size"]),
                       known_at=inp.get("known_at", inp.get("formation_end")), coverage_ok=None)
    if q<=0: raise ValueError("tick size must be positive")
    records,missing=_trade_records(inp.get("events",inp.get("trades",[])),strict_identity=False,as_of=inp.get("as_of"))
    candle_id=inp.get("candle_id")
    if candle_id is not None and any(r["candle_id"] not in {None,candle_id} for r in records): return _result("O120","invalid",{"candle_id":candle_id,"O":o,"H":h,"L":l,"C":c},base_ok=False,reason="execution belongs to another candle")
    accum={price:[Decimal(0),Decimal(0),Decimal(0)] for price in _tick_rows(l,h,q)}
    for record in records:
        if record["price"] not in accum: return _result("O120","invalid",{"candle_id":candle_id,"O":o,"H":h,"L":l,"C":c,"event_ids":[r["event_id"] for r in records]},base_ok=False,reason="trade price outside candle")
        accum[record["price"]][{"B":0,"A":1,"N":2}[record["side"]]]+=record["executed_size"]
    rows=[]
    for price,(buy,sell,unknown) in sorted(accum.items()):
        kd=buy-sell; rows.append({"price":price,"buy_volume":buy,"sell_volume":sell,"unknown_volume":unknown,"total_volume":buy+sell+unknown,
            "known_delta":kd,"full_delta":kd if unknown==0 else None,"delta_low":kd-unknown,"delta_high":kd+unknown,
            "region":"body" if min(o,c)<=price<=max(o,c) else "lower_wick" if price<min(o,c) else "upper_wick"})
    buy={_price_key(r["price"]):r["buy_volume"] for r in rows}; sell={_price_key(r["price"]):r["sell_volume"] for r in rows}; unknowns={_price_key(r["price"]):r["unknown_volume"] for r in rows}; totals={_price_key(r["price"]):r["total_volume"] for r in rows}
    known_delta=sum((r["known_delta"] for r in rows),Decimal(0)); unknown=sum((r["unknown_volume"] for r in rows),Decimal(0)); total=sum((r["total_volume"] for r in rows),Decimal(0))
    max_volume=max(totals.values()) if totals else Decimal(0); candidates=[r["price"] for r in rows if r["total_volume"]==max_volume]
    tie_policy=inp.get("poc_tie_policy"); poc=candidates[0] if len(candidates)==1 else min(candidates) if tie_policy=="lowest" else max(candidates) if tie_policy=="highest" else None
    body_delta=sum((r["known_delta"] for r in rows if r["region"]=="body"),Decimal(0)); body_unknown=sum((r["unknown_volume"] for r in rows if r["region"]=="body"),Decimal(0))
    config=deepcopy(inp.get("display_config")); marker_ids=[]
    if config:
        threshold=dec(config.get("threshold")); comparator=config.get("comparator")
        if threshold is None or comparator not in {">",">="}: missing.append("display_config")
        else: marker_ids=[r["event_id"] for r in records if r["executed_size"]>=threshold if comparator==">="] if comparator==">=" else [r["event_id"] for r in records if r["executed_size"]>threshold]
    if inp.get("coverage_ok") is not True: missing.append("candle_coverage")
    if inp.get("body_rows") and not records: missing.append("execution_records")
    if candle_id is None: missing.append("candle_id")
    if inp.get("instrument_id") is None: missing.append("instrument_id")
    return _result("O120","hole" if missing else "computed",{"candle_id":candle_id,"candle_definition":deepcopy(inp.get("candle_definition")),"instrument_id":inp.get("instrument_id"),"tick_size":q,
        "O":o,"H":h,"L":l,"C":c,"formation_start":inp.get("formation_start"),"formation_end":inp.get("formation_end"),"as_of":inp.get("as_of"),
        "rows":rows,"buy_by_price":buy,"sell_by_price":sell,"unknown_by_price":unknowns,"total_by_price":totals,"event_ids":[r["event_id"] for r in records],
        "total_volume":total,"known_delta":known_delta,"delta":known_delta if unknown==0 else None,"delta_interval":[known_delta-unknown,known_delta+unknown],
        "body_prices":[min(o,c),max(o,c)],"wick_low":l,"wick_high":h,"body_delta":body_delta if body_unknown==0 else None,
        "poc":poc,"poc_candidates":candidates,"poc_tie_state":"unique" if len(candidates)==1 else "resolved" if poc is not None else "unresolved",
        "display_config":config,"marker_event_ids":marker_ids,"later_price_in_earlier_asof":False},
        hole_ids=_holes("O120",missing),known_at=_known(records,inp.get("known_at",inp.get("formation_end"))),coverage_ok=None if missing else True)


def _native_inputs(config: Mapping[str, Any], resolved: Any, allowed: tuple[str, ...] = ()) -> dict[str, Any]:
    """Admit only recipe-scoped literals; measurements come from native rows."""
    out={key: deepcopy(config[key]) for key in allowed if key in config}
    out["events"]=resolved.rows(); out["instrument_id"]=resolved.instrument_id
    out["formation_start"],out["formation_end"]=resolved.start_ns,resolved.end_ns
    out.setdefault("as_of",resolved.end_ns); out["coverage_ok"]=resolved.coverage_ok
    out["known_at"]=resolved.known_at
    definition=resolved.instrument_definition
    if definition is not None:
        # Price units are immutable source metadata.  A recipe literal may
        # select a comparison rule, but can never replace the instrument tick.
        for key in ("q", "tick_size"):
            if key in config and dec(config[key]) != definition.tick_size:
                raise NativeEvidenceError("caller tick size conflicts with native instrument definition")
        out["q"]=definition.tick_size
        out["tick_size"]=definition.tick_size
        out["instrument_definition"]=definition
    return out


def native_o098(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    return o098(_native_inputs(config,resolved,("as_of",)))
def native_o105(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    for key in ("reference","reset_verified"):
        if key in config:
            raise NativeEvidenceError(f"O105 {key} must not be a caller observation")
    if config.get("reset_at") not in (None,resolved.start_ns):
        raise NativeEvidenceError("O105 reset must equal the exact native window start")
    values=_native_inputs(config,resolved,("as_of",))
    reset=config.get("reset_policy")
    reset_known=False
    if reset is not None:
        if (not isinstance(reset,Mapping) or set(reset)!={"policy_id","start_ns","kind"} or
                reset.get("kind")!="declared_comparison" or reset.get("start_ns")!=resolved.start_ns or
                reset.get("policy_id") is None):
            raise NativeEvidenceError("O105 reset_policy must declare this exact native comparison window")
        values.update(reset_id=str(reset["policy_id"]),reset_at=resolved.start_ns,reset_verified=True)
        reset_known=True
    else:
        values.update(reset_id=None,reset_at=resolved.start_ns,reset_verified=None)
    parents=config.get("dependencies",[])
    reference=None
    if parents:
        roles=config.get("parent_roles")
        if (len(parents)!=1 or not isinstance(roles,Mapping) or set(roles)!={"reference"} or
                str(roles["reference"])!=str(parents[0].get("object_id"))):
            raise NativeEvidenceError("O105 reference requires exactly one selected actual parent")
        reference=_pv(parents[0],"cvd","delta","known_cvd","reference")
        if reference is None: raise NativeEvidenceError("O105 reference parent has no actual contracts value")
    values.update(reference=reference,reference_unit="contracts")
    result=o105(values)
    if not reset_known:
        result.state="hole" if result.state!="invalid" else result.state
        result.coverage_ok=None
        result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O105",["reset_policy"])))
    return result
def native_o111(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    values=_native_inputs(config,resolved,("window_start","window_end")); values.setdefault("window_start",resolved.start_ns); values.setdefault("window_end",resolved.end_ns); return o111(values)
def native_o112(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    rows=resolved.rows(); cutoff=config.get("as_of",resolved.end_ns)
    quotes=[r for r in rows if (r.get("bid") is not None or r.get("ask") is not None)
            and (_event_at(r) is None or _event_at(r)<=cutoff)
            and (_at(r) is None or _at(r)<=cutoff)]
    if not quotes: raise NativeEvidenceError("O112 has no native BBO observation")
    if any(_event_at(row) is None or _at(row) is None for row in quotes):
        raise NativeEvidenceError("O112 native quote lacks event or availability time")
    latest=max(_event_at(row) for row in quotes)
    batch=[row for row in quotes if _event_at(row)==latest]
    if len(batch)>1:
        sequence=[row.get("exchange_sequence") for row in batch]
        if None in sequence or len(set(sequence)) != len(sequence):
            raise NativeEvidenceError("O112 latest quote batch has unknown order")
    quotes.sort(key=lambda row: (_event_at(row), row.get("exchange_sequence") or 0))
    values=_native_inputs(config,resolved,()); values["quote"]=quotes[-1]; return o112(values)
def native_o113(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    if any(key in config for key in ("from_px","to_px","from_at","to_at")):
        raise NativeEvidenceError("O113 endpoints must come from actual native executions")
    if config.get("touch_at") not in (None,resolved.end_ns):
        raise NativeEvidenceError("O113 touch must be the exact native window end")
    rows=[row for row in resolved.rows() if _is_trade(row) and _event_at(row)<=resolved.end_ns]
    if len(rows)<2: raise NativeEvidenceError("O113 requires at least two actual approach executions")
    tied={}
    for row in rows:tied.setdefault(_event_at(row),[]).append(row)
    ambiguous_order=False
    for batch in tied.values():
        if len(batch)>1 and len({row.get("price") for row in batch})>1:
            seq=[row.get("exchange_sequence") for row in batch]
            if None in seq or len(set(seq))!=len(seq):
                ambiguous_order=True
    if ambiguous_order:
        records,missing=_trade_records(rows,strict_identity=False)
        buy,sell,unknown=_volumes(records)
        return _result("O113","hole",{
            "path_event_ids":[record["event_id"] for record in records],
            "from_price":None,"to_price":None,"from_at":None,"to_at":None,
            "duration_seconds":None,"net_distance":None,"path_distance":None,"net_speed":None,
            "aggressive_buy_volume":buy,"aggressive_sell_volume":sell,
            "aggressive_unknown_volume":unknown,"aggressive_arrival":None,
            "touch_at":resolved.end_ns,"post_touch_included":False,
        },hole_ids=_holes("O113",missing+["event_order","interpretation"]),
            known_at=_known(records,resolved.known_at),coverage_ok=None,
            reason="approach path has unknown tied execution order")
    rows.sort(key=lambda row:(_event_at(row),row.get("exchange_sequence") or 0))
    values=_native_inputs(config,resolved,());values["events"]=rows;values["touch_at"]=resolved.end_ns
    return o113(values)
def native_o120(config: Mapping[str, Any], resolved: Any) -> RecipeResult:
    values=_native_inputs(config,resolved,("as_of","poc_tie_policy","display_config","candle_selection"))
    parents=config.get("dependencies",[])
    matches=[p for p in parents if p.get("recipe_id")=="O004"]
    if len(matches) != 1:
        raise NativeEvidenceError("O120 requires exactly one actual O004 candle parent")
    parent=matches[0]; candle=parent.get("value")
    if not isinstance(candle,Mapping): raise NativeEvidenceError("O120 requires its actual completed O004 candle parent")
    if parent.get("state") != "computed" or candle.get("complete") is not True:
        raise NativeEvidenceError("O120 candle parent is not a completed native bar")
    if str(candle.get("instrument_id")) != str(resolved.instrument_id):
        raise NativeEvidenceError("O120 candle parent instrument mismatch")
    if candle.get("start") != resolved.start_ns or candle.get("end") != resolved.end_ns:
        raise NativeEvidenceError("O120 candle parent interval mismatch")
    for key in ("candle_id","O","H","L","C"): values[key]=candle.get(key if key!="candle_id" else "bar_id",candle.get(key))
    selection=config.get("candle_selection")
    if selection is not None:
        if not isinstance(selection,Mapping) or set(selection) != {"candle_id","start_ns","end_ns","defined_at"}:
            raise NativeEvidenceError("O120 candle_selection requires exact formation identity")
        if (type(selection["start_ns"]) is not int or type(selection["end_ns"]) is not int or
                type(selection["defined_at"]) is not int or selection["candle_id"] is None):
            raise NativeEvidenceError("O120 candle_selection has invalid identity or clocks")
        if not (selection["start_ns"]==resolved.start_ns < resolved.end_ns<=selection["end_ns"]):
            raise NativeEvidenceError("O120 resolved snapshot is outside selected candle formation")
        if selection["defined_at"]>resolved.end_ns:
            raise NativeEvidenceError("O120 candle selection was defined after the snapshot")
        values["candle_id"]=str(selection["candle_id"])
        values["candle_definition"]=deepcopy(dict(selection))
    else:
        values["candle_definition"]={"candle_id":str(values["candle_id"]),
            "start_ns":candle["start"],"end_ns":candle["end"],"defined_at":candle["start"]}
    return o120(values)


class LocalFlowDerivationError(ValueError):
    pass


_ORIGIN_PARENTS = {"O002","O047","O053","O055","O086","O098","O099","O100","O101","O102","O107","O116","O119"}
_REWARD_PARENTS = {"O002","O004","O098","O104","O113","O120"}
DERIVED_PARENT_ROLES: dict[str, dict[str, set[str]]] = {
    "O099": {"tape": {"O098"}},
    "O100": {"executions": {"O098"}, "quote_before": {"O112"}, "quote_after": {"O112"}},
    "O101": {"executions": {"O098"}, "response": {"O004", "O104", "O120"}},
    "O102": {"executions": {"O098"}, "quote_before": {"O112"}, "quote_after": {"O112"}},
    "O103": {"executions": {"O098"}, "quote": {"O112"}, "tick": {"O120"}},
    "O104": {"origin": _ORIGIN_PARENTS, "reward": _REWARD_PARENTS, "tick": {"O120"}},
    "O106": {"candle": {"O004"}, "footprint": {"O120"}},
    "O107": {"footprint": {"O120"}},
    "O108": {"snapshots": {"O120"}},
    "O109": {"footprint": {"O120"}},
    "O110": {"footprint": {"O120"}},
    "O114": {"tape": {"O098"}},
    "O115": {"defense": {"O100"}, "replenishment": {"O102"}, "exhaustion": {"O114"},
             "aggression": {"O098"}, "liftoff": {"O104"},
             "decision": {"O004", "O150"}, "tick": {"O120"}},
    "O116": {"formation": {"O099"}, "departure": {"O104"}, "touches": {"O002"}},
    "O117": {"zone": {"O116"}, "current_touch": {"O002"},
             "feature_cutoff": {"O003","O148","O150"}, "history": {"O116"}},
    "O118": {"origin": {"O116"}, "failed_pushes": {"O101","O107"}, "release": {"O104"},
             "refill": {"O102"}, "drive": {"O104"}, "hold": {"O002","O100","O102"},
             "decision": {"O004", "O150"}},
    "O119": {"prior_failures": {"O119"}, "failure": {"O101", "O107"},
             "breakdown": {"O104"}, "retest": {"O002"},
             "confirmation": {"O100", "O102", "O114"}, "decision": {"O004", "O150"}},
}
_PLURAL_DERIVED_ROLES = {("O108", "snapshots"), ("O116", "touches"),
                         ("O117", "history"), ("O118", "failed_pushes"),
                         ("O119", "prior_failures")}


def _derived_roles(recipe_id: str, config: Mapping[str, Any], parents: list[dict]) -> dict[str, Any]:
    selected=config.get("parent_roles"); required=DERIVED_PARENT_ROLES[recipe_id]
    if not isinstance(selected, Mapping) or set(selected) != set(required):
        raise LocalFlowDerivationError(f"{recipe_id} requires exact semantic parent_roles {sorted(required)}")
    index={str(parent.get("object_id")):parent for parent in parents}
    if len(index)!=len(parents) or any(parent.get("object_id") is None for parent in parents):
        raise LocalFlowDerivationError("parent object identities are absent or duplicated")
    used=[]; roles={}
    for role,allowed in required.items():
        plural=(recipe_id,role) in _PLURAL_DERIVED_ROLES
        raw=selected[role]; ids=raw if plural else [raw]
        if not isinstance(ids,list) or not ids or (not plural and len(ids)!=1):
            raise LocalFlowDerivationError(f"{role} must select {'one or more' if plural else 'one'} actual parent IDs")
        matches=[]
        for object_id in ids:
            parent=index.get(str(object_id))
            if parent is None: raise LocalFlowDerivationError(f"{role} selects an absent parent")
            if parent.get("recipe_id") not in allowed: raise LocalFlowDerivationError(f"{role} parent has the wrong producer identity")
            if parent.get("state")=="invalid" or parent.get("recipe_base_ok") is False:
                raise LocalFlowDerivationError(f"{role} parent is invalid")
            matches.append(parent); used.append(str(object_id))
        roles[role]=matches if plural else matches[0]
    if len(used)!=len(set(used)) or set(used)!=set(index):
        raise LocalFlowDerivationError("semantic parent roles must cover each actual parent exactly once")
    return roles


def _pv(parent: Mapping[str, Any], *fields: str) -> Any:
    value=parent.get("value",{})
    for field in fields:
        if isinstance(value,Mapping) and value.get(field) is not None: return deepcopy(value[field])
    return None


def _parent_events(parent: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows=_pv(parent,"event_records") or []
    return [{**row,"event_ns":row.get("event_key"),"size":row.get("executed_size"),
             "known_at":row.get("known_at"),"action":"T"} for row in rows]


def _parent_price(parent: Mapping[str, Any], *, last: bool=False) -> Decimal | None:
    fields=("C","reward_price","to_price","departure_price","price","extreme","origin") if last else (
        "origin","from_price","O","price","extreme","reward_price","C")
    value=_pv(parent,*fields)
    if isinstance(value,(list,tuple)) and value: value=value[-1] if last else value[0]
    if value is None:
        events=_pv(parent,"event_records") or []
        if events: value=events[-1 if last else 0].get("price")
    return dec(value)


def _parent_side(parent: Mapping[str, Any]) -> Any:
    return _pv(parent,"direction","side","control_side","passive_side")


def _latest_row_time(rows: Any) -> int | None:
    if not isinstance(rows,list): return None
    times=[_event_at(row) for row in rows if isinstance(row,Mapping)]
    values=[at for at in times if type(at) is int]
    return max(values) if values else None


def _derive_source_composite(recipe_id: str, config: Mapping[str, Any], role: dict[str, Any]) -> RecipeResult:
    """Build source composites exclusively from selected parent observations.

    These adapters intentionally preserve a hole when a parent does not carry
    a source-only classification.  Scalar manifest literals never become
    defense, exhaustion, hold, failure, or confirmation facts.
    """
    if recipe_id=="O115":
        defense,replenishment,exhaustion,aggression,liftoff,decision=(role[name] for name in
            ("defense","replenishment","exhaustion","aggression","liftoff","decision"))
        defense_fact=_pv(defense,"defense_interpretation")
        replenishment_fact=_pv(replenishment,"verified_replenishment")
        exhaustion_fact=_pv(exhaustion,"source_classification")
        reward_fact=_pv(liftoff,"directional_reward")
        direction=_parent_side(defense) or _parent_side(liftoff)
        code="B" if str(direction).lower() in {"long","buy","b"} else "A" if str(direction).lower() in {"short","sell","a","s"} else None
        defender_events=[row for row in _parent_events(aggression) if code is not None and row.get("side")==code]
        lift_at=max((row["event_ns"] for row in defender_events),default=None)
        defense_at=_latest_row_time(_pv(defense,"local_executions","local_quote_snapshots"))
        replenishment_at=_latest_row_time(_pv(replenishment,"refresh_events","observed_same_price_size_changes"))
        exhaustion_at=_pv(exhaustion,"window_end")
        entry_at=_pv(decision,"decision_at","order_at","end")
        origin=_parent_price(defense);band=_pv(defense,"band")
        if origin is None and isinstance(band,(list,tuple)) and len(band)==2 and dec(band[0])==dec(band[1]):origin=dec(band[0])
        return o115({"origin":origin,"direction":direction,
            "tick_size":_pv(role["tick"],"tick_size"),
            "stage_ledger":{"defense":defense_at if defense_fact is not None else None,
                "replenishment":replenishment_at if replenishment_fact is True else None,
                "exhaustion":exhaustion_at if exhaustion_fact is True else None,
                "liftoff":lift_at if reward_fact is True else None,"entry":entry_at},
            "defender_aggression_events":defender_events,"reward_price":_parent_price(liftoff,last=True),
            "entry":_parent_price(decision,last=True),"confirm_px":_parent_price(liftoff,last=True)})
    if recipe_id=="O116":
        formation,departure=role["formation"],role["departure"]
        markers=_pv(formation,"marker_events") or []
        prices=[dec(row.get("price")) for row in markers if row.get("price") is not None]
        construction=_pv(formation,"source_display_known")
        zone=[min(prices),max(prices)] if prices and construction is True else None
        formed_at=_latest_row_time(markers)
        departure_at=_pv(departure,"reward_at")
        touches=[]; missing_touch=False
        for parent in role["touches"]:
            pv=parent.get("value",{}); actual=pv.get("touch_events")
            if not isinstance(actual,list):
                if all(pv.get(key) is not None for key in ("touch_id","touch_at","touch_price")):
                    actual=[{"touch_id":pv["touch_id"],"event_ns":pv["touch_at"],"known_at":parent.get("known_at"),"price":pv["touch_price"]}]
                else:actual=[];missing_touch=True
            touches.extend({**deepcopy(row),"instrument_id":row.get("instrument_id",parent.get("instrument_id"))} for row in actual)
        result=o116({"zone_id":formation["object_id"] if construction is True else None,"zone":zone,"known_at":formation.get("known_at"),
            "formed_at":formed_at,"source_setting_id":_pv(formation,"source_setting_id"),
            "formation_event_ids":[event_id for row in markers for event_id in row.get("event_ids",[])],
            "departure_at":departure_at,"departure_price":_parent_price(departure,last=True),
            "departure_event_id":departure["object_id"],"touches":touches,
            "instrument_id":formation.get("instrument_id")})
        if missing_touch:
            result.state="hole" if result.state!="invalid" else result.state;result.coverage_ok=None
            result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O116",["touch_evidence"])))
        return result
    if recipe_id=="O117":
        zone,current,cutoff_parent=role["zone"],role["current_touch"],role["feature_cutoff"]
        zv=zone.get("value",{}); current_at=_pv(current,"touch_at","contact_at")
        cutoff=_pv(cutoff_parent,"bar_close_at","window_known_at","decision_at","end")
        priors=[]; complete=True
        for parent in role["history"]:
            value=parent.get("value",{})
            ledger=value.get("touch_ledger")
            if isinstance(ledger,list):
                priors.extend(deepcopy(ledger))
            elif len(value.get("touch_ids") or [])==1 and type(value.get("touch_at")) is int:
                priors.append({"id":value["touch_ids"][0],"zone_id":value.get("zone_id"),
                               "start":value["touch_at"],"defense_at":None})
                complete=False
            else:complete=False
        return o117({"zone_id":zv.get("zone_id"),"current_touch_id":current["object_id"],
            "current_touch_at":current_at,"cutoff":cutoff,
            "history_coverage_complete":complete and all(parent.get("recipe_coverage_ok") is True for parent in role["history"]),
            "priors":priors})
    if recipe_id=="O118":
        origin=role["origin"]; ov=origin.get("value",{})
        failed=role["failed_pushes"]
        actual_failures=[p for p in failed if _pv(p,"absorption","source_spike") is True]
        release_ok=_pv(role["release"],"directional_reward") is True
        refill_ok=_pv(role["refill"],"verified_replenishment") is True
        drive_ok=_pv(role["drive"],"directional_reward") is True
        hold_value=_pv(role["hold"],"hold","source_hold","defense_interpretation")
        hold_ok=hold_value is True or isinstance(hold_value,str)
        refill_at=_latest_row_time(_pv(role["refill"],"refresh_events","observed_same_price_size_changes"))
        ledger={"release":_pv(role["release"],"reward_at") if release_ok else None,
                "failure":max((p.get("known_at") for p in actual_failures if type(p.get("known_at")) is int),default=None),
                "refill":refill_at if refill_ok else None,
                "drive":_pv(role["drive"],"reward_at") if drive_ok else None,
                "hold":_pv(role["hold"],"hold_at","contact_at") if hold_ok else None,
                "entry":_pv(role["decision"],"decision_at","order_at","end")}
        origin_ok=ov.get("zone_definition_recorded") is True and ov.get("zone_frozen") is True
        return o118({"origin_id":ov.get("zone_id") if origin_ok else None,"origin":deepcopy(ov.get("zone")) if origin_ok else None,
            "side":_parent_side(origin),"stage_ledger":ledger,
            "required_stages":["release","failure","refill","drive","hold","entry"],
            "failed_pushes":len(actual_failures),"known_at":role["decision"].get("known_at")})
    if recipe_id=="O119":
        failure,breakdown,retest,confirmation,decision=(role[name] for name in
            ("failure","breakdown","retest","confirmation","decision"))
        prior=[]
        for parent in role["prior_failures"]:
            pv=parent.get("value",{})
            prior.append({"id":parent["object_id"],"band_id":pv.get("band_id"),"known_at":parent.get("known_at")})
        band=_pv(failure,"band","stack_band","origin_band")
        band_id=_pv(failure,"band_id") or failure["object_id"]
        return o119({"band_id":band_id,"extreme":_pv(failure,"extreme"),"prior_failures":prior,
            "history_coverage_complete":all(p.get("recipe_coverage_ok") is True for p in role["prior_failures"]),
            "fail_at":failure.get("known_at"),"breakdown_at":breakdown.get("known_at"),
            "retest_at":retest.get("known_at"),"confirm_at":confirmation.get("known_at"),
            "entry_at":decision.get("known_at"),"current_evidence":{
                "failed_aggression":_pv(failure,"source_spike","absorption"),
                "body_selling":_pv(confirmation,"body_selling"),
                "control_side":_parent_side(confirmation)},"known_at":decision.get("known_at")})
    raise LocalFlowDerivationError(f"{recipe_id} has no parent-derived adapter")


def _derived_local_flow(recipe_id: str, config: Mapping[str, Any], parents: list[dict]) -> RecipeResult:
    try:
        role=_derived_roles(recipe_id,config,parents)
        if recipe_id=="O099":
            inp={"events":_parent_events(role["tape"]),"known_at":role["tape"].get("known_at")}
            setting=config.get("comparison_policy")
            if isinstance(setting,Mapping): inp["source_setting"]=deepcopy(setting)
            result=o099(inp)
            result.value["source_display_known"]=None
            result.state="hole" if result.state!="invalid" else result.state
            result.coverage_ok=None
            result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O099",["source_interpretation"])))
            return result
        if recipe_id=="O100":
            before,after=role["quote_before"],role["quote_after"]
            if (type(before.get("known_at")) is not int or type(after.get("known_at")) is not int or
                    before["known_at"]>=after["known_at"] or
                    _pv(before,"quote_id")==_pv(after,"quote_id")):
                raise LocalFlowDerivationError("BBO parents require distinct identities in causal order")
            quotes=[{**deepcopy(p.get("value",{})),"known_at":p.get("known_at"),"event_ns":p.get("known_at")} for p in (before,after)]
            events=[row for row in _parent_events(role["executions"])
                    if before["known_at"]<=row.get("event_ns",-1)<=after["known_at"]]
            return o100({"events":events,"quotes":quotes,
                         "band":deepcopy(config.get("selected_band")),"reset_at":config.get("reset_at"),
                         "execution_coverage_ok":role["executions"].get("recipe_coverage_ok"),"depth_coverage":"bbo"})
        if recipe_id=="O101":
            response=role["response"]; start=_parent_price(response); end=_parent_price(response,last=True)
            return o101({"events":_parent_events(role["executions"]),"response_start_price":start,
                         "response_end_price":end,"direction":_pv(response,"direction","side"),
                         "band":deepcopy(config.get("selected_band")),"tick_size":_pv(response,"tick_size"),
                         "passive_defense":None,"source_absorption":None})
        if recipe_id=="O102":
            before,after=role["quote_before"],role["quote_after"]
            if (type(before.get("known_at")) is not int or type(after.get("known_at")) is not int or
                    before["known_at"]>=after["known_at"] or
                    _pv(before,"quote_id")==_pv(after,"quote_id")):
                raise LocalFlowDerivationError("BBO parents require distinct identities in causal order")
            bv,av=before.get("value",{}),after.get("value",{})
            side=config.get("comparison_side"); key="bid" if side=="bid" else "ask" if side=="ask" else None
            if side not in {"bid","ask"}: key=None
            price=bv.get(key) if key else None; size_key=f"{key}_size" if key else None
            changes=[]
            if key and price==av.get(key) and bv.get(size_key) is not None and av.get(size_key) is not None:
                change=dec(av[size_key])-dec(bv[size_key])
                if change>0: changes=[{"event_id":after["object_id"],"event_ns":after.get("known_at"),"known_at":after.get("known_at"),"price":price,"change":change}]
            expected_side="A" if side=="bid" else "B" if side=="ask" else None
            consumed=[row for row in _parent_events(role["executions"])
                      if price is not None and row.get("price")==price and row.get("side") in {expected_side,"N"} and
                      before["known_at"]<=row.get("event_ns",-1)<=after["known_at"]]
            result=o102({"price":price,"passive_side":side,"consumption_events":consumed,
                         "refresh_events":changes,"first_display":bv.get(size_key) if size_key else None,
                         "last_display":av.get(size_key) if size_key else None,"hold":None})
            if key is None:
                result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O102",["comparison_side"])))
                result.state="hole";result.coverage_ok=None
            if any(row.get("side")=="N" for row in consumed):
                result.value["bbo_reload_inference"]=None;result.value["verified_replenishment"]=None
                result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O102",["aggressor_side"])))
                result.state="hole";result.coverage_ok=None
            return result
        if recipe_id=="O103":
            quote=role["quote"].get("value",{}); side=config.get("comparison_side")
            price=quote.get("bid" if side=="bid" else "ask" if side=="ask" else "")
            displayed=quote.get("bid_size" if side=="bid" else "ask_size" if side=="ask" else "")
            events=[row for row in _parent_events(role["executions"]) if row.get("price")==price]
            result=o103({"area":price,"area_ticks":Decimal(1) if side in {"bid","ask"} else None,"tick_size":_pv(role["tick"],"tick_size"),
                         "executed_total":sum((dec(row["size"]) for row in events),Decimal(0)),
                         "displayed":displayed,"participant_events":[],"depth_coverage":"bbo"})
            if side not in {"bid","ask"}:
                result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O103",["comparison_side"])))
                result.state="hole";result.coverage_ok=None
            return result
        if recipe_id=="O104":
            origin,reward,tick=role["origin"],role["reward"],role["tick"]
            return o104({"origin":_parent_price(origin),"origin_band":_pv(origin,"band","zone","origin_band"),
                         "selected_edge":config.get("selected_edge"),"direction":_pv(origin,"direction","side","control_side"),
                         "reward_price":_parent_price(reward,last=True),"reward_at":reward.get("known_at"),
                         "tick_size":_pv(tick,"tick_size")})
        if recipe_id=="O106":
            candle,foot=role["candle"],role["footprint"]; cv,fv=candle["value"],foot["value"]
            if cv.get("bar_id")!=fv.get("candle_id"): raise LocalFlowDerivationError("candle and footprint identities differ")
            change=None if cv.get("O") is None or cv.get("C") is None else dec(cv["C"])-dec(cv["O"])
            delta=dec(fv.get("delta")); ps=None if change is None else 1 if change>0 else -1 if change<0 else 0
            ds=None if delta is None else 1 if delta>0 else -1 if delta<0 else 0
            holes=[] if delta is not None else ["aggressor_side"]
            return _result("O106","hole" if holes else "computed",{"candle_id":cv.get("bar_id"),"price_change":change,
                "price_sign":ps,"delta":delta,"delta_sign":ds,"delta_bounds":deepcopy(fv.get("delta_interval")),
                "opposed_signs":None if ps is None or ds is None else ps*ds==-1,"event_ids":deepcopy(fv.get("event_ids") or [])},
                hole_ids=_holes("O106",holes),known_at=max(candle.get("known_at"),foot.get("known_at")),coverage_ok=None if holes else True)
        if recipe_id=="O107":
            foot=role["footprint"]; fv=foot["value"]; selected=config.get("selected_band")
            rows=fv.get("rows",[])
            if selected is not None:
                lo,hi=map(dec,selected); rows=[row for row in rows if lo<=dec(row["price"])<=hi]
            buy=sum((dec(r["buy_volume"]) for r in rows),Decimal(0)); sell=sum((dec(r["sell_volume"]) for r in rows),Decimal(0)); unknown=sum((dec(r["unknown_volume"]) for r in rows),Decimal(0))
            return o107({"B":buy,"A":sell,"N":unknown,"band":selected,"extreme":config.get("selected_extreme"),
                         "known_at":foot.get("known_at"),"source_spike":None})
        if recipe_id=="O108":
            snapshots=[]
            times=[parent.get("known_at") for parent in role["snapshots"]]
            if any(type(at) is not int for at in times) or len(times)!=len(set(times)):
                raise LocalFlowDerivationError("footprint snapshots require distinct causal availability keys")
            for parent in role["snapshots"]:
                value=parent["value"]
                snapshots.append({"snapshot_id":parent["object_id"],"candle_id":value.get("candle_id"),
                                  "candle_definition":deepcopy(value.get("candle_definition")),
                                  "poc":value.get("poc"),"rows":deepcopy(value.get("rows",[])),"known_at":parent.get("known_at")})
            return o108({"snapshots":snapshots,"use_at":config.get("use_at")})
        if recipe_id=="O109":
            foot=role["footprint"]; fv=foot["value"]
            return o109({"footprint_rows":deepcopy(fv.get("rows",[])),"tick_size":fv.get("tick_size"),
                         "candle_id":fv.get("candle_id"),"ratio_min":config.get("ratio_min"),
                         "row_count":config.get("row_count"),"zero_rule":config.get("zero_rule"),"known_at":foot.get("known_at")})
        if recipe_id=="O110":
            foot=role["footprint"]; rows=foot["value"].get("rows",[]); price=dec(config.get("comparison_price"))
            matches=[row for row in rows if dec(row.get("price"))==price]
            if len(matches)!=1: raise LocalFlowDerivationError("comparison_price must select exactly one actual footprint row")
            row=matches[0]
            return o110({"price":price,"buy_volume":row.get("buy_volume"),"sell_volume":row.get("sell_volume"),
                         "rule":config.get("rule"),"zero_rule":config.get("zero_rule"),"known_at":foot.get("known_at")})
        if recipe_id=="O114":
            tape=role["tape"]
            events=_parent_events(tape)
            events.sort(key=lambda row:(row.get("event_ns"),row.get("exchange_sequence") or 0))
            result=o114({"events":events,"groups":deepcopy(config.get("comparison_groups")),
                          "window_start":config.get("window_start"),"window_end":config.get("window_end"),"known_at":tape.get("known_at")})
            result.value["source_classification"]=None
            if _pv(tape,"ordering_quality")=="timestamp_ties_unordered":
                result.value["declining"]=None
                result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O114",["event_order"])))
            result.state="hole" if result.state!="invalid" else result.state
            result.coverage_ok=None
            result.hole_ids=list(dict.fromkeys(result.hole_ids+_holes("O114",["source_interpretation"])))
            return result
        return _derive_source_composite(recipe_id,config,role)
    except (ArithmeticError,KeyError,LocalFlowDerivationError,TypeError,ValueError) as exc:
        return _result(recipe_id,"invalid",{},base_ok=False,coverage_ok=None,
                       hole_ids=_holes(recipe_id,["parents"]),reason=str(exc))


NATIVE_PRODUCERS = {"O098":native_o098,"O105":native_o105,"O111":native_o111,"O112":native_o112,"O113":native_o113,"O120":native_o120}
DERIVED_PRODUCERS = {recipe_id:(lambda config,parents,recipe_id=recipe_id:
    _derived_local_flow(recipe_id,config,parents)) for recipe_id in DERIVED_PARENT_ROLES}
REGISTRATION_OVERRIDES = {rid:globals()[rid.lower()] for rid in LOCAL_FLOW_SCHEMAS}


def _type_for(name: str) -> OutputField:
    if name in {"event_records","delta_interval","delta_bounds","fraction_interval","marker_events","local_quote_snapshots","local_executions","display_changes","consumption_events","refresh_events","observed_same_price_size_changes","participant_events","snapshot_ids","buy_comparisons","sell_comparisons","buy_runs","sell_runs","ratios","event_ids","path_event_ids","sizes","digit_counts","formation_event_ids","touch_ids","eligible_history_ids","unresolved_history_ids","prior_failure_ids","rows","poc_candidates","marker_event_ids","body_prices","missing_stages","defender_aggression_events"}: return OutputField((list,))
    if name in {"band","area","origin_band","stack_band","zone","stage_ledger","groups","origin","current_stage_ledger","display_config","candle_definition","buy_by_price","sell_by_price","unknown_by_price","total_by_price"}: return OutputField((list,dict,Decimal),True)
    if name in {"markers","participant_count","snapshot_count","row_count","print_count","failed_push_count","later_touches","prior_touch_count","resolved_defense_count","prior_resolved_defense_count","distinct_failures","price_sign","delta_sign"}: return OutputField((int,),True)
    if name in {"source_display_known","same_as_other_mode","consumption_evidence","execution_evidence","consumed_and_replenished","verified_hidden_reserve","passive_defense","source_absorption","absorption","later_decline_repairs","bbo_reload_inference","verified_replenishment","hold","replenishment_hypothesis","directional_reward","retest_is_reward","opposed_signs","same_candle","consecutive","qualifies","automatic_settings","source_350_flag","meets_of","meets_more","automatic_speed","locked","crossed","stale","aggressive_arrival","post_touch_included","declining","source_classification","geometry_ok","order_ok","automatic_zone","later_high_replaces_origin","memory_causal","current_counts_as_prior","linked","branch_ok","historical_failures_known","current_evidence_complete","body_selling","later_price_in_earlier_asof","zone_definition_recorded","zone_frozen","instrument_and_threshold_preserved","departure_observed","distinct_touch_id","memory_uses_only_prior_resolved_touches","two_distinct_prior_failures"}: return OutputField((bool,),True)
    if name in {"formation_start","formation_end","as_of","reward_at","return_at","renewed_defense_at","reset_at","flip_at","window_start","window_end","from_at","to_at","touch_at","zone_known_at","departure_at","max_feature_known_at","prior_failures_known_at"}: return OutputField((int,),True)
    if name in {"candle_id","instrument_id","aggressor_convention","ordering_quality","comparator","aggregation_mode","mode","source_setting_id","defense_interpretation","depth_coverage","branch_id","passive_side","direction","reset_id","reference_unit","directional_relation","extreme","zero_rule","buy_relation","sell_relation","rule","quote_id","zone_id","origin_id","side","control_side","poc_tie_state"}: return OutputField((str,int),True)
    return OutputField((Decimal,),True)


OUTPUT_SCHEMAS = {
    rid: {name: OutputField(_type_for(name).types, nullable=True) for name in names}
    for rid, names in LOCAL_FLOW_SCHEMAS.items()
}

__all__=["DERIVED_PARENT_ROLES","DERIVED_PRODUCERS","LOCAL_FLOW_SCHEMAS","NATIVE_PRODUCERS",
         "OUTPUT_SCHEMAS","REGISTRATION_OVERRIDES","SOURCE_BIG_TRADE_SETTINGS"]
