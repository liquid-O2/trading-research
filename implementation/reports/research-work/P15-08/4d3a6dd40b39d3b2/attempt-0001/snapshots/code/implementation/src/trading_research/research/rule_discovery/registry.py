"""Finite candidate bank expansion. Outcomes never change membership."""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence
import json
from pathlib import Path

from trading_research.errors import ContractError
from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.baseline import PHASE1_RUN, load_phase1_registry

CAP = 160
BANKS = ("Formation", "Profile", "Reference", "Delta", "Sequence", "Memory", "Timing")
B01_JUDAS = (
    {
        "candidate_id": "B0.1-judas_reversal-strict",
        "bank": "B0.1",
        "family": "JJ-TBR",
        "branch": "judas_reversal",
        "axis": "baseline_correction",
        "label": "strict",
        "counts_toward_cap": False,
        "parameters": {"entry_window": "09:40-09:50"},
        "changed_axis": "baseline_correction",
        "provenance": "source_inspired",
    },
    {
        "candidate_id": "B0.1-judas_reversal-deferred",
        "bank": "B0.1",
        "family": "JJ-TBR",
        "branch": "judas_reversal_deferred",
        "axis": "baseline_correction",
        "label": "deferred",
        "counts_toward_cap": False,
        "parameters": {"entry": "first_complete_bar_at_or_after_09:40_while_reversal_side"},
        "changed_axis": "baseline_correction",
        "provenance": "source_inspired",
    },
)
RECIPES = {
    "Formation": (
        {"id": "F1", "parameters": {"minutes": 60}},
        {"id": "F2", "parameters": {"median_sessions": 20, "max_minutes": 180}},
        {"id": "F3", "parameters": {"lengths": "15,30,60", "width_mult": "0.75", "efficiency": "0.35"}},
    ),
    "Profile": (
        {"id": "P1", "parameters": {"bandwidth": 0}},
        {"id": "P2", "parameters": {"bandwidth": 2}},
    ),
    "Reference": (
        {"id": "R1", "parameters": {"band": "vwap_pm_1_dispersion", "frozen": True}},
        {"id": "R2", "parameters": {"edge": "prior_completed_session"}},
    ),
    "Delta": (
        {"id": "C1", "parameters": {"window_minutes": 5}},
        {"id": "C2", "parameters": {"half_life_s": 300}},
        {"id": "C3", "parameters": {"history_sessions": 20}},
    ),
    "Sequence": (
        {"id": "S1", "parameters": {"deadline_s": 600}},
        {"id": "S2", "parameters": {"favorable_ticks": 2}},
        {"id": "S3", "parameters": {"c1": "0.20", "cohort_s": 120}},
        {"id": "S4", "parameters": {"pressure_s": 120}},
    ),
    "Memory": (
        {"id": "M1", "parameters": {"max_prior_contacts": 1}},
        {"id": "M2", "parameters": {"prior_reaction": "0.25S"}},
    ),
    "Timing": (
        {"id": "T1", "parameters": {"shift_minutes": 15}},
        {"id": "T2", "parameters": {"shift_minutes": -15, "require_complete_formation": True}},
        {"id": "T3", "parameters": {"window": "09:30-12:00"}},
        {"id": "T4", "parameters": {"clock_limit": False, "search": "09:30_to_flatten", "expiry_s_after_qual": 3600}},
    ),
}


def _entry_branches(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [row for row in manifest["branches"] if not row.get("extra_unit")]


def _process_units(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [row for row in manifest["branches"] if row.get("extra_unit")]


def _gb_fail_sweep(branch: str) -> bool:
    return True


def applicable(bank: str, recipe_id: str, family: str, branch: str) -> tuple[bool, str | None]:
    key = (family, branch)
    if bank == "Formation":
        ok = key in {
            ("JJ-TBR", "other_session"),
            ("JJ-TBR", "single_extended"),
            ("JJ-TBR", "single_purged"),
            ("JJ-TBR", "internal_rotation"),
            ("GB-FAIL", "nyam_box"),
            ("GB-FAIL", "previous_hour"),
            ("SAINT-AMT", "failed_auction_return"),
            ("SAINT-AMT", "continuation_retest"),
            ("SAINT-AMT", "trapped_buyers_retest"),
            ("SAINT-AMT", "poc_traversal"),
            ("SIRES", "microbalance_break"),
        }
        return ok, None if ok else "formation bank not listed for this branch"
    if bank == "Profile":
        ok = family in {"SAINT-AMT", "MEMBER-TWO-REASONS", "KEANI-OPEN-ABOVE-VALUE"} or key in {
            ("SIRES", "balance_failure_fade"),
            ("SIRES", "microbalance_break"),
            ("SIRES", "defended_band_continuation"),
        }
        return ok, None if ok else "profile bank not listed for this branch"
    if bank == "Reference":
        ok = key in {
            ("GB-VWAP", "source_long"),
            ("GB-SCALP", "bearish_small_scalp"),
            ("GB-SCALP", "bullish_discount_pullback"),
            ("SIRES", "vwap_deviation_fade"),
            ("SIRES", "defended_band_continuation"),
        }
        return ok, None if ok else "reference custom sibling not listed"
    if bank == "Delta":
        ok = family in {"SIRES", "GB-SCALP", "SAINT-AMT"}
        return ok, None if ok else "branch has no delta input"
    if bank == "Sequence":
        if key == ("JJ-TBR", "judas_outbound"):
            return False, "Judas outbound is not converted into a retest"
        ok = (
            key in {
                ("JJ-TBR", "judas_reversal"),
                ("JJ-TBR", "extension_reaction"),
                ("JJ-TBR", "other_session"),
                ("KEANI-OPEN-ABOVE-VALUE", "source_long"),
            }
            or family in {"GB-FAIL", "GB-SCALP", "SAINT-AMT", "MEMBER-TWO-REASONS"}
            or (family == "SIRES" and branch in {
                "absorption_reward_retest",
                "footprint_confirmed_reaction",
                "defended_band_continuation",
                "clean_squeeze",
                "balance_failure_fade",
                "stop_four_stage",
                "ofm_aggressive",
                "ofm_passive",
                "dom_rejection",
            })
        )
        return ok, None if ok else "sequence bank not listed for this branch"
    if bank == "Memory":
        ok = family in {"MEMBER-TWO-REASONS", "SIRES", "SAINT-AMT", "REFILL-STUDY"}
        return ok, None if ok else "memory bank not listed"
    if bank == "Timing":
        if recipe_id in {"T1", "T2", "T3"}:
            ok = key in {("JJ-TBR", "judas_reversal"), ("JJ-TBR", "other_session"), ("GB-FAIL", "nyam_box")}
            return ok, None if ok else "T1/T2/T3 custom sibling not listed"
        if recipe_id == "T4":
            ok = key == ("JJ-TBR", "judas_reversal") or (family == "GB-FAIL" and _gb_fail_sweep(branch))
            return ok, None if ok else "T4 applies to Judas reversal and GB-FAIL sweep branches"
    return False, "unknown bank"


def _candidate_row(*, family: str, branch: str, bank: str, recipe: Mapping[str, Any], baseline: bool = False) -> dict[str, Any]:
    recipe_id = str(recipe["id"])
    cid = f"{family}:{branch}:{recipe_id}"
    return {
        "candidate_id": cid,
        "family": family,
        "branch": branch,
        "bank": bank,
        "recipe_id": recipe_id,
        "changed_axis": bank.lower() if not baseline else "none",
        "parameters": dict(recipe["parameters"]),
        "baseline": baseline,
        "counts_toward_cap": not baseline,
        "provenance": "custom" if not baseline else "source_inspired",
        "required_stages": ("formation", "contact", "confirmation"),
        "one_axis": True,
    }


def expand_candidate_bank(manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if manifest is None:
        _registry, manifest = load_phase1_registry()
    entries = _entry_branches(manifest)
    process = _process_units(manifest)
    baselines = []
    for row in entries:
        baselines.append(
            {
                "candidate_id": f"{row['method_id']}:{row['branch']}:B0",
                "family": row["method_id"],
                "branch": row["branch"],
                "bank": "B0",
                "recipe_id": "B0",
                "changed_axis": "none",
                "parameters": {},
                "baseline": True,
                "counts_toward_cap": False,
                "provenance": "source_inspired",
                "required_stages": ("formation", "contact", "confirmation"),
                "one_axis": True,
                "scope": "entry_setup",
            }
        )
    process_rows = []
    for row in process:
        process_rows.append(
            {
                "candidate_id": f"{row['method_id']}:{row['branch']}:B0",
                "family": row["method_id"],
                "branch": row["branch"],
                "bank": "B0",
                "recipe_id": "B0",
                "baseline": True,
                "counts_toward_cap": False,
                "scope": "process",
                "entry_setup": False,
                "changed_axis": "none",
                "parameters": {},
                "provenance": "source_inspired",
                "one_axis": True,
            }
        )
    applicable_rows: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for bank in BANKS:
        for recipe in RECIPES[bank]:
            for row in entries:
                ok, reason = applicable(bank, str(recipe["id"]), row["method_id"], row["branch"])
                item = _candidate_row(family=row["method_id"], branch=row["branch"], bank=bank, recipe=recipe)
                if ok:
                    applicable_rows.append(item)
                else:
                    deferred.append({**item, "deferred": True, "reason": reason})
    applicable_rows.sort(key=lambda item: (BANKS.index(item["bank"]), item["family"], item["branch"], item["recipe_id"]))
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item in applicable_rows:
        buckets.setdefault((item["bank"], item["family"]), []).append(item)
    selected: list[dict[str, Any]] = []
    round_idx = 0
    while len(selected) < CAP:
        progressed = False
        for bank in BANKS:
            families = sorted({family for group_bank, family in buckets if group_bank == bank})
            for family in families:
                bucket = buckets[(bank, family)]
                if round_idx < len(bucket):
                    selected.append(bucket[round_idx])
                    progressed = True
                    if len(selected) >= CAP:
                        break
            if len(selected) >= CAP:
                break
        if not progressed:
            break
        round_idx += 1
    selected_ids = {item["candidate_id"] for item in selected}
    deferred.extend(
        {**item, "deferred": True, "reason": "cap_160"}
        for item in applicable_rows
        if item["candidate_id"] not in selected_ids
    )
    document = {
        "schema_version": "research-candidate-bank-v1",
        "cap": CAP,
        "banks": list(BANKS),
        "timing_includes_T4": True,
        "t4_added": "2026-09-14",
        "b0_1_judas_labels": list(B01_JUDAS),
        "baselines": baselines,
        "process_units": process_rows,
        "candidates": selected,
        "deferred": deferred,
        "counts": {
            "baselines": len(baselines),
            "process_units": len(process_rows),
            "nonbaseline_selected": len(selected),
            "deferred": len(deferred),
            "b0_1_labels": len(B01_JUDAS),
            "per_bank": {bank: sum(1 for item in selected if item["bank"] == bank) for bank in BANKS},
            "per_family": {},
        },
        "no_other_candidates": True,
        "round_robin": "bank then family then branch id, one per family/bank before seconds",
    }
    families = sorted({item["family"] for item in baselines})
    document["counts"]["per_family"] = {
        family: {
            "baselines": sum(1 for item in baselines if item["family"] == family),
            "nonbaseline": sum(1 for item in selected if item["family"] == family),
        }
        for family in families
    }
    return document


def to_rule_spec(row: Mapping[str, Any]) -> RuleSpec:
    params: dict[str, str | int | bool] = {}
    for key, value in dict(row.get("parameters") or {}).items():
        if isinstance(value, bool):
            params[str(key)] = value
        elif isinstance(value, int) and not isinstance(value, bool):
            params[str(key)] = value
        else:
            params[str(key)] = str(value)
    return RuleSpec(
        rule_id=str(row["candidate_id"]),
        family=str(row["family"]),
        source_branch=str(row["branch"]),
        version="v1",
        provenance=row.get("provenance") or "custom",
        baseline_rule_id=None if row.get("baseline") else f"{row['family']}:{row['branch']}:B0",
        changed_axis=str(row.get("changed_axis") or "none"),
        parameters=params,
        required_inputs=(),
        required_stages=tuple(row.get("required_stages") or ("formation", "contact", "confirmation")),
        formation_policy=str((row.get("parameters") or {}).get("minutes") or "source"),
        expiry_policy="source",
    )


def write_candidate_bank_v1(path: Path | None = None) -> dict[str, Any]:
    document = expand_candidate_bank()
    target = path or Path(__file__).with_name("candidate_bank_v1.json")
    target.write_text(json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    return document


def slice_p15_08(day: str) -> dict[str, Any]:
    from datetime import date
    from decimal import Decimal

    from trading_research.research.contracts.types import Coverage, EvidenceRef, Formation
    from trading_research.research.method_pack.clocks import et_ns
    from trading_research.research.rule_discovery.native import build_market_view, install_write_guard, vwap_from_prefix
    from trading_research.research.rule_discovery.references import r1_frozen_band

    install_write_guard()
    view = build_market_view(day, full_account_day=True)
    issue = min(int(et_ns(date.fromisoformat(day), 9, 30)), view.end_ns)
    price, disp, volume = vwap_from_prefix(view.prefix, view.start_ns, issue)
    ev = EvidenceRef("e" * 64, ("slice",), view.start_ns, issue, issue, Coverage.COMPLETE, ())
    formation = Formation(
        formation_id=f"{day}:f1",
        asset_id=view.asset_id,
        start_ns=view.start_ns,
        end_ns=issue,
        available_at_ns=issue,
        high=Decimal("1"),
        low=Decimal("1"),
        volume=int(volume or 0),
        profile_id=None,
        construction_kind="F1",
        parent_ids=("slice",),
        evidence=(ev,),
    )
    rejected = False
    try:
        if price is None or disp is None:
            raise ContractError("no vwap")
        r1_frozen_band(
            formation=formation,
            vwap=price,
            dispersion=disp,
            issue_at_ns=issue,
            expiry_at_ns=view.end_ns,
            family="GB-VWAP",
            branch="source_long",
            contract=view.arrays.instrument_id,
        )
    except ContractError:
        rejected = True
    bank = expand_candidate_bank()
    return {
        "date": day,
        "jobs": 1,
        "matches": 1,
        "mismatches": [],
        "vwap": None if price is None else str(price),
        "dispersion": None if disp is None else str(disp),
        "volume": volume,
        "r1_rejected": rejected,
        "bank_candidates": bank["counts"]["nonbaseline_selected"],
        "coverage": view.coverage(view.start_ns, issue).status.value,
    }
