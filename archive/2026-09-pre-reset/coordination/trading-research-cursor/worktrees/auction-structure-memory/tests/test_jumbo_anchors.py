"""Direct canonical anchor/relationship fixtures; no market run is asserted."""
import copy
import hashlib
import unittest
import pyarrow as pa
import pyarrow.parquet as pq
from trading_research.errors import ContractError, IntegrityError
from trading_research.research.ohlc_ranges import MinuteBars
from trading_research.research.jumbo_anchors import (
    RELATIONSHIP_CLOCKS, build_anchor_supplement, validate_anchor_manifest,
    validate_anchor_content, supplement_feature_groups,
)

M=60_000_000_000
SOURCE="literal-admitted-series"


def form(clock="target",**updates):
    row=dict(root="NQ",year=2022,date="2022-01-03",clock=clock,formation_id="formation-"+clock,
      source_version=SOURCE,source_ids="literal-"+clock,contract_key="RAW",status="complete",
      formation_start_ns=0,formation_end_ns=5*M,available_at_ns=6*M,
      low_ticks=100,high_ticks=120,open_ticks=102,close_ticks=108,width_ticks=20)
    row.update(updates);return row


def path(**updates):
    row=dict(root="NQ",year=2022,date="2022-01-03",clock="target",horizon="after_15m",row_id="source-path-row",
       formation_id="formation-target",contract_key="RAW",origin_ns=10*M,endpoint_ns=25*M,
       x_last_close_position=.5,x_last_close_age_minutes=1.,x_prior_width_ticks=30.,
       x_width_prior_ratio=2/3,x_last_close_in_prior_position=.4,x_prior_last_close_displacement_ticks=4.,
       x_observed_cash_open_gap_ticks=3.,x_prior_age_minutes=100.,x_prior_5_mean_width_ticks=31.,x_prior_20_mean_width_ticks=32.)
    row.update(updates);return row


def bars(*,expected=True,late=False,other_contract=False,base=0,end_close=108):
    starts=[4,8] if expected else [4]
    prices=[base+end_close,base+110] if expected else [base+end_close]
    return MinuteBars(dict(start_ns=[t*M for t in starts],end_ns=[(t+1)*M for t in starts],
      known_at_ns=[6*M,10*M+(1 if late else 0)] if expected else [6*M],
      open_ticks=prices,high_ticks=prices,low_ticks=prices,close_ticks=prices,
      volume=[1]*len(starts),contract_key=["RAW","OTHER" if other_contract else "RAW"] if expected else ["RAW"],
      valid=[True]*len(starts)),source_version=SOURCE)


def refs(formation_count=1,path_count=1):
    return ({"kind":"literal-paths","sha256":"1"*64,"schema_sha256":"2"*64,"rows":path_count,"size_bytes":1},
            {"kind":"literal-formations","sha256":"3"*64,"schema_sha256":"4"*64,"rows":formation_count,"size_bytes":1})


def build(*,series=None,formations=None,paths=None):
    formations=[form()] if formations is None else formations
    paths=[path()] if paths is None else paths
    p,f=refs(len(formations),len(paths))
    return build_anchor_supplement(bars() if series is None else series,formations,paths,
       root="NQ",year=2022,path_ref=p,formation_ref=f,frozen_analysis_id="d5f-original-frozen")


class ExactAnchorSupplementTests(unittest.TestCase):
    def test_expected_published_minute_direct_price_and_times(self):
        result=build();r=result["table"].to_pylist()[0]
        self.assertEqual(r["anchor_ticks"],110)
        self.assertEqual((r["anchor_start_ns"],r["anchor_end_ns"],r["anchor_observation_known_at_ns"]),(8*M,9*M,10*M))
        self.assertEqual(r["anchor_known_at_ns"],10*M)
        self.assertEqual(r["anchor_source_kind"],"expected_published_minute")
        self.assertTrue(r["saved_position_reconciled"])
        self.assertEqual(r["source_path_row"],0)
        self.assertEqual(r["source_row_id"],"source-path-row")
        self.assertEqual(result["manifest"]["frozen_analysis_id"],"d5f-original-frozen")

    def test_missing_or_unpublished_expected_minute_uses_verified_formation_close(self):
        for s in (bars(expected=False),bars(late=True),bars(other_contract=True)):
            result=build(series=s,paths=[path(x_last_close_position=.4,x_last_close_age_minutes=5.)])
            r=result["table"].to_pylist()[0]
            self.assertEqual(r["anchor_ticks"],108)
            self.assertEqual(r["anchor_source_kind"],"formation_close_fallback")
            self.assertEqual((r["anchor_start_ns"],r["anchor_end_ns"],r["anchor_known_at_ns"]),(4*M,5*M,6*M))

    def test_fallback_requires_canonical_close_agreement(self):
        with self.assertRaises(IntegrityError):
            build(series=bars(expected=False),formations=[form(close_ticks=109)],paths=[path(x_last_close_position=.45,x_last_close_age_minutes=5.)])

    def test_direct_anchor_above_float_integer_precision(self):
        base=2**53+1
        f=form(low_ticks=base+100,high_ticks=base+120,open_ticks=base+102,close_ticks=base+108)
        r=build(series=bars(base=base),formations=[f])["table"].to_pylist()[0]
        self.assertEqual(r["anchor_ticks"],base+110)
        self.assertNotEqual(r["anchor_ticks"],int(float(base+110)))

    def test_saved_ratio_or_age_mismatch_is_rejected_not_inverted(self):
        for update in ({"x_last_close_position":.5000000000000001},{"x_last_close_position":None},{"x_last_close_age_minutes":0.}):
            with self.subTest(update=update),self.assertRaises(IntegrityError):build(paths=[path(**update)])

    def test_unavailable_formation_does_not_adopt_future_or_current_anchor(self):
        r=build(formations=[form(available_at_ns=11*M)],paths=[path(x_last_close_position=None,x_last_close_age_minutes=None)])["table"].to_pylist()[0]
        self.assertFalse(r["anchor_available"]);self.assertIsNone(r["anchor_ticks"])
        with self.assertRaises(IntegrityError):build(formations=[form(available_at_ns=11*M)])

    def test_zero_width_keeps_exact_anchor_without_normalized_position(self):
        f=form(low_ticks=100,high_ticks=100,open_ticks=100,close_ticks=100,width_ticks=0)
        r=build(series=bars(end_close=100),formations=[f],paths=[path(x_last_close_position=None)])["table"].to_pylist()[0]
        self.assertTrue(r["anchor_available"]);self.assertEqual(r["anchor_ticks"],110)
        self.assertIsNone(r["x_anchor_OR5_width_ratio"])

    def test_named_anchors_have_equal_causal_relationship_definitions(self):
        or5=form("OR5",low_ticks=100,high_ticks=110,open_ticks=102,close_ticks=105,width_ticks=10,
                 formation_end_ns=3*M,available_at_ns=4*M)
        or15=form("OR15",low_ticks=110,high_ticks=130,open_ticks=112,close_ticks=115,width_ticks=20,
                  formation_start_ns=2*M,formation_end_ns=7*M,available_at_ns=8*M)
        result=build(formations=[form(),or5,or15]);r=result["table"].to_pylist()[0]
        self.assertEqual(r["x_anchor_OR5_width_ratio"],.5)
        self.assertEqual(r["x_anchor_OR15_width_ratio"],1.)
        self.assertEqual(r["x_anchor_OR5_price_overlap_fraction"],.5)
        self.assertEqual(r["x_anchor_OR15_price_overlap_fraction"],.5)
        self.assertEqual(r["x_anchor_OR5_shared_time_fraction"],.6)
        self.assertEqual(r["x_anchor_OR15_shared_time_fraction"],.6)
        self.assertEqual(r["x_anchor_OR5_last_close_position"],1.)
        self.assertEqual(r["x_anchor_OR15_last_close_position"],0.)
        self.assertEqual(result["manifest"]["relationship_clocks"],list(RELATIONSHIP_CLOCKS))

    def test_unpublished_or_other_contract_reference_stays_missing(self):
        for update in ({"available_at_ns":11*M},{"contract_key":"OTHER"}):
            r=build(formations=[form(),form("OR15",**update)])["table"].to_pylist()[0]
            self.assertIsNone(r["x_anchor_OR15_width_ratio"])
            self.assertIsNone(r["x_anchor_OR15_last_close_position"])

    def test_original_generic_references_are_explicit_legacy_only(self):
        groups=supplement_feature_groups()
        for generic in ("opening_width_ratio","morning_width_ratio","asia_width_ratio","activity_threshold","prior_width_ticks"):
            self.assertNotIn(generic,groups["full"])
            self.assertIn(generic,groups["legacy_references"])
        self.assertIn("prior_actual_RTH_width_ticks",groups["controls"])
        for clock in RELATIONSHIP_CLOCKS:
            self.assertIn(f"anchor_{clock}_width_ratio",groups["named_anchor_"+clock])
            self.assertIn(f"anchor_{clock}_width_ratio",groups["full"])

    def test_future_label_changes_cannot_change_anchor_or_relationship_values(self):
        a=build();b=build(paths=[path(path="censored",label_origin_open_ticks=9999,maximum_up_ticks=9999,maturity_at_ns=99999)])
        self.assertTrue(a["table"].equals(b["table"]))
        self.assertEqual(a["manifest"]["content_sha256"],b["manifest"]["content_sha256"])

    def test_source_identity_and_parent_row_identity_are_strict(self):
        for change in ({"source_version":"other"},{"source_version":None},{"date":"2022-02-30"}):
            with self.subTest(change=change),self.assertRaises(IntegrityError):build(formations=[form(**change)])
        for change in ({"formation_id":"other"},{"clock":"other"},{"row_id":None},{"contract_key":"OTHER"}):
            with self.subTest(change=change),self.assertRaises(IntegrityError):build(paths=[path(**change)])
        with self.assertRaises(IntegrityError):build(paths=[path(),path()])

    def test_manifest_validates_canonical_ref_with_extra_metadata_and_wrapping(self):
        p,f=refs();p["note"]="preserved provenance"
        result=build_anchor_supplement(bars(),[form()],[path()],root="NQ",year=2022,
            path_ref={"artifact_ref":{k:p[k] for k in ("kind","sha256","size_bytes")},"rows":1,"schema_sha256":p["schema_sha256"],"note":p["note"]},
            formation_ref=f,frozen_analysis_id="d5f-original-frozen")
        validate_anchor_manifest(result["manifest"],root="NQ",year=2022,path_ref=p,formation_ref=f)
        self.assertEqual(result["manifest"]["source_paths"]["note"],p["note"])
        changed=dict(p,sha256="f"*64)
        with self.assertRaises(IntegrityError):validate_anchor_manifest(result["manifest"],root="NQ",year=2022,path_ref=changed,formation_ref=f)

    def test_logical_content_hash_survives_parquet_and_detects_changed_anchor(self):
        result=build();table=result["table"]
        sink=pa.BufferOutputStream();pq.write_table(table,sink)
        restored=pq.read_table(pa.BufferReader(sink.getvalue()))
        validate_anchor_content(restored,result["manifest"])
        changed=table.set_column(table.schema.get_field_index("anchor_ticks"),"anchor_ticks",pa.array([111],type=pa.int64()))
        with self.assertRaises(IntegrityError):validate_anchor_content(changed,result["manifest"])
        self.assertEqual(result["manifest"]["schema_sha256"],hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest())

if __name__ == "__main__":
    unittest.main()
