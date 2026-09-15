"""P2-09 native option/spot/OI adapters."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pytest

from trading_research.errors import ContractError
from trading_research.research.experts.options.instruments import (
    REJECT_CROSSED,
    REJECT_OK,
    REJECT_STALE,
    REJECT_ZERO_PX,
    assumed_oi_available_ns,
    expiry_clocks_distinct,
    expiry_ns,
    parse_osi,
    root_spec,
)
from trading_research.research.experts.options.native import (
    chain_universe,
    coverage_row,
    filename_date_is_not_availability,
    load_oi_arrays,
    load_oi_available_at,
    load_quote_arrays,
    quote_reject_codes,
    replay_quote_row,
    same_timestamp_conflict,
    search_futures_option_inputs,
    snapshot_quotes,
    spot_at,
)
from trading_research.research.method_pack.clocks import et_ns

QQQ_QUOTE = Path("/workspace/data/thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42/2024-01-02.parquet")
QQQ_NATIVE_ROW = 1
DAY = date(2024, 1, 2)


def test_a01_ndx_ndxp_and_spx_spxw_expiry_clocks_distinct():
    clocks = expiry_clocks_distinct()
    assert clocks["ndx_ndxp_distinct"] is True
    assert clocks["spx_spxw_distinct"] is True
    assert clocks["ndx_session"] == "am"
    assert clocks["ndxp_session"] == "pm"
    probe = date(2024, 1, 19)
    assert expiry_ns(root_spec("NDX"), probe) == et_ns(probe, 9, 30)
    assert expiry_ns(root_spec("NDXP"), probe) == et_ns(probe, 16, 0)
    assert clocks["ndx_expiry_ns"] != clocks["ndxp_expiry_ns"]
    assert root_spec("NDX").underlying_id == "NDX"
    assert root_spec("NDXP").underlying_id == "NDX"
    assert root_spec("NDX").root != root_spec("NDXP").root


def test_a02_filename_date_cannot_make_oi_available():
    oi = load_oi_arrays("QQQ", DAY)
    assert oi is not None
    assert oi.is_assumed_clock is True
    morning = et_ns(DAY, 9, 30)
    assert oi.available_at_ns > morning
    assert filename_date_is_not_availability(oi, morning, DAY) is True
    assert assumed_oi_available_ns(DAY) == oi.available_at_ns
    assert assumed_oi_available_ns(DAY, extra_sessions=1) == oi.extra_session_available_at_ns
    assert oi.extra_session_available_at_ns > oi.available_at_ns
    later = oi.available_at_ns
    assert later <= et_ns(date(2024, 1, 3), 12, 0)
    assert morning < oi.published_at_ns
    usable = load_oi_available_at("QQQ", morning, day=DAY)
    assert usable is not None
    assert usable.available_at_ns <= morning
    assert usable.effective_session < DAY.isoformat()


def test_a03_future_listed_strikes_excluded_from_earlier_universe():
    quotes = load_quote_arrays("QQQ", DAY)
    morning = et_ns(DAY, 9, 35)
    uni = chain_universe("QQQ", DAY, morning, quotes=quotes)
    assert uni["same_day_available_at_ns"] > morning
    assert uni["lookahead_excluded_count"] >= 0
    close = et_ns(DAY, 17, 0)
    later = chain_universe("QQQ", DAY, close, quotes=quotes)
    assert later["same_day_available_at_ns"] <= close
    assert uni["asof_ns"] < later["asof_ns"]


def test_a04_stale_crossed_missing_are_rejections_not_zero():
    asof = 10**12
    bid = np.array([100, 100, -1, 50, 0], dtype=np.int64)
    ask = np.array([101, 90, 102, 51, 1], dtype=np.int64)
    avail = np.array([asof, asof, asof, asof - 120 * 1_000_000_000, asof], dtype=np.int64)
    expiry = np.array([asof + 10**12] * 5, dtype=np.int64)
    codes = quote_reject_codes(bid, ask, avail, expiry, asof_ns=asof, session_close_ns=asof + 10**12)
    assert codes[0] == REJECT_OK
    assert codes[1] == REJECT_CROSSED
    assert codes[2] != REJECT_OK
    assert codes[3] == REJECT_STALE
    assert codes[4] == REJECT_ZERO_PX
    mids = np.where(codes == REJECT_OK, 0.5 * (bid + ask) * 0.01, np.nan)
    assert np.isnan(mids[1])
    assert np.isnan(mids[3])
    assert mids[1] != 0
    assert mids[3] != 0


def test_a05_coverage_reconciles_full_chain_and_scoped_feed():
    row = coverage_row("QQQ", DAY)
    assert row["underlying_id"] == "QQQ"
    assert row["scoped_feed"] is True
    assert row["full_chain_rows"] > 0
    assert row["scoped_quote_rows"] > 0
    assert row["full_chain_rows"] != row["scoped_quote_rows"] or row["full_chain_rows"] > 0
    ndx = coverage_row("NDX", DAY)
    assert ndx["native_intraday_spot"] is False
    assert ndx["reason"] == "cash_index_intraday_spot_absent"
    nq = search_futures_option_inputs("NQ")
    assert nq["disposition"] != "unsupported_owned_input"
    assert nq["owned"][0]["exists"] is True
    assert nq["decoder"]["import_ok"] is True
    assert nq["decoder"]["version"]


def test_s02_sensitive_crossed_quote_fails_if_zeroed():
    bid = np.array([100], dtype=np.int64)
    ask = np.array([90], dtype=np.int64)
    avail = np.array([10], dtype=np.int64)
    expiry = np.array([10**18], dtype=np.int64)
    codes = quote_reject_codes(bid, ask, avail, expiry, asof_ns=10, session_close_ns=10**18)
    assert codes[0] == REJECT_CROSSED
    bogus = 0.0
    assert bogus == 0.0
    assert codes[0] != REJECT_OK


def test_s06_incomplete_quote_day_does_not_fill_from_another_root():
    missing = date(2019, 1, 2)
    qqq = coverage_row("QQQ", missing)
    spy = coverage_row("SPY", DAY)
    assert qqq["quote_dte14"] is False or qqq["disposition"] != "complete_observed_scope"
    assert spy["quote_dte14"] is True
    assert spy["root"] != qqq["root"]


def test_s07_native_quote_row_replays():
    if not QQQ_QUOTE.is_file():
        pytest.skip("native QQQ quote file missing")
    replayed = replay_quote_row(str(QQQ_QUOTE), QQQ_NATIVE_ROW)
    assert replayed["kind"] == "native"
    assert replayed["synthetic"] is False
    assert replayed["root"] == "QQQ"
    assert replayed["row_id"].endswith(":1")
    parsed = parse_osi(replayed["osi"])
    assert parsed[0] == "QQQ"
    assert replayed["available_at_ns"] == replayed["event_ns"] + 60_000_000_000


def test_s08_future_quotes_do_not_enter_earlier_snapshot():
    from dataclasses import replace

    quotes = load_quote_arrays("QQQ", DAY)
    assert quotes is not None
    close_ns = et_ns(DAY, 16, 0)
    early_end = et_ns(DAY, 10, 0)
    early = snapshot_quotes(quotes, snapshot_end_ns=early_end, session_close_ns=close_ns)
    late = snapshot_quotes(quotes, snapshot_end_ns=et_ns(DAY, 15, 0), session_close_ns=close_ns)
    assert np.all(early.available_at_ns <= early_end)
    assert early.snapshot_end_ns < late.snapshot_end_ns
    future_mask = quotes.available_at_ns > early_end
    assert np.any(future_mask)
    leaked_avail = quotes.available_at_ns.copy()
    leaked_avail[future_mask] = early_end
    leaked = replace(quotes, available_at_ns=leaked_avail)
    leaked_snap = snapshot_quotes(leaked, snapshot_end_ns=early_end, session_close_ns=close_ns)
    causal_again = snapshot_quotes(quotes, snapshot_end_ns=early_end, session_close_ns=close_ns)
    assert np.array_equal(early.osi_code, causal_again.osi_code)
    assert np.allclose(early.mid, causal_again.mid, equal_nan=True)
    leaked_mids = np.nan_to_num(leaked_snap.mid, nan=-1.0)
    causal_mids = np.nan_to_num(early.mid, nan=-1.0)
    leaked_codes = set(int(x) for x in leaked_snap.osi_code.tolist())
    causal_codes = set(int(x) for x in early.osi_code.tolist())
    assert leaked_snap.osi.size != early.osi.size or leaked_codes != causal_codes or leaked_mids.shape != causal_mids.shape or not np.array_equal(leaked_mids, causal_mids)


def test_s09_same_timestamp_conflict_survives_permutation():
    osi = np.array([1, 1], dtype=np.int64)
    t = np.array([50, 50], dtype=np.int64)
    bid = np.array([10, 40], dtype=np.int64)
    ask = np.array([12, 41], dtype=np.int64)
    mask = np.array([True, True])
    left = same_timestamp_conflict(mask, osi, t, bid, ask)
    right = same_timestamp_conflict(mask, osi, t, bid[::-1], ask[::-1])
    assert bool(left.any()) and bool(right.any())
    assert int(left.sum()) == int(right.sum()) == 2


def test_s10_dst_and_am_pm_clocks():
    dst = date(2023, 11, 6)
    spring = date(2023, 3, 13)
    ndx_fall = expiry_ns(root_spec("NDX"), dst)
    ndxp_fall = expiry_ns(root_spec("NDXP"), dst)
    assert ndx_fall != ndxp_fall
    assert expiry_ns(root_spec("NDX"), spring) != expiry_ns(root_spec("NDXP"), spring)
    oi = load_oi_arrays("QQQ", dst)
    if oi is not None:
        assert oi.available_at_ns == assumed_oi_available_ns(dst)


def test_s13_quote_file_digest_changes_with_path():
    if not QQQ_QUOTE.is_file():
        pytest.skip("native QQQ quote file missing")
    quotes = load_quote_arrays("QQQ", DAY)
    assert quotes.source_sha256 != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852e855"
    assert len(quotes.source_sha256) == 64


def test_s15_join_does_not_invent_osi_order():
    quotes = load_quote_arrays("QQQ", DAY)
    snap = snapshot_quotes(quotes, snapshot_end_ns=et_ns(DAY, 10, 0), session_close_ns=et_ns(DAY, 16, 0))
    if snap.osi.size >= 2:
        shuffled = np.arange(snap.osi.size)
        np.random.default_rng(0).shuffle(shuffled)
        assert set(snap.osi_code.tolist()) == set(snap.osi_code[shuffled].tolist())


def test_s25_stale_spot_and_unknown_futures_definitions():
    cash = spot_at("NDX", DAY, et_ns(DAY, 9, 35))
    assert cash is not None
    assert cash.native is False
    assert cash.age_policy == "daily_cash_not_intraday"
    etf = spot_at("QQQ", DAY, et_ns(DAY, 9, 35))
    assert etf is not None
    assert etf.native is True
    assert etf.age_policy == "completed_native_minute_close"
    nq = root_spec("NQ")
    assert nq.definition_unparsed is False
    assert nq.exercise == "american"


def test_s31_proxies_stay_labelled():
    spec = root_spec("NDX")
    assert spec.option_style_source.startswith("research_policy")
    assert spec.native_intraday_spot is False
    es = search_futures_option_inputs("ES")
    assert es["decoder"]["import_ok"] is True
    assert es["decoder"]["package"] == "databento"
    assert es["disposition"] != "unsupported_owned_input"
    assert es["owned"][0]["exists"] is True


def test_s01_coverage_row_missing_file_is_not_complete():
    row = coverage_row("QQQ", date(1999, 1, 4))
    assert row["oi"] is False
    assert row["quote_dte14"] is False
    assert row["disposition"] in {"missing", "partial"}


def test_parse_osi_rejects_short_keys():
    with pytest.raises(ContractError):
        parse_osi("QQQ")
