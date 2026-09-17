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
