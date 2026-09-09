"""Independent timing-statistics helpers. No family re-run and no market claim."""
from datetime import date
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import ArtifactStore
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.jumbo_clock_comparison import COMMON_TARGETS, HORIZON, VERSION as COMMON_ADAPTER_VERSION
from trading_research.research.jumbo_matrix import PreparedPaths
from trading_research.research.jumbo_timing_statistics import (
    ORIGINAL_NQ2024_VARIANT, PRIMARY_VARIANT, classify_level_observation,
    classify_move_relationship, common_target_clock_spread, declared_clock_pairs,
    doubled_equilibrium, doubled_lower_half_extension, doubled_upper_half_extension,
    fit_root_prior_vol_tertiles, assign_prior_vol_bin, intended_root_dates,
    jtr_doubled_levels, jtr_known_before_turn, overlap_bin, position_bin,
    raw_contract_match, run_timing_statistics, signed_close_open, split_source_variants,
    width_ratio_bin,
)

STATISTICS = {
    "block_length": 5, "bootstrap_seed": 20260907, "confidence": 0.95,
    "minimum_dates": 100, "minimum_events": 20, "replicates": 1000,
    "descriptive_quantiles": [0.05, 0.25, 0.5, 0.75, 0.95],
}
CLOCKS = ("JTR_fixed_04", "JTR_fixed_04__shift_-10m", "OR_activity_1_1")
FEATURES = (
    "width_ticks", "open_position", "last_close_position", "last_close_age_minutes",
    "width_prior_actual_RTH_ratio", "prior_actual_RTH_20_mean_width_ticks",
    "anchor_JTR_fixed_04_price_overlap_fraction",
)
FI = {name: index for index, name in enumerate(FEATURES)}
DATES = (
    date(2021, 1, 4), date(2021, 1, 5), date(2021, 1, 6),
    date(2024, 6, 3), date(2025, 1, 2),
)
ORDINALS = tuple(day.toordinal() for day in DATES)


def _ref(kind="literal"):
    return {"kind": kind, "sha256": "a" * 64, "size_bytes": 1, "rows": 1, "schema_sha256": "b" * 64}


def _shard(root, year, *, corrected=False):
    record = {
        "root": root, "year": year, "intended_cash_dates": 1,
        "tables": {"paths": _ref("paths"), "formations": _ref("formations")},
        "anchor_supplement": {"manifest": {"id": "m"}, "table_ref": _ref("anchors")},
        "statistics": {"kind": "jumbo_actual_year_statistics_gzip_v2", "sha256": "c" * 64, "size_bytes": 1},
    }
    if corrected:
        record["source_supersession"] = {
            "kind": "jumbo_actual_definition_supersession_report_v1",
            "sha256": "d" * 64, "size_bytes": 1,
        }
        record["population_role"] = (
            "Source-corrected NQ2024; primary Context cohort after verified resolution; original shard retained"
        )
    return record


def _workers():
    original = _shard("NQ", 2024)
    corrected = _shard("NQ", 2024, corrected=True)
    development = {
        "success": True, "mode": "develop", "phase": "extract",
        "shards": [_shard("NQ", 2021), original],
        "source_sensitivity_shards": [corrected],
        "model_shards": [_shard("NQ", 2021), corrected],
        "narrative": {"kind": "jumbo_development_report_markdown_v1", "sha256": "e" * 64, "size_bytes": 1},
    }
    confirmation = {
        "success": True, "mode": "confirm", "phase": "confirmation",
        "shards": [_shard("NQ", 2025)],
        "source_sensitivity_shards": [],
        "narrative": {"kind": "jumbo_development_report_markdown_v1", "sha256": "f" * 64, "size_bytes": 1},
    }
    return development, confirmation


def _plan():
    return {
        "matched_clock_comparison": {"clocks": list(CLOCKS), "origin_local": "10:01"},
        "neighbor_clocks": ["JTR_fixed_04"],
        "neighbor_shifts_minutes": [-10, 10],
        "statistics": dict(STATISTICS),
    }


def _common_matrix(days=DATES, *, confirm_prior=10000.0, missing_neighbor=True):
    n_dates, n_clocks = len(days), len(CLOCKS)
    n = n_dates * n_clocks
    features = np.full((n, len(FEATURES)), np.nan, dtype=np.float32)
    ordinals = np.array([day.toordinal() for day in days], dtype=np.int64)
    fields = {
        "root": np.zeros(n, dtype=np.int16),
        "date": np.repeat(ordinals, n_clocks),
        "clock": np.tile(np.arange(n_clocks, dtype=np.int16), n_dates),
        "common_own_features_available": np.ones(n, dtype=np.bool_),
        "common_target_eligible": np.ones(n, dtype=np.bool_),
        "common_known_dependency_available": np.ones(n, dtype=np.bool_),
        "origin_ns": np.full(n, 1001, dtype=np.int64),
        "common_maturity_at_ns": np.full(n, 1601, dtype=np.int64),
        "common_high_priorW": np.full(n, 0.20),
        "common_low_priorW": np.full(n, 0.15),
        "common_terminal_priorW": np.full(n, 0.10),
    }
    prior = {2021: (10.0, 20.0, 30.0), 2024: (40.0,), 2025: (confirm_prior,)}
    train_values = []
    for day in days:
        if day.year == 2021:
            train_values.append(prior[2021][len(train_values)])
    prior_by_year = {2021: [10.0, 20.0, 30.0][: sum(day.year == 2021 for day in days)],
                     2024: [40.0], 2025: [confirm_prior]}
    used = {2021: 0, 2024: 0, 2025: 0}
    for index in range(n):
        day = date.fromordinal(int(fields["date"][index]))
        slot = used[day.year]
        if fields["clock"][index] == 0:
            used[day.year] = slot + 1
        features[index, FI["prior_actual_RTH_20_mean_width_ticks"]] = prior_by_year[day.year][min(slot, len(prior_by_year[day.year]) - 1)]
        features[index, FI["last_close_age_minutes"]] = 1.0
        features[index, FI["width_ticks"]] = 80 + 10 * int(fields["clock"][index])
        features[index, FI["width_prior_actual_RTH_ratio"]] = (0.4, 1.5, 0.1)[int(fields["clock"][index])]
        features[index, FI["open_position"]] = 0.25 + 0.1 * int(fields["clock"][index])
        features[index, FI["last_close_position"]] = 0.4
        features[index, FI["anchor_JTR_fixed_04_price_overlap_fraction"]] = 0.25 if fields["clock"][index] else 1.0
        if missing_neighbor and day == date(2021, 1, 6) and fields["clock"][index] == 1:
            fields["common_own_features_available"][index] = False
            features[index, FI["width_ticks"]] = np.nan
            features[index, FI["width_prior_actual_RTH_ratio"]] = np.nan
            features[index, FI["open_position"]] = np.nan
            features[index, FI["last_close_position"]] = np.nan
    manifest = {
        "id": "fixture-common", "version": COMMON_ADAPTER_VERSION, "horizon": HORIZON,
        "clock_ids": list(CLOCKS), "target_names": list(COMMON_TARGETS),
        "feature_columns": ["x_" + name for name in FEATURES],
        "target_rule": "same common receiver exact H/L/C relative to known published anchor",
    }
    return PreparedPaths(manifest, features, fields,
                         {"root": ("NQ",), "clock": CLOCKS, "horizon": (HORIZON,)}, ())


def _formation(clock, day, *, contract="NQZ1", available=901, start=600,
               open_=100, high=200, low=100, close=150, width=None):
    return {
        "date": day, "clock": clock, "contract_key": contract, "status": "complete",
        "exclusion_reasons": "", "formation_id": clock + ":" + day, "root": "NQ",
        "year": int(day[:4]), "source_version": "fixture", "definition": clock,
        "source_ids": "JTR-08", "variant_role": "source", "window_version": "v1",
        "formation_start_ns": start, "formation_end_ns": start + 10, "origin_ns": start + 11,
        "available_at_ns": available, "calendar_known_at_ns": available,
        "open_ticks": open_, "high_ticks": high, "low_ticks": low, "close_ticks": close,
        "width_ticks": high - low if width is None else width, "zero_width": False,
    }


def _formations(days=DATES):
    records = {}
    for day in days:
        iso = day.isoformat()
        jtr_available, turn_start = (940, 930) if day.year == 2025 else (901, 930)
        contract_turn = "OTHER" if day.year == 2024 else "NQZ1"
        records[("NQ", iso, "JTR_fixed_04")] = _formation(
            "JTR_fixed_04", iso, contract="NQZ1", available=jtr_available, start=600,
            open_=120, high=200, low=100, close=160)
        if day == date(2021, 1, 5):
            records[("NQ", iso, "turn_source")] = _formation(
                "turn_source", iso, contract="NQZ1", available=951, start=940,
                open_=10, high=20, low=8, close=12)
        elif day == date(2021, 1, 4):
            records[("NQ", iso, "turn_earlier")] = _formation(
                "turn_earlier", iso, contract="NQZ1", available=941, start=930,
                open_=100, high=150, low=90, close=120)
            records[("NQ", iso, "turn_source")] = _formation(
                "turn_source", iso, contract="NQZ1", available=951, start=940,
                open_=120, high=200, low=80, close=100)
            records[("NQ", iso, "turn_later")] = _formation(
                "turn_later", iso, contract="NQZ1", available=1001, start=950,
                open_=100, high=110, low=90, close=100)
        else:
            records[("NQ", iso, "turn_earlier")] = _formation(
                "turn_earlier", iso, contract=contract_turn, available=941, start=turn_start,
                open_=100, high=130, low=90, close=120)
            records[("NQ", iso, "turn_source")] = _formation(
                "turn_source", iso, contract=contract_turn, available=951, start=940,
                open_=120, high=200, low=80, close=100)
            records[("NQ", iso, "turn_later")] = _formation(
                "turn_later", iso, contract=contract_turn, available=1001, start=950,
                open_=150, high=160, low=140, close=150)
    return records


class GeometryAndObservationTests(unittest.TestCase):
    def test_width_100_equilibrium_and_half_extensions(self):
        levels = jtr_doubled_levels(200, 100)
        self.assertEqual(levels["width_ticks"], 100)
        self.assertEqual(levels["equilibrium"] / 2, 150)
        self.assertEqual(levels["lower_half_extension"] / 2, 50)
        self.assertEqual(levels["upper_half_extension"] / 2, 250)
        self.assertEqual(doubled_equilibrium(200, 100), 300)
        self.assertEqual(doubled_lower_half_extension(200, 100), 100)
        self.assertEqual(doubled_upper_half_extension(200, 100), 500)

    def test_boundary_touch_and_exact_print_are_separate_fields(self):
        observed = classify_level_observation(100, 150, 50, 120, doubled_equilibrium(200, 100))
        self.assertTrue(observed["compatible_intersection"])
        self.assertTrue(observed["boundary_touch"])
        self.assertTrue(observed["definite_print"])
        self.assertEqual(observed["print_members"], ("H",))
        self.assertEqual(observed["observation_class"], "definite_print")

    def test_crossing_without_ohlc_print_is_ambiguous(self):
        observed = classify_level_observation(100, 200, 50, 180, doubled_equilibrium(200, 100))
        self.assertTrue(observed["compatible_intersection"])
        self.assertFalse(observed["definite_print"])
        self.assertFalse(observed["boundary_touch"])
        self.assertEqual(observed["observation_class"], "ambiguous")
        self.assertEqual(observed["print_members"], ())

    def test_no_intersection_is_no_event(self):
        observed = classify_level_observation(10, 20, 8, 12, doubled_equilibrium(200, 100))
        self.assertFalse(observed["compatible_intersection"])
        self.assertEqual(observed["observation_class"], "no_event")

    def test_opposite_flat_and_continuation(self):
        self.assertEqual(classify_move_relationship(signed_close_open(120, 100), signed_close_open(100, 120)), "opposite")
        self.assertEqual(classify_move_relationship(signed_close_open(100, 100), signed_close_open(80, 90)), "flat")
        self.assertEqual(classify_move_relationship(signed_close_open(100, 130), signed_close_open(80, 90)), "continuation")
        self.assertEqual(classify_move_relationship(signed_close_open(100, 130), None), "insufficient")
        self.assertEqual(classify_move_relationship(signed_close_open(100, 130), 0), "insufficient")


class IdentityAndBinTests(unittest.TestCase):
    def test_raw_contract_mismatch_excluded_and_root_date_is_not_a_match(self):
        self.assertEqual(raw_contract_match({"contract_key": "NQZ1"}, {"contract_key": "OTHER"}), "mismatch")
        self.assertEqual(raw_contract_match({"contract_key": "NQZ1"}, {"contract_key": "NQZ1"}), "matched")
        self.assertEqual(raw_contract_match({"source_version": "same"}, {"source_version": "same"}), "unresolved")
        self.assertEqual(raw_contract_match({"root": "NQ", "date": "2024-06-03"},
                                           {"root": "NQ", "date": "2024-06-03"}), "unresolved")

    def test_wrong_known_at_cannot_classify_early(self):
        self.assertTrue(jtr_known_before_turn(901, 930))
        self.assertFalse(jtr_known_before_turn(940, 930))
        self.assertFalse(jtr_known_before_turn(None, 930))

    def test_width_overlap_position_bins(self):
        self.assertEqual(width_ratio_bin(0.0), "0-0.25")
        self.assertEqual(width_ratio_bin(0.25), "0.25-0.5")
        self.assertEqual(width_ratio_bin(2.0), "2-inf")
        self.assertEqual(width_ratio_bin(None), "missing_own_geometry")
        self.assertEqual(overlap_bin(0.49), "0-0.5")
        self.assertEqual(overlap_bin(1.0), "1")
        self.assertEqual(position_bin(-0.1), "below")
        self.assertEqual(position_bin(1.0), "upper_half")
        self.assertEqual(position_bin(1.2), "above")

    def test_train_tertiles_ignore_confirmation_extreme(self):
        train = fit_root_prior_vol_tertiles({"NQ": [10.0, 20.0, 30.0]})
        mixed = fit_root_prior_vol_tertiles({"NQ": [10.0, 20.0, 30.0, 10000.0]})
        self.assertNotEqual(train["NQ"], mixed["NQ"])
        self.assertEqual(assign_prior_vol_bin(10000.0, train["NQ"]), "high")
        self.assertEqual(assign_prior_vol_bin(10.0, train["NQ"]), "low")

    def test_pairs_are_named_neighbors_not_cartesian(self):
        pairs = declared_clock_pairs(_plan())
        kinds = {(source, neighbor, kind) for source, neighbor, kind in pairs}
        self.assertIn(("JTR_fixed_04", "JTR_fixed_04__shift_-10m", "neighbor_shift"), kinds)
        self.assertIn(("JTR_fixed_04", "OR_activity_1_1", "or15_activity"), kinds)
        self.assertFalse(any(source == "OR_activity_1_1" for source, _, _ in pairs))
        self.assertEqual(len(pairs), 2)

    def test_source_variants_are_not_concatenated(self):
        development, confirmation = _workers()
        variants = split_source_variants(development, confirmation)
        names = [name for name, _ in variants]
        self.assertEqual(names, [PRIMARY_VARIANT, ORIGINAL_NQ2024_VARIANT])
        primary_years = {(shard["root"], shard["year"], bool(shard.get("source_supersession")))
                         for shard in variants[0][1]}
        original_years = {(shard["root"], shard["year"], bool(shard.get("source_supersession")))
                          for shard in variants[1][1]}
        self.assertIn(("NQ", 2024, True), primary_years)
        self.assertEqual(original_years, {("NQ", 2024, False)})
        self.assertNotEqual(primary_years, original_years)


class CommonTargetTests(unittest.TestCase):
    def test_same_target_across_clocks_is_never_gain(self):
        matrix = _common_matrix()
        self.assertEqual(common_target_clock_spread(matrix), 0.0)
        for name in COMMON_TARGETS:
            for day in ORDINALS:
                values = matrix.fields[name][matrix.fields["date"] == day]
                self.assertTrue(np.all(values == values[0]))

    def test_disagreement_is_rejected(self):
        matrix = _common_matrix()
        matrix.fields["common_terminal_priorW"][1] = 0.99
        with self.assertRaises(IntegrityError):
            common_target_clock_spread(matrix)

    def test_missing_clock_keeps_the_intended_date(self):
        matrix = _common_matrix()
        intended = intended_root_dates(matrix, 0)
        self.assertEqual(intended, ORDINALS)
        missing = (matrix.fields["date"] == date(2021, 1, 6).toordinal()) & ~matrix.fields["common_own_features_available"]
        self.assertTrue(np.any(missing))
        self.assertIn(date(2021, 1, 6).toordinal(), intended)


class RunnerFixtureTests(unittest.TestCase):
    def test_run_timing_statistics_retains_zero_events_and_separates_variants(self):
        development, confirmation = _workers()
        primary = _common_matrix()
        original = _common_matrix(days=(date(2024, 6, 3),), missing_neighbor=False)
        original.manifest = dict(original.manifest)
        original.manifest["id"] = "fixture-original"
        forms_primary = _formations()
        forms_original = _formations(days=(date(2024, 6, 3),))

        def materialize(_store, shards, _plan, *, resources, variant):
            resources["prepare_paths_calls"] += 1
            resources["common_adapter_calls"] += 1
            resources["table_reads"] += 1
            if resources["pilot"] is None:
                resources["pilot"] = {"variant": variant, "root": "NQ", "year": 2021,
                                      "common_rows": 1, "cpu_seconds": 0.0, "rss_bytes": 1, "rule": "fixture"}
            if variant == ORIGINAL_NQ2024_VARIANT:
                return original, forms_original
            self.assertEqual(variant, PRIMARY_VARIANT)
            years = {int(shard["year"]) for shard in shards}
            self.assertIn(2021, years)
            self.assertIn(2025, years)
            return primary, forms_primary

        with tempfile.TemporaryDirectory() as folder:
            store = ArtifactStore(Path(folder) / "artifacts")
            outputs = BoundedOutputs(Path(folder) / "out", maximum_total_bytes=8 * 1024 ** 2,
                                     maximum_file_bytes=4 * 1024 ** 2)
            with patch("trading_research.research.jumbo_timing_statistics._materialize_variant",
                       side_effect=materialize):
                summary = run_timing_statistics(
                    store=store, development=development, confirmation=confirmation,
                    analysis_plan=_plan(), outputs=outputs)
            report = Path(summary["refs"]["report"]["path"]).read_text()
            tables = json.loads(Path(summary["refs"]["tables"]["path"]).read_text())
        self.assertTrue(summary["success"])
        self.assertFalse(summary["fullContext"])
        self.assertFalse(summary["context_models_complete"])
        self.assertFalse(summary["family_statistics_complete"])
        self.assertIsNone(summary["results"]["clock_ranking"])
        ids = {check["id"] for check in summary["results"]["passed_checks"]}
        self.assertIn("identical_common_target_no_clock_gain", ids)
        self.assertIn("missing_clock_preserves_intended_date", ids)
        self.assertIn("train_quantile_thresholds_independent_of_confirmation", ids)
        self.assertIn("source_variants_not_concatenated", ids)
        self.assertIn("paired_rates_same_dates_zero_event_retained", ids)
        self.assertIn("no_86_46_replication", ids)
        variants = {name for name in summary["results"]["variants"]}
        self.assertEqual(variants, {PRIMARY_VARIANT, ORIGINAL_NQ2024_VARIANT})
        self.assertEqual(summary["refs"]["tables"]["kind"], "jumbo_timing_statistics_tables_v1")
        self.assertGreater(summary["refs"]["common_dates"]["rows"], 0)
        self.assertGreater(summary["refs"]["transition_dates"]["rows"], 0)
        self.assertIn("86.46", report)
        self.assertIn("not clock gain", report)
        self.assertIn("event_label_absent", report)
        self.assertNotIn("Judas reversal confirmed", report)
        self.assertIsNone(tables["clock_ranking"])
        self.assertFalse(tables["source_86_46_replicated"])
        train = tables["prior_vol_tertiles"]["NQ"]
        mixed = fit_root_prior_vol_tertiles({"NQ": [10.0, 20.0, 30.0, 10000.0]})["NQ"]
        self.assertEqual(tuple(train), fit_root_prior_vol_tertiles({"NQ": [10.0, 20.0, 30.0]})["NQ"])
        self.assertNotEqual(tuple(train), mixed)
        source_counts = (tables["variants"][PRIMARY_VARIANT]["product_b"]["slices"]
                         ["training_2020_2022"]["roots"]["NQ"]["windows"]["turn_source"]
                         ["identification_counts"])
        self.assertGreaterEqual(source_counts.get("no_event", 0), 1)
        self.assertGreaterEqual(source_counts.get("compatible_ambiguous", 0)
                                + source_counts.get("definite_print", 0), 1)
        original_dates = tables["variants"][ORIGINAL_NQ2024_VARIANT]["intended_root_dates"]["NQ"]
        primary_dates = tables["variants"][PRIMARY_VARIANT]["intended_root_dates"]["NQ"]
        self.assertEqual(original_dates, 1)
        self.assertEqual(primary_dates, 5)
        mismatch = (tables["variants"][PRIMARY_VARIANT]["product_b"]["slices"]
                    ["development_2023_2024"]["roots"]["NQ"]["windows"]["turn_source"]
                    ["identification_counts"])
        self.assertGreaterEqual(mismatch.get("raw_contract_mismatch_excluded", 0), 1)
        early = (tables["variants"][PRIMARY_VARIANT]["product_b"]["slices"]
                 ["confirmation_2025_2026"]["roots"]["NQ"]["windows"]["turn_source"]
                 ["identification_counts"])
        self.assertGreaterEqual(early.get("jtr_not_known_before_turn", 0), 1)


if __name__ == "__main__":
    unittest.main()


class ReviewedScientificRegressions(unittest.TestCase):
    def test_transition_retains_reference_known_at_and_actual_label_maturity(self):
        from trading_research.research.jumbo_timing_statistics import _transition_row
        jtr = _formation('JTR_fixed_04','2021-01-04',available=901,start=600,high=200,low=100)
        turn = _formation('turn_source','2021-01-04',available=951,start=940,open_=150,high=150,low=150,close=150)
        turn['zero_width'] = True
        row = _transition_row(PRIMARY_VARIANT,'NQ','2021-01-04',2021,jtr,turn,None,'turn_source')
        self.assertEqual(row['feature_known_at_ns'],901)
        self.assertEqual(row['target_maturity_ns'],951)
        self.assertEqual(row['move_relationship'],'flat')
        self.assertFalse(row['target_missing'])
        self.assertEqual(row['equilibrium_class'],'definite_print')

    def test_missing_transition_does_not_become_a_zero_event(self):
        from trading_research.research.jumbo_timing_statistics import _transition_row, _transition_root_tables
        jtr = _formation('JTR_fixed_04','2021-01-04',available=901,start=600,high=200,low=100)
        rows=[]
        for day, missing in [('2021-01-04',False),('2021-01-05',True)]:
            for clock in ('turn_earlier','turn_source','turn_later'):
                turn=None if missing else _formation(clock,day,available=951,start=940,open_=10,high=20,low=8,close=12)
                rows.append(_transition_row(PRIMARY_VARIANT,'NQ',day,2021,jtr,turn,None,clock))
        table = _transition_root_tables(rows,('2021-01-04','2021-01-05'),STATISTICS,{'bootstrap_metrics':0})
        rate=table['windows']['turn_source']['rates']['no_event']
        self.assertEqual(rate['estimate'],1.0)
        self.assertEqual(rate['valid_dates'],1)
        self.assertEqual(rate['missing_dates'],1)
        self.assertFalse(rate['interval_claimable'])
        pair=table['windows']['paired']['source_minus_earlier_print']
        self.assertEqual(pair['estimate'],0.0)
        self.assertEqual(pair['valid_dates'],1)

    def test_readable_report_uses_measured_conditional_targets(self):
        from trading_research.research.jumbo_timing_statistics import _group_record
        result=_group_record(np.array(['a','b','c']),np.array([True,False,True]),np.ones(3,dtype=bool),
            {'common_terminal_priorW':np.array([1.,200.,3.]),'common_high_priorW':np.array([2.,300.,4.]),'common_low_priorW':np.array([0.,400.,2.])},STATISTICS,'width_ratio','0.5-1')
        self.assertEqual(result['target_distributions']['common_terminal']['mean'],2.0)
        self.assertEqual(result['target_distributions']['common_up']['mean'],3.0)
        self.assertEqual(result['events'],2)
