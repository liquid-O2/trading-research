"""GB-VWAP's bound synthetic method cases.

The rows below are converted to C01 episode manifests and scored through the
same binder used for acquired candidates.  The method owns the stage caps and
the small set of relationship checks that cannot be represented by a
nullable Boolean alone; the VWAP arithmetic itself remains O030.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.evidence import fixture_document
from trading_research.research.method_pack.fixture_utils import method_case


DAY = date(2026, 1, 15)


def _t(hour: int, minute: int = 0) -> int:
    return et_ns(DAY, hour, minute)


# A Boolean/price record is capped at the stage where the GB-VWAP sequence
# consumes it.  Event-key operands retain their own actual event timestamp.
STAGE_LIMITS = {
    "reference_frozen": "breakout_at",
    "london_high": "london_known_at",
    "asia_high": "asia_known_at",
    "continuation_context": "decision_at",
    "breakout_close": "breakout_at",
    "vwap_reset_verified": "vwap_known_at",
    "vwap_at_retest": "vwap_known_at",
    "retest_low": "retest_at",
    "retest_high": "retest_at",
    "risk_defined": "decision_at",
    "side": "decision_at",
}


def _positive_case() -> dict:
    """The declared supplied Asia/London breakout and VWAP retest."""

    return {
        "branch": "source_long",
        "side": "long",
        "instrument_id": "NQ-fixture",
        "band_id": "asia-london-vwap-2026-01-15",
        "reference_frozen": True,
        "london_high": "102",
        "london_known_at": _t(8),
        "london_session_id": "london-2026-01-15",
        "asia_high": "100",
        "asia_known_at": _t(8),
        "asia_session_id": "asia-2026-01-15",
        "continuation_context": True,
        "breakout_at": _t(9, 40),
        "breakout_close": "103",
        "breakout_bar_id": "breakout-bar-0940",
        "breakout_bar_complete": True,
        "vwap_reset_verified": True,
        "vwap_reset_id": "source-reset-2026-01-15",
        "vwap_basis": "trade_price",
        "canonical_tape_id": "NQ-source-tape",
        "vwap_known_at": _t(9, 44),
        "vwap_at_retest": "101.5",
        "retest_at": _t(9, 45),
        "retest_low": "101",
        "retest_high": "102",
        "retest_bar_id": "retest-bar-0945",
        "retest_bar_complete": True,
        "risk_defined": True,
        "decision_at": _t(9, 46),
        "stop_px": "99",
    }


def _payload_for(candidate: dict, field: str, assertions: dict, objects: dict,
                 evidence: dict) -> dict:
    """Return a bound field's first source payload, if one is present."""

    binding = candidate.get("operands", {}).get(field, {})
    record = assertions.get(binding.get("assertion_id"))
    if record is None:
        record = objects.get(binding.get("object_id"), {})
    producer = objects.get(record.get('object_id'), record if 'object_id' in binding else {})
    values = {**producer.get('inputs', {}), **producer.get('value', {})}
    for evidence_id in record.get("evidence_ids", []):
        row = evidence.get(evidence_id)
        if row is not None:
            return {**values, **row.get("payload", {})}
    return values


def audit_candidate(candidate, operands, objects, assertions, evidence) -> list[dict]:
    """Check source identities/evidence around the literal M03 predicate."""

    findings: list[dict] = []

    def issue(field: str, reason: str, *, kind: str = "identity",
              unknown: bool = False, recipe: str = "O046") -> None:
        findings.append({"field": field, "kind": kind, "unknown": unknown,
                         "reason": reason, "recipe_id": recipe})

    reference_payload = _payload_for(candidate, "london_high", assertions,
                                     objects, evidence)
    asia_payload = _payload_for(candidate, "asia_high", assertions, objects, evidence)
    london_id = reference_payload.get("london_session_id", reference_payload.get('source_session_id'))
    asia_id = asia_payload.get("asia_session_id", asia_payload.get('source_session_id'))
    if london_id is None or asia_id is None:
        issue('reference_frozen', 'Actual London and Asia source-session identities are required',
              unknown=True, kind='supplied_record_missing')
    elif london_id == asia_id:
        issue("reference_frozen",
              "London and Asia references reuse one source-session identity",
              recipe="O046")

    # A verified source VWAP must retain its reset, basis, and canonical tape
    # identity.  A comparison number alone cannot make the reset faithful.
    if operands.get("vwap_reset_verified") is True:
        payload = _payload_for(candidate, "vwap_reset_verified", assertions,
                               objects, evidence)
        required = {
            "vwap_reset_id": payload.get("vwap_reset_id", payload.get('reset_id')),
            "vwap_basis": payload.get("vwap_basis", payload.get('basis')),
            "canonical_tape_id": payload.get("canonical_tape_id"),
        }
        missing = [name for name, value in required.items() if value is None]
        if missing:
            issue("vwap_reset_verified",
                  "Verified VWAP is missing its source reset/basis/tape evidence: "
                  + ", ".join(missing), kind="supplied_record_missing",
                  unknown=True, recipe="O030")
        elif required["vwap_basis"] != "trade_price":
            issue("vwap_reset_verified",
                  "VWAP basis is not the source trade-price basis",
                  recipe="O030")

    for field, label in [('breakout_close', 'breakout'), ('retest_low', 'retest')]:
        payload = _payload_for(candidate, field, assertions, objects, evidence)
        complete = payload.get(f'{label}_bar_complete')
        if complete is None:
            issue(field, 'Completed source candle membership is unavailable', unknown=True,
                  kind='data_coverage', recipe='O004' if label == 'breakout' else 'O002')
        elif complete is not True:
            issue(field, 'An incomplete candle cannot establish its final close or retest bounds',
                  kind='ordering', recipe='O004' if label == 'breakout' else 'O002')

    # The selected band is the candidate's owned identity set, not a required
    # duplicate scalar transport field.
    for field in ("london_high", "asia_high", "breakout_close",
                  "vwap_at_retest", "retest_low", "retest_high"):
        binding = candidate.get("operands", {}).get(field, {})
        record = objects.get(binding.get("object_id"), {})
        if not record:
            continue
        for evidence_id in record.get("evidence_ids", []):
            row = evidence.get(evidence_id, {})
            if row.get('instrument_id') != candidate['instrument_id'] or row.get('band_id') not in candidate['band_ids']:
                issue(field, 'Source instrument/band differs from candidate', recipe='O046')

    findings.append({'field': 'general_target_policy', 'kind': 'source_definition', 'recipe_id': 'O141',
                     'reason': 'A general target policy is unpublished; a later reported 150-point gain is not an entry gate or target',
                     'affects_admission': False, 'affected_output': 'target_policy'})

    return findings


def _manifest_mutation_cases() -> list[dict]:
    """Return C08 cases that mutate actual C01 manifest records."""

    source = fixture_document("GB-VWAP", "sequence", "M03-F1", _positive_case())

    def case(suffix: str, mutate, expected: str, kind: str) -> dict:
        document = deepcopy(source)
        fid = f"M03-F1:{suffix}"
        candidate = document["candidates"][0]
        candidate["candidate_id"] = fid
        for assertion in document["assertions"]:
            assertion["candidate_id"] = fid
        mutate(document)
        return method_case("GB-VWAP", "sequence", fid, document, expected,
                           kind=kind)

    def late_vwap(document: dict) -> None:
        late = _positive_case()["retest_at"] + 1
        obj = next(row for row in document["objects"]
                   if row["object_id"].endswith(":vwap_known_at"))
        obj.update({"known_at": late, "as_of": late,
                    "formation_start": late, "formation_end": late})
        for evidence_row in document["evidence"]:
            if evidence_row["evidence_id"] in obj["evidence_ids"]:
                evidence_row.update({"known_at": late,
                                     "observation_start": late,
                                     "observation_end": late})

    def foreign_london(document: dict) -> None:
        obj = next(row for row in document["objects"]
                   if row["object_id"].endswith(":london_high"))
        obj["band_id"] = "foreign-band"
        for evidence_row in document["evidence"]:
            if evidence_row["evidence_id"] in obj["evidence_ids"]:
                evidence_row["band_id"] = "foreign-band"

    def missing_reset(document: dict) -> None:
        document["candidates"][0]["operands"].pop("vwap_reset_verified")

    return [
        case("c08-late", late_vwap, "fail", "c08_late"),
        case("c08-identity", foreign_london, "fail", "c08_identity"),
        case("c08-missing", missing_reset, "unknown", "c08_missing"),
    ]


def method_fixtures() -> list[dict]:
    """Return M03-F1/F2/F3 and C08 rows."""

    positive = _positive_case()
    rows = [method_case("GB-VWAP", "sequence", "M03-F1", positive, "pass")]

    rows.extend(_manifest_mutation_cases())

    close = deepcopy(positive)
    close["breakout_close"] = "101"
    rows.append(method_case("GB-VWAP", "sequence", "M03-F2-close", close,
                            "fail", kind="negative"))

    order = deepcopy(positive)
    order["retest_at"] = _t(9, 30)
    rows.append(method_case("GB-VWAP", "sequence", "M03-F2-order", order,
                            "fail", kind="negative"))

    short = deepcopy(positive)
    short["side"] = "short"
    rows.append(method_case("GB-VWAP", "sequence", "M03-F2-side", short,
                            "fail", kind="negative"))

    later_gain = deepcopy(positive)
    later_gain["later_gain"] = "150"
    rows.append(method_case("GB-VWAP", "sequence", "M03-F2-later-gain",
                            later_gain, "pass", kind="negative"))

    reset_hole = deepcopy(positive)
    reset_hole["vwap_reset_verified"] = None
    reset_hole["comparison_vwap"] = "101.5"
    rows.append(method_case("GB-VWAP", "sequence", "M03-F3-reset",
                            reset_hole, "unknown", kind="hole"))

    return rows


__all__ = ["STAGE_LIMITS", "audit_candidate", "method_fixtures"]
