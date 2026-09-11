# Phase 1 chart audit

**Audit complete for all 105 Section B IDs.**

This report audits the retained Phase 1 implementation against the supplied sources. It contains no Phase 2 work and makes no production recipe changes. Repair instructions at the bottom are specifications, not implemented fixes. Source conflicts stop faithful certification of the affected ID.

The four verdicts have different meanings: `source_ok` checks whether FORMULAS describes the source; `code_ok` checks construction and timing; `score_event_ok` checks the event and denominator; `chart_ok` checks the plotted implementation against the source geometry and sequence. `cannot-tell` preserves unpublished or ambiguous source details; `gap` and `blocked` preserve missing inputs. A retained positive is never treated as proof that the source recipe should fire.

Audit outcome: 102 IDs have at least one definite mismatch. R-P13 passes all four checks for its exact midnight-open touch statistic; its specification also identifies missing ancillary source tables. R-F02 and R-F07 remain correctly blocked. The other rows preserve any additional blocked or unavailable inputs in their individual verdicts.

All chart clocks are New York time unless an artifact explicitly states otherwise. Bar timestamps are starts; a one-minute close is known one minute later. Native contracts, cash indices and ETFs retain their own price coordinates. A historical screenshot date is distinguished from its posting date.

Source coverage: 39 PDFs / 580 pages; 330 distinct extracted figures inspected (328 in four overlapping native crops each, plus two decorative logos at native resolution), with vector material separately reviewed; 83 archive files plus the separate MVFL and OSF sources; six prose/source exports. Detailed figure notes preserve literal labels, profile scopes, manual annotations, positions, orders, timestamps and unresolved pixels. GB “HIS CHART” images could not be retrieved; that visual comparison remains unavailable.

Dated evidence: 227 price/geometry charts plus 16 native-product supplements, each manually inspected. Every ID has at least two dated charts. These distinguish source positives, named-default positives, prerequisite-only cases, negatives and unavailable source events. A further chronological scan of 642 eligible sessions with complete RTH bars found later A07/A08/A09 sequences, an A10 no-through-open positive and true P02/P06/P19 event negatives. It found no J03 positive under the specific existing extended/single-path and 15-minute EQ-hold conditions. Missing author definitions or unbuilt source inputs remain explicit limitations; the audit does not certify their proxy-positive charts. See [additional sequence evidence](</workspace/implementation/reports/phase1-live/chart-audit/additional_sequence_candidates.json>).

The source label distinction is material: `pRTHVAH/VAL` is prior RTH value, while `pdVAH/VAL` is prior full ETH value. Current/developing VP, prior price extremes, range EQ, range open and RTH open are separate objects. The June 8 shelf rectangle is a manual profile annotation; the 302-lot bubble is a print, and neither alone constitutes a computed absorption signal.

Evidence inventories: [audited inputs and hashes](</workspace/implementation/reports/phase1-live/chart-audit/audit_input_manifest.json>); [source figure reviews](</workspace/implementation/reports/phase1-live/chart-audit/figure_crop_manifest.json>); [literal label ledger](</workspace/implementation/reports/phase1-live/chart-audit/source_label_ledger.json>); [Pine review](</workspace/implementation/reports/phase1-live/chart-audit/pine_source_review.json>); [Pine source copies](</workspace/implementation/reports/phase1-live/chart-audit/pine_copy_manifest.json>); [prose review](</workspace/implementation/reports/phase1-live/chart-audit/prose_source_review.json>); [source pages](</workspace/implementation/reports/phase1-live/chart-audit/page_scan_coverage.json>); [vector review](</workspace/implementation/reports/phase1-live/chart-audit/vector_review_manifest.json>); [completion checks](</workspace/implementation/reports/phase1-live/chart-audit/completion_check.json>); [delivery hashes](</workspace/implementation/reports/phase1-live/chart-audit/delivery_manifest.json>).

Verification: 598 existing fixture checks passed, but several fixtures test helpers that the producer does not call, and at least one forces its pass flag. Strict replay compares the union of stored and fresh keys: 638 recipe rows lack the newer A02/A06/A18 fields, and 658 level rows lack four newer P16 bounds. All 668 failure rows match. Fresh assembly changes A02 on 371 dates, A06 on 311 and A18 on 386, out of all 668 rows (not the eligible-session denominator). Tape replay on 33 selected dates changes OFM on 22 and squeeze on 26, on 27 distinct dates. Missing s04_rev in the direct helper replay is wrapper metadata, not a demonstrated event change. The intentional S08 recipe override is also not a stale-tape disagreement. Chart headers retain the original scorer result; fresh disagreements are identified in the case notes. See [strict replay differences](</workspace/implementation/reports/phase1-live/chart-audit/producer_replay_strict_disagreements.json>), [assembly differences](</workspace/implementation/reports/phase1-live/chart-audit/assembly_predicate_disagreements.json>) and [fixture results](</workspace/implementation/reports/phase1-live/chart-audit/fixture_snapshot.json>).

The PHASE table below counts audited IDs, not trading sessions. `faithful_disagreements` counts IDs with a definite `no` in at least one verdict; it is not a recalculated trading-rate difference. The audit table records semantic leakage even when the retained structural leakage flag is zero.

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---:|---:|---|---|
| Jumbo | source + chart audit | 25 | 25 | fail | [CHART_AUDIT.md](</workspace/planning/phase-1-live/CHART_AUDIT.md>) |
| Greenbird | source + chart audit | 11 | 11 | fail | [CHART_AUDIT.md](</workspace/planning/phase-1-live/CHART_AUDIT.md>) |
| Auction / VP / TPO | source + chart audit | 18 | 18 | fail | [CHART_AUDIT.md](</workspace/planning/phase-1-live/CHART_AUDIT.md>) |
| Discretionary order flow | source + chart audit | 18 | 16 | fail | [CHART_AUDIT.md](</workspace/planning/phase-1-live/CHART_AUDIT.md>) |
| Native options / regime | source + chart audit | 4 | 4 | fail | [CHART_AUDIT.md](</workspace/planning/phase-1-live/CHART_AUDIT.md>) |
| Sires | source + chart audit | 9 | 9 | fail | [CHART_AUDIT.md](</workspace/planning/phase-1-live/CHART_AUDIT.md>) |
| Pine | source + chart audit | 20 | 19 | fail | [CHART_AUDIT.md](</workspace/planning/phase-1-live/CHART_AUDIT.md>) |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|
| Jumbo | R-J01 | fail | existing suite passes; semantic coverage insufficient | future AM extreme selects level and side | yes | July 10's retained positive is selected with knowledge of the deepest level reached over the full AM. A shallower early reversal and a later 0.5 touch are collapsed into one flag; the source reversal example violates the documented invalidation rule. |
| Jumbo | R-J02 | fail | existing suite passes; semantic coverage insufficient | side selection must be frozen at the opening event | yes | The field named open_to_m05_before_0940 ORs 0.1/0.2/0.3 and 0.5 reaches. July 10 is positive because a shallow upper projection is reached early; upper 0.5 is reached only around09:49. January 28, 2026 supplies an actual early lower-0.5 example. |
| Jumbo | R-J03 | fail | existing suite passes; semantic coverage insufficient | full-AM path class in morning eligibility | yes | The retained rate is zero. The hold call tests strict beyond-EQ closes from an EQ touch, so equality can reject the very retrace being sought. A full-AM single-side outcome is also used as if it were a known morning gate. An additional read-only scan of642 complete eligible RTH sessions found no positive under the existing extended/single-path selection, EQ touch before10:00 and15-minute side-hold check. This is a search result for those named defaults, not evidence that the author setup never occurs. |
| Jumbo | R-J04 | fail | existing suite passes; semantic coverage insufficient | outcome path used as setup category | yes | The producer substitutes containment of Asia/London extrema by the completed6–9 box for a timestamped sweep history. It omits the post-break hold/continuation sequence. November25 reaches lower1.0; July10 leaves upper overnight references unpurged. |
| Jumbo | R-J05 | fail | existing suite passes; semantic coverage insufficient | final AM class and early availability of completed OR must be corrected | yes | The score reduces the family to a full-AM single-side path plus a midpoint-retrace flag. It does not require the A-period condition, confirmation, OP/OR variants or a target reached after confirmation. |
| Jumbo | R-J06 | fail | existing suite passes; semantic coverage insufficient | five-minute RVOL and final path labelled as opening context | yes | The headline is a conjunction of outside_both, RVOL and a final double break, not the requested path distribution by opening cell. The09:30–09:35 RVOL is unavailable at09:30, and one prior-VA pair cannot represent all the source's profile scopes. |
| Jumbo | R-J07 | fail | existing suite passes; semantic coverage insufficient | none for final outcome if clearly labelled; no predictive use of final class | yes | The charted H/L/EQ and width are coherent, but the reported event is just whether the final AM class is both. It does not reproduce the required width-bin and balance-conditioned table. |
| Jumbo | R-J08 | fail | existing suite passes; semantic coverage insufficient | full-window aggregate gate; chronology must be explicit | yes | The code gates on a broad band reach and then runs a single-line G rejection at1.33, also ORing an independent line flag. It does not track entry into the band, the deepest excursion or failure beyond the far boundary. |
| Jumbo | R-J09 | fail | existing suite passes; semantic coverage insufficient | 03:00 information is unavailable to source02:00 projections | yes | The implemented00–03 box includes an extra hour of price and changes H/L, EQ, width and every projection. Code-positive London examples therefore cannot certify the authored model. |
| Jumbo | R-J10 | fail | existing suite passes; semantic coverage insufficient | future path/direction and pre-entry target visits | yes | The producer chooses direction from the final path, treats09:30 as the fire time and does not apply the existing untouched-candidate logic. Whole-AM target reach can precede the supposed reversal entry. |
| Jumbo | R-J11 | fail | existing suite passes; semantic coverage insufficient | verify each boundary's own construction cutoff | yes | The retained approximation draws a09:00 anchor and mean excursion boundaries. It omits the complete source band geometry and labels the resulting reach as source-faithful. A code reach alone cannot validate the proprietary map. |
| Jumbo | R-J12 | fail | existing suite passes; semantic coverage insufficient | unordered compound flags and source availability | yes | The only retained positive combines an approximated T1 reach, Model A and a separate m05 rejection with no common event sequence. Its source inequality is wrong, and its percentile boundaries are not validated author zones. |
| Jumbo | R-J13 | fail | existing suite passes; semantic coverage insufficient | open/anchor availability must be explicit | yes | The producer uses09:30 open plus/minus prior60-session mean excursions, while the scorer additionally requires in_value. This is a named approximation with an extra gate; its touches are not evidence of exact authored EV levels or confirmation. |
| Jumbo | R-J14 | fail | existing suite passes; semantic coverage insufficient | candle known only at its close; baseline reset is a coverage defect | yes | The3m SMA resets at09:30, so the first14-bar baseline is only available at10:12, excluding the central09:40–09:50 confirmation window. The score counts a candle-at-level without the requested subsequent response. |
| Jumbo | R-J15 | fail | existing suite passes; semantic coverage insufficient | London trades compared with future6–9 geometry | yes | The London02–05 branch compares its trades with future06–09 m05 levels; AM and London thresholds are pooled into one flag. The predicate needs no matched response/confirmation and omits the developing profile context. |
| Jumbo | R-J16 | fail | existing suite passes; semantic coverage insufficient | full-RTH profile/baselines back-applied to AM | yes | The implementation aggregates the entire09:30–16:00 profile, compares buy/sell near EQ with full-RTH medians and supplies a hardcoded two-tick excursion. It does not compute the stated touch-window response or taper. |
| Jumbo | R-J17 | fail | existing suite passes; semantic coverage insufficient | source requires developing RTH cutoff; existing clock is different | yes | The code's node detector drops zero bins, identifies unsmoothed local extrema and treats symmetric proximity as 'under'. Its6–9 profile cannot contain nodes at its own external m05 projections. The source shelf is not a universal computed rectangle. |
| Jumbo | R-J18 | fail | existing suite passes; semantic coverage insufficient | confirmation and fill must use completed candles | yes | The3m m05 OB branch has the correct full-C2 geometry, but the family omits2m/5m, other source locations, the rejection block and stop/entry variants. The source stop contradiction must be resolved without changing the OB into a wick-only box. |
| Jumbo | R-J19 | fail | existing suite passes; semantic coverage insufficient | future path selects direction; target chronology omitted | yes | Direction can be selected from a final-AM path and reach is reduced to AM extrema against a price. A level already below the open can satisfy a one-sided comparison without a later actual touch. The HTF target family is missing. |
| Jumbo | R-J20 | fail | existing suite passes; semantic coverage insufficient | release vintage and touch-versus-confirmation timing require separation | yes | The retained39/217 positives measure release-day membership and first m05-touch bin. August25 touches after10:00 and continues down; this is not a demonstrated delayed reversal. |
| Jumbo | R-J21 | fail | existing suite passes; semantic coverage insufficient | final path cannot define a pre-open class | yes | The producer passes red_folder=False and scores only the extended-width class. It does not implement the other condition populations, their available-at timing or the class-specific target/knockout/re-entry outcomes. |
| Jumbo | R-J22 | fail | existing suite passes; semantic coverage insufficient | future path/deepest level; same-bar order ambiguity | yes | The scorer uses only three near-m05 one-minute bars with small same-bar returns, selected using the final path side. Other failure functions exist but are not part of the predicate. |
| Jumbo | R-J23 | fail | existing suite passes; semantic coverage insufficient | per-clock known_at and outcome horizon must govern every flag | yes | The retained recipe rate represents only the midnight box's double-break share. The other clocks have actual geometry but their separate path/ladder/response observations are not represented by that headline. |
| Jumbo | R-J24 | fail | existing suite passes; semantic coverage insufficient | pre-entry extrema and final direction used in entry outcome | yes | The645/647 rate counts positive MFE from an assumed m05 price using extrema that can precede any touch/entry. It omits the requested multiple horizons, target chronology and valid risk denominator. |
| Jumbo | R-J25 | fail | existing suite passes; semantic coverage insufficient | future pivots and full-AM trend classification | yes | The producer scans1m data, pairs the first high and first low independently, ignores their confirmation order and back-applies the midpoint over the AM. Its hold flag is not the documented G rejection; the zero rate does not validate the observation. |
| Greenbird | R-G01 | fail | helper checks pass; producer uses a different depth / grouping engine | confirmation timing / coverage | yes | Actual NYAM geometry is correctly separated from Jumbo. However family_fail uses any strict beyond-edge wick instead of the documented two-tick depth, groups five observed rows rather than verified clock bars, and checks five-minute block starts against the deadline. It stores no matched stop/target episode. |
| Greenbird | R-G02 | fail | existing suite passes; semantic coverage insufficient | confirmation timing / coverage | yes | The code draws its own four-hour Asia box, but inherits the zero-depth/grouped-row fail-back defects. Its Asia-failure flag is not linked to the later TDO five-minute close or opposite-edge outcome. |
| Greenbird | R-G03 | fail | old14-failure fixture incompatible with seven current boxes | confirmation timing / coverage | yes | The seven clock boxes are present, but the headline is any failure across all seven, not a per-hour failure rate. Box/outcome coverage is not enforced in family_levels, and grid resampling uses the last one-minute start as close time. Old hour_fail_n=14 fixtures no longer describe seven boxes. |
| Greenbird | R-G04 | fail | existing suite passes; semantic coverage insufficient | confirmation timing / coverage | yes | The current implementation improved to a five-minute reclaim over AM, but equality counts as reclaim, there is no hold, and no completed-impulse discount target is tracked. This differs from both the older15-minute description and the full source sequence. |
| Greenbird | R-G05 | fail | existing suite passes; semantic coverage insufficient | confirmation timing / coverage | yes | The producer finds the first price already beyond TDO in AM, calls that a wick, then seeks an opposite close. It does not require a crossing approach, name the swept box edge, or connect the TDO close to that edge. Its first-side selection can miss a later valid TDO reclaim. |
| Greenbird | R-G06 | fail | existing suite passes; semantic coverage insufficient | prior visitation ignored; direction and entry chronology absent | yes | The code computes a real Friday-RTH/Sunday-open interval, but only asks whether AM extrema overlap it. August31 was already visited overnight before the scored AM touch. There is no live unfilled/retired state or entry-to-destination chronology. |
| Greenbird | R-G07 | fail | existing suite passes; semantic coverage insufficient | impulse/bias provenance not recorded | yes | The current algebra mirrors50–61.8% correctly, but anchors it to the09–10 box and infers direction from that hour’s close/open. The recipe scores only gp_touch, despite storing a separate rejection helper. It cannot certify a source impulse or continuation. |
| Greenbird | R-G08 | fail | existing suite passes; semantic coverage insufficient | final overnight close substituted for an earlier causal bias | yes | The code only combines an overnight high/low outside prior RTH with the final09:29 one-minute close back across. It does not identify a causal five-minute reclaim or invalidation, and cannot link that bias to a later pocket/rejection event. |
| Greenbird | R-G09 | fail | existing suite passes; semantic coverage insufficient | event order absent; stack field uses wrong London clock | yes | The current single eligible positive on May20,2024 contains a gap tag before an upward stack break, not the required bearish sequence. Code uses Jumbo London00–03, tests only level proximity plus Monday plus AM gap overlap, and omits sweep/failure/MSS. |
| Greenbird | R-G10 | fail | existing suite passes; semantic coverage insufficient | missing causal pressure side; session outcome must not supply lean | yes | The code adds two booleans: any-side first failure of09–10 and any-side first failure of10–11. July10 counts a low failure and a high failure as two fades. It neither counts repeated entries nor requires one pressure side. |
| Greenbird | R-G11 | fail | aplus_is_sweep_plus_failback is hard-coded pass=True | whole-day OR can grade an earlier unrelated trade | yes | Current aplus_failback correctly matches sweep and failure within each key, then ORs Asia,NYAM and10–11 over the day. That is a day-level presence label, not the grade of an individual trade. It inherits fail-back timing/depth issues and covers only one previous-hour box. |
| Auction / VP / TPO | R-A01 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | The fresh producer calls both edge rejection helpers, but discards inside-balance eligibility and POC reach. The helper evaluates acceptance over the whole AM, and its POC search starts at the window beginning and measures 60 minutes from touch rather than confirmed rejection. July 10 is a valid named fade example; that does not validate the omitted conditions on other days. |
| Auction / VP / TPO | R-A02 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | The retained recipe cache lacks a02_ledge_hold on 638 dates, allowing the old tape print-near-VA flag to supply the score. Fresh assembly differs on 371 of 668 rows. Fresh code calls the break/retest helper on both VA edges, but passes the same entire AM as break and retest windows, allowing a touch before hold confirmation. No source shelf or next node is selected. |
| Auction / VP / TPO | R-A03 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | The current helper handles outside opens only. Its held-inside check enforces one boundary, so price can exit the far side immediately and still pass. Target timing is compared with re-entry, not hold completion, and only the first whole-window target touch is considered. The scorer divides by all eligible days instead of held re-entries. |
| Auction / VP / TPO | R-A04 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | amt_80pct currently tests outside open and the 09:59/10:29 one-minute closes. It never checks the target. July 22 is a direct false success interpretation: both closes are inside, but RTH high 29342.25 does not reach VAH 29361.75. |
| Auction / VP / TPO | R-A05 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | a05_poc_tell counts touching minutes rather than independent visits, infers direction from the first AM close, and accepts held-through OR retest-reject. Near/far targets use the entire window, including prices before the signal. Only the chop flag is scored. |
| Auction / VP / TPO | R-A06 | fail | fixture reaches near VAL despite far-VAH source target | event chronology / feature availability | yes | Retained a06_naked_poc comes from a tape check against today’s final RTH POC, tested for absence overnight; this is retrospective. Fresh assembly changes 311 of 668 rows, but fresh recipe code passes the established balance’s own POC as older_poc. The helper lacks ordered break/tag windows and targets the near boundary. |
| Auction / VP / TPO | R-A07 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | The producer covers both IB edges but passes the entire post-IB window to both break and retest checks. It can count the initial boundary contact as a later retest. June 9 passes despite no return to IB low 29365 after the outside hold completes. Next value, HTF filter and other source boundaries are omitted. A separate January 30, 2026 sequence breaks IB low 25790.75 at 11:55, completes the named hold at 12:26, retests at 12:30 and confirms the half-width rejection at 12:36, beyond the producer’s noon endpoint. |
| Auction / VP / TPO | R-A08 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | Fresh code now evaluates both break sides, contrary to the stale FORMULAS description. Its inside hold still checks only the re-entered edge, and target lookup is whole-window and compared with re-entry rather than confirmation. The scorer reports reacceptance presence without the subsequent opposite-edge outcome. August 19, 2026 supplies a later valid named reacceptance: outside hold known10:19, reentry known11:44, inside hold known12:14 and opposite-edge touch in the12:18 bar. An earlier inside episode is invalidated before target. |
| Auction / VP / TPO | R-A09 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | The helper adds a total 30-minute traversal cap, scans only AM, and the scorer keeps traverse_nohold while ignoring retest_continuation. August 21 has the traversal prerequisite but its helper continuation result is false. August 26, 2026 demonstrates a valid named continuation after a41-minute traverse: first outside close known09:44, opposite outside close known10:25, retest10:25 and half-width rejection known10:28. No uninterrupted30-minute inside hold occurs. |
| Auction / VP / TPO | R-A10 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | The current drive detector uses the 09:30 open but excludes the opening one-minute bar. It does not establish all four opening types or the separate MAMT day-type table. Only drive presence is scored; a completed day label cannot be an opening feature. October 8 opening bar low 25074 is below open 25079.75, so the literal upward-drive condition is false despite the skip-first-minute flag. |
| Auction / VP / TPO | R-A11 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | Fresh producer includes P+high-only and b+low-only, unlike the stale P-only description. It classifies sparse prior HLC3-volume prices rather than trade-volume VA thirds. February 3 is a b continuation case, not P. The single path flag pools a source-specific directional claim into one score. |
| Auction / VP / TPO | R-A12 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | The retained flag is only the 09:30 opening price within two ticks of any detected overnight LVN price. No two-bulge validation, LVN/shelf band, old-POC alignment or post-open respect/disrespect sequence is scored. The available aggression trust gate remains binding. |
| Auction / VP / TPO | R-A13 | fail | existing suite passes; semantic coverage insufficient | no leakage found in fixed overnight-extreme row; unresolved added conditions | no for either-extreme row; full family incomplete | The current onh_or_onl event correctly uses 18:00–09:30 extremes and 09:30–16:00 touches. July 10 touches both; August 31 touches neither. The full ONVA/POC/MPOC and prior-reference conditional tables remain absent from this score. A different NQ rate does not itself contradict the cited ES study. |
| Auction / VP / TPO | R-A14 | fail | a14_tpo helper tests do not validate current _tpo_poor producer or next-session outcomes | event chronology / feature availability | yes | The actual scorer is bool(tpo_poor), not the stale documented OR. family_gap builds today’s full RTH one-point occupancy and calls either one-period extreme poor. Both reviewed days show long one-period tails, and all 647 scores are true. This is neither prior-profile unfinished business nor a next-session fill/revisit/hold result. |
| Auction / VP / TPO | R-A15 | fail | existing suite passes; semantic coverage insufficient | full-day path is an outcome, not an early feature | no for single-side IB row; full family incomplete | The current single-side IB path row is a valid named close-break statistic. January 28 breaks only the low and closes below it; July 10 breaks both and is correctly negative for single-side. The continuation numerator and complete source table are missing. |
| Auction / VP / TPO | R-A16 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | Current code sets ledge=prior VAL and compares it with full-AM scalar VWAP or the same profile’s VAH. It never selects a shelf, tests touch/rejection or computes stacked-versus-lone outcomes. The full-AM VWAP is unavailable before noon. |
| Auction / VP / TPO | R-A17 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | Current code takes today’s final RTH occupied-volume bins, chooses the deepest minimum, then looks for any median-sized bin on the lighter-volume side. Dropping zero bins changes adjacency, and an arbitrary lighter side is not the source balance orientation. No event-level rejection or ledge/shelf comparison is scored. |
| Auction / VP / TPO | R-A18 | fail | existing suite passes; semantic coverage insufficient | event chronology / feature availability | yes | Retained a18_single_reach falls back to AM-high≥prior-VAH. Fresh assembly differs on 386 of 668 rows. Fresh code fabricates a single above/below value, passes tick integers where the helper expects prices, and invokes the same bullish VAL rejection twice. It does not mirror the side, check a real unfilled ledger or score the target. |
| Discretionary order flow | R-F01 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | The ETH running HLC3 geometry is implemented, but f01 ORs its touch-only flag with the final-AM trade-VWAP absorption flag. The latter fixes noon bands retrospectively. Neither branch requires local absorption at the causal ETH band, the open-draw filter, or subsequent median reach. July 10 is a touch positive with f01_vwap_fade=false; August 31 has neither flag. |
| Discretionary order flow | R-F02 | blocked | existing suite passes; semantic coverage insufficient | blocked; future confirmation must remain unavailable | no: gate retained | The retained recipe is correctly blocked by the trade-CVD trust gate. Helpers exist, but the staged source events are not certified by a trusted FINDINGS row. The two diagnostic charts show price and executions only and cannot prove CVD divergence. |
| Discretionary order flow | R-F03 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | Current code compares final AM trade VWAP, overnight trade VWAP and prior VA midpoint. December 3, 2024 gives 21201.74/21202.91/21204.125 and a true spread predicate; July 10 spreads them widely. Neither is the documented anchor set, and neither scores a confirmed touch/rejection. |
| Discretionary order flow | R-F04 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | The helper named candle_stack is called on the entire current RTH profile; an AM min/max overlap is then ORed with the old whole-AM footprint flag. July 10 is true even though the returned RTH zone 30075.50–30077.50 is never reached in AM. No later departure, revisit or hold is established. |
| Discretionary order flow | R-F05 | fail | FORMULAS uses adjacent candles against explicit single-candle source | event order / future aggregates | yes | The producer treats the entire AM as one candle and scores price/delta disagreement only. July 10 O29834.75/C29944.25 with delta−443 is true; January 2 falls with delta−457 and is false. Full-RTH POC is passed to the helper but does not affect the scored disagreement fields; the defect is missing candle/level/flip chronology, not a direct POC dependency of that flag. |
| Discretionary order flow | R-F06 | fail | FORMULAS arithmetic contradicts its stated W69 threshold | event order / future aggregates | yes | The current prior-VA scan uses two-minute aggression summed across all prices, then future 15-minute extrema. On August 21 its first true print is 09:31:59 at29402.50 near VAH29402, with buy4610/sell3892; the incoming path is already descending from above. This does not verify buyer aggression arriving upward into the band. Shelves, old extremes, local delta, speed and exhaustion states are not joined. |
| Discretionary order flow | R-F07 | blocked | existing suite passes; semantic coverage insufficient | blocked; causal quote/trade alignment required | no: gate retained | The retained iceberg recipe remains blocked. Existing BBO reload flags saturate and do not establish the source sequence. Available diagnostic executions on July10/January28 are insufficient to certify an iceberg, and no depth substitute was plotted. |
| Discretionary order flow | R-F08 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | The producer has no absorption event ID: it takes the first AM trade as origin, the first20 trade signs as direction, and the last80 prices as reward window. January28 returns a 547-tick short reward over the morning; July10 fails with an adverse opening-to-noon move. Neither tests three ticks after absorption, local context, second aggression or reward retest. |
| Discretionary order flow | R-F09 | fail | existing suite passes; semantic coverage insufficient | AM-end samples; blocked replenishment remains explicit | yes | Only first20 versus last20 AM size medians are scored. Both dated cases give1/1, and all647 observations are false. This does not establish absence of local thinning or lift-off. Replenishment remains blocked; the available stage helpers are not assembled into a chronological event. |
| Discretionary order flow | R-F10 | fail | known_at occurs before its five-bar quiet prerequisite | event order / future aggregates | yes | The score is last-five AM prints above the final AM low by two ticks, true646/647. July10 compares prices near29943.50 with29675; the only negative March28 finishes at19542, the morning low. There is no swing, local delta, escape, five-bar protection or high-side mirror. |
| Discretionary order flow | R-F11 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | The score pairs full-current-RTH volume POC with an LVN in that same final profile. July23 POC28810 lies next to LVN28810.25; July10 POC30050 is far from the nearest LVNs. No signed-delta extremum, as-of dealing range, touch, wick reaction or repeat count is used. |
| Discretionary order flow | R-F12 | fail | existing suite passes; semantic coverage insufficient | final-AM samples substituted for pre-touch arrival | yes | The score compares median size of the last five AM prints with the first five. Equality1=1 makes July10 aggressive; August28 gives2→1 and false. Neither identifies arrival at an extreme or uses displacement, directional volume, five-minute bins or the15-minute confirmation. |
| Discretionary order flow | R-F13 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | Current code is wired to the high-side helper, but substitutes prior RTH high, maximum AM price as dp.max and the same current-AM high for both AM and PM failures. It passes min(AM closes) as break_close and min(AM lows) as intra_lo; break_close<intra_lo is impossible for valid bars. The pairing result is ignored and the low mirror is absent. |
| Discretionary order flow | R-F14 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | The code takes any same-price3.5× imbalance in the entire current RTH, then ANDs it with an independent Jumbo-level BigTrades flag. March9 is true without a matched candle, price or side. July10 is false because the independent Jumbo flag is false. There is no body/wick classification, matching print or later retest. |
| Discretionary order flow | R-F15 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | The current helper is wired, contrary to stale FORMULAS text, but ofm_entry uses only a comparison of resqueeze_close with fail_wick; it ignores the computed release, failure, refill and tape flags. The caller supplies final-AM extrema, last-eight wick prints and6–9 swings without event order. Retained F15 differs from fresh tape on22/33 replay dates; July10 and source-dateJuly9 are retained true but fresh false with no qualifying catalyst. |
| Discretionary order flow | R-F16 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | The current helper has both mirrors, but the caller supplies6–9 extremes, wick counts from all AM, a whole-AM no-close condition, unordered extrema for departure/return and an absorption-any-side flag. Its leave test can be satisfied by distance from the opposite edge. The target is the opposite6–9 edge rather than the prior rewarded opposite print. Both selected cases are false under the substitute geometry. |
| Discretionary order flow | R-F17 | fail | existing suite passes; semantic coverage insufficient | known_at unrecorded; source hold unmeasured | yes | Current on_touch_refill requires>=100-lot prints in a two-minute,<=2-tick cluster, checks only the first three signs and can include later opposite-side prints in its bounds. It waits until two minutes after cluster start, then departure in the large-print direction and any later return. January23 produces21928.25–21928.75 and a return near11:23; there is no hold/penetration outcome. January10 NQ is not the MNQ source reconstruction. |
| Discretionary order flow | R-F18 | fail | existing suite passes; semantic coverage insufficient | event order / future aggregates | yes | Current code is wired but the helper ignores release_close and catalyst in its trigger logic. It uses last30seconds of AM speed versus a whole-AM threshold, no-close-through over all AM and the independent prior-VA absorption flag. Continuation is computed but not scored. Fresh replay changes26/33 dates, and July10 retained true is fresh false with no catalyst. |
| Native options / regime | R-R01 | fail | existing suite passes; semantic coverage insufficient | snapshot alignment; OI vintage/known_at; missing-as-false | yes | The QQQ producer pools0–14DTE, mismatches09:30 spot with later first-five-minute quotes and uses an assumed call-positive/put-negative sign. Its flip loop calls the initial0→first-nonzero cumulative value a crossing, producing635 onJuly10 and594 onJanuary28, both first populated strikes. Walls are extrema of net signed strike exposure, not separately aggregated call/put gamma. Only short_gamma prevalence is scored;3 of647 eligible sessions have no GEX and enter as false. Native OI supplements preserve each product, including missingJanuary28 NDX/SPX nodes and unparsed NQ option statistics. |
| Native options / regime | R-R02 | fail | existing suite passes; semantic coverage insufficient | prior-close gate causal; added outcomes need explicit cutoffs | partial: narrow membership is honest; full family incomplete | The retained15–18 gate correctly uses the prior session’s VIX close: July10=15.84 is true andJanuary2=14.95 is false. That literal score event is valid. The full binning omits14, and implied/realized range, level response, intraday VIX direction and curve/context comparisons are not implemented by this ID. |
| Native options / regime | R-R03 | fail | existing suite passes; semantic coverage insufficient | future survival assigned; actual cause/time omitted | yes | The caller hard-codes any_close_beyond=false, news=false and default developing_overlap=true. Directional death is therefore a wick across the prior VA edge; neutral theses survive automatically. The helper assigns death at the evaluation time or survival to16:00 instead of the first observed cause. July10 is neutral/true; January2 long/false after a fall throughVAH25634. |
| Native options / regime | R-R04 | fail | existing suite passes; semantic coverage insufficient | absolute cross-product comparison; later/missing sister data | no scored substitute: blocked gate retained | The recipe remains blocked by the FINDINGS trust gate. Existing upstream defects include absolute ES/YM/RTY pivot prices compared with NQ prices, whole-AM rather than same-time extremes, and missing sister data capable of returning true. Own-profile VA/single-print first-fill states are not assembled. The dated normalized-return panels are diagnostics, not IOD/RFZ detections. |
| Sires | R-S01 | fail | existing suite passes; semantic coverage insufficient | either-side event reused; full-AM entry/extrema | yes | The caller reuses one either-side absorption Boolean for long-at-VAL and short-at-VAH, attaches the final AM print as entry, and supplies whole-AM extrema as local print extremes and outcomes. August21 is true after an opening VAH scan even though the accepted long uses VAL. A source band, same-level refill, sequence and prior-extreme objective are absent. |
| Sires | R-S02 | fail | existing suite passes; semantic coverage insufficient | zero substituted defence; unordered same-bar leave/retest | yes | The OHLC caller supplies zero defence volumes. The helper counts extrema within a doubly widened band, may re-arm from the same bar’s opposite extreme, and returns n>=3 without requiring a third-test close-through entry. August21 has six counted VAL tests; the unmeasured defence condition is automatically true. The resistance-long branch exists but carries the misleading third_test_short key. |
| Sires | R-S03 | fail | existing suite passes; semantic coverage insufficient | whole-AM extrema and sell distribution; last-print catalyst | yes | The current code calls r_s03_second_defence, contrary to the stale FORMULAS description of an F09 alias. It uses a last-print-derived catalyst, the minimum close and maximum high of all AM, total AM sells against a per-print q75, and the last eight AM sell sizes. It is short-only, has no first/second defence identity and scores zero of647. |
| Sires | R-S04 | fail | existing suite passes; FORMULAS1.5<=1 pairing is arithmetically false | pooled/future AM events; weekly scope/sign unverified | yes | Retained weekly references exist, but are prior-five-session18:00–16:00 aggregates, not a verified source weekly profile. Unknown aggressor side is treated as sell. The caller counts every AM high above the prior high as a touch, uses whole-AM no-close/minimum, one-price pooled buy/sell ratios and the final microbalance/close. July10 dp_min30250 is untraded in AM; January28 counts148 supposed failures. Zero scores do not validate this construction. |
| Sires | R-S05 | fail | existing suite passes; semantic coverage insufficient | last-run retrospective selection; pre-entry extrema | yes | The current producer does use a price-defined close-run, unlike the stale FORMULAS clock-box claim. It scans all09:40–12:00 runs and keeps the last qualifying box, comparing only the final AM close. July10 has a real named breakout at noon from29914–29941.5; January28 ends inside its final box. Earlier events are overwritten, and HTF reach/stop/trail are not the scored event. |
| Sires | R-S06 | fail | helper suite passes; no integration check for an untouched level | no touch gate; whole-AM final close/extrema | yes | The current recipe has both directions, despite the stale short-only description. It uses a single prior RTH extreme, prior high/low-to-last-close as rejection, the first price-sorted occupied-bin OHLC HVN and whole-AM close/extrema. Neither branch requires price to touch the chosen level. June12 fires a long near28599 while AM stays above29200; July10 also never touches its lower candidates. |
| Sires | R-S07 | fail | existing suite passes; semantic coverage insufficient | pre-entry RTH MAE; arbitrary final-close long entry | yes | The recipe uses the final AM close as an always-long entry, combines a prior-VA edge touch anywhere in AM, and measures MAE from the whole RTH minimum including pre-entry prices. Only survived_15 is scored, with no absorption, held-area geometry, objective or re-entry. July10’s morning plunge is charged against its noon entry even though afternoon price rises. |
| Sires | R-S08 | fail | existing suite passes; semantic coverage insufficient | last-AM price changes as delta; current touches labelled prior | yes | The overriding recipe now calls r_s08_minor_node, not the stale two-HVN presence rule. It substitutes prior RTH high for balance top, a single first sorted OHLC HVN for the band, current-AM high counts for prior rejections, and final three five-minute close−open values for executed delta. No actual touch, same-side control, flip, target or composite behaviour is scored. Both plotted nodes lie below the AM path. |
| Sires | R-S09 | fail | existing suite passes; semantic coverage insufficient | future10:00 VA for open; unordered break/touch | yes | The producer instead compares09:30 open with the future09:30–10:00 OHLC-VP VAH, freezes that line, and requires an unordered post10 close above plus any low below. August11 is true even though A-low29631.75 is far below prior VAH29819.75. July10 fails its open gate; later PM rally is not an above-value opening setup. |
| Pine | R-P01 | fail | existing suite passes; semantic coverage insufficient | same-minute ordering unresolved; insufficient/mixed close history | yes | The producer takes 19 log returns from at most 20 closes, starts with only five closes, and can substitute an RTH close. Both-side touch chooses smaller overshoot instead of distance from the bar open. ext_max is only the touch-bar extension. July10 returns from upper29959.91 to 08:00 open29816.75; January10 lower21232.94 touch does not return to21320.75 by noon. These validate observations of the named implemented variant, not the printed sigma distribution. |
| Pine | R-P02 | fail | existing suite passes; semantic coverage insufficient | same-minute sweep/return order; daily OR discards conditional unit | yes | The current producer scans09:00–16:00 and ORs hour results. The helper only calculates high-side returns, so low_sweep and high_ret_50 does not implement a low return.637/647 is effectively any high-sweep edge return. July10 has a high-sweep return; June16 has clear low-sweep returns, including09:01→09:02, yet scores false. |
| Pine | R-P03 | fail | existing suite passes; semantic coverage insufficient | fabricated pre-completion times; retrospective side; stop ignored | yes | The producer invents break time hour+4minutes and target time hour+20minutes, both before the hour box completes, chooses direction using future extremes and otherwise assumes a low break even when none occurred. The helper ignores invalidation.647/647 midpoint wins is not the source event. January28 hour01 has no break; July10 hour06 has an actual07:00 high break followed07:30 midpoint return. |
| Pine | R-P04 | fail | existing suite passes; semantic coverage insufficient | post-confirmation depth; wrong clock and pooled raid/presence | yes | The current caller uses09:00–10:00, only high raids, and scores raid OR confirmation. The helper uses maximum depth to the cutoff even after the first confirmation. July10 raid of the wrong box around11:25 cannot demonstrate the source09:15 box event, whose deadline is11:15. January28 high-side non-raid ignores a large low-side move. |
| Pine | R-P05 | fail | existing suite passes; semantic coverage insufficient | wrong session clocks; future NY close is outcome, not entry feature | yes | The implementation instead uses London00:00–03:00 and NY09:30–12:00, and ORs the bullish failure into the positive scorer while the bearish helper omits symmetric failure/stay outputs. January28 source London is bearish with level26286.1875 and a valid NY wick/close-back; the code is a bullish failure at26292.0625. The equal true flags represent different events and geometry. |
| Pine | R-P06 | fail | existing suite passes; semantic coverage insufficient | wrong completed ranges; intrabar order conflated; conditional units lost | yes | The caller substitutes Asia20:00–00:00 and London00:00–03:00, returns only whether any London first hit exists, and omits the NY and conditioned tables. The helper chooses both-side ties by overshoot and delays sequential detection to a later bar. July10 source Asia low is first reached02:21; August28 source low is reached03:44, outside the legacy London window, so the retained false is not a source negative. |
| Pine | R-P07 | fail | existing suite passes; semantic coverage insufficient | cohort uses wrong chronology; source security future values | yes | The helper computes an actual midpoint but calls onlyOR5 with an outcome ending at noon, uses C>O and post-OR first extreme, and the scorer retains only midpoint return. Both plotted dates formed the OR low09:30 before high09:33, while the helper calls high first from later action. July10 midpoint29866.875 returns09:39; October8 midpoint25104.5 never returns in RTH. |
| Pine | R-P08 | fail | existing suite passes; semantic coverage insufficient | retrospective class confusion; source boundary-bar quirks | yes | The current scorer is a reduced close-break path class after10:30, without the eight combo keys, midpoint leave/return, percentile extensions or source wick inequalities. January28 IB26301/26205 breaks only low on closes; July10 IB29968.5/29798 later breaks both. Correct box placement does not validate the missing source statistic. |
| Pine | R-P09 | fail | existing suite passes; semantic coverage insufficient | source clock unresolved; pooled conditional probabilities | yes | Unlike the stale CODE paragraph, the producer now uses full09:30–16:00 NY H/L and strict wick breaks correctly for that named window. It then ORs above/below far-side no-break with inside stay, losing the distinct conditional probabilities. January28 opens above priorH26114.25 and never breaks farL25917.25; July10 opens inside and later breaks only the upper edge. |
| Pine | R-P10 | fail | existing suite passes; semantic coverage insufficient | one-sided reach as contact; source opening-state reset | yes | Current pivot lines are correctly placed for the named prior18:00–17:00 Globex inputs, but the producer scores only RTH high>=P, omits the lower price bound and supplies no opening-zone outcomes. July10 P29773.25 is actually contacted10:32; January10 P21313.33 is uncontacted during RTH despite the earlier08:30 move. Most fields described by the source remain unscored. |
| Pine | R-P11 | fail | existing suite passes; semantic coverage insufficient | source lookahead; present gap mislabeled fill/effectiveness | yes | The current producer searches one-minute09:30–10:00 bars and scores whether a gap exists, passing no fill outcome.645/647 is presence, not fill/effectiveness. July10 first BISI29892.75–29893.5 forms on09:33 bar, known09:34, and later fills; August7,2024 has no qualifying1m gap in that window. Neither decides the missing source5m W1/W2 study. |
| Pine | R-P12 | fail | existing suite passes; semantic coverage insufficient | unconfirmed source HTF fields; wrong candle/timeframe and missing confirmation | yes | Current code passes only09:30 and09:31 one-minute candles, tests high sweep/close-back, and never tests low sweep or CISD. Its unscored mid_box uses prior body mid and current O. January2,2026 has a high sweep of25728.75 and a close-back; July10 sweeps prior high29876 but closes above it.133/647 therefore measures this two-minute high-only test. |
| Pine | R-P13 | pass | existing helper pass; dated positive and negative agree; ancillary tables untested | none demonstrated for the headline exact-touch predicate | no | The current tdo_hit helper and tdo_touch_ny scorer correctly implement the stated midnight-open touch, unlike the stale09:30–12:00 CODE paragraph.460/647 is the retained pooled exact-touch count. July10 level29933 is actually touched; August31 level29352.5 stays below every NY bar. The four yes verdicts certify this headline predicate and geometry; the ancillary midpoint/conditional table rows remain missing. |
| Pine | R-P14 | fail | existing suite passes; semantic coverage insufficient | source/formula checkpoint lookahead; unused helper; RTH label replaces ETH conditional state | yes | The actual producer never calls r_p14_hod_checkpoint. It compares09:30–10:00 high with final09:30–16:00 high within one tick, with no four-hour state, ETH day or LOD. The unused helper counts changes of the running maximum rather than all eliminated candles and ignores the actual checkpoint when testing hod_at. January28 RTH H26301 is in by10; July10 final H30077.75 prints about15:03. |
| Pine | R-P15 | fail | existing suite passes; semantic coverage insufficient | invented quantiles; source current-data counters/lookahead and wrong history selection | yes | The producer substitutes prior60 RTH median widths, assumes MFE=.6*width and MAE=.4*width, anchors09:30 and scores only the upper threshold over full RTH. No source session quantiles, SRP ladder or OHLC history is assembled. July10 upper30071.15 is reached around15:03, outside source08–12 NY Morning; January28 upper26423.425 is unhit while the ignored lower threshold26138.55 is crossed. |
| Pine | R-P16 | fail | existing suite passes; semantic coverage insufficient | proxy anchor/vol symbol; source clock difference; distinct close versus path labels | yes | Current code has improved: it uses prior-session VIX and prior18–17 last close with correct log-space a/b bounds. It scores whole18–16NY path inside the outer1.0 bands, not per-zone touch or final-close containment. Prior last print is not verified official settlement and missing Globex data may fall back to RTH.658 retained rows lack the four newest bound keys. July10 fits outer29636.39–30229.04; October8 rises above25326.17 late in RTH. |
| Pine | R-P17 | fail | existing suite passes; semantic coverage insufficient | source profile clock/algorithm conflict; global range bracketing can imply unobserved contact | yes | The scored flag only checks whether full RTH high/low brackets the prior18:00 open; no source OHLC-profile VA outcome is built. family_open’s half-range/half-body weighting and heavier-neighbour VA are different. The standalone r_p17_bar_vol only demonstrates allocation arithmetic and is not wired to a complete profile. July10 actually touches29937.75 around09:50; October8 RTH stays above25059.75. Actual trade VP is plotted solely as available diagnostic. |
| Pine | R-P18 | fail | existing suite passes; semantic coverage insufficient | distinct OHLC proxies; future pivot confirmation risks; trust gate correctly retained | no: scorer remains blocked | The current recipe calls r_p18_ohlc_cvd for the simple-sign series and scans a grid-divergence proxy, but the scorer remains blocked. Another producer, family_flow._ohlc_cvd, allocates volume fractionally by close position and is neither the simple sign nor the literal Confluence method. Both plotted sessions show the actual simple-sign ETH cumulative series and reference prices; there is no permissible positive/negative trade trigger to certify. |
| Pine | R-P19 | fail | existing suite passes; semantic coverage insufficient | first-pair presence replaces per-gap later fill; missing adjacency/denominator | yes | The helper only examines array positions0 and1, and the producer supplies09:30–12:00 but never loops later pairs or passes fill data. Thus25/647 is the first09:30/31 body-gap presence rate. August6 down gap29327–29328.5 forms by09:32 and actually fills on09:34; July10 first pair has no gap, which says nothing about later pairs. Down-gap confluence is hardcoded false. Later-pair inspection of July10 finds an up gap29881.25–29882.25 formed09:32 (known09:33), so the retained daily false is a counterexample. September29,2025 has no qualifying gap in any of389 adjacent RTH pairs; the642-session scan found49 such all-RTH negative dates. |
| Pine | R-P20 | fail | helper suite passes the wrong double-width anomaly; production never calls helper | unrelated tape filter; source backward drawing/loop-order; unresolved aggressor replacement | yes | The actual scorer is AM max print>=100lots AND AM price range>=8ticks:425/647. It never calls r_p20_mvfl and builds none of the source zones or seven votes. July10 max245lots/range1266ticks passes; October8 max92/range748 fails. The unused helper doubles anomaly thickness (±0.2% instead of±0.1%), and its passing fixture expects that wrong width. |

## Required per-ID verdicts

| id | source_ok | code_ok | score_event_ok | chart_ok | evidence | ask_user |
|---|---|---|---|---|---|---|
| R-J01 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J01-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J01-B-2026-01-28.png>); [2025-01-28 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J01-source-date-2025-01-28.png>). July 10's retained positive is selected with knowledge of the deepest level reached over the full AM. A shallower early reversal and a later 0.5 touch are collapsed into one flag; the source reversal example violates the documented invalidation rule. Source: [TBR p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i1.png>); [TBR p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i2.png>); [TBR p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i3.png>); [TBR p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i1.png>); [TBR p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i2.png>); [TBR p.30 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i1.png>); [TBR p.30 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i2.png>); [TBR p.30 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i3.png>); [TBR p.30 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i4.png>); [XF p.47 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p010-i1.jpeg>); [FIND p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p010-i1.jpeg>). The author shows reversal areas on both sides, overshoot and price confirmation. The January 28, 2025 NQH2025 example has a body close below the lower 0.5 projection before the successful rebound. FORMULAS' strict no-close-beyond G-default therefore excludes a cited source example. The 86.46% statement and the time histogram are separate statistics with an unrecovered joint denominator. | no |
| R-J02 | yes | no | no | yes | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J02-A-2026-07-10.png>); [2025-01-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J02-B-2025-01-10.png>); [2026-01-28 stated-positive](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J02-stated-positive-2026-01-28.png>). The field named open_to_m05_before_0940 ORs 0.1/0.2/0.3 and 0.5 reaches. July 10 is positive because a shallow upper projection is reached early; upper 0.5 is reached only around09:49. January 28, 2026 supplies an actual early lower-0.5 example. Source: [TBR p.8](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i1.png>); [TBR p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i2.png>); [TBR p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i3.png>); [TBR p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i1.png>); [TBR p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i2.png>). Trade #1 runs from the 09:30 open toward the projection ladder before the reversal window. The public examples use different depths; FORMULAS explicitly requests separate depth rows and a 0.5-before-09:40 headline. | no |
| R-J03 | yes | no | no | no | [2025-12-29 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J03-A-2025-12-29.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J03-B-2026-07-10.png>). The retained rate is zero. The hold call tests strict beyond-EQ closes from an EQ touch, so equality can reject the very retrace being sought. A full-AM single-side outcome is also used as if it were a known morning gate. An additional read-only scan of642 complete eligible RTH sessions found no positive under the existing extended/single-path selection, EQ touch before10:00 and15-minute side-hold check. This is a search result for those named defaults, not evidence that the author setup never occurs. Source: [TBR p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p012-i1.png>); [TBR p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i1.png>); [TBR p.13 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i2.png>); [TBR p.13 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i3.png>); [TBR p.13 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i4.png>); [TBR p.24](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>). The source uses EQ/quadrants after an extended overnight range and limits expectations to the box edges. Width ratio≥1, the 15-minute hold and formal single-break rule are named research defaults, not authored numerical thresholds. | no |
| R-J04 | yes | no | no | no | [2025-11-25 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J04-A-2025-11-25.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J04-B-2026-07-10.png>). The producer substitutes containment of Asia/London extrema by the completed6–9 box for a timestamped sweep history. It omits the post-break hold/continuation sequence. November25 reaches lower1.0; July10 leaves upper overnight references unpurged. Source: [TBR p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i1.png>); [TBR p.13 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i2.png>); [TBR p.13 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i3.png>); [TBR p.13 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i4.png>); [TBR p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p014-i1.png>); [TBR p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p014-i2.png>); [TBR p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p015-i1.png>); [TBR p.15 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p015-i2.png>). The source treats prior overnight highs/lows already removed as context for a single-break continuation and larger projections. The exact clock and purge tolerance must remain explicitly named where the author does not define them. | no |
| R-J05 | yes | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J05-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J05-B-2026-07-10.png>). The score reduces the family to a full-AM single-side path plus a midpoint-retrace flag. It does not require the A-period condition, confirmation, OP/OR variants or a target reached after confirmation. Source: [XF p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p012-i1.png>); [XF p.12 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p012-i2.png>); [XF p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p015-i1.jpeg>); [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.25 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p025-i1.png>). Newer examples distinguish the6–9 midpoint, its06:00 opening print and a5m/15m opening-range midpoint. The author describes entry areas and subsequent continuation; the strict G rejection is a named formalization. | no |
| R-J06 | yes | no | no | no | [2026-08-27 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J06-A-2026-08-27.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J06-B-2026-07-10.png>). The headline is a conjunction of outside_both, RVOL and a final double break, not the requested path distribution by opening cell. The09:30–09:35 RVOL is unavailable at09:30, and one prior-VA pair cannot represent all the source's profile scopes. Source: [XF p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p007-i1.png>); [XF p.8](</workspace/sources/documents/jumbo/xfcmg2.pdf>); [XF p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p010-i1.png>); [XF p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p010-i2.png>); [XF p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p016-i1.png>); [XF p.18 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p018-i1.jpeg>). The newer panels separately label previous RTH value, previous full-ETH value, previous price range, RTH open and the6–9 box. Outside prior value/price range with elevated RVOL is a conditional context observation; it is not equivalent to outside the6–9 range. | no |
| R-J07 | yes | no | no | yes | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J07-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J07-B-2026-01-28.png>). The charted H/L/EQ and width are coherent, but the reported event is just whether the final AM class is both. It does not reproduce the required width-bin and balance-conditioned table. Source: [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [TBR p.30 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i1.png>); [TBR p.30 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i2.png>); [TBR p.30 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i3.png>); [TBR p.30 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i4.png>). The source tables report all break classes conditional on range size. Printed percentages such as17.8% double break and the midpoint-retrace share have distinct populations; they are not interchangeable win rates. | no |
| R-J08 | yes | no | no | no | [2026-07-24 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J08-A-2026-07-24.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J08-B-2026-07-10.png>); [2025-01-28 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J08-source-date-2025-01-28.png>). The code gates on a broad band reach and then runs a single-line G rejection at1.33, also ORing an independent line flag. It does not track entry into the band, the deepest excursion or failure beyond the far boundary. Source: [TBR p.21 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i1.png>); [TBR p.21 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i2.png>); [TBR p.21 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i3.png>); [TBR p.21 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i4.png>); [XF p.19 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i1.png>); [XF p.19 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i2.jpeg>); [XF p.47 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p010-i1.jpeg>). The author draws a reversal area between1.33 and1.66 widths beyond the appropriate range edge, including PM examples. A band reaction and a rejection of its near line are different events. | no |
| R-J09 | no | no | no | no | [2026-05-26 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J09-A-2026-05-26.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J09-B-2026-07-10.png>); [2025-10-08 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J09-source-date-2025-10-08.png>). The implemented00–03 box includes an extra hour of price and changes H/L, EQ, width and every projection. Code-positive London examples therefore cannot certify the authored model. Source: [XF p.40 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p005-i1.jpeg>); [XF p.40 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p040-i2.jpeg>); [XF p.41 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p041-i1.jpeg>); [XF p.41 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p041-i2.jpeg>); [FIND p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p004-i1.jpeg>); [FIND p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p005-i1.jpeg>). The October6/7/8/13 source charts start their projected levels at02:00. The derived write-up and FORMULAS instead freeze a00:00–03:00 box. The exact author build start is not pinned by the screenshots alone. | yes |
| R-J10 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J10-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J10-B-2026-01-28.png>). The producer chooses direction from the final path, treats09:30 as the fire time and does not apply the existing untouched-candidate logic. Whole-AM target reach can precede the supposed reversal entry. Source: [TBR p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p016-i1.png>); [TBR p.17 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p017-i1.png>); [TBR p.17 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p017-i2.png>); [XF p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p003-i1.png>); [XF p.26 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p026-i1.jpeg>). The source manages a confirmed reversal toward remaining references and may exit at a midpoint rejection. A reference's scope and whether it remains clean at the decision matter; a final-AM nearest price is not an entry-time draw. | no |
| R-J11 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J11-A-2026-07-10.png>); [2026-08-11 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J11-B-2026-08-11.png>); [2026-07-06 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J11-source-date-2026-07-06.png>). The retained approximation draws a09:00 anchor and mean excursion boundaries. It omits the complete source band geometry and labels the resulting reach as source-faithful. A code reach alone cannot validate the proprietary map. Source: [SS p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p004-i1.png>); [SS p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p004-i2.png>); [SS p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p004-i1.png>); [SS p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p006-i1.png>); [SS p.6 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p006-i3.png>); [SS p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p009-i1.png>); [SS p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p009-i2.png>); [SS p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p009-i3.png>); [SS p.10](</workspace/sources/documents/jumbo/SessionStat+.pdf>); [XF p.19 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i1.png>); [XF p.19 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i2.jpeg>); [XF p.45](</workspace/sources/documents/jumbo/xfcmg2.pdf>). Settings show selectable sessions, mean and median levels, minimum-average levels and projections. The charts draw distinct asymmetric mean/median bands. The full author calculation, especially minimum-average, is not published. | no |
| R-J12 | no | no | no | no | [2024-10-18 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J12-A-2024-10-18.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J12-B-2026-07-10.png>); [2026-01-02 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J12-source-date-2026-01-02.png>). The only retained positive combines an approximated T1 reach, Model A and a separate m05 rejection with no common event sequence. Its source inequality is wrong, and its percentile boundaries are not validated author zones. Source: [XF p.29 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p029-i1.jpeg>); [XF p.29 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p029-i2.jpeg>); [XF p.30 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p030-i1.png>); [XF p.39 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p039-i1.jpeg>). The January2,2026 figure and its table describe a retrace from low to open (Low→Open). The visible low is below the range open. FORMULAS converts that path into low>open, an inequality. P-zones additionally use unpublished learning/scaling settings; they are not the same object as fixed percentile excursion envelopes. | no |
| R-J13 | cannot-tell | cannot-tell | no | cannot-tell | [2025-10-08 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J13-A-2025-10-08.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J13-B-2026-07-10.png>). The producer uses09:30 open plus/minus prior60-session mean excursions, while the scorer additionally requires in_value. This is a named approximation with an extra gate; its touches are not evidence of exact authored EV levels or confirmation. Source: [XF p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p003-i1.png>); [XF p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p007-i1.png>); [XF p.19 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i1.png>); [XF p.19 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i2.jpeg>). The source shows an AM EV range, asymmetry and additional EV projections as contextual boundaries. It does not publish the complete estimator. EV+50% is distinct from6–9+0.5W. | no |
| R-J14 | no | no | no | no | [2026-08-25 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J14-A-2026-08-25.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J14-B-2026-07-10.png>). The3m SMA resets at09:30, so the first14-bar baseline is only available at10:12, excluding the central09:40–09:50 confirmation window. The score counts a candle-at-level without the requested subsequent response. Source: [TBR p.31 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p031-i2.png>); [TBR p.31 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p031-i3.png>); [TBR p.31 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p031-i4.png>); [TBR p.35 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i1.png>); [TBR p.35 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i2.png>); [XF p.27 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i1.jpeg>); [XF p.27 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i2.png>); [XF p.44 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p044-i1.jpeg>); [XF p.45](</workspace/sources/documents/jumbo/xfcmg2.pdf>). The native settings panel visibly supplies body threshold0.6, volume multiplier1.5 and14-period volume average; FORMULAS says the first two are unprinted and defaults body ratio to0.3. The source says the candle can signal continuation or reversal and needs location/context. | no |
| R-J15 | yes | no | no | no | [2026-03-09 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J15-A-2026-03-09.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J15-B-2026-07-10.png>). The London02–05 branch compares its trades with future06–09 m05 levels; AM and London thresholds are pooled into one flag. The predicate needs no matched response/confirmation and omits the developing profile context. Source: [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [XF p.27 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i1.jpeg>); [XF p.27 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i2.png>); [XF p.44 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p044-i1.jpeg>); [FIND p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [FIND p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>). The source combines a large print with range location, price response and profile/footprint context. A displayed bubble is an executed trade; manual shelf highlighting is not a trading box, and a large aggressive print alone does not establish passive absorption. | no |
| R-J16 | yes | no | no | no | [2026-08-31 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J16-A-2026-08-31.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J16-B-2026-07-10.png>). The implementation aggregates the entire09:30–16:00 profile, compares buy/sell near EQ with full-RTH medians and supplies a hardcoded two-tick excursion. It does not compute the stated touch-window response or taper. Source: [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [FIND p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [FIND p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>). The June8 panels combine EQ, a profile taper/shelf, negative flow near the low and subsequent price recovery. The RTH profile is developing; the visible final histogram cannot be assumed to have existed at the first low. The35% footprint filter is printed; median and excursion cutoffs are named approximations. | no |
| R-J17 | no | no | no | no | [2025-01-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J17-A-2025-01-10.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J17-B-2026-07-10.png>). The code's node detector drops zero bins, identifies unsmoothed local extrema and treats symmetric proximity as 'under'. Its6–9 profile cannot contain nodes at its own external m05 projections. The source shelf is not a universal computed rectangle. Source: [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [FIND p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>). The cited June8 example uses a developing RTH VP and delta profile with a manually highlighted taper/shelf near6–9 EQ. FORMULAS substitutes a frozen6–9 trade profile. That changes the profile population and cannot reproduce the cited confluence. | no |
| R-J18 | no | no | no | no | [2026-07-21 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J18-A-2026-07-21.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J18-B-2026-07-10.png>). The3m m05 OB branch has the correct full-C2 geometry, but the family omits2m/5m, other source locations, the rejection block and stop/entry variants. The source stop contradiction must be resolved without changing the OB into a wick-only box. Source: [TBR p.27 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p027-i1.png>); [TBR p.27 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p027-i2.png>); [TBR p.28 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p028-i1.png>); [TBR p.28 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p028-i2.png>); [TBR p.29 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p029-i1.png>); [TBR p.29 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p029-i2.png>); [TBR p.29 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p029-i3.png>). The OB is the full second candle's H/L, confirmed by C3 closing beyond C2. The rejection block is the sweep candle's wick. Source pages distinguish midpoint entry, midpoint stop and wick-extreme stop; p29's conservative-stop prose conflicts with the drawn wick-low stop. | yes |
| R-J19 | yes | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J19-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J19-B-2026-07-10.png>). Direction can be selected from a final-AM path and reach is reduced to AM extrema against a price. A level already below the open can satisfy a one-sided comparison without a later actual touch. The HTF target family is missing. Source: [TBR p.33 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p033-i1.png>); [TBR p.33 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p033-i2.png>); [TBR p.33 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p033-i3.png>); [TBR p.34 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p034-i1.png>); [TBR p.34 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p034-i2.png>); [TBR p.35 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i1.png>); [TBR p.35 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i2.png>). The author explicitly uses prior09:30–16:00 price action, preserves those extremes through ETH sweeps and waits for RTH direction. M15/H1 first-presented FVGs are additional draws. The exact directional rule is not published. | no |
| R-J20 | yes | no | no | no | [2026-08-25 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J20-A-2026-08-25.png>); [2026-08-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J20-B-2026-08-28.png>). The retained39/217 positives measure release-day membership and first m05-touch bin. August25 touches after10:00 and continues down; this is not a demonstrated delayed reversal. Source: [TBR p.18 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p018-i1.png>); [FIND p.11](</workspace/sources/documents/jumbo/jjumbo-findings.pdf>). The source describes a later reversal after10:00 news, not simply a later first projection touch. It does not define an exact release universe. FORMULAS' old 'no10:00 calendar' description is stale: the current code consumes release_1000_dates.json. The existing JSON retains release names/IDs but the loader reduces them to a date set. FRED returns dates, not intraday times ([API documentation](https://fred.stlouisfed.org/docs/api/fred/release_dates.html)); its sample Michigan dates match the university's final-release calendar, but the JSON omits preliminary releases such as2024-01-19 and2024-02-16 ([official dates](https://data.sca.isr.umich.edu/fetchdoc.php?docid=75443)). This is incomplete release coverage, not proof that all FRED dates are delayed updates. | no |
| R-J21 | yes | no | no | no | [2025-01-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J21-A-2025-01-10.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J21-B-2026-07-10.png>). The producer passes red_folder=False and scores only the extended-width class. It does not implement the other condition populations, their available-at timing or the class-specific target/knockout/re-entry outcomes. Source: [TBR p.22 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p022-i2.png>); [TBR p.22 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p022-i3.png>); [TBR p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i1.png>); [TBR p.23 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i2.png>); [TBR p.23 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i3.png>); [TBR p.23 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i4.png>); [TBR p.24](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>). The source separates low-expectation news conditions, extended overnight ranges, pre-news range-bound conditions and expansive days. The weekday risk table is visual evidence; the width ratio and coded class boundaries are named research definitions. | no |
| R-J22 | yes | no | no | no | [2026-08-11 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J22-A-2026-08-11.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J22-B-2026-07-10.png>). The scorer uses only three near-m05 one-minute bars with small same-bar returns, selected using the final path side. Other failure functions exist but are not part of the predicate. Source: [TBR p.37](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>). The source enumerates no-rejection, momentum, extended-body, timing, extended-move and volume failures, plus three failed reversal attempts at a level. Three consecutive bars touching a level are not necessarily three attempts. | no |
| R-J23 | yes | no | no | no | [2025-01-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J23-A-2025-01-10.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J23-B-2026-07-10.png>). The retained recipe rate represents only the midnight box's double-break share. The other clocks have actual geometry but their separate path/ladder/response observations are not represented by that headline. Source: [TBR p.6](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.7](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i1.png>); [TBR p.13 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i2.png>); [TBR p.13 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i3.png>); [TBR p.13 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i4.png>). The manual explicitly lists Asia20:00–20:30, midnight00:00–00:30, London03:00–03:30,6–9,09:30–10:00,10:00–10:30,lunch12:00–12:30 and MOC15:00–15:30 construction windows. Outcome horizons and a common formal rejection rule are named research choices. | no |
| R-J24 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J24-A-2026-07-10.png>); [2025-12-03 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J24-B-2025-12-03.png>). The645/647 rate counts positive MFE from an assumed m05 price using extrema that can precede any touch/entry. It omits the requested multiple horizons, target chronology and valid risk denominator. Source: [TBR p.8](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p016-i1.png>); [XF p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p015-i1.jpeg>); [XF p.21 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p021-i1.png>); [XF p.26 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p026-i1.jpeg>). The source discusses entries, partials/adds, midpoint exits and clock context. This Phase1 row is outcome measurement after a confirmed entry, not simulated P&L or a positive-excursion win rate. | no |
| R-J25 | yes | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J25-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J25-B-2026-07-10.png>). The producer scans1m data, pairs the first high and first low independently, ignores their confirmation order and back-applies the midpoint over the AM. Its hold flag is not the documented G rejection; the zero rate does not validate the observation. Source: [XF p.26 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p026-i1.jpeg>). The tweet describes clean swing-mid retraces toward the January4 gap. The2-left/2-right5m fractal and trend definition are explicitly named observations, not an authored entry algorithm. FORMULAS' numeric fixture is internally wrong:105 is not100+0.5×20. | no |
| R-G01 | cannot-tell | no | no | cannot-tell | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G01-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G01-B-2025-10-08.png>). Actual NYAM geometry is correctly separated from Jumbo. However family_fail uses any strict beyond-edge wick instead of the documented two-tick depth, groups five observed rows rather than verified clock bars, and checks five-minute block starts against the deadline. It stores no matched stop/target episode. Source: [GB pack L28](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:28>); [GB pack L209](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:209>); [GB pack L395](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:395>). The pack explicitly fixes09:00–10:00 and entry logic after10:00: sweep, fail back inside, then trade toward the opposite side. Five-minute confirmation is sourced; two ticks and30minutes are named research defaults. The original HIS CHART pixels are unavailable. | yes |
| R-G02 | cannot-tell | no | no | cannot-tell | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G02-A-2026-07-10.png>); [2026-01-02 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G02-B-2026-01-02.png>). The code draws its own four-hour Asia box, but inherits the zero-depth/grouped-row fail-back defects. Its Asia-failure flag is not linked to the later TDO five-minute close or opposite-edge outcome. Source: [GB pack L24](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:24>); [GB pack L35](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:35>); [GB pack L427](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:427>). The pack describes a roughly20:00–00:00 Asia rectangle, AS.L, and post-midnight sweep/failure; TDO is the midnight open. This chart-derived clock remains unverified without the original image. The06:00 outcome cutoff and30-minute expiry are named defaults. | yes |
| R-G03 | cannot-tell | no | no | cannot-tell | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G03-A-2026-07-10.png>); [2025-06-09 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G03-B-2025-06-09.png>). The seven clock boxes are present, but the headline is any failure across all seven, not a per-hour failure rate. Box/outcome coverage is not enforced in family_levels, and grid resampling uses the last one-minute start as close time. Old hour_fail_n=14 fixtures no longer describe seven boxes. Source: [GB pack L32](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:32>); [GB pack L439](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:439>); [GB pack L685](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:685>). The source describes the last completed60-minute box and repeated subsequent sweep/fail entries. The current producer now uses clock hours; FORMULAS still mixes current behavior with old five-minute stepped fixtures and counts. | yes |
| R-G04 | cannot-tell | no | no | cannot-tell | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G04-A-2026-07-10.png>); [2025-01-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G04-B-2025-01-10.png>). The current implementation improved to a five-minute reclaim over AM, but equality counts as reclaim, there is no hold, and no completed-impulse discount target is tracked. This differs from both the older15-minute description and the full source sequence. Source: [GB pack L30](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:30>); [GB pack L88](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:88>); [GB pack L90](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:90>). The pack states a sweep below the09:30 open, reclaim and hold, then a retracement target with a stop at the lows. It does not give a universal hold duration or a fifteen-minute cap; the above-open short is a named side variant. | yes |
| R-G05 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G05-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G05-B-2026-01-28.png>). The producer finds the first price already beyond TDO in AM, calls that a wick, then seeks an opposite close. It does not require a crossing approach, name the swept box edge, or connect the TDO close to that edge. Its first-side selection can miss a later valid TDO reclaim. Source: [GB pack L24](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:24>); [GB pack L142](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:142>); [GB pack L612](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:612>). The source confirmation is a five-minute close through midnight open after sweeping a different named reference, such as Asia high. A standalone TDO wick/cross and the Pine73.75% touch statistic are distinct events. | yes |
| R-G06 | cannot-tell | no | no | no | [2026-08-31 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G06-A-2026-08-31.png>); [2026-08-24 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G06-B-2026-08-24.png>). The code computes a real Friday-RTH/Sunday-open interval, but only asks whether AM extrema overlap it. August31 was already visited overnight before the scored AM touch. There is no live unfilled/retired state or entry-to-destination chronology. Source: [GB pack L59](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:59>); [GB pack L68](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:68>); [GB pack L615](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:615>); [GB pack L673](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:673>). The source says Sunday18:00 versus Friday close, an unfilled weekly gap, and exit when the gap is tagged. The pack does not publish the exact Friday closing minute. FORMULAS names16:59 while the code uses15:59; these are separate endpoints. A definition that counts the formation opening print itself as a prior fill would also make every gap immediately filled. | yes |
| R-G07 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G07-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G07-B-2025-10-08.png>). The current algebra mirrors50–61.8% correctly, but anchors it to the09–10 box and infers direction from that hour’s close/open. The recipe scores only gp_touch, despite storing a separate rejection helper. It cannot certify a source impulse or continuation. Source: [GB pack L73](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:73>); [GB pack L79](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:79>); [GB pack L258](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:258>); [GB pack L537](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:537>). The source measures50–61.8% from a completed impulse end and uses the area as location for a rejection or a level sweep/failure. The accessible author-authored [September1 thread](https://threadreaderapp.com/thread/2094830361758843015.html) also describes a pocket retracement with a PDL sweep/failure; its chart media remains unavailable. | yes |
| R-G08 | cannot-tell | no | no | cannot-tell | [2025-01-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G08-A-2025-01-10.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G08-B-2026-07-10.png>). The code only combines an overnight high/low outside prior RTH with the final09:29 one-minute close back across. It does not identify a causal five-minute reclaim or invalidation, and cannot link that bias to a later pocket/rejection event. Source: [GB pack L313](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:313>); [GB pack L443](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:443>); [GB pack L543](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:543>). The pack describes PDL sweep/reclaim overnight setting a long bias and subsequent NYAM pullbacks. FORMULAS adds a five-minute hold-to09:30 convention; its exact hold rule is a named interpretation rather than a published numerical default. | yes |
| R-G09 | cannot-tell | no | no | no | [2024-05-20 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G09-A-2024-05-20.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G09-B-2026-07-10.png>). The current single eligible positive on May20,2024 contains a gap tag before an upward stack break, not the required bearish sequence. Code uses Jumbo London00–03, tests only level proximity plus Monday plus AM gap overlap, and omits sweep/failure/MSS. Source: [GB pack L156](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:156>); [GB pack L615](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:615>). The source sequence is PDH+Asia high+London high sweep, failure below, bearish structure shift and then the gap target. The London02–05 clock,0.05W proximity and numerical swing/MSS convention are named interpretations. A low-side mirror is not shown by the cited example. | yes |
| R-G10 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G10-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G10-B-2025-10-08.png>). The code adds two booleans: any-side first failure of09–10 and any-side first failure of10–11. July10 counts a low failure and a high failure as two fades. It neither counts repeated entries nor requires one pressure side. Source: [GB pack L669](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:669>). The cited chart is repeated shorts from failed highs on a grind day, with red entry arrows and blue covers. The source does not publish a universal numerical pressure/lean classifier; bidirectional chop is a different observation. | yes |
| R-G11 | cannot-tell | no | no | cannot-tell | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G11-A-2026-07-10.png>); [2026-08-25 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G11-B-2026-08-25.png>). Current aplus_failback correctly matches sweep and failure within each key, then ORs Asia,NYAM and10–11 over the day. That is a day-level presence label, not the grade of an individual trade. It inherits fail-back timing/depth issues and covers only one previous-hour box. Source: [GB pack L93](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:93>); [GB pack L147](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:147>); [GB pack L242](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:242>). The grading description requires a sweep of the relevant traded range plus failure back inside. Sweep-only is explicitly weaker. The current formula correctly names this distinction, but the original graded chart cannot be inspected. | yes |
| R-A01 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A01-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A01-B-2026-01-28.png>). The fresh producer calls both edge rejection helpers, but discards inside-balance eligibility and POC reach. The helper evaluates acceptance over the whole AM, and its POC search starts at the window beginning and measures 60 minutes from touch rather than confirmed rejection. July 10 is a valid named fade example; that does not validate the omitted conditions on other days. Source: [AMT1 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p005-i1.png>); [AMT1 p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i1.png>); [AMT1 p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i2.png>); [MAMT p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p005-i1.jpeg>); [MAMT p.9](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [ABS p.7](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>). The balance drawings show both edge bands and rotations toward POC. Fixed prior value is an explicit research construction; the source does not publish the G-default distances or band thickness. MAMT p.5 says most excursions return, while p.9 calls the general return about one in five: that statistical claim has an internal denominator/direction conflict. | no |
| R-A02 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A02-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A02-B-2026-01-28.png>). The retained recipe cache lacks a02_ledge_hold on 638 dates, allowing the old tape print-near-VA flag to supply the score. Fresh assembly differs on 371 of 668 rows. Fresh code calls the break/retest helper on both VA edges, but passes the same entire AM as break and retest windows, allowing a touch before hold confirmation. No source shelf or next node is selected. Source: [AMT1 p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i1.png>); [AMT1 p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i2.png>); [VP2 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p004-i1.png>); [VP2 p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p004-i2.png>); [VP2 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p005-i1.png>); [VP2 p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p005-i2.png>); [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>). A ledge is the edge of a volume shelf. The figures show multiple fixed ledges around POC; they do not define a universal median-volume threshold. Prior VA boundaries alone are a different named level set. | no |
| R-A03 | yes | no | no | no | [2026-01-02 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A03-A-2026-01-02.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A03-B-2026-07-10.png>); [2026-02-12 documented-hold-positive](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A03-documented-hold-positive-2026-02-12.png>). The current helper handles outside opens only. Its held-inside check enforces one boundary, so price can exit the far side immediately and still pass. Target timing is compared with re-entry, not hold completion, and only the first whole-window target touch is considered. The scorer divides by all eligible days instead of held re-entries. Source: [AMT1 p.7 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-amt-lesson-1-p007.png>); [LIVE p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-on-live-markets-p008-i1.jpeg>); [LIVE p.9](</workspace/sources/documents/discretionary/amt-on-live-markets.pdf>); [ABS p.12](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>). The loose 80% statement conditions the traverse on re-entry and acceptance inside prior value. The 30-minute hold and 16:00 horizon are named defaults, distinct from the two-period strict rule. | no |
| R-A04 | cannot-tell | no | no | no | [2026-07-22 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A04-A-2026-07-22.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A04-B-2026-07-10.png>). amt_80pct currently tests outside open and the 09:59/10:29 one-minute closes. It never checks the target. July 22 is a direct false success interpretation: both closes are inside, but RTH high 29342.25 does not reach VAH 29361.75. Source: [MAMT p.18](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>). The source requires an outside open and two consecutive 30-minute periods back inside value before a complete traverse. It does not restrict those periods to A and B or specify whether closes or complete ranges must be inside. | no |
| R-A05 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A05-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A05-B-2026-01-28.png>). a05_poc_tell counts touching minutes rather than independent visits, infers direction from the first AM close, and accepts held-through OR retest-reject. Near/far targets use the entire window, including prices before the signal. Only the chop flag is scored. Source: [LIVE p.9](</workspace/sources/documents/discretionary/amt-on-live-markets.pdf>); [RTVP p.5](</workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>). The POC tell is a sequence: repeated failed visits imply chop; an aggressive push through followed by a holding retest supports the far edge. POC is a fixed reference, and the source does not define the numeric visit reset or hold duration. | no |
| R-A06 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A06-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A06-B-2026-01-28.png>). Retained a06_naked_poc comes from a tape check against today’s final RTH POC, tested for absence overnight; this is retrospective. Fresh assembly changes 311 of 668 rows, but fresh recipe code passes the established balance’s own POC as older_poc. The helper lacks ordered break/tag windows and targets the near boundary. Source: [MAMT p.9](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [MAMT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p010-i1.jpeg>); [MAMT p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p011-i1.jpeg>); [MAMT p.26](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [LIVE p.10](</workspace/sources/documents/discretionary/amt-on-live-markets.pdf>); [VP2 p.6](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>). MAMT p.9 explicitly targets established VAH after rejecting an older POC from above, and VAL in the mirror. The p.11 accepted example labels vah = target. FORMULAS repeats the far-boundary procedure but its fixture stops at near VAL; that fixture conflicts with the source. The older POC belongs to a distinct prior balance. | no |
| R-A07 | yes | no | no | no | [2026-06-09 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A07-A-2026-06-09.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A07-B-2026-07-10.png>); [2026-01-30 sequence-positive](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A07-sequence-positive-2026-01-30.png>). The producer covers both IB edges but passes the entire post-IB window to both break and retest checks. It can count the initial boundary contact as a later retest. June 9 passes despite no return to IB low 29365 after the outside hold completes. Next value, HTF filter and other source boundaries are omitted. A separate January 30, 2026 sequence breaks IB low 25790.75 at 11:55, completes the named hold at 12:26, retests at 12:30 and confirms the half-width rejection at 12:36, beyond the producer’s noon endpoint. Source: [RTVP p.6](</workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>); [RTVP p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p008-i1.jpeg>); [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>); [WIC p.5](</workspace/sources/documents/discretionary/whos-in-control.pdf>); [WIC p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/whos-in-control-p008-i1.jpeg>); [TRAP p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p006-i1.jpeg>). The source drawings show a break followed by a separate return and continuation. IB is one named boundary family; the illustrated balance and shelf edges remain distinct. The numerical 30-minute hold and G-default are research choices. | no |
| R-A08 | yes | no | no | no | [2026-01-02 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A08-A-2026-01-02.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A08-B-2026-07-10.png>); [2026-08-19 sequence-positive](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A08-sequence-positive-2026-08-19.png>). Fresh code now evaluates both break sides, contrary to the stale FORMULAS description. Its inside hold still checks only the re-entered edge, and target lookup is whole-window and compared with re-entry rather than confirmation. The scorer reports reacceptance presence without the subsequent opposite-edge outcome. August 19, 2026 supplies a later valid named reacceptance: outside hold known10:19, reentry known11:44, inside hold known12:14 and opposite-edge touch in the12:18 bar. An earlier inside episode is invalidated before target. Source: [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>). The relevant event is acceptance outside a balance followed by acceptance back inside it, then a move toward the opposite side. This differs from merely opening outside or briefly poking an edge. | no |
| R-A09 | yes | no | no | no | [2026-08-21 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A09-A-2026-08-21.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A09-B-2026-07-10.png>); [2026-08-26 sequence-positive](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A09-sequence-positive-2026-08-26.png>). The helper adds a total 30-minute traversal cap, scans only AM, and the scorer keeps traverse_nohold while ignoring retest_continuation. August 21 has the traversal prerequisite but its helper continuation result is false. August 26, 2026 demonstrates a valid named continuation after a41-minute traverse: first outside close known09:44, opposite outside close known10:25, retest10:25 and half-width rejection known10:28. No uninterrupted30-minute inside hold occurs. Source: [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>). The source says a traverse without holding inside changes how later retests are traded. It does not impose a 30-minute maximum on the entire traverse. | no |
| R-A10 | cannot-tell | no | no | no | [2025-10-08 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A10-A-2025-10-08.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A10-B-2026-07-10.png>); [2026-05-19 sequence-positive](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A10-sequence-positive-2026-05-19.png>). The current drive detector uses the 09:30 open but excludes the opening one-minute bar. It does not establish all four opening types or the separate MAMT day-type table. Only drive presence is scored; a completed day label cannot be an opening feature. October 8 opening bar low 25074 is below open 25079.75, so the literal upward-drive condition is false despite the skip-first-minute flag. Source: [AMT1 p.10](</workspace/sources/documents/discretionary/amt-lesson-1.pdf>); [AMT1 p.11](</workspace/sources/documents/discretionary/amt-lesson-1.pdf>); [MAMT p.18](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [MAMT p.20 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p020.png>). Open drive concerns movement away from the opening price; test-drive and rejection-reverse require ordered tests. AMT and MAMT publish different day-type descriptions. Their qualitative boundaries need named numerical choices. | no |
| R-A11 | no | no | no | no | [2026-02-03 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A11-A-2026-02-03.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A11-B-2026-07-10.png>). Fresh producer includes P+high-only and b+low-only, unlike the stale P-only description. It classifies sparse prior HLC3-volume prices rather than trade-volume VA thirds. February 3 is a b continuation case, not P. The single path flag pools a source-specific directional claim into one score. Source: [AMT1 p.6 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-amt-lesson-1-p006.png>); [AMT1 p.13](</workspace/sources/documents/discretionary/amt-lesson-1.pdf>); [RTVP p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p009-i1.jpeg>); [RTVP p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p010-i1.jpeg>); [RTVP p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p011-i1.jpeg>); [MAMT p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p007-i1.jpeg>); [MAMT p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p007-i2.jpeg>); [MAMT p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p008-i1.jpeg>). The drawings distinguish D, upper-heavy P, lower-heavy b/B and two-distribution B. MAMT’s B-day prose says upside resolution, but its actual p.7 B diagram breaks down. FORMULAS says that diagram points up, which is visually false. Stop the MAMT directional certification until resolved. | yes |
| R-A12 | no | no | no | no | [2026-08-25 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A12-A-2026-08-25.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A12-B-2026-07-10.png>). The retained flag is only the 09:30 opening price within two ticks of any detected overnight LVN price. No two-bulge validation, LVN/shelf band, old-POC alignment or post-open respect/disrespect sequence is scored. The available aggression trust gate remains binding. Source: [MAMT p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p014-i1.jpeg>). The p.14 picture spans 18:00→09:30 overnight and the following RTH. It has two overnight bulges, an LVN band, a shelf band, and a red POC from an earlier left-hand balance aligned with the LVN. FORMULAS incorrectly makes that POC the developing RTH POC. The inventory prose does not supply an exact signed-volume estimator. | no |
| R-A13 | cannot-tell | no | yes | yes | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A13-A-2026-07-10.png>); [2026-08-31 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A13-B-2026-08-31.png>). The current onh_or_onl event correctly uses 18:00–09:30 extremes and 09:30–16:00 touches. July 10 touches both; August 31 touches neither. The full ONVA/POC/MPOC and prior-reference conditional tables remain absent from this score. A different NQ rate does not itself contradict the cited ES study. Source: [MAMT p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p015-i1.jpeg>); [MAMT p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p016-i1.jpeg>); [MAMT p.21 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p021.png>); [MAMT p.22 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p022.png>); [MAMT p.23 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p023.png>). The source distinguishes overnight high/low, VA edges, volume POC and geometric MPOC. The 94% figure is either extreme during RTH. For the 73% MPOC statement, the text says open inside balance while the pictured open appears below the drawn VAL; keep that condition unresolved. The tabulated half-gap pHOD cells also have an ambiguous denominator. | yes |
| R-A14 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A14-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A14-B-2026-01-28.png>). The actual scorer is bool(tpo_poor), not the stale documented OR. family_gap builds today’s full RTH one-point occupancy and calls either one-period extreme poor. Both reviewed days show long one-period tails, and all 647 scores are true. This is neither prior-profile unfinished business nor a next-session fill/revisit/hold result. Source: [TPO3 p.3](</workspace/sources/documents/discretionary/tpo-lesson-3.pdf>); [TPO3 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p005-i1.png>); [TPO3 p.5 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-tpo-lesson-3-p005.png>); [TPO3 p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p006-i1.png>); [TPO3 p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p006-i2.png>); [TPO3 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p007-i1.png>); [TPO3 p.9](</workspace/sources/documents/discretionary/tpo-lesson-3.pdf>); [C3 p.6](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>). The single-print picture marks an interior G-only strip between distributions; outer single-letter tails are excess. The poor-low figure has repeated QR at the extreme, conflicting with the prose phrase single TPO tail. The source provides 30-minute periods but no exact row size or tie algorithm. | yes |
| R-A15 | yes | no | yes | yes | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A15-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A15-B-2026-07-10.png>). The current single-side IB path row is a valid named close-break statistic. January 28 breaks only the low and closes below it; July 10 breaks both and is correctly negative for single-side. The continuation numerator and complete source table are missing. Source: [TPO3 p.8](</workspace/sources/documents/discretionary/tpo-lesson-3.pdf>); [MAMT p.19](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [MAMT p.23 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p023.png>); [XF p.8](</workspace/sources/documents/jumbo/xfcmg2.pdf>). The IB is the first hour. Source tables separate either, both, neither and one-side breaks; the continuation rows use the closing position conditional on the broken side. Close-based versus wick-based break remains an explicitly named interpretation. | no |
| R-A16 | yes | no | no | no | [2026-01-02 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A16-A-2026-01-02.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A16-B-2026-07-10.png>). Current code sets ledge=prior VAL and compares it with full-AM scalar VWAP or the same profile’s VAH. It never selects a shelf, tests touch/rejection or computes stacked-versus-lone outcomes. The full-AM VWAP is unavailable before noon. Source: [VP2 p.6](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>); [VP2 p.7](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>); [VP2 p.8](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>). The source stacks an actual shelf ledge with independent references such as VWAP, old POC or a value edge, and trades the reaction at the ledge. It supplies no universal confluence distance. | no |
| R-A17 | yes | no | no | no | [2026-01-02 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A17-A-2026-01-02.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A17-B-2026-07-10.png>). Current code takes today’s final RTH occupied-volume bins, chooses the deepest minimum, then looks for any median-sized bin on the lighter-volume side. Dropping zero bins changes adjacency, and an arbitrary lighter side is not the source balance orientation. No event-level rejection or ledge/shelf comparison is scored. Source: [MATH p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/the-math-behind-auction-market-theory-p013-i1.jpeg>); [MATH p.15](</workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>). The source requires a return to balance beyond the low-volume region, rather than a taper ending at the profile edge. It distinguishes a gradual shelf transition from an abrupt ledge; numerical ratios are named research choices. | no |
| R-A18 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A18-A-2026-07-10.png>); [2025-01-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A18-B-2025-01-10.png>). Retained a18_single_reach falls back to AM-high≥prior-VAH. Fresh assembly differs on 386 of 668 rows. Fresh code fabricates a single above/below value, passes tick integers where the helper expects prices, and invokes the same bullish VAL rejection twice. It does not mirror the side, check a real unfilled ledger or score the target. Source: [C3 p.6](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>); [C3 p.7](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>). C3 separates interior levels from balance extremes and depicts directional bias toward unfilled destinations. It also supplies a 40% intraday value setting; the prior 70% RTH VA used here is a named balance choice. | no |
| R-F01 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F01-A-2026-07-10.png>); [2026-08-31 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F01-B-2026-08-31.png>). The ETH running HLC3 geometry is implemented, but f01 ORs its touch-only flag with the final-AM trade-VWAP absorption flag. The latter fixes noon bands retrospectively. Neither branch requires local absorption at the causal ETH band, the open-draw filter, or subsequent median reach. July 10 is a touch positive with f01_vwap_fade=false; August 31 has neither flag. Source: [VWAP p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p003-i1.png>); [VWAP p.4](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>); [VWAP p.7](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>); [VWAP p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p008-i1.png>); [VWAP p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p008-i2.png>); [VWAP p.8 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p008-i3.png>). The settings show Session anchor, HLC3, standard deviation and enabled 1/2 bands. Text also names 2.5/3. The p.3 handwritten upper −2/lower +2 signs are reversed relative to the settings; its description of VWAP as POC is also mathematically wrong. Preserve those source discrepancies without changing the defined weighted-mean formula. | yes |
| R-F02 | yes | blocked | blocked | blocked | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F02-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F02-B-2026-01-28.png>). The retained recipe is correctly blocked by the trade-CVD trust gate. Helpers exist, but the staged source events are not certified by a trusted FINDINGS row. The two diagnostic charts show price and executions only and cannot prove CVD divergence. Source: [VWAP p.6](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>); [FP9 p.6 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-fp-lesson-9-p006.png>). The source distinguishes regular divergence, breakout participation and a delta extreme without price extension. The numerical swing, slope and exhaustion windows are research definitions. OHLC-signed volume is a different object. | no |
| R-F03 | cannot-tell | no | no | no | [2024-12-03 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F03-A-2024-12-03.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F03-B-2026-07-10.png>). Current code compares final AM trade VWAP, overnight trade VWAP and prior VA midpoint. December 3, 2024 gives 21201.74/21202.91/21204.125 and a true spread predicate; July 10 spreads them widely. Neither is the documented anchor set, and neither scores a confirmed touch/rejection. Source: [VWAP p.7](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>). The lesson combines the session VWAP with weekly and a swing/event anchor. An overnight mean and a prior value-area midpoint do not supply those anchors. The source gives no universal convergence distance or automatic major-swing definition. | no |
| R-F04 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F04-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F04-B-2025-10-08.png>). The helper named candle_stack is called on the entire current RTH profile; an AM min/max overlap is then ORed with the old whole-AM footprint flag. July 10 is true even though the returned RTH zone 30075.50–30077.50 is never reached in AM. No later departure, revisit or hold is established. Source: [FP8 p.4](</workspace/sources/documents/discretionary/fp-lesson-8.pdf>); [FP8 p.5 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-fp-lesson-8-p005.png>); [FP8 p.6](</workspace/sources/documents/discretionary/fp-lesson-8.pdf>); [FP8 p.7](</workspace/sources/documents/discretionary/fp-lesson-8.pdf>). FP8 p.5 highlights ask cells 220/410/512 while the printed diagonal bids 4120/3980/2110 do not satisfy the described 3–4× rule. FORMULAS resolves this by calling the drawing illustrative, contrary to the instruction to stop on a source/figure conflict. The conflict must remain open. | yes |
| R-F05 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F05-A-2026-07-10.png>); [2026-01-02 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F05-B-2026-01-02.png>). The producer treats the entire AM as one candle and scores price/delta disagreement only. July 10 O29834.75/C29944.25 with delta−443 is true; January 2 falls with delta−457 and is false. Full-RTH POC is passed to the helper but does not affect the scored disagreement fields; the defect is missing candle/level/flip chronology, not a direct POC dependency of that flag. Source: [FP9 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/fp-lesson-9-p004-i1.png>); [FP9 p.5 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-fp-lesson-9-p005.png>); [FP9 p.7](</workspace/sources/documents/discretionary/fp-lesson-9.pdf>). FP9 p.5 explicitly describes the flip as living inside a single candle. Its BEFORE/AFTER seven-row profiles show the POC moving from the sixth row to the second row within that candle. FORMULAS instead specifies adjacent candles, which is a different construction. The source sequence is location, absorption and flip; exact high/low position cutoffs are not printed. | no |
| R-F06 | no | no | no | no | [2026-08-21 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F06-A-2026-08-21.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F06-B-2026-07-10.png>). The current prior-VA scan uses two-minute aggression summed across all prices, then future 15-minute extrema. On August 21 its first true print is 09:31:59 at29402.50 near VAH29402, with buy4610/sell3892; the incoming path is already descending from above. This does not verify buyer aggression arriving upward into the band. Shelves, old extremes, local delta, speed and exhaustion states are not joined. Source: [DOM6 p.3](</workspace/sources/documents/discretionary/dom-lesson-6.pdf>); [DOM6 p.4](</workspace/sources/documents/discretionary/dom-lesson-6.pdf>); [DOM6 p.6 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-dom-lesson-6-p006.png>); [DOM6 p.7](</workspace/sources/documents/discretionary/dom-lesson-6.pdf>); [DOM5 p.6](</workspace/sources/documents/discretionary/dom-lesson-5.pdf>). The source requires aggression into a previously marked level, little progress and a reversal. It distinguishes exhaustion and visible replenishment. Three ticks is an illustrated zone; q90, two minutes and 0.25R are research defaults. FORMULAS has an arithmetic error: 17.5 exceeds 0.25×67.75=16.9375. | no |
| R-F07 | yes | blocked | blocked | blocked | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F07-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F07-B-2026-01-28.png>). The retained iceberg recipe remains blocked. Existing BBO reload flags saturate and do not establish the source sequence. Available diagnostic executions on July10/January28 are insufficient to certify an iceberg, and no depth substitute was plotted. Source: [DOM7 p.3](</workspace/sources/documents/discretionary/dom-lesson-7.pdf>); [DOM7 p.4](</workspace/sources/documents/discretionary/dom-lesson-7.pdf>); [DOM7 p.5](</workspace/sources/documents/discretionary/dom-lesson-7.pdf>). The source differentiates size that replenishes as trades execute from quotes that disappear before trading, then waits for added participation. MBP-1 can support a limited at-touch quote/trade inference; it cannot identify hidden reserve size or off-touch depth as fact. | no |
| R-F08 | no | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F08-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F08-B-2026-07-10.png>). The producer has no absorption event ID: it takes the first AM trade as origin, the first20 trade signs as direction, and the last80 prices as reward window. January28 returns a 547-tick short reward over the morning; July10 fails with an adverse opening-to-noon move. Neither tests three ticks after absorption, local context, second aggression or reward retest. Source: [ABS p.3](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>); [ABS p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p004-i1.jpeg>); [ABS p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p006-i1.jpeg>); [ABS p.7](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>); [ABS p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p009-i1.jpeg>); [ABS p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p011-i1.jpeg>). ABS p.11 repeats the same buyer-spike/opposition-losing annotation at both edges while the VAL body text describes buyers regaining control. FORMULAS elects the body text; source/figure agreement must instead remain unresolved. The wall and reward retest are bands, and the CVD-median subcheck retains its separate trust limitation. | yes |
| R-F09 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F09-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F09-B-2026-01-28.png>). Only first20 versus last20 AM size medians are scored. Both dated cases give1/1, and all647 observations are false. This does not establish absence of local thinning or lift-off. Replenishment remains blocked; the available stage helpers are not assembled into a chronological event. Source: [STOP p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.6 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p006-i2.png>); [STOP p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p009-i2.png>); [STOP p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.11 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.11 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p011-i2.png>); [STOP p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.12 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.12 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p012-i2.png>); [STOP p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>). The source stages are defense, replenishment, exhaustion and lift-off, with a two-to-four-tick reward and entry within one-to-two ticks. ES digit classes and NQ40-range illustrations are distinct. The 10-lot median threshold on NQ is a research reading, not a portable author constant. | no |
| R-F10 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F10-A-2026-07-10.png>); [2025-03-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F10-B-2025-03-28.png>). The score is last-five AM prints above the final AM low by two ticks, true646/647. July10 compares prices near29943.50 with29675; the only negative March28 finishes at19542, the morning low. There is no swing, local delta, escape, five-bar protection or high-side mirror. Source: [RD p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-delta-p004-i1.jpeg>); [RD p.5](</workspace/sources/documents/discretionary/reading-delta.pdf>); [K18 p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p008-i1.png>). The source protects successive lows/highs after local aggression, a small balance and an escape. The fractal, delta percentile and five-bar quiet period are research definitions. FORMULAS declares protection at escape even though its own five later quiet bars have not yet happened. | no |
| R-F11 | yes | no | no | no | [2026-07-23 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F11-A-2026-07-23.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F11-B-2026-07-10.png>). The score pairs full-current-RTH volume POC with an LVN in that same final profile. July23 POC28810 lies next to LVN28810.25; July10 POC30050 is far from the nearest LVNs. No signed-delta extremum, as-of dealing range, touch, wick reaction or repeat count is used. Source: [RD p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-delta-p007-i1.jpeg>); [RD p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-delta-p001-i2.jpeg>); [RD p.10](</workspace/sources/documents/discretionary/reading-delta.pdf>). The source pairs concentrated signed delta with a low/minor volume node at either balance extreme and shows repeated wick reactions. It does not equate a volume POC with a delta print. The node detector, tolerance and reversal fraction in FORMULAS are research rules; its fixture separates a wick rejection from a much larger0.5R follow-through. | no |
| R-F12 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F12-A-2026-07-10.png>); [2026-08-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F12-B-2026-08-28.png>). The score compares median size of the last five AM prints with the first five. Equality1=1 makes July10 aggressive; August28 gives2→1 and false. Neither identifies arrival at an extreme or uses displacement, directional volume, five-minute bins or the15-minute confirmation. Source: [WIC p.4](</workspace/sources/documents/discretionary/whos-in-control.pdf>); [WIC p.5](</workspace/sources/documents/discretionary/whos-in-control.pdf>); [WIC p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/whos-in-control-p001-i2.jpeg>). The source judges how price arrives at an extreme and later confirms a genuine break/retest. It draws bands and names a15-minute check. Five-minute speed, volume slope and percentile cuts are research definitions, not values supplied by the lesson. | no |
| R-F13 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F13-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F13-B-2026-01-28.png>). Current code is wired to the high-side helper, but substitutes prior RTH high, maximum AM price as dp.max and the same current-AM high for both AM and PM failures. It passes min(AM closes) as break_close and min(AM lows) as intra_lo; break_close<intra_lo is impossible for valid bars. The pairing result is ignored and the low mirror is absent. Source: [TRAP p.3](</workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>); [TRAP p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p004-i1.jpeg>); [TRAP p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p005-i1.jpeg>); [TRAP p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p006-i1.jpeg>); [TRAP p.8](</workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>); [TRAP p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p009-i1.jpeg>). The source aligns a balance with traded structure, shows heavy buying at its upper extreme, two failures in prior AM/PM, and a later intraday break followed by a body-aggression retest. Both sides are a documented mirror; the150–160-point Asia remark is illustrative. | no |
| R-F14 | cannot-tell | no | no | no | [2026-03-09 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F14-A-2026-03-09.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F14-B-2026-07-10.png>). The code takes any same-price3.5× imbalance in the entire current RTH, then ANDs it with an independent Jumbo-level BigTrades flag. March9 is true without a matched candle, price or side. July10 is false because the independent Jumbo flag is false. There is no body/wick classification, matching print or later retest. Source: [BIG p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p003-i1.jpeg>); [BIG p.4](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>); [BIG p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p005-i1.jpeg>); [BIG p.6](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>). The figures use NQ40-range bars and30–60 display settings, with a350% imbalance line attached to the aggression print. Body prints are rewarded and wick prints absorbed. A one-minute substitute is a named variant. The wording350 percent more and a3.5× platform ratio should not be silently treated as a resolved numerical identity. | yes |
| R-F15 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F15-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F15-B-2025-10-08.png>); [2026-07-09 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F15-source-date-2026-07-09.png>). The current helper is wired, contrary to stale FORMULAS text, but ofm_entry uses only a comparison of resqueeze_close with fail_wick; it ignores the computed release, failure, refill and tape flags. The caller supplies final-AM extrema, last-eight wick prints and6–9 swings without event order. Retained F15 differs from fresh tape on22/33 replay dates; July10 and source-dateJuly9 are retained true but fresh false with no qualifying catalyst. Source: [OFM p.2 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.2 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.4 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p004-i2.png>); [OFM p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.5 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p005-i2.png>); [OFM p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.6 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p006-i2.png>); [OFM p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.7 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p007-i2.png>); [OFM p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.8 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p008-i2.png>); [OFM p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p009-i2.png>); [OFM p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.10 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p010-i2.png>); [OFM p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.14 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p014-i2.png>); [BIG p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p007-i1.jpeg>); [BIG p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p008-i1.jpeg>); [BIG p.14](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>); [BIG p.18](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>); [CONT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p010-i1.jpeg>). The source distinguishes the first absorbed aggression line from its box and requires a failed attempt before the re-squeeze. The drawings show both long and short versions; entries on the first failure are a different event. The five-minute cluster,0.1R and30-second speed quantile are research definitions. Short-gamma and CVD checks need their own trustworthy, causally available inputs. | no |
| R-F16 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F16-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F16-B-2026-01-28.png>). The current helper has both mirrors, but the caller supplies6–9 extremes, wick counts from all AM, a whole-AM no-close condition, unordered extrema for departure/return and an absorption-any-side flag. Its leave test can be satisfied by distance from the opposite edge. The target is the opposite6–9 edge rather than the prior rewarded opposite print. Both selected cases are false under the substitute geometry. Source: [BIG p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p015-i1.jpeg>); [BIG p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p016-i1.jpeg>); [BIG p.18](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>). The source fades a retest of failed aggression at either edge and targets the last area where the opposite side was rewarded. Its drawn9-point stop/33-point target is an annotation, not a filled trade or a universal bracket. Long-gamma context is separate from a balance-day label. | no |
| R-F17 | cannot-tell | no | no | cannot-tell | [2025-01-23 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F17-A-2025-01-23.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F17-B-2026-07-10.png>); [2025-01-10 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F17-source-date-2025-01-10.png>). Current on_touch_refill requires>=100-lot prints in a two-minute,<=2-tick cluster, checks only the first three signs and can include later opposite-side prints in its bounds. It waits until two minutes after cluster start, then departure in the large-print direction and any later return. January23 produces21928.25–21928.75 and a return near11:23; there is no hold/penetration outcome. January10 NQ is not the MNQ source reconstruction. Source: [REF p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.5 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p005-i2.png>); [REF p.5 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p005-i3.png>); [REF p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.7 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p007-i2.png>); [REF p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.10 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p010-i2.png>); [REF p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.12 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.12 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p012-i2.png>); [REF p.17 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.17 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.17 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p017-i2.png>); [REF p.18 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.18 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.18 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p018-i2.png>); [REF p.18 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p018-i3.png>); [REF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.23 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>). The source pools NQ/MNQ; its datedJanuary10 example is MNQ with>=40 displayed, while text mentions60/80/100 in seconds. Per-print versus burst, exact formation window, defender side and hold denominator are not uniquely specified. The12/32/96 bracket is an execution illustration, not a definition proving the42% hold statistic. | no |
| R-F18 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F18-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F18-B-2025-10-08.png>). Current code is wired but the helper ignores release_close and catalyst in its trigger logic. It uses last30seconds of AM speed versus a whole-AM threshold, no-close-through over all AM and the independent prior-VA absorption flag. Continuation is computed but not scored. Fresh replay changes26/33 dates, and July10 retained true is fresh false with no catalyst. Source: [CONT p.11](</workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>); [OFM p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.5 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p005-i2.png>); [OFM p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.14 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p014-i2.png>). The source fast squeeze proceeds without the failed first attempt of OFM. It then absorbs opposing aggression at the first pullback. Speed of Tape(10) is visible but the unit of10 is not stated;30seconds, q90 and the15-minute no-failure interval are named choices. | no |
| R-R01 | cannot-tell | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-B-2026-01-28.png>). The QQQ producer pools0–14DTE, mismatches09:30 spot with later first-five-minute quotes and uses an assumed call-positive/put-negative sign. Its flip loop calls the initial0→first-nonzero cumulative value a crossing, producing635 onJuly10 and594 onJanuary28, both first populated strikes. Walls are extrema of net signed strike exposure, not separately aggregated call/put gamma. Only short_gamma prevalence is scored;3 of647 eligible sessions have no GEX and enter as false. Native OI supplements preserve each product, including missingJanuary28 NDX/SPX nodes and unparsed NQ option statistics. Source: [GEX p.6](</workspace/sources/documents/discretionary/gex-framework.pdf>); [GEX p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/gex-framework-p007-i1.jpeg>); [GEX p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/gex-framework-p013-i1.jpeg>); [GEX p.14](</workspace/sources/documents/discretionary/gex-framework.pdf>); [GEX p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/gex-framework-p015-i1.jpeg>); [GEX p.19](</workspace/sources/documents/discretionary/gex-framework.pdf>). The source shows0DTE, net-GEX sign, a gamma flip, three ranked walls, max pain and location-dependent price responses. It does not publish the dealer-position sign model, flip algorithm, Vol Trigger or hedge-pressure formula. The p.13 drawing includes a ranked call wall below spot despite the text saying calls above. Aggregate spot-repricing root, cumulative-strike crossing and per-strike sign change are different objects; none can be silently selected as the author formula. Native-product evidence: [all native plots and reviews](</workspace/implementation/reports/phase1-live/chart-audit/native_options_review.json>). | yes |
| R-R02 | yes | no | yes | yes | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R02-A-2026-07-10.png>); [2026-01-02 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R02-B-2026-01-02.png>). The retained15–18 gate correctly uses the prior session’s VIX close: July10=15.84 is true andJanuary2=14.95 is false. That literal score event is valid. The full binning omits14, and implied/realized range, level response, intraday VIX direction and curve/context comparisons are not implemented by this ID. Source: [VIX4 p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vix-lesson-4-p003-i1.png>); [VIX4 p.4](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.5](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.6](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.7](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.8](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.9](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>). The source names13,14,15–18 and20 cuts, expected daily percentage VIX/sqrt252, range completion and intraday VIX direction. Its30/50/95-point examples are ES illustrations, not fixed NQ ranges. Prior VIX close is a declared pre-open input choice; S&P-based VIX applied to NQ is a named cross-product context. | no |
| R-R03 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R03-A-2026-07-10.png>); [2026-01-02 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R03-B-2026-01-02.png>). The caller hard-codes any_close_beyond=false, news=false and default developing_overlap=true. Directional death is therefore a wick across the prior VA edge; neutral theses survive automatically. The helper assigns death at the evaluation time or survival to16:00 instead of the first observed cause. July10 is neutral/true; January2 long/false after a fall throughVAH25634. Source: [C1 p.3](</workspace/sources/documents/discretionary/code-1-thesis.pdf>); [C1 p.4](</workspace/sources/documents/discretionary/code-1-thesis.pdf>); [C1 p.6](</workspace/sources/documents/discretionary/code-1-thesis.pdf>); [C3 p.7](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>). The source requires a labelled validity band with start/end and three possible death causes: structure, value shift or new information. Open-versus-prior-VA labels,30-minute holds and non-overlap of developing value are named research definitions rather than author-exact automatic thesis construction. | no |
| R-R04 | yes | no | blocked | blocked | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R04-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R04-B-2026-01-28.png>). The recipe remains blocked by the FINDINGS trust gate. Existing upstream defects include absolute ES/YM/RTY pivot prices compared with NQ prices, whole-AM rather than same-time extremes, and missing sister data capable of returning true. Own-profile VA/single-print first-fill states are not assembled. The dated normalized-return panels are diagnostics, not IOD/RFZ detections. Source: [C1 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/code-1-thesis-p005-i1.png>); [C1 p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/code-1-thesis-p005-i2.png>); [C1 p.7](</workspace/sources/documents/discretionary/code-1-thesis.pdf>). The source compares each market’s own AMT objective and which sister uses it first. The user’s SMT definition is prior high/low taken on one index and not another, across timeframes. A3/3 fractal detector and relative-return divergence are different objects. | no |
| R-S01 | yes | no | no | no | [2026-08-21 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S01-A-2026-08-21.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S01-B-2026-07-10.png>). The caller reuses one either-side absorption Boolean for long-at-VAL and short-at-VAH, attaches the final AM print as entry, and supplies whole-AM extrema as local print extremes and outcomes. August21 is true after an opening VAH scan even though the accepted long uses VAL. A source band, same-level refill, sequence and prior-extreme objective are absent. Source: [NYAM p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p004-i1.png>); [NYAM p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p005-i1.png>); [K18 p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p010-i1.png>); [K18 p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p010-i2.png>); [K18 p.11](</workspace/sources/documents/discretionary/18k-payout-session.pdf>). The source shows absorption and refill at a defined dealing-range band, a close away, and an objective such as the prior RTH extreme. Both long and short examples are printed. Prior VA edges, two-minute aggregation, q90 and one-minute closes are named choices; the source uses 40-tick range bars. | no |
| R-S02 | no | no | no | no | [2026-08-21 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S02-A-2026-08-21.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S02-B-2026-07-10.png>). The OHLC caller supplies zero defence volumes. The helper counts extrema within a doubly widened band, may re-arm from the same bar’s opposite extreme, and returns n>=3 without requiring a third-test close-through entry. August21 has six counted VAL tests; the unmeasured defence condition is automatically true. The resistance-long branch exists but carries the misleading third_test_short key. Source: [NYAM p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p006-i1.png>); [NYAM p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p007-i1.png>); [K18 p.11](</workspace/sources/documents/discretionary/18k-payout-session.pdf>). The source depicts sellers testing support from above three times and a short through it, followed by a printed loss when it holds. The two-line support band and the ticket stop inside that band are separate observations. Absence of aggressive buying does not establish absence of passive buyers defending against aggressive sellers; FORMULAS conflates those readings. | no |
| R-S03 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S03-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S03-B-2026-01-28.png>). The current code calls r_s03_second_defence, contrary to the stale FORMULAS description of an F09 alias. It uses a last-print-derived catalyst, the minimum close and maximum high of all AM, total AM sells against a per-print q75, and the last eight AM sell sizes. It is short-only, has no first/second defence identity and scores zero of647. Source: [K18 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p004-i1.png>); [K18 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p007-i1.png>); [K18 p.11](</workspace/sources/documents/discretionary/18k-payout-session.pdf>). The source requires an established OFM area, another break/retest and sustained participation/refresh. The0.8 ratio, q75 and one-minute representation are named quantitative choices. Aggressor print consistency and actual replacement of resting orders are different evidence; the latter stays blocked. | no |
| R-S04 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S04-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S04-B-2026-01-28.png>); [2026-07-10 source-date](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S04-source-date-2026-07-10.png>). Retained weekly references exist, but are prior-five-session18:00–16:00 aggregates, not a verified source weekly profile. Unknown aggressor side is treated as sell. The caller counts every AM high above the prior high as a touch, uses whole-AM no-close/minimum, one-price pooled buy/sell ratios and the final microbalance/close. July10 dp_min30250 is untraded in AM; January28 counts148 supposed failures. Zero scores do not validate this construction. Source: [K2345 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p004-i1.jpeg>); [K2345 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p005-i1.jpeg>); [K2345 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p007-i1.jpeg>). The source shows heavy buying in the weekly delta profile behind the upward move, a small green350% box, failed reclaims and a long above a microbalance. FORMULAS instead selects dp.min near the weekly high and a downward departure. The figure does not establish that equivalence. The fixture also says distance\|120−118.5\|=1.5 is within tR1.0; it is not. The short example on p.9 belongs to S05. | yes |
| R-S05 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S05-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S05-B-2026-01-28.png>). The current producer does use a price-defined close-run, unlike the stale FORMULAS clock-box claim. It scans all09:40–12:00 runs and keeps the last qualifying box, comparing only the final AM close. July10 has a real named breakout at noon from29914–29941.5; January28 ends inside its final box. Earlier events are overwritten, and HTF reach/stop/trail are not the scored event. Source: [K2345 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p007-i1.jpeg>); [K2345 p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p009-i1.jpeg>). The source prints a small grey price-defined balance, long and short breaks, a stop beyond the box and an HTF objective. Five close-constrained bars,0.1R and one-minute bars are named definitions; the author screenshot uses40-tick range bars. The ticket’s approximately7-point box and5.59 planned R:R are examples. | no |
| R-S06 | no | no | no | no | [2026-06-12 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S06-A-2026-06-12.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S06-B-2026-07-10.png>). The current recipe has both directions, despite the stale short-only description. It uses a single prior RTH extreme, prior high/low-to-last-close as rejection, the first price-sorted occupied-bin OHLC HVN and whole-AM close/extrema. Neither branch requires price to touch the chosen level. June12 fires a long near28599 while AM stays above29200; July10 also never touches its lower candidates. Source: [K10 p.6](</workspace/sources/documents/discretionary/10k-first-month.pdf>); [K10 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/10k-first-month-p007-i1.jpeg>); [K10 p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/10k-first-month-p008-i1.jpeg>); [K10 p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/10k-first-month-p012-i1.jpeg>). The source ES2-minute chart uses a marked rejection area plus a nearby minor HVN, with a long mirror and absorption. Text says1.5R, but both tickets print1.00R with20-tick stop/target and the long illustrates a192-tick run. FORMULAS chooses the prose target while acknowledging the conflict; faithful certification must stop. Transfer to NQ is a separate named study. | yes |
| R-S07 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S07-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S07-B-2026-01-28.png>). The recipe uses the final AM close as an always-long entry, combines a prior-VA edge touch anywhere in AM, and measures MAE from the whole RTH minimum including pre-entry prices. Only survived_15 is scored, with no absorption, held-area geometry, objective or re-entry. July10’s morning plunge is charged against its noon entry even though afternoon price rises. Source: [ANAT p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p004-i1.png>); [ANAT p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p006-i1.png>); [ANAT p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p007-i1.png>); [ANAT p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p008-i1.png>); [ANAT p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p009-i1.png>); [ANAT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>). The source uses held-buyer/seller areas, objectives and stops beyond the defended structure. Its35/188,15/211 and115/248-tick tickets are illustrations, not universal thresholds. The re-entry is permitted only inside the same approximately7-point band. FORMULAS turns example distances into fixed rows; its source meaning must be corrected before faithful use. | no |
| R-S08 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S08-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S08-B-2026-01-28.png>). The overriding recipe now calls r_s08_minor_node, not the stale two-HVN presence rule. It substitutes prior RTH high for balance top, a single first sorted OHLC HVN for the band, current-AM high counts for prior rejections, and final three five-minute close−open values for executed delta. No actual touch, same-side control, flip, target or composite behaviour is scored. Both plotted nodes lie below the AM path. Source: [CONT p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p004-i1.jpeg>); [CONT p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p005-i1.jpeg>); [CONT p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p007-i1.jpeg>); [CONT p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p001-i2.jpeg>); [CONT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p010-i1.jpeg>). The source shows a minor-node band at the top of an established5-minute balance, repeated resistance and negative executed delta; extreme buying above it changes the read to a retest long toward VWAP. The approximately20-point balance band,5-point refill zone and9-point/55-point ticket are distinct. SD+1/+2 labels are coincident VWAP references, not the node definition. | no |
| R-S09 | yes | no | no | no | [2026-08-11 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S09-A-2026-08-11.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S09-B-2026-07-10.png>). The producer instead compares09:30 open with the future09:30–10:00 OHLC-VP VAH, freezes that line, and requires an unordered post10 close above plus any low below. August11 is true even though A-low29631.75 is far below prior VAH29819.75. July10 fails its open gate; later PM rally is not an above-value opening setup. Source: [AVG p.21 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [AVG p.21 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [AVG p.22 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [AVG p.22 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [AVG p.22 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p022-i2.png>). The source requires the entire A-period above prior VAH, observation around10:00, a break of current developing VAH with aggressive buying and a later defence of those imbalance prices. The source sketch is long-only; a developing-VAL short is a named mirror.70% VA, one-minute proxy and G-default hold are declared choices. | no |
| R-P01 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P01-A-2026-07-10.png>); [2025-01-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P01-B-2025-01-10.png>). The producer takes 19 log returns from at most 20 closes, starts with only five closes, and can substitute an RTH close. Both-side touch chooses smaller overshoot instead of distance from the bar open. ext_max is only the touch-bar extension. July10 returns from upper29959.91 to 08:00 open29816.75; January10 lower21232.94 touch does not return to21320.75 by noon. These validate observations of the named implemented variant, not the printed sigma distribution. Source: [PINE AM TBR - NQ Stats.txt L135](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/AM TBR - NQ Stats.txt:135>); [PINE AM TBR - NQ Stats.txt L146](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/AM TBR - NQ Stats.txt:146>); [PINE AM TBR - NQ Stats.txt L336](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/AM TBR - NQ Stats.txt:336>). The source uses sample standard deviation of 20 previous completed DAILY simple percentage returns, anchored to 08:00 open, with first ±0.25σ touch. Its lower-timeframe branch scans for return starting on the touch minute; its chart fallback skips that bar. FORMULAS simultaneously says after the touch bar and from the touch bar itself. Stop unqualified certification until those branch semantics are explicit. Hardcoded hourly claims and milestones are not measured local rates. | no |
| R-P02 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P02-A-2026-07-10.png>); [2026-06-16 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P02-B-2026-06-16.png>); [2026-08-31 event-negative](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P02-event-negative-2026-08-31.png>). The current producer scans09:00–16:00 and ORs hour results. The helper only calculates high-side returns, so low_sweep and high_ret_50 does not implement a low return.637/647 is effectively any high-sweep edge return. July10 has a high-sweep return; June16 has clear low-sweep returns, including09:01→09:02, yet scores false. Source: [PINE NQ Hourly Retracements 12y Stats with Levels.txt L126](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracements 12y Stats with Levels.txt:126>); [PINE NQ Hourly Retracements 12y Stats with Levels.txt L151](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracements 12y Stats with Levels.txt:151>); [PINE NQ Hourly Retracements 12y Stats with Levels.txt L185](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracements 12y Stats with Levels.txt:185>). The source retains prior-hour H/L/open/mid, compares current open with prior open, and distinguishes high and low sweeps and returns to the swept edge, prior mid, CURRENT hour open and opposite edge. Its depth levels are percentages of prior-hour width. The24×2 arrays are quoted historical claims, not a new daily any-event probability. | no |
| R-P03 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P03-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P03-B-2026-01-28.png>). The producer invents break time hour+4minutes and target time hour+20minutes, both before the hour box completes, chooses direction using future extremes and otherwise assumes a low break even when none occurred. The helper ignores invalidation.647/647 midpoint wins is not the source event. January28 hour01 has no break; July10 hour06 has an actual07:00 high break followed07:30 midpoint return. Source: [PINE magic_hours L55](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:55>); [PINE magic_hours L145](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:145>); [PINE magic_hours L465](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:465>); [PINE magic_hours L527](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:527>). The source builds hours23/00/01/02/06/07/08, then seeks the midpoint after a strict first break and before a stop at75% or100% of width. Actual outcome logic ends three hours after box completion; the displayed hard-stop countdown is one hour later. The supplied file ends in malformed text_ and cannot compile as supplied. FORMULAS does not preserve the source execution distinctions, so faithful certification stops. | no |
| R-P04 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P04-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P04-B-2026-01-28.png>). The current caller uses09:00–10:00, only high raids, and scores raid OR confirmation. The helper uses maximum depth to the cutoff even after the first confirmation. July10 raid of the wrong box around11:25 cannot demonstrate the source09:15 box event, whose deadline is11:15. January28 high-side non-raid ignores a large low-side move. Source: [PINE Session Raid Stats.txt L27](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Raid Stats.txt:27>); [PINE Session Raid Stats.txt L395](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Raid Stats.txt:395>). Source boxes are02:00–02:15,09:00–09:15 and13:00–13:15 NY, with strict5-point raid and close back within120minutes. Same raid-bar close-back is allowed. Literal source buckets disagree with their labels: bucket0 covers depths below30, while overflow starts80 despite >70 text. At deadline the source saves statistics before that bar’s confirmation update. FORMULAS’s labelled buckets are not the literal implementation. | no |
| R-P05 | yes | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P05-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P05-B-2026-07-10.png>). The implementation instead uses London00:00–03:00 and NY09:30–12:00, and ORs the bullish failure into the positive scorer while the bearish helper omits symmetric failure/stay outputs. January28 source London is bearish with level26286.1875 and a valid NY wick/close-back; the code is a bullish failure at26292.0625. The equal true flags represent different events and geometry. Source: [PINE Session Range Candles + 25% Level.txt L814](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Range Candles + 25% Level.txt:814>); [PINE Session Range Candles + 25% Level.txt L930](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Range Candles + 25% Level.txt:930>). The source uses Asia18:00–02:00, London02:00–08:00 and NY08:00–17:00. The level is25% into the London BODY from its close side. Success/fail/stay compares the entire NY candle’s wick and final close, not a local rejection candle. Source doji drawing uses >= while the statistical direction uses >; regime branches overlap and their precedence matters. | no |
| R-P06 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P06-A-2026-07-10.png>); [2026-08-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P06-B-2026-08-28.png>); [2026-08-26 event-negative](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P06-event-negative-2026-08-26.png>). The caller substitutes Asia20:00–00:00 and London00:00–03:00, returns only whether any London first hit exists, and omits the NY and conditioned tables. The helper chooses both-side ties by overshoot and delays sequential detection to a later bar. July10 source Asia low is first reached02:21; August28 source low is reached03:44, outside the legacy London window, so the retained false is not a source negative. Source: [PINE NQ Statistical Mapper.txt L199](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Statistical Mapper.txt:199>); [PINE NQ Statistical Mapper.txt L283](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Statistical Mapper.txt:283>); [PINE NQ Hourly Retracement Levels.txt L128](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracement Levels.txt:128>). The source Asia20:00–02:00, London02:00–08:00 and NY08:00–16:00 tables condition on session open versus the previous session midpoint. First-hit ties choose HIGH, and the opposite sequential flag can be set in the same chart bar. Asia-in-NY uses crossover/crossunder rather than any span. FORMULAS’s later opposite hit and generic hit description do not fully describe these source branches. | no |
| R-P07 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P07-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P07-B-2025-10-08.png>). The helper computes an actual midpoint but calls onlyOR5 with an outcome ending at noon, uses C>O and post-OR first extreme, and the scorer retains only midpoint return. Both plotted dates formed the OR low09:30 before high09:33, while the helper calls high first from later action. July10 midpoint29866.875 returns09:39; October8 midpoint25104.5 never returns in RTH. Source: [PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt L141](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:141>); [PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt L476](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:476>); [PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt L899](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:899>). The source first extreme is the first attainment of the FINAL OR high/low WITHIN the OR, not the first post-OR edge touch in FORMULAS. Doji is bullish (C>=O); the midpoint flag is not session-gated and source extension comparisons are strict. Its unconfirmed security values and SessionClose validation flag also require availability cautions. Stop the current cohort definition before using source probabilities. | no |
| R-P08 | no | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P08-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P08-B-2026-07-10.png>). The current scorer is a reduced close-break path class after10:30, without the eight combo keys, midpoint leave/return, percentile extensions or source wick inequalities. January28 IB26301/26205 breaks only low on closes; July10 IB29968.5/29798 later breaks both. Correct box placement does not validate the missing source statistic. Source: [PINE Initial Balance Statistical Mapping.txt L44](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Initial Balance Statistical Mapping.txt:44>); [PINE Initial Balance Statistical Mapping.txt L55](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Initial Balance Statistical Mapping.txt:55>); [PINE Initial Balance Statistical Mapping.txt L279](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Initial Balance Statistical Mapping.txt:279>). The source combo is IB colour, first attainment of FINAL IB high/low WITHIN the IB, and IB CLOSE versus midpoint. FORMULAS says open versus midpoint and post-10:30 first touch, changing the table key. The source0.1%-of-price return uses an endpoint-near test and can leave/return in the same bar; it also skips the first post-IB bar and processes16:00 before reset. These variants cannot share unqualified source claims. | no |
| R-P09 | no | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P09-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P09-B-2026-07-10.png>). Unlike the stale CODE paragraph, the producer now uses full09:30–16:00 NY H/L and strict wick breaks correctly for that named window. It then ORs above/below far-side no-break with inside stay, losing the distinct conditional probabilities. January28 opens above priorH26114.25 and never breaks farL25917.25; July10 opens inside and later breaks only the upper edge. Source: [PINE NQ Stats RTH Breaks with stats.txt L27](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats RTH Breaks with stats.txt:27>); [PINE NQ Stats RTH Breaks with stats.txt L61](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats RTH Breaks with stats.txt:61>); [PINE NQ Stats RTH Breaks with stats.txt L148](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats RTH Breaks with stats.txt:148>). The source prints conditional above/below far-side no-break and inside zero/one/both-side rates. Its time() calls omit timezone, so default Custom08:30–16:00 and the09:30–16:00 toggle use the chart exchange clock. FORMULAS labels them as NY without resolving that setting. The source displays fixed claims rather than dynamically computing those rates. | no |
| R-P10 | yes | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P10-A-2026-07-10.png>); [2025-01-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P10-B-2025-01-10.png>). Current pivot lines are correctly placed for the named prior18:00–17:00 Globex inputs, but the producer scores only RTH high>=P, omits the lower price bound and supplies no opening-zone outcomes. July10 P29773.25 is actually contacted10:32; January10 P21313.33 is uncontacted during RTH despite the earlier08:30 move. Most fields described by the source remain unscored. Source: [PINE Daily Floor Pivots.txt L1](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Daily Floor Pivots.txt:1>). The source classical pivots share prior H/L/C algebra with the implemented P/R1–3/S1–3. It also has R4/R5/S4/S5 and golden zones, and printed opening-zone statistics whose state is reset every bar in source. Timezone is implicit and the headline probabilities are hardcoded. A one-sided high>=P test does not establish contact with P. | no |
| R-P11 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P11-A-2026-07-10.png>); [2024-08-07 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P11-B-2024-08-07.png>). The current producer searches one-minute09:30–10:00 bars and scores whether a gap exists, passing no fill outcome.645/647 is presence, not fill/effectiveness. July10 first BISI29892.75–29893.5 forms on09:33 bar, known09:34, and later fills; August7,2024 has no qualifying1m gap in that window. Neither decides the missing source5m W1/W2 study. Source: [PINE First presented FVG (with stats) with statistical hourly ranges & bias.txt L8](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/First presented FVG (with stats) with statistical hourly ranges & bias.txt:8>); [PINE First presented FVG (with stats) with statistical hourly ranges & bias.txt L148](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/First presented FVG (with stats) with statistical hourly ranges & bias.txt:148>); [PINE First presented FVG (with stats) with statistical hourly ranges & bias.txt L170](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/First presented FVG (with stats) with statistical hourly ranges & bias.txt:170>). Default source FVG timeframe is5m. Its W1 condition actually opens09:00 despite the09:30 comment; raw security lookahead_on and chart-shifted HTF timestamps can expose future data. The first15-minute bias reads a later selected-bar close. The source never defines the hardcoded effectiveness event, while FORMULAS chooses hourly direction. Stop faithful certification of that choice and of the W1 clock. | no |
| R-P12 | no | no | no | no | [2026-01-02 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P12-A-2026-01-02.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P12-B-2026-07-10.png>). Current code passes only09:30 and09:31 one-minute candles, tests high sweep/close-back, and never tests low sweep or CISD. Its unscored mid_box uses prior body mid and current O. January2,2026 has a high sweep of25728.75 and a close-back; July10 sweeps prior high29876 but closes above it.133/647 therefore measures this two-minute high-only test. Source: [PINE HTF Sweep Model with CISD Table.txt L136](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweep Model with CISD Table.txt:136>); [PINE HTF Sweep Model with CISD Table.txt L309](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweep Model with CISD Table.txt:309>); [PINE HTF Sweep Model with CISD Table.txt L343](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweep Model with CISD Table.txt:343>); [PINE HTF Sweeps & Liquidity Levels with CISD.txt L695](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweeps & Liquidity Levels with CISD.txt:695>); [PINE Open Source Fractal - Customized.txt L1](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Open Source Fractal - Customized.txt:1>). The source Model default main HTF is60m, with an LTF opposing-run2..10 CISD confirmed using the previous chart close. Its C3 box is current open to C2 BODY midpoint. OSF uses C2 H/L midpoint and its own LTF run/projection rules; the Sweep/CISD sibling has yet another selective log-wick midpoint. FORMULAS substitutes15m and an HTF-close CISD and mixes candle identities in its fixture. These are separate sources, not interchangeable definitions. | no |
| R-P13 | yes | yes | yes | yes | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P13-A-2026-07-10.png>); [2026-08-31 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P13-B-2026-08-31.png>). The current tdo_hit helper and tdo_touch_ny scorer correctly implement the stated midnight-open touch, unlike the stale09:30–12:00 CODE paragraph.460/647 is the retained pooled exact-touch count. July10 level29933 is actually touched; August31 level29352.5 stays below every NY bar. The four yes verdicts certify this headline predicate and geometry; the ancillary midpoint/conditional table rows remain missing. Source: [PINE NQ Hourly Retracement Levels.txt L128](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracement Levels.txt:128>); [PINE NQ Hourly Retracement Levels.txt L279](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracement Levels.txt:279>); [PINE NQ Statistical Mapper.txt L310](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Statistical Mapper.txt:310>). The source midnight level is the00:00NY open, with exact bar-span touch in08:00–16:00. The hourly source also shows00–01/02–03/07–08 midpoints and other hour opens, plus position/pattern-conditioned claims. The two sources quote73.67% and73.75%; they are distinct historical claims, not evidence that the implementation must reproduce either exact number. | no |
| R-P14 | no | no | no | no | [2026-01-28 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P14-A-2026-01-28.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P14-B-2026-07-10.png>). The actual producer never calls r_p14_hod_checkpoint. It compares09:30–10:00 high with final09:30–16:00 high within one tick, with no four-hour state, ETH day or LOD. The unused helper counts changes of the running maximum rather than all eliminated candles and ignores the actual checkpoint when testing hod_at. January28 RTH H26301 is in by10; July10 final H30077.75 prints about15:03. Source: [PINE 4H HOD LOD Checkpoint Analysis.txt L30](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/4H HOD LOD Checkpoint Analysis.txt:30>); [PINE 4H HOD LOD Checkpoint Analysis.txt L401](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/4H HOD LOD Checkpoint Analysis.txt:401>); [PINE 4H HOD LOD Checkpoint Analysis.txt L556](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/4H HOD LOD Checkpoint Analysis.txt:556>). The source freezes state at22/02/06/10/14 after the prior candle completes and before processing the new bar. Every completed candle has its own eliminated flag; prev compares the just-completed candle with its immediate predecessor. FORMULAS instead refers to the new checkpoint candle, and its fixture undercounts eliminated older candles. Unsupported source lookup combinations return50 with sample0, not measured50% probability. | no |
| R-P15 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P15-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P15-B-2026-01-28.png>). The producer substitutes prior60 RTH median widths, assumes MFE=.6*width and MAE=.4*width, anchors09:30 and scores only the upper threshold over full RTH. No source session quantiles, SRP ladder or OHLC history is assembled. July10 upper30071.15 is reached around15:03, outside source08–12 NY Morning; January28 upper26423.425 is unhit while the ignored lower threshold26138.55 is crossed. Source: [PINE Session Statistical Levels.txt L24](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Statistical Levels.txt:24>); [PINE Session Statistical Levels.txt L707](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Statistical Levels.txt:707>); [PINE Session Range Projections with stats.txt L372](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Range Projections with stats.txt:372>); [PINE Statistical OHLC Projections HTF.txt L322](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Statistical OHLC Projections HTF.txt:322>); [PINE NQ Stats Price Distributions.txt L302](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats Price Distributions.txt:302>). These are three distinct source constructions. SSL uses100-session nearest-rank histories and has a bearish-side drawing swap plus counters mixing frozen levels with newly appended current data. SRP uses three15-minute boxes, whole-candle body extrema and range1-only statistics; its independent both-side hits are not ordered reversals. OHLC projection distribution is M+D (full range), while FORMULAS draws D alone and says latest60 despite source choosing oldest60 and unshifted live HTF data. Stop the combined faithful row. | no |
| R-P16 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P16-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P16-B-2025-10-08.png>). Current code has improved: it uses prior-session VIX and prior18–17 last close with correct log-space a/b bounds. It scores whole18–16NY path inside the outer1.0 bands, not per-zone touch or final-close containment. Prior last print is not verified official settlement and missing Globex data may fall back to RTH.658 retained rows lack the four newest bound keys. July10 fits outer29636.39–30229.04; October8 rises above25326.17 late in RTH. Source: [PINE Expected Volatility .txt L11](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Expected Volatility .txt:11>); [PINE Expected Volatility .txt L30](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Expected Volatility .txt:30>); [PINE Expected Volatility .txt L58](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Expected Volatility .txt:58>); [PINE NQ Stats Price Distributions.txt L302](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats Price Distributions.txt:302>). Expected Volatility uses prior chart DAILY close and prior NASDAQ:VOLI daily close with a=V/16/100 and b=V/√365/100. Its session uses fixedGMT−5, and lower rectangle bounds are supplied in reversed order. VIX is a declared substitute, not VOLI. The75.2% daily-close claim comes from a different return-distribution script, so it does not describe whole-path containment in these bands. FORMULAS does not preserve those differences. | no |
| R-P17 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P17-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P17-B-2025-10-08.png>). The scored flag only checks whether full RTH high/low brackets the prior18:00 open; no source OHLC-profile VA outcome is built. family_open’s half-range/half-body weighting and heavier-neighbour VA are different. The standalone r_p17_bar_vol only demonstrates allocation arithmetic and is not wired to a complete profile. July10 actually touches29937.75 around09:50; October8 RTH stays above25059.75. Actual trade VP is plotted solely as available diagnostic. Source: [PINE Sessions & VP with prev session VP & daily weekly opens.txt L216](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Sessions & VP with prev session VP & daily weekly opens.txt:216>); [PINE Sessions & VP with prev session VP & daily weekly opens.txt L252](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Sessions & VP with prev session VP & daily weekly opens.txt:252>); [PINE Sessions & VP with prev session VP & daily weekly opens.txt L641](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Sessions & VP with prev session VP & daily weekly opens.txt:641>). Source defaults are30 equal-height rows and70% volume. VA expands alternately DOWN thenUP by distance, not heavier-neighbour as FORMULAS also says. Literal source omits the threshold-crossing row and can null the POC at the final row. Source profile clocks (including fixedUTC NY/London and exchange-day Daily) differ from the named prior-RTH transplant. The18:00NY daily and Sunday weekly opens are separate from profile clocks. Stop the contradictory profile specification. | no |
| R-P18 | yes | no | blocked | blocked | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P18-A-2026-07-10.png>); [2026-01-28 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P18-B-2026-01-28.png>). The current recipe calls r_p18_ohlc_cvd for the simple-sign series and scans a grid-divergence proxy, but the scorer remains blocked. Another producer, family_flow._ohlc_cvd, allocates volume fractionally by close position and is neither the simple sign nor the literal Confluence method. Both plotted sessions show the actual simple-sign ETH cumulative series and reference prices; there is no permissible positive/negative trade trigger to certify. Source: [PINE Confluence Suite.txt L107](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Confluence Suite.txt:107>); [PINE momentum-volume-flow-levels.txt L80](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:80>). The simple MVFL sub-bar proxy assigns+V/−V/0 by close versus open. Confluence Suite instead assigns whole volume using close position, then candle direction, then prior close and persistent prior sign. Neither is executed aggressor delta. FORMULAS describes a named simple-sign series and explicitly blocks it as a trigger; that gate is appropriate. | no |
| R-P19 | yes | no | no | no | [2026-08-06 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P19-A-2026-08-06.png>); [2026-07-10 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P19-B-2026-07-10.png>); [2025-09-29 event-negative](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P19-event-negative-2025-09-29.png>). The helper only examines array positions0 and1, and the producer supplies09:30–12:00 but never loops later pairs or passes fill data. Thus25/647 is the first09:30/31 body-gap presence rate. August6 down gap29327–29328.5 forms by09:32 and actually fills on09:34; July10 first pair has no gap, which says nothing about later pairs. Down-gap confluence is hardcoded false. Later-pair inspection of July10 finds an up gap29881.25–29882.25 formed09:32 (known09:33), so the retained daily false is a counterexample. September29,2025 has no qualifying gap in any of389 adjacent RTH pairs; the642-session scan found49 such all-RTH negative dates. Source: [PINE 8020 System.txt L50](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:50>); [PINE 8020 System.txt L120](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:120>); [PINE 8020 System.txt L251](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:251>); [PINE 8020 System.txt L309](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:309>). The source detects adjacent BODY gaps at least4ticks wide, evaluates old gaps before creating new ones, and marks a later near-edge fill. It also defines price-ending20/80 references,8tick confluence and zero-wick repairs. This is distinct from three-candle wick FVG and from AMT’s80% value-area traverse. | no |
| R-P20 | no | no | no | no | [2026-07-10 A](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P20-A-2026-07-10.png>); [2025-10-08 B](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P20-B-2025-10-08.png>). The actual scorer is AM max print>=100lots AND AM price range>=8ticks:425/647. It never calls r_p20_mvfl and builds none of the source zones or seven votes. July10 max245lots/range1266ticks passes; October8 max92/range748 fails. The unused helper doubles anomaly thickness (±0.2% instead of±0.1%), and its passing fixture expects that wrong width. Source: [PINE momentum-volume-flow-levels.txt L5](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:5>); [PINE momentum-volume-flow-levels.txt L79](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:79>); [PINE momentum-volume-flow-levels.txt L113](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:113>); [PINE momentum-volume-flow-levels.txt L171](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:171>); [PINE momentum-volume-flow-levels.txt L414](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:414>). MVFL source is a seven-vote hysteresis indicator using OHLC-signed sub-bar volume. RULES explicitly asks for an aggressor-delta rebuild, while FORMULAS presents the literal OHLC version; that conflict stops faithful certification. FORMULAS also clusters at close, but source bullish events use body bottom and bearish body top, weighted by absolute delta. The historical assistant upgrade proposal is not source-author proof of equivalence. | no |

## Per-ID repair specifications

Apply these only in a separately authorized implementation task. Do not create a new faithful recipe to repair a source contradiction. Keep author definitions, explicitly named research defaults, unavailable inputs and outcome measurements distinguishable. Every event record must identify its instrument/contract, session scope, source/variant, level bounds, feature cutoff, known_at, touch, confirmation, invalidation and outcome horizon. Unknown or incomplete observations are null with a reason, not false.

Common implementation requirements: use a fixed exchange clock for resampling; require complete bars; advance close-based known_at to bar completion; use an explicit tick-rounding policy; scan events chronologically; freeze chosen levels at the decision time; never select a level or direction using later extrema. Do not count one extended visit as multiple retests. If a one-minute bar contains both success and invalidation with unknown order, inspect available executions or keep the observation ambiguous. Cache identity must include source/producer version, required schema keys, input hashes, clocks, parameters and eligibility. Validate the schema before reuse; a matching revision number alone is insufficient.

For profile work, include zero-volume price bins within the price grid, define tie handling, retain aggressor-unknown volume separately and keep fixed prior profiles separate from developing profiles. Quantile/volume baselines used at an event must use only observations available then. Rates require an explicit eligible population, censoring and event unit; conditional empty populations have n=0. A presence/touch statistic must not inherit a confirmation, hold, reversal or target-reaching label.

### R-J01 — Judas reversal at the projection ladder

The author shows reversal areas on both sides, overshoot and price confirmation. The January 28, 2025 NQH2025 example has a body close below the lower 0.5 projection before the successful rebound. FORMULAS' strict no-close-beyond G-default therefore excludes a cited source example. The 86.46% statement and the time histogram are separate statistics with an unrecovered joint denominator.

July 10's retained positive is selected with knowledge of the deepest level reached over the full AM. A shallower early reversal and a later 0.5 touch are collapsed into one flag; the source reversal example violates the documented invalidation rule.

**Source references:** [TBR p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i1.png>); [TBR p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i2.png>); [TBR p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i3.png>); [TBR p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i1.png>); [TBR p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i2.png>); [TBR p.30 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i1.png>); [TBR p.30 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i2.png>); [TBR p.30 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i3.png>); [TBR p.30 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i4.png>); [XF p.47 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p010-i1.jpeg>); [FIND p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p010-i1.jpeg>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.j01](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:496>), [grid.py::reject_after_touch](</workspace/implementation/src/trading_research/research/phase1_live/grid.py:89>), [FORMULAS.md::R-J01](</workspace/planning/phase-1-live/FORMULAS.md:702>).

**Build steps:**

1. Stop the faithful J01 claim. Retain the current G-default calculation as a named research variant until the source-compatible overshoot/confirmation definition is resolved; do not silently relax invalidation to make the historical example pass.
2. Preserve source geometry: W=H69-L69; EQ=(H69+L69)/2; high-side levels H69+kW and low-side levels L69-kW for k=0.1,0.2,0.3,0.5. Store explicit lower/upper bounds for the mean-reversal areas, and distinguish the 1.33–1.66 extension family. Do not shift an entire side by a further half-range.
3. For the named G variant, enumerate each level and side in chronological order after the 09:00 freeze. Save the first eligible touch and the exact confirmation/invalidation timestamps. Choose the tested level from information at that touch, never from the eventual AM extreme. Require confirmation in its declared horizon and record whether touch or confirmation must fall in 09:40–09:50.
4. Return separate per-depth/per-side observations and an explicitly defined session aggregate. Report touch rate, confirmed reversal rate conditional on touch, and reversal-time distribution separately. Replace the scorer's OR of ladder, m05-time and m05-rejection flags with the selected event's complete predicate.

**Acceptance checks:**

- Keep the 2025-01-28 source chart as a documented disagreement with the strict G variant, not a fixture expected to pass by force.
- Changing bars after a decision must not change the selected level, side or trigger timestamp.
- July 10, 2026 shallower pre-09:40 touches and the later 0.5 touch must remain separate records; a body close beyond the tested level must invalidate the strict G variant.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J01-A-2026-07-10.png>) | true | cannot-tell | July 10 H29887.75/L29771.25, upper +0.5 29946 first touched near09:49; price closes above it around09:50–52. Earlier ladder reversal at09:40 uses shallower depths. Full-AM choice of deepest level is retrospective; strict no-close-beyond does not describe the source Jan28 example. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J01-B-2026-01-28.png>) | false | cannot-tell | Not the dated source screenshot (that is 2025-01-28). 2026 code box H26326.75/L26255.25/W71.50; m05L26219.50 touched around09:36–38, bounce toward26295 followed fullAMdowntrend. Code false consistent early-touch time gate, but source G-default conflict stops faithful certification. |
| [source-date / 2025-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J01-source-date-2025-01-28.png>) | false | source example yes; strict documented G no | Actual continuous input reproduces the source path: lower0.5=21181.50 is penetrated by bodies around09:47–48 before a sharp rebound. Source NQH2025 line is about21181.25, one tick lower; contract/aggregation offset is retained. This confirms the source/G-invalidation conflict rather than a missing reversal. |

### R-J02 — 09:30 opening leg into projections

Trade #1 runs from the 09:30 open toward the projection ladder before the reversal window. The public examples use different depths; FORMULAS explicitly requests separate depth rows and a 0.5-before-09:40 headline.

The field named open_to_m05_before_0940 ORs 0.1/0.2/0.3 and 0.5 reaches. July 10 is positive because a shallow upper projection is reached early; upper 0.5 is reached only around09:49. January 28, 2026 supplies an actual early lower-0.5 example.

**Source references:** [TBR p.8](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i1.png>); [TBR p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i2.png>); [TBR p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p009-i3.png>); [TBR p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i1.png>); [TBR p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p010-i2.png>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.j02](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:499>).

**Build steps:**

1. Compute independent flags for each depth k in {0.1,0.2,0.3,0.5} and each side using levels H+kW/L-kW frozen at09:00.
2. The 0.5 headline must use only the 09:30≤t<09:40 window and an actual bar span or execution within the declared tick tolerance. Keep shallower reaches in named depth columns, not in its OR.
3. Store 09:30 opening price, first edge taken, first target time and excursion from open. If selecting the first-edge side, resolve same-bar two-sided order with executions or mark ambiguous. Calculate R=absolute(open-target) only when positive.
4. Condition the Model A row using its actual available-at timestamp; a 09:30–09:35 RVOL value cannot gate an entry at09:30. Report unconditional and conditional populations separately.

**Acceptance checks:**

- 2026-07-10 must be false for 0.5 before09:40 while retaining its shallow-depth positives.
- 2026-01-28 must record the early lower0.5 touch; 2025-01-10 must remain false before09:40.
- A target touched at09:40 exactly belongs outside this window; later bars cannot alter the earlier reach flag.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J02-A-2026-07-10.png>) | true | no for stated ±0.5-before09:40 event; yes for shallower depth variants | H29887.75/L29771.25/W116.50;m05H29946 first reached about09:49, after09:40. mr01H29899.40 reached about09:33. Code true pools mean ladder reaches under ±0.5 headline. Need additional valid stated-event positive case. |
| [B / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J02-B-2025-01-10.png>) | false | no | H21372.50/L21045/W327.50;m05L20881.25. 09:30–09:40 stays above low-edge and all lower mean/projection targets; m05 onlylateraround10:10. Code false is appropriate for pre09:40 target. |
| [stated-positive / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J02-stated-positive-2026-01-28.png>) | true | yes | Lower0.5=26219.50 is reached around09:36–38, before09:40; later rebound and downtrend are irrelevant to this touch event. This is a stated-event positive in addition to the two original diagnostic cases. |

### R-J03 — Extended range, single break and inner-level retrace

The source uses EQ/quadrants after an extended overnight range and limits expectations to the box edges. Width ratio≥1, the 15-minute hold and formal single-break rule are named research defaults, not authored numerical thresholds.

The retained rate is zero. The hold call tests strict beyond-EQ closes from an EQ touch, so equality can reject the very retrace being sought. A full-AM single-side outcome is also used as if it were a known morning gate. An additional read-only scan of642 complete eligible RTH sessions found no positive under the existing extended/single-path selection, EQ touch before10:00 and15-minute side-hold check. This is a search result for those named defaults, not evidence that the author setup never occurs.

**Source references:** [TBR p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p012-i1.png>); [TBR p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i1.png>); [TBR p.13 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i2.png>); [TBR p.13 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i3.png>); [TBR p.13 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i4.png>); [TBR p.24](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [formulas.py::midretrace_hold](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:194>), [grid.py::hold_after_break](</workspace/implementation/src/trading_research/research/phase1_live/grid.py:110>), [recipe_score.py::_preds.j03](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:502>).

**Build steps:**

1. Keep extended_width_ratio and red_folder_0830 as separate known-before-open inputs, plus their explicitly named union. Guard zero/missing prior RTH range and early-close sessions.
2. After the first completed close beyond one box edge, arm EQ/Q25/Q75/06:00-open retraces separately. Save touch time and confirmation time; do not reuse a breakout hold helper without specifying how equality at the retraced level is treated.
3. For the named hold variant, require the declared sequence of complete one-minute closes on the break side after the touch, with continuous coverage. Separate entry-by10:00 from confirmation-by10:00; the current prose allows touch by10:00 but source trading interest ends then, so neither timing convention may be silently substituted.
4. At decision time require the opposite edge to remain unbroken so far. Record final single-side status as an outcome. After confirmation, measure edge reach by10:00/noon and the separately named lunch-consolidation range, rather than returning only the retrace boolean.

**Acceptance checks:**

- Include equality-at-EQ, wick-through-with-close-on-side and actual close-through cases; an always-zero implementation fails these semantic fixtures.
- 2025-12-29 must show the EQ touch around09:51 and subsequent crossing separately; do not call it a completed15-minute hold by10:00.
- 2026-07-10 is not an extended single-break positive; changing its10:30 opposite break must not rewrite an earlier signal.
- The retained complete-session scan has no genuine positive for its declared J03 conditions. Keep this coverage limit and the dated negatives visible; do not relabel an equality fixture or a nonextended day as a historical source-positive.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-12-29](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J03-A-2025-12-29.png>) | false | no | Dec29 extended box H25776.75/L25660.75/EQ25718.75; first high break near09:36 then EQ return09:51, but subsequent candles cross below EQ near10:00. No clean 15-minute hold confirmed by10:00. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J03-B-2026-07-10.png>) | false | no | July10 not extended and both edges break across AM; EQ test09:40 cannot qualify the extended single-break condition. |

### R-J04 — Purged overnight extremes and single-break continuation

The source treats prior overnight highs/lows already removed as context for a single-break continuation and larger projections. The exact clock and purge tolerance must remain explicitly named where the author does not define them.

The producer substitutes containment of Asia/London extrema by the completed6–9 box for a timestamped sweep history. It omits the post-break hold/continuation sequence. November25 reaches lower1.0; July10 leaves upper overnight references unpurged.

**Source references:** [TBR p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i1.png>); [TBR p.13 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i2.png>); [TBR p.13 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i3.png>); [TBR p.13 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i4.png>); [TBR p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p014-i1.png>); [TBR p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p014-i2.png>); [TBR p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p015-i1.png>); [TBR p.15 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p015-i2.png>).

**Code to change:** [formulas.py::purged_overnight](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:183>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.j04](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:505>).

**Build steps:**

1. Create immutable Asia and London reference records with their own build-end timestamps. Only price after each reference is formed can sweep it; do not allow a reference to purge itself during construction.
2. For each H/L store first strict sweep time, side and depth in ticks. At09:30 evaluate which required references were swept. Equality/tolerance belongs to a named variant, not an implicit range-containment test.
3. Freeze the active break side after a completed RTH close, require the specified entry/hold branch and evaluate each own-width extension only after that confirmation. Retain opposite-side invalidation and censored coverage.
4. Output purge configuration, break/hold, target depth and horizon independently. Use the conjunction required by the stated continuation recipe as the score; retain pure target reach as a separate outcome.

**Acceptance checks:**

- 2025-11-25 should retain the observed lower1.0 reach24714.25; verify each prior reference's sweep time before calling the setup purged.
- 2026-07-10 must fail the all-extremes-purged gate because Asia/London highs remain above the frozen6–9 high.
- A reference still forming, an equal high and a sweep after09:30 must not be interchangeable.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-11-25](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J04-A-2025-11-25.png>) | true | yes for the named clock variant | Nov25 box H24975.25/L24844.75 contains the plotted Asia/London high and low; lower single break reaches L-W24714.25 around09:44. Source purge chronology and clock choice still need explicit event records. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J04-B-2026-07-10.png>) | false | no | July10 Asia H29963.50 and London H29948.75 remain above box H29887.75 at09:00; AM breaks both sides and reaches neither ±1 before noon. |

### R-J05 — Single-break retraces to EQ, range open and OR midpoint

Newer examples distinguish the6–9 midpoint, its06:00 opening print and a5m/15m opening-range midpoint. The author describes entry areas and subsequent continuation; the strict G rejection is a named formalization.

The score reduces the family to a full-AM single-side path plus a midpoint-retrace flag. It does not require the A-period condition, confirmation, OP/OR variants or a target reached after confirmation.

**Source references:** [XF p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p012-i1.png>); [XF p.12 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p012-i2.png>); [XF p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p015-i1.jpeg>); [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.25 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p025-i1.png>).

**Code to change:** [sessions.py::_midretrace](</workspace/implementation/src/trading_research/research/phase1_live/sessions.py:113>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.j05](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:508>).

**Build steps:**

1. Maintain separate level IDs for6–9 EQ,06:00 open,5m OR mid known09:35 and15m OR mid known09:45. Preserve the literal source label and clock in each record.
2. Detect the first A-period close break and subsequent retrace in order. The opposite edge must remain clean at that decision; final-AM path classification is a later outcome.
3. For the existing named G variant, apply its exact rejection/invalidation rule after the touch and record disagreements with source examples that permit body penetration. Do not certify an unspecified author confirmation as G-default.
4. After the actual confirmation, measure broken-edge and1.0 reach by noon, with a separate edge-by09:50 outcome. Replace the current touch-only scorer with the complete chosen variant.

**Acceptance checks:**

- 2026-01-28 shows a real low-side break then EQ26291 rejection; OP26317.25 must remain a different, unreached level for that episode.
- 2026-07-10 may have midpoint reactions but must not be labelled final single-break.
- An OR midpoint cannot trigger before its construction completes; an earlier target visit cannot satisfy a later entry's target.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J05-A-2026-01-28.png>) | true | yes for EQ retrace observation | Jan28 lower break followed09:45 EQ26291 touch and downward rejection; range open26317.25 and Q75 remain untouched by this retrace. The observed midpoint response is real; code does not implement the full inner-level family. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J05-B-2026-07-10.png>) | false | no for single-break recipe | July10 EQ29829.50 touches before and after high break, then low breaks10:30; both-side path disqualifies single-break category. |

### R-J06 — Opening-location context and RVOL

The newer panels separately label previous RTH value, previous full-ETH value, previous price range, RTH open and the6–9 box. Outside prior value/price range with elevated RVOL is a conditional context observation; it is not equivalent to outside the6–9 range.

The headline is a conjunction of outside_both, RVOL and a final double break, not the requested path distribution by opening cell. The09:30–09:35 RVOL is unavailable at09:30, and one prior-VA pair cannot represent all the source's profile scopes.

**Source references:** [XF p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p007-i1.png>); [XF p.8](</workspace/sources/documents/jumbo/xfcmg2.pdf>); [XF p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p010-i1.png>); [XF p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p010-i2.png>); [XF p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p016-i1.png>); [XF p.18 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p018-i1.jpeg>).

**Code to change:** [family_open.py::build_open_table](</workspace/implementation/src/trading_research/research/phase1_live/family_open.py:142>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.j06](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:511>).

**Build steps:**

1. Store opening location against each explicit reference population: prior RTH VA70, prior full-ETH VA70 where present, prior RTH price range and current6–9 H/L. Use a scope-qualified key; do not alias pdVAH to pRTHVAH.
2. Freeze09:30 price-derived cells at09:30. Calculate the named five-minute RVOL only after09:35, using the declared prior60-session median and complete five-minute volume. Save separate known_at for the cell and RVOL.
3. Produce all four A-period/AM path shares per opening cell, and the outside-prior-value-and-price-range conditional distribution. A 'double-break rate given outside+RVOL' denominator is qualifying sessions, not all647 sessions.
4. Keep Model A, one-way A-period, overnight reference status and EV context as separate columns with explicit availability; do not call any of their unions one source setup.

**Acceptance checks:**

- 2026-08-27 is above prior RTH price/value but inside6–9; it can qualify the outside-prior conditional row while Model A remains false.
- 2026-07-10 fails outside_both even though the AM later breaks both6–9 edges.
- Removing09:34 volume must make the RVOL-conditioned row incomplete, not a false early signal.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-27](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J06-A-2026-08-27.png>) | true | yes for outside-prior-price-and-value plus RVOL/double-break row | Aug27 open is far above prior RTH high29368.25 and VAH29305, but inside6–9 box29514.75–29630.00; early downside then high break around11:00. Retained Model A is false, so this is not a Model A positive. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J06-B-2026-07-10.png>) | false | no | July10 open lies within previous RTH price range and near prior VAL, with outside_both false; source values and current trade profile levels must retain their separate session scopes. |

### R-J07 — Width-conditioned range-break distribution

The source tables report all break classes conditional on range size. Printed percentages such as17.8% double break and the midpoint-retrace share have distinct populations; they are not interchangeable win rates.

The charted H/L/EQ and width are coherent, but the reported event is just whether the final AM class is both. It does not reproduce the required width-bin and balance-conditioned table.

**Source references:** [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [TBR p.30 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i1.png>); [TBR p.30 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i2.png>); [TBR p.30 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i3.png>); [TBR p.30 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p030-i4.png>).

**Code to change:** [sessions.py::build_session](</workspace/implementation/src/trading_research/research/phase1_live/sessions.py:147>), [family_open.py::build_open_table](</workspace/implementation/src/trading_research/research/phase1_live/family_open.py:142>), [recipe_score.py::_preds.j07](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:514>), [recipe_score.py::_stats](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:42>).

**Build steps:**

1. Compute W=H69-L69 and width_pct=100W/C08:59 using a complete6–9 box and valid final construction close. Keep the09:30-denominator variant separate.
2. Assign the documented nonoverlapping bins with explicit lower-inclusive/upper-exclusive boundaries; carry the source-versus-named provenance of the bin edges and balance-body rule.
3. Cross-tab high-only,low-only,both,neither on completed one-minute closes09:30–12:00 by width bin, with counts, missing sessions and conditional denominators. Include relative-prior-RTH width and balance as separate dimensions.
4. Replace the single j07 boolean headline with the requested distribution. Do not import source percentages as priors or thresholds; recompute them from the audited sample.

**Acceptance checks:**

- July10,2026 contributes to both; January28,2026 contributes to low-only, in their respective width bins.
- Each eligible session contributes exactly once and each bin's four counts sum to its denominator.
- A wick without a completed close beyond an edge cannot change the close-break class.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J07-A-2026-07-10.png>) | true | yes for double-break outcome | July10 box W116.50, both high and low receive AM breaks. Source asks all path frequencies conditional on width, not this single binary probability. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J07-B-2026-01-28.png>) | false | no for double-break outcome | Jan28 W71.50, lower break only; upper H26326.75 never reached in AM. Width bins and all four path classes are required. |

### R-J08 — PM reversal in the1.33–1.66 extension area

The author draws a reversal area between1.33 and1.66 widths beyond the appropriate range edge, including PM examples. A band reaction and a rejection of its near line are different events.

The code gates on a broad band reach and then runs a single-line G rejection at1.33, also ORing an independent line flag. It does not track entry into the band, the deepest excursion or failure beyond the far boundary.

**Source references:** [TBR p.21 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i1.png>); [TBR p.21 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i2.png>); [TBR p.21 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i3.png>); [TBR p.21 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p021-i4.png>); [XF p.19 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i1.png>); [XF p.19 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i2.jpeg>); [XF p.47 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p010-i1.jpeg>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [formulas_jumbo.py::band_touch](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:62>), [recipe_score.py::_preds.j08](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:517>).

**Build steps:**

1. Keep exact high-side band[H+1.33W,H+1.66W] and low-side band[L-1.66W,L-1.33W]. Store near/far relative to approach direction, not sorted-price aliases that reverse the low side.
2. Run the PM observation on12:00–16:00 with an explicit formation/eligibility cutoff. Capture the first actual overlap with the band, excursion within/beyond it and subsequent exit toward the box.
3. Retain the strict G-at1.33 calculation as a separate named line variant. Do not label it the band reaction. The author does not publish a universal numerical overshoot/rejection threshold, so a newly quantified band rule must be named or left unresolved.
4. Return conditional reversal, continuation and ambiguous-order counts per side, with band touches as the denominator. Keep AM and PM outcomes distinct.

**Acceptance checks:**

- The same band bounds must be used by plot, event detector and report; low-side near/far must mirror high-side correctly.
- 2026-07-10's PM band touch without a half-W rejection must not pass the strict G variant.
- 2025-01-28's source-date PM extension episode must remain separate from its morning lower0.5 reversal.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-24](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J08-A-2026-07-24.png>) | true | yes for the named near-line rejection; band rule unresolved | First PM low-side1.33 touch28428.98 is about13:11; price rebounds above28500 and stays above the near line through the local G horizon. Later14:20 breakdown does not invalidate that earlier bounded rejection. Far1.66 boundary28389.71 is a separate test. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J08-B-2026-07-10.png>) | false | no for strict G-at1.33; brief source-area reaction observed | First upper1.33 touch30042.69 around12:53 retreats roughly40points but does not deliver0.5W=58.25points before return/continuation into the band. Code false matches the strict line variant, not a universal absence of source-area reaction. |
| [source-date / 2025-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J08-source-date-2025-01-28.png>) | false | source-area reaction observed; strict line G no | Upper1.33=21613.08 is touched about14:47 and bodies close inside the band before a roughly35point retreat. This is an area reaction in the source example but fails no-close-beyond plus0.5W=76.25point G rules. |

### R-J09 — London reversal model

The October6/7/8/13 source charts start their projected levels at02:00. The derived write-up and FORMULAS instead freeze a00:00–03:00 box. The exact author build start is not pinned by the screenshots alone.

The implemented00–03 box includes an extra hour of price and changes H/L, EQ, width and every projection. Code-positive London examples therefore cannot certify the authored model.

**Source references:** [XF p.40 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p005-i1.jpeg>); [XF p.40 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p040-i2.jpeg>); [XF p.41 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p041-i1.jpeg>); [XF p.41 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p041-i2.jpeg>); [FIND p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p004-i1.jpeg>); [FIND p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p005-i1.jpeg>).

**Code to change:** [clocks.py::CLOCKS](</workspace/implementation/src/trading_research/research/phase1_live/clocks.py:32>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.j09](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:520>), [FORMULAS.md::R-J09](</workspace/planning/phase-1-live/FORMULAS.md:777>).

**Build steps:**

1. Stop the faithful London row pending an authoritative clock setting. Preserve00–03 under an explicit named clock ID, with the disagreement and source screenshots linked.
2. Once the build start/end are resolved, create a new clock version; calculate H,L,W,EQ and both projection ladders only from that window. Do not adjust levels to force a visual match or silently reuse6–9 widths.
3. Record separate03:00 trade-analogue and06:00 handoff/outcome times shown in the source. These are not proof that the range forms at03:00.
4. Reuse the resolved reversal variant from J01 with chronological touch/confirmation, keeping London-specific prints and thresholds separate. Regenerate all dependent tables under a new cache identity.

**Acceptance checks:**

- Overlay the2025-10-08 source-date implementation against the native figure: projection start must match02:00 after the clock is resolved.
- No pre-freeze signal may depend on later construction bars.
- May26,2026 remains a valid00–03 named-code example only, and July10 a code negative; neither is an authored-clock certification.

**Chart decision needed:** The native October screenshots project from02:00, while FORMULAS says00–03. The screenshots do not establish the exact build start. Which saved indicator clock setting produced those charts?

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-05-26](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J09-A-2026-05-26.png>) | true | cannot-tell source clock conflict | May26 code00–03 box29845.25–29782.50, m05L29751.12; touch around03:30 then return above L. It is a code-clock reversal, not proof of author clock whose lines begin02:00. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J09-B-2026-07-10.png>) | false | cannot-tell source clock conflict; code negative | July10 codeL29775.25 m05L29688.50;03–06 does not reach either m05. Source clock conflict prevents source certification. |
| [source-date / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J09-source-date-2025-10-08.png>) | false | cannot-tell: source/code clock conflict | Code00–03 box H25094/L25026.25 gives lower0.5=24992.38 and upper0.5=25127.88; neither is touched03–06. Source projections already exist from02:00 on the reviewed October chart, so a03:00 freeze cannot reproduce its geometry. |

### R-J10 — Remaining overnight/prior-session draws after reversal

The source manages a confirmed reversal toward remaining references and may exit at a midpoint rejection. A reference's scope and whether it remains clean at the decision matter; a final-AM nearest price is not an entry-time draw.

The producer chooses direction from the final path, treats09:30 as the fire time and does not apply the existing untouched-candidate logic. Whole-AM target reach can precede the supposed reversal entry.

**Source references:** [TBR p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p016-i1.png>); [TBR p.17 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p017-i1.png>); [TBR p.17 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p017-i2.png>); [XF p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p003-i1.png>); [XF p.26 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p026-i1.jpeg>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::j10_draw](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:218>), [recipe_score.py::_preds.j10](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:535>).

**Build steps:**

1. Require a valid J01/J05 reversal or retrace event with explicit confirmation time; source-conflicted parent variants remain unscored.
2. For every candidate save price, source session, side and all touches after formation. At entry filter to references ahead of the trade and still eligible under that reference's retirement rule. Do not retire prior RTH extremes merely because ETH traded through them; J19 explicitly preserves them.
3. Choose the nearest eligible draw using entry-time information. If no candidate exists, record no-target rather than defaulting to an arbitrary high/low.
4. Measure first target overlap only after confirmation and before the stated horizon. Report entry-to-draw distance and intermediate EQ/OP rejection as separate management observations.

**Acceptance checks:**

- On2026-07-10 distinguish LondonH29948.75, AsiaH29963.50 and priorRTHH29993.50, with separate touch times.
- An earlier target visit cannot satisfy a later entry. Modifying post-entry extremes cannot change the chosen draw.
- For2026-01-28, lower references reached during the downtrend cannot validate a previously selected upper London draw.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J10-A-2026-07-10.png>) | true | cannot-tell full recipe | July10 m05H29946 nearly coincides with LondonH29948.75; AsiaH29963.50 is reached09:52 and later11:25, PDH29993.50 remains unreached before noon. Retained true has no per-candidate untouched-at-entry proof. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J10-B-2026-01-28.png>) | false | no under current selected draw | Jan28 EQ bounce remains below LondonH26349; lower Asia/PDH references are later reached during the downtrend. A single nearest draw chosen from future path cannot represent both chronologies. |

### R-J11 — SessionStat mean/median/minimum-average boundaries

Settings show selectable sessions, mean and median levels, minimum-average levels and projections. The charts draw distinct asymmetric mean/median bands. The full author calculation, especially minimum-average, is not published.

The retained approximation draws a09:00 anchor and mean excursion boundaries. It omits the complete source band geometry and labels the resulting reach as source-faithful. A code reach alone cannot validate the proprietary map.

**Source references:** [SS p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p004-i1.png>); [SS p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p004-i2.png>); [SS p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p004-i1.png>); [SS p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p006-i1.png>); [SS p.6 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p006-i3.png>); [SS p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p009-i1.png>); [SS p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p009-i2.png>); [SS p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/SessionStat+-p009-i3.png>); [SS p.10](</workspace/sources/documents/jumbo/SessionStat+.pdf>); [XF p.19 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i1.png>); [XF p.19 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i2.jpeg>); [XF p.45](</workspace/sources/documents/jumbo/xfcmg2.pdf>).

**Code to change:** [family_env.py::build_env_table](</workspace/implementation/src/trading_research/research/phase1_live/family_env.py:26>), [recipe_score.py::_preds.j11](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:523>), [FORMULAS.md::R-J11](</workspace/planning/phase-1-live/FORMULAS.md:787>).

**Build steps:**

1. Keep env.ss.avgHL60 explicitly named as an approximation. For prior60 completed09–12 sessions store u=H-O and d=O-L, then U=O_today+mean(u),L=O_today-mean(d). Save exact sample dates and prior-only inclusion.
2. Store median variants separately using median(u/d). If drawing the mean–median area, its bounds are min/max of those two independently computed levels; do not label the mean line itself a source band.
3. Do not call min(mean(u),mean(d)) the author's minimum-average algorithm. Preserve it under a named estimator until the source formula is available. Session selection, midnight reset and projections must be explicit parameters.
4. Split reach of upper/lower, mean/median/minimum-average, and any subsequent rejection. Change faithful flags and documentation; do not infer an exact author formula from a handful of boundary prices.

**Acceptance checks:**

- Use the2026-07-06 source-date chart to document the source upper band roughly30033–30078 and lower29730–29836; compare like session/contract/settings before numerical certification.
- July10 and August11 code examples must remain reach/no-reach examples of the named mean estimator only.
- Changing today's later09–12 bars must not move today's frozen prior-sample boundaries.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J11-A-2026-07-10.png>) | true | cannot-tell proprietary map; code yes | July10 code ss_hi29964.87 reached around09:54 and11:25; ss_lo29614.47 unreached. No mean/median shaded source bands exist in this implementation. |
| [B / 2026-08-11](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J11-B-2026-08-11.png>) | false | cannot-tell proprietary map; code no | Aug11 code boundaries30002.28/29599.97 both unreached; source settings and native mean/median boundaries cannot be certified from one-sided rolling means alone. |
| [source-date / 2026-07-06](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J11-source-date-2026-07-06.png>) | unscored on this date | gap: no retained bars on source date | The source depicts upper30033–30078 and lower29730–29836 areas. The retained one-minute input and session rows have no July6 window, so the plotted gap cannot compare those exact bands; the two other dated code charts show only the named envelope approximation. |

### R-J12 — P-zone confluence and the low-to-open path

The January2,2026 figure and its table describe a retrace from low to open (Low→Open). The visible low is below the range open. FORMULAS converts that path into low>open, an inequality. P-zones additionally use unpublished learning/scaling settings; they are not the same object as fixed percentile excursion envelopes.

The only retained positive combines an approximated T1 reach, Model A and a separate m05 rejection with no common event sequence. Its source inequality is wrong, and its percentile boundaries are not validated author zones.

**Source references:** [XF p.29 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p029-i1.jpeg>); [XF p.29 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p029-i2.jpeg>); [XF p.30 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p030-i1.png>); [XF p.39 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p039-i1.jpeg>).

**Code to change:** [family_env.py::build_env_table](</workspace/implementation/src/trading_research/research/phase1_live/family_env.py:26>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.j12](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:526>), [FORMULAS.md::R-J12](</workspace/planning/phase-1-live/FORMULAS.md:796>).

**Build steps:**

1. Stop the faithful row and correct the source transcription from low>open to a low-to-open retracement description. Do not replace it with a newly invented trigger; retain the author's unspecified conditions as unresolved.
2. Remove the impossible fixture in which the06:00 box open lies below its own low. Enforce L≤O≤H for every box fixture and real observation.
3. Keep pz.approx.A as a named research envelope only: prior sample, anchor, p50/p75 near/far T1 boundaries and p95/p99 T4 boundaries must be separately identified. Do not treat the central p50 lower-to-upper span as one authored P-zone.
4. A future faithful implementation needs the author's learning window, percentile/volatility scaling, alignment mode, invalidation and session settings. Require those inputs before implementing; then join confluence, entry confirmation and target reach by one chronological event ID.

**Acceptance checks:**

- The2026-01-02 native table must be transcribed as Low→Open; no fixture may assert that the actual low exceeds the opening price.
- October18,2024 is retained as a diagnostic of the approximate union, not a source P-zone positive.
- T1 reach must distinguish near-band entry from the far p75 edge and must occur after the same setup's confirmation.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2024-10-18](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J12-A-2024-10-18.png>) | true | cannot-tell; source conflict | Oct18 only retained positive: EQ20452.12, box20418.50–20485.75, range open20430; code upper T1 near20529.75/far20590.50. Source low→open path was converted into low>open inequality. Approximated p50/p75 envelopes are not authored P-zones. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J12-B-2026-07-10.png>) | false | cannot-tell; source conflict | July10 code T1 near29936.12 and lower29737.25 can be reached while whole multi-gate flag is false. This does not validate author P-zone band positions or wrong low>open reading. |
| [source-date / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J12-source-date-2026-01-02.png>) | false | cannot-tell: source Low→Open condition conflict | Continuous6–9 H25742.75/L25679.25/OP25730.25 makes low>open false. Lower0.5=25647.50 is tested near09:40, followed by a rally above25774.50; source has the same low→open context. The documented inequality and source/proprietary P-zone construction remain unresolved. |

### R-J13 — Expected-volatility range

The source shows an AM EV range, asymmetry and additional EV projections as contextual boundaries. It does not publish the complete estimator. EV+50% is distinct from6–9+0.5W.

The producer uses09:30 open plus/minus prior60-session mean excursions, while the scorer additionally requires in_value. This is a named approximation with an extra gate; its touches are not evidence of exact authored EV levels or confirmation.

**Source references:** [XF p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p003-i1.png>); [XF p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p007-i1.png>); [XF p.19 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i1.png>); [XF p.19 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p019-i2.jpeg>).

**Code to change:** [family_env.py::build_env_table](</workspace/implementation/src/trading_research/research/phase1_live/family_env.py:26>), [recipe_score.py::_preds.j13](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:529>), [FORMULAS.md::R-J13](</workspace/planning/phase-1-live/FORMULAS.md:806>).

**Build steps:**

1. Relabel env.ev.mean60 and median60 as named approximations. Persist U=O09:30+mean(HAM-OAM), L=O09:30-mean(OAM-LAM), using only the declared prior sample and no current-session outcome.
2. Keep the actual anchor separate from EQ69. Store mean and median upper/lower boundaries independently and label EV-derived projections with their own width, never with6–9 projection names.
3. Report reach of each boundary from an actual overlap after09:30; make in_value an explicit conditional variant with its own denominator, not an undisclosed ingredient of the base event.
4. Leave the exact author EV formula cannot-tell until supplied. A quantitative reaction variant may use a named confirmation rule, but must not inherit the author's proprietary fidelity label.

**Acceptance checks:**

- 2025-10-08 reaches the mean upper approximation;2026-07-10 reaches a median lower boundary while missing the mean boundaries. Those outcomes must stay distinct.
- Changing today's later prices cannot change frozen levels.
- No source-level certification may be obtained by fitting the prior-window length to make one screenshot align.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J13-A-2025-10-08.png>) | true | cannot-tell unpublished EV; code yes | Oct8 EV mean upper25153.79 passed near09:47; mean lower24970.71 never reached. The chart establishes approximate envelope reach only. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J13-B-2026-07-10.png>) | false | cannot-tell unpublished EV; code no | July10 mean upper30005.90/lower29653.80 not reached in AM while lower median29702.25 is wicked through10:30. Mean and median variants produce different outcomes. |

### R-J14 — Small-body/high-volume candle confirmation

The native settings panel visibly supplies body threshold0.6, volume multiplier1.5 and14-period volume average; FORMULAS says the first two are unprinted and defaults body ratio to0.3. The source says the candle can signal continuation or reversal and needs location/context.

The3m SMA resets at09:30, so the first14-bar baseline is only available at10:12, excluding the central09:40–09:50 confirmation window. The score counts a candle-at-level without the requested subsequent response.

**Source references:** [TBR p.31 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p031-i2.png>); [TBR p.31 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p031-i3.png>); [TBR p.31 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p031-i4.png>); [TBR p.35 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i1.png>); [TBR p.35 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i2.png>); [XF p.27 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i1.jpeg>); [XF p.27 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i2.png>); [XF p.44 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p044-i1.jpeg>); [XF p.45](</workspace/sources/documents/jumbo/xfcmg2.pdf>).

**Code to change:** [formulas.py::absorption_candle_at_levels](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:90>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.j14](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:532>), [FORMULAS.md::R-J14](</workspace/planning/phase-1-live/FORMULAS.md:816>).

**Build steps:**

1. Correct source parameter provenance to the visible settings. Keep0.3 as a named variant rather than silently treating it as the authored default; do not proceed with a faithful parameter claim until this document conflict is resolved.
2. Resample continuous complete candles on a fixed clock and warm the14-bar average from candles preceding09:30. For a trailing-excluding-current variant, SMA_i=sum(V[i-14:i])/14; the current candle and centered future bars are excluded.
3. Evaluate body_ratio=abs(C-O)/(H-L) with an explicit zero-range policy; high-volume condition V≥1.5SMA. Save close-time availability, chart timeframe and source/variant parameters.
4. Join the candle to a specific6–9 level interaction, side and subsequent reject/continuation event. Add the source's newer imbalance/isolation branch only when its actual formula/input is available; candle volume alone is not passive absorption.

**Acceptance checks:**

- A09:42 three-minute candle must have a valid prior14-candle baseline when earlier bars exist.
- A body ratio0.45 must differ between0.3 and0.6 variants; the same source figure cannot validate both.
- A small high-volume candle followed by continuation must not automatically count as a reversal.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-25](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J14-A-2026-08-25.png>) | true | cannot-tell: source/default conflict | August25 reverses from the AM upper area and crosses below the lower 0.5 later; the volume panel uses actual three-minute bins. Its prior-14 baseline becomes available only after the warmup around10:12. Source settings printed0.6/1.5 differ from the scored0.3/2.5 defaults, so the retained positive cannot certify the stated source variant. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J14-B-2026-07-10.png>) | false | cannot-tell: source/default conflict | July10 has a conspicuous10:30 volume spike but it is less than2.5 times the available prior-14 three-minute baseline; retained false is plausible for that named detector. Missing warmup at09:40 and source/default parameter conflict prevent source-event certification. |

### R-J15 — Large executions at a framework level

The source combines a large print with range location, price response and profile/footprint context. A displayed bubble is an executed trade; manual shelf highlighting is not a trading box, and a large aggressive print alone does not establish passive absorption.

The London02–05 branch compares its trades with future06–09 m05 levels; AM and London thresholds are pooled into one flag. The predicate needs no matched response/confirmation and omits the developing profile context.

**Source references:** [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [XF p.27 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i1.jpeg>); [XF p.27 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p027-i2.png>); [XF p.44 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p044-i1.jpeg>); [FIND p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [FIND p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [family_tape.py::_big_at](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:219>), [recipe_score.py::_preds.j15](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:541>).

**Build steps:**

1. Use only levels already formed when a trade occurs. London events require their resolved London references; AM6–9 levels are available from09:00. Do not back-apply the future AM range to02–05 trades.
2. Retain execution timestamp, price, size, aggressor side, instrument and threshold variant. Keep NQ/MNQ and London/AM thresholds explicit rather than pooling contracts or source illustrations.
3. For each at-level print create an event joining the same level, side, price-response window and available confirmation. If the source's passive-absorption mechanism is not quantitatively specified, preserve the print observation and label the formal confirmation a named variant.
4. Carry opening cells, prior RTH/ETH value and developing profile cutoff as separate confluence fields. Score the full stated confirmation row; report print presence separately.

**Acceptance checks:**

- A02:30 print cannot use a level that changes when08:00 bars are changed.
- A large buy with falling price is not automatically a bullish confirmation; preserve the opposed price/flow example from the sources.
- The302-lot June8 print and preceding low footprint must be separate timestamped observations, not one instantaneous box signal.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-03-09](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J15-A-2026-03-09.png>) | true | cannot-tell: missing matched confirmation | AM100+ print near24400 sits close to EQ24399.62, while London75+ prints occur around04:30 before the plotted6–9 levels are known. Print presence alone does not establish source absorption or a reversal. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J15-B-2026-07-10.png>) | false | no for the current at-level print detector | AM100+ prints near29960 and29890 do not coincide with EQ29829.50 or either0.5 projection within the scored tolerance; the London subset is empty. That explains retained false without certifying broader source confirmation. |

### R-J16 — Developing RTH VP and delta-profile confirmation

The June8 panels combine EQ, a profile taper/shelf, negative flow near the low and subsequent price recovery. The RTH profile is developing; the visible final histogram cannot be assumed to have existed at the first low. The35% footprint filter is printed; median and excursion cutoffs are named approximations.

The implementation aggregates the entire09:30–16:00 profile, compares buy/sell near EQ with full-RTH medians and supplies a hardcoded two-tick excursion. It does not compute the stated touch-window response or taper.

**Source references:** [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [FIND p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [FIND p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_jumbo.py::j16_two_sided_at_eq](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:259>), [recipe_score.py::_preds.j16](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:544>).

**Build steps:**

1. At each EQ interaction build buy,sell,total and signed-delta bins from executions available at that timestamp. Keep unknown aggressor volume out of signed delta and in its own quality field.
2. Calculate the named touch-window buy/sell totals within EQ±2ticks, with medians frozen from session-so-far bins at the specified cutoff. Derive actual excursion from the observed price path; remove the hardcoded2.
3. Implement taper as a separately named shape measurement with explicit price ordering, bin widths and pre-event cutoff. Do not equate a large local volume bar, a shelf and a delta taper.
4. Apply the source top35% transaction filter using a declared causal size distribution. Save filtered and unfiltered results and join them to the same price response; replace the whole-day two-sided-presence score.

**Acceptance checks:**

- Replaying only data available at a touch must reproduce that event's profile and flags.
- A late15:00 volume burst must not alter a09:45 confirmation.
- An EQ crossing by20points must fail the named≤2tick-excursion criterion even if both sides traded heavily.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-31](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J16-A-2026-08-31.png>) | true | cannot-tell as-of confirmation | Aug31 EQ29433 repeatedly crossed; final RTH volume bulge below it is visible. Current positive pools buy/sell over all RTH and hardcodes a two-tick excursion, so it cannot prove two-sided absorption at the early touch. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J16-B-2026-07-10.png>) | false | cannot-tell as-of confirmation | July10 final profile major volume moves far above EQ29829.50; code negative uses full-RTH per-price baselines. Need individual touch-window buy/sell and subsequent response, not final VP. |

### R-J17 — Profile shelf/LVN confluence under range references

The cited June8 example uses a developing RTH VP and delta profile with a manually highlighted taper/shelf near6–9 EQ. FORMULAS substitutes a frozen6–9 trade profile. That changes the profile population and cannot reproduce the cited confluence.

The code's node detector drops zero bins, identifies unsmoothed local extrema and treats symmetric proximity as 'under'. Its6–9 profile cannot contain nodes at its own external m05 projections. The source shelf is not a universal computed rectangle.

**Source references:** [XF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>); [XF p.24 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p009-i1.jpeg>); [XF p.24 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p024-i1.jpeg>); [FIND p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/jjumbo-findings-p008-i1.png>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_jumbo.py::profile_nodes](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:153>), [formulas_jumbo.py::j17_node_under](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:267>), [FORMULAS.md::R-J17](</workspace/planning/phase-1-live/FORMULAS.md:61>).

**Build steps:**

1. Stop the source-faithful6–9-profile claim. Preserve that profile as a named variant and correct the source scope to developing RTH for the cited image.
2. Specify the desired profile input before changing node geometry: instrument, session start, as-of timestamp, one-tick grid and treatment of zero bins. Preserve all ticks between low and high.
3. Keep HVN, LVN, taper, shelf and ledge as distinct measurements. Numerical smoothing, prominence, gradient and band thickness are source-unspecified and must be named parameters; do not invent a universal author detector from the manual highlight.
4. Use directional geometry when 'under' means below the traded level, and explicit band overlap for shelf confluence. Score a matched level interaction/response separately from mere proximity; do not force impossible external nodes into the6–9 support.

**Acceptance checks:**

- Jan10,2025's frozen6–9 sparse neck nearEQ21208.75 remains a named-code proximity example only.
- No profile node can lie outside the profile's actual price support unless it is explicitly a different historical profile.
- A late-developed shelf cannot validate an earlier reaction without an as-of replay.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J17-A-2025-01-10.png>) | true | yes for code node proximity only | Jan10 6–9 executed VP has sparse neck near EQ21208.75 between upper/lower volume distributions; source uses RTH developing shelf plus delta. The two profiles have different clocks and meanings. Final rendering verified: nearest LVN21208.5 and shelf21205 flank EQ21208.75; the VP separately marks all42matched LVNs and5shelf edges, and the JSON retains every price. The plotted price labels remain readable. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J17-B-2026-07-10.png>) | false | no for code proximity only | July10 EQ29829.50 sits near a volume cluster on frozen6–9 VP; m05 levels are outside its support, so that profile cannot locate a node at either external projection. Final rendering verified: no matched LVN/shelf markers for EQ29829.5 or external mean levels; the actual06–09 VP and price zoom remain visible. |

### R-J18 — Three-candle order block and rejection block

The OB is the full second candle's H/L, confirmed by C3 closing beyond C2. The rejection block is the sweep candle's wick. Source pages distinguish midpoint entry, midpoint stop and wick-extreme stop; p29's conservative-stop prose conflicts with the drawn wick-low stop.

The3m m05 OB branch has the correct full-C2 geometry, but the family omits2m/5m, other source locations, the rejection block and stop/entry variants. The source stop contradiction must be resolved without changing the OB into a wick-only box.

**Source references:** [TBR p.27 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p027-i1.png>); [TBR p.27 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p027-i2.png>); [TBR p.28 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p028-i1.png>); [TBR p.28 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p028-i2.png>); [TBR p.29 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p029-i1.png>); [TBR p.29 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p029-i2.png>); [TBR p.29 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p029-i3.png>).

**Code to change:** [formulas_jumbo.py::j18_ob_bull](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:274>), [formulas_jumbo.py::j18_ob_bear](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:284>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.j18](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:550>), [FORMULAS.md::R-J18](</workspace/planning/phase-1-live/FORMULAS.md:70>).

**Build steps:**

1. Keep the existing OB geometry: bullish C2.low<C1.low and C3.close>C2.high; bearish mirror. Block=[C2.low,C2.high], known at C3 close. Do not redefine it as a wick to match the separate rejection-block illustration.
2. Create separate2m,3m,5m variants with fixed clock-aligned complete candles and separately enumerated reversal locations. Save C1/C2/C3 OHLC and times, level ID and sweep distance.
3. For rejection blocks store only the wick interval; require the stated close beyond the whole sweep candle before eligibility. Preserve the source disagreement about conservative stop as a blocked parameter choice, not a guessed fix.
4. Separate formation, market-confirmation entry and later midpoint-limit fill. A source arrow at a proposed midpoint does not prove a later retest/fill. Report each stop placement and invalidation outcome separately after entry.

**Acceptance checks:**

- 2026-07-21 should form the existing bullish3m m05 OB around10:18; the plotted block must use the exact C2 range.
- 2026-07-10 is negative only for that implemented branch, not all missing timeframes/locations.
- A C3 confirmation without a subsequent midpoint touch must not count as a midpoint-limit fill.

**Chart decision needed:** TBR p29 labels the conservative rejection-block stop at the midpoint in prose but draws it at the wick low. Which stop placement should the faithful rejection-block variant use?

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-21](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J18-A-2026-07-21.png>) | true | yes for 3m m05 OB formation | July21 bullish three-candle OB forms after lower m05 test near10:15, with C2 full H/L around29063.75–29104. Source OB uses full C2 candle; rejection block uses only wick and is a separate missing branch. Zoom updated to formation. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J18-B-2026-07-10.png>) | false | no for implemented 3m m05 OB | July10 does not form the implemented three-candle m05 condition; it can still have other timeframe or level setups absent from this predicate. |

### R-J19 — Prior RTH extremes and higher-timeframe imbalance draws

The author explicitly uses prior09:30–16:00 price action, preserves those extremes through ETH sweeps and waits for RTH direction. M15/H1 first-presented FVGs are additional draws. The exact directional rule is not published.

Direction can be selected from a final-AM path and reach is reduced to AM extrema against a price. A level already below the open can satisfy a one-sided comparison without a later actual touch. The HTF target family is missing.

**Source references:** [TBR p.33 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p033-i1.png>); [TBR p.33 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p033-i2.png>); [TBR p.33 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p033-i3.png>); [TBR p.34 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p034-i1.png>); [TBR p.34 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p034-i2.png>); [TBR p.35 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i1.png>); [TBR p.35 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p035-i2.png>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::j19_pd_touch](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:300>), [formulas_jumbo.py::j19_htf_fvg](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:309>), [recipe_score.py::_preds.j19](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:553>).

**Build steps:**

1. Build prior RTH H/L from the actual prior trading session, respecting early close and complete coverage. Preserve them through ETH sweeps as required by the source.
2. Keep first6–9-close-break and first15m-RTH-close direction as separate named variants, each with its real completion timestamp. Never use final path class as the opening direction.
3. Require an actual overlap/touch after direction is known, handling approach from above or below correctly. Store target side and first touch by noon and by RTH close separately.
4. For M15/H1 FVGs use complete clock-aligned RTH candles and prior-only formation data, with distinct near/mid/far fill observations. Do not substitute a5m09:00-hour gap or invent a missing imbalance input.

**Acceptance checks:**

- Jan28,2026 priorRTHH26114.25 is reached from above near11:50; a high≥level test alone is insufficient.
- July10,2026 misses both prior RTH extremes before noon.
- An ETH sweep must not retire these references, and an HTF gap cannot be available before its third candle closes.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J19-A-2026-01-28.png>) | true | yes for observed PDH touch, direction unresolved | Jan28 prior RTH high26114.25 is reached from above near11:50 after an early low-side break. Source says retain prior RTH extremes despite overnight sweeps; it does not state the future-path direction rule used here. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J19-B-2026-07-10.png>) | false | no for AM extreme reach | July10 prior RTH high29993.50 and low29614.50 remain outside AM extremes. Actual negative does not validate omitted 15m/H1 FVG and later RTH target rows. |

### R-J20 — Delayed cycle2 on10:00 release days

The source describes a later reversal after10:00 news, not simply a later first projection touch. It does not define an exact release universe. FORMULAS' old 'no10:00 calendar' description is stale: the current code consumes release_1000_dates.json. The existing JSON retains release names/IDs but the loader reduces them to a date set. FRED returns dates, not intraday times ([API documentation](https://fred.stlouisfed.org/docs/api/fred/release_dates.html)); its sample Michigan dates match the university's final-release calendar, but the JSON omits preliminary releases such as2024-01-19 and2024-02-16 ([official dates](https://data.sca.isr.umich.edu/fetchdoc.php?docid=75443)). This is incomplete release coverage, not proof that all FRED dates are delayed updates.

The retained39/217 positives measure release-day membership and first m05-touch bin. August25 touches after10:00 and continues down; this is not a demonstrated delayed reversal.

**Source references:** [TBR p.18 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p018-i1.png>); [FIND p.11](</workspace/sources/documents/jumbo/jjumbo-findings.pdf>).

**Code to change:** [family_levels.py::load_red_folder](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:51>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.j20](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:538>), [FORMULAS.md::R-J20](</workspace/planning/phase-1-live/FORMULAS.md:89>).

**Build steps:**

1. Retain and audit the existing calendar's release names/IDs, source, time zone and historical vintage instead of reducing all metadata to a date set. FRED dates alone do not provide10:00 timestamps. Explicitly state whether Michigan preliminary releases are included; they are absent from the current file. Do not infer10:00 times from08:30 CPI/NFP or unknown-time FOMC.
2. Join release membership to an independently resolved J01 reversal event. Store first projection touch, failure/confirmation and completed reversal time separately.
3. Report the full reversal-time histogram conditional on the declared release universe versus non-release sessions, with no-reversal and incomplete observations included explicitly. Keep delayed-touch as a separately named diagnostic.
4. Update the stale input-gap description only to the extent supported by the current calendar provenance; do not use the observed price move to decide whether the day had news.

**Acceptance checks:**

- August25,2026 must not pass a reversal outcome solely because m05 is touched after10:00.
- August28's first upper m05 touch around09:42 must remain in the early bin even if the other side is touched later.
- Release-universe changes must change the denominator transparently, with old and new calendar hashes retained.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-25](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J20-A-2026-08-25.png>) | true | no certified reversal; yes delayed-touch diagnostic | Aug25 m05L29250.88 first reached after10:00, then price continues through it to below29150 before rebound. Source is delayed reversal after news; headline counts time of first touch. |
| [B / 2026-08-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J20-B-2026-08-28.png>) | false | no delayed first-touch event | Aug28 upper m05 near29700.88 is touched09:42 in ordinary reversal window; later lower excursion after10:00 is not first touch. Release-day membership alone does not establish causation. |

### R-J21 — News, range condition and target expectations

The source separates low-expectation news conditions, extended overnight ranges, pre-news range-bound conditions and expansive days. The weekday risk table is visual evidence; the width ratio and coded class boundaries are named research definitions.

The producer passes red_folder=False and scores only the extended-width class. It does not implement the other condition populations, their available-at timing or the class-specific target/knockout/re-entry outcomes.

**Source references:** [TBR p.22 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p022-i2.png>); [TBR p.22 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p022-i3.png>); [TBR p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i1.png>); [TBR p.23 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i2.png>); [TBR p.23 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i3.png>); [TBR p.23 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p023-i4.png>); [TBR p.24](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::j21_class](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:317>), [formulas_jumbo.py::j21_targets](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:334>), [recipe_score.py::_preds.j21](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:556>).

**Build steps:**

1. Pass the actual known calendar flags into the condition classifier. Preserve separate CPI,NFP,FOMC,08:30-release and pre-release-in-week fields; do not use a hardcoded false.
2. Calculate the named width ratio before09:30 with the correct prior RTH session. Keep source weekday/risk annotations separate from numerically invented thresholds and retain any unreadable cell as unresolved.
3. Define each class using only its declared available information. A class requiring a break/hold becomes known only after that event, while the final day type stays an outcome.
4. For each class report its specified inner/edge/extension targets and horizons, knockout and re-entry observations. Do not present the percentage of extended labels as the framework's success rate.

**Acceptance checks:**

- Jan10,2025 has a large08:30 move and extended width; either source calendar input and width variant must be individually inspectable.
- July10,2026 is not extended under the named width rule; that says nothing about all other classes.
- A future AM trend cannot retroactively change a pre-open class.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J21-A-2025-01-10.png>) | true | yes extended context | Jan10 large08:30 expansion W327.50 and low-only AM support extended context; code happens to classify by width while red-folder input is passed false. Actual news-conditioned target map is absent. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J21-B-2026-07-10.png>) | false | no extended context under named width rule | July10 W116.50 below prior RTH width; retained extended class false. This does not test other source risk classes or news-week grids. |

### R-J22 — Failure signatures and three failed attempts

The source enumerates no-rejection, momentum, extended-body, timing, extended-move and volume failures, plus three failed reversal attempts at a level. Three consecutive bars touching a level are not necessarily three attempts.

The scorer uses only three near-m05 one-minute bars with small same-bar returns, selected using the final path side. Other failure functions exist but are not part of the predicate.

**Source references:** [TBR p.37](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::j22_three_strike](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:359>), [formulas_jumbo.py::j22_failed](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:383>), [recipe_score.py::_preds.j22](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:559>).

**Build steps:**

1. Track a specific active level and reversal episode from its actual touch, retaining the resolved level-selection rule from J01. Do not choose the side from the final AM class.
2. Define a named attempt state machine: touch, leave the tolerance band, attempted reversal, failure, re-arm after a distinct excursion. Keep repeated bars within one visit in the same attempt.
3. Calculate each source failure signature separately with timestamp and named threshold provenance. For three strikes use the maximum favorable response after each distinct attempt before its failure, not close minus wick on the touching bar.
4. Score the stated failure union only after the relevant signature becomes knowable, and record a later switch-to-single-break as its own event. Keep missing confirmation/volume branches gap rather than false.

**Acceptance checks:**

- One three-minute consolidation spanning three1m bars must count as one visit, not three failed attempts.
- Aug11,2026 has an actual lower0.5 break/continuation; distinguish momentum failure from the producer's counted-bar signal.
- July10's lack of the counted-bar flag must not mean all source failure signatures are absent.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-11](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J22-A-2026-08-11.png>) | true | yes failure signatures; three attempts not proved | Aug11 price breaks below m05L29682 around09:45, sits across/below it and later retests. Counting three one-minute near-level bars is not three failed reversal attempts; momentum/no-rejection branches are separately missing. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J22-B-2026-07-10.png>) | false | no counted three-strike pattern | July10 early m05H29946 is followed by closes above it and then later declines. Code false only says fewer selected bars meet its return test, not that all source failure conditions are absent. |

### R-J23 — Other published time-based range clocks

The manual explicitly lists Asia20:00–20:30, midnight00:00–00:30, London03:00–03:30,6–9,09:30–10:00,10:00–10:30,lunch12:00–12:30 and MOC15:00–15:30 construction windows. Outcome horizons and a common formal rejection rule are named research choices.

The retained recipe rate represents only the midnight box's double-break share. The other clocks have actual geometry but their separate path/ladder/response observations are not represented by that headline.

**Source references:** [TBR p.6](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.7](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i1.png>); [TBR p.13 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i2.png>); [TBR p.13 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i3.png>); [TBR p.13 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p013-i4.png>).

**Code to change:** [clocks.py::CLOCKS](</workspace/implementation/src/trading_research/research/phase1_live/clocks.py:32>), [family_clocks.py::build_clock_table](</workspace/implementation/src/trading_research/research/phase1_live/family_clocks.py:77>), [recipe_score.py::_preds.j23](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:568>), [recipe_score.py::_stats](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:42>).

**Build steps:**

1. Keep one observation per date,clock,side,depth,variant. Calculate H,L,W,EQ,Q25,Q75,opening price and own-width projections from that clock's completed bars.
2. Do not substitute6–9 width for another clock. Preserve the published construction times exactly; label Asia→midnight, midnight→03:00 and other outcome cutoffs as named horizons.
3. Report each clock's four path classes and level-response variants separately. The6–9 family may be linked but not counted twice; midnight's rate must have a midnight-specific name and denominator.
4. Use each clock's coverage, early-close handling and known_at. Missing extension levels such as±2 remain missing until explicitly implemented; do not fabricate them in an audit plot.

**Acceptance checks:**

- Jan10,2025 is a midnight both-side outcome; July10,2026 is not. Neither label stands for all clocks on those dates.
- Each clock's levels remain unchanged if prices after its freeze change.
- All clock rows appear individually with counts summing correctly; no full-day OR may hide a missing clock.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J23-A-2025-01-10.png>) | true | yes midnight both-side outcome | Jan10 midnight box21296.50–21317.50 first extends above then falls below by03:00; all seven other-clock boxes shown. Current score covers only midnight. Own-width projection supplements needed. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J23-B-2026-07-10.png>) | false | no midnight both-side outcome | July10 midnight box29917.25–29948.75 breaks down only by03:00; later RTH/lunch/MOC responses belong to different clock populations. |

### R-J24 — Post-entry excursions and management observations

The source discusses entries, partials/adds, midpoint exits and clock context. This Phase1 row is outcome measurement after a confirmed entry, not simulated P&L or a positive-excursion win rate.

The645/647 rate counts positive MFE from an assumed m05 price using extrema that can precede any touch/entry. It omits the requested multiple horizons, target chronology and valid risk denominator.

**Source references:** [TBR p.8](</workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>); [TBR p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/Time-Based ranges Framework (JJumbo)-p016-i1.png>); [XF p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p015-i1.jpeg>); [XF p.21 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p021-i1.png>); [XF p.26 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p026-i1.jpeg>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::j24_management](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:387>), [recipe_score.py::_preds.j24](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:562>).

**Build steps:**

1. Require a parent setup with actual entry/confirmation timestamp, side and price. Source-conflicted or missing parent events are ineligible, not negative outcomes.
2. For long entries compute MFE=max(0,max(high after entry through horizon)-entry) and MAE=max(0,entry-min(low after entry through horizon)); reverse the signs for shorts. Use execution order or censor same-bar unknown paths.
3. Produce separate09:50,10:00,noon horizons only when entry precedes the horizon. Record EQ touch/rejection, clean edge and1.0/1.33 reaches after entry, and edge-by09:50. A horizon before entry is not applicable.
4. Normalize only by a separately defined positive entry-to-invalidation distance. Remove the MFE>0 headline and any implied win/P&L interpretation; leave partial sizes and trade management simulation out of Phase1.

**Acceptance checks:**

- July10's pre09:49 extremes cannot contribute to an entry made at the later m05 interaction.
- Dec3,2025's first later m05 return near10:34 makes09:50 management not applicable, not a negative MFE trade.
- All reported MFE/MAE values are nonnegative and reproducible from the exact post-entry slice.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J24-A-2026-07-10.png>) | true | cannot score management without confirmed entry | July10 retained positive uses whole09:30–09:50 extrema around an assumed m05 price. Pre-entry high/low are visible before m05 touch09:49. A positive excursion is not the stated management outcome. |
| [B / 2025-12-03](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J24-B-2025-12-03.png>) | false | not eligible for documented morning entry | Dec3 opening09:30 prices are far below m05L25576.50 after09:00 decline; first later m05 return is around10:34. Negative MFE before09:50 from an unentered level is an invalid outcome row, not a losing setup. |

### R-J25 — Trend-day retraces to confirmed swing midpoints

The tweet describes clean swing-mid retraces toward the January4 gap. The2-left/2-right5m fractal and trend definition are explicitly named observations, not an authored entry algorithm. FORMULAS' numeric fixture is internally wrong:105 is not100+0.5×20.

The producer scans1m data, pairs the first high and first low independently, ignores their confirmation order and back-applies the midpoint over the AM. Its hold flag is not the documented G rejection; the zero rate does not validate the observation.

**Source references:** [XF p.26 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/xfcmg2-p026-i1.jpeg>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::j25_fractal_swings](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:423>), [formulas_jumbo.py::j25_mid_retrace_hold](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:436>), [FORMULAS.md::R-J25](</workspace/planning/phase-1-live/FORMULAS.md:126>).

**Build steps:**

1. Resample complete5m candles on the fixed RTH clock. A strict2-left/2-right pivot at index i becomes known at the close of i+2, not at i.
2. Pair chronological alternating pivots into actual swings: low→next high for an up swing, high→next low for a down swing. Define handling of repeated same-side pivots explicitly; never combine independently first extrema.
3. Create midpoint=(swing_high+swing_low)/2 only when both endpoints are confirmed. Detect later touch and the named rejection/close-through sequence; retain swing width versus6–9 width as explicit separate R choices.
4. Keep trend-so-far eligibility separate from final trend-day outcome. Correct the fixture: with midpoint100,R20 a0.5R upward close target is110;105 is a failure for that threshold. Replace all forced or disconnected pass checks with meaningful event fixtures.

**Acceptance checks:**

- No midpoint may appear on the plot before its second endpoint's confirmation time.
- Jan28,2026's independently chosen midpoint26250.88 must not be used from09:30.
- July10's both-side AM fails the final trend-only classification; a future trend label cannot alter an earlier pivot.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J25-A-2026-01-28.png>) | false | cannot-tell stated swing variant | Jan28 named code midpoint26250.88 comes from independently first swing H26288 and L26213.75 and is drawn from09:30 before both are confirmed. Trend contains later retraces but no causal paired-swing event was scored. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-J25-B-2026-07-10.png>) | false | no trend-only condition | July10 is both-side AM; initial independent midpoint29908.62 back-applies future pivots and cannot be a confirmed trend-swing reference at09:30. |

### R-G01 — NYAM sweep and failed breakout

The pack explicitly fixes09:00–10:00 and entry logic after10:00: sweep, fail back inside, then trade toward the opposite side. Five-minute confirmation is sourced; two ticks and30minutes are named research defaults. The original HIS CHART pixels are unavailable.

Actual NYAM geometry is correctly separated from Jumbo. However family_fail uses any strict beyond-edge wick instead of the documented two-tick depth, groups five observed rows rather than verified clock bars, and checks five-minute block starts against the deadline. It stores no matched stop/target episode.

**Source references:** [GB pack L28](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:28>); [GB pack L209](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:209>); [GB pack L395](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:395>).

**Code to change:** [family_fail.py::_failback](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:23>), [family_fail.py::build_fail_table](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:58>), [recipe_score.py::_preds.g01](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:571>), [grid.py::failback_wick_c5](</workspace/implementation/src/trading_research/research/phase1_live/grid.py:131>).

**Build steps:**

1. Freeze H and L from complete09:00–10:00 data, with known_at10:00. Retain the specified one-second construction or label the current one-minute equivalent; verify equal extrema where both feeds exist.
2. Replace the two divergent fail-back engines with one event routine parameterized by depth, confirmation interval and timeout. A high sweep requires high≥H+2 ticks; a low sweep requires low≤L−2 ticks for the named default. Keep raw touch/sweep observations separate.
3. Use wall-clock five-minute bars whose close is known at the interval end. Include the sweep-containing bar when its later close is causally ordered after the wick; when intrabar order matters, use available executions or return ambiguous. Deadline is actual close_time−sweep_time≤30minutes.
4. Return side, sweep extreme, first inside confirmation, invalidation and opposite-edge reach at12:00/16:00. Report failures conditional on eligible sweeps and targets conditional on confirmed failures. Preserve a separate day-level any-failure statistic.

**Acceptance checks:**

- July10,2026 low sweep10:32 and close known10:40 must pass; October8,2025 first high sweep with no close-back by10:30 must fail.
- A one-tick overshoot must fail the two-tick variant; a bar starting29minutes after a sweep but closing34minutes after must miss the30-minute deadline.
- Removing a minute must not shift five-minute alignment or silently create a complete confirming bar.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G01-A-2026-07-10.png>) | true | yes for the stated sweep/fail sequence | Frozen09–10 H29968.50/L29790.50. First below-low wick is10:32; five-minute inside close29881.25 is known10:40, after the block starts10:35. The low failure precedes an eventual opposite-high reach near11:25. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G01-B-2025-10-08.png>) | false | no within the named30-minute window | Price breaks above H25183.75 at10:00 and holds above for the next30minutes; return near10:50 is too late for the first-sweep rule. A sweep by itself is not failure. |

### R-G02 — Asia failure and TDO confirmation

The pack describes a roughly20:00–00:00 Asia rectangle, AS.L, and post-midnight sweep/failure; TDO is the midnight open. This chart-derived clock remains unverified without the original image. The06:00 outcome cutoff and30-minute expiry are named defaults.

The code draws its own four-hour Asia box, but inherits the zero-depth/grouped-row fail-back defects. Its Asia-failure flag is not linked to the later TDO five-minute close or opposite-edge outcome.

**Source references:** [GB pack L24](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:24>); [GB pack L35](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:35>); [GB pack L427](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:427>).

**Code to change:** [clocks.py::CLOCKS](</workspace/implementation/src/trading_research/research/phase1_live/clocks.py:32>), [family_fail.py::_failback](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:23>), [family_fail.py::build_fail_table](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:58>), [recipe_score.py::_preds.g02](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:574>).

**Build steps:**

1. Retain20:00–00:00 as the pack-derived candidate clock and mark its provenance unresolved until the cited chart can be inspected. Freeze its H/L at00:00 independently of the Jumbo20:00–20:30 range.
2. Apply the repaired G01 event routine over00:00–06:00 with mirrored high/low sweeps. Store one episode per distinct visit; later independent sweeps require a defined reset rather than being lost behind the first failed attempt.
3. Attach the00:00 opening print and optional five-minute close through TDO to the same sweep episode, preserving order. A daytime TDO flag cannot retroactively confirm an overnight failure.
4. Score Asia failure, TDO confirmation and opposite-edge reach by06:00/09:30 as separate conditional rows. Carry overnight date offsets, daylight-saving clock behavior and missing-bar eligibility.

**Acceptance checks:**

- July10,2026 low sweep02:21 then inside close known02:35 passes the named variant.
- January2,2026 first sweep00:55 has no inside five-minute close within30minutes; the01:30–35 close is too late.
- Changing09:00 bars must not change the already frozen Asia box or its overnight event record.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G02-A-2026-07-10.png>) | true | yes for the stated Asia sweep/fail sequence | Asia20–00 H29963.50/L29804.25. Low is swept02:21 and five-minute inside close is known02:35; later failure lower does not erase the initial event. The chart does not establish the optional TDO confirmation. |
| [B / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G02-B-2026-01-02.png>) | false | no within the named30-minute window | H25638.25 first swept00:55. Complete five-minute closes at01:00,01:05,...01:30 remain at/above H; first inside close from01:30–35 comes beyond30minutes. Intrabar dips below H are not the required close. |

### R-G03 — Completed previous-hour failure

The source describes the last completed60-minute box and repeated subsequent sweep/fail entries. The current producer now uses clock hours; FORMULAS still mixes current behavior with old five-minute stepped fixtures and counts.

The seven clock boxes are present, but the headline is any failure across all seven, not a per-hour failure rate. Box/outcome coverage is not enforced in family_levels, and grid resampling uses the last one-minute start as close time. Old hour_fail_n=14 fixtures no longer describe seven boxes.

**Source references:** [GB pack L32](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:32>); [GB pack L439](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:439>); [GB pack L685](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:685>).

**Code to change:** [formulas.py::clock_hour_boxes](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:121>), [formulas.py::hour_fail_count](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:125>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [grid.py::resample_close](</workspace/implementation/src/trading_research/research/phase1_live/grid.py:48>), [recipe_score.py::_preds.g03](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:577>), [family_clocks.py::_doc_from_rows](</workspace/implementation/src/trading_research/research/phase1_live/family_clocks.py:323>).

**Build steps:**

1. Keep one record for each completed hour09–10 through15–16 and its own following-hour outcome. Make the final16–17 observation explicitly outside RTH; omit it from any RTH-only headline rather than silently extending that population.
2. Require complete construction and usable outcome coverage per hour, not only session6–9 eligibility. Use actual bar-completion times and the repaired two-tick sweep/five-minute failure event.
3. Return every qualifying episode with its hour, side, sweep and confirmation; report event counts and failed-sweep fractions by hour. Retain any-hour-per-day only under that precise label.
4. Replace stepped-box fixtures, stale documentation and the clock-report selector that still expects step_min=0. Add opposite-edge and PDH/PDL/TDO outcomes after each confirmed event without counting pre-entry extrema.

**Acceptance checks:**

- July10,2026 has a valid09–10 low failure; June9,2025 is the retained no-failure case.
- Exactly seven complete hour records exist on a full day; missing input produces ineligible rows and reduces the denominator.
- Per-hour successes/eligible counts must aggregate from actual hour observations;646/647 day positives cannot be printed as a per-hour success rate.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G03-A-2026-07-10.png>) | true | yes for at least one completed-hour failure | Seven actual clock boxes09–10 through15–16 are visible. The09–10 box low is swept around10:32 and reclaimed. This one valid episode supports any-hour=true but not a per-hour rate of0.9985. |
| [B / 2025-06-09](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G03-B-2025-06-09.png>) | false | no for the retained clock-hour detector | The09–10 high21819.75 breaks upward after10:08 and price holds; subsequent plotted hour boundaries do not supply a qualifying first-sweep fail-back under the retained test. All seven boxes differ from old five-minute stepped fixtures. |

### R-G04 — 09:30 manipulation and reclaim

The pack states a sweep below the09:30 open, reclaim and hold, then a retracement target with a stop at the lows. It does not give a universal hold duration or a fifteen-minute cap; the above-open short is a named side variant.

The current implementation improved to a five-minute reclaim over AM, but equality counts as reclaim, there is no hold, and no completed-impulse discount target is tracked. This differs from both the older15-minute description and the full source sequence.

**Source references:** [GB pack L30](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:30>); [GB pack L88](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:88>); [GB pack L90](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:90>).

**Code to change:** [formulas.py::reclaim_5m](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:137>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.g04](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:580>).

**Build steps:**

1. Use the09:30 opening price and scan only after that print. Preserve the source-supported below-open long; keep any above-open mirror in a separate named variant.
2. For the named two-tick/five-minute variant require a sweep≤open−2 ticks then a completed close strictly above the open. Store confirmation at the five-minute end and an explicit expiry parameter; do not silently import the old09:45 cutoff.
3. Leave source hold duration unresolved. Quantified hold variants must state duration, tolerated closes and whether new lows invalidate. Attach the stop to the actual sweep low available at confirmation.
4. If measuring discount/GP outcomes, resolve and freeze the preceding completed down impulse before entry. Report reclaim, hold and target reach separately; a missing impulse/hold definition is null, not assumed success.

**Acceptance checks:**

- July10,2026 provides an undercut and five-minute reclaim; January10,2025 remains below21192.50 throughout AM and fails.
- A close exactly at the open must not pass a strict above-open reclaim; a later close below must invalidate a declared hold.
- Extending the final AM high cannot change an impulse already selected for the target.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G04-A-2026-07-10.png>) | true | yes for the named5m-reclaim variant; source hold unresolved | 09:30 open29834.75 is undercut around09:40, then reclaimed by a complete five-minute close near09:45. A later second undercut shows why a bare reclaim cannot stand for an unspecified hold and discount-target outcome. |
| [B / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G04-B-2025-01-10.png>) | false | no | Price falls below09:30 open21192.50 and never closes back above it in AM. This is a valid non-reclaim counterexample; a simple open touch would be the wrong event. |

### R-G05 — TDO close-through after a named sweep

The source confirmation is a five-minute close through midnight open after sweeping a different named reference, such as Asia high. A standalone TDO wick/cross and the Pine73.75% touch statistic are distinct events.

The producer finds the first price already beyond TDO in AM, calls that a wick, then seeks an opposite close. It does not require a crossing approach, name the swept box edge, or connect the TDO close to that edge. Its first-side selection can miss a later valid TDO reclaim.

**Source references:** [GB pack L24](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:24>); [GB pack L142](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:142>); [GB pack L612](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:612>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [grid.py::first_wick_break](</workspace/implementation/src/trading_research/research/phase1_live/grid.py:36>), [grid.py::resample_close](</workspace/implementation/src/trading_research/research/phase1_live/grid.py:48>), [recipe_score.py::_preds.g05](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:583>).

**Build steps:**

1. Create one frozen TDO level from the first00:00 print, with its actual timestamp. A missing midnight print makes the level unavailable instead of silently taking the next minute.
2. Consume a G01/G02 or prior-extreme sweep event carrying reference_id, side and sweep_time. For a high-side sweep require a subsequent completed five-minute close below TDO; mirror the relation for a low-side sweep.
3. Keep standalone TDO touch/cross observations in separate fields. Require an actual approach/cross where that is the measured event; being below a level at the start of the window is not automatically a new sweep.
4. Return overnight and AM confirmation rows with explicit sweep→close expiry and wick invalidation. Use eligible named sweeps for the denominator and keep the Pine08–16 comparison separate.

**Acceptance checks:**

- A price path starting wholly below TDO with no named-edge sweep cannot confirm the source setup.
- January28,2026 contains a TDO undercut/reclaim despite the retained first-side flag being false; the repaired episode scanner must retain that crossing without automatically promoting it to a sourced setup.
- An Asia-high sweep at01:10 followed by a five-minute close below TDO at01:30 must be linked to the overnight episode, not an AM flag.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G05-A-2026-07-10.png>) | true | cannot-tell for source sweep-linked event; plain TDO cross yes | TDO29933 is crossed upward around09:49 and repeatedly afterward. The producer treats already-below-TDO prices as a downward wick and never identifies the required separate Asia/NYAM/PD edge sweep. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G05-B-2026-01-28.png>) | false | no for a new TDO close-back in the producer window | TDO26220.25 is undercut09:36–38 and reclaimed, yet the first-side selection begins from already-above-TDO AM prices and looks for the opposite close. Retained false exposes why a level-cross flag is not a named-edge sweep→TDO event. |

### R-G06 — Unfilled NWOG as a destination

The source says Sunday18:00 versus Friday close, an unfilled weekly gap, and exit when the gap is tagged. The pack does not publish the exact Friday closing minute. FORMULAS names16:59 while the code uses15:59; these are separate endpoints. A definition that counts the formation opening print itself as a prior fill would also make every gap immediately filled.

The code computes a real Friday-RTH/Sunday-open interval, but only asks whether AM extrema overlap it. August31 was already visited overnight before the scored AM touch. There is no live unfilled/retired state or entry-to-destination chronology.

**Source references:** [GB pack L59](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:59>); [GB pack L68](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:68>); [GB pack L615](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:615>); [GB pack L673](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:673>).

**Code to change:** [family_fail.py::build_fail_table](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:58>), [recipe_score.py::_preds.g06](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:586>), [FORMULAS.md::R-G06](</workspace/planning/phase-1-live/FORMULAS.md:881>).

**Build steps:**

1. Keep Friday15:59-close and Friday16:59-close gaps as explicitly named endpoint variants until source chart confirmation. Use the exchange calendar for holidays and actual last available session prints; do not substitute settlement.
2. Resolve the formation convention before faithful scoring: the Sunday opening endpoint creates the gap and cannot alone retire it. Store lower/upper bounds, formation_time and a documented post-formation visit rule; leave the source rule unresolved if its exact contact semantics cannot be recovered.
3. Track untouched, first-tagged and retired states chronologically from formation. At any candidate entry require a still-live gap in the trade direction. Near edge is relative to approach, not always the numerically lower boundary.
4. Measure first post-entry tag by12:00/16:00 and exit at that tag. Keep any-AM-overlap as a separate descriptive statistic; connect optional midnight/open failures by event IDs.

**Acceptance checks:**

- August31,2026 overnight visitation must prevent its09:31 re-touch from being labeled a fresh unfilled-gap destination.
- August24,2026 AM stays below the retained29395.75 area and has no AM tag.
- A formation opening print must not cause every gap to be simultaneously created and retired; both gap-above and gap-below approaches must select the correct near edge.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-31](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G06-A-2026-08-31.png>) | true | no as a fresh unfilled-gap AM target; yes as any AM gap touch | Code gap starts at Friday15:59 close29496.50 and Sunday18:00 open above29500. Price visits the band overnight around02:00–04:00, then AM touches it again09:31. The scorer ignores prior visitation/retirement. |
| [B / 2026-08-24](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G06-B-2026-08-24.png>) | false | no for the AM gap target | Code Friday close29395.75 lies well above the AM path, which ranges around28950–29250. Sunday already traded around the gap; no AM tag occurs. Endpoint semantics remain unverified against HIS CHART. |

### R-G07 — Golden-pocket continuation

The source measures50–61.8% from a completed impulse end and uses the area as location for a rejection or a level sweep/failure. The accessible author-authored [September1 thread](https://threadreaderapp.com/thread/2094830361758843015.html) also describes a pocket retracement with a PDL sweep/failure; its chart media remains unavailable.

The current algebra mirrors50–61.8% correctly, but anchors it to the09–10 box and infers direction from that hour’s close/open. The recipe scores only gp_touch, despite storing a separate rejection helper. It cannot certify a source impulse or continuation.

**Source references:** [GB pack L73](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:73>); [GB pack L79](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:79>); [GB pack L258](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:258>); [GB pack L537](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:537>).

**Code to change:** [formulas.py::gp_band_impulse](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:112>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.g07](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:589>).

**Build steps:**

1. Keep the existing NYAM-box proxy explicitly named. For a source-compatible row, require a resolved completed impulse with ordered start/end extrema, completion_time and bias known before the retracement; do not infer it from later price.
2. Preserve the exact formulas: down H→L gives[L+0.5W,L+0.618W]; up L→H gives[H−0.618W,H−0.5W]. Store both endpoints and direction, and round only under the chosen tick policy.
3. After pocket overlap, require the declared confirmation: a named G rejection or a linked level sweep plus completed five-minute failure. Track invalidation beyond the proper pocket/structure extreme and retain ambiguity when the source confirmation is not quantified.
4. Score pocket touches, confirmed continuation and impulse-extreme reach by16:00 separately. Bias from G08 must be an earlier event, not a final overnight/session boolean joined retrospectively.

**Acceptance checks:**

- Synthetic110→100 yields[105,106.18];100→110 yields[103.82,105], with opposite continuation sides.
- July10,2026’s NYAM pocket29858.496–29879.50 is a touch diagnostic; October8,2025’s25104.028–25119.25 is untouched after10:00.
- A pocket traversal without required confirmation must never be counted as continuation merely because gp_touch=true.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G07-A-2026-07-10.png>) | true | touch yes; complete source continuation cannot-tell | NYAM candle direction is up, so its H29968.50/L29790.50 yields the lower-half pocket29858.496–29879.50. AM visits it repeatedly, including a sharp10:32 traversal. An arbitrary box sign plus touch does not establish the author’s completed impulse and confirmation. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G07-B-2025-10-08.png>) | false | no for the plotted NYAM-pocket variant | Upward NYAM H25183.75/L25054.75 yields pocket25104.028–25119.25. Price stays far above the pocket after10:00; there is no touch. The unavailable author chart prevents choosing a different impulse as faithful. |

### R-G08 — Overnight prior-extreme reclaim sets bias

The pack describes PDL sweep/reclaim overnight setting a long bias and subsequent NYAM pullbacks. FORMULAS adds a five-minute hold-to09:30 convention; its exact hold rule is a named interpretation rather than a published numerical default.

The code only combines an overnight high/low outside prior RTH with the final09:29 one-minute close back across. It does not identify a causal five-minute reclaim or invalidation, and cannot link that bias to a later pocket/rejection event.

**Source references:** [GB pack L313](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:313>); [GB pack L443](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:443>); [GB pack L543](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:543>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.g08](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:592>), [clocks.py::CLOCKS](</workspace/implementation/src/trading_research/research/phase1_live/clocks.py:32>).

**Build steps:**

1. Freeze actual prior RTH09:30–16:00 extremes from the immediately previous trading session; preserve early-close/session provenance. Scan overnight18:00–09:30 events against those levels.
2. Create ordered sweep and completed five-minute reclaim events. For the named hold-to-open variant, require every subsequent completed five-minute close through09:30 to stay on the reclaimed side; retain the last invalidation and define whether a new reclaim resets eligibility.
3. Emit directional bias at its true confirmation time with a validity interval. Source-unquantified hold duration or PDH mirror provenance must remain explicit rather than being inferred from a final-close boolean.
4. Link subsequent NYAM impulse/pocket and rejection events only to bias active then. Report next-AM path and pullback outcomes conditional on the bias; presence of either-side reclaim is a separate aggregate.

**Acceptance checks:**

- January10,2025’s08:30 PDL sweep and later recovery must expose exact reclaim/hold times; July10,2026 sweeps neither prior extreme.
- A final one-minute close above PDL after a five-minute hold failure cannot retroactively repair the earlier failed bias.
- Changing09:31 bars must not alter the frozen overnight confirmation.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G08-A-2025-01-10.png>) | true | sweep and final reclaim yes; causal hold cannot-tell | Prior RTH low21166.25 is swept by08:30 news and final overnight price returns above it near09:30. The zoom shows the sweep, not a stored five-minute reclaim/hold event. Current code only inspects the overnight extremum and final one-minute close. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G08-B-2026-07-10.png>) | false | no | Overnight remains between prior RTH low29614.50 and high29993.50. Neither prior edge is swept, so this is a clean negative for the stated prerequisite. |

### R-G09 — Stacked high sweep, bearish shift, NWOG target

The source sequence is PDH+Asia high+London high sweep, failure below, bearish structure shift and then the gap target. The London02–05 clock,0.05W proximity and numerical swing/MSS convention are named interpretations. A low-side mirror is not shown by the cited example.

The current single eligible positive on May20,2024 contains a gap tag before an upward stack break, not the required bearish sequence. Code uses Jumbo London00–03, tests only level proximity plus Monday plus AM gap overlap, and omits sweep/failure/MSS.

**Source references:** [GB pack L156](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:156>); [GB pack L615](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:615>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.g09](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:595>), [recipe_score.py::_stats](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:42>), [family_fail.py::build_fail_table](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:58>).

**Build steps:**

1. Keep the source short sequence separate from any named long mirror. Resolve London clock provenance, then use GB02–05 high rather than the00–03 Jumbo field. Freeze PDH and Asia/London levels at their completion times.
2. For the named proximity variant calculate max(levels)−min(levels)≤0.05W69 only after09:00. Preserve each reference and timestamp; a set of close levels is a prerequisite, not a sweep.
3. Require ordered high-side sweep, completed five-minute fail-back below the declared stack boundary, then a causal bearish structure-shift event from the explicitly resolved swing rule. Do not build an arbitrary swing rule to make the historical rate pass.
4. At confirmed entry require a live gap below and measure its first subsequent tag through16:00. Use eligible stacks/sweeps/confirmed setups as separate denominators; empty conditional populations stay n=0, never fall back to all sessions.

**Acceptance checks:**

- May20,2024’s09:30 gap touch followed by bullish stack break must fail the stated AM sequence.
- July10,2026 is ineligible as Friday and unstacked; it must not be fabricated as an eligible conditional negative.
- Shuffling target time to before failure or changing London00–03 without changing02–05 must not produce a valid faithful setup.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2024-05-20](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G09-A-2024-05-20.png>) | true | no for AM stacked-short sequence | PDH18677, Asia H18679.25 and code London H18678.75 cluster. AM tags the gap around09:30 BEFORE breaking up through the stack09:33–35 and trending upward. It does not fail back, shift bearish and then target the gap; the single retained positive reverses the required order. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G09-B-2026-07-10.png>) | unscored on this date | no: Friday and unstacked | Not Monday; PDH29993.50, Asia H29963.50 and code London H29948.75 are separated. This is an ineligible diagnostic, not an eligible negative in the one-row conditional denominator. |

### R-G10 — Repeated fades on the pressure side

The cited chart is repeated shorts from failed highs on a grind day, with red entry arrows and blue covers. The source does not publish a universal numerical pressure/lean classifier; bidirectional chop is a different observation.

The code adds two booleans: any-side first failure of09–10 and any-side first failure of10–11. July10 counts a low failure and a high failure as two fades. It neither counts repeated entries nor requires one pressure side.

**Source references:** [GB pack L669](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:669>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [grid.py::failback_wick_c5](</workspace/implementation/src/trading_research/research/phase1_live/grid.py:131>), [recipe_score.py::_preds.g10](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:598>).

**Build steps:**

1. Preserve the two source clock boxes09–10 and10–11, freezing each separately. A later trade may reuse a box only after a defined leave/reset and a new sweep/failure episode.
2. Keep the source shown high-side short fades as their own observation. Any numerical pressure filter must be specified as a named variant using information available before each entry; do not use final day type to declare the earlier lean.
3. Count distinct confirmed failures on the chosen side, storing per-event sweep, confirmation, stop and cover/target times. Two different-side box failures do not satisfy repeated same-side fade.
4. Report event count, sessions with at least two eligible same-side events and per-event rejection/outcome rates. Retain the old two-box-any-side count under a descriptive comparison label.

**Acceptance checks:**

- July10,2026’s NYAM low failure plus10–11 high failure must not pass repeated-short fades.
- October8,2025 upward breaks holding above both box highs provide a non-fade counterexample.
- Three bars in one continuous outside visit must count as one episode; two separated high sweeps after resets may count as two.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G10-A-2026-07-10.png>) | true | no as repeated same-side fades | NYAM first failure is a LOW sweep around10:32;10–11 first failure is a HIGH sweep near11:25 with inside close known11:40. Two opposite-side failures produce fade_count=2, contrary to the source’s repeated high-side shorts. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G10-B-2025-10-08.png>) | false | no | NYAM high and then10–11 high25231 break upward and hold; no sequence of two high-side failures occurs. This is a suitable repeated-fade negative. |

### R-G11 — A+ grade belongs to the traded setup

The grading description requires a sweep of the relevant traded range plus failure back inside. Sweep-only is explicitly weaker. The current formula correctly names this distinction, but the original graded chart cannot be inspected.

Current aplus_failback correctly matches sweep and failure within each key, then ORs Asia,NYAM and10–11 over the day. That is a day-level presence label, not the grade of an individual trade. It inherits fail-back timing/depth issues and covers only one previous-hour box.

**Source references:** [GB pack L93](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:93>); [GB pack L147](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:147>); [GB pack L242](</workspace/planning/phase-1-fable/references/greenbirdtrader-trading-framework.md:242>).

**Code to change:** [formulas.py::aplus_failback](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:165>), [family_fail.py::build_fail_table](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:58>), [family_fail.py::fail_fixtures](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:152>), [family_fail.py::report_fail](</workspace/implementation/src/trading_research/research/phase1_live/family_fail.py:163>), [recipe_score.py::_preds.g11](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:601>).

**Build steps:**

1. Assign grade to a concrete trade/setup event with traded_range_id, side and entry_time. Require the same range’s qualifying sweep and completed failure before entry; neither an unrelated overnight sweep nor a later failure can upgrade it.
2. Preserve sweep-only as a separate necessary-condition field. Source grading cannot be reduced to a six-to-nine sweep, and any-day OR should be named has_aplus_setup rather than applus trade success.
3. Use repaired G01/G02/G03 event outputs, including all eligible previous-hour boxes. Keep unknown traded range or unavailable chart grading as cannot-tell rather than automatically B+.
4. Replace hard-coded pass=True grading fixtures and the report extra def=sweep observed with executable event-level assertions and matching sweep-plus-failure text. Report outcomes conditional on actual event grades.

**Acceptance checks:**

- July10,2026 has several qualifying episodes, but an unrelated entry without its own sweep/failure cannot inherit A+.
- August25,2026 is a no-failure case under the retained three-box scan.
- A sweep in Asia plus failure only in NYAM must not pass as one setup; a failure after entry cannot establish entry grade.

**Chart decision needed:** Inspect the original Green Bird chart cited by this pack section: confirm its range/impulse endpoints, clock and ordered sweep/fail/target marks. The pack contains a description, but its HIS CHART image was unavailable in the supplied files and accessible web results.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G11-A-2026-07-10.png>) | true | yes for at least one sweep/fail setup; per-trade grade unavailable | Asia low failure, NYAM low failure and10–11 high failure are separate episodes. A session OR can be true, but cannot attach A+ to an unrelated entry lacking its own range sweep and fail. |
| [B / 2026-08-25](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-G11-B-2026-08-25.png>) | false | no for the retained three-box label | Asia high29190 breaks and holds overnight; NYAM low29279.25 breaks after10:00 and remains below through the deadline. No qualifying failure across the three tested boxes makes the retained label false. |

### R-A01 — Balance-edge fade to the fixed POC

The balance drawings show both edge bands and rotations toward POC. Fixed prior value is an explicit research construction; the source does not publish the G-default distances or band thickness. MAMT p.5 says most excursions return, while p.9 calls the general return about one in five: that statistical claim has an internal denominator/direction conflict.

The fresh producer calls both edge rejection helpers, but discards inside-balance eligibility and POC reach. The helper evaluates acceptance over the whole AM, and its POC search starts at the window beginning and measures 60 minutes from touch rather than confirmed rejection. July 10 is a valid named fade example; that does not validate the omitted conditions on other days.

**Source references:** [AMT1 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p005-i1.png>); [AMT1 p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i1.png>); [AMT1 p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i2.png>); [MAMT p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p005-i1.jpeg>); [MAMT p.9](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [ABS p.7](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>).

**Code to change:** [formulas_jumbo.py::a01_fade](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:474>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.a01](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:604>), [FORMULAS.md::R-A01](</workspace/planning/phase-1-live/FORMULAS.md:136>).

**Build steps:**

1. Freeze the prior RTH trade profile at its actual session close: one-tick grid, volume POC, 70% VA with documented tie handling. Preserve the source balance-band object separately from the named VA-edge implementation.
2. Scan each edge visit in time order. Before the touch, require price in balance and no already confirmed 30-minute acceptance outside. Do not let acceptance later in the day invalidate an earlier eligible fade. Apply the named two-tick touch and 0.5×VA-height close reversal within 15 minutes, with completion timestamps.
3. Starting at the confirmed rejection, find the first POC overlap in the following 60 minutes. Keep setup, rejection, POC target and later invalidation fields separate; an earlier POC touch cannot prevent a later valid one or count as the target.
4. Report edge-fade rejection and POC outcome conditional on eligible edge episodes. Keep the general excursion-return statistic separate and source-stopped until the p.5/p.9 conflict is resolved. Remove the unconditional reject-only pass label.

**Acceptance checks:**

- July 10, 2026 VAL 29823 rejection and POC 29900 rotation remains a named positive; January 28 opens above VAH 26100 and has no edge fade.
- A POC visit before rejection followed by no later visit is not a target success. A later valid visit must remain discoverable.
- An outside acceptance at 14:00 cannot alter a fade known at 10:00.

**Unresolved definition:** MAMT p.5 and p.9 disagree on the general failed-auction frequency. That statistical claim cannot be certified by inspecting an individual edge-fade chart.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A01-A-2026-07-10.png>) | true | yes for named prior-VA fade | July10 VAL29823 rejects into POC29900; actual a01 helper returns inside=1,poc_reach_60=1,val_reject=1. Prior profile is fixed July9; source manual balance boundaries remain a separate object. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A01-B-2026-01-28.png>) | false | no | January28 open26252.50 is above prior VAH26100 and remains above; no VA-edge touch or inside-balance fade. Prior POC26090/VAL26049.75 are separate lower references. |

### R-A02 — Ledge break, retest and continuation

A ledge is the edge of a volume shelf. The figures show multiple fixed ledges around POC; they do not define a universal median-volume threshold. Prior VA boundaries alone are a different named level set.

The retained recipe cache lacks a02_ledge_hold on 638 dates, allowing the old tape print-near-VA flag to supply the score. Fresh assembly differs on 371 of 668 rows. Fresh code calls the break/retest helper on both VA edges, but passes the same entire AM as break and retest windows, allowing a touch before hold confirmation. No source shelf or next node is selected.

**Source references:** [AMT1 p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i1.png>); [AMT1 p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-lesson-1-p009-i2.png>); [VP2 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p004-i1.png>); [VP2 p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p004-i2.png>); [VP2 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p005-i1.png>); [VP2 p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vp-lesson-2-p005-i2.png>); [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_jumbo.py::a02_shelves](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:501>), [formulas_jumbo.py::a02_ledge_retest_hold](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:505>), [recipe_score.py::_join](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:69>).

**Build steps:**

1. Invalidate caches missing any required recipe key even if recipe_rev matches. Record producer identity per joined field, rebuild the affected table in a future implementation task and remove silent fallback to a differently defined tape flag.
2. Build the named shelf detector on a complete fixed prior price grid: maximal adjacent runs at or above the declared median, with first/last prices as ledges. Store shelf bounds, height and both ledges; call the VA fallback a distinct variant.
3. For each ledge and side, require a close beyond it followed by the full 30-minute outside hold. Begin the retest search after hold completion; require approach from outside, then the named rejection in the break direction and no close back inside over the specified confirmation window.
4. Choose the next external node at setup time, using an explicit ordered candidate list. Score retest confirmation and post-confirmation reach by 16:00 separately, conditional on eligible held breaks.

**Acceptance checks:**

- July 10, 2026 retained true must be identified as old print proximity; both fresh break/retest flags are false.
- January 28 holds above VAH but never retests it in AM; it must remain false.
- A touch before the 30-minute hold ends cannot satisfy the retest. A median-derived shelf must retain zero-bin gaps rather than joining nonadjacent prices.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A02-A-2026-07-10.png>) | true | no for current break/retest helper; retained tape touch yes | July10 current a02 helper returns break_hold=0 and retest_hold=0 both sides. The retained recipe lacks this new field and falls back to tape at-VA-edge print=true. VA boundaries are not computed shelf ledges. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A02-B-2026-01-28.png>) | false | no | January28 holds above VAH26100 but never retests the plotted boundary in AM. Current helper and retained tape flag are false. |

### R-A03 — Re-entry, inside hold and opposite-edge traverse

The loose 80% statement conditions the traverse on re-entry and acceptance inside prior value. The 30-minute hold and 16:00 horizon are named defaults, distinct from the two-period strict rule.

The current helper handles outside opens only. Its held-inside check enforces one boundary, so price can exit the far side immediately and still pass. Target timing is compared with re-entry, not hold completion, and only the first whole-window target touch is considered. The scorer divides by all eligible days instead of held re-entries.

**Source references:** [AMT1 p.7 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-amt-lesson-1-p007.png>); [LIVE p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/amt-on-live-markets-p008-i1.jpeg>); [LIVE p.9](</workspace/sources/documents/discretionary/amt-on-live-markets.pdf>); [ABS p.12](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>).

**Code to change:** [formulas_jumbo.py::a03_reentry_traverse](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:521>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.a03](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:625>), [recipe_score.py::_stats](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:42>).

**Build steps:**

1. Create eligible excursions from either an outside open or a subsequently confirmed outside break. Store the same edge and side through re-entry; do not substitute the six-to-nine path class.
2. On a complete close back inside, require every confirming close to satisfy VAL < close < VAH for the entire named 30-minute hold. A break through either boundary cancels this acceptance candidate; restart only on a new valid episode.
3. After hold confirmation, scan for an opposite-edge two-tick overlap before 16:00, stopping on the defined invalidation. Earlier opposite-edge touches are path history, not a confirmed-setup outcome. Store both timestamps.
4. Report accepted re-entry count as the denominator and far-edge reach count as numerator; retain excluded, censored and ambiguous observations separately. Include both entry sides and both origin types.

**Acceptance checks:**

- January 2, 2026 rapid descent through VAH 25634 and VAL 25537.50 must fail the inside-hold prerequisite.
- The additional February 12, 2026 chart supplies a candidate that holds between both boundaries before a later far-edge reach; verify its event times directly.
- An inside open followed by a held breakout and genuine re-entry is eligible; the current open-only branch must not discard it.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A03-A-2026-01-02.png>) | true | no for a hold wholly inside value | January2 re-enters below VAH25634 around10:12 but quickly crosses VAL25537.50; current one-sided hold still passes below VAH while outside the far edge. The traverse is real, the30-minute inside hold is not. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A03-B-2026-07-10.png>) | false | no for current open-outside variant | July10 opens inside[29823,29986.25]; its later fluctuations and afternoon outside acceptance do not qualify the code open-outside condition. |
| [documented-hold-positive / 2026-02-12](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A03-documented-hold-positive-2026-02-12.png>) | true | yes for the named both-boundary 30-minute hold then traverse | Open 25346.25 is above VAH 25328. The first inside close is near 09:44; closes stay between VAL 25141.75 and VAH through the full 30-minute confirmation, then price reaches the lower edge later around 10:35. The prior February 11 trade profile is fixed. This supplies a genuine named-event positive alongside the January 2 false positive. |

### R-A04 — Strict two-period 80% rule

The source requires an outside open and two consecutive 30-minute periods back inside value before a complete traverse. It does not restrict those periods to A and B or specify whether closes or complete ranges must be inside.

amt_80pct currently tests outside open and the 09:59/10:29 one-minute closes. It never checks the target. July 22 is a direct false success interpretation: both closes are inside, but RTH high 29342.25 does not reach VAH 29361.75.

**Source references:** [MAMT p.18](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.a04](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:640>), [FORMULAS.md::R-A04](</workspace/planning/phase-1-live/FORMULAS.md:936>).

**Build steps:**

1. Keep the source period-inside definition unresolved for faithful certification. Implement only separately named close-inside and full-range-inside readings after the choice is documented; do not silently treat A/B as the only eligible pair.
2. Resample on the 09:30 exchange clock into complete 30-minute periods. Search consecutive qualifying pairs after an outside open, with known_at at the second period end.
3. Freeze the entry edge and opposite target. Starting after pair completion, measure two-tick overlap of the opposite VA edge by the actual RTH close. A target reached before the pair finishes is not a later traverse.
4. Rename the existing flag as a setup-eligibility observation. Publish traverse probability conditional on qualifying pairs, including n=0 if none exist, with one stated unit per day or per independent episode.

**Acceptance checks:**

- July 22, 2026 must show setup=true and traverse=false; July 10 opens inside and is ineligible.
- A C/D pair can qualify when A/B do not. A missing minute prevents a complete period rather than shifting a row-index close.
- Closes inside with wicks outside must differ between the two named readings.

**Unresolved definition:** The two consecutive periods may mean their closes or their complete ranges; no numerical source chart resolves this definition.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-22](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A04-A-2026-07-22.png>) | true | setup precondition yes; far-edge outcome no | July22 opens29090.50 belowVAL29196.25.09:59C29276.75 and10:29C29220 are inside, but RTH high29342.25 missesVAH29361.75. The true flag is eligibility, not an80% traverse success. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A04-B-2026-07-10.png>) | false | no | July10 opens inside prior value, disqualifying the strict outside-open setup even though both initial30-minute closes are inside. |

### R-A05 — POC repeated failure versus through-and-retest

The POC tell is a sequence: repeated failed visits imply chop; an aggressive push through followed by a holding retest supports the far edge. POC is a fixed reference, and the source does not define the numeric visit reset or hold duration.

a05_poc_tell counts touching minutes rather than independent visits, infers direction from the first AM close, and accepts held-through OR retest-reject. Near/far targets use the entire window, including prices before the signal. Only the chop flag is scored.

**Source references:** [LIVE p.9](</workspace/sources/documents/discretionary/amt-on-live-markets.pdf>); [RTVP p.5](</workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>).

**Code to change:** [formulas_jumbo.py::a05_poc_tell](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:553>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.a05](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:628>).

**Build steps:**

1. Start from a valid inside-open or A03 re-entry event. Fix the prior POC and entry side at that point. Define an explicit reset outside the touch band before a new visit may count; expose the reset as a named parameter.
2. For chop, require at least two distinct failed visits with no confirmed through-and-hold by the second failure. For traverse, require close-through, a later retest from the new side, and rejection in that direction; keep held-through-only as a separate observation.
3. Set known_at to the second failure or retest confirmation. Search near and far targets only afterward through 16:00, preserving invalidation and same-bar ambiguity.
4. Report the two signal classes and their subsequent near/far outcomes separately. Add an aggression filter only with trustworthy tape and a published or clearly named definition.

**Acceptance checks:**

- July 10, 2026 has visible repeated POC 29900 visits, but its 27 touching minutes must not become 27 attempts.
- January 28 has zero POC 26090 visits and remains a negative.
- Two adjacent touch bars in one visit count once; a far-edge touch before the second failure does not count as its outcome.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A05-A-2026-07-10.png>) | true | yes for visible POC chop episodes; exact event count wrong | July10 POC29900 has repeated separated visits and failures before later trend. Current helper counts27 touching minutes, not27 distinct episodes, and labels both near/far reach using whole-window extrema. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A05-B-2026-01-28.png>) | false | no | January28 POC26090 is below all AM prices; helper n_touch=0 and no chop label. |

### R-A06 — Failed auction at an older external balance POC

MAMT p.9 explicitly targets established VAH after rejecting an older POC from above, and VAL in the mirror. The p.11 accepted example labels vah = target. FORMULAS repeats the far-boundary procedure but its fixture stops at near VAL; that fixture conflicts with the source. The older POC belongs to a distinct prior balance.

Retained a06_naked_poc comes from a tape check against today’s final RTH POC, tested for absence overnight; this is retrospective. Fresh assembly changes 311 of 668 rows, but fresh recipe code passes the established balance’s own POC as older_poc. The helper lacks ordered break/tag windows and targets the near boundary.

**Source references:** [MAMT p.9](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [MAMT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p010-i1.jpeg>); [MAMT p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p011-i1.jpeg>); [MAMT p.26](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [LIVE p.10](</workspace/sources/documents/discretionary/amt-on-live-markets.pdf>); [VP2 p.6](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::a06_failed_auction](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:595>), [recipe_score.py::_join](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:69>), [FORMULAS.md::R-A06 fixture](</workspace/planning/phase-1-live/FORMULAS.md:172>).

**Build steps:**

1. Repair schema validation as in A02. Build a chronological ledger of completed older balance profiles and naked POCs, with their first subsequent trade-through retirement times. Never use the current day’s final RTH POC to define a morning setup.
2. At the established-balance break, choose an eligible older POC outside that balance on the break side. Preserve its originating profile and age. A POC inside the same established VA cannot satisfy the older-external-balance leg.
3. Require break confirmation, then the older POC tag, then the named five-minute instant-rejection condition in order. Separate the deep-entry-but-eventually-rejected reading from the instant variant. Use only post-tag prices to determine the rejection.
4. Set the downside-break target to established VAH and the upside-break target to established VAL, with post-rejection reach by 16:00. Correct the formula fixture to reach the actual far target. Publish setup probability and conditional target success separately.

**Acceptance checks:**

- July 10, 2026 current helpers return false; the retained true is not an older-POC setup. January 28 is also not such a setup.
- For VAL 100, VAH 120 and older POC 92, a post-rejection high of 100 is not the source target success; a later reach of 120 is.
- Changing afternoon volume must not move an older POC or alter its overnight naked status.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A06-A-2026-07-10.png>) | true | no verified older-external-POC setup; source/formula-fixture target conflict | July10 plots priorPOC29900 inside its own VA. Current failed-auction helper returns0 both sides; retained table lacks this new recipe field and falls back to old naked-POC tape flag=true. There is no older external balance POC. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A06-B-2026-01-28.png>) | false | no verified older-external-POC setup; source/formula-fixture target conflict | January28 priorPOC26090 lies inside[26049.75,26100] below AM price. Both current helpers return0; this is not the older-balance excursion shown by MAMT. |

### R-A07 — Confirmed boundary break and later holding retest

The source drawings show a break followed by a separate return and continuation. IB is one named boundary family; the illustrated balance and shelf edges remain distinct. The numerical 30-minute hold and G-default are research choices.

The producer covers both IB edges but passes the entire post-IB window to both break and retest checks. It can count the initial boundary contact as a later retest. June 9 passes despite no return to IB low 29365 after the outside hold completes. Next value, HTF filter and other source boundaries are omitted. A separate January 30, 2026 sequence breaks IB low 25790.75 at 11:55, completes the named hold at 12:26, retests at 12:30 and confirms the half-width rejection at 12:36, beyond the producer’s noon endpoint.

**Source references:** [RTVP p.6](</workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>); [RTVP p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p008-i1.jpeg>); [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>); [WIC p.5](</workspace/sources/documents/discretionary/whos-in-control.pdf>); [WIC p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/whos-in-control-p008-i1.jpeg>); [TRAP p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p006-i1.jpeg>).

**Code to change:** [formulas_jumbo.py::a07_break_retest](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:622>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.a07](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:631>).

**Build steps:**

1. Build separate fixed boundary sets for prior VA, actual source ledges and the completed 09:30–10:30 IB. Preserve clock, scope, band/line identity and known_at for every candidate.
2. Find close-break and complete the named 30-minute outside hold. Slice the retest window strictly after confirmation, require approach from outside, then apply the directional rejection and inside invalidation rule to that same episode.
3. Freeze an external next-value target and the available prior-session direction filter at setup time. Do not use a prior VA edge behind the entry as an automatically reached continuation target.
4. Measure target reach after retest confirmation until 16:00 and report it conditional on confirmed setups. Print boundary family and side separately; keep the source’s unspecified HTF-bias interpretation visible.

**Acceptance checks:**

- June 9, 2026 must fail the after-hold retest because price does not return to 29365.
- July 10, 2026 has no qualifying named IB retest hold on either side.
- Moving an initial touch earlier without changing the later path cannot create a retest; a genuine later return can.
- January 30, 2026 is a positive for the named IB hold/retest/rejection sequence: IBL25790.75, IBH25940, break close known11:56, hold known12:26, retest bar12:30, rejection close known12:36. Keep missing external next-value/HTF conditions separate; do not certify the entire author trade from this boundary sequence.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-06-09](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A07-A-2026-06-09.png>) | true | no for break→30min hold→later retest | June9 IB low29365 breaks and price trends steeply lower. Current helper passes by reusing the entire post-IB window for break and retest; the plotted boundary contact precedes a completed outside hold, with no later return to29365. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A07-B-2026-07-10.png>) | false | no for current named confirmation | July10 IB[29798,29968.50] is swept below then recovered and later breached above. Current helper returns no retest_hold on either side; no valid ordered sequence shown. |
| [sequence-positive / 2026-01-30](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A07-sequence-positive-2026-01-30.png>) | false | yes for the named IB hold/retest/rejection; external target/HTF filter remains unverified | January30 IBH25940/IBL25790.75, W149.25. Break11:55 known11:56; hold through12:25 known12:26; distinct retest12:30 known12:31; close25715.25 in12:35 confirms more than0.5W down, known12:36. Main and close zoom visibly separate these stages. Producer false because its post-IB scan ends at12:00. The plotted prior VAL25584 is not automatically the author’s next value target. |

### R-A08 — Re-acceptance flips the balance bias

The relevant event is acceptance outside a balance followed by acceptance back inside it, then a move toward the opposite side. This differs from merely opening outside or briefly poking an edge.

Fresh code now evaluates both break sides, contrary to the stale FORMULAS description. Its inside hold still checks only the re-entered edge, and target lookup is whole-window and compared with re-entry rather than confirmation. The scorer reports reacceptance presence without the subsequent opposite-edge outcome. August 19, 2026 supplies a later valid named reacceptance: outside hold known10:19, reentry known11:44, inside hold known12:14 and opposite-edge touch in the12:18 bar. An earlier inside episode is invalidated before target.

**Source references:** [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>).

**Code to change:** [formulas_jumbo.py::a08_reaccept](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:638>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.a08](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:634>), [FORMULAS.md::R-A08](</workspace/planning/phase-1-live/FORMULAS.md:190>).

**Build steps:**

1. Use both sides for outside-break candidates and require an actual complete 30-minute held break, even when the session opens outside. Set outside_confirmation to its completion time.
2. Search only after outside_confirmation for a close back through the same edge. Require all subsequent confirming closes to remain strictly between VAL and VAH for the full inside hold. A far-side escape is a traversal, not an inside hold.
3. Set bias at inside_confirmation and measure a new opposite-edge touch afterward. Stop at the defined outside invalidation; do not accept a target earlier than confirmation.
4. Report accepted re-entries conditional on held outside breaks and target success conditional on accepted re-entries. Update FORMULAS to describe current two-sided calls, while preserving the remaining defects.

**Acceptance checks:**

- January 2, 2026 crosses the far VA boundary too early to satisfy inside acceptance.
- July 10, 2026 short lower excursions do not establish the required held outside state.
- A later genuine re-entry after a failed first attempt must not be hidden by a first-touch-only search.
- August 19, 2026 VAL29563/VAH29662.5: outside break09:48, outside hold complete10:19; the later reentry11:43 completes inside acceptance12:14 and reaches VAH12:18. Reject the earlier attempt when its outside invalidation occurs before target; do not let it hide the later valid sequence.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A08-A-2026-01-02.png>) | true | no for hold wholly inside value | January2 stays aboveVAH25634 early then re-enters and rapidly travels belowVAL25537.50. One-sided held_in stays true even outside the opposite edge; source re-acceptance into the balance is not established. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A08-B-2026-07-10.png>) | false | no | July10 current reaccept helper returns0 both sides; brief lower excursions do not hold outside30minutes before a confirmed inside hold. |
| [sequence-positive / 2026-08-19](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A08-sequence-positive-2026-08-19.png>) | false | yes for the named held reacceptance and later opposite-edge outcome | August19 prior VAL29563, VAH29662.5. Outside low break09:48 known09:49, hold known10:19; later valid reentry11:43 known11:44, inside hold known12:14, VAH touched12:18 known12:19. The earlier inside attempt is invalidated before reaching VAH; the later sequence survives. Numbered actual-close marks and target detail show the chronology. Retained scorer=false. |

### R-A09 — Traverse without acceptance, then continuation retests

The source says a traverse without holding inside changes how later retests are traded. It does not impose a 30-minute maximum on the entire traverse.

The helper adds a total 30-minute traversal cap, scans only AM, and the scorer keeps traverse_nohold while ignoring retest_continuation. August 21 has the traversal prerequisite but its helper continuation result is false. August 26, 2026 demonstrates a valid named continuation after a41-minute traverse: first outside close known09:44, opposite outside close known10:25, retest10:25 and half-width rejection known10:28. No uninterrupted30-minute inside hold occurs.

**Source references:** [MAMT p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p012-i1.jpeg>).

**Code to change:** [formulas_jumbo.py::a09_traverse_nohold](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:667>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.a09](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:637>).

**Build steps:**

1. Identify an ordered close-through of the first boundary and then the other. Between them, test only whether a complete 30-minute inside acceptance occurred; remove the additional total-traverse-time cap from the source-derived row.
2. After the second crossing, search every distinct retest of either boundary from the traverse side through 16:00. Require an explicit reset between visits and store the matched boundary and approach side.
3. At each retest, measure the named directional rejection versus close-back invalidation, using only later prices. Keep quick traversal as a separately named speed bucket if desired.
4. Publish continuation share conditional on qualifying retests, along with prerequisite traversal count. Do not label traversal presence as continuation success.

**Acceptance checks:**

- August 21, 2026 prerequisite=true must coexist with the observed retest_continuation=false.
- A 45-minute traverse with no uninterrupted 30-minute inside hold remains eligible; a 29-minute move followed by an actual 30-minute acceptance does not.
- July 10 must be evaluated by the stated inside-hold condition, without using afternoon data to assign an AM signal.
- August 26, 2026 VAL29208/VAH29288: the09:43 above-VAH close and10:24 below-VAL close are41minutes apart with no30-minute inside acceptance. The10:25 retest and10:27 rejection close qualify the named continuation; removing the unsupported total-time cap must recover this case.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-21](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A09-A-2026-08-21.png>) | true | traverse prerequisite yes; retest continuation no | August21 crosses from aboveVAH29402 to belowVAL29288.75 in the early AM without30minutes inside. Current helper returns traverse_nohold=1 but retest_continuation=0; later recovery crosses back upward. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A09-B-2026-07-10.png>) | false | no | July10 has no whole-VA traverse satisfying the extra30-minute traversal cap; helper returns0. Full-day continuation differs from the AM-only predicate. |
| [sequence-positive / 2026-08-26](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A09-sequence-positive-2026-08-26.png>) | false | yes for the named no-acceptance traverse and subsequent rejection | August26 prior VAL29208/VAH29288, W80. First above-VAH close09:43 known09:44, below-VAL close10:24 known10:25:41minute traverse without30minute continuous inside acceptance.10:25 returns to VAL;10:27 close29163.75 confirms more than40points rejection known10:28. Retained false misses this eligible slower traverse. The later afternoon rise is outside this completed rejection episode. |

### R-A10 — Opening auction type and completed day type

Open drive concerns movement away from the opening price; test-drive and rejection-reverse require ordered tests. AMT and MAMT publish different day-type descriptions. Their qualitative boundaries need named numerical choices.

The current drive detector uses the 09:30 open but excludes the opening one-minute bar. It does not establish all four opening types or the separate MAMT day-type table. Only drive presence is scored; a completed day label cannot be an opening feature. October 8 opening bar low 25074 is below open 25079.75, so the literal upward-drive condition is false despite the skip-first-minute flag.

**Source references:** [AMT1 p.10](</workspace/sources/documents/discretionary/amt-lesson-1.pdf>); [AMT1 p.11](</workspace/sources/documents/discretionary/amt-lesson-1.pdf>); [MAMT p.18](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [MAMT p.20 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p020.png>).

**Code to change:** [formulas.py::amt_drive](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:237>), [family_gap.py::_amt_open_label](</workspace/implementation/src/trading_research/research/phase1_live/family_gap.py:114>), [family_gap.py::_amt_day_label](</workspace/implementation/src/trading_research/research/phase1_live/family_gap.py:131>), [recipe_score.py::_preds.a10](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:643>).

**Build steps:**

1. Define the opening-print handling explicitly: equality at the opening trade is inevitable, but a later trade through the open is disqualifying. Inspect executions or finer bars within 09:30 when available; otherwise mark first-minute order ambiguity instead of discarding that minute silently.
2. Build ordered first-30-minute records for drive, reference-test then drive, rejection through open, and rotation. Fix the reference set in advance and attach confirmation times; keep ambiguous or incomplete openings unclassified.
3. Construct completed RTH day labels at the actual close using separately named AMT and MAMT definitions. For MAMT, retain both-IB-break close-location branches, neither-break containment and the printed IB×2 trend concept without mixing taxonomies.
4. Print the opening-type × day-type transition table and separately defined continuation/fade outcomes. Set day-type known_at to session close and prohibit it from entering the earlier opening decision.

**Acceptance checks:**

- October 8, 2025 first-bar range spans both sides of open 25079.75 and must fail literal drive; July 10 also returns below the open.
- An opening test that occurs after the drive cannot classify a test-drive.
- Changing the final close may change the day label but never the already completed opening label.
- May19,2026 provides a named positive with first30 low equal to the initial open28850.25 and all later minute lows strictly above it; include the09:30 bar. Equality at the initial print is allowed while an actual opposite-side excursion remains disqualifying. Retouches within the first minute require finer observations if that stricter variant is selected.

**Unresolved definition:** The qualitative opening/day labels do not publish all numerical classification boundaries. The October8 first-minute excursion is an observed failure, independent of that definition gap.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A10-A-2025-10-08.png>) | true | no for literal drive; yes only when the opening minute is discarded | October 8, 2025 opening bar O 25079.75 / H 25098.75 / L 25074 / C 25092 spans both sides of the open. Subsequent first-30-minute lows stay above 25089.75. The up-drive flag excludes the initial 5.75-point downside excursion. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A10-B-2026-07-10.png>) | false | no | July10 returns below09:30 open29834.75 around09:40, ruling out an opening drive. Full-day uptrend does not repair the opening classification. |
| [sequence-positive / 2026-05-19](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A10-sequence-positive-2026-05-19.png>) | true | yes for named first30 no-through-open observation | May19,2026 opens28850.25; first bar O28850.25/H28943.5/L28850.25/C28911.25. All later first30 lows remain strictly above open and first30 high reaches29068. Main panel and zoom preserve the opening minute, so this is a valid no-opposite-side observation unlike October8. Intraminute equal-price revisits and the remaining qualitative opening/day types are not certified. |

### R-A11 — Author-specific profile-shape outcomes

The drawings distinguish D, upper-heavy P, lower-heavy b/B and two-distribution B. MAMT’s B-day prose says upside resolution, but its actual p.7 B diagram breaks down. FORMULAS says that diagram points up, which is visually false. Stop the MAMT directional certification until resolved.

Fresh producer includes P+high-only and b+low-only, unlike the stale P-only description. It classifies sparse prior HLC3-volume prices rather than trade-volume VA thirds. February 3 is a b continuation case, not P. The single path flag pools a source-specific directional claim into one score.

**Source references:** [AMT1 p.6 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-amt-lesson-1-p006.png>); [AMT1 p.13](</workspace/sources/documents/discretionary/amt-lesson-1.pdf>); [RTVP p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p009-i1.jpeg>); [RTVP p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p010-i1.jpeg>); [RTVP p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-the-volume-profile-p011-i1.jpeg>); [MAMT p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p007-i1.jpeg>); [MAMT p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p007-i2.jpeg>); [MAMT p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p008-i1.jpeg>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas.py::vp_p_shape](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:420>), [formulas_jumbo.py::a11_vp_shape](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:725>), [recipe_score.py::_preds.a11](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:646>), [FORMULAS.md::R-A11](</workspace/planning/phase-1-live/FORMULAS.md:208>).

**Build steps:**

1. Correct the p.7 figure description and preserve the unresolved B direction as a source stop. Store author, diagram label and literal geometry separately; B cannot mean double distribution in one row and lower-heavy b in another without an explicit mapping.
2. For a named quantitative shape variant, build the fixed prior trade profile on a complete one-tick grid and compute VA-third shares over its actual VA. Keep the existing HLC3 occupied-bin classifier explicitly named as a different object.
3. Implement the declared P/b/double/trending/D thresholds with deterministic precedence, ties and zero-bin behavior. Do not claim the author published those thresholds.
4. Report shape × next-session up/down/both/neither paths separately for AMT balance, RTVP continuation and resolved MAMT claims. Add edge reactions and no-trade trending share without pooling them as a generic pass.

**Acceptance checks:**

- February 3, 2026 must be labelled code b, and July 10 code D; do not relabel the former as P.
- An interior empty price interval must remain a bridge and cannot disappear by dropping zero-volume bins.
- No test may assert MAMT B→up as faithful until its text/diagram conflict is resolved.

**Chart decision needed:** Inspect MAMT p.7 B-day diagram versus its prose: the picture breaks down while the prose says higher. Confirm the intended direction before a faithful B outcome can be scored.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-02-03](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A11-A-2026-02-03.png>) | true | cannot-tell: source text/figure conflict | February3 actual code prior HLC3-volume shape is b, not P; current b+low-only branch passes and price sells off. This sparse occupied-price profile is not the source trade-volume VA thirds. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A11-B-2026-07-10.png>) | false | cannot-tell: source conflict; named detector no | July10 actual HLC3 profile classifiesD, with concentrated spikes and omitted zero bins. Retained false follows shape/path branch, not a verified author D profile. |

### R-A12 — Overnight inventory, LVN band and shelf reaction

The p.14 picture spans 18:00→09:30 overnight and the following RTH. It has two overnight bulges, an LVN band, a shelf band, and a red POC from an earlier left-hand balance aligned with the LVN. FORMULAS incorrectly makes that POC the developing RTH POC. The inventory prose does not supply an exact signed-volume estimator.

The retained flag is only the 09:30 opening price within two ticks of any detected overnight LVN price. No two-bulge validation, LVN/shelf band, old-POC alignment or post-open respect/disrespect sequence is scored. The available aggression trust gate remains binding.

**Source references:** [MAMT p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p014-i1.jpeg>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_jumbo.py::profile_nodes](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:153>), [formulas_jumbo.py::a12_double_lvn](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:769>), [formulas_jumbo.py::a12_respected](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:791>), [formulas_jumbo.py::a12_inventory_sign](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:802>), [FORMULAS.md::R-A12](</workspace/planning/phase-1-live/FORMULAS.md:217>).

**Build steps:**

1. Correct the POC scope to the older balance drawn left of overnight. Freeze the overnight profile at 09:30 from 18:00 executions and retain its exact session and contract; do not substitute prior RTH volume.
2. Define a named two-bulge detector on a complete grid, return the contiguous low-volume bridge as a band and the upper/lower shelf transition as a separate band. Keep minimum-price and VA-edge alternatives separately labelled.
3. After 09:30, bind each visit to the actual LVN or shelf band, then measure respect/rejection versus acceptance through it and subsequent overnight-extreme reach. The picture’s later pullback need not coincide with the opening price.
4. Keep inventory sign unscored while its trusted input/definition is unavailable. If a price-change or signed-volume variant is later chosen, label it explicitly and compare continuation conditional on the ordered band reaction, with old-POC alignment as a separate filter.

**Acceptance checks:**

- August 25, 2026 opening proximity to 29297.50 is a location observation, not a complete respected-LVN success; July 10 opening proximity is false.
- Two peaks without an intervening contiguous low-volume bridge cannot create an LVN band.
- Afternoon RTH volume must not change the old POC or overnight profile.

**Unresolved definition:** The overnight inventory formula is unpublished. The p.14 older-POC alignment is visually clear and does not select a net-inventory estimator.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-25](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A12-A-2026-08-25.png>) | true | location yes; full source respect/continuation cannot-tell | August25 open29297 sits0.50 below code overnightLVN29297.50; neighboring nodes29300.75/29301.25 drawn. Early rebound reaches29400 then fails lower. No source LVN band/two-hump/inventory/reaction sequence is scored. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A12-B-2026-07-10.png>) | false | no for open-at-LVN; broader source event unavailable | July10 nearest code LVNs29779.75,29772.75,29896.25 are far from open29834.75. The overnight trade profile is shown in its own18–09:30 scope. |

### R-A13 — Overnight reference touch statistics

The source distinguishes overnight high/low, VA edges, volume POC and geometric MPOC. The 94% figure is either extreme during RTH. For the 73% MPOC statement, the text says open inside balance while the pictured open appears below the drawn VAL; keep that condition unresolved. The tabulated half-gap pHOD cells also have an ambiguous denominator.

The current onh_or_onl event correctly uses 18:00–09:30 extremes and 09:30–16:00 touches. July 10 touches both; August 31 touches neither. The full ONVA/POC/MPOC and prior-reference conditional tables remain absent from this score. A different NQ rate does not itself contradict the cited ES study.

**Source references:** [MAMT p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p015-i1.jpeg>); [MAMT p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/mastering-amt-vp-p016-i1.jpeg>); [MAMT p.21 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p021.png>); [MAMT p.22 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p022.png>); [MAMT p.23 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p023.png>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [recipe_score.py::_preds.a13](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:649>), [FORMULAS.md::R-A13](</workspace/planning/phase-1-live/FORMULAS.md:954>).

**Build steps:**

1. Preserve the existing full-RTH either-extreme row and publish both, either, high-only, low-only and neither counts from the same eligible sessions. Verify actual overlaps or use one-sided reach only where opening location guarantees the approach side.
2. Add separately scoped ONVAH/ONVAL/ONVPOC from the completed overnight trade profile. Define MPOC=(ONH+ONL)/2 and never alias it to volume POC.
3. Keep the 73% balance-versus-profile-range ambiguity source-stopped; expose both named open-location variants for comparison only after a specification choice. Compute targets after the opening eligibility observation.
4. Reproduce each p.21–23 row with its stated open-location denominator, instrument and horizon. Retain pHOD/pLOD-to-open half gaps separately from close-to-open gaps; do not infer a success rate from the ambiguous duplicate cells.

**Acceptance checks:**

- July 10, 2026 ONH 29964.25 and ONL 29717.25 are reached; August 31 ONH 29546.25 and ONL 29273.50 remain untouched in RTH.
- MPOC must differ from POC when the distribution is asymmetric.
- An extreme first reached after noon remains a full-RTH success.

**Chart decision needed:** For MAMT p.16, resolve balance versus the full ETH profile range at the opening point; also clarify the half-gap table denominator before certifying those additional claims.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A13-A-2026-07-10.png>) | true | yes for either/both overnight-extreme touches | Overnight 18:00–09:30 H 29964.25 and L 29717.25 are both reached in RTH; the high is tested around 09:53 and the low around 10:32. EQ 29840.75 is geometric midpoint, distinct from the prior trade POC. |
| [B / 2026-08-31](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A13-B-2026-08-31.png>) | false | no | RTH stays strictly between overnight H 29546.25 and L 29273.50. The late rally still misses the overnight high; neither-extreme result is valid. |

### R-A14 — Prior TPO single prints, poor extremes and excess

The single-print picture marks an interior G-only strip between distributions; outer single-letter tails are excess. The poor-low figure has repeated QR at the extreme, conflicting with the prose phrase single TPO tail. The source provides 30-minute periods but no exact row size or tie algorithm.

The actual scorer is bool(tpo_poor), not the stale documented OR. family_gap builds today’s full RTH one-point occupancy and calls either one-period extreme poor. Both reviewed days show long one-period tails, and all 647 scores are true. This is neither prior-profile unfinished business nor a next-session fill/revisit/hold result.

**Source references:** [TPO3 p.3](</workspace/sources/documents/discretionary/tpo-lesson-3.pdf>); [TPO3 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p005-i1.png>); [TPO3 p.5 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-tpo-lesson-3-p005.png>); [TPO3 p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p006-i1.png>); [TPO3 p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p006-i2.png>); [TPO3 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/tpo-lesson-3-p007-i1.png>); [TPO3 p.9](</workspace/sources/documents/discretionary/tpo-lesson-3.pdf>); [C3 p.6](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>).

**Code to change:** [family_gap.py::_tpo_poor](</workspace/implementation/src/trading_research/research/phase1_live/family_gap.py:86>), [formulas_jumbo.py::a14_tpo](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:812>), [formulas_jumbo.py::a14_single_fill](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:869>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.a14](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:652>), [FORMULAS.md::R-A14](</workspace/planning/phase-1-live/FORMULAS.md:226>).

**Build steps:**

1. Source-stop the poor-extreme definition until its text/figure conflict is resolved; keep multi-period flat extremes and one-row tails as separate named candidates. Correct the audit-facing description of the actual scorer to bool(tpo_poor).
2. Build the prior completed RTH TPO on fixed 30-minute clock intervals and declared one-point rows, with a set of period identities at each row. Missing minutes cannot shift letters. Exclude open/close markers from the period count.
3. Classify interior singles only when the entire same-period run is bounded above and below by accepted multi-period distributions. Classify excess as a same-period outer tail of at least two rows. Preserve each run’s bounds and identity; excluding only the outermost price row is insufficient.
4. Maintain a later-session unfilled ledger. Measure single-run fill, poor-extreme revisit and excess rejection on first test as separate ordered outcomes, using the prior frozen object and post-touch prices. Remove the presence flag from the outcome numerator.

**Acceptance checks:**

- July 10 and January 28, 2026 one-period outer tails must not automatically become poor-extreme successes.
- A five-row outer tail is excess, while a five-row interior G-only bridge can be a single-print run; the surrounding rows decide.
- A gap through a run without observed overlap does not prove every row traded; preserve ambiguity or inspect executions.

**Chart decision needed:** Resolve TPO p.7’s QR poor-low figure versus its single-tail prose before choosing a faithful poor-extreme definition.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A14-A-2026-07-10.png>) | true | cannot-tell source poor definition; no demonstrated prior-profile outcome | Actual code one-point current-RTH TPO shows a long lower one-period tail down to the morning spike low and a short upper one-period tail. It calls poor=true; neither prior singles fill nor first-test excess hold is measured. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A14-B-2026-01-28.png>) | true | cannot-tell source poor definition; no genuine scored negative exists | Current-RTH top tail has many one-period rows and the low also has a one-period tail. Retained true again comes from extreme occupancy. All 647 eligible scores are true, so this second plot is a diagnostic rather than a fabricated negative. |

### R-A15 — Initial-balance extension and conditional continuation

The IB is the first hour. Source tables separate either, both, neither and one-side breaks; the continuation rows use the closing position conditional on the broken side. Close-based versus wick-based break remains an explicitly named interpretation.

The current single-side IB path row is a valid named close-break statistic. January 28 breaks only the low and closes below it; July 10 breaks both and is correctly negative for single-side. The continuation numerator and complete source table are missing.

**Source references:** [TPO3 p.8](</workspace/sources/documents/discretionary/tpo-lesson-3.pdf>); [MAMT p.19](</workspace/sources/documents/discretionary/mastering-amt-vp.pdf>); [MAMT p.23 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-mastering-amt-vp-p023.png>); [XF p.8](</workspace/sources/documents/jumbo/xfcmg2.pdf>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [family_clocks.py::build_clock_table](</workspace/implementation/src/trading_research/research/phase1_live/family_clocks.py:77>), [recipe_score.py::_preds.a15](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:655>), [FORMULAS.md::R-A15](</workspace/planning/phase-1-live/FORMULAS.md:963>).

**Build steps:**

1. Freeze complete 09:30–10:30 IB H/L at 10:30. Preserve the source one-second construction and explicitly compare the current one-minute extrema where coverage allows.
2. After 10:30, compute up/down/both/neither using the named close-break rule, with first complete close timestamps. Keep wick extensions separately labelled rather than pooling them.
3. For high-only, continuation is the RTH close beyond IBH; for low-only it is the close below IBL. Report numerator and denominator by side. For neither, score a later POC rotation with a declared fixed POC scope.
4. Reproduce the prior-IB/open-location and IB-containment rows individually. Publish the six-to-nine path comparison as a comparison of distinct clocks; do not transfer the cited ES frequency as a required NQ result.

**Acceptance checks:**

- January 28, 2026 IB 26205–26301 has a low-only break and a close below IBL; July 10 IB 29798–29968.50 breaks both.
- A high-only break followed by an inside close remains a single-break day but fails continuation.
- A 10:29 bar cannot be an after-IB breakout.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A15-A-2026-01-28.png>) | true | yes for named low-only IB extension and close continuation | IB H 26301 / L 26205 freezes at 10:30. The 10:34 bar closes below IBL, followed by persistent lower prices and a close below it; no high break. The source full table remains incomplete. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A15-B-2026-07-10.png>) | false | no for single-side; yes for both-side IB break | IB H 29968.50 / L 29798.00; low breaks in the 10:32 selloff and high breaks later before noon. Both-side correctly disqualifies the single-side row. |

### R-A16 — Actual ledge confluence and rejection

The source stacks an actual shelf ledge with independent references such as VWAP, old POC or a value edge, and trades the reaction at the ledge. It supplies no universal confluence distance.

Current code sets ledge=prior VAL and compares it with full-AM scalar VWAP or the same profile’s VAH. It never selects a shelf, tests touch/rejection or computes stacked-versus-lone outcomes. The full-AM VWAP is unavailable before noon.

**Source references:** [VP2 p.6](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>); [VP2 p.7](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>); [VP2 p.8](</workspace/sources/documents/discretionary/vp-lesson-2.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_jumbo.py::a16_stacked](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:877>), [formulas_jumbo.py::a16_stacked_reject](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:882>), [recipe_score.py::_preds.a16](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:616>).

**Build steps:**

1. Use actual fixed ledges from the repaired A02 shelf objects, including both sides and separately named composite profiles. Keep the source band bounds and the ledge line distinct.
2. At each candidate touch, snapshot only available confluence partners: running RTH VWAP/declared bands, prior VA edges and unretired older POCs. Apply the named 0.05×prior-VA-height distance and store the matched partner. Exclude self-confluence.
3. Measure the ledge touch and directional rejection using shelf height as the declared scale. Add absorption only through its validated tape event; absence of trustworthy tape cannot become a false negative.
4. Report rejection probability for stacked and lone eligible ledge visits with matched horizons. Replace the noon VWAP scalar in morning decisions with a causal running calculation.

**Acceptance checks:**

- January 2, 2026 retained true is only VAL/full-AM-VWAP proximity; it cannot certify a source ledge trade.
- July 10 proximity is false despite later price rotations; later VWAP values must not change an earlier decision.
- Listing a ledge itself as a partner must not make it stacked.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A16-A-2026-01-02.png>) | true | cannot-tell source ledge reaction; code proximity yes | The code pairs prior VAL 25537.50 with full-AM VWAP 25534.20, only 3.30 points apart within tR 4.825. Price traverses this region around 10:20 and returns, but no actual shelf ledge or ordered rejection is identified. Scalar VWAP is known at noon. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A16-B-2026-07-10.png>) | false | no for code confluence; source ledge event not constructed | Prior VAL 29823 is about 70.77 points from full-AM VWAP 29893.77, exceeding tR 8.1625. The plotted prior profile is July 9; the code cannot infer confluence from later RTH rotation. |

### R-A17 — Second transition beyond a profile extreme

The source requires a return to balance beyond the low-volume region, rather than a taper ending at the profile edge. It distinguishes a gradual shelf transition from an abrupt ledge; numerical ratios are named research choices.

Current code takes today’s final RTH occupied-volume bins, chooses the deepest minimum, then looks for any median-sized bin on the lighter-volume side. Dropping zero bins changes adjacency, and an arbitrary lighter side is not the source balance orientation. No event-level rejection or ledge/shelf comparison is scored.

**Source references:** [MATH p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/the-math-behind-auction-market-theory-p013-i1.jpeg>); [MATH p.15](</workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_jumbo.py::a17_second_transition](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:888>), [recipe_score.py::_preds.a17](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:619>).

**Build steps:**

1. Freeze a prior RTH or explicitly named composite profile before the reaction window. Preserve zero-volume bins and every candidate minimum, with its price, neighbouring balance and orientation.
2. For each candidate, identify the current balance side and search beyond the candidate on the opposite side for the declared accepted-volume run. Do not substitute whichever side happens to contain less total volume; classify terminal monotone tapers separately.
3. Apply the named abrupt-step versus multi-bin-taper definitions to distinguish ledge and shelf, returning actual bounds. Make run length, volume ratios, ties and treatment of empty rows explicit.
4. At later touches, measure directional rejection conditional on second-transition presence versus absence. Report shape presence separately from the event outcome, with known_at tied to the frozen profile.

**Acceptance checks:**

- January 2 and July 10, 2026 chart minima come from final RTH; neither may be used as a 09:30 feature.
- Inserting a real empty price bin changes the geometry and must not be erased by occupied-bin compression.
- A tail with no second balance remains a negative even if it is the lowest-volume point.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A17-A-2026-01-02.png>) | true | cannot-tell full source event; current-profile presence yes | Actual occupied-bin helper selects minimum 25616 with second_transition=1. The narrow sparse region lies between higher and lower populated regions in the final RTH trade profile. It is only known after 16:00 and is not a frozen prior-profile reaction. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A17-B-2026-07-10.png>) | false | no for current selected-minimum second transition | Actual minimum 29675.50 lies near the extreme spike low; helper second_transition=0 and tail=0. Final profile selection is retrospective, and no later reaction at a prior node is scored. |

### R-A18 — Balance-edge rejection or acceptance with unfinished targets

C3 separates interior levels from balance extremes and depicts directional bias toward unfilled destinations. It also supplies a 40% intraday value setting; the prior 70% RTH VA used here is a named balance choice.

Retained a18_single_reach falls back to AM-high≥prior-VAH. Fresh assembly differs on 386 of 668 rows. Fresh code fabricates a single above/below value, passes tick integers where the helper expects prices, and invokes the same bullish VAL rejection twice. It does not mirror the side, check a real unfilled ledger or score the target.

**Source references:** [C3 p.6](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>); [C3 p.7](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::a18_bias](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:911>), [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [recipe_score.py::_join](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:69>), [recipe_score.py::_preds.a18](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:622>).

**Build steps:**

1. Repair schema/producer validation as in A02. Remove fabricated singles and use the chronological unfilled TPO/poor-extreme ledger from A14, with price units and origin/retirement times checked at the event.
2. Define the balance profile and percentage explicitly. Exclude its interior from the trigger set. Implement four distinct side-aware branches: VAL rejection→long toward a real upper target; VAH rejection→short toward a real lower target; accepted break below→short; accepted break above→long.
3. Require the named touch/rejection or 30-minute acceptance before setting bias. Freeze the nearest valid external destination at that time and its price in price units, not tick indices. Supply proper side and mirrored arithmetic to the helper.
4. Measure post-confirmation target reach by 16:00 with invalidation and censoring. Publish bias formation and target success separately; missing real targets are unavailable observations, never a synthetic positive.

**Acceptance checks:**

- July 10, 2026 retained true is not proof of a real single target. January 10, 2025 must use only singles actually known and unfilled then.
- A tick integer around 120000 cannot be compared directly with an NQ price around 30000.
- Mirroring all prices around a fixed center must swap long/short branches and target sides, rather than calling VAL-long twice.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A18-A-2026-07-10.png>) | true | no verified source single-print setup; named VAL rejection yes | VAL 29823 rejects toward POC 29900, but no real unfilled single is drawn or supplied. Fresh calls fabricate tick integers 119949 and 119288 as price targets and both test bullish VAL rejection. Fresh and retained flags happen to be true on this date. |
| [B / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-A18-B-2025-01-10.png>) | false | no | Open 21192.50 and all RTH prices remain below prior VAL 21293 / VAH 21378.50. There is no VAL fade and no real singles ledger; fresh and retained flags are false. Synthetic inputs 85518 and 85168 are not price-unit levels. |

### R-F01 — VWAP deviation fade with absorption

The settings show Session anchor, HLC3, standard deviation and enabled 1/2 bands. Text also names 2.5/3. The p.3 handwritten upper −2/lower +2 signs are reversed relative to the settings; its description of VWAP as POC is also mathematically wrong. Preserve those source discrepancies without changing the defined weighted-mean formula.

The ETH running HLC3 geometry is implemented, but f01 ORs its touch-only flag with the final-AM trade-VWAP absorption flag. The latter fixes noon bands retrospectively. Neither branch requires local absorption at the causal ETH band, the open-draw filter, or subsequent median reach. July 10 is a touch positive with f01_vwap_fade=false; August 31 has neither flag.

**Source references:** [VWAP p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p003-i1.png>); [VWAP p.4](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>); [VWAP p.7](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>); [VWAP p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p008-i1.png>); [VWAP p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p008-i2.png>); [VWAP p.8 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vwap-lesson-10-p008-i3.png>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::running_vwap](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:32>), [recipe_score.py::_preds.f01](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:670>).

**Build steps:**

1. Retain running sums V, PV and P2V from the exchange 18:00 reopen: VWAP=PV/V; sigma=sqrt(max(P2V/V−VWAP²,0)); bands=VWAP±m×sigma. Keep the literal source sign annotation in the audit; use explicitly labelled upper/lower bands. Separate 18:00 and 09:30 anchors and each multiplier in storage.
2. For a completed-bar signal, compute touch at its completion and freeze that band price for the named absorption test; for an intrabar trigger use the previous completed band or actual streaming updates, never the final noon band. Require an actual interval overlap, not merely high>=upper when the whole candle is above it.
3. At the same band episode, require side-correct aggression within two ticks of the band, the declared two-minute q90 test, <=2-tick advance and the chosen confirmation. Evaluate an untouched draw within one sigma beyond the band using only the then-live level ledger. Label these numeric additions as research defaults.
4. Remove the OR between unrelated touch and absorption variants. Store touch, absorption, draw filter and median reach separately, measuring median reach after confirmation over the named 60-minute horizon. Publish confirmation and target rates conditional on touches, by side and anchor.

**Acceptance checks:**

- July 10, 2026 must retain ETH touch=true and final-AM absorption=false; touch alone cannot certify a fade.
- August 31, 2026 remains a no-ETH-band-touch morning although it crosses the narrower retrospectively computed AM band.
- Changing afternoon/noon trades cannot change a previously confirmed ETH-band episode. Distinct POC and VWAP must remain distinct.

**Chart decision needed:** Confirm the reversed handwritten signs on VWAP p.3 are annotation errors before certifying that particular figure; the p.8 settings define the conventional upper/lower bands.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F01-A-2026-07-10.png>) | true | band touch yes; full absorption fade unverified | ETH running upper-band touch near09:53 and lower-band contact in the10:32 spike are visible. f01_eth_touch=true while final-AM trade-band f01_vwap_fade=false. The OR score is a touch observation; no joined local absorption or later median outcome is established. Both branch geometries and legend were visually checked. |
| [B / 2026-08-31](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F01-B-2026-08-31.png>) | false | no for AM ±2 touch | AM stays between running ETH2-sigma bands, so f01_eth_touch=false. It crosses the narrower final-AM trade bands, but their absorption flag is alsofalse. This demonstrates why anchor/time population must remain explicit; both branch geometries were checked. |

### R-F02 — CVD divergence, breakout grade and absorption

The source distinguishes regular divergence, breakout participation and a delta extreme without price extension. The numerical swing, slope and exhaustion windows are research definitions. OHLC-signed volume is a different object.

The retained recipe is correctly blocked by the trade-CVD trust gate. Helpers exist, but the staged source events are not certified by a trusted FINDINGS row. The two diagnostic charts show price and executions only and cannot prove CVD divergence.

**Source references:** [VWAP p.6](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>); [FP9 p.6 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-fp-lesson-9-p006.png>).

**Code to change:** [mbp1_objects.py::cvd_from_trades](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:190>), [formulas_flow.py::r_f02_regular_div](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:119>), [formulas_flow.py::r_f02_grid_div](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:141>), [family_flow.py](</workspace/implementation/src/trading_research/research/phase1_live/family_flow.py:1>), [recipe_score.py::catalog](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:157>).

**Build steps:**

1. Preserve blocked status and a machine-readable trust reason. In a separately authorized rebuild, establish aggressor-side conventions, unknown-side treatment, contract identity, event ordering and complete session coverage before accumulating CVD=sum(buy−sell) from the declared anchor.
2. Cross-check the execution stream against the independent trade feed by date, contract, quantity and sign; store disagreement counts and eligibility. Only a passing, explicit FINDINGS trust decision may enable CVD-dependent events.
3. Then bind each price swing to the CVD value available at that swing and its confirmation time. Compare later price extremes and CVD at the same timestamp; invert the breakout-slope rule for downside breaks. Keep regular divergence, exhaustion with two later complete bars, and at-level absorption as separate observations.
4. Report event-specific denominators and timing. A CVD session-sign flag, blocked value, or unavailable swing must never become a false/no-divergence observation. Keep any OHLC-volume analogue under a separate proxy name.

**Acceptance checks:**

- July 10 and January 28 price/tape charts remain diagnostic while the trust gate is blocked.
- Prior high 110/CVD4200 followed by high110.75/CVD3950 qualifies only after the new swing is confirmed; downside mirrors reverse comparisons.
- An exhaustion definition needing two future bars has known_at at the end of the second bar, not the original spike.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F02-A-2026-07-10.png>) | unscored on this date | blocked | Price and 27 AM prints ≥30 are visible, but no trusted source CVD divergence/grade/stall event exists. Diagnostic tape is not a positive or negative. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F02-B-2026-01-28.png>) | unscored on this date | blocked | Downward AM price and 22 large prints do not establish a trusted CVD three-stage signal. Both diagnostic dates remain unscored. |

### R-F03 — Session, weekly and anchored VWAP convergence

The lesson combines the session VWAP with weekly and a swing/event anchor. An overnight mean and a prior value-area midpoint do not supply those anchors. The source gives no universal convergence distance or automatic major-swing definition.

Current code compares final AM trade VWAP, overnight trade VWAP and prior VA midpoint. December 3, 2024 gives 21201.74/21202.91/21204.125 and a true spread predicate; July 10 spreads them widely. Neither is the documented anchor set, and neither scores a confirmed touch/rejection.

**Source references:** [VWAP p.7](</workspace/sources/documents/discretionary/vwap-lesson-10.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_f03_convergence](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:224>), [family_value.py](</workspace/implementation/src/trading_research/research/phase1_live/family_value.py:1>), [recipe_score.py::_preds.f03](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:676>).

**Build steps:**

1. Create independent cumulative HLC3-volume accumulators for exchange session, Sunday 18:00 week, first trading session of month, documented event time and last confirmed five-minute swing. Store anchor timestamp and selection rule; use null for an unavailable event time.
2. At each complete minute compare session, weekly and one declared other anchor. For the named tolerance use max(VWAPs)−min(VWAPs)<=0.05×fixed prior VA height. Freeze the candidate band and anchor identities when convergence becomes observable.
3. Require a later actual two-tick band touch, then the named reversal with R equal to the available session sigma, and a separate local absorption flag. Do not replace an absent weekly anchor with a price midpoint.
4. Compare rejection rates at eligible convergences with lone-session-VWAP episodes using the same hours, confirmation, horizon and event unit. Retain the present three-scalar coincidence only under its literal name.

**Acceptance checks:**

- December 3 is a positive for the existing scalar coincidence, not for the source anchor construction.
- July 10 is a scalar-spread negative; missing source anchors keep source assessment unavailable.
- A future swing cannot move an earlier anchor, and trades after a signal cannot change its VWAP inputs.

**Unresolved definition:** The source does not publish the major-swing/event-anchor selection algorithm; a five-minute fractal is only a named research choice.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2024-12-03](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F03-A-2024-12-03.png>) | true | no certified source-anchor convergence; scalar proxy yes | Code AM VWAP 21201.74, overnight VWAP 21202.91 and prior VA mid 21204.125 are close; price oscillates around them. The AM scalar is known at noon, and neither weekly nor swing/event anchor is supplied. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F03-B-2026-07-10.png>) | false | no for scalar proxy; source anchors unavailable | AM VWAP 29893.77 / ON VWAP 29849.86 / prior VA mid 29904.625 are widely separated. Running ETH band is context, not the three producer scalars. |

### R-F04 — Per-candle diagonal stack and later revisit

FP8 p.5 highlights ask cells 220/410/512 while the printed diagonal bids 4120/3980/2110 do not satisfy the described 3–4× rule. FORMULAS resolves this by calling the drawing illustrative, contrary to the instruction to stop on a source/figure conflict. The conflict must remain open.

The helper named candle_stack is called on the entire current RTH profile; an AM min/max overlap is then ORed with the old whole-AM footprint flag. July 10 is true even though the returned RTH zone 30075.50–30077.50 is never reached in AM. No later departure, revisit or hold is established.

**Source references:** [FP8 p.4](</workspace/sources/documents/discretionary/fp-lesson-8.pdf>); [FP8 p.5 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-fp-lesson-8-p005.png>); [FP8 p.6](</workspace/sources/documents/discretionary/fp-lesson-8.pdf>); [FP8 p.7](</workspace/sources/documents/discretionary/fp-lesson-8.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_f04_candle_stack](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:251>), [formulas_flow.py::r_f04_revisit_hold](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:300>), [mbp1_objects.py::footprint_4x](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:303>), [FORMULAS.md::R-F04](</workspace/planning/phase-1-live/FORMULAS.md:290>).

**Build steps:**

1. Stop faithful certification until the highlighted-cell conflict is resolved. Preserve text-diagonal k=3 and k=4 as explicitly named candidates; do not silently pick the text over the picture.
2. If the text reading is selected, aggregate buy/sell executions per tick within each completed candle. Buy flag at p requires buy(p)>=k×sell(p−tick); sell requires sell(p)>=k×buy(p+tick). Handle zero opposition with positive own volume, and retain three adjacent same-side flags in one candle as a zone.
3. Freeze all zone bounds at candle completion. Search after formation for a departure of the named four ticks and a subsequent overlap; only then evaluate direction-specific rejection using the declared zone/candle R and horizon. Never use current full-RTH volume for an AM zone.
4. Remove the whole-AM OR shortcut. Publish stack presence, later revisit and subsequent hold as separate events, with eligible formed zones as the initial denominator and censored end-of-session observations explicit.

**Acceptance checks:**

- July 10 returned RTH zone cannot count as an AM revisit; October 8 zone25343–25344 is also above the AM maximum.
- Three flags split across two candles do not form a one-candle stack; three adjacent prices in one candle can.
- The literal p.5 highlighted cells fail the text ratio and must keep source_ok=no until clarified.

**Chart decision needed:** Resolve FP8 p.5 highlighted asks versus printed diagonal bids; which numerical cells or comparison rule in the figure is wrong?

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F04-A-2026-07-10.png>) | true | cannot-tell source stack conflict; no demonstrated later candle-zone hold | Full-RTH helper stack zone 30075.50–30077.50 lies above all AM prices, yet retained true is supplied by OR with the old AM footprint flag. The chart shows full-RTH buy/sell ladder, not an individual candle stack. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F04-B-2025-10-08.png>) | false | cannot-tell source stack conflict; code negative | Full-RTH stack zone 25343–25344 is above AM high near 25260, so no AM return to that zone. No source per-candle leave/revisit/hold is constructed. |

### R-F05 — At-level delta disagreement and intrabar POC flip

FP9 p.5 explicitly describes the flip as living inside a single candle. Its BEFORE/AFTER seven-row profiles show the POC moving from the sixth row to the second row within that candle. FORMULAS instead specifies adjacent candles, which is a different construction. The source sequence is location, absorption and flip; exact high/low position cutoffs are not printed.

The producer treats the entire AM as one candle and scores price/delta disagreement only. July 10 O29834.75/C29944.25 with delta−443 is true; January 2 falls with delta−457 and is false. Full-RTH POC is passed to the helper but does not affect the scored disagreement fields; the defect is missing candle/level/flip chronology, not a direct POC dependency of that flag.

**Source references:** [FP9 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/fp-lesson-9-p004-i1.png>); [FP9 p.5 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-fp-lesson-9-p005.png>); [FP9 p.7](</workspace/sources/documents/discretionary/fp-lesson-9.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_f05_absorption_stack](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:312>), [recipe_score.py::_preds.f05](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:682>).

**Build steps:**

1. Correct FORMULAS: source POC flip is intrabar. Preserve adjacent completed-candle POC movement only as a separately named variant. Record the source candle type and any one-minute substitute explicitly.
2. For each declared candle, process executions in time order and maintain open, current high/low/last, cumulative signed delta and the full per-tick cumulative volume profile. At a known level, record the first as-of state with upward price and negative delta, or downward price and positive delta. Keep missing/unknown aggressor volume separate.
3. After that absorption state, track POC changes within the same candle. Require an actual POC price move in the intended direction, together with the named lower-to-upper position change; do not create a flip solely because the running candle bounds expanded. Store both profile snapshots, the contributing executions and the timestamp of the qualifying update. Halves/thirds remain explicit research variants pending a source decision.
4. Measure the named0.25×fixed balance-height reversal within15minutes after the observed flip, separately from disagreement-only outcomes. A final-AM delta sign or a POC change between two completed candles cannot satisfy the source intrabar event.

**Acceptance checks:**

- July10 remains only a whole-AM disagreement in the current producer; no intrabar flip is constructed.
- The FP9 p.5 lower-sixth-row to upper-second-row example must be representable inside one candle; identical completed POCs across candles do not refute an intrabar move.
- An adjacent-candle POC jump with no intrabar transition is a separate variant. Expanding the high/low range without changing POC price cannot create a flip.

**Unresolved definition:** FP9 p.5 establishes the same-candle POC flip but does not specify halves versus thirds as the numerical position cutoffs.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F05-A-2026-07-10.png>) | true | yes only for AM direction/delta disagreement | AM first/last trade 29834.75→29944.25 with signed delta −443 yields a bullish-price/negative-delta aggregate. Final RTH POC 30050 is not an adjacent one-minute POC flip. |
| [B / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F05-B-2026-01-02.png>) | false | no for AM direction/delta disagreement | AM 25687→25341 and delta −457 agree down; the aggregate flag is false. Final RTH POC 25388 cannot substitute for the source two-candle flip. |

### R-F06 — Side-specific aggression absorbed at a marked level

The source requires aggression into a previously marked level, little progress and a reversal. It distinguishes exhaustion and visible replenishment. Three ticks is an illustrated zone; q90, two minutes and 0.25R are research defaults. FORMULAS has an arithmetic error: 17.5 exceeds 0.25×67.75=16.9375.

The current prior-VA scan uses two-minute aggression summed across all prices, then future 15-minute extrema. On August 21 its first true print is 09:31:59 at29402.50 near VAH29402, with buy4610/sell3892; the incoming path is already descending from above. This does not verify buyer aggression arriving upward into the band. Shelves, old extremes, local delta, speed and exhaustion states are not joined.

**Source references:** [DOM6 p.3](</workspace/sources/documents/discretionary/dom-lesson-6.pdf>); [DOM6 p.4](</workspace/sources/documents/discretionary/dom-lesson-6.pdf>); [DOM6 p.6 vector](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vector-dom-lesson-6-p006.png>); [DOM6 p.7](</workspace/sources/documents/discretionary/dom-lesson-6.pdf>); [DOM5 p.6](</workspace/sources/documents/discretionary/dom-lesson-5.pdf>).

**Code to change:** [mbp1_objects.py::_roll_aggressive](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:266>), [mbp1_objects.py::_absorption_a_scan](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:25>), [mbp1_objects.py::absorption_a](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:277>), [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_f06_dom_absorption](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:344>), [FORMULAS.md::R-F06 fixture](</workspace/planning/phase-1-live/FORMULAS.md:308>).

**Build steps:**

1. Freeze each marked level and its own R before approach. Retain separate prior VA, profile ledge, prior H/L and session-box objects. Define a side-specific arrival episode; a fall into VAH from above is not automatically a buy-into-resistance test.
2. For the named two-minute window count only aggressive volume of the approaching side inside the level band, preserving buy/sell/unknown quantities. Apply the frozen discovery q90 in the matching volume unit, maximum outward advance<=2 ticks, and store the actual contributing executions.
3. After the stall, evaluate >=0.25R reversal within 15 minutes and timestamp its confirmation. Attach local signed delta, causal 30-second speed and the previous-window exhaustion comparison separately. Keep displayed-size reload blocked under its existing trust/input gate.
4. Score levels and sides separately, distinguishing stall, confirmed reversal and reload. Correct the fixture: 17.5 fails for R251 but passes for R67.75. Do not reuse one range height for unrelated level families.

**Acceptance checks:**

- August 21 first true legacy scan must be labelled all-price aggression; inspect local band flow before any source-positive classification.
- July 10 has no true legacy prior-VA absorption scan; a volume spike elsewhere must not create one.
- 17.5>=16.9375 is true. Removing remote-price executions must not remove a genuinely local absorption event.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-21](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F06-A-2026-08-21.png>) | true | code absorption observation yes; source-local absorption unverified | Original scan first qualifies at 09:31:59 near VAH 29402, print 29402.50, global two-minute buy/sell totals 4610/3892. Next-15-minute maximum 29402.50 and minimum 29307.75 satisfy the code. Price arrives from above during a selloff; local buyer aggression at the level is not demonstrated by the global totals. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F06-B-2026-07-10.png>) | false | no for actual absorption-A scan | Repeated VA/POC rotations and large prints do not satisfy the frozen-q90 scan at either prior value edge. The instrumented original scan and original boolean agree false. |

### R-F07 — At-touch reload inference and iceberg limitation

The source differentiates size that replenishes as trades execute from quotes that disappear before trading, then waits for added participation. MBP-1 can support a limited at-touch quote/trade inference; it cannot identify hidden reserve size or off-touch depth as fact.

The retained iceberg recipe remains blocked. Existing BBO reload flags saturate and do not establish the source sequence. Available diagnostic executions on July10/January28 are insufficient to certify an iceberg, and no depth substitute was plotted.

**Source references:** [DOM7 p.3](</workspace/sources/documents/discretionary/dom-lesson-7.pdf>); [DOM7 p.4](</workspace/sources/documents/discretionary/dom-lesson-7.pdf>); [DOM7 p.5](</workspace/sources/documents/discretionary/dom-lesson-7.pdf>).

**Code to change:** [mbp1_objects.py::iceberg_touch_infer](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:243>), [mbp1_objects.py::absorption_b](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:216>), [recipe_score.py::catalog](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:157>), [FINDINGS.md](</workspace/planning/phase-1-live/FINDINGS.md:1>).

**Build steps:**

1. Retain blocked status and distinguish data limitations from failed validation. Do not acquire or fabricate MBP-10/MBO in this audit. If a future task enables an at-touch inference, explicitly name it BBO reload evidence rather than identified iceberg size.
2. Join each execution with the last valid pre-trade displayed quantity at exactly the traded BBO price. Require positive displayed size, trade size exceeding the chosen ratio and a later same-price replenishment within the named 500ms window; reject stale/crossed/missing quotes.
3. Count distinct execution/replenishment cycles at the same level, with the named two-cycle threshold, price hold and subsequent participation within two ticks. A cancelled quote without execution must not count as replenishment. Store raw timestamps and causal quote provenance.
4. Before unblocking, validate at-touch inference against appropriate independent evidence and publish false positives, eligible contacts and unknown observations. Keep off-touch reload unavailable unless the required depth input is actually present.

**Acceptance checks:**

- Both dated price/tape plots remain blocked for iceberg confirmation.
- A 60-lot execution against displayed25 followed by same-price28 can form one inference cycle; a disappearing25 with no execution cannot.
- Multiple snapshots of a single refresh count once, and stale display sizes cannot satisfy a cycle.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F07-A-2026-07-10.png>) | unscored on this date | blocked | Price/large-print diagnostics cannot reveal hidden iceberg identity or depth reload. No scored positive/negative is fabricated. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F07-B-2026-01-28.png>) | unscored on this date | blocked | AM selloff and print bubbles are insufficient for hidden-size replenishment. Scorer stays blocked. |

### R-F08 — Absorption location, three-tick reward and reward retest

ABS p.11 repeats the same buyer-spike/opposition-losing annotation at both edges while the VAL body text describes buyers regaining control. FORMULAS elects the body text; source/figure agreement must instead remain unresolved. The wall and reward retest are bands, and the CVD-median subcheck retains its separate trust limitation.

The producer has no absorption event ID: it takes the first AM trade as origin, the first20 trade signs as direction, and the last80 prices as reward window. January28 returns a 547-tick short reward over the morning; July10 fails with an adverse opening-to-noon move. Neither tests three ticks after absorption, local context, second aggression or reward retest.

**Source references:** [ABS p.3](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>); [ABS p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p004-i1.jpeg>); [ABS p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p006-i1.jpeg>); [ABS p.7](</workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>); [ABS p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p009-i1.jpeg>); [ABS p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/your-mistakes-with-absorption-p011-i1.jpeg>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::reward_3tick](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:366>), [formulas_flow.py::r_f08_abs_four_check](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:380>), [recipe_score.py::_preds.f08](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:688>), [FORMULAS.md::R-F08](</workspace/planning/phase-1-live/FORMULAS.md:326>).

**Build steps:**

1. Stop the conflicting p.11 sign/role classification until clarified. Preserve spike sign, active side, passive side, edge and outcome direction as separate fields; do not infer passive absorption from buy delta alone.
2. Use a qualified at-level absorption episode outside the declared POC exclusion band as origin. From its actual print/confirmation, scan executions in chronological order for three favorable ticks before more than three adverse ticks; stop at the first disqualifying excursion. The original first-AM price has no role.
3. After reward, require the named reversal-side aggression threshold from past observations and then a separate retest of the reward band. Store band bounds and exact entry-availability time. Keep CVD-median and local delta-spike comparisons blocked or separate until trusted.
4. Publish location-qualified absorption count, reward rate, retest availability and subsequent reversal separately. Do not force 27% failures or compare an unconditioned AM direction flag with that source claim.

**Acceptance checks:**

- January28 legacy true must not survive as a demonstrated absorption reward without an actual origin event.
- 120.25→120→119.75→119.50 is a three-tick short reward if adverse travel has not first exceeded three ticks.
- A path that breaches four adverse ticks then later gains three must fail the named first-passage reading; the VAL source annotation remains unresolved.

**Chart decision needed:** Resolve ABS p.11: at VAL, which side is active, which is passively absorbing, and which repeated buyer-spike caption is incorrect?

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F08-A-2026-01-28.png>) | true | cannot-tell; source role conflict; no absorption-linked event | The first-AM trade is 26252.50. The last 80 trades near noon are about 26116 and span seconds; the short-direction 547-tick reward is an opening-to-noon comparison, not three ticks after a detected absorption. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F08-B-2026-07-10.png>) | false | cannot-tell; source role conflict; no absorption-linked event | Short direction is selected from the first 20 trade signs, but last-80 prices near 29944 are above the first trade 29834.75. This explains the false aggregate result without assessing an absorption setup. |

### R-F09 — Ordered STOP defense, exhaustion and lift-off

The source stages are defense, replenishment, exhaustion and lift-off, with a two-to-four-tick reward and entry within one-to-two ticks. ES digit classes and NQ40-range illustrations are distinct. The 10-lot median threshold on NQ is a research reading, not a portable author constant.

Only first20 versus last20 AM size medians are scored. Both dated cases give1/1, and all647 observations are false. This does not establish absence of local thinning or lift-off. Replenishment remains blocked; the available stage helpers are not assembled into a chronological event.

**Source references:** [STOP p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.6 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p006-i2.png>); [STOP p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p009-i2.png>); [STOP p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.11 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.11 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.11 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p011-i2.png>); [STOP p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.12 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [STOP p.12 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/stop-re-entering-p012-i2.png>); [STOP p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [STOP p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::digits_thinning](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:402>), [formulas_flow.py::liftoff_upticks](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:406>), [formulas_flow.py::r_f09_stop_stages](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:440>), [recipe_score.py::_preds.f09](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:691>).

**Build steps:**

1. Start a stage record from a validated side-specific defense at a fixed thesis band. Store instrument and candle/tape construction. Keep literal ES digit classes separate from named NQ literal or causal-quantile classes.
2. For exhaustion compare the same aggressor side in local, successive20-print windows after defense: named median>=10 then <10, plus a completed-minute delta turn against that aggressor. Never compare all-side opening and closing prints.
3. After exhaustion scan consecutive trade-price upticks/downticks for the named2/3/4-tick reward with no intervening opposite tick. Define entry availability at the confirmation print and its one-to-two-tick band. Keep replenishment unknown; a reduced1→3→4 sequence must be labelled partial.
4. Measure stage transitions and post-confirmation0.25R reversal over15minutes with eligible prior stages as denominators. Do not equate a0/647 session-median statistic with source failure rate or the complement of27%.

**Acceptance checks:**

- July10 and January28 median1/1 cases remain negatives for the literal session-sample thinning flag only.
- An actual local sell-median15→4 with positive delta, followed by three consecutive upticks, can form the named reduced sequence.
- A missing replenishment stage stays unknown rather than automatically true; an intervening downtick restarts bullish lift-off counting.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F09-A-2026-07-10.png>) | false | no verified staged event; replenishment remains blocked | Both first-20 and last-20 size medians are 1 lot; no double-to-single thinning. Level, side, delta turn and successive reward upticks are absent from the scored observation. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F09-B-2026-01-28.png>) | false | no verified staged event; replenishment remains blocked | A falling morning and several large sell prints do not create the specified stages. The two session-end samples both have median size 1. |

### R-F10 — Protected swing after local delta and escape

The source protects successive lows/highs after local aggression, a small balance and an escape. The fractal, delta percentile and five-bar quiet period are research definitions. FORMULAS declares protection at escape even though its own five later quiet bars have not yet happened.

The score is last-five AM prints above the final AM low by two ticks, true646/647. July10 compares prices near29943.50 with29675; the only negative March28 finishes at19542, the morning low. There is no swing, local delta, escape, five-bar protection or high-side mirror.

**Source references:** [RD p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-delta-p004-i1.jpeg>); [RD p.5](</workspace/sources/documents/discretionary/reading-delta.pdf>); [K18 p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p008-i1.png>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_f10_protected_low](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:468>), [family_flow.py::_fractal_pivots](</workspace/implementation/src/trading_research/research/phase1_live/family_flow.py:34>), [recipe_score.py::_preds.f10](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:694>), [FORMULAS.md::R-F10 fixture](</workspace/planning/phase-1-live/FORMULAS.md:344>).

**Build steps:**

1. Construct confirmed2/2 one-minute fractals for the named five-bar definition, or retain the existing3/3 matcher under a distinct variant. A pivot becomes known only after all right-side bars close. Select the prior opposite swing using information available then.
2. Build per-price signed delta as of the candidate, within the low/high±2-tick band. Compare the relevant sign with the causal positive/negative per-price q75 in matching units. Then require a complete close beyond the prior opposite swing.
3. Scan the next five complete bars for no two-tick retest. Mark protection only at the last quiet-bar completion; correct the fixture timestamp from escape bar17 to quiet-confirmation bar22 completion. Implement the protected-high mirror and subsequent complete-close invalidation.
4. Track a chronological sequence of live protected levels, replacement by newly confirmed levels, first break, time-to-break and post-confirmation MFE through16:00. Report break rates conditional on protected levels, not near-universal end-of-AM distance from the minimum.

**Acceptance checks:**

- July10 legacy true must not become a protected-swing event without the missing sequence; March28 noon low has no five later bars yet.
- Changing any of the five quiet bars can affect protection only when that bar becomes available.
- A final five-print sample spanning19ms is never a substitute for five complete one-minute bars.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F10-A-2026-07-10.png>) | true | no verified protected-swing sequence | Final AM low is 29675; final five prints are near 29943.50. The large separation makes the flag true without a confirmed swing, local positive delta, escape or five complete quiet bars. |
| [B / 2025-03-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F10-B-2025-03-28.png>) | false | no at noon; no complete quiet window | The last five prints include the final AM low 19542 and span about 19 milliseconds. The false result is a last-trade proximity observation; the new noon low cannot yet be protected by five later bars. |

### R-F11 — Delta-print pairing with an LVN at a balance extreme

The source pairs concentrated signed delta with a low/minor volume node at either balance extreme and shows repeated wick reactions. It does not equate a volume POC with a delta print. The node detector, tolerance and reversal fraction in FORMULAS are research rules; its fixture separates a wick rejection from a much larger0.5R follow-through.

The score pairs full-current-RTH volume POC with an LVN in that same final profile. July23 POC28810 lies next to LVN28810.25; July10 POC30050 is far from the nearest LVNs. No signed-delta extremum, as-of dealing range, touch, wick reaction or repeat count is used.

**Source references:** [RD p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-delta-p007-i1.jpeg>); [RD p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/reading-delta-p001-i2.jpeg>); [RD p.10](</workspace/sources/documents/discretionary/reading-delta.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [family_value.py::scan_rth_delta](</workspace/implementation/src/trading_research/research/phase1_live/family_value.py:54>), [formulas_flow.py::r_f11_delta_lvn](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:512>), [formulas_jumbo.py::profile_nodes](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:153>), [recipe_score.py::_preds.f11](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:697>).

**Build steps:**

1. Require a fixed or causally developing dealing-range episode with explicit start, bounds and confirmation. Build volume and signed-delta profiles over the identical executed-trade population available before each candidate; retain the literal source profile scope.
2. Find dp.max as price of maximum positive delta and dp.min as price of most negative delta, preserving ties. Pair only a same-profile LVN/minor-node extreme within named0.05×range height; do not substitute the volume POC. Keep the node detector and zero-bin grid explicit.
3. For each paired level scan independent visits. Record a >=2-tick wick through the level with complete close back, then separately measure0.5R follow-through within five minutes. A wick-only source reaction must not inherit the stricter follow-through label.
4. Count repeated reactions per fixed zone through16:00, requiring departure/reset between visits. Report paired levels, touched levels, wick reactions and follow-through conditional counts, with no use of afternoon profile data in morning features.

**Acceptance checks:**

- July23 proximity of volumePOC28810 to LVN28810.25 is not evidence of a delta-print pairing.
- The FORMULAS118.25 example closing117.5 is wick-only; it fails a10-point follow-through requirement.
- Two adjacent wick bars in one visit count once, and future volume cannot relocate an already tested fixed node.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-23](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F11-A-2026-07-23.png>) | true | no verified delta/LVN pairing | Full-RTH volume POC 28810 is within one tick of an LVN 28810.25 and within two ticks of 28809.50. These end-of-day volume objects are back-drawn into AM; no delta-print level or repeated source reaction is computed. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F11-B-2026-07-10.png>) | false | no verified delta/LVN pairing | Full-RTH POC 30050 lies over 20 points from the nearest selected LVNs 30070.25/30070.75/30071.75, outside the code tolerance. This is a volume-node distance negative, not a delta-reaction negative. |

### R-F12 — Aggressive or drifting approach to a balance band

The source judges how price arrives at an extreme and later confirms a genuine break/retest. It draws bands and names a15-minute check. Five-minute speed, volume slope and percentile cuts are research definitions, not values supplied by the lesson.

The score compares median size of the last five AM prints with the first five. Equality1=1 makes July10 aggressive; August28 gives2→1 and false. Neither identifies arrival at an extreme or uses displacement, directional volume, five-minute bins or the15-minute confirmation.

**Source references:** [WIC p.4](</workspace/sources/documents/discretionary/whos-in-control.pdf>); [WIC p.5](</workspace/sources/documents/discretionary/whos-in-control.pdf>); [WIC p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/whos-in-control-p001-i2.jpeg>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_f12_arrival](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:541>), [recipe_score.py::_preds.f12](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:700>).

**Build steps:**

1. Freeze the eligible prior-value/dealing-range band and its break/retest state. Find the first actual approach touch, with approach direction and feature cutoff before that touch. Use the drawn band identity rather than replacing every extreme with a zero-width line.
2. For the named five-minute variant compute toward-level displacement in ticks/minute from complete minute closes and toward-level aggressive volume in each minute. Compare speed with causal prior-approach q75/q25; classify aggressive only when speed>=q75 and the five-bin volume slope>=0, drift when speed<=q25 or slope<0, otherwise mixed.
3. Store the source15-minute confirmation separately with known_at at bar completion. From touch onward test rejection versus a complete break plus30-minute outside hold, preserving which side of the band is defended.
4. Report outcomes conditional on class and eligible break/retest context. Remove the first/last-five median shortcut; retain missing five-minute tape coverage or unavailable prior quantiles as unknown.

**Acceptance checks:**

- July10 equal one-lot medians cannot establish an aggressive arrival.
- An identical final five-print sample at a different hour cannot change a previously classified approach.
- Rapid price approach with falling directional volume and slow approach with rising volume must remain distinguishable; neither is an automatic source signal.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F12-A-2026-07-10.png>) | true | no demonstrated aggressive arrival | The first-five and last-five size medians are both 1; equality is scored as aggressive. The chart does not identify a five-minute approach to a particular balance band. |
| [B / 2026-08-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F12-B-2026-08-28.png>) | false | no demonstrated class-specific level event | The first-five median is 2 lots and last-five median 1. The negative is a session-wide size comparison, with no speed or band-arrival outcome. |

### R-F13 — Prior-session trapped aggression and later break/retest

The source aligns a balance with traded structure, shows heavy buying at its upper extreme, two failures in prior AM/PM, and a later intraday break followed by a body-aggression retest. Both sides are a documented mirror; the150–160-point Asia remark is illustrative.

Current code is wired to the high-side helper, but substitutes prior RTH high, maximum AM price as dp.max and the same current-AM high for both AM and PM failures. It passes min(AM closes) as break_close and min(AM lows) as intra_lo; break_close<intra_lo is impossible for valid bars. The pairing result is ignored and the low mirror is absent.

**Source references:** [TRAP p.3](</workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>); [TRAP p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p004-i1.jpeg>); [TRAP p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p005-i1.jpeg>); [TRAP p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p006-i1.jpeg>); [TRAP p.8](</workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>); [TRAP p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/trapped-buyers-one-retest-p009-i1.jpeg>).

**Code to change:** [family_tape.py::_ofm_and_trap](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:246>), [formulas_flow.py::r_f13_trapped_buyers](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:566>), [recipe_score.py::_preds.f13](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:703>).

**Build steps:**

1. Create the declared causally redrawn balance from confirmed swings and preserve each version. Freeze the relevant prior-session signed delta profile and select its positive/negative extreme within named0.05R. A maximum traded price is not dp.max.
2. Find distinct actual band touches in prior AM and prior PM, with no qualifying outward close, using the same fixed level. Store both episode timestamps; one current AM aggregate cannot fill both roles. Require the trap-delta pairing rather than merely compute and discard it.
3. Freeze the current intraday range at its own confirmation. Search strictly later for a close through it, a separate retest from the outside and an actual same-side aggressive execution inside the retest candle body, followed by the named rejection. Build the low-side mirror with reversed inequalities.
4. Measure retest availability, hold and subsequent target reach from those events. Choose any Asia statistical target using past sessions, not the illustrative150–160 points. Remove the impossible whole-window-minimum break comparison and publish prior-pattern eligibility as the denominator.

**Acceptance checks:**

- For every valid OHLC array min(close)>=min(low); the present strict break comparison cannot be a positive event.
- July10 and January28 zero flags do not demonstrate absence of source traps.
- A prior AM failure and a distinct prior PM failure can qualify; duplicating one failure cannot. A later actual break below a frozen earlier low is possible.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F13-A-2026-07-10.png>) | false | no verified source trap setup | PDH 29993.50 remains above AM high; no two prior AM/PM failures or daily delta extreme is supplied. Actual code uses same-AM extrema and cannot make min(close)<min(low) for its breakout. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F13-B-2026-01-28.png>) | false | no verified source trap setup | Price starts above PDH 26114.25 and reaches it near 11:50. This is not the source prior two-session upper failure and subsequent intraday breakout/retest. All 647 retained flags are false; no true positive exists in this implementation. |

### R-F14 — Colocated BigTrades imbalance, body/wick and retest

The figures use NQ40-range bars and30–60 display settings, with a350% imbalance line attached to the aggression print. Body prints are rewarded and wick prints absorbed. A one-minute substitute is a named variant. The wording350 percent more and a3.5× platform ratio should not be silently treated as a resolved numerical identity.

The code takes any same-price3.5× imbalance in the entire current RTH, then ANDs it with an independent Jumbo-level BigTrades flag. March9 is true without a matched candle, price or side. July10 is false because the independent Jumbo flag is false. There is no body/wick classification, matching print or later retest.

**Source references:** [BIG p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p003-i1.jpeg>); [BIG p.4](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>); [BIG p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p005-i1.jpeg>); [BIG p.6](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_f14_imb350](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:589>), [recipe_score.py::_preds.f14](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:706>), [FORMULAS.md::R-F14](</workspace/planning/phase-1-live/FORMULAS.md:380>).

**Build steps:**

1. Preserve the source40-range chart construction and print-display settings. Specify range-bar formation and the meaning of the display maximum before author-exact reconstruction; build a one-minute variant only under that name. Resolve3.5× platform ratio versus literal4.5× reading if numerical source certification is required.
2. Within each completed candle compute same-price buy/sell totals and select the actual30–60-lot print under the literal display reading, with>=30 separately named. Require the relevant same-side imbalance at that exact price and nonzero own-side quantity; do not join an unrelated Jumbo print.
3. Classify each print against its own candle body interval, preserving side, price and completion time. Keep rewarded-body and absorbed-wick events separate. At both-side wick absorption record waiting status until a later confirmed range break.
4. Freeze the print line and optional named body area. Require departure then actual retest overlap before evaluating direction-specific0.5×candle-range rejection within15minutes. The helper must check retest contact, not merely receive an unused retest_high argument. Report matched prints, retests and outcomes separately.

**Acceptance checks:**

- March9 current true must be labelled an aggregate conjunction until a same-candle/same-price print is identified.
- A sell40 at100.5 inside body[100.25,101] is rewarded; a sell45 at100.10 is absorbed, even in the same candle.
- A favorable later close without a retest of the saved line cannot count as retest-reject.

**Chart decision needed:** Confirm the40-range bar construction, whether60 is a display cap, and whether the350% platform threshold means3.5× opposing volume; these are not determined by the one-minute implementation.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-03-09](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F14-A-2026-03-09.png>) | true | no verified colocated source print/imbalance/retest | The chart shows actual full-RTH buy/sell volumes and independent Jumbo EQ 24399.625 and 0.5 extensions. An imbalance somewhere in that final profile plus a separate Jumbo print cannot establish the source same-candle, same-price event. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F14-B-2026-07-10.png>) | false | no verified source event | Many AM prints and later full-RTH imbalance rows exist, but the independent Jumbo BigTrades flag is false. No same-print body/wick confirmation or post-creation retest is scored. |

### R-F15 — Ordered catalyst, failed squeeze, refill and re-squeeze

The source distinguishes the first absorbed aggression line from its box and requires a failed attempt before the re-squeeze. The drawings show both long and short versions; entries on the first failure are a different event. The five-minute cluster,0.1R and30-second speed quantile are research definitions. Short-gamma and CVD checks need their own trustworthy, causally available inputs.

The current helper is wired, contrary to stale FORMULAS text, but ofm_entry uses only a comparison of resqueeze_close with fail_wick; it ignores the computed release, failure, refill and tape flags. The caller supplies final-AM extrema, last-eight wick prints and6–9 swings without event order. Retained F15 differs from fresh tape on22/33 replay dates; July10 and source-dateJuly9 are retained true but fresh false with no qualifying catalyst.

**Source references:** [OFM p.2 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.2 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.4 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p004-i2.png>); [OFM p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.5 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p005-i2.png>); [OFM p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.6 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p006-i2.png>); [OFM p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.7 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p007-i2.png>); [OFM p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.8 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p008-i2.png>); [OFM p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.9 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p009-i2.png>); [OFM p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.10 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p010-i2.png>); [OFM p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.14 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p014-i2.png>); [BIG p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p007-i1.jpeg>); [BIG p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p008-i1.jpeg>); [BIG p.14](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>); [BIG p.18](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>); [CONT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p010-i1.jpeg>).

**Code to change:** [family_tape.py::_ofm_and_trap](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:246>), [formulas_flow.py::r_f15_ofm](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:617>), [recipe_score.py::_preds.f15](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:709>), [FORMULAS.md::R-F15](</workspace/planning/phase-1-live/FORMULAS.md:389>).

**Build steps:**

1. Invalidate affected tape caches using producer/source/input/schema identity. Build a causally confirmed dealing-range swing, then same-side wick-print clusters in the named five-minute window near that swing. Retain all qualifying prints in time order; mark the first absorbed print line and separate area[first print,extreme]. Do not substitute the final eight AM prints.
2. Implement a state machine per cluster and side: catalyst known→fast release beyond the extreme→later complete close back through the catalyst→later refill/retest→re-squeeze beyond the failure wicks. Persist each transition and reset on invalidation. Calculate tape speed at release using only the past30seconds and a baseline available then.
3. Require all prerequisite states for ofm_entry. Select direction explicitly from the intended swing/side rather than its incidental position inside the catalyst. Require trustworthy short-gamma scenario/context and CVD/HTF prerequisites as separate gates; unknown inputs yield partial/unknown eligibility.
4. At confirmed entry freeze the stop beyond the actual aggression, compute R=abs(entry−stop)>0, and measure directional post-entry1R/2R/3R reach through the declared horizon. Do not use the maximum of long and short MFE. Report setup frequency, retest availability and conditional outcomes separately.

**Acceptance checks:**

- July10 and July9 retained positives must display fresh=false and cannot support the published470/647 frequency under current code.
- A close beyond a wick with no preceding failure/refill must fail OFM even when it qualifies as a separate squeeze.
- Changing earlier whole-AM extrema cannot create a stage out of order; a mirrored short sequence uses its own directional stop and MFE.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F15-A-2026-07-10.png>) | true | no verified source OFM; fresh code false | Retained title true differs from fresh false. The last-eight wick-print selection yields no qualifying six-to-nine catalyst. No ordered release→failure→refill→re-squeeze is present in the producer inputs. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F15-B-2025-10-08.png>) | false | no verified source OFM; fresh code false | Upward AM path alone is not OFM. Current catalyst selection is empty; retained and fresh false agree on this date. Whole-AM extrema cannot establish ordered stages. |
| [source-date / 2026-07-09](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F15-source-date-2026-07-09.png>) | true | no fresh catalyst; source sequence not reproduced | Source-date morning rises, reverses around10:15 and recovers, but current6–9/last-eight-print construction yields no catalyst. Retained true differs from fresh false; visual resemblance does not certify failed-squeeze/refill stages. |

### R-F16 — Failed aggression at a balance edge, then fade retest

The source fades a retest of failed aggression at either edge and targets the last area where the opposite side was rewarded. Its drawn9-point stop/33-point target is an annotation, not a filled trade or a universal bracket. Long-gamma context is separate from a balance-day label.

The current helper has both mirrors, but the caller supplies6–9 extremes, wick counts from all AM, a whole-AM no-close condition, unordered extrema for departure/return and an absorption-any-side flag. Its leave test can be satisfied by distance from the opposite edge. The target is the opposite6–9 edge rather than the prior rewarded opposite print. Both selected cases are false under the substitute geometry.

**Source references:** [BIG p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p015-i1.jpeg>); [BIG p.16 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/only-trade-big-trades-p016-i1.jpeg>); [BIG p.18](</workspace/sources/documents/discretionary/only-trade-big-trades.pdf>).

**Code to change:** [family_tape.py::_ofm_and_trap](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:246>), [formulas_flow.py::r_f16_balance_fade](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:671>), [recipe_score.py::_preds.f16](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:712>).

**Build steps:**

1. Fix a causally known dealing-range edge and its local wick-aggression area. Require qualifying failed aggression at that edge and no complete outward close over the named15minutes. Preserve the declared time/range-bar variant and avoid counting remote wick prints.
2. After failure confirmation require price to leave toward the interior by>=0.25R measured from the tested edge only. Find a later actual retest of that saved area. At that retest require side-correct local absorption; an absorption at the opposite edge or earlier in AM cannot qualify.
3. Before the failed extreme, identify the latest opposite-side body print that was rewarded and freeze its price as target. Use long-gamma context only if its scenario and timestamp pass R01; a normal/neutral day label is a separate retrospective or causal variant, with its availability stated.
4. Score retest confirmation and subsequent target reach through16:00, conditional on failed edge aggression. Keep both mirrors, event order, band penetration and invalidation explicit; do not substitute fixed R multiples or the opposite box edge for the source target.

**Acceptance checks:**

- July10 closes through both6–9 extremes, and January28 does not supply the named upper-edge retest; current false values are not author-pattern incidence estimates.
- At upper120 in range100–120, a departure to119 is only1point, not a5point departure merely because it is19points from the lower edge.
- A source target112.5 from prior rewarded selling remains112.5 even if the range low is100; target touches before the retest do not count.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F16-A-2026-07-10.png>) | false | no named 6–9 fade; source dealing-range setup unbuilt | Price closes well above 6–9 high 29887.75 and below low 29771.25. The code no-close-beyond conditions fail; this is not a test of an as-of dealing range and its local absorption retest. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F16-B-2026-01-28.png>) | false | no named 6–9 fade; source dealing-range setup unbuilt | AM never reaches 6–9 high 26326.75 and trades through low 26255.25. The top return and bottom no-close-beyond conditions fail. The source target at the last rewarded opposite print is absent. |

### R-F17 — Refill-zone formation, return and held response

The source pools NQ/MNQ; its datedJanuary10 example is MNQ with>=40 displayed, while text mentions60/80/100 in seconds. Per-print versus burst, exact formation window, defender side and hold denominator are not uniquely specified. The12/32/96 bracket is an execution illustration, not a definition proving the42% hold statistic.

Current on_touch_refill requires>=100-lot prints in a two-minute,<=2-tick cluster, checks only the first three signs and can include later opposite-side prints in its bounds. It waits until two minutes after cluster start, then departure in the large-print direction and any later return. January23 produces21928.25–21928.75 and a return near11:23; there is no hold/penetration outcome. January10 NQ is not the MNQ source reconstruction.

**Source references:** [REF p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.5 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p005-i2.png>); [REF p.5 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p005-i3.png>); [REF p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.7 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p007-i2.png>); [REF p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.10 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p010-i2.png>); [REF p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.12 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.12 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p012-i2.png>); [REF p.17 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.17 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.17 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p017-i2.png>); [REF p.18 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.18 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [REF p.18 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p018-i2.png>); [REF p.18 fig.4](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/refill-effect-p018-i3.png>); [REF p.23 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [REF p.23 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>).

**Code to change:** [mbp1_objects.py::on_touch_refill](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:335>), [formulas_flow.py::r_f17_refill_zone](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:694>), [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [recipe_score.py::_preds.f17](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:715>).

**Build steps:**

1. Keep author-exact certification open until instrument units, per-print/burst interpretation, clustering, defended side and hold definition are resolved. Preserve the present NQ100-lot/two-minute/two-tick revisit under its literal variant name. Do not use NQ executions as MNQ screenshot evidence.
2. For a chosen variant, cluster only the declared side and retain all contributing executions and price bounds. Use actual completion/last qualifying print time as known_at; a rolling cluster must not grow retrospectively after being tested. Make any three-print,30-second,60/80/100 choices explicit parameters.
3. After completed formation require a declared departure and a distinct return, recording the side from observed defense rather than assuming active buy always means passive sellers or vice versa. Match leave direction between producer and helper; the current functions use opposite side conventions.
4. Measure penetration, close-through, subsequent departure and censoring as distinct touch outcomes. Keep the named32-tick/30-minute/12-tick research measurement separate from the12/32/96 execution bracket and from the source42% claim. Add memory/location/flow features frozen at each touch; report per-touch denominators.

**Acceptance checks:**

- January23 qualifies as the current revisit variant, but a later return alone does not prove a hold.
- The sourceJanuary10 MNQ chart remains an instrument mismatch against the NQ diagnostic; no false source-negative conclusion is allowed.
- A fourth opposite-side large print cannot silently widen a same-side zone; the source hold definition must be resolved before comparing42%.

**Unresolved definition:** NQ versus MNQ units, per-print versus burst aggregation, cluster width/window, defending side and the denominator behind42% need a declared definition; the source bracket does not publish all of them.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2025-01-23](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F17-A-2025-01-23.png>) | true | yes for implemented revisit variant; source hold unscored | Code cluster is 21928.25–21928.75. After an upward departure, price returns near 11:23 before moving higher. The source instrument/threshold differs, and the code does not grade penetration, 30-minute hold or later 12-tick departure. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F17-B-2026-07-10.png>) | false | no implemented cluster; source reading unresolved | No qualifying >=100-lot, <=2-tick cluster with the required departure/return is found. Visible >=30-lot prints do not satisfy the code cluster rule. |
| [source-date / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F17-source-date-2025-01-10.png>) | false | cannot-tell: NQ diagnostic versus MNQ source figure | Source example is MNQ>=40 display at09:36–09:44. This NQ tape has no qualifying current100-lot/two-minute/two-tick revisit. NQ prints and falling price cannot prove or refute the MNQ zone. |

### R-F18 — Fast squeeze without the prior failure

The source fast squeeze proceeds without the failed first attempt of OFM. It then absorbs opposing aggression at the first pullback. Speed of Tape(10) is visible but the unit of10 is not stated;30seconds, q90 and the15-minute no-failure interval are named choices.

Current code is wired but the helper ignores release_close and catalyst in its trigger logic. It uses last30seconds of AM speed versus a whole-AM threshold, no-close-through over all AM and the independent prior-VA absorption flag. Continuation is computed but not scored. Fresh replay changes26/33 dates, and July10 retained true is fresh false with no catalyst.

**Source references:** [CONT p.11](</workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>); [OFM p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.5 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p005-i2.png>); [OFM p.14 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [OFM p.14 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [OFM p.14 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/origin-of-the-move-p014-i2.png>).

**Code to change:** [family_tape.py::_ofm_and_trap](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:246>), [formulas_flow.py::r_f18_squeeze](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:734>), [formulas_flow.py::tape_speed_pps](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:48>), [recipe_score.py::_preds.f18](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:718>).

**Build steps:**

1. Invalidate stale tape rows as in F15. Build the same causally frozen catalyst object, but route a release into the no-failure branch rather than requiring OFM failure/refill. Require a complete close beyond the relevant extreme and side-correct fast tape at that release.
2. Compute the named30-second print rate and q90 from only prior observations. Preserve the unresolved10-unit source setting as metadata. Search only after release for a close back through the catalyst; for a15-minute no-failure prerequisite, its known_at cannot precede the end of that interval.
3. After confirmed no-failure state, require the first qualifying pullback and opposing aggression absorbed locally there. Define explicitly whether a pullback before the15-minute confirmation is deferred or starts a separate shorter-window variant; never use unrelated morning VA absorption.
4. Freeze the next eligible source level in the squeeze direction at trigger, then measure actual interval overlap and directional MFE afterward through16:00. Score release, no-failure, trigger and target reach separately. A prior failed squeeze belongs to F15, and passive/slow variants remain separately named.

**Acceptance checks:**

- July10 retained true must remain marked fresh=false; October8 is false under both retained and fresh predicates.
- A fast tape reading at11:59 cannot qualify a10:05 release, and an absorption before release cannot be its pullback trigger.
- A close back through the catalyst after release cancels the named no-failure candidate; target movement before the trigger is excluded.

**Unresolved definition:** The unit and reset of Speed of Tape(10) are unresolved. The30-second research speed must retain its separate definition.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F18-A-2026-07-10.png>) | true | no verified source squeeze; fresh code false | Retained true is stale; fresh false has no qualifying catalyst. The price path contains multiple pullbacks but no linked fast release and first-pullback absorption record. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-F18-B-2025-10-08.png>) | false | no verified source squeeze; fresh code false | Directional morning rise does not establish the source fast release/no-failure/absorption sequence. Current code records no qualifying catalyst. |

### R-R01 — Native options, gamma scenario and level-conditioned regime

The source shows0DTE, net-GEX sign, a gamma flip, three ranked walls, max pain and location-dependent price responses. It does not publish the dealer-position sign model, flip algorithm, Vol Trigger or hedge-pressure formula. The p.13 drawing includes a ranked call wall below spot despite the text saying calls above. Aggregate spot-repricing root, cumulative-strike crossing and per-strike sign change are different objects; none can be silently selected as the author formula.

The QQQ producer pools0–14DTE, mismatches09:30 spot with later first-five-minute quotes and uses an assumed call-positive/put-negative sign. Its flip loop calls the initial0→first-nonzero cumulative value a crossing, producing635 onJuly10 and594 onJanuary28, both first populated strikes. Walls are extrema of net signed strike exposure, not separately aggregated call/put gamma. Only short_gamma prevalence is scored;3 of647 eligible sessions have no GEX and enter as false. Native OI supplements preserve each product, including missingJanuary28 NDX/SPX nodes and unparsed NQ option statistics.

**Source references:** [GEX p.6](</workspace/sources/documents/discretionary/gex-framework.pdf>); [GEX p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/gex-framework-p007-i1.jpeg>); [GEX p.13 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/gex-framework-p013-i1.jpeg>); [GEX p.14](</workspace/sources/documents/discretionary/gex-framework.pdf>); [GEX p.15 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/gex-framework-p015-i1.jpeg>); [GEX p.19](</workspace/sources/documents/discretionary/gex-framework.pdf>).

**Code to change:** [family_gex.py::_gex_day](</workspace/implementation/src/trading_research/research/phase1_live/family_gex.py:82>), [family_gex.py::_iv](</workspace/implementation/src/trading_research/research/phase1_live/family_gex.py:53>), [family_gex.py::_qqq_spot](</workspace/implementation/src/trading_research/research/phase1_live/family_gex.py:73>), [formulas_flow.py::r_r01_gex_k](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:190>), [family_options.py::_top3_around](</workspace/implementation/src/trading_research/research/phase1_live/family_options.py:85>), [family_options.py::_node_rows](</workspace/implementation/src/trading_research/research/phase1_live/family_options.py:131>), [family_options.py::build_options_table](</workspace/implementation/src/trading_research/research/phase1_live/family_options.py:215>), [recipe_score.py::_preds.r01](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:658>).

**Build steps:**

1. Keep author-exact gamma/flip fields unresolved until the source definition is available. Name the current dealer-sign assumption explicitly. Preserve each product/expiry/underlying contract and multiplier; NDX,NDXP,SPX,SPXW,QQQ,SPY and NQ options never inherit one another’s prices or event counts.
2. Validate OI publication/request vintage and quote coverage per contract. Select a sorted, simultaneous snapshot and matching spot; known_at is the latest required observation, no earlier than09:35 for a first-five-minute QQQ snapshot. Reject crossed, stale, nonfinite or invalid-bound quotes rather than clipping negative bids into plausible mids. Use actual expiry timestamp and declared rates/dividends/model, with IV convergence/error checks.
3. For the explicit scenario calculate each exposure as sign×Gamma×OI×contract_multiplier×S²×0.01. Store calls and puts separately before forming net exposure. Make0DTE the source-described expiry cohort, with0–14DTE pooled separately named. n_contracts and n_distinct_strikes must be different counts.
4. For a named cumulative-strike variant, detect changes between established nonzero cumulative signs; starting from zero is not a crossing, and no crossing returns null rather than argmin(abs(cumsum)). Keep a named repriced aggregate root G(S)=0 and per-strike net sign crossings distinct, including multiple roots/crossings; do not add either as a purported faithful author fix without a source decision.
5. Construct call and put wall candidates from their own gamma totals with the documented side/rank policy. Keep text-above/below and the figure’s all-side ranked wall set distinguishable. If max pain is included, minimize intrinsic OI payout over candidate settlement prices and preserve ties/flat intervals. Unpublished Vol Trigger and pressure gauges remain unavailable.
6. For OI-only nodes, retain the summed-rights/expiry population honestly: a single first-row right or DTE cannot describe a pooled strike. Use genuine OI vintage and price known_at. Daily native cash candles can measure daily span only; they cannot supply intraday first-touch/hold chronology. Correct INDEX_UNION aggregation rather than copying NDX, and keep unparsed NQ options as gap, not measured zero.
7. With a valid snapshot, classify sign and spot-vs-flip separately. Freeze levels before price outcomes; record approach from below/above, already-at-level state, actual overlap, hold/break and pin-distance outcomes in that product. Score outcome distributions conditional on regime and eligible contacts rather than sign prevalence as trading efficacy.
8. Exclude unknown GEX from both positive and negative denominators, report coverage separately, and invalidate caches on producer, schema, snapshot, contract universe and parameter changes. Retain native product plots, vector inputs and source-definition limitations with each report.

**Acceptance checks:**

- July10 QQQ net scenario is negative whileJanuary28 is positive, but both reported flips are the first populated strikes; those are not valid zero-crossing examples.
- A vector with all negative values has no cumulative crossing. A negative then positive vector can cross only after an established negative cumulative value, and extending the universe with a tiny remote strike must not force that strike to be the flip.
- Eligible sign denominator is644 rather than647 for the current available inputs; the3 missing sessions remain unknown.
- January28 NDX/SPX missing nodes stay gaps while NDXP/SPXW are evaluated independently. QQQ/SPY remain in ETF coordinates; NQ option DBN remains unparsed in this audit.

**Chart decision needed:** Inspect GEX p.7 and p.13 against the terminal: which flip construction and ranked-wall selection produced those annotations? Their exact algorithms are not recoverable from the drawings alone.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-A-2026-07-10.png>) | true | cannot-tell author gamma; yes current sign scenario | Native QQQ spot721.67, call wall730, put wall715 and flip635 are shown. Net scenario GEX is negative, but the flip is the first populated strike from an erroneous zero-to-nonzero crossing. No source flip, wall-hold or pin event is demonstrated. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-B-2026-01-28.png>) | false | cannot-tell author gamma; no current short-gamma scenario | Native QQQ spot635.42, walls640/615 and flip594. Net scenario GEX is positive; the same first-strike flip defect persists. The chart preserves actual QQQ prices without NQ conversion. |

**Native-product supplements:**

| product / date | observed input and chart limitation |
|---|---|
| [ndx / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-ndx-2026-07-10.png>) | Native NDX daily candles lie below the upper30000/30100/30325 nodes; lower27000/25500/24000 nodes are far. The zoom preserves the actual daily path. OI selection is not gamma and cannot establish intraday contact order. |
| [ndxp / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-ndxp-2026-07-10.png>) | NDXP uses the same native NDX cash series but its own nodes30000/32500/30050 and27200/16000/17000. None is a demonstrated intraday event; broad strike distances are retained, not converted to NQ. |
| [spx / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-spx-2026-07-10.png>) | Native SPX daily candle stays between the nearby7500 and7600 nodes;8000/8100/7000/6000 are farther. No gamma or intraday first-touch measurement is supplied. |
| [spxw / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-spxw-2026-07-10.png>) | SPXW7550 lies within the current native SPX daily range, matching the retained daily tagged label. The moment of touch, hold and rejection remain unavailable; other SPXW nodes stay distinct from SPX. |
| [qqq / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-qqq-2026-07-10.png>) | Native QQQ minute closes reach725 around12:20 and cross it repeatedly before trading higher;730/735 and the lower700/685/710 remain separate OI references. This is an OI contact diagnostic, not a gamma-wall confirmation. |
| [spy / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-spy-2026-07-10.png>) | Native SPY minute closes pass750 during the10:30 dip and reach755 near15:00.760/757 and remote530/540 nodes remain visible in the overview; the price zoom exposes both contacts without mapping them to another instrument. |
| [QQQ / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-QQQ-gex-vector-2026-07-10.png>) | Exact producer GEX vector has mixed signs near719–726, a strong negative715 row and strong positive730 row. Flip635 is the first populated strike and is not the red/green boundary or an aggregate spot-repricing root. |
| [NQOPT / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-NQOPT-gap-2026-07-10.png>) | Explicit unparsed-DBN gap with retained continuous NQ minute close diagnostic only. No option strike, matched underlying contract or gamma event is fabricated. |
| [ndx / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-ndx-2026-01-28.png>) | No retained eligible NDX OI nodes. Actual native daily price remains visible; blank observations are labelled missing, not zero or no-touch. |
| [ndxp / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-ndxp-2026-01-28.png>) | NDXP26000 is spanned by the native NDX daily candle;26200/27000 are above and22000/21900/20000 far below. This does not fill the separate NDX-node gap or establish intraday contact order. |
| [spx / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-spx-2026-01-28.png>) | No retained eligible SPX OI nodes. Native daily price is available, but no strike event can be assessed from an absent node set. |
| [spxw / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-spxw-2026-01-28.png>) | SPXW7000 is spanned by the native SPX daily candle while7050/7060 remain above and6800/5700/5600 below. This is daily range evidence only and remains independent of SPX missing nodes. |
| [qqq / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-qqq-2026-01-28.png>) | Native QQQ minute closes move through633 near11:30 and oscillate around it later.640/637 are above this path;630/620/600 below. OI633 contact does not establish a gamma regime or wall-hold recipe. |
| [spy / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-spy-2026-01-28.png>) | Native SPY crosses697 near10:00, then696 and returns near696 in the afternoon; remote665/585/535 nodes are retained in the overview. The source gamma ingredients are not present in this OI-only diagnostic. |
| [QQQ / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-QQQ-gex-vector-2026-01-28.png>) | Exact vector has negatives mostly below630 and strong positive gamma near633–650. Flip594 is the initial populated strike, while the visible sign transition lies much higher; call640/put615 are net-strike extrema under the code scenario. |
| [NQOPT / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R01-native-NQOPT-gap-2026-01-28.png>) | Explicit NQ-options input gap. The declining continuous NQ price line cannot establish a missing native option-level response. |

### R-R02 — Prior-close VIX band and source regime comparisons

The source names13,14,15–18 and20 cuts, expected daily percentage VIX/sqrt252, range completion and intraday VIX direction. Its30/50/95-point examples are ES illustrations, not fixed NQ ranges. Prior VIX close is a declared pre-open input choice; S&P-based VIX applied to NQ is a named cross-product context.

The retained15–18 gate correctly uses the prior session’s VIX close: July10=15.84 is true andJanuary2=14.95 is false. That literal score event is valid. The full binning omits14, and implied/realized range, level response, intraday VIX direction and curve/context comparisons are not implemented by this ID.

**Source references:** [VIX4 p.3 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/vix-lesson-4-p003-i1.png>); [VIX4 p.4](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.5](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.6](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.7](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.8](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>); [VIX4 p.9](</workspace/sources/documents/discretionary/vix-lesson-4.pdf>).

**Code to change:** [formulas.py::vix_preopen](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:76>), [formulas.py::vix_band](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:62>), [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [recipe_score.py::_preds.r02](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:661>), [FORMULAS.md::R-R02](</workspace/planning/phase-1-live/FORMULAS.md:972>).

**Build steps:**

1. Preserve the prior-close lookup and vintage. Use the last available completed VIX observation before the session, retaining its date and publication availability through weekends/holidays. Do not introduce today’s close as a pre-open feature.
2. Add the missing14 boundary and explicitly choose nonoverlapping endpoint conventions: <13,[13,14),[14,15),[15,18),[18,20),>=20 is one named convention. Preserve14–15/18–20 as filler bins rather than source trading rules, and disclose the20 endpoint choice.
3. For the named daily estimate use prior-known price×VIX/(100×sqrt252); keep VIX/16, VXN and literal ES point examples distinct. Measure realized high−low and completion ratio as outcomes, by native product and chosen session.
4. Report the existing15–18 membership rate under its literal label, plus separately eligible range/VA-response comparisons if later implemented. Daily VIX direction is known only after that close; leave the four intraday combinations unavailable without intraday VIX. Do not manufacture VX-curve/VVIX joins in the audit.

**Acceptance checks:**

- July10 true andJanuary2 false remain unchanged under the existing15–18 definition.
- VIX13.2 belongs in13–14, and14.95 belongs in14–15; neither belongs in15–18.
- A same-day afternoon VIX revision or NQ price outcome cannot change the pre-open bin. An unavailable VIX input is unknown, not a low-volatility classification.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R02-A-2026-07-10.png>) | true | yes for prior-close15–18 context | The retained lagged VIX is15.84 inside the shaded15–18 band. NQ price later ranges widely; the context flag alone does not measure source implied-range completion or an intraday VIX direction. |
| [B / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R02-B-2026-01-02.png>) | false | no for prior-close15–18 context | Lagged VIX14.95 is below15; the context predicate is correctly false. The price decline does not alter the pre-open classification. |

### R-R03 — Thesis lifetime and first invalidation cause

The source requires a labelled validity band with start/end and three possible death causes: structure, value shift or new information. Open-versus-prior-VA labels,30-minute holds and non-overlap of developing value are named research definitions rather than author-exact automatic thesis construction.

The caller hard-codes any_close_beyond=false, news=false and default developing_overlap=true. Directional death is therefore a wick across the prior VA edge; neutral theses survive automatically. The helper assigns death at the evaluation time or survival to16:00 instead of the first observed cause. July10 is neutral/true; January2 long/false after a fall throughVAH25634.

**Source references:** [C1 p.3](</workspace/sources/documents/discretionary/code-1-thesis.pdf>); [C1 p.4](</workspace/sources/documents/discretionary/code-1-thesis.pdf>); [C1 p.6](</workspace/sources/documents/discretionary/code-1-thesis.pdf>); [C3 p.7](</workspace/sources/documents/discretionary/code-3-orderflow.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_r03_thesis](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:753>), [recipe_score.py::_preds.r03](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:667>).

**Build steps:**

1. Create a thesis record at its actual start with long/short/neutral label, exact band, source/scope and chosen invalidation side. Keep a prior-VA open-label variant distinct from a directional premarket-level thesis; no later band redrawing may change the original record.
2. For the named structural death, find a complete close beyond the appropriate boundary and a full30-minute hold, timestamped at confirmation. Neutral bands can invalidate on either side. Wick-only crossings remain separate observations.
3. Track the developing profile only from executions/bars available at each update, testing the declared value-overlap rule. Join only verified news timestamps, preserving missing calendar coverage as unknown. End at the earliest actual qualified cause, with simultaneous-cause ties retained.
4. Compute alive_minutes=end−start from those timestamps; survival at noon cannot imply survival to16:00. Permit a later new thesis only with a new ID/band/version. Report lifetimes and causes rather than a whole-AM extreme Boolean.

**Acceptance checks:**

- July10 neutral status must not hard-code indefinite survival; actual structure, value and news prerequisites must be evaluated or marked unknown.
- January2 downward crossing ofVAH25634 can end the named long thesis only when the chosen held-close rule confirms, not at the first wick or automatically at noon.
- An11:00 confirmed death produces90minutes from09:30, and a news event at10:00 must beat a later structural event.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R03-A-2026-07-10.png>) | true | cannot-tell full thesis survival; reduced neutral flag true | Open29834.75 lies inside prior VA[29823,29986.25]. The helper hard-codes no structure-close event, no news and overlapping developing value, so neutral remains alive despite later excursions. Full thesis state is not reconstructed. |
| [B / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R03-B-2026-01-02.png>) | false | no for named long thesis by noon; end time unmeasured | Open25687 exceeds priorVAH25634. Price later crosses below that edge and remains much lower. Current code records death from an AM low, not the first complete held structural break or its actual timestamp. |

### R-R04 — Native triad level-taking, SMT and first-fill reaction

The source compares each market’s own AMT objective and which sister uses it first. The user’s SMT definition is prior high/low taken on one index and not another, across timeframes. A3/3 fractal detector and relative-return divergence are different objects.

The recipe remains blocked by the FINDINGS trust gate. Existing upstream defects include absolute ES/YM/RTY pivot prices compared with NQ prices, whole-AM rather than same-time extremes, and missing sister data capable of returning true. Own-profile VA/single-print first-fill states are not assembled. The dated normalized-return panels are diagnostics, not IOD/RFZ detections.

**Source references:** [C1 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/code-1-thesis-p005-i1.png>); [C1 p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/code-1-thesis-p005-i2.png>); [C1 p.7](</workspace/sources/documents/discretionary/code-1-thesis.pdf>).

**Code to change:** [family_flow.py::_fractal_33_smt](</workspace/implementation/src/trading_research/research/phase1_live/family_flow.py:51>), [family_flow.py::build_smt_ohlc](</workspace/implementation/src/trading_research/research/phase1_live/family_flow.py:194>), [mbp1_objects.py::smt_trade_nq](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:369>), [recipe_score.py::catalog](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:157>), [FINDINGS.md](</workspace/planning/phase-1-live/FINDINGS.md:1>).

**Build steps:**

1. Retain blocked scoring until a new explicit trust decision. In a future repair, build each index’s own prior-session high/low with identical declared clock semantics and complete coverage. Compare each price with its own level, never a sister’s absolute price or a ratio-mapped NQ level.
2. At the first wick take, inspect all sister states using only contemporaneously available bars/trades. Missing data is unknown. Retain lead/lag timestamps and later agreement separately; use complete1/5/15-minute bars for their respective variants without looking to the end of AM.
3. Keep prior-H/L SMT distinct from the3/3 pivot variant. IOD requires the corresponding actual AMT object on each instrument; RFZ requires a causal ledger of each market’s unfilled single print and which fills first. Do not create absent sister profiles/ledgers during this audit.
4. After a verified sister event, measure the named sister rejection and NQ0.25R response in order over15minutes, with each R in its own market’s units. A sister first fill may retire a target only under the stated source rule; report eligible matched objects, coverage, lag and outcomes separately.

**Acceptance checks:**

- July10 andJanuary28 return divergence remains unscored; it cannot replace level-taking evidence.
- ES5500.5 beyond its5500 high while NQ109.5 remains below its110 high is a possible mismatch regardless of the large absolute price difference.
- An absent ES bar or a Sunday substituted for prior trading day must yield unknown, not SMT=true; later sister agreement cannot rewrite the earlier event.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R04-A-2026-07-10.png>) | unscored on this date | blocked; no source IOD/RFZ event | NQ/ES/YM/RTY normalized returns diverge, but returns are diagnostic. No matched own-profile level-taking/first-fill chronology is established. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-R04-B-2026-01-28.png>) | unscored on this date | blocked; no source IOD/RFZ event | The four own-open returns differ across the morning; that alone is not prior-high/low SMT or sister single-print first fill. Blocked state is preserved. |

### R-S01 — Refill at the same defended dealing-range band

The source shows absorption and refill at a defined dealing-range band, a close away, and an objective such as the prior RTH extreme. Both long and short examples are printed. Prior VA edges, two-minute aggregation, q90 and one-minute closes are named choices; the source uses 40-tick range bars.

The caller reuses one either-side absorption Boolean for long-at-VAL and short-at-VAH, attaches the final AM print as entry, and supplies whole-AM extrema as local print extremes and outcomes. August21 is true after an opening VAH scan even though the accepted long uses VAL. A source band, same-level refill, sequence and prior-extreme objective are absent.

**Source references:** [NYAM p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p004-i1.png>); [NYAM p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.5 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p005-i1.png>); [K18 p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p010-i1.png>); [K18 p.10 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p010-i2.png>); [K18 p.11](</workspace/sources/documents/discretionary/18k-payout-session.pdf>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [mbp1_objects.py::absorption_a](</workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py:277>), [formulas_flow.py::r_s01_refill_long](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:802>), [formulas_flow.py::r_s01_refill_short](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:784>), [recipe_score.py::_preds.s01](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:721>).

**Build steps:**

1. Represent the source band with bounds, scope, direction and establishment time. For an explicitly named VA-edge version use [edge−2ticks,edge+2ticks], keeping it distinct from the original dealing-range print span.
2. Return absorption events carrying level ID, side, start/end, local executed volume and extreme. For a long, test arriving aggressive sells against the lower band; for a short, aggressive buys against the upper band. Do not reuse an event at the other edge or infer resting refill from the same aggregate.
3. After the matching defence/refill, enter on the first complete close above the upper band bound for long or below the lower bound for short. Invalidate at the local defended print minimum−2ticks or maximum+2ticks. Reject nonpositive risk distances; store entry at completion, not final AM close.
4. Freeze the prior RTH H/L or actual owed objective known at entry. Measure target, MFE and MAE from entry forward, recording stop-versus-target order. Report eligible band contacts, defended refills, confirmed entries and objective outcomes separately; keep missing depth as blocked.

**Acceptance checks:**

- August21 cannot reuse the VAH29402 opening event to certify a VAL29288.75 long. July10 no absorption remains no confirmed refill despite the final close above VAL.
- A lower-band sell-absorption event followed by an upper-band close is a possible long; the same event must never certify an upper-band short.
- A target reached before entry is not an objective win and cannot supply post-entry MFE.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-21](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S01-A-2026-08-21.png>) | true | no | Code positive uses the AM final close 29443 above VAL 29288.75. The observed absorption scan first qualifies near VAH 29402 around 09:32, on the opening downward crossing, and is reused as a VAL-long flag. Price later crosses VAL repeatedly and makes 29220s lows; the plot does not establish a local sell-absorption refill followed by entry at VAL. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S01-B-2026-07-10.png>) | false | no | VAL 29823 is crossed around 09:40 and again after 10:30; final AM close 29944.25 is above it, but the production absorption scan is false. A close somewhere above value is insufficient for the source refill. |

### R-S02 — Third support test with absent defence and continuation entry

The source depicts sellers testing support from above three times and a short through it, followed by a printed loss when it holds. The two-line support band and the ticket stop inside that band are separate observations. Absence of aggressive buying does not establish absence of passive buyers defending against aggressive sellers; FORMULAS conflates those readings.

The OHLC caller supplies zero defence volumes. The helper counts extrema within a doubly widened band, may re-arm from the same bar’s opposite extreme, and returns n>=3 without requiring a third-test close-through entry. August21 has six counted VAL tests; the unmeasured defence condition is automatically true. The resistance-long branch exists but carries the misleading third_test_short key.

**Source references:** [NYAM p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p006-i1.png>); [NYAM p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [NYAM p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/ny-am-session-p007-i1.png>); [K18 p.11](</workspace/sources/documents/discretionary/18k-payout-session.pdf>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_s02_third_retest](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:822>), [recipe_score.py::_preds.s02](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:724>), [FORMULAS.md::R-S02](</workspace/planning/phase-1-live/FORMULAS.md:463>).

**Build steps:**

1. Correct the participant-side description first: distinguish aggressive sellers from resting buyers at support, and aggressive buyers from resting sellers at resistance. A prints-only failure-to-advance measure is a named defence proxy, while actual resting refill remains unavailable. Missing defence cannot become zero.
2. Use an explicit band and one tolerance policy. A touch is path overlap from the required approach side; a wick through the band is not missed merely because its final extreme lies beyond tolerance. Count a new test only after a subsequent known leave of the named0.25R, never by assuming same-bar low/high order.
3. Freeze the first two failed defences, then evaluate defence at the third distinct retest. Require the first completed close through support for short or resistance for long. Return side-specific entry records; do not accept n>=3 alone.
4. Define invalidation from the defended band and preserve the source ticket’s inside-band stop as that case’s annotation. Measure continuation/hold and the loss-return condition over the next15minutes from entry, with exact order, risk distance, MFE/MAE and eligible-test denominator.

**Acceptance checks:**

- August21 six counted touches cannot establish absent passive defence; July10 wick-through overlap must not be silently discarded by an extreme-equality test.
- One long visit cannot become three tests; a same-minute leave and retest with unknown ordering is ambiguous.
- Three weak tests without a subsequent close through the band produce no entry, and the source printed losing entry remains an entry with a losing outcome.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-21](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S02-A-2026-08-21.png>) | true | cannot-tell | Price oscillates through VAL 29288.75 between about 09:52 and 10:45 before rallying. The helper counts six VAL tests and one VAH test; it supplies zero defence volumes and does not require a close through the support after test three. The source no-defence third-test continuation is therefore unestablished, even though price visits the band. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S02-B-2026-07-10.png>) | false | no | Code counts zero qualified VAL/VAH tests, despite large wicks passing through VAL. Its extreme-within-band rule misses some overlaps. There is no verified three-test same-band/no-defence entry sequence; the printed tape is only diagnostic. |

### R-S03 — Second OFM defence with print-side refresh consistency

The source requires an established OFM area, another break/retest and sustained participation/refresh. The0.8 ratio, q75 and one-minute representation are named quantitative choices. Aggressor print consistency and actual replacement of resting orders are different evidence; the latter stays blocked.

The current code calls r_s03_second_defence, contrary to the stale FORMULAS description of an F09 alias. It uses a last-print-derived catalyst, the minimum close and maximum high of all AM, total AM sells against a per-print q75, and the last eight AM sell sizes. It is short-only, has no first/second defence identity and scores zero of647.

**Source references:** [K18 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p004-i1.png>); [K18 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/18k-payout-session-p007-i1.png>); [K18 p.11](</workspace/sources/documents/discretionary/18k-payout-session.pdf>).

**Code to change:** [family_tape.py::_ofm_and_trap](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:246>), [formulas_flow.py::r_s03_second_defence](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:862>), [recipe_score.py::_preds.s03](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:727>), [FORMULAS.md::R-S03](</workspace/planning/phase-1-live/FORMULAS.md:473>).

**Build steps:**

1. Keep faithful certification unavailable while the R-F15 catalyst definition is unresolved. Once a valid catalyst exists, retain its band, first defence and side as a persistent object; do not choose it from the last AM prints.
2. After a complete close through the appropriate boundary, find a later retest from the opposite side and identify it as the second distinct defence. Collect only correctly signed executions at that band in the named retest window. Compare window volume with a historical distribution of equivalent window volumes, not a quantile of individual prints.
3. For the named steady-size test require at least four comparable same-side prints; the last three must each be at least0.8 times the first. Store the sizes, times and thinner/steady result. Implement the source long reading by reversing side/geometry, rather than returning a short flag for all cases.
4. Confirm entry only after participation and level defence are known, then measure0.25R reversal and MFE/MAE over15minutes. Do not equate print-side evidence with BBO reload. Preserve coverage, first/second-defence eligibility and outcomes as separate fields.

**Acceptance checks:**

- July10 andJanuary28 missing catalyst/defence sequencing cannot turn into validated source negatives solely because the retained flag is false.
- Prints45,42,40,44 pass the named steady test;45,40,30,20 fail. Prints from another price or hours later cannot qualify the retest.
- A first touch, retest before the break, or absent resting-size feed must not be labelled a verified second reload.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S03-A-2026-07-10.png>) | false | cannot-tell | No implemented OFM catalyst/second-defence band is available in this case. Prior VA and 27 AM prints of at least 30 lots are shown; neither demonstrates a second OFM retest with steady same-side participation. Zero scored events is not proof of absence in the author framework. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S03-B-2026-01-28.png>) | false | cannot-tell | Downward AM price path remains above prior VAH 26100; the chart shows 22 large prints but no frozen OFM catalyst, first defence or later level-specific refill. The current all-AM aggregation cannot certify the source setup. |

### R-S04 — ATH pullback, weekly aggression box and microbalance entry

The source shows heavy buying in the weekly delta profile behind the upward move, a small green350% box, failed reclaims and a long above a microbalance. FORMULAS instead selects dp.min near the weekly high and a downward departure. The figure does not establish that equivalence. The fixture also says distance|120−118.5|=1.5 is within tR1.0; it is not. The short example on p.9 belongs to S05.

Retained weekly references exist, but are prior-five-session18:00–16:00 aggregates, not a verified source weekly profile. Unknown aggressor side is treated as sell. The caller counts every AM high above the prior high as a touch, uses whole-AM no-close/minimum, one-price pooled buy/sell ratios and the final microbalance/close. July10 dp_min30250 is untraded in AM; January28 counts148 supposed failures. Zero scores do not validate this construction.

**Source references:** [K2345 p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p004-i1.jpeg>); [K2345 p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p005-i1.jpeg>); [K2345 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p007-i1.jpeg>).

**Code to change:** [family_tape.py::_delta_pack](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:88>), [family_tape.py::build_weekly_delta_table](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:141>), [family_tape.py::_dp_min_near_high](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:114>), [family_tape.py::_s04_from_am](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:174>), [formulas_flow.py::r_s04_ath_ofm](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:884>), [FORMULAS.md::R-S04](</workspace/planning/phase-1-live/FORMULAS.md:482>), [recipe_score.py::_preds.s04](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:730>).

**Build steps:**

1. Stop faithful certification and resolve the source profile scope, sign and trapped-seller interpretation from the weekly delta/green-box chart. Preserve the present min-delta/downward-departure construction only as a named alternative; do not silently replace it with a positive-delta recipe. Correct the fixture1.5>1 arithmetic.
2. After that decision, specify exact session/week boundaries, contract, eligible executions, sign mapping and profile known_at. Deduplicate overlapping input chunks, retain unknown-side volume separately and verify all constituent sessions. Do not build a missing weekly input in this audit.
3. Track distinct prior-range attempts with approach, actual overlap, leave and close-back timestamps. Attach the resolved local imbalance box to its producing candle/rows and completion time, not one price aggregated across all AM. Resolve350% ratio semantics/settings without assuming the unrelated FP8 diagonal rule.
4. Only after the weekly context, failed attempts and green box are known may the first later microbalance break trigger the long. Freeze the next HTF level above entry and trail protected lows sequentially. Measure continuation to16:00 and stop/order-aware outcomes; preserve every failed stage and coverage denominator.

**Acceptance checks:**

- The printed fixture dp_min118.5 versus weekly high120 and tR1 fails pairing.
- July10 untraded30250 cannot print a new AM buy-imbalance box; January28 values entirely above a reference cannot count148 distinct retests.
- A box, close or target occurring before its prerequisite is not a completed source sequence.

**Chart decision needed:** Inspect K2345 pp.4–5: which weekly profile interval and signed delta location produced the green box, and does it represent positive buying behind the rally or a negative-delta trap near the weekly high?

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S04-A-2026-07-10.png>) | false | cannot-tell | Retained weekly high 30320 and dp_min 30250 are above the entire AM path; weekly low 28909.75 is far below. The producer microbalance is 29914–29941.5, but no buy imbalance at 30250 is traded in this AM. Source weekly buying versus FORMULAS dp_min/sign/direction conflict stops faithful certification. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S04-B-2026-01-28.png>) | false | cannot-tell | Weekly high 26114.25 and dp_min 26100 sit below most AM trading, with weekly low 25025. The last microbalance is 26100.75–26130.25 and the final AM close stays inside it. No source-validated weekly trap/box/break sequence is established. |
| [source-date / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S04-source-date-2026-07-10.png>) | false | cannot-tell | Source-date replay preserves weekly high 30320, delta reference 30250 and last AM microbalance 29914–29941.50. The delta price is untraded in AM; code failures=0, buy-imbalance=false. The source green box/heavy-buying interpretation is not reproduced; source sign/profile-scope conflict stops the ID. |

### R-S05 — Price-defined microbalance with first breakout and structural stop

The source prints a small grey price-defined balance, long and short breaks, a stop beyond the box and an HTF objective. Five close-constrained bars,0.1R and one-minute bars are named definitions; the author screenshot uses40-tick range bars. The ticket’s approximately7-point box and5.59 planned R:R are examples.

The current producer does use a price-defined close-run, unlike the stale FORMULAS clock-box claim. It scans all09:40–12:00 runs and keeps the last qualifying box, comparing only the final AM close. July10 has a real named breakout at noon from29914–29941.5; January28 ends inside its final box. Earlier events are overwritten, and HTF reach/stop/trail are not the scored event.

**Source references:** [K2345 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p007-i1.jpeg>); [K2345 p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/2345-funded-session-p009-i1.jpeg>).

**Code to change:** [formulas_flow.py::r_s05_microbalance](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:903>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [recipe_score.py::_preds.s05](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:796>), [FORMULAS.md::R-S05](</workspace/planning/phase-1-live/FORMULAS.md:492>).

**Build steps:**

1. Document the named detector independently of the author’s discretionary box. Use fixed-clock complete bars, a known dealing-range R and min_run=5 with max(close)−min(close)<=0.1R. Bounds are the full high/low span of that same run; known_at is its final bar completion.
2. Process chronologically: establish a box as soon as the run qualifies, freeze its identity for the first subsequent breakout, and apply a declared extension/overlap policy. Never overwrite completed earlier events with the final qualifying run or draw a late box as available at09:40.
3. Enter on the first later complete close above the high or below the low. Set stop at low−2ticks for long or high+2ticks for short. Choose a genuinely prior-known HTF objective in the breakout direction, not the opening ten-minute high for both directions.
4. Record all box/entry events and post-entry reach, MFE/MAE and sequential protected-extreme trail to16:00. State whether each rate is per box, per first breakout or per session; update FORMULAS to describe the actual current code before comparing results.

**Acceptance checks:**

- July10 box29914–29941.5 completes at11:59 and its11:59 bar closes above at noon; no earlier known_at is permitted.
- January28 final box26100.75–26130.25 is not broken by final AM close26116.75. An earlier confirmed box event must remain in the ledger.
- Two paths with identical final close but different earlier breaks can have different event counts and outcomes.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S05-A-2026-07-10.png>) | true | yes — named five-close microbalance breakout only | Last qualifying close-run completes at 11:59, with full-wick box 29914–29941.5. The 11:59 bar closes 29944.25 above it, known at noon. This is a real named microbalance breakout; the wide backdrawn box is not known at 09:40, and target/trail outcomes are not certified. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S05-B-2026-01-28.png>) | false | no — for the plotted final box | The selected run completes at 11:56 and spans 26100.75–26130.25. The final AM close 26116.75 stays inside. Earlier price-defined boxes are overwritten, so this false result cannot be read as no breakout anywhere in the session. |

### R-S06 — Two independent reasons at a reaction band

The source ES2-minute chart uses a marked rejection area plus a nearby minor HVN, with a long mirror and absorption. Text says1.5R, but both tickets print1.00R with20-tick stop/target and the long illustrates a192-tick run. FORMULAS chooses the prose target while acknowledging the conflict; faithful certification must stop. Transfer to NQ is a separate named study.

The current recipe has both directions, despite the stale short-only description. It uses a single prior RTH extreme, prior high/low-to-last-close as rejection, the first price-sorted occupied-bin OHLC HVN and whole-AM close/extrema. Neither branch requires price to touch the chosen level. June12 fires a long near28599 while AM stays above29200; July10 also never touches its lower candidates.

**Source references:** [K10 p.6](</workspace/sources/documents/discretionary/10k-first-month.pdf>); [K10 p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/10k-first-month-p007-i1.jpeg>); [K10 p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/10k-first-month-p008-i1.jpeg>); [K10 p.12 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/10k-first-month-p012-i1.jpeg>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_jumbo.py::profile_nodes](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:153>), [formulas_flow.py::r_s06_two_reason](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:932>), [recipe_score.py::_preds.s06](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:733>), [FORMULAS.md::R-S06](</workspace/planning/phase-1-live/FORMULAS.md:502>).

**Build steps:**

1. Resolve the source text/ticket target conflict before assigning a faithful target rule. Retain1.0R and1.5R as distinct labelled cases, and preserve ES tick/multiplier/contract values; NQ coordinates never stand in for the source ES chart.
2. Derive the reaction band from a completed prior local rejection, with extreme/close endpoints and a documented causal confirmation. A prior-day high-to-final-close scalar is not that event. Find an independent minor node from the stated profile, excluding the POC and using a complete price grid and explicit selection/tie rule.
3. Compute distance from the node to the band, not only a single swing high. Require an actual later band contact from the correct side, then the named G-default close/reversal chronology. For the source long, require matching sell-aggression absorption at the touch; an AM close far above the level is insufficient.
4. Set invalidation just beyond the observed rejection extreme, with positive risk. Apply only the resolved target multiple or the separately named alternatives to post-entry prices. Compare one-reason versus two-reason eligible contacts, side, product, rejection and target outcomes.

**Acceptance checks:**

- June12 has no contact with HVN28599/prior low28577.5 and must not produce a long rejection. July10 candidates29635.75/29614.5 are also uncontacted.
- An HVN beside the band and a later confirmed rejection can qualify; an unrelated node selected merely because it is first in sorted order cannot.
- An ES20-tick risk ticket and its20-tick target are1.0R, not1.5R; a192-tick later run does not change the planned target.

**Chart decision needed:** Inspect K10 pp.7–8: should these examples be represented by the plotted1:1 tickets or the prose1.5R target, and where are the original rejection-band endpoints?

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-06-12](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S06-A-2026-06-12.png>) | true | no | Code true is a clear missing-touch counterexample: chosen HVN 28599 lies near prior low 28577.50, but AM price stays in the 29200s–29700s and never approaches either level. The long branch accepts a far-away close above the rejection threshold. The source ES ticket/text target conflict remains separate. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S06-B-2026-07-10.png>) | false | no | Chosen HVN 29635.75 and prior low 29614.50 are below even the 10:30 AM spike to 29675; neither the lower two-reason area nor the prior high 29993.50 is touched. Full-AM price change is not a band rejection. |

### R-S07 — Reaction-area entries, structural risk and intraband re-entry

The source uses held-buyer/seller areas, objectives and stops beyond the defended structure. Its35/188,15/211 and115/248-tick tickets are illustrations, not universal thresholds. The re-entry is permitted only inside the same approximately7-point band. FORMULAS turns example distances into fixed rows; its source meaning must be corrected before faithful use.

The recipe uses the final AM close as an always-long entry, combines a prior-VA edge touch anywhere in AM, and measures MAE from the whole RTH minimum including pre-entry prices. Only survived_15 is scored, with no absorption, held-area geometry, objective or re-entry. July10’s morning plunge is charged against its noon entry even though afternoon price rises.

**Source references:** [ANAT p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.4 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p004-i1.png>); [ANAT p.6 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.6 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p006-i1.png>); [ANAT p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.7 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p007-i1.png>); [ANAT p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.8 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p008-i1.png>); [ANAT p.9 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [ANAT p.9 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p009-i1.png>); [ANAT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_s07_areas](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:964>), [recipe_score.py::_preds.s07](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:736>), [FORMULAS.md::R-S07](</workspace/planning/phase-1-live/FORMULAS.md:512>).

**Build steps:**

1. Separate source structural risk from the three printed example ticket rows. Each entry needs its own area bounds, defended side, establishment/trigger times and known objective; keep missing composite nodes or held-print spans explicitly unavailable.
2. Trigger only at a matching band defence with the correctly signed arriving aggression. Choose long at a defended lower area or short at an upper area at that moment; do not impose a direction from noon’s close.
3. Set stop just beyond the specific defended structure with a declared tick buffer. For each re-entry, require price to return inside the same still-valid band after the prior exit; a nearby price is not eligible, and a broken/retired area cannot silently be reused.
4. Measure signed MFE/MAE from the actual entry forward to stop/objective/end. For long use max(later_price−entry) and max(entry−later_price); reverse for short. Report structural-stop outcomes, objective success, attempt count and any clearly named ticket-distance sensitivity rows separately; never score15-tick survival as the complete source recipe.

**Acceptance checks:**

- July10 pre-noon low29675 cannot affect a noon29944.25 entry’s MAE. January28 no prior-VA edge contact is not a trigger.
- Inside[99.75,100.25] qualifies for a still-valid re-entry;101.5 does not. A stopped/invalidated band needs a new established defence before reuse.
- 35/188 and15/211 remain example risk/objective pairs; a short entry must use downward MFE and upward MAE.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S07-A-2026-07-10.png>) | false | cannot-tell | The noon entry line 29944.25 is drawn after the large morning dip to 29675. Code includes that pre-entry dip in MAE, despite price rising through the afternoon. No held-buyers area, absorption-triggered entry, objective or re-entry band is built. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S07-B-2026-01-28.png>) | false | no — for the retained prior-VA candidate | AM price remains above prior VAH 26100 (lowest near 26100.75), so no valid edge touch is established under the retained two-tick rule. The noon entry 26116.75 still has full-day/pre-entry extrema attached; the source intraband entry cannot be inferred. |

### R-S08 — Minor-node continuation, control and buying-pressure flip

The source shows a minor-node band at the top of an established5-minute balance, repeated resistance and negative executed delta; extreme buying above it changes the read to a retest long toward VWAP. The approximately20-point balance band,5-point refill zone and9-point/55-point ticket are distinct. SD+1/+2 labels are coincident VWAP references, not the node definition.

The overriding recipe now calls r_s08_minor_node, not the stale two-HVN presence rule. It substitutes prior RTH high for balance top, a single first sorted OHLC HVN for the band, current-AM high counts for prior rejections, and final three five-minute close−open values for executed delta. No actual touch, same-side control, flip, target or composite behaviour is scored. Both plotted nodes lie below the AM path.

**Source references:** [CONT p.4 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p004-i1.jpeg>); [CONT p.5 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p005-i1.jpeg>); [CONT p.7 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p007-i1.jpeg>); [CONT p.8 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p001-i2.jpeg>); [CONT p.10 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/a-clean-continuation-short-p010-i1.jpeg>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_s08_minor_node](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:983>), [formulas_jumbo.py::profile_nodes](</workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py:153>), [recipe_score.py::_preds.s08](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:739>), [FORMULAS.md::R-S08](</workspace/planning/phase-1-live/FORMULAS.md:522>).

**Build steps:**

1. Establish a causal balance interval and its own volume profile. The minor node is a contiguous qualified band near its top, distinct from the POC; record prior independent contacts/rejections completed before the new setup. Preserve the node/span threshold as a named rule.
2. Build executed buy-minus-sell delta in the actual preceding complete five-minute bars approaching the band. Require the named three negatives only in that context. Unknown aggressor side is neither sell nor signed volume; OHLC close−open is a separate price-change proxy and cannot satisfy this source condition.
3. On a later band contact, evaluate the short rejection and post-entry POC/last-seller-failure target, then count renewed same-side control at later valid re-entries. Freeze current POC/VWAP at their stated decision times or store their developing updates explicitly.
4. Implement the stated alternative only when a complete close above the band has local extreme buying, followed by a later held retest from above; target the session VWAP. Keep ordinary short and flip-long denominators separate. Do not manufacture yearly-composite LVNs; a separately named available proxy can have its own stall/slice outcomes once authorized.

**Acceptance checks:**

- July10 HVN29635.75 versus top29993.5 andJanuary28 HVN25924.5 versus26114.25 do not define a top-of-balance contact.
- Negative price-change bars with positive executed delta cannot qualify the source sell stack.
- A buy-pressure break without the later retest is not a flip entry; SD+1 coinciding with a refill zone does not replace the volume-node band.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S08-A-2026-07-10.png>) | false | no — for the implemented node | Selected prior OHLC HVN 29635.75 is far below balance-top substitute 29993.50 and is never touched. The final three five-minute price changes are +36.25,+17.75,+13.5; these are not executed delta. No source minor-node band/rejection exists in the plotted input. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S08-B-2026-01-28.png>) | false | no — for the implemented node | Selected HVN 25924.50 is far below prior high 26114.25 and all AM price. Inputs +5.5,-18.75,+6.75 are price changes, not three negative delta bars; this is no valid short-at-node sequence. |

### R-S09 — Entire A-period above prior value, developing-VA break and defended retest

The source requires the entire A-period above prior VAH, observation around10:00, a break of current developing VAH with aggressive buying and a later defence of those imbalance prices. The source sketch is long-only; a developing-VAL short is a named mirror.70% VA, one-minute proxy and G-default hold are declared choices.

The producer instead compares09:30 open with the future09:30–10:00 OHLC-VP VAH, freezes that line, and requires an unordered post10 close above plus any low below. August11 is true even though A-low29631.75 is far below prior VAH29819.75. July10 fails its open gate; later PM rally is not an above-value opening setup.

**Source references:** [AVG p.21 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [AVG p.21 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [AVG p.22 fig.1](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/anatomy-of-a-losing-start-p001-i1.png>); [AVG p.22 fig.2](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p002-i2.png>); [AVG p.22 fig.3](</workspace/implementation/reports/phase1-live/chart-audit/source-figures/average-unprofitable-trader-p022-i2.png>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [family_open.py::ohlc_vp](</workspace/implementation/src/trading_research/research/phase1_live/family_open.py:72>), [formulas_flow.py::r_s09_open_above_value](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1000>), [recipe_score.py::_preds.s09](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:799>).

**Build steps:**

1. At10:00, require complete A-period low>prior completed-profile VAH. Store both profile scopes and dates. The open price alone or a comparison to today’s future profile cannot establish this condition.
2. Update the current RTH profile chronologically from available executions, or a clearly named OHLC proxy. For each complete break candle after10:00 use the profile snapshot available before that break, retaining VAH/VAL and the snapshot cutoff.
3. Require the source buying imbalance in that same breaking candle and freeze its actual row-span band. Do not assume the unresolved F04 illustration establishes a4× rule; state the chosen settings as named or keep exact construction unavailable. Only a later approach from above and confirmed defence of those prices constitutes the retest entry.
4. Apply the named G-default body/invalidation/reversal sequence using the frozen developing VA height, then measure post-entry HTF reach by16:00. Report opening eligibility, break-with-buying, retest-hold and target success separately with10–11/11–12/PM splits. Keep the unprinted short mirror separately labelled.

**Acceptance checks:**

- August11 A-low29631.75<prior VAH29819.75 must fail opening eligibility despite the higher09:30 open. July10 A-low29798<29986.25 also fails.
- A touch before the break cannot count as its retest; a break without buying participation or a later failed band defence is not retest-hold.
- Adding future prints must not change the stored developing VAH or eligible state used by an earlier break.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-11](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S09-A-2026-08-11.png>) | true | no | False positive: A-period low 29631.75 is below prior VAH 29819.75, so the required entire A-period-above-value setup fails. Code instead tests open 29839.25 against its own future 10:00 VAH 29745.50, then uses unordered later breaks/touches. Afternoon selling cannot repair the missing opening premise. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-S09-B-2026-07-10.png>) | false | no | A-period low 29798 lies below prior VAH 29986.25; open 29834.75 also lies below the code 10:00 VAH 29949.75. Later afternoon trade above both lines is not an open-above-value setup. |

### R-P01 — AM TBR daily-return sigma, first touch and return to 08:00 open

The source uses sample standard deviation of 20 previous completed DAILY simple percentage returns, anchored to 08:00 open, with first ±0.25σ touch. Its lower-timeframe branch scans for return starting on the touch minute; its chart fallback skips that bar. FORMULAS simultaneously says after the touch bar and from the touch bar itself. Stop unqualified certification until those branch semantics are explicit. Hardcoded hourly claims and milestones are not measured local rates.

The producer takes 19 log returns from at most 20 closes, starts with only five closes, and can substitute an RTH close. Both-side touch chooses smaller overshoot instead of distance from the bar open. ext_max is only the touch-bar extension. July10 returns from upper29959.91 to 08:00 open29816.75; January10 lower21232.94 touch does not return to21320.75 by noon. These validate observations of the named implemented variant, not the printed sigma distribution.

**Source references:** [PINE AM TBR - NQ Stats.txt L135](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/AM TBR - NQ Stats.txt:135>); [PINE AM TBR - NQ Stats.txt L146](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/AM TBR - NQ Stats.txt:146>); [PINE AM TBR - NQ Stats.txt L336](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/AM TBR - NQ Stats.txt:336>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p01_sigma_bands](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1022>), [formulas_flow.py::r_p01_touch_revert](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1031>), [recipe_score.py::_preds.p01](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:745>), [FORMULAS.md::R-P01](</workspace/planning/phase-1-live/FORMULAS.md:542>).

**Build steps:**

1. Resolve the same-minute wording by documenting the two literal source execution branches. A causal research version must keep unresolved within-minute order ambiguous unless executions establish it; do not silently change the source branch and retain its published rates.
2. Require 21 consecutive eligible completed session closes to form exactly20 simple returns r_i=100*(C_i/C_(i−1)−1). Use sample standard deviation with denominator19, all returns known before08:00. Identify the contract, daily-session convention and roll policy; missing session closes cannot fall back to RTH without a separately named variant.
3. At08:00 freeze O, σ_px=O*sd(r)/100 and all displayed O±kσ_px levels. Scan08:00–12:00 for the first upper/lower touch. On a both-side minute use distance from that minute open, upper on equality, for the literal source branch; record the tie and original OHLC.
4. Track return to O and the entire extension path until return/end, using the resolved same-minute policy. Measure touched-side excursion from O and opposite-side MFE only after reversion. Retain per-touch side/hour, known_at, first return, milestone times and conditional counts; do not pool incomplete/no-touch sessions as failures.

**Acceptance checks:**

- A21-close input yields20 returns; 20 closes or a missing close is insufficient for the source lookback. A log-return fixture must differ when returns are large.
- July10 upper touch around09:52 and return10:32 remain identifiable under the existing log variant; recompute source bands before comparing source outcomes. January10 has no return by12:00.
- Changing only the touch-bar open must alter the both-side tie choice where appropriate. A later larger excursion before return must update ext_max.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P01-A-2026-07-10.png>) | true | yes — plotted log-return variant | Code upper band 29959.91 is first touched around09:52 and price returns to08:00 open29816.75 at10:32. The lower band29673.59 lies just below the10:30 spike. A real touch/reversion is present, but19 log returns are not the Pine20 simple daily returns and do not certify its exact sigma. |
| [B / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P01-B-2025-01-10.png>) | false | no | 08:30 price breaks code lower band21232.94, then remains below08:00 open21320.75 through noon. The news-driven decline supplies a clear no-reversion case; same-bar/tie and sigma-construction mismatches remain separate. |

### R-P02 — Hourly sweep, four return targets and 24-by-2 conditional tables

The source retains prior-hour H/L/open/mid, compares current open with prior open, and distinguishes high and low sweeps and returns to the swept edge, prior mid, CURRENT hour open and opposite edge. Its depth levels are percentages of prior-hour width. The24×2 arrays are quoted historical claims, not a new daily any-event probability.

The current producer scans09:00–16:00 and ORs hour results. The helper only calculates high-side returns, so low_sweep and high_ret_50 does not implement a low return.637/647 is effectively any high-sweep edge return. July10 has a high-sweep return; June16 has clear low-sweep returns, including09:01→09:02, yet scores false.

**Source references:** [PINE NQ Hourly Retracements 12y Stats with Levels.txt L126](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracements 12y Stats with Levels.txt:126>); [PINE NQ Hourly Retracements 12y Stats with Levels.txt L151](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracements 12y Stats with Levels.txt:151>); [PINE NQ Hourly Retracements 12y Stats with Levels.txt L185](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracements 12y Stats with Levels.txt:185>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p02_hourly_sweep](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1088>), [recipe_score.py::_preds.p02](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:748>).

**Build steps:**

1. Emit one record for every complete current hour and complete prior hour across all24 hours. Freeze prior H/L/O/M and current O at the hour boundary, with isAbove=(currentO>priorO). Require positive prior width and document timezone/DST hour identity.
2. Track independent strict high and low sweeps chronologically. For each side retain first sweep time and subsequent returns to its swept edge, prior midpoint, current-hour open and opposite edge within the same hour. Reverse inequalities for the low branch; never reuse high-return fields.
3. Preserve literal same-bar touch semantics as a source branch and keep causal within-minute ordering unresolved where necessary. Measure maximum extension beyond the swept edge through the defined hour horizon, divide by prior width, and draw H+q*W/100 or L−q*W/100 for the selected published depth percentile.
4. Compute counts and rates by hour×isAbove×side, conditional on an actual sweep for return rates. Keep sweep incidence, both/neither, depth quantiles and each target separate. A daily OR may be an explicitly named summary with its own denominator.

**Acceptance checks:**

- July10 prior08-hour high29878.75 is swept09:31 and returns around09:39. June16 low30508.75 swept09:01 and returned09:02 must populate the low-return record.
- A low sweep without a high sweep cannot depend on high_ret_50. Current and prior opens deliberately different must select the current open as return target.
- A late-hour sweep followed only by a next-hour return is not an in-hour success; non-sweep hours do not enter return denominators.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P02-A-2026-07-10.png>) | true | yes —09:00 high-sweep return | Prior08:00 high29878.75 is exceeded around09:31 and revisited from above around09:39–40; price also passes prior midpoint29825 and current-hour open29800.50. This dated high-side event exists, while the full family lacks low-side return and conditional-hour scoring. |
| [B / 2026-06-16](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P02-B-2026-06-16.png>) | false | yes —09:00 low-sweep branch omitted by score | First low sweep of30508.75 occurs09:01 and returns09:02; another visible09:30 sweep returns later. No prior-hour high sweep/return is present in the scored hours. The source09:00 low branch should fire, while its high branch should not; the pooled high-only code misses the valid low event. |
| [event-negative / 2026-08-31](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P02-event-negative-2026-08-31.png>) | true | no for the selected11:00 hourly event | August31 actual10:00–11:00 H29447.75/L29355; every11:00–12:00 bar stays within both extremes, so neither hourly sweep exists. Mid29401.375 and current open29415.25 are drawn separately. Header daily code=true can come from a different hour and is not a contradiction to this event-level negative. |

### R-P03 — Seven magic-hour boxes, first break, invalidation and midpoint target

The source builds hours23/00/01/02/06/07/08, then seeks the midpoint after a strict first break and before a stop at75% or100% of width. Actual outcome logic ends three hours after box completion; the displayed hard-stop countdown is one hour later. The supplied file ends in malformed text_ and cannot compile as supplied. FORMULAS does not preserve the source execution distinctions, so faithful certification stops.

The producer invents break time hour+4minutes and target time hour+20minutes, both before the hour box completes, chooses direction using future extremes and otherwise assumes a low break even when none occurred. The helper ignores invalidation.647/647 midpoint wins is not the source event. January28 hour01 has no break; July10 hour06 has an actual07:00 high break followed07:30 midpoint return.

**Source references:** [PINE magic_hours L55](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:55>); [PINE magic_hours L145](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:145>); [PINE magic_hours L465](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:465>); [PINE magic_hours L527](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/magic_hours:527>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p03_magic_hour](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1134>), [formulas_flow.py::ext_to_zone](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1120>), [recipe_score.py::_preds.p03](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:751>), [FORMULAS.md::R-P03](</workspace/planning/phase-1-live/FORMULAS.md:560>).

**Build steps:**

1. Resolve the incomplete source file and distinguish literal three-hour outcome window from its erroneous countdown before faithful use. Keep printed probabilities as source claims. Do not invent the missing final source text or infer trade entries from the Z labels.
2. For each of the seven full hour boxes freeze H/L/M/W only at completion. Search the following three hours for the first strict edge break, recording side/time and any both-side minute. Never select direction by the final maximum and never substitute low when no break exists.
3. Advance bar by bar after the break: source invalidation has priority before midpoint target in each later chart bar and the break bar itself is skipped. Use inv=1W for00/01/06/07 and0.75W for02/08/23. A causal variant needs actual execution order when stop and target share a minute. Stop evaluating after invalidation, target or deadline.
4. At each evaluation derive ep=100*distance beyond broken edge/W and Z1<25,Z2<50,Z3<invPct,Z4<150,Z5<300,Z6 otherwise. Draw implemented bounds on each hour’s own chart; source display levels include0,.25,.5,inv,1.5,3,4W and source runners use the broken edge, not midpoint. Report per-hour eligibility, first-break wins, invalidations and target times; no session OR under a per-hour headline.

**Acceptance checks:**

- January28 hour01 H26349/L26246 never breaks in its evaluation window and cannot win. July10 hour06 high29862.25 breaks07:00 and midpoint29833.875 returns07:30 before invalidation.
- A midpoint touch03:03 preceding July10 hour02 break03:53 is not the target; the later05:19 return is. Target timestamps cannot precede box known_at.
- Stop before target is a failure even if midpoint is eventually reached. A no-break hour and a75%-stop hour must exercise different branches.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P03-A-2026-07-10.png>) | true | yes —06:00 box; no — pre-break02:00 touch | The code-selected02:00 box has H29856.75/L29775.25 and mid29816. Price visits the mid early in03:00 before the eventual lower break, so this visit cannot be a post-break win. Other magic hours have different paths; source target-before-stop ordering must be assessed per hour, not accepted from the all-session true flag. Independent chronological read:06:00 box H29862.25/L29805.50 breaks high07:00 and reaches mid29833.875 at07:30 before invalidation;02:00 first actual low break03:53 reaches its mid only05:19, not the fabricated02:20 time. See pine_sequence_diagnostics.json. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P03-B-2026-01-28.png>) | true | no — code-selected01:00 box in its one-hour follow-up | Code-selected01:00 box H26349/L26246 has mid26297.50. The02:00–03:00 path visits the mid while staying inside those edges, so there is no strict break in the code evaluation window. The caller nevertheless chooses low by default and records a win with invented timestamps. |

### R-P04 — Three 15-minute raid boxes, confirmed return and frozen raid depth

Source boxes are02:00–02:15,09:00–09:15 and13:00–13:15 NY, with strict5-point raid and close back within120minutes. Same raid-bar close-back is allowed. Literal source buckets disagree with their labels: bucket0 covers depths below30, while overflow starts80 despite >70 text. At deadline the source saves statistics before that bar’s confirmation update. FORMULAS’s labelled buckets are not the literal implementation.

The current caller uses09:00–10:00, only high raids, and scores raid OR confirmation. The helper uses maximum depth to the cutoff even after the first confirmation. July10 raid of the wrong box around11:25 cannot demonstrate the source09:15 box event, whose deadline is11:15. January28 high-side non-raid ignores a large low-side move.

**Source references:** [PINE Session Raid Stats.txt L27](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Raid Stats.txt:27>); [PINE Session Raid Stats.txt L395](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Raid Stats.txt:395>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p04_raid](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1155>), [recipe_score.py::_preds.p04](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:754>), [FORMULAS.md::R-P04](</workspace/planning/phase-1-live/FORMULAS.md:569>).

**Build steps:**

1. Stop certification of published bucket rates until literal versus intended bucket semantics and cutoff update order are labelled. Preserve original source defects in a literal replication; correct labels/logic only in a separately named version.
2. Build complete15-minute H/L boxes at02/09/13 and freeze at:15. For each side evaluate strict H_bar>boxH+5 or L_bar<boxL−5 through box_end+120minutes, using actual timestamps. Five points is20NQ ticks, not5ticks.
3. After the first raid accumulate the running extreme only until the FIRST qualifying close-back, including the raid bar under the source rule. Freeze depth then. Track high and low independently; preserve raid without confirmation as its own event.
4. Draw each actual box and point-extension ladder20/30/40/50/60/70 on both sides. Return separate raid incidence, close-back conditional rate, frozen depth bucket and confirmation time per box. Preserve source first500-session cap as source behaviour, distinct from a trailing or full-history cohort.

**Acceptance checks:**

- A high exactlyH+5 is not a raid; H+5.25 with same-bar closeH qualifies the literal confirmation. A low-side equivalent must also work.
- A confirmed11-point raid followed by a later40-point excursion retains11-point first-return depth. Test depths19,20,29,30,70,79,80 against both literal and corrected bucket labels.
- July10 wrong-box11:25 event cannot enter the09:15 source box’s11:15 deadline. At the cutoff distinguish bar start from completed close.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P04-A-2026-07-10.png>) | true | cannot-tell — wrong source box | Code09:00–10:00 high29968.50 is raided past29973.50 around11:25, then closes back below the high around11:34. This is a real event on the wrong60-minute box; source09:00–09:15 has different bounds and an11:15 cutoff. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P04-B-2026-01-28.png>) | false | no — upper raid of the implemented box | Price never reaches code H26301+5 after10:00. It breaks down through L26213.75, illustrating why an upper-only flag misses the source low-side family. Source15-minute geometry is absent. |

### R-P05 — London body-quarter level and the whole-NY-session close-back

The source uses Asia18:00–02:00, London02:00–08:00 and NY08:00–17:00. The level is25% into the London BODY from its close side. Success/fail/stay compares the entire NY candle’s wick and final close, not a local rejection candle. Source doji drawing uses >= while the statistical direction uses >; regime branches overlap and their precedence matters.

The implementation instead uses London00:00–03:00 and NY09:30–12:00, and ORs the bullish failure into the positive scorer while the bearish helper omits symmetric failure/stay outputs. January28 source London is bearish with level26286.1875 and a valid NY wick/close-back; the code is a bullish failure at26292.0625. The equal true flags represent different events and geometry.

**Source references:** [PINE Session Range Candles + 25% Level.txt L814](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Range Candles + 25% Level.txt:814>); [PINE Session Range Candles + 25% Level.txt L930](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Range Candles + 25% Level.txt:930>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p05_london_25](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1176>), [recipe_score.py::_preds.p05](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:757>).

**Build steps:**

1. Create separate complete source session candles on the exact clocks, including the prior-evening Asia start. At08:00 freeze London O/C/H/L, bodyTop=max(O,C), bodyBot=min(O,C), B=bodyTop−bodyBot and level=bull?bodyTop−.25B:bodyBot+.25B. Record doji classification separately and preserve source drawing/statistical branch differences.
2. At17:00 classify whole NY candle: bullish London success if NYL<level and NYC>level, failure if NYL<level and NYC<=level, stay if NYL>=level; bearish mirrors use NYH>level and close below/at-or-above. Add the source London H/L wick-return counters separately.
3. Freeze Asia/London containment regime and NY-open-versus-London-mid at08:00 with documented branch precedence. Keep the source252-history retention and incomplete-session treatment explicit; do not recompute a London sign using NY price.
4. Score success only as success. Return failure, stay and no-body cases with their own labels and per-direction/regime counts. Draw source and named legacy level with distinct clocks when comparing; outcome known_at is17:00, not the intraday wick time.

**Acceptance checks:**

- January28 source London O26301.75/C26281 gives bearish level26286.1875; NYH26306 and NYC26268.25 is success. Legacy bullish-failure true cannot be presented as the same event.
- July10 source bearish level29823.8125 with NYC30068.5 is not a bearish close-back success.
- Bull failure, bear failure, stay, doji and exact equality each retain distinct output fields; a midday return followed by a failed17:00 close is not source success.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P05-A-2026-01-28.png>) | true | yes — source bearish session counter; code uses another branch | Code00:00–03:00 bullish body yields26292.06. The AM final close is far below this line, so the retained positive is the failure branch, not a successful bullish wick/close-back. The source uses02:00–08:00 London and08:00–17:00 NY. Literal source-clock arithmetic gives London02:00 open26301.75/08:00 close26281, bearish25%26286.1875; NY08–17 high26306 and close26268.25 do satisfy bearish wick/close-back. Same Boolean, different side, level and event. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P05-B-2026-07-10.png>) | false | no — for the plotted bearish close-back | Code London bearish25%-body level29847.88 is crossed repeatedly, but the AM ends above it. A bearish wick and session close back below is absent; a single local downward wick is not the source session counter. Source-clock02–08 bearish level29823.8125 also fails the bearish close-back: NY08–17 closes30068.5 above it. |

### R-P06 — Mapper first-side and opposite-side hits on the source clocks

The source Asia20:00–02:00, London02:00–08:00 and NY08:00–16:00 tables condition on session open versus the previous session midpoint. First-hit ties choose HIGH, and the opposite sequential flag can be set in the same chart bar. Asia-in-NY uses crossover/crossunder rather than any span. FORMULAS’s later opposite hit and generic hit description do not fully describe these source branches.

The caller substitutes Asia20:00–00:00 and London00:00–03:00, returns only whether any London first hit exists, and omits the NY and conditioned tables. The helper chooses both-side ties by overshoot and delays sequential detection to a later bar. July10 source Asia low is first reached02:21; August28 source low is reached03:44, outside the legacy London window, so the retained false is not a source negative.

**Source references:** [PINE NQ Statistical Mapper.txt L199](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Statistical Mapper.txt:199>); [PINE NQ Statistical Mapper.txt L283](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Statistical Mapper.txt:283>); [PINE NQ Hourly Retracement Levels.txt L128](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracement Levels.txt:128>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p06_first_hit](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1190>), [recipe_score.py::_preds.p06](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:760>), [FORMULAS.md::R-P06](</workspace/planning/phase-1-live/FORMULAS.md:587>).

**Build steps:**

1. Document literal source tie, same-bar sequential and Asia-NY crossover semantics before certification. A chronology-correct execution variant may differ but must retain its own name. Use20–02/02–08/08–16NY and validate all source bars.
2. Freeze completed prior-session H/L/M at each new session. Position is current open>M, with equality below. Track first high/low hit and opposite flag, storing timestamps and both-side-bar ambiguity; implement the literal high-first tie only for that source branch.
3. Build London-versus-Asia and NY-versus-London separately. For Asia levels during NY store the source crossover predicates using previous/current values as well as any named span alternative, conditional on whether the corresponding level was hit in London.
4. Use strict London engulf, inclusive Asia containment and specified partial-up/down branches. Report first-high, first-low, no-hit and conditional opposite-hit rates for each position/pattern cohort; hardcoded probabilities remain reference claims.

**Acceptance checks:**

- July10 source Asia H29963.5/L29804.25 has first low touch02:21. August28 H29707/L29594.25 has first low touch03:44 and cannot be labelled source no-hit by the00–03 proxy.
- A bar reaching both bounds chooses HIGH in literal source and can mark sequential immediately; the named causal view reports unresolved order if executions are unavailable.
- An Asia level already exceeded before NY and never recrossed distinguishes crossover from any-reach. Empty conditional populations have n=0.
- August26,2026 is a real source-clock no-hit: Asia20–02 H29283.25/L29096, London02–08 H29278.75/L29185. The legacy code is positive from the shorter Asia high29275.25. Keep source no-hit and legacy positive distinct.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P06-A-2026-07-10.png>) | true | yes — Asia-low first hit, clock caveat | Code GB Asia L29804.25 is broken during the00:00–03:00 substitute London interval, while H29963.5 stays unhit. The actual source clock begins London at02:00 and must be evaluated against Asia completed then; the plotted old clocks are not faithful geometry. Source20–02 Asia has the same extrema on this date; first London low hit occurs02:21. |
| [B / 2026-08-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P06-B-2026-08-28.png>) | false | yes — source London low hit omitted by code | Code Asia L29594.25 is missed by the00:00–03:00 low29594.50, giving false. The visible decline around04:00 then breaks that low during the source02:00–08:00 London session. Wrong window can turn a source first hit into a code negative. Exact source20–02 Asia L29594.25 is first hit at03:44, inside02–08 London but after the code00–03 window. |
| [event-negative / 2026-08-26](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P06-event-negative-2026-08-26.png>) | true | no for source-clock London first hit of Asia | August26,2026 source Asia20:00–02:00 H29283.25/L29096; London02:00–08:00 H29278.75/L29185 remains strictly inside, so neither first hit exists. Legacy Asia20–00 H29275.25 is reached during the legacy00–03 London box, explaining code=true. The source overlay and old boxes show how the wrong clock creates this false positive; same-bar tie/NY branch conflicts still stop whole-family certification. |

### R-P07 — OR5/OR15 midpoint returns and correctly conditioned source tables

The source first extreme is the first attainment of the FINAL OR high/low WITHIN the OR, not the first post-OR edge touch in FORMULAS. Doji is bullish (C>=O); the midpoint flag is not session-gated and source extension comparisons are strict. Its unconfirmed security values and SessionClose validation flag also require availability cautions. Stop the current cohort definition before using source probabilities.

The helper computes an actual midpoint but calls onlyOR5 with an outcome ending at noon, uses C>O and post-OR first extreme, and the scorer retains only midpoint return. Both plotted dates formed the OR low09:30 before high09:33, while the helper calls high first from later action. July10 midpoint29866.875 returns09:39; October8 midpoint25104.5 never returns in RTH.

**Source references:** [PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt L141](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:141>); [PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt L476](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:476>); [PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt L899](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:899>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p07_or_mid](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1218>), [recipe_score.py::_preds.p07](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:763>), [FORMULAS.md::R-P07](</workspace/planning/phase-1-live/FORMULAS.md:596>).

**Build steps:**

1. Correct the source description to distinguish within-OR extreme order, after-OR edge hits and IB path. Declare the literal unbounded midpoint flag versus a named RTH-bounded return. Do not interpret the source SessionClose boolean as checking direction; it only checks that the session ended.
2. Build complete09:30–09:35 and09:30–09:45 candles. At their ends freeze final H/L/O/C/M and locate the earliest complete constituent minute attaining each final extreme, high on source tie. Set bullish=C>=O; no OR-derived feature exists before its completion.
3. After each completion evaluate midpoint span or close-cross using the resolved source horizon. Separately draw price-percentage extensions:5m H*1.00411/L*.99550;15m H*1.00380/L*.99585. Strict source extension reach and named inclusive touch need separate fields.
4. Report midpoint rate by OR duration×colour×within-OR first extreme, extension reaches, later IB direction and source next-break prediction/outcome separately. Recompute all denominators from eligible sessions; do not treat copied probabilities or a reached opposite edge as proof of a first-post-OR race.

**Acceptance checks:**

- July10 andOctober8 both use within-OR low09:30 before high09:33. Their later high-first path must not alter the combo key.
- July10 midpoint29866.875 touches09:39; October8 midpoint25104.5 is unhit in RTH despite reaching the upper extension. A PM-only midpoint return distinguishes noon from RTH horizon.
- A doji is bullish in source; an exact extension-edge touch fails a strict reach. No5m box level may be used at09:32.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P07-A-2026-07-10.png>) | true | yes — midpoint touch; combo unresolved by FORMULAS | OR5 H29921.25/L29812.5 gives mid29866.875, touched around09:39. Both unscored price-percent extension levels are later reached (lower29678.34 near10:32 and upper30044.23 in PM). Source extreme chronology is within OR, while the helper reads after OR. Final OR low occurs09:30 and high09:33 in both plotted cases, hence source intra-OR extreme order is low-first; helper after-OR order is high-first. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P07-B-2025-10-08.png>) | false | no — midpoint touch | After09:35 price stays above OR midpoint25104.5 through16:00, so no midpoint retest exists. Upper price-percent extension25238.30 is reached, showing that extension and midpoint retest are separate events. Final OR low occurs09:30 and high09:33 in both plotted cases, hence source intra-OR extreme order is low-first; helper after-OR order is high-first. |

### R-P08 — IB eight-way class, source midpoint-band retest and extensions

The source combo is IB colour, first attainment of FINAL IB high/low WITHIN the IB, and IB CLOSE versus midpoint. FORMULAS says open versus midpoint and post-10:30 first touch, changing the table key. The source0.1%-of-price return uses an endpoint-near test and can leave/return in the same bar; it also skips the first post-IB bar and processes16:00 before reset. These variants cannot share unqualified source claims.

The current scorer is a reduced close-break path class after10:30, without the eight combo keys, midpoint leave/return, percentile extensions or source wick inequalities. January28 IB26301/26205 breaks only low on closes; July10 IB29968.5/29798 later breaks both. Correct box placement does not validate the missing source statistic.

**Source references:** [PINE Initial Balance Statistical Mapping.txt L44](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Initial Balance Statistical Mapping.txt:44>); [PINE Initial Balance Statistical Mapping.txt L55](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Initial Balance Statistical Mapping.txt:55>); [PINE Initial Balance Statistical Mapping.txt L279](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Initial Balance Statistical Mapping.txt:279>).

**Code to change:** [recipe_score.py::_preds.p08](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:766>), [family_open.py::build_open_table](</workspace/implementation/src/trading_research/research/phase1_live/family_open.py:142>), [FORMULAS.md::R-P08](</workspace/planning/phase-1-live/FORMULAS.md:981>).

**Build steps:**

1. Correct the source combo to C>=O, first final extreme within09:30–10:30, and C>mid (equality below). Preserve the source’s post-boundary update defects as a literal variant; a corrected causal variant must be labelled independently.
2. At10:30 freeze complete IB H/L/O/C/M and source combo. Scan later highs/lows for strict wick breaks. Keep close-break paths as a separate existing research row; do not let an eventual both-side path rewrite first-break side.
3. For the literal midpoint retest set d=M*.001: first abs(C−M)>d, then endpoint abs(L−M)<=d or abs(H−M)<=d, allowing source same-bar behaviour. A general band overlap or a two-tick touch is a different event. Store leave/retest timestamps and ambiguity.
4. Draw upper H*(1+p/100) for p=.140,.314,.601,.997 and lower L*(1−p/100) for p=.163,.380,.794,1.366. Report each reach, return time, first break and final RTH direction per eight-way cohort; do not reuse P08’s reduced single-path rate.

**Acceptance checks:**

- An IB whose open is below midpoint but close above must be ABOVE. A final high formed09:45 before low10:05 must be high-first regardless of later boundary contacts.
- January28 low-only andJuly10 both-side close paths remain valid labelled reduced observations; neither supplies the missing source combo/retest outcomes.
- A bar spanning the entire midpoint band with both endpoints far away is not a literal endpoint-near return. Test exact0.1% equality and first10:30/16:00 boundary handling.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P08-A-2026-01-28.png>) | true | cannot-tell — wrong combo definition in FORMULAS | IB09:30–10:30 H26301/L26205, mid26253. Price closes below the low around10:34 and never exceeds the high through16:00. This is the retained low-only path, but source combo uses final IB extreme order within IB and IB close relative to midpoint, not the documented open/after-IB substitution. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P08-B-2026-07-10.png>) | false | no — single-side path; source combo stopped | IB H29968.50/L29798, mid29883.25. Both sides break after10:30: lower on the10:32 spike, upper around11:23. Code false correctly means not single-side; it is not a failed source midpoint-retouch or extension forecast. |

### R-P09 — Open-location conditional no-break rates over the complete RTH

The source prints conditional above/below far-side no-break and inside zero/one/both-side rates. Its time() calls omit timezone, so default Custom08:30–16:00 and the09:30–16:00 toggle use the chart exchange clock. FORMULAS labels them as NY without resolving that setting. The source displays fixed claims rather than dynamically computing those rates.

Unlike the stale CODE paragraph, the producer now uses full09:30–16:00 NY H/L and strict wick breaks correctly for that named window. It then ORs above/below far-side no-break with inside stay, losing the distinct conditional probabilities. January28 opens above priorH26114.25 and never breaks farL25917.25; July10 opens inside and later breaks only the upper edge.

**Source references:** [PINE NQ Stats RTH Breaks with stats.txt L27](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats RTH Breaks with stats.txt:27>); [PINE NQ Stats RTH Breaks with stats.txt L61](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats RTH Breaks with stats.txt:61>); [PINE NQ Stats RTH Breaks with stats.txt L148](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats RTH Breaks with stats.txt:148>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p09_no_break](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1263>), [recipe_score.py::_preds.p09](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:769>), [FORMULAS.md::R-P09](</workspace/planning/phase-1-live/FORMULAS.md:605>).

**Build steps:**

1. Resolve and record the source chart symbol, exchange timezone and session selector. Keep the current NY09:30–16:00 as an explicit named variant until the source setting is known; do not assume08:30 exchange time equals08:30NY.
2. Require complete previous and current sessions on the selected clock. Freeze prior H/L before current open; classify Above if O>H, Below if O<L, otherwise Inside. Equal edge opens belong Inside.
3. Use strict wick H_today>priorH and L_today<priorL for the final session outcome. For Above return no_break_prev_low, for Below no_break_prev_high, and for Inside return exactly one of stay/one_side/both. Nonapplicable outputs remain null.
4. Publish each conditional rate with its own cohort count and both above/below directions. If retaining a pooled OR summary, name it explicitly and keep it separate from84.11/81.82/14.30 claims. An unfinished session is censored until its close.

**Acceptance checks:**

- January28 namedNY Above cohort is far-side no-break true. July10 Inside is one-side true and stay false after the afternoon upper break.
- A wick equal to a prior edge is not a strict break; an open on the edge is Inside.
- CME exchange08:30 and NY08:30 must not accidentally index the same interval. The three Inside outcome counts must sum to the eligible Inside cohort.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P09-A-2026-01-28.png>) | true | yes — declared New York no-far-side-break variant | Open26252.5 is above prior RTH high26114.25; the full RTH path never reaches far-side low25917.25. The narrow no-far-side-break event is true. Pine uses exchange-time session calls, so its literal runtime clock must remain separate from the declared NY variant. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P09-B-2026-07-10.png>) | false | no — inside-stay branch | Open29834.75 is inside prior[29614.5,29993.5]. The RTH path exceeds the upper boundary after noon while staying above the lower, so inside-stay is false and inside-one-side is true. The pooled Boolean does not retain these separate conditional outcomes. |

### R-P10 — Floor-pivot geometry, opening zones and actual level contacts

The source classical pivots share prior H/L/C algebra with the implemented P/R1–3/S1–3. It also has R4/R5/S4/S5 and golden zones, and printed opening-zone statistics whose state is reset every bar in source. Timezone is implicit and the headline probabilities are hardcoded. A one-sided high>=P test does not establish contact with P.

Current pivot lines are correctly placed for the named prior18:00–17:00 Globex inputs, but the producer scores only RTH high>=P, omits the lower price bound and supplies no opening-zone outcomes. July10 P29773.25 is actually contacted10:32; January10 P21313.33 is uncontacted during RTH despite the earlier08:30 move. Most fields described by the source remain unscored.

**Source references:** [PINE Daily Floor Pivots.txt L1](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Daily Floor Pivots.txt:1>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p10_pivots](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1282>), [recipe_score.py::_preds.p10](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:772>).

**Build steps:**

1. Record the source session/timezone and prior completed H/L/C convention. Preserve source opening-state reset behaviour as a literal defect; a fixed opening-zone study must have its own name. Freeze the prior inputs before the new session.
2. Retain P=(H+L+C)/3, R1=2P−L, S1=2P−H, R2=P+(H−L), S2=P−(H−L), R3=H+2(P−L), S3=L−2(H−P). Port remaining R4/R5/S4/S5 and golden-zone formulas exactly from the reviewed source, retaining formula/line references and tick rounding for every bound.
3. Detect actual per-bar overlap low<=level<=high, or a separately declared crossing/tolerance rule, rather than high>=level alone. Return first contact time for each level and zone; a price that stays wholly above P does not touch it.
4. Freeze the opening zone once at the session open and report each specified later target/contact conditional on that zone. Keep P contact, golden-zone entry, further pivot reach and quoted source claims as different outputs with complete-session denominators.

**Acceptance checks:**

- July10 P29773.25 contact10:32 is a positive actual contact; January10 RTH stays belowP21313.33, so it is negative regardless of pre-RTH touches.
- For H120/L100/C110, P110,R1/S1=120/100,R2/S2=130/90,R3/S3=140/80. A session entirely above115 cannot touchP110.
- Later price moving between opening zones must not rewrite the initial zone; verify every added source level algebra against a non-symmetric H/L/C fixture.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P10-A-2026-07-10.png>) | true | yes — PP contact | Code PP29773.25 is genuinely crossed by the10:32 drop/rebound; it is not merely below the day high on this date. Classic R1–R3/S1–S3 coordinates are drawn; Golden Zones and R4/R5 are not implemented. One-sided max>=PP still admits false positives on other days. |
| [B / 2025-01-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P10-B-2025-01-10.png>) | false | no — PP contact | PP21313.33 remains above all RTH price after09:30; the08:30 drop precedes that scoring window. S1/S2/S3 interact with the falling price but are not the scored PP event. |

### R-P11 — First-presented 5m FVG by window, fill depth and hourly bias

Default source FVG timeframe is5m. Its W1 condition actually opens09:00 despite the09:30 comment; raw security lookahead_on and chart-shifted HTF timestamps can expose future data. The first15-minute bias reads a later selected-bar close. The source never defines the hardcoded effectiveness event, while FORMULAS chooses hourly direction. Stop faithful certification of that choice and of the W1 clock.

The current producer searches one-minute09:30–10:00 bars and scores whether a gap exists, passing no fill outcome.645/647 is presence, not fill/effectiveness. July10 first BISI29892.75–29893.5 forms on09:33 bar, known09:34, and later fills; August7,2024 has no qualifying1m gap in that window. Neither decides the missing source5m W1/W2 study.

**Source references:** [PINE First presented FVG (with stats) with statistical hourly ranges & bias.txt L8](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/First presented FVG (with stats) with statistical hourly ranges & bias.txt:8>); [PINE First presented FVG (with stats) with statistical hourly ranges & bias.txt L148](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/First presented FVG (with stats) with statistical hourly ranges & bias.txt:148>); [PINE First presented FVG (with stats) with statistical hourly ranges & bias.txt L170](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/First presented FVG (with stats) with statistical hourly ranges & bias.txt:170>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p11_first_fvg](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1298>), [recipe_score.py::_preds.p11](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:775>), [FORMULAS.md::R-P11](</workspace/planning/phase-1-live/FORMULAS.md:623>).

**Build steps:**

1. Resolve literal09:00 W1 versus intended09:30 and preserve effectiveness as undefined unless the source author supplies its outcome. Treat hourly direction and near/mid/far fills as explicitly named research outcomes. Correct the source availability account before using unshifted HTF values.
2. Build complete5m bars and identify bull low_i>high_(i−2) AND close_i>high_(i−2), bear high_i<low_(i−2) AND close_i<low_(i−2). Carry native bar times; middle-bar membership uses the actual HTF middle candle. Freeze a new gap only at formation bar completion.
3. Select first gap independently for resolved W1 and W2=10:00–11:00. Bounds are[high_(i−2),low_i] for bull or[high_i,low_(i−2)] for bear. Track fills only after formation, using later lows for bull and later HIGHS for bear; the helper’s single later_low argument cannot represent both.
4. Keep gap presence, first direction, first15-minute bias, final hourly direction and each fill depth/time separate. W1 output is available after its end and W1/W2 combo after11:00; fixed source effectiveness arrays are reference claims, not observed success labels.

**Acceptance checks:**

- July10 one-minute gap known09:34 must be labelled1m comparison, not default5m source evidence. August7,2024 absence of that1m gap cannot prove no5m event.
- Bull gap[100,103] later low102 fills near but not mid101.5 or far100; bear mirror uses later high. Formation-bar wick cannot serve as a later fill.
- A09:20 middle-bar gap distinguishes literal W1 from the comment. No five-minute high/low may enter a decision before its completion.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P11-A-2026-07-10.png>) | true | cannot-tell — source timeframe/window/effectiveness conflict | Code first1m BISI band29892.75–29893.50 comes from09:31/09:32/09:33 candles, known09:34. Later candles return into it, but the producer passes no fill path and scores existence. Source default5m, W1 code/comment disagreement and undefined effectiveness prevent certification of the named source event. |
| [B / 2024-08-07](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P11-B-2024-08-07.png>) | false | no — code one-minute FVG presence | The overlapping09:30–10:00 one-minute ranges contain no qualifying first gap, and no zone is drawn. This is a valid code-presence negative, not proof of absence in the source5m/W1-W2 setup. |

### R-P12 — Distinct HTF sweep, CISD and T-spot implementations

The source Model default main HTF is60m, with an LTF opposing-run2..10 CISD confirmed using the previous chart close. Its C3 box is current open to C2 BODY midpoint. OSF uses C2 H/L midpoint and its own LTF run/projection rules; the Sweep/CISD sibling has yet another selective log-wick midpoint. FORMULAS substitutes15m and an HTF-close CISD and mixes candle identities in its fixture. These are separate sources, not interchangeable definitions.

Current code passes only09:30 and09:31 one-minute candles, tests high sweep/close-back, and never tests low sweep or CISD. Its unscored mid_box uses prior body mid and current O. January2,2026 has a high sweep of25728.75 and a close-back; July10 sweeps prior high29876 but closes above it.133/647 therefore measures this two-minute high-only test.

**Source references:** [PINE HTF Sweep Model with CISD Table.txt L136](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweep Model with CISD Table.txt:136>); [PINE HTF Sweep Model with CISD Table.txt L309](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweep Model with CISD Table.txt:309>); [PINE HTF Sweep Model with CISD Table.txt L343](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweep Model with CISD Table.txt:343>); [PINE HTF Sweeps & Liquidity Levels with CISD.txt L695](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/HTF Sweeps & Liquidity Levels with CISD.txt:695>); [PINE Open Source Fractal - Customized.txt L1](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Open Source Fractal - Customized.txt:1>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p12_sweep_cisd](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1327>), [recipe_score.py::_preds.p12](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:778>), [FORMULAS.md::R-P12](</workspace/planning/phase-1-live/FORMULAS.md:632>).

**Build steps:**

1. Stop the combined faithful row. Name the exact file/version, HTF/LTF, sweep strictness and C1/C2/C3 identities before implementing. Preserve Model close-only screener, strict-inside closed box and body-inside live-line variants separately; OSF and the log-wick sibling need distinct records.
2. For each chosen version build completed HTF candles causally and process both sweeps. Carry wick/body/inside tests independently, including double-sweep cases and equality. No current unconfirmed security high/low may be backfilled as known at the HTF open.
3. Port only that version’s opposing-run CISD search, run-open selection, age limit, crossing and bar-completion lag. Model uses LTF runs2..10 and prior chart-close confirmation; OSF has its own extreme/run fallback and projection span. A sweep close-back alone cannot be a CISD.
4. Construct the selected box from the actual next candle open and specified prior midpoint, attach known_at, lifespan and source invalidation. After CISD/box creation measure retest and objective reaches chronologically. Source OSF creates projection labels without projection lines; do not certify lines as a literal source feature without labelling an added display.

**Acceptance checks:**

- January2 high-sweep close-back at09:31 is a named one-minute positive only; July10 close above29876 is a negative for that test. Neither establishes HTF CISD.
- For C2 O100/C110/H120/L90, body midpoint105 and H/L midpoint105 coincide; add an asymmetric candle O100/C104/H120/L90 to distinguish102 from105. C3 open must not be substituted for C2 open.
- Test low mirror, both-edge sweep, body equality, run lengths1/2/10/11 and a cross known one bar later. Future C3 price cannot alter the established C2 sweep.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-02](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P12-A-2026-01-02.png>) | true | yes — one-minute high-sweep close-back only | The09:31 candle exceeds prior09:30 high25728.75 and closes back below it; the unscored helper box25704.25–25721 uses the previous body midpoint and current open. This is no completed60m sweep, CISD run or source C3 box. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P12-B-2026-07-10.png>) | false | no — one-minute high-sweep close-back | The09:31 candle exceeds prior high29876 but closes above it, so the scored close-back is false. The helper box29855.25–29874.75 exists independently of CISD; later price crossings cannot retroactively confirm the first two-bar flag. |

### R-P13 — Midnight-open touch in08:00–16:00, with ancillary table gaps

The source midnight level is the00:00NY open, with exact bar-span touch in08:00–16:00. The hourly source also shows00–01/02–03/07–08 midpoints and other hour opens, plus position/pattern-conditioned claims. The two sources quote73.67% and73.75%; they are distinct historical claims, not evidence that the implementation must reproduce either exact number.

The current tdo_hit helper and tdo_touch_ny scorer correctly implement the stated midnight-open touch, unlike the stale09:30–12:00 CODE paragraph.460/647 is the retained pooled exact-touch count. July10 level29933 is actually touched; August31 level29352.5 stays below every NY bar. The four yes verdicts certify this headline predicate and geometry; the ancillary midpoint/conditional table rows remain missing.

**Source references:** [PINE NQ Hourly Retracement Levels.txt L128](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracement Levels.txt:128>); [PINE NQ Hourly Retracement Levels.txt L279](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Hourly Retracement Levels.txt:279>); [PINE NQ Statistical Mapper.txt L310](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Statistical Mapper.txt:310>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [formulas.py::tdo_hit](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:258>), [recipe_score.py::_preds.p13](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:802>), [FORMULAS.md::R-P13](</workspace/planning/phase-1-live/FORMULAS.md:990>).

**Build steps:**

1. Preserve the correct00:00 open and08–16 exact per-bar span predicate; update FORMULAS’s stale current-code account. Record the first spanning minute and its completion/observation time, source claim version and full-window coverage.
2. Require the00:00 bar and a complete eligible08–16 observation window. Missing origin or outcome bars must be null/censored, not false. Do not widen to two ticks or replace span with whole-session high/low containment.
3. For the described ancillary family, retain each hour open and completed hour midpoint as a separate level with own known_at. Build00–01,02–03 and07–08 midpoints from their actual complete hours; no level may project before completion. Keep all16 source hourly references individually addressable.
4. Add conditional counts by08:00 open versus completed London02–08 midpoint and by source Asia20–02/London pattern, using P06’s explicit source branches. Preserve the current pooled midnight rate separately and compare source hardcoded claims without forcing equality.

**Acceptance checks:**

- July10 TDO29933 spans in08–16; August31 TDO29352.5 does not. These remain source-event positive/negative examples.
- Two bars entirely on opposite sides with a data gap between them do not imply an observed span touch; an actual high==level or low==level does.
- An absent midnight bar is unknown. A07–08 midpoint cannot be made available at07:30, and conditional counts must sum to the eligible covered population.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P13-A-2026-07-10.png>) | true | yes for exact midnight-open hit | 00:00 open29933 spans in NY around09:37 and again09:49; the full08–16 chart confirms the corrected current source window. Source companion hourly mids/conditional tables remain absent. |
| [B / 2026-08-31](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P13-B-2026-08-31.png>) | false | no | 00:00 open29352.5 stays below every08–16 candle, including the10:25 low slightly above it. Retained false is an actual no-touch observation. |

### R-P14 — Causal four-hour elimination state and HOD/LOD-already-in outcomes

The source freezes state at22/02/06/10/14 after the prior candle completes and before processing the new bar. Every completed candle has its own eliminated flag; prev compares the just-completed candle with its immediate predecessor. FORMULAS instead refers to the new checkpoint candle, and its fixture undercounts eliminated older candles. Unsupported source lookup combinations return50 with sample0, not measured50% probability.

The actual producer never calls r_p14_hod_checkpoint. It compares09:30–10:00 high with final09:30–16:00 high within one tick, with no four-hour state, ETH day or LOD. The unused helper counts changes of the running maximum rather than all eliminated candles and ignores the actual checkpoint when testing hod_at. January28 RTH H26301 is in by10; July10 final H30077.75 prints about15:03.

**Source references:** [PINE 4H HOD LOD Checkpoint Analysis.txt L30](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/4H HOD LOD Checkpoint Analysis.txt:30>); [PINE 4H HOD LOD Checkpoint Analysis.txt L401](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/4H HOD LOD Checkpoint Analysis.txt:401>); [PINE 4H HOD LOD Checkpoint Analysis.txt L556](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/4H HOD LOD Checkpoint Analysis.txt:556>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p14_hod_checkpoint](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1344>), [recipe_score.py::_preds.p14](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:781>), [FORMULAS.md::R-P14](</workspace/planning/phase-1-live/FORMULAS.md:641>).

**Build steps:**

1. Correct the checkpoint/prev definition and source fixture before certification. Use source18–22,22–02,02–06,06–10,10–14 and14–17 windows, allNY. Retain first-bar/reset source defects as a literal variant; a causal reconstruction must say which defects it corrects.
2. For each completed candle store H/L and two persistent eliminated flags. A later strictly higher high eliminates EVERY earlier completed candle below it, not just the last running maximum; lows mirror. Store each elimination time and use the source chronological flag indices to derive sequential/skip.
3. At each checkpoint snapshot only completed prior state before the new bar contributes. Compute prev from the just-completed candle versus the immediately preceding candle. Freeze this feature record; use the eventual18–17 session high/low only as later labels, with tie/first-attainment policy explicitly specified.
4. Measure HOD/LOD already present at each checkpoint and table rates by checkpoint×elimination count×structure×prev. Keep the existing RTH-before10 label as a named comparison. Unsupported/empty states have n=0 and no estimated probability; never treat source fallback50 as a forecast with evidence.

**Acceptance checks:**

- High sequence16700,16690,16705,16698 eliminates both first candles by10:00, not just16700. Altering prices after10 must not alter the10:00 feature snapshot.
- January28 RTH H26301 before10 andJuly10 H30077.75 after10 exercise only the named RTH outcome; source ETH state requires its separate event ledger.
- Test low mirror, equality (not strict elimination), skip structure, missing completed candle and unsupported sample0. A final session HOD supplied as a feature must fail the availability check.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P14-A-2026-01-28.png>) | true | yes for named RTH-HOD-before10 outcome; source checkpoint state unavailable | First30m H26301 at09:44 equals final RTH HOD; plotted final HOD is explicitly an outcome. Source18–17 four-hour elimination state is not implemented. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P14-B-2026-07-10.png>) | false | no for named RTH-HOD-before10 outcome | First30m H29968.5 is exceeded later; final RTH HOD30077.75 prints about15:03. No source LOD/4H checkpoint state is drawn because it is absent. |

### R-P15 — Separate SSL, range-projection and OHLC-distribution envelopes

These are three distinct source constructions. SSL uses100-session nearest-rank histories and has a bearish-side drawing swap plus counters mixing frozen levels with newly appended current data. SRP uses three15-minute boxes, whole-candle body extrema and range1-only statistics; its independent both-side hits are not ordered reversals. OHLC projection distribution is M+D (full range), while FORMULAS draws D alone and says latest60 despite source choosing oldest60 and unshifted live HTF data. Stop the combined faithful row.

The producer substitutes prior60 RTH median widths, assumes MFE=.6*width and MAE=.4*width, anchors09:30 and scores only the upper threshold over full RTH. No source session quantiles, SRP ladder or OHLC history is assembled. July10 upper30071.15 is reached around15:03, outside source08–12 NY Morning; January28 upper26423.425 is unhit while the ignored lower threshold26138.55 is crossed.

**Source references:** [PINE Session Statistical Levels.txt L24](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Statistical Levels.txt:24>); [PINE Session Statistical Levels.txt L707](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Statistical Levels.txt:707>); [PINE Session Range Projections with stats.txt L372](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Session Range Projections with stats.txt:372>); [PINE Statistical OHLC Projections HTF.txt L322](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Statistical OHLC Projections HTF.txt:322>); [PINE NQ Stats Price Distributions.txt L302](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats Price Distributions.txt:302>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p15_ssl](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1375>), [formulas_flow.py::r_p15_srp](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1390>), [formulas_flow.py::r_p15_ohlc_md](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1395>), [recipe_score.py::_preds.p15](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:784>), [FORMULAS.md::R-P15](</workspace/planning/phase-1-live/FORMULAS.md:650>).

**Build steps:**

1. Stop certification and register explicit file/version/variant identities for SSL, SRP and OHLC projections. Preserve source counter, selection and drawing defects in literal replication; any corrected causal version must be separately named. Remove invented0.6/0.4 excursion quantiles from source-labelled fields.
2. SSL: use19–02,02–08,08–12,12–17NY. For each completed same session retain range=H−L, up=H−O, down=O−L and close displacement. At next session start freeze last100 priors and nearest-rank q=10/25/50/75/90. Symmetric levels O±Qq(range) differ from O+Qq(up)/O−Qq(down). Preserve source bearish MFE/MAE swap only in its literal drawing branch.
3. SSL events: compute each level touch and same-sideP90 reach followed by close back insideP75, using the SAME frozen thresholds in numerator and denominator. Store all-history source counters separately from rolling100 estimates; appending the current session must not redefine that session’s already evaluated levels.
4. SRP: construct02/09/13:00–:15 wick H/L or body max/min across ALL constituent candle O/C values. Draw H+kW and L−kW for k1..6 after completion. Range1 stats run02:30–08:00; store side incidence and both conditional on each side, without imposing a source-unprinted sequence. True SD of last100 widths including just-completed box is a distinct display, default O±kσ, not kW.
5. OHLC: choose exact HTF and session anchor (default8h, daily18:00 with midnight option). For completed bullish candle M=O−L,D=H−O; bearish M=H−O,D=O−L, retaining source doji branch. Use same-slot history. Literal oldest60/unshifted source must be flagged; causal last60 completed priors is an explicit corrected version. Distribution distance is mean(M)+mean(D), or median(M)+median(D), not just D; manipulation is M. Keep separate up/down percentiles and max-range definitions.
6. For every subfamily plot the actual anchor and every implemented bound, record known_at/history membership, and report per-side touch/reversion outcomes over its own window. Source close-inside percentages from NQ Price Distributions use that file’s return-sigma method and cannot validate these envelopes. No missing geometry is added during this audit.

**Acceptance checks:**

- July10 afternoon hit30071.15 cannot establish source08–12 MFE success. January28 lower26138.55 reach must not disappear under a high-only statistic.
- For completed bull O100/H150/L80/C140, M20,D50 and distribution distance70, not50. Median(M)+median(D) must not be assumed equal to median(M+D).
- Changing current-session final H/L cannot move frozen SSL thresholds. SRP body mode on a multi-bar box must use max/min of all bodies, not only session O/C. Test nearest-rank versus interpolation and100 versus60 histories.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P15-A-2026-07-10.png>) | true | cannot-tell for source SSL; yes for arbitrary code threshold | Code upper MFE30071.15 is reached around15:03, after source08–12 NY Morning ended; lower MAE29677.15 tags10:32. Code uses0.6/0.4 of60 prior RTH median ranges, not actual excursion quantiles. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P15-B-2026-01-28.png>) | false | cannot-tell for source SSL; no for arbitrary upper code threshold | Code MFE26423.425 remains far above RTH high26301; lower MAE26138.55 is crossed around11:44 but never contributes to the scored upper MFE flag. Symmetric range levels26537.375/25967.625 remain unhit. |

### R-P16 — Eight logarithmic volatility bands with a declared substitute and outcome

Expected Volatility uses prior chart DAILY close and prior NASDAQ:VOLI daily close with a=V/16/100 and b=V/√365/100. Its session uses fixedGMT−5, and lower rectangle bounds are supplied in reversed order. VIX is a declared substitute, not VOLI. The75.2% daily-close claim comes from a different return-distribution script, so it does not describe whole-path containment in these bands. FORMULAS does not preserve those differences.

Current code has improved: it uses prior-session VIX and prior18–17 last close with correct log-space a/b bounds. It scores whole18–16NY path inside the outer1.0 bands, not per-zone touch or final-close containment. Prior last print is not verified official settlement and missing Globex data may fall back to RTH.658 retained rows lack the four newest bound keys. July10 fits outer29636.39–30229.04; October8 rises above25326.17 late in RTH.

**Source references:** [PINE Expected Volatility .txt L11](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Expected Volatility .txt:11>); [PINE Expected Volatility .txt L30](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Expected Volatility .txt:30>); [PINE Expected Volatility .txt L58](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Expected Volatility .txt:58>); [PINE NQ Stats Price Distributions.txt L302](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/NQ Stats Price Distributions.txt:302>).

**Code to change:** [family_levels.py::build_level_table](</workspace/implementation/src/trading_research/research/phase1_live/family_levels.py:131>), [formulas.py::ev_vix16_zones](</workspace/implementation/src/trading_research/research/phase1_live/formulas.py:247>), [recipe_score.py::_preds.p16](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:805>), [FORMULAS.md::R-P16](</workspace/planning/phase-1-live/FORMULAS.md:999>).

**Build steps:**

1. Name instrument, volatility input, source clock and prior price field explicitly. Preserve current VIX/last-Globex-close as a named proxy; VOLI is unavailable. Resolve fixedGMT−5 versus NY DST and source DAILY-close versus official settlement before faithful comparison. Do not silently use RTH close when the required input is missing.
2. Retain correct geometry: for k=.25,.5,1,1.5 upper=[A*exp(kb),A*exp(ka)] and lower=[A*exp(−ka),A*exp(−kb)]. Keep numeric lower bounds sorted for research drawing while recording source’s reversed rectangle arguments as a literal display defect. Freeze all inputs before the session starts.
3. Store distinct events for every inner/outer edge touch, interval entry, whole-session outer1.0 containment and final-close containment. The existing p16_inside may remain as the explicitly named whole-path outcome; it cannot inherit75.2% from a different sigma construction.
4. Require all source-bound keys, input dates, clock and schema version on cache reuse. Rebuild missing bound records in a later implementation task and compare actual price-path outcomes separately from geometry. Missing VIX/VOLI/anchor is null with reason and an excluded denominator.

**Acceptance checks:**

- July10 lower inner1.0 edge29684.11 is exceeded by low29675 but lower outer29636.39 is intact; these are different outcomes. Full path remains inside outer bands.
- October8 outer upper25326.17 is exceeded before16:00; whole-path containment is false. A path leaving and closing back inside must differ from final-close containment.
- At A16600,V14.04 verify all16 bounds from the exact exponential formula. July fixedGMT−5 session18–16 is19–17NY; winter agrees. A cache missing any required bound is invalid.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P16-A-2026-07-10.png>) | true | yes for named VIX whole-session outer-band containment; source VOLI unavailable | Prior Globex last close29931.25; outer1.0 bounds29636.39–30229.04 contain18–16 path. Lower inner1.0 edge29684.11 is breached by10:32 spike to29675, while outer remains intact; all8 bands and16 bound labels visible. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P16-B-2025-10-08.png>) | false | no for named VIX outer-band containment | Prior close25054.75; outer1.0 bounds24786.23–25326.17. Late RTH rally moves above upper25326.17 before16:00; smaller upper bands traverse earlier. This is containment, not source daily-close probability or per-zone touch rate. |

### R-P17 — Literal OHLC-profile allocation and separately scoped daily/weekly opens

Source defaults are30 equal-height rows and70% volume. VA expands alternately DOWN thenUP by distance, not heavier-neighbour as FORMULAS also says. Literal source omits the threshold-crossing row and can null the POC at the final row. Source profile clocks (including fixedUTC NY/London and exchange-day Daily) differ from the named prior-RTH transplant. The18:00NY daily and Sunday weekly opens are separate from profile clocks. Stop the contradictory profile specification.

The scored flag only checks whether full RTH high/low brackets the prior18:00 open; no source OHLC-profile VA outcome is built. family_open’s half-range/half-body weighting and heavier-neighbour VA are different. The standalone r_p17_bar_vol only demonstrates allocation arithmetic and is not wired to a complete profile. July10 actually touches29937.75 around09:50; October8 RTH stays above25059.75. Actual trade VP is plotted solely as available diagnostic.

**Source references:** [PINE Sessions & VP with prev session VP & daily weekly opens.txt L216](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Sessions & VP with prev session VP & daily weekly opens.txt:216>); [PINE Sessions & VP with prev session VP & daily weekly opens.txt L252](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Sessions & VP with prev session VP & daily weekly opens.txt:252>); [PINE Sessions & VP with prev session VP & daily weekly opens.txt L641](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Sessions & VP with prev session VP & daily weekly opens.txt:641>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [family_open.py::ohlc_vp](</workspace/implementation/src/trading_research/research/phase1_live/family_open.py:72>), [family_open.py::value_area](</workspace/implementation/src/trading_research/research/phase1_live/family_open.py:39>), [formulas_flow.py::r_p17_bar_vol](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1406>), [recipe_score.py::_preds.p17](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:787>), [FORMULAS.md::R-P17](</workspace/planning/phase-1-live/FORMULAS.md:659>).

**Build steps:**

1. Stop the combined faithful profile row until literal source versus a corrected prior-RTH transplant is chosen explicitly. Record30 equal rows, source profile clock, prior/developing scope, and70% target. Do not relabel an available trade VP as the Pine OHLC profile or build a missing input in this audit.
2. For each candle compute body=|C−O|, top=H−max(O,C), bottom=min(O,C)−L, den=body+2top+2bottom. Assign V*body/den to body, V*2top/den to top wick and V*2bottom/den to bottom wick; integrate proportional overlap across each price row. Body goes to candle-colour side, each wick half/half. Handle zero-range bars explicitly and conserve total volume.
3. POC is the max-volume row midpoint with source descending-price tie order. Port literal alternating down/up VA and record its threshold-row/last-row defects; a corrected alternating expansion including the crossing row and a heavier-neighbour variant need different names. Freeze the completed profile only at its end, with history and all row bounds retained.
4. Keep18:00NY daily open and Sunday18:00 weekly open as separate level objects. Record source weekday masks and instrument trading availability. Actual RTH touch must be a per-bar overlap, not just global H/L bracketing across a gap; weekly hold/rejection and VA outcomes need their own entry/confirmation times and scope.

**Acceptance checks:**

- Bar O100/H101/L99/C100.5/V100 yields body14.285714, top28.571429, bottom57.142857; all row allocations sum100. The equal-row source and one-tick variant must not share a POC by assumption.
- July10 open29937.75 is a valid daily-open touch; October8 open25059.75 is overnight-only and not RTH. Two separated bars bracketing it across a data gap do not prove touch.
- Exercise a last-row POC, tied maximum, threshold reached on the first added row, a zero-range bar and a Sunday-only weekly open. No current/developing profile may appear as prior value.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P17-A-2026-07-10.png>) | true | yes for18:00-open RTH touch; source profile comparison unavailable | 18:00 open29937.75 is touched around09:50 and repeatedly afterward. Side panel explicitly shows actual completed RTH trade VP as diagnostic; no Pine30-row OHLC profile or source VA geometry exists in this scored flag. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P17-B-2025-10-08.png>) | false | no for18:00-open RTH touch; source profile comparison unavailable | 18:00 open25059.75 trades overnight but RTH stays above it. Current trade VP is shown as available diagnostic, not source OHLC profile. |

### R-P18 — Keep distinct OHLC volume proxies blocked as trading triggers

The simple MVFL sub-bar proxy assigns+V/−V/0 by close versus open. Confluence Suite instead assigns whole volume using close position, then candle direction, then prior close and persistent prior sign. Neither is executed aggressor delta. FORMULAS describes a named simple-sign series and explicitly blocks it as a trigger; that gate is appropriate.

The current recipe calls r_p18_ohlc_cvd for the simple-sign series and scans a grid-divergence proxy, but the scorer remains blocked. Another producer, family_flow._ohlc_cvd, allocates volume fractionally by close position and is neither the simple sign nor the literal Confluence method. Both plotted sessions show the actual simple-sign ETH cumulative series and reference prices; there is no permissible positive/negative trade trigger to certify.

**Source references:** [PINE Confluence Suite.txt L107](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/Confluence Suite.txt:107>); [PINE momentum-volume-flow-levels.txt L80](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:80>).

**Code to change:** [formulas_flow.py::r_p18_ohlc_cvd](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:176>), [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [family_flow.py::_ohlc_cvd](</workspace/implementation/src/trading_research/research/phase1_live/family_flow.py:21>), [recipe_score.py::_preds.p18](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:790>), [FORMULAS.md::R-P18](</workspace/planning/phase-1-live/FORMULAS.md:668>).

**Build steps:**

1. Preserve blocked status in reports, joins and downstream signal selection. A computable price/volume series is not proof that the trade-CVD trust gate has passed; no automatic substitution with an available proxy is allowed.
2. Assign separate object/version names to simple sign(C−O)*V, fractional close-position allocation and the Confluence whole-volume tie/persistence algorithm. Keep their outputs, tests and labels separate. Do not describe any of them as buyer/seller aggressor volume.
3. For the simple variant retain zero on doji, reset at the stated18:00 session boundary and accumulate only complete observed bars. Store missing-bar coverage and known_at; a missing start or gap cannot silently yield a complete trusted session.
4. If a later authorized task studies proxy divergence, use chronological confirmed pivots and the explicit location/entry sequence, label the result as a price-volume proxy study, and maintain blocked source-trigger status until the required trust decision is recorded. Preserve the actual series plots as diagnostics.

**Acceptance checks:**

- 100/100.5/V120 then100.5/100.25/V80 then100.25/100.25/V50 yields+40 in the simple-sign variant. A doji near its high can differ in the other variants.
- July10 andJanuary28 curves remain unscored diagnostics even when their slope appears to agree with the price move.
- A consumer requesting a faithful CVD trigger must receive blocked with reason, not false and not the fractional/simple proxy under a trade-delta name.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P18-A-2026-07-10.png>) | unscored on this date | blocked | Actual sign(C−O)*V cumulative curve resets prior18:00; sharp AM sign swings accompany the10:30 drop and recovery. Price reference H29887.75/EQ29829.5/L29771.25 is shown. This cannot establish executed delta or a trade trigger. |
| [B / 2026-01-28](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P18-B-2026-01-28.png>) | unscored on this date | blocked | OHLC-sign cumulative volume rises near10000 overnight then falls below−15000 by noon while price breaks6–9L26255.25. Directional visual agreement does not certify aggression; scorer remains blocked. |

### R-P19 — Every adjacent body gap, later near-edge fill and80/20 confluence

The source detects adjacent BODY gaps at least4ticks wide, evaluates old gaps before creating new ones, and marks a later near-edge fill. It also defines price-ending20/80 references,8tick confluence and zero-wick repairs. This is distinct from three-candle wick FVG and from AMT’s80% value-area traverse.

The helper only examines array positions0 and1, and the producer supplies09:30–12:00 but never loops later pairs or passes fill data. Thus25/647 is the first09:30/31 body-gap presence rate. August6 down gap29327–29328.5 forms by09:32 and actually fills on09:34; July10 first pair has no gap, which says nothing about later pairs. Down-gap confluence is hardcoded false. Later-pair inspection of July10 finds an up gap29881.25–29882.25 formed09:32 (known09:33), so the retained daily false is a counterexample. September29,2025 has no qualifying gap in any of389 adjacent RTH pairs; the642-session scan found49 such all-RTH negative dates.

**Source references:** [PINE 8020 System.txt L50](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:50>); [PINE 8020 System.txt L120](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:120>); [PINE 8020 System.txt L251](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:251>); [PINE 8020 System.txt L309](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/8020 System.txt:309>).

**Code to change:** [family_recipes.py::build_recipe_table](</workspace/implementation/src/trading_research/research/phase1_live/family_recipes.py:92>), [formulas_flow.py::r_p19_body_gap](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1434>), [recipe_score.py::_preds.p19](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:793>).

**Build steps:**

1. Process every consecutive complete candle pair on the explicitly selected timeframe/window. Up gap if current body bottom−prior body top>=4ticks, bounds[priorTop,currentBottom]; down gap if priorBottom−currentTop>=4ticks, bounds[currentTop,priorBottom]. Require adjacency in time, not merely adjacent rows across missing bars.
2. Create each gap at current candle completion with direction and bounds. Evaluate previously created gaps before current creation, matching the source. Later low<=upper bound fills an up gap; later high>=lower bound fills a down gap. Store first near-edge fill, optional named mid/far fills and censoring at the selected horizon.
3. Generate the source grid100*k+20 and100*k+80 for integer k, and compute minimum distance from either gap edge to the grid on BOTH directions. Confluence is<=8ticks; do not substitute a40point band or confluence with an unrelated FVG.
4. Retain zero-wick repair markers as separate source objects with their producing candle/completion and later tap outcomes. Report per-gap presence, fill rate conditional on created gap, time-to-fill and confluence strata; the existing first-pair session count needs a distinct legacy name.

**Acceptance checks:**

- August6 down gap29327–29328.5 is known09:32 and09:34 high fills its near edge29327. The creation candle cannot fill a newly made gap.
- July10 first-pair absence is a valid pair-level negative; all later pairs must still be scanned. A gap at index20 must not disappear because the first pair overlaps.
- A4tick gap qualifies, a3tick gap does not. An up/down edge exactly8ticks from a20/80 level has the same confluence result. Gaps across missing minute rows are unknown.
- July10,2026 must discover the later09:31/09:32 up body gap29881.25–29882.25, known09:33, even though09:30/31 overlaps. September29,2025 is an all-RTH negative:389 adjacent complete pairs and no4tick gap.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-08-06](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P19-A-2026-08-06.png>) | true | yes for first two-body gap and later near-edge fill | 09:30/31 bodies leave down gap29327–29328.5, known09:32. Price moves lower, then09:34 rebound spans the near edge29327 and full band. Producer reports only first-pair gap presence, not the observed later fill. |
| [B / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P19-B-2026-07-10.png>) | false | no at the first pair; yes at later RTH pairs | July10 first09:30/31pair overlaps and the producer returns false. The complete adjacent-pair scan finds an UP gap29881.25–29882.25 in09:31/32, known09:33, then further gaps including09:40down29863.75–29864.75. Thus first-pair false is not an all-session negative. The plot shows only the actual first-pair construction; the later-pair evidence is saved in additional_sequence_candidates.json. |
| [event-negative / 2025-09-29](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P19-event-negative-2025-09-29.png>) | false | no body-gap event anywhere in complete RTH | September29,2025 has390complete minute bars and389adjacent pairs with zero4tick body gaps, corroborated by the full-session scan. Opening detail shows overlapping bodies; no gap zone is invented on either panel. All-RTH absence is stronger than the original first-pair negative; retained scorer=false. |

### R-P20 — MVFL source delta clusters, anomaly zones and seven-vote state

MVFL source is a seven-vote hysteresis indicator using OHLC-signed sub-bar volume. RULES explicitly asks for an aggressor-delta rebuild, while FORMULAS presents the literal OHLC version; that conflict stops faithful certification. FORMULAS also clusters at close, but source bullish events use body bottom and bearish body top, weighted by absolute delta. The historical assistant upgrade proposal is not source-author proof of equivalence.

The actual scorer is AM max print>=100lots AND AM price range>=8ticks:425/647. It never calls r_p20_mvfl and builds none of the source zones or seven votes. July10 max245lots/range1266ticks passes; October8 max92/range748 fails. The unused helper doubles anomaly thickness (±0.2% instead of±0.1%), and its passing fixture expects that wrong width.

**Source references:** [PINE momentum-volume-flow-levels.txt L5](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:5>); [PINE momentum-volume-flow-levels.txt L79](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:79>); [PINE momentum-volume-flow-levels.txt L113](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:113>); [PINE momentum-volume-flow-levels.txt L171](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:171>); [PINE momentum-volume-flow-levels.txt L414](</workspace/implementation/reports/phase1-live/chart-audit/source-pine/momentum-volume-flow-levels.txt:414>).

**Code to change:** [family_tape.py::_score_one](</workspace/implementation/src/trading_research/research/phase1_live/family_tape.py:357>), [formulas_flow.py::r_p20_mvfl](</workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py:1458>), [recipe_score.py::_preds.p20](</workspace/implementation/src/trading_research/research/phase1_live/recipe_score.py:742>), [FORMULAS.md::R-P20](</workspace/planning/phase-1-live/FORMULAS.md:686>), [RULES.md::R-P20](</workspace/planning/phase-1-live/RULES.md:26>).

**Build steps:**

1. Stop the faithful MVFL row and preserve the unresolved source-versus-aggressor upgrade decision. Name the literal OHLC variant, any later trusted aggressor variant and the unrelated print/range filter separately. Do not implement missing clusters or claim the upgrade already exists in this audit.
2. For a later explicitly chosen literal port use complete5m bars with1m signed sub-bars, default detection02–16NY. Δ=sum(sign(C−O)*V), signal iff abs(Δ)>max(6*SMA50(absΔ),3000), with source SMA including current completed bar. Keep significant-event pools per side across days, capped3000 detections each; source no-daily-reset must be explicit.
3. Store bullish event price=min(O,C), bearish=max(O,C), weight=absΔ. Port source weighted one-dimensional k-means k4,12iterations and exact initialization/empty-cluster handling. Visible clusters require weight>=45% of the strongest across both sides; bounds are centre±max(span/2,0.4*ATR14/2). A backdrawn earliest-cluster timestamp is visual history, not causal availability.
4. For volume anomalies require volume>2.5*SMA20(volume), source includes current bar. Zone is close±0.001*close, full0.2% thickness. Merge centres within0.5% by retaining larger-volume event, maximum50. Keep centre, chosen event volume, created/updated times and every retired version.
5. Implement each vote distinctly: HTF close/SMA200; persistent last significant delta sign; source median27 smoothedSMA3 versusSMA50; delta-zone edge break/rejection; previous MTF regime; SMA5 versusSMA200; anomaly-zone break/rejection. For edge rejection include prior wick conditions; loop-order source last eligible edge is not necessarily the latest event.
6. Preserve initial bearish bias and flip only at least4of7 votes for the other side, otherwise persist. Store all votes and their input availability at each close. Evaluate any added hold/reject or next-bar direction outcome only afterward under its own label. Fix the anomaly fixture to source width and require a producer integration test; unused helper passes cannot certify the scored MVFL family.

**Acceptance checks:**

- At close16640 the source anomaly zone is[16623.36,16656.64], not[16606.72,16673.28]. Δ4100 with SMA550 passes3300; exact threshold equality does not.
- July10’s245lot print andOctober8’s92lot maximum cannot by themselves imply any MVFL signal or no-signal. A cluster born after10:00 cannot become a causal09:00 feature because its box is drawn backward.
- A bullish event with O100/C110 clusters at100, not110; bearish O110/C100 clusters at110. Three opposing votes preserve bias, four flip; a missing vote is not silently bullish/bearish.

**Dated chart evidence:**

| case / date | retained scorer | source-event assessment | observed chart detail |
|---|---|---|---|
| [A / 2026-07-10](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P20-A-2026-07-10.png>) | true | cannot-tell for MVFL; yes for unrelated print/range filter | Actual AM largest print245lots and range1266ticks pass>=100/>=8 rule. Tape dots>=30lots show time/price/sides; no significant OHLC-delta detection, clusters, anomaly bands or7-vote bias exists. |
| [B / 2025-10-08](</workspace/implementation/reports/phase1-live/chart-audit/plots/R-P20-B-2025-10-08.png>) | false | cannot-tell for MVFL; no for unrelated print/range filter | Actual AM largest print92lots despite748tick range;28dots>=30lots shown. No100lot print makes proxy false, but does not establish source MVFL no-signal. |

