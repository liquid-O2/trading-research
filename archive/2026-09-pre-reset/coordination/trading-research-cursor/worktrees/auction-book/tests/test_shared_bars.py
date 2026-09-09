from dataclasses import asdict, replace
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import resource
import time
import unittest
from zoneinfo import ZoneInfo

from references.shared_bars_literal import literal_activity, literal_coarse, literal_summary, literal_windows
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import ActivityBars, BarEngine, Watermark, WindowCoverage
from trading_research.foundations.multiresolution import (
    BarDefinition, BarDomain, BarLimits, CoarseBar, OpportunityWitness, QuantityObservation,
    QuotePoint, ResetMarker, SharedBarEngine, TradeAllocation, AllocationPlan, WindowRequest, allocate_trade, coarse_contact_facts,
    confirm_final_bars, count_mature_opportunities, disjoint_trade_volume, empty_summary,
    merge_coarse_bars, merge_summaries, opportunity_witness, quote_bar, summarize,
    unique_quantity_observations,
)
from trading_research.foundations.units import Ticks
from trading_research.measurements.tape import Trade, TradeLedger
from trading_research.operations.artifacts import canonical_json


GOLD = json.loads((Path(__file__).parent / "golden/f09-shared-bars.json").read_text())
CASES = {c["id"]: c for c in GOLD["cases"]}
ENGINEERING_METRICS = {}
DOMAIN = BarDomain("TEST-H26", "registered-whole-print", "registered-whole-print")
TIME = BarDefinition(DOMAIN, "time-v1", "explicit-calendar-v1", "epoch-0")


def trade(id, at, price=100, size=1, side=1, *, known=None, order=1, complete=True):
    return Trade(id, "content-" + id, DOMAIN.instrument, at, at if known is None else known,
                 None if price is None else Ticks(price), size, side, order, DOMAIN.aggregation_unit, complete)


BASE = tuple(trade(r["id"], r["event_at"], r["price_ticks"], r["contracts"], r["side"],
                   known=r["known_at"], order=r["order"]) for r in GOLD["base_tape"])


def coverage(start=0, end=10, *, known=None, intervals=None, version="coverage-v1"):
    return WindowCoverage(DOMAIN.instrument, start, end, ((start, end),) if intervals is None else intervals,
                          end if known is None else known, version)


def request(definition=TIME, start=0, end=10, *, cov=None, watermark=True):
    return WindowRequest(definition.id, start, end, cov or coverage(start, end),
                         Watermark(end, end, "watermark-v1") if watermark is True else watermark or None)


def engine(rows=BASE, definitions=(TIME,), *, block=2, maximum=4096, publications=4096):
    result = SharedBarEngine(DOMAIN, definitions,
                            limits=BarLimits(maximum, max(32, len(definitions)), block, publications))
    result.add_many(rows)
    return result


def numeric(summary):
    keys = ("event_ids", "content_versions", "first_at", "last_at", "open_ticks", "high_ticks", "low_ticks",
            "close_ticks", "volume", "priced_volume", "unpriced_volume", "sum_pv", "sum_p2v", "buy", "sell",
            "unknown", "signed", "prints", "history_complete", "order_exact", "signed_bounds",
            "cvd_high", "cvd_low", "minimum_known_at")
    return {k: getattr(summary, k) for k in keys}


class SharedBarTests(unittest.TestCase):
    def assertLiteral(self, value, rows):
        self.assertEqual(numeric(value), literal_summary([r.record() for r in rows]))

    def activity(self, rows, *, kind, threshold, resets=(), opening=0):
        definition = BarDefinition(DOMAIN, "activity-v1", "explicit-calendar-v1", "epoch-0", kind, threshold)
        e = engine(rows, (definition,))
        cut = max([*(t.known_at for t in rows), *(r.known_at for r in resets), *(r.event_at for r in resets)], default=0)
        actual = e.publish_activity(e.capture(cut), definition.id, published_at=cut, resets=resets, opening_cvd=opening)
        expected = literal_activity([r.record() for r in rows], kind=kind, threshold=threshold,
                                    initial_epoch="epoch-0", resets=tuple(asdict(r) for r in resets), opening=opening)
        self.assertEqual((actual.available, actual.reason), (expected["available"], expected["reason"]))
        self.assertEqual(len(actual.completed), len(expected["completed"]))
        actual_bars = actual.completed + (() if actual.forming is None else (actual.forming,))
        expected_bars = expected["completed"] + ([] if expected["forming"] is None else [expected["forming"]])
        for a, b in zip(actual_bars, expected_bars):
            self.assertEqual(numeric(a.summary), b["summary"])
            for key in ("state", "threshold_reached", "overshoot", "opening_cvd", "reset_epoch", "interval", "index", "minimum_known_at"):
                self.assertEqual(getattr(a, key), b[key])
            self.assertEqual((a.observation_cut, a.published_at, a.revision), (cut, cut, 0))
            self.assertEqual(a.definition, definition)
            self.assertEqual(a.prefix_id, actual.prefix_id)
            self.assertEqual(a.correction_ids, ())
            self.assertEqual(a.block_ids, e.capture(cut).block_ids)
        self.assertEqual(actual.forming is None, expected["forming"] is None)
        if actual.forming is not None:
            self.assertEqual(numeric(actual.forming.summary), expected["forming"]["summary"])
        self.assertEqual(SharedBarEngine.restore(e.checkpoint()).checkpoint(), e.checkpoint())
        return e, definition, actual

    def test_b01_exact_price_volume_and_cvd(self):
        g = CASES["F09-B01"]["expected"]
        s = summarize(BASE[:3], DOMAIN)
        self.assertLiteral(s, BASE[:3])
        self.assertEqual((s.open_ticks, s.high_ticks, s.low_ticks, s.close_ticks), tuple(g["ohlc_ticks"]))
        self.assertEqual(s.cvd_ohlc(), tuple(g["cvd_ohlc"]))
        self.assertEqual((s.volume, s.prints, s.priced_volume, s.sum_pv, s.sum_p2v),
                         (g["volume"], g["source_events"], g["priced_volume"], g["sum_pv"], g["sum_p2v"]))
        self.assertEqual(s.mean, Fraction(707, 7))
        self.assertEqual(s.variance, Fraction(71413, 7) - Fraction(707, 7) ** 2)

    def test_b02_same_endpoint_different_extrema(self):
        answers = []
        for path in CASES["F09-B02"]["input"]["increment_paths"]:
            rows = tuple(trade(str(i), i + 1, size=abs(v), side=1 if v > 0 else -1) for i, v in enumerate(path))
            s = summarize(rows, DOMAIN)
            self.assertLiteral(s, rows)
            answers.append(s.cvd_ohlc())
        self.assertEqual(answers, [tuple(v) for v in CASES["F09-B02"]["expected"]["cvd_ohlc"]])

    def test_b03_associative_ordered_composition(self):
        a, b, c = [summarize((t,), DOMAIN) for t in BASE[:3]]
        x = merge_summaries(merge_summaries(a, b), c)
        y = merge_summaries(a, merge_summaries(b, c))
        self.assertEqual(x.record(), y.record())
        self.assertLiteral(x, BASE[:3])
        with self.assertRaises(ContractError):
            merge_summaries(c, a)
        with self.assertRaises(ContractError):
            merge_summaries(a, a)
        with self.assertRaises(ContractError):
            merge_summaries(replace(a, volume=999), b)

    def test_b04_ambiguous_boundary_ties(self):
        rows = (trade("x", 5, 100, 2, 1, order=None), trade("y", 5, 110, 3, -1, order=None))
        for block in (1, 2):
            e = engine(rows, block=block)
            s, _, _ = e.query(e.capture(5), start=0, end=10)
            self.assertLiteral(s, rows)
            self.assertEqual((s.open_ticks, s.close_ticks, s.high_ticks, s.low_ticks, s.volume, s.signed),
                             (None, None, 110, 100, 5, -1))
            self.assertFalse(s.order_exact)
            self.assertIsNone(s.cvd_high)
            self.assertIsNone(s.cvd_low)
        _, _, bars = self.activity(rows, kind="events", threshold=1)
        self.assertFalse(bars.available)
        same = tuple(replace(r, price=Ticks(100)) for r in rows)
        self.assertEqual((summarize(same, DOMAIN).open_ticks, summarize(same, DOMAIN).close_ticks), (100, 100))

    def test_b05_unpriced_unknown_and_missing_history(self):
        rows = (trade("x", 1, 100, 2, 1), trade("y", 2, None, 3, None))
        s = summarize(rows, DOMAIN)
        self.assertLiteral(s, rows)
        self.assertEqual((s.volume, s.priced_volume, s.unpriced_volume, s.sum_pv, s.sum_p2v, s.signed, s.unknown),
                         (5, 2, 3, 200, 20000, 2, 3))
        self.assertEqual(s.signed_bounds, (-1, 5))
        self.assertIsNone(s.cvd_ohlc())
        gap = summarize((replace(rows[0], history_complete=False), rows[1]), DOMAIN)
        self.assertIsNone(gap.signed_bounds)

    def test_b06_whole_event_count(self):
        _, _, r = self.activity(BASE[:3], kind="events", threshold=2)
        self.assertEqual([(v.summary.event_ids, v.summary.volume) for v in r.completed], [(('a', 'b'), 3)])
        self.assertEqual((r.forming.summary.event_ids, r.forming.summary.volume), (('c',), 4))

    def test_b07_whole_event_volume_overshoot(self):
        rows = (trade("big", 1, size=12), trade("next", 2, size=1))
        _, _, r = self.activity(rows, kind="volume", threshold=5)
        self.assertEqual([(v.summary.volume, v.summary.prints, v.overshoot) for v in r.completed], [(12, 1, 7)])
        self.assertEqual((r.forming.summary.volume, sum(v.summary.prints for v in r.completed) + r.forming.summary.prints), (1, 2))

    def test_b08_range_crossing_and_unavailable_prices(self):
        _, _, r = self.activity(BASE, kind="range", threshold=3)
        self.assertEqual([v.summary.event_ids for v in r.completed], [('a', 'b')])
        self.assertEqual(r.completed[0].overshoot, 0)
        self.assertEqual((r.forming.summary.event_ids, r.forming.summary.high_ticks - r.forming.summary.low_ticks), (('c', 'd'), 2))
        _, _, missing = self.activity((replace(BASE[0], price=None), BASE[1]), kind="range", threshold=3)
        self.assertFalse(missing.available)

    def test_b09_explicit_reset_partial(self):
        rows = (trade("before", 1, size=3), trade("after", 3, size=2))
        _, _, r = self.activity(rows, kind="volume", threshold=5,
                                resets=(ResetMarker("boundary", 2, 2, "epoch-1"),))
        self.assertEqual((r.completed[0].summary.volume, r.completed[0].threshold_reached,
                          r.completed[0].state, r.forming.summary.volume), (3, False, 'reset_partial', 2))
        self.assertEqual((r.completed[0].reset_epoch, r.forming.reset_epoch), ("epoch-0", "epoch-1"))

    def test_b10_immutable_complete_definition(self):
        d = BarDefinition(DOMAIN, "v1", "calendar", "reset", "volume", 5)
        e = engine((trade("forming", 1, size=2),), (d,))
        for name, value in (("threshold", 3), ("calendar_id", "another"), ("reset_id", "later")):
            with self.assertRaises(AttributeError):
                setattr(d, name, value)
        with self.assertRaises(AttributeError):
            e.limits = BarLimits()
        with self.assertRaises(AttributeError):
            e.definitions = (replace(d, threshold=3),)
        for name in ("_domain", "_definitions", "_limits"):
            with self.assertRaises(AttributeError):
                setattr(e, name, getattr(e, name))
            with self.assertRaises(AttributeError):
                delattr(e, name)
        changed = replace(d, threshold=3)
        self.assertNotEqual(d.id, changed.id)
        with self.assertRaises(ContractError):
            e.publish_activity(e.capture(1), changed.id, published_at=1)
        for change in (replace(DOMAIN, measurement="another"), replace(DOMAIN, instrument="ANOTHER")):
            self.assertNotEqual(replace(d, domain=change).id, d.id)

    def test_b11_atomic_duplicates_conflicts_and_capacity(self):
        e = engine(BASE[:1], maximum=2, block=1)
        before = e.checkpoint()
        self.assertEqual(e.add_many(BASE[:1]), 0)
        self.assertEqual(e.checkpoint(), before)
        for batch, error in (((replace(BASE[0], size=9),), IntegrityError),
                             ((BASE[1], BASE[2]), ContractError),
                             ((BASE[1], replace(BASE[1], size=9)), IntegrityError)):
            with self.assertRaises(error):
                e.add_many(batch)
            self.assertEqual(e.checkpoint(), before)
        e.add(BASE[1])
        before = e.checkpoint()
        with self.assertRaises(ContractError):
            e.correct(id="capacity", original_id="b", known_at=20, reason="fix", replacement=trade("b2", 2, known=20))
        self.assertEqual(e.checkpoint(), before)

    def test_b12_half_open_first_actual_print(self):
        e = engine()
        bar = e.publish_window(e.capture(12), request(), published_at=13)
        self.assertEqual(bar.summary.event_ids, ('a', 'b', 'c'))
        self.assertEqual(bar.summary.first_at, 1)
        self.assertLiteral(bar.summary, BASE[:3])
        other, _, _ = e.query(e.capture(12), start=10, end=20)
        self.assertEqual(other.event_ids, ('d',))

    def test_b13_actual_final_publication_clock(self):
        e = engine(BASE[:3])
        forming = e.publish_window(e.capture(9), request(cov=coverage(known=9, intervals=((0, 9),)), watermark=False), published_at=9)
        final = e.publish_window(e.capture(12), request(watermark=Watermark(10, 12, 'w12')), published_at=13)
        self.assertFalse(forming.final)
        self.assertEqual([final.available(c) for c in (9, 10, 12, 13)], [False, False, False, True])
        self.assertEqual((final.minimum_known_at, final.published_at, final.interval), (12, 13, (0, 10)))
        with self.assertRaises(ContractError):
            e.publish_window(e.capture(20), request(), published_at=19)

    def test_b14_empty_missing_and_unfinished(self):
        e = engine(())
        final = e.publish_window(e.capture(12), request(start=5, end=10), published_at=13)
        self.assertTrue(final.final and final.coverage_complete)
        self.assertEqual((final.summary.open_ticks, final.summary.high_ticks, final.summary.low_ticks, final.summary.close_ticks), (None,) * 4)
        self.assertEqual(final.summary.volume, 0)
        missing = e.publish_window(e.capture(14), request(start=5, end=10, cov=coverage(5, 10, intervals=())), published_at=14)
        self.assertFalse(missing.coverage_complete)
        other = engine(())
        unfinished = other.publish_window(other.capture(8), request(start=5, end=10, cov=coverage(5, 10, known=8, intervals=((5, 8),)), watermark=False), published_at=8)
        self.assertFalse(unfinished.final)

    def test_b15_correction_versions_and_unaffected_blocks(self):
        e = engine(BASE[:3], block=1)
        capture = e.capture(12)
        old = e.publish_window(capture, request(), published_at=13)
        replacement = trade("b2", 2, 104, 2, -1, known=20)
        e.correct(id="fix-b", original_id="b", known_at=20, reason="source correction", replacement=replacement)
        new_capture = e.capture(20)
        current = e.publish_window(new_capture, request(), published_at=21)
        self.assertEqual((old.summary.volume, old.summary.sum_pv, old.summary.signed), (7, 707, 5))
        self.assertEqual((current.summary.volume, current.summary.sum_pv, current.summary.sum_p2v, current.summary.signed), (8, 812, 82436, 4))
        self.assertEqual(current.correction_ids, ('fix-b',))
        self.assertEqual(e.asof(bar_id=old.bar_id, cut=19), old)
        self.assertEqual(capture.blocks[0].id, new_capture.blocks[0].id)
        self.assertEqual(capture.blocks[2].id, new_capture.blocks[2].id)
        self.assertNotEqual(capture.blocks[1].id, new_capture.blocks[1].id)
        self.assertLiteral(current.summary, (BASE[0], replacement, BASE[2]))

    def test_b16_future_suffix_does_not_change_old_prefix(self):
        e = engine(BASE[:3])
        early_capture = e.capture(12)
        original = e.publish_window(early_capture, request(), published_at=13)
        before = e.checkpoint()
        e.add(trade("late", 4, 999, 2, known=30))
        reconstructed = e.capture(12)
        self.assertEqual(reconstructed.prefix_id, early_capture.prefix_id)
        fresh = engine(BASE[:3])
        fresh.add(trade("late", 4, 999, 2, known=30))
        same = fresh.publish_window(fresh.capture(12), request(), published_at=13)
        self.assertEqual(same.version_id, original.version_id)
        self.assertNotEqual(same.admission_cursor, original.admission_cursor)
        e.correct(id="future-delete", original_id="late", known_at=30, reason="future correction")
        self.assertEqual(e.capture(12).prefix_id, early_capture.prefix_id)
        later = e.publish_window(e.capture(30), request(), published_at=31)
        self.assertNotEqual(original.version_id, later.version_id)
        self.assertEqual(e.asof(bar_id=original.bar_id, cut=20), original)
        replay = SharedBarEngine.restore(before)
        self.assertEqual(replay.asof(bar_id=original.bar_id, cut=20), original)

    def test_b17_restore_recomputes_publications_and_saved_cursor(self):
        e = engine(BASE[:3])
        saved = e.capture(12)
        e.add(trade("same-cut-later-admission", 4, 105, known=12))
        original = e.publish_window(saved, request(), published_at=13)
        checkpoint = e.checkpoint()
        restored = SharedBarEngine.restore(checkpoint, expected_domain=DOMAIN, expected_definitions=(TIME,), expected_limits=e.limits)
        self.assertEqual(restored.checkpoint(), checkpoint)
        self.assertEqual(restored.asof(bar_id=original.bar_id, cut=13).summary.prints, 3)
        for actual in (e, restored):
            actual.add(trade("suffix", 6, 108, known=15))
            actual.publish_window(actual.capture(15), request(), published_at=16)
        self.assertEqual(e.checkpoint(), restored.checkpoint())
        p = json.loads(checkpoint)
        variants = []
        for path in ("summary", "event_order", "threshold", "publication", "lineage"):
            bad = json.loads(checkpoint)
            if path == "summary": bad['history'][-1]['expected']['summary']['volume'] += 1
            elif path == "event_order": bad['history'][0]['trades'][0]['order'] = 7
            elif path == "threshold": bad['definitions'][0]['threshold'] = 2
            elif path == "publication": bad['history'][-1]['published_at'] = 11
            else: bad['history'][-1]['expected']['prefix_id'] = 'wrong'
            variants.append(bad)
        for bad in variants:
            with self.assertRaises((ContractError, IntegrityError)):
                SharedBarEngine.restore(canonical_json(bad), expected_definitions=(TIME,))

    def test_b18_no_splitting_opaque_coarse_bar(self):
        coarse = CoarseBar("x", "v", DOMAIN.instrument, DOMAIN.measurement, 8, 12, 12, True, (100, 110, 90, 105), 4)
        args = dict(instrument=DOMAIN.instrument, measurement=DOMAIN.measurement, start=0, end=10, cut=20)
        with self.assertRaises(DependencyUnavailable):
            merge_coarse_bars((coarse,), **args)
        whole = merge_coarse_bars((coarse,), **{**args, "start": 8, "end": 12})
        self.assertEqual((whole.ohlc, whole.volume, whole.coverage_complete), ((100, 110, 90, 105), 4, True))

    def test_b19_identical_values_separate_intervals(self):
        rows = (trade('first', 1), trade('second', 6))
        e = engine(rows)
        a = e.publish_window(e.capture(10), request(start=0, end=5), published_at=10)
        b = e.publish_window(e.capture(10), request(start=5, end=10), published_at=10)
        self.assertEqual((a.summary.open_ticks, a.summary.volume), (b.summary.open_ticks, b.summary.volume))
        self.assertNotEqual(a.bar_id, b.bar_id)
        self.assertFalse(e.add(rows[0]))
        self.assertEqual(e.event_count, 2)

    def test_b20_quotes_are_distinct_measurements(self):
        rows = (QuotePoint('q1', 'v1', DOMAIN.instrument, 1, 1, 100, 102),
                QuotePoint('q2', 'v2', DOMAIN.instrument, 2, 2, 99, 101))
        bar = quote_bar(rows, instrument=DOMAIN.instrument, definition_id='own-BBO', start=0, end=3, cut=3, published_at=3)
        self.assertEqual(bar.bid_ohlc, (100, 100, 99, 99))
        self.assertEqual(bar.ask_ohlc, (102, 102, 101, 101))
        self.assertIsNone(bar.traded_volume)
        self.assertIsNone(bar.cvd)
        with self.assertRaises(ContractError):
            engine(()).add(rows[0])

    def test_b21_coarse_side_totals_do_not_reconstruct_path(self):
        b = CoarseBar('coarse', 'v', DOMAIN.instrument, DOMAIN.measurement, 0, 10, 10, True, (100, 101, 99, 100), 10, 5, 5, 0)
        value = merge_coarse_bars((b,), instrument=DOMAIN.instrument, measurement=DOMAIN.measurement, start=0, end=10, cut=10)
        self.assertEqual(value.signed_endpoint, 0)
        self.assertIsNone(value.cvd_high)
        self.assertIsNone(value.cvd_low)
        unknown = replace(b, buy=3, sell=2, unknown=5)
        uncertain = merge_coarse_bars((unknown,), instrument=DOMAIN.instrument, measurement=DOMAIN.measurement, start=0, end=10, cut=10)
        self.assertIsNone(uncertain.signed_endpoint)
        self.assertEqual((uncertain.known_signed_mass, uncertain.unknown_mass, uncertain.signed_bounds), (1, 5, (-4, 6)))

    def test_b22_oi_and_daily_cumulative_are_not_trade_mass(self):
        oi = QuantityObservation('oi-day', 'v1', 'OPTION', 'daily_oi_delta', 8, 10)
        self.assertEqual(len(unique_quantity_observations((oi,) * 4)), 1)
        with self.assertRaises(DependencyUnavailable):
            disjoint_trade_volume((oi,) * 4, instrument=DOMAIN.instrument)
        cumulative = tuple(QuantityObservation(f'cum{i}', f'v{i}', DOMAIN.instrument, 'daily_cumulative_volume', q, i + 1) for i, q in enumerate((3, 7)))
        with self.assertRaises(DependencyUnavailable):
            disjoint_trade_volume(cumulative, instrument=DOMAIN.instrument)
        source = CoarseBar('c', 'v', DOMAIN.instrument, 'other-filter', 0, 10, 10, True, (100,) * 4, 1)
        with self.assertRaises(ContractError):
            merge_coarse_bars((source,), instrument=DOMAIN.instrument, measurement=DOMAIN.measurement, start=0, end=10, cut=10)

    def test_b23_allocations_conserve_one_original_event(self):
        original = trade('big', 1, size=12, known=2)
        plan = allocate_trade(original, (5, 5, 2))
        self.assertEqual((sum(p.size for p in plan.parts), plan.independent_source_events), (12, 1))
        self.assertEqual({p.known_at for p in plan.parts}, {2})
        for sizes in ((5, 5), (5, 5, 3), (12, 0)):
            with self.assertRaises(ContractError):
                allocate_trade(original, sizes)
        with self.assertRaises(ContractError):
            engine(()).add(plan.parts[0])

    def test_b24_constituent_bodies_survive_only_with_evidence(self):
        bars = tuple(CoarseBar(f'b{i}', f'v{i}', DOMAIN.instrument, DOMAIN.measurement, i, i + 1, i + 1, True,
                              prices, 1, body_envelope=(min(prices[0], prices[3]), max(prices[0], prices[3])))
                     for i, prices in enumerate(((100, 111, 99, 110), (110, 112, 99, 100))))
        aggregate = merge_coarse_bars(bars, instrument=DOMAIN.instrument, measurement=DOMAIN.measurement, start=0, end=2, cut=2)
        literal = literal_coarse([asdict(b) for b in bars])
        self.assertEqual((aggregate.ohlc, aggregate.body_envelope), (literal['ohlc'], literal['body_envelope']))
        self.assertEqual(aggregate.ohlc, (100, 112, 99, 100))
        self.assertEqual(aggregate.require_body_envelope(), (100, 110))
        self.assertEqual(abs(aggregate.ohlc[3] - aggregate.ohlc[0]), 0)
        opaque = CoarseBar('aggregate', 'v', DOMAIN.instrument, DOMAIN.measurement, 0, 2, 2, True, aggregate.ohlc, 2)
        view = merge_coarse_bars((opaque,), instrument=DOMAIN.instrument, measurement=DOMAIN.measurement, start=0, end=2, cut=2)
        with self.assertRaises(DependencyUnavailable):
            view.require_body_envelope()

    def test_b25_confirmation_and_estimators_remain_distinct(self):
        e = engine((trade('anchor', 1), trade('right1', 2), trade('right2', 3)))
        first = e.publish_window(e.capture(3), request(start=2, end=3), published_at=3)
        b = e.publish_window(e.capture(4), request(start=3, end=4), published_at=4)
        confirmed = confirm_final_bars((first, b), anchor_at=1, cut=4, published_at=4, definition_id='two-right-final', required_bars=2)
        self.assertFalse(confirmed.available(3))
        self.assertTrue(confirmed.available(4))
        self.assertEqual(confirmed.source_versions, (first.version_id, b.version_id))
        for bars in ((b,), (b, b), (b, first)):
            with self.assertRaises(ContractError):
                confirm_final_bars(bars, anchor_at=1, cut=4, published_at=4, definition_id='two-right-final', required_bars=2)
        for statistic in ('quantile', 'changing_anchor_deviation', 'calibrated_probability', '98%'):
            with self.assertRaises(DependencyUnavailable):
                b.summary.statistic(statistic)

    def test_b26_single_matched_resource_comparison(self):
        windows = ((0, 11), (0, 4), (2, 11))
        e = engine()
        capture = e.capture(12)
        literal, visits = literal_windows([t.record() for t in BASE], windows, cut=12)
        shared = tuple(e.query(capture, start=a, end=b)[0] for a, b in windows)
        self.assertEqual(tuple(numeric(s) for s in shared), literal)
        self.assertEqual((visits, capture.source_visits), (12, 4))
        rows = tuple(trade(f'bench-{i}', i + 1, price=100 + i % 17, size=1 + i % 3,
                           side=1 if i % 2 else -1) for i in range(4096))
        ranges = tuple((0, (i + 1) * 512 + 1) for i in range(5))
        clocks = tuple(replace(TIME, version=f'bench-clock-{i}') for i in range(5)) + (
            BarDefinition(DOMAIN, 'bench-events', 'explicit-calendar-v1', 'epoch-0', 'events', 8),
            BarDefinition(DOMAIN, 'bench-volume', 'explicit-calendar-v1', 'epoch-0', 'volume', 32),
            BarDefinition(DOMAIN, 'bench-range', 'explicit-calendar-v1', 'epoch-0', 'range', 3))
        started_wall, started_cpu = time.perf_counter_ns(), time.process_time_ns()
        primitive_rows = [r.record() for r in rows]
        full, full_visits = literal_windows(primitive_rows, ranges, cut=4097)
        literal_activities = tuple(literal_activity(primitive_rows, kind=d.kind, threshold=d.threshold, initial_epoch=d.reset_id)
                                   for d in clocks[5:])
        literal_cpu, literal_wall = time.process_time_ns() - started_cpu, time.perf_counter_ns() - started_wall
        started_wall, started_cpu = time.perf_counter_ns(), time.process_time_ns()
        shared_engine = engine(rows, clocks, block=32)
        snapshot = shared_engine.capture(4097)
        build_cpu, build_wall = time.process_time_ns() - started_cpu, time.perf_counter_ns() - started_wall
        build_work = dict(shared_engine.work)
        started_wall, started_cpu = time.perf_counter_ns(), time.process_time_ns()
        queries = tuple(shared_engine.query(snapshot, start=a, end=b) for a, b in ranges)
        query_cpu, query_wall = time.process_time_ns() - started_cpu, time.perf_counter_ns() - started_wall
        self.assertEqual(tuple(numeric(s) for s, _, _ in queries), full)
        query_work = {k: v - build_work.get(k, 0) for k, v in shared_engine.work.items() if v != build_work.get(k, 0)}
        started_wall, started_cpu = time.perf_counter_ns(), time.process_time_ns()
        activity_outputs = shared_engine.publish_activities(snapshot, tuple(d.id for d in clocks[5:]), published_at=4098)
        activity_cpu, activity_wall = time.process_time_ns() - started_cpu, time.perf_counter_ns() - started_wall
        for actual, expected in zip(activity_outputs, literal_activities):
            values = actual.completed + (() if actual.forming is None else (actual.forming,))
            expected_values = expected['completed'] + ([] if expected['forming'] is None else [expected['forming']])
            self.assertEqual(len(values), len(expected_values))
            self.assertEqual((actual.available, actual.reason), (expected['available'], expected['reason']))
            for value, reference in zip(values, expected_values):
                self.assertEqual(numeric(value.summary), reference['summary'])
                for key in ('state', 'threshold_reached', 'overshoot', 'opening_cvd', 'reset_epoch', 'interval', 'index', 'minimum_known_at'):
                    self.assertEqual(getattr(value, key), reference[key])
                self.assertEqual((value.observation_cut, value.published_at, value.prefix_id, value.block_ids, value.correction_ids),
                                 (4097, 4098, snapshot.prefix_id, snapshot.block_ids, ()))
        literal_visits = full_visits + len(clocks[5:]) * len(rows)
        self.assertEqual((literal_visits, snapshot.source_visits), (32768, 4096))
        self.assertEqual(shared_engine.work['activity_source_dispatches'], 4096)
        self.assertEqual(shared_engine.work['activity_clock_compositions'], 3 * 4096)
        self.assertEqual(query_work.get('capture_admitted_trade_records_visited', 0), 0)
        started_wall, started_cpu = time.perf_counter_ns(), time.process_time_ns()
        retained_checkpoint_bytes = len(shared_engine.checkpoint())
        checkpoint_cpu = time.process_time_ns() - started_cpu
        checkpoint_wall = time.perf_counter_ns() - started_wall
        ENGINEERING_METRICS.update({"family": "F09-shared-bar-reference-v1", "case_id": "F09-B26", "repetitions": 1,
            "events": 4096, "clocks": 8, "time_clocks": 5, "activity_clocks": 3,
            "literal_source_visits": literal_visits, "shared_capture_source_visits": snapshot.source_visits,
            "source_visit_scope": "Primitive source arithmetic folds only; all admission/hash/index and lineage-copy work is separately counted.",
            "shared_query_compositions": sum(work for _, _, work in queries),
            "capture_construction_work": build_work, "time_query_work": query_work,
            "activity_work": {k: v for k, v in shared_engine.work.items() if k.startswith('activity_')},
            "literal_wall_ns": literal_wall, "literal_cpu_ns": literal_cpu,
            "shared_build_wall_ns": build_wall, "shared_build_cpu_ns": build_cpu,
            "shared_query_wall_ns": query_wall, "shared_query_cpu_ns": query_cpu,
            "shared_activity_wall_ns": activity_wall, "shared_activity_cpu_ns": activity_cpu,
            "checkpoint_wall_ns": checkpoint_wall, "checkpoint_cpu_ns": checkpoint_cpu,
            "process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "retained_events": shared_engine.event_count, "retained_blocks": len(snapshot.blocks),
            "retained_publications": len(shared_engine.publications),
            "checkpoint_bytes": retained_checkpoint_bytes, "exact_semantic_and_lineage_parity": True,
            "universal_speedup_claim": False, "native_market_evidence": False})

    def test_b27_only_mature_complete_opportunities(self):
        e = engine((trade('a', 1),))
        complete = e.publish_window(e.capture(10), request(), published_at=10)
        missing = e.publish_window(e.capture(10), request(start=10, end=20, cov=coverage(10, 20, known=10, intervals=()), watermark=False), published_at=10)
        witnesses = (opportunity_witness(complete, target_definition='touch-v1', target_end=30, label_known_at=31,
                                        touched=False, observation_process='nonempty_completed_bar'),
                     opportunity_witness(missing, target_definition='touch-v1', target_end=30, label_known_at=31,
                                        touched=False, observation_process='nonempty_completed_bar'))
        final_missing_engine = engine(())
        fm = final_missing_engine.publish_window(final_missing_engine.capture(20), request(start=10, end=20, cov=coverage(10, 20, intervals=())), published_at=20)
        witnesses += (opportunity_witness(fm, target_definition='separate-final-missing-case', target_end=30, label_known_at=31,
                                          touched=False, observation_process='nonempty_completed_bar'),)
        result = count_mature_opportunities(witnesses + (witnesses[0],), cut=31)
        self.assertEqual((result['eligible'], result['successes']), (1, 0))
        conflicting = opportunity_witness(fm, target_definition='touch-v1', target_end=30, label_known_at=31,
                                          touched=False, observation_process='nonempty_completed_bar')
        with self.assertRaises(IntegrityError):
            count_mature_opportunities((witnesses[1], conflicting), cut=31)
        restored = tuple(OpportunityWitness(**w) for w in json.loads(canonical_json(witnesses)))
        self.assertEqual(count_mature_opportunities(restored + restored, cut=31), result)
        self.assertEqual(count_mature_opportunities(witnesses, cut=30)['eligible'], 0)
        empty_engine = engine(())
        empty = empty_engine.publish_window(empty_engine.capture(10), request(), published_at=10)
        for process, expected in (('nonempty_completed_bar', 0), ('completed_calendar_interval', 1)):
            w = opportunity_witness(empty, target_definition='empty-window', target_end=20, label_known_at=20,
                                    touched=False, observation_process=process)
            self.assertEqual(count_mature_opportunities((w,), cut=20)['eligible'], expected)

    def test_b28_explicit_calendar_endpoints_across_dst(self):
        actual = []
        for date, next_date in (((2024, 3, 10), (2024, 3, 11)), ((2024, 11, 3), (2024, 11, 4))):
            start = int(datetime(*date, tzinfo=ZoneInfo('America/New_York')).timestamp()) * 1_000_000_000
            end = int(datetime(*next_date, tzinfo=ZoneInfo('America/New_York')).timestamp()) * 1_000_000_000
            e = engine(())
            r = request(start=start, end=end)
            b = e.publish_window(e.capture(end), r, published_at=end)
            actual.append(b.observed_duration)
            with self.assertRaises(ContractError):
                WindowRequest(TIME.id, start, start + 86_400_000_000_000, r.coverage, r.watermark)
        self.assertEqual(actual, CASES['F09-B28']['expected']['elapsed_ns'])

    def test_b29_presentation_does_not_enter_semantic_identity(self):
        e = engine(BASE[:3])
        bar = e.publish_window(e.capture(12), request(), published_at=13)
        displays = tuple({'presentation': p, 'bar_id': bar.bar_id, 'version': bar.version_id,
                          'numerical': numeric(bar.summary)} for p in ('hidden', 'shown', 'backdrawn'))
        self.assertEqual(len({v['version'] for v in displays}), 1)
        self.assertEqual(displays[0]['numerical'], displays[2]['numerical'])
        for changed in (replace(TIME, calendar_id='other-calendar'), replace(TIME, reset_id='other-reset'),
                        replace(TIME, domain=replace(DOMAIN, measurement='other-measure'))):
            self.assertNotEqual(changed.id, TIME.id)
        restored = SharedBarEngine.restore(e.checkpoint())
        self.assertEqual(restored.asof(bar_id=bar.bar_id, cut=13), bar)

    def test_b30_named_cvd_carry_and_reset(self):
        rows = (trade('first-up', 1, size=5), trade('first-down', 2, size=2, side=-1), trade('next-up', 4, size=2))
        _, _, carried = self.activity(rows, kind='events', threshold=2)
        _, _, reset = self.activity(rows, kind='events', threshold=2, resets=(ResetMarker('at3', 3, 3, 'new-anchor'),))
        self.assertEqual([carried.forming.opening_cvd, reset.forming.opening_cvd], [3, 0])
        self.assertEqual([carried.forming.summary.cvd_ohlc(carried.forming.opening_cvd)[3],
                          reset.forming.summary.cvd_ohlc(reset.forming.opening_cvd)[3]], [5, 2])
        self.assertEqual(carried.completed[0].summary.cvd_high, 5)
        self.assertNotEqual(carried.forming.bar_id, reset.forming.bar_id)
        uncertain_rows = (trade('unknown-first', 1, size=3, side=None), trade('known-next', 3, size=2))
        _, _, uncertain = self.activity(uncertain_rows, kind='events', threshold=1)
        self.assertTrue(uncertain.available)
        self.assertIsNone(uncertain.completed[1].opening_cvd)
        self.assertIsNone(uncertain.completed[1].summary.cvd_ohlc(uncertain.completed[1].opening_cvd))
        _, _, reset_uncertain = self.activity(uncertain_rows, kind='events', threshold=1,
                                             resets=(ResetMarker('known-zero', 2, 2, 'new-zero'),))
        self.assertEqual(reset_uncertain.completed[1].summary.cvd_ohlc(reset_uncertain.completed[1].opening_cvd), (0, 2, 0, 2))

    def test_b31_contact_return_and_order_are_separate(self):
        bars = tuple(CoarseBar(f'b{i}', f'v{i}', DOMAIN.instrument, DOMAIN.measurement, i, i + 1, i + 1, True, prices, 1)
                     for i, prices in enumerate(((102, 106, 99, 101), (101, 102, 99, 100))))
        facts = [coarse_contact_facts(b, level=100, return_anchor=100) for b in bars]
        self.assertEqual([v['inclusive_contact'] for v in facts], [True, True])
        self.assertEqual([v['exact_close_return'] for v in facts], [False, True])
        self.assertTrue(all(v['high_first'] is None and v['intrabar_first_passage_at'] is None for v in facts))

    def test_trade_view_import_retains_correction_scope(self):
        ledger = TradeLedger()
        for t in BASE[:3]: ledger.add(t)
        ledger.correct(id='provider-correction', original_id='b', known_at=20, reason='corrected',
                       replacement=trade('b2', 2, 104, 2, -1, known=20))
        imported = SharedBarEngine.from_trade_view(ledger, DOMAIN, (TIME,), start=0, end=10, cut=20)
        bar = imported.publish_window(imported.capture(20), request(), published_at=21)
        self.assertEqual((bar.summary.volume, bar.correction_ids), (8, ('provider-correction',)))
        restored = SharedBarEngine.restore(imported.checkpoint())
        self.assertEqual(restored.asof(bar_id=bar.bar_id, cut=21), bar)
        with self.assertRaises(ContractError): imported.capture(10)
        with self.assertRaises(ContractError): imported.add(trade('new', 8, known=22))
        with self.assertRaises(DependencyUnavailable): imported.query(imported.capture(20), start=0, end=20)

    def test_legacy_configuration_and_publication_restore_integrity(self):
        legacy = BarEngine(instrument=DOMAIN.instrument, definition_version='fixed')
        for t in BASE[:3]: legacy.add(t)
        bar = legacy.publish(start=0, end=10, cut=12, published_at=13, coverage=coverage(), watermark=Watermark(10, 12, 'w'))
        for name, value in (('instrument', 'OTHER'), ('definition_version', 'changed')):
            with self.assertRaises(AttributeError): setattr(legacy, name, value)
        payload = legacy.checkpoint()
        broken = json.loads(payload)
        key = next(iter(broken['versions']))
        broken['versions'][key][0]['volume'] += 1
        with self.assertRaises(IntegrityError): BarEngine.restore(canonical_json(broken))
        legacy.add(trade('same-old-cut-new-admission', 4, known=12))
        restored = BarEngine.restore(legacy.checkpoint())
        self.assertEqual(restored.asof(start=0, end=10, cut=13), bar)

    def test_legacy_activity_reconstructs_threshold_and_boundary_partition(self):
        legacy = ActivityBars(kind='volume', threshold=5)
        legacy.add(trade('a', 1, size=3))
        legacy.boundary(known_at=2, reason='reset')
        legacy.add(trade('b', 3, size=2))
        for name, value in (('threshold', 3), ('kind', 'events'), ('max_events', 999)):
            with self.assertRaises(AttributeError): setattr(legacy, name, value)
        for field_name, changed in (('threshold_reached', True), ('close_reason', 'not the observed reset')):
            broken = json.loads(legacy.checkpoint())
            broken['completed'][0][field_name] = changed
            with self.assertRaises(IntegrityError): ActivityBars.restore(canonical_json(broken))
        restored = ActivityBars.restore(legacy.checkpoint())
        for state in (legacy, restored):
            bar = state.add(trade('c', 4, size=4))
            self.assertEqual((bar.volume, bar.event_ids), (6, ('b', 'c')))
        self.assertEqual(legacy.checkpoint(), restored.checkpoint())

    def test_shared_activity_revision_and_atomic_boundaries(self):
        definition = BarDefinition(DOMAIN, 'revision-test', 'calendar', 'reset', 'events', 1)
        e = engine(BASE[:2], (definition,))
        saved = e.capture(12)
        first = e.publish_activity(saved, definition.id, published_at=13)
        e.correct(id='replace-a', original_id='a', known_at=20, reason='correction', replacement=trade('a2', 1, 105, known=20))
        current = e.publish_activity(e.capture(20), definition.id, published_at=21)
        self.assertTrue(all(b.revision == 1 and b.correction_ids == ('replace-a',) for b in current.completed))
        self.assertEqual(first.completed[0].summary.open_ticks, 100)
        before = e.checkpoint()
        with self.assertRaises(ContractError):
            e.publish_activity(saved, definition.id, published_at=22)
        self.assertEqual(e.checkpoint(), before)
        restored = SharedBarEngine.restore(before)
        for state in (e, restored):
            state.add(trade('suffix', 5, 104, known=25))
            state.publish_activity(state.capture(25), definition.id, published_at=26)
        self.assertEqual(e.checkpoint(), restored.checkpoint())
        corrupted = json.loads(before)
        corrupted['history'][-1]['expected'][0]['completed'][0]['opening_cvd'] = 999
        with self.assertRaises(IntegrityError):
            SharedBarEngine.restore(canonical_json(corrupted))
        tied = engine((trade('one', 1, known=10),), (definition,))
        old = tied.capture(10)
        tied.add(trade('two', 2, known=10))
        tied.publish_activity(tied.capture(10), definition.id, published_at=11)
        before = tied.checkpoint()
        with self.assertRaises(ContractError):
            tied.publish_activity(old, definition.id, published_at=12)
        self.assertEqual(tied.checkpoint(), before)
        limited = engine(BASE[:2], (definition,), publications=1)
        before = limited.checkpoint()
        with self.assertRaises(ContractError):
            limited.publish_activity(limited.capture(12), definition.id, published_at=12)
        self.assertEqual(limited.checkpoint(), before)
        self.assertEqual(limited.publications, ())
        maximum_time = 2**63 - 1
        terminal = engine((trade('at-maximum', maximum_time),), (definition,))
        before = terminal.checkpoint()
        with self.assertRaises(ContractError):
            terminal.publish_activity(terminal.capture(maximum_time), definition.id, published_at=maximum_time)
        self.assertEqual(terminal.checkpoint(), before)
        with self.assertRaises(ContractError):
            SharedBarEngine(DOMAIN, (TIME, definition), limits=BarLimits(2, 1, 1, 2))
        reset_bound = engine(BASE[:2], (definition,), maximum=2, block=1)
        before = reset_bound.checkpoint()
        with self.assertRaises(ContractError):
            reset_bound.publish_activity(reset_bound.capture(12), definition.id, published_at=12,
                resets=tuple(ResetMarker(f'r{i}', i + 3, i + 3, f'epoch{i}') for i in range(3)))
        self.assertEqual(reset_bound.checkpoint(), before)

    def test_immutable_coverage_publication_and_auxiliary_support(self):
        for intervals in (([0, 10],), ((False, 10),), ((0, 10.0),)):
            with self.assertRaises(ContractError):
                coverage(intervals=intervals)
        for identity in (False, [], 10):
            with self.assertRaises(ContractError):
                WindowCoverage(identity, 0, 10, ((0, 10),), 10, 'version')
        e = engine(BASE[:3])
        bar = e.publish_window(e.capture(12), request(), published_at=13)
        forged = replace(bar, coverage_complete=True)
        with self.assertRaises(ContractError):
            forged.available(20)
        with self.assertRaises(ContractError):
            opportunity_witness(forged, target_definition='forged', target_end=30, label_known_at=30,
                                touched=True, observation_process='nonempty_completed_bar')
        for changed in ({'revision': True}, {'state': []}, {'interval': [0, 10]}, {'published_at': 11}, {'minimum_known_at': 30}):
            with self.assertRaises(ContractError):
                replace(bar, **changed)
        with self.assertRaises(ContractError):
            CoarseBar('b', 'v', DOMAIN.instrument, DOMAIN.measurement, 0, 10, 10, True,
                      (100, 115, 95, 110), 1, body_envelope=(105, 106))
        for changed in ({'part_index': True}, {'known_at': True}, {'size': False}):
            fields = dict(original_id='a', original_version='content-a', part_index=0, size=2, known_at=1)
            with self.assertRaises(ContractError):
                TradeAllocation(**(fields | changed))
        with self.assertRaises(ContractError):
            allocate_trade(replace(BASE[0], history_complete='true'), (2,))
        quote = QuotePoint('q', 'v', DOMAIN.instrument, 1, 1, 100, 101)
        with self.assertRaises(ContractError):
            quote_bar((quote,) * 4097, instrument=DOMAIN.instrument, definition_id='quotes', start=0, end=10, cut=10, published_at=10)
        with self.assertRaises(ContractError):
            allocate_trade(trade('large', 1, size=4097), (1,) * 4097)
        with self.assertRaises(ContractError):
            unique_quantity_observations((QuantityObservation('q', 'v', DOMAIN.instrument, 'disjoint_trade_volume', 1, 1),) * 4097)

    def test_imported_view_canonical_rows_and_empty_publication_tamper(self):
        class ReorderedView:
            def asof(self, **kwargs):
                return tuple(reversed(BASE[:3]))
            def changes(self, **kwargs):
                return ()
        e = SharedBarEngine.from_trade_view(ReorderedView(), DOMAIN, (TIME,), start=0, end=10, cut=12)
        self.assertEqual(SharedBarEngine.restore(e.checkpoint()).checkpoint(), e.checkpoint())
        before = e.checkpoint()
        for change in ({'rows_hash': '0' * 64}, {'start': True}, {'end': 2}, {'cut': 2},
                       {'corrections': [{'id': 'outside', 'known_at': 12, 'before_instrument': DOMAIN.instrument,
                                         'before_event_at': 11, 'after_instrument': None, 'after_event_at': None}]}):
            broken = json.loads(before)
            broken['view_evidence'].update(change)
            with self.assertRaises((ContractError, IntegrityError)):
                SharedBarEngine.restore(canonical_json(broken))
        imported = SharedBarEngine.restore(before)
        self.assertEqual(imported.publish_window(imported.capture(12), request(), published_at=13).summary.volume, 7)
