"""O030: source-bound immutable trade-weighted VWAP snapshots."""

from copy import deepcopy
from decimal import Decimal

from ..logic import dec
from ..protocol import RecipeResult, add_fixture, register


@register("O030", ("trades", "as_of"))
def o030(inp):
    as_of = inp["as_of"]
    reset = inp.get("reset_at")
    missing = [key for key in ("reset_id", "reset_at", "basis", "instrument_id", "canonical_tape_id") if inp.get(key) is None]
    if inp.get("reset_verified") is not True:
        missing.append("reset")
    if inp.get("basis") not in (None, "trade_price"):
        missing.append("source_price_basis")
    holes = [f"HOLE:O030:{key}" for key in missing]
    total = Decimal(0)
    weighted = Decimal(0)
    seen = set()
    member_ids = []
    invalid = []
    if reset is not None and reset > as_of:
        invalid.append("reset_after_snapshot")
    for index, trade in enumerate(inp["trades"]):
        at = trade.get("event_ns", trade.get("t"))
        if at is None:
            holes.append("HOLE:O030:event_time")
            continue
        if at > as_of or reset is not None and at < reset:
            continue
        if trade.get("is_quote") or trade.get("action", "T") != "T":
            continue
        known = trade.get("known_at", at)
        if known is None or known > as_of:
            holes.append("HOLE:O030:availability")
            continue
        if trade.get("instrument_id", inp.get("instrument_id")) != inp.get("instrument_id"):
            invalid.append("cross_contract_sum")
            continue
        if trade.get("dataset_id", inp.get("canonical_tape_id")) != inp.get("canonical_tape_id"):
            invalid.append("mixed_tape_ownership")
            continue
        eid = trade.get("event_id")
        if eid is not None and eid in seen:
            invalid.append("duplicate_event_id")
            continue
        if eid is not None:
            seen.add(eid)
        price, size = dec(trade.get("price")), dec(trade.get("size"))
        if price is None or size is None:
            holes.append("HOLE:O030:executed_price_size")
            continue
        if size < 0:
            invalid.append("negative_executed_size")
            continue
        total += size
        weighted += price * size
        member_ids.append(eid if eid is not None else index)
    if inp.get("gap") or inp.get("coverage_complete") is False:
        holes.append("HOLE:O030:coverage")
    touch = inp.get("touch_at")
    if touch is not None and (as_of > touch or as_of == touch and inp.get("source_includes_contact_trade") is not True):
        invalid.append("snapshot_not_before_contact")
    literal = None if total == 0 else weighted / total
    if total == 0:
        holes.append("HOLE:O030:zero_volume")
    faithful = None if holes else not invalid
    value = {"sum_v": total, "sum_pv": weighted, "vwap": literal if faithful else None,
             "comparison_vwap": literal, "reset_id": inp.get("reset_id"), "reset_at": reset,
             "basis": inp.get("basis"), "as_of": as_of, "known_at": as_of,
             "member_event_ids": member_ids, "faithful": faithful,
             "vwap_at_retest": literal if faithful else None, "vwap_known_at": as_of if faithful else None,
             "vwap_reset_verified": True if not missing else None,
             "source_vwap_known": faithful, "automatic_reset": None}
    return RecipeResult("O030", "invalid" if invalid else "hole" if holes else "computed", value,
                        known_at=as_of, base_ok=False if invalid else True,
                        coverage_ok=None if holes else True,
                        hole_ids=list(dict.fromkeys(holes + [f"HOLE:O030:{key}" for key in invalid])),
                        reason=", ".join(invalid) or None)


_BASE = {"reset_verified": True, "reset_id": "source-reset", "reset_at": 0,
         "basis": "trade_price", "instrument_id": "fixture-contract", "canonical_tape_id": "owned-trades",
         "trades": [{"price": 100, "size": 2, "t": 1, "event_id": "a"},
                    {"price": 104, "size": 1, "t": 2, "event_id": "b"},
                    {"price": 110, "size": 3, "t": 4, "event_id": "c"}],
         "as_of": 2, "known_at": 2, "use_at": 3, "touch_at": 3}
add_fixture({"id": "O030-F1", "recipe": "O030", "inputs": deepcopy(_BASE),
             "expected": {"sum_v": Decimal(3), "sum_pv": Decimal(304), "vwap": Decimal(304)/3, "faithful": True}})
_later = {**deepcopy(_BASE), "as_of": 4, "known_at": 4, "use_at": 5, "touch_at": 5}
add_fixture({"id": "O030-F1b", "recipe": "O030", "inputs": _later,
             "expected": {"sum_v": Decimal(6), "sum_pv": Decimal(634), "vwap": Decimal(634)/6}})
add_fixture({"id": "O030-F1c", "recipe": "O030", "inputs": {**deepcopy(_BASE), "reset_verified": False},
             "expected": {"faithful": None, "vwap": None, "comparison_vwap": Decimal(304)/3}})
_quotes = deepcopy(_BASE)
_quotes["trades"].extend([{"t": 1, "price": 999, "size": 100, "action": "A"},
                          {"t": 1, "price": 102, "size": 1, "side": "N", "event_id": "unknown-side"}])
add_fixture({"id": "O030-F1-quote-unknown-side", "recipe": "O030", "inputs": _quotes,
             "expected": {"sum_v": Decimal(4), "sum_pv": Decimal(406), "vwap": Decimal("101.5")}})
_foreign = deepcopy(_BASE)
_foreign["trades"][0]["instrument_id"] = "other-contract"
add_fixture({"id": "O030-F1-cross-contract", "recipe": "O030", "inputs": _foreign,
             "expected": {"base_ok": False, "faithful": False}})
add_fixture({"id": "O030-F1-contact-tie", "recipe": "O030", "inputs": {**deepcopy(_BASE), "touch_at": 2},
             "expected": {"base_ok": False}})
