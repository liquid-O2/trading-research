from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from trading_research.research.method_pack.adapters import normalize_trade_row
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.objects.profiles import (
    Coverage,
    InstrumentDefinition,
    ProfileDefinition,
    ProfileError,
    ProfileReference,
    ProfileWindow,
    SOURCE_VALUE_AREA_CONFIGS,
    ValueAreaConfig,
    build_profile,
    compose_profiles,
    native_o077,
    o065,
    o069,
    o073,
    o077,
    sires_overnight_window,
    snapshot_payload,
)


DAY = date(2026, 6, 12)


def _instrument(known_at: int = 1) -> InstrumentDefinition:
    return InstrumentDefinition("nq-42004058-v1", 42004058, Decimal("0.25"), known_at)


def _definition(
    *,
    profile_id: str = "NQ:2026-06-12:rth",
    kind: str = "prior_rth",
    start: int = 10,
    end: int = 100,
    va: ValueAreaConfig | None = None,
    poc_tie_policy: str | None = None,
) -> ProfileDefinition:
    window = ProfileWindow(f"window:{profile_id}", kind, DAY, start, end)
    return ProfileDefinition(profile_id, _instrument(), window, 2, "fixture-source",
                             poc_tie_policy=poc_tie_policy, value_area=va)


def _trade(t: int, price: str, size: int, side: str, row: int, *, instrument: int = 42004058):
    return normalize_trade_row(
        {"t": t, "price": price, "size": size, "side": side,
         "instrument_id": instrument},
        source_file="native-fixture.csv", source_row=row,
    )


def _coverage(start: int = 10, end: int = 100) -> Coverage:
    return Coverage("complete", start, end, coverage_id="fixture-coverage")


def test_native_profile_preserves_side_rows_unknown_volume_and_full_o077_payload():
    definition = _definition(poc_tie_policy="lowest")
    events = [
        _trade(20, "100", 7, "B", 1),
        _trade(21, "100", 4, "A", 2),
        _trade(22, "100", 2, "N", 3),
        _trade(23, "100.25", 2, "B", 4),
        _trade(24, "100.25", 5, "A", 5),
    ]
    profile = build_profile(definition, events, as_of=100, coverage=_coverage())

    first = profile.row("100")
    assert first is not None
    assert (first.buy_volume, first.sell_volume, first.unknown_volume) == (7, 4, 2)
    assert first.total_volume == 13
    assert first.full_delta is None
    assert (first.known_delta, first.delta_low, first.delta_high) == (3, 1, 5)
    assert sum(row.total_volume for row in profile.rows) == profile.total_volume == 20

    signed = o077({"profile": profile})
    assert signed.value["buy_by_price"] == {"100": 7, "100.25": 2}
    assert signed.value["sell_by_price"] == {"100": 4, "100.25": 5}
    assert signed.value["unknown_by_price"] == {"100": 2, "100.25": 0}
    assert signed.value["delta_by_price"] == {"100": None, "100.25": -3}
    assert signed.value["known_window_delta"] == 0
    assert signed.value["window_delta"] is None
    assert signed.value["delta_interval"] == [-2, 2]
    assert signed.value["aggressor_convention"] == "B_buy_A_sell_N_unknown"


def test_developing_snapshots_are_immutable_and_append_invariant():
    definition = _definition(profile_id="NQ:2026-06-12:developing-rth", kind="developing_rth")
    early_events = [_trade(20, "100", 10, "B", 1), _trade(30, "101", 5, "A", 2)]
    future = _trade(60, "101", 10, "B", 3)

    early = build_profile(definition, early_events, as_of=50, coverage=_coverage(10, 50))
    rebuilt_after_append = build_profile(definition, [*early_events, future], as_of=50,
                                         coverage=_coverage(10, 50))
    later = build_profile(definition, [*early_events, future], as_of=70,
                          coverage=_coverage(10, 70))

    assert early == rebuilt_after_append
    assert early.snapshot_id == rebuilt_after_append.snapshot_id
    assert early.poc == 100 and later.poc == 101
    assert early.row("101").total_volume == 5 and later.row("101").total_volume == 15
    assert early.row("100.25").total_volume == 0  # covered, known-empty native tick
    with pytest.raises(FrozenInstanceError):
        early.poc = Decimal("101")


def test_value_area_fractions_are_separate_and_ties_need_an_explicit_policy():
    assert {key: config.fraction for key, config in SOURCE_VALUE_AREA_CONFIGS.items()} == {
        "common_70": Decimal("0.70"),
        "sires_intraday_40": Decimal("0.40"),
        "saint_68": Decimal("0.68"),
    }
    assert all(config.algorithm is None and config.tie_policy is None
               for config in SOURCE_VALUE_AREA_CONFIGS.values())

    events = [
        _trade(20, "100", 4, "B", 1),
        _trade(21, "100.25", 10, "B", 2),
        _trade(22, "100.50", 4, "B", 3),
    ]
    lower = ValueAreaConfig("comparison-70-lower", Decimal(".70"),
                            "adjacent_single", "lower")
    upper = ValueAreaConfig("comparison-70-upper", Decimal(".70"),
                            "adjacent_single", "upper")
    low_profile = build_profile(_definition(profile_id="low", va=lower), events,
                                as_of=100, coverage=_coverage())
    high_profile = build_profile(_definition(profile_id="high", va=upper), events,
                                 as_of=100, coverage=_coverage())
    unresolved = build_profile(_definition(profile_id="source", va=SOURCE_VALUE_AREA_CONFIGS["common_70"]),
                               events, as_of=100, coverage=_coverage())

    assert (low_profile.val, low_profile.vah) == (Decimal("100"), Decimal("100.25"))
    assert (high_profile.val, high_profile.vah) == (Decimal("100.25"), Decimal("100.50"))
    assert low_profile.achieved_value_fraction == high_profile.achieved_value_fraction == Decimal(14) / Decimal(18)
    assert unresolved.val is unresolved.vah is None
    assert "HOLE:O062:construction" in unresolved.coverage_holes


def test_poc_tie_retains_all_candidates_until_named_rule_is_supplied():
    events = [_trade(20, "100", 10, "B", 1), _trade(21, "100.25", 10, "A", 2)]
    unresolved = build_profile(_definition(profile_id="tie"), events, as_of=100,
                               coverage=_coverage())
    highest = build_profile(_definition(profile_id="tie-high", poc_tie_policy="highest"),
                            events, as_of=100, coverage=_coverage())
    assert unresolved.poc is None
    assert unresolved.poc_candidates == (Decimal("100"), Decimal("100.25"))
    assert unresolved.poc_tie_state == "unresolved"
    assert highest.poc == Decimal("100.25") and highest.poc_tie_state == "resolved"


def test_missing_coverage_is_unknown_and_cannot_certify_an_untested_reference():
    definition = _definition()
    events = [_trade(20, "100", 2, "B", 1), _trade(30, "101", 1, "A", 2)]
    unavailable = Coverage("unavailable", None, None, ("HOLE:tape_gap",))
    profile = build_profile(definition, events, as_of=100, coverage=unavailable)
    assert profile.coverage_ok is None
    assert snapshot_payload(profile)["coverage"]["ok"] is None
    assert profile.row("100.25") is None  # a tape gap cannot be manufactured into zero volume

    reference = ProfileReference("older-poc-a", profile.profile_id,
                                 profile.snapshot_id, "poc", Decimal("101"), 100)
    absent = o065({"reference": reference, "as_of": 150, "coverage": unavailable,
                   "resolved_members": []})
    witnessed = o065({"reference": reference, "as_of": 150, "coverage": unavailable,
                      "resolved_members": [{"event_id": "touch", "event_ns": 120,
                                            "price": Decimal("101")} ]})
    assert absent.value["untested_at_decision"] is None
    assert absent.coverage_ok is None
    assert witnessed.value["untested_at_decision"] is False
    assert witnessed.value["first_qualifying_visit"]["event_id"] == "touch"


def test_scalar_untested_poc_helper_never_invents_reference_or_visit_identity():
    untouched = o065({"poc": 101, "known_at": 100, "as_of": 150,
                      "coverage_complete": True, "visits": []})
    touched = o065({"poc": 101, "known_at": 100, "as_of": 150,
                    "coverage_complete": True,
                    "visits": [{"t": 120, "price": 101}]})

    assert untouched.value["untested_at_decision"] is True
    assert touched.value["untested_at_decision"] is False
    assert untouched.value["active_reference_id"] is None
    assert untouched.value["profile_id"] is None
    assert untouched.value["snapshot_id"] is None
    assert touched.value["first_qualifying_visit"]["event_id"] is None
    assert {"HOLE:O065:reference_id", "HOLE:O065:profile_id",
            "HOLE:O065:snapshot_id"} <= set(untouched.hole_ids)
    assert "HOLE:O065:visit_identity" in touched.hole_ids
    assert untouched.state == touched.state == "hole"


def test_same_price_references_and_ledges_keep_distinct_identity():
    a = ProfileReference("poc-profile-a", "profile-a", "snapshot-a", "poc", 100, 20)
    b = ProfileReference("poc-profile-b", "profile-b", "snapshot-b", "poc", 100, 30)
    assert a.price == b.price and a.reference_id != b.reference_id

    mismatch = o069({"ledge_id": "ledge-a", "retest_ledge_id": "ledge-b",
                     "ledge_px": 100, "retest_px": 100, "known_at": 40})
    matched = o069({"ledge_id": "ledge-a", "retest_ledge_id": "ledge-a",
                    "ledge_px": 100, "retest_px": 100, "known_at": 40})
    assert mismatch.value["same_price"] is True
    assert mismatch.value["same_id"] is False
    assert matched.value["same_id"] is True


def test_composite_requires_explicit_compatible_parents_and_disjoint_ownership():
    first = build_profile(_definition(profile_id="prior-rth-a", start=10, end=40),
                          [_trade(20, "100", 3, "B", 1), _trade(21, "101", 2, "A", 2)],
                          as_of=40, coverage=_coverage(10, 40))
    second = build_profile(_definition(profile_id="prior-rth-b", start=40, end=80),
                           [_trade(50, "100", 4, "B", 3), _trade(51, "101", 1, "A", 4)],
                           as_of=80, coverage=_coverage(40, 80))
    composite = compose_profiles(composite_id="explicit-composite", profiles=[first, second],
                                 selection_known_at=90, rationale="source selected both auctions")
    assert composite.parent_ids == (first.snapshot_id, second.snapshot_id)
    assert {row.price: row.total_volume for row in composite.rows
            if row.total_volume} == {
        Decimal("100"): 7, Decimal("101"): 3,
    }
    assert composite.total_volume == 10

    duplicate = build_profile(_definition(profile_id="duplicate", start=10, end=40),
                              [_trade(20, "100", 3, "B", 1)], as_of=40,
                              coverage=_coverage(10, 40))
    with pytest.raises(ProfileError, match="overlapping canonical event ownership"):
        compose_profiles(composite_id="bad", profiles=[first, duplicate],
                         selection_known_at=90, rationale="invalid overlap")


def test_dated_prior_eth_overnight_rth_and_selected_ranges_do_not_alias():
    ids = {}
    for kind in ("prior_rth", "prior_eth", "overnight", "developing_rth", "selected_range"):
        profile = build_profile(_definition(profile_id=f"dated:{kind}", kind=kind),
                                [_trade(20, "100", 1, "B", 1)], as_of=100,
                                coverage=_coverage())
        ids[kind] = (profile.profile_id, profile.snapshot_id, profile.window_id)
    assert len({identity for triple in ids.values() for identity in triple}) == 15


def test_sires_overnight_is_bound_to_o011_window_and_later_hold_is_not_preopen_data():
    window = sires_overnight_window(DAY)
    definition = ProfileDefinition("sires:on:2026-06-12", _instrument(window.start - 1),
                                   window, window.start, "sires-mamt",
                                   poc_tie_policy="lowest")
    events = [_trade(window.start + 1, "100", 5, "B", 1),
              _trade(window.end - 1, "101", 3, "A", 2)]
    profile = build_profile(definition, events, as_of=window.end,
                            coverage=Coverage("complete", window.start, window.end))
    older = ProfileReference("older:poc", "older-profile", "older-snapshot",
                             "poc", Decimal("100.5"), window.start)
    result = o073({"profile": profile, "source": "sires", "lvn_band": [100, 101],
                   "older_poc_reference": older, "use_at": window.end,
                   "opening_response": {"kind": "hold", "known_at": window.end + 1}})
    assert result.value["source_clock_id"] == "O011:sires_overnight_1800_0930_et"
    assert result.value["older_poc_alignment"] is True
    assert result.value["opening_response"] is None
    assert result.value["opening_response_available"] is False


def test_instrument_definition_tick_and_native_identity_are_enforced():
    definition = _definition()
    off_tick = [_trade(20, "100.10", 1, "B", 1)]
    wrong_instrument = [_trade(20, "100", 1, "B", 1, instrument=999)]
    with pytest.raises(ProfileError, match="not aligned"):
        build_profile(definition, off_tick, as_of=100, coverage=_coverage())
    with pytest.raises(ProfileError, match="instrument"):
        build_profile(definition, wrong_instrument, as_of=100, coverage=_coverage())


class _Resolved:
    def __init__(self, definition, rows, coverage_ok=True):
        self.instrument_id = definition.instrument.instrument_id
        self.start_ns = definition.window.start
        self.end_ns = definition.window.end
        self.known_at = max(row["known_at"] for row in rows)
        self.coverage_ok = coverage_ok
        # Native adapters bind tick identity from the resolver-owned definition,
        # never from the profile configuration being tested.
        self.instrument_definition = type("ResolvedInstrumentDefinition", (), {
            "definition_id": definition.instrument.definition_id,
            "instrument_id": definition.instrument.instrument_id,
            "tick_size": definition.instrument.tick_size,
            "known_at": definition.instrument.known_at,
        })()
        self._rows = rows

    def rows(self):
        return list(self._rows)


def test_native_boundary_adapter_uses_resolved_members_instead_of_summary_levels():
    definition = _definition(profile_id="native-signed")
    rows = [_trade(20, "100", 7, "B", 1), _trade(21, "100", 4, "A", 2)]
    result = native_o077({"profile_definition": definition,
                          "levels": [{"B": 999, "A": 0}]},
                         _Resolved(definition, rows))
    assert result.value["known_window_delta"] == 3
    assert result.value["total"] == 11
    assert result.value["buy_by_price"] == {"100": 7}
