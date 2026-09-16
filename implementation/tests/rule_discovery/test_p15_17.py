"""P15-17 stage A: B0.2 candidate machinery. Does not score candidates."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from trading_research.errors import ContractError
from trading_research.research.rule_discovery.registry import applicable as bank_applicable
from trading_research.research.rule_discovery.search import (
    B02_FAMILIES,
    CONTROL_BRANCH,
    CONTROL_DATES,
    THROUGHPUT_CANDIDATE_IDS,
    check_causal_parameters,
    cutoff_ns,
    load_b02_market,
    load_bank,
    market_for_family,
    negative_control_pair,
    resolve_bank,
    resolve_candidate,
    scan_candidate,
    serialize_scan_bytes,
    write_control_scan,
)
from trading_research.research.rule_discovery.source_adapters.common import install_write_guard

ATTEMPT = Path(__file__).resolve().parents[2] / "reports/research-work/P15-17/47dedaaa4f5b9ce1"
FIXTURE_DAY = "2021-01-04"
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
    if bank == "Formation":
        left = left_map.get("reference") or {}
        right = right_map.get("reference") or {}
        lo = left.get("operands") or {}
        ro = right.get("operands") or {}
        if any(lo.get(key) != ro.get(key) for key in ("box_low", "box_high", "level") if key in lo):
            return True
        return (left_map.get("context") or {}).get("at_ns") != (right_map.get("context") or {}).get("at_ns")
    if bank == "Profile":
        return (left_map.get("reference") or {}).get("operands", {}).get("prior_vah") != (
            right_map.get("reference") or {}
        ).get("operands", {}).get("prior_vah")
    if bank == "Reference":
        lo = (left_map.get("reference") or {}).get("operands") or {}
        ro = (right_map.get("reference") or {}).get("operands") or {}
        return lo.get("asia_high") != ro.get("asia_high") or lo.get("london_high") != ro.get("london_high")
    if bank == "Delta":
        left = left_map.get("confirmation") or {}
        right = right_map.get("confirmation") or {}
        if left.get("verdict") != right.get("verdict"):
            return True
        return (left.get("operands") or {}).get("arrival_ratio") != (right.get("operands") or {}).get("arrival_ratio")
    if bank == "Sequence":
        deadline_s = int(item.parameters.get("deadline_s") or 600)
        for name in item.hooks:
            if name not in left_map:
                continue
            left_at = left_map[name].get("at_ns")
            right_at = right_map[name].get("at_ns")
            if left_at is not None and right_at == int(left_at) + deadline_s * NS:
                return True
        return False
    if bank == "Memory":
        left = left_map.get("location") or {}
        right = right_map.get("location") or {}
        return left.get("verdict") != right.get("verdict") or left.get("at_ns") != right.get("at_ns")
    if bank == "Timing":
        left = left_map.get("trigger") or {}
        right = right_map.get("trigger") or {}
        if (right.get("operands") or {}).get("in_modal_window") is True and (left.get("operands") or {}).get(
            "in_modal_window"
        ) is False:
            return True
        expiry_s = int(item.parameters.get("expiry_s_after_qual") or 3600)
        return left.get("at_ns") is not None and right.get("at_ns") == int(left["at_ns"]) + expiry_s * NS
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
    install_write_guard()
    market = load_b02_market(FIXTURE_DAY)
    resolved_map = {item.candidate_id: item for item in resolve_bank()}
    seen_banks = set()
    for cid in THROUGHPUT_CANDIDATE_IDS:
        item = resolved_map[cid]
        assert item.supported, (cid, item.unsupported_reason)
        seen_banks.add(item.bank)
        from trading_research.research.rule_discovery.search import scan_b02_baseline

        baseline = scan_b02_baseline(market, item.family, item.branch)
        candidate = scan_candidate(market, item)
        assert serialize_scan_bytes(baseline) != serialize_scan_bytes(candidate)
        baseline_eps = list(baseline.get("episodes") or [])
        candidate_eps = list(candidate.get("episodes") or [])
        assert len(candidate_eps) == len(baseline_eps)
        assert candidate_eps, cid
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
                assert record == right_map[name]
            if _assert_predicted_direction(item.bank, left_map, right_map, item):
                predicted = True
        assert real, cid
        assert predicted, cid
    assert seen_banks == {"Formation", "Profile", "Reference", "Delta", "Sequence", "Memory", "Timing"}


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
    assert len(unsupported) == 8
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
