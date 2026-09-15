"""Full account-day view plus every applicable bank primitive for one candidate-branch."""
from __future__ import annotations

from datetime import date
from functools import lru_cache
from typing import Any
import time

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.rule_discovery.kernels import (
    C2_HALF_LIFE_NS,
    book_observe_kernel,
    c2_fold_kernel,
    contact_lifecycle_kernel,
    delta_imbalance_kernel,
    s1_machine_kernel,
    s2_machine_kernel,
    s3_machine_kernel,
    s4_machine_kernel,
    sweep_displacement_kernel,
    warmup_kernels,
)
from trading_research.research.rule_discovery.native import (
    NS,
    bars_arrays,
    build_market_view,
    cvd_from_prefix,
    install_write_guard,
    price_to_ticks,
    vwap_from_prefix,
)
from trading_research.research.rule_discovery.registry import (
    BANKS,
    RECIPES,
    applicable,
)

MEASUREMENT_FAMILY = "SAINT-AMT"
MEASUREMENT_BRANCH = "continuation_retest"
C1_WINDOW_NS = 5 * 60 * NS


@lru_cache(maxsize=1)
def _cached_candidate_bank() -> dict[str, Any]:
    from trading_research.research.rule_discovery.registry import expand_candidate_bank

    return expand_candidate_bank()


def _time(fn, bucket: dict[str, float], name: str) -> Any:
    started = time.monotonic()
    result = fn()
    bucket[name] = bucket.get(name, 0.0) + (time.monotonic() - started)
    return result


def _cohort_trades(view, *, start_ns: int, snapshot_ns: int, horizon_s: int) -> list[dict[str, Any]]:
    """Contact-window trades for markout. Vectorized mid lookup; no per-event Python over the full session."""
    prefix = view.prefix
    arrays = view.arrays
    horizon_ns = horizon_s * NS
    left = int(np.searchsorted(prefix.t_ns, start_ns, side="left"))
    right = int(np.searchsorted(prefix.t_ns, snapshot_ns - horizon_ns, side="left"))
    if right <= left or arrays.t_ns.size == 0:
        return []
    t_ns = prefix.t_ns[left:right]
    qty = prefix.size[left:right]
    ticks = prefix.ticks[left:right]
    trade_index = prefix.trade_index[left:right]
    side = arrays.side[trade_index]
    due = t_ns + horizon_ns
    idx = np.searchsorted(arrays.t_ns, due, side="left")
    n = arrays.t_ns.size
    valid = (idx < n) & (side != 0)
    if not np.any(valid):
        return []
    idx = np.minimum(idx, n - 1)
    mid_ticks = (arrays.bid_ticks[idx].astype(np.float64) + arrays.ask_ticks[idx].astype(np.float64)) * 0.5
    mid_available = arrays.known_at_ns[idx]
    trades = []
    sel = np.flatnonzero(valid)
    for i in sel.tolist():
        trades.append(
            {
                "sign": int(side[i]),
                "qty": int(qty[i]),
                "price": float(ticks[i]) * 0.25,
                "event_ns": int(t_ns[i]),
                "mid_at_horizon": float(mid_ticks[i]) * 0.25,
                "mid_available_ns": int(mid_available[i]),
            }
        )
    return trades


def run_candidate_branch_session(day: str, *, family: str = MEASUREMENT_FAMILY, branch: str = MEASUREMENT_BRANCH) -> dict[str, Any]:
    """PERFORMANCE.md: full account-day view plus all applicable bank primitives, one candidate-branch, single core."""
    install_write_guard()
    from trading_research.research.rule_discovery.cohorts import HORIZONS, markout, memory_features, resolved_memory_row
    from trading_research.research.rule_discovery.delta import (
        C1_WINDOW_NS as DELTA_C1_NS,
        c1_normalized,
        c3_zscore,
        emit_features,
    )
    from trading_research.research.rule_discovery.formations import (
        f1_trailing_minutes,
        f2_volume_completed,
        f3_balance,
        freeze_formation,
        median_int,
    )
    from trading_research.research.rule_discovery.profiles import build_profile, location_objects
    from trading_research.research.rule_discovery.references import r1_frozen_band, r2_prior_edge
    from trading_research.research.rule_discovery.sequences import (
        advance_on_bars,
        cohort_signed_mean,
    )

    family_seconds: dict[str, float] = {bank: 0.0 for bank in BANKS}
    recipes_run: list[str] = []
    warmup_kernels()
    started_view = time.monotonic()
    view = build_market_view(day, full_account_day=True)
    view_seconds = time.monotonic() - started_view
    issue = min(int(et_ns(date.fromisoformat(day), 9, 30)), view.end_ns)
    prefix = view.prefix
    left = int(np.searchsorted(prefix.t_ns, view.start_ns, side="left"))
    right = int(np.searchsorted(prefix.t_ns, issue, side="left"))
    ticks = prefix.ticks[left:right]
    sizes = prefix.size[left:right]

    bars = bars_arrays(view.arrays, view.start_ns, issue)
    n_bars = int(bars["start_ns"].size)
    rows = [
        {key: int(bars[key][i]) for key in bars}
        for i in range(n_bars)
    ]
    volumes = [int(row["volume"]) for row in rows[-20:]]
    median = median_int(volumes) if volumes else 0
    f1 = f2 = f3 = None
    formed = []
    if applicable("Formation", "F1", family, branch)[0]:
        f1 = _time(lambda: f1_trailing_minutes(rows, issue_ns=issue), family_seconds, "Formation")
        recipes_run.append("F1")
    if applicable("Formation", "F2", family, branch)[0]:
        f2 = _time(lambda: f2_volume_completed(rows, issue_ns=issue, median_volume=median), family_seconds, "Formation")
        recipes_run.append("F2")
    if applicable("Formation", "F3", family, branch)[0]:
        f3 = _time(lambda: f3_balance(rows, issue_ns=issue), family_seconds, "Formation")
        recipes_run.append("F3")
    for item in (f1, f2, f3):
        if item is not None:
            frozen = freeze_formation(item, cutoff_ns=issue, asset_id=view.asset_id)
            if frozen is not None:
                formed.append(frozen)

    profiles = {}
    locations = []
    for recipe in RECIPES["Profile"]:
        if not applicable("Profile", str(recipe["id"]), family, branch)[0]:
            continue
        bandwidth = int(recipe["parameters"]["bandwidth"])
        profile = _time(
            lambda bandwidth=bandwidth: build_profile(ticks, sizes, bandwidth=bandwidth, window="developing_intraday", as_of_ns=issue),
            family_seconds,
            "Profile",
        )
        profiles[str(recipe["id"])] = profile
        locations.extend(location_objects(profile, later_ticks=()))
        recipes_run.append(str(recipe["id"]))

    signed, volume, unknown = (0, 0, 0)
    c1 = {"available": False, "value": None}
    c2_last = None
    features = ()
    markouts: dict[int, dict[str, Any]] = {}
    if any(applicable("Delta", str(recipe["id"]), family, branch)[0] for recipe in RECIPES["Delta"]):
        signed, volume, unknown = _time(lambda: cvd_from_prefix(prefix, view.start_ns, issue), family_seconds, "Delta")
        c1_signed, c1_vol, c1_unknown = cvd_from_prefix(prefix, max(view.start_ns, issue - DELTA_C1_NS), issue)
        c1 = c1_normalized(c1_signed, c1_vol, c1_unknown)
        features = emit_features({"delta": signed, "volume": volume, "unknown": unknown, "c0": signed}, available_at_ns=issue)
        if n_bars:
            known = bars["volume"] - bars["unknown"]
            zs, ks, norms = _time(
                lambda: c2_fold_kernel(bars["end_ns"], bars["signed"], known, np.int64(C2_HALF_LIFE_NS)),
                family_seconds,
                "Delta",
            )
            c2_last = {"t_ns": int(bars["end_ns"][-1]), "z": float(zs[-1]), "known": float(ks[-1]), "normalized": float(norms[-1]) if norms[-1] == norms[-1] else None}
        else:
            c2_last = None
        _time(lambda: c3_zscore(float(signed), ()), family_seconds, "Delta")
        for recipe in RECIPES["Delta"]:
            if applicable("Delta", str(recipe["id"]), family, branch)[0]:
                recipes_run.append(str(recipe["id"]))

    cohort_start = max(view.start_ns, issue - C1_WINDOW_NS)
    for horizon in HORIZONS:
        trades = _time(lambda horizon=horizon: _cohort_trades(view, start_ns=cohort_start, snapshot_ns=issue, horizon_s=horizon), family_seconds, "Delta")
        markouts[horizon] = _time(lambda trades=trades, horizon=horizon: markout(trades, horizon_s=horizon, snapshot_ns=issue), family_seconds, "Memory")

    memory = None
    if any(applicable("Memory", str(recipe["id"]), family, branch)[0] for recipe in RECIPES["Memory"]):
        prior = [resolved_memory_row(markouts[120], side=1)]
        memory = _time(
            lambda: memory_features(
                touch_count=1,
                formation_ns=view.start_ns,
                last_contact_ns=issue,
                now_ns=issue,
                pre_touch_departure=False,
                signed_volume_at_band=int(signed),
                prior_resolved=prior,
            ),
            family_seconds,
            "Memory",
        )
        for recipe in RECIPES["Memory"]:
            if applicable("Memory", str(recipe["id"]), family, branch)[0]:
                recipes_run.append(str(recipe["id"]))

    sequence_states = {}
    if any(applicable("Sequence", str(recipe["id"]), family, branch)[0] for recipe in RECIPES["Sequence"]):
        cohort_mean = cohort_signed_mean(markouts[120], 1)
        c1_value = c1.get("value")
        lo_seq = int(bars["low_ticks"][0]) if n_bars else 0
        hi_seq = int(bars["high_ticks"][0]) if n_bars else 0
        contact_i = 0
        deadline_i = max(n_bars - 1, 0)
        if formed and n_bars:
            lo_seq = price_to_ticks(formed[0].low)
            hi_seq = price_to_ticks(formed[0].high)
            idx = contact_lifecycle_kernel(bars["high_ticks"], bars["low_ticks"], np.int64(lo_seq), np.int64(hi_seq), np.int64(4))
            if idx.size:
                contact_i = int(idx[0])
        for recipe in RECIPES["Sequence"]:
            recipe_id = str(recipe["id"])
            if not applicable("Sequence", recipe_id, family, branch)[0]:
                continue
            if n_bars == 0:
                sequence_states[recipe_id] = "contacted"
                recipes_run.append(recipe_id)
                continue
            result = _time(
                lambda recipe_id=recipe_id: advance_on_bars(
                    recipe_id,
                    bars["high_ticks"],
                    bars["low_ticks"],
                    bars["close_ticks"],
                    lo=lo_seq,
                    hi=hi_seq,
                    side=1,
                    contact_i=contact_i,
                    deadline_i=deadline_i,
                    c1_value=None if c1_value is None else float(c1_value),
                    cohort_mean=cohort_mean,
                    cohort_after=False,
                    opposing=bars["unknown"],
                    quantile=0,
                    adverse_ticks=np.zeros(n_bars, dtype=np.int64),
                    cap_ticks=2,
                    contact_extreme=lo_seq,
                    pressure_last_i=min(contact_i + 2, deadline_i),
                ),
                family_seconds,
                "Sequence",
            )
            sequence_states[recipe_id] = result["state"]
            recipes_run.append(recipe_id)

    references = {}
    if formed:
        formation = formed[0]
        price, disp, _vol = vwap_from_prefix(prefix, view.start_ns, issue)
        for recipe in RECIPES["Reference"]:
            recipe_id = str(recipe["id"])
            if not applicable("Reference", recipe_id, family, branch)[0]:
                continue
            if recipe_id == "R1" and price is not None and disp is not None:
                try:
                    references[recipe_id] = _time(
                        lambda: r1_frozen_band(
                            formation=formation,
                            vwap=price,
                            dispersion=disp,
                            issue_at_ns=max(issue, formation.available_at_ns),
                            expiry_at_ns=view.end_ns,
                            family=family,
                            branch=branch,
                            contract=view.arrays.instrument_id,
                        ),
                        family_seconds,
                        "Reference",
                    )
                except ContractError:
                    references[recipe_id] = None
            if recipe_id == "R2":
                try:
                    references[recipe_id] = _time(
                        lambda: r2_prior_edge(
                            formation=formation,
                            edge="high",
                            issue_at_ns=max(issue, formation.available_at_ns),
                            expiry_at_ns=view.end_ns,
                            family=family,
                            branch=branch,
                            contract=view.arrays.instrument_id,
                        ),
                        family_seconds,
                        "Reference",
                    )
                except ContractError:
                    references[recipe_id] = None
            recipes_run.append(recipe_id)

    contact_n = 0
    if formed and n_bars:
        lo_ticks = price_to_ticks(formed[0].low)
        hi_ticks = price_to_ticks(formed[0].high)
        idx = contact_lifecycle_kernel(bars["high_ticks"], bars["low_ticks"], np.int64(lo_ticks), np.int64(hi_ticks), np.int64(4))
        contact_n = int(idx.size)
        _time(
            lambda: sweep_displacement_kernel(bars["high_ticks"], bars["low_ticks"], np.int64(lo_ticks), np.int64(hi_ticks), np.int64(1)),
            family_seconds,
            "Sequence",
        )
        if contact_n:
            ci = np.int64(int(idx[0]))
            dl = np.int64(n_bars - 1)
            _time(
                lambda: s1_machine_kernel(bars["high_ticks"], bars["low_ticks"], bars["close_ticks"], np.int64(lo_ticks), np.int64(hi_ticks), np.int64(1), ci, dl),
                family_seconds,
                "Sequence",
            )
            _time(
                lambda: s2_machine_kernel(bars["high_ticks"], bars["low_ticks"], bars["close_ticks"], np.int64(lo_ticks), np.int64(hi_ticks), np.int64(1), ci, dl),
                family_seconds,
                "Sequence",
            )
            _time(
                lambda: s3_machine_kernel(
                    bars["high_ticks"],
                    bars["low_ticks"],
                    bars["close_ticks"],
                    np.int64(lo_ticks),
                    np.int64(hi_ticks),
                    np.int64(1),
                    ci,
                    dl,
                    0.0 if c1.get("value") is None else float(c1["value"]),
                    np.int64(1 if c1.get("available") else 0),
                    0.0,
                    np.int64(0),
                    np.int64(0),
                ),
                family_seconds,
                "Sequence",
            )
            _time(
                lambda: s4_machine_kernel(
                    bars["unknown"],
                    np.int64(0),
                    np.zeros(n_bars, dtype=np.int64),
                    np.int64(2),
                    bars["close_ticks"],
                    np.int64(lo_ticks),
                    np.int64(1),
                    ci,
                    ci,
                    dl,
                ),
                family_seconds,
                "Sequence",
            )
        arrays = view.arrays
        if arrays.t_ns.size:
            _time(
                lambda: book_observe_kernel(
                    arrays.bid_ticks,
                    arrays.ask_ticks,
                    arrays.bid_sz,
                    arrays.ask_sz,
                    np.int64(lo_ticks),
                    np.int64(1),
                ),
                family_seconds,
                "Sequence",
            )
            trade = arrays.is_trade
            _time(
                lambda: delta_imbalance_kernel(arrays.size[trade], arrays.side[trade].astype(np.int64)),
                family_seconds,
                "Delta",
            )

    for recipe in RECIPES["Timing"]:
        if applicable("Timing", str(recipe["id"]), family, branch)[0]:
            recipes_run.append(str(recipe["id"]))
            family_seconds["Timing"] += 0.0

    bank = _time(_cached_candidate_bank, family_seconds, "Timing")
    import resource as pyresource

    peak_rss = int(pyresource.getrusage(pyresource.RUSAGE_SELF).ru_maxrss) * 1024
    return {
        "date": day,
        "jobs": 1,
        "matches": 1,
        "mismatches": [],
        "family": family,
        "branch": branch,
        "candidate_branch": f"{family}:{branch}",
        "scope": "full_account_day_view plus all applicable bank primitives for one candidate-branch, single core",
        "view_seconds": view_seconds,
        "family_seconds": family_seconds,
        "recipes_run": recipes_run,
        "issue_ns": issue,
        "instrument_id": view.arrays.instrument_id,
        "f1_available": bool(f1.get("available")) if f1 else False,
        "f2_available": bool(f2.get("available")) if f2 else False,
        "f2_overshoot": None if f2 is None else f2.get("overshoot"),
        "f3_available": bool(f3.get("available")) if f3 else False,
        "formations": len(formed),
        "profile_available": bool((profiles.get("P1") or {}).get("available")),
        "profile_volume": (profiles.get("P1") or {}).get("volume"),
        "location_objects": len(locations),
        "bar_count": n_bars,
        "contact_n": contact_n,
        "c0": signed,
        "volume": volume,
        "unknown": unknown,
        "c1_available": bool(c1.get("available")),
        "c2_z": None if c2_last is None else c2_last.get("z"),
        "feature_names": [item.name for item in features],
        "unresolved_cohorts": markouts.get(30, {}).get("unresolved"),
        "markout_120_buy_mean": markouts.get(120, {}).get("buy", {}).get("mean"),
        "memory_prior_resolved": None if memory is None else memory.get("prior_resolved_count"),
        "sequence_states": dict(sequence_states),
        "references": sorted(references),
        "bank_candidates": bank["counts"]["nonbaseline_selected"],
        "coverage": view.coverage(view.start_ns, issue).status.value,
        "peak_rss_bytes": peak_rss,
        "contact_subset_only": True,
    }
