"""Literal report population and source-evidence links."""
import unittest
from unittest.mock import patch


class NarrativePopulationTests(unittest.TestCase):
    def test_pooled_rates_keep_whole_intended_counts_and_link_original_year_evidence(self):
        from trading_research.research.jumbo_narrative import descriptive_report
        def metric(estimate,events=0):
            return dict(estimate=estimate,positive_events=events,bootstrap={"lower":.1,"upper":.9})
        def stats(complete,intended,both):
            return dict(kind="jumbo_observed_year_statistics_v1",formations=[],special_mechanisms=[],paths=[
                dict(clock="all-clocks-kept",horizon="after_180m",complete_target_dates=complete,intended_dates=intended,
                     path_counts={"no_break":complete-both,"ambiguous":both},metrics={"both_breach":metric(both/complete,both),
                     "both_full_population_rate_lower":metric(both/intended),"both_full_population_rate_upper":metric(1.)})])
        shards = [dict(root="NQ",year=year,intended_cash_dates=intended,statistics={"sha256":str(year)})
                  for year,intended in ((2022,10),(2023,20))]
        with patch("trading_research.research.jumbo_study._read_statistics",side_effect=[stats(5,10,1),stats(10,20,4)]):
            text = descriptive_report(shards,None,protocol={},analysis_plan={},stage="development")
        self.assertIn("15 / 30",text)
        self.assertIn("33.3%",text)
        self.assertIn("NQ-2022-shard.json",text)
        self.assertIn("NQ-2023-shard.json",text)
        self.assertIn("statistics SHA256 `2022`",text)
        self.assertIn("statistics SHA256 `2023`",text)
        self.assertIn("2022 | 5 / 10",text)
        self.assertIn("2023 | 10 / 20",text)
        shards[1]['source_supersession']={'sha256':'explicit-correction'}
        with patch("trading_research.research.jumbo_study._read_statistics",side_effect=[stats(5,10,1),stats(10,20,4)]):
            corrected = descriptive_report(shards,None,protocol={},analysis_plan={},stage="development")
        self.assertIn('NQ-2023-source-supersession-shard.json',corrected)
        self.assertNotIn('](NQ-2023-shard.json)',corrected)
