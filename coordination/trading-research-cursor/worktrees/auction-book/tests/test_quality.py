from dataclasses import replace
import math
from pathlib import Path
import random
import tempfile
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.provenance import InputValue
from trading_research.research.calibration import fit_sigmoid_calibration
from trading_research.research.diagnostics import chronological_training_subsets,compatible_block_permutation,interaction_effect
from trading_research.research.folds import Sample,chronological_fold,validate_oof
from trading_research.research.models import BinaryExample,fit_frequency,fit_logistic,sigmoid
from trading_research.research.protocols import Candidate,EvaluationRegistry,Protocol,QualityEvidence,predictive_disposition,scorecard,validate_comparison,QUALITY_DIMENSIONS
from trading_research.research.scoring import IntervalSpec,Metric,ScoreRow,block_interval,paired_scores,reliability


def interval():return IntervalSpec(.95,400,77,2,6)


def candidate(id,information=('x',),**kwargs):
    return Candidate(id,information,kwargs.get('representation','numeric-v1'),kwargs.get('learner','logistic-v1'),'generator-v1','policy-v1',3,30)


def protocol(id='p1',**kwargs):
    return Protocol(id,'same-selection-chain',('V07',),'binary-v1','known synthetic direction','model',
                    (candidate('base',learner='frequency-v1'),candidate('model')),Metric('brier'),interval(),.02,.01,1.,
                    tuple(f'd{i:02}' for i in range(40)),'samples-v1',kwargs.get('role','retrospective_evaluation'),100,200,kwargs.get('registered_at',300),'Synthetic controlled evidence only')


def examples(days=150,per_day=4):
    rng=random.Random(82);result=[]
    for d in range(days):
        for k in range(per_day):
            at=d*100+k*10+1;x=rng.uniform(-2,2);y=int(rng.random()<sigmoid(3*x))
            sample=Sample(f'd{d:03}:{k}',f'd{d:03}',at,at+3,at+2,'binary-v1')
            result.append(BinaryExample(sample,(InputValue('x',digest([d,k,x]),at,canonical_json(x)),),y))
    return tuple(result)


class ProperScoreTests(unittest.TestCase):
    def test_hand_calculated_losses_probability_simplex_and_floors(self):
        self.assertAlmostEqual(Metric('brier').loss(1,.75),.0625)
        self.assertAlmostEqual(Metric('log_loss').loss(0,.75),-math.log(.25))
        self.assertAlmostEqual(Metric('multiclass_log_loss').loss(2,(.2,.3,.5)),math.log(2))
        self.assertAlmostEqual(Metric('pinball',quantile=.9).loss(5,3),1.8)
        self.assertAlmostEqual(Metric('pinball',quantile=.9).loss(2,3),.1)
        self.assertAlmostEqual(Metric('qlike').loss(0,2),math.log(2))
        for metric,y,p in ((Metric('brier'),.5,.5),(Metric('brier'),1,1.1),(Metric('qlike'),2,0),(Metric('multiclass_log_loss'),0,(.5,.6))):
            with self.assertRaises(ContractError):metric.loss(y,p)

    def test_sorted_crps_matches_independent_pairwise_identity(self):
        xs=(-3.,1.,2.,2.,7.);y=3.
        literal=sum(abs(x-y) for x in xs)/len(xs)-sum(abs(x-z) for x in xs for z in xs)/(2*len(xs)**2)
        self.assertAlmostEqual(Metric('crps').loss(y,xs),literal)
        self.assertEqual(Metric('crps').loss(5,(2.,)),3)

    def test_paired_targets_population_and_unobserved_states_cannot_change(self):
        a=tuple(ScoreRow(str(i),f'd{i:02}','same-target','labels',i%2,.5) for i in range(40))
        b=tuple(replace(r,prediction=.8 if r.outcome else .2) for r in a);dates=tuple(r.date_group for r in a)
        result=paired_scores(a,b,Metric('brier'),interval(),ordered_dates=dates)
        self.assertAlmostEqual(result['improvement']['estimate'],.21)
        self.assertAlmostEqual(result['improvement']['lower'],.21)
        for changed in (b[:-1],(replace(b[0],target_signature='new-width'),)+b[1:],(replace(b[0],label_version='revised'),)+b[1:]):
            with self.assertRaises(ContractError):paired_scores(a,changed,Metric('brier'),interval(),ordered_dates=dates)
        missing=(replace(b[0],prediction=None),)+b[1:]
        result=paired_scores(a,missing,Metric('brier'),interval(),ordered_dates=dates)
        self.assertEqual((result['missing_forecast_count'],result['paired_coverage']),(1,39/40))
        self.assertEqual(predictive_disposition(result,protocol(),critical_invariants={'causal':True})['status'],'inconclusive')
        with self.assertRaises(ContractError):ScoreRow('x','d','t','l',0,None,'censored')

    def test_many_correlated_touches_do_not_manufacture_independent_dates(self):
        r=block_interval({'day':tuple(.2 for _ in range(10000))},interval(),ordered_dates=('day',))
        self.assertEqual(r['support'],'insufficient');self.assertIsNone(r['lower'])
        grouped={'a':(0.,)*1000,'b':(1.,)}
        equal_date=block_interval(grouped,interval(),ordered_dates=('a','b'))
        equal_sample=block_interval(grouped,replace(interval(),weighting='equal_sample'),ordered_dates=('a','b'))
        self.assertEqual(equal_date['estimate'],.5);self.assertAlmostEqual(equal_sample['estimate'],1/1001)

    def test_fixed_reliability_bins_keep_empty_bins_and_probability_one(self):
        rows=(ScoreRow('a','d1','t','l',0,0.),ScoreRow('b','d2','t','l',1,1.))
        r=reliability(rows,edges=(0.,.25,.5,.75,1.))
        self.assertEqual([c['count'] for c in r],[1,0,0,1]);self.assertIsNone(r[1]['mean_probability'])


class FrozenProtocolTests(unittest.TestCase):
    def test_information_model_and_generator_axes_and_exact_factorial_are_separate(self):
        validate_comparison('information',(candidate('a',()),candidate('b')))
        with self.assertRaises(ContractError):validate_comparison('information',(candidate('a',()),candidate('b',learner='larger-search')))
        factorial=(candidate('none',()),candidate('A',('a',)),candidate('B',('b',)),candidate('AB',('a','b')))
        validate_comparison('interaction',factorial)
        dates=tuple(f'd{i}' for i in range(40));losses={c.id:{d:(.25 if c.id!='AB' else .05,) for d in dates} for c in factorial}
        result=interaction_effect(factorial,losses,interval=interval(),ordered_dates=dates)
        self.assertAlmostEqual(result['synergy_gain']['estimate'],.2)
        with self.assertRaises(ContractError):validate_comparison('interaction',factorial[:-1]+(candidate('AB',('a',)),))

    def test_renamed_evaluation_cannot_reuse_outcomes_and_restart_cannot_change_models(self):
        with tempfile.TemporaryDirectory() as root:
            registry=EvaluationRegistry(Path(root)/'eval.sqlite');p=protocol();registry.register(p)
            models={'base':'bhash','model':'mhash'};first=registry.begin(p,model_artifacts=models,started_at=400)
            registry=EvaluationRegistry(Path(root)/'eval.sqlite')
            self.assertEqual(registry.begin(p,model_artifacts=models,started_at=400),first)
            with self.assertRaises(IntegrityError):registry.begin(p,model_artifacts={**models,'model':'retuned'},started_at=400)
            renamed=replace(p,id='another-name');registry.register(renamed)
            with self.assertRaises(ContractError):registry.begin(renamed,model_artifacts=models,started_at=401)
            with self.assertRaises(IntegrityError):registry.register(replace(p,minimum_useful_gain=0.))

    def test_future_freeze_and_fixed_endpoint_cannot_be_moved_to_favorable_peak(self):
        p=protocol(role='future_confirmation',registered_at=50)
        with self.assertRaises(ContractError):replace(p,registered_at=101)
        with tempfile.TemporaryDirectory() as root:
            registry=EvaluationRegistry(Path(root)/'e.sqlite');registry.register(p)
            with self.assertRaises(ContractError):registry.begin(p,model_artifacts={'base':'b','model':'m'},started_at=110)
            registry.begin(p,model_artifacts={'base':'b','model':'m'},started_at=90)
            report={'protocol_version':p.version,'sample_manifest_hash':p.sample_manifest_hash,'mean':1000}
            with self.assertRaises(ContractError):registry.finish(p,report=report,finished_at=150)
            registry.finish(p,report=report,finished_at=201)
            with self.assertRaises(IntegrityError):registry.finish(p,report={**report,'mean':3000},finished_at=201)

    def test_quality_tracks_do_not_promote_good_prediction_over_integrity_or_negative_policy(self):
        evidence=tuple(QualityEvidence(d,'supported',('actual-artifact',),'executed fixture') for d in QUALITY_DIMENSIONS)
        card=scorecard(unit_id='fixture',role='predictor',evidence=evidence,selected_version='v',objective_mean_per_day=100)
        self.assertEqual(card['objective_gap'],1900)
        bad=tuple(replace(e,status='not_met') if e.dimension=='decisions' else e for e in evidence)
        with self.assertRaises(ContractError):scorecard(unit_id='fixture',role='predictor',evidence=bad,selected_version='v',objective_mean_per_day=-10)
        measurement=tuple(QualityEvidence(d,'supported' if d in ('semantics','causality') else 'not_applicable',('fixture',) if d in ('semantics','causality') else (), 'Exact arithmetic invariant has no standalone alpha role') for d in QUALITY_DIMENSIONS)
        self.assertEqual(scorecard(unit_id='arithmetic',role='measurement',evidence=measurement,selected_version='v',objective_mean_per_day=None)['role'],'measurement')


class LearnerControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=examples();cls.fold=chronological_fold((e.sample for e in cls.rows),id='base',fit_at=6000,evaluation_start=6001,evaluation_end=16000)
        cls.model=fit_logistic(cls.rows,cls.fold,('x',),l2_strength=.1)

    def test_planted_direction_recovers_with_oof_scaling_lineage_and_held_out_gain(self):
        self.assertGreater(self.model.coefficients[0],.5);self.assertLess(self.model.maximum_gradient,1e-8)
        eval_rows=[e for e in self.rows if e.sample.id in self.fold.evaluation_ids];a=[];b=[]
        for e in eval_rows:
            p,manifest=self.model.predict(e)
            self.assertEqual(len(manifest['fit_closure']),2)
            a.append(ScoreRow(e.sample.id,e.sample.date_group,'t','l',e.outcome,.5));b.append(replace(a[-1],prediction=p))
        result=paired_scores(a,b,Metric('brier'),interval(),ordered_dates=tuple(dict.fromkeys(e.sample.date_group for e in eval_rows)))
        self.assertGreater(result['improvement']['lower'],.05)
        with self.assertRaises(ContractError):self.model.predict(self.rows[0])

    def test_future_suffix_and_eval_outcomes_cannot_change_fitted_scaler_or_weights(self):
        changed=tuple(replace(e,outcome=1-e.outcome,values=(InputValue('x','future-mutated',e.sample.decision_at,canonical_json(1000000.)),)) if e.sample.id in self.fold.evaluation_ids else e for e in self.rows)
        model=fit_logistic(changed,self.fold,('x',),l2_strength=.1)
        self.assertEqual(self.model,model)
        training=[e for e in self.rows if e.sample.id in self.fold.training_ids]
        expected=sum(json_value(e.values[0]) for e in training)/len(training)
        self.assertAlmostEqual(self.model.means[0],expected)

    def test_future_only_planted_feature_is_rejected_before_fit(self):
        changed=(replace(self.rows[0],values=(replace(self.rows[0].values[0],known_at=999999),)),)+self.rows[1:]
        with self.assertRaises(ContractError):fit_logistic(changed,self.fold,('x',),l2_strength=.1)
        with self.assertRaises(ContractError):fit_logistic(self.rows,self.fold,('undeclared-future',),l2_strength=.1)

    def test_conditional_frequency_beta_prior_empty_cell_and_constant_column(self):
        model=fit_frequency(self.rows,self.fold,('x',),cuts=((-10.,0.,10.),))
        empty=replace(self.rows[-1],values=(InputValue('x','new',self.rows[-1].sample.decision_at,b'50'),))
        p,manifest=model.predict(empty);self.assertEqual(p,model.overall);self.assertEqual(manifest['cell_support'],0)
        for key,successes,n in model.cells:
            e=next(e for e in self.rows if e.sample.id in self.fold.evaluation_ids and tuple(sum(json_value(e.values[0])>=c for c in edges) for edges in model.cuts)==key)
            p,_=model.predict(e);self.assertEqual(p,(successes+1)/(n+2))

    def test_calibration_uses_only_distinct_mature_dates_and_complete_transitive_folds(self):
        cal_fold=chronological_fold((e.sample for e in self.rows),id='calibrate',fit_at=10000,evaluation_start=10001,evaluation_end=16000,training_start=7000)
        calibrated=fit_sigmoid_calibration(self.model,self.rows,cal_fold,l2_strength=.01)
        p,manifest=calibrated.predict(self.rows[-1]);self.assertTrue(0<p<1);self.assertEqual(len(manifest['fit_closure']),5)
        self.assertTrue(all(g>='d070' and g<'d100' for g in calibrated.artifact.training_groups))
        with self.assertRaises(ContractError):calibrated.predict(self.rows[72*4])
        with self.assertRaises(ContractError):validate_oof(self.rows[-1].sample,calibrated.id,calibrated.fit_artifacts,fold_version=calibrated.artifact.fold_version)
        bad_fold=chronological_fold((e.sample for e in self.rows),id='leaked-cal',fit_at=10000,evaluation_start=10001,evaluation_end=16000)
        with self.assertRaises(ContractError):fit_sigmoid_calibration(self.model,self.rows,bad_fold,l2_strength=.01)

    def test_learning_curve_and_null_shuffle_preserve_whole_compatible_dates(self):
        ids={f'd{i}':(f'a{i}',f'b{i}') for i in range(20)};dates=tuple(ids)
        curve=chronological_training_subsets(ids,ordered_dates=dates,fractions=(.25,.5,1.))
        self.assertEqual([len(c['training_ids']) for c in curve],[10,20,40]);self.assertEqual(curve[0]['dates'],dates[:5])
        blocks={f'd{i}':(i,i+100) for i in range(20)};classes={d:'am' if i<10 else 'pm' for i,d in enumerate(blocks)}
        shuffled,mapping=compatible_block_permutation(blocks,classes,seed=4)
        self.assertEqual(sorted(shuffled.values()),sorted(blocks.values()))
        self.assertTrue(all(classes[d]==classes[mapping[d]] for d in blocks))
        self.assertTrue(all(v[1]-v[0]==100 for v in shuffled.values()))

    def test_shuffled_training_date_labels_do_not_recover_the_planted_market_direction(self):
        train=[e for e in self.rows if e.sample.id in self.fold.training_ids]
        by={d:tuple(e.outcome for e in train if e.sample.date_group==d) for d in dict.fromkeys(e.sample.date_group for e in train)}
        shuffled,mapping=compatible_block_permutation(by,{d:'same-four-observation-synthetic-date' for d in by},seed=123)
        replacements={e.sample.id:shuffled[e.sample.date_group][int(e.sample.id.split(':')[1])] for e in train}
        null=tuple(replace(e,outcome=replacements[e.sample.id]) if e.sample.id in replacements else e for e in self.rows)
        fitted=fit_logistic(null,self.fold,('x',),l2_strength=.1)
        evaluation=[e for e in self.rows if e.sample.id in self.fold.evaluation_ids]
        metric=Metric('brier');gain=sum(.25-metric.loss(e.outcome,fitted.predict(e)[0]) for e in evaluation)/len(evaluation)
        self.assertLess(gain,.02)


def json_value(value):
    import json
    return json.loads(value.payload_json)
