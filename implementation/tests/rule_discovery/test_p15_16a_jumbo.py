"""P15-16A JJ-TBR B0.2 fixtures, replay, funnel, and frozen-row identity."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any
import hashlib
import json

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.rule_discovery.baseline_repairs import scan_branch_repaired
from trading_research.research.rule_discovery.runner import engineering_slice_dates
from trading_research.research.rule_discovery.source_adapters.common import (
    dual_scan,
    frozen_scan_document,
    load_source_market,
    strip_baseline_version,
)
from trading_research.research.rule_discovery.source_adapters.jumbo import (
    FAMILY,
    PZONE_FIXTURES,
    RULES,
    STAGE_ORDER,
    classify_first_hour_sweep,
    compute_published_statistics,
    extension_reaction_bands,
    funnel_stage_counts,
    mean_reversal_bands,
    projection_ladder,
    replay_example,
    rules_payload,
    scan_b02,
)

TRACK = Path("/workspace/implementation/reports/research-work/P15-16A/_track_jumbo")
EXAMPLES = Path("/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json")
NS_MINUTE = 60_000_000_000


class Tape:
    def __init__(self, day: str, bars: list[dict], prior_rth=None, sessionstat_box=None):
        self.account_day = day
        self._bars = bars
        self.prior_rth = prior_rth
        self.sessionstat_box = sessionstat_box

    def bars(self, start, end, seconds=60):
        return [row for row in self._bars if row["start"] < end and row["end"] > start]


def _bar(day: str, hhmm: str, o, h, l, c, minutes=1, volume=100):
    hour, minute = [int(part) for part in hhmm.split(":")]
    start = et_ns(date.fromisoformat(day), hour, minute)
    end = start + minutes * NS_MINUTE
    return {
        "start": start,
        "end": end,
        "O": Decimal(str(o)),
        "H": Decimal(str(h)),
        "L": Decimal(str(l)),
        "C": Decimal(str(c)),
        "known_at": end,
        "volume": volume,
        "bar_id": f"{day}:{hhmm}:{minutes}",
        "observed_complete": True,
    }


def _range_bars(day: str, high, low):
    mid = (Decimal(str(high)) + Decimal(str(low))) / 2
    return [
        _bar(day, "06:00", mid, high, low, mid, minutes=60),
        _bar(day, "07:00", mid, high, low, mid, minutes=60),
        _bar(day, "08:00", mid, high, low, mid, minutes=60),
    ]


def _hash_doc(document) -> str:
    blob = json.dumps(document, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()


def test_rr01_extension_band_identity_and_printed_examples():
    bands = extension_reaction_bands(Decimal("110"), Decimal("100"))
    assert bands["upper"] == [Decimal("123.30"), Decimal("126.60")]
    assert bands["lower"] == [Decimal("83.40"), Decimal("86.70")]
    jan = extension_reaction_bands(Decimal("21410"), Decimal("21257.50"), Decimal("152.50"))
    assert jan["upper"][0] == Decimal("21612.8250")
    assert jan["upper"][1] == Decimal("21663.1500")
    sep = extension_reaction_bands(Decimal("23860"), Decimal("23810"), Decimal("50"))
    assert sep["lower"] == [Decimal("23727.00"), Decimal("23743.50")]
    near = mean_reversal_bands(Decimal("110"), Decimal("100"))
    assert near["upper"] != bands["upper"]
    assert "RR-01-extension-band-1.33-1.66" in RULES
    assert RULES["RR-01-OD-near-band-0.33-0.66"]["kind"] == "OD"


def test_rr01_future_bars_do_not_widen_the_band():
    day = "2025-01-28"
    bars = _range_bars(day, 110, 100) + [
        _bar(day, "10:15", 125, 125.5, 124.5, 125),
        _bar(day, "15:00", 200, 200, 199, 200),
    ]
    market = Tape(day, bars)
    doc = scan_b02(market, "extension_reaction")
    episodes = [ep for ep in doc["episodes"] if ep["side"] == "short"]
    assert episodes
    loc = next(stage for stage in episodes[0]["stages"] if stage["stage"] == "location")
    assert loc["operands"]["band"] == ["123.30", "126.60"]
    assert episodes[0]["geometry"]["reference_level"]
    assert all(int(ep["decision_at"]) < et_ns(date.fromisoformat(day), 15, 0) for ep in episodes)


def test_rr03_sweep_before_0930_is_a_valid_trigger():
    day = "2025-10-13"
    high, low = Decimal("24878"), Decimal("24731")
    bars = _range_bars(day, high, low) + [
        _bar(day, "09:05", 24870, 24890, 24860, 24848.5),
        _bar(day, "09:40", 24780, 24790, 24720, 24768.5),
        _bar(day, "09:53", 24770, 24790, 24760, 24780),
    ]
    doc = scan_b02(Tape(day, bars), "judas_reversal")
    shorts = [ep for ep in doc["episodes"] if ep["side"] == "short"]
    longs = [ep for ep in doc["episodes"] if ep["side"] == "long"]
    assert shorts
    trigger = next(stage for stage in shorts[0]["stages"] if stage["stage"] == "trigger")
    assert trigger["operands"]["before_0930"] is True
    assert longs
    assert longs[0]["values"]["edge_reclaimed"] is True


def test_rr04_london_box_is_0200_0300_not_0000_0300():
    day = "2025-10-06"
    high, low = Decimal("25108"), Decimal("25052")
    q25 = Decimal("25066")
    bars = [
        _bar(day, "00:00", 25000, 25200, 24900, 25000, minutes=120),
        _bar(day, "02:00", 25080, high, low, 25080, minutes=60),
        _bar(day, "03:40", q25, 25080, q25, 25080),
        _bar(day, "05:45", 25120, 25138, 25100, 25130),
    ]
    doc = scan_b02(Tape(day, bars), "other_session")
    assert doc["episodes"]
    ref = next(stage for stage in doc["episodes"][0]["stages"] if stage["stage"] == "reference")
    assert ref["operands"]["box"] == "02:00-03:00"
    assert Decimal(ref["operands"]["high"]) == high
    assert Decimal(ref["operands"]["low"]) == low


def test_rr05_printed_pzone_absorption_fixture():
    day = "2026-01-09"
    box = PZONE_FIXTURES[day][0]
    bars = _range_bars(day, 25810, 25710)
    for minute in range(14):
        bars.append(_bar(day, f"08:{minute:02d}", 25700, 25710, 25690, 25700, volume=100))
    bars.append(_bar(day, "09:32", Decimal("25660"), Decimal("25665"), Decimal("25655"), Decimal("25664.25"), volume=200))
    doc = scan_b02(Tape(day, bars), "timed_pzone_reversal")
    assert doc["episodes"]
    ep = doc["episodes"][0]
    assert ep["branch"] == "timed_pzone_reversal"
    assert ep["geometry"]["stop"] == float(box["low"] - Decimal("0.25"))
    assert any(row.get("operand") == "source_zone_known" for row in doc["omissions"])


def test_rr06_reclaim_is_the_entry_and_depth_is_recorded_not_required():
    day = "2025-01-28"
    high, low = Decimal("21410"), Decimal("21258")
    bars = _range_bars(day, high, low) + [
        _bar(day, "09:45", 21240, 21250, 21180, 21220),
        _bar(day, "09:53", 21240, 21270, 21230, Decimal("21241.75")),
    ]
    doc = scan_b02(Tape(day, bars), "judas_reversal")
    longs = [ep for ep in doc["episodes"] if ep["side"] == "long"]
    assert longs
    ep = longs[0]
    assert ep["research_verdict"] == "pass"
    assert ep["values"]["edge_reclaimed"] is True
    assert ep["geometry"]["sweep_depth"] is not None
    assert ep["geometry"]["target"] == float(low + (high - low) * Decimal("0.5"))
    ladder = projection_ladder(high, low)
    assert "plus_1.33" in ladder


def test_rr07_sessionstat_coincidence_and_evrange_after_tape():
    day = "2025-09-09"
    high, low = Decimal("23860"), Decimal("23810")
    bars = _range_bars(day, high, low) + [_bar(day, "10:35", 23730, 23740, 23720, 23730)]
    market = Tape(day, bars, sessionstat_box={"low": Decimal("23727"), "high": Decimal("23765")})
    doc = scan_b02(market, "extension_reaction")
    longs = [ep for ep in doc["episodes"] if ep["side"] == "long"]
    assert longs
    loc = next(stage for stage in longs[0]["stages"] if stage["stage"] == "location")
    assert loc["operands"]["sessionstat_coincidence"] is True
    late = scan_b02(Tape("2026-08-28", []), "extension_reaction")
    assert late["omissions"]
    assert late["omissions"][0]["reason"] == "data_unavailable"


def test_rr08_open_location_uses_prior_rth_at_0930():
    day = "2026-07-27"
    bars = _range_bars(day, 100, 90) + [
        _bar(day, "09:30", 80, 81, 79, 80),
        _bar(day, "09:45", 95, 96, 94, 95),
        _bar(day, "15:00", 200, 200, 199, 200),
    ]
    prior = {"high": Decimal("100"), "low": Decimal("85"), "vah": Decimal("95"), "val": Decimal("90")}
    doc = scan_b02(Tape(day, bars, prior_rth=prior), "single_extended")
    assert doc["episodes"]
    ctx = next(stage for stage in doc["episodes"][0]["stages"] if stage["stage"] == "context")
    assert ctx["operands"]["open_location"] == "below_pdl"
    assert ctx["at_ns"] == et_ns(date.fromisoformat(day), 9, 30)


def test_f08_extension_after_1000_and_1300_admitted():
    day = "2025-11-10"
    bars = _range_bars(day, 110, 100) + [_bar(day, "13:00", 125, 126, 124, 125)]
    doc = scan_b02(Tape(day, bars), "extension_reaction")
    shorts = [ep for ep in doc["episodes"] if ep["side"] == "short"]
    assert shorts
    trigger = next(stage for stage in shorts[0]["stages"] if stage["stage"] == "trigger")
    assert trigger["operands"]["after_1000"] is True
    early = Tape(day, _range_bars(day, 110, 100) + [_bar(day, "09:45", 125, 126, 124, 125)])
    early_doc = scan_b02(early, "extension_reaction")
    assert early_doc["episodes"] == []


def test_f11_3m_ob_baseline_and_od_variants_labelled():
    assert RULES["F11-confirm-3m-ob-baseline"]["kind"] == "literal"
    assert RULES["F11-OD-confirm-2m-5m-rejection"]["kind"] == "OD"
    day = "2025-01-28"
    bars = _range_bars(day, 110, 100) + [
        _bar(day, "09:40", 99, 100, 98, 99, minutes=3),
        _bar(day, "09:43", 98, 99, 97, 98, minutes=3),
        _bar(day, "09:46", 99, 101, 98, 100.5, minutes=3),
    ]
    doc = scan_b02(Tape(day, bars), "judas_reversal")
    longs = [ep for ep in doc["episodes"] if ep["side"] == "long"]
    assert longs
    confirm = next(stage for stage in longs[0]["stages"] if stage["stage"] == "confirmation")
    assert "ob_3m" in confirm["operands"]
    assert "ob_2m" in confirm["operands"]
    assert "rejection_block" in confirm["operands"]


def test_f18_f19_clock_fields():
    day = "2025-01-28"
    doc = scan_b02(Tape(day, _range_bars(day, 110, 100)), "judas_reversal")
    assert doc["clock_zone"] == "America/New_York"
    assert doc["chart_clock_notes"]["ticket_2025-01-28"] == "UTC"
    assert RULES["F18-ny-clock-ET"]["source"].startswith("TBR p.6")
    assert "F12-candidate-references-unchanged" in RULES


def test_rr09_one_side_is_high_only_plus_low_only():
    both = classify_first_hour_sweep(True, True)
    assert both["both"] == 1
    assert both["one_side"] == 0
    high = classify_first_hour_sweep(True, False)
    low = classify_first_hour_sweep(False, True)
    assert high["one_side"] + low["one_side"] == 2
    assert high["high_only"] + low["low_only"] == 2
    assert abs((0.295 + 0.376) - 0.671) < 0.002


def test_funnel_cascade_stops_after_failed_context():
    day = "2026-07-27"
    bars = _range_bars(day, 100, 90) + [
        _bar(day, "09:30", 80, 81, 79, 80),
        _bar(day, "09:45", 95, 96, 94, 95),
    ]
    prior = {"high": Decimal("100"), "low": Decimal("85"), "vah": Decimal("95"), "val": Decimal("90")}
    doc = scan_b02(Tape(day, bars, prior_rth=prior), "single_extended")
    counts = funnel_stage_counts(doc["episodes"])
    names = [name for name in STAGE_ORDER if name in counts]
    passes = [counts[name]["pass"] for name in names]
    assert passes == sorted(passes, reverse=True)
    if names:
        assert passes[-1] == doc["p"]
    assert "location" not in counts or counts["context"]["pass"] >= counts.get("location", {}).get("pass", 0)


def test_scan_b02_stage_names_are_the_contract_set():
    day = "2025-01-28"
    bars = _range_bars(day, 110, 100) + [
        _bar(day, "09:45", 99, 100, 98, 99),
        _bar(day, "09:53", 100, 101, 99, 100.5),
    ]
    doc = scan_b02(Tape(day, bars), "judas_reversal")
    for episode in doc["episodes"]:
        names = [row["stage"] for row in episode["stages"]]
        assert names == [name for name in STAGE_ORDER if name in names]
        assert episode["failed"] or episode["unknown"] or episode["research_verdict"] == "pass"


def test_b0_b01_byte_identity_two_slice_dates():
    from trading_research.research.rule_discovery.source_adapters.common import coverage_row

    hashes = {}
    for day in ("2021-01-04", "2025-01-02"):
        market = load_source_market(day)
        dual = dual_scan(market, FAMILY, "judas_reversal")
        frozen = frozen_scan_document(market, FAMILY, "judas_reversal")
        b0 = strip_baseline_version(dual["b0"])
        b01 = strip_baseline_version(dual["b01"])
        repaired = strip_baseline_version(scan_branch_repaired(market, coverage_row(FAMILY, "judas_reversal")))
        hashes[day] = {
            "b0": _hash_doc(b0.get("episodes") or []),
            "b01": _hash_doc(b01.get("episodes") or []),
            "frozen": _hash_doc(frozen.get("episodes") or []),
            "repaired": _hash_doc(repaired.get("episodes") or []),
        }
        assert hashes[day]["b0"] == hashes[day]["frozen"]
        assert hashes[day]["b01"] == hashes[day]["repaired"]
    TRACK.mkdir(parents=True, exist_ok=True)
    (TRACK / "B0_B01_HASHES.json").write_text(json.dumps(hashes, indent=2) + "\n")


def test_replay_funnel_statistics_and_rules():
    TRACK.mkdir(parents=True, exist_ok=True)
    examples = [row for row in json.loads(EXAMPLES.read_text())["examples"] if row.get("family") == "JJ-TBR"]
    replays = []
    from trading_research.research.rule_discovery.native import build_market_view

    for example in examples:
        if example.get("inside_tape"):
            try:
                market = build_market_view(example["date"])
            except Exception:
                market = None
            row = replay_example(market, example)
        else:
            row = replay_example(None, example)
        assert "detected" in row
        assert row["detected"] in {True, False, None}
        replays.append(row)
    (TRACK / "REPLAY_JJ-TBR.json").write_text(json.dumps(replays, indent=2, default=str) + "\n")

    dates = engineering_slice_dates()
    funnel: dict[str, Any] = {"slice_dates": dates, "branches": {}}
    from trading_research.research.rule_discovery.source_adapters.jumbo import BRANCHES

    for branch in BRANCHES:
        funnel["branches"][branch] = {
            "B0.1": {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0},
            "B0.2": {"episodes": 0, "pass": 0, "fail": 0, "unknown": 0, "stages": {}},
        }
    collected: dict[str, list[dict[str, Any]]] = {branch: [] for branch in BRANCHES}
    for day in dates:
        try:
            hist = load_source_market(day)
        except Exception:
            hist = None
        try:
            view = build_market_view(day)
        except Exception:
            view = None
        for branch in BRANCHES:
            b01_counts = funnel["branches"][branch]["B0.1"]
            b02_counts = funnel["branches"][branch]["B0.2"]
            if hist is not None:
                try:
                    dual = dual_scan(hist, FAMILY, branch)
                    pop = (dual.get("populations") or {}).get("B0.1") or {}
                    b01_counts["episodes"] += int(pop.get("episodes") or 0)
                    b01_counts["pass"] += int(pop.get("setup") or 0)
                    b01_counts["fail"] += int(pop.get("rejected") or 0) + int(pop.get("no_setup") or 0)
                    b01_counts["unknown"] += int(pop.get("unknown") or 0)
                except Exception:
                    pass
            doc = scan_b02(view, branch) if view is not None else scan_b02(None, branch)
            for episode in doc.get("episodes") or []:
                b02_counts["episodes"] += 1
                b02_counts[episode["research_verdict"]] += 1
                collected[branch].append(episode)
    for branch in BRANCHES:
        funnel["branches"][branch]["B0.2"]["stages"] = funnel_stage_counts(collected[branch])
        names = [name for name in STAGE_ORDER if name in funnel["branches"][branch]["B0.2"]["stages"]]
        passes = [funnel["branches"][branch]["B0.2"]["stages"][name]["pass"] for name in names]
        assert passes == sorted(passes, reverse=True)
        if names:
            assert passes[-1] == funnel["branches"][branch]["B0.2"]["pass"]
    (TRACK / "FUNNEL_JJ-TBR.json").write_text(json.dumps(funnel, indent=2) + "\n")

    stats = compute_published_statistics(dates)
    (TRACK / "STATISTICS_JJ.json").write_text(json.dumps(stats, indent=2, default=str) + "\n")
    payload = rules_payload()
    (TRACK / "RULES_JJ-TBR.json").write_text(json.dumps(payload, indent=2) + "\n")
    assert any(row["rule_id"].startswith("RR-01") for row in payload)
    assert all(row.get("file_line", "").startswith("source_adapters/jumbo.py:") for row in payload)
    assert len(replays) == len(examples)
    sep = next(row for row in replays if row["id"] == "JJ-2025-09-09")
    assert sep["detected"] is False
    assert "RR-01" in str(sep.get("level_selection") or sep.get("divergence"))
    assert "far edge" in str(sep.get("level_selection") or sep.get("divergence"))
    hour = stats["measured"]["first_hour_sweep"]
    assert hour["one_side"] == hour["high_only"] + hour["low_only"]
    for loc_row in hour["by_open_location"].values():
        assert loc_row["one_side"] == loc_row["high_only"] + loc_row["low_only"]
