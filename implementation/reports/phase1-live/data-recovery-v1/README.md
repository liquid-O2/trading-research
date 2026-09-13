# Three-priority data recovery

The three requested investigations are complete at the available-data level. **780 missing NQU6 minute bars were recovered from owned one-second bars**, completing the August 2026 prior-month RTH reference for the September 1 GB-FAIL job. The tape substitution did not repair the clock discrepancies, and the overnight census found no one-second replacements. Remaining external-data and historical-calendar requirements are recorded as exact requests; they have not been acquired or certified.

Phase 1 remains complete. Its accepted v1.0.2 results, registry, weekday policy, split, raw files and implementation are unchanged. This is an input recovery and evidence audit, **not a new outcome replay**. The recovered reference does not add an opportunity, pass, source-method verdict or return to the accepted results.

- [Summary and counts](SUMMARY.json)
- [Four-window tape reconciliation](TAPE_RECONCILIATION.json)
- [Exhaustive bar census and every consumer/window](BAR_CENSUS.json)
- [Prior-reference classification](PRIOR_REFERENCE_CLASSIFICATION.json) and [calendar evidence](calendar_evidence.json)
- [Recovered August reference and input identity](RECOVERED_AUGUST_REFERENCE.json)
- [Exact remaining input requests](REMAINING_INPUT_REQUESTS.json)
- [Verification receipt](VERIFICATION.json) and [PHASE/audit tables](PHASE_AND_AUDIT_TABLES.md)

## 1. Tape reconciliation: same executions, incompatible available clocks

All four requested windows were read by exact native instrument ID, preserving physical rows, duplicate multiplicities, prices, sizes, aggressor sides and flags. Whole-file hashes and physical-row membership digests are retained. The owned MBP-1 `action=T` records and standalone trades contain the **same 946,027 execution tuples**. Both are transformations of the same underlying feed, so their agreement is not an independent exchange completeness certificate.

| Evaluation date | Input window | Execution rows in each schema | Mismatched minutes against native 1m | Aggregated 1s vs 1m mismatches |
| --- | --- | ---: | ---: | ---: |
| 2022-01-03 | Current RTH | 256,947 | 2 | 0 |
| 2022-01-03 | 2021-12-31 prior RTH | 190,340 | 1 | 0 |
| 2026-09-01 | Current RTH | 271,795 | 2 | 0 |
| 2026-09-01 | 2026-08-31 prior RTH | 226,945 | 5 | 0 |

Local timestamp documentation identifies the retained trade `t` as event time. Databento defines OHLCV buckets using receive time. The local trade and MBP projections omit `ts_recv` and exchange sequence, although the vendor's trade schema defines those fields. This documented clock mismatch is consistent with the discrepancies; the missing timestamps prevent proving which individual executions crossed a receive-time boundary. [Databento OHLCV schema](https://databento.com/docs/schemas-and-data-formats/ohlcv), [trade schema](https://databento.com/docs/schemas-and-data-formats/trades).

The fixed boundary inspection found, for example, one execution of size 1 just **13,967 ns before 14:34 UTC on 2022-01-03**, where the adjacent volume differences are +1/-1. On 2026-09-01, executions of sizes 2 and 1 occur **67,711 and 47,737 ns before 17:33 UTC**, where the differences are +3/-3. These are candidate explanations, not reconstructed receive timestamps. The receipt includes a fixed 25 ms halo and exact physical row IDs; no timestamp was shifted and adjacent volumes were not canceled to manufacture agreement.

**Disposition:** MBP substitution supplies zero repairs. Four exact native execution requests require receive time, event time, sequence, flags, aggressor and a one-second boundary halo. Full same-clock reconciliation is still unavailable, so the eight affected missing tape rule/date searches and two Keani unknown openings retain their accepted status.

## 2. Prior references: contract checks, calendar findings and a real recovery

The census expands all missing dates from the four affected bar branches, deduplicating their shared inputs. It covers **315 missing rule/date jobs and 1,294 unique date/instrument RTH windows**. All 1,294 target instruments are active at the required window start according to the local native definition map. Contract activation does not mean a front-continuous archive contains that contract's earlier history.

| Exclusive input classification | Unique date/instrument windows |
| --- | ---: |
| Different front contract has native bars | 560 |
| Outside target contract's front segment; no bars in the window | 147 |
| Entirely before local archive | 28 |
| Straddles archive start | 2 |
| No same-contract bars; calendar/feed cause unresolved | 464 |
| Partial same-contract minutes; calendar/sparse/feed cause unresolved | 89 |
| RTH closure verified from CME notices | 2 |
| Recovered from owned same-contract one-second bars | 2 |
| **Total** | **1,294** |

The **707 windows outside the target's front segment** require outright-contract history or an explicitly different reference definition. Substituting whichever contract was front that day would change the input identity. For example, the October 2010 job's September reference requests NQZ0 while earlier September bars belong to NQU0. The requested target was already active; the continuous roll, rather than activation, limits this archive's coverage.

The archive begins on September 6, 2010 at 15:20 UTC. The 30 windows before or crossing that boundary cannot be recovered from local earlier bars. Full empty windows also occur on ordinary-looking dates such as October 1, 2010; they must not all be called holidays.

### Historical calendar verification

CME's notices establish an 08:15 Chicago halt for US equity-index futures on **October 29 and 30, 2012**, covering the entire frozen 09:30–16:00 New York RTH window. Both dates had overnight trading, so an all-day closure label would be wrong. These two missing dates share the November 2012 prior-month job. [October 29 notice](https://www.cmegroup.com/media-room/press-releases/2012/10/28/media_alert_cme_grouptocloseusequityindexfuturesandoptionsonfutu.html), [October 30 notice](https://www.cmegroup.com/tools-information/lookups/advisories/clearing/Chadv12-464.html).

The classification file flags 156 other possible holiday/early-close windows for investigation; **these are computed date flags, not certified NQ session schedules**. The other 1,136 unflagged windows are not thereby certified normal sessions. Calendar flags overlap the contract/archive categories above and must not be added to those counts.

For **January 2, 2023**, CME confirms the observed New Year's holiday and clearing changes, while Nasdaq confirms the underlying cash-market closure. Those sources do not supply exact historical NQ Globex matching hours. The requested prior profile therefore remains unverified. Historical CME Globex links for July 4, 2011 and Good Friday 2012 returned 404; the current calendar page describes current-year schedules. Retrieval limits and source scope are recorded instead of inventing a complete historical calendar. [CME advisory](https://www.cmegroup.com/tools-information/holiday-calendar/files/2023-new-years-advisory.pdf), [Nasdaq notice](https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2022-106), [current CME calendar](https://www.cmegroup.com/trading-hours.html).

The evidence file specifies the requirements for a separately versioned trading-session policy. No rule was changed from “all prior calendar weekdays” to “previous trading session,” and no closed minute was filled with a price.

### Recovered August 2026 input

The two missing dates are **August 3 and 4, 2026, NQU6 / instrument 42004177**, each with all 390 RTH minute slots present in owned native one-second bars. First open, maximum high, minimum low, last close and summed volume produce a **780-row derived minute file**. The same aggregation matches **all 7,410 existing August RTH minute bars exactly** across OHLCV, with no timestamp duplicates or off-tick prices.

The complete reference now has all **8,190 minutes across 21 weekdays**, high **30,287.50**, low **28,313.50**, and volume **7,706,764**, known at the August 31 RTH close. Existing one-minute rows are retained; only absent slots are supplied by the derived file. Sparse seconds are not fabricated.

The input stays on disk under ignored data:

`/workspace/data/derived/phase1-data-recovery-v1/NQU6-2026-08-03_04-RTH-1m-from-1s.parquet`

Its hash, source rows, per-minute membership digests and reference receipt are recorded. This resolves the missing *input grid* for the September 1 prior-month job. It is not a complete execution-feed certificate or a trade-volume profile, and it has not been bound into an outcome replay. Any such replay must explicitly use this new input identity and retain exposure and changed-denominator records.

## 3. Overnight and VWAP-prefix census

All **399 missing overnight/reference rule/date jobs**, the **three partial Asia/TDO jobs**, and **eight observed GB-VWAP unknown prefixes** were examined. The 402 job records share 398 distinct diagnostic windows with **10,393 unique missing instrument/minute slots**. The unknown-outcome prefixes were checked separately and overlap some of those dependencies. Counts remain dependent; a missing slot is not a missing opportunity count.

**None of these missing slots has a same-instrument row in the local one-second files.** All 102 SIRES failures already have a hole in the initial 18:00-to-09:30 prefix. Of 98 audited Asia/TDO midnight inputs, 12 lack their one-minute opening input. The eight GB-VWAP unknown prefixes contain 2, 12, 7, 1, 1, 120, 1 and 1 absent minutes respectively.

For action searches that stop at an absent minute, the receipt distinguishes the first absent minute from later diagnostic gaps; later gaps are not counted as further selector failures. Three Asia jobs retain their already observed subset. The four small adjacent NYAM/previous-hour reference windows were also checked: four unique absent minutes, zero one-second repairs.

Databento does not print a bar for an interval without trades. Thus absence in both bar resolutions can reflect no executions, a scheduled halt, or lost source data; it does not prove any one cause. The frozen dense-minute check deliberately leaves these unresolved. Replacing an absent bar with a flat zero-volume bar would assert evidence the archive does not contain. [Vendor no-trade convention](https://databento.com/docs/schemas-and-data-formats/ohlcv).

**Disposition:** 320 nonempty overnight/reference/prefix requests retain exact instruments, full windows, missing ranges and consumers. They require native event coverage and sequence/gap or session-status evidence before classifying absent minutes. The 120-minute July 2020 prefix hole is explicitly retained; it is not treated as normal sparse activity.


## Follow-up correction: event time and the 2020 MBP-1 archive

The tape implementation **already buckets executions on event time** (`empirical_tape.py`, line 480). Its validation then requires exact minute OHLCV agreement against downloaded vendor bars (lines 546–571), whose documented buckets use receive time. That mixes clocks. A mismatch under this check is not sufficient evidence of lost executions. The appropriate follow-on design is to build candles and execution measures consistently on event time and make the vendor-bar comparison a diagnostic that accounts for its different clock. Receive timestamps are needed for exact reproduction of the vendor buckets, not as a prerequisite for event-time research. This correction documents the implementation issue; it does not claim that the production check or accepted replay has been changed.

The earlier explanation based only on the standalone-trade archive was too narrow. Local NQ bars begin in September 2010, **MBP-1 begins January 1, 2020 at 23:00 UTC**, and the standalone-trade records begin September 1, 2021 at 18:00 UTC. The catalog's standalone-trade `expected_start=2020-01` and “2020 onward” scope do not agree with its actual observed first record. MBP-1 includes execution records, so it is an available source for event-time reconstruction from 2020. Only execution actions contribute traded OHLCV and delta; quote changes do not. [Vendor MBP-1 schema](https://databento.com/docs/schemas-and-data-formats/mbp-1), [OHLCV clock convention](https://databento.com/docs/schemas-and-data-formats/ohlcv).

The [read-only MBP-1 follow-up](OVERNIGHT_MBP_FOLLOWUP.json) checks every missing overnight/prefix slot against owned file coverage. Of 10,393 unique missing slots, **10,270 predate MBP-1 and 123 overlap it**. Actual records in those 123 slots contain no executions:

| UTC interval | Missing minutes | Observed book records | Interpretation |
| --- | ---: | ---: | --- |
| 2020-01-02 04:38–04:39 | 1 | 21 | Quiet-minute candidate: book activity with no recorded trades |
| 2021-11-01 04:33–04:34 | 1 | 52 | Quiet-minute candidate: book activity with no recorded trades |
| 2023-07-04 22:36–22:37 | 1 | 10 | Quiet-minute candidate: book activity with no recorded trades |
| 2020-06-30 22:00–2020-07-01 00:00 | 120 | 1 | Coverage cause unresolved; do not treat the whole interval as proven quiet |

The single record in the two-hour block also appears in an overlapping monthly file. File diagnostics remain separate, and that duplicate is not counted as additional activity. The three isolated minutes support the no-trade explanation but do not independently certify an uninterrupted exchange feed. No minute was filled, no quote was substituted for an execution, and the remaining input requests are investigation scopes rather than a requirement to purchase data already held locally.

**Raw-data preservation:** existing raw files must remain unchanged. Any future event-time reconstruction belongs in a separate derived dataset with source hashes, physical membership and its own versioned input identity. This follow-up reads raw files and verifies their hashes before and after inspection.

Reproduce this additional check before running `verify_recovery.py`:

```bash
python implementation/reports/phase1-live/data-recovery-v1/audit_overnight_mbp.py
```

## Verification and reproduction

The verification script rehashes every audited source, checks native file byte/row counts against the canonical manifest, reconciles all 1,294 prior inputs directly to accepted checkpoints, validates all 102 initial SIRES failures and eight unknown prefixes, checks tape equality and bar resampling, and confirms the accepted implementation and splits are unchanged. These are data-audit checks; no new production test-suite run or strategy replay is claimed.

Run from `/workspace` with the existing Python, NumPy, PyArrow and python-dateutil environment:

```bash
python implementation/reports/phase1-live/data-recovery-v1/audit_tape.py
python implementation/reports/phase1-live/data-recovery-v1/audit_bars.py
python implementation/reports/phase1-live/data-recovery-v1/recover_august.py
python implementation/reports/phase1-live/data-recovery-v1/build_recovery_report.py
python implementation/reports/phase1-live/data-recovery-v1/verify_recovery.py
```

The scripts reproduce local computations. `calendar_evidence.json` contains manually reviewed external-source findings; running the scripts does not repeat that review. The remaining request file contains four receive-clock tape windows, 1,290 prior-reference windows and 320 overnight/prefix windows. Calendar filtering must precede acquisition; these are unsent data requests, not a purchase or a promise that closed-session prices exist.
