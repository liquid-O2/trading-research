"""Executable checks for the reviewed range/profile/auction obligation ledger."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from trading_research.research.method_pack.contracts import OUTPUT_SCHEMAS, validate_output
from trading_research.research.method_pack.objects import FIXTURES
from trading_research.research.method_pack.objects import native_boundary
from trading_research.research.method_pack.protocol import c08_mutations, run_fixture_spec, run_recipe


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "implementation/validation/phase1-completion/geometry-obligations.json"
NATIVE = ROOT / "implementation/validation/phase1-completion/native-geometry.json"
OWNED = {"O002", *{f"O{number:03}" for number in range(5, 30)},
         *{f"O{number:03}" for number in range(46, 98)}}


def _schema(recipe_id):
    return {name: {"nullable": field.nullable,
                   "types": [kind.__name__ for kind in field.types]}
            for name, field in OUTPUT_SCHEMAS[recipe_id].items()}


def test_every_owned_geometry_fixture_matches_reviewed_expectations():
    fixtures = [fixture for fixture in FIXTURES if fixture["recipe"] in OWNED]
    assert {fixture["recipe"] for fixture in fixtures} == OWNED
    failures = []
    for fixture in fixtures:
        row = run_fixture_spec(fixture)
        if row["status"] != "pass":
            failures.append((fixture["id"], row["failures"]))
        validate_output(run_recipe(fixture["recipe"], deepcopy(fixture["inputs"])))
        failures.extend((mutation["id"], mutation["failures"])
                        for mutation in c08_mutations(fixture)
                        if mutation["status"] != "pass")
    assert not failures


def test_geometry_obligation_ledger_binds_semantics_schema_evidence_and_limits():
    document = json.loads(LEDGER.read_text())
    assert document["schema"] == "phase1-geometry-obligations-v1"
    assert document["object_count"] == 78
    records = {record["object_id"]: record for record in document["objects"]}
    assert set(records) == OWNED and len(records) == len(document["objects"])

    test_sources = "\n".join(path.read_text() for path in (
        ROOT / "implementation/tests/test_phase1_geometry_obligations.py",
        ROOT / "implementation/tests/test_phase1_range_geometry.py",
        ROOT / "implementation/tests/test_phase1_complete_profiles.py",
        ROOT / "implementation/tests/test_phase1_profile_integration.py",
        ROOT / "implementation/tests/test_phase1_auction_geometry.py",
    ))
    for recipe_id, record in records.items():
        assert len(record["implemented_obligation"].split()) >= 12
        assert len(record["genuine_limits"].split()) >= 8
        assert record["meaningful_schema"] == _schema(recipe_id)
        assert record["native_producer"] is (recipe_id in native_boundary.NATIVE_PRODUCERS)
        expected_fixtures = [fixture["id"] for fixture in FIXTURES
                             if fixture["recipe"] == recipe_id]
        assert record["evidence"]["fixture_ids"] == expected_fixtures
        assert expected_fixtures
        assert all(f"def {name}(" in test_sources
                   for name in record["sensitive_regression_tests"])


def test_native_geometry_controls_reconcile_and_preserve_declared_holes():
    document = json.loads(NATIVE.read_text())
    controls = document["controls"]
    assert set(controls) == {"feb24_jj_range", "june12_tpo_ib",
                             "june12_disjoint_composite", "june12_sires_overnight"}
    assert controls["feb24_jj_range"]["reconciliation"] == {
        "W_equals_H_minus_L": True, "derived_parent_ids_exact": True}
    tpo = controls["june12_tpo_ib"]
    assert tpo["source_letter_window"] is None
    assert "comparison" in tpo["construction_status"]
    composite = controls["june12_disjoint_composite"]["reconciliation"]
    assert composite["overlapping_native_event_ids"] == 0
    assert composite["constituent_total"] == composite["composite_total"]
    overnight = controls["june12_sires_overnight"]
    assert overnight["clock"]["verified_native_members"] is True
    assert {obj["recipe_id"] for obj in overnight["objects"]} == {"O011", "O073"}
    o073 = next(obj for obj in overnight["objects"] if obj["recipe_id"] == "O073")
    assert o073["state"] == "hole" and o073["recipe_base_ok"] is True
    assert "unpublished LVN selection algorithm" in overnight["source_unknowns"]
