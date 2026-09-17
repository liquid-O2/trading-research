"""The three receipt rules of the 2026-09-17 integration patch.

Each test states the rule's requirement, exercises the real checker, and pairs a
sensitive positive case with a negative control that must still fail. Expected
results come from the rule, not from the implementation's wording.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from trading_research.research.contracts.identity import file_digest
from trading_research.research.contracts.receipts import (
    AMENDMENTS_REL,
    DEFAULT_ROOT,
    CheckFailure,
    _check_declared_source_files,
    _check_inventory,
    _unpinned_owned_paths,
)


# --------------------------------------------------------------------------
# Rule 1: the amendment chain is exempt from the PLAN_SNAPSHOT hash comparison.
# --------------------------------------------------------------------------


def _plan_failures(files: dict[str, str]) -> list[CheckFailure]:
    failures: list[CheckFailure] = []
    _check_declared_source_files(files, failures, "PLAN_SNAPSHOT.json", kind="plan")
    return failures


def test_a_stale_amendments_pin_is_exempt_but_other_plan_files_are_not():
    """The chain grows with every amendment and is the document the check reads
    to excuse other plan drift, so it cannot verify through itself. Every other
    plan file still must match the live bytes."""
    other = "planning/research-program/EVALUATION.md"
    stale = "0" * 64

    # positive: a pin that no longer matches the amendment chain raises nothing
    assert file_digest(DEFAULT_ROOT / AMENDMENTS_REL) != stale
    assert _plan_failures({AMENDMENTS_REL: stale}) == []

    # negative control: the same staleness on another plan file is still caught,
    # and that file passes when it matches, so the check is not simply silent
    failures = _plan_failures({other: stale})
    assert [f.code for f in failures] == ["IDENTITY"], failures
    assert other in failures[0].detail
    assert _plan_failures({other: file_digest(DEFAULT_ROOT / other)}) == []


def test_the_amendments_exemption_does_not_extend_to_the_code_snapshot():
    """The exemption is about plan identity; code identity is unchanged."""
    failures: list[CheckFailure] = []
    _check_declared_source_files(
        {AMENDMENTS_REL: "0" * 64}, failures, "CODE_SNAPSHOT.json", kind="code"
    )
    assert [f.code for f in failures] == ["IDENTITY"]


# --------------------------------------------------------------------------
# Rule 2: a required artifact that names a directory is satisfied by a manifest
# entry whose path passes through that directory.
# --------------------------------------------------------------------------


def _inventory_failures(entries: list[dict], required: list[str]) -> list[CheckFailure]:
    failures: list[CheckFailure] = []
    _check_inventory(
        {"artifact_manifest": entries},
        SimpleNamespace(artifacts=required),
        SimpleNamespace(required_task_artifacts=()),
        Path("RECEIPT.json"),
        failures,
    )
    return failures


def test_a_directory_artifact_is_satisfied_by_a_hashed_file_inside_it(tmp_path):
    """A directory name can never equal a manifest entry's file name, so the
    hashed files inside it are what satisfies the requirement."""
    report = tmp_path / "FAMILY_REPORTS" / "INDEX.json"
    report.parent.mkdir()
    report.write_text("{}\n")
    entries = [{"name": "INDEX.json", "path": str(report), "sha256": file_digest(report)}]

    # positive: the directory requirement is met by the file inside it
    assert _inventory_failures(entries, ["FAMILY_REPORTS"]) == []
    # a trailing slash in the requirement is the same requirement
    assert _inventory_failures(entries, ["FAMILY_REPORTS/"]) == []

    # negative control: a directory no manifest path passes through is missing,
    # and a plain file name that is nowhere in the manifest is still missing
    for required in (["EXIT_REPORTS"], ["TRIALS.jsonl"]):
        failures = _inventory_failures(entries, required)
        assert [f.code for f in failures] == ["INVENTORY"], (required, failures)
        assert required[0].rstrip("/") in failures[0].detail


def test_a_path_component_match_does_not_excuse_a_partial_name(tmp_path):
    """Matching is by whole path component, so a prefix of a directory name is
    not a match and cannot smuggle a requirement through."""
    report = tmp_path / "FAMILY_REPORTS" / "SIRES.md"
    report.parent.mkdir()
    report.write_text("x\n")
    entries = [{"name": "SIRES.md", "path": str(report), "sha256": file_digest(report)}]

    assert _inventory_failures(entries, ["FAMILY_REPORTS"]) == []
    assert [f.code for f in _inventory_failures(entries, ["FAMILY"])] == ["INVENTORY"]
    assert [f.code for f in _inventory_failures(entries, ["REPORTS"])] == ["INVENTORY"]


# --------------------------------------------------------------------------
# Rule 3: a live file added under an owned path is not a failure when a later
# verified receipt pins it at the live digest.
# --------------------------------------------------------------------------


def test_an_added_owned_file_is_missing_unless_a_successor_pins_it(tmp_path):
    """A file that appeared under an owned directory after the receipt closed is
    a failure by default and stops being one only when the supersession rule
    accepts that exact path at its live digest."""
    owned = tmp_path / "pkg"
    owned.mkdir()
    (owned / "old.py").write_text("old\n")
    added = owned / "added.py"
    added.write_text("added\n")
    pinned = {"pkg/old.py": file_digest(owned / "old.py")}

    # positive: without supersession the added file is reported
    assert _unpinned_owned_paths(["pkg/"], pinned, tmp_path) == ["pkg/added.py"]

    # the rule is applied to the added path at its LIVE digest
    seen: list[tuple[str, str]] = []

    def accept(rel: str, live: str) -> bool:
        seen.append((rel, live))
        return True

    assert _unpinned_owned_paths(["pkg/"], pinned, tmp_path, superseded=accept) == []
    assert seen == [("pkg/added.py", file_digest(added))]

    # negative controls: a successor that supersedes nothing, and one that
    # supersedes a different path, both leave the failure standing
    assert _unpinned_owned_paths(
        ["pkg/"], pinned, tmp_path, superseded=lambda rel, live: False
    ) == ["pkg/added.py"]
    assert _unpinned_owned_paths(
        ["pkg/"], pinned, tmp_path, superseded=lambda rel, live: rel == "pkg/other.py"
    ) == ["pkg/added.py"]


def test_supersession_never_invents_a_file_that_is_not_there(tmp_path):
    """An owned path named directly follows the same rule; a path that does not
    exist on disk cannot be superseded by any successor."""
    (tmp_path / "kept.py").write_text("kept\n")
    always = lambda rel, live: True  # noqa: E731

    assert _unpinned_owned_paths(["kept.py"], {}, tmp_path, superseded=always) == []
    assert _unpinned_owned_paths(["gone.py"], {}, tmp_path, superseded=always) == ["gone.py"]
    assert _unpinned_owned_paths(["gone/"], {}, tmp_path, superseded=always) == ["gone/"]
    # negative control: without the rule the existing file is still unpinned
    assert _unpinned_owned_paths(["kept.py"], {}, tmp_path) == ["kept.py"]
