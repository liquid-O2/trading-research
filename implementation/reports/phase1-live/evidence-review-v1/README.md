# Follow-on branch evidence review

Phase 1 is complete. This review examines the accepted evidence and orders the next data investigations; it is not an additional Phase 1 completion gate. The Phase 1 wiki reconciliation was committed and pushed to `main` at `43beed9a0146d5a99a90d56945e61e4d799e17ab` before this review.

The best next recovery candidates are the small tape discrepancies on **2022-01-03 and 2026-09-01**, followed by calendar and native-contract checks for prior references. Broader overnight coverage comes after those bounded checks. No local repair was certified by this review, and the replay was not expanded.

The review covers all **50 registered branches**, **eight separate observation units**, **165 completed job searches**, and **36 visually inspected charts** spanning every observed branch/verdict pair. All 50 existing chart files were checked against their recorded hashes. The accepted run is v1.0.2, manifest `d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247`.

- [Branch matrix: all 50 branches and eight observation units](BRANCH_MATRIX.md)
- [Chart findings and individual examples](CHART_REVIEW.md)
- [Exact counts, per-date gaps and unknown records](DENOMINATOR_AUDIT.json)
- [Bounded local recovery probes](RECOVERY_PROBES.json)
- [PHASE and audit tables](PHASE_AND_AUDIT_TABLES.md)
- [Summary](REVIEW_SUMMARY.json), [source identities](SOURCE_IDENTITIES.json) and [validation receipt](VERIFICATION.json)

## What the denominators support

The frozen sample comprises 161 monthly bar jobs and four annual standalone-trade jobs. All 165 were searched; remaining work in that declared run is zero. The sample is sparse, retrospective and already exposed, not every historical session or an untouched test set. In particular, the split records prior-inspection exclusions across 2024–2026; absent years must not be read as zero-event years. The authoritative selection remains in the [run manifest and linked split files](../empirical/RUN_MANIFEST.json).

Across the 19 supported comparisons, the ledger contains 2,452 observed records: 1,000 pass, 1,412 fail and 40 unknown; resolved n is 2,412. These are additive bookkeeping counts across different questions and dependent populations. They do not form a pooled strategy success rate. All source-method verdicts remain unknown, and actual selections, attempts, orders, fills and returns remain unavailable.

There are 2,274 rule/date search jobs: **1,535 complete**, **six complete with population holes**, and **733 missing required inputs**. These are different units from the 165 cohort jobs and the 2,452 observed opportunities. The top-level 157 missing cohort jobs indicate at least one missing requirement in those jobs; they do not mean 157 unscanned jobs. Likewise, an observed unknown outcome is different from an unknown number of opportunities in a missing search.

| Denominator finding | Evidence and implication |
| --- | --- |
| 790 frozen reporting groups | 423 have complete populations and 367 have incomplete populations. All 367 suppress full-population rates and bounds. Of those, 207 have unavailable counts with no observed records; 160 retain counts from their observed subset, without implying complete opportunity coverage. |
| Complete groups still differ | 410 have an identified resolved rate, nine have no candidates, and four Keani opening groups contain only unknown outcomes. Empty and all-unknown groups do not receive an invented rate. |
| Previous-hour dominates record count | Its 1,124 records use repeated hourly references, unlike once-per-opening or once-per-session populations. Three dates retain incomplete reference populations. |
| MSS/FVG is conditional | All 99 children link one-to-one to the 99 passing NYAM parents, with child availability exactly at parent completion. The 52 passing children answer a conditional refinement question, not a fresh denominator of initial sweeps. |
| Keani has an observed population | All four clock-based openings exist, but their prior profiles are unverified: N=4, n=0, u=4. The frozen status `measured` does not mean the above-value classification is resolved. |
| Refill has one legitimate empty search | On 2023-01-03 the verified current-session tape contains 322,181 executions and produces zero qualifying zones/returns under the frozen definition. The other three tape dates are missing-input searches. |
| 31 dispositions and eight extra units | Counts remain unavailable. Source definitions, actual selected-order/process records and observed state transitions cannot be reconstructed by adding future price history. |

The published bounds `[p/N, (p+u)/N]` describe possible outcome fractions for already observed records when outcomes are unknown. They are not statistical confidence intervals and do not bound the number of opportunities lost to incomplete searches. No branch or family ranking is inferred from them.

## Recovery priorities

Priorities use the scope of the gap, shared dependencies, local evidence and investigation cost. They do not use observed pass fractions. Counts below describe affected **existing search jobs or observations**, not a promised number of new opportunities.

| Order | Bounded investigation | Existing evidence and affected scope | Evidence needed before a follow-on replay |
| --- | --- | --- | --- |
| 1 | Reconcile the 2022 and 2026 tape windows and their prior profiles | Current-session tape has two mismatched minutes on each date; prior profiles have one and five respectively. Owned MBP-1 files overlap all four windows. These dates account for eight missing tape rule/date jobs across three Saint branches and Refill, plus two Keani unknown openings. | Inspect exact-instrument executions around each mismatch and reconcile event times, OHLC, volume and aggressor attribution. Establish complete current/prior windows using native source provenance. Retained adjacent-minute discrepancies must not be canceled merely because net daily volume agrees. |
| 2 | Classify prior-reference gaps by calendar, native-contract coverage and true missing data | 315 missing bar rule/date jobs: GB prior day 54, prior week 69, prior month 138, and Saint continuation 54. Prior-day inputs are shared. The 2023-01-03 tape jobs also request an unavailable 2023-01-02 prior profile. | Verify historical product/session calendars and contract identity. Separate scheduled closure, partial session, roll boundary, absent same-contract data and unverified source. Obtain missing same-contract inputs where possible. A change from the frozen weekday policy to a trading-session policy changes the reference definition and requires a separately recorded version. |
| 3 | Audit the overnight/reference prefix before seeking broader data | 399 missing bar rule/date jobs: the three Jumbo branches share 37 missing dates each; Asia/TDO has 95, GB-VWAP 91 and SIRES 102. There are also eight observed GB-VWAP unknowns from unavailable boundary snapshots and three partially observed Asia action populations. | Establish exact complete reference/action windows, the midnight TDO input, and the full pre-bar VWAP prefix. Distinguish no-trade minutes and scheduled closures from lost data using authoritative event coverage. Local one-second bars are not a demonstrated repair for the sampled missing slots. |
| 4 | Resolve the small NYAM/prior-hour defects | NYAM and its MSS/FVG child each miss 2011-04-04 and 2014-05-01: four missing rule/date jobs sharing two one-minute reference gaps. Previous-hour has three partial-reference dates: 2011-02-07, 2011-04-04 and 2014-05-01. | Seek same-contract evidence for the exact minute windows. Both sampled NYAM gaps are also absent in local one-second bars. A zero-volume synthetic bar is not evidence of a complete native interval. |
| 5 | Investigate the broader 2021 tape gap, then expand only from an explicit new scope | The 2021-09-01 current tape has 272 mismatched minutes and its prior profile has no standalone tape. Owned MBP-1 metadata overlaps both windows. The 2023 current tape is already verified; its prior-profile question belongs to the calendar investigation above. | Confirm actual event and instrument coverage before reconstructing views. Preserve the legitimate 2023 Refill zero. Do not lower the frozen size/time/distance thresholds to create candidates. |

The four disjoint missing-job buckets reconcile exactly: **399 overnight/reference + 315 prior-reference + four NYAM/child + 15 tape = 733**. The six partial jobs are separate: three previous-hour and three Asia/TDO. Several branches share the same missing underlying interval, so these counts must not be treated as independent data defects.

The 2023-01-02 example is a calendar flag, not proof that more bars must exist: CME identifies that date as the observed New Year's holiday in its [2023 New Year's clearing advisory](https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-advisory.pdf). That advisory does not by itself establish the precise historical NQ session schedule. Product-specific trading hours still need to be verified before changing the prior-session reference.

### What the local probes actually established

The probes read timestamps and native instrument IDs from owned one-minute and one-second files. They compare occupied minute slots; they do not certify complete event streams, impute prices or rerun a rule. File hashes and query windows are retained in [RECOVERY_PROBES.json](RECOVERY_PROBES.json).

| Sampled window | Missing minute slots | Those slots with local one-second rows | Interpretation |
| --- | ---: | ---: | --- |
| 2010-09-07 Jumbo 06:00–09:00 reference | 3 | 0 | Finer bars do not supply these missing slots. |
| 2011-04-04 NYAM reference | 1 | 0 | Same absence in both bar resolutions. |
| 2014-05-01 NYAM reference | 1 | 0 | Same absence in both bar resolutions. |
| Prior RTH on 2023-01-02, requested by 2023-01-03 | 390 | 0 | Owned-file inventory has no overlapping one-minute/one-second events; investigate the calendar/reference policy. |
| 2016-02-01 first unknown GB-VWAP prefix | 2 | 0 | More chart context does not replace the unavailable prefix. |

For MBP-1, this review checked inventory time overlap only. The inventory did not hash those large raw files or certify same-instrument event completeness. Optional feed availability in a manifest is not evidence that those feeds were admitted to the accepted standalone-trade experiment. There is no MNQ coverage claim or transfer from NQ.

## The 40 unknown outcomes are not one recovery queue

| Cause | Observed records | Treatment |
| --- | ---: | --- |
| Next aligned close falls after frozen expiry | 18: Judas 9, previous-hour 6, extension 1, prior-day 1, NYAM 1 | Additional later prices cannot resolve these under the same rule. Changing expiry changes the question. |
| Both SIRES bands touched by one trigger bar | 10 records from six bars | Four bars contribute both sides and two contribute one remaining side. The frozen rule preserves ambiguity. Finer chronology would require an explicit alternative rule before relabeling. |
| GB-VWAP boundary snapshot unavailable | 8 | Potential data/coverage recovery: establish the complete required pre-bar prefix. The one sampled prefix was not repaired by local one-second availability. |
| Keani prior value profile unverified | 4 | Potential profile/calendar recovery: verify the correct same-contract prior RTH trade-volume profile. Current A-period prices cannot fill this gap. |

Only the last 12 are directly missing-context outcomes. The 733 missing searches can hide additional, presently uncounted opportunities and must remain separate from this outcome ledger.

## Chart conclusions

The visual sample covers every observed rule/verdict combination: 36 charts for 15 branches. The three Saint tape branches and Refill have no observed opportunities to chart. The full [chart ledger](CHART_REVIEW.md) records what is visible and which exact predicates require the underlying record.

Three examples are particularly useful:

- [GB-VWAP pass](../empirical/charts/opp-7d27a1b45154834f4a09e80a.png): the initial long breakout closes at 7011.0, while the later touch bar closes at 6988.0 and straddles its pre-bar VWAP near 6989.133. This passes the declared touch question without establishing a profitable long.
- [Asia/TDO fail](../empirical/charts/opp-c0790b23f518a4692ce463e4.png): the endpoint closes at 4188.75, above the Asia low of 4186.75 but below TDO at 4197.0. The chart does not draw TDO, so the record is necessary to understand the failure.
- [Judas expiry unknown](../empirical/charts/opp-306d004a203aba4455c09b7a.png): later visible prices do not make the next aligned close admissible before the frozen 09:50 expiry.

For future diagnostics, add the omitted TDO and dynamic VWAP boundaries, show the actual 2-minute MSS/FVG candles, and provide a local-price inset for wide prior-month references. Existing charts remain unchanged. No sampled overview is treated as proof of the full author method or an actual trade.

## Verification and scope boundary

`build_review.py` recomputes counts from the accepted checkpoints and records, checks the null/suppression rules, verifies all 165 checkpoint/artifact pairs and 50 chart/record identities, confirms the 99 parent-child links, and checks accepted implementation-file hashes. The separate presence probe reads local native files without altering them. The current Phase 1 test-suite evidence remains in [wiki reconciliation](../wiki-reconciliation/README.md); this report-only work does not represent a new suite or replay run.

To reproduce the derived review artifacts from `/workspace`:

```bash
python implementation/reports/phase1-live/evidence-review-v1/probe_recovery.py
python implementation/reports/phase1-live/evidence-review-v1/build_review.py
```

`review_notes.json` contains the manual chart observations; running a script does not repeat visual inspection. The frozen registry, split, accepted artifacts, implementation, wiki and raw data were not changed during this review. Any subsequent recovered-input run should retain these accepted results and record its input and definition changes explicitly.
