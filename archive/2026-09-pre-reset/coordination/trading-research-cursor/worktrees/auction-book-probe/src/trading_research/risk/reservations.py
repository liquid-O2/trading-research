"""Atomic one-mini intent gate with durable unknown-order reservations.

This module returns simulated wire instructions. It has no network, credentials,
or live broker adapter. Broker truth must arrive through the critical lane.
"""

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal

from trading_research.errors import ContractError, IntegrityError
from trading_research.execution.costs import FeeSchedule
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import FuturesTerms, Ticks
from trading_research.operations.artifacts import digest
from trading_research.operations.journal import Journal
from trading_research.risk.budget import Exposure, risk_verdict


@dataclass(frozen=True)
class CriticalSnapshot:
    account_id: str
    trading_date: str
    instrument: str
    terms: FuturesTerms
    at: int
    quote_observed_at: int
    feed_liveness_at: int
    broker_observed_at: int
    source_version: str
    bid: Ticks
    ask: Ticks
    position: int
    broker_open_orders: tuple[str, ...]
    trading_net_pnl: Decimal
    daily_budget: Decimal
    firm_headroom: Decimal | None
    rule_version: str
    flatten_at: int
    state_known: bool
    entry_eligible: bool
    halt_reason: str | None = None

    def __post_init__(self):
        date.fromisoformat(self.trading_date)
        for at in (self.at, self.quote_observed_at, self.feed_liveness_at, self.broker_observed_at, self.flatten_at):
            timestamp(at)
        if max(self.quote_observed_at, self.feed_liveness_at, self.broker_observed_at) > self.at:
            raise ContractError("critical snapshot contains a future source observation")
        if (not all((self.account_id, self.instrument, self.source_version, self.rule_version))
                or self.terms.root not in {"NQ", "ES"} or type(self.position) is not int):
            raise ContractError("critical snapshot needs one-account instrument and reconciliation identity")
        # Out-of-limit broker truth is retained and blocks entries; never clamped.
        if not isinstance(self.broker_open_orders, tuple) or len(set(self.broker_open_orders)) != len(self.broker_open_orders):
            raise ContractError("broker order identities must be immutable and unique")
        for value in (self.trading_net_pnl, self.daily_budget, self.firm_headroom):
            if value is not None and (not isinstance(value, Decimal) or not value.is_finite()):
                raise ContractError("exact finite USD accounting required")
        if not Decimal(0) < self.daily_budget <= Decimal(1000):
            raise ContractError("invalid daily budget")
        if type(self.state_known) is not bool or type(self.entry_eligible) is not bool:
            raise ContractError("critical state and entry eligibility require explicit booleans")

    @property
    def version(self):
        return digest(self)

    def record(self):
        return {**asdict(self), "terms": {**asdict(self.terms), "tick_size": str(self.terms.tick_size),
                                           "usd_per_point": str(self.terms.usd_per_point)},
                "bid": self.bid.value, "ask": self.ask.value, "trading_net_pnl": str(self.trading_net_pnl),
                "daily_budget": str(self.daily_budget), "firm_headroom": None if self.firm_headroom is None else str(self.firm_headroom)}

    @classmethod
    def restore(cls, p):
        terms = FuturesTerms(**{**p["terms"], "tick_size": Decimal(p["terms"]["tick_size"]),
                                 "usd_per_point": Decimal(p["terms"]["usd_per_point"])})
        return cls(**{**p, "terms": terms, "bid": Ticks(p["bid"]), "ask": Ticks(p["ask"]),
                      "broker_open_orders": tuple(p["broker_open_orders"]),
                      "trading_net_pnl": Decimal(p["trading_net_pnl"]), "daily_budget": Decimal(p["daily_budget"]),
                      "firm_headroom": None if p["firm_headroom"] is None else Decimal(p["firm_headroom"])})


@dataclass(frozen=True)
class EntryIntent:
    id: str
    account_id: str
    instrument: str
    side: int
    stop: Ticks
    worst_entry: Ticks
    decision_at: int
    expires_at: int
    horizon_end: int
    critical_version: str
    decision_id: str
    fee_version: str
    gap_reserve: Decimal

    def __post_init__(self):
        for at in (self.decision_at, self.expires_at, self.horizon_end):
            timestamp(at)
        if (type(self.side) is not int or self.side not in {-1, 1}
                or not all((self.id, self.account_id, self.instrument, self.critical_version, self.decision_id, self.fee_version))
                or min(self.expires_at, self.horizon_end) <= self.decision_at
                or not isinstance(self.gap_reserve, Decimal) or not self.gap_reserve.is_finite() or self.gap_reserve < 0):
            raise ContractError("entry intent requires frozen one-mini plan, identity, deadline, fee and reserve terms")
        if self.side * (self.worst_entry.value - self.stop.value) <= 0:
            raise ContractError("initial protective stop must be adverse to the frozen entry bound")

    def record(self):
        return {**asdict(self), "stop": self.stop.value, "worst_entry": self.worst_entry.value,
                "gap_reserve": str(self.gap_reserve)}


@dataclass(frozen=True)
class Reservation:
    client_id: str
    approved: bool
    reason: str
    critical_version: str
    reserve_usd: Decimal


@dataclass(frozen=True)
class SimulatedWireIntent:
    client_id: str
    account_id: str
    instrument: str
    side: int
    quantity: int
    at: int
    durable_dispatch_hash: str


class AtomicEntryGate:
    def __init__(self, journal: Journal, *, account_id: str, fee_schedule: FeeSchedule,
                 quote_ttl_ns: int, broker_ttl_ns: int, feed_ttl_ns: int):
        if not account_id or any(type(v) is not int or v <= 0 for v in (quote_ttl_ns, broker_ttl_ns, feed_ttl_ns)):
            raise ContractError("gate needs account identity and separate explicit critical freshness limits")
        self.journal, self.account_id, self.fees = journal, account_id, fee_schedule
        self.ttls = quote_ttl_ns, broker_ttl_ns, feed_ttl_ns
        journal.append(key="gate-contract", kind="gate_contract",
                       payload={"account_id": account_id, "fees": fee_schedule.version, "critical_ttls_ns": self.ttls})

    def _state(self):
        events, snapshot, statuses = self.journal.read(), None, {}
        for e in events:
            p = e["payload"]
            if e["kind"] == "risk_snapshot":
                snapshot = CriticalSnapshot.restore(p["snapshot"])
            elif e["kind"] == "entry_reserved":
                statuses[p["intent"]["id"]] = "reserved"
            elif e["kind"] == "entry_dispatched":
                statuses[p["client_id"]] = "sent"
            elif e["kind"] == "entry_invalidated":
                statuses[p["client_id"]] = "invalidated"
            elif e["kind"] == "entry_broker_state":
                statuses[p["client_id"]] = p["state"]
                if p["snapshot"] is not None:
                    snapshot = CriticalSnapshot.restore(p["snapshot"])
        return events, snapshot, statuses, events[-1]["hash"] if events else None

    @staticmethod
    def _require_current(events, at):
        frontier=max((e['payload']['snapshot']['at'] if e['kind']=='risk_snapshot' else e['payload']['at']
                      for e in events if e['kind']=='risk_snapshot' or 'at' in e['payload']),default=None)
        if frontier is not None and at<frontier:
            raise ContractError("gate availability regressed behind a durable reservation, dispatch or observation")

    def observe(self, snapshot: CriticalSnapshot) -> None:
        if snapshot.account_id != self.account_id:
            raise ContractError("cross-account critical snapshot")
        events, old, statuses, head = self._state()
        if any(e['key']==f'snapshot:{snapshot.version}' for e in events):
            return
        self._require_current(events,snapshot.at)
        if old is not None and snapshot.at < old.at:
            raise ContractError("older account observation cannot overwrite current critical truth")
        if old is not None and snapshot.trading_date != old.trading_date and (
                old.position != 0 or any(s in {"reserved", "sent", "working", "unknown", "cancel_requested"} for s in statuses.values())):
            raise ContractError("trading-day reset cannot erase open or uncertain exposure")
        self.journal.append(key=f"snapshot:{snapshot.version}", kind="risk_snapshot", payload={"snapshot": snapshot.record()},
                            expected_head=head, check_head=True)

    def reserve(self, intent: EntryIntent, *, at: int) -> Reservation:
        timestamp(at)
        events, snapshot, statuses, head = self._state()
        prior = next((e for e in events if e["key"] == f"reserve:{intent.id}"), None)
        if prior is not None:
            if digest(prior["payload"]["intent"]) != digest(intent.record()):
                raise IntegrityError("entry client ID reused with changed decision/plan")
            p = prior["payload"]
            return Reservation(intent.id, p["approved"], p["reason"], intent.critical_version, Decimal(p["reserve_usd"]))
        self._require_current(events,at)
        reason, reserve = None, Decimal(0)
        if snapshot is None:
            reason = "missing critical state"
        elif intent.account_id != self.account_id or intent.instrument != snapshot.instrument:
            reason = "wrong account or active outright instrument"
        elif intent.fee_version != self.fees.version:
            reason = "fee version does not match frozen account scenario"
        elif snapshot.version != intent.critical_version:
            reason = "critical state changed since decision"
        elif any(s in {"reserved", "sent", "working", "unknown", "cancel_requested"} for s in statuses.values()):
            reason = "pending or unknown order occupies one-mini action state"
        elif snapshot.position or snapshot.broker_open_orders:
            reason = "account is not flat with reconciled empty broker order state"
        elif not snapshot.state_known:
            reason = "unknown account, position, pending order or quote state"
        elif snapshot.halt_reason or not snapshot.entry_eligible:
            reason = "critical state unknown, halted or outside eligible entry population"
        elif not intent.decision_at <= at < min(intent.expires_at, intent.horizon_end, snapshot.flatten_at):
            reason = "original intent horizon or independent flatten boundary reached"
        elif snapshot.at > at or any(at - t > ttl for t, ttl in zip(
                (snapshot.quote_observed_at, snapshot.broker_observed_at, snapshot.feed_liveness_at), self.ttls)):
            reason = "stale quote, broker state or source liveness"
        elif snapshot.bid.value <= 0 or snapshot.bid.value >= snapshot.ask.value:
            reason = "invalid executable BBO"
        else:
            executable = snapshot.ask if intent.side == 1 else snapshot.bid
            if intent.side * (executable.value - intent.worst_entry.value) > 0:
                reason = "price moved beyond the frozen admissible entry bound"
            else:
                exposure = Exposure(intent.instrument, snapshot.terms, intent.side, intent.worst_entry, intent.stop,
                                    self.fees.fee(snapshot.terms.root, sides=2), intent.gap_reserve)
                verdict = risk_verdict(daily_budget=snapshot.daily_budget, trading_net_liquidation_pnl=snapshot.trading_net_pnl,
                                       firm_headroom=snapshot.firm_headroom, mutually_possible_exposures=(exposure,),
                                       rule_version=snapshot.rule_version, state_known=snapshot.state_known)
                reserve = verdict.incremental_reserve
                if not verdict.allowed:
                    reason = verdict.reason
        p = {"intent": intent.record(), "at": at, "approved": reason is None,
             "reason": reason or "reserved against unchanged critical state", "reserve_usd": str(reserve)}
        try:
            self.journal.append(key=f"reserve:{intent.id}", kind="entry_reserved" if reason is None else "entry_refused", payload=p,
                                expected_head=head, check_head=True)
        except ContractError:
            p.update(approved=False, reason="concurrent critical state change; a fresh decision is required")
            current,_,_,current_head=self._state()
            self._require_current(current,at)
            # A refusal grants no action and does not replace account truth.
            # Retain the inspected head without making concurrent refusals race
            # to authorize a commit that can only deny this attempt.
            p['refused_against_head']=current_head
            self.journal.append(key=f"reserve:{intent.id}", kind="entry_refused", payload=p)
        return Reservation(intent.id, p["approved"], p["reason"], intent.critical_version, reserve)

    def dispatch(self, intent: EntryIntent, *, at: int) -> SimulatedWireIntent | None:
        timestamp(at)
        events, snapshot, statuses, head = self._state()
        prior = next((e for e in events if e["key"] == f"reserve:{intent.id}"), None)
        if prior is None or digest(prior["payload"]["intent"]) != digest(intent.record()):
            raise ContractError("dispatch lacks its exact durable frozen reservation")
        if statuses.get(intent.id) != "reserved":
            return None
        self._require_current(events,at)
        valid = (snapshot is not None and snapshot.version == intent.critical_version and snapshot.state_known
                 and snapshot.position == 0 and not snapshot.broker_open_orders and not snapshot.halt_reason
                 and snapshot.entry_eligible and intent.decision_at <= at < min(intent.expires_at, intent.horizon_end, snapshot.flatten_at)
                 and all(0 <= at - t <= ttl for t, ttl in zip(
                     (snapshot.quote_observed_at, snapshot.broker_observed_at, snapshot.feed_liveness_at), self.ttls)))
        kind = "entry_dispatched" if valid else "entry_invalidated"
        p = {"client_id": intent.id, "at": at, "critical_version": snapshot.version if snapshot else None,
             "reason": "reserved critical version unchanged at simulated dispatch" if valid else "critical state, freshness or boundary changed before dispatch"}
        try:
            value, inserted = self.journal.append(key=f"dispatch:{intent.id}", kind=kind, payload=p, expected_head=head, check_head=True)
        except (ContractError, IntegrityError):
            # The racing worker can have committed or account state changed. In
            # either case this worker receives no permission to send anything.
            return None
        if not valid or not inserted:
            return None
        return SimulatedWireIntent(intent.id, self.account_id, intent.instrument, intent.side, 1, at, value)

    def broker_state(self, client_id: str, *, event_id: str, state: str, evidence_id: str,
                     at: int, snapshot: CriticalSnapshot | None = None) -> None:
        timestamp(at)
        events, old_snapshot, statuses, head = self._state()
        p = {"client_id": client_id, "state": state, "evidence_id": evidence_id, "at": at,
             "snapshot": None if snapshot is None else snapshot.record()}
        old = next((e for e in events if e["key"] == f"broker:{event_id}"), None)
        if old is not None:
            if digest(old["payload"]) != digest(p):
                raise IntegrityError("broker event ID reused with changed content")
            return
        self._require_current(events,at)
        if not event_id or not evidence_id or state not in {"working", "unknown", "cancel_requested", "filled", "cancelled", "rejected"}:
            raise ContractError("broker state requires immutable evidence and a supported reconciliation outcome")
        if statuses.get(client_id) not in {"sent", "working", "unknown", "cancel_requested"}:
            raise ContractError("broker transition has no matching possibly live order")
        if state in {"filled", "cancelled", "rejected"}:
            if snapshot is None or not snapshot.state_known or snapshot.account_id != self.account_id or snapshot.at > at:
                raise ContractError("only confirmed broker truth can release a pending/unknown order")
            if client_id in snapshot.broker_open_orders:
                raise ContractError("terminal broker message conflicts with still-open order truth")
            dispatch=next(e['payload'] for e in events if e['kind']=='entry_dispatched' and e['payload']['client_id']==client_id)
            if snapshot.broker_observed_at<dispatch['at']:
                raise ContractError("pre-dispatch broker truth cannot release a possibly live order")
            intent = next(e["payload"]["intent"] for e in events if e["kind"] == "entry_reserved" and e["payload"]["intent"]["id"] == client_id)
            if state == "filled" and (snapshot.position != intent["side"] or snapshot.instrument != intent["instrument"]):
                raise ContractError("fill acknowledgement lacks matching resulting one-mini position")
        elif snapshot is not None:
            raise ContractError("nonterminal state cannot replace independently reconciled critical truth")
        if snapshot is not None and old_snapshot is not None and snapshot.at < old_snapshot.at:
            raise ContractError("older broker reconciliation cannot overwrite newer account truth")
        self.journal.append(key=f"broker:{event_id}", kind="entry_broker_state", payload=p, expected_head=head, check_head=True)
