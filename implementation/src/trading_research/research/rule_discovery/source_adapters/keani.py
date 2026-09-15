"""P15-15 Keani ordered opening-value branch."""
from __future__ import annotations

from typing import Any, Mapping

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    register_family_transform,
    scan_family_date,
)

FAMILY = "KEANI-OPEN-ABOVE-VALUE"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("C4",)


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-15",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "c4": "rejection wick into developing POC or prior-day VAH; developing-VAL remains B0",
    }


def a_period_trade_below_vah_invalidates(low, vah) -> bool:
    if low is None or vah is None:
        return False
    return low < vah


def value_after_break_cannot_satisfy_before(value_known_at: int, break_at: int) -> bool:
    return int(value_known_at) <= int(break_at)


def low_support_inconclusive(n: int, floor: int = 5) -> bool:
    return n < floor


def apply_keani_rules(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """C4: A-period trade below VAH invalidates; value after the break cannot satisfy a before-break gate."""
    out = dict(document)
    kept = []
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        values = dict(row.get("values") or {})
        a_low = values.get("a_low")
        vah = values.get("prior_vah")
        values["a_period_below_vah_invalidates"] = a_period_trade_below_vah_invalidates(a_low, vah)
        if values["a_period_below_vah_invalidates"]:
            values["whole_period_above_vah"] = False
        break_at = values.get("breakout_at")
        value_at = values.get("dev_vah_known_at")
        if break_at is not None and value_at is not None:
            values["value_known_before_break"] = value_after_break_cannot_satisfy_before(value_at, break_at)
            if values["value_known_before_break"] is False:
                values["value_after_break_rejected"] = True
        n = values.get("support_n") or values.get("n") or (row.get("geometry") or {}).get("support_n")
        if n is not None:
            values["low_support_inconclusive"] = low_support_inconclusive(int(n))
        values["c4_rejection_levels"] = (row.get("geometry") or {}).get("rejection_level")
        values["keani_adapter_rules"] = True
        row["values"] = values
        kept.append(row)
    out["episodes"] = kept
    out["keani_adapter_rules"] = True
    out["baseline_version"] = version
    return out


register_family_transform(FAMILY, apply_keani_rules)


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Unchanged Keani stages from B0.1; defense uses the candidate band when the axis changed."""
    from decimal import Decimal as D

    from trading_research.research.method_pack.branch_coverage import setting
    from trading_research.research.method_pack.historical_features import MINUTE, Q, first_contact
    from trading_research.research.method_pack.historical_flow import exact_contact, flow_stages
    from trading_research.research.rule_discovery.baseline_repairs import absent_repaired, flow_absent_repaired, local_observations_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import bounds, scanner_ref

    prior = market.prior("day")
    old = prior["sessions"][-1]["window"] if prior.get("sessions") else None
    p = old.profile(old.start, old.end) if old else None
    a = market.range(market.at("09:30"), market.at("10:00"), "Keani-A")
    if a is None:
        decision = int(market.end)
        return {
            "values": {"branch": branch, "side": "long", "a_period_complete": None, "source_confirmation": None, "decision_at": decision},
            "confirm_at": None,
            "decision_at": decision,
            "cutoff_ns": decision,
            "source_confirmation": None,
        }
    initial = market.profile(a["start"], a["end"])
    limit = market.at(setting("keani_time")["latest_break"])
    observation = breakout = band = retest = defense = exact = obs = None
    dev = None
    for row in market.bars(a["end"], limit):
        current = market.profile(a["start"], row["start"])
        higher = current["val"] is not None and initial["val"] is not None and current["val"] > initial["val"] and current["vah"] >= initial["vah"]
        poc = current.get("poc")
        prior_vah = p["vah"] if p and p.get("vah") is not None and prior.get("scope_complete") else None
        hit_poc = poc is not None and row["C"] is not None and row["L"] <= poc and row["C"] > poc
        hit_vah = prior_vah is not None and row["C"] is not None and row["L"] <= prior_vah and row["C"] > prior_vah
        rejection = higher and row["C"] is not None and (hit_poc or hit_vah)
        if observation is None and rejection:
            observation = row
            continue
        if observation and row.get("observed_complete") and row["C"] is not None and current["vah"] is not None and row["C"] > current["vah"]:
            footprint = market.window.footprints.get(row["start"])
            if not footprint or any(u > 0 for _px, _b, _s, u in footprint["rows"]):
                continue
            cfg = setting("imbalance")
            im = market.domain(
                "O109",
                {
                    "candle_id": row["bar_id"],
                    "footprint_rows": [{"price": px, "B": b, "A": s} for px, b, s, u in footprint["rows"]],
                    "q": Q,
                    "ratio_min": D(str(cfg["ratio"])),
                    "row_count": cfg["consecutive_rows"],
                    "zero_rule": cfg["zero"],
                    "known_at": row["known_at"],
                },
            )
            runs = im.get("buy_runs", [])
            if runs:
                breakout = row
                dev = current
                band = [D(str(v)) for v in runs[0]["band"]]
                break
    cand_lo, cand_hi = bounds(scanner_ref(reference, formation))
    if changed_axis not in {"none", "baseline", ""} and cand_lo is not None and cand_hi is not None:
        band = [cand_lo, cand_hi]
    if breakout and band:
        retest = first_contact(market.bars(breakout["end"], min(int(market.end), breakout["end"] + 60 * MINUTE)), *band)
        if retest:
            exact = exact_contact(market, retest, *band)
            if exact:
                obs = local_observations_repaired(market, exact["at"], band, "long")
                defense = flow_stages(obs)["defense"]
    absent_stage = absent_repaired(market, a["end"], limit, fields=("C",))
    decision = defense["known_at"] if defense else min(int(market.end), limit + 60 * MINUTE)
    absent_defense = (
        flow_absent_repaired(market, retest["start"], min(int(market.end), ((int(decision) + MINUTE - 1) // MINUTE) * MINUTE), [r for r in obs["chunks"] if r["known_at"] <= decision])
        if obs
        else absent_stage
    )
    values = {
        "branch": branch,
        "side": "long",
        "prior_value_fixed": True if p and p.get("vah") is not None and prior.get("scope_complete") else None,
        "prior_vah": p["vah"] if p and prior.get("scope_complete") else None,
        "a_period_complete": True if a["coverage"]["observed_scope_complete"] else None,
        "a_low": a["low"],
        "a_end_at": a["known_at"],
        "developing_value_builds_higher": True if observation else absent_stage,
        "source_rejection_observed": True if observation else absent_stage,
        "observation_at": observation["known_at"] if observation else None,
        "dev_vah_known_at": dev["known_at"] if dev else None,
        "dev_vah_at_break": dev["vah"] if dev else None,
        "breakout_at": breakout["known_at"] if breakout else None,
        "breakout_close": breakout["C"] if breakout else None,
        "aggressive_buy_imbalance_break": True if breakout else absent_stage,
        "imbalance_band_known_at": breakout["known_at"] if breakout else None,
        "retest_at": exact["at"] if exact else None,
        "defense_at": defense["known_at"] if defense else None,
        "buyers_defend_same_imbalance_band": defense["held"] if defense else absent_defense,
        "dom_supports_long": defense["displayed_defense"] if defense else absent_defense,
        "time_of_day_allowed": breakout["known_at"] <= limit if breakout else absent_stage,
        "objective_fixed": None,
        "risk_defined": None,
        "decision_at": decision,
        "confirm_at": defense["known_at"] if defense else None,
        "source_confirmation": True if defense else absent_defense,
    }
    return {"values": values, "confirm_at": values["confirm_at"], "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-15"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["population_kind"] = "engineering_slice"
    payload["adapter_rules_applied"] = True
    return payload
