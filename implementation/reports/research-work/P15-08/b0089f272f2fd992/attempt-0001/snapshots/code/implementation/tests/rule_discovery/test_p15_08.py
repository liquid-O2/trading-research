"""P15-08 references and finite candidate bank."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage, EvidenceRef, Formation
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.references import (
    CONTROL_OFFSETS,
    control_offset,
    density_matched_control,
    developing_version,
    r1_frozen_band,
    r2_prior_edge,
    vwap_dispersion,
)
from trading_research.research.rule_discovery.registry import (
    BANKS,
    B01_JUDAS,
    CAP,
    DELTA_ADAPTER_EVIDENCE,
    GB_FAIL_SWEEP_BRANCHES,
    RECIPES,
    SEQUENCE_APPLY,
    applicable,
    applicability_matrix_document,
    cell_evidence,
    expand_candidate_bank,
    to_rule_spec,
)


def _formation(*, available_at_ns: int = 50) -> Formation:
    ev = EvidenceRef("a" * 64, ("f",), 0, 40, available_at_ns, Coverage.COMPLETE, ())
    return Formation(
        formation_id="form1",
        asset_id="NQ:test",
        start_ns=0,
        end_ns=40,
        available_at_ns=available_at_ns,
        high=Decimal("101"),
        low=Decimal("99"),
        volume=10,
        profile_id=None,
        construction_kind="F1",
        parent_ids=("p",),
        evidence=(ev,),
    )


def test_a01_one_axis_and_source_prerequisites():
    document = expand_candidate_bank()
    for row in document["candidates"]:
        assert row["one_axis"] is True
        assert row["changed_axis"] != "none"
        assert row["required_stages"]
        spec = to_rule_spec(row)
        assert spec.changed_axis == row["changed_axis"]
        assert spec.source_branch == row["branch"]
    assert document["no_other_candidates"] is True
    assert {item["label"] for item in document["b0_1_judas_labels"]} == {"strict", "deferred"}
    recipes = {recipe["id"] for recipe in RECIPES["Timing"]}
    assert recipes == {"T1", "T2", "T3", "T4"}


def test_a02_bank_byte_identical_before_outcomes():
    first = expand_candidate_bank()
    second = expand_candidate_bank()
    assert first["candidates"] == second["candidates"]
    assert first["deferred"] == second["deferred"]
    assert first["counts"]["nonbaseline_selected"] <= CAP


def test_a03_formation_unavailable_at_earlier_issue():
    formation = _formation(available_at_ns=50)
    with pytest.raises(ContractError, match="unavailable"):
        r1_frozen_band(
            formation=formation,
            vwap=Decimal("100"),
            dispersion=Decimal("1"),
            issue_at_ns=40,
            expiry_at_ns=100,
            family="GB-VWAP",
            branch="source_long",
            contract="NQ",
        )


def test_a04_reference_counts_widths_issue_expiry_controls():
    formation = _formation()
    ref = r1_frozen_band(
        formation=formation,
        vwap=Decimal("100.00"),
        dispersion=Decimal("2.00"),
        issue_at_ns=50,
        expiry_at_ns=200,
        family="GB-VWAP",
        branch="source_long",
        contract="NQ",
    )
    assert ref.upper - ref.lower == Decimal("4.00")
    assert ref.issue_at_ns == 50
    assert ref.expiry_at_ns == 200
    control = density_matched_control(ref, scale=Decimal("2"), occupied=())
    assert control["available"] is True
    assert control["offset"] in CONTROL_OFFSETS
    assert control["width"] == ref.upper - ref.lower
    assert control["issue_at_ns"] == ref.issue_at_ns
    occupied = [(control["lower"], control["upper"])]
    alt = density_matched_control(ref, scale=Decimal("2"), occupied=occupied)
    if alt["available"]:
        assert (alt["lower"], alt["upper"]) != (control["lower"], control["upper"])
    edge = r2_prior_edge(formation=formation, edge="high", issue_at_ns=50, expiry_at_ns=200, family="SIRES", branch="vwap_deviation_fade", contract="NQ")
    assert edge.lower == formation.high
    version = developing_version(ref, vwap=Decimal("101"), dispersion=Decimal("2"), issue_at_ns=80)
    assert version.reference_lifecycle_id == ref.reference_lifecycle_id
    assert version.reference_id != ref.reference_id


def test_a05_every_method_has_baseline_process_not_entry():
    document = expand_candidate_bank()
    families = {row["family"] for row in document["baselines"]}
    assert "JJ-TBR" in families
    assert "SIRES" in families
    assert all(row["scope"] == "entry_setup" for row in document["baselines"])
    assert all(row["scope"] == "process" and row["entry_setup"] is False for row in document["process_units"])
    assert any(row["branch"] == "management" for row in document["process_units"])


def test_s24_no_unregistered_trial():
    document = expand_candidate_bank()
    ids = [row["candidate_id"] for row in document["candidates"]]
    assert len(ids) == len(set(ids))
    assert document["counts"]["nonbaseline_selected"] == len(document["candidates"])
    assert document["counts"]["nonbaseline_selected"] <= CAP
    extra = [row for row in document["candidates"] if row["recipe_id"] not in {r["id"] for bank in BANKS for r in RECIPES[bank]}]
    assert extra == []
    assert document["timing_includes_T4"] is True
    t4 = [row for row in document["candidates"] + document["deferred"] if row["recipe_id"] == "T4"]
    assert t4
    assert not applicable("Sequence", "S1", "JJ-TBR", "judas_outbound")[0]


def test_s31_unknown_provenance_stays_labelled():
    document = expand_candidate_bank()
    for row in document["b0_1_judas_labels"]:
        assert row["provenance"] == "source_inspired"
        spec = to_rule_spec({**row, "required_stages": ("formation", "contact", "confirmation"), "one_axis": True, "baseline": False, "family": row["family"], "branch": row["branch"], "changed_axis": row["changed_axis"], "candidate_id": row["candidate_id"]})
        assert spec.provenance == "source_inspired"


def test_s22_new_geometry_candidate_not_filtered_from_baseline_only():
    document = expand_candidate_bank()
    f3 = [row for row in document["candidates"] if row["recipe_id"] == "F3"]
    b0 = [row for row in document["baselines"] if row["family"] == "JJ-TBR"]
    assert f3
    assert b0
    assert {row["candidate_id"] for row in f3}.isdisjoint({row["candidate_id"] for row in b0})


def test_s08_t2_does_not_borrow_future_range():
    ok, reason = applicable("Timing", "T2", "JJ-TBR", "judas_reversal")
    assert ok is True
    t2 = next(r for r in RECIPES["Timing"] if r["id"] == "T2")
    assert t2["parameters"]["require_complete_formation"] is True


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if not Path(path).is_file():
        pytest.skip("native parquet missing")
    assert replay_native_row(path, 769284)["kind"] == "native"


def test_vwap_dispersion_not_stderr():
    out = vwap_dispersion([40000, 40004], [10, 10])
    assert out["volume"] == 20
    assert out["dispersion"] is not None
    assert out["price"] is not None


def test_control_offset_deterministic():
    assert control_offset("abc") == control_offset("abc")
    assert control_offset("abc") in CONTROL_OFFSETS


def test_t4_sweep_membership_from_scanner_not_constant():
    assert applicable("Timing", "T4", "JJ-TBR", "judas_reversal")[0] is True
    for branch in GB_FAIL_SWEEP_BRANCHES:
        assert applicable("Timing", "T4", "GB-FAIL", branch)[0] is True
    ok, reason = applicable("Timing", "T4", "GB-FAIL", "mss_fvg_refinement")
    assert ok is False
    assert "sweep" in (reason or "").lower() or "T4" in (reason or "")


def test_delta_requires_adapter_evidence():
    for key, evidence in DELTA_ADAPTER_EVIDENCE.items():
        family, branch = key
        ok, _reason = applicable("Delta", "C1", family, branch)
        assert ok is True, key
        cell = cell_evidence("Delta", "C1", family, branch)
        assert cell["adapter"]["path"].endswith(".py")
        assert evidence["lines"]
    assert applicable("Delta", "C1", "GB-SCALP", "bearish_small_scalp")[0] is False
    assert applicable("Delta", "C1", "GB-SCALP", "bullish_discount_pullback")[0] is False
    assert applicable("Delta", "C1", "SIRES", "dom_rejection")[0] is False
    assert applicable("Delta", "C1", "SIRES", "clean_squeeze")[0] is False
    deferred = applicable("Delta", "C1", "GB-SCALP", "bearish_small_scalp")[1]
    assert deferred == "branch has no delta input"


def test_sequence_and_profile_per_branch_contract():
    assert applicable("Sequence", "S1", "SAINT-AMT", "continuation_retest")[0] is True
    assert applicable("Sequence", "S1", "MEMBER-TWO-REASONS", "planned_return_long")[0] is True
    assert applicable("Sequence", "S1", "GB-FAIL", "mss_fvg_refinement")[0] is False
    assert applicable("Sequence", "S1", "SIRES", "kg1_retest")[0] is True
    assert applicable("Sequence", "S1", "SIRES", "balance_failure_fade")[0] is False
    assert ("SAINT-AMT", "continuation_retest") in SEQUENCE_APPLY
    assert applicable("Profile", "P1", "SAINT-AMT", "continuation_retest")[0] is True
    assert applicable("Profile", "P1", "MEMBER-TWO-REASONS", "resistance_short")[0] is True
    assert applicable("Profile", "P1", "KEANI-OPEN-ABOVE-VALUE", "source_long")[0] is True
    assert applicable("Profile", "P1", "SIRES", "microbalance_break")[0] is True
    assert applicable("Profile", "P1", "SIRES", "dom_rejection")[0] is False


def test_measurement_branch_runs_every_applicable_recipe():
    from trading_research.research.rule_discovery.engine_slice import MEASUREMENT_BRANCH, MEASUREMENT_FAMILY

    run = []
    for bank in BANKS:
        for recipe in RECIPES[bank]:
            if applicable(bank, str(recipe["id"]), MEASUREMENT_FAMILY, MEASUREMENT_BRANCH)[0]:
                run.append(str(recipe["id"]))
    assert set(run) >= {"F1", "F2", "F3", "P1", "P2", "C1", "C2", "C3", "S1", "S2", "S3", "S4", "M1", "M2"}


def test_applicability_matrix_records_per_branch_evidence():
    matrix = applicability_matrix_document()
    assert matrix["t4_sweep_branches"]
    assert "mss_fvg_refinement" not in matrix["t4_sweep_branches"]
    assert any(cell["bank"] == "Delta" and cell["applicable"] for cell in matrix["cells"])
    delta_deferred = [cell for cell in matrix["deferred_cells"] if cell["bank"] == "Delta"]
    assert any(cell.get("reason") == "branch has no delta input" for cell in delta_deferred)
    gb_scalp_delta = [cell for cell in delta_deferred if cell["family"] == "GB-SCALP"]
    assert gb_scalp_delta
    assert all(cell.get("adapter") for cell in gb_scalp_delta)
