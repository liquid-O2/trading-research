"""E0 parity, first-fault attribution and complete-account quality reports."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from zoneinfo import ZoneInfo

from trading_research.data.events import CanonicalEvent, LatencyScenario
from trading_research.errors import ContractError
from trading_research.execution.accounting import AccountingLedger
from trading_research.execution.costs import FeeSchedule
from trading_research.execution.orders import OrderLedger
from trading_research.execution.replay import BracketOutcome, BracketPlan, OrderTiming, reference_bracket
from trading_research.execution.venue import VenuePath, FillScenario
from trading_research.foundations.units import FuturesTerms
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.protocols import QualityEvidence, scorecard


@dataclass(frozen=True)
class E0Parity:
    full_prefix_hash: str
    deleted_suffix_prefix_hash: str
    restarted_prefix_hash: str
    first_divergent_component: str | None
    component_hashes: tuple
    prefix_payloads: tuple[bytes, bytes, bytes]

    def __post_init__(self):
        order = ("source", "measurement", "object", "decision", "order", "account")
        if (type(self.prefix_payloads) is not tuple or len(self.prefix_payloads) != 3
                or any(type(raw) is not bytes or len(raw) > 4_194_304 for raw in self.prefix_payloads)):
            raise ContractError("parity needs the three actual bounded retained prefix payloads")
        try:
            states = tuple(json.loads(raw) for raw in self.prefix_payloads)
        except (ValueError, UnicodeError) as exc:
            raise ContractError("invalid actual parity state bytes") from exc
        if any(type(state) is not dict or set(state) != set(order) or canonical_json(state) != raw
               for state, raw in zip(states, self.prefix_payloads)):
            raise ContractError("parity states must contain all six canonical component records")
        if any(type(state[component]) is not dict for state in states for component in ("decision", "order", "account")):
            raise ContractError("parity decision/order/account components require their actual state records")
        expected = tuple((component, tuple(digest(state[component]) for state in states)) for component in order)
        first = next((component for component, hashes in expected if len(set(hashes)) > 1), None)
        if (self.component_hashes != expected or self.first_divergent_component != first
                or tuple(hashlib.sha256(raw).hexdigest() for raw in self.prefix_payloads) != (
                    self.full_prefix_hash, self.deleted_suffix_prefix_hash, self.restarted_prefix_hash)):
            raise ContractError("parity hashes or first-divergence report differ from the actual component states")

    @property
    def passed(self):
        return (self.full_prefix_hash == self.deleted_suffix_prefix_hash == self.restarted_prefix_hash
                and self.first_divergent_component is None)

    @property
    def version(self):
        return digest(self)


def compare_e0_prefixes(full, deleted_suffix, restarted):
    """Compare actual serializable component outputs in causal component order."""
    order = ("source", "measurement", "object", "decision", "order", "account")
    if (any(type(value) is not dict or set(value) != set(order)
            for value in (full, deleted_suffix, restarted))):
        raise ContractError("parity requires all six actual component states")
    hashes, first = [], None
    for component in order:
        values = tuple(digest(result[component]) for result in (full, deleted_suffix, restarted))
        hashes.append((component, values))
        if len(set(values)) > 1 and first is None:
            first = component
    return E0Parity(digest(full), digest(deleted_suffix), digest(restarted), first, tuple(hashes),
                    tuple(canonical_json(value) for value in (full, deleted_suffix, restarted)))


def attribute_e0_fault(*, fault_id, baseline_path, changed_path, baseline_fees,
                       changed_fees, baseline_population, changed_population,
                       baseline_outcomes=(), changed_outcomes=()):
    if (type(baseline_path) is not VenuePath or type(changed_path) is not VenuePath
            or type(baseline_fees) is not FeeSchedule or type(changed_fees) is not FeeSchedule
            or not fault_id):
        raise ContractError("fault attribution requires actual source paths and cost schedules")
    if baseline_population != changed_population:
        raise ContractError("source/cost intervention changed the pre-outcome candidate population")
    if baseline_path.version == changed_path.version and baseline_fees.version == changed_fees.version:
        raise ContractError("intervention has no source or cost change")
    first, event, economic = None, None, None
    base_quotes = {q.id: q for q in baseline_path.quotes}
    def source_position(quote):
        return (quote.instrument, quote.event_at, quote.sequence, quote.source_version)
    base_positions = {}
    for quote in baseline_path.quotes:
        base_positions.setdefault(source_position(quote), []).append(quote)
    for quote in changed_path.quotes:
        previous = base_quotes.get(quote.id)
        if previous is None:
            # Canonical IDs bind raw bytes, so changing a flag changes the ID.
            # Match only a unique retained stream position, never row order or
            # a caller-provided symbolic alias.
            matches = base_positions.get(source_position(quote), ())
            if len(matches) == 1:
                previous = matches[0]
        covered = changed_path.covered(quote.event_at)
        if previous and previous.executable and (not quote.book_valid or not covered):
            first, event, economic = "venue_path.coverage", quote.id, "execution_blocked"
            break
        _, reason = changed_path.quote_at(quote.event_at, clock="venue", same_time_ordering="venue_first")
        _, previous_reason = baseline_path.quote_at(quote.event_at, clock="venue", same_time_ordering="venue_first")
        if reason == "same-time source quote ordering is unproved" and previous_reason != reason:
            tied = tuple(q.id for q in changed_path.quotes if q.event_at == quote.event_at)
            first, event, economic = "venue_path.same_time_order", "/".join(tied), "fill_uncertain"
            break
    if first is None and baseline_path.complete_intervals != changed_path.complete_intervals:
        first, economic = "venue_path.coverage", "execution_blocked"
        event = next((q.id for q in changed_path.quotes if not changed_path.covered(q.event_at)), None)
    if first is None and baseline_fees.version != changed_fees.version:
        if baseline_path.version != changed_path.version:
            raise ContractError("a cost-only attribution cannot also change the source path")
        if (not baseline_outcomes or len(baseline_outcomes) != len(changed_outcomes)
                or any(type(o) is not BracketOutcome or not o.observation_complete
                       or o.net_usd is None for o in (*baseline_outcomes, *changed_outcomes))):
            raise ContractError("fee attribution requires both complete execution replays")
        if tuple(o.net_usd for o in baseline_outcomes) == tuple(o.net_usd for o in changed_outcomes):
            raise ContractError("changed fee scenario did not reach the complete economics")
        def physical(outcome):
            return ((outcome.entry.at, outcome.entry.side, outcome.entry.quantity, outcome.entry.price_ticks,
                     outcome.entry.source_event_id),
                    (outcome.exit.at, outcome.exit.side, outcome.exit.quantity, outcome.exit.price_ticks,
                     outcome.exit.source_event_id), outcome.gross_usd, outcome.exit_reason)
        if tuple(map(physical, baseline_outcomes)) != tuple(map(physical, changed_outcomes)):
            raise ContractError("cost-only comparison changed matched fills or gross economics")
        root = next(iter(dict(baseline_fees.per_side)))
        delta = changed_fees.fee(root, sides=2) - baseline_fees.fee(root, sides=2)
        if any(b.fees_usd - a.fees_usd != delta or b.net_usd - a.net_usd != -delta
               for a, b in zip(baseline_outcomes, changed_outcomes)):
            raise ContractError("cost effect does not equal the complete itemized fee difference")
        first, economic = "cost_scenario", "net_changed_after_complete_replay"
    if first is None:
        raise ContractError("intervention has no observed fault or completed cost effect")
    result = {"fault_id": fault_id, "first_component": first, "first_event": event,
        "candidate_count_delta": 0, "economic_effect": economic,
        "population_hash": digest(baseline_population), "baseline_source": baseline_path.version,
        "changed_source": changed_path.version, "baseline_fee": baseline_fees.version,
        "changed_fee": changed_fees.version, "untraded_rows_preserved": True}
    return {**result, "version": digest(result)}


@dataclass(frozen=True)
class EconomicInterval:
    population_hash: str
    lower: Fraction | None
    upper: Fraction | None
    method: str
    evidence_version: str

    def __post_init__(self):
        if (not all((self.population_hash, self.method, self.evidence_version))
                or (self.lower is None) != (self.upper is None)
                or self.lower is not None and (type(self.lower) is not Fraction
                    or type(self.upper) is not Fraction or self.lower > self.upper)):
            raise ContractError("bounded economic uncertainty needs its actual population and evidence")


@dataclass(frozen=True)
class E0NativeExecutionSource:
    """Retained native inputs sufficient to reproduce the public MBP bridge."""
    canonical_events: tuple[CanonicalEvent, ...]
    selected_day: object
    coverage: object
    latency_scenario: LatencyScenario
    tick_size: Decimal
    recovery_certificates: tuple = ()
    market_state: str = "continuous"

    def __post_init__(self):
        from trading_research.experiments.e0.admission import E0DayAdmission
        from trading_research.foundations.instruments import InstrumentDefinition
        if (type(self.canonical_events) is not tuple or not self.canonical_events
                or len(self.canonical_events) > 100_000
                or any(type(event) is not CanonicalEvent for event in self.canonical_events)
                or type(self.selected_day) is not E0DayAdmission
                or type(self.selected_day.selected_definition) is not InstrumentDefinition
                or type(self.latency_scenario) is not LatencyScenario
                or type(self.tick_size) is not Decimal or not self.tick_size.is_finite() or self.tick_size <= 0
                or type(self.recovery_certificates) is not tuple
                or self.market_state not in ("continuous", "auction", "halted", "closed", "unknown")):
            raise ContractError("execution source needs bounded actual native records and admitted raw identity")

    @property
    def version(self):
        return digest(self)

    def rebuild(self):
        from trading_research.experiments.e0.source_bridge import venue_path_from_mbp
        self.__post_init__()
        return venue_path_from_mbp(canonical_events=self.canonical_events,
            selected_instrument=self.selected_day, coverage=self.coverage,
            recovery_certificates=self.recovery_certificates,
            latency_scenario=self.latency_scenario, tick_size=self.tick_size, market_state=self.market_state)


def _path_values(path):
    return (path.instrument, path.quotes, path.trades, path.complete_intervals, path.coverage_version)


@dataclass(frozen=True)
class E0ExecutionEvidence:
    """Complete reproducible source/geometry evidence for one account bracket."""
    trading_date: str
    population_hash: str
    candidate: object
    path: VenuePath
    plan: BracketPlan
    terms: FuturesTerms
    fees: FeeSchedule
    fill_scenario: FillScenario
    timing: OrderTiming
    outcome: BracketOutcome
    prior_day_net: Decimal = Decimal(0)
    daily_budget: Decimal = Decimal(1000)
    native_source: E0NativeExecutionSource | None = None

    def __post_init__(self):
        from trading_research.experiments.e0.observations import E0CandidateRow
        if (type(self.candidate) is not E0CandidateRow or type(self.path) is not VenuePath
                or type(self.plan) is not BracketPlan or type(self.terms) is not FuturesTerms
                or type(self.fees) is not FeeSchedule or type(self.fill_scenario) is not FillScenario
                or type(self.timing) is not OrderTiming or type(self.outcome) is not BracketOutcome
                or type(self.native_source) is not E0NativeExecutionSource
                or type(self.prior_day_net) is not Decimal or not self.prior_day_net.is_finite()
                or type(self.daily_budget) is not Decimal or self.daily_budget != Decimal(1000)
                or not self.population_hash):
            raise ContractError("execution evidence needs the actual typed source, plan, costs and replay")
        self.candidate.__post_init__(); self.plan.__post_init__()
        self.terms.__post_init__(); self.fees.__post_init__(); self.fill_scenario.__post_init__()
        self.timing.__post_init__()
        self.native_source.__post_init__()
        row, plan = self.candidate, self.plan
        definition = self.native_source.selected_day.selected_definition
        day = datetime.fromtimestamp(row.cut // 1_000_000_000, ZoneInfo("America/New_York")).date().isoformat()
        boundary_days = tuple(datetime.fromtimestamp(at // 1_000_000_000,
            ZoneInfo("America/New_York")).date().isoformat() for at in (
                plan.flatten_send_at, plan.required_flat_at, self.outcome.entry.at,
                self.outcome.exit.at if self.outcome.exit is not None else self.outcome.entry.at))
        if (day != self.trading_date or row.cut % 60_000_000_000
                or self.native_source.selected_day.day.isoformat() != day
                or row.contact is None or row.contact.at != row.cut
                or row.contact.approach is None
                or (row.contact.object_id, row.contact.object_version) != (row.object_id, row.object_version)
                or any(boundary_day != day for boundary_day in boundary_days)
                or (plan.instrument, plan.side, plan.decision_at) != (row.instrument, row.side, row.cut)
                or self.path.instrument != plan.instrument or plan.horizon_end != row.cut + 900_000_000_000
                or self.native_source.tick_size != self.terms.tick_size
                or (self.terms.root, self.terms.tick_size, self.terms.usd_per_point, self.terms.definition_version) != (
                    definition.key.underlying, definition.tick_size, definition.multiplier, definition.key.definition_version)
                or self.fill_scenario.fee_version != self.fees.version
                or self.fill_scenario.quote_coverage_version != self.path.coverage_version
                or self.outcome.plan_version != plan.version):
            raise ContractError("execution replay changed its completed-minute contact, original horizon or source")
        quote, _ = self.path.quote_at(row.cut, clock="strategy")
        if (quote is None or Fraction(quote.bid + quote.ask, 2) != row.contact.price
                or plan.worst_entry_ticks != (quote.ask + self.fill_scenario.impact_ticks if row.side == 1
                                             else quote.bid - self.fill_scenario.impact_ticks)):
            raise ContractError("execution entry bound differs from its actual causal native quote")
        for fill in (self.outcome.entry, self.outcome.exit):
            if fill is not None and fill != self.path.marketable(order_id=fill.order_id, side=fill.side,
                    arrival_at=fill.at, scenario=self.fill_scenario):
                raise ContractError("execution fill differs from its side-correct source quote and impact")

    @property
    def version(self):
        return digest((self.trading_date, self.population_hash, self.candidate, self.path.version,
            self.plan, self.terms, self.fees.version, self.fill_scenario, self.timing,
            self.outcome, self.prior_day_net, self.daily_budget, self.native_source.version))

    def validate_replay(self):
        self.__post_init__()
        return self._compare_replay(self.native_source.rebuild())

    def _compare_replay(self, native_path):
        if _path_values(native_path) != _path_values(self.path):
            raise ContractError("execution path differs from the actual retained native bridge inputs")
        actual = reference_bracket(native_path, self.plan, terms=self.terms, fees=self.fees,
            fill_scenario=self.fill_scenario, timing=self.timing,
            prior_day_net=self.prior_day_net, daily_budget=self.daily_budget)
        if actual != self.outcome:
            raise ContractError("economic outcome differs from the complete actual native bracket replay")
        return actual


def _economic_join(accounting, orders, paths, outcomes, populations, execution_evidence):
    """Reconcile actual executions through the source, order and cash ports."""
    account = accounting.report(); order = orders.state()
    if (type(paths) is not tuple or any(type(path) is not VenuePath for path in paths)
            or type(outcomes) is not tuple
            or type(execution_evidence) is not tuple or len(execution_evidence) != len(outcomes)
            or any(type(item) is not E0ExecutionEvidence for item in execution_evidence)):
        return False
    population_dates = tuple(sorted({datetime.fromtimestamp(row.cut // 1_000_000_000,
        ZoneInfo("America/New_York")).date().isoformat() for population in populations for row in population}))
    if tuple(accounting.dates) != population_dates:
        return False
    rows = {(population.population_hash, row.decision_set_id, row.id, row.cut): row
            for population in populations for row in population}
    paths_by_version = {path.version: path for path in paths}
    day_net = {day: Decimal(0) for day in accounting.dates}
    last_flat = None
    admitted = []
    seen_plans = set()
    verified_sources = {}
    for item, outcome in zip(execution_evidence, outcomes):
        row, plan = item.candidate, item.plan
        if (rows.get((item.population_hash, row.decision_set_id, row.id, row.cut)) != row
                or item.path.version not in paths_by_version or plan.id in seen_plans
                or item.terms != accounting.terms.get(plan.instrument)
                or item.fees.version != accounting.fees.version
                or item.prior_day_net != day_net.get(item.trading_date)
                or last_flat is not None and plan.decision_at < last_flat
                or item.outcome != outcome):
            return False
        try:
            item.__post_init__()
            source_id = item.native_source.version
            if source_id not in verified_sources:
                verified_sources[source_id] = item.native_source.rebuild()
            actual = item._compare_replay(verified_sources[source_id])
        except ContractError:
            return False
        if actual.net_usd is None or actual.position_known_flat_at is None:
            return False
        day_net[item.trading_date] += actual.net_usd
        last_flat = actual.position_known_flat_at
        seen_plans.add(plan.id)
        entry = order["orders"].get(plan.id + ":entry")
        stop = order["orders"].get(plan.id + ":protective-stop")
        if (entry is None or stop is None
                or entry["spec"].authorization_version != plan.version
                or entry["spec"].submitted_at != plan.decision_at
                or entry["spec"].side != plan.side
                or stop["spec"].authorization_version != plan.version
                or stop["spec"].price_ticks != plan.stop_ticks
                or stop["spec"].parent_id != plan.id + ":entry"):
            return False
        admitted.append(item)
    fills = tuple(event["payload"] for event in accounting.journal.read() if event["kind"] == "trading_fill")
    if {fill["execution_id"] for fill in fills} != set(order["executions"]):
        return False
    for fill in fills:
        identity = order["executions"][fill["execution_id"]]["identity"]
        if identity[1:] != (fill["instrument"], fill["side"], 1, fill["price_ticks"], fill["at"]):
            return False
        if fill["fee_version"] != accounting.fees.version or Fraction(fill["fee"]) != Fraction(
                accounting.fees.fee(accounting.terms[fill["instrument"]].root)):
            return False
    physical = []
    for item in admitted:
        outcome = item.outcome
        if (type(outcome) is not BracketOutcome or not outcome.observation_complete
                or not outcome.boundary_met or outcome.daily_loss_breach is not False
                or outcome.position_known_flat_at is None or outcome.net_usd is None
                or not outcome.entry.quantity or outcome.exit is None or not outcome.exit.quantity):
            return False
        matches = tuple(path for path in paths if any(q.id == outcome.entry.source_event_id for q in path.quotes)
                        and any(q.id == outcome.exit.source_event_id for q in path.quotes)
                        and path.covered(outcome.entry.at, outcome.exit.at))
        if len(matches) != 1:
            return False
        path = matches[0]
        for fill in (outcome.entry, outcome.exit):
            quote, _ = path.quote_at(fill.at, clock="venue", same_time_ordering="venue_first")
            if quote is None or quote.id != fill.source_event_id or fill.quantity != 1:
                return False
            order_id = item.plan.id + (":entry" if fill is outcome.entry else
                ":protective-stop" if outcome.exit_reason == "stop" else ":full-exit")
            physical.append((order_id, item.trading_date, path.instrument, fill.at, fill.side, fill.price_ticks,
                             path.version))
    actual = tuple(sorted((order["executions"][fill["execution_id"]]["identity"][0], fill["trading_date"],
                          fill["instrument"], fill["at"], fill["side"], fill["price_ticks"], fill["source_version"])
                         for fill in fills))
    if actual != tuple(sorted(physical)):
        return False
    total_gross = sum((Fraction(outcome.gross_usd) for outcome in outcomes), Fraction())
    total_fees = sum((Fraction(outcome.fees_usd) for outcome in outcomes), Fraction())
    return (sum((Fraction(day["gross"]) for day in account["days"].values()), Fraction()) == total_gross
        and sum((Fraction(day["fees"]) for day in account["days"].values()), Fraction()) == total_fees
        and Fraction(account["trading_net"]) == total_gross - total_fees)


def e0_quality_report(*, accounting: AccountingLedger, orders: OrderLedger, fees: FeeSchedule | None,
                      paths: tuple[VenuePath, ...], outcomes: tuple[BracketOutcome, ...],
                      populations: tuple, parity: E0Parity, interval: EconomicInterval,
                      prediction_evidence: QualityEvidence, target=Fraction(2000),
                      execution_evidence: tuple[E0ExecutionEvidence, ...] = ()):
    from trading_research.experiments.e0.observations import E0Population
    if not populations or any(type(population) is not E0Population for population in populations):
        raise ContractError("V04 requires the actual complete decision populations")
    population_hash = digest(tuple(population.population_hash for population in populations))
    if (type(accounting) is not AccountingLedger or type(orders) is not OrderLedger
            or type(parity) is not E0Parity or type(interval) is not EconomicInterval
            or type(prediction_evidence) is not QualityEvidence
            or prediction_evidence.dimension != "prediction" or type(target) is not Fraction
            or interval.population_hash != population_hash):
        raise ContractError("V04 needs actual account/order/parity/population-bound uncertainty evidence")
    account = accounting.report()
    order_state = orders.state()
    parity.__post_init__()
    parity_state = json.loads(parity.prefix_payloads[0])
    state_bound = (parity_state["decision"].get("population_hash") == population_hash
        and parity_state["order"].get("journal_head") == digest(orders.journal.read())
        and parity_state["account"].get("report_version") == digest(account))
    mean = account["mean_net_per_eligible_day"]
    gap = None if mean is None else target - mean
    result = {"scope": "synthetic_research_account", "population_hash": population_hash,
        "eligible_day_count": account["eligible_day_count"], "day_statuses": tuple(
            (day, row["status"]) for day, row in account["days"].items()),
        "mean_net_usd": mean, "objective_gap_usd_per_day": gap,
        "trading_net_usd": account["trading_net"], "business_net_cash_usd": account["business_net_cash"],
        "account_version": digest(account), "order_version": digest(order_state),
        "parity_version": parity.version, "interval": interval,
        "execution_evidence_versions": tuple(item.version for item in execution_evidence
            if type(item) is E0ExecutionEvidence),
        "native_source_versions": tuple(dict.fromkeys(item.native_source.version
            for item in execution_evidence if type(item) is E0ExecutionEvidence
            and type(item.native_source) is E0NativeExecutionSource)),
        "economic_gate_inputs_complete": False, "program_complete": False}
    reason = None
    if not parity.passed or not state_bound:
        decision, owner, next_evidence = "no_go", "integrity", "repair parity defect before any economic interpretation"
    elif fees is None:
        decision, owner, next_evidence = "no_go", "economic_data", "admit complete fee schedule"
        reason = "itemized positive fee categories are incomplete; economic result is unavailable"
        result.update(mean_net_usd=None, objective_gap_usd_per_day=None, trading_net_usd=None)
    else:
        fees.__post_init__()
        # A declared favorable score cannot waive actual execution/account closure.
        complete = (account["complete"] and account["account"] == orders.account_id
            and accounting.fees.version == fees.version and order_state["reconciled"]
            and not order_state["live_orders"] and not any(order_state["positions"].values())
            and not order_state["incidents"] and bool(paths)
            and _economic_join(accounting, orders, paths, outcomes, populations, execution_evidence)
            and all(type(path) is VenuePath and bool(path.complete_intervals) for path in paths)
            and all(type(outcome) is BracketOutcome and outcome.observation_complete
                    and outcome.boundary_met and outcome.position_known_flat_at is not None
                    and outcome.daily_loss_breach is False for outcome in outcomes))
        if not complete:
            decision, owner, next_evidence = "no_go", "economic_data", "complete source, order, risk and account reconciliation"
        else:
            result["economic_gate_inputs_complete"] = True
            if interval.lower is not None and not interval.lower <= mean <= interval.upper:
                raise ContractError("economic interval does not contain its actual account mean")
            if (interval.lower is None or prediction_evidence.status != "supported"
                    or interval.lower <= target <= interval.upper):
                decision, owner = "inconclusive", "uncertainty_or_data"
                next_evidence = "more complete dependent blocks and verified arrival/fee evidence"
                result["interval_crosses_target"] = interval.lower is not None and interval.lower <= target <= interval.upper
            elif interval.lower > target:
                decision, owner, next_evidence = "supported_at_declared_uncertainty", "none", None
            else:
                decision, owner = "not_met", "economic_policy"
                next_evidence = "matched economic improvement or revise target in development"
    result.update(decision=decision, owner=owner, next_evidence=next_evidence)
    if reason is not None:
        result["reason"] = reason
    evidence_hash = digest(result)
    integrity = "supported" if parity.passed and state_bound else "not_met"
    economics = ("supported" if decision == "supported_at_declared_uncertainty" else
                 "not_met" if decision in ("not_met", "no_go") else "inconclusive")
    tracks = tuple(QualityEvidence(dimension, status, (evidence_hash,), why) for dimension, status, why in (
        ("semantics", integrity, "actual source-to-account fixture reconciliation"),
        ("causality", integrity, "actual suffix deletion and restart parity"),
        ("incremental_information", "inconclusive", "matched richer-model comparisons remain separate"),
        ("decisions", economics, "complete sequential one-account result"),
        ("survival", economics, "actual marked loss and boundary outcomes"))) + (prediction_evidence,)
    result["quality_tracks"] = scorecard(unit_id="E0", role="predictor", evidence=tracks,
        selected_version=None, objective_mean_per_day=None if result["mean_net_usd"] is None else float(result["mean_net_usd"]),
        objective_target=float(target))
    return {**result, "version": digest(result)}
