#!/usr/bin/env python3
"""Validate the plan graph, generated runbooks and local documentation links."""
from __future__ import annotations

import hashlib
import ast
import argparse
import importlib.util
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def prose(text: str) -> str:
    result = []
    fenced = False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
            result.append("")
        elif not fenced:
            result.append(line)
    return "\n".join(result)


def inline_targets(text: str):
    start = 0
    while True:
        mark = text.find("](", start)
        if mark < 0:
            return
        index, depth = mark + 2, 1
        first = index
        while index < len(text) and depth:
            char = text[index]
            if char == "\\":
                index += 2
                continue
            depth += (char == "(") - (char == ")")
            index += 1
        if depth == 0:
            yield text[first:index - 1]
        start = max(index, first + 1)


def anchors(path: Path) -> set[str]:
    content = prose(path.read_text())
    result = set(re.findall(r'\bid=["\']([^"\']+)["\']', content))
    seen = Counter()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", content, re.M):
        heading = re.sub(r"<[^>]+>", "", heading)
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        slug = re.sub(r"[^\w\-\s]", "", heading.lower()).replace(" ", "-")
        count = seen[slug]
        seen[slug] += 1
        result.add(slug if not count else f"{slug}-{count}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authoring-scope", action="store_true",
                        help="Also require no tracked implementation/protected edits in this documentation change")
    args = parser.parse_args()
    errors = []
    graph_path = ROOT / "planning/research-program/TASK_GRAPH.json"
    graph = json.loads(graph_path.read_text())
    tasks = graph["tasks"]
    indexed = {task["id"]: task for task in tasks}
    assurance_path = ROOT / "planning/research-program/ASSURANCE_CASES.json"
    assurance = json.loads(assurance_path.read_text())
    case_ids = [case["id"] for case in assurance["cases"]]
    if case_ids != [f"S{i:02d}" for i in range(1, 33)]:
        errors.append("expected the 32 unique assigned silent-failure cases S01-S32")
    if graph.get("assurance_version") != assurance["assurance_version"]:
        errors.append("graph and failure-case assurance versions differ")
    assignments = {task_id: [] for task_id in indexed}
    for case in assurance["cases"]:
        if len(case["tasks"]) != len(set(case["tasks"])) or not case["tasks"]:
            errors.append(f"empty/duplicate case assignment: {case['id']}")
        for field in ("title", "probe", "expected", "evidence"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                errors.append(f"case lacks concrete {field}: {case['id']}")
        for task_id in case["tasks"]:
            if task_id not in assignments:
                errors.append(f"unknown assurance task: {case['id']} {task_id}")
            else:
                assignments[task_id].append(case["id"])
    fixed = assurance["foundation_checker"]
    checker_path = ROOT / fixed["path"]
    if not checker_path.is_file() or hashlib.sha256(checker_path.read_bytes()).hexdigest() != fixed["sha256"]:
        errors.append("fixed independent foundation checker differs from its accepted pin")
    if fixed["required_case_count"] != 27:
        errors.append("foundation independent case count changed without a checker amendment")
    required_common = {"DRAFT_MANIFEST.json", "PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json",
                       "EVIDENCE_MATRIX.json", "WORK_LOG.md", "DECISIONS.tsv", "REPORT.md"}
    if set(graph.get("required_task_artifacts", [])) != required_common:
        errors.append("common task evidence artifacts are missing or changed")
    if len(indexed) != len(tasks) or len(tasks) != 46:
        errors.append("task IDs/count must be 46 unique planned tasks")
    active, visited = set(), set()

    def visit(task_id):
        if task_id in active:
            errors.append(f"dependency cycle: {task_id}")
            return
        if task_id in visited:
            return
        if task_id not in indexed:
            errors.append(f"unknown dependency: {task_id}")
            return
        active.add(task_id)
        for dep in indexed[task_id]["dependencies"]:
            visit(dep)
        active.remove(task_id)
        visited.add(task_id)

    for task in tasks:
        visit(task["id"])
        card = ROOT / task["path"]
        if not card.exists():
            errors.append(f"missing task card: {task['path']}")
            continue
        content = card.read_text()
        keys = re.findall(r"^- \[ \] (A\d\d):", content, re.M)
        if keys != task["required_acceptance_keys"]:
            errors.append(f"acceptance keys differ: {task['id']} {keys}")
        if task["status"] != "planned" or "not started by this planning task" not in content:
            errors.append(f"unexpected implementation status: {task['id']}")
        for ref in task["reads"]:
            if not (ROOT / ref).is_file():
                errors.append(f"missing required read: {task['id']} {ref}")
        if "planning/research-program/PSTACK_EXECUTION.md" not in task["reads"]:
            errors.append(f"missing pstack execution contract: {task['id']}")
        for ref in ("planning/research-program/ASSURANCE.md", "planning/research-program/SILENT_FAILURES.md"):
            if ref not in task["reads"]:
                errors.append(f"missing assurance read: {task['id']} {ref}")
        if task.get("assurance_cases") != assignments[task["id"]] or not {"S01", "S02", "S03"} <= set(assignments[task["id"]]):
            errors.append(f"silent-failure assignments differ or omit universal checks: {task['id']}")
        if not {"A07", "A08"} <= set(keys):
            errors.append(f"task lacks evidence/failure acceptance gates: {task['id']}")
        required_line = "Assigned cases: **" + ", ".join(assignments[task["id"]]) + "**"
        if required_line not in content:
            errors.append(f"card omits its assigned case IDs: {task['id']}")
        for owned in task["owns"]:
            if f"`/workspace/{owned}`" not in content:
                errors.append(f"task card omits an owned path: {task['id']} {owned}")
    if "P15-20" not in indexed["P2-00"]["dependencies"]:
        errors.append("Phase 2 entry gate is missing the complete Phase 1.5 release")
    expected = {"phase-1-5": 21, "phase-2": 25}
    if Counter(t["phase"] for t in tasks) != expected:
        errors.append("phase task counts differ")
    by_phase_group = Counter((t["phase"], t["subphase"]) for t in tasks)
    if len(by_phase_group) != 17:
        errors.append("expected 17 subphase runbooks")
    coordinator = graph.get("coordinator_artifacts", {})
    expected_groups = {f"{phase}/{group}" for phase, group in by_phase_group}
    if set(coordinator) != expected_groups:
        errors.append("every subphase must have a coordinator artifact declaration")
    for group, artifacts in coordinator.items():
        if not {"SUBPHASE_RECEIPT.json", "GATE_REVIEW.json"} <= set(artifacts):
            errors.append(f"subphase lacks candidate/review outputs: {group}")
    for task in tasks:
        if {"SUBPHASE_RECEIPT.json", "GATE_REVIEW.json", "PHASE1_5_RELEASE.json", "PHASE2_RELEASE.json"} & set(task["artifacts"]):
            errors.append(f"task output creates a circular coordinator receipt dependency: {task['id']}")

    def ancestors(task_id):
        result = set()
        todo = list(indexed[task_id]["dependencies"])
        while todo:
            dep = todo.pop()
            if dep not in result and dep in indexed:
                result.add(dep)
                todo.extend(indexed[dep]["dependencies"])
        return result

    owners = {}
    for task in tasks:
        for path in task["owns"]:
            if path == fixed["path"]:
                errors.append(f"implementation task may not edit its independent checker: {task['id']}")
            for prior in owners.get(path, []):
                if prior not in ancestors(task["id"]) and task["id"] not in ancestors(prior):
                    errors.append(f"concurrent write ownership: {prior}, {task['id']}: {path}")
            owners.setdefault(path, []).append(task["id"])
            if path.startswith(("sources/", "archive/", "planning/phase-1-fable/", "planning/phase-1-from-scratch/")):
                errors.append(f"protected task write path: {task['id']} {path}")

    build = ROOT / "tools/build_research_plan_bundles.py"
    spec = importlib.util.spec_from_file_location("research_plan_bundles", build)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generated = module.products()
    for path, value in generated.items():
        if not path.exists() or path.read_text() != value:
            errors.append(f"stale generated document: {path.relative_to(ROOT)}")
    prompt_count = 0
    for path, content in generated.items():
        if path.name != "PROMPTS.md" and path.parent.name != "tasks":
            continue
        if path.parent.name == "tasks":
            content = content.split("## Copyable worker prompt\n", 1)[-1]
        blocks = re.findall(r"```text\n(.*?)\n```", content, re.S)
        if not blocks:
            errors.append(f"no copyable prompts: {path.relative_to(ROOT)}")
        for block in blocks:
            prompt_count += 1
            if not block.startswith("/poteto-mode new task. "):
                errors.append(f"prompt omits pstack new-task entry: {path.relative_to(ROOT)}")
            if "PSTACK_EXECUTION" not in block:
                errors.append(f"prompt omits project execution contract: {path.relative_to(ROOT)}")
            for required in ("ASSURANCE.md", "EVIDENCE_MATRIX.json", "GATE_REVIEW.json"):
                if required not in block:
                    errors.append(f"prompt omits {required}: {path.relative_to(ROOT)}")
            if re.search(r"/(feature|hillclimb|autonomous-run)\b", block):
                errors.append(f"invented playbook slash command: {path.relative_to(ROOT)}")
        if path.parent.name == "tasks":
            if "parent Grok model for every pstack role" not in content:
                errors.append(f"worker model override missing: {path.relative_to(ROOT)}")
            if "No nested delegation" not in content:
                errors.append(f"worker delegation bound missing: {path.relative_to(ROOT)}")
    if prompt_count != 72:
        errors.append(f"expected 72 copyable pstack prompts, found {prompt_count}")
    for (phase, group) in by_phase_group:
        runbook = ROOT / "planning" / phase / "subphases" / group / "RUNBOOK.md"
        content = generated[runbook]
        assigned = {case_id for task in tasks if task["phase"] == phase and task["subphase"] == group
                    for case_id in assignments[task["id"]]}
        embedded = set(re.findall(r"^### (S\d\d) — ", content, re.M))
        if embedded != assigned:
            errors.append(f"runbook cases differ from its task assignment: {phase}/{group}")
        if "separately hashed GATE_REVIEW.json" not in content or "## Evidence and failure checks" not in content:
            errors.append(f"subphase omits shared assurance and independent closure: {phase}/{group}")

    docs = list((ROOT / "wiki").glob("*.md"))
    for folder in ("research-program", "phase-1-5", "phase-2"):
        docs.extend((ROOT / "planning" / folder).rglob("*.md"))
    docs += [ROOT / p for p in ("README.md", "AGENTS.md", "planning/README.md", "planning/ROADMAP.md",
                               "planning/phase-1-live/PHASE.md", "planning/phase-1-live/NEXT_PHASES_DISCUSSION.md",
                               "planning/phase-1-live/PHASE_1_5_RULE_DISCOVERY_HANDOFF.md")]
    anchor_cache = {}
    links_checked = 0
    for doc in docs:
        text = prose(doc.read_text())
        if len(re.findall(r"^# ", text, re.M)) != 1:
            errors.append(f"expected one H1: {doc.relative_to(ROOT)}")
        targets = list(inline_targets(text))
        targets.extend(re.findall(r"^\[[^\]]+\]:\s*(.+)$", text, re.M))
        for raw in targets:
            target = raw.strip()
            if target.startswith("<") and ">" in target:
                target = target[1:target.index(">")]
            target = re.split(r'\s+["\']', target, maxsplit=1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "data:", "codex:")):
                continue
            target = unquote(target).replace("\\(", "(").replace("\\)", ")")
            path_part, _, fragment = target.partition("#")
            path_part = re.sub(r":\d+$", "", path_part)
            path = (doc.parent / path_part).resolve() if path_part else doc.resolve()
            links_checked += 1
            if not path.exists():
                errors.append(f"missing local link: {doc.relative_to(ROOT)} -> {raw}")
            elif fragment and path.is_file() and path.suffix == ".md":
                if path not in anchor_cache:
                    anchor_cache[path] = anchors(path)
                if fragment not in anchor_cache[path]:
                    errors.append(f"missing anchor: {doc.relative_to(ROOT)} -> {raw}")
    alias = ROOT / "planning/phase-1-live/wiki"
    if not alias.is_symlink() or alias.resolve() != ROOT / "wiki":
        errors.append("wiki compatibility symlink is missing or wrong")

    vectors = json.loads((ROOT / "planning/research-program/fixtures/reference_vectors.json").read_text())
    ast.parse((ROOT / "planning/research-program/TYPE_REFERENCE.py").read_text())
    expected_ids = {"gk_range", "bsm_atm", "yz_constant_returns", "costed_long", "oi_prefix_clipping"}
    vector_ids = {v["id"] for v in vectors["cases"]}
    if not expected_ids <= vector_ids:
        errors.append("missing core reference vectors")
    values = {v["id"]: v["expected"] for v in vectors["cases"]}
    if not math.isclose(values["gk_range"]["variance"], .5 * math.log(110 / 90) ** 2, abs_tol=1e-12):
        errors.append("GK reference vector mismatch")
    if not math.isclose(values["bsm_atm"]["price"], 7.965567455405804, abs_tol=1e-10):
        errors.append("BSM reference vector mismatch")
    if values["costed_long"]["net_dollars"] != 25 or values["oi_prefix_clipping"]["clipped_prefix"] != [0, 10]:
        errors.append("execution/OI reference vector mismatch")

    changed = subprocess.run(["git", "diff", "--name-only", "--", "implementation", "archive", "sources",
                              "planning/phase-1-fable", "planning/phase-1-from-scratch"],
                             cwd=ROOT, check=True, text=True, capture_output=True).stdout.splitlines()
    # This is a documentation-only authoring check, not a constraint on future implementation.
    if args.authoring_scope and changed:
        errors.append("documentation change modified protected/baseline tracked paths: " + ", ".join(changed))
    summary = {"schema": "research-plan-doc-check-v1", "status": "pass" if not errors else "fail",
               "task_cards": len(tasks), "subphases": len(by_phase_group),
               "generated_files": sum(path.name in {"README.md", "PROMPTS.md", "RUNBOOK.md"} for path in generated),
               "task_prompt_sections": sum(path.parent.name == "tasks" for path in generated),
               "pstack_copyable_prompts": prompt_count,
               "silent_failure_cases": len(case_ids),
               "assurance_task_assignments": sum(map(len, assignments.values())),
               "subphases_with_review_gate": len(coordinator),
               "fixed_foundation_cases": fixed["required_case_count"],
               "markdown_files": len(docs), "local_links_checked": links_checked,
               "reference_vectors": len(vectors["cases"]), "errors": errors}
    print(json.dumps(summary, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
