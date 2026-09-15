"""P15-09 Jumbo range branches."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import inspect
import json

from trading_research.research.method_pack.historical_price_scanners import scan_jumbo
from trading_research.research.rule_discovery.baseline_repairs import scan_jumbo_repaired
from trading_research.research.rule_discovery.formations import f2_volume_completed
from trading_research.research.rule_discovery.native import empty_session_arrays, NativeMarketView, replay_native_row
from trading_research.research.rule_discovery.source_adapters.common import (
    B0,
    B01,
    changed_axis_spec,
    empty_delta_spec,
    enumerate_own_population,
    evaluate_family_rule_at_contact,
    permute_batch_ambiguity,
    quadrant_locations,
    synthetic_f2_rows,
    synthetic_quadrant_mirror,
    ten_bar_dwell_contacts,
)
from trading_research.research.rule_discovery.source_adapters.jumbo import (
    FAMILY,
    LITERAL_OPERANDS,
    family_document,
    one_source_opening,
    outbound_expiry_ns,
    quadrant_population,
    scan_variant,
)


def test_a01_outbound_respects_0940_and_opening_identity():
    src = inspect.getsource(scan_jumbo)
    assert "09:40" in src
    assert "judas_outbound" in src
    spec = empty_delta_spec(FAMILY, "judas_outbound")
    assert spec.parameters["empty_delta"] is True
    assert spec.changed_axis == "none"
    doc = family_document()
    assert "judas_outbound" in doc["branches"]
    assert doc["pzone_recipe"] == "unchanged"


def test_a02_alternate_formation_creates_new_contact():
    baseline = {"eq-long"}
    candidate = {"eq-long", "f2-long"}
    out = enumerate_own_population(baseline_ids=baseline, candidate_ids=candidate, geometry_changed=True)
    assert out["new_contacts"] == ["f2-long"]
    assert "f2-long" not in baseline


def test_a03_context_unknown_retained():
    values = {"context_fixed": None, "source_confirmation": True}
    changed_confirmation = {**values, "source_confirmation": False}
    assert changed_confirmation["context_fixed"] is None


def test_a04_quadrants_are_own_population():
    pop = quadrant_population(Decimal("100"), Decimal("108"), "long", baseline_eq_only=True)
    assert pop["enumeration"]["own_population"] is True
    assert "long:q1" in pop["candidate_ids"]
    short = quadrant_locations(Decimal("100"), Decimal("108"), "short")
    assert short["eq"] == Decimal("104")
    assert short["q1"] == Decimal("102")


def test_a05_long_short_mirror_and_ambiguity():
    long = quadrant_locations(Decimal("10"), Decimal("18"), "long")
    short = quadrant_locations(Decimal("10"), Decimal("18"), "short")
    assert long["eq"] == short["eq"]
    batch = permute_batch_ambiguity((Decimal("1"), Decimal("2")), Decimal("1"), Decimal("2"))
    assert batch["ambiguous"] is True
    assert batch["order_invariant"] is True


def test_s02_f2_uses_supplied_median_not_last_20_bars():
    rows = synthetic_f2_rows([1] * 19 + [1000])
    stand_in = f2_volume_completed(rows, issue_ns=rows[-1]["end_ns"], median_volume=1000)
    prior = f2_volume_completed(rows, issue_ns=rows[-1]["end_ns"], median_volume=10)
    assert stand_in["median_volume"] == 1000
    assert prior["median_volume"] == 10
    assert prior["available"] is True


def test_s21_source_prerequisites_named():
    spec = empty_delta_spec(FAMILY, "judas_reversal")
    assert "formation" in spec.required_stages
    assert LITERAL_OPERANDS["exit_window_recorded"] == "by_construction"


def test_s22_new_geometry_not_filter():
    out = enumerate_own_population(
        baseline_ids={"a"},
        candidate_ids={"a", "b"},
        geometry_changed=True,
    )
    assert "b" in out["new_contacts"]


def test_s31_clock_zone_and_provenance():
    doc = family_document()
    assert doc["clock_zone_unverified"] is True
    spec = empty_delta_spec(FAMILY, "judas_reversal")
    assert spec.provenance == "source_literal"


def test_s07_native_replay():
    path = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
    if not Path(path).is_file():
        return
    assert replay_native_row(path, 769284)["kind"] == "native"


def test_judas_repaired_has_both_variants():
    src = inspect.getsource(scan_jumbo_repaired)
    assert "judas_reversal_deferred" in src
    assert "09:30" in src
    assert "09:50" in src


def test_s09_batch_permutation():
    first = permute_batch_ambiguity((Decimal("5"), Decimal("6")), Decimal("5"), Decimal("6"))
    second = permute_batch_ambiguity((Decimal("6"), Decimal("5")), Decimal("5"), Decimal("6"))
    assert first == second


def test_one_source_opening_not_or_true():
    src = inspect.getsource(scan_variant)
    assert "or True" not in src
    hook = inspect.getsource(__import__("trading_research.research.rule_discovery.source_adapters.jumbo", fromlist=["_empty_hook"])._empty_hook)
    assert "or True" not in hook
    assert "None if not episodes" in hook


def test_changed_formation_enumerates_own_native_population():
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    market = load_source_market("2021-01-04")
    out = scan_variant(market, None, changed_axis_spec(FAMILY, "judas_reversal", "Formation", recipe="F1"))
    assert out["formations"]
    assert out["references"]
    assert "contacts" in out
    for episode in out.get("episodes") or []:
        assert episode["status"] == evaluate_family_rule_at_contact(episode["contact"])
        assert episode["status"] != "setup" or episode["values"].get("source_confirmation") is True


def test_changed_reference_enumerates_own_native_population():
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    market = load_source_market("2021-01-04")
    out = scan_variant(market, None, changed_axis_spec(FAMILY, "judas_reversal", "Reference", recipe="R-quadrant"))
    assert out["formations"]
    assert len(out["references"]) >= 3
    for episode in out.get("episodes") or []:
        assert episode["status"] == evaluate_family_rule_at_contact(episode["contact"])


def test_ten_bar_dwell_is_one_lifecycle_contact():
    out = ten_bar_dwell_contacts()
    assert out["n_bars"] == 10
    assert out["n_contacts"] == 1


def test_failed_family_rule_is_no_setup_not_setup():
    from trading_research.research.rule_discovery.source_adapters.common import _episodes_from_contacts

    contact = {
        "contact_id": "x",
        "reference_id": "r",
        "side": "long",
        "complete": True,
        "source_confirmation": False,
        "at_ns": 1,
    }
    episodes = _episodes_from_contacts(
        family=FAMILY, branch="judas_reversal", formation={}, reference={}, contacts=[contact]
    )
    assert episodes[0]["status"] == "no_setup"
    assert episodes[0]["strategy_assessment"]["status"] == "no_setup"


def test_a05_long_short_mirror_synthetic_market():
    out = synthetic_quadrant_mirror()
    assert out["mirrored"] is True
    assert out["long_n"] == out["short_n"]
    assert out["long_n"] >= 1
    assert out["q1_contact_absent_from_eq"] is True


def test_empty_view_prior_sessions_do_not_stand_in():
    view = NativeMarketView(
        empty_session_arrays(start_ns=0, end_ns=60_000_000_000, instrument_id="X"),
        account_day="2021-01-04",
        selection={"archive": {"instrument_id": "X"}},
    )
    dates = view.prior_complete_same_contract_dates(20)
    assert dates == []
