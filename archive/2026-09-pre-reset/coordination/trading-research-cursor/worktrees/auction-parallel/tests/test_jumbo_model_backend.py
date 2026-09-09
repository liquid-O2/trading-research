"""Independent literal checks for the standalone Jumbo numerical backend.

This file is deliberately not executed in the implementation tranche.  The
oracles use the declared equations directly instead of importing the research
pipeline's feature, fold, or data code.
"""

import json
import math
import unittest
from dataclasses import replace

import numpy as np

from trading_research.research.jumbo_model_backend import (
    BackendInputError,
    EmpiricalCategoricalFit,
    HGBChallenger,
    QuantileFit,
    fit_empirical_categorical,
    fit_empirical_quantiles,
    fit_quantile_residual_calibration,
    fit_quantiles,
    fit_softmax,
    fit_temperature,
    fit_hgb_challenger,
    predict_empirical_categorical,
    predict_empirical_quantiles,
    predict_quantile_residual,
    predict_quantiles,
    predict_softmax,
    predict_temperature,
    _pinball_objective_gradient,
    _smooth_pinball_objective_gradient,
    _temperature_objective_gradient,
    _softmax_objective_gradient,
    offset_array_checksum,
)


def literal_softmax(logits):
    shifted = logits - logits.max(axis=1, keepdims=True)
    values = np.exp(shifted)
    return values / values.sum(axis=1, keepdims=True)


class JumboNumericalBackendTests(unittest.TestCase):
    def test_softmax_objective_and_gradient_match_literal_binary_logistic_equation(self):
        X = np.asarray([[0.0], [1.0], [-1.0]], dtype=float)
        y = np.asarray([0, 1, 0], dtype=int)
        allowed = np.asarray([[True, False], [False, True], [True, False]], dtype=bool)
        weights = np.asarray([1.0, 2.0, 1.0])
        theta = np.asarray([[0.10, 0.30], [-0.20, 0.40]], dtype=float).reshape(-1)
        probabilities = literal_softmax(X @ theta.reshape(2, 2)[:, 1:].T + theta.reshape(2, 2)[:, 0])
        total = weights.sum()
        expected_loss = np.dot(weights, -np.log(probabilities[np.arange(3), y])) / total
        expected_loss += 0.5 * 0.7 * np.sum(theta.reshape(2, 2)[:, 1:] ** 2)
        residual = probabilities.copy()
        residual[np.arange(3), y] -= 1.0
        expected_gradient = np.concatenate((
            ((weights[:, None] * residual).sum(axis=0) / total)[:, None],
            (weights[:, None] * residual).T @ X / total
                + 0.7 * theta.reshape(2, 2)[:, 1:],
        ), axis=1).reshape(-1)
        actual_loss, actual_gradient = _softmax_objective_gradient(
            X, allowed, weights, theta, l2=0.7, batch_size=2,
        )
        self.assertAlmostEqual(actual_loss, expected_loss, places=12)
        np.testing.assert_allclose(actual_gradient, expected_gradient, atol=1e-12)

    def test_allowed_class_likelihood_excludes_all_class_rows_without_negative_imputation(self):
        X = np.asarray([[0.0], [1.0], [2.0]], dtype=float)
        allowed = np.asarray([[True, False, False], [False, True, False],
                              [True, True, True]], dtype=bool)
        fit = fit_softmax(X, allowed, classes=("lower", "upper", "other"), l2=.2,
                          max_iterations=30, metadata={"target": "first_side"})
        self.assertEqual(fit.label_mode, "allowed_class_set")
        self.assertEqual(fit.all_class_rows, 1)
        self.assertEqual(fit.informative_rows, 2)
        # No informative row observes class three, so this fixture must not
        # assume a finite optimum within30 iterations. It checks exclusion
        # and the explicitly requested fallback, while rejection stays strict.
        if not fit.converged:
            with self.assertRaises(BackendInputError):
                predict_softmax(fit, X)
        probabilities = predict_softmax(fit, X, allow_fallback=True)
        np.testing.assert_allclose(probabilities.sum(axis=1), 1.0, atol=1e-12)
        all_class = fit_softmax(X, np.ones((3, 3), dtype=bool), classes=(0, 1, 2), l2=.2)
        self.assertEqual(all_class.status, "all_class_rows_fallback")
        self.assertEqual(all_class.informative_rows, 0)

    def test_softmax_empty_single_class_and_fixed_offset_metadata(self):
        X = np.asarray([[0.0], [1.0]], dtype=float)
        empty = fit_softmax(np.empty((0, 1)), np.asarray([], dtype=int), classes=(0, 1), l2=.2)
        self.assertEqual(empty.status, "empty_fallback")
        np.testing.assert_allclose(predict_softmax(empty, X).sum(axis=1), 1.0)
        single = fit_softmax(X, np.asarray([1, 1]), classes=(0, 1), l2=.2)
        self.assertEqual(single.status, "single_class_fallback")
        offset = np.asarray([[3.0, -3.0], [3.0, -3.0]])
        fitted = fit_softmax(X, np.asarray([0, 1]), classes=(0, 1), l2=.2,
                             offset_logits=offset, offset_identity="baseline-v1")
        self.assertEqual(fitted.offset_identity, "baseline-v1")
        self.assertEqual(fitted.as_dict()["offset_identity"], "baseline-v1")
        np.testing.assert_allclose(predict_softmax(fitted, X, offset_logits=offset).sum(axis=1), 1.0)
        with self.assertRaises(BackendInputError):
            predict_softmax(fitted, X)
        X = np.asarray([[0.0], [1.0], [-1.0]], dtype=float)
        offset_oracle = np.asarray([[0.5, -0.5], [0.5, -0.5], [0.5, -0.5]])
        theta = np.asarray([[0.10, 0.30], [-0.20, 0.40]], dtype=float).reshape(-1)
        probabilities = literal_softmax(
            X @ theta.reshape(2, 2)[:, 1:].T + theta.reshape(2, 2)[:, 0] + offset_oracle
        )
        offset_loss, offset_gradient = _softmax_objective_gradient(
            X, np.asarray([[True, False], [False, True], [True, False]], dtype=bool),
            np.ones(3), theta, l2=0.0, batch_size=2, offset_logits=offset_oracle,
        )
        expected_offset_loss = float(np.mean(-np.log(probabilities[[0, 1, 2], [0, 1, 0]])))
        residual = probabilities.copy()
        residual[[0, 1, 2], [0, 1, 0]] -= 1.0
        expected_offset_gradient = np.concatenate((
            residual.sum(axis=0)[:, None], residual.T @ X,
        ), axis=1).reshape(-1) / 3.0
        self.assertAlmostEqual(offset_loss, expected_offset_loss, places=12)
        np.testing.assert_allclose(offset_gradient, expected_offset_gradient, atol=1e-12)

    def test_pinball_objective_gradient_and_quantile_crossing_correction(self):
        X = np.asarray([[0.0], [1.0], [-1.0]], dtype=float)
        y = np.asarray([0.0, 2.0, 1.0], dtype=float)
        weights = np.asarray([1.0, 2.0, 1.0])
        theta = np.asarray([.5, .2])
        q = .75
        loss, gradient = _pinball_objective_gradient(X, y, weights, theta,
                                                     quantile=q, l2=.1, batch_size=2)
        residual = y - (theta[0] + X[:, 0] * theta[1])
        literal_loss = np.dot(weights, np.where(residual >= 0, q * residual, (q - 1) * residual)) / weights.sum()
        literal_loss += .05 * theta[1] ** 2
        slope = np.where(residual > 0, -q, np.where(residual < 0, 1 - q, 0.0))
        literal_gradient = np.asarray([
            np.dot(weights, slope) / weights.sum(),
            np.dot(weights * slope, X[:, 0]) / weights.sum() + .1 * theta[1],
        ])
        self.assertAlmostEqual(loss, literal_loss, places=12)
        np.testing.assert_allclose(gradient, literal_gradient, atol=1e-12)
        fitted = fit_quantiles(X, np.asarray([[0.0, 1.0], [0.0, 2.0], [1.0, 3.0]]),
                               quantiles=(.1, .5, .9), l2=.05, max_iterations=1000)
        predictions, diagnostics = predict_quantiles(fitted, X, return_diagnostics=True)
        self.assertEqual(predictions.shape, (3, 2, 3))
        self.assertEqual(diagnostics["rows_with_crossing_after"], 0)
        self.assertTrue(np.all(predictions[:, :, :-1] <= predictions[:, :, 1:]))

    def test_zero_atoms_constant_and_fixed_quantile_offsets_are_explicit(self):
        X = np.asarray([[0.0], [1.0], [2.0]], dtype=float)
        constant = fit_quantiles(X, np.zeros((3, 1)), quantiles=(.1, .5, .9), l2=.1)
        self.assertEqual(constant.status, "converged")
        self.assertEqual(constant.diagnostics[0]["status"], "constant_target_fallback")
        empirical = fit_empirical_quantiles(np.asarray([0.0, 0.0, 2.0]), quantiles=(.25, .5, .75), shrinkage=2.)
        self.assertEqual(empirical.status, "zero_atom_supported")
        self.assertGreaterEqual(empirical.zero_atoms, 2)
        np.testing.assert_array_equal(predict_empirical_quantiles(empirical),
                                      np.maximum.accumulate(predict_empirical_quantiles(empirical), axis=-1))
        offsets = np.asarray([[[1., 2., 3.]], [[1., 2., 3.]], [[1., 2., 3.]]])
        fitted = fit_quantiles(X, np.asarray([[0.0], [1.0], [2.0]]), quantiles=(.1, .5, .9),
                               l2=.1, max_iterations=1000, offset_quantiles=offsets, offset_identity="q-baseline-v1")
        self.assertEqual(fitted.offset_identity, "q-baseline-v1")
        predicted = predict_quantiles(fitted, X, offset_quantiles=offsets)
        self.assertEqual(predicted.shape, (3, 1, 3))
        constant_with_offset = fit_quantiles(
            X, np.zeros((3, 1)), quantiles=(.1, .5, .9), l2=.1,
            offset_quantiles=offsets, offset_identity="q-baseline-v1",
        )
        self.assertEqual(constant_with_offset.status, "converged")
        corrected = predict_quantiles(constant_with_offset, X, offset_quantiles=offsets)
        smooth_roots = np.asarray([.001 * math.log(q / (1.0 - q)) for q in (.1, .5, .9)])
        np.testing.assert_allclose(corrected, np.tile(smooth_roots, (3,1,1)), atol=1e-12)
        empty_fallback = fit_empirical_quantiles(
            np.asarray([], dtype=float), quantiles=(.25, .5, .75), shrinkage=1.0,
            fallback_quantiles=(3.0, 1.0, 2.0),
        )
        np.testing.assert_array_equal(
            predict_empirical_quantiles(empty_fallback, correct_crossing=False),
            np.asarray([[3.0, 3.0, 3.0]]),
        )

    def test_empirical_categorical_shrinkage_and_empty_fallback_are_simplex_safe(self):
        empty = fit_empirical_categorical(np.asarray([], dtype=object), classes=("a", "b"), shrinkage=2.)
        self.assertIsInstance(empty, EmpiricalCategoricalFit)
        self.assertEqual(empty.status, "empty_fallback")
        np.testing.assert_allclose(predict_empirical_categorical(empty).sum(axis=1), 1.0)
        fitted = fit_empirical_categorical(np.asarray(["a", "a", "b"], dtype=object),
                                           classes=("a", "b"), shrinkage=2.,
                                           group_ids=("x", "x", "y"))
        self.assertEqual(fitted.status, "smoothed_empirical")
        predictions = predict_empirical_categorical(fitted, ("x", "y", "unknown"))
        np.testing.assert_allclose(predictions.sum(axis=1), 1.0, atol=1e-12)
        self.assertFalse(np.array_equal(predictions[0], predictions[2]))

    def test_temperature_and_residual_calibration_keep_separate_closure_metadata(self):
        logits = np.asarray([[2., -1.], [-1., 2.], [1., -1.]], dtype=float)
        labels = np.asarray([0, 1, 0], dtype=int)
        temperature = fit_temperature(logits, labels, classes=(0, 1), source_fit_id="fit-v1",
                                       calibration_id="cal-v1", metadata={"target": "path"})
        self.assertEqual(temperature.source_fit_id, "fit-v1")
        self.assertEqual(temperature.calibration_id, "cal-v1")
        self.assertEqual(temperature.as_dict()["metadata"]["target"], "path")
        probabilities = predict_temperature(temperature, logits)
        np.testing.assert_allclose(probabilities.sum(axis=1), 1.0, atol=1e-12)
        predictions = np.asarray([[2., 1., 0.], [0., 1., 2.]])
        residual = fit_quantile_residual_calibration(
            predictions, np.asarray([1., 2.]), quantiles=(.1, .5, .9),
            source_fit_id="fit-v1", calibration_id="q-cal-v1",
            metadata={"calibration_population": "2024H1"},
        )
        self.assertEqual(residual.source_fit_id, "fit-v1")
        calibrated, diagnostic = predict_quantile_residual(residual, predictions, return_diagnostics=True)
        self.assertEqual(diagnostic["rows_with_crossing_after"], 0)
        self.assertTrue(np.all(calibrated[:, :-1] <= calibrated[:, 1:]))

    def test_smooth_pinball_declares_uniform_bound_and_fuses_heads(self):
        X = np.asarray([[0.0], [1.0], [2.0]], dtype=float)
        y = np.asarray([0.0, 2.0, 1.0], dtype=float)
        theta = np.asarray([0.2, 0.1])
        epsilon = 0.25
        smooth_loss, smooth_gradient = _smooth_pinball_objective_gradient(
            X, y, np.ones(3), theta, quantile=.75, l2=0.0,
            batch_size=2, epsilon=epsilon,
        )
        residual = y - (theta[0] + X[:, 0] * theta[1])
        exact = np.where(residual >= 0, .75 * residual, -.25 * residual)
        smooth = .75 * residual + epsilon * np.logaddexp(0.0, -residual / epsilon)
        self.assertTrue(np.all(smooth - exact >= -1e-12))
        self.assertLessEqual(float(np.mean(smooth - exact)), epsilon * math.log(2.0) + 1e-12)
        self.assertEqual(smooth_gradient.shape, theta.shape)
        derivative = .75 - 1.0 / (1.0 + np.exp(residual / epsilon))
        np.testing.assert_allclose(
            smooth_gradient,
            np.asarray([-np.mean(derivative), -np.mean(derivative * X[:, 0])]),
            atol=1e-12,
        )
        fitted = fit_quantiles(
            X, np.asarray([[0.0, 1.0], [1.0, 2.0], [2.0, 3.0]]),
            quantiles=(.1, .5, .9), l2=.05, max_iterations=40,
            smooth_epsilon=epsilon,
        )
        self.assertEqual(fitted.metadata["optimizer"], "fused_scipy.optimize.minimize:L-BFGS-B")
        self.assertAlmostEqual(fitted.loss_error_bound, 2 * 3 * epsilon * math.log(2.0), places=12)
        self.assertAlmostEqual(
            fitted.metadata["loss_error_bound_per_head"], epsilon * math.log(2.0), places=12,
        )
        self.assertEqual(len(fitted.diagnostics), 6)
        self.assertTrue(all("kkt_residual" in row for row in fitted.diagnostics))

    def test_quantile_prediction_rejects_failed_fit_and_exposes_projection(self):
        fitted = fit_quantiles(
            np.asarray([[0.0], [1.0], [2.0]]), np.asarray([[0.0], [1.0], [2.0]]),
            quantiles=(.1, .5, .9), l2=.1, max_iterations=10,
        )
        failed = replace(fitted, converged=False, status="nonconverged")
        with self.assertRaises(BackendInputError):
            predict_quantiles(failed, np.asarray([[0.0]]))
        projected, raw, diagnostics = predict_quantiles(
            fitted, np.asarray([[0.0]]), return_raw=True, return_diagnostics=True,
            allow_fallback=True,  # This branch verifies projection, not convergence.
        )
        self.assertEqual(raw.shape, projected.shape)
        self.assertEqual(diagnostics["projected_quantiles"].shape, projected.shape)
        self.assertEqual(diagnostics["raw_quantiles"].shape, raw.shape)
        self.assertEqual(diagnostics["rows_with_crossing_after"], 0)

    def test_weighted_residual_quantile_calibration_and_temperature_intervals(self):
        predictions = np.asarray([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        residual_fit = fit_quantile_residual_calibration(
            predictions, np.asarray([1.0, 10.0]), weights=np.asarray([8.0, 2.0]),
            quantiles=(.1, .5, .9), source_fit_id="fit-v1", calibration_id="q-cal-v2",
        )
        np.testing.assert_allclose(residual_fit.corrections, [1.0, 1.0, 10.0])
        self.assertEqual(residual_fit.from_dict(residual_fit.as_dict()).quantiles, residual_fit.quantiles)
        wide = fit_quantile_residual_calibration(
            np.asarray([[-10.0, 8.0]]), np.asarray([-1.0]),
            quantiles=(.1, .9), source_fit_id="fit-v1", calibration_id="q-wide",
        )
        np.testing.assert_allclose(wide.corrections, [9.0, -9.0])
        projected = predict_quantile_residual(wide, np.zeros((1, 2)))
        np.testing.assert_allclose(projected, [[9.0, 9.0]])
        logits = np.asarray([[1000.0, -1000.0, 0.0], [-1000.0, 1000.0, 0.0]])
        allowed = np.asarray([[True, True, False], [False, True, True]], dtype=bool)
        temperature = fit_temperature(
            logits, allowed, classes=(0, 1, 2), source_fit_id="fit-v1", calibration_id="cal-v2",
            max_iterations=25,
        )
        self.assertEqual(temperature.label_mode, "allowed_class_set")
        self.assertTrue(np.isfinite(temperature.objective))
        self.assertEqual(temperature.from_dict(temperature.as_dict()).calibration_id, "cal-v2")
        np.testing.assert_allclose(predict_temperature(temperature, logits).sum(axis=1), 1.0)

    def test_convergence_requires_declared_softmax_and_quantile_kkt_tolerance(self):
        softmax = fit_softmax(
            np.asarray([[0.0], [1.0], [2.0]]), np.asarray([0, 1, 0]),
            classes=(0, 1), l2=.1, max_iterations=1, tolerance=1e-14,
        )
        if not softmax.converged:
            with self.assertRaises(BackendInputError):
                predict_softmax(softmax, np.asarray([[0.5]]))
        smooth = fit_quantiles(
            np.asarray([[0.0], [1.0], [2.0]]), np.zeros((3, 1)),
            quantiles=(.1, .9), l2=.1, smooth_epsilon=.2,
        )
        self.assertTrue(all(row["kkt_residual"] <= 1e-6 for row in smooth.diagnostics))
        self.assertEqual(smooth.status, "converged")

    def test_temperature_informative_normalization_ignores_all_class_rows(self):
        logits = np.asarray([[4.0, -4.0], [-4.0, 4.0], [100.0, -100.0]])
        informative = np.asarray([[True, False], [False, True], [True, True]], dtype=bool)
        objective, gradient = _temperature_objective_gradient(
            logits, informative, np.ones(3), 0.0, batch_size=2,
        )
        reference_objective, reference_gradient = _temperature_objective_gradient(
            logits[:2], informative[:2], np.ones(2), 0.0, batch_size=2,
        )
        self.assertAlmostEqual(objective, reference_objective, places=12)
        self.assertAlmostEqual(gradient, reference_gradient, places=12)

    def test_empirical_quantile_atoms_and_offset_checksums_are_auditable(self):
        empirical = fit_empirical_quantiles(
            np.asarray([0.0, 0.0, 2.0, 4.0]), quantiles=(.25, .5, .75),
            shrinkage=2.0, group_ids=("a", "a", "b", "b"),
        )
        self.assertEqual(len(empirical.atoms), 2)
        self.assertAlmostEqual(sum(empirical.global_atom_masses), 1.0, places=12)
        self.assertEqual(len(empirical.zero_atom_masses), 2)
        self.assertGreater(empirical.zero_atom_masses[0], 0.0)
        self.assertEqual(empirical.from_dict(empirical.as_dict()).groups, empirical.groups)
        self.assertTrue(np.all(np.diff(np.asarray(empirical.global_values)) >= 0))
        offsets = np.zeros((3, 2))
        fitted = fit_softmax(
            np.asarray([[0.0], [1.0], [2.0]]), np.asarray([0, 1, 0]),
            classes=(0, 1), l2=.1, offset_logits=offsets, offset_identity="base-v2",
        )
        checksum = offset_array_checksum(offsets)
        self.assertEqual(fitted.offset_checksum, checksum)
        predict_softmax(fitted, np.asarray([[0.0], [1.0]]),
                        offset_logits=np.zeros((2, 2)), offset_checksum=offset_array_checksum(np.zeros((2, 2))),
                        offset_identity="base-v2")
        with self.assertRaises(BackendInputError):
            predict_softmax(fitted, np.asarray([[0.0]]), offset_logits=np.zeros((1, 2)), offset_checksum="bad")
        with self.assertRaises(BackendInputError):
            predict_softmax(fitted, np.asarray([[0.0]]), offset_logits=np.zeros((1, 2)),
                            offset_identity="other")

    def test_empirical_quantile_global_weights_are_separate_from_local_group_mass(self):
        values = np.asarray([0.0, 0.0, 10.0, 10.0])
        groups = ("a", "a", "b", "b")
        local = fit_empirical_quantiles(
            values, np.ones(4), quantiles=(.5,), shrinkage=2.0,
            group_ids=groups, global_weights=np.asarray([1.0, 1.0, 3.0, 3.0]),
        )
        self.assertEqual(local.metadata["global_weighting"], "explicit")
        self.assertAlmostEqual(local.metadata["local_weight_sum"], 4.0, places=12)
        self.assertAlmostEqual(local.metadata["global_weight_sum"], 8.0, places=12)
        self.assertGreater(local.global_values[0], 0.0)
        self.assertEqual(local.values[0][0], 0.0)

    def test_hgb_wire_record_verifies_local_payload_contract_without_trigger(self):
        fit = HGBChallenger(
            "regression", "not_run", False, "below_delta",
            {"thread_limit": 1, "loss": "squared_error", "quantile": None},
            0, 1, None, None,
        )
        restored = HGBChallenger.from_dict(fit.as_dict())
        self.assertEqual(restored.status, "not_run")
        self.assertEqual(restored.provider_versions["scikit_learn"], "1.7.2")
        tampered = dict(fit.as_dict())
        tampered["provider_versions"] = {"numpy": "0", "scikit_learn": "1.7.2"}
        with self.assertRaises(BackendInputError):
            HGBChallenger.from_dict(tampered)

    def test_hgb_quantile_configuration_is_explicit_and_classifier_simplex_is_declared(self):
        quantile_fit = fit_hgb_challenger(
            np.zeros((0, 2)), np.zeros(0), task="regression", trigger=False,
            reason="literal quantile challenger", loss="quantile", quantile=.75,
        )
        self.assertEqual(quantile_fit.configuration["loss"], "quantile")
        self.assertEqual(quantile_fit.configuration["quantile"], .75)
        configured = fit_hgb_challenger(
            np.zeros((0, 2)), np.zeros(0), task="regression", trigger=False,
            reason="fixed leaf bound", min_samples_leaf=100,
        )
        self.assertEqual(configured.configuration["min_samples_leaf"], 100)
        with self.assertRaises(BackendInputError):
            fit_hgb_challenger(
                np.zeros((0, 2)), np.zeros(0), task="regression", trigger=False,
                reason="quantile must be explicit", loss="quantile", quantile=None,
            )
        classifier = fit_hgb_challenger(
            np.zeros((2, 1)), np.asarray([0, 0]), task="classification", trigger=False,
            reason="declared simplex", classes=(0, 1),
        )
        self.assertEqual(classifier.classes, (0, 1))
        self.assertEqual(classifier.configuration["loss"], "log_loss")

    def test_nonfinite_and_zero_weight_inputs_fail_closed(self):
        with self.assertRaises(BackendInputError):
            fit_softmax(np.asarray([[np.nan]]), np.asarray([0]), classes=(0, 1), l2=.1)
        with self.assertRaises(BackendInputError):
            fit_quantiles(np.asarray([[1.], [2.]]), np.asarray([[1.], [2.]]),
                          weights=np.asarray([0., 0.]), quantiles=(.5,), l2=.1)
        with self.assertRaises(BackendInputError):
            fit_empirical_quantiles(np.asarray([1., np.inf]), quantiles=(.5,), shrinkage=1.)

    def test_actual_tree_provider_fit_restore_and_unseen_class_probability(self):
        from trading_research.research.jumbo_model_backend import predict_hgb_challenger
        x = np.arange(64, dtype=float).reshape(-1, 1)
        for task in ('classification', 'regression'):
            with self.subTest(task=task):
                options = ({'classes': (0, 1, 2)} if task == 'classification'
                           else {'loss': 'quantile', 'quantile': .75})
                y = (x[:, 0] >= 32).astype(int) if task == 'classification' else x[:, 0]/4
                fit = fit_hgb_challenger(x, y, task=task, trigger=True,
                          reason='actual provider/configuration integration', max_iter=2,
                          min_samples_leaf=2, max_leaf_nodes=4, **options)
                self.assertEqual(fit.status, 'completed_fixed_iter', fit.failure)
                self.assertEqual(fit.iterations, 2)
                prediction = predict_hgb_challenger(fit, x)
                restored = HGBChallenger.from_dict(fit.as_dict())
                np.testing.assert_array_equal(prediction, predict_hgb_challenger(restored, x))
                self.assertTrue(np.isfinite(prediction).all())
                if task == 'classification':
                    self.assertEqual(prediction.shape, (64, 3))
                    self.assertTrue((prediction[:, 2] > 0).all())
                    np.testing.assert_allclose(prediction.sum(axis=1), 1., atol=1e-14)

    def test_serialized_fit_records_are_json_safe(self):
        fit = fit_softmax(np.asarray([[0.], [1.], [2.]]), np.asarray([0, 1, 0]),
                          classes=(0, 1), l2=.1, max_iterations=20)
        json.dumps(fit.as_dict(), sort_keys=True)
        self.assertEqual(fit.from_dict(fit.as_dict()).classes, fit.classes)
        quantile = fit_quantiles(np.asarray([[0.], [1.], [2.]]), np.asarray([[0.], [2.], [1.]]),
                                 quantiles=(.5,), l2=.1, max_iterations=20)
        json.dumps(quantile.as_dict(), sort_keys=True)
        self.assertEqual(quantile.from_dict(quantile.as_dict()).target_count, quantile.target_count)


if __name__ == "__main__":
    unittest.main()
