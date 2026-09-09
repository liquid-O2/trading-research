"""E0 bracket/risk authorization and native order/account replay bridges.

This module is an adapter around the repository's existing typed execution
ports.  It does not emulate a broker and it never turns an uncertain venue
observation into an economic fill.  A positive policy value still has to pass
the independent :class:`AtomicEntryGate`; replay then records the exact
one-mini order, broker observations, confirmed fills and all eligible-day
statuses in the existing ledgers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from fractions import Fraction
from typing import Any, Mapping

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.execution.accounting import AccountingLedger, TradingFill
from trading_research.execution.costs import FeeSchedule
from trading_research.execution.orders import BrokerEvent, OrderLedger, OrderSpec
from trading_research.execution.replay import BracketOutcome, BracketPlan, OrderTiming, reference_bracket
from trading_research.execution.venue import Fill, FillScenario, VenuePath
from trading_research.foundations.contracts import Decision
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import FuturesTerms, Ticks
from trading_research.operations.artifacts import digest
from trading_research.risk.reservations import (
    AtomicEntryGate,
    CriticalSnapshot,
    EntryIntent,
    Reservation,
)
from trading_research.experiments.e0.policy import E0ActionValue, E0RuleSelection, TargetPolicy, _artifact_checks


def _attr(value: Any, *names: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        for name in names:
            if name in value:
                return value[name]
    else:
        for name in names:
            if hasattr(value, name):
                return getattr(value, name)
    return default


def _name(value: Any, label: str) -> str:
    if type(value) is not str or not value:
        raise ContractError(f"{label} requires a nonempty immutable identity")
    return value


def _decimal(value: Any, label: str, *, nonnegative: bool = False) -> Decimal:
    if isinstance(value, Fraction):
        value = Decimal(value.numerator) / Decimal(value.denominator)
    if isinstance(value, bool) or not isinstance(value, Decimal) or not value.is_finite() or nonnegative and value < 0:
        raise ContractError(f"{label} requires an exact finite Decimal")
    return value


def _integer(value: Any, label: str, *, nonnegative: bool = False) -> int:
    if type(value) is not int or nonnegative and value < 0:
        raise ContractError(f"{label} requires an integer")
    return value


@dataclass(frozen=True)
class E0Boundary:
    """The independent horizon, flatten-send and required-flat clocks."""

    horizon_end: int
    flatten_send_at: int
    required_flat_at: int
    version: str = ""

    def __post_init__(self) -> None:
        for value in (self.horizon_end, self.flatten_send_at, self.required_flat_at):
            timestamp(value)
        if self.horizon_end <= 0 or self.flatten_send_at <= 0 or self.required_flat_at <= 0:
            raise ContractError("boundary clocks cannot use a zero/sentinel timestamp")
        if self.required_flat_at <= self.flatten_send_at:
            raise ContractError("required-flat boundary must follow flatten send")
        if self.version:
            _name(self.version, "boundary version")

    @property
    def effective_horizon_end(self) -> int:
        return min(self.horizon_end, self.flatten_send_at)

    @property
    def boundary_version(self) -> str:
        return self.version or digest(self)


Boundary = E0Boundary


@dataclass(frozen=True)
class E0BracketPolicy:
    """Materialized geometry and routing assumptions for one fixed target."""

    id: str
    multiple: int | Fraction = 1
    geometry_version: str = ""
    range_width_ticks: int | None = None
    stop_distance_ticks: int | None = None
    worst_entry_ticks: int | None = None
    target_ticks: int | None = None
    impact_ticks: int = 0
    gap_reserve_usd: Decimal = Decimal(0)
    source_version: str = ""
    quantity: int = 1
    plan_id: str | None = None
    policy_version: str | None = None

    def __post_init__(self) -> None:
        _name(self.id, "bracket policy")
        multiple = Fraction(self.multiple) if not isinstance(self.multiple, Fraction) else self.multiple
        if multiple <= 0:
            raise ContractError("bracket target multiple must be positive")
        for value, label in ((self.range_width_ticks, "range width"), (self.stop_distance_ticks, "stop distance"),
                             (self.worst_entry_ticks, "worst entry"), (self.target_ticks, "target")):
            if value is not None:
                _integer(value, label)
        if self.range_width_ticks is not None and self.range_width_ticks <= 0:
            raise ContractError("range width must be positive")
        if self.stop_distance_ticks is not None and self.stop_distance_ticks <= 0:
            raise ContractError("stop distance must be positive")
        _integer(self.impact_ticks, "impact", nonnegative=True)
        _decimal(self.gap_reserve_usd, "gap reserve", nonnegative=True)
        if self.quantity != 1:
            raise ContractError("E0 bracket quantity is exactly one mini")
        if self.geometry_version:
            _name(self.geometry_version, "geometry")
        if self.source_version:
            _name(self.source_version, "bracket source")
        if self.plan_id is not None:
            _name(self.plan_id, "plan")
        if self.policy_version is not None:
            _name(self.policy_version, "policy version")

    @property
    def target_policy(self) -> TargetPolicy:
        return TargetPolicy(self.id, self.multiple, self.target_ticks,
                            self.policy_version, self.source_version or None)

    @property
    def version(self) -> str:
        return digest(self)


BracketPolicy = E0BracketPolicy
PlanPolicy = E0BracketPolicy


@dataclass(frozen=True)
class AuthorizedBracket:
    plan: BracketPlan
    intent: EntryIntent
    reservation: Reservation
    policy: Any
    decision: Any
    quote_id: str
    effective_horizon_end: int
    geometry_version: str

    @property
    def approved(self) -> bool:
        return self.reservation.approved

    @property
    def reason(self) -> str:
        return self.reservation.reason

    @property
    def policy_id(self) -> str:
        return _attr(self.policy, "id", "policy_id")

    @property
    def version(self) -> str:
        return digest(self)

    def replay(self, *, fill_scenario, timing: OrderTiming,
               prior_day_net: Decimal = Decimal(0), daily_budget: Decimal = Decimal(1000)) -> BracketOutcome:
        if not self.approved:
            raise DependencyUnavailable("risk reservation did not authorize bracket replay")
        try:
            return reference_bracket(self._venue_path, self.plan, terms=self._terms, fees=self._fees,
                                    fill_scenario=fill_scenario, timing=timing,
                                    prior_day_net=prior_day_net, daily_budget=daily_budget)
        except ContractError as error:
            if str(error) == "intent expires before modeled venue arrival":
                raise ContractError("intent expires before modeled venue arrival or boundary") from error
            raise


@dataclass(frozen=True)
class E0LedgerReceipt:
    status: str
    order_submission_ids: tuple[str, ...]
    broker_event_ids: tuple[str, ...]
    execution_ids: tuple[str, ...]
    trading_fills: tuple[TradingFill, ...]
    day_status: str
    report: dict[str, Any]
    uncertain: bool
    source_version: str
    version: str

    @property
    def order_ids(self) -> tuple[str, ...]:
        return self.order_submission_ids


def _boundary(value: Any, snapshot: CriticalSnapshot | None = None) -> E0Boundary:
    if isinstance(value, E0Boundary):
        return value
    if value is None and snapshot is not None:
        flatten = snapshot.flatten_at
        return E0Boundary(flatten, flatten, flatten + 1, "snapshot-boundary")
    horizon = _attr(value, "horizon_end", "effective_horizon_end")
    flatten = _attr(value, "flatten_send_at", "flatten_at", "boundary_at")
    required = _attr(value, "required_flat_at", "required_flat", default=None)
    if required is None and flatten is not None:
        required = flatten
    if horizon is None or flatten is None or required is None:
        raise ContractError("E0 bracket requires horizon, flatten-send and required-flat boundaries")
    return E0Boundary(horizon, flatten, required, _attr(value, "version", "boundary_version", default="") or "")


def _policy(value: Any, decision: Any) -> E0BracketPolicy:
    if isinstance(value, E0BracketPolicy):
        return value
    if isinstance(value, TargetPolicy):
        # Geometry may be supplied on the selected E0 value or decision.
        selected = _attr(decision, "selected_value")
        return E0BracketPolicy(value.id, value.multiple,
                               _attr(value, "geometry_version", default="") or _attr(selected, "geometry_version", default="") or "",
                               _attr(value, "range_width_ticks", default=None) or _attr(selected, "range_width_ticks", default=None),
                               _attr(value, "stop_distance_ticks", default=None) or _attr(selected, "stop_distance_ticks", default=None),
                               value.target_ticks, None, 0,
                               _attr(value, "gap_reserve_usd", default=Decimal(0)),
                               _attr(value, "source_version", default="") or "", 1,
                               _attr(value, "plan_id", default=None), value.policy_version)
    selected = _attr(decision, "selected_value")
    get = lambda *names, default=None: _attr(value, *names, default=default)
    return E0BracketPolicy(
        get("id", "policy_id", default=_attr(selected, "policy_id", "policy", default="")),
        get("multiple", "target_multiple", default=_attr(selected, "target_multiple", default=1)),
        get("geometry_version", default=_attr(selected, "geometry_version", default="")) or "",
        get("range_width_ticks", "range_width", default=_attr(selected, "range_width_ticks", default=None)),
        get("stop_distance_ticks", "stop_distance", default=_attr(selected, "stop_distance_ticks", default=None)),
        get("worst_entry_ticks", "worst_entry", default=_attr(selected, "worst_entry_ticks", default=None)),
        get("target_ticks", "target", default=_attr(selected, "target_ticks", default=None)),
        get("impact_ticks", "impact", default=0),
        get("gap_reserve_usd", "gap_reserve", default=Decimal(0)),
        get("source_version", default=_attr(selected, "source_version", default="")) or "",
        get("quantity", default=1), get("plan_id", default=None), get("policy_version", default=None))


def _decision_side(decision: Any) -> int:
    selected = _attr(decision, "selected_value")
    side = _attr(selected, "side", default=_attr(decision, "side", default=None))
    if side is None:
        action = _attr(decision, "selected_action", default="")
        side = -1 if "short" in action else 1
    if type(side) is not int or side not in (-1, 1):
        raise ContractError("selected E0 action must carry one signed side")
    return side


def _target_policy(policy: Any) -> TargetPolicy:
    if isinstance(policy, E0BracketPolicy):
        return policy.target_policy
    if type(policy) is TargetPolicy:
        return policy
    raise ContractError("authorization requires a typed target policy")


def _same_target_policy(left: Any, right: Any) -> bool:
    left, right = _target_policy(left), _target_policy(right)
    return (left.id, Fraction(left.multiple), left.target_ticks, left.policy_version) == (
        right.id, Fraction(right.multiple), right.target_ticks, right.policy_version)


def _decision_at(decision: Any) -> int:
    at = _attr(decision, "at", "decision_at")
    timestamp(at)
    action = _attr(decision, "selected_action", default="")
    if action in ("flat_or_wait", "abstain", "flat") or not action:
        raise DependencyUnavailable("only an admitted selected entry action can authorize a bracket")
    return at


def _decision_binding(decision: Any, *, policy: E0BracketPolicy, at: int) -> int:
    """Validate the typed policy/risk selection before touching the gate.

    Learned values use the exact selected E0ActionValue.  The deterministic
    rule branch has no fitted probabilities by design, so it uses the separate
    E0RuleSelection created from observations.E0DecisionSet.  Action text alone
    is never accepted as admission evidence.
    """

    if type(decision) is not Decision:
        raise ContractError("E0 authorization requires the common typed decision")
    decision_set_id = _attr(decision, "decision_set_id", default=_attr(decision, "id", "decision_id"))
    candidate_ids = tuple(_attr(decision, "candidate_ids", default=()) or ())
    selected = _attr(decision, "selected_value", default=None)
    rule = _attr(decision, "e0_rule_selection", "rule_selection", default=None)
    action = _attr(decision, "selected_action", default="")
    target = policy.target_policy
    if type(selected) is E0ActionValue:
        if selected.expected_net_usd <= 0 or not selected.complete or selected.unavailable_reason:
            raise DependencyUnavailable("only a complete positive E0 value can authorize a bracket")
        if selected.decision_at != at or selected.decision_set_id != decision_set_id:
            raise ContractError("selected E0 value belongs to another decision cut or set")
        if not candidate_ids or selected.candidate_id not in candidate_ids:
            raise ContractError("selected E0 value is outside the admitted candidate population")
        if not _same_target_policy(selected.policy, target):
            raise ContractError("authorization target policy differs from the selected E0 value")
        expected_action = f"enter_{'long' if selected.side == 1 else 'short'}_{selected.policy.id}"
        if action != expected_action:
            raise ContractError("decision action is not the exact selected E0 policy action")
        if _attr(decision, "selected_policy_id", default=selected.policy.id) != selected.policy.id:
            raise ContractError("decision selected policy identity differs from its value")
        if not selected.intent_id or _attr(decision, "intent_id", default=None) != selected.intent_id:
            raise ContractError("decision intent differs from the selected E0 value")
        if selected.expiry_at is None or _attr(decision, "expires_at", default=None) != selected.expiry_at:
            raise ContractError("decision expiry differs from the selected E0 value")
        if _attr(decision, "risk_verdict", default="") != "pending_independent_gate":
            raise DependencyUnavailable("decision risk verdict does not authorize an entry")
        evidence_reason = _artifact_checks((selected,), (selected.artifact_evidence,), None,
                                          decision_at=at)
        if evidence_reason:
            raise DependencyUnavailable(evidence_reason)
        return selected.side
    if type(rule) is E0RuleSelection:
        rule.__post_init__()
        if rule.decision_set_id != decision_set_id or rule.decision_at != at:
            raise ContractError("rule selection belongs to another observation decision set")
        if not candidate_ids or rule.candidate_id not in candidate_ids:
            raise ContractError("rule selection is outside the admitted candidate population")
        if not _same_target_policy(rule.policy, target):
            raise ContractError("authorization target policy differs from the fixed rule selection")
        expected_action = f"enter_{'long' if rule.side == 1 else 'short'}"
        if action != expected_action:
            raise ContractError("rule action is not bound to the typed first-inward selection")
        if _attr(decision, "selected_policy_id", default=rule.policy.id) != rule.policy.id:
            raise ContractError("rule decision selected policy identity differs from fixed target")
        if (decision.intent_id != digest((rule.decision_set_id, rule.candidate_id, rule.policy.id))
                or decision.expires_at != at + 900_000_000_000):
            raise ContractError("rule intent or expiry differs from its exact selected action")
        if decision.risk_verdict != "pending_independent_gate":
            raise DependencyUnavailable("rule decision requires the independent risk gate")
        return rule.side
    raise DependencyUnavailable("typed selected E0 value or observation-backed rule selection is required")


def authorize_e0_bracket(*, decision, plan_policy, venue_path: VenuePath, terms: FuturesTerms,
                         fees: FeeSchedule, boundary, critical_snapshot: CriticalSnapshot,
                         entry_gate: AtomicEntryGate) -> AuthorizedBracket:
    """Materialize exact one-mini geometry and obtain an independent reservation."""

    if type(venue_path) is not VenuePath or type(terms) is not FuturesTerms or type(fees) is not FeeSchedule:
        raise ContractError("E0 authorization requires typed venue path, futures terms and fee schedule")
    if type(critical_snapshot) is not CriticalSnapshot or type(entry_gate) is not AtomicEntryGate:
        raise ContractError("E0 authorization requires typed critical state and atomic entry gate")
    policy = _policy(plan_policy, decision)
    at = _decision_at(decision)
    side = _decision_binding(decision, policy=policy, at=at)
    bound = _boundary(boundary, critical_snapshot)
    if venue_path.instrument != critical_snapshot.instrument:
        raise ContractError("venue and critical account state use different instruments")
    if terms.root not in {"NQ", "ES"} or critical_snapshot.terms != terms:
        raise ContractError("raw terms differ from the current critical account state")
    if critical_snapshot.at < at:
        raise ContractError("critical account state is older than the decision cut")
    quote, reason = venue_path.quote_at(at, clock="strategy")
    if quote is None:
        raise DependencyUnavailable("entry decision lacks a certified executable strategy quote: " + reason)
    executable = quote.ask if side == 1 else quote.bid
    worst_entry = policy.worst_entry_ticks
    if worst_entry is None:
        worst_entry = executable + side * policy.impact_ticks
    if type(worst_entry) is not int:
        raise ContractError("worst entry must be an exact integer tick")
    if side * (worst_entry - executable) < 0:
        raise ContractError("worst entry is more favorable than the certified executable quote")
    distance = policy.stop_distance_ticks
    if distance is None and policy.range_width_ticks is not None:
        distance = max(8, (policy.range_width_ticks + 9) // 10)
    if distance is None:
        selected = _attr(decision, "selected_value")
        distance = _attr(selected, "stop_distance_ticks")
    if type(distance) is not int or distance <= 0:
        raise ContractError("positive exact stop distance is required")
    stop = worst_entry - side * distance
    target = policy.target_ticks
    if target is None:
        multiple = Fraction(policy.multiple) if not isinstance(policy.multiple, Fraction) else policy.multiple
        if multiple.denominator != 1:
            raise ContractError("E0 target multiple must produce an integer tick target")
        target = worst_entry + side * distance * multiple.numerator
    if side * (worst_entry - stop) <= 0 or side * (target - worst_entry) <= 0:
        raise ContractError("stop and target must be adverse/favorable on the correct sides")
    effective_horizon = bound.effective_horizon_end
    if effective_horizon <= at:
        raise ContractError("intent expires before modeled venue arrival or boundary")
    decision_expiry = _attr(decision, "expires_at", default=None)
    expiry = min(effective_horizon, decision_expiry) if decision_expiry is not None else effective_horizon
    if expiry <= at:
        raise ContractError("intent expires before modeled venue arrival or boundary")
    geometry = policy.geometry_version or _attr(_attr(decision, "selected_value"), "geometry_version", default="") or digest({
        "policy": policy.version, "instrument": venue_path.instrument, "stop_distance": distance,
        "worst_entry": worst_entry, "target": target})
    plan_id = policy.plan_id or _attr(decision, "intent_id", default=None) or digest({"decision": _attr(decision, "id"), "policy": policy.version})
    plan = BracketPlan(plan_id, venue_path.instrument, side, at, worst_entry, stop, target,
                       effective_horizon, bound.flatten_send_at, bound.required_flat_at,
                       policy.gap_reserve_usd, geometry)
    decision_id = _attr(decision, "id", "decision_id")
    intent_id = _attr(decision, "intent_id", default=None) or f"intent-{plan_id}"
    intent = EntryIntent(intent_id, critical_snapshot.account_id, venue_path.instrument, side,
                         Ticks(stop), Ticks(worst_entry), at, expiry, effective_horizon,
                         critical_snapshot.version, decision_id, fees.version, policy.gap_reserve_usd)
    if entry_gate.account_id != critical_snapshot.account_id or entry_gate.fees.version != fees.version:
        raise ContractError("entry gate account or fee schedule differs from authorization")
    # Observation is idempotent for an already observed exact snapshot and
    # makes this adapter usable with a newly constructed synthetic gate.  A
    # changed/current snapshot still reaches the gate's monotonic checks.
    entry_gate.observe(critical_snapshot)
    reservation = entry_gate.reserve(intent, at=at)
    authorized = AuthorizedBracket(plan, intent, reservation, policy, decision, quote.id,
                                   effective_horizon, geometry)
    object.__setattr__(authorized, "_venue_path", venue_path)
    object.__setattr__(authorized, "_terms", terms)
    object.__setattr__(authorized, "_fees", fees)
    return authorized


def _validate_fill_binding(fill: Fill, *, venue_path: VenuePath, fill_scenario: FillScenario) -> None:
    if type(fill) is not Fill:
        raise ContractError("replay outcome must carry typed venue fills")
    if fill.scenario_version != fill_scenario.version:
        raise ContractError("fill scenario differs from the frozen replay scenario")
    actual = venue_path.marketable(order_id=fill.order_id, side=fill.side,
                                  arrival_at=fill.at, scenario=fill_scenario)
    if fill != actual:
        raise ContractError("replay fill differs from the actual side-correct venue quote and fill scenario")
    if fill.source_event_id is None:
        if fill.status == "filled_under_scenario":
            raise ContractError("confirmed fill must bind an actual venue source event")
        return
    source_events = tuple(event for event in (*venue_path.quotes, *venue_path.trades)
                          if event.id == fill.source_event_id)
    if len(source_events) != 1:
        raise ContractError("fill source event is absent or duplicated in the retained venue path")
    if source_events[0].instrument != venue_path.instrument:
        raise ContractError("fill source event uses another raw instrument")


def _validate_replay_binding(outcome: BracketOutcome, *, venue_path: VenuePath,
                             fill_scenario: FillScenario) -> None:
    if type(venue_path) is not VenuePath or type(fill_scenario) is not FillScenario:
        raise ContractError("replay requires the exact retained venue path and fill scenario")
    if fill_scenario.quote_coverage_version != venue_path.coverage_version:
        raise ContractError("fill scenario coverage differs from the retained venue path")
    _validate_fill_binding(outcome.entry, venue_path=venue_path, fill_scenario=fill_scenario)
    if outcome.exit is not None:
        _validate_fill_binding(outcome.exit, venue_path=venue_path, fill_scenario=fill_scenario)


def _manifest_fields(manifest: Any, *, outcome: BracketOutcome, accounting: AccountingLedger,
                    venue_path: VenuePath, fill_scenario: FillScenario) -> dict[str, Any]:
    if type(venue_path) is not VenuePath or type(fill_scenario) is not FillScenario:
        raise ContractError("scenario manifest requires typed venue path and fill scenario")
    _validate_replay_binding(outcome, venue_path=venue_path, fill_scenario=fill_scenario)
    instrument = _attr(manifest, "instrument", "instrument_id", default=None)
    if instrument is None:
        raise ContractError("scenario manifest must bind the raw instrument to accounting terms")
    if instrument != venue_path.instrument or instrument not in accounting.terms:
        raise ContractError("scenario instrument differs from the retained venue path or accounting terms")
    trading_date = _attr(manifest, "trading_date", "date", default=None)
    if trading_date is None:
        raise ContractError("scenario manifest must bind an eligible trading date")
    date.fromisoformat(trading_date)
    source_version = _attr(manifest, "source_version", "venue_source_version", default=None)
    fee_version = _attr(manifest, "fee_version", default=None)
    coverage_version = _attr(manifest, "coverage_version", "quote_coverage_version", default=None)
    if source_version != venue_path.version:
        raise ContractError("scenario source version differs from the retained venue path")
    if coverage_version != venue_path.coverage_version or coverage_version != fill_scenario.quote_coverage_version:
        raise ContractError("scenario coverage version differs from the retained fill scenario")
    if fee_version != fill_scenario.fee_version or fee_version != accounting.fees.version:
        raise ContractError("scenario fee version differs from the retained fill scenario")
    return {
        "instrument": instrument, "trading_date": trading_date,
        "source_version": source_version, "fee_version": fee_version,
        "coverage_version": coverage_version,
        "account_id": _attr(manifest, "account_id", default=accounting.account_id),
        "plan_id": _attr(manifest, "plan_id", "bracket_id", default=outcome.plan_version[:24]),
        "stop_ticks": _attr(manifest, "stop_ticks", default=None),
        "required_flat_at": _attr(manifest, "required_flat_at", default=None),
        "execution_ids": _attr(manifest, "execution_ids", default={}) or {},
        "evidence_version": _attr(manifest, "evidence_version", default=None),
    }


def _execution_id(manifest: dict[str, Any], fill: Fill, role: str) -> str:
    values = manifest["execution_ids"]
    if isinstance(values, Mapping):
        value = values.get(role) or values.get(fill.order_id) or values.get(f"{role}_execution_id")
        if value:
            return _name(value, f"{role} execution")
    direct = manifest.get(f"{role}_execution_id")
    if direct:
        return _name(direct, f"{role} execution")
    return f"exec-{role}-{fill.order_id}"


def _event_id(plan_id: str, role: str, kind: str) -> str:
    return f"e0:{plan_id}:{role}:{kind}"


def _outcome_plan(outcome: BracketOutcome, manifest: dict[str, Any]) -> tuple[int, int, int]:
    stop = manifest.get("stop_ticks")
    if stop is None:
        # The replay outcome does not carry a full BracketPlan by design.  A
        # caller that wants the durable protective order must bind its stop in
        # the scenario manifest; deriving one from an outcome would be a
        # hindsight geometry substitution.
        raise ContractError("scenario manifest must carry the frozen protective stop ticks")
    return _integer(stop, "protective stop"), outcome.entry.side, outcome.entry.at


def _confirmed(fill: Fill | None) -> bool:
    return fill is not None and fill.status == "filled_under_scenario" and fill.quantity == 1 and type(fill.price_ticks) is int


def _day_status(value: Any, *, manifest: dict[str, Any], outcome: BracketOutcome, uncertain: bool) -> tuple[str, int, str]:
    if isinstance(value, str):
        status, at, evidence = value, outcome.position_known_flat_at or outcome.entry.at, manifest["evidence_version"]
    elif value is None:
        status = "complete" if not uncertain and outcome.observation_complete and outcome.exit is not None and outcome.boundary_met else "incomplete"
        at, evidence = outcome.position_known_flat_at or outcome.entry.at, manifest["evidence_version"]
    else:
        status = _attr(value, "status", default="incomplete")
        at = _attr(value, "at", "known_at", default=outcome.position_known_flat_at or outcome.entry.at)
        evidence = _attr(value, "evidence_version", "source_version", default=manifest["evidence_version"])
    if status == "complete" and (uncertain or not outcome.observation_complete or outcome.exit is None or not outcome.boundary_met):
        raise ContractError("an uncertain/incomplete bracket cannot publish a complete day status")
    if status not in {"complete", "flat", "outage", "halted", "incomplete", "boundary_failure"}:
        raise ContractError("unsupported E0 day status")
    timestamp(at);_name(evidence, "day-status evidence")
    return status, at, evidence


@dataclass(frozen=True)
class ScheduledReplayEvent:
    """One causally publishable event in an E0 account replay.

    ``event_at`` is the venue/local occurrence clock carried by the source
    outcome.  ``known_at`` is the clock at which the event may be published to
    the durable ledgers.  Keeping both clocks on the scheduled object prevents
    a late broker report from being silently rewritten as a late fill.
    """

    id: str
    journal: str
    key: str
    event_at: int
    known_at: int
    payload: Any
    priority: int = 0

    def __post_init__(self) -> None:
        _name(self.id, "scheduled replay event")
        if self.journal not in {"order", "broker", "fill", "reconcile", "day"}:
            raise ContractError("unsupported scheduled replay journal")
        _name(self.key, "scheduled replay key")
        timestamp(self.event_at)
        timestamp(self.known_at)
        _integer(self.priority, "scheduled replay priority")

    @property
    def version(self) -> str:
        return digest(self)


def _outcome_event_at(outcome: BracketOutcome, kind: str, *, required: bool = False) -> int | None:
    matches = tuple(_attr(event, "at", default=None) for event in outcome.events
                    if _attr(event, "kind", default="") == kind)
    if len(matches) > 1 and len(set(matches)) != 1:
        raise IntegrityError(f"outcome carries contradictory {kind!r} event clocks")
    if matches:
        value = matches[0]
        timestamp(value)
        return value
    if required:
        raise ContractError(f"outcome lacks required {kind!r} event")
    return None


def _replay_evidence(manifest: dict[str, Any]) -> str:
    return _name(manifest["evidence_version"], "replay evidence")


class _PendingReplayEvents(tuple):
    """Tuple-like pending view that also supports the historical ``pending()`` call."""

    def __new__(cls, values=()):
        return super().__new__(cls, values)

    def __call__(self):
        return tuple(self)


class E0OutcomeReplay:
    """Causally publish a frozen :class:`BracketOutcome` in account ledgers.

    The scheduler is deliberately small and offline.  It materializes the
    broker/order/account events once, then ``advance`` publishes only events
    whose *known* clock is at or before the requested cut.  Reconstructing the
    scheduler against the same journals is safe because every event uses the
    same durable idempotency key.
    """

    VERSION = "e0-outcome-replay-v1"
    _PRIORITY = {
        "order": 10,
        "broker": 20,
        "fill": 30,
        "reconcile": 40,
        "day": 80,
    }

    def __init__(self, *, outcome: BracketOutcome, order_ledger: OrderLedger,
                 accounting: AccountingLedger, scenario_manifest=None,
                 timing: OrderTiming, venue_path: VenuePath,
                 fill_scenario: FillScenario, day_status=None, checkpoint=None,
                 finalize_day: bool = True):
        if type(outcome) is not BracketOutcome or type(order_ledger) is not OrderLedger or type(accounting) is not AccountingLedger:
            raise ContractError("E0 outcome replay requires typed replay and ledger ports")
        if type(timing) is not OrderTiming:
            raise ContractError("E0 outcome replay requires explicit order timing")
        if type(venue_path) is not VenuePath or type(fill_scenario) is not FillScenario:
            raise ContractError("E0 outcome replay requires the exact retained venue path and fill scenario")
        if outcome.timing_version != digest(timing):
            raise ContractError("replay timing differs from the outcome's frozen timing version")
        if scenario_manifest is None:
            raise ContractError("scenario manifest must bind source, date, fee and protective geometry")
        if type(finalize_day) is not bool or not finalize_day and day_status is not None:
            raise ContractError("day finalization must have one explicit owner")
        self.outcome = outcome
        self.order_ledger = order_ledger
        self.accounting = accounting
        self.timing = timing
        self.venue_path = venue_path
        self.fill_scenario = fill_scenario
        self.finalize_day = finalize_day
        self.manifest = _manifest_fields(scenario_manifest, outcome=outcome, accounting=accounting,
                                         venue_path=venue_path, fill_scenario=fill_scenario)
        if self.manifest["account_id"] != order_ledger.account_id or self.manifest["account_id"] != accounting.account_id:
            raise ContractError("order/account ledgers and scenario use different accounts")
        if self.manifest["fee_version"] != accounting.fees.version:
            raise ContractError("scenario fee version differs from the accounting ledger")
        if self.manifest["instrument"] != venue_path.instrument or self.manifest["instrument"] not in accounting.terms:
            raise ContractError("scenario instrument is outside the retained accounting/venue terms")
        self.plan_id = self.manifest["plan_id"]
        self._day_status_value = day_status
        self._events = self._build_events(day_status)
        self._schedule_version = digest(self._events)
        self._last_cut: int | None = None
        if checkpoint is not None:
            self._restore_checkpoint(checkpoint)

    @property
    def schedule_version(self) -> str:
        return self._schedule_version

    @property
    def final_cut(self) -> int:
        return max((event.known_at for event in self._events), default=self.outcome.entry.at)

    @property
    def risk_held(self) -> bool:
        """Whether the bracket's reservation must remain occupied at this cut."""

        if self.outcome.position_known_flat_at is None:
            return True
        flat_id = f"{self.plan_id}:flat"
        return not any(event.key == f"reconcile:{flat_id}" and self._recorded(event)
                       for event in self._events if event.journal == "reconcile")

    def _journal_keys(self) -> tuple[set[str], set[str]]:
        order_keys = {event["key"] for event in self.order_ledger.journal.read()}
        accounting_keys = {event["key"] for event in self.accounting.journal.read()}
        return order_keys, accounting_keys

    def _recorded(self, event: ScheduledReplayEvent, *, keys=None) -> bool:
        if keys is None:
            keys = self._journal_keys()
        order_keys, accounting_keys = keys
        if event.journal != "day":
            return event.key in (order_keys if event.journal in {"order", "broker", "reconcile"} else accounting_keys)
        if event.key in accounting_keys:
            return True
        # Legacy ledgers used day:<date>:<at>.  Treat an exact immutable
        # payload match as recorded while still rejecting any conflicting
        # status through AccountingLedger.day_status.
        expected_kind, expected_payload = self._expected_journal_entry(event)
        return any(row["kind"] == expected_kind and row["payload"] == expected_payload
                   for row in self.accounting.journal.read())

    def _existing(self, event: ScheduledReplayEvent) -> dict[str, Any] | None:
        journal = (self.order_ledger.journal
                   if event.journal in {"order", "broker", "reconcile"}
                   else self.accounting.journal)
        existing = next((row for row in journal.read() if row["key"] == event.key), None)
        if existing is not None or event.journal != "day":
            return existing
        expected_kind, expected_payload = self._expected_journal_entry(event)
        return next((row for row in journal.read()
                     if row["kind"] == expected_kind and row["payload"] == expected_payload), None)

    @staticmethod
    def _expected_journal_entry(event: ScheduledReplayEvent) -> tuple[str, dict[str, Any]]:
        if event.journal == "order":
            return "order_submitted", {"spec": asdict(event.payload)}
        if event.journal == "broker":
            return "broker_event", {"event": asdict(event.payload)}
        if event.journal == "fill":
            payload = {**asdict(event.payload), "fee": str(event.payload.fee)}
            return "trading_fill", payload
        if event.journal == "reconcile":
            return "broker_reconciliation", event.payload
        if event.journal == "day":
            trading_date, at, status, evidence = event.payload
            return "day_status", {"date": trading_date, "at": at,
                                   "status": status, "evidence_version": evidence}
        raise ContractError("unsupported scheduled replay journal")

    @property
    def pending(self) -> tuple[ScheduledReplayEvent, ...]:
        """Return scheduled events that have not yet reached a durable journal."""

        keys = self._journal_keys()
        return _PendingReplayEvents(event for event in self._events if not self._recorded(event, keys=keys))

    @property
    def pending_events(self) -> tuple[ScheduledReplayEvent, ...]:
        return tuple(self.pending)

    def checkpoint(self) -> dict[str, Any]:
        """Return a restart token bound to outcome, timing and schedule identity."""

        keys = self._journal_keys()
        return {
            "version": self.VERSION,
            "outcome_version": digest(self.outcome),
            "timing_version": digest(self.timing),
            "manifest_version": digest(self.manifest),
            "finalize_day": self.finalize_day,
            "schedule_version": self._schedule_version,
            "last_cut": self._last_cut,
            "recorded_event_ids": tuple(event.id for event in self._events if self._recorded(event, keys=keys)),
            "pending_event_ids": tuple(event.id for event in self._events if not self._recorded(event, keys=keys)),
            "risk_held": self.risk_held,
        }

    @classmethod
    def restore(cls, checkpoint, *, outcome: BracketOutcome, order_ledger: OrderLedger,
                accounting: AccountingLedger, scenario_manifest=None,
                timing: OrderTiming, venue_path: VenuePath,
                fill_scenario: FillScenario, day_status=None, finalize_day: bool = True):
        return cls(outcome=outcome, order_ledger=order_ledger, accounting=accounting,
                   scenario_manifest=scenario_manifest, timing=timing,
                   venue_path=venue_path, fill_scenario=fill_scenario,
                   day_status=day_status, checkpoint=checkpoint, finalize_day=finalize_day)

    def _restore_checkpoint(self, checkpoint: Any) -> None:
        if not isinstance(checkpoint, Mapping) or checkpoint.get("version") != self.VERSION:
            raise ContractError("unsupported E0 outcome replay checkpoint")
        expected = {
            "outcome_version": digest(self.outcome),
            "timing_version": digest(self.timing),
            "manifest_version": digest(self.manifest),
            "finalize_day": self.finalize_day,
            "schedule_version": self._schedule_version,
        }
        for key, value in expected.items():
            if checkpoint.get(key) != value:
                raise IntegrityError(f"E0 replay checkpoint {key} does not match the frozen replay")
        keys = self._journal_keys()
        actual_recorded = tuple(event.id for event in self._events if self._recorded(event, keys=keys))
        actual_pending = tuple(event.id for event in self._events if not self._recorded(event, keys=keys))
        stored_recorded = checkpoint.get("recorded_event_ids")
        stored_pending = checkpoint.get("pending_event_ids")
        if (not isinstance(stored_recorded, (tuple, list))
                or not isinstance(stored_pending, (tuple, list))
                or tuple(stored_recorded) != actual_recorded
                or tuple(stored_pending) != actual_pending):
            raise IntegrityError("E0 replay checkpoint event cursor differs from durable journals")
        # The recorded IDs are only useful if the durable payloads still agree
        # with this exact schedule.  This also catches a manually replaced
        # journal row before a later advance can silently treat it as done.
        for event in self._events:
            if not self._recorded(event, keys=keys):
                continue
            existing = self._existing(event)
            expected_kind, expected_payload = self._expected_journal_entry(event)
            if (existing is None or existing["kind"] != expected_kind
                    or digest(existing["payload"]) != digest(expected_payload)):
                raise IntegrityError(f"E0 replay checkpoint payload differs for {event.key}")
        cut = checkpoint.get("last_cut")
        if cut is not None:
            timestamp(cut)
            due = tuple(event.id for event in self._events if event.known_at <= cut)
            if tuple(stored_recorded) != due:
                raise IntegrityError("E0 replay checkpoint last cut does not match durable event cursor")
            if any(event.known_at > cut and self._recorded(event, keys=keys) for event in self._events):
                raise IntegrityError("E0 replay checkpoint records an event after its last cut")
        if "risk_held" in checkpoint and checkpoint["risk_held"] is not self.risk_held:
            raise IntegrityError("E0 replay checkpoint risk state differs from durable journals")
        self._last_cut = cut

    def _add(self, events: list[ScheduledReplayEvent], *, journal: str, key: str,
             event_id: str, event_at: int, known_at: int, payload: Any,
             priority: int | None = None) -> None:
        timestamp(event_at)
        timestamp(known_at)
        events.append(ScheduledReplayEvent(event_id, journal, key, event_at, known_at,
                                           payload, self._PRIORITY[journal] if priority is None else priority))

    def _build_events(self, day_status) -> tuple[ScheduledReplayEvent, ...]:
        outcome = self.outcome
        manifest = self.manifest
        evidence = _replay_evidence(manifest)
        instrument = manifest["instrument"]
        side, entry_at = outcome.entry.side, outcome.entry.at
        timestamp(entry_at)
        if type(side) is not int or side not in (-1, 1):
            raise ContractError("outcome entry must carry one signed side")
        stop_ticks = manifest.get("stop_ticks")
        if _confirmed(outcome.entry):
            if stop_ticks is None:
                raise ContractError("scenario manifest must carry the frozen protective stop ticks")
            stop_ticks = _integer(stop_ticks, "protective stop")
        required = manifest.get("required_flat_at")
        if required is None:
            required = outcome.position_known_flat_at
        if required is None:
            required = entry_at + 1
        timestamp(required)
        if required <= entry_at:
            raise ContractError("required-flat boundary must follow the actual entry clock")
        expiry = required
        authorization = outcome.plan_version
        if type(authorization) is not str or not authorization:
            raise ContractError("outcome plan identity is required for order authorization")
        events: list[ScheduledReplayEvent] = []

        sent_at = _outcome_event_at(outcome, "entry_sent")
        if sent_at is None:
            sent_at = entry_at
        if sent_at > entry_at:
            raise ContractError("entry submission occurs after the actual entry fill")
        entry_client = f"{self.plan_id}:entry"
        self._add(events, journal="order", key=f"order:{entry_client}",
                  event_id=f"submit:{entry_client}", event_at=sent_at,
                  known_at=sent_at,
                  payload=OrderSpec(entry_client, self.order_ledger.account_id,
                                    instrument, side, 1, "entry", "market", None,
                                    sent_at, expiry, authorization), priority=10)
        entry_known = entry_at + self.timing.broker_report_ns
        timestamp(entry_known)
        if not _confirmed(outcome.entry):
            timeout_at = outcome.entry.at
            timeout_known = timeout_at + self.timing.broker_report_ns
            self._add(events, journal="broker", key=f"broker:{_event_id(self.plan_id, 'entry', 'uncertain')}",
                      event_id=_event_id(self.plan_id, "entry", "uncertain"), event_at=timeout_at,
                      known_at=timeout_known,
                      payload=BrokerEvent(_event_id(self.plan_id, "entry", "uncertain"), entry_client,
                                          "timeout", timeout_at, timeout_known, evidence,
                                          reason=outcome.entry.reason or "uncertain entry observation"))
        else:
            entry_exec = _execution_id(manifest, outcome.entry, "entry")
            ack_id = _event_id(self.plan_id, "entry", "ack")
            fill_id = _event_id(self.plan_id, "entry", "fill")
            self._add(events, journal="broker", key=f"broker:{ack_id}", event_id=ack_id,
                      event_at=entry_at, known_at=entry_known,
                      payload=BrokerEvent(ack_id, entry_client, "acknowledged", entry_at,
                                          entry_known, evidence, reason="confirmed venue fill"), priority=20)
            self._add(events, journal="broker", key=f"broker:{fill_id}", event_id=fill_id,
                      event_at=entry_at, known_at=entry_known,
                      payload=BrokerEvent(fill_id, entry_client, "fill", entry_at, entry_known,
                                          evidence, entry_exec, 1, outcome.entry.price_ticks,
                                          outcome.entry.reason or "confirmed venue fill"), priority=21)
            entry_fill = TradingFill(entry_exec, instrument, manifest["trading_date"], entry_at,
                                     side, outcome.entry.price_ticks,
                                     self.accounting.fees.fee(self.accounting.terms[instrument].root),
                                     self.accounting.fees.version, manifest["source_version"])
            self._add(events, journal="fill", key=f"fill:{entry_exec}", event_id=f"fill:{entry_exec}",
                      event_at=entry_at, known_at=entry_known, payload=entry_fill, priority=30)

            stop_client = f"{self.plan_id}:protective-stop"
            self._add(events, journal="order", key=f"order:{stop_client}", event_id=f"submit:{stop_client}",
                      event_at=entry_known, known_at=entry_known,
                      payload=OrderSpec(stop_client, self.order_ledger.account_id, instrument, -side, 1,
                                        "protective_stop", "stop_market", stop_ticks, entry_known,
                                        expiry, authorization, self.plan_id + ":oco", entry_client), priority=11)
            working_id = _event_id(self.plan_id, "stop", "working")
            self._add(events, journal="broker", key=f"broker:{working_id}", event_id=working_id,
                      event_at=entry_known, known_at=entry_known,
                      payload=BrokerEvent(working_id, stop_client, "working", entry_known, entry_known,
                                          evidence, reason="protective stop accepted"), priority=22)
            # Entry confirmation also carries a complete simulated broker
            # snapshot.  This is the first point at which the risk gate may
            # safely mirror a filled one-mini position and its live stop.
            entry_reconcile_id = f"{self.plan_id}:entry-state"
            self._add(events, journal="reconcile", key=f"reconcile:{entry_reconcile_id}",
                      event_id=f"reconcile:{entry_reconcile_id}", event_at=entry_known,
                      known_at=entry_known,
                      payload={"id": entry_reconcile_id, "known_at": entry_known,
                               "positions": {instrument: side},
                               "open_order_ids": (stop_client,),
                               "open_orders_complete": True,
                               "execution_history_complete": True,
                               "evidence_version": evidence}, priority=42)

            exit = outcome.exit
            if exit is not None and exit.at < entry_at:
                raise ContractError("exit occurrence precedes the actual entry occurrence")
            if exit is not None and outcome.exit_reason == "stop" and _confirmed(exit):
                exit_exec = _execution_id(manifest, exit, "exit")
                stop_known = exit.at + self.timing.broker_report_ns
                stop_fill_id = _event_id(self.plan_id, "stop", "fill")
                self._add(events, journal="broker", key=f"broker:{stop_fill_id}", event_id=stop_fill_id,
                          event_at=exit.at, known_at=stop_known,
                          payload=BrokerEvent(stop_fill_id, stop_client, "fill", exit.at, stop_known,
                                              evidence, exit_exec, 1, exit.price_ticks,
                                              exit.reason or "confirmed protective stop fill"), priority=23)
                exit_fill = TradingFill(exit_exec, instrument, manifest["trading_date"], exit.at,
                                        -side, exit.price_ticks,
                                        self.accounting.fees.fee(self.accounting.terms[instrument].root),
                                        self.accounting.fees.version, manifest["source_version"])
                self._add(events, journal="fill", key=f"fill:{exit_exec}", event_id=f"fill:{exit_exec}",
                          event_at=exit.at, known_at=stop_known, payload=exit_fill, priority=31)
                self._add_reconciliation(events, outcome=outcome, known_at=outcome.position_known_flat_at,
                                         instrument=instrument, evidence=evidence, plan_id=self.plan_id,
                                         minimum_known_at=stop_known, priority=41)
            elif exit is not None and _confirmed(exit):
                # A local target or boundary exit is legal only after the
                # explicit stop-cancel/position-reconciliation event.
                sent = _outcome_event_at(outcome, "stop_cancel_sent", required=True)
                effective = _outcome_event_at(outcome, "stop_cancel_effective_under_scenario", required=True)
                reconciled = _outcome_event_at(outcome, "broker_cancel_and_position_reconciled_under_scenario", required=True)
                if sent < entry_known or effective < sent or reconciled < effective or exit.at < reconciled:
                    raise ContractError("full exit route has a contradictory cancellation timeline")
                request_id = _event_id(self.plan_id, "stop", "cancel-request")
                self._add(events, journal="broker", key=f"broker:{request_id}", event_id=request_id,
                          event_at=sent, known_at=sent,
                          payload=BrokerEvent(request_id, stop_client, "cancel_requested", sent, sent,
                                              evidence, reason="local target/boundary exit requested"), priority=23)
                cancelled_id = _event_id(self.plan_id, "stop", "cancelled")
                self._add(events, journal="broker", key=f"broker:{cancelled_id}", event_id=cancelled_id,
                          event_at=effective, known_at=reconciled,
                          payload=BrokerEvent(cancelled_id, stop_client, "cancelled", effective, reconciled,
                                              evidence, reason="broker cancellation and position reconciliation confirmed"), priority=24)
                cancel_truth_id = f"{self.plan_id}:cancel-confirmed"
                self._add(events, journal="reconcile", key=f"reconcile:{cancel_truth_id}",
                          event_id=f"reconcile:{cancel_truth_id}", event_at=reconciled, known_at=reconciled,
                          payload={"id": cancel_truth_id, "known_at": reconciled,
                                   "positions": {instrument: side}, "open_order_ids": (),
                                   "open_orders_complete": True, "execution_history_complete": True,
                                   "evidence_version": evidence}, priority=40)
                exit_client = f"{self.plan_id}:full-exit"
                self._add(events, journal="order", key=f"order:{exit_client}", event_id=f"submit:{exit_client}",
                          event_at=reconciled, known_at=reconciled,
                          payload=OrderSpec(exit_client, self.order_ledger.account_id, instrument, -side, 1,
                                            "full_exit", "market", None, reconciled, expiry, authorization,
                                            None, entry_client), priority=45)
                exit_exec = _execution_id(manifest, exit, "exit")
                exit_fill_id = _event_id(self.plan_id, "exit", "fill")
                if outcome.position_known_flat_at is None:
                    raise ContractError("confirmed full exit must carry a known-flat clock")
                if outcome.position_known_flat_at < exit.at:
                    raise ContractError("known-flat clock precedes the full-exit occurrence")
                exit_ack_id = _event_id(self.plan_id, "exit", "ack")
                self._add(events, journal="broker", key=f"broker:{exit_ack_id}", event_id=exit_ack_id,
                          event_at=exit.at, known_at=outcome.position_known_flat_at,
                          payload=BrokerEvent(exit_ack_id, exit_client, "acknowledged", exit.at,
                                              outcome.position_known_flat_at, evidence,
                                              reason="full exit accepted after reconciliation"), priority=60)
                self._add(events, journal="broker", key=f"broker:{exit_fill_id}", event_id=exit_fill_id,
                          event_at=exit.at, known_at=outcome.position_known_flat_at,
                          payload=BrokerEvent(exit_fill_id, exit_client, "fill", exit.at,
                                              outcome.position_known_flat_at, evidence, exit_exec, 1,
                                              exit.price_ticks, exit.reason or "confirmed full exit fill"), priority=61)
                exit_fill = TradingFill(exit_exec, instrument, manifest["trading_date"], exit.at,
                                        -side, exit.price_ticks,
                                        self.accounting.fees.fee(self.accounting.terms[instrument].root),
                                        self.accounting.fees.version, manifest["source_version"])
                self._add(events, journal="fill", key=f"fill:{exit_exec}", event_id=f"fill:{exit_exec}",
                          event_at=exit.at, known_at=outcome.position_known_flat_at,
                          payload=exit_fill, priority=62)
                self._add_reconciliation(events, outcome=outcome,
                                         known_at=outcome.position_known_flat_at,
                                         instrument=instrument, evidence=evidence, plan_id=self.plan_id,
                                         minimum_known_at=outcome.position_known_flat_at, priority=70)
            else:
                # Unknown exit evidence never becomes a fill or a synthetic
                # flat reconciliation.  Preserve the local cancel request and
                # the uncertainty observation, if supplied by the outcome.
                sent = _outcome_event_at(outcome, "stop_cancel_sent")
                if sent is not None:
                    if sent < entry_known:
                        raise ContractError("cancel request precedes protective-stop activation")
                    request_id = _event_id(self.plan_id, "stop", "cancel-request")
                    self._add(events, journal="broker", key=f"broker:{request_id}", event_id=request_id,
                              event_at=sent, known_at=sent,
                              payload=BrokerEvent(request_id, stop_client, "cancel_requested", sent, sent,
                                                  evidence, reason="cancel request without confirmed flat state"), priority=23)
                if exit is not None:
                    uncertain_id = _event_id(self.plan_id, "stop", "uncertain")
                    uncertain_at = exit.at
                    if uncertain_at < entry_known:
                        raise ContractError("uncertain exit precedes protective-stop activation")
                    uncertain_known = uncertain_at + self.timing.broker_report_ns
                    self._add(events, journal="broker", key=f"broker:{uncertain_id}", event_id=uncertain_id,
                              event_at=uncertain_at, known_at=uncertain_known,
                              payload=BrokerEvent(uncertain_id, stop_client, "timeout", uncertain_at,
                                                  uncertain_known, evidence,
                                                  reason=exit.reason or outcome.exit_reason or "uncertain exit"), priority=23)

        if self.finalize_day:
            status, status_at, status_evidence = _day_status(day_status, manifest=manifest,
                outcome=outcome, uncertain=(not _confirmed(outcome.entry) or outcome.exit is None
                                            or not _confirmed(outcome.exit) or not outcome.observation_complete))
            status_known = _attr(day_status, "known_at", default=None) if day_status is not None else None
            if status_known is None:
                status_known = max((event.known_at for event in events), default=status_at)
            timestamp(status_known)
            actual_fact_known = max((event.known_at for event in events), default=status_at)
            if status_known < actual_fact_known:
                raise ContractError("final day status is known before all scheduled account facts")
            self._add(events, journal="day", key=f"day:{manifest['trading_date']}:final",
                      event_id=f"day:{manifest['trading_date']}:final", event_at=status_at,
                      known_at=status_known,
                      payload=(manifest["trading_date"], status_at, status, status_evidence), priority=80)
        events.sort(key=lambda event: (event.known_at, event.priority, event.event_at, event.id))
        self._validate_schedule(events)
        return tuple(events)

    def _add_reconciliation(self, events: list[ScheduledReplayEvent], *, outcome: BracketOutcome,
                            known_at: int | None, instrument: str, evidence: str,
                            plan_id: str, minimum_known_at: int, priority: int) -> None:
        if known_at is None:
            raise ContractError("confirmed exit must carry a known-flat clock")
        timestamp(known_at)
        if known_at < minimum_known_at:
            raise ContractError("known-flat clock precedes the broker fill report")
        reconcile_id = f"{plan_id}:flat"
        self._add(events, journal="reconcile", key=f"reconcile:{reconcile_id}",
                  event_id=f"reconcile:{reconcile_id}", event_at=known_at, known_at=known_at,
                  payload={"id": reconcile_id, "known_at": known_at, "positions": {},
                           "open_order_ids": (), "open_orders_complete": True,
                           "execution_history_complete": True, "evidence_version": evidence},
                  priority=priority)

    def _validate_schedule(self, events: list[ScheduledReplayEvent]) -> None:
        last_known = None
        for event in events:
            if last_known is not None and event.known_at < last_known:
                raise ContractError("scheduled replay known clock regressed")
            last_known = event.known_at
        # Validate dependencies at their true clocks rather than repairing a
        # bad timeline with max(clock, event_at).
        order_submits = {event.payload.client_id: event for event in events
                         if event.journal == "order"}
        actual_fact_known = max((event.known_at for event in events if event.journal != "day"), default=None)
        for event in events:
            if event.journal == "order" and event.payload.role != "entry":
                parent = order_submits.get(event.payload.parent_id)
                if parent is None or event.payload.submitted_at < parent.payload.submitted_at:
                    raise ContractError("contingent order submission precedes its parent entry")
            if event.journal == "broker":
                if event.payload.known_at < event.payload.event_at:
                    raise ContractError("broker observation known clock precedes its event clock")
            if event.journal == "day" and actual_fact_known is not None and event.known_at < actual_fact_known:
                raise ContractError("final day status is known before all scheduled account facts")

    def _apply(self, event: ScheduledReplayEvent) -> None:
        existing = self._existing(event)
        if existing is not None:
            expected_kind, expected_payload = self._expected_journal_entry(event)
            if existing["kind"] != expected_kind or digest(existing["payload"]) != digest(expected_payload):
                raise IntegrityError(f"replay idempotency key {event.key} has contradictory durable content")
            return
        if event.journal == "order":
            self.order_ledger.submit(event.payload)
        elif event.journal == "broker":
            self.order_ledger.observe(event.payload)
        elif event.journal == "fill":
            self.accounting.fill(event.payload)
        elif event.journal == "reconcile":
            self.order_ledger.reconcile(**event.payload)
        elif event.journal == "day":
            trading_date, at, status, evidence = event.payload
            self.accounting.day_status(trading_date=trading_date, at=at,
                                       status=status, evidence_version=evidence)
        else:  # pragma: no cover - ScheduledReplayEvent validates the union.
            raise ContractError("unsupported scheduled replay event")

    def advance(self, cut: int) -> E0LedgerReceipt:
        """Publish all facts whose known clocks are no later than ``cut``."""

        timestamp(cut)
        if self._last_cut is not None and cut < self._last_cut:
            # A restart may replay a stale wall-clock cut.  It is harmless only
            # when every event due by that cut is already durable; never use a
            # lower cut to move the cursor or to publish a missing fact.
            if any(event.known_at <= cut and not self._recorded(event) for event in self._events):
                raise ContractError("E0 replay cut moved backward with unseen due events")
            return self._receipt()
        for event in self._events:
            if event.known_at > cut:
                break
            self._apply(event)
        self._last_cut = cut
        return self._receipt()

    def _receipt(self) -> E0LedgerReceipt:
        order_events = self.order_ledger.journal.read()
        accounting_events = self.accounting.journal.read()
        state = self.order_ledger.state()
        report = self.accounting.report()
        submissions = tuple(event["payload"]["spec"]["client_id"] for event in order_events
                            if event["kind"] == "order_submitted")
        broker_events = tuple(event["payload"]["event"]["event_id"] for event in order_events
                              if event["kind"] == "broker_event")
        executions = tuple(state["executions"])
        fills: list[TradingFill] = []
        for event in accounting_events:
            if event["kind"] != "trading_fill":
                continue
            payload = dict(event["payload"])
            payload["fee"] = Decimal(payload["fee"])
            fills.append(TradingFill(**payload))
        pending = self.pending
        days = report.get("days", {})
        day_status = days.get(self.manifest["trading_date"], {}).get("status", "pending")
        final_uncertain = (not _confirmed(self.outcome.entry) or self.outcome.exit is None or
                           not _confirmed(self.outcome.exit) or not self.outcome.observation_complete)
        uncertain = bool(pending) or final_uncertain
        status = "pending" if pending else ("uncertain" if uncertain else
                                              "admitted" if day_status == "complete" else day_status)
        receipt = E0LedgerReceipt(status, submissions, broker_events, executions,
                                  tuple(fills), day_status, report, uncertain,
                                  self.manifest["source_version"], "")
        object.__setattr__(receipt, "version", digest(receipt))
        return receipt

    @classmethod
    def reopen(cls, checkpoint, *, outcome: BracketOutcome, order_ledger: OrderLedger,
               accounting: AccountingLedger, scenario_manifest=None,
               timing: OrderTiming, venue_path: VenuePath, fill_scenario: FillScenario,
               day_status=None, finalize_day: bool = True):
        """Reopen a previously checkpointed replay against the same journals."""

        return cls.restore(checkpoint=checkpoint, outcome=outcome,
                           order_ledger=order_ledger, accounting=accounting,
                           scenario_manifest=scenario_manifest, timing=timing,
                           venue_path=venue_path, fill_scenario=fill_scenario,
                           day_status=day_status, finalize_day=finalize_day)


def append_e0_outcome(*, outcome: BracketOutcome, order_ledger: OrderLedger,
                      accounting: AccountingLedger, timing: OrderTiming,
                      venue_path: VenuePath, fill_scenario: FillScenario,
                      day_status=None, scenario_manifest=None,
                      finalize_day: bool = True) -> E0LedgerReceipt:
    """Drain :class:`E0OutcomeReplay` through its final known clock.

    Causal publication requires the same explicit frozen timing assumptions
    used to create the outcome; an outcome's timing digest is not enough to
    reconstruct broker-report or cancellation clocks.
    """

    replay = E0OutcomeReplay(outcome=outcome, order_ledger=order_ledger,
                             accounting=accounting, scenario_manifest=scenario_manifest,
                             timing=timing, venue_path=venue_path,
                             fill_scenario=fill_scenario, day_status=day_status,
                             finalize_day=finalize_day)
    return replay.advance(replay.final_cut)


__all__ = [
    "E0Boundary", "Boundary", "E0BracketPolicy", "BracketPolicy", "PlanPolicy",
    "AuthorizedBracket", "E0LedgerReceipt", "ScheduledReplayEvent", "E0OutcomeReplay",
    "authorize_e0_bracket", "append_e0_outcome",
]
