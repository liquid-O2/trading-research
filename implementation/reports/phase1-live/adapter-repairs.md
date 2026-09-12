# Adapter repairs and historical format recovery

The adapters now recognize the acquired timestamp and date encodings, preserve the difference between observation time and publication time, and expose bounded trade, best-bid/ask and time-bar views from the canonical NQ MBP-1 archive. All derived outputs are outside `/workspace/data`; the acquired files remain unchanged.

**Current study scope:** NQ is the primary traded instrument and the study begins in 2020. The archive-wide gaps below are not all study blockers: pre-2020 RTY files are outside scope, and ES MBP-1 is optional unless a selected rule needs ES quote/liquidity evidence. ES trades and OHLCV support the selected peer price/profile context. Of the recovered minute keys, 12,420 fall within the active sample; 32 earlier keys are outside it. See the [active data scope](/workspace/planning/phase-1-live/DATA_SCOPE.md) and the [successful FRED vintage check](/workspace/implementation/reports/phase1-live/macro-source-check/README.md).

## What changed

- Arrow timestamp statistics use their actual unit and raw integer values, preserving nanosecond precision. Contract definitions and roll metadata have separate temporal roles. The current roll segment remains open-ended instead of stopping at the last closed contract's end.
- CSV preambles, corroborated CFTC YYMMDD dates, BLS reference months, FOMC meeting date ranges and nested FRED observation responses are parsed. The five SHFE copper minute files use the Asia/Shanghai convention documented in their acquisition manifest; unrelated naive timestamps still require evidence of their time zone.
- Observation dates, scheduled dates, reference periods, publication times and vintages remain separate. Normalized event-calendar clocks are schedule evidence, including when a source column is named `event_ts_utc`; future scheduled dates do not extend observed market history. A date-only record does not acquire an invented intraday release time. Provenance files are identified as provenance.
- Coverage based only on observed extrema is labeled `observed_bounds_only`. It is no longer presented as a demonstrated incomplete historical window. Actual missing or empty files remain explicit.
- MBP-1 views use disjoint monthly/weekly ownership, physical row references, native contract IDs and `T` executions only. Genuine identical events remain separate. Differing prices at equal timestamps have unresolved open/close order unless the source provides a sequence.

The [runner documentation](/workspace/implementation/src/trading_research/research/method_pack/README.md) contains the export and recovery commands. The [before](/workspace/implementation/reports/phase1-live/adapter-before.json) and [after](/workspace/implementation/reports/phase1-live/adapter-after.json) inventories retain the exact diagnostic counts.

## NQ coverage and recovered formats

Every NQ monthly MBP-1 label from January 2020 through September 2026 is present and non-empty: 81 monthly files, plus 61 overlapping weekly files. The exact observed event bounds are **2020-01-01 23:00:00 UTC through 2026-09-03 06:09:59.901114377 UTC**. September is an observed partial endpoint, not a claim of data through the end of that month.

No missing NQ MBP-1 month was found. All 1,712 minute-bar-observed sessions inside the MBP-1 bounds have MBP-1 row-group endpoint evidence. No gap between canonical row-group envelopes contains a complete existing minute bar. This audit did not scan every event for internal continuity; it does not certify a gap-free tape.

| Format | Incomplete standalone window | Result |
|---|---|---|
| Native one-minute bars | 12,452 `(minute, native instrument)` keys are present in native one-second bars but absent from native one-minute bars | All 12,452 recovered from native seconds, with zero unresolved keys and no existing minute key overwritten |
| Standalone trades | Earlier than 2021-09-01 18:00:00.030617317 UTC, within the available MBP-1 history; also later than 2026-09-02 17:59:59.376719279 UTC | The MBP-1 adapter exposes `T` executions for requested windows; the earlier demonstration verifies the export without materializing a duplicate multi-year archive |
| Latest one-minute bars | Native seconds and minutes both end at 2026-09-02 15:20 UTC, exclusive | 829 non-empty event-time minute bars derived from MBP-1 through 2026-09-03 06:09 UTC, exclusive; the final unfinished minute is excluded |

The missing minute keys include nine whole 18:00–17:00 ET Globex sessions, named by trade date: **2025-06-10; 2026-06-02, 06-03, 06-04; 2026-07-06, 07-07, 07-08; 2026-08-03, 08-04**. The remaining 32 isolated minute starts fall between 2010-09-24 and 2015-08-07. They are resolution discrepancies, including closure-adjacent observations, rather than an assertion of 32 lost market sessions. The [exact missing-key manifest](/workspace/implementation/reports/phase1-live/coverage-audit/missing-one-minute-keys.json) lists every key.

Use existing native minute bars first, then the recovered missing keys. The MBP-1 tail uses a distinct event-time convention. Keep its provenance when combining views.

| Derived artifact | Evidence |
|---|---|
| Recovered native minute keys | [Manifest](/workspace/implementation/reports/phase1-live/derived-views/nq-minutes-37uhc_wa/manifest.json) · [12,452 rows](/workspace/implementation/reports/phase1-live/derived-views/nq-minutes-37uhc_wa/ohlcv-1m.jsonl) |
| Later MBP-1 minute bars | [Manifest](/workspace/implementation/reports/phase1-live/derived-views/mbp1-9_5xkllu/manifest.json) · [829 rows](/workspace/implementation/reports/phase1-live/derived-views/mbp1-9_5xkllu/ohlcv-1m.jsonl) |
| Earlier MBP-1 export demonstration | [Manifest](/workspace/implementation/reports/phase1-live/derived-views/mbp1-o741r2ic/manifest.json) · [Native minute comparison](/workspace/implementation/reports/phase1-live/derived-views/mbp1-o741r2ic/native-bar-comparison.json) · [Native second comparison](/workspace/implementation/reports/phase1-live/derived-views/mbp1-o741r2ic/native-second-comparison.json) |

The five-minute 2020 demonstration exports 9,537 trades and 107,067 top-of-book observations. All 25 minute OHLCV fields match the existing native minute bars. At one-second resolution, 1,474 fields match, 19 open/close fields remain unresolved because of timestamp ties, and 7 fields differ. The acquired MBP-1 projection lacks receive timestamps and exchange sequence; Databento's native OHLCV uses receive-time bins. Event-time views therefore cannot be promised identical to native vendor bars. See the [provider's schema documentation](https://databento.com/docs/schemas-and-data-formats).

MBP-1 can supply recorded depth-one state and trade actions. It cannot recreate missing deeper book levels, individual order IDs, receive timestamps or source-specific range-bar settings.

## Other archive acquisition limits and their scope

- **ES MBP-1 — optional for the current NQ study:** missing November 2020, January 2021–June 2023, and September 2024 through the September 2026 archive endpoint. The acquisition catalog marks this dataset partial and paused. It is required only by a selected ES quote/liquidity rule.
- **RTY definitions — pre-2020 gap outside the study window:** the retained files begin in 2019; definitions for the listed 2017–2018 period are absent after vendor read timeouts. Empty RTY minute/statistics files from 2010–2016 precede this CME listing. CME's [launch announcement](https://www.cmegroup.com/media-room/press-releases/2017/7/11/cme_group_announcesfirsttradesafterthereturnoftherussell2000inde.html) places the first trade date at July 10, 2017; those empty earlier years are not lost RTY sessions.
- **SHFE copper intraday context:** the acquisition retains capped recent samples of 1,023 bars per resolution. Their earliest dates range from January 28, 2026 for 60-minute bars to August 10, 2026 for one-minute bars; the samples end August 12. Fixing the date parser does not create a longer history.
- **Macro release availability — backfill added after this adapter report:** the identified 20-series FRED collection now has 37,003 vintage records, including initial values and revisions, plus 160 individually verified BLS publication dates. Exact intraday timing for revisions/other series and observed feed arrival remain separate evidence requirements. Macro inputs are required only by the selected branch. See the [backfill report](/workspace/implementation/reports/phase1-live/macro-backfill/README.md).

The [full coverage audit](/workspace/implementation/reports/phase1-live/coverage-audit/README.md) provides exact UTC intervals, partition evidence, recovery hashes and a reproducible audit command. Reference and superseded option datasets are outside that compact futures overview and remain inventoried in the method reports.

## Verification

**201 tests and two subtests passed.** All 166 object recipes passed 1,316 fixture/mutation checks. All 12 public method-pass commands exited 0, and all 96 declared report artifacts passed their hash and count checks. Their reports share implementation content hash `2cab034db2917ee91fe1e35d3256b71efcce07a688cc9c1a0fc51c3073f05f32`.

The JJ-TBR, SIRES and STOIC-DATA inventories have zero remaining format-related temporal failures in populated observation files. The 14 residual missing-statistic/date-bound entries in the futures inventories are the empty RTY 2010–2016 minute/statistics partitions described above. Missing publication times and vintages remain separate source limitations.

The [verification index](/workspace/implementation/reports/phase1-live/methods/index.md) records the final tests, public command exits, implementation hash and report checks. Historical method cohorts remain empty where FORMULAS requires unpublished source selectors or a supplied episode manifest. Those procedure holes are separate from the adapter repairs and recoverable data-format gaps.
