"""P15-17 enumeration-time override hook for the B0.2 source adapters.

Additive. With ``overrides=None`` (or an overrides mapping that carries no
``ENUMERATION_KEY``) every call below is the identity, so the no-override path
of every ``scan_b02`` stays byte-identical to the committed B0.2 run (RA-1).

Ruling (P15-17 stage A, 2026-09-16): recipes on the Formation, Reference and
Timing axes apply at ENUMERATION time -- before references and contacts are
built -- and may therefore change the contact population. Recipes on the
Profile, Delta, Sequence and Memory axes apply at STAGE EVALUATION on the
already enumerated contacts (``search.finish_scan_b02``).

This module deliberately has no intra-package imports so that any adapter can
import it at module scope without a cycle.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Mapping

ENUMERATION_KEY = "__enumeration__"
ENUMERATION_POINTS = ("window", "references", "contacts")
_ENUM_HOOK: ContextVar[Any] = ContextVar("b02_enumeration_hook", default=None)


def split_b02_overrides(overrides):
    """Split an overrides mapping into ``(stage_overrides, enumeration_hook)``."""
    if not overrides:
        return None, None
    if not isinstance(overrides, Mapping):
        return overrides, None
    hook = overrides.get(ENUMERATION_KEY)
    if hook is None:
        return overrides, None
    if not callable(hook):
        raise TypeError("enumeration override must be callable")
    stages = {key: value for key, value in overrides.items() if key != ENUMERATION_KEY}
    return (stages or None), hook


@contextmanager
def enumeration_scope(overrides):
    """Install the enumeration hook for the duration of one ``scan_b02`` call."""
    _stages, hook = split_b02_overrides(overrides)
    if hook is None:
        yield None
        return
    token = _ENUM_HOOK.set(hook)
    try:
        yield hook
    finally:
        _ENUM_HOOK.reset(token)


def enumeration_hook_installed() -> bool:
    return _ENUM_HOOK.get() is not None


def enumeration_point(point: str, payload, **context):
    """Offer ``payload`` to the installed enumeration hook; identity when absent."""
    hook = _ENUM_HOOK.get()
    if hook is None:
        return payload
    replaced = hook(point=point, payload=payload, **context)
    return payload if replaced is None else replaced
