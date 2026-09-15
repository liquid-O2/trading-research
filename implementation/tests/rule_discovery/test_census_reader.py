"""Census reader hash gate and B0 / B0.1 serving."""

from __future__ import annotations

from pathlib import Path
import json
import shutil

import pytest

from trading_research.research.rule_discovery.census_reader import (
    PINNED_MANIFEST_SHA256,
    PINNED_SUMMARY_SHA256,
    CensusIntegrityError,
    CensusReader,
    open_census,
    sha256_file,
)

B01_ROOT = Path("/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7")


def test_real_census_verifies_pinned_hashes():
    reader = open_census()
    check = reader.hash_check()
    assert check["ok"] is True
    assert check["manifest_sha256"] == PINNED_MANIFEST_SHA256
    assert check["summary_sha256"] == PINNED_SUMMARY_SHA256
    assert sha256_file(B01_ROOT / "MANIFEST.json") == PINNED_MANIFEST_SHA256
    assert sha256_file(B01_ROOT / "SUMMARY.json") == PINNED_SUMMARY_SHA256


def test_tampered_summary_byte_refuses(tmp_path: Path):
    (tmp_path / "RUN_COMPLETE.json").write_text((B01_ROOT / "RUN_COMPLETE.json").read_text())
    shutil.copy(B01_ROOT / "MANIFEST.json", tmp_path / "MANIFEST.json")
    summary = (B01_ROOT / "SUMMARY.json").read_bytes()
    flipped = bytes([summary[0] ^ 0x01]) + summary[1:]
    assert flipped != summary
    (tmp_path / "SUMMARY.json").write_bytes(flipped)
    with pytest.raises(CensusIntegrityError, match="SUMMARY.json"):
        CensusReader(b01_root=tmp_path)


def test_tampered_manifest_byte_refuses(tmp_path: Path):
    (tmp_path / "RUN_COMPLETE.json").write_text((B01_ROOT / "RUN_COMPLETE.json").read_text())
    shutil.copy(B01_ROOT / "SUMMARY.json", tmp_path / "SUMMARY.json")
    manifest = (B01_ROOT / "MANIFEST.json").read_bytes()
    (tmp_path / "MANIFEST.json").write_bytes(bytes([manifest[0] ^ 0x01]) + manifest[1:])
    with pytest.raises(CensusIntegrityError, match="MANIFEST.json"):
        CensusReader(b01_root=tmp_path)


def test_b01_and_b0_episodes_and_verdicts_are_served_not_recomputed():
    reader = open_census()
    b01 = reader.b01_document("2020-01-02", method_id="GB-FAIL", branch="nyam_box")
    b0 = reader.b0_document("2020-01-02", method_id="GB-FAIL", branch="nyam_box")
    assert b01["coverage_id"] == "GB-FAIL:branch:nyam_box"
    assert b0["coverage_id"] == "GB-FAIL:branch:nyam_box"
    assert len(b01["episodes"]) == 2
    verdicts = reader.b01_verdicts("2020-01-02", method_id="GB-FAIL", branch="nyam_box")
    assert {row["research_verdict"] for row in verdicts} == {"pass", "fail"}
    assert all("candidate_id" in row for row in verdicts)


def test_missing_job_refuses():
    reader = open_census()
    with pytest.raises(CensusIntegrityError, match="B0.1 job missing"):
        reader.b01_document("1999-01-01", coverage_id="GB-FAIL:branch:nyam_box")
