"""Shared recipe result, C08 guards, and fixture comparison."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable

from trading_research.research.method_pack.logic import dec


@dataclass
class RecipeResult:
    recipe_id: str
    state: str
    value: dict
    hole_ids: list[str] = field(default_factory=list)
    known_at: int | None = None
    base_ok: bool | None = True
    coverage_ok: bool | None = True
    parent_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    units: dict = field(default_factory=dict)
    applicability: str | None = None
    reason: str | None = None
    evidence_class: str = "research_helper"


RecipeFn = Callable[[dict], RecipeResult]
RECIPES: dict[str, RecipeFn] = {}
FIXTURES: list[dict] = []
REQUIRED: dict[str, tuple[str, ...]] = {}


def register(recipe_id: str, required: tuple[str, ...] = ()) -> Callable[[RecipeFn], RecipeFn]:
    def deco(fn: RecipeFn) -> RecipeFn:
        if recipe_id in RECIPES:
            raise ValueError(f'duplicate recipe registration: {recipe_id}')
        def wrapped(inp: dict) -> RecipeResult:
            blocked = guard(inp, recipe_id, required)
            if blocked is not None:
                if blocked.reason in {'dependency available after use', 'dependency available after claimed snapshot'} and all(inp.get(key) is not None for key in required):
                    observed = fn(inp)
                    observed.base_ok = False
                    observed.state = 'invalid'
                    observed.hole_ids = list(dict.fromkeys(observed.hole_ids + blocked.hole_ids))
                    observed.reason = blocked.reason
                    return observed
                return blocked
            return fn(inp)
        RECIPES[recipe_id] = wrapped
        REQUIRED[recipe_id] = required
        return wrapped
    return deco


def add_fixture(spec: dict) -> None:
    FIXTURES.append(spec)


def guard(inp: dict, recipe_id: str, required: tuple[str, ...]) -> RecipeResult | None:
    if not inp and not required:
        return RecipeResult(recipe_id,"hole",{},base_ok=None,coverage_ok=None,
                            hole_ids=[f"HOLE:{recipe_id}:observation"],reason="actual observation inputs absent")
    dependencies = inp.get("dependencies", [])
    use_at = inp.get("use_at")
    known = inp.get("known_at")
    times = [d.get("known_at") for d in dependencies]
    times += [known] if known is not None else []
    if use_at is not None and any(t is not None and t > use_at for t in times):
        return RecipeResult(recipe_id, "invalid", {},
            hole_ids=[f"HOLE:{recipe_id}:ordering"], base_ok=False,
            reason="dependency available after use")
    if known is not None and any(t is not None and t > known for t in times):
        return RecipeResult(recipe_id, "invalid", {},
            hole_ids=[f"HOLE:{recipe_id}:ordering"], base_ok=False,
            reason="dependency available after claimed snapshot")
    for dep in dependencies:
        for key in ("instrument_id", "method_id", "branch", "band_id", "side"):
            if key in inp and key in dep and inp[key] != dep[key]:
                return RecipeResult(recipe_id, "invalid", {},
                    hole_ids=[f"HOLE:{recipe_id}:{key}"], base_ok=False,
                    coverage_ok=None, reason="identity mismatch")
        expected = inp.get("parent_ids")
        if expected is not None and dep.get("object_id") not in expected:
            return RecipeResult(recipe_id, "invalid", {},
                hole_ids=[f"HOLE:{recipe_id}:parent_ids"], base_ok=False,
                coverage_ok=None, reason="parent identity mismatch")
    missing = [key for key in required if inp.get(key) is None]
    if missing:
        # Preserve declared literal inputs independently of unavailable
        # derivations. Never copy arbitrary caller keys into recipe outputs.
        literals = {key: deepcopy(inp[key]) for key in required if inp.get(key) is not None}
        for key in ('entry', 'target', 'stop', 'lo', 'hi', 'price'):
            if key in literals:
                literals[key] = dec(literals[key])
        return RecipeResult(recipe_id, "hole", literals,
            hole_ids=[f"HOLE:{recipe_id}:{key}" for key in missing],
            known_at=known, base_ok=None, coverage_ok=None, reason="missing required datum")
    return None


def values_equal(actual: Any, expected: Any) -> bool:
    if expected == "__null__":
        return actual is None
    if expected == "__true__":
        return actual is True
    if expected == "__false__":
        return actual is False
    if isinstance(expected, Decimal) or isinstance(actual, Decimal):
        if actual is None or expected is None:
            return actual is expected
        return dec(actual) == dec(expected)
    if isinstance(expected, list) and isinstance(actual, list):
        return len(actual) == len(expected) and all(values_equal(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, dict) and isinstance(actual, dict):
        return all(values_equal(actual.get(k), v) for k, v in expected.items())
    return actual == expected


def compare_result(result: RecipeResult, expected: dict) -> list[str]:
    failures = []
    for key, want in expected.items():
        if key == "state":
            got = result.state
        elif key == "base_ok":
            got = result.base_ok
        elif key == "coverage_ok":
            got = result.coverage_ok
        elif key == "known_at":
            got = result.known_at
        elif key == "hole_ids":
            got = result.hole_ids
        elif key == "applicability":
            got = result.applicability
        elif key == "reason":
            got = result.reason
        else:
            got = result.value.get(key)
        if not values_equal(got, want):
            failures.append(f"{key}: got {got!r} want {want!r}")
    return failures


def run_recipe(recipe_id: str, inp: dict) -> RecipeResult:
    fn = RECIPES[recipe_id]
    return fn(inp)


def run_fixture_spec(spec: dict) -> dict:
    recipe_id = spec["recipe"]
    result = run_recipe(recipe_id, deepcopy(spec["inputs"]))
    failures = compare_result(result, spec["expected"])
    status = "pass" if not failures else "fail"
    return {
        "id": spec["id"],
        "recipe": recipe_id,
        "kind": spec.get("kind", "positive"),
        "status": status,
        "failures": failures,
        "inputs": jsonable(spec["inputs"]),
        "expected": jsonable(spec["expected"]),
        "actual_state": result.state,
        "actual_value": _public_value(result),
        "evidence_mode": spec.get("evidence_mode", "synthetic_fixture"),
        "base_ok": result.base_ok,
        "coverage_ok": result.coverage_ok,
        "hole_ids": result.hole_ids,
        "reason": result.reason,
    }


def c08_mutations(spec: dict) -> list[dict]:
    recipe_id = spec["recipe"]
    required = REQUIRED.get(recipe_id, ())
    inputs = deepcopy(spec["inputs"])
    inputs.setdefault("instrument_id", "fixture-instrument")
    use = inputs.get("use_at", inputs.get("known_at", 100))
    if use is None:
        use = 100
    inputs["use_at"] = use
    cases = []
    missing = deepcopy(inputs)
    if missing.get('known_at') is not None:
        missing['use_at'] = max(missing['use_at'], missing['known_at'])
    missing.pop('dependencies', None)
    key = required[0] if required else next((k for k in inputs if not k.startswith('_')), None)
    if required:
        missing.pop(key, None)
        cases.append(("missing", missing, {"state": "hole", "base_ok": None,
                                          "hole_ids": [f"HOLE:{recipe_id}:{name}" for name in required if missing.get(name) is None]}))
    else:
        cases.append(("missing", {}, {"state":"hole","base_ok":None,
                                      "hole_ids":[f"HOLE:{recipe_id}:observation"]}))
    late = deepcopy(inputs)
    late["dependencies"] = [{"object_id": "late-input", "known_at": use + 1}]
    cases.append(("late", late, {"base_ok": False}))
    identity = deepcopy(inputs)
    identity['use_at'] = max(use, identity.get('known_at') or use)
    identity["dependencies"] = [{"object_id": "foreign-input", "known_at": min(use, identity.get('known_at') or use),
                                   "instrument_id": "another-instrument"}]
    cases.append(("identity", identity, {"state": "invalid", "base_ok": False, "reason": "identity mismatch"}))
    result = []
    for kind, mutated, expected in cases:
        row = run_fixture_spec({"id": f"{spec['id']}:{kind}", "recipe": recipe_id,
                                "kind": f"c08_{kind}", "inputs": mutated, "expected": expected})
        row["detected_causal_violation"] = kind == "late" and row["base_ok"] is False
        result.append(row)
    return result


def _public_value(result: RecipeResult) -> dict:
    out = dict(result.value)
    out["_state"] = result.state
    out["_holes"] = result.hole_ids
    return out


def jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items() if k != '_source_admission'}
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    return value
