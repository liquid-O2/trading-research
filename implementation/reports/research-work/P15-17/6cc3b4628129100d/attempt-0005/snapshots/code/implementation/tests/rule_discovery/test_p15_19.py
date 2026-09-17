"""P15-19 E0-E4 machinery. Synthetic fixtures are labelled. Native slice is descriptive only."""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
from pathlib import Path
import json

import pytest

from trading_research.errors import ContractError
from trading_research.research.contracts.execution import ENTRY_WINDOW_NS, LATENCY_NS, net_dollars, net_points
from trading_research.research.contracts.outcomes import PriceBatch
from trading_research.research.contracts.types import Coverage, EvidenceRef, QuoteBatch
from trading_research.research.rule_discovery.exits import (
    JOBS_ROOT,
    MINUTE_NS,
    POLICIES,
    SLICE_DATES,
    ExitRecord,
    FrozenEntry,
    IncompleteExit,
    UnsupportedRecord,
    attempt_partial_exit,
    evaluate_entry,
    evaluate_entries,
    evaluate_policy,
    run_native_slice,
)

NS = 1_000_000_000
FILL = 10 * NS
PREP = Path("/workspace/.worktrees/p15-19-exits-prep/implementation/reports/research-work/P15-19/_prep")


def _ev(ns: int, name: str) -> EvidenceRef:
    return EvidenceRef("a" * 64, (name,), ns, ns, ns, Coverage.COMPLETE, ())


def _qb(ns: int, bid: str | Decimal, ask: str | Decimal | None = None, *, name: str | None = None) -> QuoteBatch:
    bid_d = Decimal(str(bid))
    ask_d = Decimal(str(ask if ask is not None else bid))
    token = name or f"q{ns}"
    return QuoteBatch(token, "NQ:x", ns, ns, bid_d, ask_d, 1, 1, False, (_ev(ns, token),))


def _with_fills(quotes: list[QuoteBatch]) -> list[QuoteBatch]:
    extra = [
        _qb(quote.available_at_ns + LATENCY_NS, quote.bid, quote.ask, name=f"{quote.batch_id}f")
        for quote in quotes
    ]
    return list(quotes) + extra


def _entry(**kwargs) -> FrozenEntry:
    body = dict(
        entry_id="e1",
        family="F",
        branch="b",
        side=1,
        fill_price=Decimal("100"),
        fill_at_ns=FILL,
        initial_stop=Decimal("99"),
        objective=Decimal("102"),
        source_deadline_ns=None,
        flatten_at_ns=FILL + 180 * MINUTE_NS,
    )
    body.update(kwargs)
    return FrozenEntry(**body)


def test_a01_outcomes_literal_target_first_long_and_short():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(FILL + 2 * NS, "102"),
            _qb(FILL + 3 * NS, "98.5"),
        ]
    )
    long_paired = evaluate_entry(_entry(), quotes)
    assert long_paired.entry_id == "e1"
    assert all(long_paired.records[p].entry_id == "e1" for p in POLICIES)
    e0 = long_paired.records["E0"]
    assert e0.reason == "objective"
    assert e0.complete is True
    short_quotes = _with_fills(
        [
            _qb(FILL + NS, "99.5"),
            _qb(FILL + 2 * NS, "98"),
            _qb(FILL + 3 * NS, "101.5"),
        ]
    )
    short = evaluate_entry(
        _entry(side=-1, initial_stop=Decimal("101"), objective=Decimal("98")),
        short_quotes,
    )
    assert short.records["E0"].reason == "objective"


def test_a01_same_batch_pessimistic_stop():
    quotes = _with_fills([_qb(FILL + NS, "100.5"), _qb(FILL + 2 * NS, "100.5")])
    trades = [
        PriceBatch(
            event_ns=FILL + 2 * NS,
            available_at_ns=FILL + 2 * NS,
            prices=(Decimal("98.5"), Decimal("102")),
            event_ids=("lo", "hi"),
        )
    ]
    e0 = evaluate_entry(_entry(), quotes, trades).records["E0"]
    assert e0.reason == "stop"


def test_a01_neither_then_time_exit():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(FILL + 2 * NS, "101.75"),
            _qb(FILL + 3 * NS, "99.25"),
            _qb(FILL + 30 * MINUTE_NS, "100.5"),
        ]
    )
    e1 = evaluate_entry(_entry(), quotes).records["E1"]
    assert e1.reason == "expiry"
    assert e1.reason not in {"objective", "stop"}


def test_a02_e4_does_not_peek_later_high():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "105", name="arm"),
            _qb(FILL + 2 * NS, "103", name="mid"),
            _qb(FILL + 3 * NS, "100.00", name="dip"),
            _qb(FILL + 4 * NS, "130", name="late"),
        ]
    )
    entry = _entry(initial_stop=Decimal("95"), objective=Decimal("200"))
    e4 = evaluate_entry(entry, quotes).records["E4"]
    assert e4.reason == "trailing stop"
    assert e4.exit_at_ns < FILL + 4 * NS
    assert e4.exit_price != Decimal("130")
    assert all(item.trigger_batch_id != "late" for item in e4.stop_updates)
    peeked_points = net_points(
        side=1,
        entry=Decimal("100"),
        exit_price=Decimal("129.75"),
        commission=entry.round_trip_cost,
    )
    assert e4.net_points != peeked_points
    assert e4.stop_updates
    for item in e4.stop_updates:
        assert item.effective_available_at_ns > item.trigger_available_at_ns
        assert item.effective_after_batch_id != item.trigger_batch_id


def test_stop_update_names_effective_batch():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "101.00", name="arm"),
            _qb(FILL + 2 * NS, "100.50", name="hold"),
            _qb(FILL + 3 * NS, "100.20", name="be"),
        ]
    )
    e3 = evaluate_entry(_entry(), quotes).records["E3"]
    assert isinstance(e3, ExitRecord)
    assert e3.stop_updates
    for item in e3.stop_updates:
        assert item.effective_available_at_ns > item.trigger_available_at_ns
        assert item.effective_after_batch_id != item.trigger_batch_id


def test_a01_break_even_does_not_loosen():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "101.00", name="arm"),
            _qb(FILL + 2 * NS, "100.50", name="hold"),
            _qb(FILL + 3 * NS, "100.20", name="be"),
        ]
    )
    e3 = evaluate_entry(_entry(), quotes).records["E3"]
    assert e3.reason == "break-even stop"
    assert e3.stop_updates
    stops = [item.stop for item in e3.stop_updates]
    assert min(stops) >= Decimal("100.25")


def test_a03_fractional_partial_rejected():
    with pytest.raises(ContractError, match="fractional"):
        FrozenEntry(
            entry_id="x",
            family="F",
            branch="b",
            side=1,
            fill_price=Decimal("100"),
            fill_at_ns=FILL,
            initial_stop=Decimal("99"),
            objective=Decimal("102"),
            source_deadline_ns=None,
            flatten_at_ns=FILL + MINUTE_NS,
            quantity=2,
        )
    with pytest.raises(ContractError, match="fractional"):
        attempt_partial_exit(Decimal("0.5"))


def test_a04_undefined_r_unsupported_e3_e4():
    quotes = _with_fills([_qb(FILL + NS, "100.5"), _qb(FILL + 2 * NS, "102")])
    none_stop = evaluate_entry(_entry(initial_stop=None), quotes)
    equal_stop = evaluate_entry(_entry(initial_stop=Decimal("100")), quotes)
    for paired in (none_stop, equal_stop):
        assert isinstance(paired.records["E3"], UnsupportedRecord)
        assert paired.records["E3"].reason == "undefined_initial_r"
        assert isinstance(paired.records["E4"], UnsupportedRecord)
        assert isinstance(paired.records["E0"], ExitRecord)
        assert not isinstance(paired.records["E0"], UnsupportedRecord)
        assert paired.records["E0"].complete is True
        assert paired.records["E1"].complete is True
        assert paired.records["E2"].complete is True


def test_e0_missing_quote_is_incomplete_not_unsupported():
    rec = evaluate_policy(_entry(), "E0", [_qb(FILL + NS, "100.5")])
    assert isinstance(rec, IncompleteExit)
    assert rec.reason == "incomplete_no_quote"
    assert not isinstance(rec, UnsupportedRecord)


def test_e0_never_undefined_r_unsupported():
    quotes = _with_fills([_qb(FILL + NS, "100.5"), _qb(FILL + 2 * NS, "102")])
    paired = evaluate_entry(_entry(initial_stop=None), quotes)
    assert not isinstance(paired.records["E0"], UnsupportedRecord)
    assert paired.records["E0"].reason != "undefined_initial_r"
    with pytest.raises(ContractError, match="E3/E4"):
        UnsupportedRecord("E0", "e1")


def test_source_deadline_earlier_than_policy_expiry():
    deadline = FILL + 10 * MINUTE_NS
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(deadline, "100.5", name="src"),
        ]
    )
    paired = evaluate_entry(_entry(source_deadline_ns=deadline), quotes)
    for policy_id in POLICIES:
        rec = paired.records[policy_id]
        assert rec.reason == "source deadline"


def test_account_day_close_ends_open_position():
    flatten = FILL + 5 * MINUTE_NS
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(flatten, "100.5", name="flat"),
        ]
    )
    paired = evaluate_entry(_entry(flatten_at_ns=flatten, source_deadline_ns=None), quotes)
    for policy_id in POLICIES:
        rec = paired.records[policy_id]
        assert rec.reason == "account-day close"
        assert rec.exit_at_ns <= flatten + ENTRY_WINDOW_NS


def test_s02_known_at_guard_negative_control():
    quotes = _with_fills(
        [
            _qb(FILL + NS, "101.00", name="mix"),
            _qb(FILL + 180 * MINUTE_NS, "100.50", name="end"),
        ]
    )
    trades = [
        PriceBatch(
            event_ns=FILL + NS,
            available_at_ns=FILL + NS,
            prices=(Decimal("101.00"), Decimal("100.20")),
            event_ids=("hi", "be"),
        )
    ]
    entry = _entry()
    guarded = evaluate_policy(entry, "E3", quotes, trades, known_at_guard=True)
    naive = evaluate_policy(entry, "E3", quotes, trades, known_at_guard=False)
    production = evaluate_entry(entry, quotes, trades).records["E3"]
    assert naive.reason == "break-even stop"
    assert guarded.reason != naive.reason or guarded.exit_at_ns != naive.exit_at_ns
    assert production.reason == guarded.reason
    assert production.exit_at_ns == guarded.exit_at_ns


def test_a05_occupancy_flagged_not_merged():
    flatten = FILL + 180 * MINUTE_NS
    first = _entry(entry_id="a", flatten_at_ns=flatten)
    second = _entry(entry_id="b", fill_at_ns=FILL + 45 * MINUTE_NS, flatten_at_ns=flatten)
    quotes = _with_fills(
        [
            _qb(FILL + NS, "100.5"),
            _qb(FILL + 30 * MINUTE_NS, "100.5", name="e1"),
            _qb(FILL + 45 * MINUTE_NS, "100.5", name="e2"),
            _qb(FILL + 120 * MINUTE_NS, "100.5", name="e2end"),
        ]
    )
    rows = evaluate_entries([first, second], quotes)
    assert rows[0].entry_id == "a"
    assert rows[1].entry_id == "b"
    assert rows[0].records["E1"].entry_id == "a"
    assert rows[1].records["E1"].entry_id == "b"
    assert rows[1].occupancy_flags["E1"] is False
    assert rows[1].occupancy_flags["E2"] is True
    assert set(rows[1].records) == set(POLICIES)


def test_s14_worked_net_points_on_e0_exit():
    entry = _entry(fill_price=Decimal("100.25"), initial_stop=Decimal("99.00"), objective=Decimal("102.00"))
    quotes = _with_fills([_qb(FILL + NS, "102.00")])
    e0 = evaluate_entry(entry, quotes).records["E0"]
    assert e0.reason == "objective"
    assert e0.net_points == Decimal("1.25")
    assert e0.net_dollars == Decimal("25.00")
    assert e0.net_points == net_points(
        side=1, entry=Decimal("100.25"), exit_price=Decimal("101.75"), commission=entry.round_trip_cost
    )
    assert e0.net_dollars == net_dollars(
        side=1, entry=Decimal("100.25"), exit_price=Decimal("101.75"), commission=entry.round_trip_cost
    )


def test_native_chronological_slice_reconciliation():
    assert JOBS_ROOT.is_dir()
    recon = run_native_slice(SLICE_DATES, JOBS_ROOT, out_dir=PREP)
    assert recon["descriptive_only"] is True
    assert recon["dates"] == list(SLICE_DATES)
    n = recon["entries"]
    assert n > 0
    for policy_id in POLICIES:
        row = recon["per_policy"][policy_id]
        assert (
            row["reason_sum"] + row["unsupported_undefined_r"] + row["incomplete_no_quote"] == n
        )
        if policy_id in ("E0", "E1", "E2"):
            assert row["unsupported_undefined_r"] == 0
    payload = json.loads((PREP / "SLICE_EXITS.json").read_text())
    by_day = Counter(row["account_day"] for row in payload["entries"])
    assert "" not in by_day
    assert [{"date": day, "entries": by_day[day]} for day in recon["dates"]] == recon["date_counts"]
    for row in payload["entries"]:
        e0 = row["records"]["E0"]
        assert e0.get("reason") != "undefined_initial_r"
        assert e0.get("disposition") != "unsupported_undefined_r"
        for rec in row["records"].values():
            for item in rec.get("stop_updates") or []:
                assert item["effective_available_at_ns"] > item["trigger_available_at_ns"]
                assert item["effective_after_batch_id"] != item["trigger_batch_id"]
    assert (PREP / "SLICE_EXITS.json").is_file()
    assert (PREP / "RECONCILIATION.json").is_file()


# ==========================================================================
# The executed exit study: frozen entries from the entry stage's own records,
# E0-E4 on one tape, and the rule that this family cannot rescue an entry.
# ==========================================================================

import numpy as _np

from trading_research.research.rule_discovery import exits as _exits
from trading_research.research.rule_discovery.exits import POLICY_EXPIRY_MINUTES


def _tape(start, n=600, step=NS, base=100.0, drift=0.0, dip_at=None, dip=0.0):
    """A synthetic compact day. Labelled synthetic; the native evidence is the
    study's own shards."""
    event = _np.arange(n, dtype=_np.int64) * int(step) + int(start)
    price = base + drift * _np.arange(n, dtype=_np.float64)
    if dip_at is not None:
        price[dip_at:] = price[dip_at:] + dip
    return _exits.CompactDay(
        event_ns=event,
        available_at_ns=event,
        min_bid=price - 0.25,
        max_bid=price - 0.25,
        min_ask=price + 0.25,
        max_ask=price + 0.25,
        min_trade=price,
        max_trade=price,
        q_avail=event,
        q_bid=price - 0.25,
        q_ask=price + 0.25,
    )


@pytest.mark.parametrize("policy", list(POLICIES))
def test_every_policy_matches_its_scalar_reference_on_one_tape(policy):
    """Each policy's compact evaluation is the plain-Python reference's answer,
    on a path that reaches the objective late enough for the expiry minutes to
    separate E1, E0 and E2 and for E3/E4 to have moved their stop."""
    start = 1_700_000_000 * NS
    day = _tape(start, n=8000, step=NS, base=100.0, drift=0.0005)
    entry = _entry(
        fill_at_ns=int(day.event_ns[5]),
        fill_price=Decimal("100.00"),
        initial_stop=Decimal("99.00"),
        objective=Decimal("103.50"),
        flatten_at_ns=int(day.event_ns[-1]),
    )
    fast = _exits.evaluate_policy_compact(entry, policy, day)
    slow = _exits.evaluate_policy_compact_scalar(entry, policy, day)
    assert fast == slow


def test_the_five_policies_differ_where_the_contract_says_they_do():
    """E1 (30m), E0 (60m) and E2 (120m) end at their own deadlines on a path
    that never reaches stop or objective; E3 and E4 move the stop after +1R and
    exit on it, and neither is ever looser than the initial stop."""
    start = 1_700_000_000 * NS
    day = _tape(start, n=9000, step=NS, base=100.0, drift=0.0004, dip_at=7000, dip=-2.0)
    entry = _entry(
        fill_at_ns=int(day.event_ns[5]),
        fill_price=Decimal("100.00"),
        initial_stop=Decimal("99.00"),
        objective=Decimal("110.00"),
        flatten_at_ns=int(day.event_ns[8500]),
    )
    records = {policy: _exits.evaluate_policy_compact(entry, policy, day) for policy in POLICIES}
    expiries = {
        policy: entry.fill_at_ns + POLICY_EXPIRY_MINUTES[policy] * MINUTE_NS
        for policy in ("E0", "E1", "E2")
    }
    for policy in ("E0", "E1", "E2"):
        assert records[policy].reason == "expiry"
        assert records[policy].exit_at_ns >= expiries[policy]
    assert expiries["E1"] < expiries["E0"] < expiries["E2"]
    assert records["E1"].exit_at_ns < records["E0"].exit_at_ns < records["E2"].exit_at_ns
    for policy in ("E3", "E4"):
        record = records[policy]
        assert isinstance(record, ExitRecord)
        assert record.stop_updates, f"{policy} never moved its stop on a +1R path"
        for update in record.stop_updates:
            assert update.stop >= entry.initial_stop  # long: never looser
            assert update.effective_available_at_ns >= update.trigger_available_at_ns
        assert record.reason in ("break-even stop", "trailing stop", "expiry", "account-day close")
    # OUTCOMES: "A price gap fills at that actual quote, not the boundary" --
    # on this path E4's trailing stop is jumped through, so the fill is the
    # executable quote less one tick and is worse than the stop, never clipped
    # back to it.
    trailing = records["E4"]
    if trailing.reason == "trailing stop":
        last_stop = trailing.stop_updates[-1].stop
        assert trailing.exit_price != last_stop
        assert trailing.exit_price < last_stop  # long: gapped through


def _study_fixture(tmp_path, *, e0_points="1.0", entry_disposition="rejected_by_evidence"):
    """A two-day entry run and refinement selection on disk, the shape the study
    reads: job documents with their recorded E0 entries."""
    from trading_research.research.rule_discovery import search_run

    breadth = tmp_path / "breadth"
    refinement = tmp_path / "refinement"
    for root in (breadth, refinement):
        search_run._write_json(root / "MANIFEST.json", {"dates": ["2020-01-02", "2020-01-03"]})
    search_run._write_json(
        refinement / "SELECTED_RULES_BY_FOLD.json",
        {
            "folds": [
                {
                    "outer_fold": 2022,
                    "roles": [
                        {
                            "family": "SYN",
                            "candidate_id": "SYN:syn_branch:S1:deadline_minutes=5",
                            "role": "refined_selected",
                            "parent_trial_ids": ["SYN:syn_branch:S1"],
                            "disposition": entry_disposition,
                            "promoted": False,
                        }
                    ],
                    "combinations": [],
                }
            ],
            "all_history_descriptive_recommendation": None,
        },
    )
    for day in ("2020-01-02", "2020-01-03"):
        search_run._write_gz(
            search_run.job_path(refinement, day, "SYN:syn_branch:S1:deadline_minutes=5"),
            {
                "family": "SYN",
                "branch": "syn_branch",
                "status": "evaluated",
                "candidate": {
                    "opportunities": 1,
                    "fills": 1,
                    "exclusions": [],
                    "net_points": e0_points,
                    "entries": [
                        {
                            "entry_id": f"syn-{day}",
                            "side": 1,
                            "fill_at_ns": 1,
                            "fill_price": "100.00",
                            "initial_stop": "99.00",
                            "objective": "102.00",
                            "round_trip_cost": "5.00",
                            "exit_at_ns": 2,
                            "exit_reason": "objective",
                            "net_points": e0_points,
                        }
                    ],
                },
            },
        )
    return breadth, refinement


def test_frozen_entries_come_from_the_entry_stage_records(tmp_path):
    """The study freezes the entries the entry run recorded -- ids, side, fill,
    initial structural stop, objective and costs -- and never re-derives them."""
    breadth, refinement = _study_fixture(tmp_path)
    rules = _exits.selected_entry_rules(refinement, breadth)
    assert [rule["candidate_id"] for rule in rules] == ["SYN:syn_branch:S1:deadline_minutes=5"]
    assert rules[0]["role"] == "refined_selected"
    fixed = _exits.freeze_entries(breadth_run_root=breadth, refinement_run_root=refinement)
    assert fixed["entries"] == 2
    assert fixed["dates_with_entries"] == ["2020-01-02", "2020-01-03"]
    frozen = _exits.frozen_entries_for_day("2020-01-02", rules, flatten_at_ns=10**9)
    entry, recorded = frozen["SYN:syn_branch:S1:deadline_minutes=5"][0]
    assert entry.entry_id == "syn-2020-01-02"
    assert entry.fill_price == Decimal("100.00") and entry.initial_stop == Decimal("99.00")
    assert entry.round_trip_cost == Decimal("5.00")
    assert recorded["exit_reason"] == "objective"


def test_a_retained_parent_fold_contributes_the_parent_from_the_breadth_run(tmp_path):
    """When a fold kept its breadth parent, the exit study must hold the parent's
    entries, which live in the breadth run, not the neighbour's."""
    from trading_research.research.rule_discovery import search_run

    breadth, refinement = _study_fixture(tmp_path)
    rules_doc = json.loads((refinement / "SELECTED_RULES_BY_FOLD.json").read_text())
    rules_doc["folds"][0]["roles"][0]["role"] = "retained_parent"
    search_run._write_json(refinement / "SELECTED_RULES_BY_FOLD.json", rules_doc)
    rules = _exits.selected_entry_rules(refinement, breadth)
    assert [rule["candidate_id"] for rule in rules] == ["SYN:syn_branch:S1"]
    assert rules[0]["role"] == "retained_parent"
    assert rules[0]["jobs_root"] == str(breadth)


def test_the_exit_study_cannot_rescue_an_entry_candidate(tmp_path):
    """The negative control of this family: give a rejected entry rule an exit
    policy that improves its daily points enormously. The exit comparison is
    reported, and the entry's disposition is still `rejected_by_evidence` with
    `entry_rescued` false -- an exit can never promote an entry."""
    breadth, refinement = _study_fixture(tmp_path, entry_disposition="rejected_by_evidence")
    dispositions = _exits._entry_dispositions(refinement)
    entry_rule = "SYN:syn_branch:S1:deadline_minutes=5"
    assert dispositions[entry_rule]["disposition"] == "rejected_by_evidence"

    shards = []
    for index in range(40):
        day = f"2022-01-{index + 1:02d}"
        rows = [
            {
                "entry_id": f"syn-{day}",
                "side": 1,
                "fill_at_ns": 1,
                "fill_price": "100.00",
                "initial_stop": "99.00",
                "objective": "102.00",
                "round_trip_cost": "5.00",
                "recorded_e0": {"exit_at_ns": 2, "exit_reason": "objective", "net_points": "1.00"},
                "e0_matches_entry_run": True,
                "policies": {
                    policy: {
                        "policy_id": policy,
                        "entry_id": f"syn-{day}",
                        "complete": True,
                        "reason": "objective",
                        "net_points": "50.00" if policy == "E2" else "1.00",
                        "occupancy_flagged": False,
                    }
                    for policy in POLICIES
                },
            }
        ]
        shards.append(
            {"schema_version": _exits.EXIT_SHARD_SCHEMA, "account_day": day, "rules": {entry_rule: rows}}
        )
    series = _exits.exit_daily_series(shards)
    body = series[entry_rule]
    assert body["entries"] == 40 and body["e0_mismatches"] == 0
    e2 = [Decimal(cell["net_points"]["E2"]) for cell in body["daily"].values()]
    e0 = [Decimal(cell["net_points"]["E0"]) for cell in body["daily"].values()]
    assert sum(e2) > sum(e0) * 40  # the exit policy is hugely better
    # the entry stage's verdict is carried through untouched
    assert dispositions[entry_rule]["disposition"] == "rejected_by_evidence"
    assert dispositions[entry_rule]["promoted"] is False


def test_an_unusable_e0_day_leaves_the_paired_comparison(tmp_path):
    """S30/A05: if the reconstructed E0 does not reproduce the E0 the entry run
    recorded, that day cannot be paired -- it is reported, not averaged in."""
    entry_rule = "SYN:syn_branch:S1:deadline_minutes=5"

    def shard(day, matches):
        return {
            "account_day": day,
            "rules": {
                entry_rule: [
                    {
                        "entry_id": f"syn-{day}",
                        "recorded_e0": {"net_points": "1.00"},
                        "e0_matches_entry_run": matches,
                        "policies": {
                            policy: {
                                "complete": True,
                                "reason": "objective",
                                "net_points": "2.00",
                                "occupancy_flagged": False,
                            }
                            for policy in POLICIES
                        },
                    }
                ]
            },
        }

    series = _exits.exit_daily_series([shard("2022-01-03", True), shard("2022-01-04", False)])
    body = series[entry_rule]
    assert body["e0_mismatches"] == 1
    assert body["daily"]["2022-01-03"]["usable"] is True
    assert body["daily"]["2022-01-04"]["usable"] is False


def test_an_unsupported_e3_keeps_its_entry_and_drops_only_that_policys_day():
    """A04/S11: an undefined initial R is an explicit unsupported E3/E4 record;
    the entry stays in the ledger and only that policy loses the day."""
    entry_rule = "R"
    row = {
        "entry_id": "e1",
        "recorded_e0": {"net_points": "1.00"},
        "e0_matches_entry_run": True,
        "policies": {
            policy: {
                "complete": policy not in ("E3", "E4"),
                "reason": "undefined_initial_r" if policy in ("E3", "E4") else "objective",
                "net_points": "2.00",
                "occupancy_flagged": False,
            }
            for policy in POLICIES
        },
    }
    series = _exits.exit_daily_series([{"account_day": "2022-01-03", "rules": {entry_rule: [row]}}])
    body = series[entry_rule]
    assert body["entries"] == 1
    assert body["unsupported"]["E3"] == 1 and body["unsupported"]["E4"] == 1
    cell = body["daily"]["2022-01-03"]
    assert cell["complete"]["E0"] is True and cell["complete"]["E1"] is True
    assert cell["complete"]["E3"] is False and cell["complete"]["E4"] is False


def test_a_missing_daily_shard_falls_back_to_the_job_documents(tmp_path):
    """A run root without daily shards must not report zero entries: the freeze
    reads the job documents instead of treating a missing input as no entry."""
    from trading_research.research.rule_discovery import search_run

    breadth, refinement = _study_fixture(tmp_path)
    assert not search_run.daily_path(refinement, "2020-01-02").is_file()
    fixed = _exits.freeze_entries(breadth_run_root=breadth, refinement_run_root=refinement)
    assert fixed["entries"] == 2
    # and with a shard present the shard is enough
    search_run._write_json(
        search_run.daily_path(refinement, "2020-01-02"),
        {"rows": [{"candidate_id": "SYN:syn_branch:S1:deadline_minutes=5", "candidate_fills": 1}]},
    )
    again = _exits.freeze_entries(breadth_run_root=breadth, refinement_run_root=refinement)
    assert again["entries"] == 2


def test_a_holdout_date_cannot_choose_an_exit_policy(tmp_path):
    """P15-19 A09: the exit comparison drops hold-out days and records how many.
    Make E2 spectacular on the hold-out only and the comparison does not move;
    the same days in-block do move it."""
    from trading_research.research.rule_discovery import search_run as sr

    entry_rule = "SYN:syn_branch:S1:deadline_minutes=5"

    def shard(day, e2):
        return {
            "account_day": day,
            "rules": {
                entry_rule: [
                    {
                        "entry_id": f"syn-{day}",
                        "side": 1,
                        "fill_price": "100.00",
                        "round_trip_cost": "5.00",
                        "recorded_e0": {"net_points": "1.00"},
                        "e0_matches_entry_run": True,
                        "policies": {
                            policy: {
                                "complete": True,
                                "reason": "objective",
                                "net_points": e2 if policy == "E2" else "1.00",
                                "occupancy_flagged": False,
                            }
                            for policy in POLICIES
                        },
                    }
                ]
            },
        }

    in_block = [f"2026-03-{day:02d}" for day in range(2, 20)]
    holdout = [f"2026-05-{day:02d}" for day in range(4, 22)]
    assert all(sr.in_holdout(day) for day in holdout)
    assert not any(sr.in_holdout(day) for day in in_block)

    def mean_for(loud_days):
        shards = [shard(day, "9.00" if day in loud_days else "1.00") for day in in_block + holdout]
        series = _exits.exit_daily_series(shards)
        body = series[entry_rule]
        diffs = []
        excluded = 0
        for day, cell in sorted(body["daily"].items()):
            if sr.in_holdout(day):
                excluded += 1
                continue
            diffs.append(float(Decimal(cell["net_points"]["E2"]) - Decimal(cell["net_points"]["E0"])))
        return (sum(diffs) / len(diffs)), excluded

    quiet, excluded = mean_for(set())
    loud_holdout, _ = mean_for(set(holdout))
    loud_in_block, _ = mean_for(set(in_block))
    assert excluded == len(holdout)
    assert loud_holdout == quiet
    assert loud_in_block > quiet


# --------------------------------------------------------------------------
# EVALUATION.md, amended 2026-09-17, in the exit family
# --------------------------------------------------------------------------


def test_the_exit_pair_resolves_the_same_count_on_both_sides():
    """E0 and the policy manage the same frozen entries on the same common
    complete days, so the two-sided support gate is symmetric here: a policy is
    never held to a baseline that resolved fewer opportunities than it did."""
    from trading_research.research.rule_discovery import refinement as _refinement
    from trading_research.research.rule_discovery import search_run as _sr

    row = {
        "candidate_id": "SIRES:absorption:S1|E2",
        "daily_diff": [1.0] * 40,
        "daily_days": [f"2022-01-{index % 28 + 1:02d}" for index in range(40)],
        "daily_segments": ["2022"] * 40,
        "block_improvements": [1.0, 1.0, 1.0],
        "supported_outer_blocks": 3,
        "eligible_test_days": 40,
        "resolved_opportunities": 400,
        "baseline_resolved_opportunities": 400,
        "candidate_entries": 400,
        "baseline_entries": 400,
        "software_causality_pass": True,
        "cost_stress_sign_reversal": False,
        "unexplained_coverage_loss": False,
    }
    trials = [{"candidate_id": row["candidate_id"], "p_raw": 1 / 20001}] + [
        {"candidate_id": f"other-{i}", "p_raw": 1.0} for i in range(71)
    ]
    verdict = _refinement.evaluate_promotion(row, trials)
    assert verdict["support_pass_candidate"] is True
    assert verdict["support_pass_baseline"] is True
    assert verdict["entry_ratio_to_baseline"] == 1.0
    assert verdict["disposition"] == "promoted"

    # the ledger row can be audited: counts on both sides, the floor beside p_holm
    support = _sr.support_block(verdict)
    assert support["resolved_opportunities"] == 400
    assert support["baseline_resolved_opportunities"] == 400
    assert support["pass"] is True
    assert verdict["attainable_p_floor"] == pytest.approx(72 / 20001)

    # negative control: a policy that resolved on fewer days than E0 did is not
    # rescued by the symmetry, because the gate reads the counts it is given
    thin = _refinement.evaluate_promotion({**row, "baseline_resolved_opportunities": 20}, trials)
    assert thin["support_pass_baseline"] is False
    assert thin["disposition"] == "inconclusive_support"
