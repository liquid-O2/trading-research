"""Separate chronological sigmoid calibration, retaining every upstream fit."""

from dataclasses import dataclass
import math

from trading_research.errors import ContractError
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.operations.provenance import InputValue
from trading_research.research.folds import FittedArtifact, Fold, validate_oof
from trading_research.research.models import BinaryExample, BinaryModel, FrequencyModel, fit_logistic, preflight_training
from trading_research.research.temporal_folds import DEFAULT_LIMITS
from trading_research.research.scoring import finite
from trading_research.research.period import (PrimaryAdmissionV1, ResearchPeriodPolicyV1,
    ResearchScopeV1)


def artifacts(model):
    return (model.artifact,) if isinstance(model,FrequencyModel) else model.fit_artifacts


def _logit_example(example,probability,version,floor):
    p=min(1-floor,max(floor,probability))
    value=InputValue('raw_logit',version,example.sample.decision_at,canonical_json(math.log(p)-math.log1p(-p)))
    return BinaryExample(example.sample,(value,),example.outcome)


@dataclass(frozen=True)
class CalibratedBinary:
    id:str
    base:BinaryModel|FrequencyModel
    calibration:BinaryModel
    artifact:FittedArtifact
    probability_floor:float
    upstream:tuple[FittedArtifact,...]
    calibration_prediction_manifest_hash:str

    def predict_committed(self, store, commit_ref, node_id, session):
        from trading_research.operations.artifact_graph import serve_bound_model
        return serve_bound_model(self, store, commit_ref, node_id, session)

    @property
    def fit_artifacts(self):
        return (*self.upstream,*artifacts(self.base),*artifacts(self.calibration),self.artifact)

    def predict(self,example:BinaryExample):
        routes={a.id:a.fold_version for a in self.fit_artifacts}
        closure=validate_oof(example.sample,self.id,self.fit_artifacts,fold_version=self.artifact.fold_version,upstream_fold_routes=routes)
        raw,manifest=self.base.predict(example,upstream=self.upstream)
        logit=_logit_example(example,raw,digest(manifest),self.probability_floor)
        calibrated,cal_manifest=self.calibration.predict(logit)
        return calibrated,{'model':self.id,'base_prediction':manifest,'calibration_prediction':cal_manifest,'fit_closure':closure}


def fit_sigmoid_calibration(base:BinaryModel|FrequencyModel,examples,fold:Fold,*,l2_strength:float,
                            probability_floor:float=1e-9,upstream:tuple[FittedArtifact,...]=(),limits=DEFAULT_LIMITS,
                            scope: ResearchScopeV1 | None = None,
                            policy: ResearchPeriodPolicyV1 | None = None,
                            admission: PrimaryAdmissionV1 | None = None):
    if not 0<finite(probability_floor)<.5:raise ContractError("calibration logit floor must be explicit")
    examples=preflight_training(examples,fold,limits=limits,scope=scope,policy=policy,admission=admission)
    training=set(fold.training_ids);converted=[];prediction_manifests=[]
    for example in examples:
        if example.sample.id in training:
            raw,manifest=base.predict(example,upstream=upstream)
            prediction_manifests.append((example.sample.id,manifest,raw))
            converted.append(_logit_example(example,raw,digest(manifest),probability_floor))
        else:
            # No future/evaluation feature or outcome is used in calibration fitting.
            converted.append(BinaryExample(example.sample,(),example.outcome))
    fitted=fit_logistic(converted,fold,('raw_logit',),l2_strength=l2_strength,limits=limits,
                        scope=scope,policy=policy,admission=admission)
    prediction_hash=digest(prediction_manifests)
    id=digest({'role':'separate_sigmoid_calibrator','base':base.id,'calibration':fitted.id,'prediction_manifest':prediction_hash,'probability_floor':probability_floor})
    fit=fitted.fit_artifacts[-1]
    artifact=FittedArtifact(id,'calibrated_binary',fold.version,fold.fit_at,fit.training_ids,fit.training_groups,fit.training_labels_known_through,(base.id,fitted.id))
    result = CalibratedBinary(id,base,fitted,artifact,probability_floor,upstream,prediction_hash)
    if scope is not None:
        object.__setattr__(result, "_research_scope", scope)
        object.__setattr__(result, "_period_policy_hash", None if policy is None else policy.config_hash)
        object.__setattr__(result, "_primary_admission", admission)
    return result
