"""Independent re-check of the literal OUTCOMES.md fixtures via public functions."""
import sys
from decimal import Decimal as D

from trading_research.research.contracts.outcomes import (
    PriceBatch, first_passage, excursions, causal_scale,
)
from trading_research.research.contracts.execution import (
    replay_family, net_dollars, net_points, worked_net_pnl_fixture, QuoteBatch,
)
from trading_research.research.contracts.types import Coverage, CoverageReceipt, EvidenceRef

T = 1_600_000_000_000_000_000
NS = 1_000_000_000
SHA = "0" * 64
fails = []

def chk(name, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {name}: got={got!r} want={want!r}")
    if not ok:
        fails.append(name)

def batches(specs):
    return [PriceBatch(event_ns=T + k * NS, available_at_ns=T + k * NS,
                       prices=tuple(D(str(p)) for p in ps),
                       event_ids=(f"e{k}",)) for k, ps in specs]

def cov(status, missing=()):
    return CoverageReceipt(start_ns=T, end_ns=T + 10 * NS, status=status,
                           expected_matching_intervals=((T, T + 10 * NS),),
                           observed_intervals=((T, T + 10 * NS),),
                           missing_intervals=tuple(missing),
                           calendar_sha256=SHA, evidence=())

COMPLETE = cov(Coverage.COMPLETE)
long_kw = dict(start_ns=T, end_ns=T + 10 * NS, side=1,
               entry=D("100"), stop=D("99"), target=D("102"))
# mirrored short: entry 100, stop 101, target 98; prices mirrored about 100
short_kw = dict(start_ns=T, end_ns=T + 10 * NS, side=-1,
                entry=D("100"), stop=D("101"), target=D("98"))

# --- 1. target-first ---
b1 = batches([(1, [100.5]), (2, [102]), (3, [98.5])])
r = first_passage(b1, coverage=COMPLETE, **long_kw)
chk("long target_first", r.result, "target_first")
chk("long target_first resolved_at", r.resolved_at_ns, T + 2 * NS)
s1 = batches([(1, [99.5]), (2, [98]), (3, [101.5])])
chk("short target_first", first_passage(s1, coverage=COMPLETE, **short_kw).result, "target_first")

# --- 2. same-batch ambiguous ---
b2 = batches([(1, [100.5]), (2, [98.5, 102]), (3, [98.5])])
chk("long same_batch_ambiguous", first_passage(b2, coverage=COMPLETE, **long_kw).result,
    "same_batch_ambiguous")
s2 = batches([(1, [99.5]), (2, [101.5, 98]), (3, [101.5])])
chk("short same_batch_ambiguous", first_passage(s2, coverage=COMPLETE, **short_kw).result,
    "same_batch_ambiguous")

# --- 3. prior-gap-unknown: missing interval inserted before t+2 ---
gap = cov(Coverage.PARTIAL, missing=((T + NS + 1, T + 2 * NS - 1),))
chk("long prior_gap_unknown", first_passage(b1, coverage=gap, **long_kw).result,
    "prior_gap_unknown")
chk("short prior_gap_unknown", first_passage(s1, coverage=gap, **short_kw).result,
    "prior_gap_unknown")

# --- 4. neither: complete prices bounded in [99.25, 101.75] ---
b4 = batches([(1, [99.25]), (2, [101.75]), (3, [100.0])])
chk("long neither", first_passage(b4, coverage=COMPLETE, **long_kw).result, "neither")
s4 = batches([(1, [100.75]), (2, [98.25]), (3, [100.0])])
chk("short neither", first_passage(s4, coverage=COMPLETE, **short_kw).result, "neither")

# --- 5. invalid geometry guard ---
chk("invalid_geometry", first_passage(b1, start_ns=T, end_ns=T + 10 * NS, side=1,
    entry=D("100"), stop=D("101"), target=D("102"), coverage=COMPLETE).result,
    "invalid_geometry")

# --- 6. $25 / 1.25 net points fixture ---
chk("net_dollars 25", net_dollars(side=1, entry=D("100.25"), exit_price=D("101.75"),
    commission=D("5.00")), D("25.00"))
chk("net_points 1.25", net_points(side=1, entry=D("100.25"), exit_price=D("101.75"),
    commission=D("5.00")), D("1.25"))
chk("module fixture match", worked_net_pnl_fixture()["match"], True)
chk("short net_dollars 25", net_dollars(side=-1, entry=D("101.75"), exit_price=D("100.25"),
    commission=D("5.00")), D("25.00"))

# --- 7. MFE = 1S, MAE = .25S with S = 4 ---
ex = excursions([D("102"), D("99"), D("104")], side=1, reference=D("100"))
S = D("4")
chk("MFE points", ex["mfe_points"], D("4"))
chk("MAE points", ex["mae_points"], D("1"))
chk("MFE/S", ex["mfe_points"] / S, D("1"))
chk("MAE/S", ex["mae_points"] / S, D("0.25"))
exs = excursions([D("98"), D("101"), D("96")], side=-1, reference=D("100"))
chk("short MFE/S", exs["mfe_points"] / S, D("1"))
chk("short MAE/S", exs["mae_points"] / S, D("0.25"))
chk("causal_scale floor", causal_scale(D("100.5"), D("100.0"), matching_minutes=60, complete=True), D("1.00"))
chk("causal_scale missing<60", causal_scale(D("105"), D("100"), matching_minutes=59, complete=True), None)
chk("causal_scale gap", causal_scale(D("105"), D("100"), matching_minutes=60, complete=False), None)

# --- 8. zero-entry complete day stays in series; missing day absent ---
def quote(k, bid, ask):
    return QuoteBatch(batch_id=f"q{k}", asset_id="NQ", event_ns=T + k * NS,
                      available_at_ns=T + k * NS, bid=D(str(bid)), ask=D(str(ask)),
                      bid_size=5, ask_size=5, ambiguous=False,
                      evidence=(EvidenceRef(artifact_sha256=SHA, row_ids=(f"f.parquet:{k}",),
                                            event_start_ns=T + k * NS, event_end_ns=T + k * NS,
                                            available_at_ns=T + k * NS, coverage=Coverage.COMPLETE,
                                            limitation_ids=()),))

quotes = [quote(k, 100.00, 100.25) for k in range(0, 12)]
zero_day = replay_family([], quotes, account_day="2020-01-02")
chk("zero-entry day zero_entry", zero_day.zero_entry, True)
chk("zero-entry day complete", zero_day.complete, True)
chk("zero-entry day realized", zero_day.realized_dollars, D("0"))
traded = replay_family(
    [{"opportunity_id": "o1", "rule_id": "r", "reference_id": "ref", "contact_id": "c1",
      "side": 1, "decision_at_ns": T, "stop": D("99"), "target": D("102")}],
    quotes + [quote(20, 102.25, 102.50), quote(21, 102.25, 102.50)], account_day="2020-01-03")
chk("traded day zero_entry False", traded.zero_entry, False)
# a day with no usable quotes at all: entry unsupported -> not a complete zero-entry day
missing_day = replay_family(
    [{"opportunity_id": "o1", "rule_id": "r", "reference_id": "ref", "contact_id": "c1",
      "side": 1, "decision_at_ns": T, "stop": D("99"), "target": D("102")}],
    [], account_day="2020-01-06")
chk("missing day has unsupported fill", bool(missing_day.unsupported_fills), True)
series = {d.account_day: d for d in (zero_day, traded) if d.complete and not d.unsupported_fills}
chk("zero-entry day in series", "2020-01-02" in series, True)
chk("missing day absent from series", "2020-01-06" in series, False)

print()
print("TOTAL FAILURES:", len(fails), fails)
sys.exit(1 if fails else 0)
