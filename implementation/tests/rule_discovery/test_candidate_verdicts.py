"""Candidate confirmation verdicts. Fail if the family rule is not evaluated at contact."""
from __future__ import annotations

from decimal import Decimal

from trading_research.research.rule_discovery.source_adapters.common import (
    PRIMARY_BRANCH,
    dual_scan,
    evaluate_family_rule_at_contact,
    install_write_guard,
    load_source_market,
)
from trading_research.research.rule_discovery.source_adapters.confirmation import (
    evaluate_confirmation,
    finish_values,
    trigger_contact,
)
from trading_research.research.rule_discovery.source_adapters.processes import confirm_at_contact as refill_confirm

SLICE = [
    "2020-01-02",
    "2021-01-04",
    "2022-01-03",
    "2023-01-03",
    "2023-11-06",
    "2024-01-02",
    "2025-01-02",
    "2026-01-02",
    "2026-09-03",
]
# Independent verification counted 8 B0.1 primary-family episodes on 2023-01-03.
# The 9-date PRIMARY_BRANCH dual_scan total matches the B0.1 column of VERDICTS.json.
SLICE_B01_PRIMARY_EPISODES = 58
SLICE_B01_2023_01_03 = 8
MINUTE_NS = 60_000_000_000


def test_stamped_false_confirmation_is_no_setup():
    contact = {"complete": True, "source_confirmation": False, "contact_id": "x", "side": "long"}
    assert evaluate_family_rule_at_contact(contact) == "no_setup"


def test_empty_delta_matches_b01_verdicts_contact_for_contact():
    install_write_guard()
    markets = {}
    mismatches = []
    compared = 0
    compared_2023 = 0
    for day in SLICE:
        markets[day] = load_source_market(day)
        for _task, (family, branch) in PRIMARY_BRANCH.items():
            document = dual_scan(markets[day], family, branch)
            for episode in document["b01"].get("episodes") or []:
                decision = evaluate_confirmation(
                    markets[day],
                    family=family,
                    branch=branch,
                    contact=trigger_contact(episode),
                    reference=episode.get("reference") or {},
                    changed_axis="none",
                )
                compared += 1
                if day == "2023-01-03":
                    compared_2023 += 1
                if decision.research_verdict != episode.get("research_verdict"):
                    mismatches.append(
                        {
                            "date": day,
                            "family": family,
                            "branch": branch,
                            "b01": episode.get("research_verdict"),
                            "got": decision.research_verdict,
                        }
                    )
    assert compared_2023 >= SLICE_B01_2023_01_03, compared_2023
    assert compared == SLICE_B01_PRIMARY_EPISODES, compared
    assert mismatches == [], mismatches


def test_candidate_unknown_share_at_most_b01():
    from pathlib import Path
    import importlib.util
    import json

    script = Path(__file__).resolve().parents[2] / "reports/research-work/P15-17/_track_r1/produce_verdicts.py"
    out = script.with_name("VERDICTS.json")
    if not out.is_file():
        spec = importlib.util.spec_from_file_location("produce_track_r1_verdicts", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.main() == 0
    payload = json.loads(out.read_text())
    assert payload["families"]
    jj = payload["families"]["JJ-TBR"]
    assert jj["f1"]["episodes"] == 84
    assert jj["r"]["episodes"] == 156
    assert jj["b01"]["episodes"] == 10
    assert jj["f1"]["unknown"] == 0
    assert jj["r"]["unknown"] == 0
    for family, row in payload["families"].items():
        if (row["b01"].get("episodes") or 0) == 0:
            literal = _refill_literal_unknown_share()
            assert literal <= 1e-12, literal
            assert row["candidate_unknown_share"] <= literal + 1e-12, (family, row, literal)
            continue
        assert row["candidate_unknown_share"] <= row["b01_unknown_share"] + 1e-12, (family, row)


def test_jumbo_literal_pass_and_fail():
    """M01-F1 pass and M01-F2 fail on a synthetic confirmation bind."""
    contact = {"contact_id": "m01", "side": "short", "complete": True, "start": 1, "L": Decimal("121"), "H": Decimal("122")}
    passed = finish_values(
        family="JJ-TBR",
        branch="judas_reversal",
        contact=contact,
        values={
            "branch": "judas_reversal",
            "side": "short",
            "range_frozen": True,
            "range_known_at": 1,
            "context_fixed": True,
            "context_at": 1,
            "location_touched": True,
            "touch_at": 2,
            "source_confirmation": True,
            "confirm_at": 3,
            "risk_defined": True,
            "objective_fixed": True,
            "decision_at": 4,
            "reversal_context": True,
            "edge_swept": True,
            "sweep_at": 2,
            "source_time_window": True,
            "objective_is_opposing_draw": True,
        },
        confirm_at=3,
        decision_at=4,
        cutoff_ns=4,
    )
    failed = finish_values(
        family="JJ-TBR",
        branch="judas_reversal",
        contact=contact,
        values={
            "branch": "judas_reversal",
            "side": "short",
            "range_frozen": True,
            "range_known_at": 1,
            "context_fixed": True,
            "context_at": 1,
            "location_touched": True,
            "touch_at": 2,
            "source_confirmation": False,
            "confirm_at": 3,
            "risk_defined": False,
            "objective_fixed": True,
            "decision_at": 4,
            "reversal_context": True,
            "edge_swept": True,
            "sweep_at": 2,
            "source_time_window": True,
            "objective_is_opposing_draw": True,
        },
        confirm_at=3,
        decision_at=4,
        cutoff_ns=4,
    )
    assert passed.research_verdict == "pass", passed.failed
    assert failed.research_verdict == "fail"
    assert "source_confirmation" in failed.failed


def test_gb_fail_literal_pass_and_fail():
    contact = {"contact_id": "m02", "side": "short", "complete": True, "start": 1, "L": Decimal("100"), "H": Decimal("111")}
    passed = finish_values(
        family="GB-FAIL",
        branch="nyam_box",
        contact=contact,
        values={
            "branch": "nyam_box",
            "side": "short",
            "reference_frozen": True,
            "reference_known_at": 1,
            "reference_px": Decimal("110"),
            "bias_recorded": True,
            "context_at": 1,
            "source_session_allowed": True,
            "sweep_at": 2,
            "sweep_high": Decimal("111"),
            "sweep_low": Decimal("100"),
            "confirmation_mode": "five_minute_close",
            "complete_clock_five_minute_bar": True,
            "confirm_at": 3,
            "confirm_close": Decimal("109"),
            "box_return_ok": True,
            "tdo_required": False,
            "pocket_required": False,
            "retracement_entry": False,
            "risk_defined": True,
            "objective_fixed": True,
            "decision_at": 4,
        },
        confirm_at=3,
        decision_at=4,
        cutoff_ns=4,
    )
    failed = finish_values(
        family="GB-FAIL",
        branch="nyam_box",
        contact=contact,
        values={
            "branch": "nyam_box",
            "side": "short",
            "reference_frozen": True,
            "reference_known_at": 1,
            "reference_px": Decimal("110"),
            "bias_recorded": True,
            "context_at": 1,
            "source_session_allowed": True,
            "sweep_at": 2,
            "sweep_high": Decimal("111"),
            "sweep_low": Decimal("100"),
            "confirmation_mode": "five_minute_close",
            "complete_clock_five_minute_bar": True,
            "confirm_at": 3,
            "confirm_close": Decimal("111"),
            "box_return_ok": False,
            "tdo_required": False,
            "pocket_required": False,
            "retracement_entry": False,
            "risk_defined": True,
            "objective_fixed": True,
            "decision_at": 4,
        },
        confirm_at=3,
        decision_at=4,
        cutoff_ns=4,
    )
    assert passed.research_verdict == "pass", (passed.failed, passed.unknown)
    assert failed.research_verdict == "fail"


def test_removed_confirmation_would_leave_unknown():
    contact = {"complete": True, "contact_id": "bare", "side": "long"}
    assert evaluate_family_rule_at_contact(contact) == "unknown"


class _RefillMarket:
    instrument_id = "NQ"
    start = 0
    end = 4 * MINUTE_NS

    def __init__(self, rows):
        self._rows = rows

    def bars(self, lo, hi, seconds=60):
        return [row for row in self._rows if row["start"] >= lo and row["end"] <= hi]

    def coverage(self, lo, hi):
        return {"observed_scope_complete": True}


def _refill_rows(*, departed: bool):
    outside = {"start": 0, "end": MINUTE_NS, "L": Decimal("103"), "H": Decimal("104"), "C": Decimal("103.5"), "known_at": MINUTE_NS, "complete": True, "observed_complete": True}
    inside_early = {"start": 0, "end": MINUTE_NS, "L": Decimal("100"), "H": Decimal("101"), "C": Decimal("100.5"), "known_at": MINUTE_NS, "complete": True, "observed_complete": True}
    touch = {"start": 2 * MINUTE_NS, "end": 3 * MINUTE_NS, "L": Decimal("100"), "H": Decimal("101"), "C": Decimal("100.5"), "known_at": 3 * MINUTE_NS, "complete": True, "observed_complete": True}
    mid = {"start": MINUTE_NS, "end": 2 * MINUTE_NS, "L": Decimal("100.25"), "H": Decimal("100.75"), "C": Decimal("100.5"), "known_at": 2 * MINUTE_NS, "complete": True, "observed_complete": True}
    first = outside if departed else inside_early
    return [first, mid, touch]


def _refill_decision(*, departed: bool):
    market = _RefillMarket(_refill_rows(departed=departed))
    contact = {
        "contact_id": "refill-touch",
        "side": "long",
        "complete": True,
        "at_ns": 2 * MINUTE_NS,
        "available_at_ns": 3 * MINUTE_NS,
        "low": "100",
        "high": "101",
    }
    formation = {"available_at_ns": 0, "start_ns": 0, "end_ns": 0, "low": "100", "high": "101"}
    reference = {"issue_at_ns": 0, "lower": "100", "upper": "101", "reference_id": "refill-ref"}
    return evaluate_confirmation(
        market,
        family="REFILL-STUDY",
        branch="touch_record",
        contact=contact,
        reference=reference,
        formation=formation,
        changed_axis="Formation",
    )


def _refill_literal_unknown_share() -> float:
    verdicts = [_refill_decision(departed=True).research_verdict, _refill_decision(departed=False).research_verdict]
    unknown = sum(1 for item in verdicts if item == "unknown")
    return unknown / len(verdicts)


def test_refill_literal_pass_and_fail():
    passed = _refill_decision(departed=True)
    failed = _refill_decision(departed=False)
    assert passed.research_verdict == "pass", (passed.failed, passed.unknown, passed.values)
    assert failed.research_verdict == "fail", (failed.failed, failed.unknown, failed.values)
    assert passed.values.get("zone_known_at") == 0
    assert passed.values.get("departure_at") == MINUTE_NS
    assert passed.values.get("feature_max_known_at") == 0
    assert _refill_literal_unknown_share() == 0.0
    bound = refill_confirm(
        _RefillMarket(_refill_rows(departed=True)),
        branch="touch_record",
        contact={"contact_id": "x", "side": "long", "complete": True, "at_ns": 2 * MINUTE_NS, "available_at_ns": 3 * MINUTE_NS},
        reference={"issue_at_ns": 0, "lower": "100", "upper": "101"},
        formation={"available_at_ns": 0, "low": "100", "high": "101"},
    )
    assert bound["values"]["zone_known_at"] == 0
    assert bound["values"]["departure_at"] == MINUTE_NS
    assert bound["values"]["feature_max_known_at"] == 0
