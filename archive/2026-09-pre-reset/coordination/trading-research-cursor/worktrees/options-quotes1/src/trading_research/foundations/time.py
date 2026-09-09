"""Nanosecond clock contracts; observed and assumed availability stay distinct."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Iterable

from trading_research.errors import ContractError

NS = 1_000_000_000
MINUTE = 60 * NS
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def timestamp(value: int) -> int:
    if type(value) is not int or not -(2 ** 63) <= value < 2 ** 63:
        raise ContractError("timestamp must be signed int64 UTC nanoseconds, without sentinels")
    return value


def datetime_ns(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ContractError("naive local time is ambiguous")
    delta = value.astimezone(timezone.utc) - EPOCH
    return timestamp((delta.days * 86400 + delta.seconds) * NS + delta.microseconds * 1000)


class AvailabilityBasis(StrEnum):
    RECEIVED = "actual_strategy_receipt"
    PUBLISHED = "documented_publication"
    ASSUMED = "historical_latency_assumption"
    COMPUTED = "actual_computation"


@dataclass(frozen=True)
class Clocks:
    event_at: int | None
    known_at: int
    source_version: str
    basis: AvailabilityBasis
    received_at: int | None = None
    provider_received_at: int | None = None
    published_at: int | None = None
    computed_at: int | None = None
    valid_from: int | None = None
    valid_until: int | None = None
    clock_uncertainty_ns: int = 0
    assumption_id: str | None = None

    def __post_init__(self) -> None:
        timestamp(self.known_at)
        for value in (self.event_at, self.received_at, self.provider_received_at,
                      self.published_at, self.computed_at, self.valid_from, self.valid_until):
            if value is not None:
                timestamp(value)
        if not isinstance(self.basis, AvailabilityBasis) or type(self.source_version) is not str or not self.source_version:
            raise ContractError("clock basis and source version required")
        if self.assumption_id is not None and (type(self.assumption_id) is not str or not self.assumption_id):
            raise ContractError("clock assumption identity must be a nonempty string")
        if type(self.clock_uncertainty_ns) is not int or self.clock_uncertainty_ns < 0:
            raise ContractError("invalid clock uncertainty")
        if self.valid_from is not None and self.valid_until is not None and self.valid_until <= self.valid_from:
            raise ContractError("invalid validity interval")
        if self.basis == AvailabilityBasis.ASSUMED and not self.assumption_id:
            raise ContractError("missing receipt requires a named latency assumption")
        required = {AvailabilityBasis.RECEIVED: self.received_at,
                    AvailabilityBasis.PUBLISHED: self.published_at,
                    AvailabilityBasis.COMPUTED: self.computed_at}.get(self.basis)
        if self.basis != AvailabilityBasis.ASSUMED and required is None:
            raise ContractError("observed availability basis lacks its observed timestamp")
        if any(at is not None and self.known_at < at
               for at in (self.received_at, self.published_at, self.computed_at)):
            raise ContractError("availability precedes a required receipt, publication or computation")

    def available(self, cut: int, *, valid_at: int | None = None) -> bool:
        timestamp(cut)
        at = cut if valid_at is None else timestamp(valid_at)
        return (self.known_at <= cut and (self.valid_from is None or self.valid_from <= at)
                and (self.valid_until is None or at < self.valid_until))


def derived_clocks(inputs: Iterable[Clocks], *, source_version: str,
                   actual_completion_at: int | None = None,
                   confirmation_known_at: int | None = None,
                   simulated_start_at: int | None = None,
                   simulated_duration_ns: int | None = None,
                   assumption_id: str | None = None) -> Clocks:
    inputs = tuple(inputs)
    if not inputs:
        raise ContractError("derived output needs declared input clocks")
    latest = max(c.known_at for c in inputs)
    confirmation = latest if confirmation_known_at is None else timestamp(confirmation_known_at)
    if actual_completion_at is not None:
        if simulated_start_at is not None or simulated_duration_ns is not None:
            raise ContractError("observed completion and modeled compute delay cannot both be charged")
        completed = timestamp(actual_completion_at)
        basis = AvailabilityBasis.COMPUTED
    else:
        if simulated_start_at is None or simulated_duration_ns is None or not assumption_id:
            raise ContractError("unobserved completion requires explicit simulated start/duration/assumption")
        if type(simulated_duration_ns) is not int or simulated_duration_ns < 0:
            raise ContractError("invalid duration")
        completed = timestamp(max(timestamp(simulated_start_at), latest) + simulated_duration_ns)
        basis = AvailabilityBasis.ASSUMED
    return Clocks(event_at=max((c.event_at for c in inputs if c.event_at is not None), default=None),
                  known_at=max(latest, confirmation, completed), source_version=source_version,
                  basis=basis, computed_at=completed if basis == AvailabilityBasis.COMPUTED else None,
                  clock_uncertainty_ns=max(c.clock_uncertainty_ns for c in inputs), assumption_id=assumption_id)
