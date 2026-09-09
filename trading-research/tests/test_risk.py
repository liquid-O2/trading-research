from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import Decimal, localcontext
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.execution.costs import FeeSchedule, load_fee_scenarios
from trading_research.foundations.units import NQ_REFERENCE, Ticks
from trading_research.operations.journal import Journal
from trading_research.risk.budget import Exposure, risk_verdict
from trading_research.risk.reservations import AtomicEntryGate, CriticalSnapshot, EntryIntent


def fee_schedule():
    return FeeSchedule("fixture", "simulated", "synthetic test account", "USD", (("NQ", Decimal("2.88")),),
                       ("https://example.test/synthetic-fixture",), "2026-09-06", "fixture-not-market-evidence",
                       "published_benchmark_not_historical_account_cost",
                       frozenset({"exchange", "regulatory", "clearing", "commission", "routing"}))


def snapshot(**kwargs):
    value = CriticalSnapshot("one-account", "2025-01-02", "NQH5", NQ_REFERENCE, 10, 10, 10, 10, "observed-broker-and-feed-v1",
                             Ticks(10000), Ticks(10001), 0, (), Decimal(0), Decimal(1000), None,
                             "synthetic-day-start-only", 100, True, True)
    return replace(value, **kwargs)


def intent(state, *, id="entry-1", stop=9901, worst_entry=10001, **kwargs):
    value = EntryIntent(id, state.account_id, state.instrument, 1, Ticks(stop), Ticks(worst_entry), 10, 90, 95,
                        state.version, f"decision:{id}", fee_schedule().version, Decimal(20))
    return replace(value, **kwargs)


class BudgetTests(unittest.TestCase):
    def test_marked_loss_is_not_counted_twice_and_entry_fee_is_not_charged_again(self):
        # Entry 10000, bid mark 9990, stop 9900: -50 open, -2.88 fee
        # already in N; only 90 additional ticks plus the exit fee remain.
        exposure = Exposure("NQH5", NQ_REFERENCE, 1, Ticks(9990), Ticks(9900), Decimal("2.88"), Decimal(20))
        result = risk_verdict(daily_budget=Decimal(1000), trading_net_liquidation_pnl=Decimal("-52.88"),
                              firm_headroom=Decimal(900), mutually_possible_exposures=(exposure,), rule_version="test", state_known=True)
        self.assertEqual(result.daily_headroom, Decimal("947.12"))
        self.assertEqual(result.incremental_reserve, Decimal("472.88"))
        self.assertTrue(result.allowed)

    def test_profitable_day_giveback_uses_day_start_and_stricter_firm_floor(self):
        e = Exposure("NQH5", NQ_REFERENCE, 1, Ticks(10000), Ticks(9780), Decimal("2.88"), Decimal(0))
        with localcontext() as c:
            c.prec = 3
            args = dict(daily_budget=Decimal(1000), trading_net_liquidation_pnl=Decimal(500),
                        firm_headroom=None, mutually_possible_exposures=(e,), rule_version="test", state_known=True)
            result = risk_verdict(**args)
            self.assertEqual((result.daily_headroom, result.incremental_reserve), (Decimal(1500), Decimal("1102.88")))
            self.assertTrue(result.allowed)
            self.assertFalse(risk_verdict(**{**args, "firm_headroom":Decimal(1000)}).allowed)
            self.assertTrue(risk_verdict(**{**args, "trading_net_liquidation_pnl":Decimal(-1000)}).halt)

    def test_fees_equality_unknown_and_gap_beyond_stop(self):
        e = Exposure("NQH5", NQ_REFERENCE, 1, Ticks(9900), Ticks(9901), Decimal("2.88"), Decimal(20))
        self.assertEqual(e.incremental_reserve, Decimal("22.88"))
        args = dict(daily_budget=Decimal(1000), trading_net_liquidation_pnl=Decimal("-977.12"),
                    firm_headroom=None, mutually_possible_exposures=(e,), rule_version="test", state_known=True)
        self.assertTrue(risk_verdict(**args).allowed)
        self.assertFalse(risk_verdict(**{**args, "trading_net_liquidation_pnl":Decimal("-977.13")}).allowed)
        self.assertTrue(risk_verdict(**{**args, "state_known":False}).halt)
        with self.assertRaises(ContractError):
            risk_verdict(**{**args, "daily_budget":Decimal(1001)})

    def test_published_fee_scenarios_are_positive_complete_and_separate_versions(self):
        scenarios = load_fee_scenarios(Path(__file__).parents[1] / "configs/fee-scenarios.json")
        self.assertEqual({s.connection for s in scenarios}, {"Tradovate", "Rithmic"})
        self.assertEqual(len({s.version for s in scenarios}), 2)
        for s in scenarios:
            self.assertEqual(s.fee("NQ", sides=2), Decimal("5.76"))
            self.assertEqual(s.fee("ES", sides=1), Decimal("2.88"))
        with self.assertRaises(ContractError):
            replace(scenarios[0], per_side=(("NQ", Decimal(0)),))


class AtomicGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.journal = Journal(Path(self.temp.name) / "risk.sqlite")
        self.gate = self.new_gate()
        self.state = snapshot()
        self.gate.observe(self.state)

    def new_gate(self):
        return AtomicEntryGate(self.journal, account_id="one-account", fee_schedule=fee_schedule(),
                               quote_ttl_ns=30, broker_ttl_ns=40, feed_ttl_ns=20)

    def test_concurrent_one_mini_reservations_and_dispatch_have_one_winner(self):
        requests = [intent(self.state, id=f"entry-{i}") for i in range(8)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: self.new_gate().reserve(i, at=12), requests))
        self.assertEqual(sum(r.approved for r in results), 1)
        winning = requests[next(i for i, r in enumerate(results) if r.approved)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            wire = list(pool.map(lambda _: self.new_gate().dispatch(winning, at=13), range(8)))
        self.assertEqual(sum(w is not None for w in wire), 1)
        self.assertEqual(next(w for w in wire if w).quantity, 1)
        self.assertIsNone(self.new_gate().dispatch(winning, at=14))

    def test_unknown_and_cancel_request_survive_restart_until_confirmed_truth(self):
        first = intent(self.state)
        self.assertTrue(self.gate.reserve(first, at=11).approved)
        self.assertIsNotNone(self.gate.dispatch(first, at=12))
        self.gate.broker_state(first.id, event_id="timeout", state="unknown", evidence_id="ack-timeout-observed", at=13)
        self.assertFalse(self.new_gate().reserve(intent(self.state, id="entry-2"), at=14).approved)
        self.gate.broker_state(first.id, event_id="cancel-request", state="cancel_requested", evidence_id="cancel-wire", at=15)
        with self.assertRaises(ContractError):
            self.gate.broker_state(first.id, event_id="not-confirmed", state="cancelled", evidence_id="timeout", at=16)
        new_state = replace(self.state, at=17, broker_observed_at=17, source_version="broker-full-reconciliation")
        self.gate.broker_state(first.id, event_id="cancel-confirmed", state="cancelled", evidence_id="broker-order-history-and-position", at=17, snapshot=new_state)
        self.assertTrue(self.new_gate().reserve(intent(new_state, id="entry-3"), at=18).approved)

    def test_changed_quote_same_value_and_boundary_invalidate_before_dispatch(self):
        first = intent(self.state)
        self.assertTrue(self.gate.reserve(first, at=11).approved)
        changed = replace(self.state, at=12, quote_observed_at=12, source_version="new-source-receipt-same-price")
        self.gate.observe(changed)
        self.assertIsNone(self.gate.dispatch(first, at=13))
        second = intent(changed, id="second", expires_at=99, horizon_end=101)
        self.assertTrue(self.gate.reserve(second, at=14).approved)
        self.assertIsNone(self.gate.dispatch(second, at=100))
        self.assertEqual(sum(e["kind"] == "entry_dispatched" for e in self.journal.read()), 0)

    def test_fill_before_ack_cannot_release_flat_action_state_or_reset_day(self):
        first = intent(self.state)
        self.gate.reserve(first, at=11)
        self.gate.dispatch(first, at=12)
        with self.assertRaises(ContractError):
            self.gate.broker_state(first.id, event_id="bad-flat-fill", state="filled", evidence_id="partial-message", at=13, snapshot=self.state)
        filled = replace(self.state, at=14, broker_observed_at=14, position=1, trading_net_pnl=Decimal("-7.88"), source_version="fill-reconciled")
        self.gate.broker_state(first.id, event_id="fill-1", state="filled", evidence_id="broker-fill-id", at=14, snapshot=filled)
        self.gate.broker_state(first.id, event_id="fill-1", state="filled", evidence_id="broker-fill-id", at=14, snapshot=filled)
        self.assertFalse(self.gate.reserve(intent(filled, id="add"), at=15).approved)
        with self.assertRaises(ContractError):
            self.gate.observe(replace(filled, trading_date="2025-01-03", at=100))

    def test_actual_input_versions_price_bound_fees_and_freshness_are_required(self):
        cases = [intent(self.state, id="wrong-fees", fee_version="zero-fee"),
                 intent(self.state, id="price-moved", worst_entry=10000),
                 intent(self.state, id="stale-vector", critical_version="earlier-state")]
        for value in cases:
            self.assertFalse(self.gate.reserve(value, at=12).approved)
        good = intent(self.state, id="good")
        self.assertTrue(self.gate.reserve(good, at=12).approved)
        with self.assertRaises(IntegrityError):
            self.gate.reserve(replace(good, stop=Ticks(9900)), at=12)
        self.assertIsNone(self.gate.dispatch(good,at=31))
        self.assertFalse(self.gate.reserve(intent(self.state, id="stale-source"), at=31).approved)


if __name__ == "__main__":
    unittest.main()
