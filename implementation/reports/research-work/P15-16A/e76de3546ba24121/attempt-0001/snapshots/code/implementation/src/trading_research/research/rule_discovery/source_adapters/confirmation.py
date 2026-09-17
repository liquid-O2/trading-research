"""Evaluate a family's B0.1 confirmation stage at one contact.

Operands are read from HistoricalFeatures, the same market dual_scan uses.
Decision time is the confirming bar's known_at, or the family deadline.
Bars with known_at after that cutoff are not bound.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from trading_research.research.method_pack.catalog import PRIMARY
from trading_research.research.method_pack.expressions import evaluate
from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
from trading_research.research.method_pack.strategy_policy import EXCLUDED, observation_scope


@dataclass(frozen=True, slots=True)
class ConfirmationDecision:
    family: str
    branch: str
    contact_id: str
    research_verdict: str
    status: str
    values: dict[str, Any]
    failed: list[str]
    unknown: list[str]
    failed_conditions: list[str]
    unavailable_conditions: list[str]
    source_confirmation: bool | None
    decision_at_ns: int | None
    confirm_at_ns: int | None
    cutoff_ns: int | None
    extras: dict[str, Any] = field(default_factory=dict)


CONFIRMATION_RULE: dict[str, dict[str, Any]] = {
    "JJ-TBR": {"name": "O056 full-C2 _ob_repaired", "file": "baseline_repairs.py", "line": 547},
    "GB-FAIL": {"name": "first complete five-minute reclaim", "file": "baseline_repairs.py", "line": 836},
    "GB-VWAP": {"name": "later VWAP retest", "file": "baseline_repairs.py", "line": 951},
    "GB-SCALP": {"name": "scalp pullback bar", "file": "historical_process_scanners.py", "line": 1},
    "SIRES": {"name": "flow_stages selected stage", "file": "baseline_repairs.py", "line": 317},
    "SAINT-AMT": {"name": "two-bar body/delta control", "file": "historical_auction_scanners.py", "line": 16},
    "MEMBER-TWO-REASONS": {"name": "defense or rejection after contact", "file": "baseline_repairs.py", "line": 1140},
    "KEANI-OPEN-ABOVE-VALUE": {"name": "imbalance-band defense", "file": "baseline_repairs.py", "line": 1211},
    "REFILL-STUDY": {"name": "distinct return after departure", "file": "baseline_repairs.py", "line": 1284},
    "JETBUNDLE-STATES": {"name": "state observation", "file": "baseline_repairs.py", "line": 1},
    "STOIC-DATA": {"name": "process observation", "file": "baseline_repairs.py", "line": 1321},
    "STOIC-RISK": {"name": "printed ladder", "file": "baseline_repairs.py", "line": 1},
}


def px(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def bounds(reference: Mapping[str, Any] | None) -> tuple[Decimal | None, Decimal | None]:
    if not reference:
        return None, None
    lo = reference.get("low", reference.get("lower"))
    hi = reference.get("high", reference.get("upper"))
    return px(lo), px(hi)


def scanner_ref(reference: Mapping[str, Any] | None, formation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    lo, hi = bounds(reference)
    known = (reference or {}).get("known_at")
    if known is None:
        known = (reference or {}).get("issue_at_ns")
    if known is None and formation:
        known = formation.get("available_at_ns")
        if known is None:
            known = formation.get("end_ns")
    coverage = (reference or {}).get("coverage") or {"observed_scope_complete": True}
    complete = (reference or {}).get("complete")
    if complete is None:
        complete = lo is not None and hi is not None
    ident = (reference or {}).get("id") or (reference or {}).get("reference_id") or "candidate-ref"
    return {
        **dict(reference or {}),
        "id": ident,
        "low": lo,
        "high": hi,
        "known_at": known,
        "complete": complete,
        "coverage": coverage,
    }


def contact_as_trigger(market, contact: Mapping[str, Any]) -> dict[str, Any]:
    if contact.get("L") is not None and contact.get("start") is not None:
        row = dict(contact)
        for key in ("L", "H", "C", "O"):
            if row.get(key) is not None:
                row[key] = px(row[key])
        row.setdefault("observed_complete", bool(row.get("complete") or row.get("observed_complete")))
        row.setdefault("end", int(row["start"]) + MINUTE)
        row.setdefault("known_at", row.get("available_at_ns") or row["end"])
        return row
    start = int(contact.get("at_ns") or contact.get("start") or 0)
    end = int(contact.get("available_at_ns") or start + MINUTE)
    bars = list(market.bars(start, min(end + 1, int(market.end)))) if start else []
    if bars:
        bar = dict(bars[0])
        bar.setdefault("observed_complete", bool(bar.get("complete") or bar.get("observed_complete")))
        return bar
    low = px(contact.get("low"))
    high = px(contact.get("high"))
    close = px(contact.get("close"))
    return {
        "start": start,
        "end": end,
        "L": low,
        "H": high,
        "C": close,
        "known_at": end,
        "bar_id": contact.get("bar_id") or contact.get("contact_id"),
        "complete": bool(contact.get("complete", True)),
        "observed_complete": bool(contact.get("complete", True)),
    }


def contact_id_of(contact: Mapping[str, Any]) -> str:
    return str(contact.get("contact_id") or contact.get("bar_id") or contact.get("id") or contact.get("start") or "")


def contact_side(contact: Mapping[str, Any], values: Mapping[str, Any] | None = None) -> str:
    side = contact.get("side") or (values or {}).get("side") or "long"
    return str(side)


def range_frozen(ref: Mapping[str, Any]) -> bool | None:
    if ref.get("complete") and (ref.get("coverage") or {}).get("observed_scope_complete"):
        return True
    if ref.get("low") is not None and ref.get("high") is not None:
        return True if ref.get("complete") is not False else None
    return None


def _status_for(verdict: str, *, family: str, branch: str) -> str:
    scope = observation_scope(family, branch)
    if scope != "entry_setup":
        return {"pass": "condition_present", "fail": "condition_absent", "unknown": "data_unavailable"}[verdict]
    return {"pass": "setup", "fail": "no_setup", "unknown": "data_unavailable"}[verdict]


def finish_values(
    *,
    family: str,
    branch: str,
    contact: Mapping[str, Any],
    values: dict[str, Any],
    confirm_at: int | None,
    decision_at: int | None,
    cutoff_ns: int | None,
    post_fail: str | None = None,
) -> ConfirmationDecision:
    payload = dict(values)
    payload.setdefault("branch", branch)
    payload.setdefault("side", contact_side(contact, payload))
    if decision_at is not None:
        payload["decision_at"] = decision_at
    excluded = EXCLUDED.get(family, frozenset())
    result = evaluate(family, PRIMARY[family], payload, excluded_fields=excluded)
    verdict = {True: "pass", False: "fail", None: "unknown"}[result.value]
    failed = list(result.failed)
    unknown = list(result.unknown)
    if post_fail:
        verdict = "fail"
        if post_fail not in failed:
            failed.append(post_fail)
    status = _status_for(verdict, family=family, branch=branch)
    confirmation = payload.get("source_confirmation")
    if confirmation is None and "box_return_ok" in payload:
        confirmation = payload.get("box_return_ok")
    return ConfirmationDecision(
        family=family,
        branch=branch,
        contact_id=contact_id_of(contact),
        research_verdict=verdict,
        status=status,
        values=payload,
        failed=failed,
        unknown=unknown,
        failed_conditions=list(failed),
        unavailable_conditions=list(unknown),
        source_confirmation=None if confirmation is None else bool(confirmation),
        decision_at_ns=None if decision_at is None else int(decision_at),
        confirm_at_ns=None if confirm_at is None else int(confirm_at),
        cutoff_ns=None if cutoff_ns is None else int(cutoff_ns),
    )


def _family_confirm(family: str):
    if family == "JJ-TBR":
        from trading_research.research.rule_discovery.source_adapters.jumbo import confirm_at_contact
        return confirm_at_contact
    if family == "GB-FAIL":
        from trading_research.research.rule_discovery.source_adapters.green_failure import confirm_at_contact
        return confirm_at_contact
    if family in {"GB-VWAP", "GB-SCALP"}:
        from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import confirm_at_contact
        return confirm_at_contact
    if family == "SIRES":
        from trading_research.research.rule_discovery.source_adapters.sires import confirm_at_contact
        return confirm_at_contact
    if family == "SAINT-AMT":
        from trading_research.research.rule_discovery.source_adapters.saint import confirm_at_contact
        return confirm_at_contact
    if family == "MEMBER-TWO-REASONS":
        from trading_research.research.rule_discovery.source_adapters.member import confirm_at_contact
        return confirm_at_contact
    if family == "KEANI-OPEN-ABOVE-VALUE":
        from trading_research.research.rule_discovery.source_adapters.keani import confirm_at_contact
        return confirm_at_contact
    from trading_research.research.rule_discovery.source_adapters.processes import confirm_at_contact
    return confirm_at_contact


def evaluate_confirmation(
    market,
    *,
    family: str,
    branch: str,
    contact: Mapping[str, Any],
    reference: Mapping[str, Any] | None = None,
    formation: Mapping[str, Any] | None = None,
    changed_axis: str = "none",
    view=None,
) -> ConfirmationDecision:
    if contact.get("complete") is False:
        return finish_values(
            family=family,
            branch=branch,
            contact=contact,
            values={"source_confirmation": None, "location_touched": True, "complete_bar": False},
            confirm_at=None,
            decision_at=None,
            cutoff_ns=None,
        )
    binder = _family_confirm(family)
    bound = binder(
        market,
        branch=branch,
        contact=contact,
        reference=reference or {},
        formation=formation,
        changed_axis=changed_axis,
        view=view,
    )
    values = dict(bound.get("values") or bound)
    confirm_at = bound.get("confirm_at", values.get("confirm_at"))
    decision_at = bound.get("decision_at", values.get("decision_at"))
    cutoff = bound.get("cutoff_ns", decision_at)
    post_fail = bound.get("post_fail")
    return finish_values(
        family=family,
        branch=branch,
        contact=contact,
        values=values,
        confirm_at=None if confirm_at is None else int(confirm_at),
        decision_at=None if decision_at is None else int(decision_at),
        cutoff_ns=None if cutoff is None else int(cutoff),
        post_fail=post_fail,
    )


def trigger_contact(episode: Mapping[str, Any]) -> dict[str, Any]:
    trigger = dict(episode.get("trigger") or {})
    values = episode.get("values") or {}
    trigger.setdefault("side", episode.get("side") or values.get("side"))
    trigger.setdefault("contact_id", episode.get("candidate_id") or trigger.get("bar_id"))
    trigger.setdefault("complete", trigger.get("observed_complete", True))
    return trigger
