from datetime import date

import pytest

from trading_research.research.method_pack.empirical_market import clock
from trading_research.research.method_pack.session_policy import NQSessionPolicy, same_contract_prior
from trading_research.research.method_pack.derived_admission import merge_bars
from trading_research.research.method_pack.native_resolution import NativeEvidenceError


def test_historical_halt_change_and_dst_are_versioned():
    p = NQSessionPolicy()
    before, after = date(2021, 6, 25), date(2021, 6, 28)
    assert p.state(clock(before, '16:15'), clock(before, '16:30')) == 'scheduled_closure'
    assert p.state(clock(after, '16:15'), clock(after, '16:30')) == 'scheduled_open'
    assert p.state(clock(after, '17:00'), clock(after, '18:00')) == 'scheduled_closure'
    winter, summer = date(2024, 1, 8), date(2024, 7, 8)
    assert (clock(winter, '09:30') // 1_000_000_000) % 86400 == 14 * 3600 + 30 * 60
    assert (clock(summer, '09:30') // 1_000_000_000) % 86400 == 13 * 3600 + 30 * 60


def test_verified_equity_early_close_and_unknown_cash_holiday_are_distinct():
    p = NQSessionPolicy()
    early = p.rth('2023-11-24')
    assert early['known'] is True
    assert (early['windows'][0][1] - early['windows'][0][0]) // 60_000_000_000 == 225
    assert p.rth('2023-01-02')['known'] is False
    assert p.state(clock(date(2023, 1, 2), '09:30'), clock(date(2023, 1, 2), '10:00')) == 'unverified_holiday'


def test_prior_session_skips_only_known_closure_and_never_stitches_roll():
    p = NQSessionPolicy()
    assert p.previous_session('2024-01-02')['date'] == '2023-12-29'
    unknown = p.previous_session('2023-01-03')
    assert unknown['date'] == '2023-01-02' and unknown['known'] is False
    result = same_contract_prior(p, '2024-01-02', 17, [{'session_date': '2023-12-29', 'instrument_id': 18}])
    assert result['window'] is None and result['reason'] == 'same_contract_prior_session_missing'


def bar(instrument=17, volume=3, basis='vendor_receive_time'):
    return dict(instrument_id=instrument, start_ns=0, end_ns=60_000_000_000,
                O=100, H=102, L=99, C=101, V=volume, clock_basis=basis)


def test_recovery_equal_overlaps_deduplicated_but_instruments_not_coalesced():
    rows, receipt = merge_bars([bar()], [('recovered', [bar(), bar(instrument=18)])], clock_basis='vendor_receive_time')
    assert len(rows) == 2 and len(receipt) == 1
    assert sum(r['V'] for r in rows) == 6


def test_recovery_conflicts_and_mixed_clocks_are_rejected():
    with pytest.raises(NativeEvidenceError, match='contradictory'):
        merge_bars([bar()], [('recovered', [bar(volume=4)])], clock_basis='vendor_receive_time')
    with pytest.raises(NativeEvidenceError, match='mixed bar clocks'):
        merge_bars([bar()], [('event', [bar(basis='event_ns')])], clock_basis='vendor_receive_time')
