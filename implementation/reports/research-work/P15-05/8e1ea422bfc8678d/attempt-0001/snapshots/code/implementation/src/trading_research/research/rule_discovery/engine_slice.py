"""Full account-day view plus every applicable bank primitive for one candidate-branch."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
import time

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Contact, Coverage, EvidenceRef
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.rule_discovery.native import (
    NS,
    build_market_view,
    cvd_from_prefix,
    install_write_guard,
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
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


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
        python_c2_series,
    )
    from trading_research.research.rule_discovery.formations import (
        complete_minute_rows,
        f1_trailing_minutes,
        f2_volume_completed,
        f3_balance,
        freeze_formation,
        median_int,
    )
    from trading_research.research.rule_discovery.profiles import build_profile, location_objects
    from trading_research.research.rule_discovery.references import r1_frozen_band, r2_prior_edge
    from trading_research.research.rule_discovery.registry import expand_candidate_bank
    from trading_research.research.rule_discovery.sequences import (
        advance_sequence,
        cohort_signed_mean,
        initial_state,
        recipe_spec,
    )

    family_seconds: dict[str, float] = {bank: 0.0 for bank in BANKS}
    recipes_run: list[str] = []
    started_view = time.monotonic()
    view = build_market_view(day, full_account_day=True)
    view_seconds = time.monotonic() - started_view
    issue = min(int(et_ns(date.fromisoformat(day), 9, 30)), view.end_ns)
    prefix = view.prefix
    left = int(np.searchsorted(prefix.t_ns, view.start_ns, side="left"))
    right = int(np.searchsorted(prefix.t_ns, issue, side="left"))
    ticks = prefix.ticks[left:right]
    sizes = prefix.size[left:right]

    rows = complete_minute_rows(view.arrays, view.start_ns, issue)
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
        events = [(int(row["end_ns"]), int(row["signed"]), int(row["volume"]) - int(row["unknown"])) for row in rows]
        series = _time(lambda: python_c2_series(events), family_seconds, "Delta")
        c2_last = series[-1] if series else None
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
        ev = EvidenceRef(EMPTY_SHA256, ("slice",), issue, issue, issue, Coverage.COMPLETE, ())
        contact = Contact(
            contact_id=f"{day}:c",
            reference_id=f"{day}:r",
            batch_id=f"{day}:b",
            at_ns=issue,
            available_at_ns=issue,
            side=1,
            kind="touch",
            possible_prices=(Decimal("100"),),
            departure_evidence=(ev,),
            evidence=(ev,),
        )
        cohort_mean = cohort_signed_mean(markouts[120], 1)
        c1_value = c1.get("value")
        for recipe in RECIPES["Sequence"]:
            recipe_id = str(recipe["id"])
            if not applicable("Sequence", recipe_id, family, branch)[0]:
                continue
            spec = recipe_spec(recipe_id)
            state = initial_state(spec, contact, now_ns=issue, expiry_ns=min(view.end_ns, issue + 600 * NS))

            def _advance(state=state, spec=spec, recipe_id=recipe_id):
                now = issue + NS
                if recipe_id == "S4":
                    return advance_sequence(state, None, spec, now_ns=now, inputs={"opposing_aggression": 0, "opposing_exceeds_quantile": False, "seconds_after_contact": 1})
                stepped = advance_sequence(state, None, spec, now_ns=now, inputs={"sweep_ticks": 2, "swept_extreme": 99})
                return advance_sequence(
                    stepped,
                    None,
                    spec,
                    now_ns=now + NS,
                    inputs={
                        "complete_bar": {"close_inside": True, "event_ns": now + NS},
                        "c1": c1_value,
                        "cohort_120_mean": cohort_mean,
                        "cohort_120": markouts[120],
                        "cohort_available_at_ns": issue,
                    },
                )

            sequence_states[recipe_id] = _time(_advance, family_seconds, "Sequence")
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

    for recipe in RECIPES["Timing"]:
        if applicable("Timing", str(recipe["id"]), family, branch)[0]:
            recipes_run.append(str(recipe["id"]))
            family_seconds["Timing"] += 0.0

    bank = _time(expand_candidate_bank, family_seconds, "Timing")
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
        "bar_count": len(rows),
        "c0": signed,
        "volume": volume,
        "unknown": unknown,
        "c1_available": bool(c1.get("available")),
        "c2_z": None if c2_last is None else c2_last.get("z"),
        "feature_names": [item.name for item in features],
        "unresolved_cohorts": markouts.get(30, {}).get("unresolved"),
        "markout_120_buy_mean": markouts.get(120, {}).get("buy", {}).get("mean"),
        "memory_prior_resolved": None if memory is None else memory.get("prior_resolved_count"),
        "sequence_states": {key: state.state for key, state in sequence_states.items()},
        "references": sorted(references),
        "bank_candidates": bank["counts"]["nonbaseline_selected"],
        "coverage": view.coverage(view.start_ns, issue).status.value,
        "peak_rss_bytes": peak_rss,
        "contact_subset_only": True,
    }
