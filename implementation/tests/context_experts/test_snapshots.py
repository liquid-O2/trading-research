"""The quarter-hour issue-time grid. Expected instants are written as UTC wall
clocks from the calendar (New York is UTC-5 in winter, UTC-4 in summer), not
derived from the module's own clock helper."""

from datetime import date, datetime, timezone

import pytest

from trading_research.research.experts import snapshots as sn

NS = 1_000_000_000


def utc(y, m, d, hh, mm=0, ss=0) -> int:
    return int(datetime(y, m, d, hh, mm, ss, tzinfo=timezone.utc).timestamp()) * NS


def test_normal_day_has_92_account_quarters_and_26_rth_quarters():
    day = date(2024, 3, 5)  # winter: 18:00 New York on 03-04 is 23:00 UTC
    grid = sn.account_day_grid(day)
    assert grid.size == 92
    assert int(grid[0]) == utc(2024, 3, 4, 23, 0)
    assert int(grid[-1]) == utc(2024, 3, 5, 21, 45)  # 16:45 New York; 17:00 is the close, excluded
    rth = sn.rth_grid(day)
    assert rth.size == 26
    assert int(rth[0]) == utc(2024, 3, 5, 14, 30)  # 09:30
    assert int(rth[-1]) == utc(2024, 3, 5, 20, 45)  # 15:45


@pytest.mark.parametrize(
    "day, start_utc, rth_open_utc",
    [
        (date(2024, 3, 8), (2024, 3, 7, 23, 0), (2024, 3, 8, 14, 30)),  # Friday before spring forward, UTC-5
        (date(2024, 3, 11), (2024, 3, 10, 22, 0), (2024, 3, 11, 13, 30)),  # Monday after: Sunday 18:00 is already UTC-4
        (date(2024, 11, 1), (2024, 10, 31, 22, 0), (2024, 11, 1, 13, 30)),  # Friday before fall back, UTC-4
        (date(2024, 11, 4), (2024, 11, 3, 23, 0), (2024, 11, 4, 14, 30)),  # Monday after, UTC-5
    ],
)
def test_dst_transition_weeks_keep_wall_clock_quarters(day, start_utc, rth_open_utc):
    grid = sn.account_day_grid(day)
    assert grid.size == 92
    assert int(grid[0]) == utc(*start_utc)
    assert int(sn.rth_grid(day)[0]) == utc(*rth_open_utc)
    minutes = {datetime.fromtimestamp(int(t) / NS, tz=timezone.utc).astimezone(sn.NEW_YORK).minute for t in grid}
    assert minutes == {0, 15, 30, 45}


def test_early_close_ends_the_grid_at_the_close():
    day = date(2023, 11, 24)  # the policy's verified 13:15 close
    grid = sn.account_day_grid(day)
    assert grid.size == 77  # 18:00 to 13:15 is 19.25 hours
    assert int(grid[-1]) == utc(2023, 11, 24, 18, 0)  # 13:00 New York
    rth = sn.rth_grid(day)
    assert rth.size == 15  # 09:30 .. 13:00
    assert int(rth[-1]) == utc(2023, 11, 24, 18, 0)
    assert sn.grid_time_for(utc(2023, 11, 24, 19, 0), day=day) is None  # 14:00 New York, after the close


def test_weekend_has_no_rth_grid():
    assert sn.rth_grid(date(2024, 3, 10)).size == 0


def test_join_boundaries():
    quarter = utc(2024, 3, 5, 14, 45)  # 09:45 New York
    assert sn.grid_time_for(quarter) == quarter
    assert sn.grid_time_for(quarter + 1) == quarter
    assert sn.grid_time_for(quarter - 1) == utc(2024, 3, 5, 14, 30)
    assert sn.grid_time_for(quarter + 14 * 60 * NS + 59 * NS) == quarter
    # the 17:00-18:00 closure belongs to no account day's grid
    assert sn.grid_time_for(utc(2024, 3, 5, 22, 30)) is None
    # 18:00 opens the NEXT account day
    reopen = utc(2024, 3, 5, 23, 0)
    assert sn.account_day_of(reopen) == date(2024, 3, 6)
    assert sn.account_day_of(reopen - 1) == date(2024, 3, 5)
    assert sn.grid_time_for(reopen) == reopen
    # a caller's explicit day is honoured: the instant is outside that day's window
    assert sn.grid_time_for(reopen, day=date(2024, 3, 5)) is None


def test_buckets_and_holdout():
    assert sn.session_bucket(utc(2024, 3, 4, 23, 0)) == "reopen"  # 18:00
    assert sn.session_bucket(utc(2024, 3, 5, 5, 0)) == "asia"  # 00:00
    assert sn.session_bucket(utc(2024, 3, 5, 8, 0)) == "europe"  # 03:00
    assert sn.session_bucket(utc(2024, 3, 5, 14, 29, 59)) == "europe"
    assert sn.session_bucket(utc(2024, 3, 5, 14, 30)) == "us_morning"
    assert sn.session_bucket(utc(2024, 3, 5, 17, 0)) == "us_afternoon"  # 12:00
    assert sn.session_bucket(utc(2024, 3, 5, 21, 0)) == "late"  # 16:00
    assert sn.session_bucket(utc(2024, 3, 5, 22, 0)) == "closed"  # 17:00
    assert sn.is_holdout(date(2026, 4, 1)) and not sn.is_holdout(date(2026, 3, 31))
