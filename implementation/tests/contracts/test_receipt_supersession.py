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


def test_the_verifier_files_are_recorded_not_pinned():
    """A receipt that pinned contracts/receipts.py or the verify tool at an older digest
    must not fail identity when the checker is hardened later (its tests validate it);
    any other code file at a stale digest with no successor still fails."""
    from trading_research.research.contracts import receipts as r
    stale = "0" * 64
    failures: list[CheckFailure] = []
    _check_declared_source_files(
        {path: stale for path in sorted(r.VERIFIER_FILES)}, failures, "CODE_SNAPSHOT.json", kind="code"
    )
    assert failures == []
    native = "implementation/src/trading_research/research/rule_discovery/native.py"
    failures = []
    _check_declared_source_files({native: stale, next(iter(r.VERIFIER_FILES)): stale}, failures, "CODE_SNAPSHOT.json", kind="code")
    assert [(f.code, native in f.detail) for f in failures] == [("IDENTITY", True)]


# --------------------------------------------------------------------------
# Rule 4: a stale code pin is superseded by any later receipt that verifies on
# its own, pins the live digest and lists this receipt as a predecessor; the
# search must not depend on the order in which candidates are tried, nor on a
# failure recorded while another candidate was being verified.
# --------------------------------------------------------------------------

import json

from trading_research.research.contracts import receipts as rec
from trading_research.research.contracts.identity import digest
from tests.rule_discovery.test_p15_01 import (
    ASSURANCE_VERSION,
    _rebind_draft,
    _refresh_named,
    _stale_code,
    bound_graph_tasks,
    write_bound_task,
    write_graph,
)


def _pin_code(receipt: Path, rel: str, payload: bytes | None) -> str:
    """Add a second code pin to a receipt's CODE_SNAPSHOT: the live bytes, or
    a historical payload that no longer matches the workspace."""
    code_path = receipt.parent / "CODE_SNAPSHOT.json"
    code = json.loads(code_path.read_text())
    copy = receipt.parent / "snapshots/code" / rel
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_bytes((DEFAULT_ROOT / rel).read_bytes() if payload is None else payload)
    pinned = file_digest(copy)
    code["files"][rel] = pinned
    code["snapshot_paths"][rel] = f"snapshots/code/{rel}"
    code_path.write_text(json.dumps(code, indent=2) + "\n")
    _refresh_named(receipt, "CODE_SNAPSHOT.json")
    _rebind_draft(receipt, code_sha256=digest(code))
    return pinned


def _three_task_graph(tmp_path: Path) -> Path:
    tasks = bound_graph_tasks()
    third = {k: v for k, v in tasks[1].items() if k != "id"}
    third["dependencies"] = ["P15-00", "P15-01"]
    tasks.append({"id": "P15-02", **third})
    return write_graph(
        tmp_path / "graph.json",
        tasks,
        required_task_artifacts=[
            "DRAFT_MANIFEST.json", "PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json",
            "EVIDENCE_MATRIX.json", "WORK_LOG.md", "DECISIONS.tsv", "REPORT.md",
        ],
        assurance_version=ASSURANCE_VERSION,
    )


def test_supersession_is_granted_through_the_newest_verified_successor(tmp_path):
    """A (oldest) pins file 1 stale. B pins file 1 live but pins file 2 stale.
    C pins both live and lists A and B. Only C verifies on its own; B verifies
    only because C supersedes its file-2 pin. A must verify: C is a verified
    later receipt that pins A's stale file live and lists A. The old search
    tried B first, recorded B's failure in a context-free cache while C was
    still on the visiting stack, and then rejected C because of that record."""
    graph = _three_task_graph(tmp_path)
    second_rel = "implementation/src/trading_research/research/contracts/identity.py"
    a = write_bound_task(tmp_path, "P15-00")
    rel, old, live = _stale_code(a)
    assert old != live
    b = write_bound_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(a)})
    stale_second = _pin_code(b, second_rel, b"historical-identity-bytes\n")
    assert stale_second != file_digest(DEFAULT_ROOT / second_rel)
    c = write_bound_task(
        tmp_path, "P15-02",
        predecessors={"P15-00": file_digest(a), "P15-01": file_digest(b)},
    )
    _pin_code(c, second_rel, None)
    assert str(b) < str(c), "the failing candidate must sort before the verifying one"

    # positive: A verifies through C, whichever candidate the search meets first
    result = rec.verify_task_receipt(a, graph_path=graph, receipts_root=tmp_path)
    assert result.ok, result.failures
    # and B, whose own stale pin is superseded by C, verifies as well
    assert rec.verify_task_receipt(b, graph_path=graph, receipts_root=tmp_path).ok

    # negative control: once C no longer verifies, neither B nor A is excused
    (c.parent / "REPORT.md").write_text("tampered\n")
    broken_b = rec.verify_task_receipt(b, graph_path=graph, receipts_root=tmp_path)
    assert not broken_b.ok
    assert any(f.code == rec.FailureCode.IDENTITY and second_rel in f.detail for f in broken_b.failures)
    broken_a = rec.verify_task_receipt(a, graph_path=graph, receipts_root=tmp_path)
    assert not broken_a.ok
    assert any(f.code == rec.FailureCode.IDENTITY and rel in f.detail for f in broken_a.failures)


# --------------------------------------------------------------------------
# The successor guard: a candidate already being verified higher up the stack
# is decided by that frame, not reported as a cycle against the receipt under
# verification (2026-09-17).
# --------------------------------------------------------------------------


def _state(tmp_path):
    from trading_research.research.contracts.receipts import _VerifyState

    return _VerifyState(receipts_root=tmp_path, graph=None, amendments_path=tmp_path / "AMENDMENTS.json")


def test_a_candidate_on_the_stack_is_assumed_to_hold_and_left_to_its_own_frame(tmp_path, monkeypatch):
    """A re-issued successor that pins a predecessor's drifted file must verify
    its own predecessors, and one of them is that predecessor. Concluding "does
    not verify" for the candidate already on the stack would report a cycle
    against a receipt that has no defect."""
    from trading_research.research.contracts import receipts as R

    state = _state(tmp_path)
    candidate = tmp_path / "SUCCESSOR.json"
    candidate.write_text("{}")

    calls = []

    def fake_verify(path, **kwargs):
        calls.append(str(path))
        # while this candidate is in progress, ask again for the same one
        assert state.successor_verifies(candidate) is True
        return R.VerificationResult("task", True, str(path), ())

    monkeypatch.setattr(R, "verify_task_receipt", fake_verify)
    assert state.successor_verifies(candidate) is True
    assert calls == [str(candidate)]  # the re-entrant ask did not verify again

    # negative control: a candidate that is NOT on the stack is decided on its
    # own result, so a failing successor still refuses the supersession
    state2 = _state(tmp_path)
    other = tmp_path / "FAILING.json"
    other.write_text("{}")

    def failing_verify(path, **kwargs):
        return R.VerificationResult(
            "task", False, str(path), (R.CheckFailure(R.FailureCode.IDENTITY, str(path), "bad"),)
        )

    monkeypatch.setattr(R, "verify_task_receipt", failing_verify)
    assert state2.successor_verifies(other) is False
    # and the refusal is not memoized as an assumption: asking again re-verifies
    assert state2.successor_verifies(other) is False


def test_the_guard_does_not_memoize_a_result_reached_under_the_assumption(tmp_path, monkeypatch):
    """A negative outcome reached while the guard fired may be an artefact of the
    recursion, so it must not be cached as a fact about the receipt."""
    from trading_research.research.contracts import receipts as R

    state = _state(tmp_path)
    inner = tmp_path / "INNER.json"
    outer = tmp_path / "OUTER.json"
    for path in (inner, outer):
        path.write_text("{}")

    def verify(path, **kwargs):
        if str(path) == str(outer):
            # the outer verification leans on the inner one, which is on the stack
            state.successor_verifies(outer)
            return R.VerificationResult(
                "task", False, str(path), (R.CheckFailure(R.FailureCode.IDENTITY, str(path), "x"),)
            )
        return R.VerificationResult("task", True, str(path), ())

    monkeypatch.setattr(R, "verify_task_receipt", verify)
    assert state.successor_verifies(outer) is False
    assert str(outer) not in state._successors["ok"]
    # a clean candidate, verified with no guard hit, is memoized
    assert state.successor_verifies(inner) is True
    assert state._successors["ok"][str(inner)] is True
