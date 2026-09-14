# C7 literal operands (final classification)

Frozen files under `implementation/src/trading_research/research/method_pack/`. B0.1 records the kind on a `baseline_repair` stage. `details['literal_operand_kind']` is a map of operand name to kind so a mixed stage (GB-FAIL by-construction + context-direction + structural) stays unambiguous. Genuinely unevaluated Saint stages stay on `details['unevaluated_operand']` as in round two. Structural flags that are False stay on `details['structural_not_required']`. `vwap_reset_verified` also records `details['assumption_id']='A2-GB-CLOCK'`. `bias_recorded` also records `details['context_direction_unevaluated']=True`.

Kinds: **by_construction**, **operational_assumption**, **context_direction_unevaluated**, **unevaluated**, **structural**.

| operand | class | frozen file:line | frozen value | action |
| --- | --- | --- | --- | --- |
| `location_touched` | by_construction | `historical_price_scanners.py:137`, `historical_flow.py:130` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `exit_window_recorded` | by_construction | `historical_price_scanners.py:145` | `True` | restored; `literal_operand_kind=by_construction` |
| `reduced_expectations` | by_construction | `historical_price_scanners.py:153` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `expansion_policy` | by_construction | `historical_price_scanners.py:163` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `source_clock_verified` | by_construction | `historical_price_scanners.py:176` | `True` | restored; `literal_operand_kind=by_construction` |
| `source_case_verified` | by_construction | `historical_price_scanners.py:176` | `True` | restored; `literal_operand_kind=by_construction` |
| `source_zone_known` | by_construction | `historical_price_scanners.py:179` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `bias_recorded` | context_direction_unevaluated | `historical_price_scanners.py:230` | `pre is not None and pre['known_at']<=trigger['start']` | restored computed presence; `details['context_direction_unevaluated']=True` |
| `source_session_allowed` | by_construction | `historical_price_scanners.py:238` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `pocket_required` | structural | `historical_price_scanners.py:242` | `False` | kept `False`; `structural_not_required` |
| `retracement_entry` | structural | `historical_price_scanners.py:242` | `False` | kept `False`; `structural_not_required` |
| `retracement_entry` | structural (required True) | `historical_price_scanners.py:271` | `True` | kept `True` on `mss_fvg_refinement`; not recorded as not-required |
| `tdo_required` | structural | `historical_price_scanners.py:232` | `branch=='asia_tdo_case'` | kept computed value; `structural_not_required` when False |
| `vwap_reset_verified` | operational_assumption | `historical_price_scanners.py:309` | `True` | kept `True`; `literal_operand_kind=operational_assumption`, `assumption_id=A2-GB-CLOCK` |
| `arrival_read_recorded` | unevaluated | `historical_auction_scanners.py:49` | `True` | bound to `None`; `unevaluated_operand` |
| `alignment_ok` | unevaluated | `historical_auction_scanners.py:51` | `True if control else None` | bound to `None`; `unevaluated_operand` |
| `profile_allows_trade` | unevaluated | `historical_auction_scanners.py:46-47` | `ref['low']<=poc<=ref['high']` | bound to `None`; `unevaluated_operand` |
| `ltf_balance_broken` | by_construction | `historical_auction_scanners.py:103` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `actual_band_contact` | by_construction | `historical_auction_scanners.py:234` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `real_extreme` | by_construction | `historical_flow.py:170,177` | `origin<=ref['low']+Q or origin>=ref['high']-Q` | restored frozen expression; `literal_operand_kind=by_construction` |
| `selected_deviation_touched` | by_construction | `historical_flow.py:204` | `True` | kept frozen; `literal_operand_kind=by_construction` |
| `same_band_retest` | by_construction | `historical_flow.py:240` | `True` | restored; `literal_operand_kind=by_construction` |
| `kg1_retest` | by_construction | `historical_flow.py:244` | `True` | restored; `literal_operand_kind=by_construction` |
| `microbalance_frozen` | by_construction | `historical_flow.py:346` | `True` | restored; `literal_operand_kind=by_construction` |
| `zone_definition_recorded` | by_construction | `historical_process_scanners.py:38` | `True` | restored; `literal_operand_kind=by_construction` |
| `instrument_and_threshold_preserved` | by_construction | `historical_process_scanners.py:39` | `True` | restored; `literal_operand_kind=by_construction` |
| `thesis_recorded` | by_construction | `historical_process_scanners.py:41` | `True` | restored; `literal_operand_kind=by_construction` |
| `label_uses_only_post_touch_observations` | by_construction | `historical_process_scanners.py:43` | `True` | restored; `literal_operand_kind=by_construction` |
| `cycle_and_indicator_rules_recorded` | by_construction | `historical_process_scanners.py:165` | `True if reconstruct else None` | restored frozen value; `literal_operand_kind=by_construction` |
| `actual_account_or_trade` | not a predicate operand | `historical_process_scanners.py:242` | `False` | left unchanged (`published_arithmetic` metadata) |

f7 also reported that O065, O066, O067, O068, O069, O072, O087 and O116 are referenced by no historical scanner. That is a missing-stage assignment (P15-05 / family adapters), not a B0.1 operand rebind.
