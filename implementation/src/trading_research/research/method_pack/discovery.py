"""Source selector availability. Geometry alone does not select a method attempt."""

import hashlib
import json
from pathlib import Path

from .catalog import BRANCHES, METHOD_BY_ID
from .contracts import consumed_hashes, fields_for


AUDIT_PATH = Path(__file__).with_name('discovery_audit.json')


def discovery_audit(method_id: str) -> dict:
    """Return the source review only while every reviewed contract is unchanged.

    A complete numeric object or branch expression is not automatically a
    complete candidate selector. This review records the missing producer
    inputs for each full branch, rather than inferring discovery from fixtures.
    A changed source must be reviewed again; it cannot silently inherit N=0.
    """
    payload = AUDIT_PATH.read_bytes()
    doc = json.loads(payload)
    review = doc['methods'][method_id]
    if review['reviewed_source_hashes'] != consumed_hashes(method_id):
        raise ValueError(f'{method_id}: source selector review is stale; re-audit FORMULAS before discovery')
    if set(review['branches']) != set(BRANCHES[method_id]):
        raise ValueError(f'{method_id}: source selector review omits a branch')
    fields = fields_for(method_id)
    for branch, row in review['branches'].items():
        if row['complete_candidate_selector'] is not False:
            raise ValueError(f'{method_id}/{branch}: complete selector requires an acquired-data cohort builder')
        if not row['missing_fields'] or not set(row['missing_fields']) <= set(fields):
            raise ValueError(f'{method_id}/{branch}: unbound discovery-hole inputs')
    return {**review, 'audit_version': doc['audit_version'], 'audit_basis': doc['audit_basis'],
            'audit_path': str(AUDIT_PATH), 'audit_sha256': hashlib.sha256(payload).hexdigest()}


def discovery_holes(method_id: str) -> list[dict]:
    review = discovery_audit(method_id)
    fields = fields_for(method_id)
    return [{
        'hole_id': f'HOLE:{METHOD_BY_ID[method_id]}:{branch}:candidate_selector',
        'recipe_id': METHOD_BY_ID[method_id], 'method_id': method_id,
        'branch': branch, 'candidate_id': None, 'kind': 'source_definition',
        'missing_fields': ['candidate_selector', *row['missing_fields']],
        'source_ref': review['source_rule'], 'producer_recipes': row['producer_recipes'],
        'producer_rules': {key: fields[key].rule for key in row['missing_fields']},
        'affected_output': 'historical_discovery', 'reason': row['reason'],
        'complete_candidate_selector': False, 'audit_version': review['audit_version'],
        'audit_sha256': review['audit_sha256'],
        'denominator_effect': 'No source-defined candidate IDs; p=f=u=n=N=0 and rate/interval=null. Fixtures and chart diagnostics are excluded.',
    } for branch, row in review['branches'].items()]


def run_historical(method_id: str) -> list[dict]:
    discovery_holes(method_id)
    return []
