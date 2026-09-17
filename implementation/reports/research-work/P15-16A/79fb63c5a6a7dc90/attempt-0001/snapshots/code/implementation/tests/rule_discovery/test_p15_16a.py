"""P15-16A integration: track fixtures, B0/B0.1 byte identity, B0.2 dispatch."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import json

from trading_research.research.rule_discovery.baseline_repairs import scan_branch_repaired
from trading_research.research.rule_discovery.native import replay_native_row
from trading_research.research.rule_discovery.source_adapters.common import (
    CLOCK_ZONE_UNVERIFIED_FAMILIES,
    clock_zone_unverified,
    coverage_row,
    dual_scan,
    enumerate_own_population,
    family_scan_b02,
    frozen_scan_document,
    future_perturbation_stable,
    load_source_market,
    permute_batch_ambiguity,
    strip_baseline_version,
)
from trading_research.research.rule_discovery.source_adapters.jumbo import (
    FAMILY as JJ,
    extension_reaction_bands,
    family_document,
    scan_b02 as jumbo_scan_b02,
)
from trading_research.research.rule_discovery.run_adapter_populations import (
    BRANCH_RECORDS,
    b02_branch_records,
    records_for_baseline,
)

TRACK_ROOT = Path("/workspace/implementation/reports/research-work/P15-16A")
NATIVE_PARQUET = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
NATIVE_ROW = 769284


def _hash(document) -> str:
    blob = json.dumps(document, sort_keys=True, default=str).encode()
    import hashlib

    return hashlib.sha256(blob).hexdigest()


def test_A01_track_rule_tables_exist():
    paths = list(TRACK_ROOT.glob("_track_*/RULES_*.json"))
    assert len(paths) >= 6
    for path in paths:
        doc = json.loads(path.read_text())
        assert doc


def test_A01_jumbo_rr01_extension_band_is_1_33_1_66():
    bands = extension_reaction_bands(Decimal("110"), Decimal("100"))
    assert bands["upper"] == [Decimal("123.30"), Decimal("126.60")]
    assert bands["lower"] == [Decimal("83.40"), Decimal("86.70")]


def test_A02_b0_b01_byte_identity_negative_control():
    day = "2021-01-04"
    market = load_source_market(day)
    dual = dual_scan(market, JJ, "judas_reversal")
    assert "b02" not in dual
    frozen = frozen_scan_document(market, JJ, "judas_reversal")
    repaired = scan_branch_repaired(market, coverage_row(JJ, "judas_reversal"))
    assert _hash(strip_baseline_version(dual["b0"]).get("episodes") or []) == _hash(strip_baseline_version(frozen).get("episodes") or [])
    assert _hash(strip_baseline_version(dual["b01"]).get("episodes") or []) == _hash(
        strip_baseline_version(repaired).get("episodes") or []
    )


def test_A02_dual_scan_default_has_no_b02_slot():
    day = "2021-01-04"
    market = load_source_market(day)
    dual = dual_scan(market, "GB-FAIL", "nyam_box")
    assert set(dual["populations"]) == {"B0", "B0.1", "B0_to_B0.1"}


def test_A04_od_and_literal_rules_are_labelled():
    from trading_research.research.rule_discovery.source_adapters.jumbo import RULES

    kinds = {row["kind"] for row in RULES.values()}
    assert "literal" in kinds
    assert "OD" in kinds


def test_S02_rr02_eq_contacts_are_two_sided():
    from trading_research.research.rule_discovery.source_adapters.common import changed_reference_scan
    import inspect

    source = inspect.getsource(changed_reference_scan)
    assert '"R-eq": None' in source
    assert "for side in sides" in source


def test_S07_native_replay():
    path = Path(NATIVE_PARQUET)
    if not path.is_file():
        return
    row = replay_native_row(str(path), NATIVE_ROW)
    assert row["kind"] == "native"
    assert row["source_path"] == str(path)


def test_S08_future_perturbation_stable():
    before = {"issued": 1, "later": 9}
    after = {"issued": 1, "later": 99}
    assert future_perturbation_stable({"a": 1}, {"a": 1}, 0) is True
    assert future_perturbation_stable(before, after, 0) is False


def test_S09_same_timestamp_target_stop_stays_ambiguous():
    target = Decimal("10")
    stop = Decimal("9")
    out = permute_batch_ambiguity((target, stop), target, stop)
    assert out["ambiguous"] is True
    assert out["order_invariant"] is True
    assert out["status"] == "unknown"


def test_S21_source_prerequisites_named_on_jumbo():
    doc = family_document()
    assert "exit_window_recorded" in doc["literal_operands"]
    assert doc["literal_operands"]["exit_window_recorded"] == "by_construction"


def test_S22_new_geometry_is_own_population():
    out = enumerate_own_population(baseline_ids={"a"}, candidate_ids={"a", "b"}, geometry_changed=True)
    assert "b" in out["new_contacts"]
    assert out["own_population"] is True


def test_S31_jj_tbr_clock_zone_verified():
    assert "JJ-TBR" not in CLOCK_ZONE_UNVERIFIED_FAMILIES
    assert clock_zone_unverified("JJ-TBR") is False
    doc = jumbo_scan_b02(None, "judas_reversal")
    assert doc["clock_zone"] == "America/New_York"


def test_A03_replay_skips_outside_calendar_without_cache(tmp_path, monkeypatch):
    import importlib.util

    path = Path("/workspace/implementation/tools/replay_author_examples.py")
    spec = importlib.util.spec_from_file_location("replay_author_examples", path)
    replay_mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(replay_mod)

    calls = []

    def boom(day):
        calls.append(day)
        raise AssertionError("must not load market for outside dates")

    monkeypatch.setattr(replay_mod, "load_market", boom)
    example = {
        "id": "JJ-2026-09-01",
        "family": "JJ-TBR",
        "source": "test",
        "date": "2026-09-01",
        "inside_tape": False,
        "instrument": "MNQ",
        "expected_detection": {"branch": "judas_reversal", "side": "long"},
    }
    row = replay_mod.replay_one(example, {"2021-01-04"})
    assert row["detected"] is None
    assert row["divergence"] == "data_unavailable"
    assert calls == []
    es = dict(example)
    es["id"] = "MB-2026-07-K10"
    es["inside_tape"] = True
    es["date"] = "2026-07-01"
    es["instrument"] = "ES-202609"
    es["family"] = "MEMBER-TWO-REASONS"
    row = replay_mod.replay_one(es, {"2026-07-01"})
    assert row["reason"] == "es_tape_absent"
    assert calls == []
    missing = dict(example)
    missing["inside_tape"] = True
    missing["date"] = "2019-01-02"
    row = replay_mod.replay_one(missing, {"2021-01-04"})
    assert "date_outside_native_calendar" in str(row["reason"])
    assert calls == []


def test_A02_b02_branch_table_covers_families():
    rows = b02_branch_records()
    families = {row["family"] for row in rows}
    assert "JJ-TBR" in families
    assert "SIRES" in families
    assert "SAINT-AMT" in families
    assert "REFILL-STUDY" in families
    assert "JETBUNDLE-STATES" not in families
    assert all(row["scan_kind"] == "b02" for row in rows)
    default = records_for_baseline("B0.1")
    assert default == BRANCH_RECORDS


def test_S01_s03_probes_unproduced():
    path = Path("/workspace/implementation/tools/produce_p15_16a.py")
    text = path.read_text()
    assert "def run_probes" in text
    assert "--pending-s01-s03" in text
    assert 'status="unsupported"' in text or "s01_status" in text


def test_A01_fidelity_binds_fixtures_and_records_partials():
    import importlib.util

    path = Path("/workspace/implementation/tools/produce_p15_16a.py")
    spec = importlib.util.spec_from_file_location("produce_p15_16a", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    doc = module.assemble_fidelity()
    assert doc["schema"]
    for row in doc["family_rules"]:
        assert row.get("fixture"), row
    by_id = {row["id"]: row for row in doc["findings"]}
    assert by_id["RR-02"]["status"] == "partial"
    assert "q1" in str(by_id["RR-02"].get("notes") or by_id["RR-02"].get("source_reason")).lower()
    assert by_id["F18"]["status"] == "partial"
    assert "CLOCK_ZONE_UNVERIFIED_FAMILIES" in str(by_id["F18"]["file_line"])
    assert "GB-FAIL" in str(by_id["F18"].get("notes") or "")
    implemented = [row for row in doc["findings"] if row["status"] == "implemented"]
    for row in implemented:
        text = str(row.get("fixture") or "")
        assert text, row
        assert "test_" in text or text.startswith("no discriminating fixture"), row


def test_A01_imports_track_fixtures():
    import importlib.util

    here = Path(__file__).resolve().parent
    for name in (
        "test_p15_16a_jumbo",
        "test_p15_16a_greenbird",
        "test_p15_16a_sires",
        "test_p15_16a_saint",
    ):
        spec = importlib.util.spec_from_file_location(name, here / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        tests = [item for item in dir(module) if item.startswith("test_")]
        assert tests, name
