"""Finite native replay accounts for the exact four-date INT11F03 arithmetic.

Every reported dollar comes from a public reference_bracket result and real
order/account ledger ports. There are 250 sequential one-mini round trips;
no favorable prices, gate booleans or fee overrides are injected into outcomes.
"""
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from trading_research.data.events import LatencyScenario
from trading_research.execution.accounting import AccountingLedger
from trading_research.execution.orders import OrderLedger
from trading_research.execution.replay import BracketPlan, reference_bracket
from trading_research.execution.venue import FillScenario
from trading_research.experiments.e0.account_bridge import E0OutcomeReplay
from trading_research.experiments.e0.admission import bind_e0_day_operational_terms
from trading_research.experiments.e0.observations import build_e0_decision_population
from trading_research.experiments.e0.reporting import E0ExecutionEvidence, E0NativeExecutionSource
from trading_research.experiments.e0.runner import SCENARIOS
from trading_research.experiments.e0.source_bridge import NativeCoverageReceipt, venue_path_from_mbp
from trading_research.foundations.cash_calendar import VenueBoundary
from trading_research.operations.artifacts import digest
from tests.e0_source_fixtures import _build_day, _native_event

NS = 1_000_000_000
MINUTE = 60 * NS


def _publish_schedule(events, orders, accounting):
    """Apply the public scheduler's immutable events via the public ledger ports.

    Reading pending_events once avoids its per-event idempotency rescan and
    repeated full receipt reports. Each durable port still performs all of its
    own identity, chronology, position, authorization and journal checks.
    """
    for event in events:
        if event.journal == "order":
            orders.submit(event.payload)
        elif event.journal == "broker":
            orders.observe(event.payload)
        elif event.journal == "fill":
            accounting.fill(event.payload)
        elif event.journal == "reconcile":
            orders.reconcile(**event.payload)
        elif event.journal == "day":
            day, at, status, evidence = event.payload
            accounting.day_status(trading_date=day, at=at, status=status, evidence_version=evidence)
        else:
            raise ValueError("unregistered public replay event")


def build_quality_account(root, mean=2300):
    """Return genuine four-date account/source/plan evidence for mean2300 or25.

    Returns a dictionary containing accounting, orders, fees, paths, plans,
    outcomes, populations, execution_evidence, operational and native_events.
    250 trades incur exactly2515USD of fees. The two gross tick totals2343/523
    yield exactly9200/100USD net over four eligible days.
    """
    if type(mean) is not int or mean not in (2300, 25):
        raise ValueError("only the two frozen INT11F03 account means are registered")
    root = Path(root)
    days = tuple(date(2024, 6, 3) + timedelta(days=i) for i in range(4))
    source_days = tuple(_build_day(day, quote_path="comparator_quiet") for day in days)
    first = source_days[0]
    terms, fees = first.operational.terms, first.operational.fees
    # The report control uses the normal published cash day, with an explicit
    # four-minute venue flat margin and one-minute local routing safety buffer.
    cash = first.published_cash_day
    boundary = VenueBoundary(days[0], terms.root, cash.open_at, cash.close_at,
        cash.close_at - 4*MINUTE, cash.known_at, "INT11-normal-session-flat-margin-v1",
        "verified_venue_schedule")
    operational = bind_e0_day_operational_terms(day=days[0], cash_day=cash, venue_boundary=boundary,
        selected_terms=terms, fee_schedule=fees,
        source_coverage={"checks": {name: {"state": "satisfied", "evidence": "INT11-retained-native-path"}
            for name in ("mbp_full_schema", "book_recovery", "entry_and_label_window")},
            "source_versions": ("INT11-250-minute-native-source-v1",)},
        period_policy={"scope": "E0_historical_2022_2025_harness"}, safety_buffer_ns=MINUTE,
        cut=first.base_cut, require_verified_venue=True)
    cuts = tuple(first.base_cut + i*MINUTE for i in range(250))
    # Alternation resets the prior object's consumed visit:8ticks between
    # EQ72004 and prior-high72012 exceeds the5tick reset outside each1tick band.
    centers = tuple(72004 if i % 2 == 0 else 72012 for i in range(250))
    profit_ticks = tuple((10 if i < 93 else 9) if mean == 2300 else (3 if i < 23 else 2)
                         for i in range(250))
    raw_rows = [(cuts[0]-62*NS, 71999, 72001)]
    for cut, center, profit in zip(cuts, centers, profit_ticks):
        raw_rows.append((cut-2*NS, center-1, center+1))
        # Actual entry ask+impact is center+2. A long target quote bid at
        # center+profit+3 exits at that bid-impact, hence exactlyprofit ticks.
        target_bid = center + profit + 3
        raw_rows.append((cut+5*NS, target_bid, target_bid+2))
    raw_rows.append((cash.close_at, raw_rows[-1][1], raw_rows[-1][2]))
    native_events = tuple(_native_event(day=days[0], row=i+100, sequence=i+100,
        event_at=at, action="A", bid_ticks=bid, ask_ticks=ask, size=1, side="N", flags=128)
        for i, (at,bid,ask) in enumerate(raw_rows))
    coverage = NativeCoverageReceipt.from_events(native_events,
        source_id=native_events[0].address.dataset_id,
        schema_version=native_events[0].address.schema_version, instrument_id=first.context.instrument,
        complete_intervals=((cuts[0]-120*NS, cash.close_at+NS),),
        coverage_version=digest(("INT11-continuous-native-coverage-v1", tuple(event.id for event in native_events))))
    scenario = SCENARIOS[0]
    path = venue_path_from_mbp(canonical_events=native_events, selected_instrument=first.context.selected_day,
        coverage=coverage, latency_scenario=LatencyScenario(scenario.id, "event", 250_000_000, 0),
        tick_size=terms.tick_size, market_state="continuous")
    native_source = E0NativeExecutionSource(native_events, first.context.selected_day, coverage,
        LatencyScenario(scenario.id, "event", 250_000_000, 0), terms.tick_size)
    population_cuts = (cuts[0]-MINUTE, *cuts)
    midpoints = {}
    for cut in population_cuts:
        quote, reason = path.quote_at(cut, clock="strategy")
        if quote is None:
            raise ValueError(reason)
        midpoints[cut] = Fraction(quote.bid + quote.ask, 2)
    populations = [build_e0_decision_population(frozen_context=first.context,
        completed_cuts=population_cuts, sampled_midpoints=midpoints, policy_id="INT11-four-date-account-population-v1")]
    paths = [path]
    for source in source_days[1:]:
        other = venue_path_from_mbp(canonical_events=source.canonical_events,
            selected_instrument=source.context.selected_day, coverage=source.coverage,
            latency_scenario=LatencyScenario(scenario.id, "event", 250_000_000, 0),
            tick_size=source.operational.terms.tick_size, market_state="continuous")
        other_midpoints = {}
        for cut in source.cuts:
            quote, _ = other.quote_at(cut, clock="strategy")
            other_midpoints[cut] = None if quote is None else Fraction(quote.bid+quote.ask, 2)
        populations.append(build_e0_decision_population(frozen_context=source.context,
            completed_cuts=source.cuts, sampled_midpoints=other_midpoints,
            policy_id="INT11-four-date-account-population-v1"))
        paths.append(other)
    account_id = "synthetic-account-1"
    population_version = digest(tuple(pop.population_hash for pop in populations))
    accounting = AccountingLedger(root/"account.sqlite", account_id=account_id,
        eligible_dates=tuple(day.isoformat() for day in days), eligibility_version=population_version,
        terms=((path.instrument, terms),), fees=fees)
    orders = OrderLedger(root/"orders.sqlite", account_id=account_id)
    orders.reconcile(id="INT11-initial-flat", known_at=population_cuts[0], positions={}, open_order_ids=(),
        open_orders_complete=True, execution_history_complete=True, evidence_version=path.version)
    fill_scenario = FillScenario("INT11-baseline", 1, "venue_first", "strict_trade_through",
                                 path.coverage_version, fees.version)
    plans, outcomes, execution_evidence = [], [], []
    prior_net = Decimal(0)
    with orders.journal.transaction(maximum_new_events=4096), accounting.journal.transaction(maximum_new_events=1024):
        for i, (cut, center, profit) in enumerate(zip(cuts, centers, profit_ticks)):
            object_type = "06_09:eq" if i % 2 == 0 else "prior_rth:high"
            object_id = next(obj.id for obj in first.context.objects if obj.type == object_type)
            row = next(row for row in populations[0].by_cut(cut).rows if row.object_id == object_id and row.side == 1)
            if row.contact is None or row.contact.approach is None:
                raise ValueError("INT11 minute is not a fresh first-inward contact")
            entry = center+2
            plan = BracketPlan(f"INT11-{mean}-roundtrip-{i:03d}", path.instrument, 1, cut, entry,
                entry-10, entry+profit+1, cut+900*NS, operational.window["flatten_send_at"],
                operational.window["required_flat_at"], Decimal(20),
                digest(("INT11-fixed-ten-tick-stop", row.decision_set_id, row.id, profit+1)))
            outcome = reference_bracket(path, plan, terms=terms, fees=fees, fill_scenario=fill_scenario,
                timing=scenario.timing, prior_day_net=prior_net, daily_budget=Decimal(1000))
            if (not outcome.observation_complete or outcome.exit_reason != "target"
                    or outcome.position_known_flat_at is None or outcome.position_known_flat_at >= cut+MINUTE):
                raise ValueError("INT11 complete target replay failed its sequential-minute contract")
            proof = E0ExecutionEvidence(days[0].isoformat(), populations[0].population_hash, row,
                path, plan, terms, fees, fill_scenario, scenario.timing, outcome, prior_net,
                native_source=native_source)
            manifest = {"instrument": path.instrument, "trading_date": days[0].isoformat(),
                "source_version": path.version, "fee_version": fees.version, "coverage_version": path.coverage_version,
                "account_id": account_id, "plan_id": plan.id, "stop_ticks": plan.stop_ticks,
                "required_flat_at": plan.required_flat_at, "evidence_version": proof.version}
            replay = E0OutcomeReplay(outcome=outcome, order_ledger=orders, accounting=accounting,
                scenario_manifest=manifest, timing=scenario.timing, venue_path=path,
                fill_scenario=fill_scenario, finalize_day=False)
            _publish_schedule(replay.pending_events, orders, accounting)
            plans.append(plan); outcomes.append(outcome); execution_evidence.append(proof)
            prior_net += outcome.net_usd
        for day, status in zip(days, ("complete", "flat", "outage", "halted")):
            source = source_days[(day-days[0]).days]
            at = source.published_cash_day.close_at
            orders.reconcile(id="INT11-boundary-flat:"+day.isoformat(), known_at=at, positions={}, open_order_ids=(),
                open_orders_complete=True, execution_history_complete=True,
                evidence_version=digest((source.context.version, status)))
            accounting.day_status(trading_date=day.isoformat(), at=at, status=status,
                                  evidence_version=digest((source.context.version, status)))
    return {"accounting": accounting, "orders": orders, "fees": fees, "paths": tuple(paths),
        "plans": tuple(plans), "outcomes": tuple(outcomes), "populations": tuple(populations),
        "execution_evidence": tuple(execution_evidence), "operational": operational,
        "native_events": native_events, "source_days": source_days,
        "population_hash": population_version, "registered_roundtrips": 250,
        "registered_gross_ticks": 2343 if mean == 2300 else 523}


def check_history_import(test, root):
    """Bounded public-port assertions for INT10F03's historical import control."""
    from trading_research.errors import ContractError, IntegrityError
    from trading_research.execution.orders import OrderSpec, BrokerEvent
    from trading_research.execution.orders_reference import reduce_order_history
    from trading_research.operations.artifacts import canonical_json
    from trading_research.operations.journal import Journal

    root = Path(root)
    journal = Journal(root/"bounded-journal.sqlite")
    seed_payload = {"nested": {"values": [1, 2]}}
    seed, created = journal.append(key="seed", kind="control", payload=seed_payload)
    test.assertTrue(created)
    with journal.transaction(maximum_new_events=2):
        snapshot = journal.read()
        original = canonical_json(snapshot)
        # Both ordinary mutation and base-container bypasses must fail; the
        # public snapshot may not alias mutable verified cache contents.
        with test.assertRaises((TypeError, AttributeError, ContractError)):
            snapshot[0]["payload"]["nested"]["values"].append(3)
        with test.assertRaises((TypeError, ContractError)):
            dict.__setitem__(snapshot[0]["payload"]["nested"], "injected", True)
        with test.assertRaises((TypeError, ContractError)):
            list.append(snapshot[0]["payload"]["nested"]["values"], 3)
        test.assertEqual(canonical_json(journal.read()), original)
        first, created = journal.append(key="first", kind="control", payload={"value": 1},
                                        expected_head=seed, check_head=True)
        test.assertTrue(created)
        test.assertEqual(len(snapshot), 1)
        test.assertEqual(journal.append(key="first", kind="control", payload={"value": 1}), (first, False))
        with test.assertRaisesRegex(IntegrityError, "idempotency key reused"):
            journal.append(key="first", kind="control", payload={"value": 999})
        with test.assertRaisesRegex(ContractError, "critical state changed"):
            journal.append(key="stale", kind="control", payload={}, expected_head=seed, check_head=True)
        with test.assertRaisesRegex(ContractError, "nonnested"):
            with journal.transaction(maximum_new_events=1):
                pass
        journal.append(key="second", kind="control", payload={"value": 2}, expected_head=first, check_head=True)
        with test.assertRaisesRegex(ContractError, "event budget exhausted"):
            journal.append(key="over-budget", kind="control", payload={})
        # Idempotent replay is legal even when no new-event slots remain.
        test.assertEqual(journal.append(key="first", kind="control", payload={"value": 1}), (first, False))
        committed_wire = canonical_json(journal.read())
    test.assertEqual(canonical_json(Journal(journal.path).read()), committed_wire)
    with test.assertRaisesRegex(RuntimeError, "intentional import abort"):
        with journal.transaction(maximum_new_events=2):
            journal.append(key="rolled-back", kind="control", payload={"value": 3})
            raise RuntimeError("intentional import abort")
    test.assertEqual(canonical_json(journal.read()), committed_wire)
    test.assertEqual(canonical_json(Journal(journal.path).read()), committed_wire)
    with journal.transaction(maximum_new_events=1):
        _, created = journal.append(key="rolled-back", kind="control", payload={"value": 3})
        test.assertTrue(created)

    left, right = Journal(root/"paired-left.sqlite"), Journal(root/"paired-right.sqlite")
    with test.assertRaisesRegex(RuntimeError, "abort both active journals"):
        with left.transaction(maximum_new_events=1), right.transaction(maximum_new_events=1):
            left.append(key="tentative-left", kind="control", payload={})
            right.append(key="tentative-right", kind="control", payload={})
            raise RuntimeError("abort both active journals")
    test.assertEqual(left.read(), ())
    test.assertEqual(right.read(), ())

    at = 1_700_000_000_000_000_000
    account = "history-import-account"
    imported = OrderLedger(root/"import-orders.sqlite", account_id=account)
    sequential = OrderLedger(root/"sequential-orders.sqlite", account_id=account)
    def order(identity, side, role, offset, *, price=None, parent=None):
        return OrderSpec(identity, account, "1002", side, 1, role,
            "stop_market" if role == "protective_stop" else "market", price,
            at+offset, at+100, "history-import-authorization", parent_id=parent)
    def broker(identity, client, kind, offset, *, execution=None, quantity=0, price=None):
        return BrokerEvent(identity, client, kind, at+offset, at+offset, "retained-history-control",
                           execution, quantity, price)
    operations = (
        ("reconcile", {"id": "initial", "known_at": at, "positions": {}, "open_order_ids": (),
                       "open_orders_complete": True, "execution_history_complete": True,
                       "evidence_version": "initial-actual-flat"}),
        ("submit", order("entry", 1, "entry", 1)),
        ("submit", order("stop", -1, "protective_stop", 2, price=90, parent="entry")),
        ("observe", broker("entry-ack", "entry", "acknowledged", 3)),
        ("observe", broker("entry-fill", "entry", "fill", 4, execution="entry-x", quantity=1, price=100)),
        ("observe", broker("stop-working", "stop", "working", 5)),
        ("reconcile", {"id": "protected", "known_at": at+6, "positions": {"1002": 1}, "open_order_ids": ("stop",),
                       "open_orders_complete": True, "execution_history_complete": True,
                       "evidence_version": "actual-entry-and-stop"}),
        ("observe", broker("stop-cancel-request", "stop", "cancel_requested", 8)),
        ("observe", broker("stop-cancelled", "stop", "cancelled", 9)),
        ("submit", order("exit", -1, "full_exit", 10, parent="entry")),
        ("observe", broker("exit-ack", "exit", "acknowledged", 11)),
        ("observe", broker("exit-overfill", "exit", "fill", 12, execution="exit-x", quantity=2, price=105)),
        ("reconcile", {"id": "actual-overfill", "known_at": at+13, "positions": {"1002": -1}, "open_order_ids": (),
                       "open_orders_complete": True, "execution_history_complete": True,
                       "evidence_version": "actual-reversed-mini"}),
        ("submit", order("corrective-exit", 1, "full_exit", 14)),
        ("observe", broker("corrective-fill", "corrective-exit", "fill", 15,
                           execution="corrective-x", quantity=1, price=105)),
        ("reconcile", {"id": "final", "known_at": at+16, "positions": {}, "open_order_ids": (),
                       "open_orders_complete": True, "execution_history_complete": True,
                       "evidence_version": "actual-final-flat-with-retained-incident"}),
    )
    def apply(ledger, operation):
        method, payload = operation
        if method == "reconcile":
            ledger.reconcile(**payload)
        else:
            getattr(ledger, method)(payload)
    with imported.journal.transaction(maximum_new_events=32):
        for index, operation in enumerate(operations):
            apply(imported, operation); apply(sequential, operation)
            test.assertEqual(canonical_json(imported.state()), canonical_json(sequential.state()))
            test.assertEqual(canonical_json(imported.state()),
                             canonical_json(reduce_order_history(imported.journal.read())))
            if index == 6:
                expected = canonical_json(imported.state())
                view = imported.state()
                view["orders"]["entry"]["filled"] = 999
                view["executions"]["entry-x"]["known_at"] = 0
                view["positions"]["1002"] = 99
                view["incidents"].append({"kind": "invented"})
                test.assertEqual(canonical_json(imported.state()), expected)
                with test.assertRaises((TypeError, ContractError)):
                    dict.__setitem__(imported.state()["broker_truth"], "positions", {})
                before = canonical_json(imported.journal.read())
                conflict = BrokerEvent("conflicting-execution", "entry", "fill", at+4, at+7,
                    "retained-conflicting-broker-evidence", "entry-x", 1, 101)
                with test.assertRaisesRegex(IntegrityError, "execution identity reused"):
                    imported.observe(conflict)
                test.assertEqual(canonical_json(imported.journal.read()), before)
                test.assertEqual(canonical_json(imported.state()), expected)
                test.assertEqual(canonical_json(imported.state()),
                                 canonical_json(reduce_order_history(imported.journal.read())))
        during = imported.state()
        test.assertEqual(during["positions"], {"1002": 0})
        test.assertEqual(during["live_orders"], ())
        test.assertTrue(during["reconciled"])
        test.assertFalse(during["entry_allowed"])
        test.assertEqual(during["observed_unprotected_intervals"], ((at+4, at+5), (at+8, at+15)))
        test.assertEqual([item["kind"] for item in during["incidents"]], ["overfill", "exit_reversed_position"])
        during_wire = canonical_json(during)
        history_wire = canonical_json(imported.journal.read())
    test.assertEqual(canonical_json(imported.state()), during_wire)
    reopened = OrderLedger(imported.journal.path, account_id=account)
    test.assertEqual(canonical_json(reopened.state()), during_wire)
    test.assertEqual(canonical_json(reduce_order_history(reopened.journal.read())), during_wire)
    test.assertEqual(canonical_json(reopened.journal.read()), history_wire)
    test.assertEqual(canonical_json(sequential.journal.read()), history_wire)

    # A reduced tentative prefix must not survive an aborted transaction or
    # seed the next transaction's cache on this same ledger object.
    before_state = canonical_json(imported.state())
    with test.assertRaisesRegex(RuntimeError, "abort reduced prefix"):
        with imported.journal.transaction(maximum_new_events=2):
            imported.reconcile(id="rollback-reconcile", known_at=at+17, positions={}, open_order_ids=(),
                open_orders_complete=True, execution_history_complete=True, evidence_version="tentative-flat")
            imported.state()
            raise RuntimeError("abort reduced prefix")
    test.assertEqual(canonical_json(imported.state()), before_state)
    test.assertEqual(canonical_json(reduce_order_history(imported.journal.read())), before_state)
    test.assertEqual(canonical_json(imported.journal.read()), history_wire)
    with imported.journal.transaction(maximum_new_events=1):
        test.assertEqual(canonical_json(imported.state()), before_state)
        imported.reconcile(id="after-rollback", known_at=at+18, positions={}, open_order_ids=(),
            open_orders_complete=True, execution_history_complete=True, evidence_version="new-actual-flat")
        final_wire = canonical_json(imported.state())
        test.assertEqual(canonical_json(reduce_order_history(imported.journal.read())), final_wire)
    test.assertEqual(canonical_json(OrderLedger(imported.journal.path, account_id=account).state()), final_wire)
