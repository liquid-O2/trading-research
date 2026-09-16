"""P15-17 candidate machinery on the B0.2 scan. Stage A owns resolve, override, serialize."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
import bisect
import gzip
import json
import statistics
import time

from trading_research.errors import ContractError
from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.rule_discovery.registry import applicable as bank_applicable
from trading_research.research.rule_discovery.source_adapters.common import (
    coverage_id,
    install_write_guard,
    load_source_market,
)
from trading_research.research.rule_discovery.source_adapters.enumeration import ENUMERATION_KEY

_WORKTREE = Path(__file__).resolve().parents[5]
BANK_PATH = (
    _WORKTREE
    / "implementation/reports/research-work/P15-08/9728f9ee0bbbdfd5/attempt-0001/CANDIDATE_BANK.json"
)
P15_08_RECEIPT_PATH = (
    _WORKTREE
    / "implementation/reports/research-work/P15-08/9728f9ee0bbbdfd5/attempt-0001/TASK_RECEIPT.json"
)
R3_THROUGHPUT_PATH = _WORKTREE / "implementation/reports/research-work/P15-17/_track_r3/THROUGHPUT.json"
SPLIT_MANIFEST_PATH = (
    _WORKTREE / "implementation/reports/research-work/P15-03/babe7a991b6b3dc1/attempt-0001/SPLIT_MANIFEST.json"
)
EVALUATION_PROTOCOL_PATH = (
    _WORKTREE
    / "implementation/reports/research-work/P15-03/babe7a991b6b3dc1/attempt-0001/EVALUATION_PROTOCOL.json"
)

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
BANKS = ("Formation", "Profile", "Reference", "Delta", "Sequence", "Memory", "Timing")
# RA-2 axis-to-stage map, amended 2026-09-16 (P15-17 stage A finding 2).
# `phase` says WHEN the recipe runs: an enumeration axis runs before the adapter
# builds references and contacts and may change the contact population; an
# evaluation axis runs on the contacts B0.2 already enumerated.
AXIS_PHASE: dict[str, str] = {
    "Formation": "enumeration",
    "Reference": "enumeration",
    "Timing": "enumeration",
    "Profile": "evaluation",
    "Delta": "evaluation",
    "Sequence": "evaluation",
    "Memory": "evaluation",
}
AXIS_HOOKS: dict[str, tuple[str, ...]] = {
    "Formation": ("context", "reference", "location"),
    "Profile": ("reference",),
    "Reference": ("reference", "location"),
    "Delta": ("confirmation",),
    "Sequence": ("trigger", "confirmation"),
    "Memory": ("location",),
    "Timing": ("trigger", "location"),
}
# Enumeration points the axis needs the adapter to expose.
AXIS_ENUMERATION_POINTS: dict[str, tuple[str, ...]] = {
    "Formation": ("references",),
    "Reference": ("references",),
    "Timing": ("window",),
}
# Per-family stage scope for evaluation axes where the decision operand does not
# live on the axis's nominal stage.
FAMILY_AXIS_STAGES: dict[tuple[str, str], tuple[str, ...]] = {
    ("Profile", "KEANI-OPEN-ABOVE-VALUE"): ("context", "reference"),
}
# Enumeration points actually implemented in each B0.2 adapter branch.
ENUMERATION_SUPPORT: dict[str, dict[str, frozenset[str]]] = {
    "JJ-TBR": {
        "judas_reversal": frozenset({"references", "window"}),
        "other_session": frozenset({"references", "window"}),
        "single_extended": frozenset({"references", "window"}),
        "single_purged": frozenset({"references", "window"}),
        "internal_rotation": frozenset({"references", "window"}),
    },
    "GB-FAIL": {
        "nyam_box": frozenset({"references", "window"}),
        "previous_hour": frozenset({"references", "window"}),
        "asia_tdo_case": frozenset({"references", "window"}),
        "cash_open_reclaim_case": frozenset({"references", "window"}),
    },
    "GB-VWAP": {"source_long": frozenset({"references"})},
    "GB-SCALP": {
        "golden_pocket_continuation": frozenset({"references"}),
        "golden_pocket_reversal": frozenset({"references"}),
    },
    "SAINT-AMT": {
        "continuation_retest": frozenset({"references"}),
        "trapped_buyers_retest": frozenset({"references"}),
        "failed_auction_return": frozenset({"references"}),
        "poc_traversal": frozenset({"references"}),
    },
    "SIRES": {
        branch: frozenset({"references", "contacts"})
        for branch in (
            "absorption_reward_retest",
            "clean_squeeze",
            "defended_band_continuation",
            "vwap_deviation_fade",
            "kg1_retest",
            "microbalance_break",
        )
    },
}
GB_SCALP_OBSERVATIONS = frozenset({"bearish_small_scalp", "bullish_discount_pullback"})
PROCESS_FAMILIES = frozenset({"JETBUNDLE-STATES", "STOIC-DATA", "STOIC-RISK"})
B02_FAMILIES = (
    "JJ-TBR",
    "GB-FAIL",
    "GB-VWAP",
    "GB-SCALP",
    "SIRES",
    "SAINT-AMT",
    "MEMBER-TWO-REASONS",
    "KEANI-OPEN-ABOVE-VALUE",
    "REFILL-STUDY",
)
CONTROL_BRANCH: dict[str, str] = {
    "JJ-TBR": "judas_reversal",
    "GB-FAIL": "nyam_box",
    "GB-VWAP": "source_long",
    "GB-SCALP": "golden_pocket_continuation",
    "SIRES": "absorption_reward_retest",
    "SAINT-AMT": "continuation_retest",
    "MEMBER-TWO-REASONS": "planned_return_long",
    "KEANI-OPEN-ABOVE-VALUE": "source_long",
    "REFILL-STUDY": "touch_record",
}
CONTROL_DATES = ("2020-01-02", "2023-11-06", "2024-01-02")
THROUGHPUT_CANDIDATE_IDS = (
    "GB-FAIL:nyam_box:F1",
    "KEANI-OPEN-ABOVE-VALUE:source_long:P1",
    "GB-VWAP:source_long:R1",
    "SAINT-AMT:continuation_retest:C1",
    "SIRES:absorption_reward_retest:S1",
    "MEMBER-TWO-REASONS:planned_return_long:M1",
    "JJ-TBR:judas_reversal:T4",
)
NATIVE_VIEW_FAMILIES = frozenset({"SIRES", "REFILL-STUDY"})
TAPE_FIRST = "2020-01-02"
TAPE_LAST = "2026-08-19"
NS = 1_000_000_000
MINUTE_NS = 60 * NS

_BANK: dict[str, Any] | None = None


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_bank(path: Path | None = None) -> dict[str, Any]:
    global _BANK
    target = Path(path) if path is not None else BANK_PATH
    if _BANK is not None and path is None:
        return _BANK
    document = json.loads(target.read_text())
    document["_path"] = str(target)
    document["_sha256"] = file_sha256(target)
    if path is None:
        _BANK = document
    return document


@dataclass(frozen=True, slots=True)
class ResolvedCandidate:
    candidate_id: str
    family: str
    branch: str
    bank: str
    changed_axis: str
    recipe_id: str
    parameters: Mapping[str, Any]
    required_stages: tuple[str, ...]
    hooks: tuple[str, ...]
    phase: str
    applicable: bool
    supported: bool
    unsupported_reason: str | None
    coverage_id: str
    evidence: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "family": self.family,
            "branch": self.branch,
            "bank": self.bank,
            "changed_axis": self.changed_axis,
            "recipe_id": self.recipe_id,
            "parameters": dict(self.parameters),
            "required_stages": list(self.required_stages),
            "hooks": list(self.hooks),
            "phase": self.phase,
            "applicable": self.applicable,
            "supported": self.supported,
            "unsupported_reason": self.unsupported_reason,
            "coverage_id": self.coverage_id,
        }

    def freeze_row(self) -> dict[str, Any]:
        return {
            "applicable": self.applicable,
            "bank": self.bank,
            "branch": self.branch,
            "candidate_id": self.candidate_id,
            "changed_axis": self.changed_axis,
            "family": self.family,
            "hooks": list(self.hooks),
            "phase": self.phase,
            "parameters": dict(self.parameters),
            "recipe_id": self.recipe_id,
            "supported": self.supported,
            "unsupported_reason": self.unsupported_reason,
        }


def exposed_stages(family: str, branch: str) -> frozenset[str]:
    if family in PROCESS_FAMILIES:
        return frozenset()
    if family == "REFILL-STUDY":
        return frozenset({"reference", "location", "trigger", "confirmation", "risk", "objective"})
    if family == "GB-SCALP" and branch in GB_SCALP_OBSERVATIONS:
        return frozenset({"context", "reference"})
    if family in B02_FAMILIES:
        return frozenset(STAGE_ORDER)
    return frozenset()


def axis_phase(bank: str) -> str:
    if bank not in AXIS_PHASE:
        raise ContractError(f"unknown bank {bank}")
    return AXIS_PHASE[bank]


def axis_hooks(bank: str, family: str | None = None) -> tuple[str, ...]:
    if bank not in AXIS_HOOKS:
        raise ContractError(f"unknown bank {bank}")
    if family is not None and (bank, family) in FAMILY_AXIS_STAGES:
        return FAMILY_AXIS_STAGES[(bank, family)]
    return AXIS_HOOKS[bank]


def enumeration_points(family: str, branch: str) -> frozenset[str]:
    return ENUMERATION_SUPPORT.get(family, {}).get(branch, frozenset())


def resolve_candidate(row: Mapping[str, Any]) -> ResolvedCandidate:
    family = str(row["family"])
    branch = str(row["branch"])
    bank = str(row["bank"])
    recipe_id = str(row["recipe_id"])
    evidence = dict(row.get("evidence") or {})
    applicable = bool(evidence.get("applicable")) if "applicable" in evidence else bool(row.get("applicable"))
    hooks = axis_hooks(bank, family) if bank in AXIS_HOOKS else ()
    phase = AXIS_PHASE.get(bank, "evaluation")
    exposed = exposed_stages(family, branch)
    points = enumeration_points(family, branch)
    reason = None
    supported = True
    if family not in B02_FAMILIES:
        supported = False
        reason = f"no B0.2 scanner for {family}"
    elif not exposed:
        supported = False
        reason = f"adapter does not expose B0.2 stages for {family}:{branch}"
    elif phase == "enumeration":
        needed = AXIS_ENUMERATION_POINTS.get(bank, ())
        missing_points = [name for name in needed if name not in points]
        if missing_points:
            supported = False
            reason = (
                f"adapter exposes no {missing_points[0]} enumeration point for {family}:{branch}; "
                f"{bank} recipes apply before references and contacts are built "
                f"(implemented points {sorted(points)})"
            )
    else:
        missing = [name for name in hooks if name not in exposed]
        if missing:
            supported = False
            reason = (
                f"adapter does not expose stage {missing[0]} for {family}:{branch} "
                f"(hooks {list(hooks)}; exposed {sorted(exposed)})"
            )
    return ResolvedCandidate(
        candidate_id=str(row["candidate_id"]),
        family=family,
        branch=branch,
        bank=bank,
        changed_axis=str(row.get("changed_axis") or bank.lower()),
        recipe_id=recipe_id,
        parameters=dict(row.get("parameters") or {}),
        required_stages=tuple(row.get("required_stages") or ()),
        hooks=hooks,
        phase=phase,
        applicable=applicable,
        supported=supported,
        unsupported_reason=reason,
        coverage_id=coverage_id(family, branch),
        evidence=evidence,
    )


def resolve_bank(document: Mapping[str, Any] | None = None) -> list[ResolvedCandidate]:
    bank = document if document is not None else load_bank()
    return [resolve_candidate(row) for row in bank["candidates"]]


def b02_scanner(family: str):
    from trading_research.research.rule_discovery.source_adapters.common import _b02_scanner

    return _b02_scanner(family)


def load_b02_market(day: str, *, warm: bool = True, branches: Sequence[tuple[str, str]] = ()):
    """Load the account-day view once. `warm` also pays the per-session cost:
    the shared data plane, and -- for every (family, branch) in `branches` --
    that branch's cold B0.2 scan, so no candidate on the branch pays it."""
    if day < TAPE_FIRST or day > TAPE_LAST:
        raise ContractError(f"date {day} is outside the tape calendar {TAPE_FIRST}..{TAPE_LAST}")
    install_write_guard()
    market = load_source_market(day)
    from trading_research.research.rule_discovery.native import build_market_view

    try:
        market._native_view = build_market_view(day, full_account_day=True)
    except Exception:
        market._native_view = None
    if warm:
        market._p15_17_warm = warm_session(market, branches=branches)
    return market


def market_for_family(market, family: str):
    if family in NATIVE_VIEW_FAMILIES:
        return getattr(market, "_native_view", None) or market
    return market


def cutoff_ns(market) -> int:
    end = getattr(market, "end", None)
    if end is not None:
        return int(end)
    arrays = getattr(market, "arrays", None)
    if arrays is not None and getattr(arrays, "known_at_ns", None) is not None and arrays.known_at_ns.size:
        return int(arrays.known_at_ns.max())
    raise ContractError("market has no cutoff clock")


def check_causal_parameters(parameters: Mapping[str, Any], *, cutoff: int) -> None:
    for key, value in parameters.items():
        if key in {"peek_future", "future_dependent"} and value:
            raise ContractError(f"future-dependent recipe parameter {key}")
        if not str(key).endswith("_ns"):
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if int(value) > int(cutoff):
            raise ContractError(f"future-dependent parameter {key}={value} after cutoff {cutoff}")


def apply_scan_b02_overrides(document: Mapping[str, Any], overrides: Mapping[str, Any] | None) -> dict[str, Any]:
    if not overrides:
        return document if isinstance(document, dict) else dict(document)
    out = dict(document)
    episodes = []
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        stages = [dict(item) for item in row.get("stages") or []]
        replaced: list[dict[str, Any]] = []
        for stage in stages:
            name = str(stage.get("stage") or "")
            recipe = overrides.get(name)
            if recipe is None:
                replaced.append(stage)
                continue
            if not callable(recipe):
                raise ContractError(f"override for {name} is not a recipe implementation")
            replacement = recipe(stage=stage, episode=row, document=out)
            if not isinstance(replacement, Mapping) or str(replacement.get("stage")) != name:
                raise ContractError(f"override for {name} must return a stage record named {name}")
            replaced.append(dict(replacement))
        row["stages"] = replaced
        failed = [str(item["stage"]) for item in replaced if item.get("verdict") == "fail"]
        unknown = [str(item["stage"]) for item in replaced if item.get("verdict") == "unknown"]
        if failed:
            verdict = "fail"
        elif unknown:
            verdict = "unknown"
        else:
            verdict = "pass"
        row["research_verdict"] = verdict
        row["failed"] = failed
        row["unknown"] = unknown
        episodes.append(row)
    out["episodes"] = episodes
    if "p" in out or "f" in out or "u" in out or "n" in out:
        counts = {"pass": 0, "fail": 0, "unknown": 0}
        for episode in episodes:
            verdict = episode.get("research_verdict")
            if verdict in counts:
                counts[verdict] += 1
        out["p"] = counts["pass"]
        out["f"] = counts["fail"]
        out["u"] = counts["unknown"]
        out["n"] = counts["pass"] + counts["fail"]
        out["N_observed"] = len(episodes)
    return out


def finish_scan_b02(document: Mapping[str, Any], overrides: Mapping[str, Any] | None) -> dict[str, Any]:
    if not overrides:
        return document if isinstance(document, dict) else dict(document)
    return apply_scan_b02_overrides(document, overrides)


# --------------------------------------------------------------------------
# Per-session data plane. Every expensive primitive is computed once per
# session and shared by every candidate that asks for it with the same
# parameter tuple (P15-17 stage A finding 1).
# --------------------------------------------------------------------------


class SessionCache:
    """Memo bound to one loaded market view."""

    __slots__ = ("market", "_memo", "hits", "misses")

    def __init__(self, market):
        self.market = market
        self._memo: dict[tuple, Any] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: tuple, build: Callable[[], Any]):
        try:
            value = self._memo[key]
        except KeyError:
            self.misses += 1
            value = self._memo[key] = build()
        else:
            self.hits += 1
        return value

    def stats(self) -> dict[str, int]:
        return {"entries": len(self._memo), "hits": self.hits, "misses": self.misses}


def session_cache(market) -> SessionCache:
    cache = getattr(market, "_p15_17_cache", None)
    if isinstance(cache, SessionCache) and cache.market is market:
        return cache
    cache = SessionCache(market)
    try:
        market._p15_17_cache = cache
    except Exception:
        pass
    return cache


def _view_for_recipe(market):
    return getattr(market, "_native_view", None) or market


def _bars_view(market):
    if getattr(market, "bars", None) is not None:
        return market
    return _view_for_recipe(market)


def session_bars(market) -> dict[str, Any]:
    """Whole-session minute bars plus VWAP prefix sums, built once per session."""

    def build() -> dict[str, Any]:
        view = _bars_view(market)
        bars_fn = getattr(view, "bars", None)
        rows: list[dict[str, Any]] = []
        if bars_fn is not None:
            lo = int(getattr(view, "start", 0) or 0)
            hi = int(getattr(view, "end", 0) or 0)
            if hi > lo:
                for bar in bars_fn(lo, hi, 60):
                    end = int(bar.get("end") or bar.get("end_ns") or 0)
                    if end <= 0:
                        continue
                    start = int(bar.get("start") or bar.get("start_ns") or end)
                    volume = bar.get("V") if bar.get("V") is not None else bar.get("volume")
                    rows.append(
                        {
                            "start": start,
                            "end": end,
                            "H": None if bar.get("H") is None else Decimal(str(bar["H"])),
                            "L": None if bar.get("L") is None else Decimal(str(bar["L"])),
                            "C": None if bar.get("C") is None else Decimal(str(bar["C"])),
                            "O": None if bar.get("O") is None else Decimal(str(bar["O"])),
                            "V": None if volume is None else Decimal(str(volume)),
                        }
                    )
        ends = [row["end"] for row in rows]
        num = [Decimal("0")]
        den = [Decimal("0")]
        for row in rows:
            price, volume = row["C"], row["V"]
            if price is None or volume is None or volume <= 0:
                num.append(num[-1])
                den.append(den[-1])
            else:
                num.append(num[-1] + price * volume)
                den.append(den[-1] + volume)
        return {"rows": rows, "ends": ends, "vwap_num": num, "vwap_den": den}

    return session_cache(market).get(("session_bars",), build)


def _bar_bounds(market, start_ns: int, end_ns: int) -> tuple[int, int, dict[str, Any]]:
    table = session_bars(market)
    ends = table["ends"]
    lo = bisect.bisect_right(ends, int(start_ns))
    hi = bisect.bisect_right(ends, int(end_ns))
    return lo, max(lo, hi), table


def _iter_minute_bars(market, start_ns: int, end_ns: int):
    lo, hi, table = _bar_bounds(market, start_ns, end_ns)
    return table["rows"][lo:hi]


def _f1_geometry(market, issue_ns: int, minutes: int) -> dict[str, Any] | None:
    """Trailing `minutes` formation ending at issue_ns. Memoized per session."""

    def build() -> dict[str, Any] | None:
        start_ns = int(issue_ns) - int(minutes) * MINUTE_NS
        rows = [row for row in _iter_minute_bars(market, start_ns, issue_ns) if row["H"] is not None and row["L"] is not None]
        if not rows:
            return None
        window = rows[-int(minutes):] if len(rows) >= int(minutes) else rows
        return {
            "available": True,
            "complete": len(rows) >= int(minutes),
            "high": max(row["H"] for row in window),
            "low": min(row["L"] for row in window),
            "start_ns": window[0]["start"],
            "end_ns": window[-1]["end"],
            "minutes": len(window),
        }

    return session_cache(market).get(("f1", int(issue_ns), int(minutes)), build)


def _volume_completed_geometry(market, issue_ns: int, target_volume: Decimal | None, max_minutes: int) -> dict[str, Any] | None:
    """F2: walk back from issue_ns until the window has completed `target_volume`."""

    def build() -> dict[str, Any] | None:
        lo, hi, table = _bar_bounds(market, int(issue_ns) - int(max_minutes) * MINUTE_NS, issue_ns)
        rows = [row for row in table["rows"][lo:hi] if row["H"] is not None and row["L"] is not None]
        if not rows:
            return None
        goal = target_volume
        if goal is None or goal <= 0:
            goal = sum((row["V"] or Decimal("0")) for row in rows) / Decimal(max(len(rows), 1)) * Decimal(60)
        total = Decimal("0")
        window: list[dict[str, Any]] = []
        for row in reversed(rows):
            window.append(row)
            total += row["V"] or Decimal("0")
            if total >= goal:
                break
        window.reverse()
        return {
            "available": True,
            "complete": total >= goal,
            "high": max(row["H"] for row in window),
            "low": min(row["L"] for row in window),
            "start_ns": window[0]["start"],
            "end_ns": window[-1]["end"],
            "minutes": len(window),
            "volume": total,
        }

    key = ("f2", int(issue_ns), str(target_volume), int(max_minutes))
    return session_cache(market).get(key, build)


def _causal_balance_geometry(market, issue_ns: int, *, lengths: tuple[int, ...], width_mult: Decimal, efficiency: Decimal) -> dict[str, Any] | None:
    """F3: shortest trailing length that is balanced against the 60-minute scale."""

    def build() -> dict[str, Any] | None:
        scale = _f1_geometry(market, issue_ns, 60)
        if scale is None:
            return None
        reference_width = scale["high"] - scale["low"]
        for minutes in lengths:
            geo = _f1_geometry(market, issue_ns, minutes)
            if geo is None or not geo.get("complete"):
                continue
            width = geo["high"] - geo["low"]
            if reference_width > 0 and width > reference_width * width_mult:
                continue
            rows = _iter_minute_bars(market, int(issue_ns) - minutes * MINUTE_NS, issue_ns)
            opens = [row["O"] for row in rows if row["O"] is not None]
            closes = [row["C"] for row in rows if row["C"] is not None]
            if not opens or not closes or width <= 0:
                continue
            eff = abs(closes[-1] - opens[0]) / width
            if eff <= efficiency:
                return {**geo, "balanced": True, "efficiency": eff, "length_minutes": minutes}
        return None

    key = ("f3", int(issue_ns), lengths, str(width_mult), str(efficiency))
    return session_cache(market).get(key, build)


def vwap_between(market, start_ns: int, end_ns: int) -> Decimal | None:
    """Incremental account-day VWAP from the session prefix sums (O(log n))."""
    lo, hi, table = _bar_bounds(market, start_ns, end_ns)
    den = table["vwap_den"][hi] - table["vwap_den"][lo]
    if den <= 0:
        return None
    return (table["vwap_num"][hi] - table["vwap_num"][lo]) / den


def vwap_dispersion(market, start_ns: int, end_ns: int) -> Decimal | None:
    def build() -> Decimal | None:
        mean = vwap_between(market, start_ns, end_ns)
        if mean is None:
            return None
        rows = [row for row in _iter_minute_bars(market, start_ns, end_ns) if row["C"] is not None and row["V"] and row["V"] > 0]
        den = sum((row["V"] for row in rows), Decimal("0"))
        if den <= 0:
            return None
        var = sum(((row["C"] - mean) ** 2 * row["V"] for row in rows), Decimal("0")) / den
        return Decimal(str(float(var) ** 0.5))

    return session_cache(market).get(("vwap_sd", int(start_ns), int(end_ns)), build)


def _delta_prefix(market):
    """Prefix sums of signed size / volume / unknown size over the session."""

    def build():
        import numpy as np

        native = _view_for_recipe(market)
        arrays = getattr(native, "arrays", None)
        if arrays is None or getattr(arrays, "t_ns", None) is None or arrays.t_ns.size == 0:
            return None
        trade = getattr(arrays, "is_trade", None)
        mask = trade if trade is not None else np.ones(arrays.t_ns.size, dtype=bool)
        t_ns = arrays.t_ns[mask]
        side = arrays.side[mask].astype("int64")
        size = arrays.size[mask].astype("int64")
        signed = np.where(side > 0, size, np.where(side < 0, -size, 0))
        unknown = np.where(side == 0, size, 0)
        zero = np.zeros(1, dtype="int64")
        return {
            "t": t_ns,
            "signed": np.concatenate((zero, np.cumsum(signed))),
            "volume": np.concatenate((zero, np.cumsum(size))),
            "unknown": np.concatenate((zero, np.cumsum(unknown))),
        }

    return session_cache(market).get(("delta_prefix",), build)


def _delta_window(market, start_ns: int, end_ns: int) -> tuple[int, int, int] | None:
    import numpy as np

    state = _delta_prefix(market)
    if state is None:
        return None
    lo = int(np.searchsorted(state["t"], int(start_ns), side="left"))
    hi = int(np.searchsorted(state["t"], int(end_ns), side="right"))
    if hi <= lo:
        return None
    return (
        int(state["signed"][hi] - state["signed"][lo]),
        int(state["volume"][hi] - state["volume"][lo]),
        int(state["unknown"][hi] - state["unknown"][lo]),
    )


def _c1_at(market, end_ns: int, window_minutes: int) -> dict[str, Any] | None:
    from trading_research.research.rule_discovery.delta import c1_normalized

    def build():
        window = _delta_window(market, int(end_ns) - int(window_minutes) * MINUTE_NS, int(end_ns))
        if window is None:
            return None
        return c1_normalized(*window)

    return session_cache(market).get(("c1", int(end_ns), int(window_minutes)), build)


def _c2_at(market, end_ns: int, half_life_s: int) -> dict[str, Any] | None:
    """C2: exponentially weighted delta with the registered half life."""
    from trading_research.research.rule_discovery.delta import c1_normalized, decay_factor

    def build():
        span = max(int(half_life_s) * 6, int(half_life_s))
        buckets = []
        cursor = int(end_ns)
        for _ in range(6):
            window = _delta_window(market, cursor - int(half_life_s) * NS, cursor)
            buckets.append(window)
            cursor -= int(half_life_s) * NS
        signed = 0.0
        volume = 0.0
        unknown = 0.0
        for index, window in enumerate(buckets):
            if window is None:
                continue
            weight = decay_factor(index * int(half_life_s) * NS, half_life_ns=int(half_life_s) * NS)
            signed += weight * window[0]
            volume += weight * window[1]
            unknown += weight * window[2]
        if volume <= 0:
            return None
        out = c1_normalized(int(round(signed)), int(round(volume)), int(round(unknown)))
        out["half_life_s"] = int(half_life_s)
        out["span_s"] = span
        return out

    return session_cache(market).get(("c2", int(end_ns), int(half_life_s)), build)


def _c3_at(market, end_ns: int, window_minutes: int, buckets: int) -> dict[str, Any] | None:
    """C3: robust score of the current bucket against earlier same-session buckets."""
    from trading_research.research.rule_discovery.delta import c3_zscore

    def build():
        step = int(window_minutes) * MINUTE_NS
        history: list[float] = []
        cursor = int(end_ns) - step
        for _ in range(int(buckets)):
            window = _delta_window(market, cursor - step, cursor)
            if window is not None and window[1] > 0:
                history.append(window[0] / max(window[1] - window[2], 1))
            cursor -= step
        current = _delta_window(market, int(end_ns) - step, int(end_ns))
        if current is None or current[1] <= 0 or len(history) < 3:
            return None
        value = current[0] / max(current[1] - current[2], 1)
        out = dict(c3_zscore(value, history))
        out["available"] = True
        out["value"] = out.get("z")
        out["history_buckets"] = len(history)
        out["raw_ratio"] = value
        return out

    return session_cache(market).get(("c3", int(end_ns), int(window_minutes), int(buckets)), build)


def _profile_state(market):
    """Tick histogram cursor for the incremental value-area walk."""

    def build():
        import numpy as np

        native = _view_for_recipe(market)
        arrays = getattr(native, "arrays", None)
        if arrays is None or getattr(arrays, "price_ticks", None) is None or arrays.t_ns.size == 0:
            return None
        trade = getattr(arrays, "is_trade", None)
        mask = trade if trade is not None else np.ones(arrays.t_ns.size, dtype=bool)
        px = arrays.price_ticks[mask].astype("int64")
        if px.size == 0:
            return None
        base = int(px.min())
        width = int(px.max()) - base + 1
        return {
            "t": arrays.t_ns[mask],
            "bins": px - base,
            "size": arrays.size[mask].astype("int64"),
            "base": base,
            "width": width,
            "hist": np.zeros(width, dtype="int64"),
            "cursor": 0,
        }

    return session_cache(market).get(("profile_state",), build)


def _value_area(counts, *, base: int, fraction: Decimal, bandwidth: int) -> dict[str, Any] | None:
    import numpy as np

    weights = counts.astype("float64")
    if bandwidth > 0:
        kernel = np.arange(1, bandwidth + 2, dtype="float64")
        kernel = np.concatenate((kernel, kernel[-2::-1]))
        kernel = kernel / kernel.sum()
        weights = np.convolve(weights, kernel, mode="same")
    total = float(weights.sum())
    if total <= 0:
        return None
    poc = int(np.argmax(weights))
    lo = hi = poc
    inside = float(weights[poc])
    goal = float(fraction) * total
    while inside < goal and (lo > 0 or hi < weights.size - 1):
        left = float(weights[lo - 1]) if lo > 0 else -1.0
        right = float(weights[hi + 1]) if hi < weights.size - 1 else -1.0
        if right >= left:
            hi += 1
            inside += max(right, 0.0)
        else:
            lo -= 1
            inside += max(left, 0.0)
    tick = Decimal("0.25")
    return {
        "poc": Decimal(base + poc) * tick,
        "val": Decimal(base + lo) * tick,
        "vah": Decimal(base + hi) * tick,
        "total_volume": total,
        "achieved_fraction": inside / total,
        "bandwidth": int(bandwidth),
        "value_fraction": str(fraction),
    }


def profile_value_area(market, end_ns: int, *, bandwidth: int = 0, fraction: Decimal = Decimal("0.70")) -> dict[str, Any] | None:
    """Value area of the session tick profile up to end_ns, walked incrementally."""

    def build():
        import numpy as np

        state = _profile_state(market)
        if state is None:
            return None
        index = int(np.searchsorted(state["t"], int(end_ns), side="right"))
        if index <= 0:
            return None
        cursor = state["cursor"]
        if index >= cursor:
            if index > cursor:
                np.add.at(state["hist"], state["bins"][cursor:index], state["size"][cursor:index])
                state["cursor"] = index
            counts = state["hist"]
        else:
            counts = np.bincount(state["bins"][:index], weights=state["size"][:index], minlength=state["width"])
        return _value_area(counts, base=state["base"], fraction=fraction, bandwidth=int(bandwidth))

    return session_cache(market).get(("profile_va", int(end_ns), int(bandwidth), str(fraction)), build)


def prior_session_profile(market, *, bandwidth: int = 0, fraction: Decimal = Decimal("0.70")) -> dict[str, Any] | None:
    """Rebuild the prior completed session's value area on the SAME causal
    formation the source uses, with our own profile construction (P1 raw tick
    b0, P2 triangular b2). The prior window and its footprint rows are loaded
    once per session and shared by every Profile candidate."""

    def rows_build():
        try:
            prior = market.prior("day")
        except Exception:
            return None
        sessions = (prior or {}).get("sessions") or []
        if not sessions:
            return None
        window = sessions[-1]["window"]
        try:
            start = window.at("09:30")
            end = window.at("16:00")
        except Exception:
            start, end = getattr(window, "start", None), getattr(window, "end", None)
        if start is None or end is None:
            return None
        try:
            payload = window.profile(int(start), int(end))
        except Exception:
            return None
        rows = (payload or {}).get("rows") or []
        if not rows:
            return None
        return [(Decimal(str(row["price"])), Decimal(str(row["total_volume"]))) for row in rows]

    rows = session_cache(market).get(("prior_profile_rows",), rows_build)
    if not rows:
        return None

    def build():
        import numpy as np

        tick = Decimal("0.25")
        base = int(min(price for price, _ in rows) / tick)
        top = int(max(price for price, _ in rows) / tick)
        counts = np.zeros(top - base + 1, dtype="float64")
        for price, volume in rows:
            counts[int(price / tick) - base] += float(volume)
        return _value_area(counts, base=base, fraction=fraction, bandwidth=int(bandwidth))

    return session_cache(market).get(("prior_profile_va", int(bandwidth), str(fraction)), build)


def band_touches(market, low: Decimal, high: Decimal, end_ns: int) -> tuple[int | None, int, list[int]]:
    """Distinct completed contacts with [low, high] before end_ns."""

    def build():
        start_ns = int(getattr(_bars_view(market), "start", 0) or 0)
        first: int | None = None
        starts: list[int] = []
        inside = False
        for row in _iter_minute_bars(market, start_ns, end_ns):
            if row["L"] is None or row["H"] is None:
                continue
            touching = row["L"] <= high and row["H"] >= low
            if touching and not inside:
                starts.append(int(row["start"]))
                if first is None:
                    first = int(row["start"])
            inside = touching
        return first, len(starts), starts

    return session_cache(market).get(("touches", str(low), str(high), int(end_ns)), build)


def warm_session(market, *, branches: Sequence[tuple[str, str]] = (), strict: bool = False) -> dict[str, Any]:
    """Pay the per-session cost once, before any candidate runs.

    Two parts:

    * the shared data plane (minute bars with VWAP prefix sums, the delta prefix
      sums, the tick-profile cursor, the prior completed session);
    * the per-(family, branch) cold cost. Measured 2026-09-16: after the data
      plane alone, the FIRST B0.2 scan of KEANI-OPEN-ABOVE-VALUE:source_long
      still costs about 20 s and the second 0.06 s, because that scan drives 360
      `historical_features.profile` calls whose results are memoized on the
      market, not on our cache. The same holds, smaller, for other families
      (MEMBER planned_return_long 6.4 s then 0.07 s). The only way to prepay it
      is to run that family-branch's B0.2 scan once; it is the same work either
      way, and every candidate on the branch then reuses it. The baseline
      documents are returned so the caller does not scan them twice.

    No failure is swallowed silently. Each step's exception is recorded by name
    in `failures`; `strict=True` re-raises instead.
    """
    timings: dict[str, float] = {}
    failures: list[dict[str, str]] = []

    def run(name: str, fn):
        started = time.perf_counter()
        try:
            return fn()
        except Exception as exc:  # recorded, never silent
            failures.append({"step": name, "error": f"{type(exc).__name__}: {exc}"})
            if strict:
                raise
            return None
        finally:
            timings[name] = time.perf_counter() - started

    run("bars", lambda: session_bars(market))
    run("delta_prefix", lambda: _delta_prefix(market))
    run("profile_state", lambda: _profile_state(market))
    run("prior_session", lambda: prior_session_profile(market))
    data_plane_seconds = sum(timings.values())

    baselines: dict[tuple[str, str], dict[str, Any]] = {}
    started = time.perf_counter()
    for family, branch in branches:
        key = (str(family), str(branch))
        if key in baselines:
            continue
        document = run(f"branch:{family}:{branch}", lambda f=family, b=branch: scan_b02_baseline(market, f, b))
        if document is not None:
            baselines[key] = document
    prepay_seconds = time.perf_counter() - started

    return {
        "timings": timings,
        "failures": failures,
        "baselines": baselines,
        "data_plane_seconds": data_plane_seconds,
        "branch_prepay_seconds": prepay_seconds,
        "branches_prepaid": len(baselines),
    }


# --------------------------------------------------------------------------
# Enumeration-time recipes (Formation, Reference, Timing).
# These run BEFORE the adapter builds references and contacts, so they may
# change the contact population (count and ids).
# --------------------------------------------------------------------------


def _anchor_ns(payload, ctx, market) -> int:
    for key in ("begin", "end"):
        value = ctx.get(key)
        if value:
            return int(value)
    if isinstance(payload, Mapping):
        for key in ("known_at", "end", "end_ns"):
            value = payload.get(key)
            if value:
                return int(value)
    return int(getattr(_bars_view(market), "end", 0) or 0)


def _formation_geometry(resolved, market, anchor_ns: int, payload) -> dict[str, Any] | None:
    params = dict(resolved.parameters)
    recipe = resolved.recipe_id
    if recipe == "F1":
        return _f1_geometry(market, anchor_ns, int(params.get("minutes") or 60))
    if recipe == "F2":
        target = None
        if isinstance(payload, Mapping) and payload.get("volume") is not None:
            target = Decimal(str(payload["volume"]))
        return _volume_completed_geometry(market, anchor_ns, target, int(params.get("max_minutes") or 180))
    if recipe == "F3":
        lengths = tuple(int(item) for item in str(params.get("lengths") or "15,30,60").split(","))
        return _causal_balance_geometry(
            market,
            anchor_ns,
            lengths=lengths,
            width_mult=Decimal(str(params.get("width_mult") or "0.75")),
            efficiency=Decimal(str(params.get("efficiency") or "0.35")),
        )
    raise ContractError(f"unknown Formation recipe {recipe}")


def _apply_box_formation(resolved, market, payload, ctx) -> Any:
    if payload is None:
        return None
    anchor = _anchor_ns(payload, ctx, market)
    geo = _formation_geometry(resolved, market, anchor, payload)
    if geo is None or not geo.get("available"):
        return payload
    out = dict(payload)
    out["low"] = geo["low"]
    out["high"] = geo["high"]
    if "known_at" in out:
        out["known_at"] = int(geo["end_ns"])
    if "start" in out:
        out["start"] = int(geo["start_ns"])
    if "end" in out:
        out["end"] = int(geo["end_ns"])
    if out.get("id") is not None:
        out["id"] = f"{out['id']}+{resolved.recipe_id.lower()}"
    if "open" in out:
        out["open"] = geo["high"]
    out["formation_recipe"] = resolved.recipe_id
    return out


def _apply_sires_locations(resolved, market, payload, ctx) -> Any:
    if not payload:
        return payload
    cutoff = int(ctx.get("cutoff") or 0) or _anchor_ns(None, ctx, market)
    if resolved.bank == "Formation":
        geo = _formation_geometry(resolved, market, cutoff, None)
        if geo is None or not geo.get("available"):
            return payload
        lo = int(geo["low"] / Decimal("0.25"))
        hi = int(geo["high"] / Decimal("0.25"))
        kept = [row for row in payload if lo <= int(row.get("ticks") or 0) <= hi]
        return kept
    # Reference: replace the source locations with an account-day VWAP band pair.
    view = _bars_view(market)
    start = int(getattr(view, "start", 0) or 0)
    if resolved.recipe_id == "R2":
        prior = prior_session_profile(market)
        if prior is None:
            return payload
        levels = [("upper", prior["vah"]), ("lower", prior["val"])]
    else:
        mean = vwap_between(market, start, cutoff)
        sd = vwap_dispersion(market, start, cutoff)
        if mean is None or sd is None or sd <= 0:
            return payload
        levels = [("upper", mean + sd), ("lower", mean - sd)]
    known = int(payload[0].get("known_at_ns") or cutoff) if payload else cutoff
    return [
        {
            "kind": "vwap_band",
            "ticks": int(price / Decimal("0.25")),
            "known_at_ns": known,
            "role": role,
            "window": "session",
            "reference_recipe": resolved.recipe_id,
        }
        for role, price in levels
    ]


def _apply_gbvwap_reference(resolved, market, payload, ctx) -> Any:
    if not isinstance(payload, Mapping):
        return payload
    asia = dict(payload["asia"])
    london = dict(payload["london"])
    begin = max(int(asia.get("known_at") or 0), int(london.get("known_at") or 0))
    if resolved.recipe_id == "R1":
        view = _bars_view(market)
        start = int(getattr(view, "start", 0) or 0)
        mean = vwap_between(market, start, begin)
        sd = vwap_dispersion(market, start, begin)
        if mean is None or sd is None:
            return payload
        upper = mean + sd
        lower = mean - sd
    else:
        prior = prior_session_profile(market)
        if prior is None:
            return payload
        upper, lower = prior["vah"], prior["val"]
    asia["high"] = upper
    london["high"] = lower
    asia["reference_recipe"] = resolved.recipe_id
    london["reference_recipe"] = resolved.recipe_id
    return {"asia": asia, "london": london, "boundary": max(upper, lower)}


def _apply_timing_window(resolved, market, payload, ctx) -> Any:
    if not isinstance(payload, Mapping):
        return payload
    params = dict(resolved.parameters)
    recipe = resolved.recipe_id
    view = _bars_view(market)
    at = getattr(view, "at", None)
    flatten = int(getattr(view, "end", 0) or 0)
    if at is not None:
        try:
            flatten = min(flatten, int(at("16:00"))) or flatten
        except Exception:
            pass
    out = dict(payload)
    if recipe in {"T1", "T2"}:
        shift = int(params.get("shift_minutes") or 15) * MINUTE_NS
        for key in out:
            out[key] = int(out[key]) + shift
        if recipe == "T2":
            anchor = min(int(value) for value in payload.values())
            for key in out:
                out[key] = max(int(out[key]), anchor)
    elif recipe == "T3":
        if at is None:
            return payload
        try:
            lo, hi = int(at("09:30")), int(at("12:00"))
        except Exception:
            return payload
        for key in out:
            out[key] = lo if key.endswith("_lo") or key == "begin" else hi
    elif recipe == "T4":
        if at is None:
            return payload
        try:
            lo = int(at("09:30"))
        except Exception:
            return payload
        hi = flatten
        for key in out:
            out[key] = lo if key.endswith("_lo") or key == "begin" else hi
    else:
        raise ContractError(f"unknown Timing recipe {recipe}")
    return out


def build_enumeration_hook(resolved: "ResolvedCandidate", session):
    """Return the callable the adapter invokes at its enumeration points."""
    bank = resolved.bank

    def hook(*, point, payload, **ctx):
        ctx.pop("market", None)
        if point == "references":
            if bank == "Formation":
                if resolved.family == "SIRES":
                    return _apply_sires_locations(resolved, session, payload, ctx)
                return _apply_box_formation(resolved, session, payload, ctx)
            if bank == "Reference":
                if resolved.family == "SIRES":
                    return _apply_sires_locations(resolved, session, payload, ctx)
                if resolved.family == "GB-VWAP":
                    return _apply_gbvwap_reference(resolved, session, payload, ctx)
                return _apply_box_formation(resolved, session, payload, ctx)
            return payload
        if point == "window" and bank == "Timing":
            return _apply_timing_window(resolved, session, payload, ctx)
        return payload

    return hook


# --------------------------------------------------------------------------
# Stage-evaluation recipes (Profile, Delta, Sequence, Memory).
# These run on the contacts B0.2 has already enumerated; the contact set is
# unchanged and only stage records move.
# --------------------------------------------------------------------------

_GATE_KEYS = ("arrival_ok", "alignment_ok", "retest", "ltf_break", "held_retest", "eligible", "touch", "reclaim")
_BAND_KEYS = (("low", "high"), ("box_low", "box_high"), ("band_low", "band_high"), ("balance_low", "balance_high"))
_LEVEL_KEYS = ("level", "edge", "break_level", "reference_px", "location_ticks", "ticks", "origin_ticks", "prior_vah")


def _operand_decimal(operands: Mapping[str, Any], key: str) -> Decimal | None:
    value = operands.get(key)
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def episode_operands(episode: Mapping[str, Any]) -> dict[str, Any]:
    """Every operand the episode makes visible, for recipes whose own stage does
    not carry the contact level (SIRES trigger carries only opposite_absorbed;
    the level is on the location stage and the reference object)."""
    merged: dict[str, Any] = {}
    for stage in episode.get("stages") or []:
        for key, value in (stage.get("operands") or {}).items():
            merged.setdefault(key, value)
    reference = episode.get("reference")
    if isinstance(reference, Mapping):
        for key, value in reference.items():
            merged.setdefault(key, value)
    geometry = episode.get("geometry")
    if isinstance(geometry, Mapping):
        for key, value in geometry.items():
            merged.setdefault(key, value)
    return merged


def _stage_band(operands: Mapping[str, Any], fallback: Mapping[str, Any] | None = None) -> tuple[Decimal, Decimal] | None:
    for source in (operands, fallback or {}):
        for low_key, high_key in _BAND_KEYS:
            low = _operand_decimal(source, low_key)
            high = _operand_decimal(source, high_key)
            if low is not None and high is not None and high >= low:
                return low, high
        for key in _LEVEL_KEYS:
            level = _operand_decimal(source, key)
            if level is None:
                continue
            if key in {"location_ticks", "ticks", "origin_ticks"}:
                level = level * Decimal("0.25")
            return level - Decimal("0.25"), level + Decimal("0.25")
    return None


def _gate_verdict(operands: Mapping[str, Any]) -> str:
    gates = [bool(operands[key]) for key in _GATE_KEYS if key in operands and isinstance(operands[key], bool)]
    if not gates:
        return "pass"
    return "pass" if all(gates) else "fail"


def _profile_stage(resolved, market, out, operands, name, issue_ns) -> None:
    # P1/P2 rebuild the value reference from the raw tick tape of the account-day
    # view up to the stage's own known_at (the developing value), with bandwidth 0
    # (raw tick b0) or the triangular kernel b2. The source's object is the vendor
    # footprint aggregation of the prior completed session; this is the changed
    # profile construction, not a changed clock.
    bandwidth = int(dict(resolved.parameters).get("bandwidth") or 0)
    area = profile_value_area(market, issue_ns, bandwidth=bandwidth)
    if area is None:
        out["verdict"] = "unknown"
        operands["profile_reason"] = "no_observed_profile"
        return
    operands["profile_bandwidth"] = bandwidth
    operands["profile_recipe"] = resolved.recipe_id
    for key, value in (("prior_vah", area["vah"]), ("poc", area["poc"]), ("vah", area["vah"]), ("val", area["val"])):
        if key in operands:
            operands[key] = str(value)
    if "fully_above" in operands:
        a_low = _operand_decimal(operands, "a_low")
        fully = a_low is not None and a_low > area["vah"]
        operands["fully_above"] = fully
        out["verdict"] = "pass" if fully else ("unknown" if a_low is None else "fail")
    elif name in {"reference", "context"} and out.get("verdict") == "unknown":
        out["verdict"] = "pass"


def _delta_stage(resolved, market, out, operands, issue_ns) -> None:
    params = dict(resolved.parameters)
    recipe = resolved.recipe_id
    if recipe == "C1":
        result = _c1_at(market, issue_ns, int(params.get("window_minutes") or 5))
    elif recipe == "C2":
        result = _c2_at(market, issue_ns, int(params.get("half_life_s") or 300))
    else:
        result = _c3_at(market, issue_ns, 5, int(params.get("history_sessions") or 20))
    operands["delta_recipe"] = recipe
    if result is None or not result.get("available") or result.get("value") is None:
        out["verdict"] = "unknown"
        operands["delta_reason"] = (result or {}).get("reason") or "delta_unavailable"
        if "arrival_ok" in operands:
            operands["arrival_ok"] = False
        return
    value = float(result["value"])
    operands["delta_value"] = f"{value:.6f}"
    if "arrival_ratio" in operands:
        operands["arrival_ratio"] = f"{value:.6f}"
    threshold = float(params.get("threshold") or 0.0)
    if "arrival_ok" in operands:
        operands["arrival_ok"] = value >= threshold
    out["verdict"] = _gate_verdict(operands)


def _sequence_stage(resolved, market, out, operands, name, issue_ns, fallback) -> None:
    params = dict(resolved.parameters)
    recipe = resolved.recipe_id
    band = _stage_band(operands, fallback)
    operands["sequence_recipe"] = recipe
    if band is None:
        operands["sequence_reason"] = "no_level_operand"
        return
    low, high = band
    level = (low + high) / 2
    deadline = int(params.get("deadline_s") or params.get("cohort_s") or params.get("pressure_s") or 600)
    rows = [row for row in _iter_minute_bars(market, issue_ns, int(issue_ns) + deadline * NS) if row["C"] is not None]
    if not rows:
        operands["sequence_reason"] = "no_bars_in_deadline"
        out["verdict"] = "unknown"
        return
    ticks = Decimal(str(params.get("favorable_ticks") or 2)) * Decimal("0.25")
    if recipe == "S1":
        done = any(row["C"] > high for row in rows) or any(row["C"] < low for row in rows)
        operands["reclaimed"] = done
    elif recipe == "S2":
        broke = next((index for index, row in enumerate(rows) if row["C"] > high or row["C"] < low), None)
        done = False
        if broke is not None:
            after = rows[broke + 1:]
            done = bool(after) and all(abs(row["C"] - level) <= (high - low) + ticks for row in after[:5])
        operands["defended_retest"] = done
    elif recipe == "S3":
        reclaimed = any(row["C"] > high for row in rows) or any(row["C"] < low for row in rows)
        flow = _c1_at(market, int(issue_ns) + deadline * NS, max(1, deadline // 60))
        support = flow is not None and flow.get("value") is not None and abs(float(flow["value"])) >= float(params.get("c1") or 0.20)
        done = reclaimed and support
        operands["flow_supported"] = support
        operands["reclaimed"] = reclaimed
    else:  # S4 failure to progress
        progressed = any(row["C"] > high + ticks for row in rows) or any(row["C"] < low - ticks for row in rows)
        done = not progressed
        operands["failed_to_progress"] = done
    operands["sequence_at_ns"] = int(rows[-1]["end"])
    if name in {"trigger", "confirmation"}:
        out["verdict"] = "pass" if done else "fail"
        out["at_ns"] = int(rows[-1]["end"])


def _memory_stage(resolved, market, out, operands, issue_ns, fallback) -> None:
    params = dict(resolved.parameters)
    band = _stage_band(operands, fallback)
    operands["memory_recipe"] = resolved.recipe_id
    if band is None:
        operands["memory_reason"] = "no_band_operand"
        return
    low, high = band
    first, count, starts = band_touches(market, low, high, issue_ns)
    prior = max(0, count - 1)
    operands["prior_contacts"] = prior
    if resolved.recipe_id == "M1":
        limit = int(params.get("max_prior_contacts") or 1)
        operands["memory_limit"] = limit
        out["verdict"] = "fail" if prior > limit else _gate_verdict(operands)
    else:
        scale = (high - low) or Decimal("0.25")
        favorable = Decimal(str(params.get("prior_reaction") or "0.25").replace("S", "")) * scale
        reacted = False
        if first is not None:
            window = _iter_minute_bars(market, first, issue_ns)
            reacted = any(row["H"] is not None and row["H"] >= high + favorable for row in window) or any(
                row["L"] is not None and row["L"] <= low - favorable for row in window
            )
        operands["prior_favorable_reaction"] = reacted
        out["verdict"] = "pass" if (prior >= 1 and reacted) else "fail"
    if first is not None:
        out["at_ns"] = int(first)


def _replace_stage(stage: Mapping[str, Any], resolved: "ResolvedCandidate", *, episode: Mapping[str, Any], market) -> dict[str, Any]:
    out = dict(stage)
    operands = dict(out.get("operands") or {})
    name = str(stage.get("stage") or "")
    at_ns = stage.get("at_ns")
    issue_ns = int(at_ns) if at_ns is not None else int(episode.get("decision_at") or 0)
    bank = resolved.bank
    if bank == "Profile":
        _profile_stage(resolved, market, out, operands, name, issue_ns)
    elif bank == "Delta":
        _delta_stage(resolved, market, out, operands, issue_ns)
    elif bank == "Sequence":
        _sequence_stage(resolved, market, out, operands, name, issue_ns, episode_operands(episode))
    elif bank == "Memory":
        _memory_stage(resolved, market, out, operands, issue_ns, episode_operands(episode))
    else:
        raise ContractError(f"{bank} is an enumeration-time axis and has no stage recipe")
    out["operands"] = operands
    return out


def build_overrides(resolved: "ResolvedCandidate", market) -> dict[str, Any]:
    """Resolve a candidate to the override mapping scan_b02 accepts.

    Formation / Reference / Timing produce only the enumeration hook; Profile /
    Delta / Sequence / Memory produce only stage hooks (P15-17 stage A ruling,
    2026-09-16)."""
    if not resolved.supported:
        raise ContractError(resolved.unsupported_reason or f"{resolved.candidate_id} is unsupported")
    if axis_phase(resolved.bank) == "enumeration":
        return {ENUMERATION_KEY: build_enumeration_hook(resolved, market)}

    def make_hook(stage_name: str):
        def hook(*, stage, episode, document):
            return _replace_stage(stage, resolved, episode=episode, market=market)

        return hook

    return {name: make_hook(name) for name in resolved.hooks}


def scan_candidate(
    market,
    resolved: ResolvedCandidate,
    *,
    overrides: Mapping[str, Any] | None | object = None,
) -> dict[str, Any]:
    if not resolved.supported:
        raise ContractError(resolved.unsupported_reason or f"{resolved.candidate_id} is unsupported")
    check_causal_parameters(resolved.parameters, cutoff=cutoff_ns(market_for_family(market, resolved.family)))
    scanner = b02_scanner(resolved.family)
    rec = {
        "family": resolved.family,
        "method_id": resolved.family,
        "branch": resolved.branch,
        "coverage_id": resolved.coverage_id,
    }
    view = market_for_family(market, resolved.family)
    built = build_overrides(resolved, market) if overrides is None else overrides
    return scanner(view, rec, overrides=built)


def scan_b02_baseline(market, family: str, branch: str, *, with_overrides_kw: bool = False, overrides=None):
    scanner = b02_scanner(family)
    rec = {
        "family": family,
        "method_id": family,
        "branch": branch,
        "coverage_id": coverage_id(family, branch),
    }
    view = market_for_family(market, family)
    if with_overrides_kw:
        return scanner(view, rec, overrides=overrides)
    return scanner(view, rec)


def serialize_scan_bytes(document: Mapping[str, Any]) -> bytes:
    payload = json.dumps(hr.serializable(document), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return gzip.compress(payload, mtime=0)


def stage_records(document: Mapping[str, Any]) -> list[list[dict[str, Any]]]:
    return [[dict(item) for item in (episode.get("stages") or [])] for episode in document.get("episodes") or []]


def stage_diff_words(baseline: Mapping[str, Any] | None, candidate: Mapping[str, Any]) -> list[str]:
    if baseline is None:
        return []
    lines: list[str] = []
    left = list(baseline.get("episodes") or [])
    right = list(candidate.get("episodes") or [])
    n = min(len(left), len(right))
    if len(left) != len(right):
        lines.append(f"episode count {len(left)} -> {len(right)}")
    for index in range(n):
        by_left = {str(item.get("stage")): item for item in left[index].get("stages") or []}
        by_right = {str(item.get("stage")): item for item in right[index].get("stages") or []}
        for name in STAGE_ORDER:
            a = by_left.get(name)
            b = by_right.get(name)
            if a == b:
                continue
            if a is None and b is not None:
                lines.append(f"episode {index} added stage {name}")
                continue
            if a is not None and b is None:
                lines.append(f"episode {index} dropped stage {name}")
                continue
            av = (a or {}).get("verdict")
            bv = (b or {}).get("verdict")
            if av != bv:
                lines.append(f"episode {index} {name}: verdict {av} -> {bv}")
            ao = (a or {}).get("operands") or {}
            bo = (b or {}).get("operands") or {}
            keys = sorted(set(ao) | set(bo))
            changed = [key for key in keys if ao.get(key) != bo.get(key)]
            if changed:
                lines.append(f"episode {index} {name}: operands {', '.join(changed)}")
    return lines


def attach_candidate_fields(
    document: Mapping[str, Any],
    resolved: ResolvedCandidate,
    *,
    baseline: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    out = dict(document)
    out["candidate_id"] = resolved.candidate_id
    out["changed_axis"] = resolved.changed_axis
    out["recipe_id"] = resolved.recipe_id
    out["parameters"] = dict(resolved.parameters)
    out["stage_diff"] = stage_diff_words(baseline, document)
    out["search_family"] = resolved.family
    out["search_branch"] = resolved.branch
    out["search_bank"] = resolved.bank
    out["hooks"] = list(resolved.hooks)
    return out


def write_control_scan(root: Path, day: str, coverage: str, document: Mapping[str, Any]) -> Path:
    path = root / "B02_CONTROL_SCANS" / day / f"{coverage}.json.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(serialize_scan_bytes(document))
    return path


def negative_control_pair(market, family: str, branch: str) -> tuple[dict[str, Any], dict[str, Any], bool]:
    omitted = scan_b02_baseline(market, family, branch)
    none = scan_b02_baseline(market, family, branch, with_overrides_kw=True, overrides=None)
    return omitted, none, serialize_scan_bytes(omitted) == serialize_scan_bytes(none)


def r3_dates() -> list[str]:
    document = json.loads(R3_THROUGHPUT_PATH.read_text())
    return list(document["dates"])


def _percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (len(ordered) - 1) * p
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    frac = rank - lo
    return float(ordered[lo] * (1.0 - frac) + ordered[hi] * frac)


def measure_throughput(
    *,
    dates: Sequence[str] | None = None,
    candidate_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    days = list(dates) if dates is not None else r3_dates()
    wanted = list(candidate_ids) if candidate_ids is not None else list(THROUGHPUT_CANDIDATE_IDS)
    resolved_map = {item.candidate_id: item for item in resolve_bank()}
    resolved_list = []
    for cid in wanted:
        resolved = resolved_map[cid]
        if not resolved.supported:
            raise ContractError(f"throughput candidate unsupported: {cid}: {resolved.unsupported_reason}")
        resolved_list.append(resolved)
    scan_times: dict[str, list[float]] = {item.candidate_id: [] for item in resolved_list}
    load_times: list[float] = []
    for day in days:
        t_load = time.perf_counter()
        market = load_b02_market(day)
        load_times.append(time.perf_counter() - t_load)
        for resolved in resolved_list:
            t_scan = time.perf_counter()
            scan_candidate(market, resolved)
            scan_times[resolved.candidate_id].append(time.perf_counter() - t_scan)
    rows: list[dict[str, Any]] = []
    for resolved in resolved_list:
        samples = scan_times[resolved.candidate_id]
        rows.append(
            {
                "candidate_id": resolved.candidate_id,
                "family": resolved.family,
                "branch": resolved.branch,
                "bank": resolved.bank,
                "recipe_id": resolved.recipe_id,
                "hooks": list(resolved.hooks),
                "n_dates": len(days),
                "median_seconds": statistics.median(samples),
                "p90_seconds": _percentile(samples, 0.90),
                "mean_seconds": statistics.mean(samples),
                "per_date_scan_seconds": samples,
            }
        )
    p90 = max(row["p90_seconds"] for row in rows)
    median = statistics.median(row["median_seconds"] for row in rows)

    def project(workers: int) -> dict[str, Any]:
        hours = 160 * 1742 * p90 / (workers * 3600)
        return {
            "workers": workers,
            "hours": hours,
            "exceeds_24h_budget": hours > 24.0,
            "formula": "160 x 1,742 x p90 / (workers x 3600)",
            "p90_seconds": p90,
            "candidates": 160,
            "dates": 1742,
        }

    return {
        "schema_version": "research-p15-17-throughput-b02-v1",
        "dates": list(days),
        "candidates": rows,
        "load_median_seconds": statistics.median(load_times) if load_times else 0.0,
        "load_p90_seconds": _percentile(load_times, 0.90),
        "pipeline_median_seconds": median,
        "pipeline_p90_seconds": p90,
        "projection": {"workers_17": project(17), "workers_12": project(12)},
        "r3_gate": {
            "measured_p90_seconds": 1.484442432411015,
            "phase1_mean_seconds": 2.8859749833826815,
            "mean_multiple": 2.71,
            "gate_3x_vs_phase1": False,
            "status": "open engineering finding; freeze records measured values and does not shrink the bank, dates, or coverage",
            "residual": "parquet decode / load_span_arrow",
        },
        "cgroup_workers_floor": 17,
    }


def support_counts(resolved: Sequence[ResolvedCandidate]) -> dict[str, Any]:
    per_bank: dict[str, dict[str, int]] = {bank: {"supported": 0, "unsupported": 0} for bank in BANKS}
    per_family: dict[str, dict[str, int]] = {}
    reasons: list[dict[str, str]] = []
    for item in resolved:
        family = per_family.setdefault(item.family, {"supported": 0, "unsupported": 0})
        key = "supported" if item.supported else "unsupported"
        per_bank[item.bank][key] += 1
        family[key] += 1
        if not item.supported:
            reasons.append(
                {
                    "candidate_id": item.candidate_id,
                    "family": item.family,
                    "branch": item.branch,
                    "bank": item.bank,
                    "reason": item.unsupported_reason or "",
                }
            )
    return {"per_bank": per_bank, "per_family": per_family, "unsupported": reasons}


def scan_bank_session(market, resolved: Sequence["ResolvedCandidate"]) -> dict[str, Any]:
    """Evaluate a whole bank on one already loaded session. The account-day view
    and every memoized primitive are shared across candidates."""
    rows: list[dict[str, Any]] = []
    for item in resolved:
        if not item.supported:
            rows.append({"candidate_id": item.candidate_id, "supported": False, "seconds": 0.0})
            continue
        started = time.perf_counter()
        document = scan_candidate(market, item)
        rows.append(
            {
                "candidate_id": item.candidate_id,
                "family": item.family,
                "branch": item.branch,
                "bank": item.bank,
                "supported": True,
                "seconds": time.perf_counter() - started,
                "episodes": len(document.get("episodes") or []),
            }
        )
    return {"rows": rows, "seconds": sum(row["seconds"] for row in rows), "cache": session_cache(market).stats()}


def contact_ids(document: Mapping[str, Any]) -> list[str]:
    """Stable contact identity: branch, side and the located level. Deliberately
    excludes at_ns so that a recipe that only moves a clock on the SAME contact
    does not read as a different contact population."""
    counts: dict[str, int] = {}
    out: list[str] = []
    for index, episode in enumerate(document.get("episodes") or []):
        stages = {str(item.get("stage")): item for item in episode.get("stages") or []}
        located = stages.get("location") or stages.get("trigger") or stages.get("reference") or {}
        operands = located.get("operands") or {}
        marks = [
            f"{key}={operands.get(key)}"
            for key in ("level", "edge", "ticks", "location_ticks", "box_high", "box_low", "high", "low", "break_level", "zone_high")
            if operands.get(key) is not None
        ]
        key = "|".join(
            [
                str(episode.get("branch") or (episode.get("values") or {}).get("branch") or ""),
                str(episode.get("side") or ""),
                ",".join(marks) or f"episode{index}",
            ]
        )
        counts[key] = counts.get(key, 0) + 1
        out.append(f"{key}#{counts[key]}")
    return out


def verdict_vector(document: Mapping[str, Any]) -> list[str]:
    return [str(episode.get("research_verdict") or episode.get("verdict") or "") for episode in document.get("episodes") or []]


def stage_verdict_vector(document: Mapping[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for episode in document.get("episodes") or []:
        for stage in episode.get("stages") or []:
            out.append((str(stage.get("stage")), str(stage.get("verdict"))))
    return out


def verdict_changed(baseline: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    """A verdict change is an episode-level research_verdict difference, a stage
    verdict difference, or a change in the contact population."""
    base_ids = contact_ids(baseline)
    cand_ids = contact_ids(candidate)
    base_v = verdict_vector(baseline)
    cand_v = verdict_vector(candidate)
    base_s = stage_verdict_vector(baseline)
    cand_s = stage_verdict_vector(candidate)
    episode_changed = base_v != cand_v
    stage_changed = base_s != cand_s
    contacts_changed = base_ids != cand_ids
    return {
        "episode_verdict_changed": episode_changed,
        "stage_verdict_changed": stage_changed,
        "contacts_changed": contacts_changed,
        "changed": bool(episode_changed or stage_changed or contacts_changed),
        "baseline_contacts": len(base_ids),
        "candidate_contacts": len(cand_ids),
        "added_contacts": sorted(set(cand_ids) - set(base_ids))[:8],
        "dropped_contacts": sorted(set(base_ids) - set(cand_ids))[:8],
    }
