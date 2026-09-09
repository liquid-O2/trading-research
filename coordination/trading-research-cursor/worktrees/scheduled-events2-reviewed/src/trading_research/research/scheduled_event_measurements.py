"""Acquired scheduled-event calendar measurement and retrospective window links.

Retrospective labels only. This is not Context and does not establish a
historical predictive calendar. Combined topical tables are aliases only after
an exact multiset check. Date-only rows do not invent an intraday time.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import unittest
from html.parser import HTMLParser

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.time import MINUTE, datetime_ns, timestamp
from trading_research.operations.artifacts import artifact_ref, digest
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries

from trading_research.research.jumbo_matrix import _read_columns
from trading_research.research.jumbo_timing_statistics import (
    ORIGINAL_NQ2024_VARIANT, PRIMARY_VARIANT, authenticate_workers, split_source_variants,
)

VERSION = "scheduled-event-measurement-v1"
POPULATION_START = date(2020, 1, 1)
POPULATION_END = date(2026, 9, 3)
NY_ZONE = "America/New_York"
HORIZONS_MINUTES = (1, 5, 15, 60)
NORMALIZED_FIELDS = (
    "event_date", "event_ts_utc", "event_time_et", "event_type", "event_name",
    "symbol", "status", "time_basis", "source", "source_url", "details_json",
)
ENGLISH_MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}
BLS_TYPE = {"CPI": "cpi", "Employment Situation": "nfp"}
TOPICAL_SUBJECTS = ("economic", "fomc", "market", "earnings")
FORMATION_LINK_COLUMNS = (
    "date", "clock", "contract_key", "formation_id", "root", "year",
    "source_version", "definition", "source_ids", "variant_role", "window_version",
    "formation_start_ns", "formation_end_ns", "available_at_ns", "calendar_known_at_ns",
    "status",
)
JUMBO_FAMILY = "Research-Jumbo-acquired-contract-OHLC-v1"
UNAVAILABLE_QUESTIONS = (
    {
        "id": "historical_predictive_calendar_availability",
        "reason": "Acquired rows are retrospectively observed labels. known_at_ns is null and causal_feature_eligible is false unless an explicit pre-event publication timestamp exists. File mtime and date-minus-one-day are not publication.",
    },
    {
        "id": "release_revision_and_surprise_vintage",
        "reason": "FRED release_last_updated is null. Consensus/revision vintages are absent. Surprise fields in earnings details are not treated as known-at-event.",
    },
    {
        "id": "earnings_announcement_clock_vintage",
        "reason": "Earnings time_basis is source_timestamp. Historical announcement vintage is unknown; no surprise-as-known inference.",
    },
    {
        "id": "fomc_intraday_decision_time",
        "reason": "Normalized FOMC rows are date_only with null timestamps. 14:00 is not invented.",
    },
    {
        "id": "bls_snapshot_selection_vintage",
        "reason": "Raw BLS table triplets are compared to the CSV. Per-page historical capture timestamps are not present in these renamed source files, so latest-snapshot selection and pre-event calendar availability remain uncertified.",
    },
    {
        "id": "complete_no_event_coverage",
        "reason": "A date without a record is no_record_on_date plus coverage_unknown unless that source/year completeness is established independently. Min/max date span is not completeness.",
    },
    {
        "id": "context_or_predictive_event_quality",
        "reason": "This measurement emits retrospective cohorts and window links only. It does not fit Context, score paths, or claim predictive quality.",
    },
    {
        "id": "auction_window_population",
        "reason": "link_window is the reusable half-open linker for a later auction-window driver. This run binds Jumbo formations only.",
    },
)


def store_read_bytes(store, ref):
    """Read artifact bytes through ArtifactStore.read_bytes or read."""
    handle = artifact_ref({k: ref[k] for k in ("sha256", "size_bytes", "kind")})
    reader = getattr(store, "read_bytes", None)
    if reader is not None:
        return reader(handle)
    return store.read(handle)


def store_read_json(store, ref):
    handle = artifact_ref({k: ref[k] for k in ("sha256", "size_bytes", "kind")})
    return store.read_json(handle)


def _json_safe(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, bytes):
        return value.hex()
    return value


def _as_date(value):
    if value is None:
        return None
    if type(value) is date:
        return value
    if isinstance(value, datetime):
        return value.date()
    if type(value) is str:
        return date.fromisoformat(value[:10])
    raise ContractError("event_date must be a civil date")


def _as_utc_ns(value):
    if value is None:
        return None
    if type(value) is int:
        return timestamp(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return datetime_ns(value.astimezone(timezone.utc))
    if type(value) is str:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return datetime_ns(parsed.astimezone(timezone.utc))
    raise ContractError("event timestamp is not a UTC clock")


def _wall_time(value):
    if value in (None, ""):
        return None
    if type(value) is not str:
        raise ContractError("event_time_et must be a wall-time string")
    text = value.strip()
    if re.fullmatch(r"\d{1,2}:\d{2}$", text):
        text += ":00"
    try:
        wall = time.fromisoformat(text)
    except ValueError as exc:
        raise ContractError("invalid event wall time") from exc
    if wall.tzinfo is not None:
        raise ContractError("event wall time must be zone-less")
    return wall


def _iso_date(value):
    day = _as_date(value)
    return None if day is None else day.isoformat()


def _copy_row(row):
    if not isinstance(row, dict):
        raise ContractError("source rows must be mappings")
    return {key: row[key] for key in row}


def _details(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if type(value) is str and value:
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {"unparsed_details": value}
        return parsed if isinstance(parsed, dict) else {"unparsed_details": value}
    return {}


def _semantic_id(event_type, event_date, *, symbol=None, time_basis=None, event_time_et=None):
    day = _iso_date(event_date)
    symbol_part = "" if symbol in (None, "") else str(symbol)
    time_part = "date_only" if time_basis == "date_only" or not event_time_et else _wall_time(str(event_time_et)).isoformat()
    return f"{event_type}|{day}|{symbol_part}|{time_part}"


def _alias_group(event_type, event_date, *, symbol=None):
    symbol_part = "" if symbol in (None, "") else str(symbol)
    return f"{event_type}|{_iso_date(event_date)}|{symbol_part}"


def publication_eligibility(*, event_date, event_ts_utc_ns, time_basis, explicit_published_at_ns=None,
                            snapshot_date=None, file_mtime_ns=None):
    """ROOT-FROZEN availability. File mtime is ignored. No date-minus-one."""
    del file_mtime_ns
    day = _as_date(event_date)
    if day is None:
        return {"known_at_ns": None, "causal_feature_eligible": False,
                "availability_reason": "unparsed_or_missing_event_date",
                "publication_after_event": False, "time_precision": "unknown",
                "intraday_functions_defined": False}
    known_at_ns = None
    causal = False
    reason = "retrospective_observed_calendar_label"
    publication_after_event = False
    if snapshot_date is not None:
        snap = _as_date(snapshot_date)
        if snap is not None and snap > day:
            publication_after_event = True
            reason = "snapshot_or_publication_after_event_cannot_be_early_known"
    if explicit_published_at_ns is not None:
        published = timestamp(explicit_published_at_ns)
        event_clock = event_ts_utc_ns if event_ts_utc_ns is not None else local_timestamp(day, time(0), NY_ZONE)
        if published < event_clock:
            known_at_ns = published
            causal = True
            reason = "explicit_pre_event_publication_timestamp"
        else:
            publication_after_event = True
            reason = "snapshot_or_publication_after_event_cannot_be_early_known"
    return {
        "known_at_ns": known_at_ns,
        "causal_feature_eligible": causal,
        "availability_reason": reason,
        "publication_after_event": publication_after_event,
        "time_precision": "intraday_timestamp" if time_basis == "source_timestamp" and event_ts_utc_ns is not None
        else ("standard_release_time" if time_basis == "standard_release_time" and event_ts_utc_ns is not None
              else "date_only"),
        "intraday_functions_defined": bool(event_ts_utc_ns is not None and time_basis != "date_only"),
    }


def parse_fomc_csv_row(row):
    """Decision date is the last listed day. Odd/multi-month strings stay unparsed."""
    original = _copy_row(row)
    year_text = str(original.get("year") or "").strip()
    month_text = str(original.get("month") or "").strip()
    days_text = str(original.get("days") or "").strip()
    raw_range = f"{year_text} {month_text} {days_text}".strip()
    unparsed = {
        "parsed": False, "unparsed": True, "decision_date": None, "range_start": None,
        "range_end": None, "raw_range": raw_range, "year": original.get("year"),
        "month": original.get("month"), "days": original.get("days"),
        "reason": "fomc_alternative_row_unparsed_not_guessed",
    }
    if not year_text.isdigit() or month_text not in ENGLISH_MONTHS:
        return unparsed
    if not re.fullmatch(r"\d{1,2}(-\d{1,2})*", days_text):
        return unparsed
    year = int(year_text)
    month = ENGLISH_MONTHS[month_text]
    parts = [int(part) for part in days_text.split("-")]
    if any(part < 1 or part > 31 for part in parts):
        return unparsed
    try:
        dates = [date(year, month, part) for part in parts]
    except ValueError:
        return unparsed
    if dates != sorted(dates):
        return unparsed
    return {
        "parsed": True, "unparsed": False, "decision_date": dates[-1],
        "range_start": dates[0], "range_end": dates[-1], "raw_range": raw_range,
        "year": year, "month": month_text, "days": days_text, "reason": None,
    }


def bls_release_type(release_name):
    if release_name not in BLS_TYPE:
        raise ContractError(f"unsupported BLS release_name: {release_name}")
    return BLS_TYPE[release_name]


def bls_timestamp(event_date, time_et):
    day = _as_date(event_date)
    wall = _wall_time(time_et)
    if day is None or wall is None:
        raise ContractError("BLS rows require a civil date and ET wall time")
    return local_timestamp(day, wall, NY_ZONE)


def _normalized_identity(row):
    day = _as_date(row.get("event_date"))
    ts = row.get("event_ts_utc")
    ts_text = None if ts is None else (ts.isoformat() if isinstance(ts, datetime) else str(ts))
    return (
        None if day is None else day.isoformat(),
        ts_text,
        None if row.get("event_time_et") in (None, "") else str(row.get("event_time_et")),
        row.get("event_type"),
        row.get("event_name"),
        row.get("symbol"),
        row.get("status"),
        row.get("time_basis"),
        row.get("source"),
        row.get("source_url"),
        row.get("details_json"),
    )


def _subject_for_path(path):
    text = str(path)
    if text.endswith("combined-event-calendar.parquet"):
        return "combined"
    if text.endswith("economic-releases.parquet"):
        return "economic"
    if text.endswith("fomc-meetings.parquet"):
        return "fomc"
    if text.endswith("market-calendar.parquet"):
        return "market"
    if text.endswith("mega-cap-earnings.parquet"):
        return "earnings"
    if text.endswith("calendar_fomc.csv"):
        return "fomc_alternative"
    if text.endswith("calendar_boj.csv"):
        return "boj"
    if text.endswith("bls_release_dates.csv"):
        return "bls"
    if text.endswith("MANIFEST.tsv"):
        return "bls_manifest"
    if text.endswith(".htm"):
        return "bls_html"
    raise ContractError(f"unrecognized admitted event source path: {path}")


def _base_event(*, subject, source_path, source_sha256, physical_row, event_type, event_date,
                event_name, time_basis, status, symbol=None, event_time_et=None, event_ts_utc_ns=None,
                source=None, source_url=None, details=None, raw_details=None, independent_support=True,
                role="observed_source_row", unparsed=False, snapshot_date=None,
                explicit_published_at_ns=None):
    day = _as_date(event_date)
    eligibility = publication_eligibility(
        event_date=day, event_ts_utc_ns=event_ts_utc_ns, time_basis=time_basis,
        explicit_published_at_ns=explicit_published_at_ns, snapshot_date=snapshot_date,
    )
    primary = day is not None and POPULATION_START <= day < POPULATION_END
    exclusion = None
    if day is None:
        exclusion = "unparsed_or_missing_date"
    elif day < POPULATION_START:
        exclusion = "older_than_primary_population"
    elif day >= POPULATION_END:
        exclusion = "on_or_after_primary_end"
    return {
        "semantic_id": None if day is None else _semantic_id(
            event_type, day, symbol=symbol, time_basis=time_basis, event_time_et=event_time_et),
        "alias_group": None if day is None else _alias_group(event_type, day, symbol=symbol),
        "subject": subject,
        "role": role,
        "independent_support": bool(independent_support) and not unparsed,
        "source_path": source_path,
        "source_sha256": source_sha256,
        "physical_row": physical_row,
        "event_type": event_type,
        "event_name": event_name,
        "event_date": None if day is None else day.isoformat(),
        "event_time_et": event_time_et,
        "event_ts_utc_ns": event_ts_utc_ns,
        "symbol": symbol,
        "status": status,
        "time_basis": time_basis,
        "source": source,
        "source_url": source_url,
        "details": {} if details is None else dict(details),
        "raw_details": raw_details,
        "unparsed": bool(unparsed),
        "snapshot_date": None if snapshot_date is None else _iso_date(snapshot_date),
        "primary_population": primary,
        "exclusion": exclusion,
        "known_at_ns": eligibility["known_at_ns"],
        "causal_feature_eligible": eligibility["causal_feature_eligible"],
        "availability_reason": eligibility["availability_reason"],
        "publication_after_event": eligibility["publication_after_event"],
        "time_precision": eligibility["time_precision"],
        "intraday_functions_defined": eligibility["intraday_functions_defined"],
        "occurrence_basis": "source_labels_occurred" if status in ("actual", "held") else "schedule_or_occurrence_unconfirmed",
        "source_labels_occurred": status in ("actual", "held"),
        "event_labels_retrospective": True,
        "surprise_as_known": False,
        "revision_as_known": False,
    }


def _compile_normalized(subject, source_path, source_sha256, rows, *, role="observed_source_row",
                        independent_support=True):
    events = []
    for index, original in enumerate(rows):
        row = _copy_row(original)
        day = _as_date(row.get("event_date"))
        time_basis = row.get("time_basis")
        ts_ns = _as_utc_ns(row.get("event_ts_utc"))
        if time_basis == "date_only":
            ts_ns = None
            if row.get("event_time_et") not in (None, ""):
                raise ContractError("date_only rows cannot carry an invented or residual wall time")
        elif time_basis == "standard_release_time" and ts_ns is None and row.get("event_time_et"):
            ts_ns = local_timestamp(day, _wall_time(row["event_time_et"]), NY_ZONE)
        details = _details(row.get("details_json"))
        events.append(_base_event(
            subject=subject, source_path=source_path, source_sha256=source_sha256,
            physical_row=index, event_type=row.get("event_type"), event_date=day,
            event_name=row.get("event_name"), time_basis=time_basis, status=row.get("status"),
            symbol=row.get("symbol"), event_time_et=None if row.get("event_time_et") in (None, "") else str(row.get("event_time_et")),
            event_ts_utc_ns=ts_ns, source=row.get("source"), source_url=row.get("source_url"),
            details=details, raw_details=row.get("details_json"),
            independent_support=independent_support, role=role,
        ))
    return events


def _compile_fomc_alternative(source_path, source_sha256, rows):
    events = []
    for index, original in enumerate(rows):
        parsed = parse_fomc_csv_row(original)
        events.append(_base_event(
            subject="fomc_alternative", source_path=source_path, source_sha256=source_sha256,
            physical_row=index, event_type="fomc", event_date=parsed["decision_date"],
            event_name="FOMC alternative calendar decision date", time_basis="date_only",
            status="alternative_calendar_row", event_time_et=None, event_ts_utc_ns=None,
            source="alternative FOMC CSV", source_url=None,
            details={"raw_range": parsed["raw_range"], "range_start": _iso_date(parsed["range_start"]),
                     "range_end": _iso_date(parsed["range_end"]), "unparsed": parsed["unparsed"],
                     "parse_reason": parsed["reason"]},
            raw_details=json.dumps(_json_safe(original), sort_keys=True),
            independent_support=parsed["parsed"], role="alternative_source_row",
            unparsed=parsed["unparsed"],
        ))
    return events


def _compile_boj(source_path, source_sha256, rows):
    events = []
    for index, original in enumerate(rows):
        row = _copy_row(original)
        day = _as_date(row.get("mpm_date"))
        events.append(_base_event(
            subject="boj", source_path=source_path, source_sha256=source_sha256,
            physical_row=index, event_type="boj_mpm", event_date=day,
            event_name="BOJ monetary policy meeting", time_basis="date_only",
            status="alternative_calendar_row", source="alternative BOJ CSV",
            details={"mpm_date": row.get("mpm_date")}, raw_details=json.dumps(_json_safe(row), sort_keys=True),
            independent_support=day is not None, role="alternative_source_row",
        ))
    return events


def _compile_bls(source_path, source_sha256, rows):
    events = []
    for index, original in enumerate(rows):
        row = _copy_row(original)
        day = _as_date(row.get("date"))
        event_type = bls_release_type(row.get("release_name"))
        wall = row.get("time_et")
        ts_ns = bls_timestamp(day, wall) if day is not None and wall not in (None, "") else None
        snapshot = _as_date(row.get("wayback_snapshot_date"))
        events.append(_base_event(
            subject="bls", source_path=source_path, source_sha256=source_sha256,
            physical_row=index, event_type=event_type, event_date=day,
            event_name=row.get("release_name"), time_basis="standard_release_time",
            status=row.get("status"), event_time_et=None if wall in (None, "") else str(wall),
            event_ts_utc_ns=ts_ns, source="BLS release calendar CSV",
            details={"reference_month": row.get("reference_month"),
                     "wayback_snapshot_date": row.get("wayback_snapshot_date"),
                     "release_name": row.get("release_name"),
                     "snapshot_is_not_pre_event_publication": bool(snapshot is not None and day is not None and snapshot > day)},
            raw_details=json.dumps(_json_safe(row), sort_keys=True),
            independent_support=True, role="alternative_source_row", snapshot_date=snapshot,
        ))
    return events


def _compare_pairs(left, right, *, left_name, right_name, key):
    left_map = defaultdict(list)
    right_map = defaultdict(list)
    for event in left:
        left_map[key(event)].append(event)
    for event in right:
        right_map[key(event)].append(event)
    keys = sorted(set(left_map) | set(right_map), key=lambda item: tuple("" if part is None else str(part) for part in item))
    equal_aliases = 0
    disagreements = 0
    left_only = 0
    right_only = 0
    rows = []
    for item in keys:
        left_rows = left_map.get(item, [])
        right_rows = right_map.get(item, [])
        if left_rows and right_rows:
            for left_event, right_event in zip(left_rows, right_rows):
                same_time = (left_event.get("event_ts_utc_ns") is not None and
                             left_event.get("event_ts_utc_ns") == right_event.get("event_ts_utc_ns")) or (
                    left_event.get("time_basis") == "date_only" and right_event.get("time_basis") == "date_only")
                same_date = left_event.get("event_date") == right_event.get("event_date")
                relation = "equal_alias" if same_date and same_time else "disagreement"
                if relation == "equal_alias":
                    equal_aliases += 1
                else:
                    disagreements += 1
                rows.append({
                    "relation": relation, "key": [None if part is None else str(part) for part in item],
                    left_name: {"semantic_id": left_event.get("semantic_id"), "event_date": left_event.get("event_date"),
                                "event_time_et": left_event.get("event_time_et"), "physical_row": left_event.get("physical_row")},
                    right_name: {"semantic_id": right_event.get("semantic_id"), "event_date": right_event.get("event_date"),
                                 "event_time_et": right_event.get("event_time_et"), "physical_row": right_event.get("physical_row")},
                })
            extra_left = len(left_rows) - min(len(left_rows), len(right_rows))
            extra_right = len(right_rows) - min(len(left_rows), len(right_rows))
            left_only += extra_left
            right_only += extra_right
            for event in left_rows[min(len(left_rows), len(right_rows)):]:
                rows.append({"relation": f"{left_name}_only", "key": [None if part is None else str(part) for part in item],
                             left_name: {"semantic_id": event.get("semantic_id"), "physical_row": event.get("physical_row")}})
            for event in right_rows[min(len(left_rows), len(right_rows)):]:
                rows.append({"relation": f"{right_name}_only", "key": [None if part is None else str(part) for part in item],
                             right_name: {"semantic_id": event.get("semantic_id"), "physical_row": event.get("physical_row")}})
        elif left_rows:
            left_only += len(left_rows)
            for event in left_rows:
                rows.append({"relation": f"{left_name}_only", "key": [None if part is None else str(part) for part in item],
                             left_name: {"semantic_id": event.get("semantic_id"), "physical_row": event.get("physical_row")}})
        else:
            right_only += len(right_rows)
            for event in right_rows:
                rows.append({"relation": f"{right_name}_only", "key": [None if part is None else str(part) for part in item],
                             right_name: {"semantic_id": event.get("semantic_id"), "physical_row": event.get("physical_row")}})
    return {
        "left": left_name, "right": right_name,
        "equal_aliases": equal_aliases, "disagreements": disagreements,
        "left_only": left_only, "right_only": right_only, "compared_keys": len(keys),
        "rows": rows,
    }


def compile_events(sources, *, population_start=POPULATION_START, population_end=POPULATION_END):
    """Compile admitted source tables into lineage-preserving event rows.

    ``sources`` is a sequence of decoded tables. Input row mappings are copied
    and never mutated. Combined is an alias of the four topical tables only
    after exact row-multiset equality.
    """
    del population_start, population_end
    if not isinstance(sources, (list, tuple)) or not sources:
        raise ContractError("compile_events requires the admitted source tables")
    decoded = []
    for source in sources:
        if not isinstance(source, dict):
            raise ContractError("each compile_events source must be a mapping")
        rows = source.get("rows")
        if rows is not None and not isinstance(rows, (list, tuple)):
            raise ContractError("decoded source rows must be a sequence")
        decoded.append({
            "subject": source.get("subject") or _subject_for_path(source["path"]),
            "path": source["path"],
            "sha256": source["sha256"],
            "format": source.get("format"),
            "rows": tuple(_copy_row(row) for row in (rows or ())),
            "note": source.get("note"),
            "provenance_only": bool(source.get("provenance_only")),
        })
    by_subject = {item["subject"]: item for item in decoded}
    missing = [name for name in (*TOPICAL_SUBJECTS, "combined") if name not in by_subject]
    if missing:
        raise ContractError(f"compile_events requires all topical subjects and combined: {missing}")
    topical_events = []
    identity_by_subject = {}
    for subject in TOPICAL_SUBJECTS:
        item = by_subject[subject]
        compiled = _compile_normalized(subject, item["path"], item["sha256"], item["rows"])
        topical_events.extend(compiled)
        identity_by_subject[subject] = Counter(_normalized_identity(row) for row in item["rows"])
    combined_identities = Counter(_normalized_identity(row) for row in by_subject["combined"]["rows"])
    topical_identities = Counter()
    for subject in TOPICAL_SUBJECTS:
        topical_identities.update(identity_by_subject[subject])
    combined_is_alias = combined_identities == topical_identities
    expected_combined = sum(len(by_subject[subject]["rows"]) for subject in TOPICAL_SUBJECTS)
    if combined_is_alias:
        combined_events = _compile_normalized(
            "combined", by_subject["combined"]["path"], by_subject["combined"]["sha256"],
            by_subject["combined"]["rows"], role="combined_alias", independent_support=False)
    else:
        combined_events = _compile_normalized(
            "combined", by_subject["combined"]["path"], by_subject["combined"]["sha256"],
            by_subject["combined"]["rows"], role="combined_unverified_not_independent_support",
            independent_support=False)
    alternatives = []
    provenance = []
    for item in decoded:
        if item["subject"] == "fomc_alternative":
            alternatives.extend(_compile_fomc_alternative(item["path"], item["sha256"], item["rows"]))
        elif item["subject"] == "boj":
            alternatives.extend(_compile_boj(item["path"], item["sha256"], item["rows"]))
        elif item["subject"] == "bls":
            alternatives.extend(_compile_bls(item["path"], item["sha256"], item["rows"]))
        elif item["subject"] in ("bls_html", "bls_manifest"):
            provenance.append({
                "subject": item["subject"], "path": item["path"], "sha256": item["sha256"],
                "rows": len(item["rows"]) if item["rows"] else None,
                "parsed_as_numerical_source": False,
                "note": item.get("note") or "Retained hashed provenance; HTML tables are not parsed.",
            })
    events = topical_events + combined_events + alternatives
    groups = defaultdict(list)
    for event in events:
        if event["alias_group"]:
            groups[event["alias_group"]].append((event["source_sha256"], event["physical_row"]))
    for event in events:
        members = tuple(sorted(set(groups.get(event["alias_group"]) or ())))
        event["alias_group_size"] = len(members)
        event["duplicated_alias"] = len(members) > 1
    economic = [event for event in topical_events if event["subject"] == "economic"]
    fomc = [event for event in topical_events if event["subject"] == "fomc"]
    bls = [event for event in alternatives if event["subject"] == "bls"]
    fomc_alt = [event for event in alternatives if event["subject"] == "fomc_alternative" and not event["unparsed"]]
    agreements = {
        "economic_vs_bls": _compare_pairs(
            economic, bls, left_name="economic", right_name="bls",
            key=lambda event: (event["event_type"], event["event_date"])),
        "fomc_vs_alternative": _compare_pairs(
            fomc, fomc_alt, left_name="fomc", right_name="fomc_alternative",
            key=lambda event: (event["event_type"], event["event_date"])),
    }
    return {
        "version": VERSION,
        "events": events,
        "topical_events": topical_events,
        "combined_events": combined_events,
        "alternative_events": alternatives,
        "provenance": provenance,
        "combined_is_alias": combined_is_alias,
        "combined_row_count": len(by_subject["combined"]["rows"]),
        "topical_row_count": expected_combined,
        "combined_multiset_equal": combined_is_alias,
        "agreements": agreements,
        "sources": tuple({"subject": item["subject"], "path": item["path"], "sha256": item["sha256"],
                          "rows": len(item["rows"])} for item in decoded),
    }


def _half_open_contains(start_ns, end_ns, at_ns):
    timestamp(start_ns)
    timestamp(end_ns)
    if end_ns <= start_ns:
        raise ContractError("window interval must be positive half-open")
    return start_ns <= timestamp(at_ns) < end_ns


def _proximity(point_ns, event_ns, horizon_ns):
    if point_ns is None or event_ns is None:
        return False
    return abs(timestamp(event_ns) - timestamp(point_ns)) <= timestamp(horizon_ns)


def date_record_state(events_on_date, *, coverage_complete=False):
    observed = tuple(event for event in events_on_date if event.get("event_date"))
    if observed:
        return {
            "record_state": "observed",
            "coverage_state": "observed_source_rows",
            "ordinary_or_no_event_label": None,
        }
    if coverage_complete:
        return {
            "record_state": "no_record_on_date",
            "coverage_state": "source_year_complete",
            "ordinary_or_no_event_label": None,
        }
    return {
        "record_state": "no_record_on_date",
        "coverage_state": "coverage_unknown",
        "ordinary_or_no_event_label": None,
    }


def link_window(window, events, *, horizons_minutes=HORIZONS_MINUTES, coverage_complete=False):
    """Link compiled events to one half-open window.

    Date-only events set event-day flags and do not invent an intraday clock.
    Timed overlap uses ``start <= event < end``. Feature ``available_at`` is
    not the target end. Event labels stay retrospective and non-causal unless
    the compiled row already carries explicit pre-event publication.
    """
    if not isinstance(window, dict):
        raise ContractError("link_window requires a window mapping")
    start_ns = timestamp(window["start_ns"])
    end_ns = timestamp(window["end_ns"])
    available_at_ns = None if window.get("available_at_ns") is None else timestamp(window["available_at_ns"])
    window_date = _iso_date(window.get("date") or window.get("trading_date"))
    if end_ns <= start_ns:
        raise ContractError("link_window requires a positive half-open interval")
    if not isinstance(horizons_minutes, (list, tuple)) or tuple(horizons_minutes) != HORIZONS_MINUTES:
        raise ContractError("proximity horizons must remain (1, 5, 15, 60) minutes")
    day_events = []
    for event in events:
        if not isinstance(event, dict):
            raise ContractError("link_window events must be compiled mappings")
        if event.get("event_date") == window_date:
            day_events.append(event)
    record = date_record_state(day_events, coverage_complete=coverage_complete)
    types = tuple(sorted({event["event_type"] for event in day_events if event.get("event_type")}))
    date_only = any(event.get("time_basis") == "date_only" for event in day_events)
    timed = [event for event in events if event.get("intraday_functions_defined") and event.get("event_ts_utc_ns") is not None]
    overlap = []
    proximity = {int(minutes): {"start": [], "end": [], "available_at": []} for minutes in horizons_minutes}
    for event in timed:
        at = event["event_ts_utc_ns"]
        if _half_open_contains(start_ns, end_ns, at):
            overlap.append(event["semantic_id"])
        for minutes in horizons_minutes:
            horizon = int(minutes) * MINUTE
            if _proximity(start_ns, at, horizon):
                proximity[int(minutes)]["start"].append(event["semantic_id"])
            if _proximity(end_ns, at, horizon):
                proximity[int(minutes)]["end"].append(event["semantic_id"])
            if available_at_ns is not None and _proximity(available_at_ns, at, horizon):
                proximity[int(minutes)]["available_at"].append(event["semantic_id"])
    return {
        "date": window_date,
        "start_ns": start_ns,
        "end_ns": end_ns,
        "available_at_ns": available_at_ns,
        "feature_known_at_ns": available_at_ns,
        "target_end_ns": window.get("target_end_ns"),
        "event_day": bool(day_events),
        "event_day_types": types,
        "source_labeled_occurred_types": tuple(sorted({e["event_type"] for e in day_events if e.get("source_labels_occurred")})),
        "unconfirmed_schedule_types": tuple(sorted({e["event_type"] for e in day_events if not e.get("source_labels_occurred")})),
        "date_only_event_day": date_only,
        "timed_event_day": any(event.get("intraday_functions_defined") for event in day_events),
        "interval_overlap_ids": tuple(sorted(set(overlap))),
        "interval_overlap": bool(overlap),
        "proximity": {str(minutes): {name: tuple(sorted(set(ids))) for name, ids in anchors.items()}
                      for minutes, anchors in proximity.items()},
        "record_state": record["record_state"],
        "coverage_state": record["coverage_state"],
        "ordinary_or_no_event_label": None,
        "causal_feature_eligible": False,
        "event_labels_retrospective": True,
    }


def _population_dates(start=POPULATION_START, end=POPULATION_END):
    day = start
    while day < end:
        yield day
        day += timedelta(days=1)


def build_civil_dates(events, *, calendar=None, coverage_complete_years=None, start=POPULATION_START,
                      end=POPULATION_END):
    """One civil-date row from 2020-01-01 inclusive to 2026-09-03 exclusive."""
    complete_years = frozenset(coverage_complete_years or ())
    by_date = defaultdict(list)
    for event in events:
        if event.get("independent_support") and event.get("event_date"):
            by_date[event["event_date"]].append(event)
    rows = []
    for day in _population_dates(start, end):
        key = day.isoformat()
        day_events = by_date.get(key, [])
        cash_state = "missing_calendar"
        cash_reason = "cash_calendar_not_supplied"
        if calendar is not None:
            try:
                cash = calendar.resolve(day, cut=local_timestamp(day, time(0), calendar.zone))
                cash_state = cash.state
                cash_reason = "published_cash_rth_context"
            except DependencyUnavailable:
                cash_state = "missing_calendar"
                cash_reason = "cash_calendar_year_not_published_or_not_known_at_cut"
        record = date_record_state(day_events, coverage_complete=day.year in complete_years)
        rows.append({
            "date": key,
            "weekday": day.weekday(),
            "record_state": record["record_state"],
            "coverage_state": record["coverage_state"],
            "ordinary_or_no_event_label": None,
            "cash_state": cash_state,
            "cash_reason": cash_reason,
            "event_count": len(day_events),
            "event_types": tuple(sorted({event["event_type"] for event in day_events})),
            "event_semantic_ids": tuple(event["semantic_id"] for event in day_events),
            "date_only_event_day": any(event.get("time_basis") == "date_only" for event in day_events),
        })
    return rows


def _exact_counts(events):
    rows = []
    for event in events:
        if not event.get("event_date"):
            continue
        year = int(event["event_date"][:4])
        rows.append((event.get("event_type"), event.get("subject"), event.get("source"),
                     year, event.get("time_basis"), event.get("independent_support"),
                     event.get("primary_population"), event.get("role")))
    counts = Counter(rows)
    unique_dates = defaultdict(set)
    for event in events:
        if event.get("event_date") and event.get("independent_support"):
            unique_dates[(event.get("event_type"), event.get("subject"), int(event["event_date"][:4]),
                          event.get("time_basis"))].add(event["event_date"])
    return {
        "by_type_source_year_time_basis": [
            {"event_type": key[0], "subject": key[1], "source": key[2], "year": key[3],
             "time_basis": key[4], "independent_support": key[5], "primary_population": key[6],
             "role": key[7], "rows": count}
            for key, count in sorted(counts.items(), key=lambda item: (str(item[0]),))
        ],
        "unique_event_dates": [
            {"event_type": key[0], "subject": key[1], "year": key[2], "time_basis": key[3],
             "unique_event_dates": len(values)}
            for key, values in sorted(unique_dates.items(), key=lambda item: (str(item[0]),))
        ],
        "independent_rows": sum(1 for event in events if event.get("independent_support")),
        "alias_or_nonindependent_rows": sum(1 for event in events if not event.get("independent_support")),
        "unparsed_rows": sum(1 for event in events if event.get("unparsed")),
        "duplicated_alias_groups": sum(
            1 for group, members in Counter(event.get("alias_group") for event in events
                                            if event.get("alias_group") and event.get("independent_support")).items()
            if members > 1),
    }


def _gap_days(dates):
    ordered = sorted(dates)
    return [ (ordered[index] - ordered[index - 1]).days for index in range(1, len(ordered)) ]


def _gap_distribution(values):
    counts = Counter(values)
    return {
        "n": len(values),
        "min": None if not values else min(values),
        "max": None if not values else max(values),
        "mean": None if not values else (sum(values) / len(values)),
        "counts": [{"gap_days": key, "rows": counts[key]} for key in sorted(counts)],
    }



def _coverage_span(events):
    dates = sorted({event["event_date"] for event in events if event.get("event_date")})
    return {
        "first_event_date": None if not dates else dates[0],
        "last_event_date": None if not dates else dates[-1],
        "unique_event_dates": len(dates),
        "min_max_span_is_not_completeness": True,
    }


def summarize_population(compiled, civil_dates):
    events = compiled["events"]
    independent = [event for event in events if event.get("independent_support")]
    primary = [event for event in independent if event.get("primary_population")]
    older = sum(1 for event in independent if event.get("exclusion") == "older_than_primary_population")
    future = sum(1 for event in independent if event.get("exclusion") == "on_or_after_primary_end")
    gaps = {}
    for event_type in sorted({event["event_type"] for event in primary if event.get("event_type")}):
        days = sorted({date.fromisoformat(event["event_date"]) for event in primary
                       if event["event_type"] == event_type})
        gaps[event_type] = _gap_distribution(_gap_days(days))
    agreements = compiled["agreements"]
    return {
        "counts": _exact_counts(events),
        "primary_independent_rows": len(primary),
        "primary_unique_semantic_events": len({e["semantic_id"] for e in primary}),
        "row_count_scope": "Physical alternative source rows are not extra independent market events; unique semantic IDs and unique civil dates define support.",
        "older_than_primary": older,
        "on_or_after_primary_end": future,
        "combined_is_alias": compiled["combined_is_alias"],
        "combined_row_count": compiled["combined_row_count"],
        "topical_row_count": compiled["topical_row_count"],
        "temporal_coverage": _coverage_span(primary),
        "interevent_gaps_exact": gaps,
        "source_agreement": {
            name: {key: value for key, value in table.items() if key != "rows"}
            for name, table in agreements.items()
        },
        "source_agreement_rows": {name: table["rows"] for name, table in agreements.items()},
        "event_day_rate_intervals": {"applied": False, "reason": "Exact acquired calendar record frequencies; uncovered days cannot be zero-filled for event-rate inference."},
        "civil_date_summary": {
            "dates": len(civil_dates),
            "observed": sum(1 for row in civil_dates if row["record_state"] == "observed"),
            "no_record_on_date": sum(1 for row in civil_dates if row["record_state"] == "no_record_on_date"),
            "coverage_unknown": sum(1 for row in civil_dates if row["coverage_state"] == "coverage_unknown"),
            "cash_states": dict(Counter(row["cash_state"] for row in civil_dates)),
        },
    }


def resolve_input_refs(packet, protocol, root):
    """Only the exact registered supplementary input contract selects windows."""
    reference = packet.get("configuration", {}).get("window_inputs")
    if not isinstance(reference, dict) or not reference.get("sha256"):
        raise IntegrityError("registered window-input supplement with hash is required")
    _path, _raw, contract, _sha = _retained_execution(root, reference)
    if contract.get("kind") != "scheduled_event_window_inputs_v1":
        raise IntegrityError("window-input supplement kind changed")
    if contract.get("family") != protocol["family"]:
        raise IntegrityError("window-input supplement family changed")
    return {"development_execution": contract["development_execution"],
            "confirmation_execution": contract["confirmation_execution"],
            "cash_calendar": contract["cash_calendar"], "window_inputs": reference,
            "binding": "exact registered hash-bound supplementary window inputs"}


def _retained_execution(root, ref, *, maximum=64 * 1024 ** 2):
    if not isinstance(ref, dict) or "path" not in ref or not ref.get("sha256"):
        raise IntegrityError("execution reference requires an exact path")
    path = Path(ref["path"])
    path = path if path.is_absolute() else (Path(root) / path)
    path = path.resolve()
    root = Path(root).resolve()
    if (not path.is_relative_to(root) or "archive" in path.parts or not path.is_file()
            or path.stat().st_size > maximum):
        raise IntegrityError("bounded retained execution required")
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if ref.get("sha256") and sha != ref["sha256"]:
        raise IntegrityError(f"execution hash changed: {path}")
    if ref.get("size_bytes") is not None and len(raw) != ref["size_bytes"]:
        raise IntegrityError(f"execution size changed: {path}")
    return path, raw, json.loads(raw), sha


def _authenticate_attempt(registry, execution, *, family, modes):
    state = registry.state()
    attempt = state["attempts"].get(execution.get("attempt_id"))
    trial = state["trials"].get(execution.get("trial_id"))
    if (execution.get("success") is not True or execution.get("family") != family
            or execution.get("mode") not in modes
            or attempt is None or trial is None or attempt["status"] != "succeeded"
            or attempt["family"] != family or attempt["trial_id"] != execution["trial_id"]
            or trial["code_hash"] != execution.get("code_snapshot", execution.get("snapshot", {})).get("sha256")
            or not any(item["sha256"] == digest(execution) for item in attempt.get("result_artifacts", []))):
        raise IntegrityError(f"execution is not the authenticated {family} {modes} attempt")
    worker_ref = execution.get("worker") or execution.get("worker_report")
    if not isinstance(worker_ref, dict):
        raise IntegrityError("execution lacks a CAS worker reference")
    return worker_ref, attempt


def load_admission(packet, protocol, root, store):
    predecessor = (packet.get("configuration") or {}).get("predecessor")
    if not isinstance(predecessor, dict):
        raise IntegrityError("measure packet.configuration.predecessor must be the admission execution")
    path, raw, execution, sha = _retained_execution(root, predecessor)
    if execution.get("mode") != "admit" or execution.get("success") is not True:
        raise IntegrityError("predecessor is not a successful admission execution")
    if hashlib.sha256(raw).hexdigest() != predecessor.get("sha256", sha):
        raise IntegrityError("admission execution hash does not match packet.configuration.predecessor")
    from trading_research.operations.trials import TrialRegistry
    registry = TrialRegistry(Path(root) / "evidence/trials")
    worker_ref, attempt = _authenticate_attempt(
        registry, execution, family=protocol["family"], modes=("admit",))
    worker = store_read_json(store, worker_ref)
    if (worker.get("success") is not True or worker.get("attempt_id") != execution["attempt_id"]
            or worker.get("trial_id") != execution["trial_id"] or worker.get("mode") != "admit"):
        raise IntegrityError("admission worker identity does not match its CAS attempt")
    actual_ref = worker.get("actual")
    if not isinstance(actual_ref, dict) or actual_ref.get("kind") != "scheduled_event_admitted_sources_v1":
        raise IntegrityError("admission worker.actual is not scheduled_event_admitted_sources_v1")
    admitted = store_read_json(store, actual_ref)
    if (admitted.get("kind") != "scheduled_event_admitted_sources_v1"
            or admitted.get("all_declared_sources_admitted") is not True
            or admitted.get("source_files") != len(protocol["source_files"])):
        raise IntegrityError("admitted-source metadata does not match the frozen protocol")
    return {
        "execution_path": str(path),
        "execution_sha256": sha,
        "attempt_id": execution["attempt_id"],
        "attempt_status": attempt["status"],
        "worker_ref": {k: worker_ref[k] for k in ("sha256", "size_bytes", "kind")},
        "actual_ref": {k: actual_ref[k] for k in ("sha256", "size_bytes", "kind")},
        "admitted": admitted,
    }


def load_jumbo_workers(packet, protocol, root, store):
    refs = resolve_input_refs(packet, protocol, root)
    from trading_research.operations.trials import TrialRegistry
    registry = TrialRegistry(Path(root) / "evidence/trials")
    workers = []
    for name, ref, modes, phase in (
        ("development", refs["development_execution"], ("develop",), "extract"),
        ("confirmation", refs["confirmation_execution"], ("confirm",), "confirmation"),
    ):
        path, _raw, execution, sha = _retained_execution(root, ref)
        worker_ref, attempt = _authenticate_attempt(registry, execution, family=JUMBO_FAMILY, modes=modes)
        worker = store_read_json(store, worker_ref)
        if (worker.get("phase") != phase or worker.get("success") is not True
                or worker.get("attempt_id") != execution["attempt_id"]
                or worker.get("trial_id") != execution["trial_id"]):
            raise IntegrityError(f"{name} Jumbo worker phase is not {phase}")
        workers.append((name, worker, {"path": str(path), "sha256": sha,
                                       "attempt_id": execution["attempt_id"],
                                       "attempt_status": attempt["status"],
                                       "worker_ref": {k: worker_ref[k] for k in ("sha256", "size_bytes", "kind")}}))
    development = workers[0][1]
    confirmation = workers[1][1]
    authenticate_workers(development, confirmation)
    variants = split_source_variants(development, confirmation)
    return {
        "refs": refs,
        "development": workers[0][2],
        "confirmation": workers[1][2],
        "variants": variants,
    }


class _ReleaseTableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.current, self.cell, self.in_cell = [], None, [], False
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "tr": self.current = []
        if tag.lower() in ("td", "th") and self.current is not None:
            self.cell, self.in_cell = [], True
    def handle_data(self, data):
        if self.in_cell: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag.lower() in ("td", "th") and self.in_cell:
            self.current.append(" ".join(" ".join(self.cell).split()))
            self.in_cell = False
        if tag.lower() == "tr" and self.current is not None:
            self.rows.append(self.current); self.current = None


def parse_bls_html(raw, path, source_sha256):
    """Literal observed Reference Month / Release Date / Release Time triplets."""
    parser = _ReleaseTableParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    event_type = "cpi" if Path(path).name.startswith("cpi_") else "nfp" if Path(path).name.startswith("empsit_") else None
    months = {name[:3].lower(): value for name,value in ENGLISH_MONTHS.items()}
    rows, unparsed = [], []
    for ordinal, cells in enumerate(parser.rows):
        if len(cells) != 3 or not re.fullmatch(r"[A-Za-z]+ \d{4}", cells[0]):
            continue
        match = re.fullmatch(r"([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})", cells[1])
        clock = re.fullmatch(r"(\d{1,2}):(\d{2})\s*([AaPp][Mm])?", cells[2])
        if match is None or clock is None or match.group(1)[:3].lower() not in months:
            unparsed.append({"html_row":ordinal,"cells":cells});continue
        try:
            day = date(int(match.group(3)),months[match.group(1)[:3].lower()],int(match.group(2)))
            hour, minute = int(clock.group(1)), int(clock.group(2))
            if clock.group(3):
                if not 1 <= hour <= 12: raise ValueError("invalid 12h clock")
                hour = hour%12 + (12 if clock.group(3).lower()=="pm" else 0)
            wall = time(hour,minute)
        except ValueError:
            unparsed.append({"html_row":ordinal,"cells":cells});continue
        rows.append({"event_type":event_type,"reference_month":cells[0],"event_date":day.isoformat(),
            "event_time_et":wall.isoformat(),"event_ts_utc_ns":local_timestamp(day,wall,NY_ZONE),
            "source_path":path,"source_sha256":source_sha256,"html_row":ordinal,"raw_cells":cells})
    return {"rows":rows,"unparsed":unparsed,"observed_table_rows":len(parser.rows)}


def compare_bls_csv_html(events, sources):
    html = [row for source in sources for row in source.get("html_release_rows",())]
    by_triplet = defaultdict(list)
    for row in html:
        by_triplet[row["event_type"],row["reference_month"],row["event_ts_utc_ns"]].append(row)
    matched, unmatched = [], []
    for event in events:
        if event["subject"] != "bls": continue
        key = (event["event_type"],event["details"].get("reference_month"),event["event_ts_utc_ns"])
        refs = by_triplet.get(key,())
        row = {"csv_physical_row":event["physical_row"],"csv_source_sha256":event["source_sha256"],
               "reference_month":key[1],"event_date":event["event_date"],"time_et":event["event_time_et"],
               "matching_html_rows":[{k:r[k] for k in ("source_path","source_sha256","html_row")} for r in refs]}
        (matched if refs else unmatched).append(row)
    return {"scope":"Exact CSV reference-month/date/time triplets occur in retained raw BLS tables; no claim of latest-snapshot selection.",
        "csv_rows":len(matched)+len(unmatched),"matched_csv_rows":len(matched),"unmatched_csv_rows":len(unmatched),
        "all_csv_triplets_found":bool(matched) and not unmatched,"raw_html_release_rows":len(html),
        "unparsed_html_rows":[{"source_path":x["path"],"rows":x.get("html_unparsed",[])} for x in sources if x.get("html_unparsed")],
        "matched":matched,"unmatched":unmatched}


def _decode_admitted_sources(store, admitted):
    sources = []
    for record in admitted["sources"]:
        path = record["source"]["path"]
        raw_ref = record["raw"]
        raw = store_read_bytes(store, raw_ref)
        if hashlib.sha256(raw).hexdigest() != raw_ref["sha256"] or len(raw) != raw_ref["size_bytes"]:
            raise IntegrityError(f"admitted raw source bytes changed: {path}")
        subject = _subject_for_path(path)
        item = {"path": path, "sha256": raw_ref["sha256"], "format": record.get("format"),
                "subject": subject, "note": record.get("note"), "rows": []}
        suffix = Path(path).suffix.lower()
        if suffix == ".parquet":
            import pyarrow.parquet as pq
            from pyarrow import BufferReader
            table = pq.read_table(BufferReader(raw))
            if record.get("rows") is not None and table.num_rows != record["rows"]:
                raise IntegrityError(f"admitted parquet row count changed: {path}")
            item["rows"] = table.to_pylist()
        elif suffix in (".csv", ".tsv"):
            text = raw.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text), delimiter="\t" if suffix == ".tsv" else ",")
            item["rows"] = list(reader)
            if record.get("rows") is not None and len(item["rows"]) != record["rows"]:
                raise IntegrityError(f"admitted delimited row count changed: {path}")
        else:
            item["provenance_only"] = True
            item["rows"] = []
            if suffix == ".htm":
                parsed = parse_bls_html(raw,path,raw_ref["sha256"])
                item["html_release_rows"] = parsed["rows"]
                item["html_unparsed"] = parsed["unparsed"]
                item["html_table_rows"] = parsed["observed_table_rows"]
        sources.append(item)
    return sources


def _load_cash_calendar(root, reference):
    if not isinstance(reference, dict) or "path" not in reference:
        raise IntegrityError("cash_calendar path/sha256 reference required")
    path = Path(reference["path"])
    path = path if path.is_absolute() else Path(root) / path
    raw = path.read_bytes()
    if reference.get("sha256") and hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        raise IntegrityError("cash calendar bytes changed")
    if reference.get("size_bytes") is not None and len(raw) != reference["size_bytes"]:
        raise IntegrityError("cash calendar size changed")
    return CashCalendar(path), {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                                "size_bytes": len(raw)}


def _events_by_date(events):
    index = defaultdict(list)
    for event in events:
        if event.get("independent_support") and event.get("event_date"):
            index[event["event_date"]].append(event)
    return index


def _civil_index(civil_dates):
    return {row["date"]: row for row in civil_dates}


def _link_schema():
    import pyarrow as pa
    fields = [
        ("formation_id", pa.string()), ("source_variant", pa.string()), ("root", pa.string()),
        ("year", pa.int64()), ("date", pa.string()), ("clock", pa.string()),
        ("contract_key", pa.string()), ("source_version", pa.string()),
        ("definition", pa.string()), ("window_version", pa.string()),
        ("formation_status", pa.string()), ("source_ids", pa.string()),
        ("event_interval_ids", pa.string()), ("event_source_rows", pa.string()),
        ("formation_start_ns", pa.int64()), ("formation_end_ns", pa.int64()),
        ("available_at_ns", pa.int64()), ("feature_known_at_ns", pa.int64()),
        ("target_end_ns", pa.int64()), ("event_day", pa.bool_()),
        ("date_only_event_day", pa.bool_()), ("timed_event_day", pa.bool_()),
        ("event_day_types", pa.string()), ("interval_overlap", pa.bool_()),
        ("source_labeled_occurred_types", pa.string()), ("unconfirmed_schedule_types", pa.string()),
        ("record_state", pa.string()), ("coverage_state", pa.string()),
        ("ordinary_or_no_event_label", pa.string()),
        ("causal_feature_eligible", pa.bool_()), ("event_labels_retrospective", pa.bool_()),
    ]
    for minutes in HORIZONS_MINUTES:
        for anchor in ("start", "end", "available_at"):
            fields.append((f"prox_{anchor}_{minutes}m", pa.bool_()))
    return pa.schema(fields)


def _link_shard_table(table, *, source_variant, events_by_date, civil_by_date):
    import pyarrow as pa
    n = table.num_rows
    dates = table.column("date").to_pylist()
    clocks = table.column("clock").to_pylist()
    formation_ids = table.column("formation_id").to_pylist()
    roots = table.column("root").to_pylist()
    years = table.column("year").to_pylist()
    contracts = table.column("contract_key").to_pylist()
    source_versions = table.column("source_version").to_pylist()
    definitions = table.column("definition").to_pylist()
    window_versions = table.column("window_version").to_pylist()
    statuses = table.column("status").to_pylist()
    source_ids = table.column("source_ids").to_pylist()
    starts = table.column("formation_start_ns").to_pylist()
    ends = table.column("formation_end_ns").to_pylist()
    available = table.column("available_at_ns").to_pylist()
    columns = {name: [] for name in _link_schema().names}
    day_cache = {}
    for index in range(n):
        day = dates[index]
        if type(day) is not str:
            raise IntegrityError("formation date must remain an ISO civil-date string")
        start_ns, end_ns = starts[index], ends[index]
        # The published formation can span prior civil dates, including the
        # prior session and weekends. Load each covered date once per boundary.
        if start_ns is None or end_ns is None or end_ns <= start_ns:
            raise IntegrityError("intended formation interval missing or invalid")
        low_day = datetime.fromtimestamp((start_ns-60*MINUTE)//1_000_000_000, timezone.utc).astimezone(ZoneInfo(NY_ZONE)).date()
        high_ns = max(end_ns, available[index] or end_ns)+60*MINUTE
        high_day = datetime.fromtimestamp(high_ns//1_000_000_000, timezone.utc).astimezone(ZoneInfo(NY_ZONE)).date()
        cache_key = (day, low_day, high_day)
        if cache_key not in day_cache:
            selected = list(events_by_date.get(day, ()))
            at = low_day
            while at <= high_day:
                if at.isoformat() != day:
                    selected.extend(events_by_date.get(at.isoformat(), ()))
                at += timedelta(days=1)
            day_cache[cache_key] = selected
        selected = day_cache[cache_key]
        linked = link_window(
            {"date": day, "start_ns": int(start_ns), "end_ns": int(end_ns),
             "available_at_ns": None if available[index] is None else int(available[index])},
            selected, coverage_complete=False)
        columns["formation_id"].append(formation_ids[index])
        columns["source_variant"].append(source_variant)
        columns["root"].append(roots[index])
        columns["year"].append(None if years[index] is None else int(years[index]))
        columns["date"].append(day)
        columns["clock"].append(clocks[index])
        columns["contract_key"].append(contracts[index])
        columns["source_version"].append(source_versions[index])
        columns["definition"].append(definitions[index])
        columns["window_version"].append(window_versions[index])
        columns["formation_status"].append(statuses[index])
        columns["source_ids"].append(source_ids[index])
        columns["event_interval_ids"].append("|".join(linked["interval_overlap_ids"]))
        columns["event_source_rows"].append(json.dumps([{k:e.get(k) for k in ("semantic_id","source_sha256","physical_row")} for e in selected], sort_keys=True, separators=(",",":")))
        columns["formation_start_ns"].append(int(starts[index]))
        columns["formation_end_ns"].append(int(ends[index]))
        columns["available_at_ns"].append(None if available[index] is None else int(available[index]))
        columns["feature_known_at_ns"].append(linked["feature_known_at_ns"])
        columns["target_end_ns"].append(linked["target_end_ns"])
        columns["event_day"].append(linked["event_day"])
        columns["date_only_event_day"].append(linked["date_only_event_day"])
        columns["timed_event_day"].append(linked["timed_event_day"])
        columns["event_day_types"].append("|".join(linked["event_day_types"]))
        columns["source_labeled_occurred_types"].append("|".join(linked["source_labeled_occurred_types"]))
        columns["unconfirmed_schedule_types"].append("|".join(linked["unconfirmed_schedule_types"]))
        columns["interval_overlap"].append(linked["interval_overlap"])
        columns["record_state"].append(linked["record_state"])
        columns["coverage_state"].append(linked["coverage_state"])
        columns["ordinary_or_no_event_label"].append(None)
        columns["causal_feature_eligible"].append(False)
        columns["event_labels_retrospective"].append(True)
        for minutes in HORIZONS_MINUTES:
            prox = linked["proximity"][str(minutes)]
            columns[f"prox_start_{minutes}m"].append(bool(prox["start"]))
            columns[f"prox_end_{minutes}m"].append(bool(prox["end"]))
            columns[f"prox_available_at_{minutes}m"].append(bool(prox["available_at"]))
    return pa.table(columns, schema=_link_schema())


def link_formations(store, variants, events, civil_dates, outputs):
    events_by_date = _events_by_date(events)
    civil_by_date = _civil_index(civil_dates)
    series = ParquetSeries(outputs, "formation-window-links", encoding="plain")
    totals = []
    conserved = 0
    try:
        for source_variant, shards in variants:
            for shard in shards:
                table = _read_columns(store, shard["tables"]["formations"], list(FORMATION_LINK_COLUMNS))
                expected = int(shard["tables"]["formations"]["rows"])
                if table.num_rows != expected:
                    raise IntegrityError("formation shard lost rows before linking")
                linked = _link_shard_table(
                    table, source_variant=source_variant, events_by_date=events_by_date,
                    civil_by_date=civil_by_date)
                if linked.num_rows != expected:
                    raise IntegrityError("formation link row count does not conserve the shard")
                series.append(linked)
                conserved += linked.num_rows
                totals.append({
                    "source_variant": source_variant, "root": shard["root"], "year": int(shard["year"]),
                    "formation_rows": expected, "linked_rows": linked.num_rows,
                    "source_supersession": bool(shard.get("source_supersession")),
                })
                del table, linked
    except BaseException:
        series.abort()
        raise
    published = series.finish()
    if published["rows"] != conserved:
        raise IntegrityError("formation-link series does not conserve all shard rows")
    return {"series": published, "shards": totals, "formation_rows": conserved}


def _event_table(events):
    import pyarrow as pa
    columns = {
        "semantic_id": [], "alias_group": [], "subject": [], "role": [],
        "independent_support": [], "source_path": [], "source_sha256": [],
        "physical_row": [], "event_type": [], "event_name": [], "event_date": [],
        "event_time_et": [], "event_ts_utc_ns": [], "symbol": [], "status": [],
        "time_basis": [], "source": [], "source_url": [], "raw_details": [],
        "unparsed": [], "snapshot_date": [], "primary_population": [], "exclusion": [],
        "known_at_ns": [], "causal_feature_eligible": [], "availability_reason": [],
        "publication_after_event": [], "time_precision": [], "intraday_functions_defined": [],
        "event_labels_retrospective": [], "surprise_as_known": [], "revision_as_known": [],
        "alias_group_size": [], "duplicated_alias": [],
        "occurrence_basis": [], "source_labels_occurred": [],
    }
    for event in events:
        for name in columns:
            columns[name].append(event.get(name))
    boolean = {"source_labels_occurred","independent_support","unparsed","primary_population","causal_feature_eligible","publication_after_event","intraday_functions_defined","event_labels_retrospective","surprise_as_known","revision_as_known","duplicated_alias"}
    integers = {"physical_row","event_ts_utc_ns","known_at_ns","alias_group_size"}
    schema = pa.schema([(name,pa.bool_() if name in boolean else pa.int64() if name in integers else pa.string()) for name in columns])
    return pa.table(columns, schema=schema)


def _civil_table(rows):
    import pyarrow as pa
    return pa.table({
        "date": [row["date"] for row in rows],
        "weekday": [row["weekday"] for row in rows],
        "record_state": [row["record_state"] for row in rows],
        "coverage_state": [row["coverage_state"] for row in rows],
        "ordinary_or_no_event_label": pa.array([row["ordinary_or_no_event_label"] for row in rows], type=pa.string()),
        "cash_state": [row["cash_state"] for row in rows],
        "cash_reason": [row["cash_reason"] for row in rows],
        "event_count": [row["event_count"] for row in rows],
        "event_types": ["|".join(row["event_types"]) for row in rows],
        "event_semantic_ids": ["|".join(row["event_semantic_ids"]) for row in rows],
        "date_only_event_day": [row["date_only_event_day"] for row in rows],
    })


def _write_parquet(outputs, name, table, *, kind):
    import pyarrow.parquet as pq
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression="zstd", compression_level=3)
    payload = buffer.getvalue()
    with outputs.create(name) as stream:
        stream.write(payload)
    ref = outputs.reference(name, kind=kind)
    stored = pq.read_table(ref["path"])
    if not stored.equals(table, check_metadata=True):
        raise IntegrityError(f"{name} failed parquet population round trip")
    return {**ref, "rows": table.num_rows, "roundtrip_exact": True}


def _own_test_suite():
    path = Path(__file__).resolve().parents[3] / "tests" / "test_scheduled_event_measurements.py"
    if not path.is_file():
        raise IntegrityError(f"own unit-test file is missing: {path}")
    spec = importlib.util.spec_from_file_location("test_scheduled_event_measurements", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def run_own_unit_tests():
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(_own_test_suite())
    report = {
        "tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "passed": result.wasSuccessful(),
        "output": stream.getvalue(),
    }
    if not result.wasSuccessful():
        raise IntegrityError(
            "scheduled-event unit tests failed; stop without population or retry: "
            + stream.getvalue())
    return report


def _write_report(outputs, *, admission, compiled, summary, links, tests, refs):
    lines = [
        "# Scheduled-event calendar measurement",
        "",
        "Retrospective acquired-calendar labels and Jumbo formation-window links. event_day means a retained calendar record, not independently confirmed occurrence. scheduled_at_capture rows remain unconfirmed, including disrupted/cancelled releases.",
        "This is not Context and does not establish historical predictive calendar availability.",
        "",
        f"- admission_attempt: {admission['attempt_id']}",
        f"- admission_execution_sha256: {admission['execution_sha256']}",
        f"- admitted_sources: {compiled['sources']}",
        f"- combined_is_alias: {compiled['combined_is_alias']}",
        f"- combined_rows: {compiled['combined_row_count']}",
        f"- topical_rows: {compiled['topical_row_count']}",
        f"- noncombined source rows: {summary['counts']['independent_rows']}",
        f"- primary source rows: {summary['primary_independent_rows']}; unique semantic events: {summary['primary_unique_semantic_events']}",
        f"- older_than_primary: {summary['older_than_primary']}",
        f"- on_or_after_primary_end: {summary['on_or_after_primary_end']}",
        f"- unparsed_rows: {summary['counts']['unparsed_rows']}",
        f"- civil_dates: {summary['civil_date_summary']}",
        f"- economic_vs_bls: {summary['source_agreement']['economic_vs_bls']}",
        f"- fomc_vs_alternative: {summary['source_agreement']['fomc_vs_alternative']}",
        f"- formation_rows: {links['formation_rows']}",
        f"- formation_shards: {links['shards']}",
        f"- BLS raw-HTML triplet matches: {summary['raw_html_comparison']['matched_csv_rows']}/{summary['raw_html_comparison']['csv_rows']}; unmatched retained in population-counts.json",
        f"- unit_tests_passed: {tests['passed']} ({tests['tests']} tests)",
        f"- jumbo_binding: {refs['binding']}",
        f"- full_family_complete: False",
        "",
        "## Unavailable questions",
        "",
    ]
    for item in UNAVAILABLE_QUESTIONS:
        lines.append(f"- {item['id']}: {item['reason']}")
    lines.extend(["", "## Inter-event gaps (exact population counts)", ""])
    for event_type, gap in summary["interevent_gaps_exact"].items():
        lines.append(f"- {event_type}: n={gap['n']} min={gap['min']} max={gap['max']} mean={gap['mean']}")
    lines.extend(["", "## Record counts by source, type, year and clock basis", "", "| Source | Type | Year | Time basis | Rows |", "|---|---|---:|---|---:|"])
    for item in summary["counts"]["by_type_source_year_time_basis"]:
        if item["primary_population"]:
            lines.append(f"| {item['subject']} | {item['event_type']} | {item['year']} | {item['time_basis']} | {item['rows']} |")
    lines.extend(["", "Source row counts are retained alternatives. Equal schedules never add independent market-event or date support.", "Missing calendar coverage prevents ordinary-day or true event-frequency inference."])
    payload = ("\n".join(lines) + "\n").encode()
    with outputs.create("scheduled-event-report.md") as stream:
        stream.write(payload)
    return outputs.reference("scheduled-event-report.md", kind="scheduled_event_calendar_report_v1")


def run(*, packet, protocol, root, store):
    """Registered measurement entry. Runs this module's unit tests first."""
    if not isinstance(packet, dict) or not isinstance(protocol, dict):
        raise ContractError("run requires packet and protocol mappings")
    tests = run_own_unit_tests()
    admission = load_admission(packet, protocol, root, store)
    sources = _decode_admitted_sources(store, admission["admitted"])
    compiled = compile_events(sources)
    html_comparison = compare_bls_csv_html(compiled["events"],sources)
    refs = resolve_input_refs(packet, protocol, root)
    calendar, calendar_ref = _load_cash_calendar(root, refs["cash_calendar"] or protocol.get("cash_calendar"))
    civil_dates = build_civil_dates(compiled["events"], calendar=calendar)
    summary = summarize_population(compiled, civil_dates)
    summary["raw_html_comparison"] = html_comparison
    jumbo = load_jumbo_workers(packet, protocol, root, store)
    run_folder = Path(root) / "reports" / "scheduled-event-runs" / packet["attempt_id"]
    outputs = BoundedOutputs(
        run_folder / "outputs",
        maximum_total_bytes=128 * 1024 ** 2 - 8 * 1024 ** 2,
        maximum_file_bytes=64 * 1024 ** 2,
    )
    event_ref = _write_parquet(outputs, "observed-source-events.parquet", _event_table(compiled["events"]),
                               kind="scheduled_event_observed_rows_v1")
    civil_ref = _write_parquet(outputs, "civil-calendar-dates.parquet", _civil_table(civil_dates),
                               kind="scheduled_event_civil_dates_v1")
    counts_ref = outputs.json("population-counts.json", _json_safe({
        "raw_html_comparison": html_comparison,
        "counts": summary["counts"],
        "primary_independent_rows": summary["primary_independent_rows"],
        "older_than_primary": summary["older_than_primary"],
        "on_or_after_primary_end": summary["on_or_after_primary_end"],
        "combined_is_alias": summary["combined_is_alias"],
        "combined_row_count": summary["combined_row_count"],
        "topical_row_count": summary["topical_row_count"],
        "temporal_coverage": summary["temporal_coverage"],
        "interevent_gaps_exact": summary["interevent_gaps_exact"],
        "source_agreement": summary["source_agreement"],
        "source_agreement_rows": summary["source_agreement_rows"],
        "event_day_rate_intervals": summary["event_day_rate_intervals"],
        "civil_date_summary": summary["civil_date_summary"],
        "provenance": compiled["provenance"],
    }), kind="scheduled_event_population_counts_v1")
    links = link_formations(store, jumbo["variants"], compiled["events"], civil_dates, outputs)
    report_ref = _write_report(outputs, admission=admission, compiled=compiled, summary=summary,
                               links=links, tests=tests, refs=jumbo["refs"])
    return {
        "kind": "scheduled_event_measurement_results_v1",
        "version": VERSION,
        "success": True,
        "output_bytes": outputs.written,
        "full_family_complete": False,
        "family_statistics_complete": False,
        "context_models_complete": False,
        "model_fits": 0,
        "tests": {key: tests[key] for key in ("tests", "failures", "errors", "skipped", "passed")},
        "admission": {key: admission[key] for key in (
            "execution_path", "execution_sha256", "attempt_id", "attempt_status",
            "worker_ref", "actual_ref")},
        "jumbo": {"development": jumbo["development"], "confirmation": jumbo["confirmation"],
                  "refs": jumbo["refs"]},
        "cash_calendar": calendar_ref,
        "raw_html_comparison": {k:html_comparison[k] for k in ("csv_rows","matched_csv_rows","unmatched_csv_rows","all_csv_triplets_found","raw_html_release_rows")},
        "combined_is_alias": compiled["combined_is_alias"],
        "combined_row_count": compiled["combined_row_count"],
        "topical_row_count": compiled["topical_row_count"],
        "independent_rows": summary["counts"]["independent_rows"],
        "primary_independent_rows": summary["primary_independent_rows"],
        "older_than_primary": summary["older_than_primary"],
        "on_or_after_primary_end": summary["on_or_after_primary_end"],
        "civil_date_summary": summary["civil_date_summary"],
        "source_agreement": summary["source_agreement"],
        "formation_rows": links["formation_rows"],
        "formation_shards": links["shards"],
        "refs": {
            "observed_events": event_ref,
            "civil_dates": civil_ref,
            "population_counts": counts_ref,
            "formation_links": links["series"],
            "report": report_ref,
        },
        "unavailable_questions": list(UNAVAILABLE_QUESTIONS),
        "scope": "Retrospective acquired-event calendar measurement and Jumbo formation-window links for C17/C17.PRE_POST_EVENT/X01.ASYNC. Not Context. Not a historical predictive calendar.",
    }
