"""Finite single-stream oracle, independent of SQLite/query implementation."""
from trading_research.errors import ContractError, IntegrityError
from trading_research.runtime.merge import ReplayBatch


def batches(events, *, domain, contract_version, partitions, before):
    unique={}; source_order={}; grouped={}
    for event in events:
        old=unique.get(event.id)
        if old is not None:
            if old != event: raise IntegrityError('conflicting immutable event')
            continue
        key=(event.partition,event.sequence)
        if key in source_order: raise IntegrityError('reused source sequence')
        unique[event.id]=event; source_order[key]=event.id
        if event.partition in partitions and event.clocks.known_at<before:
            grouped.setdefault(event.clocks.known_at,[]).append(event)
    return tuple(ReplayBatch(domain,contract_version,at,tuple(sorted(grouped[at],key=lambda e:(e.partition,e.sequence))))
                 for at in sorted(grouped))


def full_recompute(graph, state, kernels):
    """Toy/reference algebra on identical explicit raw fields, no forecasting claim."""
    if any(edge.lag_ns for port in graph.ports.values() for edge in port.inputs):
        raise ContractError('literal recomputation requires an explicit preceding-state resolver for lagged graphs')
    if any(key not in graph.ports or graph.ports[key].inputs for key in state):
        raise ContractError('literal full recomputation accepts root-only seeds, never cached derived outputs')
    values={k:dict(v) for k,v in state.items()}
    calls=[]
    for key in graph.order:
        port=graph.ports[key]
        if not port.inputs: continue
        inputs={edge.source:values[edge.source] for edge in port.inputs if edge.source in values}
        if any(not e.optional and e.source not in inputs for e in port.inputs):
            continue
        values[key]=kernels[key](inputs); calls.append(key)
    return values,tuple(calls)
