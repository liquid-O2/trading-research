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
from trading_research.research.method_pack.protocol import FIXTURES, RECIPES, run_fixture_spec, c08_mutations

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
