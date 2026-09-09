"""Declared target adapters over immutable prepared path rows.

Compatible duration classes express interval/right-censored observations on a
declared grid. They are not invented midpoint events or negative outcomes.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.jumbo_matrix import PATH_CLASSES


CONTINUOUS_TARGETS = (
    "future_high_from_known_W", "future_low_from_known_W", "terminal_from_known_W",
    "quadratic_variation_W2",
)
DURATION_GRID = (0.0, .05, .10, .25, .50, .75, 1.0)
PHASES = {
    "fit": ("2020-01-01", "2022-12-31", "2023-01-01"),
    "tune": ("2023-01-01", "2023-12-31", "2024-01-01"),
    "calibrate": ("2024-01-01", "2024-06-30", "2024-07-01"),
    "select": ("2024-07-01", "2024-12-31", "2025-01-01"),
    "heldout": ("2025-01-01", "2026-12-31", None),
}


def boundary_ns(day):
    return int(datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp()) * 1_000_000_000


@dataclass
class Target:
    name: str
    kind: str
    values: object
    eligible: object
    label_known_at_ns: object
    metadata: dict

    def applicable(self, matrix):
        """Declared source opportunities, independent of observed outcomes."""
        import numpy as np
        clocks = self.metadata.get("applicable_clocks")
        if clocks is None:
            return np.ones(matrix.size, dtype=bool)
        if (not isinstance(clocks, (list, tuple)) or not clocks
                or len(set(clocks)) != len(clocks)
                or any(clock not in matrix.categories["clock"] for clock in clocks)):
            raise ContractError("target applicability requires declared matrix clocks")
        codes = [matrix.categories["clock"].index(clock) for clock in clocks]
        return np.isin(matrix.fields["clock"], codes)

    def phase(self, matrix, phase):
        if phase not in PHASES:
            raise ContractError("undeclared chronological target phase")
        first, last, before = PHASES[phase]
        mask = matrix.phase(first, last, maturity_before=None if before is None else boundary_ns(before),
                            label_known=self.label_known_at_ns)
        return mask & self.applicable(matrix) & self.eligible


def group_ids(matrix):
    """Root/clock/horizon identity; no outcome, year or future regime input."""
    import numpy as np
    f = matrix.fields
    return ((f["root"].astype(np.int64) * len(matrix.categories["clock"]) + f["clock"])
            * len(matrix.categories["horizon"]) + f["horizon"])


def decode_group(matrix, group):
    hcount, ccount = len(matrix.categories["horizon"]), len(matrix.categories["clock"])
    rc, h = divmod(int(group), hcount)
    r, c = divmod(rc, ccount)
    if not 0 <= r < len(matrix.categories["root"]):
        raise ContractError("unknown target group")
    return {"root": matrix.categories["root"][r], "clock": matrix.categories["clock"][c],
            "horizon": matrix.categories["horizon"][h]}


def duration_classes(lower, upper, observed_minutes, planned_minutes, *, grid=DURATION_GRID):
    """Map a first/second event interval or right-censor to compatible cells.

Finite cells cover [0,.05], (.05,.1], ... , (.75,1] of each
row's *declared* horizon; the last class is no event by that endpoint. An
interval touching a grid edge conservatively allows both adjacent cells.
With no observed event, a cell ending strictly after the observed prefix is
compatible, as is no event. A zero-length prefix is wholly uninformative.
This coarsening is explicit; cells do not imply a within-cell time density.
"""
    import numpy as np
    lo, hi = np.asarray(lower, dtype=np.float64), np.asarray(upper, dtype=np.float64)
    seen, total = np.asarray(observed_minutes), np.asarray(planned_minutes)
    if (lo.ndim != 1 or lo.shape != hi.shape or lo.shape != seen.shape or lo.shape != total.shape
            or seen.dtype != np.int64 or total.dtype != np.int64
            or np.any(seen < 0) or np.any(total <= 0) or np.any(seen > total)):
        raise ContractError("aligned valid duration intervals and exact minute counts required")
    edges = np.asarray(grid, dtype=np.float64)
    if (len(edges) < 2 or edges[0] != 0 or edges[-1] != 1
            or not np.isfinite(edges).all() or np.any(np.diff(edges) <= 0)):
        raise ContractError("duration grid must increase from zero to one")
    if np.any(np.isinf(lo)) or np.any(np.isinf(hi)):
        raise ContractError("infinite event times are not missing/censored observations")
    event = np.isfinite(lo) | np.isfinite(hi)
    if (np.any(event & (~np.isfinite(lo) | ~np.isfinite(hi)))
            or np.any(event & ((lo < 0) | (hi < lo) | (hi > seen)))):
        raise ContractError("observed event interval lies outside observed prefix")
    # Multiplication avoids dividing event times near an exact grid edge.
    left = total[:, None] * edges[:-1]
    right = total[:, None] * edges[1:]
    allowed = np.zeros((len(lo), len(edges)), dtype=bool)
    allowed[:, :-1] = np.where(event[:, None],
                               (lo[:, None] <= right) & (hi[:, None] >= left),
                               right > seen[:, None])
    allowed[:, -1] = ~event
    if np.any(~allowed.any(axis=1)):
        raise IntegrityError("duration observation has no compatible class")
    return allowed


def target_catalog(matrix):
    import numpy as np
    f = matrix.fields
    complete = (f["path"] >= 0) & (f["path"] < len(PATH_CLASSES))
    full_known = f["maturity_at_ns"]
    geometry = (f["formation_width_ticks"] > 0) & (f["planned_minutes"] > 0)
    records = {}
    for name in ("path", "inclusive_path"):
        valid = complete & (f[name] >= 0) & (f[name] < len(PATH_CLASSES))
        records[name] = Target(name, "categorical", f[name].astype(np.int64), valid, full_known,
                               {"classes": list(PATH_CLASSES), "interpretation": "Observed OHLC path class; ambiguous is its own observation class, not latent market order", "unit": "probability"})
    for name in CONTINUOUS_TARGETS:
        valid = complete & np.isfinite(f[name])
        records[name] = Target(name, "continuous", f[name], valid, full_known,
                               {"unit": "squared formation width" if name.endswith("W2") else "formation widths",
                                "nonnegative": name.endswith("W2"),
                                "anchor": "available exact feature anchor" if "known" in name else "(first close - future origin open)^2 plus consecutive observed minute close differences squared, divided by W^2",
                                "not_identified": "Trade-level realized variation or latent within-minute order"})
    # Derived nonnegative excursions preserve a genuine zero-travel atom.
    # These use the available reference, never the future origin open.
    for side in ("high", "low"):
        original = records[f"future_{side}_from_known_W"]
        name = f"positive_{side}_excursion_from_known_W"
        records[name] = Target(name, "continuous", np.maximum(original.values, 0), original.eligible,
                               original.label_known_at_ns,
                               {"unit": "formation widths", "nonnegative": True,
                                "definition": "max(0, signed future extreme displacement from available anchor)",
                                "zero_atom": "Retained explicitly; a zero forecast is not forced positive"})
    # Reclaim is an observed close strictly back inside after a strict first
    # breach; no-breach complete dates remain in the negative population.
    reclaim = f["reclaim_observed"].astype(np.int64)
    allowed = np.ones((matrix.size, 2), dtype=bool)
    known_reclaim = complete & (reclaim >= 0)
    allowed[known_reclaim] = reclaim[known_reclaim, None] == np.arange(2)
    records["reclaim"] = Target("reclaim", "interval_categorical", allowed,
                                 complete, full_known,
                                 {"classes": [0, 1], "definition": "At least one observed post-breach close strictly inside; no prior breach gives zero; ambiguous first-side paths retain both compatible outcomes"})
    for which in ("first", "second"):
        valid = geometry & (f["observed_prefix_minutes"] > 0)
        lo = f["prefix_first_lower_minutes"] if which == "first" else f["second_lower_minutes"]
        hi = f["prefix_first_upper_minutes"] if which == "first" else f["second_upper_minutes"]
        # The retained prefix carries first-hit data even on incomplete paths.
        # A second event is only recorded by this table when the complete
        # target is observed. Incomplete rows after any first hit cannot
        # supply a second-event censor at the full prefix without its event
        # state: conservatively stop at the first event's lower bound.
        seen = f["observed_prefix_minutes"].copy()
        if which == "second":
            early_first = ~complete & np.isfinite(f["prefix_first_lower_minutes"])
            seen[early_first] = np.floor(f["prefix_first_lower_minutes"][early_first]).astype(np.int64)
            valid &= seen > 0
        values = np.ones((matrix.size, len(DURATION_GRID)), dtype=bool)
        values[valid] = duration_classes(lo[valid], hi[valid], seen[valid], f["planned_minutes"][valid])
        known = np.where(full_known >= 0, full_known, f["prefix_maturity_at_ns"]).astype(np.int64)
        records[which + "_duration"] = Target(which + "_duration", "interval_categorical", values,
                                               valid & (known >= 0), known,
                                               {"classes": list(range(len(DURATION_GRID))), "relative_horizon_edges": list(DURATION_GRID),
                                                "last_class": "No event by declared endpoint", "coarsening": "Compatible-cell likelihood; exact interval support and censoring remain in source tables",
                                                "censoring_assumption": "Likelihood interpretation assumes observation coarsening is conditionally noninformative; unavailable-coverage sensitivity reported",
                                                "second_censored_rule": "Incomplete second-event state stops conservatively before the observed first breach; never counts an unrecorded second event as absent"})
    for item in records.values():
        item.metadata.update(target=item.name, source_matrix=matrix.manifest["id"])
        item.metadata["id"] = digest(item.metadata)
    return records
