"""Small typed E0 policy/account fixtures used by integration tests.

These are synthetic engineering values.  They are intentionally independent
of any market-data reader and carry explicit source/fit identities so a test
cannot accidentally turn a caller boolean into admission evidence.
"""

from decimal import Decimal
from pathlib import Path

from trading_research.execution.costs import FeeSchedule
from trading_research.execution.orders import OrderLedger
from trading_research.execution.accounting import AccountingLedger
from trading_research.execution.replay import BracketPlan, OrderTiming, reference_bracket
from trading_research.execution.venue import Fill, FillScenario, VenuePath, VenueQuote
from trading_research.experiments.e0.account_bridge import E0Boundary, E0BracketPolicy
from trading_research.experiments.e0.policy import (
    E0ActionValue, E0DecisionSet, E0SyntheticNumericalEvidence, TargetPolicy,
)
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.foundations.units import NQ_REFERENCE, Ticks
from trading_research.risk.reservations import CriticalSnapshot


DECISION = 1_717_421_520_000_000_000
HORIZON = 1_717_422_420_000_000_000
FLATTEN = 1_717_444_500_000_000_000
REQUIRED_FLAT = 1_717_444_800_000_000_000


def target_policy(multiple: int) -> TargetPolicy:
    return TargetPolicy(f"target_{multiple}x-v1", multiple)


def value(candidate_id: str, side: int, policy: TargetPolicy, *, positive: bool = True,
          expected_net: Decimal | None = None, complete: bool = True,
          unavailable_reason: str | None = None, model_version: str = "logit-2023-lambda-1-v1",
          target_version: str = "reach-depart-15m-v1", known_at: int = DECISION,
          decision_at: int = DECISION, decision_set_id: str = "ds-2025-0103-0932",
          intent_id: str | None = None, horizon_end: int = HORIZON,
          expiry_at: int | None = None, occupancy_end: int | None = None) -> E0ActionValue:
    if positive:
        if policy.multiple == 1:
            target, stop, target_probability, stop_probability = Decimal("39.94"), Decimal("-60.06"), Decimal("0.70"), Decimal("0.30")
        else:
            target, stop, target_probability, stop_probability = Decimal("89.94"), Decimal("-60.06"), Decimal("0.45"), Decimal("0.55")
    else:
        target = stop = expected_net if expected_net is not None else Decimal("-4.00")
        target_probability = stop_probability = Decimal("0.50")
    evidence = E0SyntheticNumericalEvidence(
        id=model_version, fitted_at=decision_at, target_version=target_version,
        fold_id="fit-2023-v1", feature_version="features-e0-v1",
        model_version=model_version, calibrator_version="cal-2024-v1",
        source_version="fixture-source-v1")
    return E0ActionValue(
        candidate_id, policy, target_probability, stop_probability,
        Decimal("0.00"), target, stop, Decimal("0"), decision_at, known_at,
        model_version, target_version, "fit-2023-v1", "features-e0-v1",
        "cal-2024-v1", "fixture-source-v1", f"object-{candidate_id}", decision_set_id,
        side, horizon_end, intent_id or f"intent-{candidate_id}-0932",
        expiry_at or horizon_end, occupancy_end=occupancy_end or horizon_end, complete=complete,
        unavailable_reason=unavailable_reason, artifact_evidence=evidence)


def decision_set(*candidate_ids: str, at: int = DECISION,
                 id: str = "ds-2025-0103-0932") -> E0DecisionSet:
    return E0DecisionSet(id, at, tuple(candidate_ids),
                         source_event_ids=("contact-fixture-v1",), source_version="fixture-source-v1")


def terms():
    return NQ_REFERENCE


def fees() -> FeeSchedule:
    return FeeSchedule(
        "fee-nq-synthetic-v1", "simulated", "synthetic one-mini account", "USD",
        (("NQ", Decimal("5.03")),), ("https://example.test/e0-fee",), "2026-09-07",
        "synthetic-e0-fee-evidence", "published_benchmark_not_historical_account_cost",
        frozenset({"exchange", "regulatory", "clearing", "commission", "routing"}))


def boundary() -> E0Boundary:
    return E0Boundary(HORIZON, FLATTEN, REQUIRED_FLAT, "boundary-e0-fixture-v1")


def bracket_policy(multiple: int = 1) -> E0BracketPolicy:
    return E0BracketPolicy(
        f"target_{multiple}x-v1", multiple, "geometry-c01-v1", range_width_ticks=100,
        impact_ticks=1, gap_reserve_usd=Decimal("20.00"), source_version="fixture-source-v1")


def critical_snapshot(*, account_id: str = "synthetic-account-1", position: int = 0,
                      state_known: bool = True, entry_eligible: bool = True,
                      at: int = DECISION, trading_net_pnl: Decimal = Decimal("0.00"),
                      broker_open_orders: tuple[str, ...] = (),
                      flatten_at: int = FLATTEN) -> CriticalSnapshot:
    return CriticalSnapshot(
        account_id, "2024-06-03", "1002", NQ_REFERENCE, at, at, at,
        at, "critical-fixture-v1", Ticks(72000), Ticks(72004), position, broker_open_orders,
        trading_net_pnl, Decimal("1000.00"), None, "fixture-risk-v1", flatten_at,
        state_known, entry_eligible)


def venue_path(*, at: int = DECISION, coverage_end: int | None = None,
               coverage_version: str = "coverage-e0-fixture-v1") -> VenuePath:
    quote = VenueQuote("q-entry", "1002", at, at, 101, 72000, 72004, 5, 7,
                       True, "continuous", "venue-fixture-v1")
    return VenuePath(instrument="1002", quotes=(quote,), trades=(),
                     complete_intervals=((at - 1_000_000_000,
                                           FLATTEN + 1_000_000_000 if coverage_end is None else coverage_end),),
                     coverage_version=coverage_version)


REPLAY_ENTRY_AT = DECISION + 250_000_000
REPLAY_TARGET_EVENT_AT = 1_717_421_639_250_000_000
REPLAY_TARGET_KNOWN_AT = 1_717_421_639_500_000_000
REPLAY_EXIT_AT = 1_717_421_640_000_000_000
REPLAY_COVERAGE_VERSION = "coverage-e0-08-v1"


def replay_path(*, coverage_intervals=None, coverage_version: str = REPLAY_COVERAGE_VERSION) -> VenuePath:
    """Actual typed four-quote path used by frozen INT-08 cases."""

    quotes = (
        VenueQuote("q-predecision", "1002", DECISION - 1_000_000_000,
                   DECISION - 750_000_000, 100, 72000, 72004, 5, 7,
                   True, "continuous", "venue-fixture-v1"),
        VenueQuote("q-entry", "1002", DECISION, DECISION + 250_000_000,
                   101, 72000, 72004, 5, 7, True, "continuous", "venue-fixture-v1"),
        VenueQuote("q-target", "1002", REPLAY_TARGET_EVENT_AT,
                   REPLAY_TARGET_KNOWN_AT, 102, 72015, 72017, 5, 7,
                   True, "continuous", "venue-fixture-v1"),
        VenueQuote("q-exit", "1002", REPLAY_EXIT_AT, REPLAY_EXIT_AT + 250_000_000,
                   103, 72013, 72017, 5, 7, True, "continuous", "venue-fixture-v1"),
    )
    intervals = ((DECISION - 100_000_000, REPLAY_EXIT_AT + 500_000_000),) if coverage_intervals is None else coverage_intervals
    return VenuePath(instrument="1002", quotes=quotes, trades=(),
                     complete_intervals=tuple(intervals), coverage_version=coverage_version)


def replay_plan(*, decision_at: int = DECISION, horizon_end: int = HORIZON,
                flatten_send_at: int = FLATTEN, required_flat_at: int = REQUIRED_FLAT) -> BracketPlan:
    return BracketPlan("plan-a", "1002", 1, decision_at, 72005, 71995, 72015,
                       horizon_end, flatten_send_at, required_flat_at,
                       Decimal("20.00"), "geometry-c01-v1")


def replay_timing(*, broker_report_ns: int = 0, cancellation_tie: str = "cancel_first") -> OrderTiming:
    return OrderTiming("timing-out250-report" + str(broker_report_ns) + "-stop0-v1",
                       250_000_000, broker_report_ns, 0, cancellation_tie)


def replay_scenario(*, impact_ticks: int = 1, coverage_version: str = REPLAY_COVERAGE_VERSION) -> FillScenario:
    return FillScenario("feed250-out250-impact" + str(impact_ticks), impact_ticks,
                        "venue_first", "strict_trade_through", coverage_version,
                        fees().version)


def replay_outcome(*, path: VenuePath | None = None, plan: BracketPlan | None = None,
                   timing: OrderTiming | None = None, scenario: FillScenario | None = None):
    path = path or replay_path()
    plan = plan or replay_plan()
    timing = timing or replay_timing()
    scenario = scenario or replay_scenario(coverage_version=path.coverage_version)
    return reference_bracket(path, plan, terms=NQ_REFERENCE, fees=fees(),
                             fill_scenario=scenario, timing=timing)


def replay_manifest(*, outcome, plan: BracketPlan | None = None,
                    path: VenuePath | None = None, account_id: str = "synthetic-account-1") -> dict:
    plan = plan or replay_plan()
    path = path or replay_path()
    from trading_research.operations.artifacts import digest
    return {"instrument": path.instrument, "trading_date": "2024-06-03",
            "source_version": path.version, "fee_version": fees().version,
            "coverage_version": path.coverage_version, "account_id": account_id,
            "plan_id": plan.id, "stop_ticks": plan.stop_ticks,
            "required_flat_at": plan.required_flat_at,
            "execution_ids": {"entry": "exec-entry-a", "exit": "exec-exit-a"},
            "evidence_version": digest(outcome)}


def ledgers(root: Path, *, eligible_dates: tuple[str, ...] = ("2024-06-03",),
            multi_instrument: bool = False):
    orders = OrderLedger(root / "orders.sqlite", account_id="synthetic-account-1")
    orders.reconcile(id="fixture-initial-flat", known_at=DECISION - 1_000_000_000,
                     positions={}, open_order_ids=(), open_orders_complete=True,
                     execution_history_complete=True, evidence_version="fixture-risk-v1")
    term_rows = (("1002", NQ_REFERENCE), ("1003", NQ_REFERENCE)) if multi_instrument else (("1002", NQ_REFERENCE),)
    accounting = AccountingLedger(root / "account.sqlite", account_id="synthetic-account-1",
                                 eligible_dates=eligible_dates,
                                 eligibility_version="fixture-accounting-v1",
                                 terms=term_rows, fees=fees())
    return orders, accounting


__all__ = [
    "DECISION", "HORIZON", "FLATTEN", "REQUIRED_FLAT", "target_policy", "value",
    "decision_set", "terms", "fees", "boundary", "bracket_policy", "critical_snapshot",
    "venue_path", "REPLAY_ENTRY_AT", "REPLAY_TARGET_EVENT_AT", "REPLAY_TARGET_KNOWN_AT",
    "REPLAY_EXIT_AT", "REPLAY_COVERAGE_VERSION", "replay_path", "replay_plan", "replay_timing",
    "replay_scenario", "replay_outcome", "replay_manifest", "ledgers",
]
