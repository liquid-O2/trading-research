"""Retain complete empirical distributions once; serve their exact quantiles.

The empirical calculator's atoms, masses and diagnostics remain in the frozen
family. Each prediction model carries only the fields its existing quantile
lookup uses, bound to the complete distribution by content digest. This avoids
copying and revalidating millions of unused atoms for every model prediction.
"""
import numpy as np

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import digest


SCHEMA = 'jumbo-empirical-quantile-serving-v1'
FAMILY_SCHEMA = 'jumbo-continuous-prior-sharing-v1'
SERVING_FIELDS = ('quantiles', 'groups', 'values', 'global_values')


def quantile_serving_record(full):
    if full.get('kind') != 'EmpiricalQuantileFitV1':
        raise IntegrityError('complete empirical quantile evidence required')
    return {'kind': SCHEMA, 'full_distribution_sha256': digest(full),
            **{key: full[key] for key in SERVING_FIELDS}}


def predict_quantile_serving(record, groups):
    if (record.get('kind') != SCHEMA
            or set(record) != {'kind', 'full_distribution_sha256', *SERVING_FIELDS}
            or not isinstance(record['full_distribution_sha256'], str)
            or len(record['full_distribution_sha256']) != 64):
        raise IntegrityError('complete bound quantile serving record required')
    levels = np.asarray(record['quantiles'], dtype=np.float64)
    local = np.asarray(record['values'], dtype=np.float64)
    pooled = np.asarray(record['global_values'], dtype=np.float64)
    keys = record['groups']
    if (levels.ndim != 1 or not len(levels) or np.any(np.diff(levels) <= 0)
            or np.any(levels <= 0) or np.any(levels >= 1)
            or local.shape != (len(keys), len(levels)) or pooled.shape != (len(levels),)
            or not all(np.isfinite(value).all() for value in (levels, local, pooled))):
        raise IntegrityError('quantile serving arrays have an invalid layout or value')
    try:
        lookup = {group: row for group, row in zip(keys, record['values'], strict=True)}
    except TypeError as exc:
        raise IntegrityError('quantile group identities must be hashable') from exc
    if len(lookup) != len(keys):
        raise IntegrityError('quantile serving groups must be unique')
    # The same ordered lookup, global fallback and monotone projection as
    # backend.predict_empirical_quantiles; no CDF is refitted or approximated.
    result = np.asarray([lookup.get(group, pooled) for group in groups], dtype=np.float64)
    return np.maximum.accumulate(result, axis=-1)


def validate_family_priors(family, *, store=None):
    """Verify full distribution/serving closure once on freeze and restore."""
    models = family.get('models', {})
    has_serving = any(isinstance(model.get('baseline'), list)
        and any(wire.get('kind') == SCHEMA for wire in model['baseline']) for model in models.values())
    if not has_serving and family.get('prior_storage_schema') is None:
        return  # Existing categorical and historical full-wire contracts.
    if family.get('prior_storage_schema') != FAMILY_SCHEMA:
        raise IntegrityError('shared quantile prior schema is missing')
    evidence = family.get('empirical_distribution_evidence')
    reference = family.get('empirical_distribution_artifact')
    if reference is not None:
        if evidence is not None or store is None:
            raise IntegrityError('one available full distribution artifact is required')
        from trading_research.research.jumbo_fitting import read_json_compressed
        evidence = read_json_compressed(store, reference)
    if not isinstance(evidence, list) or not evidence:
        raise IntegrityError('shared prior lacks its full atom/mass evidence')
    from trading_research.research.jumbo_model_backend import EmpiricalQuantileFit
    for wire in evidence:
        # One complete validation at the persistence boundary retains the
        # original calculator's wire contract. Serving does not repeat it.
        EmpiricalQuantileFit.from_dict(wire)
    prior_id = digest(evidence)
    serving = [quantile_serving_record(wire) for wire in evidence]
    for model in models.values():
        if (model.get('target_kind') != 'continuous'
                or model.get('baseline_id') != prior_id or model.get('baseline') != serving):
            raise IntegrityError('model quantiles differ from the retained complete distributions')
    return {'full_distribution_count': len(evidence), 'baseline_id': prior_id,
            'full_atom_and_mass_evidence_retained': True}
