"""Versioned physical DBN fields and explicitly scoped typed values (F01).

Strings and padding are bytes. Enum interpretation and instrument valuation
belong to their source-specific consumers, not to a generic attribute getter.
"""

from decimal import Decimal
from functools import lru_cache
import importlib.metadata
from typing import TYPE_CHECKING

from trading_research.data.native_layouts import LAYOUTS, PROVIDER_VERSION
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.units import decimal_product
from trading_research.operations.artifacts import digest

if TYPE_CHECKING:
    from trading_research.data.readers import NativeRecord


@lru_cache(maxsize=32)
def registered_layout(kind: str, dbn_version: int, ts_out: bool):
    if type(dbn_version) is not int or dbn_version not in {1, 2, 3} or type(ts_out) is not bool:
        raise ContractError("native fields require an explicit registered DBN version and ts_out declaration")
    allowed = {"TradeMsg", "MBP1Msg", "OHLCVMsg",
               "StatMsg" if dbn_version == 3 else "StatMsgV1",
               {1: "InstrumentDefMsgV1", 2: "InstrumentDefMsgV2", 3: "InstrumentDefMsg"}[dbn_version]}
    if kind not in allowed:
        raise ContractError("native record class is unregistered for the declared source version")
    try:
        import databento_dbn as dbn
    except ImportError as exc:
        raise DependencyUnavailable("native field registration needs the pinned data extra") from exc
    layout = LAYOUTS[kind]
    if (importlib.metadata.version("databento-dbn") != PROVIDER_VERSION
            or tuple(tuple(field) for field in getattr(dbn, kind)._dtypes) != layout):
        raise ContractError("provider version or native physical layout changed; review and register it explicitly")
    if ts_out:
        layout += (("ts_out", "u8"),)
    layout_id = digest({"format": "dbn-physical-fields-v1", "provider_version": PROVIDER_VERSION,
                        "dbn_version": dbn_version, "kind": kind, "layout": layout})
    return layout, layout_id


def decode_record_fields(raw: bytes, *, kind: str, dbn_version: int, ts_out: bool):
    layout, layout_id = registered_layout(kind, dbn_version, ts_out)
    if (not isinstance(raw, bytes) or not raw or len(raw) != sum(int(t[1:]) for _, t in layout)
            or raw[0]*4 != len(raw)):
        raise ContractError("native record length disagrees with registered layout or physical record header")
    fields = {}
    offset = 0
    for key, dtype in layout:
        width = int(dtype[1:])
        value = raw[offset:offset+width]
        fields[key] = value if dtype[0] == "S" else int.from_bytes(value, "little", signed=dtype[0] == "i")
        offset += width
    expected_rtypes = {"TradeMsg": {0}, "MBP1Msg": {1}, "OHLCVMsg": {32, 33, 34, 35},
                       "StatMsg": {24}, "StatMsgV1": {24}, "InstrumentDefMsg": {19},
                       "InstrumentDefMsgV1": {19}, "InstrumentDefMsgV2": {19}}
    if fields["rtype"] not in expected_rtypes[kind]:
        raise ContractError("native header record type disagrees with its registered physical class")
    return fields, layout_id


def reassemble_native_fields(record: "NativeRecord") -> bytes:
    layout, layout_id = registered_layout(record.kind, record.dbn_version, "ts_out" in record.fields)
    if record.layout_id != layout_id or tuple(record.fields) != tuple(k for k, _ in layout):
        raise ContractError("native field bundle lost, reordered or changed a declared field/layout")
    output = bytearray()
    for key, dtype in layout:
        value, width = record.fields[key], int(dtype[1:])
        if dtype[0] == "S":
            if not isinstance(value, bytes) or len(value) != width:
                raise ContractError("native character array must retain every physical byte")
            output.extend(value)
        else:
            if type(value) is not int:
                raise ContractError("native integer field cannot be coerced from another physical type")
            try:
                output.extend(value.to_bytes(width, "little", signed=dtype[0] == "i"))
            except OverflowError as exc:
                raise ContractError("native integer exceeds its registered field width") from exc
    if bytes(output) != record.raw_bytes:
        raise ContractError("native field bundle no longer reconstructs its complete raw record")
    return bytes(output)


_FIXED_POINT = frozenset({"price", "bid_px_00", "ask_px_00", "open", "high", "low", "close",
                         "min_price_increment", "display_factor", "high_limit_price", "low_limit_price",
                         "max_price_variation", "trading_reference_price", "unit_of_measure_qty",
                         "min_price_increment_amount", "price_ratio", "strike_price", "leg_price", "leg_delta"})
_TIMESTAMPS = frozenset({"ts_event", "ts_recv", "ts_ref", "ts_out", "activation", "expiration"})
_ORDER_SIZES = frozenset({"size", "bid_sz_00", "ask_sz_00"})
_PLAIN_INTEGERS = frozenset({"publisher_id", "instrument_id", "rtype", "sequence", "flags", "depth",
                           "ts_in_delta", "volume", "stat_type", "update_action", "stat_flags",
                           "underlying_id", "raw_instrument_id", "leg_count", "leg_index",
                           "leg_instrument_id", "leg_underlying_id", "leg_ratio_price_numerator",
                           "leg_ratio_price_denominator", "leg_ratio_qty_numerator", "leg_ratio_qty_denominator"})


def typed_native_fields(record: "NativeRecord") -> dict:
    """Explicit physical scalars only; this is not a complete economic adapter.

    Unlisted values remain raw. In particular this function does not infer
    publication time, derivative payoff, dollar multipliers or enum meanings.
    """
    reassemble_native_fields(record)
    layout = dict(registered_layout(record.kind, record.dbn_version, "ts_out" in record.fields)[0])
    values = {}
    for key, value in record.fields.items():
        if key in _FIXED_POINT:
            values[key] = None if value == 2**63-1 else decimal_product(value, Decimal("0.000000001"))
        elif key in _TIMESTAMPS:
            values[key] = None if value == 2**64-1 else value
        elif key in _ORDER_SIZES:
            values[key] = None if value == 2**32-1 else value
        elif key == "quantity" and record.kind in {"StatMsg", "StatMsgV1"}:
            maximum = 2**(int(layout[key][1:])*8-1)-1
            values[key] = None if value == maximum else value
        elif key == "contract_multiplier" and record.kind.startswith("InstrumentDefMsg"):
            values[key] = None if value == 2**31-1 else value
        elif key in _PLAIN_INTEGERS:
            values[key] = value
    return values
