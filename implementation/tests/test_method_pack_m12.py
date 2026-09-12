from decimal import Decimal

from trading_research.research.method_pack.catalog import BRANCHES, objects_for
from trading_research.research.method_pack.method_slices import m12


def _rows():
    return {row["id"]: row for row in m12.method_fixtures()}


def test_m12_inventory_and_all_declared_cases_run_at_c01_boundary():
    assert objects_for("STOIC-RISK") == [
        "O001", "O002", "O003", "O140", "O148", "O153", "O154", "O155",
    ]
    assert BRANCHES["STOIC-RISK"] == ["first", "second", "reset_after_second_win"]
    rows = _rows()
    assert len(rows) == 15
    assert all(row["status"] == "pass" for row in rows.values())
    assert all(row["predicate"] == "printed_ladder" for row in rows.values())


def test_m12_f1_fixed_baseline_actual_trades_and_reset_geometry():
    rows = _rows()
    first, second, reset = (rows[name] for name in
                            ("M12-F1-first", "M12-F1-second", "M12-F1-reset"))
    assert [row["actual_value"]["verdict"] for row in (first, second, reset)] == [
        "pass", "pass", "pass",
    ]
    p1 = first["inputs"]["evidence"][0]["payload"]
    p2 = second["inputs"]["evidence"][0]["payload"]
    p3 = reset["inputs"]["evidence"][0]["payload"]
    assert p1["equity_baseline"]["E0"] == "10000"
    assert p1["equity_baseline"]["B"] == "100"
    assert p1["equity_baseline"]["fixed"] is True
    assert (p1["planned_risk_amount"], p1["planned_reward_amount"]) == ("100", "300")
    assert (p2["planned_risk_amount"], p2["planned_reward_amount"]) == ("400", "1200")
    assert p2["closed_trade_records"][0]["result_amount"] == "300"
    assert p2["closed_trade_records"][0]["closed_at"] < p2["decision_at"]
    assert p3["cumulative_result_amount"] == "1500"
    assert p3["next_risk_amount"] == "100"
    second_trade = next(row for row in p3["closed_trade_records"]
                        if row["trade_id"] == p3["stage_parent_trade_id"])
    first_trade = next(row for row in p3["closed_trade_records"]
                       if row["trade_id"] == second_trade["parent_trade_id"])
    assert first_trade["closed_at"] < second_trade["closed_at"] < p3["decision_at"]


def test_m12_validation_has_actual_100_record_cohort_and_metric_ids():
    row = _rows()["M12-F1-first"]
    payload = row["inputs"]["evidence"][0]["payload"]
    records = payload["prior_trade_records"]
    assert len(records) == len(payload["prior_sample_ids"]) == 100
    assert [record["trade_id"] for record in records] == payload["prior_sample_ids"]
    assert {record["process_id"] for record in records} == {payload["process_id"]}
    assert all(record["closed_at"] <= payload["validation_known_at"] < payload["decision_at"]
               for record in records)
    assert payload["win_rate_record"]["metric_id"]
    assert payload["average_rr_record"]["metric_id"]
    assert payload["mc_record"]["result_id"] and payload["mc_record"]["design_id"]
    assert payload["mc_record"]["supplied_result"] is True
    assert "simulation_run_by_pack" not in payload
    assert "profitability_asserted" not in payload and "entry_created" not in payload


def test_m12_actual_parent_graph_links_cohort_outcome_validation_equity_stage():
    row = _rows()["M12-F1-second"]
    payload = row["inputs"]["evidence"][0]["payload"]
    ids = payload["support_object_ids"]
    objects = {obj["object_id"]: obj for obj in row["inputs"]["objects"]}
    assert objects[ids["cohort"]]["recipe_id"] == "O148"
    assert objects[ids["outcomes"]]["parent_ids"] == [ids["cohort"]]
    assert set(objects[ids["validation"]]["parent_ids"]) == {ids["cohort"], ids["outcomes"]}
    assert objects[ids["equity"]]["recipe_id"] == "O140"
    assert set(objects[ids["stage"]]["parent_ids"]) == {
        ids["validation"], ids["equity"], ids["trades"],
    }
    assert {objects[ids[name]]["recipe_id"] for name in ids} == {
        "O140", "O148", "O153", "O154", "O155",
    }


def test_m12_negative_controls_fail_with_specific_evidence():
    rows = _rows()
    not_closed = rows["M12-F2-not-closed"]["actual_value"]
    assert not_closed["verdict"] == "fail"
    assert any("actual same-process closed first +3B trade" in h["reason"]
               for h in not_closed["holes"])
    rebase = rows["M12-F2-rebase-412"]["actual_value"]
    assert rebase["verdict"] == "fail"
    assert any("updated equity" in h["reason"] for h in rebase["holes"])
    for fid in ("M12-F2-n99", "M12-F2-base-1.01pct", "M12-F2-unvalidated"):
        assert rows[fid]["actual_value"]["verdict"] == "fail"

    from trading_research.research.method_pack.evidence import parse_manifest, score_episode

    document = m12._document("branch-mismatch", m12._base("first"))
    document["candidates"][0]["branch"] = "second"
    for obj in document["objects"]:
        obj["branch_scope"] = ["second"]
    for assertion in document["assertions"]:
        assertion["branch"] = "second"
    for evidence in document["evidence"]:
        evidence["branch"] = "second"
    candidates, objects, assertions, evidence = parse_manifest(document, "STOIC-RISK")
    mismatch = score_episode(next(iter(candidates.values())), objects, assertions, evidence)
    assert mismatch["verdict"] == "fail"
    assert any("risk stage does not match" in hole["reason"] for hole in mismatch["holes"])


def test_m12_source_holes_stay_unknown():
    rows = _rows()
    for fid, phrase in (
        ("M12-F3-mc", "mc_loss_streak_known"),
        ("M12-F3-activation", "heading and printed ladder conflict"),
        ("M12-F3-after-loss", "second loss is unpublished"),
        ("M12-F3-rebase-policy", "rebasing"),
    ):
        actual = rows[fid]["actual_value"]
        assert actual["verdict"] == "unknown" and actual["hole_ids"]
        assert phrase in str(actual)


def test_m12_reset_uses_opaque_trade_links_and_observed_close_cash_geometry():
    from trading_research.research.method_pack.evidence import parse_manifest, score_episode

    def score(op, fid):
        document = m12._document(fid, op)
        candidates, objects, assertions, evidence = parse_manifest(document, "STOIC-RISK")
        return score_episode(next(iter(candidates.values())), objects, assertions, evidence)

    opaque = m12._base("reset_after_second_win")
    first, second = opaque["closed_trade_records"]
    first["trade_id"] = "opaque-7e91"
    second.update(trade_id="opaque-c204", parent_trade_id="opaque-7e91")
    opaque["stage_parent_trade_id"] = "opaque-c204"
    assert score(opaque, "opaque-reset")["verdict"] == "pass"

    reversed_closes = m12._base("reset_after_second_win")
    reversed_closes["closed_trade_records"][0]["closed_at"] = m12._t(10, 30)
    reversed_closes["closed_trade_records"][1]["closed_at"] = m12._t(10, 15)
    reversed_closes["second_trade_close_at"] = m12._t(10, 15)
    result = score(reversed_closes, "reversed-reset")
    assert result["verdict"] == "fail"
    assert any("close order" in hole["reason"] for hole in result["holes"])

    wrong_cash = m12._base("reset_after_second_win")
    wrong_cash["closed_trade_records"][1]["result_amount"] = "1199"
    result = score(wrong_cash, "wrong-cash-reset")
    assert result["verdict"] == "fail"
    assert any("cash amounts" in hole["reason"] for hole in result["holes"])

    missing_cash = m12._base("reset_after_second_win")
    missing_cash["closed_trade_records"][1].pop("result_amount")
    result = score(missing_cash, "missing-cash-reset")
    assert result["verdict"] == "unknown"
    assert any("cash geometry is missing" in hole["reason"] for hole in result["holes"])


def test_m12_missing_source_details_are_unknown_and_fixture_attestations_not_required():
    from trading_research.research.method_pack.evidence import parse_manifest, score_episode

    def score(op, fid):
        document = m12._document(fid, op)
        candidates, objects, assertions, evidence = parse_manifest(document, "STOIC-RISK")
        return score_episode(next(iter(candidates.values())), objects, assertions, evidence)

    missing_time = m12._base("first")
    missing_time["validation_known_at"] = None
    missing_time["validation_record"]["known_at"] = None
    result = score(missing_time, "missing-validation-time")
    assert result["verdict"] == "unknown"
    assert any("validation availability is missing" in hole["reason"]
               for hole in result["holes"])

    missing_prior = m12._base("first")
    missing_prior.pop("prior_trade_records")
    assert score(missing_prior, "missing-prior-records")["verdict"] == "unknown"

    missing_metric = m12._base("first")
    missing_metric.pop("win_rate_record")
    assert score(missing_metric, "missing-win-rate-record")["verdict"] == "unknown"

    missing_amount = m12._base("first")
    missing_amount.pop("planned_reward_amount")
    result = score(missing_amount, "missing-first-amount")
    assert result["verdict"] == "unknown"
    assert any("risk or reward amount is missing" in hole["reason"]
               for hole in result["holes"])

    no_attestations = m12._base("first")
    no_attestations["activation_conflict_preserved"] = False
    result = score(no_attestations, "no-fixture-attestations")
    assert result["verdict"] == "pass"
    assert any(hole.get("affects_admission") is False
               and "activation remains unresolved" in hole["reason"]
               for hole in result["holes"])

    unsupported = m12._base("first")
    unsupported.update(simulation_run_by_pack=True, entry_created=True,
                       profitability_asserted=True)
    assert score(unsupported, "unsupported-claims")["verdict"] == "fail"

    missing_stage_doc = m12._document("missing-risk-stage", m12._base("first"))
    missing_stage_doc["candidates"][0]["operands"].pop("risk_stage")
    candidates, objects, assertions, evidence = parse_manifest(
        missing_stage_doc, "STOIC-RISK")
    result = score_episode(next(iter(candidates.values())), objects, assertions, evidence)
    assert result["verdict"] == "unknown"
    assert not any("risk stage does not match" in hole["reason"] for hole in result["holes"])


def test_m12_missing_baseline_is_unknown_but_nonpositive_baseline_fails():
    from trading_research.research.method_pack.evidence import parse_manifest, score_episode

    def score(op, fid):
        document = m12._document(fid, op)
        candidates, objects, assertions, evidence = parse_manifest(document, "STOIC-RISK")
        return score_episode(next(iter(candidates.values())), objects, assertions, evidence)

    missing = m12._base("first")
    missing["equity_baseline"] = {}
    assert score(missing, "missing-baseline")["verdict"] == "unknown"

    nonpositive = m12._base("first", b="-100")
    result = score(nonpositive, "negative-baseline")
    assert result["verdict"] == "fail"
    assert any("must both be positive" in hole["reason"] for hole in result["holes"])


def test_m12_method_c08_mutates_late_missing_and_identity_records():
    rows = _rows()
    late = rows["M12-F1:late"]["actual_value"]
    assert late["verdict"] == "fail" and late["detected_causal_violations"] >= 1
    assert rows["M12-F1:missing"]["actual_value"]["verdict"] == "unknown"
    identity = rows["M12-F1:identity"]["actual_value"]
    assert identity["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in identity["holes"])


def test_all_m12_objects_have_passing_numeric_and_c08_fixtures():
    from trading_research.research.method_pack.objects import FIXTURES, RECIPES, run_object_fixtures

    ids = objects_for("STOIC-RISK")
    assert set(ids) <= set(RECIPES)
    assert set(ids) <= {fixture["recipe"] for fixture in FIXTURES}
    rows = run_object_fixtures(ids)
    assert all(row["status"] == "pass" for row in rows)
    for oid in ids:
        kinds = {row["kind"] for row in rows if row["recipe"] == oid}
        assert {"c08_missing", "c08_late", "c08_identity"} <= kinds


def test_m12_owned_recipes_enforce_gate_and_fixed_geometry():
    from trading_research.research.method_pack.objects import RECIPES

    gate = RECIPES["O154"]({
        "n": 100, "win_rate": "0.55", "avg_rr": "2", "mc_max_streak": 8,
        "same_process": True, "known_at": m12._t(16, 0, day=m12.YDAY),
        "use_at": m12._t(9, 30),
    })
    assert gate.value["overlay_validation"] is True
    assert gate.value["simulation_run"] is False
    n99 = RECIPES["O154"]({
        "n": 99, "win_rate": "0.55", "avg_rr": "2", "mc_max_streak": 8,
        "known_at": m12._t(16, 0, day=m12.YDAY), "use_at": m12._t(9, 30),
    })
    assert n99.value["overlay_validation"] is False
    missing_mc = RECIPES["O154"]({
        "n": 100, "win_rate": "0.55", "avg_rr": "2",
        "known_at": m12._t(16, 0, day=m12.YDAY), "use_at": m12._t(9, 30),
    })
    assert missing_mc.state == "hole" and missing_mc.value.get("overlay_validation") is None
    ladder = RECIPES["O155"]({"E0": 10000, "B": 100})
    assert ladder.value["base_risk_fraction"] == Decimal("0.01")
    assert ladder.value["net_second_loss"] == Decimal("-100")
    assert ladder.value["net_second_win"] == Decimal("1500")
    assert ladder.value["entry_created"] is False
    over = RECIPES["O155"]({"E0": 10000, "B": 101})
    assert over.state == "invalid" and over.base_ok is False


def test_m12_semantic_audit():
    assert m12.semantic_audit() == {
        "fixture_count": 15, "all_pass": True, "positive_cases": 3,
        "negative_cases": 5, "hole_cases": 4, "c08_cases": 3,
    }
