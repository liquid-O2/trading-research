"""Preserved literal F11 serving path for bounded parity checks.

Source before the optional read-operation adapter: SHA256 65b588285faa886b7a5c17756d7f958491723d54f2f6914f2eb201a04c92803f.
"""

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifact_graph import (
    SemanticArtifactStore, CommitRef, ReadSession, FITTED,
    _model_domain, _attest_components, validate_oof_producer, _ancestors,
    _json, attest_state, _admit,
)

def reference_serve_bound_model(model, store, commit_ref, node_id, session):
    """Sanctioned finite supplied-state adapter; no fitting or model search."""
    from trading_research.research.models import BinaryModel, FrequencyModel, sigmoid
    from trading_research.research.calibration import CalibratedBinary
    from trading_research.research.scoring import finite, probability
    import math
    if type(store) is not SemanticArtifactStore or type(commit_ref) is not CommitRef or type(session) is not ReadSession:
        raise ContractError("typed committed serving boundary required")
    configuration = session._configuration
    if configuration.store is not store or configuration.commit_ref != commit_ref:
        raise ContractError("served session belongs to another exact commit/store")
    _model_domain(model)
    commit = store.read_commit(commit_ref.key)
    if commit.reference != commit_ref or node_id not in commit.closure.by_id:
        raise IntegrityError("served model not in named complete commit")
    node = commit.closure.by_id[node_id]
    if node.kind not in FITTED:
        raise ContractError("served node is not fitted state")
    columns = model.base.columns if type(model) is CalibratedBinary else model.columns
    _attest_components(model, node, commit.closure, commit.closure._payloads)
    request = session.bindings[0].request
    if request.purpose not in {"OOF", "final"} or request.target_definition_ref is None:
        raise ContractError("serving requires coherent OOF or final target request")
    if request.purpose == "OOF":
        validate_oof_producer(request, node_id, commit)
    else:
        if request.target_start != request.decision_cut or request.assembled_at >= request.target_end:
            raise ContractError("final serving original target expired or shifted")
        for i in _ancestors(node_id, commit.closure.by_id):
            fit = commit.closure.by_id[i].fit_evidence
            if fit and (fit.actual_fit_completion_at > request.decision_cut or fit.target_definition_ref != request.target_definition_ref):
                raise ContractError("final fitted ancestor target/completion differs")
    values = tuple(finite(_json(session.read(c))) for c in columns)
    manifest = session.seal()
    attest_state(model, node, commit.closure._payloads, columns, manifest)
    for record in manifest.reads:
        b = record.binding
        if _admit(commit.closure, b.node_id, b.source_column, b.request) != record.row:
            raise IntegrityError("served actual read differs from admitted commit")
    def calculate(candidate, x):
        if type(candidate) is BinaryModel:
            return sigmoid(candidate.intercept + math.fsum(w*(v-m)/s for w,v,m,s in zip(candidate.coefficients,x,candidate.means,candidate.scales)))
        if type(candidate) is FrequencyModel:
            key = tuple(sum(v >= c for c in edges) for v, edges in zip(x, candidate.cuts))
            cell = next(((s,n) for k,s,n in candidate.cells if k == key), None)
            center = .5 if candidate.prior_center == "uniform" else candidate.overall
            return candidate.overall if cell is None else (cell[0]+candidate.prior_strength*center)/(cell[1]+candidate.prior_strength)
        p = calculate(candidate.base, x)
        p = min(1-candidate.probability_floor, max(candidate.probability_floor, p))
        return calculate(candidate.calibration, (math.log(p)-math.log1p(-p),))
    return probability(calculate(model, values)), manifest
