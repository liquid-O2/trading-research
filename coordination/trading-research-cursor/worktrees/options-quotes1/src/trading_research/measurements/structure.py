"""Causal bar pivots, threshold swings and anchor-matched divergence facts."""

from dataclasses import asdict,dataclass
from fractions import Fraction
import json

from trading_research.errors import ContractError,DependencyUnavailable,IntegrityError
from trading_research.foundations.bars import CausalBar
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import canonical_json,digest


@dataclass(frozen=True)
class Swing:
    id:str
    instrument:str
    side:str
    price_ticks:int
    extreme_start:int
    extreme_end:int
    confirmed_at:int
    source_versions:tuple[str,...]
    definition_version:str
    status:str

    @property
    def version_id(self):return digest(self)


def pivot_reference(bars:tuple[CausalBar,...],*,left:int,right:int,cut:int,ties:str='strict'):
    if any(type(k) is not int or k<1 or k>1000 for k in (left,right)) or ties not in {'strict','earliest','latest','ambiguous'}:
        raise ContractError("bounded pivot lengths and explicit equality convention required")
    latest={}
    for b in bars:
        if b.published_at is not None and b.published_at<=cut:
            old=latest.get(b.bar_id)
            if old is None or (b.published_at,b.revision)>(old.published_at,old.revision):latest[b.bar_id]=b
    seq=sorted(latest.values(),key=lambda b:b.start)
    if len({b.instrument for b in seq})>1:raise ContractError("pivots cannot span a raw contract transition")
    definition=digest({'left':left,'right':right,'ties':ties,'kind':'final_bar_pivot'})
    output=[]
    for i in range(left,len(seq)-right):
        window=seq[i-left:i+right+1];center=seq[i]
        if any(not b.final or not b.coverage_complete or b.high_ticks is None or b.low_ticks is None for b in window):continue
        if any(a.end!=b.start for a,b in zip(window,window[1:])):continue
        for side,field,best in (('high','high_ticks',max),('low','low_ticks',min)):
            prices=[getattr(b,field) for b in window];level=getattr(center,field)
            if level!=best(prices):continue
            equal=[j for j,p in enumerate(prices) if p==level]
            if ties=='strict' and len(equal)>1:continue
            if ties=='earliest' and equal[0]!=left or ties=='latest' and equal[-1]!=left:continue
            known=max(b.published_at for b in window)
            output.append(Swing(digest([center.bar_id,side,definition]),center.instrument,side,level,center.start,center.end,known,
                                tuple(b.version_id for b in window),definition,'ambiguous_equal_extremum' if ties=='ambiguous' and len(equal)>1 else 'confirmed'))
    return tuple(output)


@dataclass(frozen=True)
class PricePoint:
    id:str
    instrument:str
    event_at:int
    known_at:int
    ticks:int
    order:int|None
    complete:bool=True

    def __post_init__(self):
        timestamp(self.event_at);timestamp(self.known_at)
        if not self.id or not self.instrument or type(self.ticks) is not int or type(self.complete) is not bool or (self.order is not None and (type(self.order) is not int or self.order<0)):
            raise ContractError("price point needs immutable instrument, exact ticks, quality and ordering")


class DirectionalChanges:
    def __init__(self,*,instrument:str,threshold_ticks:int,definition_version:str):
        if not instrument or not definition_version or type(threshold_ticks) is not int or threshold_ticks<1:
            raise ContractError("directional changes require prior-frozen positive tick threshold")
        self.instrument=instrument;self.threshold=threshold_ticks;self.definition=definition_version
        self.direction=0;self.high=None;self.low=None;self.last=None;self.seen={};self.confirmed=[]

    def add(self,point:PricePoint):
        if point.instrument!=self.instrument:raise ContractError("roll requires a new directional-change state")
        if point.id in self.seen:
            if self.seen[point.id]!=digest(point):raise IntegrityError("directional-change event ID changed")
            return ()
        if self.last and (point.known_at<self.last.known_at or point.event_at<self.last.event_at):raise ContractError("late path needs an explicit corrected version, not a historical swing rewrite")
        if self.last and point.event_at==self.last.event_at and (point.order is None or self.last.order is None or point.order<=self.last.order):
            raise DependencyUnavailable("unknown same-time path order cannot confirm a directional change")
        if len(self.seen)>=100000:raise ContractError("directional-change reference retention bound reached")
        self.seen[point.id]=digest(point);self.last=point
        if not point.complete:
            self.high=self.low=None;self.direction=0;return ()
        if self.high is None:self.high=self.low=point;return ()
        if point.ticks>self.high.ticks:self.high=point
        if point.ticks<self.low.ticks:self.low=point
        swing=None
        if self.direction>=0 and self.high.ticks-point.ticks>=self.threshold:
            extreme=self.high;swing=self._swing(extreme,'high',point);self.direction=-1;self.low=point;self.high=point
        elif self.direction<=0 and point.ticks-self.low.ticks>=self.threshold:
            extreme=self.low;swing=self._swing(extreme,'low',point);self.direction=1;self.high=point;self.low=point
        if swing:self.confirmed.append(swing);return (swing,)
        return ()

    def _swing(self,extreme,side,confirmation):
        return Swing(digest([self.definition,extreme.id,side,confirmation.id]),self.instrument,side,extreme.ticks,extreme.event_at,extreme.event_at,
                     max(extreme.known_at,confirmation.known_at),(extreme.id,confirmation.id),self.definition,'confirmed')

    def checkpoint(self):
        return canonical_json({'schema':'directional-change-reference-v1','instrument':self.instrument,'threshold':self.threshold,'definition':self.definition,'direction':self.direction,
                               'high':None if self.high is None else asdict(self.high),'low':None if self.low is None else asdict(self.low),'last':None if self.last is None else asdict(self.last),
                               'seen':self.seen,'confirmed':[asdict(s) for s in self.confirmed]})

    @classmethod
    def restore(cls,payload):
        p=json.loads(payload)
        if p['schema']!='directional-change-reference-v1':raise ContractError("incompatible swing checkpoint")
        result=cls(instrument=p['instrument'],threshold_ticks=p['threshold'],definition_version=p['definition']);result.direction=p['direction'];result.seen=p['seen']
        for name in ('high','low','last'):setattr(result,name,None if p[name] is None else PricePoint(**p[name]))
        result.confirmed=[Swing(**{**s,'source_versions':tuple(s['source_versions'])}) for s in p['confirmed']]
        if result.checkpoint()!=payload or result.direction not in (-1,0,1):raise IntegrityError("invalid directional-change checkpoint")
        for point in (result.high,result.low,result.last):
            if point and result.seen.get(point.id)!=digest(point):raise IntegrityError("swing checkpoint omits its live extreme evidence")
        return result


def retracement(low:int,high:int,fraction:Fraction):
    if type(low) is not int or type(high) is not int or high<low or not isinstance(fraction,Fraction):raise ContractError("exact ordered tick anchors required")
    return Fraction(low)+fraction*(high-low)


@dataclass(frozen=True)
class DivergenceAnchor:
    id:str
    instrument:str
    trading_date:str
    extreme_at:int
    known_at:int
    price:Fraction
    flow:Fraction|None
    side:str
    comparator:str


def divergence(a:DivergenceAnchor,b:DivergenceAnchor,*,cut:int,price_scale:Fraction,flow_scale:Fraction):
    if a.instrument!=b.instrument or a.trading_date!=b.trading_date or a.side!=b.side or a.comparator!=b.comparator or a.extreme_at>=b.extreme_at:
        raise ContractError("divergence must compare previously declared ordered compatible anchors")
    if max(a.known_at,b.known_at)>cut or a.flow is None or b.flow is None:raise DependencyUnavailable("anchor flow/confirmation unavailable at cut")
    if price_scale<=0 or flow_scale<=0:raise ContractError("normalization requires preceding positive price/flow scales")
    dp=b.price-a.price;df=b.flow-a.flow;high=a.side=='high'
    if a.side not in ('high','low'):raise ContractError("divergence anchor must identify high or low")
    regular=(dp>0 and df<0) if high else (dp<0 and df>0)
    hidden=(dp<0 and df>0) if high else (dp>0 and df<0)
    return {'anchors':(a.id,b.id),'known_at':max(a.known_at,b.known_at),'price_change':dp/price_scale,'flow_change':df/flow_scale,
            'regular':regular,'hidden':hidden,'tie':dp==0 or df==0,'interpretation':'Observed anchor disagreement; no reversal or held-inventory conclusion.'}


from dataclasses import field, replace
from itertools import groupby
from trading_research.foundations.multiresolution import SharedBarEngine
from trading_research.measurements.common import CapturedTradeWindow, bounded_name, bounded_rows, positive_limit, validate_trade_window


@dataclass(frozen=True)
class SwingBarCapture:
    publication_ids: tuple
    bars: tuple
    requests: tuple
    cut: int
    published_at: int
    definition_version: str
    max_inputs: int
    max_bytes: int
    _engine: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {"publication_ids": self.publication_ids, "bars": tuple(b.record() for b in self.bars),
            "requests": self.requests, "cut": self.cut, "published_at": self.published_at,
            "definition_version": self.definition_version, "max_inputs": self.max_inputs, "max_bytes": self.max_bytes}

    @property
    def id(self):
        return digest(self.record())


def capture_swing_bars(*, engine, publication_ids, cut, published_at, definition_version,
                       max_inputs=4096, max_bytes=8388608):
    bounded_rows(publication_ids, max_inputs, name="swing source publications")
    positive_limit(max_bytes)
    timestamp(cut)
    timestamp(published_at)
    bounded_name(definition_version)
    if type(engine) is not SharedBarEngine or published_at < cut:
        raise ContractError("swing bars require an actual engine and causal publication")
    if len(set(publication_ids)) != len(publication_ids):
        raise ContractError("duplicate swing publication recipe")
    latest = {}
    for identity in publication_ids:
        bar, request = engine.window_publication(identity)
        if bar.definition.kind != "time" or bar.published_at > cut:
            raise ContractError("swing input must be an available actual time publication")
        old = latest.get(bar.bar_id)
        if old is None or (bar.published_at, bar.revision) > (old[0].published_at, old[0].revision):
            latest[bar.bar_id] = (bar, request)
    rows = sorted(latest.values(), key=lambda pair: pair[0].interval)
    if len({(b.definition.id, b.reset_epoch) for b, _ in rows}) > 1:
        raise ContractError("swing window crosses raw domain, clock, definition or reset")
    if any(a[0].interval[1] > b[0].interval[0] for a, b in zip(rows, rows[1:])):
        raise ContractError("swing bars contain overlapping incompatible windows")
    result = SwingBarCapture(tuple(publication_ids), tuple(b for b, _ in rows), tuple(r for _, r in rows),
                              cut, published_at, definition_version, max_inputs, max_bytes)
    object.__setattr__(result, "_engine", engine)
    if len(canonical_json(result.record())) > max_bytes:
        raise ContractError("swing capture byte capacity exhausted")
    return result


def validate_swing_bars(capture):
    if type(capture) is not SwingBarCapture:
        raise ContractError("detached bars cannot certify a swing capture")
    fresh = capture_swing_bars(engine=capture._engine, **{k: getattr(capture, k) for k in (
        "publication_ids", "cut", "published_at", "definition_version", "max_inputs", "max_bytes")})
    if fresh != capture:
        raise IntegrityError("swing bars differ from their retained F09 publications")


@dataclass(frozen=True)
class SwingScale:
    capture_id: str
    value: Fraction
    known_at: int
    recipe: str
    _capture: object = field(default=None, init=False, compare=False, repr=False)


def swing_scale(capture, *, recipe="mean_true_range"):
    validate_swing_bars(capture)
    if recipe != "mean_true_range" or not capture.bars:
        raise ContractError("swing scale requires an explicit supported preceding bar recipe")
    previous, ranges = None, []
    for b in capture.bars:
        if not b.final or not b.coverage_complete or any(getattr(b.summary,k) is None for k in ('high_ticks','low_ticks','close_ticks')):
            raise DependencyUnavailable("scale requires complete preceding raw bar geometry")
        s = b.summary
        ranges.append(max(s.high_ticks - s.low_ticks, 0 if previous is None else abs(s.high_ticks - previous),
                          0 if previous is None else abs(s.low_ticks - previous)))
        previous = s.close_ticks
    value = Fraction(sum(ranges), len(ranges))
    if value <= 0:
        raise DependencyUnavailable("zero volatility cannot define a positive reversal threshold")
    result = SwingScale(capture.id, value, capture.published_at, recipe)
    object.__setattr__(result, "_capture", capture)
    return result


@dataclass(frozen=True)
class SwingDefinition:
    version: str
    kind: str = "directional_change"
    left: int = 1
    right: int = 1
    ties: str = "strict"
    reversal_ticks: Fraction = Fraction(2)
    scale_version: str | None = None
    scale_known_at: int | None = None
    frozen_at: int = 0
    max_age_ns: int = 86400000000000
    scale: SwingScale | None = None
    subsequent_scales: tuple = ()

    def __post_init__(self):
        bounded_name(self.version)
        timestamp(self.frozen_at)
        positive_limit(self.max_age_ns)
        if self.kind not in ("pivot", "directional_change") or self.ties not in ("strict", "earliest", "latest", "ambiguous"):
            raise ContractError("unknown swing definition or equality rule")
        if any(type(v) is not int or not 1 <= v <= 1000 for v in (self.left, self.right)):
            raise ContractError("swing pivot lengths exceed the finite recipe")
        if type(self.reversal_ticks) not in (int, Fraction) or self.reversal_ticks <= 0:
            raise ContractError("swing threshold needs positive exact ticks")
        bounded_rows(self.subsequent_scales, 32, name="subsequent swing scales")
        if type(self.subsequent_scales) is not tuple:
            raise ContractError("subsequent swing scales must be an immutable sequence")
        if self.scale is None and (self.scale_version is not None or self.scale_known_at is not None):
            raise ContractError("a scale string cannot replace actual preceding bar evidence")
        for scale in ((self.scale,) if self.scale is not None else ()) + self.subsequent_scales:
            if type(scale) is not SwingScale or swing_scale(scale._capture, recipe=scale.recipe) != scale:
                raise IntegrityError("swing scale differs from actual preceding bars")
        if self.scale is not None and (self.scale_version, self.scale_known_at) != (self.scale.capture_id, self.scale.known_at):
            raise ContractError("swing scale metadata differs from its actual capture")

    @property
    def id(self):
        return digest({k: getattr(self, k) for k in self.__dataclass_fields__ if k not in ("scale", "subsequent_scales")} | {
            "scales": tuple((s.capture_id, s.value, s.known_at, s.recipe) for s in
                            ((self.scale,) if self.scale else ()) + self.subsequent_scales)})


@dataclass(frozen=True)
class ObservedSwing:
    id: str
    side: str
    price_ticks: int
    extreme_start: int
    extreme_end: int
    extreme_source: str
    origin_at: int
    origin_ticks: int
    confirmation_event_at: int
    confirmed_at: int
    confirmation_ticks: int | None
    threshold: Fraction
    source_versions: tuple
    definition_id: str
    status: str

    @property
    def prominence(self):
        return abs(Fraction(self.price_ticks - self.origin_ticks)) / self.threshold

    @property
    def confirmation_cost(self):
        return None if self.confirmation_ticks is None else abs(self.confirmation_ticks - self.price_ticks)

    @property
    def confirmation_delay(self):
        return self.confirmed_at - self.extreme_end


@dataclass(frozen=True)
class SwingSnapshot:
    capture_id: str
    instrument: str
    reset_id: str
    definition_id: str
    cut: int
    published_at: int
    confirmed: tuple
    provisional: tuple
    order_exact: bool
    source_versions: tuple
    work: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())


def swing_snapshot(capture, *, definition, view=None):
    if type(definition) is not SwingDefinition:
        raise ContractError("typed frozen swing definition required")
    definition.__post_init__()
    confirmed, provisional, visits = [], [], 0
    if type(capture) is SwingBarCapture:
        validate_swing_bars(capture)
        if definition.kind != "pivot":
            raise DependencyUnavailable("OHLC bars do not certify intrabar directional-change order")
        bars, cut, published = capture.bars, capture.cut, capture.published_at
        instrument = bars[0].definition.domain.instrument if bars else capture._engine.domain.instrument
        reset = bars[0].definition.reset_id if bars else capture.definition_version
        start = bars[0].interval[0] if bars else cut
        sources = tuple(b.version_id for b in bars)
        exact = all(b.summary.order_exact for b in bars)
        for i in range(definition.left, len(bars) - definition.right):
            window = bars[i-definition.left:i+definition.right+1]
            visits += len(window)
            if (any(not b.final or not b.coverage_complete or b.summary.high_ticks is None for b in window)
                    or any(a.interval[1] != b.interval[0] for a, b in zip(window, window[1:]))):
                continue
            center = bars[i]
            for side, name, extreme in (("high", "high_ticks", max), ("low", "low_ticks", min)):
                prices = [getattr(b.summary, name) for b in window]
                price = getattr(center.summary, name)
                equal = [j for j, p in enumerate(prices) if p == price]
                if price != extreme(prices) or definition.ties == "strict" and len(equal) > 1:
                    continue
                if definition.ties == "earliest" and equal[0] != definition.left or definition.ties == "latest" and equal[-1] != definition.left:
                    continue
                known = max(b.published_at for b in window)
                sid = digest((definition.id, center.bar_id, side, tuple(b.version_id for b in window)))
                confirmed.append(ObservedSwing(sid, side, price, *center.interval, center.version_id,
                    window[0].interval[0], window[0].summary.low_ticks if side == "high" else window[0].summary.high_ticks,
                    window[-1].interval[1], known, window[-1].summary.close_ticks,
                    Fraction(definition.reversal_ticks), tuple(b.version_id for b in window), definition.id,
                    "ambiguous_equal_extremum" if definition.ties == "ambiguous" and len(equal) > 1 else "confirmed"))
    elif type(capture) is CapturedTradeWindow:
        validate_trade_window(capture, view)
        if definition.kind != "directional_change":
            raise ContractError("bar-count pivots require certified time-bar publications")
        w = capture.window
        cut, published, instrument, reset, start = w.cut, w.published_at, w.instrument, w.definition_version, w.start
        sources, exact = w.source_versions, w.order_exact
        if definition.scale is not None and definition.scale.known_at > start:
            raise ContractError("initial swing scale must be known before leg birth")
        threshold = Fraction(definition.reversal_ticks) * (definition.scale.value if definition.scale else 1)
        direction, high, low, origin, last_at = 0, None, None, None, None
        for _, group in groupby(capture.trades, key=lambda t: t.event_at):
            batch = tuple(group)
            visits += len(batch)
            ordered = len(batch) == 1 or all(t.order is not None for t in batch) and len({t.order for t in batch}) == len(batch)
            for t in batch:
                gap = last_at is not None and not any(a <= last_at <= t.event_at <= b for a, b in w.coverage.observed_intervals)
                last_at = t.event_at
                if gap:
                    direction, high, low, origin = 0, None, None, None
                if t.price is None or not t.history_complete or not ordered:
                    direction, high, low, origin = 0, None, None, None
                    continue
                if high is None:
                    high = low = origin = t
                    continue
                if t.price.value > high.price.value:
                    high = t
                if t.price.value < low.price.value:
                    low = t
                side = "high" if direction >= 0 and high.price.value - t.price.value >= threshold else (
                    "low" if direction <= 0 and t.price.value - low.price.value >= threshold else None)
                if side:
                    extreme = high if side == "high" else low
                    sid = digest((definition.id, extreme.id, t.id, side))
                    confirmed.append(ObservedSwing(sid, side, extreme.price.value, extreme.event_at, extreme.event_at,
                        extreme.id, origin.event_at, origin.price.value, t.event_at, max(extreme.known_at, t.known_at),
                        t.price.value, threshold, (origin.source_content_version, extreme.source_content_version,
                                                t.source_content_version), definition.id, "confirmed"))
                    initial_confirmation = direction == 0
                    direction = -1 if side == "high" else 1
                    origin, high, low = extreme, t, t
                    if not initial_confirmation:
                        available = [s for s in definition.subsequent_scales if s.known_at <= t.known_at]
                        if available:
                            threshold = Fraction(definition.reversal_ticks) * max(available, key=lambda s: s.known_at).value
        if high is not None:
            for side, t in (("high", high), ("low", low)):
                if direction == 0 or side == ("high" if direction > 0 else "low"):
                    provisional.append((side, t.price.value, t.event_at, t.id, threshold))
    else:
        raise ContractError("swing snapshot requires actual trade or shared-bar captures")
    if definition.frozen_at > start:
        raise ContractError("swing rule must be frozen before the measured path")
    if len(confirmed) > 1024:
        raise ContractError("swing version capacity exhausted")
    confirmed = tuple(s for s in confirmed if cut - s.extreme_start <= definition.max_age_ns)
    result = SwingSnapshot(capture.id, instrument, reset, definition.id, cut, published, confirmed, tuple(provisional),
                           exact, sources, (("source_visits", visits), ("source_records_hashed", len(sources))))
    object.__setattr__(result, "_recipe", (capture, definition, view))
    return result


def validate_swing_snapshot(snapshot):
    if type(snapshot) is not SwingSnapshot or type(snapshot._recipe) is not tuple:
        raise ContractError("actual swing recipe required")
    capture, definition, view = snapshot._recipe
    if swing_snapshot(capture, definition=definition, view=view) != snapshot:
        raise IntegrityError("swing result differs from its actual source recipe")


class SwingTree(dict):
    __slots__ = ('_recipe',)


def validate_swing_tree(tree):
    seen, node = set(), tree
    while node is not None:
        if type(node) is not SwingTree or id(node) in seen or len(seen) >= 1024:
            raise ContractError("swing predecessor history must be actual, bounded and acyclic")
        seen.add(id(node))
        if type(node._recipe) is not dict or _make_swing_tree(**node._recipe) != node:
            raise IntegrityError("swing tree differs from its actual source and predecessor recipe")
        node = node._recipe['previous']


def multiscale_swing_tree(capture, *, definitions, view=None, previous=None, max_scales=32):
    if previous is not None:
        validate_swing_tree(previous)
    return _make_swing_tree(capture, definitions=definitions, view=view, previous=previous, max_scales=max_scales)


def _make_swing_tree(capture, *, definitions, view=None, previous=None, max_scales=32):
    bounded_rows(definitions, max_scales, name="swing scales")
    if not definitions or len({d.id for d in definitions}) != len(definitions):
        raise ContractError("multiscale tree needs distinct frozen definitions")
    snapshots = tuple(swing_snapshot(capture, definition=d, view=view) for d in definitions)
    rows = [(s, n) for s in snapshots for n in s.confirmed]
    if len(rows) > 1024:
        raise ContractError("multiscale retained node capacity exhausted")
    nodes = []
    for snapshot, n in rows:
        persistence = tuple(sorted(s.definition_id for s, other in rows
            if other.extreme_source == n.extreme_source and other.side == n.side))
        parents = [(other.threshold, other.confirmed_at, other.id) for _, other in rows
            if other.threshold > n.threshold and other.side == n.side
            and other.origin_at <= n.origin_at and other.extreme_end >= n.extreme_end]
        parent = min(parents)[2] if parents else None
        provisional_parent = None
        if parent is None:
            candidates = [(p[4], s.definition_id) for s in snapshots for p in s.provisional
                          if p[0] == n.side and p[4] > n.threshold and p[2] >= n.extreme_end]
            provisional_parent = min(candidates)[1] if candidates else None
        nodes.append({"swing": n, "snapshot_id": snapshot.id, "persistence_scales": persistence,
            "persistence": len(persistence), "parent": parent, "provisional_parent": provisional_parent,
            "relation_known_at": snapshot.published_at, "prominence": n.prominence,
            "confirmation_cost": n.confirmation_cost, "confirmation_delay": n.confirmation_delay})
    by_id = {r["swing"].id: r for r in nodes}
    for row in nodes:
        depth, parent = 0, row["parent"]
        while parent is not None:
            depth += 1
            if depth > len(nodes):
                raise IntegrityError("swing parent cycle")
            parent = by_id[parent]["parent"]
        row["nesting_depth"] = depth
    result = {"capture_id": capture.id, "snapshots": tuple(s.record() for s in snapshots), "nodes": tuple(nodes),
        "previous_version": None if previous is None else previous["version_id"],
        "published_at": snapshots[0].published_at, "known_at": snapshots[0].published_at}
    result["version_id"] = digest(result)
    tree = SwingTree(result)
    tree._recipe = dict(capture=capture, definitions=tuple(definitions), view=view, previous=previous, max_scales=max_scales)
    return tree


class SwingBook:
    def __init__(self, *, instrument, definition_ids, max_versions=1024, max_bytes=8388608):
        bounded_name(instrument)
        bounded_rows(definition_ids, 32, name="swing book definitions")
        self.instrument, self.definition_ids = instrument, tuple(definition_ids)
        self.max_versions, self.max_bytes = positive_limit(max_versions), positive_limit(max_bytes)
        self._recipes, self._versions = [], []
        self._sealed = self._state_bytes()

    def advance(self, capture, definitions, *, view=None):
        self.checkpoint()
        if tuple(d.id for d in definitions) != self.definition_ids:
            raise ContractError("swing book definition changed without a reset")
        if len(self._versions) >= self.max_versions:
            raise ContractError("swing book capacity requires explicit archival")
        previous = self._versions[-1] if self._versions else None
        staged = multiscale_swing_tree(capture, definitions=definitions, view=view, previous=previous)
        if any(s["instrument"] != self.instrument for s in staged["snapshots"]):
            raise ContractError("swing book cannot cross a raw contract")
        if previous is not None and staged["published_at"] <= previous["published_at"]:
            raise ContractError("swing revisions require increasing actual publication")
        if len(canonical_json((*self._versions, staged))) > self.max_bytes:
            raise ContractError("swing book retained bytes exhausted")
        self._recipes.append((capture, tuple(definitions), view))
        self._versions.append(staged)
        raw = self._state_bytes()
        if len(raw) > self.max_bytes:
            self._recipes.pop(); self._versions.pop()
            raise ContractError("swing full checkpoint byte capacity exhausted")
        self._sealed = raw
        return staged

    def _state_bytes(self):
        return canonical_json({"schema": "measurement-swing-book-v1", "instrument": self.instrument,
            "definition_ids": self.definition_ids, "max_versions": self.max_versions, "max_bytes": self.max_bytes,
            "versions": self._versions, "capture_ids": tuple(r[0].id for r in self._recipes)})

    def checkpoint(self):
        if self._state_bytes() != self._sealed or len(self._recipes) != len(self._versions):
            raise IntegrityError("swing book changed outside actual source replay")
        if len(self._sealed) > self.max_bytes:
            raise ContractError("swing checkpoint byte capacity exhausted")
        return self._sealed

    @classmethod
    def restore(cls, payload, *, recipes, instrument, definition_ids, max_versions=1024, max_bytes=8388608):
        bounded_rows(recipes, max_versions, name="swing restoration recipes")
        if type(payload) is not bytes or len(payload) > positive_limit(max_bytes):
            raise ContractError("swing restore exceeds bounded bytes")
        result = cls(instrument=instrument, definition_ids=definition_ids, max_versions=max_versions, max_bytes=max_bytes)
        for capture, definitions, view in recipes:
            result.advance(capture, definitions, view=view)
        if result.checkpoint() != payload:
            raise IntegrityError("swing checkpoint differs from complete bounded replay or predecessors")
        return result
