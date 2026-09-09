"""The frozen E0 source integration cases.

The golden file is the case authority.  These tests keep every frozen case
identifier and variant visible while exercising the public typed adapters with
the retained source fixture.  The fixture's dates are deliberately sparse
engineering dates; assertions therefore compare the causal contract and exact
arithmetic rather than pretending that those rows are the historical golden
market tape.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

from trading_research.context.ranges import range_version
from trading_research.data.book import RecoveryCertificate
from trading_research.data.events import Flags, LatencyScenario
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.execution.accounting import AccountingLedger, TradingFill
from trading_research.execution.costs import FeeSchedule
from trading_research.execution.venue import VenuePath
from trading_research.experiments.e0.admission import (
    admit_e0_day,
    separate_scope_manifests,
)
from trading_research.experiments.e0.candidates import stop_distance
from trading_research.experiments.e0.observations import (
    build_e0_decision_population,
    label_e0_candidate,
)
from trading_research.experiments.e0.source_bridge import (
    freeze_e0_ranges,
    reconcile_trade_streams,
    venue_path_from_mbp,
)
from trading_research.foundations.cash_calendar import e0_window
from trading_research.foundations.instruments import instrument_identity
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest

from e0_source_fixtures import fee_schedule, make_int01_source, make_source_day, shared_comparator_source
from e0_source_case_fixtures import (
    check_int02_f01, check_int02_f02, check_int02_f03,
    check_int03_f01, check_int03_f02, check_int03_f03,
    check_int05_f01, check_int05_f02, check_int05_f03,
)

from e0_source_operational_cases import (
    check_int04_f01, check_int04_f02, check_int04_f03,
    check_int12_f01, check_int12_f02, check_int12_f03, check_scope_f01,
)


GOLDEN_PATH = Path(__file__).with_name("golden") / "e0_integration_v1.json"
NS = 1_000_000_000
MINUTE = 60 * NS


def _golden() -> dict:
    with GOLDEN_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _case(case_id: str) -> dict:
    return next(case for case in _golden()["cases"] if case["case_id"] == case_id)


def _expected(case_id: str) -> dict:
    return _case(case_id)["expected"]


def _variant(case: dict, variant_id: str) -> dict:
    return next(row for row in case.get("variants", ()) if row["id"] == variant_id)


def _path(source, events=None, *, latency_id="source-integration"):
    return venue_path_from_mbp(
        canonical_events=tuple(source.canonical_events if events is None else events),
        selected_instrument=source.admission,
        coverage=source.coverage,
        latency_scenario=LatencyScenario(latency_id, "event", 0, 0),
        market_state="continuous",
        tick_size=source.operational.terms.tick_size,
    )


def _population(source, *, cuts=None, midpoint=None, objects_override=None, path_coverage=None):
    cuts = tuple(source.cuts if cuts is None else cuts)
    sampled = None if midpoint is None else {cut: midpoint for cut in cuts}
    return build_e0_decision_population(
        frozen_context=source.context,
        completed_cuts=cuts,
        sampled_midpoints=sampled,
        object_versions=objects_override,
        path_coverage=path_coverage,
        policy_id="frozen-e0-source-integration-v1",
    )


class E0SourceIntegrationTests(unittest.TestCase):
    """One method per frozen case, including each declared variant matrix."""

    def test_e0_int01_f01_complete_parent_volume_selection(self):
        case = _case("E0-INT-01-F01")
        inputs = case["inputs"]
        source = make_int01_source()
        expected = _expected("E0-INT-01-F01")

        self.assertEqual(source.day, date.fromisoformat(inputs["day"]))
        self.assertEqual(source.cut, inputs["cut"]["utc_ns"])
        self.assertEqual(source.admission.cut, inputs["selection_cut_utc_ns"])
        self.assertEqual(source.admission.prior_session_id, inputs["previous_session"]["id"])
        self.assertEqual(source.session_sequence.sessions[0].trading_date, date(2024, 5, 31))
        self.assertEqual(source.session_sequence.sessions[0].open_at, inputs["previous_session"]["start"])
        self.assertEqual(source.session_sequence.sessions[0].close_at, inputs["previous_session"]["end"])
        self.assertEqual(source.session_sequence.sessions[0].known_at, inputs["previous_session"]["known_at"])
        self.assertEqual(tuple(source.universe.contract_ids), tuple(inputs["universe"]["contract_ids"]))
        self.assertEqual(source.universe.coverage_scope, inputs["universe"]["coverage_scope"])
        self.assertEqual(source.universe.known_at, inputs["universe"]["known_at"])
        self.assertEqual(tuple(source.source_manifest["data_versions"]), tuple(inputs["data_versions"]))
        self.assertEqual(tuple(source.source_manifest["golden_inspected_fields"]),
                         tuple(inputs["inspected_fields"]))
        self.assertEqual(expected["status"], "admitted")
        self.assertEqual(source.admission.selected_instrument_id, expected["selected_instrument_id"])
        self.assertEqual(source.admission.selected_lifetime,
                         source.lifetime_aliases[expected["selected_lifetime"]])
        self.assertEqual(
            next(v.contracts for v in source.volumes if v.instrument_id == expected["selected_instrument_id"]),
            expected["selected_contracts"],
        )
        self.assertEqual(source.admission.selected_lifetime,
                         instrument_identity(source.admission.selected_definition))
        self.assertEqual(source.admission.excluded, tuple())
        self.assertEqual(source.admission.selection_evidence["excluded"], {})
        self.assertEqual(len(source.admission.considered), len(inputs["definitions"]))
        self.assertEqual(source.admission.selection_evidence["decision_cut"], inputs["selection_cut_utc_ns"])
        self.assertEqual(source.admission.selection_evidence["input_known_at"],
                         inputs["selection_evidence_known_at"])
        self.assertEqual(source.admission.selection_evidence["volumes"],
                         {"1001": 1200, "1002": 2100})
        self.assertEqual(source.admission.selection_evidence["universe_scope"],
                         inputs["universe"]["coverage_scope"])
        self.assertFalse(source.admission.selection_evidence["published"])
        states = {name: state for name, state, _ in source.admission.completeness.checks}
        self.assertEqual(states, expected["required_check_states"])
        self.assertEqual(tuple(expected["tie_break_order"]),
                         ("contracts_desc", "expiry_at_asc", "canonical_instrument_id_asc"))
        self.assertEqual(set(source.admission.selection_evidence["volumes"]), {"1001", "1002"})
        self.assertTrue(source.admission.completeness.data_versions)

    def test_e0_int01_f02_ties_and_missing_competitor_matrix(self):
        case = _case("E0-INT-01-F02")
        source = make_int01_source()
        self.assertEqual(_expected("E0-INT-01-F02"), {"status": "variant_matrix"})
        self.assertEqual(
            {row["id"] for row in case["variants"]},
            {"tie-earlier-expiry", "tie-same-expiry-id", "missing-competitor"},
        )

        tied = tuple(replace(row, contracts=2000) for row in source.volumes)
        kwargs = dict(
            day=source.day, cut=source.admission.cut, universe=source.universe,
            definitions=source.definitions, volumes=tied,
            session_sequence=source.session_sequence, calendar=source.session_sequence,
            boundary=source.venue_boundary, source_manifest=source.source_manifest,
            terms=source.terms, scope=source.admission.scope,
        )
        earlier = admit_e0_day(**kwargs)
        self.assertEqual(earlier.selected_instrument_id,
                         _variant(case, "tie-earlier-expiry")["expected"]["selected_instrument_id"])
        self.assertEqual(_variant(case, "tie-earlier-expiry")["expected"]["status"], "admitted")
        self.assertEqual(_variant(case, "tie-earlier-expiry")["expected"]["reason"], "earlier expiry")
        self.assertIn("earlier expiry", earlier.selection_evidence["selection_basis"])
        self.assertLess(source.definitions[0].key.expiry_at, source.definitions[1].key.expiry_at)

        same_expiry = source.definitions[0].key.expiry_at
        same_definitions = tuple(replace(d, key=replace(d.key, expiry_at=same_expiry))
                                 for d in source.definitions)
        same_volumes = tuple(replace(v, instrument_lifetime=instrument_identity(d))
                             for v, d in zip(tied, same_definitions))
        same_universe = replace(
            source.universe,
            lifetimes=tuple((d.key.instrument_id, instrument_identity(d)) for d in same_definitions),
        )
        same_id = admit_e0_day(**{**kwargs, "universe": same_universe,
                                  "definitions": same_definitions, "volumes": same_volumes})
        self.assertEqual(same_id.selected_instrument_id,
                         _variant(case, "tie-same-expiry-id")["expected"]["selected_instrument_id"])
        self.assertEqual(_variant(case, "tie-same-expiry-id")["expected"]["status"], "admitted")
        self.assertEqual(_variant(case, "tie-same-expiry-id")["expected"]["reason"],
                         "canonical instrument ID")
        self.assertIn("canonical ID", same_id.selection_evidence["selection_basis"])
        self.assertEqual(same_definitions[0].key.expiry_at, same_definitions[1].key.expiry_at)

        with self.assertRaises(DependencyUnavailable) as raised:
            admit_e0_day(**{**kwargs, "volumes": (tied[0],)})
        missing = _variant(case, "missing-competitor")["expected"]
        self.assertEqual(missing["error_type"], "DependencyUnavailable")
        self.assertEqual(missing["excluded_check"], "prior_session_volume")
        self.assertEqual(str(raised.exception), missing["reason"])
        self.assertEqual(missing["status"], "rejected")

    def test_e0_int01_f03_raw_identity_rejection_matrix(self):
        case = _case("E0-INT-01-F03")
        source = make_int01_source()
        event_source = make_source_day("2024-06-03")
        self.assertEqual(_expected("E0-INT-01-F03")["status"], "all_rejected")
        self.assertTrue(_expected("E0-INT-01-F03")["selected_identity_preserved"])
        variants = case["inputs"]["downstream_variants"]
        self.assertEqual(len(variants), 3)

        mixed_events = tuple(
            replace(event, instrument_id=1001) if index == 1 else event
            for index, event in enumerate(event_source.canonical_events)
        )
        with self.assertRaises(ContractError) as mixed_error:
            venue_path_from_mbp(
                canonical_events=mixed_events,
                selected_instrument=source.admission,
                coverage=event_source.coverage,
                latency_scenario=LatencyScenario("int01-raw-identity", "event", 0, 0),
                market_state="continuous",
            )
        self.assertEqual(str(mixed_error.exception), variants[0]["expected_reason"])

        valid_range = event_source.range_versions[0]
        bad_definition = replace(
            valid_range.definition,
            raw_instrument_definition=variants[1]["raw_instrument_definition"],
        )
        with self.assertRaises(ContractError) as range_error:
            range_version(valid_range.primitive, bad_definition, cut=valid_range.known_at)
        self.assertEqual(str(range_error.exception), variants[1]["expected_reason"])

        with tempfile.TemporaryDirectory(prefix="e0-int01-ledger-") as directory:
            fees = fee_schedule()
            ledger = AccountingLedger(
                Path(directory) / "ledger.jsonl",
                account_id="int01-source-account",
                eligible_dates=(source.day.isoformat(),),
                eligibility_version=source.admission.version,
                terms=((source.admission.selected_instrument_id,
                        source.terms[source.admission.selected_instrument_id]),),
                fees=fees,
            )
            wrong_symbol = TradingFill(
                "int01-wrong-symbol", variants[2]["instrument"], source.day.isoformat(),
                source.cut, 1, 72000, fees.fee("NQ"), fees.version, "int01-fill-source-v1",
            )
            with self.assertRaises(ContractError) as fill_error:
                ledger.fill(wrong_symbol)
        self.assertEqual(str(fill_error.exception), variants[2]["expected_reason"])

    def test_e0_int02_f01_only_final_positive_ranges_publish(self):
        check_int02_f01(self)

    def test_e0_int02_f02_range_corrections_are_immutable_versions(self):
        check_int02_f02(self)

    def test_e0_int02_f03_zero_width_and_prior_binding_matrix(self):
        check_int02_f03(self)

    def test_e0_int03_f01_complete_population_and_order(self):
        check_int03_f01(self)

    def test_e0_int03_f02_missing_midpoint_and_future_gap_keep_rows(self):
        check_int03_f02(self)

    def test_e0_int03_f03_revisions_and_future_births(self):
        check_int03_f03(self)

    def test_e0_int04_f01_canonical_mbp_path_preserves_two_clocks(self):
        check_int04_f01(self)

    def test_e0_int04_f02_book_flags_and_recovery_matrix(self):
        check_int04_f02(self)

    def test_e0_int04_f03_trade_deduplication_and_same_time_matrix(self):
        check_int04_f03(self)

    def test_e0_int05_f01_sampled_contact_and_native_touch_are_separate(self):
        check_int05_f01(self)

    def test_e0_int05_f02_gap_and_unknown_order_matrix(self):
        check_int05_f02(self)

    def test_e0_int05_f03_endpoint_is_inclusive_and_fixed(self):
        check_int05_f03(self)

    def test_e0_int12_f01_calendar_boundary_and_window_matrix(self):
        check_int12_f01(self)

    def test_e0_int12_f02_fee_category_matrix(self):
        check_int12_f02(self)

    def test_e0_int12_f03_eligible_denominator_retains_flat_outage_halted(self):
        check_int12_f03(self)

    def test_e0_scope_f01_historical_and_primary_populations_are_separate(self):
        check_scope_f01(self)


if __name__ == "__main__":
    unittest.main()
