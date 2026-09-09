# E0 minimum prerequisites and opening evidence

Recorded 2026-09-06 after governing-document closure and the single consolidated
implementation review. Exact E0 has not run. No historical cohort has been
frozen for fitting or economic evaluation. This is a dependency and evidence
review; it does not classify every supplied market session as invalid.

## Contract-selection dependency

The supplied catalog explicitly describes the NQ outright definition, bars,
statistics, trades and MBP acquisitions as `NQ.c.0`. Databento defines `c` as
calendar expiry rank and `v` as preceding-day volume rank. A continuous symbol
maps to an actual, unadjusted contract; it does not expose the simultaneous
parent outright tapes. The separately acquired `NQ.OPT` chain contains option
instruments and cannot supply missing outright competitor volumes.
[Databento symbology](https://databento.com/docs/standards-and-conventions/symbology)

The ten-partition definition audit decoded all 2,579 rows from NQ and ES
2021–2025. Each yearly NQ file contains five distinct instruments appearing
over that year. This establishes a sequence of observed contracts, not the
set listed at every historical cut. CME notice SER-8975 describes five
consecutive quarterly NQ futures before its May 23, 2022 expansion, adding
four December contract months. A dated listing rule still cannot substitute
for contract definitions and observed prior-session volumes.
[CME SER-8975](https://www.cmegroup.com/notices/ser/2022/04/SER-8975.pdf)

Exact E0 requires selection among eligible unexpired outright contracts using
the preceding completed session's volume, with earlier expiry then canonical
ID as tie-breakers. Existing selection code refuses an absent eligible
competitor and preserves the declared universe scope. The cohort gate refuses
to replace `complete_outright_universe` with acquired-cohort evidence.

Required dependency: provide or locate a historically available complete
parent outright definition/listing set, preceding completed-session volume
for its eligible contracts, and MBP coverage for the selected contract's
required windows. Alternatively, a demonstrably equivalent acquired mapping
would need its own historical causal/coverage proof. Present catalog and
definition evidence do not establish equivalence. No acquisition, paid API
request or modification of original data was performed.

The complete parent requirement remains part of exact E0. A separately
registered study of `NQ.c.0` is an eligible diagnostic research branch once
its own minimum gates pass; its results cannot be labeled exact E0 or used
to erase the volume-selection comparison.

## Minimum gate matrix

| Gate | Existing evidence | Remaining prerequisite |
|---|---|---|
| Raw definition | All fields and all rows in ten selected NQ/ES yearly partitions; literal outright adapter and missing/unsupported tests | Per-decision applicable definitions and joins through the selected contract; definition deletion/retirement support for cohorts that need it |
| Product terms | Explicit dated NQ 20 USD/point reference; raw definitions supply the 0.25 point tick | Frozen actual NQ terms joins; separate dated ES evidence if ES becomes an execution candidate |
| Cash calendar | Dated NYSE holiday releases, publication-time revisions, early closes, DST and 2025 mourning closure | Freeze the relevant cash-day population with exact calendar/timezone versions; calendar dates alone are not data admission |
| Venue boundary | Synthetic independent boundary timer and cash/venue separation fixtures | Historical CME schedule/status and any applicable firm/platform deadline, with availability and measured safety margin for each admitted date |
| Prior-session volume | Deterministic selection, incomplete-competitor rejection and tie fixtures | Complete compatible preceding-session volumes across the actual eligible parent outright universe |
| Complete outright universe | Catalog confirms acquired continuous scope; actual definition audit is bounded and complete within its selected files | Exact historical parent scope and causal mapping evidence described above |
| Full MBP schema | Full-column decoder; every Parquet physical profile now has fixed-prefix evidence; complete synthetic MBP partition admission and crash tests | Admit exact real partitions/windows and inspect schema/cohort-specific semantics; prefix checks do not certify unread bodies |
| Book recovery | Explicit gap/clear/snapshot state tests, trade-history separation, compact replay parity | Source-supported recovery and trusted quotes over the actual admitted execution intervals; a clean later quote alone is not a recovery certificate |
| Formation 06:00–09:00 NY | Half-open clock/bar fixtures and frozen E0 range object geometry | Complete selected-contract trade observations and causal bar/range reconciliation on actual dates |
| Prior RTH window | Known-time bars, source coordinates and roll/reset rules in reference code | Complete prior cash-session observations for the applicable raw contract; no fabricated roll translation |
| Entry and label window | Ordered paths, unknown-order ambiguity, fixed 15-minute endpoints, visit reset and no-contact fixtures | Complete actual observations, standing BBO support, execution window and mature labels for every admitted opportunity |

The current CME trading-hours page covers 2026/2027 and explicitly allows
schedule changes. It cannot certify the 2022–2025 dates. The older one-page
equity-hours document found during this review lacks a year on the page and
describes a different historical arrangement; it was not imported as a
2022–2025 calendar. Search results for options, micro, sector and dividend
products were not used to certify outright NQ hours.
[CME trading hours](https://www.cmegroup.com/trading-hours.html),
[older equity-hours document](https://www.cmegroup.com/education/files/eq-trading-hours.pdf)

The SER-8975 text was accessible through web extraction. Direct PDF byte
capture returned HTTP 403, and the attempted web screenshot supplied no image
content in this environment. No raw PDF hash or completed visual review is
claimed. That limitation does not turn a listing notice into session evidence.

## Engineering evidence and next eligible work

The 247-method verification and reconstructed code snapshot remain unchanged.
[F02 source/case review](F02_SOURCE_CASES.md) names the actual assertions and
the remaining contract/payoff cases. Other opening service assertions include
separate clocks, no future joins, known-time calendar revisions, persistent
gaps, lossless admission, immutable objects, mature labels and forward folds.
Those tests have not been rerun merely to create this mapping.

Continue the opening original-source and case closure and implement the
collected missing reference/admission work as a batch. Exact E0 data
dependencies remain visible while independent data and deterministic
measurement branches progress. Wider options/native admission remains
required for its own consumers; it is not an artificial prerequisite for
the simpler NQ path. B10 still requires future elapsed observations.
