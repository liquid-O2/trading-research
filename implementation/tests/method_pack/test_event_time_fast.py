"""event_time_fast reproduces the pinned event-time implementation byte for byte.

Every fast path is compared with the pinned function it replaces on synthetic
documents that exercise the edge cases (ties, tick-grid fills, late-known minutes,
non-monotone ends, partial minutes, non-integer volumes, two spellings of one
price, misaligned prices) and, when the frozen event cache is present, on a real
session window. Equality is on the ``jsonable`` JSON bytes, so a Decimal spelled
differently ('1.0' versus '1.00') is a failure even though the values compare equal.
"""
from __future__ import annotations

from decimal import Decimal
import json
import os
from pathlib import Path

import pytest

from trading_research.research.method_pack import event_cache, event_time
from trading_research.research.method_pack import event_time_fast as fast
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.event_time import CONTRACT, MINUTE, VERSION, EventWindow
from trading_research.research.method_pack.protocol import jsonable

MP = Path(__file__).resolve().parents[2] / "src/trading_research/research/method_pack"
CACHE = Path("/workspace/data/derived/phase1-event-time-v2")


def canonical(payload) -> bytes:
    return json.dumps(jsonable(payload), sort_keys=True, separators=(",", ":")).encode()


def synthetic_document(*, start=1_000_000 * MINUTE, minutes=6, spellings=False, floats=False):
    """A tiny event window: six minutes, one late-known minute, gaps in the tick grid."""
    end = start + minutes * MINUTE
    footprints, bars = [], []
    table = [
        [["100.25", 4, 1, 0], ["100.5", 2, 2, 0], ["101.0", 0, 3, 1]],
        [["100.5", 1, 1, 0], ["100.75", 5, 0, 0]],
        [["101.0", 2, 2, 0], ["101.5", 2, 2, 0]],          # tie at the top, gap at 101.25
        [["100.25", 3, 3, 0], ["101.5", 1, 0, 0]],
        [["100.0", 1, 0, 0]],
        [["101.75", 0, 1, 0], ["100.5", 1, 1, 0]],
    ]
    if spellings:
        table[3][0][0] = "100.250"                            # a second spelling of 100.25
    if floats:
        table[1][1][1] = 5.0                                  # a non-integer volume type
    for i, rows in enumerate(table):
        at = start + i * MINUTE
        known = at + MINUTE + (3 * MINUTE if i == 2 else 0)  # minute 2 is known late
        volume = int(sum(b + s + u for _, b, s, u in rows))   # the minute volume is an int in every window
        pv = sum(Decimal(px) * Decimal(str(b + s + u)) for px, b, s, u in rows)
        p2v = sum(Decimal(px) * Decimal(px) * Decimal(str(b + s + u)) for px, b, s, u in rows)
        footprints.append({"start": at, "end": at + MINUTE, "known_at": known, "instrument_id": 7,
                           "rows": [[Decimal(px), b, s, u] for px, b, s, u in rows],
                           "volume": volume, "pv": pv, "p2v": p2v})
        bars.append({"start": at, "end": at + MINUTE, "known_at": known, "observed_complete": i != 4,
                     "O": Decimal("100.5"), "H": Decimal("101.75"), "L": Decimal("100"), "C": Decimal("100.5"),
                     "V": volume, "bar_id": f"b{i}"})
    return {"schema": VERSION, "contract_sha256": content_hash(CONTRACT), "instrument_id": 7,
            "start_ns": start, "end_ns": end, "bars": {"60": bars}, "footprints": footprints,
            "plan": {"unowned_intervals": [[start + 4 * MINUTE + 10, start + 4 * MINUTE + 20]]}}


def queries(document):
    start, end = document["start_ns"], document["end_ns"]
    out = []
    for s in (start, start + MINUTE, start + 2 * MINUTE + 5):
        for e in (start + MINUTE, start + 3 * MINUTE, start + 5 * MINUTE + 30, end, start + 2 * MINUTE, end - 1):
            if e > s:
                out.append((s, e))
    return out


@pytest.mark.parametrize("spellings,floats", [(False, False), (True, False), (False, True)])
def test_fast_window_equals_pinned_window_synthetic(spellings, floats):
    document = synthetic_document(spellings=spellings, floats=floats)
    pinned, quick = EventWindow(document), fast.FastEventWindow(document)
    assert quick._prefix_index()["vectorised"] is (not spellings and not floats)
    for s, e in queries(document):                         # non-monotone ends and several starts
        assert canonical(quick.coverage(s, e)) == canonical(pinned.coverage(s, e)), (s, e)
        assert canonical(quick.profile(s, e)) == canonical(pinned.profile(s, e)), (s, e)
        assert canonical(quick.vwap(s, e)) == canonical(pinned.vwap(s, e)), (s, e)
    # A returned coverage is a fresh object: mutating it cannot leak into the memo.
    first = quick.coverage(document["start_ns"], document["end_ns"])
    first["states"]["poisoned"] = 1
    assert "poisoned" not in quick.coverage(document["start_ns"], document["end_ns"])["states"]


def test_payload_arrays_equals_pinned_payload_with_fills_and_ties():
    document = synthetic_document()
    quick = fast.FastEventWindow(document)
    start, end = document["start_ns"], document["end_ns"]
    value_area = {"fraction": Decimal(".70"), "algorithm": "contiguous_larger_adjacent_volume_tie_both",
                  "tie_policy": "both"}
    for complete in (True, False, None):
        for e in (start + MINUTE, start + 3 * MINUTE, end):
            prefix = quick._prefix(start, e)
            expected = fast.PINNED["profile_payload"](prefix.accum(), tick=Decimal(".25"), tie_policy="lowest",
                                                      value_area=value_area, complete=complete)
            got = prefix.payload(tick=Decimal(".25"), tie_policy="lowest", value_area=value_area,
                                 complete=complete)
            assert canonical(got) == canonical(expected), (complete, e)
            if complete is True and e == end:
                assert any(str(row["price"]) == "101.25" for row in got["rows"])   # a tick-grid fill
                assert got["poc_tie_state"] in ("unique", "resolved")
    # The empty prefix (no minute qualifies) and the empty-profile path.
    prefix = quick._prefix(end - 1, end)
    expected = fast.PINNED["profile_payload"](prefix.accum(), tick=Decimal(".25"), tie_policy="lowest",
                                              value_area=value_area, complete=True)
    assert canonical(prefix.payload(tick=Decimal(".25"), tie_policy="lowest", value_area=value_area,
                                    complete=True)) == canonical(expected)
    assert expected["poc_tie_state"] == "empty"


def test_payload_arrays_raises_like_pinned_on_misaligned_price():
    document = synthetic_document()
    document["footprints"][0]["rows"][0][0] = Decimal("100.3")
    quick = fast.FastEventWindow(document)
    start, end = document["start_ns"], document["end_ns"]
    with pytest.raises(event_time.NativeEvidenceError, match="not aligned to native tick"):
        quick.profile(start, end)
    with pytest.raises(event_time.NativeEvidenceError, match="not aligned to native tick"):
        EventWindow(document).profile(start, end)


def test_row_dict_equals_asdict():
    from dataclasses import asdict
    from trading_research.research.method_pack.objects.profiles import PriceRow
    row = PriceRow(Decimal("1.25"), Decimal(3), Decimal(1), Decimal(0), Decimal(4), Decimal(2), Decimal(2),
                   Decimal(2), Decimal(2))
    assert fast._row_payload(row) == asdict(row)
    assert list(fast._row_payload(row)) == list(asdict(row))


def test_file_digest_memo_is_signature_bound(tmp_path, monkeypatch):
    store = tmp_path / "store"
    monkeypatch.setenv("TR_FILE_DIGEST_CACHE", str(store))
    fast._DIGEST_MEMO.clear()
    fast._DIGEST_STORE_OFFSETS.clear()
    big = tmp_path / "big.bin"
    big.write_bytes(os.urandom(1024) * (8 * 1024 + 1))          # above the 8 MiB memo floor
    first = fast.file_digest(big)
    assert first == fast.PINNED["file_digest"](big)
    assert any(store.glob("*.jsonl"))
    key = next(k for k in fast._DIGEST_MEMO if k[0] == str(big))
    fast._DIGEST_MEMO[key] = "sentinel"                           # a hit is returned without hashing
    assert fast.file_digest(big) == "sentinel"
    big.write_bytes(os.urandom(1024) * (8 * 1024 + 2))          # new size: the memo cannot answer
    assert fast.file_digest(big) == fast.PINNED["file_digest"](big) != "sentinel"
    # The persistent store answers a fresh process (simulated by clearing the memo).
    fast._DIGEST_MEMO.clear()
    fast._DIGEST_STORE_OFFSETS.clear()
    assert fast.file_digest(big) == fast.PINNED["file_digest"](big)
    small = tmp_path / "small.bin"
    small.write_bytes(b"a" * 4096)
    assert fast.file_digest(small) == fast.PINNED["file_digest"](small)
    small.write_bytes(b"b" * 4096)                                # same size and inode: still hashed
    assert fast.file_digest(small) == fast.PINNED["file_digest"](small)
    monkeypatch.setenv("TR_FILE_DIGEST_CACHE", "off")
    assert fast.digest_store_dir() is None


def test_install_rebinds_pinned_modules():
    assert event_time.file_digest is fast.file_digest
    assert event_cache.file_digest is fast.file_digest
    assert event_cache.contract_at is fast.contract_at
    assert event_time._canonical_manifest is fast.canonical_manifest
    from trading_research.research.method_pack import historical_features, strategy_measurements
    assert historical_features.EventWindow is fast.FastEventWindow
    assert issubclass(strategy_measurements.StrategyWindow, fast.FastEventWindow)


def test_transform_identity_files_are_untouched():
    """The fast module lives outside the event-cache transform identity."""
    names = ['event_time.py', 'event_cache.py', 'mbp1_views.py', 'adapters.py', 'native_resolution.py',
             'empirical_tape.py', 'objects/profiles.py']
    for name in names:
        assert "event_time_fast" not in (MP / name).read_text(), name
    assert (MP / "event_time_fast.py").is_file()


@pytest.mark.skipif(not CACHE.is_dir() or not Path("/workspace/data").is_dir(), reason="frozen event cache absent")
def test_real_window_and_lookups_equal_pinned():
    windows = sorted(p for p in CACHE.iterdir() if (p / "window.json.gz").is_file())
    if not windows:
        pytest.skip("no cached window")
    import gzip
    chosen = max(windows[:64], key=lambda p: (p / "window.json.gz").stat().st_size)
    document = event_cache.restore(json.loads(gzip.decompress((chosen / "window.json.gz").read_bytes())))
    pinned, quick = EventWindow(document), fast.FastEventWindow(document)
    start, end = document["start_ns"], document["end_ns"]
    minutes = sorted(quick.footprints)
    probes = [(start, minutes[len(minutes) // 3]), (start, minutes[len(minutes) // 2]), (start, end),
              (minutes[len(minutes) // 4], minutes[-1]), (start, minutes[len(minutes) // 3] + 7)]
    for s, e in probes:
        assert canonical(quick.coverage(s, e)) == canonical(pinned.coverage(s, e))
        assert canonical(quick.profile(s, e)) == canonical(pinned.profile(s, e))
        assert canonical(quick.vwap(s, e)) == canonical(pinned.vwap(s, e))
    root = "/workspace/data"
    at = start + 3 * 3600 * 10 ** 9
    assert fast.contract_at(root, at) == fast.PINNED["contract_at"](root, at)
    assert fast.canonical_manifest(Path(root)) == fast.PINNED["canonical_manifest"](Path(root))
