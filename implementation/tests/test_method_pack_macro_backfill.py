"""Acquisition integrity and causal release-boundary checks for the macro backfill."""

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import io
import json
from pathlib import Path
import urllib.error

import pytest

from trading_research.research.method_pack import objects as _objects  # noqa: F401
from trading_research.research.method_pack.macro_backfill import (
    AcquisitionError, FredClient, fetch_pages, new_output, normalize_bundle,
    normalized_rows, parse_release_clock, releases_for_decision, sha256,
    vintage_on_date, write_json, resolve_clocks,
)
from trading_research.research.method_pack.protocol import run_recipe


METADATA = {"units": "Index 1982-1984=100", "frequency": "Monthly", "seasonal_adjustment": "Seasonally Adjusted"}
INITIAL = {"date": "2020-01-01", "realtime_start": "2020-02-13", "realtime_end": "2021-02-07", "value": "258.820"}
REVISED = {"date": "2020-01-01", "realtime_start": "2021-02-08", "realtime_end": "2022-01-01", "value": "258.687"}
EVIDENCE = {"series_id": "CPIAUCSL", "vintage_date": "2020-02-13",
            "url": "https://www.bls.gov/news.release/archives/cpi_02132020.htm",
            "header_text": "embargoed until 8:30 a.m. (EST) February 13, 2020"}


def rows():
    clock = parse_release_clock(EVIDENCE)
    return normalized_rows("CPIAUCSL", METADATA, [INITIAL, REVISED], [INITIAL],
                           {("CPIAUCSL", "2020-02-13"): clock}, start="2020-01-01", end="2022-01-01")


class Pages:
    def __init__(self, payloads):
        self.payloads, self.offsets = iter(payloads), []

    def get(self, endpoint, params):
        self.offsets.append(params["offset"])
        return next(self.payloads)


def test_pagination_retains_every_row_and_checksums(tmp_path):
    client = Pages([{"count": 3, "offset": 0, "observations": [{"value": "1"}, {"value": "2"}]},
                    {"count": 3, "offset": 2, "observations": [{"value": "3"}]}])
    got, artifacts = fetch_pages(client, "series/observations", {}, "observations", tmp_path, "test", page_limit=2)
    assert [r["value"] for r in got] == ["1", "2", "3"]
    assert client.offsets == [0, 2]
    assert all(sha256(tmp_path / a["path"]) == a["sha256"] for a in artifacts)


@pytest.mark.parametrize("bad", [
    {"count": 3, "offset": 2, "observations": []},
    {"count": 4, "offset": 2, "observations": [{"value": "3"}]},
    {"count": 3, "offset": 0, "observations": [{"value": "3"}]},
])
def test_pagination_never_reports_truncation_as_complete(tmp_path, bad):
    client = Pages([{"count": 3, "offset": 0, "observations": [{}, {}]}, bad])
    with pytest.raises(AcquisitionError):
        fetch_pages(client, "series/observations", {}, "observations", tmp_path, "test", page_limit=2)


def test_request_errors_and_responses_cannot_retain_credentials():
    key = "a" * 32

    def broken(request, **kwargs):
        raise urllib.error.URLError(request.full_url)

    client = FredClient(key, opener=broken, sleep=lambda _: None)
    with pytest.raises(AcquisitionError) as caught:
        client.get("series", {"series_id": "CPIAUCSL"})
    assert key not in str(caught.value)
    assert client.requests == 5
    client = FredClient(key, opener=lambda *a, **k: io.BytesIO(json.dumps({"echo": key}).encode()), sleep=lambda _: None)
    with pytest.raises(AcquisitionError) as caught:
        client.get("series", {"series_id": "CPIAUCSL"})
    assert key not in str(caught.value)


def test_raw_archive_and_existing_artifacts_are_protected(tmp_path):
    raw = tmp_path / "data"
    raw.mkdir()
    sentinel = raw / "original"
    sentinel.write_text("unchanged")
    link = tmp_path / "link"
    link.symlink_to(raw, target_is_directory=True)
    for output in (raw, raw / "child", link / "child"):
        with pytest.raises(ValueError, match="read-only"):
            new_output(output, raw, "test-")
    assert list(raw.iterdir()) == [sentinel]
    assert sentinel.read_text() == "unchanged"
    write_json(tmp_path / "one.json", {"original": True})
    with pytest.raises(FileExistsError):
        write_json(tmp_path / "one.json", {"overwritten": True})


def test_clocks_preserve_dst_and_require_exact_release_identity():
    assert parse_release_clock(EVIDENCE)["released_at_utc"] == "2020-02-13T13:30:00+00:00"
    summer = {**EVIDENCE, "vintage_date": "2020-08-12", "url": "https://www.bls.gov/news.release/archives/cpi_08122020.htm",
              "header_text": "embargoed until 8:30 a.m. (ET) August 12, 2020"}
    assert parse_release_clock(summer)["released_at_utc"] == "2020-08-12T12:30:00+00:00"
    for bad in ({**EVIDENCE, "header_text": EVIDENCE["header_text"].replace("EST", "EDT")},
                {**EVIDENCE, "header_text": EVIDENCE["header_text"].replace("13,", "14,")},
                {**EVIDENCE, "url": summer["url"]}):
        with pytest.raises(ValueError):
            parse_release_clock(bad)


def test_omitted_clocks_are_reported_as_missing_evidence():
    clocks, missing = resolve_clocks([EVIDENCE], [])
    assert not clocks
    assert missing[0]["status"] == "clock_evidence_not_supplied"
    clocks, missing = resolve_clocks([EVIDENCE], [EVIDENCE])
    assert len(clocks) == 1 and not missing
    with pytest.raises(ValueError):
        resolve_clocks([], [EVIDENCE])


def test_date_level_revision_boundary_does_not_backdate_revised_values():
    got = rows()
    assert vintage_on_date(got, "CPIAUCSL", "2020-01-01", "2020-01-31") is None
    assert vintage_on_date(got, "CPIAUCSL", "2020-01-01", "2021-02-07")["value"] == "258.820"
    assert vintage_on_date(got, "CPIAUCSL", "2020-01-01", "2021-02-08")["value"] == "258.687"
    assert all(r["available_at"] is None and r["known_at"] is None for r in got)
    assert got[1]["released_at"] is None  # A revision does not inherit the original release clock.


def test_prior_reference_period_can_be_first_released_in_trading_window():
    december = {"date": "2019-12-01", "realtime_start": "2020-01-10", "realtime_end": "2020-02-06", "value": "152383"}
    got = normalized_rows("PAYEMS", METADATA, [december], [december], {}, start="2019-12-01", end="2019-12-31",
                          realtime_start="2020-01-01", realtime_end="2026-09-12")
    assert got[0]["reference_period"] == "2019-12-01"
    assert got[0]["realtime_start"] == "2020-01-10"
    assert got[0]["available_at"] is None


def test_o162_cannot_see_release_early_or_skip_an_unknown_revision():
    got = rows()
    release = parse_release_clock(EVIDENCE)["released_at"]

    def evaluate(at, *, assumption=True, initial_only=False):
        return run_recipe("O162", {"series_id": "CPIAUCSL", "reference_period": "2020-01-01",
                                   "releases": releases_for_decision(got, "CPIAUCSL", "2020-01-01", at, initial_only=initial_only),
                                   "as_of": at, "vintage_policy": "initial_release" if initial_only else "latest_available",
                                   "release_as_availability": assumption})

    assert evaluate(release - 1).state == "hole"
    assert evaluate(release, assumption=False).state == "hole"
    assert evaluate(release).value["value"] == Decimal("258.820")
    revision_day = int(datetime(2021, 2, 8, 15, tzinfo=timezone.utc).timestamp()) * 1_000_000_000
    assert "HOLE:O162:available_at" in evaluate(revision_day).hole_ids
    assert evaluate(revision_day, initial_only=True).value["value"] == Decimal("258.820")


def test_missing_values_remain_missing_and_conflicting_intervals_fail():
    empty = {**INITIAL, "value": "."}
    result = normalized_rows("CPIAUCSL", METADATA, [empty], [empty], {}, start="2020-01-01", end="2022-01-01")
    assert result[0]["value"] is None and result[0]["released_at"] is None
    for history in ([INITIAL, deepcopy(INITIAL)], [INITIAL, {**REVISED, "realtime_start": "2021-02-07"}]):
        with pytest.raises(ValueError):
            normalized_rows("CPIAUCSL", METADATA, history, [INITIAL], {}, start="2020-01-01", end="2022-01-01")


def test_normalizer_rejects_tampered_source_before_creating_output(tmp_path):
    bundle = tmp_path / "bundle"
    (bundle / "CPIAUCSL").mkdir(parents=True)
    original = write_json(bundle / "CPIAUCSL" / "vintages-000.json", {"observations": [INITIAL]})
    write_json(bundle / "manifest.json", {"series": [{"series_id": "CPIAUCSL", "artifacts": [original]}]})
    (bundle / "CPIAUCSL" / "vintages-000.json").write_text("tampered")
    evidence = tmp_path / "clocks.json"
    evidence.write_text("[]")
    with pytest.raises(ValueError, match="checksum"):
        normalize_bundle(bundle, tmp_path / "data", evidence)
    assert not list(bundle.glob("normalized-*"))
