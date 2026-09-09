"""Frozen INT11: actual causal prefixes, source interventions, and V04 ports."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests.e0_source_fixtures import _native_event, make_run_day
from trading_research.data.book import BookCheckpoint, BookReducer, BookState
from trading_research.data.events import LatencyScenario, Quote, decode_fields, normalize_mbp
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.execution.accounting import AccountingLedger
from trading_research.execution.orders import OrderLedger
from trading_research.execution.replay import BracketPlan, reference_bracket
from trading_research.execution.venue import FillScenario
from trading_research.experiments.e0.candidates import VisitTracker
from trading_research.experiments.e0.observations import build_e0_decision_population
from trading_research.experiments.e0.reporting import (
    E0Parity, EconomicInterval, attribute_e0_fault, compare_e0_prefixes, e0_quality_report,
)
from trading_research.experiments.e0.runner import SCENARIOS, _thaw_checkpoint_value
from trading_research.experiments.e0.source_bridge import NativeCoverageReceipt, venue_path_from_mbp
from trading_research.foundations.contracts import Decision
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.journal import Journal
from trading_research.research.protocols import QualityEvidence


REPO = Path(__file__).resolve().parents[1]
NS = 1_000_000_000


def literal(identity):
    return next(case for case in json.loads((REPO / "tests/golden/e0_integration_v1.json").read_bytes())["cases"]
                if case["case_id"] == identity)


def native_quote(day, *, row, at, midpoint, sequence=None, flags=128):
    event = _native_event(day=date.fromisoformat(day.day), row=row,
        sequence=row if sequence is None else sequence, event_at=at, action="A",
        bid_ticks=midpoint - 1, ask_ticks=midpoint + 1, size=1, side="N", flags=flags)
    return normalize_mbp(decode_fields(event.raw_fields), event.address, native=True,
                          scenario=LatencyScenario("INT11-known-after-250ms", "event", 250_000_000, 0))


def source_path(day, events):
    events = tuple(events)
    receipt = NativeCoverageReceipt.from_events(events, source_id=events[0].address.dataset_id,
        schema_version=events[0].address.schema_version, instrument_id=day.context.instrument,
        source_order_known=all(event.provider_sequence is not None for event in events),
        complete_intervals=((min(event.clocks.event_at for event in events) - NS,
                             max(event.clocks.event_at for event in events) + 61*NS),),
        recovery_complete=True,
        coverage_version=digest(("INT11-actual-retained-native-window", tuple(event.id for event in events))))
    return venue_path_from_mbp(canonical_events=tuple(events), selected_instrument=day.context.selected_day,
        coverage=receipt, recovery_certificates=day.recovery_certificates,
        tick_size=day.operational.terms.tick_size,
        latency_scenario=LatencyScenario("INT11-known-after-250ms", "event", 250_000_000, 0), market_state="continuous")


def prefix_run(root, day, events, *, restart=False):
    """Advance two actual cuts; restart between them after the e-0931 event."""
    root = Path(root)
    case = literal("E0-INT-11-F01")
    cuts = tuple(row["cut"] for row in case["inputs"]["decision_observations"])
    book, tracker = BookReducer(), VisitTracker(maximum_gap_ns=60 * NS)
    observations, contacts, cursor = [], [], 0
    orders = OrderLedger(root / "orders.sqlite", account_id="synthetic-account-1")
    account = AccountingLedger(root / "account.sqlite", account_id=orders.account_id,
        eligible_dates=(day.day,), eligibility_version=digest((day.day, cuts)),
        terms=((day.context.instrument, day.operational.terms),), fees=day.operational.fees)
    decisions = Journal(root / "decisions.sqlite")
    for index, cut in enumerate(cuts):
        while cursor < len(events) and events[cursor].clocks.known_at <= cut:
            book.apply(events[cursor]); cursor += 1
        standing = book.standing(int(day.context.instrument), cut=cut, max_age_ns=120 * NS)
        midpoint = Fraction(standing.quote.bid + standing.quote.ask) / (2 * Fraction(day.operational.terms.tick_size))
        observations.append({"cut": cut, "midpoint_ticks": int(midpoint),
            "source_event_id": standing.source_event_id, "source_event_known_at": standing.known_at})
        contacts.extend(tracker.observe(cut=cut, price=midpoint, candidates=day.context.objects))
        orders.reconcile(id="prefix-flat:" + str(cut), known_at=cut, positions={}, open_order_ids=(),
            open_orders_complete=True, execution_history_complete=True, evidence_version=digest((cut, "synthetic-flat")))
        population = build_e0_decision_population(frozen_context=day.context,
            completed_cuts=cuts[:index+1], sampled_midpoints={row["cut"]: row["midpoint_ticks"] for row in observations},
            policy_id="E0-prefix-v1")
        current = population.by_cut(cut)
        decision = Decision(current.id, cut, tuple(row.id for row in current.rows), "flat_or_wait",
            tuple((row.id, "always_flat_policy") for row in current.rows), digest(orders.state()), (),
            None, None, "not_called_for_entry", cut, None)
        decisions.append(key="cut:" + str(cut), kind="decision", payload={"decision": decision, "population": current})
        if restart and index == 0:
            # e-0931 arrives after the first decision. Persist its actual book
            # state and the already published visit/decision/account prefix.
            while cursor < len(events) and events[cursor].clocks.known_at < cuts[1]:
                book.apply(events[cursor]); cursor += 1
            checkpoint = root / "prefix-checkpoint.json"
            checkpoint.write_bytes(canonical_json({"book": book.checkpoint(), "visits": tracker.checkpoint(),
                "cursor": cursor, "observations": observations, "order_head": digest(orders.journal.read()),
                "account_head": digest(account.journal.read()), "decision_head": digest(decisions.read())}))
            stored = _thaw_checkpoint_value(json.loads(checkpoint.read_bytes()))
            raw_book = stored["book"]
            state = tuple(BookState(**{**row, "quote": None if row["quote"] is None else Quote(**row["quote"])})
                          for row in raw_book["states"])
            book = BookReducer.restore(BookCheckpoint(raw_book["decoder_version"], state, raw_book["source_rows"]))
            tracker = VisitTracker.restore(stored["visits"])
            cursor, observations = stored["cursor"], list(stored["observations"])
            orders = OrderLedger(root / "orders.sqlite", account_id=orders.account_id)
            account = AccountingLedger(root / "account.sqlite", account_id=orders.account_id,
                eligible_dates=(day.day,), eligibility_version=digest((day.day, cuts)),
                terms=((day.context.instrument, day.operational.terms),), fees=day.operational.fees)
            decisions = Journal(root / "decisions.sqlite")
            assert stored["order_head"] == digest(orders.journal.read())
            assert stored["account_head"] == digest(account.journal.read())
            assert stored["decision_head"] == digest(decisions.read())
    state = {"source": {"book_checkpoint": book.checkpoint()},
        "measurement": {"observations": observations},
        "object": {"objects": day.context.objects, "visits": tracker.checkpoint(), "contacts": tuple(contacts)},
        "decision": {"population_hash": digest((population.population_hash,)), "journal": decisions.read()},
        "order": {"journal_head": digest(orders.journal.read()), "state": orders.state()},
        "account": {"report_version": digest(account.report()), "report": account.report()}}
    return state, tuple(observations), population


def quality_components(fixture, *, orders=None):
    orders = fixture["orders"] if orders is None else orders
    return {"source": {"path_versions": tuple(path.version for path in fixture["paths"])},
        "measurement": {"replay_versions": tuple(digest(outcome) for outcome in fixture["outcomes"])},
        "object": {"population_versions": tuple(pop.population_hash for pop in fixture["populations"])},
        "decision": {"population_hash": fixture["population_hash"], "plan_versions": tuple(plan.version for plan in fixture["plans"])},
        "order": {"journal_head": digest(orders.journal.read()), "state": orders.state()},
        "account": {"report_version": digest(fixture["accounting"].report()), "report": fixture["accounting"].report()}}


class E0ReportingIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.day = make_run_day("2024-06-03", quote_path="comparator_down")

    def test_e0_int_11_f01_real_source_visit_order_and_account_prefix_restart(self):
        case = literal("E0-INT-11-F01")
        events = tuple(native_quote(self.day, row=index+10, at=row["event_at"], midpoint=row["price_ticks"])
                       for index, row in enumerate(case["inputs"]["events"]))
        for event, expected in zip(events, case["inputs"]["events"]):
            self.assertEqual(event.clocks.event_at, expected["event_at"])
            self.assertEqual(event.clocks.known_at, expected["known_at"])
        full, observations, population = prefix_run(self.root / "full", self.day, events)
        deleted, other, _ = prefix_run(self.root / "deleted", self.day, events[:-1])
        restarted, recovered, _ = prefix_run(self.root / "restarted", self.day, events, restart=True)
        self.assertEqual(observations, other)
        self.assertEqual(observations, recovered)
        for observed, expected in zip(observations, case["inputs"]["decision_observations"]):
            self.assertEqual(observed["cut"], expected["cut"])
            self.assertEqual(observed["midpoint_ticks"], expected["midpoint_ticks"])
            self.assertEqual(observed["source_event_known_at"], expected["source_event_known_at"])
            same_cut = next(event for event in events if event.clocks.event_at == observed["cut"])
            self.assertEqual(same_cut.clocks.known_at, expected["same_cut_event_known_at"])
            self.assertGreater(same_cut.clocks.known_at, observed["cut"])
            self.assertNotEqual(observed["source_event_id"], same_cut.id)
        parity = compare_e0_prefixes(full, deleted, restarted)
        self.assertTrue(parity.passed)
        self.assertEqual(parity.first_divergent_component, case["expected"]["first_divergent_component"])
        self.assertEqual(len(parity.component_hashes), 6)
        self.assertEqual(len(population), 54)
        # The frozen hashes describe this semantic projection, not the actual
        # larger six-component runtime state. Recompute both independently.
        alias = {event.id: row["id"] for event, row in zip(events, case["inputs"]["events"])}
        descriptor = {"cut_event_ids": [alias[row["source_event_id"]] for row in observations],
            "midpoint_ticks": [row["midpoint_ticks"] for row in observations],
            "source_versions": ["mbp-1-synthetic-v1"], "decision_definition": "E0-prefix-v1"}
        self.assertEqual(descriptor, case["inputs"]["prefix_hash_payload"])
        projected = {component: hashlib.sha256(json.dumps({"component": component, **descriptor},
            sort_keys=True, separators=(",", ":")).encode()).hexdigest() for component in ("measurement", "object", "decision")}
        for field in ("full_run_prefix_hashes", "suffix_deleted_prefix_hashes", "restart_prefix_hashes"):
            self.assertEqual(projected, case["inputs"][field])
        changed = native_quote(self.day, row=12, at=events[-1].clocks.event_at, midpoint=73000)
        altered, earlier, _ = prefix_run(self.root / "future-altered", self.day, (*events[:-1], changed))
        self.assertEqual(observations, earlier)
        self.assertTrue(compare_e0_prefixes(full, deleted, altered).passed)

    def test_e0_int_11_f02_actual_first_source_fault_and_complete_fee_replay(self):
        case = literal("E0-INT-11-F02")
        interventions = case["inputs"]["fault_interventions"]
        t = interventions[0]["at"]
        events = (native_quote(self.day, row=19, at=t-60*NS, midpoint=72000),
                  native_quote(self.day, row=20, at=t, midpoint=72004),
                  native_quote(self.day, row=21, at=t+60*NS, midpoint=72004),
                  native_quote(self.day, row=22, at=t+60*NS, midpoint=72005),
                  native_quote(self.day, row=23, at=t+120*NS, midpoint=71980),
                  native_quote(self.day, row=24, at=t+16*60*NS, midpoint=71980))
        baseline = source_path(self.day, events)
        population = build_e0_decision_population(frozen_context=self.day.context,
            completed_cuts=(t-60*NS, t), sampled_midpoints={t-60*NS: 72000, t: 72000})
        projection = ["cand-a-long", "cand-a-short", "cand-b-long", "cand-b-short", "cand-c-long", "cand-c-short", "background-0932"]
        self.assertEqual(digest(projection), case["inputs"]["candidate_population_hash"])
        gap_event = native_quote(self.day, row=20, at=t, midpoint=72004, flags=interventions[0]["flags"])
        gap = source_path(self.day, (events[0], gap_event, *events[2:]))
        self.assertFalse(next(quote for quote in gap.quotes if quote.id == gap_event.id).book_valid)
        rows = [attribute_e0_fault(fault_id=interventions[0]["id"], baseline_path=baseline, changed_path=gap,
            baseline_fees=self.day.operational.fees, changed_fees=self.day.operational.fees,
            baseline_population=population, changed_population=population)]
        unknown = []
        for event in events:
            if event.clocks.event_at == interventions[1]["at"]:
                fields = decode_fields(event.raw_fields); fields["sequence"] = None
                event = normalize_mbp(fields, event.address, native=True,
                    scenario=LatencyScenario("INT11-known-after-250ms", "event", 250_000_000, 0))
            unknown.append(event)
        ambiguous = source_path(self.day, unknown)
        rows.append(attribute_e0_fault(fault_id=interventions[1]["id"], baseline_path=baseline, changed_path=ambiguous,
            baseline_fees=self.day.operational.fees, changed_fees=self.day.operational.fees,
            baseline_population=population, changed_population=population))
        fees = self.day.operational.fees
        high_fees = replace(fees, id=interventions[2]["fee_version"], per_side=(("NQ", Decimal("10.03")), ("ES", Decimal("10.03"))))
        plan = BracketPlan("INT11-cost-plan", self.day.context.instrument, -1, t+NS, 72002, 72012, 71992,
            t+901*NS, t+16*60*NS, t+17*60*NS, Decimal(20), digest("INT11-ten-tick-cost-plan"))
        def replay(schedule):
            scenario = FillScenario("INT11-fixed-native-route", 1, "venue_first", "strict_trade_through",
                                    baseline.coverage_version, schedule.version)
            return reference_bracket(baseline, plan, terms=self.day.operational.terms, fees=schedule,
                                     fill_scenario=scenario, timing=SCENARIOS[0].timing)
        original, expensive = replay(fees), replay(high_fees)
        self.assertTrue(original.observation_complete)
        self.assertTrue(expensive.observation_complete)
        self.assertEqual(original.gross_usd, expensive.gross_usd)
        self.assertEqual(original.net_usd - expensive.net_usd, Decimal(10))
        rows.append(attribute_e0_fault(fault_id=interventions[2]["id"], baseline_path=baseline, changed_path=baseline,
            baseline_fees=fees, changed_fees=high_fees, baseline_population=population, changed_population=population,
            baseline_outcomes=(original,), changed_outcomes=(expensive,)))
        aliases = {gap_event.id: "mbp-20", "/".join(event.id for event in unknown if event.clocks.event_at == t+60*NS): "q-a/q-b"}
        actual = [{key: aliases.get(row[key], row[key]) if key == "first_event" else row[key]
                   for key in ("fault_id", "first_component", "first_event", "candidate_count_delta", "economic_effect")}
                  for row in rows]
        self.assertEqual(actual, case["expected"]["attribution"])
        self.assertTrue(all(row["untraded_rows_preserved"] for row in rows))
        with self.assertRaisesRegex(ContractError, "no source or cost change"):
            attribute_e0_fault(fault_id="no-op", baseline_path=baseline, changed_path=baseline,
                baseline_fees=fees, changed_fees=fees, baseline_population=population, changed_population=population)
        with self.assertRaisesRegex(ContractError, "both complete execution replays"):
            attribute_e0_fault(fault_id="unreplayed-cost", baseline_path=baseline, changed_path=baseline,
                baseline_fees=fees, changed_fees=high_fees, baseline_population=population, changed_population=population)

    def test_e0_int_11_f03_actual_four_day_account_gates_and_all_frozen_verdicts(self):
        from tests.e0_report_fixtures import build_quality_account
        case = literal("E0-INT-11-F03")
        fixtures = {value: build_quality_account(self.root / ("account-" + str(value)), mean=value) for value in (2300, 25)}
        expected_by_id = {row["id"]: row["expected"] for row in case["variants"]}
        for variant in case["inputs"]["variants"]:
            fixture = fixtures[2300 if variant["mean_net_usd"] in (None, "2300.00") else 25]
            account = fixture["accounting"].report()
            self.assertEqual(account["eligible_day_count"], case["inputs"]["complete_gate_inputs"]["eligible_day_count"])
            self.assertEqual([{"date": day, "status": row["status"]} for day, row in account["days"].items()],
                             case["inputs"]["complete_gate_inputs"]["day_statuses"])
            self.assertEqual(sum(day["fills"] for day in account["days"].values()), 500)
            self.assertEqual(len(fixture["outcomes"]), 250)
            full = quality_components(fixture)
            # Reopen both durable ports, checking their original contracts.
            reopened_orders = OrderLedger(fixture["orders"].journal.path, account_id=fixture["orders"].account_id)
            reopened_account = AccountingLedger(fixture["accounting"].journal.path,
                account_id=fixture["accounting"].account_id, eligible_dates=fixture["accounting"].dates,
                eligibility_version=fixture["accounting"].journal.read()[0]["payload"]["eligibility_version"],
                terms=tuple(fixture["accounting"].terms.items()), fees=fixture["fees"])
            restarted = quality_components({**fixture, "orders": reopened_orders, "accounting": reopened_account})
            self.assertEqual(canonical_json(full), canonical_json(restarted))
            changed = full
            if variant["parity"] == "fail":
                # An actual modified native source record creates the one
                # critical defect, with profitable cash left fully retained.
                changed = {**full, "source": {"fault": native_quote(self.day, row=20,
                    at=self.day.cuts[1], midpoint=72004, flags=4)}}
            parity = compare_e0_prefixes(full, changed, restarted)
            interval_values = variant["net_interval_usd"]
            interval = EconomicInterval(fixture["population_hash"],
                None if interval_values is None else Fraction(interval_values[0]),
                None if interval_values is None else Fraction(interval_values[1]),
                "frozen synthetic classification interval", digest((case["case_id"], variant)))
            predictive = QualityEvidence("prediction", "supported" if variant["predictive"] == "pass" else "inconclusive",
                (digest(fixture["outcomes"]),), "frozen synthetic oracle classification control; no market predictive claim")
            fees = fixture["fees"]
            if variant["id"] == "missing-fee-no-go":
                with self.assertRaises(DependencyUnavailable):
                    replace(fees, id=variant["fee_schedule"]["id"], included=frozenset(variant["fee_schedule"]["included"]))
                fees = None
            report = e0_quality_report(accounting=fixture["accounting"], orders=fixture["orders"], fees=fees,
                paths=fixture["paths"], outcomes=fixture["outcomes"], populations=fixture["populations"], parity=parity,
                interval=interval, prediction_evidence=predictive, execution_evidence=fixture["execution_evidence"])
            with self.subTest(variant=variant["id"]):
                for key, value in expected_by_id[variant["id"]].items():
                    self.assertEqual(report[key], Fraction(value) if key == "objective_gap_usd_per_day" and value is not None else value)
                self.assertFalse(report["program_complete"])
                self.assertEqual(report["mean_net_usd"], None if variant["mean_net_usd"] is None else Fraction(variant["mean_net_usd"]))
                if fees is None:
                    self.assertIsNone(report["quality_tracks"]["objective_mean_per_day"])
        with self.assertRaises(ContractError):
            E0Parity("x", "x", "x", None, (), (b"{}", b"{}", b"{}"))
        fixture = fixtures[2300]
        unrelated = OrderLedger(self.root / "unrelated-orders.sqlite", account_id=fixture["orders"].account_id)
        unrelated.reconcile(id="unrelated-flat", known_at=self.day.cuts[0], positions={}, open_order_ids=(),
            open_orders_complete=True, execution_history_complete=True, evidence_version="unrelated-synthetic-broker-truth")
        state = quality_components(fixture, orders=unrelated)
        result = e0_quality_report(accounting=fixture["accounting"], orders=unrelated, fees=fixture["fees"],
            paths=fixture["paths"], outcomes=fixture["outcomes"], populations=fixture["populations"],
            parity=compare_e0_prefixes(state, state, state), interval=EconomicInterval(fixture["population_hash"],
                Fraction(2100), Fraction(2500), "literal", digest(case)), prediction_evidence=QualityEvidence(
                    "prediction", "supported", (digest(case),), "synthetic control"), execution_evidence=fixture["execution_evidence"])
        self.assertEqual((result["decision"], result["owner"]), ("no_go", "economic_data"))
        evidence = fixture["execution_evidence"][0]
        with self.assertRaises(ContractError):
            replace(evidence, outcome=replace(evidence.outcome, entry=replace(evidence.outcome.entry,
                                                                            price_ticks=evidence.outcome.entry.price_ticks - 1000)))


if __name__ == "__main__":
    unittest.main()
