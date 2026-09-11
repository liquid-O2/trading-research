# All 85 model cards

These are new research definitions, **specified but not implemented**. Read the [shared engines](ENGINES.md), [data contracts](DATA_CONTRACTS.md) and [experiment protocol](EXPERIMENT_PROTOCOL.md) first. JSON keys are literal configuration identifiers. Narrative bindings describe the exact selected objects, lifetimes and outcomes. A parameter with one allowed value is fixed; sensitivities described as diagnostic do not enter alpha selection.

Total: 85 models; 293 declared parameters; 593 default/one-factor configurations before bounded interactions. No performance runs are reported.

| Family | IDs | Count |
|---|---|---:|
| jumbo | [R-J01](#r-j01)–R-J25 | 25 |
| greenbird | [R-G01](#r-g01)–R-G11 | 11 |
| amt | [R-A01](#r-a01)–R-A18 | 18 |
| flow | [R-F01](#r-f01)–R-F18 | 18 |
| regime | [R-R01](#r-r01)–R-R04 | 4 |
| sires | [R-S01](#r-s01)–R-S09 | 9 |

## Required family status tables

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---|---|---|---|
| jumbo | research-v1 specification | not_run | not_applicable_research_definition | specified_not_implemented | [cards](#r-j01) |
| greenbird | research-v1 specification | not_run | not_applicable_research_definition | specified_not_implemented | [cards](#r-g01) |
| amt | research-v1 specification | not_run | not_applicable_research_definition | specified_not_implemented | [cards](#r-a01) |
| flow | research-v1 specification | not_run | not_applicable_research_definition | specified_not_implemented | [cards](#r-f01) |
| regime | research-v1 specification | not_run | not_applicable_research_definition | specified_not_implemented | [cards](#r-r01) |
| sires | research-v1 specification | not_run | not_applicable_research_definition | specified_not_implemented | [cards](#r-s01) |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|
| jumbo | [R-J01](#r-j01) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 5 parameters |
| jumbo | [R-J02](#r-j02) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 2 parameters |
| jumbo | [R-J03](#r-j03) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| jumbo | [R-J04](#r-j04) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| jumbo | [R-J05](#r-j05) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| jumbo | [R-J06](#r-j06) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 3 parameters |
| jumbo | [R-J07](#r-j07) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 3 parameters |
| jumbo | [R-J08](#r-j08) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| jumbo | [R-J09](#r-j09) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| jumbo | [R-J10](#r-j10) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | management; 2 parameters |
| jumbo | [R-J11](#r-j11) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 3 parameters |
| jumbo | [R-J12](#r-j12) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| jumbo | [R-J13](#r-j13) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 3 parameters |
| jumbo | [R-J14](#r-j14) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| jumbo | [R-J15](#r-j15) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 3 parameters |
| jumbo | [R-J16](#r-j16) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| jumbo | [R-J17](#r-j17) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| jumbo | [R-J18](#r-j18) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| jumbo | [R-J19](#r-j19) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | management; 2 parameters |
| jumbo | [R-J20](#r-j20) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 2 parameters |
| jumbo | [R-J21](#r-j21) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 2 parameters |
| jumbo | [R-J22](#r-j22) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | management; 3 parameters |
| jumbo | [R-J23](#r-j23) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 2 parameters |
| jumbo | [R-J24](#r-j24) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | management; 3 parameters |
| jumbo | [R-J25](#r-j25) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| greenbird | [R-G01](#r-g01) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| greenbird | [R-G02](#r-g02) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| greenbird | [R-G03](#r-g03) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| greenbird | [R-G04](#r-g04) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| greenbird | [R-G05](#r-g05) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 3 parameters |
| greenbird | [R-G06](#r-g06) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | management; 3 parameters |
| greenbird | [R-G07](#r-g07) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| greenbird | [R-G08](#r-g08) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 3 parameters |
| greenbird | [R-G09](#r-g09) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| greenbird | [R-G10](#r-g10) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| greenbird | [R-G11](#r-g11) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 3 parameters |
| amt | [R-A01](#r-a01) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| amt | [R-A02](#r-a02) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| amt | [R-A03](#r-a03) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| amt | [R-A04](#r-a04) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| amt | [R-A05](#r-a05) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| amt | [R-A06](#r-a06) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| amt | [R-A07](#r-a07) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| amt | [R-A08](#r-a08) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| amt | [R-A09](#r-a09) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| amt | [R-A10](#r-a10) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 3 parameters |
| amt | [R-A11](#r-a11) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 3 parameters |
| amt | [R-A12](#r-a12) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| amt | [R-A13](#r-a13) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 2 parameters |
| amt | [R-A14](#r-a14) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 3 parameters |
| amt | [R-A15](#r-a15) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 2 parameters |
| amt | [R-A16](#r-a16) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| amt | [R-A17](#r-a17) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| amt | [R-A18](#r-a18) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F01](#r-f01) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F02](#r-f02) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| flow | [R-F03](#r-f03) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| flow | [R-F04](#r-f04) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F05](#r-f05) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| flow | [R-F06](#r-f06) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| flow | [R-F07](#r-f07) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 4 parameters |
| flow | [R-F08](#r-f08) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F09](#r-f09) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| flow | [R-F10](#r-f10) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | component; 3 parameters |
| flow | [R-F11](#r-f11) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F12](#r-f12) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 3 parameters |
| flow | [R-F13](#r-f13) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| flow | [R-F14](#r-f14) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F15](#r-f15) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F16](#r-f16) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| flow | [R-F17](#r-f17) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| flow | [R-F18](#r-f18) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| regime | [R-R01](#r-r01) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 6 parameters |
| regime | [R-R02](#r-r02) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 3 parameters |
| regime | [R-R03](#r-r03) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | management; 3 parameters |
| regime | [R-R04](#r-r04) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | context; 4 parameters |
| sires | [R-S01](#r-s01) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| sires | [R-S02](#r-s02) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 3 parameters |
| sires | [R-S03](#r-s03) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| sires | [R-S04](#r-s04) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| sires | [R-S05](#r-s05) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| sires | [R-S06](#r-s06) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| sires | [R-S07](#r-s07) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| sires | [R-S08](#r-s08) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |
| sires | [R-S09](#r-s09) | specified_not_implemented | acceptance cases specified; engine not run | causal contract specified; engine not run | prohibited; research assumptions named | signal; 4 parameters |

<a id="r-j01"></a>
## R-J01 — Judas reversal at the projection ladder

Use a causal overshoot-and-return reversal at a frozen projection. Select the first qualified episode in time, never the eventual deepest AM extreme. Test strict rejection as an explicit alternative.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E11.

| Binding | Exact policy |
|---|---|
| `clock` | J69 |
| `entry_window` | 09:40–09:50 New York; confirmation must be inside |
| `observation_start` | 09:00 |
| `sides` | both independently |
| `level_set` | outer H+kW and L-kW |
| `stop` | episode adverse extreme + stop_buffer_ticks outward |
| `target` | EQ69; if it is behind expected entry, no_target |
| `exit_horizon` | 12:00 |
| `episode_policy` | first visit per projection ID; later deeper projection is a different ID; max one fill at a time |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `depth_set` | manual | ["manual", "thirds"] | named set — manual={0.1,0.2,0.3,0.5}; thirds={0.33,0.66,1.0}; enumerate every level, not final depth |
| `confirm_minutes` | 5 | [3, 5, 10] | minutes — REACTION deadline from each projection first touch |
| `response_ticks` | 4 | [2, 4, 8] | ticks — complete close back toward range beyond near edge |
| `rejection` | overshoot_return | ["overshoot_return", "strict_close"] | enum — strict_close fails on any completed close beyond the projection before confirmation; overshoot_return uses E02 far-edge invalidation |
| `stop_buffer_ticks` | 2 | [1, 2, 4] | ticks — outward from observed episode extreme |

**Algorithm**

1. Freeze J69 geometry and start a separate E02 episode for each projection side at its first post-09:00 contact; use d=-1 for upper and +1 for lower.
2. For overshoot_return treat the level as a zero-width band, allow up to 8 ticks adverse completed-close penetration before failure, and require response_ticks completed-close retreat within confirm_minutes. Strict_close fails at the first beyond-level completed close. The 8-tick ceiling is fixed for this baseline, not the historical strict-G rule.
3. An episode may touch before 09:40 but can trade only if its actual confirmation is in [09:40,09:50); reject stale expired episodes. Order simultaneous confirmations by confirmation timestamp, first-touch timestamp, smaller k, then low-side before high-side, recording that deterministic tie.
4. At confirmation freeze stop from that episode prefix and EQ69 target. Submit E11 market entry. A new deeper touch does not rewrite a prior entry or label; measure side/depth-specific touch, confirmation and post-entry target outcomes separately.
5. Keep wick reach and complete-close reaction separate. Export all non filled and failed episodes so selecting a later successful projection cannot hide earlier failed trades.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `depth` | decimal |
| `touch_at` | UTC ns |
| `confirm_at` | UTC ns? |
| `adverse_excursion` | ticks |
| `reversal_state` | enum |
| `EQ_reach_after_fill` | bool? |
| `net_R0` | float? |

**Comparisons**

- strict_close vs overshoot_return
- same-window outer-edge-only reversal using identical E02/E11
- delay-matched no-flow baseline; J14/J15/J16 are optional later ablations

**Acceptance cases**

- H=120, L=100, W=20 gives upper0.5=130, lower0.5=90. An upper touch at 09:42 then close129 with response4 ticks on tick0.25 confirms short; EQ110 is the target.
- An upper0.1 touch at 09:35 and upper0.5 at 09:49 are distinct; the later one cannot assign depth0.5 to the earlier episode.
- A confirming close exactly 09:50 cannot enter the baseline. After-entry lows before fill never contribute to MFE.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J01 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `4c0d978318930c43d83b733562577d052d934c646f4dd2d36b6f9de3765fa6a2`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j02"></a>
## R-J02 — 09:30 opening leg into projections

Measure each opening-leg projection reach and a causal first-edge directional forecast; do not call an either-side reach a trade win.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01.

**Fixed consumers:** [R-J01](#r-j01).

| Binding | Exact policy |
|---|---|
| `clock` | J69 |
| `window` | 09:30–09:40 |
| `depths` | [0.1, 0.2, 0.3, 0.5] |
| `primary_output` | 0.5 reach per side |
| `direction` | first fresh J69 edge visited after 09:30; already consumed pre 09:30 -> no fresh directional forecast |
| `consumer` | J01 opening context only; no direct order |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `reach_rule` | wick | ["wick", "close"] | enum — tick crossing/visit vs complete 1m close beyond rounded target |
| `opening_window_minutes` | 10 | [5, 10, 15] | minutes — distinct research horizons from 09:30 |

**Algorithm**

1. Freeze all levels at 09:00; record exact 09:30 open and freshness state of both edges.
2. For every depth and side store first target visit in the selected half-open window. A0.1 visit cannot satisfy0.5.
3. For the directional forecast use only the first fresh edge encounter; equal-timestamp opposite encounters are ambiguous. Continue reporting unconditional either-side descriptive reaches on all complete sessions.
4. Fit conditional reach probabilities only on earlier training sessions. Export per-side, either-side and first-edge-direction denominators separately; no risk/return is inferred from open-to-target distance.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `reach_by_depth_side` | map<bool?> |
| `first_edge` | enum(high,low,none,ambiguous,consumed) |
| `first_reach_at` | UTC ns? |
| `open_to_target` | points |

**Comparisons**

- unconditional same-clock reach distribution
- first-edge directional vs either-side descriptive rate

**Acceptance cases**

- H120, L100, upper0.5=130: high125 before 09:40 is not0.5 reach.
- A130 print at 09:40 is excluded from10-minute window.
- An edge consumed 09:15 is not a fresh 09:30 directional trigger; its geometry remains valid for descriptive reach.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J02 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `a7bf823f97f31f59f141c80724e84b195d72078b2876c190caa2ad1982ff95cf`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j03"></a>
## R-J03 — Extended range, single break and inner-level retrace

Define extended range numerically and test a break–hold–inner-retrace sequence with a real decision deadline; later single-side path is an outcome.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E11.

| Binding | Exact policy |
|---|---|
| `clock` | J69 |
| `extended` | W69/prior_RTH_width >= width_ratio |
| `entry_window` | 09:30–10:00 |
| `level` | EQ69 baseline; Q25/Q75 directional alternatives |
| `direction` | first completed 1m close beyond J69 edge by2 ticks after 09:30 |
| `hold` | outside break edge until inner retrace begins; no future final-path gate |
| `target` | broken J69 edge as historical episode objective, not a fresh external draw |
| `stop` | retrace adverse extreme +2 ticks |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `width_ratio` | 1.0 | [0.75, 1.0, 1.25] | ratio — current range width / previous complete same-contract RTH width |
| `inner_level` | EQ | ["EQ", "directional_quadrant"] | enum — up->Q75, down->Q25 |
| `hold_minutes` | 3 | [1, 3, 5] | minutes — completed outside closes after break |
| `response_ticks` | 4 | [2, 4, 8] | ticks — retrace E02 confirmation |

**Algorithm**

1. Calculate extended flag before 09:30 with a positive complete prior RTH width. News is a separate output, not a shortcut for extended.
2. Start the first directional break episode and complete its HOLD; require opposite edge unvisited as of confirmation, never through noon.
3. After hold, wait for first selected inner-level touch, then E02 REACTION in breakout direction. Entry confirmation must be before 10:00; earlier touches with later confirmations do not enter.
4. Freeze actual retrace stop and target broken edge. Edge is an objective within the original breakout episode despite consumed high/low status, explicitly not a new fresh-target event. E11 handles fills and exit.
5. Record final both/single path and lunch range only as outcome labels.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `width_ratio` | float |
| `break_at` | UTC ns? |
| `hold_at` | UTC ns? |
| `retrace_at` | UTC ns? |
| `final_path` | enum |
| `net_R0` | float? |

**Comparisons**

- same sequence without extended gate
- EQ vs directional quadrant

**Acceptance cases**

- W69=120, prior width100 qualifies threshold1.0; prior width0 is unavailable.
- Break 09:45, hold ends 09:49, retrace 09:56 and confirmation 10:01 yields no entry.
- Opposite break 11:00 cannot erase a valid 09:55 signal; it changes later outcome only.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J03 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `8ba0473cef2794925bf00bc0ceacd489210bc6cd381f5f84c5f0d8939760910b`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j04"></a>
## R-J04 — Purged overnight extremes and single-break continuation

Use actual first-visit purge timestamps and an internal expansion trigger; the final range envelope is irrelevant to purge.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E11.

| Binding | Exact policy |
|---|---|
| `reference_set` | ASIA and GB_LONDON H/L, each from its own completion |
| `purge_cutoff` | 09:30 |
| `clock` | J69 |
| `entry_window` | 09:30–11:00 |
| `direction` | first confirmed internal-reference expansion |
| `target` | own-side outer projection1.0 |
| `stop` | internal trigger episode adverse extreme+2 ticks |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `purge_rule` | all_four_visited | ["all_four_visited", "both_opposite_side_visited"] | enum — all4 before 09:30; alternative for up requires Asia/London lows visited, down requires highs |
| `inner_reference` | EQ | ["EQ", "directional_quadrant"] | enum — Q75 up,Q25 down |
| `hold_minutes` | 3 | [1, 3, 5] | minutes — close-through then subsequent closes on expansion side |

**Algorithm**

1. Build each overnight reference independently. Evaluate exact first visits from own known_at through 09:30. For all-four require all consumed; for directional alternative evaluate the two adverse-side references independently for each candidate direction.
2. After 09:30 detect first 1m close two ticks through the selected internal reference and HOLD on that side. No outer-edge break is required.
3. At hold completion require the other internal-direction episode has not confirmed earlier; earliest valid side wins. Snapshot level, stop and projected target.
4. Execute E11; report purge facts, internal confirmation and later projection outcome separately. Missing London/Asia coverage makes the gate unavailable.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `purge_mask` | 4 booleans? |
| `purge_times` | 4 UTC ns? |
| `internal_break_at` | UTC ns? |
| `projection_reach_after_fill` | bool? |
| `net_R0` | float? |

**Comparisons**

- same internal expansion without purge gate
- all4 vs adverse-side-only purge

**Acceptance cases**

- A reference formed 05:00 cannot be purged by 04:30 price.
- An equality print consumes its reference even if strict sweep depth is0.
- 2026-07-10 Asia/London highs first visited 09:52/09:49 cannot satisfy all-four at 09:30.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J04 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `b93f9292e8c19dfaea1c645e906fa23be5e6bfbc160edd76a6bb87f65f1422ce`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j05"></a>
## R-J05 — Single-break retraces to EQ, range open and OR midpoint

Make range-finish open, EQ and completed OR midpoint separate inner-entry branches; test break-first versus internal-first instead of assuming one chronology.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E11.

| Binding | Exact policy |
|---|---|
| `clock` | J69 |
| `entry_window` | 09:00–10:00 |
| `reference_snapshot` | immutable at own available_at |
| `stop` | interaction extreme+2 ticks |
| `target` | directional J69 edge within same episode; target must be ahead |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `reference` | finish_open | ["finish_open", "EQ", "OR5_mid", "OR15_mid"] | object — 09:00 first-minute open; ORs known 09:35/09:45 |
| `sequence` | internal_first | ["internal_first", "outer_break_first"] | enum — internal: approach from above and react back above -> long; approach from below and react back below -> short. Break-first uses a previously confirmed outer-break direction. |
| `response_ticks` | 4 | [2, 4, 8] | ticks — close retreat from selected line |
| `hold_minutes` | 3 | [1, 3, 5] | minutes — required outer break hold only |

**Algorithm**

1. Create four independent inner objects. Do not alias 06:00 build_open to 09:00 finish_open.
2. For internal_first determine approach side from the last completed 1m close before touch; below->short reaction back below, above->long back above. Thus d is the side occupied before retrace. Equal prior close gives no directional signal. For outer_break_first require a prior J69 E02 break and HOLD and then retrace in that direction.
3. Apply E02 REACTION at the selected line in the direction established by the previous step. Both sides may form observations; earliest valid confirmation enters.
4. Target the directional range edge only when ahead at decision; stop from prefix episode extreme. E11 records fill and outcomes. Snapshot availability disallows p reformation OR entries.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `reference_id` | string |
| `reference_price` | points |
| `sequence` | enum |
| `approach_side` | enum |
| `net_R0` | float? |

**Comparisons**

- reference branches compared with identical timing/fees
- break-first vs internal pullback

**Acceptance cases**

- 09:00 open105 and 06:00 open100 remain distinct.
- An OR15 midpoint touched 09:40 cannot exist yet.
- Prior close above EQ, retrace EQ and close4 ticks above produces long; a close through below is failure, not a forced short.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J05 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `54c3f7bb8a3b60e755ecec38236c0c7cfda7896aec55c95f34ebf84dae837794`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j06"></a>
## R-J06 — Opening-location context and RVOL

Build point-in-time opening cells and completed five-minute RVOL, then estimate their conditional path distributions.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E03, E04.

**Fixed consumers:** [R-J01](#r-j01), [R-J04](#r-j04).

| Binding | Exact policy |
|---|---|
| `clock` | J69 |
| `opening_price` | 09:30 open |
| `profile` | prior_rth VP70 |
| `outcomes` | ["09:30–10:30", "09:30–12:00"] |
| `cells` | below/inside/above prior VA x below/inside/above prior RTH price x below/inside/above J69; equality inside |
| `RVOL_known_at` | 09:35 |
| `consumer` | J01/J04; RVOL gate can only act 09:35 or later |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `history_sessions` | 60 | [60, 120, 252] | complete sessions — prior same5m 09:30–09:35 volume median |
| `rvol_cutoff` | 1.5 | [1.0, 1.5, 2.0] | ratio — V_current5m / historical median |
| `prior_profile_scope` | prior_rth | ["prior_rth", "prior_eth"] | enum — ETH previous scheduled 18:00–17:00 same contract; no silent scope alias |

**Algorithm**

1. Build selected prior profile and price bounds from D02 and calendar, preserving profile parameters. Missing full profile is unavailable.
2. Freeze27 opening cells at 09:30. At 09:35 calculate RVOL from five complete minutes and strictly prior history; median0 is unavailable.
3. For each outcome horizon calculate four mutually exclusive wick path classes relative to J69, as well as close-path labels, with one eligible session per cell.
4. Estimate conditional probabilities with the protocol shrinkage, keeping unconditional cells and RVOL-conditioned cells separate. Test incremental information in registered consumers after features are available.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `opening_cell` | 3x3x3 enum |
| `RVOL` | float? |
| `path_probabilities` | 4 probabilities |
| `n_cell` | int |
| `log_loss` | float |

**Comparisons**

- unconditional path distribution
- opening cells without RVOL
- prior RTH vs ETH scope

**Acceptance cases**

- Current5m volume3000 and prior median2000 gives RVOL1.5 at 09:35 only.
- Below VA but inside prior price range is a valid cell, not discarded.
- 59 prior sessions cannot satisfy60-session baseline.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J06 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `7e6653c1882fa671ba5a007a0035d0695b5be2fd07de3834b2aee70c138f878c`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j07"></a>
## R-J07 — Width-conditioned range-break distribution

Replace the daily boolean with a proper four-way width-conditioned distribution and a calibrated forecast.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E04.

**Fixed consumers:** [R-J01](#r-j01), [R-J03](#r-j03).

| Binding | Exact policy |
|---|---|
| `clock` | J69 |
| `primary_horizon` | 09:00–12:00 |
| `width_pct` | 100*W69/last_complete08:59_close |
| `width_bins_pct` | [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, "inf"] |
| `boundary` | lower inclusive upper exclusive |
| `consumer` | J01/J03; class known 09:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `break_rule` | wick | ["wick", "close"] | enum — first inclusive crossing vs completed 1m strict beyond |
| `horizon_start` | 09:00 | ["09:00", "09:30"] | NY wall — separate output population |
| `normalizer` | 08:59_close | ["08:59_close", "build_open"] | price — 08:59 complete close or 06:00 build open; both known at 09:00 |

**Algorithm**

1. Require complete positive W and normalizer. Assign exactly one width bin at 09:00. Both listed normalizers are available by that time.
2. Track high and low path flags over the selected horizon; derive high_only,low_only, both, neither, with incomplete outcomes censored.
3. Fit smoothed four-class distributions from training only. Keep source study percentages as reference metadata, never priors.
4. Score conditional log loss/Brier versus unconditional clock distribution and expose uncertainty/counts in each cell.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `width_pct` | percent |
| `width_bin` | enum |
| `path_class` | 4-way enum |
| `forecast` | probability[4] |

**Comparisons**

- unconditional clock distribution
- price-normalized width vs raw width quantile classes

**Acceptance cases**

- width0.4% belongs[0.4,0.6), not both neighboring bins.
- Each complete session contributes exactly one class and class counts sum toN.
- A09:15 sweep changes 09:00 horizon but not 09:30 horizon.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J07 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `4e3fd652b09fe43c2b39a070b0e70c68f0d256f84f361eebaf3a2c041035b5ef`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j08"></a>
## R-J08 — PM reversal in the1.33–1.66 extension area

Trade a completed reaction from the whole PM extension area; distinguish it from exact1.33 line rejection.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E11.

| Binding | Exact policy |
|---|---|
| `clock` | J69 |
| `entry_window` | 13:00–15:30 |
| `bands` | upper[H+1.33W, H+1.66W], lower[L-1.66W, L-1.33W] |
| `side` | fade toward range |
| `stop` | observed interaction extreme+2 ticks |
| `target` | corresponding J69 edge as geometric retracement objective |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | one first PM episode per side; record earlier contacts, untouched gate parameter |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `area_mode` | band | ["band", "line_1.33"] | enum — whole area vs near line |
| `fresh_pm` | true | [true, false] | bool — true excludes same area touched from 09:00 through 13:00; not external-H/L lifetime override |
| `confirm_minutes` | 5 | [3, 5, 10] | minutes — E02 reaction deadline |
| `response_ticks` | 8 | [4, 8, 16] | ticks — retreat beyond near area edge |

**Algorithm**

1. Freeze outer-price bands 09:00 and track all contacts; apply fresh_pm at 13:00.
2. First in-window band contact starts E02 fade reaction, d=-1 upper/+1 lower. Far-edge completed close beyond2 ticks invalidates. Confirmation must retreat response_ticks beyond near edge.
3. Stop uses the observed episode extreme, including penetration inside/beyond band before confirmation; no final PM extreme is used.
4. Execute E11 to the corresponding range edge and close by 16:00. Record band touch, reversal confirmation and outcome separately; no one-sided either-band OR.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `band_side` | enum |
| `pre_PM_contact` | bool |
| `contact_at` | UTC ns? |
| `confirmed` | bool? |
| `net_R0` | float? |

**Comparisons**

- exact1.33 line
- PM reaction without untouched gate

**Acceptance cases**

- H120, L100 gives upper[146.6,153.2], lower[66.8,73.4] before directional tick rounding.
- 12:54 contact is pre-PM; baseline fresh_pm excludes later retouch.
- Source execution that exits before later band contact is not an entry for this model.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J08 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `0076ef9587efa64c1a17b6413d717b4064b08ff50bb9c6a909599aee84bab4a2`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j09"></a>
## R-J09 — London reversal model

Choose explicit New York London research clocks preserving a one-hour freeze-to-action lead, and compare them without waiting for the source display timezone.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E11.

| Binding | Exact policy |
|---|---|
| `default_clock` | J_LONDON_A |
| `ladder` | outer0.1,0.2,0.3,0.5 |
| `entry` | own action window |
| `side` | fade projection; separate inner pullback branch |
| `stop` | episode extreme+2 ticks |
| `target` | projection_fade: own EQ; EQ_pullback: directional box edge, which must be ahead |
| `exit_horizon` | own clock outcome end |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `clock` | J_LONDON_A | ["J_LONDON_A", "J_LONDON_B", "J_LONDON_C"] | clock enum — E01 jointly specifies build/action intervals; no independent timezone fit |
| `setup` | projection_fade | ["projection_fade", "EQ_pullback"] | enum — fade first 0.3 projection reaction; EQ pullback uses approach-side rule from J05 |
| `confirm_minutes` | 5 | [3, 5, 10] | minutes — E02 reaction deadline |
| `response_ticks` | 4 | [2, 4, 8] | ticks — completed-close response |

**Algorithm**

1. Build selected clock, freeze own W and projections; retain the explicit one-hour action lead.
2. For projection_fade observe first 0.3 level touch after action start and use E02 fade. For EQ_pullback use prior completed 1m close side, touch EQ, then reaction back to that side. No outer sweep is required for the inner branch.
3. Use own clock levels only; J69 cannot be an input before 09:00. EQ_pullback target is directional box edge; projection_fade target isEQ.
4. Execute E11, expire at selected clock end and report each clock independently. Do not optimize wall timezone or move a source chart to align one result.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `clock_id` | enum |
| `setup` | enum |
| `touch_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- three fixed clock alternatives
- inner pullback vs projection fade

**Acceptance cases**

- J_LONDON_A freezes 02:00 and acts 03:00, exactly 1h later.
- A03:30 decision cannot use 08:00 bars.
- An EQ pullback without either edge sweep can qualify its own branch.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J09 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `93558745353b3ae7168c684079a647ab6d20db3a57d7bb8acb0fe268fe197b90`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j10"></a>
## R-J10 — Remaining overnight/prior-session draws after reversal

Choose remaining genuinely unvisited draws at the parent confirmation; compare target selection on identical entries.

**Role:** management. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E09, E11.

**Build dependencies:** [R-J01](#r-j01), [R-J04](#r-j04).

| Binding | Exact policy |
|---|---|
| `parents` | J01 and J04 filled-entry ledgers, reported separately |
| `reference_universe` | ASIA,GB_LONDON,PRIOR_RTH H/L |
| `selection` | nearest fresh target ahead at parent decision |
| `no_target` | retain parent baseline target in control only; selected-draw branch records no eligible target and no target-policy trade comparison |
| `stop` | identical parent initial stop |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `target_universe` | all | ["all", "overnight_only", "prior_rth_only"] | enum — all=three specified source clocks; no current final extremes |
| `selection` | nearest | ["nearest", "farthest"] | enum — available unvisited targets ahead; ties E09 |

**Algorithm**

1. Ingest actual parent confirmations and orders/fills; rebuild every candidate first-visit status from its own known_at including ETH.
2. At decision freeze the complete candidate set and selected target; do not choose at fill or after observing price movement.
3. Replay target exits on identical parent entries and stops. Compare only paired entries with a qualifying target, and separately report their fraction of all parent opportunities; do not pretend no-target entries won/lost.
4. Track target consumption after decision; a target visited before delayed entry may make the order path immediately marketable or passed, which E11 handles without deleting the fill.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `candidate_ids` | list<string> |
| `selected_target_id` | string? |
| `fresh_at_decision` | bool? |
| `paired_delta_net_R0` | float? |

**Comparisons**

- parent fixed target on identical entries
- nearest vs farthest target

**Acceptance cases**

- 2026-01-28 prior RTH high consumed2026-01-27 16:45 cannot be selected 09:30.
- An Asia high consumed 02:00 does not consume the Asia low.
- Future target visits cannot change the candidate set saved at decision.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J10 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `ad54f6fbca050cc5ab4879476342e0599bd125b69a7eea661f74dc080eb4905d`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j11"></a>
## R-J11 — SessionStat mean/median/minimum-average boundaries

Build explicit directional excursion distributions and per-session smaller-excursion statistics; keep mean, median and widths separate.

**Role:** component. **Inputs:** D01, D04. **Engines:** E00, E01, E04.

**Fixed consumers:** [R-J01](#r-j01).

| Binding | Exact policy |
|---|---|
| `sample_clock` | 09:00–12:00 |
| `anchor` | 09:00 finish-open |
| `outputs` | upper/lower means and medians, min-excursion means/medians, shaded mean–median side bands |
| `consumer` | J01 location feature with boundaries available 09:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `history_sessions` | 60 | [60, 120, 252] | sessions — complete prior same-clock samples |
| `normalization` | return | ["return", "points"] | enum — historical excursion/O_i scaled by current O, or raw points |
| `weighting` | equal | ["equal", "exp_half_life_30"] | enum — weighted mean uses2^(-age/30); weighted quantile first cumulative normalized weight>=q; age0 newest prior |

**Algorithm**

1. For each prior complete session store O, H, L, u=H-O, d=O-L and min(u, d). Keep sample date and raw contract.
2. Compute mean and median separately for each side; exponential option weights means and quantiles with the declared rule, never today.
3. Anchor at current 09:00 observed open, directional-round derived prices, and freeze; produce mean–median shaded bands and min-excursion symmetric boundaries.
4. Measure coverage and pinball loss of median boundaries and downstream J01 confluence benefit; a boundary draw extending past noon does not extend outcome horizon.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `upper_mean` | points |
| `lower_mean` | points |
| `upper_median` | points |
| `lower_median` | points |
| `mean_min_excursion` | points |
| `sample_dates` | date[] |

**Comparisons**

- raw points vs return scaling
- mean vs median; min-of-means as named diagnostic only

**Acceptance cases**

- u=[2,8], d=[8,2] gives mean(min)=2 while min(mean(u), mean(d))=5; they must differ.
- Exactly59 prior sessions cannot create a60-session boundary.
- Today 15:00 burst cannot change 09:00 levels.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J11 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `032d4ef163fcaceb61ca37f40df39a4fb43309b6b4472b12f7de4d2486854463`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j12"></a>
## R-J12 — P-zone confluence and the low-to-open path

Replace unpublished P-zones with frozen conditional excursion-quantile bands, optionally scaled by known pre-open volatility; test low-to-finish-open as an ordered path.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E04, E11.

| Binding | Exact policy |
|---|---|
| `anchor` | J69 finish-open 09:00 |
| `historical_outcome` | 09:00–12:00 |
| `zone_pairs` | E04 T1..T4 |
| `entry_window` | 09:00–11:30 |
| `side` | fade selected zone |
| `stop` | far zone edge or episode extreme, whichever more adverse, plus2 ticks |
| `target` | 09:00 finish-open; must be ahead |
| `exit_horizon` | 12:00 |
| `lifecycle` | freeze baseline; E04 two-close far-edge invalidation |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `history_sessions` | 252 | [120, 252, 500] | sessions — full prior history |
| `zone_tier` | T1 | ["T1", "T2", "T3", "T4"] | enum — complete fixed quantile pairs from E04 |
| `volatility_scale` | none | ["none", "preopen_RV"] | enum — E04 clipped ratio using06–09 RV |
| `confirm_minutes` | 5 | [3, 5, 10] | minutes — E02 reaction |

**Algorithm**

1. Build side-specific normalized excursion histories and quantile bands using chosen N. Never infer bounds from the eventual current excursion.
2. At 09:00 anchor and freeze upper/lower zones independently. Do not force bands outside J69 H/L.
3. For each first eligible zone contact use E02 fade confirmation, keeping zone identity and side. For a low-to-open study separately require a fresh J69 low visit before the lower-zone confirmation; this is a conditional output, not price inequality.
4. Execute E11 to finish-open after confirmation. A target behind expected entry is no_target. Export lower and upper cohorts separately and compare pinball/calibration of zone edges.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `zone_id` | string |
| `quantile_edges` | float[2] |
| `low_then_zone_then_open` | bool? |
| `zone_response` | enum |
| `net_R0` | float? |

**Comparisons**

- unscaled vs known-RV scaling
- outer fixed projection fade with same reaction rule
- T1 throughT4 registered tiers

**Acceptance cases**

- O100, lower excursion q50=.02,q65=.03 gives lower zone[97,98]; it may lie inside a price range[95,105].
- Low100 and open101 can support low-to-open traversal; no low>open test exists.
- Later volatility cannot change a touched frozen zone.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J12 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `7270f20bbddcbad9d1b0af2e9491fb471ffc0aa5b970e9b2709ca8ff2fe33d01`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j13"></a>
## R-J13 — Expected-volatility range

Specify an expected-range model using prior directional returns and optional pre-open RV scaling; test boundary-to-EQ traversal separately.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E04.

**Fixed consumers:** [R-J01](#r-j01), [R-J05](#r-j05).

| Binding | Exact policy |
|---|---|
| `anchor` | 09:30 open |
| `history_clock` | 09:30–12:00 |
| `geometry` | directional mean/median return distances; EV width=U-L |
| `extension` | U+0.5*(U-L), L-0.5*(U-L) |
| `consumer` | J01/J05 only after 09:30 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `history_sessions` | 120 | [60, 120, 252] | sessions — prior complete samples |
| `estimator` | median | ["mean", "median"] | enum — both always exported; selected estimator supplies consumer |
| `volatility_scale` | none | ["none", "preopen_RV"] | enum — E04 scaling |

**Algorithm**

1. Create prior up/down return samples and fit specified estimators. Snapshot includes all dates and full N.
2. At 09:30 calculate EV levels and width, independent ofEQ69 and source inner-value POC.
3. For each boundary first interaction record later EQ69 touch in the same side episode through noon; an earlier EQ touch cannot count.
4. Evaluate quantile/coverage calibration and the optional consumer gate; do not turn any EV-to-EQ pair from unrelated sides into a success.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `EV_upper` | points |
| `EV_lower` | points |
| `EV_width` | points |
| `boundary_then_EQ` | bool? |
| `boundary_at` | UTC ns? |

**Comparisons**

- constant-return median vs mean
- preopen-scaled vs unscaled

**Acceptance cases**

- O100, median u_return.02,d_return.01 gives U102, L99, width3 and upper+50%=103.5.
- EV at 09:30 cannot gate 09:20 entry.
- EQ touch 09:40 before EV boundary 09:45 does not satisfy subsequent traversal.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J13 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `67e8a051a230ffc6fc1f7a29bfc225df5412a3e99e6c1a0f6c06c9018214f8de`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j14"></a>
## R-J14 — Small-body/high-volume candle confirmation

Use a complete-bar small-body/large-volume observation with prior-bar warm up, then measure whether it adds information at a parent level.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E05.

**Fixed consumers:** [R-J01](#r-j01), [R-J08](#r-j08).

| Binding | Exact policy |
|---|---|
| `scope` | continuous bars across session boundary |
| `location` | parent level/area available at candle close, with actual candle span overlap |
| `consumer` | J01/J08; confirmation waits for bar close |
| `direction` | observation has no automatic trade side |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `bar_minutes` | 3 | [1, 3, 5] | minutes — fixed clock-aligned candles |
| `body_max` | 0.6 | [0.3, 0.6, 0.8] | ratio — abs(C-O)/(H-L) <=threshold |
| `volume_multiple` | 1.5 | [1.5, 2.0, 2.5] | multiple — current volume / mean of prior n bars |
| `baseline_bars` | 14 | [14, 30, 60] | bars — exclude current; no AM reset |

**Algorithm**

1. Build complete E05 bars and prior-only volume baseline.
2. Evaluate inclusive body/volume thresholds; zero-range or missing warm up is unavailable.
3. Join the observation to an actual contemporaneous parent level interaction, retaining bar and snapshot ID.
4. Compare parent responses with/without observation and delay-matched price-only control; continuation and reversal are separate outcomes.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `body_ratio` | float |
| `volume_ratio` | float |
| `observation` | bool? |
| `available_at` | UTC ns |
| `level_id` | string? |

**Comparisons**

- body only
- volume only
- combined vs delay-matched price control

**Acceptance cases**

- Body0.45, volume2x passes default0.6/1.5, fails0.3/2.5.
- A09:03 candle may warm up using pre 09:00 bars.
- A marker followed by continuation is not relabelled absorption reversal.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J14 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `9b0dad4d16f965361d35645d0e0f066cab7e2cb2470434ae66692e1885e762cd`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j15"></a>
## R-J15 — Large executions at a framework level

Retain actual large executions, side and level identity; compare fixed thresholds with a prior-only adaptive size threshold.

**Role:** component. **Inputs:** D02, D03, D04. **Engines:** E00, E01, E06.

**Fixed consumers:** [R-J01](#r-j01), [R-J09](#r-j09).

| Binding | Exact policy |
|---|---|
| `NY_window` | 09:30–16:00 |
| `London_window` | selected J09 action window |
| `fixed_thresholds` | NY>=100 NQ contracts, London>=75 NQ contracts |
| `location` | nearest available parent level within tolerance; tie E09 |
| `response_horizon` | 15 minutes from print |
| `consumer` | J01/J09 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `threshold_mode` | fixed | ["fixed", "prior_q99"] | enum — E06 adaptive floor20; no execution aggregation |
| `tol_ticks` | 2 | [1, 2, 4] | ticks — print-to-level distance |
| `response_minutes` | 15 | [5, 15, 30] | minutes — post-print outcome only |

**Algorithm**

1. Load one canonical execution stream, normalize buy/sell/unknown and preserve single execution identity.
2. Select threshold by clock; London can run when NY data is absent. Future J69 levels cannot be used in London.
3. Join each qualifying execution to known level(s), preserving signed side and exact distance. Unknown-side large prints can be descriptive but cannot satisfy a directional flow gate.
4. Measure both aggressor reward and defender reaction after the print; compare with all same-parent touches without a large print using matching clock and delay.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `print_id` | string |
| `size` | contracts |
| `aggressor` | enum |
| `level_distance` | ticks |
| `rewarded` | bool? |
| `defender_reaction` | bool? |

**Comparisons**

- fixed vs q99 threshold
- same parent touches without large executions

**Acceptance cases**

- Exactly100 contracts qualifies NY baseline.
- A75-contract London print cannot use 09:00 geometry at 02:30.
- A302 print15 points from EQ fails two-tick confluence regardless caption.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J15 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `389d436629fa8dcc51b183cc1b0c7c630f27b9b3e822cce9953a9ee23338a558`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j16"></a>
## R-J16 — Developing RTH VP and delta-profile confirmation

Use full developing RTH signed profiles plus a separately computed highlight mask and local absorption response; highlighting never changes totals.

**Role:** component. **Inputs:** D02, D03, D04. **Engines:** E00, E03, E06.

**Fixed consumers:** [R-J01](#r-j01), [R-J05](#r-j05).

| Binding | Exact policy |
|---|---|
| `profile` | rth_developing at each complete minute |
| `highlight` | top35% execution sizes in prior 60 same-slot size distribution, threshold q65 |
| `confirmation` | E06 ABSORB at parent area, then separate defender reward |
| `consumer` | J01/J05 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `highlight_quantile` | 0.65 | [0.65, 0.8, 0.95] | quantile — prior-history display mask only |
| `flow_seconds` | 30 | [15, 30, 60] | seconds — matched-duration baselines rebuilt |
| `aggression_quantile` | 0.85 | [0.7, 0.85, 0.95] | quantile — E06 local aggressor volume gate |
| `max_excursion_ticks` | 4 | [2, 4, 8] | ticks — observed all-price excursion |

**Algorithm**

1. Build all signed/unknown bins from current RTH prefix, keeping negative local cells even inside a net-positive candle.
2. Apply the historical size quantile only to a second display/feature view; retain aggregate volume/delta unchanged.
3. At a parent interaction freeze profile snapshot and run E06 side-specific absorption with real excursion; no literal excursion constant or full-RTH baseline.
4. Evaluate local profile shape, highlight presence, absorption and later reward as separate columns and ablations; full day changes cannot affect earlier features.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `snapshot_id` | string |
| `local_buy_sell_unknown` | contracts[3] |
| `highlight_volume` | contracts |
| `absorption` | bool? |
| `actual_excursion` | ticks |

**Comparisons**

- aggregate profile only
- highlight mask only
- absorption vs same delay without flow

**Acceptance cases**

- Late 15:00 prints do not alter 09:45 bins.
- Empty signed volume cannot pass even if a quantile threshold is0.
- Net-positive candle with negative lower cells retains those negative cells.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J16 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `3b6a683c3f7b2ab36e971d6632964418161b436b8b5d1c438ca204067a3c938f`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j17"></a>
## R-J17 — Profile shelf/LVN confluence under range references

Define nodes, shelves and ledges algorithmic ally and compare explicit profile scopes; confluence means measured overlap rather than an ambiguous “under”.

**Role:** component. **Inputs:** D02, D04. **Engines:** E00, E03.

**Fixed consumers:** [R-J01](#r-j01), [R-J05](#r-j05), [R-J12](#r-j12).

| Binding | Exact policy |
|---|---|
| `primary_scope` | rth_developing |
| `location` | parent EQ/zone at first interaction |
| `selector` | nearest eligible node/band then prominence then lower price |
| `consumer` | J01/J05/J12 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `profile_scope` | rth_developing | ["rth_developing", "j69_frozen", "prior_rth"] | enum — distinct profile ownership |
| `feature` | LVN | ["LVN", "shelf", "ledge"] | enum — E03 exact detector |
| `smooth_ticks` | 5 | [3, 5, 9] | odd ticks — triangular kernel |
| `tol_ticks` | 2 | [1, 2, 4] | ticks — closed-band overlap padding |

**Algorithm**

1. Build selected profile at available snapshot; retain dense zero ticks and proper scope.
2. Detect E03 feature with specified smoothing and fixed prominence/shoulder rules.
3. Freeze the feature nearest to a given parent reference at first interaction, checking actual band overlap. No signed below inequality in baseline.
4. Test later parent response with and without confluence. Export distance and orientation so a signed-below variant can be registered later without rewriting history.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `profile_scope` | enum |
| `feature_band` | points[2]? |
| `distance` | ticks |
| `overlap` | bool? |
| `snapshot_at` | UTC ns |

**Comparisons**

- each scope with same node algorithm
- no-node parent control

**Acceptance cases**

- No node may lie outside profile support.
- Zero-volume internal ticks must remain available to LVN detection.
- A shelf created after the interaction cannot qualify that earlier episode.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J17 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `50cb377ed0ad4622d9310ad692b01c8568197dc581617e4b9cdfed73e5f33fcc`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j18"></a>
## R-J18 — Three-candle order block and rejection block

Implement full three-candle block and wick-only rejection-block branches with explicit structural-stop alternatives and actual later fills.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E08, E11.

| Binding | Exact policy |
|---|---|
| `window` | 09:00–11:30 |
| `location` | within 2 ticks of J69 edge or0.5 projection, geometry available |
| `side` | block formation direction |
| `entry` | market at C3 confirmation baseline; midpoint limit alternative |
| `target` | 1.5R0 from expected entry, direction ally rounded |
| `exit_horizon` | 12:00 |
| `stop` | stop_mode=full_C2: C2 adverse extreme plus2 ticks outward; local_control: E07 CONTROL_STOP at formation/entry decision |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `bar_minutes` | 3 | [2, 3, 5] | minutes — fixed clock aligned complete C1/C2/C3 |
| `block_type` | full_OB | ["full_OB", "wick_RB"] | enum — E08 formation; wick RB also requires close beyond full C2 |
| `entry_mode` | market | ["market", "midpoint_limit"] | enum — midpoint from frozen full block or wick; E11 trade-through |
| `stop_mode` | full_C2 | ["full_C2", "local_control"] | enum — full adverse C2+2 ticks or E07 CONTROL_STOP, computed before entry |

**Algorithm**

1. Construct complete bars and detect E08 bullish/bearish geometry; C2 must overlap a permitted available framework location.
2. Freeze geometry only at C3 close; both sides are implemented with exact mirrors.
3. For market branch submit at confirmation. For limit branch place at selected block midpoint after confirmation, cancel after 5 minutes or 11:30; no later retest means no fill.
4. Use explicit stop branch and 1.5R target under E11. Preserve full block, wick, midpoint and original stop separately; do not infer stop from later protective orders.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `C1_C2_C3` | bar IDs[3] |
| `block_band` | points[2] |
| `formed_at` | UTC ns |
| `fill_status` | enum |
| `net_R0` | float? |

**Comparisons**

- full OB vs wick RB
- market vs limit, same formation set

**Acceptance cases**

- C2[90,100], C1low92, C3close101 yields bullish full block[90,100] known C3 close.
- A missing minute in a3m candle invalidates formation instead of shifting rows.
- A C3 confirmation with no later midpoint trade-through is no_fill.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J18 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `d8ce5e4c76759456e8694f158275f741128298de91d627eb7178971b46be4ebc`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j19"></a>
## R-J19 — Prior RTH extremes and higher-timeframe imbalance draws

Use fresh prior-session extremes and causally formed HTF gaps as distinct target policies on fixed parent entries.

**Role:** management. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E08, E09, E11.

**Build dependencies:** [R-J01](#r-j01), [R-J05](#r-j05).

| Binding | Exact policy |
|---|---|
| `parents` | J01 and J05 entries separately |
| `high_low` | PRIOR_RTH both sides, first-visit lifecycle |
| `gap_scope` | previous5 trading sessions, same raw contract |
| `selection` | nearest eligible objective ahead |
| `exit_horizons` | ["12:00", "calendar RTH close"] |
| `stop` | unchanged parent stop |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `target_type` | prior_extreme | ["prior_extreme", "HTF_FVG_near", "HTF_FVG_mid", "HTF_FVG_far"] | enum — gap must be un contacted at decision in baseline |
| `gap_minutes` | 15 | [15, 60] | minutes — complete fixed-clock RTH candles |

**Algorithm**

1. Build prior RTH reference and scan every ETH/RTH revisit, with actual preceding trading date and early-close calendar.
2. Build prior-only HTF FVGs atC3 close; assign independent fill/expiry states.
3. For each parent decision choose nearest eligible target of selected type; external extreme must be fresh, gap must be untouched. No candidate yields no-target subset, not arbitrary final extreme.
4. Replay both horizons on identical entries/stops and report the qualified subset and whole-parent coverage; preserve target-type ownership.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `target_id` | string? |
| `target_type` | enum |
| `available_at` | UTC ns |
| `paired_outcome` | float? |

**Comparisons**

- parent default target
- prior extreme vs gap near/mid/far

**Acceptance cases**

- A previous RTH high revisited during ETH is inactive next morning.
- 15mFVG cannot exist before C3end.
- Target behind expected entry is rejected even if a later inequality is true.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J19 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `d28d5c1379ebd445f4c04c3dcea39450c0f0200a6cd66c253a1c8986dcd5d7bf`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j20"></a>
## R-J20 — Delayed cycle2 on10:00 release days

Measure the timing of fully specified reversals around actual scheduled 10:00 releases; no unpublished reversal definition remains.

**Role:** context. **Inputs:** D01, D02, D04, D09. **Engines:** E00, E01, E02.

**Build dependencies:** [R-J01](#r-j01).

**Fixed consumers:** [R-J01](#r-j01).

| Binding | Exact policy |
|---|---|
| `reversal_detector` | J01 default overshoot_return event detector, observation 09:00–11:00 without its entry-window gate; no trade implied |
| `calendar` | official named releases at 10:00 New York |
| `bins` | before 09:40,09:40–09:50,09:50–10:00,10:00–10:10,10:10–10:30,10:30–11:00,no_reversal; lower inclusive |
| `consumer` | J01 window comparison, preregistered broader news branch |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `release_group` | all_verified_1000 | ["all_verified_1000", "survey_only", "hard_data_only"] | enum — survey=ISM, Michigan, Conference Board; hard=Census/BLS/BEA10:00 publications; calendar stores actual agency/time |
| `event_time` | confirmation | ["confirmation", "first_touch"] | enum — first_touch remains diagnostic, never called completed reversal |

**Algorithm**

1. Build verified release membership independently of price moves and preserve calendar availability/vintage.
2. Run the shared J01 detector with a fixed 09:00–11:00 observation horizon; use the first confirmed reversal, preserving earlier failed episodes and side.
3. Cross-tab timing bins and no-reversal against calendar classes and non release controls; censored sessions are separate.
4. Compare conditional time forecasts and a preregistered J01 news-window extension; do not use release-day realized movement to identify news.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `release_ids` | string[] |
| `touch_time_bin` | enum |
| `reversal_time_bin` | enum |
| `no_reversal` | bool? |
| `conditional_probabilities` | float[] |

**Comparisons**

- non release same-weekday sessions
- touch-time vs completed-confirmation histogram

**Acceptance cases**

- A10:05 touch and 10:12 confirmation belongs 10:10–10:30 reversal bin.
- 08:30 CPI is not 10:00 calendar membership.
- Unknown-time FRED update cannot enter all_verified_1000.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J20 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `ea6834434717609ad26e642b674bba9d5eec736a8702493cffaa18d3e580786c`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j21"></a>
## R-J21 — News, range condition and target expectations

Define explicit preopen range/news classes and target-distribution forecasts; every unmatched case is other, not expansive by default.

**Role:** context. **Inputs:** D01, D02, D04, D09. **Engines:** E00, E01, E04.

**Fixed consumers:** [R-J01](#r-j01), [R-J04](#r-j04).

| Binding | Exact policy |
|---|---|
| `classification_at` | 09:30; post break state is separately timestamped |
| `classes` | extended, pre_news, ordinary; precedence extended then pre_news then ordinary |
| `news` | verified CPI, NFP, FOMC,08:30/10:00 releases, separately named flags |
| `targets` | EQ, edge,0.5,1.0,1.33 by noon, each conditional on actual parent direction |
| `consumer` | J01/J04 risk/target comparison only |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `extended_ratio` | 1.0 | [0.75, 1.0, 1.25] | ratio — W69/prior RTH width |
| `pre_news_days` | 1 | [0, 1, 2] | trading days — next verified scheduled major release within this many future trading dates, schedule already known |

**Algorithm**

1. At 09:30 compute width ratio and independently known calendar flags including whether a scheduled major release is later that week.
2. Classify extended when ratio meets threshold; otherwise pre_news if verified future release qualifies; otherwise ordinary. Missing width/calendar fields remain explicit and cannot be auto expansive.
3. For parent signals use class frozen before entry to forecast target-distance distributions, fitted on training only.
4. Compare any class-specific target policy against fixed parent targets on identical entries; source qualitative risk labels do not prescribe account sizing.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `class` | enum |
| `calendar_flags` | map<bool?> |
| `width_ratio` | float? |
| `target_probabilities` | map<float> |

**Comparisons**

- width only
- calendar only
- unconditional parent target distribution

**Acceptance cases**

- No width/news condition yields ordinary, not an assumed expansive state.
- Future realized AM trend cannot rewrite 09:30 class.
- A later schedule revision cannot be treated as known before its publication.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J21 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `e14a88e1f4afd20afb5aae781b796a57c3340c999d7df78b69119322ae6ac955`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j22"></a>
## R-J22 — Failure signatures and three failed attempts

Count distinct failed reaction attempts within a parent projection area and stop or switch only after the actual failure sequence is known.

**Role:** management. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E11.

**Build dependencies:** [R-J01](#r-j01).

| Binding | Exact policy |
|---|---|
| `parent` | J01 projection episodes |
| `reusable_object` | projection area only; consumed external high/low never rearms |
| `failure` | no response before deadline or adverse accepted close |
| `management` | after N consecutive failed distinct episodes disable that projection side for remaining AM; optional continuation entry is separate |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `failures` | 3 | [2, 3, 4] | episodes — consecutive failures; confirmed reaction resets count |
| `leave_ticks` | 4 | [4, 8, 12] | ticks — minimum departure from padded area to start distinct episode |
| `leave_seconds` | 60 | [30, 60, 120] | seconds — continuous outside separation |

**Algorithm**

1. Start from each projection area and chronological touch episode; save touch, separation, failure/confirmation and terminal time.
2. A completed response resets consecutive failures; expired or invalidated episodes increment. Censored episodes do neither.
3. After failures reaches threshold emit disable_side_at; apply it only to subsequent parent opportunities. Baseline does not retroactively close a previously filled trade or manufacture a continuation trade.
4. Replay J01 with and without this prospective disable policy on the full parent ledger, preserving missed trades and identical pre-disable entries.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `attempt_ids` | string[] |
| `consecutive_failures` | int |
| `disabled_at` | UTC ns? |
| `management_delta` | float? |

**Comparisons**

- no disable policy
- 2/3/4 distinct-failure thresholds

**Acceptance cases**

- Three adjacent near-level one-minute bars without departure count one episode.
- An unfinished final episode is censored and does not increment.
- A successful response between failures resets consecutive count to0.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J22 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `c79373f41de1aca3e0ea972919e36227b32673c486e8839684d3fea4fe645ac5`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j23"></a>
## R-J23 — Other published time-based range clocks

Provide a complete own-width framework for every published alternate clock, including geometry, first visits and conditional responses.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E02.

| Binding | Exact policy |
|---|---|
| `clocks` | ["TBR_ASIA", "TBR_MIDNIGHT", "TBR_LONDON", "TBR_RTH_A", "TBR_RTH_B", "TBR_LUNCH", "TBR_MOC"] |
| `geometry` | H, L, W, EQ,Q25,Q75,build_open,finish_open; projections0.1,0.2,0.3,0.5,1,1.33,1.66,2 |
| `primary_metric` | 4-way own-horizon path distribution |
| `consumer` | clock-specific J01-style research response detector, no cross-clock pooling |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `break_rule` | wick | ["wick", "close"] | enum — exact first visit vs complete-close directional path |
| `reaction_ticks` | 4 | [2, 4, 8] | ticks — E02 response for separately reported contact cohorts |

**Algorithm**

1. For every clock/date require complete formation and own outcome coverage; build every geometry field from that clock.
2. Track independent H/L active lifetimes and projection first-contact episodes from its freeze.
3. Produce four path classes and side/depth reaction outcomes at that clock own horizon. Statistics keep all seven clocks separate.
4. Compare training-smoothed forecasts across dates, never call midnight high/low rate a6–9 rate or reuse 09:40 entry gate.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `clock_id` | enum |
| `geometry` | object |
| `first_visits` | map<UTC ns?> |
| `path_class` | enum |
| `responses` | map<state> |

**Comparisons**

- unconditional distribution per clock
- wick vs close paths

**Acceptance cases**

- MOC wick below L with all closes inside is wick-low but close-neither.
- A clock with W10 uses its own0.5 distance5 even when W69=100.
- Empty outcome coverage is unavailable, not neither.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J23 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `83e7b9d1d5d6c154a73e5fcdc11f2283fd15da99f4c3ab11ccec139c66328432`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j24"></a>
## R-J24 — Post-entry excursions and management observations

Measure post-fill excursions correctly and compare explicit fixed-stop, break-even and confirmed-pivot management on identical entries.

**Role:** management. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E08, E11.

**Build dependencies:** [R-J01](#r-j01), [R-J08](#r-j08), [R-G01](#r-g01), [R-S05](#r-s05).

| Binding | Exact policy |
|---|---|
| `parents` | J01, J08, G01, S05, reported separately |
| `entry_ledger` | identical fills for every management candidate |
| `horizons` | ["09:50", "10:00", "12:00", "parent_expiry"] |
| `baseline` | parent fixed target and structural stop |
| `one_contract` | no fractional partial exits |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `management` | fixed | ["fixed", "break_even_at_1R", "confirmed_pivot_trail"] | enum — E11 stop cannot widen |
| `trail_minutes` | 5 | [1, 3, 5] | minutes — strict 1left/1right pivot for trail, known only after right bar close; unused fixed/BE |
| `BE_trigger_R` | 1.0 | [0.75, 1.0, 1.5] | R0 — executable favorable excursion before stop moves; unused other modes |

**Algorithm**

1. Load actual parent fills/stops/targets; reject drawing-only positions as non entries.
2. Calculate executable-side MFE/MAE only after fill; horizons earlier than fill areNA, not losses.
3. Apply selected management causally: BE at trigger moves stop to fee-adjusted break even on next eligible quote; pivot trail uses new confirmed adverse pivots only and never widens.
4. Replay identical orders except exits and record paired PnL, drawdown, duration, missed targets and stop changes; no new entry selection.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `MFE_R0` | float? |
| `MAE_R0` | float? |
| `horizon_applicable` | bool |
| `exit_policy` | enum |
| `paired_net_R0` | float? |

**Comparisons**

- fixed parent exits
- BE vs pivot trail on same entries

**Acceptance cases**

- Fill 10:34 makes 09:50/10:00 horizons NA.
- Low before fill cannot enter MAE.
- A stop raised above entry is management, not initial risk.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J24 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `b18b8753073c918e9375518ab36bb1b1ee0e85160b2215c548c7070b74dedb48`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-j25"></a>
## R-J25 — Trend-day retraces to confirmed swing midpoints

Use confirmed alternating swings and a causal trend-so-far filter for midpoint retraces; never select pivots from the final day.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E08, E02, E11.

| Binding | Exact policy |
|---|---|
| `entry_window` | 10:00–15:00 |
| `trend_so_far` | last 15 complete 1m closes >=80% on same side EQ69 and opposite J69 edge not visited since 09:00; both directions tested |
| `swing` | most recent confirmed alternating directional leg |
| `entry` | first post-confirmation midpoint retrace + E02 reaction in trend direction |
| `stop` | adverse swing endpoint+2 ticks |
| `target` | 1.5R0 fixed target, not a previously visited swing extreme |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `bar_minutes` | 5 | [3, 5, 15] | minutes — pivot bars fixed clock |
| `pivot_sides` | 2 | [1, 2, 3] | bars — strict l=r confirmation |
| `trend_share` | 0.8 | [0.7, 0.8, 0.9] | fraction — last 15completed1m closes same EQ side |
| `response_ticks` | 4 | [2, 4, 8] | ticks — midpoint REACTION |

**Algorithm**

1. Build confirmed pivots and alternating swings using E08 repeated-side replacement. Keep recognition and pivot times separately.
2. At each confirmed swing end evaluate trend-so-far using only last 15 complete closes and active/opposite edge history.
3. Freeze midpoint and wait for its first subsequent retrace; if price already revisited that level before swing became known, record consumed-before-eligibility and do not create a fresh midpoint entry. Confirm E02 in trend direction.
4. Execute E11 with endpoints top and fixed 1.5R target. Final trend day/single break remains outcome only.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `swing_ids` | string[2] |
| `swing_known_at` | UTC ns |
| `midpoint` | points |
| `trend_share` | float |
| `net_R0` | float? |

**Comparisons**

- midpoint retraces without trend filter
- 1/2/3 bar pivot confirmation

**Acceptance cases**

- Pivot at 10:00 with 2right5m bars is unknown until 10:15 bar close when bars are indexed by start.
- Mid100 and desired0.5*width20 reward requires110;105 is insufficient.
- A later opposite edge visit cannot erase an earlier causal trend eligible signal.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-J25 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_jumbo.json); record SHA-256 `6ce8363466d057bf683e46322b130265019a325a983457d543cbefb1a145eb76`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g01"></a>
## R-G01 — NYAM sweep and failed breakout

Use the first-visit NYAM sweep episode, a completed fail-back, and a separately tested full-excursion or local-control stop.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E07, E09, E11.

| Binding | Exact policy |
|---|---|
| `clock` | GB_NYAM |
| `entry_window` | 10:00–11:30 |
| `target` | opposite GB_NYAM edge, fresh at confirmation and ahead of expected entry |
| `stop` | selected stop_mode; fixed outward buffer2 ticks |
| `exit_horizon` | 12:00 |
| `sides` | upper short and lower long |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `sweep_ticks` | 1 | [1, 2, 4] | ticks — strict excursion after exact first visit |
| `close_minutes` | 5 | [1, 3, 5] | minutes — complete clock-aligned fail-back candle |
| `fail_deadline_minutes` | 30 | [15, 30, 60] | minutes — from first visit |
| `stop_mode` | full_excursion | ["full_excursion", "local_control"] | enum — full observed sweep extreme+2 ticks; local E07 CONTROL_STOP |

**Algorithm**

1. Freeze the complete 09:00–10:00 range and create independent H/L references at 10:00.
2. Run E02 SWEEP_FAIL on each first visit, allowing the sweep-containing bar to confirm only at its later completed close. Equality consumes the reference even before strict sweep.
3. At confirmation reject if the opposite edge was already visited. Freeze target and chosen structural stop; local control may lie inside the full wick and is explicitly a different research model.
4. Enter through E11; export failure given first sweep and target after filled entry separately. Subsequent retests cannot rearm the same external edge.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `range_id` | string |
| `visited_side` | enum |
| `sweep_depth` | ticks |
| `failure_at` | UTC ns? |
| `stop_basis` | enum |
| `net_R0` | float? |

**Comparisons**

- one-minute vs five-minute fail-back
- full excursion vs local control
- sweep without fail-back as descriptive control

**Acceptance cases**

- H120, L100, first high print120 then121 and complete 5m close119.75 yields short confirmation if deadline met; target100 must still be fresh.
- Opposite low touched before confirmation makes fresh-opposite-target baseline ineligible.
- A target drawing that extends beyond the chart is not a filled limit.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G01 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `7a7cc403b7d032fd1c59908677d7ee1267eaaf2f81a5029edfbe10b167ec4f7a`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g02"></a>
## R-G02 — Asia failure and TDO confirmation

Use the completed Asia range and optional same-episode midnight-open confirmation; midnight is not cash open.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E07, E11.

| Binding | Exact policy |
|---|---|
| `clock` | ASIA |
| `entry_window` | 00:00–05:30 |
| `TDO` | first print in 00:00 minute with actual availability |
| `target` | opposite ASIA edge, fresh and ahead |
| `stop` | full sweep excursion+2 ticks |
| `exit_horizon` | 06:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `sweep_ticks` | 1 | [1, 2, 4] | ticks — E02 first-visit sweep |
| `close_minutes` | 5 | [1, 3, 5] | minutes — fail-back candle |
| `TDO_gate` | false | [false, true] | bool — if true require a completed close after sweep below TDO for short/above for long by episode expiry; entry at later of failure and TDO condition |
| `fail_deadline_minutes` | 30 | [15, 30, 60] | minutes — from first visit |

**Algorithm**

1. Freeze 20:00–00:00 Asia box, independently create midnight open when its first print is known.
2. Run E02 SWEEP_FAIL during 00:00–06:00; confirmation must be before 05:30 for entry.
3. If TDO_gate is enabled, search a completed selected-timeframe close on the required side after the sweep. This is a post-sweep close state, not necessarily a new crossing; delay entry until both conditions exist and recheck target freshness then.
4. Use E11 with opposite-edge target and full excursion stop. Record optional gate attrition and delayed entries separately.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `asia_failure_at` | UTC ns? |
| `TDO_close_at` | UTC ns? |
| `TDO_price` | points |
| `opposite_edge_fresh` | bool? |
| `net_R0` | float? |

**Comparisons**

- failure only
- failure plus TDO close

**Acceptance cases**

- TDO100 and high-side fail close99 passes optional short gate; a missing midnight print is unavailable only for the gated variant.
- An 01:11 snapshot with target not yet reached stays un reached even if 01:18 reaches.
- Asia low consumed 02:21 is no longer a fresh target at 03:00.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G02 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `e653b42e23b216702be916727249bc029ac106b3b2645a0dca5d1f31cd9942a9`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g03"></a>
## R-G03 — Completed previous-hour failure

Evaluate every completed hour independently over exactly its next hour, then aggregate using actual eligible-hour counts.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E07, E11.

| Binding | Exact policy |
|---|---|
| `formation_hours` | 09:00–10:00 through 14:00–15:00 baseline; next-hour actions 10:00–16:00 |
| `entry_cutoff` | 5 minutes before each outcome end |
| `target` | opposite same-hour edge, still fresh |
| `stop` | full sweep excursion+2 ticks |
| `exit_horizon` | hour formation end+60 minutes |
| `denominator` | eligible completed boxes; both sides belong to their own episodes |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `sweep_ticks` | 1 | [1, 2, 4] | ticks — E02 strict depth |
| `close_minutes` | 5 | [1, 3, 5] | minutes — fail-back candle |
| `hour_scope` | RTH_next_hour | ["RTH_next_hour", "include_08_09"] | enum — alternative adds08–09 box trading09–10; no15–16 box trading after RTH |

**Algorithm**

1. Enumerate configured hours from the real calendar; require formation and next-hour coverage, no literal number of boxes.
2. Create new H/L IDs at each hour end and run E02 first-visit failures with a30-minute deadline bounded by that outcome hour.
3. Reject targets already visited by confirmation and submit E11 before the five-minute entry cutoff. Flatten by that hour end even if later price would reach target.
4. Report k failures / n eligible boxes, episodes, trades and any-success-per-day separately, clustering uncertainty by session.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `hour_box_id` | string |
| `hour_eligible` | bool? |
| `hour_failure` | bool? |
| `first_confirm_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- same-clock unconditional hourly path
- 08–09 inclusion as separate clock scope

**Acceptance cases**

- A09–10 box has outcome10–11, never10–12.
- Missing two boxes gives a smaller actual n, not a hard coded7.
- Two failures on two new hour IDs are distinct; two retouches of one consumed high are not.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G03 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `1bfc98d8636d9c8ed7f0e2dc545326005cc84ea2277b4bdb311050ec294ac15b`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g04"></a>
## R-G04 — 09:30 manipulation and reclaim

Define a symmetric opening-price manipulation/reclaim with explicit hold and risk; it is a research extension of the qualitative source.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E07, E11.

| Binding | Exact policy |
|---|---|
| `open` | 09:30 first-minute opening print |
| `entry_window` | 09:30–10:00 |
| `side` | undercut/reclaim long; overshoot/fail-back short |
| `target` | 1.5R0 from expected entry |
| `stop` | full pre confirmation manipulation extreme+2 ticks |
| `exit_horizon` | 11:00 |
| `open_lifecycle` | reusable open object, one first episode per side per day |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `manipulation_ticks` | 2 | [2, 4, 8] | ticks — excursion beyond open |
| `close_minutes` | 5 | [1, 3, 5] | minutes — first complete close through open by1 tick |
| `hold_minutes` | 3 | [0, 3, 5] | minutes — subsequent complete closes on reclaimed side;0 means no extra hold |

**Algorithm**

1. Create 09:30 open with real availability; include opening-bar manipulation only when execution ordering proves it follows the open.
2. For long require print<=open-manipulation_ticks, then a complete close>=open+1 tick; short mirrors. The first completed directional reclaim wins; an unordered simultaneous case is ambiguous.
3. Complete the selected subsequent hold, failing on a close back through open. Freeze manipulation extreme through confirmation, stop and target.
4. Enter E11 only before 10:00. A separately measured GP retrace cannot use the future final impulse; baseline uses fixed 1.5R target.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `manipulation_at` | UTC ns? |
| `reclaim_at` | UTC ns? |
| `hold_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- reclaim without hold
- 2/4/8 tick manipulation depths

**Acceptance cases**

- Open100, print99.5,5m close100.25 can confirm long only at that bar end.
- A reclaim at 09:59 followed by3-minute hold misses 10:00 entry deadline.
- The final09–10 box cannot be used by a 09:36 opening entry.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G04 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `8a888d86eccb1da164de281816a0c1eb2d03eca66c33232b89124171c013d9bf`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g05"></a>
## R-G05 — TDO close-through after a named sweep

Separate true midnight-open crossing from simply being on one side, and attach it to the same already-recorded fresh sweep episode.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E02.

**Build dependencies:** [R-G01](#r-g01), [R-G02](#r-g02), [R-G03](#r-g03).

**Fixed consumers:** [R-G01](#r-g01), [R-G02](#r-g02), [R-G03](#r-g03).

| Binding | Exact policy |
|---|---|
| `parents` | G01/G02/G03 confirmed sweep episodes |
| `TDO` | 00:00 opening print |
| `cross_direction` | after high sweep cross below TDO; after low sweep cross above TDO |
| `consumer` | delayed parent entry wrapper; never re grade an already filled entry using future data |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `close_minutes` | 5 | [1, 3, 5] | minutes — complete clock-aligned crossing bars |
| `deadline_minutes` | 30 | [15, 30, 60] | minutes — from parent first sweep |
| `confirmation_type` | cross | ["cross", "close_state"] | enum — cross requires previous completed close on opposite/equal side and new close strictly beyond; state only requires new close beyond |

**Algorithm**

1. Load a specific parent episode with reference ID, side and first-visit history, plus TDO available that date.
2. Search only bars closing after its sweep. For strict short cross require previous close>=TDO and current close<TDO; bullish mirror.
3. Emit known_at at the actual crossing close, bounded by deadline and parent expiry. If consumed reference later retouches it is still the old episode, not a new qualifying sweep.
4. A gated-entry consumer waits until max(parent_confirmation,TDO_confirmation), rechecks target and order eligibility then, and reports its delay against a matched control.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `parent_episode_id` | string |
| `TDO_cross_at` | UTC ns? |
| `TDO_state` | enum |
| `gate_known_at` | UTC ns? |

**Comparisons**

- close-state vs actual cross
- parent failure without TDO gate

**Acceptance cases**

- Entire window below TDO is a short state but not a new downward cross.
- An unrelated later sweep cannot upgrade an earlier entry.
- Missing TDO cannot become false cross or a guessed cash open.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G05 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `46511991701aabda4ce1b3d3c20279d44f0903c0d9b9cb0dcf249c940e04fde6`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g06"></a>
## R-G06 — Unfilled NWOG as a destination

Build an exact scheduled-close-to-Sunday-open NWOG and test untouched versus partially filled destinations on fixed parent entries.

**Role:** management. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E09, E11.

**Build dependencies:** [R-G01](#r-g01), [R-G02](#r-g02), [R-G03](#r-g03).

| Binding | Exact policy |
|---|---|
| `parents` | G01, G02, G03 entries separately |
| `gap` | E09 NWOG same contract |
| `target` | near/mid/far selected edge ahead |
| `stop` | unchanged parent stop |
| `exit_horizons` | ["parent horizon", "RTH close"] |
| `availability` | born at actual Sunday opening print; opening print does not count return |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `gap_state` | untouched | ["untouched", "not_fully_filled"] | enum — strict E09 return vs far-edge completion |
| `target_edge` | near | ["near", "mid", "far"] | enum — near relative to approach from current price; must lie ahead |
| `friday_endpoint` | globex_close | ["globex_close", "rth_close"] | enum — calendar last print before 17:00 or 16:00 typical; never call settlement |

**Algorithm**

1. Build gap endpoints using selected actual schedule and same contract; a zero gap is no_gap.
2. Track post-formation return, near/mid/far fill over all ETH/RTH events with E09 opening-endpoint exception.
3. At each parent decision require selected gap-state and an ahead destination. Freeze target version and compare only identical entries with qualified gap, reporting subset coverage.
4. Replay target policy under E11; a target visited before entry is handled as observed execution timing, not back filled success.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `gap_id` | string |
| `formed_at` | UTC ns |
| `first_return_at` | UTC ns? |
| `filled_at` | UTC ns? |
| `paired_net_R0` | float? |

**Comparisons**

- parent target
- untouched vs partial-gap destination
- Globex vs RTH Friday endpoint

**Acceptance cases**

- Friday100 Sunday110 creates[100,110]; forming110 print does not make it returned.
- Later109 penetrates gap and makes untouched false; full fill remains false until100 or below.
- A contract roll between Friday/Sunday makes baseline gap unavailable.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G06 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `806d581597ec5afbbb6fc8facbf7fa0f4701a6787d7c54b6d6069ba606ccbb98`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g07"></a>
## R-G07 — Golden-pocket continuation

Construct golden pockets from causally confirmed directional swings, with explicit timeframe and continuation confirmation.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E08, E09, E11.

| Binding | Exact policy |
|---|---|
| `entry_window` | 09:30–15:00 |
| `leg` | most recent E08 confirmed alternating swing |
| `pocket` | 50–61.8% retracement of that leg |
| `direction` | sign(B-A) |
| `stop` | adverse leg start A+2 ticks outward |
| `target` | unvisited leg endpoint B baseline; fixed 1.5R alternative |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `swing_minutes` | 5 | [5, 15, 60] | minutes — fixed complete bars |
| `pivot_sides` | 2 | [1, 2, 3] | bars — strict l=r |
| `confirmation` | reaction | ["reaction", "MSS"] | enum — E02 reaction4 ticks or E08 causal1mMSS after pocket touch |
| `target_mode` | leg_endpoint | ["leg_endpoint", "fixed_1.5R"] | enum — no implicit fallback from missing target |

**Algorithm**

1. Build chronological confirmed pivots and select latest complete directional leg before touch. The currently forming high/low is forbidden.
2. Compute pocket from ordered A, B and freeze; reject a pocket already touched after B occurred but before B confirmation for first-touch baseline.
3. At first eligible subsequent overlap require selected reaction/MSS in leg direction. Any external high/low confluence must have been fresh before its own first visit.
4. Freeze stop and target. Endpoint target must still be unvisited and ahead; otherwise no_target for endpoint variant. Enter E11 and retain no-fill/expired cases.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `leg_ids` | string[2] |
| `leg_known_at` | UTC ns |
| `pocket` | points[2] |
| `confirm_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- 50% line only with same leg
- reaction vs MSS confirmation

**Acceptance cases**

- Up leg100->120 gives pocket[107.64,110]; down120->100 gives[110,112.36].
- Cropped source swing high does not authorize deriving it from target price.
- A pullback before pivot confirmation isnot a causal post confirmation entry.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G07 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `974488f0f849960a24be13fe7cf8e40a5ca60a6b09fb8884268d2495ab5a19c5`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g08"></a>
## R-G08 — Overnight prior-extreme reclaim sets bias

Create a timed directional bias from a fresh overnight prior-extreme failure, with explicit hold and invalidation.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E02.

**Fixed consumers:** [R-G01](#r-g01), [R-G07](#r-g07).

| Binding | Exact policy |
|---|---|
| `reference` | previous completed RTH H/L baseline |
| `episode_window` | prior RTH close–09:30 |
| `bias` | high failure -> bearish; low failure -> bullish |
| `invalidation` | complete 5m close beyond observed sweep extreme by2 ticks, opposite confirmed bias, or 12:00 expiry |
| `consumer` | G01/G07 directional filter; missing bias is no filter qualification, not opposite bias |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `prior_scope` | prior_rth | ["prior_rth", "prior_eth"] | enum — actual previous calendar session |
| `hold_minutes` | 5 | [0, 5, 15] | minutes — subsequent completed 1m closes on reclaimed side |
| `sweep_ticks` | 1 | [1, 2, 4] | ticks — E02 first visit strict sweep |

**Algorithm**

1. Build prior reference and track first visits immediately from its close, including 16:00–18:00 trading where scheduled.
2. Run E02 SWEEP_FAIL with 5m close/30m deadline before 09:30; retain each direction episode.
3. After hold emit bias at actual completion; subsequent adverse close or opposite confirmed bias terminates it. A terminated bias never rearms from same consumed reference.
4. At each consumer decision join latest active bias, preserving absence/unavailable. Evaluate forward outcomes and exact gating costs with matched control.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `bias` | enum(long,short,none,unavailable) |
| `confirmed_at` | UTC ns? |
| `valid_until` | UTC ns? |
| `cause` | enum |

**Comparisons**

- no bias filter
- RTH vs full session prior reference

**Acceptance cases**

- Final 09:29 close cannot replace the ordered sweep/reclaim history.
- A16:45 first visit on prior day consumes that side before overnight window entry.
- A later invalidation cannot remove the earlier recorded bias interval.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G08 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `52fb49c4d3397cc3c01fa201c21ddc14d80e47b967a4758c76fb2ef8b35692f4`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g09"></a>
## R-G09 — Stacked high sweep, bearish shift, NWOG target

Define a fresh multi-reference sweep, fail-back and MSS followed by a live NWOG destination; test mirrored direction explicitly.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E08, E09, E11.

| Binding | Exact policy |
|---|---|
| `reference_set` | PRIOR_RTH, ASIA,GB_LONDON H/L |
| `entry_window` | 09:30–11:30 |
| `stack` | at least 2 distinct price clusters first visited within 15 minutes |
| `failure` | 5m close back beyond all swept edges toward range |
| `MSS` | E08 1m opposite pivot close break after fail back |
| `target` | untouched NWOG near edge ahead |
| `stop` | stack episode extreme+2 ticks |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `direction_scope` | both | ["both", "short_only", "long_only"] | enum — mirrors are named research variants |
| `stack_width_fraction` | 0.05 | [0.025, 0.05, 0.1] | W69 — max-min original reference prices <= fraction*W69 |
| `minimum_clusters` | 2 | [2, 3] | clusters — within 2 ticks references count one price cluster |
| `pivot_sides` | 1 | [1, 2, 3] | 1m bars — MSS pivot confirmation |

**Algorithm**

1. At 09:30 form candidate same-side stacks from available references; each must be fresh before its sweep, actual GB_LONDON clock 02:00–05:00.
2. Require strict 1 tick sweeps of minimum distinct clusters within 15 minutes, then a complete 5m close below all high stack levels for short or above all low stack levels for long.
3. Require later causal MSS and still-live untouched NWOG ahead; gap return before confirmation makes baseline ineligible. Earliest MSS after fail back qualifies.
4. Execute E11 with stack extreme stop and gap near edge target. Empty qualified stacks remain n=0; no all-day fallback.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `stack_ids` | string[] |
| `cluster_count` | int |
| `failback_at` | UTC ns? |
| `MSS_at` | UTC ns? |
| `gap_id` | string? |
| `net_R0` | float? |

**Comparisons**

- single-reference failure with same MSS/NWOG
- stack without MSS as diagnostic

**Acceptance cases**

- Two IDs at same price count one cluster.
- A PDH consumed Sunday cannot be re swept fresh Monday.
- Gap tagged 09:30 before MSS09:35 isnot untouched target at entry.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G09 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `49958a25d32fd7e62df2a728784f2f2e94ae6d0134e617f3d45cd0e4303db916`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g10"></a>
## R-G10 — Repeated fades on the pressure side

Define pressure causally and trade repeated same-side failures only across independently completed boxes.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E05, E11.

| Binding | Exact policy |
|---|---|
| `boxes` | G03 baseline hour set |
| `pressure` | last 15 completed 1m closes >=share below their own as-of RTH VWAP -> short; >=share above -> long; else neutral |
| `entry` | G03 first-visit failure on pressure side; each new box has new ID |
| `target` | fresh opposite edge of that box |
| `stop` | full sweep extreme+2 ticks |
| `exit` | own next-hour end |
| `session_cap` | 3filled entries, one per box |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `pressure_share` | 0.8 | [0.7, 0.8, 0.9] | fraction — strict side of contemporaneous VWAP; equality neither |
| `required_event_number` | 1 | [1, 2] | same-side episodes — 1 trades first and subsequent;2 waits for second independently formed reference failure |
| `close_minutes` | 5 | [1, 3, 5] | minutes — fail back timeframe |

**Algorithm**

1. Build as-of RTH VWAP and completed hour refs; require15known1m closes for pressure.
2. RunG03-style SWEEP_FAIL; at confirmation evaluate pressure using each close contemporaneous VWAP, not current VWAP applied backward.
3. Maintain count of qualifying same-side failures on different box IDs. Opposite pressure resets the count; neutral pauses without increment. Trade only at/after required number.
4. Submit E11 using selected box target/stop; a cover is an exit, not an opposite-side setup. Report references, attempts, trades and repeated same-side sessions separately.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `pressure` | enum |
| `pressure_share` | float |
| `same_side_event_number` | int |
| `box_id` | string |
| `net_R0` | float? |

**Comparisons**

- hour failure without pressure
- first vs second-event entry

**Acceptance cases**

- One low failure and one high failure are not two repeated shorts.
- A09:36 scalp cannot use completed 09–10box.
- Two retouches of same consumed high cannot increment reference count.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G10 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `e885e59d1d13397f7d613afca89e2c6df68251a829930249ed0f0f38c849d991`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-g11"></a>
## R-G11 — A+ grade belongs to the traded setup

Replace incomplete author A+ labels with an explicitly named four-item research quality score on a particular episode.

**Role:** component. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E06, E09.

**Build dependencies:** [R-G01](#r-g01), [R-G02](#r-g02), [R-G03](#r-g03).

**Fixed consumers:** [R-G01](#r-g01), [R-G02](#r-g02), [R-G03](#r-g03).

| Binding | Exact policy |
|---|---|
| `parents` | G01/G02/G03 pending confirmed failure episodes |
| `score_items` | ["same-reference fresh strict sweep+fail back", "fresh opposite target ahead", "post-sweep TDO close on trade side", "local ABSORB of opposing aggression available before grade"] |
| `grade` | Q0..Q4 only; no author A+ equivalence |
| `consumer` | parent entry wrapper atgradeknown_at; recheck target freshness then |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `minimum_score` | 3 | [2, 3, 4] | items — count known true; any required item unavailable ->grade unavailable, not zero |
| `flow_seconds` | 30 | [15, 30, 60] | seconds — E06 observation from first touch; matched history |
| `TDO_required` | false | [false, true] | bool — if true explicitly requires TDO item regardless sum |

**Algorithm**

1. Join all four items to the same episode/reference/side, with item availability and evidence IDs.
2. The flow window starts at first touch. Fix grade_at=max(parent failure confirmation, flow-window end). Do not wait for a later favorable TDO close.
3. At grade_at, evaluate all four items from available evidence. The TDO item is true if a qualifying completed post-sweep close exists by grade_at; otherwise false when TDO and bars are complete, or unavailable when inputs are missing. Recompute target freshness at grade_at. Unknown required input makes the grade unavailable.
4. For trading consumer compare parent price-only entry at the same grade clock againstminimum_score gate, rechecking target/order eligibility. Existing already-filled parent trades are diagnostic only, never retroactively upgraded.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `episode_id` | string |
| `quality_score` | int0..4? |
| `items` | bool?[4] |
| `grade_known_at` | UTC ns |
| `consumer_gate` | bool? |

**Comparisons**

- un graded delay-matched parent
- each one-item ablation

**Acceptance cases**

- A later unrelated failure cannot raise quality of an earlier entry.
- Missing flow is unavailable, not score0.
- A high-side failure cannot satisfy the low-side entry sweep item.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-G11 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_greenbird.json); record SHA-256 `527fabb366790fd9a2f9876d9db7f61fde34db4c0b511dd869e11511c3f51501`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a01"></a>
## R-A01 — Balance-edge fade to the fixed POC

Use a frozen algorithmic balance, causal edge rejection and a fixed POC target that is still ahead when the signal forms.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `trigger` | first eligible VAL/VAH area contact from inside balance |
| `side` | VAL long, VAH short |
| `target` | same frozen profile POC |
| `stop` | interaction adverse extreme+2 ticks |
| `outside_acceptance` | 30 subsequent complete 1m closes beyond edge disables fades of that accepted side |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `composite_sessions` | 2 | [1, 2, 3] | sessions — 1 removes multi-session balance-overlap gate;2/3 require all adjacent profile pairs satisfy E03 balance test |
| `response_fraction` | 0.1 | [0.05, 0.1, 0.2] | VA width — response=max(4 ticks, ceil(fraction*VA width/tick)ticks) |
| `confirm_minutes` | 5 | [3, 5, 15] | minutes — E02 reaction deadline |

**Algorithm**

1. Build selected complete same-contract composite; require positive VA width and balance gate. Fix VAL, VAH, POC before 09:30.
2. A candidate needs the last complete 1m close inside [VAL, VAH] before edge contact and no already-confirmed outside acceptance. Later acceptance cannot rewrite eligibility.
3. Apply E02 inward reaction with selected response distance; stop from touch-through-confirmation prefix. Reject at decision if confirmation has already passed POCso target is no longer ahead.
4. Execute E11 to fixed POC. Distinct reusable-area episodes require E02 separation; report rejection probability and post-fill POC reach separately.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `profile_id` | string |
| `edge` | enum |
| `rejection_at` | UTC ns? |
| `POC_target` | points |
| `net_R0` | float? |

**Comparisons**

- prior 1 profile vs multi-session balance
- price-only fixed 4 tick reaction vs width-scaled response

**Acceptance cases**

- VAL100, VAH120, POC111,10% response=2 points; lower touch then close102 can confirm long with target111 ahead.
- POC111 already below expected long entry112 makes no_target, not immediate success.
- Outside acceptance completed 11:00 cannot erase a 10:00 fade.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A01 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `149ec18434727c004998a64edfb090f23b50eb77bcbb1c06bf367e2f72d6757f`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a02"></a>
## R-A02 — Ledge break, retest and continuation

Use actual dense-profile shelf ledges, a completed outside hold, later retest and pre selected external node.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E09, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `object` | E03 shelf outer ledges, no VA fallback |
| `direction` | outward through selected ledge |
| `target` | nearest distinct HVN band centre ahead from prior 5 complete RTH profiles; current selected shelf excluded |
| `stop` | retest extreme+2 ticks |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `smooth_ticks` | 5 | [3, 5, 9] | ticks — E03 shelf smoothing |
| `hold_minutes` | 30 | [5, 15, 30] | minutes — outside hold after 2 tick completed close break |
| `retest_minutes` | 60 | [30, 60, 120] | minutes — search after hold |
| `response_ticks` | 4 | [2, 4, 8] | ticks — directional reaction |

**Algorithm**

1. Build complete dense profile and all E03 shelf bands; shelf width is its actual price span, not occupied-key distance.
2. For each ledge run E02 BREAK_RETEST with selected hold and time out, ordered by event time. No retest can precede hold completion.
3. At retest confirmation select a target from already frozen prior 5-session HVN objects. Require target ahead and outside the triggering shelf; ties E09. A naked historical node target is retired at its first post-formation touch, as specified for this target catalog.
4. Submit E11 with target centre and structural stop. If no node survives, no_target; do not switch silently to VAH/VAL or today final profile.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `shelf_id` | string |
| `ledge_band` | points[2] |
| `hold_at` | UTC ns? |
| `target_node_id` | string? |
| `net_R0` | float? |

**Comparisons**

- same shelf break without hold
- VA-edge alternative separately reported, never silent fallback

**Acceptance cases**

- Ticks100 and 102 with missing101 are not adjacent occupied rows; dense101=0 must remain.
- Break 10:00 and 30 minute hold requires subsequent closes through 10:30 before retest search.
- A target node visited overnight is excluded from the named naked-node target catalog.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A02 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `2b0716025712264eb48dce236096ab03413571cb89ec216c1110ee1c6005324a`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a03"></a>
## R-A03 — Re-entry, inside hold and opposite-edge traverse

Trade accepted re-entry from either an outside open or later outside excursion after a complete inside hold.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `origin` | outside 09:30 open or completed close2 ticks outside selected VA edge |
| `inside` | strict VAL<close<VAH for every holding close |
| `side` | re-enter from below -> long; from above -> short |
| `target` | opposite VA edge as reusable balance objective |
| `stop` | re-entry episode adverse extreme+2 ticks |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `inside_hold_minutes` | 30 | [5, 15, 30] | minutes — subsequent complete 1m closes after re-entry close |
| `origin_type` | both | ["both", "outside_open", "intraday_excursion"] | enum — separate eligible populations |
| `reentry_buffer_ticks` | 1 | [0, 1, 2] | ticks — required distance inside edge on initiating close; later hold still strictly interior |

**Algorithm**

1. Track outside episodes in both directions, preserving originating edge. For later excursions require an actual completed close beyond by2 ticks.
2. The first subsequent completed close inside by reentry_buffer starts hold. Every required later close must remain strictly inside; far-edge escape cancels this candidate.
3. At hold completion freeze direction, stop and opposite edge target. A earlier far-edge touch is history only; the target must be ahead at this new decision.
4. Execute E11, expire on declared session close; subsequent new profile-area episodes may qualify after failed holds with E02 separation.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `origin_type` | enum |
| `reentry_at` | UTC ns? |
| `inside_hold_at` | UTC ns? |
| `far_edge_after_fill` | bool? |
| `net_R0` | float? |

**Comparisons**

- re-entry without hold
- outside-open vs later-excursion cohorts

**Acceptance cases**

- Inside close 10:00 then30 subsequent valid minute closes confirms 10:30.
- A close equal VAL during strict inside hold fails.
- Far-edge touch 10:10 cannot count as outcome for 10:30 entry.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A03 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `5462d375ba2aaf6c6b67d8e9b8a57138c59c2b28c7ab28d1534d208eef81b882`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a04"></a>
## R-A04 — Strict two-period 80% rule

Define two complete consecutive periods inside prior value, then test the opposite-edge traverse; do not bake80% into the expected result.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E03, E11.

| Binding | Exact policy |
|---|---|
| `profile` | prior_rth VP70 frozen |
| `opening_gate` | 09:30 open strictly outside prior VA |
| `period_clock` | 30 minutes aligned 09:30 |
| `entry_window` | 10:30–14:30 |
| `direction` | toward opposite VA edge from original outside side |
| `stop` | near VA edge minus/plus2 ticks outward |
| `target` | far VA edge |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `inside_rule` | close | ["close", "full_range"] | enum — inclusive period close inVA vs all traded prices within VA |
| `period_minutes` | 30 | [15, 30, 60] | minutes — two complete consecutive periods, preserve clock alignment |
| `required_periods` | 2 | [2, 3] | periods — consecutive inside periods after outside open |

**Algorithm**

1. Require real outside open and freeze original entry side; search all consecutive qualifying period runs after 09:30, not just A/B.
2. Use selected inside predicate and complete period coverage; full-range requires min/max inside inclusive.
3. Earliest required-run completion in entry window confirms. If expected entry is outside VA or beyond the far target, no valid entry; do not declare traverse already won.
4. Execute E11 to fixed far VA edge with near-edge structural stop. Report eligible patterns and conditional target/PnL outcomes; source80% is comparison metadata.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `period_ids` | string[] |
| `pair_known_at` | UTC ns? |
| `inside_rule` | enum |
| `traverse_after_fill` | bool? |
| `net_R0` | float? |

**Comparisons**

- one-period re-entry diagnostic
- close vs full-range inside

**Acceptance cases**

- Two closes inside with a wick outside qualifies close-only but not full-range.
- A target reached before second period ends is not post entry success.
- Open exactly VAH is inside and fails strict outside open gate.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A04 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `16813b89e08f31fb48b8a41d5bd0b5a69f041ee3289f76e9110ae7c2a037e2b7`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a05"></a>
## R-A05 — POC repeated failure versus through-and-retest

Turn POC behavior into two ordered branches: distinct repeated failures toward the near edge, or through–hold–retest toward the far edge.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E11.

**Build dependencies:** [R-A03](#r-a03).

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `initial_state` | inside 09:30 open, or an A03 accepted re-entry |
| `POC` | fixed selected balance POC |
| `near_edge` | VAH when initial price>POC, VAL when below |
| `far_edge` | opposite near edge |
| `stop` | latest reaction/retest adverse extreme+2 ticks |
| `target` | two_failures: original near VA edge; through_retest: original far VA edge; selected edge must be ahead at decision |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `branch` | through_retest | ["through_retest", "two_failures"] | enum — continuation vs rotation branches |
| `failed_visits` | 2 | [2, 3] | episodes — used bytwo_failures |
| `hold_minutes` | 3 | [1, 3, 5] | minutes — POC completed close-through hold |
| `leave_ticks` | 4 | [4, 8, 12] | ticks — E02 distinct visit separation |

**Algorithm**

1. Fix initial POCside from first eligible inside state; if equal POC wait for a complete close outside2 tick band before establishing side.
2. For two_failures count distinct POC touches each followed within 5 minutes by a4 tick close back to initial side, with no successful through-hold before threshold. Repeated in-band bars count one visit.
3. For through_retest require completed close2 ticks through POC to opposite side, selected HOLD, then later retouch and 4 tick REACTION in that direction. This branch supersedes the still-pending two-failures branch when it confirms first.
4. At confirmation target near edge for failures or far edge for traverse; enter E11 with actual episode stop. Emit branch/known_at so later POC behavior cannot relabel an earlier trade.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `initial_POC_side` | enum |
| `visit_ids` | string[] |
| `branch` | enum |
| `confirmed_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- POC touch-only control
- two failures vs through/retest

**Acceptance cases**

- 12 contiguous near POC minutes are one visit, not12failures.
- Initial price above POC gives near VAH and far VAL.
- A later through break cannot erase an earlier completed two-failure trade.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A05 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `a804b54726792dd2f02665acb1aa23865fec893dbf953378a792f94b2b796b24`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a06"></a>
## R-A06 — Failed auction at an older external balance POC

Select an older untouched POC outside the current balance, then trade its first rejection after a balance breakout.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E09, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `older_catalog` | individual prior RTH POCs age2..10 sessions, excluding all current composite members |
| `POC_lifecycle` | naked target retires at first exact touch or crossing after its profile close; original first-tag episode may confirm later |
| `sequence` | balance close break2 ticks -> older external POC tag -> inward reaction |
| `target` | opposite edge of current balance |
| `stop` | old POC tag episode adverse extreme+2 ticks |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `max_age_sessions` | 10 | [5, 10, 20] | sessions — old POC catalog; same raw contract |
| `reject_minutes` | 5 | [3, 5, 15] | minutes — after first tag |
| `response_ticks` | 4 | [2, 4, 8] | ticks — close away from old POC back toward balance |

**Algorithm**

1. Build older POC ledger from completed profiles; retire first touch over all ETH/RTH. A current final RTH POC is forbidden.
2. At current balance breakout select nearest eligible old POC beyond the broken VA edge in break direction. It must lie outside current VA and be untouched then.
3. Wait for first tag within 60 minutes after break. On that same episode require E02 reaction against break direction; tag consumes naked POC but pending reaction remains valid.
4. Enter E11 toward far balance edge after rejection, saving target and actual stop. An un tagged old POC or same balance inside POC cannot satisfy setup.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `older_profile_id` | string |
| `older_POC` | points |
| `age_sessions` | int |
| `tag_at` | UTC ns? |
| `reject_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- balance break/re-entry without old POC
- 5/10/20 session naked POC catalog

**Acceptance cases**

- Current VA[100,120], older POC130 can qualify upper break; older POC110 cannot.
- Old POC touched overnight is not naked at 09:30.
- Upper break/old POC rejection short targets VAL100, not VAH120.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A06 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `4e9f01997f1cae32e86050298913d40a47cc34cb5d5061f926c31efe520fb9b1`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a07"></a>
## R-A07 — Confirmed boundary break and later holding retest

Make the boundary break, complete hold, later retest and post-retest hold one explicit episode; IB freshness cannot be rearmed.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E03, E09, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `boundary_types` | prior VA baseline; IB H/L or actual shelf ledge alternatives |
| `firstvisit_rule` | IB first exact visit begins only pending episode; completed break must occur within 5 minutes; failing/expired episode never rearms same IB side |
| `target` | nearest untouched prior 5 session HVN band centre beyond entry; no fallback |
| `stop` | retest adverse extreme+2 ticks |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `boundary_type` | prior_VA | ["prior_VA", "IB", "shelf_ledge"] | enum — own formation and lifecycle |
| `outside_hold_minutes` | 30 | [5, 15, 30] | minutes — after first close break |
| `retest_hold_minutes` | 30 | [3, 15, 30] | minutes — after retouch require every completed close remain on outside break side |
| `retest_timeout_minutes` | 60 | [30, 60, 120] | minutes — after outside hold |

**Algorithm**

1. Build selected boundary before use. Profile bands follow E02 reuse; IB high/low follow E01 first visit and the five-minute pending break deadline.
2. Require a complete 1m close2 ticks outside, then outside_hold_minutes subsequent closes outside. Any close inside fails candidate.
3. Find first later retest from outside, require4 tick reaction within 5 minutes and retest_hold_minutes complete closes outside from touch; confirmation is later of reaction/hold completion. Any close inside fails strict variant.
4. Select ahead untouched historical HVN target with known snapshot and E11 execute. No complete conjunction means no event, not a relaxed hold-only success.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `boundary_id` | string |
| `break_at` | UTC ns? |
| `outside_hold_at` | UTC ns? |
| `retest_at` | UTC ns? |
| `confirmed_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- 5/15/30 minute holds
- profile boundary vs IB reference

**Acceptance cases**

- IBL first visit 10:30 then failed pending episode cannot rearm for 11:55 break.
- A retest during outside hold cannot count as a later retouch.
- No inside close for30 minutes is stronger than merely no30 minute inside hold; implement the former.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A07 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `95a71e6e382d627265343787ef84af33fe94c4c5fb63c2aa4a3e0c2229845b61`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a08"></a>
## R-A08 — Re-acceptance flips the balance bias

Flip bias only after a real held outside break and a later complete inside re-acceptance.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `initial_requirement` | completed outside break and full hold even for outside open |
| `inside` | strict VAL<close<VAH |
| `direction` | opposite original outside break |
| `target` | opposite VA edge from reentry |
| `stop` | reentry adverse extreme+2 ticks |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `outside_hold_minutes` | 30 | [5, 15, 30] | minutes — subsequent complete closes outside |
| `inside_hold_minutes` | 30 | [5, 15, 30] | minutes — subsequent complete closes strict inside |
| `break_ticks` | 2 | [1, 2, 4] | ticks — completed close break distance |

**Algorithm**

1. Build current balance and find both direction outside break episodes; outside open still needs first complete outside close and hold.
2. Only after outside hold confirmation search for close back through same edge, then strict inside hold. Far-side escape cancels inside acceptance.
3. At inside confirmation set reversed bias with timestamp and freezes top/target. A failed profile area candidate may restart only after E02 distinct episode separation.
4. Enter E11 if target ahead; later outside accepted break invalidates bias without rewriting its past interval.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `outside_confirm_at` | UTC ns? |
| `inside_confirm_at` | UTC ns? |
| `bias` | enum |
| `far_edge_after_fill` | bool? |
| `net_R0` | float? |

**Comparisons**

- A03reentry without prior outside hold
- shorter vs strict 30 minute acceptance

**Acceptance cases**

- Outside open alone is not a30 minute held break.
- A far-side escape during inside hold fails, even if price is not back outside the original edge.
- Target before inside confirmation is not success.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A08 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `885fda9f52ea63a9f00f5c63afc9109fa61281033906612cf340475072b6426d`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a09"></a>
## R-A09 — Traverse without acceptance, then continuation retests

Define a full value traverse without any intervening accepted inside hold, then independently evaluate each later continuation retest.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `traverse` | completed close beyond one VA edge then later close beyond the other in traversal direction |
| `acceptance_exclusion` | no consecutive 30 minute strict inside close hold between crossings |
| `target` | fixed 1.5R0 after retest confirmation |
| `stop` | retest adverse extreme+2 ticks |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `inside_accept_minutes` | 30 | [15, 30, 60] | minutes — acceptance threshold; not a maximum traversal duration |
| `retest_reference` | both_edges | ["both_edges", "exit_edge_only"] | enum — candidates ordered by actual touch time |
| `response_ticks` | 4 | [2, 4, 8] | ticks — directional E02 reaction |

**Algorithm**

1. Enumerate ordered crossing pairs after 09:30. Upward traverse starts below VAL and ends above VAH; downward mirror.
2. Reject only if a full inside hold occurred between crossings. A45 minute traverse that never holds inside30 minutes can qualify.
3. After exit crossing search distinct later retests of selected edges from traverse side through 15:00. Evaluate all candidates chronologically; a failed first edge does not suppress later other edge.
4. Confirm E02 continuation, freeze actual stop and fixed 1.5R target, enter E11. Save prerequisite traverse and later retest outcomes separately.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `crossing_pair` | UTC ns[2] |
| `inside_max_run` | minutes |
| `retest_edge` | enum |
| `confirmed_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- quick traverse<=30 minute as descriptive bucket only
- exit-edge-only vs both-edge retests

**Acceptance cases**

- Traverse45 minutes with longest inside hold20 passes default.
- A30 minute inside hold invalidates even if total traverse31 minutes.
- A failed VAH retest cannot suppress a later eligible VAL retouch in the same down traverse.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A09 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `94cfcd28f338949bee46761ace4287e6a9477d6676c6f9e5a2fc9ca9f33871f1`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a10"></a>
## R-A10 — Opening auction type and completed day type

Create deterministic opening-type and final-day taxonomies, with final labels unavailable until the close.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E03, E05.

**Fixed consumers:** [R-G03](#r-g03), [R-J25](#r-j25).

| Binding | Exact policy |
|---|---|
| `opening_window` | 09:30–10:00 |
| `opening_references` | prior VA edges, fresh prior RTH H/L, ONH/L and 09:30 open, all identity qualified |
| `day_clock` | IB09:30–10:30 then RTH close |
| `consumer` | G03/J25 only after 10:00 opening type known |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `drive_close_fraction` | 0.8 | [0.7, 0.8, 0.9] | opening range fraction — long close position>threshold, short<1-threshold |
| `test_window_minutes` | 15 | [5, 10, 15] | minutes — actual reference interaction before subsequent drive |
| `trend_range_multiple` | 2.0 | [1.5, 2.0, 2.5] | IB widths — full RTH range threshold for trend label |

**Algorithm**

1. From executions retain first open and ordered crossings. After the forming open, a price strictly on the opposite side disqualifies a pure open-drive; equality alone does not.
2. At 10:00 classify with precedence test_drive, rejection_reverse, drive, rotation: test_drive requires actual available external reference touch in test_window_minutes, later close back through open, final net direction and close position meeting drive threshold; rejection_reverse requires an initial>=4 tick move one side and later>=4 tick close other side with final position threshold; drive requires no opposite open trade and final position threshold; remaining complete cases rotation. Zero width opening range is degenerate.
3. At RTH close classify trend if full range>=multiple*IBW, only one IB close break side and close in outer20% of daily range; else neutral_extreme if both IB sides broken and close outside IB; neutral if both and close inside; normal_variation if exactly one; normal if neither. Completeness and zero IBW guard apply.
4. Report opening type x day type conditional forecasts and forward consumer performance. No end of day label can enter morning features.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `opening_type` | enum |
| `opening_known_at` | UTC ns |
| `day_type` | enum |
| `day_known_at` | UTC ns |
| `transition_probabilities` | map<float> |

**Comparisons**

- unconditional day type
- opening return/width numeric features without taxonomy

**Acceptance cases**

- A strict excursion across open 09:30:20 disqualifies pure drive; ignoring first minute would be wrong.
- Being entirely above VAH is not an actual VAH test.
- Final day type is known only at calendar close.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A10 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `3e988c2106c9298dd47ef26dbcb11663fb750b315f272840d22adc9168e08d28`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a11"></a>
## R-A11 — Author-specific profile-shape outcomes

Replace ambiguous visual shape names with E03 quantitative B/P/b/D/other classes and test next-session distributions.

**Role:** context. **Inputs:** D02, D04. **Engines:** E00, E03, E04.

**Fixed consumers:** [R-A01](#r-a01), [R-A03](#r-a03).

| Binding | Exact policy |
|---|---|
| `profile` | prior_rth VP70 |
| `classification` | E03 precedence B, P, b, D, other |
| `outcome` | next RTH high-only/low-only/both/neither relative to prior VA, and opening-to-close signed return |
| `consumer` | A01/A03 after profile close; research names do not resolve author B diagram |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `profile_scope` | prior_rth | ["prior_rth", "balance_composite_2"] | enum — same algorithm different scope |
| `smooth_ticks` | 5 | [3, 5, 9] | ticks — node/shape smoothing |
| `tail_mass_cutoff` | 0.35 | [0.25, 0.35, 0.45] | volume fraction — P lower half/b upper half maximum; all other E03 shape thresholds fixed |

**Algorithm**

1. Build complete dense V and fixed VA; use price-distance coordinates, not occupied-key indices.
2. Compute E03 shape features and apply deterministic precedence with selected tail mass cutoff. Export underlying continuous features too.
3. At next session fit and score conditional path probabilities using prior training only; preserve N per label and no-trade other/degenerate cases.
4. Test shape increment in A01/A03 against unconditional balance features; never impose a published direction as a computed truth.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `shape` | enum(B,P,b,D,other,degenerate) |
| `POC_location` | fraction |
| `skewness` | float? |
| `tail_mass` | fraction |
| `forecast` | probability[4] |

**Comparisons**

- continuous shape variables without categorical bins
- unconditional prior profile outcomes

**Acceptance cases**

- POC location0.8 and lower half volume0.30 yields P unless higher precedence B qualifies.
- Adding internal zero volume rows must notre normalize price coordinates by occupied count.
- A finished profile shape cannot be moved before its close.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A11 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `f64155287e017bad2b6272ded1e49dc976133b104fe65f817d82efa184d36433`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a12"></a>
## R-A12 — Overnight inventory, LVN band and shelf reaction

Build overnight two-bulge/LVN structure from executions and test its first reaction with an explicitly defined inventory feature.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E03, E06, E11.

| Binding | Exact policy |
|---|---|
| `profile` | ON18:00–09:30 frozen 09:30 |
| `two_bulges` | two E03 HVNs separated>=0.20ON width with an LVN between; choose pair maximizing smaller peak prominence, ties nearest ON midpoint |
| `inventory` | net signed ON volume/total ON volume; abs<0.10 balanced; unknown side quality required only when gated |
| `old_POC` | mostrecentcompletedbalance_composite_2 ending before ON start; alignment feature separate |
| `entry_window` | 09:30–11:30 |
| `target` | fresh ONH for long/ONL for short |
| `stop` | band episode extreme+2 ticks |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `feature_band` | LVN_bridge | ["LVN_bridge", "upper_shelf", "lower_shelf"] | enum — E03 feature from selected pair; bridge=contiguous LVN band between peaks |
| `inventory_gate` | none | ["none", "same_direction", "opposite_direction"] | enum — compare trade d with sign of net inventory; balanced does not qualify gated variants |
| `response_ticks` | 4 | [2, 4, 8] | ticks — E02 reaction |

**Algorithm**

1. Build complete ON profile and selected two peak structure; no qualifying pair meansno_structure, not arbitrary minimum.
2. Select band before touch. Determine approach side from last complete 1m close: above band->long reaction, below->short; inside has no direction until departure.
3. At reaction confirmation apply optional inventory gate and check chosen ON extreme freshness from 09:30. Old POC alignment within 2 ticks is recorded but not mandatory baseline.
4. Execute E11 to fresh ON target; no target or missing required signed flow has explicit state.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `ON_profile_id` | string |
| `bulge_ids` | string[2]? |
| `band` | points[2]? |
| `inventory_ratio` | float? |
| `net_R0` | float? |

**Comparisons**

- reaction without inventory
- signed inventory same vs opposite direction
- old POC alignment ablation

**Acceptance cases**

- Net buy100, total1000 gives inventory+0.10, long aligned.
- A prior RTH profile cannot stand in for ON profile.
- ONH consumed before band confirmation is not fresh long target.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A12 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `18e34ecd37063e9ad0ccda752bdd5ac20ad285ea3cad31e58b9aba9f52a49c49`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a13"></a>
## R-A13 — Overnight reference touch statistics

Retain correctly scoped overnight-touch statistics and add independent price-midpoint and volume-value references.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E03, E04.

**Fixed consumers:** [R-G01](#r-g01), [R-J19](#r-j19).

| Binding | Exact policy |
|---|---|
| `formation` | ON18:00–09:30 |
| `observation` | 09:30–RTH close |
| `references` | ONH, ONL, ON mid=(H+L)/2, ON VAH, ON VAL, ON VPOC |
| `opening_cells` | below/inside/above ON price x below/inside/above ON value, equality inside |
| `consumer` | G01/J19 target context only |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `touch_rule` | exact | ["exact", "within_2ticks"] | enum — statistical interaction tolerance only; active external H/L retirement stays exact |
| `outcome_end` | RTH_close | ["12:00", "RTH_close"] | clock — separate horizons |

**Algorithm**

1. FreezeONpriceandtradeprofilewithownknown_at; distinguish arithmetic mid from VPOC.
2. Track first actual H/L visits independently from 09:30 and all reference contacts by selected horizon.
3. Publish high-only, low-only, both, neither, either with same eligible N and conditional opening-cell tables.
4. Score training conditional forecasts without transferring ES source percentages to NQ. Target consumers must check live freshness despite historical statistics persisting.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `first_touch_times` | map<UTC ns?> |
| `ON_path` | 4-wayenum |
| `either` | bool? |
| `opening_cell` | enum |
| `forecast` | map<float> |

**Comparisons**

- unconditional ON touches
- price-midpoint vs volume POC

**Acceptance cases**

- H120, L100 gives ON mid110 even if VPOC116.
- both+high only+low only+neither=N; either excludes neither.
- Missing outcome coverage is not neither.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A13 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `bc78d4d15d8314ac27873bcb4590383c28ccd279e80f44f8dbe762ef224d5fb0`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a14"></a>
## R-A14 — Prior TPO single prints, poor extremes and excess

Build a chronological ledger of actual prior TPO single runs, poor extremes and excess with explicit repair states.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E03.

**Fixed consumers:** [R-A18](#r-a18).

| Binding | Exact policy |
|---|---|
| `profile` | previous complete RTH TPO |
| `period_minutes` | 30 |
| `singles` | E03 interior same-letter runs, exclude entire edge-connected tails |
| `poor` | outer row has>=2 periods |
| `excess` | same-letter tail>=2 rows |
| `lifetime` | up to5 sessions or full repair; H/L first visit independent |
| `consumer` | A18 external target catalog |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `row_ticks` | 4 | [1, 4, 8] | ticks per TPO row — row origin0integer ticks; price bounds converted explicitly |
| `minimum_single_rows` | 2 | [1, 2, 3] | rows — interior same letter run length |
| `excess_rows` | 2 | [2, 3, 4] | rows — same-letter edge tail length |

**Algorithm**

1. Build period-identity sets at fixed price rows using trades, excluding decorative open markers. Save actual price bounds for each row.
2. Classify single runs, poor extremes and excess with chosen lengths; adjacent A-only andB-only rows are separate runs.
3. From profile close track first contact and each row visited. Single full repair requires all its rows visited; nearest row contact is not full repair. External poor/excess high low uses E01 first visit, with same first-tag episode response allowed later.
4. Export unfilled catalog at any as-of cutoff and separate repair/rejection outcomes. Presence of a poor extreme is not a trading win.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `TPO_object_id` | string |
| `period_sets` | map<set> |
| `run_price_bounds` | points[2] |
| `first_contact_at` | UTC ns? |
| `full_repair_at` | UTC ns? |

**Comparisons**

- row-size sensitivity
- poor/excess presence vs actual first test outcome

**Acceptance cases**

- Row index100 withrow_ticks4, tick0.25 corresponds price100, but with tick0.5corresponds200; never assume index equals price.
- Three A-only edge rows are all tail and none interior singles.
- Visiting one of three interior single rows leaves partial repair.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A14 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `9dd1a5103ec2f6221d6204f6d6da83effabcf5a60b3bfd61cf416a6965a5172e`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a15"></a>
## R-A15 — Initial-balance extension and conditional continuation

Measure completed IB extension and continuation with side-specific denominators and independent first-visit state.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E03, E04.

**Fixed consumers:** [R-A07](#r-a07), [R-J25](#r-j25).

| Binding | Exact policy |
|---|---|
| `formation` | IB09:30–10:30 |
| `horizon` | 10:30–RTH close |
| `primary` | close-break four way path |
| `continuation` | among high-only final RTH close>IBH; low-only close<IBL |
| `rotation` | neither-path sessions, post 10:30 touch fixed prior RTH POC |
| `consumer` | A07/J25 context available increment ally; final path only outcome |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `break_rule` | close | ["close", "wick"] | enum — completed 1m strict close vs inclusive execution visit |
| `break_ticks` | 1 | [1, 2, 4] | ticks — for close break distance; wick alternative uses exact visit regardless parameter |

**Algorithm**

1. Freeze complete IB and record contributing1m/1s execution rebuild comparison.
2. Track exact first visits and separate close break timestamps independently; first visit ends active line.
3. At RTH close classify path and compute continuation with side-specific conditional counts; neither rotation uses real post 10:30 POC contact.
4. Fit causal forecasts using only currently observed first break/width/open location; never use final high-only as already-known trend filter.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `IB_width` | points |
| `first_visits` | UTC ns?[2] |
| `first_close_breaks` | UTC ns?[2] |
| `final_path` | enum |
| `continuation` | bool? |

**Comparisons**

- wick vs close paths
- unconditional IB continuation

**Acceptance cases**

- Final close exact IBH fails strict up continuation.
- A wick below IBL with inside closes alters wick path but not close path.
- A10:30 first touch cannot be reset at the first later close break.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A15 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `ed7a3d8e703e5146d715afd54b5c0c7b94faf66c998bb10a1d1904b79bd5d843`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a16"></a>
## R-A16 — Actual ledge confluence and rejection

Trade measured ledge reactions and test confluence from independently identified objects available at contact.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E05, E06, E09, E11.

| Binding | Exact policy |
|---|---|
| `profile` | prior 5 complete RTH composite, same contract |
| `ledge` | E03 dense profile ledge |
| `partners` | as-of RTH VWAP and±1sigma, prior RTH VA edges, untouched older POCs; excludes objects derived from same origin profile |
| `entry_window` | 09:30–15:00 |
| `side` | reaction back toward higher-volume ledge side |
| `stop` | episode extreme+2 ticks |
| `target` | nearest same-profile HVN centre ahead; else no_target |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `confluence_required` | true | [false, true] | bool — at least one independent origin partner within selected distance |
| `distance_fraction` | 0.05 | [0.025, 0.05, 0.1] | prior VA width — max band distance |
| `absorption_gate` | false | [false, true] | bool — E06 opposite aggression absorption available before entry; gated decision delay matched |
| `response_ticks` | 4 | [2, 4, 8] | ticks — E02 reaction |

**Algorithm**

1. Freeze composite and detect actual ledge orientation. Profiles with contract changes are unavailable.
2. At first touch snapshot already available partners and their origin IDs. Exclude self-confluence and consumed external high low/naked POC targets.
3. Require E02 reaction toward higher-volume side. If absorption gate, wait for E06 completion and confirm defender direction before entry, retaining delayed control.
4. Select real HVN target ahead and E11 execute; compare stacked versus lone ledge visits on same parent universe.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `ledge_id` | string |
| `partner_ids` | string[] |
| `distance` | points |
| `absorption` | bool? |
| `net_R0` | float? |

**Comparisons**

- lone ledge
- confluence with outflow
- same-delay price-only reaction

**Acceptance cases**

- No on VWAP cannot be used at 09:45.
- The same profile VAH and its ledge cannot claim independent-origin confluence.
- A historical POC already visited cannot be used as naked partner.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A16 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `2c6a701fcc3b76574182ff148169d0d9715d1736effc9d0f17f6919e21c77136`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a17"></a>
## R-A17 — Second transition beyond a profile extreme

Identify a second accepted-volume region beyond a real profile transition; terminal taper and genuine bridge are distinct.

**Role:** component. **Inputs:** D02, D04. **Engines:** E00, E03.

**Fixed consumers:** [R-A16](#r-a16), [R-A18](#r-a18).

| Binding | Exact policy |
|---|---|
| `profile` | prior RTH baseline |
| `candidate` | E03 LVN outside VAL/VAH but inside profile full support |
| `direction` | from current value through candidate outward |
| `second_region` | beyond LVN band at least N consecutive dense price cells >=profile median positive volume; zeros remain below threshold |
| `consumer` | A16/A18 location feature |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `accepted_run_ticks` | 3 | [2, 3, 5] | ticks — consecutive accepted volume cells |
| `step_ratio` | 3.0 | [2.0, 3.0, 4.0] | ratio — high/low adjacent smoothed volume, low must>0 |
| `taper_ticks` | 3 | [3, 5, 8] | ticks — consecutive strictly decreasing outward volume to classify taper |
| `profile_scope` | prior_rth | ["prior_rth", "balance_composite_2"] | enum — completed fixed scope |

**Algorithm**

1. Build dense profile and candidate LVNs with orientation from the frozen VA, never choose whichever side total is smaller.
2. Compute acceptance cutoff as median of positive unsmoothed support volumes; if no positive volume unavailable. Search beyond candidate in outward direction for the first qualifying contiguous run.
3. Classify abrupt step when adjacent ratio>=step_ratio with nonzero denominator; taper when minimum selected strictly decreasing sequence exists; export both flags if both geometry parts occur, plus the second_region boolean.
4. Freeze geometry before later reactive consumer; measure first test response with/without second region, not shape-presence as win.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `candidate_band` | points[2]? |
| `second_region_band` | points[2]? |
| `second_region` | bool? |
| `transition_type` | enum |
| `acceptance_cutoff` | contracts |

**Comparisons**

- terminal taper without second region
- accepted run length sensitivity

**Acceptance cases**

- Volumes[150,160,40,30,140,155] have positive median145;140fails,155alone is not2 tick accepted run.
- Zero-volume gaps break accepted runs.
- A node outside full profile support is invalid.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A17 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `acec384b0cfefa3d24fdc2de983ce05b9f1d87866dfeba8cd6cd40ce6c80e40b`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-a18"></a>
## R-A18 — Balance-edge rejection or acceptance with unfinished targets

Implement all four balance-edge rejection/acceptance branches with real unfinished TPO or fresh-extreme targets.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E03, E09, E11.

**Build dependencies:** [R-A14](#r-a14).

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2 VP70, fixed before current RTH |
| `entry_window` | 09:30–15:00 |
| `exit_horizon` | 16:00 |
| `area_lifecycle` | E02 reusable profile area until accepted break or session expiry; external H/L targets use E01 |
| `branches` | VAL reject->long, VAH reject->short, accepted above VAH->long, accepted below VAL->short |
| `targets` | A14unfilled single-run near row or fresh poor/excess/prior RTH high low; nearest eligible ahead |
| `stop` | rejection episode extreme+2 ticks; acceptance break episode extreme+2 ticks |
| `inside_trigger` | excluded; must actual edge interaction |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `branch_mode` | both | ["both", "rejection_only", "acceptance_only"] | enum — four branches explicit |
| `accept_minutes` | 30 | [5, 15, 30] | minutes — outside HOLD after 2 tick close break |
| `target_kind` | all | ["all", "single_runs", "fresh_extremes"] | enum — no fabricated targets |
| `response_ticks` | 4 | [2, 4, 8] | ticks — rejection E02 confirmation |

**Algorithm**

1. Build real balance and A14as-of unfinished catalog, preserving row price units and prior-session coverage.
2. At edge first interaction run rejection and acceptance candidates in parallel; earliest completed confirmation wins for episode, exact tie chooses acceptance and records tie.
3. At confirmation choose ahead target that remains eligible then. Single-run target is nearest untouched row edge, with first contact and full repair reported separately. High/low target must be unvisited from own birth.
4. Freeze initial stop and target and execute E11. Missing target means no_target, never constant synthetic price or automatic positive bullish flag.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `branch` | enum |
| `bias_known_at` | UTC ns? |
| `target_origin_id` | string? |
| `target_price` | points? |
| `target_reached_after_fill` | bool? |
| `net_R0` | float? |

**Comparisons**

- rejection vs acceptance branches
- unfinished TPO vs fresh-extreme targets

**Acceptance cases**

- VAL rejection long cannot use a lower target.
- A target consumed while30 minute acceptance forms is ineligible at confirmation.
- A target tick index must be converted with row origin/tick size before order comparison.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-A18 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_amt.json); record SHA-256 `fc25c548d6f063429d4cb356170fa02159b45943f73cde14af109b612d39e487`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f01"></a>
## R-F01 — VWAP deviation fade with absorption

Use execution-weighted VWAP dispersion, an actual band contact and local opposing aggression that stalls; test the later fade to a frozen VWAP.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E05, E06, E09, E11.

| Binding | Exact policy |
|---|---|
| `anchor` | scheduled Globex open, normally 18:00 |
| `entry_window` | 09:30–15:00 |
| `band_snapshot` | previous completed minute; freeze version at first touch |
| `side` | upper short, lower long |
| `absorption` | E06 with aggressor toward outer band |
| `target` | VWAP frozen at confirmation |
| `stop` | touch-through-confirmation adverse extreme+2 ticks |
| `exit_horizon` | min(fill+60 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `VWAP_anchor` | ETH | ["ETH", "RTH"] | enum — scheduled Globex open vs 09:30 |
| `sigma_multiple` | 2.0 | [1.0, 2.0, 3.0] | standard deviations — execution-price weighted population sigma |
| `flow_seconds` | 30 | [15, 30, 60] | seconds — local absorption observation with matched history |
| `exclude_outstanding_draw` | false | [false, true] | bool — if true no fresh ASIA/GB_LONDON/PRIOR_RTH extreme within one frozen sigma beyond band |

**Algorithm**

1. Build E05 VWAP moments from the chosen anchor; require complete anchor history and positive sigma.
2. At the first actual band interaction freeze its prior-minute geometry and direction. Repeated minute updates cannot restart an already pending episode.
3. Run E06 ABSORB of approaching aggression, then E02 defender REACTION by four ticks beyond the near band edge within five minutes. If the optional draw exclusion is enabled, evaluate all reference lifetimes at confirmation.
4. Freeze VWAP target at confirmation and submit E11 only if ahead. Measure absorption, reaction and later target reach separately, with same-delay price-only controls.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `VWAP_snapshot_id` | string |
| `sigma` | points |
| `band_touch_at` | UTC ns? |
| `absorption_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- band reaction without absorption
- ETH vs RTH anchor
- outstanding-draw exclusion ablation

**Acceptance cases**

- Two trades at 100 and 102 with equal size give VWAP101 and sigma1.
- A candle wholly above an upper band is not a new interval-overlap touch.
- The noon VWAP cannot replace a 09:45 target snapshot.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F01 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `244fbb60ce824f6533b2ab3189aebf1b3f7a21e3f6cc98ca354739abf87956ac`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f02"></a>
## R-F02 — CVD divergence, breakout grade and absorption

Rebuild and validate signed CVD, then expose causal divergence, CVD breakout and absorption as separate features.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E06, E08.

**Fixed consumers:** [R-F15](#r-f15), [R-G09](#r-g09).

| Binding | Exact policy |
|---|---|
| `anchor` | scheduled Globex open |
| `trust` | D02 arithmetic, coverage, sign and overlapping-feed checks; no discretionary source clarification required |
| `pivot` | confirmed price pivots with CVD sampled at their actual pivot timestamps |
| `consumer` | F15 BIG branch and G09 divergence ablation |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `pivot_minutes` | 1 | [1, 3, 5] | minutes — fixed-time pivot bars |
| `pivot_sides` | 2 | [1, 2, 3] | bars — strict left/right confirmation |
| `CVD_threshold_quantile` | 0.5 | [0.25, 0.5, 0.75] | quantile — prior 60 same-slot absolute five-minute CVD change |
| `anchor` | ETH | ["ETH", "RTH"] | enum — separate reset scopes |

**Algorithm**

1. Normalize executed side and build CVD from one canonical stream. Unknown volume never receives a guessed sign. Fail quality as a typed unavailable result.
2. Attach CVD at each confirmed price pivot; compare ordered same-side pivot pairs using E06 divergence and the selected threshold.
3. Independently detect breaks of the prior complete 15-minute CVD range and local E06 absorption; neither is substituted for the other.
4. Expose feature availability at pivot confirmation or actual flow completion. Compare each feature in fixed consumers against price-only and same-delay controls; do not infer trust from how often CVD crosses zero.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `CVD` | contracts |
| `divergence` | enum(bull,bear,none,unavailable) |
| `CVD_break` | enum |
| `feature_known_at` | UTC ns |
| `signed_coverage` | fraction |

**Comparisons**

- price pivots without CVD
- divergence vs CVD breakout vs absorption features

**Acceptance cases**

- Buy100, sell70, unknown20 gives CVD30 and signed coverage170/190; this fails0.95 quality.
- CVD at a price high is not the maximum CVD anywhere in that interval.
- Appending afternoon trades cannot change a morning CVD/pivot observation.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F02 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `6c8c11144124b805868c82879ff0a2ccca3716460ff83e1b9f5cbd7908cb20e8`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f03"></a>
## R-F03 — Session, weekly and anchored VWAP convergence

Create real session, weekly and third-anchor VWAP convergence, then test its first subsequent reaction.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E05, E06, E08, E11.

**Conditional inputs:** {"third_anchor=latest_verified_release": ["D09"]}.

| Binding | Exact policy |
|---|---|
| `anchors` | RTH session, scheduled week open, and selected third anchor |
| `third_default` | first scheduled exchange session whose trading date is in current month |
| `entry_window` | 09:30–15:00 |
| `convergence_band` | min/max of three available VWAPs |
| `side` | approach-side reaction back toward origin side |
| `stop` | interaction extreme+2 ticks |
| `target` | 1.5R0 fixed |
| `exit_horizon` | min(fill+60 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `third_anchor` | month | ["month", "last_confirmed_5m_pivot", "latest_verified_release"] | enum — release within previous24hours with actual timestamp; absent anchor makes only that variant unavailable |
| `spread_fraction` | 0.05 | [0.025, 0.05, 0.1] | prior VA width — max VWAP-min VWAP threshold |
| `absorption_gate` | false | [false, true] | bool — E06 local opposing aggression, with delayed control |

**Algorithm**

1. Maintain independent E05 execution-weighted accumulators. Month starts at the scheduled open of the first trading-date session in that month; do not reset at arbitrary midnight.
2. At each minute end form convergence when its total spread is within the chosen fraction of prior RTH VA width. Freeze all three anchor IDs and the band at the first observable convergence.
3. Wait for a later actual touch; previous close above band defines long reaction, below defines short. Use E02 four-tick response and optional E06 absorption. An already-in-band close requires departure before a new approach.
4. Execute E11 with fixed 1.5R target. Compare with lone-session VWAP interactions in the same clock and delay; never replace missing weekly data with a price midpoint.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `anchor_ids` | string[3] |
| `convergence_band` | points[2] |
| `known_at` | UTC ns |
| `touch_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- session VWAP only
- third-anchor alternatives
- absorption gate ablation

**Acceptance cases**

- VWAPs100,101,102 converge at fraction0.05 only if prior VA width>=40.
- A pivot anchor may replay earlier trades but cannot signal before pivot recognition.
- Missing event time prevents event-anchor variant, not the default month model.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F03 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `6af11b87289ae4cf44dadf722b2a454a31afa31c2fd896348c24eda72147dd36`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f04"></a>
## R-F04 — Per-candle diagonal stack and later revisit

Use fully specified diagonal stacks within a candle, then a distinct departure and first retest in the stack direction.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E05, E11.

| Binding | Exact policy |
|---|---|
| `formation` | complete one-minute footprint baseline |
| `direction` | buy stack long, sell stack short |
| `zone` | all consecutive same-direction qualifying tick rows, not only longest |
| `departure` | >=4 ticks in stack direction after formation |
| `entry_window` | 09:30–15:00 |
| `retest_expiry` | 30 minutes after formation |
| `stop` | far zone edge or retest extreme, whichever more adverse, plus2 ticks |
| `target` | 1.5R0 |
| `exit_horizon` | min(fill+30 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `bar_minutes` | 1 | [1, 3, 5] | minutes — fixed-time complete candles |
| `ratio` | 3.0 | [3.0, 4.0, 5.0] | ratio — E05 diagonal numerator/opposition |
| `stack_rows` | 3 | [2, 3, 4] | adjacent ticks — same side in same candle |
| `zero_opposition` | exclude | ["exclude", "positive_min_cell"] | enum — alternative qualifies zero opposition only when own size>=min_cell10; both zero never qualifies |

**Algorithm**

1. Build E05 footprints from qualified signed trades. Enumerate every contiguous buy and sell stack with exact cell-pair evidence.
2. Freeze each zone at candle close; a zone cannot be retested before it exists. If two zones overlap, retain both identities and choose earliest subsequent confirmation for orders.
3. After directional departure wait for first later band return. Confirm E02 reaction in stack direction; a completed close beyond adverse zone edge by2 ticks invalidates.
4. Execute E11 and preserve stack-presence, return, confirmation and PnL denominators separately. New candle zones cannot rewrite previously frozen bounds.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `zone_id` | string |
| `cell_pairs` | list<object> |
| `formed_at` | UTC ns |
| `returned_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- ratio3 vs4 vs5
- zero-opposition exclusionsensitivity
- formed stack without retest as descriptive control

**Acceptance cases**

- Buy atp compares with sell atp-tick, not same-price sell.
- Three qualifying rows split across two candles are not one stack.
- Zero buy and zero sell cannot pass any mode.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F04 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `1ccd61ece3d5c9bc53ab6c67ccaa523925653e2bfef985e62012da15a36c6ef6`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f05"></a>
## R-F05 — At-level delta disagreement and intrabar POC flip

Detect price/delta disagreement and an actual intrabar POC move using prefix snapshots and fixed comparison geometry.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E03, E05.

**Fixed consumers:** [R-F08](#r-f08), [R-S03](#r-s03).

| Binding | Exact policy |
|---|---|
| `candle` | complete fixed five-minute container, streaming one-second prefix snapshots |
| `location` | available prior VA edge, J69 edge/projection or E03 ledge with actual contact |
| `direction` | price up with local negative delta -> bullish candidate; price down with local positive delta -> bearish candidate |
| `POC_reference_geometry` | prefix H/L frozen when disagreement first appears |
| `consumer` | F08 and S03 confirmation alternatives |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `bar_minutes` | 5 | [1, 3, 5] | minutes — candle duration |
| `position_partition` | halves | ["halves", "thirds"] | enum — bull old POC in lower half/third then new POC in upper half/third; bearish mirror |
| `persistence_seconds` | 2 | [1, 2, 3] | complete snapshots — new POCside must persist |
| `minimum_delta_contracts` | 10 | [5, 10, 20] | contracts — absolute local disagreement delta |

**Algorithm**

1. Process each candle in available-time order, maintaining prefix OHLC, dense total-volume profile and local signed delta in the contacted band.
2. At the first nonzero price change from candle open whose sign opposes local delta, freeze prefix H/L and old POC; require chosen delta magnitude and quality.
3. Within the same candle require POC price itself to move at least one tick in price direction and from the selected lower/upper partition to the opposite partition of the frozen range. Changing candle bounds alone cannot flip classification.
4. Emit only after persistence snapshots complete and before or at candle end. Preserve before/after profile IDs and compare later consumer responses against disagreement-only observations.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `candle_id` | string |
| `disagreement_at` | UTC ns? |
| `old_POC` | points? |
| `new_POC` | points? |
| `flip_known_at` | UTC ns? |

**Comparisons**

- disagreement only
- actual intrabar flip vs adjacent completed-candle POC change

**Acceptance cases**

- Frozen range100–110, old POC102, new POC108 is a bullish half flip; unchanged POC102 with expanded high120 is not.
- Price up and negative local delta must remain distinct from total candle delta.
- A flip requiring two seconds beyond candle end does not qualify that candle.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F05 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `1f079c7a00ee487aff7d0dff6d5646a0cd173dd301e22f2e04b8f265ad985d25`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f06"></a>
## R-F06 — Side-specific aggression absorbed at a marked level

Quantify local side-specific aggression, actual stall and later defender response at a frozen level.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E02, E06.

**Fixed consumers:** [R-A16](#r-a16), [R-F01](#r-f01), [R-F08](#r-f08), [R-S01](#r-s01), [R-S07](#r-s07).

| Binding | Exact policy |
|---|---|
| `locations` | parent prior VA, ledge, range edge or external high/low; each keeps its scope |
| `aggressor` | actual approach direction, not a hard coded side by level name |
| `observation` | E06 ABSORB; local delta and all-price excursion both explicitly labelled |
| `consumer` | A16/F01/F08/S01/S07 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `flow_seconds` | 30 | [15, 30, 60] | seconds — matched historical duration |
| `aggression_quantile` | 0.85 | [0.7, 0.85, 0.95] | quantile — prior same-slot same-side full-market volume |
| `max_excursion_ticks` | 4 | [2, 4, 8] | ticks — actual outward travel over complete observation |
| `response_fraction` | 0.1 | [0.05, 0.1, 0.25] | parent range width — later defender response, separate outcome from absorption feature |

**Algorithm**

1. Freeze parent area, approach direction and its own width before interaction. Missing parent width makes normalized response unavailable, not borrowed from J69.
2. Aggregate approaching-side volume inside padded area, signed coverage and true excursion across all observation prices; preserve their different scopes.
3. At observation end emit absorption feature if E06 conditions pass. Then measure defender response of max(4 ticks,selected_fraction*parent_width) within 15 minutes, with first passage and prior adverse invalidation.
4. Use only the feature available at the consumer decision; later response is an outcome unless the consumer explicitly waits for it. Track first-visit lifetime for external high/low origins.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `local_volume` | contracts[3] |
| `aggression_quantile_value` | contracts |
| `actual_advance` | ticks |
| `absorption_known_at` | UTC ns? |
| `later_response` | bool? |

**Comparisons**

- same location without aggression gate
- volume only vs volume-plus-stall

**Acceptance cases**

- A20 point advance cannot pass4 ticks onNQ.
- 17.5 points is less than0.25*251 but greater than0.25*67.75; use actual parent width.
- Absorption at a remote opposite edge cannot qualify this contact.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F06 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `3c49d6ae6ee1b733c1d291255d65834be697e85475a3cbac718b9d02ab3785fd`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f07"></a>
## R-F07 — At-touch reload inference and iceberg limitation

Build auditable displayed-reload inference from the available BBO stream; reserve identified iceberg claims for stronger data.

**Role:** component. **Inputs:** D02, D03, D04. **Engines:** E00, E01, E07.

**Fixed consumers:** [R-F17](#r-f17), [R-S01](#r-s01), [R-S03](#r-s03).

| Binding | Exact policy |
|---|---|
| `scope` | same raw NQ contract, exact best price and resting side |
| `cycle` | strictly later depletion and rebuild timestamps; nonoverlapping cycles |
| `quality` | no stale/crossed/reset/ambiguous book sequence |
| `consumer` | F17/S01/S03 as an optional observable feature |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `minimum_cycles` | 3 | [2, 3, 4] | cycles — within 30 second episode |
| `rebuild_seconds` | 1.0 | [0.5, 1.0, 2.0] | seconds — maximum time from qualifying depletion to rebuilt queue |
| `executed_display_multiple` | 2.0 | [1.5, 2.0, 3.0] | ratio — cumulative executed volume / maximum observed displayed size |
| `rebuild_fraction` | 0.8 | [0.5, 0.8, 1.0] | fraction — relative to pre depletion displayed size |

**Algorithm**

1. Use the last valid book state strictly before execution and exact executed price; trade-row book fields are not assumed pretrade.
2. Run E07 sequential cycle states. One rebuild update closes at most one cycle; do not start the next cycle before the previous terminates.
3. Require the selected cycle count, cumulative execution/display ratio and uninterrupted same-price best quote. An action cancellation without execution is not a depletion cycle.
4. Emit inference with raw evidence IDs and ambiguity/coverage rates. Validate cycle arithmetic and price-hold fixtures; do not label it hidden order identity or off-touch depth.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `reload_episode_id` | string |
| `resting_side` | enum |
| `cycle_evidence` | list<object> |
| `reload_known_at` | UTC ns? |
| `inference_quality` | enum |

**Comparisons**

- high execution/display ratio without cycles
- cycle thresholds and rebuild latency sensitivity

**Acceptance cases**

- q_before10,q_after4,q_rebuilt8 within 1 second qualifies one cycle, not three.
- One quote update cannot confirm three overlapping executions as three reloads.
- No pretrade quote or zero displayed size yields unavailable, not infinite ratio.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F07 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `34d4ec4a650b623f47879682dab8f0e2c023fca61705a867d11ae1628d8559c4`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f08"></a>
## R-F08 — Absorption location, three-tick reward and reward retest

Test a defended absorption area, a chronological three-tick defender reward and a distinct rewarded-area retest.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E06, E11.

| Binding | Exact policy |
|---|---|
| `locations` | prior VA edges and J69 projections with actual first eligible contact |
| `initial_direction` | defender direction opposite observed absorbed aggression |
| `reward` | E06 first favorable passage before adverse passage |
| `retest_band` | original absorption area, not reward endpoint or CVD value |
| `entry_window` | 09:30–15:00 |
| `stop` | retest extreme+2 ticks |
| `target` | 1.5R0 |
| `exit_horizon` | min(fill+30 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `reward_ticks` | 3 | [2, 3, 4] | ticks — defender reward threshold |
| `adverse_ticks` | 3 | [2, 3, 4] | ticks — before reward, adverse first passage fails |
| `POC_exclusion_fraction` | 0.0 | [0.0, 0.025, 0.05] | prior VA width — 0 no exclusion; otherwise area must not overlap POC±fraction*width |
| `retest_minutes` | 15 | [5, 15, 30] | minutes — after reward, E02 separation required |

**Algorithm**

1. Build E06 absorption at a qualified area; apply the explicitly optional POC exclusion, never a global POC ban.
2. After absorption availability measure defender reward with selected first-passage thresholds and 60 second expiry. Later adversity does not erase a reward that occurred first, but remains subsequent outcome.
3. After reward require directional departure and a distinct return to the original area. Confirm E02 defender reaction; a distant favorable extreme without return cannot qualify.
4. Execute E11 and report each stage denominator separately. CVD remains a separate same-unit feature; never compare market price numerically with CVD.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `absorption_id` | string |
| `reward_at` | UTC ns? |
| `adverse_first` | bool? |
| `retest_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- absorption reaction without reward/retest stages
- POC exclusion variants

**Acceptance cases**

- Reward+3 ticks before adverse3 succeeds even if later price reverses; adverse first fails.
- Original area100–101 and reward endpoint102 are distinct objects.
- A POC-excluded variant must not silently alter the no-exclusion baseline.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F08 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `a35ca691d746e2adb3d7f89ef62c4c732483acb6a04511ace6460914b7c7b8af`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f09"></a>
## R-F09 — Ordered STOP defense, exhaustion and lift-off

Require ordered defense, same-side exhaustion and an actual directional lift-off run, with declared print units.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E06, E11.

| Binding | Exact policy |
|---|---|
| `defense` | E06 ABSORB at prior VA/J69 area |
| `exhaustion` | successive nonoverlapping20-print windows of the previously absorbed aggressor side; both after defense, maximum 5 minutes |
| `lift_direction` | defender direction |
| `entry_window` | 09:30–15:00 |
| `stop` | defense/formation adverse extreme+2 ticks |
| `target` | 1.5R0 |
| `exit_horizon` | min(fill+30 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `large_median_contracts` | 10 | [5, 10, 20] | contracts per execution — first 20-print median>=threshold, next 20-print median<threshold |
| `run_ticks` | 3 | [2, 3, 4] | net ticks — monotone trade-price run in defender direction |
| `exhaustion_prints` | 20 | [10, 20, 40] | same-side prints — each of two consecutive windows |

**Algorithm**

1. Start one thesis episode from E06 defense and freeze absorbed/defender roles.
2. Collect first and second selected-count windows of that same aggressor side after defense; ignore opposite trades for window membership but keep them in price/coverage. Require high-then-low median and a subsequently completed one-minute delta sign in defender direction.
3. After exhaustion confirmation track the earliest monotone price run in defender direction. Unchanged prices do not reset; an opposite price change resets start; a multi-tick jump contributes its actual distance but one price-change count. Emit at the first run reaching selected tick distance.
4. Freeze stop from the already observed defense-to-lift-off path, enter E11 and measure later outcomes. Return actual run index/time, never the final AM print.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `defense_at` | UTC ns? |
| `window_medians` | contracts[2]? |
| `exhaustion_at` | UTC ns? |
| `lift_at` | UTC ns? |
| `run_change_count` | int |
| `net_R0` | float? |

**Comparisons**

- defense only
- defense plus exhaustion without monotone-run gate

**Acceptance cases**

- Three unchanged prices are not three up ticks.
- A two-tick jump counts2 ticks but1price change.
- A favorable run before exhaustion cannot satisfy later lift-off.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F09 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `c8191c04df800dcf63725a8010e5d8cd48990238e4e4f947cbd2fa155d283cda`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f10"></a>
## R-F10 — Protected swing after local delta and escape

Create protected swing state only after pivot confirmation, escape and a complete quiet interval; separate first revisit from later close-break invalidation.

**Role:** component. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E06, E08.

**Fixed consumers:** [R-J24](#r-j24), [R-S07](#r-s07).

| Binding | Exact policy |
|---|---|
| `pivot` | one-minute strict 2-left/2-right baseline; pivot_sides overrides both counts |
| `local_delta` | E06 extreme_band_delta_1m: signed volume within two ticks of pivot during the candidate pivot candle only; defender direction d=-1 at a high and d=+1 at a low; d*delta>0 and >= the registered prior-60-session same-slot band-delta quantile |
| `escape` | first complete one-minute close two ticks beyond the latest opposite pivot that was already confirmed at candidate recognition; escape must be later than candidate recognition |
| `quiet` | no price within two ticks of candidate pivot during every required subsequent complete one-minute bar after escape |
| `consumer` | J24/S07 optional structural stop reference |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `pivot_sides` | 2 | [1, 2, 3] | bars — strict symmetric pivot confirmation |
| `quiet_bars` | 5 | [3, 5, 10] | complete one-minute bars — after escape |
| `local_delta_quantile` | 0.75 | [0.5, 0.75, 0.9] | quantile — type-7 quantile of E06 extreme_band_delta_1m samples with identical side, one-minute duration and five-tick band |

**Algorithm**

1. Build strict confirmed pivots; freeze local signed delta using only executions in the candidate pivot candle and its closed five-tick band. Compare with the E06 matched historical band distribution, requiring positive defender delta and D02 side coverage. Save pivot formation, recognition, candidate candle and historical sample times.
2. At candidate recognition select the latest already confirmed opposite pivot, save its ID, and require a later directional escape close beyond that frozen price. An opposite pivot confirmed after candidate recognition cannot replace it.
3. After escape require every quiet bar with complete coverage and no candidate-level proximity. Protection becomes known only at the final quiet-bar close.
4. Track active first-visit lifetime from actual pivot formation, including the recognition/quiet interval. If already revisited, report protected-pattern history but no fresh active high/low. Separately track future complete-close break as a historical invalidation field.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `pivot_at` | UTC ns |
| `pivot_known_at` | UTC ns |
| `escape_at` | UTC ns? |
| `protected_known_at` | UTC ns? |
| `active_fresh` | bool? |
| `close_break_at` | UTC ns? |
| `local_delta_contracts` | signed contracts from candidate pivot candle only |
| `defender_delta_threshold_contracts` | prior-only matched E06 quantile in contracts |
| `historical_sample_ids` | ordered immutable candle IDs for the selected 60 prior sessions |

**Comparisons**

- confirmed pivot only
- escape without quiet hold

**Acceptance cases**

- Escape bar 17 followed by five complete quiet bars becomes protected at bar 22 close.
- An escape before pivot recognition fails ordering.
- First exact revisit ends active line even if no later close break occurs.
- Large opposing prints during recognition candles do not change candidate-candle delta; the historical threshold uses five-tick bands, not per-price cells or full-market volume.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F10 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `83e8c76d051e702941500d75a56c8dba46d04f02c72dd2b6056f06a518950667`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f11"></a>
## R-F11 — Delta-print pairing with an LVN at a balance extreme

Pair signed delta extremes with real same-profile LVNs, then test side-aware repeated profile-zone reactions.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E06, E11.

| Binding | Exact policy |
|---|---|
| `profile` | prior RTH VP/delta from identical executions |
| `pairing` | positive delta maximum near upper-side LVN -> short rejection; negative minimum near lower-side LVN -> long rejection |
| `zone_lifecycle` | reusable profile memory with E02 separation; any external H/L identity separately retires |
| `entry_window` | 09:30–15:00 |
| `stop` | reaction extreme+2 ticks |
| `target` | fixed same-profile POC if ahead; otherwise no_target |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `pair_distance_fraction` | 0.05 | [0.025, 0.05, 0.1] | profile full width — absolute price distance; candidate must be in corresponding outer quart ile |
| `sweep_ticks` | 2 | [1, 2, 4] | ticks — wick/execution beyond paired line before close back |
| `response_fraction` | 0.1 | [0.05, 0.1, 0.25] | profile full width — follow-through distance after close back; minimum 4 ticks |
| `profile_scope` | prior_rth | ["prior_rth", "j69_frozen"] | enum — completed snapshot only |

**Algorithm**

1. Build dense total and signed profiles over the identical scope. dp.max is maximum positive delta price, dp.min most negative; ties choose nearest corresponding outer edge then lower price.
2. Detect E03 LVNs and require same-snapshot pairing within selected distance and outer quart ile. No correctly signed extreme or LVN means no_pair.
3. At each distinct paired-zone visit require selected outward sweep and a complete 1m close back, then selected inward response within 5 minutes. Freeze zone and response width before touch.
4. Execute E11 only after full response, provided POC remains ahead. Report wick reaction and stronger follow-through separately; do not claim every repeated area test is a fresh external-high/low event.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `delta_extreme_price` | points? |
| `delta_extreme_value` | contracts? |
| `LVN_id` | string? |
| `pair_distance` | points |
| `confirmed_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- LVN only
- delta extreme only
- paired feature and response threshold variants

**Acceptance cases**

- Maximum traded price is not maximum delta price.
- A lower wick/close back must produce long mirror, never upper-only logic.
- Unpaired zones cannot score a favorable reaction.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F11 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `979b734de8ca04521cb75eba42ae06f267adbea2c279c22decb6f57cabe4a261`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f12"></a>
## R-F12 — Aggressive or drifting approach to a balance band

Measure approach speed and aggressive-volume slope before contact, then estimate both defense and acceptance outcomes without assuming their relationship.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E02, E03, E06.

**Fixed consumers:** [R-A01](#r-a01), [R-A07](#r-a07), [R-F16](#r-f16).

| Binding | Exact policy |
|---|---|
| `band` | frozen prior VA/dealing-range area supplied by parent |
| `feature_end` | last completed minute end <= first touch |
| `feature_window` | five full minutes, six endpoint closes |
| `toward_direction` | +1 from below band, -1 from above |
| `labels` | E02 inward reaction vs30 minute accepted outward break, neither/censored distinct |
| `consumer` | A01/A07/F16 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `speed_window_minutes` | 5 | [3, 5, 10] | minutes — use N+1 endpoint closes spanning N actual minutes |
| `fast_quantile` | 0.75 | [0.65, 0.75, 0.85] | quantile — prior 60 same-slot toward-displacement rate |
| `slow_quantile` | 0.25 | [0.15, 0.25, 0.35] | quantile — same historical population |

**Algorithm**

1. Freeze band and first-touch time; evaluate only preceding complete minute intervals, with approach direction established from price outside band.
2. Compute toward_rate=d_approach*(C_last-C_first)/(tick*elapsed_minutes), and OLS slope of same-aggressor volume over those N minute bins using x=0..N-1.
3. Fast requires rate>=fast quantile and volume slope>=0; drift if rate<=slow quantile or slope<0; otherwise mixed. Missing matched history or signed coverage yields unavailable.
4. After touch measure fixed 5 minute four-tick defender reaction and separately complete 30 minute outside acceptance. Fit class-conditional probabilities and test fixed consumers; do not infer source defending side from fast/slow names.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `toward_rate` | ticks/minute |
| `volume_slope` | contracts/minute-bin |
| `approach_class` | enum |
| `defense_outcome` | bool? |
| `acceptance_outcome` | bool? |

**Comparisons**

- speed alone
- volume slope alone
- unconditional same-band response

**Acceptance cases**

- Five closes one minute apart span4 minutes;3.9 points on0.25 tick then equals3.9 ticks/minute.
- A downward approach uses signed toward distance, not a reversed inequality bug.
- Post-touch high/low cannot enter the pre-touch speed feature.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F12 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `59795c64c561de3a81e6c67294b8ec1b56a7e576a98c6ea57038371d122476ce`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f13"></a>
## R-F13 — Prior-session trapped aggression and later break/retest

Use two prior known-zone failures, signed delta pairing and a newly frozen current microbalance break/retest with actual body aggression.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E05, E06, E08, E11.

| Binding | Exact policy |
|---|---|
| `historical_profile` | completed RTH two sessions before current trading date; known before prior AM/PM |
| `historical_zone` | upper positive-delta extreme or lower negative-delta extreme paired to E03 LVN within 0.05profile width |
| `historical_tests` | prior actual RTH AM09:30–12:00 and PM13:00–16:00, one distinct failed outward test each |
| `current_range` | first E08 microbalance after 09:30 |
| `entry_window` | 09:30–11:30 |
| `target` | 1.5R0 fixed |
| `stop` | retest extreme+2 ticks |
| `exit_horizon` | 12:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `pair_distance_fraction` | 0.05 | [0.025, 0.05, 0.1] | historical profile width — delta/LVN pairing |
| `body_trade_contracts` | 30 | [20, 30, 60] | single execution contracts — actual same-side print inside completed retest candle body |
| `break_hold_minutes` | 3 | [1, 3, 5] | minutes — current range outside hold before retest |

**Algorithm**

1. Freeze the historical profile before the prior day. Pair correct signed delta extreme and node; do not select a final current AM price extreme.
2. In each prior AM and PM require actual zone touch, outward attempt>=2 ticks and complete 1m close back within 5 minutes, with no30 minute accepted outward break afterward through that prior RTH close. These are historical profile-area episodes, not rearmed external highs/lows.
3. Build first current microbalance and freeze. For historically trapped buyers choose downward break/retest; trapped sellers upward. Require E02 break/selected hold then distinct retouch.
4. The complete 1m retest candle must contain an actual trade of selected size in trade direction inside its own body and close4 ticks back in breakout direction. Confirm at bar close, freeze stop/target and execute E11.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `historical_zone_id` | string |
| `prior_AM_test` | UTC ns? |
| `prior_PM_test` | UTC ns? |
| `current_box_id` | string |
| `body_print_id` | string? |
| `net_R0` | float? |

**Comparisons**

- current microbalance break/retest without historical pattern
- historical pair without body-print gate

**Acceptance cases**

- The same current AM observations cannot fill both prior AM and prior PM fields.
- A min(close)<min(low) predicate is impossible and must not appear.
- A red candle without an actual signed seller execution is not the body-trade gate.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F13 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `3fbc95469bc3b852e93129d1a82b474a0e74f8a48554ef5a67033b57609a4fea`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f14"></a>
## R-F14 — Colocated BigTrades imbalance, body/wick and retest

Match individual large prints to same-price imbalance in their own candle, then test a real later retest of the frozen print area.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E05, E06, E11.

| Binding | Exact policy |
|---|---|
| `bar_default` | fixed 1 minute |
| `range_bar_alternative` | 40 tick total high-low range; close on first execution reaching/exceeding40 ticks, retain overshoot; next execution starts next bar, no synthetic intermediate bars |
| `print_class` | body if price lies inclusively between own candle O/C; otherwise wick |
| `entry_window` | 09:30–15:00 |
| `side` | rewarded body -> aggressor direction; absorbed wick -> opposite direction |
| `stop` | retest extreme+2 ticks |
| `target` | 1.5R0 |
| `exit_horizon` | min(fill+30 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `bar_type` | minute1 | ["minute1", "minute3", "range40ticks"] | enum — explicit alternative construction |
| `print_size_mode` | 30_to_60 | ["30_to_60", "at_least_30", "prior_q99"] | enum — inclusive30..60; >=30; or E06 adaptive |
| `same_price_ratio` | 3.5 | [3.0, 3.5, 4.5] | ratio — same-price directional/opposite volume; denominator must be positive |
| `setup_type` | rewarded_body | ["rewarded_body", "absorbed_wick"] | enum — later directional reward vs E06 opposing defense |

**Algorithm**

1. Build complete chosen candles and all individual matched prints, preserving aggressor, price, size and availability.
2. At each print price require same-side total volume>=ratio*opposite volume with nonzero denominator and known side. Classify body/wick only at candle close.
3. For rewarded body require E06 aggressor reward after candle close; for absorbed wick require a local E06 absorption observation and defender reward after its availability. Then require departure>=4 ticks and a distinct first return to print band±1 tick within 30 minutes.
4. Confirm E02 in selected direction, freeze retest stop and E11 trade. Every matched print remains recorded; simultaneous entries use earliest confirmation then earliest print, not last match overwrite.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `print_id` | string |
| `candle_id` | string |
| `body_or_wick` | enum |
| `same_price_ratio` | float |
| `retest_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- size modes
- 3.5ratio vs literal4.5interpretation
- one-minute vs explicit range40 tick bars

**Acceptance cases**

- Zero/zero volume does not satisfy3.5ratio.
- A large print elsewhere in the candle cannot satisfy imbalance at another price.
- An intrabar retouch before body classification isnot a later known-area retest.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F14 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `c9b8253cc56f3794e2f3db0f124f100fe6585a0818c2562e471c87a92d48d42e`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f15"></a>
## R-F15 — Ordered catalyst, failed squeeze, refill and re-squeeze

Separate passive memory retests from ordered aggressive failure/refill/re-squeeze; only the BIG branch requires negative gamma and CVD.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E06, E07, E08, E10, E11.

**Conditional inputs:** {"branch=BIG_resqueeze": ["D05", "D06", "D07", "D08", "D10"]}.

**Conditional dependencies:** {"branch=BIG_resqueeze": ["R-R01", "R-F02"]}.

| Binding | Exact policy |
|---|---|
| `seed_locations` | prior VA edges or newly confirmed microbalance edges, available at first contact |
| `entry_window` | 09:30–15:00 |
| `catalyst_age_limit` | 120 minutes |
| `direction` | explicit catalyst defender/aggressor direction by branch |
| `stop` | E07 CONTROL_STOP at final retest, never whole-AM extreme |
| `target` | 1.5R0 fixed |
| `exit_horizon` | min(fill+60 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `branch` | aggressive_resqueeze | ["passive_memory", "aggressive_resqueeze", "BIG_resqueeze"] | enum — BIG adds selected R01 NDXP call-plus/put-minus negative gamma and E06 same-direction CVD range break before entry |
| `flow_seconds` | 30 | [15, 30, 60] | seconds — catalyst/absorption matched baselines |
| `failure_deadline_minutes` | 5 | [3, 5, 10] | minutes — after aggressive release |
| `refill_formation_seconds` | 120 | [30, 60, 120] | seconds — fixed E07 formation window |

**Algorithm**

1. At an eligible seed area build E07 catalyst with line, full band, side and available_at separately. A current final range or last AM prints cannot define it retroactively.
2. Passive_memory uses an ABSORB+defender REWARD catalyst: after departure wait for first distinct return to that original band, another local same-defender ABSORB or RELOAD, and E02 reaction. It does not require fast tape, failed squeeze, gamma or CVD.
3. Aggressive_resqueeze requires catalyst -> FAST release in direction d -> FAILED_SQUEEZE -> later REFILL_ZONE formation and return -> RESQUEEZE. Every transition must be later than the preceding available_at and within 120 minutes of catalyst; accepted adverse close through seed zone invalidates.
4. BIG_resqueeze uses the same sequence and additionally requires R01 selected NDXP scenario net negative and E06 CVD range break in d available at final confirmation. Unknown option/CVD data makes only BIG unavailable. Freeze local control stop/target and execute E11.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `branch` | enum |
| `catalyst_line` | points |
| `catalyst_band` | points[2] |
| `transition_times` | map<UTC ns> |
| `gamma_scenario_id` | string? |
| `net_R0` | float? |

**Comparisons**

- passive vs aggressive as separate populations
- aggressive with/without gamma/CVD
- failure/refill stage ablations

**Acceptance cases**

- Release before catalyst availability fails.
- Passive first return can qualify with slow tape and no option data.
- A favorable move without prior failed squeeze belongs F18, not aggressive F15.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F15 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `079f13a8e5473bad26353921f5218dd442313e0430c18cb49506579a89c364e6`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f16"></a>
## R-F16 — Failed aggression at a balance edge, then fade retest

Test failed edge aggression, an inward departure and a locally defended retest targeting a previously rewarded opposite print.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E05, E06, E07, E11.

**Conditional inputs:** {"gamma_gate=positive_NDXP_scenario": ["D05", "D06", "D07", "D08", "D10"]}.

**Conditional dependencies:** {"gamma_gate=positive_NDXP_scenario": ["R-R01"]}.

| Binding | Exact policy |
|---|---|
| `balance` | E03 balance_composite_2 |
| `entry_window` | 09:30–15:00 |
| `aggression` | outward at VAH for upper/VAL for lower |
| `target` | latest earlier rewarded opposite-side body print inside balance, price frozen; profile-memory target may have been visited earlier, external H/L may not |
| `stop` | E07 CONTROL_STOP |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `failure_observation_minutes` | 15 | [5, 15, 30] | minutes — no complete outward close beyond edge+2 ticks after aggression |
| `departure_fraction` | 0.25 | [0.1, 0.25, 0.5] | VA width — movement toward interior from tested edge |
| `gamma_gate` | none | ["none", "positive_NDXP_scenario"] | enum — only gated variant needs R01; no final day type substitute |

**Algorithm**

1. Record a local E06 outward aggression/absorption observation at the actual edge, then complete failure_observation_minutes with no outward accepted close.
2. Before that failed edge episode, find latest opposite-side body print >=30 contracts whose E06 reward was already known, located inside balance. Freeze its price as target; no eligible print meansno_target.
3. After failure confirmation require selected inward departure, then a distinct retouch of saved area and local E06 absorption of renewed outward aggression. Confirm E02 fade; do not require new own-side squeeze/reward.
4. Ifgamma_gate is enabled check selected positive R01scenario at confirmation. Execute E11 with local control stop and known opposite print target ahead, separately reporting repeat-memory targets vs external fresh levels.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `failed_aggression_id` | string |
| `failure_known_at` | UTC ns? |
| `retest_at` | UTC ns? |
| `target_print_id` | string? |
| `net_R0` | float? |

**Comparisons**

- edge fade without failed aggression stages
- gamma gate ablation
- actual print target vs fixed 1.5R diagnostic

**Acceptance cases**

- Departure is measured from tested edge only, not opposite box edge.
- Absorption at another level cannot confirm this retest.
- An opposite rewarded print known after the failure cannot be selected as an earlier target.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F16 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `5b818906c694836e5ab8b791af4407a15cbe06cdbe95f46b3ff9e872d6c0e3f2`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f17"></a>
## R-F17 — Refill-zone formation, return and held response

Freeze a refill band from explicit same-direction prints, require actual departure and return, then measure local held response.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E06, E07, E11.

| Binding | Exact policy |
|---|---|
| `parent` | E07 rewarded aggressive catalyst/release |
| `formation_start` | first qualifying print after release |
| `direction` | same as qualifying aggressive prints; defender at return is opposite approaching aggression |
| `entry_window` | 09:30–15:00 |
| `stop` | return extreme+2 ticks |
| `target` | 1.5R0 |
| `exit_horizon` | min(fill+30 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `formation_seconds` | 120 | [30, 60, 120] | seconds — fixed window from first print |
| `formation_mode` | fixed_window | ["fixed_window", "third_print"] | enum — full window end vs actual third qualifying print timestamp |
| `minimum_print_contracts` | 100 | [60, 80, 100] | contracts — single execution threshold NQ research units |
| `departure_ticks` | 4 | [4, 8, 12] | ticks — at least this distance in print direction before later return |

**Algorithm**

1. Build explicit qualifying print list from same side, size and time after causal release. Unknown/opposite prints never widen the band.
2. Fixed window freezes only at window end and requires>=3 prints; third_print freezes at third print. Bounds are min/max qualifying prices padded one tick and cannot widen afterward.
3. Require later directional departure then actual return within 30 minutes. At return require E06 defender absorption or E07 reload, then E02 reaction in print direction.
4. Execute E11 and report formation, return, held response and filled trade cohorts. A source32 tick bracket isnot silently substituted forthe1.5R research target.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `formation_mode` | enum |
| `print_ids` | string[] |
| `band` | points[2] |
| `known_at` | UTC ns |
| `return_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- fixed window vs stream threshold
- 60/80/100execution thresholds
- return with/without local defense

**Acceptance cases**

- First three buy prints and later opposite sell cannot expand buy zone.
- A120 second window is unknown at its last print10 seconds after start.
- A later favorable extreme without an intervening return isnot a held retest.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F17 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `350c932bc4adb8d5a40e9b7c950602b33e0b3f01579907b4c3b65075e1b93683`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-f18"></a>
## R-F18 — Fast squeeze without the prior failure

Route a fast catalyst release into an explicitly timed no-failure branch, then trade a later locally defended pullback.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E06, E07, E09, E11.

| Binding | Exact policy |
|---|---|
| `catalyst` | E07 aggressive catalyst with explicit direction |
| `entry_window` | 09:30–15:00 |
| `release` | complete 1m close beyond catalyst far edge+2 ticks and E07 FAST_APPROACH in d |
| `pullback` | first distinct return after no failure confirmation; earlier pullbacks are diagnostic and never backdated entries |
| `stop` | pullback adverse extreme+2 ticks |
| `target` | nearest fresh ASIA/GB_LONDON/PRIOR_RTH high/low ahead baseline |
| `exit_horizon` | min(fill+60 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `no_failure_minutes` | 15 | [5, 10, 15] | minutes — complete subsequent closes cannot cross catalyst adverse edge |
| `fast_quantile` | 0.8 | [0.7, 0.8, 0.9] | quantile — matched prior 30 second displacement rate |
| `target_mode` | fresh_reference | ["fresh_reference", "fixed_1.5R"] | enum — separate model, no automatic fallback |
| `pullback_deadline_minutes` | 30 | [15, 30, 60] | minutes — after no failure confirmation |

**Algorithm**

1. Build causal catalyst and fast directional release, retaining line and band identity.
2. Observe full no_failure_minutes after release. Any complete close through adverse catalyst edge fails this branch and may start F15only if its own sequence qualifies.
3. After confirmation wait for first eligible pullback to original catalyst/refill band, require local E06 opposing aggression absorption and E02 reaction in d. No unrelated morning VA flag can qualify.
4. Freeze target from fresh ledger at final confirmation or use explicit fixed target variant, stop from actual pullback and execute E11. Missing draw producesno_target.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `release_at` | UTC ns? |
| `no_failure_known_at` | UTC ns? |
| `pullback_at` | UTC ns? |
| `target_id` | string? |
| `net_R0` | float? |

**Comparisons**

- release without 15 minute hold
- fresh draw vs fixed target
- local defense gate ablation

**Acceptance cases**

- A15 minute no failure state cannot be known at release.
- A pullback before hold ends cannot become an entry backdated to that touch.
- A consumed Asia high cannot be the next fresh long draw.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-F18 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_flow.json); record SHA-256 `653d1559cefb096e8fd944f1c87e30ab39d786e9f65e67672d278a165573ec48`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-r01"></a>
## R-R01 — Native options, gamma scenario and level-conditioned regime

Build native, point-in-time option exposure scenarios with explicit pricing, OI vintage, scope and root finding; dealer inventory remains unobserved.

**Role:** context. **Inputs:** D04, D05, D06, D07, D08, D10. **Engines:** E00, E10.

**Fixed consumers:** [R-F15](#r-f15), [R-F16](#r-f16).

| Binding | Exact policy |
|---|---|
| `native_products` | NDX, NDXP, SPX, SPXW, QQQ, SPY separately; no price-coordinate pooling |
| `primary_product` | NDXP for NQ consumer context |
| `snapshots` | every 5 minutes 09:35–15:55, latest available inputs only |
| `default_expiry` | same-day expiration at true settlement timestamp |
| `European_pricing` | E10 parity-forward Black; native cash branch only if acquired |
| `American_ETF_pricing` | E10 CRR and declared dividend approximation |
| `walls` | same-right strike gamma maxima; keep OI-only walls separate |
| `consumer` | F15 BIG, F16 optional gate; no direct option orders |
| `quote_spread_sensitivity` | 0.15,0.30,0.50; diagnostic only, never selected for better PnL |
| `option_flow_pressure` | E10 previous complete 5 minute signed delta-notional transaction pressure; optional output with 80% quantity/sign/Greek coverage, never dealer-position inference |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `scenario` | call_plus_put_minus | ["call_plus_put_minus", "all_short", "all_long"] | position-sign hypothesis — explicit scenarios, not observed dealer ownership |
| `expiry_cohort` | 0DTE | ["0DTE", "1_to_7DTE"] | calendar DTE — separate populations; never silently pooled |
| `gamma_neutral_fraction` | 0.1 | [0.05, 0.1, 0.2] | abs net/gross — E10 neutral threshold |
| `max_relative_spread` | 0.3 | [0.3] | quote relative spread — Fixed baseline quality cap; 0.15 and 0.50 are separately reported coverage sensitivities, excluded from alpha selection. |
| `strike_scope` | stored_wide | ["stored_wide", "within_2pct", "within_5pct"] | native forward/spot moneyness — subsets of actually acquired scope; coverage ratio denominator matches selected scope |
| `gamma_stress_threshold` | -0.25 | [-0.1, -0.25, -0.5] | net gamma / gross absolute gamma — E10 stress-boundary root, separately named from zero-gamma flip; test subsequent realized volatility rather than asserting a volatility switch |

**Algorithm**

1. Create contract metadata and actual OI publication vintages, expiry instants, multipliers and exercise styles. As-of join each quote/spot/rate; known_at is maximum availability, not a request-date assumption.
2. Apply D06 quality and declared scope. Build European index forward from synchronized put-call pairs or native acquired cash; ETF spot is its own completed minute close. No NQ-to-NDX or ES-to-SPX level copy.
3. Solve IV and Greeks under E10 with convergence/no-arbitrage checks, then aggregate each sign scenario by native product and expiry cohort. Export calls, puts, net/gross and missing OI coverage separately.
4. Reprice aggregate gamma over E10 grid, find genuine sign-change roots, select nearest root and export all roots. Compute same-right gamma/OI walls and native distance features. Missing flip is no_flip, not zero gamma.
5. Fit native level-response/path distributions and test fixed NQ consumer gates only with fully available snapshots. A snapshot changes only when its inputs change; wall updates have their own expiry, not session-high first-visit semantics.
6. Compute E10 gamma-stress roots at the selected threshold and optional signed option-flow pressure. Keep those objects separate from flip/walls and evaluate later realized-volatility/consumer responses; missing trade-quote pressure does not suppress a valid gamma snapshot.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `native_snapshot_id` | string |
| `underlying_coordinate` | enum(spot,forward) |
| `OI_vintage` | UTC ns |
| `scope_coverage` | fraction |
| `net_gamma` | dollars per1pct move |
| `gamma_regime` | enum |
| `flip_roots` | native prices[] |
| `call_wall` | native price? |
| `put_wall` | native price? |
| `gamma_stress_roots` | native prices[] |
| `option_flow_pressure` | float[-1,1]? |
| `option_flow_coverage` | fraction |

**Comparisons**

- OI-only walls
- unsigned gross exposure vs signed scenarios
- same consumer without options gate
- 0DTE vs1–7DTE

**Acceptance cases**

- A zero-to-positive cumulative sequence is not a negative/positive flip.
- NDXP OI published 06:30 cannot be used 00:00 that day.
- Daily full-chain OI plus scoped minute quotes does not imply full intraday-chain coverage.
- Equal NDX and NQ numeric prices do not authorize treating them as the same underlying.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-R01 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_regime.json); record SHA-256 `506d47cb7c82c291c2725fad15fd19ca2385997bebe2d8efb06a0af65060fb8a`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-r02"></a>
## R-R02 — Prior-close VIX band and source regime comparisons

Use prior-known VIX bands and explicitly scaled return-volatility forecasts, then test their usefulness instead of interpreting membership as performance.

**Role:** context. **Inputs:** D01, D04, D08. **Engines:** E00, E04.

**Fixed consumers:** [R-J01](#r-j01), [R-A01](#r-a01), [R-F18](#r-f18).

| Binding | Exact policy |
|---|---|
| `VIX_bands` | <13,[13,14),[14,15),[15,18),[18,20),>=20 |
| `context_at` | 09:30 with previous published session VIX |
| `price_anchor` | previous complete NQ RTH close |
| `raw_scale` | anchor*VIX/(100*sqrt(252)), a return-volatility point scale, not full high-low width |
| `consumer` | J01/A01/F18 context only; no same-day VIX close feature |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `volatility_index` | VIX | ["VIX", "VXN"] | native index series — VXN variant requires its actual D08 history; missing is unavailable |
| `calibration` | raw | ["raw", "prior_q68_absolute_return"] | enum — raw index return-volatility scale or type7 q68 of prior normalized absolute return ratios, as defined in the algorithm |
| `history_sessions` | 120 | [60, 120, 252] | sessions — only used by calibration/conditional probability history |

**Algorithm**

1. Find last published volatility-index observation available before decision, preserving date and publication lag through holidays.
2. Assign exact nonoverlapping VIX bands for VIX; for VXN keep the same numeric boundaries as an explicitly different research categorization and export raw value.
3. Compute raw point scale. For calibrated variant take type7 q68 of prior N absolute NQ close-to-close return divided by corresponding prior-known index/(100sqrt252), then multiply current raw scale by that ratio. Samples crossing an un adjusted contract roll are excluded.
4. Measure future absolute close return and full high-low range as distinct labels, calibrate coverage/pinball loss, and test fixed consumers versus no-volatility context. Do not draw full-width bands without naming the scale convention.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `volatility_value` | index points |
| `band` | enum |
| `available_at` | UTC ns |
| `raw_return_scale` | NQ points |
| `calibrated_scale` | NQ points? |
| `future_abs_return` | points? |

**Comparisons**

- raw vs realized calibration
- VIX vs VXN when available
- unconditional consumer

**Acceptance cases**

- VIX14 belongs[14,15), not[13,14).
- VIX15.84 belongs[15,18);14.95 does not.
- Today eventual VIX close cannot gate today 09:30.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-R02 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_regime.json); record SHA-256 `62bd90e76a4ef19d0f21c2b0be753c2284eb9168bf5b12bdf7ee74cff843af08`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-r03"></a>
## R-R03 — Thesis lifetime and first invalidation cause

Measure thesis survival from actual creation to the first qualified invalidation cause, preserving the delay between a breach and its confirmation.

**Role:** management. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E02, E03.

**Conditional inputs:** {"cause_set=structural_profile_news": ["D09"]}.

**Fixed consumers:** [R-J24](#r-j24), [R-S07](#r-s07).

| Binding | Exact policy |
|---|---|
| `thesis_source` | consumer parent decision supplies side and broad frozen balance/area; no automatic noon thesis |
| `structural_death` | long: close below lower edge then outside hold; short above upper edge; neutral either |
| `profile_death` | developing RTH VA overlap fraction below threshold in3 consecutive complete-minute snapshots, only after 10:00 |
| `news_death` | actual scheduled CPI, NFP, FOMC, ISM release time after thesis start when selected |
| `objective_completion` | target first visit, separate from death |
| `consumer` | J24/S07 diagnostics or explicitly timed thesis-exit variant |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `cause_set` | structural | ["structural", "structural_and_profile", "structural_profile_news"] | enum — required inputs depend on selected causes |
| `structural_hold_minutes` | 30 | [5, 15, 30] | minutes — complete subsequent outside closes |
| `overlap_cutoff` | 0.25 | [0.1, 0.25, 0.5] | overlap fraction — intersection length/min(developing VA width, thesis width), both positive |

**Algorithm**

1. At actual parent creation freeze thesis ID, side, band, objectives and initial availability. A new thesis needs a new ID; do not redraw the old band.
2. Track structural breach start and full-hold confirmation independently. First exact revisit retires any external objective, but does not automatically kill structural thesis.
3. For enabled profile cause compute as-of E03 VA overlap and its three-snapshot confirmation. For enabled news cause use verified actual release time and calendar coverage; unknown required cause history makes complete survival unknown.
4. End at earliest qualified confirmation/release, retaining tied causes. Lifetime is end-start; alive-at-noon is right-censored at noon, not presumed alive until 16:00. Paired thesis-exit tests use identical parent entries.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `thesis_id` | string |
| `start_at` | UTC ns |
| `breach_started_at` | UTC ns? |
| `death_known_at` | UTC ns? |
| `causes` | enum[] |
| `alive_minutes` | float? |
| `objective_complete_at` | UTC ns? |

**Comparisons**

- structural cause only
- profile/news additions
- fixed parent exit for any trade consumer

**Acceptance cases**

- Breach 10:00 with 30subsequent held closes is known 10:30, not 10:00.
- Objective reached 10:15 and structural death 11:00 are different events.
- No observations after 12:00 imply censoring, not survival to 16:00.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-R03 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_regime.json); record SHA-256 `bb8b0eef674d8641f1194f461a1e7b6a2084a119c2dc2decd204db2ecb10a466`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-r04"></a>
## R-R04 — Native triad level-taking, SMT and first-fill reaction

Rebuild native NQ/ES/YM comparison objects and first-take/first-fill state; use each market’s own levels and units.

**Role:** context. **Inputs:** D01, D02, D04. **Engines:** E00, E01, E02, E03, E08.

**Fixed consumers:** [R-G09](#r-g09), [R-J01](#r-j01).

| Binding | Exact policy |
|---|---|
| `markets` | NQ, ES, YM baseline; optional RTY replaces YM |
| `clock` | 09:30–12:00 |
| `primary_event` | NQ first fresh prior RTH H/L take with at least one covered sister untaken at same event time |
| `sister_staleness` | last trade<=5 seconds old and complete intervening feed coverage |
| `directional_outcome` | NQ high first mismatch -> later short response; low first -> long response, a research hypothesis |
| `consumer` | G09/J01 optional filter |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `third_market` | YM | ["YM", "RTY"] | root — actual own data, no ratio mapping |
| `object_type` | prior_extreme | ["prior_extreme", "prior_VA_reaction", "TPO_first_fill"] | enum — three separate event definitions in algorithm |
| `response_fraction` | 0.1 | [0.05, 0.1, 0.25] | each own J69 width — post-event15 minute response, no cross-market price subtraction |
| `sister_agreement_seconds` | 60 | [0, 60, 300] | seconds — diagnostic lag window after first event; not available at first take |

**Algorithm**

1. Build corresponding prior RTH high/low, VP70 and TPO ledgers per market with real calendar and first-visit history. Reject missing maps/coverage; ES BBO is not needed for price-based sister events.
2. For prior_extreme, observe exact first takes and compare persistent taken/not_taken states asof NQ event. Co-timed events without cross-market ordering are co-first/ambiguous, not fabricated leaders. Later sister agreement is a new timestamped state.
3. For prior_VA_reaction, compare same-side E02 reactions at each own prior VA edge using own4 tick threshold. For TPO_first_fill, match runs by(origin trading date, singleton period letter, ordinal from low); require equal run counts for that letter across selected markets, then compare each own first contact/full repair times. No price-level mapping is used.
4. After eligible event measure each sister and NQ response in its own width/ticks over15 minutes; a sister-first full repair can invalidate the paired target at that time. Test causal first-event features in consumers, never eventual whole AM agreement.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `native_object_ids` | map<string> |
| `first_event_market` | enum |
| `taken_states` | map<enum> |
| `lead_lag_seconds` | map<float?> |
| `NQ_response` | bool? |
| `coverage` | map<state> |

**Comparisons**

- NQ event without sister filter
- native prior H/L vs VA vs TPO event types
- YM vs RTY when qualified

**Acceptance cases**

- NQ30000 is compared to its own NQ high, never ES6000.
- A sister high taken overnight stays taken after price returns below it.
- A TPO run only partially filled has not reached full repair.
- Missing sister data means unknown, not divergence.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-R04 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_regime.json); record SHA-256 `6273b9242f06cc194e9fe5cd74dfaa066c366c31867e9af15458f7421893d325`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s01"></a>
## R-S01 — Refill at the same defended dealing-range band

Enter only after renewed local defense at the same frozen area, preserving participant roles and a fresh objective.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E03, E06, E07, E09, E11.

| Binding | Exact policy |
|---|---|
| `band` | prior VA edge±2 ticks baseline, or actual E03 ledge |
| `direction` | lower/support long after sells absorbed; upper/resistance short after buys absorbed |
| `entry_window` | 09:30–15:00 |
| `entry` | first complete 1m close beyond band in defender direction after defense known |
| `stop` | defended local print minimum/maximum+2 ticks outward |
| `target` | nearest fresh PRIOR_RTH/ASIA/GB_LONDON extreme ahead |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `band_type` | prior_VA | ["prior_VA", "ledge"] | enum — actual frozen object scope |
| `defense_mode` | absorption | ["absorption", "reload", "both"] | enum — E06 observed stall, E07 BBO reload, or both same episode |
| `flow_seconds` | 30 | [15, 30, 60] | seconds — matched absorption interval |
| `target_mode` | fresh_extreme | ["fresh_extreme", "fixed_1.5R"] | enum — no implicit fallback |

**Algorithm**

1. Build the frozen support/resistance band, direction and first eligible contact; external high/low origin freshness is checked independently.
2. Require selected defense at that exact band and side. Sell aggression absorbed by buyers is different from new aggressive buys; retain both fields.
3. After defense availability require first completed 1m close above upper band for long or below lower band for short. Freeze local defended print extremes and chosen target.
4. Execute E11; missing BBO affects reload mode, not absorption-only observations, while execution still needs valid BBO. Report contact, defense, confirmation, fill and objective cohorts.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `band_id` | string |
| `absorbed_aggressor` | enum |
| `defense_known_at` | UTC ns? |
| `entry_confirm_at` | UTC ns? |
| `target_id` | string? |
| `net_R0` | float? |

**Comparisons**

- absorption vs reload vs both
- fixed target vs fresh objective

**Acceptance cases**

- VAH absorption cannot be reused for a VAL long.
- A first complete close at 09:46 is the trigger, not final AM close.
- Target revisited overnight cannot serve as fresh objective.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S01 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `b0de2f03cb63a85e6ba4870f2707917e39a1a3e5c73a1b83de961b8e56bdc740`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s02"></a>
## R-S02 — Third support test with absent defence and continuation entry

Count distinct tests of a reusable area and trade a real third-test break only when measured defense is absent, never when data is missing.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E06, E11.

| Binding | Exact policy |
|---|---|
| `band` | prior VA edge±2 ticks or established S01defense area |
| `support_branch` | first two tests defend, third has no qualifying defense then complete close below -> short |
| `resistance_branch` | exact mirror -> long |
| `entry_window` | 09:30–15:00 |
| `stop` | broken band far edge+2 ticks |
| `target` | 1.5R0 |
| `exit_horizon` | min(fill+30 minutes, RTH close) |
| `area_vs_reference` | three area tests do not create three fresh external H/L IDs |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `test_number` | 3 | [2, 3, 4] | distinct tests — all earlier tests must have qualified defender reaction |
| `departure_fraction` | 0.1 | [0.05, 0.1, 0.25] | prior VA width — new test requires interior departure this far and>=60 seconds |
| `defense_seconds` | 30 | [15, 30, 60] | seconds — complete observation; false only with qualified data |

**Algorithm**

1. Start an established profile-area record and count actual touches from the required side. One consolidation is one test until the selected departure and time separation occur.
2. For tests before selected number require E06 defense and E02 inward reaction; any accepted outward break invalidates area and ends count.
3. On selected test observe a complete defense window. Require defense=false with all inputs valid, then a completed 1m close2 ticks through the band in continuation direction before 5 minute expiry. Missing defense is unavailable, not zero.
4. Enter E11 with fixed band stop and target. Stop-out/return-to-entry is a later outcome, measured from actual fill, not band edge or source floating PnL.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `test_ids` | string[] |
| `defense_results` | state[] |
| `break_at` | UTC ns? |
| `net_R0` | float? |
| `return_to_entry_at` | UTC ns? |

**Comparisons**

- third test without defense-absence gate
- test-number and departure variants

**Acceptance cases**

- Three bars at the band without departure count one test.
- A missing trade partition cannot mean absent defense.
- Third contact alone without completed break produces no entry.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S02 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `a3914cf39e280a8e920aa1adca6fd3de88888050ec42055852979fe5c10e4532`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s03"></a>
## R-S03 — Second OFM defence with print-side refresh consistency

Specify the original catalyst and the exact participant side, then require a later second defense with non-thinning same-side prints.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E06, E07, E11.

| Binding | Exact policy |
|---|---|
| `catalyst` | E07 passive ABSORB+defender REWARD area, frozen |
| `second_defense` | first distinct later return after completed defender-direction close beyond band and departure |
| `participant_test` | approaching aggression is opposite defender d; alternative uses new aggressive defender prints explicitly |
| `entry_window` | 09:30–15:00 |
| `stop` | second defense local extreme+2 ticks |
| `target` | 1.5R0 |
| `exit_horizon` | min(fill+30 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `print_role` | absorbed_aggressor | ["absorbed_aggressor", "active_defender"] | enum — explicit tested side, no assumption based on unreadable source legend |
| `steady_fraction` | 0.8 | [0.6, 0.8, 1.0] | size ratio — last 3>=fraction*first among first 4qualifying same-side prints |
| `flow_seconds` | 30 | [15, 30, 60] | seconds — at second return; matched volume baseline |
| `minimum_prints` | 4 | [4, 6, 8] | prints — require at least this count; steadiness compares first vs final3within fixed window |

**Algorithm**

1. Build passive catalyst and first defense with role-labeled evidence. Require completed departure in defender direction, then E02 distinct return to same band.
2. Collect only selected role prints inside band in the fixed retest window; require E06 same-duration volume>=q85, signed quality andminimum_prints.
3. Define steady iff every last 3 size>=steady_fraction*first size; thinning is its logical complement on qualified samples. Do not allow both labels or compare one print with itself. Also require renewed E06 absorption at same band.
4. Confirm E02 defender reaction after all features known, freeze local stop/target and execute E11. BBO reload is separate optional diagnostic, not inferred from steady sizes.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `catalyst_id` | string |
| `print_role` | enum |
| `print_sizes` | contracts[] |
| `steady` | bool? |
| `second_defense_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- second defense without steadiness
- absorbed-aggressor vs active-defender role

**Acceptance cases**

- Sizes[100,80,90,85] pass0.8;[100,79,90,85] fail.
- Three prints cannot satisfy minimum 4.
- Same retest window cannot be labeled both steady and thinning.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S03 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `427cf763a593e982c4c1061d05a1cbc74a31d29431b8229cc92150376b2fde6d`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s04"></a>
## R-S04 — ATH pullback, weekly aggression box and microbalance entry

Create an explicit record-high context, weekly signed-volume support hypothesis and later microbalance entry; test sign and ratio assumptions openly.

**Role:** signal. **Inputs:** D01, D02, D03, D04, D07. **Engines:** E00, E02, E03, E05, E06, E08, E11.

| Binding | Exact policy |
|---|---|
| `record_context` | previous available native NDX daily close >=0.995*maximum NDX daily high in stored history through that date; label stored-history record context, not proven all-time record if archive incomplete |
| `weekly_profile` | previous complete exchange week RTH executions, same raw NQ contract |
| `weekly_band` | most negative delta cell in upper half weekly support, padded2 ticks; require negative value |
| `hypothesis` | failed selling at weekly band -> bullish defense; positive-delta alternative explicit |
| `entry_window` | 09:30–15:00 |
| `microbalance` | first E08 box formed after second defense |
| `stop` | microbalance low-2 ticks |
| `target` | 1.5R0 baseline |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `record_distance_fraction` | 0.005 | [0.0, 0.005, 0.01] | native NDX fraction — prior close distance below stored historical high |
| `weekly_sign` | negative_absorbed_selling | ["negative_absorbed_selling", "positive_rewarded_buying"] | enum — negative: E06 sell absorption; positive: E06 buy reward |
| `same_price_ratio` | 3.5 | [3.0, 3.5, 4.5] | buy/sell volume ratio — new complete 1m local buy confirmation at band; positive opposition required |
| `defense_tests` | 2 | [1, 2, 3] | distinct tests — E02 area separation |

**Algorithm**

1. Build record context solely in NDX daily coordinates and freeze prior weekly NQ profile; no cross-instrument level copy. Contract roll week without qualified mapping is unavailable.
2. For negative branch select upper-half most negative delta band; positive branch most positive upper-half band. Require selected number distinct local defenses/rewards with correct roles.
3. After those conditions, require a complete local1m candle with buy/sell same-price ratio meeting threshold at one known band cell, then form first E08 microbalance from later bars. The green box is this observed candle/rowspan, not an all-AM aggregate.
4. Enter long on first causal microbalance close break under E11. Use structural stop and fixed target; fresh HTF target maybe reported as separate candidate, never invented above a new record.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `NDX_context_known_at` | UTC ns |
| `weekly_profile_id` | string |
| `weekly_band` | points[2] |
| `defense_ids` | string[] |
| `microbalance_id` | string? |
| `net_R0` | float? |

**Comparisons**

- same setup without record context
- weekly sign alternatives
- 3.5vs4.5 same-price ratio

**Acceptance cases**

- A five-calendar-day profile is not automatically an exchange week.
- 1.5>1; any<=1fixture must fail.
- The microbalance cannot be known before its final formation bar; later protected stop is not initial risk.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S04 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `bbed9357e011d9f02b23d47a44054efc513a6a5ce731080d1e1ef85e9813715f`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s05"></a>
## R-S05 — Price-defined microbalance with first breakout and structural stop

Establish the first qualifying price microbalance, freeze it, and trade only its first eligible completed breakout episode.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E08, E09, E11.

| Binding | Exact policy |
|---|---|
| `search_window` | 09:30–15:00 |
| `scale` | frozen J69width |
| `formation` | first chronological rolling N complete 1m bars meetings elected width, then freeze |
| `firstvisit` | each frozen box high/low first visit consumes active line; pending break can confirm within 5 minutes, then expires without rearm |
| `entry` | first complete 1m close2 ticks outside after formation |
| `stop` | opposite frozen box edge+2 ticks |
| `target` | 1.5R0 baseline; fresh draw alternative |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `minimum_bars` | 5 | [5, 8, 12] | complete 1m bars — contiguous timestamps |
| `width_fraction` | 0.15 | [0.1, 0.15, 0.2] | J69width — max allowed formation high-low span in baseline |
| `width_measure` | full_range | ["full_range", "close_range"] | enum — close_range additionally requires full span<=0.40J69width; bounds always actual H/L |
| `target_mode` | fixed_1.5R | ["fixed_1.5R", "fresh_reference"] | enum — fresh ASIA/GB_LONDON/PRIOR_RTH extreme ahead; no fallback |

**Algorithm**

1. Scan rolling windows chronologically until the first qualifies. Width>=4 ticks and complete J69scale are required. Freeze actual H/L and formation end.
2. While waiting for break, do not expand bounds for outside wicks. Every first edge visit starts only one pending break episode; if no close break within 5 minutes that side is consumed and cannot rearm. A new box can be formed only after the old box terminal state and from later bars.
3. At first qualifying completed break confirm direction and freeze opposite edge stop and selected target. Simultaneous unordered breaks are ambiguous, not chosen by future Pnl.
4. Execute E11 and retain all boxes/trades in time order. Never overwrite earlier entries with the last qualifying day run.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `box_id` | string |
| `formed_at` | UTC ns |
| `box_bounds` | points[2] |
| `first_visit_times` | UTC ns?[2] |
| `break_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- full range vs close-range contraction
- 5/8/12 bar formation
- fixed target vs fresh draw

**Acceptance cases**

- A box known 11:59 cannot be projected as available 09:40.
- Five rows across missing minutes fail contiguity.
- Wick past upper edge with close inside cannot widen upper bound to avoid the visit.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S05 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `534ef3f148f5cf2a73cde053f8fc3fb2f8a7321154edc7a8d0c6da78d73d8b50`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s06"></a>
## R-S06 — Two independent reasons at a reaction band

Combine a previously confirmed reaction band with an independently formed minor node, then test a real new contact and local defense.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E06, E11.

| Binding | Exact policy |
|---|---|
| `reason1` | earlier current RTH E02 rejection at prior VA edge; band from observed reaction extreme to tested edge, known at reaction confirmation |
| `reason2` | E03 minor HVN in previous completed RTH profile, independent of current reaction formation |
| `entry_window` | 09:30–15:00 |
| `direction` | same as earlier defender |
| `stop` | current contact adverse extreme+2 ticks |
| `target` | selected fixed R0multiple |
| `exit_horizon` | min(fill+60 minutes, RTH close) |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `required_reasons` | 2 | [1, 2] | objects — 1uses reaction band only;2adds qualified minor HVN |
| `node_distance_fraction` | 0.05 | [0.025, 0.05, 0.1] | prior VA width — minimum distance between actual bands |
| `target_R` | 1.5 | [1.0, 1.5, 2.0] | R0 — explicit research targets; source9.60graphic is not default |
| `absorption_gate` | true | [false, true] | bool — E06 opposing aggression at the new contact |

**Algorithm**

1. Record an actual earlier reaction and freeze its band; never derive it from previous high-to-final current close.
2. Select nearest real minor HVN from known prior profile within chosen distance. A dominant POC cannot be silently renamed minor, and this rule is not a global POC ban.
3. After E02 distinct departure/return require matching local defense when enabled, then E02 reaction in defender direction. All target/stop parameters are known before entry.
4. Enter E11 with selected R target and compare one-vs-two-reason parent contacts. Different object origins do not assert statistical independence; measure incremental benefit.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `reaction_band_id` | string |
| `minor_node_id` | string? |
| `reason_count` | int |
| `new_touch_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- one reason vs both
- 1R/1.5R/2R targets
- absorption ablation

**Acceptance cases**

- A node50 points below the whole AM price path does not establish actual contact.
- Risk20 ticks, target30 ticks is1.5R;20/20 is1R.
- Two labels for the same object do not count two independent reasons.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S06 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `2bc55baf13838f8f92706230ef7f84e15f3c6dff9c33555daef0dc648587c8fd`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s07"></a>
## R-S07 — Reaction-area entries, structural risk and intraband re-entry

Use local defended structure for each attempt’s stop while preserving a broader area’s separate validity and renewed intraband re-entry.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E06, E07, E09, E11.

| Binding | Exact policy |
|---|---|
| `broad_area` | prior profile ledge or previously confirmed E07 passive catalyst band, available before contact |
| `defense` | local E06 absorption; direction from actual defender |
| `entry_window` | 09:30–15:00 |
| `entry` | complete 1m closeout of local defense band in defender direction |
| `stop` | E07 CONTROL_STOP beyond specific local pivot/episode extreme |
| `target` | nearest fresh prior RTH extreme ahead; fixed 1.5R alternative |
| `exit_horizon` | 16:00 |
| `reentry` | after prior filled exit, at least 60 seconds and new nonoverlapping full flow window inside same still-valid broad area; no departure outside broad area required |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `stop_buffer_ticks` | 2 | [1, 2, 4] | ticks — outward from local control |
| `area_invalidation_minutes` | 5 | [3, 5, 15] | subsequent complete 1m closes — beyond broad area adverse edge+2 ticks |
| `maximum_attempts` | 3 | [1, 2, 3] | filled attempts per broad area — also respect E11 session cap3 |
| `target_mode` | fresh_extreme | ["fresh_extreme", "fixed_1.5R"] | enum — no implicit fallback |

**Algorithm**

1. Freeze broad area and state; on local defense freeze actual signed print band and local control stop, which may lie inside broad area.
2. Enter only after defense availability and complete close confirmation. Do not choose side from the eventual no on close.
3. An attempts top-out closes only that attempt. Broad area ends after selected accepted break. A new attempt requires new post-exit flow evidence and 60 second separation, even if price remained inside broad area; reuse ofthe same prints is forbidden.
4. Execute E11 for each independent attempt, retaining original risk and post fill MFE/MAE. Any external H/L target is fresh checked; repeated area memory does not rearm consumed highs/lows.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `broad_area_id` | string |
| `attempt_number` | int |
| `local_defense_band` | points[2] |
| `local_stop` | points |
| `area_valid_until` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- one attempt only
- local control vs full broad area stop sensitivity
- fresh target vs fixed R

**Acceptance cases**

- Local stop inside broadband can be triggered without invalidating the whole area.
- Re-entry cannot reuse prints from before previous stop-out.
- A pre-entry morning low does not count as MAE for a no on long.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S07 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `659a5acf870941a8f64146a73b2404eabcf570168b91e4407690811ccc1079c1`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s08"></a>
## R-S08 — Minor-node continuation, control and buying-pressure flip

Define a minor-node continuation with actual signed five-minute approach delta, plus a separately confirmed buying-pressure flip branch.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E02, E03, E05, E06, E07, E11.

| Binding | Exact policy |
|---|---|
| `profile` | E03 balance_composite_2, fixed before RTH |
| `node` | minor HVN in upper quarter of balance VA; prior 2 distinct same-session rejections known before current test |
| `entry_window` | 09:45–15:00 |
| `short_context` | three preceding complete 5m bars have executed buy-sell delta<0 |
| `short_target` | developing RTH POCsnapshot before entry, or selected last rewarded seller print |
| `long_flip` | complete close above band with local buy aggression then later held retest from above |
| `long_target` | RTH VWAP frozen at entry, must be ahead |
| `stop` | E07 local control+2 ticks |
| `exit_horizon` | 16:00 |
| `target` | short: selected RTH_POC or last_rewarded_seller_print, known and below expected entry; long_flip: RTH VWAP frozen at decision and above expected entry |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `branch` | short_continuation | ["short_continuation", "long_flip"] | enum — separate eligible populations |
| `negative_bars` | 3 | [2, 3, 4] | complete 5m bars — short approach delta strictly negative |
| `prior_rejections` | 2 | [1, 2, 3] | distinct episodes — each E02 short reaction at the same known node |
| `short_target` | RTH_POC | ["RTH_POC", "last_rewarded_seller_print"] | enum — available and below expected entry; no automatic fallback |

**Algorithm**

1. Build real minor-node band and its earlier rejection ledger. Higher-timeframe context band and later local refill band keep their own IDs.
2. For short branch compute actual signed delta over last selected complete 5m bars before touch. Require all negative, then new contact/E02 short reaction with local E06 buy aggression absorbed.
3. For long flip require a completed 1m close2 ticks above band with same-candle buy volume>=prior 60 same-slot q90 and buy share>=0.70; then E02 BREAK_RETEST using3 minute hold and later retouch from above. Ordinary short and flip long are not daily ORs.
4. Freeze target from available snapshot/print before entry and E11 execute. Range-leg POC computed after entry is post-entry context only; later control can create new attempt only with new evidence.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `minor_node_id` | string |
| `prior_rejection_ids` | string[] |
| `approach_deltas` | contracts[] |
| `branch` | enum |
| `target_snapshot_id` | string? |
| `net_R0` | float? |

**Comparisons**

- price-change proxy as diagnostic only
- short without delta filter
- ordinary short vs confirmed long flip

**Acceptance cases**

- Three negative C-O values cannot substitute for executed negative deltas.
- A positive third5m delta fails strict three-negative gate.
- POC first computed after entry cannot validate that entry.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S08 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `5c849a9b2be52fd5c4110be54b1571695098894654088e8d6cb55f6e0a68ecfa`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.

<a id="r-s09"></a>
## R-S09 — Entire A-period above prior value, developing-VA break and defended retest

Require the entire completed A period outside prior value, then a break of a pre-existing developing-value snapshot with same-candle buying and a later defended retest.

**Role:** signal. **Inputs:** D01, D02, D03, D04. **Engines:** E00, E01, E02, E03, E05, E06, E09, E11.

| Binding | Exact policy |
|---|---|
| `A_period` | 09:30–10:00, complete |
| `long_opening_gate` | A.low>prior RTH VAH |
| `short_mirror` | named alternative A.high<prior RTH VAL |
| `entry_window` | 10:00–15:00 |
| `developing_boundary` | last complete RTH profile snapshot before break candle starts |
| `entry_area` | actual same-direction diagonal imbalance row band from break candle, not VAH line alias |
| `stop` | retest extreme+2 ticks |
| `target` | nearest fresh ASIA/GB_LONDON/PRIOR_RTH extreme ahead; fixed 1.5R alternative |
| `exit_horizon` | 16:00 |

| Parameter | Default | Allowed grid | Units / definition |
|---|---|---|---|
| `direction_scope` | long_only | ["long_only", "both"] | enum — short mirror research variant |
| `break_candle_minutes` | 1 | [1, 3, 5] | minutes — complete fixed candles after 10:00 |
| `imbalance_ratio` | 3.0 | [3.0, 4.0, 5.0] | diagonal ratio — E05 min cell 10,>=3 consecutive same-side rows, zero opposition excluded |
| `target_mode` | fresh_reference | ["fresh_reference", "fixed_1.5R"] | enum — separate policy, no fallback |

**Algorithm**

1. At 10:00 evaluate whole A-range strict outside prior value; open alone cannot qualify. Prior profile is frozen and separate from developing RTH profile.
2. For each later break candle freeze already available developing VA boundary before bar start. Require complete close2 ticks beyond it in trade direction and qualifying E05 same-candle imbalance stack.
3. Freeze actual stack row band at candle close, require after formation departure>=4 ticks then first later return from breakout side within 30 minutes. Confirm E06 opposing aggression absorption and E02 reaction.
4. Select fresh objective or registered fixed target at final confirmation, stop from retest prefix and execute E11. Report 10–11,11–12 and PM cohorts separately; source aggregate accounts are not recipe performance.

**Model-specific outputs**

| Field | Type / unit |
|---|---|
| `A_gate` | bool? |
| `prior_profile_id` | string |
| `developing_snapshot_id` | string |
| `imbalance_band_id` | string? |
| `retest_at` | UTC ns? |
| `net_R0` | float? |

**Comparisons**

- A opening gate with outflow
- whole A outside vs open only diagnostic
- imbalance ratio and target alternatives

**Acceptance cases**

- Open above prior VAH but A low below it fails.
- Today future VAH cannot serve as prior value.
- A later retouch of VAH alone cannot replace actual imbalance row band defense.

**Missing input:** E00 typed states; any required unavailable input prevents a signal; complete eligible windows with no event emit no_event; interrupted outcomes are censored. All shared prefix, mirror, lifetime and fill tests also apply.

**Audit provenance:** [R-S09 source/old-code record](../../../implementation/reports/phase1-live/chart-audit/audit_records_sires.json); record SHA-256 `62f6af056beb020164a29970bda743cef8f97cae3bc243afdc0fe8e19c4dc054`. Its historical source verdict is preserved; the new assumptions above are the implementation authority.
