"""Historical F10 anchor provenance shared by measurement producers."""

from dataclasses import dataclass

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.object_graph import (
    AnchorVersion, EvidencePurpose, EvidenceVersion, Instrument, ObjectGraph, Support, content_hash,
)
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class AnchoredCapture:
    anchor: AnchorVersion
    evidence: tuple
    instrument: Instrument
    cut: int
    published_at: int
    definition_version: str
    registry_definition: str
    lineage_digest: str
    max_evidence: int
    max_bytes: int

    @property
    def id(self):
        return digest(self)


def capture_anchor(graph, *, anchor_version_id, instrument, cut, published_at,
                   definition_version, max_evidence=4096, max_bytes=8388608,
                   accumulation_evidence_versions=()):
    """Retain formation provenance plus optional independent accumulation receipts.

    Formation evidence stays in its original anchor order; extra receipt IDs
    must be sorted and unique. Both roles resolve from the actual graph.
    """
    positive_limit(max_evidence)
    positive_limit(max_bytes)
    bounded_name(anchor_version_id)
    bounded_name(definition_version)
    bounded_rows(accumulation_evidence_versions, max_evidence, name="accumulation evidence")
    if type(accumulation_evidence_versions) is not tuple:
        raise ContractError("accumulation evidence versions must be an immutable tuple")
    for identity in accumulation_evidence_versions:
        bounded_name(identity)
    if tuple(sorted(set(accumulation_evidence_versions))) != accumulation_evidence_versions:
        raise ContractError("accumulation evidence versions must be unique and canonical")
    timestamp(cut)
    timestamp(published_at)
    if type(graph) is not ObjectGraph or type(instrument) is not Instrument:
        raise ContractError("actual F10 graph and exact raw instrument required")
    instrument.__post_init__()
    if not instrument.valid(cut) or published_at < cut:
        raise ContractError("anchor instrument lifetime or publication is invalid")
    anchor = graph.get_version(anchor_version_id)
    if type(anchor) is not AnchorVersion or anchor.known_at > cut:
        raise ContractError("anchor is unavailable at its declared historical cut")
    if set(anchor.evidence_versions).intersection(accumulation_evidence_versions):
        raise ContractError("accumulation evidence repeats formation evidence")
    if len(anchor.evidence_versions)+len(accumulation_evidence_versions)>max_evidence:
        raise ContractError("anchor and accumulation evidence exceed the combined capacity")
    evidence_ids = (*anchor.evidence_versions, *accumulation_evidence_versions)
    bounded_rows(evidence_ids, max_evidence, name="anchor and accumulation evidence")
    evidence = tuple(graph.get_version(i) for i in evidence_ids)
    if any(type(e) is not EvidenceVersion or e.instrument != instrument
           or e.purpose != EvidencePurpose.MEASUREMENT or e.support != Support.OBSERVED
           or e.known_at > cut or e.event_at > cut for e in evidence):
        raise ContractError("anchor needs observed same-instrument measurement evidence")
    closure = graph.lineage_closure((anchor_version_id, *accumulation_evidence_versions), cut)
    result = AnchoredCapture(anchor, evidence, instrument, cut, published_at, definition_version,
                             graph.definition.version, content_hash(closure), max_evidence, max_bytes)
    if len(canonical_json(result)) > max_bytes:
        raise ContractError("anchor capture byte capacity exhausted")
    return result


def validate_anchor(captured, graph):
    if (type(captured) is not AnchoredCapture or type(graph) is not ObjectGraph
            or type(captured.anchor) is not AnchorVersion or type(captured.evidence) is not tuple):
        raise ContractError("typed anchor capture required")
    bounded_rows(captured.evidence, captured.max_evidence, name="anchor and accumulation evidence")
    if any(type(e) is not EvidenceVersion for e in captured.evidence):
        raise ContractError("typed retained anchor evidence required")
    actual_anchor = graph.get_version(captured.anchor.version_id)
    if type(actual_anchor) is not AnchorVersion:
        raise IntegrityError("anchor capture lacks its actual retained formation")
    formation_ids = set(actual_anchor.evidence_versions)
    accumulation_ids = tuple(e.version_id for e in captured.evidence if e.version_id not in formation_ids)
    fresh = capture_anchor(graph, anchor_version_id=captured.anchor.version_id,
        accumulation_evidence_versions=accumulation_ids,
        **{k: getattr(captured, k) for k in ("instrument", "cut", "published_at", "definition_version",
                                          "max_evidence", "max_bytes")})
    if fresh != captured:
        raise IntegrityError("anchor capture differs from its actual historical graph")


def bind_anchor_members(anchor, graph, capture, view, *, member_digest=None, published_at=None):
    """Bind accumulation evidence in addition to the anchor's historical provenance."""
    validate_anchor(anchor, graph)
    validate_trade_window(capture, view)
    w = capture.window
    if w.instrument not in (anchor.instrument.key, anchor.instrument.raw_symbol):
        raise ContractError("measurement accumulation and anchor raw instrument differ")
    publication = max(w.published_at, anchor.published_at) if published_at is None else timestamp(published_at)
    if (anchor.anchor.end > w.cut or anchor.cut > publication
            or anchor.published_at > publication or w.published_at > publication):
        raise ContractError("anchor was not available for the measurement publication")
    expected = digest(capture.record()) if member_digest is None else bounded_name(member_digest)
    if expected not in {e.content_digest for e in anchor.evidence}:
        raise IntegrityError("anchor evidence does not bind the full formula-specific source recipe")
    return expected
