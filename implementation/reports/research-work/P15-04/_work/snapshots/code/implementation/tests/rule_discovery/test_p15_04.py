"""P15-04 source reconstruction: printed arithmetic, B0.1 overrides, ledger honesty."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import json

import pytest

from trading_research.research.contracts.outcomes import first_passage
from trading_research.research.method_pack.clocks import datetime_ns
from trading_research.research.rule_discovery.reconstruction import (
    B0,
    B01,
    RULE_BIGTRADES,
    RULE_TBR_15,
    apply_source_check_results,
    big_trades_qualifies,
    big_trades_session,
    build_ledger_rows,
    conventional_horizon_move,
    dependency_limits,
    ledger_document,
    log_space_iv_bands,
    max_pain_strike,
    override_for_adapters,
    printed_ev_percent,
    printed_refill_geometry,
    range_deviation_ladder,
    regime_dimensions,
    require_source_stages,
    source_checks_template,
    tbr_projection_levels,
    unknown_stays_unknown,
    validate_ledger,
)


def _et_ns(year: int, month: int, day: int, hour: int, minute: int = 0) -> int:
    from zoneinfo import ZoneInfo
    local = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("America/New_York"))
    return int(local.timestamp() * 1_000_000_000)


def test_a02_conventional_ev_fixture_gives_10():
    move = conventional_horizon_move(Decimal("100"), Decimal("0.2"), Decimal("0.25"))
    assert move == Decimal("10")
    serialized = {"spot": "100", "sigma": "0.2", "T": "0.25", "points": str(move)}
    assert Decimal(json.loads(json.dumps(serialized))["points"]) == Decimal("10")


def test_a02_negative_ev_is_rejected():
    with pytest.raises(Exception):
        conventional_horizon_move(Decimal("0"), Decimal("0.2"), Decimal("0.25"))


def test_bigtrades_london_80_b01_not_b0():
    london = _et_ns(2024, 6, 3, 4, 0)
    ny = _et_ns(2024, 6, 3, 10, 0)
    assert big_trades_session(london) == "london"
    assert big_trades_session(ny) == "ny"
    assert big_trades_qualifies(80, "london", version=B01) is True
    assert big_trades_qualifies(80, "london", version=B0) is False
    assert big_trades_qualifies(80, "ny", version=B01) is False
    assert big_trades_qualifies(80, "ny", version=B0) is False
    assert big_trades_qualifies(100, "ny", version=B0) is True


def test_tbr_1_5_between_1_33_and_1_66():
    low, high = Decimal("10000"), Decimal("10100")
    b0 = tbr_projection_levels(low, high, version=B0)
    b01 = tbr_projection_levels(low, high, version=B01)
    assert "1.5" not in b0["upper"]
    one_five = b01["upper"]["1.5"]
    assert b01["upper"]["1.33"] < one_five < b01["upper"]["1.66"]
    width = high - low
    assert one_five == high + width * Decimal("1.5")
    assert (one_five - (high + width * Decimal("1.33"))) / width == Decimal("0.17")


def test_max_pain_printed_definition():
    contracts = [
        {"strike": "100", "right": "CALL", "oi": "10"},
        {"strike": "100", "right": "PUT", "oi": "1"},
        {"strike": "90", "right": "PUT", "oi": "50"},
        {"strike": "110", "right": "CALL", "oi": "50"},
    ]
    result = max_pain_strike(contracts)
    assert result["available"] is True
    assert result["oi_clock"] == "prior_date"
    assert result["consumed_by_phase_15_setup"] is False
    assert result["strike"] == Decimal("100")
    empty = max_pain_strike([])
    assert empty["available"] is False


def test_range_deviation_ladder_mirrors():
    out = range_deviation_ladder(Decimal("10"), Decimal("20"))
    assert out["h_0.5"] == Decimal("25")
    assert out["l_0.5"] == Decimal("5")
    assert out["h_2.0"] == Decimal("40")


def test_printed_refill_geometry_long():
    geom = printed_refill_geometry(1, Decimal("100"))
    assert geom["entry"] == Decimal("100") - Decimal("0.25") * 12
    assert geom["target"] - geom["entry"] == Decimal("0.25") * 96
    assert geom["entry"] - geom["stop"] == Decimal("0.25") * (32 + 1)


def test_s21_omitted_stage_fails_unless_registered_axis():
    required = ("formation", "contact", "confirmation")
    assert require_source_stages(("formation", "contact", "confirmation"), required) is True
    assert require_source_stages(("formation", "contact"), required) is False
    assert require_source_stages(("formation", "contact"), required, replacement_axis="confirmation") is True


def test_s31_unknown_does_not_become_bool():
    assert unknown_stays_unknown(None) == "unknown"
    assert unknown_stays_unknown("unknown") == "unknown"
    assert unknown_stays_unknown(True) is True


def test_a04_undated_figure_is_not_source_exact_replay():
    rows = build_ledger_rows()
    ev = next(row for row in rows if row.row_id == "L001")
    assert ev.source_exact is False
    assert "A04" in ev.notes or "undated" in ev.notes.lower() or "replay" in ev.notes.lower()


def test_a03_no_pzone_optimizer_flag():
    document = ledger_document()
    assert document["no_pzone_optimizer"] is True
    assert document["no_forward_vol_optimizer"] is True
    assert validate_ledger(document) == []


def test_a01_every_recoverable_row_present():
    document = ledger_document()
    ids = {row["row_id"] for row in document["rows"]}
    for needed in ("L001", "L002", "L003", "L004", "L005", "L006", "L007", "L008", "L009", "L010", "L011", "L012", "L013", "L014", "L015", "L016", "L017", "L018"):
        assert needed in ids
    assert document["row_count"] >= 40
    attrib = next(row for row in document["rows"] if row["row_id"] == "L009")
    assert attrib["disposition"] == "research_alternative_recorded_only"
    assert "no author" in attrib["notes"].lower() or "Not the author's" in attrib["notes"]


def test_a05_ledger_links_without_editing_sources():
    document = ledger_document()
    pine_zip = Path("/workspace/sources/documents/indicators/Pinescript-indicators--main.zip")
    assert pine_zip.is_file()
    for row in document["rows"]:
        assert (
            "sources/" in row["raw_anchor"]
            or row["raw_anchor"].startswith("none")
            or "Pinescript" in row["raw_anchor"]
            or "opened" in row["raw_anchor"]
            or row["raw_anchor"] == ""
        )


def test_overrides_preserve_b0():
    big = override_for_adapters(RULE_BIGTRADES)
    tbr = override_for_adapters(RULE_TBR_15)
    assert big["preserves_b0"] is True
    assert tbr["parameters"]["extension_b0"] == ["1.33", "1.66"]
    assert "1.5" in tbr["parameters"]["extension_b01"]


def test_source_checks_registered_before_replay():
    checks = source_checks_template()
    assert checks["registered_before_replay"] is True
    refill = next(item for item in checks["deterministic_checks"] if item["id"].startswith("refill"))
    assert refill["tolerances"]["hold_rate_pp"] == 5
    assert refill["status"] == "registered"
    filled = apply_source_check_results(
        checks,
        {"hold_rate": 0.10, "per_trade_r": -0.5, "median_winner_dip_ticks": 20, "touches": 10},
        Decimal("10"),
    )
    refill2 = next(item for item in filled["deterministic_checks"] if item["id"].startswith("refill"))
    assert refill2["status"] == "disagree"
    ev = next(item for item in filled["deterministic_checks"] if item["id"].startswith("ev-"))
    assert ev["status"] == "agree"


def test_regime_dimensions_frozen_and_descriptive():
    dims = regime_dimensions()
    assert dims["frozen_before_candidate_results"] is True
    assert dims["no_candidate_threshold_or_date_from_these_tables"] is True
    ids = [item["id"] for item in dims["dimensions"]]
    assert "prior_close_vix_bucket" in ids
    assert "session_bucket" in ids


def test_dependency_limits_name_inferred_operands():
    limits = dependency_limits()
    assert "P15-09" in limits["tasks"]
    assert "P2-03" in limits["tasks"]
    assert any("O018" in item for item in limits["tasks"]["P15-09"]["inferred_or_unavailable"])


def test_s02_first_passage_on_printed_refill_fixture():
    geom = printed_refill_geometry(1, Decimal("100"))
    start = 10
    events = [
        {"event_ns": 11, "available_at_ns": 11, "prices": [geom["entry"] + Decimal("1")]},
        {"event_ns": 12, "available_at_ns": 12, "prices": [geom["target"]]},
    ]
    hit = first_passage(events, start_ns=start, end_ns=20, side=1, entry=geom["entry"], stop=geom["stop"], target=geom["target"])
    assert hit.result == "target_first"
    miss = first_passage(
        [{"event_ns": 11, "available_at_ns": 11, "prices": [geom["stop"]]}],
        start_ns=start,
        end_ns=20,
        side=1,
        entry=geom["entry"],
        stop=geom["stop"],
        target=geom["target"],
    )
    assert miss.result == "stop_first"


def test_log_space_alternative_is_not_a_phase15_candidate():
    bands = log_space_iv_bands(Decimal("20000"), Decimal("16"), convention="sqrt365", k=Decimal("1"))
    assert bands["upper"] > Decimal("20000")
    document = ledger_document()
    alt = next(row for row in document["rows"] if row["row_id"] == "L002")
    assert alt["disposition"] == "research_alternative_recorded_only"


def test_s01_ledger_rejects_missing_required_row():
    document = ledger_document()
    document["rows"] = [row for row in document["rows"] if row["row_id"] != "L003"]
    errors = validate_ledger(document)
    assert errors


def test_printed_ev_percent_uses_sqrt_252():
    pct = printed_ev_percent(Decimal("20"))
    assert abs(float(pct) - 20 / (252 ** 0.5)) < 1e-12


def test_s03_owned_paths_and_override_identity():
    from trading_research.research.contracts.identity import digest, file_digest
    from trading_research.research.rule_discovery.reconstruction import P15_04_OWNED, ROOT
    files = {rel: file_digest(ROOT / rel) for rel in P15_04_OWNED}
    assert len(digest(files)) == 64
    mutated = dict(files)
    mutated["implementation/tests/rule_discovery/test_p15_04.py"] = "0" * 64
    assert digest(mutated) != digest(files)
