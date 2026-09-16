"""P15-17 candidate machinery on the B0.2 scan. Stage A owns resolve, override, serialize."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
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
AXIS_HOOKS: dict[str, tuple[str, ...]] = {
    "Formation": ("context", "reference"),
    "Profile": ("reference",),
    "Reference": ("reference",),
    "Delta": ("confirmation",),
    "Sequence": ("trigger", "confirmation"),
    "Memory": ("location",),
    "Timing": ("trigger",),
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


def axis_hooks(bank: str) -> tuple[str, ...]:
    if bank not in AXIS_HOOKS:
        raise ContractError(f"unknown bank {bank}")
    return AXIS_HOOKS[bank]


def resolve_candidate(row: Mapping[str, Any]) -> ResolvedCandidate:
    family = str(row["family"])
    branch = str(row["branch"])
    bank = str(row["bank"])
    recipe_id = str(row["recipe_id"])
    evidence = dict(row.get("evidence") or {})
    applicable = bool(evidence.get("applicable")) if "applicable" in evidence else bool(row.get("applicable"))
    hooks = axis_hooks(bank) if bank in AXIS_HOOKS else ()
    exposed = exposed_stages(family, branch)
    reason = None
    supported = True
    if family not in B02_FAMILIES:
        supported = False
        reason = f"no B0.2 scanner for {family}"
    elif not exposed:
        supported = False
        reason = f"adapter does not expose B0.2 stages for {family}:{branch}"
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


def load_b02_market(day: str):
    if day < TAPE_FIRST or day > TAPE_LAST:
        raise ContractError(f"date {day} is outside the tape calendar {TAPE_FIRST}..{TAPE_LAST}")
    install_write_guard()
    market = load_source_market(day)
    from trading_research.research.rule_discovery.native import build_market_view

    try:
        market._native_view = build_market_view(day, full_account_day=True)
    except Exception:
        market._native_view = None
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


def _view_for_recipe(market):
    return getattr(market, "_native_view", None) or market


def _iter_minute_bars(market, start_ns: int, end_ns: int):
    view = market
    bars_fn = getattr(view, "bars", None)
    if bars_fn is None:
        view = _view_for_recipe(market)
        bars_fn = getattr(view, "bars", None)
    if bars_fn is None:
        return
    lo = int(start_ns)
    hi = int(end_ns)
    origin = getattr(view, "start", None)
    finish = getattr(view, "end", None)
    if origin is not None:
        lo = max(lo, int(origin))
    if finish is not None:
        hi = min(hi, int(finish))
    if hi <= lo:
        return
    for bar in bars_fn(lo, hi, 60):
        yield bar


def _f1_geometry(market, issue_ns: int, minutes: int) -> dict[str, Any] | None:
    start_ns = int(issue_ns) - int(minutes) * MINUTE_NS
    highs: list[Decimal] = []
    lows: list[Decimal] = []
    starts: list[int] = []
    ends: list[int] = []
    for bar in _iter_minute_bars(market, start_ns, issue_ns):
        end = int(bar.get("end") or bar.get("end_ns") or 0)
        if end <= 0 or end > int(issue_ns):
            continue
        high = bar.get("H")
        low = bar.get("L")
        if high is None or low is None:
            continue
        highs.append(Decimal(str(high)))
        lows.append(Decimal(str(low)))
        starts.append(int(bar.get("start") or bar.get("start_ns") or end))
        ends.append(end)
    if len(highs) < minutes:
        return None if not highs else {
            "available": True,
            "high": max(highs),
            "low": min(lows),
            "start_ns": starts[0],
            "end_ns": ends[-1],
        }
    window_h = highs[-minutes:]
    window_l = lows[-minutes:]
    return {
        "available": True,
        "high": max(window_h),
        "low": min(window_l),
        "start_ns": starts[-minutes],
        "end_ns": ends[-1],
    }


def _vwap_from_bars(market, start_ns: int, end_ns: int) -> Decimal | None:
    num = Decimal("0")
    den = Decimal("0")
    for bar in _iter_minute_bars(market, start_ns, end_ns):
        close = bar.get("C")
        volume = bar.get("V") if bar.get("V") is not None else bar.get("volume")
        if close is None or volume is None:
            continue
        vol = Decimal(str(volume))
        if vol <= 0:
            continue
        num += Decimal(str(close)) * vol
        den += vol
    if den <= 0:
        return None
    return num / den


def _c1_at(market, end_ns: int, window_minutes: int) -> dict[str, Any] | None:
    from trading_research.research.rule_discovery.delta import c1_normalized
    from trading_research.research.rule_discovery.native import python_cvd

    native = _view_for_recipe(market)
    arrays = getattr(native, "arrays", None)
    if arrays is None or getattr(arrays, "t_ns", None) is None or arrays.t_ns.size == 0:
        return None
    start_ns = int(end_ns) - int(window_minutes) * MINUTE_NS
    t_ns = arrays.t_ns
    mask = (t_ns >= start_ns) & (t_ns <= int(end_ns))
    sizes = [int(v) for v in arrays.size[mask]]
    sides = [int(v) for v in arrays.side[mask]]
    if not sizes:
        return None
    signed, volume, unknown = python_cvd(sizes, sides)
    return c1_normalized(signed, volume, unknown)


def _profile_poc(market, end_ns: int) -> Decimal | None:
    start_ns = int(getattr(market, "start", 0) or 0)
    try:
        profile = market.profile(start_ns, int(end_ns))
    except Exception:
        profile = None
    if not isinstance(profile, Mapping):
        return None
    poc = profile.get("poc")
    if poc is None:
        return None
    return Decimal(str(poc))


def _first_band_touch_ns(market, low: Decimal, high: Decimal, end_ns: int) -> tuple[int | None, int]:
    start_ns = int(getattr(market, "start", 0) or 0)
    first = None
    count = 0
    for bar in _iter_minute_bars(market, start_ns, end_ns):
        bar_low = bar.get("L")
        bar_high = bar.get("H")
        if bar_low is None or bar_high is None:
            continue
        if Decimal(str(bar_low)) <= high and Decimal(str(bar_high)) >= low:
            count += 1
            if first is None:
                first = int(bar.get("start") or bar.get("end") or 0)
    return first, count


def _replace_stage(stage: Mapping[str, Any], resolved: ResolvedCandidate, *, episode: Mapping[str, Any], market) -> dict[str, Any]:
    out = dict(stage)
    operands = dict(out.get("operands") or {})
    name = str(stage.get("stage") or "")
    at_ns = stage.get("at_ns")
    issue_ns = int(at_ns) if at_ns is not None else int(episode.get("decision_at") or 0)
    bank = resolved.bank
    recipe_id = resolved.recipe_id
    params = dict(resolved.parameters)

    if bank == "Formation" and recipe_id == "F1":
        minutes = int(params.get("minutes") or 60)
        formed = _f1_geometry(market, issue_ns, minutes)
        if formed and formed.get("available"):
            if name == "context":
                out["at_ns"] = int(formed["start_ns"])
            if name == "reference":
                if "box_low" in operands:
                    operands["box_low"] = str(formed["low"])
                if "box_high" in operands:
                    operands["box_high"] = str(formed["high"])
                if "level" in operands:
                    operands["level"] = str(formed["high"])
                out["at_ns"] = int(formed["end_ns"])
        elif formed is None and name == "context":
            out["verdict"] = "unknown"

    elif bank == "Profile" and recipe_id in {"P1", "P2"}:
        poc = _profile_poc(market, issue_ns)
        if poc is not None and "prior_vah" in operands:
            operands["prior_vah"] = str(poc)

    elif bank == "Reference" and recipe_id == "R1":
        start_ns = int(getattr(market, "start", 0) or 0)
        vwap = _vwap_from_bars(market, start_ns, issue_ns)
        if vwap is not None:
            disp = Decimal("1")
            if "asia_high" in operands:
                operands["asia_high"] = str(vwap + disp)
            if "london_high" in operands:
                operands["london_high"] = str(vwap - disp)

    elif bank == "Delta" and recipe_id == "C1":
        window = int(params.get("window_minutes") or 5)
        c1 = _c1_at(market, issue_ns, window)
        if c1 is None:
            out["verdict"] = "unknown"
        else:
            if "arrival_ratio" in operands and c1.get("value") is not None:
                operands["arrival_ratio"] = str(c1["value"])
            if c1.get("available") is False:
                out["verdict"] = "unknown"

    elif bank == "Sequence" and recipe_id in {"S1", "S2", "S3", "S4"}:
        deadline_s = int(params.get("deadline_s") or 600)
        if at_ns is not None:
            out["at_ns"] = int(at_ns) + deadline_s * NS

    elif bank == "Memory" and recipe_id == "M1":
        max_prior = int(params.get("max_prior_contacts") or 1)
        try:
            low = Decimal(str(operands["low"]))
            high = Decimal(str(operands["high"]))
        except Exception:
            low = high = None
        if low is not None and high is not None and issue_ns:
            first, count = _first_band_touch_ns(market, low, high, issue_ns)
            prior = max(0, count - 1)
            if prior > max_prior:
                out["verdict"] = "fail"
            if first is not None:
                out["at_ns"] = first

    elif bank == "Timing" and recipe_id == "T4":
        if "in_modal_window" in operands:
            operands["in_modal_window"] = True
        expiry_s = int(params.get("expiry_s_after_qual") or 3600)
        if at_ns is not None:
            out["at_ns"] = int(at_ns) + expiry_s * NS

    out["operands"] = operands
    return out


def build_overrides(resolved: ResolvedCandidate, market) -> dict[str, Callable[..., dict[str, Any]]]:
    if not resolved.supported:
        raise ContractError(resolved.unsupported_reason or f"{resolved.candidate_id} is unsupported")

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
