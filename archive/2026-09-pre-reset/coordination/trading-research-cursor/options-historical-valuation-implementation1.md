Goal: implement the historical option valuation measurement consumer required for Deliverable1 actual IV/Greek/ATM/smile/term/0DTE distributions. User September8 20:41 says complete all D1 measurements/statistics/timing before Context. Root owns protocol, registered execution, scientific acceptance. Use selected Cursor Grok4.6ExtraHighFast. Read START_HERE.md once, then relevant OPTIONS O01/O02/O05, COMMON_CONTRACTS CC02, FOUNDATIONS F02, CROSS_ASSET X02.bootstrap, SYSTEM_REFINEMENT SR-O01/O02/O05; no catalogue audit.

Only write TWO NEW files in this checkout:
src/trading_research/research/options_historical_valuation.py
tests/test_options_historical_valuation.py
They do not exist canonically. Do not change numerics, quote, OI, sharedstatistics, runners, protocols or any other files. Read ALL baselines from /workspace/trading-research; checkout older files are stale. No shell/imports/tests/data scans/network/research execution. Root runs registered checks. 30minute wall allowance, return concise API/risk/source/test report. No more worker repair round expected: self-review entire code before final.

Read canonical src/trading_research/research/options_valuation_numerics.py and accepted test/options_valuation_numerics, validation/OPTIONS_VALUATION_NUMERICS_V1.json+EXECUTION_V1; numerical44checks already accepted. Read options_quote_measurements.py schemas/cut/support/OIjoin output and validation/OPTIONS_QUOTE_QUALITY_SUPPORT_V1.json. Actual accepted pilot16 contract-cut boards 4.22Mrows but only68922quoted; root streams accepted tables not rawtape. Exact names/types MUST match actual schemas. All scientific computations need named assumptions and nullable clocks. Do not reread/reprice listed-unquoted rows: aggregate coverage from vectorized mask counts then compute only relevant quoted rows, retaining denominator by everygroup. The full49chain/year quote18 run is active, source/modules must stay unchanged.

Root study decisions for this implementation: accept named scenario conventions from assessment below, do NOT claim certification. Actual/365Fixed from exact expiry-minus-cut ns; exact ns >2**53 remainint64. Main cash-close SPX/NDX EOD and lagged-cash earlier cuts explicit; ETF intraday eligible from accepted support. VIX unavailable cash cannot be replaced by VX futures as spot; permit put/call-parity forward independently if eligible paired prices. No join to missing VIX external series in this consumer. ETF dividend exdate support retrospective not PIT announcements; call schedule diagnostic vsq0. Missing required rate/support yields explicitstatus; zero-rate is own named scenario. FREDrate units percent todecimal; closesttenor main, zero and linear own sensitivity. European forward from Sexp(rT) with q0 named; independently parityFcallput sameexpiry/strike exactcontract coordinate, interval from bidask preservesnegative/nonpositive inadmissibility. Use robust ATM/parity aggregation with contributorcounts; do not treat one selected source family as another. Apply accepted Black/American funcs only; no newsolver or genericresponsecube. American n_space128 is frozennumericaldefault, notuserliteral, no per-contract gridrefinement.

Pure consumer needs practical streaming interface: build_valuation_tables(board: ArrowTable, underlier_support: ArrowTable, fred_support: ArrowTable, action_support: ArrowTable, *, scenario_contract: dict) -> mapping of Arrowtables {contract_cut, expiry_cut, coverage}. Input board batch MUST contain a complete chain/date/cut/source_family group for parity andATM; validate grouping or clearly return mergeable reductions with groupseal owner. Root partitions fullcalendar chain/day and will call wholechain/date groups. Cap <=250000rows percall or documented equivalent, use Arrow/NumPy selecting quoteeligible rows before.to_pylist(); avoid perboard Python allrows. Include build_cross_chain_table(expiry_tables, *, scenario_contract) if exactT/nativeexpiry matching can be implemented honestly. One stable scenario identity hash binds all choices; use explicit preset generator default_scenario_contract() frozenversion and validate modifications (not arbitrarysilentfallbacks). Allow callers choose namedscenarios for pilotcost probe but no scenario multiplicative explosion by accident. Primary plus one-at-a-time sensitivities, labelbaseandchangedassumption. Cache deterministic underlier/rate/dividend lookup at whole economicgroup, reuse repeated quote numeric inputs if exactsame source payload/scenario but preserve each physicalsource family row.

Output exact IDs/rawclocks/OSI/right/strike plus allstatusmasks, scientificdependencies, namedstyle/expiry/model/coordinate choices, T/discount/F/S/r, bidmidask prices+IVbounds/statuses/residual, perunit delta/gamma/vega/vanna/charm/volga/theta using accepted API. No inferred knownat. model_asof=cut; actualknown_at/received/published=null andcausal_feature_eligible=False. DTEcivil unchanged;0DTE valuationT maypositive. Greeks only identified/stable: do notfillweakvega/unboundedwithzero. Multiplier optionalpostsolver100scenario, not inside inversion. OIstatus masks preserved no inferreddealerholding. Expiry row counts allrequired denom, ATMcandidate minabslogK/F tiebreaklowerK thencontractid, separatecallput nativeexpiry, wIV2T,kbinmedians; noforcedconstanttenorinterpolation. Crosschain comparators nativeexpiry+exactT/modelclockclass/sourcefamily/cut/scenarios compatible, incompletepairs explicit undefined. Coverage includes listedunquoted/basecensor counts so quoted-onlyoutput doesnotinflate support.

Independent tests on literal fixtures, monkeypatch numerical funcs for studyjoin semantics only whennotcheckingnumerics: AMvsPMsametimestamp/strike; laggedvssamedatecash; askonly/zerobid/crossed/conflict; ETFdividendsq0; VIXmissingdoesnotdropSPY andparitywithoutspot; listedunquoted denominators; nearbroadremainseparate; civilDTE0positiveT; nanoseconds>2**53; nullknownatstaysnull; multiplierpostsolver; futureunderliernotselected. Atleastone actual existing numerics call demonstrates acceptedAPI compatibility. No tests mirroring implementation alone. Types/emptytables stable. Allunavailable statuses still emitted/covered. No Context forecasts/exposureflow/node/PnL.

Prior bounded assessment is reference; these root decisions override ambiguity in it:

I'll read the project entry point and the valuation/measurement contracts first, then only the accepted Deliverable 1 state needed to define the missing historical study.Next I’ll pull only the current Deliverable 1 state and the options/implied valuation clauses, not the broader catalogue.I’ll read the implied/options spec sections and the accepted valuation/quote/OI contracts next.I’ll now read the frozen current-deliverable acceptance block and the valuation/quote/OI source contracts.Option price/IV/Greek clauses live in OPTIONS.md and siblings, not MEASUREMENTS.md. I’ll read those plus the accepted valuation/quote/OI contracts.I’ll read the accepted numerical API, quote/OI linkage contracts, and the governing O01/O02/O05 experiment clauses.I have the numerical API. Next I’ll freeze per-chain conventions and the quote/OI fields the historical study can actually consume.I’ll pull the remaining source-backed chain conventions and the quote-pilot metadata the historical study must consume.**Study:** `Research-Options-Historical-Valuation-v1` — first missing D1 valuation *population* after accepted OI11, numerics 44, and quote-pilot16 kernels (full18 starting). Root freezes protocol, registers, executes. This does **not** re-open those methods. `MEASUREMENTS.md` has no IV/price/Greek clauses; governing siblings are `OPTIONS.md` O01/O02/O05, `COMMON_CONTRACTS.md` CC-02, `FOUNDATIONS.md` F02, `CROSS_ASSET.md` X02.bootstrap, `CONTEXT.md` C15 measurement ports, `COMPUTATION_SCHEDULE.md` S2, `RUNTIME_SCHEDULER.md` options board, `SYSTEM_REFINEMENT.md` SR-O01/O02/O05, `SOURCE_FINDINGS_AND_CONFLICTS.md` DRF-A06.

Omit this study and D1 still has no acquired IV/Greek tables, no ATM/smile/term/0DTE/cross-IV *measurements*, and O04/C15/O09/O16 have no honest input.

---

### 1. Per-chain conventions vs unknown

**Observed facts** (quote `cut_board` + OI `identity_map`): `chain`, OSI, `expiration` date, `millistrike`, `right`, `contract_id`, quote `ts_event_ns`/`cut_ns`, listing/OI flags. Civil `dte_days` ≠ valuation `T`.

**Named model classes** (O02: European Black vs American ETF FD; *not* a certified F02 master — DRF-A06 still “verify by product/series”):

| Chain | Style / coordinate | Settlement class | Expiry-clock *scenario* (not official SOQ) | Multiplier |
|---|---|---|---|---|
| SPX, NDX | `european_black`, forward | cash-index, AM-class vs SPXW/NDXP | `osi_date_0930_et` primary; `osi_date_1600_et` sensitivity | `scenario_equity_100` via `apply_contract_multiplier` only |
| SPXW, NDXP | `european_black`, forward | cash-index, PM-class | `osi_date_1600_et` | same scenario |
| QQQ, SPY | `american_spot_fd`, spot | American ETF | `osi_date_1600_et` | same scenario |
| VIX | `european_black`, forward | cash VIX options ≠ VX futures options | `osi_date_0930_et` named only | same scenario |

**Unknown — do not invent:** official AM fixing/SOQ, PIT announced dividends, intraday SPX/NDX/VIX spot, VIX forward per maturity, `known_at`/`received_at`/`published_at`, certified multiplier/tick, VIX listing denominator. `T = years_from_nanoseconds(expiry_ns − cut_ns)` (Actual/365 Fixed). Same-date AM/PM series stay distinct (O01/F02/X04).

**Fail if omitted:** 0DTE Greeks mix AM/PM; American ETF priced as Black; VIX treated as VX; silent `dte_days/365` (numerics already reject that).

---

### 2. Usable input branches (do not suppress independents)

Shared: quote cuts `09:30`/`10:00`/`15:00`/`cash_close` (+ `15:00_utc` diagnostic). Early-close `15:00` is `not_applicable`. Stages train `[2020-01-01,2023-01-01)`, dev `[2023,2025)`, confirm `[2025,2026-09-04)`. Chains NDX/NDXP/QQQ/SPX/SPXW/SPY/VIX. Consume **accepted quote cut boards + support**, never raw tape.

**A. ETF intraday (QQQ, SPY)** — independently live at every applicable cut.  
`S` = ETF 1m complete bar end ≤ cut (`latest_complete_one_minute_bar_end_at_or_before_cut`); gap/age retained. Rate: FRED `obs_date≤request_date`, `historical_known=UNKNOWN`, `r = rate_pct/100`, closest `tenor_days` to `T×365` (also zero-r and linear-tenor). Dividends: `action_support` cash amounts with `request_date < ex_date ≤ expiration` as `exdate_schedule_not_announcement_pit` vs `q0_no_dividend`. Invert with `invert_american_quote_interval` / `american_iv` / `american_greeks`.

**B. Index retrospective EOD (SPX, SPXW, NDX, NDXP)** — do not invent intraday cash.  
`cash_close` cut: `retrospective_same_date_close_at_or_after_declared_close`. Earlier cuts: `prior_available_cash_date_close` (lagged). `cash_publication_known` null. `F_spotcarry = S·exp(rT)` with **q=0 named**. Independently, same-expiry usable call/put: `F_parity = K+(C−P)/D` (X02.bootstrap; no IV). Invert with `invert_quote_interval` / `black_iv` / `black_greeks`. Missing cash → valuation-ineligible, quotes still counted.

**C. VIX** — `vix_cash_unavailable` in quote support. Join accepted *daily* VX/VIX close only as a tagged retrospective underlier; else `vix_spot_unavailable`. No VIX forward curve. Parity-F still allowed on usable European pairs.

**Quote → valuation masks (separate, SR-O01):**  
`quoted` / `usable` (finite bid>0, ask≥bid, sizes>0, no conflict; locked usable+flagged) / `valuation_input_ok` (usable or ask-only) / `underlier_ok` / `rate_ok` / `T_ok` / `style_supported` / `price_admissible` / `solver_converged` / `iv_identified` / `greek_stable`. Mid = `(bid+ask)/2` from boards. Crossed/conflict: no price, no fallback.

**ATM / tail / DTE (quote buckets, not OI `8-30`):** `expired,0,1,2-7,8-14,15-30,31-60,61+`. ATM = min `|K−F|` among `iv_identified` per `chain×expiration×cut×source_family` (also `|k|=|ln(K/F)|` bins `≤0.02, 0.02–0.10, >0.10`). Tail = outer k bins. Near/broad are *acquisition* families, not ATM truth.

**Denominators (never implicit):** raw board rows; quoted; listed-unquoted; usable; valuation-eligible; identified bid/mid/ask IV; one-sided/unbounded; weak-vega; Greek-unstable; OI-available vs missing/ambiguous/stale/expired/zero; VIX listing unknown; missing underlier/rate. Zero OI total → undefined OI-weighted fraction.

**Fail if omitted:** pre-close index IV uses unpublished same-date cash; VIX hole kills QQQ/SPY; ATM defined on near-file names; listed-unquoted dropped (O01 coverage).

---

### 3. Output schema and clocks

Pure consumer of quote boards/`underlier_support`/`fred_support`/`action_support` and OI identity already joined on boards.

`valuation_contract_cut` (compact, no raw tape):  
`contract_id, chain, osi_symbol, expiration, millistrike, right, request_date, cut_label, cut_ns, source_family, dte, dte_bucket,` quote `bid/mid/ask`, `ts_event_ns, sample_age_ns, usable, base_class,` OI flags,  
`style, coordinate, expiry_clock_id, underlier_assumption, rate_assumption, dividend_assumption, multiplier_assumption,`  
`S, F_used, F_spotcarry, F_parity, r, discount, T, expiry_ns,`  
`iv_bid/mid/ask, iv_lower/upper, residual_*, status_*, greek_status,`  
`delta,gamma,vega,vanna,charm,volga,theta` (per-unit; optional `*_per_contract`),  
`known_at_ns=NULL, received_at_ns=NULL, published_at_ns=NULL, last_actual_update_ns=NULL, causal_feature_eligible=false`.

`valuation_expiry_cut`: ATM K/F/iv, call/put ATM, `w=σ²T`, k-bin medians, parity-F interval, identified/eligible counts.  
`valuation_cross_chain_cut`: NDX–NDXP–QQQ and SPX–SPXW–SPY ATM IV at matched date/cut/`k`/`T` class; unmatched = undefined.  
`valuation_coverage`: all mask counts by chain/cut/family/DTE/right/stage.

**Linkage:** `contract_id` = OI/quote identity. Formation = `cut_ns`. Quote clock = board `ts_event_ns` (sample, not last economic update). OI = same source-clock interval already on the board. No causal features.

**Fail if omitted:** later O16 cannot enforce `valuation_event_at ≤ trade`; clocks get laundered into `known_at`.

---

### 4. Empirical report now (not Context)

Reuse quote statistics grammar: equal-date means, block-5 bootstrap 1000, seed `20260908`, min 100 dates / 20 events, stages, year, chain, source_family, cut, right, DTE, k-bin.

Required: identified-IV and residual distributions; bid≤mid≤ask IV where monotonic; failure/censor fractions; ATM IV and `w`; smile/term by native expiry (no forced constant-tenor interpolate); 0DTE remainder-`T` and IV; near vs broad vs union on **same** `contract_id×cut`; lagged-cash vs cash-close; parity-F vs spot-carry; zero-r vs FRED tenor; QQQ/SPY dividend vs q0; AM vs PM clock on SPX/NDX; chronological train/dev/confirm (descriptive only).

**Exclude now:** C15/C16 forecasts, VRP vs OOF physical, O04 SVI, O03/O15–O20 flow, O07–O14/O23 holdings/nodes/max-pain, PnL, Location.

**Fail if omitted:** fixture-only “completion”; ATM that is really 0DTE; no source/assumption split.

---

### 5. Two consumer files

1. `/workspace/trading-research/src/trading_research/research/options_historical_valuation.py` — join + batch invert + coverage/ATM-term-cross reductions + report.  
2. `/workspace/trading-research/tests/test_options_historical_valuation.py` — join/status/cohort cases only.

**Existing API (do not wrap new solvers):**  
`years_from_nanoseconds`; `invert_quote_interval(bid,mid,ask,F,K,T,discount,right)`; `black_iv` / `black_greeks(F,K,T,sigma,discount,right,r)`; `invert_american_quote_interval` / `american_iv` / `american_greeks(S,K,T,sigma,r,right, dividend_times=, dividend_amounts=)`; `apply_contract_multiplier`; `enable_native` (same hash-bound binary `48bef3c9…`). No `response_cube` / grid refinement on the population (fixtures only). `n_space=128`.

**CPU/output:** consume quote boards (pilot16: 4.22M board / 68,922 quoted / 8 dates). Full ~`1677/8` scale if density holds — stream partitions (same 49 chain/year as quote18), emit identified+eligible rows + expiry/coverage aggregates, not a second 885M-row board. European vectorized; American only QQQ/SPY eligible. Own family budget (do not spend quote 105k). Peak RAM like quote (~4 GiB/worker). Pilot first on accepted `49e1cb18…` boards; full after quote18 boards exist.

**Independent cases (not numerics 44):** AM vs PM same strike/date; lagged vs same-date cash; ask-only / zero bid / crossed; QQQ discrete dividend vs q0; VIX missing spot does not drop SPY; listed-unquoted censor; near≠broad ATM; civil DTE=0 with `T>0`; `F_parity` without IV; null clocks stay null; multiplier not inside invert.

---

**Root next:** freeze protocol + schema IDs; implement the two files; register a bounded family; pilot on 16; full on 18 boards. O04 surface and C15/C16 *forecasts* stay later D1 branches.