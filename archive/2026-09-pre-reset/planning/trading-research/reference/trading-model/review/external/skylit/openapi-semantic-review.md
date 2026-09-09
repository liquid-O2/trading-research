## SKY029 https://docs.skylit.ai/api-reference/heatmap/live-per-strike-heatmap-one-or-more-symbols
paths./v1/heatmap.get summary: Live per-strike heatmap (one or more symbols)
paths./v1/heatmap.get description: Current per-strike heatmap for one or more symbols at the latest snapshot. Includes the live `velocityPct` per strike. Pass multiple comma-separated symbols for a single cross-asset (Trinity) call. 
paths./v1/heatmap.get.parameters ref Symbols
paths./v1/heatmap.get.parameters ref Metric
paths./v1/heatmap.get.parameters ref MaxStrikes
components.parameters.Symbols description: One ticker, or a comma-separated list for a single cross-asset call (e.g. `SPY` or `SPY,SPX,QQQ`). Each is returned as an element of `data.symbols`. 
components.parameters.Metric description: Which Greek exposure to return per strike.
components.parameters.Metric.schema enum: ['gamma', 'vanna']
components.parameters.Metric.schema default: gamma
components.parameters.MaxStrikes description: Maximum number of strikes around spot to return.
components.parameters.MaxStrikes.schema default: 92
components.parameters.MaxStrikes.schema minimum: 1
components.parameters.MaxStrikes.schema maximum: 400
components.schemas.SymbolHeatmap.properties.symbol description: Canonical ticker for the returned data.
components.schemas.SymbolHeatmap.properties.asOf description: RFC3339 timestamp of the snapshot actually returned (nearest to the requested instant).
components.schemas.SymbolHeatmap.properties.spot description: Spot price at the snapshot.
components.schemas.SymbolHeatmap.properties.priceChange description: Spot minus previous close.
components.schemas.SymbolHeatmap.properties.expirations description: Expiration dates (YYYY-MM-DD) contributing to each strike's net value.
components.schemas.SymbolHeatmap.properties.strikes description: Per-strike nodes, ordered by strike ascending.
components.schemas.SymbolHeatmap.properties.strikes.items ref StrikeNode
components.schemas.Meta.properties.metric enum: ['gamma', 'vanna']
components.schemas.Meta.properties.mode enum: ['live', 'historical']
components.schemas.Meta.properties.cached description: True if served from the in-process cache.
components.schemas.StrikeNode.properties.strike description: Strike price.
components.schemas.StrikeNode.properties.value description: Net exposure for the selected `metric` at this strike (summed across the returned expirations).
components.schemas.StrikeNode.properties.nodeType description: Skylit's node classification for this strike.
components.schemas.StrikeNode.properties.nodeType enum: ['king', 'gatekeeper', 'pika', 'barney', 'significant', 'normal']
components.schemas.StrikeNode.properties.velocityPct description: Live percent change of this strike's value over the velocity window. Present on `/v1/heatmap` only; omitted on `/v1/historical`. 
components.schemas.Error.properties.error.properties.code description: Stable, machine-readable error code.
components.schemas.Error.properties.error.properties.message description: Human-readable explanation.
components.securitySchemes.bearerApiKey description: Skylit API key in the `Authorization` header (`Authorization: Bearer <key>`). `X-API-Key` is also accepted. 

## SKY030 https://docs.skylit.ai/api-reference/heatmap/replay-per-strike-heatmap-at-a-past-instant-one-or-more-symbols
paths./v1/historical.get summary: Replay per-strike heatmap at a past instant (one or more symbols)
paths./v1/historical.get description: The snapshot nearest `at` for one or more symbols — same shape as `/v1/heatmap` minus `velocityPct` (velocity is live-only). `at` may be up to 365 days in the past; if no snapshot exists at/near that instant the response is `404` with `code: no_data`. 
paths./v1/historical.get.parameters ref Symbols
paths./v1/historical.get.parameters.at description: RFC3339 instant to replay (e.g. `2026-03-05T10:01:00Z`). Up to 365 days back.
paths./v1/historical.get.parameters ref Metric
paths./v1/historical.get.parameters ref MaxStrikes
components.schemas.SymbolHeatmap.properties.strikes.items ref StrikeNode

## SKY031 https://docs.skylit.ai/api-reference/heatmap/live-sse-stream-one-symbol-per-connection
paths./v1/stream.get summary: Live SSE stream (one symbol per connection)
paths./v1/stream.get description: A **Server-Sent Events** (`text/event-stream`) feed of live per-strike heatmap updates for **one** symbol. Open one connection per symbol.  **Events:** - `connected` — handshake, payload `{symbol, creditsRemaining}`. - `initial_data` — current heatmap snapshot on connect. - `snapshot_update` — full heatmap on each change. - `velocity_update` — per-strike % change. - `credits` — emitted every minute boundary, payload `{remaining}`. - `closed` — stream terminates with `{reason: "insufficient_credits"   | "account_suspended" | "credit_check_failed"}`. - `reconnect` — server is recycling the connection (after ~1h),   payload `{reason: "max_duration"}`. Reconnect to continue. - `: keepalive` comment every 30s for proxy keepalive.  **Pricing.** 1 credit on connect (charged before the SSE upgrade — an under-funded client gets a clean `402` HTTP response, not a half-open stream), then 1 credit per minute open. The per-minute ticker emits `event: credits {remaining: N}` after each successful debit so clients can budget the next minute.  **Concurrency.** Up to 5 concurrent streams per customer per pod. Exceeding the cap returns `429` `stream_limit_reached`.  > OpenAPI is request/response-oriented and can't fully model an event > stream. See [docs/api-credits.md](https://github.com/SkylitAI/skylit-main/blob/main/docs/api-credits.md#live-stream-v1stream) > for the full stream lifecycle. 
paths./v1/stream.get.parameters.symbol description: Single ticker to stream (e.g. `SPY`). One symbol per connection.
paths./v1/stream.get.parameters ref Metric
paths./v1/stream.get.parameters ref MaxStrikes

## SKY033 https://docs.skylit.ai/api-reference/flow/raw-flow-feed-for-a-ticker-flow-score-+-flowbonus-per-trade
paths./v1/flow/{ticker}.get summary: Raw flow feed for a ticker (Flow Score + FlowBonus per trade)
paths./v1/flow/{ticker}.get description: Returns the most recent options trades for `{ticker}` within the requested timeframe, each scored on Skylit's directional Flow Score (-100 → +100) and conviction-weighted FlowBonus. The response also includes timeframe-level VWF / SDF / FIR aggregates. 
paths./v1/flow/{ticker}.get.parameters ref Ticker
paths./v1/flow/{ticker}.get.parameters ref Timeframe
paths./v1/flow/{ticker}.get.parameters.limit description: Max trades returned. Server caps this at 500.
paths./v1/flow/{ticker}.get.parameters.limit.schema default: 100
paths./v1/flow/{ticker}.get.parameters.limit.schema minimum: 1
paths./v1/flow/{ticker}.get.parameters.limit.schema maximum: 500
paths./v1/flow/{ticker}.get.parameters.min_premium description: Minimum total premium per trade (USD).
paths./v1/flow/{ticker}.get.parameters.option_type description: Filter to calls or puts. `all` returns both.
paths./v1/flow/{ticker}.get.parameters.option_type.schema enum: ['call', 'put', 'all']
paths./v1/flow/{ticker}.get.parameters.option_type.schema default: all
paths./v1/flow/{ticker}.get.parameters.trade_type description: Filter by trade type. Comma-separated for multiple.
paths./v1/flow/{ticker}.get.parameters.trade_type.schema enum: ['sweep', 'multi_leg', 'all']
paths./v1/flow/{ticker}.get.parameters.trade_type.schema default: all
paths./v1/flow/{ticker}.get.parameters.moneyness description: Moneyness category filter. Comma-separated for multiple (e.g. `otm,deep_otm`). Unknown tokens are ignored. 
paths./v1/flow/{ticker}.get.parameters.moneyness.schema enum: ['deep_itm', 'itm', 'atm', 'otm', 'deep_otm', 'all']
paths./v1/flow/{ticker}.get.parameters.moneyness.schema default: all
paths./v1/flow/{ticker}.get.parameters.start_time description: Optional lower bound for the trade window. Accepts RFC 3339 (`2026-05-27T13:30:00Z`) or Unix seconds. Omit to use the timeframe. 
paths./v1/flow/{ticker}.get.parameters.end_time description: Optional upper bound (RFC 3339 or Unix seconds).
paths./v1/flow/{ticker}.get.parameters.max_premium description: Maximum total premium per trade (USD).
paths./v1/flow/{ticker}.get.parameters.min_contracts description: Minimum contract size per trade.
paths./v1/flow/{ticker}.get.parameters.min_contracts.schema minimum: 0
paths./v1/flow/{ticker}.get.parameters.max_contracts description: Maximum contract size per trade.
paths./v1/flow/{ticker}.get.parameters.max_contracts.schema minimum: 0
paths./v1/flow/{ticker}.get.parameters.single_leg_only description: If `true`, exclude trades flagged as part of a multi-leg structure.
paths./v1/flow/{ticker}.get.parameters.single_leg_only.schema default: False
paths./v1/flow/{ticker}.get.parameters.min_dte description: Minimum days to expiration.
paths./v1/flow/{ticker}.get.parameters.max_dte description: Maximum days to expiration.
paths./v1/flow/{ticker}.get.parameters.min_strike description: Minimum strike price (inclusive).
paths./v1/flow/{ticker}.get.parameters.max_strike description: Maximum strike price (inclusive).
paths./v1/flow/{ticker}.get.parameters.expiration description: Filter to a single expiration date (YYYY-MM-DD).
paths./v1/flow/{ticker}.get.parameters.conviction_weights description: Optional JSON object overriding the Flow Score conviction weights. Weights must be non-negative and sum to within 0.95–1.05, else 400. 
paths./v1/flow/{ticker}.get.parameters.min_flow_score description: Filter to trades with `flowScore` ≥ this value (-100..100).
paths./v1/flow/{ticker}.get.parameters.min_flow_score.schema minimum: -100
paths./v1/flow/{ticker}.get.parameters.min_flow_score.schema maximum: 100
paths./v1/flow/{ticker}.get.parameters.min_flow_bonus description: Filter to trades with `flowBonus` ≥ this value.
paths./v1/flow/{ticker}.get.parameters.min_flow_bonus.schema minimum: 0
paths./v1/flow/{ticker}.get.parameters.min_rvol description: Filter to trades with relative volume ≥ this multiple.
paths./v1/flow/{ticker}.get.parameters.min_rvol.schema minimum: 0
paths./v1/flow/{ticker}.get.parameters.include_clusters description: If `true`, attach `cluster*` fields when a trade is part of a multi-leg cluster (sweep, condor, etc.). 
paths./v1/flow/{ticker}.get.parameters.include_clusters.schema default: True
paths./v1/flow/{ticker}.get.parameters.date description: Trading date (YYYY-MM-DD). Defaults to current trading date.
components.parameters.Ticker description: Underlying ticker symbol (uppercase, e.g. `SPY`, `AAPL`).
components.parameters.Timeframe description: Trailing window label for the request. Supported values: `5m`, `15m`, `1h`, `4h`, `1d`. 
components.parameters.Timeframe.schema enum: ['5m', '15m', '1h', '4h', '1d']
components.parameters.Timeframe.schema default: 1h
components.schemas.FlowSuccess.properties.data ref FlowResponse
components.schemas.FlowSuccess.properties.meta ref Meta
components.schemas.FlowResponse.properties.trades.items ref FlowTradeItem
components.schemas.FlowResponse.properties.aggregate ref AggregateScores
components.schemas.FlowResponse.properties.tradeCount minimum: 0
components.schemas.FlowResponse.properties.sweepCount minimum: 0
components.schemas.FlowResponse.properties.queryTimeMs minimum: 0
components.schemas.Meta.properties.timestamp description: Server-side timestamp the response was generated at.
components.schemas.Meta.properties.requestId description: Short opaque ID for log correlation.
components.schemas.Error.properties.error.properties.code description: Stable machine-readable error code. Common values: `BAD_REQUEST`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `RATE_LIMITED`, `QUOTA_EXCEEDED`, `INTERNAL_ERROR`, `UNAVAILABLE`. 
components.schemas.Error.properties.error.properties.message description: Human-readable explanation. Wording may evolve; key off `code`.
components.schemas.FlowTradeItem description: One options trade with full Skylit scoring + context. A subset of the most-relevant fields is documented inline; the response may add new fields under additive evolution rules. 
components.schemas.FlowTradeItem.properties.optionType enum: ['CALL', 'PUT']
components.schemas.FlowTradeItem.properties.dte minimum: 0
components.schemas.FlowTradeItem.properties.dteCategory enum: ['zero_dte', 'weekly', 'monthly', 'leap']
components.schemas.FlowTradeItem.properties.contracts minimum: 1
components.schemas.FlowTradeItem.properties.premium description: Total premium in USD.
components.schemas.FlowTradeItem.properties.price description: Trade price per contract.
components.schemas.FlowTradeItem.properties.liquidityGrade enum: ['A', 'B', 'C', 'D', 'F']
components.schemas.FlowTradeItem.properties.exchangeCount nullable: True
components.schemas.FlowTradeItem.properties.exchangeCount description: Number of distinct OPRA exchanges that filled the order.
components.schemas.FlowTradeItem.properties.moneyness enum: ['DEEP_ITM', 'ITM', 'ATM', 'OTM', 'DEEP_OTM']
components.schemas.FlowTradeItem.properties.delta nullable: True
components.schemas.FlowTradeItem.properties.notionalDeltaExposure nullable: True
components.schemas.FlowTradeItem.properties.openInterest minimum: 0
components.schemas.FlowTradeItem.properties.dailyVolume minimum: 0
components.schemas.FlowTradeItem.properties.volOiRatio nullable: True
components.schemas.FlowTradeItem.properties.sizeOiRatio nullable: True
components.schemas.FlowTradeItem.properties.rvol nullable: True
components.schemas.FlowTradeItem.properties.rvolCategory nullable: True
components.schemas.FlowTradeItem.properties.iv nullable: True
components.schemas.FlowTradeItem.properties.ivChangePct nullable: True
components.schemas.FlowTradeItem.properties.relativePremium description: Premium relative to the contract's average premium.
components.schemas.FlowTradeItem.properties.scores ref FlowTradeScores
components.schemas.FlowTradeItem.properties.cluster ref ClusterInfo
components.schemas.AggregateScores description: Window-level scoring components.
components.schemas.AggregateScores.properties.vwf description: Volume-Weighted Flow score (-100..+100).
components.schemas.AggregateScores.properties.sdf description: Sweep-Dominant Flow score (-100..+100).
components.schemas.AggregateScores.properties.fir description: Flow Imbalance Ratio (-100..+100).
components.schemas.FlowTradeScores description: Per-trade scoring outputs (PRD Section 10).
components.schemas.FlowTradeScores.properties.flowScore description: Composite directional score (-100..+100).
components.schemas.FlowTradeScores.properties.flowScore minimum: -100
components.schemas.FlowTradeScores.properties.flowScore maximum: 100
components.schemas.FlowTradeScores.properties.flowBonus description: Conviction bonus (0..+100).
components.schemas.FlowTradeScores.properties.flowBonus minimum: 0
components.schemas.FlowTradeScores.properties.flowBonus maximum: 100
components.schemas.FlowTradeScores.properties.baseDirection description: Pre-conviction directional score (-100..+100).
components.schemas.FlowTradeScores.properties.convictionMultiplier description: Multiplier applied to base direction to yield `flowScore`.
components.schemas.ClusterInfo description: Present when `includeClusters=true` and the trade is part of a sweep, condor, or other multi-leg cluster. 
components.schemas.ClusterInfo.properties.clusterTradeCount minimum: 1
components.schemas.ClusterInfo.properties.clusterTimeSpanSeconds minimum: 0
components.securitySchemes.bearerApiKey description: Skylit API key in the `Authorization` header (`Authorization: Bearer fs_live_<key>`). `X-API-Key` is also accepted. 

## SKY034 https://docs.skylit.ai/api-reference/flow/aggregate-flow-over-an-arbitrary-[start-end]-window
paths./v1/flow/{ticker}/aggregate.get summary: Aggregate flow over an arbitrary [start, end] window
paths./v1/flow/{ticker}/aggregate.get description: Server-side aggregation across an arbitrary `[startTime, endTime]` window — no row cap. Returns trade/sweep counts, VWF/SDF/FIR, and a bullish/bearish/neutral premium split with a one-line interpretation. Useful for arbitrary slicing without paging the full trade list. 
paths./v1/flow/{ticker}/aggregate.get.parameters ref Ticker
paths./v1/flow/{ticker}/aggregate.get.parameters ref StartTime
paths./v1/flow/{ticker}/aggregate.get.parameters ref EndTime
paths./v1/flow/{ticker}/aggregate.get.parameters.option_type.schema enum: ['call', 'put', 'all']
paths./v1/flow/{ticker}/aggregate.get.parameters.option_type.schema default: all
paths./v1/flow/{ticker}/aggregate.get.parameters.exclude_multi_leg description: Exclude trades flagged as part of a multi-leg structure.
paths./v1/flow/{ticker}/aggregate.get.parameters.exclude_multi_leg.schema default: False
paths./v1/flow/{ticker}/aggregate.get.parameters.min_dte.schema minimum: 0
paths./v1/flow/{ticker}/aggregate.get.parameters.max_dte.schema minimum: 0
components.parameters.StartTime description: Lower bound of the window. Accepts RFC 3339 (`2026-05-27T13:30:00Z`) or Unix seconds. 
components.parameters.EndTime description: Upper bound of the window (RFC 3339 or Unix seconds).
components.schemas.FlowAggregateSuccess.properties.data ref FlowAggregateResponse
components.schemas.FlowAggregateSuccess.properties.meta ref Meta
components.schemas.FlowAggregateResponse.properties.tradeCount minimum: 0
components.schemas.FlowAggregateResponse.properties.sweepCount minimum: 0
components.schemas.FlowAggregateResponse.properties.aggregate ref WindowAggregateScores
components.schemas.FlowAggregateResponse.properties.premiumSplit ref WindowPremiumSplit
components.schemas.FlowAggregateResponse.properties.interpretation ref WindowInterpretation
components.schemas.FlowAggregateResponse.properties.queryTimeMs minimum: 0
components.schemas.WindowAggregateScores.allOf ref AggregateScores
components.schemas.WindowAggregateScores.allOf.properties.composite description: Composite roll-up of VWF/SDF/FIR for the window.
components.schemas.WindowPremiumSplit.properties.bullishCount minimum: 0
components.schemas.WindowPremiumSplit.properties.bearishCount minimum: 0
components.schemas.WindowPremiumSplit.properties.neutralCount minimum: 0
components.schemas.WindowInterpretation.properties.bias enum: ['bullish', 'bearish', 'neutral', 'mixed']
components.schemas.WindowInterpretation.properties.signalStrength enum: ['strong', 'moderate', 'weak']

## SKY035 https://docs.skylit.ai/api-reference/flow/per-ticker-net-premium-time-series-"flow-tide"
paths./v1/flow/{ticker}/tide.get summary: Per-ticker net-premium time series ("flow tide")
paths./v1/flow/{ticker}/tide.get description: Bucketed bullish vs bearish premium time series for a single ticker, with cumulative net premium and per-bucket VWF/SDF/FIR. The ticker-level analogue of `/v1/market/tide`. 
paths./v1/flow/{ticker}/tide.get.parameters ref Ticker
paths./v1/flow/{ticker}/tide.get.parameters ref StartTime
paths./v1/flow/{ticker}/tide.get.parameters ref EndTime
paths./v1/flow/{ticker}/tide.get.parameters ref Bucket
paths./v1/flow/{ticker}/tide.get.parameters.option_type.schema enum: ['call', 'put', 'all']
paths./v1/flow/{ticker}/tide.get.parameters.option_type.schema default: all
paths./v1/flow/{ticker}/tide.get.parameters.exclude_multi_leg.schema default: False
paths./v1/flow/{ticker}/tide.get.parameters.min_dte.schema minimum: 0
paths./v1/flow/{ticker}/tide.get.parameters.max_dte.schema minimum: 0
components.parameters.Bucket description: Bucket size for the time series. Pre-aggregated tables back the sub-hourly resolutions. Coarser buckets (`1d`, `1w`) are rejected on intraday endpoints. 
components.parameters.Bucket.schema enum: ['1min', '5min', '15min', '30min', '1h']
components.parameters.Bucket.schema default: 5min
components.schemas.FlowTideSuccess.properties.data ref FlowTideResponse
components.schemas.FlowTideSuccess.properties.meta ref Meta
components.schemas.FlowTideResponse.properties.bars.items ref FlowTideBar
components.schemas.FlowTideResponse.properties.queryTimeMs minimum: 0
components.schemas.FlowTideBar.properties.timestamp description: Unix seconds (bucket start).
components.schemas.FlowTideBar.properties.timestampEnd description: Unix seconds (bucket end).
components.schemas.FlowTideBar.properties.bullishVolume minimum: 0
components.schemas.FlowTideBar.properties.bearishVolume minimum: 0
components.schemas.FlowTideBar.properties.tradeCount minimum: 0
components.schemas.FlowTideBar.properties.sweepCount minimum: 0

## SKY036 https://docs.skylit.ai/api-reference/flow/trailing-per-time-of-day-flow-baseline-avg-+-stddev
paths./v1/flow/{ticker}/baseline.get summary: Trailing per-time-of-day flow baseline (avg + stddev)
paths./v1/flow/{ticker}/baseline.get description: Time-of-day baseline buckets for `{ticker}` — average and standard deviation of trade count, premium, and FIR per intraday bucket over a configurable lookback window. The reference distribution behind `/v1/flow/{ticker}/momentum` z-scores. 
paths./v1/flow/{ticker}/baseline.get.parameters ref Ticker
paths./v1/flow/{ticker}/baseline.get.parameters ref Bucket
paths./v1/flow/{ticker}/baseline.get.parameters.lookback_days description: Trailing window size in trading days.
paths./v1/flow/{ticker}/baseline.get.parameters.lookback_days.schema default: 20
paths./v1/flow/{ticker}/baseline.get.parameters.lookback_days.schema minimum: 1
paths./v1/flow/{ticker}/baseline.get.parameters.lookback_days.schema maximum: 30
paths./v1/flow/{ticker}/baseline.get.parameters.start_time_of_day description: Lower bound of intraday window (HH:MM ET).
paths./v1/flow/{ticker}/baseline.get.parameters.start_time_of_day.schema default: 09:30
paths./v1/flow/{ticker}/baseline.get.parameters.end_time_of_day description: Upper bound of intraday window (HH:MM ET).
paths./v1/flow/{ticker}/baseline.get.parameters.end_time_of_day.schema default: 16:00
paths./v1/flow/{ticker}/baseline.get.parameters.min_dte.schema minimum: 0
paths./v1/flow/{ticker}/baseline.get.parameters.max_dte.schema minimum: 0
components.schemas.BaselineSuccess.properties.data ref BaselineResponse
components.schemas.BaselineSuccess.properties.meta ref Meta
components.schemas.BaselineResponse.properties.buckets.items ref BaselineBucket
components.schemas.BaselineResponse.properties.queryTimeMs minimum: 0
components.schemas.BaselineBucket.properties.daysCount minimum: 0

## SKY037 https://docs.skylit.ai/api-reference/flow/live-momentum-signal-vs-baseline-5m-30m-1h-windows
paths./v1/flow/{ticker}/momentum.get summary: Live momentum signal vs baseline (5m / 30m / 1h windows)
paths./v1/flow/{ticker}/momentum.get description: Compares the current 5-minute, 30-minute, and 1-hour flow against the trailing per-time-of-day baseline (`/v1/flow/{ticker}/baseline`). Returns z-scores for the 5-minute window and a one-token `trend` classification. 
paths./v1/flow/{ticker}/momentum.get.parameters ref Ticker
paths./v1/flow/{ticker}/momentum.get.parameters.as_of description: Replay anchor. Accepts RFC 3339 or Unix seconds. Defaults to "now".
paths./v1/flow/{ticker}/momentum.get.parameters.lookback_days description: Trailing window size in trading days.
paths./v1/flow/{ticker}/momentum.get.parameters.lookback_days.schema default: 20
paths./v1/flow/{ticker}/momentum.get.parameters.lookback_days.schema minimum: 1
paths./v1/flow/{ticker}/momentum.get.parameters.lookback_days.schema maximum: 30
paths./v1/flow/{ticker}/momentum.get.parameters.min_dte.schema minimum: 0
paths./v1/flow/{ticker}/momentum.get.parameters.max_dte.schema minimum: 0
components.schemas.MomentumSuccess.properties.data ref MomentumResponse
components.schemas.MomentumSuccess.properties.meta ref Meta
components.schemas.MomentumResponse.properties.current5m ref MomentumWindowMetrics
components.schemas.MomentumResponse.properties.current30m ref MomentumWindowMetrics
components.schemas.MomentumResponse.properties.current1h ref MomentumWindowMetrics
components.schemas.MomentumResponse.properties.baseline.oneOf ref MomentumBaselineRef
components.schemas.MomentumResponse.properties.baseline description: Null when there are insufficient baseline days available.
components.schemas.MomentumResponse.properties.signals ref MomentumSignals
components.schemas.MomentumResponse.properties.queryTimeMs minimum: 0
components.schemas.MomentumWindowMetrics.properties.tradeCount minimum: 0
components.schemas.MomentumBaselineRef.properties.daysInBaseline minimum: 0
components.schemas.MomentumSignals.properties.firZscore5m description: Z-score of the current 5-minute FIR vs baseline.
components.schemas.MomentumSignals.properties.premiumZscore5m description: Z-score of the current 5-minute premium vs baseline.
components.schemas.MomentumSignals.properties.trend enum: ['accelerating', 'steady', 'fading', 'neutral']
components.schemas.MomentumSignals.properties.interpretation description: One-sentence human-readable summary.

## SKY038 https://docs.skylit.ai/api-reference/flow/strike-level-flow-concentration
paths./v1/flow/{ticker}/strikes.get summary: Strike-level flow concentration
paths./v1/flow/{ticker}/strikes.get description: Where the directional money is going for `{ticker}`. Top-N strikes by selected ordering (premium, net premium, volume, etc.) with bullish/bearish premium split, ask/bid mix, and OI context. Includes a top-3 concentration summary. 
paths./v1/flow/{ticker}/strikes.get.parameters ref Ticker
paths./v1/flow/{ticker}/strikes.get.parameters ref StartTime
paths./v1/flow/{ticker}/strikes.get.parameters ref EndTime
paths./v1/flow/{ticker}/strikes.get.parameters.top_n description: Number of strikes to return.
paths./v1/flow/{ticker}/strikes.get.parameters.top_n.schema default: 20
paths./v1/flow/{ticker}/strikes.get.parameters.top_n.schema minimum: 1
paths./v1/flow/{ticker}/strikes.get.parameters.top_n.schema maximum: 100
paths./v1/flow/{ticker}/strikes.get.parameters.right description: Restrict to calls or puts only.
paths./v1/flow/{ticker}/strikes.get.parameters.right.schema enum: ['call', 'put']
paths./v1/flow/{ticker}/strikes.get.parameters.order_by.schema enum: ['net_premium', 'total_premium', 'volume']
paths./v1/flow/{ticker}/strikes.get.parameters.order_by.schema default: net_premium
paths./v1/flow/{ticker}/strikes.get.parameters.min_dte.schema minimum: 0
paths./v1/flow/{ticker}/strikes.get.parameters.max_dte.schema minimum: 0
components.schemas.StrikesSuccess.properties.data ref StrikesResponse
components.schemas.StrikesSuccess.properties.meta ref Meta
components.schemas.StrikesResponse.properties.byStrike.items ref StrikeBreakdown
components.schemas.StrikesResponse.properties.concentration ref StrikesConcentration
components.schemas.StrikeBreakdown.properties.right enum: ['C', 'P']
components.schemas.StrikeBreakdown.properties.tradeCount minimum: 0
components.schemas.StrikeBreakdown.properties.volume minimum: 0
components.schemas.StrikeBreakdown.properties.askPct description: Share of premium executed at-or-above ask (aggressive buying).
components.schemas.StrikeBreakdown.properties.bidPct description: Share of premium executed at-or-below bid (aggressive selling).
components.schemas.StrikeBreakdown.properties.openInterest minimum: 0
components.schemas.StrikesConcentration.properties.top3StrikesShare description: Share (0–1) of the window's premium concentrated in the top 3 strikes.

## SKY039 https://docs.skylit.ai/api-reference/flow/todays-flow-vs-trailing-average-with-similar-days-lookback
paths./v1/flow/{ticker}/historical-compare.get summary: Today's flow vs trailing average (with similar-days lookback)
paths./v1/flow/{ticker}/historical-compare.get description: Compares the current trading day's premium / volume / net premium / call-put ratio against the trailing 20-trading-day average for the same ticker. Returns absolute deltas, percentile rankings, and the five most-similar past trading days. 
paths./v1/flow/{ticker}/historical-compare.get.parameters ref Ticker
paths./v1/flow/{ticker}/historical-compare.get.parameters.date description: Date to evaluate (YYYY-MM-DD). Defaults to today.
components.schemas.HistoricalCompareSuccess.properties.data ref HistoricalCompareResponse
components.schemas.HistoricalCompareSuccess.properties.meta ref Meta
components.schemas.HistoricalCompareResponse.properties.current ref CurrentMetrics
components.schemas.HistoricalCompareResponse.properties.historical ref HistoricalMetrics
components.schemas.HistoricalCompareResponse.properties.vsAverage ref VsAverage
components.schemas.HistoricalCompareResponse.properties.percentileRankings ref PercentileRankings
components.schemas.HistoricalCompareResponse.properties.similarDays.items ref SimilarDay
components.schemas.CurrentMetrics.properties.totalVolume minimum: 0
components.schemas.CurrentMetrics.properties.callVolume minimum: 0
components.schemas.CurrentMetrics.properties.putVolume minimum: 0
components.schemas.HistoricalMetrics.properties.daysAnalyzed minimum: 0
components.schemas.VsAverage.properties.premiumVsAvg description: Today's premium as a multiple of the historical average (1.0 = at average).
components.schemas.PercentileRankings.properties.premiumPercentile minimum: 0
components.schemas.PercentileRankings.properties.premiumPercentile maximum: 100
components.schemas.PercentileRankings.properties.volumePercentile minimum: 0
components.schemas.PercentileRankings.properties.volumePercentile maximum: 100
components.schemas.PercentileRankings.properties.netPremiumPercentile minimum: 0
components.schemas.PercentileRankings.properties.netPremiumPercentile maximum: 100
components.schemas.SimilarDay.properties.similarityScore description: 0..1; higher = more similar to today's flow profile.

## SKY040 https://docs.skylit.ai/api-reference/sector/sector-or-industry-level-flow-aggregation
paths./v1/flow/sector/{sector}.get summary: Sector- or industry-level flow aggregation
paths./v1/flow/sector/{sector}.get description: Aggregates options flow across all tickers in a GICS sector. The `{sector}` path parameter accepts either a sector ETF symbol (`XLK`, `XLF`, `XLE`, …) or a sector name (`Technology`, `Financials`, …). Returns sector-level metrics, top-contributor tickers, and an industry-level breakdown. 
paths./v1/flow/sector/{sector}.get.parameters.sector description: Sector ETF symbol (`XLK`, `XLF`, `XLE`, `XLV`, `XLY`, `XLP`, `XLU`, `XLI`, `XLB`, `XLRE`, `XLC`) or full sector name (`Technology`, `Financials`, `Healthcare`, etc.). 
paths./v1/flow/sector/{sector}.get.parameters.top_n.schema default: 10
paths./v1/flow/sector/{sector}.get.parameters.top_n.schema minimum: 1
paths./v1/flow/sector/{sector}.get.parameters.top_n.schema maximum: 50
components.schemas.SectorFlowSuccess.properties.data ref SectorFlowResponse
components.schemas.SectorFlowSuccess.properties.meta ref Meta
components.schemas.SectorFlowResponse.properties.etf nullable: True
components.schemas.SectorFlowResponse.properties.etf description: Sector ETF symbol when resolvable (e.g. `XLK` for Technology).
components.schemas.SectorFlowResponse.properties.metrics ref SectorMetrics
components.schemas.SectorFlowResponse.properties.topContributors.items ref TopContributor
components.schemas.SectorFlowResponse.properties.industryBreakdown.items ref IndustryBreakdown
components.schemas.SectorFlowResponse.properties.tickerCount minimum: 0
components.schemas.SectorMetrics.properties.totalVolume minimum: 0
components.schemas.SectorMetrics.properties.callVolume minimum: 0
components.schemas.SectorMetrics.properties.putVolume minimum: 0
components.schemas.SectorMetrics.properties.fir description: Flow Imbalance Ratio (-100..+100).
components.schemas.TopContributor.properties.pctOfSector description: Share of the sector's net premium (0–100).
components.schemas.IndustryBreakdown.properties.tickerCount minimum: 0

## SKY041 https://docs.skylit.ai/api-reference/market/market-wide-breadth-advancedecline-and-sector-rotation
paths./v1/flow/market-breadth.get summary: Market-wide breadth, advance/decline, and sector rotation
paths./v1/flow/market-breadth.get description: Combines SPY/QQQ/IWM aggregate sentiment with an advance/decline ratio (over directional FIR) and per-sector rotation signals. Ideal as a single "is the market risk-on or risk-off right now" probe. 
paths./v1/flow/market-breadth.get.parameters.date description: Trading date (YYYY-MM-DD). Defaults to today.
paths./v1/flow/market-breadth.get.parameters.fir_threshold description: Absolute FIR threshold (in %) used to classify a ticker as advancing or declining. Tickers with `|fir| < threshold` count as unchanged. 
paths./v1/flow/market-breadth.get.parameters.fir_threshold.schema default: 10
components.schemas.MarketBreadthSuccess.properties.data ref MarketBreadthResponse
components.schemas.MarketBreadthSuccess.properties.meta ref Meta
components.schemas.MarketBreadthResponse.properties.majorIndices.items ref IndexSentiment
components.schemas.MarketBreadthResponse.properties.aggregateSentiment ref AggregateSentiment
components.schemas.MarketBreadthResponse.properties.advanceDecline ref AdvanceDecline
components.schemas.MarketBreadthResponse.properties.sectorRotation.items ref SectorRotation
components.schemas.IndexSentiment.properties.sentiment enum: ['strong_bullish', 'bullish', 'slightly_bullish', 'neutral', 'slightly_bearish', 'bearish', 'strong_bearish']
components.schemas.AggregateSentiment.properties.sentiment enum: ['strong_bullish', 'bullish', 'slightly_bullish', 'neutral', 'slightly_bearish', 'bearish', 'strong_bearish']
components.schemas.AdvanceDecline.properties.advancing minimum: 0
components.schemas.AdvanceDecline.properties.declining minimum: 0
components.schemas.AdvanceDecline.properties.unchanged minimum: 0
components.schemas.AdvanceDecline.properties.total minimum: 0
components.schemas.AdvanceDecline.properties.ratio description: Advancing / declining (capped). 0.0 means no decliners.
components.schemas.AdvanceDecline.properties.breadthPct description: Share (0–100) of tickers classified as advancing.
components.schemas.AdvanceDecline.properties.marketAvgFir description: Mean FIR across all tickers (-100..+100).
components.schemas.SectorRotation.properties.signal enum: ['strong_inflow', 'inflow', 'neutral', 'outflow', 'strong_outflow']

## SKY042 https://docs.skylit.ai/api-reference/market/market-wide-flow-overview-for-the-current-trading-day
paths./v1/market/overview.get summary: Market-wide flow overview for the current trading day
paths./v1/market/overview.get description: Returns market-wide call/put premium, total volume, directional bullish/bearish premium, FIR, premium relative volume vs the trailing 20-day baseline at the same time of day, and the top 10 tickers by total premium. Optionally narrowed to a comma-separated ticker filter. 
paths./v1/market/overview.get.parameters.tickers description: Comma-separated list of tickers (e.g. `AAPL,NVDA,SPY`). When omitted, returns true market-wide stats over every ticker. 
components.schemas.MarketOverviewSuccess.properties.data ref MarketOverviewResponse
components.schemas.MarketOverviewSuccess.properties.meta ref Meta
components.schemas.MarketOverviewResponse.properties.totalVolume minimum: 0
components.schemas.MarketOverviewResponse.properties.callVolume minimum: 0
components.schemas.MarketOverviewResponse.properties.putVolume minimum: 0
components.schemas.MarketOverviewResponse.properties.activeTickers minimum: 0
components.schemas.MarketOverviewResponse.properties.premiumRvol description: Premium relative to the trailing 20-day baseline at this time of day.
components.schemas.MarketOverviewResponse.properties.topTickers.items ref TopTickerSummary
components.schemas.TopTickerSummary.properties.totalVolume minimum: 0

## SKY043 https://docs.skylit.ai/api-reference/market/bucketed-market-wide-net-call-premium-net-put-premium-time-series
paths./v1/market/tide.get summary: Bucketed market-wide net call premium / net put premium time series
paths./v1/market/tide.get description: Returns the market-wide intraday "tide" — bucketed Net Call Premium and Net Put Premium series with both per-bucket and cumulative values, plus an SPY price overlay for context. Two directional flavors are emitted per bar: the standard `ncp`/`npp` (call-buying minus call-selling, etc.) and a `manualNcp`/ `manualNpp` variant with the script-trade exclusion logic relaxed for callers that need raw flow. 
paths./v1/market/tide.get.parameters.interval description: Trailing window length. Defaults to a single trading day (`1D`); multi-day intervals roll up history at the chosen bucket size. 
paths./v1/market/tide.get.parameters.interval.schema enum: ['1D', '2D', '3D', '5D', '7D', '14D', '30D', '45D', '60D', '90D', '120D', '180D', '360D']
paths./v1/market/tide.get.parameters.interval.schema default: 1D
paths./v1/market/tide.get.parameters.bucket description: Bucket size for the time series.
paths./v1/market/tide.get.parameters.bucket.schema enum: ['1min', '5min', '15min', '30min', '1d', '1w']
paths./v1/market/tide.get.parameters.bucket.schema default: 5min
paths./v1/market/tide.get.parameters.date description: Trading date anchor (`YYYY-MM-DD`). Defaults to today.
paths./v1/market/tide.get.parameters.exclude_multi_leg description: Exclude multi-leg / spread trades from the directional totals.
paths./v1/market/tide.get.parameters.exclude_multi_leg.schema default: False
paths./v1/market/tide.get.parameters.exclude_deep_itm description: Exclude deep in-the-money trades (`moneyness_percent < -20`) from the directional totals. 
paths./v1/market/tide.get.parameters.exclude_deep_itm.schema default: False
components.schemas.MarketTideSuccess.properties.data ref MarketTideResponse
components.schemas.MarketTideSuccess.properties.meta ref Meta
components.schemas.MarketTideResponse.properties.bars.items ref MarketTideBar
components.schemas.MarketTideBar.properties.timestamp description: Unix seconds (bucket start).
components.schemas.MarketTideBar.properties.timestampEnd description: Unix seconds (bucket end).
components.schemas.MarketTideBar.properties.ncp description: Net Call Premium for the bucket (call buying minus call selling).
components.schemas.MarketTideBar.properties.npp description: Net Put Premium for the bucket.
components.schemas.MarketTideBar.properties.manualNcp description: NCP variant computed without the script-trade exclusion.
components.schemas.MarketTideBar.properties.callVolume minimum: 0
components.schemas.MarketTideBar.properties.putVolume minimum: 0
components.schemas.MarketTideBar.properties.totalVolume minimum: 0
components.schemas.MarketTideBar.properties.spyPrice description: SPY trade price at the bucket boundary, for overlay charts.
components.schemas.MarketTideBar.properties.isGap description: True when this bucket spans a session/holiday gap and contains no real trades.

## SKY044 https://docs.skylit.ai/api-reference/sweeps/aggregated-multi-exchange-sweep-activity
paths./v1/sweeps/{ticker}.get summary: Aggregated multi-exchange sweep activity
paths./v1/sweeps/{ticker}.get description: Returns "logical sweeps" — multi-exchange splits of one large order grouped by contract within a one-second execution window. Each row carries the venue list, total contracts/premium, spread position, moneyness bucket, and Skylit Flow Score / FlowBonus. The summary block adds population-level Sweep Dominance Factor (SDF) and bullish/bearish counts extrapolated from the full-day total. 
paths./v1/sweeps/{ticker}.get.parameters ref Ticker
paths./v1/sweeps/{ticker}.get.parameters.timeframe description: Trailing window. Currently only restricts the trading day; the handler reads the full day's sweep partition. `5m`/`15m`/`1h`/ `4h` reserved for future intraday filtering. 
paths./v1/sweeps/{ticker}.get.parameters.timeframe.schema enum: ['5m', '15m', '1h', '4h', '1d']
paths./v1/sweeps/{ticker}.get.parameters.timeframe.schema default: 1h
paths./v1/sweeps/{ticker}.get.parameters.option_type.schema enum: ['call', 'put', 'all']
paths./v1/sweeps/{ticker}.get.parameters.option_type.schema default: all
paths./v1/sweeps/{ticker}.get.parameters.moneyness.schema enum: ['deep_itm', 'itm', 'atm', 'otm', 'deep_otm', 'all']
paths./v1/sweeps/{ticker}.get.parameters.moneyness.schema default: all
paths./v1/sweeps/{ticker}.get.parameters.min_dte.schema minimum: 0
paths./v1/sweeps/{ticker}.get.parameters.max_dte.schema minimum: 0
paths./v1/sweeps/{ticker}.get.parameters.expiration description: Restrict to a single expiration date (`YYYY-MM-DD`).
paths./v1/sweeps/{ticker}.get.parameters.limit description: Max sweep rows returned (server caps at 500).
paths./v1/sweeps/{ticker}.get.parameters.limit.schema default: 100
paths./v1/sweeps/{ticker}.get.parameters.limit.schema minimum: 1
paths./v1/sweeps/{ticker}.get.parameters.limit.schema maximum: 500
components.schemas.SweepSuccess.properties.data ref SweepResponse
components.schemas.SweepSuccess.properties.meta ref Meta
components.schemas.SweepResponse.properties.sweeps.items ref SweepItem
components.schemas.SweepResponse.properties summary: {'$ref': '#/components/schemas/SweepSummary'}
components.schemas.SweepItem.properties.optionType enum: ['CALL', 'PUT']
components.schemas.SweepItem.properties.dte minimum: 0
components.schemas.SweepItem.properties.totalContracts minimum: 1
components.schemas.SweepItem.properties.exchangeCount minimum: 1
components.schemas.SweepItem.properties.exchanges description: Distinct OPRA exchange codes that filled the sweep.
components.schemas.SweepItem.properties.executionTimeMs minimum: 0
components.schemas.SweepItem.properties.executionTimeMs description: Milliseconds between first and last leg of the sweep.
components.schemas.SweepItem.properties.spreadPosition enum: ['AT_ASK', 'ABOVE_MID', 'AT_MID', 'BELOW_MID', 'AT_BID', 'UNKNOWN']
components.schemas.SweepItem.properties.moneyness enum: ['DEEP_ITM', 'ITM', 'ATM', 'OTM', 'DEEP_OTM']
components.schemas.SweepItem.properties.scores ref SweepScores
components.schemas.SweepSummary.properties.totalSweeps minimum: 0
components.schemas.SweepSummary.properties.totalSweeps description: Estimated total logical sweeps for the day (population, not just `returnedCount`).
components.schemas.SweepSummary.properties.bullishSweeps minimum: 0
components.schemas.SweepSummary.properties.bearishSweeps minimum: 0
components.schemas.SweepSummary.properties.sdf description: Sweep Dominance Factor (-100..+100) over the full day.
components.schemas.SweepSummary.properties.returnedCount minimum: 0
components.schemas.SweepSummary.properties.returnedCount description: Sweeps included in the `sweeps` array (capped by `limit`).
components.schemas.SweepScores.properties.flowScore minimum: -100
components.schemas.SweepScores.properties.flowScore maximum: 100
components.schemas.SweepScores.properties.flowScore description: Directional Flow Score for the aggregated sweep.
components.schemas.SweepScores.properties.flowBonus minimum: 0
components.schemas.SweepScores.properties.flowBonus maximum: 100
components.schemas.SweepScores.properties.flowBonus description: Conviction bonus (multi-exchange, OTM, premium size).

## SKY045 https://docs.skylit.ai/api-reference/analytics/aggregate-sentiment-scoring-across-timeframes-vwf-sdf-fir-composite
paths./v1/aggregate/{ticker}.get summary: Aggregate sentiment scoring across timeframes (VWF / SDF / FIR / Composite)
paths./v1/aggregate/{ticker}.get description: Returns a Composite directional score plus its VWF / SDF / FIR components for one or more trailing timeframes (intraday or multi-day). Optional moneyness breakdown, optional time-decay weighting, and a comparative trend block contrasting short- vs long-horizon sentiment. Reference: PRD Section 8. 
paths./v1/aggregate/{ticker}.get.parameters ref Ticker
paths./v1/aggregate/{ticker}.get.parameters.timeframes description: Comma-separated timeframes, or `all`. Supported atoms: `1h, 4h, 1d, 7d, 30d, 90d`. `all` expands to all six. Unknown atoms are treated as a single trading day. 
paths./v1/aggregate/{ticker}.get.parameters.timeframes.schema default: 1d
paths./v1/aggregate/{ticker}.get.parameters.include_breakdown description: Attach the per-timeframe VWF/SDF/FIR component split.
paths./v1/aggregate/{ticker}.get.parameters.include_breakdown.schema default: True
paths./v1/aggregate/{ticker}.get.parameters.include_moneyness description: Attach a `byMoneyness` array (deep_itm → deep_otm).
paths./v1/aggregate/{ticker}.get.parameters.include_moneyness.schema default: False
paths./v1/aggregate/{ticker}.get.parameters.moneyness_filter.schema enum: ['deep_itm', 'itm', 'atm', 'otm', 'deep_otm', 'all']
paths./v1/aggregate/{ticker}.get.parameters.moneyness_filter.schema default: all
paths./v1/aggregate/{ticker}.get.parameters.expiration_filter description: Restrict to one expiration bucket.
paths./v1/aggregate/{ticker}.get.parameters.expiration_filter.schema enum: ['0dte', 'weekly', 'monthly', 'leaps', 'all']
paths./v1/aggregate/{ticker}.get.parameters.expiration_filter.schema default: all
paths./v1/aggregate/{ticker}.get.parameters.time_decay description: Apply exponential time decay to VWF / SDF / FIR components.
paths./v1/aggregate/{ticker}.get.parameters.time_decay.schema default: False
paths./v1/aggregate/{ticker}.get.parameters.time_decay_half_life description: Half-life in minutes for the decay (only applied when `timeDecay=true`).
paths./v1/aggregate/{ticker}.get.parameters.time_decay_half_life.schema minimum: 1
paths./v1/aggregate/{ticker}.get.parameters.time_decay_half_life.schema default: 30
components.schemas.AggregateSuccess.properties.data ref AggregateResponse
components.schemas.AggregateSuccess.properties.meta ref Meta
components.schemas.AggregateResponse.properties.byTimeframe.additionalProperties ref TimeframeAggregate
components.schemas.AggregateResponse.properties.byTimeframe description: Map keyed by timeframe id (`1h`, `4h`, `1d`, `7d`, `30d`, `90d`, …). Only the requested timeframes appear; missing entries indicate the underlying query failed for that horizon. 
components.schemas.AggregateResponse.properties.trend ref TrendAnalysis
components.schemas.AggregateResponse.properties.byMoneyness description: Present when `includeMoneyness=true`.
components.schemas.AggregateResponse.properties.byMoneyness.items ref MoneynessAggregate
components.schemas.TimeframeAggregate.properties.composite minimum: -100
components.schemas.TimeframeAggregate.properties.composite maximum: 100
components.schemas.TimeframeAggregate.properties.composite description: 0.4×VWF + 0.35×SDF + 0.25×FIR (clamped to ±100).
components.schemas.TimeframeAggregate.properties.direction enum: ['strong_bullish', 'bullish', 'neutral', 'bearish', 'strong_bearish']
components.schemas.TimeframeAggregate.properties.signalStrength enum: ['strong', 'moderate', 'weak', 'neutral']
components.schemas.TimeframeAggregate.properties.confidence minimum: 0
components.schemas.TimeframeAggregate.properties.confidence maximum: 1
components.schemas.TimeframeAggregate.properties.sweepAlignment description: True when VWF and SDF agree in direction.
components.schemas.TimeframeAggregate.properties.components ref ScoreComponents
components.schemas.TimeframeAggregate.properties.tradeCount minimum: 0
components.schemas.TimeframeAggregate.properties.sweepCount minimum: 0
components.schemas.TimeframeAggregate.properties.timeDecayApplied description: Present only when time decay was applied.
components.schemas.TrendAnalysis.properties.shortVsLong enum: ['stable', 'bullish_divergence', 'bearish_divergence', 'improving', 'deteriorating']
components.schemas.TrendAnalysis.properties.momentum enum: ['stable', 'accelerating_bullish', 'accelerating_bearish', 'mixed']
components.schemas.TrendAnalysis.properties description: {'type': 'string', 'description': 'Human-readable interpretation of the short→long horizon contour.'}
components.schemas.MoneynessAggregate.properties.category enum: ['DEEP_ITM', 'ITM', 'ATM', 'OTM', 'DEEP_OTM']
components.schemas.MoneynessAggregate.properties.tradeCount minimum: 0
components.schemas.ScoreComponents.properties.vwf description: Volume-Weighted Flow: Σ(premium × flowScore) / Σ(premium)
components.schemas.ScoreComponents.properties.sdf description: Sweep Dominance Factor.
components.schemas.ScoreComponents.properties.fir description: Flow Imbalance Ratio: (bullish − bearish) / total directional × 100

## SKY046 https://docs.skylit.ai/api-reference/analytics/volume-vs-open-interest-accumulation-analysis
paths./v1/vol-oi/{ticker}.get summary: Volume-vs-Open-Interest accumulation analysis
paths./v1/vol-oi/{ticker}.get description: Distinguishes new position building (accumulation) from position closing (distribution) by bucketing Vol/OI ratios per option type and moneyness band. Returns an overall accumulation score (0–100), an estimate of the share of volume representing new positions, and a one-token signal (`strong_accumulation` → `low_activity`). 
paths./v1/vol-oi/{ticker}.get.parameters ref Ticker
paths./v1/vol-oi/{ticker}.get.parameters.timeframe.schema enum: ['daily', 'weekly']
paths./v1/vol-oi/{ticker}.get.parameters.timeframe.schema default: daily
paths./v1/vol-oi/{ticker}.get.parameters.option_type.schema enum: ['call', 'put', 'all']
paths./v1/vol-oi/{ticker}.get.parameters.option_type.schema default: all
paths./v1/vol-oi/{ticker}.get.parameters.moneyness.schema enum: ['otm_10plus', 'otm_5_10', 'otm_3_5', 'atm_itm', 'all']
paths./v1/vol-oi/{ticker}.get.parameters.moneyness.schema default: all
paths./v1/vol-oi/{ticker}.get.parameters.min_oi.schema minimum: 0
components.schemas.VolOiSuccess.properties.data ref VolOiResponse
components.schemas.VolOiSuccess.properties.meta ref Meta
components.schemas.VolOiResponse.properties.timeframe enum: ['daily', 'weekly']
components.schemas.VolOiResponse.properties.volOiAnalysis ref VolOiAnalysis
components.schemas.VolOiResponse.properties.accumulationScore minimum: 0
components.schemas.VolOiResponse.properties.accumulationScore maximum: 100
components.schemas.VolOiResponse.properties.accumulationScore description: Composite accumulation score weighted by volume + OTM share.
components.schemas.VolOiResponse.properties.newPositionEstimatePct minimum: 0
components.schemas.VolOiResponse.properties.newPositionEstimatePct maximum: 100
components.schemas.VolOiResponse.properties.newPositionEstimatePct description: Estimated share of volume that represents new positions.
components.schemas.VolOiResponse.properties.signal enum: ['strong_accumulation', 'accumulation', 'mixed', 'distribution', 'low_activity']
components.schemas.VolOiAnalysis.properties.calls ref VolOiOptionType
components.schemas.VolOiAnalysis.properties.puts ref VolOiOptionType
components.schemas.VolOiOptionType.properties.totalVolume minimum: 0
components.schemas.VolOiOptionType.properties.totalOi minimum: 0
components.schemas.VolOiOptionType.properties.signal enum: ['strong_accumulation', 'accumulation', 'mixed', 'distribution', 'low_activity']
components.schemas.VolOiOptionType.properties.byMoneyness ref VolOiByMoneyness
components.schemas.VolOiByMoneyness.properties.otm10plus.allOf ref VolOiMoneynessBucket
components.schemas.VolOiByMoneyness.properties.otm10plus.allOf description: ≥10% OTM.
components.schemas.VolOiByMoneyness.properties.otm510.allOf ref VolOiMoneynessBucket
components.schemas.VolOiByMoneyness.properties.otm510.allOf description: 5–10% OTM.
components.schemas.VolOiByMoneyness.properties.otm35.allOf ref VolOiMoneynessBucket
components.schemas.VolOiByMoneyness.properties.otm35.allOf description: 3–5% OTM.
components.schemas.VolOiByMoneyness.properties.atmItm.allOf ref VolOiMoneynessBucket
components.schemas.VolOiByMoneyness.properties.atmItm.allOf description: ATM/ITM (<3% OTM or already ITM).
components.schemas.VolOiMoneynessBucket.properties.volume minimum: 0
components.schemas.VolOiMoneynessBucket.properties.oi minimum: 0
components.schemas.VolOiMoneynessBucket.properties.ratio description: Vol/OI ratio for the bucket (0 when OI is zero).

## SKY047 https://docs.skylit.ai/api-reference/analytics/moneyness-breakdown-with-pattern-detection
paths./v1/moneyness/{ticker}.get summary: Moneyness breakdown with pattern detection
paths./v1/moneyness/{ticker}.get description: Splits calls and puts across `deep_itm / itm / atm / otm / deep_otm` buckets with premium, sentiment, percentage of total, and trade count. Surfaces detected patterns (e.g. heavy OTM call accumulation, ATM concentration, deep-OTM lottery tickets) and a directional `signal`/`dominantStrategy` interpretation. 
paths./v1/moneyness/{ticker}.get.parameters ref Ticker
paths./v1/moneyness/{ticker}.get.parameters.timeframe.schema enum: ['intraday', 'daily', '7d', '30d']
paths./v1/moneyness/{ticker}.get.parameters.timeframe.schema default: daily
components.schemas.MoneynessSuccess.properties.data ref MoneynessResponse
components.schemas.MoneynessSuccess.properties.meta ref Meta
components.schemas.MoneynessResponse.properties.moneynessBreakdown ref MoneynessFullBreakdown
components.schemas.MoneynessResponse.properties.notablePatterns.items ref MoneynessNotablePattern
components.schemas.MoneynessResponse.properties.interpretation ref MoneynessInterpretation
components.schemas.MoneynessFullBreakdown.properties.calls ref MoneynessOptionTypeBreakdown
components.schemas.MoneynessFullBreakdown.properties.puts ref MoneynessOptionTypeBreakdown
components.schemas.MoneynessNotablePattern.properties pattern: {'type': 'string', 'enum': ['otm_call_accumulation', 'otm_put_accumulation', 'atm_concentration', 'lottery_ticket_calls', 'itm_stock_replacement', 'heavy_put_skew', 'heavy_call_skew']}
components.schemas.MoneynessNotablePattern.properties description: {'type': 'string', 'description': 'Human-readable description of the pattern.'}
components.schemas.MoneynessNotablePattern.properties.significance enum: ['high', 'medium', 'low']
components.schemas.MoneynessNotablePattern.properties.metrics ref MoneynessPatternMetrics
components.schemas.MoneynessInterpretation.properties.convictionFocus enum: ['otm_calls', 'otm_puts', 'atm', 'distributed', 'none']
components.schemas.MoneynessInterpretation.properties.dominantStrategy enum: ['speculative_bullish', 'call_selling', 'bearish_speculation', 'put_selling', 'directional_bullish', 'directional_bearish', 'mixed', 'no_activity']
components.schemas.MoneynessInterpretation.properties.signal enum: ['bullish', 'moderately_bullish', 'neutral', 'moderately_bearish', 'bearish']
components.schemas.MoneynessOptionTypeBreakdown.properties.deepItm ref MoneynessCategoryMetrics
components.schemas.MoneynessOptionTypeBreakdown.properties.itm ref MoneynessCategoryMetrics
components.schemas.MoneynessOptionTypeBreakdown.properties.atm ref MoneynessCategoryMetrics
components.schemas.MoneynessOptionTypeBreakdown.properties.otm ref MoneynessCategoryMetrics
components.schemas.MoneynessOptionTypeBreakdown.properties.deepOtm ref MoneynessCategoryMetrics
components.schemas.MoneynessOptionTypeBreakdown.properties.totalTrades minimum: 0
components.schemas.MoneynessCategoryMetrics.properties.sentiment minimum: -100
components.schemas.MoneynessCategoryMetrics.properties.sentiment maximum: 100
components.schemas.MoneynessCategoryMetrics.properties.tradeCount minimum: 0
components.schemas.MoneynessCategoryMetrics.properties.weightedPremium description: Premium scaled by a moneyness weight (deeper OTM = higher multiplier).

## SKY048 https://docs.skylit.ai/api-reference/scoring/detailed-scoring-for-a-single-trade
paths./v1/score/{trade_id}.get summary: Detailed scoring for a single trade
paths./v1/score/{trade_id}.get description: Returns sentiment, urgency, and confidence scores for an individual trade plus a spread-level breakdown and full trade context (ticker, strike, expiration, sweep/block flags, moneyness). Used to drill into a single row from `/v1/flow/{ticker}`.  The `trade_id` path parameter accepts three formats: the canonical `flow_{hex}_{idx}` id returned by the flow feed, a bare hex timestamp (`188afe42c3a77af2`), or a raw nanosecond integer. 
paths./v1/score/{trade_id}.get.parameters.trade_id description: Trade id (`flow_{hex}_{idx}`, bare hex timestamp, or raw nanos). 
components.schemas.TradeScoreSuccess.properties.data ref TradeScoreResponse
components.schemas.TradeScoreSuccess.properties.meta ref Meta
components.schemas.TradeScoreResponse.properties.scores ref TradeScores
components.schemas.TradeScoreResponse.properties.interpretation ref TradeInterpretation
components.schemas.TradeScoreResponse.properties.spreadAnalysis ref SpreadAnalysis
components.schemas.TradeScoreResponse.properties.tradeContext ref TradeContext
components.schemas.TradeScores.properties.sentiment minimum: -100
components.schemas.TradeScores.properties.sentiment maximum: 100
components.schemas.TradeScores.properties.urgency minimum: 0
components.schemas.TradeScores.properties.urgency maximum: 100
components.schemas.TradeScores.properties.confidence minimum: 0
components.schemas.TradeScores.properties.confidence maximum: 1
components.schemas.TradeInterpretation.properties.direction enum: ['bullish', 'bearish', 'neutral']
components.schemas.TradeInterpretation.properties.intent description: Intent classification (e.g. `opening_long_call`, `closing_short_put`, `aggressive_call_buy`, `passive_call_sell`). Returned as a stable `snake_case` token; new values may be added as classification improves. 
components.schemas.TradeInterpretation.properties description: {'type': 'string', 'description': 'One-sentence human-readable explanation of the trade.'}
components.schemas.SpreadAnalysis.properties.positionInSpread description: Discrete bucket label inferred from the canonical side code (`A`/`AA`/`BA` → ask-side, `B`/`BB`/`AB` → bid-side, `M` → mid, `N` → no BBO). 
components.schemas.SpreadAnalysis.properties.positionInSpread enum: ['above_ask', 'at_ask', 'below_ask', 'mid', 'above_bid', 'at_bid', 'below_bid', 'no_bbo']
components.schemas.TradeContext.properties.optionType enum: ['call', 'put']
components.schemas.TradeContext.properties.size minimum: 1
components.schemas.TradeContext.properties.tradeType enum: ['sweep', 'block', 'regular']
components.schemas.TradeContext.properties.dte minimum: 0
components.schemas.TradeContext.properties.moneyness enum: ['deep_itm', 'itm', 'atm', 'otm', 'deep_otm']

## SKY049 https://docs.skylit.ai/api-reference/ratios/chain-level-bidaskmid-distribution
paths./v1/chain-ratio/{ticker}.get summary: Chain-level bid/ask/mid distribution
paths./v1/chain-ratio/{ticker}.get description: Aggregates a ticker's full option chain to surface buying vs selling pressure (`askRatio`, `bidRatio`, `midRatio`, `aggressionRatio`), call/put balance, and ATM/OTM concentration. Returns a `bias`, `aggression`, and `confidence` interpretation. Reference: PRD Sections 12.3 and 14. 
paths./v1/chain-ratio/{ticker}.get.parameters ref Ticker
paths./v1/chain-ratio/{ticker}.get.parameters.timeframe.schema enum: ['5m', '15m', '1h', '4h', '1d']
paths./v1/chain-ratio/{ticker}.get.parameters.timeframe.schema default: 1d
paths./v1/chain-ratio/{ticker}.get.parameters.option_type.schema enum: ['call', 'put', 'all']
paths./v1/chain-ratio/{ticker}.get.parameters.option_type.schema default: all
paths./v1/chain-ratio/{ticker}.get.parameters.min_premium.schema minimum: 0
paths./v1/chain-ratio/{ticker}.get.parameters.min_dte.schema minimum: 0
paths./v1/chain-ratio/{ticker}.get.parameters.max_dte.schema minimum: 0
components.schemas.ChainRatioSuccess.properties.data ref ChainRatioResponse
components.schemas.ChainRatioSuccess.properties.meta ref Meta
components.schemas.ChainRatioResponse.properties.tradeCount minimum: 0
components.schemas.ChainRatioResponse.properties.chainRatios ref ChainRatios
components.schemas.ChainRatioResponse.properties.interpretation ref RatioInterpretation
components.schemas.ChainRatios.properties.callPutRatio description: Call premium / put premium (capped at 999 when puts = 0).
components.schemas.ChainRatios.properties.askRatio description: Share (0–1) of trades at or above ask.
components.schemas.ChainRatios.properties.bidRatio description: Share (0–1) of trades at or below bid.
components.schemas.ChainRatios.properties.midRatio description: Share (0–1) of trades at mid (or with no BBO).
components.schemas.ChainRatios.properties.aggressionRatio description: (askTrades + bidTrades) / midTrades — capped at 999 when midTrades = 0.
components.schemas.ChainRatios.properties.atmConcentration description: Share (0–1) of volume in ATM strikes (±3% moneyness).
components.schemas.ChainRatios.properties.otmCallConcentration description: Share (0–1) of call volume in OTM strikes.
components.schemas.ChainRatios.properties.otmPutConcentration description: Share (0–1) of put volume in OTM strikes.
components.schemas.RatioInterpretation.properties.bias enum: ['BULLISH', 'BEARISH', 'NEUTRAL', 'MIXED']
components.schemas.RatioInterpretation.properties.aggression enum: ['HIGH', 'MEDIUM', 'LOW']
components.schemas.RatioInterpretation.properties.confidence enum: ['HIGH', 'MEDIUM', 'LOW']
components.schemas.RatioInterpretation.properties description: {'type': 'string'}

## SKY050 https://docs.skylit.ai/api-reference/ratios/per-contract-bidaskmid-distribution
paths./v1/contract-ratio/{symbol}.get summary: Per-contract bid/ask/mid distribution
paths./v1/contract-ratio/{symbol}.get description: Single-contract counterpart to `/v1/chain-ratio/{ticker}`. Returns `askRatio`, `bidRatio`, `midRatio`, `aggressionRatio`, and a `bias`/`aggression`/`confidence` interpretation for one specific OPRA option symbol. 
paths./v1/contract-ratio/{symbol}.get.parameters ref OptionSymbol
paths./v1/contract-ratio/{symbol}.get.parameters.timeframe.schema enum: ['5m', '15m', '1h', '4h', '1d']
paths./v1/contract-ratio/{symbol}.get.parameters.timeframe.schema default: 1d
paths./v1/contract-ratio/{symbol}.get.parameters.min_premium.schema minimum: 0
components.parameters.OptionSymbol description: OPRA option symbol in URL-safe form: `{ticker}__{YYMMDD}{C|P}{strike×1000, 8 digits}` — the ticker and the 15-character contract block are joined by a **double underscore** (`__`). For example, an AAPL $250 call expiring 2026-01-17 is `AAPL__260117C00250000`. (A space-padded 21-char OCC form such as `AAPL  260117C00250000` is also accepted on some endpoints, but the `__` form is canonical and works across all contract routes.) 
components.schemas.ContractRatioSuccess.properties.data ref ContractRatioResponse
components.schemas.ContractRatioSuccess.properties.meta ref Meta
components.schemas.ContractRatioResponse.properties.optionType enum: ['CALL', 'PUT', 'UNKNOWN']
components.schemas.ContractRatioResponse.properties.tradeCount minimum: 0
components.schemas.ContractRatioResponse.properties.totalVolume minimum: 0
components.schemas.ContractRatioResponse.properties.contractRatios ref ContractRatios
components.schemas.ContractRatioResponse.properties.interpretation ref RatioInterpretation

## SKY051 https://docs.skylit.ai/api-reference/ratios/chain-level-callput-aware-bullbear-pressure
paths./v1/chain-bull-bear/{ticker}.get summary: Chain-level call/put-aware bull/bear pressure
paths./v1/chain-bull-bear/{ticker}.get description: Folds option type into the bid/ask/mid signal: a call lifted at the ask is bullish, a put hit at the bid is also bullish (put selling), etc. Returns overall bull/bear/neutral percentages plus call-only and put-only bull breakdowns so callers can tell whether the directional pressure originates from call buying, put selling, or both. 
paths./v1/chain-bull-bear/{ticker}.get.parameters ref Ticker
paths./v1/chain-bull-bear/{ticker}.get.parameters.timeframe.schema enum: ['5m', '15m', '1h', '4h', '1d']
paths./v1/chain-bull-bear/{ticker}.get.parameters.timeframe.schema default: 1d
paths./v1/chain-bull-bear/{ticker}.get.parameters.option_type.schema enum: ['call', 'put', 'all']
paths./v1/chain-bull-bear/{ticker}.get.parameters.option_type.schema default: all
paths./v1/chain-bull-bear/{ticker}.get.parameters.min_premium.schema minimum: 0
paths./v1/chain-bull-bear/{ticker}.get.parameters.min_dte.schema minimum: 0
paths./v1/chain-bull-bear/{ticker}.get.parameters.max_dte.schema minimum: 0
components.schemas.ChainBullBearSuccess.properties.data ref ChainBullBearResponse
components.schemas.ChainBullBearSuccess.properties.meta ref Meta
components.schemas.ChainBullBearResponse.properties.tradeCount minimum: 0
components.schemas.ChainBullBearResponse.properties.totalVolume minimum: 0
components.schemas.ChainBullBearResponse.properties.metrics ref ChainBullBearMetrics
components.schemas.ChainBullBearResponse.properties.interpretation ref BullBearInterpretation
components.schemas.ChainBullBearMetrics.properties.bullPct description: Share (0–100) of volume classified as bullish.
components.schemas.ChainBullBearMetrics.properties.bullBearRatio description: bullVolume / bearVolume (capped at 999 when bear = 0).
components.schemas.ChainBullBearMetrics.properties.callBullPct description: Bullish share within calls only (high = aggressive call buying).
components.schemas.ChainBullBearMetrics.properties.putBullPct description: Bullish share within puts only (high = put selling = contrarian bullish).
components.schemas.BullBearInterpretation.properties.bias enum: ['BULLISH', 'BEARISH', 'NEUTRAL', 'MIXED']
components.schemas.BullBearInterpretation.properties.strength enum: ['strong', 'moderate', 'weak', 'uncertain', 'passive', 'balanced']
components.schemas.BullBearInterpretation.properties.confidence enum: ['HIGH', 'MEDIUM', 'LOW']
components.schemas.BullBearInterpretation.properties description: {'type': 'string'}

## SKY052 https://docs.skylit.ai/api-reference/ratios/per-contract-callput-aware-bullbear-pressure
paths./v1/contract-bull-bear/{symbol}.get summary: Per-contract call/put-aware bull/bear pressure
paths./v1/contract-bull-bear/{symbol}.get description: Single-contract counterpart to `/v1/chain-bull-bear/{ticker}`. Maps a contract's trades to bull/bear/neutral buckets using both side (bid/ask/mid) and option type, so a bullish put-seller and a bullish call-buyer both register as bullish pressure. 
paths./v1/contract-bull-bear/{symbol}.get.parameters ref OptionSymbol
paths./v1/contract-bull-bear/{symbol}.get.parameters.timeframe.schema enum: ['5m', '15m', '1h', '4h', '1d']
paths./v1/contract-bull-bear/{symbol}.get.parameters.timeframe.schema default: 1d
paths./v1/contract-bull-bear/{symbol}.get.parameters.min_premium.schema minimum: 0
components.schemas.ContractBullBearSuccess.properties.data ref ContractBullBearResponse
components.schemas.ContractBullBearSuccess.properties.meta ref Meta
components.schemas.ContractBullBearResponse.properties.optionType enum: ['CALL', 'PUT', 'UNKNOWN']
components.schemas.ContractBullBearResponse.properties.tradeCount minimum: 0
components.schemas.ContractBullBearResponse.properties.totalVolume minimum: 0
components.schemas.ContractBullBearResponse.properties.metrics ref ContractBullBearMetrics
components.schemas.ContractBullBearResponse.properties.interpretation ref BullBearInterpretation

## SKY053 https://docs.skylit.ai/api-reference/underlying/list-underlyings-active-on-a-date
paths./v1/underlying.get summary: List underlyings active on a date
paths./v1/underlying.get description: Lists every ticker that traded options on the requested date, ordered by total premium (descending). Useful as a starting point for discovery or for repopulating the universe of tradable tickers. 
paths./v1/underlying.get.parameters.limit description: Maximum rows to return. Server caps at 500.
paths./v1/underlying.get.parameters.limit.schema default: 100
paths./v1/underlying.get.parameters.limit.schema minimum: 1
paths./v1/underlying.get.parameters.limit.schema maximum: 500
paths./v1/underlying.get.parameters ref DateQuery
paths./v1/underlying.get.parameters.min_premium.schema minimum: 0
paths./v1/underlying.get.parameters.min_premium description: Minimum total premium (USD) for the day.
paths./v1/underlying.get.parameters.min_volume.schema minimum: 0
paths./v1/underlying.get.parameters.min_volume description: Minimum total option volume for the day.
components.parameters.DateQuery description: Trading date the request targets, in `YYYY-MM-DD`. Defaults to the current trading date (the most recent session that has settled enough data to be queryable). Past dates fall through to the daily rollup tables. 
components.schemas.TickerListSuccess.properties.data.items ref TickerListItem
components.schemas.TickerListSuccess.properties.meta ref Meta
components.schemas.TickerListItem.properties.totalPremium description: Total premium (USD) across all option trades on the day.
components.schemas.TickerListItem.properties.totalVolume minimum: 0
components.schemas.TickerListItem.properties.totalVolume description: Total option contracts traded.

## SKY054 https://docs.skylit.ai/api-reference/underlying/prefix-search-active-tickers
paths./v1/underlying/search.get summary: Prefix-search active tickers
paths./v1/underlying/search.get description: Case-insensitive prefix search over the active-tickers universe for the requested date. Use to power autocomplete UIs. 
paths./v1/underlying/search.get.parameters.q description: Search prefix (1–10 characters, uppercased server-side).
paths./v1/underlying/search.get.parameters.limit.schema minimum: 1
paths./v1/underlying/search.get.parameters.limit.schema maximum: 50
paths./v1/underlying/search.get.parameters.limit.schema default: 20
paths./v1/underlying/search.get.parameters ref DateQuery
components.schemas.TickerListSuccess.properties.data.items ref TickerListItem
components.schemas.TickerListSuccess.properties.meta ref Meta

## SKY055 https://docs.skylit.ai/api-reference/underlying/top-underlyings-by-daily-flow
paths./v1/underlying/top/daily.get summary: Top underlyings by daily flow
paths./v1/underlying/top/daily.get description: Top tickers for a single trading day, with call/put premium and volume splits, net premium, and call/put ratio. Sortable by `premium`, `volume`, `net_premium`, or `call_put_ratio`. 
paths./v1/underlying/top/daily.get.parameters.limit description: Maximum rows to return. Server caps at 500.
paths./v1/underlying/top/daily.get.parameters.limit.schema default: 100
paths./v1/underlying/top/daily.get.parameters.limit.schema minimum: 1
paths./v1/underlying/top/daily.get.parameters.limit.schema maximum: 500
paths./v1/underlying/top/daily.get.parameters ref DateQuery
paths./v1/underlying/top/daily.get.parameters.min_premium.schema minimum: 0
paths./v1/underlying/top/daily.get.parameters.min_volume.schema minimum: 0
paths./v1/underlying/top/daily.get.parameters.order_by.schema enum: ['premium', 'volume', 'net_premium', 'call_put_ratio']
paths./v1/underlying/top/daily.get.parameters.order_by.schema default: premium
paths./v1/underlying/top/daily.get.parameters.order.schema enum: ['asc', 'desc']
paths./v1/underlying/top/daily.get.parameters.order.schema default: desc
components.schemas.TopUnderlyingListSuccess.properties.data.items ref TopUnderlyingItem
components.schemas.TopUnderlyingListSuccess.properties.meta ref Meta
components.schemas.TopUnderlyingItem.properties.totalVolume minimum: 0
components.schemas.TopUnderlyingItem.properties.callVolume minimum: 0
components.schemas.TopUnderlyingItem.properties.putVolume minimum: 0
components.schemas.TopUnderlyingItem.properties.netPremium description: `callPremium - putPremium`.
components.schemas.TopUnderlyingItem.properties.callPutRatio description: `callPremium / putPremium` (0 when no put premium).

## SKY056 https://docs.skylit.ai/api-reference/underlying/top-underlyings-by-trailing-5-day-flow
paths./v1/underlying/top/weekly.get summary: Top underlyings by trailing-5-day flow
paths./v1/underlying/top/weekly.get description: Same shape as `/v1/underlying/top/daily` but rolled up across the trailing 5 trading days ending on `date`. 
paths./v1/underlying/top/weekly.get.parameters.limit description: Maximum rows to return. Server caps at 500.
paths./v1/underlying/top/weekly.get.parameters.limit.schema default: 100
paths./v1/underlying/top/weekly.get.parameters.limit.schema minimum: 1
paths./v1/underlying/top/weekly.get.parameters.limit.schema maximum: 500
paths./v1/underlying/top/weekly.get.parameters ref DateQuery
paths./v1/underlying/top/weekly.get.parameters.min_premium.schema minimum: 0
paths./v1/underlying/top/weekly.get.parameters.min_volume.schema minimum: 0
paths./v1/underlying/top/weekly.get.parameters.order_by.schema enum: ['premium', 'volume', 'net_premium', 'call_put_ratio']
paths./v1/underlying/top/weekly.get.parameters.order_by.schema default: premium
paths./v1/underlying/top/weekly.get.parameters.order.schema enum: ['asc', 'desc']
paths./v1/underlying/top/weekly.get.parameters.order.schema default: desc
components.schemas.TopUnderlyingListSuccess.properties.data.items ref TopUnderlyingItem
components.schemas.TopUnderlyingListSuccess.properties.meta ref Meta

## SKY057 https://docs.skylit.ai/api-reference/underlying/bulk-underlying-stats-for-a-list-of-tickers
paths./v1/underlying/bulk/stats.get summary: Bulk underlying stats for a list of tickers
paths./v1/underlying/bulk/stats.get description: Returns a single-day `UnderlyingStats` record per requested ticker. Tickers absent from the response had no options activity that day. 
paths./v1/underlying/bulk/stats.get.parameters.tickers description: Comma-separated list of tickers (max 50).
paths./v1/underlying/bulk/stats.get.parameters ref DateQuery
components.schemas.UnderlyingStatsListSuccess.properties.data.items ref UnderlyingStats
components.schemas.UnderlyingStatsListSuccess.properties.meta ref Meta
components.schemas.UnderlyingStats.properties.lastPrice description: Last traded underlying stock price on `date`.
components.schemas.UnderlyingStats.properties.totalVolume minimum: 0
components.schemas.UnderlyingStats.properties.callVolume minimum: 0
components.schemas.UnderlyingStats.properties.putVolume minimum: 0
components.schemas.UnderlyingStats.properties.tradeCount minimum: 0
components.schemas.UnderlyingStats.properties.uniqueStrikes minimum: 0
components.schemas.UnderlyingStats.properties.uniqueExpirations minimum: 0

## SKY058 https://docs.skylit.ai/api-reference/underlying/daily-stats-for-a-single-underlying
paths./v1/underlying/{ticker}/stats.get summary: Daily stats for a single underlying
paths./v1/underlying/{ticker}/stats.get.parameters ref Ticker
paths./v1/underlying/{ticker}/stats.get.parameters ref DateQuery
components.schemas.UnderlyingStatsSuccess.properties.data ref UnderlyingStats
components.schemas.UnderlyingStatsSuccess.properties.meta ref Meta

## SKY059 https://docs.skylit.ai/api-reference/underlying/intraday-chart-bars-for-a-ticker
paths./v1/underlying/{ticker}/chart.get summary: Intraday chart bars for a ticker
paths./v1/underlying/{ticker}/chart.get description: Returns time-bucketed bars aggregating options activity for the underlying (call/put volume + premium, P/C ratio, bid/ask execution split) plus the underlying stock price at each boundary. Backed by the same intraday rollup tables that power the chart modal in the Skylit UI. 
paths./v1/underlying/{ticker}/chart.get.parameters ref Ticker
paths./v1/underlying/{ticker}/chart.get.parameters.interval description: Trailing window covered by the bars (e.g. `1D`, `7D`, `30D`).
paths./v1/underlying/{ticker}/chart.get.parameters.bucket description: Bucket size.
paths./v1/underlying/{ticker}/chart.get.parameters.bucket.schema enum: ['1min', '5min', '10min', '15min', '30min', '1d', '1w']
components.schemas.UnderlyingChartSuccess.properties.data.items ref UnderlyingChartBar
components.schemas.UnderlyingChartSuccess.properties.meta ref Meta
components.schemas.UnderlyingChartBar description: One bucketed bar in the underlying-chart response. Each bar covers `[timestamp, timestampEnd)` in Unix UTC seconds. 
components.schemas.UnderlyingChartBar.properties.timestamp description: Bucket start, Unix seconds (returned as a string for JS-precision safety).
components.schemas.UnderlyingChartBar.properties.callVolume minimum: 0
components.schemas.UnderlyingChartBar.properties.putVolume minimum: 0
components.schemas.UnderlyingChartBar.properties.candleVolume minimum: 0
components.schemas.UnderlyingChartBar.properties.candleVolume description: `callVolume + putVolume`.
components.schemas.UnderlyingChartBar.properties.pcRatio description: `putVolume / callVolume` (0 when no calls).
components.schemas.UnderlyingChartBar.properties.avgVolume description: 30D baseline volume for this time-of-day slot. Omitted when insufficient history.
components.schemas.UnderlyingChartBar.properties.avgPremium description: 30D baseline premium for this time-of-day slot.
components.schemas.UnderlyingChartBar.properties.chainBidPct description: % of bucket volume executed at/below the bid.
components.schemas.UnderlyingChartBar.properties.chainAskPct description: % of bucket volume executed at/above the ask.

## SKY060 https://docs.skylit.ai/api-reference/underlying/raw-enriched-trades-for-a-ticker
paths./v1/underlying/{ticker}/trades.get summary: Raw enriched trades for a ticker
paths./v1/underlying/{ticker}/trades.get description: Returns the raw enriched trade rows that feed the chart bars and the live feed. Supports rich filtering — sweep-only / multi-leg, moneyness, premium floor, DTE / strike / expiration windows. See `OptionTradeRow` below. 
paths./v1/underlying/{ticker}/trades.get.parameters ref Ticker
paths./v1/underlying/{ticker}/trades.get.parameters.start description: Lower time bound — ISO 8601 (e.g. `2026-01-12T09:30:00Z`) or Unix seconds. Defaults to start-of-trading-day. 
paths./v1/underlying/{ticker}/trades.get.parameters.end description: Upper time bound — ISO 8601 or Unix seconds. Defaults to now. 
paths./v1/underlying/{ticker}/trades.get.parameters.limit.schema minimum: 1
paths./v1/underlying/{ticker}/trades.get.parameters.limit.schema maximum: 500
paths./v1/underlying/{ticker}/trades.get.parameters.limit.schema default: 50
paths./v1/underlying/{ticker}/trades.get.parameters.only_sweeps.schema default: False
paths./v1/underlying/{ticker}/trades.get.parameters.only_multi_leg.schema default: False
paths./v1/underlying/{ticker}/trades.get.parameters.exclude_multi_leg.schema default: False
paths./v1/underlying/{ticker}/trades.get.parameters.moneyness.schema enum: ['ITM', 'ATM', 'OTM']
paths./v1/underlying/{ticker}/trades.get.parameters.min_premium.schema minimum: 0
components.schemas.OptionTradeListSuccess.properties.data.items ref OptionTradeRow
components.schemas.OptionTradeListSuccess.properties.meta ref Meta
components.schemas.OptionTradeRow description: Enriched single-trade row served by the trades endpoints. Most fields are always present; `*Pct`, `nextIv`, `agg*`, `strategy*`, and `earnings*` are optional. 
components.schemas.OptionTradeRow.properties.date description: Days since 1970-01-01 (compact session date).
components.schemas.OptionTradeRow.properties.tsEvent description: Trade event timestamp in milliseconds since epoch.
components.schemas.OptionTradeRow.properties.tsEventUs description: Microsecond-precision timestamp (contract-trades endpoint only).
components.schemas.OptionTradeRow.properties.expiration description: Expiration as days since 1970-01-01.
components.schemas.OptionTradeRow.properties.right enum: ['C', 'P']
components.schemas.OptionTradeRow.properties.size minimum: 0
components.schemas.OptionTradeRow.properties.side description: Granular execution-side label — `BB` (below bid), `B` (bid), `AB` (above bid), `M` (mid), `BA` (below ask), `A` (ask), `AA` (above ask), or `N` (no BBO). 
components.schemas.OptionTradeRow.properties.side enum: ['BB', 'B', 'AB', 'M', 'BA', 'A', 'AA', 'N']
components.schemas.OptionTradeRow.properties.bidPx nullable: True
components.schemas.OptionTradeRow.properties.askPx nullable: True
components.schemas.OptionTradeRow.properties.bidSz nullable: True
components.schemas.OptionTradeRow.properties.askSz nullable: True
components.schemas.OptionTradeRow.properties.spread nullable: True
components.schemas.OptionTradeRow.properties.iv nullable: True
components.schemas.OptionTradeRow.properties.moneyness enum: ['ITM', 'ATM', 'OTM']
components.schemas.OptionTradeRow.properties.openInterest minimum: 0
components.schemas.OptionTradeRow.properties.prevOi minimum: 0
components.schemas.OptionTradeRow.properties.prevClose nullable: True
components.schemas.OptionTradeRow.properties.prevCloseAge minimum: 0
components.schemas.OptionTradeRow.properties.prevCloseAge nullable: True
components.schemas.OptionTradeRow.properties.prevCloseAge description: Trading days back the `prevClose` came from (0 = yesterday).
components.schemas.OptionTradeRow.properties.priceChange nullable: True
components.schemas.OptionTradeRow.properties.dailyVolume minimum: 0
components.schemas.OptionTradeRow.properties.ivDirection enum: [-1, 0, 1]
components.schemas.OptionTradeRow.properties.ivDirection description: -1 = down, 0 = flat/unknown, 1 = up.
components.schemas.OptionTradeRow.properties.ingestionTimestamp description: Server ingest time in milliseconds since epoch.
components.schemas.OptionTradeRow.properties.prevIv nullable: True
components.schemas.OptionTradeRow.properties.nextIv nullable: True
components.schemas.OptionTradeRow.properties.premiumPercentile enum: [0, 50, 75, 90, 95, 99]
components.schemas.OptionTradeRow.properties.premiumPercentile description: Bucketed premium percentile band (0 = below P50, 99 = P99+).
components.schemas.OptionTradeRow.properties.flowScore minimum: -100
components.schemas.OptionTradeRow.properties.flowScore maximum: 100
components.schemas.OptionTradeRow.properties.aggCount minimum: 0
components.schemas.OptionTradeRow.properties.aggTotalSize minimum: 0
components.schemas.OptionTradeRow.properties.mlSibling description: True when this leg was included via spread association rather than its own filter match.
components.schemas.OptionTradeRow.properties.strategyLegCount minimum: 1

## SKY061 https://docs.skylit.ai/api-reference/underlying/premium-volume-by-strike
paths./v1/underlying/{ticker}/by-strike.get summary: Premium / volume by strike
paths./v1/underlying/{ticker}/by-strike.get description: Strike-level distribution of call/put premium, volume, and OI for the requested window, plus chain-wide aggregates and a max-pain estimate. 
paths./v1/underlying/{ticker}/by-strike.get.parameters ref Ticker
paths./v1/underlying/{ticker}/by-strike.get.parameters.interval.schema enum: ['1D', '1W', '7D']
paths./v1/underlying/{ticker}/by-strike.get.parameters.interval.schema default: 1D
paths./v1/underlying/{ticker}/by-strike.get.parameters.dte_filter description: DTE bucket — `all`, `0-7`, `8-30`, `31-90`, or `90+`.
paths./v1/underlying/{ticker}/by-strike.get.parameters.dte_filter.schema enum: ['all', '0-7', '8-30', '31-90', '90+']
paths./v1/underlying/{ticker}/by-strike.get.parameters.dte_filter.schema default: all
paths./v1/underlying/{ticker}/by-strike.get.parameters ref DateQuery
components.schemas.StrikeDistributionSuccess.properties.data ref StrikeDistributionResponse
components.schemas.StrikeDistributionSuccess.properties.meta ref Meta
components.schemas.StrikeDistributionResponse.properties.interval enum: ['1D', '1W', '7D']
components.schemas.StrikeDistributionResponse.properties.dteFilter enum: ['all', '0-7', '8-30', '31-90', '90+']
components.schemas.StrikeDistributionResponse.properties.totalCallVolume minimum: 0
components.schemas.StrikeDistributionResponse.properties.totalPutVolume minimum: 0
components.schemas.StrikeDistributionResponse.properties.topStrike description: Strike with the highest combined call+put premium.
components.schemas.StrikeDistributionResponse.properties.strikeCount minimum: 0
components.schemas.StrikeDistributionResponse.properties.maxPain description: Strike at which total option-holder payout would be minimized.
components.schemas.StrikeDistributionResponse.properties.bars.items ref StrikeDistributionBar
components.schemas.StrikeDistributionBar.properties.callVolume minimum: 0
components.schemas.StrikeDistributionBar.properties.putVolume minimum: 0
components.schemas.StrikeDistributionBar.properties.callOi minimum: 0
components.schemas.StrikeDistributionBar.properties.putOi minimum: 0

## SKY062 https://docs.skylit.ai/api-reference/underlying/premium-volume-by-expiration-for-a-strike
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get summary: Premium / volume by expiration for a strike
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get description: For a single strike on the underlying, breaks the requested window's premium and volume out by expiration date. 
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get.parameters ref Ticker
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get.parameters.strike description: Strike price (decimal allowed; e.g. `580` or `580.5`).
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get.parameters.interval.schema enum: ['1D', '1W', '7D']
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get.parameters.interval.schema default: 1D
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get.parameters.dte_filter.schema enum: ['all', '0-7', '8-30', '31-90', '90+']
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get.parameters.dte_filter.schema default: all
paths./v1/underlying/{ticker}/by-strike/{strike}/expirations.get.parameters ref DateQuery
components.schemas.ExpirationDistributionSuccess.properties.data ref ExpirationDistributionResponse
components.schemas.ExpirationDistributionSuccess.properties.meta ref Meta
components.schemas.ExpirationDistributionResponse.properties.interval enum: ['1D', '1W', '7D']
components.schemas.ExpirationDistributionResponse.properties.expirationCount minimum: 0
components.schemas.ExpirationDistributionResponse.properties.bars.items ref ExpirationDistributionBar
components.schemas.ExpirationDistributionBar.properties.callVolume minimum: 0
components.schemas.ExpirationDistributionBar.properties.putVolume minimum: 0

## SKY063 https://docs.skylit.ai/api-reference/underlying/list-traded-expirations-for-a-ticker
paths./v1/underlying/{ticker}/expirations.get summary: List traded expirations for a ticker
paths./v1/underlying/{ticker}/expirations.get description: Returns each expiration that traded on `date`, with per-expiration call/put volume + premium and the unique-contract count. 
paths./v1/underlying/{ticker}/expirations.get.parameters ref Ticker
paths./v1/underlying/{ticker}/expirations.get.parameters ref DateQuery
components.schemas.ExpirationListSuccess.properties.data.items ref ExpirationItem
components.schemas.ExpirationListSuccess.properties.meta ref Meta
components.schemas.ExpirationItem.properties.callVolume minimum: 0
components.schemas.ExpirationItem.properties.putVolume minimum: 0
components.schemas.ExpirationItem.properties.contractCount minimum: 0

## SKY064 https://docs.skylit.ai/api-reference/underlying/option-chain-snapshot
paths./v1/underlying/{ticker}/chain.get summary: Option chain snapshot
paths./v1/underlying/{ticker}/chain.get description: Snapshot of the option chain for a single expiration on the requested date — call & put volume, premium, OI, last IV, and last trade price per strike, plus the underlying price. 
paths./v1/underlying/{ticker}/chain.get.parameters ref Ticker
paths./v1/underlying/{ticker}/chain.get.parameters.expiration description: Expiration date (`YYYY-MM-DD`).
paths./v1/underlying/{ticker}/chain.get.parameters.min_volume description: Suppress strikes whose total (call+put) volume is below this floor.
paths./v1/underlying/{ticker}/chain.get.parameters.min_volume.schema minimum: 0
paths./v1/underlying/{ticker}/chain.get.parameters ref DateQuery
components.schemas.ChainSuccess.properties.data ref ChainResponse
components.schemas.ChainSuccess.properties.meta ref Meta
components.schemas.ChainResponse.properties.strikes.items ref ChainItem
components.schemas.ChainItem.properties.callVolume minimum: 0
components.schemas.ChainItem.properties.callOi minimum: 0
components.schemas.ChainItem.properties.callIv nullable: True
components.schemas.ChainItem.properties.callIv description: Last call-side IV in the bucket. May be null when no quotes are available.
components.schemas.ChainItem.properties.putVolume minimum: 0
components.schemas.ChainItem.properties.putOi minimum: 0
components.schemas.ChainItem.properties.putIv nullable: True

## SKY065 https://docs.skylit.ai/api-reference/underlying/daily-history-for-a-ticker
paths./v1/underlying/{ticker}/history.get summary: Daily history for a ticker
paths./v1/underlying/{ticker}/history.get description: Daily aggregates (premium, volume, call/put split, net premium) between `startDate` and `endDate` (inclusive), one row per trading day with activity. 
paths./v1/underlying/{ticker}/history.get.parameters ref Ticker
components.schemas.UnderlyingHistorySuccess.properties.data.items ref UnderlyingHistoryItem
components.schemas.UnderlyingHistorySuccess.properties.meta ref Meta
components.schemas.UnderlyingHistoryItem.properties.totalVolume minimum: 0
components.schemas.UnderlyingHistoryItem.properties.callVolume minimum: 0
components.schemas.UnderlyingHistoryItem.properties.putVolume minimum: 0

## SKY066 https://docs.skylit.ai/api-reference/underlying/relative-volume-bars-for-a-ticker
paths./v1/underlying/{ticker}/rvol.get summary: Relative-volume bars for a ticker
paths./v1/underlying/{ticker}/rvol.get description: Time-bucketed bars with call/put volume + premium and an average-volume baseline computed from `avgPeriod` recent days, plus aggregate RVOL stats. 
paths./v1/underlying/{ticker}/rvol.get.parameters ref Ticker
paths./v1/underlying/{ticker}/rvol.get.parameters.interval description: Trailing window — `{N}D` where N is 1–365 (e.g. `1D`, `7D`, `30D`).
paths./v1/underlying/{ticker}/rvol.get.parameters.interval.schema default: 1D
paths./v1/underlying/{ticker}/rvol.get.parameters.bucket.schema enum: ['1min', '5min', '10min', '15min', '30min', '1d', '1w']
paths./v1/underlying/{ticker}/rvol.get.parameters.bucket.schema default: 5min
paths./v1/underlying/{ticker}/rvol.get.parameters.avg_period description: Baseline lookback as `{N}d` (e.g. `14d`, `30d`). Max 365 days.
paths./v1/underlying/{ticker}/rvol.get.parameters.avg_period.schema default: 14d
paths./v1/underlying/{ticker}/rvol.get.parameters ref DateQuery
paths./v1/underlying/{ticker}/rvol.get.parameters.order_by.schema enum: ['rvol', 'volume', 'premium', 'time']
paths./v1/underlying/{ticker}/rvol.get.parameters.order_by.schema default: time
paths./v1/underlying/{ticker}/rvol.get.parameters.order description: Sort direction. Defaults to `asc` when `order_by=time`, otherwise `desc`.
paths./v1/underlying/{ticker}/rvol.get.parameters.order.schema enum: ['asc', 'desc']
paths./v1/underlying/{ticker}/rvol.get.parameters.limit.schema minimum: 1
paths./v1/underlying/{ticker}/rvol.get.parameters.format.schema enum: ['full', 'summary']
paths./v1/underlying/{ticker}/rvol.get.parameters.format.schema default: full
components.schemas.UnderlyingRvolSuccess.properties.data ref UnderlyingRvolResponse
components.schemas.UnderlyingRvolSuccess.properties.meta ref Meta
components.schemas.UnderlyingRvolResponse.properties.bars.items ref UnderlyingRvolBar
components.schemas.UnderlyingRvolResponse.properties.stats ref RvolStats
components.schemas.UnderlyingRvolResponse.properties.callRvol description: Aggregate call-volume RVOL.
components.schemas.UnderlyingRvolResponse.properties.putRvol description: Aggregate put-volume RVOL.
components.schemas.UnderlyingRvolBar.properties.callVolume minimum: 0
components.schemas.UnderlyingRvolBar.properties.putVolume minimum: 0
components.schemas.UnderlyingRvolBar.properties.volume minimum: 0
components.schemas.UnderlyingRvolBar.properties.avgCallVolume nullable: True
components.schemas.UnderlyingRvolBar.properties.avgPutVolume nullable: True
components.schemas.UnderlyingRvolBar.properties.avgVolume nullable: True
components.schemas.UnderlyingRvolBar.properties.avgPremium nullable: True
components.schemas.UnderlyingRvolBar.properties.avgDaysCount nullable: True
components.schemas.RvolStats.properties.todayVolume minimum: 0
components.schemas.RvolStats.properties.rvolVolume description: `todayVolume / avgVolume`.
components.schemas.RvolStats.properties.rvolPremium description: `todayPremium / avgPremium`.
components.schemas.RvolStats.properties.avgDaysCount minimum: 0
components.schemas.RvolStats.properties.avgDaysCount description: Number of days actually used in the baseline.

## SKY067 https://docs.skylit.ai/api-reference/contract/top-contracts-by-daily-flow
paths./v1/contract/top/daily.get summary: Top contracts by daily flow
paths./v1/contract/top/daily.get description: Single-day top-contract screener with full-spectrum filters (premium / volume / OI / IV / DTE / strike windows, call vs put, sweep vs multi-leg). Sortable by `premium`, `volume`, `oi`, or `iv`. 
paths./v1/contract/top/daily.get.parameters.limit description: Maximum rows to return. Server caps at 500.
paths./v1/contract/top/daily.get.parameters.limit.schema default: 100
paths./v1/contract/top/daily.get.parameters.limit.schema minimum: 1
paths./v1/contract/top/daily.get.parameters.limit.schema maximum: 500
paths./v1/contract/top/daily.get.parameters ref DateQuery
paths./v1/contract/top/daily.get.parameters.min_volume.schema minimum: 0
paths./v1/contract/top/daily.get.parameters.max_volume.schema minimum: 0
paths./v1/contract/top/daily.get.parameters.min_oi.schema minimum: 0
paths./v1/contract/top/daily.get.parameters.max_oi.schema minimum: 0
paths./v1/contract/top/daily.get.parameters.right.schema enum: ['C', 'P']
paths./v1/contract/top/daily.get.parameters.order_by.schema enum: ['premium', 'volume', 'oi', 'iv']
paths./v1/contract/top/daily.get.parameters.order_by.schema default: premium
paths./v1/contract/top/daily.get.parameters.order.schema enum: ['asc', 'desc']
paths./v1/contract/top/daily.get.parameters.order.schema default: desc
paths./v1/contract/top/daily.get.parameters.only_sweeps.schema default: False
paths./v1/contract/top/daily.get.parameters.only_multi_leg.schema default: False
paths./v1/contract/top/daily.get.parameters.exclude_multi_leg.schema default: False
components.schemas.TopContractListSuccess.properties.data.items ref TopContractItem
components.schemas.TopContractListSuccess.properties.meta ref Meta
components.schemas.TopContractItem.properties.right enum: ['C', 'P']
components.schemas.TopContractItem.properties.totalVolume minimum: 0
components.schemas.TopContractItem.properties.openInterest minimum: 0
components.schemas.TopContractItem.properties.bidVolume minimum: 0
components.schemas.TopContractItem.properties.askVolume minimum: 0
components.schemas.TopContractItem.properties.midVolume minimum: 0
components.schemas.TopContractItem.properties.tradeCount minimum: 0
components.schemas.TopContractItem.properties.sweepVolume minimum: 0
components.schemas.TopContractItem.properties.multiLegVolume minimum: 0

## SKY068 https://docs.skylit.ai/api-reference/contract/top-contracts-by-trailing-5-day-flow
paths./v1/contract/top/weekly.get summary: Top contracts by trailing-5-day flow
paths./v1/contract/top/weekly.get description: Same shape as `/v1/contract/top/daily`, rolled up over the trailing 5 trading days ending on `date`. 
paths./v1/contract/top/weekly.get.parameters.limit description: Maximum rows to return. Server caps at 500.
paths./v1/contract/top/weekly.get.parameters.limit.schema default: 100
paths./v1/contract/top/weekly.get.parameters.limit.schema minimum: 1
paths./v1/contract/top/weekly.get.parameters.limit.schema maximum: 500
paths./v1/contract/top/weekly.get.parameters ref DateQuery
paths./v1/contract/top/weekly.get.parameters.min_volume.schema minimum: 0
paths./v1/contract/top/weekly.get.parameters.max_volume.schema minimum: 0
paths./v1/contract/top/weekly.get.parameters.min_oi.schema minimum: 0
paths./v1/contract/top/weekly.get.parameters.max_oi.schema minimum: 0
paths./v1/contract/top/weekly.get.parameters.right.schema enum: ['C', 'P']
paths./v1/contract/top/weekly.get.parameters.order_by.schema enum: ['premium', 'volume', 'oi', 'iv']
paths./v1/contract/top/weekly.get.parameters.order_by.schema default: premium
paths./v1/contract/top/weekly.get.parameters.order.schema enum: ['asc', 'desc']
paths./v1/contract/top/weekly.get.parameters.order.schema default: desc
paths./v1/contract/top/weekly.get.parameters.only_sweeps.schema default: False
paths./v1/contract/top/weekly.get.parameters.only_multi_leg.schema default: False
paths./v1/contract/top/weekly.get.parameters.exclude_multi_leg.schema default: False
components.schemas.TopContractListSuccess.properties.data.items ref TopContractItem
components.schemas.TopContractListSuccess.properties.meta ref Meta

## SKY069 https://docs.skylit.ai/api-reference/contract/contracts-with-unusual-relative-volume
paths./v1/contract/unusual-volume.get summary: Contracts with unusual relative volume
paths./v1/contract/unusual-volume.get description: Contracts whose volume on the target date is anomalously high relative to a `avgPeriod`-day baseline. Filters cover RVOL, raw volume, OI dynamics, premium, IV, moneyness, sweep / multi-leg, and ticker include / exclude lists. Sortable by `rvol`, `volume`, `premium`, `vol_oi`, or `oi_change`. 
paths./v1/contract/unusual-volume.get.parameters ref DiscoveryLimit
paths./v1/contract/unusual-volume.get.parameters.min_rvol.schema default: 2
paths./v1/contract/unusual-volume.get.parameters.avg_period description: Baseline window as `{N}d`. Must be 2–365 days.
paths./v1/contract/unusual-volume.get.parameters.avg_period.schema default: 10d
paths./v1/contract/unusual-volume.get.parameters.min_avg_volume.schema minimum: 0
paths./v1/contract/unusual-volume.get.parameters.min_avg_volume.schema default: 100
paths./v1/contract/unusual-volume.get.parameters.right.schema enum: ['C', 'P']
paths./v1/contract/unusual-volume.get.parameters.date description: Target trading date (`YYYY-MM-DD`). Defaults to the **previous calendar day** (not the current trading date) since baselines need a settled session. 
paths./v1/contract/unusual-volume.get.parameters.order_by.schema enum: ['rvol', 'volume', 'premium', 'vol_oi', 'oi_change']
paths./v1/contract/unusual-volume.get.parameters.order_by.schema default: rvol
paths./v1/contract/unusual-volume.get.parameters.min_bid_imbalance.schema minimum: 0
paths./v1/contract/unusual-volume.get.parameters.min_bid_imbalance.schema maximum: 1
paths./v1/contract/unusual-volume.get.parameters.min_ask_imbalance.schema minimum: 0
paths./v1/contract/unusual-volume.get.parameters.min_ask_imbalance.schema maximum: 1
paths./v1/contract/unusual-volume.get.parameters.moneyness.schema enum: ['ITM', 'ATM', 'OTM']
paths./v1/contract/unusual-volume.get.parameters.exclude_tickers description: Comma-separated tickers to exclude (e.g. `SPY,QQQ,IWM`).
components.parameters.DiscoveryLimit description: Maximum rows to return.
components.parameters.DiscoveryLimit.schema minimum: 1
components.parameters.DiscoveryLimit.schema maximum: 200
components.parameters.DiscoveryLimit.schema default: 50
components.schemas.UnusualVolumeListSuccess.properties.data.items ref UnusualVolumeItem
components.schemas.UnusualVolumeListSuccess.properties.meta ref Meta
components.schemas.UnusualVolumeItem.properties.right enum: ['C', 'P']
components.schemas.UnusualVolumeItem.properties.volume minimum: 0
components.schemas.UnusualVolumeItem.properties.avgVolume description: Baseline volume over the requested `avgPeriod`.
components.schemas.UnusualVolumeItem.properties.rvol description: `volume / avgVolume`.
components.schemas.UnusualVolumeItem.properties.openInterest minimum: 0
components.schemas.UnusualVolumeItem.properties.prevOi minimum: 0
components.schemas.UnusualVolumeItem.properties.bidVolume minimum: 0
components.schemas.UnusualVolumeItem.properties.askVolume minimum: 0
components.schemas.UnusualVolumeItem.properties.sweepVolume minimum: 0
components.schemas.UnusualVolumeItem.properties.multiLegVolume minimum: 0

## SKY070 https://docs.skylit.ai/api-reference/contract/contracts-with-significant-oi-changes
paths./v1/contract/unusual-oi.get summary: Contracts with significant OI changes
paths./v1/contract/unusual-oi.get description: Contracts whose open interest changed by at least `min_oi_change` (or `min_oi_change_pct`) on the target date. `direction` narrows the result to opening (OI ↑) or closing (OI ↓) flow. 
paths./v1/contract/unusual-oi.get.parameters ref DiscoveryLimit
paths./v1/contract/unusual-oi.get.parameters.min_oi_change.schema default: 500
paths./v1/contract/unusual-oi.get.parameters.min_oi_change_pct.schema default: 25
paths./v1/contract/unusual-oi.get.parameters.right.schema enum: ['C', 'P']
paths./v1/contract/unusual-oi.get.parameters.min_volume.schema minimum: 0
paths./v1/contract/unusual-oi.get.parameters.date description: Target trading date (`YYYY-MM-DD`). Defaults to the **previous calendar day** (not the current trading date). 
paths./v1/contract/unusual-oi.get.parameters.order_by.schema enum: ['oi_change', 'oi_change_pct', 'volume', 'premium']
paths./v1/contract/unusual-oi.get.parameters.order_by.schema default: oi_change
paths./v1/contract/unusual-oi.get.parameters.direction.schema enum: ['opening', 'closing', 'both']
paths./v1/contract/unusual-oi.get.parameters.direction.schema default: both
components.schemas.UnusualOiListSuccess.properties.data.items ref UnusualOiItem
components.schemas.UnusualOiListSuccess.properties.meta ref Meta
components.schemas.UnusualOiItem.properties.right enum: ['C', 'P']
components.schemas.UnusualOiItem.properties.openInterest minimum: 0
components.schemas.UnusualOiItem.properties.prevOi minimum: 0
components.schemas.UnusualOiItem.properties.volume minimum: 0
components.schemas.UnusualOiItem.properties.bidVolume minimum: 0
components.schemas.UnusualOiItem.properties.askVolume minimum: 0
components.schemas.UnusualOiItem.properties.positionType enum: ['opening', 'closing']
components.schemas.UnusualOiItem.properties.sweepVolume minimum: 0
components.schemas.UnusualOiItem.properties.multiLegVolume minimum: 0

## SKY071 https://docs.skylit.ai/api-reference/contract/bulk-contract-stats-for-a-list-of-symbols
paths./v1/contract/bulk/stats.get summary: Bulk contract stats for a list of symbols
paths./v1/contract/bulk/stats.get description: Returns a single-day `ContractStats` record per requested OPRA symbol. Symbols absent from the response had no activity that day. 
paths./v1/contract/bulk/stats.get.parameters.symbols description: Comma-separated OPRA symbols (max 50).
paths./v1/contract/bulk/stats.get.parameters ref DateQuery
components.schemas.ContractStatsListSuccess.properties.data.items ref ContractStats
components.schemas.ContractStatsListSuccess.properties.meta ref Meta
components.schemas.ContractStats.properties.right enum: ['C', 'P']
components.schemas.ContractStats.properties.totalVolume minimum: 0
components.schemas.ContractStats.properties.openInterest minimum: 0
components.schemas.ContractStats.properties.bidVolume minimum: 0
components.schemas.ContractStats.properties.askVolume minimum: 0
components.schemas.ContractStats.properties.midVolume minimum: 0
components.schemas.ContractStats.properties.tradeCount minimum: 0
components.schemas.ContractStats.properties.sweepVolume minimum: 0
components.schemas.ContractStats.properties.multiLegVolume minimum: 0

## SKY072 https://docs.skylit.ai/api-reference/contract/daily-stats-for-a-single-contract
paths./v1/contract/{symbol}/stats.get summary: Daily stats for a single contract
paths./v1/contract/{symbol}/stats.get.parameters ref OptionSymbol
paths./v1/contract/{symbol}/stats.get.parameters ref DateQuery
components.schemas.ContractStatsSuccess.properties.data ref ContractStats
components.schemas.ContractStatsSuccess.properties.meta ref Meta

## SKY073 https://docs.skylit.ai/api-reference/contract/intraday-chart-bars-for-a-contract
paths./v1/contract/{symbol}/chart.get summary: Intraday chart bars for a contract
paths./v1/contract/{symbol}/chart.get description: Time-bucketed bars for a single contract — granular bid/mid/ask execution split, premium and volume per side, daily cumulative totals, VWAP, and (when available) IV and 30D average baselines. 
paths./v1/contract/{symbol}/chart.get.parameters ref OptionSymbol
paths./v1/contract/{symbol}/chart.get.parameters.interval description: Trailing window — `{N}D` where N is 1–365 (e.g. `1D`, `7D`).
paths./v1/contract/{symbol}/chart.get.parameters.bucket.schema enum: ['1min', '5min', '10min', '15min', '30min', '1d', '1w']
components.schemas.ContractChartSuccess.properties.data.items ref ContractChartBar
components.schemas.ContractChartSuccess.properties.meta ref Meta
components.schemas.ContractChartBar description: One bucketed bar in the contract-chart response. 
components.schemas.ContractChartBar.properties.belowBidVolume minimum: 0
components.schemas.ContractChartBar.properties.bidVolume minimum: 0
components.schemas.ContractChartBar.properties.aboveBidVolume minimum: 0
components.schemas.ContractChartBar.properties.midVolume minimum: 0
components.schemas.ContractChartBar.properties.belowAskVolume minimum: 0
components.schemas.ContractChartBar.properties.askVolume minimum: 0
components.schemas.ContractChartBar.properties.aboveAskVolume minimum: 0
components.schemas.ContractChartBar.properties.noSideVolume minimum: 0
components.schemas.ContractChartBar.properties.candleVolume minimum: 0
components.schemas.ContractChartBar.properties.candleVolumeNoMl minimum: 0
components.schemas.ContractChartBar.properties.candleVolumeNoMl description: Single-leg volume (used for multi-leg % calculation).
components.schemas.ContractChartBar.properties.dailyVolume minimum: 0
components.schemas.ContractChartBar.properties.iv nullable: True

## SKY074 https://docs.skylit.ai/api-reference/contract/raw-enriched-trades-for-a-contract
paths./v1/contract/{symbol}/trades.get summary: Raw enriched trades for a contract
paths./v1/contract/{symbol}/trades.get description: Same enriched trade shape as `/v1/underlying/{ticker}/trades`, scoped to a single OPRA contract. Because the contract is fixed, chain-level filters (moneyness, strike, DTE, expiration) do not apply here. 
paths./v1/contract/{symbol}/trades.get.parameters ref OptionSymbol
paths./v1/contract/{symbol}/trades.get.parameters.start description: Lower time bound — RFC 3339 or Unix seconds. Defaults to start-of-trading-day.
paths./v1/contract/{symbol}/trades.get.parameters.end description: Upper time bound — RFC 3339 or Unix seconds. Defaults to now.
paths./v1/contract/{symbol}/trades.get.parameters.limit.schema minimum: 1
paths./v1/contract/{symbol}/trades.get.parameters.limit.schema maximum: 500
paths./v1/contract/{symbol}/trades.get.parameters.limit.schema default: 50
paths./v1/contract/{symbol}/trades.get.parameters.min_premium.schema minimum: 0
components.schemas.OptionTradeListSuccess.properties.data.items ref OptionTradeRow
components.schemas.OptionTradeListSuccess.properties.meta ref Meta

## SKY075 https://docs.skylit.ai/api-reference/contract/daily-history-for-a-contract
paths./v1/contract/{symbol}/history.get summary: Daily history for a contract
paths./v1/contract/{symbol}/history.get description: Daily aggregates per trading day in `[startDate, endDate]` — total premium / volume, OI dynamics, bid/ask execution split, sweep and multi-leg shares, VWAP, last price, IV, and trade count. 
paths./v1/contract/{symbol}/history.get.parameters ref OptionSymbol
components.schemas.ContractHistorySuccess.properties.data.items ref ContractHistoryItem
components.schemas.ContractHistorySuccess.properties.meta ref Meta
components.schemas.ContractHistoryItem.properties.totalVolume minimum: 0
components.schemas.ContractHistoryItem.properties.openInterest minimum: 0
components.schemas.ContractHistoryItem.properties.bidVolume minimum: 0
components.schemas.ContractHistoryItem.properties.askVolume minimum: 0
components.schemas.ContractHistoryItem.properties.midVolume minimum: 0
components.schemas.ContractHistoryItem.properties.sweepVolume minimum: 0
components.schemas.ContractHistoryItem.properties.multiLegVolume minimum: 0
components.schemas.ContractHistoryItem.properties.tradeCount minimum: 0

## SKY076 https://docs.skylit.ai/api-reference/contract/relative-volume-bars-for-a-contract
paths./v1/contract/{symbol}/rvol.get summary: Relative-volume bars for a contract
paths./v1/contract/{symbol}/rvol.get description: Same shape as `/v1/underlying/{ticker}/rvol` but scoped to a single contract. 
paths./v1/contract/{symbol}/rvol.get.parameters ref OptionSymbol
paths./v1/contract/{symbol}/rvol.get.parameters.interval description: Trailing window — `{N}D` where N is 1–365.
paths./v1/contract/{symbol}/rvol.get.parameters.interval.schema default: 1D
paths./v1/contract/{symbol}/rvol.get.parameters.bucket.schema enum: ['1min', '5min', '10min', '15min', '30min', '1d', '1w']
paths./v1/contract/{symbol}/rvol.get.parameters.bucket.schema default: 5min
paths./v1/contract/{symbol}/rvol.get.parameters.avg_period description: Baseline lookback as `{N}d` (e.g. `14d`). Max 365 days.
paths./v1/contract/{symbol}/rvol.get.parameters.avg_period.schema default: 14d
paths./v1/contract/{symbol}/rvol.get.parameters ref DateQuery
paths./v1/contract/{symbol}/rvol.get.parameters.order_by.schema enum: ['rvol', 'volume', 'premium', 'time']
paths./v1/contract/{symbol}/rvol.get.parameters.order_by.schema default: time
paths./v1/contract/{symbol}/rvol.get.parameters.order description: Sort direction. Defaults to `asc` when `order_by=time`, otherwise `desc`.
paths./v1/contract/{symbol}/rvol.get.parameters.order.schema enum: ['asc', 'desc']
paths./v1/contract/{symbol}/rvol.get.parameters.limit.schema minimum: 1
paths./v1/contract/{symbol}/rvol.get.parameters.format.schema enum: ['full', 'summary']
paths./v1/contract/{symbol}/rvol.get.parameters.format.schema default: full
components.schemas.ContractRvolSuccess.properties.data ref ContractRvolResponse
components.schemas.ContractRvolSuccess.properties.meta ref Meta
components.schemas.ContractRvolResponse.properties.bars.items ref ContractRvolBar
components.schemas.ContractRvolResponse.properties.stats ref RvolStats
components.schemas.ContractRvolBar.properties.volume minimum: 0
components.schemas.ContractRvolBar.properties.avgVolume nullable: True
components.schemas.ContractRvolBar.properties.avgPremium nullable: True
components.schemas.ContractRvolBar.properties.avgDaysCount nullable: True

## SKY077 https://docs.skylit.ai/api-reference/dark-pool/paginated-off-exchange-trf-prints
paths./v1/dark-pool/trades.get summary: Paginated off-exchange (TRF) prints
paths./v1/dark-pool/trades.get description: Server-side filtered dark-pool prints from the off-exchange tape (FINRA TRF, publisher FINN/FINC). Defaults to **today (ET)** with a **$1,000,000** minimum notional (the blocks-by-default rule); pass `min_notional=0` for the full firehose. The trade-date span is capped at **31 days** per request — page with `limit`/`offset` or narrow the range for more. Prints carry **no side, BBO, or greeks**. Pagination state (`limit`, `offset`, `count`, `hasMore`) is returned in `meta`. 
paths./v1/dark-pool/trades.get.parameters.tickers description: Comma-separated tickers to include (e.g. `AAPL,NVDA`). Omit for all names.
paths./v1/dark-pool/trades.get.parameters.date description: Single trade date (`YYYY-MM-DD`, ET). Defaults to today (ET).
paths./v1/dark-pool/trades.get.parameters.date_start description: Inclusive start of a trade-date range (`YYYY-MM-DD`, ET). Max span 31 days.
paths./v1/dark-pool/trades.get.parameters.date_end description: Inclusive end of a trade-date range (`YYYY-MM-DD`, ET). Max span 31 days.
paths./v1/dark-pool/trades.get.parameters.time_start description: Inclusive lower bound of the time-of-day window (`HH:MM`, ET).
paths./v1/dark-pool/trades.get.parameters.time_end description: Inclusive upper bound of the time-of-day window (`HH:MM`, ET).
paths./v1/dark-pool/trades.get.parameters.min_notional description: Minimum notional (USD). Defaults to 1,000,000. Pass 0 for the firehose.
paths./v1/dark-pool/trades.get.parameters.min_notional.schema default: 1000000
paths./v1/dark-pool/trades.get.parameters.min_size.schema minimum: 0
paths./v1/dark-pool/trades.get.parameters.max_size.schema minimum: 0
paths./v1/dark-pool/trades.get.parameters.sectors description: Comma-separated GICS sectors to include.
paths./v1/dark-pool/trades.get.parameters.industries description: Comma-separated GICS industries to include.
paths./v1/dark-pool/trades.get.parameters.venue description: Reporting venue filter. Omit for both.
paths./v1/dark-pool/trades.get.parameters.venue.schema enum: ['FINN', 'FINC']
paths./v1/dark-pool/trades.get.parameters.limit description: Page size (server caps at 5000).
paths./v1/dark-pool/trades.get.parameters.limit.schema default: 500
paths./v1/dark-pool/trades.get.parameters.limit.schema minimum: 1
paths./v1/dark-pool/trades.get.parameters.limit.schema maximum: 5000
paths./v1/dark-pool/trades.get.parameters.offset description: Row offset for pagination.
paths./v1/dark-pool/trades.get.parameters.offset.schema default: 0
paths./v1/dark-pool/trades.get.parameters.offset.schema minimum: 0
paths./v1/dark-pool/trades.get.parameters.offset.schema maximum: 50000
paths./v1/dark-pool/trades.get.parameters.order description: Sort by trade time.
paths./v1/dark-pool/trades.get.parameters.order.schema enum: ['asc', 'desc']
paths./v1/dark-pool/trades.get.parameters.order.schema default: desc
components.schemas.DarkPoolTradesSuccess.properties.data.items ref DarkPoolPrint
components.schemas.DarkPoolTradesSuccess.properties.meta ref DarkPoolTradesMeta
components.schemas.DarkPoolPrint description: One off-exchange (TRF) print. Carries no side / BBO / greeks. 
components.schemas.DarkPoolPrint.properties.timestamp description: Trade time, ISO-8601 UTC (millisecond precision).
components.schemas.DarkPoolPrint.properties.ticker description: Underlying (dotted equity symbol, e.g. `BRK.B`).
components.schemas.DarkPoolPrint.properties.size minimum: 0
components.schemas.DarkPoolPrint.properties.size description: Shares.
components.schemas.DarkPoolPrint.properties.notional description: `price × size` (USD).
components.schemas.DarkPoolPrint.properties.venue enum: ['FINN', 'FINC']
components.schemas.DarkPoolPrint.properties.venue description: FINRA TRF reporting venue.
components.schemas.DarkPoolPrint.properties.sector description: GICS sector of the underlying.
components.schemas.DarkPoolPrint.properties.industry description: GICS industry of the underlying.
components.schemas.DarkPoolTradesMeta.allOf ref Meta
components.schemas.DarkPoolTradesMeta.allOf.properties.limit description: Page size applied (after clamping to 1..=5000).
components.schemas.DarkPoolTradesMeta.allOf.properties.offset description: Row offset applied.
components.schemas.DarkPoolTradesMeta.allOf.properties.count description: Number of prints returned in this page.
components.schemas.DarkPoolTradesMeta.allOf.properties.hasMore description: `true` when the page is full (`count == limit`), so more rows may exist. Offset-based heuristic, not an exact total. 

## SKY078 https://docs.skylit.ai/api-reference/dark-pool/largest-individual-dark-pool-prints-for-a-ticker
paths./v1/dark-pool/top-prints/{ticker}.get summary: Largest individual dark-pool prints for a ticker
paths./v1/dark-pool/top-prints/{ticker}.get description: The top-N largest individual off-exchange prints for `{ticker}` over a trailing window, ordered by notional descending. Each row is a single TRF print (not an aggregate), useful as a support/resistance anchor. 
paths./v1/dark-pool/top-prints/{ticker}.get.parameters ref Ticker
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.top_n description: Number of largest prints to return.
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.top_n.schema default: 5
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.top_n.schema minimum: 1
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.top_n.schema maximum: 20
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.lookback_days description: Calendar-day trailing window.
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.lookback_days.schema default: 45
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.lookback_days.schema minimum: 1
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.lookback_days.schema maximum: 180
paths./v1/dark-pool/top-prints/{ticker}.get.parameters.as_of_date description: Optional anchor date (`YYYY-MM-DD`); the window becomes `[as_of_date - lookback_days, as_of_date]`. Omit for a today-anchored window. 
components.schemas.DarkPoolTopPrintsSuccess.properties.data.items ref DarkPoolTopPrint
components.schemas.DarkPoolTopPrintsSuccess.properties.meta ref Meta
components.schemas.DarkPoolTopPrint description: One of the largest individual dark-pool prints over the window.
components.schemas.DarkPoolTopPrint.properties.timestamp description: Trade time, ISO-8601 UTC.
components.schemas.DarkPoolTopPrint.properties.notional description: `price × size` (USD).
components.schemas.DarkPoolTopPrint.properties.size minimum: 0
components.schemas.DarkPoolTopPrint.properties.size description: Shares.

## SKY079 https://docs.skylit.ai/api-reference/meta/this-openapi-specification-as-json
paths./v1/openapi.json.get summary: This OpenAPI specification, as JSON

## SKY092 https://docs.skylit.ai/api-reference/history/ohlcv-price-bars-for-a-symbol-and-resolution
paths./v1/history.get summary: OHLCV price bars for a symbol and resolution
paths./v1/history.get description: TradingView UDF history bars for one `symbol` at one `resolution`, covering `[from, to)` (Unix seconds; `to` is exclusive). Returns column arrays (`t`, `o`, `h`, `l`, `c`, `v`) of equal length, oldest-first. When the window holds no bars the response is a `200` with `{ "s": "no_data" }` (plus `nextTime` pointing at the nearest earlier bar when one exists), per the UDF contract. Equity bars also carry sided-volume columns (`bv`/`sv`/`uv` = buy / sell / unclassified) where available.  ## Request-window limit  One call may span at most a fixed number of **trading days**, set by the bar tier the resolution reads from — not by the resolution itself. `240` and `60` share the 1-hour tier and therefore share its allowance.  | Tier   | Resolutions                | Max trading days / request | |--------|----------------------------|---------------------------:| | 1-min  | `1` `2` `3` `5` `15` `30`  |                         90 | | 1-hour | `60` `240` `480`           |                        720 | | 1-day  | `D` `W`                    |                      2,600 |  A window **wider than the cap is rejected with `400`**, carrying the two numbers a client needs to react (`requested_days`, `max_days`). It is never silently shortened — a short `{ "s": "ok" }` always means the data ends there, never that your range was clipped. Page through anything wider in windows of `max_days` or fewer.  A rejected `400` **still debits 1 credit**, because metering happens before the request is inspected. The caps are fixed and published here, so check your range before sending it rather than discovering the limit by retrying — a client that retries a `400` unchanged burns credits without ever succeeding. `/v1/config` is free if you would rather read the feed's capabilities first.  Cache-Control tracks data freshness: today `max-age=2`, the prior session `max-age=60`, older complete days `immutable`. A `400` is `no-store`. 
paths./v1/history.get.parameters ref Symbol
paths./v1/history.get.parameters.resolution description: Bar size. Intraday minutes or `D`/`W`.
paths./v1/history.get.parameters.resolution.schema enum: ['1', '2', '3', '5', '15', '30', '60', '240', '480', 'D', 'W']
paths./v1/history.get.parameters.from description: Window start, Unix seconds (UTC).
paths./v1/history.get.parameters.to description: Window end, Unix seconds (UTC).
paths./v1/history.get.parameters.countback description: When set, return exactly this many bars ending at `to` (takes precedence over `from`, per the UDF spec). 
paths./v1/history.get.parameters.countback.schema minimum: 1
paths./v1/history.get.parameters.extended description: Include extended-hours (pre / post-market) bars. Default is regular trading hours only (09:30–16:00 ET). 
paths./v1/history.get.parameters.extended.schema default: False
components.parameters.Symbol description: Ticker (e.g. `SPY`).
components.schemas.HistoryOk.properties.s enum: ['ok']
components.schemas.HistoryOk.properties.s description: Status flag.
components.schemas.HistoryOk.properties.t description: Bar open times, Unix seconds (UTC), oldest-first.
components.schemas.HistoryOk.properties.o description: Opens.
components.schemas.HistoryOk.properties.h description: Highs.
components.schemas.HistoryOk.properties.l description: Lows.
components.schemas.HistoryOk.properties.c description: Closes.
components.schemas.HistoryOk.properties.v description: Volumes.
components.schemas.HistoryOk.properties.bv description: Buy (aggressor) volume per bar, equities where available.
components.schemas.HistoryOk.properties.sv description: Sell (aggressor) volume per bar.
components.schemas.HistoryOk.properties.uv description: Unclassified volume per bar.
components.schemas.HistoryNoData.properties.s enum: ['no_data']
components.schemas.HistoryNoData.properties.nextTime description: Unix seconds of the nearest earlier bar, when one exists.
components.schemas.HistoryError description: UDF-shaped error body for a rejected `/v1/history` request. `errmsg` is the human-readable text a TradingView datafeed surfaces; `requested_days` and `max_days` are additive fields for programmatic callers, which are the ones that have to react — compute your page size from `max_days` rather than hardcoding a cap that later drifts. 
components.schemas.HistoryError.properties.s enum: ['error']
components.schemas.HistoryError.properties.requested_days description: Trading days the requested window spans.
components.schemas.HistoryError.properties.max_days description: Trading days one request may span at this resolution's tier.
components.schemas.Error.properties.error.properties.code description: Stable machine-readable code.
components.securitySchemes.bearerApiKey description: Skylit API key in the `Authorization` header (`Authorization: Bearer <key>`). `X-API-Key` is also accepted. The same key works across Atlas, Heatseeker, and Flowseeker. 

## SKY093 https://docs.skylit.ai/api-reference/symbols/search-symbols
paths./v1/search.get summary: Search symbols
paths./v1/search.get description: Ranked symbol search for the datafeed's symbol picker (exact ticker > prefix > substring). Returns up to `limit` matches. 
paths./v1/search.get.parameters.query description: Search text (ticker or name fragment).
paths./v1/search.get.parameters.limit description: Max results.
paths./v1/search.get.parameters.limit.schema default: 25
paths./v1/search.get.parameters.limit.schema minimum: 1
paths./v1/search.get.parameters.limit.schema maximum: 500
components.schemas.SearchResult.properties.symbol description: Canonical internal identifier (echo back to /v1/symbols and /v1/history).
components.schemas.SearchResult.properties.ticker description: Display ticker shown in the picker.
components.schemas.SearchResult.properties description: {'type': 'string'}

## SKY094 https://docs.skylit.ai/api-reference/symbols/resolve-a-symbol
paths./v1/symbols.get summary: Resolve a symbol
paths./v1/symbols.get description: The TradingView `LibrarySymbolInfo` for one ticker — price scale, session, timezone, and supported resolutions the charting library needs before requesting history. 
paths./v1/symbols.get.parameters ref Symbol
components.schemas.SymbolInfo description: TradingView `LibrarySymbolInfo`.
components.schemas.SymbolInfo.properties description: {'type': 'string'}
components.schemas.UdfError description: Symbol-resolution error (UDF-native shape).
components.schemas.UdfError.properties.success enum: [False]

## SKY095 https://docs.skylit.ai/api-reference/meta/datafeed-configuration
paths./v1/config.get summary: Datafeed configuration
paths./v1/config.get description: The static UDF `DatafeedConfiguration` — supported resolutions, exchanges, symbol types, and feature flags. Free.  Also carries **`max_fetch_trading_days`**: the `/v1/history` request-window cap, keyed by every advertised resolution. Read it once at startup and size your history pages from it, rather than hardcoding a window that later drifts — or discovering the limit by being rejected, which costs a credit each time. This call is free precisely so the limit is knowable in advance.  The values are served from the same table the server enforces, so they cannot disagree with it. A charting client can ignore the field: it is not part of the UDF spec, and TradingView skips config keys it does not recognise.  ⚠ Cached for an hour (`max-age=3600`), so treat a `400` naming a `max_days` SMALLER than your cached value as authoritative and re-read this endpoint. 
components.schemas.DatafeedConfig.properties.max_fetch_trading_days description: Max trading days one `/v1/history` request may span, keyed by resolution. Resolutions sharing a bar tier share a value — `60`, `240` and `480` all read hourly bars and all cap at 720. 

## SKY096 https://docs.skylit.ai/api-reference/meta/server-time
paths./v1/time.get summary: Server time
paths./v1/time.get description: Current server time as a Unix-seconds integer (UDF `/time`). Free.