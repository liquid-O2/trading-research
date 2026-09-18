# Context inventory: what each author reads before and during a trade (2026-09-18)

User direction, 2026-09-18: the context is more than one comparison; the overnight range and its size, how the profile looks, the news week and the rest all belong to the strategy. This file lists every context read the source states, where the code computes it, and the selection feature that carries it. A read is RECORDED for the selection layer, never a gate, unless the source makes it a rule of the play. Features live in `implementation/tools/day_context_features.py` (day and moment) and `implementation/tools/grading_features.py` (the level and its profile); both are added to every row by `tools/build_selection_dataset.py`.

## Jumbo (Time-Based Ranges Framework, page in brackets; JR = his X archive)

| read | source | computed in | feature | status |
| --- | --- | --- | --- | --- |
| size of the 6-9 range, his size bins | [12] "the size of the ONS range will give you a hint whether we will have a false breakout or just a breakout", range table [13] | `jumbo.range_class` | `day_range_pct`, `day_range_bin`, `day_big_range` | built |
| extended overnight range | [12] scenario 1, [24] "Extended Overnight Session ... targets limited to the high and low of the overnight range" | `day_context_features.jumbo_day` | `day_overnight_range_pct`, `day_overnight_vs_box` | built 2026-09-18 |
| overnight liquidity purged, edges still drawn | [11] purge confluence, [12] scenario 2 "every significant overnight liquidity has been purged" | `jumbo._purge_state`, `drawn_levels` | `day_overnight_purged_high/low`, `day_overnight_balanced`, `day_edges_still_drawn` | built, feature added 2026-09-18 |
| relative strength between indices overnight | [12] scenario 2 | `jumbo_context.sister_index` (NQ against ES: who took the prior session's extremes, overnight travel) | `day_sister_divergence_high/low`, `day_nq_minus_es_overnight_pct`, `side_on_sister_divergence` | built 2026-09-18 |
| open against prior value and the prior RTH range | [32]-[34] PD RTH Range+; JR p.34, p.42 (pRTHVAH / pRTHVAL / POC) | `jumbo.session_context`, `prior_value_area` | `day_open_location`, `day_rth_open_location`, `day_open_inside_value`; level distances `prior_day_vah/val/poc_distance` | built |
| the day's play and direction | [8] Judas model, [12] single breakout, JR day reads | `jumbo.session_read` | `day_classification`, `day_primary_play`, `day_aligned`, `side_with_day_direction`, `play` | built; a feature since 2026-09-18, no longer a gate on the candidate list |
| the value-area layer of the range | JR p.10, p.11 ("VA 0.28%", "VA 0.45%", May 2026) | `jumbo.box_geometry(market, "ny_value" / "london_value")` | `day_value_range_pct`; its lines are candidates | built 2026-09-18 |
| news week: CPI, NFP, FOMC and the days before | [22] table, [23], [24] | `jumbo_context.news_week` on the owned calendar (`data/free-sources/context__event-calendar__normalized`) | `day_news_tier`, `day_news_release` | built 2026-09-18 |
| 10:00 release delays cycle 2 | [18] | none: no 10:00 release calendar on disk | `day_ten_am_release` (always absent) | NOT built: needs a calendar of 10:00 releases (ISM, JOLTS, sentiment) |
| his time windows | [8], [15]-[19] the open, 09:40-09:50, out by 10:00, 9-12 frame; [36] lunch and PM | `day_context_features.moment` | `clock_window`, `minutes_from_open` | built |
| sessions correlation | [36] "AM Consolidation -> PM Expansion", "AM Expansion -> PM Consolidation" | `day_context_features.moment` | `am_range_vs_box`, `am_close_position` (decisions after 12:00) | built 2026-09-18 |
| price signature at the level | [20] rejection wicks, [27]-[29] orderblock and rejection block on 2, 3, 5 minutes | `jumbo.confirm_pack` | fill `mode`, signature kind | built |
| volume signature: absorption candle, volume divergence | [31], [35] small body, volume above a multiple of the 14-period average; [37] | `day_context_features.moment`; `jumbo.confirm_pack` absorption | `trigger_relative_volume`, `trigger_body_share` | built 2026-09-18 |
| big executed trades at the level | JR p.50 "100 threshold on NQ during NY and 75 during London" | `grading_features.aggression_features`; `jumbo.BIG_PRINT_CONFIRMATION` fill | `aggression_*` | built |
| three-strike rule | [37] "attempts to reverse 3 times at a level without follow-through" | sweep cycles and contacts | `cycle`, `prior_touches_session` | built as a feature |
| how the profile looks at the level | JR profile panels; FIND p.8 HVN / LVN shelves | `grading_features` | `prior_day_shape`, `developing_shape`, HVN / LVN / ledge / POC distances (prior day, overnight, RTH, composite), naked POCs, delta prints | built |
| SessionStat envelope, EVRange, P-zones | SessionStat+.pdf; JR printed frames | `jumbo.sessionstat_envelope`, `generated_evrange`, `generated_pzones` (fitted recipes) | levels and `coincident_levels` | built (recipes fitted: his tools are proprietary) |
| aggressive entry at the orderblock midpoint | [28] | none | none | NOT built: an entry mode, to add with the entry-side upgrades |
| expectations: targets and risk by condition | [24] | none | none | parked with exits (user direction 2026-09-18) |

## Green Bird

Built and carried as features: the day model (sweep-and-fail or pullback day), the bias the overnight sets and whether a trade is with it, the overnight span in percent of price, the open held beyond both session boxes, whether a weekly level is within reach, the overnight events, the clock window, the morning behind an afternoon trade, the volume signature of the trigger minute, and the level's profile, delta and aggression features. A page-by-page pass of his archive against this list, like the one above, is still to do.

## Open items

1. A 10:00 release calendar (Jumbo [18]).
2. Jumbo's aggressive orderblock-midpoint entry ([28]).
3. Green Bird's page-by-page context pass.
