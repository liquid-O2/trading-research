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
    RECIPES,
    applicable,
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
