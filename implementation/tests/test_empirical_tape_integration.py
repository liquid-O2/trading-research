"""Registry-level integration controls for the empirical tape/bar bridges."""
from __future__ import annotations

from copy import deepcopy
import csv
from datetime import date, timedelta
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import sys

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.empirical_bar_engine import run_bar_rule
from trading_research.research.method_pack.empirical_market import BarMarket, clock
from trading_research.research.method_pack.empirical_protocol import population_summary
from trading_research.research.method_pack.empirical_registry import (
    build_registry, canonical_hash, validated_registry_batch,
)
from trading_research.research.method_pack.empirical_selectors import MINUTE
from trading_research.research.method_pack.empirical_tape import (
    load_tape_session, m09_research_comparison, stream_native_trades,
)
from trading_research.research.method_pack.empirical_tape_binding import assemble_m09
from trading_research.research.method_pack.native_resolution import NativeEvidenceError


DAY = date(2026, 1, 15)
PRIOR = DAY - timedelta(days=1)
INSTRUMENT = 42
DATASET = "quantpad/cme__nq-continuous-futures__ohlcv-1m"
TRADES = "quantpad/cme__nq-continuous-futures__trades"


def _archived_tape_module():
    """Load the immutable run-v1 implementation under its package namespace."""
    name = "trading_research.research.method_pack._empirical_tape_run_v1"
    if name in sys.modules:
        return sys.modules[name]
    path = (Path(__file__).resolve().parents[1] / "reports/phase1-live/empirical"
            / "revisions/run-v1/source/empirical_tape.py")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load preserved run-v1 empirical tape source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def registry():
    document = build_registry()
    document["freeze_status"] = "frozen"
    document["registry_sha256"] = canonical_hash(document)
    return document


def _rule(registry, method, branch):
    return next(row for row in registry["rules"]
                if row["method_id"] == method and row["branch"] == branch)


def _make_market(root, *, overrides=None, omitted=()):
    overrides = overrides or {}
    omitted = set(omitted)
    rows = []
    for day in (PRIOR, DAY):
        for at in range(clock(day, "09:30"), clock(day, "16:00"), MINUTE):
            if at in omitted:
                continue
            if day == PRIOR:
                values = {"o": 95, "h": 100, "l": 90, "c": 95, "v": 10}
            else:
                values = {"o": 99, "h": 99.5, "l": 98.5, "c": 99, "v": 10}
            values.update(overrides.get(at, {}))
            rows.append({"t": at // 1_000_000, "instrument_id": INSTRUMENT,
                         **values})
    path = root / DATASET / "native.parquet"
    path.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=120)
    manifest = root / "manifests/files.csv"
    manifest.parent.mkdir()
    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["dataset_id", "archive_path"])
        writer.writeheader()
        writer.writerow({"dataset_id": DATASET,
                         "archive_path": path.relative_to(root).as_posix()})
    definition = root / "derived/continuous-futures__instrument-and-roll-maps/nq-instruments.json"
    definition.parent.mkdir(parents=True)
    definition.write_text(json.dumps([{
        "instrument_id": INSTRUMENT, "root": "NQ", "raw_symbol": "NQH6",
        "min_price_increment": ".25",
        "first_definition_ns": clock(PRIOR, "09:30") - 1,
    }]))
    return BarMarket({"partition_id": "fixture-native-partition",
                      "instrument_id": INSTRUMENT,
                      "session_date": DAY.isoformat()}, root)


def _tape(*, action_delta=Decimal(1), retest_delta=Decimal(-1),
          missing=(), delayed=()):
    missing, delayed = set(missing), set(delayed)
    minutes, reconciliation = [], []
    for at in range(clock(DAY, "09:30"), clock(DAY, "09:45"), MINUTE):
        if at in missing:
            continue
        if at < clock(DAY, "09:35"):
            delta = action_delta
        elif at >= clock(DAY, "09:40"):
            delta = retest_delta
        else:
            delta = Decimal(0)
        minutes.append({"minute_start": at, "minute_end": at + MINUTE,
                        "known_at": at + (2 * MINUTE if at in delayed else MINUTE),
                        "instrument_id": INSTRUMENT, "delta": delta})
        reconciliation.append({"minute_start": at, "matched": True})
    return {"minutes": minutes, "coverage": {"coverage_ok": True,
                                               "reconciliation": reconciliation}}


def _prior_profile(*, instrument=INSTRUMENT, known_at=None,
                   algorithm="contiguous_larger_adjacent_volume_tie_both",
                   fraction=Decimal("0.70"), poc_tie="lowest"):
    return {"profile": {
        "profile_id": "prior-rth-profile", "snapshot_id": "prior-rth-snapshot",
        "instrument_id": instrument,
        "kind": "prior_rth", "session_date": PRIOR.isoformat(),
        "formation_start": clock(PRIOR, "09:30"),
        "formation_end": clock(PRIOR, "16:00"),
        "as_of": clock(PRIOR, "16:00"),
        "known_at": clock(PRIOR, "16:00") if known_at is None else known_at,
        "poc": Decimal(95), "poc_tie_policy": poc_tie,
        "val": Decimal(93), "vah": Decimal(97),
        "value_area_fraction": fraction,
        "value_area_algorithm": algorithm,
        "value_area_tie_policy": "both" if algorithm.endswith("tie_both") else "lower",
        "coverage": {"state": "complete", "ok": True, "holes": []},
    }}


def _trap_market(root):
    overrides = {}
    # First five-minute bar trades above prior high and closes back below.
    overrides[clock(DAY, "09:30")] = {"h": 101, "l": 98, "c": 99}
    # The first later bar does not touch 100; the second retests and closes below.
    for at in range(clock(DAY, "09:35"), clock(DAY, "09:40"), MINUTE):
        overrides[at] = {"h": 99.75, "l": 98.5, "c": 99}
    overrides[clock(DAY, "09:40")] = {"h": 100, "l": 98.5, "c": 99}
    return _make_market(root, overrides=overrides)


def test_tape_membership_cache_matches_preserved_run_v1_output(tmp_path):
    root = tmp_path / "tape-cache-equivalence"
    start = clock(DAY, "09:30")
    paths = [root / TRADES / "part-a.parquet",
             root / TRADES / "part-b.parquet"]
    paths[0].parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([
        {"t": start + 1_000_000_000, "price": "100.00", "size": 2,
         "side": "B", "instrument_id": INSTRUMENT},
        {"t": start + 2_000_000_000, "price": "100.25", "size": 1,
         "side": "A", "instrument_id": INSTRUMENT},
    ]), paths[0])
    pq.write_table(pa.Table.from_pylist([
        {"t": start + MINUTE + 1_000_000_000, "price": "100.50", "size": 2,
         "side": "B", "instrument_id": INSTRUMENT},
        {"t": start + MINUTE + 2_000_000_000, "price": "100.25", "size": 1,
         "side": "A", "instrument_id": INSTRUMENT},
    ]), paths[1])
    bar_path = root / DATASET / "native.parquet"
    bar_path.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([
        {"t": start // 1_000_000, "o": "100.00", "h": "100.25",
         "l": "100.00", "c": "100.25", "v": 3,
         "instrument_id": INSTRUMENT},
        {"t": (start + MINUTE) // 1_000_000, "o": "100.50", "h": "100.50",
         "l": "100.25", "c": "100.25", "v": 3,
         "instrument_id": INSTRUMENT},
    ]), bar_path)
    entries = [(path, TRADES) for path in paths] + [(bar_path, DATASET)]
    manifest = root / "manifests/files.csv"
    manifest.parent.mkdir()
    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle,
                                fieldnames=["dataset_id", "archive_path", "bytes"])
        writer.writeheader()
        for path, dataset in entries:
            writer.writerow({"dataset_id": dataset,
                             "archive_path": path.relative_to(root).as_posix(),
                             "bytes": path.stat().st_size})
    frozen = [{"path": path.relative_to(root).as_posix(),
               "dataset_id": dataset, "bytes": path.stat().st_size,
               "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
               "hash_basis": "full_file_sha256"}
              for path, dataset in entries]
    kwargs = {
        "frozen_inputs": frozen, "ohlcv_dataset": DATASET, "tick_size": ".25",
        "profile_kind": "prior_rth", "session_date": DAY.isoformat(),
        "value_area_fraction": ".70", "value_area_tie_policy": "both",
        "poc_tie_policy": "lowest",
    }
    archived = _archived_tape_module().load_tape_session(
        root, TRADES, start, start + 2 * MINUTE, INSTRUMENT, **kwargs)
    current = load_tape_session(
        root, TRADES, start, start + 2 * MINUTE, INSTRUMENT, **kwargs)
    assert current["profile"] == archived["profile"]
    assert current["minutes"] == archived["minutes"]
    assert current["membership_sha256"] == archived["membership_sha256"]


def test_saint_trap_uses_exact_five_minute_delta_and_source_assembly(tmp_path, registry):
    market = _trap_market(tmp_path / "saint-pass")
    rule = _rule(registry, "SAINT-AMT", "trapped_buyers_retest")
    found = run_bar_rule(rule, market, registry, tape=_tape())
    assert found["population_holes"] == []
    assert len(found["records"]) == 1
    opportunity, replay = found["records"][0]
    assert opportunity.side == "short"
    assert (opportunity.occurrence_start, opportunity.available_at) == (
        clock(DAY, "09:30"), clock(DAY, "09:35"))
    assert replay.verdict == "pass"
    assert replay.reason == "first_high_retest_close_and_delta"
    assert replay.completed_at == clock(DAY, "09:45")
    with validated_registry_batch(registry):
        assembled = market.source_assembly(rule, opportunity, registry)
    assert assembled.result["faithful_eligible"] is False
    assert assembled.result["historical_comparison_eligible"] is True
    assert assembled.result["verdict"] == "unknown"
    objects = assembled.manifest["objects"]
    assert any(row["recipe_id"] == "O004"
               and row["formation_end"] == opportunity.available_at for row in objects)


def test_saint_delta_missing_unknown_and_late_clocks_are_not_admitted(tmp_path, registry):
    rule = _rule(registry, "SAINT-AMT", "trapped_buyers_retest")
    market = _trap_market(tmp_path / "saint-controls")
    missing_at = clock(DAY, "09:32")
    missing = run_bar_rule(rule, market, registry,
                           tape=_tape(missing=[missing_at]))
    assert missing["records"] == []
    assert missing["population_holes"] == ["initial_delta_coverage_unknown"]
    unknown = run_bar_rule(rule, market, registry,
                           tape=_tape(action_delta=None))
    assert unknown["records"] == []
    assert unknown["population_holes"] == ["initial_delta_coverage_unknown"]
    with pytest.raises(ValueError, match="delta unavailable at bar close"):
        run_bar_rule(rule, market, registry,
                     tape=_tape(delayed=[clock(DAY, "09:34")]))


def test_saint_initial_opportunity_is_invariant_to_later_tape(tmp_path, registry):
    rule = _rule(registry, "SAINT-AMT", "trapped_buyers_retest")
    market = _trap_market(tmp_path / "saint-prefix")
    original = run_bar_rule(rule, market, registry, tape=_tape())
    changed_tape = _tape()
    changed_tape["minutes"].append({
        "minute_start": clock(DAY, "15:59"), "minute_end": clock(DAY, "16:00"),
        "known_at": clock(DAY, "16:00"), "instrument_id": INSTRUMENT,
        "delta": Decimal(999999),
    })
    changed_tape["coverage"]["reconciliation"].append({
        "minute_start": clock(DAY, "15:59"), "matched": True})
    changed = run_bar_rule(rule, market, registry, tape=changed_tape)
    assert original["records"][0][0].to_dict() == changed["records"][0][0].to_dict()
    assert original["records"][0][1] == changed["records"][0][1]


def test_opening_population_precedes_profile_endpoint_and_assembles_native_prefix(tmp_path, registry):
    market = _make_market(tmp_path / "opening-pass")
    rule = _rule(registry, "KEANI-OPEN-ABOVE-VALUE", "source_long")
    complete = run_bar_rule(rule, market, registry,
                            prior_profile=_prior_profile())
    absent = run_bar_rule(rule, market, registry, prior_profile=None)
    complete_opportunity, complete_replay = complete["records"][0]
    absent_opportunity, absent_replay = absent["records"][0]
    assert complete_opportunity.opportunity_id == absent_opportunity.opportunity_id
    assert complete_opportunity.observation_unit == "opening_period_state"
    assert complete_opportunity.available_at == clock(DAY, "09:31")
    assert complete_replay.verdict == "pass"
    assert complete_replay.completed_at == clock(DAY, "10:00")
    assert absent_replay.verdict == "unknown" and absent_replay.censored
    assert absent_replay.reason == "prior_value_profile_unverified"
    summary = population_summary([{
        "opportunity": complete_opportunity.to_dict(),
        "replay": complete_replay.to_dict(complete_opportunity),
    }])
    assert summary["N"] == summary["p"] == 1
    assert summary["actual_selections"] is summary["actual_fills"] is None
    with validated_registry_batch(registry):
        assembled = market.source_assembly(rule, complete_opportunity, registry)
    assert assembled.result["verdict"] == "unknown"
    assert assembled.result["faithful_eligible"] is False
    assert any(row["recipe_id"] == "O004" for row in assembled.manifest["objects"])


def test_opening_missing_membership_and_profile_identity_controls(tmp_path, registry):
    rule = _rule(registry, "KEANI-OPEN-ABOVE-VALUE", "source_long")
    missing_later = _make_market(
        tmp_path / "opening-missing-later", omitted=[clock(DAY, "09:47")])
    found = run_bar_rule(rule, missing_later, registry,
                         prior_profile=_prior_profile())
    opportunity, replay = found["records"][0]
    assert replay.verdict == "unknown" and replay.censored
    assert replay.reason == "opening_A_membership_incomplete"
    missing_first = _make_market(
        tmp_path / "opening-missing-first", omitted=[clock(DAY, "09:30")])
    first = run_bar_rule(rule, missing_first, registry,
                         prior_profile=_prior_profile())
    assert first["records"] == []
    assert first["population_holes"] == ["session_opening_minute_unavailable"]
    market = _make_market(tmp_path / "opening-identity")
    with pytest.raises(ValueError, match="foreign"):
        run_bar_rule(rule, market, registry,
                     prior_profile=_prior_profile(instrument=99))
    with pytest.raises(ValueError, match="late"):
        run_bar_rule(rule, market, registry,
                     prior_profile=_prior_profile(known_at=clock(DAY, "09:31")))


def test_opening_rejects_profile_that_does_not_match_frozen_va70_rule(tmp_path, registry):
    market = _make_market(tmp_path / "opening-wrong-profile")
    rule = _rule(registry, "KEANI-OPEN-ABOVE-VALUE", "source_long")
    wrong = _prior_profile(algorithm="adjacent_single", poc_tie="highest")
    with pytest.raises(ValueError, match="profile.*configuration|value.area|VA70"):
        run_bar_rule(rule, market, registry, prior_profile=wrong)


def test_saint_rejects_covered_poc_from_wrong_formation_window(tmp_path, registry):
    market = _make_market(tmp_path / "saint-wrong-profile", overrides={
        clock(DAY, "09:34"): {"c": 101, "h": 101},
        clock(DAY, "09:39"): {"c": 101, "h": 101},
        clock(DAY, "09:44"): {"c": 95, "h": 99, "l": 94},
        clock(DAY, "09:49"): {"h": 95, "l": 94, "c": 95},
    })
    rule = _rule(registry, "SAINT-AMT", "failed_auction_return")
    wrong = _prior_profile()
    wrong["profile"]["formation_start"] = clock(PRIOR, "10:00")
    with pytest.raises(ValueError, match="prior.*profile|formation"):
        run_bar_rule(rule, market, registry, prior_profile=wrong)


def test_m09_exact_pair_and_touch_members_assemble_as_native_o098(tmp_path, registry):
    root = tmp_path / "m09-binding"
    market = _make_market(root)
    trade_dataset = "quantpad/cme__nq-continuous-futures__trades"
    start = clock(DAY, "09:30")
    trade_path = root / trade_dataset / "native.parquet"
    trade_path.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([
        {"t": start + 1_000_000_000, "price": "100.00", "size": 100,
         "side": "B", "instrument_id": INSTRUMENT},
        {"t": start + 2_000_000_000, "price": "100.50", "size": 100,
         "side": "B", "instrument_id": INSTRUMENT},
        {"t": start + 3_000_000_000, "price": "101.50", "size": 1,
         "side": "B", "instrument_id": INSTRUMENT},
        {"t": start + 4_000_000_000, "price": "100.25", "size": 1,
         "side": "A", "instrument_id": INSTRUMENT},
    ]), trade_path)
    with (root / "manifests/files.csv").open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["dataset_id", "archive_path"])
        writer.writerow({"dataset_id": trade_dataset,
                         "archive_path": trade_path.relative_to(root).as_posix()})
    # The application opens its resolver against the completed immutable file
    # inventory. Recreate this fixture market after extending that inventory so
    # resolver reuse exercises the same ownership lifecycle.
    market = BarMarket(market.partition, root)
    digest = __import__("hashlib").sha256(trade_path.read_bytes()).hexdigest()
    frozen = [{"path": trade_path.relative_to(root).as_posix(),
               "dataset_id": trade_dataset, "bytes": trade_path.stat().st_size,
               "sha256": digest, "hash_basis": "full_file_sha256"}]
    stream = stream_native_trades(root, trade_dataset, start, clock(DAY, "16:00"),
                                  INSTRUMENT, frozen_inputs=frozen)
    rule = _rule(registry, "REFILL-STUDY", "touch_record")
    comparison = m09_research_comparison(
        stream, rule=rule, partition=market.partition,
        registry_sha256=registry["registry_sha256"], tick_size=".25",
        coverage_ok=True, session_end=clock(DAY, "16:00"))
    assert len(comparison["records"]) == 1
    tape = {"schema": "phase1-empirical-tape-session-v1",
            "dataset_id": trade_dataset,
            "instrument_id": INSTRUMENT,
            "source_files": [identity.__dict__ for identity in stream.file_identities],
            "evidence_sha256": "d" * 64}
    with validated_registry_batch(registry):
        assembled = assemble_m09(rule, comparison["records"][0]["opportunity"],
                                 registry, market, tape)
    assert assembled.result["faithful_eligible"] is False
    assert assembled.result["verdict"] == "unknown"
    assert len(assembled.manifest["objects"]) == 1
    obj = assembled.manifest["objects"][0]
    assert obj["recipe_id"] == "O098"
    assert [(row["row_start"], row["row_end"])
            for row in obj["raw_member_locators"]] == [(0, 2), (3, 4)]
    assert obj["formation_end"] == start + 4_000_000_001
    tampered = deepcopy(tape)
    tampered["source_files"][0]["sha256"] = "0" * 64
    with pytest.raises(NativeEvidenceError, match="digest mismatch|source digest"):
        assemble_m09(rule, comparison["records"][0]["opportunity"],
                     registry, market, tampered)
