"""Independent literal compatible-set baseline tests; no candidate execution here."""
import copy
import unittest
import numpy as np
from trading_research.errors import ContractError
from trading_research.research.jumbo_baselines import (
    _allowed, _em, fit_grouped_distribution, predict_grouped_distribution,
)


def fit(values, groups, dates, *, classes=2, group_count=2, **kwargs):
    return fit_grouped_distribution(np.asarray(values),np.asarray(groups,dtype=np.int64),
       np.asarray(dates,dtype=np.int64),classes=classes,group_count=group_count,**kwargs)


class JumboBaselineTests(unittest.TestCase):
    def test_integer_frequencies_plus_prior_date_mass(self):
        record=fit([0,0,1],[0,0,0],[1,2,3],shrinkage=2.)
        # Pooled: (2+.5,1+.5)/(3+1). Group: (2,1)+2*(.625,.375), /5.
        np.testing.assert_allclose(record["global_probabilities"],[.625,.375],atol=1e-12,rtol=0)
        np.testing.assert_allclose(record["probabilities"],[[.65,.35],[.625,.375]],atol=1e-12,rtol=0)
        self.assertTrue(record["converged"])
        self.assertEqual(record["group_diagnostics"]["group_information_weight"],[3.,0.])
        self.assertEqual(record["shrinkage_date_mass"],2.)

    def test_literal_interval_responsibility_update(self):
        allowed=np.array([[True,True,False]])
        prior=np.array([.2,.3,.5])
        p,diag=_em(allowed,np.array([0],dtype=np.int64),np.array([1.]),prior,2.,prior[None,:],1,1e-12)
        # Conditional compatible posterior (.4,.6,0), plus prior pseudo-counts (.4,.6,1).
        expected=np.array([[4/15,2/5,1/3]])
        np.testing.assert_allclose(p,expected,atol=1e-12,rtol=0)
        objective=np.log(2/3)+2*np.sum(prior*np.log(expected[0]))
        self.assertAlmostEqual(diag["penalized_log_likelihood"],objective,places=12)
        self.assertFalse(diag["converged"])

    def test_all_class_rows_supply_no_em_counts(self):
        allowed=np.array([[True,False],[True,True]])
        p,diag=_em(allowed,np.array([0,0],dtype=np.int64),np.array([1.,100.]),
                  np.array([.25,.75]),2.,np.array([[.25,.75]]),20,1e-12)
        np.testing.assert_allclose(p,[[.5,.5]],atol=1e-12,rtol=0)
        self.assertEqual(diag["informative_rows"],1)
        self.assertEqual(diag["all_class_rows"],1)
        self.assertEqual(diag["group_information_weight"],[1.])

    def test_pooled_equal_dates_differs_from_pooled_row_frequency(self):
        record=fit([0,0,1],[0,1,0],[1,1,2],shrinkage=2.)
        np.testing.assert_allclose(record["global_probabilities"],[.5,.5],atol=1e-12,rtol=0)
        np.testing.assert_allclose(record["probabilities"],[[.5,.5],[2/3,1/3]],atol=1e-12,rtol=0)
        self.assertEqual(record["training_date_count"],2)
        self.assertEqual(record["group_diagnostics"]["group_information_weight"],[2.,1.])
        self.assertEqual(record["global_diagnostics"]["group_information_weight"],[2.])

    def test_adding_all_class_row_does_not_attenuate_other_date_information(self):
        original=fit(np.array([[True,False],[True,False],[False,True]]),[0,1,0],[1,1,2],group_count=3,shrinkage=2.)
        augmented=fit(np.array([[True,False],[True,False],[False,True],[True,True]]),[0,1,0,2],[1,1,2,2],group_count=3,shrinkage=2.)
        np.testing.assert_allclose(original["global_probabilities"],augmented["global_probabilities"],atol=1e-12,rtol=0)
        np.testing.assert_allclose(original["probabilities"],augmented["probabilities"],atol=1e-12,rtol=0)
        self.assertEqual(augmented["global_diagnostics"]["all_class_rows"],1)

    def test_empty_and_all_class_populations_return_uniform(self):
        for values,groups,dates in ((np.empty(0,dtype=np.int64),[],[]),
                                   (np.ones((2,3),dtype=bool),[0,1],[1,1])):
            record=fit(values,groups,dates,classes=3,group_count=2)
            self.assertTrue(record["converged"])
            np.testing.assert_allclose(record["probabilities"],np.full((2,3),1/3),atol=1e-12,rtol=0)
            self.assertEqual(record["global_diagnostics"]["informative_rows"],0)
            self.assertEqual(record["group_diagnostics"]["iterations"],0)

    def test_separate_groups_do_not_pool_raw_counts(self):
        record=fit([0,0,1,1],[0,0,1,1],[1,2,1,2],shrinkage=2.)
        np.testing.assert_allclose(record["global_probabilities"],[.5,.5],atol=1e-12,rtol=0)
        np.testing.assert_allclose(record["probabilities"],[[.75,.25],[.25,.75]],atol=1e-12,rtol=0)
        np.testing.assert_allclose(predict_grouped_distribution(record,np.array([1,0],dtype=np.int64)),[[.25,.75],[.75,.25]])

    def test_all_six_paths_and_seven_duration_classes_supported(self):
        for classes in (6,7):
            record=fit(list(range(classes)),[0]*classes,list(range(1,classes+1)),classes=classes,group_count=1)
            self.assertTrue(record["converged"])
            np.testing.assert_allclose(record["probabilities"],[np.full(classes,1/classes)],atol=1e-12,rtol=0)
        # Ambiguous reclaim row remains a two-class observation, not a third category.
        record=fit(np.array([[True,False],[False,True],[True,True]]),[0,0,0],[1,2,3],group_count=1)
        np.testing.assert_allclose(record["probabilities"],[[.5,.5]],atol=1e-12,rtol=0)

    def test_duplicate_group_date_rejected_but_same_date_different_group_allowed(self):
        with self.assertRaises(ContractError):fit([0,1],[0,0],[1,1])
        self.assertTrue(fit([0,1],[0,1],[1,1])["converged"])

    def test_exact_group_date_identities_and_valid_domains(self):
        for groups,dates in ((np.array([-1],dtype=np.int64),np.array([1],dtype=np.int64)),
                            (np.array([2],dtype=np.int64),np.array([1],dtype=np.int64)),
                            (np.array([0.]),np.array([1],dtype=np.int64)),
                            (np.array([0],dtype=np.int64),np.array([1.])),
                            (np.array([0],dtype=np.int64),np.array([-1],dtype=np.int64)),
                            (np.array([0],dtype=np.int64),np.array([0],dtype=np.int64))):
            with self.subTest(groups=groups,dates=dates),self.assertRaises(ContractError):
                fit_grouped_distribution(np.array([0]),groups,dates,classes=2,group_count=2)

    def test_invalid_classes_and_empty_compatible_sets_rejected(self):
        for values in (np.array([-1]),np.array([2]),np.array([0.]),np.array([[False,False]]),np.array([[True,False,True]])):
            with self.subTest(values=values),self.assertRaises(ContractError):
                fit(values,[0],[1])

    def test_nonconvergence_requires_explicit_uniform_fallback(self):
        record=fit([0,0,0],[0,0,0],[1,2,3],max_iterations=1,tolerance=1e-15)
        self.assertFalse(record["converged"])
        groups=np.array([0,1],dtype=np.int64)
        with self.assertRaises(ContractError):predict_grouped_distribution(record,groups)
        fallback=predict_grouped_distribution(record,groups,allow_declared_fallback=True)
        np.testing.assert_allclose(fallback,np.full((2,2),.5),atol=0,rtol=0)
        self.assertNotEqual(record["probabilities"][0],[.5,.5])

    def test_prediction_checks_stored_simplex_and_groups(self):
        record=fit([0,1],[0,0],[1,2])
        for p in ([[1.,0.],[.5,.5]],[[.6,.6],[.5,.5]],[[np.nan,.5],[.5,.5]],[[.5,.5]]):
            broken=copy.deepcopy(record);broken["probabilities"]=p
            with self.assertRaises(ContractError):predict_grouped_distribution(broken,np.array([0],dtype=np.int64))
        for g in (np.array([-1],dtype=np.int64),np.array([2],dtype=np.int64),np.array([0.])):
            with self.assertRaises(ContractError):predict_grouped_distribution(record,g)

    def test_map_prior_concentration_does_not_change_with_row_order(self):
        a=fit([0,1,0],[0,0,1],[1,2,1],shrinkage=3.5)
        b=fit([0,0,1],[1,0,0],[1,1,2],shrinkage=3.5)
        np.testing.assert_allclose(a["probabilities"],b["probabilities"],atol=1e-12,rtol=0)
        self.assertEqual(a["shrinkage_date_mass"],3.5)
        self.assertNotIn("twenty",a["weighting"].lower())
        self.assertIn("alpha_k=1+shrinkage_date_mass*pooled_p_k",a["weighting"])

if __name__ == "__main__":
    unittest.main()
