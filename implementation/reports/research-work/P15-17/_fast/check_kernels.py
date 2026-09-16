"""Kernel parity: compaction and the E0/E1/E2 first passage vs their scalar references."""
import sys
from dataclasses import fields
from decimal import Decimal
import numpy as np
from trading_research.research.rule_discovery import exits
from trading_research.research.rule_discovery.native import build_market_view

day = sys.argv[1]
view = build_market_view(day, full_account_day=True)
fast = exits.compact_from_view(view)
slow = exits.compact_from_view_scalar(view)
bad = []
for f in fields(exits.CompactDay):
    a, b = getattr(fast, f.name), getattr(slow, f.name)
    if a.shape != b.shape or not np.array_equal(a, b, equal_nan=True):
        bad.append(f.name)
print(f"compact_from_view {day}: groups={fast.event_ns.size} quotes={fast.q_avail.size} mismatched_fields={bad}")
assert not bad, bad

rng = np.random.default_rng(20260916)
n = int(fast.event_ns.size)
finite = fast.max_trade[np.isfinite(fast.max_trade)]
mismatch = 0
checked = 0
reasons = {}
for trial in range(300):
    i = int(rng.integers(0, max(n - 1, 1)))
    fill_ns = int(fast.event_ns[i])
    base = float(finite[int(rng.integers(0, finite.size))]) if finite.size else 4000.0
    side = 1 if trial % 2 == 0 else -1
    width = float(rng.choice([0.25, 0.5, 1.0, 2.0, 5.0, 25.0]))
    q = lambda x: Decimal(str(round(round(x * 4) / 4, 2)))
    try:
        entry = exits.FrozenEntry(
            entry_id=f"t{trial}", family="SYN", branch="b", side=side,
            fill_price=q(base), fill_at_ns=fill_ns,
            initial_stop=q(base - side * width),
            objective=q(base + side * 2 * width) if trial % 5 else None,
            source_deadline_ns=(fill_ns + int(rng.integers(1, 3600)) * 10**9) if trial % 3 == 0 else None,
            flatten_at_ns=int(fast.event_ns[-1]), account_day=day,
        )
    except Exception:
        continue
    for policy in ("E0", "E1", "E2"):
        a = exits.evaluate_policy_compact(entry, policy, fast)
        b = exits.evaluate_policy_compact_scalar(entry, policy, fast)
        checked += 1
        if a != b:
            mismatch += 1
            if mismatch < 4:
                print("  MISMATCH", policy, a, b)
        r = getattr(a, "reason", None)
        reasons[r] = reasons.get(r, 0) + 1
print(f"first passage {day}: records_compared={checked} mismatches={mismatch} reasons={reasons}")
assert mismatch == 0
