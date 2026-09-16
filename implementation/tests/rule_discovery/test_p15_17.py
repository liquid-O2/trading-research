"""P15-17 stage A: B0.2 candidate machinery. Does not score candidates."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from trading_research.errors import ContractError
from trading_research.research.rule_discovery.registry import applicable as bank_applicable
from trading_research.research.rule_discovery.search import (
    AXIS_ENUMERATION_POINTS,
    AXIS_PHASE,
    B02_FAMILIES,
    CONTROL_BRANCH,
    CONTROL_DATES,
    THROUGHPUT_CANDIDATE_IDS,
    build_overrides,
    check_causal_parameters,
    contact_ids,
    cutoff_ns,
    load_b02_market,
    load_bank,
    market_for_family,
    negative_control_pair,
    resolve_bank,
    resolve_candidate,
    scan_b02_baseline,
    scan_candidate,
    serialize_scan_bytes,
    stage_verdict_vector,
    verdict_changed,
    write_control_scan,
)
from trading_research.research.rule_discovery.source_adapters.common import install_write_guard
from trading_research.research.rule_discovery.source_adapters.enumeration import ENUMERATION_KEY

ATTEMPT = Path(__file__).resolve().parents[2] / "reports/research-work/P15-17/47dedaaa4f5b9ce1"
FIXTURE_DAY = "2021-11-01"
ENUMERATION_PROOF_DAY = "2021-11-01"
SEQUENCE_PROOF_ID = "SAINT-AMT:continuation_retest:S2"
NS = 1_000_000_000


def _stage_map(episode: dict) -> dict[str, dict]:
    return {str(item.get("stage")): item for item in episode.get("stages") or []}


def _existing_value_changed(left: dict, right: dict) -> bool:
    if left.get("verdict") != right.get("verdict"):
        return True
    if left.get("at_ns") != right.get("at_ns"):
        return True
    lo = left.get("operands") or {}
    ro = right.get("operands") or {}
    return any(key in ro and ro[key] != value for key, value in lo.items())


def _assert_predicted_direction(bank: str, left_map: dict, right_map: dict, item) -> bool:
    """The overridden stage moved in the direction the recipe predicts."""
    if bank == "Profile":
        lo = (left_map.get("context") or left_map.get("reference") or {}).get("operands") or {}
        ro = (right_map.get("context") or right_map.get("reference") or {}).get("operands") or {}
        if ro.get("profile_recipe") != item.recipe_id:
            return False
        return any(lo.get(key) != ro.get(key) for key in ("prior_vah", "poc", "vah", "val", "fully_above")) or (
            (left_map.get("context") or {}).get("verdict") != (right_map.get("context") or {}).get("verdict")
        )
    if bank == "Delta":
        left = left_map.get("confirmation") or {}
        right = right_map.get("confirmation") or {}
        ro = right.get("operands") or {}
        if ro.get("delta_recipe") != item.recipe_id:
            return False
        return left.get("verdict") != right.get("verdict") or (left.get("operands") or {}).get(
            "arrival_ratio"
        ) != ro.get("arrival_ratio") or "delta_value" in ro or "delta_reason" in ro
    if bank == "Sequence":
        for name in item.hooks:
            if name not in left_map:
                continue
            ro = (right_map[name].get("operands") or {})
            if ro.get("sequence_recipe") == item.recipe_id:
                return True
        return False
    if bank == "Memory":
        left = left_map.get("location") or {}
        right = right_map.get("location") or {}
        ro = right.get("operands") or {}
        if ro.get("memory_recipe") != item.recipe_id:
            return False
        return "prior_contacts" in ro or "memory_reason" in ro
    return False


def test_applicability_equals_bank_flags():
    bank = load_bank()
    resolved = {item.candidate_id: item for item in resolve_bank(bank)}
    assert len(resolved) == 160
    assert len(resolved) == len(bank["candidates"])
    for row in bank["candidates"]:
        item = resolved[row["candidate_id"]]
        flag = bool(row["evidence"]["applicable"])
        assert item.applicable is flag
        ok, _reason = bank_applicable(row["bank"], row["recipe_id"], row["family"], row["branch"])
        assert item.applicable is ok
    deferred_ids = {row["candidate_id"] for row in bank["deferred"]}
    assert deferred_ids.isdisjoint(resolved)


def test_unsupported_path_records_a_reason():
    resolved = resolve_bank()
    unsupported = [item for item in resolved if not item.supported]
    assert unsupported
    for item in unsupported:
        assert item.unsupported_reason
        assert item.candidate_id
    scalp_seq = next(item for item in resolved if item.candidate_id == "GB-SCALP:bearish_small_scalp:S1")
    assert scalp_seq.supported is False
    assert "does not expose stage" in scalp_seq.unsupported_reason
    jet = resolve_candidate(
        {
            "candidate_id": "JETBUNDLE-STATES:B:F1",
            "family": "JETBUNDLE-STATES",
            "branch": "B",
            "bank": "Formation",
            "recipe_id": "F1",
            "changed_axis": "formation",
            "parameters": {"minutes": 60},
            "required_stages": ["formation", "contact", "confirmation"],
            "evidence": {"applicable": False, "reason": "process unit"},
        }
    )
    assert jet.supported is False
    assert jet.unsupported_reason
    assert "no B0.2 scanner" in jet.unsupported_reason


def test_ra1_negative_control_per_family():
    install_write_guard()
    mismatches = []
    for family in B02_FAMILIES:
        branch = CONTROL_BRANCH[family]
        coverage = f"{family}:branch:{branch}"
        for day in CONTROL_DATES:
            market = load_b02_market(day)
            omitted, none, equal = negative_control_pair(market, family, branch)
            path = write_control_scan(ATTEMPT, day, coverage, omitted)
            assert path.is_file()
            assert path.read_bytes() == serialize_scan_bytes(omitted)
            if not equal:
                mismatches.append({"family": family, "branch": branch, "date": day})
    assert mismatches == []


def test_positive_control_per_bank_other_stages_unchanged():
    """Evaluation axes move only their own stage; enumeration axes are allowed to
    move the contact population and are checked separately."""
    install_write_guard()
    market = load_b02_market(FIXTURE_DAY)
    resolved_map = {item.candidate_id: item for item in resolve_bank()}
    seen_banks = set()
    for cid in THROUGHPUT_CANDIDATE_IDS:
        item = resolved_map[cid]
        assert item.supported, (cid, item.unsupported_reason)
        seen_banks.add(item.bank)
        baseline = scan_b02_baseline(market, item.family, item.branch)
        candidate = scan_candidate(market, item)
        assert serialize_scan_bytes(baseline) != serialize_scan_bytes(candidate), cid
        baseline_eps = list(baseline.get("episodes") or [])
        candidate_eps = list(candidate.get("episodes") or [])
        assert baseline_eps, cid
        if item.phase == "enumeration":
            # An enumeration axis runs before references and contacts are built,
            # so the contact population itself is allowed to move.
            base_stages = [_stage_map(episode) for episode in baseline_eps]
            cand_stages = [_stage_map(episode) for episode in candidate_eps]
            assert contact_ids(candidate) != contact_ids(baseline) or base_stages != cand_stages, cid
            continue
        assert len(candidate_eps) == len(baseline_eps), cid
        assert contact_ids(candidate) == contact_ids(baseline), cid
        predicted = False
        real = False
        for left, right in zip(baseline_eps, candidate_eps):
            left_map = _stage_map(left)
            right_map = _stage_map(right)
            assert set(left_map) == set(right_map)
            for name, record in left_map.items():
                if name in item.hooks:
                    if _existing_value_changed(record, right_map[name]):
                        real = True
                    continue
                assert record == right_map[name], (cid, name)
            if _assert_predicted_direction(item.bank, left_map, right_map, item):
                predicted = True
        assert real, cid
        assert predicted, cid
    assert seen_banks == {"Formation", "Profile", "Reference", "Delta", "Sequence", "Memory", "Timing"}


def test_axis_phase_map_splits_enumeration_from_evaluation():
    assert {bank for bank, phase in AXIS_PHASE.items() if phase == "enumeration"} == {
        "Formation",
        "Reference",
        "Timing",
    }
    assert {bank for bank, phase in AXIS_PHASE.items() if phase == "evaluation"} == {
        "Profile",
        "Delta",
        "Sequence",
        "Memory",
    }
    assert AXIS_ENUMERATION_POINTS["Formation"] == ("references",)
    assert AXIS_ENUMERATION_POINTS["Reference"] == ("references",)
    assert AXIS_ENUMERATION_POINTS["Timing"] == ("window",)
    resolved_map = {item.candidate_id: item for item in resolve_bank()}
    for cid in THROUGHPUT_CANDIDATE_IDS:
        item = resolved_map[cid]
        overrides = build_overrides(item, object())
        if item.phase == "enumeration":
            assert set(overrides) == {ENUMERATION_KEY}
        else:
            assert ENUMERATION_KEY not in overrides
            assert set(overrides) == set(item.hooks)


def test_enumeration_axes_change_the_contact_population():
    """Formation and Timing (T4) recipes run before references and contacts are
    built, so they may change which contacts exist. A Sequence recipe runs after
    and leaves the contact set alone while moving stage verdicts."""
    install_write_guard()
    market = load_b02_market(ENUMERATION_PROOF_DAY)
    resolved_map = {item.candidate_id: item for item in resolve_bank()}

    for cid, expected in (("GB-FAIL:nyam_box:F1", (3, 2)), ("JJ-TBR:judas_reversal:T4", (2, 1))):
        item = resolved_map[cid]
        baseline = scan_b02_baseline(market, item.family, item.branch)
        candidate = scan_candidate(market, item)
        base_ids = contact_ids(baseline)
        cand_ids = contact_ids(candidate)
        assert (len(base_ids), len(cand_ids)) == expected, (cid, base_ids, cand_ids)
        assert cand_ids != base_ids, (cid, base_ids, cand_ids)
        assert verdict_changed(baseline, candidate)["changed"], cid

    item = resolved_map[SEQUENCE_PROOF_ID]
    baseline = scan_b02_baseline(market, item.family, item.branch)
    candidate = scan_candidate(market, item)
    assert contact_ids(candidate) == contact_ids(baseline), SEQUENCE_PROOF_ID
    assert stage_verdict_vector(candidate) != stage_verdict_vector(baseline), SEQUENCE_PROOF_ID


def test_freeze_pins_every_candidate_resolution():
    import json

    from trading_research.research.rule_discovery.search import resolve_bank as resolve

    freeze = json.loads((ATTEMPT / "FREEZE.json").read_text())
    rows = freeze["resolutions"]
    resolved = resolve()
    assert len(rows) == 160
    assert len(rows) == len(resolved)
    for row, item in zip(rows, resolved):
        assert row == item.freeze_row()
    unsupported = [row for row in rows if not row["supported"]]
    assert len(unsupported) == 12
    assert freeze["support_counts"]["unsupported"]
    assert {row["candidate_id"] for row in unsupported} == {
        item["candidate_id"] for item in freeze["support_counts"]["unsupported"]
    }


def test_future_dependent_recipe_parameter_fails():
    install_write_guard()
    market = load_b02_market(FIXTURE_DAY)
    item = next(row for row in resolve_bank() if row.candidate_id == "GB-VWAP:source_long:R1")
    future = cutoff_ns(market_for_family(market, item.family)) + 1
    poisoned = replace(item, parameters={**dict(item.parameters), "issue_at_ns": future})
    with pytest.raises(ContractError, match="future-dependent"):
        scan_candidate(market, poisoned)
    with pytest.raises(ContractError, match="future-dependent"):
        check_causal_parameters({"peek_future": True}, cutoff=future - 1)
