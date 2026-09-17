"""P15-16A integration: track fixtures, B0/B0.1 byte identity, B0.2 dispatch."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import json
import sys

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


def test_loader_refuses_date_outside_native_calendar(monkeypatch):
    from trading_research.errors import ContractError
    from trading_research.research.method_pack import event_cache
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    called = []

    def boom(*_a, **_k):
        called.append(True)
        raise AssertionError("build_event_window must not run for a date outside the native calendar")

    monkeypatch.setattr(event_cache, "build_event_window", boom)

    called.clear()
    loaded = False
    try:
        load_source_market("2026-09-03")
        loaded = True
    except AssertionError:
        pass
    except ContractError as exc:
        raise AssertionError(f"frozen session 2026-09-03 must not be refused: {exc}") from exc
    assert loaded or called, "2026-09-03 must pass the calendar guard (load or reach derived cache)"

    called.clear()
    try:
        load_source_market("2026-09-11")
    except ContractError as exc:
        assert "outside the native calendar" in str(exc)
        assert "2026-09-11" in str(exc)
    else:
        raise AssertionError("after-tape date must be refused before the derived cache")
    assert not called, "2026-09-11 must be refused before build_event_window"

    called.clear()
    try:
        load_source_market("2022-01-01")
    except ContractError as exc:
        assert "outside the native calendar" in str(exc)
        assert "2022-01-01" in str(exc)
    else:
        raise AssertionError("in-range non-session date must be refused before the derived cache")
    assert not called, "2022-01-01 must be refused before build_event_window"


def test_track_round1_files_stay_byte_identical():
    import hashlib

    expected = {
        TRACK_ROOT / "_track_jumbo/FUNNEL_JJ-TBR.json": "23aa7991bdb800aae7d591117522e1ec26aa1b8f8fe9a64c2bb747a63d95c4d5",
        TRACK_ROOT / "_track_jumbo/REPLAY_JJ-TBR.json": "4bf6567b085cbd35e14d2b4c239323b7f55070fa84a79be9a44956d646b502b4",
        TRACK_ROOT / "_track_jumbo/RULES_JJ-TBR.json": "d8a1a90fadfc77b1230c7d34ea728fd2031f93594e942c4188bda0e685009e28",
        TRACK_ROOT / "_track_greenbird/FUNNEL_GB-FAIL.json": "415af2eef2e8d2af5eb7b9dbb2f242ec4ba5e334962e2b620688fdfff683fd59",
        TRACK_ROOT / "_track_greenbird/FUNNEL_GB-SCALP.json": "35e65593fd20c0f931a2eaa82d31dd6cc9b2385fe8b2a997ac8ca892b0928d74",
        TRACK_ROOT / "_track_greenbird/FUNNEL_GB-VWAP.json": "d2ad319aaeb64b18735f9c0d2bfade672bb10a4c5fe55edd113cf473d1757756",
        TRACK_ROOT / "_track_greenbird/REPLAY_GB.json": "96fb13cf707de73cec6657df4828989f830d64875de6874c214d66e4dfd6124e",
        TRACK_ROOT / "_track_greenbird/RULES_GB.json": "fb6abaf6988425a259dc7c2d1efbf18ba63efa8600958ac9812183439e57f735",
        TRACK_ROOT / "_track_sires/RULES_SIRES.json": "342e80e2bd2db367aae65ab6fa25f5ffab0f445052226f31a54fd338d841957b",
        TRACK_ROOT / "_track_sires/RULES_REFILL-STUDY.json": "1837fd81aa67eec4734d3fb7f737105f552bbee192e62b840d38d9b061647a08",
        TRACK_ROOT / "_track_sires/REPLAY_SIRES.json": "bd13925f209cf5011a55b43e81affc4d1a15c08d80dfaad2dfd37e23379528cf",
        TRACK_ROOT / "_track_sires/FUNNEL_SIRES.json": "6c10d6cb94e42e712e9f52055bee8d2c10a820cf4a2e0ba17e2210e27f5e3dfa",
        TRACK_ROOT / "_track_sires/FUNNEL_REFILL-STUDY.json": "40f7803cab1a1b809810db62e817f29087b0c1f7373824f52515d63b263ffe6b",
        TRACK_ROOT / "_track_sires/ENTRY_TIMES.json": "98656599bf65a7659e76e81451302f092606ede8a22d1466eecd5476aff39ba2",
        TRACK_ROOT / "_track_sires/REFILL_SLICE.json": "9cacf5487617f544fe86831f85face7d676a8dfe6685a51be4af98daeb47dd47",
        TRACK_ROOT / "_track_saint/FUNNEL_MEMBER-TWO-REASONS.json": "b6c9e313f722f7b9de406c5bb56a43fcc62a57fb369744b3a996113255846860",
        TRACK_ROOT / "_track_saint/FUNNEL_SAINT-AMT.json": "badc59dae64539ed50d9c4049483c06e520d5072ffeda9f1610e63e687a5b742",
        TRACK_ROOT / "_track_saint/REPLAY_SAINT.json": "47ddf0b3cf8ebb33a74d733d9a2c3c5d292093f88008b392846a3eb6987403f7",
        TRACK_ROOT / "_track_saint/RULES_KEANI.json": "d367e2fa89483d8f9f3f79decf3100a28be58777f85753c3cc537788e507cde3",
        TRACK_ROOT / "_track_saint/RULES_MEMBER-TWO-REASONS.json": "f9ab96429b5aa871cf199c11c900a85581714dbe22b7ad5fa90f417c113db2ae",
        TRACK_ROOT / "_track_saint/RULES_SAINT-AMT.json": "ce357cdfabdefbd29675632fbdceec36be69bb298287e3fdd24319077a2572d3",
        TRACK_ROOT / "_track_saint/STATISTICS_SAINT.json": "b70f35a3874075240bcd5f22aa3d25f92cdf665e2d136b60f35c809fe3194c91",
        TRACK_ROOT / "_repair_sires/FUNNEL_SIRES.json": "94c3d84b25c46aa3e41ada2883e8a861dea25c8fd0bb923fa8b9427bfabb3833",
        TRACK_ROOT / "_repair_sires/PLAUSIBILITY_SIRES.json": "da88e5bc34f39dd780dd4d5da8aff1e7a41dcb41d786aa8d36f8e81889112692",
        TRACK_ROOT / "_repair_sires/PLAUSIBILITY_SIRES.md": "4d1d982f357a342a16bad0a8a658335908e5a15af6a81c0dc5573177dc1601fb",
        TRACK_ROOT / "_repair_sires/REPLAY_SIRES.json": "b6e93fe361b19fab1227a347b39980dd458dd473a2d4ab5c6c83eccea901098c",
        TRACK_ROOT / "_repair_sires/ENTRY_TIMES.json": "8b50757f0857fd159d18e82c67b28028b727ccea3d3d1ae48c7364abd7e32001",
        TRACK_ROOT / "_repair_saint/FUNNEL_KEANI-OPEN-ABOVE-VALUE.json": "91bcab1aa6a35af4bf954a7c97b510a54eb517158f176404c3bf0449f09f56b3",
        TRACK_ROOT / "_repair_saint/PLAUSIBILITY_keani.json": "f6e687caea99f0c0d8e1600c8ae1541a20991140fa72619643820117aac3aaf0",
        TRACK_ROOT / "_repair_saint/PLAUSIBILITY_keani.md": "3eda28e709f891873ea36f708b58806e050c446e62183ceb402a1634e2b60bd6",
        TRACK_ROOT / "_repair_saint/PLAUSIBILITY_saint.json": "12048ece9c07564d6d2c6dcd2d76fe784b5ace905e81002948a6a440df11b26e",
        TRACK_ROOT / "_repair_greenbird/PLAUSIBILITY_GB-FAIL.json": "493296fd2988ef8bb86a42fbe3cfa35e3a6897e32fbdbe775f333da9a4846995",
        TRACK_ROOT / "_repair_greenbird/PLAUSIBILITY_GB-FAIL.md": "5581b293f35fb1547ba2316401c7b1b50642dfa3d360a25a5a16900a527bc149",
        TRACK_ROOT / "_repair_greenbird/PLAUSIBILITY_GB-VWAP.json": "d1fddf5245a082e122ce77a1258d4107327df707477229db81a055aa77448723",
        TRACK_ROOT / "_repair_greenbird/PLAUSIBILITY_GB-VWAP.md": "83b62e2cc95da033d545b1bc8ccdddb2195a236cf3ce1f862bc64cfabbcef7ce",
        TRACK_ROOT / "_repair_greenbird/PLAUSIBILITY_GB-SCALP.json": "7903fb439d3acb28a524d7285158eadc670aee09caec128980f650e227b4e60e",
        TRACK_ROOT / "_repair_greenbird/PLAUSIBILITY_GB-SCALP.md": "cb8d72afc40689d04a3cf3da7e20b29564eba59b3f24369ffb7000b6d0c44480",
        TRACK_ROOT / "_repair_greenbird/REPLAY_GB-FAIL.json": "feccf13f9d97b1ab5b9f4c61a08e241317bfe94f9e8e3b82b309a15007a89b4b",
        TRACK_ROOT / "_repair_greenbird/REPLAY_GB-VWAP.json": "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570",
        TRACK_ROOT / "_repair_greenbird/REPLAY_GB-SCALP.json": "176723b315af3d1b7ffde99ad4114f7a60ebbb6e33d1f8a0ffaab11b0ad304bf",
        TRACK_ROOT / "_repair_greenbird/REPLAY_LOCATION_MISSES.json": "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570",
        TRACK_ROOT / "_repair_jumbo/PLAUSIBILITY_jumbo.json": "dc36850cd6abbedc3e30dfcdb55e4739f0fd77c7f0a38e5df8b520f0469775fe",
        TRACK_ROOT / "_repair_jumbo/PLAUSIBILITY_jumbo.md": "0c4a2a9f582f88650a67d7025e698e00c581216b652157a0e72ab3fea66b1087",
        TRACK_ROOT / "_repair_jumbo/B0_B01_HASHES.json": "ebbf59a34634ad1b5f0ef8b5ccc4a608c33627e976992923bd70a25472c81102",
        TRACK_ROOT / "_repair_jumbo/REPLAY_jumbo.json": "a56b1bf36bac8c2d365e65190f744e849851760d1bd6c3bcf7f541cc8095535f",
        TRACK_ROOT / "_repair_jumbo/FUNNEL_jumbo.json": "c23d93b515d65dcfd7dbad52bb3e25729e6e13c47e2cbab21b8806eedaf11ae1",
        TRACK_ROOT / "_repair_jumbo/STATISTICS_jumbo.json": "53796782c644b8caa47532bf8e9eef1fc07b3da7adfd6d98c49a68882500354a",
        TRACK_ROOT / "_repair_jumbo/RULES_jumbo.json": "5e45b7d3901690aea9f5af38d473993cd434eb7623376b0e5ba839ee971812d1",
    }
    for path, digest in expected.items():
        assert path.is_file(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == digest, (path.name, actual, digest)


def test_A05_every_after_tape_example_replays_without_building_a_window(monkeypatch):
    """No example outside the frozen session list may reach the derived cache.

    The guard is membership in the frozen classified session list, so this
    covers both an after-tape date (2026-09-08 onward) and any date inside the
    span that is not a session. build_event_window is replaced by a raise, so a
    replay that got as far as building a window fails here instead of leaving an
    empty entry under /workspace/data.
    """
    from trading_research.research.method_pack import event_cache, event_time
    from trading_research.research.rule_discovery.source_adapters.common import is_native_session

    sys.path.insert(0, str(Path("/workspace/implementation/tools")))
    import replay_author_examples as replay_tool

    built = []

    def boom(*args, **kwargs):
        built.append(args)
        raise AssertionError("build_event_window must not run for a date outside the frozen session list")

    monkeypatch.setattr(event_cache, "build_event_window", boom)
    monkeypatch.setattr(event_time, "build_event_window", boom)

    examples = json.loads(
        Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json").read_text()
    )["examples"]
    outside = [
        row
        for row in examples
        if row.get("inside_tape") is False or not is_native_session(str(row.get("date") or "")[:10])
    ]
    assert outside, "the example set must contain at least one date outside the frozen list"
    calendar = set(replay_tool.load_calendar())
    assert "2026-09-03" in calendar and "2026-09-11" not in calendar
    for row in outside:
        result = replay_tool.replay_one(row, calendar)
        assert result.get("detected") is None, (row.get("id"), result.get("detected"))
        assert result.get("reason"), row.get("id")
    assert not built


def _complete_b02_runs() -> list[Path]:
    skip = {"1e13829f2c88f1e1", "4e3ed4d86149bf9c"}
    found = []
    for path in TRACK_ROOT.iterdir():
        if not path.is_dir() or path.name.startswith("_") or path.name in skip:
            continue
        if (path / "RUN_COMPLETE.json").is_file() and (path / "SUMMARY.json").is_file():
            found.append(path)
    return found


def _branch_count(root: Path) -> int:
    try:
        return int(json.loads((root / "RUN_COMPLETE.json").read_text()).get("n_branches") or 0)
    except Exception:
        return 0


def _complete_b02_run() -> Path | None:
    """The main full-history root: the complete run carrying the most branches."""
    found = _complete_b02_runs()
    if not found:
        return None
    return max(found, key=_branch_count)


def _merged_b02_branch_rows() -> tuple[list[dict], list[Path]]:
    """Main-root rows with every supplemental root's rows superseding them by coverage id."""
    found = _complete_b02_runs()
    if not found:
        return [], []
    main = max(found, key=_branch_count)
    supplemental = sorted(
        (path for path in found if path != main),
        key=lambda item: (item / "RUN_COMPLETE.json").stat().st_mtime,
    )
    rows = [dict(row) for row in json.loads((main / "SUMMARY.json").read_text()).get("branches") or []]
    index = {row["coverage_id"]: position for position, row in enumerate(rows)}
    for extra in supplemental:
        for row in json.loads((extra / "SUMMARY.json").read_text()).get("branches") or []:
            row = dict(row)
            row["run_root"] = str(extra)
            if row["coverage_id"] in index:
                rows[index[row["coverage_id"]]] = row
            else:
                index[row["coverage_id"]] = len(rows)
                rows.append(row)
    return rows, supplemental


def test_A05_plausibility_gate_full_history():
    import pytest

    run_root = _complete_b02_run()
    if run_root is None:
        pytest.skip("corrected full-history B0.2 run is not complete")
    rows, _supplemental = _merged_b02_branch_rows()
    summary = {"branches": rows}
    families_root = Path(
        "/workspace/implementation/src/trading_research/research/rule_discovery/families"
    )
    spec_by_family = {
        "JJ-TBR": json.loads((families_root / "jumbo.json").read_text()).get("plausibility") or {},
        "GB-FAIL": json.loads((families_root / "green_failure.json").read_text()).get("plausibility") or {},
        "GB-VWAP": (json.loads((families_root / "green_vwap_scalp.json").read_text()).get("plausibility") or {}).get("GB-VWAP") or {},
        "GB-SCALP": (json.loads((families_root / "green_vwap_scalp.json").read_text()).get("plausibility") or {}).get("GB-SCALP") or {},
        "SIRES": json.loads((families_root / "sires.json").read_text()).get("plausibility") or {},
        "REFILL-STUDY": json.loads((families_root / "processes.json").read_text()).get("plausibility") or {},
        "SAINT-AMT": json.loads((families_root / "saint.json").read_text()).get("plausibility") or {},
        "MEMBER-TWO-REASONS": json.loads((families_root / "member.json").read_text()).get("plausibility") or {},
        "KEANI-OPEN-ABOVE-VALUE": json.loads((families_root / "keani.json").read_text()).get("plausibility") or {},
    }
    errors = []
    for row in summary.get("branches") or []:
        family = row.get("family")
        branch = row.get("branch")
        episodes = int(row.get("episodes") or 0)
        n_pass = int(row.get("pass") or 0)
        funnel = row.get("funnel") or {}
        for name, stage in funnel.items():
            entering = int(stage.get("entering") or 0)
            counted = int(stage.get("pass") or 0) + int(stage.get("fail") or 0) + int(stage.get("unknown") or 0)
            if entering != counted:
                errors.append(f"{family}:{branch}:{name} entering {entering} != pass+fail+unknown {counted}")
            if entering > episodes:
                errors.append(f"{family}:{branch}:{name} entering {entering} > episodes {episodes}")
        if episodes > 0 and n_pass == 0:
            killing = [
                name
                for name, stage in funnel.items()
                if int(stage.get("fail") or 0) > 0 or int(stage.get("unknown") or 0) > 0
            ]
            if not killing:
                errors.append(f"{family}:{branch} zero-pass with no named killing stage")
        bound = (spec_by_family.get(family) or {}).get(branch) or {}
        rate = (n_pass / episodes) if episodes else 0.0
        eps = (episodes / int(row.get("dates_run") or 0)) if row.get("dates_run") else 0.0
        out = False
        if bound:
            ep_bound = bound.get("episodes_per_session")
            pr_bound = bound.get("pass_rate")
            if not (isinstance(ep_bound, (list, tuple)) and len(ep_bound) >= 2 and ep_bound[0] is not None and ep_bound[1] is not None):
                out = True
            elif not (ep_bound[0] <= eps <= ep_bound[1]):
                out = True
            if isinstance(pr_bound, (list, tuple)) and len(pr_bound) >= 2 and pr_bound[0] is not None and pr_bound[1] is not None:
                if not (pr_bound[0] <= rate <= pr_bound[1]):
                    out = True
            if out:
                just = bound.get("observed_rate_justification")
                diagnosis = bound.get("source_claim")
                if not just and not diagnosis:
                    errors.append(f"{family}:{branch} out of bound without diagnosis")
        if family == "SIRES" and branch in {"ofm_aggressive", "balance_failure_fade"}:
            if not out:
                errors.append(f"{family}:{branch} must be out of bound; source gives no contact density")
            just = bound.get("observed_rate_justification") or {}
            page = str(just.get("page") or bound.get("page") or "")
            if branch == "ofm_aggressive" and "OFM p.4" not in page:
                errors.append(f"{family}:{branch} diagnosis must cite OFM p.4")
            if branch == "balance_failure_fade" and "BIG p.14" not in page:
                errors.append(f"{family}:{branch} diagnosis must cite BIG p.14")
    covered = {(row.get("family"), row.get("branch")) for row in summary["branches"]}
    if ("GB-FAIL", "prior_week_level") not in covered:
        errors.append("GB-FAIL:prior_week_level is not in the merged full-history rows")
    if ("GB-FAIL", "prior_month_level") in covered:
        errors.append("prior_month_level must stay out of B0.2")
    assert not errors, errors


def test_A05_supplemental_run_covers_the_added_branch_and_changed_scans():
    """The supplemental root is a complete 1742-date run and no main job file changed."""
    import pytest

    rows, supplemental = _merged_b02_branch_rows()
    if not rows:
        pytest.skip("corrected full-history B0.2 run is not complete")
    if not supplemental:
        pytest.skip("supplemental B0.2 run is not complete")
    main = _complete_b02_run()
    main_complete = json.loads((main / "RUN_COMPLETE.json").read_text())
    covered = set()
    for extra in supplemental:
        complete = json.loads((extra / "RUN_COMPLETE.json").read_text())
        assert complete.get("n_dates") == 1742, (extra.name, complete.get("n_dates"))
        assert not complete.get("failed_dates"), (extra.name, complete.get("failed_dates"))
        manifest = json.loads((extra / "MANIFEST.json").read_text())
        assert manifest["baseline"] == "B0.2"
        assert len(manifest["dates"]) == 1742
        covered |= set(manifest["branches"])
        assert complete["job_count"] == len(manifest["branches"]) * 1742
        assert complete["run_id"] != main_complete["run_id"]
    assert "GB-FAIL:branch:prior_week_level" in covered
    assert {"GB-FAIL:branch:asia_box", "GB-FAIL:branch:prior_day_level"} <= covered
    # internal_rotation's location stage read the old range guard, so its job
    # files had to be re-scanned under the shared frozen-list guard.
    assert "JJ-TBR:branch:internal_rotation" in covered
    by_cid = {row["coverage_id"]: row for row in rows}
    for cid in covered:
        assert by_cid[cid].get("run_root") in {str(item) for item in supplemental}, cid
    for row in rows:
        if row["coverage_id"] not in covered:
            assert row.get("run_root") is None, row["coverage_id"]


def test_A05_tdo_retest_mode_counts_are_reported():
    """The registered confirmation variant is recorded, and it can fail with a named reason."""
    import gzip

    import pytest

    _rows, supplemental = _merged_b02_branch_rows()
    if not supplemental:
        pytest.skip("supplemental B0.2 run is not complete")
    modes: dict[str, int] = {}
    reasons: dict[str, int] = {}
    wanted = {"GB-FAIL--branch--asia_box.json.gz", "GB-FAIL--branch--prior_day_level.json.gz"}
    for extra in supplemental:
        for path in sorted((extra / "jobs").rglob("*.json.gz")):
            if path.name not in wanted:
                continue
            document = json.loads(gzip.decompress(path.read_bytes()).decode())
            for episode in document.get("episodes") or []:
                values = episode.get("values") or {}
                if values.get("confirmation_mode"):
                    modes[values["confirmation_mode"]] = modes.get(values["confirmation_mode"], 0) + 1
                if values.get("tdo_retest_reason"):
                    reasons[values["tdo_retest_reason"]] = reasons.get(values["tdo_retest_reason"], 0) + 1
    assert modes.get("five_minute_close"), modes
    assert modes.get("tdo_retest"), modes
    assert reasons, "the variant must be able to fail with a named reason"
    assert set(reasons) <= {"no_retest_in_window", "retest_broke_through", "retest_close_unknown", "tdo_unavailable"}, reasons


def test_S03_false_plan_identity_is_rejected(tmp_path):
    from trading_research.research.contracts.identity import ASSURANCE_VERSION
    from trading_research.research.contracts.receipts import FailureCode
    from tests.rule_discovery.test_p15_01 import (
        failure_codes,
        foundation_tasks,
        invoke,
        write_bound_task,
        write_graph,
    )

    graph = write_graph(
        tmp_path / "graph.json",
        foundation_tasks(),
        required_task_artifacts=[
            "DRAFT_MANIFEST.json",
            "PLAN_SNAPSHOT.json",
            "CODE_SNAPSHOT.json",
            "EVIDENCE_MATRIX.json",
            "WORK_LOG.md",
            "DECISIONS.tsv",
            "REPORT.md",
        ],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    good = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert good.returncode == 0, good.stdout
    document = json.loads(receipt.read_text())
    document["plan_sha256"] = "0" * 64
    receipt.write_text(json.dumps(document, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.IDENTITY in failure_codes(proc)


def test_rule_discovery_tests_do_not_write_track_dirs():
    root = Path("/workspace/implementation/tests/rule_discovery")
    banned = []
    for path in sorted(root.glob("test_*.py")):
        for index, line in enumerate(path.read_text().splitlines(), 1):
            if "_track_" not in line:
                continue
            if any(token in line for token in ("write_text", "write_bytes", "mkdir", "unlink", "replace(", "open(")):
                banned.append(f"{path.name}:{index}:{line.strip()}")
    assert banned == []
