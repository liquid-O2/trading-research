"""Bounded E0 common-population simulation with chronological account state.

The entry point accepts retained native source records and admitted context.
All output is simulated; it has no network or broker dispatch adapter.
"""

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import resource
import stat
import time
from zoneinfo import ZoneInfo

from trading_research.data.events import CanonicalEvent, LatencyScenario
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.execution.accounting import AccountingLedger
from trading_research.execution.costs import FeeSchedule
from trading_research.execution.orders import OrderLedger
from trading_research.execution.replay import BracketOutcome, BracketPlan, OrderTiming
from trading_research.execution.venue import Fill, FillScenario, VenuePath
from trading_research.experiments.e0.account_bridge import AuthorizedBracket, E0Boundary, E0BracketPolicy, authorize_e0_bracket
from trading_research.experiments.e0.admission import E0OperationalBinding
from trading_research.experiments.e0.candidates import numeric_features, stop_distance
from trading_research.experiments.e0.learning import FEATURE_COLUMNS, E0BracketPrediction, E0BracketRouter
from trading_research.experiments.e0.observations import (
    build_e0_decision_population, label_e0_candidate, label_e0_price_path,
)
from trading_research.experiments.e0.policy import (
    E0ActionValue, E0CommittedPredictionEvidence, E0DecisionSet, E0RuleSelection,
    TargetPolicy, score_and_decide_e0,
)
from trading_research.experiments.e0.source_bridge import E0FrozenContext, venue_path_from_mbp
from trading_research.foundations.contracts import Decision
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import Ticks
from trading_research.operations.artifacts import ArtifactStore, artifact_ref, canonical_json, digest, publish_new
from trading_research.operations.journal import Journal
from trading_research.operations.provenance import InputValue, cache_key, compatible_checkpoint
from trading_research.operations.trials import TrialRegistry
from trading_research.risk.reservations import AtomicEntryGate, CriticalSnapshot, EntryIntent, Reservation


NS = 1_000_000_000
MINUTE = 60 * NS
BRANCHES = ("always_flat", "rule", "frequency", "logistic")
OBJECT_TYPES = ("06_09:low", "06_09:quarter_1", "06_09:eq", "06_09:quarter_3", "06_09:high",
                "06_09:lower_half_extension", "06_09:lower_full_extension",
                "06_09:upper_half_extension", "06_09:upper_full_extension",
                "prior_rth:low", "prior_rth:high", "prior_rth:open", "prior_rth:close")


@dataclass(frozen=True)
class E0Scenario:
    id: str
    feed_lag_ms: int
    outbound_delay_ms: int
    impact_ticks: int

    def __post_init__(self):
        if not self.id or any(type(v) is not int or v < 0 for v in (
                self.feed_lag_ms, self.outbound_delay_ms, self.impact_ticks)):
            raise ContractError("exact explicit source/routing/impact assumptions required")

    @property
    def version(self):
        return digest(self)

    @property
    def timing(self):
        return OrderTiming("E0-reference-route:" + self.id, self.outbound_delay_ms * 1_000_000,
                           250_000_000, 0, "trigger_first")


SCENARIOS = tuple(E0Scenario(*row) for row in (
    ("baseline", 250, 250, 1), ("feed-0", 0, 250, 1), ("feed-1000", 1000, 250, 1),
    ("outbound-50", 250, 50, 1), ("outbound-1000", 250, 1000, 1),
    ("impact-0", 250, 250, 0), ("impact-2", 250, 250, 2),
    ("joint-1000-1000-2", 1000, 1000, 2)))


@dataclass(frozen=True)
class E0MinutePrice:
    end_at: int
    known_at: int
    ticks: Fraction
    source_version: str

    def __post_init__(self):
        timestamp(self.end_at); timestamp(self.known_at)
        if (self.known_at < self.end_at or type(self.ticks) is not Fraction
                or self.ticks <= 0 or not self.source_version):
            raise ContractError("completed minute observation requires actual source and availability")


@dataclass(frozen=True)
class E0RunDay:
    day: str
    cuts: tuple[int, ...]
    context: E0FrozenContext
    operational: E0OperationalBinding
    native_events: tuple[CanonicalEvent, ...]
    coverage: dict
    minute_history: tuple[E0MinutePrice, ...]
    recovery_certificates: tuple = ()
    market_state: str = "unknown"

    def __post_init__(self):
        calendar_day = date.fromisoformat(self.day)
        if (type(self.context) is not E0FrozenContext or type(self.operational) is not E0OperationalBinding
                or calendar_day != self.operational.day or not self.cuts
                or tuple(sorted(set(self.cuts))) != self.cuts
                or type(self.native_events) is not tuple or not self.native_events
                or any(type(event) is not CanonicalEvent for event in self.native_events)
                or type(self.minute_history) is not tuple
                or any(type(row) is not E0MinutePrice for row in self.minute_history)
                or self.market_state not in ("continuous", "auction", "halted", "closed", "unknown")):
            raise ContractError("E0 day requires immutable admitted source, calendar and minute population")
        for cut in self.cuts:
            timestamp(cut)
            if datetime.fromtimestamp(cut / NS, ZoneInfo("America/New_York")).date() != calendar_day:
                raise ContractError("decision cut is outside the declared New York business date")
            if not self.operational.window["entry_start"] <= cut <= self.operational.window["entry_end"]:
                raise ContractError("decision cut lies outside the registered E0 entry window")
        if self.context.selected_day.day != calendar_day:
            raise ContractError("raw universe admission belongs to another day")

    @property
    def version(self):
        return digest(self)


def e0_feature_values(day: E0RunDay, row, *, midpoint, cut, source_quote=None, scenario=SCENARIOS[0]):
    """Build the full ten-column feature vector from completed source windows."""
    if row.side not in (-1, 1) or row.cut != cut:
        raise ContractError("feature query must be an actual object-side decision row")
    if scenario not in SCENARIOS:
        raise ContractError("feature source must use a registered availability scenario")
    source_path = venue_path_from_mbp(canonical_events=day.native_events,
        selected_instrument=day.context.selected_day, coverage=day.coverage,
        recovery_certificates=day.recovery_certificates,
        latency_scenario=LatencyScenario(scenario.id, "event", scenario.feed_lag_ms * 1_000_000, 0),
        tick_size=day.operational.terms.tick_size, market_state=day.market_state)
    actual_quote, reason = source_path.quote_at(cut, clock="strategy")
    if actual_quote is None:
        raise DependencyUnavailable("causal feature quote unavailable: " + reason)
    if ((source_quote is not None and source_quote != actual_quote)
            or midpoint != Fraction(actual_quote.bid + actual_quote.ask, 2)):
        raise ContractError("feature midpoint or source quote differs from the actual available native book")
    native_quote = next(event for event in day.native_events if event.id == actual_quote.id)
    objects = {obj.id: obj for obj in day.context.objects}
    obj = objects[row.object_id]
    prior = tuple(sorted((bar for bar in day.minute_history if bar.end_at < cut and bar.known_at <= cut),
                         key=lambda bar: bar.end_at))
    if len(prior) < 31:
        raise DependencyUnavailable("full E0 features require 31 completed prices for 30 changes")
    prior = prior[-31:]
    if prior[-1].end_at != cut - MINUTE:
        raise DependencyUnavailable("E0 feature history is missing the last completed minute before the cut")
    if any(b.end_at - a.end_at != MINUTE for a, b in zip(prior, prior[1:])):
        raise DependencyUnavailable("E0 feature history has a missing completed minute")
    prices = tuple(bar.ticks for bar in prior)
    ret = prices[-1] - prices[-6]
    variation = sum(((b - a) ** 2 for a, b in zip(prices, prices[1:])), Fraction())
    local = datetime.fromtimestamp(cut / NS, ZoneInfo("America/New_York"))
    minute = local.hour * 60 + local.minute - (9 * 60 + 30)
    features = numeric_features(obj=obj, side=row.side, cut=cut, price=midpoint,
        range_06_09=day.context.range_06_09, prior_rth=day.context.prior_rth,
        five_minute_return=ret, thirty_minute_realized_variation=variation,
        history_known_at=max(bar.known_at for bar in prior), minute_of_session=minute,
        remaining_minutes=Fraction(day.operational.window["flatten_send_at"] - cut, MINUTE),
        object_type_code=OBJECT_TYPES.index(obj.type))
    version = digest({"object": obj.version, "ranges": (day.context.range_06_09.version,
        day.context.prior_rth.version), "history": prior, "midpoint": midpoint, "cut": cut,
        "native_quote": native_quote})
    return tuple(InputValue(column, version, cut, canonical_json(features[column])) for column in FEATURE_COLUMNS)


@dataclass(frozen=True)
class E0RunManifest:
    id: str
    scope: str
    eligible_dates: tuple[str, ...]
    day_versions: tuple[str, ...]
    code_hash: str
    fold_version: str
    model_version: str
    source_hashes: tuple[tuple[str, str], ...]
    fees_version: str
    account_id: str = "synthetic-account-1"
    target_multiples: tuple[int, ...] = (1, 2)
    branches: tuple[str, ...] = BRANCHES
    scenarios: tuple[E0Scenario, ...] = SCENARIOS
    daily_budget_usd: Decimal = Decimal(1000)
    gap_reserve_usd: Decimal = Decimal(20)
    horizon_ns: int = 900 * NS
    maximum_days: int = 160
    maximum_cuts: int = 57600

    def __post_init__(self):
        if (not all((self.id, self.code_hash, self.fold_version, self.model_version, self.fees_version,
                     self.account_id)) or self.scope not in ("synthetic_engineering_two_day_sparse_cut_control",
                                                           "E0_exact")
                or self.target_multiples != (1, 2) or self.branches != BRANCHES or self.scenarios != SCENARIOS
                or self.daily_budget_usd != Decimal(1000) or self.gap_reserve_usd != Decimal(20)
                or self.horizon_ns != 900 * NS or not self.source_hashes
                or len(set(self.eligible_dates)) != len(self.eligible_dates)
                or len(self.eligible_dates) != len(self.day_versions)
                or not 0 < len(self.eligible_dates) <= self.maximum_days
                or type(self.maximum_cuts) is not int or not 1 <= self.maximum_cuts <= 57600):
            raise ContractError("E0 run manifest changed the frozen population, policy, scenarios or resource bound")
        for day in self.eligible_dates:
            date.fromisoformat(day)
        if tuple(sorted(self.eligible_dates)) != self.eligible_dates:
            raise ContractError("E0 dates must retain chronological order")

    @property
    def version(self):
        return digest(self)


def e0_run_inputs(days, router):
    """The six retained input bodies shared by direct replay and bundle I/O."""
    if type(router) is not E0BracketRouter:
        raise ContractError("E0 input verification requires its actual committed model router")
    return {
        "native_sources": tuple(day.native_events for day in days),
        "admitted_contexts": tuple(day.context for day in days),
        "operational_terms": tuple(day.operational for day in days),
        "completed_minutes": tuple(day.minute_history for day in days),
        "source_coverage": tuple(day.coverage for day in days),
        "model_references": tuple((policy, tuple((head.name, head.fit.version,
            tuple((binding.model_id, binding.commit_ref) for binding in head.committed.bindings))
            for head in heads)) for policy, heads in router.policies),
    }


def e0_router_fold_version(router):
    if type(router) is not E0BracketRouter:
        raise ContractError("E0 fold verification requires its actual committed model router")
    return digest(tuple((policy, tuple((head.name, head.fit.stages.version) for head in heads))
                        for policy, heads in router.policies))


def validate_run_inputs(manifest, days, *, predict):
    if type(manifest) is not E0RunManifest or type(days) is not tuple or any(type(day) is not E0RunDay for day in days):
        raise ContractError("typed frozen E0 manifest and day inputs required")
    manifest.__post_init__()
    if (tuple(day.day for day in days) != manifest.eligible_dates
            or tuple(day.version for day in days) != manifest.day_versions
            or sum(len(day.cuts) for day in days) > manifest.maximum_cuts):
        raise ContractError("E0 input source/date/cut population differs from its frozen manifest")
    if any(day.operational.fees.version != manifest.fees_version for day in days):
        raise ContractError("E0 days changed the frozen itemized fee scenario")
    if type(predict) is not E0BracketRouter:
        raise ContractError("typed E0 router required for the complete frozen manifest")
    predict.__post_init__()
    if manifest.model_version != predict.version or manifest.fold_version != e0_router_fold_version(predict):
        raise IntegrityError("E0 model/fold differs from the frozen manifest")
    expected = tuple(sorted((name, digest(value)) for name, value in e0_run_inputs(days, predict).items()))
    if manifest.source_hashes != expected:
        raise IntegrityError("E0 actual typed inputs differ from retained source hashes")
    if manifest.scope == "E0_exact":
        from trading_research.experiments.e0.cohort import freeze_cohort, require_runnable
        cohort = freeze_cohort(tuple(day.context.selected_day.completeness for day in days))
        require_runnable(cohort)
        if tuple(cohort["dates"]) != manifest.eligible_dates:
            raise ContractError("exact E0 dates differ from the first/last completeness-selected cohort")
    return manifest.version


def e0_label_inventory(days, populations, paths, *, multiple, horizon_ns, scenario):
    """Publish future observations separately, after every decision is fixed.

    Background rows remain in the denominator. Object reach/departure and the
    integer-tick price-path control retain separate target definitions; an
    unsupported price coordinate remains explicitly unavailable.
    """
    if multiple not in (1, 2) or horizon_ns != 900 * NS or scenario not in SCENARIOS:
        raise ContractError("label inventory changed the fixed E0 target")
    rows = []
    for day, population, path in zip(days, populations, paths, strict=True):
        sampled = {}
        for cut in day.cuts:
            quote, _ = path.quote_at(cut, clock="strategy")
            sampled[cut] = None if quote is None else Fraction(quote.bid + quote.ask, 2)
        for candidate in population:
            endpoint = candidate.cut + horizon_ns
            common = {"candidate_id": candidate.id, "candidate_version": candidate.version,
                "decision_set_id": candidate.decision_set_id, "date": day.day,
                "cut": candidate.cut, "fixed_end": endpoint, "side": candidate.side,
                "source_path_version": path.version}
            if candidate.side == 0:
                rows.append({**common, "status": "background", "object_label": None,
                    "price_path_label": None, "reason": "complete clock-population background has no object target"})
                continue
            distance = stop_distance(candidate.range_width)
            object_label = label_e0_candidate(candidate_row=candidate, sampled_midpoints=sampled,
                venue_path=path, target_end=endpoint, observation_process="E0-native-fixed-end-v1",
                favorable_distance=Fraction(distance * multiple), adverse_distance=Fraction(distance))
            price_label = None
            price_reason = None
            try:
                price_label = label_e0_price_path(candidate_row=candidate, sampled_midpoints=sampled,
                    venue_path=path, target_end=endpoint, observation_process="E0-native-price-path-v1",
                    up_ticks=distance * (multiple if candidate.side == 1 else 1),
                    down_ticks=distance * (multiple if candidate.side == -1 else 1))
            except DependencyUnavailable as exc:
                price_reason = str(exc)
            except ContractError as exc:
                if str(exc) != "typed integer-tick price-path control cannot round fractional midpoints":
                    raise
                price_reason = str(exc)
            rows.append({**common, "status": object_label.label["status"],
                "object_label": object_label, "price_path_label": price_label,
                "price_path_unavailable_reason": price_reason})
    values = tuple(rows)
    object_rows = tuple(row for row in values if row["side"])
    counts = {"population": len(values), "background": len(values) - len(object_rows),
        "object_side": len(object_rows),
        "contact": sum(row["object_label"].label["reach_status"] == "contact" for row in object_rows),
        "no_contact": sum(row["object_label"].label["reach_status"] == "no_contact" for row in object_rows),
        "censored": sum(row["status"] == "censored" for row in object_rows),
        "ambiguous": sum(row["status"] == "ambiguous" for row in object_rows),
        "unavailable": sum(row["status"] == "unavailable" for row in object_rows),
        "price_path_unavailable": sum(row["price_path_label"] is None for row in object_rows)}
    body = {"schema": "E0CompleteFutureLabelsV1", "role": "post_replay_fixed_end_labels",
        "population_hash": digest(tuple(population.population_hash for population in populations)),
        "scenario_version": scenario.version,
        "source_path_versions": {day.day: path.version for day, path in zip(days, paths, strict=True)},
        "target_multiple": multiple, "rows": values, "counts": counts,
        "used_for_action_selection": False}
    return {**body, "version": digest(body)}


def _read_e0_label_bytes(store, ref):
    """Read at most one declared inventory, without following path aliases."""
    path = store.path(ref).absolute()
    directory = descriptor = None
    try:
        if path.resolve(strict=True) != path:
            raise IntegrityError("E0 label artifact path contains an alias")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        directory = os.open(path.anchor, flags)
        for component in path.parts[1:-1]:
            child = os.open(component, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        # NONBLOCK lets fstat reject a FIFO/device before any read could wait.
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory)
        observed = os.fstat(descriptor)
        if not stat.S_ISREG(observed.st_mode) or observed.st_size != ref.size_bytes:
            raise IntegrityError("E0 label artifact is not a regular file of its declared bounded size")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            raw = stream.read(ref.size_bytes + 1)
        if len(raw) != ref.size_bytes or hashlib.sha256(raw).hexdigest() != ref.sha256:
            raise IntegrityError("E0 label artifact bytes differ from their retained reference")
        return raw
    except OSError as exc:
        raise IntegrityError("E0 label artifact cannot be read through its bounded regular-file path") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if directory is not None:
            os.close(directory)


def load_e0_result_labels(store, result):
    """Resolve the complete, bounded post-replay inventory named by a result."""
    if type(store) is not ArtifactStore or type(result) is not dict:
        raise ContractError("retained E0 labels require an actual artifact store and result")
    ref = artifact_ref(result["label_inventory_artifact"])
    if ref.kind != "E0_complete_future_labels" or not 0 < ref.size_bytes <= 4 * 1024 ** 2:
        raise IntegrityError("E0 label artifact exceeds its declared schema or byte bound")
    value = json.loads(_read_e0_label_bytes(store, ref))
    if (value["schema"] != "E0CompleteFutureLabelsV1"
            or value["population_hash"] != result["population_hash"]
            or value["target_multiple"] != result["target_multiple"]
            or value["scenario_version"] != result["scenario_version"]
            or value["source_path_versions"] != result["source_path_versions"]
            or value["version"] != digest({key: item for key, item in value.items() if key != "version"})
            or value["counts"]["population"] != result["population_count"]
            or len(value["rows"]) != result["population_count"]
            or value["used_for_action_selection"] is not False):
        raise IntegrityError("retained E0 label inventory differs from its result population/target/scenario/source")
    return value


def run_cache_key(manifest, *, branch, multiple, scenario):
    return cache_key(code_hash=manifest.code_hash, inputs=dict(manifest.source_hashes),
        target_version="target-" + str(multiple) + "x-fixed", fold_version=manifest.fold_version,
        transform_versions=(), model_version=manifest.model_version, calibrator_version=manifest.model_version,
        numerical_settings={"exact_ticks": True, "usd": "decimal", "seed": None},
        configuration={"manifest": manifest.version, "branch": branch, "scenario": scenario.version})


def restore_run_checkpoint(checkpoint, manifest, *, branch, multiple, scenario):
    try:
        return compatible_checkpoint(checkpoint, run_cache_key(manifest, branch=branch,
                                                               multiple=multiple, scenario=scenario))
    except ContractError as exc:
        raise ContractError("input/code/fold hash changed; checkpoint cannot be reused") from exc


def _thaw_checkpoint_value(value):
    if type(value) is dict:
        if set(value) == {"$decimal"}:
            return Decimal(value["$decimal"])
        if set(value) == {"$fraction"}:
            return Fraction(*value["$fraction"])
        return {key: _thaw_checkpoint_value(item) for key, item in value.items()}
    if type(value) in (tuple, list):
        return tuple(_thaw_checkpoint_value(item) for item in value)
    return value


def _flat_decision(decision_set, state_version, reason, *, held_side=0):
    ids = tuple(row.id for row in decision_set.rows)
    return Decision(decision_set.id, decision_set.cut, ids, "hold" if held_side else "flat_or_wait",
        tuple((identity, reason) for identity in ids), state_version, (), None, None,
        "existing_bracket" if held_side else "not_called_for_entry", decision_set.cut, None)


def _value(row, day, policy, prediction: E0BracketPrediction):
    if type(prediction) is not E0BracketPrediction or prediction.at != row.cut or prediction.sample_id != row.id:
        raise ContractError("E0 policy value must consume the actual committed prediction for this action")
    if prediction.policy_version != policy.id:
        raise ContractError("prediction belongs to another fixed target policy")
    ps = dict(prediction.probabilities)
    distance = stop_distance(row.range_width)
    tick_usd = Fraction(day.operational.terms.tick_size) * Fraction(day.operational.terms.usd_per_point)
    fee = Fraction(day.operational.fees.fee(day.operational.terms.root, sides=2))
    evidence = E0CommittedPredictionEvidence.from_prediction(prediction, source_version=row.source_version)
    return E0ActionValue(row.id, policy, ps["target"], ps["stop"], ps["deadline"],
        distance * policy.multiple * tick_usd - fee, -distance * tick_usd - fee, -fee,
        row.cut, row.cut, prediction.version, digest(tuple(e[2] for e in prediction.head_evidence)),
        digest(tuple(e[3] for e in prediction.head_evidence)), digest(prediction.head_evidence),
        calibrator_version=prediction.version, source_version=row.source_version, object_version=row.object_version,
        decision_set_id=row.decision_set_id, side=row.side, horizon_end=row.cut + 900 * NS,
        intent_id=digest((row.decision_set_id, row.id, policy.id)), expiry_at=row.cut + 900 * NS,
        risk_reserve_usd=distance * tick_usd + fee + 20, artifact_evidence=evidence)


class E0ReplaySession:
    """A single branch/target/scenario. Ledgers advance only at known time."""

    def __init__(self, root, *, manifest, days, branch, multiple, scenario, predict=None):
        validate_run_inputs(manifest, days, predict=predict)
        if branch not in manifest.branches or multiple not in manifest.target_multiples or scenario not in manifest.scenarios:
            raise ContractError("unregistered E0 branch/target/scenario")
        if branch in ("frequency", "logistic") and type(predict) is not E0BracketRouter:
            raise ContractError("learned E0 branch requires committed target-specific model serving")
        if type(predict) is E0BracketRouter and predict.version != manifest.model_version:
            raise ContractError("E0 model router differs from the frozen manifest")
        self.root, self.manifest, self.days = Path(root), manifest, days
        self.branch, self.multiple, self.scenario, self.predict = branch, multiple, scenario, predict
        self.fees = days[0].operational.fees
        self.orders = OrderLedger(self.root / "orders.sqlite", account_id=manifest.account_id)
        terms = tuple(sorted({day.context.instrument: day.operational.terms for day in days}.items()))
        self.accounting = AccountingLedger(self.root / "account.sqlite", account_id=manifest.account_id,
            eligible_dates=manifest.eligible_dates, eligibility_version=manifest.version, terms=terms, fees=self.fees)
        self.gate = AtomicEntryGate(Journal(self.root / "risk.sqlite"), account_id=manifest.account_id,
            fee_schedule=self.fees, quote_ttl_ns=120 * NS, broker_ttl_ns=120 * NS, feed_ttl_ns=120 * NS)
        self.decisions = Journal(self.root / "decisions.sqlite")
        self.checkpoints = Journal(self.root / "checkpoints.sqlite")
        self.paths, self.populations = [], []
        for day in days:
            latency = LatencyScenario(scenario.id, "event", scenario.feed_lag_ms * 1_000_000, 0)
            path = venue_path_from_mbp(canonical_events=day.native_events,
                selected_instrument=day.context.selected_day, coverage=day.coverage,
                recovery_certificates=day.recovery_certificates, latency_scenario=latency,
                tick_size=day.operational.terms.tick_size, market_state=day.market_state)
            midpoints = {}
            for cut in day.cuts:
                quote, _ = path.quote_at(cut, clock="strategy")
                midpoints[cut] = None if quote is None else Fraction(quote.bid + quote.ask, 2)
            population = build_e0_decision_population(frozen_context=day.context,
                completed_cuts=day.cuts, sampled_midpoints=midpoints, policy_id="E0-common-clock-population-v1")
            self.paths.append(path); self.populations.append(population)
        self.population_hash = digest(tuple(pop.population_hash for pop in self.populations))
        self.cursor = 0
        self.pending = []
        self.authorized = []
        self.outcomes = []
        self.latencies_ns = []
        self._closed_days = set()

    def _snapshot(self, day, path, at):
        state = self.orders.state()
        quote, reason = path.quote_at(at, clock="strategy")
        if quote is None:
            raise DependencyUnavailable("critical source quote unavailable: " + reason)
        account = self.accounting.report()
        known = state["last_known_at"]
        position = state["positions"].get(path.instrument, 0)
        # Mark current exposure at the side-correct visible quote, including
        # fees already charged by confirmed executions in the account journal.
        net = account["days"][day.day]["net"]
        if position:
            fills = tuple(e["payload"] for e in self.accounting.journal.read() if e["kind"] == "trading_fill")
            entry = fills[-1]
            net += day.operational.terms.pnl(Ticks(entry["price_ticks"]),
                Ticks(quote.bid if position == 1 else quote.ask), side=position).value
        return CriticalSnapshot(self.manifest.account_id, day.day, path.instrument, day.operational.terms,
            at, quote.known_at, quote.known_at, known if known is not None else at,
            digest((quote, state["broker_truth"])), Ticks(quote.bid), Ticks(quote.ask), position,
            state["live_orders"], net, self.manifest.daily_budget_usd, None,
            "synthetic-static-day-start-budget", day.operational.window["flatten_send_at"],
            state["reconciled"], state["entry_allowed"])

    def _mirror_gate(self, at):
        state = self.orders.state()
        if not state["reconciled"]:
            return
        _, old, statuses, _ = self.gate._state()
        if old is None:
            return
        day = next((day for day in self.days if day.day == old.trading_date), None)
        path = self.paths[self.days.index(day)]
        snapshot = self._snapshot(day, path, at)
        for authorized in self.authorized:
            identity = authorized.intent.id
            if statuses.get(identity) in ("sent", "working", "unknown", "cancel_requested"):
                if (snapshot.position == authorized.intent.side
                        and state["position_parent_ids"].get(path.instrument) == authorized.plan.id + ":entry"):
                    self.gate.broker_state(identity, event_id="entry-confirmed:" + identity,
                        state="filled", evidence_id=digest(state["broker_truth"]), at=at, snapshot=snapshot)
        self.gate.observe(snapshot)

    def _advance(self, at):
        clocks = sorted({event.known_at for pending in self.pending for event in pending.pending
                         if event.known_at <= at})
        for known in clocks:
            for pending in self.pending:
                pending.advance(known)
            self._mirror_gate(known)
        for pending in self.pending:
            pending.advance(at)

    def run(self, *, through_cut=None):
        from trading_research.experiments.e0.account_bridge import E0OutcomeReplay
        schedule = tuple((index, day, cut) for index, day in enumerate(self.days) for cut in day.cuts)
        while self.cursor < len(schedule):
            index, day, cut = schedule[self.cursor]
            if through_cut is not None and cut > through_cut:
                break
            if index and index - 1 not in self._closed_days:
                self._finish_day(index - 1)
            path, population = self.paths[index], self.populations[index]
            self._advance(cut)
            state = self.orders.state()
            if state["last_known_at"] is None or (not state["live_orders"] and not any(state["positions"].values())):
                self.orders.reconcile(id="clock-flat:" + str(cut), known_at=cut, positions={}, open_order_ids=(),
                    open_orders_complete=True, execution_history_complete=True, evidence_version=digest((self.manifest.version, cut)))
                state = self.orders.state()
            ds = population.by_cut(cut)
            held_side = next((p for p in state["positions"].values() if p), 0)
            pending_entry = any(o["spec"].role == "entry" for identity, o in state["orders"].items()
                                if identity in state["live_orders"])
            if pending_entry and not held_side:
                held_side = next(o["spec"].side for identity, o in state["orders"].items()
                                 if identity in state["live_orders"] and o["spec"].role == "entry")
            state_version = digest(state)
            contacts = tuple(row for row in ds.rows if row.contact is not None and row.side)
            selected = None; reason = "not_in_first_inward_contact_set"
            started = time.perf_counter_ns()
            if held_side:
                reason = "existing_bracket_position_remains_open"
                decision = _flat_decision(ds, state_version, reason, held_side=held_side)
            elif not contacts:
                decision = _flat_decision(ds, state_version, reason)
            elif self.branch == "always_flat":
                reason = "always_flat_policy"
                decision = _flat_decision(ds, state_version, reason)
            elif self.branch == "rule":
                selected = next((row for row in contacts if row.side == row.fade_side), None)
                reason = "unknown_approach" if selected is None else "selected"
                decision = _flat_decision(ds, state_version, reason)
                if selected is not None:
                    policy = TargetPolicy("target-" + str(self.multiple) + "x-fixed", self.multiple)
                    selection = E0RuleSelection.from_decision_set(ds, policy=policy)
                    if (selection.candidate_id, selection.side) != (selected.id, selected.side):
                        raise IntegrityError("rule selection differs from its actual first inward contact")
                    decision = replace(decision, selected_action="enter_" + ("long" if selected.side == 1 else "short"),
                        intent_id=digest((ds.id, selected.id, policy.id)), expires_at=cut + self.manifest.horizon_ns,
                        risk_verdict="pending_independent_gate")
                    object.__setattr__(decision, "side", selected.side)
                    object.__setattr__(decision, "decision_set_id", ds.id)
                    object.__setattr__(decision, "selected_policy_id", policy.id)
                    object.__setattr__(decision, "e0_rule_selection", selection)
            else:
                quote, _ = path.quote_at(cut, clock="strategy")
                policy = TargetPolicy("target-" + str(self.multiple) + "x-fixed", self.multiple)
                values = {}
                for row in contacts:
                    features = e0_feature_values(day, row, midpoint=Fraction(quote.bid + quote.ask, 2),
                        cut=cut, source_quote=quote, scenario=self.scenario)
                    prediction = self.predict(branch=self.branch, policy_version=policy.id, day=day,
                                              row=row, features=features)
                    values[row.id] = _value(row, day, policy, prediction)
                _, decision = score_and_decide_e0(decision_set=E0DecisionSet(ds.id, cut,
                    tuple(row.id for row in ds.rows), source_version=digest(ds.source_versions),
                    pre_action_state_version=state_version), bracket_candidates=values,
                    model_artifacts=tuple(value.artifact_evidence for value in values.values()),
                    account_state=state, risk_state=self._snapshot(day, path, cut))
                chosen = getattr(decision, "selected_value", None)
                selected = next((row for row in contacts if chosen and row.id == chosen.candidate_id), None)
                reason = "selected" if selected else "nonpositive_conservative_expected_net"
            self.latencies_ns.append(time.perf_counter_ns() - started)
            reserve = Decimal(0)
            if selected is not None:
                snapshot = self._snapshot(day, path, cut)
                width = day.context.range_06_09.width
                if width.denominator != 1:
                    raise ContractError("E0 exact stop geometry requires integer tick range width")
                bracket_policy = E0BracketPolicy("target-" + str(self.multiple) + "x-fixed", self.multiple,
                    geometry_version=digest((day.context.version, self.multiple)), range_width_ticks=int(width),
                    stop_distance_ticks=stop_distance(width), impact_ticks=self.scenario.impact_ticks,
                    gap_reserve_usd=self.manifest.gap_reserve_usd, source_version=day.context.version,
                    plan_id=decision.intent_id)
                boundary = E0Boundary(cut + self.manifest.horizon_ns, day.operational.window["flatten_send_at"],
                                      day.operational.window["required_flat_at"], day.operational.version)
                authorized = authorize_e0_bracket(decision=decision, plan_policy=bracket_policy,
                    venue_path=path, terms=day.operational.terms, fees=self.fees, boundary=boundary,
                    critical_snapshot=snapshot, entry_gate=self.gate)
                if authorized.approved and self.gate.dispatch(authorized.intent, at=cut) is not None:
                    scenario = FillScenario(self.scenario.id, self.scenario.impact_ticks, "venue_first",
                                           "strict_trade_through", path.coverage_version, self.fees.version)
                    outcome = authorized.replay(fill_scenario=scenario, timing=self.scenario.timing,
                        prior_day_net=snapshot.trading_net_pnl, daily_budget=self.manifest.daily_budget_usd)
                    manifest = {"instrument": path.instrument, "trading_date": day.day,
                        "source_version": path.version, "fee_version": self.fees.version,
                        "coverage_version": path.coverage_version, "account_id": self.manifest.account_id,
                        "plan_id": authorized.plan.id, "stop_ticks": authorized.plan.stop_ticks,
                        "required_flat_at": boundary.required_flat_at, "evidence_version": digest(outcome)}
                    pending = E0OutcomeReplay(outcome=outcome, order_ledger=self.orders,
                        accounting=self.accounting, scenario_manifest=manifest, timing=self.scenario.timing,
                        venue_path=path, fill_scenario=scenario, finalize_day=False)
                    self.pending.append(pending); self.authorized.append(authorized); self.outcomes.append(outcome)
                    pending.advance(cut)
                    reserve = authorized.reservation.reserve_usd
                else:
                    selected = None; reason = authorized.reason
            self.decisions.append(key="decision:" + str(cut), kind="e0_decision", payload={
                "day": day.day, "cut": cut, "decision": decision, "decision_set": ds,
                "action": "enter" if selected else "hold" if held_side else "flat",
                "desired_position": selected.side if selected else held_side,
                "candidate_id": selected.id if selected else None, "reason": reason,
                "value_evidence": getattr(decision, "value_sidecars", ()),
                "rule_selection": getattr(decision, "e0_rule_selection", None),
                "reserve_usd": reserve, "pre_action_state_version": state_version})
            self.cursor += 1
            if cut == day.cuts[-1] and through_cut is None:
                self._finish_day(index)
        if through_cut is None:
            for index in range(len(self.days)):
                self._finish_day(index)
        return self

    def _finish_day(self, index):
        if index in self._closed_days:
            return
        day = self.days[index]
        at = day.operational.window["required_flat_at"]
        self._advance(at)
        state = self.orders.state()
        if not state["live_orders"] and not any(state["positions"].values()):
            self.orders.reconcile(id="boundary-flat:" + day.day, known_at=at, positions={}, open_order_ids=(),
                open_orders_complete=True, execution_history_complete=True, evidence_version=day.operational.version)
        day_outcomes = tuple(outcome for outcome in self.outcomes if day.cuts[0] <= outcome.entry.at < at)
        status = "flat" if not day_outcomes else "complete" if all(
            o.observation_complete and o.boundary_met for o in day_outcomes) else "incomplete"
        self.accounting.day_status(trading_date=day.day, at=at, status=status, evidence_version=day.operational.version)
        self._closed_days.add(index)

    def checkpoint(self):
        state = {"cursor": self.cursor, "decision_head": tuple(e["hash"] for e in self.decisions.read()),
            "order_head": tuple(e["hash"] for e in self.orders.journal.read()),
            "account_head": tuple(e["hash"] for e in self.accounting.journal.read()),
            "risk_head": tuple(e["hash"] for e in self.gate.journal.read()),
            "population_hash": self.population_hash, "closed_days": tuple(sorted(self._closed_days)),
            "pending": tuple({"checkpoint": p.checkpoint(), "outcome": p.outcome,
                              "manifest": p.manifest, "authorization": authorization}
                             for p, authorization in zip(self.pending, self.authorized)),
            "processing_latency_ns": tuple(self.latencies_ns)}
        self._validate_checkpoint_inventory(state)
        key = run_cache_key(self.manifest, branch=self.branch, multiple=self.multiple, scenario=self.scenario)
        version = digest({"cache_key": key, "state": state})
        self.checkpoints.append(key="checkpoint:" + version, kind="e0_checkpoint",
            payload={"cache_key": key, "state_version": version})
        return {"cache_key": key, "state": state, "retained_state_version": version}

    def _validate_checkpoint_inventory(self, state):
        """Join pending schedules and closed dates to the durable account prefix."""
        state = _thaw_checkpoint_value(state)
        required = {"cursor", "decision_head", "order_head", "account_head", "risk_head", "population_hash",
                    "closed_days", "pending", "processing_latency_ns"}
        if type(state) is not dict or set(state) != required:
            raise IntegrityError("E0 checkpoint state schema differs from the complete runner state")
        schedule = tuple((index, day.day, cut) for index, day in enumerate(self.days) for cut in day.cuts)
        cursor = state["cursor"]
        if (type(cursor) is not int or not 0 <= cursor <= len(schedule)
                or type(state["pending"]) is not tuple
                or type(state["closed_days"]) is not tuple
                or type(state["processing_latency_ns"]) is not tuple
                or len(state["processing_latency_ns"]) != cursor
                or any(type(value) is not int or value <= 0 for value in state["processing_latency_ns"])):
            raise IntegrityError("E0 checkpoint cursor, latency observations or inventory is malformed")
        decisions = tuple(event["payload"] for event in self.decisions.read())
        if tuple((row["day"], row["cut"]) for row in decisions) != tuple((day, cut) for _, day, cut in schedule[:cursor]):
            raise IntegrityError("E0 checkpoint decision prefix differs from the frozen chronological schedule")
        risk = self.gate.journal.read()
        dispatched = tuple(event["payload"]["client_id"] for event in risk if event["kind"] == "entry_dispatched")
        entered = tuple(row["decision"]["intent_id"] for row in decisions if row["action"] == "enter")
        identities, plan_ids = [], []
        for record in state["pending"]:
            if type(record) is not dict or set(record) != {"checkpoint", "outcome", "manifest", "authorization"}:
                raise IntegrityError("E0 checkpoint lost part of an authorized pending bracket")
            authorization = record["authorization"]
            if type(authorization) is AuthorizedBracket:
                intent, plan, reservation = authorization.intent, authorization.plan, authorization.reservation
                identity, plan_id = intent.id, plan.id
                approved = reservation.approved
            elif type(authorization) is dict:
                identity = authorization["intent"]["id"]
                plan_id = authorization["plan"]["id"]
                approved = authorization["reservation"]["approved"]
            else:
                raise IntegrityError("E0 checkpoint authorization is not a retained bracket")
            if not approved or identity != plan_id or record["manifest"]["plan_id"] != plan_id:
                raise IntegrityError("E0 checkpoint pending plan differs from its approved entry intent")
            identities.append(identity); plan_ids.append(plan_id)
        if tuple(identities) != dispatched or tuple(identities) != entered or len(set(identities)) != len(identities):
            raise IntegrityError("E0 checkpoint must retain exactly every dispatched bracket and future exit schedule")
        actual_entries = tuple(event["payload"]["spec"]["client_id"] for event in self.orders.journal.read()
                               if event["kind"] == "order_submitted" and event["payload"]["spec"]["role"] == "entry")
        if actual_entries != tuple(plan_id + ":entry" for plan_id in plan_ids):
            raise IntegrityError("E0 checkpoint pending plans differ from durable submitted entries")
        account = self.accounting.report()
        closed = tuple(index for index, day in enumerate(self.days) if account["days"][day.day]["status"] != "unreported")
        if state["closed_days"] != closed or any(type(index) is not int for index in state["closed_days"]):
            raise IntegrityError("E0 checkpoint closed-day inventory differs from the actual account journal")
        if any(not all((day.day, cut) in {(d["day"], d["cut"]) for d in decisions} for cut in day.cuts)
               for index, day in enumerate(self.days) if index in closed):
            raise IntegrityError("E0 checkpoint closes a day before its full decision population")

    @classmethod
    def restore(cls, root, checkpoint, *, manifest, days, branch, multiple, scenario, predict=None):
        from trading_research.experiments.e0.account_bridge import E0OutcomeReplay
        state = restore_run_checkpoint(checkpoint, manifest, branch=branch, multiple=multiple, scenario=scenario)
        result = cls(root, manifest=manifest, days=days, branch=branch, multiple=multiple, scenario=scenario, predict=predict)
        version = digest({"cache_key": checkpoint["cache_key"], "state": state})
        if (checkpoint.get("retained_state_version") != version
                or not any(event["key"] == "checkpoint:" + version and event["kind"] == "e0_checkpoint"
                           and event["payload"] == {"cache_key": checkpoint["cache_key"], "state_version": version}
                           for event in result.checkpoints.read())):
            raise IntegrityError("E0 restart state differs from its actual retained checkpoint")
        for field, journal in (("decision_head", result.decisions), ("order_head", result.orders.journal),
                               ("account_head", result.accounting.journal), ("risk_head", result.gate.journal)):
            if tuple(state[field]) != tuple(e["hash"] for e in journal.read()):
                raise IntegrityError("E0 restart journals differ from the retained checkpoint prefix")
        if (type(state["cursor"]) is not int or not 0 <= state["cursor"] <= sum(len(day.cuts) for day in days)
                or len(state["decision_head"]) != state["cursor"]
                or state["population_hash"] != result.population_hash):
            raise IntegrityError("E0 restart cursor or population changed")
        result._validate_checkpoint_inventory(state)
        result.cursor = state["cursor"]
        result._closed_days = set(state["closed_days"])
        result.latencies_ns = list(state["processing_latency_ns"])
        for record in state["pending"]:
            # The checkpoint is a typed value in memory, or the explicitly
            # tagged canonical artifact wire when reopened from disk.
            record = _thaw_checkpoint_value(record)
            outcome = record["outcome"]
            if type(outcome) is dict:
                outcome = BracketOutcome(**{**outcome, "entry": Fill(**outcome["entry"]),
                    "exit": None if outcome["exit"] is None else Fill(**outcome["exit"]),
                    "events": tuple(outcome["events"]),
                    "unprotected_interval": None if outcome["unprotected_interval"] is None else tuple(outcome["unprotected_interval"])})
            authorized = record["authorization"]
            if type(authorized) is dict:
                intent = authorized["intent"]
                intent = EntryIntent(**{**intent, "stop": Ticks(intent["stop"]["value"]),
                                         "worst_entry": Ticks(intent["worst_entry"]["value"])})
                decision = authorized["decision"]
                decision = Decision(**{**decision, "candidate_ids": tuple(decision["candidate_ids"]),
                    "rejected_reasons": tuple(tuple(row) for row in decision["rejected_reasons"]),
                    "model_versions": tuple(decision["model_versions"])})
                authorized = AuthorizedBracket(BracketPlan(**authorized["plan"]), intent,
                    Reservation(**authorized["reservation"]), E0BracketPolicy(**authorized["policy"]),
                    decision, authorized["quote_id"], authorized["effective_horizon_end"], authorized["geometry_version"])
            path = result.paths[next(index for index, day in enumerate(result.days)
                                     if day.day == record["manifest"]["trading_date"])]
            fill_scenario = FillScenario(scenario.id, scenario.impact_ticks, "venue_first",
                "strict_trade_through", path.coverage_version, result.fees.version)
            pending = E0OutcomeReplay.restore(record["checkpoint"], outcome=outcome,
                order_ledger=result.orders, accounting=result.accounting, scenario_manifest=record["manifest"],
                timing=scenario.timing, venue_path=path, fill_scenario=fill_scenario, finalize_day=False)
            result.pending.append(pending); result.outcomes.append(outcome); result.authorized.append(authorized)
        return result

    def report(self):
        account = self.accounting.report()
        occupied = sum((Fraction(o.exit.at - o.entry.at, NS) for o in self.outcomes if o.exit and o.exit.quantity), Fraction())
        complete = self.cursor == sum(len(day.cuts) for day in self.days) and len(self._closed_days) == len(self.days)
        labels = (e0_label_inventory(self.days, self.populations, self.paths, multiple=self.multiple,
                                    horizon_ns=self.manifest.horizon_ns, scenario=self.scenario) if complete else None)
        return {"schema": "E0RunResultV1", "manifest_version": self.manifest.version,
            "branch": self.branch, "target_multiple": self.multiple, "scenario": self.scenario.id,
            "scenario_version": self.scenario.version,
            "source_path_versions": {day.day: path.version for day, path in zip(self.days, self.paths, strict=True)},
            "population_hash": self.population_hash, "population_count": sum(len(p) for p in self.populations),
            "decision_sets": tuple(ds for p in self.populations for ds in p.decision_sets),
            "decisions": tuple(e["payload"] for e in self.decisions.read()),
            "label_inventory": labels,
            "label_status": "post_replay_inventory" if complete else "pending_complete_replay",
            "outcomes": tuple(self.outcomes), "account": account,
            "orders": self.orders.state(), "occupied_seconds": occupied,
            "zero_trade_day_count": sum(row["fills"] == 0 for row in account["days"].values()),
            "maximum_risk_reserve_usd": max((a.reservation.reserve_usd for a in self.authorized), default=Decimal(0)),
            "daily_loss_breaches": sum(o.daily_loss_breach is True for o in self.outcomes),
            "minimum_marked_net_usd": min((o.minimum_marked_net_usd for o in self.outcomes
                                          if o.minimum_marked_net_usd is not None), default=Decimal(0)),
            "boundary_met": all(o.boundary_met for o in self.outcomes),
            "processing_latency_ns": tuple(self.latencies_ns), "economic_market_evidence": False}


def register_matrix_trials(registry, manifest):
    family = "E0-matrix:" + manifest.version
    registry.register_family(family, scope_ids=("B03.1", "B03.2", "V03", "V08"),
        protocol={"manifest": manifest, "execution": "finite_synthetic_matrix"},
        max_attempts=3, cpu_budget_seconds=600)
    rows = []
    for multiple in manifest.target_multiples:
        for scenario in manifest.scenarios:
            for branch in manifest.branches:
                trial = registry.register(name="E0-" + branch + "-" + str(multiple) + "x-" + scenario.id,
                    family=family, stage="integration", configuration={"manifest": manifest.version,
                        "branch": branch, "multiple": multiple, "scenario": scenario},
                    code_hash=manifest.code_hash, data_hashes=dict(manifest.source_hashes),
                    fold_version=manifest.fold_version, target_version="target-" + str(multiple) + "x-fixed")
                rows.append((multiple, scenario.id, branch, trial))
    return family, tuple(rows)


def run_e0_matrix(root, *, manifest, days, predict):
    """Freeze and retain all 64 logical trials, with one measured physical run."""
    validate_run_inputs(manifest, days, predict=predict)
    root = Path(root)
    registry = TrialRegistry(root / "trials")
    family, trials = register_matrix_trials(registry, manifest)
    trial = registry.register(name="E0-complete-matrix", family=family, stage="integration",
        configuration={"manifest": manifest.version, "logical_trials": trials}, code_hash=manifest.code_hash,
        data_hashes=dict(manifest.source_hashes), fold_version=manifest.fold_version, target_version="two_fixed_policies")
    attempt = registry.start(trial, cpu_reservation_seconds=180)
    started_cpu, started_wall = time.process_time(), time.monotonic()
    results = []
    label_artifacts = {}
    try:
        publish_new(root / "manifest.json", canonical_json(manifest))
        for multiple in manifest.target_multiples:
            for scenario in manifest.scenarios:
                for branch in manifest.branches:
                    session = E0ReplaySession(root / (str(multiple) + "x-" + scenario.id + "-" + branch),
                        manifest=manifest, days=days, branch=branch, multiple=multiple, scenario=scenario, predict=predict)
                    result = session.run().report()
                    labels = result.pop("label_inventory")
                    label_version = labels["version"]
                    if label_version not in label_artifacts:
                        raw_labels = canonical_json(labels)
                        if len(raw_labels) > 4 * 1024 ** 2:
                            raise ContractError("E0 complete label inventory exceeds its registered 4 MiB artifact bound")
                        label_artifacts[label_version] = registry.artifacts.put_bytes(
                            raw_labels, kind="E0_complete_future_labels")
                    # Branches share the exact fixed-end inventory. Scenario
                    # known clocks remain in its version and are never merged
                    # merely because two paths have the same contact counts.
                    result["label_inventory_artifact"] = label_artifacts[label_version].__dict__
                    results.append(result)
                    if time.process_time() - started_cpu >= 180:
                        raise ContractError("E0 matrix exceeded its registered 180 CPU second physical bound")
        if len(results) != 64 or len({r["population_hash"] for r in results}) != 1:
            raise IntegrityError("E0 comparator changed the common candidate population")
        output = {"manifest": manifest, "trials": trials, "results": tuple(results),
            "physical_attempt": attempt, "historical_role": "development_and_retrospective_evaluation",
            "label_inventory_artifacts": tuple(ref.__dict__ for ref in label_artifacts.values()),
            "market_evidence": False, "program_complete": False}
        raw_output = canonical_json(output)
        if len(raw_output) > 64 * 1024 ** 2:
            raise ContractError("E0 complete matrix exceeds its registered 64 MiB artifact bound")
        artifact = registry.artifacts.put_bytes(raw_output, kind="E0_complete_matrix")
        cpu, wall, rss = (time.process_time() - started_cpu, time.monotonic() - started_wall,
                         resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
        if not (0 < cpu < 180 and 0 < wall < 360 and 0 < rss < 4 * 1024 ** 3):
            raise ContractError("E0 matrix final observed resources exceed the strict accepted bounds")
        registry.finish(attempt, status="succeeded", cpu_seconds=cpu,
            wall_seconds=wall, peak_rss_bytes=rss,
            reason="completed every frozen source/branch/policy/scenario result", result_artifacts=(artifact.__dict__,))
        return output
    except Exception as exc:
        registry.finish(attempt, status="failed", cpu_seconds=time.process_time() - started_cpu,
            wall_seconds=time.monotonic() - started_wall, peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            reason=type(exc).__name__ + ": " + str(exc))
        raise
