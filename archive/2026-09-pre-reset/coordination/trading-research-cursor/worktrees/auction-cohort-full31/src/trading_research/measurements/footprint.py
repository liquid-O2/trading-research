"""Exact side rows, diagonal contrasts and contiguous imbalance stacks."""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction

from trading_research.errors import ContractError
from trading_research.measurements.tape import Trade,_one_tape


@dataclass(frozen=True)
class FootprintRow:
    price:int
    buy:int
    sell:int
    unknown:int
    trade_ids:tuple[str,...]


def footprint(trades:tuple[Trade,...],*,row_ticks:int,grid_origin:int=0):
    if type(row_ticks) is not int or row_ticks<1 or type(grid_origin) is not int:raise ContractError("frozen positive tick grid required")
    rows=defaultdict(lambda:[0,0,0,[]]);unpriced=0
    for t in _one_tape(trades):
        if t.price is None:unpriced+=t.size;continue
        price=grid_origin+((t.price.value-grid_origin)//row_ticks)*row_ticks
        row=rows[price];row[{1:0,-1:1,None:2}[t.side]]+=t.size;row[3].append(t.id)
    return {'rows':tuple(FootprintRow(p,*v[:3],tuple(v[3])) for p,v in sorted(rows.items())),
            'unpriced_volume':unpriced,'total_volume':sum(t.size for t in trades),'row_ticks':row_ticks,'grid_origin':grid_origin}


def imbalance_rows(view:dict,*,ratio:Fraction,minimum_volume:int,comparison:str,zero_opponent:str):
    if not isinstance(ratio,Fraction) or ratio<=1 or type(minimum_volume) is not int or minimum_volume<1 or comparison not in ('same_price','diagonal') or zero_opponent not in ('require_observed_opponent','infinite_if_minimum'):
        raise ContractError("frozen imbalance ratio, volume, row comparison and zero rules required")
    rows={r.price:r for r in view['rows']};step=view['row_ticks'];results=[]
    for p,r in rows.items():
        flags={}
        for name,direction,numerator in (('buy',-1,r.buy),('sell',1,r.sell)):
            other=rows.get(p+direction*step) if comparison=='diagonal' else r
            denominator=0 if other is None else (other.sell if name=='buy' else other.buy)
            unknown=0 if other is None else other.unknown
            worst=denominator+unknown
            lower=None if worst==0 else Fraction(numerator,worst)
            qualifying=(numerator>=minimum_volume and ((worst==0 and zero_opponent=='infinite_if_minimum') or (lower is not None and lower>=ratio)))
            if zero_opponent=='require_observed_opponent' and denominator==0:qualifying=False
            flags[name]={'qualifying':qualifying,'numerator':numerator,'opponent':denominator,'unknown_opponent':unknown,'ratio_lower_bound':lower,
                         'zero_opponent':worst==0,'counterpart_row_observed':other is not None}
        results.append({'price':p,**flags})
    return tuple(results)


def stacked_imbalances(rows:tuple[dict,...],*,side:str,row_ticks:int,minimum_rows:int):
    if side not in ('buy','sell') or row_ticks<1 or minimum_rows<2:raise ContractError("stack needs side, contiguous grid and at least two rows")
    runs=[];current=[]
    for row in sorted(rows,key=lambda r:r['price']):
        if not row[side]['qualifying'] or (current and row['price']!=current[-1]+row_ticks):
            if len(current)>=minimum_rows:runs.append(tuple(current))
            current=[]
        if row[side]['qualifying']:current.append(row['price'])
    if len(current)>=minimum_rows:runs.append(tuple(current))
    return tuple(runs)


from dataclasses import field
from trading_research.errors import DependencyUnavailable, IntegrityError
from trading_research.measurements.common import bounded_rows, positive_limit
from trading_research.measurements.profiles import ProfileSnapshot, validate_profile, side_geometry
from trading_research.operations.artifacts import canonical_json, digest


@dataclass(frozen=True)
class FootprintMeasurement:
    profile_id: str
    source_bar_version: str
    cut: int
    published_at: int
    final: bool
    rows: tuple
    buy_stacks: tuple
    sell_stacks: tuple
    geometry: tuple
    signed_peaks: tuple
    total_delta: Fraction
    absolute_delta_mass: Fraction
    integrated_contrast: Fraction | None
    concentration: Fraction | None
    haar: tuple
    ordered_prefixes: tuple
    _recipe: object = field(default=None, init=False, compare=False, repr=False)

    def record(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__ if k != "_recipe"}

    @property
    def id(self):
        return digest(self.record())


def haar_channels(values):
    bounded_rows(values, 4096, name="fixed Haar rows")
    if not values:
        return ()
    current, levels = tuple(Fraction(v) for v in values), []
    while len(current)>1:
        padded = current if len(current)%2 == 0 else current+(Fraction(0),)
        means = tuple((a+b)/2 for a, b in zip(padded[::2], padded[1::2]))
        differences = tuple((a-b)/2 for a, b in zip(padded[::2], padded[1::2]))
        levels.append((means, differences, len(current)))
        current = means
    return tuple(levels)


def measure_footprint(profile, *, ratio=Fraction(3), minimum_numerator=1,
                       comparison="diagonal", zero_policy="require_opposition", minimum_stack=2, prefixes=()):
    validate_profile(profile)
    bounded_rows(prefixes, 32, name="actual chronological footprint prefixes")
    if (type(ratio) not in (int, Fraction) or ratio <= 1 or type(minimum_stack) is not int
            or not 2 <= minimum_stack <= 4096 or comparison not in ("diagonal", "same_price")
            or zero_policy not in ("require_opposition", "qualify_zero")):
        raise ContractError("footprint requires exact ratio, finite stack and declared comparison/zero policy")
    positive_limit(minimum_numerator)
    if (profile._recipe[0] != "build" or len(profile.source_bar_versions) != 1
            or profile.source_bar_versions[0] is None or not profile.representation.startswith("whole_trade")):
        raise ContractError("footprint needs one actual F09 whole-trade bar profile")
    capture = profile._recipe[1]["captures"][0]
    engine, bar_id = capture._bar_recipe
    bar, _ = engine.window_publication(bar_id)
    cells = {r.row: r for r in profile.rows}
    observed = {profile.grid.row(t.price.value) for t in profile.members if t.price is not None}
    rows = []
    full_price_support=profile.history_complete and not sum(profile.unpriced)
    for row in profile.rows:
        flags = {}
        for side, direction in (("buy", -1), ("sell", 1)):
            other_index = row.row if comparison == "same_price" else row.row+direction
            other = cells.get(other_index)
            numerator = row.buy if side == "buy" else row.sell
            denominator = Fraction(0) if other is None else (other.sell if side == "buy" else other.buy)
            uncertain = Fraction(0) if other is None else other.unknown
            observed_ratio = numerator/denominator if denominator else None
            minimum_ratio = numerator/(denominator+uncertain) if denominator+uncertain else None
            maximum_ratio = (numerator+row.unknown)/denominator if denominator else None
            def qualifies(n, d):
                if n < minimum_numerator:
                    return False
                if not d:
                    return zero_policy == "qualify_zero"
                return n/d >= ratio
            observed_flag = qualifies(numerator, denominator)
            certain = qualifies(numerator, denominator+uncertain)
            if zero_policy == "require_opposition" and not denominator:
                certain = False
            full_support=full_price_support and (other is not None or not sum(
                profile.low_overflow if other_index<profile.grid.lower_row else profile.high_overflow))
            flags[side] = {"numerator": numerator, "opponent": denominator, "unknown_opponent": uncertain,
                "observed_ratio": observed_ratio, "minimum_compatible_ratio": minimum_ratio if full_support else None,
                "maximum_compatible_ratio": maximum_ratio if full_support else None, "observed_qualifies": observed_flag,
                "certain_qualifies": certain if full_support else None,
                "possible_qualifies": qualifies(numerator+row.unknown, denominator) if full_support else None,
                "full_price_support":full_support,
                "zero_opposing_status": not bool(denominator), "counterpart_row_observed": other_index in observed}
        rows.append({"row": row.row, **flags})
    def stacks(side):
        runs, current = [], []
        for row in rows:
            if row[side]["certain_qualifies"]:
                if current and row["row"] != current[-1]+1:
                    if len(current)>=minimum_stack:
                        runs.append(tuple(current))
                    current = []
                current.append(row["row"])
            else:
                if len(current)>=minimum_stack:
                    runs.append(tuple(current))
                current = []
        if len(current)>=minimum_stack:
            runs.append(tuple(current))
        return tuple(runs)
    summary = bar.summary
    o, h, l, close = summary.open_ticks, summary.high_ticks, summary.low_ticks, summary.close_ticks
    upper_wick = None if None in (o, h, close) else h-max(o, close)
    lower_wick = None if None in (o, l, close) else min(o, close)-l
    geometry = (("open", o), ("high", h), ("low", l), ("close", close), ("upper_wick", upper_wick),
                ("lower_wick", lower_wick), ("last_print_at", summary.last_at), ("order_exact", summary.order_exact),
                ("geometry_status", "partial" if not full_price_support else "final" if bar.final else "provisional"))
    for prefix in prefixes:
        validate_profile(prefix)
        if (prefix.instrument != profile.instrument or prefix.grid != profile.grid or prefix.cut > profile.cut
                or prefix.published_at > profile.published_at or prefix._recipe[0] != "build"):
            raise ContractError("footprint prefix differs from actual causal source/grid/publication")
    sides = side_geometry(profile)
    mass = sum(r.mass for r in profile.rows)
    delta = sum(r.delta for r in profile.rows)
    result = FootprintMeasurement(profile.id, bar_id, profile.cut, profile.published_at, bar.final,
        tuple(rows), stacks("buy"), stacks("sell"), geometry,
        (("negative", sides["minimum_rows"]), ("positive", sides["maximum_rows"]), ("absolute", sides["absolute_peak_rows"])),
        delta, sides["absolute_delta_mass"], delta/mass if mass else None,
        sum((r.mass/mass)**2 for r in profile.rows) if mass else None,
        (("buy", haar_channels(tuple(r.buy for r in profile.rows))), ("sell", haar_channels(tuple(r.sell for r in profile.rows))),
         ("unknown", haar_channels(tuple(r.unknown for r in profile.rows)))),
        tuple((p.id, p.cut, p.published_at, tuple((r.row, r.buy, r.sell, r.unknown) for r in p.rows)) for p in prefixes))
    object.__setattr__(result, "_recipe", dict(profile=profile, ratio=ratio, minimum_numerator=minimum_numerator,
        comparison=comparison, zero_policy=zero_policy, minimum_stack=minimum_stack, prefixes=tuple(prefixes)))
    return result


def validate_footprint(value):
    if type(value) is not FootprintMeasurement or type(value._recipe) is not dict or measure_footprint(**value._recipe) != value:
        raise IntegrityError("footprint differs from its actual retained F09/profile recipe")


def footprint_available(value, cut, *, final_only=False):
    validate_footprint(value)
    return value.published_at <= cut and (value.final or not final_only)
