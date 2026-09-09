"""Shared synthetic source builders; fixture assembly performs no candidate fit."""

import json
from pathlib import Path

from trading_research.foundations.bars import WindowCoverage
from trading_research.measurements.common import capture_trade_window
from trading_research.measurements.tape import Trade, TradeLedger


UNIT = "provider-reported-trade-record"
GOLD = json.loads((Path(__file__).parent / "golden/m01_m02_m10_engineering_v1.json").read_text())
CASES = {c["case_id"]: c for c in GOLD["cases"]}


def row(id, *, at=1, known=None, price=100, size=1, side=1, order=None, instrument="NQ.test", **kw):
    result = dict(id=id, source_content_version=id + ".v1", instrument=instrument, event_at=at,
        known_at=at if known is None else known, price=price, size=size, side=side,
        order=order, aggregation_unit=UNIT, history_complete=True)
    result.update(kw)
    return result


def ledger(rows, *, max_events=4096):
    result = TradeLedger(max_events=max_events)
    for r in sorted(rows, key=lambda r: r["known_at"]):
        result.add(Trade.restore(r))
    return result


def request(*, start=0, end=100, cut=None, published=None, instrument="NQ.test", spans=None,
            coverage_known=None, definition="m-test-v1", coverage_version="coverage.v1", max_inputs=4096, max_bytes=8388608):
    cut = end if cut is None else cut
    if spans is None:
        spans = ((start, min(end,cut)),) if start < min(end,cut) else ()
    return dict(instrument=instrument, start=start, end=end, cut=cut, published_at=cut + 1 if published is None else published,
        definition_version=definition, aggregation_unit=UNIT, max_inputs=max_inputs, max_bytes=max_bytes,
        coverage=WindowCoverage(instrument, start, end, tuple(spans),
                                cut if coverage_known is None else coverage_known, coverage_version))


def capture(rows, **kw):
    view = ledger(rows)
    return view, capture_trade_window(view, **request(**kw))


def gold_capture(case_id, *, rows_key="trades"):
    inputs = CASES[case_id]["inputs"]
    view = ledger(inputs[rows_key])
    req = inputs.get("window")
    if req is None:
        return view, capture_trade_window(view, **request())
    req = dict(req)
    req["coverage"] = WindowCoverage(**{**req["coverage"], "observed_intervals": tuple(map(tuple, req["coverage"]["observed_intervals"]))})
    return view, capture_trade_window(view, **req)
