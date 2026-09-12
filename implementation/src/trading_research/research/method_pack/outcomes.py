"""C06 non-financial outcomes after the decision."""

from __future__ import annotations

from decimal import Decimal

from trading_research.research.method_pack.logic import dec


def first_touch(events: list[dict], level: Decimal, *, after: int, before: int | None, side: str) -> int | None:
    target = dec(level)
    for event in sorted(events, key=lambda item: item['t']):
        t = event["t"]
        if t <= after:
            continue
        if before is not None and t >= before:
            continue
        price = dec(event["price"])
        if side == "long_target" and price >= target:
            return t
        if side == "short_target" and price <= target:
            return t
        if side == "long_invalidation" and price <= target:
            return t
        if side == "short_invalidation" and price >= target:
            return t
    return None


def ohlc_window_order_unknown(bar: dict, target: Decimal, invalid: Decimal, side: str) -> bool:
    h = dec(bar["H"])
    l = dec(bar["L"])
    if side == "long":
        hit_t = h >= target
        hit_i = l <= invalid
    else:
        hit_t = l <= target
        hit_i = h >= invalid
    return bool(hit_t and hit_i)


def score_outcome(
    *,
    decision_at: int,
    side: str,
    target: Decimal | None,
    invalidation: Decimal | None,
    window_end: int | None,
    events: list[dict] | None,
    bars: list[dict] | None,
    window_complete: bool,
    observation_stopped_at: int | None = None,
    gap: bool = False,
    target_def: bool = True,
    invalidation_def: bool = True,
) -> dict:
    if side not in {'long', 'short'} or not target_def or not invalidation_def or target is None or invalidation is None:
        return {"outcome": "unknown", "hole": "HOLE:C06:definition"}
    if window_end is None or window_end <= decision_at:
        return {"outcome": "unknown", "hole": "HOLE:C06:window_end"}
    if gap:
        return {"outcome": "unknown", "hole": "HOLE:C06:coverage"}
    end = min(window_end, observation_stopped_at) if observation_stopped_at is not None else window_end
    targets, invalidations = [], []
    for event in events or []:
        at = event.get('t', event.get('event_ns'))
        if at is None or type(at) is not int:
            return {"outcome": "unknown", "hole": "HOLE:C06:event_time"}
        if not decision_at < at < end:
            continue
        px = dec(event['price'])
        if (side == 'long' and px >= target) or (side == 'short' and px <= target):
            targets.append((at, at))
        if (side == 'long' and px <= invalidation) or (side == 'short' and px >= invalidation):
            invalidations.append((at, at))
    for bar in bars or []:
        if bar['end'] <= decision_at or bar['start'] >= end:
            continue
        if bar.get('complete') is False:
            return {"outcome": "unknown", "hole": "HOLE:C06:bar_coverage"}
        if bar['start'] < decision_at or bar['end'] > end or bar['end'] <= bar['start']:
            return {"outcome": "unknown", "hole": "HOLE:C06:bar_boundary_order"}
        high, low = dec(bar['H']), dec(bar['L'])
        if (side == 'long' and high >= target) or (side == 'short' and low <= target):
            targets.append((bar['start'], bar['end']))
        if (side == 'long' and low <= invalidation) or (side == 'short' and high >= invalidation):
            invalidations.append((bar['start'], bar['end']))
    first_t = min(targets) if targets else None
    first_i = min(invalidations) if invalidations else None
    if first_t is not None and first_i is not None:
        if first_t[1] < first_i[0]:
            outcome = 'target_first'
        elif first_i[1] < first_t[0]:
            outcome = 'invalidation_first'
        else:
            outcome = 'same_time_unknown'
        return {'outcome': outcome, 'T_interval': first_t, 'I_interval': first_i,
                'invalidation_observation_complete': window_complete}
    complete = window_complete and end == window_end
    if first_t is not None or first_i is not None:
        if not complete:
            return {'outcome': 'unknown', 'hole': 'HOLE:C06:opposing_observation_complete'}
        return {'outcome': 'target_first' if first_t is not None else 'invalidation_first',
                'T_interval': first_t, 'I_interval': first_i,
                'invalidation_observation_complete': True}
    if observation_stopped_at is not None and observation_stopped_at < window_end:
        return {'outcome': 'censored', 'stopped_at': observation_stopped_at}
    if complete:
        return {'outcome': 'neither_observed', 'invalidation_observation_complete': True}
    return {'outcome': 'unknown', 'hole': 'HOLE:C06:coverage'}


def c06_f1() -> dict:
    decision = 10_06
    # use integer keys as relative seconds for the synthetic clock
    t0 = 10 * 3600 + 6 * 60
    events_target_first = [
        {"t": t0 + 4 * 60, "price": Decimal("104")},
        {"t": t0 + 6 * 60, "price": Decimal("98")},
    ]
    events_inv_first = [
        {"t": t0 + 4 * 60, "price": Decimal("98")},
        {"t": t0 + 6 * 60, "price": Decimal("104")},
    ]
    before = [{"t": t0 - 2 * 60, "price": Decimal("104")}]
    a = score_outcome(
        decision_at=t0, side="long", target=Decimal("104"), invalidation=Decimal("98"),
        window_end=t0 + 24 * 60, events=events_target_first, bars=None, window_complete=True,
    )
    b = score_outcome(
        decision_at=t0, side="long", target=Decimal("104"), invalidation=Decimal("98"),
        window_end=t0 + 24 * 60, events=events_inv_first, bars=None, window_complete=True,
    )
    c = score_outcome(
        decision_at=t0, side="long", target=Decimal("104"), invalidation=Decimal("98"),
        window_end=t0 + 24 * 60, events=None,
        bars=[{"start": t0, "end": t0 + 60, "H": Decimal("104"), "L": Decimal("98")}],
        window_complete=True,
    )
    d = score_outcome(
        decision_at=t0, side="long", target=Decimal("104"), invalidation=Decimal("98"),
        window_end=t0 + 24 * 60, events=before, bars=None, window_complete=True,
    )
    e = score_outcome(
        decision_at=t0, side="long", target=Decimal("104"), invalidation=Decimal("98"),
        window_end=t0 + 24 * 60, events=[], bars=None, window_complete=False,
        observation_stopped_at=t0 + 2 * 60,
    )
    f = score_outcome(
        decision_at=t0, side="long", target=Decimal("104"), invalidation=Decimal("98"),
        window_end=t0 + 24 * 60, events=[], bars=None, window_complete=False, gap=True,
    )
    return {
        "target_first": a["outcome"],
        "invalidation_first": b["outcome"],
        "same_time_unknown": c["outcome"],
        "pre_decision_high_ignored": d["outcome"] == "neither_observed",
        "censored": e["outcome"],
        "gap_unknown": f["outcome"],
    }
