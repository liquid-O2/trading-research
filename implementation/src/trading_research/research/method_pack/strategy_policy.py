"""User-authorized source reconstruction; thresholds frozen before this replay.

These operational choices implement the cited qualitative logic. They are
neither proprietary formulas nor evidence of the authors' orders/positions.
"""
EXCLUDED = {'GB-SCALP':frozenset({'small_size_recorded','source_scalp_management_recorded'}),
            'SIRES':frozenset({'daily_r_before'})}
POLICY = {
 'version':'1.1.0', 'purpose':'recreate strategy conditions from sources, excluding personal execution records',
 'exposure':'prior v2 engineering outcomes have been inspected; no holdout or profitability claim',
 'personal_exclusions':{k:sorted(v) for k,v in EXCLUDED.items()},
 'measurements':{
     'candle_endpoints':'same-contract published OHLCV after interval close; fill only after native H/L/V and all already-known endpoints match',
     'local_flow_price':'execution VWAP of first and last timestamp batches; causal, order independent, not an inferred exchange sequence',
     'flow_entry_price':'adverse-side observed price in the last execution timestamp batch; tick-valid research entry, not an actual fill',
     'absence':'all canonical records in an owned active-contract interval are enumerated; no execution does not imply missing data; market feed completeness remains separate',
     'prior_range':'fallback to all acquired published prior RTH continuous-chart bars; contract changes remain explicit and unadjusted; empty post-expiration c.0 mapping windows excluded with recorded expiry and roll-map identity; never substituted for native volume profile or depth'},
 'auction':{'source':'the-math-behind-auction-market-theory.pdf pp.4–11',
     'window_seconds':120,'high_effort_multiple':1.5,'low_efficiency':.2,'high_efficiency':.6,
     'replenishment_stop_fraction':.25,
     'response':'difference of first/last quarter-window execution VWAP; efficiency divided by window range',
     'inventory':'displayed depth-one additions/removals; removal less executions is an estimate, not identified cancels'},
 'gamma':{'source':'gex-framework.pdf pp.4–20; ny-am-session.pdf pp.8–9',
     'inventory_assumption':'call OI positive, put OI negative; model sign convention, not observed dealer inventory',
     'option_model':'European Black-Scholes, r=q=0, midquote implied volatility, 100 shares/contract',
     'expiry':'0DTE if quoted; otherwise nearest listed expiry explicitly identified as a front-expiry approximation',
     'oi':'latest prior-date snapshot only','max_quote_age_seconds':180,
     'quote_availability':'minute label plus 60 seconds; completed QQQ and NQ minute prices only',
     'KG1':'largest absolute signed gamma strike; same-time NQ/QQQ mapping; inferred key-gamma node, not proprietary KG1'},
 'pzone':{'source':'JJumboFX_Raw_X_Archive_v2.pdf pp.16–18,53–55,60–61',
     'lookback_sessions':500,'minimum_sessions':20,'anchors':['02:00','09:00','10:00'],
     'quantiles':[.70,.80], 'volume_filter':'historical session volume at least median of prior training sessions',
     'distance':'maximum up/down move from anchor to 16:00 divided by pre-anchor 60-minute range',
     'live_scale':'current completed pre-anchor 60-minute range; quarter-point outward rounding',
     'target':'frozen anchor price; support and resistance evaluated only toward anchor',
     'clock':'historical minute-bar training only, prior dates; live anchor uses event-time bars'},
 'macro':{'source':'data-engine.pdf pp.5–6','model':'equal mean of signed initial-release z scores: payroll positive, CPI negative; 12 prior initial observations',
     'output':'research context only; not proprietary C-score or an entry'},
}

def observation_scope(method,branch):
    if method=='STOIC-RISK' or branch in {'management','selected_order_configuration','supplied_selected_order'}:
        return 'personal_execution_out_of_scope'
    if method in {'JETBUNDLE-STATES','STOIC-DATA','REFILL-STUDY'}:return 'context_or_research'
    if branch in {'automatic_admission','case_description','reentry','mss_fvg_annotation'}:return 'supplemental_observation'
    return 'entry_setup'

POLICY['calendar']={'model':'regular NQ schedule with inferred New Year/Christmas RTH closures',
    'scope':'fixed-date New Year/Christmas closures, including Monday observance; Friday before Saturday New Year remains regular, corroborated by 390 native 2021-12-31 RTH minute records; other unverified holidays remain unavailable',
    'interpretation':'reconstruction calendar assumption, not newly recovered CME schedule evidence'}
