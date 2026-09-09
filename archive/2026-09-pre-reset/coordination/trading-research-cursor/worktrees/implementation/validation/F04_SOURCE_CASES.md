# F04 availability and scheduler source cases

All 58 assigned/lineage findings have original-passage coverage. The retained report records 28 static source files, six newly inspected original PDF pages, six reused PDF pages, three original conversation excerpts, unchanged inventory evidence and the original image. No Pine source was executed. Cases are expectations, not whole-source or whole-phase completion.

DTM cadence values are proposed comparisons, not mandatory live frequencies. CEX vendor one-for-one equivalence and claimed pulls remain unaudited.
CRL selective updates only on traded/gate-positive examples and forced daily gate zeroing are rejected; retain all matured labels and continuity.
Unshifted final HTF H/L/C under lookahead_on is unavailable at interval start; prior [1] completed values have a different causal release contract.
PIN037 offset default 1 means expression offset-1=0 (current HTF); default lookahead_off still has historical/live confirmation differences.
PIN019 getFVGData includes unoffset current close/high/low at L81-85; cannot publish completed gap before confirmation.
PIN022 manual HTF/auto current timeframe mismatch is not inherited; compute and publication clocks must identify the actual source series.
PIN027 IB close is assigned from first outside-session bar; preserve literal parity separately from last inside close. Same-minute high-first ties are ambiguous.
PIN032 pivot draws at offset origin but becomes confirmed after right bars; FindT price equality is a visual placement, not receipt evidence.
PIN048 lower-timeframe arrays only contain confirmed observed prefixes; a parent-bar array is not available at its bar open, and simultaneous extremes remain ambiguous.
PIN045 volatility multiplier is frozen per anchor from what was available; close-to-close standard deviation differs from source RMS estimator and embedded performance is unverified.
PIN071 _ischange compares OHLC value, omitting equal-valued new bars/lineage. Exact bar identity must drive admission; visual deletes do not delete historical state.
PIN066 daily OI delta is neither signed trade volume nor an intraday holdings observation; receipt/report publication controls its use.
Final body/wick classification in OFM becomes available at bar close. Aggressive liquidity can include marketable limits; the cited bubble thresholds are source candidates.
ALM p11 right edge recovers the weekly balance; do not describe it as a current confirmed lower hold. Narrative claims and screenshots provide no complete event tape.
Provider receipt, local wall display, filename and inventory metadata do not establish actual strategy receipt latency or economic observations.

| Case | Expected behavior | Source clauses |
|---|---|---|
| F04-01 | Availability joins: future OI, revised CPI, stale and conflicting observations | CEX-24, PIN066-02 |
| F04-02 | Derived completion, confirmation and modeled duration are charged once | DTM-A01, OSF-02, OSF-03, PIN081-03 |
| F04-03 | Pivot origin differs from right-bar confirmation and actionable availability | OSF-02, OSF-03, PIN009-02, PIN032-01, PIN071-06 |
| F04-04 | Availability merge has insertion-order and prefix invariance | INV-01, INV-02, INV-03, INV-04, INV-05, INV-06, INV-07, INV-08, INV-09, INV-10, CEX-24 |
| F04-05 | Independent equal-time streams retain ambiguity and within-source order | PIN027-02, PIN048-01, PIN073-02, PIN081-03 |
| F04-06 | Domain watermarks isolate optional feed stalls and asynchronous chains | CEX-24, INV-01, INV-07, PIN066-02 |
| F04-07 | Durable spill, repeatable peek, ack and restart preserve exact envelope identity | INV-01, INV-02, INV-03, INV-04, INV-05, INV-06, INV-07, INV-08, INV-09, INV-10 |
| F04-08 | Record/byte/tie bounds fail closed with retained backpressure evidence | INV-12, DTM-A01 |
| F04-09 | Changed OI fields invalidate exposure without recomputing trade CVD | PIN066-02, CEX-24, DTM-A01 |
| F04-10 | Unchanged numeric value with new source lineage still invalidates forecast | PIN071-02, PIN064-02, PIN045-03 |
| F04-11 | Missing required input blocks only consumers; optional absence is explicit | CEX-24, INV-01, INV-07 |
| F04-12 | Registered FIFO, deadline and cost-aware optional ordering retain choices | DTM-A01, CEX-04, CRL-17 |
| F04-13 | Past measured runtime costs, prefix-safe estimates and percentile telemetry | INV-12, DTM-A01 |
| F04-14 | Queued/slow/late forecasts preserve original cut and endpoint | DTM-A01, CEX-04, PIN081-03 |
| F04-15 | Duplicate dispatch, terminal publication and coalescing preserve identity | DTM-A01, CRL-17 |
| F04-16 | Raw market, timer, account and order integrity remain unconditional | DTM-A01, CRL-17, PIN066-03, PIN077-02 |
| F04-17 | Current HTF final H/L/C is unavailable at start; offset prior values differ | PIN012-02, PIN014-02, PIN019-02, PIN021-01, PIN022-01, PIN022-03, PIN023-01, PIN023-02, PIN035-01, PIN037-01, PIN047-01, PIN058-01, PIN059-01, PIN068-02, PIN071-01, PIN071-02, PIN071-03 |
| F04-18 | Display toggles, drawn origins and screen timestamps cannot select observations | IMG-01, DEN-04, ALM-06, TBR-07, PIN023-02, PIN064-02, PIN071-02 |
| F04-19 | Daily OI changes are delayed reports, not observed intraday traded volume | PIN066-02, CEX-24 |
| F04-20 | Completed ranges, minute aggregates and anchors have separate formation/freeze cuts | VW10-05, OFM-01, PIN027-02, PIN040-02, PIN043-01, PIN045-03, PIN048-01, PIN056-01, PIN059-01, PIN066-03, PIN073-02, PIN077-02, PIN080-01 |
| F04-21 | Inventory/screenshot/provider clocks do not certify live strategy receipts | IMG-01, INV-11, INV-12, VX4-07, DEN-04, ALM-06, OFM-01, TBR-07, CEX-24 |
| F04-22 | Cadence is a candidate; retain every matured label and rejected/untraded opportunity | DTM-A01, CEX-04, CRL-17 |
| F04-23 | Full versus incremental output parity is separate from empirical/economic admission | DTM-A01, CEX-24, PIN045-03, PIN047-01, PIN080-01 |

Executed partial reference status: the first registered combined run passed all 321 methods, including 33 new merge, scheduler and collected-review assertions. Case-specific evidence is retained in `reports/f04-replay-case-coverage.json`. Cases with no executed source-specific assertions remain explicitly empty; no whole case, phase, dataset cohort or economic result is promoted.
