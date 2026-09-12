"""Object recipe registry. Importing this module registers FORMULAS recipes."""

from trading_research.research.method_pack.objects import m01_recipes  # noqa: F401
from trading_research.research.method_pack.objects import m02_recipes  # noqa: F401
from trading_research.research.method_pack.objects import m03_recipes  # noqa: F401
from trading_research.research.method_pack.objects import rest_recipes  # noqa: F401
from trading_research.research.method_pack.objects import m06_recipes  # noqa: F401
from trading_research.research.method_pack.objects import m09_recipes  # noqa: F401
from trading_research.research.method_pack.objects import m10_recipes  # noqa: F401
from trading_research.research.method_pack.objects import m11_recipes  # noqa: F401
from trading_research.research.method_pack.objects import m12_recipes  # noqa: F401
from trading_research.research.method_pack.protocol import FIXTURES, RECIPES, REQUIRED, guard, run_fixture_spec, c08_mutations
from trading_research.research.method_pack.contracts import register_output_schema
from trading_research.research.method_pack.objects import (
    native_boundary, range_geometry, profiles, profile_integration,
    context_observations, auction_geometry, local_flow, flow_sequences, lifecycles, process_observations,
)


def _install_domain(module):
    """Install reviewed domains while retaining the shared helper guard.

    Helpers and synthetic fixtures never acquire native provenance here. The
    separate native boundary resolves member locators and validates payloads.
    """
    for recipe_id, producer in getattr(module, 'REGISTRATION_OVERRIDES', {}).items():
        required = getattr(module, 'REQUIRED_INPUTS', {}).get(recipe_id, ())
        hole_payload = getattr(module, 'GUARD_HOLE_PAYLOADS', {}).get(recipe_id)
        def wrapped(inputs, producer=producer, recipe_id=recipe_id, required=required,
                    hole_payload=hole_payload):
            blocked = guard(inputs, recipe_id, required)
            if blocked is not None:
                if blocked.reason in {'dependency available after use', 'dependency available after claimed snapshot'} and all(inputs.get(key) is not None for key in required):
                    observed = producer(inputs)
                    observed.base_ok, observed.state = False, 'invalid'
                    observed.hole_ids = list(dict.fromkeys(observed.hole_ids + blocked.hole_ids))
                    observed.reason = blocked.reason
                    return observed
                if blocked.state == 'hole' and hole_payload is not None:
                    # Opt-in domain payloads preserve the guard's unknown
                    # validity, clocks, holes, and declared literal inputs.
                    blocked.value = {**hole_payload(blocked), **blocked.value}
                return blocked
            return producer(inputs)
        wrapped.__name__ = producer.__name__
        wrapped.__module__ = producer.__module__
        RECIPES[recipe_id] = wrapped
        REQUIRED[recipe_id] = required
    for recipe_id, schema in getattr(module, 'OUTPUT_SCHEMAS', {}).items():
        register_output_schema(recipe_id, schema)
    if module is not native_boundary:
        for recipe_id, producer in getattr(module, 'NATIVE_PRODUCERS', {}).items():
            native_boundary.register_native(recipe_id, producer, module.OUTPUT_SCHEMAS[recipe_id])
        for recipe_id, producer in getattr(module, 'DERIVED_PRODUCERS', {}).items():
            native_boundary.register_derived(recipe_id, producer, module.OUTPUT_SCHEMAS[recipe_id])


for _domain in (native_boundary, range_geometry, profiles, profile_integration,
                context_observations, auction_geometry, local_flow, flow_sequences, lifecycles, process_observations):
    _install_domain(_domain)

from . import fixtures_completion_geometry, fixtures_completion_context, fixtures_completion_native, fixtures_completion_flow
fixtures_completion_geometry.install(FIXTURES)
fixtures_completion_context.install(FIXTURES)
fixtures_completion_native.install(FIXTURES)
fixtures_completion_flow.install(FIXTURES)

__all__ = ["FIXTURES", "RECIPES", "run_object_fixtures", "recipes_for"]


def recipes_for(object_ids: list[str]) -> list[str]:
    return [oid for oid in object_ids if oid in RECIPES]


def run_object_fixtures(object_ids: list[str]) -> list[dict]:
    wanted = set(object_ids)
    rows = []
    for spec in FIXTURES:
        if spec["recipe"] not in wanted:
            continue
        rows.append(run_fixture_spec(spec))
        rows.extend(c08_mutations(spec))
    return rows
