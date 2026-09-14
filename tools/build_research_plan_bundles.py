#!/usr/bin/env python3
"""Build coordinator bundles and worker prompt sections from canonical plans."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "planning/research-program/TASK_GRAPH.json"
PHASES = ("phase-1-5", "phase-2")
PSTACK_CONTRACT = "planning/research-program/PSTACK_EXECUTION.md"
ASSURANCE_CONTRACT = "planning/research-program/ASSURANCE.md"
CASEBOOK = ROOT / "planning/research-program/SILENT_FAILURES.md"
REPAIR = ROOT / "planning/research-program/FOUNDATION_REPAIR.md"


def failure_casebook(task_ids: set[str] | None = None) -> str:
    registry = json.loads((ROOT / "planning/research-program/ASSURANCE_CASES.json").read_text())
    lines = ["# Silent failure checks", "",
             "Generated from [ASSURANCE_CASES.json](/workspace/planning/research-program/ASSURANCE_CASES.json). "
             "These are required prevention cases, not claims that every listed defect was found in current code. "
             "Use [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) for evidence and closure rules.", "",
             "Reuse a bound shared test/evidence artifact when it proves the same invariant on the same code and inputs. "
             "Run task-specific native/behavior cases where scope differs. Do not duplicate a test solely to increase the test count. "
             "An inherited check must name its current artifact/hash and applicability; a stale pass cannot be inherited.", ""]
    if task_ids is not None:
        lines += ["This runbook includes only cases assigned to: " + ", ".join(sorted(task_ids)) + ".", ""]
    for case in registry["cases"]:
        if task_ids is not None and not set(case["tasks"]) & task_ids:
            continue
        lines += [f"## {case['id']} — {case['title']}", "",
                  "Assigned tasks: " + ", ".join(case["tasks"]) + ".", "",
                  "**Probe:** " + case["probe"], "",
                  "**Expected:** " + case["expected"], "",
                  "**Evidence:** " + case["evidence"], ""]
    return "\n".join(lines)


def prompt_kind(task: dict) -> str:
    if task["id"] in {"P15-17", "P15-18", "P15-19", "P2-23"}:
        return "finite_experiment"
    if task["id"] in {"P15-20", "P2-24"}:
        return "release_verification"
    return "feature"


def worker_prompt(task: dict) -> str:
    kind = prompt_kind(task)
    intent = {
        "feature": "Implement this feature",
        "finite_experiment": "Run this finite registered research experiment",
        "release_verification": "Complete this planned phase-release verification and replay",
    }[kind]
    lines = [f"/poteto-mode new task. {intent}: {task['id']} — {task['title']}.",
             f"Read /workspace/{task['path']} and /workspace/{PSTACK_CONTRACT}. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.",
             "Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.",
             "Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.",
             f"Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and {', '.join(task['required_acceptance_keys'])} checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.",
             "Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there."]
    if task["id"] == "P15-00":
        lines[2] = ("Use the coordinator's actual working root, accepted Phase 1 report/input identities, code identity and new run root. This bootstrap task creates the draft/frozen manifest templates and initial receipts; do not wait for future task artifacts or a verifier that P15-01 has not built yet.")
        lines[-1] = ("Bootstrap exception: implement and check the serializer, baseline identities, types and manifest template now. Return the real TASK_RECEIPT.json plus local check evidence to the foundation coordinator. P15-01 creates the verifier and must verify this receipt before the subphase can close; do not claim that future command ran. Keep the decision trail and runtime todos in the run's WORK_LOG.md/DECISIONS.tsv.")
    if task["id"] == "P15-01":
        lines.append("Bootstrap dependency: inspect P15-00's actual artifacts and local checks, implement this task's verifier, then verify P15-00 retrospectively before verifying your own receipt. Return foundation gate inputs to the coordinator, which alone writes SUBPHASE_RECEIPT.json.")
    lines.append(f"Apply /workspace/{ASSURANCE_CONTRACT} and the card's assigned silent-failure cases: {', '.join(task['assurance_cases'])}. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.")
    if kind == "finite_experiment":
        lines.append("Use the specified finite-experiment route, not pstack's agent/prompt Eval protocol or an open-ended Hillclimb. Reconcile every registered trial; a verified negative or inconclusive research result is valid. Do not expand the search to force a winner.")
    lines.append("Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.")
    return "\n".join(lines)


def worker_section(task: dict) -> str:
    return ("## Copyable worker prompt\n\n"
            "Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.\n\n"
            "```text\n" + worker_prompt(task) + "\n```\n")


def absolute_links(text: str, source: Path) -> str:
    def convert(match: re.Match[str]) -> str:
        target = match.group(1)
        if target.startswith(("/", "http:", "https:", "mailto:", "data:")):
            return match.group(0)
        path, mark, fragment = target.partition("#")
        resolved = (source.parent / path).resolve() if path else source
        return f"]({resolved}{mark}{fragment})"

    return re.sub(r"\]\(([^\s)]+)\)", convert, text)


def embed(source: Path, overrides: dict[Path, str]) -> str:
    original = overrides.get(source)
    if original is None:
        original = source.read_text()
    if source.suffix == ".py":
        text = "# Type declaration blueprint\n\n```python\n" + original + "\n```\n"
    else:
        text = absolute_links(original, source)
    # Demote prose headings without changing Python comments in fenced examples.
    result = []
    fenced = False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and re.match(r"^#{1,5} ", line):
            line = "#" + line
        result.append(line)
    return f"Canonical source: [{source.name}]({source}).\n\n" + "\n".join(result)


def products() -> dict[Path, str]:
    graph = json.loads(GRAPH.read_text())
    outputs: dict[Path, str] = {CASEBOOK: failure_casebook()}
    for task in graph["tasks"]:
        card = ROOT / task["path"]
        content = card.read_text()
        marker = "## Copyable worker prompt\n"
        if content.count(marker) != 1:
            raise ValueError(f"Expected one worker prompt section: {card}")
        outputs[card] = content.split(marker)[0] + worker_section(task)
    for phase in PHASES:
        selected = [t for t in graph["tasks"] if t["phase"] == phase]
        groups = sorted({t["subphase"] for t in selected})
        title = "Phase 1.5" if phase == "phase-1-5" else "Phase 2"
        prompt_lines = [f"# {title} — copyable coordinator prompts", "",
                        "These prompts start implementation when you send them. The pack itself is a specification; no task is marked implemented by its creation.", "",
                        "pstack is included in the user's Grok build. Copy the entire block, starting with /poteto-mode new task. No separate setup prompt is required. Send one subphase prompt to one Grok task; complete and verify it before the next.", "",
                        "The user sends one coordinator prompt per subphase (17 subphases across both packs). Worker prompts are internal coordinator dispatch material. Resume/review/repair/pause blocks are alternatives for those situations, not additional prompts the user must send for a normal subphase run.", "",
                        f"The [pstack execution contract](/workspace/{PSTACK_CONTRACT}) defines routing, Grok-only roles, worker briefs, local scope and honest stop rules. Each RUNBOOK includes it. The installed router chooses supporting skills; the prompts do not hard-code a skill chain.", "",
                        "Use one coordinator per subphase. A shared checkout has one code writer at a time; independent read-only work may run alongside it. Keep the same declared data-process parallelism and resource limits.", ""]
        summary = []
        if phase == "phase-1-5":
            prompt_lines += ["## Current entry: repair 00-foundation", "",
                             "The 2026-09-14 independent audit rejected the original completion claim. "
                             "Use this repair block before 01-native-and-outcomes. Preserve the original reports. "
                             f"[Findings and repair instructions]({REPAIR}).", "",
                             REPAIR.read_text().split("<!-- copyable-repair-start -->\n", 1)[1].split("\n<!-- copyable-repair-end -->", 1)[0], ""]
        for index, group in enumerate(groups):
            pending = {t["id"]: t for t in selected if t["subphase"] == group}
            members = []
            while pending:
                ready = sorted(t for t in pending if not (set(pending[t]["dependencies"]) & set(pending)))
                if not ready:
                    raise ValueError(f"Cyclic subphase dependencies: {phase}/{group}")
                for task_id in ready:
                    members.append(pending.pop(task_id))
            runbook = ROOT / "planning" / phase / "subphases" / group / "RUNBOOK.md"
            own_ids = {t["id"] for t in members}
            external = sorted({dep for t in members for dep in t["dependencies"] if dep not in own_ids})
            prior = groups[index - 1] if index else ("Phase 1.5 final release" if phase == "phase-2" else "accepted Phase 1 census")
            needed = [PSTACK_CONTRACT, ASSURANCE_CONTRACT, str(CASEBOOK.relative_to(ROOT))]
            if phase == "phase-1-5" and group == "00-foundation":
                needed.append(str(REPAIR.relative_to(ROOT)))
            for task in members:
                for ref in task["reads"]:
                    # Source method definitions stay canonical and are worker reads.
                    # Bundle the executable contracts, not the whole 191-page wiki.
                    if ref.startswith("planning/") and ref not in needed:
                        needed.append(ref)
            source_paths = [ROOT / ref for ref in needed] + [ROOT / t["path"] for t in members]
            source_overrides = {**outputs, CASEBOOK: failure_casebook(own_ids)}
            digest = hashlib.sha256()
            for source in source_paths:
                digest.update(str(source.relative_to(ROOT)).encode())
                digest.update(b"\0")
                digest.update(source_overrides[source].encode() if source in source_overrides else source.read_bytes())
                digest.update(b"\0")
            header = [f"# {title} / {group} — coordinator runbook", "",
                      "Status: **planned; not implemented by this planning task**. Generated from canonical contracts and task cards. Edit those sources, then rebuild; do not edit this bundle independently.", "",
                      f"Source content SHA256: `{digest.hexdigest()}`.", "",
                      f"Previous gate: **{prior}**. External task dependencies: {', '.join(external) or 'none beyond the accepted baseline'}. Read and verify their actual receipts before implementation.", "",
                      "## Coordinator work order", "",
                      "Enter through /poteto-mode new task and run only this bounded subphase to its verification predicate. Match the installed playbook, copy its steps into runtime todos and record explicit skip reasons. Apply the included Grok-only model and host-capability overrides to all routed skills. A large-task figure-it-out route must use this existing runbook, not invent a new research plan.", "",
                      "Implement only the tasks listed below, in dependency order. Start with one verified vertical slice. Delegate bounded cards with the complete brief in PSTACK_EXECUTION; a shared checkout has one code writer at a time. At most three live Grok/poteto agents including the coordinator; unavailable workers mean sequential execution. The coordinator reviews and integrates shared schemas/runners and alone writes SUBPHASE_RECEIPT.json.", "",
                      "Read workspace AGENTS.md. The executable contracts and task cards are included below. Source method wiki pages linked by a task are additional focused worker reads; they retain the precise author predicates. Do not reread the whole archive or invent alternative formulas.", "",
                      "The native slice, numerical checks, coverage, future perturbation, actual output inspection and immutable receipts are part of the task. A negative/inconclusive research result is valid; missing implementation is not. Preserve prior evidence and all unsuccessful trials. Do not start the next subphase automatically.", "",
                      "| Task | Dependencies | Canonical card |", "| --- | --- | --- |"]
            for task in members:
                header.append(f"| {task['id']} — {task['title']} | {', '.join(task['dependencies']) or 'bootstrap'} | [Task](/workspace/{task['path']}) |")
            header += ["", "## Subphase completion", "",
                       "Collect verified task receipts for every listed task. Record acceptance checks, hashes, native date/coverage identities, schema versions, shared-file integration diffs, runtime and remaining input limits. Write SUBPHASE_RECEIPT.json under a new immutable report run and verify it with verify_research_release.py subphase. The foundation coordinator first creates that verifier and retrospectively verifies its bootstrap task. Then apply ASSURANCE.md: inspect every EVIDENCE_MATRIX.json and assigned failure case, run required independent checks, and write a separately hashed GATE_REVIEW.json referencing the immutable candidate receipt. Closure requires receipt verification plus a matching passing review with no unresolved correctness, causality or integrity findings. Valid controls must pass as well as invalid controls fail.", "",
                       "Return the user a concise completion report, both required family tables when reporting family results, real evidence links, limitations and the next eligible prompt. A subphase gate closes only this subphase. Phase 2 requires all of Phase 1.5 closed first.", ""]
            outputs[runbook] = "\n".join(header) + "\n\n".join(embed(p, source_overrides) for p in source_paths) + "\n"
            prompt_lines += [f"## {group}", "", "```text",
                            f"/poteto-mode new task. Implement {title} subphase {group} in /workspace.",
                            f"Read /workspace/AGENTS.md and {runbook}.",
                            "This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.",
                            f"Verify the previous gate ({prior}) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.",
                            "Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.",
                            "State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.",
                            "Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.",
                            "Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.",
                            "This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.",
                            "```", ""]
            summary.append((group, members, runbook))
        prompt_lines += ["## Resume an interrupted subphase", "",
                         "Use this in the existing subphase task. In a fresh task, append the actual RUNBOOK path, run-root path and prior WORK_LOG/receipt paths from its handoff.", "", "```text",
                         "/poteto-mode new task. Take over the interrupted subphase and resume from its existing runbook, WORK_LOG.md, decision trail and immutable manifests. Use Session pickup to establish the resume point, then route the remaining work for execution. Read PSTACK_EXECUTION.md from the runbook; keep all roles on the parent Grok model and the same bounded ownership.",
                         "Verify inherited artifact hashes and distinguish done from pending using ASSURANCE.md, EVIDENCE_MATRIX.json and the matching GATE_REVIEW.json. Reuse successful shards and retain failed attempts; finish missing work under the same frozen configuration. Do not invent dates, drop slow/negative cases or overwrite reports. Reconcile defects in bounded repairs and rerun affected silent-failure cases. A real contract amendment requires a new plan/run identity and explicit supersession; obsolete receipts cannot authorize downstream work.",
                         "Keep going until the existing subphase completion predicate verifies, or return an evidenced incomplete/blocking disposition under its stop rules. Return actual receipts, decision trail and the next eligible prompt. Local scope only; no automatic later phase or shipping.", "```", "",
                         "## Independent review prompt", "", "```text",
                         "/poteto-mode new task. Review the completed subphase using the RUNBOOK and receipt paths in the supplied completion handoff. This is a read-only investigation. Use /interrogate as the skeptical-review override; do not change implementation or accepted evidence. Read the runbook's PSTACK_EXECUTION contract and keep every review role on the parent Grok model. A fresh same-model review is not cross-model evidence.",
                         "Read actual code and artifacts before the author summary. Apply ASSURANCE.md and every task assigned silent-failure case. Reproduce adversarial controls, independently recalculate a central result, trace a native output and inspect EVIDENCE_MATRIX.json. Check attribution, nested availability, actual predictor matrices, native coverage and zero days, trial/job reconciliation, numerical fixtures, recursive dependency hashes and downstream claims. Review maintainability and decision trails separately. Preserve evidence; use isolated temporary outputs and the fixed independent checks where required, including valid controls.",
                         "Done means GATE_REVIEW.json under ASSURANCE.md with a pass, issues or blocked verdict bound to actual candidate receipt/code/evidence hashes, covering every task, findings with reproductions and explicit unverified checks. No unresolved correctness/causality/integrity issue may pass. Test counts or attractive charts alone are insufficient. Return the report to the coordinator; no fixes, PRs or shipping in this review task.", "```", "",
                         "## Repair a failed check", "",
                         "Append the failing command, exact error and affected task/runbook paths from the run's receipt.", "", "```text",
                         "/poteto-mode new task. Reproduce the reported verification failure first, then fix its root cause within the affected task's ownership and verify it. Read its card and PSTACK_EXECUTION.md. Keep all roles on the parent Grok model. Use the Bug fix playbook; preserve the frozen research contract and all failed evidence.",
                         "Apply ASSURANCE.md and assigned silent-failure cases. Done means the discriminating reproduction fails before repair and passes after it, affected native/causal checks pass, the new immutable task receipt verifies and a matching GATE_REVIEW.json passes. Return EVIDENCE_MATRIX.json, commands, evidence and explicitly invalidated downstream artifacts. Preserve prior attempts; do not weaken or edit fixed checks, redesign the model grid or start unrelated work.", "```", "",
                         "## Pause safely", "", "```text",
                         "/poteto-mode new task. Pause this subphase safely at the next atomic boundary. Preserve existing files, manifests, completed shards and failed attempts. Stop further dispatch, reconcile active workers and write the exact done/pending state, code identity, receipt paths and next resume command into this run's WORK_LOG.md and decision trail. Apply PSTACK_EXECUTION.md and ASSURANCE.md; preserve EVIDENCE_MATRIX.json and pending GATE_REVIEW.json findings. No PR, push, automatic history rewrite or fabricated completion. Return a durable resume handoff and leave the run incomplete when work remains.", "```", ""]
        outputs[ROOT / "planning" / phase / "PROMPTS.md"] = "\n".join(prompt_lines)
        readme = [f"# {title} implementation pack", "", "Status: **specified, not implemented by this planning task**.", "",
                  ("Reconstruct missing numerical rules and compare finite, explicitly attributed setup improvements. All Phase 1.5 work must close before Phase 2 implementation." if phase == "phase-1-5" else "Build intraday forecasts, native options updates and separately fitted context/method experts. Start only after the verified complete Phase 1.5 release."), "",
                  f"Start with [copyable prompts](/workspace/planning/{phase}/PROMPTS.md). Send the first eligible /poteto-mode new task block to Grok; pstack is already in the user's build. Each coordinator runbook includes its task cards, the [Grok/pstack execution contract](/workspace/{PSTACK_CONTRACT}) and applicable mathematical/data contracts. Workers additionally read their focused source wiki links.", "",
                  f"[Specification](/workspace/planning/{phase}/SPEC.md) · [Roadmap](/workspace/planning/ROADMAP.md) · [Execution contract](/workspace/planning/research-program/WORKFLOW.md) · [Machine-readable task graph](/workspace/planning/research-program/TASK_GRAPH.json).", "",
                  "## Subphases", "", "| Order | Subphase/runbook | Tasks | Exit evidence |", "| --- | --- | --- | --- |"]
        for index, (group, members, runbook) in enumerate(summary):
            readme.append(f"| {index} | [{group}]({runbook}) | {', '.join(t['id'] for t in members)} | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |")
        readme += ["", "## Operating rules", "",
                   "One coordinator owns a subphase. Workers get one bounded card and actual predecessor/run artifacts. The pstack router selects supporting skills; all roles inherit the parent Grok model. Default at most three live agents including the coordinator and one code writer per shared checkout. Dependency order governs task execution; shared integration and fresh review belong to the coordinator. Unavailable permitted workers mean sequential execution.", "",
                   "All source-independent thresholds, costs, numerical recipes and search limits are registered research defaults. Preserve baselines, complete no-opportunity days, missing data, ambiguous ordering and unsuccessful trials. Negative or low-support findings can close a correct experiment; missing code or unreconciled runs cannot.", "",
                   "The commands and proposed Python APIs in this pack are implementation requirements. This planning task has not created those research runners or executed their tests/censuses. Every task/subphase obeys ASSURANCE.md and its assigned silent-failure cases. A final release requires receipt verification, fixed independent checks and a matching passing GATE_REVIEW.json, plus both workspace-required family/audit tables.", "",
                   "## Document maintenance", "", "Canonical contracts and task-card requirements are the source of truth. The builder updates coordinator bundles and only the Copyable worker prompt section of each task card. The checker rejects stale prompts or missing pstack routing. From /workspace:", "", "```bash", "python tools/build_research_plan_bundles.py", "python tools/check_research_plan.py", "```", ""]
        outputs[ROOT / "planning" / phase / "README.md"] = "\n".join(readme)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = products()
    counts = {"generated_files": sum(path.name in {"README.md", "PROMPTS.md", "RUNBOOK.md"} for path in output),
              "task_prompt_sections": sum(path.parent.name == "tasks" for path in output)}
    mismatches = [str(path.relative_to(ROOT)) for path, value in output.items()
                  if not path.exists() or path.read_text() != value]
    if args.check:
        print(json.dumps({**counts, "stale": mismatches}))
        return 1 if mismatches else 0
    for path, value in output.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    print(json.dumps({**counts, "updated": len(mismatches)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
