"""P15-16A saint-track B0.2 helpers. Not imported by B0/B0.1 paths."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

from trading_research.research.method_pack.empirical_market import clock

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
B02_VERSION = "B0.2-2026-09-15"
LEVEL_TOLERANCE_TICKS = 8
Q = Decimal("0.25")
MINUTE_NS = 60_000_000_000
SLICE_DATES = [
    "2020-01-02",
    "2021-01-04",
    "2022-01-03",
    "2023-01-03",
    "2024-01-02",
    "2025-01-02",
    "2026-01-02",
    "2023-11-06",
    "2026-09-03",
]
HASH_DATES = ["2021-01-04", "2022-01-03"]
TRACK_DIR = Path("/workspace/.worktrees/b02-saint/implementation/reports/research-work/P15-16A/_track_saint")
AUTHOR_EXAMPLES = Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json")
NQ_TICK_VALUE = Decimal("5")
FIXED_RISK_USD = Decimal("500")


def dec(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def stage(name: str, verdict: str | None, at_ns: int | None, operands: dict[str, Any]) -> dict[str, Any]:
    return {"stage": name, "verdict": verdict, "at_ns": at_ns, "operands": operands}


def stage_from(name: str, at_ns: int | None, operands: Mapping[str, Any], *, require: Sequence[str]) -> dict[str, Any]:
    """Derive pass/fail/unknown from operand values. None is unknown. False is fail."""
    verdict = "pass"
    payload = dict(operands)
    for key in require:
        if key not in payload:
            verdict = "unknown"
            break
        val = payload[key]
        if val is None:
            verdict = "unknown"
            break
        if val is False:
            verdict = "fail"
            break
    return stage(name, verdict, at_ns, payload)


def cascade_stages(stages: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Keep stages in order and stop after the first fail or unknown."""
    out: list[dict[str, Any]] = []
    for item in stages:
        out.append(dict(item))
        if item.get("verdict") in {"fail", "unknown"}:
            break
    return out


class FixtureMarket:
    """Overlay B0.2 fixtures without writing them onto the inner market."""

    def __init__(self, inner, extra: Mapping[str, Any] | None = None) -> None:
        object.__setattr__(self, "_inner", inner)
        base = dict(getattr(inner, "b02_fixtures", None) or {})
        object.__setattr__(self, "b02_fixtures", {**base, **dict(extra or {})})

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_inner"), name)


def export_rules(rules_table: Mapping[str, Mapping[str, Any]], functions_by_id: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for rule_id, spec in rules_table.items():
        fn = functions_by_id.get(rule_id)
        if fn is None:
            file_line = spec.get("file_line") or "unknown:0"
        else:
            file_line = f"{Path(fn.__code__.co_filename).name}:{fn.__code__.co_firstlineno}"
        row = {
            "rule_id": rule_id,
            "kind": spec["kind"],
            "source": spec["source"],
            "file_line": file_line,
        }
        for key in ("unresolved", "notes", "conflict"):
            if key in spec:
                row[key] = spec[key]
        rows.append(row)
    return rows


def parse_rec(rec, default_family: str, branches: Sequence[str]) -> tuple[str, tuple[str, ...]]:
    if rec is None:
        return default_family, tuple(branches)
    if isinstance(rec, str):
        return rec, tuple(branches)
    family = str(rec.get("family") or rec.get("method_id") or default_family)
    branch = rec.get("branch")
    if branch:
        return family, (str(branch),)
    return family, tuple(branches)


def market_day(market) -> date:
    day = getattr(market, "day", None)
    if isinstance(day, date):
        return day
    return date.fromisoformat(str(day))


def market_at(market, hhmm: str, *, offset: int = 0) -> int:
    overrides = getattr(market, "at_overrides", None) or {}
    key = f"{offset}:{hhmm}" if offset else hhmm
    if key in overrides:
        return int(overrides[key])
    at = getattr(market, "at", None)
    if callable(at):
        try:
            return int(at(hhmm, offset) if offset else at(hhmm))
        except TypeError:
            return int(at(hhmm))
    return int(clock(market_day(market) + timedelta(days=offset), hhmm))


def market_bars(market, start, end, seconds: int = 60) -> list[dict[str, Any]]:
    bars = getattr(market, "bars", None)
    if not callable(bars):
        return []
    try:
        rows = bars(int(start), int(end), seconds)
    except TypeError:
        rows = bars(int(start), int(end))
    return list(rows or [])


def bars_upto(bars: Sequence[Mapping[str, Any]], decision_at: int) -> list[dict[str, Any]]:
    out = []
    for row in bars:
        known = row.get("known_at") or row.get("end")
        if known is None:
            continue
        if int(known) <= int(decision_at):
            out.append(dict(row))
    return out


def first_touch(bars: Sequence[Mapping[str, Any]], lo, hi) -> dict[str, Any] | None:
    lo, hi = dec(lo), dec(hi)
    for row in bars:
        low, high = row.get("L"), row.get("H")
        if low is None or high is None:
            continue
        if dec(low) <= hi and dec(high) >= lo:
            return dict(row)
    return None


def sha256_json(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def fixtures(market) -> dict[str, Any]:
    raw = getattr(market, "b02_fixtures", None)
    if raw is None:
        return {}
    return dict(raw)


def as_balance(value, *, known_at: int | None = None, start: int | None = None) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict) and value.get("low") is not None and value.get("high") is not None:
        out = dict(value)
        out["low"] = dec(out["low"])
        out["high"] = dec(out["high"])
        out.setdefault("id", "fixture-balance")
        if known_at is not None:
            out.setdefault("known_at", known_at)
        if start is not None:
            out.setdefault("start", start)
        return out
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        lo, hi = dec(value[0]), dec(value[1])
        if lo > hi:
            lo, hi = hi, lo
        return {"id": "fixture-balance", "low": lo, "high": hi, "known_at": known_at, "start": start, "width": hi - lo}
    return None


def episode_doc(
    *,
    family: str,
    branch: str,
    side: str,
    market,
    verdict: str,
    failed: Sequence[str],
    unknown: Sequence[str],
    stages: Sequence[Mapping[str, Any]],
    rules: Sequence[Mapping[str, Any]],
    values: Mapping[str, Any],
    decision_at: int | None,
    reference: Mapping[str, Any] | None = None,
    trigger: Mapping[str, Any] | None = None,
    geometry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    day = market_day(market)
    return {
        "schema": "phase1-historical-episode-v2",
        "baseline_version": B02_VERSION,
        "method": family,
        "branch": branch,
        "side": side,
        "session_date": str(day),
        "instrument_id": getattr(market, "instrument_id", None),
        "decision_at": decision_at,
        "research_verdict": verdict,
        "verdict": verdict,
        "failed": list(failed),
        "unknown": list(unknown),
        "values": dict(values),
        "stages": [dict(item) for item in stages],
        "rules": [dict(item) for item in rules],
        "reference": dict(reference or {}),
        "trigger": dict(trigger or {}),
        "geometry": dict(geometry or {}),
        "source_contract_verdict": verdict,
    }


def window_doc(
    family: str,
    branch: str | None,
    market,
    episodes: Sequence[Mapping[str, Any]],
    rules: Sequence[Mapping[str, Any]],
    omissions: Sequence[Mapping[str, Any]] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    counts = {"pass": 0, "fail": 0, "unknown": 0}
    for episode in episodes:
        verdict = episode.get("verdict") or episode.get("research_verdict")
        if verdict in counts:
            counts[verdict] += 1
    coverage = {"observed_scope_complete": True}
    cov = getattr(market, "coverage", None)
    if callable(cov):
        try:
            coverage = cov(getattr(market, "start", 0), getattr(market, "end", 0))
        except Exception:
            coverage = {"observed_scope_complete": True}
    doc = {
        "schema_version": "research-family-b02-scan-v1",
        "baseline_version": B02_VERSION,
        "method_id": family,
        "family": family,
        "branch": branch,
        "session_date": str(market_day(market)),
        "instrument_id": getattr(market, "instrument_id", None),
        "episodes": list(episodes),
        "omissions": list(omissions or []),
        "rules": list(rules),
        "n": counts["pass"] + counts["fail"],
        "p": counts["pass"],
        "f": counts["fail"],
        "u": counts["unknown"],
        "N_observed": len(episodes),
        "coverage": coverage,
    }
    if extra:
        doc.update(dict(extra))
    return doc


def combine_verdict(stages: Sequence[Mapping[str, Any]]) -> tuple[str, list[str], list[str]]:
    failed: list[str] = []
    unknown: list[str] = []
    for item in stages:
        name = str(item.get("stage"))
        verdict = item.get("verdict")
        if verdict == "fail":
            failed.append(name)
        elif verdict == "unknown":
            unknown.append(name)
    if failed:
        return "fail", failed, unknown
    if unknown:
        return "unknown", failed, unknown
    return "pass", failed, unknown


def parse_hhmm(text: str) -> tuple[int, int] | None:
    match = re.match(r"^(\d{1,2}):(\d{2})$", text.strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def entry_window_ns(day: date, window_et: str | None) -> tuple[int | None, int | None]:
    if not window_et:
        return None, None
    text = str(window_et).strip().lower()
    if "session" in text or text in {"week", "later", "unknown"}:
        return None, None
    match = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", window_et)
    if not match:
        return None, None
    start = parse_hhmm(match.group(1))
    end = parse_hhmm(match.group(2))
    if start is None or end is None:
        return None, None
    return clock(day, f"{start[0]:02d}:{start[1]:02d}"), clock(day, f"{end[0]:02d}:{end[1]:02d}")


def account_day_for_example(example: Mapping[str, Any]) -> str | None:
    raw = example.get("date")
    if not raw or not re.match(r"^\d{4}-\d{2}-\d{2}$", str(raw)):
        return None
    day = date.fromisoformat(str(raw))
    session = str(example.get("session") or "").lower()
    actions = example.get("actions") or []
    hour = None
    for action in actions:
        time_et = str(action.get("time_et") or "")
        parsed = parse_hhmm(time_et)
        if parsed:
            hour = parsed[0]
            break
    if "asia" in session or (hour is not None and hour >= 18):
        return (day + timedelta(days=1)).isoformat()
    return day.isoformat()


def numbers_from(value) -> list[Decimal]:
    found: list[Decimal] = []
    if isinstance(value, (int, float, Decimal)):
        found.append(dec(value))
        return found
    if isinstance(value, (list, tuple)):
        for item in value:
            found.extend(numbers_from(item))
        return found
    if isinstance(value, dict):
        for item in value.values():
            found.extend(numbers_from(item))
        return found
    if isinstance(value, str):
        for match in re.findall(r"\d+(?:\.\d+)?", value.replace(",", "")):
            number = dec(match)
            if number >= 100:
                found.append(number)
    return found


def levels_close(a, b, ticks: int = LEVEL_TOLERANCE_TICKS) -> bool:
    if a is None or b is None:
        return False
    return abs(dec(a) - dec(b)) <= Q * ticks


def author_printed_fill(example: Mapping[str, Any]):
    """Author fill from the ticket. Not a balance edge."""
    for action in example.get("actions") or []:
        price = action.get("price")
        if price is not None:
            return dec(price)
    return None


def replay_match(document: Mapping[str, Any], example: Mapping[str, Any]) -> dict[str, Any]:
    expected = example.get("expected_detection") or {}
    author_side = expected.get("side")
    fill = author_printed_fill(example)
    author_level = float(fill) if fill is not None else None
    wanted_sides = set()
    if isinstance(author_side, str):
        for token in re.split(r"[^a-z]+", author_side.lower()):
            if token in {"long", "short"}:
                wanted_sides.add(token)
    wanted_branch = str(expected.get("branch") or "")
    window_et = expected.get("entry_window_et")
    try:
        day = date.fromisoformat(str(example.get("date") or document.get("session_date")))
    except Exception:
        day = date(2026, 1, 1)
    win_lo, win_hi = entry_window_ns(day, window_et)
    best = None
    matched = False
    for episode in document.get("episodes") or []:
        side = str(episode.get("side") or "")
        branch = str(episode.get("branch") or "")
        if wanted_sides and side not in wanted_sides:
            continue
        if wanted_branch:
            tokens = re.split(r"[^a-z0-9_]+", wanted_branch.lower())
            if tokens and not any(token and token in branch.lower() for token in tokens if token not in {"then", "the", "and"}):
                if "continuation" in wanted_branch.lower() and "continuation" not in branch and "trapped" not in branch:
                    continue
        geom = episode.get("geometry") or {}
        values = episode.get("values") or {}
        our_level = geom.get("entry") or values.get("entry")
        entry_ns = episode.get("decision_at") or values.get("entry_ns") or geom.get("entry_ns")
        window_hit = True
        if win_lo is not None and win_hi is not None and entry_ns is not None:
            window_hit = int(win_lo) <= int(entry_ns) <= int(win_hi)
        if fill is None:
            if best is None:
                best = episode
            continue
        if our_level is None or not levels_close(our_level, fill):
            if best is None:
                best = episode
            continue
        if not window_hit:
            if best is None:
                best = episode
            continue
        best = episode
        matched = True
        break
    if not (document.get("episodes") or []) and document.get("tape_missing"):
        return {
            "detected": None,
            "branch": wanted_branch or None,
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": author_level,
            "author_side": author_side,
            "divergence": "date outside tape",
        }
    if best is None:
        return {
            "detected": False,
            "branch": wanted_branch or None,
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": author_level,
            "author_side": author_side,
            "divergence": "miss" if fill is not None else "no printed fill",
        }
    geom = best.get("geometry") or {}
    values = best.get("values") or {}
    our_level = geom.get("entry") or values.get("entry")
    our_level_f = float(our_level) if our_level is not None else None
    if fill is None:
        detected = False
        divergence = "no printed fill"
    elif not matched:
        detected = False
        divergence = "level"
    else:
        detected = True
        divergence = "match"
    if wanted_sides and str(best.get("side")) not in wanted_sides:
        detected = False
        divergence = "side"
    return {
        "detected": detected,
        "branch": best.get("branch"),
        "our_side": best.get("side"),
        "our_level": our_level_f,
        "our_entry_ns": best.get("decision_at"),
        "author_level": author_level,
        "author_side": author_side,
        "divergence": divergence,
    }


def funnel_counts(documents: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_branch: dict[str, dict[str, Any]] = {}
    for document in documents:
        branch = str(document.get("branch") or "all")
        row = by_branch.setdefault(
            branch,
            {
                "episodes": 0,
                "pass": 0,
                "fail": 0,
                "unknown": 0,
                "stages": {name: {"pass": 0, "fail": 0, "unknown": 0, "omitted": 0} for name in STAGE_ORDER},
            },
        )
        episodes = document.get("episodes") or []
        row["episodes"] += len(episodes)
        for episode in episodes:
            verdict = episode.get("verdict") or episode.get("research_verdict")
            if verdict in {"pass", "fail", "unknown"}:
                row[verdict] += 1
            present = {item.get("stage") for item in episode.get("stages") or []}
            for name in STAGE_ORDER:
                if name not in present:
                    row["stages"][name]["omitted"] += 1
            for item in episode.get("stages") or []:
                name = item.get("stage")
                verdict = item.get("verdict")
                if name in row["stages"] and verdict in {"pass", "fail", "unknown"}:
                    row["stages"][name][verdict] += 1
    return by_branch


def synth_bar(
    start_ns: int,
    o,
    h,
    l,
    c,
    *,
    delta=None,
    volume: int = 10,
    complete: bool = True,
    seconds: int = 60,
    bar_id: str | None = None,
) -> dict[str, Any]:
    end = int(start_ns) + int(seconds) * 1_000_000_000
    return {
        "start": int(start_ns),
        "end": end,
        "known_at": end,
        "O": dec(o),
        "H": dec(h),
        "L": dec(l),
        "C": dec(c),
        "V": volume,
        "delta": None if delta is None else dec(delta),
        "observed_complete": complete,
        "complete": complete,
        "bar_id": bar_id or f"bar:{start_ns}",
    }


class SynthMarket:
    def __init__(
        self,
        day,
        bars: Sequence[Mapping[str, Any]],
        *,
        start: int | None = None,
        end: int | None = None,
        fixtures: Mapping[str, Any] | None = None,
        prior: Mapping[str, Any] | None = None,
        profiles: Mapping[Any, Mapping[str, Any]] | None = None,
        at_overrides: Mapping[str, int] | None = None,
        footprints: Mapping[Any, Any] | None = None,
        instrument_id: Any = "NQ",
        weekly_high=None,
        domain: Mapping[str, Any] | None = None,
    ) -> None:
        self.day = date.fromisoformat(day) if isinstance(day, str) else day
        self._bars = [dict(row) for row in bars]
        self.start = int(start if start is not None else (self._bars[0]["start"] if self._bars else 0))
        self.end = int(end if end is not None else (self._bars[-1]["end"] if self._bars else 0))
        self.instrument_id = instrument_id
        self.reconstruct = False
        self.b02_fixtures = dict(fixtures or {})
        self.at_overrides = dict(at_overrides or {})
        self._prior = dict(prior or {"sessions": [], "omissions": [], "scope_complete": False, "range": None})
        self._profiles = dict(profiles or {})
        self._weekly_high = weekly_high
        self._domain = dict(domain or {})
        self.window = SimpleNamespace(document={"input_sha256": "synth"}, footprints=dict(footprints or {}))

    def at(self, text, offset=0):
        key = f"{offset}:{text}" if offset else text
        if key in self.at_overrides:
            return int(self.at_overrides[key])
        return int(clock(self.day + timedelta(days=int(offset or 0)), text))

    def bars(self, start, end, seconds=60):
        start, end = int(start), int(end)
        rows = []
        width = int(seconds) * 1_000_000_000
        for row in self._bars:
            if int(row["start"]) >= start and int(row["end"]) <= end:
                span = int(row["end"]) - int(row["start"])
                if seconds == 60 or span == width or seconds != 60:
                    rows.append(row)
        if seconds != 60 and rows and all(int(r["end"]) - int(r["start"]) == MINUTE_NS for r in rows):
            grouped = []
            bucket = []
            bucket_start = None
            for row in rows:
                if bucket_start is None:
                    bucket_start = int(row["start"])
                if int(row["start"]) >= bucket_start + width:
                    grouped.append(_coalesce(bucket, bucket_start, width))
                    bucket = [row]
                    bucket_start = int(row["start"])
                else:
                    bucket.append(row)
            if bucket:
                grouped.append(_coalesce(bucket, bucket_start, width))
            return grouped
        return rows

    def profile(self, start, end, fraction=".68"):
        key = (int(start), int(end), str(fraction))
        if key in self._profiles:
            return dict(self._profiles[key])
        for item in self._profiles.values():
            return dict(item)
        fx = self.b02_fixtures.get("developing_profile") or self.b02_fixtures.get("profile")
        if fx:
            return dict(fx)
        rows = self.bars(start, end)
        if not rows:
            return {"poc": None, "vah": None, "val": None, "rows": [], "known_at": end, "start": start, "end": end}
        levels: dict[Decimal, int] = {}
        for row in rows:
            px = dec(row["C"]) if row.get("C") is not None else dec(row["L"])
            levels[px] = levels.get(px, 0) + int(row.get("V") or 1)
        poc = max(levels, key=lambda px: (levels[px], -px))
        lo = min(dec(r["L"]) for r in rows)
        hi = max(dec(r["H"]) for r in rows)
        return {
            "poc": poc,
            "vah": hi,
            "val": lo,
            "low": lo,
            "high": hi,
            "rows": [{"price": px, "total_volume": vol} for px, vol in levels.items()],
            "known_at": end,
            "start": start,
            "end": end,
            "formation_start": start,
        }

    def prior(self, kind="day"):
        if kind == "week" and self._weekly_high is not None:
            payload = dict(self._prior)
            payload.setdefault("range", {"high": dec(self._weekly_high), "low": None})
            return payload
        return dict(self._prior)

    def range(self, start, end, label=None):
        rows = self.bars(start, end)
        if not rows:
            fx = self.b02_fixtures.get("a_period")
            if fx:
                return dict(fx)
            return None
        return {
            "id": f"{label}:{start}:{end}",
            "start": start,
            "end": end,
            "known_at": max(int(r["known_at"]) for r in rows),
            "low": min(dec(r["L"]) for r in rows),
            "high": max(dec(r["H"]) for r in rows),
            "open": rows[0]["O"],
            "close": rows[-1]["C"],
            "coverage": {"observed_scope_complete": True},
        }

    def coverage(self, start, end):
        return {"observed_scope_complete": True}

    def domain(self, rid, inputs):
        if rid in self._domain:
            return dict(self._domain[rid])
        fx = (self.b02_fixtures.get("domain") or {}).get(rid)
        if fx:
            return dict(fx)
        return {"buy_runs": []}


def _coalesce(bucket: list[dict[str, Any]], start: int, width: int) -> dict[str, Any]:
    end = start + width
    return {
        "start": start,
        "end": end,
        "known_at": max(int(r["known_at"]) for r in bucket),
        "O": bucket[0]["O"],
        "H": max(dec(r["H"]) for r in bucket),
        "L": min(dec(r["L"]) for r in bucket),
        "C": bucket[-1]["C"],
        "V": sum(int(r.get("V") or 0) for r in bucket),
        "delta": sum((dec(r["delta"]) if r.get("delta") is not None else Decimal(0)) for r in bucket),
        "observed_complete": all(r.get("observed_complete") or r.get("complete") for r in bucket),
        "complete": all(r.get("complete") or r.get("observed_complete") for r in bucket),
        "bar_id": f"agg:{start}",
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n")
