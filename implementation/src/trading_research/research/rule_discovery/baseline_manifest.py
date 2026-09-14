"""Bind the accepted Phase 1 baseline and freeze engineering-date coverage."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from trading_research.errors import IntegrityError
from trading_research.research.contracts.identity import (
    ASSURANCE_VERSION,
    artifact_entry,
    canonical_value,
    code_snapshot_document,
    digest,
    file_digest,
    freeze_mapping,
    git_dirty_patch,
    make_task_receipt,
    plan_identity,
    plan_snapshot_document,
    semantic_run_id,
    write_json_document,
    write_snapshot_tree,
    write_task_receipt,
)
from trading_research.research.contracts.types import (
    Coverage,
    CoverageReceipt,
    EvidenceRef,
    FeatureValue,
    NativeBatch,
    NativeTrade,
    Opportunity,
    ScanResult,
    SequenceState,
    source_exact_from_baseline,
)
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.measurement_runner import measurement_scope
from trading_research.research.method_pack.session_policy import NQSessionPolicy

ROOT = Path("/workspace")
PHASE1_RUN = ROOT / "implementation/reports/phase1-live/historical-measurement/run-1.0.1"
PHASE1_REPORT = ROOT / "implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md"
OWNED_PATHS = (
    "implementation/src/trading_research/research/contracts/types.py",
    "implementation/src/trading_research/research/contracts/identity.py",
    "implementation/src/trading_research/research/rule_discovery/baseline_manifest.py",
    "implementation/tests/rule_discovery/test_p15_00.py",
)
PLAN_PATHS = (
    "planning/phase-1-5/tasks/P15-00.md",
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/phase-1-5/SPEC.md",
    "planning/research-program/TYPE_REFERENCE.py",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
)
CODE_PATHS = OWNED_PATHS + (
    "implementation/src/trading_research/errors.py",
    "implementation/src/trading_research/research/method_pack/empirical_protocol.py",
    "implementation/src/trading_research/research/method_pack/measurement_runner.py",
    "implementation/src/trading_research/research/method_pack/session_policy.py",
    "implementation/pyproject.toml",
)
INPUT_GROUPS = (
    {
        "group_id": "current_session_executions",
        "coverage_id": "JJ-TBR:branch:judas_outbound",
        "requirements": ("verified matching calendar", "current-session observed executions"),
        "complete_key": "current_complete",
    },
    {
        "group_id": "prior_same_contract_rth_profile",
        "coverage_id": "KEANI-OPEN-ABOVE-VALUE:branch:source_long",
        "requirements": ("verified matching calendar", "same-contract prior RTH profile lookback"),
        "complete_key": "eligible_complete_session",
    },
    {
        "group_id": "prior_month_levels",
        "coverage_id": "GB-FAIL:branch:prior_month_level",
        "requirements": ("verified matching calendar", "same-contract prior month lookback"),
        "complete_key": "eligible_complete_session",
    },
)
SUPERSEDED_P15_00 = {
    "path": "implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json",
    "sha256": "a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20",
}
YEARS = tuple(range(2020, 2027))
DST_ANCHOR = date(2023, 11, 5)
EXAMPLE_SHA = digest({"schema": "p15-00-schema-example"})
JOB_ROOT = PHASE1_RUN / "jobs/evaluation"
NATIVE_PARQUET = ROOT / "data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
NATIVE_ROW_INDEX = 769284


def job_file(day: str, coverage_id: str) -> Path:
    return JOB_ROOT / day / f"{coverage_id.replace(':', '--')}.json.gz"


@lru_cache(maxsize=None)
def load_job_coverage(day: str, coverage_id: str) -> dict[str, Any]:
    import gzip
    import json
    path = job_file(day, coverage_id)
    if not path.is_file():
        return {
            "date": day,
            "coverage_id": coverage_id,
            "status": "missing",
            "current_complete": False,
            "eligible_complete_session": False,
            "omission_reasons": ["job_missing"],
            "unknown_interval_count": 0,
            "path": str(path),
            "sha256": None,
            "market_feed_completeness": None,
        }
    document = json.loads(gzip.decompress(path.read_bytes()))
    accounting = document.get("session_accounting") or {}
    prefix = accounting.get("current_prefix_coverage") or {}
    omissions = [item for item in (accounting.get("active_omissions") or []) if isinstance(item, dict)]
    unknown = 0
    reasons = []
    for item in omissions:
        reason = item.get("reason")
        if reason:
            reasons.append(reason)
        coverage = item.get("coverage") or {}
        unknown += len(coverage.get("unknown_intervals") or [])
        states = coverage.get("states") or {}
        if isinstance(states.get("unknown_coverage"), int):
            unknown = max(unknown, states["unknown_coverage"])
    eligible = bool(accounting.get("eligible_complete_session"))
    current = bool(prefix.get("observed_scope_complete"))
    return {
        "date": day,
        "coverage_id": coverage_id,
        "status": "complete" if eligible else "partial" if current else "missing",
        "current_complete": current,
        "eligible_complete_session": eligible,
        "omission_reasons": reasons,
        "unknown_interval_count": unknown,
        "path": str(path),
        "sha256": file_digest(path),
        "market_feed_completeness": document.get("market_feed_completeness"),
        "selector": "/session_accounting",
    }


def build_input_groups(declared_dates: list[str], calendar_rows: list[Mapping[str, str]]) -> list[dict[str, Any]]:
    calendar = {row["date"]: row for row in calendar_rows}
    groups = []
    for spec in INPUT_GROUPS:
        rows = []
        for day in declared_dates:
            job = load_job_coverage(day, spec["coverage_id"])
            cal = calendar.get(day, {})
            if cal.get("status") != "complete":
                complete = False
            elif spec["group_id"] == "current_session_executions":
                complete = bool(job.get("current_complete"))
            else:
                complete = bool(job.get("eligible_complete_session"))
            row = {
                **job,
                "calendar_status": cal.get("status"),
                "status": "complete" if complete else ("partial" if job.get("current_complete") else job.get("status") or "missing"),
            }
            rows.append(row)
        selected = select_engineering_dates(rows)
        groups.append({
            "group_id": spec["group_id"],
            "requirements": list(spec["requirements"]),
            "coverage_id": spec["coverage_id"],
            "coverage_rows": rows,
            "year_slots": selected["year_slots"],
            "dst_slot": selected["dst_slot"],
            "source_inventory_sha256": digest({row["date"]: row.get("sha256") for row in rows}),
        })
    return groups


def executable_gap_fixture() -> dict[str, Any]:
    expected = ((0, 10), (10, 20), (20, 30))
    copied = expected[:-1]
    missing = expected[-1]
    return {
        "kind": "synthetic_fixture",
        "expected_intervals": [list(item) for item in expected],
        "observed_after_removal": [list(item) for item in copied],
        "unknown_interval": list(missing),
        "unknown_preserved": missing not in copied,
    }


def executable_batch_conflict_fixture() -> dict[str, Any]:
    evidence = EvidenceRef(EXAMPLE_SHA, ("r1",), 20, 20, 20, Coverage.COMPLETE, ())
    first = NativeTrade("t-a", "NQ:example", 20, 20, Decimal("98.50"), 1, -1, evidence)
    second = NativeTrade("t-b", "NQ:example", 20, 20, Decimal("102.00"), 1, 1, evidence)
    left = NativeBatch("b1", 20, 20, (first, second), False)
    right = NativeBatch("b2", 20, 20, (second, first), False)
    prices_left = tuple(trade.price for trade in left.trades)
    prices_right = tuple(trade.price for trade in right.trades)
    return {
        "kind": "synthetic_fixture",
        "prices_ab": [str(price) for price in prices_left],
        "prices_ba": [str(price) for price in prices_right],
        "ambiguity_preserved": set(prices_left) == set(prices_right),
        "internal_order_known": False,
    }


def replay_native_row() -> dict[str, Any]:
    import pyarrow.parquet as pq
    parquet = NATIVE_PARQUET
    digest_value = file_digest(parquet)
    file = pq.ParquetFile(parquet)
    group_rows = file.metadata.row_group(0).num_rows
    group = NATIVE_ROW_INDEX // group_rows
    offset = NATIVE_ROW_INDEX % group_rows
    table = file.read_row_group(group)
    raw = table.slice(offset, 1).to_pylist()[0]
    event_ns = int(raw["t"])
    if event_ns < 10**15:
        event_ns *= 1_000_000
    available_at_ns = event_ns
    evidence = EvidenceRef(digest_value, (f"{parquet}:{NATIVE_ROW_INDEX}",), event_ns, event_ns, available_at_ns, Coverage.COMPLETE, ())
    trade = NativeTrade(
        event_id=f"{parquet}:{NATIVE_ROW_INDEX}",
        asset_id=f"NQ:{raw.get('instrument_id')}",
        event_ns=event_ns,
        available_at_ns=available_at_ns,
        price=Decimal(str(raw["price"])),
        quantity=int(raw.get("size") or 0),
        aggressor=None,
        evidence=evidence,
    )
    return {
        "kind": "native",
        "source_path": str(parquet),
        "source_sha256": digest_value,
        "row_id": f"{parquet}:{NATIVE_ROW_INDEX}",
        "adapter": "pyarrow.parquet.ParquetFile.read_row_group",
        "serialized": canonical_value(trade),
        "event_ns": event_ns,
        "instrument_id": raw.get("instrument_id"),
        "price": str(trade.price),
    }


def _read_json(path: Path) -> Any:
    import json
    return json.loads(path.read_text())


def verify_declared_hash(document: Mapping[str, Any], field: str) -> str:
    body = {key: value for key, value in document.items() if key != field}
    declared = document[field]
    actual = content_hash(body)
    if actual != declared:
        raise IntegrityError(f"{field} does not match canonical content hash")
    return declared


def load_phase1_inputs() -> dict[str, Any]:
    registry_path = PHASE1_RUN / "registry/registry.json"
    coverage_path = PHASE1_RUN / "registry/coverage.json"
    protocol_path = PHASE1_RUN / "protocol/MEASUREMENT_PROTOCOL_1_1.json"
    calendar_path = PHASE1_RUN / "protocol/CALENDAR_RECOVERY_COMPOSITION.json"
    population_path = PHASE1_RUN / "protocol/ACQUIRED_INPUT_POPULATION.json"
    census_path = PHASE1_RUN / "validation/CENSUS_RECONCILIATION.json"
    acceptance_path = PHASE1_RUN / "validation/ACCEPTANCE.json"
    registry = _read_json(registry_path)
    coverage = _read_json(coverage_path)
    calendar = _read_json(calendar_path)
    census = _read_json(census_path)
    acceptance = _read_json(acceptance_path)
    protocol = _read_json(protocol_path)
    population = _read_json(population_path)
    registry_sha256 = verify_declared_hash(registry, "registry_sha256")
    coverage_sha256 = verify_declared_hash(coverage, "manifest_sha256")
    calendar_sha256 = verify_declared_hash(calendar, "composition_sha256")
    if coverage_sha256 != registry["coverage_sha256"]:
        raise IntegrityError("registry coverage_sha256 does not match coverage manifest")
    if file_digest(Path(registry["scope_path"])) != registry["scope_sha256"]:
        raise IntegrityError("frozen scope file digest changed")
    if census["registry_sha256"] != registry_sha256:
        raise IntegrityError("census registry identity differs from the bound registry")
    if census["status"] != "pass":
        raise IntegrityError("accepted census status is not pass")
    if acceptance["registry_sha256"] != registry_sha256:
        raise IntegrityError("acceptance registry identity differs from the bound registry")
    if acceptance["status"] != "completed_with_explicit_input_limitations":
        raise IntegrityError("acceptance status is not the completed census gate")
    return {
        "registry": registry,
        "coverage": coverage,
        "calendar": calendar,
        "census": census,
        "acceptance": acceptance,
        "protocol": protocol,
        "population": population,
        "paths": {
            "registry": registry_path,
            "coverage": coverage_path,
            "protocol": protocol_path,
            "calendar": calendar_path,
            "population": population_path,
            "census": census_path,
            "acceptance": acceptance_path,
            "report": PHASE1_REPORT,
            "scope": Path(registry["scope_path"]),
        },
        "identities": {
            "registry_sha256": registry_sha256,
            "coverage_sha256": coverage_sha256,
            "calendar_sha256": calendar_sha256,
            "scope_sha256": registry["scope_sha256"],
            "software_sha256": registry["software"]["sha256"],
            "protocol_file_sha256": file_digest(protocol_path),
            "census_file_sha256": file_digest(census_path),
            "acceptance_file_sha256": file_digest(acceptance_path),
            "report_file_sha256": file_digest(PHASE1_REPORT),
            "registry_file_sha256": file_digest(registry_path),
            "coverage_file_sha256": file_digest(coverage_path),
            "calendar_file_sha256": file_digest(calendar_path),
            "population_file_sha256": file_digest(population_path),
        },
    }


def bind_units(coverage: Mapping[str, Any]) -> dict[str, Any]:
    units = []
    scope_counts: dict[str, int] = {}
    for row in coverage["branches"]:
        scope = measurement_scope(row["method_id"], row["branch"])
        scope_counts[scope] = scope_counts.get(scope, 0) + 1
        units.append({
            "coverage_id": row["coverage_id"],
            "method_id": row["method_id"],
            "branch": row["branch"],
            "extra_unit": row["extra_unit"],
            "observation_unit": row["observation_unit"],
            "scope_kind": scope,
            "implementation_state": row["implementation_state"],
            "input_limits": [
                {"id": item.get("id"), "required": item.get("required"), "recovery": item.get("recovery")}
                for item in row.get("input_limits", [])
            ],
            "scanner": row.get("scanner"),
            "producer": row.get("producer"),
        })
    extra = sum(1 for unit in units if unit["extra_unit"])
    branches = len(units) - extra
    if branches != 50 or extra != 8 or len(units) != 58:
        raise IntegrityError(f"expected 50 branches and 8 extra units, found {branches}+{extra}")
    if coverage["counts"]["branches"] != 50 or coverage["counts"]["additional_units"] != 8:
        raise IntegrityError("coverage count fields do not reconcile to 50+8")
    return {
        "units": units,
        "branch_count": branches,
        "extra_unit_count": extra,
        "unit_count": len(units),
        "scope_counts": dict(sorted(scope_counts.items())),
        "methods": coverage["counts"]["methods"],
    }


def classify_declared_dates(
    declared_dates: list[str],
    *,
    policy: NQSessionPolicy,
    partial_final_date: str,
) -> list[dict[str, str]]:
    rows = []
    for label in declared_dates:
        day = date.fromisoformat(label)
        calendar = policy.day(day)
        state = calendar["state"]
        if label == partial_final_date:
            status = "partial"
            reason = "owned native endpoint is exclusive of a completed matching session"
        elif state == "closed_rth":
            status = "missing"
            reason = calendar.get("reason", "closed_rth")
        elif state == "unverified_holiday":
            status = "ambiguous"
            reason = calendar.get("reason", "unverified_holiday")
        elif state in {"regular", "early_close"}:
            status = "complete"
            reason = calendar.get("reason", state)
        else:
            status = "ambiguous"
            reason = calendar.get("reason", state)
        rows.append({
            "date": label,
            "status": status,
            "calendar_state": state,
            "reason": str(reason),
        })
    return rows


def select_engineering_dates(
    rows: list[Mapping[str, str]],
    *,
    years: tuple[int, ...] = YEARS,
    dst_anchor: date = DST_ANCHOR,
) -> dict[str, Any]:
    complete = [date.fromisoformat(row["date"]) for row in rows if row["status"] == "complete"]
    year_slots = []
    for year in years:
        year_dates = [item for item in complete if item.year == year]
        if year_dates:
            chosen = min(year_dates)
            year_slots.append({"year": year, "status": "complete", "date": chosen.isoformat()})
        else:
            year_slots.append({"year": year, "status": "missing", "date": None})
    if complete:
        chosen = min(complete, key=lambda item: (abs((item - dst_anchor).days), item))
        dst_slot = {
            "anchor": dst_anchor.isoformat(),
            "status": "complete",
            "date": chosen.isoformat(),
            "tie_rule": "earlier",
        }
    else:
        dst_slot = {
            "anchor": dst_anchor.isoformat(),
            "status": "missing",
            "date": None,
            "tie_rule": "earlier",
        }
    return {
        "schema": "research-engineering-dates-v1",
        "years": list(years),
        "year_slots": year_slots,
        "dst_slot": dst_slot,
        "complete_eligible_dates": len(complete),
        "declared_dates": len(rows),
        "status_counts": {
            status: sum(1 for row in rows if row["status"] == status)
            for status in ("complete", "partial", "missing", "ambiguous")
        },
    }


def _example_evidence(start_ns: int, end_ns: int) -> EvidenceRef:
    return EvidenceRef(
        artifact_sha256=EXAMPLE_SHA,
        row_ids=("row-1",),
        event_start_ns=start_ns,
        event_end_ns=end_ns,
        available_at_ns=end_ns,
        coverage=Coverage.COMPLETE,
        limitation_ids=(),
    )


def schema_examples() -> dict[str, Any]:
    start = 1_577_923_800_000_000_000
    end = start + 60_000_000_000
    evidence = _example_evidence(start, end)
    payload_unknown = freeze_mapping({
        "schema": "phase1-historical-episode-v2",
        "author_exact_verdict": "unknown",
        "faithful_eligible": False,
        "actual_trade": False,
        "research_verdict": "pass",
        "source_contract_verdict": "unknown",
        "method": "JJ-TBR",
        "branch": "judas_outbound",
    })
    entry = Opportunity(
        opportunity_id=digest({"kind": "entry", "branch": "judas_outbound", "t": start}),
        parent_opportunity_id=None,
        overlap_group_id=digest({"native": "NQ", "trigger": "row-1", "formation": "f1"}),
        rule_id="JJ-TBR:branch:judas_outbound",
        family="JJ-TBR",
        branch="judas_outbound",
        account_day="2020-01-02",
        side=1,
        issue_at_ns=start,
        decision_at_ns=end,
        reference_asset="NQ:example",
        response_asset="NQ:example",
        execution_asset="NQ:example",
        reference_id="ref-1",
        lower=Decimal("1.00"),
        upper=Decimal("2.00"),
        entry_reference=Decimal("1.00"),
        invalidation=Decimal("0.75"),
        objective=Decimal("3.00"),
        expiry_at_ns=end + 3_600_000_000_000,
        stages=(evidence,),
        coverage=Coverage.COMPLETE,
        source_exact=source_exact_from_baseline(payload_unknown),
        hypothesis_ids=("H-baseline",),
    )
    context = Opportunity(
        opportunity_id=digest({"kind": "context", "branch": "touch_record", "t": start}),
        parent_opportunity_id=None,
        overlap_group_id=digest({"native": "NQ", "trigger": "zone-1", "formation": "z1"}),
        rule_id="REFILL-STUDY:branch:touch_record",
        family="REFILL-STUDY",
        branch="touch_record",
        account_day="2020-01-02",
        side=-1,
        issue_at_ns=start,
        decision_at_ns=end,
        reference_asset="NQ:example",
        response_asset="NQ:example",
        execution_asset="NQ:example",
        reference_id="ref-zone",
        lower=Decimal("10.00"),
        upper=Decimal("10.50"),
        entry_reference=None,
        invalidation=None,
        objective=None,
        expiry_at_ns=end + 3_600_000_000_000,
        stages=(evidence,),
        coverage=Coverage.COMPLETE,
        source_exact=False,
        hypothesis_ids=("H-context",),
    )
    personal = Opportunity(
        opportunity_id=digest({"kind": "personal", "branch": "first", "t": start}),
        parent_opportunity_id=None,
        overlap_group_id=digest({"process": "stoic-risk", "stage": "first"}),
        rule_id="STOIC-RISK:branch:first",
        family="STOIC-RISK",
        branch="first",
        account_day="2020-01-02",
        side=1,
        issue_at_ns=start,
        decision_at_ns=end,
        reference_asset="NQ:example",
        response_asset="NQ:example",
        execution_asset="NQ:example",
        reference_id="risk-first",
        lower=Decimal("0"),
        upper=Decimal("0"),
        entry_reference=None,
        invalidation=None,
        objective=None,
        expiry_at_ns=end,
        stages=(evidence,),
        coverage=Coverage.MISSING,
        source_exact=False,
        hypothesis_ids=("H-personal-out-of-scope",),
    )
    missing = FeatureValue(
        name="kg1",
        value=None,
        unit="points",
        available_at_ns=end,
        evidence=(),
        missing_reason="KG1/key-gamma model input unavailable",
    )
    batch = NativeBatch(
        batch_id="batch-ambiguous",
        event_ns=end,
        available_at_ns=end,
        trades=(
            NativeTrade(
                event_id="t-ask",
                asset_id="NQ:example",
                event_ns=end,
                available_at_ns=end,
                price=Decimal("102.00"),
                quantity=1,
                aggressor=1,
                evidence=evidence,
            ),
            NativeTrade(
                event_id="t-bid",
                asset_id="NQ:example",
                event_ns=end,
                available_at_ns=end,
                price=Decimal("98.50"),
                quantity=1,
                aggressor=-1,
                evidence=evidence,
            ),
        ),
        internal_order_known=False,
    )
    scan = ScanResult(
        opportunities=(entry, context, personal),
        rejected_contacts=(),
        unknown_contacts=(),
        formations=(),
        sequences=(
            SequenceState(
                sequence_id="seq-1",
                recipe_id="B0",
                contact_id="c-1",
                state="input_unknown",
                state_at_ns=end,
                available_at_ns=end,
                deadline_ns=end + 600_000_000_000,
                stage_evidence=(),
                terminal_reason="same_batch_ambiguous",
                working_memory={"possible_prices": ["98.50", "102.00"]},
            ),
        ),
        coverage=CoverageReceipt(
            start_ns=start,
            end_ns=end,
            status=Coverage.AMBIGUOUS,
            expected_matching_intervals=((start, end),),
            observed_intervals=((start, end),),
            missing_intervals=(),
            calendar_sha256=EXAMPLE_SHA,
            evidence=(evidence,),
        ),
        baseline_payloads=(dict(payload_unknown),),
    )
    return {
        "schema": "research-schema-examples-v1",
        "decimal_canonical": str(Decimal("1.00")),
        "entry_setup": canonical_value(entry),
        "context_or_research": canonical_value(context),
        "personal_execution": canonical_value(personal),
        "missing_input": canonical_value(missing),
        "same_batch_ambiguity": {
            "batch": canonical_value(batch),
            "internal_order_known": False,
            "scan": canonical_value(scan),
        },
        "author_exact_unknown_round_trip": {
            "payload_author_exact_verdict": payload_unknown["author_exact_verdict"],
            "source_exact": entry.source_exact,
        },
    }


def engineering_fixtures(rows: list[Mapping[str, str]], *, partial_final_date: str) -> dict[str, Any]:
    unverified = next((row for row in rows if row["calendar_state"] == "unverified_holiday"), None)
    return {
        "partial_final_date": {
            "date": partial_final_date,
            "status": "partial",
            "reason": "owned MBP-1 endpoint is exclusive; session label is not a completed RTH day",
        },
        "roll": {
            "status": "archive_membership_map",
            "path": "/workspace/data/derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet",
            "identity_use": "acquired continuous membership only, not a tradable roll forecast",
        },
        "unverified_holiday": unverified or {"status": "missing", "reason": "no unverified holiday in declared dates"},
        "feed_gap": {
            "status": "not_in_calendar_metadata",
            "reason": "session prefix holes are recorded on Phase 1 jobs, not in the calendar coverage used here",
        },
        "same_timestamp_conflict": {
            "status": "synthetic_fixture",
            "reason": "same-timestamp conflicting events are a typed fixture, not a selected study date",
        },
    }


@lru_cache(maxsize=1)
def bind_baseline() -> dict[str, Any]:
    inputs = load_phase1_inputs()
    units = bind_units(inputs["coverage"])
    census_totals = inputs["census"]["totals"]
    if census_totals["setups"] != 18747:
        raise IntegrityError("bound census setup count is not 18747")
    if census_totals["daily_jobs"] != 99294:
        raise IntegrityError("bound census daily job count is not 99294")
    if census_totals["sessions"] != 1742:
        raise IntegrityError("bound census session count is not 1742")
    policy = NQSessionPolicy()
    declared = list(inputs["registry"]["scope"]["evaluation_dates"])
    partial_final_date = inputs["registry"]["scope"]["study_end"]
    date_rows = classify_declared_dates(declared, policy=policy, partial_final_date=partial_final_date)
    groups = build_input_groups(declared, date_rows)
    dates = {
        "schema": "research-engineering-dates-v2",
        "policy": "per-input-group native coverage with same-contract lookbacks; calendar is necessary but not sufficient",
        "calendar_sha256": policy.sha256,
        "coverage_sha256": inputs["identities"]["coverage_sha256"],
        "partial_final_date": partial_final_date,
        "classified_dates": date_rows,
        "input_groups": groups,
        "year_slots": groups[0]["year_slots"],
        "dst_slot": groups[0]["dst_slot"],
        "declared_dates": len(date_rows),
        "complete_eligible_dates": groups[0]["year_slots"] and select_engineering_dates(groups[0]["coverage_rows"])["complete_eligible_dates"],
        "status_counts": select_engineering_dates(groups[0]["coverage_rows"])["status_counts"],
        "fixtures": {
            **engineering_fixtures(date_rows, partial_final_date=partial_final_date),
            "feed_gap": executable_gap_fixture(),
            "same_timestamp_conflict": executable_batch_conflict_fixture(),
        },
        "native_replay": replay_native_row(),
        "discriminating_negatives": {
            "2020-01-02_prior_profile": next(
                row for row in groups[1]["coverage_rows"] if row["date"] == "2020-01-02"
            ),
        },
    }
    exposure = {
        "schema": "research-exposure-ledger-v1",
        "registry_sha256": inputs["identities"]["registry_sha256"],
        "outcome_blind": inputs["registry"]["evaluation_exposure"]["outcome_blind"],
        "purpose": inputs["registry"]["evaluation_exposure"]["purpose"],
        "policy_changes_after_outcomes": inputs["registry"]["evaluation_exposure"]["policy_changes_after_outcomes"],
        "implementation_fixes_after_development": inputs["registry"]["evaluation_exposure"]["implementation_fixes_after_development"],
        "initial_policy_exposure": inputs["registry"]["evaluation_exposure"]["initial_policy_exposure"],
        "development_artifact_count": len(inputs["registry"]["evaluation_exposure"]["development_artifacts"]),
        "earlier_run_registry_sha256": {
            path: value["registry_sha256"]
            for path, value in inputs["registry"]["evaluation_exposure"]["earlier_attempts"].items()
        },
        "note": "Phase 1 engineering exposure is copied from the accepted registry. It is not reconstructed from the current wiki hash.",
        "assurance_version": ASSURANCE_VERSION,
        "supersedes": SUPERSEDED_P15_00,
        "coverage_rule_correction": "Engineering completeness is per input group. Open calendar days with missing same-contract prior profiles are not complete prior-profile inputs.",
        "previously_exposed_engineering_dates": ["2020-01-02", "2021-01-04", "2022-01-03", "2023-01-03", "2024-01-02", "2025-01-02", "2026-01-02", "2023-11-06"],
    }
    binding = {
        "schema": "research-baseline-binding-v1",
        "phase1_run_id": inputs["protocol"].get("run_id"),
        "identities": inputs["identities"],
        "census": {
            "status": inputs["census"]["status"],
            "totals": {
                "sessions": census_totals["sessions"],
                "daily_jobs": census_totals["daily_jobs"],
                "setups": census_totals["setups"],
                "native_executions": census_totals["native_executions"],
                "duplicate_opportunities": census_totals["duplicate_opportunities"],
                "future_leakage": census_totals["future_leakage"],
            },
            "setups_are_branch_opportunities": True,
            "setups_are_independent_trades": False,
        },
        "units": units,
        "strategy_reconstruction": inputs["registry"]["strategy_reconstruction"],
        "clock_contract": inputs["registry"]["clock_contract"],
        "software_sha256": inputs["identities"]["software_sha256"],
        "wiki_not_used_for_identity": True,
        "acceptance_status": inputs["acceptance"]["status"],
        "study_start": inputs["registry"]["scope"]["study_start"],
        "study_end": inputs["registry"]["scope"]["study_end"],
        "assurance_version": ASSURANCE_VERSION,
        "supersedes": SUPERSEDED_P15_00,
        "phase1_software_file_count": 248,
    }
    examples = schema_examples()
    examples["schema"] = "research-schema-examples-v2"
    examples["native_replay"] = dates["native_replay"]
    examples["synthetic_labelled"] = True
    return {
        "binding": binding,
        "exposure": exposure,
        "dates": dates,
        "examples": examples,
        "inputs": inputs,
    }


def draft_manifest(bound: Mapping[str, Any], *, plan_sha256: str, code_sha256: str) -> dict[str, Any]:
    return {
        "schema_version": "research-draft-manifest-v2",
        "task_id": "P15-00",
        "assurance_version": ASSURANCE_VERSION,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": {},
        "input_identities": {
            name: {"path": str(path), "sha256": file_digest(path)}
            for name, path in bound["inputs"]["paths"].items()
        },
        "coverage_identity": bound["dates"].get("coverage_sha256"),
        "registered_candidate_config": None,
        "declared_study_dates": {
            "start": bound["binding"]["study_start"],
            "end": bound["binding"]["study_end"],
        },
    }


def write_p15_00_artifacts(run_root: Path | None = None) -> dict[str, Any]:
    import sys
    bound = bind_baseline()
    plan_files = {rel: file_digest(ROOT / rel) for rel in PLAN_PATHS}
    code_files = {rel: file_digest(ROOT / rel) for rel in CODE_PATHS}
    staging = Path(run_root) if run_root is not None else Path("/tmp/p15-00-staging")
    staging.mkdir(parents=True, exist_ok=True)
    plan_copies = write_snapshot_tree(staging, "plan", plan_files, root=ROOT)
    code_copies = write_snapshot_tree(staging, "code", code_files, root=ROOT)
    plan_doc = plan_snapshot_document(plan_files, plan_copies)
    lock = ROOT / "implementation/uv.lock"
    lock_sha = file_digest(lock) if lock.is_file() else file_digest(ROOT / "implementation/pyproject.toml")
    code_doc = code_snapshot_document(
        code_files,
        code_copies,
        runtime={"python": sys.version.split()[0]},
        dependency_lock_sha256=lock_sha,
        imported_modules=[
            "trading_research.errors",
            "trading_research.research.contracts.identity",
            "trading_research.research.contracts.types",
            "trading_research.research.method_pack.empirical_protocol",
            "trading_research.research.method_pack.measurement_runner",
            "trading_research.research.method_pack.session_policy",
        ],
    )
    plan_sha256 = digest(plan_files)
    code_sha256 = digest(code_doc)
    draft = draft_manifest(bound, plan_sha256=plan_sha256, code_sha256=code_sha256)
    run_id = semantic_run_id(draft)
    attempt = Path(run_root) if run_root is not None else ROOT / "implementation/reports/research-work/P15-00" / run_id / "attempt-0001"
    attempt.mkdir(parents=True, exist_ok=True)
    if staging.resolve() != attempt.resolve():
        write_snapshot_tree(attempt, "plan", plan_files, root=ROOT)
        write_snapshot_tree(attempt, "code", code_files, root=ROOT)
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    write_json_document(attempt / "BASELINE_BINDING.json", bound["binding"])
    write_json_document(attempt / "EXPOSURE_LEDGER.json", bound["exposure"])
    write_json_document(attempt / "ENGINEERING_DATES.json", bound["dates"])
    write_json_document(attempt / "SCHEMA_EXAMPLES.json", bound["examples"])
    snapshot = {
        "schema": "research-worktree-snapshot-v1",
        "owned_paths": list(OWNED_PATHS),
        "dirty_patch_sha256": digest(git_dirty_patch(OWNED_PATHS, cwd=ROOT)),
        "unrelated_note": "Unrelated working-tree wiki/planning moves were present at coordinator start and were not staged into this binding.",
        "supersedes": SUPERSEDED_P15_00,
    }
    write_json_document(attempt / "WORKTREE_SNAPSHOT.json", snapshot)
    return {
        "run_id": run_id,
        "attempt": attempt,
        "draft": draft,
        "bound": bound,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "plan": {"sha256": plan_sha256, "files": plan_files},
        "code": {"files": code_files},
    }


def write_p15_00_receipt(
    attempt: Path,
    *,
    run_id: str,
    plan_sha256: str,
    code_sha256: str,
    command_results: list[dict[str, Any]],
    acceptance_checks: Mapping[str, bool],
    coverage: Mapping[str, Any],
    unresolved: list[str],
    reason: str,
) -> dict[str, Any]:
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("BASELINE_BINDING.json", "research-baseline-binding-v1", None),
        ("EXPOSURE_LEDGER.json", "research-exposure-ledger-v1", None),
        ("ENGINEERING_DATES.json", "research-engineering-dates-v2", None),
        ("SCHEMA_EXAMPLES.json", "research-schema-examples-v2", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", None),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
    ]
    manifest = [
        artifact_entry(attempt / name, schema=schema, row_count=rows)
        for name, schema, rows in named
        if (attempt / name).exists()
    ]
    receipt = make_task_receipt(
        task_id="P15-00",
        run_id=run_id,
        plan_sha256=plan_sha256,
        code_sha256=code_sha256,
        predecessor_receipts={},
        command_results=command_results,
        artifact_manifest=manifest,
        acceptance_checks=acceptance_checks,
        disposition="implemented_verified" if all(acceptance_checks.values()) else "blocked_implementation",
        reason=reason,
        coverage=coverage,
        unresolved=unresolved,
    )
    write_task_receipt(attempt / "TASK_RECEIPT.json", receipt)
    return receipt
