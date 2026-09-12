"""Append-only FRED/ALFRED acquisition; civil vintage dates are never event clocks."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import tempfile
import time
from typing import Callable
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo


FRED_BASE = "https://api.stlouisfed.org/fred/"
BANKED_SERIES = (
    "DEXJPUS", "DFF", "DGS1", "DGS1MO", "DGS3MO", "DGS6MO", "DGS10",
    "DTB3", "DTWEXAFEGS", "EFFR", "GVZCLS", "RVXCLS", "SOFR", "T10YIE",
    "VIXCLS", "VXDCLS", "VXNCLS", "VXVCLS",
)
BLS_SERIES = {"CPIAUCSL": (10, "cpi"), "PAYEMS": (50, "empsit")}
DEFAULT_SERIES = tuple(BLS_SERIES) + BANKED_SERIES


class AcquisitionError(RuntimeError):
    """Messages contain fixed diagnostics, never authenticated request URLs."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def new_output(parent: Path, data_root: Path, prefix: str) -> Path:
    parent, data_root = parent.resolve(), data_root.resolve()
    if parent == data_root or parent.is_relative_to(data_root):
        raise ValueError("Output must be outside the read-only data root")
    parent.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=parent))


def write_json(path: Path, value: object) -> dict:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")
    return {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}


class FredClient:
    def __init__(self, key: str, *, opener=urllib.request.urlopen, sleep=time.sleep):
        if not re.fullmatch(r"[a-z0-9]{32}", key):
            raise ValueError("Invalid FRED API key format")
        self._key, self._opener, self._sleep = key, opener, sleep
        self.requests = 0

    def get(self, endpoint: str, parameters: dict) -> dict:
        if endpoint not in {"series", "series/observations", "series/vintagedates"}:
            raise ValueError("Unsupported FRED endpoint")
        params = {**parameters, "file_type": "json", "api_key": self._key}
        request = urllib.request.Request(
            FRED_BASE + endpoint + "?" + urllib.parse.urlencode(params),
            headers={"User-Agent": "trading-research-macro-backfill/1.0"},
        )
        for attempt in range(5):
            self._sleep(0.55 if attempt == 0 else min(2 ** attempt, 16))
            self.requests += 1
            try:
                with self._opener(request, timeout=30) as response:
                    body = response.read()
            except urllib.error.HTTPError as exc:
                status = exc.code
                exc.close()
                if status in {429, 500, 502, 503, 504} and attempt < 4:
                    continue
                raise AcquisitionError(f"FRED HTTP status {status}") from None
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt < 4:
                    continue
                raise AcquisitionError("FRED network request failed after retries") from None
            if self._key.encode() in body:
                raise AcquisitionError("Refusing to retain a response containing credentials")
            try:
                payload = json.loads(body)
            except (ValueError, UnicodeError):
                raise AcquisitionError("FRED returned invalid JSON") from None
            if not isinstance(payload, dict) or "error_code" in payload:
                raise AcquisitionError("FRED returned an API error")
            return payload
        raise AcquisitionError("FRED retry budget exhausted")


def fetch_pages(client: FredClient, endpoint: str, params: dict, row_key: str,
                directory: Path, label: str, *, page_limit: int = 100000) -> tuple[list, list]:
    """Check counts and offsets on every page; reject truncation or moving totals."""
    rows, artifacts = [], []
    total = None
    while total is None or len(rows) < total:
        request_params = {**params, "limit": page_limit, "offset": len(rows)}
        payload = client.get(endpoint, request_params)
        page = payload.get(row_key)
        if not isinstance(page, list) or type(payload.get("count")) is not int:
            raise AcquisitionError("FRED pagination metadata or rows missing")
        if payload.get("offset") != len(rows):
            raise AcquisitionError("FRED pagination offset mismatch")
        if total is None:
            total = payload["count"]
        if total < 0 or payload["count"] != total:
            raise AcquisitionError("FRED result count changed while paging")
        if len(rows) + len(page) > total or (not page and len(rows) < total):
            raise AcquisitionError("FRED returned a truncated or inconsistent page")
        artifact = write_json(directory / f"{label}-{len(artifacts):03d}.json", payload)
        artifacts.append({**artifact, "endpoint": FRED_BASE + endpoint,
                          "parameters": {**request_params, "file_type": "json"},
                          "row_key": row_key, "rows": len(page), "fetched_at": utc_now()})
        rows.extend(page)
    return rows, artifacts


def scope_sources(data_root: Path, series_ids: tuple[str, ...]) -> dict[str, list[dict]]:
    base = data_root / "free-sources"
    folders = [p for p in base.iterdir() if p.is_dir() and
               (p.name.startswith("fred__") or p.name == "cross-asset__rates")]
    result = {}
    for series in series_ids:
        names = {f"{series}.json", f"FRED_{series}.csv"}
        if series in BLS_SERIES:
            names = {f"release-{BLS_SERIES[series][0]}.json"}
        paths = sorted(p for folder in folders for p in folder.iterdir()
                       if p.is_file() and p.name in names)
        if not paths:
            raise ValueError(f"No existing archive reference for {series}")
        result[series] = [{"path": str(p.resolve()), "sha256": sha256(p),
                           "bytes": p.stat().st_size, "mtime_ns": p.stat().st_mtime_ns}
                          for p in paths]
    return result


def acquire(data_root: Path, output_root: Path, key: str, *, start: str, end: str,
            series_ids: tuple[str, ...] = DEFAULT_SERIES,
            reference_start: str | None = None, reference_end: str | None = None,
            progress: Callable[[dict], None] = lambda _: None) -> dict:
    if date.fromisoformat(start) > date.fromisoformat(end):
        raise ValueError("Start date must not follow end date")
    if date.fromisoformat(end) > datetime.now(timezone.utc).date():
        raise ValueError("Acquisition end must not be in the future")
    reference_start, reference_end = reference_start or start, reference_end or end
    if not date.fromisoformat(reference_start) <= date.fromisoformat(reference_end) <= date.fromisoformat(end):
        raise ValueError("Invalid observation reference-period window")
    if not series_ids or len(set(series_ids)) != len(series_ids):
        raise ValueError("Select at least one distinct series")
    if set(series_ids) - set(DEFAULT_SERIES):
        raise ValueError("Series must be selected from the identified archive scope")
    sources = scope_sources(data_root.resolve(), series_ids)
    output = new_output(output_root, data_root, "fred-")
    progress({"status": "started", "output_dir": str(output), "series": len(series_ids)})
    client = FredClient(key)
    manifest = {"schema": "fred-vintage-backfill-v1", "started_at": utc_now(),
                "output_dir": str(output), "observation_start": reference_start, "observation_end": reference_end,
                "realtime_start": start, "realtime_end": end, "series": [],
                "scope": "18 existing FRED series plus CPIAUCSL and PAYEMS identified by banked release calendars; acquisition does not select author model inputs",
                "credentials_retained": False,
                "vintage_precision": "civil date; inclusive real-time intervals; no midnight timestamp inference",
                "source_references": sources}
    clock_candidates = []
    for series in series_ids:
        directory = output / series
        directory.mkdir()
        result = {"series_id": series, "status": "error", "artifacts": []}
        try:
            metadata = client.get("series", {"series_id": series, "realtime_start": end, "realtime_end": end})
            meta_rows = metadata.get("seriess", [])
            if len(meta_rows) != 1 or meta_rows[0].get("id") != series:
                raise AcquisitionError("FRED series metadata identity mismatch")
            result["metadata"] = meta_rows[0]
            result["artifacts"].append({**write_json(directory / "metadata.json", metadata),
                                        "endpoint": FRED_BASE + "series", "fetched_at": utc_now()})
            params = {"series_id": series, "observation_start": reference_start, "observation_end": reference_end,
                      "realtime_start": start, "realtime_end": end, "sort_order": "asc", "units": "lin"}
            histories = {}
            for label, output_type in (("vintages", 1), ("initial", 4)):
                rows, artifacts = fetch_pages(client, "series/observations", {**params, "output_type": output_type},
                                               "observations", directory, label)
                result["artifacts"].extend(artifacts)
                histories[label] = rows
            dates, artifacts = fetch_pages(client, "series/vintagedates",
                                           {"series_id": series, "realtime_start": start, "realtime_end": end, "sort_order": "asc"},
                                           "vintage_dates", directory, "vintage-dates", page_limit=1000)
            result["artifacts"].extend(artifacts)
            valid = [r for r in histories["vintages"] if r["value"] != "."]
            initial = [r for r in histories["initial"] if r["value"] != "."]
            periods = sorted({r["date"] for r in valid})
            counts = Counter(r["date"] for r in valid)
            result.update(status="ok", vintage_rows=len(histories["vintages"]),
                          nonmissing_vintage_rows=len(valid), initial_rows=len(initial),
                          observation_periods=len(periods), revised_periods=sum(v > 1 for v in counts.values()),
                          first_observation=periods[0] if periods else None,
                          last_observation=periods[-1] if periods else None, vintage_dates=len(dates))
            if series in BLS_SERIES:
                prefix = BLS_SERIES[series][1]
                for day in sorted({r["realtime_start"] for r in initial}):
                    stamp = date.fromisoformat(day).strftime("%m%d%Y")
                    clock_candidates.append({"series_id": series, "vintage_date": day,
                                             "url": f"https://www.bls.gov/news.release/archives/{prefix}_{stamp}.htm"})
        except (AcquisitionError, ValueError, KeyError) as exc:
            # Only fixed AcquisitionError diagnostics are safe to retain.
            result["error"] = str(exc) if isinstance(exc, AcquisitionError) else type(exc).__name__
        write_json(directory / "receipt.json", result)
        manifest["series"].append(result)
        progress({k: v for k, v in result.items() if k not in {"artifacts", "metadata"}})
    manifest["source_references_unchanged"] = all(
        sha256(Path(ref["path"])) == ref["sha256"] and Path(ref["path"]).stat().st_mtime_ns == ref["mtime_ns"]
        for refs in sources.values() for ref in refs)
    manifest["all_series_succeeded"] = all(s["status"] == "ok" for s in manifest["series"])
    manifest["completed_at"], manifest["http_requests"] = utc_now(), client.requests
    manifest["clock_candidates"] = write_json(output / "clock-candidates.json", clock_candidates)
    write_json(output / "manifest.json", manifest)
    return manifest


def parse_release_clock(evidence: dict) -> dict | None:
    """Require the actual BLS embargo header and the matching vintage civil date."""
    header = evidence.get("header_text")
    if not header:
        return None
    series, day = evidence["series_id"], evidence["vintage_date"]
    if series not in BLS_SERIES:
        raise ValueError("BLS clock supplied for a non-BLS series")
    expected = ("https://www.bls.gov/news.release/archives/" + BLS_SERIES[series][1] +
                "_" + date.fromisoformat(day).strftime("%m%d%Y") + ".htm")
    if evidence["url"] != expected:
        raise ValueError("BLS clock URL does not match its series and vintage date")
    match = re.search(r"embargoed until.*?(\d{1,2}):(\d{2})\s*a\.m\.\s*\((E[DS]?T)\)\s*"
                      r"(?:[A-Za-z]+,\s*)?([A-Za-z]+\s+\d{1,2},\s*\d{4})", header, re.I)
    if not match:
        raise ValueError("Unrecognized BLS embargo header")
    parsed = datetime.strptime(match[4], "%B %d, %Y").date()
    if parsed.isoformat() != day:
        raise ValueError("BLS publication date differs from the FRED vintage date")
    local = datetime(parsed.year, parsed.month, parsed.day, int(match[1]), int(match[2]),
                     tzinfo=ZoneInfo("America/New_York"))
    if match[3] != "ET" and local.tzname() != match[3]:
        raise ValueError("BLS timezone abbreviation conflicts with the publication date")
    return {**evidence, "released_at": int(local.timestamp()) * 1_000_000_000,
            "released_at_utc": local.astimezone(timezone.utc).isoformat(),
            "release_timezone": "America/New_York", "precision": "minute",
            "binding": "BLS publication header date matches FRED initial-vintage date; feed receipt unobserved"}


def normalized_rows(series: str, metadata: dict, history: list[dict], initial: list[dict],
                    clocks: dict[tuple[str, str], dict], *, start: str, end: str,
                    realtime_start: str | None = None, realtime_end: str | None = None) -> list[dict]:
    realtime_start, realtime_end = realtime_start or start, realtime_end or end
    def identity(row):
        value = None if row["value"] == "." else Decimal(row["value"])
        if value is not None and not value.is_finite():
            raise ValueError("Non-finite FRED observation")
        return row["date"], row["realtime_start"], value

    initial_keys = {identity(r) for r in initial if r["value"] != "."}
    history_keys = {identity(r) for r in history}
    if not initial_keys <= history_keys:
        raise ValueError("Initial releases do not reconcile with the vintage history")
    result, previous, seen_keys = [], {}, set()
    for row in sorted(history, key=lambda r: (r["date"], r["realtime_start"])):
        period, vintage, numeric = identity(row)
        last = row["realtime_end"]
        for text in (period, vintage, last):
            date.fromisoformat(text)
        if not start <= period <= end or not realtime_start <= vintage <= last <= realtime_end:
            raise ValueError("Observation or vintage interval outside the acquisition window")
        if (period, vintage) in seen_keys:
            raise ValueError("Duplicate or conflicting observation vintage")
        if period in previous and vintage <= previous[period]:
            raise ValueError("Overlapping real-time intervals")
        seen_keys.add((period, vintage))
        previous[period] = last
        is_initial = identity(row) in initial_keys
        clock = clocks.get((series, vintage)) if is_initial else None
        result.append({
            "series_id": series, "reference_period": period,
            "value": None if numeric is None else row["value"], "fred_value": row["value"],
            "units": metadata["units"], "frequency": metadata["frequency"],
            "seasonal_adjustment": metadata.get("seasonal_adjustment"),
            "vintage_id": f"FRED:{series}:{period}:{vintage}",
            "realtime_start": vintage, "realtime_end": last,
            "vintage_precision": "civil_date", "is_initial_release": is_initial,
            "scheduled_at": None, "available_at": None, "known_at": None,
            "released_at": clock["released_at"] if clock else None,
            "released_at_utc": clock["released_at_utc"] if clock else None,
            "release_clock_source": clock["url"] if clock else None,
            "clock_precision": clock["precision"] if clock else None,
            "availability_assumption": None,
            "availability_status": "verified_publication_only" if clock else "intraday_unknown",
            "source": "FRED/ALFRED output_type=1, initial identity checked against output_type=4",
        })
    return result


def vintage_on_date(rows: list[dict], series: str, period: str, as_of: str) -> dict | None:
    """Date-level ALFRED snapshot only; this does not establish intraday availability."""
    date.fromisoformat(as_of)
    selected = [r for r in rows if r["series_id"] == series and r["reference_period"] == period
                and r["realtime_start"] <= as_of <= r["realtime_end"]]
    if len(selected) > 1:
        raise ValueError("Conflicting vintages at the requested date")
    return selected[0] if selected else None


def releases_for_decision(rows: list[dict], series: str, period: str, decision_ns: int,
                          *, initial_only: bool = False) -> list[dict]:
    """Prepare O162 inputs. Unknown clocks stay unknown, including relevant revisions.

    O162 must receive ``release_as_availability=True`` explicitly to use verified
    publication clocks. Future vintage *dates* can be excluded without inventing
    a midnight availability timestamp; same-day unknown releases stay in the input.
    """
    day = datetime.fromtimestamp(decision_ns // 1_000_000_000, ZoneInfo("America/New_York")).date().isoformat()
    return [dict(r) for r in rows if r["series_id"] == series and r["reference_period"] == period
            and r["realtime_start"] <= day and (not initial_only or r["is_initial_release"])]


def resolve_clocks(candidates: list[dict], evidence_rows: list[dict]) -> tuple[dict, list]:
    expected = {(r["series_id"], r["vintage_date"]): r for r in candidates}
    clocks, supplied, unresolved = {}, set(), []
    for evidence in evidence_rows:
        key = (evidence["series_id"], evidence["vintage_date"])
        if key not in expected or key in supplied:
            raise ValueError("Clock evidence is outside this bundle or duplicated")
        supplied.add(key)
        clock = parse_release_clock(evidence)
        if clock:
            clocks[key] = clock
        else:
            unresolved.append(evidence)
    unresolved.extend({**row, "status": "clock_evidence_not_supplied"}
                      for key, row in expected.items() if key not in supplied)
    return clocks, unresolved


def normalize_bundle(bundle: Path, data_root: Path, clock_evidence: Path) -> dict:
    bundle = bundle.resolve()
    manifest = json.loads((bundle / "manifest.json").read_text())
    evidence_rows = json.loads(clock_evidence.read_text())
    # Validate every retained response before creating a normalized output directory.
    for item in manifest["series"]:
        for artifact in item["artifacts"]:
            path = (bundle / item["series_id"] / artifact["path"]).resolve()
            if not path.is_relative_to(bundle) or sha256(path) != artifact["sha256"]:
                raise ValueError("Source artifact path or checksum mismatch")
    candidates_path = bundle / "clock-candidates.json"
    if sha256(candidates_path) != manifest["clock_candidates"]["sha256"]:
        raise ValueError("Clock candidate checksum mismatch")
    clocks, unresolved = resolve_clocks(json.loads(candidates_path.read_text()), evidence_rows)
    output = new_output(bundle, data_root, "normalized-")
    summary = {"schema": "economic-vintages-v1", "created_at": utc_now(), "output_dir": str(output),
               "acquisition_manifest": {"path": str(bundle / "manifest.json"), "sha256": sha256(bundle / "manifest.json")},
               "clock_evidence": {"path": str(clock_evidence.resolve()), "sha256": sha256(clock_evidence)},
               "clock_records_verified": len(clocks), "clock_records_unresolved": len(unresolved),
               "unresolved_clock_candidates": unresolved,
               "series": [], "artifacts": [],
               "availability_policy": "available_at/known_at remain null; O162 may explicitly use verified released_at as availability. Revisions without a verified value-specific publication clock remain holes.",
               "observation_window": [manifest["observation_start"], manifest["observation_end"]],
               "realtime_window": [manifest["realtime_start"], manifest["realtime_end"]]}
    summary["artifacts"].append(write_json(output / "release-clocks.json", list(clocks.values())))
    for item in manifest["series"]:
        if item["status"] != "ok":
            summary["series"].append({"series_id": item["series_id"], "status": "acquisition_failed"})
            continue
        series = item["series_id"]
        loaded = {label: [row for art in item["artifacts"] if art["path"].startswith(label + "-")
                          for row in json.loads((bundle / series / art["path"]).read_text())["observations"]]
                  for label in ("vintages", "initial")}
        rows = normalized_rows(series, item["metadata"], loaded["vintages"], loaded["initial"], clocks,
                               start=manifest["observation_start"], end=manifest["observation_end"],
                               realtime_start=manifest["realtime_start"], realtime_end=manifest["realtime_end"])
        path = output / f"{series}.jsonl"
        with path.open("x", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
        artifact = {"path": path.name, "sha256": sha256(path), "rows": len(rows), "bytes": path.stat().st_size}
        summary["artifacts"].append(artifact)
        summary["series"].append({"series_id": series, "status": "ok", "rows": len(rows),
                                  "nonmissing_rows": sum(r["value"] is not None for r in rows),
                                  "initial_release_rows": sum(r["is_initial_release"] for r in rows),
                                  "publication_clock_rows": sum(r["released_at"] is not None for r in rows),
                                  "feed_availability_rows": 0,
                                  "missing_observation_periods": sorted({r["reference_period"] for r in rows if r["value"] is None}),
                                  "artifact": artifact})
    summary["all_series_normalized"] = all(r["status"] == "ok" for r in summary["series"])
    write_json(output / "manifest.json", summary)
    return summary
