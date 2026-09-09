"""Descriptive heldout entry point, preserving the accepted extraction module."""
import hashlib
import json
from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import ArtifactStore, artifact_ref
from trading_research.research.jumbo_study import _predecessor, _run_extraction

def _descriptive_confirmation_authorized(packet, predecessor):
    """Packet flag must match the exact loaded predecessor; it cannot open a model gate."""
    expected = (predecessor is not None
                and predecessor.get("success") is True
                and predecessor.get("mode") == "develop"
                and predecessor.get("phase") == "extract")
    flag = packet.get("descriptive_confirmation") is True
    if flag is not expected:
        raise IntegrityError("descriptive_confirmation does not match the exact predecessor")
    return expected

def _admission_from_extract(extract_worker, root, store):
    identity = extract_worker.get("admission_predecessor")
    if identity is None:
        raise IntegrityError("extract predecessor lacks admission_predecessor")
    raw = (root / identity["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != identity["sha256"]:
        raise IntegrityError("admission predecessor identity changed")
    execution = json.loads(raw)
    if execution.get("success") is not True:
        raise IntegrityError("admission predecessor was not successful")
    if execution.get("mode") != "admit":
        raise IntegrityError("admission predecessor mode differs")
    phase = execution.get("phase")
    if phase is not None and phase != "full_admission":
        raise IntegrityError("admission predecessor phase differs")
    admitted = store.read_json(artifact_ref(execution["worker_report"]))
    if admitted.get("mode") != "admit" or admitted.get("success") is not True:
        raise IntegrityError("admission worker is not a successful admit report")
    return admitted

def _source_supplement_from_extract(extract_worker, store):
    ref = extract_worker.get("source_supersession")
    if not ref:
        raise IntegrityError("extract predecessor lacks source_supersession")
    if ref.get("kind") != "jumbo_actual_definition_supersession_report_v1":
        raise IntegrityError("source supersession kind differs")
    report = store.read_json(artifact_ref(ref))
    if report.get("actual_accepted") is not True:
        raise IntegrityError("source supersession was not actually accepted")
    return ref

def _descriptive_confirmation_report(extracted, packet, predecessor):
    if extracted.get('success') is not True or extracted.get('model_fits') != 0:
        raise IntegrityError('descriptive confirmation did not complete without model fitting')
    result = dict(extracted)
    result.update(
        mode=packet["mode"], phase=packet["phase"], descriptive_confirmation=True,
        development_predecessor=packet["predecessor"],
        admission_predecessor=predecessor.get("admission_predecessor"),
        family_statistics_complete=False, model_fits=0,
        context_models_complete=False, location_quality_complete=False,
        scope="Complete declared heldout descriptive extraction; Context and Location scoring remain later",
        remaining=["Pooled training/development phase objects and year-to-year stability remain for later supervisor assessment of the complete catalogue",
                   "Ordinary/event-day and width-regime timing comparisons when those labels exist",
                   "Chronological independent model comparisons, calibration and incremental information",
                   "Full conditional range/internal/extension/statistical Location catalogue quality",
                   "Exact unresolved source formulas retain their separately evidenced dependencies; generic ranges do not close them"])
    return result


def run(packet, protocol, root):
    if packet.get('mode') != 'confirm' or packet.get('phase') != 'confirmation':
        raise IntegrityError('descriptive confirmation requires its registered mode and phase')
    store = ArtifactStore(root / 'evidence/trials/artifacts')
    predecessor = _predecessor(packet, root, store)
    if not _descriptive_confirmation_authorized(packet, predecessor):
        raise IntegrityError('descriptive entry requires an authenticated extraction predecessor')
    admitted = _admission_from_extract(predecessor, root, store)
    supplement = _source_supplement_from_extract(predecessor, store)
    extracted = _run_extraction(packet, protocol, root, store, admitted=admitted,
                               heldout=True, frozen_source_supplement=supplement)
    return _descriptive_confirmation_report(extracted, packet, predecessor)
