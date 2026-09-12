"""C04 Kleene three-valued predicates. None is unknown. Never coerce."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

Tri = bool | None


def kleene_and(*xs: Tri) -> Tri:
    if any(x is False for x in xs):
        return False
    if any(x is None for x in xs):
        return None
    return True


def kleene_or(*xs: Tri) -> Tri:
    if any(x is True for x in xs):
        return True
    if any(x is None for x in xs):
        return None
    return False


def kleene_not(x: Tri) -> Tri:
    if x is None:
        return None
    return not x


def kleene_eq(a: Any, b: Any) -> Tri:
    if a is None or b is None:
        return None
    return a == b


def kleene_cmp(op: str, a: Any, b: Any) -> Tri:
    if a is None or b is None:
        return None
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    raise ValueError(op)


def kleene_between(x: Any, lo: Any, hi: Any) -> Tri:
    return kleene_and(kleene_cmp(">=", x, lo), kleene_cmp("<=", x, hi))


def kleene_case(key: Any, mapping: dict[Any, Tri], default: Tri = None) -> Tri:
    if key is None:
        return None
    if key in mapping:
        return mapping[key]
    return default


def implies(required: Tri, cond: Tri) -> Tri:
    return kleene_or(kleene_not(required), cond)


def verdict(base_ok: Tri, coverage_ok: Tri, sequence_ok: Tri) -> str:
    if base_ok is False or sequence_ok is False:
        return "fail"
    if base_ok is None or coverage_ok is not True or sequence_ok is None:
        return "unknown"
    return "pass"


def dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise TypeError("boolean is not a price")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(value)


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise TypeError("boolean is not an integer key")
    return int(value)
