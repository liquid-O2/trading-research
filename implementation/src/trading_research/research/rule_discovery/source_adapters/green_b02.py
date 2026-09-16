"""Green Bird B0.2 scan. Family-owned; does not edit common.py or the runner."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping
import inspect

from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
from trading_research.research.method_pack.protocol import jsonable

B02_VERSION = "B0.2-2026-09-15"
TAPE_END = date(2026, 8, 19)
STAGE_ORDER = (
    "context",
    "reference",
    "location",
    "trigger",
    "confirmation",
    "risk",
    "objective",
    "management",
)
FIVE = 5 * MINUTE
LEVEL_TOLERANCE = Decimal("2.00")
LADDER_SPACING = Decimal("15")
RISK_DOLLARS = Decimal("750")
MNQ_POINT_VALUE = Decimal("2")
VWAP_STOP_POINTS = Decimal("30")
VWAP_TARGET_POINTS = Decimal("150")
VWAP_TARGET_POINTS_VARIANT_100 = Decimal("100")
AT_LEVEL_FAIL_BARS = 1
SWEEP_STOP_BUFFER = Decimal("11.75")
PREVIOUS_HOUR_SEARCH_MINUTES = 15
RETEST_TO_RTH = True
RETEST_60M_CANDIDATE = False
REC_IDENTITY_KEYS = frozenset(
    {"family", "method_id", "branch", "coverage_id", "registered_od", "parameters"}
)
AUTHOR_EXAMPLES_PATH = Path(
    "/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json"
)

B02_BRANCHES = {
    "GB-FAIL": (
        "london_box",
        "asia_box",
        "asia_tdo_case",
        "prior_day_level",
        "nyam_box",
        "previous_hour",
        "nwog",
        "cash_open_reclaim_case",
        "golden_pocket",
        "ny_session_extreme",
    ),
    "GB-VWAP": ("source_long",),
    "GB-SCALP": ("golden_pocket_continuation",),
}

SCALP_OBSERVATIONS = ("bearish_small_scalp", "bullish_discount_pullback")

ASIA_VARIANTS = {
    "20:00-21:00": {"start": "20:00", "end": "21:00", "start_off": -1, "end_off": -1},
    "20:00-23:00": {"start": "20:00", "end": "23:00", "start_off": -1, "end_off": -1},
    "20:00-00:00": {"start": "20:00", "end": "00:00", "start_off": -1, "end_off": 0},
}
LONDON_VARIANTS = {
    "03:00-04:30": {"start": "03:00", "end": "04:30", "start_off": 0, "end_off": 0},
    "02:00-05:00": {"start": "02:00", "end": "05:00", "start_off": 0, "end_off": 0},
}


def _d(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _dec(value: Any) -> Decimal:
    got = _d(value)
    if got is None:
        raise ValueError("missing decimal")
    return got


def asia_variant_for(day: date) -> str:
    """RR-11 baseline: Apr-Aug 20:00-23:00, September 20:00-00:00."""
    if day.month == 9:
        return "20:00-00:00"
    if 4 <= day.month <= 8:
        return "20:00-23:00"
    return "20:00-00:00"


def london_variant_for(day: date) -> str:
    """RR-11: 03:00-04:30 April and early August; 02:00-05:00 late August and September."""
    if day.month == 4 or (day.month == 8 and day.day < 20):
        return "03:00-04:30"
    return "02:00-05:00"


def asia_box_spec(day: date) -> dict[str, Any]:
    name = asia_variant_for(day)
    return {"name": name, **ASIA_VARIANTS[name]}


def london_box_spec(day: date) -> dict[str, Any]:
    name = london_variant_for(day)
    return {"name": name, **LONDON_VARIANTS[name]}


def pocket_in_leg_direction(low: Decimal, high: Decimal, impulse_side: str) -> tuple[Decimal, Decimal]:
    """F06/RR-14: up-leg [H-0.618W, H-0.50W]; down-leg [L+0.50W, L+0.618W]."""
    width = high - low
    if impulse_side in {"up", "long"}:
        lo, hi = high - Decimal("0.618") * width, high - Decimal("0.50") * width
    else:
        lo, hi = low + Decimal("0.50") * width, low + Decimal("0.618") * width
    return (min(lo, hi), max(lo, hi))


def near_edge(pocket: tuple[Decimal, Decimal], impulse_side: str) -> Decimal:
    lo, hi = pocket
    return hi if impulse_side in {"up", "long"} else lo


def far_edge(pocket: tuple[Decimal, Decimal], impulse_side: str) -> Decimal:
    lo, hi = pocket
    return lo if impulse_side in {"up", "long"} else hi


def limit_ladder(entry: Decimal, target: Decimal, side: str, spacing: Decimal = LADDER_SPACING) -> list[Decimal]:
    sg = Decimal(1) if side == "long" else Decimal(-1)
    rungs: list[Decimal] = []
    px = entry + sg * spacing
    while len(rungs) < 17 and sg * (target - px) >= 0:
        rungs.append(px)
        px = px + sg * spacing
    if not rungs or rungs[-1] != target:
        rungs.append(target)
    return rungs[:18]


def derived_quantity(stop_points: Decimal) -> Decimal | None:
    if stop_points is None or stop_points <= 0:
        return None
    return RISK_DOLLARS / (stop_points * MNQ_POINT_VALUE)


def session_label(market, ns: int) -> str:
    if market.at("20:00", -1) <= ns < market.at("00:00"):
        return "asia"
    if market.at("00:00") <= ns < market.at("03:00"):
        return "overnight"
    if market.at("03:00") <= ns < market.at("09:30"):
        return "london"
    if market.at("09:30") <= ns < market.at("12:00"):
        return "ny_am"
    if market.at("12:00") <= ns <= market.at("16:00"):
        return "ny_pm"
    return "other"


def in_entry_windows(market, ns: int) -> bool:
    windows = (
        (market.at("00:00"), market.at("02:00") + MINUTE),
        (market.at("03:00"), market.at("06:00") + MINUTE),
        (market.at("09:30"), market.at("11:30") + MINUTE),
        (market.at("12:45"), market.at("14:30") + MINUTE),
        (market.at("20:00", -1), market.at("23:00", -1) + MINUTE),
    )
    return any(start <= ns < end for start, end in windows)


def next_rth_open_ns(market, decision_ns: int) -> int:
    for offset in range(0, 6):
        stamp = market.at("09:30", offset)
        if stamp > decision_ns:
            return int(stamp)
    return int(decision_ns + 18 * 60 * MINUTE)


def _bar_complete(row: Mapping[str, Any] | None) -> bool:
    return bool(row) and bool(row.get("observed_complete")) and row.get("C") is not None


def _five_min_row(market, start: int) -> dict[str, Any] | None:
    rows300 = _safe_bars(market, start, start + FIVE, 300)
    row = rows300[0] if rows300 else None
    if _bar_complete(row):
        return row
    rows = _safe_bars(market, start, start + FIVE, 60)
    if not rows:
        return None
    closes = [r.get("C") for r in rows if r.get("C") is not None]
    highs = [r.get("H") for r in rows if r.get("H") is not None]
    lows = [r.get("L") for r in rows if r.get("L") is not None]
    if not closes or not highs or not lows:
        return None
    return {
        "start": start,
        "end": start + FIVE,
        "O": rows[0].get("O"),
        "H": max(highs),
        "L": min(lows),
        "C": closes[-1],
        "known_at": max(int(r.get("known_at") or start) for r in rows),
        "observed_complete": True,
        "bar_id": f"5m:{start}",
    }


def _safe_bars(market, start: int, end: int, seconds: int = 60) -> list[dict[str, Any]]:
    if start is None or end is None or end <= start:
        return []
    lo = max(int(start), int(market.start))
    hi = min(int(end), int(market.end))
    if hi <= lo:
        return []
    try:
        return list(market.bars(lo, hi, seconds) or [])
    except Exception:
        return []


def _range(market, start: int, end: int, label: str) -> dict[str, Any] | None:
    if end <= start:
        return None
    try:
        ref = market.range(start, end, label)
    except Exception:
        return None
    if ref is None:
        return None
    if ref.get("low") is None or ref.get("high") is None:
        return None
    return ref


def _tdo(market) -> Decimal | None:
    rows = _safe_bars(market, market.at("00:00"), market.at("00:00") + MINUTE)
    if not rows:
        return None
    return _d(rows[0].get("O"))


def _prior_day_range(market) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    fixture = getattr(market, "b02_prior_day", None)
    if fixture is not None:
        return fixture, []
    try:
        prior = market.prior("day")
    except Exception as exc:
        return None, [{"reason": "prior_day_unavailable", "detail": str(exc)}]
    if not prior:
        return None, [{"reason": "prior_day_unavailable"}]
    return prior.get("range"), list(prior.get("omissions") or [])


def _prior_value(market) -> dict[str, Any] | None:
    fixture = getattr(market, "b02_prior_value", None)
    if fixture is not None:
        return fixture
    ref, _omissions = _prior_day_range(market)
    if ref is None or ref.get("low") is None or ref.get("high") is None:
        return None
    mid = (_dec(ref["low"]) + _dec(ref["high"])) / Decimal("2")
    close = _d(ref.get("close"))
    return {"mid": mid, "close": close, "low": _dec(ref["low"]), "high": _dec(ref["high"])}


def _nwog_levels(market) -> dict[str, Any] | None:
    fixture = getattr(market, "b02_nwog", None)
    if fixture is not None:
        return fixture
    sunday_open_ns = market.at("18:00", -1)
    if market.day.weekday() != 0:
        sunday = market.day - timedelta(days=market.day.weekday() + 1)
        sunday_open_ns = market.at("18:00") - int((market.day - sunday).days * 24 * 60 * MINUTE)
        sunday_open_ns = int(sunday_open_ns)
    rows = _safe_bars(market, int(market.start), int(market.start) + MINUTE)
    sunday_open = _d(rows[0].get("O")) if rows else None
    prior, _ = _prior_day_range(market)
    friday_close = None if prior is None else _d(prior.get("close"))
    if sunday_open is None or friday_close is None:
        return None
    lo, hi = sorted((friday_close, sunday_open))
    return {
        "low": lo,
        "high": hi,
        "friday_close": friday_close,
        "sunday_open": sunday_open,
        "known_at": int(market.start),
        "id": f"nwog:{market.instrument_id}:{market.day}",
    }


def directional_bias(market, at_ns: int) -> dict[str, Any]:
    """F07 OD: prior close vs its range midpoint; 09:00-10:00 box direction after 10:00 only."""
    prior = _prior_value(market)
    prior_side = None
    if prior and prior.get("close") is not None:
        if prior["close"] > prior["mid"]:
            prior_side = "long"
        elif prior["close"] < prior["mid"]:
            prior_side = "short"
    box_side = None
    box_known = market.at("10:00")
    if at_ns >= box_known:
        box = _range(market, market.at("09:00"), market.at("10:00"), "nyam-box-bias")
        if box is not None and box.get("open") is not None and box.get("close") is not None:
            if _dec(box["close"]) > _dec(box["open"]):
                box_side = "long"
            elif _dec(box["close"]) < _dec(box["open"]):
                box_side = "short"
    sides = [item for item in (prior_side, box_side) if item is not None]
    if not sides:
        compatible = None
        direction = None
    elif len(set(sides)) == 1:
        direction = sides[0]
        compatible = True
    else:
        direction = None
        compatible = False
    return {
        "prior_side": prior_side,
        "box_side": box_side,
        "direction": direction,
        "inputs_agree": compatible,
        "rule_id": "F07-directional-bias",
    }


def bias_compatible(bias: Mapping[str, Any], side: str) -> bool | None:
    direction = bias.get("direction")
    if direction is None:
        if bias.get("inputs_agree") is False:
            return False
        return None
    return direction == side


def first_sweep(market, begin: int, end: int, level: Decimal, side: str) -> dict[str, Any] | None:
    rows = _safe_bars(market, begin, end)
    for row in rows:
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if side == "short" and hi is not None and hi > level:
            return row
        if side == "long" and lo is not None and lo < level:
            return row
    return None


def first_five_minute_close_through(
    market, after_ns: int, level: Decimal, side: str, *, limit_ns: int
) -> dict[str, Any] | None:
    aligned = int(after_ns) // FIVE * FIVE
    t = aligned
    while t + FIVE <= int(market.end) and t < int(limit_ns):
        if t < int(market.start):
            t += FIVE
            continue
        row = _five_min_row(market, t)
        if not _bar_complete(row):
            t += FIVE
            continue
        known = int(row.get("known_at") or (t + FIVE))
        if known > int(limit_ns):
            break
        close = _dec(row["C"])
        through = close > level if side == "long" else close < level
        if through:
            return {"bar": row, "at_ns": int(t + FIVE), "close": close, "known_at": known}
        t += FIVE
    return None


def _through_level(close: Decimal | None, level: Decimal, side: str) -> bool:
    if close is None:
        return False
    return close <= level if side == "short" else close >= level


def _inside_box(close: Decimal | None, box_low: Decimal | None, box_high: Decimal | None) -> bool | None:
    if close is None or box_low is None or box_high is None:
        return None
    if box_low == box_high:
        return True
    return box_low <= close <= box_high


def sweep_and_at_level(
    market,
    begin: int,
    end: int,
    level: Decimal,
    side: str,
    *,
    box_low: Decimal | None = None,
    box_high: Decimal | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Sweep beyond the edge, then fail back through it inside the fail window.

    RR-13 at-level: enter as soon as the sweep fails (GB pp.43, 58; 2026-08-31
    two minutes after the spike). A same-bar wick is not the failure. A later
    touch after price continued is not confirmation. Window is the sweep's
    5-minute clock bar (AT_LEVEL_FAIL_BARS=1). The next 1-minute bar must stay
    inside (failure to continue).
    """
    rows = _safe_bars(market, begin, end)
    sweep = None
    for row in rows:
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if lo is None or hi is None:
            continue
        swept = (side == "short" and hi > level) or (side == "long" and lo < level)
        if not swept:
            continue
        sweep = row
        break
    if sweep is None:
        return None, None
    sweep_at = int(sweep.get("start") or begin)
    sweep_end = int(sweep.get("end") or (sweep_at + MINUTE))
    aligned = sweep_at // FIVE * FIVE
    window_end = min(int(end), aligned + AT_LEVEL_FAIL_BARS * FIVE)
    extreme = _d(sweep.get("H")) if side == "short" else _d(sweep.get("L"))
    confirm = None
    for row in _safe_bars(market, sweep_end, window_end):
        lo, hi, close = _d(row.get("L")), _d(row.get("H")), _d(row.get("C"))
        if side == "short" and hi is not None and extreme is not None and hi > extreme:
            break
        if side == "long" and lo is not None and extreme is not None and lo < extreme:
            break
        if not _through_level(close, level, side):
            continue
        inside = _inside_box(close, box_low, box_high)
        if inside is False:
            continue
        hold_start = int(row.get("end") or (int(row.get("start") or sweep_end) + MINUTE))
        hold_rows = _safe_bars(market, hold_start, hold_start + MINUTE)
        if not hold_rows:
            continue
        hold = hold_rows[0]
        hold_hi, hold_lo, hold_close = _d(hold.get("H")), _d(hold.get("L")), _d(hold.get("C"))
        if side == "short" and hold_hi is not None and extreme is not None and hold_hi > extreme:
            continue
        if side == "long" and hold_lo is not None and extreme is not None and hold_lo < extreme:
            continue
        if not _through_level(hold_close, level, side):
            continue
        known = int(hold.get("known_at") or hold.get("end") or hold_start)
        depth = None if extreme is None else (extreme - level if side == "short" else level - extreme)
        confirm = {
            "bar": hold,
            "at_ns": known,
            "level": level,
            "close": close,
            "inside_box": True if inside is None else inside,
            "sweep_extreme": extreme,
            "sweep_depth": depth,
            "fail_window_end_ns": window_end,
            "fail_to_continue": True,
            "hold_close": hold_close,
        }
        break
    if confirm is None and extreme is not None:
        depth = extreme - level if side == "short" else level - extreme
        sweep = dict(sweep)
        sweep["sweep_extreme"] = extreme
        sweep["sweep_depth"] = depth
        sweep["fail_window_end_ns"] = window_end
    return sweep, confirm


def excursion(market, start: int, end: int) -> tuple[Decimal | None, Decimal | None]:
    rows = _safe_bars(market, start, end)
    if not rows:
        return None, None
    return max(_dec(r["H"]) for r in rows if r.get("H") is not None), min(
        _dec(r["L"]) for r in rows if r.get("L") is not None
    )


def _stage(name: str, verdict: str, at_ns: int | None, **operands: Any) -> dict[str, Any]:
    return {"stage": name, "verdict": verdict, "at_ns": at_ns, "operands": jsonable(operands)}


def _rules_for(*ids: str) -> list[dict[str, Any]]:
    out = []
    for rule_id in ids:
        row = RULES.get(rule_id)
        if not row:
            continue
        item = {"rule_id": rule_id, **{k: v for k, v in row.items() if k != "_fn"}}
        out.append(item)
    return out


def _gate_stages(stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Later stages cannot pass after an earlier fail or unknown. Funnel stays monotone."""
    blocked = None
    blocker = None
    out: list[dict[str, Any]] = []
    by_name = {row["stage"]: row for row in stages}
    for name in STAGE_ORDER:
        row = by_name.get(name)
        if row is None:
            continue
        if blocked is not None and row.get("verdict") == "pass":
            operands = dict(row.get("operands") or {})
            operands["blocked_by"] = blocker
            row = {**row, "verdict": blocked, "operands": operands}
        out.append(row)
        if blocked is None and row.get("verdict") in {"fail", "unknown"}:
            blocked = "fail" if row.get("verdict") == "fail" else "unknown"
            blocker = name
    return out


def _verdict_from_stages(stages: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    failed: list[str] = []
    unknown: list[str] = []
    for row in stages:
        name = row["stage"]
        if row["verdict"] == "fail":
            failed.append(name)
        elif row["verdict"] == "unknown":
            unknown.append(name)
    if unknown and not failed:
        return "unknown", failed, unknown
    if failed:
        return "fail", failed, unknown
    return "pass", failed, unknown


def _episode(
    market,
    *,
    family: str,
    branch: str,
    side: str,
    stages: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    decision_at: int | None,
    entry: Decimal | None,
    stop: Decimal | None,
    target: Decimal | None,
    reference: Mapping[str, Any] | None,
    trigger: Mapping[str, Any] | None,
    values: dict[str, Any],
    geometry: dict[str, Any],
    scope: str = "entry_setup",
) -> dict[str, Any]:
    ordered = _gate_stages(stages)
    verdict, failed, unknown = _verdict_from_stages(ordered)
    if decision_at is None:
        decision_at = int(market.end)
        if verdict == "pass":
            verdict = "unknown"
            unknown = list(unknown) + ["decision_at"]
    identity = {
        "method": family,
        "branch": branch,
        "side": side,
        "session_date": str(market.day),
        "instrument_id": market.instrument_id,
        "reference_id": None if reference is None else reference.get("id"),
        "occurrence_at": None if trigger is None else trigger.get("start", trigger.get("at")),
        "baseline": B02_VERSION,
    }
    if scope == "entry_setup":
        status = {"pass": "setup", "fail": "no_setup", "unknown": "data_unavailable"}[verdict]
    else:
        status = {"pass": "condition_present", "fail": "condition_absent", "unknown": "data_unavailable"}[verdict]
    stop_points = None
    if entry is not None and stop is not None:
        stop_points = abs(entry - stop)
    ladder = []
    if entry is not None and target is not None:
        ladder = limit_ladder(entry, target, side)
    geometry = dict(geometry)
    geometry.update(
        {
            "entry": entry,
            "stop": stop,
            "target": target,
            "ladder": ladder,
            "first_objective": None if not ladder else ladder[0],
            "far_objective": None if not ladder else ladder[-1],
            "risk_dollars": RISK_DOLLARS,
            "derived_quantity": derived_quantity(stop_points) if stop_points else None,
            "objective_horizon_ns": next_rth_open_ns(market, decision_at),
            "research_horizon_30m_ns": int(decision_at) + 30 * MINUTE,
        }
    )
    values = dict(values)
    values.update(
        {
            "branch": branch,
            "side": side,
            "decision_at": decision_at,
            "risk_defined": None if entry is None or stop is None else sign(side) * (entry - stop) > 0,
            "objective_fixed": None if entry is None or target is None else sign(side) * (target - entry) > 0,
        }
    )
    return jsonable(
        {
            "schema": "phase1-historical-episode-v2",
            "candidate_id": "b02:" + content_hash(identity)[:32],
            "method": family,
            "branch": branch,
            "predicate": "sequence",
            "side": side,
            "session_date": str(market.day),
            "instrument_id": market.instrument_id,
            "reference_id": identity["reference_id"],
            "trigger_id": None if trigger is None else trigger.get("bar_id", trigger.get("id")),
            "occurrence_at": identity["occurrence_at"],
            "decision_at": decision_at,
            "values": values,
            "stages": ordered,
            "rules": rules,
            "research_verdict": verdict,
            "failed": failed,
            "unknown": unknown,
            "strategy_assessment": {"status": status, "scope": scope, "baseline_version": B02_VERSION},
            "author_exact_verdict": "unknown",
            "faithful_eligible": False,
            "actual_trade": False,
            "reference": reference,
            "trigger": trigger,
            "geometry": geometry,
            "baseline_version": B02_VERSION,
            "input_sha256": (market.window.document or {}).get("input_sha256"),
        }
    )


def _document(market, family: str, branch: str, episodes: list[dict[str, Any]], *, omissions: list | None = None) -> dict[str, Any]:
    counts = {key: sum(ep["research_verdict"] == key for ep in episodes) for key in ("pass", "fail", "unknown")}
    unfiltered = sum(1 for ep in episodes if ep["research_verdict"] == "pass")
    filtered = sum(
        1
        for ep in episodes
        if ep["research_verdict"] == "pass" and ep.get("values", {}).get("bias_compatible") is not False
    )
    try:
        coverage = market.coverage(market.at("09:30"), market.end)
    except Exception:
        coverage = {"observed_scope_complete": False}
    return jsonable(
        {
            "method_id": family,
            "branch": branch,
            "session_date": str(market.day),
            "instrument_id": market.instrument_id,
            "population_scope": "owned_observed_events",
            "population_complete": bool((coverage or {}).get("observed_scope_complete")) and not omissions,
            "coverage": coverage,
            "N_observed": len(episodes),
            "n": counts["pass"] + counts["fail"],
            "p": counts["pass"],
            "f": counts["fail"],
            "u": counts["unknown"],
            "episodes": episodes,
            "omissions": list(omissions or []),
            "baseline_version": B02_VERSION,
            "clock_zone_unverified": False,
            "coverage_id": f"{family}:branch:{branch}",
            "rules": _rules_for(*RULES),
            "bias": {
                "unfiltered_pass": unfiltered,
                "bias_filtered_pass": filtered,
                "rule_id": "F07-directional-bias",
            },
            "input_sha256": (market.window.document or {}).get("input_sha256"),
        }
    )


def _box_ns(market, spec: Mapping[str, Any]) -> tuple[int, int]:
    start = market.at(spec["start"], spec["start_off"])
    end = market.at(spec["end"], spec["end_off"])
    if spec["end"] == "00:00" and spec["end_off"] == 0 and end <= start:
        end = market.at("00:00")
    return int(start), int(end)


def _merge_extra_stages(stages: list[dict[str, Any]], extra: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not extra:
        return stages
    by_name = {row["stage"]: row for row in stages}
    for row in extra:
        name = row["stage"]
        current = by_name.get(name)
        if current is None:
            by_name[name] = row
            continue
        operands = dict(current.get("operands") or {})
        operands.update(row.get("operands") or {})
        verdict = current.get("verdict")
        if row.get("verdict") in {"fail", "unknown"}:
            verdict = row["verdict"]
        by_name[name] = {**current, **row, "verdict": verdict, "operands": operands}
    return [by_name[name] for name in STAGE_ORDER if name in by_name]


def _finish_level_trade(
    market,
    *,
    family: str,
    branch: str,
    side: str,
    ref: Mapping[str, Any],
    level: Decimal,
    sweep: Mapping[str, Any],
    confirm: Mapping[str, Any],
    mode: str,
    stop: Decimal,
    target: Decimal,
    rule_ids: tuple[str, ...],
    extra_values: dict[str, Any] | None = None,
    extra_stages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    decision = int(confirm["at_ns"])
    entry = level if mode == "at_level" else confirm.get("close")
    if entry is None:
        entry = level
    sweep_at = int(sweep.get("start") or decision)
    high, low = excursion(market, sweep_at, decision)
    box_low, box_high = _d(ref.get("low")), _d(ref.get("high"))
    confirm_close = _d(confirm.get("close"))
    sweep_extreme = _d(confirm.get("sweep_extreme"))
    if sweep_extreme is None:
        sweep_extreme = high if side == "short" else low
    sweep_depth = _d(confirm.get("sweep_depth"))
    if sweep_depth is None and sweep_extreme is not None:
        sweep_depth = sweep_extreme - level if side == "short" else level - sweep_extreme
    inside = confirm.get("inside_box")
    if inside is None:
        if mode == "at_level":
            inside = _inside_box(confirm_close, box_low, box_high)
            if inside is None:
                inside = _through_level(confirm_close, level, side)
        else:
            inside = _through_level(confirm_close, level, side)
    fail_to_continue = bool(confirm.get("fail_to_continue", True))
    through = confirm.get("through")
    if through is None:
        through = _through_level(confirm_close, level, side)
    bias = directional_bias(market, decision)
    compatible = bias_compatible(bias, side)
    session = session_label(market, decision)
    allowed = in_entry_windows(market, decision) or branch in {
        "nwog",
        "previous_hour",
        "golden_pocket",
        "golden_pocket_continuation",
        "source_long",
        "ny_session_extreme",
    }
    context_verdict = "pass" if allowed else "fail"
    location_distance = None
    if sweep_extreme is not None:
        location_distance = abs(sweep_extreme - level)
    trigger_ok = sweep_depth is not None and sweep_depth > 0
    confirm_ok = bool(through and inside is not False and fail_to_continue and confirm_close is not None)
    risk_ok = entry is not None and stop is not None and sign(side) * (entry - stop) > 0
    objective_ok = entry is not None and target is not None and sign(side) * (target - entry) > 0
    stop_points = None if entry is None or stop is None else abs(entry - stop)
    quantity = derived_quantity(stop_points) if stop_points else None
    ladder = limit_ladder(entry, target, side) if entry is not None and target is not None else []
    stages = [
        _stage(
            "context",
            context_verdict,
            decision,
            session=session,
            decision_ns=decision,
            bias_direction=bias.get("direction"),
            bias_prior_side=bias.get("prior_side"),
            bias_box_side=bias.get("box_side"),
            source_session_allowed=allowed,
            bias_compatible=compatible,
        ),
        _stage(
            "reference",
            "pass",
            int(ref.get("known_at") or decision),
            id=ref.get("id"),
            box_low=box_low,
            box_high=box_high,
            level=level,
            known_at=ref.get("known_at"),
        ),
        _stage(
            "location",
            "pass",
            sweep_at,
            level=level,
            box_low=box_low,
            box_high=box_high,
            sweep_extreme=sweep_extreme,
            distance_beyond_edge=location_distance,
        ),
        _stage(
            "trigger",
            "pass" if trigger_ok else "fail",
            sweep_at,
            sweep_at_ns=sweep_at,
            sweep_depth=sweep_depth,
            sweep_extreme=sweep_extreme,
            level=level,
            side=side,
        ),
        _stage(
            "confirmation",
            "pass" if confirm_ok else "fail",
            decision,
            mode=mode,
            confirm_close=confirm_close,
            confirm_at_ns=decision,
            through_level=through,
            inside_box=inside,
            fail_to_continue=fail_to_continue,
            fail_window_end_ns=confirm.get("fail_window_end_ns"),
            sweep_depth=sweep_depth,
        ),
        _stage(
            "risk",
            "pass" if risk_ok else "fail",
            decision,
            stop=stop,
            entry=entry,
            stop_points=stop_points,
            risk_dollars=str(RISK_DOLLARS),
        ),
        _stage(
            "objective",
            "pass" if objective_ok else "fail",
            decision,
            target=target,
            entry=entry,
            first_rung=None if not ladder else ladder[0],
            opposite_edge=box_low if side == "short" else box_high,
        ),
        _stage(
            "management",
            "pass" if risk_ok and objective_ok and quantity is not None else "fail",
            decision,
            derived_quantity=quantity,
            stop_points=stop_points,
            ladder_rungs=len(ladder),
            ladder_spacing=str(LADDER_SPACING),
            risk_dollars=str(RISK_DOLLARS),
        ),
    ]
    stages = _merge_extra_stages(stages, extra_stages)
    values = {
        "reference_frozen": True,
        "reference_known_at": ref.get("known_at"),
        "reference_px": level,
        "confirmation_mode": mode,
        "sweep_at": sweep.get("start"),
        "sweep_high": high,
        "sweep_low": low,
        "sweep_depth": sweep_depth,
        "confirm_at": decision,
        "confirm_close": confirm.get("close"),
        "inside_box": inside,
        "fail_to_continue": fail_to_continue,
        "bias_recorded": True,
        "bias_compatible": compatible,
        "bias": bias,
        "source_session_allowed": allowed,
    }
    if extra_values:
        values.update(extra_values)
    return _episode(
        market,
        family=family,
        branch=branch,
        side=side,
        stages=stages,
        rules=_rules_for(*rule_ids),
        decision_at=decision,
        entry=_d(entry),
        stop=stop,
        target=target,
        reference=ref,
        trigger=sweep,
        values=values,
        geometry={"confirmation_mode": mode},
    )


def _unknown_ref_episode(market, family, branch, side, reason, rule_ids):
    stages = [
        _stage("context", "pass", int(market.at("09:30")), session="ny_am"),
        _stage("reference", "unknown", None, reason=reason),
    ]
    return _episode(
        market,
        family=family,
        branch=branch,
        side=side,
        stages=stages,
        rules=_rules_for(*rule_ids),
        decision_at=int(market.at("09:30")),
        entry=None,
        stop=None,
        target=None,
        reference=None,
        trigger=None,
        values={"bias_compatible": None, "confirmation_mode": None},
        geometry={},
    )


def _scan_a1_london(market) -> list[dict[str, Any]]:
    spec = london_box_spec(market.day)
    start, end = _box_ns(market, spec)
    ref = _range(market, start, end, f"london-box-{spec['name']}")
    if ref is None:
        return [_unknown_ref_episode(market, "GB-FAIL", "london_box", "long", "london_box_missing", ("RR-11-sessions-boxes", "F06-A1-london"))]
    level = _dec(ref["low"])
    side = "long"
    search_end = min(int(market.end), int(market.at("11:30") + MINUTE))
    sweep = first_sweep(market, end, min(search_end, int(market.at("09:30"))), level, side)
    if sweep is None:
        sweep = first_sweep(market, end, search_end, level, side)
    if sweep is None:
        stages = [
            _stage("context", "pass", end, session="london", box=spec["name"]),
            _stage("reference", "pass", int(ref["known_at"]), low=level, box=spec["name"]),
            _stage("location", "fail", end, reason="no_london_low_sweep"),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="london_box",
                side=side,
                stages=stages,
                rules=_rules_for("RR-11-sessions-boxes", "F06-A1-london"),
                decision_at=end,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=None,
                values={"confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={"box": spec["name"]},
            )
        ]
    sweep_at = int(sweep.get("start") or end)
    reclaim = first_five_minute_close_through(market, sweep_at, level, side, limit_ns=search_end)
    if reclaim is None:
        stages = [
            _stage("context", "pass", sweep_at, session=session_label(market, sweep_at)),
            _stage("reference", "pass", int(ref["known_at"]), low=level),
            _stage("location", "pass", sweep_at, sweep=True),
            _stage("trigger", "pass", sweep_at, sweep=True, level=level),
            _stage("confirmation", "fail", sweep_at, reason="no_reclaim"),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="london_box",
                side=side,
                stages=stages,
                rules=_rules_for("F06-A1-london"),
                decision_at=sweep_at,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=sweep,
                values={"confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={},
            )
        ]
    high, low = excursion(market, sweep_at, int(reclaim["at_ns"]))
    retest_start = int(reclaim["at_ns"])
    retest = None
    hl_ok = False
    later = _safe_bars(market, retest_start, int(market.at("09:30")) if retest_start < market.at("09:30") else search_end)
    for row in later:
        lo = _d(row.get("L"))
        hi = _d(row.get("H"))
        if lo is None:
            continue
        if lo <= level <= (hi or level):
            retest = row
            hl_ok = low is None or lo > low
            if hl_ok:
                break
    if retest is None or not hl_ok:
        if int(reclaim["at_ns"]) >= int(market.at("09:30")):
            high, low = excursion(market, sweep_at, int(reclaim["at_ns"]))
            stop = (low - SWEEP_STOP_BUFFER) if low is not None else level - SWEEP_STOP_BUFFER
            far = _dec(ref["high"])
            tdo = _tdo(market)
            entry_px = _d(reclaim.get("close")) or level
            if tdo is not None and (tdo - entry_px) > 0:
                target = tdo
            else:
                target = far if far > entry_px else entry_px + Decimal("15")
            extra = [
                _stage(
                    "confirmation",
                    "pass",
                    int(reclaim["at_ns"]),
                    mode="five_minute_close",
                    reclaim_px=reclaim.get("close"),
                    reclaim_at_ns=reclaim.get("at_ns"),
                    stop_placement="sweep_extreme_plus_buffer",
                    sweep_low=low,
                    buffer=str(SWEEP_STOP_BUFFER),
                )
            ]
            ep = _finish_level_trade(
                market,
                family="GB-FAIL",
                branch="london_box",
                side=side,
                ref=ref,
                level=level,
                sweep=sweep,
                confirm=reclaim,
                mode="five_minute_close",
                stop=stop,
                target=target,
                rule_ids=("RR-11-sessions-boxes", "F06-A1-london", "RR-13-confirmation-modes", "RR-12-risk-exits", "F07-directional-bias"),
                extra_values={
                    "tdo_required": False,
                    "tdo": tdo,
                    "london_high": far,
                    "box": spec["name"],
                    "stop_placement": "sweep_extreme_plus_buffer",
                    "stop_sweep_extreme_plus_buffer": stop,
                    "sweep_extreme": low,
                },
                extra_stages=extra,
            )
            ep["geometry"]["second_objective"] = far
            return [ep]
        stages = [
            _stage("context", "pass", retest_start, session=session_label(market, retest_start)),
            _stage("reference", "pass", int(ref["known_at"]), id=ref.get("id"), level=level),
            _stage("location", "pass", sweep_at, sweep=True, level=level),
            _stage("trigger", "pass", sweep_at, sweep=True, level=level),
            _stage("confirmation", "fail", retest_start, reason="mandatory_retest_or_higher_low_missing"),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="london_box",
                side=side,
                stages=stages,
                rules=_rules_for("F06-A1-london"),
                decision_at=retest_start,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=sweep,
                values={"confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={},
            )
        ]
    post_open = first_five_minute_close_through(
        market, max(int(retest.get("end") or retest_start), int(market.at("09:30"))), level, side, limit_ns=search_end
    )
    if post_open is None:
        stages = [
            _stage("context", "pass", int(market.at("09:30")), session="ny_am"),
            _stage("reference", "pass", int(ref["known_at"]), id=ref.get("id"), level=level),
            _stage("location", "pass", sweep_at, sweep=True, level=level),
            _stage("trigger", "pass", sweep_at, sweep=True, level=level),
            _stage("confirmation", "fail", int(market.at("09:30")), reason="no_post_open_close"),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="london_box",
                side=side,
                stages=stages,
                rules=_rules_for("F06-A1-london"),
                decision_at=int(market.at("09:30")),
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=sweep,
                values={"confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={},
            )
        ]
    tdo = _tdo(market)
    retest_low = _d(retest.get("L"))
    sweep_extreme_stop = (low - Q) if low is not None else level - Q
    stop = (retest_low - Q) if retest_low is not None else sweep_extreme_stop
    far = _dec(ref["high"])
    entry_px = _d(post_open.get("close")) or level
    if tdo is not None and (tdo - entry_px) > 0:
        target = tdo
    else:
        target = far if far > entry_px else entry_px + Decimal("15")
    extra = [
        _stage(
            "confirmation",
            "pass",
            int(post_open["at_ns"]),
            mode="five_minute_close",
            reclaim_px=reclaim.get("close"),
            reclaim_at_ns=reclaim.get("at_ns"),
            retest_low=retest_low,
            retest_at_ns=retest.get("known_at") or retest.get("end"),
            sweep_low=low,
            higher_low_ok=bool(hl_ok),
            higher_low_comparison={"retest_low": retest_low, "sweep_low": low},
            post_open_close=post_open.get("close"),
            post_open_at_ns=post_open.get("at_ns"),
        )
    ]
    ep = _finish_level_trade(
        market,
        family="GB-FAIL",
        branch="london_box",
        side=side,
        ref=ref,
        level=level,
        sweep=sweep,
        confirm=post_open,
        mode="five_minute_close",
        stop=stop,
        target=target,
        rule_ids=("RR-11-sessions-boxes", "F06-A1-london", "RR-13-confirmation-modes", "RR-12-risk-exits", "F07-directional-bias"),
        extra_values={
            "tdo_required": False,
            "tdo": tdo,
            "london_high": far,
            "box": spec["name"],
            "stop_placement": "retest_higher_low",
            "stop_retest_higher_low": stop,
            "stop_sweep_extreme_od_variant": sweep_extreme_stop,
            "retest_low": retest_low,
            "sweep_extreme": low,
        },
        extra_stages=extra,
    )
    ep["geometry"]["second_objective"] = far
    return [ep]


def _scan_asia_high(market) -> list[dict[str, Any]]:
    spec = asia_box_spec(market.day)
    start, end = _box_ns(market, spec)
    ref = _range(market, start, end, f"asia-box-{spec['name']}")
    if ref is None:
        return [_unknown_ref_episode(market, "GB-FAIL", "asia_box", "short", "asia_box_missing", ("RR-11-sessions-boxes", "F06-A2-asia"))]
    level = _dec(ref["high"])
    side = "short"
    search_end = int(market.end)
    sweep = first_sweep(market, end, search_end, level, side)
    if sweep is None:
        stages = [
            _stage("context", "pass", end, session="asia", box=spec["name"]),
            _stage("reference", "pass", int(ref["known_at"]), high=level, box=spec["name"]),
            _stage("location", "fail", end, reason="no_asia_high_sweep"),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="asia_box",
                side=side,
                stages=stages,
                rules=_rules_for("F06-A2-asia"),
                decision_at=end,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=None,
                values={"tdo_required": False, "confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={"box": spec["name"]},
            )
        ]
    sweep_at = int(sweep.get("start") or end)
    confirm = first_five_minute_close_through(market, sweep_at, level, side, limit_ns=search_end)
    if confirm is None:
        stages = [
            _stage("context", "pass", sweep_at, session=session_label(market, sweep_at)),
            _stage("reference", "pass", int(ref["known_at"]), id=ref.get("id"), level=level),
            _stage("location", "pass", sweep_at, sweep=True, level=level),
            _stage("trigger", "pass", sweep_at, sweep=True, level=level),
            _stage("confirmation", "fail", sweep_at, reason="no_five_minute_close", tdo_required=False),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="asia_box",
                side=side,
                stages=stages,
                rules=_rules_for("F06-A2-asia", "RR-13-confirmation-modes"),
                decision_at=sweep_at,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=sweep,
                values={"tdo_required": False, "confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={},
            )
        ]
    high, low = excursion(market, sweep_at, int(confirm["at_ns"]))
    stop = (high + Q) if high is not None else level + Q
    target = _dec(ref["low"])
    return [
        _finish_level_trade(
            market,
            family="GB-FAIL",
            branch="asia_box",
            side=side,
            ref=ref,
            level=level,
            sweep=sweep,
            confirm=confirm,
            mode="five_minute_close",
            stop=stop,
            target=target,
            rule_ids=("RR-11-sessions-boxes", "F06-A2-asia", "RR-13-confirmation-modes", "RR-12-risk-exits", "F07-directional-bias"),
            extra_values={"tdo_required": False, "box": spec["name"]},
        )
    ]


def _scan_asia_tdo(market) -> list[dict[str, Any]]:
    spec = asia_box_spec(market.day)
    start, end = _box_ns(market, spec)
    ref = _range(market, start, end, f"asia-tdo-{spec['name']}")
    tdo = _tdo(market)
    if ref is None or tdo is None:
        return [_unknown_ref_episode(market, "GB-FAIL", "asia_tdo_case", "short", "asia_or_tdo_missing", ("RR-13-confirmation-modes", "F06-A2-asia"))]
    level = _dec(ref["high"])
    side = "short"
    sweep = first_sweep(market, end, int(market.end), level, side)
    if sweep is None:
        stages = [
            _stage("context", "pass", end, session="asia"),
            _stage("reference", "pass", int(ref["known_at"]), asia_high=level, tdo=tdo),
            _stage("location", "fail", end, reason="no_asia_high_sweep", level=level, tdo=tdo),
            _stage("trigger", "fail", end, reason="no_sweep", sweep_depth=0, level=level),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="asia_tdo_case",
                side=side,
                stages=stages,
                rules=_rules_for("RR-13-confirmation-modes", "F06-A2-asia"),
                decision_at=end,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=None,
                values={"tdo_required": True, "confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={},
            )
        ]
    sweep_at = int(sweep.get("start") or end)
    confirm = first_five_minute_close_through(market, sweep_at, tdo, side, limit_ns=int(market.end))
    if confirm is None:
        stages = [
            _stage("context", "pass", sweep_at, session=session_label(market, sweep_at)),
            _stage("reference", "pass", int(ref["known_at"]), asia_high=level, tdo=tdo),
            _stage("location", "pass", sweep_at, sweep=True, level=level),
            _stage("trigger", "pass", sweep_at, sweep=True, level=level, tdo=tdo),
            _stage("confirmation", "fail", sweep_at, reason="no_five_minute_close_below_tdo"),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="asia_tdo_case",
                side=side,
                stages=stages,
                rules=_rules_for("RR-13-confirmation-modes"),
                decision_at=sweep_at,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=sweep,
                values={"tdo_required": True, "confirmation_mode": "five_minute_close", "bias_compatible": None},
                geometry={},
            )
        ]
    high, _low = excursion(market, sweep_at, int(confirm["at_ns"]))
    stop = (high + Q) if high is not None else level + Q
    target = _dec(ref["low"])
    return [
        _finish_level_trade(
            market,
            family="GB-FAIL",
            branch="asia_tdo_case",
            side=side,
            ref=ref,
            level=tdo,
            sweep=sweep,
            confirm=confirm,
            mode="five_minute_close",
            stop=stop,
            target=target,
            rule_ids=("RR-13-confirmation-modes", "F06-A2-asia", "RR-12-risk-exits"),
            extra_values={"tdo_required": True, "asia_high": level, "tdo": tdo},
        )
    ]


def _scan_pdl(market) -> list[dict[str, Any]]:
    ref, omissions = _prior_day_range(market)
    if ref is None:
        return [_unknown_ref_episode(market, "GB-FAIL", "prior_day_level", "long", "prior_day_missing", ("F06-A3-pdl",))]
    episodes = []
    for side, key in (("long", "low"), ("short", "high")):
        level = _d(ref.get(key))
        if level is None:
            continue
        begin = int(market.start)
        sweep = first_sweep(market, begin, int(market.end), level, side)
        if sweep is None:
            stages = [
                _stage("context", "pass", begin, session=session_label(market, begin)),
                _stage("reference", "pass", int(ref.get("known_at") or begin), level=level, side=side),
                _stage("location", "fail", begin, reason="no_sweep_of_prior_day_level", level=level, side=side),
                _stage("trigger", "fail", begin, reason="no_sweep", sweep_depth=0, level=level),
            ]
            episodes.append(
                _episode(
                    market,
                    family="GB-FAIL",
                    branch="prior_day_level",
                    side=side,
                    stages=stages,
                    rules=_rules_for("F06-A3-pdl"),
                    decision_at=begin,
                    entry=None,
                    stop=None,
                    target=None,
                    reference=ref,
                    trigger=None,
                    values={"confirmation_mode": "five_minute_close", "bias_compatible": None},
                    geometry={},
                )
            )
            continue
        sweep_at = int(sweep.get("start") or begin)
        confirm = first_five_minute_close_through(market, sweep_at, level, side, limit_ns=int(market.end))
        if confirm is None:
            stages = [
                _stage("context", "pass", sweep_at, session=session_label(market, sweep_at)),
                _stage("reference", "pass", int(ref.get("known_at") or begin), level=level),
                _stage("location", "pass", sweep_at, sweep=True, level=level),
                _stage("trigger", "pass", sweep_at, sweep=True, level=level),
                _stage("confirmation", "fail", sweep_at, reason="no_five_minute_close"),
            ]
            episodes.append(
                _episode(
                    market,
                    family="GB-FAIL",
                    branch="prior_day_level",
                    side=side,
                    stages=stages,
                    rules=_rules_for("F06-A3-pdl", "RR-13-confirmation-modes"),
                    decision_at=sweep_at,
                    entry=None,
                    stop=None,
                    target=None,
                    reference=ref,
                    trigger=sweep,
                    values={"confirmation_mode": "five_minute_close", "bias_compatible": None},
                    geometry={},
                )
            )
            continue
        stop = level + Q if side == "short" else level - Q
        tdo = _tdo(market)
        if side == "long":
            pdh = _d(ref.get("high"))
            target = pdh if pdh is not None else tdo
        else:
            target = _dec(ref["low"])
        episodes.append(
            _finish_level_trade(
                market,
                family="GB-FAIL",
                branch="prior_day_level",
                side=side,
                ref=ref,
                level=level,
                sweep=sweep,
                confirm=confirm,
                mode="five_minute_close",
                stop=stop,
                target=target,
                rule_ids=("F06-A3-pdl", "RR-13-confirmation-modes", "RR-12-risk-exits", "RR-15-objective-horizon"),
                extra_values={"stop_is_swept_level": True},
            )
        )
    if omissions:
        for ep in episodes:
            ep.setdefault("limitations", []).extend(omissions)
    return episodes


def _scan_box_at_level(market, *, branch: str, ref: Mapping[str, Any], begin: int, end: int, sides: tuple[str, ...], extra_values=None) -> list[dict[str, Any]]:
    episodes = []
    box_low, box_high = _d(ref.get("low")), _d(ref.get("high"))
    for side in sides:
        level = _dec(ref["high"] if side == "short" else ref["low"])
        sweep, ret = sweep_and_at_level(
            market, begin, end, level, side, box_low=box_low, box_high=box_high
        )
        if sweep is None:
            stages = [
                _stage("context", "pass", int(begin), session=session_label(market, int(begin))),
                _stage(
                    "reference",
                    "pass",
                    int(ref.get("known_at") or begin),
                    id=ref.get("id"),
                    box_low=box_low,
                    box_high=box_high,
                    level=level,
                ),
                _stage(
                    "location",
                    "fail",
                    int(begin),
                    reason="no_touch_of_edge",
                    level=level,
                    box_low=box_low,
                    box_high=box_high,
                    search_begin=begin,
                    search_end=end,
                ),
                _stage("trigger", "fail", int(begin), reason="no_sweep", sweep_depth=0, level=level),
            ]
            episodes.append(
                _episode(
                    market,
                    family="GB-FAIL",
                    branch=branch,
                    side=side,
                    stages=stages,
                    rules=_rules_for("RR-13-confirmation-modes"),
                    decision_at=int(begin),
                    entry=None,
                    stop=None,
                    target=None,
                    reference=ref,
                    trigger=None,
                    values={
                        "confirmation_mode": "at_level",
                        "not_before_1000": False,
                        "bias_compatible": None,
                        **(extra_values or {}),
                    },
                    geometry={},
                )
            )
            continue
        sweep_at = int(sweep.get("start") or begin)
        depth = _d(sweep.get("sweep_depth"))
        extreme = _d(sweep.get("sweep_extreme"))
        if ret is None:
            if depth is None and extreme is not None:
                depth = extreme - level if side == "short" else level - extreme
            stages = [
                _stage("context", "pass", sweep_at, session=session_label(market, sweep_at)),
                _stage(
                    "reference",
                    "pass",
                    int(ref.get("known_at") or begin),
                    id=ref.get("id"),
                    box_low=box_low,
                    box_high=box_high,
                    level=level,
                ),
                _stage(
                    "location",
                    "pass",
                    sweep_at,
                    level=level,
                    box_low=box_low,
                    box_high=box_high,
                    sweep_extreme=extreme,
                    distance_beyond_edge=depth,
                ),
                _stage(
                    "trigger",
                    "pass",
                    sweep_at,
                    sweep_at_ns=sweep_at,
                    sweep_depth=depth,
                    sweep_extreme=extreme,
                    level=level,
                ),
                _stage(
                    "confirmation",
                    "fail",
                    int(sweep.get("fail_window_end_ns") or sweep.get("end") or begin),
                    reason="no_close_back_inside_fail_window",
                    mode="at_level",
                    fail_window_end_ns=sweep.get("fail_window_end_ns"),
                    sweep_depth=depth,
                    inside_box=False,
                    fail_to_continue=False,
                    confirm_close=None,
                ),
            ]
            episodes.append(
                _episode(
                    market,
                    family="GB-FAIL",
                    branch=branch,
                    side=side,
                    stages=stages,
                    rules=_rules_for("RR-13-confirmation-modes"),
                    decision_at=int(sweep.get("end") or begin),
                    entry=None,
                    stop=None,
                    target=None,
                    reference=ref,
                    trigger=sweep,
                    values={
                        "confirmation_mode": "at_level",
                        "not_before_1000": False,
                        "bias_compatible": None,
                        **(extra_values or {}),
                    },
                    geometry={},
                )
            )
            continue
        decision = int(ret["at_ns"])
        high, low = excursion(market, sweep_at, decision)
        if side == "short":
            stop = (high + Q) if high is not None else level + Q
            target = _dec(ref["low"])
        else:
            stop = (low - Q) if low is not None else level - Q
            target = _dec(ref["high"])
        values = {"not_before_1000": False, "box_complete_after_1000": begin >= market.at("10:00")}
        if extra_values:
            values.update(extra_values)
        episodes.append(
            _finish_level_trade(
                market,
                family="GB-FAIL",
                branch=branch,
                side=side,
                ref=ref,
                level=level,
                sweep=sweep,
                confirm=ret,
                mode="at_level",
                stop=stop,
                target=target,
                rule_ids=("RR-13-confirmation-modes", "RR-11-sessions-boxes", "RR-12-risk-exits", "F07-directional-bias"),
                extra_values=values,
            )
        )
    return episodes


def _scan_nyam(market) -> list[dict[str, Any]]:
    """Named NY boxes only. 09:00-10:00 cannot be traded before 10:00 (wiki RR-11).

    09:00-09:30 is GB p.58 and is searched only until 10:00, when the green
    09:00-10:00 box exists. The PM short is the 12:45-13:00 sweep of the
    09:00-10:00 highs (GB pp.45, 56). The grey 10:00-11:00 sub-box is the
    live-painted developing hour on the Sep-2026 charts (context for the
    10:05 retest of the 9-10 box), not a third fail reference.
    """
    episodes = []
    nyam_end = int(market.at("11:30") + MINUTE)
    boxes = [
        ("09:00-09:30", market.at("09:00"), market.at("09:30"), market.at("09:30"), int(market.at("10:00") + MINUTE)),
        ("09:00-10:00", market.at("09:00"), market.at("10:00"), market.at("10:00"), nyam_end),
    ]
    seen: set[tuple[str, str]] = set()
    for name, a, b, begin, end in boxes:
        ref = _range(market, a, b, f"nyam-{name}")
        if ref is None:
            continue
        part = _scan_box_at_level(
            market,
            branch="nyam_box",
            ref=ref,
            begin=int(begin),
            end=int(end),
            sides=("short", "long"),
            extra_values={"box": name},
        )
        for ep in part:
            key = ep["side"], str(ep["values"].get("reference_px"))
            if key in seen:
                continue
            seen.add(key)
            episodes.append(ep)
    nine_ten = _range(market, market.at("09:00"), market.at("10:00"), "nyam-09:00-10:00-pm")
    if nine_ten is not None:
        part = _scan_box_at_level(
            market,
            branch="nyam_box",
            ref=nine_ten,
            begin=int(market.at("12:45")),
            end=int(market.at("13:30") + MINUTE),
            sides=("short",),
            extra_values={"box": "pm_sweep_910_high", "session": "ny_pm"},
        )
        for ep in part:
            key = ep["side"], str(ep["values"].get("reference_px"))
            if key in seen:
                continue
            seen.add(key)
            episodes.append(ep)
    return episodes


def _scan_previous_hour(market) -> list[dict[str, Any]]:
    """Completed-hour fail-back (GB pp.37-38) for hours that are not a named NYAM box.

    Hours 9 and 10 are the 09:00-10:00 box and the 10:00-11:00 sub-box. Hour 8
    (08:00-09:00) completes before cash open and is not a painted session box;
    09:00-09:15 is also before the author's NYAM entries (GB p.58 is 09:32).
    Hours 11-12 sit in the 11:30-12:45 lunch gap and the 12:45-13:00 PM
    window of the 9-10 highs; those clocks are nyam_box, not this branch.
    Hours 13-14 remain the repeating previous-hour template after the PM window.
    """
    episodes = []
    for hour in (13, 14):
        a = market.at(f"{hour:02d}:00")
        b = market.at(f"{hour + 1:02d}:00")
        ref = _range(market, a, b, f"hour-{hour}")
        if ref is None:
            continue
        begin = int(ref.get("known_at") or b)
        end = min(int(market.end), begin + PREVIOUS_HOUR_SEARCH_MINUTES * MINUTE)
        episodes.extend(
            _scan_box_at_level(
                market,
                branch="previous_hour",
                ref=ref,
                begin=begin,
                end=end,
                sides=("short", "long"),
                extra_values={"hour": hour},
            )
        )
    return episodes


def _scan_cash_open(market) -> list[dict[str, Any]]:
    """09:30 manipulation below, reclaim, retracement objective, stop at lows.

    GB p.3 / p.40. B0.2 previously reused the box at-level helper on a
    degenerate single-price ref, so target==entry and objective always failed
    (0 full-history passes vs 721 under B0.1). That kill is not the source's.
    """
    rows = _safe_bars(market, market.at("09:30"), market.at("09:30") + MINUTE)
    if not rows or rows[0].get("O") is None:
        return [_unknown_ref_episode(market, "GB-FAIL", "cash_open_reclaim_case", "long", "cash_open_unknown", ("F06-A3-pdl",))]
    row = rows[0]
    px = _dec(row["O"])
    known = int(row.get("known_at") or market.at("09:30"))
    ref = {
        "id": str(row.get("bar_id")) + ":cash-open",
        "low": px,
        "high": px,
        "known_at": known,
        "open": px,
    }
    begin = int(market.at("09:30"))
    end = int(market.at("11:30") + MINUTE)
    side = "long"
    sweep = first_sweep(market, begin, end, px, side)
    if sweep is None:
        stages = [
            _stage("context", "pass", begin, session="ny_am"),
            _stage("reference", "pass", known, cash_open=px, level=px),
            _stage("location", "fail", begin, reason="no_trade_below_cash_open", level=px, cash_open=px),
            _stage("trigger", "fail", begin, reason="no_sweep_below_open", sweep_depth=0, level=px),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="cash_open_reclaim_case",
                side=side,
                stages=stages,
                rules=_rules_for("F06-A3-pdl"),
                decision_at=begin,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=None,
                values={"confirmation_mode": "reclaim_od", "bias_compatible": None},
                geometry={},
            )
        ]
    sweep_at = int(sweep.get("start") or begin)
    confirm = first_five_minute_close_through(market, sweep_at, px, side, limit_ns=end)
    high, low = excursion(market, sweep_at, int(confirm["at_ns"]) if confirm else sweep_at + FIVE)
    if confirm is None:
        stages = [
            _stage("context", "pass", sweep_at, session=session_label(market, sweep_at)),
            _stage("reference", "pass", known, cash_open=px, level=px),
            _stage("location", "pass", sweep_at, level=px, cash_open=px, sweep_extreme=low),
            _stage(
                "trigger",
                "pass",
                sweep_at,
                sweep_at_ns=sweep_at,
                sweep_depth=None if low is None else px - low,
                sweep_extreme=low,
                level=px,
            ),
            _stage(
                "confirmation",
                "fail",
                sweep_at,
                reason="no_reclaim_close_above_open",
                mode="reclaim_od",
                cash_open=px,
                confirm_close=None,
                duration_unspecified=True,
            ),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="cash_open_reclaim_case",
                side=side,
                stages=stages,
                rules=_rules_for("F06-A3-pdl"),
                decision_at=sweep_at,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=sweep,
                values={"confirmation_mode": "reclaim_od", "bias_compatible": None},
                geometry={},
            )
        ]
    stop = (low - Q) if low is not None else px - Q
    sweep_depth = None if low is None else px - low
    target = px + sweep_depth * Decimal("0.5") if sweep_depth is not None else None
    extra = [
        _stage(
            "confirmation",
            "pass",
            int(confirm["at_ns"]),
            mode="reclaim_od",
            duration_unspecified=True,
            confirm_close=confirm.get("close"),
            confirm_at_ns=confirm.get("at_ns"),
            cash_open=px,
            through_level=True,
            inside_box=True,
        )
    ]
    return [
        _finish_level_trade(
            market,
            family="GB-FAIL",
            branch="cash_open_reclaim_case",
            side=side,
            ref=ref,
            level=px,
            sweep=sweep,
            confirm={**confirm, "inside_box": True, "fail_to_continue": True, "sweep_extreme": low, "sweep_depth": sweep_depth},
            mode="reclaim_od",
            stop=stop,
            target=target,
            rule_ids=("F06-A3-pdl", "RR-12-risk-exits"),
            extra_values={
                "confirmation_mode_od": True,
                "retracement_objective": True,
                "stop_at_lows": True,
                "cash_open": px,
                "sweep_depth": sweep_depth,
            },
            extra_stages=extra,
        )
    ]


def _scan_nwog(market) -> list[dict[str, Any]]:
    if market.day.weekday() != 0:
        stages = [
            _stage("context", "fail", int(market.at("09:30")), reason="not_monday", weekday=market.day.weekday()),
            _stage("reference", "fail", int(market.at("09:30")), reason="not_monday"),
        ]
        return [
            _episode(
                market,
                family="GB-FAIL",
                branch="nwog",
                side="short",
                stages=stages,
                rules=_rules_for("F06-A5-nwog"),
                decision_at=int(market.at("09:30")),
                entry=None,
                stop=None,
                target=None,
                reference=None,
                trigger=None,
                values={"confirmation_mode": "at_level", "bias_compatible": None},
                geometry={},
            )
        ]
    gap = _nwog_levels(market)
    if gap is None:
        return [_unknown_ref_episode(market, "GB-FAIL", "nwog", "short", "nwog_unavailable", ("F06-A5-nwog",))]
    ref = {
        "id": gap["id"],
        "low": gap["low"],
        "high": gap["high"],
        "known_at": gap["known_at"],
    }
    return _scan_box_at_level(
        market,
        branch="nwog",
        ref=ref,
        begin=int(gap["known_at"]),
        end=int(market.end),
        sides=("short", "long"),
        extra_values={"no_0930_1100_cutoff": True, "monday_only": True},
    )


def _impulse_leg(market, *, kind: str, end_ns: int | None = None) -> dict[str, Any] | None:
    if kind == "up":
        rows = _safe_bars(market, market.at("06:00"), int(end_ns) if end_ns is not None else market.at("09:35"))
    else:
        rows = _safe_bars(market, market.at("18:00", -1), int(end_ns) if end_ns is not None else market.at("00:00"))
    if not rows:
        return None
    lo_i = min(range(len(rows)), key=lambda i: _dec(rows[i]["L"]))
    hi_i = max(range(len(rows)), key=lambda i: _dec(rows[i]["H"]))
    if kind == "up" and hi_i > lo_i:
        low, high = _dec(rows[lo_i]["L"]), _dec(rows[hi_i]["H"])
        side = "up"
        start, end = rows[lo_i]["start"], rows[hi_i]["end"]
        known = rows[hi_i].get("known_at") or end
    elif kind == "down" and lo_i > hi_i:
        low, high = _dec(rows[lo_i]["L"]), _dec(rows[hi_i]["H"])
        side = "down"
        start, end = rows[hi_i]["start"], rows[lo_i]["end"]
        known = rows[lo_i].get("known_at") or end
    else:
        return None
    if high <= low:
        return None
    return {
        "id": f"impulse:{kind}:{market.instrument_id}:{start}:{end}",
        "low": low,
        "high": high,
        "side": side,
        "start": start,
        "end": end,
        "known_at": known,
    }


def _scan_golden_pocket(market, *, family: str, branch: str, kinds: tuple[str, ...]) -> list[dict[str, Any]]:
    episodes = []
    nyam = _range(market, market.at("09:00"), market.at("10:00"), "nyam-not-impulse")
    ny_pullback = family == "GB-SCALP"
    impulse_end = market.at("09:30") if ny_pullback else None
    for kind in kinds:
        impulse = _impulse_leg(market, kind=kind, end_ns=impulse_end)
        if impulse is None:
            stages = [
                _stage("context", "pass", int(market.at("09:30")), session="ny_am" if ny_pullback else "overnight"),
                _stage("reference", "fail", int(market.at("09:30")), reason="no_defined_impulse", kind=kind),
                _stage("location", "fail", int(market.at("09:30")), reason="no_defined_impulse", kind=kind),
            ]
            episodes.append(
                _episode(
                    market,
                    family=family,
                    branch=branch,
                    side="long" if kind == "up" else "short",
                    stages=stages,
                    rules=_rules_for("RR-14-golden-pocket", "F06-A4-pocket"),
                    decision_at=int(market.at("09:30")),
                    entry=None,
                    stop=None,
                    target=None,
                    reference=None,
                    trigger=None,
                    values={"confirmation_mode": "five_minute_close", "bias_compatible": None, "pocket_required": True},
                    geometry={},
                )
            )
            continue
        if nyam is not None and impulse["low"] == _d(nyam.get("low")) and impulse["high"] == _d(nyam.get("high")):
            continue
        pocket = pocket_in_leg_direction(impulse["low"], impulse["high"], impulse["side"])
        near = near_edge(pocket, impulse["side"])
        far = far_edge(pocket, impulse["side"])
        trade_side = "long" if impulse["side"] == "up" else "short"
        begin = int(impulse["known_at"])
        if ny_pullback:
            begin = max(begin, int(market.at("09:30")))
        end = int(market.end)
        pullback = None
        far_taken_before_confirm = False
        for row in _safe_bars(market, begin, end):
            lo, hi = _d(row.get("L")), _d(row.get("H"))
            if lo is None or hi is None:
                continue
            if lo <= pocket[1] and hi >= pocket[0]:
                pullback = row
                close = _d(row.get("C"))
                if trade_side == "long" and close is not None and close < far:
                    far_taken_before_confirm = True
                if trade_side == "short" and close is not None and close > far:
                    far_taken_before_confirm = True
                break
        if pullback is None:
            stages = [
                _stage("context", "pass", begin, session=session_label(market, begin)),
                _stage(
                    "reference",
                    "pass",
                    begin,
                    impulse=impulse["id"],
                    pocket_low=pocket[0],
                    pocket_high=pocket[1],
                    impulse_width=impulse["high"] - impulse["low"],
                    not_9_10_box=True,
                ),
                _stage(
                    "location",
                    "fail",
                    begin,
                    reason="no_pullback_into_pocket",
                    pocket_low=pocket[0],
                    pocket_high=pocket[1],
                    ny_pullback=ny_pullback,
                ),
                _stage(
                    "trigger",
                    "fail",
                    begin,
                    reason="no_pullback_into_pocket",
                    pocket_low=pocket[0],
                    pocket_high=pocket[1],
                ),
            ]
            episodes.append(
                _episode(
                    market,
                    family=family,
                    branch=branch,
                    side=trade_side,
                    stages=stages,
                    rules=_rules_for("RR-14-golden-pocket", "F06-A4-pocket", "F01-scalp-observations"),
                    decision_at=begin,
                    entry=None,
                    stop=None,
                    target=None,
                    reference=impulse,
                    trigger=None,
                    values={"confirmation_mode": "five_minute_close", "bias_compatible": None, "pocket_required": True},
                    geometry={"pocket": {"low": pocket[0], "high": pocket[1]}, "impulse": impulse},
                    scope="entry_setup",
                )
            )
            continue
        confirm = first_five_minute_close_through(
            market, int(pullback.get("end") or begin), near, trade_side, limit_ns=end
        )
        pull_at = int(pullback.get("start") or begin)
        if far_taken_before_confirm:
            stages = [
                _stage("context", "pass", pull_at, session=session_label(market, pull_at)),
                _stage("reference", "pass", begin, not_9_10_box=True, pocket_low=pocket[0], pocket_high=pocket[1]),
                _stage("location", "pass", pull_at, pocket_touch=True, near=near, pocket_low=pocket[0], pocket_high=pocket[1]),
                _stage("trigger", "pass", pull_at, pocket_touch=True, near=near, pullback_at_ns=pull_at),
                _stage(
                    "confirmation",
                    "fail",
                    pull_at,
                    reason="far_edge_taken_before_close_out",
                    mode_od=True,
                    far=far,
                    near=near,
                    continuation_hold=False,
                ),
            ]
            episodes.append(
                _episode(
                    market,
                    family=family,
                    branch=branch,
                    side=trade_side,
                    stages=stages,
                    rules=_rules_for("RR-14-golden-pocket", "F06-A4-pocket"),
                    decision_at=pull_at,
                    entry=None,
                    stop=None,
                    target=None,
                    reference=impulse,
                    trigger=pullback,
                    values={"confirmation_mode": "five_minute_close", "bias_compatible": None, "pocket_required": True},
                    geometry={"pocket": {"low": pocket[0], "high": pocket[1]}},
                )
            )
            continue
        if confirm is None:
            stages = [
                _stage("context", "pass", pull_at, session=session_label(market, pull_at)),
                _stage("reference", "pass", begin, not_9_10_box=True, pocket_low=pocket[0], pocket_high=pocket[1]),
                _stage("location", "pass", pull_at, pocket_touch=True, near=near, pocket_low=pocket[0], pocket_high=pocket[1]),
                _stage("trigger", "pass", pull_at, pocket_touch=True, near=near, pullback_at_ns=pull_at),
                _stage(
                    "confirmation",
                    "fail",
                    int(pullback.get("end") or begin),
                    reason="no_close_out_of_pocket",
                    mode_od=True,
                    near=near,
                    confirm_close=None,
                ),
            ]
            episodes.append(
                _episode(
                    market,
                    family=family,
                    branch=branch,
                    side=trade_side,
                    stages=stages,
                    rules=_rules_for("RR-14-golden-pocket", "F06-A4-pocket"),
                    decision_at=int(pullback.get("end") or begin),
                    entry=None,
                    stop=None,
                    target=None,
                    reference=impulse,
                    trigger=pullback,
                    values={"confirmation_mode": "five_minute_close", "bias_compatible": None, "pocket_required": True},
                    geometry={"pocket": {"low": pocket[0], "high": pocket[1]}},
                )
            )
            continue
        stop = near
        target = impulse["high"] if trade_side == "long" else impulse["low"]
        extra = [
            _stage(
                "confirmation",
                "pass",
                int(confirm["at_ns"]),
                mode="five_minute_close",
                mode_od=True,
                close_out_of_pocket=True,
                confirm_close=confirm.get("close"),
                near=near,
                far=far,
                pocket_low=pocket[0],
                pocket_high=pocket[1],
                continuation_hold=True,
                ny_pullback=ny_pullback,
            )
        ]
        episodes.append(
            _finish_level_trade(
                market,
                family=family,
                branch=branch,
                side=trade_side,
                ref=impulse,
                level=near,
                sweep=pullback,
                confirm=confirm,
                mode="five_minute_close",
                stop=stop,
                target=target,
                rule_ids=("RR-14-golden-pocket", "F06-A4-pocket", "RR-12-risk-exits", "F01-scalp-observations"),
                extra_values={
                    "pocket_required": True,
                    "stop_at_near_edge": True,
                    "far_edge_stop_variant": False,
                    "impulse_not_9_10_box": True,
                    "pocket_low": pocket[0],
                    "pocket_high": pocket[1],
                },
                extra_stages=extra,
            )
        )
    return episodes


def _scan_vwap(market) -> list[dict[str, Any]]:
    asia_spec = asia_box_spec(market.day)
    london_spec = london_box_spec(market.day)
    a0, a1 = _box_ns(market, asia_spec)
    l0, l1 = _box_ns(market, london_spec)
    asia = _range(market, a0, a1, "asia-vwap")
    london = _range(market, l0, l1, "london-vwap")
    if asia is None or london is None:
        return [_unknown_ref_episode(market, "GB-VWAP", "source_long", "long", "session_reference_missing", ("F13-gb-vwap",))]
    boundary = max(_dec(asia["high"]), _dec(london["high"]))
    begin = max(int(market.at("09:30")), int(asia["known_at"]), int(london["known_at"]))
    rows = _safe_bars(market, begin, int(market.end), 300)
    breakout = None
    for row in rows:
        if not _bar_complete(row):
            continue
        if _dec(row["C"]) > boundary:
            breakout = row
            break
    ref = {"id": f"{asia.get('id')}+{london.get('id')}", "asia": asia, "london": london, "known_at": begin, "low": min(_dec(asia["low"]), _dec(london["low"])), "high": boundary}
    if breakout is None:
        stages = [
            _stage("context", "pass", begin, session="ny_am"),
            _stage("reference", "pass", begin, asia_high=asia["high"], london_high=london["high"]),
            _stage("location", "fail", begin, reason="no_close_above_both_highs", asia_high=asia["high"], london_high=london["high"]),
            _stage(
                "trigger",
                "fail",
                begin,
                reason="no_close_above_both_highs",
                close_above_both=False,
                asia_high=asia["high"],
                london_high=london["high"],
                breakout_close=None,
            ),
        ]
        return [
            _episode(
                market,
                family="GB-VWAP",
                branch="source_long",
                side="long",
                stages=stages,
                rules=_rules_for("F13-gb-vwap"),
                decision_at=begin,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=None,
                values={"confirmation_mode": "vwap_retest", "bias_compatible": None},
                geometry={},
            )
        ]
    break_end = int(breakout.get("end") or begin)
    rth_end = int(market.at("16:00")) if market.at("16:00") <= market.end else int(market.end)
    retest = None
    vw = None
    missing_coverage = False
    for row in _safe_bars(market, break_end, rth_end):
        try:
            snapshot = market.vwap(row["start"])
        except Exception:
            snapshot = {}
        price = _d((snapshot or {}).get("price"))
        lo, hi = _d(row.get("L")), _d(row.get("H"))
        if price is None:
            continue
        if lo is None or hi is None:
            missing_coverage = True
            continue
        if lo <= price <= hi:
            retest = row
            vw = snapshot
            break
    if retest is None:
        verdict_stage = "unknown" if missing_coverage else "fail"
        stages = [
            _stage("context", "pass", break_end, session="ny_am"),
            _stage("reference", "pass", begin, asia_high=asia["high"], london_high=london["high"]),
            _stage("location", "pass", break_end, breakout=True),
            _stage("trigger", "pass", break_end, breakout=True, close=breakout.get("C"), boundary=boundary),
            _stage("confirmation", verdict_stage, rth_end, reason="no_retest_before_rth_close", horizon="rth_close", candidate_60m=False),
        ]
        return [
            _episode(
                market,
                family="GB-VWAP",
                branch="source_long",
                side="long",
                stages=stages,
                rules=_rules_for("F13-gb-vwap"),
                decision_at=rth_end,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=breakout,
                values={
                    "confirmation_mode": "vwap_retest",
                    "continuation_context": True,
                    "retest_horizon": "rth_close",
                    "bias_compatible": None,
                },
                geometry={"retest_horizon": "rth_close", "census_unknowns_explained_by": "unspecified_retest_horizon"},
            )
        ]
    decision = int(retest.get("known_at") or retest.get("end") or break_end)
    vwap_px = _d((vw or {}).get("price"))
    entry = _d(retest.get("C")) or vwap_px
    retest_low, retest_high = _d(retest.get("L")), _d(retest.get("H"))
    breakout_close = _d(breakout.get("C"))
    asia_high, london_high = _dec(asia["high"]), _dec(london["high"])
    touched_vwap = vwap_px is not None and retest_low is not None and retest_high is not None and retest_low <= vwap_px <= retest_high
    held = entry is not None and entry > boundary
    if not (touched_vwap and held):
        stages = [
            _stage("context", "pass", break_end, session="ny_am"),
            _stage("reference", "pass", begin, asia_high=asia["high"], london_high=london["high"]),
            _stage("location", "pass", break_end, breakout=True, breakout_close=breakout_close, boundary=boundary),
            _stage("trigger", "pass", break_end, close_above_both=True, breakout_close=breakout_close, boundary=boundary),
            _stage(
                "confirmation",
                "fail",
                decision,
                reason="retest_lost_breakout" if touched_vwap and not held else "vwap_touch_not_held",
                vwap=vwap_px,
                retest_close=entry,
                boundary=boundary,
                touched_vwap=touched_vwap,
                continuation_hold=held,
                horizon="rth_close",
            ),
        ]
        return [
            _episode(
                market,
                family="GB-VWAP",
                branch="source_long",
                side="long",
                stages=stages,
                rules=_rules_for("F13-gb-vwap"),
                decision_at=decision,
                entry=None,
                stop=None,
                target=None,
                reference=ref,
                trigger=breakout,
                values={"confirmation_mode": "vwap_retest", "continuation_context": True, "bias_compatible": None},
                geometry={"retest_horizon": "rth_close"},
            )
        ]
    stop = (entry - VWAP_STOP_POINTS) if entry is not None else None
    target = entry + VWAP_TARGET_POINTS if entry is not None else None
    extra = [
        _stage(
            "confirmation",
            "pass",
            decision,
            mode="vwap_retest",
            vwap=vwap_px,
            retest_low=retest_low,
            retest_high=retest_high,
            breakout_close=breakout_close,
            asia_high=asia_high,
            london_high=london_high,
            horizon="rth_close",
            touched_vwap=True,
            continuation_hold=True,
            retest_close=entry,
            boundary=boundary,
        )
    ]
    extra_trigger = [
        _stage(
            "trigger",
            "pass",
            break_end,
            breakout_close=breakout_close,
            asia_high=asia_high,
            london_high=london_high,
            close_above_both=bool(
                breakout_close is not None and breakout_close > asia_high and breakout_close > london_high
            ),
        )
    ]
    return [
        _finish_level_trade(
            market,
            family="GB-VWAP",
            branch="source_long",
            side="long",
            ref=ref,
            level=vwap_px or entry,
            sweep=breakout,
            confirm={
                "at_ns": decision,
                "close": entry,
                "bar": retest,
                "inside_box": True,
                "fail_to_continue": True,
                "through": True,
                "sweep_depth": None if breakout_close is None else breakout_close - boundary,
                "sweep_extreme": _d(breakout.get("H")),
            },
            mode="vwap_retest",
            stop=stop,
            target=target,
            rule_ids=("F13-gb-vwap", "F07-directional-bias", "RR-12-risk-exits"),
            extra_values={
                "continuation_context": True,
                "retest_horizon": "rth_close",
                "vwap_at_retest": vwap_px,
                "example_stop_points_od": str(VWAP_STOP_POINTS),
                "example_target_points": str(VWAP_TARGET_POINTS),
                "example_target_points_variant_100": str(VWAP_TARGET_POINTS_VARIANT_100),
                "asia_high": asia_high,
                "london_high": london_high,
                "breakout_close": breakout_close,
            },
            extra_stages=extra + extra_trigger,
        )
    ]


def _scan_scalp_observation(market, branch: str) -> list[dict[str, Any]]:
    stages = [
        _stage("context", "pass", int(market.at("10:00")), session="ny_am"),
        _stage("reference", "fail", int(market.at("10:00")), reason="unpublished_entry", observation_only=True),
    ]
    return [
        _episode(
            market,
            family="GB-SCALP",
            branch=branch,
            side="short" if branch == "bearish_small_scalp" else "long",
            stages=stages,
            rules=_rules_for("F01-scalp-observations"),
            decision_at=int(market.at("10:00")),
            entry=None,
            stop=None,
            target=None,
            reference=None,
            trigger=None,
            values={"confirmation_mode": None, "bias_compatible": None},
            geometry={},
            scope="observation",
        )
    ]


def _scan_ny_session_extreme(market) -> list[dict[str, Any]]:
    """Afternoon sweep-and-fail of the 09:30–11:00 NY range after 11:00.

    Source addition 2026-09-15 trade 3: the author's NY marker is the 10:55
    session low (~29,215.5), swept at 15:35 to ~29,209, fail back inside.
    Freeze the range at 11:00. A later print that makes a new extreme is a
    break of that frozen level, not a new setup — the page does not support
    scanning every running extreme through the close.
    """
    begin = int(market.at("09:30"))
    freeze_at = int(market.at("11:00"))
    end = int(market.at("16:00")) if market.at("16:00") <= market.end else int(market.end)
    ref = _range(market, begin, freeze_at, "ny-session-0930-1100")
    if ref is None:
        return [_unknown_ref_episode(market, "GB-FAIL", "ny_session_extreme", "long", "ny_session_range_missing", ("RR-11-sessions-boxes",))]
    return _scan_box_at_level(
        market,
        branch="ny_session_extreme",
        ref=ref,
        begin=freeze_at,
        end=end,
        sides=("short", "long"),
        extra_values={
            "ny_session": True,
            "frozen_at": "11:00",
            "one_dated_example": "2026-09-15",
        },
    )


SCANNERS = {
    ("GB-FAIL", "london_box"): _scan_a1_london,
    ("GB-FAIL", "asia_box"): _scan_asia_high,
    ("GB-FAIL", "asia_tdo_case"): _scan_asia_tdo,
    ("GB-FAIL", "prior_day_level"): _scan_pdl,
    ("GB-FAIL", "nyam_box"): _scan_nyam,
    ("GB-FAIL", "previous_hour"): _scan_previous_hour,
    ("GB-FAIL", "nwog"): _scan_nwog,
    ("GB-FAIL", "cash_open_reclaim_case"): _scan_cash_open,
    ("GB-FAIL", "golden_pocket"): lambda m: _scan_golden_pocket(m, family="GB-FAIL", branch="golden_pocket", kinds=("down",)),
    ("GB-FAIL", "ny_session_extreme"): _scan_ny_session_extreme,
    ("GB-VWAP", "source_long"): _scan_vwap,
    ("GB-SCALP", "golden_pocket_continuation"): lambda m: _scan_golden_pocket(
        m, family="GB-SCALP", branch="golden_pocket_continuation", kinds=("up",)
    ),
}


def scan_b02(market, rec: Mapping[str, Any] | None = None, *, overrides=None) -> dict[str, Any]:
    def finish(doc):
        if not overrides:
            return doc
        from trading_research.research.rule_discovery.search import finish_scan_b02

        return finish_scan_b02(doc, overrides)

    rec = {key: value for key, value in dict(rec or {}).items() if key in REC_IDENTITY_KEYS or key in {"family", "method_id", "branch"}}
    family = rec.get("family") or rec.get("method_id") or "GB-FAIL"
    branch = rec.get("branch")
    branches = B02_BRANCHES.get(family, ())
    if branch in SCALP_OBSERVATIONS and family == "GB-SCALP":
        return finish(_document(market, family, branch, _scan_scalp_observation(market, branch)))
    selected = list(branches) if branch in {None, "*", "all", "B0.2"} else [branch]
    episodes: list[dict[str, Any]] = []
    omissions: list[dict[str, Any]] = []
    used = []
    for name in selected:
        fn = SCANNERS.get((family, name))
        if fn is None:
            omissions.append({"reason": "unknown_b02_branch", "branch": name})
            continue
        used.append(name)
        try:
            episodes.extend(fn(market))
        except Exception as exc:
            omissions.append({"reason": "scan_error", "branch": name, "error": f"{type(exc).__name__}: {exc}"})
    label = used[0] if len(used) == 1 else "B0.2"
    return finish(_document(market, family, label, episodes, omissions=omissions))


def _parse_windows(text: str | None, market) -> list[tuple[int, int]]:
    if not text:
        return [(int(market.start), int(market.end))]
    windows = []
    for part in text.replace("and", ",").split(","):
        chunk = part.strip()
        if "-" not in chunk:
            continue
        lo, hi = [item.strip() for item in chunk.split("-", 1)]
        def stamp(token: str) -> int | None:
            token = token.split("(")[0].strip()
            if len(token) == 5 and token[2] == ":":
                hour = int(token[:2])
                if hour >= 18:
                    return int(market.at(token, -1))
                return int(market.at(token))
            return None
        a, b = stamp(lo), stamp(hi)
        if a is None or b is None:
            continue
        if b <= a:
            b = b + 24 * 60 * MINUTE
        windows.append((a, b + MINUTE))
    return windows or [(int(market.start), int(market.end))]


def _drawn_author_level(example: Mapping[str, Any], side: str | None) -> Decimal | None:
    """Drawn chart levels, not live fills. Used only when no ticket price exists."""
    levels = example.get("levels") or {}
    pairs = ("box_9_10", "ny_box_9_10", "box_9_930", "box_10_11", "mss_fvg_boxes")
    if side == "short":
        for key in ("nyam_high", "am_high", "box_9_10_high", "asia_high"):
            raw = levels.get(key)
            if raw is not None and not isinstance(raw, (list, tuple, dict)):
                return _d(raw)
        for key in pairs:
            raw = levels.get(key)
            if isinstance(raw, (list, tuple)) and len(raw) >= 2 and not isinstance(raw[0], (list, tuple)):
                return _d(max(raw[0], raw[1]))
    if side == "long":
        for key in ("nyam_low", "box_9_10_low", "asia_low", "pdl", "london_low"):
            raw = levels.get(key)
            if raw is not None and not isinstance(raw, (list, tuple, dict)):
                return _d(raw)
        for key in pairs:
            raw = levels.get(key)
            if isinstance(raw, (list, tuple)) and len(raw) >= 2 and not isinstance(raw[0], (list, tuple)):
                return _d(min(raw[0], raw[1]))
    raw = levels.get("box_9_10")
    if isinstance(raw, (list, tuple)) and len(raw) >= 2 and not isinstance(raw[0], (list, tuple)):
        return _d(raw[1] if side == "short" else raw[0])
    return None


def _author_fill(example: Mapping[str, Any]) -> tuple[str | None, Decimal | None]:
    expected = example.get("expected_detection") or {}
    side = expected.get("side")
    if side in {"short", "long"}:
        pass
    elif isinstance(side, str) and "short" in side and "long" not in side.split("then")[0]:
        side = "short"
    elif isinstance(side, str) and side.startswith("long"):
        side = "long"
    else:
        side = None
    for action in example.get("actions") or []:
        if action.get("price") is None:
            continue
        act = action.get("action")
        if act in {"sell", "buy"}:
            mapped = "short" if act == "sell" else "long"
            if side in {None, mapped, "both"} or (isinstance(expected.get("side"), str) and mapped in expected.get("side")):
                return mapped, _d(action["price"])
    return side, None


def _level_close(a: Decimal | None, b: Decimal | None) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= LEVEL_TOLERANCE


def _date_outside_tape(example: Mapping[str, Any]) -> bool:
    if example.get("inside_tape") is False:
        return True
    try:
        day = date.fromisoformat(str(example.get("date") or "")[:10])
    except Exception:
        return True
    return day > TAPE_END


def replay_example(market, example: Mapping[str, Any]) -> dict[str, Any]:
    example = dict(example)
    if _date_outside_tape(example):
        author_side, author_level = _author_fill(example)
        return {
            "detected": None,
            "reached_location": None,
            "failing_stage": None,
            "failing_operand": None,
            "branch": None,
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": None if author_level is None else float(author_level),
            "author_side": author_side,
            "divergence": "date outside the tape",
            "example_id": example.get("id"),
        }
    family = str(example.get("family") or "GB-FAIL")
    families = []
    if "GB-SCALP" in family:
        families.append("GB-SCALP")
    if "GB-VWAP" in family:
        families.append("GB-VWAP")
    if "GB-FAIL" in family or not families:
        families.append("GB-FAIL")
    episodes = []
    for item in families:
        doc = scan_b02(market, {"family": item, "branch": "all"})
        episodes.extend(doc.get("episodes") or [])
    expected = example.get("expected_detection") or {}
    author_side, author_level = _author_fill(example)
    windows = _parse_windows(expected.get("entry_window_et"), market)
    want_branch = str(expected.get("branch") or "")
    def _ep_level(ep: Mapping[str, Any]) -> Decimal | None:
        return _d((ep.get("values") or {}).get("reference_px")) or _d((ep.get("geometry") or {}).get("entry"))

    def _location_ok(ep: Mapping[str, Any]) -> bool:
        for row in ep.get("stages") or []:
            if row.get("stage") == "location":
                return row.get("verdict") == "pass"
        return False

    def _failing(ep: Mapping[str, Any] | None) -> tuple[str, str]:
        if ep is None:
            return "location", "no_episode_at_author_level"
        if ep.get("research_verdict") == "pass":
            return "detection", "window_or_branch_mismatch"
        for row in ep.get("stages") or []:
            if row.get("verdict") in {"fail", "unknown"}:
                ops = row.get("operands") or {}
                named = ops.get("reason") or ops.get("mode") or next(iter(ops), None)
                if named is None:
                    named = row.get("verdict")
                return str(row.get("stage") or "stage"), str(named)
        return "verdict", str(ep.get("research_verdict") or "not_pass")

    author_levels = [author_level] if author_level is not None else []
    for raw in (example.get("levels") or {}).values():
        candidates = []
        if isinstance(raw, (int, float, Decimal)):
            candidates = [raw]
        elif isinstance(raw, str):
            try:
                candidates = [Decimal(raw)]
            except Exception:
                candidates = []
        elif isinstance(raw, (list, tuple)) and raw and not isinstance(raw[0], (list, tuple)):
            candidates = list(raw[:2])
        for item in candidates:
            try:
                got = _d(item)
            except Exception:
                continue
            if got is not None:
                author_levels.append(got)

    def _any_level(our_level: Decimal | None) -> bool:
        if our_level is None or not author_levels:
            return True
        return any(_level_close(our_level, item) for item in author_levels if item is not None)

    location_hits = []
    matches = []
    for ep in episodes:
        our_level = _ep_level(ep)
        side = ep.get("side")
        loc_ok = _any_level(our_level)
        fill_ok = author_level is None or our_level is None or _level_close(our_level, author_level)
        if author_side in {"long", "short"} and side != author_side and expected.get("side") not in {"both", "short then long", "long then short"}:
            if not (isinstance(expected.get("side"), str) and side in expected.get("side")):
                if not _location_ok(ep):
                    if not loc_ok:
                        continue
        if _location_ok(ep) and loc_ok:
            location_hits.append(ep)
        if ep.get("research_verdict") != "pass":
            continue
        if author_level is not None and our_level is not None and not fill_ok:
            continue
        entry_ns = ep.get("decision_at")
        if entry_ns is None or not any(a <= int(entry_ns) < b for a, b in windows):
            continue
        if want_branch and ep.get("branch") not in want_branch and want_branch.split()[0] not in (ep.get("branch") or ""):
            if "golden_pocket" in want_branch and "golden_pocket" in (ep.get("branch") or ""):
                pass
            elif "nyam_box" in want_branch and ep.get("branch") == "nyam_box":
                pass
            elif "asia" in want_branch and ep.get("branch") in {"asia_box", "asia_tdo_case", "prior_day_level"}:
                pass
            elif "london" in want_branch and ep.get("branch") == "london_box":
                pass
            elif "previous_hour" in want_branch and ep.get("branch") == "previous_hour":
                pass
            elif "ny_session_extreme" in want_branch and ep.get("branch") == "ny_session_extreme":
                pass
            else:
                continue
        matches.append(ep)

    def _loc_rank(ep: Mapping[str, Any]) -> tuple[int, str]:
        name = ep.get("branch") or ""
        if want_branch and name in want_branch:
            return (0, name)
        if want_branch and want_branch.split()[0] in name:
            return (1, name)
        return (2, name)

    location_hits.sort(key=_loc_rank)
    if not matches:
        loc = location_hits[0] if location_hits else None
        fail_stage, fail_op = _failing(loc)
        return {
            "detected": False,
            "reached_location": loc is not None,
            "failing_stage": fail_stage,
            "failing_operand": fail_op,
            "branch": None if loc is None else loc.get("branch"),
            "our_side": None if loc is None else loc.get("side"),
            "our_level": None if loc is None or _ep_level(loc) is None else float(_ep_level(loc)),
            "our_entry_ns": None if loc is None else loc.get("decision_at"),
            "author_level": None if author_level is None else float(author_level),
            "author_side": author_side,
            "divergence": "no_matching_episode" if loc is None else f"miss_after_location:{fail_stage}:{fail_op}",
            "example_id": example.get("id"),
        }
    best = matches[0]
    our_level = _d((best.get("values") or {}).get("reference_px")) or _d((best.get("geometry") or {}).get("entry"))
    divergence = ""
    reported_author = author_level
    if author_level is None:
        drawn = _drawn_author_level(example, best.get("side"))
        if drawn is None:
            divergence = "no author fill to compare"
        else:
            reported_author = drawn
            divergence = "drawn-not-live"
    return {
        "detected": True,
        "reached_location": True,
        "failing_stage": None,
        "failing_operand": None,
        "branch": best.get("branch"),
        "our_side": best.get("side"),
        "our_level": None if our_level is None else float(our_level),
        "our_entry_ns": best.get("decision_at"),
        "author_level": None if reported_author is None else float(reported_author),
        "author_side": author_side if author_side in {"long", "short"} else best.get("side"),
        "divergence": divergence,
        "example_id": example.get("id"),
    }


def funnel_from_document(document: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, dict[str, dict[str, int]]] = {}
    for ep in document.get("episodes") or []:
        branch = ep.get("branch") or document.get("branch")
        bucket = out.setdefault(branch, {name: {"pass": 0, "fail": 0, "unknown": 0} for name in STAGE_ORDER})
        for row in ep.get("stages") or []:
            name = row.get("stage")
            if name not in bucket:
                continue
            verdict = row.get("verdict") or "unknown"
            if verdict not in bucket[name]:
                verdict = "unknown"
            bucket[name][verdict] += 1
    return {
        "branch": document.get("branch"),
        "family": document.get("method_id"),
        "counts": {
            "pass": document.get("p"),
            "fail": document.get("f"),
            "unknown": document.get("u"),
            "episodes": document.get("N_observed"),
        },
        "bias": document.get("bias"),
        "stages": out,
    }


RULES: dict[str, dict[str, Any]] = {
    "RR-11-sessions-boxes": {
        "kind": "OD",
        "source": "OD:asia_box_windows,london_box_windows,ny_sub_boxes",
        "finding": "RR-11",
        "parameters": {
            "asia_variants": list(ASIA_VARIANTS),
            "asia_baseline_apr_aug": "20:00-23:00",
            "asia_baseline_sep": "20:00-00:00",
            "london_variants": list(LONDON_VARIANTS),
            "london_baseline": "02:00-05:00",
            "ny": ["09:00-10:00", "09:00-09:30", "10:00-11:00"],
            "ny_fail_scan": ["09:00-09:30", "09:00-10:00", "pm_sweep_910_high"],
            "ny_10_11_painted_live": "developing hour on Sep-2026 charts, not a third fail reference",
            "entry_windows": ["00:00-02:00", "20:00-23:00", "03:00-06:00", "09:30-11:30", "12:45-14:30"],
        },
        "_fn": asia_box_spec,
    },
    "F06-A1-london": {
        "kind": "literal",
        "source": "GB NG 2099513366326730859; GB p.60",
        "finding": "F06",
        "parameters": {
            "stop_retest_higher_low": "retest_higher_low_minus_tick",
            "stop_direct_reclaim": "sweep_extreme_plus_buffer",
            "sweep_buffer_points": str(SWEEP_STOP_BUFFER),
            "dated_retest": "2026-09-14",
            "dated_direct_reclaim": "2026-09-15",
        },
        "_fn": _scan_a1_london,
    },
    "F06-A2-asia": {
        "kind": "literal",
        "source": "GB pp.19, 27; NG 2099513366326730859",
        "finding": "F06",
        "_fn": _scan_asia_high,
    },
    "F06-A3-pdl": {
        "kind": "literal",
        "source": "GB pp.25, 48, 52-54; NG 2099503614372741234",
        "finding": "F06",
        "_fn": _scan_pdl,
    },
    "F06-A4-pocket": {
        "kind": "OD",
        "source": "OD:five_minute_close_out_of_pocket; stop_near_50_edge; far_edge_variant",
        "finding": "F06",
        "parameters": {"stop": "near_50_edge", "far_edge_variant": True, "confirmation": "five_minute_close_out"},
        "_fn": pocket_in_leg_direction,
    },
    "F06-A5-nwog": {
        "kind": "literal",
        "source": "GB p.37 and pp.23, 30-39",
        "finding": "F06",
        "_fn": _scan_nwog,
    },
    "RR-13-confirmation-modes": {
        "kind": "literal",
        "source": "GB pp.19, 25; RR-13 at-level box edges",
        "finding": "RR-13",
        "_fn": sweep_and_at_level,
    },
    "F07-directional-bias": {
        "kind": "OD",
        "source": "OD:prior_close_vs_range_midpoint,nyam_box_close_vs_open",
        "finding": "F07",
        "parameters": {
            "prior": "close vs prior RTH midpoint (value unpublished; midpoint registered)",
            "nyam_box": "09:00-10:00 close vs open, available only at/after 10:00",
            "no_daily_cap": True,
        },
        "_fn": directional_bias,
    },
    "RR-12-risk-exits": {
        "kind": "literal",
        "source": "GB pp.52-53, 56, 58, 60",
        "finding": "RR-12",
        "parameters": {"risk_dollars": 750, "ladder_spacing_od_baseline": 15, "author_spacing": [8, 33]},
        "_fn": limit_ladder,
    },
    "RR-14-golden-pocket": {
        "kind": "literal",
        "source": "GB pp.23, 25, 51; raw capture 2026-09-11",
        "finding": "RR-14",
        "_fn": pocket_in_leg_direction,
    },
    "RR-15-objective-horizon": {
        "kind": "literal",
        "source": "GB pp.51-54",
        "finding": "RR-15",
        "_fn": next_rth_open_ns,
    },
    "F13-gb-vwap": {
        "kind": "OD",
        "source": "OD:retest_horizon_rth_close; 60m_candidate",
        "finding": "F13",
        "parameters": {
            "retest_horizon": "rth_close",
            "no_retest": "fail",
            "candidate": "60m",
            "census_unknowns": 628,
            "example_stop_points": 30,
            "example_target_points": 150,
            "example_target_points_variant_100": 100,
        },
        "_fn": _scan_vwap,
    },
    "F01-scalp-observations": {
        "kind": "literal",
        "source": "GB p.40",
        "finding": "F01",
        "_fn": _scan_scalp_observation,
    },
    "F18-clock-seasonal-ny": {
        "kind": "literal",
        "source": "GB pp.43, 45, 48",
        "finding": "F18",
        "_fn": session_label,
    },
    "RR-12-position-size": {
        "kind": "literal",
        "source": "GB pp.52-53, 56, 58, 60",
        "finding": "RR-12",
        "parameters": {"amount": 750, "scored": False},
        "_fn": derived_quantity,
    },
}


def _bind_rule_lines() -> None:
    here = Path(__file__).name
    for row in RULES.values():
        fn = row.get("_fn")
        if fn is None:
            continue
        row["file_line"] = f"{here}:{inspect.getsourcelines(fn)[1]}"


_bind_rule_lines()
