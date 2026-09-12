"""The consumed FORMULAS sections, inventories and typed producer bindings."""

from dataclasses import dataclass
from functools import lru_cache
import hashlib
from pathlib import Path
import re

from . import FORMULAS_PATH
from .catalog import METHOD_BY_ID, objects_for


@dataclass(frozen=True)
class Field:
    name: str
    type: str
    recipes: tuple[str, ...]
    rule: str


@lru_cache(maxsize=1)
def sections() -> dict[str, str]:
    text = Path(FORMULAS_PATH).read_text()
    matches = list(re.finditer(r"^## ([CMO]\d{2,3}) — .*$", text, re.M))
    return {m[1]: text[m.start():matches[i + 1].start() if i + 1 < len(matches) else text.find('## Source references', m.end())]
            for i, m in enumerate(matches)}


@lru_cache(maxsize=12)
def fields_for(method_id: str) -> dict[str, Field]:
    result = {}
    for line in sections()[METHOD_BY_ID[method_id]].splitlines():
        if not line.startswith('| `'):
            continue
        cols = line.split('|')
        recipes = tuple(re.findall(r'\[(O\d{3})', cols[2]))
        for declaration in re.findall(r'`([^`]+)`', cols[1]):
            if ':' in declaration:
                name, kind = declaration.split(':', 1)
                result[name] = Field(name, kind, recipes, cols[3].strip())
    return result


def consumed_hashes(method_id: str) -> dict[str, str]:
    keys = [f'C{i:02}' for i in range(9)] + [METHOD_BY_ID[method_id]] + objects_for(method_id)
    return {key: hashlib.sha256(sections()[key].encode()).hexdigest() for key in keys}


def inventory_errors(method_id: str) -> list[str]:
    section = sections()[METHOD_BY_ID[method_id]].split('### ')[0]
    printed = sorted(set(re.findall(r'\bO\d{3}\b', section)))
    errors = []
    if printed != sorted(objects_for(method_id)):
        errors.append('mapped object inventory differs from FORMULAS')
    if any(not f.recipes for f in fields_for(method_id).values()):
        errors.append('predicate operand has no declared producer')
    return errors


class OutputContractError(ValueError):
    """A producer implementation violated C07; this is not a source hole."""


@dataclass(frozen=True)
class OutputField:
    types: tuple[type, ...]
    nullable: bool = False


OUTPUT_SCHEMAS: dict[str, dict[str, OutputField]] = {}


def register_output_schema(recipe_id, fields):
    """Register complete producer payload fields (including explicit unknowns).

    No keys are inserted in output. A nullable field needs an explicit value;
    schema omissions are implementation errors and cannot masquerade as holes.
    """
    if recipe_id not in sections() or not recipe_id.startswith('O'):
        raise OutputContractError(f'unknown object schema {recipe_id}')
    OUTPUT_SCHEMAS[recipe_id] = dict(fields)


def validate_output(result, *, require_schema=True):
    if result.state not in {'computed', 'supplied', 'hole', 'invalid'}:
        raise OutputContractError(f'{result.recipe_id}: domain state used as validity state')
    if type(result.value) is not dict:
        raise OutputContractError(f'{result.recipe_id}: payload is not a typed mapping')
    for name in ('base_ok', 'coverage_ok'):
        if getattr(result, name) is not None and type(getattr(result, name)) is not bool:
            raise OutputContractError(f'{result.recipe_id}: invalid {name}')
    if result.known_at is not None and (type(result.known_at) is not int or not -(2**63) <= result.known_at < 2**63):
        raise OutputContractError(f'{result.recipe_id}: invalid known_at')
    schema = OUTPUT_SCHEMAS.get(result.recipe_id)
    if schema is None:
        if require_schema:
            raise OutputContractError(f'{result.recipe_id}: complete output schema not implemented')
        return result
    # Invalid evidence may be rejected before a payload can exist. Domain/data
    # holes, however, must retain the full meaningful partial-result contract.
    if result.state == 'invalid' and not result.value:
        return result
    for name, field in schema.items():
        if name not in result.value:
            raise OutputContractError(f'{result.recipe_id}: missing required output {name}')
        value = result.value[name]
        if value is None and field.nullable:
            continue
        if type(value) not in field.types:
            raise OutputContractError(f'{result.recipe_id}: invalid output type for {name}')
    return result
