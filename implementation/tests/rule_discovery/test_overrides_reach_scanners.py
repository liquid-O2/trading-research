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


JUMBO = ADAPTERS / "jumbo.py"


def _uses(tree: ast.Module, name: str) -> list[tuple[int, str]]:
    """(line, kind) for every read of ``name``: 'compare' when it is an
    operand of a comparison, 'arith' when it is an operand of + or -, else
    'other'."""
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load)):
            continue
        parent = parents.get(node)
        if isinstance(parent, ast.Compare):
            out.append((node.lineno, "compare"))
        elif isinstance(parent, ast.BinOp) and isinstance(parent.op, (ast.Add, ast.Sub)):
            # ``low - TOL <= price <= high + TOL`` widens a band for a
            # comparison: arithmetic whose result is compared is a tolerance
            grand = parents.get(parent)
            out.append((node.lineno, "compare" if isinstance(grand, ast.Compare) else "arith"))
        elif isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) and parent.func.id == "str":
            out.append((node.lineno, "other"))  # the parameters record
        else:
            out.append((node.lineno, "other"))
    return out


def test_jumbo_tolerance_is_compared_and_stop_distance_is_added():
    """``LEVEL_COINCIDENCE`` is the tolerance for a print or an extreme to
    count as at a level and ``STOP_BEYOND_EXTREME`` is the distance a resting
    stop sits beyond the swept extreme. One constant once served both, so a
    rescan of the tolerance moved every stop (2026-09-18: the first split
    moved two of the eight stop sites and "coincide12-clean" still widened
    the stops of 207,182 of 344,306 episodes by seven points; its +18.3 a
    session was a stop read). A tolerance is only ever compared; a stop
    distance is only ever added to or subtracted from a price."""
    tree = ast.parse(JUMBO.read_text())
    tolerance = [(line, kind) for line, kind in _uses(tree, "LEVEL_COINCIDENCE") if kind == "arith"]
    assert not tolerance, f"LEVEL_COINCIDENCE added to a price (a stop?) at lines {tolerance}"
    distance = [(line, kind) for line, kind in _uses(tree, "STOP_BEYOND_EXTREME") if kind == "compare"]
    assert not distance, f"STOP_BEYOND_EXTREME used as a tolerance at lines {distance}"
    assert any(kind == "arith" for _, kind in _uses(tree, "STOP_BEYOND_EXTREME")), "no stop reads STOP_BEYOND_EXTREME"
    assert any(kind == "compare" for _, kind in _uses(tree, "LEVEL_COINCIDENCE")), "nothing compares against LEVEL_COINCIDENCE"
