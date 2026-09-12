"""Source selector availability. Geometry alone does not select a method attempt."""

from .catalog import BRANCHES, DISCOVERY_REASON, METHOD_BY_ID
from .contracts import sections


def discovery_holes(method_id: str) -> list[dict]:
    section = sections()[METHOD_BY_ID[method_id]]
    source_rule = next(line for line in section.splitlines()
                       if line.startswith('**Source-complete candidate discovery:**'))
    return [{
        'hole_id': f'HOLE:{METHOD_BY_ID[method_id]}:{branch}:candidate_selector',
        'recipe_id': METHOD_BY_ID[method_id], 'method_id': method_id,
        'branch': branch, 'candidate_id': None, 'kind': 'source_definition',
        'missing_fields': ['candidate_selector'], 'source_ref': source_rule,
        'affected_output': 'historical_discovery', 'reason': DISCOVERY_REASON[method_id],
    } for branch in BRANCHES[method_id]]


def run_historical(method_id: str) -> list[dict]:
    discovery_holes(method_id)
    return []
