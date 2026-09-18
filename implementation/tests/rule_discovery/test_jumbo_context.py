"""Jumbo's news-week table (TBR p.22) and the sister-index read (TBR p.12).
The expected tiers are the dots of his table, read for the weekdays it is
drawn for: CPI on a Wednesday, NFP on a Friday, FOMC on a Wednesday."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from trading_research.research.rule_discovery.source_adapters import jumbo_context as jc

MONDAY = date(2026, 3, 9)
TABLE = {
    "cpi": (2, ["moderate", "low", "risk_on", "risk_on", "risk_on"]),
    "nfp": (4, ["moderate", "risk_on", "risk_on", "low", "moderate"]),
    "fomc": (2, ["risk_on", "risk_on", "low", "risk_on", "risk_on"]),
}


@pytest.mark.parametrize("kind", sorted(TABLE))
def test_each_weekday_of_a_news_week_gets_the_dot_of_his_table(kind):
    release_weekday, dots = TABLE[kind]
    release = MONDAY + timedelta(days=release_weekday)
    assert [jc._tier(kind, MONDAY + timedelta(days=n), release) for n in range(5)] == dots


def test_two_releases_in_a_week_take_the_more_cautious_tier_and_a_quiet_week_has_none(monkeypatch):
    wednesday, friday = MONDAY + timedelta(days=2), MONDAY + timedelta(days=4)
    monkeypatch.setattr(jc, "_releases", lambda root: {wednesday: ("cpi",), friday: ("nfp",)})
    thursday = jc.news_week(MONDAY + timedelta(days=3), "anywhere")
    assert thursday["tier"] == "low", "risk-on after CPI, low before NFP: the cautious one stands"
    assert jc.news_week(wednesday, "anywhere")["release_today"] == ["cpi"]
    assert jc.news_week(MONDAY + timedelta(days=7), "anywhere")["tier"] is None
    monkeypatch.setattr(jc, "_releases", lambda root: {})
    assert jc.news_week(wednesday, "anywhere") == {"available": False, "tier": None, "events": []}


def test_sister_index_reads_who_took_the_prior_extremes(monkeypatch):
    spans = {(0, 10): {"open": 100.0, "high": 110.0, "low": 95.0, "close": 105.0}, (10, 20): {"open": 105.0, "high": 109.0, "low": 94.0, "close": 106.05}}
    monkeypatch.setattr(jc, "_es_span", lambda root, start, end: spans[(start, end)])
    read = jc.sister_index(data_root="anywhere", prior_window=(0, 10), overnight=(10, 20), nq_prior={"high": 1000, "low": 950}, nq_overnight={"open": 990.0, "high": 1004.0, "low": 960.0, "close": 999.9})
    assert (read["nq_purged_prior_high"], read["es_purged_prior_high"], read["divergence_at_high"]) == (True, False, True)
    assert (read["nq_purged_prior_low"], read["es_purged_prior_low"], read["divergence_at_low"]) == (False, True, True)
    assert read["nq_overnight_pct"] == 1.0 and read["es_overnight_pct"] == 1.0 and read["nq_minus_es_overnight_pct"] == 0.0
    assert jc.sister_index(data_root=None, prior_window=(0, 10), overnight=(10, 20), nq_prior={}, nq_overnight={}) == {"available": False}


def test_minimum_average_sits_under_both_side_averages_as_his_tables_print_it():
    """JR p.69 prints Min Avg 40.74 under Exp 74.53 and Dist 65.55: the mean of each
    session's smaller excursion, never the smaller of the two side means. Two sessions
    worked by hand: excursions up 100 and 20, down 10 and 80; side means 60 and 45."""
    from decimal import Decimal

    from trading_research.research.rule_discovery.source_adapters import jumbo as jj

    assert jj.minimum_average([Decimal(100), Decimal(20)], [Decimal(10), Decimal(80)]) == Decimal(15)
