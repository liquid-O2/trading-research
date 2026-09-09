from datetime import date,time
from pathlib import Path
import unittest

from trading_research.errors import DependencyUnavailable
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar,VenueBoundary,e0_window
from trading_research.foundations.time import MINUTE


class PublishedCalendarTests(unittest.TestCase):
    def setUp(self):self.calendar=CashCalendar(Path(__file__).resolve().parents[1]/'configs/cash-rth-calendar.json')
    def at(self,day,wall=time(0)):return local_timestamp(day,wall,'America/New_York')

    def test_dated_mourning_override_cannot_change_earlier_calendar_queries(self):
        day=date(2025,1,9)
        old=self.calendar.resolve(day,cut=self.at(date(2024,12,29)))
        new=self.calendar.resolve(day,cut=self.at(date(2024,12,31)))
        self.assertEqual((old.state,new.state),('regular','closed'))
        self.assertNotEqual(old.version,new.version);self.assertIsNone(new.open_at)
        with self.assertRaises(DependencyUnavailable):self.calendar.resolve(date(2025,2,3),cut=self.at(date(2022,12,20)))

    def test_holidays_short_sessions_and_dst_use_published_cash_dates(self):
        day=date(2024,11,29);row=self.calendar.resolve(day,cut=self.at(day))
        self.assertEqual(row.state,'early_close');self.assertEqual(row.close_at-row.open_at,210*MINUTE)
        self.assertEqual(self.calendar.resolve(date(2022,6,20),cut=self.at(date(2022,6,20))).state,'closed')
        before=self.calendar.resolve(date(2024,3,8),cut=self.at(date(2024,3,8)))
        after=self.calendar.resolve(date(2024,3,11),cut=self.at(date(2024,3,11)))
        self.assertEqual(after.open_at-before.open_at,71*60*MINUTE)
        self.assertEqual(len(self.calendar.timezone_version),64)

    def test_year_counts_and_quarter_dates_include_early_days_and_exclude_announced_closure(self):
        counts={y:sum(len(self.calendar.quarter_dates(y,q)) for q in range(1,5)) for y in range(2022,2026)}
        self.assertEqual(counts,{2022:251,2023:250,2024:252,2025:250})
        self.assertNotIn(date(2025,1,9),[r.day for r in self.calendar.quarter_dates(2025,1)])
        self.assertIn(date(2025,12,24),[r.day for r in self.calendar.quarter_dates(2025,4)])

    def test_cash_calendar_does_not_silently_certify_futures_boundary(self):
        day=date(2024,11,29);row=self.calendar.resolve(day,cut=self.at(day))
        boundary=VenueBoundary(day,'NQ',row.open_at,row.close_at,row.close_at,row.known_at,'synthetic-window','synthetic_research_window')
        with self.assertRaises(DependencyUnavailable):e0_window(row,boundary=boundary,cut=self.at(day),safety_buffer_ns=5*MINUTE)
        w=e0_window(row,boundary=boundary,cut=self.at(day),safety_buffer_ns=5*MINUTE,require_verified_venue=False)
        self.assertEqual(w['flatten_send_at'],self.at(day,time(12,55)));self.assertEqual(w['required_flat_at'],self.at(day,time(13)))
