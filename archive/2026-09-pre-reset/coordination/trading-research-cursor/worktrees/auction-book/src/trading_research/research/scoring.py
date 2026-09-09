"""Target-matched proper losses and paired, dependent-block comparisons.

Loss conventions: lower is better. CRPS is E|X-y| - E|X-X'|/2.
Reference: https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf
The declared probability floor modifies log loss at the boundary and is reported.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
import random
from statistics import fmean

from trading_research.errors import ContractError
from trading_research.operations.artifacts import digest


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError("finite numeric score input required")
    return float(value)


def probability(value):
    p = finite(value)
    if not 0 <= p <= 1:
        raise ContractError("probability outside [0,1]")
    return p


@dataclass(frozen=True)
class Metric:
    name: str
    probability_floor: float = 1e-12
    quantile: float = .5
    variance_floor: float = 1e-12

    def __post_init__(self):
        if self.name not in {"brier", "log_loss", "multiclass_log_loss", "pinball", "qlike", "crps", "squared_error"}:
            raise ContractError("unsupported metric; censored/path targets need a separately valid observation model")
        if not 0 < finite(self.probability_floor) < .5 or not 0 < finite(self.quantile) < 1 or finite(self.variance_floor) <= 0:
            raise ContractError("numerical floors and quantile must be frozen valid values")

    @property
    def version(self):
        return digest(self)

    def loss(self, y, prediction):
        if self.name == "multiclass_log_loss":
            if type(y) is not int or not isinstance(prediction, tuple) or not 0 <= y < len(prediction):
                raise ContractError("class index and immutable probability vector required")
            ps = tuple(probability(p) for p in prediction)
            if not math.isclose(math.fsum(ps), 1, rel_tol=0, abs_tol=1e-12):
                raise ContractError("class probabilities do not sum to one")
            return -math.log(max(self.probability_floor, ps[y]))
        y = finite(y)
        if self.name in {"brier", "log_loss"}:
            if y not in (0, 1):
                raise ContractError("binary scores require observed binary labels")
            p = probability(prediction)
            if self.name == "brier":
                return (y - p) ** 2
            p = min(1 - self.probability_floor, max(self.probability_floor, p))
            return -math.log(p) if y == 1 else -math.log1p(-p)
        if self.name == "crps":
            if not isinstance(prediction, tuple) or not prediction or len(prediction) > 4096:
                raise ContractError("CRPS requires a bounded immutable equally weighted ensemble")
            xs = sorted(finite(x) for x in prediction)
            n = len(xs)
            # Sorted O(n log n) identity; reference tests use the independent pair sum.
            half_pair = math.fsum((2*i - n + 1)*x for i, x in enumerate(xs)) / (n*n)
            return fmean(abs(x-y) for x in xs) - half_pair
        p = finite(prediction)
        if self.name == "pinball":
            error = y-p
            return self.quantile*error if error >= 0 else (self.quantile-1)*error
        if self.name == "qlike":
            if y < 0 or p <= 0:
                raise ContractError("QLIKE needs nonnegative observed variance and a strictly positive forecast")
            p = max(p, self.variance_floor)
            return math.log(p) + y/p  # Label-only constant omitted, including y=0.
        return (y-p)**2


@dataclass(frozen=True)
class ScoreRow:
    sample_id: str
    date_group: str
    target_signature: str
    label_version: str
    outcome: float | int | None
    prediction: float | tuple[float, ...] | None
    state: str = "observed"
    subgroup: str = "all"

    def __post_init__(self):
        if not all((self.sample_id, self.date_group, self.target_signature, self.label_version, self.subgroup)):
            raise ContractError("score rows require complete sample/target/label identity")
        if self.state not in {"observed", "censored", "ambiguous", "missing"}:
            raise ContractError("unregistered label observation state")
        if self.state == "observed" and self.outcome is None:
            raise ContractError("observed label cannot be absent")
        if self.state != "observed" and self.outcome is not None:
            raise ContractError("unobserved outcome cannot be zero-filled")


def _rows(rows):
    rows = tuple(rows)
    ids = {r.sample_id:r for r in rows}
    if not rows or len(ids) != len(rows):
        raise ContractError("empty or duplicate score population")
    return ids


def quantile(values, level):
    if not values or not 0 <= level <= 1:
        raise ContractError("invalid empirical quantile")
    xs = sorted(values)
    index = (len(xs)-1)*level
    lo = math.floor(index); hi = math.ceil(index)
    return xs[lo] + (xs[hi]-xs[lo])*(index-lo)


@dataclass(frozen=True)
class IntervalSpec:
    confidence: float
    replicates: int
    seed: int
    block_length: int
    minimum_blocks: int
    weighting: str = "equal_date"

    def __post_init__(self):
        if not .5 < finite(self.confidence) < 1 or type(self.replicates) is not int or not 200 <= self.replicates <= 20000:
            raise ContractError("invalid declared bootstrap confidence or bounded replication count")
        if type(self.seed) is not int or type(self.block_length) is not int or self.block_length < 1 or type(self.minimum_blocks) is not int or self.minimum_blocks < 2:
            raise ContractError("explicit seed, dependence length and support threshold required")
        if self.weighting not in {"equal_date", "equal_sample"}:
            raise ContractError("unknown date/sample estimand")


def block_interval(values_by_date: dict[str, tuple[float, ...]], spec: IntervalSpec,
                   *, ordered_dates: tuple[str, ...]):
    if len(ordered_dates) != len(set(ordered_dates)) or set(ordered_dates) != set(values_by_date):
        raise ContractError("explicit chronological date order must cover exactly the compared dates")
    dates = [tuple(finite(v) for v in values_by_date[d]) for d in ordered_dates]
    if not dates or any(not day for day in dates):
        raise ContractError("empty date in comparison; complete-day economics must retain explicit zero days")
    def mean(indices):
        if spec.weighting == "equal_date":
            return fmean(fmean(dates[i]) for i in indices)
        return fmean(x for i in indices for x in dates[i])
    n = len(dates); estimate = mean(range(n)); blocks = n // spec.block_length
    if blocks < spec.minimum_blocks:
        return {"estimate":estimate, "lower":None, "upper":None, "support":"insufficient",
                "dates":n, "nonoverlapping_block_count":blocks}
    # Moving contiguous blocks, without artificial wrap from last date to first.
    rng = random.Random(spec.seed); draws = []
    for _ in range(spec.replicates):
        indices = []
        while len(indices) < n:
            start = rng.randrange(n-spec.block_length+1)
            indices.extend(range(start, start+spec.block_length))
        draws.append(mean(indices[:n]))
    tail = (1-spec.confidence)/2
    return {"estimate":estimate,"lower":quantile(draws,tail),"upper":quantile(draws,1-tail),
            "support":"adequate_under_declared_block_model", "dates":n, "nonoverlapping_block_count":blocks,
            "method":"paired moving-date-block percentile bootstrap", "specification":spec,
            "limitations":"Conditional on declared blocks and support; nonstationarity and trial selection require separate controls."}


def paired_scores(baseline, challenger, metric: Metric, interval: IntervalSpec, *, ordered_dates: tuple[str, ...]):
    a, b = _rows(baseline), _rows(challenger)
    if set(a) != set(b):
        raise ContractError("comparison changed candidate/sample population; register a generator/policy experiment")
    gains = defaultdict(list); score_a, score_b = [], []; states = defaultdict(int); groups = defaultdict(list)
    missing_forecasts = 0
    for id in sorted(a):
        x, y = a[id], b[id]
        if (x.date_group,x.target_signature,x.label_version,x.outcome,x.state,x.subgroup) != (y.date_group,y.target_signature,y.label_version,y.outcome,y.state,y.subgroup):
            raise ContractError("paired score changed target, horizon, geometry, label, date or observation state")
        states[x.state] += 1
        if x.state != "observed":
            continue
        if x.prediction is None or y.prediction is None:
            missing_forecasts += 1
            continue
        la, lb = metric.loss(x.outcome,x.prediction), metric.loss(y.outcome,y.prediction)
        score_a.append(la); score_b.append(lb); gains[x.date_group].append(la-lb); groups[x.subgroup].append(la-lb)
    declared = set(ordered_dates)
    if declared != {row.date_group for row in a.values()}:
        raise ContractError("declared evaluation dates omit/add sample groups")
    evaluable_dates = tuple(d for d in ordered_dates if d in gains)
    effect = block_interval(gains, interval, ordered_dates=evaluable_dates) if gains else {"estimate":None,"lower":None,"upper":None,"support":"insufficient","dates":0}
    return {"population_hash":digest(tuple((id,a[id].target_signature,a[id].label_version) for id in sorted(a))),
            "population_count":len(a),"observed_label_count":states['observed'],"label_states":dict(states),
            "paired_forecast_count":len(score_a),"missing_forecast_count":missing_forecasts,
            "paired_coverage":len(score_a)/len(a),"omitted_score_dates":sorted(declared-set(gains)),
            "baseline_loss":fmean(score_a) if score_a else None,"challenger_loss":fmean(score_b) if score_b else None,
            "improvement":effect,"metric":metric,"descriptive_subgroup_effects":{k:{"samples":len(v),"mean":fmean(v)} for k,v in groups.items()}}


def reliability(rows, *, edges: tuple[float, ...]):
    if not isinstance(edges,tuple) or len(edges)<2 or edges[0]!=0 or edges[-1]!=1 or any(x>=y for x,y in zip(edges,edges[1:])):
        raise ContractError("calibration bins must be fixed ordered edges from zero to one")
    cells=[[] for _ in edges[1:]]
    for row in _rows(rows).values():
        if row.state!='observed' or row.prediction is None:
            continue
        if row.outcome not in (0,1): raise ContractError("binary reliability labels required")
        p=probability(row.prediction)
        cell=min(len(cells)-1, next((i for i,e in enumerate(edges[1:]) if p<e),len(cells)-1))
        cells[cell].append((p,row.outcome,row.date_group))
    return tuple({"lower":edges[i],"upper":edges[i+1],"count":len(c),"dates":len({r[2] for r in c}),
                  "mean_probability":fmean(r[0] for r in c) if c else None,"observed_frequency":fmean(r[1] for r in c) if c else None,
                  "uncertainty":"descriptive; use registered date-block resampling for inference"} for i,c in enumerate(cells))
