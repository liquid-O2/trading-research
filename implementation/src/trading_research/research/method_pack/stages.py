"""Availability caps for the actual stage consuming each source operand."""

from importlib import import_module
from importlib.util import find_spec

from .catalog import METHOD_BY_ID

M01 = {
    'range_frozen': 'range_known_at', 'context_fixed': 'context_at',
    'reversal_context': 'context_at', 'directional_context': 'context_at',
    'extended_context': 'context_at', 'purged_compressed_context': 'context_at',
    'rotation_context': 'context_at', 'location_touched': 'touch_at',
    'source_confirmation': 'confirm_at', 'reaction_side_confirmed': 'confirm_at',
    'edge_swept': 'sweep_at', 'source_zone_known': 'zone_known_at',
}


def limits_for(method_id):
    if method_id == 'JJ-TBR':
        return M01
    module = __package__ + '.method_slices.' + METHOD_BY_ID[method_id].lower()
    return getattr(import_module(module), 'STAGE_LIMITS', {}) if find_spec(module) else {}


def stage_at(method_id, field, operands):
    name = limits_for(method_id).get(field)
    return operands.get(name) if name else None


def audit_candidate(candidate, operands, objects, assertions, evidence):
    module = __package__ + '.method_slices.' + METHOD_BY_ID[candidate['method_id']].lower()
    hook = getattr(import_module(module), 'audit_candidate', None) if find_spec(module) else None
    return hook(candidate, operands, objects, assertions, evidence) if hook else []
