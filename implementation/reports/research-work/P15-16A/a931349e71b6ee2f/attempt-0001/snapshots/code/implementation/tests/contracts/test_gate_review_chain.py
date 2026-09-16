"""Gate-review registry hash may be superseded by the plan amendment chain."""

from __future__ import annotations

import json
from pathlib import Path

from trading_research.research.contracts.identity import digest, file_digest
from trading_research.research.contracts.receipts import (
    CANONICAL_REGISTRY_REL,
    FailureCode,
    load_task_graph,
    verify_gate_review,
    verify_subphase_receipt,
)
from tests.rule_discovery.test_p15_01 import (
    AMENDMENT_ROOT,
    REGISTRY,
    _amendments_path,
    _new_shape_entry,
    _write_pair,
    _write_review,
    _write_subphase,
)

SUBPHASE_04 = Path(
    "/workspace/implementation/reports/research-work/04-family-adapters/8b7e84385817cb18/attempt-0001/SUBPHASE_RECEIPT.json"
)
REVIEW_04 = Path(
    "/workspace/implementation/reports/research-work/04-family-adapters/8b7e84385817cb18/attempt-0001/GATE_REVIEW.json"
)


def _closed_foundation_review(tmp_path: Path) -> tuple[Path, Path, Path]:
    graph, first, child = _write_pair(tmp_path)
    subphase = _write_subphase(tmp_path, graph, first, child)
    review = _write_review(tmp_path, subphase=subphase, graph=graph, first=first, child=child)
    control = verify_subphase_receipt(
        subphase,
        graph_path=graph,
        receipts_root=tmp_path,
        gate_review=review,
    )
    assert control.ok is True, control.failures
    assert control.failures == ()
    return graph, subphase, review


def _write_pinned_registry(subphase: Path, document: dict) -> str:
    pinned_copy = subphase.parent / "snapshots/plan" / CANONICAL_REGISTRY_REL
    pinned_copy.parent.mkdir(parents=True, exist_ok=True)
    pinned_copy.write_text(json.dumps(document, indent=2) + "\n")
    return file_digest(pinned_copy)


def _rebind_review_registry(review: Path, pinned_hash: str) -> None:
    payload = json.loads(review.read_text())
    payload["registry"]["sha256"] = pinned_hash
    review.write_text(json.dumps(payload, indent=2) + "\n")


def _registry_amendments(tmp_path: Path, *, before: str, after: str, previous: str) -> Path:
    return _amendments_path(
        tmp_path,
        [
            AMENDMENT_ROOT,
            _new_shape_entry(path=CANONICAL_REGISTRY_REL, before=before, after=after, previous=previous),
        ],
    )


def _verify(subphase: Path, graph: Path, tmp_path: Path, review: Path, amendments: Path):
    return verify_subphase_receipt(
        subphase,
        graph_path=graph,
        receipts_root=tmp_path,
        gate_review=review,
        amendments_path=amendments,
    )


def _unchanged_pinned_registry() -> dict:
    document = json.loads(REGISTRY.read_text())
    document["_fixture"] = "pinned"
    return document


def test_gate_review_stale_registry_hash_verifies_when_amendment_chain_carries_unchanged_cases(tmp_path: Path) -> None:
    graph, subphase, review = _closed_foundation_review(tmp_path)
    pinned_hash = _write_pinned_registry(subphase, _unchanged_pinned_registry())
    _rebind_review_registry(review, pinned_hash)
    live_hash = file_digest(REGISTRY)
    assert pinned_hash != live_hash
    amendments = _registry_amendments(
        tmp_path,
        before=pinned_hash,
        after=live_hash,
        previous=digest(AMENDMENT_ROOT),
    )
    result = _verify(subphase, graph, tmp_path, review, amendments)
    assert result.ok is True
    assert result.failures == ()


def test_gate_review_stale_registry_hash_fails_when_amendment_chain_broken(tmp_path: Path) -> None:
    graph, subphase, review = _closed_foundation_review(tmp_path)
    pinned_hash = _write_pinned_registry(subphase, _unchanged_pinned_registry())
    _rebind_review_registry(review, pinned_hash)
    live_hash = file_digest(REGISTRY)
    amendments = _registry_amendments(
        tmp_path,
        before=pinned_hash,
        after=live_hash,
        previous="0" * 64,
    )
    result = _verify(subphase, graph, tmp_path, review, amendments)
    assert result.ok is False
    details = [item.detail for item in result.failures]
    codes = {item.code for item in result.failures}
    assert FailureCode.ARTIFACT_HASH in codes
    assert FailureCode.GATE_REVIEW in codes
    assert "registry hash does not match file bytes" in details
    assert "review registry hash is not the current assurance registry" in details
    assert all("review-bound case" not in item.detail for item in result.failures)


def test_gate_review_stale_registry_hash_fails_when_sha256_after_is_not_live(tmp_path: Path) -> None:
    graph, subphase, review = _closed_foundation_review(tmp_path)
    pinned_hash = _write_pinned_registry(subphase, _unchanged_pinned_registry())
    _rebind_review_registry(review, pinned_hash)
    live_hash = file_digest(REGISTRY)
    amendments = _registry_amendments(
        tmp_path,
        before=pinned_hash,
        after=digest({"not-live": live_hash}),
        previous=digest(AMENDMENT_ROOT),
    )
    result = _verify(subphase, graph, tmp_path, review, amendments)
    assert result.ok is False
    details = [item.detail for item in result.failures]
    codes = {item.code for item in result.failures}
    assert FailureCode.ARTIFACT_HASH in codes
    assert FailureCode.GATE_REVIEW in codes
    assert "registry hash does not match file bytes" in details
    assert "review registry hash is not the current assurance registry" in details
    assert all("review-bound case" not in item.detail for item in result.failures)


def test_gate_review_stale_registry_hash_fails_when_review_bound_case_probe_changed(tmp_path: Path) -> None:
    graph, subphase, review = _closed_foundation_review(tmp_path)
    pinned_doc = json.loads(REGISTRY.read_text())
    for case in pinned_doc["cases"]:
        if case.get("id") == "S01":
            case["probe"] = "fixture-changed S01 probe"
            break
    else:
        raise AssertionError("S01 missing from live registry")
    pinned_hash = _write_pinned_registry(subphase, pinned_doc)
    _rebind_review_registry(review, pinned_hash)
    live_hash = file_digest(REGISTRY)
    amendments = _registry_amendments(
        tmp_path,
        before=pinned_hash,
        after=live_hash,
        previous=digest(AMENDMENT_ROOT),
    )
    result = _verify(subphase, graph, tmp_path, review, amendments)
    assert result.ok is False
    assert any("review-bound case S01 changed after the gate closed" in item.detail for item in result.failures)
    assert all(item.detail != "registry hash does not match file bytes" for item in result.failures)


def test_current_04_family_adapters_gate_review_verifies() -> None:
    graph, graph_fail = load_task_graph()
    assert graph is not None
    assert graph_fail == ()
    failures = verify_gate_review(
        REVIEW_04,
        SUBPHASE_04,
        file_digest(SUBPHASE_04),
        graph,
    )
    assert failures == ()
