"""Three public frozen INT-09 groups; assertions use independent literal oracles."""
from dataclasses import replace
from datetime import date
from fractions import Fraction
from tempfile import TemporaryDirectory
import unittest

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.research.folds import Sample, FittedArtifact, validate_oof
from trading_research.research.models import BinaryExample, FrequencyModel, fit_frequency, fit_logistic
from trading_research.experiments.e0.learning import (
    E0LearningConfig, e0_stages, audit_training_intervals, fit_e0_binary, year_start)
from trading_research.experiments.e0.learning_store import commit_e0_fit
from tests.e0_learning_fixtures import (literal, stage_literal_samples, analytic_learning_fixture,
    constant_learning_control, frequency_learning_control, physical_reach_learning_control,
    build_connected_bracket_router)


class E0LearningIntegrationTests(unittest.TestCase):
    def test_int09_f01_chronological_roles_and_interval_exclusions(self):
        case = literal("E0-INT-09-F01")
        rows = stage_literal_samples()
        config = E0LearningConfig(case["inputs"]["target_version"], "INT09-F01", "literal-five-rows")
        stages = e0_stages(rows, config)
        for role, key in (("fit", "fit_ids"), ("selection", "selection_ids"),
                          ("calibration", "calibration_ids"),
                          ("retrospective_evaluation", "evaluation_ids")):
            self.assertEqual(stages.ids(role), tuple(case["expected"][key]))
        self.assertEqual(stages.fit_fold.training_ids, ("s22-a", "s22-b"))
        self.assertEqual(stages.calibration_fold.training_ids, ("s24-a",))
        boundary = case["inputs"]["interval_purge_embargo_examples"]
        def sample(name):
            r = boundary[name]
            return Sample(r["id"], r["date_group"], r["decision_at"],
                          r["dependency_interval"][1], r.get("label_known_at", r["dependency_interval"][1]),
                          config.target_version)
        heldout = sample("heldout")
        for key in ("training_overlap", "training_embargo"):
            row = sample(key)
            self.assertEqual(audit_training_intervals((row,), (heldout,), embargo_ns=boundary["embargo_ns"]),
                             ((row.id, "purged"),))
        with self.assertRaisesRegex(ContractError, boundary["date_group_mate"]["reason"]):
            audit_training_intervals((sample("date_group_mate"),), (heldout,), embargo_ns=boundary["embargo_ns"])
        self.assertEqual({r.target_version for r in stages.population}, {config.target_version})
        wrong_date = tuple(replace(row, date_group="2022-01-01") if row.id == "s22-a" else row
                           for row in rows)
        with self.assertRaisesRegex(ContractError, "actual New York business date"):
            e0_stages(wrong_date, config)

    def test_int09_f02_future_insample_and_wrong_target_artifacts(self):
        case = literal("E0-INT-09-F02")
        source = case["inputs"]["sample"]
        query = Sample(**{k: v for k, v in source.items() if k != "past_lookback_end"})
        expected = {v["id"]: v["expected"]["reason"] for v in case["variants"]}
        for variant in case["inputs"]["artifact_variants"][:2]:
            with self.subTest(variant=variant["id"]):
                artifact = FittedArtifact(variant["artifact_id"], "binary_logistic", variant["fold_version"],
                    variant["fitted_at"], frozenset(variant["training_ids"]), frozenset(),
                    variant["fitted_at"], ())
                with self.assertRaisesRegex(ContractError, expected[variant["id"]]):
                    validate_oof(query, artifact.id, (artifact,), fold_version=variant["fold_version"])
        with TemporaryDirectory() as root:
            fixture = analytic_learning_fixture(root)
            fit = fit_e0_binary(fixture["examples"], fixture["config"])
            variant = case["inputs"]["artifact_variants"][2]
            # An actual fitted model is relabeled only for this negative control.
            wrong = replace(fit.selected, id=variant["artifact_id"], target_version=variant["target_version"])
            with self.assertRaisesRegex(ContractError, expected["wrong-target"]):
                wrong.predict(BinaryExample(query, (), 0))

    def test_int09_f03_typed_learning_selection_calibration_and_retained_serving(self):
        rows, fold, scope, query, oracle = constant_learning_control()
        for strength, coefficients in zip((.1, 1., 10.), oracle["expected_coefficients_for_lambda_0.1_1_10"]):
            model = fit_logistic(rows, fold, tuple(oracle["feature_columns"]), l2_strength=strength, scope=scope)
            self.assertEqual(model.means, tuple(oracle["expected_scaler_mean"]))
            self.assertEqual(model.scales, tuple(oracle["expected_scaler_scale_fallback"]))
            self.assertEqual(model.coefficients, tuple(coefficients))
            self.assertAlmostEqual(model.intercept, float(oracle["expected_intercept"]), places=8)
            self.assertAlmostEqual(model.predict(query)[0], float(oracle["expected_probability_all_rows"]), places=8)
        rows, fold, scope, populated, unseen, columns = frequency_learning_control()
        frequency = fit_frequency(rows, fold, columns, cuts=((.5,), (0.,), (.25, .5, 1.)), scope=scope)
        self.assertAlmostEqual(frequency.predict(populated)[0], 3/5, places=12)
        self.assertAlmostEqual(frequency.predict(unseen)[0], 4/7, places=12)
        self.assertEqual(frequency.predict(populated)[1]["cell_support"], 3)
        self.assertEqual(frequency.predict(unseen)[1]["cell_support"], 0)
        rows, config, physical = physical_reach_learning_control()
        physical_fit = fit_e0_binary(rows, config)
        by_physical = {e.sample.id: e for e in rows}
        for row in physical["fit_rows"]:
            actual = by_physical[row["id"]]
            self.assertEqual(actual.outcome, row["label"])
            import json
            self.assertEqual(tuple(json.loads(v.payload_json) for v in actual.values), tuple(row["features"]))
        for model in physical_fit.logistic_candidates:
            self.assertEqual(model.coefficients, (0.,) * 5)
            self.assertAlmostEqual(model.intercept, 0., places=8)
        self.assertEqual(physical_fit.selected_lambda, .1)
        self.assertAlmostEqual(physical_fit.calibrated.calibration.intercept, 0., places=8)
        self.assertAlmostEqual(physical_fit.calibrated.calibration.coefficients[0], 0., places=8)
        self.assertAlmostEqual(physical_fit.calibrated.predict(rows[-1])[0], .5, places=8)
        with TemporaryDirectory() as root:
            fixture = analytic_learning_fixture(root)
            examples, config = fixture["examples"], fixture["config"]
            fit = fit_e0_binary(examples, config)
            linked = fixture["literal"]["linked_nonconstant_pipeline"]
            by = {e.sample.id: e for e in examples}
            for model, oracle in zip(fit.logistic_candidates, linked["fit_artifacts_and_selection_predictions"]):
                with self.subTest(strength=oracle["lambda"]):
                    self.assertEqual(model.l2_strength, float(oracle["lambda"]))
                    self.assertAlmostEqual(model.intercept, float(oracle["intercept"]), places=7)
                    for actual, expected in zip(model.coefficients, oracle["coefficients"]):
                        self.assertAlmostEqual(actual, float(expected), places=7)
                    self.assertAlmostEqual(dict(fit.selection_scores)[model.l2_strength],
                                           float(oracle["selection_logloss"]), places=7)
                    for row in oracle["predictions"]:
                        p, reads = model.predict(by[row["id"]])
                        self.assertAlmostEqual(p, float(row["probability"]), places=7)
                        self.assertTrue(reads["input_manifest"]["actual_reads"])
            self.assertEqual(fit.selected_lambda, .1)
            self.assertAlmostEqual(fit.calibrated.calibration.intercept, 0., places=7)
            self.assertGreater(fit.calibrated.calibration.coefficients[0], 0.)
            zero = by["INT09-extra-zero-evaluation"]
            self.assertAlmostEqual(fit.calibrated.predict(zero)[0], .5, places=7)
            for row in linked["calibration_2024"]["model_predictions_from_actual_selected_w1"]:
                self.assertAlmostEqual(fit.selected.predict(by[row["id"]])[0], float(row["probability"]), places=7)
            self.assertAlmostEqual(fit.selected.predict(by["eval-s25-1"])[0],
                                   float(fixture["literal"]["evaluation_predictions_2025"][0]["raw_probability"]), places=7)
            flipped = tuple(replace(e, outcome=1-e.outcome) if e.sample.date_group.startswith("2025") else e for e in examples)
            same = fit_e0_binary(flipped, config)
            self.assertEqual((same.selected.id, same.calibrated.id, same.selection_scores),
                             (fit.selected.id, fit.calibrated.id, fit.selection_scores))
            late = tuple(replace(e, sample=replace(e.sample, label_known_at=year_start(2024)+1))
                         if e.sample.id == "sel-23-a" else e for e in examples)
            with self.assertRaisesRegex(DependencyUnavailable, "selection labels unavailable"):
                fit_e0_binary(late, config)
            single = tuple(replace(e, outcome=0) if e.sample.date_group.startswith("2022") else e for e in examples)
            fallback = fit_e0_binary(single, config)
            self.assertIsInstance(fallback.calibrated, FrequencyModel)
            self.assertEqual(fallback.logistic_candidates, ())
            single_cal = tuple(replace(e, outcome=0) if e.sample.date_group.startswith("2024") else e for e in examples)
            with self.assertRaises(ContractError):
                fit_e0_binary(single_cal, config)
            committed = commit_e0_fit(fixture["store"], namespace=fixture["namespace"],
                **fixture["references"], examples=examples, fit=fit)
            for model in (fit.frequency, *fit.logistic_candidates, fit.calibrated):
                binding = committed.binding(model)
                reopened = binding.reopen()
                self.assertEqual(reopened.id, model.id)
                p, reads = binding.predict(zero)
                self.assertAlmostEqual(p, model.predict(zero)[0], places=12)
                self.assertTrue(reads)
        from tests.e0_source_fixtures import make_run_day
        evaluation_day = make_run_day(date(2025, 6, 2), quote_path="comparator_down")
        with TemporaryDirectory() as root:
            router, evidence = build_connected_bracket_router(root, (evaluation_day,))
            for policy, heads in router.policies:
                for head in heads:
                    self.assertEqual(len(head.fit.stages.ids("fit")), 8)
                    self.assertEqual(len(head.fit.stages.ids("selection")), 8)
                    self.assertEqual(len(head.fit.stages.ids("calibration")), 8)
                    self.assertEqual(len(head.fit.config.columns), 10)
                    self.assertEqual((head.fit.config.policy_version, head.fit.config.head), (policy, head.name))
                    query = next(e for e in head.examples if e.sample.date_group == evaluation_day.day)
                    if head.name == "deadline":
                        self.assertIsInstance(head.fit.calibrated, FrequencyModel)
                        self.assertEqual(head.fit.logistic_candidates, ())
                        self.assertAlmostEqual(head.fit.frequency.overall, .1, places=12)
                        self.assertAlmostEqual(head.committed(head.fit.calibrated, query)[0], .25, places=12)
                    else:
                        self.assertEqual(head.fit.selected_lambda, .1)
                        for model in head.fit.logistic_candidates:
                            self.assertEqual(model.coefficients, (0.,)*10)
                            self.assertAlmostEqual(model.intercept, 0., places=8)
                        self.assertAlmostEqual(head.committed(head.fit.calibrated, query)[0], .5, places=12)
                actual_rows = dict(evidence["policies"])[policy]
                for day_id, row, features, plan, outcome in actual_rows:
                    self.assertEqual(plan.horizon_end, row.cut + 900_000_000_000)
                    self.assertTrue(outcome.observation_complete)
                    if day_id != evaluation_day.day:
                        expected = "target" if (day_id.endswith("-01") == (row.side == 1)) else "stop"
                        self.assertEqual(outcome.exit_reason, expected)
                        continue
                    for branch in ("frequency", "logistic"):
                        prediction = router(branch=branch, policy_version=policy, day=evaluation_day,
                                            row=row, features=features)
                        self.assertEqual(prediction.probabilities,
                            (("target", Fraction(2, 5)), ("stop", Fraction(2, 5)), ("deadline", Fraction(1, 5))))
                        self.assertEqual(len(prediction.head_evidence), 3)
                        self.assertEqual(sum(p for _, p in prediction.probabilities), 1)
                        from trading_research.experiments.e0.policy import E0CommittedPredictionEvidence
                        evidence = E0CommittedPredictionEvidence.from_prediction(prediction)
                        self.assertEqual(evidence.fitted_at, max(
                            head[4]["verified_head_receipt"].fitted_at for head in prediction.head_evidence))
                        self.assertEqual(evidence.probabilities, prediction.probabilities)
                        with self.assertRaises(ContractError):
                            E0CommittedPredictionEvidence.from_prediction(
                                prediction, fitted_at=evidence.fitted_at - 1)
                        with self.assertRaises(ContractError):
                            E0CommittedPredictionEvidence.from_prediction(object())
                        with self.assertRaises(ContractError):
                            replace(prediction, probabilities=(("target", Fraction(1, 5)),
                                ("stop", Fraction(2, 5)), ("deadline", Fraction(2, 5))))
                        with self.assertRaises(ContractError):
                            replace(prediction, sample_id="different-query")
                        with self.assertRaises(ContractError):
                            replace(prediction.head_evidence[0][4]["verified_head_receipt"],
                                    probability=Fraction(1))
