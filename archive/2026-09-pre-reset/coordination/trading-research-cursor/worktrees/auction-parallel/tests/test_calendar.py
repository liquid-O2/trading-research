from dataclasses import replace
from datetime import date, time
import unittest

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.calendar import Calendar, Session, local_timestamp, wall_window
from trading_research.foundations.time import NS


class CalendarTests(unittest.TestCase):
    def test_nonexistent_and_repeated_new_york_wall_times_require_resolution(self):
        with self.assertRaises(ContractError):
            local_timestamp(date(2026, 3, 8), time(2, 30), "America/New_York")
        with self.assertRaises(ContractError):
            local_timestamp(date(2026, 11, 1), time(1, 30), "America/New_York")
        first = local_timestamp(date(2026, 11, 1), time(1, 30), "America/New_York", fold=0)
        second = local_timestamp(date(2026, 11, 1), time(1, 30), "America/New_York", fold=1)
        self.assertEqual(second - first, 3600 * NS)

    def test_ny_wall_and_fixed_est_are_separate_summer_variants(self):
        day = date(2026, 7, 1)
        ny = local_timestamp(day, time(9, 30), "America/New_York")
        fixed = local_timestamp(day, time(9, 30), "Etc/GMT+5")
        self.assertEqual(fixed - ny, 3600 * NS)
        self.assertEqual(ny - local_timestamp(day, time(9), "America/New_York"), 1800 * NS)

    def test_midnight_window_belongs_to_declared_trading_date_and_excludes_endpoint(self):
        window = wall_window(id="overnight", trading_date=date(2026, 9, 7), start_day=date(2026, 9, 6),
                             start=time(20), end=time(0), zone="America/New_York", definition_version="synthetic-source-v1",
                             crosses_midnight=True)
        self.assertEqual(window.end - window.start, 4 * 3600 * NS)
        self.assertEqual(window.trading_date, date(2026, 9, 7))
        self.assertTrue(window.contains(window.start))
        self.assertFalse(window.contains(window.end))
        with self.assertRaises(ContractError):
            wall_window(id="bad", trading_date=date(2026, 9, 7), start_day=date(2026, 9, 6),
                        start=time(20), end=time(0), zone="America/New_York", definition_version="v")

    def test_earliest_firm_boundary_and_later_holiday_revision_are_known_time(self):
        # Deliberately synthetic timestamps: this is not a certified exchange date.
        session = Session("s", date(2026, 9, 8), "NQ", 10, 100, (("firm", 90), ("platform", 80)), 5,
                          1, "calendar-v1", "zone-test-version", True, "synthetic eligible day")
        calendar = Calendar()
        calendar.append(session)
        calendar.append(replace(session, close_at=70, required_boundaries=(("platform", 65),), known_at=30, source_version="early-close-v2"))
        self.assertEqual(calendar.resolve(session.trading_date, "NQ", cut=20).flatten_at, 75)
        self.assertEqual(calendar.resolve(session.trading_date, "NQ", cut=40).flatten_at, 60)
        self.assertIn((75, "flatten_deadline"), calendar.timers(session.trading_date, "NQ", cut=20))
        with self.assertRaises(DependencyUnavailable):
            calendar.resolve(date(2026, 9, 9), "NQ", cut=40)
