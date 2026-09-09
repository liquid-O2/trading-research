"""Bounded independent binary baselines with audited reads and fitted closure.

The logistic objective is mean log loss + lambda/2 * ||standardized slopes||^2;
the intercept is unpenalized. Lambda is a strength, not sklearn's inverse C.
"""

from collections import defaultdict
from dataclasses import dataclass
import json
import math
from statistics import fmean

from trading_research.errors import ContractError
from trading_research.operations.artifacts import digest
from trading_research.operations.provenance import InputAudit, InputValue
from trading_research.research.folds import FittedArtifact, Fold, Sample, validate_oof, validate_fold_population
from trading_research.research.scoring import finite, probability
from trading_research.research.temporal_folds import (TemporalFoldV1, TemporalSampleV1,
    validate_temporal_fold_population, DEFAULT_LIMITS, V01V02LimitsV1, bounded)
from trading_research.research.period import (PrimaryAdmissionV1, ResearchPeriodPolicyV1,
    ResearchScopeV1, check_sample_population, validate_consumer_admission,
    validate_consumer_admission_shape, validate_scope)


def sigmoid(x):
    if x>=0:
        z=math.exp(-x);return 1/(1+z)
    z=math.exp(x);return z/(1+z)


@dataclass(frozen=True)
class BinaryExample:
    sample: Sample
    values: tuple[InputValue,...]
    outcome: int

    def __post_init__(self):
        if (type(self.sample) not in (Sample,TemporalSampleV1) or type(self.outcome) is not int
                or self.outcome not in (0,1) or type(self.values) is not tuple
                or any(type(v) is not InputValue for v in self.values)):
            raise ContractError("binary example requires exact observed label and immutable input versions")
        if len({v.column for v in self.values})!=len(self.values):
            raise ContractError("duplicate feature column")


def read_features(example:BinaryExample,columns:tuple[str,...],*,fold_version:str,upstream:tuple[FittedArtifact,...]=()):
    if not isinstance(columns,tuple) or len(set(columns))!=len(columns):
        raise ContractError("immutable unique declared features required")
    audit=InputAudit(frozenset(columns),{v.column:v for v in example.values},cut=example.sample.decision_at,fold_version=fold_version)
    values=tuple(finite(json.loads(audit.read(c))) for c in columns)
    manifest=audit.manifest()
    for read in manifest['actual_reads'].values():
        for id in read['fitted_dependency_ids']:
            validate_oof(example.sample,id,upstream,fold_version=fold_version)
    return values,manifest


def preflight_training(examples,fold,*,limits=DEFAULT_LIMITS,
                       scope: ResearchScopeV1 | None = None,
                       policy: ResearchPeriodPolicyV1 | None = None,
                       admission: PrimaryAdmissionV1 | None = None):
    if type(limits) is not V01V02LimitsV1 or type(fold) not in (Fold,TemporalFoldV1):
        raise ContractError('exact fold and explicit local training limits required')
    limits.__post_init__()
    examples=bounded(examples,limits.max_temporal_population if type(fold) is TemporalFoldV1 else 200000,'training population')
    if any(type(e) is not BinaryExample for e in examples):
        raise ContractError('typed binary examples required before model reads')
    for example in examples:
        example.__post_init__()
    samples=tuple(sorted((e.sample for e in examples),key=lambda s:(s.decision_at,s.id)))
    validate_scope(scope, policy)
    admission_cut = validate_consumer_admission_shape(scope=scope, policy=policy, admission=admission)
    check_sample_population(scope, policy, samples, fit_at=fold.fit_at,
                            evaluation_start=fold.evaluation_start, evaluation_end=fold.evaluation_end,
                            training_start=getattr(fold, 'training_start', None),
                            actual_cut_at=admission_cut)
    validate_consumer_admission(samples, scope=scope, policy=policy, admission=admission)
    if type(fold) is TemporalFoldV1:
        validate_temporal_fold_population(samples, fold, limits=limits, scope=scope, policy=policy,
                                          admission=admission)
    else:
        validate_fold_population(samples, fold, scope=scope, policy=policy, admission=admission)
    if digest(samples)!=fold.sample_manifest_hash:
        raise ContractError("training rows differ from the complete frozen fold population")
    by={e.sample.id:e for e in examples}
    if len(by)!=len(examples) or not fold.training_ids or set(fold.training_ids)&set(fold.evaluation_ids):
        raise ContractError("invalid or empty training partition")
    rows=tuple(by[id] for id in fold.training_ids)
    targets={e.sample.target_version for e in rows}
    if len(targets)!=1:raise ContractError("one binary fit cannot mix target definitions")
    for e in rows:
        if e.sample.label_known_at>fold.fit_at or (type(fold) is not TemporalFoldV1 and e.sample.dependency_end>=fold.evaluation_start-fold.embargo_ns):
            raise ContractError("training label/span overlaps evaluation")
    return examples


def _training(examples,fold:Fold,columns,upstream,*,limits=DEFAULT_LIMITS,
              scope: ResearchScopeV1 | None = None,
              policy: ResearchPeriodPolicyV1 | None = None,
              admission: PrimaryAdmissionV1 | None = None):
    examples=preflight_training(examples,fold,limits=limits,scope=scope,policy=policy,admission=admission)
    by={e.sample.id:e for e in examples}
    rows=tuple(by[id] for id in fold.training_ids); data=[]; manifests=[]
    for e in rows:
        x,m=read_features(e,columns,fold_version=fold.version,upstream=upstream);data.append(x);manifests.append(m)
    dependencies=tuple(sorted({id for m in manifests for r in m['actual_reads'].values() for id in r['fitted_dependency_ids']}))
    return rows,tuple(data),tuple(manifests),dependencies


@dataclass(frozen=True)
class BinaryModel:
    id:str
    columns:tuple[str,...]
    means:tuple[float,...]
    scales:tuple[float,...]
    intercept:float
    coefficients:tuple[float,...]
    l2_strength:float
    iterations:int
    maximum_gradient:float
    objective:float
    training_read_hash:str
    target_version:str
    fit_artifacts:tuple[FittedArtifact,...]

    @property
    def fold_version(self):return self.fit_artifacts[-1].fold_version

    def predict_committed(self, store, commit_ref, node_id, session):
        from trading_research.operations.artifact_graph import serve_bound_model
        return serve_bound_model(self, store, commit_ref, node_id, session)

    def predict(self,example:BinaryExample,*,upstream:tuple[FittedArtifact,...]=()):
        if example.sample.target_version!=self.target_version:raise ContractError("model target differs from requested target")
        by_id={}
        for artifact in (*upstream,*self.fit_artifacts):
            if artifact.id in by_id and by_id[artifact.id]!=artifact:
                raise ContractError("conflicting fitted artifacts share one immutable identity")
            by_id[artifact.id]=artifact
        closure=tuple(by_id.values())
        validate_oof(example.sample,self.id,closure,fold_version=self.fold_version)
        x,reads=read_features(example,self.columns,fold_version=self.fold_version,upstream=closure)
        z=self.intercept+math.fsum(w*(v-m)/s for w,v,m,s in zip(self.coefficients,x,self.means,self.scales))
        return sigmoid(z),{'model':self.id,'input_manifest':reads,'fit_closure':validate_oof(example.sample,self.id,closure,fold_version=self.fold_version)}


def _linear_solve(matrix,rhs):
    n=len(rhs); a=[list(row)+[b] for row,b in zip(matrix,rhs)]
    for i in range(n):
        pivot=max(range(i,n),key=lambda r:abs(a[r][i]))
        if abs(a[pivot][i])<1e-14:raise ContractError("singular reference Hessian; no silently regularized solution")
        a[i],a[pivot]=a[pivot],a[i]
        scale=a[i][i];a[i]=[x/scale for x in a[i]]
        for r in range(n):
            if r==i:continue
            factor=a[r][i];a[r]=[x-factor*y for x,y in zip(a[r],a[i])]
    return tuple(row[-1] for row in a)


def fit_logistic(examples,fold:Fold,columns:tuple[str,...],*,l2_strength:float,
                 maximum_iterations:int=60,tolerance:float=1e-8,upstream:tuple[FittedArtifact,...]=(),limits=DEFAULT_LIMITS,
                 scope: ResearchScopeV1 | None = None,
                 policy: ResearchPeriodPolicyV1 | None = None,
                 admission: PrimaryAdmissionV1 | None = None):
    if finite(l2_strength)<=0 or not 0<finite(tolerance)<1 or type(maximum_iterations) is not int or not 1<=maximum_iterations<=200 or len(columns)>64:
        raise ContractError("bounded solver with positive explicit L2 and convergence tolerance required")
    rows,x,reads,dependencies=_training(examples,fold,columns,upstream,limits=limits,
                                        scope=scope,policy=policy,admission=admission)
    if len(rows)>200000:raise ContractError("reference learner row budget exceeded; benchmark an optimized implementation first")
    ys=tuple(e.outcome for e in rows);n=len(rows)
    if len(set(ys))<2:raise ContractError("single-class training: use the registered smoothed-frequency fallback")
    means=tuple(fmean(row[j] for row in x) for j in range(len(columns)))
    scales=tuple(math.sqrt(fmean((row[j]-means[j])**2 for row in x)) or 1. for j in range(len(columns)))
    design=tuple((1.,)+tuple((v-m)/s for v,m,s in zip(row,means,scales)) for row in x)
    p=len(columns)+1;weights=[math.log(sum(ys)/(n-sum(ys)))]+[0.]*(p-1)
    def objective(w):
        scores=(math.fsum(a*b for a,b in zip(row,w)) for row in design)
        return fmean(max(z,0)-y*z+math.log1p(math.exp(-abs(z))) for z,y in zip(scores,ys))+l2_strength*math.fsum(v*v for v in w[1:])/2
    value=objective(weights);gradient_norm=math.inf
    for iteration in range(1,maximum_iterations+1):
        gradient=[0.]*p;hessian=[[0.]*p for _ in range(p)]
        for row,y in zip(design,ys):
            pred=sigmoid(math.fsum(a*b for a,b in zip(row,weights)));res=(pred-y)/n;curvature=pred*(1-pred)/n
            for j in range(p):
                gradient[j]+=res*row[j]
                for k in range(j+1):hessian[j][k]+=curvature*row[j]*row[k]
        for j in range(p):
            if j:gradient[j]+=l2_strength*weights[j];hessian[j][j]+=l2_strength
            for k in range(j):hessian[k][j]=hessian[j][k]
        gradient_norm=max(abs(g) for g in gradient)
        if gradient_norm<=tolerance:break
        direction=_linear_solve(hessian,gradient);slope=math.fsum(g*d for g,d in zip(gradient,direction));step=1.
        for _ in range(30):
            proposal=[w-step*d for w,d in zip(weights,direction)];new_value=objective(proposal)
            if new_value<=value-1e-4*step*slope+1e-15:
                weights=proposal;value=new_value;break
            step*=.5
        else:raise ContractError("logistic line search did not converge")
    else:raise ContractError("logistic iteration budget exhausted before convergence")
    common={'fold_version':fold.version,'fitted_at':fold.fit_at,'training_ids':frozenset(e.sample.id for e in rows),
            'training_groups':frozenset(e.sample.date_group for e in rows),'training_labels_known_through':max(e.sample.label_known_at for e in rows)}
    read_hash=digest(reads);scale_id=digest({'role':'training_only_scaler','means':means,'scales':scales,'reads':read_hash,'fold':fold.version})
    scaler=FittedArtifact(scale_id,'scaler',upstream_ids=dependencies,**common)
    id=digest({'role':'binary_logistic','columns':columns,'scaler':scale_id,'weights':weights,'lambda':l2_strength,'objective':'mean_log_loss_plus_half_lambda_slope_l2','tolerance':tolerance,'iterations':iteration})
    learner=FittedArtifact(id,'binary_logistic',upstream_ids=(scale_id,),**common)
    result = BinaryModel(id,columns,means,scales,weights[0],tuple(weights[1:]),l2_strength,iteration,gradient_norm,value,read_hash,rows[0].sample.target_version,(scaler,learner))
    if scope is not None:
        object.__setattr__(result, "_research_scope", scope)
        object.__setattr__(result, "_period_policy_hash", None if policy is None else policy.config_hash)
        object.__setattr__(result, "_primary_admission", admission)
    return result


@dataclass(frozen=True)
class FrequencyModel:
    id:str
    columns:tuple[str,...]
    cuts:tuple[tuple[float,...],...]
    cells:tuple[tuple[tuple[int,...],int,int],...]
    overall:float
    prior_strength:float
    prior_center:str
    artifact:FittedArtifact
    target_version:str
    training_read_hash:str

    def predict_committed(self, store, commit_ref, node_id, session):
        from trading_research.operations.artifact_graph import serve_bound_model
        return serve_bound_model(self, store, commit_ref, node_id, session)

    def predict(self,example:BinaryExample,*,upstream:tuple[FittedArtifact,...]=()):
        if example.sample.target_version!=self.target_version:raise ContractError("frequency model target mismatch")
        validate_oof(example.sample,self.id,(*upstream,self.artifact),fold_version=self.artifact.fold_version)
        x,reads=read_features(example,self.columns,fold_version=self.artifact.fold_version,upstream=upstream)
        key=tuple(sum(v>=c for c in edges) for v,edges in zip(x,self.cuts))
        cell=next(((successes,n) for k,successes,n in self.cells if k==key),None)
        center=.5 if self.prior_center=='uniform' else self.overall
        p=self.overall if cell is None else (cell[0]+self.prior_strength*center)/(cell[1]+self.prior_strength)
        return p,{'model':self.id,'cell':key,'cell_support':0 if cell is None else cell[1],'input_manifest':reads}


def fit_frequency(examples,fold:Fold,columns:tuple[str,...],*,cuts:tuple[tuple[float,...],...],prior_strength:float=2.,prior_center:str='uniform',upstream:tuple[FittedArtifact,...]=(),limits=DEFAULT_LIMITS,
                  scope: ResearchScopeV1 | None = None,
                  policy: ResearchPeriodPolicyV1 | None = None,
                  admission: PrimaryAdmissionV1 | None = None):
    if (not isinstance(cuts,tuple) or any(not isinstance(cs,tuple) for cs in cuts)
            or prior_center not in {'uniform','training_overall'} or len(cuts)!=len(columns) or finite(prior_strength)<=0
            or any(any(not math.isfinite(finite(c)) for c in cs) or any(a>=b for a,b in zip(cs,cs[1:])) for cs in cuts)):
        raise ContractError("prespecified bins and strictly positive shrinkage required")
    rows,x,reads,dependencies=_training(examples,fold,columns,upstream,limits=limits,
                                        scope=scope,policy=policy,admission=admission);cells=defaultdict(lambda:[0,0])
    overall=(sum(e.outcome for e in rows)+1)/(len(rows)+2)
    for values,e in zip(x,rows):
        key=tuple(sum(v>=c for c in edges) for v,edges in zip(values,cuts));cells[key][0]+=e.outcome;cells[key][1]+=1
    content=tuple((key,*value) for key,value in sorted(cells.items()));read_hash=digest(reads)
    id=digest({'role':'shrunken_conditional_frequency','cells':content,'overall_beta_1_1':overall,'prior_strength':prior_strength,'prior_center':prior_center,'cuts':cuts,'reads':read_hash,'fold':fold.version})
    artifact=FittedArtifact(id,'conditional_frequency',fold.version,fold.fit_at,frozenset(e.sample.id for e in rows),frozenset(e.sample.date_group for e in rows),max(e.sample.label_known_at for e in rows),dependencies)
    result = FrequencyModel(id,columns,cuts,content,overall,prior_strength,prior_center,artifact,rows[0].sample.target_version,read_hash)
    if scope is not None:
        object.__setattr__(result, "_research_scope", scope)
        object.__setattr__(result, "_period_policy_hash", None if policy is None else policy.config_hash)
        object.__setattr__(result, "_primary_admission", admission)
    return result
