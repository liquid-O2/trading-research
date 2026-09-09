from copy import deepcopy
import json
import unittest

import numpy as np

from trading_research.errors import IntegrityError
from trading_research.research.jumbo_evaluation_storage import (
    pack_grouped_evaluation, expand_grouped_evaluation, verify_packed_evaluation, normalized_json_bytes)
from trading_research.operations.artifacts import canonical_json
from trading_research.research.jumbo_model_evaluation import grouped_date_evaluation
from trading_research.research.jumbo_models import json_safe


class EvaluationStorageTests(unittest.TestCase):
    def result(self, bounded=False):
        dates = np.asarray([1, 1, 2, 4, 5, 6, 7, 8, 9, 10], dtype=np.int64)
        groups = np.asarray([1] * len(dates), dtype=np.int64)
        probabilities = np.asarray([[.8, .2], [.4, .6], [.0, 1.], [.7, .3], [.5, .5],
                                    [.8, .2], [.4, .6], [.0, 1.], [.7, .3], [.5, .5]])
        observed = np.asarray([[1., 0.], [0., 1.]] * 5)
        options = {'lower_matrix': np.zeros_like(observed), 'upper_matrix': observed} if bounded else {
            'observed_binary_matrix': observed}
        return grouped_date_evaluation({'loss': np.asarray([0., 2., 1., np.nan, 0., 1., 2., 3., 1., 0.])},
            dates, groups, {1: np.arange(1, 13, dtype=np.int64), 2: np.arange(1, 13, dtype=np.int64)},
            probability_matrix=probabilities, paired_candidate=np.arange(len(dates), dtype=float),
            paired_baseline=np.arange(len(dates), dtype=float) + 1, replicates=200,
            minimum_dates=5, minimum_events=2, **options)

    def test_all_point_metrics_calibration_empty_groups_and_uncertainty_roundtrip_exactly(self):
        original = self.result()
        before = json_safe(original, omit_date_vectors=True)
        packed = pack_grouped_evaluation(original)
        decoded = json.loads(json.dumps(packed, allow_nan=False))
        restored = expand_grouped_evaluation(decoded)
        self.assertEqual(restored, before)
        self.assertEqual(json_safe(original, omit_date_vectors=True), before)
        self.assertIs(restored['groups']['1']['calibration'], restored['groups']['1']['calibration_by_class'])
        check = verify_packed_evaluation(original, decoded)
        self.assertTrue(check['passed'])
        self.assertGreater(check['missing_numbers_retained_as_null'], 0)
        self.assertLess(len(json.dumps(packed)), len(json.dumps(before)))
        self.assertEqual(normalized_json_bytes(packed), canonical_json(packed))

    def test_interval_endpoint_calibration_remains_bounded_and_does_not_become_fractional_truth(self):
        original = self.result(bounded=True)
        packed = pack_grouped_evaluation(original)
        self.assertEqual(expand_grouped_evaluation(packed), json_safe(original, omit_date_vectors=True))
        self.assertTrue(verify_packed_evaluation(original, packed)['passed'])

    def test_cached_bin_membership_matches_original_scorer_for_point_and_interval_labels(self):
        from references.jumbo_evaluation_check11.evaluation import grouped_date_evaluation as reference
        dates = np.asarray([1, 1, 2, 4, 5, 8, 10, 10], dtype=np.int64)
        groups = np.asarray([1, 2, 1, 2, 1, 2, 1, 2], dtype=np.int64)
        p = np.asarray([[.0, 1.], [.1, .9], [.2, .8], [.3, .7], [.5, .5], [.6, .4], [.9, .1], [1., .0]])
        y = np.asarray([[1., 0.], [0., 1.]] * 4)
        for bounded in (False, True):
            options = {'lower_matrix': np.zeros_like(y), 'upper_matrix': y} if bounded else {'observed_binary_matrix': y}
            args = ({'loss': np.asarray([1., 2., np.nan, 4., 2., 1., 1., 0.])}, dates, groups,
                    {1: np.arange(1, 13, dtype=np.int64), 2: np.arange(1, 13, dtype=np.int64), 3: np.arange(1, 13, dtype=np.int64)})
            expected = reference(*args, probability_matrix=p, replicates=200, **options)
            actual = grouped_date_evaluation(*args, probability_matrix=p, replicates=200, **options)
            self.assertTrue(verify_packed_evaluation(expected, pack_grouped_evaluation(actual))['passed'])

    def test_one_group_can_be_read_without_expanding_other_groups(self):
        packed = pack_grouped_evaluation(self.result())
        result = expand_grouped_evaluation(packed, group_ids=(2,))
        self.assertEqual(set(result['groups']), {'2'})
        self.assertEqual(result['group_count'], 2)
        self.assertEqual(result['groups']['2']['actual_row_count'], 0)
        with self.assertRaises(IntegrityError):
            expand_grouped_evaluation(packed, group_ids=(99,))

    def test_multiple_events_per_date_keep_the_original_ordered_mean_at_exact_precision(self):
        from references.jumbo_evaluation_check11.evaluation import grouped_date_evaluation as reference
        # Many same-bin events/date exercise ordered means rather than the
        # one-observation-per-clock/date fast path of the actual Jumbo cohort.
        values = np.asarray([.21, .24, .22, .23, .27, .28, .26, .29, .25, .21] * 8)
        probabilities = np.column_stack((values, 1-values))
        dates = np.repeat(np.arange(1, 9, dtype=np.int64), 10)
        groups = np.ones(len(dates), dtype=np.int64)
        outcomes = np.column_stack((np.arange(len(dates)) % 2, 1-np.arange(len(dates)) % 2)).astype(float)
        args = ({'loss': values.copy()}, dates, groups, {1: np.arange(1, 11, dtype=np.int64)})
        kwargs = dict(probability_matrix=probabilities, observed_binary_matrix=outcomes, replicates=200)
        original = reference(*args, **kwargs)
        actual = grouped_date_evaluation(*args, **kwargs)
        self.assertTrue(verify_packed_evaluation(original, pack_grouped_evaluation(actual))['passed'])

    def test_unknown_fields_broken_references_and_changed_values_fail_visibly(self):
        original = self.result()
        changed = deepcopy(original)
        changed['groups']['1']['metrics']['loss']['bootstrap']['new_diagnostic'] = 1
        with self.assertRaises(IntegrityError):
            pack_grouped_evaluation(changed)
        packed = pack_grouped_evaluation(original)
        broken = deepcopy(packed)
        broken['groups']['1']['metrics']['loss']['statistic'] = len(broken['statistics_rows'])
        with self.assertRaises(IntegrityError):
            expand_grouped_evaluation(broken)
        row = packed['groups']['1']['metrics']['loss']['statistic']
        packed['statistics_rows'][row][0] += 1
        with self.assertRaises(IntegrityError):
            verify_packed_evaluation(original, packed)

    def test_signed_zero_and_literal_scalar_types_are_not_merged(self):
        original = self.result()
        metric = original['groups']['1']['metrics']['loss']
        metric['estimate'] = 0.0
        other = deepcopy(metric)
        other['estimate'] = -0.0
        original['groups']['1']['metrics']['negative_zero'] = other
        packed = pack_grouped_evaluation(original)
        self.assertNotEqual(packed['groups']['1']['metrics']['loss']['statistic'],
                            packed['groups']['1']['metrics']['negative_zero']['statistic'])
        self.assertTrue(verify_packed_evaluation(original, packed)['passed'])
