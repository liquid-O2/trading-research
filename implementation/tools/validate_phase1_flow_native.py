#!/usr/bin/env python3
"""Validate Phase 1 flow objects against three bounded native NQ windows.

The readable JSON is a chart-ready summary.  Its gzip companion preserves the
complete producer payloads, immutable row locators, and coverage reconciliation.
Decimal measurements are encoded as exact strings in both artifacts.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict, is_dataclass
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementation/src"))

from trading_research.research.method_pack.native_windows import collect_window
from trading_research.research.method_pack.objects import native_boundary


TRADES = "quantpad/cme__nq-continuous-futures__trades"
OHLC = "quantpad/cme__nq-continuous-futures__ohlcv-1m"
MBP1 = "quantpad/cme__nq-continuous-futures__mbp-1"
MINUTE = 60_000_000_000
WINDOWS = (
    ("2026-02-24", 42002475, 1771943400000000000, 1771943700000000000),
    ("2026-06-12", 42004058, 1781271000000000000, 1781271300000000000),
    ("2026-07-23", 42004177, 1784813400000000000, 1784813700000000000),
)


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, MappingProxyType):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(type(value).__name__)


def _bytes(value: Any, *, pretty: bool) -> bytes:
    options = {"default": _json_default, "sort_keys": True, "ensure_ascii": False}
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return (json.dumps(value, **options) + "\n").encode()


def _write_gzip(path: Path, payload: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            zipped.write(payload)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _result_record(object_id: str, result, window, config: Mapping[str, Any], *,
                   locators=None, parent_ids=(), formation_end=None):
    return {
        "object_id": object_id,
        "recipe_id": result.recipe_id,
        "instrument_id": window.instrument_id,
        "formation_start": window.start_ns,
        "formation_end": window.end_ns if formation_end is None else formation_end,
        "known_at": result.known_at,
        "native_window_coverage_ok": window.coverage_ok,
        "raw_member_locators": [dict(row) for row in (window.locators if locators is None else locators)],
        "inputs": dict(config),
        "result": asdict(result),
    }


def _parent_record(object_id: str, instrument_id: Any, result) -> dict[str, Any]:
    return {"object_id": object_id, "recipe_id": result.recipe_id, "state": result.state,
            "instrument_id": instrument_id, "known_at": result.known_at,
            "value": result.value, "recipe_base_ok": result.base_ok,
            "recipe_coverage_ok": result.coverage_ok, "hole_ids": list(result.hole_ids),
            "evidence_class": result.evidence_class}


def _native_obj(recipe_id: str, window, inputs: Mapping[str, Any], *, object_id: str,
                parent_ids=(), formation_end=None):
    return {"object_id": object_id, "recipe_id": recipe_id, "instrument_id": window.instrument_id,
            "formation_start": window.start_ns,
            "formation_end": window.end_ns if formation_end is None else formation_end,
            "as_of": window.end_ns if formation_end is None else formation_end,
            "known_at": window.end_ns if formation_end is None else formation_end,
            "raw_member_locators": [dict(row) for row in window.locators],
            "parent_ids": list(parent_ids), "inputs": dict(inputs)}


def _minute_flow(rows, start: int, end: int):
    buckets = defaultdict(lambda: [Decimal(0), Decimal(0), Decimal(0), 0])
    for row in rows:
        if row.get("action") != "T":
            continue
        at = row["event_ns"]
        if not start <= at < end:
            continue
        minute = (at // MINUTE) * MINUTE
        side = row.get("aggressor")
        slot = 0 if side == "buy" else 1 if side == "sell" else 2
        buckets[minute][slot] += Decimal(row["size"])
        buckets[minute][3] += 1
    cumulative = Decimal(0)
    result = []
    for minute in range(start, end, MINUTE):
        buy, sell, unknown, count = buckets[minute]
        known_delta = buy - sell
        cumulative += known_delta
        result.append({"start_ns": minute, "end_ns": minute + MINUTE, "buy": buy,
                       "sell": sell, "unknown": unknown, "known_delta": known_delta,
                       "cumulative_known_delta": cumulative, "trade_count": count})
    return result


def _produce_day(data_root: Path, spec):
    day, instrument, start, end = spec
    print(f"{day}: collecting trades", flush=True)
    trades = collect_window(data_root, TRADES, start, end, instrument, required="trades")
    print(f"{day}: collecting OHLCV", flush=True)
    ohlc = collect_window(data_root, OHLC, start, end, instrument, required="ohlcv")
    print(f"{day}: collecting MBP-1", flush=True)
    mbp = collect_window(data_root, MBP1, start, end, instrument, required="trades")
    for name, window in (("trades", trades), ("ohlcv", ohlc), ("mbp1", mbp)):
        if window.resolved is None or window.coverage_ok is not True:
            raise RuntimeError(f"{day}: {name} native window is unresolved or incomplete")

    tick = trades.instrument_definition.tick_size
    candle_id = f"{instrument}:{start}:{end}"
    bar_config = {"kind": "time", "size_minutes": 5, "bar_id": candle_id, "use_at": end}
    bar_obj=_native_obj("O004",ohlc,bar_config,object_id=f"{day}:O004")
    bar=native_boundary.run_native_object(bar_obj,ohlc.resolver)
    if bar.state != "computed" or bar.value["complete"] is not True:
        raise RuntimeError(f"{day}: native five-minute candle did not complete")
    bar_parent=_parent_record(f"{day}:O004",instrument,bar)

    configs = {
        "O098": {"as_of": end},
        "O105": {"reset_policy":{"policy_id":f"{day}:window-open-comparison",
                  "start_ns":start,"kind":"declared_comparison"},"as_of":end},
        "O111": {"window_start": start, "window_end": end},
        "O112": {"as_of": end},
        "O113": {"touch_at": end},
        "O120": {"as_of": end, "poc_tie_policy": "lowest"},
        "O163": {},
        "O164": {"side": "long", "effort_side": "total", "response_basis": "trade_price",
                  "use_at": end},
    }
    objects = [_result_record(f"{day}:O004", bar, ohlc, bar_config)]
    produced = {"O004": bar}
    parents_by_recipe={"O120":[bar_parent]}
    for recipe_id in ("O098", "O105", "O111", "O113", "O120"):
        actual_parents=parents_by_recipe.get(recipe_id,[])
        obj=_native_obj(recipe_id,trades,configs[recipe_id],object_id=f"{day}:{recipe_id}",
                        parent_ids=[p["object_id"] for p in actual_parents])
        result=native_boundary.run_native_object(obj,trades.resolver,parents=actual_parents)
        produced[recipe_id] = result
        objects.append(_result_record(f"{day}:{recipe_id}",result,trades,configs[recipe_id],
                                      parent_ids=[p["object_id"] for p in actual_parents]))
    quote_obj=_native_obj("O112",mbp,configs["O112"],object_id=f"{day}:O112")
    quote=native_boundary.run_native_object(quote_obj,mbp.resolver)
    produced["O112"] = quote
    objects.append(_result_record(f"{day}:O112", quote, mbp, configs["O112"]))
    for recipe_id in ("O163","O164"):
        process_obj=_native_obj(recipe_id,trades,configs[recipe_id],object_id=f"{day}:{recipe_id}")
        process=native_boundary.run_native_object(process_obj,trades.resolver)
        produced[recipe_id]=process
        objects.append(_result_record(f"{day}:{recipe_id}",process,trades,configs[recipe_id]))

    # A two-minute snapshot uses only native members known by that clock.  It
    # keeps the completed five-minute candle identity so O108 can test a true
    # developing-versus-close POC change within one candle.
    snapshot_end = start + 2 * MINUTE
    early_trades = collect_window(data_root, TRADES, start, snapshot_end, instrument, required="trades")
    early_ohlc = collect_window(data_root, OHLC, start, snapshot_end, instrument, required="ohlcv")
    early_bar_config = {"kind": "time", "size_minutes": 2, "use_at": snapshot_end}
    early_bar_obj=_native_obj("O004",early_ohlc,early_bar_config,object_id=f"{day}:O004:developing-2m")
    early_bar=native_boundary.run_native_object(early_bar_obj,early_ohlc.resolver)
    early_parent=_parent_record(f"{day}:O004:developing-2m",instrument,early_bar)
    early_config={"as_of":snapshot_end,"poc_tie_policy":"lowest",
                  "candle_selection":{"candle_id":candle_id,"start_ns":start,"end_ns":end,"defined_at":start}}
    early_obj=_native_obj("O120",early_trades,early_config,object_id=f"{day}:O120:developing-2m",
                          parent_ids=[early_parent["object_id"]])
    early_footprint=native_boundary.run_native_object(early_obj,early_trades.resolver,parents=[early_parent])
    objects.append(_result_record(f"{day}:O120:developing-2m", early_footprint, trades, early_config,
                                  parent_ids=(f"{day}:O004:developing-2m",), formation_end=snapshot_end))
    footprint_parents=[_parent_record(f"{day}:O120:developing-2m",instrument,early_footprint),
                       _parent_record(f"{day}:O120",instrument,produced["O120"])]
    poc_obj={"object_id":f"{day}:O108:same-candle","recipe_id":"O108","instrument_id":instrument,
             "formation_start":start,"formation_end":end,"as_of":end,"known_at":end,
             "raw_member_locators":[],"parent_ids":[p["object_id"] for p in footprint_parents],
             "inputs":{"use_at":end,"parent_roles":{"snapshots":[p["object_id"] for p in footprint_parents]}}}
    poc_change=native_boundary.run_native_object(poc_obj,None,parents=footprint_parents)
    objects.append({"object_id": f"{day}:O108:same-candle", "recipe_id": "O108",
                    "instrument_id": instrument, "formation_start": start,
                    "formation_end": end, "known_at": poc_change.known_at,
                    "native_window_coverage_ok": trades.coverage_ok,
                    "raw_member_locators": [dict(row) for row in trades.locators],
                    "inputs": poc_obj["inputs"],
                    "result": asdict(poc_change)})

    tape_parent=_parent_record(f"{day}:O098",instrument,produced["O098"])
    closed_footprint=footprint_parents[-1]
    derived_specs=(
        ("O099",[tape_parent],{"comparison_policy":{"setting_id":f"{day}:100-contract-comparison",
            "threshold":100,"comparator":">=","aggregation_mode":"per_print"},
            "parent_roles":{"tape":tape_parent["object_id"]}}),
        ("O106",[bar_parent,closed_footprint],{"parent_roles":{"candle":bar_parent["object_id"],
            "footprint":closed_footprint["object_id"]}}),
        ("O107",[closed_footprint],{"selected_band":[bar.value["L"],bar.value["H"]],
            "selected_extreme":"complete_candle_range_comparison",
            "parent_roles":{"footprint":closed_footprint["object_id"]}}),
        ("O109",[closed_footprint],{"ratio_min":4,"row_count":3,"zero_rule":"does_not_qualify",
            "parent_roles":{"footprint":closed_footprint["object_id"]}}),
        ("O110",[closed_footprint],{"comparison_price":produced["O120"].value["poc"],
            "rule":"350_of","zero_rule":"does_not_qualify",
            "parent_roles":{"footprint":closed_footprint["object_id"]}}),
        ("O114",[tape_parent],{"comparison_groups":{"basis":"decimal_digit_count"},
            "window_start":start,"window_end":end,"parent_roles":{"tape":tape_parent["object_id"]}}),
    )
    for recipe_id,actual_parents,inputs in derived_specs:
        obj={"object_id":f"{day}:{recipe_id}:derived","recipe_id":recipe_id,"instrument_id":instrument,
             "formation_start":start,"formation_end":end,"as_of":end,"known_at":end,
             "raw_member_locators":[],"parent_ids":[p["object_id"] for p in actual_parents],"inputs":inputs}
        result=native_boundary.run_native_object(obj,None,parents=actual_parents)
        produced[f"{recipe_id}:derived"]=result
        objects.append(_result_record(obj["object_id"],result,trades,inputs,locators=[],
                                      parent_ids=obj["parent_ids"]))

    chart = {
        "ohlcv_1m": [{key: row[key] for key in ("start", "end", "O", "H", "L", "C", "V")}
                     for row in ohlc.rows],
        "flow_1m": _minute_flow(trades.rows, start, end),
        "footprint_close": produced["O120"].value["rows"],
        "bbo_at_window_end": {key: quote.value[key] for key in
                              ("quote_id", "bid", "ask", "bid_size", "ask_size", "spread_ticks")},
        "same_candle": {
            "candle_id": candle_id,
            "developing_2m": {"poc": early_footprint.value["poc"],
                              "delta": early_footprint.value["delta"],
                              "body_delta": early_footprint.value["body_delta"]},
            "complete_5m": {"poc": produced["O120"].value["poc"],
                            "delta": produced["O120"].value["delta"],
                            "body_delta": produced["O120"].value["body_delta"]},
            "poc_change": poc_change.value["change"],
        },
    }
    summary_objects = [{"object_id": row["object_id"], "recipe_id": row["recipe_id"],
                        "state": row["result"]["state"], "known_at": row["result"]["known_at"],
                        "coverage_ok": row["result"]["coverage_ok"],
                        "hole_ids": row["result"]["hole_ids"]} for row in objects]
    return {
        "date": day, "instrument_id": instrument, "tick_size": tick,
        "start_ns": start, "end_ns": end,
        "instrument_definition": trades.instrument_definition,
        "coverage": {"trades": dict(trades.coverage_evidence), "ohlcv": dict(ohlc.coverage_evidence),
                     "mbp1": dict(mbp.coverage_evidence)},
        "objects": objects, "summary_objects": summary_objects, "chart_data": chart,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=ROOT / "data")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "implementation/validation/phase1-completion/native-flow.json")
    args = parser.parse_args()
    days = [_produce_day(args.data_root.resolve(), spec) for spec in WINDOWS]
    full = {
        "schema": "phase1-native-flow-validation-v1",
        "scope": "Actual bounded NQ native observations; source-only interpretations remain explicit holes",
        "decimal_encoding": "exact decimal strings",
        "windows": days,
    }
    full_path = args.output.with_suffix(args.output.suffix + ".gz")
    full_sha = _write_gzip(full_path, _bytes(full, pretty=False))
    summary = {
        "schema": "phase1-native-flow-validation-summary-v1",
        "scope": full["scope"],
        "command": "PYTHONPATH=implementation/src python implementation/tools/validate_phase1_flow_native.py",
        "full_artifact": {"path": str(full_path.relative_to(ROOT)), "sha256": full_sha,
                          "encoding": "deterministic gzip JSON (mtime=0); exact Decimal strings"},
        "windows": [{key: day[key] for key in ("date", "instrument_id", "tick_size", "start_ns", "end_ns",
                                                   "summary_objects", "chart_data")} for day in days],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_bytes(summary, pretty=True))
    print(json.dumps({"status": "pass", "summary": str(args.output), "full": str(full_path),
                      "full_sha256": full_sha}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
