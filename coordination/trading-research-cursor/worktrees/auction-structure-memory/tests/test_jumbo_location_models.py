"""Literal Location adapter and frozen statistical geometry checks; not executed."""
import unittest
import numpy as np
from tests.test_jumbo_location_tables import extract, M
class LocationModelViewsTests(unittest.TestCase):
    def view(self, result=None):
        from datetime import date
        from trading_research.research.jumbo_matrix import PreparedPaths
        from trading_research.research.jumbo_location_models import prepare_location_chunk
        result = extract() if result is None else result
        plan = dict(location_generators=["raw","mirrored_raw","tick_snapped","mirrored_tick_snapped"],
                    location_horizons_minutes=[15,30,60,180])
        context = PreparedPaths(dict(id="literal-context",feature_columns=["x_width_ticks"],
            feature_groups={g:["width_ticks"] for g in ("controls","own","full")}),
            np.full((4,1),10.),dict(date=np.full(4,date(2020,1,2).toordinal(),dtype=np.int64),
            root=np.zeros(4,dtype=np.int16),clock=np.zeros(4,dtype=np.int16),horizon=np.arange(4),
            origin_ns=np.full(4,5*M,dtype=np.int64),planned_minutes=np.array([15,30,60,180],dtype=np.int64)),
            dict(root=("NQ",),clock=("literal-clock",),horizon=tuple(f"after_{h}m" for h in (15,30,60,180))),())
        return prepare_location_chunk(result,context,plan=plan)

    def test_full_population_features_and_unique_prior_groups(self):
        from trading_research.research.jumbo_targets import group_ids
        from trading_research.research.jumbo_matrix import fit_feature_transform, transformed_features
        matrix, targets = self.view()
        self.assertEqual(matrix.size,416)
        self.assertEqual(len(np.unique(group_ids(matrix))),416)
        self.assertEqual(np.bincount(matrix.fields["generator"]).tolist(),[104]*4)
        self.assertEqual(matrix.fields["planned_minutes"][:4].tolist(),[15,30,60,180])
        transform = fit_feature_transform(matrix,np.ones(416,dtype=bool),group="full")
        self.assertEqual(len(transformed_features(matrix,transform)),416)
        self.assertEqual(targets["reach"].values.shape,(416,2))

    def test_future_changes_cannot_change_features(self):
        original = extract()
        first,_ = self.view(original)
        original["arrays"]["outcome_reach_lower"][:] = 0
        original["arrays"]["outcome_reach_upper"][:] = 1
        original["arrays"]["outcome_up_excursion_upper"][:] = np.nan
        second,_ = self.view(original)
        np.testing.assert_equal(first.features,second.features)

    def test_missing_exact_origin_rejected(self):
        from trading_research.errors import ContractError
        result = extract()
        result["manifest"]["formations"][0]["forecast_origin_ns"] += M
        with self.assertRaises(ContractError):
            self.view(result)

    def test_possible_only_duration_keeps_no_contact(self):
        result = extract()
        a = result["arrays"]
        a["outcome_eligible"][:] = True
        a["outcome_first_possible_minute"][:] = 2
        a["outcome_first_definite_minute"][:] = -1
        a["outcome_latest_first_contact_minute"][:] = 3
        _,targets = self.view(result)
        allowed = targets["first_contact_duration"].values
        self.assertTrue(allowed[:,-1].all())
        self.assertTrue(allowed[:,:-1].any(axis=1).all())

    def test_generator_comparison_uses_identical_ancestry_support(self):
        from trading_research.research.jumbo_location_models import paired_generator_date_losses
        matrix,_ = self.view()
        losses = matrix.fields["generator"].astype(float)
        eligible = np.ones(matrix.size,dtype=bool)
        eligible[0] = False
        output = paired_generator_date_losses(matrix,losses,eligible,scorer_id="frozen-literal")
        self.assertEqual(output["intended_pairs"],104)
        self.assertEqual(output["paired_pairs"],103)
        self.assertEqual(output["unpaired_pairs"],1)
        self.assertEqual(output["dates"][0]["mean_losses"],[0.,1.,2.,3.])

class StatisticalLocationTests(unittest.TestCase):
    def provider(self, **changes):
        from trading_research.research.jumbo_targets import boundary_ns
        cut = boundary_ns("2025-01-02")
        result = dict(original_fit_id="fit-original",model_id="frozen-model",source_analysis_id="source-original",
            prediction_id="prediction-one",forecast_origin_ns=cut,available_at_ns=cut,
            fit_labels_before_ns=boundary_ns("2023-01-01"),historical_training_calibration_closure_ns=boundary_ns("2024-07-01"),actual_artifact_created_at_ns=boundary_ns("2026-09-07"),retrospective_reconstruction=True,creation_period="heldout",
            high=dict(target="future_high_from_known_W",model_id="high-model",quantiles=[.25,.5,.75,.95],values=[.1,.2,.3,.4]),
            low=dict(target="future_low_from_known_W",model_id="low-model",quantiles=[.25,.5,.75,.95],values=[.1,.2,.3,.4]))
        result.update(changes)
        return result

    def definitions(self, provider=None, **changes):
        from trading_research.research.jumbo_location_models import statistical_location_definitions
        from trading_research.research.jumbo_targets import boundary_ns
        args = dict(anchor_ticks=100,width_ticks=10,origin_ns=boundary_ns("2025-01-02"),provider=provider)
        args.update(changes)
        return statistical_location_definitions(**args)

    def test_twelve_slots_unavailable_without_independent_predictions(self):
        rows = self.definitions()
        self.assertEqual(len(rows),12)
        self.assertTrue(all(row["lower"] is None and row["upper"] is None for row in rows))
        self.assertTrue(all(row["unavailable_reason"]=="independent_frozen_prediction_unavailable" for row in rows))

    def test_explicit_grid_and_ieee_provenance(self):
        from fractions import Fraction
        rows = self.definitions(self.provider())
        band = rows[2]
        self.assertEqual((band["lower"],band["upper"]),(Fraction(99),Fraction(101)))
        self.assertEqual(band["high_coordinate"]["prediction_ieee754_hex"],"3fb999999999999a")
        meta = band["high_coordinate"]
        self.assertLessEqual(abs(Fraction(int(meta["grid_error_numerator"]),int(meta["grid_error_denominator"]))),Fraction(1,2048))
        self.assertEqual(band["provenance"]["original_fit_id"],"fit-original")

    def test_ties_even_and_signed_inverted_band_not_sorted(self):
        from fractions import Fraction
        provider = self.provider()
        provider["high"]["values"] = [1/2048,3/2048,-.3,-.4]
        provider["low"]["values"] = [0.,0.,-.3,-.4]
        rows = self.definitions(provider,width_ticks=1)
        self.assertEqual(rows[1]["lower"],Fraction(100))
        self.assertEqual(rows[4]["lower"],Fraction(100)+Fraction(2,1024))
        self.assertTrue(rows[8]["inverted_band"])
        self.assertIsNone(rows[8]["lower"])
        self.assertEqual(rows[8]["unavailable_reason"],"inverted_predicted_band")
        self.assertIsNotNone(rows[6]["lower"])
        self.assertIsNotNone(rows[7]["lower"])

    def test_future_or_training_period_provider_rejected(self):
        from trading_research.errors import ContractError
        from trading_research.research.jumbo_targets import boundary_ns
        for provider in (self.provider(available_at_ns=boundary_ns("2025-01-03")),
                         self.provider(creation_period="fit"),
                         self.provider(fit_labels_before_ns=boundary_ns("2024-01-01")),
                         self.provider(forecast_origin_ns=boundary_ns("2025-01-03"))):
            with self.assertRaises(ContractError):
                self.definitions(provider)

    def test_unrepresentable_grid_preserves_unavailable_slots(self):
        provider = self.provider()
        provider["high"]["values"] = [1e300]*4
        rows = self.definitions(provider)
        self.assertEqual(rows[1]["unavailable_reason"],"grid_coordinate_exceeds_int64")
        self.assertFalse(rows[1]["high_coordinate"]["storage_representable"])
        self.assertEqual(len(rows),12)

    def test_actual_creation_later_is_explicit_reconstruction_not_backdated(self):
        from trading_research.research.jumbo_targets import boundary_ns
        rows = self.definitions(self.provider())
        provenance = rows[0]["provenance"]
        self.assertTrue(provenance["retrospective_reconstruction"])
        self.assertGreater(provenance["actual_artifact_created_at_ns"],provenance["forecast_origin_ns"])
        self.assertEqual(provenance["historical_training_calibration_closure_ns"],boundary_ns("2024-07-01"))

    def test_future_calibration_or_same_selection_period_closure_rejected(self):
        from trading_research.errors import ContractError
        from trading_research.research.jumbo_targets import boundary_ns
        for closure in ("2024-12-31","2025-01-03"):
            with self.assertRaises(ContractError):
                self.definitions(self.provider(historical_training_calibration_closure_ns=boundary_ns(closure)))
        with self.assertRaises(ContractError):
            self.definitions(self.provider(retrospective_reconstruction=False))

    def test_target_semantic_binding_survives_different_matrix_artifact(self):
        from trading_research.research.jumbo_models import _target_binding
        from trading_research.research.jumbo_targets import Target
        first = Target("reach","interval_categorical",np.array([[True,False]]),np.array([True]),np.array([1],dtype=np.int64),
                       dict(id="development-artifact",source_matrix="development",classes=[0,1],definition="fixed geometry"))
        second = Target("reach","interval_categorical",np.array([[False,True]]),np.array([True]),np.array([2],dtype=np.int64),
                        dict(id="heldout-artifact",source_matrix="heldout",classes=[0,1],definition="fixed geometry"))
        self.assertEqual(_target_binding(first,0),_target_binding(second,0))
