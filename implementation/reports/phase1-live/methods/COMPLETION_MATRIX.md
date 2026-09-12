# Phase 1 completion matrix

Status: **complete**. Registered inventory, fixture passes, and source-hole handlers remain separate from obligation resolution.

The JSON companion contains the complete typed schemas, field bindings, fixture check IDs/results, ledger rows, and artifact hashes. This document keeps the review table readable by omitting fixture payloads.

## Inventory and checks

| dimension | status | n | resolved | unreviewed | unavailable | implementation_fail | evidence status counts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| software | resolved | 548 | 548 | 0 | 0 | 0 | {'gaps': 0, 'native_route': 59, 'parent_derived_route': 274, 'reviewed_with_limitations': 116, 'supplied_record_route': 3, 'supplied_source_route': 96} |
| source_ambiguity | reviewed_with_limitations | 166 | 0 | 0 | 0 | 0 | {'gaps': 0, 'native_route': 6, 'parent_derived_route': 50, 'reviewed_with_limitations': 107, 'supplied_record_route': 0, 'supplied_source_route': 3} |
| data | reviewed_with_limitations | 166 | 0 | 0 | 0 | 0 | {'gaps': 0, 'native_route': 6, 'parent_derived_route': 50, 'reviewed_with_limitations': 107, 'supplied_record_route': 0, 'supplied_source_route': 3} |
| source_agreement | reviewed_with_limitations | 166 | 0 | 0 | 0 | 0 | {'gaps': 0, 'native_route': 6, 'parent_derived_route': 50, 'reviewed_with_limitations': 107, 'supplied_record_route': 0, 'supplied_source_route': 3} |
| historical | unavailable | — | — | — | 1 | — | {'unavailable': 1} |

Object obligations: 166; core contracts: 9; methods: 12; method fields: 373.
Registered normal fixtures: 329; normal object fixtures checked: 329; object fixture result rows including C08 mutations: 1316; output schema checks: 329.
Fresh regression audit: pass; probes: 27 / 27 expected.

## Objects

| id | title | legacy | code | manual review | status | fixtures | schema | tests | native/derived | current implementation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| O001 | Evidence and data coverage | partial | pass | resolved | complete | 16 | 4 | 3 | native | Resolve every physical row in the exact half-open window; certify minute coverage by interval membership and trade coverage against independently retained native minute OHLCV. Missing minutes and cross-source volume discrepancies remain explicit unknown coverage. |
| O002 | Touch, reject, hold and break measurements | partial | pass | resolved | complete | 8 | 2 | 3 | native | Measure contact, overlap, strict break side, and sweep depth from native events/bars against an actual parent band; keep literal close return separate from audited source reject/hold labels. |
| O003 | Source clocks and availability | partial | pass | resolved | complete | 8 | 2 | 5 | native | Preserve date-aware ET clocks and exact native precision; source-clock verification requires exact-window source-admitted evidence or an actual frozen catalog fact with immutable citation verification. Plain caller verification and inferred comparison settings remain unknown. |
| O004 | Source execution bars | partial | pass | resolved | complete | 8 | 2 | 4 | native | Construct the exact ET-aligned time bar from all complete finer bars or identified events, retaining native instrument, original member IDs, OHLCV and latest availability. Missing members prevent completeness. Same-price boundary batches have exact OHLC; differing prices without… |
| O005 | Jumbo's 06:00–09:00 range | partial | pass | resolved | complete | 12 | 3 | 2 | native | Freeze the dated 06:00-09:00 ET high, low, width, member identity, availability, and interval coverage from native members. |
| O006 | Other time-based range formations | partial | pass | resolved | complete | 8 | 2 | 2 | native | Build another explicitly clocked native range and expose whether the selected source clock was actually verified. |
| O007 | Range EQ and quadrants | bounded_primitive | pass | resolved | complete | 8 | 2 | 2 | derived | Compute EQ and 25/75 percent quadrants from one selected positive-width parent range, rejecting caller replacement geometry. |
| O008 | Source range-open and range-close references | partial | pass | resolved | complete | 4 | 1 | 1 | derived | Bind range-open and range-close prices to selected parent observations while preserving source anchor identity and directed-path evidence. |
| O009 | Range width and expectations | bounded_primitive | pass | resolved | complete | 4 | 1 | 1 | derived | Measure range width in points, ticks, percent, and prior-width ratio using separately identified denominator parents. |
| O010 | Retrospective range path | partial | pass | resolved | complete | 12 | 3 | 2 | native | Replay a covered post-formation path to identify which side broke first and any later EQ return without turning an unfinished absence into false. |
| O011 | Overnight high, low and width | supplied_scalar_only | pass | resolved | complete | 8 | 2 | 1 | native | Measure overnight high, low, width, exact window identity, member ownership, and availability; enforce Sires 18:00-09:30 ET when selected. |
| O012 | Chronological liquidity purges | partial | pass | resolved | complete | 12 | 3 | 1 | native | Retire a selected liquidity reference only after an ordered qualifying native visit in the declared consumption scope. |
| O013 | Opening location and participation | partial | pass | resolved | complete | 4 | 1 | 1 | derived | Classify the cash open relative to prior value, prior range, and optional current range while excluding participation context unavailable at use time. |
| O014 | Range exhaustion and mean-reversal area | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Project the configured exhaustion ladder from one frozen range and measure observed sweep depth independently of the source-selected reversal band. |
| O015 | The 1.33–1.66 extension area | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Project the 1.33-1.66 extension bands from the same selected parent width and reject width substitution. |
| O016 | Nested source range geometry | partial | pass | resolved | complete | 8 | 2 | 1 | derived | Preserve distinct outer and inner range identities, compute both widths/midpoints, and bind later projection to the selected span. |
| O017 | Session Stat+ envelopes | source_hole_handler_partial | pass | resolved | complete | 4 | 1 | 1 | derived | Carry cited Stat+ average/median/min-average envelopes with complete settings identity; compute only the labeled midpoint. |
| O018 | Jumbo EVRange | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 2 | derived | Carry a versioned, anchored EVRange observation and expose supplied midpoint geometry without auto-deriving unpublished bounds. |
| O019 | Time-anchored P-zones | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 1 | derived | Track an anchored P-zone through dated state and path events, separating active-at-use from the source zone label. |
| O020 | PD RTH Range+ destinations | supplied_scalar_only | pass | resolved | complete | 4 | 1 | 1 | native | Measure the prior RTH range from the exact 09:30-16:00 ET native window and retain destination/context fields as separate source information. |
| O021 | Jumbo reversal and action windows | partial | pass | resolved | complete | 12 | 3 | 2 | derived | Evaluate an actual action timestamp against explicit reversal/action window boundaries and surface boundary ambiguity. |
| O022 | Source session-cleanliness assessment | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 1 | derived | Preserve the source cleanliness label, session identity, reason, and selection time; never invent an automatic cleanliness classifier. |
| O023 | Accumulation, manipulation and distribution phases | source_hole_handler_partial | pass | resolved | complete | 4 | 1 | 1 | derived | Preserve a contemporaneous source phase label and dated transition sequence without automatic phase inference. |
| O024 | Jumbo failure signatures and three attempts | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Count distinct failed attempts at the same level and branch by the decision time and apply the source invalidation/allocation policy separately. |
| O025 | Opening-range midpoint reference | supplied_scalar_only | pass | resolved | complete | 4 | 1 | 1 | native | Measure opening-range high, low, and midpoint from an identified native interval while keeping later midpoint retrace evidence distinct. |
| O026 | Confirmed swing midpoint retrace | bounded_primitive | pass | resolved | complete | 8 | 2 | 1 | derived | Compute a swing midpoint from two confirmed, identified endpoints and record a later midpoint contact without selecting pivots automatically. |
| O027 | Relative-volume context at the open | supplied_scalar_only | pass | resolved | complete | 8 | 2 | 1 | native | Compute current native volume and relative volume against an explicit same-clock arithmetic-mean baseline, retaining sample identities and classification threshold. |
| O028 | Equal-high or equal-low liquidity objective | bounded_primitive | pass | resolved | complete | 8 | 2 | 2 | derived | Create an equal-high/low objective from at least two dated contributor parents and an explicit equality/band policy; track remaining status at selection. |
| O029 | Scheduled news and changing information | supplied_scalar_only | pass | resolved | complete | 4 | 1 | 1 | derived | Separate schedule publication, actual release, vintage, source response, and thesis revision by their real availability times. |
| O030 | Session VWAP | bounded_primitive | pass | resolved | complete | 24 | 6 | 1 | native | Compute price-volume and squared-price-volume sums from actual resolved trades or complete contiguous bars; clip snapshots, retain unknown-side execution volume, and require an exact reset-to-cutoff membership interval. |
| O031 | Anchored VWAP | partial | pass | resolved | complete | 8 | 2 | 1 | native | Derive an anchored VWAP from the selected real anchor parent and every eligible execution/bar; anchor availability and snapshot cutoff both constrain use. |
| O032 | VWAP deviation bands | bounded_primitive | pass | resolved | complete | 16 | 4 | 1 | derived | Derive weighted population dispersion from the identical VWAP parent membership; preserve reset, snapshot and band identity and reject mixed or contact-inclusive snapshots. |
| O033 | Source gamma regime | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | — | Preserve the observed source gamma regime, native 0DTE product identity, eligible rereads and source-scoped branch permission; later rereads contribute availability. |
| O034 | Native options-chain identity | partial | pass | resolved | complete | 8 | 2 | 1 | — | Build a full dated option identity from product, class, expiry, strike, right and OSI key; calculate 0DTE from observation date and retain only a contemporaneous explicit mapping. |
| O035 | Gamma-flip reference | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | — | Retain attributed flip level, units and regime interpretation and compute spot relation using both observation clocks. |
| O036 | Gamma call and put walls | source_hole_handler | pass | resolved | complete | 4 | 1 | 1 | — | Preserve every wall identity, dated price/band, units and selected wall; compute same-unit spot relations and prevent max-pain identity aliasing. |
| O037 | Source max-pain reference | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | — | Retain max-pain identity separately from same-price walls and calculate only the stated difference. |
| O038 | Source Vol Trigger readout | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | — | Retain the attributed source readout, units, interpretation and availability without replacing it with a differently computed quantity. |
| O039 | Source VOL-GEX readout | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | — | Keep the source Vol/GEX value and its units distinct from the labeled arithmetic comparison. |
| O040 | Source hedging-pressure gauge | source_hole_handler | pass | resolved | complete | 4 | 1 | 1 | — | Preserve gauge scale and units; percentage conversion is available only for an actual percent scale, with no fabricated entry permission. |
| O041 | Source KG1 level | partial | pass | resolved | complete | 8 | 2 | 1 | — | Preserve the KG1 band and identity and require actual independent prior-reaction and minor-HVN records; same-price and KG1 labels do not count as two reasons. |
| O042 | VIX and volatility context | partial | pass | resolved | complete | 8 | 2 | 1 | — | Select the latest available VIX observation at decision time with unit and vintage tie checks; later observations cannot modify an earlier snapshot. |
| O043 | Volatility-implied daily-move estimate | bounded_primitive | pass | resolved | complete | 4 | 1 | 1 | — | Calculate VIX daily percentage, fraction and optional points with the factor of 100 and explicit conversion instrument; propagate both input clocks. |
| O044 | Volatility term structure and event change | partial | pass | resolved | complete | 8 | 2 | 1 | — | Retain the exact selected tenor pair, comparable units and chosen difference/ratio; include an event change only after its actual publication. |
| O045 | VVIX context | partial | pass | resolved | complete | 8 | 2 | 1 | — | Select the actual available VVIX vintage and retain context and interpretation with no backward use of later releases. |
| O046 | Green Bird's finished session references | partial | pass | resolved | complete | 12 | 3 | 1 | native | Build a finished local/session box from complete contiguous members, with identified boundaries, measurable width, explicit clock verification, and coverage state. |
| O047 | Sweep, failure and reclaim | partial | pass | resolved | complete | 16 | 4 | 3 | native | Measure a strict sweep and completed failure/reclaim close against an actual reference parent, using only raw or O004 confirmation bars and audited source policy. |
| O048 | Prior day, week and month extremes | supplied_scalar_only | pass | resolved | complete | 8 | 2 | 1 | native | Measure prior-period high/low from native members and preserve period identity, scope, end, active state, and retirement policy. |
| O049 | Green Bird's midnight true-day open | bounded_primitive | pass | resolved | complete | 12 | 3 | 2 | native | Resolve the midnight true-day-open from the first causally ordered execution and evaluate any required close-through only from an actual complete five-minute bar. |
| O050 | 09:30 cash-open price | partial | pass | resolved | complete | 4 | 1 | 3 | native | Resolve the 09:30 cash open and replay the native path through the snapshot to locate below/above crossings and strict reclaim. |
| O051 | New-week opening gap | bounded_primitive | pass | resolved | complete | 12 | 3 | 1 | derived | Construct a new-week gap from separate Friday-close and Sunday-open parents and distinguish contact from full fill. |
| O052 | Measured 50–61.8% retracement | bounded_primitive | pass | resolved | complete | 8 | 2 | 1 | derived | Project the directional 50-61.8 percent retracement band from one measured impulse with preserved failure linkage. |
| O053 | Premium / discount within a selected range | bounded_primitive | pass | resolved | complete | 4 | 1 | 1 | derived | Compute midpoint, normalized location, premium/discount, and optional value relation from selected range, price, and value parents. |
| O054 | Market-structure shift after failure | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | derived | Validate the ordered failure, confirmed swing, structural break, and entry sequence while preserving source break convention and episode identity. |
| O055 | Fair-value gaps and higher-timeframe imbalances | partial | pass | resolved | complete | 4 | 1 | 1 | derived | Preserve an identified three-candle imbalance/FVG, active-state history, direction, and actual defining candle parent IDs; measure contact/fill separately. |
| O056 | Jumbo orderblocks | partial | pass | resolved | complete | 8 | 2 | 3 | native/derived | Detect bullish or bearish three-candle orderblock confirmation from three distinct complete chronological candles and preserve the audited entry/stop policy. |
| O057 | Jumbo rejection blocks | bounded_primitive | pass | resolved | complete | 4 | 1 | 1 | native/derived | Measure body and rejection wick geometry from one actual complete candle while keeping rejection, location, entry, and stop permissions source-bound. |
| O058 | Jumbo Absorption Zone+ candle | partial | pass | resolved | complete | 4 | 1 | 2 | native/derived | Measure body and volume ratios from one current complete candle plus exactly fourteen causal same-timeframe bars under explicit averaging/reset/equality policies. |
| O059 | Source setup quality and exposure | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | derived | Preserve the source setup grade and selected exposure while separating necessary conditions from unpublished sufficient A+ criteria. |
| O060 | Auction balance | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 1 | derived | Represent an identified accepted auction balance, its width, migration state, scale, profile identity, and point-in-band relation without automatic balance discovery. |
| O061 | Volume profile | partial | pass | resolved | complete | 8 | 2 | 3 | native | Build an immutable volume-by-price profile from canonical native executions, preserving B/A/N ownership, binning, coverage, event IDs, and instrument definition. |
| O062 | Profile value area | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Expose VAL/VAH, target fraction, volume inside, achieved fraction, and exact value-area algorithm/tie configuration from a selected profile snapshot. |
| O063 | Developing profile snapshot | partial | pass | resolved | complete | 4 | 1 | 2 | native | Freeze an immutable developing-RTH profile snapshot at as-of so later events cannot revise the earlier snapshot. |
| O064 | Profile point of control | bounded_primitive | pass | resolved | complete | 8 | 2 | 2 | derived | Return all maximum-volume POC candidates and select a POC only under an explicit tie policy. |
| O065 | Untested prior POC | partial | pass | resolved | complete | 12 | 3 | 3 | native | Evaluate whether an identified prior POC remained untested through a fully covered decision interval using actual post-formation visits. |
| O066 | High-volume node | source_hole_handler_partial | pass | resolved | complete | 4 | 1 | 1 | derived | Measure volume in a source-selected HVN band from the actual profile while leaving automatic node selection unavailable. |
| O067 | Low-volume node | source_hole_handler_partial | pass | resolved | complete | 4 | 1 | 1 | derived | Measure volume in a source-selected bridge/LVN band and preserve the identities of the two accepted areas and their transition evidence. |
| O068 | Profile shelf | source_hole_handler_partial | pass | resolved | complete | 4 | 1 | 1 | derived | Measure source-selected shelf and transition-band volume with shelf/edge identity and no automatic shelf discovery. |
| O069 | Profile ledge | partial | pass | resolved | complete | 4 | 1 | 3 | derived | Derive ledge and retest arithmetic only from selected parent objects; preserve stable lineage separately from equal price and deny late or unrelated retests. |
| O070 | Composite auction profiles | partial | pass | resolved | complete | 8 | 2 | 3 | derived | Compose explicitly selected compatible profile parents with disjoint native event ownership and reconcile every row and total. |
| O071 | Source-selected dealing range | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 3 | derived | Compute the dealing band and controlling reference from actual selected parents; admit source rationale/thesis fields only through audited selection and leave unavailable source qualifiers unknown. |
| O072 | Prior defended reaction area | partial | pass | resolved | complete | 12 | 3 | 3 | derived | Derive prior/current defense from identified parents with strict lineage and event ordering; equal price cannot transfer history between bands and pre-contact or future control is denied. |
| O073 | Overnight volume structure | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Bind overnight profile structure to the exact Sires O011 window, preserve older-POC identity and optional opening response, and never auto-select an LVN. |
| O074 | Overnight directional inventory | source_hole_handler | pass | resolved | complete | 8 | 2 | 1 | derived | Preserve the source overnight inventory label and measured profile evidence; later opening response cannot rewrite the frozen inventory. |
| O075 | ETH profile identity | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Keep prior-ETH profile identity distinct and evaluate source scope, balance/value bands, and cohort eligibility at the open. |
| O076 | MPOC: the profile midpoint | bounded_primitive | pass | resolved | complete | 4 | 1 | 2 | derived | Compute MPOC strictly as the midpoint of verified profile high/low and compare it separately with volume POC and later contacts. |
| O077 | Signed volume-by-price profile | partial | pass | resolved | complete | 8 | 2 | 2 | native | Expose signed volume by price from canonical B/A/N rows, retaining exact known delta and bounded uncertainty when aggression is unknown. |
| O078 | Time-price-opportunity profile | partial | pass | resolved | complete | 12 | 3 | 3 | native | Construct a dated TPO membership map from a declared trade-visited or complete period-range grid, preserving letter clock and coverage. |
| O079 | TPO single-print structure | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 3 | derived | Find source-selected interior single-print rows and evaluate later repair without treating outer tails as single prints. |
| O080 | TPO excess at auction extremes | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Evaluate side-specific extreme TPO tails for the declared same-letter excess criterion on an explicit price grid. |
| O081 | TPO poor high and poor low | partial | pass | resolved | complete | 12 | 3 | 2 | derived | Evaluate poor-high/poor-low structure only under the instrument-specific adjacent-row criterion and compatible source grid. |
| O082 | Initial balance | partial | pass | resolved | complete | 8 | 2 | 2 | native | Build initial balance only after complete A and B periods and keep later upper/lower extensions separate from IB geometry. |
| O083 | Developing auction open type | partial | pass | resolved | complete | 8 | 2 | 2 | native | Measure the cash-open path through as-of and preserve a source open-type label as provisional unless elapsed coverage and label timing support it. |
| O084 | Developing auction day structure | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 2 | derived | Preserve provisional and final auction day-type observations with taxonomy, author, evidence cutoff, and permission reference. |
| O085 | Profile shape and trade permission | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Preserve a source profile-shape label and permission, sub-balance/LVN identities, and completed break-retest evidence without inferring direction from shape. |
| O086 | Prior-session auction landmarks | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Bind a prior-session landmark by stable identity and compute half-range gap, half-close gap, and opening relation as distinct quantities. |
| O087 | Remaining auction objectives | partial | pass | resolved | complete | 4 | 1 | 2 | native | Freeze objective priority and retirement from actual covered visits under the declared RTH/ETH scope and consumption rule. |
| O088 | Source-conditioned reference statistics | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Keep a literal source claim separate from a comparable observed cohort and report both/either hit counts and rates without relabeling them as trade win rate. |
| O089 | Saint's Asia-range target context | bounded_primitive | pass | resolved | complete | 4 | 1 | 2 | derived | Measure entry-stop-target distances for the cited Asia-range case while preserving the source range reference and leaving automatic target construction unavailable. |
| O090 | Rotation within accepted balance | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Validate ordered edge arrival and local confirmation inside an actual balance; keep later far-side outcome separate from the rotation setup. |
| O091 | Accepted break and defended boundary retest | partial | pass | resolved | complete | 12 | 3 | 2 | derived | Require break, acceptance, departure, same-boundary retest, defense, and initiative in order, with source-held retest and stable boundary identity. |
| O092 | Re-acceptance into value | partial | pass | resolved | complete | 16 | 4 | 2 | derived | Require a return from outside and two consecutive complete whole-range-inside half-hours before certifying value re-acceptance. |
| O093 | Sires's narrower Failed Auction setup | partial | pass | resolved | complete | 12 | 3 | 2 | derived | Keep established and older profiles distinct, then validate the Sires break, older-POC tag, rejection, and source target sequence. |
| O094 | Saint's failed auction and return to value | bounded_primitive | pass | resolved | complete | 8 | 2 | 2 | derived | Keep original and tested value identities distinct and validate Saint exploration, failure, return, re-acceptance, and control in order. |
| O095 | POC failure versus efficient passage | bounded_primitive | pass | resolved | complete | 8 | 2 | 2 | derived | Count distinct failed POC tests through as-of, preserve efficient-passage interpretation, and admit a held retest only when available. |
| O096 | Whole-balance traversal with one side in control | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Validate a complete entry-to-exit traversal of one identified balance and causal one-side control, without imposing an unsupported 30-minute cap. |
| O097 | Higher- and lower-timeframe control alignment | partial | pass | resolved | complete | 16 | 4 | 3 | derived | Require a live higher-timeframe thesis and current lower-timeframe control on the same area; preserve both availability clocks and reject free two-sided chop. |
| O098 | Executed aggressor-side trades | partial | pass | resolved | complete | 12 | 3 | 2 | native | Preserve each executed print, B/A/N aggressor volume, exact delta bounds, and timestamp-order quality without treating quotes as trades. |
| O099 | Big Trades aggression markers | partial | pass | resolved | complete | 8 | 2 | 4 | derived | Apply the declared big-trade threshold, comparator, and per-print or cluster aggregation without merging the two marker semantics. |
| O100 | DOM at a planned location | partial | pass | resolved | complete | 8 | 2 | 4 | derived | Measure local BBO display and executions while leaving hidden reserve and source defense interpretation unknown unless observed. |
| O101 | Absorption: effort without price reward | supplied_scalar_only | pass | resolved | complete | 4 | 1 | 4 | derived | Keep aggressive effort, price response, passive defense, and source absorption as separate evidence; later decline cannot repair missing passive proof. |
| O102 | Executed passive replenishment | partial | pass | resolved | complete | 8 | 2 | 6 | derived | Reconcile consumption and subsequent same-price refresh; zero or unordered activity cannot verify replenishment. |
| O103 | Iceberg evidence and added participation | source_hole_handler_partial | pass | resolved | complete | 4 | 1 | 5 | derived | Compare executed and displayed quantities within the declared area while refusing to infer participant identity or hidden reserve from BBO alone. |
| O104 | Price reward near the absorption origin | partial | pass | resolved | complete | 12 | 3 | 4 | derived | Measure directional reward from the selected origin edge and keep reward, return, and renewed defense as distinct dated events. |
| O105 | Cumulative volume delta and its source reference | partial | pass | resolved | complete | 12 | 3 | 3 | native | Reset CVD at the declared clock, filter by as-of, preserve unknown aggressor volume as an interval, and require a same-unit reference. |
| O106 | Candle direction versus executed delta | partial | pass | resolved | complete | 8 | 2 | 4 | derived | Compare candle direction with exact same-candle execution delta and reject execution membership from another candle. |
| O107 | Local delta concentration at an extreme | partial | pass | resolved | complete | 4 | 1 | 4 | derived | Compute delta concentration over total volume and retain an interval when aggressor side is unknown; source spike classification remains supplied. |
| O108 | POC relocation within a candle | partial | pass | resolved | complete | 12 | 3 | 5 | derived | Compare at least two visible POC snapshots sharing one candle identity and reject cross-candle rewrites. |
| O109 | Diagonal footprint imbalance stacks | partial | pass | resolved | complete | 12 | 3 | 4 | derived | Evaluate diagonal buy and sell imbalance runs with explicit tick adjacency, threshold, run length, and zero-denominator policy. |
| O110 | Same-price 350% imbalance display | partial | pass | resolved | complete | 8 | 2 | 4 | derived | Disambiguate 350-percent-of from 350-percent-more and require an explicit zero-denominator rule. |
| O111 | Speed of tape | supplied_scalar_only | pass | resolved | complete | 4 | 1 | 2 | native | Measure print and contract speed over an exact half-open tape window while keeping any vendor panel value and classifier separate. |
| O112 | Bid-ask spread | bounded_primitive | pass | resolved | complete | 12 | 3 | 2 | native | Compute BBO spread in points and instrument ticks, retaining locked/crossed/stale state and rejecting crossed quotes. |
| O113 | How price arrives at the area | partial | pass | resolved | complete | 4 | 1 | 4 | native | Measure pre-touch path, duration, net/path speed, and aggressive volumes; exclude post-touch events and keep arrival interpretation supplied. |
| O114 | Aggressor print-size thinning | partial | pass | resolved | complete | 8 | 2 | 3 | derived | Record execution-size digit groups and decline pattern while requiring the source grouping threshold before classification. |
| O115 | Absorber becomes aggressive and price lifts off | partial | pass | resolved | complete | 8 | 2 | 5 | derived | Require ordered defense, replenishment, exhaustion, and liftoff stages, then measure directional reward and entry geometry. |
| O116 | Zone formed by aggressive prints | bounded_primitive | pass | resolved | complete | 8 | 2 | 4 | derived | Freeze the source-defined zone, formation identities, departure, and distinct return touch without letting later highs redefine it. |
| O117 | Memory of earlier zone tests | bounded_primitive | pass | resolved | complete | 4 | 1 | 4 | derived | Count only prior resolved touches known by the feature clock and keep current touch and unresolved history outside causal memory. |
| O118 | Origin-of-the-Move catalyst | partial | pass | resolved | complete | 4 | 1 | 4 | derived | Link a catalyst origin to ordered release, failure, refill, drive, retest, and reward stages without replacing the origin later. |
| O119 | Trapped aggression at an auction extreme | partial | pass | resolved | complete | 12 | 3 | 3 | derived | Require two distinct prior failed pushes known before the current test and keep current body-selling evidence separate. |
| O120 | Native candle footprint | partial | pass | resolved | complete | 4 | 1 | 4 | native | Build a complete tick-row footprint from same-candle executions, preserving unknown volume, POC ties, body/wick delta, as-of, and display settings. |
| O121 | At-level DOM rejection | partial | pass | resolved | complete | 12 | 3 | 2 | derived | Require ordered aggression, rejection, and optional added participation with separate DOM and absorption checks. |
| O122 | Four-check absorption reversal | partial | pass | resolved | complete | 12 | 3 | 2 | derived | Require the strict absorption-reward-return-renewed-defense sequence and independent CVD/delta filters. |
| O123 | Defense, replenishment, exhaustion and lift-off | partial | pass | resolved | complete | 12 | 3 | 3 | derived | Enforce the STOP branch two-to-four tick reward, zero-to-two tick entry distance, ordered flow stages, and pre-entry daily-risk gate. |
| O124 | Footprint-confirmed reaction | partial | pass | resolved | complete | 12 | 3 | 2 | derived | Require delta disagreement, POC flip, absorption, and flow confirmation from one candle with ordered snapshot clocks. |
| O125 | Confirmed VWAP deviation fade | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Freeze the selected VWAP deviation band and pre-existing objective; later VWAP cannot rewrite the target. |
| O126 | Aggressive Origin of the Move | partial | pass | resolved | complete | 12 | 3 | 1 | derived | Audit the complete aggressive OFM catalyst-to-reward sequence while preserving the optional CVD filter as unknown when absent. |
| O127 | Passive Origin-of-the-Move variant | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Audit the long-only passive OFM failure, dying tape, buyer area, entry, stop, and one-to-three-R geometry without automatic selection. |
| O128 | Clean squeeze continuation | partial | pass | resolved | complete | 8 | 2 | 3 | derived | Use the first pullback and a complete prior-failure history; later failure is an outcome and cannot alter admission. |
| O129 | Failure of aggression in long-gamma balance | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Audit long-gamma balance-extreme failure, departure, same-area retest, and prior opposite-control target without inheriting another branch gate. |
| O130 | Fresh defense of a continuation band | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Require prior control plus fresh defense at the same band, executed aggression, refresh, and a live matching thesis. |
| O131 | Price-defined microbalance continuation | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Freeze a positive-width microbalance, adverse-side stop, pre-existing target, and dated breakout in thesis direction. |
| O132 | KG1 retest and subsequent trailing | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Keep KG1 known before retest/confirmation, preserve original risk, and apply later management changes only after entry. |
| O133 | Deliberate pre-confirmation attempts | source_hole_handler_partial | pass | resolved | complete | 4 | 1 | 2 | derived | Retain deliberate pre-confirmation attempts in the cohort, with predefined small risk and no thesis death inferred from loss alone. |
| O134 | Third support test without new buyer defense | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Count distinct return/departure episodes at one support band, preserve third-touch losses in cohort, and leave entry selection unautomated. |
| O135 | Late small resistance-fade case | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 2 | derived | Require resistance marked before entry, an upward approach, source exhaustion, short side, and explicit small risk; selector remains unknown. |
| O136 | Green Bird's directional read | source_hole_handler | pass | resolved | complete | 8 | 2 | 3 | derived | Bind directional bias to a dated support/origin identity and candidate side; later events cannot explain an earlier bias. |
| O137 | Declared model and review version | bounded_primitive | pass | resolved | complete | 8 | 2 | 1 | — | Hash and freeze the process definition, observation inventory, version, and revision lineage before use. |
| O138 | Thesis, validity band and death condition | partial | pass | resolved | complete | 8 | 2 | 3 | derived | Maintain the thesis condition ledger, record first death once, and prohibit silent revival without a replacement identity. |
| O139 | Entry-side structural invalidation | bounded_primitive | pass | resolved | complete | 12 | 3 | 2 | derived | Bind the planned stop to the actual selected invalidation reference, side, method, clock, tick size, and adverse-side price comparison. |
| O140 | Exposure fitted to source risk constraints | partial | pass | resolved | complete | 4 | 1 | 1 | derived | Calculate unit, position, and aggregate monetary risk with quantity policy and account cap in compatible units. |
| O141 | Objective selected before entry | partial | pass | resolved | complete | 4 | 1 | 1 | derived | Select one dated active objective before entry and keep later outcome separate from objective selection. |
| O142 | Source-selected position management | partial | pass | resolved | complete | 4 | 1 | 2 | derived | Apply only ordered executed management actions to position, stop, and target ledgers while preserving initial risk. |
| O143 | Confirmed protected high or low | supplied_scalar_only | pass | resolved | complete | 8 | 2 | 1 | derived | Trail only after the protected price and required confirmation are known, with side-specific protection. |
| O144 | Freshly qualified re-entry | partial | pass | resolved | complete | 12 | 3 | 3 | derived | Allow re-entry only after the linked parent exit, in the same live thesis band, with fresh confirmation and a full branch verdict. |
| O145 | Source account and session stop | partial | pass | resolved | complete | 8 | 2 | 4 | — | Compute daily R strictly from same-source/account/session prior results and enforce the fixed pre-entry policy limit. |
| O146 | Thesis and execution journal | bounded_primitive | pass | resolved | complete | 8 | 2 | 2 | — | Reconcile every eligible candidate to a uniform journal row and separate pre-entry inputs from post-trade outcomes and reviews. |
| O147 | Triad AMT-object first use: IØD and RFZ | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Record native AMT objects and first-use times for ES/NQ/YM while preserving the documented IOD and RFZ revisions. |
| O148 | Frozen observation cohort | bounded_primitive | pass | resolved | complete | 8 | 2 | 2 | derived | Hash the fixed eligible cohort, account for selected/order/fill identities, and preserve uniform inclusion and split direction. |
| O149 | Supplied refill-touch grade | source_hole_handler_partial | pass | resolved | complete | 12 | 3 | 2 | derived | Apply a pre-known supplied grading rule to causal features while excluding post-touch labels and leaving automatic grading unknown. |
| O150 | Observed order lifecycle | partial | pass | resolved | complete | 4 | 1 | 3 | derived | Reconcile the full order and position state machine across placement, amendment, fills, cancel/expiry/reopen, brackets, exits, and source policy. |
| O151 | Refill-study fill assumption | partial | pass | resolved | complete | 8 | 2 | 2 | derived | Separate modeled touch-fill eligibility from actual fill reports and leave queue priority unverified without order-level evidence. |
| O152 | Trading and account costs | bounded_primitive | pass | resolved | complete | 8 | 2 | 1 | derived | Reconcile trade costs and stop slippage against the fixed R denominator while keeping account fees separate. |
| O153 | Outcome distribution of a declared process | partial | pass | resolved | complete | 8 | 2 | 1 | — | Preserve all eight outcome categories, explicit closed denominator, process/version/cohort identity, original-R provenance and causal corrections; check literal supplied metric consistency. |
| O154 | Prior loss-streak validation for Stoic's overlay | partial | pass | resolved | complete | 12 | 3 | 1 | — | Validate an actual distinct same-process closed sample of at least 100, reconcile its win rate, and require a matched supplied MC design/result available strictly before the risk decision. |
| O155 | Stoic's printed asymmetric risk ladder | source_hole_handler_partial | pass | resolved | complete | 12 | 3 | 2 | derived | Apply the documented STOIC stage ladder to fixed baseline equity/R units and dated prior results without retroactive activation. |
| O156 | Refill-study evaluation-risk scenarios | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 2 | derived | Preserve the supplied refill scenario assumptions and reported results while exposing missing path rules and causal limits. |
| O157 | Stoic's macro indicator set | partial | pass | resolved | complete | 4 | 1 | 1 | — | Retain explicitly selected leverage/credit/housing/valuation series and causal vintages; preserve a supplied historical verdict without making a current classifier. |
| O158 | Stoic's macro-cycle classification | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 1 | — | Preserve the source cycle label, rationale and actual available input vintages instead of a majority-vote substitute. |
| O159 | Stoic's custom C-score | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 1 | — | Retain an attributed custom C-score, source unit and context and reject substitution of a z-score. |
| O160 | Historical-average and standardized-deviation comparison | bounded_primitive | pass | resolved | complete | 16 | 4 | 1 | — | Compute selected prior-record mean, sample/population scale, raw deviation and standardized deviation with distinct series IDs, causal vintages and a zero-scale case. |
| O161 | Stoic's trend-strength measure | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 1 | — | Retain source strength, horizon and scale separately from an explicitly labeled regression slope. |
| O162 | Economic observation and release vintage | bounded_primitive | pass | resolved | complete | 8 | 2 | 1 | — | Resolve the chosen series/reference-period initial or latest available vintage at the cutoff; preserve release history and reject impossible release ordering or ambiguous ties. |
| O163 | Provide, withdraw and consume events | partial | pass | resolved | complete | 4 | 1 | 2 | native | Replay actual identified order actions for provided/withdrawn/consumed quantity and remaining-state reconciliation. A separate native executed-tape adapter retains B/A/N consumption and two-sided executions, with passive consumption opposite the known aggressor. Add/cancel/full-… |
| O164 | Aggressive effort versus price-response efficiency | partial | pass | resolved | complete | 8 | 2 | 2 | native | Compute directional effort and response from actual selected interval events and instrument-definition tick size; preserve unknown aggressor bounds and resolve endpoint ties only with actual sequence. |
| O165 | B–A–D–E–W auction-state alphabet | source_hole_handler_partial | pass | resolved | complete | 8 | 2 | 2 | derived | Record a dated supplied state only when all required evidence, both sides, depth, and availability checks are complete; no automatic state. |
| O166 | Conditioned next-state transition | partial | pass | resolved | complete | 8 | 2 | 3 | derived | Validate an actual adjacent dated state transition and causal conditioning evidence; aggregate counts alone never certify it. |

## Core contracts

| id | legacy status | executable evidence/status | manual review | status | current implementation |
| --- | --- | --- | --- | --- | --- |
| C00 | partial | C00:pytest:test_all_twelve_method_contracts_have_every_operand_and_alternative:pass, C00:pytest:test_complete_source_fixture_assembles_and_replays_without_using_outcome:pass | resolved | complete | Score each named method and source-selected branch at its decision; process, state, risk and management units remain separate. Synthetic and comparison controls never certify historical faithful execution. |
| C01 | partial | C01:pytest:test_actual_native_result_ignores_supplied_summary_and_retains_members:pass, C01:pytest:test_locator_false_provenance_rejected:pass, C01:pytest:test_missing_schema_and_domain_state_are_implementation_errors:pass, C01:pytest:test_supplied_parent_cannot_launder_unrelate… | resolved | complete | Resolve immutable file hashes, physical row spans, native instrument definitions and exact decimals; retain typed object lineage. Cited qualitative interpretations require actual immutable source bytes and exact field, author, role and observation identity. |
| C02 | partial | C02-F1:pass | resolved | complete | Apply date-aware America/New_York boundaries, half-open intervals, complete finer-bar membership and strict-order uncertainty at timestamp ties. |
| C03 | partial | C03-F1:pass | resolved | complete | Read retained native schemas and all physical rows in each selected instrument window; never use supplied object summaries as native market inputs. |
| C04 | partial | C04-F1:pass | resolved | complete | Propagate latest consumed member, parent and window availability. Reject later observations and source-parent laundering. Preserve false versus unknown and named coverage/source holes. |
| C05 | unbuilt_historical_assembly | C05:pytest:test_relabelled_fixture_cannot_enter_contemporary_cohort:pass, C05:pytest:test_raw_derived_cohort_cannot_be_built_from_supplied_assertions:pass, C05:pytest:test_supplied_attempts_reconcile_without_entering_discovery:pass | resolved | complete | Keep source illustrations, synthetic fixtures, native comparison controls and historical discovery as distinct cohorts; preserve method, branch, instrument and source-version identity. |
| C06 | bounded_helper_with_missing_inputs | C06-F1:pass | resolved | complete | Keep post-decision reference outcomes separate from sequence admission. Freeze target, invalidation and observation coverage and retain unordered or censored results. |
| C07 | partial | C07-F1:pass | resolved | complete | Preserve p/f/u and finite-cohort missingness bounds, year and branch partitions, fixture failures and implementation gaps; source incompleteness remains distinct from software failure. |
| C08 | partial | C08:pytest:test_m05_f3_and_c08_mutations_preserve_false_unknown_and_identity:pass, C08:pytest:test_m11_c08_late_missing_and_identity_mutations:pass, C08:pytest:test_m12_method_c08_mutates_late_missing_and_identity_records:pass | resolved | complete | Execute positive fixtures plus future-dependency, absent-required-observation and foreign-identity mutations. Empty inputs to recipes without legacy required tuples produce a named observation hole. |

## Methods

| id | method | status | fields | objects | field statuses | retained N | retained source holes | retained leakage | retained proxy-as-faithful | original audit finding |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | JJ-TBR | complete | 40 | 62 | {'complete': 40} | 0 | 8 | 0 | 0 | Full source profiles, parent geometry, mirrored OB, 14-bar history and source-selected context/confirmation assembly remain incomplete. |
| M02 | GB-FAIL | complete | 27 | 25 | {'complete': 27} | 0 | 8 | 0 | 0 | Reference/sweep timing and operand construction need completion; November 20 must retain its observed sweep-entry interpretation. |
| M03 | GB-VWAP | complete | 17 | 11 | {'complete': 17} | 0 | 1 | 0 | 0 | Dated Asia/London high roles, source VWAP configuration and later retest/risk evidence are not assembled. |
| M04 | GB-SCALP | complete | 4 | 15 | {'complete': 4} | 0 | 2 | 0 | 0 | Case descriptions exist; a complete automatic admission rule cannot be inferred from the supplied bias/risk fragments. |
| M05 | SIRES | complete | 135 | 117 | {'complete': 135} | 0 | 12 | 0 | 0 | Full profiles, local footprint/DOM sequences, persistent thesis/re-entry and order management have major documented gaps. |
| M06 | SAINT-AMT | complete | 37 | 36 | {'complete': 37} | 0 | 4 | 0 | 0 | Profile routes need native construction, same-band break/retest and HTF/LTF evidence; presence-only profile permission is inadequate. |
| M07 | MEMBER-TWO-REASONS | complete | 18 | 28 | {'complete': 18} | 0 | 2 | 0 | 0 | Two reasons need independent prior reaction/HVN evidence and planned return identity; supplied geometry is insufficient. |
| M08 | KEANI-OPEN-ABOVE-VALUE | complete | 23 | 24 | {'complete': 23} | 0 | 1 | 0 | 0 | Full prior VA, complete A period, developing value and defended imbalance retest are not constructed as one dated sequence. |
| M09 | REFILL-STUDY | complete | 24 | 27 | {'complete': 24} | 0 | 2 | 0 | 0 | Touch/selection checks are useful; native source zone/grading records and correct pending-order/lifecycle behavior remain incomplete. |
| M10 | JETBUNDLE-STATES | complete | 20 | 15 | {'complete': 20} | 0 | 5 | 0 | 0 | Supplied state audits exist; native lifecycle identity and actual adjacent transition evidence remain incomplete. |
| M11 | STOIC-DATA | complete | 13 | 14 | {'complete': 13} | 0 | 2 | 0 | 0 | Process/journal primitives exist, but actual versioned research records and joins are unbuilt; macro remains deferred. |
| M12 | STOIC-RISK | complete | 15 | 8 | {'complete': 15} | 0 | 3 | 0 | 0 | Printed risk arithmetic exists; complete prior validation, stage/reset and account-policy evidence remain incomplete. |

## Method field bindings

| method | field | type | producers | binding | native | source alternative | code | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | at_rth_open | boolean? | O050, O021 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | branch | enum | O005, O006 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | confirm_at | event_key? | O056, O057, O058, O099, O120, O063 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | context_at | event_key? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | context_fixed | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | decision_at | event_key? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | directed_path_recorded | boolean? | O019 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | directional_context | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | edge_swept | boolean? | O047, O014 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | entry_at_eq_or_quadrant | boolean? | O007, O018, O016 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | entry_at_named_internal_or_ev_band | boolean? | O007, O018, O016 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | exit_window_recorded | boolean? | O050, O021 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | expansion_policy | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | extended_context | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | location_touched | boolean? | O002, O014, O007 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | objective_fixed | boolean? | O141, O087, O020, O028 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | objective_is_named_rotation_target | boolean? | O141, O087, O020, O028 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | objective_is_opposing_draw | boolean? | O141, O087, O020, O028 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | objective_is_range_edge | boolean? | O141, O087, O020, O028 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | objective_is_remaining_draw | boolean? | O141, O087, O020, O028 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | objective_is_selected_exhaustion | boolean? | O141, O087, O020, O028 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | prior_expansion | boolean? | O015, O010 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | purge_known_at | event_key? | O012 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | purged_compressed_context | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | range_frozen | boolean? | O005, O006, O007, O008 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | range_known_at | event_key? | O005, O006, O007, O008 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | reaction_side_confirmed | boolean? | O056, O057, O058, O099, O120, O063 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | reduced_expectations | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | reversal_context | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | risk_defined | boolean? | O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | rotation_context | boolean? | O009, O011, O012, O013, O029, O027 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | source_case_verified | boolean? | O003, O006, O022 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | source_clock_verified | boolean? | O003, O006, O022 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | source_confirmation | boolean? | O056, O057, O058, O099, O120, O063 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | source_time_window | boolean? | O050, O021 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | source_zone_known | boolean? | O019 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | sweep_at | event_key? | O047, O014 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | touch_at | event_key? | O002, O014, O007 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | touch_in_source_extension_area | boolean? | O015, O010 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M01 | zone_known_at | event_key? | O019 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | bias_recorded | boolean? | O136 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | box_return_ok | boolean? | O046, O047 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | complete_clock_five_minute_bar | boolean? | O047, O003 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | confirm_at | event_key? | O047, O003 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | confirm_close | decimal_price? | O047, O003 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | confirmation_mode | enum | O047 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | context_at | event_key? | O136 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | decision_at | event_key? | O139, O141, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | impulse_known_at | event_key? | O052 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | objective_fixed | boolean? | O139, O141, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | pocket_required | boolean? | O052 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | reference_frozen | boolean? | O046, O048, O049, O050 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | reference_known_at | event_key? | O046, O048, O049, O050 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | reference_px | decimal_price? | O046, O048, O049, O050 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | retest_at | event_key? | O047, O054, O055 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | retracement_entry | boolean? | O047, O054, O055 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | risk_defined | boolean? | O139, O141, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | side | enum | O047 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | source_hold_confirmed | boolean? | O047, O003 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | source_session_allowed | boolean? | O046, O003 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | source_tdo_close_confirmed | boolean? | O049, O047 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | sweep_at | event_key? | O047 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | sweep_high | decimal_price? | O047 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | sweep_low | decimal_price? | O047 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | tdo_required | boolean? | O049, O047 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | touch_at | event_key? | O052 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M02 | touch_in_measured_pocket | boolean? | O052 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | asia_high | decimal_price? | O046 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | asia_known_at | event_key? | O046 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | breakout_at | event_key? | O004, O046 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | breakout_close | decimal_price? | O004, O046 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | continuation_context | boolean? | O136, O046 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | decision_at | event_key? | O139, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | london_high | decimal_price? | O046 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | london_known_at | event_key? | O046 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | reference_frozen | boolean? | O046 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | retest_at | event_key? | O002, O030 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | retest_high | decimal_price? | O002, O030 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | retest_low | decimal_price? | O002, O030 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | risk_defined | boolean? | O139, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | side | enum | O139, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | vwap_at_retest | decimal_price? | O030 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | vwap_known_at | event_key? | O030 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M03 | vwap_reset_verified | boolean? | O030 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M04 | direction_recorded_before_entry | boolean? | O136 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M04 | small_size_recorded | boolean? | O059, O140 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M04 | source_directional_pullback_observed | boolean? | O053 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M04 | source_scalp_management_recorded | boolean? | O142, O145 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | absorber_aggressive | boolean? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | absorption_at | event_key? | O122, O101, O102, O104 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | absorption_at_that_band | boolean? | O125, O030, O031, O032, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | action_at | event_key? | O142, O143, O140, O150, O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | action_matches_preselected_policy | boolean? | O142, O143, O140, O150, O138 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | aggression_at | event_key? | O121, O100, O101, O102, O103 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | aggression_confirms | boolean? | O132, O041 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | aggression_still_unrewarded | boolean? | O129, O060, O101, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | arriving_aggression | boolean? | O121, O100, O101, O102, O103 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | at_valid_level | boolean? | O071, O060, O072, O066, O067, O069, O032, O002 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | auction_route_ok | boolean? | O090, O091, O092, O093, O096, O073, O083, O084 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | balance_context | boolean? | O129, O060, O101, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | band_known_at | event_key? | O125, O030, O031, O032, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | branch_regime_allowed | boolean? | O033, O034, O035, O042 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | breakout_at | event_key? | O131, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | breakout_in_thesis_direction | boolean? | O131, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | buyers_area_identified | boolean? | O127, O111, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | candle_delta_disagreement | boolean? | O124, O106, O108, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | catalyst_at | event_key? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | catalyst_known | boolean? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | catalyst_reclaimed | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | confirm_at | event_key? | O004 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | continuation_confirmed | boolean? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | control_side_matches_thesis | boolean? | O130, O072, O116, O102, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | cvd_filter_ok | boolean? | O105, O098 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | daily_limit_allows_entry | boolean? | O144, O145, O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | daily_r_before | decimal_source_R? | O104, O115, O145 | implemented | supplied_record | audited structured source/process records; full recipe rerun and typed projection | pass | complete |
| M05 | decision_at | event_key? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | defense | boolean? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | defense_at | event_key? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | delta_filter_ok | boolean? | O105, O098 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | directional_strength | boolean? | O131, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | distinct_test_count | integer? | O134, O117, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | drive_at | event_key? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | drive_retest_defended | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | earlier_risk_secured | boolean? | O142, O143, O140, O150, O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | entry_above_buyers | boolean? | O127, O111, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | entry_distance_ticks | decimal_ticks? | O104, O115, O145 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | entry_trigger_at | event_key? | O127, O111, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | executed_aggression | boolean? | O130, O072, O116, O102, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | exhaust_at | event_key? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | exit_or_new_thesis_recorded | boolean? | O142, O143, O140, O150, O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | explicitly_early_entry | boolean? | O133, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | failed_aggression_at_extreme | boolean? | O129, O060, O101, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | failure_at | event_key? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | fast_release | boolean? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | first_pullback | boolean? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | first_release_at | event_key? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | first_squeeze | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | flip_at | event_key? | O124, O106, O108, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | fresh_confirmation_after_stopout | boolean? | O144, O145, O138 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | fresh_confirmation_at | event_key? | O144, O145, O138 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | fresh_reward_retest_defended | boolean? | O122, O101, O102, O104 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | fresh_same_side_defense | boolean? | O130, O072, O116, O102, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | initiative_drive | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | intervening_wicks_taken | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | intrabar_poc_flip | boolean? | O124, O106, O108, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | kg1_retest | boolean? | O132, O041 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | ladder_confirmation | boolean? | O125, O030, O031, O032, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | leave_at | event_key? | O129, O060, O101, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | left_failed_area | boolean? | O129, O060, O101, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | level_known_at | event_key? | O071, O060, O072, O066, O067, O069, O032, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | lift_off | boolean? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | liftoff_at | event_key? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | little_progress | boolean? | O121, O100, O101, O102, O103 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | local_absorption | boolean? | O124, O106, O108, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | local_rejection | boolean? | O121, O100, O101, O102, O103 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | location_fixed | boolean? | O071, O060, O072, O066, O067, O069, O032, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | location_known_at | event_key? | O071, O060, O072, O066, O067, O069, O032, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | location_touched | boolean? | O071, O060, O072, O066, O067, O069, O032, O002 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | long_gamma | boolean? | O033, O034, O035, O042 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | microbalance_frozen | boolean? | O131, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | microbalance_known_at | event_key? | O131, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | no_aggression_at_failure | boolean? | O127, O111, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | no_new_buyer_defense | boolean? | O134, O117, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | no_prior_squeeze_failure | boolean? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | objective_fixed | boolean? | O141, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | opponent_thinning | boolean? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | opposing_effort_no_result | boolean? | O122, O101, O102, O104 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | opposing_pullback_aggression_absorbed | boolean? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | own_aggression_rewarded | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | own_reward_confirmed | boolean? | O122, O101, O102, O104 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | passive_wall_confirmed | boolean? | O122, O101, O102, O104 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | preconfirmation_entry | boolean? | O133, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | price_back_inside_band | boolean? | O144, O145, O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | prior_band_control | boolean? | O130, O072, O116, O102, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | prior_defense_at | event_key? | O130, O072, O116, O102, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | prior_exit_at | event_key? | O144, O145, O138 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | protected_structure_confirmed | boolean? | O142, O143, O140, O150, O138 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | pullback_at | event_key? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | real_extreme | boolean? | O071, O060, O072, O066, O067, O069, O032, O002 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | refill_at | event_key? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | refill_held | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | refresh_consistent | boolean? | O130, O072, O116, O102, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | rejection_at | event_key? | O121, O100, O101, O102, O103 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | release_at | event_key? | O128, O118, O111, O101 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | repeated_effort_no_reward | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | replenish_at | event_key? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | replenishment | boolean? | O123, O102, O114, O115 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | resistance_known_before_approach | boolean? | O135, O113, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | retest_at | event_key? | O122, O126, O129, O130, O132 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | retest_same_failed_area | boolean? | O129, O060, O101, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | reward_at | event_key? | O122, O101, O102, O104 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | reward_near_origin | boolean? | O122, O101, O102, O104 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | reward_ticks | decimal_ticks? | O104, O115, O145 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | risk_added | boolean? | O142, O143, O140, O150, O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | risk_defined | boolean? | O141, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | same_band_id | boolean? | O144, O145, O138 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | same_band_retest | boolean? | O130, O072, O116, O102, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | same_support_band | boolean? | O134, O117, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | selected_deviation_touched | boolean? | O125, O030, O031, O032, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | short_gamma | boolean? | O033, O034, O035, O042 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | side | enum | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | sires_branch_ok | boolean? | O121, O122, O123, O124, O125, O126, O127, O128, O129, O130, O131, O132 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | small_risk_declared | boolean? | O133, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | source_dom_confirmation | boolean? | O121, O100, O101, O102, O103 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | source_flow_confirmation | boolean? | O124, O106, O108, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | source_kg1_level_known | boolean? | O132, O041 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | source_refill_return | boolean? | O133, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | source_risk_predefined | boolean? | O133, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | source_squeeze_failed | boolean? | O127, O111, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | source_vwap_known | boolean? | O125, O030, O031, O032, O100 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | squeeze_failed | boolean? | O126, O118, O116, O099, O110 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | stop_behind_microbalance | boolean? | O131, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | stop_below_aggression | boolean? | O127, O111, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | stop_predefined | boolean? | O133, O139, O140 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | stop_trailed | boolean? | O142, O143, O140, O150, O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | supporting_structure_known_at | event_key? | O142, O143, O140, O150, O138 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | tape_died_at_failure | boolean? | O127, O111, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | target_is_prior_opposite_control | boolean? | O129, O060, O101, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | thesis_alive | boolean? | O138, O029, O147 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | thesis_dead | boolean? | O138, O029, O147 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | thesis_known_at | event_key? | O138, O029, O147 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | touch_at | event_key? | O071, O060, O072, O066, O067, O069, O032, O002 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M05 | upward_approach_loses_aggression | boolean? | O135, O113, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | aggressive_poc_passage | boolean? | O095, O064, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | alignment_ok | boolean? | O113, O097, O120, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | arrival_at | event_key? | O113, O097, O120, O100 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | arrival_read_recorded | boolean? | O113, O097, O120, O100 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | balance_fixed_before_use | boolean? | O060, O062, O085, O084 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | balance_known_at | event_key? | O060, O062, O085, O084 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | branch | enum | O097, O150 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | breakout_at | event_key? | O091, O097, O120, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | confirm_at | event_key? | O091, O097, O120, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | control_at | event_key? | O113, O097, O120, O100 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | control_evidence_recorded | boolean? | O113, O097, O120, O100 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | decision_at | event_key? | O097, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | local_control_confirms_return | boolean? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | ltf_balance_broken | boolean? | O091, O097, O120, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | ltf_balance_known_at | event_key? | O091, O097, O120, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | ltf_break_down | boolean? | O119, O107, O120 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | objective_fixed | boolean? | O139, O141, O089 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | older_value_known_at | event_key? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | older_value_rejected | boolean? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | older_value_tested | boolean? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | older_value_touch_at | event_key? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | original_balance_reaccepted | boolean? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | poc_passage_at | event_key? | O095, O064, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | prior_buying_at_upper_extreme | boolean? | O119, O107, O120 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | prior_failures_known_at | event_key? | O119, O107, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | profile_allows_trade | boolean? | O060, O062, O085, O084 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | reaccept_at | event_key? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | rejection_at | event_key? | O094, O092, O097 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | repeated_aggression_in_trade_direction | boolean? | O091, O097, O120, O100 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | repeated_body_selling | boolean? | O119, O107, O120 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | retest_at | event_key? | O091, O097, O120, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | risk_defined | boolean? | O139, O141, O089 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | same_boundary_retest_held | boolean? | O091, O097, O120, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | side | enum | O097, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | source_poc_hold_confirmed | boolean? | O095, O064, O141 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | target_is_far_balance_edge | boolean? | O095, O064, O141 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M06 | two_distinct_prior_failures | boolean? | O119, O107, O120 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | actual_band_contact | boolean? | O071, O072, O066, O002 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | area_known_at | event_key? | O072, O066, O070 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | buyers_absorb_and_hold | boolean? | O072, O101, O139 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | confluence_band_defined | boolean? | O071, O072, O066, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | decision_at | event_key? | O138, O141, O139, O140, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | hvn_known_at | event_key? | O072, O066, O070 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | independent_minor_hvn_known | boolean? | O072, O066, O070 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | objective_fixed | boolean? | O138, O141, O139, O140, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | planned_return_to_structure | boolean? | O072, O101, O139 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | prior_reaction_area_known | boolean? | O072, O066, O070 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | reaction_at | event_key? | O072, O139 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | resistance_rejection | boolean? | O072, O139 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | risk_defined | boolean? | O138, O141, O139, O140, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | side | enum | O138, O141, O139, O140, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | stop_above_rejection_high | boolean? | O072, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | stop_behind_long_invalidation | boolean? | O072, O101, O139 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | thesis_predefined | boolean? | O138, O141, O139, O140, O150 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M07 | touch_at | event_key? | O071, O072, O066, O002 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | a_end_at | event_key? | O078, O003 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | a_low | decimal_price? | O078, O003 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | a_period_complete | boolean? | O078, O003 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | aggressive_buy_imbalance_break | boolean? | O109, O120, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | breakout_at | event_key? | O063, O062, O004 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | breakout_close | decimal_price? | O063, O062, O004 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | buyers_defend_same_imbalance_band | boolean? | O091, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | decision_at | event_key? | O003, O141, O139, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | defense_at | event_key? | O091, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | dev_vah_at_break | decimal_price? | O063, O062, O004 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | dev_vah_known_at | event_key? | O063, O062, O004 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | developing_value_builds_higher | boolean? | O063, O062, O097 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | dom_supports_long | boolean? | O091, O100 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | imbalance_band_known_at | event_key? | O109, O120, O098 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | objective_fixed | boolean? | O003, O141, O139, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | observation_at | event_key? | O063, O062, O097 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | prior_vah | decimal_price? | O062, O086 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | prior_value_fixed | boolean? | O062, O086 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | retest_at | event_key? | O091, O100 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | risk_defined | boolean? | O003, O141, O139, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | side | enum | O003, O141, O139, O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | source_rejection_observed | boolean? | O063, O062, O097 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M08 | time_of_day_allowed | boolean? | O003, O141, O139, O150 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | cancel_minutes | decimal_minutes? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | departure_at | event_key? | O116, O148, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | departure_observed | boolean? | O116, O148, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | distinct_touch_id | boolean? | O116, O148, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | feature_max_known_at | event_key? | O117, O148, O149 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | fill_assumption_recorded | boolean? | O152, O151 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | grade_available_at | event_key? | O149, O148 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | grade_model_frozen_before_touch | boolean? | O149, O148 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | instrument_and_threshold_preserved | boolean? | O116, O099 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | label_uses_only_post_touch_observations | boolean? | O117, O148, O149 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | memory_uses_only_prior_resolved_touches | boolean? | O117, O148, O149 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | one_position_policy | boolean? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | order_at | event_key? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | order_inside_ticks | decimal_ticks? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | round_trip_cost_ticks | decimal_ticks? | O152, O151 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | stop_slippage_ticks | decimal_ticks? | O152, O151 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | stop_ticks | decimal_ticks? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | target_ticks | decimal_ticks? | O150 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | thesis_recorded | boolean? | O138 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | touch_at | event_key? | O116, O148, O002 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | touch_selected_without_future_information | boolean? | O149, O148 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | zone_definition_recorded | boolean? | O116, O099 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | zone_frozen | boolean? | O116, O099 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M09 | zone_known_at | event_key? | O116, O099 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | aggression | boolean? | O165, O164 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | cancellations_dominate | boolean? | O165, O163 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | conditioning_known_at | event_key? | O166, O111 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | efficient_displacement | boolean? | O165, O164 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | high_aggression | boolean? | O165, O164, O102 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | level_gives_way | boolean? | O165, O102 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | low_aggression_both_sides | boolean? | O165, O163 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | low_response_efficiency | boolean? | O165, O164, O102 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | next_state_at | event_key? | O166, O111 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | opposite_liquidity_holds_and_refills | boolean? | O165, O164, O102 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | participation_known_at | event_key? | O163 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | participation_record_complete | boolean? | O163 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | prior_absorption_or_effort | boolean? | O165, O102 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | recent_revisits | boolean? | O165, O163 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | replenishment_stops | boolean? | O165, O102 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | response_known_at | event_key? | O164 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | response_record_complete | boolean? | O164 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | state | enum | O165 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | state_at | event_key? | O165 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M10 | two_sided_executions | boolean? | O165, O163 | implemented | implemented | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | aggregate_winner_loser_comparison_recorded | boolean? | O153, O146 | implemented | supplied_record | audited structured source/process records; full recipe rerun and typed projection | pass | complete |
| M11 | all_eligible_observations_retained | boolean? | O148, O146 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | cycle_and_indicator_rules_recorded | boolean? | O162, O157, O158, O159, O160, O161 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | features_available_before_decisions | boolean? | O148, O146 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | historical_comparison_defined | boolean? | O162, O157, O158, O159, O160, O161 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | inclusion_rule_fixed | boolean? | O137, O148 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | outcomes_separated_from_inputs | boolean? | O148, O146 | implemented | supplied_record | audited structured source/process records; full recipe rerun and typed projection | pass | complete |
| M11 | process_spec_frozen | boolean? | O137, O148 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | release_vintages_recorded | boolean? | O162, O157, O158, O159, O160, O161 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | revision_uses_only_prior_sample | boolean? | O137, O148 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | sample_start_at | event_key? | O137, O148 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | spec_known_at | event_key? | O137, O148 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M11 | uniform_schema | boolean? | O137, O148 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | average_rr_known | boolean? | O154, O148, O153 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | base_risk_fraction | decimal_fraction? | O155 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | decision_at | event_key? | O155, O153 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | first_trade_close_at | event_key? | O155, O153 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | first_trade_closed | boolean? | O155, O153 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | first_trade_result_units | decimal_baseline_units? | O155, O153 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | mc_loss_streak_known | boolean? | O154, O148, O153 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | next_risk_units | decimal_baseline_units? | O155 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | planned_reward_r | decimal_source_R? | O155 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | prior_sample_n | integer? | O154, O148, O153 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | risk_stage | enum | O155 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | risk_units | decimal_baseline_units? | O155 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | second_trade_result_units | decimal_baseline_units? | O155, O153 | implemented | parent_derived | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | validated_process | boolean? | O154, O148, O153 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |
| M12 | win_rate_known | boolean? | O154, O148, O153 | implemented | source_only | audited source interpretation; remains supplied, never a native detector | pass | complete |

## PHASE — retained historical run (not an acceptance result)

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/jj-tbr.md |
| GB-FAIL | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/gb-fail.md |
| GB-VWAP | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/gb-vwap.md |
| GB-SCALP | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/gb-scalp.md |
| SIRES | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/sires.md |
| SAINT-AMT | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/saint-amt.md |
| MEMBER-TWO-REASONS | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/member-two-reasons.md |
| KEANI-OPEN-ABOVE-VALUE | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/keani-open-above-value.md |
| REFILL-STUDY | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/refill-study.md |
| JETBUNDLE-STATES | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/jetbundle-states.md |
| STOIC-DATA | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/stoic-data.md |
| STOIC-RISK | historical/source | — | — | unavailable (retained report: not recorded) | /workspace/implementation/reports/phase1-live/methods/stoic-risk.md |

## Audit — current contract coverage

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Full source profiles, parent geometry, mirrored OB, 14-bar history and source-selected context/confirmation assembly remain incomplete. |
| GB-FAIL | M02 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Reference/sweep timing and operand construction need completion; November 20 must retain its observed sweep-entry interpretation. |
| GB-VWAP | M03 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Dated Asia/London high roles, source VWAP configuration and later retest/risk evidence are not assembled. |
| GB-SCALP | M04 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Case descriptions exist; a complete automatic admission rule cannot be inferred from the supplied bias/risk fragments. |
| SIRES | M05 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Full profiles, local footprint/DOM sequences, persistent thesis/re-entry and order management have major documented gaps. |
| SAINT-AMT | M06 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Profile routes need native construction, same-band break/retest and HTF/LTF evidence; presence-only profile permission is inadequate. |
| MEMBER-TWO-REASONS | M07 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Two reasons need independent prior reaction/HVN evidence and planned return identity; supplied geometry is insufficient. |
| KEANI-OPEN-ABOVE-VALUE | M08 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Full prior VA, complete A period, developing value and defended imbalance retest are not constructed as one dated sequence. |
| REFILL-STUDY | M09 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Touch/selection checks are useful; native source zone/grading records and correct pending-order/lifecycle behavior remain incomplete. |
| JETBUNDLE-STATES | M10 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Supplied state audits exist; native lifecycle identity and actual adjacent transition evidence remain incomplete. |
| STOIC-DATA | M11 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Process/journal primitives exist, but actual versioned research records and joins are unbuilt; macro remains deferred. |
| STOIC-RISK | M12 | complete | current contract checks: complete | unavailable (no historical cohort) | unavailable (no historical cohort) | retained report status: not recorded; original audit: Printed risk arithmetic exists; complete prior validation, stage/reset and account-policy evidence remain incomplete. |
