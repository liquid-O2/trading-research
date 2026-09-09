"""Validate and import the exact durable plan; never write planning manifests."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import digest, file_digest


def unique(rows: list[dict], key: str, label: str) -> dict[str, dict]:
    result = {r[key]: r for r in rows}
    if len(result) != len(rows):
        raise IntegrityError(f"duplicate {label} ID")
    return result


@dataclass(frozen=True)
class ScopeEntry:
    id: str
    kind: str
    owner: str
    phase_or_clause: str
    definition_version: str
    dependency_ids: tuple[str, ...]
    definition: dict[str, Any]


class Scope:
    def __init__(self, manifest: dict, experiment_registry: dict,
                 component_registry: dict, contract_texts: dict[str, str]):
        # Copy caller-owned mutable objects before validating or hashing them.
        self.manifest = json.loads(json.dumps(manifest))
        self.experiments = json.loads(json.dumps(experiment_registry))
        self.components = json.loads(json.dumps(component_registry))
        self.contract_texts = dict(contract_texts)
        self.version = self.manifest["scope_version"]
        self._validate()
        self.entries = self._entries()

    @classmethod
    def load(cls, plan_root: Path, workspace: Path | None = None) -> Scope:
        plan_root = Path(plan_root).resolve()
        workspace = Path(workspace or plan_root.parents[1]).resolve()
        manifest = json.loads((plan_root / "review/implementation_scope.json").read_bytes())
        for name, expected in manifest["input_hashes"].items():
            declared = Path(name)
            try:
                relative = declared.relative_to("/workspace")
            except ValueError as exc:
                raise IntegrityError(f"input outside declared workspace: {name}") from exc
            path = (workspace / relative).resolve()
            if not path.is_relative_to(workspace) or path.is_relative_to(workspace / "archive"):
                raise IntegrityError(f"excluded source path: {name}")
            if not path.is_file() or file_digest(path) != expected:
                raise IntegrityError(f"stale definition/input hash: {name}")
        experiments = json.loads((plan_root / "review/third-review/experiment_registry.json").read_bytes())
        components = json.loads((plan_root / "review/component_registry.json").read_bytes())
        contracts = {}
        for id, card in components.items():
            relative = Path(card["path"]).relative_to("/workspace/planning/trading-model")
            lines = (plan_root / relative).read_text().splitlines()
            start = card["line"] - 1
            end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith("## ")), len(lines))
            contracts[id] = "\n".join(lines[start:end])
        return cls(manifest, experiments, components, contracts)

    def _validate(self) -> None:
        m = self.manifest
        if m.get("schema_version") != 1:
            raise IntegrityError("unsupported scope schema")
        if digest({k: v for k, v in m.items() if k != "scope_version"}) != self.version:
            raise IntegrityError("scope payload hash does not match scope_version")
        units = unique(m["units"], "id", "unit")
        source = unique(m["source_findings"], "id", "source")
        registries = {
            "requirements": unique(m["requirements"], "id", "requirement"),
            "datasets": unique(m["datasets"], "dataset_id", "dataset"),
            "backlog_tasks": unique(m["backlog_tasks"], "id", "task"),
            "external_findings": unique(m["external_findings"], "id", "external"),
        }
        parents = {u["id"] for u in units.values() if u["level"] == "parent"}
        exp = unique(self.experiments["units"], "id", "experiment")
        cards = self.components
        if set(exp) != set(units) or set(cards) != parents:
            raise IntegrityError("independent component/experiment registries differ from scope")
        if set(self.contract_texts) != parents:
            raise IntegrityError("missing parent contract text")
        for id, body in self.contract_texts.items():
            if [int(n) for n in re.findall(r"^(\d+)\. \*\*", body, re.M)] != list(range(1, 11)):
                raise IntegrityError(f"incomplete ten-part parent card: {id}")
        all_phases = []
        for uid, unit in units.items():
            if unit["parent"] not in parents:
                raise IntegrityError(f"missing parent: {uid}")
            if not set(unit["source_ids"]).issubset(source):
                raise IntegrityError(f"unknown source route: {uid}")
            expected = [f"EX-{uid}-P{i}" for i in range(8)]
            if unit["phase_ids"] != expected:
                raise IntegrityError(f"missing/reordered phase: {uid}")
            if [p[0] for p in exp[uid]["phases"]] != [f"P{i}" for i in range(8)]:
                raise IntegrityError(f"phase definition missing: {uid}")
            if unit["target"] != exp[uid]["target"] or unit["local_cases"] != exp[uid]["local_cases"]:
                raise IntegrityError(f"local definition mismatch: {uid}")
            upgrade = unit["upgrade_contract"]
            if (upgrade["id"] != uid or upgrade["required_phase_ids"] != expected
                    or upgrade != exp[uid]["upgrade_contract"]):
                raise IntegrityError(f"upgrade binding mismatch: {uid}")
            if not unit["contract"] or not unit["experiment"] or not unit["local_cases"]:
                raise IntegrityError(f"empty contract/fixture route: {uid}")
            all_phases.extend(expected)
        counts = {"parents": len(parents), "refinements": len(units) - len(parents),
                  "units": len(units), "phases": len(all_phases),
                  "source_findings": len(source), **{k: len(v) for k, v in registries.items()}}
        if counts != m["counts"] or len(set(all_phases)) != len(all_phases):
            raise IntegrityError("exact scope counts/phase IDs do not reconcile")
        if Counter(u["id"][0] for u in units.values()) != Counter(self.experiments["family_counts"]):
            raise IntegrityError("family coverage mismatch")
        for finding in source.values():
            if not set(finding["components"]).issubset(parents):
                raise IntegrityError(f"unknown source consumer: {finding['id']}")

    def _entries(self) -> dict[str, ScopeEntry]:
        entries: dict[str, ScopeEntry] = {}
        exp = {u["id"]: u for u in self.experiments["units"]}
        cards = self.components

        def add(id: str, kind: str, owner: str, phase: str, payload: dict,
                dependencies: tuple[str, ...] = ()) -> None:
            if id in entries:
                raise IntegrityError(f"scope ID collision: {id}")
            # The full governing closure participates in definition identity.
            version = digest({"definition": payload, "inputs": self.manifest["input_hashes"]})
            entries[id] = ScopeEntry(id, kind, owner, phase, version, dependencies, payload)

        for u in self.manifest["units"]:
            uid = u["id"]
            definition = {"unit": u, "experiment": exp[uid], "parent_card": cards[u["parent"]],
                          "parent_contract_text": self.contract_texts[u["parent"]]}
            add(uid, "unit", uid, "definition", definition,
                () if uid == u["parent"] else (u["parent"],))
            for phase in exp[uid]["phases"]:
                pid = f"EX-{uid}-{phase[0]}"
                add(pid, "phase", uid, phase[0], {"unit": uid, "phase": phase}, (uid,))
        for group, kind, key in (
            ("source_findings", "source", "id"), ("external_findings", "external", "id"),
            ("requirements", "requirement", "id"), ("datasets", "dataset", "dataset_id"),
            ("backlog_tasks", "task", "id"), ("upgrade_method_references", "method", "id"),
        ):
            for row in self.manifest[group]:
                add(row[key], kind, row[key], "clauses" if kind in {"source", "external"} else "definition", row)
        return entries

    def bundle(self) -> dict:
        return {"manifest": self.manifest, "experiments": self.experiments,
                "components": self.components, "contract_texts": self.contract_texts}
