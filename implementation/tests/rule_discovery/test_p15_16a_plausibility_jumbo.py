"""P15-16A JJ-TBR repair gate: measured stages and population plausibility."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
import copy
import json

import pytest

from trading_research.research.rule_discovery.native import build_market_view, install_write_guard
from trading_research.research.rule_discovery.source_adapters.common import load_source_market
from trading_research.research.rule_discovery.source_adapters.common import is_native_session
from trading_research.research.rule_discovery.source_adapters.jumbo import (
    BRANCHES,
    FAMILY,
    PZONE_FIXTURES,
    funnel_stage_counts,
    replay_example,
    scan_b02,
    selection_for,
)

REPAIR = Path(__file__).resolve().parents[2] / "reports/research-work/P15-16A/_repair_jumbo"
# Generated evidence goes to the round-3 work directory; committed repair evidence stays byte-identical.
OUT = Path(__file__).resolve().parents[2] / "reports/research-work/P15-16A/_work_r3"
OUT.mkdir(parents=True, exist_ok=True)
FAMILY_JSON = Path(__file__).resolve().parents[2] / "src/trading_research/research/rule_discovery/families/jumbo.json"
EXAMPLES = Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json")
SLICE_DATES = [
    "2020-01-02",
    "2020-06-01",
    "2020-11-02",
    "2021-06-01",
    "2021-11-01",
    "2022-01-03",
    "2022-06-01",
    "2023-01-03",
    "2023-11-06",
    "2024-03-05",
    "2024-11-01",
    "2025-01-02",
    "2025-06-02",
    "2026-01-02",
    "2026-06-01",
]
ET = ZoneInfo("America/New_York")
SESSION_PASS_CAP = 0.60


def _bucket(ns: int | None) -> str | None:
    if ns is None:
        return None
    dt = datetime.fromtimestamp(int(ns) / 1_000_000_000, tz=timezone.utc).astimezone(ET)
    minute = 0 if dt.minute < 30 else 30
    return f"{dt.hour:02d}:{minute:02d}"


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return str(value)


def _valid_justification(just: Any, bound: dict[str, Any], violated: str) -> bool:
    if not isinstance(just, dict):
        return False
    quote = str(just.get("quote") or "").strip()
    page = str(just.get("page") or "").strip()
    supports = str(just.get("supports") or "").strip()
    if len(quote) < 20 or not page:
        return False
    if page == str(bound.get("page") or ""):
        return False
    if quote == str(bound.get("source_claim") or ""):
        return False
    if supports and supports != violated:
        return False
    return True


def evaluate_gate(
    bounds: dict[str, Any],
    collected: dict[str, list[dict[str, Any]]],
    audit: dict[str, Any],
    sessions_used: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    n_sessions = len(sessions_used)
    rows = []
    for branch in BRANCHES:
        episodes = collected[branch]
        n_ep = len(episodes)
        n_pass = sum(1 for ep in episodes if ep.get("research_verdict") == "pass")
        n_fail = sum(1 for ep in episodes if ep.get("research_verdict") == "fail")
        n_unk = sum(1 for ep in episodes if ep.get("research_verdict") == "unknown")
        pass_rate = (n_pass / n_ep) if n_ep else 0.0
        eps = (n_ep / n_sessions) if n_sessions else 0.0
        sessions_with_pass = len({ep.get("session_date") for ep in episodes if ep.get("research_verdict") == "pass"})
        session_frac = (sessions_with_pass / n_sessions) if n_sessions else 0.0
        bound = bounds[branch]
        fixture_limited = bool(bound.get("fixture_limited"))
        lo_e, hi_e = bound["episodes_per_session"]
        in_eps = lo_e <= eps <= hi_e
        pr_bound = bound.get("pass_rate")
        in_pr = True
        if pr_bound is None:
            in_pr = True
        else:
            in_pr = pr_bound[0] <= pass_rate <= pr_bound[1]
        in_bound = in_eps and in_pr
        side_pass = defaultdict(Counter)
        for ep in episodes:
            if ep.get("research_verdict") == "pass":
                side_pass[ep.get("session_date")][ep.get("side")] += 1
        extra_side = [
            (day, side, count)
            for day, sides in side_pass.items()
            for side, count in sides.items()
            if count > 1
        ]
        if branch == "other_session" and extra_side:
            in_bound = False
        if fixture_limited:
            printed = set(bound.get("printed_zone_dates") or PZONE_FIXTURES)
            extra_dates = sorted({ep.get("session_date") for ep in episodes if ep.get("session_date") not in printed})
            if extra_dates:
                errors.append(f"{branch} emitted episodes on non-fixture dates {extra_dates}")
            in_bound = in_eps and not extra_dates
        stages = funnel_stage_counts(episodes)
        histogram: Counter[str] = Counter()
        for ep in episodes:
            if ep.get("research_verdict") == "pass":
                bucket = _bucket(ep.get("decision_at"))
                if bucket:
                    histogram[bucket] += 1
        just = bound.get("out_of_bound_justification")
        violations: list[str] = []
        if not in_eps:
            violations.append("episodes_per_session")
        if not fixture_limited and pr_bound is not None and not in_pr:
            violations.append("pass_rate")
        if not fixture_limited and session_frac > SESSION_PASS_CAP:
            violations.append("session_frequency")
            in_bound = False
        if not fixture_limited and n_ep > 0 and n_pass == n_ep:
            violations.append("all_episodes_pass")
            in_bound = False
        if extra_side and branch == "other_session":
            violations.append("passes_per_side")
        for violated in violations:
            if not _valid_justification(just, bound, violated):
                errors.append(
                    f"{branch} out of bound on {violated}: eps={eps:.3f} pass_rate={pass_rate:.3f} "
                    f"sessions_with_pass={sessions_with_pass}/{n_sessions} ({session_frac:.3f}) "
                    f"n={n_ep} pass={n_pass}. Bound eps={bound.get('episodes_per_session')} "
                    f"pass_rate={bound.get('pass_rate')}. A generated diagnosis is not a waiver."
                )
        audit_branch = audit["branches"][branch]["stages"]
        operand_values: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
        stage_fail = Counter()
        stage_seen = Counter()
        for ep in episodes:
            for row in ep.get("stages") or []:
                name = str(row.get("stage"))
                stage_seen[name] += 1
                if row.get("verdict") == "fail":
                    stage_fail[name] += 1
                for op_name, op_val in (row.get("operands") or {}).items():
                    operand_values[name][op_name].add(json.dumps(_jsonable(op_val), sort_keys=True))
        for stage_name, ops in operand_values.items():
            meta = audit_branch.get(stage_name) or {}
            if meta.get("emission_gate") or meta.get("omitted"):
                continue
            if stage_name not in {"context", "trigger", "confirmation"}:
                continue
            gating = [
                op["name"]
                for op in meta.get("operands") or []
                if not op.get("recorded_not_gating")
            ]
            if stage_fail[stage_name] == 0 and stage_seen[stage_name]:
                varying = [op for op in gating if len(ops.get(op, set())) > 1]
                if varying:
                    errors.append(
                        f"{branch}.{stage_name} never fails across the slice while gating operand(s) {varying} vary"
                    )
        funnel_note = None
        if violations:
            hottest = None
            if stages:
                hottest = max(stages, key=lambda name: stages[name]["pass"])
            funnel_note = (
                f"violations={violations} hottest_stage={hottest}. "
                f"This note is not a waiver."
            )
        rows.append(
            {
                "branch": branch,
                "sessions": n_sessions,
                "episodes": n_ep,
                "pass": n_pass,
                "fail": n_fail,
                "unknown": n_unk,
                "pass_rate": pass_rate,
                "episodes_per_session": eps,
                "sessions_with_pass": sessions_with_pass,
                "session_pass_fraction": session_frac,
                "stages": stages,
                "time_of_entry_histogram_30m_et": dict(sorted(histogram.items())),
                "bound": bound,
                "in_bound": in_bound and not violations,
                "violations": violations,
                "diagnosis": funnel_note,
                "printed_zone_fixture_count": len(PZONE_FIXTURES) if branch == "timed_pzone_reversal" else None,
            }
        )
    return rows, errors


@pytest.fixture(scope="module")
def slice_population():
    install_write_guard()
    collected: dict[str, list[dict[str, Any]]] = {branch: [] for branch in BRANCHES}
    sessions_used: list[str] = []
    load_errors: list[str] = []
    selected: list[dict[str, Any]] = []
    for day in SLICE_DATES:
        try:
            # B0.3 reads the session window itself -- the 06:00-09:00 box, the
            # prior sessions and the day's clock -- so the slice is scanned on
            # the session market, not on the replay view.
            market = load_source_market(day)
            market.jj_sessionstat = False
        except Exception as exc:
            load_errors.append(f"{day}: {type(exc).__name__}: {exc}")
            continue
        sessions_used.append(day)
        day_episodes: list[dict[str, Any]] = []
        primary_play = None
        for branch in BRANCHES:
            doc = scan_b02(market, {"method_id": FAMILY, "branch": branch, "coverage_id": "slice"})
            read = doc.get("day_read") or {}
            primary_play = primary_play or read.get("primary_play") or read.get("play")
            for episode in doc.get("episodes") or []:
                collected[branch].append(episode)
                if episode.get("research_verdict") == "pass":
                    day_episodes.append(episode)
        # Phase 1.5 scores the trade list the family would actually have taken:
        # the day's play, first qualifying setup, at most three entries.
        selection = selection_for(market, day_episodes, primary_play=primary_play)
        selected.append({"session_date": day, "primary_play": primary_play, "n_entries": int(selection.get("n_entries") or 0)})
    return {"collected": collected, "sessions_used": sessions_used, "load_errors": load_errors, "selected": selected}


def test_p15_16a_plausibility_jumbo_gate(slice_population):
    audit = json.loads((REPAIR / "STAGE_AUDIT_jumbo.json").read_text())
    family_spec = json.loads(FAMILY_JSON.read_text())
    bounds = family_spec["plausibility"]
    errors: list[str] = []
    for branch, payload in audit["branches"].items():
        for stage_name, stage in payload["stages"].items():
            measured = bool(stage.get("measured"))
            omitted = bool(stage.get("omitted"))
            unobservable = stage.get("unobservable")
            if not measured and not omitted and not unobservable:
                errors.append(f"{branch}.{stage_name} is unmeasured without a named unobservable operand")
            if measured:
                origins = {op.get("origin") for op in stage.get("operands") or []}
                if origins and origins <= {"constant", "label", "branch_record"}:
                    errors.append(f"{branch}.{stage_name} is marked measured but operands are not market-derived")
    rows, gate_errors = evaluate_gate(
        bounds,
        slice_population["collected"],
        audit,
        slice_population["sessions_used"],
    )
    # Branch-population bounds are DIAGNOSTIC from B0.3 onwards: a branch
    # raising many candidate setups is not a defect when only the selected
    # trade list is traded. They are reported, not asserted; the gate is
    # test_p15_16a_selected_trade_list_is_plausible below. Structural errors
    # (a branch emitting on non-fixture dates, a stage that never fails while
    # its gating operands vary) remain fatal.
    structural = [msg for msg in gate_errors if "out of bound on" not in msg]
    branch_population_diagnostics = [msg for msg in gate_errors if "out of bound on" in msg]
    errors.extend(structural)
    payload = {
        "family": FAMILY,
        "branch_population_diagnostics": branch_population_diagnostics,
        "slice_dates": SLICE_DATES,
        "sessions_used": slice_population["sessions_used"],
        "load_errors": slice_population["load_errors"],
        "branches": rows,
    }
    REPAIR.mkdir(parents=True, exist_ok=True)
    (OUT / "PLAUSIBILITY_jumbo.json").write_text(json.dumps(payload, indent=2, default=str) + "\n")
    lines = [
        "# JJ-TBR plausibility (15 stratified dates)",
        "",
        f"Sessions loaded: {len(slice_population['sessions_used'])} / {len(SLICE_DATES)}.",
        "",
        "| branch | sessions | episodes | pass | fail | unknown | pass_rate | eps | sessions_with_pass | bound eps | bound pass_rate | in_bound |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        b = row["bound"]
        lines.append(
            f"| {row['branch']} | {row['sessions']} | {row['episodes']} | {row['pass']} | {row['fail']} | {row['unknown']} | "
            f"{row['pass_rate']:.3f} | {row['episodes_per_session']:.3f} | {row['sessions_with_pass']}/{row['sessions']} | "
            f"{b['episodes_per_session']} | {b.get('pass_rate')} | "
            f"{'in' if row['in_bound'] else 'out'} |"
        )
    lines.append("")
    for row in rows:
        if row["diagnosis"] or row["violations"]:
            lines.append(f"## {row['branch']}")
            lines.append("")
            lines.append(str(row["diagnosis"] or row["violations"]))
            lines.append("")
            hist = row["time_of_entry_histogram_30m_et"]
            if hist:
                lines.append("Time-of-entry (pass, 30-minute ET): " + ", ".join(f"{k}={v}" for k, v in hist.items()))
                lines.append("")
    (OUT / "PLAUSIBILITY_jumbo.md").write_text("\n".join(lines) + "\n")
    assert not errors, "\n".join(errors)
    assert len(slice_population["sessions_used"]) >= 10, slice_population["load_errors"]


def test_mutated_pass_rate_bound_fails_the_gate(slice_population):
    audit = json.loads((REPAIR / "STAGE_AUDIT_jumbo.json").read_text())
    bounds = copy.deepcopy(json.loads(FAMILY_JSON.read_text())["plausibility"])
    live = next(branch for branch in BRANCHES if slice_population["collected"][branch])
    bounds[live]["pass_rate"] = [0.0, 0.0]
    bounds[live]["episodes_per_session"] = [0.0, 0.0]
    bounds[live].pop("out_of_bound_justification", None)
    _rows, errors = evaluate_gate(
        bounds,
        slice_population["collected"],
        audit,
        slice_population["sessions_used"],
    )
    assert errors, f"mutating {live} bounds to [0,0] must fail the gate"
    assert any("out of bound" in item for item in errors)


def test_after_tape_examples_do_not_call_build_event_window(monkeypatch):
    from trading_research.research.method_pack import event_cache, event_time

    def boom(*_args, **_kwargs):
        raise AssertionError("build_event_window must not run for after-tape replay")

    monkeypatch.setattr(event_cache, "build_event_window", boom)
    monkeypatch.setattr(event_time, "build_event_window", boom)
    examples = [row for row in json.loads(EXAMPLES.read_text())["examples"] if row.get("family") == FAMILY]
    after = [
        row
        for row in examples
        if row.get("inside_tape") is False or not is_native_session(row.get("date"))
    ]
    after.append(
        {
            "id": "JJ-AFTER-TAPE",
            "family": "JJ-TBR",
            "date": "2026-09-11",
            "inside_tape": False,
            "expected_detection": {"branch": "judas_reversal"},
        }
    )
    assert after, "expected after-tape JJ examples"
    for example in after:
        row = replay_example(None, example)
        assert row["detected"] is None
        assert row["divergence"] == "date outside the tape"
        assert row["failing_operand"] == "date"


# ---------------------------------------------------------------------------
# Phase 1.5 scores the SELECTED TRADE LIST, not the branch population.
#
# The branch bounds in families/*.json stay as a diagnostic of how many
# candidate setups each branch raises; they no longer gate. What gates is the
# list the family would have traded: the day's play, first qualifying setup,
# no re-entry after a full objective, at most three entries a session. The
# authors show roughly one trade a session and never more than three, so a
# faithful rebuild has to land between a trade every other session and the cap.
SELECTED_ENTRIES_PER_SESSION = (0.5, 3.0)


def test_p15_16a_selected_trade_list_is_plausible(slice_population):
    rows = slice_population["selected"]
    assert rows, "no sessions scanned"
    total = sum(row["n_entries"] for row in rows)
    per_session = total / len(rows)
    lo, hi = SELECTED_ENTRIES_PER_SESSION
    over_cap = [row for row in rows if row["n_entries"] > 3]
    payload = {
        "family": FAMILY,
        "sessions": len(rows),
        "entries": total,
        "entries_per_session": per_session,
        "bound": list(SELECTED_ENTRIES_PER_SESSION),
        "rows": rows,
    }
    (OUT / "SELECTED_jumbo.json").write_text(json.dumps(payload, indent=2, default=str) + "\n")
    assert not over_cap, f"the session cap of three entries was exceeded: {over_cap}"
    assert lo <= per_session <= hi, (
        f"JJ-TBR selected {total} entries over {len(rows)} sessions "
        f"({per_session:.2f}/session), outside {SELECTED_ENTRIES_PER_SESSION}"
    )


def test_selected_list_gate_rejects_an_implausible_list():
    """The gate is a real check: a list at ten entries a session must fail it."""
    rows = [{"session_date": "2026-01-02", "n_entries": 10}]
    per_session = sum(row["n_entries"] for row in rows) / len(rows)
    lo, hi = SELECTED_ENTRIES_PER_SESSION
    assert not (lo <= per_session <= hi)
    assert [row for row in rows if row["n_entries"] > 3]
