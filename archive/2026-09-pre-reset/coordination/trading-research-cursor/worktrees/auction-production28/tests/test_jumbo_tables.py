"""Independent clock, date-population and causal table examples.

These literal price/volume fixtures test extraction contracts, not market
statistics. Candidate code is exercised only by the registered shared check.
"""
from datetime import date, datetime, time, timezone
from pathlib import Path
import unittest

from trading_research.errors import ContractError
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.calendar import local_timestamp
from trading_research.research.ohlc_ranges import MinuteBars
from trading_research.research.jumbo_tables import (
    cash_dates, extract_dates, features_at, observed_prefix, path_row,
)

M = 60_000_000_000
RAW = "NQ:NQZ4:independent-fixed-raw-lifetime"


def utc(ns):
    return datetime.fromtimestamp(ns // 1_000_000_000, timezone.utc).isoformat()


def calendar():
    return CashCalendar(Path(__file__).resolve().parents[1] / "configs/cash-rth-calendar.json")


def cash(day):
    cal = calendar()
    return cal.resolve(day, cut=local_timestamp(day, time(0), cal.zone))


def series(rows):
    """Rows: (start_ns, open, high, low, close, volume[, contract[, known]])."""
    names = ("start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
             "low_ticks", "close_ticks", "volume", "contract_key", "valid")
    columns = {name: [] for name in names}
    for row in sorted(rows, key=lambda value: value[0]):
        start, o, h, l, c, volume = row[:6]
        values = (start, start + M, row[7] if len(row) > 7 else start + 2 * M,
                  o, h, l, c, volume, row[6] if len(row) > 6 else RAW, True)
        for name, value in zip(names, values, strict=True):
            columns[name].append(value)
    return MinuteBars(columns, source_version="independent-causal-date-price-fixture")


def clock(id, start="09:30", end="09:31", *, day_offset=0):
    return {"id": id, "output_definition": "wick_range_v1", "source_ids": ["literal-clock-fixture"],
            "local_zone": "America/New_York", "local": {
                "start": {"day_offset": day_offset, "time": start},
                "end": {"day_offset": 0, "time": end}, "interval": "[start,end)"}}


def recipes():
    # The extractor requires its exact population width. Distinct inert
    # fixture IDs fill that shape; the four tested anchors have literal clocks.
    return [clock("Asia20", "20:00", "02:00", day_offset=-1),
            clock("JTR_fixed_04", "06:00", "09:00"), clock("OR15", "09:30", "09:45"),
            clock("literal_RTH", "09:30", "16:00"),
            *(clock(f"literal_{i:02d}") for i in range(65))]


def plan():
    return {"neighbor_clocks": [], "neighbor_shifts_minutes": [], "horizons_minutes": [1, 3],
            "matched_clock_comparison": {"origin_local": "10:01", "clocks": []},
            "prefix_clocks": [], "prefix_delays_minutes": [2],
            "activity": {"lookback_dates": 2, "minimum_reference_dates": 1,
                         "maximum_minutes": 15, "threshold_multiples_exact": [[1, 1]]}}


def session_rows(day, *, volume, count=None):
    minutes = (day.close_at - day.open_at) // M if count is None else count
    return [(day.open_at + i * M, 100, 101, 99, 100, volume) for i in range(minutes)]


def formation(rows, name):
    return next(row for row in rows["formations"] if row["clock"] == name)


def feature_fields(row):
    return {key: value for key, value in row.items() if key.startswith("x_")}


class JumboTableTests(unittest.TestCase):
    def test_checkpoint_continuation_rebuilds_prior_session_and_activity_state(self):
        friday, monday = cash(date(2024, 11, 29)), cash(date(2024, 12, 2))
        bars = series(session_rows(friday, volume=10) + session_rows(monday, volume=100))
        settings = dict(root="NQ", recipes=recipes(), plan=plan(),
                        evaluation_cut=monday.close_at + 2 * M)
        full = list(extract_dates(bars, (friday, monday), **settings))
        resumed = list(extract_dates(bars, (friday, monday), emit_first_date=monday.day, **settings))
        self.assertEqual(resumed, full[1:])
        self.assertEqual(formation(resumed[0], "OR_activity_1_1")["activity_threshold"], 150)

    def test_path_serialization_keeps_null_schema_and_exact_large_integer_values(self):
        import pyarrow as pa
        import pyarrow.parquet as pq
        from trading_research.research.jumbo_study import _rows_table
        empty_values = _rows_table([{}], kind="paths")
        literal = {"origin_ns": 9_007_199_254_740_993,
                   "endpoint_ns": 9_007_259_254_740_993,
                   "terminal_ticks": 9_007_199_254_740_995,
                   "squared_close_returns_ticks2": 9_007_199_254_740_997,
                   "x_width_ticks": 1.25}
        populated = _rows_table([literal], kind="paths")
        self.assertEqual(empty_values.schema, populated.schema)
        for name in ("origin_ns", "endpoint_ns", "terminal_ticks", "squared_close_returns_ticks2"):
            self.assertEqual(populated.schema.field(name).type, pa.int64())
            self.assertEqual(empty_values[name].to_pylist(), [None])
        self.assertEqual(populated.schema.field("x_width_ticks").type, pa.float64())
        sink = pa.BufferOutputStream()
        pq.write_table(populated, sink)
        restored = pq.read_table(pa.BufferReader(sink.getvalue()))
        self.assertEqual(restored.schema, populated.schema)
        for name, value in literal.items():
            self.assertEqual(restored[name].to_pylist(), [value])
        with self.assertRaises(ContractError):
            _rows_table([{"undeclared_extra_column": 1}], kind="paths")

    def test_actual_cash_date_population_skips_thanksgiving_and_weekend(self):
        days = cash_dates(calendar(), date(2024, 11, 27), date(2024, 12, 2))
        self.assertEqual([day.day.isoformat() for day in days], ["2024-11-27", "2024-11-29", "2024-12-02"])
        self.assertEqual([day.state for day in days], ["regular", "early_close", "regular"])
        self.assertEqual(utc(days[1].open_at), "2024-11-29T14:30:00+00:00")
        self.assertEqual(utc(days[1].close_at), "2024-11-29T18:00:00+00:00")
        self.assertEqual(utc(days[2].close_at), "2024-12-02T21:00:00+00:00")

    def test_prior_is_friday_actual_session_not_sunday_and_literal_close_stays_separate(self):
        friday, monday = cash(date(2024, 11, 29)), cash(date(2024, 12, 2))
        bars = series(session_rows(friday, volume=10) + session_rows(monday, volume=100))
        result = list(extract_dates(bars, (friday, monday), root="NQ", recipes=recipes(),
                                    plan=plan(), evaluation_cut=monday.close_at + 2 * M))
        first_actual = formation(result[0], "RTH_actual")
        literal = formation(result[0], "literal_RTH")
        self.assertEqual(first_actual["status"], "complete")
        self.assertEqual(first_actual["expected_minutes"], 210)
        self.assertEqual(utc(first_actual["formation_end_ns"]), "2024-11-29T18:00:00+00:00")
        self.assertEqual(literal["status"], "unavailable")
        self.assertEqual(literal["expected_minutes"], 390)
        self.assertEqual(utc(literal["formation_end_ns"]), "2024-11-29T21:00:00+00:00")
        prior = formation(result[1], "prior_RTH_preopen")
        self.assertEqual(prior["status"], "complete")
        self.assertEqual(prior["date"], "2024-12-02")
        self.assertEqual(utc(prior["formation_start_ns"]), "2024-11-29T14:30:00+00:00")
        self.assertEqual(utc(prior["formation_end_ns"]), "2024-11-29T18:00:00+00:00")
        self.assertEqual(utc(prior["origin_ns"]), "2024-12-02T14:30:00+00:00")
        self.assertEqual(prior["expected_minutes"], 210)
        first_prior = formation(result[0], "prior_RTH_preopen")
        self.assertEqual(first_prior["status"], "unavailable")
        self.assertIn("outside_primary_admitted_history", first_prior["exclusion_reasons"])

    def test_activity_uses_only_prior_dates_and_features_survive_later_price_removal(self):
        friday, monday = cash(date(2024, 11, 29)), cash(date(2024, 12, 2))
        prior_rows = session_rows(friday, volume=10)
        full = series(prior_rows + session_rows(monday, volume=100))
        removed = series(prior_rows + session_rows(monday, volume=100, count=3))
        full_days = list(extract_dates(full, (friday, monday), root="NQ", recipes=recipes(),
                                       plan=plan(), evaluation_cut=monday.close_at + 2 * M))
        short_days = list(extract_dates(removed, (friday, monday), root="NQ", recipes=recipes(),
                                        plan=plan(), evaluation_cut=monday.close_at + 2 * M))
        no_history = formation(full_days[0], "OR_activity_1_1")
        self.assertEqual(no_history["activity_reference_dates"], 0)
        self.assertIsNone(no_history["activity_threshold"])
        self.assertEqual(no_history["status"], "unavailable")
        full_activity = formation(full_days[1], "OR_activity_1_1")
        short_activity = formation(short_days[1], "OR_activity_1_1")
        # Friday OR15=15*10=150. Monday completed OR15=1500 cannot
        # supply Monday's threshold; the prior threshold completes at minute2.
        self.assertEqual(full_activity["activity_threshold"], 150)
        self.assertEqual(full_activity["activity_reference_dates"], 1)
        self.assertEqual(full_activity["expected_minutes"], 2)
        self.assertEqual(full_activity["formation_end_ns"], monday.open_at + 2 * M)
        self.assertEqual(full_activity["origin_ns"], monday.open_at + 3 * M)
        self.assertEqual(feature_fields(full_activity), feature_fields(short_activity))
        self.assertEqual(short_activity["status"], "complete")
        for rows in (full_days[1], short_days[1]):
            early = formation(rows, "literal_00")
            self.assertIsNone(early["x_opening_width_ratio"])
            self.assertIsNone(early["x_opening_last_close_position"])
        full_path = next(row for row in full_days[1]["paths"]
                         if row["clock"] == "OR_activity_1_1" and row["horizon"] == "after_3m")
        short_path = next(row for row in short_days[1]["paths"]
                          if row["clock"] == "OR_activity_1_1" and row["horizon"] == "after_3m")
        self.assertEqual(full_path["status"], "observed")
        self.assertEqual(short_path["status"], "censored")
        self.assertEqual(feature_fields(full_path), feature_fields(short_path))
        self.assertEqual(len(full_days[1]["formations"]), len(short_days[1]["formations"]))
        self.assertEqual(len(full_days[1]["paths"]), len(short_days[1]["paths"]))

    def test_origin_open_remains_a_label_until_its_bar_publication(self):
        day = cash(date(2024, 6, 3))
        begin, origin = day.open_at, day.open_at + 2 * M
        rows = [(begin, 100, 101, 99, 100, 10),
                (begin + M, 500, 550, 450, 520, 10),
                (origin, 900, 950, 850, 920, 10)]
        full = series(rows)
        truncated = series(rows[:1])
        kwargs = {"origin": origin, "cash": day, "prior": None, "prior_widths": (),
                  "anchors": {}, "recipe": {}}
        values = features_at(full.window(begin, begin + M), **kwargs)
        absent = features_at(truncated.window(begin, begin + M), **kwargs)
        self.assertEqual(values, absent)
        self.assertEqual(values["x_last_close_position"], 0.5)
        self.assertEqual(values["x_last_close_age_minutes"], 1)
        not_yet_published = full.window(origin, origin + M, available_at=origin)
        self.assertFalse(not_yet_published.complete)
        self.assertIn("final_bar_not_available", not_yet_published.reasons)
        published = full.window(origin, origin + M, available_at=origin + 2 * M)
        self.assertTrue(published.complete)
        self.assertEqual(published.summary()["open_ticks"], 900)

    def test_complete_future_censored_but_earlier_observed_event_is_retained(self):
        day = cash(date(2024, 6, 3))
        begin, origin = day.open_at, day.open_at + 2 * M
        bars = series([(begin, 100, 101, 99, 100, 10),
                       (origin, 100, 103, 99, 102, 10),
                       (origin + 2 * M, 102, 104, 101, 103, 10)])
        window = bars.window(begin, begin + M)
        future = bars.window(origin, origin + 3 * M, contract_key=RAW, available_at=origin + 4 * M)
        prefix = observed_prefix(future, available_cut=origin + 4 * M)
        self.assertFalse(future.complete)
        self.assertIsNotNone(prefix)
        self.assertEqual(prefix.expected_minutes, 1)
        self.assertEqual(prefix.end, origin + M)
        literal = {"date": "2024-06-03", "year": 2024, "clock": "literal", "formation_id": "literal-formation",
                   "exclusion_reasons": "", "contract_key": RAW, "zero_width": False,
                   "available_at_ns": origin, "low_ticks": 99, "high_ticks": 101, "width_ticks": 2}
        features = features_at(window, origin=origin, cash=day, prior=None,
                               prior_widths=(), anchors={}, recipe={})
        out = path_row((literal, window), origin=origin, endpoint=origin + 3 * M,
                       horizon="literal_3m", features=features, available_cut=origin + 4 * M, root="NQ")
        self.assertEqual(out["status"], "censored")
        self.assertEqual(out["observed_prefix_minutes"], 1)
        self.assertTrue(out["prefix_upper_breach"])
        self.assertEqual(out["prefix_first_lower_minutes"], 0)
        self.assertEqual(out["prefix_first_upper_minutes"], 1)
        self.assertEqual(out["prefix_maturity_at_ns"], origin + 2 * M)
        self.assertIsNone(out["terminal_ticks"])
        self.assertIsNone(out["upper_breach"])

    def test_cash_open_gap_waits_for_publication_and_differs_from_last_close_displacement(self):
        previous, day = cash(date(2024, 5, 31)), cash(date(2024, 6, 3))
        begin = day.open_at
        bars = series([(previous.close_at - M, 100, 102, 98, 100, 10),
                       (begin - 3 * M, 105, 106, 104, 105, 10),
                       (begin, 110, 114, 109, 112, 10)])
        prior = bars.window(previous.close_at - M, previous.close_at)
        target = bars.window(begin - 3 * M, begin - 2 * M)
        kwargs = {"cash": day, "prior": prior, "prior_widths": (), "anchors": {}, "recipe": {}}
        before_publication = features_at(target, origin=begin + M, **kwargs)
        after_publication = features_at(target, origin=begin + 2 * M, **kwargs)
        self.assertIsNone(before_publication["x_observed_cash_open_gap_ticks"])
        self.assertEqual(before_publication["x_prior_last_close_displacement_ticks"], 5)
        self.assertEqual(after_publication["x_observed_cash_open_gap_ticks"], 10)
        self.assertEqual(after_publication["x_prior_last_close_displacement_ticks"], 12)

    def test_prefix_respects_publication_cut_and_different_raw_coordinate(self):
        day = cash(date(2024, 6, 3))
        begin = day.open_at
        bars = series([(begin, 100, 103, 99, 102, 10),
                       (begin + M, 102, 104, 101, 103, 10)])
        future = bars.window(begin, begin + 2 * M, available_at=begin + 2 * M)
        prefix = observed_prefix(future, available_cut=begin + 10 * M)
        self.assertEqual(prefix.expected_minutes, 1)
        self.assertEqual(prefix.observation_cut_ns, begin + 2 * M)
        other = bars.window(begin, begin + 2 * M, contract_key="different-coordinate")
        self.assertIsNone(observed_prefix(other, available_cut=begin + 10 * M))


if __name__ == "__main__":
    unittest.main()
