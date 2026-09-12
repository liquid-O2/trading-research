"""Reviewed fixture upgrades for the range, profile, and auction families.

The first method-pack fixture catalog predates the evidence-complete object
contracts.  These patches keep the stable fixture IDs while replacing summary
aliases with identified observations and expectations named by the live
schemas.  Installation is explicit so the registry owner controls import
order.
"""

from __future__ import annotations

from decimal import Decimal
from datetime import date
from typing import Any

from trading_research.research.method_pack.objects.range_geometry import RangeGeometry
from trading_research.research.method_pack.objects.profiles import (
    Coverage, InstrumentDefinition, ProfileDefinition, ProfileWindow,
    ValueAreaConfig, build_profile,
)
from trading_research.research.method_pack.adapters import normalize_trade_row


D = Decimal


def _range(inp: dict[str, Any], fixture_id: str, *, clock: str = "fixture-clock",
           coverage: bool | None = True) -> RangeGeometry:
    members = inp.get("members") or []
    lows = [D(str(row["L"])) for row in members] or [D(str(inp.get("L", 100)))]
    highs = [D(str(row["H"])) for row in members] or [D(str(inp.get("H", 110)))]
    start = inp.get("start_ns", inp.get("formation_start", 1))
    end = inp.get("end_ns", inp.get("formation_end", start + 1))
    known = inp.get("known_at", end)
    low, high = min(lows), max(highs)
    return RangeGeometry(f"{fixture_id}:range", "NQ", clock, start, end, known,
                         low, high, high-low, coverage,
                         tuple(str(row.get("bar_id", f"{fixture_id}:bar:{i}"))
                               for i, row in enumerate(members)) or (f"{fixture_id}:bar",))


def _candle(cid: str, start: int, O: Any, H: Any, L: Any, C: Any, V: Any = 100) -> dict[str, Any]:
    return {"candle_id": cid, "instrument_id": "NQ", "start": start,
            "end": start + 1, "known_at": start + 1, "O": D(str(O)),
            "H": D(str(H)), "L": D(str(L)), "C": D(str(C)),
            "V": D(str(V)), "complete": True}


def _profile(profile_id: str, row_offset: int = 0, *, mode: str = "base"):
    instrument = InstrumentDefinition("NQ:v1", "NQ", D(".25"), 1)
    window = ProfileWindow(f"window:{profile_id}", "developing_rth",
                           date(2026, 1, 15), 10, 100)
    definition = ProfileDefinition(profile_id, instrument, window, 2,
        "fixture-source", poc_tie_policy=None if mode == "tied" else "lowest",
        value_area=ValueAreaConfig("fixture-va", D(".70"), "supplied_bounds",
                                   "lower", supplied_val=D("100"),
                                   supplied_vah=D("100.50" if mode == "tied" else "100.25")))
    raw_rows = {
        "base": [("100", 7, "B"), ("100", 3, "A"), ("100.25", 2, "B")],
        # The quote-only compatibility input has no canonical executions after
        # source normalization, so its typed profile is deliberately empty.
        "empty": [],
        "tied": [("100", 4, "B"), ("100.25", 10, "B"), ("100.50", 10, "B")],
        "unknown": [("100", 7, "B"), ("100", 4, "A"),
                    ("100.25", 2, "B"), ("100.25", 5, "A"),
                    ("100.25", 2, "N")],
    }[mode]
    observations = [normalize_trade_row(
        {"t": 20 + index, "price": price, "size": size, "side": side,
         "instrument_id": "NQ"}, source_file="fixture.csv",
        source_row=row_offset + index + 1)
        for index, (price, size, side) in enumerate(raw_rows)]
    return build_profile(definition, observations, as_of=100,
                         coverage=Coverage("complete",10,100,coverage_id=f"coverage:{profile_id}"))


def _range_patch(spec: dict[str, Any]) -> None:
    fid, rid, inp = spec["id"], spec["recipe"], spec["inputs"]
    exp = spec["expected"]
    if rid == "O002":
        inp["bars"] = [{**inp.pop("bar"), "complete": True}]
        inp.update(side="upper", source_criterion="literal_close_return",
                   source_reject_evidence=fid.endswith("F1b"), coverage_ok=True)
        exp.clear(); exp.update(price_overlap=True, sweep_depth=D("1"),
                                sweep_depth_ticks=D("4") if inp.get("q") else None,
                                literal_close_return=fid.endswith("F1b"))
    elif rid == "O005":
        cov = None if fid.endswith("F1c") else True
        inp["range"] = _range(inp, fid, clock="JJ-TBR:06:00-09:00", coverage=cov)
        exp.clear()
        if fid.endswith("F1c"): exp.update(state="invalid",base_ok=False)
        else: exp.update(L=inp["range"].L, H=inp["range"].H,
                         W=inp["range"].W, range_frozen=True, coverage_ok=True)
    elif rid == "O006":
        inp["range"] = _range(inp, fid, clock=str(inp.get("clock_id", "manual")))
        exp.clear(); exp.update(W=inp["range"].W,
                                source_clock_verified=inp.get("source_clock_verified"))
    elif rid == "O007":
        exp.clear(); exp.update(q25=D(str(inp["L"])) + D(".25")*(D(str(inp["H"]))-D(str(inp["L"]))),
                                eq=(D(str(inp["L"]))+D(str(inp["H"])))/2,
                                q75=D(str(inp["L"])) + D(".75")*(D(str(inp["H"]))-D(str(inp["L"]))))
    elif rid == "O008":
        inp.update(anchor_id="range-open", reference_verified=True,
                   path_source_id="range-open", path_target_id="range-low",
                   source_event={"reference_id":"range-open", "known_at":1},
                   target_event={"reference_id":"range-low", "known_at":2})
        exp.clear(); exp.update(reference_verified=True, directed_path=True,
                                range_open_ref=D(str(inp["range_open_ref"])))
    elif rid == "O009":
        inp.update(prior_range_width=inp.pop("prior_W"), source_width_class="extended",
                   denominator_ids=["tick:NQ", "prior-range"])
        exp.clear(); exp.update(width_points=D(str(inp["W"])), width_ticks=D("80"),
                                price_percent=D("0.10"), width_ratio=D("0.25"),
                                source_width_class="extended")
    elif rid == "O010":
        inp["coverage_ok"] = True
        if fid.endswith("F1b"): exp.clear(); exp.update(path="high_so_far", first_side="high", window_complete=False)
        elif fid.endswith("F1c"): exp.clear(); exp.update(path="neither", first_side=None, window_complete=True)
        else: exp.clear(); exp.update(path="both", first_side="high", window_complete=True)
    elif rid == "O011":
        cov = not fid.endswith("F1b")
        inp["range"] = _range(inp, fid, clock="O011:sires_overnight", coverage=True if cov else None)
        exp.clear(); exp.update(on_high=inp["range"].H, on_low=inp["range"].L,
                                on_width=inp["range"].W, coverage_ok=True if cov else None)
    elif rid == "O012":
        sweep = inp.pop("sweep_at")
        inp.update(reference_id="prior-high", side="high", sweep_definition="strict_trade",
                   events=[{"t": sweep, "price": D(str(inp["reference_px"]))+1,
                            "known_at": sweep, "session":"rth"}], coverage_ok=True)
        exp.clear(); exp.update(purged_at=sweep,
                                source_purged_context=sweep < inp["decision_at"],
                                active_before_use=not (sweep < inp["decision_at"]))
    elif rid == "O013":
        inp.update(prior_value=[inp.pop("prior_val"), inp.pop("prior_vah")],
                   prior_range=[inp.pop("prior_range_l"), inp.pop("prior_range_h")],
                   opening_context="above_value_inside_range", reference_ids=["prior-va","prior-range"])
        exp.clear(); exp.update(open_vs_value="above", open_vs_range="inside",
                                opening_context=None if inp["rvol_known_at"] > inp["use_at"] else "above_value_inside_range")
    elif rid == "O014":
        inp.update(coordinate_convention_verified=True, selected_band=[D("122"),D("124")],
                   side="upper", events=[{"t": inp.get("known_at", 1), "price": inp.get("price")}])
        exp.clear(); exp.update(upper_ladder={"0.1":D("122"),"0.2":D("124"),"0.3":D("126"),"0.5":D("130")},
                                sweep_depth_W=D("0.05"), parent_id=None)
    elif rid == "O015":
        inp["coordinate_convention_verified"] = True
        width=D(str(inp["H"]))-D(str(inp["L"]))
        exp.clear(); exp.update(upper_band=[D(str(inp["H"]))+D("1.33")*width,D(str(inp["H"]))+D("1.66")*width],
                                lower_band=[D(str(inp["L"]))-D("1.66")*width,D(str(inp["L"]))-D("1.33")*width])
    elif rid == "O016":
        inp.update(outer_id="outer", inner_id="inner", source_label="nested_range",
                   literal_labels=["outer", "inner"])
        exp.clear(); exp.update(outer_width=D(str(inp["outer_H"]))-D(str(inp["outer_L"])),
                                inner_width=None if inp.get("inner_H") is None else D(str(inp["inner_H"]))-D(str(inp["inner_L"])),
                                automatic_inner_span=None)
    elif rid == "O017":
        inp.update(min_average=inp.get("average"), midpoint_parent="average",
                   settings={"source_version":"fixture","platform":"Sierra","chart_timeframe":"30m",
                             "session":"RTH","reset":"session","lookback":20})
        exp.clear(); exp.update(midpoint_when_labeled=D("110"), source_band_known=True, automatic_bands=None)
    elif rid == "O018":
        inp.update(source_version="fixture", anchor_id="session-anchor", ev_id="evrange",
                   snapshot_known_at=inp.get("known_at"))
        raw_mid = inp.get("midpoint", inp.get("ev_mid"))
        exp.clear(); exp.update(ev_reference_known=True if raw_mid is not None or inp.get("ev_low") is not None else None, automatic_ev=None,
                                ev_mid_if_supplied=None if raw_mid is None else D(str(raw_mid)))
    elif rid == "O019":
        inp.update(snapshot_known_at=inp.get("snapshot_known_at", inp.get("known_at")), state_events=[{"known_at":inp.get("known_at"),"active":True}],
                   settings={"source_version":"fixture"}, path_source_id="anchor", path_target_id="zone",
                   path_events=[{"reference_id":"anchor","known_at":1},{"reference_id":"zone","known_at":2}])
        exp.clear(); exp.update(source_zone_known=None if inp.get("touch_at") is None else True, active_at_use=True, directed_path_recorded=True)
    elif rid == "O020":
        inp["prior_range_id"] = "prior:RTH"
        exp.clear(); exp.update(prior_rth_high=D(str(inp.get("prior_rth_h"))), prior_rth_low=D(str(inp.get("prior_rth_l"))),
                                rth_active_objectives=[], coverage_ok=None, state="hole")
    elif rid == "O021":
        event=inp["event_ns"]
        inp.update(window_start=event-60, window_end=event+60, purpose="entry", branch="reversal")
        if fid.endswith("F1b"): inp.update(window_start=event+1, window_end=event+61)
        exp.clear(); exp.update(source_time_window=not fid.endswith("F1b"), purpose="entry", branch="reversal")
    elif rid == "O022":
        inp["label"] = "clean" if "clean" in inp["label"] else "preferred"
        inp["session_id"]="session:selected"
        exp.clear()
        if inp["recorded_at"] > inp["use_at"]: exp.update(state="invalid",base_ok=False)
        else: exp.update(source_cleanliness_label=inp["label"], session_selected_before_use=True,automatic_cleanliness=None)
    elif rid == "O023":
        inp.update(phase_label=inp.get("phase"), used_as_context=True, contemporaneous=True,
                   transition_events=[{"known_at":inp.get("known_at")}])
        exp.clear(); exp.update(phase_label=inp.get("phase"), used_as_context=True,
                                automatic_phase=None, contemporaneous=True)
    elif rid == "O024":
        for row in inp["attempts"]:
            row["ended_at"] = row.pop("end")
            row["outcome"] = "failed"
        inp.update(level_id="fixture-level", branch="reversal", invalidation_evidence_complete=True)
        exp.clear(); exp.update(failed_attempt_count=3 if fid.endswith("F1b") else 2,
                                three_failed_attempts=fid.endswith("F1b"),
                                reversal_invalidated=fid.endswith("F1b"))
    elif rid == "O025":
        inp.update(or_id="NQ:OR", source_clock_verified=True, end_ns=inp.pop("or_end"))
        exp.clear(); exp.update(or_mid=D("104"), or_known=True)
    elif rid == "O026":
        inp.update(low_id="swing-low", high_id="swing-high", swing_id="swing-1", timeframe="5m")
        exp.clear(); exp.update(swing_mid=(D(str(inp["low"]))+D(str(inp["high"])))/2,
                                later_mid_contact=inp.get("retrace_at"), automatic_pivot=None)
    elif rid == "O028":
        selected=inp.get("known_at")
        inp.update(objective_band=[min(D(str(inp["a"])),D(str(inp["b"]))),max(D(str(inp["a"])),D(str(inp["b"])))],
                   a_confirmed_at=selected, b_confirmed_at=selected, selected_at=selected,
                   coverage_ok=True, objective_id="equal-highs")
        exp.clear(); exp.update(prices_equal=D(str(inp["a"]))==D(str(inp["b"])), reference_known=True,
                                remaining_objective=True)
    elif rid == "O029":
        at=inp["as_of"]
        inp.update(event_id="CPI", timezone="America/New_York", schedule_published_at=at-2,
                   scheduled_at=at+10, actual_release_at=at+10, vintage_id="CPI:v1",
                   release_known_at=at+10)
        exp.clear(); exp.update(schedule_known=True, release_known=False, new_information_known=False)
    elif rid == "O046":
        start,end=inp.get("start_ns"),inp.get("end_ns")
        if start is None and end is not None:
            # Preserve the intended coverage hole without discarding the
            # identified formation interval or its measurable geometry.
            start = end - 3_600_000_000_000
            inp["start_ns"] = start
        inp["source_clock_verified"] = True
        if start is not None and end is not None:
            inp["members"]=[{"bar_id":f"{fid}:bar","start":start,"end":end,"L":inp.get("L"),"H":inp.get("H"),
                             "complete":not inp.get("missing_row",False),"coverage_state":"complete" if not inp.get("missing_row",False) else "missing",
                             "known_at":end}]
        exp.clear()
        if inp.get("missing_row", False):
            exp.update(box_low=D(str(inp["L"])),box_high=D(str(inp["H"])),
                       box_width=D(str(inp["H"]))-D(str(inp["L"])),
                       coverage_ok=None,state="hole")
        else: exp.update(box_low=D(str(inp["L"])), box_high=D(str(inp["H"])),
                         box_width=D(str(inp["H"]))-D(str(inp["L"])), coverage_ok=True)
    elif rid == "O047":
        ref=D(str(inp["reference_px"])); high=inp.get("side") in {"upper","high"}; sweep=inp.get("sweep_at", inp.get("known_at",1)+1)
        inp.update(side="high" if high else "low", reference_known_at=inp.get("reference_known_at", sweep-1),
                   events=[{"t":sweep,"price":ref+(1 if high else -1)}], confirmation_type="complete_close",
                   confirmation_bar={"C":D(str(inp.get("confirm_close",ref))),"end":inp.get("confirm_at",sweep+1),"known_at":inp.get("confirm_at",sweep+1),"complete":True},
                   decision_at=inp.get("decision_at",inp.get("use_at")), coverage_ok=True)
        exp.clear()
        if inp["decision_at"] < inp["confirmation_bar"]["known_at"]: exp.update(state="invalid",base_ok=False)
        else: exp.update(failure_confirmed=D(str(inp.get("confirm_close",ref))) < ref if high else D(str(inp.get("confirm_close",ref))) > ref, reference_known_before_sweep=True)
    elif rid == "O048":
        inp.update(prior_high=inp.get("pdh"), prior_low=inp.get("pdl", 100), period_id="prior:RTH",
                   period_kind="session", period_scope="RTH", period_end=inp.get("known_at"),
                   active_state=True, retirement_policy="RTH_touch")
        exp.clear(); exp.update(prior_high=None if inp.get("prior_high") is None else D(str(inp.get("prior_high"))),
                                prior_low=D(str(inp.get("prior_low"))),
                                active_state=inp.get("active_state"), state="hole")
    elif rid == "O050":
        inp["source_reclaim_criterion"]="strict"
        exp.clear(); exp.update(cross_below_at=inp["events"][0]["t"], reclaim_at=inp["events"][1]["t"], source_open_reclaim=True)
    elif rid == "O051":
        inp.update(sunday_convention="globex_open", gap_id="weekend-gap")
        exp.clear(); exp.update(gap_lo=D("100"),gap_hi=D("104"),gap_width=D("4"),
                                full_fill=inp.get("price")==100,automatic_gap=True)
    elif rid == "O052":
        inp["impulse_id"]="impulse-1"
        band=[D("110"),D("112.36")] if inp["impulse_side"]=="down" else [D("107.64"),D("110")]
        exp.clear(); exp.update(band_lo=band[0],band_hi=band[1],impulse_id="impulse-1",automatic_impulse=None)
    elif rid == "O053":
        inp.update(parent_id="range-1",value_reference_id="vwap-1")
        exp.clear(); exp.update(range_mid=D("110"),normalized_position=D("0.4"),location="discount",value_relative_relation="above")
    elif rid == "O055":
        inp.update(construction="three_candle_imbalance", defining_candle_ids=["c1","c2","c3"],
                   active_policy="until_full_fill", state_events=[{"known_at":inp.get("known_at"),"active":True}],
                   events=[{"price":inp.get("touch_px")}],far_edge=104,direction="up")
        exp.clear(); exp.update(contact_or_fill={"contact":True,"full_fill":False},active_at_use=True)
    elif rid == "O056":
        bull=not fid.endswith("F1b")
        inp.clear(); inp.update(c1=_candle("c1",1,102,103,101,102),
          c2=_candle("c2",3,102,104,100,103),
          c3=_candle("c3",5,103,106,102,105 if bull else 103), sweep_side="low",
          selected_entry_mode="midpoint", selected_stop=100,timeframe="2m", known_at=6,use_at=7)
        exp.clear(); exp.update(ob_band=[D("100"),D("104")],ob_mid=D("102"),confirmed=bull,candle_ids=["c1","c2","c3"])
    elif rid == "O057":
        inp.update(source_rejection=True,allowed_location=True,stop_policy="beyond_wick",entry_policy="source",candle_id="rej-1",timeframe="5m")
        exp.clear(); exp.update(body_lo=D("102"),body_hi=D("103"),rejection_band=[D("100"),D("102")],wick_width=D("2"),has_wick=True)
    elif rid == "O058":
        end=inp.get("known_at",30); inp.update(start=end-1,complete=True,candle_id="current",
          history=[_candle(f"h{i}",end-30+2*i,100,110,100,101,100) for i in range(14)],
          average_inclusion="prior_only",reset_policy="source",equality_policy="strict")
        exp.clear(); exp.update(body_ratio=D("0.2"),volume_average=D("100"),volume_ratio=D("2"),source_zone_flag=True)
    elif rid == "O060":
        inp.update(auction_id="auction-1",profile_id="profile-1",scale="session",source_acceptance=True)
        exp.clear()
        if inp.get("declared_at") > inp.get("use_at"): exp.update(state="invalid",base_ok=False)
        else: exp.update(balance_band=[D(str(inp["lo"])),D(str(inp["hi"]))],balance_width=D(str(inp["hi"]))-D(str(inp["lo"])),inside=True,automatic_balance=None)
    elif rid == "O049":
        inp.update(tdo_id="tdo-1",role="opening_confirmation",opening_event_id="rth-open")


def _auction_patch(spec: dict[str, Any]) -> None:
    fid, rid, inp = spec["id"], spec["recipe"], spec["inputs"]
    exp = spec["expected"]
    t=inp.get("known_at",10)
    if rid == "O078":
        inp.update(profile_id="tpo-profile",instrument_id="NQ",instrument_definition_id="NQ:v1",
                   session_date_et="2026-01-15",price_step=1,construction="trade_visited",coverage_ok=True)
        exp.clear(); exp.update(count_by_price={"100":2,"101":1} if fid.endswith("F1") else None)
        # The exact dated letter at a selected row is the contract under test.
        price=D(str(inp.get("price",100)))
        letters=sorted({f"2026-01-15:{row['letter']}" for row in inp["visits"] if D(str(row["price"]))==price and row["t"]<=inp["as_of"]})
        exp.clear(); exp.update(members=letters,count=len(letters))
        if fid.endswith("F1c"): exp.update(a_low=D("99"),a_period_complete=True)
    elif rid == "O079":
        inp.update(memberships=inp.pop("rows"),interior_band=inp.pop("accepted"),
                   lower_accepted_id="lower",upper_accepted_id="upper",formation_known_at=t,
                   repair_policy="any_later_letter")
        if "later_letter" in inp:
            price,letter=inp.pop("later_letter");inp["repairs"]=[{"price":price,"letter":letter,"at":inp["later_at"]}]
        exp.clear(); exp.update(single_letter_rows=[{"price":D("102"),"letter_id":"C","count":1}] if fid.endswith("F1b") else [{"price":D("101"),"letter_id":"C","count":1},{"price":D("102"),"letter_id":"C","count":1}],letter_ids=["C"],outer_tail_excluded=True)
    elif rid == "O080":
        inp.update(memberships=inp.pop("rows"),side="high",price_step=1,
                   source_criterion="same_letter_tail_min_2",instrument_id="NQ",grid_id="tick")
        exp.clear(); exp.update(tail_length_rows=2,same_letter_tail=not fid.endswith("F1b"),source_excess=not fid.endswith("F1b"))
    elif rid == "O081":
        inp.update(memberships=inp.pop("rows"),side="low" if inp.pop("side")=="lower" else "high",
                   price_step=1,instrument_root=inp.pop("instrument"),criterion="nq_one_row_tail",source_grid_compatible=True)
        if inp["instrument_root"]!="NQ": inp.pop("criterion")
        exp.clear(); exp.update(poor_high=True if inp["side"]=="high" and inp["instrument_root"]=="NQ" else False if inp["side"]=="low" else None,
                                poor_low=False if inp["side"]=="low" else False if inp["instrument_root"]=="NQ" else None)
    elif rid == "O082":
        inp["A"].update(complete=True,end=t-1);inp["B"].update(complete=True,end=t)
        inp.update(ib_id="ib",later_high=inp.pop("later_H",None),later_low=inp.pop("later_L",None),later_known_at=t)
        exp.clear();exp.update(ibh=D("110"),ibl=D("99"),ibw=D("11"))
        if inp.get("later_high") is not None: exp.update(upper_extension=D("2"),lower_extension=D("1"),later_break_flags={"upper_broken":True,"lower_broken":True,"both_broken":True})
    elif rid == "O083":
        inp.update(cash_open=inp.pop("open_px"),open_at=min(row["t"] for row in inp["prices"])-1,
                   path=inp.pop("prices"),claim_side="long",coverage_ok=True,observation_end=inp["as_of"],
                   source_type_criterion="supplied_case",source_open_type="open_drive",type_known_at=inp["as_of"],final=False)
        exp.clear();exp.update(crossed_open_by_asof=True,source_open_type="open_drive",provisional=True)
    elif rid == "O084":
        label=inp.pop("label");at=inp.pop("label_at")
        inp.update(author="Sires",taxonomy="Sires-AMT",provisional_type=label,provisional_known_at=at,
                   evidence_until=at,as_of=inp["use_at"],permission_reference="wait_for_evidence")
        exp.clear();exp.update(provisional_type=label,automatic_classifier=None)
    elif rid == "O085":
        inp.update(profile_id="profile-1",source_shape=inp.pop("shape"),source_permission="context_only",decision_at=t)
        exp.clear();exp.update(source_shape="P",automatic_shape_direction=None,break_retest_complete=False)
    elif rid == "O086":
        inp.update(reference_id="prior-high",kind="prior_rth_high",period_id="prior:RTH",selected_role="target",current_open=inp.pop("open_px"))
        exp.clear();exp.update(half_range_gap=D("112"),half_close_gap=D("109.5"),opening_relation="above_prior_high")
    elif rid == "O087":
        inp.update(objective_id="prior-high",objective_type="prior_rth_high",bounds=[inp.get("level"),inp.get("level")],
                   original_known_at=inp.get("known_at"),consumption_scope="RTH",consumption_rule="touch",
                   history_coverage_ok=True,priority_at_decision=1)
        exp.clear();exp.update(active_at_decision=True,eth_visits_do_not_retire_rth=True)
    elif rid == "O088":
        hits=inp.get("sessions",[]);cohort=[{"onh_hit":i < 6,"onl_hit":i in {0,1,2,6,7}} for i in range(10)] if not hits else hits
        inp.update(source_claim={"claim_id":"94pct","literal_rate":D(".94")},claim_definition_complete=True,observed_cohort=cohort)
        exp.clear();exp.update(observed_hit_counts={"n":10,"onh":6,"onl":5,"both":3,"either":8},observed_rate=D(".8"),claim_is_trade_win_rate=False)
    elif rid == "O089":
        inp.update(source_case_id="saint-case",source_range_reference=D(str(inp.get("asia_range"))),source_ambition_ok=True,rationale_known_at=t,side="short")
        exp.clear();exp.update(stop_distance=D("2"),target_distance=D("5"),automatic_target=None,side="short")
    elif rid == "O090":
        inp.update(balance_id="balance-1",edge_id="balance-1:low",side="long",balance_known_at=inp.get("known_at"),
                   edge_arrival_at=inp.pop("contact_at"),local_confirm_at=inp.pop("confirm_at",None),decision_at=inp["decision_at"],fair_value_id="poc")
        exp.clear();exp.update(rotation_sequence=None if inp["local_confirm_at"] is None else True,later_far_side_objective=None)
    elif rid == "O091":
        inp.update(boundary_id="ledge",retest_boundary_id="other" if inp.pop("other_band",False) else "ledge",direction="up",
                   boundary_known_at=inp.pop("ledge_known_at"),accept_at=inp["break_at"]+1,depart_at=inp.pop("departure_at"),
                   initiative_at=inp.pop("entry_at"),source_retest_held=True)
        inp["decision_at"] = inp["initiative_at"] + 1
        inp["use_at"] = max(inp.get("use_at",inp["decision_at"]),inp["decision_at"])
        exp.clear();exp.update(break_retest_sequence=True,same_boundary=True)
        if inp["retest_boundary_id"]!="ledge" or inp["initiative_at"] < inp["defense_at"]:
            exp.clear();exp.update(state="invalid",base_ok=False)
    elif rid == "O092":
        inp.update(area_id="value-area",val=inp.pop("va_lo"),vah=inp.pop("va_hi"),outside_before="above",
                   return_at=t-1,acceptance_definition="two_consecutive_complete_30m_whole_range_inside",next_objective_id="poc")
        periods=inp.pop("periods",None)
        if periods is None:
            px=inp.pop("price"); periods=[[px,px],[px,px]]
        base=t-3_600_000_000_000
        inp["inside_observations"]=[{"L":row[0],"H":row[1],"start":base+i*1_800_000_000_000,"end":base+(i+1)*1_800_000_000_000,"complete":True} for i,row in enumerate(periods)]
        accepted=all(D(str(row[0]))>=D("100") and D(str(row[1]))<=D("110") for row in periods)
        exp.clear();exp.update(reacceptance_sequence=accepted,value_band=[D("100"),D("110")])
    elif rid == "O093":
        inp.update(established_balance_id=inp.pop("established_id",None),older_profile_id=inp.pop("older_id",None),
                   established_vah=inp.pop("va_hi"),established_val=inp.pop("va_lo"),break_at=inp.pop("breakout_at",None),
                   older_poc_tag_at=inp.pop("tag_at",None),tag_price=inp.pop("tag_px"),reject_at=inp.pop("rejection_at",None),
                   source_rejection_observed=True,source_target_id="est:vah",source_target_price=inp.pop("target",110))
        distinct=inp.get("established_balance_id") is not None and inp.get("older_profile_id") is not None and inp.get("established_balance_id")!=inp.get("older_profile_id")
        exp.clear()
        if not distinct: exp.update(state="invalid",base_ok=False)
        else: exp.update(tagged=inp["tag_price"]==inp["older_poc"],distinct_balances=True,source_target_price=D("110"))
    elif rid == "O095":
        inp.update(profile_id="profile-1",tests=[{"attempt_id":f"a{i}","at":at,"failed":True} for i,at in enumerate(inp.pop("failed_crosses"))],
                   held_retest_at=inp.pop("retest_at",None),current_poc_read="efficient_passage",next_objective_id="far-edge",source_efficient_passage=True)
        if inp.get("as_of") is None: inp["decision_at"] = inp.get("use_at")
        decision = inp.get("as_of", inp.get("decision_at", inp.get("use_at")))
        exp.clear()
        if inp.get("as_of") is None and inp.get("held_retest_at") is not None and inp["held_retest_at"] > decision:
            exp.update(state="invalid",base_ok=False)
        else:
            exp.update(failed_test_count=2,test_ids=["a0","a1"],held_retest_at=inp["held_retest_at"] if inp["held_retest_at"] is not None and inp["held_retest_at"]<=decision else None)
    elif rid == "O096":
        inp.update(balance_id="balance-1",direction="up",traverse_start=inp.pop("lower_at"),traverse_end=inp.pop("upper_at"),
                   entry_boundary_id="low",exit_boundary_id="high",path_coverage_ok=True,hold_definition="source",no_source_hold=True,
                   control_at=inp.get("control_at"),decision_at=inp.get("entry_at",inp.get("use_at")))
        exp.clear()
        if inp.get("retest_at") is not None and inp.get("decision_at") < inp.get("control_at"): exp.update(state="invalid",base_ok=False)
        else: exp.update(traverse_duration=inp["traverse_end"]-inp["traverse_start"],whole_balance_crossed=True,maximum_duration=None)
    elif rid == "O097":
        inp.update(author="Saint",htf_thesis_id="thesis-1",htf_area_id="area-1",local_area_id="area-1",
                   thesis_alive=inp.get("thesis_died_at") is None,thesis_known_at=inp.pop("thesis_at"),control_at=inp.pop("local_at"),decision_at=inp.get("use_at"),free_two_sided_chop=False)
        exp.clear()
        if inp["control_at"] > inp["decision_at"]: exp.update(state="invalid",base_ok=False)
        else: exp.update(alignment_ok=inp["thesis_alive"] and inp["htf_side"]==inp["ltf_side"],thesis_alive=inp["thesis_alive"])
    elif rid == "O094" and fid.endswith("F1b"):
        exp.clear(); exp.update(state="invalid",base_ok=False)


def _profile_patch(spec: dict[str, Any]) -> None:
    """Give the principal profile fixtures a complete immutable snapshot."""
    fid, rid, inp, exp = spec["id"], spec["recipe"], spec["inputs"], spec["expected"]
    if rid == "O065":
        inp.update(reference_id=f"{fid}:reference", profile_id=f"{fid}:profile",
                   snapshot_id=f"{fid}:snapshot")
        for index, visit in enumerate(inp.get("visits", ())):
            visit["event_id"] = f"{fid}:visit:{index}"
        return
    if fid.endswith("F1b") and rid == "O074":
        inp.update(source_inventory="unknown", measured_evidence=[])
        exp.clear(); exp.update(source_inventory="unknown", measured_evidence=[],
                                automatic_inventory=None)
        return
    if not fid.endswith(("F1", "F1b")):
        return
    mode = ({("O061", "F1b"): "empty", ("O064", "F1b"): "tied",
             ("O077", "F1b"): "unknown"}.get((rid, "F1b"))
            if fid.endswith("F1b") else "base")
    profile = _profile(f"fixture:{rid}:{fid}", mode=mode or "base")
    if rid in {"O061", "O063", "O077"}:
        inp.clear(); inp.update(profile=profile, known_at=profile.known_at, use_at=profile.known_at)
        exp.clear()
        if rid == "O061": exp.update(total_volume=profile.total_volume, profile_id=profile.profile_id)
        elif rid == "O063": exp.update(poc=D("100"), snapshot_id=profile.snapshot_id)
        else:
            exp.update(total_volume=profile.total_volume,
                       known_window_delta=sum((row.known_delta for row in profile.rows), D(0)),
                       profile_id=profile.profile_id)
            if mode == "unknown":
                exp.update(known_delta=None, delta_interval=[D("-2"), D("2")])
    elif rid == "O062":
        inp.clear(); inp.update(profile=profile, known_at=profile.known_at, use_at=profile.known_at)
        exp.clear(); exp.update(val=D("100"),vah=D("100.25"),achieved_fraction=D("1"),construction_known=True)
    elif rid == "O064":
        inp.clear(); inp.update(profile=profile, known_at=profile.known_at, use_at=profile.known_at)
        exp.clear(); exp.update(poc=profile.poc,
                                max_volume=max((row.total_volume for row in profile.rows), default=None),
                                profile_id=profile.profile_id)
    elif rid == "O066":
        inp.clear(); inp.update(profile=profile,node=[100,100],node_id="hvn",source_node_known=True,
                                known_at=profile.known_at,use_at=profile.known_at)
        exp.clear(); exp.update(hvn_band=[D("100"),D("100")],node_volume=D("10"),source_node_known=True)
    elif rid == "O067":
        inp.clear(); inp.update(profile=profile,bridge_band=[100.25,100.25],accepted_a_id="a",accepted_b_id="b",
                                transition_ids=["x"],source_node_known=True,known_at=profile.known_at,use_at=profile.known_at)
        exp.clear(); exp.update(bridge_band=[D("100.25"),D("100.25")],bridge_volume=D("2"),accepted_area_ids=["a","b"])
    elif rid == "O068":
        inp.clear(); inp.update(profile=profile,shelf_band=[100,100],transition_band=[100.25,100.25],
                                shelf_id="shelf",edge_id="edge",source_shelf_known=True,
                                known_at=profile.known_at,use_at=profile.known_at)
        exp.clear(); exp.update(shelf_band=[D("100"),D("100")],shelf_volume=D("10"),transition_volume=D("2"))
    elif rid == "O070":
        second=_profile(f"fixture:O070:{fid}:b",100)
        inp.clear();inp.update(profiles=[profile,second],composite_id="fixture:composite",
                               selection_known_at=100,rationale="explicit fixtures",known_at=100,use_at=100)
        exp.clear();exp.update(total_volume=D("24"),constituent_ids=[profile.snapshot_id,second.snapshot_id])


def install(fixtures: list[dict[str, Any]]) -> None:
    """Upgrade the stable legacy fixture records in place."""
    range_ids = {"O002", *{f"O{i:03}" for i in range(5, 30)}, *{f"O{i:03}" for i in range(46, 61)}}
    profile_ids = {f"O{i:03}" for i in range(61, 78)}
    auction_ids = {f"O{i:03}" for i in range(78, 98)}
    for spec in fixtures:
        if spec.get("_completion_geometry_v2") is True:
            continue
        if spec["recipe"] in range_ids:
            _range_patch(spec)
            spec["_completion_geometry_v2"] = True
        elif spec["recipe"] in profile_ids:
            _profile_patch(spec)
            spec["_completion_geometry_v2"] = True
        elif spec["recipe"] in auction_ids:
            _auction_patch(spec)
            spec["_completion_geometry_v2"] = True


__all__ = ["install"]
