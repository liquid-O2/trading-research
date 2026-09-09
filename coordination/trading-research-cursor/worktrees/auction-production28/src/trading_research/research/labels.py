"""Literal fixed-endpoint price-path labels; missing data is never a zero move."""

from dataclasses import dataclass
from itertools import groupby

from trading_research.errors import ContractError
from trading_research.foundations.contracts import Target
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import Ticks
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class PathPoint:
    at: int
    sequence: int
    price: Ticks
    known_at: int

    def __post_init__(self) -> None:
        timestamp(self.at)
        timestamp(self.known_at)
        if type(self.sequence) is not int or self.sequence < 0 or type(self.price) is not Ticks:
            raise ContractError("path observation requires preserved source order")


@dataclass(frozen=True)
class ObservationWindow:
    start: int
    end: int
    certified_through: int
    gaps: tuple[tuple[int, int], ...] = ()
    source_order_known: bool = True
    version: str = ""

    def __post_init__(self) -> None:
        for at in (self.start, self.end, self.certified_through):
            timestamp(at)
        if self.end <= self.start or self.certified_through < self.end or type(self.version) is not str or not self.version:
            raise ContractError("observation window needs bounds, certification clock and version")
        if type(self.source_order_known) is not bool or type(self.gaps) is not tuple:
            raise ContractError("typed immutable observation capability required")
        previous = None
        for gap in self.gaps:
            if type(gap) is not tuple or len(gap) != 2:
                raise ContractError("typed gap interval required")
            a, b = gap
            timestamp(a); timestamp(b)
            if not self.start <= a < b <= self.end or (previous is not None and a < previous):
                raise ContractError("invalid overlapping or unordered gap interval")
            previous = b


@dataclass(frozen=True)
class PathLabel:
    target_signature: str
    observation_version: str
    maturity_at: int
    observed_end: int
    status: str
    terminal_ticks: int | None
    maximum_up_ticks: int | None
    maximum_down_ticks: int | None
    first_barrier: str | None
    first_barrier_at: int | None
    observed_count: int

    @property
    def version(self) -> str:
        return digest(self)


def reference_path_label(target: Target, *, initial: Ticks, points: tuple[PathPoint, ...],
                         coverage: ObservationWindow, up_ticks: int, down_ticks: int) -> PathLabel:
    if any(type(x) is not int or x <= 0 for x in (up_ticks, down_ticks)):
        raise ContractError("positive integral barrier distances required")
    if coverage.start != target.decision_at or coverage.end > target.horizon_end:
        raise ContractError("coverage must start at the frozen cut and cannot extend the target")
    ordered = sorted(points, key=lambda p: (p.at, p.sequence))
    if len({(p.at, p.sequence) for p in ordered}) != len(ordered):
        raise ContractError("duplicate/ambiguous source identity in path")
    if any(not target.decision_at < p.at <= coverage.end for p in ordered):
        raise ContractError("future label path is outside its actual observation window")
    if any(a <= p.at < b for p in ordered for a, b in coverage.gaps):
        raise ContractError("an observed point contradicts a declared unavailable interval")
    maturity = max([coverage.certified_through, *(p.known_at for p in ordered)])
    # An empty price-observation path does not establish a zero move. Preserve
    # the separately declared last-observed-mark process: a complete certified
    # tape with no new event leaves that particular mark unchanged.
    has_target_observation = bool(ordered) or target.observation_process == "certified_last_observed_mark"
    complete = coverage.end == target.horizon_end and not coverage.gaps and has_target_observation
    if not complete:
        # Partial excursions are lower bounds, not observations of the fixed-end target.
        return PathLabel(target.signature, coverage.version, maturity, coverage.end, "censored",
                         None, None, None, None, None, len(ordered))
    deltas = [0, *(p.price.value - initial.value for p in ordered)]
    first, first_at = "neither", None
    for at, group in groupby(ordered, key=lambda p: p.at):
        hits = [("upper" if p.price.value - initial.value >= up_ticks else
                 "lower" if p.price.value - initial.value <= -down_ticks else None) for p in group]
        hits = [h for h in hits if h is not None]
        if hits:
            first_at = at
            first = "ambiguous" if not coverage.source_order_known and len(set(hits)) > 1 else hits[0]
            break
    terminal = deltas[-1] if coverage.source_order_known or len({p.price for p in ordered if p.at == coverage.end}) <= 1 else None
    # Unknown order also makes the last observation ambiguous, even before the endpoint.
    if not coverage.source_order_known and ordered:
        last_prices = {p.price for p in ordered if p.at == ordered[-1].at}
        if len(last_prices) > 1:
            terminal = None
    status = "ambiguous" if first == "ambiguous" or terminal is None else "observed"
    return PathLabel(target.signature, coverage.version, maturity, coverage.end, status,
                     terminal, max(deltas), -min(deltas), first, first_at, len(ordered))


def ohlc_barrier_order(*, initial: Ticks, high: Ticks, low: Ticks,
                       up_ticks: int, down_ticks: int) -> str:
    """OHLC extrema do not identify the ordering when both barriers are reached."""
    if high.value < low.value or up_ticks <= 0 or down_ticks <= 0:
        raise ContractError("invalid OHLC/barriers")
    up = high.value >= initial.value + up_ticks
    down = low.value <= initial.value - down_ticks
    return "ambiguous" if up and down else "upper" if up else "lower" if down else "neither"
