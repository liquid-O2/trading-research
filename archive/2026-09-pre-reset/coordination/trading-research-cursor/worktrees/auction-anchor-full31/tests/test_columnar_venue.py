from decimal import Decimal
from pathlib import Path
import unittest

import pyarrow as pa

from trading_research.data.compact import CompactProjector
from trading_research.data.events import decode_fields
from trading_research.execution.columnar import ColumnarVenuePath
from trading_research.execution.costs import load_fee_scenarios
from trading_research.execution.replay import BracketPlan,OrderTiming,reference_bracket
from trading_research.execution.venue import FillScenario,VenuePath
from trading_research.foundations.units import NQ_REFERENCE
from tests.test_market_data import event


class ColumnarVenueTests(unittest.TestCase):
    def paths(self):
        events=(event(0,at=1),event(1,at=2,action='T',flags=0),event(2,at=20,bid=102.,ask=102.25),
                event(3,at=21,action='T',flags=0,price=102.),event(4,at=31,bid=98.,ask=98.25),event(5,at=32,action='T',flags=0,price=98.))
        p=CompactProjector(tick_denominator=4,maximum_rows=100);qs,ts=p.project(pa.RecordBatch.from_pylist([decode_fields(e.raw_fields) for e in events]),source_part='fixture')
        q=pa.concat_tables(qs).combine_chunks();t=pa.concat_tables(ts).combine_chunks()
        fast=ColumnarVenuePath(instrument='NQH5',instrument_id=1,quotes=q,trades=t,source_version='synthetic-source',feed_delay_ns=2,
                              latency_scenario='event-plus-2ns',market_state='continuous',market_state_version='synthetic-status',complete_intervals=((0,100),),coverage_version='fixture-coverage')
        literal=VenuePath(instrument=fast.instrument,quotes=tuple(fast.quotes),trades=tuple(fast.trades),complete_intervals=fast.complete_intervals,coverage_version=fast.coverage_version)
        return literal,fast

    def test_every_cut_and_same_time_scenario_matches_independent_literal_state(self):
        literal,fast=self.paths()
        for at in range(1,100):
            for clock in ('strategy','venue'):
                for ordering in ('ambiguous','order_first','venue_first'):
                    with self.subTest(at=at,clock=clock,ordering=ordering):
                        a=literal.quote_at(at,clock=clock,same_time_ordering=ordering)[0];b=fast.quote_at(at,clock=clock,same_time_ordering=ordering)[0]
                        self.assertEqual(a,b)

    def test_full_bracket_outcome_and_fee_cash_are_identical(self):
        literal,fast=self.paths();fees=load_fee_scenarios(Path(__file__).resolve().parents[1]/'configs/fee-scenarios.json')[0]
        scenario=FillScenario('fixture',0,'venue_first','strict_trade_through','fixture-coverage',fees.version)
        plan=BracketPlan('p','NQH5',1,10,401,393,409,50,80,90,Decimal(50),'geometry')
        timing=OrderTiming('timing',2,2,0,'trigger_first')
        args=dict(terms=NQ_REFERENCE,fees=fees,fill_scenario=scenario,timing=timing)
        self.assertEqual(reference_bracket(literal,plan,**args),reference_bracket(fast,plan,**args))
