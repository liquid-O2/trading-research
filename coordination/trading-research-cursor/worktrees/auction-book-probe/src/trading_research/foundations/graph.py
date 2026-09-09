"""Compile named runtime ports, capabilities, clocks and dependency closures."""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from types import MappingProxyType
from typing import Iterable, Mapping

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.contracts import Capability
from trading_research.foundations.time import Clocks, timestamp
from trading_research.foundations.units import Unit
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class InputPort:
    source: str
    schema: str
    fields: frozenset[str]
    unit: Unit | None = None
    target_id: str | None = None
    required_capabilities: frozenset[Capability] = frozenset()
    lag_ns: int = 0
    max_age_ns: int | None = None
    optional: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.fields, frozenset) or not isinstance(self.required_capabilities, frozenset):
            raise ContractError("input field/capability declarations must be immutable")
        if (any(type(v) is not str or not v for v in (self.source, self.schema, *self.fields))
                or any(not isinstance(v, Capability) for v in self.required_capabilities)
                or (self.target_id is not None and (type(self.target_id) is not str or not self.target_id))
                or (self.unit is not None and not isinstance(self.unit, Unit))
                or type(self.optional) is not bool or type(self.lag_ns) is not int or self.lag_ns < 0):
            raise ContractError("invalid input port/lag")
        if self.max_age_ns is not None and (type(self.max_age_ns) is not int or self.max_age_ns < self.lag_ns):
            raise ContractError("maximum age is below the required lag")


@dataclass(frozen=True)
class Port:
    id: str
    owner: str
    stage: int
    schema: str
    fields: frozenset[str]
    inputs: tuple[InputPort, ...] = ()
    unit: Unit | None = None
    target_id: str | None = None
    capabilities: frozenset[Capability] = frozenset()
    learned: bool = False
    lane: str = "optional"

    def __post_init__(self) -> None:
        if not isinstance(self.fields, frozenset) or not isinstance(self.capabilities, frozenset) or not isinstance(self.inputs, tuple):
            raise ContractError("producer fields, capabilities and dependency edges must be immutable")
        if (any(type(v) is not str or not v for v in (self.id, self.owner, self.schema, *self.fields))
                or any(not isinstance(v, Capability) for v in self.capabilities)
                or any(not isinstance(v, InputPort) for v in self.inputs)
                or (self.target_id is not None and (type(self.target_id) is not str or not self.target_id))
                or (self.unit is not None and not isinstance(self.unit, Unit))
                or type(self.learned) is not bool or type(self.stage) is not int or self.stage < 0):
            raise ContractError("invalid producer port")
        if type(self.lane) is not str or self.lane not in {"optional", "market", "account", "timer", "offline"}:
            raise ContractError("invalid scheduler lane")
        if len({i.source for i in self.inputs}) != len(self.inputs):
            raise ContractError("duplicate input edge")


@dataclass(frozen=True)
class PublishedVersion:
    port_id: str
    id: str
    decision_cut: int
    clocks: Clocks
    input_versions: tuple[str, ...]
    payload_hash: str
    horizon_end: int | None = None

    def __post_init__(self) -> None:
        timestamp(self.decision_cut)
        if (any(type(v) is not str or not v for v in (self.port_id, self.id, self.payload_hash))
                or not isinstance(self.clocks, Clocks)):
            raise ContractError("published version requires typed clocks and string identities")
        if (not isinstance(self.input_versions, tuple)
                or any(type(v) is not str or not v for v in self.input_versions)
                or len(set(self.input_versions)) != len(self.input_versions)):
            raise ContractError("published inputs must preserve immutable unique evidence identities")
        if self.horizon_end is not None:
            timestamp(self.horizon_end)
            if self.horizon_end <= self.decision_cut:
                raise ContractError("forecast end must follow its original cut")


@dataclass(frozen=True, init=False)
class Graph:
    ports: Mapping[str, Port]
    children: Mapping[str, frozenset[str]]
    order: tuple[str, ...]
    version: str

    def __init__(self, ports: Iterable[Port]):
        records = tuple(ports)
        by_id = {p.id: p for p in records}
        if len(by_id) != len(records):
            raise ContractError("duplicate producer ID")
        children = {id: set() for id in by_id}
        degrees = {id: 0 for id in by_id}
        for consumer in records:
            for edge in consumer.inputs:
                if edge.source not in by_id:
                    raise ContractError(f"unknown port {edge.source} for {consumer.id}")
                producer = by_id[edge.source]
                if producer.schema != edge.schema or not edge.fields.issubset(producer.fields):
                    raise ContractError(f"schema/field mismatch: {edge.source} -> {consumer.id}")
                if edge.unit != producer.unit or edge.target_id != producer.target_id:
                    raise ContractError(f"unit/target mismatch: {edge.source} -> {consumer.id}")
                if not edge.required_capabilities.issubset(producer.capabilities):
                    raise ContractError(f"incompatible capability: {edge.source} -> {consumer.id}")
                if edge.lag_ns == 0:
                    if producer.stage > consumer.stage:
                        raise ContractError(f"same-batch stage feedback: {edge.source} -> {consumer.id}")
                    children[producer.id].add(consumer.id)
                    degrees[consumer.id] += 1
                elif edge.max_age_ns is None:
                    raise ContractError("lagged state must declare a maximum age")
        queue = [id for id, degree in degrees.items() if degree == 0]
        heapq.heapify(queue)
        order = []
        while queue:
            id = heapq.heappop(queue)
            order.append(id)
            for child in sorted(children[id]):
                degrees[child] -= 1
                if degrees[child] == 0:
                    heapq.heappush(queue, child)
        if len(order) != len(records):
            raise ContractError(f"same-batch dependency cycle: {sorted(k for k, v in degrees.items() if v)}")
        object.__setattr__(self, "ports", MappingProxyType(by_id))
        object.__setattr__(self, "children", MappingProxyType({id: frozenset(values) for id, values in children.items()}))
        object.__setattr__(self, "order", tuple(order))
        object.__setattr__(self, "version", digest(sorted(records, key=lambda p: p.id)))

    def descendants(self, changed: Iterable[str]) -> frozenset[str]:
        changed = set(changed)
        if not changed.issubset(self.ports):
            raise ContractError("unknown dirty port")
        result = set(changed)
        queue = list(changed)
        while queue:
            for child in self.children[queue.pop()]:
                if child not in result:
                    result.add(child)
                    queue.append(child)
        return frozenset(result)

    def affected_by_fields(self, producer: str, changed_fields: frozenset[str]) -> frozenset[str]:
        if producer not in self.ports or not changed_fields.issubset(self.ports[producer].fields):
            raise ContractError("unknown changed field")
        immediate = {p.id for p in self.ports.values() for e in p.inputs
                     if e.source == producer and e.lag_ns == 0 and e.fields.intersection(changed_fields)}
        return self.descendants(immediate)

    def validate_inputs(self, consumer: str, versions: dict[str, PublishedVersion], *, cut: int,
                        available_at: int | None = None) -> tuple[str, ...]:
        timestamp(cut)
        assembled_at = cut if available_at is None else timestamp(available_at)
        if assembled_at < cut:
            raise ContractError("assembly time precedes the frozen observation cut")
        port = self.ports[consumer]
        expected = {e.source for e in port.inputs}
        if set(versions) - expected:
            raise ContractError("undeclared model inputs")
        admitted = []
        for edge in port.inputs:
            value = versions.get(edge.source)
            if value is None:
                if edge.optional:
                    continue
                raise DependencyUnavailable(f"missing required port: {edge.source}")
            if value.port_id != edge.source or not value.clocks.available(assembled_at):
                raise DependencyUnavailable(f"future or invalid input: {edge.source}")
            if value.clocks.known_at > cut and (edge.lag_ns > 0 or not self.ports[edge.source].inputs):
                raise ContractError("late external or preceding-state data cannot be spliced into a frozen cut")
            if edge.lag_ns == 0 and value.decision_cut != cut:
                raise ContractError("mixed decision cuts require an explicitly lagged edge")
            if edge.lag_ns and value.decision_cut > cut - edge.lag_ns:
                raise ContractError("current state disguised as lagged feedback")
            if edge.max_age_ns is not None and cut - value.decision_cut > edge.max_age_ns:
                raise DependencyUnavailable("input exceeds declared maximum age")
            if value.horizon_end is not None and assembled_at >= value.horizon_end:
                raise DependencyUnavailable("expired forecast; original horizon cannot restart")
            admitted.append(value.id)
        return tuple(admitted)

    def validate_fit_order(self, order: Iterable[str]) -> None:
        actual = tuple(order)
        expected = {p.id for p in self.ports.values() if p.learned}
        if set(actual) != expected or len(actual) != len(expected):
            raise ContractError("missing, duplicate or non-learned fit node")
        positions = {id: n for n, id in enumerate(actual)}
        # Traverse through deterministic intermediates as well as learned edges.
        for producer in expected:
            for consumer in self.descendants([producer]).intersection(expected) - {producer}:
                if positions[producer] >= positions[consumer]:
                    raise ContractError("fit order violates the transitive OOF graph")
