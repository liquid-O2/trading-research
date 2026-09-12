"""Bound C01 fixtures and report checks for the GB-SCALP slice."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from trading_research.research.method_pack.catalog import BRANCHES, objects_for
from trading_research.research.method_pack.evidence import parse_manifest, score_episode
from trading_research.research.method_pack.method_slices import m04
from trading_research.research.method_pack.objects import run_object_fixtures
from trading_research.research.method_pack.protocol import jsonable


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "implementation/tools/run_phase1_objects.py"


def _score(document):
    candidates, objects, assertions, evidence = parse_manifest(document, m04.METHOD)
    return score_episode(next(iter(candidates.values())), objects, assertions, evidence)


def test_m04_inventory_and_bounded_source_cases():
    assert objects_for(m04.METHOD) == [
        "O001", "O002", "O003", "O004", "O029", "O046", "O053", "O059",
        "O136", "O139", "O140", "O141", "O142", "O145", "O150",
    ]
    assert BRANCHES[m04.METHOD] == [
        "bearish_small_scalp", "bullish_discount_pullback",
    ]
    rows = {row["id"]: row for row in m04.method_fixtures()}
    assert all(row["status"] == "pass" for row in rows.values())
    assert rows["M04-F1"]["actual_value"]["verdict"] == "pass"
    assert rows["M04-F1-bullish"]["actual_value"]["verdict"] == "pass"
    assert rows["M04-F2-late-direction"]["actual_value"]["verdict"] == "fail"
    assert rows["M04-F2-wrong-side"]["actual_value"]["verdict"] == "fail"
    assert rows["M04-F2-large-size"]["actual_value"]["verdict"] == "fail"


def test_m04_f1_retains_the_literal_times_size_side_and_management_reference():
    row = {item["field"]: item for item in m04.method_fixtures()[0]["inputs"]["assertions"]}
    payload = m04.method_fixtures()[0]["inputs"]["evidence"][0]["payload"]
    assert payload["direction_at"] == m04._t(9, 30)
    assert payload["pullback_at"] == m04._t(9, 40)
    assert payload["size_contracts"] == 1
    assert payload["small_size_limit"] == 1
    assert payload["size_at"] == m04._t(9, 39)
    assert payload["entry_at"] == m04._t(9, 41)
    assert payload["direction_side"] == "bearish"
    assert payload["management_points"] == "20"
    assert payload["management_at"] == m04._t(9, 42)
    assert row["direction_recorded_before_entry"]["known_at"] == m04._t(9, 30)
    assert row["small_size_recorded"]["known_at"] == m04._t(9, 39)
    assert row["source_directional_pullback_observed"]["known_at"] == m04._t(9, 40)
    assert row["source_scalp_management_recorded"]["known_at"] == m04._t(9, 42)


def test_m04_automatic_admission_is_null_with_all_source_definition_holes():
    rows = {row["id"]: row for row in m04.method_fixtures()}
    for fid in ("M04-F1-automatic", "M04-F1-bullish-automatic", "M04-F3-automatic"):
        actual = rows[fid]["actual_value"]
        assert actual["sequence_ok"] is None
        assert actual["verdict"] == "unknown"
        assert actual["coverage_ok"] is None
        fields = {hole["missing_fields"][0] for hole in actual["holes"]
                  if hole["kind"] == "source_definition"}
        assert {"entry_trigger", "measured_impulse", "invalidation", "exit_algorithm"} <= fields
        policy = next(hole for hole in actual["holes"]
                      if hole["missing_fields"] == ["general_target_policy"])
        assert policy["affected_output"] == "target_policy"


def test_m04_stage_caps_and_causal_mutations_use_c01_records():
    assert m04.STAGE_LIMITS == {
        "direction_recorded_before_entry": "direction_at",
        "small_size_recorded": "size_at",
        "source_directional_pullback_observed": "pullback_at",
        "source_scalp_management_recorded": "management_at",
    }
    rows = {row["id"]: row for row in m04.method_fixtures()}
    late = rows["M04-F1:late"]["actual_value"]
    assert late["verdict"] == "fail"
    assert late["detected_causal_violations"] > 0
    assert rows["M04-F1:missing"]["actual_value"]["verdict"] == "unknown"
    assert "HOLE:O059:small_size_recorded" in rows["M04-F1:missing"]["actual_value"]["hole_ids"]
    identity = rows["M04-F1:identity"]["actual_value"]
    assert identity["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in identity["holes"])


def test_m04_object_fixtures_cover_all_mapped_objects_and_c08_mutations():
    object_ids = objects_for(m04.METHOD)
    rows = run_object_fixtures(object_ids)
    assert rows
    assert all(row["status"] == "pass" for row in rows)
    for object_id in object_ids:
        assert any(row["id"] == f"{object_id}-F1" for row in rows)
        kinds = {row["kind"] for row in rows if row["recipe"] == object_id}
        assert {"c08_late", "c08_missing", "c08_identity"} <= kinds


def test_m04_empty_acquired_pass_separates_implementation_checks_and_discovery(tmp_path):
    data = tmp_path / "empty-data"
    reports = tmp_path / "reports"
    data.mkdir()
    result = subprocess.run([
        sys.executable, str(RUNNER), "method-pass", "--method", m04.METHOD,
        "--scope", "acquired", "--data-root", str(data), "--report-root", str(reports),
        "--formula-version", "method-pack-v1",
    ], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((reports / "gb-scalp.json").read_text())
    assert report["status"] == "checks_passed"
    assert report["summary"]["N"] == 0
    assert len(report["branches"]) == 2
    assert report["quality"]["fixture_failures"] == 0


def test_m04_disposable_manifest_still_uses_the_production_expression():
    document = m04._document("disposable", "case_description", m04._positive_case())
    encoded = json.loads(json.dumps(jsonable(document)))
    result = _score(encoded)
    assert result["sequence_ok"] is True
    assert result["verdict"] == "pass"
