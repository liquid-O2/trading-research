# Acquired data, family populations and availability

Family: **options-data**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[DATA_INVENTORY.md, L1–35,138–264,738–745](../../../sources/documents/inventory/DATA_INVENTORY.md) lists NQ/ES/YM 1m observations from 2010-09 to2026-09-02; RTY actually starts2017-07 despite2010 partition names. NQ 1s starts2010. NQMBP1 observed2020-01-01T23:00 to2026-09-03T06:09:59.901114UTC,11.536billion rows. Separate NQ trades start2021-09, not2020; ES/YM/RTY trades start2020. ES MBP1 is partial. Roll-map extrema end2026-06-19 forNQ/ES/YM; RTY is absent.

[DATA_INVENTORY.md, L295–556,560–737](../../../sources/documents/inventory/DATA_INVENTORY.md) describes options and daily auxiliary scope. QQQ/SPY minute data starts2018; NDX/SPX cash is daily. VIX/VXN/VIX 3M/VVIX and VX curve are daily. Rates/events have some unknown endpoints/releases. [databento_pull_list.md, L1–91](../../../sources/documents/inventory/databento_pull_list.md) does not establish acquisitions. The bundle manifest covers source documents, not all raw-data completeness.

## Computability and faithful reconstruction

Use the longest honest sample for each family. Inventory extrema do not prove complete sessions. Only the minimal later coverage query needed by the slice should inspect real partitions; this planning task does not scan or alter raw data.

Build family eligibility from actual observations, contracts, calendar, schema and knowability. Distinguish source_time, event_time, received_time where available, release_known_at and research_known_at. Stored nanoseconds do not imply nanosecond measurement precision. No all-dataset intersection. No same-day completed volume for a pre-open roll selection.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **family-native sample** plus **matched-overlap comparison**.
- **vendor agreement**, **gap/sequence checks**, **as-of roll map**, **daily-lagged auxiliary** and **explicit proxy** versions.
- Keep acquired/requested/unavailable status on every input; no auto-purchases/pulls.

## Phase 1 outcomes

Eligible/complete/partial/missing sessions, first/last honest observations, warmup, source vintage, roll gaps and comparison overlap. Freeze2024–2026 confirmation where available, ending at the last complete observed session for that family; earlier discovery cannot inspect it for selection.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q03 fixes day boundaries/roll conventions. Q22 fixes release/pricing metadata gaps. Missing datasets are reported, never invented.

## Related

[options chain availability](options-chain-availability.md), [measurement contract](measurement-contract.md), [cross market price mapping](cross-market-price-mapping.md)

Review findings: BUNDLE-01, DATA-01, DATA-02, DATA-03, DATA-04, DATA-05. [Review ledger](../REVIEW_LEDGER.md).
