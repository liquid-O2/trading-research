"""Bitemporal contract identity and purpose-specific eligibility (F02)."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.time import AvailabilityBasis, Clocks, timestamp
from trading_research.foundations.units import FuturesTerms
from trading_research.operations.artifacts import digest, json_value


@dataclass(frozen=True)
class InstrumentDefinition:
    key: InstrumentKey
    clocks: Clocks
    classification: str
    multiplier: Decimal | None
    tick_size: Decimal | None
    underlying_future_id: str | None = None
    leg_ids: tuple[str, ...] = ()
    deliverable_supported: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.key, InstrumentKey) or not isinstance(self.clocks, Clocks):
            raise ContractError("immutable instrument key and clocks required")
        if self.classification not in {"future", "option", "spread", "equity", "unknown"}:
            raise ContractError("unknown instrument classification")
        if not isinstance(self.key.definition_version, str) or not self.key.definition_version:
            raise ContractError("definition version is mandatory")
        if self.key.expiry_at is not None:
            timestamp(self.key.expiry_at)
        if self.clocks.valid_from is None or self.clocks.valid_until is None:
            raise ContractError("bitemporal definition requires a valid interval")
        if (not isinstance(self.leg_ids, tuple) or any(not isinstance(v, str) or not v for v in self.leg_ids)
                or len(set(self.leg_ids)) != len(self.leg_ids)
                or type(self.deliverable_supported) is not bool):
            raise ContractError("immutable distinct leg identities and explicit deliverable eligibility required")
        if self.underlying_future_id is not None and (not isinstance(self.underlying_future_id, str) or not self.underlying_future_id):
            raise ContractError("underlying future ID must be explicit text")
        for value in (self.multiplier, self.tick_size):
            if value is not None and (not isinstance(value, Decimal) or not value.is_finite() or value <= 0):
                raise ContractError("sentinel/invalid contract term must be resolved before registry entry")

    def eligibility(self, purpose: str) -> tuple[bool, str]:
        if purpose == "raw_flow":
            return True, "raw contract counts retain their identity without inferred valuation"
        if purpose not in {"valuation", "execution"}:
            raise ContractError("unknown instrument use")
        if self.classification in {"unknown", "spread"} or not self.deliverable_supported:
            return False, "unknown, spread or unsupported deliverable"
        if self.multiplier is None or (purpose == "execution" and self.tick_size is None):
            return False, "required multiplier/tick terms missing"
        if self.classification == "option" and any(x is None for x in (
                self.key.expiry_at, self.key.strike, self.key.right, self.key.exercise, self.key.settlement)):
            return False, "option payoff/exercise/settlement identity incomplete"
        if self.classification == "option" and self.key.settlement == "future" and not self.underlying_future_id:
            return False, "specific underlying future is missing"
        return True, "known purpose-specific terms"

    def futures_terms(self) -> FuturesTerms:
        eligible, reason = self.eligibility("execution")
        if not eligible or self.classification != "future" or self.key.underlying not in {"NQ", "ES"}:
            raise DependencyUnavailable(f"primary execution definition unavailable: {reason}")
        return FuturesTerms(self.key.underlying, self.tick_size, self.multiplier, self.key.definition_version)


def instrument_identity(definition: InstrumentDefinition) -> str:
    """Price coordinate identity for this instrument lifetime, without a display alias."""
    key = definition.key
    return digest((key.provider, key.venue, key.instrument_id, key.raw_symbol, key.expiry_at,
                   definition.clocks.valid_from, definition.clocks.valid_until))


@dataclass(frozen=True)
class InstrumentRetirement:
    id: str
    previous_definition_version: str
    instrument_lifetime: str
    effective_at: int
    clocks: Clocks

    def __post_init__(self):
        timestamp(self.effective_at)
        if (any(not isinstance(v, str) or not v for v in (self.id, self.previous_definition_version, self.instrument_lifetime))
                or not isinstance(self.clocks, Clocks)):
            raise ContractError("retirement needs source identity and the exact prior instrument lifetime")


def _restore_clocks(value: dict) -> Clocks:
    return Clocks(**{**value, 'basis': AvailabilityBasis(value['basis'])})


def _decimal(value):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {'$decimal'}:
        raise ContractError("checkpoint decimal encoding is invalid")
    return Decimal(value['$decimal'])


class InstrumentRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, InstrumentDefinition] = {}
        self._retirements: dict[str, InstrumentRetirement] = {}

    def append(self, definition: InstrumentDefinition) -> None:
        if not isinstance(definition, InstrumentDefinition):
            raise ContractError("registry requires an immutable instrument definition")
        id = definition.key.definition_version
        prior = self._definitions.get(id)
        if prior is not None and prior != definition:
            raise ContractError("immutable instrument definition version changed")
        self._definitions[id] = definition

    def retire(self, retirement: InstrumentRetirement) -> None:
        if not isinstance(retirement, InstrumentRetirement):
            raise ContractError("registry retirement requires its immutable event")
        parent = self._definitions.get(retirement.previous_definition_version)
        if parent is None:
            raise DependencyUnavailable("retirement references a missing prior definition")
        if instrument_identity(parent) != retirement.instrument_lifetime:
            raise ContractError("retirement cannot cross instrument lifetimes")
        if parent.clocks.known_at >= retirement.clocks.known_at:
            raise ContractError("retirement ordering must be known after its prior definition")
        if retirement.effective_at < parent.clocks.valid_from:
            raise ContractError("retirement predates the instrument's lifetime")
        prior = self._retirements.get(retirement.id)
        if prior is not None and prior != retirement:
            raise ContractError("immutable retirement version changed")
        self._retirements[retirement.id] = retirement

    def resolve(self, *, provider: str, venue: str, instrument_id: str,
                valid_at: int, known_at: int) -> InstrumentDefinition | None:
        timestamp(valid_at)
        timestamp(known_at)
        if any(not isinstance(v, str) or not v for v in (provider, venue, instrument_id)):
            raise ContractError("registry query requires provider, venue and instrument ID")
        candidates = [d for d in self._definitions.values()
                      if (d.key.provider, d.key.venue, d.key.instrument_id) == (provider, venue, instrument_id)
                      and d.clocks.available(known_at, valid_at=valid_at)]
        if not candidates:
            return None
        lifetimes = {instrument_identity(d) for d in candidates}
        if len(lifetimes) != 1:
            raise ContractError("ambiguous overlapping instrument lifetimes require explicit reconciliation")
        # A correction does not revoke a deletion. Reinstatement is a distinct,
        # currently unsupported event; disjoint reused IDs have another lifetime.
        if any(r.instrument_lifetime in lifetimes and r.clocks.known_at <= known_at and r.effective_at <= valid_at
               for r in self._retirements.values()):
            return None
        latest = max(d.clocks.known_at for d in candidates)
        candidates = [d for d in candidates if d.clocks.known_at == latest]
        if len(candidates) != 1:
            raise ContractError("ambiguous same-time instrument definition")
        return candidates[0]

    def checkpoint(self) -> dict:
        body = json_value({'schema': 'instrument-registry-v2',
                           'definitions': tuple(self._definitions[k] for k in sorted(self._definitions)),
                           'retirements': tuple(self._retirements[k] for k in sorted(self._retirements))})
        return {**body, 'content_hash': digest(body)}

    @classmethod
    def restore(cls, checkpoint: dict):
        if not isinstance(checkpoint, dict) or set(checkpoint) != {'schema', 'definitions', 'retirements', 'content_hash'}:
            raise ContractError("invalid instrument checkpoint envelope")
        body = {k: v for k, v in checkpoint.items() if k != 'content_hash'}
        if body['schema'] != 'instrument-registry-v2' or digest(body) != checkpoint['content_hash']:
            raise ContractError("instrument checkpoint version/content mismatch")
        result = cls()
        try:
            for value in body['definitions']:
                key = InstrumentKey(**{**value['key'], 'strike': _decimal(value['key']['strike'])})
                definition = InstrumentDefinition(**{**value, 'key': key, 'clocks': _restore_clocks(value['clocks']),
                    'multiplier': _decimal(value['multiplier']), 'tick_size': _decimal(value['tick_size']),
                    'leg_ids': tuple(value['leg_ids'])})
                result.append(definition)
            for value in body['retirements']:
                result.retire(InstrumentRetirement(**{**value, 'clocks': _restore_clocks(value['clocks'])}))
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise ContractError("invalid instrument checkpoint record") from exc
        if result.checkpoint() != checkpoint:
            raise ContractError("instrument checkpoint has duplicate or noncanonical records")
        return result
