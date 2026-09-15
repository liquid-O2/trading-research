"""Tick profiles, value area, nodes, shelves and location objects."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence
from hashlib import sha256
import json
import math

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.rule_discovery.native import TICK, ticks_to_decimal

VA_FRACTION = Decimal("0.70")
HVN_PROMINECE = 0.20
NEIGHBOR = 2
MINIMA_SPAN = 8
BAND_FRACTION = 0.50
BAND_MAX_BINS = 8
SHELF_MIN_BINS = 3
SHELF_WITHIN = 0.20
SHELF_MEAN_MULT = 2.0
LEDGE_DROP = 0.50
PROFILE_WINDOWS = (
    "prior_regular_session",
    "prior_full_account_day",
    "overnight",
    "prior_five_sessions",
    "prior_calendar_week",
    "developing_intraday",
)
LOCATION_KINDS = (
    "naked_poc",
    "hvn",
    "lvn",
    "shelf",
    "ledge",
    "prior_reaction_area",
    "unfinished_business",
    "refill_zone",
)
OBJECT_IDS = {
    "naked_poc": "O065",
    "hvn": "O066",
    "lvn": "O067",
    "shelf": "O068",
    "ledge": "O069",
    "prior_reaction_area": "O072",
    "unfinished_business": "O087",
    "refill_zone": "O116",
}


def triangular_kernel(bandwidth: int) -> np.ndarray:
    if bandwidth < 0:
        raise ContractError("bandwidth must be nonnegative")
    if bandwidth == 0:
        return np.array([1.0], dtype=np.float64)
    span = np.arange(-bandwidth, bandwidth + 1, dtype=np.float64)
    weights = np.maximum(0.0, (bandwidth + 1) - np.abs(span))
    total = float(weights.sum())
    return weights / total


def python_triangular_kernel(bandwidth: int) -> list[float]:
    if bandwidth == 0:
        return [1.0]
    weights = [max(0.0, (bandwidth + 1) - abs(j)) for j in range(-bandwidth, bandwidth + 1)]
    total = sum(weights)
    return [w / total for w in weights]


def python_bincount(ticks: Sequence[int], sizes: Sequence[int]) -> tuple[int, list[int]]:
    if not ticks:
        return 0, []
    lo = min(ticks)
    hi = max(ticks)
    raw = [0] * (hi - lo + 1)
    for tick, size in zip(ticks, sizes):
        raw[tick - lo] += int(size)
    return lo, raw


def python_smooth(raw: Sequence[int], bandwidth: int) -> list[float]:
    kernel = python_triangular_kernel(bandwidth)
    n = len(raw)
    k = len(kernel)
    full = [0.0] * (n + k - 1)
    for i, volume in enumerate(raw):
        for j, weight in enumerate(kernel):
            full[i + j] += volume * weight
    start = (k - 1) // 2
    return full[start:start + n]


def vector_profile(ticks: np.ndarray, sizes: np.ndarray, *, bandwidth: int) -> dict[str, Any]:
    if ticks.size == 0 or int(sizes.sum()) <= 0:
        return {"available": False, "reason": "empty or zero-volume", "raw": np.zeros(0, dtype=np.int64)}
    from trading_research.research.rule_discovery.kernels import profile_accumulate_kernel

    lo = int(ticks.min())
    n_bins = int(ticks.max()) - lo + 1
    raw = profile_accumulate_kernel(ticks.astype(np.int64, copy=False), sizes.astype(np.int64, copy=False), np.int64(lo), np.int64(n_bins))
    kernel = triangular_kernel(bandwidth)
    full = np.convolve(raw.astype(np.float64), kernel, mode="full")
    start = (kernel.size - 1) // 2
    smoothed = full[start:start + raw.size]
    return {
        "available": True,
        "reason": None,
        "min_tick": lo,
        "raw": raw,
        "smoothed": smoothed,
        "bandwidth": bandwidth,
        "volume": int(raw.sum()),
    }


def python_profile(ticks: Sequence[int], sizes: Sequence[int], *, bandwidth: int) -> dict[str, Any]:
    if not ticks or sum(sizes) <= 0:
        return {"available": False, "reason": "empty or zero-volume", "raw": []}
    lo, raw = python_bincount(ticks, sizes)
    smoothed = python_smooth(raw, bandwidth)
    return {
        "available": True,
        "reason": None,
        "min_tick": lo,
        "raw": raw,
        "smoothed": smoothed,
        "bandwidth": bandwidth,
        "volume": sum(raw),
    }


def volume_weighted_mean_ticks(min_tick: int, raw: Sequence[int]) -> float:
    total = sum(raw)
    if total <= 0:
        raise ContractError("zero-volume mean")
    acc = 0
    for i, volume in enumerate(raw):
        acc += (min_tick + i) * volume
    return acc / total


def poc_tick(min_tick: int, smoothed: Sequence[float], raw: Sequence[int]) -> int:
    peak = max(smoothed)
    candidates = [i for i, value in enumerate(smoothed) if value == peak]
    mean = volume_weighted_mean_ticks(min_tick, raw)
    candidates.sort(key=lambda i: (abs((min_tick + i) - mean), min_tick + i))
    return min_tick + candidates[0]


def python_value_area(
    min_tick: int,
    raw: Sequence[int],
    smoothed: Sequence[float],
    poc: int,
    *,
    fraction: Decimal = VA_FRACTION,
) -> dict[str, Any]:
    total = sum(raw)
    if total <= 0:
        return {"available": False, "reason": "zero volume"}
    target = fraction * Decimal(total)
    index = poc - min_tick
    selected = {index}
    inside = Decimal(raw[index])
    low = index - 1
    high = index + 1
    n = len(raw)

    def rank(side: int) -> tuple[float, int]:
        if side < 0 or side >= n:
            return (-1.0, 1)
        return (float(smoothed[side]), -1 if side < index else 1)

    while inside < target and (low >= 0 or high < n):
        left_ok = low >= 0
        right_ok = high < n
        if not left_ok:
            chosen = high
        elif not right_ok:
            chosen = low
        else:
            left_s, right_s = float(smoothed[low]), float(smoothed[high])
            if left_s > right_s:
                chosen = low
            elif right_s > left_s:
                chosen = high
            else:
                chosen = low
        selected.add(chosen)
        inside += Decimal(raw[chosen])
        if chosen == low:
            low -= 1
        else:
            high += 1
    lo = min(selected)
    hi = max(selected)
    return {
        "available": True,
        "val_ticks": min_tick + lo,
        "vah_ticks": min_tick + hi,
        "inside_raw": int(inside),
        "total_raw": total,
        "fraction": float(inside / Decimal(total)),
        "bins": sorted(selected),
    }


def frozen_sparse_row_value_area(rows: Sequence[tuple[int, int]], poc_tick_value: int, *, fraction: Decimal = VA_FRACTION) -> dict[str, Any]:
    """Reproduce method_pack objects/profiles._value_area on sparse occupied rows.

    Adjacent *rows* are treated as neighbors, so missing ticks are skipped.
    """
    if not rows:
        return {"available": False}
    total = sum(v for _t, v in rows)
    index = next(i for i, (tick, _v) in enumerate(rows) if tick == poc_tick_value)
    selected = {index}
    inside = rows[index][1]
    low = index - 1
    high = index + 1
    while Decimal(inside) / Decimal(total) < fraction and (low >= 0 or high < len(rows)):
        low_volume = rows[low][1] if low >= 0 else None
        high_volume = rows[high][1] if high < len(rows) else None
        if low_volume is None:
            chosen = high
        elif high_volume is None:
            chosen = low
        elif low_volume > high_volume:
            chosen = low
        elif high_volume > low_volume:
            chosen = high
        else:
            chosen = low
        selected.add(chosen)
        inside += rows[chosen][1]
        if chosen == low:
            low -= 1
        else:
            high += 1
    lo = min(selected)
    hi = max(selected)
    return {
        "available": True,
        "val_ticks": rows[lo][0],
        "vah_ticks": rows[hi][0],
        "inside_raw": inside,
        "row_neighbors": True,
    }


def _local_extrema(smoothed: Sequence[float], *, want_max: bool) -> list[int]:
    n = len(smoothed)
    hits = []
    for i in range(n):
        lo = max(0, i - NEIGHBOR)
        hi = min(n, i + NEIGHBOR + 1)
        window = smoothed[lo:hi]
        if want_max:
            if smoothed[i] == max(window) and smoothed[i] > 0:
                hits.append(i)
        else:
            if smoothed[i] == min(window):
                hits.append(i)
    return hits


def _prominence(smoothed: Sequence[float], index: int, *, peak: bool) -> float:
    n = len(smoothed)
    left = smoothed[max(0, index - MINIMA_SPAN):index]
    right = smoothed[index + 1:min(n, index + MINIMA_SPAN + 1)]
    if peak:
        left_ext = min(left) if left else smoothed[index]
        right_ext = min(right) if right else smoothed[index]
        base = max(left_ext, right_ext)
        return (smoothed[index] - base) / max(smoothed[index], 1.0)
    left_ext = max(left) if left else smoothed[index]
    right_ext = max(right) if right else smoothed[index]
    top = min(left_ext, right_ext)
    return (top - smoothed[index]) / max(top, 1.0)


def _group_plateaus(indices: Sequence[int], smoothed: Sequence[float]) -> list[list[int]]:
    if not indices:
        return []
    ordered = sorted(set(indices))
    groups = [[ordered[0]]]
    for index in ordered[1:]:
        prev = groups[-1][-1]
        if index == prev + 1 and smoothed[index] == smoothed[prev]:
            groups[-1].append(index)
        else:
            groups.append([index])
    return groups


def _node_tick(min_tick: int, members: Sequence[int], raw: Sequence[int]) -> int:
    acc = 0
    volume = 0
    for index in members:
        acc += (min_tick + index) * raw[index]
        volume += raw[index]
    if volume <= 0:
        return min_tick + min(members)
    mean = acc / volume
    rounded = int(math.floor(mean + 0.5))
    if abs((rounded - 0.5) - mean) < 1e-15:
        rounded = int(math.floor(mean))
    return rounded


def _node_band(min_tick: int, peak_index: int, raw: Sequence[int], peak_volume: int) -> tuple[int, int]:
    threshold = BAND_FRACTION * peak_volume
    lo = hi = peak_index
    n = len(raw)
    for _ in range(BAND_MAX_BINS):
        left = lo - 1
        if left < 0 or raw[left] < threshold:
            break
        if left >= 1 and raw[left] > raw[lo] and raw[left] > raw[left - 1]:
            break
        lo = left
    for _ in range(BAND_MAX_BINS):
        right = hi + 1
        if right >= n or raw[right] < threshold:
            break
        if right + 1 < n and raw[right] > raw[hi] and raw[right] > raw[right + 1]:
            break
        hi = right
    return min_tick + lo, min_tick + hi


def nodes(
    min_tick: int,
    raw: Sequence[int],
    smoothed: Sequence[float],
    *,
    kind: str,
) -> list[dict[str, Any]]:
    want_max = kind == "hvn"
    extrema = _local_extrema(smoothed, want_max=want_max)
    groups = _group_plateaus(extrema, smoothed)
    records = []
    for members in groups:
        peak_index = members[int(np.argmax([smoothed[i] for i in members]))] if want_max else members[int(np.argmin([smoothed[i] for i in members]))]
        prom = _prominence(smoothed, peak_index, peak=want_max)
        if prom < HVN_PROMINECE:
            continue
        volume = sum(raw[i] for i in members)
        tick = _node_tick(min_tick, members, raw)
        band = _node_band(min_tick, peak_index, raw, max(raw[i] for i in members) if want_max else max(raw) or 1)
        records.append(
            {
                "kind": kind,
                "tick": tick,
                "prominence": prom,
                "volume": volume,
                "band_low": band[0],
                "band_high": band[1],
                "members": [min_tick + i for i in members],
            }
        )
    records.sort(key=lambda item: (-item["prominence"], -item["volume"], item["tick"]))
    kept: list[dict[str, Any]] = []
    for item in records:
        overlap = False
        for prior in kept:
            if not (item["band_high"] < prior["band_low"] or item["band_low"] > prior["band_high"]):
                overlap = True
                break
        if not overlap:
            kept.append(item)
    kept.sort(key=lambda item: item["tick"])
    return kept


def _occupied_median(raw: Sequence[int]) -> float:
    occupied = [v for v in raw if v > 0]
    if not occupied:
        return 0.0
    occupied.sort()
    n = len(occupied)
    if n % 2:
        return float(occupied[n // 2])
    return (occupied[n // 2 - 1] + occupied[n // 2]) / 2.0


def shelves_and_ledges(min_tick: int, raw: Sequence[int]) -> list[dict[str, Any]]:
    """Research choice: LEVEL_ATLAS shelf/ledge, not a recovered source formula."""
    n = len(raw)
    median = _occupied_median(raw)
    found: list[dict[str, Any]] = []
    i = 0
    while i < n:
        if raw[i] <= 0:
            i += 1
            continue
        j = i
        run = [raw[i]]
        while j + 1 < n and raw[j + 1] > 0:
            candidate = run + [raw[j + 1]]
            lo, hi = min(candidate), max(candidate)
            if lo <= 0:
                break
            if (hi - lo) / max(lo, 1) > SHELF_WITHIN:
                break
            run = candidate
            j += 1
        length = j - i + 1
        if length >= SHELF_MIN_BINS:
            mean = sum(run) / length
            if mean > SHELF_MEAN_MULT * median:
                left_drop = i > 0 and raw[i - 1] <= (1.0 - LEDGE_DROP) * mean
                right_drop = j + 1 < n and raw[j + 1] <= (1.0 - LEDGE_DROP) * mean
                if left_drop or right_drop:
                    ledge_ticks = []
                    if left_drop:
                        ledge_ticks.append(min_tick + i - 1)
                    if right_drop:
                        ledge_ticks.append(min_tick + j + 1)
                    found.append(
                        {
                            "kind": "shelf",
                            "research_choice": True,
                            "low_ticks": min_tick + i,
                            "high_ticks": min_tick + j,
                            "mean_volume": mean,
                            "ledge_ticks": ledge_ticks,
                            "definition": "LEVEL_ATLAS_2026-09-14",
                        }
                    )
                    for tick in ledge_ticks:
                        found.append(
                            {
                                "kind": "ledge",
                                "research_choice": True,
                                "tick": tick,
                                "shelf_low_ticks": min_tick + i,
                                "shelf_high_ticks": min_tick + j,
                                "definition": "LEVEL_ATLAS_2026-09-14",
                            }
                        )
        i = j + 1
    return found


def profile_identity(*, window: str, as_of_ns: int, min_tick: int, raw: Sequence[int], bandwidth: int) -> str:
    if window not in PROFILE_WINDOWS:
        raise ContractError(f"unknown profile window {window}")
    payload = json.dumps(
        {"window": window, "as_of_ns": as_of_ns, "min_tick": min_tick, "raw": list(raw), "bandwidth": bandwidth},
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode()).hexdigest()


def build_profile(
    ticks: np.ndarray | Sequence[int],
    sizes: np.ndarray | Sequence[int],
    *,
    bandwidth: int,
    window: str,
    as_of_ns: int,
) -> dict[str, Any]:
    tick_arr = np.asarray(ticks, dtype=np.int64)
    size_arr = np.asarray(sizes, dtype=np.int64)
    vector = vector_profile(tick_arr, size_arr, bandwidth=bandwidth)
    reference = python_profile([int(v) for v in tick_arr.tolist()], [int(v) for v in size_arr.tolist()], bandwidth=bandwidth)
    if vector["available"] != reference["available"]:
        raise ContractError("vector profile availability diverged from python")
    if not vector["available"]:
        return {**vector, "window": window, "as_of_ns": as_of_ns, "research_choice_windows": list(PROFILE_WINDOWS)}
    if list(vector["raw"]) != list(reference["raw"]):
        raise ContractError("raw bincount diverged from python")
    if any(abs(a - b) > 1e-12 * max(1.0, abs(b)) for a, b in zip(vector["smoothed"].tolist(), reference["smoothed"])):
        raise ContractError("smoothed profile diverged from python")
    raw = [int(v) for v in vector["raw"].tolist()]
    smoothed = [float(v) for v in vector["smoothed"].tolist()]
    min_tick = int(vector["min_tick"])
    poc = poc_tick(min_tick, smoothed, raw)
    value_area = python_value_area(min_tick, raw, smoothed, poc)
    hvn = nodes(min_tick, raw, smoothed, kind="hvn")
    lvn = nodes(min_tick, raw, smoothed, kind="lvn")
    structure = shelves_and_ledges(min_tick, raw)
    identity = profile_identity(window=window, as_of_ns=as_of_ns, min_tick=min_tick, raw=raw, bandwidth=bandwidth)
    return {
        "available": True,
        "window": window,
        "as_of_ns": as_of_ns,
        "profile_id": identity,
        "min_tick": min_tick,
        "raw": raw,
        "smoothed": smoothed,
        "bandwidth": bandwidth,
        "volume": vector["volume"],
        "poc_ticks": poc,
        "poc_price": str(ticks_to_decimal(poc)),
        "value_area": value_area,
        "hvn": hvn,
        "lvn": lvn,
        "shelves": [item for item in structure if item["kind"] == "shelf"],
        "ledges": [item for item in structure if item["kind"] == "ledge"],
        "research_choice_windows": list(PROFILE_WINDOWS),
        "research_choice_shelf_ledge": True,
    }


def naked_poc(poc_ticks: int, later_ticks: Sequence[int]) -> bool:
    return all(int(tick) != int(poc_ticks) for tick in later_ticks)


def unfinished_business(extreme_ticks: int, later_ticks: Sequence[int], *, side: int) -> bool:
    if side == 1:
        return all(int(tick) < int(extreme_ticks) for tick in later_ticks)
    return all(int(tick) > int(extreme_ticks) for tick in later_ticks)


def prior_reaction_area(*, band_low: int, band_high: int, prior_sweep_then_close_inside: bool) -> dict[str, Any]:
    return {
        "kind": "prior_reaction_area",
        "object_id": OBJECT_IDS["prior_reaction_area"],
        "band_low": band_low,
        "band_high": band_high,
        "available": bool(prior_sweep_then_close_inside),
        "research_choice": False,
    }


def refill_zone(*, band_low: int, band_high: int, departed: bool, returned: bool) -> dict[str, Any]:
    return {
        "kind": "refill_zone",
        "object_id": OBJECT_IDS["refill_zone"],
        "band_low": band_low,
        "band_high": band_high,
        "available": bool(departed and returned),
        "research_choice": False,
    }


def location_objects(profile: Mapping[str, Any], *, later_ticks: Sequence[int], prior_reaction: Mapping[str, Any] | None = None, refill: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    if not profile.get("available"):
        return []
    poc = int(profile["poc_ticks"])
    va = profile["value_area"]
    rows = [
        {
            "kind": "naked_poc",
            "object_id": OBJECT_IDS["naked_poc"],
            "tick": poc,
            "naked": naked_poc(poc, later_ticks),
            "research_choice": False,
        }
    ]
    hvn_rows = list(profile.get("hvn") or []) or [{"kind": "hvn", "available": False}]
    lvn_rows = list(profile.get("lvn") or []) or [{"kind": "lvn", "available": False}]
    shelf_rows = list(profile.get("shelves") or []) or [{"kind": "shelf", "available": False, "research_choice": True}]
    ledge_rows = list(profile.get("ledges") or []) or [{"kind": "ledge", "available": False, "research_choice": True}]
    for item in hvn_rows:
        rows.append({**item, "kind": "hvn", "object_id": OBJECT_IDS["hvn"], "research_choice": False})
    for item in lvn_rows:
        rows.append({**item, "kind": "lvn", "object_id": OBJECT_IDS["lvn"], "research_choice": False})
    for item in shelf_rows:
        rows.append({**item, "kind": "shelf", "object_id": OBJECT_IDS["shelf"], "research_choice": True})
    for item in ledge_rows:
        rows.append({**item, "kind": "ledge", "object_id": OBJECT_IDS["ledge"], "research_choice": True})
    if prior_reaction:
        rows.append(prior_reaction_area(**prior_reaction) if "band_low" in prior_reaction else dict(prior_reaction))
    else:
        rows.append(prior_reaction_area(band_low=va["val_ticks"], band_high=va["vah_ticks"], prior_sweep_then_close_inside=False))
    rows.append(
        {
            "kind": "unfinished_business",
            "object_id": OBJECT_IDS["unfinished_business"],
            "tick": poc,
            "unfinished": unfinished_business(poc, later_ticks, side=1),
            "research_choice": False,
        }
    )
    if refill:
        rows.append(refill_zone(**refill) if "band_low" in refill else dict(refill))
    else:
        rows.append(refill_zone(band_low=va["val_ticks"], band_high=va["vah_ticks"], departed=False, returned=False))
    kinds = {row["kind"] for row in rows}
    if not set(LOCATION_KINDS) <= kinds:
        raise ContractError("location object kinds missing")
    return rows


@dataclass(frozen=True, slots=True)
class ProfileCase:
    case_id: str
    poc_ticks: int | None
    val_ticks: int | None
    vah_ticks: int | None
    volume: int
    notes: str
