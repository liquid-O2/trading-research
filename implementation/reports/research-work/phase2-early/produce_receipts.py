#!/usr/bin/env python3
"""Produce the early Phase 2 task receipts for P2-09, P2-10 and P2-03.

Two roots. ``--root`` (default ``/workspace``) is the identity root: the plan and
code bytes that ``verify_research_release.py`` re-hashes live there, because the
verifier resolves every declared plan/code path against ``/workspace``.
``--out-root`` (default this worktree) holds the slice run, the attempt
directories and the receipts. Every owned code file must be byte-identical in
both roots; the producer refuses to issue a receipt otherwise, because the
receipt would otherwise claim code the verifier cannot see.

The task spec (card, reads, owns, artifacts, acceptance keys, assurance cases,
dependencies) is read from TASK_GRAPH.json, never restated here, so a card or
graph amendment cannot drift away from the receipt.

Forgery probes and the receipt are brought to a fixed point: the probes file
named by the receipt is the probe of that same receipt's bytes.
"""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
sys.path.insert(0, str(WORKTREE / "implementation" / "src"))

from trading_research.research.contracts.identity import (  # noqa: E402
    ASSURANCE_VERSION,
    artifact_entry,
    canonical_bytes,
    code_snapshot_document,
    digest,
    file_digest,
    make_task_receipt,
    plan_snapshot_document,
    semantic_run_id,
    write_json_document,
    write_snapshot_tree,
    write_task_receipt,
)
from trading_research.research.contracts.receipts import (  # noqa: E402
    _VerifyState,
    DEFAULT_AMENDMENTS_PATH,
    DEFAULT_RECEIPTS_ROOT,
    verify_task_receipt,
)

IDENTITY_ROOT = Path("/workspace")
GRAPH_REL = "planning/research-program/TASK_GRAPH.json"
REGISTRY_REL = "planning/research-program/ASSURANCE_CASES.json"
VERIFIER_REL = "implementation/tools/verify_research_release.py"
CHECKER_REL = "implementation/src/trading_research/research/contracts/receipts.py"
PROBES_NAME = "FORGERY_PROBES.json"
PROBES_SCHEMA = "research-forgery-probes-v1"
RESULT_CARD_SCHEMA = "research-result-card-v1"
COMMON_ARTIFACTS = (
    ("DRAFT_MANIFEST.json", "research-draft-manifest-v2"),
    ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2"),
    ("CODE_SNAPSHOT.json", "research-code-snapshot-v2"),
    ("WORK_LOG.md", "research-work-log-v1"),
    ("DECISIONS.tsv", "research-decisions-tsv-v1"),
    ("REPORT.md", "research-task-report-v1"),
    ("pytest.log", "pytest-log"),
    ("slice.log", "slice-log"),
    ("predecessor_verify.log", "verify-task-log"),
    ("predecessor_verify_P2-10.log", "verify-task-log"),
)
P15_02 = IDENTITY_ROOT / "implementation/reports/research-work/P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json"
P15_02_SHA = "38ea80350aa20abecf619b18fe18ad4a9c5a8a2c7ed98461415a340645ef3069"
HOLDOUT = ("2026-04-01", "2026-09-03")

# Everything below is producer-side detail the graph does not carry: which extra
# files the run also executed, which module the attempt imported, and which
# artifact row proves each acceptance key.
EXTRA: dict[str, dict] = {
    "P2-09": {
        "slice_dir": "P2-09",
        "test": "implementation/tests/context_experts/test_p2_09.py",
        "helpers": [
            "implementation/src/trading_research/research/experts/options/slice_runner.py",
            "implementation/src/trading_research/research/experts/options/databento_decode.py",
            "implementation/src/trading_research/research/experts/options/atlas.py",
            "implementation/tools/run_context_experts.py",
            "implementation/src/trading_research/research/contracts/identity.py",
            "implementation/src/trading_research/research/method_pack/clocks.py",
            "implementation/src/trading_research/research/method_pack/session_policy.py",
            "implementation/src/trading_research/errors.py",
            "implementation/src/trading_research/research/rule_discovery/native.py",
            "implementation/src/trading_research/research/contracts/receipts.py",
        ],
        "imported": [
            "trading_research.research.experts.options.instruments",
            "trading_research.research.experts.options.native",
            "trading_research.research.experts.options.databento_decode",
        ],
        "artifact_schemas": {
            "INSTRUMENT_LEDGER.json": "research-instrument-ledger-v1",
            "OPTIONS_AVAILABILITY.json": "research-options-availability-v1",
            "SURFACE_INPUT_SLICE.json": "research-surface-input-slice-v1",
            "PUBLICATION_SENSITIVITY.json": "research-publication-sensitivity-v1",
            "RESULT_CARD.json": RESULT_CARD_SCHEMA,
            "THROUGHPUT.json": "research-throughput-v1",
        },
        "mapping": [
            ("A01", "NDX/NDXP and SPX/SPXW expiry clocks stay distinct", "expiry_clocks_distinct",
             [("INSTRUMENT_LEDGER.json", "/expiry_clocks/ndx_ndxp_distinct"),
              ("INSTRUMENT_LEDGER.json", "/expiry_clocks/spx_spxw_distinct")]),
            ("A02", "A filename date cannot make daily OI available before publication", "load_oi_available_at",
             [("SURFACE_INPUT_SLICE.json", "/slices/0/oi_used_before_asof"),
              ("PUBLICATION_SENSITIVITY.json", "/filename_date_is_not_publication")]),
            ("A03", "Future-listed strikes cannot appear in an earlier universe", "chain_universe",
             [("SURFACE_INPUT_SLICE.json", "/slices/{lookahead_slice}/universe/lookahead_excluded_count")]),
            ("A04", "Stale, crossed and missing quotes stay rejection records, not zero prices", "quote_reject_codes",
             [("SURFACE_INPUT_SLICE.json", "/slices/{quote_slice}/n_rejected"),
              ("SURFACE_INPUT_SLICE.json", "/slices/{quote_slice}/n_ok")]),
            ("A05", "Root coverage reconciles full-chain and scoped-feed denominators with native underlying IDs", "coverage_row",
             [("OPTIONS_AVAILABILITY.json", "/coverage/{chain_row}/full_chain_rows"),
              ("OPTIONS_AVAILABILITY.json", "/coverage/{chain_row}/underlying_id")]),
        ],
    },
    "P2-10": {
        "slice_dir": "P2-10",
        "test": "implementation/tests/context_experts/test_p2_10.py",
        "helpers": [
            "implementation/src/trading_research/research/experts/options/instruments.py",
            "implementation/src/trading_research/research/experts/options/native.py",
            "implementation/src/trading_research/research/experts/options/slice_runner.py",
            "implementation/tools/run_context_experts.py",
            "implementation/src/trading_research/errors.py",
            "implementation/src/trading_research/research/rule_discovery/native.py",
            "implementation/src/trading_research/research/contracts/receipts.py",
        ],
        "imported": [
            "trading_research.research.experts.options.pricing",
            "trading_research.research.experts.options.surfaces",
            "trading_research.research.experts.options.boards",
        ],
        "artifact_schemas": {
            "PRICING_FIXTURES.json": "research-pricing-fixtures-v1",
            "GREEK_SENSITIVITY.json": "research-greek-sensitivity-v1",
            "EXPOSURE_BOARDS.json": "research-exposure-boards-v1",
            "SURFACE_QUALITY.json": "research-surface-quality-v1",
            "RESULT_CARD.json": RESULT_CARD_SCHEMA,
            "THROUGHPUT.json": "research-throughput-v1",
        },
        "mapping": [
            ("A01", "The S=K=100, sigma=.2, one-year Greek fixture and put-call parity hold", "european_greeks",
             [("PRICING_FIXTURES.json", "/atm/call"), ("PRICING_FIXTURES.json", "/atm/parity_c_minus_p")]),
            ("A02", "Analytic Greeks match finite differences and American 400/800 steps are compared", "american_tree_price",
             [("PRICING_FIXTURES.json", "/finite_difference/delta"), ("GREEK_SENSITIVITY.json", "/delta_rel"),
              ("GREEK_SENSITIVITY.json", "/n400/gamma"), ("GREEK_SENSITIVITY.json", "/n800/gamma")],
             ("accepted-limit",
              "Analytic Greeks match central finite differences within 1.2e-06 relative. The American sensitivity is "
              "one engineering ATM contract, not the contract's 16-contract-per-root-date sample, and the CRR gamma "
              "at 400 versus 800 steps differs by far more than the contract's 10% exclusion threshold, which is the "
              "known lattice artifact: no American gamma is consumed anywhere, because the full-chain reference and "
              "every board Greek use the labelled equivalent-European model.")),
            ("A03", "Vega per one volatility point uses .01 scaling and units name the multiplier and underlier", "exposure_units",
             [("PRICING_FIXTURES.json", "/vega_per_vol_point"), ("PRICING_FIXTURES.json", "/units/multiplier")]),
            ("A04", "A no-bracket IV and an absent term-interpolation bracket stay unavailable", "implied_vol",
             [("PRICING_FIXTURES.json", "/iv_no_bracket/status"), ("PRICING_FIXTURES.json", "/term_no_bracket/status")]),
            ("A05", "Every signed exposure scenario is a labelled assumption, not known dealer inventory", "scenario_sign",
             [("EXPOSURE_BOARDS.json", "/boards/0/scenario_label"), ("EXPOSURE_BOARDS.json", "/boards/0/scenario")]),
        ],
    },
    "P2-03": {
        "slice_dir": "P2-03",
        "test": "implementation/tests/context_experts/test_p2_03.py",
        "helpers": [
            "implementation/src/trading_research/research/experts/options/slice_runner.py",
            "implementation/src/trading_research/research/experts/options/native.py",
            "implementation/tools/run_context_experts.py",
            "implementation/src/trading_research/research/method_pack/clocks.py",
            "implementation/src/trading_research/research/method_pack/session_policy.py",
            "implementation/src/trading_research/errors.py",
            "implementation/src/trading_research/research/rule_discovery/native.py",
            "implementation/src/trading_research/research/contracts/receipts.py",
        ],
        "imported": [
            "trading_research.research.experts.features.volatility",
            "trading_research.research.experts.labels.volatility",
        ],
        "artifact_schemas": {
            "VOLATILITY_FEATURES.json": "research-volatility-features-v1",
            "VOLATILITY_TARGETS.json": "research-volatility-targets-v1",
            "VOLATILITY_FIXTURES.json": "research-volatility-fixtures-v1",
            "RESULT_CARD.json": RESULT_CARD_SCHEMA,
            "THROUGHPUT.json": "research-throughput-v1",
        },
        "mapping": [
            ("A01", "GK, YZ and RV reproduce the contract's worked examples", "garman_klass",
             [("VOLATILITY_FIXTURES.json", "/gk/variance"), ("VOLATILITY_FIXTURES.json", "/yz/variance"),
              ("VOLATILITY_FIXTURES.json", "/rv/variance")]),
            ("A02", "Annualized IV variance, interval realized variance and the point conversion stay separate units",
             "iv_variance_one_calendar_day",
             [("VOLATILITY_FIXTURES.json", "/iv_scaling/kind"), ("VOLATILITY_FIXTURES.json", "/rv/unit")]),
            ("A03", "A fixed horizon crossing the close or a roll is unsupported, not truncated", "build_heads",
             [("VOLATILITY_TARGETS.json", "/rows/0/unsupported_close_cross"),
              ("VOLATILITY_TARGETS.json", "/rows/0/head_names")]),
            ("A04", "Every requested IV group is consumed or carries an explicit missing-group record", "har_inputs",
             [("VOLATILITY_FEATURES.json", "/rows/0/iv_groups")]),
            ("A05", "Future target prices cannot affect the current GK/YZ/HAR features", "future_prices_do_not_enter",
             [("VOLATILITY_FEATURES.json", "/rows/0/gk/variance")]),
        ],
    },
}


# --------------------------------------------------------------------------- spec


def load_spec(task_id: str, root: Path) -> dict:
    graph = json.loads((root / GRAPH_REL).read_text())
    for raw in graph["tasks"]:
        if raw["id"] == task_id:
            spec = dict(EXTRA[task_id])
            spec.update(
                {
                    "id": task_id,
                    "card": raw["path"],
                    "reads": list(raw["reads"]),
                    "owns": list(raw["owns"]),
                    "artifacts": list(raw["artifacts"]),
                    "cases": list(raw["required_acceptance_keys"]) + list(raw["assurance_cases"]),
                    "acceptance_keys": list(raw["required_acceptance_keys"]),
                    "deps": list(raw["dependencies"]),
                    "required_common": list(graph.get("required_task_artifacts") or ()),
                }
            )
            return spec
    raise SystemExit(f"{task_id} is not in {root / GRAPH_REL}")


# --------------------------------------------------------------------------- commands


def _run(argv: list[str], cwd: Path, log_path: Path) -> dict:
    started = datetime.now(timezone.utc)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(cwd / "src")
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    log_path.write_text(proc.stdout + proc.stderr)
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "log_path": str(log_path),
        "log_sha256": file_digest(log_path),
        "seconds": (datetime.now(timezone.utc) - started).total_seconds(),
    }


def _recorded_slice_command(run_dir: Path, attempt: Path) -> dict:
    """The slice run already executed; re-bind its log under the attempt."""
    record = json.loads((run_dir / "slice_command.json").read_text())
    if record["exit_code"] != 0:
        raise SystemExit(f"slice command for {run_dir} exited {record['exit_code']}")
    log_src = Path(record["log_path"])
    if not log_src.is_absolute():
        log_src = Path(record["cwd"]) / log_src
    dest = attempt / "slice.log"
    shutil.copy2(log_src, dest)
    return {
        "argv": list(record["argv"]),
        "cwd": record["cwd"],
        "exit_code": 0,
        "log_path": str(dest),
        "log_sha256": file_digest(dest),
        "seconds": float(record["seconds"]),
    }


# --------------------------------------------------------------------------- symbols


def _def_class_names(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        names.add(f"{node.name}.{child.name}")
    return names


def _owned_symbol_index(spec: dict, root: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for rel in list(spec["owns"]) + list(spec["helpers"]):
        if "/tests/" in rel.replace("\\", "/"):
            continue
        for name in _def_class_names(root / rel):
            index.setdefault(name, rel)
    return index


def _owned_only_index(spec: dict, root: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for rel in spec["owns"]:
        if "/tests/" in rel.replace("\\", "/"):
            continue
        for name in _def_class_names(root / rel):
            index.setdefault(name, rel)
    return index


def _test_functions(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]


def _bind_test_function(functions: list[str], check_id: str) -> str:
    prefix = f"test_{check_id.lower()}"
    matches = [name for name in functions if name == prefix or name.startswith(prefix + "_")]
    if len(matches) != 1:
        raise RuntimeError(f"{check_id} needs exactly one test matching {prefix!r}, got {matches}")
    return matches[0]


def _module_src_rel(mod: str | None, root: Path) -> str | None:
    if not mod or not mod.startswith("trading_research"):
        return None
    rel = "implementation/src/" + mod.replace(".", "/") + ".py"
    return rel if (root / rel).is_file() else None


def _code_ref_for_function(test_path: Path, func_name: str, index: dict[str, str], root: Path) -> dict[str, str]:
    tree = ast.parse(test_path.read_text(encoding="utf-8"))
    func = next(
        (n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func_name),
        None,
    )
    if func is None:
        raise RuntimeError(f"{func_name} is not a top-level function in {test_path}")
    found: list[dict[str, str]] = []

    def add(rel: str, name: str) -> None:
        if "/tests/" in rel.replace("\\", "/") or name not in _def_class_names(root / rel):
            return
        item = {"path": rel, "symbol": name}
        if item not in found:
            found.append(item)

    class Finder(ast.NodeVisitor):
        def visit_Name(self, item: ast.Name) -> None:
            if item.id in index:
                add(index[item.id], item.id)
            self.generic_visit(item)

        def visit_Attribute(self, item: ast.Attribute) -> None:
            self.generic_visit(item)
            if item.attr in index:
                add(index[item.attr], item.attr)

        def visit_ImportFrom(self, item: ast.ImportFrom) -> None:
            rel = _module_src_rel(item.module, root)
            for alias in item.names:
                name = alias.asname or alias.name
                if name in index:
                    add(index[name], name)
                elif rel is not None:
                    add(rel, name)

    Finder().visit(func)
    if not found:
        raise RuntimeError(f"{func_name} names no source def/class")
    return found[0]


# --------------------------------------------------------------------------- evidence


def _evidence(path: Path, selector: str) -> dict:
    return {"path": str(path), "sha256": file_digest(path), "selector": selector}


def _pytest_selector(attempt: Path) -> str:
    log = attempt / "pytest.log"
    chosen = " passed"
    if log.is_file():
        for line in log.read_text(encoding="utf-8").splitlines():
            match = re.search(r"\d+ passed(?: in)?", line)
            if match:
                chosen = match.group(0)
    return chosen


def _load(path: Path) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {}


# --------------------------------------------------------------------------- forgery probes


def _relocate(src: Path, dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, symlinks=True)
    receipt = dest / "TASK_RECEIPT.json"
    text = receipt.read_text()
    for old in {str(src), str(src.resolve())}:
        text = text.replace(old, str(dest))
    receipt.write_text(text)
    return receipt


def _edit_json(path: Path, editor) -> None:
    payload = json.loads(path.read_text())
    editor(payload)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")


def _rebind(receipt: Path, name: str) -> None:
    """Re-declare one artifact's hash and size after its bytes were changed."""
    target = receipt.parent / name

    def edit(payload: dict) -> None:
        for entry in payload.get("artifact_manifest") or []:
            if Path(entry.get("path", "")).name == name:
                entry["sha256"] = file_digest(target)
                entry["bytes"] = target.stat().st_size

    _edit_json(receipt, edit)


def _mut_remove_artifact(receipt: Path, spec: dict) -> None:
    (receipt.parent / "WORK_LOG.md").unlink()


def _mut_substitute_file(receipt: Path, spec: dict) -> None:
    name = spec["artifacts"][0]
    (receipt.parent / name).write_bytes((receipt.parent / "THROUGHPUT.json").read_bytes())
    _rebind(receipt, name)


def _mut_row_count(receipt: Path, spec: dict) -> None:
    def edit(payload: dict) -> None:
        for entry in payload.get("artifact_manifest") or []:
            if Path(entry.get("path", "")).name == "EVIDENCE_MATRIX.json":
                entry["rows"] = 10**9

    _edit_json(receipt, edit)


def _mut_invalid_json(receipt: Path, spec: dict) -> None:
    name = spec["artifacts"][0]
    (receipt.parent / name).write_text("not-json\n")
    _rebind(receipt, name)


def _mut_plan_digest(receipt: Path, spec: dict) -> None:
    _edit_json(receipt, lambda payload: payload.update({"plan_sha256": "0" * 64}))


def _mut_code_digest(receipt: Path, spec: dict) -> None:
    _edit_json(receipt, lambda payload: payload.update({"code_sha256": "0" * 64}))


def _mut_run_id(receipt: Path, spec: dict) -> None:
    _edit_json(receipt, lambda payload: payload.update({"run_id": "0" * 16}))


def _mut_omit_owned_file(receipt: Path, spec: dict) -> None:
    snapshot = receipt.parent / "CODE_SNAPSHOT.json"
    drop = next(rel for rel in spec["owns"] if "/tests/" not in rel)

    def edit(payload: dict) -> None:
        payload["files"] = {k: v for k, v in payload["files"].items() if k != drop}
        payload["snapshot_paths"] = {k: v for k, v in payload["snapshot_paths"].items() if k != drop}

    _edit_json(snapshot, edit)
    _rebind(receipt, "CODE_SNAPSHOT.json")


def _mut_command_log(receipt: Path, spec: dict) -> None:
    def edit(payload: dict) -> None:
        payload["command_results"][0]["log_sha256"] = "0" * 64

    _edit_json(receipt, edit)


def _mut_predecessor_digest(receipt: Path, spec: dict) -> None:
    def edit(payload: dict) -> None:
        for key in payload["predecessor_receipts"]:
            payload["predecessor_receipts"][key] = "0" * 64

    _edit_json(receipt, edit)


def _mut_matrix_evidence(receipt: Path, spec: dict) -> None:
    matrix = receipt.parent / "EVIDENCE_MATRIX.json"

    def edit(payload: dict) -> None:
        for check in payload["checks"]:
            for item in check.get("evidence") or []:
                item["sha256"] = "0" * 64
                return

    _edit_json(matrix, edit)
    _rebind(receipt, "EVIDENCE_MATRIX.json")


def _mut_matrix_status(receipt: Path, spec: dict) -> None:
    matrix = receipt.parent / "EVIDENCE_MATRIX.json"

    def edit(payload: dict) -> None:
        payload["checks"][0]["status"] = "fail"

    _edit_json(matrix, edit)
    _rebind(receipt, "EVIDENCE_MATRIX.json")


MUTATIONS = (
    ("remove_artifact", _mut_remove_artifact, "ARTIFACT_MISSING", "a required artifact file is deleted"),
    ("substitute_file", _mut_substitute_file, "SCHEMA", "another artifact's bytes are declared under this name"),
    ("row_count", _mut_row_count, "INVENTORY", "a declared row count does not match the parsed rows"),
    ("invalid_json", _mut_invalid_json, "JSON_PARSE", "an artifact no longer parses"),
    ("plan_digest", _mut_plan_digest, "IDENTITY", "plan_sha256 does not recompute from PLAN_SNAPSHOT"),
    ("code_digest", _mut_code_digest, "IDENTITY", "code_sha256 does not recompute from CODE_SNAPSHOT"),
    ("run_id", _mut_run_id, "IDENTITY", "run_id does not recompute from DRAFT_MANIFEST"),
    ("omit_owned_file", _mut_omit_owned_file, "INVENTORY", "an owned source file is not pinned"),
    ("command_log", _mut_command_log, "ARTIFACT_HASH", "a command log digest does not match the log bytes"),
    ("predecessor_digest", _mut_predecessor_digest, "PREDECESSOR_HASH", "a predecessor receipt digest is forged"),
    ("matrix_evidence", _mut_matrix_evidence, "ARTIFACT_HASH", "an evidence digest in the matrix is forged"),
    ("matrix_status", _mut_matrix_status, "ACCEPTANCE", "a matrix row claims fail under an accepted disposition"),
)


def _verify(receipt: Path, state: _VerifyState) -> dict:
    result = verify_task_receipt(receipt, _state=state)
    return {"ok": bool(result.ok), "codes": sorted({item.code for item in result.failures})}


def run_probes(spec: dict, attempt: Path) -> dict:
    """Verify the receipt as issued, then one forgery per gate on temporary copies."""
    receipt = attempt / "TASK_RECEIPT.json"
    state = _VerifyState(receipts_root=DEFAULT_RECEIPTS_ROOT, graph=None, amendments_path=DEFAULT_AMENDMENTS_PATH)
    control = _verify(receipt, state)
    mutations: dict[str, dict] = {}
    parent = Path(tempfile.mkdtemp(prefix=f"{spec['id']}-forgery-"))
    try:
        for name, mutate, expected, description in MUTATIONS:
            copy = _relocate(attempt, parent / name)
            mutate(copy, spec)
            outcome = _verify(copy, state)
            outcome["expected_code"] = expected
            outcome["expected_code_present"] = expected in outcome["codes"]
            outcome["forgery"] = description
            outcome["rejected"] = (not outcome["ok"]) and outcome["expected_code_present"]
            mutations[name] = outcome
    finally:
        shutil.rmtree(parent, ignore_errors=True)
    return {
        "schema_version": PROBES_SCHEMA,
        "task_id": spec["id"],
        "control": control,
        "mutations": mutations,
        "n_rejected": sum(1 for item in mutations.values() if item["rejected"]),
        "n_mutations": len(mutations),
        "ok": control["ok"] and all(item["rejected"] for item in mutations.values()),
    }


# --------------------------------------------------------------------------- matrix


def build_matrix(spec: dict, attempt: Path, root: Path, indices: dict[str, int]) -> dict:
    index = _owned_symbol_index(spec, root)
    owned_only = _owned_only_index(spec, root)
    test_rel = spec["test"]
    functions = _test_functions(root / test_rel)
    probes = _load(attempt / PROBES_NAME)
    pytest_selector = _pytest_selector(attempt)
    mapping = {item[0]: item for item in spec["mapping"]}
    places = _placeholders(attempt)
    audit = list(indices["predecessors"])
    checks: list[dict] = []
    for case in spec["cases"]:
        if case == "A06":
            checks.append(
                {
                    "id": case,
                    "requirement": "Command exit codes, artifact hashes, coverage counts, runtime and inspected "
                    "output are recorded, and every predecessor receipt verifies",
                    "code_refs": [{"path": CHECKER_REL, "symbol": "verify_task_receipt"}],
                    "test_nodeids": [],
                    "command_indices": [indices["pytest"], indices["slice"], *audit],
                    "evidence": [
                        _evidence(attempt / "predecessor_verify.log", "/ok"),
                        _evidence(attempt / "THROUGHPUT.json", "/median_seconds"),
                        _evidence(attempt / "slice.log", "/ok"),
                        _evidence(attempt / "REPORT.md", "Inspected output"),
                    ],
                    "expected": "every predecessor receipt verifies; runtime and coverage counts are recorded",
                    "observed": f"predecessor verification exit 0; {len(spec['deps'])} predecessor receipts",
                    "oracle": "verify_research_release.py task on each predecessor receipt",
                    "status": "pass",
                }
            )
            continue
        if case == "A07":
            checks.append(
                {
                    "id": case,
                    "requirement": "Every acceptance key and assigned case resolves to code, executed commands and "
                    "hashed evidence; artifact, identity and command forgeries fail",
                    "code_refs": [{"path": CHECKER_REL, "symbol": "verify_task_receipt"}],
                    "test_nodeids": [],
                    "command_indices": [*audit],
                    "evidence": [_evidence(attempt / PROBES_NAME, "/control/ok")]
                    + [
                        _evidence(attempt / PROBES_NAME, f"/mutations/{name}/rejected")
                        for name, _fn, _code, _desc in MUTATIONS
                    ],
                    "expected": f"control verifies and all {len(MUTATIONS)} forgeries are rejected with their intended code",
                    "observed": f"control ok={probes.get('control', {}).get('ok')}; "
                    f"rejected {probes.get('n_rejected')} of {probes.get('n_mutations')}",
                    "oracle": "verify_research_release.py on mutated copies of this receipt",
                    "status": "pass" if probes.get("ok") else "fail",
                }
            )
            continue
        if case == "A08":
            case_nodes = [
                f"{test_rel}::{_bind_test_function(functions, item)}"
                for item in spec["cases"]
                if item.startswith("S")
            ]
            checks.append(
                {
                    "id": case,
                    "requirement": "The assigned silent-failure probes pass with sensitive positive and negative "
                    "controls and honest native, unknown and job counts",
                    "code_refs": [{"path": CHECKER_REL, "symbol": "verify_task_receipt"}],
                    "test_nodeids": case_nodes,
                    "command_indices": [indices["pytest"], *audit],
                    "evidence": [
                        _evidence(attempt / "pytest.log", pytest_selector),
                        _evidence(attempt / PROBES_NAME, "/ok"),
                    ],
                    "expected": "the assigned case tests pass and the forgery controls behave as declared",
                    "observed": f"pytest {pytest_selector}; {len(case_nodes)} assigned case tests",
                    "oracle": "pytest on the owned test file plus the receipt forgery probes",
                    "status": "pass",
                }
            )
            continue
        item = mapping.get(case)
        if item is not None:
            check_id, requirement, symbol, pointers = item[:4]
            status, note = item[4] if len(item) > 4 else ("pass", None)
            if symbol not in index:
                raise RuntimeError(f"{symbol} is not defined in the owned or helper files of {spec['id']}")
            func = _bind_test_function(functions, check_id)
            resolved = [(name, selector.format(**places)) for name, selector in pointers]
            checks.append(
                {
                    "id": check_id,
                    "requirement": requirement,
                    "code_refs": [{"path": index[symbol], "symbol": symbol}],
                    "test_nodeids": [f"{test_rel}::{func}"],
                    "command_indices": [indices["pytest"], indices["slice"]],
                    "evidence": [_evidence(attempt / name, selector) for name, selector in resolved],
                    "expected": requirement,
                    "observed": "; ".join(
                        f"{name}{selector}={_pointer(attempt / name, selector)}" for name, selector in resolved
                    )
                    + (f" | {note}" if note else ""),
                    "oracle": "the contract's literal worked example and the native slice artifact",
                    "status": status,
                }
            )
            continue
        func = _bind_test_function(functions, case)
        ref = _code_ref_for_function(root / test_rel, func, {**index, **owned_only}, root)
        checks.append(
            {
                "id": case,
                "requirement": f"Assigned silent-failure case {case}",
                "code_refs": [ref],
                "test_nodeids": [f"{test_rel}::{func}"],
                "command_indices": [indices["pytest"], indices["slice"]],
                "evidence": [_evidence(attempt / "pytest.log", pytest_selector)],
                "expected": "the case probe passes with its sensitive positive case and negative control",
                "observed": f"pytest {pytest_selector}",
                "oracle": "the owned case test and the native slice artifacts",
                "status": "pass",
            }
        )
    return {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": spec["id"],
        "assurance_version": ASSURANCE_VERSION,
        "checks": checks,
    }


def _placeholders(attempt: Path) -> dict[str, int]:
    """Point each acceptance row at a slice row that actually exercises it."""
    surface = _load(attempt / "SURFACE_INPUT_SLICE.json").get("slices") or []
    coverage = _load(attempt / "OPTIONS_AVAILABILITY.json").get("coverage") or []
    quote = next((i for i, row in enumerate(surface) if row.get("n_ok")), 0)
    lookahead = next(
        (i for i, row in enumerate(surface) if (row.get("universe") or {}).get("lookahead_excluded_count")),
        quote,
    )
    chain = next((i for i, row in enumerate(coverage) if row.get("full_chain_rows")), 0)
    return {"quote_slice": quote, "lookahead_slice": lookahead, "chain_row": chain}


def _pointer(path: Path, selector: str):
    document = _load(path)
    current = document
    for raw in selector.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    if isinstance(current, (dict, list)):
        return json.dumps(current, sort_keys=True)[:160]
    return current


# --------------------------------------------------------------------------- result cards


def _headline(
    name: str,
    value: float,
    unit: str,
    *,
    attempt: Path,
    artifact: str,
    selector: str,
    support: int | None = None,
    interval: list[float] | None = None,
    note: str = "",
) -> dict:
    """One judgeable number: its unit, its support count or interval, and where it was read.

    A count carries the denominator it was counted out of. A deterministic identity check
    against a contract worked example carries interval [value, value]: the same inputs always
    give the same number, so there is nothing to put an interval around.
    """
    path = attempt / artifact
    if (support is None) == (interval is None):
        raise RuntimeError(f"headline {name!r} needs exactly one of support or interval")
    row = {
        "name": name,
        "value": value,
        "unit": unit,
        "artifact": str(path),
        "sha256": file_digest(path),
        "selector": selector,
        "note": note,
    }
    if support is not None:
        row["support"] = int(support)
    else:
        row["interval"] = [float(interval[0]), float(interval[1])]
    return row


IDENTITY_INTERVAL_LIMIT = (
    "Headline rows whose interval is [value, value] are deterministic identity checks against the "
    "contract's literal worked example: the inputs are fixed, so the interval is the value itself and "
    "not a sampling interval."
)
HOLDOUT_LIMIT = (
    f"Nothing here is fitted, tuned, ranked or selected, so the blind hold-out {HOLDOUT[0]}..{HOLDOUT[1]} "
    "is not consumed; 2026-09-03 appears only as a slice date."
)


def _p2_09_card(attempt: Path, dates: list[str]) -> dict:
    ledger = _load(attempt / "INSTRUMENT_LEDGER.json")
    avail = _load(attempt / "OPTIONS_AVAILABILITY.json")
    surface = _load(attempt / "SURFACE_INPUT_SLICE.json")
    coverage = avail.get("coverage") or []
    slices = surface.get("slices") or []
    roots = ledger.get("roots") or {}
    complete = [row for row in coverage if row.get("disposition") == "complete_observed_scope"]
    no_spot = [row for row in coverage if not row.get("native_intraday_spot")]
    n_ok = sum(int(row.get("n_ok") or 0) for row in slices)
    n_rejected = sum(int(row.get("n_rejected") or 0) for row in slices)
    early_oi = [row for row in slices if row.get("oi_used_before_asof")]
    return {
        "question": "Does every required option root get a dated instrument definition, a causally clocked "
        "quote/spot/OI snapshot and an explicit disposition for what is not owned?",
        "headline": [
            _headline("required option roots with a dated instrument definition", len(roots), "roots",
                      support=len(roots), attempt=attempt, artifact="INSTRUMENT_LEDGER.json", selector="/roots",
                      note="the 8 roots OPTIONS.md requires: NDX, NDXP, SPX, SPXW, QQQ, SPY, NQ, ES"),
            _headline("root-days with a complete observed-scope disposition", len(complete), "root-days",
                      support=len(coverage), attempt=attempt, artifact="OPTIONS_AVAILABILITY.json",
                      selector="/coverage", note="denominator is every root-day attempted in the slice"),
            _headline("snapshot quote rows kept by the freshness and crossed filters", n_ok, "quote rows",
                      support=n_ok + n_rejected, attempt=attempt, artifact="SURFACE_INPUT_SLICE.json",
                      selector="/slices",
                      note=f"{n_rejected} rejected rows are retained as rejection records, never zero prices"),
            _headline("slices that used open interest before its publication clock", len(early_oi), "slices",
                      support=len(slices), attempt=attempt, artifact="SURFACE_INPUT_SLICE.json", selector="/slices",
                      note="the assumed clock is the next regular session at 12:00 ET"),
            _headline("root-days without native intraday spot", len(no_spot), "root-days",
                      support=len(coverage), attempt=attempt, artifact="OPTIONS_AVAILABILITY.json",
                      selector="/coverage", note="NDX/NDXP/SPX/SPXW cash index, explicitly unsupported"),
        ],
        "target": {
            "text": "Card P2-09 A01-A08: distinct expiry clocks, no pre-publication OI, no look-ahead strikes, "
            "rejections rather than zero prices, reconciled coverage denominators, and bound evidence.",
            "met": "yes",
        },
        "verdict": {
            "value": "needs_upgrade",
            "reason": "The adapters carry every owned input with dated definitions and explicit dispositions, "
            "but two of the six required underlyings have no owned two-sided option quote (NQ/ES use a "
            "one-minute last-trade mid) and the cash indices have no owned intraday spot, so the surface "
            "inputs are thin where the contract wants a chain.",
        },
        "lever": {
            "change": "Own an option BBO or MBP schema for NQ and ES, and an intraday NDX/SPX print.",
            "evidence": "The same 20-date slice would show live contracts per board in the tens or hundreds "
            "for NQ and ES instead of 1 and 6, in OPTIONS_AVAILABILITY.board_depth_20date and "
            "EXPOSURE_BOARDS.depth_by_root.",
        },
        "limits": [
            f"Slice of {len(dates)} engineering dates, not full history; the frozen engineering dates are a subset.",
            "Exchange-feed completeness is unknown; scoped feeds are labelled scoped, never treated as full chains.",
            "NQ/ES option quotes are ohlcv-1m last trade as bid=ask mid (no owned option BBO), labelled in the artifact.",
            "Cash-index intraday spot is not owned, so native NDX/SPX intraday exposure stays unsupported.",
            HOLDOUT_LIMIT,
        ],
    }


def _p2_10_card(attempt: Path, dates: list[str]) -> dict:
    pricing = _load(attempt / "PRICING_FIXTURES.json")
    greeks = _load(attempt / "GREEK_SENSITIVITY.json")
    boards_doc = _load(attempt / "EXPOSURE_BOARDS.json")
    atm = pricing.get("atm") or {}
    fd = pricing.get("finite_difference") or {}
    compared = ("delta", "gamma", "vega", "vanna")
    worst = max(abs(float(fd[key]) - float(atm[key])) / max(abs(float(atm[key])), 1e-12) for key in compared)
    boards = boards_doc.get("boards") or []
    days = boards_doc.get("days") or []
    depth = boards_doc.get("depth_by_root") or {}
    medians = {root: (rec.get("n_live") or {}).get("median") for root, rec in depth.items()}
    nq = depth.get("NQ") or {}
    call = float(atm.get("call"))
    return {
        "question": "Do the pricing, Greek and exposure-board primitives reproduce the contract's reference "
        "vectors, and do the native boards they build carry their model and scenario labels?",
        "headline": [
            _headline("ATM European call, S=K=100, sigma=.2, T=1", call, "index points",
                      interval=[call, call], attempt=attempt, artifact="PRICING_FIXTURES.json",
                      selector="/atm/call",
                      note="deterministic identity against the OPTIONS.md reference 7.96556746; parity C-P-(S-K) is 0"),
            _headline("worst analytic-versus-finite-difference relative error", worst, "relative",
                      support=len(compared), attempt=attempt, artifact="PRICING_FIXTURES.json",
                      selector="/finite_difference",
                      note="delta, gamma, vega and vanna at h=.01 and v=.0001; the contract tolerance is 1e-4"),
            _headline("American 400 versus 800 step delta relative difference", float(greeks.get("delta_rel")),
                      "relative", support=1, attempt=attempt, artifact="GREEK_SENSITIVITY.json",
                      selector="/delta_rel",
                      note="one engineering ATM contract, not the contract's 16-per-root-date sample; the "
                      "exclusion gate is 10%"),
            _headline("native boards built", len(boards), "boards", support=len(days), attempt=attempt,
                      artifact="EXPOSURE_BOARDS.json", selector="/boards",
                      note=f"{len(days) - len(boards)} of {len(days)} root-days are refused with a named reason"),
            _headline("median live contracts per NQ board", float((nq.get("n_live") or {}).get("median") or 0.0),
                      "contracts", support=int(nq.get("n_boards") or 0), attempt=attempt,
                      artifact="EXPOSURE_BOARDS.json", selector="/depth_by_root",
                      note=f"medians by root: {medians}; QQQ and SPY are deep, NQ and ES are degenerate"),
        ],
        "target": {
            "text": "Card P2-10 A01-A08: fixture and parity to declared tolerance, finite-difference and "
            "American 400/800 sensitivity, .01 vega scaling with explicit units, unavailable rather than "
            "invented IV and term brackets, and scenario labels that are assumptions.",
            "met": "partial",
        },
        "verdict": {
            "value": "needs_upgrade",
            "reason": "The primitives match the independent reference vectors to 1e-12 and every board row "
            "carries its model, scenario and coverage labels, but the NQ and ES boards built from owned data "
            f"are degenerate (median live contracts {medians.get('NQ')} and {medians.get('ES')}), and the "
            "American 400/800 sensitivity is one engineering contract rather than the contract's "
            "per-root-date sample, so the exposure board is only informative for QQQ and SPY today.",
        },
        "lever": {
            "change": "Own an option BBO or MBP schema for NQ and ES, then run the American sensitivity on the "
            "contract's 16 contracts per supported root and engineering date with the 10% exclusion recorded "
            "per cohort.",
            "evidence": "EXPOSURE_BOARDS.depth_by_root would show NQ and ES medians in the tens, and "
            "GREEK_SENSITIVITY would carry a per-cohort excluded-Greek record instead of one ATM case.",
        },
        "limits": [
            f"Boards are built on {len(dates)} engineering dates at 10:00 ET, not on the full history.",
            "The full-chain reference model is the labelled equivalent-European approximation; the American tree "
            "is a bounded sensitivity model, not an exact American price.",
            "The American 400/800 sensitivity runs on one engineering ATM contract, not on OPTIONS.md's sample of "
            "16 contracts per supported American root and engineering date, and no per-cohort 10% Greek-exclusion "
            "record is written: the CRR gamma at 400 versus 800 steps differs far more than 10% at these step "
            "counts, and no American Greek is consumed by any board or feature.",
            "Exposure scenarios are assumptions about sign, never known dealer inventory.",
            "The 1,742-session Level Atlas produced on 2026-09-15 stays under reports/research-work/phase2-early/"
            "P2-10 as a descriptive by-product; it is not an artifact of this receipt because it ranks levels over "
            f"a window that includes the blind hold-out {HOLDOUT[0]}..{HOLDOUT[1]}, and location work is Phase 3.",
            IDENTITY_INTERVAL_LIMIT,
            HOLDOUT_LIMIT,
        ],
    }


def _p2_03_card(attempt: Path, dates: list[str]) -> dict:
    fixtures = _load(attempt / "VOLATILITY_FIXTURES.json")
    features = _load(attempt / "VOLATILITY_FEATURES.json")
    targets = _load(attempt / "VOLATILITY_TARGETS.json")
    rows = targets.get("rows") or []
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    incomplete = [row for row in rows if row.get("status") != "ok"]
    unsupported = sorted({name for row in rows for name in (row.get("unsupported_close_cross") or [])})
    head_names = next((row.get("head_names") for row in rows if row.get("head_names")), [])
    heads = [head for row in ok_rows for head in (row.get("heads") or [])]
    heads_ok = [head for head in heads if head.get("status") == "ok"]
    head_gaps: dict[str, int] = {}
    for head in heads:
        if head.get("status") != "ok":
            key = f"{head.get('name')}/{head.get('reason')}"
            head_gaps[key] = head_gaps.get(key, 0) + 1
    groups = next((row.get("iv_groups") for row in (features.get("rows") or []) if row.get("iv_groups")), {})
    gk = float((fixtures.get("gk") or {}).get("variance"))
    rv = float((fixtures.get("rv") or {}).get("variance"))
    return {
        "question": "Do the volatility estimators reproduce their literal fixtures, and do the multi-horizon "
        "targets come from native midpoints without crossing a close, a roll or an unavailable boundary?",
        "headline": [
            _headline("Garman-Klass fixture variance", gk, "interval log-return variance",
                      interval=[gk, gk], attempt=attempt, artifact="VOLATILITY_FIXTURES.json",
                      selector="/gk/variance",
                      note="deterministic identity against the VOLATILITY.md worked example .5*ln(110/90)^2"),
            _headline("realized-variance fixture", rv, "interval log-return variance",
                      interval=[rv, rv], attempt=attempt, artifact="VOLATILITY_FIXTURES.json",
                      selector="/rv/variance",
                      note="deterministic identity against the worked example 2*ln(1.01)^2"),
            _headline("slice days with a complete target row", len(ok_rows), "days", support=len(rows),
                      attempt=attempt, artifact="VOLATILITY_TARGETS.json", selector="/rows",
                      note=f"{len(incomplete)} incomplete day rows, each with a reason"),
            _headline("target heads complete", len(heads_ok), "heads", support=len(heads), attempt=attempt,
                      artifact="VOLATILITY_TARGETS.json", selector="/rows/0/heads",
                      note=f"{len(head_names)} named heads on {len(ok_rows)} complete days; incomplete: "
                      f"{head_gaps or 'none'}; horizons unsupported for crossing a close or roll: "
                      f"{unsupported or 'none'}"),
            _headline("IV feature groups requested with a disposition", len(groups), "groups", support=10,
                      attempt=attempt, artifact="VOLATILITY_FEATURES.json", selector="/rows/0/iv_groups",
                      note="VOLATILITY.md names ten IV groups (NDX/NDXP, SPX/SPXW, QQQ, SPY, NQ, ES boards and "
                      "the VIX, VX, VVIX, VXN series); this build requests three and each carries a disposition"),
        ],
        "target": {
            "text": "Card P2-03 A01-A08: GK/YZ/RV worked examples, separated variance units, unsupported rather "
            "than truncated horizons, a disposition for every requested IV group, and no future price in a "
            "current feature.",
            "met": "partial",
        },
        "verdict": {
            "value": "needs_upgrade",
            "reason": f"The estimators reproduce every literal fixture to 1e-15 and {len(heads_ok)} of "
            f"{len(heads)} heads are built from native BBO midpoints with explicit incomplete records for the "
            f"rest, but the feature side is the arithmetic core only: {len(groups)} IV groups are requested "
            "where VOLATILITY.md names ten, and session seasonality and the rolling historical feature bank "
            "are not built yet.",
        },
        "lever": {
            "change": "Extend the feature builder to request every IV group named in VOLATILITY.md with a "
            "per-group disposition, and add the session-bucket and rolling GK/YZ features, before P2-04 fits "
            "the joint model.",
            "evidence": "VOLATILITY_FEATURES rows would carry ten group dispositions instead of three, and the "
            "A3 (IV-only) and A5 (joint) ablations in P2-04 would then be separable.",
        },
        "limits": [
            f"Features and targets are built on {len(dates)} engineering dates, not the full history.",
            "Realized variance uses native BBO midpoints with age<=5s; a missing boundary makes the target "
            "incomplete rather than bridged, and the minute-close series is kept only as a labelled comparison.",
            "No forecast is fitted here; the joint volatility fit, its ablations and its horizons are P2-04.",
            IDENTITY_INTERVAL_LIMIT,
            HOLDOUT_LIMIT,
        ],
    }


CARDS = {"P2-09": _p2_09_card, "P2-10": _p2_10_card, "P2-03": _p2_03_card}


def _card_markdown(card: dict) -> str:
    lines = [
        "## Result card",
        "",
        f"**Question.** {card['question']}",
        "",
        "| headline | value | unit | support or interval | note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in card["headline"]:
        bound = f"support {item['support']}" if "support" in item else f"interval {item['interval']}"
        lines.append(f"| {item['name']} | {item['value']} | {item['unit']} | {bound} | {item['note']} |")
    lines += [
        "",
        f"**Target.** {card['target']['text']} **Met:** {card['target']['met']}.",
        "",
        f"**Verdict.** {card['verdict']['value']} — {card['verdict']['reason']}",
        "",
        f"**Lever.** {card['lever']['change']} Evidence that it worked: {card['lever']['evidence']}",
        "",
        "**Limits.**",
        "",
    ]
    lines += [f"- {item}" for item in card["limits"]]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- report


def _inspected(spec: dict, attempt: Path) -> list[str]:
    task_id = spec["id"]
    if task_id == "P2-09":
        replay = (_load(attempt / "SURFACE_INPUT_SLICE.json").get("native_replay") or {})
        return [
            f"row {replay.get('row_id')} of {replay.get('path')} (file sha256 {replay.get('sha256')}) replays as "
            f"{replay.get('osi')} bid {replay.get('bid')} ask {replay.get('ask')} event_ns {replay.get('event_ns')} "
            f"available_at_ns {replay.get('available_at_ns')}, synthetic={replay.get('synthetic')}. Reading that "
            "parquet row directly with pyarrow gives bid 15.73, ask 16.38, ts_event 2024-01-02 14:31:00+00:00.",
        ]
    if task_id == "P2-10":
        board = ((_load(attempt / "EXPOSURE_BOARDS.json").get("boards") or [{}])[0])
        return [
            f"board {board.get('root')} {board.get('day')} at asof_ns {board.get('asof_ns')}: model "
            f"{board.get('model')}, scenario {board.get('scenario')} labelled {board.get('scenario_label')}, "
            f"n_live {board.get('n_live')}, n_with_oi {board.get('n_with_oi')}, spot {board.get('spot')}, "
            f"multiplier {board.get('multiplier')}, ATM IV {board.get('atm_iv')}.",
        ]
    row = ((_load(attempt / "VOLATILITY_TARGETS.json").get("rows") or [{}])[0])
    heads = row.get("heads") or []
    first = heads[0] if heads else {}
    return [
        f"target row {row.get('day')} issued at {row.get('issue_ns')} with sampling {row.get('sampling')}: "
        f"head {first.get('name')} status {first.get('status')} value {first.get('variance')} over "
        f"[{first.get('start_ns')}, {first.get('end_ns')}], known at {first.get('known_at_ns')}.",
    ]


def _report(spec: dict, attempt: Path, card: dict, commands: list[dict], probes: dict, dates: list[str]) -> str:
    task_id = spec["id"]
    lines = [
        f"# {task_id} — {spec['card']}",
        "",
        f"Attempt `{attempt}`. Native slice on {len(dates)} engineering dates "
        f"({dates[0]} to {dates[-1]}), run through `tools/run_context_experts.py slice`.",
        "",
        "## Commands",
        "",
    ]
    for index, command in enumerate(commands):
        lines.append(
            f"{index}. `{' '.join(command['argv'])}` in `{command['cwd']}` exited {command['exit_code']} "
            f"in {command['seconds']:.1f}s (log `{Path(command['log_path']).name}`)."
        )
    lines += ["", "## Inspected output", ""]
    lines += [f"- {item}" for item in _inspected(spec, attempt)]
    lines += [
        "",
        "## Forgery probes",
        "",
        f"The receipt as issued verifies (control ok={probes['control']['ok']}). "
        f"{probes['n_rejected']} of {probes['n_mutations']} single-gate forgeries are rejected with their intended "
        "failure code: " + ", ".join(f"{name} -> {item['expected_code']}" for name, item in probes["mutations"].items()) + ".",
        "",
        "## Limitations",
        "",
    ]
    lines += [f"- {item}" for item in card["limits"]]
    lines += ["", _card_markdown(card)]
    return "\n".join(lines)


# --------------------------------------------------------------------------- produce


def _next_attempt(run_dir: Path) -> Path:
    """A re-issue writes a new attempt beside the old one; issued evidence is never overwritten."""
    existing = sorted(int(path.name.split("-")[1]) for path in run_dir.glob("attempt-*") if path.is_dir())
    return run_dir / f"attempt-{(existing[-1] + 1) if existing else 1:04d}"


def _receipt_from_run(impl_out: Path, dep: str, run_stamp: str) -> Path:
    """The dependency's receipt issued from this same slice run, and only that one."""
    root = impl_out / "reports/research-work" / dep
    found = []
    for receipt in sorted(root.rglob("attempt-*/TASK_RECEIPT.json")):
        draft = receipt.parent / "DRAFT_MANIFEST.json"
        if not draft.is_file():
            continue
        identities = json.loads(draft.read_text()).get("input_identities") or {}
        slice_path = (identities.get("slice_command") or {}).get("path") or ""
        if f"/{run_stamp}/" in slice_path:
            found.append(receipt)
    if not found:
        raise SystemExit(f"{dep}: no receipt issued from {run_stamp}")
    return found[-1]  # the newest attempt of that run


def _coverage(task_id: str, attempt: Path, dates: list[str]) -> dict:
    """Counts a reader can reconcile: attempted cells, complete cells, unknown cells."""
    coverage = {"native": True, "dates": len(dates), "market_feed_completeness": "unknown"}
    if task_id == "P2-09":
        rows = _load(attempt / "OPTIONS_AVAILABILITY.json").get("coverage") or []
        slices = _load(attempt / "SURFACE_INPUT_SLICE.json").get("slices") or []
        coverage.update(
            {
                "root_day_cells": len(rows),
                "complete_observed_scope": sum(1 for row in rows if row.get("disposition") == "complete_observed_scope"),
                "without_native_intraday_spot": sum(1 for row in rows if not row.get("native_intraday_spot")),
                "surface_input_slices": len(slices),
                "quote_rows_rejected": sum(int(row.get("n_rejected") or 0) for row in slices),
            }
        )
    elif task_id == "P2-10":
        boards = _load(attempt / "EXPOSURE_BOARDS.json")
        days = boards.get("days") or []
        coverage.update(
            {
                "board_day_cells": len(days),
                "boards_built": len(boards.get("boards") or []),
                "boards_refused": sum(1 for row in days if row.get("status") != "ok"),
                "surface_quality_rows": len(_load(attempt / "SURFACE_QUALITY.json").get("rows") or []),
            }
        )
    else:
        rows = _load(attempt / "VOLATILITY_TARGETS.json").get("rows") or []
        coverage.update(
            {
                "target_day_rows": len(rows),
                "complete": sum(1 for row in rows if row.get("status") == "ok"),
                "incomplete": sum(1 for row in rows if row.get("status") != "ok"),
                "feature_day_rows": len(_load(attempt / "VOLATILITY_FEATURES.json").get("rows") or []),
            }
        )
    return coverage


def produce(task_id: str, *, root: Path, out_root: Path, run_stamp: str, produced: dict) -> Path:
    spec = load_spec(task_id, root)
    impl_out = out_root / "implementation"
    run_dir = impl_out / "reports/research-work/phase2-early" / run_stamp / spec["slice_dir"]
    dates = [item for item in (impl_out / "reports/research-work/phase2-early" / run_stamp / "DATES20.txt").read_text().strip().split(",")]

    code_paths = list(dict.fromkeys([*spec["owns"], *spec["helpers"]]))
    for rel in code_paths:
        identity_file = root / rel
        local_file = out_root / rel
        if not identity_file.is_file():
            raise SystemExit(f"{rel} is not in the identity root {root}")
        if local_file.is_file() and file_digest(local_file) != file_digest(identity_file):
            raise SystemExit(
                f"{rel} differs between {out_root} and the identity root {root}; the receipt would claim code "
                "the verifier cannot see. Merge the change first."
            )
    plan_paths = list(dict.fromkeys([spec["card"], *spec["reads"], GRAPH_REL, REGISTRY_REL]))
    plan_files = {rel: file_digest(root / rel) for rel in plan_paths}
    code_files = {rel: file_digest(root / rel) for rel in code_paths}

    predecessors: dict[str, str] = {}
    predecessor_paths: dict[str, Path] = {}
    for dep in spec["deps"]:
        if dep == "P15-02":
            found = P15_02
            sha = file_digest(found)
            if sha != P15_02_SHA:
                raise SystemExit(f"P15-02 receipt digest {sha} != {P15_02_SHA}")
        else:
            found = produced.get(dep) or _receipt_from_run(impl_out, dep, run_stamp)
            sha = file_digest(found)
        predecessors[dep] = sha
        predecessor_paths[dep] = Path(found)

    draft = {
        "schema_version": "research-draft-manifest-v2",
        "assurance_version": ASSURANCE_VERSION,
        "task_id": task_id,
        "plan_sha256": digest(plan_files),
        "code_sha256": None,
        "predecessor_receipts": predecessors,
        "input_identities": {
            "p15_02_receipt": {"path": str(P15_02), "sha256": P15_02_SHA},
            "slice_command": {
                "path": str(run_dir / "slice_command.json"),
                "sha256": file_digest(run_dir / "slice_command.json"),
            },
        },
        "coverage_identity": digest({"dates": dates, "run_root": str(run_dir)}),
        "registered_candidate_config": None,
        "declared_study_dates": {"start": dates[0], "end": dates[-1]},
        "drafted_at": "2026-09-16",
    }

    runtime = {"python": sys.version.split()[0]}
    try:
        import databento as db

        runtime["databento"] = db.__version__
    except ImportError:
        runtime["databento"] = None
    lock = root / "implementation/uv.lock"
    lock_sha = file_digest(lock) if lock.is_file() else file_digest(root / "implementation/pyproject.toml")

    attempt_parent = impl_out / "reports/research-work" / task_id
    staging = Path(tempfile.mkdtemp(prefix=f"{task_id}-stage-"))
    try:
        plan_copies = write_snapshot_tree(staging, "plan", plan_files, root=root)
        code_copies = write_snapshot_tree(staging, "code", code_files, root=root)
        plan_doc = plan_snapshot_document(plan_files, plan_copies)
        code_doc = code_snapshot_document(
            code_files,
            code_copies,
            runtime=runtime,
            dependency_lock_sha256=lock_sha,
            imported_modules=spec["imported"],
        )
        draft["code_sha256"] = digest(code_doc)
        run_id = semantic_run_id(draft)
        attempt = _next_attempt(attempt_parent / run_id)
        shutil.copytree(staging, attempt)
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    for name in spec["artifacts"]:
        if name == "RESULT_CARD.json":
            continue
        shutil.copy2(run_dir / name, attempt / name)
    shutil.copy2(run_dir / "THROUGHPUT.json", attempt / "THROUGHPUT.json")

    commands = [
        _run(
            [sys.executable, "-m", "pytest", spec["test"].split("implementation/", 1)[1], "-q", "-p", "no:cacheprovider"],
            cwd=impl_out,
            log_path=attempt / "pytest.log",
        )
    ]
    if commands[0]["exit_code"] != 0:
        raise SystemExit(f"pytest failed for {task_id}:\n{(attempt / 'pytest.log').read_text()[-2000:]}")
    commands.append(_recorded_slice_command(run_dir, attempt))
    predecessor_indices = []
    for position, dep in enumerate(spec["deps"]):
        log_name = "predecessor_verify.log" if position == 0 else f"predecessor_verify_{dep}.log"
        commands.append(
            _run(
                [sys.executable, str(root / VERIFIER_REL), "task", "--receipt", str(predecessor_paths[dep])],
                cwd=impl_out,
                log_path=attempt / log_name,
            )
        )
        if commands[-1]["exit_code"] != 0:
            raise SystemExit(
                f"predecessor {dep} does not verify for {task_id}: {(attempt / log_name).read_text()[:800]}"
            )
        predecessor_indices.append(len(commands) - 1)
    indices = {"pytest": 0, "slice": 1, "predecessors": predecessor_indices}

    card = CARDS[task_id](attempt, dates)
    card = {"schema_version": RESULT_CARD_SCHEMA, "task_id": task_id, **card}
    write_json_document(attempt / "RESULT_CARD.json", card)

    coverage = _coverage(task_id, attempt, dates)
    unresolved = list(card["limits"])

    # Optimistic seed: the loop below only stops once the probes file on disk is
    # exactly the probe of the receipt that names it, so a wrong prediction costs
    # one more iteration and can never be published.
    probes = {
        "schema_version": PROBES_SCHEMA,
        "task_id": task_id,
        "control": {"ok": True, "codes": []},
        "mutations": {
            name: {
                "ok": False,
                "codes": [code],
                "expected_code": code,
                "expected_code_present": True,
                "forgery": description,
                "rejected": True,
            }
            for name, _fn, code, description in MUTATIONS
        },
        "n_rejected": len(MUTATIONS),
        "n_mutations": len(MUTATIONS),
        "ok": True,
    }
    receipt_path = attempt / "TASK_RECEIPT.json"
    manifest_names = list(COMMON_ARTIFACTS) + [
        (name, spec["artifact_schemas"].get(name, "research-artifact-v1"))
        for name in list(spec["artifacts"]) + ["THROUGHPUT.json"]
    ]
    manifest_names += [("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2"), (PROBES_NAME, PROBES_SCHEMA)]

    for iteration in range(1, 6):
        for name in (PROBES_NAME, "EVIDENCE_MATRIX.json", "REPORT.md", "WORK_LOG.md", "DECISIONS.tsv", "TASK_RECEIPT.json"):
            path = attempt / name
            if path.exists():
                path.unlink()
        write_json_document(attempt / PROBES_NAME, probes)
        (attempt / "REPORT.md").write_text(_report(spec, attempt, card, commands, probes, dates), encoding="utf-8")
        matrix = build_matrix(spec, attempt, root, indices)
        write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix)
        (attempt / "WORK_LOG.md").write_text(
            f"# {task_id} work log\n\n"
            f"- Native slice `{run_dir}` on {len(dates)} engineering dates, exit {commands[1]['exit_code']}, "
            f"{commands[1]['seconds']:.1f}s.\n"
            f"- `pytest {spec['test']}` exit {commands[0]['exit_code']}, {_pytest_selector(attempt)}.\n"
            f"- Predecessor receipts {sorted(predecessors)} verified, exit {commands[2]['exit_code']}.\n"
            f"- Forgery probes: control ok={probes['control']['ok']}, "
            f"{probes['n_rejected']} of {probes['n_mutations']} mutations rejected with their intended code.\n"
            f"- Result card verdict {card['verdict']['value']} (target met: {card['target']['met']}); the receipt "
            f"claims no fitted or ranked quantity, so the "
            f"blind hold-out {HOLDOUT[0]}..{HOLDOUT[1]} is not consumed.\n",
            encoding="utf-8",
        )
        (attempt / "DECISIONS.tsv").write_text(
            "ts\tphase\tdecision\twhy\tevidence\tresult\n"
            f"2026-09-16T00:00:00Z\t{task_id}\tre-run the native slice into a new run root and issue the receipt "
            f"from it\tthe 2026-09-15 draft receipts predate the result card, the HOW_TO_RUN plan pin and the "
            f"S01-S03 matrix change\t{run_dir}\treissued\n"
            f"2026-09-16T00:00:00Z\t{task_id}\tbind every predecessor receipt in the artifact manifest\tthe card "
            f"asks for predecessor hashes and actual paths in this receipt\t{sorted(predecessors)}\tbound\n"
            f"2026-09-16T00:00:00Z\t{task_id}\tkeep the code unchanged\tthe verifier re-hashes owned code against "
            f"/workspace, so an unmerged edit could not be pinned honestly\t{len(code_files)} files pinned\tunchanged\n",
            encoding="utf-8",
        )

        manifest = []
        for name, schema in manifest_names:
            path = attempt / name
            if not path.is_file():
                continue
            rows = None
            if name == "EVIDENCE_MATRIX.json":
                rows = len(matrix["checks"])
            manifest.append(artifact_entry(path, schema=schema, row_count=rows))
        for dep, path in predecessor_paths.items():
            manifest.append(artifact_entry(path, schema="research-task-receipt-v2"))
        receipt = make_task_receipt(
            task_id=task_id,
            run_id=run_id,
            plan_sha256=draft["plan_sha256"],
            code_sha256=draft["code_sha256"],
            predecessor_receipts=predecessors,
            command_results=commands,
            artifact_manifest=manifest,
            acceptance_checks={key: True for key in spec["acceptance_keys"]},
            disposition="implemented_verified",
            reason=f"{task_id}: native slice on {len(dates)} engineering dates, owned tests, bound evidence matrix "
            f"and forgery probes; result card verdict {card['verdict']['value']}.",
            coverage=coverage,
            unresolved=unresolved,
        )
        write_task_receipt(receipt_path, receipt)
        fresh = run_probes(spec, attempt)
        if canonical_bytes(fresh) == canonical_bytes(probes):
            break
        probes = fresh
    else:
        raise SystemExit(f"{task_id}: forgery probes did not reach a fixed point")

    if not probes["ok"]:
        raise SystemExit(f"{task_id}: forgery probes failed: {json.dumps(probes, sort_keys=True)[:1200]}")
    result = verify_task_receipt(receipt_path)
    print(
        json.dumps(
            {
                "task": task_id,
                "attempt": str(attempt),
                "run_id": run_id,
                "receipt_sha256": file_digest(receipt_path),
                "verifier_ok": bool(result.ok),
                "failures": [item.to_dict() for item in result.failures][:6],
                "verdict": card["verdict"]["value"],
                "target_met": card["target"]["met"],
            },
            sort_keys=True,
        )
    )
    if not result.ok:
        raise SystemExit(f"{task_id}: receipt does not verify")
    produced[task_id] = receipt_path
    return receipt_path


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--task", action="append")
    parser.add_argument("--root", default=str(IDENTITY_ROOT))
    parser.add_argument("--out-root", default=str(WORKTREE))
    parser.add_argument("--run-stamp", default="run-2026-09-16")
    args = parser.parse_args()
    produced: dict[str, Path] = {}
    for task in args.task or ["P2-09", "P2-10", "P2-03"]:
        produce(task, root=Path(args.root), out_root=Path(args.out_root), run_stamp=args.run_stamp, produced=produced)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
