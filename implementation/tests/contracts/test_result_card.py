"""The verifier validates RESULT_CARD.json (DELIVERABLES.md): each rule below catches one
distinct way a task could close without a judgeable result."""
import json
from pathlib import Path

import pytest

from trading_research.research.contracts import receipts


def valid_card() -> dict:
    return {
        "schema_version": "research-result-card-v1",
        "question": "Does any candidate beat B0.2 under the gates?",
        "headline": [{"value": 0, "unit": "candidates promoted", "support": 148, "artifact": "BREADTH_RESULTS.json", "sha256": "a" * 64},
                     {"value": 37.4, "unit": "points/day paired improvement, best candidate", "interval": [-2.1, 71.0], "artifact": "BREADTH_RESULTS.json", "sha256": "a" * 64}],
        "target": {"text": "promotion gates of EVALUATION.md", "met": "no"},
        "verdict": {"value": "needs_upgrade", "reason": "no candidate clears support and the lower bound"},
        "lever": {"change": "location-first revisit of the 48 location_miss candidates in Phase 3", "evidence": "a positive lower bound on the same folds"},
        "limits": ["rehearsal pairing root; hold-out excluded"],
    }


def write(tmp_path: Path, card) -> Path:
    path = tmp_path / "RESULT_CARD.json"
    path.write_text(json.dumps(card))
    return path


def test_a_valid_card_passes(tmp_path):
    assert receipts.result_card_failures(write(tmp_path, valid_card())) == []


@pytest.mark.parametrize("mutate, expect", [
    (lambda c: c.update(schema_version="v0"), "schema_version"),
    (lambda c: c.update(question=""), "question"),
    (lambda c: c.update(headline=[]), "1 to 5"),
    (lambda c: c.update(headline=[dict(valid_card()["headline"][0], value="many")]), "value must be a number"),
    (lambda c: c.update(headline=[{k: v for k, v in valid_card()["headline"][0].items() if k != "support"}]), "interval"),
    (lambda c: c.update(headline=[dict(valid_card()["headline"][0], sha256="nope")]), "sha256"),
    (lambda c: c.update(target={"text": "gates", "met": "mostly"}), "met"),
    (lambda c: c.update(verdict={"value": "great", "reason": "x"}), "verdict"),
    (lambda c: c.pop("lever"), "lever"),
    (lambda c: c.update(limits="none"), "limits"),
])
def test_each_defect_is_named(tmp_path, mutate, expect):
    card = valid_card(); mutate(card)
    problems = receipts.result_card_failures(write(tmp_path, card))
    assert problems and any(expect in p for p in problems), problems


def test_done_well_needs_no_lever(tmp_path):
    card = valid_card(); card["verdict"] = {"value": "done_well", "reason": "gates met"}; card.pop("lever")
    assert receipts.result_card_failures(write(tmp_path, card)) == []


def test_the_artifact_check_reports_card_defects_as_inventory_failures(tmp_path):
    card = valid_card(); card.pop("lever")
    path = write(tmp_path, card)
    failures: list = []
    receipts._check_artifacts([{"path": str(path), "sha256": receipts.file_digest(path), "bytes": path.stat().st_size}], tmp_path / "TASK_RECEIPT.json", failures)
    assert failures and all(f.code == receipts.FailureCode.INVENTORY for f in failures)
