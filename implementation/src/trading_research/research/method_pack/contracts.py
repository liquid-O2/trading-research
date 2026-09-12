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
