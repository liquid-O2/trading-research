"""Reuse admitted point-in-time coordinates without rereading definition tape.

The original DefinitionIndex lookup is called directly on its retained lookup
interface. No price or lifetime is reconstructed. The validated NQZ4 snapshot
supplement is a narrowly bound alternative for its original ambiguity only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from types import MappingProxyType

from trading_research.data.ohlc import DefinitionIndex
from trading_research.errors import ContractError, IntegrityError


@dataclass(frozen=True)
class RetainedCoordinate:
    source_path: str
    source_row: int
    source_sha256: str
    raw_fields_sha256: str
    instrument_id: int
    raw_symbol: str
    contract_key: str
    lifetime_id: str
    definition_version: str
    known_at_ns: int
    valid_from_ns: int
    valid_until_ns: int
    tick_size: Decimal | None
    eligible: bool
    reason: str

    def __post_init__(self):
        if (any(type(v) is not int for v in (self.source_row, self.instrument_id, self.known_at_ns,
                                             self.valid_from_ns, self.valid_until_ns))
                or self.source_row < 0 or self.instrument_id < 1 or self.known_at_ns < 0
                or not 0 <= self.valid_from_ns < self.valid_until_ns
                or type(self.eligible) is not bool
                or any(type(v) is not str or not v for v in (
                    self.source_path, self.source_sha256, self.raw_fields_sha256, self.raw_symbol,
                    self.contract_key, self.lifetime_id, self.definition_version, self.reason))
                or self.tick_size is not None and (not self.tick_size.is_finite() or self.tick_size <= 0)):
            raise ContractError("retained coordinate omits its admitted exact identity/clock/terms")


@dataclass(frozen=True)
class RetainedBlock:
    source_path: str
    source_row: int
    source_sha256: str
    raw_fields_sha256: str
    instrument_id: int
    raw_symbol: str | None
    known_at_ns: int
    reason: str
    blocks_prior_lifetime: bool = True

    def __post_init__(self):
        if (any(type(value) is not int for value in (self.source_row,self.instrument_id,self.known_at_ns))
                or self.source_row<0 or self.instrument_id<1 or self.known_at_ns<0
                or self.blocks_prior_lifetime is not True
                or any(type(value) is not str or not value for value in
                    (self.source_path,self.source_sha256,self.raw_fields_sha256,self.reason))
                or self.raw_symbol is not None and (type(self.raw_symbol) is not str or not self.raw_symbol)):
            raise ContractError('retained definition block lacks its admitted identity and blocking clock')


class RetainedCoordinateIndex:
    def __init__(self, manifest, *, source_version, snapshot_supplement=None, snapshot_version=None):
        if (manifest.get("root") not in ("NQ", "ES") or not source_version
                or len(manifest.get("records", ())) != manifest.get("indexed_records")):
            raise ContractError("complete retained definition admission and immutable reference required")
        self.root = manifest["root"]
        self.source_version = source_version
        self.records = tuple(RetainedCoordinate(**{**row,
            "tick_size": None if row["tick_size"] is None else Decimal(row["tick_size"])})
            for row in manifest["records"])
        if any(not r.contract_key.startswith(self.root + ":") for r in self.records):
            raise IntegrityError("admitted coordinate root differs from its retained source")
        self.blocks = tuple(RetainedBlock(**row) for row in manifest["blocks"])
        self.unknown_instrument_ids = tuple(manifest["unknown_instrument_ids"])
        grouped, blocked = {}, {}
        for row in self.records:
            grouped.setdefault(row.instrument_id, []).append(row)
        for row in self.blocks:
            blocked.setdefault(row.instrument_id, []).append(row)
        self._by_instrument = MappingProxyType({k: tuple(v) for k, v in grouped.items()})
        self._blocks_by_instrument = MappingProxyType({k: tuple(v) for k, v in blocked.items()})
        self.snapshot, self.snapshot_version = None, snapshot_version
        self._snapshot_known = {}
        if snapshot_supplement is not None:
            source = snapshot_supplement
            candidate = source.get("candidate_report", {})
            if (self.root != "NQ" or not snapshot_version or source.get("actual_accepted") is not True
                    or source.get("generic_admission_untouched") is not True
                    or source.get("target_instrument_id") != 106364 or source.get("target_symbol") != "NQZ4"
                    or source.get("target_year") != 2024 or candidate.get("nonretroactive") is not True
                    or candidate.get("physical_coordinate", {}).get("tick_size") != "0.25"):
                raise IntegrityError("snapshot coordinate supplement lacks its exact accepted source binding")
            audited = [r for audit in source.get("audits", ()) for r in audit.get("target_relevant_fields", ())]
            by_version = {r.definition_version: r for r in self.records}
            if len(audited) != source.get("target_a_count") or len(audited) < 2:
                raise IntegrityError("the complete accepted snapshot record population is absent")
            for raw in audited:
                record = by_version.get(raw["definition_version"])
                known = max(raw["t"], raw["ts_recv"]) + 250_000_000
                if (record is None or record.known_at_ns != known
                        or (record.source_path, record.source_row, record.source_sha256, record.raw_fields_sha256)
                        != (raw["source_path"], raw["source_row"], raw["source_sha256"], raw["raw_fields_sha256"])
                        or record.instrument_id != 106364 or record.raw_symbol != "NQZ4"
                        or record.tick_size != Decimal("0.25") or raw["security_update_action"] != "A"):
                    raise IntegrityError("snapshot raw-row proof differs from retained definition coordinates")
                self._snapshot_known[record.definition_version] = known
            self.snapshot = candidate

    def resolve(self, instrument_id: int, event_ns: int):
        """Return the coordinate and a quality disposition at the event time.

        The original lookup checks known-at and physical lifetime separately.
        The event-delay scenario is applied by the observation consumer after
        this conservative source-availability check.
        """
        try:
            result = DefinitionIndex.resolve(self, instrument_id, event_ns)
        except IntegrityError as exc:
            if (str(exc) == "overlapping definition lifetimes for one raw instrument ID are ambiguous"
                    and self.snapshot is not None and instrument_id == 106364
                    and 1704067200000000000 <= event_ns < 1735689600000000000):
                candidate = self.snapshot
                # Select the newest known generic state first, respecting the
                # original block boundary. A newer unaudited or ineligible
                # update must not resurrect an older accepted snapshot.
                current=[r for r in self._by_instrument.get(instrument_id,()) if r.known_at_ns<=event_ns]
                blocks=[r.known_at_ns for r in self._blocks_by_instrument.get(instrument_id,()) if r.known_at_ns<=event_ns]
                if blocks:
                    current=[r for r in current if r.known_at_ns>max(blocks)]
                if current:
                    newest=max(r.known_at_ns for r in current)
                    current=[r for r in current if r.known_at_ns==newest]
                # Include every audited snapshot, not only versions selected
                # by the earlier minute-price correction, after that cut.
                known = self._snapshot_known
                records = [r for r in current
                           if r.definition_version in known and known[r.definition_version] <= event_ns
                           and r.known_at_ns == known[r.definition_version]
                           and r.valid_from_ns <= event_ns < r.valid_until_ns
                           and r.raw_symbol == "NQZ4" and r.tick_size == Decimal("0.25") and r.eligible]
                if len(current)==1 and records:
                    if len(records) == 1:
                        first = candidate["authoritative_original"]
                        if first["known_at_ns"] <= event_ns < candidate["physical_coordinate"]["expiration_ns"]:
                            return replace(records[0], contract_key=first["contract_key"]), "accepted_snapshot_supplement"
            return None, "ambiguous_definition: " + str(exc)
        if result is None:
            return None, "blocked_definition" if DefinitionIndex.is_blocked(self, instrument_id, event_ns) else "unavailable_definition"
        if not result.eligible or result.tick_size != Decimal("0.25"):
            return result, "unavailable_quarter_point_terms"
        return result, "accepted_original_definition"

    def change_points(self, instrument_id, start, end):
        values = {start, end}
        for row in self._by_instrument.get(instrument_id, ()):
            values.update(t for t in (row.known_at_ns, row.valid_from_ns, row.valid_until_ns) if start < t < end)
        for row in self._blocks_by_instrument.get(instrument_id, ()):
            if start < row.known_at_ns < end:
                values.add(row.known_at_ns)
        return tuple(sorted(values))
