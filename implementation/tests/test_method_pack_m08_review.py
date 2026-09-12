"""Adversarial review checks for the KEANI M08 C01 evidence boundary.

These tests stay on the supplied-manifest path.  They do not open acquired
data or exercise unrelated object recipes.
"""

from __future__ import annotations

from trading_research.research.method_pack.evidence import parse_manifest, score_episode
from trading_research.research.method_pack.method_slices import m08


def _score(document):
    candidates, objects, assertions, evidence = parse_manifest(document, m08.METHOD)
    candidate = next(iter(candidates.values()))
    return score_episode(candidate, objects, assertions, evidence)


def _objects(document):
    return {row["object_id"]: row for row in document["objects"]}


def _evidence(document):
    return {row["evidence_id"]: row for row in document["evidence"]}


def test_m08_fixture_uses_the_literal_whole_a_and_break_retest_contract():
    op = m08._positive()
    assert op["a_start_at"] == m08._t(9, 30)
    assert op["a_end_at"] == m08._t(10, 0)
    assert op["a_low"] == 101
    assert op["prior_vah"] == 100
    assert op["dev_vah_known_at"] == m08._t(10, 2)
    assert op["breakout_at"] == m08._t(10, 5)
    assert op["retest_at"] == m08._t(10, 7)
    assert op["defense_at"] == m08._t(10, 8)
    assert op["decision_at"] == m08._t(10, 9)
    assert op["imbalance_band"][0] == 104
    assert str(op["imbalance_band"][1]) == "104.5"
    assert _score(m08._document("review-f1", op))["verdict"] == "pass"


def test_m08_whole_a_object_cannot_change_period_or_minimum_after_binding():
    for field, value in (
        ("a_start_at", m08._t(9, 31)),
        ("a_end_at", m08._t(9, 59)),
        ("a_low", 100),
    ):
        fid = f"review-a-{field}"
        document = m08._document(fid, m08._positive())
        objects = _objects(document)
        evidence = _evidence(document)
        # Keep the mutation internally supported by its source record, so the
        # result exercises the semantic audit rather than a schema exception.
        for obj in objects.values():
            if field in obj.get("value", {}):
                obj["value"][field] = value
                for evidence_id in obj["evidence_ids"]:
                    evidence[evidence_id]["payload"][field] = value
        result = _score(document)
        assert result["sequence_ok"] is False or result["verdict"] == "fail"
        assert result["verdict"] == "fail"


def test_m08_prior_and_developing_snapshots_cannot_alias_evidence_ids():
    fid = "review-snapshot-evidence-alias"
    document = m08._document(fid, m08._positive())
    objects = _objects(document)
    prior = objects[f"{fid}:o:prior_vah"]
    developing = objects[f"{fid}:o:dev_vah_at_break"]
    developing["evidence_ids"] = list(prior["evidence_ids"])
    result = _score(document)
    assert result["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in result["holes"])


def test_m08_imbalance_must_keep_the_developing_snapshot_parent():
    fid = "review-imbalance-parent"
    document = m08._document(fid, m08._positive())
    objects = _objects(document)
    imbalance = objects[f"{fid}:o:aggressive_buy_imbalance_break"]
    imbalance["parent_ids"] = []
    result = _score(document)
    assert result["verdict"] == "fail"
    assert any("developing" in hole["reason"].lower() or "parent" in hole["reason"].lower()
               for hole in result["holes"])


def test_m08_missing_diagonal_source_config_in_bound_evidence_is_unknown():
    fid = "review-missing-diagonal-config"
    document = m08._document(fid, m08._positive())
    objects = _objects(document)
    evidence = _evidence(document)
    imbalance = objects[f"{fid}:o:aggressive_buy_imbalance_break"]
    for evidence_id in imbalance["evidence_ids"]:
        evidence[evidence_id]["payload"].pop("diagonal_settings", None)
    result = _score(document)
    assert result["verdict"] == "unknown"
    assert result["coverage_ok"] is None
    assert any("source" in hole["reason"].lower() or "settings" in hole["reason"].lower()
               for hole in result["holes"])


def test_m08_defense_before_retest_fails_the_literal_order():
    fid = "review-defense-too-early"
    document = m08._document(fid, m08._positive())
    objects = _objects(document)
    evidence = _evidence(document)
    early = m08._t(10, 6)
    defense = objects[f"{fid}:o:defense_at"]
    defense["value"]["defense_at"] = early
    for evidence_id in defense["evidence_ids"]:
        evidence[evidence_id]["payload"]["defense_at"] = early
    result = _score(document)
    assert result["sequence_ok"] is False
    assert result["verdict"] == "fail"


def test_m08_developing_vah_known_after_break_is_a_causal_failure():
    fid = "review-late-developing-snapshot"
    document = m08._document(fid, m08._positive())
    objects = _objects(document)
    evidence = _evidence(document)
    late = m08._t(10, 6)
    snapshot = objects[f"{fid}:o:dev_vah_at_break"]
    snapshot.update(known_at=late, as_of=late, formation_start=late, formation_end=late)
    for evidence_id in snapshot["evidence_ids"]:
        evidence[evidence_id].update(known_at=late, observation_start=late, observation_end=late)
    result = _score(document)
    assert result["verdict"] == "fail"
    assert result["detected_causal_violations"] > 0


def test_m08_retest_on_a_foreign_band_is_not_a_same_imbalance_retest():
    fid = "review-foreign-retest-band"
    document = m08._document(fid, m08._positive())
    retest = _objects(document)[f"{fid}:o:retest_at"]
    retest["band_id"] = "foreign-band"
    result = _score(document)
    assert result["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in result["holes"])
