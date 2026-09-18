"""Green Bird's drawn lines on the native tape, against what his charts print.

Every expected value is a label he printed on a chart (context pass
2026-09-18, sections C and D); MNQ labels sit within a point or two of NQ.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
from trading_research.research.rule_discovery.source_adapters.common import load_source_market
from trading_research.research.rule_discovery.source_adapters.session_levels import prior_sessions

LABEL_TOLERANCE = Decimal("3")  # a chart label read to the point, MNQ against NQ


def _refs(market):
    refs, omissions = gb.session_references(market)
    return {ref["kind"]: ref for ref in refs}, omissions


@pytest.mark.parametrize(
    "day, printed_pdh, source",
    [
        ("2026-08-27", Decimal("29437"), "p38_x62 / p56_x119: 'PDH' label about 29,437; both ladders end 29,425.50 under it"),
        ("2026-04-23", Decimal("27137"), "p45_x79: the PDH line starts at 18:00 at about 27,137"),
    ],
)
def test_c1_prior_day_high_is_the_globex_day_to_1700(day, printed_pdh, source):
    market = load_source_market(day)
    refs, omissions = _refs(market)
    prior = refs["prior_day"]
    assert prior["scope"] == "globex_day_1800_1700", omissions
    assert abs(prior["high"] - printed_pdh) <= LABEL_TOLERANCE, (prior["high"], source)
    # negative control: the 18:00-16:00 session high (Jumbo's span, unchanged)
    # is NOT his line on either day -- the closing hour made the high
    session_high = prior_sessions(market, 1)[0]["high"]
    assert abs(session_high - printed_pdh) > Decimal("40"), session_high
    assert not [row for row in omissions if row.get("reason") == "globex_closing_hour_unavailable"]


def test_c1_a_missing_closing_hour_is_recorded_not_hidden(monkeypatch):
    from trading_research.research.rule_discovery.source_adapters import session_levels

    market = load_source_market("2026-08-27")
    monkeypatch.setattr(session_levels, "minute_span", lambda *a, **k: None)
    span, omissions = session_levels.globex_prior_day(market)
    assert span["scope"] == "cme_session_1800_1600" and span["high"] == Decimal("29368.25")
    assert [row["reason"] for row in omissions] == ["globex_closing_hour_unavailable"]
