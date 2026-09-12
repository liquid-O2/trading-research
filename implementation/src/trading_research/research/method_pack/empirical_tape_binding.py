"""Exact native O098 source assembly for an observed M09 zone return.

M09 opportunities are event-point observations and therefore cannot be routed
through the bar-only ``BarMarket.source_assembly`` helper.  This bridge selects
the two immutable formation executions plus the actual return-touch execution
batch by physical row identity, resolves them against frozen full-file hashes,
and supplies one bounded O098 object to the accepted method assembler.  It does
not infer private selection, an order, a fill, or continuous coverage from the
selected subset.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .assembly import assemble_episode
from .empirical_protocol import Opportunity, content_hash
from .empirical_registry import validate_comparison_candidate
from .native_resolution import NativeEvidenceError, NativeResolver
from .objects.native_boundary import run_native_object


def _physical_event_id(event_id: str, root: Path, instrument_id: int | str):
    try:
        source, row_text, event_instrument = str(event_id).rsplit(":", 2)
        source_row = int(row_text)
    except (TypeError, ValueError) as exc:
        raise NativeEvidenceError("M09 event lacks a physical native event_id") from exc
    if source_row < 0 or str(event_instrument) != str(instrument_id):
        raise NativeEvidenceError("M09 event_id has foreign physical identity")
    path = Path(source)
    path = path.resolve() if path.is_absolute() else (root / path).resolve()
    if not path.is_relative_to(root):
        raise NativeEvidenceError("M09 event source escapes native data root")
    return path.relative_to(root).as_posix(), source_row


def _selected_event_ids(opportunity: Opportunity) -> list[str]:
    formation = opportunity.reference.get("formation_event_ids")
    if not isinstance(formation, (list, tuple)) or len(formation) != 2:
        raise NativeEvidenceError("M09 opportunity lacks its exact formation pair")
    touch = opportunity.trigger.get("member_event_ids")
    if touch is None:
        touch = [opportunity.trigger.get("event_id")]
    if not isinstance(touch, (list, tuple)) or not touch or any(not item for item in touch):
        raise NativeEvidenceError("M09 opportunity lacks its exact touch membership")
    selected = [*formation, *touch]
    if len(selected) != len(set(selected)):
        raise NativeEvidenceError("M09 formation/touch physical membership overlaps")
    return [str(item) for item in selected]


def _locators(opportunity: Opportunity, tape: Mapping[str, Any], root: Path):
    dataset = tape.get("dataset_id")
    if not isinstance(dataset, str) or "trades" not in dataset and "mbp-1" not in dataset:
        raise NativeEvidenceError("M09 tape envelope lacks its execution dataset")
    identities = tape.get("source_files")
    if not isinstance(identities, list):
        raise NativeEvidenceError("M09 tape envelope lacks frozen source identities")
    frozen = {}
    for identity in identities:
        if not isinstance(identity, Mapping) or identity.get("dataset_id") != dataset:
            raise NativeEvidenceError("M09 tape source identity has foreign dataset")
        path = str(identity.get("path", "")).replace("\\", "/")
        digest = identity.get("sha256")
        if (not path or not isinstance(digest, str) or len(digest) != 64
                or identity.get("hash_basis") != "full_file_sha256"):
            raise NativeEvidenceError("M09 tape source lacks a full-file identity")
        if path in frozen:
            raise NativeEvidenceError("M09 tape repeats a frozen source identity")
        frozen[path] = digest
    grouped = {}
    for event_id in _selected_event_ids(opportunity):
        path, source_row = _physical_event_id(event_id, root, opportunity.instrument_id)
        digest = frozen.get(path)
        if digest is None:
            raise NativeEvidenceError("M09 event is outside the frozen tape envelope")
        grouped.setdefault((path, digest), []).append(source_row)
    locators = []
    for (path, digest), indices in sorted(grouped.items()):
        for index in sorted(indices):
            if locators and locators[-1]["source_file"] == path and locators[-1]["row_end"] == index:
                locators[-1]["row_end"] += 1
            else:
                locators.append({"source_file": path, "dataset_id": dataset,
                                 "sha256": digest, "row_start": index,
                                 "row_end": index + 1})
    return dataset, locators


def assemble_m09(rule: Mapping[str, Any], opdict: Mapping[str, Any],
                 registry: Mapping[str, Any], market: Any,
                 tape: Mapping[str, Any]):
    """Assemble one M09 opportunity with exact pair+touch O098 evidence.

    Returns :class:`assembly.AssembledEpisode`.  The O098 object is expected to
    remain coverage-incomplete because selected events do not prove continuous
    tape membership; its observed event records are still exact and replayable.
    """
    opportunity = Opportunity(**dict(opdict)).validate()
    if (rule.get("method_id"), rule.get("branch")) != ("REFILL-STUDY", "touch_record"):
        raise ValueError("M09 assembly requires the frozen touch_record rule")
    if (opportunity.rule_id != rule.get("rule_id")
            or opportunity.registry_sha256 != registry.get("registry_sha256")
            or opportunity.partition_id != market.partition.get("partition_id")
            or str(opportunity.instrument_id) != str(market.instrument_id)):
        raise ValueError("M09 opportunity differs from rule/registry/partition identity")
    root = Path(market.window.resolver.root).resolve()
    _, locators = _locators(opportunity, tape, root)
    # Reuse the partition resolver so its immutable full-file digest cache is
    # shared by all M09 returns in this bounded job. Selected row ranges are
    # still re-read and revalidated for each replayable object.
    resolver = market.window.resolver
    formed_at = opportunity.reference.get("formed_at")
    if type(formed_at) is not int:
        raise NativeEvidenceError("M09 opportunity lacks its zone formation clock")
    formation_seconds = int(rule["parameters"]["formation_seconds"])
    broad_start = formed_at - formation_seconds * 1_000_000_000
    broad_end = opportunity.occurrence_end
    broad = resolver.resolve(locators, instrument_id=opportunity.instrument_id,
                             start_ns=broad_start, end_ns=broad_end,
                             as_of=opportunity.available_at,
                             use_at=opportunity.available_at)
    actual_start = min(row["event_ns"] for row in broad.members)
    actual_end = max(row["event_ns"] for row in broad.members) + 1
    # Re-resolve the exact event envelope. Coverage remains unknown because the
    # locators intentionally contain only pair+touch evidence.
    resolver.resolve(locators, instrument_id=opportunity.instrument_id,
                     start_ns=actual_start, end_ns=actual_end,
                     as_of=opportunity.available_at,
                     use_at=opportunity.available_at)
    object_id = "m09-o098-" + content_hash({
        "opportunity_id": opportunity.opportunity_id,
        "locators": locators,
    })[:24]
    obj = {
        "object_id": object_id, "recipe_id": "O098",
        "method_id": "REFILL-STUDY", "branch_scope": ["touch_record"],
        "author": "empirical-research", "instrument_id": opportunity.instrument_id,
        "parent_ids": [],
        "source_ref": "planning/phase-1-live/SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md",
        "source_version": "empirical-v1", "value": {}, "units": {},
        "formation_start": actual_start, "formation_end": actual_end,
        "as_of": opportunity.available_at, "known_at": opportunity.available_at,
        "state": "computed", "hole_ids": [], "evidence_ids": [],
        "inputs": {"use_at": opportunity.available_at,
                   "as_of": opportunity.available_at},
        "raw_member_locators": locators,
    }
    # Fail before assembly if the claimed native evidence cannot replay.
    result = run_native_object(obj, resolver)
    if result.base_ok is False or result.evidence_class != "resolved_native":
        raise NativeEvidenceError("M09 selected native execution evidence is invalid")
    candidate = {
        "candidate_id": opportunity.opportunity_id, "rule_id": rule["rule_id"],
        "registry_version": registry["version"],
        "registry_sha256": registry["registry_sha256"],
        "assumption_ids": list(rule["assumption_ids"]),
        "method_id": "REFILL-STUDY", "branch": "touch_record",
        "side": opportunity.side, "instrument_id": opportunity.instrument_id,
        "session_date_et": opportunity.session_date,
        "decision_at": opportunity.available_at,
        "band_ids": [opportunity.reference_id],
        "cohort_id": opportunity.partition_id,
        "evidence_mode": "research_comparison", "variant": "comparison",
        "faithful_eligible": False, "object_ids": [object_id],
        "assertion_ids": [], "operands": {},
        "native_tape_evidence_sha256": tape.get("evidence_sha256"),
    }
    validate_comparison_candidate(candidate, registry)
    assembled = assemble_episode(candidate, [obj], resolver=resolver)
    if (assembled.result.get("faithful_eligible") is not False
            or assembled.result.get("detected_causal_violations")):
        raise ValueError("M09 O098 assembly crossed causal/faithfulness boundary")
    return assembled


__all__ = ["assemble_m09"]
