"""VWAP/dispersion references, prior edges, and density-matched controls."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from typing import Any, Mapping, Sequence
import json

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage, EvidenceRef, Formation, Reference
from trading_research.research.rule_discovery.native import PrefixSums, TICK, ticks_to_decimal, vwap_from_prefix, python_vwap

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
CONTROL_OFFSETS = (-2, -1, 1, 2)


def vwap_dispersion(ticks: Sequence[int], sizes: Sequence[int]) -> dict[str, Any]:
    vector_price, vector_disp, volume = python_vwap(list(ticks), list(sizes))
    return {"price": vector_price, "dispersion": vector_disp, "volume": volume}


def vwap_from_market(prefix: PrefixSums, start_ns: int, end_ns: int) -> dict[str, Any]:
    price, disp, volume = vwap_from_prefix(prefix, start_ns, end_ns)
    return {"price": price, "dispersion": disp, "volume": volume}


def lifecycle_id(*, family: str, branch: str, contract: str, formation_id: str, kind: str) -> str:
    payload = json.dumps(
        {"family": family, "branch": branch, "contract": contract, "formation_id": formation_id, "kind": kind},
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode()).hexdigest()


def r1_frozen_band(
    *,
    formation: Formation,
    vwap: Decimal,
    dispersion: Decimal,
    issue_at_ns: int,
    expiry_at_ns: int,
    family: str,
    branch: str,
    contract: str,
) -> Reference:
    if issue_at_ns < formation.available_at_ns:
        raise ContractError("formation unavailable at issue time")
    if expiry_at_ns < issue_at_ns:
        raise ContractError("expiry precedes issue")
    lower = vwap - dispersion
    upper = vwap + dispersion
    lid = lifecycle_id(family=family, branch=branch, contract=contract, formation_id=formation.formation_id, kind="R1")
    return Reference(
        reference_id=f"{lid}:{issue_at_ns}",
        reference_lifecycle_id=lid,
        formation_id=formation.formation_id,
        asset_id=formation.asset_id,
        lower=lower,
        upper=upper,
        issue_at_ns=issue_at_ns,
        expiry_at_ns=expiry_at_ns,
        permitted_sides=(-1, 1),
        evidence=formation.evidence,
    )


def r2_prior_edge(
    *,
    formation: Formation,
    edge: str,
    issue_at_ns: int,
    expiry_at_ns: int,
    family: str,
    branch: str,
    contract: str,
) -> Reference:
    if issue_at_ns < formation.available_at_ns:
        raise ContractError("formation unavailable at issue time")
    price = formation.high if edge == "high" else formation.low
    lid = lifecycle_id(family=family, branch=branch, contract=contract, formation_id=formation.formation_id, kind="R2")
    return Reference(
        reference_id=f"{lid}:{edge}:{issue_at_ns}",
        reference_lifecycle_id=lid,
        formation_id=formation.formation_id,
        asset_id=formation.asset_id,
        lower=price,
        upper=price,
        issue_at_ns=issue_at_ns,
        expiry_at_ns=expiry_at_ns,
        permitted_sides=(-1, 1),
        evidence=formation.evidence,
    )


def control_offset(reference_id: str) -> int:
    digest = sha256(reference_id.encode()).hexdigest()
    return CONTROL_OFFSETS[int(digest, 16) % 4]


def density_matched_control(
    reference: Reference,
    *,
    scale: Decimal,
    occupied: Sequence[tuple[Decimal, Decimal]],
) -> dict[str, Any]:
    start = CONTROL_OFFSETS.index(control_offset(reference.reference_id))
    width = reference.upper - reference.lower
    for step in range(4):
        offset = CONTROL_OFFSETS[(start + step) % 4]
        shift = scale * offset
        lower = reference.lower + shift
        upper = reference.upper + shift
        duplicate = any(abs(lower - lo) <= TICK and abs(upper - hi) <= TICK for lo, hi in occupied)
        if not duplicate:
            return {
                "available": True,
                "offset": offset,
                "lower": lower,
                "upper": upper,
                "width": width,
                "issue_at_ns": reference.issue_at_ns,
                "expiry_at_ns": reference.expiry_at_ns,
            }
    return {"available": False, "reason": "all control offsets duplicate a real band"}


def developing_version(parent: Reference, *, vwap: Decimal, dispersion: Decimal, issue_at_ns: int) -> Reference:
    if issue_at_ns < parent.issue_at_ns:
        raise ContractError("version issue precedes parent")
    return Reference(
        reference_id=f"{parent.reference_lifecycle_id}:{issue_at_ns}",
        reference_lifecycle_id=parent.reference_lifecycle_id,
        formation_id=parent.formation_id,
        asset_id=parent.asset_id,
        lower=vwap - dispersion,
        upper=vwap + dispersion,
        issue_at_ns=issue_at_ns,
        expiry_at_ns=parent.expiry_at_ns,
        permitted_sides=parent.permitted_sides,
        evidence=parent.evidence,
    )


@dataclass(frozen=True, slots=True)
class ReferenceCase:
    case_id: str
    kind: str
    available: bool
