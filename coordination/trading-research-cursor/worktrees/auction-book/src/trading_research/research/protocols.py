"""Frozen comparisons, one-use evaluation reservations and explicit quality gates."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.journal import Journal
from trading_research.research.scoring import IntervalSpec, Metric, finite
from trading_research.research.period import (PrimaryAdmissionV1, ResearchPeriodPolicyV1,
    ResearchScopeV1, check_protocol_dates, validate_primary_cut, validate_scope)


@dataclass(frozen=True)
class Candidate:
    id: str
    information: tuple[str, ...]
    representation_version: str
    learner_version: str
    generator_version: str
    policy_version: str
    search_attempts: int
    cpu_budget_seconds: int

    def __post_init__(self):
        if not all((self.id,self.representation_version,self.learner_version,self.generator_version,self.policy_version)):
            raise ContractError("candidate must version information, representation, learner, generator and policy separately")
        if not isinstance(self.information,tuple) or len(set(self.information))!=len(self.information):
            raise ContractError("immutable unique information set required")
        if type(self.search_attempts) is not int or self.search_attempts<1 or type(self.cpu_budget_seconds) is not int or self.cpu_budget_seconds<1:
            raise ContractError("candidate needs finite matched search and compute budgets")


def validate_comparison(kind: str, candidates: tuple[Candidate, ...]):
    if len(candidates)<2 or len({c.id for c in candidates})!=len(candidates):
        raise ContractError("comparison requires unique baseline and challenger definitions")
    fields={"information","representation_version","learner_version","generator_version","policy_version","search_attempts","cpu_budget_seconds"}
    allowed={"information":{"information"},"representation":{"representation_version"},"model":{"learner_version"},
             "generator":{"generator_version"},"policy":{"policy_version"},"full_stack":fields,"interaction":{"information"}}
    if kind not in allowed: raise ContractError("unregistered comparison axis")
    for field in fields-allowed[kind]:
        if len({getattr(c,field) for c in candidates})!=1:
            raise ContractError(f"{kind} comparison also changes {field}; use a distinct registered experiment")
    if kind=='interaction':
        if len(candidates)!=4: raise ContractError("interaction must register neither, A, B and A+B")
        neither,a,b,both=(set(c.information) for c in candidates)
        if not (neither<a and neither<b and a&b==neither and both==a|b):
            raise ContractError("interaction information sets do not form the exact 2x2 design")


@dataclass(frozen=True)
class Protocol:
    id: str
    selection_chain: str
    scope_ids: tuple[str, ...]
    target_version: str
    expected_mechanism: str
    comparison: str
    candidates: tuple[Candidate, ...]
    metric: Metric
    interval: IntervalSpec
    minimum_useful_gain: float
    noninferiority_loss_limit: float
    minimum_paired_coverage: float
    ordered_dates: tuple[str, ...]
    sample_manifest_hash: str
    role: str
    evaluation_start_at: int
    endpoint_at: int
    registered_at: int
    earlier_inspection: str

    def __post_init__(self):
        if not all((self.id,self.selection_chain,self.target_version,self.expected_mechanism,self.sample_manifest_hash,self.earlier_inspection)) or not self.scope_ids:
            raise ContractError("hypothesis needs mechanism, exact target/cohort, scope and prior-inspection disclosure")
        if not isinstance(self.ordered_dates,tuple) or not self.ordered_dates or len(set(self.ordered_dates))!=len(self.ordered_dates):
            raise ContractError("freeze exact chronological dates before outcomes")
        if finite(self.minimum_useful_gain)<0 or finite(self.noninferiority_loss_limit)<0 or not 0<finite(self.minimum_paired_coverage)<=1:
            raise ContractError("useful-effect, non-inferiority and coverage limits must be chosen in development")
        if self.role not in {'development','retrospective_evaluation','future_confirmation'}:
            raise ContractError("train/selection evidence is not automatically untouched confirmation")
        if any(type(x) is not int for x in (self.evaluation_start_at,self.endpoint_at,self.registered_at)) or self.endpoint_at<=self.evaluation_start_at:
            raise ContractError("explicit fixed endpoint and protocol registration clocks required")
        if self.role=='future_confirmation' and self.registered_at>=self.evaluation_start_at:
            raise ContractError("future start and endpoint must be registered before the first evaluation observation")
        validate_comparison(self.comparison,self.candidates)

    @property
    def version(self):return digest(self)


class EvaluationRegistry:
    def __init__(self,path:Path):self.journal=Journal(path)

    @staticmethod
    def _period_binding(protocol: Protocol, *, scope: ResearchScopeV1 | None,
                        policy: ResearchPeriodPolicyV1 | None,
                        admission: PrimaryAdmissionV1 | None,
                        actual_cut_at: int | None = None) -> dict:
        if type(protocol) is not Protocol:
            raise ContractError("evaluation registry requires a typed Protocol")
        validate_scope(scope, policy)
        resolved_cut = actual_cut_at
        if scope is not None and scope.is_primary:
            if admission is not None:
                if type(admission) is not PrimaryAdmissionV1:
                    raise ContractError("primary protocol requires an immutable population admission envelope")
                if admission.scope != scope:
                    raise IntegrityError("primary protocol admission scope differs from its declared scope")
                validate_primary_cut(admission.actual_cut_at, policy)  # type: ignore[arg-type]
                if resolved_cut is None:
                    resolved_cut = admission.actual_cut_at
                else:
                    validate_primary_cut(resolved_cut, policy)  # type: ignore[arg-type]
                    if resolved_cut != admission.actual_cut_at:
                        raise IntegrityError("primary protocol frozen cut differs from its admission envelope")
            elif resolved_cut is not None:
                validate_primary_cut(resolved_cut, policy)  # type: ignore[arg-type]
        elif resolved_cut is not None:
            timestamp(resolved_cut)
        check_protocol_dates(scope, policy, protocol.ordered_dates,
                             evaluation_start_at=protocol.evaluation_start_at,
                             endpoint_at=protocol.endpoint_at,
                             actual_cut_at=resolved_cut)
        if scope is None:
            if admission is not None:
                raise ContractError("population admission envelope needs an explicit research scope")
            return {}
        if scope.is_primary:
            if type(admission) is not PrimaryAdmissionV1:
                raise ContractError("primary protocol requires an immutable population admission envelope")
            if admission.scope != scope:
                raise IntegrityError("primary protocol admission scope differs from its declared scope")
            if admission.population_hash != protocol.sample_manifest_hash:
                raise IntegrityError("primary protocol sample manifest differs from its admission population hash")
        elif admission is not None:
            raise ContractError("population admission envelope is only valid for an explicit primary scope")
        return {'research_scope': asdict(scope),
                **({'primary_admission': asdict(admission), 'actual_cut_at': resolved_cut}
                   if admission is not None else ({'actual_cut_at': resolved_cut}
                                                   if resolved_cut is not None else {}))}

    @staticmethod
    def _stored_binding(payload: dict) -> dict:
        """Extract the immutable registration binding, preserving legacy omission."""
        return {key: payload[key] for key in ("research_scope", "primary_admission", "actual_cut_at")
                if key in payload}

    @classmethod
    def _require_binding_match(cls, expected_payload: dict, supplied: dict, *, phase: str) -> None:
        expected = cls._stored_binding(expected_payload)
        if expected != supplied:
            raise IntegrityError(f"{phase} scope/policy/population/cut differs from immutable registration")

    def register(self,protocol:Protocol, *, scope: ResearchScopeV1 | None = None,
                 policy: ResearchPeriodPolicyV1 | None = None,
                 admission: PrimaryAdmissionV1 | None = None,
                 actual_cut_at: int | None = None):
        binding = self._period_binding(protocol, scope=scope, policy=policy,
                                       admission=admission, actual_cut_at=actual_cut_at)
        self.journal.append(key='protocol:'+protocol.id,kind='protocol',
                            payload={'version':protocol.version,'definition':asdict(protocol),**binding})

    def register_primary(self, protocol: Protocol, *, scope: ResearchScopeV1,
                         policy: ResearchPeriodPolicyV1, admission: PrimaryAdmissionV1,
                         actual_cut_at: int | None = None):
        validate_scope(scope, policy, require_primary=True)
        if type(admission) is not PrimaryAdmissionV1:
            raise ContractError("register_primary requires an immutable population admission envelope")
        if type(protocol) is not Protocol:
            raise ContractError("register_primary requires a typed Protocol")
        if not scope.is_primary:
            raise ContractError("register_primary requires purpose_scope=primary_model")
        return self.register(protocol, scope=scope, policy=policy, admission=admission,
                             actual_cut_at=actual_cut_at)

    def begin(self,protocol:Protocol,*,model_artifacts:dict[str,str],started_at:int,
              scope: ResearchScopeV1 | None = None,
              policy: ResearchPeriodPolicyV1 | None = None,
              admission: PrimaryAdmissionV1 | None = None,
              actual_cut_at: int | None = None):
        started_at = timestamp(started_at)
        binding = self._period_binding(protocol, scope=scope, policy=policy,
                                       admission=admission, actual_cut_at=actual_cut_at)
        events=self.journal.read(); registered=next((e for e in events if e['key']=='protocol:'+protocol.id),None)
        if registered is None or registered['payload']['version']!=protocol.version:
            raise ContractError("evaluation requires the immutable registered protocol")
        self._require_binding_match(registered['payload'], binding, phase="evaluation")
        if (type(model_artifacts) is not dict
                or any(type(k) is not str or not k or type(v) is not str or not v
                       for k, v in model_artifacts.items())
                or set(model_artifacts)!={c.id for c in protocol.candidates}):
            raise ContractError("freeze every candidate model before evaluation labels are read")
        if started_at<protocol.registered_at:
            raise ContractError("evaluation precedes protocol registration")
        if protocol.role=='future_confirmation' and started_at>protocol.evaluation_start_at:
            raise ContractError("future candidate models must be frozen before evaluation begins")
        payload={'protocol':protocol.version,'selection_chain':protocol.selection_chain,'dates':protocol.ordered_dates,
                 'models':model_artifacts,'started_at':started_at,'role':protocol.role}
        payload.update(binding)
        old=next((e for e in events if e['key']=='evaluation:'+protocol.version),None)
        if old:
            if digest(old['payload'])!=digest(payload):raise IntegrityError("evaluation restart changed models, dates or initial start")
            return old['hash']
        if protocol.role!='development':
            for e in events:
                p=e['payload']
                if e['kind']=='evaluation_started' and p['selection_chain']==protocol.selection_chain and set(p['dates'])&set(protocol.ordered_dates):
                    raise ContractError("this selection chain already inspected these evaluation dates; new tuning needs new evidence")
        return self.journal.append(key='evaluation:'+protocol.version,kind='evaluation_started',payload=payload,
                                   expected_head=events[-1]['hash'] if events else None,check_head=True)[0]

    def begin_primary(self, protocol: Protocol, *, model_artifacts: dict[str, str], started_at: int,
                      scope: ResearchScopeV1, policy: ResearchPeriodPolicyV1,
                      admission: PrimaryAdmissionV1, actual_cut_at: int | None = None):
        validate_scope(scope, policy, require_primary=True)
        if type(admission) is not PrimaryAdmissionV1:
            raise ContractError("begin_primary requires an immutable population admission envelope")
        if type(protocol) is not Protocol:
            raise ContractError("begin_primary requires a typed Protocol")
        if not scope.is_primary:
            raise ContractError("begin_primary requires purpose_scope=primary_model")
        return self.begin(protocol, model_artifacts=model_artifacts, started_at=started_at,
                          scope=scope, policy=policy, admission=admission,
                          actual_cut_at=actual_cut_at)

    def finish(self,protocol:Protocol,*,report:dict,finished_at:int,
               scope: ResearchScopeV1 | None = None,
               policy: ResearchPeriodPolicyV1 | None = None,
               admission: PrimaryAdmissionV1 | None = None,
               actual_cut_at: int | None = None):
        finished_at = timestamp(finished_at)
        if type(report) is not dict:
            raise ContractError("evaluation result report must be an immutable mapping")
        binding = self._period_binding(protocol, scope=scope, policy=policy,
                                       admission=admission, actual_cut_at=actual_cut_at)
        events=self.journal.read()
        registered=next((e for e in events if e['key']=='protocol:'+protocol.id),None)
        start=next((e for e in events if e['key']=='evaluation:'+protocol.version),None)
        if registered is None or registered['payload']['version'] != protocol.version:
            raise ContractError("result requires the immutable registered protocol")
        if start is None or finished_at<start['payload']['started_at']:
            raise ContractError("unreserved evaluation or reversed completion clock")
        self._require_binding_match(registered['payload'], binding, phase="result")
        self._require_binding_match(start['payload'], binding, phase="result")
        if protocol.role=='future_confirmation' and finished_at<protocol.endpoint_at:
            raise ContractError("cannot stop a future evaluation at a favorable interim result")
        if scope is not None and scope.is_primary:
            # A future plan is registerable, but its immutable observation cut
            # cannot establish completion of an endpoint it has not reached.
            if admission.actual_cut_at < protocol.endpoint_at:
                raise ContractError("primary_result_endpoint_not_observed_at_frozen_cut")
            if admission.actual_cut_at > finished_at:
                raise ContractError("primary_result_observation_cut_after_completion")
        if report.get('protocol_version')!=protocol.version or report.get('sample_manifest_hash')!=protocol.sample_manifest_hash:
            raise ContractError("result does not identify the frozen evaluation population")
        payload={'protocol':protocol.version,'finished_at':finished_at,'report':report}
        payload.update(binding)
        return self.journal.append(key='result:'+protocol.version,kind='evaluation_finished',
                                   payload=payload)[0]

    def finish_primary(self, protocol: Protocol, *, report: dict, finished_at: int,
                       scope: ResearchScopeV1, policy: ResearchPeriodPolicyV1,
                       admission: PrimaryAdmissionV1, actual_cut_at: int | None = None):
        validate_scope(scope, policy, require_primary=True)
        if type(admission) is not PrimaryAdmissionV1:
            raise ContractError("finish_primary requires an immutable population admission envelope")
        if type(protocol) is not Protocol:
            raise ContractError("finish_primary requires a typed Protocol")
        if not scope.is_primary:
            raise ContractError("finish_primary requires purpose_scope=primary_model")
        return self.finish(protocol, report=report, finished_at=finished_at, scope=scope,
                           policy=policy, admission=admission, actual_cut_at=actual_cut_at)


def predictive_disposition(report:dict, protocol:Protocol, *, critical_invariants:dict[str,bool]):
    if not critical_invariants or any(value is not True for value in critical_invariants.values()):
        return {'status':'not_met','reason':'critical semantic/causal invariant failure; repair before judging prediction'}
    effect=report['improvement']
    if report['paired_coverage']<protocol.minimum_paired_coverage or effect.get('lower') is None:
        return {'status':'inconclusive','reason':'insufficient comparable coverage or dependent-block support'}
    if effect['lower']>=protocol.minimum_useful_gain and effect['lower']>=-protocol.noninferiority_loss_limit:
        return {'status':'supported','reason':'local prediction comparison meets frozen effect rule; economics and survival remain separate'}
    if effect['upper']<protocol.minimum_useful_gain or effect['upper']<-protocol.noninferiority_loss_limit:
        return {'status':'not_met','reason':'adequately supported interval fails the registered useful-effect/non-inferiority rule'}
    return {'status':'inconclusive','reason':'interval crosses the frozen acceptance threshold'}


QUALITY_DIMENSIONS=('semantics','causality','prediction','incremental_information','decisions','survival')


@dataclass(frozen=True)
class QualityEvidence:
    dimension:str
    status:str
    artifact_hashes:tuple[str,...]
    reason:str

    def __post_init__(self):
        if self.dimension not in QUALITY_DIMENSIONS or self.status not in {'unrun','supported','not_met','inconclusive','not_applicable'} or not self.reason:
            raise ContractError("quality track needs a declared role, result and reason")
        if self.status not in {'unrun','not_applicable'} and not self.artifact_hashes:
            raise ContractError("completed quality judgments require actual evidence artifacts")


def scorecard(*,unit_id:str,role:str,evidence:tuple[QualityEvidence,...],selected_version:str|None,
              objective_mean_per_day:float|None,objective_target:float=2000):
    by={e.dimension:e for e in evidence}
    if not unit_id or role not in {'predictor','measurement','risk_invariant','operations'} or len(by)!=len(evidence) or set(by)!=set(QUALITY_DIMENSIONS):
        raise ContractError("each component needs all six distinct quality tracks with appropriate explicit applicability")
    if role=='predictor' and any(by[d].status=='not_applicable' for d in QUALITY_DIMENSIONS):
        raise ContractError("a predictor cannot remove downstream value/survival obligations")
    if selected_version and any(by[d].status!='supported' for d in ('semantics','causality')):
        raise ContractError("unverified semantic/causal component cannot be selected")
    if selected_version and role=='predictor' and any(by[d].status!='supported' for d in QUALITY_DIMENSIONS):
        raise ContractError("complete predictor promotion requires all six evidence tracks")
    return {'unit':unit_id,'role':role,'evidence':[asdict(by[d]) for d in QUALITY_DIMENSIONS],
            'selected_version':selected_version,'objective_mean_per_day':objective_mean_per_day,
            'objective_gap':None if objective_mean_per_day is None else finite(objective_target)-finite(objective_mean_per_day),
            'program_complete':False,'interpretation':'Track-specific evidence; local scores never substitute for complete sequential economics.'}
