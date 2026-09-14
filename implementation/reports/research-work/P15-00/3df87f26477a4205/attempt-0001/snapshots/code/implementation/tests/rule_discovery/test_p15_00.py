"""P15-00 baseline binding and typed-record checks."""

from __future__ import annotations

from decimal import Decimal
from math import nan

import pytest

from trading_research.errors import ContractError
from trading_research.research.contracts.identity import canonical_bytes, digest
from trading_research.research.contracts.types import (
    Bar,
    Contact,
    Coverage,
    CoverageReceipt,
    EvidenceRef,
    FeatureValue,
    Forecast,
    Formation,
    NativeBatch,
    NativeTrade,
    Opportunity,
    PredicateEvidence,
    QuoteBatch,
    Reference,
    RuleSpec,
    SequenceState,
    Snapshot,
    parse_forecast,
    parse_native_trade,
    parse_reference,
    record_from_json,
    source_exact_from_baseline,
)
from trading_research.research.rule_discovery.baseline_manifest import (
    bind_baseline,
    bind_units,
    select_engineering_dates,
    write_p15_00_artifacts,
    write_p15_00_receipt,
)


def _evidence(available: int = 10, event_end: int | None = None) -> EvidenceRef:
    end = available if event_end is None else event_end
    return EvidenceRef(
        artifact_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        row_ids=("r1",),
        event_start_ns=0,
        event_end_ns=end,
        available_at_ns=available,
        coverage=Coverage.COMPLETE,
        limitation_ids=(),
    )


def _opportunity(**overrides):
    values = dict(
        opportunity_id="a" * 64,
        parent_opportunity_id=None,
        overlap_group_id="b" * 64,
        rule_id="JJ-TBR:branch:judas_outbound",
        family="JJ-TBR",
        branch="judas_outbound",
        account_day="2020-01-02",
        side=1,
        issue_at_ns=1,
        decision_at_ns=2,
        reference_asset="NQ:x",
        response_asset="NQ:x",
        execution_asset="NQ:x",
        reference_id="ref",
        lower=Decimal("1.00"),
        upper=Decimal("2.00"),
        entry_reference=Decimal("1.00"),
        invalidation=None,
        objective=None,
        expiry_at_ns=3,
        stages=(_evidence(2),),
        coverage=Coverage.COMPLETE,
        source_exact=False,
        hypothesis_ids=("H1",),
    )
    values.update(overrides)
    return Opportunity(**values)


def test_a01_units_and_census_are_the_accepted_registry():
    bound = bind_baseline()
    units = bound["binding"]["units"]
    census = bound["binding"]["census"]
    assert units["branch_count"] == 50
    assert units["extra_unit_count"] == 8
    assert units["unit_count"] == 58
    assert census["totals"]["setups"] == 18747
    assert census["totals"]["daily_jobs"] == 99294
    assert census["totals"]["sessions"] == 1742
    assert census["setups_are_branch_opportunities"] is True
    assert census["setups_are_independent_trades"] is False
    assert census["totals"]["native_executions"] == 591714592
    assert census["totals"]["setups"] != census["totals"]["native_executions"]
    assert bound["binding"]["wiki_not_used_for_identity"] is True
    assert units["scope_counts"]["entry_setup"] == 37
    assert units["scope_counts"]["context_or_research"] == 10
    assert units["scope_counts"]["personal_execution_out_of_scope"] == 7
    assert units["scope_counts"]["supplemental_observation"] == 4


def test_a02_canonical_hashes_ignore_key_order_and_worker_count():
    first = {"family": "JJ-TBR", "price": Decimal("1.00"), "clock": 10}
    second = {"clock": 10, "price": Decimal("1.00"), "family": "JJ-TBR"}
    assert digest(first) == digest(second)
    changed_clock = {"family": "JJ-TBR", "price": Decimal("1.00"), "clock": 11}
    changed_price = {"family": "JJ-TBR", "price": Decimal("1.01"), "clock": 10}
    assert digest(changed_clock) != digest(first)
    assert digest(changed_price) != digest(first)
    with_workers = {"family": "JJ-TBR", "price": Decimal("1.00"), "clock": 10, "worker_count": 4}
    assert digest(first) != digest(with_workers)
    semantic = {key: value for key, value in with_workers.items() if key != "worker_count"}
    assert digest(semantic) == digest(first)
    assert canonical_bytes({"b": 1, "a": 2}) == canonical_bytes({"a": 2, "b": 1})


def test_a03_future_invalid_side_geometry_and_nan_fail():
    with pytest.raises(ContractError, match="future evidence"):
        _evidence(available=5, event_end=9)
    with pytest.raises(ContractError, match=r"\+1 or -1"):
        _opportunity(side=0)
    with pytest.raises(ContractError, match="invalid geometry"):
        _opportunity(lower=Decimal("3.00"), upper=Decimal("2.00"))
    with pytest.raises(ContractError, match="finite float"):
        FeatureValue(
            name="x",
            value=nan,
            unit="points",
            available_at_ns=1,
            evidence=(),
            missing_reason=None,
        )


def test_a04_author_exact_unknown_stays_unknown():
    payload = {"author_exact_verdict": "unknown", "faithful_eligible": False, "geometry": "matched"}
    assert source_exact_from_baseline(payload) is False
    opp = _opportunity(source_exact=source_exact_from_baseline(payload))
    round_trip = digest({"payload": payload, "source_exact": opp.source_exact})
    again = digest({"source_exact": False, "payload": {"geometry": "matched", "faithful_eligible": False, "author_exact_verdict": "unknown"}})
    assert round_trip == again
    assert opp.source_exact is False


def test_a05_eight_date_selection_preserves_missing_year_slots():
    rows = [
        {"date": "2020-01-02", "status": "complete", "calendar_state": "regular", "reason": "regular"},
        {"date": "2021-01-04", "status": "complete", "calendar_state": "regular", "reason": "regular"},
        {"date": "2023-11-06", "status": "complete", "calendar_state": "regular", "reason": "regular"},
        {"date": "2023-11-03", "status": "complete", "calendar_state": "regular", "reason": "regular"},
        {"date": "2024-01-02", "status": "complete", "calendar_state": "regular", "reason": "regular"},
        {"date": "2025-01-02", "status": "complete", "calendar_state": "regular", "reason": "regular"},
        {"date": "2026-01-02", "status": "complete", "calendar_state": "regular", "reason": "regular"},
        {"date": "2026-09-03", "status": "partial", "calendar_state": "regular", "reason": "partial"},
    ]
    selected = select_engineering_dates(rows)
    by_year = {slot["year"]: slot for slot in selected["year_slots"]}
    assert by_year[2020]["date"] == "2020-01-02"
    assert by_year[2022]["status"] == "missing"
    assert by_year[2022]["date"] is None
    assert selected["dst_slot"]["date"] == "2023-11-06"
    assert selected["year_slots"][0]["date"] == min(row["date"] for row in rows if row["status"] == "complete" and row["date"].startswith("2020"))
    bound = bind_baseline()
    native = bound["dates"]
    assert len(native["year_slots"]) == 7
    assert native["dst_slot"]["anchor"] == "2023-11-05"
    assert native["classified_dates"][0]["date"] == bound["binding"]["study_start"]
    statuses = {row["date"]: row["status"] for row in native["classified_dates"]}
    assert statuses[bound["binding"]["study_end"]] == "partial"
    prior = next(row for row in native["input_groups"][1]["coverage_rows"] if row["date"] == "2020-01-02")
    assert prior["status"] != "complete"
    assert "same_contract_prior_scope_unknown" in prior["omission_reasons"]
    assert native["native_replay"]["kind"] == "native"
    assert native["fixtures"]["feed_gap"]["unknown_preserved"] is True
    assert native["fixtures"]["same_timestamp_conflict"]["ambiguity_preserved"] is True


def test_a06_receipt_records_commands_hashes_and_bootstrap_predecessors(tmp_path):
    written = write_p15_00_artifacts(tmp_path)
    receipt = write_p15_00_receipt(
        tmp_path,
        run_id=written["run_id"],
        plan_sha256=written["plan_sha256"],
        code_sha256=written["code_sha256"],
        command_results=[{"argv": ["pytest"], "cwd": "/workspace/implementation", "exit_code": 0, "seconds": 0.1, "log": None}],
        acceptance_checks={f"A{index:02d}": True for index in range(1, 14)},
        coverage={"native": False, "unknown": 0},
        unresolved=["P15-01 verifier is pending"],
        reason="bootstrap serializer and baseline identities",
    )
    assert receipt["predecessor_receipts"] == {}
    assert receipt["schema_version"] == "research-task-receipt-v2"
    assert (tmp_path / "TASK_RECEIPT.json").is_file()
    assert (tmp_path / "BASELINE_BINDING.json").is_file()
    assert all(receipt["acceptance_checks"].values())


def test_frozen_parameters_do_not_alias_caller_dict():
    params = {"bandwidth": 2, "reset": "R1"}
    spec = RuleSpec(
        rule_id="vwap-r1",
        family="SIRES",
        source_branch="vwap_deviation_fade",
        version="1",
        provenance="custom",
        baseline_rule_id="SIRES:branch:vwap_deviation_fade",
        changed_axis="reference",
        parameters=params,
        required_inputs=("vwap",),
        required_stages=("issued",),
        formation_policy="R1",
        expiry_policy="source",
    )
    params["bandwidth"] = 99
    assert spec.parameters["bandwidth"] == 2
    with pytest.raises(TypeError):
        spec.parameters["reset"] = "B0"


def test_decimal_one_keeps_documented_scale():
    assert digest({"price": Decimal("1.00")}) != digest({"price": Decimal("1.0")})
    assert digest({"price": Decimal("1.00")}) != digest({"price": 1.0})


def test_native_chronological_slice_rejects_reversed_availability():
    evidence = _evidence(20)
    early = NativeTrade(
        event_id="e1",
        asset_id="NQ:x",
        event_ns=10,
        available_at_ns=10,
        price=Decimal("100.00"),
        quantity=1,
        aggressor=1,
        evidence=_evidence(10),
    )
    late = NativeTrade(
        event_id="e2",
        asset_id="NQ:x",
        event_ns=20,
        available_at_ns=20,
        price=Decimal("101.00"),
        quantity=1,
        aggressor=-1,
        evidence=evidence,
    )
    first = NativeBatch("b1", 10, 10, (early,), True)
    second = NativeBatch("b2", 20, 20, (late,), True)
    assert first.event_ns < second.event_ns
    with pytest.raises(ContractError, match="future evidence"):
        NativeTrade(
            event_id="future",
            asset_id="NQ:x",
            event_ns=20,
            available_at_ns=10,
            price=Decimal("101.00"),
            quantity=1,
            aggressor=1,
            evidence=_evidence(10),
        )


def test_bind_units_uses_coverage_not_wiki(monkeypatch):
    bound = bind_baseline()
    coverage_ids = [unit["coverage_id"] for unit in bound["binding"]["units"]["units"]]
    assert "JJ-TBR:branch:judas_outbound" in coverage_ids
    assert "STOIC-DATA:unit:macro_application" in coverage_ids
    assert len(coverage_ids) == len(set(coverage_ids))
    rebound = bind_units(bound["inputs"]["coverage"])
    assert rebound["unit_count"] == 58


def _late() -> EvidenceRef:
    return EvidenceRef(
        artifact_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        row_ids=("future-row",),
        event_start_ns=100,
        event_end_ns=100,
        available_at_ns=100,
        coverage=Coverage.COMPLETE,
        limitation_ids=(),
    )


def _early() -> EvidenceRef:
    return _evidence(5)


def test_a09_nested_clocks_and_deserializers_reject_late_and_malformed():
    late = _late()
    early = _early()
    with pytest.raises(ContractError, match="future evidence"):
        NativeTrade("t", "NQ:test", 10, 10, Decimal("100"), 1, 1, late)
    NativeTrade("t", "NQ:test", 5, 10, Decimal("100"), 1, 1, early)
    with pytest.raises(ContractError, match="future evidence"):
        Reference("r", "l", "f", "NQ:test", Decimal("99"), Decimal("101"), 10, 200, (1,), (late,))
    Reference("r", "l", "f", "NQ:test", Decimal("99"), Decimal("101"), 10, 200, (1,), (early,))
    with pytest.raises(ContractError, match="future evidence"):
        Forecast("f", "e", "a" * 64, "s", 10, "h", 20, {"variance": 1.0}, "supported", 100, 5, (), ())
    Forecast("f", "e", "a" * 64, "s", 10, "h", 20, {"variance": 1.0}, "supported", 4, 5, (), ())
    with pytest.raises(ContractError, match="future evidence"):
        QuoteBatch("q", "NQ:test", 10, 10, Decimal("1"), Decimal("2"), 1, 1, False, (late,))
    with pytest.raises(ContractError, match="future evidence"):
        Bar("b", "NQ:test", 0, 10, 10, Decimal("1"), Decimal("2"), Decimal("1"), Decimal("1"), 1, 0, 0, Coverage.COMPLETE, (late,))
    with pytest.raises(ContractError, match="future evidence"):
        Formation("f1", "NQ:test", 0, 10, 10, Decimal("2"), Decimal("1"), 1, None, "range", (), (late,))
    with pytest.raises(ContractError, match="future evidence"):
        Contact("c", "r", "b", 10, 10, 1, "touch", (Decimal("1.00"),), (), (late,))
    with pytest.raises(ContractError, match="future evidence"):
        PredicateEvidence("p", True, 10, (late,), None)
    with pytest.raises(ContractError, match="future evidence"):
        SequenceState("s", "R1", "c", "open", 10, 10, 20, (PredicateEvidence("p", True, 100, (early,), None),), None, {})
    with pytest.raises(ContractError, match="future evidence"):
        Snapshot("snap", "2020-01-02", "NQ:test", 10, "schema", (FeatureValue("x", 1.0, "points", 100, (early,), None),), "a" * 64)
    with pytest.raises(ContractError, match="future evidence"):
        CoverageReceipt(0, 10, Coverage.COMPLETE, ((0, 10),), ((0, 10),), (), "a" * 64, (late,))
    with pytest.raises(ContractError, match="int UTC nanosecond"):
        EvidenceRef("a" * 64, ("r1",), True, 5, 5, Coverage.COMPLETE, ())
    with pytest.raises(ContractError, match="finite float"):
        FeatureValue("x", float("inf"), "points", 1, (), None)
    payload = {
        "event_id": "t",
        "asset_id": "NQ:test",
        "event_ns": 10,
        "available_at_ns": 10,
        "price": "100",
        "quantity": 1,
        "aggressor": 1,
        "evidence": {
            "artifact_sha256": "a" * 64,
            "row_ids": ["future-row"],
            "event_start_ns": 100,
            "event_end_ns": 100,
            "available_at_ns": 100,
            "coverage": "complete_observed_scope",
            "limitation_ids": [],
        },
    }
    with pytest.raises(ContractError, match="future evidence"):
        parse_native_trade(payload)
    with pytest.raises(ContractError, match="future evidence"):
        NativeTrade.from_mapping(payload)
    with pytest.raises(ContractError, match="future evidence"):
        record_from_json(NativeTrade, __import__("json").dumps(payload))
    valid = dict(payload)
    valid["evidence"] = {
        "artifact_sha256": "a" * 64,
        "row_ids": ["earlier-row"],
        "event_start_ns": 5,
        "event_end_ns": 5,
        "available_at_ns": 5,
        "coverage": "complete_observed_scope",
        "limitation_ids": [],
    }
    trade = parse_native_trade(valid)
    assert trade.price == Decimal("100")
    assert trade.available_at_ns >= trade.evidence.available_at_ns
    with pytest.raises(ContractError, match="future evidence"):
        parse_reference(
            {
                "reference_id": "r",
                "reference_lifecycle_id": "l",
                "formation_id": "f",
                "asset_id": "NQ:test",
                "lower": "99",
                "upper": "101",
                "issue_at_ns": 10,
                "expiry_at_ns": 200,
                "permitted_sides": [1],
                "evidence": [payload["evidence"]],
            }
        )
    with pytest.raises(ContractError, match="future evidence"):
        parse_forecast(
            {
                "forecast_id": "f",
                "expert_id": "e",
                "artifact_sha256": "a" * 64,
                "snapshot_id": "s",
                "issue_at_ns": 10,
                "horizon_id": "h",
                "target_end_ns": 20,
                "output": {"variance": 1.0},
                "support": "supported",
                "train_end_ns": 100,
                "fit_available_at_ns": 5,
                "input_feature_ids": [],
                "parent_forecast_ids": [],
            }
        )
    with pytest.raises(ContractError, match="must be an int"):
        parse_native_trade({**valid, "available_at_ns": "tomorrow"})
    with pytest.raises(ContractError, match="must be an int"):
        parse_native_trade({**valid, "event_ns": True})


def test_a09_immutable_records_do_not_alias_nested_state():
    memory = {"possible_prices": ["98.50", "102.00"]}
    state = SequenceState("s", "R1", "c", "open", 10, 10, 20, (), None, memory)
    memory["possible_prices"] = ["1"]
    assert state.working_memory["possible_prices"] == ("98.50", "102.00")
    with pytest.raises(TypeError):
        state.working_memory["x"] = 1
    output = {"variance": 1.0}
    forecast = Forecast("f", "e", "a" * 64, "s", 10, "h", 20, output, "supported", 4, 5, (), ())
    output["variance"] = 99.0
    assert forecast.output["variance"] == 1.0


def test_a10_a12_native_group_coverage_and_replay():
    bound = bind_baseline()
    dates = bound["dates"]
    assert dates["schema"] == "research-engineering-dates-v2"
    groups = {row["group_id"]: row for row in dates["input_groups"]}
    prior = next(row for row in groups["prior_same_contract_rth_profile"]["coverage_rows"] if row["date"] == "2020-01-02")
    current = next(row for row in groups["current_session_executions"]["coverage_rows"] if row["date"] == "2020-01-02")
    assert prior["status"] != "complete"
    assert "same_contract_prior_scope_unknown" in prior["omission_reasons"]
    assert prior["unknown_interval_count"] == 390
    assert current["current_complete"] is True
    replay = dates["native_replay"]
    assert replay["kind"] == "native"
    assert replay["row_id"].endswith("769284")
    trade = parse_native_trade(replay["serialized"])
    assert str(trade.price) == replay["price"]
    assert trade.event_ns == replay["event_ns"]
    again = bound["examples"]["native_replay"]
    assert again["source_sha256"] == replay["source_sha256"]
    assert dates["fixtures"]["feed_gap"]["kind"] == "synthetic_fixture"
    assert dates["fixtures"]["feed_gap"]["unknown_preserved"] is True
    assert dates["fixtures"]["same_timestamp_conflict"]["ambiguity_preserved"] is True
    assert dates["fixtures"]["feed_gap"].get("status") != "not_in_calendar_metadata"


def test_a11_a13_identities_recompute_and_supersede_without_overwrite(tmp_path):
    written = write_p15_00_artifacts(tmp_path)
    import json
    plan = json.loads((tmp_path / "PLAN_SNAPSHOT.json").read_text())
    code = json.loads((tmp_path / "CODE_SNAPSHOT.json").read_text())
    draft = json.loads((tmp_path / "DRAFT_MANIFEST.json").read_text())
    assert digest(plan["files"]) == written["plan_sha256"]
    assert digest(code) == written["code_sha256"]
    assert digest(draft)[:16] == written["run_id"]
    assert written["run_id"] != "b291864ccceaca9a"
    exposure = json.loads((tmp_path / "EXPOSURE_LEDGER.json").read_text())
    assert exposure["supersedes"]["sha256"] == "a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20"
    original = __import__("pathlib").Path(
        "/workspace/implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json"
    )
    assert original.is_file()
    from trading_research.research.contracts.identity import file_digest
    assert file_digest(original) == "a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20"
    zeros = "0" * 64
    assert written["plan_sha256"] != zeros
    assert written["code_sha256"] != zeros
