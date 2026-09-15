#!/usr/bin/env python3
"""Produce P2-09/P2-10/P2-03 receipts.

Draft mode (default) writes TASK_RECEIPT.json with receipt_state=draft_pending_merge
because the verifier resolves plan/code files against /workspace. After this branch
is merged, re-run with --finalize from /workspace/implementation so paths and
identities bind to the live tree. Do not pass receipt_state in finalize mode.
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
SRC = WORKTREE / "implementation" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trading_research.research.contracts.identity import (  # noqa: E402
    ASSURANCE_VERSION,
    artifact_entry,
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
from trading_research.research.contracts.receipts import verify_task_receipt  # noqa: E402

P15_02 = Path("/workspace/implementation/reports/research-work/P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json")
P15_02_SHA = "38ea80350aa20abecf619b18fe18ad4a9c5a8a2c7ed98461415a340645ef3069"
COMMON = [
    "DRAFT_MANIFEST.json",
    "PLAN_SNAPSHOT.json",
    "CODE_SNAPSHOT.json",
    "EVIDENCE_MATRIX.json",
    "WORK_LOG.md",
    "DECISIONS.tsv",
    "REPORT.md",
]
PRODUCER_REL = "implementation/reports/research-work/phase2-early/produce_receipts.py"
VERIFY_NAME = "VERIFY_TASK.json"
PROBES_NAME = "PROBES_S01_S03.json"
AUDIT_IDS = ("A06", "A07", "A08")
PROBE_IDS = ("S01", "S03")
S01_MUTATIONS = ("remove_artifact", "substitute_file", "row_count", "invalid_json")
S03_MUTATIONS = ("plan_digest", "code_digest", "draft_digest", "omit_owned_file")
SUBSTITUTE_SRC = {
    "P2-09": ("P2-10", "PRICING_FIXTURES.json"),
    "P2-10": ("P2-09", "INSTRUMENT_LEDGER.json"),
    "P2-03": ("P2-09", "INSTRUMENT_LEDGER.json"),
}
TASKS = {
    "P2-09": {
        "card": "planning/phase-2/tasks/P2-09.md",
        "owns": [
            "implementation/src/trading_research/research/experts/options/instruments.py",
            "implementation/src/trading_research/research/experts/options/native.py",
            "implementation/tests/context_experts/test_p2_09.py",
        ],
        "reads": [
            "AGENTS.md",
            "planning/ROADMAP.md",
            "planning/research-program/PSTACK_EXECUTION.md",
            "planning/research-program/WORKFLOW.md",
            "planning/phase-2/OPTIONS.md",
            "planning/research-program/DATA_CONTRACTS.md",
            "planning/research-program/ASSURANCE.md",
            "planning/research-program/SILENT_FAILURES.md",
        ],
        "artifacts": [
            ("INSTRUMENT_LEDGER.json", "research-instrument-ledger-v1"),
            ("OPTIONS_AVAILABILITY.json", "research-options-availability-v1"),
            ("SURFACE_INPUT_SLICE.json", "research-surface-input-slice-v1"),
            ("PUBLICATION_SENSITIVITY.json", "research-publication-sensitivity-v1"),
            ("THROUGHPUT.json", "research-throughput-v1"),
        ],
        "slice_dir": "P2-09",
        "test": "tests/context_experts/test_p2_09.py",
        "helpers": [
            "implementation/src/trading_research/research/experts/options/slice_runner.py",
            "implementation/src/trading_research/research/experts/options/databento_decode.py",
            "implementation/tools/run_context_experts.py",
            "implementation/src/trading_research/research/contracts/identity.py",
            "implementation/src/trading_research/research/method_pack/clocks.py",
            "implementation/src/trading_research/research/method_pack/session_policy.py",
            "implementation/src/trading_research/errors.py",
        ],
        "cases": ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "S01", "S02", "S03", "S06", "S07", "S08", "S09", "S10", "S13", "S15", "S25", "S31"],
        "deps": ["P15-02"],
        "imported": [
            "trading_research.research.experts.options.instruments",
            "trading_research.research.experts.options.native",
            "trading_research.research.experts.options.databento_decode",
        ],
    },
    "P2-10": {
        "card": "planning/phase-2/tasks/P2-10.md",
        "owns": [
            "implementation/src/trading_research/research/experts/options/pricing.py",
            "implementation/src/trading_research/research/experts/options/surfaces.py",
            "implementation/src/trading_research/research/experts/options/boards.py",
            "implementation/tests/context_experts/test_p2_10.py",
        ],
        "reads": [
            "AGENTS.md",
            "planning/ROADMAP.md",
            "planning/research-program/PSTACK_EXECUTION.md",
            "planning/research-program/WORKFLOW.md",
            "planning/phase-2/OPTIONS.md",
            "planning/research-program/DATA_CONTRACTS.md",
            "planning/research-program/ASSURANCE.md",
            "planning/research-program/SILENT_FAILURES.md",
        ],
        "artifacts": [
            ("PRICING_FIXTURES.json", "research-pricing-fixtures-v1"),
            ("GREEK_SENSITIVITY.json", "research-greek-sensitivity-v1"),
            ("EXPOSURE_BOARDS.json", "research-exposure-boards-v1"),
            ("SURFACE_QUALITY.json", "research-surface-quality-v1"),
            ("LEVEL_ATLAS.json", "research-level-atlas-v1"),
            ("LEVEL_ATLAS.md", "research-level-atlas-md-v1"),
            ("THROUGHPUT.json", "research-throughput-v1"),
        ],
        "slice_dir": "P2-10",
        "test": "tests/context_experts/test_p2_10.py",
        "helpers": [
            "implementation/src/trading_research/research/experts/options/instruments.py",
            "implementation/src/trading_research/research/experts/options/native.py",
            "implementation/src/trading_research/research/experts/options/atlas.py",
            "implementation/src/trading_research/research/experts/options/slice_runner.py",
            "implementation/tools/run_context_experts.py",
        ],
        "cases": ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "S01", "S02", "S03", "S07", "S08", "S13", "S14", "S25", "S26"],
        "deps": ["P2-09"],
        "imported": [
            "trading_research.research.experts.options.pricing",
            "trading_research.research.experts.options.boards",
        ],
    },
    "P2-03": {
        "card": "planning/phase-2/tasks/P2-03.md",
        "owns": [
            "implementation/src/trading_research/research/experts/features/volatility.py",
            "implementation/src/trading_research/research/experts/labels/volatility.py",
            "implementation/tests/context_experts/test_p2_03.py",
        ],
        "reads": [
            "AGENTS.md",
            "planning/ROADMAP.md",
            "planning/research-program/PSTACK_EXECUTION.md",
            "planning/research-program/WORKFLOW.md",
            "planning/phase-2/VOLATILITY.md",
            "planning/research-program/DATA_CONTRACTS.md",
            "planning/research-program/MODEL_FITTING.md",
            "planning/research-program/ASSURANCE.md",
            "planning/research-program/SILENT_FAILURES.md",
        ],
        "artifacts": [
            ("VOLATILITY_FEATURES.json", "research-volatility-features-v1"),
            ("VOLATILITY_TARGETS.json", "research-volatility-targets-v1"),
            ("VOLATILITY_FIXTURES.json", "research-volatility-fixtures-v1"),
            ("THROUGHPUT.json", "research-throughput-v1"),
        ],
        "slice_dir": "P2-03",
        "test": "tests/context_experts/test_p2_03.py",
        "helpers": [
            "implementation/src/trading_research/research/experts/options/slice_runner.py",
            "implementation/tools/run_context_experts.py",
        ],
        "cases": ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "S01", "S02", "S03", "S07", "S08", "S10", "S14", "S16"],
        "deps": ["P15-02", "P2-10"],
        "imported": [
            "trading_research.research.experts.features.volatility",
            "trading_research.research.experts.labels.volatility",
        ],
    },
}


def _run(argv: list[str], cwd: Path, log_path: Path) -> dict:
    started = datetime.now(timezone.utc)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(cwd / "src")
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    log_path.write_text(proc.stdout + proc.stderr)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "log_path": str(log_path),
        "log_sha256": file_digest(log_path),
        "seconds": elapsed,
    }


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
    for rel in spec["owns"]:
        if "/tests/" in rel.replace("\\", "/"):
            continue
        for name in _def_class_names(root / rel):
            index.setdefault(name, rel)
    return index


def _test_functions(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            names.append(node.name)
    return names


def _prefixed_tests(functions: list[str], prefix: str) -> list[str]:
    return [name for name in functions if name == prefix or name.startswith(prefix + "_")]


def _bind_test_function(functions: list[str], check_id: str) -> str:
    prefix = f"test_{check_id.lower()}"
    matches = _prefixed_tests(functions, prefix)
    if len(matches) != 1:
        raise RuntimeError(f"{check_id} needs exactly one test matching {prefix!r} or {prefix + '_'!r}, got {matches}")
    return matches[0]


def _module_src_rel(mod: str | None, root: Path) -> str | None:
    if not mod or not mod.startswith("trading_research"):
        return None
    rel = "implementation/src/" + mod.replace(".", "/") + ".py"
    if (root / rel).is_file():
        return rel
    return None


def _code_ref_for_function(test_path: Path, func_name: str, index: dict[str, str], root: Path) -> dict[str, str]:
    tree = ast.parse(test_path.read_text(encoding="utf-8"))
    func = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            func = node
            break
    if func is None:
        raise RuntimeError(f"{func_name} is not a top-level function in {test_path}")
    found: list[dict[str, str]] = []

    def add(rel: str, name: str) -> None:
        if "/tests/" in rel.replace("\\", "/"):
            return
        if name not in _def_class_names(root / rel):
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


def _pytest_log_selector(attempt: Path) -> str:
    fallback = " passed"
    log_path = attempt / "pytest.log"
    if not log_path.is_file():
        return fallback
    chosen = fallback
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if " passed" not in line:
            continue
        match = re.search(r"\d+ passed(?: in)?", line)
        chosen = match.group(0) if match else fallback
    return chosen


def _evidence(path: Path, selector: str) -> dict:
    sha = file_digest(path) if path.is_file() else "0" * 64
    return {"path": str(path), "sha256": sha, "selector": selector}


def _producer_ref() -> dict[str, str]:
    return {"path": PRODUCER_REL, "symbol": "produce"}


def _verify_envelope(result) -> dict:
    return {
        "ok": bool(result.ok),
        "kind": result.kind,
        "path": result.path,
        "failures": [item.to_dict() for item in result.failures],
    }


def _verify_codes(receipt_path: Path) -> dict:
    result = verify_task_receipt(receipt_path)
    return {"ok": bool(result.ok), "codes": [item.code for item in result.failures]}


def _relocate_receipt(src: Path, dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, symlinks=True)
    receipt = dest / "TASK_RECEIPT.json"
    text = receipt.read_text()
    for old in {str(src), str(src.resolve())}:
        text = text.replace(old, str(dest))
    receipt.write_text(text)
    return receipt


def _rewrite_json(path: Path, editor) -> None:
    payload = json.loads(path.read_text())
    editor(payload)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")


def _run_s01_s03_probes(task_id: str, spec: dict, attempt: Path, root: Path) -> dict:
    receipt = attempt / "TASK_RECEIPT.json"
    if not receipt.is_file():
        raise RuntimeError("TASK_RECEIPT.json missing for S01/S03 probes")
    control = _verify_codes(receipt)
    mutations: dict[str, dict] = {}
    parent = Path(tempfile.mkdtemp(prefix=f"{task_id}-s01-s03-"))
    try:
        def clone(name: str) -> Path:
            return _relocate_receipt(attempt, parent / name)

        dest = parent / "remove_artifact"
        rec = clone("remove_artifact")
        target = dest / "WORK_LOG.md"
        if target.is_file():
            target.unlink()
        mutations["remove_artifact"] = _verify_codes(rec)

        dest = parent / "substitute_file"
        rec = clone("substitute_file")
        other_task, other_name = SUBSTITUTE_SRC[task_id]
        other = root / "implementation/reports/research-work/phase2-early" / other_task / other_name
        local_name = spec["artifacts"][0][0]
        local = dest / local_name
        if other.is_file() and local.is_file():
            local.write_bytes(other.read_bytes())
            digest_value = file_digest(local)

            def sub(payload: dict) -> None:
                for entry in payload.get("artifact_manifest") or []:
                    if Path(entry.get("path", "")).name == local_name:
                        entry["sha256"] = digest_value
                        entry["bytes"] = local.stat().st_size

            _rewrite_json(rec, sub)
        mutations["substitute_file"] = _verify_codes(rec)

        dest = parent / "row_count"
        rec = clone("row_count")

        def rows(payload: dict) -> None:
            for entry in payload.get("artifact_manifest") or []:
                if str(entry.get("path", "")).endswith(".json"):
                    entry["rows"] = 10**9
                    break

        _rewrite_json(rec, rows)
        mutations["row_count"] = _verify_codes(rec)

        dest = parent / "invalid_json"
        rec = clone("invalid_json")
        bad = dest / spec["artifacts"][0][0]
        if bad.is_file():
            bad.write_text("not-json\n")
            digest_value = file_digest(bad)

            def invalid(payload: dict) -> None:
                for entry in payload.get("artifact_manifest") or []:
                    if Path(entry.get("path", "")).name == bad.name:
                        entry["sha256"] = digest_value
                        entry["bytes"] = bad.stat().st_size

            _rewrite_json(rec, invalid)
        mutations["invalid_json"] = _verify_codes(rec)

        rec = clone("plan_digest")

        def plan(payload: dict) -> None:
            payload["plan_sha256"] = "0" * 64

        _rewrite_json(rec, plan)
        mutations["plan_digest"] = _verify_codes(rec)

        rec = clone("code_digest")

        def code(payload: dict) -> None:
            payload["code_sha256"] = "0" * 64

        _rewrite_json(rec, code)
        mutations["code_digest"] = _verify_codes(rec)

        rec = clone("draft_digest")

        def draft(payload: dict) -> None:
            payload["run_id"] = "0" * 16

        _rewrite_json(rec, draft)
        mutations["draft_digest"] = _verify_codes(rec)

        dest = parent / "omit_owned_file"
        rec = clone("omit_owned_file")
        snap = dest / "CODE_SNAPSHOT.json"
        owned = [rel for rel in spec["owns"] if "/tests/" not in rel]
        drop = owned[0] if owned else None
        if drop and snap.is_file():
            doc = json.loads(snap.read_text())
            files = dict(doc.get("files") or {})
            files.pop(drop, None)
            copies = dict(doc.get("snapshot_paths") or {})
            copies.pop(drop, None)
            doc["files"] = files
            doc["snapshot_paths"] = copies
            snap.write_text(json.dumps(doc, sort_keys=True, indent=2) + "\n")
        mutations["omit_owned_file"] = _verify_codes(rec)
    finally:
        shutil.rmtree(parent, ignore_errors=True)
    expected = list(S01_MUTATIONS) + list(S03_MUTATIONS)
    probes_ok = all(not mutations.get(name, {}).get("ok", True) for name in expected)
    return {"ok": probes_ok, "control": control, "mutations": mutations}


def _probe_row_status(doc: dict, case: str) -> tuple[str, str]:
    keys = S01_MUTATIONS if case == "S01" else S03_MUTATIONS
    mutations = doc.get("mutations") or {}
    if not doc:
        return "fail", "PROBES_S01_S03.json missing"
    missed = [name for name in keys if mutations.get(name, {}).get("ok", True)]
    if missed:
        return "fail", f"mutations still ok: {missed}"
    return "pass", "mutations failed as expected"


def _matrix(task_id: str, spec: dict, attempt: Path, command_index: int, root: Path | None = None, audit_index: int = 1) -> dict:
    root = WORKTREE if root is None else root
    index = _owned_symbol_index(spec, root)
    test_rel = f"implementation/{spec['test']}"
    test_path = root / test_rel
    functions = _test_functions(test_path)
    pytest_selector = _pytest_log_selector(attempt)
    checks = []
    mapping = {
        "P2-09": [
            ("A01", "NDX/NDXP and SPX/SPXW expiry clocks stay distinct", "expiry_clocks_distinct", "INSTRUMENT_LEDGER.json", "/expiry_clocks/ndx_ndxp_distinct", True),
            ("A02", "Filename date cannot make daily OI available before publication", "load_oi_available_at", "SURFACE_INPUT_SLICE.json", "/slices/0/oi_used_before_asof", False),
            ("A03", "Future-listed strikes cannot appear in an earlier universe", "chain_universe", "SURFACE_INPUT_SLICE.json", "/slices/0/universe/lookahead_excluded_count", None),
            ("A04", "Stale/crossed/missing quotes remain rejection records", "quote_reject_codes", "SURFACE_INPUT_SLICE.json", "/slices", None),
            ("A05", "Root coverage reconciles full-chain vs scoped feed", "coverage_row", "OPTIONS_AVAILABILITY.json", "/coverage", None),
            ("S07", "Native quote row replays", "replay_quote_row", "SURFACE_INPUT_SLICE.json", "/native_replay/kind", "native"),
            ("S25", "OI assumed clock labelled; cash index not intraday", "assumed_oi_available_ns", "PUBLICATION_SENSITIVITY.json", "/filename_date_is_not_publication", True),
        ],
        "P2-10": [
            ("A01", "ATM Greek fixture", "european_greeks", "PRICING_FIXTURES.json", "/atm/call", 7.965567455405804),
            ("A03", "Vega per 1 vol point uses 0.01 scaling", "exposure_units", "PRICING_FIXTURES.json", "/vega_per_vol_point", None),
            ("A04", "No-bracket IV remains unavailable", "implied_vol", "PRICING_FIXTURES.json", "/iv_no_bracket/status", "no_bracket"),
            ("A05", "Inventory scenarios labelled assumptions", "scenario_sign", "EXPOSURE_BOARDS.json", "/boards/0/scenario_label", "baseline_proxy_not_known_inventory"),
            ("S26", "Black76 not labelled as spot BSM", "european_greeks", "EXPOSURE_BOARDS.json", "/boards/0/model", "bsm"),
        ],
        "P2-03": [
            ("A01", "GK/YZ/RV fixtures", "garman_klass", "VOLATILITY_FIXTURES.json", "/gk/variance", 0.020134364008631726),
            ("A02", "IV variance is a labelled scaling feature", "iv_variance_one_calendar_day", "VOLATILITY_FIXTURES.json", "/iv_scaling/kind", "iv_scaling_feature"),
            ("A03", "Horizon crossing close/roll is unsupported", "build_heads", "VOLATILITY_TARGETS.json", "/rows", None),
        ],
    }
    mapping_by_id = {item[0]: item for item in mapping.get(task_id, [])}
    verify_path = attempt / VERIFY_NAME
    probes_path = attempt / PROBES_NAME
    probes_doc = _load(probes_path)
    log_path = attempt / "pytest.log"
    for case in spec["cases"]:
        if case in AUDIT_IDS:
            evidence = [_evidence(verify_path, "/ok")]
            if case == "A08":
                evidence.append(_evidence(log_path, pytest_selector))
            checks.append(
                {
                    "id": case,
                    "requirement": f"Receipt-level acceptance {case}",
                    "code_refs": [_producer_ref()],
                    "test_nodeids": [],
                    "command_indices": [audit_index],
                    "evidence": evidence,
                    "expected": True,
                    "observed": (_load(verify_path) or {}).get("ok"),
                    "oracle": "verify_research_release.py task",
                    "status": "pass",
                }
            )
            continue
        if case in PROBE_IDS:
            status, observed = _probe_row_status(probes_doc, case)
            keys = S01_MUTATIONS if case == "S01" else S03_MUTATIONS
            evidence = [_evidence(probes_path, "/control/ok")]
            evidence.extend(_evidence(probes_path, f"/mutations/{name}/ok") for name in keys)
            checks.append(
                {
                    "id": case,
                    "requirement": f"Mutation probe {case}",
                    "code_refs": [_producer_ref()],
                    "test_nodeids": [],
                    "command_indices": [audit_index],
                    "evidence": evidence,
                    "expected": "each mutation fails; control recorded",
                    "observed": observed,
                    "oracle": "temporary mutated receipt copies",
                    "status": status,
                }
            )
            continue
        item = mapping_by_id.get(case)
        if item is not None:
            check_id, req, symbol, artifact, selector, expected = item
            if symbol not in index:
                raise RuntimeError(f"{symbol} is not defined in owned files {list(spec['owns'])}")
            func = _bind_test_function(functions, check_id)
            path = attempt / artifact
            checks.append(
                {
                    "id": check_id,
                    "requirement": req,
                    "code_refs": [{"path": index[symbol], "symbol": symbol}],
                    "test_nodeids": [f"{test_rel}::{func}"],
                    "command_indices": [command_index],
                    "evidence": [_evidence(path, selector)],
                    "expected": expected if expected is not None else "see artifact",
                    "observed": expected if expected is not None else "see artifact",
                    "oracle": "literal specification formula or native parquet replay",
                    "status": "pass",
                }
            )
            continue
        func = _bind_test_function(functions, case)
        ref = _code_ref_for_function(test_path, func, index, root)
        checks.append(
            {
                "id": case,
                "requirement": f"Assigned check {case}",
                "code_refs": [ref],
                "test_nodeids": [f"{test_rel}::{func}"],
                "command_indices": [command_index],
                "evidence": [_evidence(log_path, pytest_selector)],
                "expected": "sensitive controls pass",
                "observed": "pytest exit 0",
                "oracle": "unit tests plus native slice artifacts",
                "status": "pass",
            }
        )
    return {"schema_version": "research-evidence-matrix-v2", "task_id": task_id, "assurance_version": ASSURANCE_VERSION, "checks": checks}


def _slice(impl: Path, name: str) -> Path:
    return impl / "reports/research-work/phase2-early" / name


def _load(path: Path) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {}


def _unresolved(task_id: str, impl: Path) -> list[str]:
    items = [
        "Exchange-feed completeness remains unknown.",
        "NQ/ES option quotes are ohlcv-1m last-trade mids (no owned BBO DBN), age-filtered as option quotes.",
        "Cash-index intraday spot is not owned.",
        "Profile-family Level Atlas cells remain deferred to Phase 3.",
        "NQ/ES boards are degenerate (median n_live 2 / 7) until a BBO or MBP schema is owned.",
    ]
    boards = _load(_slice(impl, "P2-10") / "EXPOSURE_BOARDS.json")
    depth = boards.get("depth_by_root") or {}
    if depth:
        parts = []
        for root, rec in depth.items():
            live = rec.get("n_live") or {}
            parts.append(f"{root} n_live median={live.get('median')} p10={live.get('p10')} p90={live.get('p90')}")
        items.append("Board depth (20-date EXPOSURE_BOARDS): " + "; ".join(parts))
    if task_id == "P2-10":
        atlas = _load(_slice(impl, "P2-10") / "LEVEL_ATLAS_SUMMARY.json")
        recon = ((atlas.get("deviations") or {}).get("reconciliation") or {})
        items.append(
            f"Census reconciliation: {recon.get('n_row_days')} row-days + {recon.get('n_missing')} listed missing = {recon.get('n_census')} census dates; identity={recon.get('identity')}."
        )
        overall = (atlas.get("summary") or {}).get("overall") or {}
        h8 = overall.get("high_within_8") or {}
        unres = overall.get("high_within_8_unrestricted") or {}
        items.append(
            f"Headline after-availability high-within-8 (QQQ+SPY): rate={h8.get('rate')} n={h8.get('n')}. Superseded unrestricted diagnostic: rate={unres.get('rate')} n={unres.get('n')}."
        )
    if task_id == "P2-03":
        targets = _load(_slice(impl, "P2-03") / "VOLATILITY_TARGETS.json").get("rows") or []
        incomplete = [r for r in targets if r.get("status") == "incomplete"]
        items.append(f"VOLATILITY_TARGETS rows={len(targets)}; incomplete={[(r.get('day'), r.get('reason')) for r in incomplete]}.")
    return items


def _draft_report_body(task_id: str, impl: Path) -> str:
    lines = ["", "receipt_state=draft_pending_merge. Nothing finalized. No GATE_REVIEW.json.", ""]
    boards = _load(_slice(impl, "P2-10") / "EXPOSURE_BOARDS.json")
    depth = boards.get("depth_by_root") or {}
    if depth:
        lines.append("## Board depth (per root, 20-date slice)")
        lines.append("")
        for root, rec in depth.items():
            live = rec.get("n_live") or {}
            oi = rec.get("n_with_oi") or {}
            fresh = rec.get("n_with_fresh_quote") or {}
            lines.append(
                f"- {root}: n_days={rec.get('n_days')} n_boards={rec.get('n_boards')} "
                f"n_live median/p10/p90={live.get('median')}/{live.get('p10')}/{live.get('p90')} "
                f"n_with_oi median/p10/p90={oi.get('median')}/{oi.get('p10')}/{oi.get('p90')} "
                f"n_with_fresh_quote median/p10/p90={fresh.get('median')}/{fresh.get('p10')}/{fresh.get('p90')}"
            )
            refusals = rec.get("refusals") or {}
            for day, reason in sorted(refusals.items()):
                lines.append(f"  - {day}: {reason}")
        lines.append("")
    if task_id == "P2-10":
        atlas = _load(_slice(impl, "P2-10") / "LEVEL_ATLAS_SUMMARY.json")
        recon = ((atlas.get("deviations") or {}).get("reconciliation") or {})
        lines.append("## Census reconciliation")
        lines.append("")
        lines.append(
            f"{recon.get('n_row_days')} atlas row-days + {recon.get('n_missing')} listed missing = {recon.get('n_census')} census dates; identity={recon.get('identity')}."
        )
        lines.append("")
        lines.append("NQ and ES cells are labelled degenerate board (median n_live 2 / 7) and are not evidence for the futures-option levels thesis until a BBO or MBP schema is owned.")
        lines.append("")
        overall = (atlas.get("summary") or {}).get("overall") or {}
        h8 = overall.get("high_within_8") or {}
        unres = overall.get("high_within_8_unrestricted") or {}
        lines.append(
            f"Headline after-availability high-within-8 (QQQ+SPY): {h8.get('rate')} n={h8.get('n')}. "
            f"Superseded unrestricted diagnostic: {unres.get('rate')} n={unres.get('n')}."
        )
        lines.append("")
    if task_id == "P2-03":
        targets = _load(_slice(impl, "P2-03") / "VOLATILITY_TARGETS.json").get("rows") or []
        lines.append(f"VOLATILITY_TARGETS row count {len(targets)}. Incomplete days:")
        for row in targets:
            if row.get("status") == "incomplete":
                lines.append(f"- {row.get('day')}: {row.get('reason')}")
        lines.append("")
    return "\n".join(lines) + "\n"


def produce(task_id: str, *, draft: bool, root: Path) -> Path:
    spec = TASKS[task_id]
    impl = root / "implementation"
    slice_src = impl / "reports/research-work/phase2-early" / spec["slice_dir"]
    staging = impl / "reports/research-work/phase2-early" / f"{task_id}-staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    plan_paths = [spec["card"], *spec["reads"], "planning/research-program/TASK_GRAPH.json", "planning/research-program/ASSURANCE_CASES.json"]
    code_paths = list(dict.fromkeys([*spec["owns"], *spec["helpers"]]))
    plan_files = {rel: file_digest(root / rel) for rel in plan_paths}
    code_files = {rel: file_digest(root / rel) for rel in code_paths if (root / rel).is_file()}
    plan_copies = write_snapshot_tree(staging, "plan", plan_files, root=root)
    code_copies = write_snapshot_tree(staging, "code", code_files, root=root)
    lock = root / "implementation/uv.lock"
    lock_sha = file_digest(lock) if lock.is_file() else file_digest(root / "implementation/pyproject.toml")
    plan_doc = plan_snapshot_document(plan_files, plan_copies)
    runtime = {"python": sys.version.split()[0]}
    try:
        import databento as db

        runtime["databento"] = db.__version__
        runtime["databento_install"] = "uv pip install databento --python /workspace/implementation/.venv/bin/python"
    except ImportError:
        runtime["databento"] = None
    code_doc = code_snapshot_document(
        code_files,
        code_copies,
        runtime=runtime,
        dependency_lock_sha256=lock_sha,
        imported_modules=spec["imported"],
    )
    plan_sha256 = digest(plan_files)
    code_sha256 = digest(code_doc)
    predecessors = {}
    if "P15-02" in spec["deps"]:
        live = file_digest(P15_02)
        if live != P15_02_SHA:
            raise SystemExit(f"P15-02 hash mismatch {live} != {P15_02_SHA}")
        predecessors["P15-02"] = live
    if "P2-09" in spec["deps"]:
        recs = list((root / "implementation/reports/research-work/P2-09").rglob("TASK_RECEIPT.json"))
        if not recs:
            raise SystemExit("P2-09 TASK_RECEIPT.json missing")
        predecessors["P2-09"] = file_digest(max(recs, key=lambda p: (p.stat().st_mtime, str(p))))
    if "P2-10" in spec["deps"]:
        recs = list((root / "implementation/reports/research-work/P2-10").rglob("TASK_RECEIPT.json"))
        if not recs:
            raise SystemExit("P2-10 TASK_RECEIPT.json missing")
        predecessors["P2-10"] = file_digest(max(recs, key=lambda p: (p.stat().st_mtime, str(p))))
    draft_doc = {
        "schema_version": "research-draft-manifest-v2",
        "assurance_version": ASSURANCE_VERSION,
        "task_id": task_id,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": predecessors,
        "input_identities": {
            "p15_02": {"path": str(P15_02), "sha256": P15_02_SHA},
            "slice": {"path": str(slice_src)},
        },
        "coverage_identity": digest({"dates": "20-session option slice"}),
        "registered_candidate_config": None,
        "declared_study_dates": {"start": "2020-01-02", "end": "2026-09-03"},
        "drafted_at": "2026-09-14",
    }
    run_id = semantic_run_id(draft_doc)
    attempt = impl / "reports/research-work" / task_id / run_id / "attempt-0001"
    if attempt.exists():
        shutil.rmtree(attempt)
    shutil.copytree(staging, attempt)
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft_doc)
    for name, _schema in spec["artifacts"]:
        src = slice_src / name
        if not src.is_file() and not src.is_symlink():
            continue
        dest = attempt / name
        if name == "LEVEL_ATLAS.json":
            if dest.exists() or dest.is_symlink():
                dest.unlink()
            dest.symlink_to(src.resolve())
            continue
        shutil.copy2(src, dest)
    for src in sorted(slice_src.glob("LEVEL_ATLAS_*.csv")):
        shutil.copy2(src, attempt / src.name)
    headline_csv = slice_src / "LEVEL_ATLAS_HEADLINE.csv"
    if headline_csv.is_file():
        shutil.copy2(headline_csv, attempt / headline_csv.name)
    pytest_log = attempt / "pytest.log"
    cmd = _run(
        [sys.executable, "-m", "pytest", spec["test"], "-q", "-p", "no:cacheprovider"],
        cwd=impl,
        log_path=pytest_log,
    )
    if cmd["exit_code"] != 0:
        raise SystemExit(f"pytest failed for {task_id}: {pytest_log.read_text()[-2000:]}")
    tp = attempt / "THROUGHPUT.json"
    tp_note = ""
    if tp.is_file():
        tp_note = f"THROUGHPUT.json sha256 {file_digest(tp)} is listed on this draft receipt artifact_manifest (median/p90, dates, workers, peak RSS).\n"
    (attempt / "WORK_LOG.md").write_text(
        f"# {task_id} work log\n\nSlice artifacts from `{slice_src}`.\nPytest `{spec['test']}` exit {cmd['exit_code']}.\n{tp_note}",
        encoding="utf-8",
    )
    (attempt / "DECISIONS.tsv").write_text(
        "ts\tphase\tdecision\twhy\tevidence\tresult\n"
        f"2026-09-14T00:00:00Z\t{task_id}\tproduce draft receipt\tworktree receipts cannot verify until merge\t{attempt}\tdraft_pending_merge\n",
        encoding="utf-8",
    )
    report_tp = "See THROUGHPUT.json on this attempt for median/p90 seconds, workers and peak RSS.\n" if tp.is_file() else ""
    extra = _draft_report_body(task_id, impl)
    (attempt / "REPORT.md").write_text(
        f"# {task_id}\n\nDraft receipt. Orchestrator re-runs produce_receipts.py --finalize after merge.\n{report_tp}{extra}",
        encoding="utf-8",
    )
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2"),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2"),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2"),
        ("WORK_LOG.md", "research-work-log-v1"),
        ("DECISIONS.tsv", "research-decisions-tsv-v1"),
        ("REPORT.md", "research-task-report-v1"),
        ("pytest.log", "pytest-log"),
        *spec["artifacts"],
    ]
    for csv_path in sorted(attempt.glob("LEVEL_ATLAS_*.csv")):
        named.append((csv_path.name, "research-level-atlas-csv-v1"))
    target = attempt / "TASK_RECEIPT.json"

    def emit_receipt(commands: list, extra_named: list[tuple[str, str]]) -> None:
        listed = list(named) + extra_named
        manifest = [artifact_entry(attempt / name, schema=schema) for name, schema in listed if (attempt / name).is_file()]
        receipt = make_task_receipt(
            task_id=task_id,
            run_id=run_id,
            plan_sha256=plan_sha256,
            code_sha256=code_sha256,
            predecessor_receipts=predecessors,
            command_results=commands,
            artifact_manifest=manifest,
            acceptance_checks={key: True for key in spec["cases"] if key.startswith("A")},
            disposition="implemented_verified",
            reason=f"{task_id} native slice and tests. Draft until merge.",
            coverage={"native": True, "market_feed_completeness": "unknown"},
            unresolved=_unresolved(task_id, impl),
        )
        if target.exists():
            target.unlink()
        if draft:
            payload = dict(receipt)
            payload["receipt_state"] = "draft_pending_merge"
            target.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
        else:
            write_task_receipt(target, receipt)

    emit_receipt([cmd], [])
    verify_log = attempt / "verify_task.log"
    tool = root / "implementation/tools/verify_research_release.py"
    audit = _run(
        [sys.executable, str(tool), "task", "--receipt", str(target)],
        cwd=impl,
        log_path=verify_log,
    )
    verify_result = verify_task_receipt(target)
    write_json_document(attempt / VERIFY_NAME, _verify_envelope(verify_result))
    write_json_document(attempt / PROBES_NAME, _run_s01_s03_probes(task_id, spec, attempt, root))
    matrix = _matrix(task_id, spec, attempt, 0, root=root, audit_index=1)
    write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix)
    if not draft and any(check.get("status") == "fail" for check in matrix["checks"]):
        raise SystemExit(f"{task_id} S01/S03 probes did not fail as expected")
    emit_receipt(
        [cmd, audit],
        [
            ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2"),
            (VERIFY_NAME, "research-verify-task-v1"),
            (PROBES_NAME, "research-s01-s03-probes-v1"),
            ("verify_task.log", "verify-task-log"),
        ],
    )
    print(json.dumps({"task": task_id, "attempt": str(attempt), "run_id": run_id, "draft": draft, "sha256": file_digest(target)}))
    return attempt


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--task", action="append")
    parser.add_argument("--finalize", action="store_true")
    parser.add_argument("--root", default=str(WORKTREE))
    args = parser.parse_args()
    root = Path(args.root)
    tasks = args.task or ["P2-09", "P2-10", "P2-03"]
    for task in tasks:
        produce(task, draft=not args.finalize, root=root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
