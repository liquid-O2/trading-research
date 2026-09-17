"""Read frozen B0 and B0.1 census jobs. The search never recomputes either baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import gzip
import hashlib
import json

from trading_research.errors import IntegrityError

PINNED_RUN_ID = "20def36e065c13d7"
PINNED_MANIFEST_SHA256 = "20def36e065c13d75d738fbce475cf7ea5425255488861c58a1b5fbbbe8b488f"
PINNED_SUMMARY_SHA256 = "073f270c5a5f454f4a338219eca9421e43bd3440f4ed42252dfb19f5f4d7838d"
DEFAULT_B01_ROOT = Path("/workspace/implementation/reports/research-work/baseline-repair") / PINNED_RUN_ID
DEFAULT_B0_ROOT = Path("/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1")


class CensusIntegrityError(IntegrityError):
    """Census bytes failed the pinned hash check."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def coverage_id(method_id: str, branch: str) -> str:
    return f"{method_id}:branch:{branch}"


def job_filename(coverage_id: str) -> str:
    return coverage_id.replace(":", "--") + ".json.gz"


def resolve_coverage_id(method_id: str | None, branch: str | None, coverage: str | None) -> str:
    if coverage:
        return str(coverage)
    if method_id and branch:
        return coverage_id(method_id, branch)
    raise CensusIntegrityError("coverage_id or method_id+branch is required")


def _read_json_gz(path: Path) -> dict[str, Any]:
    return json.loads(gzip.decompress(path.read_bytes()))


def _episode_verdict(episode: Mapping[str, Any]) -> dict[str, Any]:
    assessment = episode.get("strategy_assessment") or {}
    return {
        "candidate_id": episode.get("candidate_id"),
        "research_verdict": episode.get("research_verdict"),
        "status": assessment.get("status") or episode.get("status"),
        "side": episode.get("side"),
        "reference_id": episode.get("reference_id"),
    }


class CensusReader:
    """Hash-gated reader for B0.1 repair jobs and B0 run-1.0.1 jobs."""

    def __init__(
        self,
        *,
        b01_root: Path | str | None = None,
        b0_root: Path | str | None = None,
        expected_manifest_sha256: str = PINNED_MANIFEST_SHA256,
        expected_summary_sha256: str = PINNED_SUMMARY_SHA256,
    ) -> None:
        self.b01_root = Path(b01_root or DEFAULT_B01_ROOT)
        self.b0_root = Path(b0_root or DEFAULT_B0_ROOT)
        self.expected_manifest_sha256 = expected_manifest_sha256
        self.expected_summary_sha256 = expected_summary_sha256
        self.manifest_sha256, self.summary_sha256 = self._verify()

    def _verify(self) -> tuple[str, str]:
        complete_path = self.b01_root / "RUN_COMPLETE.json"
        manifest_path = self.b01_root / "MANIFEST.json"
        summary_path = self.b01_root / "SUMMARY.json"
        if not complete_path.is_file():
            raise CensusIntegrityError(f"RUN_COMPLETE.json missing: {complete_path}")
        if not manifest_path.is_file():
            raise CensusIntegrityError(f"MANIFEST.json missing: {manifest_path}")
        if not summary_path.is_file():
            raise CensusIntegrityError(f"SUMMARY.json missing: {summary_path}")
        complete = json.loads(complete_path.read_text())
        manifest_sha256 = sha256_file(manifest_path)
        summary_sha256 = sha256_file(summary_path)
        claimed_manifest = str(complete.get("manifest_sha256") or "")
        claimed_summary = str(complete.get("summary_sha256") or "")
        if manifest_sha256 != claimed_manifest:
            raise CensusIntegrityError("MANIFEST.json does not match RUN_COMPLETE.json manifest_sha256")
        if summary_sha256 != claimed_summary:
            raise CensusIntegrityError("SUMMARY.json does not match RUN_COMPLETE.json summary_sha256")
        if manifest_sha256 != self.expected_manifest_sha256:
            raise CensusIntegrityError("MANIFEST.json does not match the pinned B0.1 manifest_sha256")
        if summary_sha256 != self.expected_summary_sha256:
            raise CensusIntegrityError("SUMMARY.json does not match the pinned B0.1 summary_sha256")
        return manifest_sha256, summary_sha256

    def hash_check(self) -> dict[str, Any]:
        return {
            "ok": True,
            "run_id": PINNED_RUN_ID,
            "b01_root": str(self.b01_root),
            "b0_root": str(self.b0_root),
            "manifest_sha256": self.manifest_sha256,
            "summary_sha256": self.summary_sha256,
            "pinned_manifest_sha256": self.expected_manifest_sha256,
            "pinned_summary_sha256": self.expected_summary_sha256,
        }

    def b01_path(self, day: str, coverage_id: str) -> Path:
        return self.b01_root / "jobs" / day / job_filename(coverage_id)

    def b0_path(self, day: str, coverage_id: str) -> Path:
        return self.b0_root / "jobs" / "evaluation" / day / job_filename(coverage_id)

    def b01_document(
        self,
        day: str,
        *,
        method_id: str | None = None,
        branch: str | None = None,
        coverage_id: str | None = None,
    ) -> dict[str, Any]:
        cid = resolve_coverage_id(method_id, branch, coverage_id)
        path = self.b01_path(day, cid)
        if not path.is_file():
            raise CensusIntegrityError(f"B0.1 job missing: {path}")
        return _read_json_gz(path)

    def b0_document(
        self,
        day: str,
        *,
        method_id: str | None = None,
        branch: str | None = None,
        coverage_id: str | None = None,
    ) -> dict[str, Any]:
        cid = resolve_coverage_id(method_id, branch, coverage_id)
        path = self.b0_path(day, cid)
        if not path.is_file():
            raise CensusIntegrityError(f"B0 job missing: {path}")
        return _read_json_gz(path)

    def b01_episodes(self, day: str, **identity: str | None) -> list[dict[str, Any]]:
        return list(self.b01_document(day, **identity).get("episodes") or [])

    def b0_episodes(self, day: str, **identity: str | None) -> list[dict[str, Any]]:
        return list(self.b0_document(day, **identity).get("episodes") or [])

    def b01_verdicts(self, day: str, **identity: str | None) -> list[dict[str, Any]]:
        return [_episode_verdict(episode) for episode in self.b01_episodes(day, **identity)]

    def b0_verdicts(self, day: str, **identity: str | None) -> list[dict[str, Any]]:
        return [_episode_verdict(episode) for episode in self.b0_episodes(day, **identity)]


def open_census(
    *,
    b01_root: Path | str | None = None,
    b0_root: Path | str | None = None,
) -> CensusReader:
    return CensusReader(b01_root=b01_root, b0_root=b0_root)
