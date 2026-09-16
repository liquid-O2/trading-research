"""P15-17 stage B: the breadth run.

Owned by P15-17. Stage A (attempt 47dedaaa4f5b9ce1) froze the bank, the splits,
the gates, the seed and the resource profile in FREEZE.json; nothing here may
change any of them. This module only executes them:

* per session, load the account-day view once (`search.load_b02_market` with
  `warm_session` over every (family, branch) in the bank), evaluate all
  supported candidates on that one view, and record the unsupported ones;
* pair every candidate against the source-faithful B0.2 job written by P15-16A,
  read from the frozen run root -- never re-derived here;
* turn both sides into the deterministic one-mini benchmark: entries frozen from
  the scan episodes, the E0 baseline management from `exits.py`, and the costed
  exit arithmetic of `contracts/execution.py` that `exits.py` calls;
* score folds with the frozen split manifest, `refinement.py`'s ranking,
  selection, Holm and moving-block bootstrap, and write the trial ledger.

No result may change the bank, the gates, the splits or the seed.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import gzip
import json
import math
import os
import resource
import time
import traceback

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.contracts.execution import (
    COMMISSION_SIDE,
    DAY_LOSS_LIMIT,
    POINT_VALUE,
    STRESS_COMMISSION,
    STRESS_LATENCY_NS,
    STRESS_TICKS,
    TICK,
)
from trading_research.research.rule_discovery import exits, refinement, search

TASK_ID = "P15-17"
STAGE = "B"
JOB_SCHEMA = "research-p15-17-breadth-job-v1"
DAILY_SCHEMA = "research-p15-17-breadth-daily-v1"
RUN_META_SCHEMA = "research-p15-17-breadth-run-meta-v1"
MANIFEST_SCHEMA = "research-p15-17-breadth-manifest-v1"
RESULTS_SCHEMA = "research-p15-17-breadth-results-v1"
ALLOWLIST_SCHEMA = "research-p15-17-refinement-allowlist-v1"

WORKSPACE = Path("/workspace")
REPORTS = WORKSPACE / "implementation/reports/research-work"
STAGE_A_ATTEMPT = "47dedaaa4f5b9ce1"
MINUTE_NS = 60_000_000_000
NS = Decimal("1000000000")
STAGE_BUDGET_HOURS = 24.0

#: The B0.2 pairing baseline. Read-only. The corrected run root and any
#: supplemental root are supplied by the orchestrating session and recorded in
#: RUN_META.json; these are the defaults used until then.
B02_ROOTS_DEFAULT = ("/workspace/implementation/reports/research-work/P15-16A/1019e6c09ee54609",)

#: Measured 2026-09-16 on 2024-03-05 with the stage A engine: the stage B
#: additions on top of the frozen per-session p90 are the compact account-day
#: tape (16.1 s), the E0 evaluation of every entry of every candidate (0.1 s)
#: and the cost-stress repeat plus job serialisation. Used only to make the
#: budget projection honest; it never reduces coverage.
BREADTH_OVERHEAD_SECONDS = 18.0

REFERENCE_CONTROL_OFFSETS = (-2, -1, 1, 2)
MISSED_MOVE_REASONS = frozenset({"expiry", "source deadline", "account-day close"})
STOP_REASONS = frozenset({"stop", "break-even stop", "trailing stop"})
E0 = "E0"
DEFAULT_ROUND_TRIP = COMMISSION_SIDE * 2
STRESS_ROUND_TRIP = STRESS_COMMISSION * 2


# --------------------------------------------------------------------------
# identity
# --------------------------------------------------------------------------

#: The runtime code identity of a breadth run: the candidate machinery, this
#: runner and the additive registration hook. Test bytes are evidence and are
#: hashed in the receipt, not in the run identity, so editing a test can never
#: silently rewrite the identity of jobs already written.
OWNED_CODE = (
    "implementation/src/trading_research/research/rule_discovery/search.py",
    "implementation/src/trading_research/research/rule_discovery/search_run.py",
    "implementation/src/trading_research/research/rule_discovery/runner.py",
    "implementation/src/trading_research/research/rule_discovery/refinement.py",
    "implementation/src/trading_research/research/rule_discovery/exits.py",
)


def _worktree_root() -> Path:
    return Path(__file__).resolve().parents[5]


def file_sha256(path: str | Path) -> str:
    return search.file_sha256(Path(path))


def code_identity() -> dict[str, Any]:
    root = _worktree_root()
    files = {}
    for rel in OWNED_CODE:
        path = root / rel
        files[rel] = file_sha256(path) if path.is_file() else None
    digest = sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {
        "worktree": str(root),
        "python": ".".join(str(part) for part in os.sys.version_info[:3]),
        "files": files,
        "code_sha256": digest,
    }


def freeze_identity(freeze_path: str | Path) -> dict[str, Any]:
    path = Path(freeze_path)
    document = json.loads(path.read_text())
    if document.get("task_id") != TASK_ID:
        raise ContractError(f"{path} is not a P15-17 freeze")
    if not document.get("immutable"):
        raise ContractError("FREEZE.json is not marked immutable")
    return {"path": str(path), "sha256": file_sha256(path), "attempt_id": document.get("attempt_id")}


def load_freeze(freeze_path: str | Path) -> dict[str, Any]:
    return json.loads(Path(freeze_path).read_text())


# --------------------------------------------------------------------------
# workers and the budget gate
# --------------------------------------------------------------------------


def cgroup_workers() -> int:
    """floor(cfs_quota / cfs_period) when a cgroup quota exists, else cpu_count.

    PERFORMANCE.md process hygiene; never a hard-coded worker count.
    """
    from trading_research.research.rule_discovery.native import cgroup_worker_count

    return int(cgroup_worker_count())


def budget_projection(
    freeze: Mapping[str, Any],
    *,
    workers: int,
    n_dates: int,
    overhead_seconds: float = BREADTH_OVERHEAD_SECONDS,
) -> dict[str, Any]:
    profile = freeze["resource_profile"]
    p90 = float(profile["per_session_p90_seconds"])
    budget = float(profile.get("stage_budget_hours") or STAGE_BUDGET_HOURS)
    per_session = p90 + float(overhead_seconds)
    hours = n_dates * per_session / (max(int(workers), 1) * 3600.0)
    return {
        "formula": "dates x (frozen per-session p90 + measured stage B overhead) / (workers x 3600)",
        "frozen_per_session_p90_seconds": p90,
        "stage_b_overhead_seconds": float(overhead_seconds),
        "per_session_seconds": per_session,
        "dates": int(n_dates),
        "workers": int(workers),
        "hours": hours,
        "stage_budget_hours": budget,
        "exceeds_budget": hours > budget,
    }


def check_budget(projection: Mapping[str, Any]) -> None:
    line = (
        f"P15-17 breadth projection: {projection['dates']} dates x "
        f"{projection['per_session_seconds']:.1f} s / ({projection['workers']} workers x 3600) = "
        f"{projection['hours']:.2f} h against a {projection['stage_budget_hours']:.0f} h budget"
    )
    print(line, flush=True)
    if projection["exceeds_budget"]:
        raise ContractError(
            "breadth projection exceeds the stage budget; fix the engineering, "
            f"never the coverage or the bank: {line}"
        )


# --------------------------------------------------------------------------
# job paths
# --------------------------------------------------------------------------


def sanitize_candidate_id(candidate_id: str) -> str:
    return str(candidate_id).replace(":", "--")


def job_path(run_root: str | Path, day: str, candidate_id: str) -> Path:
    return Path(run_root) / "jobs" / str(day) / f"{sanitize_candidate_id(candidate_id)}.json.gz"


def daily_path(run_root: str | Path, day: str) -> Path:
    return Path(run_root) / "daily" / f"{day}.json"


def checkpoint_path(run_root: str | Path, day: str) -> Path:
    return Path(run_root) / "checkpoints" / f"{day}.json"


def b02_job_path(root: str | Path, day: str, family: str, branch: str) -> Path:
    return Path(root) / "jobs" / str(day) / f"{family}--branch--{branch}.json.gz"


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text(json.dumps(payload, sort_keys=True, default=str, indent=1))
    tmp.replace(path)
    return path


def _write_gz(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode()
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(gzip.compress(body, mtime=0))
    tmp.replace(path)
    return path


def read_gz(path: str | Path) -> dict[str, Any]:
    with gzip.open(Path(path), "rb") as handle:
        return json.loads(handle.read())


# --------------------------------------------------------------------------
# the deterministic one-mini benchmark, E0 management
# --------------------------------------------------------------------------


def ensure_candidate_ids(document: Mapping[str, Any], family: str, branch: str) -> dict[str, Any]:
    """Give every episode the identity P15-16A gives it.

    The B0.2 job files on disk carry `candidate_id` on every episode because the
    P15-16A runner assigns it after the scan; a scan run in this process does
    not. Without it `exits.frozen_entry_from_b02_episode` has no entry id and
    silently declines the entry, so a candidate would lose entries the baseline
    keeps. The same function is reused, not reimplemented, so the ids match.
    """
    from trading_research.research.rule_discovery.run_adapter_populations import (
        _ensure_candidate_ids,
    )

    return _ensure_candidate_ids(dict(document), {"family": family, "branch": branch})


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def session_scale(view: Any, at_ns: int) -> Decimal | None:
    """S: the registered 60-minute scale ending at `at_ns` (the same scale F3
    balances against). Memoized per session by search.session_cache."""
    geometry = search._f1_geometry(view, int(at_ns), 60)
    if not geometry:
        return None
    width = geometry["high"] - geometry["low"]
    return width if width > 0 else None


def _slice_bounds(tape: exits.CompactDay, start_ns: int, end_ns: int) -> tuple[int, int]:
    lo = int(np.searchsorted(tape.event_ns, int(start_ns), side="right"))
    hi = int(np.searchsorted(tape.event_ns, int(end_ns), side="right"))
    return lo, hi


def excursions(
    tape: exits.CompactDay,
    *,
    side: int,
    fill_price: Decimal,
    objective: Decimal,
    fill_at_ns: int,
    exit_at_ns: int,
    scale: Decimal | None,
) -> dict[str, Any]:
    """Favorable/adverse excursion diagnostics in units of S, from the tape.

    `nearest_approach_S` is how far the objective stayed away, in S; the
    RETENTION.md `location_miss` attribution reads it together with
    `adverse_S_before_favorable_0_5S`.
    """
    lo, hi = _slice_bounds(tape, fill_at_ns, exit_at_ns)
    out: dict[str, Any] = {
        "scale_S": None if scale is None else str(scale),
        "nearest_approach_S": None,
        "adverse_S_before_favorable_0_5S": None,
        "batches": int(max(hi - lo, 0)),
    }
    if scale is None or hi <= lo:
        return out
    high = tape.max_trade[lo:hi]
    low = tape.min_trade[lo:hi]
    mask = np.isfinite(high) & np.isfinite(low)
    if not mask.any():
        return out
    high = high[mask]
    low = low[mask]
    fill = float(fill_price)
    scale_f = float(scale)
    if side == 1:
        favorable = high - fill
        adverse = fill - low
        remaining = float(objective) - float(np.max(high))
    else:
        favorable = fill - low
        adverse = high - fill
        remaining = float(np.min(low)) - float(objective)
    out["nearest_approach_S"] = max(remaining, 0.0) / scale_f
    reached = np.nonzero(favorable >= 0.5 * scale_f)[0]
    window = adverse[: int(reached[0])] if reached.size else adverse
    worst = float(np.max(window)) if window.size else 0.0
    out["adverse_S_before_favorable_0_5S"] = max(worst, 0.0) / scale_f
    return out


@dataclass(frozen=True, slots=True)
class BenchmarkRow:
    entry_id: str
    side: int
    fill_at_ns: int
    fill_price: Decimal
    initial_stop: Decimal | None
    objective: Decimal | None
    exit_price: Decimal | None
    round_trip_cost: Decimal
    admitted: bool
    reason: str
    exit_reason: str | None
    exit_at_ns: int | None
    net_points: Decimal | None
    net_dollars: Decimal | None
    confirmation_delay_s: float | None
    diagnostics: dict[str, Any]


def _confirmation_delay_seconds(episode: Mapping[str, Any]) -> float | None:
    stages = {str(item.get("stage")): item for item in episode.get("stages") or []}
    trigger = stages.get("trigger") or stages.get("reference")
    if not trigger or trigger.get("at_ns") is None or episode.get("decision_at") is None:
        return None
    return (int(episode["decision_at"]) - int(trigger["at_ns"])) / 1e9


def daily_benchmark(
    document: Mapping[str, Any],
    *,
    tape: exits.CompactDay,
    view: Any,
    flatten_at_ns: int,
    round_trip_cost: Decimal = DEFAULT_ROUND_TRIP,
    diagnostics: bool = True,
) -> dict[str, Any]:
    """One account day of the deterministic one-mini benchmark for one scan.

    Entries are frozen from the scan's own `pass` episodes (`exits.py`); each is
    managed by the frozen E0 baseline policy, whose exit price, commission and
    tick slippage come from `contracts/execution.py`. Day accounting is the
    benchmark's: one position at a time, the $1,000 day loss limit, and complete
    zero-entry days retained. A04: opportunities == fills + exclusions.
    """
    episodes = document.get("episodes") or []
    opportunities = 0
    unknown = 0
    pending: list[tuple[exits.FrozenEntry, Mapping[str, Any]]] = []
    not_executable: list[dict[str, Any]] = []
    for episode in episodes:
        verdict = episode.get("research_verdict")
        if verdict == "unknown":
            unknown += 1
        if verdict != "pass":
            continue
        opportunities += 1
        try:
            frozen = exits.frozen_entry_from_b02_episode(
                episode, flatten_at_ns=int(flatten_at_ns), round_trip_cost=round_trip_cost
            )
        except ContractError as exc:
            # e.g. an episode whose decision clock is at or after the account-day
            # flatten: E0 cannot manage it. Recorded with the contract's own
            # reason, never swallowed and never a dropped opportunity.
            not_executable.append(
                {
                    "entry_id": str(episode.get("candidate_id") or ""),
                    "reason": f"not_manageable: {exc}",
                }
            )
            continue
        if frozen is None:
            not_executable.append(
                {
                    "entry_id": str(episode.get("candidate_id") or ""),
                    "reason": "not_executable_geometry",
                }
            )
            continue
        pending.append((frozen, episode))
    pending.sort(key=lambda item: (item[0].fill_at_ns, item[0].entry_id))

    rows: list[BenchmarkRow] = []
    exclusions: list[dict[str, Any]] = list(not_executable)
    realized = Decimal(0)
    net_points_total = Decimal(0)
    open_until: int | None = None
    risk_stop = False
    gap_breach = False
    for frozen, episode in pending:
        if risk_stop:
            exclusions.append({"entry_id": frozen.entry_id, "reason": "day_risk_stop"})
            continue
        if open_until is not None and frozen.fill_at_ns < open_until:
            exclusions.append({"entry_id": frozen.entry_id, "reason": "occupied"})
            continue
        stop_risk = abs(frozen.fill_price - frozen.initial_stop) * POINT_VALUE + frozen.round_trip_cost
        if stop_risk > DAY_LOSS_LIMIT + realized:
            exclusions.append({"entry_id": frozen.entry_id, "reason": "remaining_loss_budget"})
            continue
        record = exits.evaluate_policy_compact(frozen, E0, tape)
        if not isinstance(record, exits.ExitRecord):
            exclusions.append(
                {
                    "entry_id": frozen.entry_id,
                    "reason": getattr(record, "reason", "incomplete"),
                }
            )
            continue
        open_until = record.exit_at_ns
        realized += record.net_dollars
        net_points_total += record.net_points
        diag: dict[str, Any] = {}
        if diagnostics:
            scale_error = None
            try:
                scale = session_scale(view, frozen.fill_at_ns)
            except Exception as exc:  # a diagnostic never costs the day
                scale = None
                scale_error = f"{type(exc).__name__}: {exc}"
            diag = excursions(
                tape,
                side=frozen.side,
                fill_price=frozen.fill_price,
                objective=frozen.objective,
                fill_at_ns=frozen.fill_at_ns,
                exit_at_ns=record.exit_at_ns,
                scale=scale,
            )
            diag["objective_reached"] = record.reason == "objective"
            if scale_error is not None:
                diag["scale_error"] = scale_error
        rows.append(
            BenchmarkRow(
                entry_id=frozen.entry_id,
                side=frozen.side,
                fill_at_ns=frozen.fill_at_ns,
                fill_price=frozen.fill_price,
                initial_stop=frozen.initial_stop,
                objective=frozen.objective,
                exit_price=record.exit_price,
                round_trip_cost=frozen.round_trip_cost,
                admitted=True,
                reason="filled",
                exit_reason=record.reason,
                exit_at_ns=record.exit_at_ns,
                net_points=record.net_points,
                net_dollars=record.net_dollars,
                confirmation_delay_s=_confirmation_delay_seconds(episode),
                diagnostics=diag,
            )
        )
        if record.net_dollars < -DAY_LOSS_LIMIT:
            gap_breach = True
        if realized <= -DAY_LOSS_LIMIT:
            risk_stop = True

    fills = len(rows)
    missed = sum(1 for row in rows if row.exit_reason in MISSED_MOVE_REASONS)
    stopped = sum(1 for row in rows if row.exit_reason in STOP_REASONS)
    delays = [row.confirmation_delay_s for row in rows if row.confirmation_delay_s is not None]
    nearest = [
        row.diagnostics.get("nearest_approach_S")
        for row in rows
        if row.diagnostics.get("nearest_approach_S") is not None and not row.diagnostics.get("objective_reached")
    ]
    adverse = [
        row.diagnostics.get("adverse_S_before_favorable_0_5S")
        for row in rows
        if row.diagnostics.get("adverse_S_before_favorable_0_5S") is not None
    ]
    if opportunities != fills + len(exclusions):
        raise ContractError(
            f"A04 reconciliation failed: {opportunities} opportunities != {fills} fills + {len(exclusions)} exclusions"
        )
    return {
        "episodes": len(episodes),
        "unknown": unknown,
        "opportunities": opportunities,
        "fills": fills,
        "exclusions": exclusions,
        "exclusion_counts": _counts(item["reason"] for item in exclusions),
        "zero_day": fills == 0,
        "net_points": str(net_points_total),
        "net_dollars": str(realized),
        "risk_stop": risk_stop,
        "gap_breach": gap_breach,
        "exit_reasons": _counts(row.exit_reason for row in rows if row.exit_reason),
        "missed_move": missed,
        "stop_first": stopped,
        "confirmation_delay_s_mean": float(np.mean(delays)) if delays else None,
        "nearest_approach_S_min": min(nearest) if nearest else None,
        "adverse_S_before_favorable_0_5S_max": max(adverse) if adverse else None,
        "entries": [
            {
                "entry_id": row.entry_id,
                "side": row.side,
                "fill_at_ns": row.fill_at_ns,
                "fill_price": str(row.fill_price),
                "initial_stop": None if row.initial_stop is None else str(row.initial_stop),
                "objective": None if row.objective is None else str(row.objective),
                "exit_at_ns": row.exit_at_ns,
                "exit_price": None if row.exit_price is None else str(row.exit_price),
                "round_trip_cost": str(row.round_trip_cost),
                "exit_reason": row.exit_reason,
                "net_points": str(row.net_points),
                "net_dollars": str(row.net_dollars),
                "confirmation_delay_s": row.confirmation_delay_s,
                "diagnostics": row.diagnostics,
            }
            for row in rows
        ],
    }


def _counts(values: Iterable[Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(value)
        out[key] = out.get(key, 0) + 1
    return out


class cost_stress:
    """The declared stress setting of contracts/execution.py, applied to the E0
    exit without editing exits.py: 500 ms decision-to-fill latency, two ticks of
    exit slippage and $3.50 commission a side. The module constants exits.py
    reads at call time are restored on exit."""

    def __enter__(self) -> "cost_stress":
        self._latency = exits.LATENCY_NS
        self._tick = exits.TICK
        exits.LATENCY_NS = STRESS_LATENCY_NS
        exits.TICK = TICK * STRESS_TICKS
        return self

    def __exit__(self, *exc: Any) -> None:
        exits.LATENCY_NS = self._latency
        exits.TICK = self._tick


# --------------------------------------------------------------------------
# density-matched controls for the Reference bank
# --------------------------------------------------------------------------


def control_offset(reference_id: str) -> int:
    """SEARCH_CONTRACT: offsets {-2S,-S,+S,+2S} cycled by SHA256(reference_id) mod 4."""
    digest = sha256(str(reference_id).encode()).hexdigest()
    return REFERENCE_CONTROL_OFFSETS[int(digest, 16) % 4]


def shift_band(payload: Any, shift: Decimal) -> Any:
    """Shift a reference payload's band/level by `shift` price points, keeping
    its count, width, issue time and expiry."""
    if not isinstance(payload, Mapping):
        return payload
    out = dict(payload)
    moved = False
    for key in ("high", "low", "level", "edge", "boundary", "band_high", "band_low", "open"):
        value = out.get(key)
        if isinstance(value, Decimal):
            out[key] = value + shift
            moved = True
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            out[key] = Decimal(str(value)) + shift
            moved = True
    if moved:
        out["density_matched_control"] = True
    return out


def control_overrides(resolved: search.ResolvedCandidate, view: Any) -> dict[str, Any]:
    """Wrap the candidate's own enumeration hook so the reference band it
    produces is moved by the deterministic offset. Direction and every stage and
    exit rule are unchanged; only the placement moves."""
    inner = search.build_enumeration_hook(resolved, view)

    def hook(*, point, payload, **ctx):
        out = inner(point=point, payload=payload, **ctx)
        if point != "references":
            return out
        return _shift_reference_payload(out, resolved, view)

    return {search.ENUMERATION_KEY: hook}


def _shift_reference_payload(payload: Any, resolved: search.ResolvedCandidate, view: Any) -> Any:
    if payload is None:
        return payload
    anchor = search.cutoff_ns(view)
    scale = session_scale(view, anchor)
    if scale is None:
        return payload
    if isinstance(payload, Mapping) and not any(
        isinstance(value, Mapping) for value in payload.values()
    ):
        return _shift_one(payload, resolved, scale)
    if isinstance(payload, Mapping):
        return {
            key: (_shift_one(value, resolved, scale) if isinstance(value, Mapping) else value)
            for key, value in payload.items()
        }
    if isinstance(payload, (list, tuple)):
        return [_shift_one(item, resolved, scale) for item in payload]
    return payload


def _shift_one(payload: Any, resolved: search.ResolvedCandidate, scale: Decimal) -> Any:
    if not isinstance(payload, Mapping):
        return payload
    reference_id = str(payload.get("id") or resolved.candidate_id)
    order = list(REFERENCE_CONTROL_OFFSETS)
    start = order.index(control_offset(reference_id))
    for step in range(len(order)):
        offset = order[(start + step) % len(order)]
        shift = Decimal(offset) * scale
        if abs(shift) <= TICK:
            continue  # duplicates a real band within one tick
        moved = shift_band(payload, shift)
        if moved is not payload:
            moved = dict(moved)
            moved["control_offset_S"] = offset
            return moved
    out = dict(payload)
    out["density_matched_control"] = "unavailable"
    return out


# --------------------------------------------------------------------------
# per-session evaluation
# --------------------------------------------------------------------------


def _load_b02_document(
    roots: Sequence[str], day: str, family: str, branch: str
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    for root in roots:
        path = b02_job_path(root, day, family, branch)
        if path.is_file():
            return read_gz(path), {
                "pairing_baseline_source": "p15_16a_job",
                "pairing_baseline_path": str(path),
                "pairing_baseline_sha256": file_sha256(path),
            }
    return None, {
        "pairing_baseline_source": "missing",
        "pairing_baseline_path": None,
        "pairing_baseline_sha256": None,
    }


def _unavailable_session(
    day: str,
    *,
    resolved: Sequence[search.ResolvedCandidate],
    b02_roots: Sequence[str],
    run_root: str | Path | None,
    reason: str,
    started: float,
) -> dict[str, Any]:
    """Every declared candidate keeps a row on a session that cannot be loaded.

    The date is reconciled with an explicit disposition, never dropped and never
    imputed as a zero-net-points day (S11, S06, A01, A05).
    """
    rows: list[dict[str, Any]] = []
    for item in resolved:
        _, provenance = _load_b02_document(list(b02_roots), day, item.family, item.branch)
        row = {
            "schema_version": JOB_SCHEMA,
            "task_id": TASK_ID,
            "stage": STAGE,
            "account_day": day,
            "candidate_id": item.candidate_id,
            "family": item.family,
            "branch": item.branch,
            "bank": item.bank,
            "recipe_id": item.recipe_id,
            "changed_axis": item.changed_axis,
            "parameters": dict(item.parameters),
            "supported": item.supported,
            "unsupported_reason": item.unsupported_reason,
            "status": "session_unavailable",
            "session_unavailable_reason": reason,
            "complete": False,
            "candidate": None,
            "baseline": None,
            "seconds": 0.0,
            **provenance,
        }
        rows.append(row)
        if run_root is not None:
            _write_gz(job_path(run_root, day, item.candidate_id), row)
    session = {
        "schema_version": DAILY_SCHEMA,
        "task_id": TASK_ID,
        "account_day": day,
        "candidates": len(resolved),
        "supported": sum(1 for item in resolved if item.supported),
        "unsupported": sum(1 for item in resolved if not item.supported),
        "session_available": False,
        "session_unavailable_reason": reason,
        "load_seconds": 0.0,
        "wall_seconds": time.perf_counter() - started,
        "peak_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024,
        "warm_failures": [],
        "tape_batches": 0,
        "baseline_sources": _counts(row["pairing_baseline_source"] for row in rows),
        "rows": [_daily_row(row) for row in rows],
    }
    if run_root is not None:
        _write_json(daily_path(run_root, day), session)
    return {"day": day, "session": session, "rows": rows}


def evaluate_session(
    day: str,
    *,
    resolved: Sequence[search.ResolvedCandidate],
    b02_roots: Sequence[str] = B02_ROOTS_DEFAULT,
    run_root: str | Path | None = None,
    with_controls: bool = True,
    with_stress: bool = True,
) -> dict[str, Any]:
    """Load the session once, evaluate the whole bank on it, pair against B0.2."""
    started = time.perf_counter()
    supported = [item for item in resolved if item.supported]
    branches = sorted({(item.family, item.branch) for item in supported})
    if day < search.TAPE_FIRST or day > search.TAPE_LAST:
        # A declared session outside the native tape (e.g. 2020-01-01, a closed
        # RTH holiday for which P15-16A still wrote zero-episode jobs). It keeps
        # a reconciled row per candidate and is NOT a complete zero-net-points
        # trading day, so it never enters a paired denominator.
        return _unavailable_session(
            day,
            resolved=resolved,
            b02_roots=b02_roots,
            run_root=run_root,
            reason=f"declared date outside the native tape {search.TAPE_FIRST}..{search.TAPE_LAST}",
            started=started,
        )
    market = search.load_b02_market(day, warm=True, branches=branches)
    warm = getattr(market, "_p15_17_warm", {}) or {}
    native = getattr(market, "_native_view", None)
    if native is None:
        raise ContractError(f"{day}: no native account-day view; the session cannot be benchmarked")
    tape = exits.compact_from_view(native)
    from trading_research.research.rule_discovery.native import account_day_window

    _, end_ns = account_day_window(date.fromisoformat(day))
    flatten_at_ns = end_ns - MINUTE_NS
    load_seconds = time.perf_counter() - started

    baselines: dict[tuple[str, str], dict[str, Any]] = {}
    for family, branch in branches:
        document, provenance = _load_b02_document(list(b02_roots), day, family, branch)
        if document is None:
            local = (warm.get("baselines") or {}).get((family, branch))
            if local is not None:
                document = ensure_candidate_ids(local, family, branch)
                provenance = {
                    "pairing_baseline_source": "in_process_b02_scan",
                    "pairing_baseline_path": None,
                    "pairing_baseline_sha256": None,
                    "pairing_baseline_reason": "no B0.2 job for this branch in the supplied run roots",
                }
        view = search.market_for_family(market, family)
        if document is None:
            baselines[(family, branch)] = {"document": None, "benchmark": None, **provenance}
            continue
        try:
            benchmark = daily_benchmark(document, tape=tape, view=view, flatten_at_ns=flatten_at_ns)
            error = None
        except Exception as exc:  # recorded against the branch, never silent
            benchmark = None
            error = f"{type(exc).__name__}: {exc}"
        baselines[(family, branch)] = {
            "document": document,
            "benchmark": benchmark,
            "pairing_baseline_error": error,
            **provenance,
        }

    rows: list[dict[str, Any]] = []
    for item in resolved:
        rows.append(
            _evaluate_candidate(
                item,
                day=day,
                market=market,
                tape=tape,
                flatten_at_ns=flatten_at_ns,
                baselines=baselines,
                with_controls=with_controls,
                with_stress=with_stress,
            )
        )
        if run_root is not None:
            _write_gz(job_path(run_root, day, item.candidate_id), rows[-1])

    session = {
        "schema_version": DAILY_SCHEMA,
        "task_id": TASK_ID,
        "account_day": day,
        "candidates": len(resolved),
        "supported": len(supported),
        "unsupported": len(resolved) - len(supported),
        "load_seconds": load_seconds,
        "wall_seconds": time.perf_counter() - started,
        "peak_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024,
        "session_available": True,
        "warm_failures": list(warm.get("failures") or []),
        "tape_batches": int(tape.event_ns.size),
        "baseline_sources": _counts(
            value["pairing_baseline_source"] for value in baselines.values()
        ),
        "rows": [_daily_row(row) for row in rows],
    }
    if run_root is not None:
        _write_json(daily_path(run_root, day), session)
    return {"day": day, "session": session, "rows": rows}


def _daily_row(row: Mapping[str, Any]) -> dict[str, Any]:
    candidate = row.get("candidate") or {}
    baseline = row.get("baseline") or {}
    return {
        "candidate_id": row["candidate_id"],
        "family": row["family"],
        "branch": row["branch"],
        "bank": row["bank"],
        "recipe_id": row["recipe_id"],
        "status": row["status"],
        "supported": row["supported"],
        "pairing_baseline_source": row.get("pairing_baseline_source"),
        "complete": row.get("complete", False),
        "candidate_net_points": candidate.get("net_points"),
        "baseline_net_points": baseline.get("net_points"),
        "candidate_fills": candidate.get("fills"),
        "baseline_fills": baseline.get("fills"),
        "candidate_opportunities": candidate.get("opportunities"),
        "baseline_opportunities": baseline.get("opportunities"),
        "candidate_zero_day": candidate.get("zero_day"),
        "baseline_zero_day": baseline.get("zero_day"),
        "unknown": candidate.get("unknown"),
        "missed_move": candidate.get("missed_move"),
        "stop_first": candidate.get("stop_first"),
        "confirmation_delay_s_mean": candidate.get("confirmation_delay_s_mean"),
        "nearest_approach_S_min": candidate.get("nearest_approach_S_min"),
        "adverse_S_before_favorable_0_5S_max": candidate.get("adverse_S_before_favorable_0_5S_max"),
        "stress_net_points": (row.get("cost_stress") or {}).get("net_points"),
        "control_net_points": (row.get("control") or {}).get("net_points"),
        "verdict_changed": (row.get("verdict_change") or {}).get("changed"),
        "seconds": row.get("seconds"),
    }


def _evaluate_candidate(
    item: search.ResolvedCandidate,
    *,
    day: str,
    market: Any,
    tape: exits.CompactDay,
    flatten_at_ns: int,
    baselines: Mapping[tuple[str, str], Mapping[str, Any]],
    with_controls: bool,
    with_stress: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    pairing = baselines.get((item.family, item.branch)) or {}
    base = {
        "schema_version": JOB_SCHEMA,
        "task_id": TASK_ID,
        "stage": STAGE,
        "account_day": day,
        "candidate_id": item.candidate_id,
        "family": item.family,
        "branch": item.branch,
        "bank": item.bank,
        "recipe_id": item.recipe_id,
        "changed_axis": item.changed_axis,
        "parameters": dict(item.parameters),
        "phase": item.phase,
        "hooks": list(item.hooks),
        "supported": item.supported,
        "unsupported_reason": item.unsupported_reason,
        "pairing_baseline_source": pairing.get("pairing_baseline_source"),
        "pairing_baseline_path": pairing.get("pairing_baseline_path"),
        "pairing_baseline_sha256": pairing.get("pairing_baseline_sha256"),
        "pairing_baseline_error": pairing.get("pairing_baseline_error"),
        "baseline": pairing.get("benchmark"),
    }
    if not item.supported:
        base.update(
            {
                "status": "unsupported",
                "complete": False,
                "candidate": None,
                "seconds": time.perf_counter() - started,
            }
        )
        return base
    view = search.market_for_family(market, item.family)
    try:
        document = ensure_candidate_ids(search.scan_candidate(market, item), item.family, item.branch)
        benchmark = daily_benchmark(document, tape=tape, view=view, flatten_at_ns=flatten_at_ns)
    except Exception as exc:  # a runtime failure is never a data rejection
        error = f"{type(exc).__name__}: {exc}"
        kind = classify_failure(error)
        base.update(
            {
                # a session that never had this family's inputs is an explained
                # missing input, not a defect in the candidate
                "status": "input_unavailable" if kind == "input_unavailable" else "runtime_failure",
                "failure_class": kind,
                "complete": False,
                "candidate": None,
                "error": error,
                "traceback": traceback.format_exc(limit=6),
                "seconds": time.perf_counter() - started,
            }
        )
        return base
    base["candidate"] = benchmark
    base["status"] = "evaluated"
    base["complete"] = pairing.get("benchmark") is not None
    baseline_document = pairing.get("document")
    if baseline_document is not None:
        base["verdict_change"] = search.verdict_changed(baseline_document, document)
    if with_stress:
        with cost_stress():
            stressed = daily_benchmark(
                document,
                tape=tape,
                view=view,
                flatten_at_ns=flatten_at_ns,
                round_trip_cost=STRESS_ROUND_TRIP,
                diagnostics=False,
            )
        base["cost_stress"] = {
            "setting": {
                "latency_ns": STRESS_LATENCY_NS,
                "ticks": STRESS_TICKS,
                "commission_side": str(STRESS_COMMISSION),
            },
            "net_points": stressed["net_points"],
            "fills": stressed["fills"],
        }
    if with_controls and item.bank == "Reference":
        try:
            control_document = search.scan_candidate(
                market, item, overrides=control_overrides(item, view)
            )
            control = daily_benchmark(
                control_document, tape=tape, view=view, flatten_at_ns=flatten_at_ns, diagnostics=False
            )
            control["available"] = True
        except Exception as exc:
            control = {"available": False, "error": f"{type(exc).__name__}: {exc}"}
        base["control"] = control
    base["seconds"] = time.perf_counter() - started
    base["peak_rss_bytes"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    return base


# --------------------------------------------------------------------------
# run orchestration
# --------------------------------------------------------------------------

_WORKER: dict[str, Any] = {}


def _init_worker(payload: Mapping[str, Any]) -> None:
    _WORKER.update(payload)
    _WORKER["resolved"] = search.resolve_bank()


def release_session_caches() -> None:
    """Drop the per-process caches the method pack keeps across sessions.

    ``strategy_options.option_rows`` (32 option-quote files as Python rows), ``spot_rows``
    and ``strategy_measurements.vendor_rows`` (24 vendor-bar files) grow a worker by
    hundreds of MB per session; the P15-16A producer clears the same three after every
    date. Clearing changes no result: each is a pure loader keyed by file path."""
    import gc

    from trading_research.research.method_pack.strategy_measurements import vendor_rows
    from trading_research.research.method_pack.strategy_options import option_rows, spot_rows

    option_rows.cache_clear()
    spot_rows.cache_clear()
    vendor_rows.cache_clear()
    gc.collect()


def _process_date(day: str) -> dict[str, Any]:
    run_root = Path(_WORKER["run_root"])
    started = time.perf_counter()
    try:
        result = evaluate_session(
            day,
            resolved=_WORKER["resolved"],
            b02_roots=_WORKER["b02_roots"],
            run_root=run_root,
        )
    except Exception as exc:
        release_session_caches()
        record = {
            "date": day,
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(limit=8),
            "seconds": time.perf_counter() - started,
        }
        _write_json(run_root / "failed" / f"{day}.json", record)
        return record
    release_session_caches()
    session = result["session"]
    record = {
        "date": day,
        "status": "completed",
        "candidates": session["candidates"],
        "supported": session["supported"],
        "unsupported": session["unsupported"],
        "jobs": [str(job_path(run_root, day, row["candidate_id"]).name) for row in session["rows"]],
        "daily_sha256": file_sha256(daily_path(run_root, day)),
        "wall_seconds": session["wall_seconds"],
        "peak_rss_bytes": session["peak_rss_bytes"],
    }
    _write_json(checkpoint_path(run_root, day), record)
    return record


def declared_dates(freeze: Mapping[str, Any] | None = None) -> list[str]:
    from trading_research.research.rule_discovery.runner import declared_dates as _dates

    return list(_dates())


def init_run(
    *,
    run_root: str | Path,
    freeze_path: str | Path,
    dates: Sequence[str] | None = None,
    workers: int | None = None,
    b02_roots: Sequence[str] = B02_ROOTS_DEFAULT,
    p15_16a_receipt: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(run_root)
    freeze = load_freeze(freeze_path)
    identity = freeze_identity(freeze_path)
    selected = list(dates) if dates else declared_dates(freeze)
    worker_n = int(workers) if workers else cgroup_workers()
    projection = budget_projection(freeze, workers=worker_n, n_dates=len(selected))
    check_budget(projection)
    resolved = search.resolve_bank()
    bank = search.load_bank()
    meta = {
        "schema_version": RUN_META_SCHEMA,
        "task_id": TASK_ID,
        "stage": STAGE,
        "run_root": str(root),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "freeze": identity,
        "stage_a_attempt": STAGE_A_ATTEMPT,
        "code_identity": code_identity(),
        "bank": {"path": bank.get("_path"), "sha256": bank.get("_sha256"), "candidates": len(resolved)},
        "b02_roots": list(b02_roots),
        "p15_16a_receipt": p15_16a_receipt or {"status": "PENDING"},
        "workers": worker_n,
        "dates": len(selected),
        "budget_projection": projection,
        "splits": freeze["ra4_splits"],
        "uncertainty": freeze["uncertainty"],
        "promotion_gates": freeze["promotion_gates"],
        "scoring_policy": freeze["scoring_policy"],
    }
    existing = root / "RUN_META.json"
    if existing.is_file():
        previous = json.loads(existing.read_text())
        conflict = {
            key
            for key in ("freeze", "b02_roots", "stage_a_attempt")
            if previous.get(key) != meta.get(key)
        }
        if conflict or previous.get("bank", {}).get("sha256") != meta["bank"]["sha256"]:
            raise ContractError(
                f"run root {root} was frozen with a different configuration: {sorted(conflict) or ['bank']}"
            )
        meta["started_at"] = previous.get("started_at", meta["started_at"])
        history = list(previous.get("previous_code_identities") or [])
        if previous.get("code_identity", {}).get("code_sha256") != meta["code_identity"]["code_sha256"]:
            # a resume under changed code never silently rewrites the identity
            history.append(
                {
                    "code_identity": previous.get("code_identity"),
                    "superseded_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        if history:
            meta["previous_code_identities"] = history
    _write_json(existing, meta)
    _write_json(
        root / "MANIFEST.json",
        {
            "schema_version": MANIFEST_SCHEMA,
            "task_id": TASK_ID,
            "freeze_sha256": identity["sha256"],
            "freeze_path": identity["path"],
            "code_sha256": meta["code_identity"]["code_sha256"],
            "code_files": meta["code_identity"]["files"],
            "bank_sha256": meta["bank"]["sha256"],
            "split_manifest_sha256": freeze["ra4_splits"]["split_manifest_sha256"],
            "evaluation_protocol_sha256": freeze["ra4_splits"]["evaluation_protocol_sha256"],
            "b02_roots": list(b02_roots),
            "dates": selected,
            "candidates": [item.candidate_id for item in resolved],
        },
    )
    _write_json(
        root / "JOB_INVENTORY.json",
        {
            "schema_version": "research-p15-17-job-inventory-v1",
            "task_id": TASK_ID,
            "jobs": [
                {"date": day, "candidate_id": item.candidate_id, "status": "declared"}
                for day in selected
                for item in resolved
            ],
            "dates": len(selected),
            "candidates": len(resolved),
            "declared_jobs": len(selected) * len(resolved),
        },
    )
    return meta


def pending_dates(run_root: str | Path, dates: Sequence[str]) -> list[str]:
    root = Path(run_root)
    out = []
    for day in dates:
        marker = checkpoint_path(root, day)
        if not marker.is_file():
            out.append(day)
            continue
        try:
            record = json.loads(marker.read_text())
        except json.JSONDecodeError:
            out.append(day)
            continue
        if record.get("status") != "completed":
            out.append(day)
            continue
        target = daily_path(root, day)
        if not target.is_file() or file_sha256(target) != record.get("daily_sha256"):
            out.append(day)
    return out


def retained_failures(run_root: str | Path, dates: Sequence[str]) -> list[dict[str, Any]]:
    """The failed records of dates that never produced a daily shard.

    A runtime failure is not a data rejection and is not a reason to hide a run:
    it stays in the ledger with its own error and traceback. A date is a
    *retained* failure when it has a `failed/<date>.json` record; a date with no
    record at all is unresolved work and still blocks completion.
    """
    out: list[dict[str, Any]] = []
    root = Path(run_root)
    for day in dates:
        path = root / "failed" / f"{day}.json"
        if not path.is_file():
            continue
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if record.get("status") != "failed":
            continue
        out.append(
            {
                "date": day,
                "status": "failed",
                "error": record.get("error"),
                "record": str(path),
                "record_sha256": file_sha256(path),
                "disposition": "runtime_failure_retained",
            }
        )
    return out


def complete_run(*, run_root: str | Path) -> dict[str, Any]:
    """Close a run whose only pending dates carry retained failure records.

    Reads checkpoints, daily shards and failed records only; it never re-runs a
    date and never touches RUN_META.json, so the run keeps the code identities
    that actually produced its documents.
    """
    root = Path(run_root)
    manifest = json.loads((root / "MANIFEST.json").read_text())
    dates = list(manifest["dates"])
    still = pending_dates(root, dates)
    retained = retained_failures(root, still)
    unresolved = sorted(set(still) - {row["date"] for row in retained})
    if unresolved:
        raise ContractError(
            f"{len(unresolved)} pending dates have no failure record and are unfinished work: "
            f"{unresolved[:10]}"
        )
    summary = {
        "task_id": TASK_ID,
        "run_root": str(root),
        "dates_declared": len(dates),
        "dates_completed": len(dates) - len(still),
        "dates_pending": 0,
        "dates_retained_failures": len(retained),
        "closed_by": "complete_run",
    }
    path = write_run_complete(root, summary, retained=retained)
    return {**summary, "run_complete": str(path)}


def run_dates(
    *,
    run_root: str | Path,
    freeze_path: str | Path,
    dates: Sequence[str] | None = None,
    workers: int | None = None,
    b02_roots: Sequence[str] = B02_ROOTS_DEFAULT,
    resume_only: bool = False,
) -> dict[str, Any]:
    root = Path(run_root)
    meta = init_run(
        run_root=root, freeze_path=freeze_path, dates=dates, workers=workers, b02_roots=b02_roots
    )
    manifest = json.loads((root / "MANIFEST.json").read_text())
    selected = list(manifest["dates"])
    todo = pending_dates(root, selected)
    worker_n = int(meta["workers"])
    payload = {"run_root": str(root), "b02_roots": list(b02_roots)}
    started = time.perf_counter()
    completed: list[str] = []
    failed: list[str] = []
    if todo:
        if worker_n <= 1:
            _init_worker(payload)
            for day in todo:
                record = _process_date(day)
                (completed if record["status"] == "completed" else failed).append(day)
                _progress(root, selected, completed, failed, started)
        else:
            with ProcessPoolExecutor(
                max_workers=worker_n, initializer=_init_worker, initargs=(payload,)
            ) as pool:
                futures = {pool.submit(_process_date, day): day for day in todo}
                for future in as_completed(futures):
                    day = futures[future]
                    try:
                        record = future.result()
                    except Exception:
                        _write_json(
                            root / "failed" / f"{day}.json",
                            {"date": day, "status": "failed", "error": traceback.format_exc()},
                        )
                        failed.append(day)
                        continue
                    (completed if record["status"] == "completed" else failed).append(day)
                    _progress(root, selected, completed, failed, started)
    still = pending_dates(root, selected)
    retained = retained_failures(root, still)
    unresolved = sorted(set(still) - {row["date"] for row in retained})
    summary = {
        "task_id": TASK_ID,
        "run_root": str(root),
        "dates_declared": len(selected),
        "dates_completed": len(selected) - len(still),
        "dates_pending": len(unresolved),
        "dates_retained_failures": len(retained),
        "dates_failed": sorted(set(failed)),
        "wall_seconds": time.perf_counter() - started,
        "workers": worker_n,
        "resume_only": resume_only,
    }
    _write_json(root / "PROGRESS.json", {**summary, "pending": unresolved[:50]})
    if not unresolved:
        # A run whose only pending dates carry retained failure records is
        # complete, and RUN_COMPLETE.json names them.
        write_run_complete(root, summary, retained=retained)
    return summary


def _progress(
    root: Path, selected: Sequence[str], completed: Sequence[str], failed: Sequence[str], started: float
) -> None:
    done = len(completed) + len(failed)
    elapsed = time.perf_counter() - started
    _write_json(
        root / "PROGRESS.json",
        {
            "task_id": TASK_ID,
            "dates_declared": len(selected),
            "dates_done_this_process": done,
            "dates_failed": len(failed),
            "elapsed_seconds": elapsed,
            "rate_seconds_per_date": elapsed / done if done else None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def write_run_complete(
    run_root: str | Path,
    summary: Mapping[str, Any],
    *,
    retained: Sequence[Mapping[str, Any]] = (),
) -> Path:
    """Close the run. Retained runtime failures are named here, never hidden:
    the declared-job arithmetic is written out so the missing shards of a failed
    date are visible in the same file that claims completion."""
    root = Path(run_root)
    manifest = json.loads((root / "MANIFEST.json").read_text())
    dates = list(manifest["dates"])
    candidates = len(manifest["candidates"])
    jobs = 0
    for day in dates:
        folder = root / "jobs" / day
        jobs += len(list(folder.glob("*.json.gz"))) if folder.is_dir() else 0
    failures = [dict(row) for row in retained]
    declared = len(dates) * candidates
    body = {
        "schema_version": "research-p15-17-run-complete-v2",
        "task_id": TASK_ID,
        "stage": STAGE,
        "run_root": str(root),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "dates": len(dates),
        "candidates": candidates,
        "declared_jobs": declared,
        "written_jobs": jobs,
        "dates_with_documents": len(dates) - len(failures),
        "retained_failures": failures,
        "retained_failure_dates": [row["date"] for row in failures],
        "jobs_absent_on_retained_failure_dates": len(failures) * candidates,
        "declared_jobs_reconciled": jobs + len(failures) * candidates == declared,
        "completed_with_retained_failures": bool(failures),
        "manifest_sha256": file_sha256(root / "MANIFEST.json"),
        "run_meta_sha256": file_sha256(root / "RUN_META.json"),
        "completed_by_code_sha256": code_identity()["code_sha256"],
        "summary": dict(summary),
    }
    return _write_json(root / "RUN_COMPLETE.json", body)


# --------------------------------------------------------------------------
# runner entry points (additive hook from runner.slice_run / resume / summarize)
# --------------------------------------------------------------------------


def slice_run(
    *,
    run_root: str | Path,
    manifest: str | Path,
    dates: Sequence[str] | None = None,
    workers: int | None = None,
    b02_roots: Sequence[str] = B02_ROOTS_DEFAULT,
) -> dict[str, Any]:
    return run_dates(
        run_root=run_root, freeze_path=manifest, dates=dates, workers=workers, b02_roots=b02_roots
    )


def resume(
    *,
    run_root: str | Path,
    manifest: str | Path,
    workers: int | None = None,
    b02_roots: Sequence[str] = B02_ROOTS_DEFAULT,
) -> dict[str, Any]:
    root = Path(run_root)
    meta_path = root / "RUN_META.json"
    if not meta_path.is_file():
        raise ContractError(f"{root} has no RUN_META.json; resume needs the same immutable run")
    meta = json.loads(meta_path.read_text())
    roots = meta.get("b02_roots") or list(b02_roots)
    declared = json.loads((root / "MANIFEST.json").read_text())["dates"]
    return run_dates(
        run_root=root,
        freeze_path=manifest,
        dates=declared,
        workers=workers or meta.get("workers"),
        b02_roots=roots,
        resume_only=True,
    )


def summarize(*, run_root: str | Path) -> dict[str, Any]:
    root = Path(run_root)
    manifest = json.loads((root / "MANIFEST.json").read_text())
    dates = list(manifest["dates"])
    pending = pending_dates(root, dates)
    counts = {"evaluated": 0, "unsupported": 0, "runtime_failure": 0}
    families: dict[str, dict[str, Any]] = {}
    for day in dates:
        path = daily_path(root, day)
        if not path.is_file():
            continue
        for row in json.loads(path.read_text())["rows"]:
            status = row["status"]
            counts[status] = counts.get(status, 0) + 1
            family = families.setdefault(
                row["family"], {"entries": 0, "baseline_entries": 0, "candidates": set()}
            )
            family["candidates"].add(row["candidate_id"])
            family["entries"] += int(row.get("candidate_fills") or 0)
            family["baseline_entries"] += int(row.get("baseline_fills") or 0)
    return {
        "task_id": TASK_ID,
        "run_root": str(root),
        "dates_declared": len(dates),
        "dates_complete": len(dates) - len(pending),
        "dates_pending": len(pending),
        "rows": counts,
        "run_complete": (root / "RUN_COMPLETE.json").is_file(),
        "families": {
            name: {
                "candidates": len(value["candidates"]),
                "entries": value["entries"],
                "baseline_entries": value["baseline_entries"],
            }
            for name, value in sorted(families.items())
        },
    }


# --------------------------------------------------------------------------
# fold evaluation
#
# Inner tuning (fit + tune days of the fold) is the ONLY evidence that chooses
# banks; outer test outcomes never reach the choice (A02). Holm runs across
# every candidate at the decision stage, and the moving block bootstrap uses the
# frozen seed 15022026, 2,000 draws and block length 5 through
# contracts.evaluation.
# --------------------------------------------------------------------------


def load_splits(freeze: Mapping[str, Any]) -> list[dict[str, Any]]:
    path = Path(freeze["ra4_splits"]["split_manifest_path"])
    if not path.is_file():  # the freeze pins an absolute worktree path
        path = _worktree_root() / Path(*path.parts[path.parts.index("implementation") :])
    document = json.loads(path.read_text())
    if document.get("schema_version") != "research-split-manifest-v1":
        raise ContractError(f"{path} is not the frozen split manifest")
    return [dict(row) for row in document["outer"]]


def load_daily_table(run_root: str | Path, dates: Sequence[str] | None = None) -> dict[str, dict[str, Any]]:
    """{candidate_id: {account_day: compact row}} from the per-date summaries."""
    root = Path(run_root)
    if dates is None:
        dates = json.loads((root / "MANIFEST.json").read_text())["dates"]
    table: dict[str, dict[str, Any]] = {}
    for day in dates:
        path = daily_path(root, day)
        if not path.is_file():
            continue
        for row in json.loads(path.read_text())["rows"]:
            table.setdefault(row["candidate_id"], {})[day] = row
    return table


def _float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


#: A session can be missing the inputs a family needs (a holiday with no native
#: events: `market_for_family` returns a view with no clock). That is a missing
#: input, not a defect in the candidate, and it must not read as a software
#: failure on the promotion gate. The messages are the contract's own.
INPUT_UNAVAILABLE_MARKERS = (
    "market has no cutoff clock",
    "no native account-day view",
)


def classify_failure(error: str | None) -> str:
    """`input_unavailable` for a missing required input, else `software_failure`.

    Pure: it reads a message, never a file. Neither class is ever a data
    rejection -- both keep their row, their reason and their terminal
    disposition; they differ only in which gate they inform.
    """
    text = str(error or "")
    if any(marker in text for marker in INPUT_UNAVAILABLE_MARKERS):
        return "input_unavailable"
    return "software_failure"


def paired_row(day: str, row: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """The one definition of a common complete day, used by both the in-memory
    table path and the streaming path, so they cannot drift apart.

    A complete day with no opportunity stays in the denominator with zero net
    points (S11); it is never dropped and never imputed.
    """
    if row is None or row.get("status") != "evaluated" or not row.get("complete"):
        return None
    candidate = _float(row.get("candidate_net_points"))
    baseline = _float(row.get("baseline_net_points"))
    if candidate is None or baseline is None:
        return None
    return _paired_body(day, row, candidate, baseline)


def paired_days(rows: Mapping[str, Any], days: Sequence[str]) -> list[dict[str, Any]]:
    """Common complete days of `days`, in that order."""
    out = []
    for day in days:
        paired = paired_row(day, rows.get(day))
        if paired is not None:
            out.append(paired)
    return out


def _paired_body(day: str, row: Mapping[str, Any], candidate: float, baseline: float) -> dict[str, Any]:
    return (
            {
                "day": day,
                "candidate": candidate,
                "baseline": baseline,
                "diff": candidate - baseline,
                "candidate_fills": int(row.get("candidate_fills") or 0),
                "baseline_fills": int(row.get("baseline_fills") or 0),
                "stress": _float(row.get("stress_net_points")),
                "control": _float(row.get("control_net_points")),
                "missed_move": int(row.get("missed_move") or 0),
                "stop_first": int(row.get("stop_first") or 0),
                "delay": _float(row.get("confirmation_delay_s_mean")),
                "nearest_approach_S": _float(row.get("nearest_approach_S_min")),
                "adverse_S": _float(row.get("adverse_S_before_favorable_0_5S_max")),
            }
        )


def _inner_from_paired(
    item: search.ResolvedCandidate, paired: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Inner tuning summary of one candidate over an already-paired day list.

    The single scoring core: the table path and the streaming path both call it
    with the same days in the same order, so they cannot diverge.
    """
    candidate_mean = float(np.mean([p["candidate"] for p in paired])) if paired else 0.0
    baseline_mean = float(np.mean([p["baseline"] for p in paired])) if paired else 0.0
    improvement = candidate_mean - baseline_mean
    entries = sum(p["candidate_fills"] for p in paired)
    baseline_entries = sum(p["baseline_fills"] for p in paired)
    delays = [p["delay"] for p in paired if p["delay"] is not None]
    return {
        "candidate_id": item.candidate_id,
        "family": item.family,
        "branch": item.branch,
        "bank": item.bank,
        "recipe_id": item.recipe_id,
        "parameters": dict(item.parameters),
        "changed_axis": item.changed_axis,
        "changed_axes": 1,
        "score": improvement,
        "inner_tuning": {
            "improvement_vs_b02": improvement,
            "candidate_mean_daily_net_points": candidate_mean,
            "baseline_mean_daily_net_points": baseline_mean,
            "common_complete_days": len(paired),
            "support_opportunities": entries,
            "support_days": sum(1 for p in paired if p["candidate_fills"] > 0),
            "entries": entries,
            "baseline_entries": baseline_entries,
            "frequency_of_baseline": (entries / baseline_entries) if baseline_entries else None,
            "mean_confirmation_delay_s": float(np.mean(delays)) if delays else None,
        },
    }




def inner_days(fold: Mapping[str, Any]) -> list[str]:
    return list(fold["fit"]) + list(fold["tune"])


def inner_row(
    item: search.ResolvedCandidate, rows: Mapping[str, Any], fold: Mapping[str, Any]
) -> dict[str, Any]:
    return _inner_from_paired(item, paired_days(rows, inner_days(fold)))


def pick_representative(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    """The 1% simplicity rule inside one bank: among candidates whose inner
    tuning score is within 1% of the best, take the simpler model (fewer changed
    axes, then fewer parameters), then the lower candidate ID lexically."""
    if not rows:
        return None
    ranked = refinement.rank_inner(rows)
    best = float(ranked[0].get("score") or 0.0)
    span = abs(best) * refinement.SIMPLICITY_THRESHOLD
    near = [row for row in ranked if float(row.get("score") or 0.0) >= best - span]
    near.sort(
        key=lambda row: (
            refinement.changed_axes(row),
            len(row.get("parameters") or {}),
            str(row.get("candidate_id")),
        )
    )
    return dict(near[0])


@dataclass(slots=True)
class CandidateSeries:
    """What one candidate needs from a whole run, in bounded memory.

    Only the paired numbers of its common complete days are kept -- never the
    job documents, never the raw daily rows. 148 supported candidates over 1,742
    declared sessions is a few hundred megabytes, so an evaluation of any run
    root is a single streaming pass.
    """

    candidate_id: str
    paired: dict[str, dict[str, Any]] = field(default_factory=dict)
    coverage_loss_days: set[str] = field(default_factory=set)
    runtime_failures: int = 0
    input_unavailable: int = 0
    failure_dates: dict[str, str] = field(default_factory=dict)
    status_counts: dict[str, int] = field(default_factory=dict)
    days_seen: int = 0

    def select(self, days: Sequence[str]) -> list[dict[str, Any]]:
        """The candidate's common complete days among `days`, in that order --
        the same list `paired_days` would return from the full table."""
        out = []
        for day in days:
            paired = self.paired.get(day)
            if paired is not None:
                out.append(paired)
        return out

    def coverage_loss(self, days: Sequence[str]) -> int:
        return sum(1 for day in days if day in self.coverage_loss_days)


def stream_run(
    run_root: str | Path,
    dates: Sequence[str] | None = None,
) -> tuple[dict[str, CandidateSeries], dict[str, Any]]:
    """One pass over `daily/<date>.json`, one date at a time.

    Returns the per-candidate series and a coverage report that states, in the
    run's own terms, how many declared dates produced a shard, how many did not
    and what the row statuses were. Dates without a shard are reported, never
    silently skipped.
    """
    root = Path(run_root)
    if dates is None:
        dates = json.loads((root / "MANIFEST.json").read_text())["dates"]
    series: dict[str, CandidateSeries] = {}
    statuses: dict[str, int] = {}
    failure_classes: dict[str, int] = {}
    missing: list[str] = []
    present = 0
    unavailable = 0
    for day in dates:
        path = daily_path(root, day)
        if not path.is_file():
            missing.append(day)
            continue
        document = json.loads(path.read_text())
        present += 1
        if document.get("session_available") is False:
            unavailable += 1
        for row in document["rows"]:
            item = series.get(row["candidate_id"])
            if item is None:
                item = series[row["candidate_id"]] = CandidateSeries(row["candidate_id"])
            status = str(row.get("status"))
            statuses[status] = statuses.get(status, 0) + 1
            item.status_counts[status] = item.status_counts.get(status, 0) + 1
            item.days_seen += 1
            if status in ("runtime_failure", "input_unavailable"):
                kind = (
                    "input_unavailable"
                    if status == "input_unavailable"
                    else classify_failure(_failure_error(root, day, row["candidate_id"]))
                )
                item.failure_dates[day] = kind
                if kind == "input_unavailable":
                    item.input_unavailable += 1
                else:
                    item.runtime_failures += 1
                failure_classes[kind] = failure_classes.get(kind, 0) + 1
            paired = paired_row(day, row)
            if paired is not None:
                item.paired[day] = paired
            elif row.get("baseline_net_points") is not None and not row.get("complete"):
                item.coverage_loss_days.add(day)
        del document
    report = {
        "run_root": str(root),
        "dates_declared": len(dates),
        "dates_with_daily_shard": present,
        "dates_without_daily_shard": missing,
        "sessions_unavailable": unavailable,
        "rows_by_status": statuses,
        "runtime_failure_classes": failure_classes,
        "candidates_seen": len(series),
    }
    return series, report


def _failure_error(run_root: Path, day: str, candidate_id: str) -> str | None:
    """The recorded error of one runtime-failure row. Only those documents are
    opened; the daily shard does not carry the message."""
    path = job_path(run_root, day, candidate_id)
    if not path.is_file():
        return None
    try:
        return read_gz(path).get("error")
    except OSError:
        return None


def inner_row_from_series(
    item: search.ResolvedCandidate, series: CandidateSeries | None, fold: Mapping[str, Any]
) -> dict[str, Any]:
    paired = series.select(inner_days(fold)) if series is not None else []
    return _inner_from_paired(item, paired)


def outer_row_from_series(
    item: search.ResolvedCandidate,
    series: CandidateSeries | None,
    folds: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if series is None:
        return _outer_from_paired(item, [[] for _ in folds], coverage_loss=0, runtime_failures=0)
    per_fold = [series.select(fold["test"]) for fold in folds]
    coverage_loss = sum(series.coverage_loss(fold["test"]) for fold in folds)
    row = _outer_from_paired(
        item, per_fold, coverage_loss=coverage_loss, runtime_failures=series.runtime_failures
    )
    # An input the session never had is explained coverage, not a software
    # failure and not an unexplained loss; it is reported with its dates.
    row["input_unavailable_days"] = series.input_unavailable
    row["input_unavailable_dates"] = sorted(
        day for day, kind in series.failure_dates.items() if kind == "input_unavailable"
    )
    row["software_failure_dates"] = sorted(
        day for day, kind in series.failure_dates.items() if kind == "software_failure"
    )
    return row


def select_for_fold_from_series(
    resolved: Sequence[search.ResolvedCandidate],
    series: Mapping[str, CandidateSeries],
    fold: Mapping[str, Any],
) -> dict[str, Any]:
    rows = [
        inner_row_from_series(item, series.get(item.candidate_id), fold)
        for item in resolved
        if item.supported
    ]
    return _select_from_inner_rows(rows, fold)


def _select_from_inner_rows(
    inner_rows: Sequence[Mapping[str, Any]], fold: Mapping[str, Any]
) -> dict[str, Any]:
    """At most two mechanism banks per family, from inner tuning only."""
    by_family: dict[str, list[dict[str, Any]]] = {}
    for row in inner_rows:
        by_family.setdefault(row["family"], []).append(row)
    selections: dict[str, Any] = {}
    for family, rows in sorted(by_family.items()):
        by_bank: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_bank.setdefault(row["bank"], []).append(row)
        representatives = [
            rep for rep in (pick_representative(group) for group in by_bank.values()) if rep
        ]
        chosen = refinement.select_banks(family, representatives, max_banks=2)
        selections[family] = {
            "selected_banks": chosen,
            "representatives": [
                {
                    "bank": rep["bank"],
                    "candidate_id": rep["candidate_id"],
                    "score": rep["score"],
                    "inner_tuning": rep["inner_tuning"],
                }
                for rep in sorted(representatives, key=lambda row: str(row["bank"]))
            ],
            "retained_baseline": not chosen,
        }
    return {
        "outer_fold": fold["test_year"],
        "inner_days": len(fold["fit"]) + len(fold["tune"]),
        "families": selections,
        "evidence": "inner fit+tune days only",
    }




def select_for_fold(
    resolved: Sequence[search.ResolvedCandidate],
    table: Mapping[str, Mapping[str, Any]],
    fold: Mapping[str, Any],
) -> dict[str, Any]:
    """Inner-only bank selection over an in-memory daily table."""
    rows = [
        inner_row(item, table.get(item.candidate_id, {}), fold)
        for item in resolved
        if item.supported
    ]
    return _select_from_inner_rows(rows, fold)


def _outer_from_paired(
    item: search.ResolvedCandidate,
    per_fold: Sequence[Sequence[Mapping[str, Any]]],
    *,
    coverage_loss: int,
    runtime_failures: int,
) -> dict[str, Any]:
    """Outer evidence for the decision stage, over already-paired test days, one
    list per outer fold. Never consumed by select_for_fold (A02)."""
    diffs: list[float] = []
    block_improvements: list[float] = []
    supported_blocks = 0
    days = 0
    entries = 0
    baseline_entries = 0
    resolved_opportunities = 0
    stress_diffs: list[float] = []
    control_diffs: list[float] = []
    missed = 0
    stopped = 0
    nearest: list[float] = []
    adverse: list[float] = []
    for paired in per_fold:
        if not paired:
            continue
        supported_blocks += 1
        block_improvements.append(float(np.mean([p["diff"] for p in paired])))
        diffs.extend(p["diff"] for p in paired)
        days += len(paired)
        entries += sum(p["candidate_fills"] for p in paired)
        baseline_entries += sum(p["baseline_fills"] for p in paired)
        resolved_opportunities += sum(p["candidate_fills"] for p in paired)
        stress_diffs.extend(
            p["stress"] - p["baseline"] for p in paired if p["stress"] is not None
        )
        control_diffs.extend(
            p["control"] - p["baseline"] for p in paired if p["control"] is not None
        )
        missed += sum(p["missed_move"] for p in paired)
        stopped += sum(p["stop_first"] for p in paired)
        nearest.extend(p["nearest_approach_S"] for p in paired if p["nearest_approach_S"] is not None)
        adverse.extend(p["adverse_S"] for p in paired if p["adverse_S"] is not None)
    mean_diff = float(np.mean(diffs)) if diffs else 0.0
    stress_mean = float(np.mean(stress_diffs)) if stress_diffs else None

    return {
        "candidate_id": item.candidate_id,
        "family": item.family,
        "branch": item.branch,
        "bank": item.bank,
        "recipe_id": item.recipe_id,
        "parameters": dict(item.parameters),
        "changed_axes": 1,
        "daily_diff": diffs,
        "mean_diff": mean_diff,
        "block_improvements": block_improvements,
        "supported_outer_blocks": supported_blocks,
        "eligible_test_days": days,
        "resolved_opportunities": resolved_opportunities,
        "candidate_entries": entries,
        "baseline_entries": baseline_entries,
        "software_causality_pass": runtime_failures == 0,
        "runtime_failures": runtime_failures,
        "cost_stress_mean_diff": stress_mean,
        "cost_stress_sign_reversal": bool(
            stress_mean is not None and mean_diff > 0 and stress_mean <= 0
        ),
        "control_mean_diff": float(np.mean(control_diffs)) if control_diffs else None,
        "unexplained_coverage_loss": coverage_loss > 0,
        "coverage_loss_days": coverage_loss,
        "missed_move": missed,
        "stop_first": stopped,
        "nearest_approach_S": min(nearest) if nearest else None,
        "adverse_S_before_favorable_0_5S": max(adverse) if adverse else None,
        "objective_reached": None,
    }




def _coverage_loss_days(rows: Mapping[str, Any], days: Sequence[str]) -> int:
    """Test days where the paired baseline exists but the candidate row is not a
    usable common complete day: unexplained input coverage loss."""
    lost = 0
    for day in days:
        row = rows.get(day)
        if row is None:
            continue
        if row.get("baseline_net_points") is not None and not row.get("complete"):
            lost += 1
    return lost


def outer_row(
    item: search.ResolvedCandidate,
    rows: Mapping[str, Any],
    folds: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    per_fold = [paired_days(rows, fold["test"]) for fold in folds]
    coverage_loss = sum(_coverage_loss_days(rows, fold["test"]) for fold in folds)
    # The table path classifies from the recorded terminal disposition alone;
    # the streaming path additionally repairs a legacy `runtime_failure` row by
    # reading the error the job document recorded.
    unavailable = sorted(day for day, row in rows.items() if row.get("status") == "input_unavailable")
    failures = sorted(day for day, row in rows.items() if row.get("status") == "runtime_failure")
    row = _outer_from_paired(
        item, per_fold, coverage_loss=coverage_loss, runtime_failures=len(failures)
    )
    row["input_unavailable_days"] = len(unavailable)
    row["input_unavailable_dates"] = unavailable
    row["software_failure_dates"] = failures
    return row


def family_thresholds(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, float]]:
    """RETENTION.md thresholds are family-relative: the family median missed-move
    share and the family baseline stop-first share, both fixed before any
    candidate result is read into a disposition."""
    by_family: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        by_family.setdefault(row["family"], []).append(row)
    out: dict[str, dict[str, float]] = {}
    for family, group in by_family.items():
        missed_shares = [
            row["missed_move"] / row["candidate_entries"]
            for row in group
            if row["candidate_entries"]
        ]
        stop_shares = [
            row["stop_first"] / row["candidate_entries"] for row in group if row["candidate_entries"]
        ]
        out[family] = {
            "family_median_missed_move_share": float(np.median(missed_shares)) if missed_shares else 0.0,
            "family_baseline_stop_first_share": float(np.median(stop_shares)) if stop_shares else 0.0,
        }
    return out


def decide(
    rows: Sequence[Mapping[str, Any]],
    *,
    holm_fn: Any = None,
    bootstrap_fn: Any = None,
) -> list[dict[str, Any]]:
    """Promotion at the decision stage: the frozen bootstrap for every candidate,
    Holm across all of them, then the promotion gates with support sensitivity
    at half and twice the gate and the frequency floor."""
    kwargs: dict[str, Any] = {}
    if holm_fn is not None:
        kwargs["holm_fn"] = holm_fn
    if bootstrap_fn is not None:
        kwargs["bootstrap_fn"] = bootstrap_fn
    stage_trials = []
    for row in rows:
        computed = refinement.centered_bootstrap_pvalue(
            row.get("daily_diff") or (),
            **({"bootstrap_fn": bootstrap_fn} if bootstrap_fn is not None else {}),
        )
        stage_trials.append({"candidate_id": row["candidate_id"], "p_raw": computed["p_raw"]})
    thresholds = family_thresholds(rows)
    out = []
    for row in rows:
        verdict = refinement.evaluate_promotion(row, stage_trials, **kwargs)
        diagnostics = {
            **row,
            **thresholds.get(row["family"], {}),
            "missed_move_share": (row["missed_move"] / row["candidate_entries"])
            if row["candidate_entries"]
            else 0.0,
            "stop_first_share": (row["stop_first"] / row["candidate_entries"])
            if row["candidate_entries"]
            else 0.0,
        }
        attribution = (
            [] if verdict["promoted"] else refinement.attribute_failure(diagnostics)
        )
        out.append(
            {
                **row,
                "promotion": verdict,
                "failure_attribution": attribution,
                "first_attribution": attribution[0] if attribution else None,
                "stage_trials": len(stage_trials),
            }
        )
    return out


def pareto_set(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Quality-frequency Pareto set: no other candidate is at least as good on
    both the mean paired improvement and the entry count and better on one."""
    out = []
    for row in rows:
        quality = float(row.get("mean_diff") or 0.0)
        frequency = float(row.get("candidate_entries") or 0)
        dominated = any(
            float(other.get("mean_diff") or 0.0) >= quality
            and float(other.get("candidate_entries") or 0) >= frequency
            and (
                float(other.get("mean_diff") or 0.0) > quality
                or float(other.get("candidate_entries") or 0) > frequency
            )
            for other in rows
            if other["candidate_id"] != row["candidate_id"]
        )
        if not dominated:
            out.append(
                {
                    "candidate_id": row["candidate_id"],
                    "family": row["family"],
                    "bank": row["bank"],
                    "mean_diff": quality,
                    "candidate_entries": int(frequency),
                    "baseline_entries": int(row.get("baseline_entries") or 0),
                }
            )
    return sorted(out, key=lambda row: (row["family"], -row["mean_diff"], row["candidate_id"]))


def retention_set(
    resolved: Sequence[search.ResolvedCandidate],
    decided: Sequence[Mapping[str, Any]],
    selections: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """RETENTION rule 1 and 5: nothing is discarded; every registry branch keeps
    a status and its first attribution."""
    chosen: set[str] = set()
    for fold in selections:
        for family in fold["families"].values():
            for bank in family["selected_banks"]:
                chosen.add(str(bank["candidate_id"]))
    by_id = {row["candidate_id"]: row for row in decided}
    out = []
    for item in resolved:
        row = by_id.get(item.candidate_id)
        if not item.supported:
            status = "inactive_retained"
            attribution = ["coverage"]
            reason = item.unsupported_reason
        elif row is None:
            status = "inactive_retained"
            attribution = ["coverage"]
            reason = "no evaluated day"
        elif row["promotion"]["promoted"]:
            status = "active_selected"
            attribution = []
            reason = None
        elif item.candidate_id in chosen:
            status = "active_selected"
            attribution = row["failure_attribution"]
            reason = "selected for refinement by inner tuning"
        else:
            status = "inactive_retained"
            attribution = row["failure_attribution"]
            reason = row["promotion"]["reason"]
        out.append(
            {
                "candidate_id": item.candidate_id,
                "family": item.family,
                "branch": item.branch,
                "bank": item.bank,
                "status": status,
                "disposition": None if row is None else row["promotion"]["disposition"],
                "failure_attribution": attribution,
                "first_attribution": attribution[0] if attribution else None,
                "reason": reason,
            }
        )
    return out


def refinement_allowlist(
    selections: Sequence[Mapping[str, Any]], folds: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Per fold, the selected banks and the neighborhoods refinement.py expands."""
    by_year = {int(fold["test_year"]): fold for fold in folds}
    out = []
    for fold_selection in selections:
        year = int(fold_selection["outer_fold"])
        fold = by_year[year]
        fit_days = list(fold["fit"]) + list(fold["tune"])
        cutoff = fit_days[-1] if fit_days else None
        families = []
        for family, body in sorted(fold_selection["families"].items()):
            banks = body["selected_banks"]
            neighborhoods = []
            for bank in banks:
                neighborhoods.append(
                    {
                        "bank": bank["bank"],
                        "candidate_id": bank["candidate_id"],
                        "recipe_id": bank["recipe_id"],
                        "parameters": bank["parameters"],
                        "neighbors": refinement.neighborhood_values(
                            str(bank["recipe_id"]), bank["parameters"]
                        ),
                    }
                )
            families.append(
                {
                    "family": family,
                    "selected_banks": banks,
                    "retained_baseline": body["retained_baseline"],
                    "neighborhoods": neighborhoods,
                }
            )
        out.append(
            {
                "outer_fold": year,
                "inner_cutoff_day": cutoff,
                "families": families,
            }
        )
    return {
        "schema_version": ALLOWLIST_SCHEMA,
        "task_id": TASK_ID,
        "selection_evidence": "inner fit+tune only; outer test outcomes excluded",
        "max_banks_per_family": 2,
        "folds": out,
    }


def trial_records(
    resolved: Sequence[search.ResolvedCandidate],
    decided: Sequence[Mapping[str, Any]],
    selections: Sequence[Mapping[str, Any]],
    folds: Sequence[Mapping[str, Any]],
    *,
    identity: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """One row for every registered candidate in every outer fold, plus the
    decision-stage row. Unsupported, not-applicable and runtime-failed
    candidates all keep a row; a runtime failure is never a data rejection."""
    by_id = {row["candidate_id"]: row for row in decided}
    selection_by_fold = {int(row["outer_fold"]): row for row in selections}
    rows: list[dict[str, Any]] = []
    for fold in folds:
        year = int(fold["test_year"])
        chosen = {
            str(bank["candidate_id"])
            for family in selection_by_fold[year]["families"].values()
            for bank in family["selected_banks"]
        }
        for item in resolved:
            decided_row = by_id.get(item.candidate_id)
            if not item.supported:
                status, disposition, reason = "unsupported", "unsupported_owned_input", item.unsupported_reason
                attribution = ["coverage"]
            elif decided_row is None:
                status, disposition, reason = "not_applicable", "inconclusive_support", "no evaluated day"
                attribution = ["coverage"]
            elif decided_row["runtime_failures"]:
                status, disposition, reason = "runtime_failure", "rejected_by_evidence", "runtime failure"
                attribution = decided_row["failure_attribution"]
            elif item.candidate_id in chosen:
                status, disposition, reason = "attempted", "active_selected", "selected by inner tuning"
                attribution = []
            else:
                status = "attempted"
                disposition = "deselected"
                reason = "not among the two banks chosen for this family by inner tuning"
                attribution = decided_row["failure_attribution"] or ["support"]
            rows.append(
                refinement.make_trial_record(
                    trial_id=f"P15-17:{year}:{item.candidate_id}",
                    parent_trial_ids=[],
                    family=item.family,
                    branch=item.branch,
                    outer_fold=year,
                    stage="breadth",
                    bank=item.bank,
                    parameters=dict(item.parameters),
                    code_hash=identity["code_sha256"],
                    data_hash=identity["bank_sha256"],
                    plan_hash=identity["freeze_sha256"],
                    fit_window=[fold["fit"][0], fold["fit"][-1]] if fold["fit"] else None,
                    tune_window=[fold["tune"][0], fold["tune"][-1]] if fold["tune"] else None,
                    calibration_window=[fold["calibrate"][0], fold["calibrate"][-1]]
                    if fold["calibrate"]
                    else None,
                    outcome_exposure_cutoff=fold["test"][-1] if fold["test"] else None,
                    candidate_population_counts={
                        "candidate_entries": None if decided_row is None else decided_row["candidate_entries"],
                        "baseline_entries": None if decided_row is None else decided_row["baseline_entries"],
                        "eligible_test_days": None if decided_row is None else decided_row["eligible_test_days"],
                    },
                    score=None if decided_row is None else decided_row["mean_diff"],
                    loss=None,
                    support={} if decided_row is None else decided_row["promotion"]["support_sensitivity"],
                    test_metrics={} if decided_row is None else {
                        "mean_diff": decided_row["mean_diff"],
                        "p_raw": decided_row["promotion"]["p_raw"],
                        "p_holm": decided_row["promotion"]["p_holm"],
                        "ci_low": decided_row["promotion"]["ci_low"],
                        "ci_high": decided_row["promotion"]["ci_high"],
                    },
                    reason=reason,
                    disposition=disposition,
                    runtime=None,
                    artifacts={"run_root": identity["run_root"]},
                    failure_attribution=attribution,
                    candidate_id=item.candidate_id,
                    recipe_id=item.recipe_id,
                    status=status,
                )
            )
    return rows


def _table(header: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    out = ["| " + " | ".join(str(item) for item in header) + " |"]
    out.append("| " + " | ".join("---" for _ in header) + " |")
    for row in rows:
        out.append("| " + " | ".join("" if item is None else str(item) for item in row) + " |")
    return "\n".join(out)


def family_report(
    family: str,
    decided: Sequence[Mapping[str, Any]],
    retention: Sequence[Mapping[str, Any]],
    selections: Sequence[Mapping[str, Any]],
    *,
    run_root: str,
    report_path: str,
) -> str:
    rows = [row for row in decided if row["family"] == family]
    held = [row for row in retention if row["family"] == family]
    phase_rows = [
        [
            family,
            row["candidate_id"],
            row["eligible_test_days"],
            "not claimed (no source-exact comparison)",
            row["promotion"]["disposition"],
            report_path,
        ]
        for row in sorted(rows, key=lambda row: row["candidate_id"])
    ]
    audit_rows = [
        [
            family,
            TASK_ID,
            row["promotion"]["disposition"],
            "pass" if row["software_causality_pass"] else "fail",
            row["coverage_loss_days"],
            0,
            f"support {row['resolved_opportunities']} opps / {row['eligible_test_days']} days / "
            f"{row['supported_outer_blocks']} blocks; first attribution "
            f"{row.get('first_attribution')}; baseline retained",
        ]
        for row in sorted(rows, key=lambda row: row["candidate_id"])
    ]
    lines = [
        f"# P15-17 breadth — {family}",
        "",
        f"Run root `{run_root}`. Every number below is a cell of "
        f"`BREADTH_RESULTS.json` in the same run root; per-day evidence is "
        f"`daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.",
        "",
        "## PHASE table",
        "",
        _table(
            ["family", "variant", "n", "faithful_disagreements", "status", "report path"],
            phase_rows,
        ),
        "",
        "## Audit table",
        "",
        _table(
            ["family", "id", "verdict", "fixture", "leakage", "proxy-as-faithful", "notes"],
            audit_rows,
        ),
        "",
        "## Quality–frequency Pareto set",
        "",
        _table(
            ["candidate_id", "bank", "mean paired improvement (points/day)", "entries", "baseline entries"],
            [
                [row["candidate_id"], row["bank"], f"{row['mean_diff']:.4f}", row["candidate_entries"], row["baseline_entries"]]
                for row in pareto_set(rows)
            ],
        ),
        "",
        "## Retention set",
        "",
        _table(
            ["candidate_id", "branch", "bank", "status", "first attribution", "reason"],
            [
                [row["candidate_id"], row["branch"], row["bank"], row["status"], row["first_attribution"], row["reason"]]
                for row in sorted(held, key=lambda row: row["candidate_id"])
            ],
        ),
        "",
        "## Fold selections (inner tuning only)",
        "",
        _table(
            ["outer fold", "selected banks", "retained baseline"],
            [
                [
                    fold["outer_fold"],
                    ", ".join(
                        f"{bank['bank']}:{bank['candidate_id']}"
                        for bank in fold["families"].get(family, {}).get("selected_banks", [])
                    )
                    or "none",
                    fold["families"].get(family, {}).get("retained_baseline"),
                ]
                for fold in selections
            ],
        ),
        "",
    ]
    return "\n".join(lines)


def reconcile_jobs(
    run_root: str | Path,
    *,
    dates: Sequence[str] | None = None,
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    """Stream every job document of the run, one date and family at a time.

    Opens each `jobs/<date>/<candidate>.json.gz`, checks A04 on both sides of
    the pairing (opportunities == fills + exclusions, daily net points == the sum
    of the filled entries), tallies exclusion and exit reasons per family, and
    reconciles the declared job count against what is on disk. One document is
    held at a time; nothing is accumulated but counters.
    """
    root = Path(run_root)
    manifest = json.loads((root / "MANIFEST.json").read_text())
    if dates is None:
        dates = list(manifest["dates"])
    candidates = list(manifest["candidates"])
    families: dict[str, dict[str, Any]] = {}
    statuses: dict[str, int] = {}
    pairing_sources: dict[str, int] = {}
    missing: list[dict[str, str]] = []
    violations: list[dict[str, Any]] = []
    identity_mismatches: list[dict[str, Any]] = []
    dates_without_jobs: list[str] = []
    documents = 0
    # unique artifacts: the sanitized file name must be injective over the bank,
    # or two candidates would share one document.
    names: dict[str, str] = {}
    collisions: list[dict[str, str]] = []
    for candidate_id in candidates:
        name = sanitize_candidate_id(candidate_id)
        if name in names:
            collisions.append({"name": name, "candidates": f"{names[name]} + {candidate_id}"})
        names[name] = candidate_id
    for day in dates:
        folder = root / "jobs" / day
        if not folder.is_dir():
            dates_without_jobs.append(day)
            continue
        for candidate_id in candidates:
            path = job_path(root, day, candidate_id)
            if not path.is_file():
                missing.append({"date": day, "candidate_id": candidate_id})
                continue
            job = read_gz(path)
            documents += 1
            # the artifact must say which declared job it is (no substitution)
            if job.get("candidate_id") is not None and (
                job.get("candidate_id") != candidate_id or job.get("account_day") not in (None, day)
            ):
                identity_mismatches.append(
                    {
                        "date": day,
                        "expected_candidate_id": candidate_id,
                        "document_candidate_id": job.get("candidate_id"),
                        "document_account_day": job.get("account_day"),
                    }
                )
            status = str(job.get("status"))
            statuses[status] = statuses.get(status, 0) + 1
            source = str(job.get("pairing_baseline_source"))
            pairing_sources[source] = pairing_sources.get(source, 0) + 1
            family = families.setdefault(
                job.get("family") or "?",
                {
                    "documents": 0,
                    "candidate_opportunities": 0,
                    "candidate_fills": 0,
                    "baseline_opportunities": 0,
                    "baseline_fills": 0,
                    "candidate_zero_days": 0,
                    "unknown_episodes": 0,
                    "verdict_changed": 0,
                    "exclusions": {},
                    "exit_reasons": {},
                    "runtime_failures": 0,
                },
            )
            family["documents"] += 1
            if status == "runtime_failure":
                family["runtime_failures"] += 1
            if job.get("verdict_change", {}).get("changed"):
                family["verdict_changed"] += 1
            for side, prefix in (("candidate", "candidate"), ("baseline", "baseline")):
                body = job.get(side)
                if not body:
                    continue
                opportunities = int(body["opportunities"])
                fills = int(body["fills"])
                exclusions = body.get("exclusions") or []
                if opportunities != fills + len(exclusions):
                    violations.append(
                        {
                            "date": day,
                            "candidate_id": candidate_id,
                            "side": side,
                            "reason": "opportunities != fills + exclusions",
                            "opportunities": opportunities,
                            "fills": fills,
                            "exclusions": len(exclusions),
                        }
                    )
                total = sum(Decimal(str(row["net_points"])) for row in body.get("entries") or [])
                if Decimal(str(body["net_points"])) != total:
                    violations.append(
                        {
                            "date": day,
                            "candidate_id": candidate_id,
                            "side": side,
                            "reason": "net points != sum of filled entries",
                        }
                    )
                family[f"{prefix}_opportunities"] += opportunities
                family[f"{prefix}_fills"] += fills
                if side == "candidate":
                    family["candidate_zero_days"] += int(bool(body.get("zero_day")))
                    family["unknown_episodes"] += int(body.get("unknown") or 0)
                    for name, count in (body.get("exclusion_counts") or {}).items():
                        family["exclusions"][name] = family["exclusions"].get(name, 0) + int(count)
                    for name, count in (body.get("exit_reasons") or {}).items():
                        family["exit_reasons"][name] = family["exit_reasons"].get(name, 0) + int(count)
            del job
    declared = len(dates) * len(candidates)
    absent = len(dates_without_jobs) * len(candidates)
    report = {
        "schema_version": "research-p15-17-job-reconciliation-v1",
        "task_id": TASK_ID,
        "run_root": str(root),
        "dates_declared": len(dates),
        "candidates": len(candidates),
        "declared_jobs": declared,
        "documents_read": documents,
        "dates_without_a_jobs_directory": dates_without_jobs,
        "jobs_absent_on_those_dates": absent,
        "jobs_missing_individually": missing,
        "declared_jobs_reconciled": documents + absent + len(missing) == declared,
        "rows_by_status": statuses,
        "terminal_dispositions": {
            **statuses,
            "absent_on_retained_failure_dates": absent,
            "missing_without_a_record": len(missing),
        },
        "terminal_dispositions_cover_declared": documents + absent + len(missing) == declared,
        "artifact_name_collisions": collisions,
        "identity_mismatches": identity_mismatches,
        "pairing_baseline_sources": pairing_sources,
        "a04_violations": violations,
        "families": {name: body for name, body in sorted(families.items())},
    }
    if out_path is not None:
        _write_json(Path(out_path), report)
    return report


def _run_complete_summary(run_root: str | Path) -> dict[str, Any] | None:
    """The run's own completion record, including any retained runtime failures,
    carried into the results so a reader of BREADTH_RESULTS sees them."""
    path = Path(run_root) / "RUN_COMPLETE.json"
    if not path.is_file():
        return None
    body = json.loads(path.read_text())
    return {
        "path": str(path),
        "sha256": file_sha256(path),
        "completed_at": body.get("completed_at"),
        "dates": body.get("dates"),
        "written_jobs": body.get("written_jobs"),
        "declared_jobs": body.get("declared_jobs"),
        "declared_jobs_reconciled": body.get("declared_jobs_reconciled"),
        "retained_failures": body.get("retained_failures"),
    }


def evaluate_run(
    *,
    run_root: str | Path,
    freeze_path: str | Path,
    out_dir: str | Path,
    dates: Sequence[str] | None = None,
) -> dict[str, Any]:
    """The whole fold evaluation of a run root, streaming.

    A pure function of the run root: it reads `MANIFEST.json`, the per-date
    daily shards and (optionally) `RUN_COMPLETE.json`, and writes the four
    deliverables into `out_dir`. Point it at another run root and it re-runs in
    minutes; nothing about it is specific to one attempt.
    """
    root = Path(run_root)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    freeze = load_freeze(freeze_path)
    folds = load_splits(freeze)
    resolved = search.resolve_bank()
    series, coverage = stream_run(root, dates)
    selections = [select_for_fold_from_series(resolved, series, fold) for fold in folds]
    outer = [
        outer_row_from_series(item, series.get(item.candidate_id), folds)
        for item in resolved
        if item.supported
    ]
    decided = decide(outer)
    retention = retention_set(resolved, decided, selections)
    allowlist = refinement_allowlist(selections, folds)
    manifest = json.loads((root / "MANIFEST.json").read_text())
    identity = {
        "code_sha256": manifest["code_sha256"],
        "bank_sha256": manifest["bank_sha256"],
        "freeze_sha256": manifest["freeze_sha256"],
        "run_root": str(root),
    }
    ledger_path = out / "TRIALS.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = refinement.TrialLedger(ledger_path)
    for record in trial_records(resolved, decided, selections, folds, identity=identity):
        ledger.append(record)
    results = {
        "schema_version": RESULTS_SCHEMA,
        "task_id": TASK_ID,
        "stage": STAGE,
        "run_root": str(root),
        "identity": identity,
        "coverage": coverage,
        "run_complete": _run_complete_summary(root),
        "dates_evaluated": coverage["dates_with_daily_shard"],
        "candidates": len(resolved),
        "supported": sum(1 for item in resolved if item.supported),
        "unsupported": [
            {"candidate_id": item.candidate_id, "reason": item.unsupported_reason}
            for item in resolved
            if not item.supported
        ],
        "uncertainty": freeze["uncertainty"],
        "promotion_gates": freeze["promotion_gates"],
        "folds": [
            {"test_year": fold["test_year"], "test_days": len(fold["test"]), "inner_days": len(fold["fit"]) + len(fold["tune"])}
            for fold in folds
        ],
        "selections": selections,
        "decisions": [
            {key: value for key, value in row.items() if key != "daily_diff"} for row in decided
        ],
        "pareto": pareto_set(decided),
        "retention": retention,
        "family_thresholds": family_thresholds(outer),
    }
    _write_json(out / "BREADTH_RESULTS.json", results)
    _write_json(out / "REFINEMENT_ALLOWLIST.json", allowlist)
    reports = out / "FAMILY_REPORTS"
    reports.mkdir(parents=True, exist_ok=True)
    for family in sorted({item.family for item in resolved}):
        body = family_report(
            family,
            decided,
            retention,
            selections,
            run_root=str(root),
            report_path=str(reports / f"{family}.md"),
        )
        (reports / f"{family}.md").write_text(body)
    return {
        "coverage": coverage,
        "trials": sum(1 for _ in ledger_path.read_text().splitlines() if _.strip()),
        "results": str(out / "BREADTH_RESULTS.json"),
        "allowlist": str(out / "REFINEMENT_ALLOWLIST.json"),
        "family_reports": sorted(path.name for path in reports.glob("*.md")),
        "promoted": [row["candidate_id"] for row in decided if row["promotion"]["promoted"]],
    }


def semantic_run_id(
    *,
    freeze_path: str | Path,
    b02_roots: Sequence[str] = B02_ROOTS_DEFAULT,
    n_dates: int,
) -> str:
    """WORKFLOW run naming: the first 16 hex of SHA256 of the canonical run
    manifest. Deliberately independent of the code hash, so a code fix does not
    move the immutable run root; the code identity is bound in MANIFEST.json."""
    freeze = load_freeze(freeze_path)
    canonical = {
        "task_id": TASK_ID,
        "stage": STAGE,
        "freeze_sha256": file_sha256(freeze_path),
        "bank_sha256": freeze["ra3_bank"]["sha256"],
        "split_manifest_sha256": freeze["ra4_splits"]["split_manifest_sha256"],
        "evaluation_protocol_sha256": freeze["ra4_splits"]["evaluation_protocol_sha256"],
        "b02_roots": sorted(str(item) for item in b02_roots),
        "dates": int(n_dates),
        "pairing_baseline": freeze["pairing_baseline"],
    }
    return sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()[:16]
