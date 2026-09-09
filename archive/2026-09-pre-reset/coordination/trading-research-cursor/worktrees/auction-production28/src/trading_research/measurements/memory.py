"""Observed historical effort, immutable clusters and separate future labels."""

from dataclasses import dataclass, field
from fractions import Fraction
from contextvars import ContextVar

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import timestamp
from trading_research.measurements.common import bounded_name, bounded_rows, positive_limit, validate_trade_window
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class MemoryDefinition:
    version: str
    minimum_size: int = 1
    price_radius_ticks: int = 0
    time_radius_ns: int = 0
    cohort_definition: str = "reported_aggressor"
    spatial_grid: tuple = ()
    spatial_kernel: str = "point"
    decay_clock: str = "time"
    decay_scale: Fraction = Fraction(1)
    max_age_ns: int = 86400000000000
    strict_size: bool = False
    spatial_radius_ticks: int = 1
    decay_kernel: str = "half_life"
    frozen_at: int = 0
    max_inputs: int = 4096
    max_clusters: int = 1024
    max_cells: int = 4096
    max_bytes: int = 8388608

    def __post_init__(self):
        bounded_name(self.version)
        positive_limit(self.minimum_size)
        for value in (self.max_inputs, self.max_clusters, self.max_cells, self.max_bytes, self.max_age_ns):
            positive_limit(value)
        for value in (self.price_radius_ticks, self.time_radius_ns, self.spatial_radius_ticks):
            if type(value) is not int or value < 0:
                raise ContractError("memory radii must be exact nonnegative units")
        bounded_rows(self.spatial_grid, self.max_cells, name="memory spatial grid")
        if (type(self.spatial_grid) is not tuple or tuple(sorted(set(self.spatial_grid))) != self.spatial_grid
                or any(type(p) is not int for p in self.spatial_grid) or type(self.strict_size) is not bool):
            raise ContractError("memory requires immutable increasing exact grid and threshold convention")
        if self.spatial_grid and any(b-a != 1 for a, b in zip(self.spatial_grid, self.spatial_grid[1:])):
            raise ContractError("memory triangular grid is a contiguous raw-tick grid")
        if (self.spatial_kernel not in ("point", "triangular") or self.decay_clock not in ("time", "volume", "visits")
                or self.decay_kernel not in ("half_life", "box") or type(self.decay_scale) not in (int, Fraction)
                or self.decay_scale <= 0 or self.cohort_definition != "reported_aggressor"):
            raise ContractError("memory requires an explicit supported whole-print metric and decay recipe")
        if 2*self.spatial_radius_ticks + 1 > self.max_cells:
            raise ContractError("memory kernel support exceeds its spatial capacity")
        timestamp(self.frozen_at)

    @property
    def id(self):
        return digest(self)


@dataclass(frozen=True)
class MemoryCluster:
    id: str
    member_ids: tuple
    member_versions: tuple
    side: int | None
    center_ticks: Fraction
    low_ticks: int
    high_ticks: int
    first_at: int
    last_at: int
    gross: int
    raw_count: int
    predecessors: tuple


@dataclass(frozen=True)
class MemorySnapshot:
    instrument: str
    aggregation_unit: str
    definition: MemoryDefinition
    cut: int
    published_at: int
    source_capture_ids: tuple
    clusters: tuple
    field_cells: tuple
    overflow: tuple
    raw_mass: tuple
    decayed_mass: tuple
    history_complete: bool
    order_exact: bool
    predecessor_id: str | None
    work: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())


def _union_captures(captures, views, limit):
    bounded_rows(captures, 256, name="memory source windows")
    bounded_rows(views, 256, name="memory source views")
    if not captures or len(captures) != len(views):
        raise ContractError("one actual source view per memory capture required")
    by = {}
    count = 0
    for capture, view in zip(captures, views):
        validate_trade_window(capture, view)
        for trade in capture.trades:
            count += 1
            if trade.id in by and by[trade.id] != trade:
                raise IntegrityError("overlapping memory windows disagree on a whole-print revision")
            by[trade.id] = trade
            if len(by) > limit:
                raise ContractError("memory whole-print union capacity exhausted")
    return tuple(sorted(by.values(), key=lambda t: (t.event_at, -1 if t.order is None else t.order, t.id))), count


def build_memory(captures, *, views, definition, cut, published_at, previous=None, profile=None, visits=None):
    if type(definition) is not MemoryDefinition:
        raise ContractError("typed memory definition required")
    definition.__post_init__()
    timestamp(cut)
    timestamp(published_at)
    if published_at < cut:
        raise ContractError("memory publication predates its input cut")
    trades, source_visits = _union_captures(captures, views, definition.max_inputs)
    w = captures[0].window
    if any((c.window.instrument, c.window.aggregation_unit, c.window.definition_version) !=
           (w.instrument, w.aggregation_unit, w.definition_version) or c.window.cut > cut
           or c.window.published_at > published_at or definition.frozen_at > c.window.start for c in captures):
        raise ContractError("memory captures differ in raw/reset/whole-print definition or availability")
    if profile is not None:
        from trading_research.measurements.profiles import validate_profile
        validate_profile(profile)
        if profile.instrument != w.instrument:
            raise ContractError("memory profile support has a different raw domain")
    if previous is not None:
        validate_memory(previous)
        if (previous.instrument != w.instrument or previous.definition != definition
                or previous.published_at >= published_at):
            raise ContractError("memory revision needs a compatible earlier predecessor")
    if visits is not None:
        validate_memory_visits(visits)
        if previous is None or visits.memory_id != previous.id or visits.published_at > published_at:
            raise ContractError("visit decay must bind the actual preceding memory episode")
    selected = tuple(t for t in trades if t.price is not None and cut-t.event_at <= definition.max_age_ns
                     and (t.size > definition.minimum_size if definition.strict_size else t.size >= definition.minimum_size))
    n, comparisons = len(selected), 0
    parent = list(range(n))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, a in enumerate(selected):
        for j in range(i):
            b = selected[j]
            comparisons += 1
            if (a.side == b.side and a.event_at-b.event_at <= definition.time_radius_ns
                    and abs(a.price.value-b.price.value) <= definition.price_radius_ticks):
                ra, rb = root(i), root(j)
                parent[max(ra, rb)] = min(ra, rb)
    components = {}
    for i, t in enumerate(selected):
        components.setdefault(root(i), []).append(t)
    if len(components) > definition.max_clusters:
        raise ContractError("memory cluster capacity exhausted")
    clusters = []
    for members in components.values():
        ids = tuple(sorted(t.id for t in members))
        versions = tuple(sorted((t.id, t.source_content_version) for t in members))
        quantity = sum(t.size for t in members)
        predecessors = () if previous is None else tuple(sorted(c.id for c in previous.clusters if set(c.member_ids) & set(ids)))
        clusters.append(MemoryCluster(digest((definition.id, versions)), ids, versions, members[0].side,
            Fraction(sum(t.size*t.price.value for t in members), quantity), min(t.price.value for t in members),
            max(t.price.value for t in members), min(t.event_at for t in members), max(t.event_at for t in members),
            quantity, len(members), predecessors))
    clusters.sort(key=lambda c: (c.first_at, c.low_ticks, c.id))
    complete = all(c.window.history_complete for c in captures)
    exact = all(c.window.order_exact for c in captures)
    raw, decayed = [0, 0, 0], [0, 0, 0]
    cells = {p: [[Fraction(0)] * 3, [0] * 3] for p in definition.spatial_grid}
    overflow = [[Fraction(0)] * 3, [0] * 3]
    operations = 0
    for t in selected:
        channel = 0 if t.side == 1 else 1 if t.side == -1 else 2
        raw[channel] += t.size
        if definition.decay_clock == "time":
            age = cut-t.event_at
        elif definition.decay_clock == "volume":
            age = sum(other.size for other in trades if other.event_at > t.event_at) if exact and complete else None
            operations += len(trades)
        else:
            age = visits.retests if visits is not None and exact and complete else None
        weight = None if age is None else (int(age <= definition.decay_scale) if definition.decay_kernel == "box"
                                          else 2 ** (-float(Fraction(age, definition.decay_scale))))
        if weight is None:
            decayed[channel] = None
        elif decayed[channel] is not None:
            decayed[channel] += t.size*weight
        radius = 0 if definition.spatial_kernel == "point" else definition.spatial_radius_ticks
        denominator = (radius+1)**2
        for p in range(t.price.value-radius, t.price.value+radius+1):
            operations += 1
            spatial = Fraction(radius+1-abs(p-t.price.value), denominator)
            target = cells[p] if p in cells else overflow
            target[0][channel] += t.size*spatial
            if weight is None:
                target[1][channel] = None
            elif target[1][channel] is not None:
                target[1][channel] += t.size*spatial*weight
    if any(sum(cell[0][i] for cell in cells.values())+overflow[0][i] != raw[i] for i in range(3)):
        raise IntegrityError("memory spatial kernel failed raw-mass conservation")
    result = MemorySnapshot(w.instrument, w.aggregation_unit, definition, cut, published_at,
        tuple(c.id for c in captures), tuple(clusters), tuple((p, tuple(v[0]), tuple(v[1])) for p, v in cells.items()),
        (tuple(overflow[0]), tuple(overflow[1])), tuple(raw), tuple(decayed), complete, exact,
        None if previous is None else previous.id, (("source_visits", source_visits), ("cluster_comparisons", comparisons),
                                                    ("kernel_operations", operations)))
    if len(canonical_json(result.record())) > definition.max_bytes:
        raise ContractError("memory retained result bytes exhausted")
    object.__setattr__(result, "_recipe", dict(captures=tuple(captures), views=tuple(views), definition=definition,
        cut=cut, published_at=published_at, previous=previous, profile=profile, visits=visits))
    return result


_validated_memories = ContextVar('measurement_memory_validation', default=None)


def validate_memory(memory):
    if type(memory) is not MemorySnapshot or type(memory._recipe) is not dict:
        raise ContractError("actual historical-memory recipe required")
    checked = _validated_memories.get()
    if checked is not None and id(memory) in checked:
        return
    chain, seen, node = [], set(), memory
    while node is not None and (checked is None or id(node) not in checked):
        if (type(node) is not MemorySnapshot or type(node._recipe) is not dict
                or id(node) in seen or len(chain) >= 1024):
            raise ContractError("memory predecessor chain must be bounded and acyclic")
        seen.add(id(node)); chain.append(node)
        node = node._recipe.get('previous')
    token = _validated_memories.set(set() if checked is None else checked)
    try:
        for node in reversed(chain):
            if build_memory(**node._recipe) != node:
                raise IntegrityError("memory differs from its retained actual whole-print sources")
            _validated_memories.get().add(id(node))
    finally:
        _validated_memories.reset(token)


@dataclass(frozen=True)
class MemoryVisits:
    memory_id: str
    cluster_id: str
    visits: int
    retests: int
    arrivals: tuple
    departures: tuple
    time_away: tuple
    new_flow: int
    new_source_ids: tuple
    published_at: int
    order_exact: bool
    _recipe: object = field(default=None, init=False, compare=False, repr=False)


def observe_memory_visits(memory, *, cluster_id, price_capture, view, definition):
    validate_memory(memory)
    validate_trade_window(price_capture, view)
    if type(definition) is not tuple or len(definition) != 3:
        raise ContractError("visit definition needs version, hysteresis ticks and minimum time away")
    bounded_name(definition[0])
    if any(type(v) is not int or v < 0 for v in definition[1:]):
        raise ContractError("visit hysteresis and time-away must be exact nonnegative units")
    matches = [c for c in memory.clusters if c.id == cluster_id]
    if len(matches) != 1 or price_capture.window.instrument != memory.instrument:
        raise ContractError("visit must bind one actual frozen memory cluster")
    c, w = matches[0], price_capture.window
    if w.cut < memory.cut or w.published_at < memory.published_at:
        raise ContractError("visit cannot precede the memory it observes")
    inside, left_at = False, None
    arrivals, departures, away, new = [], [], [], {}
    for t in price_capture.trades:
        if t.price is None or t.event_at < c.first_at:
            continue
        p = t.price.value
        in_band = c.low_ticks-definition[1] <= p <= c.high_ticks+definition[1]
        if in_band and not inside:
            if left_at is None or t.event_at-left_at >= definition[2]:
                arrivals.append((t.event_at, t.known_at, t.id))
                if left_at is not None:
                    away.append(t.event_at-left_at)
            inside = True
        elif not in_band and inside:
            departures.append((t.event_at, t.known_at, t.id))
            left_at, inside = t.event_at, False
        qualifies = (t.size > memory.definition.minimum_size if memory.definition.strict_size
                     else t.size >= memory.definition.minimum_size)
        if in_band and qualifies and t.id not in c.member_ids and t.event_at > c.last_at:
            new[t.id] = t.size
    exact = w.order_exact and w.history_complete and not w.unpriced_volume
    result = MemoryVisits(memory.id, c.id, len(arrivals), max(0, len(arrivals)-1), tuple(arrivals), tuple(departures),
        tuple(away), sum(new.values()), tuple(sorted(new)), w.published_at, exact)
    object.__setattr__(result, "_recipe", dict(memory=memory, cluster_id=cluster_id, price_capture=price_capture,
                                              view=view, definition=definition))
    return result


def validate_memory_visits(visits):
    if type(visits) is not MemoryVisits or type(visits._recipe) is not dict or observe_memory_visits(**visits._recipe) != visits:
        raise IntegrityError("memory visits differ from the actual chronological price recipe")


@dataclass(frozen=True)
class MemoryMarkout:
    memory_id: str
    cluster_id: str
    horizon_end: int
    earliest_known_at: int
    published_at: int
    status: str
    terminal_markout: Fraction | None
    mfe: Fraction | None
    mae: Fraction | None
    observed_mfe: Fraction
    observed_mae: Fraction
    source_ids: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    @property
    def id(self):
        return digest({k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"})


def markout(memory, *, cluster_id, future_capture, future_view, horizon_end,
            observation_definition, cut, published_at):
    validate_memory(memory)
    validate_trade_window(future_capture, future_view)
    for at in (horizon_end, cut, published_at):
        timestamp(at)
    bounded_name(observation_definition)
    matches = [c for c in memory.clusters if c.id == cluster_id]
    if len(matches) != 1:
        raise ContractError("memory markout must bind its original cluster")
    cluster, w = matches[0], future_capture.window
    if (w.instrument != memory.instrument or horizon_end <= memory.published_at or published_at < cut
            or w.start > memory.published_at):
        raise ContractError("memory markout domain, origin or horizon differs")
    available_points = tuple(t for t in future_capture.trades
                             if memory.published_at < t.event_at <= horizon_end and t.price is not None)
    points = tuple(t for t in available_points if t.known_at <= cut and t.event_at <= cut)
    if w.published_at > cut:
        points = ()
    side = cluster.side
    values = [Fraction(0)] if side is None else [Fraction(0), *(side*(t.price.value-cluster.center_ticks) for t in points)]
    maturity = max(horizon_end, w.published_at, w.coverage.known_at, *(t.known_at for t in available_points))
    covered = any(a <= memory.published_at and b >= horizon_end for a, b in w.coverage.observed_intervals)
    complete = covered and w.history_complete and not w.unpriced_volume and w.end >= horizon_end
    status = "pending" if cut < maturity else "unavailable" if not complete or side is None else "mature"
    terminal = values[-1] if status == "mature" else None
    if status == "mature" and not w.order_exact and points:
        tail = {t.price.value for t in points if t.event_at == points[-1].event_at}
        if len(tail) > 1:
            status, terminal = "ambiguous", None
    result = MemoryMarkout(memory.id, cluster.id, horizon_end, maturity, published_at, status, terminal,
        max(values) if complete and side is not None and cut >= maturity else None,
        min(values) if complete and side is not None and cut >= maturity else None,
        max(values), min(values), tuple((t.id, t.source_content_version) for t in points))
    object.__setattr__(result, "_recipe", dict(memory=memory, cluster_id=cluster_id, future_capture=future_capture,
        future_view=future_view, horizon_end=horizon_end, observation_definition=observation_definition,
        cut=cut, published_at=published_at))
    return result


def validate_memory_markout(label):
    if type(label) is not MemoryMarkout or type(label._recipe) is not dict or markout(**label._recipe) != label:
        raise IntegrityError("memory label differs from its frozen origin and actual future observations")


def protect_memory(memory, *, cluster_id, swings, swing_id, published_at, cut):
    from trading_research.measurements.structure import validate_swing_snapshot
    validate_memory(memory)
    validate_swing_snapshot(swings)
    if swings.instrument != memory.instrument or not any(c.id == cluster_id for c in memory.clusters):
        raise ContractError("protection must bind a same-instrument memory and actual confirmation")
    found = [s for s in swings.confirmed if s.id == swing_id]
    if len(found) != 1 or published_at < max(memory.published_at, swings.published_at, found[0].confirmed_at):
        raise ContractError("protection cannot predate its actual supporting confirmation")
    return {"memory_id": memory.id, "cluster_id": cluster_id, "swing_id": swing_id,
            "birth": memory.published_at, "known_at": published_at, "protected": published_at <= cut}


@dataclass(frozen=True)
class MemoryContext:
    memory_id: str
    cluster_id: str
    features: tuple
    feature_names: tuple
    formed_at: int
    episode: str
    date_group: str
    _recipe: object = field(default=None, init=False, compare=False, repr=False)


def memory_context(memory, *, cluster_id, feature_names, episode, date_group):
    validate_memory(memory)
    bounded_rows(feature_names, 16, name="memory observable context")
    bounded_name(episode)
    bounded_name(date_group)
    found = [c for c in memory.clusters if c.id == cluster_id]
    if len(found) != 1:
        raise ContractError("memory context must identify one frozen source cluster")
    c = found[0]
    values = {"size": Fraction(c.gross), "center": c.center_ticks, "width": Fraction(c.high_ticks-c.low_ticks),
              "age": Fraction(memory.cut-c.first_at), "count": Fraction(c.raw_count)}
    if not feature_names or len(set(feature_names)) != len(feature_names) or any(k not in values for k in feature_names):
        raise ContractError("memory context requires distinct supported causal observables")
    result = MemoryContext(memory.id, cluster_id, tuple(values[k] for k in feature_names), tuple(feature_names),
                            memory.published_at, episode, date_group)
    object.__setattr__(result, "_recipe", dict(memory=memory, cluster_id=cluster_id, feature_names=tuple(feature_names),
                                              episode=episode, date_group=date_group))
    return result


def _validate_context(context):
    if type(context) is not MemoryContext or type(context._recipe) is not dict or memory_context(**context._recipe) != context:
        raise IntegrityError("retrieval context differs from actual causal memory features")


@dataclass(frozen=True)
class MemoryEpisode:
    id: str
    context: MemoryContext
    label: MemoryMarkout


def retrieve_matured(query, episodes, *, definition, cut, fit_admission, query_session):
    from trading_research.measurements.measurement_fits import reconstruct_numeric_measurement_fit, read_measurement_query
    _validate_context(query)
    bounded_rows(episodes, 1024, name="matured retrieval episodes")
    if type(definition) is not tuple or len(definition) != 3 or not 1 <= definition[1] <= 128 or type(definition[2]) is not bool:
        raise ContractError("retrieval needs version, bounded neighbors and explicit date exclusion")
    bounded_name(definition[0])
    state, parameters = reconstruct_numeric_measurement_fit(fit_admission, family="memory_distance")
    retained_query = read_measurement_query(fit_admission, query_session, window_start=query.formed_at,
                                            columns=tuple(parameters["columns"]))
    if tuple(retained_query[k] for k in parameters["columns"]) != query.features:
        raise IntegrityError("retrieval query differs from the actual retained inference reads")
    if len(state["scales"]) != len(query.features):
        raise ContractError("retrieval fitted feature dimensions differ")
    selected, seen = [], set()
    for episode in episodes:
        if type(episode) is not MemoryEpisode:
            raise ContractError("retrieval requires typed observed episodes")
        bounded_name(episode.id)
        if episode.id in seen:
            raise ContractError("retrieval repeats an episode identity")
        seen.add(episode.id)
        _validate_context(episode.context)
        validate_memory_markout(episode.label)
        c, label = episode.context, episode.label
        if (label.memory_id != c.memory_id or label.cluster_id != c.cluster_id or c.feature_names != query.feature_names):
            raise ContractError("retrieval episode joins a different origin or feature definition")
        if (label.status != "mature" or label.earliest_known_at >= query.formed_at or label.published_at >= query.formed_at
                or label.published_at > cut or c.episode == query.episode
                or definition[2] and c.date_group == query.date_group):
            continue
        if any(s <= 0 for s in state["scales"]):
            raise DependencyUnavailable("retrieval distance has an unsupported zero scale")
        distance = sum(((float(a)-float(b))/s)**2 for a, b, s in zip(query.features, c.features, state["scales"]))**0.5
        selected.append((distance, episode.id, label.terminal_markout))
    selected.sort(key=lambda row: (row[0], row[1]))
    selected = tuple(selected[:definition[1]])
    return {"selected": tuple(r[1] for r in selected), "distances": tuple(r[0] for r in selected),
            "support": len(selected), "mean_markout": sum(r[2] for r in selected)/len(selected) if selected else None,
            "query_memory": query.memory_id, "fit_recipe_id": fit_admission.recipe_id}


@dataclass(frozen=True)
class MemoryAttempt:
    id: str
    episode: str
    memory_id: str
    cluster_id: str
    label: MemoryMarkout
    visits: MemoryVisits

    def __post_init__(self):
        bounded_name(self.id)
        bounded_name(self.episode)
        validate_memory_markout(self.label)
        validate_memory_visits(self.visits)
        if ((self.memory_id,self.cluster_id) != (self.label.memory_id,self.label.cluster_id)
                or (self.memory_id,self.cluster_id) != (self.visits.memory_id,self.visits.cluster_id)
                or self.label.status != 'mature' or self.visits.published_at >= self.label.horizon_end):
            raise ContractError('attempt requires the actual same-episode matured label and preceding visit observation')


def memory_attempt_summary(attempts):
    bounded_rows(attempts,1024,name='memory attempts')
    if any(type(a) is not MemoryAttempt for a in attempts) or len({a.id for a in attempts}) != len(attempts):
        raise ContractError('memory attempt identities must be actual, unique and bounded')
    for a in attempts:
        a.__post_init__()
    if len({a.label.id for a in attempts}) != len(attempts):
        raise ContractError('one actual memory outcome cannot count as multiple attempts')
    by={}
    sources={}
    fresh=[]
    for a in sorted(attempts,key=lambda a:(a.visits.published_at,a.id)):
        previous=by.get(a.episode)
        if previous is not None and (previous.memory_id,previous.cluster_id) != (a.memory_id,a.cluster_id):
            raise ContractError('one memory episode cannot change its original source cluster')
        seen=sources.setdefault(a.episode,set())
        fresh.append((a.id,bool(set(a.visits.new_source_ids)-seen)))
        seen.update(a.visits.new_source_ids)
        by[a.episode]=a
    return {'attempt_count':len(attempts),'independent_episode_count':len(by),
        'sum_attempt_markouts':sum(a.label.terminal_markout for a in attempts),
        'fresh_effort':tuple(fresh),'label_versions':tuple(a.label.id for a in attempts)}


class MemoryBook:
    def __init__(self, *, definition, max_versions=1024):
        definition.__post_init__()
        self.definition, self.max_versions = definition, positive_limit(max_versions)
        self.versions, self.recipes = (), ()
        self._sealed = self._state_bytes()

    def advance(self, captures, *, views, cut, published_at):
        self.checkpoint()
        if len(self.versions) >= self.max_versions:
            raise ContractError("memory book requires explicit archival at capacity")
        recipe = dict(captures=tuple(captures), views=tuple(views), definition=self.definition, cut=cut,
                      published_at=published_at, previous=self.versions[-1] if self.versions else None)
        result = build_memory(**recipe)
        staged = canonical_json({"definition": self.definition, "max_versions": self.max_versions,
                                 "versions": tuple(v.record() for v in (*self.versions, result))})
        if len(staged) > self.definition.max_bytes:
            raise ContractError("memory book retained byte capacity exhausted")
        self.versions, self.recipes = (*self.versions, result), (*self.recipes, recipe)
        self._sealed = staged
        return result

    def _state_bytes(self):
        return canonical_json({"definition": self.definition, "max_versions": self.max_versions,
                               "versions": tuple(v.record() for v in self.versions)})

    def checkpoint(self):
        if self._state_bytes() != self._sealed or len(self.versions) != len(self.recipes):
            raise IntegrityError("memory book state changed outside its authenticated replay")
        if len(self._sealed) > self.definition.max_bytes:
            raise ContractError("memory checkpoint byte capacity exhausted")
        return self._sealed

    @classmethod
    def restore(cls, payload, *, recipes, definition, max_versions=1024):
        bounded_rows(recipes, max_versions, name="memory restoration recipes")
        if type(payload) is not bytes or len(payload) > definition.max_bytes:
            raise ContractError("memory restoration byte capacity exhausted")
        result = cls(definition=definition, max_versions=max_versions)
        for r in recipes:
            result.advance(r["captures"], **{k: r[k] for k in ("views", "cut", "published_at")})
        if result.checkpoint() != payload:
            raise IntegrityError("memory checkpoint differs from its complete bounded source replay")
        return result
