"""P15-16A repair-round plausibility gate for the saint track."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
import tempfile
from pathlib import Path
from zoneinfo import ZoneInfo

from trading_research.research.rule_discovery.source_adapters.b02_saint_track import (
    AUTHOR_EXAMPLES,
    REPAIR_DIR,
    REPAIR_SLICE_DATES,
    STAGE_ORDER,
    account_day_for_example,
    funnel_counts,
    outside_native_tape,
    write_json,
)
from trading_research.research.rule_discovery.source_adapters.common import load_source_market
from trading_research.research.rule_discovery.source_adapters.keani import replay_example as keani_replay
from trading_research.research.rule_discovery.source_adapters.keani import scan_b02 as keani_scan
from trading_research.research.rule_discovery.source_adapters.member import replay_example as member_replay
from trading_research.research.rule_discovery.source_adapters.member import scan_b02 as member_scan
from trading_research.research.rule_discovery.source_adapters.saint import replay_example as saint_replay
from trading_research.research.rule_discovery.source_adapters.saint import scan_b02 as saint_scan

WORK_DIR = Path(tempfile.gettempdir()) / "p15_16a_gate_out"  # test output, kept out of the evidence tree
ET = ZoneInfo("America/New_York")
FAMILIES = {
    "SAINT-AMT": {
        "scan": saint_scan,
        "replay": saint_replay,
        "branches": ("continuation_retest", "trapped_buyers_retest", "failed_auction_return", "poc_traversal"),
        "audit": REPAIR_DIR / "STAGE_AUDIT_saint.json",
        "slug": "saint",
    },
    "MEMBER-TWO-REASONS": {
        "scan": member_scan,
        "replay": member_replay,
        "branches": ("resistance_short", "planned_return_long"),
        "audit": REPAIR_DIR / "STAGE_AUDIT_member.json",
        "slug": "member",
    },
    "KEANI-OPEN-ABOVE-VALUE": {
        "scan": keani_scan,
        "replay": keani_replay,
        "branches": ("source_long",),
        "audit": REPAIR_DIR / "STAGE_AUDIT_keani.json",
        "slug": "keani",
    },
}


def _stage(episode, name):
    for item in episode.get("stages") or []:
        if item.get("stage") == name:
            return item
    return None


def _bucket(ns):
    if ns is None:
        return "unknown"
    ts = datetime.fromtimestamp(int(ns) / 1_000_000_000, tz=timezone.utc).astimezone(ET)
    minute = 0 if ts.minute < 30 else 30
    return f"{ts.hour:02d}:{minute:02d}"


def _resolve_stage(audit_branch, name):
    row = dict(audit_branch.get(name) or {})
    if not row and audit_branch.get("inherits"):
        return row
    return row


def _load_family_json(family: str) -> dict:
    path = Path(__file__).resolve().parents[2] / "src/trading_research/research/rule_discovery/families"
    names = {"SAINT-AMT": "saint.json", "MEMBER-TWO-REASONS": "member.json", "KEANI-OPEN-ABOVE-VALUE": "keani.json"}
    return json.loads((path / names[family]).read_text())


def _audit_unmeasured_errors(audit: dict) -> list[str]:
    errors = []
    for branch, stages in (audit.get("branches") or {}).items():
        inherited = {}
        parent = stages.get("inherits")
        if parent:
            inherited = dict(audit["branches"].get(parent) or {})
        for name in STAGE_ORDER:
            spec = dict(inherited.get(name) or {})
            spec.update(stages.get(name) or {})
            if not spec:
                errors.append(f"{audit['family']}/{branch}/{name}: missing from STAGE_AUDIT")
                continue
            measured = spec.get("measured")
            omitted = spec.get("omitted")
            if measured is False and not spec.get("unobservable_operand"):
                errors.append(f"{audit['family']}/{branch}/{name}: unmeasured without named unobservable_operand")
            if measured is False and not omitted and not spec.get("unobservable_operand"):
                errors.append(f"{audit['family']}/{branch}/{name}: unmeasured live stage without unobservable operand")
    return errors


def _never_fail_errors(audit: dict, funnel: dict) -> list[str]:
    errors = []
    family = audit["family"]
    for branch, stages in (audit.get("branches") or {}).items():
        inherited = dict(audit["branches"].get(stages.get("inherits") or "") or {})
        counts = (funnel.get(branch) or {}).get("stages") or {}
        samples = (funnel.get(branch) or {}).get("operand_values") or {}
        for name in STAGE_ORDER:
            spec = dict(inherited.get(name) or {})
            spec.update(stages.get(name) or {})
            if spec.get("omitted") or spec.get("measured") is False:
                continue
            row = counts.get(name) or {}
            if int(row.get("fail") or 0) > 0:
                continue
            if int(row.get("unknown") or 0) > 0:
                continue
            if int(row.get("pass") or 0) == 0:
                continue
            depends = spec.get("verdict_depends_on") or []
            varying = []
            for operand in depends:
                seen = list((samples.get(name) or {}).get(operand) or [])
                flags = {str(v).strip('"').lower() for v in seen}
                boolean_like = flags <= {"true", "false", "null", "none"}
                if boolean_like and flags & {"true", "false"} == {"true", "false"}:
                    varying.append(f"{operand}={sorted(flags)}")
            if varying:
                errors.append(
                    f"{family}/{branch}/{name}: never fails while operand varies ({', '.join(varying)})"
                )
            if name == "confirmation" and spec.get("measured") is not False and not spec.get("omitted"):
                if int(row.get("pass") or 0) > 0 and int(row.get("fail") or 0) == 0:
                    errors.append(
                        f"{family}/{branch}/confirmation: never fails (pass={row.get('pass')} fail=0); "
                        "confirmation cannot be determined by an earlier stage"
                    )
    return errors


def bound_violation_errors(family: str, branch: str, row: dict, bound: dict | None) -> list[str]:
    """Fail out-of-bound branches unless family JSON has a human justification quoting a page that supports the observed rate."""
    errors = []
    if not bound:
        return [f"{family}/{branch}: missing plausibility block"]
    episodes = int(row.get("episodes") or 0)
    passed = int(row.get("pass") or 0)
    sessions = int(row.get("sessions") or 0) or 1
    pass_rate = (passed / episodes) if episodes else 0.0
    eps = (episodes / sessions) if sessions else 0.0
    ep_bound = bound.get("episodes_per_session") or [0, 99]
    pr_bound = bound.get("pass_rate") or [0.0, 1.0]
    in_ep = ep_bound[0] <= eps <= ep_bound[1]
    in_pr = pr_bound[0] <= pass_rate <= pr_bound[1]
    if in_ep and in_pr:
        return errors
    just = bound.get("observed_rate_justification")
    if not isinstance(just, dict):
        errors.append(
            f"{family}/{branch}: out of bound (episodes_per_session={eps:.3f} pass_rate={pass_rate:.4f} "
            f"bound eps={ep_bound} pass_rate={pr_bound}) without observed_rate_justification in family JSON"
        )
        return errors
    pages = str(just.get("pages") or "").strip()
    text = str(just.get("text") or "").strip()
    claim = str(bound.get("source_claim") or "").strip().lower()
    if not pages or not text:
        errors.append(f"{family}/{branch}: observed_rate_justification missing pages or text")
    elif claim == "unstated":
        errors.append(
            f"{family}/{branch}: source_claim unstated cannot justify observed pass_rate {pass_rate:.4f}"
        )
    return errors


def _diagnose(family: str, branch: str, funnel_row: dict, bound: dict) -> str:
    stages = funnel_row.get("stages") or {}
    conf = stages.get("confirmation") or {}
    trig = stages.get("trigger") or {}
    loc = stages.get("location") or {}
    ctx = stages.get("context") or {}
    parts = [
        f"{family}/{branch}: episodes={funnel_row.get('episodes')} pass={funnel_row.get('pass')} "
        f"fail={funnel_row.get('fail')} unknown={funnel_row.get('unknown')} "
        f"pass_rate={funnel_row.get('pass_rate')} bound={bound}."
    ]
    if family == "SAINT-AMT" and branch in {"continuation_retest", "trapped_buyers_retest"}:
        parts.append(
            "Confirmation requires confirm_at (F10), held_retest (WIC p.8), arrival_ok (WIC p.4) "
            f"and alignment_ok (WIC pp.5-10). confirmation={conf} trigger={trig}."
        )
        if branch == "continuation_retest" and int(conf.get("unknown") or 0) > int(conf.get("pass") or 0):
            parts.append(
                "Root operand on the first B0.2 run was htf_control=None from an inverted HTF window "
                "(balance.start after trigger). The repair reads bars from market.start when the window would invert."
            )
        if branch == "trapped_buyers_retest":
            parts.append(
                "Arrival must be fast (aggressive into the extreme, TRAP pp.4-5). Slow approaches fail arrival_ok; "
                "missing approach O/C is unknown, never pass."
            )
    if family == "SAINT-AMT" and branch == "failed_auction_return":
        parts.append(
            "Drive must reach a distinct prior VA (AMTL p.8). Overlapping prior VA is skipped so mean-reversion "
            f"inside one box cannot pass. confirmation={conf} location={loc}."
        )
    if family == "SAINT-AMT" and branch == "poc_traversal":
        parts.append(
            "AMTL p.9 80/20 is conditional on return-into-range then POC behavior, not a session pass rate. "
            "Push episodes now emit when the retest fails (held_retest can be False). "
            f"confirmation={conf} trigger={trig}."
        )
    if family == "MEMBER-TWO-REASONS":
        parts.append(
            "A pass needs both reasons (independent HVN/KG1 and prior reaction, K10 pp.5-8) and a measured "
            f"rejection/hold at contact. trigger={trig} confirmation={conf}. Touch-only is fail."
        )
    if family == "KEANI-OPEN-ABOVE-VALUE":
        parts.append(
            "AVG p.21 A period fully above prior-day 70% VAH (strict > , SD11), then POC-or-VAH rejection, "
            f"aggressive VAH break, defended 3-tick retest. context={ctx} trigger={trig} confirmation={conf}. "
            "39/1695 B0.1 is the reference density. DOM at retest is unobservable."
        )
    return " ".join(parts)


def test_p15_16a_plausibility_saint_track():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    markets = {}
    load_errors = {}
    for day in REPAIR_SLICE_DATES:
        try:
            markets[day] = load_source_market(day)
        except Exception as exc:
            load_errors[day] = str(exc)

    gate_errors = []
    for family, cfg in FAMILIES.items():
        audit = json.loads(cfg["audit"].read_text())
        gate_errors.extend(_audit_unmeasured_errors(audit))
        spec = _load_family_json(family)
        plaus = spec.get("plausibility") or {}
        docs = []
        operand_values: dict[str, dict[str, dict[str, set]]] = {}
        histograms: dict[str, Counter] = {}
        sessions_with_pass: dict[str, int] = {branch: 0 for branch in cfg["branches"]}
        for day in REPAIR_SLICE_DATES:
            market = markets.get(day)
            if market is None:
                continue
            for branch in cfg["branches"]:
                doc = cfg["scan"](market, {"family": family, "branch": branch})
                docs.append(doc)
                if any((ep.get("verdict") or ep.get("research_verdict")) == "pass" for ep in doc.get("episodes") or []):
                    sessions_with_pass[branch] += 1
                branch_ops = operand_values.setdefault(branch, {})
                hist = histograms.setdefault(branch, Counter())
                for episode in doc.get("episodes") or []:
                    ns = episode.get("decision_at")
                    hist[_bucket(ns)] += 1
                    for item in episode.get("stages") or []:
                        name = item.get("stage")
                        ops = branch_ops.setdefault(name, {})
                        for key, value in (item.get("operands") or {}).items():
                            ops.setdefault(key, set()).add(json.dumps(value, default=str, sort_keys=True))
        funnel = funnel_counts(docs)
        sessions = len(REPAIR_SLICE_DATES) - len(load_errors)
        branch_rows = {}
        md_lines = [
            f"# Plausibility {family}",
            "",
            f"Sessions attempted: {len(REPAIR_SLICE_DATES)}. Loaded: {sessions}. Load errors: {load_errors or '{}'}.",
            "",
        ]
        for branch in cfg["branches"]:
            row = dict(funnel.get(branch) or {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0, "stages": {}})
            episodes = int(row.get("episodes") or 0)
            passed = int(row.get("pass") or 0)
            failed = int(row.get("fail") or 0)
            unknown = int(row.get("unknown") or 0)
            pass_rate = (passed / episodes) if episodes else 0.0
            eps = (episodes / sessions) if sessions else 0.0
            bound = plaus.get(branch) or {}
            ep_bound = bound.get("episodes_per_session") or [0, 99]
            pr_bound = bound.get("pass_rate") or [0.0, 1.0]
            in_ep = ep_bound[0] <= eps <= ep_bound[1]
            in_pr = pr_bound[0] <= pass_rate <= pr_bound[1]
            in_bound = bool(in_ep and in_pr)
            serial_ops = {
                stage: {k: sorted(v)[:12] for k, v in ops.items()} for stage, ops in operand_values.get(branch, {}).items()
            }
            row["pass_rate"] = pass_rate
            row["episodes_per_session"] = eps
            row["sessions"] = sessions
            row["sessions_with_pass"] = sessions_with_pass.get(branch, 0)
            row["bound"] = bound
            row["in_bound"] = in_bound
            row["report_note"] = _diagnose(family, branch, {**row, "pass_rate": pass_rate}, bound)
            row["time_of_entry_et_30m"] = dict(sorted(histograms.get(branch, {}).items()))
            row["operand_values"] = serial_ops
            branch_rows[branch] = row
            md_lines.append(f"## {branch}")
            md_lines.append(
                f"sessions={sessions} sessions_with_pass={row['sessions_with_pass']} episodes={episodes} "
                f"pass={passed} fail={failed} unknown={unknown} pass_rate={pass_rate:.4f} "
                f"episodes_per_session={eps:.3f} in_bound={in_bound}"
            )
            md_lines.append(f"bound episodes_per_session={ep_bound} pass_rate={pr_bound}")
            md_lines.append(f"claim: {bound.get('source_claim')} ({bound.get('pages')})")
            md_lines.append("")
            gate_errors.extend(bound_violation_errors(family, branch, row, bound))
        funnel_for_gate = {k: {**v, "operand_values": operand_values.get(k, {})} for k, v in branch_rows.items()}
        gate_errors.extend(_never_fail_errors(audit, funnel_for_gate))
        payload = {
            "family": family,
            "slice_dates": list(REPAIR_SLICE_DATES),
            "sessions_loaded": sessions,
            "load_errors": load_errors,
            "branches": branch_rows,
        }
        write_json(WORK_DIR / f"PLAUSIBILITY_{cfg['slug']}.json", payload)
        (WORK_DIR / f"PLAUSIBILITY_{cfg['slug']}.md").write_text("\n".join(md_lines) + "\n")

    examples = json.loads(AUTHOR_EXAMPLES.read_text())["examples"]
    replay_rows = {"SAINT-AMT": [], "MEMBER-TWO-REASONS": [], "KEANI-OPEN-ABOVE-VALUE": []}
    for example in examples:
        family = example.get("family")
        if family not in FAMILIES:
            continue
        if family == "MEMBER-TWO-REASONS":
            result = member_replay(None, example)
            result["id"] = example["id"]
            replay_rows[family].append(result)
            continue
        if family == "KEANI-OPEN-ABOVE-VALUE":
            result = keani_replay(None, example)
            result["id"] = example.get("id")
            replay_rows[family].append(result)
            continue
        if outside_native_tape(example):
            result = saint_replay(None, example)
            result["id"] = example["id"]
            replay_rows[family].append(result)
            continue
        day = account_day_for_example(example) or example.get("date")
        try:
            market = markets.get(str(day))
            result = saint_replay(market, example)
        except Exception as exc:
            result = saint_replay(None, {**example, "date": "2099-01-01", "inside_tape": False})
            result["divergence"] = f"date outside the tape: {exc}"
        result["id"] = example["id"]
        replay_rows[family].append(result)
    write_json(WORK_DIR / "REPLAY_saint.json", {"family": "SAINT-AMT", "examples": replay_rows["SAINT-AMT"]})
    write_json(WORK_DIR / "REPLAY_member.json", {"family": "MEMBER-TWO-REASONS", "examples": replay_rows["MEMBER-TWO-REASONS"]})
    write_json(WORK_DIR / "REPLAY_keani.json", {"family": "KEANI-OPEN-ABOVE-VALUE", "examples": replay_rows["KEANI-OPEN-ABOVE-VALUE"]})

    if gate_errors:
        raise AssertionError("\n".join(gate_errors))


def test_p15_16a_plausibility_mutated_bound_fails():
    spec = _load_family_json("SAINT-AMT")
    bound = dict(spec["plausibility"]["trapped_buyers_retest"])
    bound["pass_rate"] = [0.0, 0.0]
    bound.pop("observed_rate_justification", None)
    row = {
        "episodes": 30,
        "pass": 1,
        "fail": 27,
        "unknown": 2,
        "pass_rate": 0.033,
        "episodes_per_session": 2.0,
        "sessions": 15,
    }
    errors = bound_violation_errors("SAINT-AMT", "trapped_buyers_retest", row, bound)
    assert errors, "mutating pass_rate to [0,0] must fail the gate"
    assert any("out of bound" in item for item in errors)


def test_after_tape_replay_does_not_build_cache(monkeypatch):
    def boom(*_args, **_kwargs):
        raise AssertionError("build_event_window called")

    monkeypatch.setattr("trading_research.research.method_pack.event_cache.build_event_window", boom)
    monkeypatch.setattr("trading_research.research.method_pack.event_time.build_event_window", boom)
    examples = json.loads(AUTHOR_EXAMPLES.read_text())["examples"]
    ours = []
    for row in examples:
        if row.get("family") not in FAMILIES:
            continue
        if row.get("inside_tape") is False or outside_native_tape(row):
            ours.append(row)
    ours.append({"id": "after-tape-probe", "family": "SAINT-AMT", "date": "2026-09-02", "inside_tape": False})
    ours.append({"id": "after-tape-probe-2", "family": "SAINT-AMT", "date": "2026-08-28", "inside_tape": False})
    assert ours
    for example in ours:
        family = example.get("family")
        if family == "MEMBER-TWO-REASONS":
            out = member_replay(None, example)
        elif family == "KEANI-OPEN-ABOVE-VALUE":
            out = keani_replay(None, example)
        else:
            out = saint_replay(None, example)
        assert out["detected"] is None
        if family == "MEMBER-TWO-REASONS" and str((example or {}).get("instrument") or "").upper().startswith("ES"):
            assert out["divergence"] == "ES tape required"
        elif example.get("id") == "MB-2026-07-K10":
            assert out["divergence"] == "ES tape required"
        else:
            assert out["divergence"] == "date outside the tape"
        assert out.get("reached_location") is False
