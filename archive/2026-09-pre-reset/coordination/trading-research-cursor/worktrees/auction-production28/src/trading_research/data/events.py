"""Lossless source values and canonical MBP messages (F01.DECODER)."""

from dataclasses import dataclass
from decimal import Decimal
from enum import IntFlag
import json
import math
import re
import struct
from typing import Any, Mapping

from trading_research.errors import ContractError
from trading_research.foundations.time import AvailabilityBasis, Clocks, timestamp
from trading_research.foundations.units import decimal_product
from trading_research.operations.artifacts import canonical_json, digest

DECODER_VERSION = "mbp-literal-v4"
UNDEF_PRICE = 2**63 - 1
MBP_EXPORT_FIELDS = frozenset({"t", "action", "side", "price", "size", "flags", "instrument_id",
                               "bid_px", "ask_px", "bid_sz", "ask_sz"})
MBP_NATIVE_FIELDS = frozenset({"ts_event", "ts_recv", "action", "side", "price", "size", "flags", "instrument_id",
                               "bid_px_00", "ask_px_00", "bid_sz_00", "ask_sz_00", "publisher_id", "sequence", "depth"})


class Flags(IntFlag):
    RESERVED = 1
    PUBLISHER_SPECIFIC = 2
    MAYBE_BAD_BOOK = 4
    BAD_TS_RECV = 8
    MBP = 16
    SNAPSHOT = 32
    TOB = 64
    LAST = 128


def encode_fields(fields: Mapping[str, Any]) -> bytes:
    """Preserve float bits/sentinels without writing nonfinite JSON numbers."""
    encoded = []
    for key, value in fields.items():
        if isinstance(value, float):
            cell = ["float64", struct.pack(">d", value).hex()]
        elif type(value) in (str, int, bool) or value is None:
            cell = [type(value).__name__, value]
        elif isinstance(value, bytes):
            cell = ["bytes", value.hex()]
        else:
            raise ContractError(f"unregistered raw source type for {key}: {type(value).__name__}")
        encoded.append([key, cell])
    return canonical_json(encoded)


def decode_fields(payload: bytes) -> dict[str, Any]:
    result = {}
    for key, (kind, value) in json.loads(payload):
        if key in result:
            raise ContractError("duplicate raw column")
        if kind == "float64":
            value = struct.unpack(">d", bytes.fromhex(value))[0]
        elif kind == "bytes":
            value = bytes.fromhex(value)
        elif kind not in {"str", "int", "bool", "NoneType"}:
            raise ContractError("unsupported raw type tag")
        result[key] = value
    return result


@dataclass(frozen=True)
class SourceAddress:
    dataset_id: str
    acquisition_version: str
    relative_path: str
    container_version: str
    partition: str
    row: int
    schema_version: str
    full_file_sha256: str | None = None

    def __post_init__(self) -> None:
        if (not all((self.dataset_id, self.acquisition_version, self.relative_path,
                     self.container_version, self.partition, self.schema_version))
                or type(self.row) is not int or self.row < 0):
            raise ContractError("raw event requires an explicit source-row address/version")
        if self.full_file_sha256 is not None and (not isinstance(self.full_file_sha256, str)
                or not re.fullmatch(r"[0-9a-f]{64}", self.full_file_sha256)):
            raise ContractError("whole-file content identity requires a SHA-256, not a metadata fingerprint")

    @property
    def source_version(self) -> str:
        return self.full_file_sha256 or self.container_version

    @property
    def id(self) -> str:
        if self.full_file_sha256 is not None:
            # Locators remain in the address as evidence. Verified aliases of
            # the same acquired bytes do not create additional economic events.
            return digest({"identity_version": "source-content-v1", "dataset": self.dataset_id,
                           "acquisition": self.acquisition_version, "sha256": self.full_file_sha256,
                           "partition": self.partition, "row": self.row, "schema": self.schema_version})
        return digest(self)


@dataclass(frozen=True)
class LatencyScenario:
    id: str
    anchor: str
    delay_ns: int
    uncertainty_ns: int

    def __post_init__(self) -> None:
        if (not self.id or self.anchor not in {"event", "provider_received"}
                or any(type(v) is not int or v < 0 for v in (self.delay_ns, self.uncertainty_ns))):
            raise ContractError("historical receipt needs a named nonnegative latency/uncertainty scenario")


@dataclass(frozen=True)
class Quote:
    bid: Decimal | None
    ask: Decimal | None
    bid_size: int | None
    ask_size: int | None
    bid_count: int | None = None
    ask_count: int | None = None

    @property
    def valid(self) -> bool:
        return (self.bid is not None and self.ask is not None and self.bid <= self.ask
                and self.bid_size is not None and self.ask_size is not None
                and self.bid_size > 0 and self.ask_size > 0)


@dataclass(frozen=True)
class CanonicalEvent:
    address: SourceAddress
    raw_fields: bytes
    raw_record: bytes | None
    instrument_id: int
    clocks: Clocks
    action: str | None
    reported_side: str | None
    flags: Flags
    price: Decimal | None
    size: int | None
    quote: Quote | None
    quote_association: str
    provider_sequence: int | None
    publisher_id: int | None
    depth: int | None
    quality_reasons: tuple[str, ...]
    decoder_version: str = DECODER_VERSION

    @property
    def id(self) -> str:
        return digest({"source_row_id": self.address.id, "raw_fields": self.raw_fields, "raw_record": self.raw_record,
                       "decoder": self.decoder_version})

    @property
    def aggressor(self) -> int | None:
        return {"B": 1, "A": -1}.get(self.reported_side) if self.action == "T" else None

    @property
    def trade_eligible(self) -> bool:
        # F_LAST and book health do not determine inclusion of observed trades.
        return self.action == "T" and self.size is not None and self.size > 0 and not (self.flags & Flags.SNAPSHOT)


def _character(value: Any, allowed: set[str]) -> str | None:
    if isinstance(value, bytes):
        try:
            value = value.decode("ascii")
        except UnicodeDecodeError:
            return None
    elif type(value) is int:
        value = chr(value) if 0 <= value <= 127 else None
    return value if value in allowed else None


def _price(value: Any, *, native: bool) -> Decimal | None:
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return None
    if native:
        if type(value) is not int or value == UNDEF_PRICE:
            return None
        return decimal_product(value, Decimal("0.000000001"))
    if type(value) not in (float, int):
        raise ContractError("QuantPad MBP price must preserve its numeric physical type")
    # Decimal.from_float retains the actual exported value, including an off-tick residual.
    return Decimal.from_float(value) if isinstance(value, float) else Decimal(value)


def _size(value: Any) -> int | None:
    return value if type(value) is int and 0 <= value < 2**32 - 1 else None


def normalize_mbp(fields: Mapping[str, Any], address: SourceAddress, *, native: bool,
                  scenario: LatencyScenario | None, strategy_received_at: int | None = None,
                  raw_record: bytes | None = None) -> CanonicalEvent:
    required = MBP_NATIVE_FIELDS if native else MBP_EXPORT_FIELDS
    if not required.issubset(fields):
        raise ContractError(f"source MBP schema lacks supplied contract fields: {sorted(required - fields.keys())}")
    raw = encode_fields(fields)
    event_at = timestamp(fields["ts_event" if native else "t"])
    received = fields.get("ts_recv") if native else None
    provider_at = None if received in {None, 2**64 - 1} else timestamp(received)
    if strategy_received_at is not None:
        c = Clocks(event_at, timestamp(strategy_received_at), address.source_version, AvailabilityBasis.RECEIVED,
                   received_at=strategy_received_at, provider_received_at=provider_at,
                   clock_uncertainty_ns=scenario.uncertainty_ns if scenario else 0)
    else:
        if scenario is None:
            raise ContractError("archive lacks actual strategy receipt; no implicit zero-lag clock")
        base = event_at if scenario.anchor == "event" else provider_at
        if base is None:
            raise ContractError("latency scenario requires a provider-receive field absent from this source")
        c = Clocks(event_at, timestamp(base + scenario.delay_ns), address.source_version, AvailabilityBasis.ASSUMED,
                   provider_received_at=provider_at, clock_uncertainty_ns=scenario.uncertainty_ns, assumption_id=scenario.id)
    if type(fields["flags"]) is not int or not 0 <= fields["flags"] <= 255:
        raise ContractError("flags are a preserved uint8 bitset")
    flags = Flags(fields["flags"])
    action = _character(fields["action"], {"T", "A", "M", "C", "R", "N"})
    side = _character(fields["side"], {"A", "B", "N"})
    if type(fields["instrument_id"]) is not int or fields["instrument_id"] <= 0:
        raise ContractError("unresolved instrument ID cannot be silently reassigned")
    suffix = "_00" if native else ""
    quote = Quote(*(_price(fields[x + suffix], native=native) for x in ("bid_px", "ask_px")),
                  *(_size(fields[x + suffix]) for x in ("bid_sz", "ask_sz")),
                  _size(fields.get("bid_ct_00")), _size(fields.get("ask_ct_00")))
    price, size = _price(fields["price"], native=native), _size(fields["size"])
    issues = []
    if action is None:
        issues.append("unknown_action")
    if side is None:
        issues.append("unknown_side_enum")
    if price is None:
        issues.append("missing_event_price")
    if size is None:
        issues.append("missing_event_size")
    if not quote.valid:
        issues.append("invalid_or_incomplete_quote")
    for bit, name in ((Flags.MAYBE_BAD_BOOK, "maybe_bad_book"), (Flags.BAD_TS_RECV, "unreliable_provider_receive_time"),
                      (Flags.SNAPSHOT, "snapshot_initialization"), (Flags.PUBLISHER_SPECIFIC, "publisher_bit_requires_source_supplement")):
        if flags & bit:
            issues.append(name)
    return CanonicalEvent(address, raw, raw_record, fields["instrument_id"], c, action, side, flags, price, size, quote,
                          "pre_trade" if action == "T" else "book_update" if action in {"A", "M", "C"} else "metadata_or_clear",
                          fields.get("sequence") if native else None, fields.get("publisher_id") if native else None,
                          fields.get("depth") if native else None, tuple(issues))
