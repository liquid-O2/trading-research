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


# scan_green_failure (historical_price_scanners.py:203-205) runs the sweep+five-minute-reclaim
# path for every GB-FAIL branch except mss_fvg_refinement, which is routed to
# scan_green_refinement (line 256) as a post-parent annotation, not a sweep.
GB_FAIL_SWEEP_BRANCHES = frozenset({
    "nyam_box",
    "previous_hour",
    "asia_tdo_case",
    "cash_open_reclaim_case",
    "prior_day_level",
    "prior_week_level",
    "prior_month_level",
})
GB_FAIL_SWEEP_EVIDENCE = {
    "path": "implementation/src/trading_research/research/method_pack/historical_price_scanners.py",
    "symbol": "scan_green_failure",
    "lines": "203-253",
    "citation": "SEARCH_CONTRACT.md Timing T4: JJ judas_reversal and every GB-FAIL sweep branch",
}
GB_FAIL_NON_SWEEP_EVIDENCE = {
    "path": "implementation/src/trading_research/research/method_pack/historical_price_scanners.py",
    "symbol": "scan_green_refinement",
    "lines": "256-278",
    "citation": "mss_fvg_refinement is a post-parent annotation of nyam_box, not a sweep branch",
}

# SEARCH_CONTRACT Delta: every branch that actually consumes delta/flow in Sires,
# GB-SCALP, Saint; confirm input use in the source adapter. A branch with no
# delta input is explicitly not applicable.
DELTA_ADAPTER_EVIDENCE: dict[tuple[str, str], dict[str, Any]] = {
    ("SIRES", "absorption_reward_retest"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "174",
        "symbol": "_flow_episode",
        "field": "cvd_filter_ok",
        "note": "binds cvd_filter_ok to own_delta",
    },
    ("SIRES", "stop_four_stage"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "179",
        "symbol": "_flow_episode",
        "field": "delta_filter_ok",
        "note": "binds delta_filter_ok to own_delta",
    },
    ("SIRES", "footprint_confirmed_reaction"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "199-200",
        "symbol": "_flow_episode",
        "field": "candle_delta_disagreement,source_flow_confirmation",
        "note": "bar delta disagreement and own_delta flow confirmation",
    },
    ("SIRES", "vwap_deviation_fade"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "205",
        "symbol": "_flow_episode",
        "field": "cvd_filter_ok",
        "note": "binds cvd_filter_ok to own_delta",
    },
    ("SIRES", "ofm_aggressive"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "215",
        "symbol": "_flow_episode",
        "field": "cvd_filter_ok",
        "note": "binds cvd_filter_ok to own_delta",
    },
    ("SIRES", "defended_band_continuation"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "241-242",
        "symbol": "_flow_episode",
        "field": "executed_aggression,control_side_matches_thesis",
        "note": "both fields bind own_delta",
    },
    ("SIRES", "kg1_retest"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "244",
        "symbol": "_flow_episode",
        "field": "aggression_confirms",
        "note": "binds aggression_confirms to own_delta",
    },
    ("SIRES", "microbalance_break"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "345-348",
        "symbol": "scan_microbalance",
        "field": "directional_strength",
        "note": "directional_strength is sign*trigger['delta']>0",
    },
    ("SAINT-AMT", "continuation_retest"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_auction_scanners.py",
        "lines": "16-21,102-105",
        "symbol": "_control,scan_saint",
        "field": "delta",
        "note": "repeated body/delta control requires r['delta'] is not None",
    },
    ("SAINT-AMT", "trapped_buyers_retest"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_auction_scanners.py",
        "lines": "16-21,59-63,108-111",
        "symbol": "_control,_upper_failures,scan_saint",
        "field": "delta",
        "note": "upper-band failures skip rows with delta None; control uses bar delta",
    },
    ("SAINT-AMT", "failed_auction_return"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_auction_scanners.py",
        "lines": "16-21,45-55,164",
        "symbol": "_control,_saint_base,scan_saint",
        "field": "delta",
        "note": "_saint_base records directional body/delta control via _control",
    },
    ("SAINT-AMT", "poc_traversal"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_auction_scanners.py",
        "lines": "148,168",
        "symbol": "scan_saint",
        "field": "delta",
        "note": "aggressive POC passage requires r['delta'] is not None and sign*delta>0",
    },
}

DELTA_NO_INPUT_EVIDENCE: dict[tuple[str, str], dict[str, Any]] = {
    ("SIRES", "dom_rejection"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "165-168",
        "symbol": "_flow_episode",
        "note": "bound checks are aggression/progress/DOM confirmation; no delta/cvd field",
    },
    ("SIRES", "ofm_passive"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "218-224",
        "symbol": "_flow_episode",
        "note": "uses unknown/own/opposing counts; no delta/cvd field",
    },
    ("SIRES", "clean_squeeze"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "225-231",
        "symbol": "_flow_episode",
        "note": "uses count/unknown/opposing vs own; no delta/cvd field",
    },
    ("SIRES", "balance_failure_fade"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
        "lines": "232-237",
        "symbol": "_flow_episode",
        "note": "failed aggression / no_progress; no delta/cvd field",
    },
    ("GB-SCALP", "bearish_small_scalp"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_process_scanners.py",
        "lines": "60-85",
        "symbol": "scan_scalp",
        "note": "direction, pullback, size, management only; no delta/flow input",
    },
    ("GB-SCALP", "bullish_discount_pullback"): {
        "path": "implementation/src/trading_research/research/method_pack/historical_process_scanners.py",
        "lines": "60-85",
        "symbol": "scan_scalp",
        "note": "direction, pullback, size, management only; no delta/flow input",
    },
}

SEQUENCE_CONTRACT = "SEARCH_CONTRACT.md Sequence: JJ reversal/extension/other_session; GB failure/scalps; Sires reaction/continuation; Saint retests; Member reaction; Keani retest."
SEQUENCE_APPLY = {
    ("JJ-TBR", "judas_reversal"): "JJ reversal",
    ("JJ-TBR", "extension_reaction"): "JJ extension",
    ("JJ-TBR", "other_session"): "JJ other_session",
    ("GB-FAIL", "nyam_box"): "GB failure sweep+reclaim",
    ("GB-FAIL", "previous_hour"): "GB failure sweep+reclaim",
    ("GB-FAIL", "asia_tdo_case"): "GB failure sweep+reclaim",
    ("GB-FAIL", "cash_open_reclaim_case"): "GB failure sweep+reclaim",
    ("GB-FAIL", "prior_day_level"): "GB failure sweep+reclaim",
    ("GB-FAIL", "prior_week_level"): "GB failure sweep+reclaim",
    ("GB-FAIL", "prior_month_level"): "GB failure sweep+reclaim",
    ("GB-SCALP", "bearish_small_scalp"): "GB scalps",
    ("GB-SCALP", "bullish_discount_pullback"): "GB scalps",
    ("SIRES", "absorption_reward_retest"): "Sires reaction/retest",
    ("SIRES", "footprint_confirmed_reaction"): "Sires reaction",
    ("SIRES", "defended_band_continuation"): "Sires continuation",
    ("SIRES", "clean_squeeze"): "Sires continuation",
    ("SIRES", "stop_four_stage"): "Sires reaction",
    ("SIRES", "ofm_aggressive"): "Sires reaction",
    ("SIRES", "ofm_passive"): "Sires reaction",
    ("SIRES", "dom_rejection"): "Sires reaction",
    ("SIRES", "kg1_retest"): "Sires retest",
    ("SAINT-AMT", "continuation_retest"): "Saint retests",
    ("SAINT-AMT", "trapped_buyers_retest"): "Saint retests",
    ("SAINT-AMT", "failed_auction_return"): "Saint retest of original auction after return",
    ("SAINT-AMT", "poc_traversal"): "Saint reacceptance then aggressive passage",
    ("MEMBER-TWO-REASONS", "resistance_short"): "Member reaction",
    ("MEMBER-TWO-REASONS", "planned_return_long"): "Member reaction",
    ("KEANI-OPEN-ABOVE-VALUE", "source_long"): "Keani retest",
}
SEQUENCE_DEFER = {
    ("JJ-TBR", "judas_outbound"): "Judas outbound is not converted into a retest",
    ("GB-FAIL", "mss_fvg_refinement"): "post-parent annotation, not a reclaim/retest machine",
    ("SIRES", "balance_failure_fade"): "SEARCH_CONTRACT Sequence names Sires reaction/continuation; fade is not a retest",
    ("SIRES", "vwap_deviation_fade"): "SEARCH_CONTRACT Sequence names Sires reaction/continuation; fade is not a retest",
    ("SIRES", "microbalance_break"): "breakout, not a reaction/continuation retest",
}

PROFILE_CONTRACT = "SEARCH_CONTRACT.md Profile: Saint and Member profile references; Keani developing value; Sires balance references."
PROFILE_SIRES = {
    "balance_failure_fade": "Sires balance references (auction/pivots fade)",
    "microbalance_break": "Sires balance references (microbalance inside HTF auction)",
    "defended_band_continuation": "Sires balance references (HTF auction band as the defended reference)",
}

FORMATION_KEYS = {
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
FORMATION_CONTRACT = "SEARCH_CONTRACT.md Formation: JJ other_session, single_extended, single_purged, internal_rotation; GB nyam_box/previous_hour; Saint balance branches; Sires microbalance."

REFERENCE_KEYS = {
    ("GB-VWAP", "source_long"),
    ("GB-SCALP", "bearish_small_scalp"),
    ("GB-SCALP", "bullish_discount_pullback"),
    ("SIRES", "vwap_deviation_fade"),
    ("SIRES", "defended_band_continuation"),
}
REFERENCE_CONTRACT = "SEARCH_CONTRACT.md Reference: custom siblings of GB-VWAP, GB-SCALP and Sires vwap_deviation_fade/defended_band_continuation only."

MEMORY_FAMILIES = {"MEMBER-TWO-REASONS", "SIRES", "SAINT-AMT", "REFILL-STUDY"}
MEMORY_CONTRACT = "SEARCH_CONTRACT.md Memory: existing reference-contact candidates in Member/Sires/Saint; Refilling observations separately."

T123_KEYS = {("JJ-TBR", "judas_reversal"), ("JJ-TBR", "other_session"), ("GB-FAIL", "nyam_box")}
T123_CONTRACT = "SEARCH_CONTRACT.md Timing: JJ judas_reversal/other_session and GB nyam_box custom siblings."


def _gb_fail_sweep(branch: str) -> bool:
    """True only for scanner sweep+reclaim branches, never for mss_fvg_refinement."""
    return branch in GB_FAIL_SWEEP_BRANCHES


def cell_evidence(bank: str, recipe_id: str, family: str, branch: str) -> dict[str, Any]:
    ok, reason = applicable(bank, recipe_id, family, branch)
    key = (family, branch)
    evidence: dict[str, Any] = {
        "family": family,
        "branch": branch,
        "bank": bank,
        "recipe_id": recipe_id,
        "applicable": ok,
        "reason": reason,
        "contract": None,
        "adapter": None,
    }
    if bank == "Formation":
        evidence["contract"] = FORMATION_CONTRACT
    elif bank == "Profile":
        evidence["contract"] = PROFILE_CONTRACT
        if family in {"SAINT-AMT", "MEMBER-TWO-REASONS", "KEANI-OPEN-ABOVE-VALUE"}:
            evidence["adapter"] = {
                "path": "implementation/src/trading_research/research/method_pack/historical_auction_scanners.py",
                "note": "family uses profile/value references in the source adapter",
            }
        elif key[0] == "SIRES" and branch in PROFILE_SIRES:
            evidence["adapter"] = {
                "path": "implementation/src/trading_research/research/method_pack/historical_flow.py",
                "note": PROFILE_SIRES[branch],
            }
    elif bank == "Reference":
        evidence["contract"] = REFERENCE_CONTRACT
    elif bank == "Delta":
        evidence["contract"] = "SEARCH_CONTRACT.md Delta: confirm input use in the source adapter. A branch with no delta input is explicitly not applicable."
        evidence["adapter"] = DELTA_ADAPTER_EVIDENCE.get(key) or DELTA_NO_INPUT_EVIDENCE.get(key) or {
            "note": "branch has no delta input",
        }
    elif bank == "Sequence":
        evidence["contract"] = SEQUENCE_CONTRACT
        evidence["adapter"] = {"note": SEQUENCE_APPLY.get(key) or SEQUENCE_DEFER.get(key) or reason}
    elif bank == "Memory":
        evidence["contract"] = MEMORY_CONTRACT
    elif bank == "Timing":
        if recipe_id == "T4":
            evidence["contract"] = GB_FAIL_SWEEP_EVIDENCE["citation"]
            evidence["adapter"] = dict(GB_FAIL_SWEEP_EVIDENCE if _gb_fail_sweep(branch) or key == ("JJ-TBR", "judas_reversal") else GB_FAIL_NON_SWEEP_EVIDENCE)
        else:
            evidence["contract"] = T123_CONTRACT
    return evidence


def applicable(bank: str, recipe_id: str, family: str, branch: str) -> tuple[bool, str | None]:
    key = (family, branch)
    if bank == "Formation":
        ok = key in FORMATION_KEYS
        return ok, None if ok else "formation bank not listed for this branch"
    if bank == "Profile":
        if family in {"SAINT-AMT", "MEMBER-TWO-REASONS", "KEANI-OPEN-ABOVE-VALUE"}:
            return True, None
        if family == "SIRES" and branch in PROFILE_SIRES:
            return True, None
        return False, "profile bank not listed for this branch"
    if bank == "Reference":
        ok = key in REFERENCE_KEYS
        return ok, None if ok else "reference custom sibling not listed"
    if bank == "Delta":
        if key in DELTA_ADAPTER_EVIDENCE:
            return True, None
        return False, "branch has no delta input"
    if bank == "Sequence":
        if key in SEQUENCE_APPLY:
            return True, None
        return False, SEQUENCE_DEFER.get(key) or "sequence bank not listed for this branch"
    if bank == "Memory":
        ok = family in MEMORY_FAMILIES
        return ok, None if ok else "memory bank not listed"
    if bank == "Timing":
        if recipe_id in {"T1", "T2", "T3"}:
            ok = key in T123_KEYS
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
                evidence = cell_evidence(bank, str(recipe["id"]), row["method_id"], row["branch"])
                item["evidence"] = evidence
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
        "t4_sweep_branches": sorted(GB_FAIL_SWEEP_BRANCHES),
        "delta_adapter_branches": sorted(f"{family}:{branch}" for family, branch in DELTA_ADAPTER_EVIDENCE),
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


def applicability_matrix_document(document: Mapping[str, Any] | None = None) -> dict[str, Any]:
    bank = document or expand_candidate_bank()
    cells = []
    for row in bank["candidates"]:
        cells.append(row.get("evidence") or cell_evidence(row["bank"], row["recipe_id"], row["family"], row["branch"]))
    deferred_cells = []
    for row in bank["deferred"]:
        evidence = row.get("evidence") or cell_evidence(row["bank"], row["recipe_id"], row["family"], row["branch"])
        deferred_cells.append({**evidence, "deferred": True, "reason": row.get("reason")})
    return {
        "schema_version": "research-applicability-matrix-v1",
        "contract": "planning/phase-1-5/SEARCH_CONTRACT.md",
        "selected": [{"id": r["candidate_id"], "bank": r["bank"], "family": r["family"], "branch": r["branch"], "evidence": r.get("evidence")} for r in bank["candidates"]],
        "deferred": bank["deferred"],
        "cells": cells,
        "deferred_cells": deferred_cells,
        "counts": bank["counts"],
        "t4_sweep_branches": sorted(GB_FAIL_SWEEP_BRANCHES),
        "delta_adapter_branches": sorted(f"{family}:{branch}" for family, branch in DELTA_ADAPTER_EVIDENCE),
        "delta_no_input_branches": sorted(f"{family}:{branch}" for family, branch in DELTA_NO_INPUT_EVIDENCE),
        "sequence_apply": {f"{family}:{branch}": note for (family, branch), note in SEQUENCE_APPLY.items()},
        "profile_sires": dict(PROFILE_SIRES),
    }


def write_candidate_bank_v1(path: Path | None = None) -> dict[str, Any]:
    document = expand_candidate_bank()
    target = path or Path(__file__).with_name("candidate_bank_v1.json")
    target.write_text(json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    return document


def slice_p15_08(day: str) -> dict[str, Any]:
    from trading_research.research.rule_discovery.engine_slice import run_candidate_branch_session

    return run_candidate_branch_session(day)
