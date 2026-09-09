"""Versioned explicit fee and latency scenarios, never a zero-fee fallback."""

from dataclasses import dataclass
from decimal import Decimal
import json
from pathlib import Path

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.units import decimal_product, decimal_sum
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class FeeSchedule:
    id: str
    connection: str
    account_product: str
    currency: str
    per_side: tuple[tuple[str, Decimal], ...]
    source_urls: tuple[str, ...]
    verified_at: str
    evidence_hash: str
    historical_basis: str
    included: frozenset[str]

    def __post_init__(self):
        if (not all((self.id, self.connection, self.account_product, self.verified_at, self.evidence_hash))
                or self.currency != "USD" or not self.source_urls or not isinstance(self.per_side, tuple)):
            raise ContractError("economic replay needs a verified, versioned account-product fee schedule")
        if self.historical_basis not in {"published_benchmark_not_historical_account_cost", "verified_historical_terms"}:
            raise ContractError("historical cost basis must be explicit")
        if self.included != frozenset({"exchange", "regulatory", "clearing", "commission", "routing"}):
            raise DependencyUnavailable("all transaction-cost categories must be resolved")
        if len(dict(self.per_side)) != len(self.per_side) or any(
                not isinstance(value, Decimal) or not value.is_finite() or value <= 0 for _, value in self.per_side):
            raise ContractError("missing fees cannot become zero or duplicate product rows")

    @property
    def version(self):
        return digest(self)

    def fee(self, root: str, *, sides: int = 1, contracts: int = 1) -> Decimal:
        if type(sides) is not int or sides not in {1, 2} or type(contracts) is not int or contracts != 1:
            raise ContractError("primary fee accounting is for one mini, one or two explicit sides")
        try:
            return decimal_product(dict(self.per_side)[root], sides)
        except KeyError as exc:
            raise DependencyUnavailable(f"unverified fee product {root}") from exc


@dataclass(frozen=True)
class CostScenario:
    id: str
    fee_version: str
    feed_delay_ns: int
    outbound_delay_ns: int
    adverse_slippage_ticks: int
    receipt_basis: str
    execution_basis: str

    def __post_init__(self):
        if not all((self.id, self.fee_version, self.receipt_basis, self.execution_basis)):
            raise ContractError("cost/latency assumptions require identity and verified fees")
        if any(type(v) is not int or v < 0 for v in (self.feed_delay_ns, self.outbound_delay_ns, self.adverse_slippage_ticks)):
            raise ContractError("negative or fractional delay/slippage scenario")


def load_fee_scenarios(path: Path) -> tuple[FeeSchedule, ...]:
    data = json.loads(Path(path).read_text())
    evidence = data["verification"]
    if digest(evidence) != data["verification_hash"]:
        raise IntegrityError("fee verification facts/source provenance changed")
    result = []
    for row in data["schedules"]:
        result.append(FeeSchedule(**{**row, "per_side": tuple((root, Decimal(value)) for root, value in row["per_side"]),
                                    "source_urls": tuple(row["source_urls"]), "included": frozenset(row["included"]),
                                    "evidence_hash": data["verification_hash"]}))
    return tuple(result)


def sum_costs(*values: Decimal) -> Decimal:
    total = Decimal(0)
    for value in values:
        total = decimal_sum(total, value)
    return total
