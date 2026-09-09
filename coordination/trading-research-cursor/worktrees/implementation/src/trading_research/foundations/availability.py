"""Literal backward availability joins and a reference incremental index."""

from __future__ import annotations

from bisect import bisect_right, insort
from dataclasses import dataclass
from typing import Iterable

from trading_research.errors import ContractError
from trading_research.foundations.time import Clocks, timestamp


@dataclass(frozen=True)
class Observation:
    key: str
    id: str
    revision: int
    clocks: Clocks
    payload_json: bytes
    observed_at: int
    session: str | None = None
    eligible: bool = True
    reason: str | None = None

    def __post_init__(self) -> None:
        timestamp(self.observed_at)
        if (any(type(v) is not str or not v for v in (self.key, self.id))
                or type(self.revision) is not int or self.revision < 0
                or not isinstance(self.clocks, Clocks) or not isinstance(self.payload_json, bytes)
                or type(self.eligible) is not bool
                or any(v is not None and (type(v) is not str or not v) for v in (self.session, self.reason))):
            raise ContractError("invalid versioned observation")


@dataclass(frozen=True)
class JoinPolicy:
    max_age_ns: int
    session: str | None = None

    def __post_init__(self) -> None:
        if type(self.max_age_ns) is not int or self.max_age_ns < 0:
            raise ContractError("invalid maximum observation age")
        if self.session is not None and (type(self.session) is not str or not self.session):
            raise ContractError("join session must be a nonempty string")


def backward_reference(observations: Iterable[Observation], key: str, *, cut: int,
                       policy: JoinPolicy, valid_at: int | None = None) -> Observation | None:
    effective_cut = cut if valid_at is None else valid_at
    candidates = [o for o in observations if o.key == key and o.clocks.available(cut, valid_at=valid_at)
                  and o.observed_at <= effective_cut
                  and (policy.session is None or o.session == policy.session)]
    if not candidates:
        return None
    # A newer invalidating revision must not resurrect an older valid value.
    # Late delivery of an older observation cannot replace a newer observation.
    # Within the same observed timestamp, the latest available revision wins.
    order = lambda o: (o.observed_at, o.clocks.known_at, o.revision)
    newest = max(candidates, key=order)
    ties = [o for o in candidates if order(o) == order(newest)]
    if len({(o.payload_json, o.eligible, o.observed_at) for o in ties}) != 1:
        raise ContractError("conflicting overlapping acquisitions require a source priority contract")
    newest = min(ties, key=lambda o: o.id)
    if not newest.eligible or not 0 <= cut - newest.observed_at <= policy.max_age_ns:
        return None
    return newest


class AvailabilityIndex:
    def __init__(self) -> None:
        self._by_id: dict[str, Observation] = {}
        self._times: dict[str, list[tuple[int, int, str]]] = {}

    def append(self, observation: Observation) -> None:
        if not isinstance(observation, Observation):
            raise ContractError("typed immutable observation required")
        prior = self._by_id.get(observation.id)
        if prior is not None:
            if prior != observation:
                raise ContractError("observation ID reused with different content")
            return
        self._by_id[observation.id] = observation
        insort(self._times.setdefault(observation.key, []),
               (observation.clocks.known_at, observation.revision, observation.id))

    def asof(self, key: str, *, cut: int, policy: JoinPolicy, valid_at: int | None = None) -> Observation | None:
        order = self._times.get(key, [])
        n = bisect_right(order, (cut, float("inf"), ""))
        # Lookup narrows to the key/prefix; literal function remains the semantic oracle.
        return backward_reference((self._by_id[id] for _, _, id in order[:n]), key,
                                  cut=cut, policy=policy, valid_at=valid_at)

    def checkpoint(self) -> tuple[Observation, ...]:
        return tuple(self._by_id[id] for id in sorted(self._by_id))

    @classmethod
    def restore(cls, observations: Iterable[Observation]) -> AvailabilityIndex:
        index = cls()
        for observation in observations:
            index.append(observation)
        return index
