"""Literal BBO/flow projection; book recovery never repairs missing flow history."""

from dataclasses import dataclass, replace
from decimal import Decimal

from trading_research.data.events import DECODER_VERSION, CanonicalEvent, Flags, Quote
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class BookState:
    instrument_id: int
    quote: Quote | None = None
    source_event_id: str | None = None
    event_at: int | None = None
    known_at: int | None = None
    economic_quote_at: int | None = None
    trusted: bool = False
    recovery_required_by: str | None = None
    flow_complete: bool = True
    total_volume: int = 0
    buy_volume: int = 0
    sell_volume: int = 0
    unknown_volume: int = 0
    trade_count: int = 0
    fresh_book_events: int = 0


@dataclass(frozen=True)
class RecoveryCertificate:
    instrument_id: int
    invalidating_event_id: str
    recovery_event_id: str
    method: str
    evidence_id: str

    def __post_init__(self) -> None:
        if self.method not in {"documented_full_snapshot", "source_certified_rebuild"} or not self.evidence_id:
            raise ContractError("plausible prices are not a book recovery certificate")


@dataclass(frozen=True)
class Transition:
    event_id: str
    before: BookState
    after: BookState
    pretrade_quote: Quote | None
    bid_size_delta_at_same_price: int | None
    ask_size_delta_at_same_price: int | None
    duplicate: bool = False


@dataclass(frozen=True)
class BookCheckpoint:
    decoder_version: str
    states: tuple[BookState, ...]
    source_rows: tuple[tuple[str, str], ...]


class BookReducer:
    def __init__(self, *, decoder_version: str = DECODER_VERSION):
        self.decoder_version = decoder_version
        self.states: dict[int, BookState] = {}
        self._seen: dict[str, str] = {}

    def apply(self, event: CanonicalEvent, *, recovery: RecoveryCertificate | None = None) -> Transition:
        if event.decoder_version != self.decoder_version:
            raise ContractError("decoder change requires explicit replay/checkpoint migration")
        before = self.states.get(event.instrument_id, BookState(event.instrument_id))
        key, raw_hash = event.address.id, digest({"fields": event.raw_fields, "record": event.raw_record})
        old = self._seen.get(key)
        if old is not None:
            if old != raw_hash:
                raise ContractError("source row was reused with different raw content")
            if recovery is not None:
                raise ContractError("cannot retroactively apply a recovery to an already processed event")
            return Transition(event.id, before, before, None, None, None, True)
        state = before
        bad = bool(event.flags & Flags.MAYBE_BAD_BOOK)
        if bad or event.action is None or event.action == "R":
            # Preserve the first invalidation so repeated bit-4 rows do not lose gap lineage.
            state = replace(state, trusted=False, recovery_required_by=state.recovery_required_by or event.id,
                            flow_complete=state.flow_complete and not bad and event.action is not None)
            if event.action == "R":
                state = replace(state, quote=None, economic_quote_at=None)
        if event.trade_eligible:
            size, side = event.size, event.aggressor
            state = replace(state, total_volume=state.total_volume + size, trade_count=state.trade_count + 1,
                            buy_volume=state.buy_volume + (size if side == 1 else 0),
                            sell_volume=state.sell_volume + (size if side == -1 else 0),
                            unknown_volume=state.unknown_volume + (size if side is None else 0))
        elif event.action == "T" and not event.flags & Flags.SNAPSHOT:
            state = replace(state, flow_complete=False)
        quote_update = event.action in {"A", "M", "C"}
        snapshot = bool(event.flags & Flags.SNAPSHOT)
        if recovery is not None:
            if (recovery.instrument_id != event.instrument_id or recovery.recovery_event_id != event.id
                    or recovery.invalidating_event_id != state.recovery_required_by or bad
                    or not quote_update or event.quote is None or not event.quote.valid
                    or (recovery.method == "documented_full_snapshot" and not snapshot)):
                raise ContractError("recovery certificate does not match this gap and source reconstruction")
            state = replace(state, recovery_required_by=None)
        bid_delta = ask_delta = None
        if quote_update:
            trusted = bool(event.quote and event.quote.valid and not state.recovery_required_by and not bad)
            # Initialization does not invent a fresh venue age or pressure burst.
            economic_at = state.economic_quote_at if snapshot else event.clocks.event_at
            if trusted and before.trusted and not snapshot and before.quote:
                if before.quote.bid == event.quote.bid:
                    bid_delta = event.quote.bid_size - before.quote.bid_size
                if before.quote.ask == event.quote.ask:
                    ask_delta = event.quote.ask_size - before.quote.ask_size
            state = replace(state, quote=event.quote, source_event_id=event.id,
                            event_at=event.clocks.event_at, known_at=event.clocks.known_at,
                            economic_quote_at=economic_at, trusted=trusted,
                            fresh_book_events=state.fresh_book_events + (1 if trusted and not snapshot else 0))
        # A trade carries the pre-trade quote. It never decrements displayed size here.
        if state.total_volume != state.buy_volume + state.sell_volume + state.unknown_volume:
            raise ContractError("signed/unknown flow partition lost volume")
        self._seen[key] = raw_hash
        self.states[event.instrument_id] = state
        return Transition(event.id, before, state, event.quote if event.action == "T" else None, bid_delta, ask_delta)

    def standing(self, instrument_id: int, *, cut: int, max_age_ns: int) -> BookState:
        state = self.states.get(instrument_id)
        if (state is None or not state.trusted or state.known_at is None or state.known_at > cut
                or state.economic_quote_at is None or not 0 <= cut - state.economic_quote_at <= max_age_ns):
            raise DependencyUnavailable("standing BBO is missing, untrusted, future or has unsupported age")
        return state

    def checkpoint(self) -> BookCheckpoint:
        return BookCheckpoint(self.decoder_version, tuple(self.states[id] for id in sorted(self.states)), tuple(sorted(self._seen.items())))

    @classmethod
    def restore(cls, checkpoint: BookCheckpoint, *, decoder_version: str = DECODER_VERSION):
        if checkpoint.decoder_version != decoder_version:
            raise ContractError("stale decoder checkpoint")
        result = cls(decoder_version=decoder_version)
        result.states = {s.instrument_id: s for s in checkpoint.states}
        result._seen = dict(checkpoint.source_rows)
        return result
