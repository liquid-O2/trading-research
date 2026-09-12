# Phase 1 implementer formulas

Version: `method-pack-v1`, 2026-09-11. Method inventory: 12. Object inventory: 166. This document replaces the previous formula specification in full.

## Read and implement in this order

1. Read **C00–C08** once. They define the data and evidence contract, not another operating method.
2. In **M01–M12**, select exactly one method from the wiki index and its source branch. Follow that method's object list into **O001–O166**. Each object recipe contains its complete allowed procedure, field contract, timing, invalid cases, constants and fixture.
3. Implement the selected method through its report in one vertical slice. Use the command and acceptance criteria in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md). A helper being implemented does not finish a method.
4. Implement literal algebra and state transitions. For a **HOLE**, implement the specified unknown value and reason. Do not search the PDFs for an alternative, tune a detector, use another author's rule, or silently adopt an old function's behavior. A supplied source record can fill only the fields it actually supplies.
5. Existing functions may be deleted or replaced. Preserve repository interfaces only when they can satisfy this contract. Old formula IDs, old component scores and stale cached rows are not acceptance evidence. Do not rebuild the unpublished engines listed in the recipes.

The controlling evidence is [the wiki index](/workspace/planning/phase-1-live/wiki/index.md) and its mapped pages at commit `4962136bf1522a49bb0bd2fd6a1ad8f18d2813c9`. The source sentences and citations needed to implement are reproduced beside each recipe. Cited source figures clarify printed arithmetic; an unresolved figure/caption conflict remains a hole. No existing PRD, SPEC, PHASE or FORMULAS content was used as a requirement baseline.

## C00 — What a Phase 1 result means

The unit is a **named operating method**, not an object family, isolated indicator or profitable trade. The primary predicate checks the method's source sequence. A valid losing attempt can pass that predicate. A later favorable move cannot repair missing context, a late reference or a skipped confirmation.

Keep these measurements separate:

| Measurement | Unit | Required interpretation |
|---|---|---|
| `sequence` | One source-defined candidate episode | Did all prerequisites for the selected method/branch exist, in order, by the decision? |
| `case_description` | One incomplete source case | Does the record match the disclosed portion? It never upgrades an unpublished full trigger to pass. |
| `management` | One observed action linked to an entry | Does the action obey the previously selected source policy and use already-known structure? |
| `reference_outcome` | One preselected level/objective after a decision | Which objective/invalidation event occurred first, or was the observation censored? This is not a financial return. |
| `process` / `risk_rule` / `state_observation` | The non-entry unit explicitly specified by M09–M12 | Verify the published research, arithmetic or observation process without inventing an entry system. |

No order routing, portfolio simulation, strategy optimization, expected-profit claim, new classifier training or unpublished indicator reconstruction belongs to this implementation. Imported source return/risk numbers can be checked for provenance and literal arithmetic where a method requires them; do not generate a new return series.

## C01 — Types, identity and evidence

**Use exact units.** Store timestamps as signed 64-bit integer UTC nanoseconds, never floating-point epochs. Keep source timestamp precision separately. Store trade prices as exact decimal values or integer native ticks. Use the instrument definition's positive tick size `q`; do not infer q from the smallest movement in a sample. Algebraic levels such as midpoints and 1.33 projections may lie between tradable ticks: retain their exact decimal price, and do not round them into an order unless the source supplies an order-rounding convention.

**Required normalized records:**

| Record | Required fields and types |
|---|---|
| `event` | `event_id:string`, `dataset_id:string`, `source_file:string`, `source_row:integer`, `instrument_id:integer/string`, `raw_symbol:string`, `root:string`, `event_ns:int64`, `source_precision:string`, `action:enum`, `aggressor:buy/sell/unknown`, `price:decimal?`, `size:integer?`, `bid:decimal?`, `ask:decimal?`, `bid_size:integer?`, `ask_size:integer?`, `flags:integer?`, `ordering_basis:string`, `known_at:key` |
| `bar` | `bar_id`, `instrument_id`, `kind:time/native_range`, `size`, `start:key`, `end:key`, `O,H,L,C:decimal`, `volume:integer/decimal`, `member_event_ids` or immutable member-range locator, `complete:boolean`, `coverage_state`, `known_at:key` |
| `object` | `object_id`, `recipe_id`, `method_id`, `branch_scope`, `author`, `instrument_id`, `parent_ids[]`, `source_ref`, `value` or typed payload, `units`, `formation_start`, `formation_end`, `as_of`, `known_at`, `state:computed/supplied/hole/invalid`, `hole_ids[]`, `evidence_ids[]` |
| `assertion` | `assertion_id`, `field`, `value:true/false/null`, `method_id`, `branch`, `candidate_id`, `band_id`, `side`, `evidence_ids[]`, `observation_start`, `observation_end`, `known_at`, `evidence_mode:raw_derived/supplied_contemporaneous/source_illustration/synthetic_fixture`, `source_ref`, `reason` |
| `candidate` | `candidate_id`, `method_id`, `branch`, `side:long/short/not_applicable`, `instrument_id`, `session_date_et`, `decision_at`, `parent_attempt_id?`, `thesis_id?`, `band_ids[]`, `object_ids[]`, `assertion_ids[]`, `cohort_id`, `evidence_mode` |
| `hole` | `hole_id`, `recipe_id`, `method_id`, `branch`, `candidate_id?`, `kind:source_definition/source_conflict/data_coverage/ordering/identity/supplied_record_missing`, `missing_fields[]`, `source_ref`, `affected_output`, `reason` |

An evidence record is not permission to type `true`. Every computed assertion must name the object recipe, its raw inputs and the comparison performed. Every supplied assertion must contain the actual cited observation, its author/side/band, event interval and availability. Blank descriptions, a naked Boolean, a later outcome or an uncited screenshot label do not satisfy this schema.

**Qualitative assertions:** a source says “acceptance,” “strong,” “little progress,” “clean,” “consistent refresh,” “valid balance,” or similar without a reconstructable detector. Preserve the observable prices/volumes and a supplied source interpretation. The automatic interpretation is `null` with that recipe's hole. Do not turn `source_confirmation`, `context_fixed`, `thesis_alive`, or any similarly named field into a caller-supplied escape hatch. Its producer and evidence are mandatory.

**Two evidence times:** `known_at` is when the market fact or supplied decision record was available, not when this pack was written. `recorded_at`/`source_published_at`, if present, is when a caption or annotation was created. A retrospective drawing alone cannot prove that a historical trader selected the band before entry. Such a record can pass an explicitly labeled source-illustration fixture, not a contemporaneous historical-cohort admission test. Synthetic fixtures never enter market counts.

**Identity joins:** stages join on `candidate_id + method_id + branch + instrument_id + band_id + side`. A source explicitly connecting two different bands adds named parent/child IDs and the relationship. Do not join by nearest price, same calendar day, row number alone, or whichever available event makes the expression true. Shared objects do not transfer another author's trigger.

## C02 — ET, bars, resets and ordering

1. Where the source specifies ET, interpret wall time in IANA `America/New_York`, with date-aware DST. Store both the ET date/clock and UTC key. No fixed UTC−4 or UTC−5 offset for a multi-year run. A source chart with unresolved timezone remains `HOLE:CLOCK_SOURCE`.
2. A time interval is half-open `[start,end)`. A 09:00–10:00 range includes the 09:59 minute and excludes the 10:00 minute. A range built from time bars is available at `end`, after the last included bar closes. Intraday bars are aligned to ET wall-clock multiples of the stated size, not every N observed rows.
3. For a d-minute bar, group all valid member events in its interval, preserving instrument. `O=first price`, `H=max price`, `L=min price`, `C=last price`, `V=sum size`. Equivalently aggregate complete finer bars with `O=first O`, `H=max H`, `L=min L`, `C=last C`, `V=sum V`. A known empty interval may have zero activity but has no fabricated OHLC. A missing interval is not a known empty interval. Never forward-fill an entry confirmation across a coverage gap.
4. If input is only a completed one-minute OHLCV bar, its O/H/L/C/V as a record are known at minute end. In particular, do not expose the stored open at the exact opening instant as if a tick had arrived. A literal opening price at first trade requires the trade event. This distinction matters for Jumbo's outbound cash-open leg and TDO/cash-open availability.
5. A five-minute confirmation at 10:05 uses the complete `[10:00,10:05)` interval. Four minutes plus the next observed minute at 10:06 is not that bar. The sweep can precede the bar's closing event within the same five-minute bar only if finer evidence establishes that order; a high/low alone is not an event timestamp.
6. The source TPO lesson specifies 30-minute letters: A `[09:30,10:00)`, B `[10:00,10:30)`, etc.; its IB is the first hour, A+B. Those are that source's settings, not a global reset for volume profiles or VWAP. Jumbo OB examples use 2/3/5-minute candles. NQ “40-range” preserves its native source construction; range-size unit, reversal/overshoot treatment and event membership must be source-compatible. Do not substitute 40 minutes, 40 bars or a guessed range-bar algorithm. [TPO] pp.3, 8; [TBR] pp.27–29; [BIG] pp.3–5.
7. Completed fixed objects retain their original `known_at`. A developing profile/VWAP creates a new immutable snapshot at every use, with `as_of <= known_at <= use_at`. Never mutate an earlier snapshot to the final-day value. A swing anchor becomes usable at confirmation, not at the earlier pivot's price time.
8. Reset **only at the object's stated source boundary**: chosen formation, profile, VWAP anchor, DOM observation start, account day or process-version change. Midnight, Globex open and cash open are different resets. Missing reset is a hole; `09:30` is not a fallback.
9. An event key has UTC time and a verified ordering relation. The retained Quant Pad schemas omit exchange sequence and receive timestamps. Preserve physical file-row identity for reproducibility, but do not claim an economic ordering between indistinguishable tied timestamps from that alone. Aggregate commutative quantities over the entire tie batch. If a predicate needs strict order inside an unresolvable tie batch, return `unknown_order`; do not break the tie by side/price. Independent streams also need a verified common ordering before a strict cross-stream claim.
10. A known instrument roll, a coverage gap or a reset terminates the current raw aggregation. Do not join a pre-roll price level to post-roll prices without an explicit source-compatible mapping. Preserve native contracts and record the unavailable bridge. Historical continuous-contract roll maps are provenance, not evidence of a live roll-selection strategy.

**Clock fixture C02-F1 (synthetic):** 2026-01-15 09:30 ET is 14:30 UTC; 2026-07-15 09:30 ET is 13:30 UTC. Range `[09:00,10:00)` has final H=105 at 09:59 and L=100 at 09:10: at 09:45 its final range is unavailable; at 10:00 it is H=105/L=100. A 10:00 bar with H=120 cannot change that range. A five-minute bar missing 10:02 has `complete=false`; grouping five available rows must not pass it.

## C03 — Acquired data: adapters and limits

Inventory inspected for this pack: 111 dataset entries in [dataset-catalog.json](/workspace/data/manifests/dataset-catalog.json), with per-file bounds in [files.csv](/workspace/data/manifests/files.csv), schemas in [schema-catalog.json](/workspace/data/manifests/schema-catalog.json), timestamp profiles in [timestamp-conventions.json](/workspace/data/manifests/timestamp-conventions.json) and exclusions in [exclusions-and-gaps.json](/workspace/data/manifests/exclusions-and-gaps.json). Inventory generation was 2026-09-05. Resolve `archive_path` under `/workspace/data/`; do not use the catalog's historical staging-root string as the live root. “Complete” is acquisition scope, not proof every method input exists.

### Exact adapters

| Input under `/workspace/data/` | Native fields → normalized use | Timing / restriction |
|---|---|---|
| `quantpad/cme__{nq,es,ym,rty}-continuous-futures__ohlcv-1m/*.parquet` | `t→bar_start_ms`; `o,h,l,c,v→O,H,L,C,V`; `instrument_id` retained | `t` is UTC **milliseconds**; `start_ns=t×1,000,000`, close one minute later. Price doubles are already price units. No `1e-9` rescaling. |
| `quantpad/cme__nq-continuous-futures__ohlcv-1s/*.parquet` | Same OHLCV fields | UTC milliseconds, one-second bars. Better temporal resolution still does not order high versus low inside that second. |
| `quantpad/cme__{nq,es,ym,rty}-continuous-futures__trades/*.parquet` | `t,price,size,side,instrument_id,flags` | `t` is UTC **nanoseconds**. All rows are trade records. Source side must be decoded as below. |
| `quantpad/cme__{nq,es}-continuous-futures__mbp-1/*.parquet` | `t,action,side,price,size,bid_px,ask_px,bid_sz,ask_sz,instrument_id,flags` | UTC nanoseconds. Executed volume comes only from `action='T'`. Quote updates are not volume. BBO depth only. |
| `derived/continuous-futures__instrument-and-roll-maps/{nq,es,ym}-instruments.parquet` and `*-rolls.parquet` | `instrument_id,raw_symbol,root,min_price_increment`; segment `*_ms` fields; definition `*_ns` fields | Decode each unit from manifest, join by actual instrument/segment. `contract_multiplier` can be null: do not fabricate monetary tick value. RTY roll maps are absent. |
| `thetadata-opra/opra__{qqq,spy,...}-options__{contracts,open-interest,quote-1m...,trade-quote...}/*.parquet` | Native identity is `symbol,expiration,strike,right,osi_symbol`; OI=`open_interest`; quote=`bid,ask,bid_size,ask_size`; timestamps=`ts_event`, `ts_quote`, `ts_created` where actually present | Arrow UTC timestamps, effective millisecond source precision. Already localized from ET; **do not localize a second time**. `request_date` is not availability. Expiration ET date must equal observation ET date for a selected 0DTE cohort. No Greek/position sign or proprietary level is inferred. |
| `free-sources/context__event-calendar__normalized/*` | `event_date,event_ts_utc,event_time_et,event_type,event_name,time_basis,status,source,source_url,details_json` | Some files have null intraday time. Preserve that null. Calendar schedule is not released macro value or announcement vintage. |
| `free-sources/context__volatility__normalized/*`, `cboe__vx-futures__normalized/*`, `fred__usd-rates__normalized/*` | Dataset-specific series, date, value/settlement and units | Date-only records do not prove a morning value or publication time. Later revisions are not original releases. Preserve vintage holes. |
| `databento/cme__*-options-on-futures__*` and companion futures archives | Native `.dbn.zst`, separate trade/definition/statistics schemas | Decode DBN using its schema; native fixed-point price scaling differs from normalized Parquet doubles. These are available reference data, not replacements for a method's native QQQ/SPY context. |

**Correct aggressor decoding:** Databento `Trade` side `B` is buyer aggression, `A` is seller aggression, `N` is unspecified. Therefore `signed_size=+size` for B, `-size` for A, and null signed contribution with separately counted unknown volume for N. For add/modify/cancel records, side describes the resting book side; do not interpret it as an execution. `F` fills must not be added to `T` aggressor events to count the same business twice. Source: [Databento trade schema](https://databento.com/docs/schemas-and-data-formats/trades) and [action/side definitions](https://databento.com/docs/standards-and-conventions/common-fields-enums-types). The current `mbp1_extract._side_code` does the opposite; replace that behavior and invalidate dependent retained signed-flow rows. Do not reuse them under a new label.

**Raw fixture C03-F1:** first eight qualifying A/B `T` records in `quantpad/cme__nq-continuous-futures__mbp-1/2026-08.parquet`, instrument 42004177 / NQU6, q=0.25 from the instrument table:

| t (UTC ns) | side | price | size | bid | ask | expected signed size |
|---:|---|---:|---:|---:|---:|---:|
| 1785708000010094835 | A | 28565.00 | 2 | 28565.00 | 28565.50 | −2 |
| 1785708000012065051 | B | 28565.00 | 1 | 28562.50 | 28565.00 | +1 |
| 1785708000064473453 | B | 28565.00 | 3 | 28562.50 | 28565.00 | +3 |
| 1785708000064473453 | B | 28565.50 | 1 | 28562.50 | 28565.00 | +1 |
| 1785708000064473453 | B | 28566.50 | 1 | 28562.50 | 28565.00 | +1 |
| 1785708000114275709 | A | 28560.50 | 1 | 28560.50 | 28568.00 | −1 |
| 1785708000137317581 | A | 28565.25 | 1 | 28565.25 | 28567.75 | −1 |
| 1785708000149312667 | B | 28565.50 | 1 | 28562.00 | 28565.50 | +1 |

Expected buy volume **7**, sell volume **4**, total **11**, delta **+3**. The three equal timestamps form a five-contract buy batch; their internal sequencing must not supply three successive lift-off observations. The first quote spread is `0.50/0.25=2` ticks. The stored price 28565 is not 0.000028565. This fixture checks the adapter, not a source trade setup.

### Coverage boundaries that affect method eligibility

| Data | Manifest observation coverage | Required handling |
|---|---|---|
| NQ/ES/YM minute bars | 2010-09-06 through 2026-09-02 15:19 UTC; initial/final days partial | Derive each complete local window from actual rows. Do not mark an entire endpoint day covered. |
| NQ one-second bars | 2010-09-06 through 2026-09-02 15:19:59 UTC | Same window check; no signed volume. |
| NQ standalone trades | 2021-09-01 18:00 UTC through 2026-09-02 17:59:59 UTC | The directory's advertised “2020 onward” scope is not its actual lower bound. |
| NQ MBP-1 including `T` trades | 2020-01-01 23:00 UTC through 2026-09-03 06:09:59 UTC | Can supply the earlier executed tape where valid. Use one canonical tape, not standalone trades appended to MBP-1 trades. |
| ES/YM/RTY standalone trades | 2020-01-01 through 2026-09-03 partial day | Validate exact per-instrument windows. These do not supply missing DOM depth. |
| ES MBP-1 | 25 files, partial/paused; last observed 2024-08-30; many missing months | No blanket 2020–2026 DOM coverage. Emit candidate-specific missing intervals. |
| Native options | QQQ/SPY full-chain contracts and OI begin 2016; selected quote/trade cohorts generally begin 2020 | Respect actual expiry/strike/quote coverage and OI knowledge times. Available chains do not reconstruct dealer positioning, KG1 or source wall engines. |
| Volatility, rates, calendars | Mixed date-only and timed observations | Do not manufacture intraday availability or a complete news universe. |
| AAPL 10-level/order stream, verified hidden reserve, source account journals, proprietary source snapshots | Not supplied by the inspected relevant inventory | Return the explicit required-data/source hole. NQ BBO is not AAPL full participation; option-chain data are not proprietary readouts. |

**Overlap and double counting:** NQ MBP-1 contains both weekly and monthly files, including overlapping 2020 partitions. Never glob-append all 142 files as independent events. For each UTC calendar month, select the complete monthly file as owner when present and valid; use weekly partitions only for a span not owned by a valid monthly file, clipping them to that span. Freeze a file-ownership manifest with source paths and disjoint half-open time spans. If two fallback files overlap, verify identical ordered records for the overlap before choosing one; otherwise emit `HOLE:DATA_OVERLAP` for that span. Do not deduplicate on `(t,price,size,side)`: distinct genuine trades can share those fields. For flow use MBP-1 T events when available; standalone trades are a separately declared fallback/cross-check, never additional volume. This is a transport convention, not an author parameter.

Other acquired copper, Nikkei, silver, rates, fund-flow, COT and options archives were inventoried. No method here names an entry rule on those merely because files exist. Do not broaden the method universe. `/workspace/data` remains on disk, unmodified and uncommitted.

## C04 — Availability and three-valued predicates

For every prerequisite x used at stage s, require `x.known_at <= s`, its source scope to match, and all dependency observations to be available by x.known_at. `max_input_known_at` is the maximum of dependencies, not a chosen constant. If a later datum supplies an earlier premise, emit a witnessed **false** for `base_ok` and increment `detected_causal_violations`. If availability is unknown, `base_ok=null` with a hole. `leakage_count` counts violations incorrectly admitted as valid evidence/pass; it must be zero. Correctly rejecting a leaky source record or a deliberate negative fixture is successful validation, not an implementation failure.

`base_ok` combines source/author/instrument identity, correct units/clocks, causal dependency checks and source-compatible joins. `coverage_ok` is true only for the inputs required by the selected branch. Optional context from another branch is not a missing required input. `sequence_ok` is the exact selected method expression below. Use SQL/Kleene three-valued AND/OR/NOT, never language truthiness and never `COALESCE(missing,true/false)`.

```sql
CASE
  WHEN base_ok IS FALSE OR sequence_ok IS FALSE THEN 'fail'
  WHEN base_ok IS NULL OR coverage_ok IS NOT TRUE
       OR sequence_ok IS NULL THEN 'unknown'
  ELSE 'pass'
END
```

`false AND unknown` is false because a demonstrated broken prerequisite is sufficient to reject an attempted sequence; preserve the unknown reasons too. `true AND unknown` is unknown. `true OR unknown` is true only when that OR is actually present in the source method, not when unrelated confirmation branches are pooled. If an object is not required by the chosen branch, store `applicability=not_required`; do not pretend it was observed true.

A corrupted record or absent file yields invalid/unknown evidence, not a negative market example. A fully observed sweep which stays outside, wrong-side entry, late reference or missing required retest in a fully observed admitted attempt can yield false. If the source never specified what a qualifying retest/hold is, lack of a chosen proxy does not yield false; it is a definition hole.

**C04-F1:** four candidates with `(base,coverage,sequence)` of `(T,T,T)`, `(T,T,F)`, `(T,F,null)`, `(F,F,null)` produce pass, fail, unknown, fail. Counts: p=1, f=2, u=1, n=3, N=4. Changing only the fourth candidate's later target outcome cannot change its fail.

## C05 — Candidate discovery, attempts and cohorts

A candidate is a proposed decision/observation, **not** each bar, each indicator flag, every calendar day or each row of a touch. Freeze an inclusion manifest before scoring. It contains method/branch, evidence mode, instruments, source configuration, date span, data ownership, candidate rule, required inputs and their recipe versions. Hash the manifest and selected formula sections into every report.

Three disjoint cohorts are allowed:

- **Synthetic fixtures:** exact numbers and mutations printed in this pack. They test implementation behavior and are excluded from historical n/rate/year splits.
- **Source illustrations / supplied episodes:** the cited source case or a supplied, timestamped decision/state/process record. Preserve whether it is retrospective or contemporaneous. Every proposed attempt is retained, including losses, misses and failed prerequisites. A source illustration is not an unbiased discovery sample.
- **Historical discovery:** only episodes found by a complete, source-defined causal candidate selector and all its required object procedures. Do not invent a scan threshold or use target reach to select candidates. Most discretionary context/confirmation selectors in this wiki are incomplete: the corresponding automatic cohort is explicitly unavailable, even if geometry can be calculated for many dates.

If a required selector is a hole, output `candidate_discovery=hole`, a complete branch hole record, and `n=0` for that unavailable automatic cohort. Do not fabricate one unknown trade per minute/day to inflate N. If supplied candidates exist, score them and retain their own denominator. A missing whole cohort is different from u unknown candidates within an identified cohort.

A **distinct touch** needs contact after a documented departure from the same frozen band; repeated rows while still inside are one touch. Spatial departure can be recorded literally as price outside `[lo,hi]`; the source's stronger acceptance/hold criterion remains a separate field. A new source-defined attempt needs a new decision/entry record and, where relevant, a completed prior exit. Three touch bars do not become three failed trades. Re-entry has a new candidate ID and parent attempt; it does not reset thesis, band, daily losses or source rule version.

Do not pool branch, instrument, source version, evidence mode or different observation units to obtain an apparent large sample. The method headline can summarize the same unit's branches with counts and a visible branch breakdown; process/state/risk rows remain separate methods. The report must expose every branch, including branches with no source-complete automatic selector.

## C06 — Non-financial outcomes after the decision

Freeze `outcome_start=decision_at`, the source objective ID/bounds, invalidation rule, observation end and coverage rule before examining later records. No universal 15/30-minute, half-range, stop-distance or target cap is supplied here. If the source or supplied record does not define the needed outcome window/stop/target, output `outcome=unknown` with that field's hole and still score any independently complete entry predicate.

Using ordered, covered events strictly after the decision, find the first target event T and first invalidation event I under their literal rules. Return:

- `target_first` if T exists and I is observed absent through the window or T<I;
- `invalidation_first` if I exists and T is observed absent through the window or I<T;
- `same_time_unknown` if T and I cannot be ordered;
- `neither_observed` if the full declared window is covered and neither occurs;
- `censored` if the window terminates early or the position/observation is ended before resolution;
- `unknown` for missing definition, coverage or event order needed for the answer.

A null I is not proof that invalidation never occurred. It must carry `invalidation_observation_complete=true` before target-first can use absence. Partial objective touch and full-band traversal are separate events. A source's entry may use a close while its destination is a price touch; preserve both conventions. Do not calculate target reach using an extreme before decision or choose an objective from the final session path.

**C06-F1:** long decision 10:06, entry reference 100, preselected target 104, price invalidation 98, complete window through 10:30. A 10:10 trade at 104 and 10:12 trade at 98 → target_first. Reverse the times → invalidation_first. Only one OHLC bar H=104/L=98 covering both → same_time_unknown. A 10:04 high of 104 does not count. If the observed prefix through 10:08 is complete, neither event has occurred and observation then stops, return censored. If an internal gap prevents establishing that prefix, return unknown with the coverage hole. Neither result is a completed target miss.

## C07 — Report arithmetic and acceptance status

For one method/predicate/cohort with identified candidates:

- `p=count(verdict='pass')`, `f=count(verdict='fail')`, `u=count(verdict='unknown')`.
- `n=p+f` is the number whose predicate is decidable; `N=n+u` is the identified candidate population. Emit both p/f/u/N in the report even though the requested headline has only n.
- `rate=p/n` when n>0, otherwise null (`—` in Markdown). This is source-sequence compliance among decidable candidates, never a trade win rate.
- The headline `interval` is the **exact missingness interval** for compliance over the identified finite cohort: `[p/N,(p+u)/N]`, when N>0. It answers how much unresolved candidates can change the overall rate. It is not a sampling confidence interval. This choice requires no invented confidence level, independence assumption or trading constant. When N=0 both bounds are null, never `[0,0]`.
- Split by the ET year of `decision_at`; for a state/process/risk record use its method-defined observation/decision key. Print every year actually in the selected cohort, plus covered requested years with zero candidates and the reason. Label partial endpoint years. Sum yearly counts to the corresponding cohort totals. Do not move a prior-evening event into a different year from its chosen session/decision identity.

**C07-F1:** p=8, f=2, u=2 → n=10, N=12, rate=0.8, interval=[2/3, 5/6] ≈ [0.666667, 0.833333]. If 2025 has p=3/f=1/u=1 and 2026 has p=5/f=1/u=1, their n values are 4 and 6 and sum to 10. If p=f=u=0, rate and interval are null. Formatting can show six decimals, but counts and exact ratios are retained; display precision is not a model parameter.

**Status separates software correctness from source completeness:**

| Status | Exact condition |
|---|---|
| `not_run` | This planning pack has not executed the method. Counts/rates are not populated from old reports. |
| `implementation_fail` | Any printed fixture mismatch, incorrectly admitted causal leak, proxy-as-faithful admission, missing required output, wrong method inventory, or violated report invariant. Correctly rejected negative cases do not cause this status. |
| `source_hole` | Implementation checks pass, but any required source definition/conflict or absent source-specific record prevents the claimed full method/branch from being implemented faithfully. Emit all affected branches. |
| `data_hole` | Definitions for the attempted scope are complete, but required market/decision evidence is absent or incomplete. Source holes take precedence if both exist. |
| `measured` | Implementation checks pass, the claimed cohort and branch definitions are complete, observations are present, n>0, and all remaining unknown candidates/reasons are explicitly retained. This certifies the report's scope, not an entry edge. |
| `no_candidates` | Complete selector and coverage, but genuinely zero identified candidates in the requested scope. Distinguish this from a missing selector. |

Every method writes summary, branches, yearly counts, candidate verdicts, used object values, fixture results and holes. Keep `detected_causal_violations` and `rejected_proxy_attempts` separate from zero-required `leakage_count` and `proxy_as_faithful_count`. A successful command can produce `source_hole`: correct refusal to invent is part of the acceptance contract. It must not print `measured` for only the easiest surviving branch while hiding the other branches required by that method's selected scope.

## C08 — Numerical fixture rules and source holes

Every O recipe has a numbered fixture. Unless labeled **raw** or **source-printed**, numbers are synthetic inputs that exercise the cited procedure; they are not new trading constants and are never observations in a historical sample. A fixture's q=0.25 is a declared test instrument unit, not permission to assume every instrument uses it.

For every object fixture also execute these mutations: use one dependency whose known_at is after use → false causal check; remove one required datum → unknown with the named field; replace parent/band/instrument with another identity → invalid join/unknown identity, or witnessed false if the mismatch itself is the tested rule. For every method fixture execute the explicit negative and hole cases in its M section. Preserve false versus unknown.

A source hole is an output contract, not unfinished implementer reasoning. Implement `value=null`, its `HOLE:Oxxx:<field>` identifier, affected branch and exactly what evidence is absent. Never choose a default, search a parameter grid, copy another author's threshold or ask the implementer to “use judgment.” A supplied, independently timestamped source value can be ingested with its provenance and limits; that does not authorize building its unpublished engine.

**Applicability is not invented evidence.** If the selected source branch explicitly does not require an object, retain `applicability=not_required`. Its conditional gate contributes the Boolean identity `true` when composing that branch, but no observed assertion is fabricated. If it is unclear whether the source requires the object, return an applicability hole. This is how optional TDO, optional pocket and branch-specific gamma requirements remain scoped.

**Method fixtures are algebra fixtures.** Their supplied qualitative observations have `evidence_mode=synthetic_fixture`, an ID, the stated source-recipe meaning, side/band, observation interval and known_at. They exercise the printed predicate and do not claim that the missing author detector has been recovered. Never ingest them as historical candidates. A method's positive fixture must be paired with its printed negative and hole mutations and the C08 identity/time mutations.

**Replacement obligations.** The object pages below reproduce the wiki's current-code attachments for navigation only; old R-/P3- labels are not surviving requirements. Replace conflicting functions, adapters and caches. In particular: correct A/B aggression; use clock-aligned closes; remove final-day/profile/median inputs from earlier decisions; preserve full C2 orderblocks versus wick rejection blocks; use 0.6/1.5/14 for Jumbo's displayed candle settings with unresolved conventions explicit; preserve true impulse parents for golden pockets and projections; keep same-candle POC snapshots, same-band retests, older external POC identity and correct Failed Auction target binding; preserve every required OFM stage; and keep unknown proprietary/reset/threshold fields unknown. A cached result produced by a conflicting rule is not reusable evidence.


## Method input views and primary predicates

Each M section is a typed contract for one conceptual `operator_input` view. These views do not yet exist. A future implementation may use SQL or equivalent three-valued evaluation, but it must preserve every operand, source identity and timing comparison. Evaluate the printed Boolean body as `sequence_ok` (or the explicitly named case/process/risk predicate), then apply C04. No unbound field may default to true or false. Every scalar retains its producing object and evidence IDs. A null operand carries its specific `HOLE:Oxxx:field` or `HOLE:Mxx:field` reason.

| Contract | Method | Primary predicate / unit |
|---|---|---|
| [M01](#m01) | JJ-TBR | `sequence` — One source-selected TBR decision attempt, with one of its eight named branches. |
| [M02](#m02) | GB-FAIL | `sequence` — One identified failed-breakout/failed-breakdown attempt at its actual completed source reference. |
| [M03](#m03) | GB-VWAP | `sequence` — One supplied/defined long continuation after a close above both finished Asia and London highs and a later VWAP retest. |
| [M04](#m04) | GB-SCALP | `case_description` — One supplied directional scalp case; automatic full entry admission remains unknown. |
| [M05](#m05) | SIRES | `sequence` — One source-selected confirmed entry attempt within a live Sires thesis; separate units for incomplete cases, management actions and fresh re-entries. |
| [M06](#m06) | SAINT-AMT | `sequence` — One of Saint's four source routes with current HTF/LTF agreement. |
| [M07](#m07) | MEMBER-TWO-REASONS | `sequence` — One unnamed member attempt combining independently known reaction history and minor HVN at a preplanned confluence area. |
| [M08](#m08) | KEANI-OPEN-ABOVE-VALUE | `sequence` — One Keani long with whole A above prior VAH, later developing-value breakout and defended buying-imbalance retest. |
| [M09](#m09) | REFILL-STUDY | `touch_causality` — One already-identified source zone touch; separate supplied selected-order configuration rows. |
| [M10](#m10) | JETBUNDLE-STATES | `state_observation` — One source-defined or supplied B/A/D/E/W state; a separate next-state observation audit. |
| [M11](#m11) | STOIC-DATA | `process` — One declared research/process review block; macro application is a scoped additional process check. |
| [M12](#m12) | STOIC-RISK | `printed_ladder` — One supplied risk-stage decision under Stoic's printed illustration and prior-process validation. |


<a id="m01"></a>

## M01 — JJ-TBR

**Source of truth:** [JJumbo FX — SDRange / Time-Based Ranges](/workspace/planning/phase-1-live/wiki/method-jumbo-tbr.md). **Unit:** One source-selected TBR decision attempt, with one of its eight named branches.

**Required end-to-end behavior:** The entire selected context → frozen range → location → source confirmation → predeclared risk/objective sequence, followed by separate management and reference outcomes.

**Source-complete candidate discovery:** Unavailable without the source context/location/confirmation selectors. Literal ranges and projections can still be computed for covered windows.

**Branch inventory:** `judas_outbound`, `judas_reversal`, `single_extended`, `single_purged`, `internal_rotation`, `extension_reaction`, `other_session`, `timed_pzone_reversal`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Session and range geometry.** O005 Jumbo's 06:00–09:00 range; O006 Other time-based range formations; O007 Range EQ and quadrants; O008 Source range-open and range-close references; O009 Range width and expectations; O010 Retrospective range path; O011 Overnight high, low and width; O012 Chronological liquidity purges; O013 Opening location and participation; O014 Range exhaustion and mean-reversal area; O015 The 1.33–1.66 extension area; O016 Nested source range geometry; O017 Session Stat+ envelopes; O018 Jumbo EVRange; O019 Time-anchored P-zones; O020 PD RTH Range+ destinations; O021 Jumbo reversal and action windows; O022 Source session-cleanliness assessment; O023 Accumulation, manipulation and distribution phases; O024 Jumbo failure signatures and three attempts; O025 Opening-range midpoint reference; O026 Confirmed swing midpoint retrace; O027 Relative-volume context at the open; O028 Equal-high or equal-low liquidity objective.

**Regime and thesis context.** O029 Scheduled news and changing information.

**Price references and price-action confirmation.** O047 Sweep, failure and reclaim; O048 Prior day, week and month extremes; O050 09:30 cash-open price; O055 Fair-value gaps and higher-timeframe imbalances; O056 Jumbo orderblocks; O057 Jumbo rejection blocks; O058 Jumbo Absorption Zone+ candle.

**Auction and profile structure.** O061 Volume profile; O062 Profile value area; O063 Developing profile snapshot; O064 Profile point of control; O066 High-volume node; O067 Low-volume node; O068 Profile shelf; O069 Profile ledge; O073 Overnight volume structure; O075 ETH profile identity; O077 Signed volume-by-price profile; O086 Prior-session auction landmarks; O087 Remaining auction objectives; O088 Source-conditioned reference statistics.

**Order-flow evidence.** O098 Executed aggressor-side trades; O099 Big Trades aggression markers; O101 Absorption: effort without price reward; O107 Local delta concentration at an extreme; O120 Native candle footprint.

**Risk, objectives and process.** O139 Entry-side structural invalidation; O140 Exposure fitted to source risk constraints; O141 Objective selected before entry; O142 Source-selected position management; O145 Source account and session stop.

**Research, execution-study and risk records.** O150 Observed order lifecycle; O162 Economic observation and release vintage.

### M01 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `branch:enum` | [O005 — Jumbo's 06:00–09:00 range](#o005)<br>[O006 — Other time-based range formations](#o006) | The preselected source branch is exactly one of M01's eight names; unsupported names give sequence unknown. A final path label never selects this enum. |
| `decision_at:event_key?` | [O150 — Observed order lifecycle](#o150) | Actual source entry/decision, including the literal cash-open event for the outbound branch. A drawn anchor is not an entry. |
| `range_frozen:boolean?`<br>`range_known_at:event_key?` | [O005 — Jumbo's 06:00–09:00 range](#o005)<br>[O006 — Other time-based range formations](#o006)<br>[O007 — Range EQ and quadrants](#o007)<br>[O008 — Source range-open and range-close references](#o008) | Frozen means the selected source range interval, instrument, bounds and required geometry are complete and available. known_at is its real formation end/availability, never the start. |
| `context_fixed:boolean?`<br>`context_at:event_key?`<br>`directional_context:boolean?`<br>`reversal_context:boolean?`<br>`extended_context:boolean?`<br>`purged_compressed_context:boolean?`<br>`rotation_context:boolean?`<br>`reduced_expectations:boolean?`<br>`expansion_policy:boolean?` | [O009 — Range width and expectations](#o009)<br>[O011 — Overnight high, low and width](#o011)<br>[O012 — Chronological liquidity purges](#o012)<br>[O013 — Opening location and participation](#o013)<br>[O029 — Scheduled news and changing information](#o029)<br>[O027 — Relative-volume context at the open](#o027) | Validate a source-context record for this branch, with all reasons and selected risk/target policy already available before touch. Quantitative width/volume/open-cell measurements do not automatically generate qualitative extended/compressed/reversal/directional labels. Missing source selector/record yields the named field hole; final single/double-break outcome is prohibited as input. |
| `location_touched:boolean?`<br>`touch_at:event_key?` | [O002 — Touch, reject, hold and break measurements](#o002)<br>[O014 — Range exhaustion and mean-reversal area](#o014)<br>[O007 — Range EQ and quadrants](#o007) | Actual contact with the preselected branch location, using its exact band/line and C02/C06 ordering. First qualifying event key is retained; reference and context must already exist. |
| `source_confirmation:boolean?`<br>`confirm_at:event_key?`<br>`reaction_side_confirmed:boolean?` | [O056 — Jumbo orderblocks](#o056)<br>[O057 — Jumbo rejection blocks](#o057)<br>[O058 — Jumbo Absorption Zone+ candle](#o058)<br>[O099 — Big Trades aggression markers](#o099)<br>[O120 — Native candle footprint](#o120)<br>[O063 — Developing profile snapshot](#o063) | Select the actual source confirmation mode before scoring: full-C2 OB, rejection wick, printed candle feature or the specifically supplied local flow/profile read. Run that exact recipe and required conjunction for the case; never OR unrelated easiest flags. For outbound entry, the source opening-entry choice remains its own supplied/undefined selector, not a forced later reversal OB. confirm_at is the final required observation close/key. |
| `risk_defined:boolean?` | [O139 — Entry-side structural invalidation](#o139)<br>[O140 — Exposure fitted to source risk constraints](#o140) | Actual source invalidation and applicable exposure policy are fixed before decision, correct side/units, and supported by source structure. Missing general stop/size policy is a hole; small size alone is not confirmation. |
| `objective_fixed:boolean?`<br>`objective_is_selected_exhaustion:boolean?`<br>`objective_is_opposing_draw:boolean?`<br>`objective_is_range_edge:boolean?`<br>`objective_is_named_rotation_target:boolean?`<br>`objective_is_remaining_draw:boolean?` | [O141 — Objective selected before entry](#o141)<br>[O087 — Remaining auction objectives](#o087)<br>[O020 — PD RTH Range+ destinations](#o020)<br>[O028 — Equal-high or equal-low liquidity objective](#o028) | Require one preselected objective ID, source role/priority, original availability and active state. Compare its actual parent/type to the branch-required exhaustion/opposing/range-edge/rotation/remaining-draw role. Do not choose the nearest or later-hit target. RTH-only consumption remains source-scoped. |
| `at_rth_open:boolean?`<br>`exit_window_recorded:boolean?`<br>`source_time_window:boolean?` | [O050 — 09:30 cash-open price](#o050)<br>[O021 — Jumbo reversal and action windows](#o021) | Check actual 09:30 cash-open entry for outbound, and its source-recorded 09:40–09:50 exit framing. Other branches use their own cited action window; later P-zone examples are not universally forced into that manual interval. Exact unresolved endpoints are holes. |
| `edge_swept:boolean?`<br>`sweep_at:event_key?` | [O047 — Sweep, failure and reclaim](#o047)<br>[O014 — Range exhaustion and mean-reversal area](#o014) | Strict excursion beyond the selected frozen edge; retain actual first sweep time and depth. A touch is not a sweep and no universal exact 0.5W depth is required. |
| `entry_at_eq_or_quadrant:boolean?`<br>`entry_at_named_internal_or_ev_band:boolean?` | [O007 — Range EQ and quadrants](#o007)<br>[O018 — Jumbo EVRange](#o018)<br>[O016 — Nested source range geometry](#o016) | Compare actual selected entry/contact to its source internal line/band. Preserve EQ, quadrant, inner-span and EV identities. An EV engine hole cannot be filled by equal 6–9 midpoint geometry. |
| `purge_known_at:event_key?` | [O012 — Chronological liquidity purges](#o012) | Maximum known_at of the actual required earlier liquidity purges, each tied to an independently known reference and chronological sweep; no box-containment substitute. |
| `prior_expansion:boolean?`<br>`touch_in_source_extension_area:boolean?` | [O015 — The 1.33–1.66 extension area](#o015)<br>[O010 — Retrospective range path](#o010) | Prior expansion must have occurred before the source extension reaction; measure only the elapsed path. Contact uses the selected parent's exact 1.33/1.66 coordinate convention. Do not use final HOD/LOD to declare prior expansion or choose the parent. |
| `source_clock_verified:boolean?`<br>`source_case_verified:boolean?` | [O003 — Source clocks and availability](#o003)<br>[O006 — Other time-based range formations](#o006)<br>[O022 — Source session-cleanliness assessment](#o022) | Verify the actual other-session source formation/action clock, version and case linkage. A modern London source clock or cleanliness judgment not supplied remains unknown; no generic 00:00–03:00 or rolling-ten-day fallback. |
| `source_zone_known:boolean?`<br>`zone_known_at:event_key?`<br>`directed_path_recorded:boolean?` | [O019 — Time-anchored P-zones](#o019) | Require supplied source zone bounds/settings/active policy and true availability. Preserve the ordered source→destination path as linked IDs; the chart's arrow is not a price inequality and an anchor time is not a fill. |

### M01 predicate: sequence

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

### M01 acceptance fixtures

**M01-F1 — positive / declared scope.** Synthetic source-illustration judas_reversal: 06:00–09:00 range L100/H120, known 09:00; source reversal context fixed 09:20; high sweep 121 at 09:41; selected source rejection confirmation 09:43; short decision 09:44; risk above the case rejection structure and preselected opposing objective 100. All source-context/confirmation records carry synthetic evidence IDs, same band/side and actual known_at. The sequence passes its fixture; sweep depth is 0.05W and need not equal 0.5W.

**M01-F2 — negative controls.** Replace rejection with fully observed continued acceptance above 120: fail. Move purge/context evidence after 09:44: causal fail. Replace a projection parent with a different range: invalid identity/fail. No favorable later target can repair these.

**M01-F3 — source/data hole.** Remove source confirmation or a required P-zone/EV/Session Stat source value: unknown for that branch. Do not generate the missing engine.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m02"></a>

## M02 — GB-FAIL

**Source of truth:** [Green Bird — failed breakout / failed breakdown](/workspace/planning/phase-1-live/wiki/method-green-bird-failure.md). **Unit:** One identified failed-breakout/failed-breakdown attempt at its actual completed source reference.

**Required end-to-end behavior:** Frozen reference → relevant sweep → actual source failure/reclaim confirmation → optional case-specific confluence/retest → entry risk and preselected objective.

**Source-complete candidate discovery:** Complete five-minute comparisons are calculable for verified references; the full source session/bias/admission selector and several reference clocks remain holes.

**Branch inventory:** `nyam_box`, `previous_hour`, `asia_tdo_case`, `prior_day_level`, `prior_week_level`, `prior_month_level`, `cash_open_reclaim_case`, `mss_fvg_refinement`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Regime and thesis context.** O029 Scheduled news and changing information.

**Price references and price-action confirmation.** O046 Green Bird's finished session references; O047 Sweep, failure and reclaim; O048 Prior day, week and month extremes; O049 Green Bird's midnight true-day open; O050 09:30 cash-open price; O051 New-week opening gap; O052 Measured 50–61.8% retracement; O053 Premium / discount within a selected range; O054 Market-structure shift after failure; O055 Fair-value gaps and higher-timeframe imbalances; O059 Source setup quality and exposure.

**Auction and profile structure.** O086 Prior-session auction landmarks; O087 Remaining auction objectives.

**Risk, objectives and process.** O136 Green Bird's directional read; O139 Entry-side structural invalidation; O140 Exposure fitted to source risk constraints; O141 Objective selected before entry; O142 Source-selected position management; O145 Source account and session stop.

**Research, execution-study and risk records.** O150 Observed order lifecycle.

### M02 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `side:enum` | [O047 — Sweep, failure and reclaim](#o047) | Actual source attempt side. It chooses high-failure short versus low-reclaim long; unsupported source-specific mirrors remain holes. |
| `reference_frozen:boolean?`<br>`reference_known_at:event_key?`<br>`reference_px:decimal_price?` | [O046 — Green Bird's finished session references](#o046)<br>[O048 — Prior day, week and month extremes](#o048)<br>[O049 — Green Bird's midnight true-day open](#o049)<br>[O050 — 09:30 cash-open price](#o050) | Select the source box edge or single reference with completed formation, exact session/period identity and known_at. reference_px is the actual swept boundary, not the opposing edge or a later final box. |
| `bias_recorded:boolean?`<br>`context_at:event_key?` | [O136 — Green Bird's directional read](#o136) | Validate the candidate's source directional/context record and actual availability before sweep. A later prior-level or NYAM reclaim cannot supply earlier bias. |
| `source_session_allowed:boolean?` | [O046 — Green Bird's finished session references](#o046)<br>[O003 — Source clocks and availability](#o003) | The chosen reference and action interval belong to the cited source case. Incomplete/approximate Asia or unpublished London bounds are not silently author-exact; no hard-coded available-hour count. |
| `sweep_at:event_key?`<br>`sweep_high:decimal_price?`<br>`sweep_low:decimal_price?` | [O047 — Sweep, failure and reclaim](#o047) | Use the actual same-reference sweep episode and its observed extreme through the required confirmation, never the later morning extreme. For a short only sweep_high is required; for a long only sweep_low. Preserve irrelevant counterpart as not_required. |
| `confirmation_mode:enum` | [O047 — Sweep, failure and reclaim](#o047) | Choose the source's disclosed confirmation mode, not whichever passes. The cash-open partial example does not acquire a universal 5 minute rule. |
| `complete_clock_five_minute_bar:boolean?`<br>`confirm_at:event_key?`<br>`confirm_close:decimal_price?`<br>`source_hold_confirmed:boolean?` | [O047 — Sweep, failure and reclaim](#o047)<br>[O003 — Source clocks and availability](#o003) | Five-minute mode uses full aligned interval and close at interval end, with actual sweep before confirmation. Hold mode requires the source-observed reclaim/hold and its actual completion value/key; undisclosed automatic hold duration gives unknown. Do not group five available rows or stamp bar start. |
| `box_return_ok:boolean?` | [O046 — Green Bird's finished session references](#o046)<br>[O047 — Sweep, failure and reclaim](#o047) | For a selected box require the same confirmation back inside both frozen bounds under its source boundary convention. For a single line, return-inside-box is not_required and the composite gate is the logical identity true; retain that applicability instead of claiming a box observation. |
| `tdo_required:boolean?`<br>`source_tdo_close_confirmed:boolean?` | [O049 — Green Bird's midnight true-day open](#o049)<br>[O047 — Sweep, failure and reclaim](#o047) | tdo_required is fixed from the selected source variant. If required, its actual completed source close must cross the correct side of midnight TDO; if not required, no TDO observation is invented. Unknown applicability stays unknown. |
| `pocket_required:boolean?`<br>`impulse_known_at:event_key?`<br>`touch_at:event_key?`<br>`touch_in_measured_pocket:boolean?` | [O052 — Measured 50–61.8% retracement](#o052) | Required only in the selected measured-impulse case. Use the exact completed source impulse and subsequent band contact; down-impulse pocket is[L+0.5W, L+0.618W]. touch_at is this pocket contact when required, otherwise the source location contact. No 9–10 net-candle substitution. |
| `retracement_entry:boolean?`<br>`retest_at:event_key?` | [O047 — Sweep, failure and reclaim](#o047)<br>[O054 — Market-structure shift after failure](#o054)<br>[O055 — Fair-value gaps and higher-timeframe imbalances](#o055) | The source entry choice declares whether a later retest is required. Require actual retest after confirmation and before decision, with source MSS/FVG refinement when selected; unspecified construction stays a hole. |
| `risk_defined:boolean?`<br>`objective_fixed:boolean?`<br>`decision_at:event_key?` | [O139 — Entry-side structural invalidation](#o139)<br>[O141 — Objective selected before entry](#o141)<br>[O150 — Observed order lifecycle](#o150) | Use actual predeclared source stop and opposing/session/prior-level objective, then actual entry/decision. No universal stop beyond every sweep extreme; target outcome is measured separately after this decision. |

### M02 predicate: sequence

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

### M02 acceptance fixtures

**M02-F1 — positive / declared scope.** Synthetic NYAM box H110/L100 known 10:00, bias known 09:55, high sweep 111 at 10:01, clock-aligned complete 10:00–10:05 close 109, short decision 10:06, source risk 112 and opposing objective 100. tdo_required=false, pocket_required=false, retracement_entry=false because this selected fixture has no such requirements. Complete source evidence yields pass.

**M02-F2 — negative controls.** At 09:45 the final 09:00–10:00 box is unavailable: causal fail. Close 111 after sweep 111 remains outside: fail. A pocket touch without a failure fails. A fifth observed row at 10:06 cannot complete a missing 10:02 clock interval.

**M02-F3 — source/data hole.** Unspecified London/session clock, source hold detector, prior-period scope or stop policy → corresponding unknown. TDO is not universally mandatory.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m03"></a>

## M03 — GB-VWAP

**Source of truth:** [Green Bird — VWAP continuation](/workspace/planning/phase-1-live/wiki/method-green-bird-vwap-continuation.md). **Unit:** One supplied/defined long continuation after a close above both finished Asia and London highs and a later VWAP retest.

**Required end-to-end behavior:** Known finished session references → completed close above both highs → later source VWAP retest → long with predeclared risk.

**Source-complete candidate discovery:** Unavailable until source session bounds, breakout-bar definition, VWAP reset/basis and risk/admission evidence are supplied.

**Branch inventory:** `source_long`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Regime and thesis context.** O030 Session VWAP.

**Price references and price-action confirmation.** O046 Green Bird's finished session references.

**Risk, objectives and process.** O136 Green Bird's directional read; O139 Entry-side structural invalidation; O141 Objective selected before entry; O142 Source-selected position management.

**Research, execution-study and risk records.** O150 Observed order lifecycle.

### M03 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `reference_frozen:boolean?`<br>`london_high:decimal_price?`<br>`london_known_at:event_key?`<br>`asia_high:decimal_price?`<br>`asia_known_at:event_key?` | [O046 — Green Bird's finished session references](#o046) | Both source sessions must be finished and independently identified before breakout. Unpublished exact London or approximate Asia settings require supplied source bounds/clock evidence; no invented default. |
| `continuation_context:boolean?` | [O136 — Green Bird's directional read](#o136)<br>[O046 — Green Bird's finished session references](#o046) | Validate the source long continuation context after the above-both-highs break. Do not require an opposite-direction failure or Sires fade/tape gate. |
| `breakout_at:event_key?`<br>`breakout_close:decimal_price?` | [O004 — Source execution bars](#o004)<br>[O046 — Green Bird's finished session references](#o046) | Actual completed source breakout candle and its close. Source timeframe/inclusion must be supplied; not any intrabar high. Close must exceed both highs in the printed expression. |
| `vwap_reset_verified:boolean?`<br>`vwap_known_at:event_key?`<br>`vwap_at_retest:decimal_price?` | [O030 — Session VWAP](#o030) | Source reset/basis must be verified. Freeze the corresponding pre-retest VWAP snapshot from only available volume; named comparison resets cannot set verification true. |
| `retest_at:event_key?`<br>`retest_low:decimal_price?`<br>`retest_high:decimal_price?` | [O002 — Touch, reject, hold and break measurements](#o002)<br>[O030 — Session VWAP](#o030) | Actual later source retest observation/bar with L≤VWAP≤H. Require complete membership/availability and breakout before retest. No invented defended-retake condition is added beyond the source sequence. |
| `risk_defined:boolean?`<br>`decision_at:event_key?`<br>`side:enum` | [O139 — Entry-side structural invalidation](#o139)<br>[O150 — Observed order lifecycle](#o150) | Actual source pre-entry risk and long decision. General target is unpublished and is not added as an entry operand; reported 150 points is not a target recipe. |

### M03 predicate: sequence

```sql
reference_frozen AND continuation_context AND risk_defined
AND london_known_at <= breakout_at AND asia_known_at <= breakout_at
AND breakout_close > london_high AND breakout_close > asia_high
AND breakout_at < retest_at AND retest_at <= decision_at
AND vwap_reset_verified AND vwap_known_at <= retest_at
AND retest_low <= vwap_at_retest AND retest_high >= vwap_at_retest
AND side = 'long'
```

### M03 acceptance fixtures

**M03-F1 — positive / declared scope.** Synthetic supplied Asia H100 and London H102 known 08:00; source breakout candle closes 103 at 09:40; verified source VWAP 101.5 available before 09:45 retest bar L101/H102; long decision 09:46 with source risk 99. Both highs were exceeded and the retest straddles 101.5: pass for the supplied fixture.

**M03-F2 — negative controls.** Breakout close 101 is not above London H102: fail. A retest before breakout fails order. A short mirror fails side. Later 150 point reported gain cannot serve as target or confirmation.

**M03-F3 — source/data hole.** Remove verified source VWAP reset: unknown even if a 09:30-reset comparison VWAP exists. General target policy is separately unknown and does not become an added entry gate.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m04"></a>

## M04 — GB-SCALP

**Source of truth:** [Green Bird — directional scalps](/workspace/planning/phase-1-live/wiki/method-green-bird-directional-scalps.md). **Unit:** One supplied directional scalp case; automatic full entry admission remains unknown.

**Required end-to-end behavior:** Audit the disclosed directional read → favorable pullback/pop → small exposure → limited source management, preserving all undisclosed trigger/invalidation/exit fields.

**Source-complete candidate discovery:** No repeatable source-complete scalp selector is disclosed. Never create a two-box, VWAP or failure-trigger replacement.

**Branch inventory:** `bearish_small_scalp`, `bullish_discount_pullback`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Regime and thesis context.** O029 Scheduled news and changing information.

**Price references and price-action confirmation.** O046 Green Bird's finished session references; O053 Premium / discount within a selected range; O059 Source setup quality and exposure.

**Risk, objectives and process.** O136 Green Bird's directional read; O139 Entry-side structural invalidation; O140 Exposure fitted to source risk constraints; O141 Objective selected before entry; O142 Source-selected position management; O145 Source account and session stop.

**Research, execution-study and risk records.** O150 Observed order lifecycle.

### M04 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `direction_recorded_before_entry:boolean?` | [O136 — Green Bird's directional read](#o136) | Actual source direction and its evidence available before this scalp; compare with actual side. No direction chosen from outcome. |
| `small_size_recorded:boolean?` | [O059 — Source setup quality and exposure](#o059)<br>[O140 — Exposure fitted to source risk constraints](#o140) | Source explicitly describes/selects small exposure before entry; if actual policy amount is supplied, audit it. No universal contract count or fraction is inferred. |
| `source_directional_pullback_observed:boolean?` | [O053 — Premium / discount within a selected range](#o053) | Retain the actual source favorable pullback/pop and parent-range/value identity. Its unpublished impulse/entry selector remains a hole for automatic admission. |
| `source_scalp_management_recorded:boolean?` | [O142 — Source-selected position management](#o142)<br>[O145 — Source account and session stop](#o145) | Source small scalp/limited ambition/session restraint is recorded with actual action times. This audits disclosed case behavior only; automatic full sequence is NULL regardless of a favorable case outcome. |

### M04 predicate: case_description

```sql
direction_recorded_before_entry AND small_size_recorded
AND source_directional_pullback_observed AND source_scalp_management_recorded
```

### M04 predicate: automatic_admission

```sql
NULL
```

### M04 acceptance fixtures

**M04-F1 — positive / declared scope.** Synthetic case: bearish direction recorded 09:30, supplied favorable pop 09:40, deliberately small size 1 contract declared 09:39, short 09:41 and supplied limited 20 point scalp-management reference. The case-description expression can pass; automatic sequence_ok stays NULL. The 20 point value illustrates the cited 20–30 point source case, not a new general target.

**M04-F2 — negative controls.** Direction first recorded after entry or opposite to the actual scalp makes the claimed case fail. A large-size entry cannot satisfy an explicitly supplied small-size policy merely because it won.

**M04-F3 — source/data hole.** Full trigger, measured-impulse selection, general invalidation and exit algorithm are holes in every automatic scalp-admission result.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m05"></a>

## M05 — SIRES

**Source of truth:** [Sires — thesis, risk and order flow](/workspace/planning/phase-1-live/wiki/method-sires-thesis-flow.md). **Unit:** One source-selected confirmed entry attempt within a live Sires thesis; separate units for incomplete cases, management actions and fresh re-entries.

**Required end-to-end behavior:** Version/model and account box → current auction/regime → thesis/death → allowed location → exactly one complete execution branch → structural risk/objective → supported management/re-entry → versioned review.

**Source-complete candidate discovery:** Most automatic selectors are source-incomplete: current auction bands, context, local qualitative flow, range bars, CVD reference, proprietary levels and full account journals. Implement their explicit holes, not substitutes.

**Branch inventory:** `dom_rejection`, `absorption_reward_retest`, `stop_four_stage`, `footprint_confirmed_reaction`, `vwap_deviation_fade`, `ofm_aggressive`, `ofm_passive`, `clean_squeeze`, `balance_failure_fade`, `defended_band_continuation`, `microbalance_break`, `kg1_retest`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Session and range geometry.** O011 Overnight high, low and width; O013 Opening location and participation.

**Regime and thesis context.** O029 Scheduled news and changing information; O030 Session VWAP; O031 Anchored VWAP; O032 VWAP deviation bands; O033 Source gamma regime; O034 Native options-chain identity; O035 Gamma-flip reference; O036 Gamma call and put walls; O037 Source max-pain reference; O038 Source Vol Trigger readout; O039 Source VOL-GEX readout; O040 Source hedging-pressure gauge; O041 Source KG1 level; O042 VIX and volatility context; O043 Volatility-implied daily-move estimate; O044 Volatility term structure and event change; O045 VVIX context.

**Price references and price-action confirmation.** O050 09:30 cash-open price; O053 Premium / discount within a selected range; O059 Source setup quality and exposure.

**Auction and profile structure.** O060 Auction balance; O061 Volume profile; O062 Profile value area; O063 Developing profile snapshot; O064 Profile point of control; O065 Untested prior POC; O066 High-volume node; O067 Low-volume node; O068 Profile shelf; O069 Profile ledge; O070 Composite auction profiles; O071 Source-selected dealing range; O072 Prior defended reaction area; O073 Overnight volume structure; O074 Overnight directional inventory; O075 ETH profile identity; O076 MPOC: the profile midpoint; O077 Signed volume-by-price profile; O078 Time-price-opportunity profile; O079 TPO single-print structure; O080 TPO excess at auction extremes; O081 TPO poor high and poor low; O082 Initial balance; O083 Developing auction open type; O084 Developing auction day structure; O085 Profile shape and trade permission; O086 Prior-session auction landmarks; O087 Remaining auction objectives; O088 Source-conditioned reference statistics.

**Auction routes inside a method.** O090 Rotation within accepted balance; O091 Accepted break and defended boundary retest; O092 Re-acceptance into value; O093 Sires's narrower Failed Auction setup; O095 POC failure versus efficient passage; O096 Whole-balance traversal with one side in control; O097 Higher- and lower-timeframe control alignment.

**Order-flow evidence.** O098 Executed aggressor-side trades; O099 Big Trades aggression markers; O100 DOM at a planned location; O101 Absorption: effort without price reward; O102 Executed passive replenishment; O103 Iceberg evidence and added participation; O104 Price reward near the absorption origin; O105 Cumulative volume delta and its source reference; O106 Candle direction versus executed delta; O107 Local delta concentration at an extreme; O108 POC relocation within a candle; O109 Diagonal footprint imbalance stacks; O110 Same-price 350% imbalance display; O111 Speed of tape; O112 Bid-ask spread; O113 How price arrives at the area; O114 Aggressor print-size thinning; O115 Absorber becomes aggressive and price lifts off; O116 Zone formed by aggressive prints; O117 Memory of earlier zone tests; O118 Origin-of-the-Move catalyst; O119 Trapped aggression at an auction extreme; O120 Native candle footprint.

**Execution branches within Sires's loop.** O121 At-level DOM rejection; O122 Four-check absorption reversal; O123 Defense, replenishment, exhaustion and lift-off; O124 Footprint-confirmed reaction; O125 Confirmed VWAP deviation fade; O126 Aggressive Origin of the Move; O127 Passive Origin-of-the-Move variant; O128 Clean squeeze continuation; O129 Failure of aggression in long-gamma balance; O130 Fresh defense of a continuation band; O131 Price-defined microbalance continuation; O132 KG1 retest and subsequent trailing; O133 Deliberate pre-confirmation attempts; O134 Third support test without new buyer defense; O135 Late small resistance-fade case.

**Risk, objectives and process.** O137 Declared model and review version; O138 Thesis, validity band and death condition; O139 Entry-side structural invalidation; O140 Exposure fitted to source risk constraints; O141 Objective selected before entry; O142 Source-selected position management; O143 Confirmed protected high or low; O144 Freshly qualified re-entry; O145 Source account and session stop; O146 Thesis and execution journal; O147 Triad AMT-object first use: IØD and RFZ.

**Research, execution-study and risk records.** O148 Frozen observation cohort; O150 Observed order lifecycle; O152 Trading and account costs; O153 Outcome distribution of a declared process; O162 Economic observation and release vintage.

**Auction-state observation.** O164 Aggressive effort versus price-response efficiency.

### M05 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `decision_at:event_key?`<br>`side:enum` | [O150 — Observed order lifecycle](#o150) | Actual source decision and trade side. Each confirmed branch, incomplete case, management action and re-entry has its own typed unit/ID; do not pool them. |
| `thesis_alive:boolean?`<br>`thesis_dead:boolean?`<br>`thesis_known_at:event_key?` | [O138 — Thesis, validity band and death condition](#o138)<br>[O029 — Scheduled news and changing information](#o029)<br>[O147 — Triad AMT-object first use: IØD and RFZ](#o147) | Replay the declared structure/value/news death conditions with available data. thesis_dead is the known dead state, not a default inverse of missing data; unknown remains unknown. Record first death and native-object revisions. Stop-out alone is not thesis death. |
| `auction_route_ok:boolean?` | [O090 — Rotation within accepted balance](#o090)<br>[O091 — Accepted break and defended boundary retest](#o091)<br>[O092 — Re-acceptance into value](#o092)<br>[O093 — Sires's narrower Failed Auction setup](#o093)<br>[O096 — Whole-balance traversal with one side in control](#o096)<br>[O073 — Overnight volume structure](#o073)<br>[O083 — Developing auction open type](#o083)<br>[O084 — Developing auction day structure](#o084) | Exactly one source-selected auction-to-objective route is required. Execute its own O recipe and current context; preserve source holes in acceptance/selection. No OR across unrelated route stages and no final-day label as current permission. |
| `branch_regime_allowed:boolean?`<br>`short_gamma:boolean?`<br>`long_gamma:boolean?` | [O033 — Source gamma regime](#o033)<br>[O034 — Native options-chain identity](#o034)<br>[O035 — Gamma-flip reference](#o035)<br>[O042 — VIX and volatility context](#o042) | Use the actual source-native pre-choice regime. BIG aggressive OFM requires short gamma; BIG balance-failure fade requires long gamma. Other branches use their own cited permissions/uncertainty. If a source branch does not require a gamma filter, record not_required and use logical identity for that gate, not fabricated positive gamma evidence. Unknown source applicability/regime stays unknown. |
| `location_fixed:boolean?`<br>`location_touched:boolean?`<br>`real_extreme:boolean?`<br>`at_valid_level:boolean?`<br>`location_known_at:event_key?`<br>`level_known_at:event_key?`<br>`touch_at:event_key?` | [O071 — Source-selected dealing range](#o071)<br>[O060 — Auction balance](#o060)<br>[O072 — Prior defended reaction area](#o072)<br>[O066 — High-volume node](#o066)<br>[O067 — Low-volume node](#o067)<br>[O069 — Profile ledge](#o069)<br>[O032 — VWAP deviation bands](#o032)<br>[O002 — Touch, reject, hold and break measurements](#o002) | Use the actual source chosen band and its pre-touch availability/contact. real_extreme is the source fixed outer extreme, with strict absorption's POC/middle exclusion; at_valid_level is the selected source route's permission. level_known_at aliases the actual selected footprint/KG1 level as appropriate, never the nearest final profile line. No universal automated band selector is disclosed. |
| `objective_fixed:boolean?`<br>`risk_defined:boolean?` | [O141 — Objective selected before entry](#o141)<br>[O139 — Entry-side structural invalidation](#o139)<br>[O140 — Exposure fitted to source risk constraints](#o140) | The selected source HTF destination/priority and structural invalidation/exposure are fixed and available before decision. Missing source stop/size/target policies stay holes. No fixed 15/35 tick ticket default or attractive R:R structure invention. |
| `sires_branch_ok:boolean?` | [O121 — At-level DOM rejection](#o121)<br>[O122 — Four-check absorption reversal](#o122)<br>[O123 — Defense, replenishment, exhaustion and lift-off](#o123)<br>[O124 — Footprint-confirmed reaction](#o124)<br>[O125 — Confirmed VWAP deviation fade](#o125)<br>[O126 — Aggressive Origin of the Move](#o126)<br>[O127 — Passive Origin-of-the-Move variant](#o127)<br>[O128 — Clean squeeze continuation](#o128)<br>[O129 — Failure of aggression in long-gamma balance](#o129)<br>[O130 — Fresh defense of a continuation band](#o130)<br>[O131 — Price-defined microbalance continuation](#o131)<br>[O132 — KG1 retest and subsequent trailing](#o132) | Evaluate exactly the named branch SQL body below, with this candidate's operands only. Unknown branch gives NULL. All 12 confirmed branches have separate rows; incomplete cases are not alternative true branches. |
| `confirm_at:event_key?` | [O004 — Source execution bars](#o004) | Maximum actual availability of the selected branch's required local confirmation stages. It is not the first touch/bar start. Every required stage also retains its own key below. |
| `arriving_aggression:boolean?`<br>`little_progress:boolean?`<br>`local_rejection:boolean?`<br>`source_dom_confirmation:boolean?`<br>`aggression_at:event_key?`<br>`rejection_at:event_key?` | [O121 — At-level DOM rejection](#o121)<br>[O100 — DOM at a planned location](#o100)<br>[O101 — Absorption: effort without price reward](#o101)<br>[O102 — Executed passive replenishment](#o102)<br>[O103 — Iceberg evidence and added participation](#o103) | Use same-band arriving effort, its actual limited response, observed rejection and the specific selected DOM lesson's extra confirmation. BBO reload remains an inference; required hidden/off-touch/participant evidence missing yields unknown. aggression_at and rejection_at are the corresponding actual local events. |
| `passive_wall_confirmed:boolean?`<br>`opposing_effort_no_result:boolean?`<br>`own_reward_confirmed:boolean?`<br>`reward_near_origin:boolean?`<br>`fresh_reward_retest_defended:boolean?`<br>`absorption_at:event_key?`<br>`reward_at:event_key?` | [O122 — Four-check absorption reversal](#o122)<br>[O101 — Absorption: effort without price reward](#o101)<br>[O102 — Executed passive replenishment](#o102)<br>[O104 — Price reward near the absorption origin](#o104) | Strict reversal requires actual passive defense against opposing effort, new-side price reward near the true origin, then fresh defended reward-area return. Distance/reference conventions not printed remain holes. absorption_at precedes reward_at; retest_at below is the later reward-area test. No first AM-print origin or continuation-push substitution. |
| `cvd_filter_ok:boolean?`<br>`delta_filter_ok:boolean?` | [O105 — Cumulative volume delta and its source reference](#o105)<br>[O098 — Executed aggressor-side trades](#o098) | Apply the source selected same-unit directional/reference relation to corrected signed executions, with verified reset and causal reference. The unpublished CVD median/reference or source filter is a hole unless supplied. Do not compare CVD to a price median, use candle-sign volume, or initialize missing confirmation true. |
| `defense:boolean?`<br>`replenishment:boolean?`<br>`opponent_thinning:boolean?`<br>`absorber_aggressive:boolean?`<br>`lift_off:boolean?`<br>`defense_at:event_key?`<br>`replenish_at:event_key?`<br>`exhaust_at:event_key?`<br>`liftoff_at:event_key?` | [O123 — Defense, replenishment, exhaustion and lift-off](#o123)<br>[O102 — Executed passive replenishment](#o102)<br>[O114 — Aggressor print-size thinning](#o114)<br>[O115 — Absorber becomes aggressive and price lifts off](#o115) | Current local STOP stages only: passive defense, executed refresh, opposing print exhaustion and defender becoming aggressive with real displacement. Map replenish_at to actual refresh, exhaust_at to source exhaustion completion, liftoff_at to actual own-side rewarded initiative. Preserve source instrument digit classes and verified order; no reused prior-attempt stages. |
| `reward_ticks:decimal_ticks?`<br>`entry_distance_ticks:decimal_ticks?`<br>`daily_r_before:decimal_source_R?` | [O104 — Price reward near the absorption origin](#o104)<br>[O115 — Absorber becomes aggressive and price lifts off](#o115)<br>[O145 — Source account and session stop](#o145) | Reward uses actual source origin andq; entry distance is absolute distance from the actual confirmation price divided byq. daily_r_before uses only prior resolved source account results with its fixed R definition. The STOP expression enforces 2–4, 0–2 and>-4 literally; other branches do not inherit these limits. |
| `candle_delta_disagreement:boolean?`<br>`local_absorption:boolean?`<br>`intrabar_poc_flip:boolean?`<br>`source_flow_confirmation:boolean?`<br>`flip_at:event_key?` | [O124 — Footprint-confirmed reaction](#o124)<br>[O106 — Candle direction versus executed delta](#o106)<br>[O108 — POC relocation within a candle](#o108)<br>[O120 — Native candle footprint](#o120) | Same native candle and source location throughout: opposite candle/delta signs, local source absorption, POC relocation inside that candle, selected local DOM/delta confirmation. flip_at is later intrabar snapshot availability. Adjacent-candle and whole AM substitutes fail. |
| `source_vwap_known:boolean?`<br>`selected_deviation_touched:boolean?`<br>`absorption_at_that_band:boolean?`<br>`ladder_confirmation:boolean?`<br>`band_known_at:event_key?` | [O125 — Confirmed VWAP deviation fade](#o125)<br>[O030 — Session VWAP](#o030)<br>[O031 — Anchored VWAP](#o031)<br>[O032 — VWAP deviation bands](#o032)<br>[O100 — DOM at a planned location](#o100) | Source-compatible VWAP reset/basis/deviation and pre-touch frozen band, actual selected deviation contact, local absorption/rejection at that band and actual ladder confirmation. Unpublished reset/variance construction propagates unknown. band_known_at is the actual used snapshot's availability. |
| `repeated_effort_no_reward:boolean?`<br>`first_squeeze:boolean?`<br>`squeeze_failed:boolean?`<br>`catalyst_reclaimed:boolean?`<br>`refill_held:boolean?`<br>`initiative_drive:boolean?`<br>`intervening_wicks_taken:boolean?`<br>`drive_retest_defended:boolean?`<br>`own_aggression_rewarded:boolean?`<br>`catalyst_at:event_key?`<br>`first_release_at:event_key?`<br>`failure_at:event_key?`<br>`refill_at:event_key?`<br>`drive_at:event_key?` | [O126 — Aggressive Origin of the Move](#o126)<br>[O118 — Origin-of-the-Move catalyst](#o118)<br>[O116 — Zone formed by aggressive prints](#o116)<br>[O099 — Big Trades aggression markers](#o099)<br>[O110 — Same-price 350% imbalance display](#o110) | Bind every aggressive OFM stage to one catalyst/side: formation, first release, actual failed squeeze, return/refill, wick-taking initiative drive, held refill and defended drive retest with own reward. Each temporal alias is the actual corresponding event. failure_at for passive/fade branches instead uses their own named failure event; never reuse another branch's failure. Missing display/cluster rules stay holes rather than substituted constants. |
| `source_squeeze_failed:boolean?`<br>`tape_died_at_failure:boolean?`<br>`no_aggression_at_failure:boolean?`<br>`buyers_area_identified:boolean?`<br>`entry_above_buyers:boolean?`<br>`stop_below_aggression:boolean?`<br>`entry_trigger_at:event_key?` | [O127 — Passive Origin-of-the-Move variant](#o127)<br>[O111 — Speed of tape](#o111)<br>[O139 — Entry-side structural invalidation](#o139) | The passive source long has failure while tape dies without aggressive orders, a known buyers' area, entry above it and stop below source aggression. Numeric pace/no-aggression selectors are unpublished; supplied source observations required. entry_trigger_at is the actual above-area trigger; do not require aggressive failure prints or a universal gamma sign. |
| `catalyst_known:boolean?`<br>`fast_release:boolean?`<br>`no_prior_squeeze_failure:boolean?`<br>`first_pullback:boolean?`<br>`opposing_pullback_aggression_absorbed:boolean?`<br>`continuation_confirmed:boolean?`<br>`release_at:event_key?`<br>`pullback_at:event_key?` | [O128 — Clean squeeze continuation](#o128)<br>[O118 — Origin-of-the-Move catalyst](#o118)<br>[O111 — Speed of tape](#o111)<br>[O101 — Absorption: effort without price reward](#o101) | Known catalyst, source fast release, actual first pullback with opposing absorption and continuation. No-prior-failure covers only already-observed history through decision under a defined source failure criterion; no future survival window. release_at/pullback_at are the actual source events, not favorable later substitutes. |
| `balance_context:boolean?`<br>`failed_aggression_at_extreme:boolean?`<br>`left_failed_area:boolean?`<br>`retest_same_failed_area:boolean?`<br>`aggression_still_unrewarded:boolean?`<br>`target_is_prior_opposite_control:boolean?`<br>`leave_at:event_key?` | [O129 — Failure of aggression in long-gamma balance](#o129)<br>[O060 — Auction balance](#o060)<br>[O101 — Absorption: effort without price reward](#o101)<br>[O141 — Objective selected before entry](#o141) | Source long-gamma balance fade requires unpaid effort at a real extreme, actual departure, same-area return and still-unpaid aggression. leave_at is that departure. Target ID must be where the opposite side previously controlled; an opposite 6–9 edge is not an automatic alias. No own-reward requirement is added. |
| `prior_band_control:boolean?`<br>`same_band_retest:boolean?`<br>`fresh_same_side_defense:boolean?`<br>`executed_aggression:boolean?`<br>`refresh_consistent:boolean?`<br>`control_side_matches_thesis:boolean?`<br>`prior_defense_at:event_key?` | [O130 — Fresh defense of a continuation band](#o130)<br>[O072 — Prior defended reaction area](#o072)<br>[O116 — Zone formed by aggressive prints](#o116)<br>[O102 — Executed passive replenishment](#o102)<br>[O098 — Executed aggressor-side trades](#o098) | Earlier control at the exact band, actual return, new same-side executed defense/refill under source consistency criteria, and current control still matching live thesis. prior_defense_at is earlier observed control; fresh confirmation is new. A supported break/flip is a new source decision, not ignored to preserve the old short. |
| `microbalance_frozen:boolean?`<br>`directional_strength:boolean?`<br>`breakout_in_thesis_direction:boolean?`<br>`stop_behind_microbalance:boolean?`<br>`microbalance_known_at:event_key?`<br>`breakout_at:event_key?` | [O131 — Price-defined microbalance continuation](#o131)<br>[O139 — Entry-side structural invalidation](#o139) | Source-selected small balance completed before actual strong break in live thesis direction; stop behind source opposite side and pre-existing HTF objective. Source strength/box selectors are holes where missing. The last detected box/final AM close cannot supply earlier breakout. |
| `source_kg1_level_known:boolean?`<br>`kg1_retest:boolean?`<br>`aggression_confirms:boolean?` | [O132 — KG1 retest and subsequent trailing](#o132)<br>[O041 — Source KG1 level](#o041) | Actual provider/source KG1 level known before its retest and observed aggressive confirmation. Generic gamma wall cannot fill source KG1. Its trailing actions are separate and the undisclosed engines remain holes. |
| `retest_at:event_key?` | [O122 — Four-check absorption reversal](#o122)<br>[O126 — Aggressive Origin of the Move](#o126)<br>[O129 — Failure of aggression in long-gamma balance](#o129)<br>[O130 — Fresh defense of a continuation band](#o130)<br>[O132 — KG1 retest and subsequent trailing](#o132) | Resolve from the selected branch's actual retest ID: rewarded-area retest, drive retest, failed-area return, continuation-band return or KG1 retest. Retest objects may share a timestamp but not be merged by same-day proximity. Missing required return in a fully observed admitted attempt is false; missing definition/data is unknown. |
| `preconfirmation_entry:boolean?`<br>`small_risk_declared:boolean?`<br>`stop_predefined:boolean?`<br>`explicitly_early_entry:boolean?`<br>`source_refill_return:boolean?`<br>`source_risk_predefined:boolean?` | [O133 — Deliberate pre-confirmation attempts](#o133)<br>[O139 — Entry-side structural invalidation](#o139)<br>[O140 — Exposure fitted to source risk constraints](#o140) | These belong only to incomplete case-description predicates. Require actual deliberate early choice, already defined source small risk/stop, and actual earlier OFM refill return when selected. No automatic early admission is supplied and these cannot set a confirmed branch true. |
| `same_support_band:boolean?`<br>`distinct_test_count:integer?`<br>`no_new_buyer_defense:boolean?` | [O134 — Third support test without new buyer defense](#o134)<br>[O117 — Memory of earlier zone tests](#o117)<br>[O100 — DOM at a planned location](#o100) | Literal third-test case: one frozen band, three distinct departure/return episodes and observed lack of fresh buyer defense on current test. Do not hard-code zero defense or count adjacent bars. General entry selector remains unknown. |
| `resistance_known_before_approach:boolean?`<br>`upward_approach_loses_aggression:boolean?` | [O135 — Late small resistance-fade case](#o135)<br>[O113 — How price arrives at the area](#o113)<br>[O120 — Native candle footprint](#o120) | Actual late case premarked resistance and source upward approach with declining candle-by-candle aggression before small short. Preserve actual chart direction and missing quantitative exhaustion/timing rule. |
| `action_at:event_key?`<br>`action_matches_preselected_policy:boolean?`<br>`supporting_structure_known_at:event_key?`<br>`stop_trailed:boolean?`<br>`protected_structure_confirmed:boolean?`<br>`risk_added:boolean?`<br>`earlier_risk_secured:boolean?`<br>`exit_or_new_thesis_recorded:boolean?` | [O142 — Source-selected position management](#o142)<br>[O143 — Confirmed protected high or low](#o143)<br>[O140 — Exposure fitted to source risk constraints](#o140)<br>[O150 — Observed order lifecycle](#o150)<br>[O138 — Thesis, validity band and death condition](#o138) | Observed management action after entry, matched to policy selected before entry. Supporting record is the actual required source structure, or the already known static policy/reference when no new structure is required. Trailing needs a confirmed protected structure; an add needs earlier risk secured under the source policy. If thesis dies, actual exit/replacement must be recorded. Neither requested fill nor unconfirmed wick changes exposure. |
| `same_band_id:boolean?`<br>`price_back_inside_band:boolean?`<br>`fresh_confirmation_after_stopout:boolean?`<br>`prior_exit_at:event_key?`<br>`fresh_confirmation_at:event_key?`<br>`daily_limit_allows_entry:boolean?` | [O144 — Freshly qualified re-entry](#o144)<br>[O145 — Source account and session stop](#o145)<br>[O138 — Thesis, validity band and death condition](#o138) | For a new candidate require identical still-valid thesis/band identity, actual return, prior real exit before all required fresh branch confirmation and new decision, plus current account permission. same_band_id is a Boolean equality check, not an arbitrary nonempty string. Preserve prior losses and rerun full branch; do not reuse prior confirmation. |

### M05 predicate: sequence

```sql
thesis_alive AND auction_route_ok AND branch_regime_allowed
AND location_fixed AND location_touched AND objective_fixed AND risk_defined
AND thesis_known_at <= touch_at AND location_known_at <= touch_at
AND touch_at <= confirm_at AND confirm_at <= decision_at
AND sires_branch_ok
```

### M05 predicate: management

```sql
action_at > decision_at
AND action_matches_preselected_policy
AND supporting_structure_known_at <= action_at
AND (NOT stop_trailed OR protected_structure_confirmed)
AND (NOT risk_added OR earlier_risk_secured)
AND (NOT thesis_dead OR exit_or_new_thesis_recorded)
```

### M05 predicate: reentry

Conjoin this with the full current selected entry branch; earlier confirmation cannot be reused.

```sql
same_band_id AND thesis_alive AND price_back_inside_band
AND fresh_confirmation_after_stopout
AND prior_exit_at < fresh_confirmation_at
AND fresh_confirmation_at <= decision_at
AND daily_limit_allows_entry
```

### M05 exact branch bodies

Set `sires_branch_ok` to exactly one of these bodies according to the preselected branch. There is no cross-branch OR. All stage keys refer to the same candidate, side, instrument and source band/catalyst; the corresponding O recipe adds its literal source-geometry and evidence checks.

**dom_rejection**

```sql
arriving_aggression AND little_progress AND local_rejection AND source_dom_confirmation AND aggression_at <= rejection_at AND rejection_at <= decision_at
```

**absorption_reward_retest**

```sql
real_extreme AND passive_wall_confirmed AND opposing_effort_no_result AND own_reward_confirmed AND reward_near_origin AND cvd_filter_ok AND fresh_reward_retest_defended AND absorption_at < reward_at AND reward_at < retest_at AND retest_at <= decision_at
```

**stop_four_stage**

```sql
real_extreme AND defense AND replenishment AND opponent_thinning AND absorber_aggressive AND delta_filter_ok AND lift_off AND reward_ticks BETWEEN 2 AND 4 AND entry_distance_ticks BETWEEN 0 AND 2 AND daily_r_before > -4 AND defense_at < replenish_at AND replenish_at <= exhaust_at AND exhaust_at < liftoff_at AND liftoff_at <= decision_at
```

**footprint_confirmed_reaction**

```sql
at_valid_level AND candle_delta_disagreement AND local_absorption AND intrabar_poc_flip AND source_flow_confirmation AND level_known_at <= absorption_at AND absorption_at <= flip_at AND flip_at <= decision_at
```

**vwap_deviation_fade**

```sql
source_vwap_known AND selected_deviation_touched AND absorption_at_that_band AND cvd_filter_ok AND ladder_confirmation AND band_known_at <= touch_at AND touch_at <= confirm_at
```

**ofm_aggressive**

```sql
short_gamma AND repeated_effort_no_reward AND first_squeeze AND squeeze_failed AND catalyst_reclaimed AND refill_held AND initiative_drive AND intervening_wicks_taken AND drive_retest_defended AND own_aggression_rewarded AND cvd_filter_ok AND catalyst_at < first_release_at AND first_release_at < failure_at AND failure_at <= refill_at AND refill_at < drive_at AND drive_at < retest_at AND retest_at <= decision_at
```

**ofm_passive**

```sql
source_squeeze_failed AND tape_died_at_failure AND no_aggression_at_failure AND buyers_area_identified AND entry_above_buyers AND stop_below_aggression AND failure_at < entry_trigger_at AND entry_trigger_at <= decision_at
```

**clean_squeeze**

```sql
catalyst_known AND fast_release AND no_prior_squeeze_failure AND first_pullback AND opposing_pullback_aggression_absorbed AND continuation_confirmed AND catalyst_at < release_at AND release_at < pullback_at AND pullback_at <= confirm_at
```

**balance_failure_fade**

```sql
long_gamma AND balance_context AND failed_aggression_at_extreme AND left_failed_area AND retest_same_failed_area AND aggression_still_unrewarded AND target_is_prior_opposite_control AND failure_at < leave_at AND leave_at < retest_at AND retest_at <= decision_at
```

**defended_band_continuation**

```sql
prior_band_control AND same_band_retest AND fresh_same_side_defense AND executed_aggression AND refresh_consistent AND control_side_matches_thesis AND prior_defense_at < retest_at AND retest_at <= confirm_at
```

**microbalance_break**

```sql
microbalance_frozen AND directional_strength AND breakout_in_thesis_direction AND stop_behind_microbalance AND microbalance_known_at < breakout_at AND breakout_at <= decision_at
```

**kg1_retest**

```sql
source_kg1_level_known AND kg1_retest AND aggression_confirms AND level_known_at <= retest_at AND retest_at <= confirm_at
```

### M05 incomplete source cases

These expressions are `case_description` only. Their automatic full entry selector remains NULL, and they are excluded from the confirmed-entry headline denominator.

**pre_file_early**

```sql
thesis_alive AND preconfirmation_entry AND small_risk_declared AND stop_predefined
```

**third_retest_case**

```sql
same_support_band AND distinct_test_count = 3 AND no_new_buyer_defense AND side = 'short' AND risk_defined
```

**late_resistance_fade_case**

```sql
resistance_known_before_approach AND upward_approach_loses_aggression AND side = 'short' AND small_risk_declared
```

**ofm_early_refill_case**

```sql
source_refill_return AND explicitly_early_entry AND source_risk_predefined
```

### M05 acceptance fixtures

**M05-F1 — positive / declared scope.** Synthetic defended_band_continuation: source short thesis/band [109, 110] known 09:20 and still alive under supplied death rules; valid auction route/regime evidence before touch; prior seller defense 09:30; same-band return 09:45; fresh seller executions/refill and source refresh/control confirmation 09:47; short decision 09:48 with predeclared stop 111 and target 103. All identities and supporting assertions are supplied in synthetic mode. Full selected branch passes.

**M05-F2 — negative controls.** Use a 09:30 defense as the fresh 09:47 confirmation: fail. For aggressive OFM, omit release/failure/refill or enter before drive/retest: fail. For strict absorption reversal, remove own reward/reward retest: fail. For long-gamma balance fade, do not invent an own-reward gate. STOP entry at daily R=-4 fails.

**M05-F3 — source/data hole.** Missing exact CVD reference, source state/refresh criterion, full required depth, gamma/KG1 readout or thesis death input → unknown. Incomplete early/third-test/late-fade cases remain case-description rows and do not enter confirmed-branch n.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m06"></a>

## M06 — SAINT-AMT

**Source of truth:** [Saint — AMT on live markets](/workspace/planning/phase-1-live/wiki/method-saint-amt.md). **Unit:** One of Saint's four source routes with current HTF/LTF agreement.

**Required end-to-end behavior:** Actual HTF balance/profile permission → read arrival → wait for present LTF control → complete selected route/retest → source structural risk and objective.

**Source-complete candidate discovery:** Automatic source balance/control/acceptance/arrival selectors and some profile conventions are incomplete; supplied source cases are auditable.

**Branch inventory:** `continuation_retest`, `trapped_buyers_retest`, `failed_auction_return`, `poc_traversal`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Auction and profile structure.** O060 Auction balance; O061 Volume profile; O062 Profile value area; O063 Developing profile snapshot; O064 Profile point of control; O066 High-volume node; O067 Low-volume node; O068 Profile shelf; O071 Source-selected dealing range; O077 Signed volume-by-price profile; O084 Developing auction day structure; O085 Profile shape and trade permission; O089 Saint's Asia-range target context.

**Auction routes inside a method.** O090 Rotation within accepted balance; O091 Accepted break and defended boundary retest; O092 Re-acceptance into value; O094 Saint's failed auction and return to value; O095 POC failure versus efficient passage; O097 Higher- and lower-timeframe control alignment.

**Order-flow evidence.** O098 Executed aggressor-side trades; O100 DOM at a planned location; O101 Absorption: effort without price reward; O102 Executed passive replenishment; O107 Local delta concentration at an extreme; O113 How price arrives at the area; O119 Trapped aggression at an auction extreme; O120 Native candle footprint.

**Risk, objectives and process.** O139 Entry-side structural invalidation; O141 Objective selected before entry; O142 Source-selected position management.

**Research, execution-study and risk records.** O150 Observed order lifecycle.

**Auction-state observation.** O164 Aggressive effort versus price-response efficiency.

### M06 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `branch:enum`<br>`side:enum`<br>`decision_at:event_key?` | [O097 — Higher- and lower-timeframe control alignment](#o097)<br>[O150 — Observed order lifecycle](#o150) | Exactly one of Saint's four routes and the actually sourced direction; actual decision/entry. The trapped-buyers case is the published short, and an opposite mirror needs explicit source evidence. |
| `balance_fixed_before_use:boolean?`<br>`balance_known_at:event_key?`<br>`profile_allows_trade:boolean?` | [O060 — Auction balance](#o060)<br>[O062 — Profile value area](#o062)<br>[O085 — Profile shape and trade permission](#o085)<br>[O084 — Developing auction day structure](#o084) | Actual HTF balance/profile snapshot selected before arrival, with Saint's own source permission. Unbalanced trending profile requires rebalance; no Sires trend permission is borrowed. Source 68% value is separate from 70%/40% and balance is not automatically VA. |
| `arrival_read_recorded:boolean?`<br>`arrival_at:event_key?`<br>`control_evidence_recorded:boolean?`<br>`control_at:event_key?`<br>`alignment_ok:boolean?` | [O113 — How price arrives at the area](#o113)<br>[O097 — Higher- and lower-timeframe control alignment](#o097)<br>[O120 — Native candle footprint](#o120)<br>[O100 — DOM at a planned location](#o100) | Record actual aggressive/drifting arrival then current LTF control at the HTF area. HTF permission and current side must agree before decision. Free two-sided chop is not confirmed control. Qualitative detector/source timeframe gaps remain holes. |
| `risk_defined:boolean?`<br>`objective_fixed:boolean?` | [O139 — Entry-side structural invalidation](#o139)<br>[O141 — Objective selected before entry](#o141)<br>[O089 — Saint's Asia-range target context](#o089) | Source structural stop/exposure and actual objective/ambition known before entry. Saint's Asia context is not Sires overnight-inventory clock or a fixed range fraction. |
| `ltf_balance_broken:boolean?`<br>`ltf_balance_known_at:event_key?`<br>`breakout_at:event_key?`<br>`same_boundary_retest_held:boolean?`<br>`repeated_aggression_in_trade_direction:boolean?`<br>`retest_at:event_key?`<br>`confirm_at:event_key?` | [O091 — Accepted break and defended boundary retest](#o091)<br>[O097 — Higher- and lower-timeframe control alignment](#o097)<br>[O120 — Native candle footprint](#o120)<br>[O100 — DOM at a planned location](#o100) | Use actual current LTF structure, break and same-boundary held retest, then repeated source aggression in trade direction. Unknown strength/hold duration stays unknown. breakout_at/retest_at/confirm_at alias the selected route's actual events, never unrelated earlier historical failures. |
| `prior_buying_at_upper_extreme:boolean?`<br>`two_distinct_prior_failures:boolean?`<br>`prior_failures_known_at:event_key?`<br>`ltf_break_down:boolean?`<br>`repeated_body_selling:boolean?` | [O119 — Trapped aggression at an auction extreme](#o119)<br>[O107 — Local delta concentration at an extreme](#o107)<br>[O120 — Native candle footprint](#o120) | Preserve distinct earlier AM/PM failed-buying episodes at the known HTF upper area, with max prior resolution time. Current breakdown/retest and repeated body selling remain fresh requirements. A duplicated AM high is one failure, not two; Sires diagonal-stack settings are not a required Saint threshold. |
| `older_value_tested:boolean?`<br>`older_value_rejected:boolean?`<br>`older_value_known_at:event_key?`<br>`older_value_touch_at:event_key?`<br>`rejection_at:event_key?`<br>`original_balance_reaccepted:boolean?`<br>`reaccept_at:event_key?`<br>`local_control_confirms_return:boolean?` | [O094 — Saint's failed auction and return to value](#o094)<br>[O092 — Re-acceptance into value](#o092)<br>[O097 — Higher- and lower-timeframe control alignment](#o097) | Two source area identities: tested lower/older value known before exploration, actual failure/rejection, original balance reaccepted, current local control confirms return. Keep the full deep/time-consuming live sequence. Sires instant older POC tag is not a universal prerequisite here. |
| `aggressive_poc_passage:boolean?`<br>`source_poc_hold_confirmed:boolean?`<br>`target_is_far_balance_edge:boolean?`<br>`poc_passage_at:event_key?` | [O095 — POC failure versus efficient passage](#o095)<br>[O064 — Profile point of control](#o064)<br>[O141 — Objective selected before entry](#o141) | Actual aggressive passage of the original profile's POC after reacceptance, held/retested under the selected source convention, then preselected far balance edge. Repeated POC failure is a different read. Later far edge reach cannot label earlier passage efficient. |

### M06 predicate: sequence

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

### M06 acceptance fixtures

**M06-F1 — positive / declared scope.** Synthetic trapped_buyers_retest: source upper HTF area 110 defined yesterday; distinct earlier AM/PM buying failures known yesterday; current LTF balance breaks down 09:45, retests same boundary 09:50, repeated body selling and DOM/current short control confirm 09:52, short 09:53 with predefined risk and objective. Prior failures and all current stages precede entry: pass.

**M06-F2 — negative controls.** Duplicate one prior failure as two: fail distinctness. Enter during free two-sided chop before current control: fail when fully observed. Remove actual retest from a chased attempt: fail. Do not require Sires's older-POC instant-rejection rule for every Saint failed auction.

**M06-F3 — source/data hole.** Missing source current control, exact source profile/balance selection or required acceptance/hold procedure → unknown. Saint 68% value remains distinct from Sires 70%/40% settings.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m07"></a>

## M07 — MEMBER-TWO-REASONS

**Source of truth:** [Unnamed member — reaction area plus minor HVN](/workspace/planning/phase-1-live/wiki/method-member-two-reasons.md). **Unit:** One unnamed member attempt combining independently known reaction history and minor HVN at a preplanned confluence area.

**Required end-to-end behavior:** Conditional thesis/objective/risk → independently identified reaction band and minor HVN → actual planned-band contact → current source rejection or buyers absorbing/holding → entry.

**Source-complete candidate discovery:** Automatic source reaction/node selection and exact local confirmation/risk policies are incomplete. KG1 is optional additional context, not a replacement for either reason.

**Branch inventory:** `resistance_short`, `planned_return_long`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Regime and thesis context.** O041 Source KG1 level.

**Auction and profile structure.** O060 Auction balance; O061 Volume profile; O062 Profile value area; O064 Profile point of control; O066 High-volume node; O070 Composite auction profiles; O071 Source-selected dealing range; O072 Prior defended reaction area; O086 Prior-session auction landmarks; O087 Remaining auction objectives.

**Auction routes inside a method.** O097 Higher- and lower-timeframe control alignment.

**Order-flow evidence.** O098 Executed aggressor-side trades; O101 Absorption: effort without price reward.

**Risk, objectives and process.** O138 Thesis, validity band and death condition; O139 Entry-side structural invalidation; O140 Exposure fitted to source risk constraints; O141 Objective selected before entry; O142 Source-selected position management; O146 Thesis and execution journal.

**Research, execution-study and risk records.** O148 Frozen observation cohort; O150 Observed order lifecycle; O152 Trading and account costs; O153 Outcome distribution of a declared process.

### M07 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `thesis_predefined:boolean?`<br>`objective_fixed:boolean?`<br>`risk_defined:boolean?`<br>`decision_at:event_key?`<br>`side:enum` | [O138 — Thesis, validity band and death condition](#o138)<br>[O141 — Objective selected before entry](#o141)<br>[O139 — Entry-side structural invalidation](#o139)<br>[O140 — Exposure fitted to source risk constraints](#o140)<br>[O150 — Observed order lifecycle](#o150) | Actual member conditional thesis, objective and source risk before decision; no universal Sires death/delta/reward engine is inherited. Preserve actual instrument and stop/target provenance. |
| `prior_reaction_area_known:boolean?`<br>`area_known_at:event_key?`<br>`independent_minor_hvn_known:boolean?`<br>`hvn_known_at:event_key?` | [O072 — Prior defended reaction area](#o072)<br>[O066 — High-volume node](#o066)<br>[O070 — Composite auction profiles](#o070) | Independently identified earlier reaction history and source minor HVN, each known before current touch. Two labels for one line are not independent evidence. Automatic band/node selectors remain holes when unpublished. |
| `confluence_band_defined:boolean?`<br>`actual_band_contact:boolean?`<br>`touch_at:event_key?` | [O071 — Source-selected dealing range](#o071)<br>[O072 — Prior defended reaction area](#o072)<br>[O066 — High-volume node](#o066)<br>[O002 — Touch, reject, hold and break measurements](#o002) | Use the actual preplanned source confluence area and explicitly linked reaction/HVN parents. Literal overlap/distance can be measured, but no unsourced tolerance or automatic intersection-only selector is invented. Require actual contact with that selected area. |
| `resistance_rejection:boolean?`<br>`reaction_at:event_key?`<br>`stop_above_rejection_high:boolean?` | [O072 — Prior defended reaction area](#o072)<br>[O139 — Entry-side structural invalidation](#o139) | For the source short, observe current resistance rejection before decision and actual stop strictly above its source rejection high. Rejection detector/band choice requires source evidence; no extra tick buffer is assumed. |
| `planned_return_to_structure:boolean?`<br>`buyers_absorb_and_hold:boolean?`<br>`stop_behind_long_invalidation:boolean?` | [O072 — Prior defended reaction area](#o072)<br>[O101 — Absorption: effort without price reward](#o101)<br>[O139 — Entry-side structural invalidation](#o139) | For the source long, actual preplanned return and current buyers absorbing/holding at that structure, with the chosen source stop behind long invalidation. Do not add Sires's separate own-reward/lift-off/CVD/defended-reward-retest gate. Conflicting target prose/ticket stays a separate policy hole. |

### M07 predicate: sequence

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

### M07 acceptance fixtures

**M07-F1 — positive / declared scope.** Synthetic prior reaction band [100, 102] and independently sourced minor HVN [101, 103] known 09:30; source-selected confluence band [101, 102]; contact 101.5 at 09:45, supplied resistance rejection high 102 at 09:47, short decision 101.5 at 09:48 with source stop 102.25 and objective 98. The two reasons, actual contact and source short stop relation pass.

**M07-F2 — negative controls.** Reuse one resistance line as both independent reasons: fail/identity hole. No actual band contact or stop below the short rejection high fails. A later HVN cannot explain an earlier entry.

**M07-F3 — source/data hole.** Source target prose/ticket conflict is kept as a separate target-policy hole. The long case needs buyers absorbing/holding; do not import Sires's four-check lift-off gate.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m08"></a>

## M08 — KEANI-OPEN-ABOVE-VALUE

**Source of truth:** [Keani — open above value](/workspace/planning/phase-1-live/wiki/method-keani-open-above-value.md). **Unit:** One Keani long with whole A above prior VAH, later developing-value breakout and defended buying-imbalance retest.

**Required end-to-end behavior:** Prior VA fixed → complete A entirely above prior VAH → observe developing value higher/source rejection → break current VAH with aggressive buy imbalance → defend actual imbalance band with DOM → time/risk/objective check → long.

**Source-complete candidate discovery:** Exact source value/imbalance settings, near 10:00 timing tolerance, automatic developing-value/control selectors and source risk/target records are incomplete.

**Branch inventory:** `source_long`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Session and range geometry.** O013 Opening location and participation.

**Price references and price-action confirmation.** O050 09:30 cash-open price.

**Auction and profile structure.** O060 Auction balance; O061 Volume profile; O062 Profile value area; O063 Developing profile snapshot; O064 Profile point of control; O078 Time-price-opportunity profile; O086 Prior-session auction landmarks; O087 Remaining auction objectives.

**Auction routes inside a method.** O091 Accepted break and defended boundary retest; O097 Higher- and lower-timeframe control alignment.

**Order-flow evidence.** O098 Executed aggressor-side trades; O100 DOM at a planned location; O109 Diagonal footprint imbalance stacks; O120 Native candle footprint.

**Risk, objectives and process.** O139 Entry-side structural invalidation; O141 Objective selected before entry; O142 Source-selected position management.

**Research, execution-study and risk records.** O150 Observed order lifecycle.

### M08 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `prior_value_fixed:boolean?`<br>`prior_vah:decimal_price?` | [O062 — Profile value area](#o062)<br>[O086 — Prior-session auction landmarks](#o086) | Yesterday's actual source VAH and settings, fixed/known before current A. Do not substitute the whole prior range or today's developing boundary. |
| `a_period_complete:boolean?`<br>`a_low:decimal_price?`<br>`a_end_at:event_key?` | [O078 — Time-price-opportunity profile](#o078)<br>[O003 — Source clocks and availability](#o003) | A is the whole 09:30–10:00ET source period. Require full coverage, a_low=min price overall of A and a_end_at=10:00 availability. a_low>prior_vah is strict: equality does not pass. Open above VAH alone is insufficient. |
| `developing_value_builds_higher:boolean?`<br>`source_rejection_observed:boolean?`<br>`observation_at:event_key?` | [O063 — Developing profile snapshot](#o063)<br>[O062 — Profile value area](#o062)<br>[O097 — Higher- and lower-timeframe control alignment](#o097) | Source observed higher-building current value and its rejection/control evidence after whole A completes and before the later breakout. Exact migration/rejection detector is unpublished; use supplied source evidence or return hole, never final profile. |
| `dev_vah_known_at:event_key?`<br>`dev_vah_at_break:decimal_price?`<br>`breakout_at:event_key?`<br>`breakout_close:decimal_price?` | [O063 — Developing profile snapshot](#o063)<br>[O062 — Profile value area](#o062)<br>[O004 — Source execution bars](#o004) | Freeze developing VAH at the actual pre break snapshot, then use the actual completed source breakout candle. This boundary is distinct from prior VAH and cannot move retrospectively to fit the break. |
| `aggressive_buy_imbalance_break:boolean?`<br>`imbalance_band_known_at:event_key?` | [O109 — Diagonal footprint imbalance stacks](#o109)<br>[O120 — Native candle footprint](#o120)<br>[O098 — Executed aggressor-side trades](#o098) | Source aggressive buying at the current VAH break defines the actual imbalance band under its native candle/grid/ratio/run settings. Missing exact settings stay holes; do not manufacture a generic 3 row/4X stack from inconsistent highlights. |
| `retest_at:event_key?`<br>`defense_at:event_key?`<br>`buyers_defend_same_imbalance_band:boolean?`<br>`dom_supports_long:boolean?` | [O091 — Accepted break and defended boundary retest](#o091)<br>[O100 — DOM at a planned location](#o100) | After breakout require actual return to that same buying-imbalance band and fresh buyer defense with DOM support. Source qualitative hold/refresh criteria remain required evidence; unrelated later VAH touch cannot fill the band retest. |
| `time_of_day_allowed:boolean?`<br>`objective_fixed:boolean?`<br>`risk_defined:boolean?`<br>`decision_at:event_key?`<br>`side:enum` | [O003 — Source clocks and availability](#o003)<br>[O141 — Objective selected before entry](#o141)<br>[O139 — Entry-side structural invalidation](#o139)<br>[O150 — Observed order lifecycle](#o150) | The source near 10:00 timing is retained with its exact case clock; no universal tolerance is invented. Target/risk must be already selected, actual decision after defense, and side is long. General VAL short mirror is not sourced. |

### M08 predicate: sequence

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

### M08 acceptance fixtures

**M08-F1 — positive / declared scope.** Synthetic prior VAH 100, whole A 09:30–10:00 low 101, so 101>100; source developing value higher/rejection observation 10:01; frozen developing VAH 104 known 10:02; breakout close 105 at 10:05 with supplied buying-imbalance band [104, 104.5]; retest 10:07, buyer defense/DOM 10:08, long decision 10:09 with source timing/risk/objective. With all supplied source conventions this passes.

**M08-F2 — negative controls.** Whole A low 99.75 even if open 101: fail. Use prior VAH as the later moving VAH or retest another band: invalid/false. Entry before 10:00 cannot know whole A. Short mirror is not published and fails side.

**M08-F3 — source/data hole.** Unknown exact source near 10:00 timing convention or diagonal settings stays unknown; do not select a minute tolerance or a developing VAL short mirror.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m09"></a>

## M09 — REFILL-STUDY

**Source of truth:** [Sires × Team VOT — The Refill Effect](/workspace/planning/phase-1-live/wiki/method-refill-effect.md). **Unit:** One already-identified source zone touch; separate supplied selected-order configuration rows.

**Required end-to-end behavior:** Frozen source zone → departure → distinct return → strictly causal pre-touch construction/memory/location/flow → later label; if supplied, audit frozen grade/order/bracket/fill/cost records and preserve the later causal correction.

**Source-complete candidate discovery:** Source cluster/normalization, hold label, grade transformations/model and complete order lifecycle are missing. Do not train a grader, choose later days or turn a useful grade into an entry strategy.

**Branch inventory:** `touch_record`, `supplied_selected_order`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Auction and profile structure.** O060 Auction balance; O061 Volume profile; O062 Profile value area; O064 Profile point of control; O072 Prior defended reaction area.

**Order-flow evidence.** O098 Executed aggressor-side trades; O099 Big Trades aggression markers; O100 DOM at a planned location; O111 Speed of tape; O113 How price arrives at the area; O116 Zone formed by aggressive prints; O117 Memory of earlier zone tests.

**Risk, objectives and process.** O138 Thesis, validity band and death condition; O140 Exposure fitted to source risk constraints; O141 Objective selected before entry; O142 Source-selected position management.

**Research, execution-study and risk records.** O148 Frozen observation cohort; O149 Supplied refill-touch grade; O150 Observed order lifecycle; O151 Refill-study fill assumption; O152 Trading and account costs; O153 Outcome distribution of a declared process; O156 Refill-study evaluation-risk scenarios.

### M09 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `zone_definition_recorded:boolean?`<br>`zone_frozen:boolean?`<br>`zone_known_at:event_key?`<br>`instrument_and_threshold_preserved:boolean?` | [O116 — Zone formed by aggressive prints](#o116)<br>[O099 — Big Trades aggression markers](#o099) | Source zone construction, side/instrument/threshold/normalization and frozen bounds are recorded with true availability. Missing cluster engine or NQ/MNQ conversion stays hole; old 100/2 minute/2 tick variant cannot fill it. |
| `departure_observed:boolean?`<br>`departure_at:event_key?`<br>`distinct_touch_id:boolean?`<br>`touch_at:event_key?` | [O116 — Zone formed by aggressive prints](#o116)<br>[O148 — Frozen observation cohort](#o148)<br>[O002 — Touch, reject, hold and break measurements](#o002) | Actual departure after formation then actual distinct return. distinct_touch_id verifies persistent unique episode identity, not merely an arbitrary non empty string. Repeated inside rows are one contact. |
| `thesis_recorded:boolean?` | [O138 — Thesis, validity band and death condition](#o138) | Actual source thesis context is recorded before the touch/order use. A grade is not an independent entry method and cannot replace the thesis. |
| `feature_max_known_at:event_key?`<br>`memory_uses_only_prior_resolved_touches:boolean?`<br>`label_uses_only_post_touch_observations:boolean?` | [O117 — Memory of earlier zone tests](#o117)<br>[O148 — Frozen observation cohort](#o148)<br>[O149 — Supplied refill-touch grade](#o149) | Compute maximum actual feature availability. Every memory label must come from earlier touches resolved by the feature cutoff. Current touch label uses only later observations and is never a feature for itself. The SQL≤touch relation does not permit future response inside a pre-touch feature; tied order must be verified. Missing label definition remains a source hole even when its timingis auditable. |
| `grade_model_frozen_before_touch:boolean?`<br>`grade_available_at:event_key?`<br>`touch_selected_without_future_information:boolean?` | [O149 — Supplied refill-touch grade](#o149)<br>[O148 — Frozen observation cohort](#o148) | Audit only a supplied frozen model/grade and exact selection rule with training/model/features available before order. Later day selection or future current touch outcome is causal fail. No classifier training or threshold search. |
| `order_at:event_key?`<br>`order_inside_ticks:decimal_ticks?`<br>`stop_ticks:decimal_ticks?`<br>`target_ticks:decimal_ticks?`<br>`cancel_minutes:decimal_minutes?`<br>`one_position_policy:boolean?` | [O150 — Observed order lifecycle](#o150) | Use supplied actual/model source order record:12 inside, 32 stop, 96 target, 30 minute cancel and one position at a time. Retain exact inside-anchor/sign and cancel anchor; if undefined, measured tick distance is unknown rather than guessed. Different authors do not inherit these values. |
| `round_trip_cost_ticks:decimal_ticks?`<br>`stop_slippage_ticks:decimal_ticks?`<br>`fill_assumption_recorded:boolean?` | [O152 — Trading and account costs](#o152)<br>[O151 — Refill-study fill assumption](#o151) | Record source 1 tick round trip and 1 tick stop slippage, plus declared touch-or-through modeled fill. Queue/actual fill is not proven by price contact. This is configuration/causality audit, not new P&L. |

### M09 predicate: touch_causality

```sql
zone_definition_recorded AND zone_frozen AND departure_observed
AND zone_known_at < departure_at AND departure_at < touch_at
AND distinct_touch_id AND thesis_recorded
AND feature_max_known_at <= touch_at
AND memory_uses_only_prior_resolved_touches
AND label_uses_only_post_touch_observations
AND instrument_and_threshold_preserved
```

### M09 predicate: selected_order_configuration

This is additionally conjoined with the parent touch-causality verdict for a supplied selected-order record; its denominator is selected orders, not all touches.

```sql
grade_model_frozen_before_touch AND grade_available_at <= order_at
AND touch_selected_without_future_information
AND order_inside_ticks = 12 AND stop_ticks = 32 AND target_ticks = 96
AND cancel_minutes = 30 AND one_position_policy
AND round_trip_cost_ticks = 1 AND stop_slippage_ticks = 1
AND fill_assumption_recorded
```

### M09 acceptance fixtures

**M09-F1 — positive / declared scope.** Synthetic supplied zone [100, 101] known 09:40, departure 102 at 09:45, distinct touch 10:00, all features known 09:59, prior defense resolved 09:42, later label resolved 10:10. This touch-causality record passes. A separate supplied order fixture preserves 12/32/96 ticks, 30 minute cancel, one position, 1 tick cost and 1 tick stop slippage.

**M09-F2 — negative controls.** Include 10:10 current-touch outcome in 09:59 memory: causal fail. Use a later-day selection or future-trained grade for the order: fail. Treat 312 signals and 64 fills as paired trades: cohort failure.

**M09-F3 — source/data hole.** No supplied frozen grader/grade or exact source zone/side definition → unknown. Headline primary measures touch-record causality, not profitability; later-OFM negative causal rebuild must remain visible.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m10"></a>

## M10 — JETBUNDLE-STATES

**Source of truth:** [jetbundle — participation and auction states](/workspace/planning/phase-1-live/wiki/method-jetbundle-auction-states.md). **Unit:** One source-defined or supplied B/A/D/E/W state; a separate next-state observation audit.

**Required end-to-end behavior:** Native provide/withdraw/consume events → same-interval response/liquidity evidence → source heuristic state → later next state with conditioning known at current state.

**Source-complete candidate discovery:** The framework applies to native NQ or another declared instrument. AAPL's ten-level sample is an illustration, not an instrument or universal depth requirement ([MATH] pp.3, 10, 16; user clarification 2026-09-12). Complete automatic classifier/window/threshold definitions remain absent. Native event and depth coverage must support the selected observation scope; missing cancellations or off-touch depth cannot be invented. No automatic classifier is claimed by this source-faithful contract.

**Branch inventory:** `B`, `A`, `D`, `E`, `W`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability; O004 Source execution bars.

**Order-flow evidence.** O098 Executed aggressor-side trades; O100 DOM at a planned location; O101 Absorption: effort without price reward; O102 Executed passive replenishment; O103 Iceberg evidence and added participation; O111 Speed of tape; O112 Bid-ask spread.

**Auction-state observation.** O163 Provide, withdraw and consume events; O164 Aggressive effort versus price-response efficiency; O165 B–A–D–E–W auction-state alphabet; O166 Conditioned next-state transition.

### M10 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `participation_record_complete:boolean?`<br>`participation_known_at:event_key?` | [O163 — Provide, withdraw and consume events](#o163) | Actual provide/cancel/consume events for the declared native instrument and local scope, with required ordering. Record `required_depth_levels` before the observation and require actual `depth_levels` to cover it. NQ is permitted; neither ten levels nor AAPL is a universal gate. Incomplete native action/lifecycle evidence or an off-touch level still yields its specific data hole. |
| `response_record_complete:boolean?`<br>`response_known_at:event_key?` | [O164 — Aggressive effort versus price-response efficiency](#o164) | Same-local-interval price/mid response and opposite liquidity evidence, all available by current state. Completeness does not invent an exact efficiency classifier. |
| `state:enum`<br>`state_at:event_key?` | [O165 — B–A–D–E–W auction-state alphabet](#o165) | Supplied source heuristic label and actual observation key. Unknown automatic threshold/window/priority rules mean raw automatic label NULL. A supplied illustration is explicitly labeled and never promoted to an unbiased NQ cohort. |
| `two_sided_executions:boolean?`<br>`recent_revisits:boolean?`<br>`low_aggression_both_sides:boolean?` | [O165 — B–A–D–E–W auction-state alphabet](#o165)<br>[O163 — Provide, withdraw and consume events](#o163) | B state requires all source qualitative facts:two-sided executions, frequent recent revisits and low aggression on both sides. No published visit window/low threshold; source evidence or hole for each. |
| `high_aggression:boolean?`<br>`low_response_efficiency:boolean?`<br>`opposite_liquidity_holds_and_refills:boolean?` | [O165 — B–A–D–E–W auction-state alphabet](#o165)<br>[O164 — Aggressive effort versus price-response efficiency](#o164)<br>[O102 — Executed passive replenishment](#o102) | A state needs actual higher effort, little response and persistent opposite hold/refill in the same interval. Large volume alone and BBO hypothesis cannot fill missing full source evidence/thresholds. |
| `aggression:boolean?`<br>`efficient_displacement:boolean?` | [O165 — B–A–D–E–W auction-state alphabet](#o165)<br>[O164 — Aggressive effort versus price-response efficiency](#o164) | D state requires source effort with efficient actual displacement; no automatic ratio cutoff or fade entry follows. |
| `prior_absorption_or_effort:boolean?`<br>`replenishment_stops:boolean?`<br>`level_gives_way:boolean?` | [O165 — B–A–D–E–W auction-state alphabet](#o165)<br>[O102 — Executed passive replenishment](#o102) | Estate preserves prior observed effort, then actual replenishment failure and level giving way by current state. Future next state cannot provide these earlier facts. |
| `cancellations_dominate:boolean?` | [O165 — B–A–D–E–W auction-state alphabet](#o165)<br>[O163 — Provide, withdraw and consume events](#o163) | W state needs actual native cancellation evidence and the source dominance criterion. Static display change and missing cancels cannot be hard-coded false or true. |
| `next_state_at:event_key?`<br>`conditioning_known_at:event_key?` | [O166 — Conditioned next-state transition](#o166)<br>[O111 — Speed of tape](#o111) | Actual next source observation under the declared cadence after current state. Conditioning liquidity/pace must already be known at current state; unresolved adjacency/tied order remains unknown. No new transition matrix is trained. |

### M10 predicate: state_observation

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

### M10 predicate: transition_observation

Conjoin this with valid current/next supplied state observations and the declared adjacency/cohort checks.

```sql
state_at < next_state_at AND conditioning_known_at <= state_at
```

### M10 acceptance fixtures

**M10-F1 — positive / declared scope.** Synthetic supplied A state at 10:00 with complete local executed effort, low response and verified opposite holding/refill, all known 10:00, satisfies its observation expression. A next state at 10:01 with conditioning frozen 09:59 can pass the transition-timing audit.

**M10-F2 — negative controls.** W state with unobserved cancellations cannot be passed from displayed imbalance. Conditioning first known 10:00:30 for state 10:00 is causal fail. Same-time unresolved next state order is unknown. Do not transfer printed AAPL84%/12% values to NQ.

**M10-F3 — source/data hole.** Missing source depth/cancel data or heuristic thresholds → automatic state unknown. There is no entry-admission predicate beyond this observation method.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m11"></a>

## M11 — STOIC-DATA

**Source of truth:** [Stoic — data engine / quantifying fundamentals](/workspace/planning/phase-1-live/wiki/method-stoic-data-engine.md). **Unit:** One declared research/process review block; macro application is a scoped additional process check.

**Required end-to-end behavior:** Freeze reproducible process/inclusion → collect all observations uniformly → separate inputs/outcomes → record supplied aggregate winner/loser comparison → revise using completed prior sample; macro application adds vintages/history/declared rules.

**Source-complete candidate discovery:** The full trading recipe, macro series/transforms/C-score/cycle/trend-strength classifiers and decision thresholds are unpublished. Audit supplied process records; do not invent a trading or current macro model.

**Branch inventory:** `process_review`, `macro_application`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability.

**Regime and thesis context.** O029 Scheduled news and changing information.

**Risk, objectives and process.** O137 Declared model and review version; O146 Thesis and execution journal.

**Research, execution-study and risk records.** O148 Frozen observation cohort; O153 Outcome distribution of a declared process; O157 Stoic's macro indicator set; O158 Stoic's macro-cycle classification; O159 Stoic's custom C-score; O160 Historical-average and standardized-deviation comparison; O161 Stoic's trend-strength measure; O162 Economic observation and release vintage.

### M11 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `process_spec_frozen:boolean?`<br>`spec_known_at:event_key?`<br>`sample_start_at:event_key?`<br>`inclusion_rule_fixed:boolean?`<br>`uniform_schema:boolean?` | [O137 — Declared model and review version](#o137)<br>[O148 — Frozen observation cohort](#o148) | Immutable declared process/inclusion and typed collection schema before the first sample observation. Verify actual freeze and first sample times, not retroactive version labels. Missing underlying trading recipe is not invented. |
| `all_eligible_observations_retained:boolean?`<br>`features_available_before_decisions:boolean?`<br>`outcomes_separated_from_inputs:boolean?` | [O148 — Frozen observation cohort](#o148)<br>[O146 — Thesis and execution journal](#o146) | Join every frozen eligible ID, including losers/misses/breaches, to uniform records. Verify each feature dependency known by its decision and separate post decision outcomes. Current target hit cannot select the cohort. |
| `aggregate_winner_loser_comparison_recorded:boolean?` | [O153 — Outcome distribution of a declared process](#o153)<br>[O146 — Thesis and execution journal](#o146) | Record the supplied aggregate comparison using all declared groups and its metric definitions. No new P&L backtest is required; screenshots/selected winners are insufficient. |
| `revision_uses_only_prior_sample:boolean?` | [O137 — Declared model and review version](#o137)<br>[O148 — Frozen observation cohort](#o148) | The actual revision record references only completed, available earlier observations and creates a new version. Do not relabel previous inputs or use future block results. |
| `release_vintages_recorded:boolean?`<br>`historical_comparison_defined:boolean?`<br>`cycle_and_indicator_rules_recorded:boolean?` | [O162 — Economic observation and release vintage](#o162)<br>[O157 — Stoic's macro indicator set](#o157)<br>[O158 — Stoic's macro-cycle classification](#o158)<br>[O159 — Stoic's custom C-score](#o159)<br>[O160 — Historical-average and standardized-deviation comparison](#o160)<br>[O161 — Stoic's trend-strength measure](#o161) | Additional macro application requires actual point-in-time vintages, predeclared history comparison and complete/supplied source cycle/indicator rules. The unpublished custom engines remain holes; a named generic z-score cannot replace C-score and historical bubble verdict is not a current call. |

### M11 predicate: process

```sql
process_spec_frozen AND spec_known_at < sample_start_at
AND inclusion_rule_fixed AND uniform_schema
AND all_eligible_observations_retained
AND features_available_before_decisions
AND outcomes_separated_from_inputs
AND aggregate_winner_loser_comparison_recorded
AND revision_uses_only_prior_sample
```

### M11 predicate: macro_application

Conjoin this with the parent process expression for the specifically selected macro application.

```sql
release_vintages_recorded AND historical_comparison_defined AND cycle_and_indicator_rules_recorded
```

### M11 acceptance fixtures

**M11-F1 — positive / declared scope.** Synthetic process v 1 frozen January 1 before sample January 2–31; eligible IDs 1–100 all retained in one schema; features known before their decisions; outcomes stored separately; comparison recorded February 1; v 2 revision February 2 uses only that completed block. The process expression passes.

**M11-F2 — negative controls.** Drop 20 losing observations: fail. Freeze inclusion after January 31 outcomes: causal fail. A macro input revised in March cannot fill a January decision. A custom C-score cannot be replaced by z-score.

**M11-F3 — source/data hole.** Missing series/vintages or custom metric/cycle rules leaves macro application unknown while separately complete process-record checks may be reported.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


<a id="m12"></a>

## M12 — STOIC-RISK

**Source of truth:** [Stoic — asymmetric compounding](/workspace/planning/phase-1-live/wiki/method-stoic-asymmetric-compounding.md). **Unit:** One supplied risk-stage decision under Stoic's printed illustration and prior-process validation.

**Required end-to-end behavior:** Prior≥100 trade validation and known win rate/average RR/Monte Carlo loss streak → fixed baseline≤1% → risk 1 for 3R → after closed+3 risk 4 for 3R → reset 1 after second+12.

**Source-complete candidate discovery:** Only printed-stage arithmetic is reconstructable. Activation heading conflicts with ladder; generic rebasing/other-outcome transitions and Monte Carlo construction are unpublished.

**Branch inventory:** `first`, `second`, `reset_after_second_win`. Branch identifiers used only for transport do not create additional operating methods.

**Objects already named by the method:**

**Observation foundations.** O001 Evidence and data coverage; O002 Touch, reject, hold and break measurements; O003 Source clocks and availability.

**Risk, objectives and process.** O140 Exposure fitted to source risk constraints.

**Research, execution-study and risk records.** O148 Frozen observation cohort; O153 Outcome distribution of a declared process; O154 Prior loss-streak validation for Stoic's overlay; O155 Stoic's printed asymmetric risk ladder.

### M12 input producers

| Predicate fields and exact types | Producer recipes | Required derivation / hole behavior |
|---|---|---|
| `validated_process:boolean?`<br>`prior_sample_n:integer?`<br>`win_rate_known:boolean?`<br>`average_rr_known:boolean?`<br>`mc_loss_streak_known:boolean?` | [O154 — Prior loss-streak validation for Stoic's overlay](#o154)<br>[O148 — Frozen observation cohort](#o148)<br>[O153 — Outcome distribution of a declared process](#o153) | Same underlying process has at least 100 closed prior observations, and actual source win rate, average RR and compatible Monte Carlo max loss streak result known before overlay decision. No new Monte Carlo or proxy validation is invented; one unknown metric prevents admission. |
| `base_risk_fraction:decimal_fraction?`<br>`risk_stage:enum`<br>`risk_units:decimal_baseline_units?`<br>`planned_reward_r:decimal_source_R?`<br>`next_risk_units:decimal_baseline_units?` | [O155 — Stoic's printed asymmetric risk ladder](#o155) | Use fixed original baseline B/E0, strictly positive and≤0.01. Printed stage 1 risk 1/reward 3R; stage 2 risk 4/reward 3R; after second win next 1. Preserve heading-vs-ladder activation conflict and unpublished other transitions. Do not rebase on updated equity. |
| `first_trade_closed:boolean?`<br>`first_trade_result_units:decimal_baseline_units?`<br>`first_trade_close_at:event_key?`<br>`second_trade_result_units:decimal_baseline_units?`<br>`decision_at:event_key?` | [O155 — Stoic's printed asymmetric risk ladder](#o155)<br>[O153 — Outcome distribution of a declared process](#o153) | Supplied actual closed underlying trade results in original baseline units. First+3 must be closed/known before second risk decision; second+12 must be closed/known before the printed reset. Base causality checks apply even where the second close is not an explicit SQL operand. No entry is synthesized by this overlay. |

### M12 predicate: printed_ladder

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

### M12 acceptance fixtures

**M12-F1 — positive / declared scope.** Synthetic prior n 100 and all required validation known, E0=10000/B=100. First risk 1B for 3R; closed first win+300 before second decision; second risk 400 for 1200; second win gives net 1500 and next printed risk 100. Printed ladder checks pass with supplied records.

**M12-F2 — negative controls.** First win not closed before second risk: causal fail. Risk 412 from 4% of 10300 fails printed fixed baseline 4 units. Prior sample 99 or base risk 1.01% fails. No validated process cannot be treated as admitted.

**M12-F3 — source/data hole.** Unknown Monte Carlo result, general activation conflict or undefined after-loss/rebase transitions → corresponding unknown. No new simulation or profitability assertion.

Run C08's late-dependency, missing-input and identity mutations as well. Count fixtures separately from all reported market/process cohorts. The method pass command and output contract are in [PHASE.md](/workspace/planning/phase-1-live/PHASE.md).


## Object procedure index

Every one of the 166 objects mapped by the wiki has exactly one procedure below. Shared use means shared data definitions, not shared author permission. The method input tables above determine which outputs are required for the selected branch.

| ID | Object | Wiki group |
|---|---|---|
| [O001](#o001) | Evidence and data coverage | Observation foundations |
| [O002](#o002) | Touch, reject, hold and break measurements | Observation foundations |
| [O003](#o003) | Source clocks and availability | Observation foundations |
| [O004](#o004) | Source execution bars | Observation foundations |
| [O005](#o005) | Jumbo's 06:00–09:00 range | Session and range geometry |
| [O006](#o006) | Other time-based range formations | Session and range geometry |
| [O007](#o007) | Range EQ and quadrants | Session and range geometry |
| [O008](#o008) | Source range-open and range-close references | Session and range geometry |
| [O009](#o009) | Range width and expectations | Session and range geometry |
| [O010](#o010) | Retrospective range path | Session and range geometry |
| [O011](#o011) | Overnight high, low and width | Session and range geometry |
| [O012](#o012) | Chronological liquidity purges | Session and range geometry |
| [O013](#o013) | Opening location and participation | Session and range geometry |
| [O014](#o014) | Range exhaustion and mean-reversal area | Session and range geometry |
| [O015](#o015) | The 1.33–1.66 extension area | Session and range geometry |
| [O016](#o016) | Nested source range geometry | Session and range geometry |
| [O017](#o017) | Session Stat+ envelopes | Session and range geometry |
| [O018](#o018) | Jumbo EVRange | Session and range geometry |
| [O019](#o019) | Time-anchored P-zones | Session and range geometry |
| [O020](#o020) | PD RTH Range+ destinations | Session and range geometry |
| [O021](#o021) | Jumbo reversal and action windows | Session and range geometry |
| [O022](#o022) | Source session-cleanliness assessment | Session and range geometry |
| [O023](#o023) | Accumulation, manipulation and distribution phases | Session and range geometry |
| [O024](#o024) | Jumbo failure signatures and three attempts | Session and range geometry |
| [O025](#o025) | Opening-range midpoint reference | Session and range geometry |
| [O026](#o026) | Confirmed swing midpoint retrace | Session and range geometry |
| [O027](#o027) | Relative-volume context at the open | Session and range geometry |
| [O028](#o028) | Equal-high or equal-low liquidity objective | Session and range geometry |
| [O029](#o029) | Scheduled news and changing information | Regime and thesis context |
| [O030](#o030) | Session VWAP | Regime and thesis context |
| [O031](#o031) | Anchored VWAP | Regime and thesis context |
| [O032](#o032) | VWAP deviation bands | Regime and thesis context |
| [O033](#o033) | Source gamma regime | Regime and thesis context |
| [O034](#o034) | Native options-chain identity | Regime and thesis context |
| [O035](#o035) | Gamma-flip reference | Regime and thesis context |
| [O036](#o036) | Gamma call and put walls | Regime and thesis context |
| [O037](#o037) | Source max-pain reference | Regime and thesis context |
| [O038](#o038) | Source Vol Trigger readout | Regime and thesis context |
| [O039](#o039) | Source VOL-GEX readout | Regime and thesis context |
| [O040](#o040) | Source hedging-pressure gauge | Regime and thesis context |
| [O041](#o041) | Source KG1 level | Regime and thesis context |
| [O042](#o042) | VIX and volatility context | Regime and thesis context |
| [O043](#o043) | Volatility-implied daily-move estimate | Regime and thesis context |
| [O044](#o044) | Volatility term structure and event change | Regime and thesis context |
| [O045](#o045) | VVIX context | Regime and thesis context |
| [O046](#o046) | Green Bird's finished session references | Price references and price-action confirmation |
| [O047](#o047) | Sweep, failure and reclaim | Price references and price-action confirmation |
| [O048](#o048) | Prior day, week and month extremes | Price references and price-action confirmation |
| [O049](#o049) | Green Bird's midnight true-day open | Price references and price-action confirmation |
| [O050](#o050) | 09:30 cash-open price | Price references and price-action confirmation |
| [O051](#o051) | New-week opening gap | Price references and price-action confirmation |
| [O052](#o052) | Measured 50–61.8% retracement | Price references and price-action confirmation |
| [O053](#o053) | Premium / discount within a selected range | Price references and price-action confirmation |
| [O054](#o054) | Market-structure shift after failure | Price references and price-action confirmation |
| [O055](#o055) | Fair-value gaps and higher-timeframe imbalances | Price references and price-action confirmation |
| [O056](#o056) | Jumbo orderblocks | Price references and price-action confirmation |
| [O057](#o057) | Jumbo rejection blocks | Price references and price-action confirmation |
| [O058](#o058) | Jumbo Absorption Zone+ candle | Price references and price-action confirmation |
| [O059](#o059) | Source setup quality and exposure | Price references and price-action confirmation |
| [O060](#o060) | Auction balance | Auction and profile structure |
| [O061](#o061) | Volume profile | Auction and profile structure |
| [O062](#o062) | Profile value area | Auction and profile structure |
| [O063](#o063) | Developing profile snapshot | Auction and profile structure |
| [O064](#o064) | Profile point of control | Auction and profile structure |
| [O065](#o065) | Untested prior POC | Auction and profile structure |
| [O066](#o066) | High-volume node | Auction and profile structure |
| [O067](#o067) | Low-volume node | Auction and profile structure |
| [O068](#o068) | Profile shelf | Auction and profile structure |
| [O069](#o069) | Profile ledge | Auction and profile structure |
| [O070](#o070) | Composite auction profiles | Auction and profile structure |
| [O071](#o071) | Source-selected dealing range | Auction and profile structure |
| [O072](#o072) | Prior defended reaction area | Auction and profile structure |
| [O073](#o073) | Overnight volume structure | Auction and profile structure |
| [O074](#o074) | Overnight directional inventory | Auction and profile structure |
| [O075](#o075) | ETH profile identity | Auction and profile structure |
| [O076](#o076) | MPOC: the profile midpoint | Auction and profile structure |
| [O077](#o077) | Signed volume-by-price profile | Auction and profile structure |
| [O078](#o078) | Time-price-opportunity profile | Auction and profile structure |
| [O079](#o079) | TPO single-print structure | Auction and profile structure |
| [O080](#o080) | TPO excess at auction extremes | Auction and profile structure |
| [O081](#o081) | TPO poor high and poor low | Auction and profile structure |
| [O082](#o082) | Initial balance | Auction and profile structure |
| [O083](#o083) | Developing auction open type | Auction and profile structure |
| [O084](#o084) | Developing auction day structure | Auction and profile structure |
| [O085](#o085) | Profile shape and trade permission | Auction and profile structure |
| [O086](#o086) | Prior-session auction landmarks | Auction and profile structure |
| [O087](#o087) | Remaining auction objectives | Auction and profile structure |
| [O088](#o088) | Source-conditioned reference statistics | Auction and profile structure |
| [O089](#o089) | Saint's Asia-range target context | Auction and profile structure |
| [O090](#o090) | Rotation within accepted balance | Auction routes inside a method |
| [O091](#o091) | Accepted break and defended boundary retest | Auction routes inside a method |
| [O092](#o092) | Re-acceptance into value | Auction routes inside a method |
| [O093](#o093) | Sires's narrower Failed Auction setup | Auction routes inside a method |
| [O094](#o094) | Saint's failed auction and return to value | Auction routes inside a method |
| [O095](#o095) | POC failure versus efficient passage | Auction routes inside a method |
| [O096](#o096) | Whole-balance traversal with one side in control | Auction routes inside a method |
| [O097](#o097) | Higher- and lower-timeframe control alignment | Auction routes inside a method |
| [O098](#o098) | Executed aggressor-side trades | Order-flow evidence |
| [O099](#o099) | Big Trades aggression markers | Order-flow evidence |
| [O100](#o100) | DOM at a planned location | Order-flow evidence |
| [O101](#o101) | Absorption: effort without price reward | Order-flow evidence |
| [O102](#o102) | Executed passive replenishment | Order-flow evidence |
| [O103](#o103) | Iceberg evidence and added participation | Order-flow evidence |
| [O104](#o104) | Price reward near the absorption origin | Order-flow evidence |
| [O105](#o105) | Cumulative volume delta and its source reference | Order-flow evidence |
| [O106](#o106) | Candle direction versus executed delta | Order-flow evidence |
| [O107](#o107) | Local delta concentration at an extreme | Order-flow evidence |
| [O108](#o108) | POC relocation within a candle | Order-flow evidence |
| [O109](#o109) | Diagonal footprint imbalance stacks | Order-flow evidence |
| [O110](#o110) | Same-price 350% imbalance display | Order-flow evidence |
| [O111](#o111) | Speed of tape | Order-flow evidence |
| [O112](#o112) | Bid-ask spread | Order-flow evidence |
| [O113](#o113) | How price arrives at the area | Order-flow evidence |
| [O114](#o114) | Aggressor print-size thinning | Order-flow evidence |
| [O115](#o115) | Absorber becomes aggressive and price lifts off | Order-flow evidence |
| [O116](#o116) | Zone formed by aggressive prints | Order-flow evidence |
| [O117](#o117) | Memory of earlier zone tests | Order-flow evidence |
| [O118](#o118) | Origin-of-the-Move catalyst | Order-flow evidence |
| [O119](#o119) | Trapped aggression at an auction extreme | Order-flow evidence |
| [O120](#o120) | Native candle footprint | Order-flow evidence |
| [O121](#o121) | At-level DOM rejection | Execution branches within Sires's loop |
| [O122](#o122) | Four-check absorption reversal | Execution branches within Sires's loop |
| [O123](#o123) | Defense, replenishment, exhaustion and lift-off | Execution branches within Sires's loop |
| [O124](#o124) | Footprint-confirmed reaction | Execution branches within Sires's loop |
| [O125](#o125) | Confirmed VWAP deviation fade | Execution branches within Sires's loop |
| [O126](#o126) | Aggressive Origin of the Move | Execution branches within Sires's loop |
| [O127](#o127) | Passive Origin-of-the-Move variant | Execution branches within Sires's loop |
| [O128](#o128) | Clean squeeze continuation | Execution branches within Sires's loop |
| [O129](#o129) | Failure of aggression in long-gamma balance | Execution branches within Sires's loop |
| [O130](#o130) | Fresh defense of a continuation band | Execution branches within Sires's loop |
| [O131](#o131) | Price-defined microbalance continuation | Execution branches within Sires's loop |
| [O132](#o132) | KG1 retest and subsequent trailing | Execution branches within Sires's loop |
| [O133](#o133) | Deliberate pre-confirmation attempts | Execution branches within Sires's loop |
| [O134](#o134) | Third support test without new buyer defense | Execution branches within Sires's loop |
| [O135](#o135) | Late small resistance-fade case | Execution branches within Sires's loop |
| [O136](#o136) | Green Bird's directional read | Risk, objectives and process |
| [O137](#o137) | Declared model and review version | Risk, objectives and process |
| [O138](#o138) | Thesis, validity band and death condition | Risk, objectives and process |
| [O139](#o139) | Entry-side structural invalidation | Risk, objectives and process |
| [O140](#o140) | Exposure fitted to source risk constraints | Risk, objectives and process |
| [O141](#o141) | Objective selected before entry | Risk, objectives and process |
| [O142](#o142) | Source-selected position management | Risk, objectives and process |
| [O143](#o143) | Confirmed protected high or low | Risk, objectives and process |
| [O144](#o144) | Freshly qualified re-entry | Risk, objectives and process |
| [O145](#o145) | Source account and session stop | Risk, objectives and process |
| [O146](#o146) | Thesis and execution journal | Risk, objectives and process |
| [O147](#o147) | Triad AMT-object first use: IØD and RFZ | Risk, objectives and process |
| [O148](#o148) | Frozen observation cohort | Research, execution-study and risk records |
| [O149](#o149) | Supplied refill-touch grade | Research, execution-study and risk records |
| [O150](#o150) | Observed order lifecycle | Research, execution-study and risk records |
| [O151](#o151) | Refill-study fill assumption | Research, execution-study and risk records |
| [O152](#o152) | Trading and account costs | Research, execution-study and risk records |
| [O153](#o153) | Outcome distribution of a declared process | Research, execution-study and risk records |
| [O154](#o154) | Prior loss-streak validation for Stoic's overlay | Research, execution-study and risk records |
| [O155](#o155) | Stoic's printed asymmetric risk ladder | Research, execution-study and risk records |
| [O156](#o156) | Refill-study evaluation-risk scenarios | Research, execution-study and risk records |
| [O157](#o157) | Stoic's macro indicator set | Research, execution-study and risk records |
| [O158](#o158) | Stoic's macro-cycle classification | Research, execution-study and risk records |
| [O159](#o159) | Stoic's custom C-score | Research, execution-study and risk records |
| [O160](#o160) | Historical-average and standardized-deviation comparison | Research, execution-study and risk records |
| [O161](#o161) | Stoic's trend-strength measure | Research, execution-study and risk records |
| [O162](#o162) | Economic observation and release vintage | Research, execution-study and risk records |
| [O163](#o163) | Provide, withdraw and consume events | Auction-state observation |
| [O164](#o164) | Aggressive effort versus price-response efficiency | Auction-state observation |
| [O165](#o165) | B–A–D–E–W auction-state alphabet | Auction-state observation |
| [O166](#o166) | Conditioned next-state transition | Auction-state observation |


<a id="o001"></a>

## O001 — Evidence and data coverage

**Wiki:** [Evidence and data coverage](/workspace/planning/phase-1-live/wiki/data-coverage.md). **Implementation mode:** compute + audit.

An observation is usable only if its evidence supports what the method asks. An executed trade, a displayed quote, a full-depth cancellation and a drawn chart annotation are different observations. The auction-state source uses submissions, cancellations and executions; the data-engine source requires consistent collection. [MATH] pp.4–8; [DATA] pp.3–4.

**Not a standalone trade.** Coverage supplies evidence for a decision; it does not supply the decision rule. A BBO reload hypothesis cannot certify hidden reserve or off-touch depth.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | C03 file inventory/schema, frozen required input list, exact requested event intervals, source/instrument identity, coverage and missingness records. |
| Outputs / units | coverage_ok:boolean?, base_identity_ok:boolean?, missing_intervals[], missing_fields[], source_precision, available_depth. |
| ET clock / interval | ET windows converted per C02; native input UTC units per C03. |
| Bars / event membership | Inspect actual required intervals; a file's min/max alone does not establish continuous event coverage. |
| Reset / persistence | New coverage record for every dataset/instrument/window/branch; do not inherit one all-method eligible-day flag. |
| known_at | At the relevant observation cutoff after all required records are validated; a later file audit can validate coverage but cannot move a market value's own known_at earlier. |

**Procedure:**

1. Resolve each required object to its actual dataset or supplied record. Check instrument, clock, schema, bounds, file ownership and fields before aggregating.
2. Intersect the branch's required data intervals; retain every absent interval and field. A healthy trade tape does not establish hidden reserve, full-depth cancels, a proprietary value or a source-selected thesis.
3. Return true only when every required observation is available and supported. Return null for any required hole. An explicitly wrong instrument/unit is a witnessed false identity check. Do not discard the candidate to improve coverage.

**Printed constants and limits:** No trading thresholds. Dataset dates/counts in C03 are inventory facts, not detector parameters.

**Invalid / unavailable behavior:** Unknown timestamp unit; overlapping unowned files; missing side/depth; absent source version; partial required interval. All produce the corresponding hole rather than invented zeros. Apply C04; emit `HOLE:O001:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O001-F1 — numeric fixture:** Synthetic: a branch requires 10:00–10:05 OHLC and signed trades. Five complete minute bars exist but trade side is absent for volume 12: price coverage=true, side coverage=null, coverage_ok=null; missing_fields contains aggressor. Supplying all five correctly timed signed intervals makes coverage_ok=true. Four minute bars alone cannot pass.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** slice and mbp1_extract; mbp1_objects provides trade and best-quote ingredients. Full order/depth reconstruction, several proprietary levels and a complete operator event ledger are missing. Existing behavior is not authority over this procedure.


<a id="o002"></a>

## O002 — Touch, reject, hold and break measurements

**Wiki:** [Touch, reject, hold and break measurements](/workspace/planning/phase-1-live/wiki/touch-reject-hold-break-grid.md). **Implementation mode:** literal measurements; source confirmation can remain a hole.

The authors distinguish arrival, failure, acceptance and defended retest; their observation durations and confirmations differ. The common repository grid is a measurement convention for comparing those events, not a universal author rule. [TBR] pp.8–15, 27–29; [GB] pp.25, 27; [AMT1] pp.7–9.

**Not a standalone trade.** A touch or grid rejection cannot replace the method's context and complete confirmation. A profitability label cannot repair an absent prerequisite.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen band [lo, hi], parent width W when used, known_at, source side, exact price/bar evidence, explicitly supplied tolerance and hold/rejection criteria. |
| Outputs / units | contact_at, price_overlap:boolean?, strict_break_side, sweep_depth, literal_close_return:boolean?, source_reject:boolean?, source_hold:boolean?. |
| ET clock / interval | Candidate's source ET interval; no added time limit. |
| Bars / event membership | Ticks establish ordered contact; completed bars can establish interval overlap or closing side. OHLC cannot establish the within-bar path. |
| Reset / persistence | New touch after a documented departure; freeze band per touch/attempt. |
| known_at | Contact at the witnessed event; bar overlap/close at bar close; a hold/rejection only when its complete stated evidence is available. |

**Procedure:**

1. Literal tick contact is lo<=price<=hi; bar overlap is H>=lo AND L<=hi. An exact projected level can be crossed without a print exactly on it; label crossing separately. Record literal geometry, not a fill.
2. An upper strict price break is price>hi; a lower break is price<lo. Equality is contact, not strict break. Return inside a box requires lo<close<hi when the selected method uses strict close comparisons; preserve an endpoint equality as a separately observed boundary, not the stated reclaim.
3. If the source explicitly supplies tolerance e in ticks, use [lo-e*q, hi+e*q] and record e; otherwise do not add a tolerance. The old e=2, 0.5W/15-minute reject and 30-minute hold/cap remain historical research conventions and are not admitted as author checks here.
4. A meaningful rejection/hold needs the source branch's actual evidence. An unspecified duration, displacement or control detector produces null. Keep raw contact/break metrics available without calling them confirmation.

**Printed constants and limits:** Only source-supplied per-case tolerance/window. Literal ordering and range algebra add no trading constant.

**Invalid / unavailable behavior:** lo>hi, W<=0 where required, unknown tick size, band known after contact, or unresolved same-bar ordering. Missing confirmation definition => HOLE for reject/hold, not for computable price overlap. Apply C04; emit `HOLE:O002:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O002-F1 — numeric fixture:** Synthetic q=0.25, band [100, 101], bar L=100.50/H=102: overlap=true, upper price excursion=1 point=4 ticks. C=101 does not satisfy C<101; C=100.75 does. No source hold duration was supplied: source_hold=null despite ten bars inside.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels §0.2 / P3-03; [grid.touch_level](/workspace/implementation/src/trading_research/research/phase1_live/grid.py), [grid.reject_after_touch](/workspace/implementation/src/trading_research/research/phase1_live/grid.py), [grid.hold_after_break](/workspace/implementation/src/trading_research/research/phase1_live/grid.py) and [grid.failback_wick_c5](/workspace/implementation/src/trading_research/research/phase1_live/grid.py). The default two ticks, half-range rejection in 15 minutes, 30-minute hold and 30-minute fail-back cap are named research settings. Existing behavior is not authority over this procedure.


<a id="o003"></a>

## O003 — Source clocks and availability

**Wiki:** [Source clocks and availability](/workspace/planning/phase-1-live/wiki/clock-grid-and-bars.md). **Implementation mode:** compute.

The clock identifies what has finished before a decision. Jumbo's main range forms 06:00–09:00 ET; Green Bird's NYAM box forms 09:00–10:00; TPO and opening observations have their own completed periods. These clocks cannot be interchanged. [TBR] p.7; [GB] pp.23, 30–31; [AVG] pp.21–22.

**Not a standalone trade.** A scheduled minute does not create a trade. A 09:45 candidate cannot use the final 09:00–10:00 range.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source timezone/clock/version, dated interval endpoints, native timestamp profile, instrument and complete bar/event membership. |
| Outputs / units | start_ns, end_ns, session_date_et, bar_close_at, window_known_at, clock_verified. |
| ET clock / interval | America/New_York where ET is stated; see C02-F1 for DST conversion. |
| Bars / event membership | Clock-aligned 1/2/3/5/15/60-minute only when the selected source names that size; keep native range/TPO construction distinct. |
| Reset / persistence | Every selected dated source window; carry previous-evening date explicitly. |
| known_at | Completed window at end; completed bar at close; source clock verification is an input, not a guess from a label. |

**Procedure:**

1. Apply C02 exactly. For each bar compute ET-aligned start/end and record UTC equivalents. A range's final values become available at its formation end, never at its start.
2. For cross-midnight windows set the start on the explicitly identified prior calendar date. Never interpret 18:00–09:30 as a negative-duration same-date window.
3. Retain unresolved chart timezone or formation bounds as null clock_verified and list the missing endpoint. Never fill London bounds from another author.

**Printed constants and limits:** Jumbo 06:00–09:00 and listed half-hour formations; GB 09:00–10:00; TPO 30-minute A/B as cited. No universal source reset.

**Invalid / unavailable behavior:** Unresolved DST wall time, missing endpoint, inconsistent source/date or incomplete aggregate; C02 defines outcomes. Apply C04; emit `HOLE:O003:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O003-F1 — numeric fixture:** C02-F1 is the numerical fixture. Additionally a completed 03:00–03:30 ET source range is not available to an event at 03:15: clock check=false; its 03:30 value can be used at 03:31.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** clocks. CLOCKS/clock_bounds; [family_clocks.build_clock_table](/workspace/implementation/src/trading_research/research/phase1_live/family_clocks.py); the previous formula labels P3-01/P3-06. Exact London bounds and some modern source clock configurations remain unresolved. Existing behavior is not authority over this procedure.


<a id="o004"></a>

## O004 — Source execution bars

**Wiki:** [Source execution bars](/workspace/planning/phase-1-live/wiki/execution-bars.md). **Implementation mode:** compute time bars; native-range construction hole.

Bar construction changes what a candle, print cluster and confirmation mean. Jumbo illustrates 2/3/5-minute block entries; Green Bird specifies completed five-minute closes in selected cases; Sires uses NQ 40-range charts in the Big Trades material. [TBR] pp.27–29; [GB] pp.25, 27; [BIG] pp.3–5.

**Not a standalone trade.** A range bar or short timeframe is a display/observation unit, not an entry model.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | C03 executed events or complete finer OHLCV; source bar kind/size/anchor, instrument and member IDs. |
| Outputs / units | bar_id, O, H, L, C, V, start, end, complete, known_at, native_source_compatible. |
| ET clock / interval | ET alignment for source time bars; event-driven source clock for range bars. |
| Bars / event membership | Jumbo 2/3/5-minute; selected GB five-minute; Sires NQ 40-range remains native, with no guessed range-bar implementation. |
| Reset / persistence | Each interval or verified native bar boundary; source session reset remains explicit. |
| known_at | Completed bar at final required event/close, developing native candle snapshot only at its as_of event. |

**Procedure:**

1. Build time bars by C02 O/H/L/C/V aggregation on one instrument. Keep complete membership and exact boundaries for later footprint/delta joins.
2. Never supply a 1-minute candle where the source requests a range candle or aggregate the whole morning into one candle.
3. For 40-range, ingest source candle IDs/member events or a complete supplied platform construction. Missing tick-versus-point unit, gap treatment, reset, overshoot or reversal handling yields HOLE:native_bar_definition; do not infer them from the number 40.

**Printed constants and limits:** 2, 3, 5 minutes in TBR; five-minute close in selected GB cases; literal source display 40-range. These do not publish the native-range algorithm.

**Invalid / unavailable behavior:** Mixed instruments, missing member intervals, fabricated zero-volume OHLC, unidentified native construction, or backdated candle close. Apply C04; emit `HOLE:O004:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O004-F1 — numeric fixture:** Synthetic two complete one-minute bars (O, H, L, C, V)=(100, 102, 99, 101, 10) and (101, 103, 100, 102, 20) inside 10:00–10:02 produce (100, 103, 99, 102, 30), known_at=10:02. The same inputs cannot produce a source-compatible NQ 40-range bar: compatibility=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** clocks and mbp1_extract provide time and event ingredients. Native source-compatible range-bar reconstruction and several intrabar footprint stages are missing; the previous formula labels P3-01/P3-04 and R-F04/F05/F14. Existing behavior is not authority over this procedure.


<a id="o005"></a>

## O005 — Jumbo's 06:00–09:00 range

**Wiki:** [Jumbo's 06:00–09:00 range](/workspace/planning/phase-1-live/wiki/tbr-6-9-range.md). **Implementation mode:** compute frozen geometry.

The main New York formation range supplies its high, low, width and internal references before the post-formation decisions. It is one geometry inside SDRange / Time-Based Ranges. [TBR] pp.4–8; [JR] pp.11, 14, posts 2055344660986364371 / 2026059018750378427.

**Not a standalone trade.** The high, low or EQ is a location. Neither an edge touch nor the eventual single/double-break class is a complete entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Complete source-compatible prices/bars for [06:00, 09:00) ET on one contract/date. |
| Outputs / units | range_id, L, H, W, formation_start, formation_end, range_known_at, range_frozen. |
| ET clock / interval | [06:00, 09:00) ET; date-aware conversion. |
| Bars / event membership | Complete minute bars suffice for H/L; finer events required for literal opening/entry instants. |
| Reset / persistence | New range_id each dated 6–9 formation and contract; never extend it with later bars. |
| known_at | 09:00 ET after included bars close; q and identity must already be verified. |

**Procedure:**

1. Select only members with start>=06:00 and end<=09:00. Compute L=min L_i, H=max H_i, W=H-L. Validate complete formation coverage and W>0.
2. Emit immutable geometry and its known_at. Compute internals/projections only from this parent ID. The 09:30 open and later high/low never modify it.
3. A candidate touching the alleged final range before 09:00 fails availability; it is not an early use of the completed box.

**Printed constants and limits:** 06:00 and 09:00 ET from TBR. No minimum width, liquidity or directional threshold.

**Invalid / unavailable behavior:** Empty/incomplete formation, W<=0, mixed roll segment, or later included bar => invalid/unknown geometry; a proven future dependency is base fail. Apply C04; emit `HOLE:O005:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O005-F1 — numeric fixture:** Synthetic formation has L=100/H=120: W=20, known_at=09:00. A 09:10 high=130 leaves H=120. A 08:50 decision using H=120 as the completed range fails even if the number later happens to be correct.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [sessions.build_session/projections](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); family_range; family_clocks; the previous formula labels R-J05/J07/J23, P3-01/P3-06. Geometry exists; source-open identity and modern inner ranges require separate records. Existing behavior is not authority over this procedure.


<a id="o006"></a>

## O006 — Other time-based range formations

**Wiki:** [Other time-based range formations](/workspace/planning/phase-1-live/wiki/tbr-remaining-clocks.md). **Implementation mode:** compute verified manual clocks; later source configuration hole.

The manual applies the same framework to Asia 20:00–20:30, midnight 00:00–00:30, London 03:00–03:30, 09:30–10:00, 10:00–10:30, lunch 12:00–12:30 and 15:00–15:30. Each formation has its own geometry and availability. [TBR] pp.6–7, 36. Later London examples show another source configuration whose exact formation bounds must be verified. [JR] pp.50–51, 63–66.

**Not a standalone trade.** These are session variants of the range loop, not eight independent entry systems. Liquidity-map hours are also not automatically the formation hours.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source version plus exactly selected dated formation; same H/L inputs as 6–9. |
| Outputs / units | source_clock_id, range_id, L, H, W, known_at, source_clock_verified. |
| ET clock / interval | Manual: 20:00–20:30, 00:00–00:30, 03:00–03:30, 09:30–10:00, 10:00–10:30, 12:00–12:30, 15:00–15:30 ET. |
| Bars / event membership | Complete source time bars/events, half-open windows per C02. |
| Reset / persistence | One immutable range per source clock/date/instrument. These are JJ-TBR variants, not new method IDs. |
| known_at | At each chosen formation end; later London configuration requires its own verified endpoints. |

**Procedure:**

1. Choose the source clock before reading outcomes. Use the same frozen H/L/W calculation as the 6–9 recipe, with that window's own parent ID.
2. Keep formation and action windows separate: the price can act after a range froze. Liquidity-map session hours do not define the formation automatically.
3. For a later London example lacking exact formation endpoints, return null source_clock_verified. Do not replace it with retained 00:00–03:00.

**Printed constants and limits:** The seven listed half-hour source formations. No preferred-session lookback or modern London default.

**Invalid / unavailable behavior:** Unverified configuration/axis, pre-end use, missing formation or parent substitution. Apply C04; emit `HOLE:O006:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O006-F1 — numeric fixture:** Synthetic manual London [03:00, 03:30) L=200/H=208 gives W=8 known 03:30. A 03:35 action can use it. Selecting 00:00–03:00 instead with H=220 fails source_clock_verified for this manual fixture.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** clocks. CLOCKS; [family_clocks.build_clock_table](/workspace/implementation/src/trading_research/research/phase1_live/family_clocks.py); [sessions.projections](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); the previous formula labels R-J09/J23. Retained 00:00–03:00 London is an approximation, not a universally verified author clock. Existing behavior is not authority over this procedure.


<a id="o007"></a>

## O007 — Range EQ and quadrants

**Wiki:** [Range EQ and quadrants](/workspace/planning/phase-1-live/wiki/range-internals.md). **Implementation mode:** compute.

EQ and the quarter levels divide the chosen frozen range and provide internal locations or destinations. Extended and purged cases use EQ/quadrant entries differently; the large-range September example trades EQ in both directions with confirmation. [TBR] pp.4–5, 12–15, 24; [JR] p.3, post 2095172969035096454.

**Not a standalone trade.** Touch EQ is not a reversal command. Range EQ, an EV midpoint, volume POC and a range-open line have different identities.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen parent range_id, L, H, W>0 and known_at. |
| Outputs / units | q25=L+0.25W, eq=L+0.50W, q75=L+0.75W, all with parent ID. |
| ET clock / interval | Parent's ET formation. |
| Bars / event membership | No new bars; algebra over the frozen parent. |
| Reset / persistence | Recompute only for a new parent range/version, not on every later price. |
| known_at | Parent range known_at. |

**Procedure:**

1. Calculate the three exact decimal levels from the same L/H. Preserve fractional ticks; do not round a midpoint into a tradable quote.
2. Use literal contact/break measures from the touch recipe. Equality at EQ is not a strict break; context and chosen confirmation remain separate.
3. Never substitute EV midpoint, POC, range open, a different box's EQ or a future profile midpoint.

**Printed constants and limits:** 0.25, 0.50, 0.75 printed range fractions.

**Invalid / unavailable behavior:** Unknown/zero width or inconsistent parent ID; independently calculated levels from another range cannot join. Apply C04; emit `HOLE:O007:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O007-F1 — numeric fixture:** Synthetic L=100/H=120/W=20 => Q25=105, EQ=110, Q75=115. A price of 110 is at EQ; it is neither strictly above nor strictly below. For L=100/H=100.25, EQ=100.125 remains unrounded.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [sessions.projections](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py) and build_session; the previous formula labels R-J03/J04/J05 and P3-01. The internal geometry exists; contextual entry and same-attempt confirmation are partial. Existing behavior is not authority over this procedure.


<a id="o008"></a>

## O008 — Source range-open and range-close references

**Wiki:** [Source range-open and range-close references](/workspace/planning/phase-1-live/wiki/range-open-close.md). **Implementation mode:** supplied source identity; literal price computation only when anchor is explicit.

Range open and close are separately drawn references. Their identity must be read from the actual source version, label and price. The January 2 range-open path is low → range open; the displayed line is anchored near the range finish, so a blanket first-06:00-print substitution is not established for that fixture. [TBR] pp.4–5; [JR] pp.53–54.

**Not a standalone trade.** A colored line or the arrow in low → open does not imply a fixed clock, an inequality, or a fill at the zone anchor time.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal source label, parent range/version, source price/band, anchor event or verified open/close rule, source time and known_at. |
| Outputs / units | range_open_ref, range_close_ref, anchor_id, reference_verified, directed_path. |
| ET clock / interval | Source anchor's ET clock, not an assumed formation-start clock. |
| Bars / event membership | Use a referenced opening trade or completed closing bar only if source identifies it; otherwise retain supplied line. |
| Reset / persistence | Each source range/version/date; labels never imply identical anchors across versions. |
| known_at | Actual anchor availability or supplied pre-use snapshot; unresolved time => null. |

**Procedure:**

1. Preserve the named open/close line separately from H/L/EQ. If the source says first formation trade, compute that; if it identifies a finish-time line, use that exact anchor. The January source does not license a blanket first-06:00 substitution.
2. Represent low→range-open as ordered source/target IDs, not low>open. Observe a low-origin event then later line reach, only after both references are known.
3. When the chart doesn't identify the anchor/price sufficiently, output HOLE:source_open_identity; do not select the price which makes the path true.

**Printed constants and limits:** No universal open/close timestamp is supplied for every source version.

**Invalid / unavailable behavior:** Unresolved line/axis, conflating path arrow with inequality, assumed 06:00 origin, later-selected anchor. Apply C04; emit `HOLE:O008:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O008-F1 — numeric fixture:** Synthetic source line marked range open=112 known 09:00, range low=100. A 10:00 test at 100 then 10:10 trade 112 completes low→open; numeric 100>112 is false and is not the path predicate. An unrelated 06:00 open 108 must not replace 112.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [sessions.build_session](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py) exposes the first open; the previous formula labels R-J05/J12 and P3-01. The source-specific open/close identity and path join are partial. Existing behavior is not authority over this procedure.


<a id="o009"></a>

## O009 — Range width and expectations

**Wiki:** [Range width and expectations](/workspace/planning/phase-1-live/wiki/range-width-context.md). **Implementation mode:** compute widths/ratios; qualitative classification hole.

Width conditions expectations: a wide/extended overnight can call for restrained targets; a compressed range after purges can support expansion. Printed percentage-width break tables and prior-RTH comparisons have different denominators. [TBR] pp.12–15, 24; [JR] pp.48–49.

**Not a standalone trade.** Wide or narrow is context, not a direction or an automatic single-break entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Own W; explicit positive denominator price P and its timestamp or separate prior_range_width; source bucket/definition if supplied. |
| Outputs / units | width_points, width_ticks=W/q, price_percent=100W/P, width_ratio=W/prior_W, source_width_class:boolean/enum?. |
| ET clock / interval | Own and comparison ranges' ET clocks. |
| Bars / event membership | Only completed parent ranges and pre-decision comparison values. |
| Reset / persistence | Each range/context snapshot; baseline identities cannot change after entry. |
| known_at | Maximum of own and comparison input known_at. |

**Procedure:**

1. Compute only ratios whose denominator identity is explicitly specified. Price-percent and ratio-to-prior-width are different output fields.
2. A literal printed bucket can be checked using its recorded boundaries and inclusivity. Without a source bucket definition, retain the scalar and set extended/compressed classification null.
3. Do not map wide/narrow to direction or use eventual single-break outcome to select an entry branch.

**Printed constants and limits:** No universal extended/compressed threshold. Percentage factor 100 is unit conversion, not a setup threshold.

**Invalid / unavailable behavior:** P<=0 or prior_W<=0; missing denominator convention; future comparison values; unprinted generic buckets. Apply C04; emit `HOLE:O009:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O009-F1 — numeric fixture:** Synthetic W=20, P=20000, prior_W=80 => price_percent=0.10%, width_ratio=0.25, width_ticks=80 if q=.25. These numbers do not establish extended_context: without a source class rule it is null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [sessions.width_bin](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); family_range; family_open; the previous formula labels R-J03/J04/J07/J21. Generic ratio buckets do not reproduce a source price-percent table. Existing behavior is not authority over this procedure.


<a id="o010"></a>

## O010 — Retrospective range path

**Wiki:** [Retrospective range path](/workspace/planning/phase-1-live/wiki/range-path-class.md). **Implementation mode:** compute retrospective event geometry.

High-only, low-only, both and neither describe which sides of a completed range were taken in a specified later window; break order and mid retraces describe the path. The author's single/double-break statistics frame expectations. [TBR] pp.8–15, 30; [JR] pp.48–49.

**Not a standalone trade.** The final path label is not information available at the opening entry. Judas, extended and purged branch qualification needs its earlier context and confirmation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen L/H, explicit later outcome window, source break definition, ordered post-formation prices. |
| Outputs / units | high_break_at, low_break_at, path=high_only/low_only/both/neither/unknown, first_side, eq_return_at. |
| ET clock / interval | Keep source [09:00, 12:00), [09:30, 10:30) and other windows separate. |
| Bars / event membership | Tick order or complete source bars; same-bar both-side order can be unknown. |
| Reset / persistence | New range+outcome-window record, never reused as pre-entry context. |
| known_at | Final path at declared outcome-window end; prefix observations only at their actual event time. |

**Procedure:**

1. Using the stated break criterion, collect first post-formation upper/lower breaches inside the selected window. For literal price breaks use >H and <L; equality is not a breach.
2. After complete observation label both/high_only/low_only/neither. For incomplete coverage preserve known positive breaches but absence of a breach is unknown.
3. Compute first_side only if the two events are ordered. Compute later EQ return from observations after the first event, without selecting the final deepest excursion.
4. Keep this output out of all earlier direction/context gates.

**Printed constants and limits:** Source-specific windows only. No pooled single/double-break probability.

**Invalid / unavailable behavior:** Incomplete absence evidence, unknown ordering or break convention, pre-formation measurements, using final label as entry input. Apply C04; emit `HOLE:O010:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O010-F1 — numeric fixture:** Synthetic H=120/L=100. At 09:35 price 121, at 10:10 price 99: the 09:30–10:30 path is both, first_side=high. Through 10:00 the prefix is high-only-so-far, not a final single-break classification. A single bar H121/L99 gives both but first_side=unknown.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_path; [sessions.build_session](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); the previous formula labels R-J01–J07. Daily path flags are useful descriptive outputs, not a method scorer. Existing behavior is not authority over this procedure.


<a id="o011"></a>

## O011 — Overnight high, low and width

**Wiki:** [Overnight high, low and width](/workspace/planning/phase-1-live/wiki/overnight-range.md). **Implementation mode:** compute source-scoped range.

Overnight price extremes frame remaining liquidity and opening context. Sires's AMT discussion uses the 18:00–09:30 overnight auction; Jumbo also draws named Asia/London references whose configured windows differ. [MAMT] pp.14–16; [TBR] pp.12–15; [JR] pp.16–18.

**Not a standalone trade.** An overnight extreme or the claim that either side is often reached supplies no entry direction and no proof that both sides will trade.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source overnight start/end, contract, complete prices, separately named Asia/London window IDs. |
| Outputs / units | on_high, on_low, on_width, window_id, known_at; separate Asia/London records. |
| ET clock / interval | Sires source 18:00 prior calendar day–09:30 decision date ET; Jumbo configured windows stay distinct. |
| Bars / event membership | Complete source-compatible time bars/events. |
| Reset / persistence | Each selected overnight window/date/contract. |
| known_at | At selected overnight window end; developing prefix has a different object ID/state. |

**Procedure:**

1. Apply frozen H/L/W procedure to the exact overnight window. Do not use 6–9, prior RTH or an inferred London window as overnight.
2. Retain source configuration for named session liquidity levels. A custom chart setting must travel with that object.
3. Later either-edge reach is a separate outcome; ONH/ONL existence supplies neither direction nor a both-sides prediction.

**Printed constants and limits:** 18:00–09:30 only for the cited Sires overnight scope; no universal Jumbo overnight clock beyond verified configuration.

**Invalid / unavailable behavior:** Missing prior-evening data, mixed contract, unknown configured bounds or pre-end final-range use. Apply C04; emit `HOLE:O011:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O011-F1 — numeric fixture:** Synthetic Sires overnight H=150/L=130 ends 09:30: width 20. Separate 6–9H145/L135 has width 10 and cannot replace it. At 09:20 full ONH=150 is not yet a final overnight object.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** clocks; sessions; [family_levels.build_level_table](/workspace/implementation/src/trading_research/research/phase1_live/family_levels.py); the previous formula labels R-J04/J10, R-A12 and P3-06. Exact configured window identity is required. Existing behavior is not authority over this procedure.


<a id="o012"></a>

## O012 — Chronological liquidity purges

**Wiki:** [Chronological liquidity purges](/workspace/planning/phase-1-live/wiki/overnight-purge.md). **Implementation mode:** state ledger over source-defined sweep events.

In the purged single-break case, the overnight auction has already taken relevant earlier highs/lows before the later expansion decision. Later source settings keep named session and prior-day liquidity references and can retire them after use. [TBR] pp.11–15; [JR] pp.16–18, 33–39.

**Not a standalone trade.** Containment of two completed boxes does not prove when liquidity was taken. The RTH-only destination application deliberately has a different consumption scope.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Reference ID/price/side, formation known_at, source consumption scope and sweep definition, chronological event stream. |
| Outputs / units | active_before_use, purged_at, consumption_scope, purge_known_at, source_purged_context?. |
| ET clock / interval | Reference/session's ET scope; purge must precede the expansion decision. |
| Bars / event membership | Events sufficient for source sweep criterion; unresolved intrabar sequence remains unknown. |
| Reset / persistence | Each new reference instance; preserve history rather than resetting every caller. RTH-only ledger is a separate scope. |
| known_at | At first qualifying sweep event/confirmation; not when two completed ranges are compared later. |

**Procedure:**

1. Initialize a known reference as active. Scan forward only from its known_at. On its first source-defined qualifying sweep, record purged_at once; do not backdate that state.
2. For the purged branch, evaluate relevant ledger entries as of decision_at and require purge_known_at<decision_at. Which references must be purged and what compressed means remain source-context inputs/hole.
3. For expressly RTH-only objectives, record ETH sweeps separately without retiring the RTH objective. Do not apply that exception to erase overnight purge evidence in single_purged.

**Printed constants and limits:** No added lookback, tolerance or universal retired-on-touch rule.

**Invalid / unavailable behavior:** Reference formed after alleged sweep; later sweep used earlier; blanket box containment; source sweep/retirement definition absent. Apply C04; emit `HOLE:O012:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O012-F1 — numeric fixture:** Synthetic prior high 110 known 18:00, verified qualifying sweep 111 at 02:10, decision 09:45 => purged_at02:10 and purge-before-decision=true. Move sweep to 10:00 =>false. Under RTH-only scope the 02:10 hit leaves active=true for 09:45; the same event can be a true overnight purge in its distinct ledger.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [sessions._purged](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); family_levels; [formulas_jumbo.j10_draw](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-J04/J10/J19. A persistent source-scoped consumption ledger is missing. Existing behavior is not authority over this procedure.


<a id="o013"></a>

## O013 — Opening location and participation

**Wiki:** [Opening location and participation](/workspace/planning/phase-1-live/wiki/open-location-switch.md). **Implementation mode:** compute location cells; source context interpretation hole.

Locate the opening auction against already-known prior value, prior price range and current frozen references. Jumbo's raw examples include continuation outside prior value while still inside the prior price range. Keani separately requires the whole current A period above prior VAH. [TBR] pp.16–24; [JR] pp.33–39, 48–49; [AVG] pp.21–22.

**Not a standalone trade.** Outside both range and value plus high RVOL is one context cell, not the only continuation permission. An opening cell alone supplies no entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Observed cash-open price/time; prior fixed value [VAL, VAH] and prior price [L, H]; today's already-frozen range; optional source RVOL record. |
| Outputs / units | open_vs_value=below/inside/above/on_boundary, open_vs_range, open_vs_current_range, opening_context?, rvol_known_at. |
| ET clock / interval | 09:30 ET opening event; each prior/current reference retains its own session definition. |
| Bars / event membership | Opening trade for immediate use; a stored one-minute open is usable no earlier than its completed bar unless the trade is supplied. |
| Reset / persistence | One opening snapshot per instrument/session; source reference IDs fixed. |
| known_at | Maximum opening-event and reference availability; RVOL measured 09:30–09:35 adds known_at09:35. |

**Procedure:**

1. Compare the same opening price separately with prior value and prior full range. Preserve strict outside, interior and exact-boundary cases; do not collapse distinct cells.
2. Store a source interpretation only if the chosen example supplies it before entry. Outside value while inside the prior price range can still be a continuation context; do not require outside both.
3. Do not compute direction from the final path. Keani's whole-A-low test is separate and is evaluated only after A completes.

**Printed constants and limits:** 09:30 cash open and the explicitly selected RVOL window. No universal high-RVOL threshold or continuation lookup.

**Invalid / unavailable behavior:** Prior area not fixed; final current-day VA substituted; future RVOL supplied at 09:30; unverified prior RTH/ETH identity. Apply C04; emit `HOLE:O013:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O013-F1 — numeric fixture:** Synthetic prior value [100, 110], prior range [95, 115], open 112 => above value, inside range. It does not fail merely for being inside range. RVOL from 09:30–09:35 cannot be a 09:31 context input.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_open.build_open_table](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); the previous formula labels R-J06/J21, R-A10 and R-S09. Current final-path direction and future participation inputs are not contemporaneous context. Existing behavior is not authority over this procedure.


<a id="o014"></a>

## O014 — Range exhaustion and mean-reversal area

**Wiki:** [Range exhaustion and mean-reversal area](/workspace/planning/phase-1-live/wiki/range-exhaustion-area.md). **Implementation mode:** compute identified ladder; source location selection hole.

The manual draws mean-reversal levels and a shaded exhaustion area beyond each range edge, commonly involving 0.1/0.2/0.3 and the half-width area. Source charts include shallower sweeps and overshoot. [TBR] pp.5, 8–11, 20, 27–30; [JR] pp.53–57.

**Not a standalone trade.** An exact half-width touch is neither compulsory in every raw reversal nor sufficient for one. Location and confirmed rejection are different observations.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen range_id, L, H, W; exact source ladder coordinate convention and selected band; price events. |
| Outputs / units | upper_k=H+k W, lower_k=L-k W, selected_band, sweep_depth_points, sweep_depth_W, touch_at. |
| ET clock / interval | Parent range ET formation; branch-specific later action interval. |
| Bars / event membership | Parent range bars; subsequent tick/bar location evidence, not future extrema. |
| Reset / persistence | New parent range or explicitly selected source ladder/version. |
| known_at | Parent geometry and source band selection must be known before use; contact at its event/complete bar. |

**Procedure:**

1. For an explicitly beyond-edge ladder compute upper and lower coordinates using that parent's W. Preserve each printed k and its literal label; an anchor convention not stated is a hole.
2. Measure a high sweep as max(0, price-H)/W, low sweep as max(0, L-price)/W. Store the actual first source-eligible sweep and later observations rather than selecting the deepest morning excursion.
3. Whether this is the allowed exhaustion location and whether rejection occurred are separate source branch fields. Do not require exact 0.5W for every source reversal; shallow sweeps are retained.

**Printed constants and limits:** Source discusses 0.1, 0.2, 0.3 and half-width 0.5 areas; no one compulsory depth or tolerance.

**Invalid / unavailable behavior:** Unknown parent/anchor, W<=0, final-extreme selection, interpreting every band touch as confirmation. Apply C04; emit `HOLE:O014:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O014-F1 — numeric fixture:** Synthetic L100/H120/W20 gives upper 0.1=122, 0.2=124, 0.3=126, 0.5=130. A price 121 has depth 0.05W, not 0.5W. A source-selected shallow-sweep fixture is not rejected merely because 130 never trades.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [sessions.projections](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); [family_env.build_env_table](/workspace/implementation/src/trading_research/research/phase1_live/family_env.py); the previous formula labels R-J01/J02/J18/J22, P3-02. Geometry is partial support; choosing the deepest final-AM excursion leaks. Existing behavior is not authority over this procedure.


<a id="o015"></a>

## O015 — The 1.33–1.66 extension area

**Wiki:** [The 1.33–1.66 extension area](/workspace/planning/phase-1-live/wiki/extensions-1-33-1-66.md). **Implementation mode:** compute identified beyond-edge geometry.

Jumbo reads the extended area on either side after expansion and looks for reaction plus a still-relevant destination. The September 9 long combines session-average lows, the extension area and equal highs as its objective. [TBR] pp.20–21; [JR] pp.23–26, 57, 71.

**Not a standalone trade.** Touching an extension, making a daily extreme there and entering a confirmed reversal are separate events. The band is not a P-zone.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source-selected parent span L/H/W and verified beyond-edge coordinate convention. |
| Outputs / units | upper_band=[H+1.33W, H+1.66W], lower_band=[L-1.66W, L-1.33W], parent_id, known_at. |
| ET clock / interval | Selected parent's ET formation; later reaction interval remains branch-specific. |
| Bars / event membership | No new bar construction; later contact uses C02/C06. |
| Reset / persistence | Per independently identified parent span, including a supplied inner span. |
| known_at | Maximum parent geometry and source coordinate-selection time, before touch. |

**Procedure:**

1. Compute all four endpoints as exact decimal prices. Store raw endpoints even when off tick. Verify that label 1.33 is beyond the selected edge in this source convention; do not silently use L+1.33W when H+1.33W is specified.
2. Keep a touch, a later extreme inside the band, and a confirmed reversal as separate outputs. The method still needs prior expansion, reaction and a preselected remaining objective.
3. An inner span can project independently; never replace its W with outer 6–9 or EV width.

**Printed constants and limits:** 1.33 and 1.66 source projection labels; no rounding or fixed target rule.

**Invalid / unavailable behavior:** Unverified coordinate convention, unknown/zero width, wrong parent, later-selected span. Apply C04; emit `HOLE:O015:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O015-F1 — numeric fixture:** Synthetic L100/H120/W20 => upper [146.60, 153.20], lower [66.80, 73.40]. An independently supplied inner L106/H114/W8 gives upper [124.64, 127.28]. Using the outer width for the inner projection is a fixture failure.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [sessions.projections](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); [formulas_jumbo.band_133_166](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); family_env; the previous formula labels R-J08/J09 and P3-02. Beyond-edge geometry is available; modern inner-span identity is partial. Existing behavior is not authority over this procedure.


<a id="o016"></a>

## O016 — Nested source range geometry

**Wiki:** [Nested source range geometry](/workspace/planning/phase-1-live/wiki/nested-range-geometry.md). **Implementation mode:** supplied span + literal geometry; construction hole.

Later charts layer inner profile/range spans inside the outer 6–9 framework and project the selected span independently. These are refinements of the same range loop. [JR] pp.11, 14 and the May 2026 charts; posts 2055344660986364371 / 2026059018750378427.

**Not a standalone trade.** An inner gray box or blue line is not automatically outer-range EQ or EV. Layering is not evidence of another operating method.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source outer and inner IDs/bounds, literal labels/version, supplied span creation/known_at and projection parent. |
| Outputs / units | outer_width, inner_width, parent_binding, inner_geometry_known?, automatic_inner_span=null. |
| ET clock / interval | Each supplied span's own source ET clock; do not inherit 6–9 timing automatically. |
| Bars / event membership | Source drawing/snapshot or complete disclosed construction only. |
| Reset / persistence | Each dated/versioned inner and outer span; never mutate prior geometry. |
| known_at | Supplied pre-use snapshot time; retrospective drawing is source-illustration evidence only. |

**Procedure:**

1. Ingest inner and outer bounds as distinct objects. Compute each width H-L. Bind every projection to the explicitly selected parent ID.
2. Preserve gray/blue literal labels and source names; color is not an algorithm and does not imply EV or EQ.
3. Set automatic span generation null with HOLE:inner_range_construction. Do not create an inner value area or percentage of outer range to imitate the source.

**Printed constants and limits:** No published automatic inner-span selector.

**Invalid / unavailable behavior:** Missing source label/bounds/known_at, negative width, swapped parent, label inferred from color alone. Apply C04; emit `HOLE:O016:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O016-F1 — numeric fixture:** Synthetic outer [100, 120], inner [106, 114] => widths 20 and 8. The two EQ values happen to equal 110; that equality does not merge IDs or prove EV. Remove inner bounds: inner width and its projections are null, not 20.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_range/family_env supply generic geometry; the previous formula labels R-J13/J16/J17 identify nearby components. The exact modern inner-range construction is missing. Existing behavior is not authority over this procedure.


<a id="o017"></a>

## O017 — Session Stat+ envelopes

**Wiki:** [Session Stat+ envelopes](/workspace/planning/phase-1-live/wiki/sessionstat-9-12-envelope.md). **Implementation mode:** supplied source bands only; engine hole.

Session Stat frames likely reach and exhaustion with average/median high-low boxes, a midpoint, extensions and minimum-average shading for the selected session/lookback. It also warns about choppy/low-volatility conditions. [SS] pp.3–12; [JR] pp.23–26.

**Not a standalone trade.** The envelope supplies context and confluence; it is not a blind band-touch trade or the full TBR loop.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Versioned source session/reset/lookback/settings, labeled average/median/min-average bands and their snapshot time. |
| Outputs / units | average_hi/lo, median_hi/lo, min_average_hi/lo, midpoint_when_labeled, source_band_known?, automatic_bands=null. |
| ET clock / interval | Actual source session; a 9–12 label is not a universal reset for all examples. |
| Bars / event membership | No band engine reconstructed; subsequent contact uses source-compatible prices. |
| Reset / persistence | Each supplied source session/settings/snapshot. |
| known_at | Snapshot availability before the tested touch; later calculated session extrema are not prerequisites. |

**Procedure:**

1. Ingest each separately labeled band with its value and settings. Check ordering of endpoints and keep average versus median distinct.
2. Only calculate (hi+lo)/2 when that pair is explicitly the source midpoint's parent; do not relabel another midpoint as Session Stat.
3. Record contact and branch confirmation against the supplied band. Missing min-average construction or values => hole. Do not compute min(mean_up, mean_down), choose a lookback, or substitute current generic envelope output.

**Printed constants and limits:** Only printed/supplied settings for the particular source record. No universal lookback or minimum-average equation.

**Invalid / unavailable behavior:** Absent source value, unknown session/reset/lookback, future snapshot, average/median label substitution. Apply C04; emit `HOLE:O017:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O017-F1 — numeric fixture:** Synthetic supplied average [100, 120], median [102, 118], no min-average value: average midpoint 110; median endpoints remain 102/118; min-average=null. The min of the two widths, 16, is not a permissible min-average band.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_env.build_env_table](/workspace/implementation/src/trading_research/research/phase1_live/family_env.py); the previous formula labels R-J11/P3-02. Average-excursion approximations exist; the exact minimum-average engine is missing. Existing behavior is not authority over this procedure.


<a id="o018"></a>

## O018 — Jumbo EVRange

**Wiki:** [Jumbo EVRange](/workspace/planning/phase-1-live/wiki/ev-range-expected-move.md). **Implementation mode:** supplied source reference only.

EVRange is a separately named expected-range reference in the raw examples, used alongside the time-based range to frame rotations and targets. Its bands and midpoint are distinct from 6–9 EQ. [JR] pp.3, 38–43 and the late-August/early-September 2026 charts.

**Not a standalone trade.** EVRange does not define an independent entry, and a generic historical-average envelope is not automatically the author’s EVRange.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal EVRange band/midpoint values, source date/version/anchor and verified known_at. |
| Outputs / units | ev_low, ev_high, ev_mid_if_supplied, ev_reference_known?, automatic_ev=null. |
| ET clock / interval | Source EV anchor/time; no borrowed 6–9 or cash-open reset. |
| Bars / event membership | Supplied source snapshot; later contact can use prices. |
| Reset / persistence | New source snapshot/version; retain prior values as historical states. |
| known_at | Verified source snapshot time before candidate use, otherwise unknown/source illustration. |

**Procedure:**

1. Retain EV values under their literal label and parent identity. If the source supplies only a midpoint, do not invent a width/band around it.
2. Check subsequent contact using that supplied value, with the selected TBR branch's context and confirmation.
3. Never call an average-excursion estimator, inner profile box or 6–9EQ the author EVRange. The engine is outside this pack.

**Printed constants and limits:** No published EV estimator, lookback, weight or reset.

**Invalid / unavailable behavior:** Missing source band/availability, label inferred from blue line, unsupported reconstruction. Apply C04; emit `HOLE:O018:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O018-F1 — numeric fixture:** Synthetic source EV mid 111 and 6–9EQ110 remain different. A price 110 touches EQ but not exact EV mid 111. Remove EV snapshot: ev_reference_known=null even if a generic envelope returns 111.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_env.build_env_table](/workspace/implementation/src/trading_research/research/phase1_live/family_env.py); the previous formula labels R-J13. The exact EV estimator is unpublished; the current average-excursion construction is a named approximation. Existing behavior is not authority over this procedure.


<a id="o019"></a>

## O019 — Time-anchored P-zones

**Wiki:** [Time-anchored P-zones](/workspace/planning/phase-1-live/wiki/p-zones-benchmark.md). **Implementation mode:** supplied source zone/state only.

The source shows P-zones with session anchors, learning-window/percentile controls and invalidation settings. The January low → range-open and December 10 am P-zone → London-low examples describe directed paths. [JR] pp.16–18, 53–55, 58–62.

**Not a standalone trade.** A settings panel does not disclose the proprietary formula. A time anchor does not prove an entry at that time; a path arrow is not a price inequality.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal P-zone bounds, anchor, source settings/version, known_at, supplied active/invalidation history and directed source/target IDs. |
| Outputs / units | pzone_id, lo, hi, anchor_at, source_zone_known?, active_at_use?, directed_path_recorded. |
| ET clock / interval | Actual zone anchor and source action window; 09:00/10:00 examples do not imply entry then. |
| Bars / event membership | Supplied zone snapshots and later price/confirmation events. |
| Reset / persistence | Source zone/version; active-state changes append events, not new retroactive bounds. |
| known_at | Actual source snapshot availability; anchor time alone does not prove known_at or fill_at. |

**Procedure:**

1. Ingest labeled bounds and their configuration without recreating the engine. Keep learning-window/percentile settings as supplied metadata, not a recovered formula.
2. Apply only a supplied source invalidation rule/event. If absent, active_at_use is unknown where it is required.
3. Store paths such as low→range-open or 10 am P-zone→London-low as ordered identities. A path arrow is not a numerical inequality. Require zone_known_at<=touch and actual confirmation before entry.

**Printed constants and limits:** No recoverable P-zone engine or universal invalidation threshold. Only literal case settings may be retained.

**Invalid / unavailable behavior:** Anchor mistaken for fill, missing active-state rule, inferred quantile substitute, forced 09:40 timing on another source case. Apply C04; emit `HOLE:O019:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O019-F1 — numeric fixture:** Synthetic zone [100, 102], anchor 09:00, verified snapshot 09:02, touch 09:45, decision 09:47: known-before-touch=true; entry_at09:00 is not implied. With only anchor and no availability evidence, source_zone_known=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_env.build_env_table](/workspace/implementation/src/trading_research/research/phase1_live/family_env.py); the previous formula labels R-J12/P3-02. Exact P-zone construction and active-zone state are missing; historical quantile bands are approximations. Existing behavior is not authority over this procedure.


<a id="o020"></a>

## O020 — PD RTH Range+ destinations

**Wiki:** [PD RTH Range+ destinations](/workspace/planning/phase-1-live/wiki/pd-rth-range-plus.md). **Implementation mode:** compute specified prior range; source direction/imbalance selection can be holes.

The RTH-only application uses prior 09:30–16:00 highs/lows and M15/H1 imbalances, waits for current RTH direction and then pursues the named objective within the range framework. An ETH sweep does not consume this expressly RTH-only objective. [TBR] pp.32–35.

**Not a standalone trade.** Prior extremes and gaps are context/destinations, not an entry on contact or a separate system. This scope does not erase overnight purge information in another branch.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Prior 09:30–16:00ET prices, M15/H1 source imbalance IDs/bounds, current pre-entry direction record, source consumption scope. |
| Outputs / units | prior_rth_high/low, known_at, rth_active_objectives[], chosen_draw?, current_direction?. |
| ET clock / interval | Prior RTH [09:30, 16:00)ET; current RTH target-consumption scope. |
| Bars / event membership | Complete range bars plus source-defined 15/60-minute imbalance candles. |
| Reset / persistence | New prior-RTH reference per completed session; persistent RTH-only visit ledger. |
| known_at | Prior range at 16:00; imbalance at its defining confirmation; direction only when observed before decision. |

**Procedure:**

1. Compute prior RTH H/L from its complete fixed window. Store each source-selected higher-timeframe imbalance independently; use the FVG recipe's explicit definition/holes.
2. Initialize RTH-only objectives. Preserve overnight hits in a separate log; they do not retire these objectives.
3. Choose direction and objective from a supplied pre-entry source read or complete source procedure. Do not use final AM path direction. Measure reach strictly after entry in the source scope.

**Printed constants and limits:** 09:30–16:00ET; M15/H1 source timeframe labels.

**Invalid / unavailable behavior:** Prior full-session substituted, current final high/low used as direction, missing imbalance convention, ETH consumption incorrectly retires RTH reference. Apply C04; emit `HOLE:O020:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O020-F1 — numeric fixture:** Synthetic prior RTH H120/L100; ETH price 121 at 02:00 does not consume upper RTH objective 120. Current RTH source long declared 09:40 and target 120, reached 10:05, preserves the correct ordering; choosing long only because the 12:00 close rose fails.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.j19_draw/j19_pd_touch/j19_htf_fvg](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); family_levels; the previous formula labels R-J19. Final morning direction or reach cannot establish an earlier setup. Existing behavior is not authority over this procedure.


<a id="o021"></a>

## O021 — Jumbo reversal and action windows

**Wiki:** [Jumbo reversal and action windows](/workspace/planning/phase-1-live/wiki/reversal-time-window.md). **Implementation mode:** check source-selected times.

The manual's Judas opening leg runs from the 09:30 open toward exhaustion, with reversal/exit framing around 09:40–09:50. In the purged continuation case that interval can be an add/continuation window. Later time-anchored examples use their actual clocks. [TBR] pp.8–15; [JR] pp.53–55.

**Not a standalone trade.** Being inside the interval does not confirm reversal, and a final reversal-time histogram cannot choose a live entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Method branch, exact source action interval/purpose, sweep/confirmation/decision/exit events; any supplied source delay. |
| Outputs / units | at_rth_open, source_time_window:boolean?, exit_window_recorded, actual_action_at. |
| ET clock / interval | Manual outbound 09:30 and reversal/exit framing 09:40–09:50ET; later source cases retain own clocks. |
| Bars / event membership | Event times or completed confirmation bars; no trading from a histogram mode. |
| Reset / persistence | Per source branch/attempt; outbound and reversal are distinct candidate legs. |
| known_at | Window instruction before decision; actual confirmation/exit when it happens. |

**Procedure:**

1. Bind the clock to the selected purpose: outbound entry at cash open, later exit window, reversal confirmation, or continuation/add. Do not use one Boolean for all purposes.
2. Compare actual event time with the supplied window. Where exact endpoint inclusivity/tolerance is not stated, report interior membership directly and an exact boundary ambiguity as a hole rather than adding a minute.
3. A news-related delayed reversal needs the observed delayed source sequence, not merely the first touch after news.

**Printed constants and limits:** 09:30 and 09:40–09:50 manual framing only; no extra tolerance or universal news delay.

**Invalid / unavailable behavior:** Wrong branch/purpose, anchor mistaken for entry, missing boundary convention, future histogram selects live time. Apply C04; emit `HOLE:O021:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O021-F1 — numeric fixture:** Synthetic manual reversal confirmation 09:45 is inside 09:40–09:50; 09:55 is outside. A timed P-zone case confirmed 10:07 is not rejected by the manual window unless that case actually requires it. An exact 09:50 boundary remains unresolved if source inclusivity is absent.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-J01/J02/J20; clock and grid ingredients. A joint source-timed branch record is missing; first post-news touch is not necessarily the delayed reversal. Existing behavior is not authority over this procedure.


<a id="o022"></a>

## O022 — Source session-cleanliness assessment

**Wiki:** [Source session-cleanliness assessment](/workspace/planning/phase-1-live/wiki/clean-session-label.md). **Implementation mode:** supplied qualitative context only.

The raw record sometimes favors London as the cleaner session in that market cycle. The manual relates AM expansion/consolidation to later-session behavior. This is an observed session-selection context. [TBR] p.36; [JR] pp.46, 50–51, 63–66.

**Not a standalone trade.** Cleaner is not a disclosed rolling-ten-day selector or a separate London entry rule.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author/date, selected session/version, reason for cleaner-session preference, evidence interval and known_at. |
| Outputs / units | source_cleanliness_label, session_selected_before_use, automatic_cleanliness=null. |
| ET clock / interval | Source session and observation interval ET. |
| Bars / event membership | Source context record with supporting prior observations, not today's final path. |
| Reset / persistence | Each contemporaneous source judgment/version; no automatic rolling window. |
| known_at | When that judgment was recorded before the selected session/decision. |

**Procedure:**

1. Retain the source session preference and stated reason. Validate that the reason was available before selection.
2. Do not calculate a rolling-ten-day winner/cleanliness score, select the session with the best final reversal, or treat the label as an entry confirmation.
3. If no quantitative selector or source judgment is supplied, return a hole and leave session selection unresolved.

**Printed constants and limits:** No published lookback, cleanliness score or threshold.

**Invalid / unavailable behavior:** Retrospective winner-selected session, missing reason/time or incompatible modern London clock. Apply C04; emit `HOLE:O022:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O022-F1 — numeric fixture:** Synthetic London preference recorded 02:00 for a 03:30 action can be a supplied context. A 12:00 note that London was clean cannot establish a 02:00 preference. Ten profitable London days alone do not generate a faithful selector.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_clocks and the previous formula labels R-J09/J23 provide measurements. A source-defined quantitative cleanliness selector is missing. Existing behavior is not authority over this procedure.


<a id="o023"></a>

## O023 — Accumulation, manipulation and distribution phases

**Wiki:** [Accumulation, manipulation and distribution phases](/workspace/planning/phase-1-live/wiki/amd-phase-labels.md). **Implementation mode:** source description/state audit only.

The range narrative can describe formation/balance, a sweep or misleading opening move, and subsequent directional distribution. Its role is to explain the observed path within the TBR cases. [TBR] pp.6–15.

**Not a standalone trade.** A retrospective phase name is not another system and does not determine direction before the actual failure or continuation evidence.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Parent range/branch, supplied phase names, transition evidence keys and contemporaneous versus retrospective flag. |
| Outputs / units | phase_label, phase_known_at, used_as_context:boolean, automatic_phase=null. |
| ET clock / interval | Parent formation/action clocks ET. |
| Bars / event membership | Only elapsed events can support a live label; final path remains an outcome. |
| Reset / persistence | Per range/source narrative; phase revisions append rather than rewrite. |
| known_at | At actual evidence/annotation time; not at the earlier bar named after the fact. |

**Procedure:**

1. Record formation/balance, sweep/manipulation and directional distribution in the source's stated order where evidence exists.
2. Validate the label's use time. An explanation based on a completed path cannot supply earlier direction.
3. No universal phase detector is disclosed; do not implement one from arbitrary range/volume thresholds.

**Printed constants and limits:** None beyond selected source clocks.

**Invalid / unavailable behavior:** Future path supplies earlier phase, phase enum used as a complete entry, source sequence absent. Apply C04; emit `HOLE:O023:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O023-F1 — numeric fixture:** Synthetic accumulation 06:00–09:00, sweep 09:35, distribution observed 10:15: the 10:15 distribution label is unavailable at 09:30. The sequence timestamps are recordable; automatic distribution-before-open is null/causal fail if asserted true.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_path and the previous formula labels R-J01–J05 hold related range/path ingredients. A uniquely disclosed universal phase detector is missing. Existing behavior is not authority over this procedure.


<a id="o024"></a>

## O024 — Jumbo failure signatures and three attempts

**Wiki:** [Jumbo failure signatures and three attempts](/workspace/planning/phase-1-live/wiki/jumbo-failure-attempts.md). **Implementation mode:** attempt ledger and literal allocation audit.

The manual rejects the reversal idea after three failed attempts at the same level, persistent strong bodies/volume through it, or absent rejection. It says to exit/observe and, if continuing after failure, reduce allocation at least 50%. [TBR] pp.36–37.

**Not a standalone trade.** Three adjacent touch bars are not three trades or three distinct reversal attempts. Strong continuation through a level does not retrospectively make a failed fade successful.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Same source level/branch, distinct admitted attempt/exit IDs, outcome and timing; continuing-through evidence; original and subsequent allocation. |
| Outputs / units | failed_attempt_count, three_failed_attempts, reversal_invalidated?, later_allocation_ok?. |
| ET clock / interval | Source session ET; count only completed failures before the next decision. |
| Bars / event membership | Attempt records plus supporting source confirmation/failure events; no touch-bar counting. |
| Reset / persistence | New source level/thesis case where explicitly reset; a re-entry name does not erase failed attempts. |
| known_at | At third completed failure or other observed source invalidation; allocation check at later allocation decision. |

**Procedure:**

1. Group distinct attempt IDs at the same level/branch. Count only failures observed before the evaluation key. Three consecutive rows from one contact count as one touch and zero additional attempts.
2. The third failed attempt supplies the source stop/observe condition. Strong continued bodies/volume or absent rejection can also invalidate when that qualitative source evidence is supplied; no numeric strength detector is invented.
3. If source records continued trading after failure, require new_allocation<=0.50*prior_allocation. The at-least 50% reduction is the stated rule, not a mandatory next trade.

**Printed constants and limits:** 3 failed attempts; allocation reduction at least 50% in the stated continuation-after-failure case.

**Invalid / unavailable behavior:** Duplicate IDs; failures resolved after evaluation; undefined allocation units; turning one touch into three attempts. Apply C04; emit `HOLE:O024:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O024-F1 — numeric fixture:** Synthetic attempts A1/A2/A3 end 09:41/09:44/09:48 as failures: count at 09:45=2, at 09:49=3. Prior allocation 4 units permits at most 2 units if continuing. Three 09:40 touch rows under A1 still count one attempt.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.j22_three_strike/j22_failed](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-J22/J24. Distinct attempt and management ledgers are missing. Existing behavior is not authority over this procedure.


<a id="o025"></a>

## O025 — Opening-range midpoint reference

**Wiki:** [Opening-range midpoint reference](/workspace/planning/phase-1-live/wiki/opening-range-midpoint.md). **Implementation mode:** compute only for a verified source OR.

The July 21 raw post describes adapting with the 6–9 range and OR-mid retracements, taking nearer results and breakevens rather than assuming continuation. The OR is a separate source-selected reference. [JR] p.40, post 2079574963640512677; [TBR] pp.7, 24.

**Not a standalone trade.** OR midpoint is not 6–9 EQ or a standalone opening-range system. The source example does not disclose a universal OR duration for every chart.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source opening-range start/end/version, complete H/L, distinct parent ID and known_at. |
| Outputs / units | or_mid=(or_high+or_low)/2, or_known, subsequent_mid_retrace. |
| ET clock / interval | Source-selected OR clock; source does not publish a universal duration for every chart. |
| Bars / event membership | Complete source OR bars/events, later contact after formation. |
| Reset / persistence | Each verified OR instance; never alias 6–9EQ. |
| known_at | OR end after complete data; source clock unknown meansor_known=null. |

**Procedure:**

1. Require explicit OR identity and completed bounds. Calculate the exact midpoint from its own high/low.
2. Observe later return using the selected TBR case; nearer objectives and breakevens are source management records, not a universal continuation rule.
3. Without an OR duration, return HOLE:or_clock rather than choosing 5/15/30 minutes.

**Printed constants and limits:** Midpoint 0.5; no general OR duration.

**Invalid / unavailable behavior:** Unverified window, later favorable interval selection, mixed parent, pre-end use. Apply C04; emit `HOLE:O025:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O025-F1 — numeric fixture:** Synthetic verified ORH108/L100 produces mid 104 known at its stated end.6–9EQ110 remains different. Remove the OR end: midpoint can be retained as supplied geometry but automatic OR construction/availability is null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** clocks/family_clocks and formulas_jumbo range helpers; the previous formula labels R-J05/J23. Source-specific OR clock and entry-linked retrace remain partial. Existing behavior is not authority over this procedure.


<a id="o026"></a>

## O026 — Confirmed swing midpoint retrace

**Wiki:** [Confirmed swing midpoint retrace](/workspace/planning/phase-1-live/wiki/confirmed-swing-midpoint.md). **Implementation mode:** compute supplied confirmed swing; automatic pivot hole.

The January 14 post describes clean retraces to each swing's midpoint on a trend toward the January 4 gap. It reports an observation, not a new exact swing-entry algorithm. [JR] p.51, post 2011483105089974551; [XF] p.26.

**Not a standalone trade.** A swing midpoint is not the 6–9 EQ, and no universal fractal length or trend-day detector is supplied.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source swing high/low IDs and prices, price times, confirmation times, source chart timeframe. |
| Outputs / units | swing_mid=(high+low)/2, swing_known_at, later_mid_contact. |
| ET clock / interval | Source swing/confirmation times ET, not a preset opening window. |
| Bars / event membership | Actual cited source bars; no universal fractal length or 1-minute substitution. |
| Reset / persistence | Each distinct confirmed swing pair. |
| known_at | Maximum endpoint confirmation time, not the earlier pivot's timestamp. |

**Procedure:**

1. Check two endpoints belong to the same source-defined swing. Compute exact midpoint only after both are confirmed.
2. Measure later retrace from observationsafterknown_at. Keep final trend-day label separate from the pre-entry direction.
3. If endpoint detector/confirmation is not supplied, automatic swing selection=null. Do not choose first independent high/low or a favorable future pivot.

**Printed constants and limits:** Midpoint 0.5; no printed universal fractal length.

**Invalid / unavailable behavior:** Backdated confirmation, unrelated endpoints, later trend label selectswing, missing source bar frame. Apply C04; emit `HOLE:O026:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O026-F1 — numeric fixture:** Synthetic low 100 priced 09:35 confirmed 09:40 and high 120 priced 09:50 confirmed 09:55 produce midpoint 110 known 09:55. A 09:52 touch 110 cannot count as post-confirmation retrace; 10:00 touch can.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.j25_fractal_swings/j25_mid_retrace_hold](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-J25. Current one-minute/backdated or independently chosen pivots do not establish the source's completed swing. Existing behavior is not authority over this procedure.


<a id="o027"></a>

## O027 — Relative-volume context at the open

**Wiki:** [Relative-volume context at the open](/workspace/planning/phase-1-live/wiki/relative-volume.md). **Implementation mode:** compute explicit ratio; source baseline/class hole.

The opening-location discussion uses participation to frame continuation versus rotation, alongside prior value/range location and overnight condition. It does not make one high-RVOL cell the only continuation case. [TBR] pp.16–24; [JR] pp.33–39, 48–49.

**Not a standalone trade.** Relative volume is context, not an entry trigger; a first-five-minute measure cannot be known at the cash-open instant.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Current completed source volume window, explicit prior comparison sessions with same clock and their volumes, baseline statistic/configuration. |
| Outputs / units | current_volume, baseline_volume, rvol=current/baseline, source_high_rvol?. |
| ET clock / interval | Selected source participation window, including 09:30–09:35 where used; baseline same time-of-day. |
| Bars / event membership | Executed sizes or complete bar volumes with consistent universe and coverage. |
| Reset / persistence | Each current window; freeze baseline membership before that window. |
| known_at | Maximum baseline and current window-end availability; never cash-open if window ends later. |

**Procedure:**

1. Aggregate current volume exactly inside its selected interval. Compute only the supplied baseline statistic over prior complete comparable intervals.
2. Divide by positive baseline. Store sample IDs and each known_at. If baseline formula/lookback is missing, ratio and high classification are holes, not a chosen 20-day average.
3. A supplied ratio does not define a universal continuation permission; keep the opening cell and source interpretation.

**Printed constants and limits:** Only source window and supplied baseline; no universal high cutoff/lookback.

**Invalid / unavailable behavior:** Incomplete current window, baseline<=0, mismatched time-of-day, future baseline member, unset classification threshold. Apply C04; emit `HOLE:O027:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O027-F1 — numeric fixture:** Synthetic supplied prior window volumes 100/200/300 with explicitly supplied arithmetic mean 200; current 09:30–09:35 volume 300 =>rvol 1.5 known 09:35. At 09:31 unavailable. Without the baseline or high threshold, source_high_rvol=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_open.build_open_table](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); the previous formula labels R-J06/J21. Source-exact baseline/threshold and early-decision availability are partial. Existing behavior is not authority over this procedure.


<a id="o028"></a>

## O028 — Equal-high or equal-low liquidity objective

**Wiki:** [Equal-high or equal-low liquidity objective](/workspace/planning/phase-1-live/wiki/equal-high-low-objectives.md). **Implementation mode:** supplied reference + explicit equality measurement.

The extension-reaction example points toward still-owed equal highs after the source location produces a long reaction. Repeated prices are a destination only when the source selects them. [JR] pp.23–26.

**Not a standalone trade.** Repeated-looking highs do not by themselves create an entry or a guaranteed liquidity run.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source reference point IDs/prices/times, chosen equality criterion/tolerance, objective band and pre-entry selection. |
| Outputs / units | equal_reference_band, contributors[], reference_known, remaining_objective?. |
| ET clock / interval | Contributing source event times ET; all must precede objective use. |
| Bars / event membership | Source-confirmed extrema or supplied line; no future double top selection. |
| Reset / persistence | Each source objective identity; later consumption tracked separately. |
| known_at | Maximum contributor confirmation and source selection time. |

**Procedure:**

1. Retain every source contributor and its price. For literal exact equality compare exact native prices; for a drawn approximate band require the source band/tolerance.
2. Do not create an arbitrary two-tick cluster or select later highs as preplanned liquidity. A source objective must be chosen before entry.
3. Use the remaining-objective ledger and entry specific outcome to check later reach, keeping equality detection separate from entry.

**Printed constants and limits:** No universal equality tolerance or required touch count.

**Invalid / unavailable behavior:** Future contributor, guessed tolerance, missing objective priority or band, later hit selects reference. Apply C04; emit `HOLE:O028:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O028-F1 — numeric fixture:** Synthetic confirmed highs 120.00 and 120.00 have exact equality; 120.00 and 120.25 do not. A source-defined band [120, 120.25] may contain both, but without that sourced band a near-equal classification is null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_levels and [formulas_jumbo.j10_draw](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) are related; the previous formula labels R-J10. Source-exact equality tolerance and target-selection ledger are missing. Existing behavior is not authority over this procedure.


<a id="o029"></a>

## O029 — Scheduled news and changing information

**Wiki:** [Scheduled news and changing information](/workspace/planning/phase-1-live/wiki/news-event-context.md). **Implementation mode:** timestamped schedule/release ledger; response selection hole.

News and range conditions change target ambition or thesis validity. Jumbo discusses reduced expectations and delayed cycles; Sires maps the news plan and treats new information as a possible thesis death. [TBR] pp.24, 36–37; [C1] pp.3–6; [AVG] pp.27–29. Green Bird's calendar/bias commentary is context, not an extra trigger. [GB] pp.30–40.

**Not a standalone trade.** A release date or the first touch after a release is not the source's reversal signal. A past macro conclusion is not a current recommendation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Calendar event ID, scheduled ET time/timezone, schedule publication key; actual release key, vintage/value if supplied; source thesis/target response and decision key. |
| Outputs / units | schedule_known, release_known, new_information_known, source_response?, thesis_revision_id?. |
| ET clock / interval | Each event's actual ET clock; date-only rows have no intraday release time. |
| Bars / event membership | No bars required for schedule; market reaction uses separately identified complete bars/events. |
| Reset / persistence | Per event/vintage and thesis revision; never overwrite a prior release with a revision. |
| known_at | Schedule at publication; release at actual availability; response at its observed source decision. |

**Procedure:**

1. Match event identity and timezone. Preserve scheduled and actual release times separately. An event scheduled for 08:30 may be known earlier; its released value is not.
2. At each decision select only schedule/releases with known_at no later than that decision. Null time or absent vintage returns a hole for that information.
3. Record the source's resulting delay, reduced ambition or thesis change. Do not infer a universal news delay, force every first post-release touch to be a reversal, or initialize news_change=false when the calendar is incomplete.

**Printed constants and limits:** Only the supplied event clock; no universal event-response threshold.

**Invalid / unavailable behavior:** Date-only timestamp promoted to 00:00/08:30 release; revised value backdated; incomplete calendar treated as proof of no news. Apply C04; emit `HOLE:O029:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O029-F1 — numeric fixture:** Synthetic scheduled release 08:30 known the prior day, actual value received 08:30:02: at 08:30:01 schedule_known=true and release_known=false. A thesis revision recorded 08:31 is unavailable at 08:30:30. A date-only event gives release_known=null at either intraday decision.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_levels.load_red_folder](/workspace/implementation/src/trading_research/research/phase1_live/family_levels.py); [formulas_jumbo.j21_class/j21_targets](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_r03_thesis](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-J20/J21/R-R03. Date-only calendar entries do not provide complete event times or release information. Existing behavior is not authority over this procedure.


<a id="o030"></a>

## O030 — Session VWAP

**Wiki:** [Session VWAP](/workspace/planning/phase-1-live/wiki/vwap-session.md). **Implementation mode:** exact trade-weighted arithmetic for verified reset; author reset/basis hole where absent.

VWAP is the auction's volume-weighted average under the selected reset and price basis. Green Bird's explicit continuation returns to VWAP after closing above both session highs; Sires uses VWAP as fair-value location or destination within a thesis. [GB] p.33, posts 2026329904690712970 / 2026386393820283204; [VWAP] pp.3–8; [CONT] p.5.

**Not a standalone trade.** A VWAP touch is not a trade. Green Bird's continuation does not inherit Sires's fade or tape-confirmation rule, and the session reset is not universally established from a settings label.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Instrument, source reset key and anchor convention; canonical executed trades price p_i and size v_i, source weighting basis, as_of key. |
| Outputs / units | sum_v, sum_pv, vwap=sum_pv/sum_v, reset_id, basis, as_of, known_at. |
| ET clock / interval | Selected source session/reset in ET; neither 18:00 nor 09:30 is a universal default. |
| Bars / event membership | Exact version uses executed trades. Bar HLC3=(H+L+C)/3 times bar volume is a separately named approximation and cannot satisfy author-exact evidence without source support. |
| Reset / persistence | Set both sums to zero at verified anchor; terminate at contract change or unknown coverage gap. |
| known_at | As_of after all included events are available; a band frozen for a touch uses only records before that touch (strictly earlier key unless source explicitly includes the contact trade). |

**Procedure:**

1. Select one canonical executed tape and instrument under C03. Include events within the verified reset-to-as_of interval; quote updates do not contribute volume.
2. Accumulate sum_v=Σv and sum_pv=Σ(p×v) exactly. Return null if sum_v=0; otherwise divide. Unknown aggressor side does not remove an otherwise valid executed trade from total VWAP.
3. Store the value snapshot and its parent reset ID. Evaluate later contact against that snapshot. If Green Bird's reset/basis is not supplied, his faithful vwap_known is null even when a named comparison VWAP can be calculated.

**Printed constants and limits:** No universal reset or lookback. Volume weighting is the stated meaning; source-specific price basis must be identified.

**Invalid / unavailable behavior:** Future volume; duplicate tape; quote size as volume; zero denominator; cross-contract sum; unverified reset labeled faithful. Apply C04; emit `HOLE:O030:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O030-F1 — numeric fixture:** Synthetic verified reset: trade 100×2 then 104×1 gives sum_v=3, sum_pv=304, VWAP=304/3=101.333333…. A later 110×3 changes the later snapshot to 634/6=105.666667, but cannot change the earlier contact value. Missing reset => faithful VWAP null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.running_vwap](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); family_value; the previous formula labels R-F01/F03 and partial GB level ingredients. HLC3/bar-volume VWAP is a named approximation; Green Bird's exact reset is unpublished. Existing behavior is not authority over this procedure.


<a id="o031"></a>

## O031 — Anchored VWAP

**Wiki:** [Anchored VWAP](/workspace/planning/phase-1-live/wiki/vwap-anchored.md). **Implementation mode:** verified source anchor plus session-VWAP accumulator.

The lesson anchors VWAP to a relevant swing, event or weekly/monthly context and uses it as confluence with the current auction read. The anchor must be meaningful before the trade. [VWAP] pp.7–8.

**Not a standalone trade.** An anchor selected after seeing the best reaction is not contemporaneous evidence. Anchored VWAP is not another complete system.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Anchor event/swing ID, anchor price time, confirmation/selection key and source reason; weighting convention; executed events after anchor; evaluation key. |
| Outputs / units | anchor_id, anchor_price_at, anchor_known_at, avwap, as_of, usable_at. |
| ET clock / interval | Actual source anchor ET; weekly, monthly, swing and event anchors remain distinct. |
| Bars / event membership | Trade accumulation as session-vwap; a swing detector is not supplied by this object. |
| Reset / persistence | Start at the selected anchor; a new anchor makes a new series, not a rewrite of past snapshots. |
| known_at | max(anchor confirmation, source selection, latest included input availability); no use before anchor was known. |

**Procedure:**

1. Require the cited source reason and confirmed anchor identity. If the source gives no anchor/confirmation procedure, emit that hole instead of selecting the best-reacting pivot.
2. Apply the exact VWAP accumulation over the selected source interval. Historical events between price time and confirmation may be aggregated only after the anchor is confirmed; their resulting value is not backdated.
3. Keep this confluence separate from local entry confirmation.

**Printed constants and limits:** No automatic pivot length or mandatory weekly/monthly reset.

**Invalid / unavailable behavior:** Future-confirmed anchor used early; anchor chosen by outcome; unknown source basis. Apply C04; emit `HOLE:O031:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O031-F1 — numeric fixture:** Synthetic swing priced at 09:40, confirmed/selected at 09:50; included trades 100×1 and 102×3 give AVWAP=101.5. This value is usable no earlier than 09:50; a 09:45 touch is not a confirmed-anchor test.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.running_vwap](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) provides cumulative ingredients; the previous formula labels R-F03/P3-02. Source event/swing anchors and confirmation-time joins are missing. Existing behavior is not authority over this procedure.


<a id="o032"></a>

## O032 — VWAP deviation bands

**Wiki:** [VWAP deviation bands](/workspace/planning/phase-1-live/wiki/vwap-deviations.md). **Implementation mode:** band algebra from verified deviation; variance/reset construction hole.

The lesson draws standard-deviation bands around the selected VWAP and reads absorption/rejection at a chosen deviation. ±1/±2 are displayed; 2.5 and optional 3 also appear in the discussion. [VWAP] pp.3–8.

**Not a standalone trade.** A ±2 touch is not a universal fade, and changing band multiplier/reset is not automatically the source's chosen setting.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Parent VWAP snapshot μ, supplied/source-defined standard deviation σ with weighting convention, selected multiplier k and band side, availability. |
| Outputs / units | upper=μ+kσ, lower=μ-kσ, band_id, variance_convention, as_of. |
| ET clock / interval | Parent anchor/session ET; use frozen pre-contact snapshot. |
| Bars / event membership | Same source weighting universe as parent; do not combine trade VWAP with an arbitrary unweighted rolling close deviation. |
| Reset / persistence | Exactly parent reset and variance state; no independent rolling window. |
| known_at | Maximum parent and deviation snapshot availability before contact. |

**Procedure:**

1. Require σ≥0 and a source-defined calculation or supplied source σ/band. If variance weighting, degrees of freedom or reset is absent, automatic σ is a hole; do not choose population/sample variance by taste.
2. Calculate μ±kσ for the specifically selected displayed multiplier. Keep all source variants labeled and do not select the best later reaction.
3. A band contact remains location. The selected Sires branch still requires auction context and flow confirmation.

**Printed constants and limits:** Displayed ±1 and ±2; 2.5 and optional 3 are separate source variants, not a universal ±2 fade.

**Invalid / unavailable behavior:** Unknown variance/reset supplied as exact; future band snapshot; k chosen after outcome. Apply C04; emit `HOLE:O032:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O032-F1 — numeric fixture:** Synthetic supplied μ=100, σ=2: k=2 produces [96, 104], k=2.5 [95, 105], k=3 [94, 106]. Contact 104 touches the k=2 upper band; it does not prove a fade. Remove σ convention/value: faithful calculated band null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.running_vwap/r_f01_vwap_fade](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F01/F03/P3-02. Exact source variance/reset construction and local confirmation are partial. Existing behavior is not authority over this procedure.


<a id="o033"></a>

## O033 — Source gamma regime

**Wiki:** [Source gamma regime](/workspace/planning/phase-1-live/wiki/gex-regime.md). **Implementation mode:** source snapshot and branch-permission audit; engine hole.

Sires's framework uses the relevant 0DTE complex to frame balance/responsive behavior versus aggressive continuation. BIG explicitly restricts aggressive OFM to short gamma and its failure-of-aggression balance fade to long gamma. Other recaps preserve their own regime evidence, including disagreement near the flip. [GEX] pp.4–20; [BIG] pp.14–18; [K18] p.4.

**Not a standalone trade.** A generic sign scenario is not the source's dealer map, and it does not impose one unanimously signed gamma gate on every historical Sires trade.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Native product, expiry cohort, source regime/sign interpretation and snapshot time; branch ID; uncertainty/reread record. |
| Outputs / units | source_regime:short_gamma/long_gamma/uncertain/null, branch_regime_ok?, native_identity_ok, reread_at?. |
| ET clock / interval | Snapshot before branch choice; reread at the next source-requested impulse. |
| Bars / event membership | Options/source panel snapshot; no price bar computes dealer position sign. |
| Reset / persistence | Each product/expiry/source-panel version and later reread. |
| known_at | Actual snapshot availability, not request date or final OI. |

**Procedure:**

1. Ingest the source regime with its sign/model convention and native 0DTE identity. Keep uncertain or conflicting reads explicit.
2. For BIG aggressive OFM require short_gamma; for BIG failure-of-aggression balance fade require long_gamma. Apply no universal regime sign to all other Sires executions.
3. Missing dealer-position assumptions or engine => automatic regime null. A pooled 0–14DTE assumed-sign result cannot fill this field.

**Printed constants and limits:** Source-specific 0DTE cohort; BIG short-gamma OFM versus long-gamma balance-fade permissions only.

**Invalid / unavailable behavior:** Wrong product/expiry; post-decision snapshot; sign/price-versus-flip conventions combined opportunistically. Apply C04; emit `HOLE:O033:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O033-F1 — numeric fixture:** Synthetic supplied source regime long_gamma, observed at 09:20 and used at 09:30, gives BIG aggressive-OFM regime permission=false and BIG balance-fade regime permission=true. The latter still needs its other gates. With an uncertain source regime both permissions are null; later direction cannot select them.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_gex._gex_day/build_gex_table](/workspace/implementation/src/trading_research/research/phase1_live/family_gex.py); family_options; the previous formula labels R-R01. Pooled 0–14DTE assumed-sign output is not an author-exact 0DTE regime. Existing behavior is not authority over this procedure.


<a id="o034"></a>

## O034 — Native options-chain identity

**Wiki:** [Native options-chain identity](/workspace/planning/phase-1-live/wiki/options-nodes.md). **Implementation mode:** native contract identity and temporal cohort filter.

The source gamma read uses the relevant native options complex, particularly QQQ/SPY 0DTE context for the Nasdaq/S&P application. Product, expiry and price units must remain attached to the resulting levels. [GEX] pp.4–19.

**Not a standalone trade.** An ETF strike, index strike and futures price are not interchangeable. A repository comparison chain is not a newly disclosed author method.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | symbol, option class, expiration, strike, right, osi_symbol; observation ET date and source snapshot times; OI/volume/Greek provenance and explicit mapping if any. |
| Outputs / units | native_contract_key, is_0dte, native_strike, source_product_ok, mapped_price? with mapping provenance. |
| ET clock / interval | Compare expiry calendar date to snapshot's ET date, not UTC date or file partition date. |
| Bars / event membership | Options contracts/quotes/OI native records; not futures OHLC. |
| Reset / persistence | Per source product/expiry/snapshot; never merge products merely by strike. |
| known_at | Each required record's true availability; OI request_date is insufficient. |

**Procedure:**

1. Construct identity from product/class/expiry/strike/right. Filter to the source-native product and expiry cohort before aggregation.
2. For 0DTE require expiration_date_et=observation_date_et. Keep later expiry observations as separate comparison data only.
3. Preserve ETF/index/futures units. Produce a mapped futures level only from an explicitly supplied contemporaneous mapping; absent mapping is a hole. Options ingredients alone do not supply dealer-position signs or proprietary levels.

**Printed constants and limits:** 0DTE means same ET expiry date. No universal strike-to-futures ratio.

**Invalid / unavailable behavior:** QQQ/SPY mixed; strike units lost; next-day expiry pooled; final OI made intraday-known. Apply C04; emit `HOLE:O034:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O034-F1 — numeric fixture:** Synthetic QQQ call strike 500 expiring 2026-09-11 observed on ET 2026-09-11 is 0DTE; otherwise identical 2026-09-14 expiry is not. QQQ strike 500 cannot become NQ 25000 without a supplied mapping; mapped_price=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_options and family_gex; the previous formula labels R-R01/P3-05. Native ingredients exist; faithful dealer-position signs, complete source expiry selection and level mapping are missing. Existing behavior is not authority over this procedure.


<a id="o035"></a>

## O035 — Gamma-flip reference

**Wiki:** [Gamma-flip reference](/workspace/planning/phase-1-live/wiki/gex-flip.md). **Implementation mode:** supplied native reference; construction hole.

The flip is a source regime/location reference read with current price and the relevant gamma map. The materials use more than one sign/flip description, and a recap records disagreement near it without changing the plan. [GEX] pp.6–7, 13–19; [K18] p.4.

**Not a standalone trade.** A calculated zero of an assumed aggregate gamma curve does not automatically reproduce the proprietary flip or dictate an entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal flip label/value, product/expiry, source sign convention, native spot, snapshot and uncertainty. |
| Outputs / units | flip_value, spot_minus_flip, relation:below/on/above, source_regime_interpretation?. |
| ET clock / interval | Actual pre-decision source snapshot; later impulse reread has a new key. |
| Bars / event membership | Source panel and synchronized native spot; no inferred gamma curve. |
| Reset / persistence | Each source snapshot/version/product/expiry. |
| known_at | Maximum flip/spot availability used by the comparison. |

**Procedure:**

1. Ingest the supplied flip under its literal convention. Compute spot minus flip only in identical native units.
2. Preserve disagreement near the flip; do not replace a stated regime read with whichever aggregate sign gives the desired branch.
3. Automatic flip construction is null because the source algorithm/position model is not disclosed.

**Printed constants and limits:** No flip engine, uncertainty buffer or sign override threshold.

**Invalid / unavailable behavior:** Guessed zero-crossing; mixed units; future reread backdated. Apply C04; emit `HOLE:O035:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O035-F1 — numeric fixture:** Synthetic native spot 502 and supplied flip 500 gives difference +2 and above. A source interpretation marked uncertain remains uncertain; +2 does not manufacture a regime. No flip snapshot => relation null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_gex._gex_day/build_gex_table](/workspace/implementation/src/trading_research/research/phase1_live/family_gex.py); the previous formula labels R-R01. The exact source flip algorithm and consistent dealer-position assumptions are missing. Existing behavior is not authority over this procedure.


<a id="o036"></a>

## O036 — Gamma call and put walls

**Wiki:** [Gamma call and put walls](/workspace/planning/phase-1-live/wiki/gex-walls-and-max-pain.md). **Implementation mode:** supplied ranked native references; engine hole.

The gamma material marks call/put walls and also shows ranked wall references. Their native product, rank and position relative to spot must be preserved; the drawings do not reduce to one fixed wall on each side in every case. [GEX] pp.11–19.

**Not a standalone trade.** A wall touch is not a trade and a put-wall label is not universally identical to max pain.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source product/expiry, wall label/type/rank, native value or band, optional explicit mapping, snapshot. |
| Outputs / units | walls[] preserving label/rank/units, spot_relation, selected_wall_id, automatic_walls=null. |
| ET clock / interval | Pre-decision source panel ET; each refresh version retained. |
| Bars / event membership | Source panel/options reference, then native-compatible price evidence. |
| Reset / persistence | Per source product/expiry/panel version; do not discard extra ranked walls. |
| known_at | Verified source snapshot availability before selection/contact. |

**Procedure:**

1. Ingest all source-selected ranked wall records and validate unique source IDs. Do not collapse to one maximum-OI call and one put.
2. Compute literal price relation/contact only in matched units. Local defense/rejection/break belongs to its execution recipe.
3. Keep max pain as a different object even if its number matches a wall. Missing ranking/position engine leaves automatic walls null.

**Printed constants and limits:** Only supplied source ranks/values; no maximum-OI substitution.

**Invalid / unavailable behavior:** Dropped ranks; max-pain alias; absent mapping; later panel value substituted. Apply C04; emit `HOLE:O036:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O036-F1 — numeric fixture:** Synthetic source call-wall ranks 1=510 and 2=505 with spot 506: spot is below rank 1 and above rank 2. Both records survive. Put wall 490 and max pain 490 retain two IDs.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_options/family_gex; the previous formula labels R-R01/P3-05. Exact source wall ranking and positioning assumptions remain missing. Existing behavior is not authority over this procedure.


<a id="o037"></a>

## O037 — Source max-pain reference

**Wiki:** [Source max-pain reference](/workspace/planning/phase-1-live/wiki/max-pain.md). **Implementation mode:** supplied source reference only.

The source gamma panels include a max-pain reference alongside walls. A panel's put wall and max pain can coincide in an example; that does not establish universal identity. [GEX] pp.13–19.

**Not a standalone trade.** Max pain is a contextual reference, not a standalone pinning trade or an automatic terminal-price prediction.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal source label/value, native product/expiry, panel/version, snapshot and stated calculation convention if present. |
| Outputs / units | max_pain_value, source_known, relation_to_separate_walls, automatic_max_pain=null. |
| ET clock / interval | Source snapshot before use. |
| Bars / event membership | Source panel record; no expiry-outcome inference. |
| Reset / persistence | Per product/expiry/source snapshot. |
| known_at | Actual snapshot availability. |

**Procedure:**

1. Retain source max pain in native units and with a distinct ID. If only a payout/OI approximation exists, name it separately and leave faithful source value unknown.
2. Equality to a put wall in one record does not define universal identity. No automatic pinning entry or guaranteed expiry destination follows.

**Printed constants and limits:** No source-complete payout/position convention.

**Invalid / unavailable behavior:** Payout proxy labeled source exact; expiry close used to select level. Apply C04; emit `HOLE:O037:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O037-F1 — numeric fixture:** Synthetic supplied max pain 500 and put wall 495 give difference 5. Updating a separate put-wall record to 500 changes equality, not object identity or a predicted terminal price. Missing source max pain => null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_options and the previous formula labels R-R01/P3-05 have related options inputs. The exact source construction and entry-linked use are missing. Existing behavior is not authority over this procedure.


<a id="o038"></a>

## O038 — Source Vol Trigger readout

**Wiki:** [Source Vol Trigger readout](/workspace/planning/phase-1-live/wiki/volatility-trigger.md). **Implementation mode:** supplied readout only; engine hole.

The gamma materials show a Vol Trigger reference among the regime panels, but do not disclose a complete reconstructable algorithm for it. [GEX] pp.6–7, 13–19.

**Not a standalone trade.** A proprietary readout is not a standalone trade or permission to invent an equivalent level.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal label/value/unit, native product, panel/version, snapshot and stated interpretation. |
| Outputs / units | source_value, unit, interpretation?, automatic_value=null. |
| ET clock / interval | Source snapshot ET before use. |
| Bars / event membership | No bar-derived substitute. |
| Reset / persistence | Each source panel/version. |
| known_at | Verified snapshot availability. |

**Procedure:**

1. Ingest only the disclosed readout and unit. If either is absent, emit the missing field.
2. Do not compute a generic volatility threshold and rename it Vol Trigger. The readout is optional context unless the selected source case explicitly uses it.

**Printed constants and limits:** No published engine or threshold.

**Invalid / unavailable behavior:** Guessed unit/engine; future panel; mandatory universal filter invented. Apply C04; emit `HOLE:O038:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O038-F1 — numeric fixture:** Synthetic supplied Vol Trigger 500 in native ETF price units at 09:20 is usable as that reference at 09:30. A computed volatility value 20 cannot replace 500; without the panel source_value=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Related context: family_gex/family_vol and the previous formula labels R-R01/R-R02. The source Vol Trigger construction is missing. Existing behavior is not authority over this procedure.


<a id="o039"></a>

## O039 — Source VOL-GEX readout

**Wiki:** [Source VOL-GEX readout](/workspace/planning/phase-1-live/wiki/vol-gex.md). **Implementation mode:** supplied readout only; engine hole.

VOL-GEX appears as a source gamma-panel readout; its exact construction is not published in the material. [GEX] pp.13–19.

**Not a standalone trade.** Its presence in the panel does not define a new method or justify substituting a generic volume-weighted gamma formula.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal VOL-GEX label/value/unit, product/expiry, source panel/version, snapshot and interpretation. |
| Outputs / units | source_vol_gex, unit, interpretation?, automatic_value=null. |
| ET clock / interval | Source snapshot before use. |
| Bars / event membership | Source panel; no generic volume-weighted gamma construction. |
| Reset / persistence | Each source panel/product/expiry version. |
| known_at | Actual snapshot availability. |

**Procedure:**

1. Preserve the source number and native unit; unknown unit is a hole.
2. No automatic faithful computation is disclosed. Do not infer one from the readout's name or make it a universal passing gate.

**Printed constants and limits:** None published for construction.

**Invalid / unavailable behavior:** Assumed formula/unit; hindsight threshold. Apply C04; emit `HOLE:O039:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O039-F1 — numeric fixture:** Synthetic panel value 12 with source unit U is retained as 12 U. A separately computed 10 U remains a comparison, not source value. Missing source panel => faithful value null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gex and the previous formula labels R-R01 provide related inputs. A source-compatible VOL-GEX object is missing. Existing behavior is not authority over this procedure.


<a id="o040"></a>

## O040 — Source hedging-pressure gauge

**Wiki:** [Source hedging-pressure gauge](/workspace/planning/phase-1-live/wiki/hedging-pressure.md). **Implementation mode:** supplied gauge only; engine hole.

The source panel includes a hedging-pressure gauge as part of its regime/location read. Its exact gauge formula, unit and thresholds are not disclosed. [GEX] pp.13–19.

**Not a standalone trade.** The gauge is not an automatic buy/sell rule and is not identical to a simple net-gamma sign.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Gauge label/value/unit, native product, source panel/version, timestamp and stated interpretation. |
| Outputs / units | gauge_value, source_interpretation?, automatic_pressure=null. |
| ET clock / interval | Source snapshot before branch use. |
| Bars / event membership | Source panel record only. |
| Reset / persistence | Each panel/product version. |
| known_at | Actual snapshot availability. |

**Procedure:**

1. Retain exactly the supplied gauge and interpretation; missing formula, scale or thresholds remain holes.
2. Do not equate the gauge to net-gamma sign or derive a buy/sell permission absent a cited branch rule.

**Printed constants and limits:** No disclosed gauge equation, unit or threshold.

**Invalid / unavailable behavior:** Assumed percentage scale; net-gamma substitute; threshold fitted to outcome. Apply C04; emit `HOLE:O040:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O040-F1 — numeric fixture:** Synthetic explicitly supplied gauge 7 on stated scale 0–10 is recorded as 7, not 70% unless the source defines that conversion. A missing scale leaves interpretation null; no entry predicate follows from 7.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gex and the previous formula labels R-R01 are related. The faithful source gauge is missing. Existing behavior is not authority over this procedure.


<a id="o041"></a>

## O041 — Source KG1 level

**Wiki:** [Source KG1 level](/workspace/planning/phase-1-live/wiki/kg1-level.md). **Implementation mode:** supplied level/band only; engine hole.

KG1 supplies a source level in the NYAM retest example and an additional compatible input to the unnamed member's original reaction/HVN process. The source explicitly does not fully summarize its mechanism. [NYAM] pp.8–9; [K10] pp.6, 9.

**Not a standalone trade.** A generic gamma wall cannot impersonate KG1. Adding the level does not replace the member's own reaction area plus independent HVN.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | KG1 literal level/band, provider/version, instrument/date, availability and role in selected source case. |
| Outputs / units | kg1_band, source_known, role, automatic_kg1=null. |
| ET clock / interval | Source level before its retest/reaction. |
| Bars / event membership | Source level snapshot plus later actual retest evidence. |
| Reset / persistence | Each provider/date/version; preserve the member's independent reaction/HVN IDs. |
| known_at | Verified source availability before contact. |

**Procedure:**

1. Ingest KG1 under its own label. Validate instrument and level identity.
2. Require the specific NYAM retest or member source process separately. A generic gamma wall is not KG1 and KG1 does not replace the member's two independent reasons.

**Printed constants and limits:** No disclosed level engine or universal tolerance.

**Invalid / unavailable behavior:** Wall proxy; absent provider/time; member HVN replaced by KG1. Apply C04; emit `HOLE:O041:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O041-F1 — numeric fixture:** Synthetic source KG1 band [100, 101], independently supplied HVN [99.5, 100.5] and reaction band [100, 100.75] preserve three IDs. Removing the HVN does not pass the member's two-reason condition merely because KG1 exists.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gex/level ingredients are only surrounding context; the previous formula labels R-R01/R-S01/R-S06. The KG1 level engine is missing. Existing behavior is not authority over this procedure.


<a id="o042"></a>

## O042 — VIX and volatility context

**Wiki:** [VIX and volatility context](/workspace/planning/phase-1-live/wiki/vix-context.md). **Implementation mode:** available source observation and scoped interpretation.

The VIX lesson uses volatility levels, expected-range examples, completion, events and curve changes to adjust ambition and risk. Those examples frame the trade environment; they do not select a local entry. [VIX4] pp.3–9.

**Not a standalone trade.** A VIX threshold is not a universal direction or stop rule. A later daily VIX close is unavailable to a morning decision.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | VIX observation/value/unit, publication time, source instrument/range context, event context and selected risk interpretation. |
| Outputs / units | available_vix, observation_at, source_context?, ambition_adjustment?. |
| ET clock / interval | Last actually available pre-decision observation; date-only close is not assumed morning-known. |
| Bars / event membership | Published observation/vintage; no VIX price substituted for futures ticks. |
| Reset / persistence | Each context reread/event revision. |
| known_at | Publication/availability, not merely observation date. |

**Procedure:**

1. Select the most recent verified available source observation and retain its age.
2. Apply only the source-selected illustrated range/risk context. No universal direction, stop or risk lookup is supplied by this object.

**Printed constants and limits:** No universal VIX regime table; printed daily-move formula is the separate recipe.

**Invalid / unavailable behavior:** Same-day close used in morning; instrument range examples merged; invented thresholds. Apply C04; emit `HOLE:O042:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O042-F1 — numeric fixture:** Synthetic prior available VIX 20 and later same-day close 25: a 09:30 decision can use 20 only if its publication is verified; 25 is unavailable. Missing publication time prevents a faithful preopen selection.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas.vix_preopen/vix_band](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); family_vol; the previous formula labels R-R02. Source-compatible time/vintage and exact regime mapping are partial. Existing behavior is not authority over this procedure.


<a id="o043"></a>

## O043 — Volatility-implied daily-move estimate

**Wiki:** [Volatility-implied daily-move estimate](/workspace/planning/phase-1-live/wiki/expected-daily-move.md). **Implementation mode:** source-printed algebra.

The lesson figure displays expected daily move (%) = VIX / √252 and also discusses instrument-specific point-range examples. This is a volatility/range framing estimate used before deciding target ambition. [VIX4] pp.3–5.

**Not a standalone trade.** The estimate is not a guaranteed daily range, a confidence-certified target, or a standalone fade at completion.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Available VIX value in percentage points; optional explicitly selected contemporaneous conversion price P and instrument identity. |
| Outputs / units | daily_move_percent=VIX/sqrt(252), daily_fraction=VIX/(100*sqrt(252)), point_estimate=P*daily_fraction if mapped. |
| ET clock / interval | Pre-decision VIX/price observation ET. |
| Bars / event membership | No future realized range; source publication records and native reference price. |
| Reset / persistence | Each updated VIX/reference-price snapshot. |
| known_at | Maximum VIX and conversion-price availability. |

**Procedure:**

1. Divide the percentage-point index by sqrt(252) to obtain percent, not a decimal return.
2. Only if a price/instrument conversion is explicitly selected, divide by 100 and multiply by that price. Label the result an estimate; it is not a guaranteed range or universal NQ/ES table.
3. Record elapsed realized movement separately after its observation; it cannot set the original expected move.

**Printed constants and limits:** 252 is printed in the source figure; no confidence probability is inferred.

**Invalid / unavailable behavior:** Percent/fraction factor 100 error; later price/VIX; automatic cross-instrument mapping. Apply C04; emit `HOLE:O043:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O043-F1 — numeric fixture:** Synthetic VIX 20 gives 20/sqrt(252)=1.2598815767%. With an explicitly selected P=5000, point estimate=62.994078835. It is not 6299.4078835 points and does not assert that price must travel 62.994 points.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_vol; [formulas.vix_band](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); the previous formula labels R-R02. Exact source example-to-instrument mapping and event-time update are partial. Existing behavior is not authority over this procedure.


<a id="o044"></a>

## O044 — Volatility term structure and event change

**Wiki:** [Volatility term structure and event change](/workspace/planning/phase-1-live/wiki/volatility-curve.md). **Implementation mode:** aligned source observations and literal changes; interpretation hole.

The volatility lesson reads curve shape, expansion/crush and event changes as context for risk and expected movement. These are inputs to the live thesis and trade ambition. [VIX4] pp.5–9.

**Not a standalone trade.** Curve shape alone is not an entry, and the source does not supply a universal ratio threshold that overrides the auction.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Named products/tenors, native values/units, synchronized availability, source curve/event interpretation. |
| Outputs / units | tenor_values[], difference_or_ratio_when_selected, event_change, source_curve_label?. |
| ET clock / interval | Common as-of before decision; event comparison must use verified pre/post observations. |
| Bars / event membership | Native published observations/vintages; no date-only timing invention. |
| Reset / persistence | Each curve snapshot and event comparison pair. |
| known_at | Latest required component availability; post-event change only after the post observation. |

**Procedure:**

1. Align the exact source-selected tenors in compatible units. Compute a named difference b-a or ratio b/a only when the record explicitly requests it; no selected ratio is a new entry rule.
2. Record curve shape/expansion/crush only as the supplied source interpretation or complete stated relation. Preserve timing and missing values.

**Printed constants and limits:** No universal tenor ratio or curve threshold.

**Invalid / unavailable behavior:** Mismatched timestamps; future crush used early; arbitrary ratio promoted to source rule. Apply C04; emit `HOLE:O044:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O044-F1 — numeric fixture:** Synthetic selected near/far values 20 and 22 give difference +2 and, if explicitly requested, far/near=1.1. A post-release near value 16 yields change -4 only after its release. It is unavailable before the event.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_vol; the previous formula labels R-R02. Source-selected tenor/ratio and event-change interpretation are partial. Existing behavior is not authority over this procedure.


<a id="o045"></a>

## O045 — VVIX context

**Wiki:** [VVIX context](/workspace/planning/phase-1-live/wiki/vvix-context.md). **Implementation mode:** available observation with supplied context.

VVIX appears in the volatility lesson's broader read of changing volatility conditions. It modifies the context in which risk and expected movement are assessed. [VIX4] pp.6–9.

**Not a standalone trade.** The supplied material does not turn one VVIX value into a disclosed standalone entry algorithm.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | VVIX native observation/unit, publication time, source interpretation and relation to selected volatility read. |
| Outputs / units | available_vvix, source_interpretation?, automatic_entry_rule=null. |
| ET clock / interval | Verified publication before decision. |
| Bars / event membership | Native observation record. |
| Reset / persistence | Each source volatility reread/version. |
| known_at | Actual publication availability; date alone is insufficient. |

**Procedure:**

1. Retain the latest actually available observation under its own identity and units.
2. Do not create a universal VVIX threshold, entry, direction or stop from the contextual mention.

**Printed constants and limits:** No disclosed decision threshold.

**Invalid / unavailable behavior:** Later close; VIX/VVIX units merged; invented mapping. Apply C04; emit `HOLE:O045:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O045-F1 — numeric fixture:** Synthetic VVIX 100 available 09:00 may be recorded at 09:30; value 110 first available 10:00 may not. The number 100 alone leaves entry_permission=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_vol and the previous formula labels R-R02 are related. A source-complete VVIX decision mapping is missing. Existing behavior is not authority over this procedure.


<a id="o046"></a>

## O046 — Green Bird's finished session references

**Wiki:** [Green Bird's finished session references](/workspace/planning/phase-1-live/wiki/session-fail-boxes.md). **Implementation mode:** completed source range geometry; unresolved session clocks are holes.

NYAM is the completed 09:00–10:00 box; the previous-hour trade uses the completed hour. Asia is drawn approximately 20:00–00:00, while exact London bounds are not published. Those session highs/lows also frame the separately stated VWAP continuation. [GB] pp.23, 27, 30–35, 38–40.

**Not a standalone trade.** A box is a reference, not the failed-breakout system. A sweep while the box is still forming does not qualify as a sweep of its finished boundary.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source session ID, verified formation [start, end), complete native H/L and instrument; selected traded/opposing boundary. |
| Outputs / units | box_high, box_low, box_width, formation_end, known_at, boundary_ids. |
| ET clock / interval | NYAM [09:00, 10:00) ET; previous-hour box is the preceding completed clock hour. Asia approximately 20:00–00:00 is source context with unresolved exactness; exact London bounds are unpublished. |
| Bars / event membership | Complete one-minute or finer observations within the verified clock; not N observed rows. |
| Reset / persistence | Every actual source session/hour; no hard-coded count of seven available hours. |
| known_at | Formation end after coverage validation; never an earlier forming-range sweep. |

**Procedure:**

1. Use max H and min L within the selected complete interval and freeze both. Hour h's boundary can be used only after that hour closes.
2. Require source-exact Asia/London clock input before claiming faithful automatic boxes for those variants; an approximate chart interval is not a recovered setting.
3. Keep every valid hour and its actual later action window as a separate episode. Missing data creates coverage holes; boxes do not supply the scalp trigger.

**Printed constants and limits:** 09:00–10:00 and completed clock hours; approximate Asia clock remains approximate.

**Invalid / unavailable behavior:** Sweep before formation ends; inferred London clock labeled exact; missing minutes compressed into complete hour. Apply C04; emit `HOLE:O046:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O046-F1 — numeric fixture:** Synthetic NYAM H=110/L=100 forms at 10:00. Price 111 at 09:45 cannot sweep its finished boundary; a 10:05 price 111 can. Its opposing low remains 100. A missing 09:32 row prevents automatic complete-box status.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_fail.build_fail_table](/workspace/implementation/src/trading_research/research/phase1_live/family_fail.py); [formulas.clock_hour_boxes](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); family_levels; the previous formula labels R-G01/G02/G03/G09. Inferred London bounds cannot be labeled author-exact. Existing behavior is not authority over this procedure.


<a id="o047"></a>

## O047 — Sweep, failure and reclaim

**Wiki:** [Sweep, failure and reclaim](/workspace/planning/phase-1-live/wiki/sweep-reclaim.md). **Implementation mode:** ordered literal failure; source confirmation mode required.

Green Bird shorts after a high is swept and price fails back below, or buys after a low is swept and reclaimed. Selected PDL and Asia/TDO cases explicitly wait for a completed five-minute close. Jumbo's range reversal also needs a sweep/reaction but keeps its own selected block/flow confirmation. [GB] pp.21, 23, 25, 27, 30–35; [TBR] pp.8–11, 27–29.

**Not a standalone trade.** A sweep alone is not confirmation. The five-minute rule from one author/case must not silently become a universal rule for every range reversal.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen reference L/H or line R, side, ordered prices, source confirmation type/timeframe, complete bar C when applicable, decision time. |
| Outputs / units | sweep_at, sweep_extreme, confirm_at, failure_confirmed?, reference_known_before_sweep. |
| ET clock / interval | Reference formation then source action window ET; five-minute close only for the explicitly selected GB cases. |
| Bars / event membership | Clock-aligned complete five-minute candles when prescribed. Other reclaim/hold modes need supplied source evidence or a disclosed detector. |
| Reset / persistence | Per reference/side/attempt; extrema accumulate only for that attempt through its confirmation. |
| known_at | Reference before sweep; sweep before confirmation; confirmation available at close before decision. |

**Procedure:**

1. For a high failure, require observed price>R followed by the prescribed close/return below R. For a low reclaim require price<R followed by close/return above R. Equality is contact, not a sweep or strict reclaim.
2. For a box return-inside requirement compare confirmation with both frozen edges, preserving that case's rule. A line reclaim alone need not use an unrelated box.
3. Require reference_known_at≤sweep_at<confirm_at≤decision_at. A bar containing sweep and close can establish price excursion then completed close only when its inputs establish the relevant order; do not stamp confirmation at bar start.
4. GB five-minute cases use completed clock bars; Jumbo retains its selected block/flow confirmation. An unspecified hold duration is a hole, not a 30-minute default.

**Printed constants and limits:** 5 minutes only where stated; strict sweep/return side from source descriptions.

**Invalid / unavailable behavior:** Touch counted as sweep; close before sweep; incomplete bar; universal 5-minute rule imposed across authors. Apply C04; emit `HOLE:O047:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O047-F1 — numeric fixture:** Synthetic high R110, trade 111 at 10:01 then complete [10:00, 10:05) close 109 at 10:05, decision 10:06 gives high-failure sequence true when finer evidence supplies the sweep time. Close 111 gives false; close 110 does not satisfy strict below. A 10:04 decision using that close fails causality.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_fail._failback](/workspace/implementation/src/trading_research/research/phase1_live/family_fail.py); [formulas.reclaim_5m](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); [grid.failback_wick_c5](/workspace/implementation/src/trading_research/research/phase1_live/grid.py); the previous formula labels R-G01–G05/G08 and R-J01. Grouping five observed rows and stamping their start is not a clock-aligned five-minute close. Existing behavior is not authority over this procedure.


<a id="o048"></a>

## O048 — Prior day, week and month extremes

**Wiki:** [Prior day, week and month extremes](/workspace/planning/phase-1-live/wiki/prior-day-week-month-levels.md). **Implementation mode:** extrema for verified prior-period convention; unspecified scope hole.

Green Bird uses prior-day levels, the previous weekly candle's extremes and previous-month extremes as sweep/reclaim references or objectives. Jumbo's liquidity maps retain named prior-day highs/lows with a configurable lookback. [GB] pp.25, 31–35; [JR] pp.16–18, 33–39.

**Not a standalone trade.** A prior extreme supplies location or bias; it is not automatically the 9–10 range trade, and prior RTH is not a substitute for every PDH/PDL label.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Period kind/calendar, full-session or RTH scope, complete prior period prices, source lookback and active-state rule. |
| Outputs / units | prior_high, prior_low, period_id, period_end, known_at, active_state?. |
| ET clock / interval | Source-defined prior day/week/month boundaries in ET; do not silently substitute RTH for an unqualified PD label. |
| Bars / event membership | Complete source-period bars/events in one instrument or explicitly declared contract mapping. |
| Reset / persistence | New completed prior period; older named references persist only under their source lookback/retirement policy. |
| known_at | Prior period close plus required coverage; not current-period final extrema. |

**Procedure:**

1. Resolve the exact immediately prior source period. Compute max H/min L and preserve scope in its ID.
2. Retain weekly/monthly references independently from daily boxes. Link a sweep/reclaim bias only if established before the later pullback.
3. If full-session boundary, week calendar, lookback or retirement rule needed by the branch is not stated, emit that hole. Do not choose a convenient calendar.

**Printed constants and limits:** Only explicitly supplied source period/lookback settings.

**Invalid / unavailable behavior:** Current final extrema; RTH/full-session alias; expired level kept without policy; later bias backdated. Apply C04; emit `HOLE:O048:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O048-F1 — numeric fixture:** Synthetic verified previous week H120/L90 and prior day H110/L100 give four separate references. A115 trade sweeps daily high but not weekly high. Missing weekly endpoint convention makes the automatic weekly reference unknown.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_levels.build_level_table](/workspace/implementation/src/trading_research/research/phase1_live/family_levels.py); the previous formula labels R-G05/G08/G09, R-J10/J19. Persistent prior-week/month references and source-scoped retirement are missing or partial. Existing behavior is not authority over this procedure.


<a id="o049"></a>

## O049 — Green Bird's midnight true-day open

**Wiki:** [Green Bird's midnight true-day open](/workspace/planning/phase-1-live/wiki/true-day-open.md). **Implementation mode:** literal midnight opening reference.

TDO is the midnight opening price used as confluence, reclaim confirmation or destination. It is not an instruction to sell simply because price is above it. Some Asia examples combine their failure with a close through TDO; that requirement belongs to that selected case. [GB] pp.21, 27, 30–33, 38.

**Not a standalone trade.** A TDO touch is not a complete trade, and TDO is not a universal extra AND condition for every Green Bird failure.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Instrument, ET session date, verified midnight opening trade or supplied source opening value, source role and optional required close-through mode. |
| Outputs / units | tdo_price, tdo_known_at, role, close_through_tdo?. |
| ET clock / interval | 00:00 ET date-aware DST; not 18:00 or 09:30. |
| Bars / event membership | First actual opening event under the supplied source convention; one-minute stored O is available at 00:01 unless matching trade proves earlier availability. |
| Reset / persistence | Each ET midnight source day. |
| known_at | Opening event availability or completed input bar close. |

**Procedure:**

1. Create a distinct TDO ID and preserve whether the source opening convention is exact first trade at/after midnight; missing exact data is a hole.
2. Use TDO as confluence, confirmation or target only as selected in the source case. Where a completed five-minute close through TDO is required, wait for it.
3. Do not add TDO as a compulsory AND to all GB failures or infer sell from price above it.

**Printed constants and limits:** 00:00 ET; source-specific optional five-minute confirmation.

**Invalid / unavailable behavior:** 18:00 open substitution; stored O exposed early; optional gate made universal. Apply C04; emit `HOLE:O049:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O049-F1 — numeric fixture:** Synthetic midnight TDO 100, cash open 105, evening open 98 remain distinct. A selected Asia-high-failure short with required five-minute close 99 satisfies close below TDO; close 101 fails that selected gate. Another source case with no TDO requirement remains not_required.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_levels TDO fields; [formulas.reclaim_5m](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); the previous formula labels R-G02/G06/G09. Event linkage and source-specific optionality remain partial. Existing behavior is not authority over this procedure.


<a id="o050"></a>

## O050 — 09:30 cash-open price

**Wiki:** [09:30 cash-open price](/workspace/planning/phase-1-live/wiki/cash-open-reference.md). **Implementation mode:** literal opening event and ordered source opening case.

The cash-open price anchors the opening read. Green Bird's September 1 example describes a move below the open, reclaim and long; it is a 09:30 manipulation branch, not an already finished 9–10 box. Sires's open-drive read asks whether price crosses back through this open. [GB] p.40; [TBR] pp.8–10; [AMT1] p.11; [AVG] pp.21–22.

**Not a standalone trade.** A move through the open does not automatically qualify a trade. A partial early-session example cannot borrow a later box's final high/low.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Instrument, first source cash-open event, opening value, excursions/returns, source branch/confirmation. |
| Outputs / units | cash_open, known_at, cross_below_at, cross_above_at, source_open_reclaim?. |
| ET clock / interval | 09:30 ET cash open; no dependency on final 09:00–10:00 box. |
| Bars / event membership | Opening trade for immediate price; completed stored one-minute open available 09:31. Exact GB opening confirmation duration is not supplied. |
| Reset / persistence | Per cash session. |
| known_at | Opening event, then actual excursion/return evidence; confirmation at its own source key. |

**Procedure:**

1. Freeze opening price from the correct event. Compare later prices to it with strict sides.
2. For the GB September 1 long description record move below open then reclaim then long. Preserve this disclosed direction; do not fabricate a short mirror or force an unstated five-minute rule.
3. For Sires open-drive context separately track whether price crossed back through open by the current as-of. Never read final-day behavior into an early drive label.

**Printed constants and limits:** 09:30 ET only; no universal reclaim duration.

**Invalid / unavailable behavior:** Final 9–10 range used at 09:35; future cross absence; unsupported short mirror. Apply C04; emit `HOLE:O050:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O050-F1 — numeric fixture:** Synthetic cash open 100 at 09:30, price 99 at 09:32, return 101 at 09:34: below-then-above order is observed. Full source confirmation remains null without its disclosed/supplied rule. A 09:33 long cannot use 09:34 reclaim.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_open; family_levels; the previous formula labels R-G04, R-J02, R-A10 and R-S09. Green Bird's exact opening confirmation detector remains incomplete. Existing behavior is not authority over this procedure.


<a id="o051"></a>

## O051 — New-week opening gap

**Wiki:** [New-week opening gap](/workspace/planning/phase-1-live/wiki/new-week-opening-gap.md). **Implementation mode:** literal supplied endpoints; endpoint convention hole.

NWOG is the area between the source's Friday-close and Sunday-open references. Green Bird uses it as a destination after an appropriate failure/reclaim, including the August 17 example. [GB] pp.35–39.

**Not a standalone trade.** The gap is an objective or confluence, not an entry at its edge. A chart's eventual gap fill is not evidence that it was the preplanned target.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source Friday close F with exact close convention, Sunday opening S with exact convention, source week/instrument, preselected objective. |
| Outputs / units | gap_lo=min(F, S), gap_hi=max(F, S), gap_width=abs(S-F), known_at, partial_contact, full_fill. |
| ET clock / interval | Actual source Friday close and Sunday open ET; do not replace close with settlement/RTH without evidence. |
| Bars / event membership | Verified endpoint events/complete bars and later price path. |
| Reset / persistence | Each new-week gap; retain its ID until source consumption/end rule. |
| known_at | Maximum endpoint availability, normally Sunday opening observation. |

**Procedure:**

1. Construct gap only from verified source endpoints. Equal endpoints yield zero-width/no gap, not a tradable interval.
2. Freeze chosen near/far destination before entry. For an opening gap up S>F, return to upper edge is contact and reach F is full downward fill; reverse for gap down.
3. Measure after the linked entry under C06. An eventual weekly fill cannot select the earlier objective.

**Printed constants and limits:** No universal Friday close or fill horizon.

**Invalid / unavailable behavior:** Wrong close/settlement; future target selection; partial touch counted full fill. Apply C04; emit `HOLE:O051:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O051-F1 — numeric fixture:** Synthetic F100/S104 gives gap [100, 104], width 4. Later trade 102 enters the gap but does not fill it; 100 completes the downward fill. Without the Friday-close convention, faithful automatic gap is null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_levels NWOG fields; the previous formula labels R-G07/G09. The exact endpoint convention and entry-linked outcome need source verification. Existing behavior is not authority over this procedure.


<a id="o052"></a>

## O052 — Measured 50–61.8% retracement

**Wiki:** [Measured 50–61.8% retracement](/workspace/planning/phase-1-live/wiki/golden-pocket.md). **Implementation mode:** source-measured impulse retracement algebra.

Green Bird's golden pocket is the 50–61.8% retracement of the explicitly measured impulse. The September 1 illustration combines it with a PDL sweep and five-minute failure; the July example combines fib pullback and hourly-low reclaim. [GB] pp.25, 31–35.

**Not a standalone trade.** The band is entry location/confluence inside the failure method. A fib touch alone is not another system.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Completed measured impulse ID, direction, high H/low L, endpoint confirmations and source selection, later touch. |
| Outputs / units | width W, band_lo, band_hi, known_at, linked_failure_id. |
| ET clock / interval | Impulse confirmed/selected before pullback in ET; no assumed 9–10 net-candle selector. |
| Bars / event membership | Actual source impulse bars/endpoint records; automatic swing selection remains a hole if undisclosed. |
| Reset / persistence | Each separately identified measured impulse. |
| known_at | Maximum endpoint confirmation/selection key before band use. |

**Procedure:**

1. Set W=H-L>0. For down impulse, upward retracement band=[L+0.50W, L+0.618W]. For explicitly supplied up-impulse mirror, downward retracement band=[H-0.618W, H-0.50W]; do not invent an otherwise absent branch.
2. Retain exact decimal endpoints and associate the band with its actual sweep/reclaim event.
3. Keep impulse choice fixed before touch. A band touch supplies location only.

**Printed constants and limits:** 0.50 and 0.618 printed retracement fractions.

**Invalid / unavailable behavior:** Zero width; future endpoint; down impulse algebra reversed; unrelated 9–10 candle substituted. Apply C04; emit `HOLE:O052:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O052-F1 — numeric fixture:** Synthetic down impulse H120/L100 gives band [110, 112.36]. A declared up impulse with the same extrema gives [107.64, 110]. A touch 111 fits the down retracement only; no failure confirmation follows from it.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas.gp_band_impulse](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); the previous formula labels R-G05. The algebra exists, but the caller's 9–10 net-candle impulse is not necessarily the source's larger measured impulse. Existing behavior is not authority over this procedure.


<a id="o053"></a>

## O053 — Premium / discount within a selected range

**Wiki:** [Premium / discount within a selected range](/workspace/planning/phase-1-live/wiki/premium-discount-50.md). **Implementation mode:** literal range-position algebra; source value meaning preserved.

Premium and discount describe position within a declared price range or value context. Green Bird's smaller directional longs buy pullbacks into discount; Sires's sources also discuss auction/value location. These references require the particular source's range identity. [GB] pp.35, 40; [TPO] pp.4, 9; [VWAP] pp.3–6.

**Not a standalone trade.** Being below a midpoint is not a buy rule, and VWAP-relative discount is not necessarily the same object as a 50% high-low split.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Selected parent range H/L or explicit VWAP/value reference, known_at, current price, author/branch. |
| Outputs / units | range_mid, normalized_position=(P-L)/(H-L), location:discount/equilibrium/premium; or separately labeled value-relative relation. |
| ET clock / interval | Parent known before current comparison ET. |
| Bars / event membership | Completed parent or source developing snapshot as-of; no final-day range. |
| Reset / persistence | Parent ID/version; a value reference is not a high-low range. |
| known_at | Maximum parent and current price availability. |

**Procedure:**

1. For a literal range W>0 compute midpoint=(H+L)/2. Below midpoint is discount, equal is equilibrium, above is premium; preserve positions beyond the full range too.
2. For source VWAP-relative discount compare with that VWAP under its own recipe; do not rename the comparison as a 50% split.
3. No entry or scalp trigger follows from location alone.

**Printed constants and limits:** 0.5 for the literal price-range split only.

**Invalid / unavailable behavior:** Parent unavailable; wrong meaning; range chosen from final path. Apply C04; emit `HOLE:O053:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O053-F1 — numeric fixture:** Synthetic range [100, 120], P108 gives midpoint 110, position 0.4, discount. Supplied VWAP 107 puts the same P above VWAP. The two relations can differ without either being rewritten.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** formulas and sessions supply midpoint geometry; the previous formula labels R-G10, R-A01/A16 and R-F01/F03. The directional-scalp impulse and complete trigger are unpublished. Existing behavior is not authority over this procedure.


<a id="o054"></a>

## O054 — Market-structure shift after failure

**Wiki:** [Market-structure shift after failure](/workspace/planning/phase-1-live/wiki/market-structure-shift.md). **Implementation mode:** supplied source-confirmed structure sequence; automatic detector hole.

A raw Green Bird chart labels the 9–10 high sweep/failed breakout, then MSS plus FVG for entry/risk, then opposing 9–10 lows. MSS is the selected execution refinement after the failure. [GB] p.43.

**Not a standalone trade.** MSS is not disclosed as a separate complete system here, and the chart does not make it compulsory in every Green Bird case.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Confirmed swing/boundary IDs, price and confirmation keys, prior failure ID, actual break/close event, linked gap and decision. |
| Outputs / units | structure_reference, structure_confirmation_at, mss_after_failure?, automatic_mss=null. |
| ET clock / interval | Failure before source structure confirmation before entry ET. |
| Bars / event membership | Source chart timeframe and break convention; no universal fractal length. |
| Reset / persistence | Per failed-breakout execution refinement. |
| known_at | At actual boundary confirmation/break completion, not pivot price time. |

**Procedure:**

1. Require the source boundary, swing confirmation and break convention. If absent, emit holes instead of choosing a common MSS recipe.
2. Validate failure_at<structure_confirm_at≤entry and the same side/episode. Link the FVG under its own source definition.
3. MSS is optional only where not selected by the source case; it is not a universal GB gate.

**Printed constants and limits:** No published swing length or break-close threshold.

**Invalid / unavailable behavior:** Backdated fractal; different episode; later gap used early. Apply C04; emit `HOLE:O054:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O054-F1 — numeric fixture:** Synthetic failure 10:05, source swing boundary 108 confirmed 10:06, break 107 at 10:07 and entry 10:08 preserve order for a supplied bearish refinement. A 10:04 entry fails causality; absent swing detector leaves automatic MSS null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-G01/R-G09 provide surrounding failure ingredients. An event-linked source MSS detector and its exact swing-confirmation parameters are missing. Existing behavior is not authority over this procedure.


<a id="o055"></a>

## O055 — Fair-value gaps and higher-timeframe imbalances

**Wiki:** [Fair-value gaps and higher-timeframe imbalances](/workspace/planning/phase-1-live/wiki/fvg-body-gaps.md). **Implementation mode:** supplied source gap; unresolved construction/fill holes.

Jumbo's PD RTH Range+ uses M15/H1 imbalance destinations; Green Bird's chart uses an FVG after a confirmed failure/MSS for execution. The gap's timeframe and role belong to the source case. [TBR] pp.32–35; [GB] p.43.

**Not a standalone trade.** A gap is an area or refinement, not an independent trade. A body-only gap or first-presented variant must not be borrowed from another source without evidence.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Instrument/timeframe, defining complete candle IDs, explicit wick/body construction, bounds, confirmation, active/fill policy and entry/target role. |
| Outputs / units | gap_lo, gap_hi, gap_known_at, construction, active_at_use?, contact_or_fill?. |
| ET clock / interval | M15/H1 for Jumbo's selected destinations; GB execution gap retains its chart's actual timeframe. |
| Bars / event membership | Complete source-defined candles. Do not choose body-only or wick-only from an old helper. |
| Reset / persistence | Each gap identity; append later fill-state events under source scope. |
| known_at | Last defining confirmation close; not the first candle's time. |

**Procedure:**

1. If source supplies gap bounds and their confirmation, ingest them directly. If the source fully specifies a construction, execute it exactly; otherwise automatic bound generation=null with construction hole.
2. Keep wick and body candidates separately named where unresolved. Do not silently adopt a generic three-candle gap formula as author-exact.
3. For contact measure interval intersection against frozen bounds; full fill needs traversal to the far bound under the source direction and active policy. Missing retirement/fill scope remains unknown.

**Printed constants and limits:** Only selected M15/H1 or source execution timeframe; no universal fill percentage/horizon.

**Invalid / unavailable behavior:** Unresolved construction labeled exact; incomplete defining candle; ETH retirement imposed on RTH-only target. Apply C04; emit `HOLE:O055:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O055-F1 — numeric fixture:** Synthetic supplied bullish gap [100, 102] confirmed 10:15: it is unavailable 10:14. A later descent to 101 is partial contact, to 100 reaches the far edge. Without a source active-state policy, a later entry's active_gap remains null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap; [formulas_jumbo.j19_htf_fvg](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-J19 and related R-G01/R-G09 ingredients. Source-specific entry and fill-state joins are partial. Existing behavior is not authority over this procedure.


<a id="o056"></a>

## O056 — Jumbo orderblocks

**Wiki:** [Jumbo orderblocks](/workspace/planning/phase-1-live/wiki/sweep-cisd-blocks.md). **Implementation mode:** source three-candle OB geometry and confirmed entry choice.

The manual's personal reversal entry choice uses a short-timeframe three-candle structure and the second candle's full range as the orderblock. Immediate versus retracement execution and risk choices are distinguished. [TBR] pp.27–29.

**Not a standalone trade.** The author expressly treats these as preferred entries, not a fixed universal component of every TBR trade. The orderblock is not the rejection wick.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source 2/3/5-minute complete candles C1/C2/C3, sweep side, chosen immediate/midpoint/retrace entry and source stop policy. |
| Outputs / units | ob_band=[L2, H2], ob_mid=(L2+H2)/2, confirmation_at, selected_entry_mode, selected_stop?. |
| ET clock / interval | All three candles close before their dependent decision ET. |
| Bars / event membership | Actual source 2/3/5-minute candles, aligned clock intervals; C2 full range is mandatory for this object. |
| Reset / persistence | Each three-candle structure/attempt. |
| known_at | C3 confirmation close for confirmed OB; C2 alone cannot confirm it. |

**Procedure:**

1. Bullish source pattern: C2 sweeps C1 low (L2<L1), then C3 closes above C2 high (C3>H2). Bearish mirror requires the corresponding source-selected high sweep H2>H1 and C3<L2. Preserve actual candle identities.
2. Set OB to the full second-candle range, including body and both wicks. Compute its exact midpoint separately.
3. Immediate confirmed entry versus later retracement/midpoint entry are distinct selected policies. In the bullish p 27/28 example midpoint stop is aggressive and low stop conservative; p 29 caption/drawing ambiguity does not establish a universal stop. Missing chosen policy is a hole.

**Printed constants and limits:** Source 2/3/5-minute examples; midpoint 0.5. No universal mandatory OB for every TBR branch.

**Invalid / unavailable behavior:** Wick substituted for OB; C3 incomplete; fabricated universal stop; wrong-side sweep. Apply C04; emit `HOLE:O056:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O056-F1 — numeric fixture:** Synthetic bullish C1L101; C2O102/H104/L100/C103; C3 close 105. Sweep 100<101 and close 105>104 give confirmed OB [100, 104], mid 102. Rejection wick [100, 102] is a different object. C3 close 103 fails this confirmation; decision before C3 close fails causality.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.j18_ob_bull/j18_ob_bear](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); family_gap; the previous formula labels R-J18. Full source entry, timing and management linkage is partial. Existing behavior is not authority over this procedure.


<a id="o057"></a>

## O057 — Jumbo rejection blocks

**Wiki:** [Jumbo rejection blocks](/workspace/planning/phase-1-live/wiki/rejection-block.md). **Implementation mode:** literal source rejection wick and selected execution policy.

The rejection block is the rejection wick used as a chosen reversal-entry area, distinct from the full-candle orderblock. It sits inside the context/location/confirmation loop. [TBR] pp.27–29.

**Not a standalone trade.** A wick alone is not a complete TBR entry, and a rejection-block boundary is not automatically an orderblock boundary.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Completed source candle O/H/L/C, rejection side, timeframe, allowed location, source confirmation and chosen entry/stop geometry. |
| Outputs / units | body_lo=min(O, C), body_hi=max(O, C), rejection_band, wick_width, known_at, stop_policy?. |
| ET clock / interval | Source candle completion after allowed-location reaction and before entry. |
| Bars / event membership | Actual source candle timeframe; not a merged three-candle OB. |
| Reset / persistence | Each selected rejection candle/attempt. |
| known_at | Candle close plus source confirmation/selection availability. |

**Procedure:**

1. For lower rejection wick use[L, min(O, C)]; for upper rejection use[max(O, C), H]. Zero wick width is no wick area.
2. Require the source rejection interpretation and allowed framework location; wick geometry alone is insufficient.
3. Preserve selected entry and stop from the specific figure. Ambiguous midpoint/conservative captions remain a policy hole; do not choose the better historical stop.

**Printed constants and limits:** No universal wick-length ratio or stop beyond wick.

**Invalid / unavailable behavior:** Full C2 range substituted; unconfirmed candle; hindsight block/stop selection. Apply C04; emit `HOLE:O057:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O057-F1 — numeric fixture:** Synthetic O102/C103/H104/L100 gives lower rejection band [100, 102], width 2, upper [103, 104], width 1. Full candle OB [100, 104] is neither wick. A zero lower wick L102 would eliminate that lower-wick area.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap and [formulas_jumbo.j18_ob_bull/j18_ob_bear](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) are related; the previous formula labels R-J18. Distinct source rejection-wick execution is partial. Existing behavior is not authority over this procedure.


<a id="o058"></a>

## O058 — Jumbo Absorption Zone+ candle

**Wiki:** [Jumbo Absorption Zone+ candle](/workspace/planning/phase-1-live/wiki/absorption-candle-jumbo.md). **Implementation mode:** printed feature arithmetic; undisclosed comparison/reset conventions remain holes.

The source settings display body threshold 0.6, volume multiplier 1.5 and a 14-period volume average. The small-body/high-volume candle is one confirmation aid at a framework location. [TBR] pp.31, 35; [JR] pp.14, 67–69.

**Not a standalone trade.** This is a candle feature, not proof of passive replenishment or an independent reversal system. The same word absorption does not make it the DOM four-check sequence.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Complete source bar O/H/L/C/V, source timeframe, 14-period volume reference and exact inclusion/reset/warm-up convention, threshold equality convention. |
| Outputs / units | body_ratio=abs(C-O)/(H-L), volume_average, volume_ratio=V/average, small_body?, high_volume?, source_zone_flag?. |
| ET clock / interval | Completed source candle; volume baseline causal and source-reset compatible. |
| Bars / event membership | Actual selected timeframe; trailing 14-period SMA only with disclosed inclusion/warm-up convention. |
| Reset / persistence | Source indicator history/reset; do not force 09:30 or center the average. |
| known_at | Current candle close and all baseline dependencies; future volume forbidden. |

**Procedure:**

1. For H>L compute absolute body divided by range. Zero range returns null ratio and invalid degenerate-candle reason.
2. For a verified 14-member simple average compute Σvolume/14. The displayed settings are body threshold 0.6, volume multiplier 1.5 and volume average 14; previous 0.3/2.5 settings must be discarded.
3. Compare body and volume with the printed thresholds under the source's exact inequality. Strictly below/above can be recorded directly; equality, inclusion of current bar, insufficient history and source reset stay holes if not disclosed. A supplied source flag can be retained with provenance.
4. This is a candle feature at a planned location; it is not DOM replenishment or the four-check sequence.

**Printed constants and limits:** 0.6 body threshold; 1.5 volume multiplier; 14-period SMA setting from source figure.

**Invalid / unavailable behavior:** Centered average; invented reset; guessed equality; 0.3/2.5 old settings; zero denominator. Apply C04; emit `HOLE:O058:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O058-F1 — numeric fixture:** Synthetic O100/C102/H110/L100, V200 and explicitly supplied 14 prior volumes 100 each: body_ratio0.2, average 100, volume_ratio2. These are strictly inside the displayed small-body/high-volume conditions. At body_ratio0.6 or volume_ratio1.5 exact equality handling is null unless supplied. Omitting average inclusion/reset prevents an automatic faithful zone flag.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap/family_levels; the previous formula labels R-J14. Retained 0.3/2.5 constants do not match the printed settings; a reset that only starts at 09:30 can also delay availability. Existing behavior is not authority over this procedure.


<a id="o059"></a>

## O059 — Source setup quality and exposure

**Wiki:** [Source setup quality and exposure](/workspace/planning/phase-1-live/wiki/quality-grade.md). **Implementation mode:** source grade and necessary-condition audit; no universal grading engine.

Green Bird says no relevant sweep means not A+, while his raw record also includes smaller non-A+ scalps. Sires separately labels deliberate early attempts B+ and distinguishes them from confirmed entries. [GB] pp.21–23, 37–40; [K18] pp.5–6, 14.

**Not a standalone trade.** A relevant sweep is necessary for Green Bird's A+ label, not sufficient for every A+ setup. A quality label does not create an entry or excuse a failed prerequisite.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author, candidate/branch, source grade/reasons, relevant same-candidate sweep, grade availability and selected exposure. |
| Outputs / units | source_grade, necessary_grade_condition_ok?, unpublished_grade_fields[], grade_known_at. |
| ET clock / interval | Grade and exposure choice before the action they qualify. |
| Bars / event membership | Evidence belongs to actual candidate; not any sweep on same day. |
| Reset / persistence | Per candidate/author; a later regrade is a new record. |
| known_at | Actual source grade/reason availability. |

**Procedure:**

1. For Green Bird A+ require the relevant sweep. No sweep proves not A+; a sweep alone does not prove A+ because sufficient criteria are unpublished.
2. Keep smaller directional non-A+ scalps as their incomplete method. Keep Sires B+ early attempts distinct from confirmed entries.
3. Do not let a grade excuse failed sequence prerequisites or manufacture position size.

**Printed constants and limits:** Source literal A+/B+ labels; no numerical score or sizing multiplier.

**Invalid / unavailable behavior:** Same-day unrelated sweep; hindsight grade; necessary condition treated as biconditional. Apply C04; emit `HOLE:O059:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O059-F1 — numeric fixture:** Synthetic GB candidate at a preselected high of 110 has a fully evidenced required-sweep flag=false and a supplied A+ label: the necessary grade condition fails. With a sweep above 110 but no other grade evidence, automatic A+ remains null. A Sires B+ early entry remains an early entry, not a confirmed-refill pass.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-G10/G11 and R-S01/S03 attach only partially. A universal grade engine and event-linked sizing record are missing. Existing behavior is not authority over this procedure.


<a id="o060"></a>

## O060 — Auction balance

**Wiki:** [Auction balance](/workspace/planning/phase-1-live/wiki/auction-balance.md). **Implementation mode:** source-selected accepted band; automatic selector hole.

Balance is an accepted area with repeated two-sided trade; imbalance is directional discovery between accepted areas. Sires maps the current auction before choosing an execution branch. Saint fits the actual HTF balance and waits for rebalance on an unbalanced trending profile. [AMT1] pp.3–10; [RTVP] pp.3–11; [MATH] pp.12–14.

**Not a standalone trade.** A balance rectangle does not license every edge fade. Saint and Sires retain different permissions for trading an established trend.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author/auction ID, selected bounds, scale/profile scope, prior two-sided acceptance evidence and known_at, later migration events. |
| Outputs / units | balance_band, balance_width, source_acceptance?, balance_active_at_use?, automatic_balance=null. |
| ET clock / interval | Actual source auction ET; bounds fixed before arrival. |
| Bars / event membership | Source timeframe/profile snapshot; no arbitrary stale/final profile. |
| Reset / persistence | Each selected auction/balance version; migration creates a new version. |
| known_at | When bounds and acceptance evidence were available, not after the later reaction. |

**Procedure:**

1. Ingest the source-selected accepted area and evidence of repeated two-sided trade. Validate L≤H and compute width H-L.
2. Keep balance bounds separate from VA and full price range. Later discovery/migration is a new observed state.
3. No universal quantitative balance detector is disclosed. Saint waits for rebalance in an unbalanced trending profile; Sires's other trend permissions do not override that.

**Printed constants and limits:** No minimum touches, duration, width or two-sided ratio.

**Invalid / unavailable behavior:** Outcome-selected rectangle; final shape used early; cross-author permission transfer. Apply C04; emit `HOLE:O060:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O060-F1 — numeric fixture:** Synthetic source balance [100, 110] declared 09:20 has width 10. Price 108 at 09:40 is inside that band; this does not prove an edge fade. A replacement [105, 115] drawn 10:30 cannot qualify the 09:40 arrival.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_value; [family_open.value_area](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); formulas_jumbo profile helpers; the previous formula labels R-A01–A11/A16/A17. Automatic source-selected balance bands are missing. Existing behavior is not authority over this procedure.


<a id="o061"></a>

## O061 — Volume profile

**Wiki:** [Volume profile](/workspace/planning/phase-1-live/wiki/value-and-profiles.md). **Implementation mode:** exact executed volume histogram; source auction/bin selection required.

A volume profile distributes executed volume by price over a specified auction. POC, value, nodes, shelves and ledges are different readings of it. Jumbo later adds profile information at range references; Sires and Saint use it to locate current accepted structure. [VP2] pp.3–8; [RTVP] pp.3–11; [JR] pp.14, 48, 50.

**Not a standalone trade.** A volume histogram or its maximum is not a complete method. The current full-day profile cannot supply a morning confirmation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Canonical executed events p_i/v_i, source profile interval/as_of, instrument tick q, explicit price-bin width/grid/membership convention. |
| Outputs / units | native_volume_by_price, source_bins[], total_volume, profile_id, coverage, as_of. |
| ET clock / interval | Source-selected [start, as_of) ET interval or explicit event-key endpoint; no current final session. |
| Bars / event membership | Executed trades only for faithful volume-by-price. OHLC volume allocation is a named proxy. |
| Reset / persistence | New source auction/profile; developing snapshots append; contract changes/gaps terminate complete coverage. |
| known_at | Latest included event availability after the declared profile interval, plus source selection availability. |

**Procedure:**

1. Sum all valid execution sizes at each exact native price. Unknown aggression still contributes total volume. Exclude quote updates and duplicate tape copies.
2. If source bins are exact tick prices, keep that grid. For explicitly supplied wider bins assign each price using the supplied origin/boundaries/membership and sum member volumes; do not invent an automatic bin width or rounding.
3. Require Σbin_volume=Σincluded_execution_size and preserve explicit known-empty versus uncovered rows. A source histogram can be supplied directly with provenance when construction is absent.
4. POC/value/nodes are separate derived readings; this histogram alone does not define them all.

**Printed constants and limits:** No universal number of bins, bandwidth or session start.

**Invalid / unavailable behavior:** Uniform OHLC allocation called exact; final RTH profile at morning touch; missing bins treated zero; overlapping files doubled. Apply C04; emit `HOLE:O061:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O061-F1 — numeric fixture:** Synthetic trades 100×2, 100.25×3, 100×1 give native bins 100:3 and 100.25:3, total 6. Under explicitly supplied [100, 100.5) bin both aggregate to 6. A quote update size 50 contributes 0 volume. Unspecified source binning leaves source-compatible binned profile unknown, while native totals remain exact.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_open.scan_prior_rth_trade_vp](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); family_value; [mbp1_objects.vp_rth](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); the previous formula labels P3-04/P3-07 and R-J16/J17, R-A01–A18. Developing source-aligned snapshots are partial. Existing behavior is not authority over this procedure.


<a id="o062"></a>

## O062 — Profile value area

**Wiki:** [Profile value area](/workspace/planning/phase-1-live/wiki/value-area.md). **Implementation mode:** source-specific VA geometry/coverage; undisclosed construction hole.

VAH and VAL bound the selected profile's value area. They are not the whole price range and can migrate in a developing profile. The lessons commonly discuss 70% value, while Sires's order-flow discussion also uses a 40% intraday setting; the source setting must travel with the object. [VP2] pp.4–6; [C3] pp.6–7; [AMT1] pp.6–9. Saint separately describes 68% value; retain that source fraction rather than importing the other lesson settings. [RTVP] p.4.

**Not a standalone trade.** A VA edge touch is not acceptance, rejection or entry. One source's value fraction is not a global replacement for every profile.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Profile histogram, author/fraction f, source VA algorithm/contiguity/POC expansion/tie conventions or supplied VAL/VAH, fixed/developing identity. |
| Outputs / units | val, vah, fraction, volume_inside, achieved_fraction, construction_known, known_at. |
| ET clock / interval | Parent profile as-of ET; prior fixed and current developing VAs keep different IDs. |
| Bars / event membership | Parent executed volume/TPO basis as actually selected; do not mix them. |
| Reset / persistence | Exactly parent profile/version and source settings. |
| known_at | Parent snapshot plus construction/selection availability. |

**Procedure:**

1. Retain source fraction:70% in the common lesson, 40% in Sires's selected intraday discussion, 68% in Saint. They are distinct configurations.
2. If complete source VA algorithm and tie rules exist, execute them literally. These sources do not settle one universal expansion/row-pairing/tie rule; absent configuration gives automatic VAL/VAH=null. Do not silently inherit the old greedy helper.
3. For supplied bounds, sum the included source bins under the supplied boundary convention and divide by total volume. Check coverage of the claimed fraction as an arithmetic audit, not proof that these were the correct algorithmic bounds.
4. Opening inside balance and opening inside VA are separate comparisons.

**Printed constants and limits:** 0.70, 0.40, 0.68 scoped as above; no universal algorithm.

**Invalid / unavailable behavior:** Author fraction swapped; tie guessed; TPO/volume basis mixed; final VA used early. Apply C04; emit `HOLE:O062:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O062-F1 — numeric fixture:** Synthetic total volume 100 and supplied Saint VA bins summing 68 gives achieved_fraction0.68. It meets the literal 68% coverage check but not a 70% requirement. Two different bands can each contain 68; that fact does not resolve the missing selection algorithm.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_open.value_area](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); [formulas_flow.developing_va](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-A01/A03/A04/A08 and R-S09, P3-04. Existing behavior is not authority over this procedure.


<a id="o063"></a>

## O063 — Developing profile snapshot

**Wiki:** [Developing profile snapshot](/workspace/planning/phase-1-live/wiki/developing-profile.md). **Implementation mode:** immutable causal profile snapshots.

The developing profile is the state visible so far. Sires rereads it after an impulse; Keani first observes value building higher and only later trades a break/retest of the current VAH. [AMT1] pp.12–13; [AVG] pp.21–22; [JR] pp.14, 48.

**Not a standalone trade.** The final bullish profile or final POC is not a pre-entry fact. A moving boundary by itself is not a trade.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Parent profile definition, ordered events through each stage key, source settings, available POC/VA/node recipes. |
| Outputs / units | snapshot_id, as_of, volume_histogram, poc?, val?, vah?, H, L, known_at. |
| ET clock / interval | Source reset followed by each actual decision/impulse stage ET. |
| Bars / event membership | Only elapsed executed/TPO observations; incomplete future letter cannot be marked complete. |
| Reset / persistence | Parent auction reset; each update gets a new snapshot ID. |
| known_at | Maximum included observation and source-setting availability. |

**Procedure:**

1. Recompute/update cumulative native histogram from only events before the stage's as-of. Persist immutable snapshot or reproducible input locator.
2. Derive POC/VA only under their source-complete conventions; propagate their holes.
3. For Keani use prior VAH at opening and a separately frozen developing VAH at later break/retest. Do not overwrite either ID with the final-day boundary.

**Printed constants and limits:** No polling cadence or automatic profile selector; snapshot at actual required stages.

**Invalid / unavailable behavior:** Earlier snapshot mutated; final-day POC; moving retest target switched after break. Apply C04; emit `HOLE:O063:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O063-F1 — numeric fixture:** Synthetic at 10:00 bins 100:10/101:5 gives unique POC 100; at 10:30 added 101:10 gives unique POC 101. A 10:05 action still sees first snapshot POC 100. The later value cannot revise its evidence.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_value; [formulas_flow.developing_va](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [mbp1_objects.vp_rth](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); the previous formula labels R-J16, R-A01/A17, R-S09. Reliable event-time snapshots and joins are partial. Existing behavior is not authority over this procedure.


<a id="o064"></a>

## O064 — Profile point of control

**Wiki:** [Profile point of control](/workspace/planning/phase-1-live/wiki/profile-poc.md). **Implementation mode:** maximum-volume row with explicit tie handling.

Volume POC identifies the highest-volume price under the selected construction. It can be fair-value destination, a continuation test or part of another auction reference. Saint reads failure versus efficient passage at POC; Sires's strict absorption fade excludes a middle/POC location. [VP2] pp.3–7; [AMTL] pp.8–11; [ABS] pp.5–8.

**Not a standalone trade.** POC is neither the geometric midpoint nor universally a place to fade. One branch's POC restriction does not ban its use as another branch's target.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source profile bins/price convention/as_of, volume per bin, source tie rule or supplied POC. |
| Outputs / units | max_volume, poc_candidates[], poc_price_or_band?, tie_state, known_at. |
| ET clock / interval | Parent profile snapshot ET. |
| Bars / event membership | Volume bins, not time-count TPO unless source explicitly names TPO POC separately. |
| Reset / persistence | Parent profile/version. |
| known_at | Parent snapshot availability plus tie resolution evidence. |

**Procedure:**

1. Find max bin volume and every bin attaining it. If exactly one bin, return that source bin's price/band; retain the price-within-bin convention.
2. If tied, apply only a published/supplied source tie rule. Otherwise poc=null with all tied candidates and HOLE:poc_tie; do not choose lowest/highest/nearest midpoint.
3. Keep midpoint MPOC separate. POC role depends on branch: destination, passage/failure test, or excluded middle location for strict absorption fade.

**Printed constants and limits:** Maximum volume definition; no invented tie rule.

**Invalid / unavailable behavior:** Midpoint alias; final profile at earlier decision; after-the-fact refill alignment as gate. Apply C04; emit `HOLE:O064:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O064-F1 — numeric fixture:** Synthetic bins 100:4, 101:10, 102:6 give POC 101 and max 10. Change 102 to 10 => tied candidates [101, 102], faithful POC null absent tie rule. Profile midpoint(100+102)/2=101 in first case is coincidental, not the POC formula.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_open.value_area](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); [mbp1_objects.vp_rth](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_jumbo.a05_poc_tell](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A05/A06 and P3-04. Existing behavior is not authority over this procedure.


<a id="o065"></a>

## O065 — Untested prior POC

**Wiki:** [Untested prior POC](/workspace/planning/phase-1-live/wiki/naked-poc.md). **Implementation mode:** as-of untouched-reference ledger.

An older POC that has not yet been revisited is a possible destination or reaction reference, depending on the live auction. It is one of the untouched landmarks mapped before action. [VP2] pp.6–8; [AMT1] pp.12–13; [MAMT] pp.9–11.

**Not a standalone trade.** An untouched POC alone is not Sires's Failed Auction setup; that setup requires an established balance, departure, actual older-POC tag and rejection.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Older completed profile POC, known_at, source contact/consumption scope, all intervening covered prices, decision key. |
| Outputs / units | untested_at_decision?, first_qualifying_visit?, active_reference_id. |
| ET clock / interval | From older POC availability through strictly before current decision in source scope. |
| Bars / event membership | Ordered prices or complete range bars for contact; ambiguous intra-bar ordering stays unknown. |
| Reset / persistence | New older POC reference; a later visit changes its state, not original known_at. |
| known_at | Untested status at current as-of only with complete intervening observation. |

**Procedure:**

1. Initialize untested after reference becomes known. Apply the specified contact rule only to eligible later observations.
2. A qualifying visit at/before decision makes untested false; no visit with full coverage makes true. Missing scope/coverage makes null.
3. Keep this older profile distinct from the established balance in Sires FA. Untested POC alone does not establish that branch.

**Printed constants and limits:** No proximity tolerance or lookback default.

**Invalid / unavailable behavior:** Future visit used early; same established POC masquerades as older external POC; gaps treated absence. Apply C04; emit `HOLE:O065:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O065-F1 — numeric fixture:** Synthetic older POC 105 known yesterday 16:00; no visits through 09:40 under complete coverage =>untested true. First visit 105 at 09:45 changes status false afterward, not at 09:40. Missing overnight coverage makes earlier untouched status null if overnight visits count.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Profile and level ingredients; [formulas_jumbo.a06_failed_auction](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A06/P3-04. A persistent as-of untouched-reference ledger is missing. Existing behavior is not authority over this procedure.


<a id="o066"></a>

## O066 — High-volume node

**Wiki:** [High-volume node](/workspace/planning/phase-1-live/wiki/hvn.md). **Implementation mode:** source-selected node band with literal profile measurements; selector hole.

An HVN is a locally accepted concentration of volume; a minor HVN can refine a reaction area inside the larger auction. The unnamed member requires an independently identified minor HVN plus prior reaction history. [VP2] pp.3, 6–8; [K10] pp.5–8; [JR] pp.14, 48.

**Not a standalone trade.** The first detected peak, one high-volume price or a rounded resistance line is not automatically the member's two-reason setup.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Profile/as_of, source node bounds/peak/scale, adjacent structure, independent reaction band if required. |
| Outputs / units | hvn_band, node_volume, peak_candidates, source_node_known, automatic_node_selection=null. |
| ET clock / interval | Node identified before arrival under its profile as-of. |
| Bars / event membership | Source histogram bins; not whole-day hindsight. |
| Reset / persistence | Each profile/node version; minor versus major scale preserved. |
| known_at | Profile plus source node selection availability. |

**Procedure:**

1. Ingest the selected HVN area and sum its bins; calculate its local maximum with explicit tie handling.
2. The source does not publish universal smoothing, prominence or bandwidth. Do not label the first peak as the source minor HVN.
3. For the member require independent node provenance and prior reaction history, followed by actual contact/current response.

**Printed constants and limits:** No peak-prominence, neighborhood or width threshold.

**Invalid / unavailable behavior:** One max bin automatically HVN; final-day node; reaction line reused as independent node. Apply C04; emit `HOLE:O066:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O066-F1 — numeric fixture:** Synthetic supplied node [100, 102] with volumes 4/10/6 has volume 20 and peak 101. Independently supplied reaction [100.5, 101.5] overlaps [100.5, 101.5]. That overlap is geometry only; absent independent HVN evidence the two-reason gate is null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.profile_nodes](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_s06_two_reason/r_s08_minor_node](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-A16/A17, R-S06/S08 and R-J17. Source band selection is partial. Existing behavior is not authority over this procedure.


<a id="o067"></a>

## O067 — Low-volume node

**Wiki:** [Low-volume node](/workspace/planning/phase-1-live/wiki/lvn.md). **Implementation mode:** source-selected bridge between accepted areas; detector hole.

An LVN is the lower-participation connection between accepted areas; price can travel through it quickly or react at its boundary. Sires stresses the second transition back into balance: an outer taper alone is not the complete structure. [VP2] pp.3–5; [MATH] pp.12–14; [RTVP] pp.7–8.

**Not a standalone trade.** The minimum histogram bin or a thin tail outside one hump is not automatically a valid LVN or an entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Profile bins, two accepted-area IDs/bounds, connecting source LVN band/trough and snapshot. |
| Outputs / units | bridge_band, bridge_volume, trough_candidates, left_transition, right_transition, source_lvn_known?. |
| ET clock / interval | Both accepted areas and bridge identified before use ET. |
| Bars / event membership | Complete histogram grid with known-empty versus missing bins. |
| Reset / persistence | Per profile/bridge identity. |
| known_at | Latest constituent profile/area-selection availability. |

**Procedure:**

1. Require two distinct neighboring accepted areas and the low-participation connection between them. Record both transitions.
2. Sum source bridge volume and identify minimum-volume bins only as measurements. Min bin or one outer taper alone does not prove a valid LVN.
3. No universal node threshold/second-transition detector is disclosed. An LVN alleged outside 6–9 cannot be derived solely from a profile restricted inside 6–9.

**Printed constants and limits:** No minimum-volume ratio or smoothing width.

**Invalid / unavailable behavior:** Outer tail as bridge; absent second accepted area; missing bins treated zeros; range-scope contradiction. Apply C04; emit `HOLE:O067:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O067-F1 — numeric fixture:** Synthetic accepted bins 100:10 and 104:12, supplied bridge 101:2/102:1/103:2 gives bridge volume 5, trough 102. Remove the 104 accepted area: two-sided bridge validity is null/false if the complete profile proves it absent, even though 102 remains the minimum.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.profile_nodes/profile_ledges](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_f11_delta_lvn](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-A17, R-F11 and R-J17. Sparse-bin heuristics and final-RTH profiles are partial. Existing behavior is not authority over this procedure.


<a id="o068"></a>

## O068 — Profile shelf

**Wiki:** [Profile shelf](/workspace/planning/phase-1-live/wiki/profile-shelf.md). **Implementation mode:** source shelf body/transition geometry; detector hole.

A shelf is a shelf-like accepted volume structure; the body and its transition must be distinguished from the ledge at the edge. It is a location/read used with acceptance, rejection or continuation. [VP2] pp.4–5; [MATH] p.13; [RTVP] pp.7–8.

**Not a standalone trade.** A hand-drawn shelf rectangle is not proof of a computed absorption event, and it is not interchangeable with the value-area boundary.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Profile/as_of, source shelf body bounds, neighboring taper/LVN transition and source drawing/construction. |
| Outputs / units | shelf_body, transition_band, body_volume, edge_ids, automatic_shelf=null. |
| ET clock / interval | Source structure before use ET. |
| Bars / event membership | Profile bins in selected scale. |
| Reset / persistence | Per shelf/profile version. |
| known_at | Profile and source selection time. |

**Procedure:**

1. Retain body and transition as separate bands; sum their volumes from the identified profile.
2. No source fixed thickness or generic volume-drop threshold is disclosed. A shelf is neither automatically a VA edge nor observed absorption.
3. Link any later break/retest to the selected ledge recipe.

**Printed constants and limits:** No shelf thickness or drop ratio.

**Invalid / unavailable behavior:** Shelf body merged with edge; every decline called shelf; later profile substituted. Apply C04; emit `HOLE:O068:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O068-F1 — numeric fixture:** Synthetic supplied shelf [100, 102] with volumes 8/8/7 totals 23; transition [103, 104] with 3/1 totals 4. The shelf body remains [100, 102]; neither volume ratio 23/4 nor VAH automatically defines its ledge algorithm.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.profile_ledges/profile_nodes](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A02/A16/A17, R-J17 and P3-07. Source thickness and automatic shelf selection remain partial. Existing behavior is not authority over this procedure.


<a id="o069"></a>

## O069 — Profile ledge

**Wiki:** [Profile ledge](/workspace/planning/phase-1-live/wiki/profile-ledge.md). **Implementation mode:** source-selected structural edge and same-edge join.

A ledge is the edge/cutoff of the relevant shelf or accepted volume area. Sires contrasts stable structural ledges with value-area lines that can change with calculation/settings. [VP2] pp.4–8; [MATH] p.13.

**Not a standalone trade.** A ledge is a location. Breaking it still requires the chosen acceptance/retest and flow sequence; it is not another system.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Profile/shelf IDs, source edge price/band, adjacent volume contrast, as_of, later break/retest IDs. |
| Outputs / units | ledge_id, ledge_band, neighbor_volumes, same_ledge_retest?, automatic_edge=null. |
| ET clock / interval | Ledge selected before break; retest later ET. |
| Bars / event membership | Profile structure plus actual ordered reaction prices. |
| Reset / persistence | Each shelf/ledge version; stable ID survives later VA drift. |
| known_at | Source structural selection availability. |

**Procedure:**

1. Ingest the shelf's specific cutoff and native bounds. Store neighboring measured volumes without inventing a contrast threshold.
2. Require break and return to the same ledge ID. A later changed VAH or nearest final profile boundary is not the retest reference.
3. Acceptance/defense remains the execution route's confirmation.

**Printed constants and limits:** No automatic edge-selection threshold.

**Invalid / unavailable behavior:** VA line substitution; nearest-price join; reference selected after retest. Apply C04; emit `HOLE:O069:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O069-F1 — numeric fixture:** Synthetic ledge 102 known 09:50 breaks 10:00 and retests 102 at 10:05: same ID true. Developing VAH has moved 103 by 10:05; touching 103 is not a retest of ledge 102 without an explicit source relationship.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.profile_ledges](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_jumbo.a02_ledge_retest_hold](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A02/A16/A17 and P3-07. Exact source edge-selection thresholds are unpublished. Existing behavior is not authority over this procedure.


<a id="o070"></a>

## O070 — Composite auction profiles

**Wiki:** [Composite auction profiles](/workspace/planning/phase-1-live/wiki/composite-profiles.md). **Implementation mode:** sum source-selected constituent auctions; selector hole.

Profiles can combine the periods relevant to the current auction and its higher-timeframe objective. Sires distinguishes a small intraday auction from a weekly/swing scale; the current auction's structure determines the useful aggregation. [VP2] pp.6–8; [MATH] pp.12–14; [K10] pp.5–7.

**Not a standalone trade.** A fixed 5/20/250-day composite is not a universal source prescription and its node is not an entry on contact.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Explicit constituent session/auction IDs, nonoverlapping event ownership, common instrument/bin convention, selection rationale/as_of. |
| Outputs / units | composite_histogram, constituent_ids, total_volume, known_at, automatic_window_selection=null. |
| ET clock / interval | Source-selected constituent windows ET; current constituent clipped to available as-of if developing. |
| Bars / event membership | Canonical executed profiles on compatible exact grid. |
| Reset / persistence | New constituent membership/configuration version; no universal rolling lookback. |
| known_at | Maximum constituent availability and selection time. |

**Procedure:**

1. Validate compatible instruments/price grid and disjoint event ownership. Sum matching bins over only available constituents.
2. If constituent windows overlap, count each canonical event once under a declared ownership manifest; do not add overlapping histograms blindly.
3. Require the source auction-selection rationale.5/20/250-day profiles can be named comparison variants only; none is a universal source rule.

**Printed constants and limits:** No fixed composite lookback.

**Invalid / unavailable behavior:** Overlapping volume doubled; future constituent; undeclared roll; source selection replaced by fixed lookback. Apply C04; emit `HOLE:O070:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O070-F1 — numeric fixture:** Synthetic disjoint profiles A{100:3, 101:2}, B{100:4, 101:1} give composite{100:7, 101:3}, total 10. If B includes the same 2-contract event already in A, naïve 10 is wrong; ownership must remove that duplicated contribution or return overlap hole.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_value and profile primitives; the previous formula labels R-A16/A17/P3-07. Source-selected multi-session composites are missing or partial. Existing behavior is not authority over this procedure.


<a id="o071"></a>

## O071 — Source-selected dealing range

**Wiki:** [Source-selected dealing range](/workspace/planning/phase-1-live/wiki/dealing-range.md). **Implementation mode:** source-selected thesis band and controlling structure.

The dealing range is the actual swing/auction band framing the thesis, control and objective. Session examples draw reaction/defense as areas; re-entry is considered only when price returns to the same area and produces fresh evidence. [K18] p.4; [CONT] pp.4–10; [ANAT] pp.7–9; [TRAP] pp.3–4.

**Not a standalone trade.** A future-selected swing box or an arbitrary opening clock box is not the source dealing range. Remaining somewhere nearby is not a defended re-entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Auction/band ID, source bounds/scale/rationale, thesis side, controlling extreme, selection time and later tests. |
| Outputs / units | dealing_band, width, controlling_reference, band_known_before_use. |
| ET clock / interval | Actual source band selection ET; no automatic opening-clock range. |
| Bars / event membership | Source swing/profile/auction evidence; automatic selection undisclosed. |
| Reset / persistence | Explicit new source auction/thesis version; stop-out alone does not reset band. |
| known_at | Bound confirmations and source selection time. |

**Procedure:**

1. Freeze the supplied actual dealing area with its own identity and compute width.
2. Keep microbalance, larger range and prior profile as separate parent objects. Return/re-entry must reference the same source area with fresh evidence.
3. Missing band selector/confirmation makes automatic range unknown; do not draw it around later favorable movement.

**Printed constants and limits:** No fixed clock, fractal length or width.

**Invalid / unavailable behavior:** Future swing rectangle; stop-out redraw; unrelated nearby area join. Apply C04; emit `HOLE:O071:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O071-F1 — numeric fixture:** Synthetic long dealing band [100, 105], controlling low 100 selected 09:40 remains the reference after a 09:50 stop-out. A 10:00 return 104 is inside it; replacing bounds with [103, 108] because later price rose is invalid.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_s07_areas/r_s08_minor_node](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) and profile ingredients; the previous formula labels R-S07/S08, R-A16/A17. Stable band identity and source selection are missing. Existing behavior is not authority over this procedure.


<a id="o072"></a>

## O072 — Prior defended reaction area

**Wiki:** [Prior defended reaction area](/workspace/planning/phase-1-live/wiki/prior-reaction-area.md). **Implementation mode:** same-band historical defense record.

A previously observed clean reaction or defended band supplies a location for a later test. The unnamed member pairs this history with an independent minor HVN; Sires requires fresh same-band defense on a return. [K10] pp.5–8; [ANAT] p.7; [CONT] pp.4–10.

**Not a standalone trade.** Remembering a prior bounce does not authorize another entry; the new touch must satisfy the current thesis and confirmation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source band bounds/ID, prior reaction event/side/availability, independent node if required, current contact and fresh confirmation. |
| Outputs / units | prior_defense_known, same_band_contact, current_defense?, history_ids. |
| ET clock / interval | Prior reaction must end and be known before current arrival ET. |
| Bars / event membership | Ordered source reaction events/complete bars; qualitative clean/defended selector remains supplied or hole. |
| Reset / persistence | Band/thesis identity; retain all distinct tests chronologically. |
| known_at | Prior evidence actual availability; current evidence only when observed. |

**Procedure:**

1. Ingest the earlier source-defined reaction and validate its interval precedes the new test.
2. Require current contact with the same frozen band, then the current method's new confirmation. Earlier bounce is location evidence only.
3. The member additionally needs independently selected minor HVN; Sires needs current thesis and fresh same-band defense.

**Printed constants and limits:** No automatic clean-bounce threshold or memory horizon.

**Invalid / unavailable behavior:** Current outcome used as prior memory; different band; old defense reused as new confirmation. Apply C04; emit `HOLE:O072:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O072-F1 — numeric fixture:** Synthetic band [100, 101] defended 09:30, known 09:32, contacted again 10:00: prior_defense_knowntrue. A fresh defense 10:02 is unavailable at 10:01. A separate band [102, 103] cannot inherit that memory.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_s06_two_reason/r_s08_minor_node](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-S06/S08. Current helpers do not supply complete contact, history and same-band joins. Existing behavior is not authority over this procedure.


<a id="o073"></a>

## O073 — Overnight volume structure

**Wiki:** [Overnight volume structure](/workspace/planning/phase-1-live/wiki/overnight-profile.md). **Implementation mode:** source overnight profile and landmarks; exact window/selection required.

The overnight profile describes accepted volume, bridge LVNs, shelves and POC before the cash open. Sires then reads whether the opening auction holds or aggressively breaks the relevant shelf. [MAMT] pp.14–16; [TBR] pp.16–24.

**Not a standalone trade.** A final-RTH POC cannot be part of the preopen overnight read. An overnight shelf is not a fixed buy/sell level without current confirmation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Verified overnight window, executed profile, source H/L/POC/VA/shelf/bridge IDs, older external POC if aligned, cash-opening event. |
| Outputs / units | overnight_profile_snapshot, landmarks[], older_poc_alignment?, known_at. |
| ET clock / interval | Source overnight interval ends before current cash-open read; exact source window must be supplied, not inferred from a generic ETH label. |
| Bars / event membership | Executed profile recipe and source-selected structures. |
| Reset / persistence | Each overnight auction/window; older POC retains separate older profile ID. |
| known_at | Window completion plus source structure availability before the opening decision. |

**Procedure:**

1. Build or ingest the overnight profile using the selected source clock and bin settings; propagate missing profile/node definitions.
2. Match older POC alignment to the source overnight LVN, in native price units and with explicit bands. Do not substitute today's later developing/final RTH POC.
3. Record current opening hold/aggressive break as later route evidence, not a preopen profile property.

**Printed constants and limits:** No universal overnight profile clock/tolerance.

**Invalid / unavailable behavior:** Final RTH POC as preopen input; old/current POC alias; invented shelf. Apply C04; emit `HOLE:O073:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O073-F1 — numeric fixture:** Synthetic supplied overnight LVN [100, 101] and older POC 100.5 align geometrically. Today's final RTH POC 103 does not change this. A 09:31 opening hold is unavailable to a 09:30 decision.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_open.value_area](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); family_value; the previous formula labels R-A12/A13, R-J06 and P3-04. Exact source band selection and some POC-alignment joins are partial. Existing behavior is not authority over this procedure.


<a id="o074"></a>

## O074 — Overnight directional inventory

**Wiki:** [Overnight directional inventory](/workspace/planning/phase-1-live/wiki/overnight-inventory.md). **Implementation mode:** source inventory interpretation with causal measurements; classifier hole.

Inventory describes the overnight auction's net directional positioning and location, then asks how RTH responds at its LVN/shelf. It changes expectations through the hold or aggressive break. [MAMT] p.14; [AMT1] pp.12–13.

**Not a standalone trade.** An inventory label is context, not a direction to trade regardless of the opening response.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source overnight auction, preopen direction/positioning evidence, source inventory label, selected LVN/shelf, open location and later response. |
| Outputs / units | source_inventory:net_long/net_short/balanced/unknown, measured_evidence, opening_response?. |
| ET clock / interval | Inventory from completed overnight observations; opening response later ET. |
| Bars / event membership | Source profile/price/flow basis, not assumed close-minus-open classifier. |
| Reset / persistence | Each overnight auction and later source reread. |
| known_at | Inventory evidence before RTH; response when actually observed. |

**Procedure:**

1. Retain source direction evidence and label without inventing a universal net-long threshold.
2. Freeze the selected shelf/LVN before RTH. Record later hold versus aggressive break separately and apply the chosen Sires route.
3. A later correction cannot set the earlier inventory label; the 94% either-edge claim is a separate context statistic.

**Printed constants and limits:** No automatic inventory percentage or price threshold.

**Invalid / unavailable behavior:** Later correction as classifier; overnight close sign substituted without source; either-edge claim converted to directional certainty. Apply C04; emit `HOLE:O074:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O074-F1 — numeric fixture:** Synthetic supplied net_long inventory known 09:20 and shelf 100; opening break below 99 at 09:35 is a later observed response. It does not retroactively change net_long to net_short. Missing inventory definition/record =>label null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-A12; family_open and profile ingredients. A source-exact inventory classifier and causal response join are partial. Existing behavior is not authority over this procedure.


<a id="o075"></a>

## O075 — ETH profile identity

**Wiki:** [ETH profile identity](/workspace/planning/phase-1-live/wiki/prior-eth-profile.md). **Implementation mode:** source ETH identity binding; unresolved scope conflict preserved.

The source's ETH profile must be identified from its actual auction window and labels. The AMT statistics distinguish overnight extremes and the previous ETH balance; those are not automatically prior RTH value or a generic full-day profile. [MAMT] pp.14–16; [TBR] pp.16–24.

**Not a standalone trade.** Calling a profile ETH does not settle whether it is the overnight interval, prior full session or another selected auction. Its target statistic is not an entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal source ETH label, dated start/end, prior/current relationship, profile H/L/VA/POC/MPOC and source setting/availability. |
| Outputs / units | eth_profile_id, scope_resolved?, balance_band?, va_band?, known_at, scope_holes[]. |
| ET clock / interval | Actual source ETH interval; overnight, previous full session and prior RTH are not aliases. |
| Bars / event membership | Parent profile input, with literal source clock evidence. |
| Reset / persistence | Per dated source ETH auction. |
| known_at | Selected profile completion/availability before current opening condition. |

**Procedure:**

1. Resolve the source profile's real window and relation to current RTH. If the drawing/prose does not settle balance versus VA or exact ETH scope, preserve both literal observations and mark affected condition unknown.
2. Keep the 94% either ON edge and 73% previous ETH balance-to-MPOC claims separate. Do not choose the easier denominator.
3. Compute only verified geometry; unresolved identity prevents faithful statistical cohort admission.

**Printed constants and limits:** No universal ETH reset or balance=VA rule.

**Invalid / unavailable behavior:** Prior RTH substitution; convenient interpretation of conflicting figure; full session/overnight merge. Apply C04; emit `HOLE:O075:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O075-F1 — numeric fixture:** Synthetic prior ETH price balance [100, 120], VA [105, 115], open 103 gives inside balance=true and inside VA=false. If the source's intended condition is unresolved, 73% cohort eligibility is null; do not select either to improve results.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_open/family_value; the previous formula labels R-A12/A13 and R-J06. Generic prior/full/overnight field names do not resolve source identity. Existing behavior is not authority over this procedure.


<a id="o076"></a>

## O076 — MPOC: the profile midpoint

**Wiki:** [MPOC: the profile midpoint](/workspace/planning/phase-1-live/wiki/mpoc.md). **Implementation mode:** source-printed profile midpoint.

MAMT explicitly labels the mid of the profile MPOC. It is different from volume POC. The 73% statement is conditional on RTH opening inside the previous ETH profile's balance. [MAMT] pp.15–16.

**Not a standalone trade.** MPOC is a target-context object; the percentage is not a trade admission rule or volume-POC hit rate.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Verified source profile H/L and scope, known_at, current opening condition, later price path. |
| Outputs / units | mpoc=(H+L)/2, profile_id, opening_condition?, later_contact?. |
| ET clock / interval | Prior source ETH profile completion then current RTH observation. |
| Bars / event membership | Profile price bounds plus later prices; not maximum-volume bin. |
| Reset / persistence | Per selected profile. |
| known_at | Profile bounds/scope availability; opening condition at actual open. |

**Procedure:**

1. Compute midpoint from full selected profile H/L. Keep independently computed volume POC in another field.
2. Use as a destination only under the source's selected context. The 73% statement requires opening inside previous ETH balance and retains that condition's unresolved details.
3. Measure later contact after the relevant decision; do not interpret the printed percentage as a method win rate.

**Printed constants and limits:** Midpoint 0.5; printed 73% is a source claim, not a computed probability.

**Invalid / unavailable behavior:** POC substituted; wrong profile; unconditional 73% claim. Apply C04; emit `HOLE:O076:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O076-F1 — numeric fixture:** Synthetic ETH H120/L100 gives MPOC 110. A volume POC at 114 stays 114. A later price 110 touches MPOC even if 114 is untouched; these are two distinct outcome predicates.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-A13; profile/level geometry in family_value/family_levels. Source scope and the open-inside condition need explicit binding. Existing behavior is not authority over this procedure.


<a id="o077"></a>

## O077 — Signed volume-by-price profile

**Wiki:** [Signed volume-by-price profile](/workspace/planning/phase-1-live/wiki/weekly-delta-profile.md). **Implementation mode:** exact signed execution histogram for selected source window.

Executed delta by price adds who traded aggressively to where volume was accepted. Weekly/daily delta is used in the larger thesis; current local delta at a range location is a separate snapshot. [K18] p.4; [K2345] pp.4–6; [RD] pp.3–9; [JR] pp.14, 48.

**Not a standalone trade.** A positive/negative weekly total is not a local entry, and a light profile side is not automatically a structural LVN.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Canonical trades, corrected aggression, exact price bins, source daily/weekly/local window/as_of, instrument and source node pairings. |
| Outputs / units | buy_by_price, sell_by_price, unknown_by_price, total_by_price, delta_by_price=buy-sell, window_delta, known_at. |
| ET clock / interval | Source window/reset in ET; current week/current day clipped to actualas_of. |
| Bars / event membership | Executed events only; weekly totals and local contact snapshots distinct. |
| Reset / persistence | Selected source profile window; no universal calendar-week boundary. |
| known_at | Latest included execution availability; unresolved window prevents faithful source profile. |

**Procedure:**

1. At each price sum B buy volume and A sell volume under C03; N unknown volume separately. For no unknown volume, delta=buy-sell exact. With unknown volume, signed known contribution plus bounds [known_delta-unknown, known_delta+unknown] are measurements; faithful full delta is null unless source resolves sides.
2. Aggregate over the explicit source bins/window. Check buy+sell+unknown=total and sum price-delta equals known window delta.
3. A light signed profile side is not a structural LVN. Pair only with a separately identified price LVN. Final week/daily totals cannot confirm earlier entries.

**Printed constants and limits:** No weekly directional threshold or LVN inference.

**Invalid / unavailable behavior:** Old reversed A/B; future weekly volume; delta units treated price; quote depth as execution. Apply C04; emit `HOLE:O077:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O077-F1 — numeric fixture:** Synthetic price 100 has B7/A4 =>delta+3, total 11. Price 101 has B2/A5 =>delta-3, total 7; windowknown_delta0, total 18. Add unknown size 2 at 101: true window delta is unknown with interval [-2,+2], not exactly 0.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_tape.build_weekly_delta_table](/workspace/implementation/src/trading_research/research/phase1_live/family_tape.py); [family_value.scan_rth_delta](/workspace/implementation/src/trading_research/research/phase1_live/family_value.py); [formulas_flow.r_f11_delta_lvn](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F10/F11, R-J16 and P3-08. Causal profile selection is partial. Existing behavior is not authority over this procedure.


<a id="o078"></a>

## O078 — Time-price-opportunity profile

**Wiki:** [Time-price-opportunity profile](/workspace/planning/phase-1-live/wiki/tpo-ib-auction.md). **Implementation mode:** letter-aware time profile; exact source price visitation convention required.

TPO records which source letter periods visited each price and shows the time structure of the auction. It provides value context, single prints, excess, poor extremes and opening-period information. Keani's whole-A-period requirement uses this object. [TPO] pp.3–9; [AVG] pp.21–22.

**Not a standalone trade.** A TPO shape or label is not an entry. A trade-visited approximation is not automatically the same as the source's letter construction.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source session/price step q, 30-minute periods and labels, native price observations, source visited-trade versus period-range construction, as_of. |
| Outputs / units | memberships price→set(letter IDs), count_by_price, period H/L, completed_periods, known_at. |
| ET clock / interval | Source RTHA [09:30, 10:00), B [10:00, 10:30), then consecutive 30-minute letters ET. Keep session date with letter ID. |
| Bars / event membership | Per-source price-period membership; a trade-visited approximation is not automatically the source's plotted range coverage. |
| Reset / persistence | Each source TPO session/profile; counts do not cross session. |
| known_at | Membership at actual observation; whole-period facts at its completed end. |

**Procedure:**

1. For an explicitly selected trade-visited construction, map each trade price to a source price row and add that period ID once; 100 trades in A at one price give one A membership.
2. If the selected source uses all rows between period H/L, expand exactly that source grid after observing its bounds; do not claim this convention is established merely by existing code. Missing construction/grid is a fidelity hole.
3. Retain full lettersets rather than only counts. Derive interior prints/excess/poor extremes from the selected source's letter structure and currentas_of.
4. Keani's whole A low is min price during all of A and is unavailable before 10:00.

**Printed constants and limits:** 30-minute letters; A 09:30–10:00, B 10:00–10:30 from TPO lesson. Source grid/visitation must be verified.

**Invalid / unavailable behavior:** One TPO per trade; letter identity discarded; incomplete A called complete; final tail used early. Apply C04; emit `HOLE:O078:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O078-F1 — numeric fixture:** Synthetic selected trade-visited price 100 sees A twice and B once =>members{A, B}, count 2; price 101 sees A once=>{A}, count 1. A price 99 first seen 09:59 changes A-low to 99 at 10:00; it cannot be excluded from whole A test.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.tpo_trade_visited](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); family_gap; the previous formula labels R-A04/A14/A15 and R-S09, P3-04. Period identity and developing structure are partial. Existing behavior is not authority over this procedure.


<a id="o079"></a>

## O079 — TPO single-print structure

**Wiki:** [TPO single-print structure](/workspace/planning/phase-1-live/wiki/single-prints.md). **Implementation mode:** interior letter structure with supplied accepted distributions; selection holes preserved.

Single prints are interior thin time structure left by directional movement between accepted areas. Their location can remain a future auction reference. [TPO] pp.5–7; [MAMT] pp.18–20.

**Not a standalone trade.** An outer excess tail or any price with one observed trade is not automatically an interior single-print zone or a trade.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | TPO lettersets/as_of, source interior band and accepted distributions on both sides, source formation and repair policy. |
| Outputs / units | single_letter_rows, interior_band?, letter_ids, formation_known_at, repair_state?. |
| ET clock / interval | CurrentTPOas_of; later repair after formation. |
| Bars / event membership | Letter-aware TPO rows, not one-trade counts or price offsets. |
| Reset / persistence | Each source zone; later letter scan repair it in new snapshots. |
| known_at | Both neighboring distributions and interior structure must exist by observation. |

**Procedure:**

1. Measure each row's distinct period count. A count 1 row retains its actual letter.
2. For a source interior single-print band require a bounded thin connection between source accepted distributions; do not include merely outer excess tails. Missing distribution/zone criterion is a hole.
3. Append actual later letter/visit events under selected repair rule. Do not fabricate a band by fixed offset from POC or use final membership at morning entry.

**Printed constants and limits:** Single period membership; no automatic zone-length or repair threshold.

**Invalid / unavailable behavior:** Outer tail counted interior; missing letters; unrelated fixed offset; future distribution. Apply C04; emit `HOLE:O079:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O079-F1 — numeric fixture:** Synthetic rows 100:{A, B}, 101:{C}, 102:{C}, 103:{C, D} with supplied accepted areas at 100/103 yield interior one-letter rows 101–102, both letter C. Row 104:{D} beyond the upper accepted area is outer tail, not part of that interior band. Later D at 101 changes count to 2 only after its arrival.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.tpo_trade_visited](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); family_gap; the previous formula labels R-A14/A18. True interior letter-aware bands and an unfinished-reference ledger are partial. Existing behavior is not authority over this procedure.


<a id="o080"></a>

## O080 — TPO excess at auction extremes

**Wiki:** [TPO excess at auction extremes](/workspace/planning/phase-1-live/wiki/excess.md). **Implementation mode:** source extreme-tail letter geometry.

Excess describes the taper/rejection structure at an auction extreme in the time profile, helping assess completion. It differs from an interior single-print region and a poor extreme. [TPO] pp.5–7.

**Not a standalone trade.** Excess is evidence about an auction boundary, not a complete fade or confirmation that an extreme cannot be revisited.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | TPO profile/as_of, high/low side, row grid and lettersets, source criterion and instrument. |
| Outputs / units | extreme_tail_rows, tail_length_rows, same_letter_tail, source_excess?. |
| ET clock / interval | As-of TPO state ET; eventual completed profile is separate. |
| Bars / event membership | Source TPO letter rows. The lesson describes 2 or more same-letter rows at an extreme; source grid must be compatible. |
| Reset / persistence | Each profile snapshot/side; classify high and low separately. |
| known_at | When the observed tail and source conditions exist; not known at first touch from final profile. |

**Procedure:**

1. Starting at the chosen extreme, enumerate consecutive outer rows with one period each and retain whether they share the same letter.
2. Under the cited two-or-more same letter criterion, requiretail_length≥2 and same letter true; attach source grid/instrument. If the exact source grid or required criterion is unresolved, preserve geometry and mark faithful label unknown.
3. Keep this outer tail out of interior single prints. Excess does not guarantee no revisit.

**Printed constants and limits:** At least 2 same-letter extreme rows in TPO lesson p 6; no arbitrary tick tail ratio.

**Invalid / unavailable behavior:** All count 1 rows any where called excess; different letters merged; final profile backdated. Apply C04; emit `HOLE:O080:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O080-F1 — numeric fixture:** Synthetic upper rows 104:{D}, 103:{D}, 102:{B, D} givetail_length2, same letter true, excess under selected criterion true. If 103:{C}, two one-letter rows do not satisfy same letter tail. A matching low-sidecheck is independent.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap and TPO ingredients; the previous formula labels R-A14. Source-compatible tail/letter classification is partial. Existing behavior is not authority over this procedure.


<a id="o081"></a>

## O081 — TPO poor high and poor low

**Wiki:** [TPO poor high and poor low](/workspace/planning/phase-1-live/wiki/poor-extremes.md). **Implementation mode:** source instrument-specific incomplete extreme; definition hole where unresolved.

A poor extreme indicates incomplete auction structure under the selected TPO reading and can remain an unfinished reference. It is distinct from an excess extreme. [TPO] pp.5–7; [MAMT] pp.18–20.

**Not a standalone trade.** A poor-high flag is not a short trigger, and a poor low is not a long trigger. A label does not guarantee repair.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source TPO profile/letter grid, side, extreme period memberships and tail geometry, instrument-specific criterion, later repair history. |
| Outputs / units | poor_high?, poor_low?, criterion, extreme_price, repair_state?. |
| ET clock / interval | Currentprofileas_ofthenlaterrepairET. |
| Bars / event membership | Source letter TPO, not generic candle wick. |
| Reset / persistence | Per profile side; no OR merge of high and low. |
| known_at | Available tail membership/criterion at observation. |

**Procedure:**

1. Apply the actually selected source poor-extreme definition. The NQ discussion singles out a one-row tail; ES discussion is different and does not fully settle an automatic criterion. Do not impose one universal flag.
2. Store poor high and poor low independently; missing definition/coverage returns null. If using the source NQ one-row case, verify the source compatible grid and tail membership.
3. Track later repair using the unfinished-objective ledger; no guarantee or reversal entry follows.

**Printed constants and limits:** NQ source one-row tail case only; no universal ES/NQ criterion.

**Invalid / unavailable behavior:** poor_highORpoor_lowusedasboth; ES criterion guessed; final repair used early. Apply C04; emit `HOLE:O081:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O081-F1 — numeric fixture:** Synthetic verified NQ upper outer tail has one D row at 104, next row 103:{B, D}: tail_length1 is the selected source poor-high case. Low tail with 2 same A rows is excess under its criterion, not automatically poor low. With ES and no exact criterion, poor_high=null even for same geometry.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap; the previous formula labels R-A14/A18. The source's exact letter-aware criterion and persistent repair history are partial. Existing behavior is not authority over this procedure.


<a id="o082"></a>

## O082 — Initial balance

**Wiki:** [Initial balance](/workspace/planning/phase-1-live/wiki/initial-balance.md). **Implementation mode:** completed first-hour range and later descriptive extensions.

The initial balance is the early completed opening range used to read later range extension and day structure. Its eventual relationship to the whole day is descriptive context. [TPO] pp.3–9; [MAMT] pp.18–23.

**Not a standalone trade.** An IB statistic alone is not an entry edge or permission to trade before the initial interval has finished.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source RTH prices/TPOA+B, exact session date, complete coverage, later prices through source observation end. |
| Outputs / units | ibh, ibl, ibw, known_at, upper_extension, lower_extension, later_break_flags. |
| ET clock / interval | IB [09:30, 10:30)ET from A+B; subsequent descriptive path [10:30, 16:00)when source RTH end 16:00. |
| Bars / event membership | Complete clock bars or native events; include all of Aand B. |
| Reset / persistence | Each current RTHIB; prior IB has different date/ID. |
| known_at | 10:30 after full IB coverage; later extensions at actual event time. |

**Procedure:**

1. Compute IBH=max H, IBL=min L, IBW=IBH-IBL. Zero-width makes width normalization null.
2. Forlateras_ofcomputeupper_extension=max(0, later_high-IBH), lower_extension=max(0, IBL-later_low). Strict price beyond edge is break; exact touch separate.
3. Keep both/one/neither break and RTH close relation as later descriptive events, not initial entry permission. Any IB x 2 taxonomy needing an unsettled anchor stays a hole.

**Printed constants and limits:** First hour 09:30–10:30ET; source RTH end 16:00 for full-day description.

**Invalid / unavailable behavior:** Used before 10:30; prior IB substitution; final extension as early context; zero W division. Apply C04; emit `HOLE:O082:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O082-F1 — numeric fixture:** Synthetic A H110/L100, B H108/L99 =>IBH 110, IBL 99, W11 known 10:30. Later H112/L98 yields upper extension 2, lower 1, both broken=true. A 10:15 decision cannot use IBL 99 if its defining trade occurs 10:20.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap and clock/range ingredients; the previous formula labels R-A10/A14/A15. Later day-type classification remains an outcome. Existing behavior is not authority over this procedure.


<a id="o083"></a>

## O083 — Developing auction open type

**Wiki:** [Developing auction open type](/workspace/planning/phase-1-live/wiki/open-type.md). **Implementation mode:** developing source opening-path description; classifier holes.

The AMT lesson distinguishes open drive, open test-drive, open rejection-reverse and open auction by the behavior after the open. These guide continuation versus rotational expectations. [AMT1] pp.10–13.

**Not a standalone trade.** The opening type does not replace local confirmation. A final classification cannot be assigned before the behavior that defines it.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Actual cash open, complete elapsed path including first minute, source observation window and type criterion, test/rejection events. |
| Outputs / units | crossed_open_by_asof, source_open_type?, type_known_at, provisional/final flag. |
| ET clock / interval | Start 09:30ET; source-defined classification observation end, not invented 5/15/30 minutes. |
| Bars / event membership | Actual opening events/complete bars; no first minute skip. |
| Reset / persistence | Each RTH open; later classification versions append. |
| known_at | After the behavior needed by the selected type is observed. |

**Procedure:**

1. Record the path through/away from cash open over all elapsed data. For a source open-drive candidate record whether it crossed back through open; absence can only cover elapsed time.
2. Retain source open-drive, test-drive, rejection-reverse, open-auction labels and their actual evidence. Automatic duration/strength/acceptance thresholds missing=>holes.
3. Opening location versus prior VA is not open type; final day type is not open type.

**Printed constants and limits:** Four literal type names; no universal observation duration.

**Invalid / unavailable behavior:** First minute skipped; final no cross known at open; prior VA location used as drive classifier. Apply C04; emit `HOLE:O083:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O083-F1 — numeric fixture:** Synthetic open 100, 09:30:20 price 99, 09:32 price 102: a bullish no-through-open claim over that interval is false because 99 crossed below. Dropping the first minute would incorrectly pass. Ata 09:31 as-of, later 09:40 behavior is unavailable.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap; formulas_jumbo open-type helpers; the previous formula labels R-A10. Prior-VA location or skipping the first minute does not reproduce a no-through-open drive. Existing behavior is not authority over this procedure.


<a id="o084"></a>

## O084 — Developing auction day structure

**Wiki:** [Developing auction day structure](/workspace/planning/phase-1-live/wiki/day-type.md). **Implementation mode:** source-taxonomy state observation; no universal early classifier.

Sires discusses trend, normal, normal variation, neutral and nontrend behavior, with different permitted tactics. MAMT's IB-based day categories have another definition. Saint waits for a new balance in an unbalanced trending profile. [AMT1] pp.10–13; [MAMT] pp.18–20; [RTVP] p.9.

**Not a standalone trade.** A final-day label is not an entry-time filter, and distinct source taxonomies cannot be pooled into one directional switch.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author/taxonomy, as-of elapsed balance/IB/extensions, source provisional label, final descriptive label separately. |
| Outputs / units | provisional_type?, evidence_until, final_type?, permission_reference. |
| ET clock / interval | As-of current auction ET; final session label known only at its defining end. |
| Bars / event membership | Source profile/path/IB evidence; different taxonomies kept distinct. |
| Reset / persistence | Each source day/taxonomy; new impulse reread a pp ends state. |
| known_at | Maximum elapsed facts needed by each label. |

**Procedure:**

1. Preserve Sires lesson trend/normal/normal variation/neutral/nontrend and MAMT's distinct IB based categories; do not pool names into one classifier.
2. Record provisional state only when its required evidence exists. Missing quantitative category definition=>null automatic label.
3. Apply Saint's wait-for-new-balance permission within his own method; Sires established-trend continuation stays in his method.

**Printed constants and limits:** No universal day type classifier or lookahead permission.

**Invalid / unavailable behavior:** Final trend label used 09:30; taxonomies merged; Saint stand-down overridden. Apply C04; emit `HOLE:O084:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O084-F1 — numeric fixture:** Synthetic provisional balance at 10:00 and final trend label at 16:00 are two observations. The 16:00 label cannot pass a 10:15 trend context gate. A complete IB extension of 2 points is recordable without inventing a Trend Day label.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_gap; the previous formula labels R-A10/A11/A15. Generic daily labels do not implement source-specific evolving permissions. Existing behavior is not authority over this procedure.


<a id="o085"></a>

## O085 — Profile shape and trade permission

**Wiki:** [Profile shape and trade permission](/workspace/planning/phase-1-live/wiki/profile-shape.md). **Implementation mode:** source shape and author-specific permission; detector/direction holes.

Balanced, double-distribution, trending and P/b shapes describe where the auction has accepted trade. Saint's P/b examples form a balance after an impulse and then require break/retest. Sires's MAMT P/b captions and drawings do not prescribe a consistent universal direction. [RTVP] pp.6–11; [MAMT] pp.6–8.

**Not a standalone trade.** Buy every P or sell every b is not a sourced rule. A double distribution requires reading both shelves and the connection.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author, source profile/as_of, selected shape definition, accepted sub balances/connecting LVN, stated permission. |
| Outputs / units | source_shape?, subbalance_ids, source_permission?, automatic_shape_direction=null. |
| ET clock / interval | Actual profile as-of before branch choice. |
| Bars / event membership | Source profile geometry; not final histogram at earlier decision. |
| Reset / persistence | Each profile/permission version after impulse. |
| known_at | Source evidence/permission availability. |

**Procedure:**

1. Preserve literal balanced/double-distribution/trending/P/b reading with source evidence; accepted sub balances and bridge are distinct objects.
2. Saint's P/b cases require balance after impulse then break/retest; his unbalanced trend requires rebalance. Sires MAMTP/b caption/drawing direction conflict remains unresolved.
3. No universal buy P/sell b, shape classifier or standalone entry is in this pack.

**Printed constants and limits:** No automatic shape threshold or P/b direction table.

**Invalid / unavailable behavior:** P/b direction invented; second hump/LVN ignored; cross-author permission. Apply C04; emit `HOLE:O085:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O085-F1 — numeric fixture:** Synthetic Saint source P shape with balance [100, 105] is context only; no break/retest means no entry pass. A Sires P caption and drawing with opposite directions yields direction=null, not an optimized choice.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Profile helpers and the previous formula labels R-A11/A17. An automatic universal shape-to-direction mapping is missing and unsupported. Existing behavior is not authority over this procedure.


<a id="o086"></a>

## O086 — Prior-session auction landmarks

**Wiki:** [Prior-session auction landmarks](/workspace/planning/phase-1-live/wiki/prior-session-reference-levels.md). **Implementation mode:** typed prior landmark registry and literal geometry.

Known prior highs/lows, opens/closes, IB references and profile landmarks supply context or destinations. MAMT's appendix describes separately conditioned reference-hit statistics; Jumbo and Green Bird choose the reference relevant to their case. [MAMT] pp.15–26; [TBR] pp.16–24, 32–35; [GB] pp.25, 30–39.

**Not a standalone trade.** A landmark hit rate is not the win rate of a trade targeting it. Close-based and range-edge-based gap references are different constructions.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Reference kind, exact source period/date/window, verified price/band, prior IB/VA/POC/MPOC parent, opening condition and availability. |
| Outputs / units | reference_id, kind, price_or_band, known_at, opening_relation, selected_role. |
| ET clock / interval | Prior landmark formed before current use; exact RTH/ETH relationship retained. |
| Bars / event membership | Each parent's own bar/profile procedure. |
| Reset / persistence | Each dated reference; active retirement under selected method policy. |
| known_at | Parent completion/availability; current opening relation at later actual open. |

**Procedure:**

1. Use each parent recipe and preserve kind/period identity:prior open/close, H/L, IB edges, VA edges, POC, MPOC.
2. For a source half-gap of p HOD with open above prior high, use(open+p HOD)/2; for open below p LOD use(open+p LOD)/2. This is not(open+prior close)/2.
3. Keep a reference's later hit separate from entry and its conditioned claim denominator.

**Printed constants and limits:** Half-gap 0.5 for explicitly named range-edge gap; no automatic closest-target rule.

**Invalid / unavailable behavior:** RTH/ETH alias; POC midpoint alias; close-gap geometry substituted. Apply C04; emit `HOLE:O086:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O086-F1 — numeric fixture:** Synthetic prior session high = 110, prior close = 105, current open = 114 gives half-session-gap = (114 + 110)/2 = 112 and half-close-gap = (114 + 105)/2 = 109.5. A price of 112 touches the first reference; it does not establish a fill to the prior close at 105.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_levels; family_open; the previous formula labels R-A13/A15/A18, R-J06/J10/J19, R-G05–G09. Complete source-scoped reference/visit ledgers are partial. Existing behavior is not authority over this procedure.


<a id="o087"></a>

## O087 — Remaining auction objectives

**Wiki:** [Remaining auction objectives](/workspace/planning/phase-1-live/wiki/unfinished-business.md). **Implementation mode:** persistent source-scoped objective state machine.

An untouched or still-relevant prior/session extreme, POC, poor extreme, single-print area or other source reference can remain a destination. The source method determines when that objective is consumed. [TBR] pp.11–15, 32–35; [JR] pp.23–26, 33–39; [AMT1] pp.12–13; [TPO] pp.5–9; [GB] pp.30–39.

**Not a standalone trade.** The nearest level is not automatically the remaining draw. A later hit cannot choose the pre-entry target, and all methods do not share one purge rule.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Preselected objective ID/type/bounds, original known_at, source eligible visits/consumption rule, ordered covered history, decision priority. |
| Outputs / units | active_at_decision?, first_consumption_at?, priority_at_decision, subsequent_outcome. |
| ET clock / interval | Original reference formation through current decision; visits count only in source RTH/ETH/session policy. |
| Bars / event membership | Native prices/complete bars and letter repair records as the object requires. |
| Reset / persistence | New objective identity; state changes append. Method-specific reset only. |
| known_at | At decision only prior qualifying visits; future outcome separate. |

**Procedure:**

1. Register objective as available after formation. Store its active/consumed state under the specific visit/repair rule; missing rule or history=>unknown.
2. For Jumbo RTH-only targets log ETH visits without retirement. For purged-overnight branch retain actual earlier sweeps under that branch's rule.
3. Freeze objective priority before entry; never choose closest/best later hit unless source explicitly prescribes that selector.
4. C06 measures subsequent first events; a POC, poor-extreme or interior print needs its own source consumption definition.

**Printed constants and limits:** No universal purge, repair percentage or priority distance.

**Invalid / unavailable behavior:** ETH retirement of RTH-only reference; future hit selects target; fabricated print offset; missing coverage as untouched. Apply C04; emit `HOLE:O087:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O087-F1 — numeric fixture:** Synthetic RTH-only objective 120 known yesterday 16:00, ETH hit 02:00, RTH entry 09:40: active=true if no qualifying RTH visit. RTH hit 10:00 consumes after entry. Another method whose policy counts ETH would have active=false at 09:40; do not share the flags.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_levels; [formulas_jumbo.j10_draw/j19_draw](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-J10/J19, R-A18 and R-G01–G09. A persistent source-scoped objective ledger is missing. Existing behavior is not authority over this procedure.


<a id="o088"></a>

## O088 — Source-conditioned reference statistics

**Wiki:** [Source-conditioned reference statistics](/workspace/planning/phase-1-live/wiki/reference-statistics.md). **Implementation mode:** source-claim registry plus separately scoped nonfinancial reference observations.

The sources present path and landmark statistics with particular windows and conditions. MAMT explicitly says the 94% either-overnight-edge and 73% MPOC claims are context after HTF understanding, not an edge by themselves. Its appendix is a separately scoped historical ES sample. [MAMT] pp.15–26; [TBR] p.30; [JR] pp.48–49.

**Not a standalone trade.** Either is not both; a reference hit is not a method win. A printed percentage with an unresolved definition cannot justify an unconditional trade probability.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Claim ID/citation, literal percentage, instrument/contract, date/sample_n, eligibility, event/window/side, denominator basis, unresolved definitions; separate observed cohort. |
| Outputs / units | source_claim, claim_definition_complete, observed_hit_counts?, observed_rate?, comparability_holes[]. |
| ET clock / interval | Claim's own formation/observation windows; statistic available only after its measured sample. It cannot provide earlier candidate context unless already known. |
| Bars / event membership | Reference-specific prices/profiles; never trade P&L. |
| Reset / persistence | Each claim definition/version/instrument/cohort; do not pool unlike claims. |
| known_at | Claim publication for context; measured observation at window end. |

**Procedure:**

1. Register 94% either ONH-or-ONL, current-session touch; not both and not 94% chance of one specific edge. Register 73% MPOC conditional on RTH open inside previous ETH balance; retain balance/VA/scope conflict.
2. Keep MAMT appendix ES 2021–2024, 1040 days/260 per quarter-code ESH/ESM/ESU/ESZ separate from NQ and from unscoped lesson claims. Literal appendix clock is 06:30–13:00PST, IB 06:30–07:30PST; exact DST interpretation/sample membership must be verified before claiming reproduction.
3. Measure each fully defined event/cohort by C06/C07 separately from method sequence. A conditional heading does not settle whether printed percentages use all-session or condition-eligible denominators; preserve unresolved denominator.
4. Missing event definition or cohort means claim stored and automatic replication unknown. Never reverse-engineer integer hits from rounded percentages, renormalize incomplete taxonomy tables, or call reference hit rate a trade win rate.

**Printed constants and limits:** 94%, 73%, 1040, 260, 2021–2024 are source claims/sample metadata; other printed appendix values remain literal claim records, not method thresholds.

**Invalid / unavailable behavior:** Either→both; ES→NQ; conditional denominator guessed; rounded percent reverse-engineered; reference hit called entry edge. Apply C04; emit `HOLE:O088:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O088-F1 — numeric fixture:** Synthetic 10 identified sessions with ONH hit 6, ONL hit 5, both 3 give either=6+5-3=8, either rate 0.8, both rate 0.3. They are not 0.94 and not interchangeable. A supplied ETH H120/L100 gives MPOC 110, never volume POC 114; unresolved open condition prevents 73% replication.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** stats/report; the previous formula labels R-J06/J07, R-A13/A15/A18. Old component rates and retrospective labels do not certify the operating method. Existing behavior is not authority over this procedure.


<a id="o089"></a>

## O089 — Saint's Asia-range target context

**Wiki:** [Saint's Asia-range target context](/workspace/planning/phase-1-live/wiki/asia-range-risk-context.md). **Implementation mode:** Saint source target-ambition record; range/target selector hole.

The trapped-buyer example keeps its target within a realistic Asia-session range distance and uses normal risk after the confirmed retest. This is the source case's target-ambition context. [TRAP] pp.8–10.

**Not a standalone trade.** It is not Sires's 18:00–09:30 overnight-inventory framework, a fixed numerical target, or an independent Asia-box entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Saint source Asia session identity/clock, observed or anticipated range reference actually used, entry/structural stop, target and pre-decision rationale. |
| Outputs / units | source_range_reference, target_distance, stop_distance, source_ambition_ok?, automatic_target=null. |
| ET clock / interval | Actual cited Asia source case; no 18:00–09:30 inventory clock inherited. |
| Bars / event membership | Source compatible Asia range/ticket record; not generic overnight profile. |
| Reset / persistence | Per source case/rationale version. |
| known_at | Range reference and risk rationale before decision; later realized range is outcome only. |

**Procedure:**

1. Retain the source case's realistic range-distance explanation and normal risk after confirmed retest.
2. Compute literal entry-to-target and entry-to-stop distances in native price units; source adequacy judgment remains provided/unknown without an exact rule.
3. Do not invent clock, range percentage or fixed point target from one example.

**Printed constants and limits:** No published universal Asia clock or percentage/point target.

**Invalid / unavailable behavior:** Sires overnight context substituted; future Asia range; one example becomes fixed target. Apply C04; emit `HOLE:O089:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O089-F1 — numeric fixture:** Synthetic short entry 110, stop 112, target 105 gives stop distance 2, target distance 5. A supplied Asia range reference 8 points is retained, but 5/8=0.625 does not become a universal 62.5% target rule; ambition classification needs its source rationale.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Clock/range and ticket-distance ingredients; the previous formula labels R-F13 has related entry context. Source-exact Asia-range target selection and management are missing. Existing behavior is not authority over this procedure.


<a id="o090"></a>

## O090 — Rotation within accepted balance

**Wiki:** [Rotation within accepted balance](/workspace/planning/phase-1-live/wiki/balance-rotation.md). **Implementation mode:** ordered source route; acceptance and local confirmation definitions required.

An established balance permits a responsive read at a real outer edge, followed by the chosen confirmation and travel toward POC/fair value. Reassess at POC before presuming the far side. [AMT1] pp.7–10; [VP2] pp.3–8; [RTVP] pp.5–8.

**Not a standalone trade.** This is an auction route inside the parent loop. A prior-VA edge touch without current balance and confirmation is not a complete fade.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Established balance ID and bounds, actual outer edge, contemporaneous balance evidence, selected local confirmation, preselected POC/fair-value target and later reread. |
| Outputs / units | edge_arrival_at, local_confirm_at, rotation_sequence?, first_fair_value_event, poc_reread?, later_far_side_objective?. |
| ET clock / interval | Balance available before arrival; source action interval in ET. No full-morning inside flag at the opening decision. |
| Bars / event membership | Selected parent's execution bars/events and fixed or developing profile snapshot as specified. |
| Reset / persistence | Per balance/edge/side/attempt; a later far-side leg is separately selected after the POC read. |
| known_at | Each stage at its actual observation; initial objective before entry and later objective before its own action. |

**Procedure:**

1. Require source-defined current balance and actual contact at its real outer edge. A prior VA line is insufficient if the current auction is no longer balanced.
2. Apply the local confirmation branch required by that author and case. Join on the same balance, edge, side and candidate.
3. Check balance_known_at≤arrival_at<confirmation_at≤decision_at, then observe travel toward the preselected POC/fair value under C06.
4. At POC create a new failure/passage observation. Do not presume the far side or use its later reach to label initial control.

**Printed constants and limits:** No universal edge tolerance, hold duration or far-side target.

**Invalid / unavailable behavior:** Final-morning inside status used early; bare edge touch counted entry; author confirmation borrowed; POC skipped in target progression. Apply C04; emit `HOLE:O090:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O090-F1 — numeric fixture:** Synthetic balance [100, 110], POC 106 known 09:20; low-edge contact 100 at 09:40, supplied source confirmation 09:42, decision 09:43 and later POC 106 at 10:00 preserve the route. Far edge 110 reached 10:20 is a separate outcome; it cannot replace the missing 09:42 confirmation.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.a01_fade/a05_poc_tell/a16_stacked](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A01/A05/A16. A full-morning inside flag and a bare edge predicate do not supply the route. Existing behavior is not authority over this procedure.


<a id="o091"></a>

## O091 — Accepted break and defended boundary retest

**Wiki:** [Accepted break and defended boundary retest](/workspace/planning/phase-1-live/wiki/break-retest.md). **Implementation mode:** same-reference break, acceptance, return and defense sequence.

The auction leaves balance or a ledge with participation and acceptance, then returns to that same broken boundary. Defense and renewed initiative can confirm continuation. Saint additionally requires the lower-timeframe control to agree with his HTF read; Keani's own retest is of the buying-imbalance band after the VAH break. [AMT1] pp.8–9; [MAMT] p.12; [WIC] pp.7–10; [TRAP] pp.6–9; [AVG] pp.21–22.

**Not a standalone trade.** A break, retest and confirmation from unrelated times or boundaries do not compose a trade. Do not make every source use the same hold duration.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Known balance/ledge/developing-VAH ID, direction, source breakout/acceptance evidence, departure and actual retest-band ID, fresh defense/initiative evidence, decision. |
| Outputs / units | break_at, accept_at, depart_at, retest_at, defense_at, initiative_at, break_retest_sequence?. |
| ET clock / interval | Boundary known before break; break before retest; selected source timeframe and ET action interval. |
| Bars / event membership | Complete source execution bars or ordered events; source hold duration is not universal. |
| Reset / persistence | Each source boundary and breakout attempt. A changed boundary needs a new source identity, not a nearest-price join. |
| known_at | Every confirmation after its final necessary event; no close-at-start timestamps. |

**Procedure:**

1. Validate the literal break direction against the frozen boundary. Acceptance beyond it needs the source's stated procedure or supplied observation; crossing alone cannot fill acceptance.
2. Require a documented departure and later return to the same broken structure. Preserve an explicit parent-to-retest-band relationship when the source uses a sub-band.
3. Require the chosen local defense/renewed initiative at that retest before entry. Saint adds current HTF/LTF agreement; Keani retests his post-VAH-break buying-imbalance band, not an arbitrary VAH touch.
4. Use boundary_known_at<break_at<retest_at≤confirmation_at≤decision_at. If the retest is missed, mark that failed prerequisite for an identified chased attempt; do not invent a chase branch.

**Printed constants and limits:** No fixed retest interval, distance or acceptance duration.

**Invalid / unavailable behavior:** Unrelated break and retest; boundary reselected later; no departure; anticipated defense; mandatory common hold timer invented. Apply C04; emit `HOLE:O091:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O091-F1 — numeric fixture:** Synthetic ledge 110 known 09:30, break 111 at 09:40, departure 112 at 09:41, retest 110 at 09:45, source defense 09:46 and entry 09:47 pass the literal order when acceptance and branch gates are supplied. Entry 09:44 lacks the required later retest and fails. Retest 109 on another band cannot be joined to ledge 110 by date alone.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.a02_ledge_retest_hold/a07_break_retest](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_s09_open_above_value](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-A02/A07/R-S09. Side-specific event joins and source bands are partial. Existing behavior is not authority over this procedure.


<a id="o092"></a>

## O092 — Re-acceptance into value

**Wiki:** [Re-acceptance into value](/workspace/planning/phase-1-live/wiki/value-reacceptance.md). **Implementation mode:** original-area re-entry plus source-specific acceptance.

When price leaves or opens outside accepted value and then re-enters with acceptance, the directional read can rotate toward another part of that balance. Two-period-inside and general re-entry claims have separate definitions. [AMT1] p.7; [MAMT] pp.12, 18; [AMTL] pp.8–11.

**Not a standalone trade.** One wick inside value does not prove acceptance or an 80% traversal trade. A compiler's 30-minute hold is not a universal source rule.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Original VA/balance ID with both bounds, departure/open-outside side, return events, selected acceptance definition and completed observations, current control and objective. |
| Outputs / units | outside_before, return_at, inside_observations, acceptance_at, reacceptance_sequence?, next_objective_id. |
| ET clock / interval | Original area before departure/open; actual return then complete source acceptance in ET. |
| Bars / event membership | General acceptance uses its source evidence. The separately quoted two-consecutive-30-minute-period rule has its own cohort and exact inside convention, not a global 30-minute hold. |
| Reset / persistence | Per original area/departure episode; leaving again is retained in the path. |
| known_at | Acceptance at the end of its required observations; both boundaries already known. |

**Procedure:**

1. Establish original area and outside origin. Compare inside location with both VAL and VAH, preserving boundary cases under the source's convention.
2. Require actual return followed by the selected acceptance. If a source says two consecutive 30-minute periods inside, preserve that distinct rule and wait for both completed periods; whether entire ranges or another criterion count as inside must be source-defined.
3. A wick inside or one-boundary inequality does not establish acceptance. An unspecified acceptance detector is a hole.
4. Keep POC progression, whole-value traversal and their reference statistics separate; do not attach a generic 80% win probability.

**Printed constants and limits:** Two consecutive 30-minute periods belong only to the narrower quoted reference claim. No universal 30-minute hold or maximum traversal duration.

**Invalid / unavailable behavior:** Price above VAL but above VAH counted inside; final traversal used to confirm re-entry; distinct claims pooled. Apply C04; emit `HOLE:O092:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O092-F1 — numeric fixture:** Synthetic original VA [100, 110], prior price 112, return 108: literal location is inside. A later price 111 is outside despite 111≥VAL. Under an explicitly supplied whole-period-inside test, periods with ranges [102, 109] and [101, 108] satisfy both bounds after the second closes; replacing the second high with 111 fails that supplied test. Without that exact source inside convention, automatic acceptance remains null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.a03_reentry_traverse/a08_reaccept](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A03/A04/A08. Testing only one value boundary can wrongly count excursions outside the other side as inside. Existing behavior is not authority over this procedure.


<a id="o093"></a>

## O093 — Sires's narrower Failed Auction setup

**Wiki:** [Sires's narrower Failed Auction setup](/workspace/planning/phase-1-live/wiki/failed-auction-sires.md). **Implementation mode:** two-balance, older-POC tag and rejection route.

Established balance → break out → actually tag an older, separate balance's POC → instant rejection → return toward the specified boundary of the established balance. The source says rejection from above the older POC targets established VAH, and rejection from below targets established VAL; the diagram fixes the two balance identities. [MAMT] pp.9–11.

**Not a standalone trade.** A generic return to a gray zone is not this setup. The source's negative chart breaks/retests in continuation without tagging and rejecting an older POC.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Established balance ID/VAH/VAL, a distinct older profile ID/POC, both available times, breakout, actual older-POC tag, source instant rejection evidence, decision and target. |
| Outputs / units | distinct_balances, break_at, older_poc_tag_at, reject_at, fa_sequence?, source_target_id/price. |
| ET clock / interval | Established/older structures known before breakout; break<tag<rejection≤decision in ET. |
| Bars / event membership | Source price/order-flow observations; instant rejection has no invented universal seconds limit. |
| Reset / persistence | Per established-balance departure and older-POC test. |
| known_at | Each event's actual availability; older POC must be confirmed before the attempt, never today's final POC. |

**Procedure:**

1. Require two distinct profile identities. Verify an actual departure from the established balance and actual contact with the older external POC.
2. Require source instant rejection at that POC, not acceptance or a continuation break/retest. Missing exact rejection detector is a source hole unless the episode supplies the observation.
3. Bind target exactly as the source states: rejection from above the older POC → established VAH; rejection from below → established VAL. Preserve the approach/rejection-side label; do not choose nearest/farthest boundary by a replacement heuristic.
4. The printed 80% statement stays an unverified source claim; the method predicate is the ordered route, not that number.

**Printed constants and limits:** No numerical instant-rejection timer. Source 80% is not a new measured rate.

**Invalid / unavailable behavior:** Established POC reused as older POC; no tag; continuation accepted as rejection; target boundary swapped; old final-day POC leak. Apply C04; emit `HOLE:O093:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O093-F1 — numeric fixture:** Synthetic established balance VA [100, 110], distinct older POC 115, both known 09:20; breakout 09:40, actual tag 115 at 09:45, supplied rejection-from-above 09:46, decision 09:47 binds target 110. No tag while price only reaches 114 makes this route false with complete evidence. Replacing older profile ID with established ID fails distinctness.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.a06_failed_auction](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A06. The current caller's POC identity and the helper's target do not reproduce the full source geometry. Existing behavior is not authority over this procedure.


<a id="o094"></a>

## O094 — Saint's failed auction and return to value

**Wiki:** [Saint's failed auction and return to value](/workspace/planning/phase-1-live/wiki/failed-auction-saint.md). **Implementation mode:** exploration failure, original-value reacceptance and renewed control.

Saint reads attempted acceptance in lower/older value, its failure, return into the original balance, and renewed POC/control evidence. The live sequence can dip deeply and take time to confirm. [AMTL] pp.8–12.

**Not a standalone trade.** This is Saint's route within HTF/LTF alignment. Sires's instant rejection at an older POC is not mandatory for every Saint example.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Saint original balance/value ID, tested lower/older value ID, exploration/attempted acceptance, failure, original-area reacceptance, current POC/control read, decision/objective. |
| Outputs / units | explore_at, failure_at, return_at, reaccept_at, control_at, saint_fa_sequence?. |
| ET clock / interval | Original structures known before exploration; subsequent source events ordered in ET without an invented maximum delay. |
| Bars / event membership | Actual source HTF/LTF profile and execution evidence; no borrowed Sires instant-POC rule. |
| Reset / persistence | Per original-balance exploration/return episode. |
| known_at | Each renewed control/reacceptance observation only after it occurs. |

**Procedure:**

1. Preserve both original and tested value identities. Record attempted acceptance away from the original balance and the evidence that it failed.
2. Require actual return and acceptance back in the original balance; a deep temporary excursion does not automatically invalidate a source case that later completes this sequence.
3. Require the current POC/control confirmation and HTF/LTF alignment before entry. An earlier failed attempt cannot stand in for present control.
4. Sires's distinct older-POC tag and instant rejection are not extra universal requirements here.

**Printed constants and limits:** No fixed maximum excursion, time cap or universal older-POC requirement.

**Invalid / unavailable behavior:** Only a return wick; old control reused; source definitions merged across authors; missing original identity. Apply C04; emit `HOLE:O094:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O094-F1 — numeric fixture:** Synthetic original balance [100, 110], tested lower value [90, 98]; exploration 95 at 09:40, source failure 09:50, return 102 at 10:00, reacceptance 10:05, renewed long control 10:07 and decision 10:08 preserve the source route. The long cannot pass at 09:55 before return/control, even if price eventually 110.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.a08_reaccept/a05_poc_tell](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) and profile ingredients; the previous formula labels R-A03/A05/A08. The complete Saint event sequence is missing. Existing behavior is not authority over this procedure.


<a id="o095"></a>

## O095 — POC failure versus efficient passage

**Wiki:** [POC failure versus efficient passage](/workspace/planning/phase-1-live/wiki/poc-traversal.md). **Implementation mode:** source POC test/passage state and target progression.

Repeated failure to cross and hold POC favors rotational chop. Efficient passage, with the held retest where the source shows it, supports travel toward the other accepted area or far edge. [AMTL] pp.8–11; [RTVP] pp.5–8; [MAMT] p.12.

**Not a standalone trade.** A POC touch or a candle merely beyond it does not by itself establish control or far-side continuation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Known profile/POC, prior reacceptance or rotation context, distinct test events, side/effort, source efficient-passage and held-retest observations, preselected next objective. |
| Outputs / units | test_ids[], failed_test_count, passage_at?, held_retest_at?, current_poc_read?, next_objective_id. |
| ET clock / interval | Current POC behavior observed before later target decisions in ET. |
| Bars / event membership | Source local bars/flow; completed confirming observations only. |
| Reset / persistence | Per profile POC and current test episode; repeated rows within one test stay one test. |
| known_at | At the observed failure or completed source passage/retest. |

**Procedure:**

1. Record distinct attempts to cross and hold the actual POC. Repeated source failures support the supplied rotational-chop read; no numeric count threshold is published.
2. For efficient passage require the source effort/control observation and held retest where that example shows it. A candle merely beyond POC is not enough.
3. Freeze the next accepted-area/far-edge objective after the read and before the next action. Its later hit cannot determine what the earlier read was.

**Printed constants and limits:** No universal failure count, speed, volume ratio or hold duration.

**Invalid / unavailable behavior:** Final far-edge hit labels earlier passage; one close automatically efficient; duplicate rows as repeated tests. Apply C04; emit `HOLE:O095:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O095-F1 — numeric fixture:** Synthetic POC 105 tested at 09:40 and 09:45 with two supplied failed-cross records gives failed_test_count2. Later source passage 09:50 and held retest 09:52 are new evidence; a 09:51 continuation requiring that retest cannot use it. Far edge 110 remains a separate outcome.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.a05_poc_tell/a03_reentry_traverse](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A03/A05/A08. Entry-conditioned progression and source control evidence are partial. Existing behavior is not authority over this procedure.


<a id="o096"></a>

## O096 — Whole-balance traversal with one side in control

**Wiki:** [Whole-balance traversal with one side in control](/workspace/planning/phase-1-live/wiki/balance-traversal.md). **Implementation mode:** whole-area path then source no-hold/control and later retest.

Price traverses a whole established balance without holding; later retests can then be read with the controlling side until contradicted. This is one route in the broader auction loop. [MAMT] p.12.

**Not a standalone trade.** A fast move or the eventual side of the session is not enough. The source does not prescribe the compiler's universal maximum traversal duration.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen balance bounds, entry/exit-side events, complete traversing path, source internal-hold criterion/evidence, later same-structure retest and controlling side. |
| Outputs / units | traverse_start, traverse_end, traverse_duration, whole_balance_crossed, no_source_hold?, retest_at, control_at, route_sequence?. |
| ET clock / interval | Actual elapsed traversal and later retest ET; no universal 30-minute maximum. |
| Bars / event membership | Covered ordered price path plus source-defined hold/control evidence. |
| Reset / persistence | Per frozen balance and traversal direction. |
| known_at | Whole traversal only at exit-side event; no-hold assessment after its entire required path. |

**Procedure:**

1. For an upward path require ordered travel from the lower boundary to the upper boundary of the same balance; downward is the source-selected reverse. Store actual duration without turning it into a new cutoff.
2. Determine absence of holding only under a complete source hold definition and full path coverage; otherwise no_hold=null.
3. Require later retest and present controlling-side evidence before an entry under this route. Whole-AM extrema or final close cannot supply event order.

**Printed constants and limits:** No maximum traversal time or automatic hold detector.

**Invalid / unavailable behavior:** Final extrema as ordered traverse; fixed time cap borrowed from helper; unknown hold treated absent. Apply C04; emit `HOLE:O096:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O096-F1 — numeric fixture:** Synthetic balance [100, 110], lower-bound event 10:00 and upper-bound event 10:40 give whole upward traversal and duration 40 minutes. It is not rejected merely for exceeding 30 minutes. No source hold definition =>no_hold=null; later retest 10:45/control 10:46 cannot authorize 10:42 entry.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.a09_traverse_nohold](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-A09. The helper's fixed time limits are measurement variants, not the full source rule. Existing behavior is not authority over this procedure.


<a id="o097"></a>

## O097 — Higher- and lower-timeframe control alignment

**Wiki:** [Higher- and lower-timeframe control alignment](/workspace/planning/phase-1-live/wiki/htf-ltf-alignment.md). **Implementation mode:** source thesis and current local control alignment.

The larger auction frames the direction/reaction and objective; the lower timeframe must show present control at the relevant area. Saint calls this the whole alignment method and waits through free two-sided chop. Sires's several confirmations can express one HTF thesis. [WIC] pp.7–10; [TRAP] pp.5–9; [CONT] pp.4–12; [K10] pp.5–8; [AVG] pp.21–22.

**Not a standalone trade.** HTF bias alone is not an entry, and an LTF print cannot erase an invalidated larger thesis. Sharing alignment does not merge these authors' methods.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author, HTF thesis/balance ID/side/validity, current LTF source timeframe/structure, same-area test/retest, control evidence and confirmation keys. |
| Outputs / units | htf_side, ltf_side, thesis_alive?, same_area, alignment_ok?, confirm_at. |
| ET clock / interval | HTF thesis known before local setup; current LTF control before decision ET. |
| Bars / event membership | Actual source HTF and LTF construction; no universal timeframe pair or classifier. |
| Reset / persistence | Each thesis version and new local decision; later supported flips create a new record. |
| known_at | Maximum live thesis and fresh LTF control availability. |

**Procedure:**

1. Validate the still-live HTF objective/validity band and the actual area in which the local event occurs.
2. For a directional aligned entry require source HTF permission and current LTF control supporting that side. Free two-sided chop does not supply one-sided control.
3. A local print cannot revive a dead larger thesis. A later flip may revise the read only after its evidence exists; preserve author's method identity.

**Printed constants and limits:** No universal timeframe, control-volume ratio or alignment score.

**Invalid / unavailable behavior:** Old failed test as present control; dead thesis ignored; unrelated area; hindsight flip. Apply C04; emit `HOLE:O097:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O097-F1 — numeric fixture:** Synthetic live HTF long thesis known 09:20, current LTF short control 09:40 =>directional alignment false for long. Fresh source long control 09:45 can align a 09:46 decision; it is unavailable to 09:42. If the thesis died 09:44, that later local long alone cannot pass.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Profile and flow ingredients; the previous formula labels R-A07/A08, R-F13 and R-S01–S09. A stable HTF → LTF → same-band event join is missing. Existing behavior is not authority over this procedure.


<a id="o098"></a>

## O098 — Executed aggressor-side trades

**Wiki:** [Executed aggressor-side trades](/workspace/planning/phase-1-live/wiki/aggressor-trades.md). **Implementation mode:** exact native executed-event adapter.

An executed trade identifies participation actually consuming liquidity; its aggressor side, size and price must be preserved. The sources compare effort with price response and distinguish executed orders from resting display. [DOM5] pp.3–7; [FP8] pp.3–7; [MATH] pp.4–8.

**Not a standalone trade.** A large buy print is not automatically bullish reward, absorption or an entry. Price upticks are not a substitute for known trade-side delta.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | C03 native trade/MBP-1 fields, instrument definition, event identity/order, side provenance and optional verified quote association. |
| Outputs / units | executed_size, aggressor:buy/sell/unknown, signed_known_size, unknown_size, price, event_key, ordering_quality. |
| ET clock / interval | UTC event nanoseconds converted to source ET only for session selection. Preserve tied timestamps. |
| Bars / event membership | Native execution events; later bars aggregate these events without inventing order. |
| Reset / persistence | No reset for the immutable event; every downstream accumulator defines its own source reset. |
| known_at | Actual event availability; source price time is not a later bar close when the raw event exists. |

**Procedure:**

1. From MBP-1 select action T; from a trade schema use every valid trade row. Decode B=buy,+size; A=sell,-size; N=unknown with unknown_size=size. Retain native price and contract units.
2. Do not infer unknown side from uptick/down tick or BBO when that source association is not verified. The supplied side is authoritative for these retained Databento trades.
3. Preserve physical event identity and one canonical tape. Aggregate tied events commutatively; a strict sequence within an unresolved timestamp tie is unknown.
4. Validate positive execution size and native price/tick compatibility. Missing or corrupt fields create data holes rather than directional trades.

**Printed constants and limits:** No aggression threshold; B/A/N semantics are the verified data adapter, not a strategy choice.

**Invalid / unavailable behavior:** Reversed A/B; unknown side forced directional; quote update counted as trade; duplicated MBP/standalone tapes; NQ/MNQ identity lost. Apply C04; emit `HOLE:O098:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O098-F1 — numeric fixture:** Raw C03-F1 has buy 7, sell 4, total 11, delta+3. Synthetic extra unknown trade size 2 increases total to 13 while exact signed delta becomes unresolved in [+1,+5]. An ask-side quote update size 100 adds zero executed volume.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** mbp1_extract; [mbp1_objects.cvd_from_trades/footprint_4x](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); the previous formula labels P3-04/P3-08 and R-F02/F04/F06. Source-compatible event joins are partial. Existing behavior is not authority over this procedure.


<a id="o099"></a>

## O099 — Big Trades aggression markers

**Wiki:** [Big Trades aggression markers](/workspace/planning/phase-1-live/wiki/big-trades.md). **Implementation mode:** source-configured executed-size display; aggregation semantics required.

Jumbo explicitly says his bubbles are Big Trades, not absorption, and names NQ 100 during New York / 75 during London. Sires's Big Trades material uses NQ 30–60 settings with a 40-range chart. The Refill study's mixed NQ/MNQ displays require their own unit/configuration. [JR] p.50; [BIG] pp.3–5; [REF] pp.5, 23.

**Not a standalone trade.** Thresholded executed size is evidence at a location, not a passive-wall detector or complete trade.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author/instrument/session, actual source threshold and per-print/cluster rule, native executed events, source bar/zone association. |
| Outputs / units | marker_events[], marker_side, marker_volume, threshold, aggregation_mode, source_display_known?. |
| ET clock / interval | Actual source London/NY action window; local reference must already exist at the marker time. |
| Bars / event membership | Jumbo native executed bubbles; Sires selected NQ 30–60 setting on source 40-range bars; Refill NQ/MNQ display configuration kept separate. |
| Reset / persistence | Source display/cluster reset and native bar membership; no full-session percentile. |
| known_at | At execution for a verified per-print rule; at completed cluster/bar only if source aggregation requires completion. |

**Procedure:**

1. Require the source instrument and exact selected display setting. Jumbo states NQ 100 in New York and 75 in London; Sires discusses settings 30–60, which is not permission to choose one after outcomes.
2. Compare the source's per-print or grouped executed size to its threshold using its equality convention. Unknown cluster/inclusion semantics remain a hole; do not aggregate arbitrary 2-minute bursts.
3. Keep markers labeled aggression. Their presence alone does not establish absorption, passive walls or entry.
4. A London marker cannot be located against a later-completed 6–9 box; use a contemporaneous source reference.

**Printed constants and limits:** Jumbo NQ 100/75 by source session; Sires NQ 30–60 setting range and 40-range chart; no cross-instrument normalized threshold supplied.

**Invalid / unavailable behavior:** Percentile substitute; NQ/MNQ sizes pooled; future location; marker relabeled absorption; guessed burst rule. Apply C04; emit `HOLE:O099:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O099-F1 — numeric fixture:** Synthetic explicitly configured per-print threshold 100 with inclusive comparison: trades 60 and 60 create 0 markers, trade 100 creates 1. Under a separately supplied aggregate-cluster rule, 60+60 may total 120, but it is not the same display. Remove the comparator/aggregation setting: faithful marker classification at the boundary is null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_tape._big_at](/workspace/implementation/src/trading_research/research/phase1_live/family_tape.py); mbp1_objects trade ingredients; the previous formula labels R-J15/R-F14/R-F17 and P3-08. The caller must use contemporaneous location and thresholds. Existing behavior is not authority over this procedure.


<a id="o100"></a>

## O100 — DOM at a planned location

**Wiki:** [DOM at a planned location](/workspace/planning/phase-1-live/wiki/dom.md). **Implementation mode:** local quote/execution observation; depth and source interpretation holes explicit.

The DOM combines resting display, executed activity and pace at the planned level. Sires resets/reads it before arrival and then checks who is absorbed, who refreshes and who gains actual price reward. [DOM5] pp.3–7; [DOM6] pp.3–7; [DOM7] pp.3–7. Saint uses DOM with footprint at the held retest. [TRAP] pp.8–10. The Refill paper also shows its pre-modeling observations as read from the DOM. [REF] p.7.

**Not a standalone trade.** A displayed wall can disappear without executing. DOM display alone does not certify defense or hidden size.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Premarked band/side, source DOM reset key, available quote levels/sizes, executed events, verified quote/event relationship, arrival and confirmation keys. |
| Outputs / units | local_quote_snapshots, local_executions, spread, display_changes, consumption_evidence?, defense_interpretation?, depth_coverage. |
| ET clock / interval | Reset/read before arrival at the planned level; stop local observation at each decision as-of. |
| Bars / event membership | Native DOM events and executed tape; MBP-1 supplies BBO only, not all off-touch levels or hidden reserve. |
| Reset / persistence | Actual source pre-arrival reset. If reset is not disclosed/supplied, local source DOM state is a hole. |
| known_at | Each local event/snapshot when available; same-level association must be verified. |

**Procedure:**

1. Start a new observation linked to the already-known band. Record resting display and executions in separate streams.
2. Compute literal BBO/spread and displayed changes where both same-price snapshots are observed. Record executions consuming liquidity separately; do not infer execution from a disappearing wall.
3. For depth beyond BBO or participant/hidden-reserve claims, require that actual input. NQ BBO cannot fill an AAPL 10-level field or a currently off-touch level.
4. Interpret absorption/replenishment/reward under the selected source branch, using the same local episode. Whole-session medians are not local evidence.

**Printed constants and limits:** No universal DOM reset window, wall size or refresh threshold.

**Invalid / unavailable behavior:** Displayed wall as executed defense; final-session statistic as local state; off-touch depth fabricated; separate levels joined. Apply C04; emit `HOLE:O100:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O100-F1 — numeric fixture:** Synthetic band 100, bid 100 size 10 before touch, later bid 100 size 15: observed display change+5. With no executed sell event, this is not consumed-and-replenished defense. A sell execution size 4 at 100 supplies execution evidence, but missing lifecycle/depth still prevents a verified hidden-reserve claim.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** mbp1_extract and mbp1_objects supply trade/BBO ingredients; the previous formula labels R-F06/F07/F13 and R-S09. Off-touch depth and verified hidden reserve are missing. Existing behavior is not authority over this procedure.


<a id="o101"></a>

## O101 — Absorption: effort without price reward

**Wiki:** [Absorption: effort without price reward](/workspace/planning/phase-1-live/wiki/absorption-and-big-trades.md). **Implementation mode:** source local effort/result and passive defense; exact detector hole.

Absorption requires aggressive effort making little progress against liquidity that actually holds/replenishes. The ensuing action depends on the branch: Sires's strict reversal additionally needs own-side reward and a defended reward retest, while his long-gamma balance fade does not require that reward sequence. [ABS] pp.5–13; [BIG] pp.14–15; [MATH] pp.6–8. Jumbo also describes absorption in his footprint/range read, without publishing the complete detector used there. [JR] pp.48–50. The member case records buyers absorbing and holding on the planned return; it does not publish the same four-check entry gate. [K10] pp.7–8.

**Not a standalone trade.** Large volume alone is not absorption; absorption alone is not every method's entry. Jumbo's small-body candle is a separate candle proxy.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen band, aggressive side/volume, local response interval/prices, actual passive holding/replenishment evidence, source interpretation and selected branch. |
| Outputs / units | aggressive_buy/sell/unknown_volume, price_progress_points/ticks, passive_defense?, source_absorption?, branch_id. |
| ET clock / interval | Effort and response at the selected area before decision; later reversal is an outcome. |
| Bars / event membership | Source local execution/DOM or native footprint intervals; Jumbo candle feature is a different object. |
| Reset / persistence | Each local test at the frozen band; no whole-session absorption flag. |
| known_at | After all effort, response and passive evidence used in the observation exists. |

**Procedure:**

1. Measure signed executed effort over the declared local interval and actual price progress in that effort's direction. Preserve the exact price/volume units.
2. Require the source passive hold/replenishment observation. Missing passive data cannot be repaired by a later reversal or high total volume.
3. The source does not disclose a universal large-effort/small-progress threshold; automatic absorption interpretation is null unless the complete source detector or contemporaneous interpretation is supplied.
4. Strict Sires reversal adds own-side reward and defended reward retest. BIG long-gamma failure fade and the member's buyers-absorbing/holding case retain their different gates.

**Printed constants and limits:** No universal volume/progress ratio, wall size or response horizon.

**Invalid / unavailable behavior:** Bigtrade alone=true; candle proxy as DOM proof; future reversal as prerequisite; strict reward gate imposed on every author/branch. Apply C04; emit `HOLE:O101:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O101-F1 — numeric fixture:** Synthetic at supplied resistance 110, buy 100 contracts produces only 0.25 point upward progress before the observation ends. These are exact measurements; without source passive evidence/interpretation, absorption=null. A later 2 point decline cannot retrospectively set absorption=true at the earlier decision.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.absorption_a/absorption_b](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_flow.r_f06_dom_absorption/r_f08_abs_four_check](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F06–F09/F16. Thresholds and BBO-only reload remain partial proxies. Existing behavior is not authority over this procedure.


<a id="o102"></a>

## O102 — Executed passive replenishment

**Wiki:** [Executed passive replenishment](/workspace/planning/phase-1-live/wiki/passive-replenishment.md). **Implementation mode:** executed-consumption and refresh sequence; BBO inference separately labeled.

Passive defense means liquidity is consumed and replenished at the relevant area, with the level continuing to hold. Consistency of refresh, size and pace matters on a retest. [DOM7] pp.3–7; [K18] p.11; [STOP] pp.9–10; [MATH] pp.6–8.

**Not a standalone trade.** A resting wall or one BBO size increase does not establish this sequence. A previously formed aggressive-print zone is not itself verified passive reload.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Same price/band/passive side, executed consumption events, quote/depth lifecycle snapshots, source refresh consistency criterion, local hold evidence. |
| Outputs / units | consumption_events, observed_same_price_size_changes, refresh_events?, bbo_reload_inference?, verified_replenishment?, hold?. |
| ET clock / interval | Consumption before/with refresh at the actual retest; local source observation interval in ET. |
| Bars / event membership | Native execution and order-book lifecycle evidence; retained BBO alone does not observe all changes at a level. |
| Reset / persistence | Actual local test/reset; earlier formed aggressive zone does not initialize verified passive defense. |
| known_at | At each verified sequence event; consistency only after the source-required observation interval. |

**Procedure:**

1. Require an actual execution consuming the defended side before claiming replenishment. A displayed increase without execution is new display, not the full sequence.
2. Match subsequent same-price updates under verified ordering and lifecycle coverage. Store literal changes and any explicitly named BBO reload inference; do not identify hidden reserve from it.
3. Apply only supplied source consistency/size/pace criteria. Without them, measured events remain available but faithful persistent-defense classification is a source hole.
4. If the price leaves BBO coverage, intervening state is unobserved; do not forward-fill it as a held wall.

**Printed constants and limits:** No exact source refresh count, window or size threshold is disclosed.

**Invalid / unavailable behavior:** One BBO increase as full defense; unexecuted wall; whole-session reload flag; off-touch state invented. Apply C04; emit `HOLE:O102:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O102-F1 — numeric fixture:** Synthetic verified lifecycle: bid 100 displays 10, sells consume 6, displayed remainder 4, then add 8 at 100 gives display 12. Consumption 6 and refresh 8 are observed. With only first 10 and last 12 snapshots, net+2 cannot prove the intervening 6/8 sequence. Missing lifecycle yields verified_replenishment=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.absorption_b/iceberg_touch_infer/on_touch_refill](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); the previous formula labels R-F06/F07/F09/F17 and R-S03. Full off-touch depth and hidden reserve verification are missing. Existing behavior is not authority over this procedure.


<a id="o103"></a>

## O103 — Iceberg evidence and added participation

**Wiki:** [Iceberg evidence and added participation](/workspace/planning/phase-1-live/wiki/iceberg-evidence.md). **Implementation mode:** evidence grading for hidden-liquidity hypothesis; verification requires missing data.

The DOM lesson refines defense through executed depletion, continuing replenishment and additional participants joining in the illustrated two-tick area, then entry behind the defended structure. [DOM7] pp.3–7. The auction-state discussion likewise requires persistent liquidity rather than a static wall. [MATH] pp.6–8.

**Not a standalone trade.** A hidden-order hypothesis is not proof of hidden reserve and is not a standalone entry. Spoof-like displayed size without executions fails the evidence read.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Executed depletion, same-price continuing refresh, persistent defense, added participant evidence, local price response and source configuration. |
| Outputs / units | executed_defense_evidence, bbo_iceberg_hypothesis?, verified_hidden_reserve?, added_participation?, source_entry_structure?. |
| ET clock / interval | Actual consumed/refreshed sequence before the source entry in ET. |
| Bars / event membership | Order-level/depth evidence where required. BBO-only inventory cannot verify hidden reserve or identify participants. |
| Reset / persistence | Each defended level/test; no global inferred iceberg flag. |
| known_at | After the required actual executions and added-participant observations. |

**Procedure:**

1. First validate consumption and replenishment under their recipe. Without executions, spoof-like display is insufficient evidence.
2. Separate a named hidden-liquidity hypothesis from verified reserve. Verification needs the actual source-compatible hidden/order lifecycle evidence, absent from the retained BBO schema.
3. The lesson's added participants in a two-tick area are a scoped refinement; preserve their actual source events and use entry behind that defended structure only when the source sequence supplies it.

**Printed constants and limits:** Illustrated two-tick participation area is case-specific, not a universal detector.

**Invalid / unavailable behavior:** Hidden reserve inferred as fact from BBO; participant IDs fabricated; two-tick rule transferred universally. Apply C04; emit `HOLE:O103:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O103-F1 — numeric fixture:** Synthetic q 0.25 gives a two-tick area width 0.50. Observed executions totaling 30 against repeatedly displayed 10 can support a labeled replenishment hypothesis; they do not uniquely prove hidden reserve 30 or identify 3 participants. verified_hidden_reserve remains null without the required evidence.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.iceberg_touch_infer](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); the previous formula labels R-F07. BBO inference exists; verified hidden reserve, off-touch depth and the full participant sequence are missing. Existing behavior is not authority over this procedure.


<a id="o104"></a>

## O104 — Price reward near the absorption origin

**Wiki:** [Price reward near the absorption origin](/workspace/planning/phase-1-live/wiki/reward-system-3tick.md). **Implementation mode:** price displacement relative to actual defense origin and scoped source reward.

The strict absorption reversal asks for the new controlling side to gain actual price reward near the original defense before a defended retest. The source discusses a three-tick neighborhood; the later four-stage clip illustrates 2–4 ticks of lift-off and entry within 1–2 ticks of confirmation. [ABS] pp.8–13; [STOP] pp.10–14.

**Not a standalone trade.** Failed opposing effort without reward does not pass the strict reversal branch. That does not add a reward requirement to the separate long-gamma balance-fade branch.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen defense origin/band, rewarded side, native tick q, local price path, source reference/distance convention, later retest and entry. |
| Outputs / units | reward_points, reward_ticks, source_reward_ok?, reward_at, retest_at, entry_distance_ticks. |
| ET clock / interval | After local absorption/defense, before its defended reward retest and decision. |
| Bars / event membership | Ordered price events/source bars; ticks are price units, never event counts. |
| Reset / persistence | Each actual defense origin/attempt; do not use first AM trade as origin. |
| known_at | At observed displacement; retest and entry distance only at their later events. |

**Procedure:**

1. For an explicitly supplied origin price P0 and direction d=+1 long/-1 short, calculate reward_points=d*(P-P0), reward_ticks=reward_points/q. If origin is a band and source chooses no reference edge, return that reference hole instead of midpoint guessing.
2. Apply the actual source reward/near-origin convention. The three-tick neighborhood is not automatically a minimum 3 tick move or a 3 event lookahead; STOP's 2–4 tick lift and 1–2 tick entry distance are separate illustrated values.
3. Strict reversal requires observed own-side reward followed by defended retest. This object does not add that sequence to BIG's separate long-gamma fade.

**Printed constants and limits:** Three-tick neighborhood in ABS; 2–4 tick lift and 1–2 tick entry distance in STOP are scoped source illustrations.

**Invalid / unavailable behavior:** Wrong origin; ticks treated events; universal minimum invented; future maximum reward. Apply C04; emit `HOLE:O104:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O104-F1 — numeric fixture:** Synthetic long origin 100, q 0.25, later 100.75 gives reward 0.75 point=3 ticks. A retest 100.50 occurs later and needs its own defense. A move of 3 events with prices 100, 100, 100 gives 0 ticks, not 3. With origin band [100, 100.5] and no selected edge, exact source reward distance is null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.reward_3tick/r_f08_abs_four_check/liftoff_upticks](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F08/F09. The first AM trade is not the source origin; exact reward window/reference remains partial. Existing behavior is not authority over this procedure.


<a id="o105"></a>

## O105 — Cumulative volume delta and its source reference

**Wiki:** [Cumulative volume delta and its source reference](/workspace/planning/phase-1-live/wiki/cvd-variants.md). **Implementation mode:** exact signed accumulation with source reset/reference holes.

Trade CVD accumulates signed executed volume under a chosen reset. Sires checks its direction/reference with local absorption, reward and retest; a price move and opposing CVD can weaken that reading. The plotted CVD median/reference is not fully defined. [ABS] pp.5, 8–13; [STOP] pp.6–8, 12–14; [BIG] pp.7–14.

**Not a standalone trade.** CVD divergence alone is not an entry, and an OHLC sign proxy is not known aggressor delta. A price-unit median cannot be compared with CVD units.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Canonical signed executions, verified source reset key, as_of, source CVD reference line/value and same-unit construction. |
| Outputs / units | cvd_known_component, unknown_volume, cvd_exact?, cvd_bounds, source_reference?, reference_relation?, cvd_change. |
| ET clock / interval | Actual selected source reset in ET; alternative resets stay named variants. |
| Bars / event membership | Executed aggressor delta. OHLC candle-sign volume is a labeled estimate and cannot fill true CVD. |
| Reset / persistence | Set cumulative buy/sell/unknown to 0 at the verified source reset; unknown coverage terminates exact accumulation. |
| known_at | Latest included trade and source reference availability; reference cannot be final-session or price-unit median. |

**Procedure:**

1. Accumulate B size minus A size under C03. Track N volume separately; with any unresolved N volume, exact CVD=null and possible signed bounds are known_component±unknown_volume.
2. Compute changes only between compatible snapshots of the same reset/instrument. A missing reset prevents author-exact CVD even if a comparison series can be computed.
3. The plotted source median/reference construction is unpublished. Retain a supplied, contemporaneous, volume-unit reference or emit HOLE:cvd_reference; do not use a price median or silently make CVD confirmation true.
4. Apply the selected branch's directional/reference relation; divergence alone is not entry.

**Printed constants and limits:** No source-complete median lookback, reset or universal divergence threshold.

**Invalid / unavailable behavior:** Reversed side; future trades; price/CVD unit comparison; OHLC proxy faithful; unknowns dropped. Apply C04; emit `HOLE:O105:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O105-F1 — numeric fixture:** Synthetic reset sequence B10, A4, B2 gives CVD 8 contracts. A supplied same-unit reference 5 gives difference+3. Comparing CVD 8 contracts with price 100 is invalid. Adding N3 gives CVD bounds [5, 11], exact CVD null; no fixed sign/reference conclusion is assumed where those bounds cross the relevant threshold.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.cvd_from_trades](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); family_flow; formulas_flow; the previous formula labels R-F02/F08/F09/F15 and P3-08. Source reference-line construction and some sign/retest joins are missing. Existing behavior is not authority over this procedure.


<a id="o106"></a>

## O106 — Candle direction versus executed delta

**Wiki:** [Candle direction versus executed delta](/workspace/planning/phase-1-live/wiki/candle-delta-disagreement.md). **Implementation mode:** same-candle price and executed-delta signs.

A candle can move one way while executed aggression leans the other, revealing effort without proportional result at an appropriate location. The footprint lesson then looks for absorption, evolving POC and local confirmation. [FP9] pp.4–7; [RD] pp.3–8.

**Not a standalone trade.** Opposite candle and delta signs do not automatically identify a trade or a passive wall; location and the branch sequence still matter.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Native candle ID and as-of/complete status, O/C/H/L, member executed events and side quality, planned location. |
| Outputs / units | price_change=C-O, known_delta, price_sign, delta_sign?, opposed_signs?, candle_id. |
| ET clock / interval | Actual source candle/as-of in ET; completed-candle requirement waits for close. |
| Bars / event membership | Native source candle, not whole AM aggregate or two different candles. |
| Reset / persistence | At each source candle start; intrabar snapshots retain the same candle ID. |
| known_at | At snapshot/close from included events only. |

**Procedure:**

1. Compute C-O and executed buy-minus-sell for the exact same candle membership. A positive or negative price sign requires nonzero change; a doji has sign 0.
2. If exact delta exists, disagreement is price_change*delta<0. A zero in either factor is not opposite signs. Missing sign data gives null unless a complete bounded sign conclusion is explicitly supported.
3. This feature is effort/result evidence only. Footprint reaction additionally needs valid location, same-candle POC relocation and the selected confirmation.

**Printed constants and limits:** Opposite strict signs only; no invented minimum delta/body threshold.

**Invalid / unavailable behavior:** Different candles joined; final CVD before close; delta inferred from C-O; disagreement called passive wall. Apply C04; emit `HOLE:O106:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O106-F1 — numeric fixture:** Synthetic candle O100/C101, executed B4/A10 gives price change+1, delta-6, opposed_signstrue. O=C100 gives false even with delta-6. Adjacent-candle delta cannot be substituted for this candle's-6.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f05_absorption_stack](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); mbp1_objects footprint/delta ingredients; the previous formula labels R-F05. Current whole-AM aggregation is not the native candle sequence. Existing behavior is not authority over this procedure.


<a id="o107"></a>

## O107 — Local delta concentration at an extreme

**Wiki:** [Local delta concentration at an extreme](/workspace/planning/phase-1-live/wiki/delta-spike.md). **Implementation mode:** local executed concentration measurements; source classifier/caption hole.

A concentration of aggressive delta at a fixed auction extreme must be interpreted with price response and the controlling side. One source figure repeats contradictory directional annotations at its two extremes, so the lower annotation does not settle an exact signed rule. [ABS] pp.10–13; [RD] pp.3–8; [TRAP] pp.4–5.

**Not a standalone trade.** A spike is effort, not proof of absorption, reward or reversal. An unrelated later maximum cannot define the earlier event.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Fixed auction extreme/band, source local interval, exact signed/total volume, baseline if explicitly supplied, response and literal annotation. |
| Outputs / units | local_delta, total_volume, delta_fraction?, source_spike?, observed_response, annotation_conflict. |
| ET clock / interval | Only local observations at the fixed extreme before decision. |
| Bars / event membership | Source native footprint/events; not final RTH maximum delta. |
| Reset / persistence | Each fixed location/test and declared interval. |
| known_at | After local interval observations; future response kept separate. |

**Procedure:**

1. Measure exact local delta and total volume. When total>0 and sides complete, delta_fraction=delta/total; it is a measurement, not a published spike threshold.
2. A concentration/spike detector needs the source baseline/window/threshold, which are not fully disclosed. Retain source annotations with their actual sign and evidence.
3. Where the figure repeats contradictory directional annotations, preserve conflict and do not manufacture a universal extreme-to-direction map. Absorption/reward/trapping require their own observations.

**Printed constants and limits:** No disclosed universal spike percentile or signed threshold.

**Invalid / unavailable behavior:** Later max defines earlier extreme; caption conflict resolved by outcome; positive Delta always bullish. Apply C04; emit `HOLE:O107:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O107-F1 — numeric fixture:** Synthetic upper band 110, local B80/A20 gives delta+60, total 100, fraction 0.6. If price fails to advance, record that response separately. The number 0.6 does not define a universal spike or short entry; source_spike=null without its criterion.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_value.scan_rth_delta](/workspace/implementation/src/trading_research/research/phase1_live/family_value.py); formulas_flow helpers; the previous formula labels R-F05/F08/F13 and R-J16. Exact source spike thresholds and reliable local joins are partial. Existing behavior is not authority over this procedure.


<a id="o108"></a>

## O108 — POC relocation within a candle

**Wiki:** [POC relocation within a candle](/workspace/planning/phase-1-live/wiki/candle-poc-flip.md). **Implementation mode:** same-native-candle event-time POC relocation.

The footprint schematic moves POC within the evolving candle after the local absorption read. It is not simply comparing two different candles' POC s. [FP9] pp.4–7.

**Not a standalone trade.** A POC flip alone is not the complete footprint reaction; the valid level, candle/delta disagreement and selected local confirmation must also exist.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | One native candle ID, at least two causal volume-by-price snapshots, source POC/tie conventions, source side/location interpretation and confirmation. |
| Outputs / units | poc_before, poc_after, poc_change, flip_at, source_relocation_ok?, same_candle. |
| ET clock / interval | Earlier snapshot before later snapshot and both before decision; candle can be developing only when source uses intrabar evidence. |
| Bars / event membership | One source-native candle; never an entire morning or adjacent-candle substitute. |
| Reset / persistence | Each candle start; accumulate only its own member executions. |
| known_at | At the later snapshot when the new POC is identifiable; ties propagate holes. |

**Procedure:**

1. Compute/ingest POC at each snapshot with the profile POC recipe and identical candle identity.
2. Record literal price relocation and source location within the candle. The source's intended qualifying direction/region must be provided where not fully specified; no arbitrary midpoint cross is invented.
3. Require the valid level and associated candle/delta disagreement and selected confirmation from the parent footprint route. POC movement alone is not the entry.

**Printed constants and limits:** No automatic flip threshold, cadence or universal upper/lower-half test.

**Invalid / unavailable behavior:** Adjacent candle POC s; final snapshot backdated; unresolved tie chosen; whole AM as candle. Apply C04; emit `HOLE:O108:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O108-F1 — numeric fixture:** Synthetic candle K at 10:01 has bins 100:10/101:5, POC 100; same K at 10:02 has 100:10/101:15, POC 101, change+1 known 10:02. A 10:01:30 entry cannot use it. Replacing the second snapshot's ID with K+1 fails same-candle identity.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f05_absorption_stack](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F05. An event-time intrabar POC series and same-candle flip detector are missing or partial. Existing behavior is not authority over this procedure.


<a id="o109"></a>

## O109 — Diagonal footprint imbalance stacks

**Wiki:** [Diagonal footprint imbalance stacks](/workspace/planning/phase-1-live/wiki/footprint-imbalance-zones.md). **Implementation mode:** explicit diagonal ratios and consecutive source rows; ambiguous source settings are holes.

The lesson compares ask volume at a price with bid volume one tick below, and the sell-side diagonal in the opposite direction. Runs of about 3–4× with stacked rows are the illustrated evidence; the source also shows two-row versus three-row cases at a level. [FP8] pp.3–7. Keani returns to the actual aggressive-buying imbalance band. [AVG] pp.21–22.

**Not a standalone trade.** A stack is neither absorption nor a complete breakout method. A same-price 350% display is another construction.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Native candle, tick q/source row grid, executed buy Ask(p) and sell Bid(p), selected ratio/comparator/zero rule, source stack length and current band. |
| Outputs / units | buy_ratio(p)=Ask(p)/Bid(p-q), sell_ratio(p)=Bid(p)/Ask(p+q), row_flags?, stack_bands[], known_at. |
| ET clock / interval | Source candle/as-of; completed pattern available only after required rows/events exist. |
| Bars / event membership | Same native candle and exact source price grid; gaps in rows are not collapsed. |
| Reset / persistence | Each source candle; later departure/retest references a frozen stack ID. |
| known_at | Latest required numerator/denominator and source configuration availability. |

**Procedure:**

1. Aggregate true aggressive buys and sells by exact row. For buys compare ask atp with bid one tick below; for sells compare bid atp with ask one tick above. Do not use same-price ratios.
2. For positive denominator compute the exact ratio. For denominator 0 distinguish numerator 0 (undefined 0/0) from positive numerator (unbounded ratio); source qualification for those cases remains null unless its zero/minimum volume rule is supplied.
3. Apply only the selected source threshold/run convention.3–4× and 3 stacked rows are illustrated; some source cases use 2 rows. Highlight inconsistencies prevent one universal threshold from being asserted.
4. Find runs on actual consecutive price rows p, p+q,… with same side; a missing row breaks measured contiguity or produces a coverage hole. Freeze the actual row band for a later defended revisit.

**Printed constants and limits:** Source illustrates 3–4×, 3 stacked rows and separate 2 row cases. Raw figure 56 ask/5 bid below gives 11.2×; 350% same-price display is different.

**Invalid / unavailable behavior:** Same-price instead of diagonal; rows gaps compressed; zero denominator automatic pass; source highlight assumed universal algorithm. Apply C04; emit `HOLE:O109:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O109-F1 — numeric fixture:** Synthetic q 0.25, Ask 100=40/Bid 99.75=10; Ask 100.25=60/Bid 100=10; Ask 100.5=80/Bid 100.25=20 gives buy ratios 4, 6, 4. Under explicitly supplied inclusive 4×, 3 row setting, stack band [100, 100.5]qualifies. Remove row 100.25 and 100/100.5 are not consecutive. Source-printed 56/5=11.2.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.footprint_4x](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_flow.r_f04_candle_stack/r_f04_revisit_hold](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F04/R-S09. Native candle membership and defended revisit are partial. Existing behavior is not authority over this procedure.


<a id="o110"></a>

## O110 — Same-price 350% imbalance display

**Wiki:** [Same-price 350% imbalance display](/workspace/planning/phase-1-live/wiki/same-price-imbalance.md). **Implementation mode:** same-price ratio measurements; literal 350% convention unresolved.

The Big Trades charts show a 350% imbalance display and a small band around the associated candle/print area. It contributes evidence at a catalyst or defended level. [BIG] pp.3–5; [K2345] p.5.

**Not a standalone trade.** This is not the diagonal footprint ratio and is not an entry by itself. A large bubble sharing the line does not prove absorption.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source native candle, price row, aggressive buy B and sell S at that same price, displayed label, exact ratio convention and source band. |
| Outputs / units | buy_multiple=B/S, sell_multiple=S/B, buy_percent_of=100*B/S, buy_percent_more=100*(B-S)/S, source_350_flag?. |
| ET clock / interval | Actual source candle/as-of before use; no final-candle band at an earlier stage. |
| Bars / event membership | Same-price native footprint/Big Trades display, not diagonal adjacent prices. |
| Reset / persistence | Each source candle/display observation. |
| known_at | When both same-row quantities and the source setting are available. |

**Procedure:**

1. For positive denominators calculate ratios and explicitly named percentage forms.350% of means 3.5 times; 350% more means 4.5 times. Preserve this ambiguity until the source configuration resolves it.
2. For zero denominators preserve undefined/unbounded numeric states and require a source zero rule for classification.
3. Retain the actual source small candle/print band. A calculated comparison may be reported under its own name but cannot fill author-exact source_350_flag when the convention is missing.
4. A bubble and imbalance sharing a line do not prove absorption or OFM completion.

**Printed constants and limits:** Literal 350% is printed; 3.5× versus 4.5× is unresolved, not a choice for the implementer.

**Invalid / unavailable behavior:** Diagonal ratio substituted; 350% more forced to 3.5; zero denominator automatically true; future candle. Apply C04; emit `HOLE:O110:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O110-F1 — numeric fixture:** Synthetic B35, S10 gives buy_multiple3.5, percent_of350%, percent_more250%. It meets an explicitly supplied 350%-of rule but fails 350%-more. With source wording alone, source_350_flag=null; do not choose whichever interpretation passes.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f14_imb350](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F14/F15. The source's 350% wording does not unambiguously equate 350% more with 3.5 times. Existing behavior is not authority over this procedure.


<a id="o111"></a>

## O111 — Speed of tape

**Wiki:** [Speed of tape](/workspace/planning/phase-1-live/wiki/tape-speed.md). **Implementation mode:** source pace observation; optional named descriptive arithmetic.

Pace distinguishes urgent initiative, slowing aggression and a dying tape. The passive OFM variant specifically describes failure without aggressive orders as tape speed dies. Charts label a panel Speed of Tape (10), but its unit/reset is not published. [DOM5] pp.3–7; [OFM] pp.7, 14; [BIG] pp.3–5.

**Not a standalone trade.** Fast or slow tape is not an independent entry. Ten is not automatically ten seconds.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Executed event identities/times, source local interval, panel setting and unit/reset if supplied, planned band and source pace interpretation. |
| Outputs / units | event_count, elapsed_seconds, prints_per_second_when_declared, volume_per_second_when_declared, source_pace?, source_panel_value?. |
| ET clock / interval | Pre-decision local observation interval ET; do not use the day's later maximum. |
| Bars / event membership | Executed events; tied physical trades count separately for totals but not as an invented ordered micro-sequence. |
| Reset / persistence | Actual source panel/local reset. Speed of Tape(10) does not identify ten seconds. |
| known_at | Observation interval end and source panel availability. |

**Procedure:**

1. If an explicit descriptive interval duration d>0 is supplied, count canonical executions and sum sizes; rates are count/d and volume/d. Label these named measurements, not the proprietary panel.
2. Retain source panel/settings and interpretation. Missing unit/window/reset gives source_panel_value=null even when prints-per-second can be calculated.
3. Passive OFM requires the source tape-dying/no-aggressive-order observation at its catalyst. A low rate alone does not define that branch.

**Printed constants and limits:** The literal panel setting 10 has unpublished unit/reset; no invented ten-second window or fast/slow threshold.

**Invalid / unavailable behavior:** 10 assumed seconds; day max as local; quote updates counted prints; arbitrary rate cutoff. Apply C04; emit `HOLE:O111:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O111-F1 — numeric fixture:** Synthetic explicitly selected 2 second interval contains 6 executions totaling 15 contracts:3 prints/second and 7.5 contracts/second. These numbers do not reproduce Speed of Tape(10) without its definition, so source_panel_value remains null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.tape_speed_pps](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) and flow ingredients; the previous formula labels R-F12/F15/F18/P3-08. The source panel's exact construction is missing. Existing behavior is not authority over this procedure.


<a id="o112"></a>

## O112 — Bid-ask spread

**Wiki:** [Bid-ask spread](/workspace/planning/phase-1-live/wiki/spread-width.md). **Implementation mode:** exact contemporaneous quote geometry.

The spread is part of the liquidity and execution context read with DOM and pace. Changes in displayed liquidity can alter the meaning and cost of the same aggressive print. [DOM5] pp.3–7; [MATH] pp.4–8.

**Not a standalone trade.** A narrow or wide spread is not a trade signal, and no universal source spread threshold admits every method.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Same-instrument bid/ask, tick q, quote event key, source quote quality/status and local association. |
| Outputs / units | spread_points=ask-bid, spread_ticks=(ask-bid)/q, quote_state, known_at. |
| ET clock / interval | Quote available at the local observation/entry key; no future or session-average quote. |
| Bars / event membership | Native BBO snapshots; no executed price substituted for bid or ask. |
| Reset / persistence | Each quote snapshot; no aggregation reset required. |
| known_at | Actual quote availability with verified event association. |

**Procedure:**

1. Require positive q and both valid quotes in the same units. Compute exact difference and divide byq.
2. If ask<bid mark crossed_quote and do not use a negative spread as normal liquidity. If ask=bid retain locked_quote/zero spread; whether usable depends on source/data semantics, not automatic entry approval.
3. Missing/stale quote validity is preserved as a hole. No universal source spread threshold admits trades.

**Printed constants and limits:** Instrument q comes from definitions; no strategy spread limit.

**Invalid / unavailable behavior:** Crossed/missing quotes treated normal; q guessed; future quote; session median at entry. Apply C04; emit `HOLE:O112:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O112-F1 — numeric fixture:** Synthetic bid 100, ask 100.50, q 0.25 gives spread 0.50 point=2 ticks. Ask 99.75 with bid 100 is crossed and invalid for normal spread evidence. Missing ask returns null, not 0.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** mbp1_extract and quote fields; the previous formula labels P3-08. Source-specific quantitative spread filters and order-linked costs are missing. Existing behavior is not authority over this procedure.


<a id="o113"></a>

## O113 — How price arrives at the area

**Wiki:** [How price arrives at the area](/workspace/planning/phase-1-live/wiki/approach-speed.md). **Implementation mode:** pre-touch arrival measurements and source interpretation.

Saint reads aggressive arrival versus drift and whether that effort produces acceptance or rejection at the HTF extreme. Sires also interprets pace at the planned reaction band. [WIC] pp.4–6; [AMTL] pp.5–10; [DOM5] pp.3–7. The Refill study separately lists approach speed among pre-touch flow/state features. [REF] p.8.

**Not a standalone trade.** Arrival style is context/control evidence, not an automatic direction or a complete entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Premarked area, explicitly selected approach start/end before touch, ordered price path, executions/pace, side and source class. |
| Outputs / units | approach_duration, net_distance, path_distance, net_speed_when_declared, effort, source_arrival_class?. |
| ET clock / interval | Approach ends at or before the actual test; subsequent rejection/acceptance is later evidence. |
| Bars / event membership | Native local price/flow observations; not final session extrema or medians. |
| Reset / persistence | Each arrival at the frozen area; prior departures define separate approaches. |
| known_at | At approach end after all included observations; source area known before approach selection. |

**Procedure:**

1. With explicit endpoints compute elapsed seconds, net price displacement and, if fully ordered, sum of absolute successive changes. Net speed is net displacement/elapsed time for a named descriptive measurement.
2. Retain executed effort and pace over exactly that interval. Source aggressive-arrival/drift classes have no universal published numeric threshold or start selector; absent definition means automatic class null.
3. Interpret current response only after arrival. Refills use pre-touch approach features; the touch's own later hold cannot enter them.

**Printed constants and limits:** No fixed approach distance/window or speed threshold.

**Invalid / unavailable behavior:** Future high selects start; touch outcome in feature; whole-session median; unknown order used for path length. Apply C04; emit `HOLE:O113:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O113-F1 — numeric fixture:** Synthetic preselected approach from 100 at 09:59:50 to 102 at 10:00:00 has duration 10 seconds, net distance 2 points, net speed 0.2 point/second. This does not automatically classify aggressive arrival. A 10:00:05 rejection is outside these pre-touch features.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f12_arrival](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F12. Current session-median trade size or maximum price is not local arrival speed; exact class thresholds are unpublished. Existing behavior is not authority over this procedure.


<a id="o114"></a>

## O114 — Aggressor print-size thinning

**Wiki:** [Aggressor print-size thinning](/workspace/planning/phase-1-live/wiki/digit-thinning.md). **Implementation mode:** source-local print-size sequence; cross-instrument threshold hole.

The execution clips read the opposing side's prints shrinking while the absorbing side begins to act. Literal digit classes differ across the ES clip and the coaching example; they are not global NQ size thresholds. [STOP] pp.10–14; [AVG] pp.25–26.

**Not a standalone trade.** Smaller prints alone do not confirm lift-off or a safe re-entry. The level, actual result and delta checks still apply.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Same band and opposing aggressor side, ordered sizes, instrument, actual source digit classes and thinning interpretation, opposite participation. |
| Outputs / units | size_sequence, digit_counts, source_thinning?, thinning_at, opposite_participation?. |
| ET clock / interval | Local opposing effort after defense and before lift-off in the selected source clip. |
| Bars / event membership | Actual execution sequence; unresolved tied order cannot be manufactured. |
| Reset / persistence | Each local defense/test; not an entire session distribution. |
| known_at | After the observed sequence and source class evidence. |

**Procedure:**

1. For positive integer execution sizes record decimal digit count as 1+floor(log 10(size)), implemented without floating rounding at powers of 10; this is display arithmetic only.
2. Retain the clip's actual instrument and direction of thinning. ES and coaching examples have different literal digit sequences; no universal 10/100-lot NQ cutoff follows.
3. Automatic thinning classification needs the source grouping/window/consistency rule. A few smaller prints alone do not establish opposing exhaustion or lift-off.

**Printed constants and limits:** No universal NQ size thresholds, percentile or required run length.

**Invalid / unavailable behavior:** Cross-instrument digits borrowed; session percentile; different band; thinning alone entry. Apply C04; emit `HOLE:O114:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O114-F1 — numeric fixture:** Synthetic same-side sizes 120, 85, 9 have digit counts 3, 2, 1 in that observed order. Sizes 9, 85, 120 give 1, 2, 3 and do not show that decline. The first sequence remains a source-classification hole if the qualifying grouping/window is not supplied.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.digits_thinning](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F09/P3-08. Source-local grouping, side alignment and full stage sequence are partial. Existing behavior is not authority over this procedure.


<a id="o115"></a>

## O115 — Absorber becomes aggressive and price lifts off

**Wiki:** [Absorber becomes aggressive and price lifts off](/workspace/planning/phase-1-live/wiki/lift-off.md). **Implementation mode:** absorber-to-aggressor transition with real price reward.

After defense, replenishment and opposing exhaustion, the absorber turns aggressive and price accelerates. The correct clip illustrates a small initial reward and prompt entry; the wrong clip enters late while the opposite side still gets paid. [STOP] pp.10–14.

**Not a standalone trade.** An uptick by itself is not the four-stage confirmation. Late distance from the origin cannot be repaired by smaller size.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Same-band defense/replenishment/exhaustion events, passive defender side, new aggression by that side, origin/confirmation price, q, actual decision. |
| Outputs / units | lift_at, new_aggressor_side, reward_ticks, entry_distance_ticks, stage_order_ok?, source_liftoff?. |
| ET clock / interval | defense<replenishment≤exhaustion<lift-off≤decision; local source clip in ET. |
| Bars / event membership | Native events and source price-response evidence; ticks are displacement, not event counts. |
| Reset / persistence | Per defended area/attempt; never reuse an earlier lift for a fresh re-entry. |
| known_at | At new aggression plus observed price reward; entry distance at actual decision. |

**Procedure:**

1. Require the same passive defender to become the source-observed aggressive side after opposing exhaustion. Buying versus selling identity must match the defended side.
2. Measure directional reward from the actual source origin and decision distance from the source confirmation price using q. Unknown band-edge reference is a hole.
3. Retain the clip's illustrated 2–4 ticks of initial reward and entry within 1–2 ticks as scoped geometry. Do not make those universal instrument settings or repair a late entry by smaller size.
4. Delta/location and the preceding stages remain mandatory in the selected four-stage branch.

**Printed constants and limits:** STOP illustration 2–4 tick lift and 1–2 tick entry distance; no universal acceleration detector.

**Invalid / unavailable behavior:** One uptick as all stages; opposite side paid ignored; future lift; late entry excused by size. Apply C04; emit `HOLE:O115:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O115-F1 — numeric fixture:** Synthetic long origin 100, q 0.25; defense 09:40, refresh 09:41, exhaustion 09:42, new buying and reward 100.75 at 09:43, entry 101 at 09:43:01 gives 3 tick reward and 1 tick distance from confirmation. Entry 102 has 5 tick distance from 100.75 and does not fit that illustrated 1–2 tick entry geometry.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.liftoff_upticks/r_f09_stop_stages](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F09. Full local side-specific stage binding is partial. Existing behavior is not authority over this procedure.


<a id="o116"></a>

## O116 — Zone formed by aggressive prints

**Wiki:** [Zone formed by aggressive prints](/workspace/planning/phase-1-live/wiki/refill-zone.md). **Implementation mode:** source aggressive-print zone plus later touch lifecycle; construction holes.

The Refill study first constructs an area from clustered large aggressive orders, then observes departure and a later return. Sires uses such areas as remembered control/refill locations within a thesis. This zone construction is distinct from proving passive order-book replenishment at a later test. [REF] pp.5–9; [OFM] pp.3–13; [CONT] pp.4–10.

**Not a standalone trade.** A burst or the zone's existence is not an automatic entry. Its later hold cannot be included in the features used to grade that same touch.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Zone ID, instrument/side, source per-print/burst threshold and clustering/band rule, formation events, source bounds, departure and later distinct contacts. |
| Outputs / units | zone_band, formation_start/end, known_at, departure_at, touch_ids[], construction_known?. |
| ET clock / interval | Formation before departure before current return in ET; current-touch outcome is excluded from formation/features. |
| Bars / event membership | Native aggressive executions/source bars. NQ/MNQ unit conversion requires actual source configuration. |
| Reset / persistence | Each newly formed source zone; history persists across later tests of that frozen zone. |
| known_at | At completed source zone formation; bounds cannot expand using later touch outcomes. |

**Procedure:**

1. Ingest the source zone or build it only from a fully disclosed cluster rule. Source thresholds, aggregation and NQ/MNQ normalization are incomplete; ≥100/2 minutes/2 ticks is only an old named variant, never faithful default.
2. Require an actual departure outside the source band, then a later return. Repeated rows inside the band are one contact under C05.
3. Keep aggressive zone formation separate from verified passive replenishment during a later test. A zone's existence is not an automatic entry.

**Printed constants and limits:** No complete source cluster engine; old 100/2 minute/2 tick parameters are prohibited as automatic source defaults.

**Invalid / unavailable behavior:** Current hold in zone features; bounds redraw; aggressive zone called passive reload; cross-instrument unit guess. Apply C04; emit `HOLE:O116:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O116-F1 — numeric fixture:** Synthetic supplied zone [100, 101] formed 09:40, departure 102 at 09:45, return 100.75 at 10:00 gives one later touch. Prices 100.5/100.75/101 while remaining inside that touch do not create 3 touches. Missing formation rule leaves automatic zone discovery null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.on_touch_refill](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_flow.r_f17_refill_zone](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F17/P3-08. Source clustering, NQ/MNQ normalization and full order lifecycle are missing; ≥100/2-minute/2-tick is a variant. Existing behavior is not authority over this procedure.


<a id="o117"></a>

## O117 — Memory of earlier zone tests

**Wiki:** [Memory of earlier zone tests](/workspace/planning/phase-1-live/wiki/zone-touch-memory.md). **Implementation mode:** strictly pre-touch persistent history.

The Refill study grades a newly encountered touch using earlier defense history, construction, location and incoming flow. Current-touch outcome must not supply its own memory. [REF] pp.6–10, 16; [OFM] pp.15–18.

**Not a standalone trade.** Remembered defenses are inputs to a read/grade, not an established automatic positive entry edge.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Frozen zone ID, current distinct touch ID/time, prior touch IDs/start/end/outcomes, each outcome resolution time, feature cutoff and source history fields. |
| Outputs / units | eligible_history_ids, prior_touch_count, prior_resolved_defense_count, unresolved_history_ids, max_feature_known_at, memory_causal. |
| ET clock / interval | Every historical touch must precede current touch and be resolved by its feature cutoff. |
| Bars / event membership | Touch lifecycle/event ledger; not daily aggregate touch count. |
| Reset / persistence | Zone identity persists; a new current touch changes the cutoff, not prior records. |
| known_at | Maximum actual availability of selected history fields, strictly no later than feature cutoff before touch. |

**Procedure:**

1. For current touch k, select only earlier distinct touch IDs of the same zone whose required labels were resolved before the pre-touch feature key.
2. Keep prior unresolved touches in an explicit list and retain all unselected current candidates. Do not insert the current hold/fail result into its own defense count.
3. Construction, memory, location and incoming flow remain separate feature groups. Published grading transformations are unavailable; this ledger does not recreate a grade engine.

**Printed constants and limits:** No disclosed lookback limit, memory decay or grade weight.

**Invalid / unavailable behavior:** Current outcome included; prior unresolved label backdated; later-day selection; different zone history. Apply C04; emit `HOLE:O117:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O117-F1 — numeric fixture:** Synthetic prior touch A ended 09:40 and defense resolved 09:42; touch B began 09:50 but outcome resolves 10:05; current touch C 10:00 with feature cutoff 09:59 can include A's defense only. Prior touch count can record A/B, but resolved defense count=1; C's later success cannot increase its own count.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-F17 has related revisit ingredients. A causal persistent touch-memory/availability ledger and the published grade transformations are missing. Existing behavior is not authority over this procedure.


<a id="o118"></a>

## O118 — Origin-of-the-Move catalyst

**Wiki:** [Origin-of-the-Move catalyst](/workspace/planning/phase-1-live/wiki/ofm-catalyst.md). **Implementation mode:** source repeated effort/failure origin and linked stages.

Repeated aggressive effort failing to achieve movement creates the squeeze catalyst/origin. The source draws a line at the relevant absorbed aggression with its surrounding cluster; later releases, failures and retests refer back to that identified origin. [OFM] pp.3–13; [BIG] pp.5–14; [CONT] p.10.

**Not a standalone trade.** The catalyst, a failed squeeze or a bubble is not the completed OFM entry. Aggressive and passive branches have different later requirements.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source catalyst line/cluster band, repeated aggressive effort and lack of reward, side, formation/availability, later release/failure/refill/drive/retest IDs. |
| Outputs / units | catalyst_id, origin_band, source_failed_effort?, known_at, linked_stage_ids. |
| ET clock / interval | Catalyst formed before its later release and chosen aggressive/passive branch. |
| Bars / event membership | Source native Big Trades/footprint/DOM events; not final morning extrema. |
| Reset / persistence | Each distinct source catalyst; later failed squeeze does not silently select a new origin. |
| known_at | After actual repeated effort/response establishing the source origin. |

**Procedure:**

1. Freeze the actual line and surrounding aggressive cluster described by the source. Repeated effort and no reward need source evidence; no automatic large-print/failure-count detector is disclosed.
2. Bind every subsequent stage to that catalyst and side. The first failed squeeze is only one stage, not a completed OFM entry.
3. Keep aggressive OFM, passive dying-tape variant and clean squeeze as different execution branches with their own requirements.

**Printed constants and limits:** No universal catalyst threshold, repetition count or final-extreme selector.

**Invalid / unavailable behavior:** Final high as origin; first failure entry; stage flags ignored; different catalyst joined. Apply C04; emit `HOLE:O118:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O118-F1 — numeric fixture:** Synthetic source catalyst band [100, 100.5] known 09:40 after two supplied failed aggressive pushes; release 09:45 and failure 09:47 remain linked stages. Entering 09:47 solely on that failure cannot pass a branch that still requires refill, drive and hold. A later morning high 110 cannot replace the origin.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f15_ofm/r_f18_squeeze](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F15/F18 and R-S03/S04. Current triggers can ignore their supplied stage flags. Existing behavior is not authority over this procedure.


<a id="o119"></a>

## O119 — Trapped aggression at an auction extreme

**Wiki:** [Trapped aggression at an auction extreme](/workspace/planning/phase-1-live/wiki/trapped-buyers.md). **Implementation mode:** Saint's source upper-extreme trapped-buying sequence; current confirmation required.

Saint's short example shows aggressive buying at an upper HTF extreme repeatedly failing, then requires current intraday break/retest and repeated body selling for entry. Two prior AM/PM failures support the thesis; they do not replace today's confirmation. Sires also distinguishes trapped participation from a responsive absorption fade. [TRAP] pp.3–10; [WIC] pp.4–10; [AVG] p.19.

**Not a standalone trade.** Large positive delta or one failed push is not the full short. A generic trapped-trader pattern does not merge the authors' methods.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Fixed HTF upper area, aggressive-buy effort/response, distinct earlier AM/PM failure IDs and times, current LTF break/retest, repeated body selling, DOM/control and decision. |
| Outputs / units | prior_failure_ids, buying_effort, failed_reward?, current_break_at, retest_at, body_selling_at, current_short_control?, source_sequence?. |
| ET clock / interval | Historical failures known before current test; current break/retest/body selling before entry ET. |
| Bars / event membership | Source HTF/LTF and native candle footprint; body selling is not automatically Sires diagonal-stack threshold. |
| Reset / persistence | Per fixed HTF area and new current attempt; historical episodes keep distinct IDs. |
| known_at | Each historical outcome when resolved; current control only after fresh source evidence. |

**Procedure:**

1. Retain the source's separate earlier AM and PM failures; do not duplicate today's AM high to fabricate two observations.
2. Measure current buying aggression and actual lack of upward reward at the fixed extreme. Then require the current intraday break/retest and repeated selling inside source candle bodies with DOM agreement.
3. Preserve the disclosed short example. No generic opposite-side mirror is invented. If buyers instead take and defend the area, the current short read fails/revises before a new decision.
4. Target/risk come from Saint's structural and Asia-range context, not a borrowed Sires entry rule.

**Printed constants and limits:** Two distinct historical AM/PM examples are case evidence, not a universal pattern threshold. No fixed local delta/body-sell cutoff.

**Invalid / unavailable behavior:** Duplicated history; positive Delta alone; old failures replace current retest; buyer defense ignored; unsupported mirror. Apply C04; emit `HOLE:O119:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O119-F1 — numeric fixture:** Synthetic earlier failures A yesterday 10:00 and B yesterday 14:00 are 2 distinct records. Current upper area 110 fails at 09:40, breaks down 09:45, retests 09:50, source body-selling/DOM confirms 09:52, entry 09:53 preserves order. Using A twice yields 1 distinct failure; entering 09:48 skips current retest.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f13_trapped_buyers](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F13. Local concentration, separate historical attempts and same-boundary current confirmation are partial. Existing behavior is not authority over this procedure.


<a id="o120"></a>

## O120 — Native candle footprint

**Wiki:** [Native candle footprint](/workspace/planning/phase-1-live/wiki/footprint.md). **Implementation mode:** native candle executed-volume rows with body/wick and source display filters.

A footprint locates executed buy/sell participation at prices inside the actual source candle. Sires uses it for local effort/result and imbalance reads; Saint's confirmed short has repeated selling inside candle bodies with DOM agreement. Jumbo's raw display can highlight only the top 35% of transactions. [FP8] pp.3–7; [TRAP] pp.8–10; [JR] pp.48–50; [AVG] pp.21–22.

**Not a standalone trade.** A footprint is evidence, not one shared entry rule. Saint's body selling does not make Sires's diagonal-stack threshold mandatory for him.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source bar definition/candle ID, member executed events, exact row grid, O/C as-of, source filter settings and source interpretation. |
| Outputs / units | per_price_buy/sell/unknown/total, delta, body_rows, wick_rows, displayed_rows, filter_provenance, known_at. |
| ET clock / interval | Source candle/as-of; complete-candle bodies use final O/C only after close. Intrabar bodies use the actual as-of C. |
| Bars / event membership | Source native time/range bars; unknown range-bar construction remains a hole. |
| Reset / persistence | Each candle; preserve every intrabar snapshot's ID and as-of. |
| known_at | At member events/as-of, or close when the branch needs a completed candle. |

**Procedure:**

1. Aggregate executed side/size per exact source price row using C03. Check total=buy+sell+unknown and keep unknown delta unresolved.
2. For the selected body definition classify native row prices between min(O, C) and max(O, C), with boundaries retained explicitly; remaining traded rows are wicks. Source row-band overlap/boundary convention must be supplied for wider rows.
3. Apply only the source display filter. Jumbo's top 35% of transactions label does not disclose the selection universe/tie rule; retain supplied highlighted records or emit a filter hole. Do not choose a future percentile.
4. Saint repeated body aggression, Sires diagonal stacks and Jumbo filters remain different readings, each requiring its own local sequence.

**Printed constants and limits:** Top 35% display in Jumbo source; universe/tie rule unpublished. No universal footprint signal.

**Invalid / unavailable behavior:** Whole AM delta as native candle; source bars guessed; final body used early; display filter as full volume; author pattern borrowed. Apply C04; emit `HOLE:O120:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O120-F1 — numeric fixture:** Synthetic completed candle O100/C101, H102/L99, q 1 has literal body prices 100 and 101; 99 and 102 are wick rows. If body rows contain B3/A8, body delta=-5 with complete sides. At an earlier as-of C100, price 101 was not yet in that as-of body. Missing top 35% selection convention leaves the faithful filtered display null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.footprint_4x](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py) and trade ingredients; family_tape; the previous formula labels R-F04/F05/F13/F14, R-J15/J16 and R-S09. Native source bars and local multi-candle joins are partial. Existing behavior is not authority over this procedure.


<a id="o121"></a>

## O121 — At-level DOM rejection

**Wiki:** [At-level DOM rejection](/workspace/planning/phase-1-live/wiki/dom-rejection-branch.md). **Implementation mode:** Sires at-level execution route.

At a premarked allowed location, arriving aggression makes little progress; observe actual rejection and the selected lesson's additional participation, then enter behind defended structure. The iceberg refinement requires executed replenishment rather than a resting wall. [DOM6] pp.3–7; [DOM7] pp.3–7.

**Not a standalone trade.** This branch still needs Sires's live thesis, auction route, location, risk and objective. A DOM wall or rejection elsewhere does not pass.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Live Sires thesis/auction route, premarked allowed band, arrival effort and little-progress evidence, actual rejection, selected DOM/iceberg confirmation, source structural stop/objective. |
| Outputs / units | arrival_at, rejection_at, additional_confirmation_at?, local_sequence?, selected_confirmation_mode. |
| ET clock / interval | Band before arrival; arrival≤rejection≤decision, with any selected extra participation observed before decision. |
| Bars / event membership | Native DOM/execution events and source-compatible price response. |
| Reset / persistence | Each band/side/attempt; local DOM reset must precede arrival. |
| known_at | Latest selected local confirmation event; no future response supplies an earlier gate. |

**Procedure:**

1. Resolve the parent method's thesis, auction permission, planned location, objective and risk first.
2. Require aggressive arrival with source-observed little progress, then actual rejection at the same band. These qualitative readings require source evidence under C01.
3. If the selected DOM 7 refinement requires executed replenishment or added participation, require those observations. A resting wall is insufficient and missing depth gives unknown.
4. Enter only under the source selected confirmation and behind its defended structure; no arbitrary stop buffer is introduced.

**Printed constants and limits:** No universal volume, duration, rejection or stop-buffer threshold.

**Invalid / unavailable behavior:** Different-band rejection; unexecuted wall; missing extra confirmation bypassed; parent thesis/risk ignored. Apply C04; emit `HOLE:O121:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O121-F1 — numeric fixture:** Synthetic band 110 known 09:30; aggressive arrival 09:40, source rejection 09:41, required added participation 09:42, decision 09:43 preserve local order. A 09:41:30 decision requiring the 09:42 evidence fails causality. Missing depth makes that evidence unknown, not automatically true.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.aggressive_at_level/r_f06_dom_absorption](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [mbp1_objects.absorption_a/absorption_b/iceberg_touch_infer](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); the previous formula labels R-F06/F07. The full local sequence is partial. Existing behavior is not authority over this procedure.


<a id="o122"></a>

## O122 — Four-check absorption reversal

**Wiki:** [Four-check absorption reversal](/workspace/planning/phase-1-live/wiki/absorption-reward-retest.md). **Implementation mode:** strict four-check Sires reversal at a fixed real extreme.

The strict reversal starts at a fixed real extreme: opposing aggression is absorbed by a passive wall, the new side earns price reward near that origin, and price retests the rewarded area with renewed defense/aggression and supportive CVD. [ABS] pp.5–13.

**Not a standalone trade.** This source pattern is a fade/local reversal, not a continuation of the same push. The long-gamma failure fade is a different branch with no compulsory own-reward stage.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Fixed real extreme/band, source local absorption/passive defense, new-side price reward near origin, same rewarded-area retest and renewed defense/aggression, supportive source CVD reference, parent method gates. |
| Outputs / units | absorption_at, reward_at, retest_at, retest_defense_at, cvd_ok?, strict_reversal_sequence?. |
| ET clock / interval | absorption<own_reward<defended_reward_retest≤decision; all source observations in the same local episode. |
| Bars / event membership | Native source DOM/footprint and execution bars; evolving CVD and reward snapshots causal. |
| Reset / persistence | Each real extreme/attempt; moving current VA edge is not a fixed real extreme. |
| known_at | At the final defended retest/CVD evidence needed by the decision. |

**Procedure:**

1. Require a source real extreme, with the strict branch's middle/POC exclusion. Confirm opposing aggression is absorbed by actual passive defense.
2. Require the new side to gain actual directional price reward near the source origin under the reward recipe.
3. Require later return to the same rewarded area, renewed defense/aggression and supportive CVD under its own source reset/reference. Missing CVD reference cannot be hard-coded true.
4. This is the source local reversal/fade. Do not use a continuation push to satisfy it or add this own-reward sequence to BIG's separate long-gamma failure fade.

**Printed constants and limits:** Source three-tick neighborhood is scoped by its reward convention; no invented universal reference or timer.

**Invalid / unavailable behavior:** Middle/POC entry; moving edge; first AM trade as origin; no reward; retest absent; CVD proxy; all same-day events pooled. Apply C04; emit `HOLE:O122:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O122-F1 — numeric fixture:** Synthetic fixed support 100, q 0.25; absorption 09:40, own reward 100.75 at 09:41, return 100.50 at 09:42, source renewed defense/CVD 09:43, decision 09:44 gives the ordered sequence. Remove the return: strict_reversal_sequence=false with complete attempt evidence. If CVD reference is missing, the otherwise valid sequence is unknown.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.reward_3tick/r_f08_abs_four_check](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F08 with F02/F06/F07. Source CVD reference, reward window and same-event stages remain incomplete. Existing behavior is not authority over this procedure.


<a id="o123"></a>

## O123 — Defense, replenishment, exhaustion and lift-off

**Wiki:** [Defense, replenishment, exhaustion and lift-off](/workspace/planning/phase-1-live/wiki/stop-four-stage.md). **Implementation mode:** source four-stage stop/re-entry execution variant.

The stop/re-entry lesson requires location → initial defense → replenishment → opposing print thinning → absorber becomes aggressive and price lifts off. The correct clip illustrates 2–4 ticks of reward, entry within 1–2 ticks of confirmation and the stated −4R daily stop. [STOP] pp.6–15.

**Not a standalone trade.** No missing box becomes acceptable by reducing size. A stop-out starts a new attempt with every check repeated.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Fixed real extreme, defense/refresh/opposing-thinning/lift events and sides, supportive delta, q, source origin/confirmation reference, actual entry and pre-entry daily R. |
| Outputs / units | stage_order_ok, reward_ticks, entry_distance_ticks, daily_stop_ok, source_variant_sequence?. |
| ET clock / interval | defense<replenishment≤exhaustion<lift-off≤decision in the current attempt. |
| Bars / event membership | Native local executions and price displacement; no ticks-as-event-count implementation. |
| Reset / persistence | Every attempt, including re-entry, repeats all stages. Daily R resets only on the source account day. |
| known_at | All stages and daily R before actual entry; no later loss included in pre-entry daily R. |

**Procedure:**

1. Require the fixed extreme, initial passive defense, actual replenishment, opposing print thinning and the absorber becoming aggressive with real price reward.
2. Require supportive source delta/CVD and consistent sides/band IDs.
3. For this printed source variant require 2≤reward_ticks≤4, abs(entry_price-confirmation_price)/q≤2, and daily_R_before>-4. If source origin/reference is absent, distance is unknown rather than measured from a convenient price.
4. A failed/missing check is not excused by small size. After a stop-out create a new attempt and reacquire every required observation.

**Printed constants and limits:** Reward 2–4 ticks, entry distance at most 2 ticks and daily stop-4R are scoped to STOP's illustrated variant.

**Invalid / unavailable behavior:** Event counts as ticks; stages reused after stop; absent delta passed; entry at daily R=-4; late entry repaired by size. Apply C04; emit `HOLE:O123:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O123-F1 — numeric fixture:** Synthetic q 0.25, origin 100, lift confirmation 100.75, entry 101 and daily R=-3 produce reward 3 ticks, distance 1 tick, daily_stop_ok=true. At daily R=-4 it is false. Entry 101.50 is 3 ticks from confirmation and fails the at-most 2 tick condition even if size is halved.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.digits_thinning/liftoff_upticks/r_f09_stop_stages](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F09 with F02/F06/F07/F08. Complete source-local stage association is partial. Existing behavior is not authority over this procedure.


<a id="o124"></a>

## O124 — Footprint-confirmed reaction

**Wiki:** [Footprint-confirmed reaction](/workspace/planning/phase-1-live/wiki/footprint-confirmed-reaction.md). **Implementation mode:** same-candle footprint reaction route.

The footprint lesson first locates the valid area, then reads candle/delta disagreement, local absorption, POC relocation within the candle and the selected DOM/delta confirmation. [FP9] pp.4–7.

**Not a standalone trade.** An intrabar POC flip or delta disagreement alone is not this branch; common thesis, auction, risk and objective gates still apply.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Premarked valid area, native candle ID, price/delta disagreement, source local absorption, intrabar POC before/after snapshots, selected DOM/delta confirmation and parent gates. |
| Outputs / units | disagreement_at, absorption_at, poc_flip_at, flow_confirm_at, footprint_sequence?. |
| ET clock / interval | level_known≤absorption≤intrabar_flip≤decision, with all selected flow confirmation by decision. |
| Bars / event membership | Actual native candle; intrabar snapshots within the same candle. |
| Reset / persistence | Each candle/area/attempt; not an AM-wide pseudo-candle. |
| known_at | Later POC snapshot and actual local confirmation availability. |

**Procedure:**

1. Require the source-valid location and same-candle price/delta disagreement.
2. Require local absorption followed by POC relocation within that candle using the candle-POC recipe.
3. Require the selected source DOM/delta confirmation at the same area before entry. Adjacent-candle POC comparisons cannot fill this field.
4. Propagate unavailable evolving candle data and source POC/reference definitions as holes; common thesis/risk/objective remain mandatory.

**Printed constants and limits:** No universal POC-flip distance, delta threshold or candle timeframe.

**Invalid / unavailable behavior:** Adjacent candle flip; bare disagreement; final candle at earlier decision; missing local confirmation. Apply C04; emit `HOLE:O124:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O124-F1 — numeric fixture:** Synthetic level 100 known 09:30, candle K disagreement/absorption 09:40, same K POC 100→101 observed 09:41, source flow confirmation 09:42, entry 09:43 preserve the route. Changing the second POC snapshot to candle L fails same-candle identity. Missing intrabar tape gives unknown, not an inferred flip.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f05_absorption_stack](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F05. Adjacent-candle POC s or an entire AM candle do not implement the source sequence. Existing behavior is not authority over this procedure.


<a id="o125"></a>

## O125 — Confirmed VWAP deviation fade

**Wiki:** [Confirmed VWAP deviation fade](/workspace/planning/phase-1-live/wiki/vwap-deviation-fade.md). **Implementation mode:** confirmed source VWAP-band rotation.

In an appropriate auction context, price reaches the selected source VWAP deviation; absorption/rejection plus CVD and ladder confirmation permit a rotation toward VWAP or another named objective. [VWAP] pp.3–8.

**Not a standalone trade.** A blind ±2-band touch is not the entry. This fade is not Green Bird's separately disclosed VWAP continuation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Live Sires auction context, source VWAP/reset/deviation settings, frozen selected band, actual touch, absorption/rejection, supportive CVD and ladder confirmation, preselected objective and risk. |
| Outputs / units | band_touch_at, absorption_at, ladder_confirm_at, cvd_ok?, vwap_fade_sequence?, target_id. |
| ET clock / interval | VWAP/band available before touch; all local confirmations before decision. |
| Bars / event membership | Source VWAP weighting and local DOM/footprint evidence; not blind bar-band touch. |
| Reset / persistence | Parent VWAP reset and local test reset separately recorded. |
| known_at | Maximum band and local confirmation availability; later VWAP snapshot cannot change earlier band. |

**Procedure:**

1. Require the source-compatible reset, variance convention and selected multiplier; unresolved construction leaves the faithful band unknown.
2. At the actual selected band touch require source absorption/rejection plus CVD and ladder evidence supporting the rotation.
3. Freeze VWAP or another source objective before entry. Keep this fade inside Sires's method, distinct from Green Bird's separately disclosed VWAP continuation.

**Printed constants and limits:** Only the selected source deviation multiplier; no universal±2 fade.

**Invalid / unavailable behavior:** Blind band touch; unknown reset labeled exact; unrelated later absorption; GB continuation merged. Apply C04; emit `HOLE:O125:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O125-F1 — numeric fixture:** Synthetic supplied VWAP 100,σ2, k 2 gives upper band 104. Touch 104 at 09:40, local rejection 09:41 and source CVD/ladder 09:42 can qualify an otherwise complete 09:43 short toward preselected VWAP 100. A touch 104 alone leaves confirmation missing; a later VWAP 101 cannot rewrite the target selected as 100.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.running_vwap/r_f01_vwap_fade/r_f03_convergence](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F01/F03 with F02/F06. Exact source reset/deviation and at-band confirmation are partial. Existing behavior is not authority over this procedure.


<a id="o126"></a>

## O126 — Aggressive Origin of the Move

**Wiki:** [Aggressive Origin of the Move](/workspace/planning/phase-1-live/wiki/ofm-aggressive-branch.md). **Implementation mode:** full aggressive OFM ordered execution branch.

Repeated unpaid effort establishes a catalyst; an attempted squeeze fails; price returns through the catalyst/refill area; renewed initiative takes intervening wicks, refill holds, and entry is on the drive's defended retest with own-side aggression and supportive CVD. BIG restricts this aggressive branch to short gamma. [OFM] pp.3–13; [BIG] pp.7–14, 18; [CONT] p.10.

**Not a standalone trade.** The first failure, catalyst bubble or refill touch is not the complete confirmed entry. Optional earlier entries are separately labeled.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Known catalyst, first release, failed squeeze, refill return, renewed drive taking intervening wicks, held refill and defended drive retest, own aggression/reward, source CVD, short-gamma context and parent gates. |
| Outputs / units | catalyst_at, release_at, failure_at, refill_at, drive_at, drive_retest_at, wick_taken?, refill_held?, aggressive_ofm_sequence?. |
| ET clock / interval | catalyst<first_release<failure≤refill<drive<defended_retest≤decision. |
| Bars / event membership | Source native catalyst/Big Trades/DOM/price structure; no final-AM extrema stages. |
| Reset / persistence | Each source catalyst/attempt; optional early entry is a separate case record. |
| known_at | At final defended retest plus source CVD/regime availability. |

**Procedure:**

1. Require BIG's source short-gamma permission for this aggressive branch and the parent live thesis/auction/risk/objective.
2. Validate every named stage and side in the printed order. A first failed squeeze or refill touch cannot bypass later drive and held retest.
3. Require the actual drive to take the source intervening wick references, refill to hold, and the defended retest to show own-side aggression/reward and supportive CVD.
4. Any supplied stage flag must be recomputed/validated from cited evidence under C01; ignored release/failure/refill inputs are an implementation failure.

**Printed constants and limits:** Source short-gamma permission; no invented catalyst/drive thresholds or stage timeouts.

**Invalid / unavailable behavior:** First failure entry; required stage ignored; long gamma passed; future extreme as wick; early exception promoted. Apply C04; emit `HOLE:O126:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O126-F1 — numeric fixture:** Synthetic stages 09:40 catalyst, 09:41 release, 09:42 failure, 09:43 refill, 09:45 drive, 09:47 defended retest, 09:48 entry with all supplied side/control gates and short gamma preserve the sequence. Move entry to 09:44: it fails required drive/retest. Missing source CVD reference makes the otherwise ordered candidate unknown.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f15_ofm/r_f14_imb350/r_s03_second_defence/r_s04_ath_ofm](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F14/F15/F17, R-S03/S04. The current trigger can ignore required release/failure/refill flags. Existing behavior is not authority over this procedure.


<a id="o127"></a>

## O127 — Passive Origin-of-the-Move variant

**Wiki:** [Passive Origin-of-the-Move variant](/workspace/planning/phase-1-live/wiki/ofm-passive-branch.md). **Implementation mode:** source passive long case; incomplete quantitative selector.

The passive example's squeeze fails without aggressive orders at that failure as tape speed dies. The illustrated long enters above the buyers' area with a stop below the aggression and a 1R–3R scalp objective. The source calls it a passive version of the same model. [OFM] p.14.

**Not a standalone trade.** This branch must not inherit a requirement for aggressive failure prints. The replay does not publish a universal gamma condition or a mirrored short rule.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source squeeze and failure, local no-aggressive-order/dying-tape evidence, preknown buyers' area, trigger above it, entry, stop below source aggression and chosen 1R–3R scalp objective. |
| Outputs / units | failure_at, trigger_at, buyer_area, entry_above_area, stop_below_aggression, objective_R, passive_case_sequence?. |
| ET clock / interval | Source failure<trigger≤decision; pace/no-aggression observations cover the actual failure before decision. |
| Bars / event membership | Source native tape/area evidence; no invented mirrored short or gamma gate. |
| Reset / persistence | Per source catalyst/passive case. |
| known_at | Failure/pace and buyer-area availability before trigger; risk/target selected before entry. |

**Procedure:**

1. Preserve the illustrated long and the failure without aggressive orders as tape speed dies. Missing exact pace/no-aggression detector remains a hole, not aggressive-branch confirmation.
2. Check actual entry trigger above the buyers' area and stop below the relevant aggression, using source bounds without an invented tick buffer.
3. Record the selected 1R–3R scalp objective as source ticket geometry. No new P&L simulation or universal gamma condition is added.

**Printed constants and limits:** Illustrated 1R–3R scalp objective; no published universal gamma gate or mirrored short rule.

**Invalid / unavailable behavior:** Aggressive failure prints required; short mirror invented; future pace; stop relationship wrong. Apply C04; emit `HOLE:O127:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O127-F1 — numeric fixture:** Synthetic buyers' area [100, 101], aggression loweredge 100, long entry 101.25, source stop 99.75 gives initial risk 1.5 points. A selected 2R reference is 104.25, within the illustrated 1–3R range. This arithmetic does not fill the unpublished dying-tape selector; case qualification remains unknown if that evidence is absent.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-F15 is related; a distinct passive branch and full source execution record are missing. Existing behavior is not authority over this procedure.


<a id="o128"></a>

## O128 — Clean squeeze continuation

**Wiki:** [Clean squeeze continuation](/workspace/planning/phase-1-live/wiki/clean-squeeze.md). **Implementation mode:** first-pullback clean release continuation.

A fast release leaves the catalyst without the prior failed-squeeze sequence. On the first pullback, opposing aggression is absorbed and continuation confirms the thesis direction. [CONT] p.11; [OFM] p.5.

**Not a standalone trade.** A fast move alone is not entry, and no-failure refers only to history through the decision, not future survival.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Known catalyst, actual fast release, complete source history through decision showing no prior failed-squeeze sequence, first pullback, opposing absorption and continuation confirmation, parent thesis/risk. |
| Outputs / units | release_at, first_pullback_at, opposing_absorption_at, confirm_at, no_prior_failure?, clean_squeeze_sequence?. |
| ET clock / interval | catalyst<release<first_pullback≤confirmation≤decision; no-failure history stops at decision. |
| Bars / event membership | Source local pace/events and price/flow; no future 15-minute survival filter. |
| Reset / persistence | Each catalyst's initial release; later pullbacks keep their actual ordinal. |
| known_at | After first-pullback confirmation and complete already-elapsed history. |

**Procedure:**

1. Require source fast-release evidence from the catalyst. Source pace detector missing remains a hole.
2. Identify the actual first pullback under the source definition; do not select a later favorable retest. No prior failed-squeeze sequence is an as-of historical statement only.
3. Require opposing aggression to be absorbed at that pullback and continuation to confirm the live thesis direction before entry.

**Printed constants and limits:** No automatic pace cutoff, pullback distance or future survival horizon.

**Invalid / unavailable behavior:** Catalyst/release flags ignored; later pullback selected; future failure absence; fast move alone. Apply C04; emit `HOLE:O128:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O128-F1 — numeric fixture:** Synthetic catalyst 09:40, release 09:41, first pullback 09:43, source absorption/confirmation 09:44 and entry 09:45 preserve order with complete history. A later failure 10:00 cannot invalidate the earlier no-prior-failure fact; choosing a second pullback 09:50 instead fails the first-pullback branch.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f18_squeeze/tape_speed_pps](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F18. The current helper can ignore supplied catalyst/release flags. Existing behavior is not authority over this procedure.


<a id="o129"></a>

## O129 — Failure of aggression in long-gamma balance

**Wiki:** [Failure of aggression in long-gamma balance](/workspace/planning/phase-1-live/wiki/balance-failure-fade.md). **Implementation mode:** long-gamma balance failure-and-return fade.

In long-gamma balance, aggression at an extreme repeatedly goes unpaid; price leaves and returns to that failed area; the aggression remains unpaid. The fade targets where the opposite side previously had control. [BIG] pp.14–15, 18.

**Not a standalone trade.** This branch does not require an own-side aggressive squeeze/reward sequence. It still requires balance, the real extreme, retest, risk and the source objective.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source long-gamma and balance context, fixed real extreme, repeated unpaid aggression, departure and same-area retest, continued lack of reward, preselected earlier opposite-control target. |
| Outputs / units | failed_effort_at, leave_at, retest_at, still_unpaid?, target_control_id, balance_fade_sequence?. |
| ET clock / interval | failure<leave<same-area_retest≤decision with continued unpaid effort observed by decision. |
| Bars / event membership | Source native local effort/price response and balance snapshot. |
| Reset / persistence | Each extreme/failed-effort episode; previous opposite-control objective retains its own ID. |
| known_at | Context/extreme before failure; retest evidence before decision; target selected before entry. |

**Procedure:**

1. Require BIG's long-gamma balance permission and a real outer extreme.
2. Observe aggressive effort failing, actual departure, later return and continued lack of price reward at the same area.
3. Target the source place where the opposite side previously controlled. Do not substitute the opposite 6–9 edge without that source relationship.
4. Own-side squeeze/reward/reward-retest is not compulsory here; those gates belong to strict absorption reversal.

**Printed constants and limits:** Long gamma source permission; no fixed failure count, no universal target edge.

**Invalid / unavailable behavior:** Touch without return; short gamma; reward gate borrowed; opposite clock edge as default target. Apply C04; emit `HOLE:O129:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O129-F1 — numeric fixture:** Synthetic long-gamma balance [100, 110]: failed buying at price 110 at 09:40, departure to 108 at 09:42, retest of 110 at 09:45 with source evidence of buying still unpaid, short entry at 09:46, and a preselected opposite-control target of 103 preserve the route. The target is 103; it is not automatically the balance low of 100. This branch does not require a lift in the intended trade direction.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f16_balance_fade](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F16. Opposite 6–9 edge is not automatically the source's prior-control target. Existing behavior is not authority over this procedure.


<a id="o130"></a>

## O130 — Fresh defense of a continuation band

**Wiki:** [Fresh defense of a continuation band](/workspace/planning/phase-1-live/wiki/defended-band-continuation.md). **Implementation mode:** fresh same-side defense within a live directional thesis.

An established HTF direction and band have prior control; a return finds the same side defending/refilling with real participation; entry follows that fresh confirmation. If buyers instead break above the short thesis's extreme with strong buying, the clean-continuation source considers a retest long toward VWAP. [NYAM] pp.4–5; [K18] pp.7, 11, 14; [CONT] pp.4–10; [ANAT] p.7.

**Not a standalone trade.** A previous defense is not permanent permission. A break of the thesis's controlling extreme cannot be ignored to keep fading it.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Live HTF thesis and controlling extreme, known band/prior control, actual return, fresh same-side executions/reload/refresh consistency, current control, optional supported source flip. |
| Outputs / units | prior_defense_at, retest_at, fresh_defense_at, control_matches_thesis?, continuation_sequence?, flip_record?. |
| ET clock / interval | prior_defense<retest≤fresh_confirmation≤decision; source flip only after its current evidence. |
| Bars / event membership | Native local executions/DOM and source area; not candle-sign delta. |
| Reset / persistence | Each distinct return/attempt; prior defense does not supply fresh confirmation. |
| known_at | At current defense and thesis-validity reread before entry. |

**Procedure:**

1. Require the established source direction and exact prior-controlled band, still valid before the current retest.
2. Observe fresh same-side defense/refill and real participation at that same band; source refresh consistency detector/record is required.
3. If buyers take and defend the short thesis's controlling extreme with source strong buying, record the actual supported flip and a later retest-long toward VWAP only when that source sequence occurs.
4. For re-entry apply the separate attempt/daily-risk checks as well. Price-change signs cannot replace signed executions.

**Printed constants and limits:** No universal refill size/pace or strong-break threshold.

**Invalid / unavailable behavior:** Old defense as new; dead thesis ignored; different band; OHLC delta; unobserved flip. Apply C04; emit `HOLE:O130:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O130-F1 — numeric fixture:** Synthetic short band [109, 110] previously defended 09:30; return 09:45 and fresh seller defense 09:47 permit an otherwise complete 09:48 candidate. If buyers instead take and defend above 110 at 09:46, current short control is false; the old 09:30 defense cannot keep it true.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_s01_refill_long/r_s01_refill_short/r_s03_second_defence/r_s08_minor_node](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-S01/S03/S07/S08 and R-F17. Persistent identities and local side/refresh joins are missing. Existing behavior is not authority over this procedure.


<a id="o131"></a>

## O131 — Price-defined microbalance continuation

**Wiki:** [Price-defined microbalance continuation](/workspace/planning/phase-1-live/wiki/microbalance.md). **Implementation mode:** source small price-balance breakout within larger thesis.

Inside the larger directional auction a small price balance forms, then strength breaks it in the thesis direction. The opposite side supplies structural risk; the pre-existing HTF objective remains the destination and later protected structure guides management. [K2345] pp.4–7.

**Not a standalone trade.** The microbalance is an execution structure in the wider thesis, not a standalone opening-range system.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Premarked microbalance bounds/formation, live larger thesis, source strength/break evidence, entry, opposite-side structural stop and prior HTF objective. |
| Outputs / units | micro_high, micro_low, width, break_at, source_strength?, stop_side_ok, objective_preexists, sequence?. |
| ET clock / interval | Microbalance completed/known before break and entry ET. |
| Bars / event membership | Actual source small price balance; no universal fixed clock box or run detector. |
| Reset / persistence | Each source microbalance formation; preserve first/current episode instead of overwriting with last winning box. |
| known_at | Formation plus source strength/break confirmation before entry. |

**Procedure:**

1. Ingest the actual small balance and compute H-L. Automatic selection remains a hole where unpublished.
2. Require strength breaking in the live larger thesis direction. A final AM close cannot supply this earlier event.
3. Check stop behind the source opposite structure and pre-existing HTF objective; later protected structure governs only later management.

**Printed constants and limits:** No fixed formation duration, breakout-strength threshold or stop buffer.

**Invalid / unavailable behavior:** Winning box selected later; final AM close; opening box substituted; new target after outcome. Apply C04; emit `HOLE:O131:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O131-F1 — numeric fixture:** Synthetic live long thesis has target 120 known at 09:20. A microbalance [100, 102] completes at 09:40, followed by a source-confirmed strong break to 103 at 09:42. Entry 103 and supplied stop 99.75 put the stop below the opposite edge of 100 and retain the pre-existing target 120. A microbalance drawn only at 10:00 cannot qualify the 09:42 decision.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_s05_microbalance](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-S05. Current price-run detection can retain the last box and final-AM close instead of the source episode. Existing behavior is not authority over this procedure.


<a id="o132"></a>

## O132 — KG1 retest and subsequent trailing

**Wiki:** [KG1 retest and subsequent trailing](/workspace/planning/phase-1-live/wiki/kg1-retest.md). **Implementation mode:** source KG1 retest case plus separate management arithmetic.

The NYAM example uses a known KG1 level, an aggressive confirmed retest, entry and trailing convexity as the trade develops. [NYAM] pp.8–9.

**Not a standalone trade.** A scenario gamma wall is not necessarily KG1, and the displayed improvement in R:R is not a new entry method. The exact KG1 and trailing engine are not disclosed.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Verified source KG1/version, retest/aggressive confirmation, initial ticket entry/stop/target, later supported stop/target actions and their times. |
| Outputs / units | kg1_known, retest_at, confirm_at, entry_sequence?, initial_reward_to_risk, later_reward_to_risk, management_records. |
| ET clock / interval | KG1 known≤retest≤aggressive confirmation≤decision; later trailing/target changes only at later decisions. |
| Bars / event membership | Source level and actual execution/management records; no proprietary KG1/trailing reconstruction. |
| Reset / persistence | Each source KG1 case/position; original risk denominator remains stored. |
| known_at | Each level/action from contemporaneous source evidence. |

**Procedure:**

1. Ingest KG1 under its source identity; a generic gamma wall cannot replace it.
2. Require actual aggressive retest confirmation before entry, with parent thesis/risk gates.
3. For each supplied ticket compute directional target-distance/stop-distance using the actual contemporaneous prices, separately preserving initial risk. The figures'0.69→1.83 also involves target expansion; do not attribute all improvement to stop tightening.
4. Missing automatic KG1 or trailing algorithm remains a hole; literal supplied actions are still auditable.

**Printed constants and limits:** Source displayed 0.69→1.83 is case evidence, not a trailing formula.

**Invalid / unavailable behavior:** Gamma wall alias; future trail as entry; original risk rewritten; ratio change attributed only to stop. Apply C04; emit `HOLE:O132:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O132-F1 — numeric fixture:** Synthetic long entry 100, initial stop 90, target 106.9 gives 6.9/10=0.69. Later stop 95, target 109.15 gives 9.15/5=1.83. Both reward distance and stop distance changed; original risk stays 10 points. This arithmetic does not reproduce an unpublished trailing engine.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Generic gamma, level and refill ingredients attach; the previous formula labels R-S01 and R-R01 are partial surroundings. The KG1 engine and full trailing-convexity algorithm are missing. Existing behavior is not authority over this procedure.


<a id="o133"></a>

## O133 — Deliberate pre-confirmation attempts

**Wiki:** [Deliberate pre-confirmation attempts](/workspace/planning/phase-1-live/wiki/early-attempts.md). **Implementation mode:** source case-description only; repeatable full selector hole.

The K18 recap records small B+ pre-file attempts with a cheap buffer before full confirmation; a loss can leave the larger thesis alive. The OFM schematic separately permits an earlier refill return entry with greater risk than the confirmed drive/retest. [K18] pp.5–6, 14; [OFM] p.6.

**Not a standalone trade.** These source cases are not passes of the later confirmed-refill/OFM predicate. Their repeatable early-entry selector is unpublished.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Actual K18B+ or OFM early-refill case, live thesis, deliberate pre-confirmation choice recorded before entry, predeclared risk/stop, later outcome/thesis state. |
| Outputs / units | case_fidelity?, deliberate_early=true, full_confirmed_branch_pass=false, automatic_early_admission=null. |
| ET clock / interval | Early decision before the full confirmation; its intention and risk must already be known. |
| Bars / event membership | Source episode records and partial local evidence; no fabricated missing later stages. |
| Reset / persistence | Each deliberate early attempt; loss can leave thesis alive under its separate death rule. |
| known_at | At actual predeclared early choice/risk and live-thesis evidence. |

**Procedure:**

1. Keep K18 small B+ pre-file attempt and OFM earlier refill-return choice separately labeled; do not combine them into a universal early trigger.
2. Audit whether thesis was alive, choice was deliberately early and risk was specified before action.
3. Always leave the unpublished repeatable admission selector as a hole. Such a case cannot count as a pass of confirmed-refill or confirmed-drive/retest merely because it later wins.

**Printed constants and limits:** No published universal small-risk fraction or early-entry selector.

**Invalid / unavailable behavior:** Later confirmation backdated; small size excuses missing gates; early win promoted to confirmed pass. Apply C04; emit `HOLE:O133:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O133-F1 — numeric fixture:** Synthetic source early entry at 09:40, risk of 1 point declared at 09:39, and full confirmation first available at 09:45: the deliberate-early case can match its disclosed description. The confirmed-entry branch fails for this 09:40 attempt because its required confirmation is observed to arrive later. A loss at 09:42 does not by itself kill a thesis whose structural death level remains untouched.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-S01/S03/R-F15 provide surrounding components; a full repeatable early-admission rule is missing. Existing behavior is not authority over this procedure.


<a id="o134"></a>

## O134 — Third support test without new buyer defense

**Wiki:** [Third support test without new buyer defense](/workspace/planning/phase-1-live/wiki/third-retest-attempt.md). **Implementation mode:** NYAM source-case description; no universal third-touch trade.

The NYAM example shows earlier tests of one support band, no fresh buyer defense on the third, then a small short with a stop just above and a stop-out. The source explicitly denies a memorized third-touch guarantee. [NYAM] pp.6–7.

**Not a standalone trade.** Three touches are not a standalone pattern, and losing source cases must not disappear from the record.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | One fixed support band, three distinct prior/current test episodes with departures, actual lack of fresh buyer defense on third, small short ticket and later stop-out record. |
| Outputs / units | distinct_test_count, current_test_ordinal, no_new_buyer_defense?, case_fidelity?, automatic_entry_selector=null. |
| ET clock / interval | Tests ordered before third-test short; current no-defense evidence observed before decision. |
| Bars / event membership | Actual local touch/DOM records; not adjacent bars counted as independent tests. |
| Reset / persistence | Same source support band; every distinct test requires departure/return under C05. |
| known_at | At third test's actual evidence; later stop-out is a separate outcome. |

**Procedure:**

1. Count distinct same-band episodes, not rows. Require current ordinal 3 for this literal source case.
2. Validate actual no-new-buyer-defense observation; hard-coded zero defense volumes do not prove it.
3. Retain the small short and its losing outcome. General third-touch entry qualification remains a source hole, because the source explicitly rejects a memorized third-touch guarantee.

**Printed constants and limits:** Third distinct test only as case identity; no universal third-touch probability or size.

**Invalid / unavailable behavior:** Three bars as three tests; zero-default defense; loss omitted; third touch guarantee. Apply C04; emit `HOLE:O134:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O134-F1 — numeric fixture:** Synthetic tests A 09:30, B 09:45, C 10:00 with intervening departures give current ordinal 3. Three inside-band rows at 10:00 under C remain one test. Source short entry 100, stop 100.5 and later stop-out retain a losing case; that outcome does not erase it from the supplied cohort.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_s02_third_retest](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-S02. Adjacent touch bars and hard-coded zero defense volumes do not reproduce the case. Existing behavior is not authority over this procedure.


<a id="o135"></a>

## O135 — Late small resistance-fade case

**Wiki:** [Late small resistance-fade case](/workspace/planning/phase-1-live/wiki/late-resistance-fade.md). **Implementation mode:** late NYAM source-case description; automatic exhaustion selector hole.

The later NYAM case describes a premarked resistance area, upward approach losing aggression candle by candle, a small short near the session objective and ending the session. [NYAM] pp.10–11.

**Not a standalone trade.** The example does not publish a universal exhaustion threshold or complete automatic fade rule. Caption shorthand cannot override the actual direction of the chart sequence.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Premarked resistance, actual upward approach/candle sequence, source losing-aggression evidence, small short choice, session objective/context and end-session record. |
| Outputs / units | resistance_known, approach_at, source_exhaustion?, short_case_fidelity?, session_end_at, automatic_entry_selector=null. |
| ET clock / interval | Late source sequence at its actual ET times; resistance and small-risk choice before entry. |
| Bars / event membership | Source candle-by-candle local participation; no generic later high/final reversal detector. |
| Reset / persistence | Per cited late case/session objective. |
| known_at | After observed participation loss and before actual short decision. |

**Procedure:**

1. Preserve the actual chart's upward approach to resistance and short direction, even if caption shorthand is ambiguous.
2. Retain source candle-by-candle aggression loss, small risk choice and session end. No exact universal exhaustion threshold is supplied.
3. Do not force strict reward/retest gates onto this incomplete case or turn a later final-session reversal into its missing admission rule.

**Printed constants and limits:** No universal late clock, exhaustion threshold or small-risk fraction.

**Invalid / unavailable behavior:** Final high as preplanned resistance; caption overrides chart; strict branch borrowed; detector invented. Apply C04; emit `HOLE:O135:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O135-F1 — numeric fixture:** Synthetic resistance 110 marked 12:00, upward approach 109→110 after 14:00, source declining aggression observations 14:03/14:04, small short 14:05 and session end 14:20 preserve a supplied case. A resistance only drawn 14:30 cannot qualify that 14:05 entry. Automatic full trigger remains null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-S01/S07 have related area/risk pieces; the complete source admission detector is missing. Existing behavior is not authority over this procedure.


<a id="o136"></a>

## O136 — Green Bird's directional read

**Wiki:** [Green Bird's directional read](/workspace/planning/phase-1-live/wiki/directional-bias.md). **Implementation mode:** Green Bird source direction and causal revision ledger.

A prior day/week/month or session reclaim can establish direction for later aligned trades; the explicit VWAP continuation instead follows a close above both session highs. The smaller scalp posts retain a directional read with limited ambition. [GB] pp.25, 31–35, 40.

**Not a standalone trade.** A directional opinion is not an entry, and a later NYAM sweep is not required to explain a separately cited earlier prior-level reclaim.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source reference/context, actual supporting reclaim/break, declared side and availability, source change-of-view evidence, linked candidate IDs. |
| Outputs / units | bias_side, bias_start, bias_known_at, origin_reference_id, revision_history, automatic_bias_selector=null where undisclosed. |
| ET clock / interval | Supporting prior day/week/month/session reclaim before later aligned entry; VWAP continuation uses its own above-both-session-highs sequence. |
| Bars / event membership | Actual selected source confirmation bars/events; not final profitable direction. |
| Reset / persistence | Explicit new source bias/reference revision; no automatic reset from an unrelated later NYAM sweep. |
| known_at | At completed supporting reclaim/break plus contemporaneous source direction record. |

**Procedure:**

1. Bind the direction to the actual known source reference and event that supports it. Preserve a prior-level reclaim that occurs before the later NYAM setup.
2. Check the candidate side agrees with the applicable source directional read where that method requires alignment.
3. The smaller scalp method lacks a full trigger/invalidation selector. Direction alone cannot fill those holes or define an automatic trade.

**Printed constants and limits:** No universal direction score, expiry or bias reversal threshold.

**Invalid / unavailable behavior:** Later winner determines bias; later NYAM sweep required for earlier reclaim; bias alone entry. Apply C04; emit `HOLE:O136:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O136-F1 — numeric fixture:** Synthetic PDL 100 reclaimed by a completed 09:15 source confirmation; long bias known 09:15 can support a 09:40 aligned pullback. A 10:05 NYAM sweep is not required to explain that earlier bias and cannot establish it retroactively. A 09:10 entry cannot use 09:15 confirmation.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_levels/family_fail and the previous formula labels R-G01–G11 supply ingredients. A persistent source bias/reclaim ledger is missing. Existing behavior is not authority over this procedure.


<a id="o137"></a>

## O137 — Declared model and review version

**Wiki:** [Declared model and review version](/workspace/planning/phase-1-live/wiki/model-definition.md). **Implementation mode:** immutable declared process/version contract.

Sires's coaching blueprint defines the product, allowed features, regimes and account box before the daily process, then changes one variable over a block of observations. Stoic likewise fixes a reproducible process before collecting data. [AVG] pp.17–20, 27–30; [DATA] pp.3–4.

**Not a standalone trade.** A list of features is not an entry system; changing the definition after seeing winners invalidates the comparison.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author/process ID, version, products, allowed features/context/regimes, inclusion/risk constraints, frozen_at, review block and explicit revision. |
| Outputs / units | model_version, definition_hash, frozen_at, observation_ids, revision_parent, changed_fields[]. |
| ET clock / interval | Definition frozen before its observation block; revisions use only completed earlier evidence. |
| Bars / event membership | No bar algorithm; binds all downstream observations to their applicable recipe/source versions. |
| Reset / persistence | New declared version at actual revision time; earlier observations retain their original version. |
| known_at | Actual definition/revision recording time, not a retroactive label. |

**Procedure:**

1. Serialize the complete declared process and hash it deterministically under a declared encoding. No missing feature list is filled from later winners.
2. Associate every observation with the version active when it was admitted. Freeze each review block before outcomes.
3. For the source coaching one-variable revision, compute the changed-field set and require exactly the one declared experimental variable; administrative version/timestamp changes do not count as strategy changes.
4. No experiment, optimization or classifier training is run by this Phase 1 pack.

**Printed constants and limits:** One declared variable changed per source review block; no prescribed block length where absent.

**Invalid / unavailable behavior:** Version rewrites earlier rows; outcome-selected features; multiple variables labeled one; undefined review block. Apply C04; emit `HOLE:O137:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O137-F1 — numeric fixture:** Synthetic v 1 frozen 09:00 allows features A/B; v 2 next day changes only threshold T from a supplied 1 to supplied 2. changed_fields=[T], count 1. If feature C and T both change, count 2 fails the one-variable review claim. The numbers 1/2 are fixture inputs, not new trading thresholds.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** slice/compute/stats/report are generic support; the previous formula labels has no complete versioned author-process object. Model version, rule-breach and revision ledgers are missing. Existing behavior is not authority over this procedure.


<a id="o138"></a>

## O138 — Thesis, validity band and death condition

**Wiki:** [Thesis, validity band and death condition](/workspace/planning/phase-1-live/wiki/thesis-lifecycle.md). **Implementation mode:** source conditional thesis and first-death state machine.

Sires forms a thesis, states where it dies, trades while it lives and recreates it after invalidation. Structure break, value migration or new information can end it. The unnamed member writes a conditional reaction thesis; the Refill study's touch grade remains aligned with a thesis rather than becoming an independent entry. [C1] pp.3–6; [ANAT] pp.4, 7–10; [K10] pp.5, 7, 12; [OFM] pp.15–18.

**Not a standalone trade.** A stop-out does not automatically kill the wider thesis, and a live thesis does not authorize every new entry. The member and study do not inherit an undisclosed identical quantitative death algorithm.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Thesis ID/author/version, direction/conditional read, validity band, objective, explicit source death conditions, known_at, ordered structure/value/news events, replacement link. |
| Outputs / units | state:unavailable/alive/dead/unknown, first_death_at?, death_reason?, replacement_id?, alive_at_decision?. |
| ET clock / interval | Thesis declared before use; each death input uses actual information availability in ET. |
| Bars / event membership | Source-specific structure/close, developing value and news records; no universal detector. |
| Reset / persistence | Only a new explicitly formed thesis after death/reassessment. Stop-out alone does not reset or kill it. |
| known_at | State at evaluation uses only death-condition observations available by that time. |

**Procedure:**

1. Register each explicit death condition with its source producer, comparison and evidence scope. Missing condition definition/required observations gives unknown state rather than assumed alive.
2. Replay conditions chronologically. The first observed true death condition makes the thesis dead from that key onward; retain it even if price later recovers.
3. Before death, alive is true only if all required conditions are observed false through the evaluation scope. Do not hard-code news_change or value_migration false.
4. A stopped entry can leave the broader band/thesis alive, but each new entry needs fresh branch confirmation. A dead thesis requires a separately recorded replacement.

**Printed constants and limits:** No universal price buffer, value migration threshold or news-death mapping.

**Invalid / unavailable behavior:** Stopout equals death by default; dead thesis revived silently; unknown news false; future event extends validity. Apply C04; emit `HOLE:O138:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O138-F1 — numeric fixture:** Synthetic long thesis with explicitly supplied death rule complete 5 minute close<100: a 10:00 close 99 makes first_death10:00. Recovery 102 at 10:10 does not revive it. An entry stopped at 101 at 09:50 does not alone kill that thesis. Missing required news coverage makes overall alive status unknown before price death, unless an independent observed death already makes it false.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_r03_thesis](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-R03, R-S03/S07/S08. Hard-coding news/value changes away is incomplete; first-invalidation and persistent band state are missing. Existing behavior is not authority over this procedure.


<a id="o139"></a>

## O139 — Entry-side structural invalidation

**Wiki:** [Entry-side structural invalidation](/workspace/planning/phase-1-live/wiki/structural-risk.md). **Implementation mode:** source entry-side invalidation geometry and timing.

Where the source supplies it, controlling structure determines invalidation before size is chosen. Sires explicitly works from stop structure to account risk and real HTF objective; Jumbo and Green Bird keep case-specific block/swing stops. Some cases disclose only an example distance or an incomplete rule. [ANAT] pp.8–10; [TBR] pp.27–29; [GB] pp.25, 31–34, 40; [TRAP] pp.8–10; [K10] pp.7–9; [AVG] pp.21–22.

**Not a standalone trade.** An attractive R:R does not justify inventing a structure. A ticket's 30-point stop or a screenshot boundary is not a universal stop for that method.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Candidate side/entry E, source controlling band/extreme and confirmation, stop/invalidation S with wick/close rule, q, actual-order versus drawing provenance. |
| Outputs / units | structural_stop, stop_distance_points=d*(E-S), stop_distance_ticks=distance/q, stop_side_ok, risk_known_before_entry, policy_holes[]. |
| ET clock / interval | Source invalidation and geometry selected before decision; event-based breach later. |
| Bars / event membership | Actual source block/swing/defense structure and chosen wick/close confirmation. |
| Reset / persistence | Each entry ticket and source policy; later stop changes are management records, not initial-risk rewrites. |
| known_at | Maximum structure confirmation and stop-policy selection before entry. |

**Procedure:**

1. Set direction d=+1 for long,-1 for short. Risk distance d*(E-S) must be positive for an ordinary adverse stop; zero/negative distance is not valid initial adverse risk.
2. Check the actual source relationship to the controlling structure and its exact crossing/close rule. A stop beyond a sweep, block midpoint, candle low or ticket distance belongs only to its source case.
3. Keep drawn risk boxes separate from actual order evidence. If the source does not settle a general stop rule or caption/figure conflict, return the policy hole; do not choose a universal 30 point or extra tick stop.
4. C06 observes later invalidation only under this frozen rule.

**Printed constants and limits:** No universal stop distance/buffer; q from instrument definition.

**Invalid / unavailable behavior:** Wrong side stop; future structure; wick/close swapped; drawn box claimed order; case distance generalized. Apply C04; emit `HOLE:O139:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O139-F1 — numeric fixture:** Synthetic long E105, S100, q 0.25 gives risk 5 points=20 ticks; short E105, S110 also 5 points=20 ticks. Long S106 gives negative distance and invalid initial adverse stop. A five-minute-close-below 100 policy is not breached merely by an intrabar 99.75 trade if the completed close is 100.25.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.j18_ob_bull/j18_ob_bear](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_s01_refill_long/r_s01_refill_short/r_s07_areas](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-J18/R-S01/R-S07 and GB ingredients. Complete source-linked risk records are missing. Existing behavior is not authority over this procedure.


<a id="o140"></a>

## O140 — Exposure fitted to source risk constraints

**Wiki:** [Exposure fitted to source risk constraints](/workspace/planning/phase-1-live/wiki/position-sizing.md). **Implementation mode:** literal source exposure arithmetic and constraint audit; no universal sizing policy.

The sources connect exposure to stop distance, case quality and account limits. Jumbo reduces ambition/risk in difficult context and allocation after repeated failure; Sires fits size after structure and adds only when earlier risk is secured. Stoic's overlay uses its separate printed ladder. [TBR] pp.24, 37; [GB] pp.37–40; [ANAT] pp.8–10; [K18] pp.11–14; [K10] pp.4–9; [REF] pp.12, 19–21; [DATA] pp.7–8.

**Not a standalone trade.** Sizing does not create an entry or cure missing confirmation. Research risk scenarios and one account's contract count are not universal presets.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source account policy/capital/risk cap, pre-entry structural distance, instrument multiplier/tick value, actual quantity, applicable costs, existing exposure and source quality/allocation rule. |
| Outputs / units | unit_risk_money, position_risk_money, aggregate_risk_money, cap_ok?, quantity_policy_ok?, missing_units[]. |
| ET clock / interval | Structure and source risk policy before size choice; prior exposure state before entry/add. |
| Bars / event membership | Ticket/account/definition records; no P&L simulation. |
| Reset / persistence | Source account/risk day or policy version; current positions persist until observed actions change them. |
| known_at | All capital, structure, multiplier and exposure facts before the action. |

**Procedure:**

1. For a verified multiplier M in currency per price point and stop distance D>0, unit risk=D*M; equivalently stop_ticks*tick value when tick value is verified. Do not infer a missing multiplier from product familiarity.
2. Multiply unit risk by actual quantity and add only costs/reserves explicitly included by the source risk policy. Aggregate simultaneous exposure under the actual policy; correlated risk aggregation is a hole if not specified.
3. Audit against the predeclared cap and source allocation/quality rule. If a source explicitly calls for integer-contract maximum size under a cap, quantity=floor(cap/unit risk), adjusted only for its stated cost/exposure policy; otherwise audit supplied size without inventing an allocator.
4. Adds require earlier risk secured under the source management rule. Smaller size cannot convert missing confirmation into pass. Stoic's ladder and research brackets remain separate objects.

**Printed constants and limits:** No universal capital percentage/contract count. Jumbo's at-least 50% post-failure allocation reduction is scoped to its own recipe.

**Invalid / unavailable behavior:** Missing multiplier guessed; negative D; research risk pooled with account policy; unsecured add; size excuses invalid entry. Apply C04; emit `HOLE:O140:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O140-F1 — numeric fixture:** Synthetic explicitly supplied D2 points, M10 currency/point, quantity 3 gives unit risk 20 and position risk 60. With a supplied cap 50, cap_ok=false; under an explicitly supplied integer-max allocator, floor(50/20)=2 contracts. If M is null, money risk and derived quantity are null, even though D2 is known.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Some r_s01/r_s07 ticket-distance helpers exist; the previous formula labels R-S01/S07, R-J21/J24. Event-linked sizing, account constraints and aggregate exposure are missing. Existing behavior is not authority over this procedure.


<a id="o141"></a>

## O141 — Objective selected before entry

**Wiki:** [Objective selected before entry](/workspace/planning/phase-1-live/wiki/trade-objective.md). **Implementation mode:** pre-entry source destination and post-decision outcome binding.

The method selects a real destination: range/internal/opposing liquidity, POC/shelf/value, prior control, or the study's declared bracket. Sires fits reward to the HTF objective; Green Bird's VWAP post reports a result without publishing a general target-selection rule. [TBR] pp.8–24; [GB] pp.30–40; [ANAT] pp.8–10; [RTVP] pp.5–8; [REF] p.12.

**Not a standalone trade.** A later high/low or reported 150-point result cannot become the assumed planned target. A destination does not supply the entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Objective ID/type/bounds, source side/scope/priority, original known_at, selection key, entry association and source outcome window/invalidation. |
| Outputs / units | selected_objective, target_distance_points?, objective_preknown, active_at_selection?, later_outcome, policy_holes[]. |
| ET clock / interval | Objective selected before entry where the method requires it; reach only strictly after decision. |
| Bars / event membership | Target parent's own geometry and later ordered source price path. |
| Reset / persistence | Each selected objective/entry association; later justified target change creates a new management record. |
| known_at | Original reference and selection availability, before the decision using it. |

**Procedure:**

1. Require the actual source destination: named range/liquidity, POC/value/shelf, prior control or a declared study bracket. Bind its exact object ID and source priority.
2. For a supplied point target T and entry E calculate directional distance d*(T-E). For a band retain near/far contact distinctions; do not choose one favorable endpoint later.
3. Apply the unfinished-objective ledger at selection and C06 after entry. Missing target algorithm is a hole even if the source reports a later gain.
4. Green Bird's reported 150 point result in the VWAP post is an outcome, not a universally preplanned target.

**Printed constants and limits:** No nearest-target, fixed point result or outcome horizon default.

**Invalid / unavailable behavior:** Later high/low as target; reported result as plan; consumed objective without source permission; pre entry hit counted. Apply C04; emit `HOLE:O141:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O141-F1 — numeric fixture:** Synthetic long E100, target 104 selected 09:40 before entry 09:41 gives distance 4 points. A104 print 09:39 is not a post-entry hit; 10:00 print 104 is. Replacing target with later high 110 after seeing it violates selection timing.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_levels; [formulas_jumbo.j10_draw/j19_draw/j21_targets](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); the previous formula labels R-J10/J19/J21, R-A03/A05/A06 and R-G01–G09. Full entry-linked selection and progression are missing. Existing behavior is not authority over this procedure.


<a id="o142"></a>

## O142 — Source-selected position management

**Wiki:** [Source-selected position management](/workspace/planning/phase-1-live/wiki/position-management.md). **Implementation mode:** source action ledger and supported policy audit.

Management follows the entry and the chosen source policy: static objectives, partials, breakeven, trailing or justified additions. Sires distinguishes account-dependent exit policies; NYAM shows target expansion as well as trailing, with the original risk box still drawn. [C2] pp.3–7; [C3] p.4; [NYAM] pp.8–9; [K18] pp.8–14; [TBR] pp.24, 36–37; [GB] pp.30–40; [REF] p.12.

**Not a standalone trade.** Management is not another entry system, and a later stop/target adjustment cannot rewrite the original ticket. No universal algorithm is inferred where the source gives only a case.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Entry ID, immutable initial stop/target/risk/policy, actual partial/BE/trail/add/exit actions, quantities, supporting confirmed structure and exposure state. |
| Outputs / units | management_actions[], position_quantity_after, stop/target_versions, action_policy_ok?, initial_risk_unchanged, exit_reason. |
| ET clock / interval | Actions after entry; supporting evidence known by each action. No whole-AM excursion before entry. |
| Bars / event membership | Observed order/ticket actions and source confirmed structure; no simulated orders. |
| Reset / persistence | Each observed position lifecycle; initial values remain immutable through all updates. |
| known_at | Action at actual time; supporting structure at its confirmation time. |

**Procedure:**

1. Choose the source account/case policy before entry: static target, partial, breakeven, trail or justified add. Undisclosed general policy remains a hole.
2. Replay observed actions in order. Partials reduce quantity by the observed filled amount; a requested partial without fill does not.
3. For structural trailing require the protected reference to be confirmed before stop action. For adds require the source condition that earlier risk is secured and recalculate actual exposure.
4. Keep target expansion separate from stop tightening and preserve initial risk. Do not infer an algorithm from one displayed R:R change.

**Printed constants and limits:** Only the selected source policy; no universal partial fraction, BE trigger or trailing distance.

**Invalid / unavailable behavior:** Unconfirmed trail; requested quantity as fill; unsecured add; original risk rewritten; future excursion before entry. Apply C04; emit `HOLE:O142:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O142-F1 — numeric fixture:** Synthetic position 3 contracts entered 09:40; observed partial fill 1 at 09:50 leaves 2. A requested partial 1 with no fill leaves 3. Protected high confirmed 10:00 cannot support a 09:55 stop trail; a 10:01 action may use it under the selected policy. Initial risk 5 points remains 5 after the stop moves.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_jumbo.j24_management](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_f10_protected_low](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) and related R-S helpers; the previous formula labels R-J24/R-F10/R-S01/S05/S07. Complete action and position-exposure ledgers are missing. Existing behavior is not authority over this procedure.


<a id="o143"></a>

## O143 — Confirmed protected high or low

**Wiki:** [Confirmed protected high or low](/workspace/planning/phase-1-live/wiki/protected-high-low.md). **Implementation mode:** source confirmed control structure for later management.

Protected structure follows demonstrated control. In the K18 short, the prior low must break and close with real aggression before the intervening high is treated as protected for trailing. The low-side lesson similarly links protection to defended control and reward. [K18] pp.8–14; [RD] pp.4–7.

**Not a standalone trade.** An unconfirmed wick or final-AM extreme is not a protected stop reference. The high-side mirror must be bound to actual source evidence.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source pivot/intervening extreme, price-time and source selection, controlling band, later required prior low/high break and completed close with real aggression, stop action. |
| Outputs / units | protected_price, price_at, confirmation_at, protected_known_at, side, trail_allowed_at?. |
| ET clock / interval | Pivot price first; source break/close/aggression confirmation later; management after confirmation. |
| Bars / event membership | Actual source timeframe and signed executions; no automatic fractal length or final-AM extreme. |
| Reset / persistence | Each newly confirmed protected structure; earlier structures remain in history. |
| known_at | Maximum required confirming break/close and aggression availability, never pivot price time. |

**Procedure:**

1. For the K18 short, preserve the intervening high and require the prior low to break and close with actual source aggressive selling before labeling that high protected.
2. For the low-side lesson use its own demonstrated defended control/reward sequence; do not assume a fully defined symmetric detector from one side.
3. If pivot/confirmation/strength conventions are absent, emit the corresponding hole. A wick alone does not establish protection.
4. A stop action can reference the protected structure only after protected_known_at.

**Printed constants and limits:** No universal pivot length, aggression threshold or stop buffer.

**Invalid / unavailable behavior:** Pivot backdating; wick only confirmation; price-sign as delta; unsupported mirror; final high. Apply C04; emit `HOLE:O143:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O143-F1 — numeric fixture:** Synthetic short: intervening high 110 priced 09:40; prior low 105 breaks and source candle closes 104 with verified selling at 09:50. Protected high 110 becomes known 09:50, not 09:40. A 09:45 trail using it fails causality; 09:51 can use it if the selected policy permits.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [formulas_flow.r_f10_protected_low](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F10 and R-S01/S05/S07. High-side symmetry and event-time confirmation are incomplete. Existing behavior is not authority over this procedure.


<a id="o144"></a>

## O144 — Freshly qualified re-entry

**Wiki:** [Freshly qualified re-entry](/workspace/planning/phase-1-live/wiki/reentry.md). **Implementation mode:** new attempt with persistent thesis/band and full fresh qualification.

A stop-out can leave the wider thesis/band intact, but a new entry requires return inside that same band and fresh selected-branch confirmation. The location, reward/result and delta checks are rerun from zero. [ANAT] pp.7, 10; [STOP] pp.6, 14–15; [CONT] pp.8–10.

**Not a standalone trade.** Prior confirmation is not reusable entry permission, and calling a trade a re-entry does not reset a daily stop. A dead thesis needs a new thesis.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Parent entry/exit, new candidate ID, same live thesis/band, actual return, fresh selected-branch evidence after exit, current daily/account permission. |
| Outputs / units | parent_exit_at, new_candidate_id, same_thesis_band, fresh_confirmation_at, full_branch_verdict, reentry_permission?. |
| ET clock / interval | prior_exit<fresh_confirmation≤new decision, plus actual return and the entire selected branch's order. |
| Bars / event membership | New local source events; prior confirmation IDs cannot be reused. |
| Reset / persistence | Reset local entry checks to a fresh attempt; do not reset thesis, band or daily losses by renaming. |
| known_at | At new fresh confirmation and current risk-state check before decision. |

**Procedure:**

1. Confirm the prior attempt actually exited and create a distinct new candidate linked to it.
2. Require the same still-valid source band and thesis, actual return into the source area and all fresh selected-branch stages. A dead thesis requires a new thesis record.
3. Apply current account/session stop and exposure rules with prior losses intact. Unknown fresh evidence remains unknown.
4. Count and retain every new attempt, including another loss; do not collapse repeated re-entries into one winner.

**Printed constants and limits:** No automatic cooldown, retry count or risk reset unless the selected source says so.

**Invalid / unavailable behavior:** Prior confirmation reused; reentry name erases losses; dead thesis; new band without declaration. Apply C04; emit `HOLE:O144:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O144-F1 — numeric fixture:** Synthetic first exit 09:45, new return 09:50, fresh confirmation 09:52, new entry 09:53 satisfies the temporal re-entry condition. Reusing confirmation 09:40 fails freshness. Under STOP daily R=-4, the new entry is blocked even if every fresh local stage is present.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-R03/R-S03/R-S07/R-S08 are ingredients. Persistent thesis/band identities, distinct attempts and loss-limit state are missing. Existing behavior is not authority over this procedure.


<a id="o145"></a>

## O145 — Source account and session stop

**Wiki:** [Source account and session stop](/workspace/planning/phase-1-live/wiki/daily-loss-limit.md). **Implementation mode:** source account/session permission from pre-action ledger.

The sources limit further exposure after adverse results or when the planned session is finished. STOP's illustrated rule forbids another entry at −4R; other recaps/account examples retain their own constraints and inconsistent example dollar amounts. [STOP] pp.14–15; [ANAT] pp.5, 11; [TBR] p.37; [GB] pp.37–40; [K10] pp.4–5; [DATA] p.8.

**Not a standalone trade.** One account's −4R, dollar cap or contract count is not a universal author limit. A session stop is not an entry signal.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author/account policy/version, source day/reset, observed prior results in policy units, remaining risk, session-end declaration and next attempt key. |
| Outputs / units | daily_R_before?, policy_limit, session_finished, entry_permission?, rule_breach, ledger_ids. |
| ET clock / interval | Only prior resolved account outcomes available before attempted entry; actual source account-day reset. |
| Bars / event membership | Supplied account/attempt records, not newly simulated P&L. |
| Reset / persistence | Source account day or explicitly stated policy boundary; re-entry does not reset it. |
| known_at | Each observed result at its resolution/availability; policy must predate attempt. |

**Procedure:**

1. Aggregate prior supplied results in the same source R/currency convention, preserving losses and policy version. Missing account ledger or R definition gives unknown.
2. For STOP's selected branch require daily_R_before>-4. At exactly-4 another entry is forbidden. Other sources retain their own caps/units and unresolved inconsistent dollar examples.
3. If the source declares the session finished, later attempts fail that session permission unless an explicit new applicable session/policy exists.
4. Do not change the policy retroactively to erase a breach.

**Printed constants and limits:** -4R belongs to STOP's source variant, not every method/account.

**Invalid / unavailable behavior:** Global-4R; losses erased; currency/R mixed; later policy backdated; missing ledger as zero. Apply C04; emit `HOLE:O145:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O145-F1 — numeric fixture:** Synthetic supplied day results-1R,-1R,-2R sum-4R before next attempt; STOPentry_permission=false. At-3.5R it is true for this limit alone. A missing prior result prevents assuming 0R; a separate source dollar cap cannot be compared directly with-4R.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-J22/R-J24/R-S07 have related flags. A persistent account/attempt ledger is missing. Existing behavior is not authority over this procedure.


<a id="o146"></a>

## O146 — Thesis and execution journal

**Wiki:** [Thesis and execution journal](/workspace/planning/phase-1-live/wiki/process-journal.md). **Implementation mode:** complete versioned observation and review ledger.

Sires's codex records bias/validity times, reason and confidence, every trade, regime, changes and rule breaches; the coaching review pauses replay before entry and changes one variable over a block. The member's written thesis and Stoic's uniform aggregate collection are separately attributed applications. [C1] pp.6–7; [AVG] pp.27–30; [EMO] pp.6–8; [K10] pp.3–5, 10–15; [DATA] pp.3–4.

**Not a standalone trade.** A payout screenshot or selected winner is not process evidence. Recorded profitability does not repair a missing entry prerequisite.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Author/process version, thesis/candidate IDs, pre-entry reason/confidence, context/regime, every eligible attempt/miss/breach, observed outcomes/costs and later review revisions. |
| Outputs / units | journal_rows, pre_entry_fields_valid, eligible_ids_accounted_for, missing_ids, breach_records, review_links. |
| ET clock / interval | Pre-entry rationale at its actual time; later explanation/review separate. |
| Bars / event membership | References native market evidence without replacing it with payout screenshots. |
| Reset / persistence | Each declared process/version/review block; earlier rows immutable. |
| known_at | Each field keeps its own availability; a later journal note is not assumed contemporaneous. |

**Procedure:**

1. Join every ID in the frozen eligible cohort to its journal row, including losses, misses, invalid attempts and rule breaches.
2. Separate original reason/confidence from later explanation and result. A source screenshot or payout alone cannot supply missing pre-entry rationale.
3. Bind review changes to completed earlier evidence and a new model version. Recorded profitability cannot repair a failed entry sequence.

**Printed constants and limits:** No invented confidence scale, review block length or acceptable breach count.

**Invalid / unavailable behavior:** Selected winners only; later explanation backdated; version rewrite; missing attempts. Apply C04; emit `HOLE:O146:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O146-F1 — numeric fixture:** Synthetic frozen eligible IDs[A, B, C] with journal Awin, Cwin and B missing gives accounted 2 of 3, missing[B]; completeness false. Adding B's loss makes 3 of 3 without changing A/C. A reason recorded 10:00 for 09:40 entry is later explanation unless independent pre-entry evidence exists.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** stats/report/compute provide generic summaries/storage; no full author journal exists in the previous formula labels or current operator objects. Existing behavior is not authority over this procedure.


<a id="o147"></a>

## O147 — Triad AMT-object first use: IØD and RFZ

**Wiki:** [Triad AMT-object first use: IØD and RFZ](/workspace/planning/phase-1-live/wiki/correlated-object-first-use.md). **Implementation mode:** source-corresponding native AMT-object timing and thesis revision.

C1 compares ES, NQ and YM reacting to their corresponding AMT objects at different speeds. In IØD, YM's prior-balance test/rejection changes the ES reaction read. RFZ, Reactive Fill Zone, describes a correlated asset filling the corresponding single-print objective first, requiring reassessment of the remaining target. [C1] p.5.

**Not a standalone trade.** This is native-object timing and reaction, not generic same-price divergence or a separate entry system. Raw prices of different indices are not directly comparable.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | ES/NQ/YM native corresponding object IDs/bounds/known_at, source correspondence rationale, first-use/rejection or fill events, revised thesis/target decision. |
| Outputs / units | native_first_use_times, source_object_correspondence, first_instrument?, iod_reaction_revision?, rfz_target_revision?. |
| ET clock / interval | Each object's own known_at before its use; peer event before revised decision; cross-stream ordering verified. |
| Bars / event membership | Each market's native profile/price/TPO events; no raw cross-index price comparison. |
| Reset / persistence | Per source matched triad object set/thesis version. |
| known_at | Maximum native object/event availability and verified cross-stream timing. |

**Procedure:**

1. Require explicit source correspondence between the markets' own AMT objects; arbitrary high/low disagreement is not this object.
2. For IØD preserve YM's earlier prior-balance test/rejection and the actual resulting ES reaction reread. For RFZ preserve peer first fill of the corresponding single-print objective and subsequent target reassessment.
3. Record first use only over complete covered eligible history; tied/unresolved cross-stream order yields unknown first.
4. Do not convert this context revision into a separate entry or a same-price SMT detector.

**Printed constants and limits:** ES/NQ/YM source triad; no cross-price ratio or divergence threshold.

**Invalid / unavailable behavior:** Raw index prices compared; future peer fill; arbitrary objects matched; uncertain event order tie broken. Apply C04; emit `HOLE:O147:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O147-F1 — numeric fixture:** Synthetic ES balance edge 5000, NQ edge 20000, YM edge 40000 are three native objects. Verified YM test 09:40 then ES decision 09:42 can inform the source IØD reread; numerical edge inequality is irrelevant. A peer RFZ fill 09:45 cannot revise an ES decision 09:42.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** family_flow sister-market ingredients; the previous formula labels R-R04. Source-compatible native-object matching and first-use/target-consumption logic are missing. Existing behavior is not authority over this procedure.


<a id="o148"></a>

## O148 — Frozen observation cohort

**Wiki:** [Frozen observation cohort](/workspace/planning/phase-1-live/wiki/research-cohort.md). **Implementation mode:** frozen eligible-observation and selection identity audit.

A repeatable process collects all eligible observations uniformly, then compares groups. The Refill study separates discovered touches, selected signals and actual fills; Sires reviews a declared block instead of selected winners; Stoic validates an existing process before applying the overlay. [DATA] pp.3–4, 8; [AVG] pp.27–30; [REF] pp.8–16; [K10] pp.10–15.

**Not a standalone trade.** A filtered set of profitable days is not the original opportunity set, and 64 fills versus 312 selected signals are not paired trade returns.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Process/version, source inclusion rule/frozen_at, instrument/date scope, every candidate/touch ID, selections/orders/fills, supplied split boundaries and missingness. |
| Outputs / units | cohort_hash, eligible_count, selected_count, order_count, filled_order_count, unselected_ids, split_direction, cohort_causal?. |
| ET clock / interval | Inclusion definition before observations; selection/features before each order; actual split chronology preserved. |
| Bars / event membership | No new market signal detector; joins the selected method's source-defined or supplied episodes. |
| Reset / persistence | New declared inclusion/version/split; do not rewrite an old cohort after outcomes. |
| known_at | Manifest at its freeze time; each selection at actual availability. |

**Procedure:**

1. Freeze eligible IDs or a complete causal selector before scoring. Every eligible observation remains in its original denominator, including unselected cases and misses.
2. Keep discovered touches, selected signals, orders and fills as different sets linked by explicit IDs. Distinct partial fills do not create extra signals.
3. Label forward, reverse and rotating supplied splits honestly. A reverse/rotating diagnostic is not a forward deployment estimate.
4. If the source selector is incomplete, do not create a historical cohort by arbitrary scanning. Return candidate_discovery=hole; supplied episodes remain a separate auditable cohort.

**Printed constants and limits:** No new split percentage or sample-selection threshold. Source 64 fills and 312 signals are distinct denominators.

**Invalid / unavailable behavior:** Winners only; later-day selection; unmatched cohorts compared as paired; historical selector invented. Apply C04; emit `HOLE:O148:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O148-F1 — numeric fixture:** Synthetic eligible touches 10, selected signals 6, orders 6, filled orders 4 yields counts 10/6/6/4 and 4 unselected touches. A4-fill execution sample cannot be paired row-for-row with 6 market-entry results without explicit common candidate IDs. Missing 2 selected orders from the lifecycle is a completeness failure.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** slice/compute/stats/report provide generic support. Complete source-compatible episode/selection joins are missing from the previous formula labels and operator objects. Existing behavior is not authority over this procedure.


<a id="o149"></a>

## O149 — Supplied refill-touch grade

**Wiki:** [Supplied refill-touch grade](/workspace/planning/phase-1-live/wiki/touch-grader.md). **Implementation mode:** supplied frozen grade and feature-availability audit only.

The Refill study grades an already-found zone touch using pre-touch memory, construction, location and flow. The later OFM correction retains touch grading and passive execution lessons but reports a negative fully causal mechanical entry rebuild. [REF] pp.6–10, 16; [OFM] pp.15–18.

**Not a standalone trade.** A useful grade is not an independently established profitable entry system. The earlier positive replay used later-day selection and cannot certify automatic trade admission.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Current touch ID, supplied model/version and training cutoff, feature values/transform versions, feature known_at values, score/selection threshold/comparator, grade available_at and order time. |
| Outputs / units | supplied_grade, model_known_before_use, max_feature_known_at, feature_causal, selected_by_supplied_rule?, automatic_grade=null. |
| ET clock / interval | All features, model and grade available before current order; current-touch outcome occurs later and is excluded. |
| Bars / event membership | Pre-touch source memory/construction/location/flow inputs; no new trained model or threshold search. |
| Reset / persistence | Each supplied model/version and current touch; retain unselected touches under the same cohort. |
| known_at | max(model availability, feature availability, grade output availability), no later than order. |

**Procedure:**

1. Ingest only a supplied frozen source grade. Require model provenance/training end, exact feature transformation versions and actual feature timestamps.
2. Reject leakage if any required feature uses the current touch's future hold/label, a later-day selection or post-order data. Unknown transformations/model timing create source holes.
3. If a supplied threshold and comparator exist, audit the score's selection literally; do not infer a threshold from selected examples.
4. No author grader is reconstructed. Preserve the later OFM correction: causal mechanical-entry rebuilds around-0.16R to-0.54R out of sample do not support treating the earlier positive replay as established automatic entry edge.

**Printed constants and limits:** No source-complete grade engine, threshold, hold-label or feature transformations.

**Invalid / unavailable behavior:** Current outcome in features; training cutoff later than order; later day selection; new classifier; positive claim without correction. Apply C04; emit `HOLE:O149:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O149-F1 — numeric fixture:** Synthetic supplied score 0.8, threshold 0.7, inclusive comparator, model known yesterday and all features known 09:59 for 10:00 order gives literal selection true. One feature known 10:01 makes feature_causal=false regardless of score. Remove supplied threshold: selection null, not threshold 0.5.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-F17 and profile/flow ingredients are partial inputs. The published classifier, feature transformations, hold label and threshold are missing. Existing behavior is not authority over this procedure.


<a id="o150"></a>

## O150 — Observed order lifecycle

**Wiki:** [Observed order lifecycle](/workspace/planning/phase-1-live/wiki/order-lifecycle.md). **Implementation mode:** observed/supplied instruction-to-exit lifecycle audit; no orders placed.

An entry instruction, drawn ticket, resting order, triggered order, fill, cancellation and exit are different events. OFM illustrates a stop-triggered continuation entry; the Refill study documents a passive-limit bracket and cancellation policy. [OFM] pp.11–13; [REF] pp.12, 22; [TBR] pp.27–29.

**Not a standalone trade.** A plotted bracket does not prove a fill or make its eventual target a preplanned outcome.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Candidate/order/position IDs, actual order type/price/quantity, placement/trigger/fill/cancel/expiry/amend/exit events, source initial bracket and policy. |
| Outputs / units | order_state_timeline, remaining_quantity, filled_quantity, position_open, bracket_versions, lifecycle_valid?, source_policy_ok?. |
| ET clock / interval | Decision≤placement≤eligible trigger/fill; cancellation and expiry at actual event keys. Source Refills cancellation age 30 minutes from its specified placement anchor. |
| Bars / event membership | Observed order events or explicitly modeled source records; a drawing is not an order/fill. |
| Reset / persistence | New order ID for a new order; amendments version the same order. Position state changes only through actual/supplied fill events. |
| known_at | Each lifecycle event at its actual availability; no eventual bracket result backdated. |

**Procedure:**

1. Keep instruction, drawing, resting, triggered, partially filled, filled, canceled, expired and exited states distinct. Preserve actual type-specific trigger and fill rules; do not manufacture a fill from placement.
2. For each order require 0≤cumulative filled≤placed/amended quantity under the actual amendment policy. A cancellation ends remaining working quantity but does not erase prior fills; an exit closes only its observed quantity.
3. For the documented Refill configuration retain entry 12 ticks inside the source level, stop 32 ticks, target 96 ticks, cancel after 30 minutes and one position at a time. Exact inside-edge/sign and placement-anchor conventions are not fully disclosed; require supplied order price/anchor or emit a hole.
4. Other methods keep their own stop/limit/market conventions. This Phase 1 pass validates records and source assumptions; it does not place orders or simulate a strategy.

**Printed constants and limits:** Refill 12 tick inside, 32 tick stop, 96 tick target, 30 minute cancellation, one position at a time only for that source configuration.

**Invalid / unavailable behavior:** Ticket as fill; overfill; fill after confirmed cancel without ordering explanation; second open position in Refill; inside anchor invented. Apply C04; emit `HOLE:O150:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O150-F1 — numeric fixture:** Synthetic supplied Refill long limit 100, q 0.25, placed 10:00 gives stop 92, target 124 and cancel age 30 minutes at 10:30 under an explicitly supplied placement anchor. Quantity 3 with fills 1 then 1 has filled 2/remaining 1; cancel remaining 1 leaves a 2 contract position, not 0. A reference level alone does not determine the 12 tick inside price without its edge convention.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Partial ticket geometry in [formulas_jumbo.j18_ob_bull/j18_ob_bear](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) and [formulas_flow.r_s01_refill_long/r_s01_refill_short](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-J18/R-F15/R-F17/R-S01. Full event lifecycle is missing. Existing behavior is not authority over this procedure.


<a id="o151"></a>

## O151 — Refill-study fill assumption

**Wiki:** [Refill-study fill assumption](/workspace/planning/phase-1-live/wiki/fill-model.md). **Implementation mode:** audit the declared Refill touch/trade-through assumption on supplied orders.

The study's touch-or-trade-through execution assumption determines which passive orders count as filled. A modeled touch is not proof of queue priority or real fill. [REF] pp.12, 15, 22.

**Not a standalone trade.** A fill assumption is not an entry edge, and limit-versus-market cohorts with different fill counts are not paired outcomes on identical trades.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Supplied resting order ID/side/price/placement, canonical subsequent trades, declared source fill convention, cancellation/expiry/one-position state and actual-fill evidence if any. |
| Outputs / units | first_modeled_fill_at?, modeled_fill_rule, actual_fill_at?, queue_verified=false unless evidence exists, fill_eligibility?. |
| ET clock / interval | Only trades after active placement and before effective cancel/expiry; unresolved same-key order remains unknown. |
| Bars / event membership | Ordered executed prices; OHLC containment alone may not resolve placement/fill/cancel order. |
| Reset / persistence | Per resting order; one order may have partial observed fills but a modeled source fill must retain its declared quantity assumption. |
| known_at | Modeled fill when first qualifying price event is observed; actual fill only from execution report. |

**Procedure:**

1. For the source modeled passive buy at L, qualifying trade price≤L; for passive sell at L, price≥L. Require the order was active and the source cancellation/position policy allowed it.
2. Keep a touch-or-through modeled fill distinct from an actual queue fill. Do not infer priority, partial allocation or hidden queue from touch.
3. Use explicit candidate/order IDs to retain selected-but-unfilled cases and distinguish unmatched limit/market cohorts.
4. No autonomous order strategy or new performance replay is built; this recipe audits supplied orders and their declared source execution assumption.

**Printed constants and limits:** Source touch-or-trade-through assumption; no queue priority or fill-probability model.

**Invalid / unavailable behavior:** Pre placement touch; post cancel fill; modeled as actual; unmatched fills as paired results; OHLC order invented. Apply C04; emit `HOLE:O151:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O151-F1 — numeric fixture:** Synthetic buy limit 100 active 10:00; trade 100.25 at 10:01 does not qualify, trade 100 at 10:02 gives modeled fill 10:02. Actual fill remains unknown without a fill report. If cancellation effective 10:01:30, the 10:02 trade cannot fill that active order under this assumption.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** the previous formula labels R-F17 only covers related zone/revisit ingredients. The documented order/fill lifecycle and queue model are missing. Existing behavior is not authority over this procedure.


<a id="o152"></a>

## O152 — Trading and account costs

**Wiki:** [Trading and account costs](/workspace/planning/phase-1-live/wiki/cost-model.md). **Implementation mode:** source cost-unit and supplied ticket arithmetic audit.

The coaching review compares aggregate outcomes with fees/payout economics; the member's account evaluation costs matter to his actual result. The Refill configuration uses one tick round-trip cost and one tick stop slippage. [AVG] pp.27–30; [K10] pp.3–5, 10–15; [REF] pp.12, 22.

**Not a standalone trade.** A gross chart move, payout cover or modeled bracket is not a net process result. Study costs are not universal live costs.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Instrument q/tick value if known, source round trip commission/slippage assumptions, supplied stop/win outcome geometry, account/evaluation fees and matching cohort. |
| Outputs / units | trade_cost_ticks, stop_slippage_ticks, currency_cost?, supplied_gross/net_consistency?, account_fees_separate. |
| ET clock / interval | Assumed cost policy declared before study selection; observed fees at actual availability. |
| Bars / event membership | Supplied ticket/account records; no new price-derived P&L series. |
| Reset / persistence | Per source policy/instrument/account cohort; account fees are not per trade unless explicitly allocated. |
| known_at | Actual source cost assumption or observed fee availability. |

**Procedure:**

1. Retain Refill's 1 tick round-trip cost and 1 tick stop slippage separately. Charge the extra stop slippage only on the source stop outcome, not every target outcome.
2. For supplied bracket arithmetic only, initial risk 32 ticks means a 96 tick target less 1 tick cost is 95/32R; stop 32 plus 1 slippage plus 1 cost is-34/32R. This checks stated units, not a new return series.
3. Convert ticks cost to currency only with a verified tick value and quantity. Keep evaluation/account fees in a separate ledger and do not infer net account result from gross chart movement.

**Printed constants and limits:** Refill 1 tick round trip, 1 tick stop slippage, 32 tick risk/96 tick target from the stated configuration.

**Invalid / unavailable behavior:** Cost double count; stop slippage charged to target; missing tick value guessed; account fees ignored in reported net claim. Apply C04; emit `HOLE:O152:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O152-F1 — numeric fixture:** Source-configuration arithmetic: supplied target outcome gives 95/32=2.96875R; supplied stop outcome gives-34/32=-1.0625R. These are bracket unit checks only. With supplied tick value 2 currency and quantity 3, 1 tick round trip cost=6 currency; missing tick value yields currency cost null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** stats/report have generic summaries; the previous formula labels has no full source-specific order/account cost ledger. Existing behavior is not authority over this procedure.


<a id="o153"></a>

## O153 — Outcome distribution of a declared process

**Wiki:** [Outcome distribution of a declared process](/workspace/planning/phase-1-live/wiki/outcome-metrics.md). **Implementation mode:** supplied process-summary provenance/arithmetic audit only.

Sires's codex and review use all trades under a bias/model, with R outcomes, average win/loss, EV, profit factor and drawdown. Stoic requires win rate and average R:R from an adequate sample. The Refill correction reports causal mechanical-entry results around −0.16R to −0.54R out of sample. [C1] p.6; [AVG] pp.27–30; [DATA] pp.3–4, 8; [OFM] p.18.

**Not a standalone trade.** Source-sequence fidelity and profitability are separate. A component touch rate or a payout screenshot is not the whole method's win rate.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Declared process/cohort version, all candidate/order/fill denominators, supplied closed outcomes and reported summary metrics, initial R definition, costs/missingness and evaluation window. |
| Outputs / units | reported_metrics, denominator_identity, initial_R_provenance, summary_consistency?, causal_correction_retained, unavailable_metrics[]. |
| ET clock / interval | Outcome belongs after its associated decision; source-summary availability after its reported observation window. |
| Bars / event membership | Supplied source/journal results only; no reconstructed trade P&L or new strategy return series. |
| Reset / persistence | Each declared process/cohort/version; do not pool component touch rates with whole method outcomes. |
| known_at | Each closed result/summary at actual availability; prior validation uses only completed history. |

**Procedure:**

1. Store supplied n, win rate, average win/loss or average RR, EV, profit factor, drawdown and their definitions. Missing source metric definition remains a hole; no new metric estimator is required by this pack.
2. Check only literal consistency when the source provides sufficient aggregate inputs: e.g. wins/decidable closed count, average R arithmetic, or profit factor positive gross/absolute-negative gross. Preserve breakeven/censored/missing cases and denominator conventions.
3. Do not equate source-sequence compliance or reference hit rate with win rate. Keep the later OFM causal rebuild around-0.16R to-0.54R out of sample visible beside earlier Refill claims, with different cohorts/provenance.
4. No new P&L, optimization, Monte Carlo or trade performance back test is authorized bythis Phase 1 outcome.

**Printed constants and limits:** Source-reported negative causal range approximately-0.16R to-0.54R is provenance, not a parameter.

**Invalid / unavailable behavior:** Component rate as win rate; loss quarter omitted; unselected cohort lost; initial R rebased; new P&L generated. Apply C04; emit `HOLE:O153:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O153-F1 — numeric fixture:** Synthetic supplied summary with 5 wins/5 losses, mean win+2R, mean loss-1R and no other outcomes implies win rate 0.5, arithmetic EV 0.5R and profit factor 10/5=2. A reported EV 1R would fail this literal consistency check. This fixture does not authorize deriving returns from market prices.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** stats/report; the previous formula labels component scores supply only their own event summaries. Whole source-method episode distributions are missing. Existing behavior is not authority over this procedure.


<a id="o154"></a>

## O154 — Prior loss-streak validation for Stoic's overlay

**Wiki:** [Prior loss-streak validation for Stoic's overlay](/workspace/planning/phase-1-live/wiki/loss-streak-validation.md). **Implementation mode:** pre-overlay supplied validation gate.

Before the overlay, Stoic asks for at least 100 trades, known win rate and average R:R, and a Monte Carlo estimate of maximum consecutive losses. If these are unknown, the source does not admit the overlay. [DATA] p.8.

**Not a standalone trade.** A win streak alone is not a trade or permission to increase risk. Generic bootstrap output is not automatically the source's loss-streak validation.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Underlying process/version, prior closed sample IDs/n, supplied win rate and average RR definitions/values, supplied Monte Carlo design/max-loss-streak result and availability. |
| Outputs / units | sample_n, sample_at_least100, winrate_known, average_rr_known, mc_result_known, validation_before_risk, overlay_validation?. |
| ET clock / interval | All sample outcomes and validation results closed/available before overlay risk decision. |
| Bars / event membership | Supplied validated process/journal records; no new Monte Carlo is run. |
| Reset / persistence | New underlying process/version requires its own compatible validation; no transfer from another strategy. |
| known_at | Maximum closed sample/metric/Monte Carlo result availability. |

**Procedure:**

1. Require at least 100 prior trades under the same underlying process and known source win rate/average RR.
2. Require a supplied compatible Monte Carlo design/result for maximum consecutive losses, with actual availability before the risk decision. Exact simulation construction is undisclosed; generic bootstrap is not author-exact.
3. If any of those required metrics is missing, overlay admission is unknown/not admitted; a recent winning streak cannot replace validation.

**Printed constants and limits:** sample_n≥100; all three source knowledge items required. No new Monte Carlo specification or path count.

**Invalid / unavailable behavior:** 99 trades accepted; future closed trade; missing MC as zero; other process sample; simulation invented. Apply C04; emit `HOLE:O154:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O154-F1 — numeric fixture:** Synthetic prior n 100, known win rate 0.55, known average RR 2 and supplied MC max loss streak 8 all available yesterday satisfy this gate for today's risk decision. n 99 fails minimum. With n 100 but MC result missing, overlay_validation=null and overlay cannot be admitted.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** stats offers generic summaries; the previous formula labels and current objects have no source-complete validation/overlay state. Exact Monte Carlo construction is unpublished. Existing behavior is not authority over this procedure.


<a id="o155"></a>

## O155 — Stoic's printed asymmetric risk ladder

**Wiki:** [Stoic's printed asymmetric risk ladder](/workspace/planning/phase-1-live/wiki/asymmetric-risk-state.md). **Implementation mode:** printed two-step risk arithmetic; activation/rebase conflict preserved.

The printed example risks one baseline unit for 3R, then after that win risks four units for 3R; after the second win it resets to one. The page heading instead says activation on a two-trade winning streak, so the discrepancy remains visible. [DATA] pp.7–8.

**Not a standalone trade.** This overlay consumes trades admitted by another validated process; it does not create entries or guarantee a favorable sequence.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Validated underlying process, fixed baseline equity E0/risk unit B≤1% of E0, closed prior results, stage, printed ladder choice and source activation interpretation. |
| Outputs / units | printed_stage, planned_risk_units, planned_reward_units, cumulative_baseline_units, next_stage?, activation_holes[]. |
| ET clock / interval | Second risk decision only after first+3 baseline units are closed/known; reset after second win. |
| Bars / event membership | Supplied underlying trades/closed results; this overlay creates no entries. |
| Reset / persistence | Printed reset to 1 baseline unit after second win. Other outcomes and equity rebasing are unpublished. |
| known_at | Prior closed results and risk baseline available before each sizing action. |

**Procedure:**

1. For the explicitly printed example use a fixed original baseline unit B with B/E0≤0.01. Stage 1 risks 1B for 3B; after that win Stage 2 risks 4B for 12B (3R of its own 4B risk).
2. Audit second-loss net 3B-4B=-1B and second-win net 3B+12B=15B. After second win, next printed risk is 1B. Do not compound percentages on updated equity unless a source policy explicitly defines it.
3. Preserve the source conflict: heading says activation on a two-trade winning streak, printed ladder increases the second trade after one win. Audit printed ladder separately; faithful general activation remains unknown.
4. Do not invent first-loss, second-loss, next-cycle or breakeven transitions, rebasing or unlimited martingale. Supplied cases outside printed transition stable return named holes.

**Printed constants and limits:** Base≤1%; printed risk units 1 then 4; reward multiple 3R; net-1 or+15 baseline units; reset 1 after second win.

**Invalid / unavailable behavior:** 4% of new 103% equity as printed 4 units; activation conflict erased; unvalidated process; future win funds entry; invented recovery ladder. Apply C04; emit `HOLE:O155:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O155-F1 — numeric fixture:** Synthetic fixed E0=10000, B=100: first win+300; second risk 400, target profit 1200. Second loss leaves net-100; second win leaves net+1500 and printed next risk 100. Using 4% of 10300=412 is not the printed fixed baseline 400. General activation and second-loss next state remain null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** No corresponding risk-state object exists in the previous formula labels or current implementation. Generic return arithmetic is not the complete overlay. Existing behavior is not authority over this procedure.


<a id="o156"></a>

## O156 — Refill-study evaluation-risk scenarios

**Wiki:** [Refill-study evaluation-risk scenarios](/workspace/planning/phase-1-live/wiki/evaluation-risk-scenarios.md). **Implementation mode:** source scenario record and arithmetic/provenance audit only.

The paper explores modeled evaluation outcomes using its supplied trade/process assumptions, including 4, 000 simulated paths, a 3, 000 target, 2, 000 trailing drawdown, −4R daily stop and risk scenarios such as 60/80/100. These are source study configurations. [REF] pp.19–21.

**Not a standalone trade.** The simulation is not a new entry method or proof of deployable alpha, especially after the causal mechanical-entry correction. It is not Stoic's asymmetric ladder.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Supplied source return cohort, evaluation path design, baseline currency/risk, target/trailing-drawdown/daily-stop/consistency policies, path count and reported outputs. |
| Outputs / units | scenario_id, assumptions, reported_pass_rate, reported_time_to_pass, source_causal_status, missing_path_rules[]. |
| ET clock / interval | Source assumptions frozen before the reported scenario; inputs must come from their actual completed cohort. |
| Bars / event membership | Supplied study records; no new market strategy, Monte Carlo paths or account simulation. |
| Reset / persistence | Each source risk scenario and evaluation/account definition. |
| known_at | Source study/result publication; these are historical source claims, not current account rules. |

**Procedure:**

1. Preserve the paper's 4000 paths, 3000 currency target, 2000 trailing drawdown,-4R daily stop, consistency-rule mention and supplied risk scenarios. Exact consistency/trailing/path generation is not fully disclosed; emit those holes.
2. Keep source outputs attached to the original cohort and assumptions. For example, 80 currency/R and 92% reported evaluation pass rate are source records, not deployable probabilities.
3. Retain the later causal mechanical-entry correction before any downstream inference. No new evaluation model or transfer to Stoic's ladder is allowed.
4. Literal currency/R conversions may be audited without simulating paths or asserting live evaluation policies.

**Printed constants and limits:** 4000 paths; 3000 target; 2000 trailing drawdown; -4R stop; source risk examples 60/80/100/150 currency per R. Source 80/R→92% and 60/R→about 97% are reported claims.

**Invalid / unavailable behavior:** Historical scenarios called current policy; new paths run; uncausal cohort ignored; Stoic ladder merged; consistency rule invented. Apply C04; emit `HOLE:O156:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O156-F1 — numeric fixture:** Synthetic source-scenario arithmetic at 80 currency/R:3000 target=37.5R, 2000 drawdown=25R,-4R daily stop=-320 currency. A supplied 3680 passes/4000 paths equals 0.92, but the count cannot be reconstructed from a rounded 92% claim unless the source supplies it.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Generic stats/report are only ingredients. Exact source path generation and evaluation/account lifecycle are missing from the previous formula labels. Existing behavior is not authority over this procedure.


<a id="o157"></a>

## O157 — Stoic's macro indicator set

**Wiki:** [Stoic's macro indicator set](/workspace/planning/phase-1-live/wiki/macro-indicators.md). **Implementation mode:** Stoic's declared macro evidence set and provenance ledger.

The macro application identifies the cycle, examines leverage/credit/housing/valuation evidence, compares it with history and reaches a data-based verdict. These are examples inside the data-engine process, not a separate intraday model. [DATA] pp.5–6.

**Not a standalone trade.** One unusual series or the source's historical bubble conclusion is not a current trade instruction.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source question/cycle context, named leverage/credit-borrowing/housing/valuation series, units/frequency/vintages, historical baseline and selected transformations. |
| Outputs / units | indicator_records[], required_series_present?, vintage_causal?, source_historical_verdict?, automatic_current_verdict=null. |
| ET clock / interval | Only releases/vintages available by the source historical decision; reference period is not publication time. |
| Bars / event membership | Economic/financial observations, not an intraday bar entry model. |
| Reset / persistence | Each declared question/process/version and as-of snapshot. |
| known_at | Actual release/available_at for every indicator and baseline component. |

**Procedure:**

1. Preserve the source steps: identify macro cycle, check leverage/corporate borrowing/housing/valuation evidence, compare with history, then record the data-supported verdict.
2. The exact series IDs, transforms, thresholds and complete vintage archive are not disclosed. Map only supplied named inputs; a calendar date does not supply a released value.
3. Record the historical bubble-question conclusion as that dated source case. Do not produce a fresh current macro recommendation or use unrelated acquired series to fill an unnamed author input.

**Printed constants and limits:** No source-complete series list or current decision thresholds.

**Invalid / unavailable behavior:** Revised data used early; unnamed series invented; historical verdict as current call; one unusual series as entry. Apply C04; emit `HOLE:O157:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O157-F1 — numeric fixture:** Synthetic declared evidence set has 4 required series. Three have verified pre-decision vintages; the fourth has no supplied observation or availability proof. available_series_count = 3 of 4; required_series_present = null with a missing-series hole, and automatic_verdict = null. A later revised leverage value of 2.0 cannot replace the actually available 1.5 at the historical decision.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** A dated economic calendar is only an ingredient; the previous formula labels and implementation do not contain Stoic's full series set, cycle classifier or decision thresholds. Existing behavior is not authority over this procedure.


<a id="o158"></a>

## O158 — Stoic's macro-cycle classification

**Wiki:** [Stoic's macro-cycle classification](/workspace/planning/phase-1-live/wiki/macro-cycle.md). **Implementation mode:** supplied historical source classification; engine hole.

The macro example locates the current cycle before interpreting leverage, credit, housing and valuation against historical episodes. The source does not disclose a complete cycle-classification algorithm. [DATA] pp.5–6.

**Not a standalone trade.** A cycle label is not an entry or proof that a historical outcome must recur.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source cycle label/as-of, series/vintages, business-cycle/sentiment rationale and explicit classifier availability. |
| Outputs / units | source_cycle_label, rationale, inputs_available, automatic_cycle=null. |
| ET clock / interval | Cycle interpretation at actual source decision from then-available data. |
| Bars / event membership | Released macro observations; generic price trend/day type is not this classifier. |
| Reset / persistence | Each source macro as-of/version; revisions are new records. |
| known_at | Maximum required release and source classification availability. |

**Procedure:**

1. Retain the source overheating/contraction or other literal cycle interpretation and evidence.
2. No complete cycle classification procedure is published. Do not choose moving averages, recession rules or label thresholds for the author.
3. A historical source conclusion is a case observation and does not guarantee recurrence or generate entries.

**Printed constants and limits:** No disclosed classifier thresholds or history window.

**Invalid / unavailable behavior:** Generic trend as cycle; future vintage; unsupported current label; detector invented. Apply C04; emit `HOLE:O158:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O158-F1 — numeric fixture:** Synthetic supplied contraction label at 09:00 supported by 3 available indicators can be retained as a supplied source observation. The count 3 does not imply a majority-vote algorithm. Without the source label/rules, automatic_cycle=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** The source classifier is missing from the previous formula labels and current phase 1 objects. Generic trend or calendar labels are not substitutes. Existing behavior is not authority over this procedure.


<a id="o159"></a>

## O159 — Stoic's custom C-score

**Wiki:** [Stoic's custom C-score](/workspace/planning/phase-1-live/wiki/c-score.md). **Implementation mode:** supplied custom score only; formula hole.

The quantifying-fundamentals discussion names custom C-scores among its ways of turning context into comparable data, but supplies no complete formula. [DATA] p.5.

**Not a standalone trade.** A named score is not a disclosed trade trigger and must not be replaced silently by a generic z-score.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Literal C-score name, source variable/context, supplied score/unit if any, source version, timestamp/vintage and missing formula record. |
| Outputs / units | source_c_score?, source_score_unit?, automatic_c_score=null, hole:custom_score_formula. |
| ET clock / interval | Actual supplied score availability before use. |
| Bars / event membership | Source macro score record; no implied price bar transform. |
| Reset / persistence | Each source metric/version/observation. |
| known_at | Score and underlying source input availability, when supplied. |

**Procedure:**

1. Retain a supplied source number under its exact custom-score identity and provenance.
2. No complete normalization, weights, comparison set or cutoff is disclosed. A conventional z-score cannot be renamed C-score.
3. Missing score/definition returns null and the named hole. No threshold can be inferred from the historical verdict.

**Printed constants and limits:** None published for the custom engine.

**Invalid / unavailable behavior:** Z-score alias; weights invented; cutoff fit to outcome; missing unit guessed. Apply C04; emit `HOLE:O159:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O159-F1 — numeric fixture:** Synthetic supplied C-score 2.4 and separately computed named z-score 1.2 remain distinct values. Removing the supplied C-score leaves automatic_c_score=null, not 1.2.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Missing from the previous formula labels and current implementation; no author-exact C-score can be generated from the supplied material. Existing behavior is not authority over this procedure.


<a id="o160"></a>

## O160 — Historical-average and standardized-deviation comparison

**Wiki:** [Historical-average and standardized-deviation comparison](/workspace/planning/phase-1-live/wiki/standardized-deviation.md). **Implementation mode:** explicitly named conventional arithmetic with source-definition holes.

Stoic discusses position relative to historical averages and standard deviations as quantitative context. The exact series, history window and decision cutoffs are not disclosed. [DATA] p.5.

**Not a standalone trade.** An extreme standardized value is not itself the data-engine's entry rule or a replacement for C-score.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Series/vintage, current value x, explicitly selected prior baseline IDs, mean/deviation convention, supplied transform and interpretation. |
| Outputs / units | baseline_mean, baseline_sd, raw_deviation=x-mean, standardized_deviation=(x-mean)/sd when declared, source_transform_known?. |
| ET clock / interval | Baseline ends before evaluated observation and every vintage is available by its decision. |
| Bars / event membership | Comparable native economic observations; frequency/seasonal adjustment/units retained. |
| Reset / persistence | Each declared baseline/version; no automatic rolling length. |
| known_at | Maximum baseline/current release availability and transform specification time. |

**Procedure:**

1. If a conventional transform is explicitly supplied, compute its stated mean and standard deviation over the selected prior observations. Population uses divisor N; sample uses N-1 and requires N≥2. Do not choose between them for the author.
2. For positive SD calculate(x-mean)/SD. Zero SD returns null with zero_scale, not 0 or infinity as a valid score.
3. Missing source series/window/convention/cutoff means source-specific exact transform/decision unknown. A named conventional comparison remains distinct from C-score.

**Printed constants and limits:** No disclosed history window, degrees-of-freedom choice or decision cutoff. Formula is explicitly named conventional arithmetic only.

**Invalid / unavailable behavior:** Current value in prior baseline without source; future vintage; population/sample guessed; zero SD division; C-score alias. Apply C04; emit `HOLE:O160:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O160-F1 — numeric fixture:** Synthetic explicitly selected population baseline [1, 3] has mean 2, SD 1; current x 4 gives raw deviation 2 andz 2. Under explicitly selected sample SD=sqrt 2, z=sqrt 2≈1.414214. Missing convention makes author-exact z unknown; a constant baseline [2, 2] has SD 0 and standardized value null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Missing source-specific transforms and thresholds in the previous formula labels and implementation; generic statistics provide only ingredients. Existing behavior is not authority over this procedure.


<a id="o161"></a>

## O161 — Stoic's trend-strength measure

**Wiki:** [Stoic's trend-strength measure](/workspace/planning/phase-1-live/wiki/trend-strength.md). **Implementation mode:** supplied Stoic context measure; engine hole.

Trend strength is another quantified context item named in the data-engine macro discussion. The source supplies the question, not a complete detector. [DATA] p.5.

**Not a standalone trade.** The phrase does not authorize a particular moving-average, regression or momentum strategy.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source series/instrument, intended horizon, observation/vintage set, supplied strength reading/unit and source version. |
| Outputs / units | source_strength?, horizon, unit, automatic_strength=null. |
| ET clock / interval | Actual source observation/availability before its contextual use. |
| Bars / event membership | Named source series; Sires microbalance strength is a different object. |
| Reset / persistence | Each source metric/horizon/version. |
| known_at | Supplied reading and its input availability. |

**Procedure:**

1. Preserve a supplied source reading and horizon with provenance.
2. The phrase trend strength supplies no moving-average, regression, momentum or other detector. Return the missing formula/threshold hole rather than choosing one.
3. Do not select a horizon after seeing the eventual trend or transfer another author's execution-strength rule.

**Printed constants and limits:** No published equation, horizon or threshold.

**Invalid / unavailable behavior:** MA/regression invented; later trend selects horizon; microbalance strength borrowed. Apply C04; emit `HOLE:O161:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O161-F1 — numeric fixture:** Synthetic supplied strength 7 on a stated 0–10 source scale is recorded as 7. A separate regression slope 0.5 is not an equivalent score. Without the source reading/engine, automatic_strength=null.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** Missing from the previous formula labels and current source-method objects. Other authors' microbalance strength is a different observation. Existing behavior is not authority over this procedure.


<a id="o162"></a>

## O162 — Economic observation and release vintage

**Wiki:** [Economic observation and release vintage](/workspace/planning/phase-1-live/wiki/economic-release-vintage.md). **Implementation mode:** point-in-time economic observation adapter.

The data engine compares macro evidence through time; thesis/news reads depend on information actually available when used. A historical series value, its first release and a later revision need separate availability records for a causal Phase 1 observation. [DATA] pp.3–6; [C1] pp.3–6; [TBR] pp.24, 36–37.

**Not a standalone trade.** A date-only calendar is not the released value, and a revised series cannot be treated as information available at the original decision.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Series/event ID, reference period, scheduled_at, released_at, available_at, revision/vintage ID/time, native value/units and source provenance. |
| Outputs / units | latest_available_vintage_at_decision, reference_period, actual_value, available_at, vintage_history. |
| ET clock / interval | Use actual release/availability timestamp, preserving timezone and precision. Reference period/date-only calendar is not an intraday release key. |
| Bars / event membership | Native released values, not price bars or a calendar-only record. |
| Reset / persistence | Each series/reference period has immutable vintages; revisions append. |
| known_at | Actual available_at for the selected vintage. If only released_at is verified, record that availability assumption explicitly; missing intraday time remains unknown. |

**Procedure:**

1. For a decision keyt select only vintages whose available_at≤t and whose series/reference period match the source question. Among them use the latest available version only when the source requested that current-vintage view.
2. Keep initial release and revisions separately. A later revision cannot replace the value in an earlier snapshot.
3. Missing historical vintages or publication times yield causal input holes. No interpolation or backfill can make a later number historically known.

**Printed constants and limits:** No invented release time or revision lag.

**Invalid / unavailable behavior:** Period label as release; date only at midnight; latest revised series backdated; double timezone conversion. Apply C04; emit `HOLE:O162:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O162-F1 — numeric fixture:** Synthetic March 2026 observation is first released on 2026-04-01 at 08:30 ET with value 2.0, then revised on 2026-05-01 at 08:30 ET to 1.5. A 2026-04-15 10:00 ET decision sees 2.0. A 2026-05-02 10:00 ET decision may see 1.5 under the explicitly selected latest-available-vintage policy. The March 31 observation-period date does not make 2.0 available in March.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [family_levels.load_red_folder](/workspace/implementation/src/trading_research/research/phase1_live/family_levels.py) is only a calendar ingredient. Full release values, revisions and source macro transformations are missing; related the previous formula labels R-J20/J21/R-R03. Existing behavior is not authority over this procedure.


<a id="o163"></a>

## O163 — Provide, withdraw and consume events

**Wiki:** [Provide, withdraw and consume events](/workspace/planning/phase-1-live/wiki/order-participation-events.md). **Implementation mode:** native provide/withdraw/consume lifecycle evidence; source depth hole.

jetbundle begins with submissions that provide liquidity, cancellations that withdraw it and executions that consume it, then relates those events to the chart/DOM/tape impression. The illustration uses an AAPL ten-level order-book record. [MATH] pp.4–6.

**Not a standalone trade.** A static book snapshot does not reconstruct the event process, and displayed imbalance alone is not an entry.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Native order/event ID, exchange ordering, instrument, time, action, side, price, size, depth/order identity and lifecycle coverage. |
| Outputs / units | provide_events, withdraw_events, consume_events, per_side_volumes, depth_coverage, source_process_complete?. |
| ET clock / interval | Native event order and source observation interval; indistinguishable ties cannot be arbitrarily ordered. |
| Bars / event membership | The declared native instrument, event interval and required depth scope. AAPL ten-level LOBSTER is the printed illustration; NQ is permitted. |
| Reset / persistence | Source book/session initialization and explicit gaps/resets; no snapshot-to-event invention. |
| known_at | Each native action when observed with valid book state. |

**Procedure:**

1. Decode actual submissions/adds as providing, actual cancellations/removals as withdrawing, actual executions as consuming under that dataset's schema. A modification's meaning depends on its native lifecycle; do not automatically call every net change an add/cancel.
2. Track only levels/orders covered by the data. Static snapshots alone cannot reconstruct unobserved cancellations or all interim replenishment.
3. Preserve the selected instrument and declare `required_depth_levels` before the observation. Require positive native depth coverage at least that large, and reject any event outside the declared coverage. AAPL/ten levels describes the illustration, not a universal restriction. NQ is eligible when its actual data supports the declared scope; missing native lifecycle/order evidence remains a specific hole.

**Printed constants and limits:** Source illustration AAPL, 10 levels; no universal instrument, depth count or action-rate thresholds. [MATH] p.3 explicitly discusses an NQ application and p.16 calls AAPL illustrative.

**Invalid / unavailable behavior:** BBO as 10 levels; disappearing wall as cancel without action; quote updates as executions; order identities invented. Apply C04; emit `HOLE:O163:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O163-F1 — numeric fixture:** Synthetic verified event log adds 10 at bid 100, cancels 3, executes 4 against it: provided 10, withdrawn 3, consumed 4, remaining 3 under that complete lifecycle. Snapshots 10 then 3 alone cannot distinguish 7 canceled from 3 canceled+4 executed; all three event types are unknown without the log.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** mbp1_extract and mbp1_objects have limited trade/BBO ingredients. Full source order/depth reconstruction is missing; the previous formula labels R-F06/F07 are only related partial observations. Existing behavior is not authority over this procedure.


<a id="o164"></a>

## O164 — Aggressive effort versus price-response efficiency

**Wiki:** [Aggressive effort versus price-response efficiency](/workspace/planning/phase-1-live/wiki/response-efficiency.md). **Implementation mode:** same-interval effort/response measurements and supplied state interpretation.

jetbundle compares participation with actual price response and whether opposite liquidity persists. Efficient aggressive displacement is discovery; large executions with little response and persistent refill support absorption. The Sires/Saint flow reads likewise compare effort with result without inheriting the guest's exact state model. [MATH] pp.6–8; [ABS] pp.8–13; [WIC] pp.4–6.

**Not a standalone trade.** High volume alone is not absorption, and efficient discovery is not an automatic fade.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Explicit local interval, native aggressive volume, selected trade price or mid reference, source response definition, opposing liquidity persistence/refresh and as-of. |
| Outputs / units | aggressive_volume, price_response_points/ticks, mid_response?, named_response_per_volume?, source_efficiency_class?. |
| ET clock / interval | Same local interval for effort, response and liquidity; interval fixed before later outcome. |
| Bars / event membership | Native ordered execution/book observations; no future reversal window. |
| Reset / persistence | Each declared local interval/state observation. |
| known_at | At interval end after required observations; source current state cannot use the next state. |

**Procedure:**

1. Measure directional response between the explicitly selected reference points and total/source-side executed effort in the same interval.
2. An explicitly named descriptive ratio response/volume may be calculated when volume>0; it is not a published source detector. Zero effort gives null ratio, not perfect efficiency.
3. Classify efficient discovery versus effort-with-little response-and-persistent refill only with the source qualitative record or complete criteria. Missing depth/thresholds means automatic class unknown.
4. Do not transfer jetbundle's five-state interpretation as an unspoken entry rule to Sires/Saint.

**Printed constants and limits:** No source-complete response window, volume threshold or ratio cutoff.

**Invalid / unavailable behavior:** Different intervals; future window; high volume alone absorption; invented ratio as author engine. Apply C04; emit `HOLE:O164:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O164-F1 — numeric fixture:** Synthetic selected interval buy volume 100, response+1 point yields named response/volume 0.01 point/contract. Another interval buy volume 100, response 0 with unknown opposing depth does not prove absorption. Source efficiency class remains null without the required interpretation/evidence.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** [mbp1_objects.absorption_a/absorption_b](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_flow.aggressive_at_level/r_f06_dom_absorption](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); the previous formula labels R-F06/F07. Full source efficiency and depth measures are missing. Existing behavior is not authority over this procedure.


<a id="o165"></a>

## O165 — B–A–D–E–W auction-state alphabet

**Wiki:** [B–A–D–E–W auction-state alphabet](/workspace/planning/phase-1-live/wiki/auction-state.md). **Implementation mode:** supplied heuristic B/A/D/E/W state audit; automatic classifier hole.

The guest framework names B balance, A absorption, D discovery, E exhaustion and W withdrawal. B has two-sided activity/revisits and low aggression; A combines high effort, low response and holding/refilling opposite liquidity; D is efficient displacement; E includes replenishment ending/level failure after prior effort; W is cancellation-dominated. [MATH] pp.7–10.

**Not a standalone trade.** These are heuristic current states, not AMT day types or automatic trade signals. Sires's following application remains separately attributed.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Source state ID/time/label, native instrument, local participation/response/depth evidence, predeclared required_depth_levels, explicit qualitative criteria and inputmaxknown_at. |
| Outputs / units | state_label:B/A/D/E/W/null, state_evidence_complete?, automatic_state=null, missing_criteria[]. |
| ET clock / interval | All state inputs known by state_at; next state events excluded. |
| Bars / event membership | Source native order/depth process; not AMT day types or generic absorption flags. |
| Reset / persistence | Each state observation/local context; source cadence/window is not disclosed. |
| known_at | At state_at after all cited support exists. |

**Procedure:**

1. Preserve literal source meanings:B=two-sided quiet/revisiting balance; A=higher effort, little displacement, opposite liquidity holds/refills; D=effort with efficient displacement; E=prior effort then liquidity/replenishment fails; W=cancellations dominate.
2. The labels are heuristic observations and the source supplies no complete threshold/window/tie/priority classifier. Audit supplied labeled examples and emit automatic_state=null for raw discovery.
3. Missing cancellation or required local depth evidence prevents claiming the affected W/A/E observations. Any native instrument, including NQ, is eligible; assess coverage against the declared required depth scope rather than imposing the illustration's ten levels.
4. These states do not generate entries or a fixed win rate claim.

**Printed constants and limits:** Five labels B/A/D/E/W; source illustration 20000AAPL order book events, not universal training data.

**Invalid / unavailable behavior:** Day type as state; W without cancels; future liquidity failure as earlier A; new classifier trained; state as entry. Apply C04; emit `HOLE:O165:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O165-F1 — numeric fixture:** Synthetic supplied state A at 10:00 cites buy volume 100, little 0.25 point response and verified persistent opposite refill, all known 10:00. Re moving refill evidence makes that source A observation incomplete. A later liquidity failure 10:01 may support an E observation at 10:01; it cannot be used at 10:00.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** The source five-state classifier is missing from the previous formula labels and current implementation. Generic day or absorption flags are not the complete state model. Existing behavior is not authority over this procedure.


<a id="o166"></a>

## O166 — Conditioned next-state transition

**Wiki:** [Conditioned next-state transition](/workspace/planning/phase-1-live/wiki/auction-state-transition.md). **Implementation mode:** ordered supplied next-state and conditioning audit; no classifier/matrix training.

The framework considers the next auction state conditional on current liquidity and pace, distinguishing persistence from change. The 20, 000-event AAPL example and its matrix illustrate the process; they are not universal NQ probabilities. [MATH] pp.9–11.

**Not a standalone trade.** A matrix cell or persistent absorption state is not an entry, and absorption must be reconsidered when replenishment fails.

| Contract item | Exact requirement |
|---|---|
| Inputs / native fields | Supplied source current/next state IDs/labels/times, exact next-observation definition, current liquidity/pace conditions, native instrument/depth cohort and supplied transition counts/matrix with source_counts_symbol provenance. |
| Outputs / units | from_state, to_state, state_at, next_state_at, conditioning_causal, transition_valid?, supplied_row_count, reported_probability?. |
| ET clock / interval | state_at<next_state_at; allconditioningknown_at≤state_at. Next-state cadence must be identified. |
| Bars / event membership | The declared native state sequence, instrument and depth context. NQ observations are permitted; printed AAPL counts retain their original provenance. |
| Reset / persistence | Each declared cohort/conditioning state version; do not join across gaps/resets as adjacent states. |
| known_at | Conditioning at current state; transition outcome only at next state. |

**Procedure:**

1. Match actual adjacent observations under the supplied source cadence and stable instrument/cohort. Missing next-state definition is a hole.
2. Audit current conditioning using only current available liquidity/pace, then observe next state later. Preserve persistence on diagonal versus changes off diagonal.
3. For supplied counts only, row-normalized P(i→j)=count(i→j)/sum_jcount(i→j) when row total>0; empty row probabilities null. Require the counts' declared native instrument (`source_counts_symbol`) to match the observation cohort. Matching the printed numbers by coincidence is not an identity error; borrowing another instrument's records is. This is literal count arithmetic, not training a new matrix or claiming universal probabilities.
4. Retain source AAPL20000 event illustration and printed D→D84%, D→A12% as that case; never transfer to NQ or call them trade odds.

**Printed constants and limits:** Source 20000AAPL events; printed 84% D persistence/12% D→A are case claims, not universal parameters.

**Invalid / unavailable behavior:** Future conditioning; states not adjacent; gap bridged; NQ probability borrowed; new matrix trained; row zero as 0 probability. Apply C04; emit `HOLE:O166:<missing_field>` with the actual missing field and affected method/branch. Unknown construction/coverage is not false market evidence. A witnessed wrong-side, late or identity-mismatched prerequisite can be false.

**O166-F1 — numeric fixture:** Synthetic supplied transition row from current state D has next-state counts D:84, A:12, B:4, E:0, W:0, total 100. Thus P(D→D) = 84/100 = 0.84, P(D→A) = 12/100 = 0.12, and the complete row sum is 1. These synthetic counts illustrate arithmetic; they are not recovered source counts. A conditioning feature known at 10:01 for a current state observed at 10:00 fails causality even if the next state arrives at 10:02.

**Fixture mutations:** Repeat this fixture with one required dependency available after use, one missing required datum, and one wrong parent/band/instrument. Expect the C08 causal, unknown and identity results; preserve the reason.

**Current-code attachment to review/replace:** No source-compatible state-transition/cohort implementation exists in the previous formula labels. Generic rate tables do not reconstruct the state definitions. Existing behavior is not authority over this procedure.


## Source references

Page numbers are one-based PDF pages, including covers. The 166 wiki object procedures and 12 method contracts above contain the required rules and unresolved boundaries; the implementer does not need to open the 41 PDFs to fill a gap. A gap is implemented as the specified unknown. Source links remain for audit provenance. The complete reviewed source inventory is [the wiki source catalog](/workspace/planning/phase-1-live/wiki/source-catalog.md).

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[SS]: </workspace/sources/documents/jumbo/SessionStat+.pdf>
[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
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
[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[K2345]: </workspace/sources/documents/discretionary/2345-funded-session.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[XF]: </workspace/sources/documents/jumbo/xfcmg2.pdf>
[FIND]: </workspace/sources/documents/jumbo/jjumbo-findings.pdf>
