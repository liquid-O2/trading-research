"""A Phase 1.5 rescan candidate sets a module constant with
``--scanner-overrides``; a constant bound as a function's default argument is
evaluated when the module loads and the override never reaches the scanner
(2026-09-17: two candidates on ``jumbo.MAX_CONTACTS_PER_LEVEL`` returned the
baseline on every one of 1,742 sessions). No parameter default in a source
adapter may be a bare module-level constant."""
import ast
from pathlib import Path

import pytest

ADAPTERS = Path(__file__).resolve().parents[2] / "src/trading_research/research/rule_discovery/source_adapters"
FILES = sorted(p for p in ADAPTERS.glob("*.py") if not p.name.startswith("_"))


def _module_constants(tree: ast.Module) -> set[str]:
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    names.add(t.id)
    return names


@pytest.mark.parametrize("path", FILES, ids=[p.name for p in FILES])
def test_no_scanner_default_is_bound_to_a_module_constant(path):
    tree = ast.parse(path.read_text())
    constants = _module_constants(tree)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = node.args
        for default in list(args.defaults) + [d for d in args.kw_defaults if d is not None]:
            if isinstance(default, ast.Name) and default.id in constants:
                offenders.append(f"{path.name}:{node.lineno} {node.name}(... = {default.id})")
    assert not offenders, "\n".join(offenders)


def _override_constants() -> dict[str, set[str]]:
    """{module basename: {constant names any candidates file overrides}}."""
    out: dict[str, set[str]] = {}
    root = Path(__file__).resolve().parents[3] / "planning/phase-1-5/candidates"
    import json

    for path in sorted(root.glob("rescan_candidates_*.json")):
        for cand in json.loads(path.read_text()):
            for key in (cand.get("overrides") or {}):
                module, name = key.split(".", 1)
                out.setdefault(module, set()).add(name)
    return out


@pytest.mark.parametrize("path", FILES, ids=[p.name for p in FILES])
def test_no_module_constant_is_derived_from_an_overridden_one(path):
    """A module-level constant computed from an overridden constant is fixed
    when the module loads (2026-09-18: ``FAIL_WINDOW_NS = FAIL_WINDOW_BARS *
    FIVE`` kept four deadlines on the default while the bar count was
    overridden); derive it inside the function that uses it instead."""
    overridden = _override_constants().get(path.stem, set())
    if not overridden:
        pytest.skip("no candidate overrides this module")
    tree = ast.parse(path.read_text())
    offenders = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name) and t.id.isupper()]
            value = node.value
            if not names or value is None:
                continue
            if names == ["RULES"]:
                # the rules document records the defaults as the family's
                # published parameters; a rescan run names its overrides in
                # its own candidates file, so the document is not the record
                # of what ran and is exempt here
                continue
            used = {n.id for n in ast.walk(value) if isinstance(n, ast.Name) and n.id in overridden}
            if used:
                offenders.append(f"{path.name}:{node.lineno} {', '.join(names)} derived from {', '.join(sorted(used))}")
    assert not offenders, "\n".join(offenders)
