"""Independent scheduled-event measurement cases. No population run."""
from datetime import date, datetime, timezone
import unittest

from trading_research.foundations.time import datetime_ns
from trading_research.research.scheduled_event_measurements import (
    bls_timestamp, build_civil_dates, compile_events, date_record_state,
    link_window, parse_fomc_csv_row, publication_eligibility,
)


def _norm(**overrides):
    row = {
        "event_date": date(2021, 1, 8),
        "event_ts_utc": datetime(2021, 1, 8, 13, 30, tzinfo=timezone.utc),
        "event_time_et": "08:30:00",
        "event_type": "nfp",
        "event_name": "Employment Situation",
        "symbol": None,
        "status": "scheduled_or_observed",
        "time_basis": "standard_release_time",
        "source": "FRED release calendar",
        "source_url": "https://fred.stlouisfed.org/docs/api/fred/release_dates.html",
        "details_json": '{"release_id": 50, "release_last_updated": null}',
    }
    row.update(overrides)
    return row


def _source(subject, path, rows, sha="a" * 64):
    return {"subject": subject, "path": path, "sha256": sha, "rows": rows}


def _topical(economic=None, fomc=None, market=None, earnings=None, combined=None):
    economic = [] if economic is None else economic
    fomc = [] if fomc is None else fomc
    market = [] if market is None else market
    earnings = [] if earnings is None else earnings
    if combined is None:
        combined = list(economic) + list(fomc) + list(market) + list(earnings)
    return [
        _source("economic", "free-sources/context__event-calendar__normalized/economic-releases.parquet", economic),
        _source("fomc", "free-sources/context__event-calendar__normalized/fomc-meetings.parquet", fomc),
        _source("market", "free-sources/context__event-calendar__normalized/market-calendar.parquet", market),
        _source("earnings", "free-sources/context__event-calendar__normalized/mega-cap-earnings.parquet", earnings),
        _source("combined", "free-sources/context__event-calendar__normalized/combined-event-calendar.parquet", combined),
    ]


class ScheduledEventMeasurementTests(unittest.TestCase):
    def test_dst_winter_830_et_is_1330_utc(self):
        ns = bls_timestamp(date(2021, 1, 8), "08:30")
        expected = datetime_ns(datetime(2021, 1, 8, 13, 30, tzinfo=timezone.utc))
        self.assertEqual(ns, expected)

    def test_dst_summer_830_et_is_1230_utc(self):
        ns = bls_timestamp(date(2021, 7, 2), "08:30")
        expected = datetime_ns(datetime(2021, 7, 2, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(ns, expected)

    def test_fomc_date_only_does_not_invent_1400(self):
        row = _norm(
            event_date=date(2021, 4, 28), event_ts_utc=None, event_time_et=None,
            event_type="fomc", event_name="FOMC meeting decision date",
            time_basis="date_only", status="held", source="Federal Reserve",
            details_json='{"meeting_end": "2021-04-28", "meeting_start": "2021-04-27"}',
        )
        compiled = compile_events(_topical(fomc=[row]))
        event = compiled["topical_events"][0]
        self.assertEqual(event["time_basis"], "date_only")
        self.assertIsNone(event["event_ts_utc_ns"])
        self.assertIsNone(event["event_time_et"])
        self.assertFalse(event["intraday_functions_defined"])
        self.assertNotIn("14:00", str(event["details"]))
        self.assertNotIn("14:00", str(event.get("event_time_et")))

    def test_future_publication_cannot_be_early_known(self):
        eligibility = publication_eligibility(
            event_date=date(2020, 11, 6), event_ts_utc_ns=None,
            time_basis="standard_release_time", snapshot_date=date(2021, 6, 5),
        )
        self.assertIsNone(eligibility["known_at_ns"])
        self.assertFalse(eligibility["causal_feature_eligible"])
        self.assertTrue(eligibility["publication_after_event"])
        later = datetime_ns(datetime(2021, 6, 5, 12, 0, tzinfo=timezone.utc))
        event_at = datetime_ns(datetime(2020, 11, 6, 13, 30, tzinfo=timezone.utc))
        after = publication_eligibility(
            event_date=date(2020, 11, 6), event_ts_utc_ns=event_at,
            time_basis="standard_release_time", explicit_published_at_ns=later,
        )
        self.assertIsNone(after["known_at_ns"])
        self.assertFalse(after["causal_feature_eligible"])

    def test_combined_multiset_alias_is_not_double_sample(self):
        economic = [_norm()]
        fomc = [_norm(
            event_date=date(2021, 4, 28), event_ts_utc=None, event_time_et=None,
            event_type="fomc", event_name="FOMC meeting decision date",
            time_basis="date_only", status="held")]
        market = [_norm(
            event_date=date(2021, 3, 19), event_ts_utc=None, event_time_et=None,
            event_type="monthly_opex", event_name="US monthly option expiration",
            time_basis="date_only")]
        earnings = [_norm(
            event_date=date(2021, 1, 27), event_type="mega_cap_earnings",
            event_name="AAPL earnings", symbol="AAPL", time_basis="source_timestamp",
            event_time_et="16:00:00",
            event_ts_utc=datetime(2021, 1, 27, 21, 0, tzinfo=timezone.utc),
            details_json='{"eps_estimate": 0.99, "surprise_pct": 1.0}')]
        compiled = compile_events(_topical(economic=economic, fomc=fomc, market=market, earnings=earnings))
        self.assertTrue(compiled["combined_is_alias"])
        self.assertEqual(compiled["combined_row_count"], 4)
        self.assertEqual(compiled["topical_row_count"], 4)
        self.assertEqual(sum(1 for event in compiled["events"] if event["independent_support"]), 4)
        self.assertEqual(sum(1 for event in compiled["combined_events"] if event["independent_support"]), 0)
        self.assertTrue(all(event["role"] == "combined_alias" for event in compiled["combined_events"]))

    def test_csv_disagreement_is_retained(self):
        fomc = [_norm(
            event_date=date(2021, 4, 28), event_ts_utc=None, event_time_et=None,
            event_type="fomc", event_name="FOMC meeting decision date",
            time_basis="date_only", status="held")]
        economic = [_norm(event_date=date(2021, 1, 13), event_type="cpi",
                          event_name="Consumer Price Index",
                          event_ts_utc=datetime(2021, 1, 13, 13, 30, tzinfo=timezone.utc))]
        sources = _topical(economic=economic, fomc=fomc)
        sources.append(_source(
            "fomc_alternative",
            "free-sources/central-banks__fomc-and-boj-calendars/calendar_fomc.csv",
            [{"year": "2021", "month": "April", "days": "26-27"}]))
        sources.append(_source(
            "bls", "free-sources/bls__release-calendars/bls_release_dates.csv",
            [{"release_name": "CPI", "reference_month": "December 2020", "date": "2021-01-13",
              "time_et": "08:31", "status": "actual", "wayback_snapshot_date": "2021-06-07"}]))
        compiled = compile_events(sources)
        alt = [event for event in compiled["alternative_events"] if event["subject"] == "fomc_alternative"]
        self.assertEqual(len(alt), 1)
        self.assertEqual(alt[0]["event_date"], "2021-04-27")
        self.assertFalse(alt[0]["unparsed"])
        self.assertEqual(compiled["agreements"]["fomc_vs_alternative"]["left_only"], 1)
        self.assertEqual(compiled["agreements"]["fomc_vs_alternative"]["right_only"], 1)
        self.assertGreaterEqual(compiled["agreements"]["economic_vs_bls"]["disagreements"], 1)
        self.assertEqual(sum(1 for event in compiled["events"] if event["subject"] == "fomc"), 1)
        self.assertEqual(sum(1 for event in compiled["events"] if event["subject"] == "fomc_alternative"), 1)
        self.assertEqual(sum(1 for event in compiled["events"] if event["subject"] == "bls"), 1)

    def test_half_open_start_included_end_excluded(self):
        start = datetime_ns(datetime(2021, 1, 8, 13, 30, tzinfo=timezone.utc))
        end = datetime_ns(datetime(2021, 1, 8, 13, 45, tzinfo=timezone.utc))
        event_at_start = {
            "event_date": "2021-01-08", "event_type": "nfp", "semantic_id": "nfp|2021-01-08||08:30:00",
            "time_basis": "standard_release_time", "intraday_functions_defined": True,
            "event_ts_utc_ns": start,
        }
        event_at_end = {
            "event_date": "2021-01-08", "event_type": "nfp", "semantic_id": "nfp|2021-01-08||end",
            "time_basis": "standard_release_time", "intraday_functions_defined": True,
            "event_ts_utc_ns": end,
        }
        window = {"date": "2021-01-08", "start_ns": start, "end_ns": end, "available_at_ns": end}
        included = link_window(window, [event_at_start])
        excluded = link_window(window, [event_at_end])
        self.assertTrue(included["interval_overlap"])
        self.assertIn(event_at_start["semantic_id"], included["interval_overlap_ids"])
        self.assertFalse(excluded["interval_overlap"])
        self.assertEqual(excluded["interval_overlap_ids"], ())

    def test_missing_coverage_is_not_no_event(self):
        rows = build_civil_dates([], start=date(2021, 1, 4), end=date(2021, 1, 6))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["record_state"], "no_record_on_date")
            self.assertEqual(row["coverage_state"], "coverage_unknown")
            self.assertIsNone(row["ordinary_or_no_event_label"])
            self.assertNotEqual(row["record_state"], "no_event")
            self.assertNotEqual(row["coverage_state"], "ordinary")
        state = date_record_state([])
        self.assertEqual(state["record_state"], "no_record_on_date")
        self.assertEqual(state["coverage_state"], "coverage_unknown")
        self.assertIsNone(state["ordinary_or_no_event_label"])

    def test_compile_events_does_not_mutate_source_rows(self):
        row = _norm()
        before = dict(row)
        compiled = compile_events(_topical(economic=[row]))
        self.assertEqual(row, before)
        self.assertIsNot(compiled["topical_events"][0]["details"], row)
        row["event_type"] = "mutated"
        self.assertEqual(compiled["topical_events"][0]["event_type"], "nfp")

    def test_fomc_odd_string_stays_unparsed(self):
        parsed = parse_fomc_csv_row({"year": "2021", "month": "April/May", "days": "27-28"})
        self.assertTrue(parsed["unparsed"])
        self.assertIsNone(parsed["decision_date"])
        crossing = parse_fomc_csv_row({"year": "2021", "month": "January", "days": "31-1"})
        self.assertTrue(crossing["unparsed"])
        decision = parse_fomc_csv_row({"year": "2021", "month": "April", "days": "27-28"})
        self.assertFalse(decision["unparsed"])
        self.assertEqual(decision["decision_date"], date(2021, 4, 28))
        self.assertEqual(decision["range_start"], date(2021, 4, 27))

    def test_date_only_event_has_no_intraday_overlap(self):
        start = datetime_ns(datetime(2021, 4, 28, 14, 0, tzinfo=timezone.utc))
        end = datetime_ns(datetime(2021, 4, 28, 15, 0, tzinfo=timezone.utc))
        event = {
            "event_date": "2021-04-28", "event_type": "fomc", "semantic_id": "fomc|2021-04-28||date_only",
            "time_basis": "date_only", "intraday_functions_defined": False, "event_ts_utc_ns": None,
        }
        linked = link_window({"date": "2021-04-28", "start_ns": start, "end_ns": end, "available_at_ns": end}, [event])
        self.assertTrue(linked["event_day"])
        self.assertTrue(linked["date_only_event_day"])
        self.assertFalse(linked["interval_overlap"])
        self.assertFalse(linked["causal_feature_eligible"])
        self.assertTrue(linked["event_labels_retrospective"])
        self.assertEqual(linked["feature_known_at_ns"], end)
        self.assertIsNone(linked["target_end_ns"])


    def test_equal_formatted_times_alias_and_no_event_rate_inference(self):
        from trading_research.research.scheduled_event_measurements import summarize_population
        sources = _topical(economic=[_norm()])
        sources.append(_source("bls","bls_release_dates.csv",[{"release_name":"Employment Situation","reference_month":"2020-12","date":"2021-01-08","time_et":"08:30","status":"actual","wayback_snapshot_date":"2021-06-05"}]))
        compiled = compile_events(sources)
        self.assertEqual(compiled["agreements"]["economic_vs_bls"]["equal_aliases"],1)
        self.assertEqual(compiled["agreements"]["economic_vs_bls"]["disagreements"],0)
        self.assertEqual(compiled["topical_events"][0]["semantic_id"], compiled["alternative_events"][0]["semantic_id"])
        self.assertFalse(summarize_population(compiled,build_civil_dates(compiled["events"]))["event_day_rate_intervals"]["applied"])

    def test_unparsed_fomc_survives_compilation(self):
        sources = _topical()
        sources.append(_source("fomc_alternative","calendar_fomc.csv",[{"year":"2021","month":"April/May","days":"27-28"}]))
        event=compile_events(sources)["alternative_events"][0]
        self.assertTrue(event["unparsed"])
        self.assertIsNone(event["event_date"])
        self.assertIsNone(event["known_at_ns"])

    def test_prior_civil_date_event_links_overnight_interval(self):
        at=datetime_ns(datetime(2021,1,8,21,0,tzinfo=timezone.utc))
        event={"event_date":"2021-01-08","event_type":"earnings","semantic_id":"prior", "time_basis":"source_timestamp","intraday_functions_defined":True,"event_ts_utc_ns":at}
        linked=link_window({"date":"2021-01-11","start_ns":at-60_000_000_000,"end_ns":at+60_000_000_000,"available_at_ns":at+120_000_000_000},[event])
        self.assertFalse(linked["event_day"])
        self.assertTrue(linked["interval_overlap"])
        self.assertIsNone(linked["target_end_ns"])

    def test_actual_formation_link_shape_and_nullable_event_time_roundtrip(self):
        import pyarrow as pa
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from trading_research.research.auction_flow_storage import BoundedOutputs
        from trading_research.research.scheduled_event_measurements import _link_shard_table, _event_table, _write_parquet
        at=datetime_ns(datetime(2021,4,28,14,0,tzinfo=timezone.utc))
        row={"date":"2021-04-28","clock":"prior_RTH_preopen","formation_id":"f","root":"NQ","year":2021,"contract_key":"NQH1","source_version":"v","definition":"d","source_ids":"source","window_version":"w","formation_start_ns":at-60_000_000_000,"formation_end_ns":at,"available_at_ns":None,"status":"unavailable"}
        linked=_link_shard_table(pa.Table.from_pylist([row]),source_variant="primary",events_by_date={},civil_by_date={})
        self.assertEqual(linked.num_rows,1)
        self.assertIsNone(linked["target_end_ns"][0].as_py())
        self.assertEqual(linked["formation_status"][0].as_py(),"unavailable")
        event=compile_events(_topical(fomc=[_norm(event_type="fomc",event_ts_utc=None,event_time_et=None,time_basis="date_only")]))["events"][0]
        table=_event_table([event])
        self.assertEqual(table.schema.field("known_at_ns").type,pa.int64())
        with TemporaryDirectory() as td:
            outputs=BoundedOutputs(Path(td)/"outputs",maximum_total_bytes=1000000,maximum_file_bytes=1000000)
            result=_write_parquet(outputs,"events.parquet",table,kind="fixture")
            self.assertTrue(result["roundtrip_exact"])



    def test_raw_bls_triplet_fidelity_and_unconfirmed_schedule(self):
        from trading_research.research.scheduled_event_measurements import parse_bls_html,compare_bls_csv_html
        raw=b"<table><tr><th>Reference Month</th><th>Release Date</th><th>Release Time</th></tr><tr><td>December 2020</td><td>Jan. 8, 2021</td><td>08:30 AM</td></tr></table>"
        parsed=parse_bls_html(raw,"empsit_2021.htm","a"*64)
        self.assertEqual(parsed["rows"][0]["event_date"],"2021-01-08")
        sources=_topical()
        sources.append(_source("bls","bls_release_dates.csv",[{"release_name":"Employment Situation","reference_month":"December 2020","date":"2021-01-08","time_et":"08:30","status":"scheduled_at_capture","wayback_snapshot_date":"2020-12-01"}]))
        compiled=compile_events(sources)
        self.assertFalse(compiled["events"][0]["source_labels_occurred"])
        result=compare_bls_csv_html(compiled["events"],[{"html_release_rows":parsed["rows"]}])
        self.assertTrue(result["all_csv_triplets_found"])
        self.assertEqual(result["matched_csv_rows"],1)


if __name__ == "__main__":
    unittest.main()
