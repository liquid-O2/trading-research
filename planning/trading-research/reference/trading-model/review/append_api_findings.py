from pathlib import Path
import json
b=Path('/workspace/planning/trading-model');p=b/'review/external/skylit';inv=json.loads((p/'inventory.json').read_text()); sem=(p/'openapi-semantic-review.md').read_text()
find={
27:'Limited beta; multi-symbol heatmaps, up to 365-day replay, and live-only velocity. Benchmark horizon and entitlement are explicit dependencies.',
28:'Credits meter requests/streams separately from rate ceilings. Any future integration needs a fixed request budget and acquisition approval; no calls made here.',
29:'Strike values sum returned expirations; gamma/vanna alternatives; default 92 strikes around spot, maximum 400. No exposed per-expiry board tensor or published exposure-unit convention is established by this endpoint. Preserve asOf and universe truncation.',
30:'Nearest snapshot is not necessarily at-or-before requested time; replay omits velocity and returns no_data if absent. Reject future asOf; repeated earlier query does not reconstruct unarchived velocity.',
31:'One symbol per SSE connection, full snapshot plus separate velocity updates, reconnect lifecycle and concurrent-stream cap. Snapshot/velocity pairing needs source timestamps, deduplication, and stale-state handling.',
33:'Capped recent print feed with directional score, conviction multiplier, optional cluster fields and configurable weights. Completed-bucket freshness is described in shared API text. Compare transparent signed flow and calibrated specialists; capped rows cannot reconstruct total flow.',
34:'Arbitrary-window server aggregation avoids the print row cap and exposes counts and directional premium split. Reconcile aggregate to raw rows under identical exclusions and half-open boundaries.',
35:'Ticker tide distinguishes bucket and cumulative premium, volume, counts, and bucket start/end. Availability is after bucket completion; cumulative values must not be summed across bars.',
36:'Time-of-day mean/SD baseline uses 1–30 trailing trading days, default 20, with per-bucket sample count. Require anchor-relative history, zero-day handling and robust/expiry-conditioned alternatives.',
37:'5/30/60-minute flow versus baseline, z-scores, trend and optional as_of. Insufficient baseline is null. Verify replay-relative baseline and calibrate continuous values; no forced trend category agreement.',
38:'Top strikes by net/total premium or volume, premium-side shares and top-three concentration. Explicit denominators and untruncated universe are needed; concentration across correlated expiry rows must not double count.',
39:'Daily profile versus trailing 20-day distribution and five similar historical days. Intraday comparison to completed-day profiles would leak or mismatch time. Train-only nearest-neighbor retrieval with available prefixes is our alternative.',
40:'Sector/industry aggregation and contributors. Version sector membership; a contributor share of signed net premium can be unstable near zero. Compare gross and signed normalization, ETF flow and constituent flow separately.',
41:'Advance/decline refers to directional FIR threshold, not price breadth. The documented zero ratio when no decliners is a sentinel. Retain separate price breadth and options breadth with explicit no-denominator status.',
42:'Market totals, directional premium and same-time trailing premium RVOL; optional ticker subset changes universe. No historical anchor here implies live capture or independent reconstruction for causal benchmarks.',
43:'Market NCP/NPP are side-aware buying-minus-selling; relaxed script-exclusion variants differ. Bucket/cumulative values, multi-leg/deep-ITM toggles, price overlay and gap flags require versioned semantics.',
44:'Logical sweeps group same-contract multi-venue activity within one second. Intraday timeframe is documented as presently ignored; full-day extrapolated summary differs from capped returned sweeps. Never use that daily total earlier; grouping does not prove one parent order.',
45:'Documented composite = .4 VWF + .35 SDF + .25 FIR; VWF is actually premium-weighted trade score. Optional exponential decay defaults to 30-minute half-life. Compare transparent benchmark with out-of-sample calibrated mixtures; undocumented component details remain unresolved.',
46:'Volume/OI buckets produce claimed accumulation and new-position estimates; zero OI yields ratio zero. These do not identify opening/closing flow. Use explicit undefined-ratio masks and next-report OI labels with constrained uncertainty.',
47:'Moneyness buckets and premiums produce strategy labels, with deeper-OTM weighting. Preserve continuous forward moneyness/DTE/liquidity inputs; intent labels are inferred hypotheses, not observed positions.',
48:'Trade-level sentiment, urgency, confidence and intent derive from trade context/side. Canonical id matters when timestamps collide. Test side validity and calibration; opening_long_call is not a known execution instruction.',
49:'Ask/bid/mid shares here count trades, aggression divides aggressive trades by mid trades, and no-BBO joins mid. Capped ratio sentinels differ elsewhere. Keep counts/contracts/premium versions separate and unknown distinct from neutral.',
50:'Contract-level version of execution-side ratios; canonical option key encodes ticker, expiry, right and strike×1000. Resolve adjusted contracts through metadata rather than key text alone.',
51:'Call/put-aware directional buckets use contract volume and classify ask calls/bid puts as bullish. This is a signed-flow convention, not proof of directional intent or dealer side.',
52:'Same directional convention within one contract. Do not combine with chain ratios as independent evidence; maintain lineage and compare aggregation scales.',
53:'Active list means traded during the requested date, ranked by full-day premium, capped at 500. It is neither all listed contracts nor a valid morning point-in-time universe.',
54:'Prefix search uses date-active universe. Reference-only discovery; independent instrument definitions establish tradable/listed universe.',
55:'Here netPremium = gross callPremium − gross putPremium, unlike side-aware tide. call/put ratio returns zero with no puts. Rename semantically; do not join same-named fields blindly.',
56:'Trailing five-trading-day form of daily ranking. Window end must precede decision unless a causal partial-current-day form is reconstructed.',
57:'Bulk daily stats omit names without activity; lastPrice is date-end trade. Missing may be inactivity, not zero inventory; historical daily values are unavailable intraday.',
58:'Single-underlying daily stats share the same availability and missing-activity limitations.',
59:'Underlying chart aggregates options activity plus boundary stock price; baseline slots may be absent. Each bar covers [start,end). It is not ordinary underlying-price OHLCV.',
60:'Enriched rows mix event/ingestion timestamps, optional later IV, evolving clusters/strategies, daily volume and OI. Whitelist causal fields and retain feature-specific known_at; exclude nextIv at trade time.',
61:'Strike distribution combines call/put premium, volume/OI and max-pain estimate. Expiry mixtures alter payoff geometry; max pain is benchmark-only, not a dealer objective or deterministic settlement forecast.',
62:'Strike→expiry breakdown retains an essential second dimension lost by summed boards. Use stable contract identities and expiry-specific normalization before cross-expiry pooling.',
63:'Expirations list includes those traded that date. Use definitions to include listed but inactive maturities; avoid full-day activity selection at morning decisions.',
64:'Date/expiry snapshot uses last prices/IV and can suppress low-volume strikes. No intraday as-of guarantee follows from date. Build surfaces from valid contemporaneous quotes and preserve coverage mask.',
65:'Daily history has activity days only. Calendar-complete joins distinguish holiday, inactive and missing feed, and respect next-available daily publication.',
66:'Underlying RVOL exposes actual baseline-day count and nullable baseline. Normalize against causally comparable same-time samples, not complete-day hindsight; compare robust shrinkage for sparse histories.',
67:'Daily contract ranking has broad filters and a row cap. Retain as a display benchmark; use all eligible point-in-time candidates for model selection and log rejected rows.',
68:'Five-day contract ranking inherits daily selection and expiry-aging issues. Do not repeatedly count the same contract as independent evidence.',
69:'Unusual-volume scanner defaults to previous calendar day, not previous trading day, and requires baseline volume. Specify date explicitly; sparse/new contracts need a separate model and missing-baseline status.',
70:'Unusual-OI opening/closing tags refer to net reported OI change, not individual trade open/close flags. Align report date/publication time and distinguish exercises, expiry, revisions and observed volume.',
71:'Bulk contract stats omit inactive contracts. Keep missing activity distinct from missing OI, contract delisting and feed failure.',
72:'Single-contract daily stats have the same publication and incompleteness constraints.',
73:'Contract bars preserve granular side buckets, single-leg volume, cumulative daily totals, VWAP and IV. Reconcile to raw trades; side sub-buckets and cumulative totals require disjoint aggregation.',
74:'Contract-scoped enriched trades offer microsecond timestamp detail absent in some underlying views. Preserve source precision and independent ordering/receipt uncertainty; same timestamp alone is not a unique trade.',
75:'Contract daily history combines OI changes, executions, VWAP and IV. Use as future labels or lagged features according to individual publication rules.',
76:'Contract RVOL requires expiry-age, listing-age, moneyness and sample-count controls. A ticker-level baseline is an explicit alternative, not interchangeable history for the same contract.',
77:'TRF prints have shares/notional and venue but no side/BBO/Greeks. Date-span and offset caps, plus heuristic hasMore, need complete pagination checks. TRF is a reporting channel, not proof of a dark-pool execution.',
78:'Largest individual prints over a calendar-day window are candidate anchors; as_of_date includes that whole date. Filter by receipt before a decision and test placebo levels; size is not guaranteed support/resistance.',
79:'OpenAPI metadata is a reproducible interface reference, not an additional market signal.',
80:'MCP wraps the same REST data and credits, with session/concurrency limits. No new predictive information or independent evidence comes from transport.',
81:'Access requires account entitlement; setup instructions were read but not executed. No agent-driven paid market-data queries were initiated.',
82:'Catalog advertises 40 tools while overview says 38. This illustrates version drift; discover actual capabilities only in a separately authorized integration, and record schema versions.',
83:'Example workflows combine heatmaps and flow, but their wording treats positioning/intent more confidently than the data identifies. Retain joint-feature experiments with measurement uncertainty.',
84:'Nexus documentation is coming soon; no substantive algorithm is available. Social-layer dependency deferred and unnecessary for the proposed core.',
92:'OHLCV history uses [from,to), bar-open timestamps, sided equity volume where available, and countback precedence. RTH is default; history limits depend on storage tier. Larger bars cannot reconstruct trade-sequence CVD extrema.',
93:'Ranked symbol picker is reference metadata; canonical id differs from display ticker. No evidence of complete historical listing universe.',
94:'Symbol resolution includes price scale/session/timezone. Validate these against contract records and historical changes rather than relying on current metadata for all history.',
95:'Configuration exposes history caps and can be cached while server limits change. Future adapter should version capability snapshots and handle authoritative rejection without blind retries.',
96:'Server time measures the vendor clock, not exchange-event or local receipt time. Use for clock diagnostics only.'}
with (b/'EXTERNAL_RESEARCH.md').open('a') as f:
 f.write('## API and integration semantics\n\nThe 55 generated OpenAPI pages received a focused semantic review of unique endpoint descriptions, input defaults, field definitions and constraints using [deduplicated semantic extraction](review/external/skylit/openapi-semantic-review.md). Repeated boilerplate and example payloads were not counted as additional full-text review. The complete original pages remain captured. Intro/authentication and all four MCP pages plus Nexus were read in full. This scope is distinct from the exhaustive full-text review of every supplied source file.\n\n| Finding | Source | Mechanism, limitation, and proposed disposition |\n|---|---|---|\n')
 for n,txt in find.items():
  d=inv['pages'][n-1];f.write(f"| EXT-{n:03d} | [{d['id']}]({d['url']}) | {txt} |\n")
for d in inv['pages']:
 n=int(d['id'][3:])
 if n in [27,28,80,81,82,83,84]:d['text_reviewed']=[[1,d['readable_lines']]];d['review_method']='Full readable Markdown text.'
 elif '## SKY'+d['id'][3:] in sem:d['review_method']='Focused unique OpenAPI endpoint/field semantic review; repeated boilerplate/examples not full-text reviewed.';d['semantic_reviewed']=True
(p/'inventory.json').write_text(json.dumps(inv,indent=2))
print('appended',len(find),'API/metadata findings')
