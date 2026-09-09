"""Field/lineage planning and explicitly named optional scheduling policies."""
from collections import deque
from dataclasses import dataclass
from math import ceil
from statistics import median_low
from types import MappingProxyType

from trading_research.errors import ContractError
from trading_research.foundations.graph import Graph
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class FieldChange:
    fields: frozenset[str]
    lineage_changed: bool = False

    def __post_init__(self):
        if not isinstance(self.fields, frozenset) or any(not isinstance(s,str) or not s for s in self.fields) or type(self.lineage_changed) is not bool:
            raise ContractError('field invalidation needs immutable names and explicit lineage state')


@dataclass(frozen=True)
class DirtyPlan:
    graph_version: str
    mode: str
    optional: tuple[str, ...]
    unconditional: tuple[str, ...]
    blocked: frozenset[str]


class DirtyPlanner:
    def __init__(self, graph: Graph): self.graph=graph

    def plan(self, changes, *, unavailable=frozenset(), mode='incremental'):
        if mode not in {'incremental','full'} or not isinstance(unavailable,frozenset) or not unavailable.issubset(self.graph.ports):
            raise ContractError('unknown schedule or unavailable producer')
        dirty=set()
        for key, change in changes.items():
            if key not in self.graph.ports or not isinstance(change,FieldChange):
                raise ContractError('unknown field-change producer')
            if not change.fields.issubset(self.graph.ports[key].fields):
                raise ContractError('unknown raw field')
            if change.lineage_changed:
                dirty.update(self._affected_by_lineage(key))
            else:
                dirty.update(self.graph.affected_by_fields(key,change.fields))
        # An outage changes the effective input vector even if the numeric cache
        # still contains the previous value. Do not reuse that value silently.
        for key in unavailable:
            dirty.update(self._affected_by_lineage(key))
        blocked=set(unavailable)
        while True:
            before=len(blocked)
            blocked.update(p.id for p in self.graph.ports.values()
                           if any(not e.optional and e.source in blocked for e in p.inputs))
            if len(blocked)==before: break
        unconditional=tuple(k for k in self.graph.order if self.graph.ports[k].lane in {'market','account','timer'})
        optional=tuple(k for k in self.graph.order if self.graph.ports[k].lane=='optional'
                       and self.graph.ports[k].inputs and k not in blocked and (mode=='full' or k in dirty))
        return DirtyPlan(self.graph.version,mode,optional,unconditional,frozenset(blocked))

    def _affected_by_lineage(self, producer):
        immediate = {p.id for p in self.graph.ports.values() for e in p.inputs
                     if e.source == producer and e.lag_ns == 0}
        return self.graph.descendants(immediate)


@dataclass(frozen=True)
class CostSample:
    id: str
    producer: str
    received_at: int
    wall_ns: int
    cpu_ns: int
    censored: bool = False

    def __post_init__(self):
        timestamp(self.received_at)
        if (not isinstance(self.id,str) or not self.id or not isinstance(self.producer,str) or not self.producer
                or type(self.wall_ns) is not int or self.wall_ns <= 0 or type(self.cpu_ns) is not int or self.cpu_ns < 0
                or type(self.censored) is not bool):
            raise ContractError('measured runtime sample needs exact identity, receipt and nonnegative costs')


class RuntimeCosts:
    """Bounded chronological telemetry, not a fitted live latency model.

    After eviction, retrospective queries before the replacement receipt fail
    explicitly: a future sample must not silently alter an earlier decision.
    Censored/failed work is retained but does not masquerade as completion time.
    """
    def __init__(self, *, max_samples=4096, producer_window=16):
        if any(type(v) is not int or v<=0 for v in (max_samples,producer_window)):
            raise ContractError('runtime history needs positive limits')
        self.max_samples,self.producer_window=max_samples,producer_window
        self._samples=deque(); self._floor=None; self._replay_from=None

    def add(self, sample: CostSample):
        if not isinstance(sample,CostSample): raise ContractError('typed runtime sample required')
        for old in self._samples:
            if old.id==sample.id:
                if old!=sample: raise ContractError('runtime evidence ID conflict')
                return False
        if self._samples and sample.received_at<self._samples[-1].received_at:
            raise ContractError('runtime sample receipts must be ingested chronologically')
        if len(self._samples)==self.max_samples:
            self._floor=self._samples.popleft().received_at
            self._replay_from=sample.received_at
        self._samples.append(sample)
        return True

    def _available(self, producer, at):
        timestamp(at)
        if self._replay_from is not None and at<self._replay_from:
            raise ContractError('runtime cut precedes retained history; replay original telemetry')
        return [s for s in self._samples if s.producer==producer and s.received_at<=at]

    def estimate(self, producer, *, at, fallback_ns):
        if type(fallback_ns) is not int or fallback_ns<=0: raise ContractError('explicit positive fallback required')
        rows=[s.wall_ns for s in self._available(producer,at) if not s.censored][-self.producer_window:]
        return median_low(rows) if rows else fallback_ns

    def summary(self, producer, *, at):
        rows=self._available(producer,at)
        values=sorted(s.wall_ns for s in rows if not s.censored)
        def q(p): return values[max(0,ceil(p*len(values))-1)] if values else None
        return {'completed':len(values),'censored':sum(s.censored for s in rows),
                'p95_wall_ns':q(.95),'p99_wall_ns':q(.99),'cpu_ns':sum(s.cpu_ns for s in rows),
                'retained_from_exclusive':self._floor}


@dataclass(frozen=True)
class QueuePolicy:
    name: str = 'fifo'
    priorities: tuple[tuple[str,int], ...] = ()
    fallback_cost_ns: int = 1_000_000_000

    def __post_init__(self):
        if self.name not in {'fifo','deadline','deadline_cost'} or type(self.fallback_cost_ns) is not int or self.fallback_cost_ns<=0:
            raise ContractError('unknown optional policy or invalid registered fallback')
        if not isinstance(self.priorities,tuple) or any(not isinstance(v,tuple) or len(v)!=2 or
                not isinstance(v[0],str) or not v[0] or type(v[1]) is not int for v in self.priorities):
            raise ContractError('decision priorities must be immutable producer/integer pairs')
        if len({k for k,_ in self.priorities})!=len(self.priorities): raise ContractError('duplicate decision priority')

    @property
    def version(self): return digest(self)

    def select(self, requests, *, at, costs: RuntimeCosts):
        timestamp(at)
        if not requests: raise ContractError('empty optional queue')
        priorities=dict(self.priorities); candidates=[]
        for i,r in enumerate(requests):
            if r.submitted_at>at: raise ContractError('request has not arrived at scheduling cut')
            deadline=min(r.expires_at,r.horizon_end if r.horizon_end is not None else r.expires_at)
            estimate=costs.estimate(r.producer,at=at,fallback_ns=self.fallback_cost_ns)
            key=(i,) if self.name=='fifo' else ((deadline,-priorities.get(r.producer,0),i) if self.name=='deadline'
                else (-priorities.get(r.producer,0),deadline,estimate,i))
            candidates.append({'id':r.id,'deadline':deadline,'priority':priorities.get(r.producer,0),'estimated_wall_ns':estimate,'key':key})
        index=min(range(len(candidates)),key=lambda i:candidates[i]['key'])
        return index,{'policy':self.name,'policy_version':self.version,'at':at,'selected':requests[index].id,'candidates':candidates}
