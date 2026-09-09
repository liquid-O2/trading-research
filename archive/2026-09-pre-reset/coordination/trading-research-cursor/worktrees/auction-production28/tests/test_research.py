from dataclasses import asdict, replace
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import ContractError
from trading_research.foundations.units import Ticks
from trading_research.operations.provenance import InputAudit, InputValue, cache_key, compatible_checkpoint
from trading_research.operations.trials import TrialRegistry
from trading_research.research.folds import FittedArtifact, Sample, chronological_fold, validate_oof
from trading_research.research.labels import ObservationWindow, PathPoint, ohlc_barrier_order, reference_path_label
from tests.test_foundations import target


class LabelTests(unittest.TestCase):
    def label(self, prices, *, coverage=None, base=None):
        points = tuple(PathPoint(11 + n, n, Ticks(p), 12 + n) for n, p in enumerate(prices))
        return reference_path_label(base or target(), initial=Ticks(100), points=points,
                                    coverage=coverage or ObservationWindow(10, 30, 31, version="full-tape-v1"),
                                    up_ticks=4, down_ticks=4)

    def test_identical_extrema_and_terminal_do_not_identify_barrier_order(self):
        up = self.label([105, 95, 100])
        down = self.label([95, 105, 100])
        self.assertEqual((up.terminal_ticks, up.maximum_up_ticks, up.maximum_down_ticks),
                         (down.terminal_ticks, down.maximum_up_ticks, down.maximum_down_ticks))
        self.assertEqual((up.first_barrier, down.first_barrier), ("upper", "lower"))
        self.assertEqual(ohlc_barrier_order(initial=Ticks(100), high=Ticks(105), low=Ticks(95),
                                            up_ticks=4, down_ticks=4), "ambiguous")

    def test_one_sided_excursion_includes_initial_zero_and_absent_future_is_censored(self):
        self.assertEqual(self.label([101, 103]).maximum_down_ticks, 0)
        self.assertEqual(self.label([99, 97]).maximum_up_ticks, 0)
        partial = self.label([], coverage=ObservationWindow(10, 20, 21, version="truncated"))
        self.assertEqual(partial.status, "censored")
        self.assertIsNone(partial.terminal_ticks)
        absent = self.label([])
        self.assertEqual((absent.status, absent.first_barrier, absent.terminal_ticks), ("censored", None, None))
        self.assertEqual((absent.maximum_up_ticks, absent.maximum_down_ticks, absent.observed_count),
                         (None, None, 0))
        observed_flat = self.label([100])
        self.assertEqual((observed_flat.status, observed_flat.first_barrier, observed_flat.terminal_ticks),
                         ("observed", "neither", 0))
        carried = self.label([], base=replace(target(), observation_process="certified_last_observed_mark"))
        self.assertEqual((carried.status, carried.first_barrier, carried.terminal_ticks),
                         ("observed", "neither", 0))
        carried_gap = self.label([], base=replace(target(), observation_process="certified_last_observed_mark"),
                                 coverage=ObservationWindow(10, 30, 31, gaps=((20, 25),), version="gap"))
        self.assertEqual((carried_gap.status, carried_gap.terminal_ticks), ("censored", None))

    def test_fixed_endpoint_not_restarted_at_contact_and_gap_not_clean_no_contact(self):
        original = self.label([102])
        later = self.label([], base=target(at=15, end=35), coverage=ObservationWindow(15, 35, 36, version="later"))
        self.assertNotEqual(original.target_signature, later.target_signature)
        gap = self.label([102], coverage=ObservationWindow(10, 30, 31, gaps=((20, 25),), version="gap"))
        self.assertEqual(gap.status, "censored")
        self.assertIsNone(gap.first_barrier)

    def test_unknown_same_timestamp_order_stays_ambiguous_and_maturity_uses_receipt(self):
        result = reference_path_label(target(), initial=Ticks(100),
                                      points=(PathPoint(11, 0, Ticks(105), 40), PathPoint(11, 1, Ticks(95), 41)),
                                      coverage=ObservationWindow(10, 30, 31, source_order_known=False, version="unordered"),
                                      up_ticks=4, down_ticks=4)
        self.assertEqual(result.first_barrier, "ambiguous")
        self.assertEqual(result.status, "ambiguous")
        self.assertIsNone(result.terminal_ticks)
        self.assertEqual(result.maturity_at, 41)


class FoldTests(unittest.TestCase):
    def test_forward_grouped_fold_purges_maturity_and_interval_overlap(self):
        samples = (Sample("past", "d0", 1, 5, 4, "v"), Sample("late-oi", "d1", 10, 32, 15, "v"),
                   Sample("carry", "d1", 11, 20, 20, "v"), Sample("NQ", "d2", 21, 30, 29, "v"),
                   Sample("ES", "d2", 22, 31, 30, "v"))
        fold = chronological_fold(samples, id="f", fit_at=20, evaluation_start=21, evaluation_end=40, embargo_ns=1)
        self.assertEqual(fold.training_ids, ("past",))
        self.assertEqual(fold.evaluation_ids, ("NQ", "ES"))
        self.assertEqual(dict(fold.purged), {"late-oi": "label_not_mature_at_fit",
                                          "carry": "dependency_interval_overlaps_evaluation_or_embargo"})
        with self.assertRaises(ContractError):
            chronological_fold(samples, id="split", fit_at=21, evaluation_start=22, evaluation_end=40)
        with self.assertRaises(ContractError):
            chronological_fold(samples, id="future-fit", fit_at=23, evaluation_start=21, evaluation_end=40)

    def test_scaler_leakage_and_missing_calibrator_dependency_fail_transitively(self):
        sample = Sample("NQ", "d2", 21, 30, 29, "v")
        scale = FittedArtifact("scaler", "scaler", "fold1", 10, frozenset({"past"}), frozenset({"d0"}), 5, ())
        model = FittedArtifact("expert", "expert", "fold1", 11, frozenset({"past"}), frozenset({"d0"}), 5, ("scaler",))
        cal = FittedArtifact("calibrator", "calibrator", "fold1", 15, frozenset({"cal"}), frozenset({"d1"}), 14, ("expert",))
        self.assertEqual(validate_oof(sample, "calibrator", [scale, model, cal], fold_version="fold1"),
                         ("calibrator", "expert", "scaler"))
        with self.assertRaises(ContractError):
            validate_oof(sample, "calibrator", [replace(scale, training_groups=frozenset({"d2"})), model, cal], fold_version="fold1")
        with self.assertRaises(ContractError):
            validate_oof(sample, "calibrator", [model, cal], fold_version="fold1")
        with self.assertRaises(ContractError):
            validate_oof(sample, "calibrator", [scale, model, cal], fold_version="fold2")


class InputLineageTests(unittest.TestCase):
    def test_actual_reads_reject_omitted_undeclared_and_future_adjusted_columns(self):
        values = {"a": InputValue("a", "v1", 5, b"1"), "b": InputValue("b", "v2", 12, b"2")}
        view = InputAudit(frozenset({"a", "b"}), values, cut=10, fold_version="fold1")
        self.assertEqual(view.read("a"), b"1")
        with self.assertRaises(ContractError):
            view.read("b")
        with self.assertRaises(ContractError):
            view.read("future_label")
        with self.assertRaises(ContractError):
            view.manifest()
        old = InputAudit(frozenset({"a"}), values, cut=10, fold_version="fold1")
        old.read("a")
        new = InputAudit(frozenset({"a"}), {"a": replace(values["a"], version="v2")}, cut=10, fold_version="fold1")
        new.read("a")
        self.assertNotEqual(old.manifest(), new.manifest())

    def test_cache_changes_for_equal_value_new_version_and_calibration_fold(self):
        params = dict(code_hash="code", inputs={"price": "v1"}, target_version="t", fold_version="f",
                      transform_versions=("scale1",), model_version="m", calibrator_version="c1",
                      numerical_settings={"precision": "float64", "seed": 1}, configuration={"window": 20})
        original = cache_key(**params)
        for field, value in (("inputs", {"price": "v2"}), ("calibrator_version", "c2"), ("fold_version", "f2"),
                             ("transform_versions", ("scale2",)), ("configuration", {"window": 21})):
            changed = cache_key(**{**params, field: value})
            self.assertNotEqual(original, changed)
            with self.assertRaises(ContractError):
                compatible_checkpoint({"cache_key": original, "state": {"row": 42}}, changed)
        self.assertEqual(compatible_checkpoint({"cache_key": original, "state": {"row": 42}}, original), {"row": 42})


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.registry = TrialRegistry(Path(self.temp.name))
        self.registry.register_family("pilot-v1", scope_ids=("V03", "V08"), protocol={"kind": "engineering", "endpoint": "fixed"},
                                      max_attempts=2, cpu_budget_seconds=10)

    def register(self, name="first", configuration=None):
        return self.registry.register(name=name, family="pilot-v1", stage="engineering", configuration=configuration or {"window": 20},
                                      code_hash="code", data_hashes={"fixture": "v1"}, fold_version="f", target_version="t")

    def test_renamed_trials_failures_and_restarts_remain_in_search_and_resource_history(self):
        first = self.register()
        self.assertEqual(self.register("renamed"), first)
        self.assertEqual(len(self.registry.state()["trials"]), 1)
        attempt = self.registry.start(first, cpu_reservation_seconds=5)
        with self.assertRaises(ContractError):
            self.registry.start(first, cpu_reservation_seconds=5)
        self.registry.finish(attempt, status="interrupted", cpu_seconds=None, wall_seconds=None,
                             peak_rss_bytes=None, reason="fixture simulates worker lost before telemetry")
        self.registry = TrialRegistry(Path(self.temp.name))
        stored = self.registry.state()["attempts"][attempt]
        self.assertEqual(stored["cpu_seconds"], 5)
        self.assertEqual(stored["resource_basis"], "reservation_charged_usage_unknown")
        with self.assertRaises(ContractError):
            self.registry.start(first, cpu_reservation_seconds=6)
        second = self.registry.start(first, cpu_reservation_seconds=5)
        self.registry.finish(second, status="failed", cpu_seconds=1.0, wall_seconds=2.0, peak_rss_bytes=100,
                             reason="intentional null-control failure")
        with self.assertRaises(ContractError):
            self.registry.start(first, cpu_reservation_seconds=1)
        self.assertEqual(len(self.registry.state()["attempts"]), 2)

    def test_protocol_change_new_search_and_success_without_evidence(self):
        first = self.register()
        changed = self.register(configuration={"window": 21})
        self.assertNotEqual(first, changed)
        with self.assertRaises(ContractError):
            self.registry.register_family("pilot-v1", scope_ids=("V03", "V08"), protocol={"endpoint": "extend-until-pass"},
                                          max_attempts=50, cpu_budget_seconds=100)
        attempt = self.registry.start(first, cpu_reservation_seconds=1)
        with self.assertRaises(ContractError):
            self.registry.finish(attempt, status="succeeded", cpu_seconds=0.1, wall_seconds=0.2,
                                 peak_rss_bytes=100, reason="missing output")
        ref = self.registry.artifacts.put_json({"status": "fixture passed"}, kind="test-output")
        self.registry.finish(attempt, status="succeeded", cpu_seconds=0.1, wall_seconds=0.2,
                             peak_rss_bytes=100, reason="synthetic fixture output", result_artifacts=(asdict(ref),))
        with self.assertRaises(ContractError):
            self.registry.finish(attempt, status="failed", cpu_seconds=0.1, wall_seconds=0.2, peak_rss_bytes=100, reason="overwrite")
