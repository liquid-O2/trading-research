#!/usr/bin/env python3
"""Replay AUTHOR_EXAMPLES_2026-09-15.json through each family's B0.2 scan."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import argparse
import json
import sys

ROOT = Path("/workspace")
SRC = ROOT / "implementation/src"
sys.path.insert(0, str(SRC))

from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.rule_discovery.baseline import PHASE1_RUN
from trading_research.research.rule_discovery.native import CacheWriteBlocked, install_write_guard
from trading_research.research.rule_discovery.run_baseline_repair import evaluation_dates
from trading_research.research.rule_discovery.source_adapters import (
    green_failure,
    green_vwap_scalp,
    jumbo,
    keani,
    member,
    processes,
    saint,
    sires,
)

EXAMPLES_PATH = ROOT / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json"
SCHEMA = "author-example-replay-v1"

ADAPTERS = {
    "JJ-TBR": jumbo,
    "GB-FAIL": green_failure,
    "GB-VWAP": green_vwap_scalp,
    "GB-SCALP": green_vwap_scalp,
    "SIRES": sires,
    "SAINT-AMT": saint,
    "MEMBER-TWO-REASONS": member,
    "KEANI-OPEN-ABOVE-VALUE": keani,
    "REFILL-STUDY": processes,
}


def _family_key(raw: str | None) -> str:
    text = str(raw or "")
    if "GB-SCALP" in text and "GB-FAIL" in text:
        return "GB-FAIL"
    if "GB-SCALP" in text:
        return "GB-SCALP"
    if "GB-VWAP" in text:
        return "GB-VWAP"
    if "GB-FAIL" in text:
        return "GB-FAIL"
    return text


def _is_es(example: dict) -> bool:
    instrument = str(example.get("instrument") or "").upper()
    return instrument.startswith("ES")


def _as_date(text) -> str | None:
    if not text:
        return None
    token = str(text)[:10]
    try:
        date.fromisoformat(token)
    except ValueError:
        return None
    return token


def _decimal(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _episode_level_and_side(episode: dict) -> tuple[object, object]:
    geo = episode.get("geometry") or {}
    values = episode.get("values") or {}
    ref = episode.get("reference") or {}
    side = episode.get("side") or values.get("side")
    for raw in (
        geo.get("reference_level"),
        geo.get("reference_px"),
        geo.get("entry"),
        values.get("entry"),
        values.get("reference_px"),
        ref.get("ticks"),
        ref.get("price"),
    ):
        if raw is None:
            continue
        return raw, side
    return None, side


def _fill_level(row: dict, replay: dict) -> dict:
    if row.get("our_level") is not None and row.get("our_side") is not None:
        return row
    episode = replay.get("episode") or replay.get("matched_episode") or {}
    level, side = _episode_level_and_side(episode) if episode else (None, None)
    if row.get("our_level") is None and level is not None:
        row["our_level"] = float(level) if not isinstance(level, str) else level
    if row.get("our_side") is None and side is not None:
        row["our_side"] = side
    return row


def _unavailable(example: dict, reason: str) -> dict:
    expected = example.get("expected_detection") or {}
    return {
        "id": example.get("id"),
        "source": example.get("source"),
        "date": example.get("date"),
        "family": example.get("family"),
        "branch": expected.get("branch"),
        "detected": None,
        "reached_location": None,
        "operands": None,
        "failing_operand": None,
        "failing_stage": None,
        "our_level": None,
        "our_side": None,
        "author_level": None,
        "author_side": expected.get("side"),
        "entry_time": None,
        "divergence": "data_unavailable",
        "reason": reason,
    }


def _replay_operands(replay: dict) -> object:
    if replay.get("operands") is not None:
        return replay.get("operands")
    fo = replay.get("failing_operand")
    if isinstance(fo, dict):
        return fo.get("operands") if fo.get("operands") is not None else fo
    episode = replay.get("episode") or replay.get("matched_episode") or {}
    for stage in episode.get("stages") or []:
        if stage.get("stage") == "location" and stage.get("operands") is not None:
            return stage.get("operands")
        if stage.get("verdict") in {"fail", "unknown"} and stage.get("operands") is not None:
            return stage.get("operands")
    return fo


def load_calendar() -> set[str]:
    registry, _coverage = hr.load_registry(PHASE1_RUN, check_software=False)
    return set(evaluation_dates(registry))


_MARKET_CACHE: dict[str, object] = {}


def load_market(day: str):
    cached = _MARKET_CACHE.get(day)
    if cached is not None:
        return cached
    install_write_guard()
    registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
    market = HistoricalFeatures(day, records=hr._records(registry))
    try:
        from trading_research.research.rule_discovery.native import build_market_view

        market._native_view = build_market_view(day, full_account_day=True)
    except CacheWriteBlocked:
        market._native_view = None
    except Exception:
        market._native_view = None
    _MARKET_CACHE[day] = market
    return market


def replay_one(example: dict, calendar: set[str]) -> dict:
    expected = example.get("expected_detection") or {}
    family = _family_key(example.get("family"))
    day = _as_date(example.get("date"))
    if _is_es(example):
        return _unavailable(example, "es_tape_absent")
    if example.get("inside_tape") is False:
        return _unavailable(example, "outside_tape")
    if day is None:
        return _unavailable(example, "date_unparseable")
    if day not in calendar:
        return _unavailable(example, f"date_outside_native_calendar:{day}")
    adapter = ADAPTERS.get(family)
    if adapter is None:
        return _unavailable(example, f"unknown_family:{family}")
    try:
        market = load_market(day)
    except CacheWriteBlocked:
        return _unavailable(example, "cache_write_blocked")
    except Exception as exc:
        return _unavailable(example, f"market_load:{type(exc).__name__}")
    replay = adapter.replay_example(market, example)
    row = {
        "id": example.get("id"),
        "source": example.get("source"),
        "date": day,
        "family": example.get("family"),
        "branch": replay.get("branch") or expected.get("branch"),
        "detected": replay.get("detected"),
        "reached_location": replay.get("reached_location"),
        "operands": _replay_operands(replay),
        "failing_operand": replay.get("failing_operand"),
        "failing_stage": replay.get("failing_stage"),
        "our_level": replay.get("our_level"),
        "our_side": replay.get("our_side"),
        "author_level": replay.get("author_level"),
        "author_side": replay.get("author_side") or expected.get("side"),
        "entry_time": replay.get("our_entry_ns"),
        "divergence": replay.get("divergence") or "",
        "reason": None,
    }
    return _fill_level(row, replay)


def render_md(payload: dict) -> str:
    lines = [
        "# Author example replay",
        "",
        f"- Examples: {payload['n']}",
        f"- Detected: {payload['detected_yes']}",
        f"- Miss: {payload['detected_no']}",
        f"- data_unavailable: {payload['data_unavailable']}",
        "",
        "| id | source | date | family | branch | detected | our_level | our_side | author_level | author_side | entry_time | divergence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["examples"]:
        lines.append(
            f"| `{row.get('id')}` | {row.get('source')} | {row.get('date')} | {row.get('family')} | "
            f"{row.get('branch')} | {row.get('detected')} | {row.get('our_level')} | {row.get('our_side')} | "
            f"{row.get('author_level')} | {row.get('author_side')} | {row.get('entry_time')} | {row.get('divergence')} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", type=Path, default=EXAMPLES_PATH)
    parser.add_argument("--index", type=Path, default=None, help="unused; examples JSON is canonical")
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args(argv)
    install_write_guard()
    calendar = load_calendar()
    document = json.loads(args.examples.read_text())
    rows = []
    for example in document.get("examples") or []:
        rows.append(replay_one(example, calendar))
    detected_yes = sum(1 for row in rows if row.get("detected") is True)
    detected_no = sum(1 for row in rows if row.get("detected") is False)
    unavailable = sum(1 for row in rows if row.get("detected") is None)
    payload = {
        "schema": SCHEMA,
        "examples_path": str(args.examples),
        "n": len(rows),
        "detected_yes": detected_yes,
        "detected_no": detected_no,
        "data_unavailable": unavailable,
        "calendar_n": len(calendar),
        "examples": rows,
    }
    args.run_root.mkdir(parents=True, exist_ok=True)
    json_path = args.run_root / "AUTHOR_EXAMPLE_REPLAY.json"
    md_path = args.run_root / "AUTHOR_EXAMPLE_REPLAY.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    md_path.write_text(render_md(payload))
    print(json.dumps({"event": "replay_complete", "n": len(rows), "path": str(json_path)}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
