"""GB-FAIL's bound synthetic method cases.

Each row is converted through ``fixture_document`` and scored through the
same C01 parser used by a supplied episode manifest.  The values below are
the published M02 operands; they are not a second implementation of the
SQL predicate.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.fixture_utils import method_case


DAY = date(2026, 1, 15)


def _t(hour: int, minute: int) -> int:
    return et_ns(DAY, hour, minute)


# The binder uses these caps to check that each bound operand was available at
# the stage where GB-FAIL consumes it.  Event-key operands keep their own
# timestamp; Boolean/price records inherit the mapped stage in fixture mode.
STAGE_LIMITS = {
    "reference_frozen": "reference_known_at",
    "reference_px": "reference_known_at",
    "bias_recorded": "context_at",
    "source_session_allowed": "sweep_at",
    "sweep_high": "sweep_at",
    "sweep_low": "sweep_at",
    "confirmation_mode": "sweep_at",
    "complete_clock_five_minute_bar": "confirm_at",
    "confirm_close": "confirm_at",
    "source_hold_confirmed": "confirm_at",
    "box_return_ok": "confirm_at",
    "tdo_required": "sweep_at",
    "source_tdo_close_confirmed": "confirm_at",
    "pocket_required": "sweep_at",
    "touch_in_measured_pocket": "touch_at",
    "retracement_entry": "confirm_at",
    "risk_defined": "decision_at",
    "objective_fixed": "decision_at",
}


def _positive_case() -> dict:
    """The declared NYAM high-failure example from M02-F1."""

    return {
        "branch": "nyam_box",
        "side": "short",
        "instrument_id": "NQ-test",
        "band_id": "nyam-box-2026-01-15",
        "reference_frozen": True,
        "reference_known_at": _t(10, 0),
        "reference_px": 110,
        "bias_recorded": True,
        "context_at": _t(9, 55),
        "source_session_allowed": True,
        "sweep_at": _t(10, 1),
        "sweep_high": 111,
        "sweep_low": None,
        "confirmation_mode": "five_minute_close",
        "complete_clock_five_minute_bar": True,
        "confirm_at": _t(10, 5),
        "confirm_close": 109,
        "source_hold_confirmed": None,
        "box_return_ok": True,
        "tdo_required": False,
        "source_tdo_close_confirmed": None,
        "pocket_required": False,
        "impulse_known_at": None,
        "touch_at": None,
        "touch_in_measured_pocket": None,
        "retracement_entry": False,
        "retest_at": None,
        "risk_defined": True,
        "objective_fixed": True,
        "decision_at": _t(10, 6),
        # Retained source ticket values are descriptive operands for the
        # fixture; the entry predicate consumes the two Boolean gates above.
        "stop_px": 112,
        "objective_px": 100,
    }


def _manifest_mutation_cases() -> list[dict]:
    """Exercise C08 against records in a complete episode manifest.

    The ordinary method rows are compact fixture operands.  These rows keep
    the same manifest shape after mutating a producer record, so identity,
    late availability, and missing-binding findings come from the C01
    binder itself rather than from a private fixture switch.
    """

    from trading_research.research.method_pack.fixture_utils import fixture_document

    source = fixture_document("GB-FAIL", "sequence", "M02-F1", _positive_case())

    def case(suffix: str, mutate, expected: str, kind: str) -> dict:
        document = deepcopy(source)
        fid = f"M02-F1:{suffix}"
        candidate = document["candidates"][0]
        candidate["candidate_id"] = fid
        # Assertions carry candidate identity as part of the record.  Keep
        # that identity aligned so each mutation isolates its intended C08
        # finding instead of creating unrelated assertion mismatches.
        for assertion in document["assertions"]:
            assertion["candidate_id"] = fid
        mutate(document, fid)
        return method_case("GB-FAIL", "sequence", fid, document, expected, kind=kind)

    def late_reference(document: dict, _fid: str) -> None:
        late_at = _positive_case()["decision_at"] + 1
        obj = next(o for o in document["objects"]
                   if o["object_id"].endswith(":reference_known_at"))
        obj.update({"known_at": late_at, "as_of": late_at,
                    "formation_start": late_at, "formation_end": late_at})
        for evidence in document["evidence"]:
            if evidence["evidence_id"] in obj["evidence_ids"]:
                evidence.update({"known_at": late_at,
                                 "observation_start": late_at,
                                 "observation_end": late_at})

    def foreign_reference(document: dict, _fid: str) -> None:
        obj = next(o for o in document["objects"]
                   if o["object_id"].endswith(":reference_px"))
        obj["band_id"] = "foreign-band"

    def missing_session_binding(document: dict, _fid: str) -> None:
        document["candidates"][0]["operands"].pop("source_session_allowed")

    return [
        case("c08-late", late_reference, "fail", "c08_late"),
        case("c08-identity", foreign_reference, "fail", "c08_identity"),
        case("c08-missing", missing_session_binding, "unknown", "c08_missing"),
    ]


def method_fixtures() -> list[dict]:
    """Return M02-F1/F2/F3 rows with explicit branch operands."""

    positive = _positive_case()
    rows = [method_case("GB-FAIL", "sequence", "M02-F1", positive, "pass")]
    rows.extend(_manifest_mutation_cases())

    # A 09:45 attempt cannot use the final 09:00--10:00 box.  The reference
    # remains identified, but its actual availability is after the sweep.
    early = deepcopy(positive)
    early.update({
        "reference_frozen": False,
        "reference_known_at": _t(10, 0),
        "sweep_at": _t(9, 45),
        "confirm_at": _t(9, 50),
        "decision_at": _t(9, 51),
    })
    rows.append(method_case("GB-FAIL", "sequence", "M02-F2-box-unavailable", early, "fail", kind="negative"))

    # A close equal to the sweep remains outside the frozen high; strict
    # close-below-reference and the explicit box return both reject it.
    outside = deepcopy(positive)
    outside.update({"confirm_close": 111, "box_return_ok": False})
    rows.append(method_case("GB-FAIL", "sequence", "M02-F2-close-outside", outside, "fail", kind="negative"))

    # A measured-pocket touch is only location/confluence.  It cannot replace
    # the actual failure/reclaim confirmation.
    pocket = deepcopy(positive)
    pocket.update({
        "pocket_required": True,
        "impulse_known_at": _t(9, 50),
        "touch_at": _t(10, 3),
        "touch_in_measured_pocket": True,
        "confirm_close": 111,
        "box_return_ok": False,
    })
    rows.append(method_case("GB-FAIL", "sequence", "M02-F2-pocket-no-fail", pocket, "fail", kind="negative"))

    # Five observed rows with a missing 10:02 clock interval are not a
    # complete aligned [10:00,10:05) confirmation bar.
    grouped = deepcopy(positive)
    grouped["complete_clock_five_minute_bar"] = False
    rows.append(method_case("GB-FAIL", "sequence", "M02-F2-grouped-rows", grouped, "fail", kind="negative"))

    # Hold duration/detector is source supplied and remains unknown when the
    # selected mode has no completed hold observation.
    hold = deepcopy(positive)
    hold.update({
        "confirmation_mode": "reclaim_and_hold",
        "complete_clock_five_minute_bar": None,
        "source_hold_confirmed": None,
    })
    rows.append(method_case("GB-FAIL", "sequence", "M02-F3-hold", hold, "unknown", kind="hole"))

    # Exact London/session boundaries are unpublished.  Preserve the branch
    # and source-session operand as an explicit hole rather than borrowing a
    # clock from another method.
    session_hole = deepcopy(positive)
    session_hole.update({
        "branch": "previous_hour",
        "band_id": "previous-hour-2026-01-15",
        "source_session_allowed": None,
    })
    rows.append(method_case("GB-FAIL", "sequence", "M02-F3-london-clock", session_hole, "unknown", kind="hole"))

    # Prior-period scope and the general stop policy are separately named
    # source holes.  They are intentionally not promoted to universal gates.
    period_hole = deepcopy(positive)
    period_hole.update({
        "branch": "prior_week_level",
        "band_id": "prior-week-level-2026-01-15",
        "reference_frozen": None,
        "reference_known_at": None,
        "reference_px": None,
    })
    rows.append(method_case("GB-FAIL", "sequence", "M02-F3-prior-period-scope", period_hole, "unknown", kind="hole"))

    stop_hole = deepcopy(positive)
    stop_hole["risk_defined"] = None
    rows.append(method_case("GB-FAIL", "sequence", "M02-F3-stop-policy", stop_hole, "unknown", kind="hole"))

    return rows


__all__ = ["STAGE_LIMITS", "method_fixtures"]
