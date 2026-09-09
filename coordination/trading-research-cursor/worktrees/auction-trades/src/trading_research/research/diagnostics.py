"""Prespecified learning-curve, permutation and interaction diagnostics."""

from collections import defaultdict
from dataclasses import dataclass
import random
from statistics import fmean

from trading_research.errors import ContractError
from trading_research.research.protocols import Candidate, validate_comparison
from trading_research.research.scoring import IntervalSpec, ScoreRow, block_interval


def chronological_training_subsets(ids_by_date:dict[str,tuple[str,...]],*,ordered_dates:tuple[str,...],fractions:tuple[float,...]):
    if not fractions or any(not 0<f<=1 for f in fractions) or any(a>=b for a,b in zip(fractions,fractions[1:])):
        raise ContractError("chronological learning fractions must be frozen and strictly increasing")
    if set(ordered_dates)!=set(ids_by_date) or len(set(ordered_dates))!=len(ordered_dates):
        raise ContractError("learning curve requires exact chronological training date groups")
    all_ids=[id for d in ordered_dates for id in ids_by_date[d]]
    if len(set(all_ids))!=len(all_ids):raise ContractError("sample appears in two training dates")
    return tuple({'fraction':f,'dates':ordered_dates[:max(1,int(len(ordered_dates)*f))],
                  'training_ids':tuple(id for d in ordered_dates[:max(1,int(len(ordered_dates)*f))] for id in ids_by_date[d])}
                 for f in fractions)


def compatible_block_permutation(blocks:dict[str,tuple],compatibility:dict[str,str],*,seed:int):
    if set(blocks)!=set(compatibility) or any(not b for b in blocks.values()):
        raise ContractError("null control requires every intact block and its declared compatibility class")
    groups=defaultdict(list)
    for id in sorted(blocks):groups[(compatibility[id],len(blocks[id]))].append(id)
    rng=random.Random(seed);mapping={}
    for ids in groups.values():
        if len(ids)<2:raise ContractError("cannot shuffle a singleton compatible block; report insufficient null support")
        permutation=list(ids);rng.shuffle(permutation)
        mapping.update(zip(ids,permutation))
    return {id:blocks[mapping[id]] for id in blocks},mapping


def interaction_effect(candidates:tuple[Candidate,...],losses:dict[str,dict[str,tuple[float,...]]],*,interval:IntervalSpec,ordered_dates:tuple[str,...]):
    validate_comparison('interaction',candidates)
    if set(losses)!={c.id for c in candidates}:raise ContractError("missing registered 2x2 arm")
    arrays=[losses[c.id] for c in candidates]
    if any(set(a)!=set(ordered_dates) for a in arrays):raise ContractError("interaction changed compared dates")
    differences={}
    for date in ordered_dates:
        values=[a[date] for a in arrays]
        if len({len(v) for v in values})!=1 or not values[0]:raise ContractError("interaction needs aligned same-date sample losses")
        differences[date]=tuple(a+b-both-neither for neither,a,b,both in zip(*values))
    return {'synergy_gain':block_interval(differences,interval,ordered_dates=ordered_dates),
            'interpretation':'Additional loss reduction from A+B beyond separate A and B gains; evidence conditional on registered matching and model capacity.'}


def learning_diagnostic(training_losses:tuple[float,...],evaluation_losses:tuple[float,...],*,minimum_change:float):
    if len(training_losses)!=len(evaluation_losses) or len(training_losses)<2 or minimum_change<=0:
        raise ContractError("diagnostic requires paired prespecified learning-curve points and a development threshold")
    train_gain=training_losses[0]-training_losses[-1];eval_gain=evaluation_losses[0]-evaluation_losses[-1]
    if train_gain>minimum_change and eval_gain<=minimum_change:
        return 'generalization concern: compare regularization, information/target fidelity and support; not proof of a unique cause'
    if eval_gain>minimum_change:return 'evaluation improves with more chronological training; compare cost and remaining uncertainty'
    return 'plateau at these fractions: test measurement, information, target and matched-capacity alternatives separately'
