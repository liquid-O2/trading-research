"""Independent daily-volatility arithmetic fixtures. No population run."""
from datetime import date, timedelta
import unittest

from trading_research.research.daily_volatility_complex import (
    build_dated_curve,
    build_identity_changes,
    compare_source_values,
    contract_change,
    decompose_front_change,
    duration_curve_key,
    equal_date_values,
    event_values,
    front_source_key,
    group_denominators,
    independent_dates,
    index_relationship,
    intended_universe,
    normalize_duration,
    nullable_int64,
    observation_clock,
    previous_intended_date,
    resolve_index_levels,
    stage_of,
)


def _fx(dte, level, *, trade=date(2020, 1, 2), label="A", product="P", duration="M", sha="a" * 64,
        path="free-sources/cboe__vx-futures__normalized/all-contracts.parquet"):
    return {
        "trade_date": trade,
        "contract_expiration": trade + timedelta(days=dte),
        "root": "VX",
        "duration_type": duration,
        "contract_label": label,
        "product_display": product,
        "settlement": level,
        "close": level,
        "source_path": path,
        "source_sha256": sha,
        "source": "Cboe",
    }


def _same_identity(level, *, trade, expiration, label="A"):
    return {
        "trade_date": trade,
        "contract_expiration": expiration,
        "root": "VX",
        "duration_type": "M",
        "contract_label": label,
        "product_display": "P",
        "settlement": level,
        "close": level,
        "source_path": "vx.parquet",
        "source_sha256": "a" * 64,
        "source": "Cboe",
    }


class DailyVolatilityComplexTests(unittest.TestCase):
    def test_upward_two_point_curve(self):
        structure = build_dated_curve([_fx(20, 10.0), _fx(40, 30.0)])["structure"]
        self.assertEqual(structure["front_level"], 10.0)
        self.assertEqual(structure["second_level"], 30.0)
        self.assertEqual(structure["spread"], 20.0)
        self.assertEqual(structure["ratio_minus_one"], 2.0)
        self.assertEqual(structure["tenor_spacing"], 20)
        self.assertEqual(structure["structure"], "contango")

    def test_flat_two_point_curve(self):
        structure = build_dated_curve([_fx(20, 10.0), _fx(40, 10.0)])["structure"]
        self.assertEqual(structure["spread"], 0.0)
        self.assertEqual(structure["ratio_minus_one"], 0.0)
        self.assertEqual(structure["structure"], "flat")

    def test_downward_two_point_curve(self):
        structure = build_dated_curve([_fx(20, 20.0), _fx(40, 10.0)])["structure"]
        self.assertEqual(structure["spread"], -10.0)
        self.assertEqual(structure["ratio_minus_one"], -0.5)
        self.assertEqual(structure["structure"], "backwardation")

    def test_linear_f30_equals_20_weights_half(self):
        item = build_dated_curve([_fx(20, 10.0), _fx(40, 30.0)])["interpolations"][30]
        self.assertEqual(item["price"], 20.0)
        self.assertEqual(item["weight_left"], 0.5)
        self.assertEqual(item["weight_right"], 0.5)
        self.assertEqual(item["left_dte"], 20)
        self.assertEqual(item["right_dte"], 40)
        self.assertEqual(item["method"], "linear_price")
        self.assertIsNone(item["missing_bracket_reason"])

    def test_exact_tenor_uses_observed_price(self):
        item = build_dated_curve([_fx(30, 15.0), _fx(60, 21.0)])["interpolations"][30]
        self.assertEqual(item["price"], 15.0)
        self.assertEqual(item["method"], "exact_observed")
        self.assertEqual(item["weight_left"], 1.0)
        self.assertEqual(item["weight_right"], 0.0)

    def test_outside_bracket_is_null(self):
        item = build_dated_curve([_fx(10, 10.0), _fx(20, 12.0)])["interpolations"][30]
        self.assertIsNone(item["price"])
        self.assertEqual(item["missing_bracket_reason"], "missing_right")

    def test_unequal_tenors_linear_interpolation(self):
        item = build_dated_curve([_fx(10, 10.0), _fx(40, 40.0)])["interpolations"][30]
        self.assertAlmostEqual(item["weight_right"], 20 / 30)
        self.assertAlmostEqual(item["weight_left"], 10 / 30)
        self.assertAlmostEqual(item["price"], 30.0)

    def test_weekly_monthly_not_pooled(self):
        rows = [_fx(20, 10.0, duration="M"), _fx(40, 30.0, duration="W")]
        monthly = build_dated_curve(rows, duration_family="monthly")
        weekly = build_dated_curve(rows, duration_family="weekly")
        self.assertIsNone(monthly["interpolations"][30]["price"])
        self.assertEqual(monthly["structure"]["front_dte"], 20)
        self.assertIsNone(weekly["interpolations"][30]["price"])
        self.assertEqual(weekly["structure"]["front_dte"], 40)

    def test_duplicate_equal_alias_dedup_with_count(self):
        built = build_dated_curve([_fx(20, 10.0, label="A"), _fx(20, 10.0, label="B")])
        self.assertEqual(len(built["ranking"]["ranked"]), 1)
        self.assertEqual(built["ranking"]["ranked"][0]["alias_count"], 2)
        self.assertEqual(built["ranking"]["aliases"][0]["identities"][0]["contract_label"], "A")
        self.assertEqual(len(built["ranking"]["aliases"][0]["identities"]), 2)

    def test_duplicate_conflict_excluded_and_flagged(self):
        built = build_dated_curve([_fx(20, 10.0, label="A"), _fx(20, 12.0, label="B")])
        self.assertEqual(built["disposition"], "missing_front")
        self.assertIsNone(built["structure"]["front_level"])
        self.assertEqual(len(built["ranking"]["maturity_conflicts"]), 2)

    def test_partial_curve_keeps_conflict_identities(self):
        built = build_dated_curve([_fx(20, 10.0, label="A"), _fx(20, 12.0, label="B"), _fx(40, 30.0, label="C")])
        self.assertEqual(built["disposition"], "partial_curve")
        self.assertEqual(built["structure"]["front_level"], 30.0)
        self.assertEqual(len(built["ranking"]["maturity_conflicts"]), 2)
        self.assertEqual(built["ranking"]["maturity_conflicts"][0]["identity_record"]["contract_label"], "A")

    def test_expired_dte0_retained_excluded_from_positive_curve(self):
        built = build_dated_curve([_fx(0, 9.0, label="F"), _fx(20, 15.0, label="G")])
        self.assertEqual(built["collected"]["expired"][0]["dte"], 0)
        self.assertEqual(built["structure"]["front_dte"], 20)
        self.assertEqual(len(built["ranking"]["ranked"]), 1)

    def test_nonfinite_level_ineligible(self):
        row = _fx(20, 10.0)
        row["settlement"] = float("nan")
        built = build_dated_curve([row])
        self.assertEqual(built["collected"]["ineligible"][0]["disposition"], "nonfinite")
        self.assertIsNone(built["structure"]["front_level"])

    def test_nonpositive_level_ineligible(self):
        built = build_dated_curve([_fx(20, 0.0)])
        self.assertEqual(built["collected"]["ineligible"][0]["disposition"], "nonpositive")
        self.assertIsNone(built["structure"]["front_level"])

    def test_missing_front_not_zero(self):
        built = build_dated_curve([_fx(30, 10.0, label="A"), _fx(30, 11.0, label="B")])
        self.assertEqual(built["disposition"], "missing_front")
        self.assertIsNone(built["structure"]["front_level"])

    def test_previous_intended_day_missing_no_change(self):
        intended = (date(2020, 1, 2), date(2020, 1, 3), date(2020, 1, 6))
        self.assertEqual(previous_intended_date(intended, date(2020, 1, 6)), date(2020, 1, 3))
        self.assertIsNone(contract_change(10.0, 12.0, False))
        self.assertEqual(contract_change(10.0, 12.0, True), 2.0)

    def test_conflict_current_blocks_same_contract_change(self):
        expiration = date(2020, 2, 19)
        intended = (date(2020, 1, 2), date(2020, 1, 3))
        rows = [
            _same_identity(10.0, trade=date(2020, 1, 2), expiration=expiration),
            _same_identity(11.0, trade=date(2020, 1, 3), expiration=expiration),
            _same_identity(12.0, trade=date(2020, 1, 3), expiration=expiration),
        ]
        change = build_identity_changes(rows, intended)[1]
        self.assertEqual(change["current_disposition"], "conflict_identity")
        self.assertIsNone(change["same_contract_change"])
        self.assertEqual(change["change_reason"], "conflict_or_invalid")

    def test_conflict_previous_blocks_same_contract_change(self):
        expiration = date(2020, 2, 19)
        intended = (date(2020, 1, 2), date(2020, 1, 3))
        rows = [
            _same_identity(10.0, trade=date(2020, 1, 2), expiration=expiration),
            _same_identity(10.5, trade=date(2020, 1, 2), expiration=expiration),
            _same_identity(11.0, trade=date(2020, 1, 3), expiration=expiration),
        ]
        current = [row for row in build_identity_changes(rows, intended) if row["date_value"] == date(2020, 1, 3)][0]
        self.assertEqual(current["previous_disposition"], "conflict_identity")
        self.assertIsNone(current["same_contract_change"])

    def test_nonpositive_excludes_same_contract_change(self):
        expiration = date(2020, 2, 19)
        intended = (date(2020, 1, 2), date(2020, 1, 3))
        rows = [
            _same_identity(10.0, trade=date(2020, 1, 2), expiration=expiration),
            _same_identity(0.0, trade=date(2020, 1, 3), expiration=expiration),
        ]
        current = [row for row in build_identity_changes(rows, intended) if row["date_value"] == date(2020, 1, 3)][0]
        self.assertEqual(current["current_disposition"], "nonpositive")
        self.assertIsNone(current["same_contract_change"])
        prior_zero = [
            _same_identity(0.0, trade=date(2020, 1, 2), expiration=expiration),
            _same_identity(11.0, trade=date(2020, 1, 3), expiration=expiration),
        ]
        current = [row for row in build_identity_changes(prior_zero, intended) if row["date_value"] == date(2020, 1, 3)][0]
        self.assertIsNone(current["same_contract_change"])

    def test_identical_alias_carries_count_and_change(self):
        expiration = date(2020, 2, 19)
        intended = (date(2020, 1, 2), date(2020, 1, 3))
        rows = [
            _same_identity(10.0, trade=date(2020, 1, 2), expiration=expiration),
            _same_identity(11.0, trade=date(2020, 1, 3), expiration=expiration),
            _same_identity(11.0, trade=date(2020, 1, 3), expiration=expiration),
        ]
        current = [row for row in build_identity_changes(rows, intended) if row["date_value"] == date(2020, 1, 3)][0]
        self.assertEqual(current["alias_count"], 2)
        self.assertEqual(current["same_contract_change"], 1.0)

    def test_rank_roll_split_from_same_contract_change(self):
        first = ("VX", date(2020, 2, 19), "M", "G", "P", "a" * 64)
        second = ("VX", date(2020, 3, 18), "M", "H", "P", "a" * 64)
        rolled = decompose_front_change({"identity": first, "level": 10.0}, {"identity": second, "level": 12.0})
        self.assertIsNone(rolled["same_contract_change"])
        self.assertEqual(rolled["rank_roll_gap"], 2.0)
        same = decompose_front_change({"identity": first, "level": 10.0}, {"identity": first, "level": 11.0})
        self.assertEqual(same["same_contract_change"], 1.0)
        self.assertIsNone(same["rank_roll_gap"])

    def test_front_source_key_includes_path_and_hash(self):
        left = front_source_key(date(2020, 1, 2), "monthly", "Cboe", "VX", "settlement", "a.parquet", "aaa")
        right = front_source_key(date(2020, 1, 2), "monthly", "Cboe", "VX", "settlement", "b.parquet", "bbb")
        self.assertNotEqual(left, right)

    def test_vix3m_over_vix_ratio_is_one(self):
        relation = index_relationship(20.0, 10.0)
        self.assertEqual(relation["difference"], 10.0)
        self.assertEqual(relation["ratio_minus_one"], 1.0)
        self.assertFalse(relation["missing"])

    def test_date_only_future_publication_not_usable(self):
        clock = observation_clock(date(2026, 9, 3), date(2026, 9, 3), date(2026, 9, 3))
        self.assertIsNone(clock["known_at_ns"])
        self.assertFalse(clock["causal_feature_eligible"])
        self.assertFalse(clock["usable_as_known_feature"])
        self.assertIsNone(clock["expected_next_publication"])

    def test_repeated_source_alias_does_not_double_dates(self):
        primary = {date(2020, 1, 2): 10.0, date(2020, 1, 3): 11.0, date(2020, 1, 6): 12.0}
        alias = dict(primary)
        self.assertEqual(len(independent_dates(primary, alias)), 3)
        compared = compare_source_values(primary, alias)
        self.assertEqual(compared["equal_values"], 3)
        self.assertEqual(compared["independent_primary_dates"], 3)
        self.assertFalse(compared["treat_as_independent"])

    def test_duplicate_level_conflict_not_independent_support(self):
        resolved = resolve_index_levels([{"value": 10.0}, {"value": 11.0}])
        self.assertEqual(resolved["disposition"], "conflict_symbol_date")
        self.assertFalse(resolved["usable"])
        mixed = resolve_index_levels([{"value": 10.0}, {"value": None}])
        self.assertEqual(mixed["disposition"], "mixed_invalid_valid")
        self.assertFalse(mixed["usable"])
        self.assertFalse(resolve_index_levels([{"value": 0.0}])["usable"])

    def test_nullable_int64_timestamps(self):
        array = nullable_int64([None, None])
        self.assertEqual(array.null_count, 2)
        self.assertEqual(str(array.type), "int64")

    def test_unknown_duration_originals_not_mixed(self):
        self.assertEqual(duration_curve_key("M"), "monthly")
        self.assertEqual(duration_curve_key("quarterly"), "unexpected:quarterly")
        self.assertEqual(duration_curve_key("custom"), "unexpected:custom")
        self.assertNotEqual(duration_curve_key("quarterly"), duration_curve_key("custom"))
        self.assertEqual(normalize_duration("quarterly")["family"], "unexpected")
        mixed = build_dated_curve(
            [_fx(20, 10.0, duration="quarterly"), _fx(40, 30.0, duration="custom")],
            duration_family="unexpected:quarterly",
        )
        self.assertEqual(mixed["structure"]["front_dte"], 20)
        self.assertIsNone(mixed["structure"]["second_level"])

    def test_year_stage_intended_date_denominators(self):
        intended = (date(2020, 6, 1), date(2020, 6, 2), date(2023, 6, 1), date(2025, 6, 2))
        self.assertEqual(intended_universe(intended, year=2020), (date(2020, 6, 1), date(2020, 6, 2)))
        self.assertEqual(intended_universe(intended, stage="training"), (date(2020, 6, 1), date(2020, 6, 2)))
        self.assertEqual(intended_universe(intended, stage="development"), (date(2023, 6, 1),))
        self.assertEqual(intended_universe(intended, stage="confirmation"), (date(2025, 6, 2),))
        self.assertEqual(stage_of(date(2020, 6, 1)), "training")
        observed = {date(2020, 6, 1)}
        self.assertEqual(group_denominators(intended, "all", "all", observed),
                         {"intended": 4, "observed": 1, "missing": 3})
        self.assertEqual(group_denominators(intended, 2020, "all", observed),
                         {"intended": 2, "observed": 1, "missing": 1})
        self.assertEqual(group_denominators(intended, "all", "development", observed),
                         {"intended": 1, "observed": 0, "missing": 1})

    def test_equal_date_and_event_distributions_stay_separate(self):
        date_map = {date(2020, 1, 2): [2.0, 4.0], date(2020, 1, 3): [6.0]}
        self.assertEqual(equal_date_values(date_map), [3.0, 6.0])
        self.assertEqual(event_values(date_map), [2.0, 4.0, 6.0])
        monthly = {date(2020, 1, 2): 10.0}
        weekly = {date(2020, 1, 2): 20.0}
        self.assertNotEqual(equal_date_values(monthly), equal_date_values(weekly))
