"""Versioned event-time inputs for the method-pack empirical replay.

This is an admission/aggregation layer over the existing owned MBP-1 adapter,
not a second market feed. All quantities refer to the observed execution
population. Unknown feed continuity is retained independently of whether a
quantity can be calculated from that population. Vendor-clock bars never
certify or invalidate an event-time candle.
"""
from __future__ import annotations

from collections import defaultdict
from bisect import bisect_left
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from .empirical_protocol import content_hash
from .mbp1_views import DATASET, TapeError, TradeBars, iter_mbp1_window, plan_window
from .native_resolution import NativeEvidenceError, NativeResolver, file_digest, _stat_signature
from .empirical_tape import _canonical_manifest, _profile_payload, _d
from .protocol import jsonable

SECOND = 1_000_000_000
MINUTE = 60 * SECOND
VERSION = "event-time-observed-v2.0.0"
STANDARD = "https://databento.com/docs/standards-and-conventions/common-fields-enums-types"
CONTRACT = {
    "version": VERSION,
    "population": "all canonically owned physical T rows for the identified instrument/window",
    "clock": "event_ns; half-open buckets; receive time retained separately",
    "known_at": "max(bucket end, retained member availability); event-time assumption when receipt absent",
    "ownership": "existing monthly-primary/disjoint-weekly-fallback MBP-1 ownership",
    "ties": "whole timestamp batches; no physical-order resolution of unequal-price endpoints",
    "vendor_bars": "receive-clock diagnostic only; never inserted into an event-time series",
    "empty": "no candle; scheduled closure and evidenced no-trade distinguished from unknown",
    "continuity": "observed values do not assert exchange-feed completeness",
    "book": "R clears; snapshot resets comparisons; bad-book flags invalidate local book evidence; F_LAST selects completed updates",
    "source": STANDARD,
}


def _hash_row(digest, row):
    digest.update(json.dumps(jsonable(row), sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
    digest.update(b"\n")


def identify_sources(plan, *, frozen_inputs=None):
    """Full-file hashes plus canonical ownership, never a filename-only receipt."""
    root = Path(plan["data_root"])
    canonical = _canonical_manifest(root)
    frozen = None if frozen_inputs is None else {r["path"]: r for r in frozen_inputs}
    identities = []
    for name in sorted({s["path"] for s in plan["owned_spans"]}):
        path = Path(name)
        relative = path.relative_to(root).as_posix()
        member = canonical.get(relative)
        if member is None:
            raise NativeEvidenceError("event source is absent from canonical manifest: " + relative)
        signature = _stat_signature(path)
        if member.get("bytes") not in (None, "") and int(member["bytes"]) != path.stat().st_size:
            raise NativeEvidenceError("canonical event source size changed")
        digest = file_digest(path)
        if signature != _stat_signature(path):
            raise NativeEvidenceError("event source changed while hashing")
        if frozen is not None and (relative not in frozen or frozen[relative]["sha256"] != digest):
            raise NativeEvidenceError("event source differs from frozen input")
        identities.append({"path": relative, "sha256": digest, "bytes": path.stat().st_size,
                           "dataset_id": DATASET, "hash_basis": "full_file_sha256"})
    return identities


class BookObservations:
    """Depth-one changes with no queue/hidden-order inference.

    A reset, snapshot, bad-book flag or uncertain timestamp ordering cuts the
    comparison chain. Even at a constant price an increase is *displayed size
    added*, not proof that the same passive order replenished.
    """
    def __init__(self):
        self.previous = None
        self.batch = []
        self.at = None
        self.rows = []

    def add(self, row):
        out = []
        if self.at is not None and row["event_ns"] != self.at:
            out = self.finish()
        self.at = row["event_ns"]
        self.batch.append(row)
        return out

    def finish(self):
        batch, self.batch = self.batch, []
        if not batch:
            return []
        # Sequence may resolve a batch only when it is complete and unique.
        seq = [r.get("exchange_sequence") for r in batch]
        ordered = all(s is not None for s in seq) and len(set(seq)) == len(seq)
        if ordered:
            batch = sorted(batch, key=lambda r: r["exchange_sequence"])
        bad = any(int(r.get("flags") or 0) & 4 for r in batch)
        reset = any(r.get("action") == "R" or int(r.get("flags") or 0) & 32 for r in batch)
        final = [r for r in batch if int(r.get("flags") or 0) & 128 and r.get("action") != "R"]
        snapshots = {(r.get("bid"), r.get("ask"), r.get("bid_size"), r.get("ask_size")) for r in final}
        chosen = final[-1] if final and (ordered or len(snapshots) == 1) else None
        if bad or reset or chosen is None:
            self.previous = None
        result = {"event_ns": batch[0]["event_ns"], "instrument_id": batch[0]["instrument_id"],
                  "reset": reset, "bad_book": bad, "timestamp_order_known": ordered or len(batch) == 1,
                  "book_depth": 1, "individual_order_identity": None,
                  "known_at": max(r["known_at"] for r in batch),
                  "bid": None, "ask": None, "bid_size": None, "ask_size": None,
                  "bid_added": None, "ask_added": None, "bid_removed": None, "ask_removed": None,
                  "source_rows": [[r["source_file"], r["source_row"]] for r in batch]}
        if chosen is not None and not bad:
            for key in ("bid", "ask", "bid_size", "ask_size"):
                result[key] = chosen.get(key)
            valid = (result["bid"] is not None and result["ask"] is not None
                     and result["bid"] <= result["ask"] and result["bid_size"] is not None
                     and result["ask_size"] is not None and result["bid_size"] >= 0 and result["ask_size"] >= 0)
            if valid:
                if self.previous is not None:
                    for side in ("bid", "ask"):
                        if result[side] == self.previous[side]:
                            change = result[side + "_size"] - self.previous[side + "_size"]
                            result[side + "_added"] = max(0, change)
                            result[side + "_removed"] = max(0, -change)
                self.previous = {k: result[k] for k in ("bid", "ask", "bid_size", "ask_size")}
            else:
                self.previous = None
        return [result]


def interval_state(start, end, bars, *, schedule=None, continuity=()):
    """Return one of four states without inferring quiet from quotes/absence."""
    if bars:
        if schedule is not None and schedule.state(start, end) == "scheduled_closure":
            raise NativeEvidenceError("executions conflict with certified product closure")
        return "observed_executions"
    if schedule is not None and schedule.state(start, end) == "scheduled_closure":
        return "scheduled_closure"
    for receipt in continuity:
        if (receipt.get("kind") == "verified_no_trade" and receipt.get("source_path")
                and receipt.get("source_sha256") and receipt["start_ns"] <= start
                and receipt["end_ns"] >= end):
            path = Path(receipt["source_path"])
            if not path.is_file() or file_digest(path) != receipt["source_sha256"]:
                raise NativeEvidenceError("unverified no-trade continuity receipt")
            evidence = json.loads(path.read_text())
            if (evidence.get("kind") != "verified_no_trade" or evidence.get("start_ns") != receipt["start_ns"]
                    or evidence.get("end_ns") != receipt["end_ns"] or not evidence.get("verification_method")):
                raise NativeEvidenceError("continuity source does not support interval")
            return "evidenced_no_trade"
    return "unknown_coverage"


def aggregate_events(events, start, end, instrument_id, *, seconds=(1, 60, 120, 180, 300, 1800)):
    """Pure causal transformations; useful for real native integration controls."""
    accumulators = {s: TradeBars(s, start, end) for s in seconds}
    bars = {str(s): [] for s in seconds}
    footprints = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    moments = defaultdict(lambda: [Decimal(0), Decimal(0), 0, 0])
    membership = sha256()
    count = 0
    first = last = None
    flags = defaultdict(int)
    physical = set()
    for row in events:
        if row["action"] != "T":
            continue
        at = row["event_ns"]
        if not start <= at < end or str(row["instrument_id"]) != str(instrument_id):
            raise NativeEvidenceError("foreign event in admitted window")
        if last is not None and at < last:
            raise NativeEvidenceError("event stream is not chronological")
        key = row["source_file"], row["source_row"]
        if key in physical:
            raise NativeEvidenceError("duplicate physical event")
        physical.add(key)
        price, size = row["price"], row["executed_size"]
        if price is None or not price.is_finite() or type(size) is not int or size < 0:
            raise NativeEvidenceError("invalid execution value")
        if row.get("side") not in {"A", "B", "N"}:
            raise NativeEvidenceError("unknown native aggressor encoding")
        first = at if first is None else first
        last = at
        count += 1
        flags[str(int(row.get("flags") or 0))] += 1
        _hash_row(membership, {k: row.get(k) for k in
            ("source_file", "source_row", "event_ns", "instrument_id", "price", "executed_size", "side", "flags", "exchange_sequence", "ts_recv")})
        for s, acc in accumulators.items():
            bars[str(s)].extend(acc.add(row))
        minute = at // MINUTE * MINUTE
        footprints[minute][price][{"B": 0, "A": 1, "N": 2}[row["side"]]] += size
        moments[minute][0] += price * size
        moments[minute][1] += price * price * size
        moments[minute][2] += size
        moments[minute][3] = max(moments[minute][3], row["known_at"])
    for s, acc in accumulators.items():
        bars[str(s)].extend(acc.finish())
    for series in bars.values():
        for bar in series:
            bar.update(start=bar["start_ns"], end=bar["end_ns"],
                       bar_id=f"{VERSION}:{instrument_id}:{bar['start_ns']}:{bar['end_ns']}",
                       observed_complete=bar["full_bar_requested"] and bar["invalid_trade_count"] == 0,
                       complete=bar["full_bar_requested"] and bar["invalid_trade_count"] == 0
                                and bar["open_order_known"] and bar["close_order_known"],
                       feed_complete=None, clock_contract=VERSION)
    return {"bars": bars, "footprints": [
        {"start": at, "end": at + MINUTE, "known_at": max(at + MINUTE, moments[at][3]),
         "instrument_id": instrument_id, "pv": moments[at][0], "p2v": moments[at][1],
         "volume": moments[at][2], "rows": [[p, *v] for p, v in sorted(levels.items())]}
        for at, levels in sorted(footprints.items())],
        "membership_sha256": membership.hexdigest(), "row_count": count,
        "first_event_ns": first, "last_event_ns": last, "flags": dict(flags)}


def build_event_window(data_root, start, end, instrument_id, *, ownership=None, frozen_inputs=None,
                       seconds=(1, 60, 120, 180, 300, 1800)):
    plan = plan_window(data_root, start, end, ownership=ownership)
    if any("DATA_OVERLAP" in str(r.get("reason")) for r in plan["holes"]):
        raise NativeEvidenceError("unresolved canonical ownership overlap")
    identities = identify_sources(plan, frozen_inputs=frozen_inputs)
    signatures = {str(Path(data_root) / r["path"]): _stat_signature(Path(data_root) / r["path"])
                  for r in identities}
    result = aggregate_events(iter_mbp1_window(plan, trades_only=True, instrument_id=instrument_id),
                              start, end, instrument_id, seconds=seconds)
    for path, before in signatures.items():
        if _stat_signature(Path(path)) != before:
            raise NativeEvidenceError("event input changed during aggregation")
    result.update(schema=VERSION, contract=CONTRACT, contract_sha256=content_hash(CONTRACT),
                  instrument_id=instrument_id, start_ns=start, end_ns=end,
                  source_files=identities, plan=plan, raw_sources_unchanged=True,
                  market_coverage_complete=None)
    result["input_sha256"] = content_hash({"sources": identities, "ownership": plan["ownership_sha256"],
        "membership": result["membership_sha256"], "contract": CONTRACT,
        "instrument_id": instrument_id, "start": start, "end": end, "seconds": list(seconds)})
    return result


def vendor_diagnostics(event_bars, vendor_bars):
    """Cross-clock differences are diagnostics; no acceptance bit is returned."""
    event = {r.get("start", r.get("start_ns")): r for r in event_bars}
    vendor = {}
    for row in vendor_bars:
        key = row.get("start", row.get("start_ns"))
        if key in vendor:
            raise NativeEvidenceError("duplicate vendor bar identity")
        vendor[key] = row
    rows = []
    for at in sorted(event.keys() | vendor.keys()):
        a, b = event.get(at), vendor.get(at)
        diff = {}
        for key in "OHLCV":
            x, y = (None if a is None else a.get(key)), (None if b is None else b.get(key))
            diff[key] = None if x is None or y is None else _d(x) - _d(y)
        rows.append({"minute_start": at, "event_present": a is not None, "vendor_present": b is not None,
                     "event_minus_vendor": diff})
    return {"event_clock": "event_ns", "vendor_clock": "receive_time",
            "purpose": "diagnostic_only", "rows": rows,
            "different_minutes": sum(any(v not in (None, 0) for v in r["event_minus_vendor"].values()) for r in rows)}


class EventWindow:
    """Prefix-only candles, executed profiles, VWAP, delta and TPO.

    Coverage holes do not erase the observed subset. Consumers explicitly ask
    whether a prefix's scope is known before treating an absence as failure.
    """
    def __init__(self, document, *, schedule=None, continuity=()):
        if document.get("schema") != VERSION or document.get("contract_sha256") != content_hash(CONTRACT):
            raise NativeEvidenceError("unrecognized event-time admission contract")
        self.document = document
        self.instrument_id = document["instrument_id"]
        self.start = document["start_ns"]
        self.end = document["end_ns"]
        self.schedule, self.continuity = schedule, tuple(continuity)
        self.series = {int(s): {r["start"]: r for r in rows} for s, rows in document["bars"].items()}
        self.keys = {s: sorted(rows) for s, rows in self.series.items()}
        self.footprints = {r["start"]: r for r in document["footprints"]}

    def bars(self, start, end, seconds=60):
        if start < self.start or end > self.end or end <= start:
            raise NativeEvidenceError("event prefix outside admitted window")
        keys = self.keys.get(seconds, [])
        return [r for at in keys[bisect_left(keys, start):bisect_left(keys, end)]
                if (r := self.series[seconds][at])["end"] <= end and r["known_at"] <= end]

    def coverage(self, start, end):
        if start < self.start or end > self.end:
            return {"observed_scope_complete": False, "market_coverage_complete": None,
                    "unknown_intervals": [[start, end]], "states": {}}
        states = defaultdict(int)
        holes = []
        for at in range(start // MINUTE * MINUTE, end, MINUTE):
            lo, hi = max(start, at), min(at + MINUTE, end)
            row = self.series.get(60, {}).get(at)
            state = interval_state(lo, hi, [] if row is None else [row],
                                   schedule=self.schedule, continuity=self.continuity)
            unowned = self.document.get('plan', {}).get('unowned_intervals', [])
            def intersects(span):
                a,b=(span.get('start_ns'),span.get('end_ns')) if isinstance(span,dict) else span
                return a is not None and b is not None and a < hi and b > lo
            if state != 'scheduled_closure' and (any(intersects(span) for span in unowned)
                    or lo != at or hi != at + MINUTE
                    or row is not None and (not row['observed_complete'] or row['known_at'] > end)):
                state = 'unknown_coverage'
            states[state] += 1
            if state == "unknown_coverage":
                holes.append([lo, hi])
        return {"observed_scope_complete": not holes, "market_coverage_complete": None,
                "unknown_intervals": holes, "states": dict(states)}

    def profile(self, start, end, *, tick=Decimal(".25"), kind="selected_range"):
        accum = defaultdict(lambda: [Decimal(0), Decimal(0), Decimal(0)])
        members = []
        for at, row in self.footprints.items():
            if start <= at and row["end"] <= end and row["known_at"] <= end:
                members.append(at)
                for price, buy, sell, unknown in row["rows"]:
                    for i, value in enumerate((buy, sell, unknown)):
                        accum[_d(price)][i] += _d(value)
        coverage = self.coverage(start, end)
        result = _profile_payload(accum, tick=tick, tie_policy="lowest",
            value_area={"fraction": Decimal(".70"), "algorithm": "contiguous_larger_adjacent_volume_tie_both", "tie_policy": "both"},
            complete=coverage["observed_scope_complete"])
        result.update(profile_id=f"{VERSION}:{self.instrument_id}:{start}:{end}",
            kind=kind, formation_start=start, formation_end=end, known_at=end,
            instrument_id=self.instrument_id, coverage=coverage, minute_members=members)
        return result

    def vwap(self, start, end):
        rows = [r for at, r in self.footprints.items() if start <= at and r["end"] <= end and r["known_at"] <= end]
        volume = sum(r["volume"] for r in rows)
        pv = sum((_d(r["pv"]) for r in rows), Decimal(0))
        p2v = sum((_d(r["p2v"]) for r in rows), Decimal(0))
        price = pv / volume if volume else None
        variance = max(Decimal(0), p2v / volume - price * price) if volume else None
        return {"price": price, "variance": variance, "sd": variance.sqrt() if variance is not None else None,
                "volume": volume, "reset_at": start, "known_at": end,
                "basis": "execution_price_volume_event_time", "coverage": self.coverage(start, end)}
