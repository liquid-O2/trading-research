"""P15-16A repair gate: population plausibility for SIRES and REFILL-STUDY."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path
import hashlib
import json

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.rule_discovery.native import build_market_view, install_write_guard
from trading_research.research.rule_discovery.source_adapters.common import FAMILY_BRANCHES
from trading_research.research.rule_discovery.source_adapters.refill_b02 import (
    replay_example as refill_replay,
    scan_b02 as refill_scan,
)
from trading_research.research.rule_discovery.source_adapters.sires_b02 import (
    STAGE_ORDER,
    _date_outside_tape,
    replay_example,
    scan_b02,
)

IMPL = Path(__file__).resolve().parents[2]
REPAIR = IMPL / "reports/research-work/P15-16A/_repair_sires"
WORK = IMPL / "reports/research-work/P15-16A/_work_r3"
TRACK = IMPL / "reports/research-work/P15-16A/_track_sires"
FAMILIES = IMPL / "src/trading_research/research/rule_discovery/families"
EXAMPLES = IMPL.parent / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json"
SLICE = (
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
)
AUTHOR_CONTEXT = {
    "location_kind",
    "defended_ticks",
    "gamma_regime",
    "thesis_killer",
    "entry_variant",
    "entry_ticks",
    "stop_ticks",
    "control_zone_far_ticks",
    "fade_variant",
    "account_daily_r",
}
TRACK_SHA256 = {
    "RULES_SIRES.json": "342e80e2bd2db367aae65ab6fa25f5ffab0f445052226f31a54fd338d841957b",
    "RULES_REFILL-STUDY.json": "1837fd81aa67eec4734d3fb7f737105f552bbee192e62b840d38d9b061647a08",
    "REPLAY_SIRES.json": "bd13925f209cf5011a55b43e81affc4d1a15c08d80dfaad2dfd37e23379528cf",
    "FUNNEL_SIRES.json": "6c10d6cb94e42e712e9f52055bee8d2c10a820cf4a2e0ba17e2210e27f5e3dfa",
    "FUNNEL_REFILL-STUDY.json": "40f7803cab1a1b809810db62e817f29087b0c1f7373824f52515d63b263ffe6b",
    "ENTRY_TIMES.json": "98656599bf65a7659e76e81451302f092606ede8a22d1466eecd5476aff39ba2",
    "REFILL_SLICE.json": "9cacf5487617f544fe86831f85face7d676a8dfe6685a51be4af98daeb47dd47",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _empty_stages(names):
    return {name: {"pass": 0, "fail": 0, "unknown": 0} for name in names}


def _histogram(episodes, day: str) -> dict[str, int]:
    open_ns = et_ns(date.fromisoformat(day), 9, 30)
    out: dict[str, int] = {}
    for ep in episodes:
        entry_ns = ep.get("decision_at")
        if entry_ns is None:
            continue
        minutes = int((int(entry_ns) - open_ns) // 60_000_000_000)
        bucket = minutes - (minutes % 30)
        hour = 9 + (30 + bucket) // 60
        minute = (30 + bucket) % 60
        key = f"{hour:02d}:{minute:02d}"
        out[key] = out.get(key, 0) + 1
    return out


def _human_justification(bounds: dict) -> str | None:
    """Family-JSON justification only. Never a string the test generated."""
    raw = bounds.get("observed_rate_justification")
    if not isinstance(raw, dict):
        return None
    page = str(raw.get("page") or "").strip()
    text = str(raw.get("text") or "").strip()
    if not page or not text:
        return None
    return f"{page}: {text}"


def _in_bound(row: dict, bound: dict) -> bool:
    per = row["episodes_per_session"]
    rate = row["pass_rate"]
    ep_bound = bound.get("episodes_per_session")
    pr_bound = bound.get("pass_rate")
    if not (isinstance(ep_bound, (list, tuple)) and len(ep_bound) >= 2 and ep_bound[0] is not None and ep_bound[1] is not None):
        return False
    if not (isinstance(pr_bound, (list, tuple)) and len(pr_bound) >= 2 and pr_bound[0] is not None and pr_bound[1] is not None):
        return False
    lo_e, hi_e = ep_bound[0], ep_bound[1]
    lo_p, hi_p = pr_bound[0], pr_bound[1]
    return lo_e <= per <= hi_e and lo_p <= rate <= hi_p


def _gate_errors(sires_rows: dict, refill_rows: dict, sires_spec: dict, refill_spec: dict, audit_s: dict, audit_r: dict) -> list[str]:
    errors = []
    for branch, spec in (audit_s.get("branches") or {}).items():
        for stage, row in (spec.get("stages") or {}).items():
            if row.get("measured"):
                continue
            if row.get("unobservable") or row.get("unobservable_reason"):
                continue
            errors.append(f"SIRES:{branch}:{stage} unmeasured without a named unobservable operand")
    for branch, spec in (audit_r.get("branches") or {}).items():
        for stage, row in (spec.get("stages") or {}).items():
            if row.get("measured"):
                continue
            if row.get("unobservable") or row.get("unobservable_reason"):
                continue
            errors.append(f"REFILL-STUDY:{branch}:{stage} unmeasured without a named unobservable operand")
    for branch, row in sires_rows.items():
        bound = sires_spec[branch]
        if not _in_bound(row, bound) and not _human_justification(bound):
            errors.append(
                f"SIRES:{branch} out of bound eps={row['episodes_per_session']:.3f} "
                f"pr={row['pass_rate']:.4f} bound={bound['episodes_per_session']}/{bound['pass_rate']} "
                "(no observed_rate_justification in family JSON)"
            )
        ctx = row["stages"].get("context") or {}
        context_unknown = int(ctx.get("unknown") or 0) > 0
        for name in ("trigger", "confirmation"):
            counts = row["stages"].get(name) or {}
            total = counts.get("pass", 0) + counts.get("fail", 0) + counts.get("unknown", 0)
            if total and counts.get("fail", 0) == 0 and counts.get("unknown", 0) == 0 and counts.get("pass", 0) > 0:
                if context_unknown and row["pass"] == 0:
                    continue
                errors.append(f"SIRES:{branch}:{name} never fails while present")
    for branch, row in refill_rows.items():
        bound = refill_spec[branch]
        if not _in_bound(row, bound) and not _human_justification(bound):
            errors.append(
                f"REFILL-STUDY:{branch} out of bound eps={row['episodes_per_session']:.3f} "
                f"pr={row['pass_rate']:.4f} bound={bound['episodes_per_session']}/{bound['pass_rate']} "
                "(no observed_rate_justification in family JSON)"
            )
    for branch, page in (("ofm_aggressive", "OFM p.4"), ("balance_failure_fade", "BIG p.14")):
        row = sires_rows[branch]
        bound = sires_spec[branch]
        if _in_bound(row, bound):
            errors.append(f"SIRES:{branch} must be out of bound; source gives no contact density")
        just = _human_justification(bound) or ""
        if page not in just:
            errors.append(f"SIRES:{branch} diagnosis must cite {page}")
    return errors


def _scan_family(family: str, branches: tuple[str, ...], dates: tuple[str, ...]) -> dict:
    rows = {
        branch: {
            "sessions": 0,
            "episodes": 0,
            "pass": 0,
            "fail": 0,
            "unknown": 0,
            "stages": _empty_stages(STAGE_ORDER if family == "SIRES" else ("reference", "location", "trigger", "confirmation", "risk", "objective")),
            "histogram": defaultdict(int),
            "per_date": {},
        }
        for branch in branches
    }
    from trading_research.research.rule_discovery.source_adapters.common import is_native_session

    install_write_guard()
    for day in dates:
        if not is_native_session(day):
            continue
        try:
            view = build_market_view(day, full_account_day=True)
        except Exception:
            continue
        for branch in branches:
            rec = {"method_id": family, "branch": branch}
            if family == "SIRES":
                doc = scan_b02(view, rec)
            else:
                doc = refill_scan(view, rec)
            row = rows[branch]
            row["sessions"] += 1
            eps = doc.get("episodes") or []
            row["episodes"] += len(eps)
            n_pass = sum(1 for ep in eps if ep.get("research_verdict") == "pass")
            n_fail = sum(1 for ep in eps if ep.get("research_verdict") == "fail")
            n_unk = sum(1 for ep in eps if ep.get("research_verdict") == "unknown")
            row["pass"] += n_pass
            row["fail"] += n_fail
            row["unknown"] += n_unk
            row["per_date"][day] = {
                "episodes": len(eps),
                "pass": n_pass,
                "fail": n_fail,
                "unknown": n_unk,
                "hold_rate": (n_pass / len(eps)) if eps else 0.0,
            }
            for ep in eps:
                for st in ep.get("stages") or []:
                    bucket = row["stages"].setdefault(st["stage"], {"pass": 0, "fail": 0, "unknown": 0})
                    bucket[st["verdict"]] = bucket.get(st["verdict"], 0) + 1
            hist = _histogram(eps, day)
            for key, count in hist.items():
                row["histogram"][key] += count
    for branch, row in rows.items():
        row["histogram"] = dict(row["histogram"])
        row["episodes_per_session"] = (row["episodes"] / row["sessions"]) if row["sessions"] else 0.0
        row["pass_rate"] = (row["pass"] / row["episodes"]) if row["episodes"] else 0.0
    return rows


def test_p15_16a_plausibility_sires_and_refill():
    sires_spec = _load_json(FAMILIES / "sires.json")["plausibility"]
    refill_spec = _load_json(FAMILIES / "processes.json")["plausibility"]
    audit_s = _load_json(REPAIR / "STAGE_AUDIT_SIRES.json")
    audit_r = _load_json(REPAIR / "STAGE_AUDIT_REFILL-STUDY.json")
    sires_rows = _scan_family("SIRES", FAMILY_BRANCHES["SIRES"], SLICE)
    refill_rows = _scan_family("REFILL-STUDY", FAMILY_BRANCHES["REFILL-STUDY"], SLICE)
    payload = {"dates": list(SLICE), "SIRES": {}, "REFILL-STUDY": {}}
    md = []
    for branch, row in sires_rows.items():
        bound = sires_spec[branch]
        in_bound = _in_bound(row, bound)
        just = _human_justification(bound) if not in_bound else None
        payload["SIRES"][branch] = {
            **{k: v for k, v in row.items() if k != "histogram"},
            "histogram": row["histogram"],
            "bound": bound,
            "in_bound": in_bound,
            "justification": just,
        }
        md.append(
            f"| SIRES | {branch} | {row['sessions']} | {row['episodes']} | {row['pass']}/{row['fail']}/{row['unknown']} | {row['pass_rate']:.3f} | {bound['episodes_per_session']} | {bound['pass_rate']} | {'in' if in_bound else 'out'} |"
        )
    refill_dates = []
    for branch, row in refill_rows.items():
        bound = refill_spec[branch]
        in_bound = _in_bound(row, bound)
        just = _human_justification(bound) if not in_bound else None
        payload["REFILL-STUDY"][branch] = {
            **{k: v for k, v in row.items() if k != "histogram"},
            "histogram": row["histogram"],
            "bound": bound,
            "in_bound": in_bound,
            "justification": just,
        }
        md.append(
            f"| REFILL-STUDY | {branch} | {row['sessions']} | {row['episodes']} | {row['pass']}/{row['fail']}/{row['unknown']} | {row['pass_rate']:.3f} | {bound['episodes_per_session']} | {bound['pass_rate']} | {'in' if in_bound else 'out'} |"
        )
        for day, stats in sorted(row["per_date"].items()):
            refill_dates.append(
                f"| {day} | {stats['episodes']} | {stats['pass']} | {stats['fail']} | {stats['hold_rate']:.3f} |"
            )
    errors = _gate_errors(sires_rows, refill_rows, sires_spec, refill_spec, audit_s, audit_r)
    src = Path(scan_b02.__code__.co_filename).read_text()
    for key in AUTHOR_CONTEXT:
        if f'rec.get("{key}")' in src or f"rec.get('{key}')" in src:
            errors.append(f"scan_b02 still reads rec.{key}")
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "PLAUSIBILITY_SIRES.json").write_text(json.dumps({"family": "SIRES", "dates": list(SLICE), "branches": payload["SIRES"]}, indent=2) + "\n")
    (WORK / "PLAUSIBILITY_REFILL-STUDY.json").write_text(json.dumps({"family": "REFILL-STUDY", "dates": list(SLICE), "branches": payload["REFILL-STUDY"]}, indent=2) + "\n")
    header = "| family | branch | sessions | episodes | pass/fail/unknown | pass_rate | eps_bound | rate_bound | in/out |"
    (WORK / "PLAUSIBILITY_SIRES.md").write_text(
        "# SIRES plausibility\n\n"
        + header
        + "\n|---|---|---|---|---|---|---|---|---|\n"
        + "\n".join(x for x in md if x.startswith("| SIRES"))
        + "\n"
    )
    refill_just = payload["REFILL-STUDY"]["touch_record"].get("justification") or ""
    (WORK / "PLAUSIBILITY_REFILL-STUDY.md").write_text(
        "# REFILL-STUDY plausibility\n\n"
        + header
        + "\n|---|---|---|---|---|---|---|---|---|\n"
        + "\n".join(x for x in md if x.startswith("| REFILL"))
        + "\n\n## Per-date touches\n\n| date | touches | hold | broke | hold_rate |\n|---|---|---|---|---|\n"
        + "\n".join(refill_dates)
        + "\n\n"
        + refill_just
        + "\n"
    )
    assert not errors, errors


def test_mutated_stop_four_stage_bound_fails_the_gate():
    spec = json.loads((FAMILIES / "sires.json").read_text())
    spec["plausibility"]["stop_four_stage"]["pass_rate"] = [0.0, 0.0]
    spec["plausibility"]["stop_four_stage"].pop("observed_rate_justification", None)
    payload_path = WORK / "PLAUSIBILITY_SIRES.json"
    assert payload_path.is_file()
    stats = json.loads(payload_path.read_text())["branches"]["stop_four_stage"]
    bounds = spec["plausibility"]["stop_four_stage"]
    in_bound = _in_bound(stats, bounds)
    just = _human_justification(bounds)
    assert stats["pass_rate"] > 0.0
    assert in_bound is False
    assert just is None


def test_after_tape_replay_does_not_call_build_event_window(monkeypatch):
    from trading_research.research.method_pack import event_cache

    def boom(*_a, **_k):
        raise AssertionError("build_event_window must not run for after-tape replay")

    monkeypatch.setattr(event_cache, "build_event_window", boom)
    examples = json.loads(EXAMPLES.read_text())["examples"]
    ours = [
        row
        for row in examples
        if str(row.get("family") or "") in {"SIRES", "REFILL-STUDY"} and _date_outside_tape(row)
    ]
    ours.append({"id": "SI-AFTER-TAPE", "family": "SIRES", "date": "2026-09-11", "inside_tape": False})
    ours.append({"id": "REF-AFTER-TAPE", "family": "REFILL-STUDY", "date": "2026-08-28", "inside_tape": False})
    assert ours
    for example in ours:
        if str(example.get("family")) == "REFILL-STUDY":
            row = refill_replay(None, example)
        else:
            row = replay_example(None, example)
        assert row.get("detected") is None, example.get("id")
        assert row.get("divergence") == "date outside the tape", example.get("id")


def test_track_sires_round1_files_byte_identical():
    for name, digest in TRACK_SHA256.items():
        path = TRACK / name
        assert path.is_file(), name
        assert _sha256(path) == digest, name
