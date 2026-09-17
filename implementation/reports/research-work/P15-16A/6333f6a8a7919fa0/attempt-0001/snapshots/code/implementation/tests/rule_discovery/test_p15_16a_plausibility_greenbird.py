"""P15-16A repair gate: measured stages and source plausibility on 15 dates."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal
from pathlib import Path
import json

from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.rule_discovery.source_adapters.common import dual_scan, load_source_market, strip_baseline_version
from trading_research.research.rule_discovery.source_adapters.green_b02 import B02_VERSION, STAGE_ORDER
from trading_research.research.rule_discovery.source_adapters.green_failure import scan_b02 as fail_scan
from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import scan_b02 as vwap_scan

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
REPAIR = Path(__file__).resolve().parents[2] / "reports/research-work/P15-16A/_repair_greenbird"
# Generated evidence goes to the round-3 work directory. The committed round-1
# and repair-track evidence under _repair_*/_track_* stays byte-identical.
OUT = Path(__file__).resolve().parents[2] / "reports/research-work/P15-16A/_work_r3"
BYTE_DATES = ("2020-01-02", "2021-01-04")
HASH_START = REPAIR / "B0_B01_HASHES_START.json"
FAMILIES = {
    "GB-FAIL": Path(__file__).resolve().parents[2] / "src/trading_research/research/rule_discovery/families/green_failure.json",
    "GB-VWAP": Path(__file__).resolve().parents[2] / "src/trading_research/research/rule_discovery/families/green_vwap_scalp.json",
    "GB-SCALP": Path(__file__).resolve().parents[2] / "src/trading_research/research/rule_discovery/families/green_vwap_scalp.json",
}
BRANCHES = {
    "GB-FAIL": (
        "london_box",
        "asia_box",
        "asia_tdo_case",
        "prior_day_level",
        "prior_week_level",
        "nyam_box",
        "previous_hour",
        "nwog",
        "cash_open_reclaim_case",
        "golden_pocket",
        "ny_session_extreme",
    ),
    "GB-VWAP": ("source_long",),
    "GB-SCALP": ("golden_pocket_continuation",),
}
BOX_BRANCHES = ("london_box", "asia_box", "nyam_box", "previous_hour")


def _audit_path(family: str) -> Path:
    return REPAIR / f"STAGE_AUDIT_{family}.json"


def _load_bounds(family: str, branch: str) -> dict:
    spec = json.loads(FAMILIES[family].read_text())
    block = spec.get("plausibility") or {}
    if family == "GB-FAIL":
        row = block.get(branch) or {}
    else:
        row = ((block.get(family) or {}).get(branch) or {})
    return row


def _bucket_et(ns: int | None) -> str | None:
    if ns is None:
        return None
    dt = datetime.fromtimestamp(int(ns) / 1_000_000_000, tz=timezone.utc).astimezone(ZoneInfo("America/New_York"))
    minute = (dt.minute // 30) * 30
    return f"{dt.hour:02d}:{minute:02d}"


def _scan(market, family: str, branch: str) -> dict:
    rec = {"family": family, "branch": branch}
    if family == "GB-FAIL":
        return fail_scan(market, rec)
    return vwap_scan(market, rec)


def _summarize(docs: list[dict], family: str, branch: str) -> dict:
    sessions = len(docs)
    episodes = 0
    verdicts = Counter()
    stage_counts = {name: Counter() for name in STAGE_ORDER}
    stage_values = defaultdict(lambda: defaultdict(set))
    histogram = Counter()
    monday_passes = 0
    asia_hits = 0
    london_hits = 0
    sessions_with_pass = 0
    for doc in docs:
        session_hit = False
        for ep in doc.get("episodes") or []:
            episodes += 1
            verdict = ep.get("research_verdict") or "unknown"
            verdicts[verdict] += 1
            if verdict == "pass":
                session_hit = True
                histogram[_bucket_et(ep.get("decision_at"))] += 1
                session = None
                for row in ep.get("stages") or []:
                    if row.get("stage") == "context":
                        session = (row.get("operands") or {}).get("session")
                if session == "asia":
                    asia_hits += 1
                if session == "london":
                    london_hits += 1
                day = str(doc.get("session_date") or "")
                try:
                    if datetime.fromisoformat(day).weekday() == 0:
                        monday_passes += 1
                except ValueError:
                    pass
            for row in ep.get("stages") or []:
                name = row.get("stage")
                if name not in stage_counts:
                    continue
                stv = row.get("verdict") or "unknown"
                stage_counts[name][stv] += 1
                for key, value in (row.get("operands") or {}).items():
                    if key in {"reason", "mode", "id"}:
                        continue
                    if isinstance(value, (str, int, float, bool, Decimal)) or value is None:
                        stage_values[name][key].add(str(value))
        if session_hit:
            sessions_with_pass += 1
    passes = int(verdicts["pass"])
    pass_rate = (passes / episodes) if episodes else 0.0
    eps_per = (episodes / sessions) if sessions else 0.0
    bounds = _load_bounds(family, branch)
    ep_lo, ep_hi = (bounds.get("episodes_per_session") or [0, 99])[:2]
    pr_lo, pr_hi = (bounds.get("pass_rate") or [0.0, 1.0])[:2]
    in_bound = (ep_lo <= eps_per <= ep_hi) and (pr_lo <= pass_rate <= pr_hi)
    diagnosis = None
    if not in_bound:
        diagnosis = _human_justification(bounds, pass_rate, eps_per)
    return {
        "family": family,
        "branch": branch,
        "sessions": sessions,
        "episodes": episodes,
        "pass": passes,
        "fail": int(verdicts["fail"]),
        "unknown": int(verdicts["unknown"]),
        "pass_rate": round(pass_rate, 4),
        "episodes_per_session": round(eps_per, 4),
        "stage_counts": {name: dict(counter) for name, counter in stage_counts.items()},
        "time_of_entry_histogram_et_30m": {key: int(val) for key, val in sorted((k, v) for k, v in histogram.items() if k)},
        "asia_passes": asia_hits,
        "london_passes": london_hits,
        "monday_passes": monday_passes,
        "bound": {"episodes_per_session": [ep_lo, ep_hi], "pass_rate": [pr_lo, pr_hi], "source_claim": bounds.get("source_claim"), "page": bounds.get("page")},
        "sessions_with_pass": sessions_with_pass,
        "in_bound": in_bound,
        "diagnosis": diagnosis,
        "stage_value_nunique": {name: {key: len(vals) for key, vals in keys.items()} for name, keys in stage_values.items()},
        "stage_never_fails_while_varies": _never_fails(stage_counts, stage_values),
    }


def _human_justification(bounds: dict, pass_rate: float, eps_per: float) -> str | None:
    """Return a family-JSON justification only. Never invent a diagnosis string."""
    raw = bounds.get("observed_rate_justification")
    if not isinstance(raw, dict):
        return None
    page = str(raw.get("page") or "").strip()
    text = str(raw.get("text") or "").strip()
    if not page or not text:
        return None
    return f"{page}: {text}"


def _never_fails(stage_counts: dict, stage_values: dict) -> list[dict]:
    out = []
    for name, counter in stage_counts.items():
        if int(counter.get("fail") or 0) or int(counter.get("unknown") or 0):
            continue
        if int(counter.get("pass") or 0) == 0:
            continue
        varying = [key for key, vals in (stage_values.get(name) or {}).items() if len(vals) > 1]
        if varying:
            out.append({"stage": name, "varying_operands": varying})
    return out


def _audit_unmeasured(family: str) -> list[str]:
    audit = json.loads(_audit_path(family).read_text())
    bad = []
    for branch, body in (audit.get("branches") or {}).items():
        for stage, row in (body.get("stages") or {}).items():
            if row.get("measured"):
                continue
            if row.get("unobservable"):
                continue
            bad.append(f"{family}:{branch}:{stage} unmeasured without named unobservable")
    return bad


def test_p15_16a_plausibility_greenbird_gate():
    OUT.mkdir(parents=True, exist_ok=True)
    start_hashes = json.loads(HASH_START.read_text()) if HASH_START.is_file() else {"hashes": {}}
    by_branch: dict[tuple[str, str], list] = {(family, branch): [] for family, branches in BRANCHES.items() for branch in branches}
    load_errors = []
    for day in SLICE:
        try:
            market = load_source_market(day)
        except Exception as exc:
            load_errors.append({"date": day, "error": str(exc)})
            continue
        fail_doc = fail_scan(market, {"family": "GB-FAIL", "branch": "all"})
        grouped = defaultdict(list)
        for ep in fail_doc.get("episodes") or []:
            grouped[ep.get("branch")].append(ep)
        for branch in BRANCHES["GB-FAIL"]:
            by_branch[("GB-FAIL", branch)].append(
                {
                    "session_date": day,
                    "episodes": grouped.get(branch) or [],
                    "research_verdict": None,
                }
            )
        for family, branch in (("GB-VWAP", "source_long"), ("GB-SCALP", "golden_pocket_continuation")):
            by_branch[(family, branch)].append(_scan(market, family, branch))

    rebuilt = {}
    for (family, branch), rows in by_branch.items():
        if family == "GB-FAIL":
            docs = [{"session_date": row["session_date"], "episodes": row["episodes"]} for row in rows]
        else:
            docs = rows
        rebuilt[(family, branch)] = _summarize(docs, family, branch)

    family_box_passes = 0
    family_sessions = 0
    if rebuilt:
        family_sessions = rebuilt[("GB-FAIL", "nyam_box")]["sessions"]
    for branch in BOX_BRANCHES:
        family_box_passes += rebuilt[("GB-FAIL", branch)]["pass"]
    box_per_session = (family_box_passes / family_sessions) if family_sessions else 0.0
    box_in = box_per_session <= 2.0
    family_spec = json.loads(FAMILIES["GB-FAIL"].read_text())
    box_diag = _human_justification(family_spec.get("plausibility", {}).get("family_pass_cap_per_session") or {}, box_per_session, box_per_session)

    reports = {}
    for family in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
        payload = {
            "family": family,
            "slice": list(SLICE),
            "baseline": B02_VERSION,
            "load_errors": load_errors,
            "branches": {branch: rebuilt[(family, branch)] for branch in BRANCHES[family]},
        }
        if family == "GB-FAIL":
            payload["across_boxes"] = {
                "passes": family_box_passes,
                "sessions": family_sessions,
                "passes_per_session": round(box_per_session, 4),
                "bound": [0, 2],
                "in_bound": box_in,
                "diagnosis": box_diag,
                "page": "GB p.30, p.31",
            }
        reports[family] = payload
        (OUT / f"PLAUSIBILITY_{family}.json").write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
        lines = [f"# Plausibility {family}", "", f"slice n={len(SLICE)} baseline={B02_VERSION}", ""]
        lines.append("| branch | sessions | episodes | pass | fail | unknown | pass_rate | eps/session | bound | in/out |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        diagnoses = []
        for branch in BRANCHES[family]:
            row = rebuilt[(family, branch)]
            status = "in" if row["in_bound"] else "out"
            lines.append(
                f"| {branch} | {row['sessions']} | {row['episodes']} | {row['pass']} | {row['fail']} | {row['unknown']} | "
                f"{row['pass_rate']:.3f} | {row['episodes_per_session']:.2f} | "
                f"eps {row['bound']['episodes_per_session']} pr {row['bound']['pass_rate']} | {status} |"
            )
            if row["diagnosis"]:
                diagnoses.append(f"Diagnosis `{branch}`. {row['diagnosis']}")
        for note in diagnoses:
            lines.append("")
            lines.append(note)
        if family == "GB-FAIL":
            lines.append("")
            lines.append(
                f"Across GB-FAIL boxes (london/asia/nyam/previous_hour) passes/session={box_per_session:.3f} bound=[0,2] "
                f"{'in' if box_in else 'out'}."
            )
            if box_diag:
                lines.append(box_diag)
            nyam = rebuilt[("GB-FAIL", "nyam_box")]
            asia = rebuilt[("GB-FAIL", "asia_box")]
            london = rebuilt[("GB-FAIL", "london_box")]
            lines.append(
                f"Asia histogram passes={asia['asia_passes']+asia['pass'] and asia['time_of_entry_histogram_et_30m']}. "
                f"London passes={london['pass']} histogram={london['time_of_entry_histogram_et_30m']}."
            )
            nwog = rebuilt[("GB-FAIL", "nwog")]
            lines.append(f"NWOG monday_passes={nwog['monday_passes']} of {nwog['pass']} passes (GB pp.13,14,36,37).")
        (OUT / f"PLAUSIBILITY_{family}.md").write_text("\n".join(lines) + "\n")

    problems = []
    for family in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
        problems.extend(_audit_unmeasured(family))
        for branch in BRANCHES[family]:
            row = rebuilt[(family, branch)]
            if not row["in_bound"] and not row.get("diagnosis"):
                problems.append(
                    f"{family}:{branch} out of bound eps={row['episodes_per_session']:.3f} "
                    f"pr={row['pass_rate']:.3f} sessions_with_pass={row.get('sessions_with_pass')} "
                    f"bound={row['bound']} (no observed_rate_justification in family JSON)"
                )
            confirm_counts = row["stage_counts"].get("confirmation") or {}
            confirm_fails = int(confirm_counts.get("fail") or 0)
            for item in row["stage_never_fails_while_varies"]:
                if item["stage"] != "confirmation":
                    continue
                predicate = {
                    "confirm_close",
                    "inside_box",
                    "through_level",
                    "fail_to_continue",
                    "touched_vwap",
                    "retest_low",
                    "vwap",
                }
                varying_pred = [key for key in item["varying_operands"] if key in predicate]
                if varying_pred:
                    continue
                if confirm_fails == 0:
                    problems.append(
                        f"{family}:{branch}:confirmation never fails and records no varying market predicate {item['varying_operands']}"
                    )
    if not box_in and not box_diag:
        problems.append(
            f"GB-FAIL across-box passes/session={box_per_session:.3f} bound=[0,2] "
            "without observed_rate_justification that supports the observed rate"
        )

    if start_hashes.get("hashes"):
        for day in BYTE_DATES:
            market = load_source_market(day)
            for family, branch in (("GB-FAIL", "nyam_box"), ("GB-VWAP", "source_long")):
                dual = dual_scan(market, family, branch)
                b0 = content_hash(strip_baseline_version(dual["b0"]))
                b01 = content_hash(strip_baseline_version(dual["b01"]))
                assert b0 == start_hashes["hashes"][f"{day}|{family}|{branch}|B0"]
                assert b01 == start_hashes["hashes"][f"{day}|{family}|{branch}|B0.1"]

    assert not problems, problems
    assert (OUT / "PLAUSIBILITY_GB-FAIL.json").is_file()
    assert (OUT / "PLAUSIBILITY_GB-VWAP.md").is_file()
    assert (OUT / "PLAUSIBILITY_GB-SCALP.json").is_file()


def test_repair_replay_inside_tape_location_stage():
    from datetime import date
    from trading_research.research.rule_discovery.source_adapters.green_b02 import _date_outside_tape
    from trading_research.research.rule_discovery.source_adapters.green_failure import replay_example as fail_replay
    from trading_research.research.rule_discovery.source_adapters.green_vwap_scalp import replay_example as vwap_replay

    examples = json.loads(Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json").read_text())["examples"]
    gb = [row for row in examples if str(row.get("id", "")).startswith("GB-")]
    by_family = {"GB-FAIL": [], "GB-VWAP": [], "GB-SCALP": []}
    for example in gb:
        day = example.get("date")
        family_raw = str(example.get("family") or "GB-FAIL")
        if _date_outside_tape(example):
            row = fail_replay(None, example)
            assert row.get("divergence") == "date outside the tape"
            row["reached_location"] = None
            keys = ["GB-FAIL"]
            if "SCALP" in family_raw:
                keys = ["GB-FAIL", "GB-SCALP"] if "FAIL" in family_raw else ["GB-SCALP"]
            for key in keys:
                by_family[key].append(row)
            continue
        try:
            market = load_source_market(str(day)[:10])
        except Exception as exc:
            row = {
                "detected": None,
                "reached_location": None,
                "failing_stage": None,
                "failing_operand": f"operands_unavailable:{exc}",
                "example_id": example.get("id"),
                "divergence": f"operands_unavailable:{exc}",
            }
            by_family["GB-FAIL"].append(row)
            continue
        if "GB-SCALP" in family_raw or "VWAP" in family_raw:
            row = vwap_replay(market, example)
            if "SCALP" in family_raw:
                by_family["GB-SCALP"].append(row)
            if "VWAP" in family_raw:
                by_family["GB-VWAP"].append(row)
            if "FAIL" in family_raw:
                by_family["GB-FAIL"].append(fail_replay(market, example))
        else:
            by_family["GB-FAIL"].append(fail_replay(market, example))
    for family, rows in by_family.items():
        (OUT / f"REPLAY_{family}.json").write_text(json.dumps(rows, indent=2, sort_keys=True, default=str) + "\n")
    inside_fail = [row for row in by_family["GB-FAIL"] if row.get("detected") is not None]
    assert inside_fail
    missing_location = [
        row for row in inside_fail if row.get("detected") is False and row.get("reached_location") is False
    ]
    (OUT / "REPLAY_LOCATION_MISSES.json").write_text(
        json.dumps(missing_location, indent=2, sort_keys=True, default=str) + "\n"
    )
    for row in inside_fail:
        if row.get("detected") is False:
            assert row.get("failing_operand"), row


def test_mutated_asia_box_bound_fails_the_gate(tmp_path):
    spec = json.loads(FAMILIES["GB-FAIL"].read_text())
    spec["plausibility"]["asia_box"]["pass_rate"] = [0.0, 0.0]
    spec["plausibility"]["asia_box"].pop("observed_rate_justification", None)
    payload_path = OUT / "PLAUSIBILITY_GB-FAIL.json"
    assert payload_path.is_file()
    stats = json.loads(payload_path.read_text())["branches"]["asia_box"]
    bounds = spec["plausibility"]["asia_box"]
    in_bound = (
        bounds["episodes_per_session"][0] <= stats["episodes_per_session"] <= bounds["episodes_per_session"][1]
        and bounds["pass_rate"][0] <= stats["pass_rate"] <= bounds["pass_rate"][1]
    )
    just = _human_justification(bounds, stats["pass_rate"], stats["episodes_per_session"])
    assert stats["pass_rate"] > 0.0
    assert in_bound is False
    assert just is None


def test_after_tape_replay_does_not_call_build_event_window(monkeypatch):
    from datetime import date as date_cls
    from trading_research.research.method_pack import event_cache
    from trading_research.research.rule_discovery.source_adapters.green_b02 import _date_outside_tape
    from trading_research.research.rule_discovery.source_adapters.green_failure import replay_example as fail_replay

    def boom(*_a, **_k):
        raise AssertionError("build_event_window must not run for after-tape replay")

    monkeypatch.setattr(event_cache, "build_event_window", boom)
    examples = json.loads(Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json").read_text())["examples"]
    gb = [row for row in examples if str(row.get("id", "")).startswith("GB-")]
    after = [row for row in gb if _date_outside_tape(row)]
    assert after
    for example in after:
        row = fail_replay(None, example)
        assert row.get("detected") is None
        assert row.get("divergence") == "date outside the tape"
