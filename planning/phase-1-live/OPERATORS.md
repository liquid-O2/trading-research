# Operating methods from the sources

Planning compilation, 11 September 2026. An operating method is the author's ordered decision loop: how the situation is framed, where action is allowed, what must happen there, and how the position and the next decision are handled. A range, profile, probability, footprint print, or management technique is not automatically another method.

The source review covered all 41 PDFs listed in §12: 711 pages of text, diagrams, charts, settings, and other images, including enlarged inspection of the figures. Repeated images were matched across copies. The media archive is used only with its matching PDF post. Raw posts and their figures take precedence over the introductory summaries, findings documents, wiki, and existing rule tables.

The resulting organization is:

| Author / attribution | Operating method | Treatment |
|---|---|---|
| JJumboFX | SDRange / Time-Based Ranges framework | One operating loop, with Judas, single-break, internal-rotation, extension, and session variants. |
| Green Bird Trader | Failed breakout / failed breakdown; “sweep → reclaim → opposing liquidity” | One reversal method across different references and retracement locations. |
| Green Bird Trader | VWAP continuation | Separate: the author explicitly distinguishes it from his usual reversals. |
| Green Bird Trader | Directional scalps / pullbacks into discount | Used in the record, but the complete trigger is unpublished. Preserve as an incomplete method description. |
| Sires / Ethos | Thesis, risk, and order flow; a framework for continuation and balance | One operating loop with distinct, explicitly gated execution branches. The session-recap titles are not separate systems. |
| Saint | AMT on live markets; continuation through balance and a defended retest | One method across his four PDFs; retain his profile interpretation and preferences separately from Sires. |
| Unnamed member, reported by Sires | Prior reaction area plus minor high-volume node | The member's own thesis and execution application; KG1 is an additional input. |
| Keani, discussed by Sires | Open above value | His own ordered opening setup, not a universal Sires opening rule. |
| Sires × TeamVOT | The Refill Effect | A zone-touch research and execution study. Touch grading is not an independently established mechanical entry edge. |
| jetbundle | Provide / withdraw / consume; B–A–D–E–W states | An auction-reading and transition-analysis method, not an automatic trade signal. |
| Stoic | Data engine; quantifying fundamentals | A research process, with a macro-analysis application, not a disclosed entry system. |
| Stoic | Asymmetric compounding | A separate risk overlay that requires an already validated trading process. |

## 1. Phase 1 scoring contract

The predicates below check **source-sequence fidelity**, not profitability. A losing trade can follow a method; a profitable move cannot repair a missing prerequisite. Record subsequent target reach, invalidation, excursion, and management separately.

Each predicate is a SQL Boolean expression over one proposed `operator_input` row per candidate episode. These are planning specifications for a scorer, **not claims that this input view or a complete operator scorer already exists**. A scorer can evaluate the expressions on source-annotated fixtures; automatic discovery is missing where the source or current objects do not supply the required fields.

Common inputs and semantics:

| Input | Meaning |
|---|---|
| `candidate_id, operator_id, branch, author, source_ref` | One author, one specified branch, file/page and, where available, post and figure. Re-entry is a new candidate linked to its earlier attempt. |
| `base_ok` | Source/figure identity, instrument, contract, tick unit, clock conversion, and event association are correct; every decision input was available by its use. No final-day profile, later extreme, future label, or later-selected “best” touch supplies a prerequisite. |
| `coverage_ok` | The observations needed for this candidate and branch are present. Missing aggressor, depth, source settings, or intrabar ordering are recorded as missing. |
| `map_at, context_at, touch_at, confirm_at, decision_at` | Ordered observation keys, with timestamp and a tie-breaking event ordinal. A bar confirmation is known at its close. A completed window is known at its end. When OHLC cannot order two events within a bar, the order is unknown. |
| `source_*` / descriptive Boolean fields | The complete observation described beside that predicate, with its evidence and availability time. An unspecified numeric detector may be replaced by a declared research variant, but cannot silently become author-exact. |
| `risk_defined` | Entry-side invalidation and the selected management policy were recorded before the decision. A drawn ticket is distinguished from an order, a fill, and a later outcome. |
| `objective_fixed` | The source objective's identity, side, bounds, and availability are recorded before the decision. A destination is not selected using the eventual high or low. |

Preserve SQL's three-valued logic. For the Boolean `sequence_ok` returned by a method expression:

```sql
CASE
  WHEN base_ok IS FALSE OR sequence_ok IS FALSE THEN 'fail'
  WHEN base_ok IS NULL OR coverage_ok IS NOT TRUE
       OR sequence_ok IS NULL THEN 'unknown'
  ELSE 'pass'
END
```

Unknown is neither a passing setup nor a negative market example. Report pass/fail/unknown counts, the eligible episode denominator, and the missing stage. A source conflict can leave a field unknown even when market data exist.

For each qualified entry, record `target_at` and `invalidation_at` only after `decision_at`. The target-first observation is:

```sql
target_at > decision_at
AND (invalidation_at IS NULL OR target_at < invalidation_at)
```

Here a null invalidation time means **observed not to occur during a fully covered, declared outcome window**, not missing data. Otherwise the outcome is unknown. Record no-hit/censored and unresolvable same-bar order separately. The window, touch tolerance, and price-versus-close invalidation convention must be stated. The common grid in [FORMULAS] §0.2 / P3-03 is a research measurement convention; its two ticks, half-range rejection, 15-minute reversal, 30-minute hold, and 30-minute fail-back cap are not universal author rules.

The code references below point under [the current implementation directory][CODE]. “Partial” means useful ingredients exist; it does not certify the caller, event order, or whole method. [RULES], [FORMULAS], [AUDIT], [AUDIT-F], [SCORES], and [WIKI] were read as prior compilations. Their row names and “match” labels do not override the sources.

## 2. JJumboFX — SDRange / Time-Based Ranges framework

**Why one method.** The manual calls false breakout/Judas and range breakout applications of the same time-based framework ([TBR] pp.6–12). The raw record says “same ranges, different layers” on 15 May 2026 and “same 6-9 framework, more refinement” when adding order flow on 23 February ([JR] pp.11, 14, posts 2055344660986364371 / 2026059018750378427). The later summary is the author's own ordered phrase: context, location, confirmation ([JR] p.33, post 2093335135789719861).

### Ordered loop and attachments

| Step | Source operation, in order | Existing attachment / missing work |
|---|---|---|
| 1. Choose the session and freeze its geometry | Select the range being traded. Main NY formation is 06:00–09:00 ET; draw H/L, width, EQ, quadrants, range open/close and projections. The manual also lists Asia 20:00–20:30, midnight 00:00–00:30, London 03:00–03:30, 09:30–10:00, 10:00–10:30, lunch 12:00–12:30 and 15:00–15:30. These are applications of the framework, not eight entry products. ([TBR] pp.4–7.) | `clocks.CLOCKS/clock_bounds`, `sessions.build_session/projections`, `family_clocks.build_clock_table` and range/path producers; [FORMULAS] P3-01/P3-06, R-J05/J09/J23. Basic frozen H/L geometry exists. A faithful source-selected clock, source range-open identity, and the newer inner-range geometry are only partial. |
| 2. Set expectations before the entry | Read overnight size and balance, liquidity already purged, open versus previous RTH value/range and today's box, news, and current behavior. Wide/extended overnight and range-bound news conditions reduce targets and risk; compressed/purged conditions can favor single-direction expansion. The raw July examples include continuation from outside value while still inside the prior price range: “outside both AND high RVOL” is a particular case, not the only permission to continue. ([TBR] pp.12, 16–24; [JR] pp.33–39, 48–49.) | `family_open.build_open_table`, `sessions.width_bin/_purged`, `family_levels.build_level_table/load_red_folder`, `formulas_jumbo.j21_class/j21_targets`; R-J03/J04/J05/J06/J07/J20/J21. Partial: purge chronology, event-time news, and contextual classification. Final single/double-break labels are outcomes. First-five-minute RVOL cannot inform a 09:30 decision. |
| 3. Choose a location and a destination within that case | Exhaustion beyond a swept edge, EQ/quadrants on internal entries, 1.33–1.66 after expansion, or a source-drawn P-zone/expected-range boundary. Preserve separate identities for 6–9 EQ, EV midpoint, SessionStat bands, P-zones, and RTH/profile references. Mark the remaining directional objective before acting. ([TBR] pp.8–24, 31–35; [JR] pp.3, 23–26, 48, 53–57.) | `sessions.projections`, `family_env.build_env_table`, `formulas_jumbo.band_133_166/j10_draw/j19_draw`; R-J01/J02/J08/J10/J11/J12/J13/J19 and P3-02. Geometry/approximation only for several rows. Exact EV, P-zone, and SessionStat minimum-average construction is missing. A time-stamped, source-scoped remaining-liquidity ledger is missing. |
| 4. Let the selected location produce the selected entry signature | The manual's favorite reversal entries use 2/3/5-minute orderblocks or rejection blocks; they are expressly personal entry choices, not fixed to the model. Later charts add absorption candles, BigTrades, footprint/profile behavior, and refinements at the same range levels. Use the confirmation actually present in that source episode. ([TBR] pp.27–31, 35; [JR] pp.14, 48, 50, 52, 67–69.) | `formulas_jumbo.j18_ob_bull/j18_ob_bear`, `family_gap`, `family_levels`, `family_tape._big_at`, `j15_bigtrade_at_level/j16_two_sided_at_eq/j17_node_under`; R-J14–J18. Partial. Current full-RTH profile/median inputs and London prints compared with a later 6–9 box do not establish a contemporaneous confirmation. |
| 5. Enter with the case's risk and target policy | Choose immediate, retracement, or stop-triggered execution and structural invalidation. The OB example distinguishes a midpoint stop/entry from a conservative boundary stop. Size and target ambition depend on the case. Do not turn a ticket's points or R:R into a universal preset. ([TBR] pp.24–29; [JR] pp.3, 54–57.) | `j18_ob_*` exposes block/mid/stop; `j21_targets` and `j24_management` relate to risk/targets; R-J18/J21/J24. Missing: source entry choice, actual entry timestamp, stop policy, partials and adds tied to that entry. |
| 6. Manage, recognize failure, and reassess | Take the appropriate internal/opposite/external objective, protect or compound justified winners, and reduce ambition in grind. Three failed reversal attempts at the same level, strong bodies/volume continuing through it, or absent rejection defeat a reversal idea. Exit and observe; if continuing after failure the manual says reduce allocation at least 50%. Reassess another case/session rather than relabel the failed fade as a successful breakout. ([TBR] pp.24, 36–37.) | `j22_three_strike/j22_failed/j24_management/j25_mid_retrace_hold`; R-J20–J25. Partial: three touch bars are not three distinct attempts; whole-window extrema are not post-entry excursions. The attempt/management ledger is missing. |

### Branches inside this loop

| Branch | Source sequence and objective | Boundary on interpretation |
|---|---|---|
| `judas_outbound` — Judas Trade #1 | At the 09:30 open, take the contextual move toward the selected exhaustion projection; close as the 09:40–09:50 reversal window arrives. ([TBR] pp.8–10.) | The direction and exact entry selection are not supplied by the later double-break label. This is an outbound leg, not the reversal entry. |
| `judas_reversal` — Judas Trade #2 | A completed range edge is swept; the exhaustion area produces a reversal signature, normally in the manual's 09:40–09:50 window; trade back through internal levels toward the opposite liquidity/projections. ([TBR] pp.8–11, 27–29.) | A mandatory exact ±0.5 touch is too narrow. Raw charts include shallow edge sweeps. Record depth; do not choose the deepest eventual excursion retrospectively. |
| `single_extended` | Extended overnight: wait for an EQ/quadrant entry in the allowed direction, usually take the range edge, moderate risk and expansion expectations. ([TBR] pp.12–14, 24.) | The eventual “single break” cannot be an entry-time input. “Extended” has no author-exact universal width ratio. |
| `single_purged` | Overnight stop hunts have already removed the relevant liquidity; the contracted range supports expansion from EQ/quadrants. 09:40–09:50 can be a continuation/add window, not a compulsory reversal. ([TBR] pp.12–15.) | Preserve the actual overnight references and when they were taken. Containment of two completed boxes is not a purge-time ledger. |
| `internal_rotation` | In the appropriate wide/in-value context, take confirmed rotations at EQ/expected-range locations, with nearer objectives. The 2 September raw example explicitly trades EQ both ways on a big 6–9 range and includes two losing attempts. ([JR] p.3, post 2095172969035096454; pp.38–43.) | EQ is a location; the author does not publish “touch EQ = reverse.” EV and EQ are different targets. |
| `extension_reaction` | After range expansion reaches the 1.33–1.66 area, examine rejection/continuation and the still-owed objective. The September 9 example combines session-average lows, that extension area, and equal highs as the long's destination. ([TBR] pp.20–21; [JR] pp.23–26, 57, 71.) | Extension touch, HOD/LOD in the band, and a confirmed reversal are different observations. Each projection uses its actual parent range width. |
| `other_session` | Apply the selected geometry and signatures to the observed London or later-session case. AM consolidation can precede PM expansion; AM expansion can precede PM consolidation. ([TBR] pp.7, 36; [JR] pp.46, 50–51, 63–66.) | Modern London charts freeze a box before the marked action; the retained 00:00–03:00 assumption is not a verified universal author clock. A source-known clock is required. “London is cleaner this cycle” does not publish a rolling-ten-day selector. |
| `timed_pzone_reversal` | Use the actual time-anchored P-zone and observed reversal sequence. The January 2 post's “low > range open” describes a path from the low to the range-open line; the December 17 post's “10 am p-zone > london low” names another path. ([JR] pp.53–55.) | The arrow is not an inequality. A 09:00 zone anchor is not proof of a 09:00 fill. Later time-specific examples must not be forced into the manual's 09:40 window. |

**PD RTH Range+ is a context/destination application.** It uses prior 09:30–16:00 highs/lows and M15/H1 imbalances, waits for current RTH direction, then trades toward those objectives with the range framework. In this expressly RTH-only view, an ETH sweep does not consume the RTH objective ([TBR] pp.32–35). This exception does not erase overnight purge information in `single_purged`. R-J19 / `j19_draw/j19_pd_touch/j19_htf_fvg` attach here; the current caller's final-path direction and whole-AM reach are insufficient.

**SessionStat, EV, P-zones, and flow are not standalone trades.** SessionStat's average/median high-low areas, minimum-average levels, projection extensions, selected session, and lookback frame likely reach/exhaustion ([SS] pp.3–12); its choppy/low-volatility limitations remain part of the read. The source settings do not publish the exact minimum-average engine. P-zone settings show learning-window/percentile controls, not a recoverable formula ([JR] pp.16–18, 58–62). Newer nested profile/range spans must not be mistaken for outer 6–9 width or automatically named EV.

Jumbo explicitly distinguishes BigTrades from absorption bubbles and gives **NQ 100 during NY, 75 during London** ([JR] p.50). An MNQ chart is not evidence for an NQ print-size threshold. The Absorption Zone+ settings actually display body threshold **0.6**, volume multiplier **1.5**, and a **14-period** volume average ([TBR] p.35); the old “unprinted” claim is wrong. Those settings still do not prove passive replenishment. The OB is the second candle's full range; a rejection block is its rejection wick. The two “midpoint” stop captions on p.29 conflict with the differently drawn stops; retain the fixture's geometry and mark the generic conservative rule unresolved.

### Phase 1 predicate — `JJ-TBR`

The branch fields below are observations made by the decision time: `extended_context`, `purged_compressed_context`, `rotation_context`, and `directional_context` are source-context labels, not final-session path classes. `source_confirmation` identifies the chosen OB/rejection/flow signature and its location/side. `source_time_window` is the documented timing for that particular branch/fixture.

```sql
range_frozen AND context_fixed AND location_touched
AND source_confirmation AND risk_defined AND objective_fixed
AND range_known_at <= touch_at
AND context_at <= touch_at AND touch_at <= confirm_at
AND confirm_at <= decision_at
AND CASE branch
  WHEN 'judas_outbound' THEN
    directional_context AND at_rth_open
    AND objective_is_selected_exhaustion AND exit_window_recorded
  WHEN 'judas_reversal' THEN
    reversal_context AND edge_swept AND sweep_at <= confirm_at
    AND source_time_window AND objective_is_opposing_draw
  WHEN 'single_extended' THEN
    extended_context AND entry_at_eq_or_quadrant
    AND objective_is_range_edge AND reduced_expectations
  WHEN 'single_purged' THEN
    purged_compressed_context AND purge_known_at < decision_at
    AND entry_at_eq_or_quadrant AND expansion_policy
  WHEN 'internal_rotation' THEN
    rotation_context AND entry_at_named_internal_or_ev_band
    AND objective_is_named_rotation_target
  WHEN 'extension_reaction' THEN
    prior_expansion AND touch_in_source_extension_area
    AND reaction_side_confirmed AND objective_is_remaining_draw
  WHEN 'other_session' THEN
    source_clock_verified AND source_case_verified
  WHEN 'timed_pzone_reversal' THEN
    source_zone_known AND source_time_window
    AND zone_known_at <= touch_at AND directed_path_recorded
  ELSE NULL
END
```

Citations for the sequence: [TBR] pp.6–12, 20–29, 37; [JR] pp.3, 14, 25, 33, 50–57. A source-drawn proprietary band can support a fixture check; an automatically generated approximation cannot set `source_zone_known` true. Report branch eligibility, confirmation, and directional target outcomes separately. Negative controls include momentum through an exhaustion level without rejection, a presumed purge occurring after entry, and a location/target picked from the final morning range. No current R-J predicate establishes this whole loop.

## 3. Green Bird — failed breakout / failed breakdown

**Source name and unification.** “Sweep → reclaim → opposing liquidity” is his own formulation ([GB] p.31). NYAM, Asia, prior hour, prior day/week/month, TDO confluence, and golden-pocket examples repeat this failure-and-reclaim mechanism. The raw golden-pocket explanation requires a failed breakdown and reclaim, or the PDL sweep followed by a five-minute close back below; the retracement band alone is not another strategy ([GB] pp.25, 31–35).

### Ordered loop and attachments

| Step | Source operation | Existing attachment / missing work |
|---|---|---|
| 1. Establish the reference and contextual direction | Finish the selected box or use a known prior level. NYAM is 09:00–10:00 and that box cannot be traded as finished before 10:00. Previous-hour examples use the completed hour. Asia's drawn box is approximately 20:00–00:00; exact London bounds are not stated. Prior day, previous weekly candle, previous month, and an already-observed overnight reclaim can supply the context. ([GB] pp.23, 25, 27, 30–35, 38–40.) | `clocks`, `family_fail.build_fail_table`, `family_levels.build_level_table`, `formulas.clock_hour_boxes`; R-G01/G02/G03/G04/G08/G09. Partial. Prior-week/month levels and a persistent bias/reclaim ledger are missing. Do not substitute prior RTH for every PDH/PDL or impose the inferred London clock as author-exact. |
| 2. Locate the potential failure | Watch the relevant high/low or reclaimed level. Optional confluence includes PDH/PDL, Asia/London, midnight TDO, and the 50–61.8% retracement of the explicitly measured impulse. TDO is the midnight opening price; NWOG is a destination between the Friday-close and Sunday-open references. ([GB] pp.21, 25, 27, 32–39.) | `formulas.gp_band_impulse`, TDO/NWOG/PD fields in `family_levels`; R-G05/G06/G07/G08/G09. Golden-pocket algebra exists, but the caller's selected impulse is not necessarily the source impulse. NWOG endpoint convention must match the source chart. |
| 3. Wait for the sweep and its failure | Sweep above and fail back below → short; sweep below and reclaim → long. The explicit PDL and Asia/TDO examples wait for a completed five-minute close. A sweep alone does not permit entry. ([GB] pp.21, 23, 25, 27, 30–35, 38.) | `family_fail._failback`, `formulas.reclaim_5m`, `grid.failback_wick_c5`; R-G01–G05/G08. Partial: `_failback` groups every five observed rows and stamps the first row, rather than guaranteeing a complete clock-aligned five-minute close. Its fixed 30-minute cap is not the author's universal rule. |
| 4. Enter after confirmation, with structural risk | Enter the reclaim or its retracement; the PDL reply says to wait a few points after the close and use a low-risk retracement. The 2025 example names MSS plus FVG as the execution refinement after the 9–10 high failure. The September 1 09:30 manipulation/reclaim long is a distinct timing branch, not an early completed 9–10 box. ([GB] pp.25, 31, 40, chart p.43.) | Failure geometry partly exists; event-linked retracement entry, MSS/FVG refinement, entry timing and structural stop are **missing**. R-G04's fixed opening window is a named approximation. The source does not prescribe one stop beyond the absolute sweep extreme for every case. |
| 5. Take opposing liquidity; manage the remaining position | Opposite box edge, intermediate 50%, TDO, prior/session extremes or NWOG as actually named. Take partials, move to breakeven once working, trail/leave the runner when appropriate, then stop the session. Size the quality of the setup; do not average down. ([GB] pp.25, 30–39.) | R-G01–G09 target ingredients exist, but most predicates stop at a daily failure/touch flag. Entry-conditioned target order, partials, stop changes, runners and session stop are **missing**. |

**Branches, not new products.**

- NYAM / completed hour / Asia failures use their own finished reference. A sweep during construction is part of the box.
- A prior-day/week/month reclaim can establish a bias for subsequent aligned pullbacks. Do not demand a fresh NYAM sweep for a separately cited prior-level trade.
- The golden pocket is `[L + 0.50(H-L), L + 0.618(H-L)]` for the illustrated retracement of a down impulse; direction and measured impulse matter. The September 1 source combines it with an actual PDL sweep and five-minute failure ([GB] p.25). The July example combines a fib pullback and hourly-low reclaim ([GB] p.35).
- The 09:30 manipulation branch is the source's below-open/reclaim long with a retracement objective and stop at the lows ([GB] p.40). Its confirmation duration is not fully specified by that reply; do not silently impose all parameters from the PDL example.
- A+ requires a relevant sweep; “no sweep = not A+” is a necessary quality condition, not proof that every sweep is A+ or that no other trade is allowed ([GB] pp.21–23, 37–40). R-G11 attaches to grading this candidate, not an OR across unrelated boxes somewhere during the day.

### Phase 1 predicate — `GB-FAIL`

`reference_px` is the swept boundary; `opposite_bound` is the other edge when the reference is a box. `box_return_ok` means the confirmation is back inside that finished box, or true for a single-level reclaim. `source_hold_confirmed` records the actual reclaim/hold observation when a five-minute rule was not stated. `tdo_required` is true only in the selected source variant.

```sql
reference_frozen AND bias_recorded AND risk_defined AND objective_fixed
AND reference_known_at <= sweep_at
AND context_at <= sweep_at AND sweep_at < confirm_at
AND confirm_at <= decision_at AND source_session_allowed
AND (
  (side = 'short' AND sweep_high > reference_px
                  AND confirm_close < reference_px)
  OR
  (side = 'long' AND sweep_low < reference_px
                 AND confirm_close > reference_px)
)
AND box_return_ok
AND CASE confirmation_mode
  WHEN 'five_minute_close' THEN complete_clock_five_minute_bar
  WHEN 'reclaim_and_hold' THEN source_hold_confirmed
  ELSE NULL
END
AND (NOT tdo_required OR source_tdo_close_confirmed)
AND (NOT pocket_required OR impulse_known_at <= touch_at
                            AND touch_in_measured_pocket)
AND (NOT retracement_entry OR confirm_at <= retest_at
                              AND retest_at <= decision_at)
```

Sequence citations: [GB] pp.21, 23, 25, 27, 30–35, 38–40. Outcome: the preselected opposing-liquidity objective after this entry, with source stop/management recorded separately. Examples that sweep and remain accepted outside fail this predicate. A 09:45 candidate using a final 09:00–10:00 box fails availability. A pocket touch without failure fails. Missing London bounds, prior-week/month data, or an unspecified reclaim detector leave the corresponding automatic check unknown.

## 4. Green Bird — VWAP continuation

This is explicitly separate. On 24 February 2026 he reports a break and close above **both London and Asia highs**, a retracement into VWAP, then a long. His reply says he consults VWAP for continuation, while normally trading reversals at time-based levels ([GB] p.33, posts 2026329904690712970 / 2026386393820283204).

| Step | Source loop | Attachment |
|---|---|---|
| 1 | Establish the London and Asia highs and the auction's continuation direction. | The GB clock/level ingredients above; source London bounds remain unresolved. R-G02/G09 provide references, not this method. |
| 2 | Price breaks and **closes above both** highs. | OHLC/close primitives exist; a joint, ordered GB continuation event is **missing** from [FORMULAS]. |
| 3 | Price subsequently retraces into the contemporaneous VWAP, the auction average. | `formulas_flow.running_vwap` and `family_value` supply VWAP ingredients. Its HLC3/bar-volume version is a declared approximation; the exact source VWAP reset is **missing**. R-F01's fade and R-F03's convergence are not this entry. |
| 4 | Enter long and manage the continuation. The post gives a 30-point stop and a 150-point result for this trade. | Source-linked entry and management are **missing**. Those numbers are one case, not a published universal stop or target-selection formula. |

**Not standalone:** a VWAP touch, one session high breaking, or an unrelated failed breakout. The source does not publish a short mirror or require Sires-style tape confirmation for this method.

### Phase 1 predicate — `GB-VWAP`

`vwap_reset_verified` is required for an author-faithful automatic check; a clearly named reset variant can be measured separately.

```sql
reference_frozen AND continuation_context AND risk_defined
AND london_known_at <= breakout_at AND asia_known_at <= breakout_at
AND breakout_close > london_high AND breakout_close > asia_high
AND breakout_at < retest_at AND retest_at <= decision_at
AND vwap_reset_verified AND vwap_known_at <= retest_at
AND retest_low <= vwap_at_retest AND retest_high >= vwap_at_retest
AND side = 'long'
```

Citation: [GB] p.33 and its chart. Score this **entry sequence** and later directional movement. General target selection is unpublished. Do not use the reported 150-point result as an entry condition or an assumed planned target.

### Used but incompletely specified — `GB-SCALP`

The September 2 post describes bearish-bias, 20–30-point short scalps with no reason to size up. September 10 describes NYAM-direction longs on pullbacks into discount, smaller size, and no compelling A+ setup ([GB] p.40, posts 2095257805242446135 / 2098075540607410229). The known loop is **directional read → favorable pullback/pop → small exposure → limited scalp/management → stop overtrading**. The entry/failure rule, impulse selection, exact invalidation, and general exit algorithm are missing. These posts cannot be silently assigned the VWAP trigger or fabricated into a “two boxes present” rule.

R-G10, premium/discount geometry, and GB level objects attach only to context/location. For a source-case scorer:

```sql
direction_recorded_before_entry AND small_size_recorded
AND source_directional_pullback_observed AND source_scalp_management_recorded
```

That is `case_description_ok`, not full entry qualification. `sequence_ok = NULL` for automatic method admission until the missing trigger is specified by evidence. The posts demonstrate that non-A+ trading occurs; they do not establish a reusable trigger or its performance.

## 5. Sires — thesis, risk, and order flow

**Source identity.** [C1] p.3 states the loop: form the thesis, define where it dies, trade while it lives, and recreate it when invalidated. [BIG] pp.14–18 explicitly places aggressive continuation and balance fades inside one framework. [CONT] p.12 says its three lower-timeframe confirmations expressed the **same higher-timeframe short thesis**. The payout/session titles therefore identify examples, not new operating systems. [C3] is by Sires and explicitly credits a recording with **orderxfilled**; that collaboration is retained without inventing another disclosed entry system.

### The operating loop

| Step | Source operation, in order | Existing attachment / missing work |
|---|---|---|
| 1. Define the model and account constraints | Define the features, regimes and products being traded; set the loss/risk constraints and news plan. The coaching blueprint then tests one change over a block of trades, rather than switching tools after individual losses. ([AVG] pp.17–20, 27–30; [C3] pp.3–7; [EMO] pp.3–8.) | The existing slice/coverage and report machinery can retain cohorts. The source model version, account limits, selected exit policy, rule-breach journal and one-variable review loop are **missing** from the operator objects. This is preparation, not a trade signal. |
| 2. Read the current auction and relevant larger structure | Map actual balances and imbalances, prior value, shelves/ledges, minor nodes, naked POCs, overnight inventory, current and composite structure, and the weekly/daily signed-delta evidence relevant to the idea. Use the current auction, not an arbitrary stale profile. Locate untouched objectives and recognize when a correlated market has already used its own objective. ([AMT1] pp.3–13; [VP2] pp.3–8; [TPO] pp.3–9; [MAMT] pp.4–17; [MATH] pp.12–14; [C1] pp.5–6; [K18] p.4; [K2345] pp.4–6.) | `family_open.value_area/scan_prior_rth_trade_vp`, `family_value.scan_rth_delta/build_value_table`, `mbp1_objects.vp_rth/tpo_trade_visited`, `formulas_jumbo.profile_nodes/profile_ledges`, `family_tape.build_weekly_delta_table`; R-A01–A18, R-F10/F11, R-R04, P3-04/P3-07/P3-08. Partial. Source-selected dealing/composite bands, reliable developing snapshots, native triad-object first-use, and an unfinished-object ledger are missing. |
| 3. Read the relevant regime, then write the thesis and death condition | When using the gamma framework, read the native 0DTE complex, flip/walls, location and current regime before setup selection; re-read after a large impulse. VIX/range completion, event expansion/crush and curve context modify ambition and risk. Write direction or a conditional reaction, objective and validity band. Structure break, value migration or new information can kill the thesis. ([GEX] pp.4–20; [VIX4] pp.3–9; [C1] pp.3–6; [ANAT] pp.4, 10.) | `family_gex._gex_day/build_gex_table`, `family_options`, `formulas.vix_preopen/vix_band`, `family_vol`, `formulas_flow.r_r03_thesis`; R-R01/R-R02/R-R03. Partial and sometimes the wrong construction: pooled 0–14DTE sign scenarios are not the source 0DTE dealer map; the thesis caller hard-codes away news/value changes. Proprietary KG levels, faithful flip/wall algorithms and first-invalidation timing are **missing**. |
| 4. Wait at a location allowed by that thesis | A real auction extreme, previously defended reaction/refill band, appropriate broken balance boundary, or the relevant VWAP deviation/anchored confluence. Mark the band before the trade. VA calculations may move; a fixed previous-day value reference is different from today's developing value. A first naked touch is not proof of defense. ([ABS] pp.5–8; [VP2] pp.4–8; [VWAP] pp.3–8; [ANAT] pp.7–10; [CONT] pp.4–8.) | `profile_nodes/profile_ledges`, `formulas_flow.running_vwap/r_f03_convergence`, `formulas_flow.r_s08_minor_node`; R-A16/A17, R-F01/F03/F11, R-S01/S07/S08. Partial. Automatic source band selection, event/swing anchors, and a same-band event join are missing. The POC-to-refill alignment checked **after** the trade in [CONT] p.9 cannot become a pre-entry gate. |
| 5. Read participation and result; choose one permitted execution branch | Reset/read the DOM at the level, distinguish aggressive effort from price reward, and observe actual replenishment, thinning, pace, delta/CVD and the relevant footprint structure. Run the branch below; do not combine the easiest Boolean from several unrelated times. ([DOM5], [DOM6], [DOM7] pp.3–7; [FP8], [FP9] pp.3–7; [ABS] pp.8–13; [STOP] pp.6–14; [BIG] pp.5–18; [OFM] pp.3–14.) | `mbp1_objects.cvd_from_trades/absorption_a/absorption_b/iceberg_touch_infer/footprint_4x/on_touch_refill`; `formulas_flow` helpers listed below; R-F01–F11/F14–F18 and R-S01–S05/S07/S08. These are partial ingredients. Full local, side-specific stage sequences, native range bars, the author's CVD reference and hidden-depth confirmation are missing or unverified. |
| 6. Fit structural risk to the account and execute | The controlling structure determines invalidation; size follows the stop distance and account constraint; an actual HTF objective determines available reward. Do not pick an attractive R:R and invent the structure to fit it. A modest initial R:R can be acceptable when the defense and management are sound. ([ANAT] pp.8–10; [C2] pp.3–7; [K18] pp.7–9, 14; [K2345] p.7.) | `r_s01_refill_long/short`, `r_s07_areas` and some ticket-distance fields exist. An event-linked structural risk/size/objective record and account-aware execution policy are **missing**. R-S07's fixed 15/35-tick examples are not the operating rule. |
| 7. Manage the position as control develops | Take the chosen static/partial or dynamic policy. Move to breakeven at a logical change in risk; trail behind newly confirmed protected highs/lows, not an unconfirmed wick. For the K18 short, a prior low must break and close with real aggression before the intervening high becomes protected. Add risk only after earlier risk is secured. ([RD] pp.4–5; [C2] p.5; [C3] p.4; [NYAM] pp.8–9; [K18] pp.8–14; [ANAT] p.10.) | `r_f10_protected_low` and R-F10 / R-S01/S05/S07 attach to structure and outcome measurements. Full confirmation timing, high-side mirror, stop-change ledger, partials and position-level aggregate exposure are **missing**. A final-AM low is not a protected low. |
| 8. Re-enter only on a fresh qualifying episode, or rebuild the thesis | A stop-out can leave the larger reaction band valid. Price must return inside that same band and produce fresh branch-specific confirmation; rerun location, reward/result and delta checks from zero. A thesis death requires a new thesis. A daily stop is not reset by calling the next attempt a re-entry. ([ANAT] pp.7, 10; [STOP] pp.6, 14–15; [CONT] pp.8–10; [C1] pp.3–4.) | R-R03/R-S03/R-S07/R-S08 are related pieces. Persistent thesis/band identities, distinct attempt IDs and loss-limit state are **missing**. |
| 9. Review process and distributions, then change one thing | Record thesis, confidence, regime, every attempted trade and breach; pause replay before the entry to state its reason; examine aggregate outcomes, MFE/MAE and account costs; revise a single model variable over a defined sample. ([C1] pp.6–7; [C2] pp.4, 6–7; [AVG] pp.27–30; [EMO] pp.6–8.) | `stats`/`report` can summarize valid observations. They do not supply the missing operator episode/journal or certify the old session flags as source trades. No new performance run is part of this compilation. |

### Auction routes that decide which execution is allowed

These are context-to-objective routes within Sires's loop. They are not a license to enter on a profile label.

| Route | Ordered read and destination | Formula attachment |
|---|---|---|
| Balance rotation | Establish balance; wait at a real outer edge; require the chosen fade confirmation; target POC/fair value and reassess before expecting the far side. ([AMT1] pp.7–10; [VP2] pp.3–8.) | R-A01/A05/A16; `a01_fade/a05_poc_tell/a16_stacked`. A prior-VA edge touch without the balance premise and confirmation is insufficient. |
| Accepted breakout / boundary retest | Balance or ledge breaks with participation and acceptance outside; return to the broken boundary; its defense permits continuation toward the next value area/objective. ([AMT1] pp.8–9; [MAMT] p.12.) | R-A02/A07; `a02_ledge_retest_hold/a07_break_retest`. Require break before retest at the same boundary. |
| Re-acceptance / rotation | Price leaves or opens outside value, returns inside and establishes acceptance; the directional read changes toward the opposite side. Two-period-inside and generic re-entry claims keep separate denominators. ([AMT1] p.7; [MAMT] pp.12, 18.) | R-A03/A04/A08; `a03_reentry_traverse/a08_reaccept` and held-inside primitives. “Inside for 30 minutes” is a declared approximation unless that source variant says so. |
| The **Failed Auction setup** | Established balance → break → actually tag an **older, separate balance's POC** → instant rejection → trade back toward the established balance's specified boundary. The source names VAH after rejection from above a prior POC and VAL after rejection from below; the schematic/fixture fixes which balance and side. ([MAMT] pp.9–11.) | R-A06; `a06_failed_auction`. The current caller passes the wrong POC identity and the helper's target does not reproduce the source geometry. Presence of a naked POC alone does not pass. |
| Full traversal with one side in control | Price traverses the whole balance without holding; subsequent retests trade with that side until contradicted. ([MAMT] p.12.) | R-A09; `a09_traverse_nohold`. The compiler's maximum traversal duration is not the source rule. |
| Overnight/open/day structure | Read overnight inventory and its LVN/shelf at the open, then the developing open/day type. A shelf's hold or aggressive break changes expectations. IB, single prints, excess, poor extremes, prior-session landmarks and MPOC inform targets and timing. ([TPO] pp.3–9; [AMT1] pp.10–13; [MAMT] pp.14–26.) | R-A10/A12/A13/A14/A15/A18. Final-day type is an outcome. The 94% either-overnight-edge and 73% MPOC statements are separate conditional claims, not entry probabilities; MPOC is not volume POC. |

The P/b sketches are not a universal directional switch: [MAMT] p.7's caption and diagrams do not consistently prescribe the same break direction, and Saint's P/b continuation explanations are his own. An LVN requires the appropriate profile structure on both sides; an outer taper alone is not the second transition back into balance ([MATH] pp.12–14; R-A17).

### Execution branches and their full predicates

All qualified Sires branches use:

```sql
thesis_alive AND auction_route_ok AND branch_regime_allowed
AND location_fixed AND location_touched AND objective_fixed AND risk_defined
AND thesis_known_at <= touch_at AND location_known_at <= touch_at
AND touch_at <= confirm_at AND confirm_at <= decision_at
AND sires_branch_ok
```

`thesis_alive` means no **observed** structure/value/news death before the decision, using the recorded death conditions. `branch_regime_allowed` has the scope the source gives it: [BIG]'s aggressive OFM is short-gamma-only; its balance fade is long gamma. Other examples retain their own regime evidence, including the disagreement near the flip in [K18] p.4. Do not invent a unanimously signed gamma gate for every historical Sires example.

Each row below defines `sires_branch_ok` for that named branch. Stage times refer to the same level, side and attempt.

| Branch / source name | Required ordered observation and SQL Boolean body | Existing attachment |
|---|---|---|
| `dom_rejection` — at-level DOM absorption | At a premarked level, arriving aggression makes little progress; observe actual rejection and additional opposing participation where the selected lesson requires it; enter behind the defended structure. `arriving_aggression AND little_progress AND local_rejection AND source_dom_confirmation AND aggression_at <= rejection_at AND rejection_at <= decision_at`. The iceberg refinement adds executed depletion → persistent replenishment → added participation within the illustrated two-tick area. ([DOM6] pp.3–7; [DOM7] pp.3–7.) | R-F06/F07; `aggressive_at_level/r_f06_dom_absorption`, `absorption_a/absorption_b/iceberg_touch_infer`. BBO reload inference is not verified hidden reserve or off-touch depth. |
| `absorption_reward_retest` — the four-check absorption reversal | A **fixed real extreme**, opposing aggression absorbed at a passive wall, actual reward by the new controlling side within the source's three-tick neighborhood, then a retest of that rewarded area with renewed defense/aggression; CVD must support the read. `real_extreme AND passive_wall_confirmed AND opposing_effort_no_result AND own_reward_confirmed AND reward_near_origin AND cvd_filter_ok AND fresh_reward_retest_defended AND absorption_at < reward_at AND reward_at < retest_at AND retest_at <= decision_at`. ([ABS] pp.5–13.) | R-F08 plus F02/F06/F07; `reward_3tick/r_f08_abs_four_check`. Reward location/window and the author's CVD reference are incomplete; the current first-AM-print origin is wrong. This source's pattern is a fade/local reversal, not a continuation of the same push. |
| `stop_four_stage` — defense, replenishment, exhaustion, lift-off | Location → initial defense → replenishment → the opposing aggressor's prints shrink → absorber turns aggressive and price lifts off; reward is illustrated as 2–4 ticks, entry within 1–2 ticks of confirmation; re-entry repeats every check and respects the stated −4R daily stop. `real_extreme AND defense AND replenishment AND opponent_thinning AND absorber_aggressive AND delta_filter_ok AND lift_off AND reward_ticks BETWEEN 2 AND 4 AND entry_distance_ticks BETWEEN 0 AND 2 AND daily_r_before > -4 AND defense_at < replenish_at AND replenish_at <= exhaust_at AND exhaust_at < liftoff_at AND liftoff_at <= decision_at`. ([STOP] pp.6–15.) | R-F09 with F02/F06/F07/F08; `digits_thinning/liftoff_upticks/r_f09_stop_stages`. The source's three-tick replenishment description is not automatically a three-event time horizon or the same as reward distance. ES digit examples are not universal NQ thresholds. |
| `footprint_confirmed_reaction` — level, absorption, intrabar POC flip | A valid level first, candle direction versus executed delta disagreement there, absorption, then POC relocation **within the candle**, supported by the selected DOM/delta read. `at_valid_level AND candle_delta_disagreement AND local_absorption AND intrabar_poc_flip AND source_flow_confirmation AND level_known_at <= absorption_at AND absorption_at <= flip_at AND flip_at <= decision_at`. ([FP9] pp.4–7.) | R-F05; `r_f05_absorption_stack` only partially attaches. Adjacent-candle POC positions or an entire AM treated as one candle do not implement the source. |
| `vwap_deviation_fade` — VWAP premium/discount reaction | An appropriate auction context and source session/anchor, price at a selected deviation, absorption/rejection plus CVD/ladder confirmation, then rotation toward VWAP or the named objective. `source_vwap_known AND selected_deviation_touched AND absorption_at_that_band AND cvd_filter_ok AND ladder_confirmation AND band_known_at <= touch_at AND touch_at <= confirm_at`. ([VWAP] pp.3–8.) | R-F01/F03 with F02/F06; `running_vwap/r_f01_vwap_fade/r_f03_convergence`. ±1/±2 are drawn, 2.5 and optional 3 also discussed; neither a blind ±2 touch nor an unrelated absorption is the method. |
| `ofm_aggressive` — Origin of the Move, aggressive drive | Repeated absorbed effort creates the catalyst; an attempted squeeze fails; price returns through the catalyst/refill area; renewed initiative takes the intervening wicks, the refill holds, and the entry is on the drive's retest with own-side aggression and CVD not against it. `short_gamma AND repeated_effort_no_reward AND first_squeeze AND squeeze_failed AND catalyst_reclaimed AND refill_held AND initiative_drive AND intervening_wicks_taken AND drive_retest_defended AND own_aggression_rewarded AND cvd_filter_ok AND catalyst_at < first_release_at AND first_release_at < failure_at AND failure_at <= refill_at AND refill_at < drive_at AND drive_at < retest_at AND retest_at <= decision_at`. ([OFM] pp.3–13; [BIG] pp.7–14, 18; [CONT] p.10.) | R-F15/F14/F17, R-S03/S04; `r_f15_ofm/r_f14_imb350/r_s03_second_defence/r_s04_ath_ofm`. The present `ofm_entry` can ignore its own release/failure/refill flags. The caller's final-AM extrema are not this sequence. |
| `ofm_passive` — the passive variant | The squeeze fails **without aggressive orders at the failure** as tape speed dies; the demonstrated long enters above the buyers, stop below the aggression, with a 1R–3R scalp objective. `source_squeeze_failed AND tape_died_at_failure AND no_aggression_at_failure AND buyers_area_identified AND entry_above_buyers AND stop_below_aggression AND failure_at < entry_trigger_at AND entry_trigger_at <= decision_at`. ([OFM] p.14.) | R-F15 is related but the distinct passive branch is **missing**. It must not inherit the aggressive branch's requirement for an aggressive failure print. The source calls it the same model's passive edition; no universal gamma condition is printed for this replay. |
| `clean_squeeze` — squeeze without the failed first attempt | Fast release from the catalyst without the prior OFM failure; on the first pullback, opposing aggression is absorbed and continuation is confirmed in the thesis direction. `catalyst_known AND fast_release AND no_prior_squeeze_failure AND first_pullback AND opposing_pullback_aggression_absorbed AND continuation_confirmed AND catalyst_at < release_at AND release_at < pullback_at AND pullback_at <= confirm_at`. ([CONT] p.11; [OFM] p.5.) | R-F18; `r_f18_squeeze/tape_speed_pps`. The current helper ignores its supplied catalyst/release in the trigger. “No failure” is only through the decision, not a future 15-minute survival test. |
| `balance_failure_fade` — failure of aggression in balance | Long gamma/balance, aggression at an extreme repeatedly goes unpaid, price leaves and retests the failed area, aggression there is still unpaid; fade toward where the opposite side **previously had control**. `long_gamma AND balance_context AND failed_aggression_at_extreme AND left_failed_area AND retest_same_failed_area AND aggression_still_unrewarded AND target_is_prior_opposite_control AND failure_at < leave_at AND leave_at < retest_at AND retest_at <= decision_at`. ([BIG] pp.14–15, 18.) | R-F16; `r_f16_balance_fade`. **Own-side aggressive reward and a squeeze are not required by this branch.** An opposite 6–9 edge is not automatically the source target. |
| `defended_band_continuation` — refill / minor-node continuation or re-entry | Established HTF direction and band; prior defense/control is visible; the return finds the same side defending/refilling with real participation; enter the confirmed continuation. A break above the short thesis's extreme with strong buying instead calls for a retest long toward VWAP. `prior_band_control AND same_band_retest AND fresh_same_side_defense AND executed_aggression AND refresh_consistent AND control_side_matches_thesis AND prior_defense_at < retest_at AND retest_at <= confirm_at`. ([NYAM] pp.4–5; [K18] pp.7, 11, 14; [CONT] pp.4–10; [ANAT] p.7.) | R-S01/S03/S07/S08 and F17; `r_s01_refill_long/short/r_s03_second_defence/r_s08_minor_node`. Missing: the band identity, local side-specific refresh sequence and actual flip branch. Price changes cannot stand in for executed delta. |
| `microbalance_break` — price-defined microbalance continuation | Within the established directional auction, a small price balance forms; price shows strength and breaks it; use the opposite side of that structure for risk and the pre-existing HTF objective, then trail confirmed structure. `microbalance_frozen AND directional_strength AND breakout_in_thesis_direction AND stop_behind_microbalance AND microbalance_known_at < breakout_at AND breakout_at <= decision_at`. ([K2345] pp.4–7.) | R-S05; `r_s05_microbalance`. Current code detects price runs but retains the last box and final-AM close. A fixed opening clock box or a future chosen box is not the source structure. |
| `kg1_retest` — KG1 retest with trailing convexity | Source KG1 level known → retest with aggressive confirmation → entry → trail as the trade develops. ([NYAM] pp.8–9.) `source_kg1_level_known AND kg1_retest AND aggression_confirms AND level_known_at <= retest_at AND retest_at <= confirm_at`. | The generic gamma/level and refill ingredients attach. The KG1 level engine and full trailing-convexity algorithm are **missing**; [K10] p.9 explicitly says the mechanism is not fully summarized there. A scenario gamma wall must not impersonate the KG1 level. |

These predicates preserve branch differences. They do not require every indicator in every source. Diagonal footprint stacks, same-price 350% displays, a candle POC, a big trade, delta divergence, tape speed and an iceberg hypothesis are **evidence at a location**, not independent entry products. When the chosen confirmation uses a stack, record the candle, side, actual row band, departure and later defended revisit ([FP8] pp.4–7; R-F04). For the 350% display, preserve its ratio convention and instrument: “350% more” and “3.5 times” are not automatically interchangeable ([BIG] pp.3–5). Never compare a CVD value with a price-unit median.

### Attempts and exceptions the source actually shows

The source record includes more than textbook confirmed trades. Preserve these observations without manufacturing complete automatic entry rules:

| Source case | Known loop and Phase 1 case predicate | Missing / interpretation |
|---|---|---|
| “Pre-file” / early buffer entries | Thesis → deliberately small pre-confirmation attempt → defined small stop → loss → unchanged thesis pending the actual test. `thesis_alive AND preconfirmation_entry AND small_risk_declared AND stop_predefined`. ([K18] pp.5–6, 14.) | The repeatable early-entry selector is unpublished. These are labeled B+ early attempts, not passes of the confirmed-refill predicate. `sequence_ok = NULL` for an automatic pre-file method. |
| Third retest with no new buyer defense | Prior tests of a support band → no fresh buyer defense on the third test → small short with stop just above → stop-out. `same_support_band AND distinct_test_count = 3 AND no_new_buyer_defense AND side = 'short' AND risk_defined`. ([NYAM] pp.6–7.) | The source explicitly says it is not a memorized third-touch guarantee. R-S02 / `r_s02_third_retest` attach to the case, but hard-coded zero defense volumes and adjacent touch bars cannot reproduce it. General trigger remains incomplete. |
| Late small resistance fade | Premarked resistance → an upward approach loses aggression candle by candle → small short near the session objective → session ends. `resistance_known_before_approach AND upward_approach_loses_aggression AND side = 'short' AND small_risk_declared`. ([NYAM] pp.10–11.) | Full entry timing and quantitative exhaustion threshold are not published. Keep it as a source-case check, not a newly invented universal detector. |
| Earlier refill entry in OFM schematic | Catalyst/failure → return to the refill → optional earlier entry with more risk, instead of waiting for the later confirmed drive/retest. ([OFM] p.6.) `source_refill_return AND explicitly_early_entry AND source_risk_predefined`. | The source distinguishes this choice from the later confirmation. It does not license omitting the retest from [BIG]'s aggressive branch. |

### Management and re-entry checks

Management is attached to the original entry and its chosen account policy. [C2] p.5 offers breakeven-then-trail, a trailing-distance example, and partial exits; [C3] p.4 distinguishes static/funded and dynamic/personal-account choices. The example numbers are not one mandatory rule for every session. [NYAM] pp.8–9 shows both target expansion and a trail; the pictured original risk box remains unchanged while the displayed target changes. Do not attribute the entire displayed 0.69→1.83 change to a shrinking initial stop.

A management scorer checks each action, after entry:

```sql
action_at > decision_at
AND action_matches_preselected_policy
AND supporting_structure_known_at <= action_at
AND (NOT stop_trailed OR protected_structure_confirmed)
AND (NOT risk_added OR earlier_risk_secured)
AND (NOT thesis_dead OR exit_or_new_thesis_recorded)
```

A re-entry candidate additionally requires:

```sql
same_band_id AND thesis_alive AND price_back_inside_band
AND fresh_confirmation_after_stopout
AND prior_exit_at < fresh_confirmation_at
AND fresh_confirmation_at <= decision_at
AND daily_limit_allows_entry
```

Citations: [RD] pp.4–5; [K18] pp.8–14; [ANAT] pp.7–10; [STOP] pp.6, 14–15; [CONT] pp.8–10. The new candidate must also pass its selected execution branch. A stop-out does not automatically kill the wider thesis, and prior confirmation does not automatically authorize another entry.

**Key fidelity limits.** The strict absorption reversal's “real extreme, not POC” restriction does not prohibit every other Sires setup from using POC as a destination or a different continuation context. [ABS] p.11 repeats contradictory directional annotations at its two extremes; its lower-side example cannot settle an exact signed-delta rule. [FP8] p.5's highlighted cells conflict with the stated diagonal ratio. The plotted CVD reference and “Speed of Tape (10)” reset/unit are unpublished. These remain unknown fields for author-exact automatic scoring. The current morning-level R-F/R-S booleans do not measure the complete operating loop.

## 6. Saint — AMT on live markets and confirmed alignment

[AMTL] p.12 explicitly describes its apparent setups as the same acceptance/rejection read applied at the area being tested. [WIC] p.10 names higher/lower-timeframe alignment as the whole method. [RTVP] p.6 states his preference for continuations and relatively infrequent reversals. Keep all four Saint PDFs together, and keep his decisions separate from Sires's.

| Step | Saint's ordered loop | Existing attachment / missing work |
|---|---|---|
| 1. Fit the higher-timeframe balance to traded structure | Identify accepted value and its actual extremes; redraw the balance until it fits the market before trading it. Read the profile: balanced distribution; two shelves and their connecting LVN; P/b with a formed balance at the head/base. An unbalanced trending profile is left alone until a new balance forms. ([RTVP] pp.3–11; [TRAP] pp.3–4.) | `value_area/profile_nodes/profile_ledges`, `family_value`; R-A01/A07/A11/A17. Source-selected HTF balance bands and separate sub-distributions are **missing**. The profile's name alone does not determine entry direction. |
| 2. Read arrival, acceptance/rejection and the controlling side | At the extreme ask whether price accepts or rejects; inspect how price arrived, executed delta and whether aggressive effort achieves movement. Heavy buying at an upper extreme can identify trapped buyers if repeated attempts fail. ([AMTL] pp.5–10; [WIC] pp.4–6; [TRAP] pp.4–5.) | R-F12/F13 and signed-delta/profile ingredients; `r_f12_arrival/r_f13_trapped_buyers`. Current session-median size or maximum-price inputs are not local arrival speed or delta concentration. The exact arrival-class thresholds and an automatic directional lookup are unpublished. |
| 3. Require the lower timeframe to agree | Wait through free two-sided chop. An actual intraday balance break followed by a held retest shows control; inspect the 15-minute view when the smaller chart is unclear. In the trapped-buyer example, two prior AM/PM failures support the thesis, but the current break/retest is still required. ([WIC] pp.7–10; [TRAP] pp.5–9.) | R-A07/A08, R-F13; `a07_break_retest`, `r_f13_trapped_buyers`. A side-specific, ordered HTF → LTF → same-boundary retest join is **missing**. Two separate historical failures cannot be supplied by duplicating today's AM high. |
| 4. Confirm at the retest and enter | Confirm real initiative in the intended direction; the short example has repeated aggressive selling inside candle bodies, with footprint and DOM agreement. If the retest is missed, do not chase; wait for another relevant area/test. If buyers take and defend the band instead, revise the directional read. ([TRAP] pp.6–12; [WIC] pp.8–10.) | `mbp1_objects` flow ingredients, `r_f13_trapped_buyers`; R-F13. Repeated local body aggression, reliable side identity and entry timing are **missing**. Green/red daily totals do not replace the retest. |
| 5. Target the actual next accepted area and manage the evidence | Initial destinations are POC/fair value, the other shelf, the far balance edge or prior balance. Repeated inability to cross and hold POC favors chop; aggressive passage, with a held retest where shown, supports travel to the far side. The TRAP ticket deliberately keeps the objective within a realistic Asia-range distance and uses normal risk. ([RTVP] pp.5–8; [AMTL] pp.8–11; [TRAP] pp.8–10.) | R-A03/A05/A07/A08/A11, `a05_poc_tell/a03_reentry_traverse` and target geometry. Entry-conditioned target progression and the complete structural stop policy are **missing**. Do not turn the example Asia distance or ticket profit into a constant. |

The failed-auction branch in [AMTL] pp.8–10 is **lower value tried → failure to accept → return into original value → read POC/acceptance again**. Its live example can dip deeply and take time to confirm. Do not import Sires's narrower instant rejection at an older POC as a mandatory condition for every Saint failed-auction read.

**Not standalone:** HTF bias, a large positive delta print, slow/fast arrival, P/b shape, an 80/20 claim, or a high-volume node. Saint's P/b examples start with an impulsive move, establish the new balance, then wait for its break/retest ([RTVP] pp.10–11). They do not license buying every P or selling every b. His choice to wait for rebalance on a trending profile also must not be replaced with Sires's permission to trade an established trend.

### Phase 1 predicate — `SAINT-AMT`

`alignment_ok` means the *current* HTF read and actual lower-timeframe control agree. `source_route_ok` chooses the documented path instead of pooling all profile conditions:

```sql
balance_fixed_before_use AND profile_allows_trade
AND arrival_read_recorded AND control_evidence_recorded
AND alignment_ok AND risk_defined AND objective_fixed
AND balance_known_at <= arrival_at
AND arrival_at <= control_at AND control_at <= decision_at
AND CASE branch
  WHEN 'continuation_retest' THEN
    ltf_balance_broken AND same_boundary_retest_held
    AND repeated_aggression_in_trade_direction
    AND ltf_balance_known_at < breakout_at
    AND breakout_at < retest_at AND retest_at <= confirm_at
    AND confirm_at <= decision_at
  WHEN 'trapped_buyers_retest' THEN
    prior_buying_at_upper_extreme AND two_distinct_prior_failures
    AND prior_failures_known_at < breakout_at
    AND ltf_break_down AND same_boundary_retest_held
    AND repeated_body_selling AND side = 'short'
    AND breakout_at < retest_at AND retest_at <= confirm_at
    AND confirm_at <= decision_at
  WHEN 'failed_auction_return' THEN
    older_value_tested AND older_value_rejected
    AND original_balance_reaccepted AND local_control_confirms_return
    AND older_value_known_at < older_value_touch_at
    AND older_value_touch_at < rejection_at
    AND rejection_at < reaccept_at AND reaccept_at <= decision_at
  WHEN 'poc_traversal' THEN
    original_balance_reaccepted AND aggressive_poc_passage
    AND source_poc_hold_confirmed AND target_is_far_balance_edge
    AND reaccept_at < poc_passage_at AND poc_passage_at <= decision_at
  ELSE NULL
END
```

Citations: [RTVP] pp.5–11; [AMTL] pp.8–12; [WIC] pp.7–10; [TRAP] pp.3–10. Preserve an explicitly sourced long mirror as its own side binding. A range still in “free game” with no confirmed control fails entry admission; an unobserved retest is unknown, not an assumed continuation. Measure POC chop versus passage and the subsequent source objective separately.

## 7. Unnamed member — prior reaction area plus minor HVN

This is the member's own model reported in [K10], not another Sires payout strategy. His original levels were higher-timeframe HVNs with prior clean reactions; KG1 supplied an additional compatible source, not a replacement ([K10] pp.4–6).

| Step | Source loop | Attachment |
|---|---|---|
| 1 | Before the session, identify the current auction phase, previously reacted areas and HTF objective; write the conditional thesis. ([K10] pp.5, 7, 12.) | Profile/composite and dealing-range ingredients; R-A16/A17, R-S06. Source-selected reaction history, objective and thesis record are **missing**. |
| 2 | Require the prior reaction area and an independently identified nearby minor HVN to agree. A KG1 reference may add an input where appropriate. ([K10] pp.6–7.) | `profile_nodes`, `r_s06_two_reason`. The first sorted OHLC HVN and a prior-day extreme are not necessarily these two reasons; the KG1 engine is missing. |
| 3 | Wait for the planned reaction: short on the resistance rejection, or long on the return/second tap when buyers absorb and hold. ([K10] pp.7–8.) | R-S06, local absorption ingredients. Current `two_reason` calls can pass without any actual contact; the complete contact/reaction join is **missing**. |
| 4 | Put risk beyond the relevant rejection structure; use the preplanned target, then the selected management method. ([K10] pp.7–9.) | `r_s06_two_reason` has illustrative stop/target arithmetic only. A faithful ticket/management ledger is **missing**. |
| 5 | Review written thesis quality and actual aggregate results, including evaluation costs and execution discipline. ([K10] pp.3–5, 10–15.) | Generic summaries attach only after valid episodes exist; the member's account/cost journal is missing. |

**Not standalone:** one HVN, a rounded resistance price, the cover's payout, or merely adding a KG1 level. The prose says 1.5R planned targets, but the short graphic shows a 1.00R ticket and the long graphic shows a later 9.60R expansion ([K10] pp.7–8). Keep these evidence states separate; neither the exact universal bracket nor the full trailing-convexity mechanism can be certified.

### Phase 1 predicate — `MEMBER-TWO-REASONS`

```sql
thesis_predefined AND objective_fixed AND risk_defined
AND prior_reaction_area_known AND independent_minor_hvn_known
AND confluence_band_defined AND actual_band_contact
AND area_known_at <= touch_at AND hvn_known_at <= touch_at
AND touch_at <= reaction_at AND reaction_at <= decision_at
AND (
  (side = 'short' AND resistance_rejection
                  AND stop_above_rejection_high)
  OR
  (side = 'long' AND planned_return_to_structure
                 AND buyers_absorb_and_hold
                 AND stop_behind_long_invalidation)
)
```

Citation: [K10] pp.5–8, 12. Score the structural sequence and post-entry outcomes in the instrument actually shown. A target-policy check is separate and unknown when the prose and ticket conflict. The student's case is not automatic evidence for transferring the same thresholds to another contract.

## 8. Keani — open above value

[AVG] pp.21–22 calls this **Keani's own setup**, which Sires then validates through AMT. It is separate from the unnamed member above.

| Step | Source loop | Attachment |
|---|---|---|
| 1 | Current TPO opens fully above yesterday's value: the entire A period is clear of prior VAH. Observe the developing profile around 10:00. | Prior profile/VA, TPO and `developing_va` ingredients; R-S09. Comparing the 09:30 open with a future current-day VAH is the wrong opening condition. |
| 2 | Value builds higher; observe rejection at POC or previous VAH within that bullish auction. | Profile/rejection primitives attach; the ordered value-build/rejection event is **missing**. |
| 3 | Price breaks the current developing VAH with aggressive buying imbalances. Freeze the actual imbalance prices and their known time. | `r_s09_open_above_value` and R-F04 stack ingredients. Developing VAH and the defended imbalance band are distinct objects. |
| 4 | Price returns to those imbalance prices; buyers defend them, with the DOM and time of day supporting the trade. | `r_s09_open_above_value` partially encodes retest/hold. The caller does not provide this same-band sequence or the DOM confirmation. |
| 5 | Enter long toward a worthwhile, preselected HTF objective, with defined risk. | Source-linked risk/target is **missing**. A clean retest into no objective does not pass the source checklist. |

All steps: [AVG] pp.21–22. **Not standalone:** an opening gap, `open > current VAH`, an eventual bullish day, or a break without defense on return. Around 10:00 is an observation point, not access to the finished day type. The displayed dashboard results and the document's data-collection discussion do not establish this setup's entry edge.

### Phase 1 predicate — `KEANI-OPEN-ABOVE-VALUE`

```sql
prior_value_fixed AND a_period_complete
AND a_low > prior_vah
AND developing_value_builds_higher AND source_rejection_observed
AND dev_vah_known_at <= breakout_at
AND breakout_close > dev_vah_at_break
AND aggressive_buy_imbalance_break
AND imbalance_band_known_at <= retest_at
AND breakout_at < retest_at AND retest_at <= defense_at
AND buyers_defend_same_imbalance_band AND dom_supports_long
AND time_of_day_allowed AND objective_fixed AND risk_defined
AND a_end_at <= observation_at AND observation_at <= breakout_at
AND defense_at <= decision_at AND side = 'long'
```

Citation: [AVG] pp.21–22. The source's near-10:00 observation does not define an exact universal minute tolerance. Missing that convention is an explicitly named timing variant. A developing-VAL short is not claimed as Keani's published mirror.

## 9. Sires × TeamVOT — The Refill Effect

The paper is jointly credited **Sires × TeamVOT** ([REF] p.1). Its object is a **return to a previously formed aggressive-print zone**, with pre-touch memory, construction, location and flow information. It is not a separate automatic “large print = trade” system.

| Step | Source research/execution loop | Attachment |
|---|---|---|
| 1 | Form the zone from clustered large aggressive orders, retaining instrument, side, price span and formation time; price then leaves. ([REF] pp.5–7.) | `on_touch_refill`, `r_f17_refill_zone`; R-F17, P3 refill object. Partial. Source clustering details and NQ/MNQ threshold normalization are unpublished; the code's ≥100/2-minute/2-tick rule is a variant. |
| 2 | At each later return, create a distinct touch event. Freeze memory of **earlier** defenses, construction, auction location and incoming flow **before this touch resolves**. ([REF] pp.6–9.) | Profile/flow ingredients attach. Full zone memory, distinct touch IDs and feature-availability ledger are **missing**. The outcome of this touch cannot define its own memory. |
| 3 | Grade the already-found touch under a frozen model and aligned thesis; retain the unselected cohort too. ([REF] pp.8–9, 16; [OFM] pp.15–18.) | The published classifier, feature transformations, complete hold label and selection threshold are **missing** from [FORMULAS] and current phase1 objects. Phase 1 can audit supplied grades and freeze observations; it does not train a new model here. |
| 4 | In the documented execution study, rest a limit 12 ticks inside the selected zone, 32-tick stop, 96-tick target, 30-minute cancellation, one position at a time; modeled round-trip cost is one tick and stop slippage one tick. ([REF] p.12.) | R-F17's penetration/hold helper is not this order lifecycle. Event-linked order placement, queue/fill assumptions, cancellation, bracket and cost records are **missing**. These are this research configuration, not universal Sires risk. |
| 5 | Separate filled orders from selected touches; evaluate untouched held-out sessions, independent-engine comparisons and robustness diagnostics. Keep fill assumptions, losing quarters and causal rebuilds visible. ([REF] pp.12–22; [OFM] p.18.) | Generic statistical summaries exist. Exact study reconstruction and its source-compatible cohort/event joins are **missing**. Current daily revisit flags are not the study's per-touch hold rate. |

**What survives the source's own correction.** [OFM] p.18 says the fully causal mechanical entry rebuild was negative, approximately −0.16R to −0.54R out of sample, and that the earlier positive selection used later-day information. It retains touch grading and the passive-side execution lesson. Do not certify an automatic positive entry edge by quoting [REF]'s earlier replay alone. The independent limit/market cohorts have different fill counts; they are not paired returns on identical filled trades. Reverse splits and rotating folds are diagnostic experiments, not forward-deployable estimates. Touch-or-trade-through fill assumptions do not prove real queue fills.

### Phase 1 predicates — `REFILL-STUDY`

The primary check is a causal zone-touch record:

```sql
zone_definition_recorded AND zone_frozen AND departure_observed
AND zone_known_at < departure_at AND departure_at < touch_at
AND distinct_touch_id AND thesis_recorded
AND feature_max_known_at <= touch_at
AND memory_uses_only_prior_resolved_touches
AND label_uses_only_post_touch_observations
AND instrument_and_threshold_preserved
```

If auditing a **supplied** selected-order record, additionally check:

```sql
grade_model_frozen_before_touch AND grade_available_at <= order_at
AND touch_selected_without_future_information
AND order_inside_ticks = 12 AND stop_ticks = 32 AND target_ticks = 96
AND cancel_minutes = 30 AND one_position_policy
AND round_trip_cost_ticks = 1 AND stop_slippage_ticks = 1
AND fill_assumption_recorded
```

Citations: [REF] pp.5–12, 16, 22; [OFM] pp.15–18. This second predicate verifies the documented configuration, not its profitability. If the grade/model or side/zone construction is unavailable, it is unknown. The default full mechanical-entry claim remains unsupported by the supplied sources.

## 10. jetbundle — participation and B–A–D–E–W states

[MATH] p.3 explicitly separates jetbundle's framework in pp.4–11 from Sires's NQ application in pp.12–14. They are not merged here.

| Step | Source loop | Attachment |
|---|---|---|
| 1 | Observe **provide, withdraw, consume** through submissions, cancellations and executions; reconcile the record with DOM/tape/footprint impressions. ([MATH] pp.4–6.) | `mbp1_extract` and trade/BBO fields in `mbp1_objects` provide limited ingredients. The illustrated AAPL ten-level order-book record and full order/depth event reconstruction are **missing**. |
| 2 | Measure participation and price-response efficiency, then whether opposite liquidity persists/replenishes or disappears. Efficient aggression is discovery; large executions alone are not absorption. ([MATH] pp.6–8.) | R-F06/F07 and `aggressive_at_level/absorption_a/absorption_b` are related partial observations. Full source efficiency and replenishment measures are **missing**. |
| 3 | Assign the heuristic current state: B balance, A absorption, D discovery, E exhaustion, W withdrawal. ([MATH] pp.9–10.) | The five-state classifier is **missing** from [FORMULAS] and implementation. AMT day labels are not these states. |
| 4 | Observe the next transition conditional on current liquidity and pace; distinguish state persistence from a change. Do not fade efficient discovery or continue leaning on absorption after replenishment fails. ([MATH] pp.7–11.) | Transition/cohort machinery for this state alphabet is **missing**. Generic rate tables do not reconstruct the illustrated state definitions. |
| 5 | Let the state evidence discipline discretion and sizing; it is not an automated entry instruction. ([MATH] pp.3, 10–11.) | No source entry/stop/target algorithm exists to attach. |

**Not standalone:** high volume, static book imbalance, displayed resting size, or the source matrix's numerical persistence. The 20,000-event AAPL example is an illustration with its own sampling and depth, not a universal NQ transition table. “A setup cannot have a fixed win rate” is the author's argument for conditioning the analysis; it is not adopted here as a mathematical impossibility.

### Phase 1 predicate — `JETBUNDLE-STATES`

With source-defined or explicitly annotated qualitative fields:

```sql
participation_record_complete AND response_record_complete
AND participation_known_at <= state_at
AND response_known_at <= state_at
AND CASE state
  WHEN 'B' THEN two_sided_executions AND recent_revisits
                AND low_aggression_both_sides
  WHEN 'A' THEN high_aggression AND low_response_efficiency
                AND opposite_liquidity_holds_and_refills
  WHEN 'D' THEN aggression AND efficient_displacement
  WHEN 'E' THEN prior_absorption_or_effort
                AND replenishment_stops AND level_gives_way
  WHEN 'W' THEN cancellations_dominate
  ELSE NULL
END
```

A transition row additionally requires `state_at < next_state_at` and `conditioning_known_at <= state_at`. Citations: [MATH] pp.5–11. Unpublished thresholds, missing cancels or off-touch depth make faithful automatic classification unknown. A declared BBO-only observation must retain that label; it cannot claim to be the full source method. There is no trade-admission predicate beyond this observation method.

## 11. Stoic — data engine and asymmetric compounding

### Data engine / quantifying fundamentals

This is Stoic's contribution in [DATA] pp.3–8, published in a Sires guide. Its ordered loop is:

| Step | Source operation | Attachment |
|---|---|---|
| 1 | Pick the concept, then define a reproducible execution/research process before collecting the sample. ([DATA] p.3.) | Existing object/fixture infrastructure is raw material. A versioned Stoic process specification is **missing**. |
| 2 | Collect every observation the same way; distinguish individual journaling from aggregate system-level data. ([DATA] pp.3–4.) | `slice/compute/stats/report` offer storage and summaries only. Process-specific inclusion and consistent field definitions are **missing**. |
| 3 | Compare all winners and losers, identify recurring differences, refine the process and repeat. ([DATA] pp.3–4.) | Generic summaries can attach after valid episodes exist. No source-complete Stoic trading recipe appears in [FORMULAS]. |
| 4. Macro application | Quantify trend strength, position versus historical averages, custom C-scores, standard deviations and macro cycle. For the bubble example: identify the cycle → examine leverage/credit/housing/valuation indicators → compare with history → reach a data-based verdict. ([DATA] pp.5–6.) | A dated economic calendar is only an ingredient. The source's macro series, release vintages, C-score formula, cycle classifier and decision thresholds are **missing**. |

The last step is an application of the data process, not a separate intraday entry. The source's historical bubble conclusion is not a current market verdict. Concepts, a macro label or one unusual release are not standalone trades.

Phase 1 — `STOIC-DATA`:

```sql
process_spec_frozen AND spec_known_at < sample_start_at
AND inclusion_rule_fixed AND uniform_schema
AND all_eligible_observations_retained
AND features_available_before_decisions
AND outcomes_separated_from_inputs
AND aggregate_winner_loser_comparison_recorded
AND revision_uses_only_prior_sample
```

For the macro application add `release_vintages_recorded AND historical_comparison_defined AND cycle_and_indicator_rules_recorded`. Citation: [DATA] pp.3–6. This measures the research process. Exact macro-model outputs remain unknown without its unpublished rules; no entry/stop/target strategy is disclosed.

### Asymmetric compounding

The risk overlay has different inputs and a different loop, so it stays separate:

1. **Establish eligibility.** An existing trading process must have at least 100 observations, known win rate and average R:R, and a Monte Carlo estimate of maximum loss streak; base risk must not exceed 1% ([DATA] p.8).
2. **First trade.** In the printed illustration, risk one baseline unit (1% of initial account units) for 3R. A win banks three baseline units ([DATA] p.7).
3. **Second trade.** Risk the original one plus the three just banked, four units total. A 3R win earns twelve more units; a loss leaves the two-trade sequence down one unit ([DATA] p.7).
4. **Reset after the second win.** Return to base risk and repeat. Retain the source's stated volatility and validation constraints ([DATA] pp.7–8).

**Not standalone:** a win streak does not generate a trade; this overlay consumes trades admitted by an already validated process. No corresponding risk-state object exists in [FORMULAS] or the implementation. Generic summary/bootstrap functions are not the source Monte Carlo loss-streak validation.

The page heading says the overlay activates on a “two trade winning streak,” while its explicit ladder increases risk **after the first 3R win**. Preserve that discrepancy. The following Phase 1 predicate checks the **printed ladder**, not an invented resolution of the heading:

```sql
validated_process AND prior_sample_n >= 100
AND win_rate_known AND average_rr_known AND mc_loss_streak_known
AND base_risk_fraction <= 0.01 AND base_risk_fraction > 0
AND CASE risk_stage
  WHEN 'first' THEN risk_units = 1 AND planned_reward_r = 3
  WHEN 'second' THEN first_trade_closed AND first_trade_result_units = 3
                     AND risk_units = 4 AND planned_reward_r = 3
                     AND first_trade_close_at < decision_at
  WHEN 'reset_after_second_win' THEN second_trade_result_units = 12
                                     AND next_risk_units = 1
  ELSE NULL
END
```

Citation: [DATA] pp.7–8. Units use the initial baseline of the printed illustration, so `3 - 4 = -1` and `3 + 12 = 15`; silently rebasing every percentage on the changed equity produces different arithmetic. Handling after other outcomes, the sizing denominator in a general implementation, and the heading's alternative activation rule are not fully specified. The generic overlay is therefore only partially reconstructable. This is a rule/arithmetic audit, not a new simulation or a profitability claim.


## 12. Source inventory and reconciliation

Page numbers are one-based PDF pages, including covers. Every PDF below was read in full and visually reviewed; the ranges in the method sections identify the evidence for that operation. Settings, numerical examples, contradictions and incomplete disclosures were retained according to their role. Marketing, account screenshots and decorative images do not create entry rules.

| Key / source file | Pages | Attribution and place in this compilation |
|---|---:|---|
| [JR] — JJumboFX_Raw_X_Archive_v2.pdf | 71 | JJumboFX; primary raw posts and figures; §2 |
| [GB] — greenbirdtrader-complete.pdf | 60 | Green Bird; raw records and charts outrank introductory summaries; §§3–4 |
| [TBR] — Time-Based ranges Framework (JJumbo).pdf | 38 | JJumboFX; range framework, entries and management; §2 |
| [SS] — SessionStat+.pdf | 12 | JJumboFX; statistical session framing within §2 |
| [XF] — xfcmg2.pdf | 48 | JJumboFX; duplicate raw-post coverage, reconciled with JR; §2 |
| [FIND] — jjumbo-findings.pdf | 14 | Secondary Jumbo findings; no additional independent method; §2 |
| [AMT1] — amt-lesson-1.pdf | 14 | Sires; auction routes and daily preparation; §5 |
| [VP2] — vp-lesson-2.pdf | 9 | Sires; profile location and objectives; §5 |
| [TPO] — tpo-lesson-3.pdf | 10 | Sires; time profile, auction completion and IB context; §5 |
| [VIX4] — vix-lesson-4.pdf | 10 | Sires; volatility context and risk; §5 |
| [DOM5] — dom-lesson-5.pdf | 8 | Sires; DOM, pace and spread reading; §5 |
| [DOM6] — dom-lesson-6.pdf | 8 | Sires; at-level aggression and rejection; §5 |
| [DOM7] — dom-lesson-7.pdf | 8 | Sires; executed replenishment and iceberg confirmation; §5 |
| [FP8] — fp-lesson-8.pdf | 8 | Sires; diagonal stacks, candle profile and revisit; §5 |
| [FP9] — fp-lesson-9.pdf | 8 | Sires; delta disagreement and intrabar POC flip; §5 |
| [VWAP] — vwap-lesson-10.pdf | 9 | Sires; deviations, anchors and confirmed reactions; §5 |
| [C1] — code-1-thesis.pdf | 8 | Sires; thesis lifetime, triad and codex; §5 |
| [C2] — code-2-risk.pdf | 8 | Sires; exposure and management; §5 |
| [C3] — code-3-orderflow.pdf | 8 | Sires, recorded with orderxfilled; risk, exits and auction process; §5 |
| [EMO] — emotion.pdf | 9 | Sires; preparation, restraint and review within §5 |
| [GEX] — gex-framework.pdf | 22 | Sires; regime/location followed by order-flow confirmation; §5 |
| [MAMT] — mastering-amt-vp.pdf | 27 | Sires; auction routes and separately scoped reference statistics; §5 |
| [ABS] — your-mistakes-with-absorption.pdf | 14 | Sires; fixed-location absorption, reward and retest; §5 |
| [STOP] — stop-re-entering.pdf | 17 | Sires; four-stage confirmation and fresh re-entry; §5 |
| [RD] — reading-delta.pdf | 11 | Sires; price response, node pairing and protected structure; §5 |
| [BIG] — only-trade-big-trades.pdf | 19 | Sires; aggressive OFM versus balance failure fade; §5 |
| [OFM] — origin-of-the-move.pdf | 19 | Sires; OFM variants and causal research correction; §§5, 9 |
| [REF] — refill-effect.pdf | 24 | Sires × TeamVOT; zone-touch research/execution study; §9 |
| [NYAM] — ny-am-session.pdf | 12 | Sires; linked session examples, losses and management; §5 |
| [K18] — 18k-payout-session.pdf | 15 | Sires; early attempts, confirmed refill and protected-high management; §5 |
| [K2345] — 2345-funded-session.pdf | 11 | Sires; directional control, microbalance and OFM; §5 |
| [ANAT] — anatomy-of-a-losing-start.pdf | 12 | Sires; reaction bands, structural risk and re-entry; §5 |
| [CONT] — a-clean-continuation-short.pdf | 14 | Sires; one thesis, several continuation confirmations; §5 |
| [RTVP] — reading-the-volume-profile.pdf | 13 | Saint; profile structure and continuation preference; §6 |
| [AMTL] — amt-on-live-markets.pdf | 14 | Saint; acceptance/rejection and POC route; §6 |
| [WIC] — whos-in-control.pdf | 12 | Saint; arrival and HTF/LTF alignment; §6 |
| [TRAP] — trapped-buyers-one-retest.pdf | 13 | Saint; trapped aggression then confirmed break/retest; §6 |
| [K10] — 10k-first-month.pdf | 16 | Unnamed member reported by Sires; own reaction/HVN model; §7 |
| [AVG] — average-unprofitable-trader.pdf | 33 | Sires coaching/research process (§5); Keani’s own opening setup (§8) |
| [MATH] — the-math-behind-auction-market-theory.pdf | 16 | jetbundle pp.3–11 (§10); Sires pp.12–14 (§5) |
| [DATA] — data-engine.pdf | 9 | Stoic guest contribution: research/macro process and risk overlay; §11 |

The [media archive][ZIP] has no independent textual rule authority. Its SDRange upgrade frames match [JR] pp.16–18, post 2005354451008426148; the older embedded-video frames match [JR] pp.27–28, post 1907376388916568139. The four GsIT images match [JR] p.68, post 1928125498736955814; non-chart photographs add no rule. Other repeated stills were matched by their archive filenames to the PDF captions. A frame is not treated as a new trade or a new method merely because it appears in both places.

### Existing-file map

All shorthand code references above resolve inside [CODE]. These are attachment points, not a claim that every proposed input field is already produced.

| Current file | Role in this compilation |
|---|---|
| [clocks.py](/workspace/implementation/src/trading_research/research/phase1_live/clocks.py) | Clock specifications and window availability. |
| [sessions.py](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py) | Frozen range geometry and retrospective path observations. |
| [family_range.py](/workspace/implementation/src/trading_research/research/phase1_live/family_range.py) | Range-family measurements. |
| [family_path.py](/workspace/implementation/src/trading_research/research/phase1_live/family_path.py) | Path-family measurements. |
| [family_clocks.py](/workspace/implementation/src/trading_research/research/phase1_live/family_clocks.py) | Other clock/range constructions. |
| [family_open.py](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py) | Prior value, opening-location cells and RVOL ingredients. |
| [family_env.py](/workspace/implementation/src/trading_research/research/phase1_live/family_env.py) | Extension geometry and disclosed envelope/P-zone approximations. |
| [family_fail.py](/workspace/implementation/src/trading_research/research/phase1_live/family_fail.py) | Box sweep/fail-back ingredients. |
| [family_levels.py](/workspace/implementation/src/trading_research/research/phase1_live/family_levels.py) | Reference levels and assembled daily flags. |
| [family_value.py](/workspace/implementation/src/trading_research/research/phase1_live/family_value.py) | Profile, delta and value ingredients. |
| [family_gap.py](/workspace/implementation/src/trading_research/research/phase1_live/family_gap.py) | Candle/block, open/day-label and TPO ingredients. |
| [family_flow.py](/workspace/implementation/src/trading_research/research/phase1_live/family_flow.py) | CVD and sister-market ingredients. |
| [family_tape.py](/workspace/implementation/src/trading_research/research/phase1_live/family_tape.py) | Tape-derived daily flags; many inputs still aggregate beyond the candidate decision. |
| [mbp1_extract.py](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_extract.py) | Available trade and best-quote extraction. |
| [mbp1_objects.py](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py) | Trade CVD, limited absorption/reload, footprint and profile primitives. |
| [formulas.py](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py) | Shared geometry, close/reclaim and scalar helper functions. |
| [formulas_jumbo.py](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) | Jumbo/AMT component helpers and fixture definitions. |
| [formulas_flow.py](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) | Flow, regime and execution-component helpers. |
| [family_recipes.py](/workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py) | Assembly of daily recipe flags; not an operator event ledger. |
| [family_gex.py](/workspace/implementation/src/trading_research/research/phase1_live/family_gex.py) | An assumed gamma scenario, not a recovered proprietary dealer-position model. |
| [family_options.py](/workspace/implementation/src/trading_research/research/phase1_live/family_options.py) | Native options/OI ingredients with product identity. |
| [family_vol.py](/workspace/implementation/src/trading_research/research/phase1_live/family_vol.py) | Volatility measurements; not an independent source entry method. |
| [grid.py](/workspace/implementation/src/trading_research/research/phase1_live/grid.py) | Named touch/hold/reject/break measurements. |
| [recipe_score.py](/workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py) | Joins and scores component flags; cannot certify the whole loops above. |
| [compute.py](/workspace/implementation/src/trading_research/research/phase1_live/compute.py) | Retained row storage and assembly. |
| [slice.py](/workspace/implementation/src/trading_research/research/phase1_live/slice.py) | Declared sample and coverage selection. |
| [stats.py](/workspace/implementation/src/trading_research/research/phase1_live/stats.py) | Summary statistics for correctly defined observations. |
| [report.py](/workspace/implementation/src/trading_research/research/phase1_live/report.py) | Reporting support. |

The existing score tables are component observations with differing event definitions and, in places, stale caller descriptions. No old rate is promoted here to a method win rate, no missing observation is converted to false, and no report is regenerated. This pass changes only this planning document.

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[SS]: </workspace/sources/documents/jumbo/SessionStat+.pdf>
[XF]: </workspace/sources/documents/jumbo/xfcmg2.pdf>
[FIND]: </workspace/sources/documents/jumbo/jjumbo-findings.pdf>
[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[VIX4]: </workspace/sources/documents/discretionary/vix-lesson-4.pdf>
[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[DOM6]: </workspace/sources/documents/discretionary/dom-lesson-6.pdf>
[DOM7]: </workspace/sources/documents/discretionary/dom-lesson-7.pdf>
[FP8]: </workspace/sources/documents/discretionary/fp-lesson-8.pdf>
[FP9]: </workspace/sources/documents/discretionary/fp-lesson-9.pdf>
[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[C1]: </workspace/sources/documents/discretionary/code-1-thesis.pdf>
[C2]: </workspace/sources/documents/discretionary/code-2-risk.pdf>
[C3]: </workspace/sources/documents/discretionary/code-3-orderflow.pdf>
[EMO]: </workspace/sources/documents/discretionary/emotion.pdf>
[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[RD]: </workspace/sources/documents/discretionary/reading-delta.pdf>
[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[K2345]: </workspace/sources/documents/discretionary/2345-funded-session.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[CODE]: </workspace/implementation/src/trading_research/research/phase1_live/>
[ZIP]: </workspace/sources/x-raw-2026-09-11/JJumboFX_media_v2.zip>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[RULES]: </workspace/planning/phase-1-live/RULES.md>
[AUDIT]: </workspace/planning/phase-1-live/CHART_AUDIT.md>
[AUDIT-F]: </workspace/planning/phase-1-live/CHART_AUDIT_FABLE.md>
[SCORES]: </workspace/planning/phase-1-live/RULES_SCORES.md>
[WIKI]: </workspace/planning/phase-1-live/wiki/>
