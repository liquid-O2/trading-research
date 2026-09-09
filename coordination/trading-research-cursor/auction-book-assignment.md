# Bounded reported-BBO reinitialization candidate

Implement ONLY two NEW files:
- src/trading_research/research/auction_flow_book_recovery.py
- tests/test_auction_flow_book_recovery.py

Do not modify any original source, decoder, BookReducer, CompactProjector, quote/native kernels, pipeline, runner, fixtures, protocol, budgets or evidence. No shell, imports/tests, scans, fits, web, new worker, Context or Location evaluation. The controller will review and wire actual-data comparison after the currently pending cohort/parallel check. This is a separate precisely named source-semantics candidate; it is not an accepted replacement for strict invalidation or a venue recovery certificate.

## Source evidence and interpretation decided by controller

Primary sources checked September 8, 2026:
- https://databento.com/docs/schemas-and-data-formats/mbp-1 : MBP-1 carries the complete top bid/ask prices and aggregate sizes alongside each top-of-book update, and includes trades. Trade-associated quotes are pretrade observations, not a synthetic displayed-size decrement.
- https://databento.com/docs/standards-and-conventions/common-fields-enums-types : bit 4 MAYBE_BAD_BOOK marks an upstream unrecoverable channel gap; bit 32 SNAPSHOT marks replay; bit 128 LAST marks the final record of an event for that raw instrument; bit 8 concerns receive time.
- https://databento.com/docs/standards-and-conventions/mbo-snapshot : MBO snapshot completion can need a later LAST record; a snapshot flag alone cannot certify a fresh completed economic event.
- https://databento.com/blog/data-cleaning : provider book warnings can persist and some source gaps may heal by natural refresh. This does not independently certify a particular local recovery event.

Current accepted projection keeps book_valid false forever after first bit-4, clear or unknown-action invalidation; all raw rows/trades remain retained. Two 23-hour accepted windows therefore have zero valid quote cells, while later cash subwindows from those SAME source files have many valid local quotes. The candidate asks whether the reported local BBO can restart from a clean full completed record, retaining earlier missing-flow uncertainty. It is explicitly the provider-reported BBO state under a declared reinitialization policy, not an assertion of perfect venue sequence or complete historical flow.

## Kernel interface and exact policy

Expose a small bounded class, e.g. `ReportedBBOReinitializer`, with constructor `instrument_id`, `start_ns`, `end_ns`, `latency_ns`, maximum_rows (<=50,000,000), maximum_episodes (finite, <=50,000), and optional adjacent continuation. `add(table)` accepts a <=65536-row original retained quote/invalidation projection for ONE raw instrument and ONE original source_key, with the normal quote schema (see auction_flow_quotes.py). It returns a new Arrow table with only derived `book_valid` changed for this candidate; all original columns, values, types, row order and multiplicity remain exact and input buffers are never mutated. New candidate metadata belongs in its report, not raw columns. `finish()`/`carry()` retain evidence and support exact batch/cut continuation. Read the existing quote/raw projection code and test builders first.

Policy in strict original storage order:
1. An invalidating record has bit4, clear action R, or an unknown action. It sets blocked=true, retaining the FIRST actual invalidating source address in that unresolved episode. Repeated warning rows increase record counts but do not create additional outages/episodes. Clear alone does not imply lost executed flow; bit4/unknown action makes cumulative observed-history completeness false permanently for this prefix.
2. After invalidation, reinitialize ONLY on an A/M/C record with bit4 unset, SNAPSHOT unset, LAST set, and a valid full two-sided BBO in the exact admitted quarter-tick/size domain: 0<bid<=ask<2**53, both sizes strictly between 0 and 2**32-1. Invalid, zero, crossed, sentinel, snapshot-only, no-LAST, trade, no-action N and unknown-action rows cannot be recovery markers. Reinitialization takes effect at that record's own t+latency availability.
3. Before an invalidation, reproduce the original book_valid projection. After a qualifying reinitialization, allow subsequent ordinary A/M/C full-BBO updates in this source domain, with existing snapshot handling; another invalidation blocks again. Respect the original action/validity constraints. Do not promote T/N/R to trusted updates. The recovery record may initialize standing state but must never create OFI against the invalid predecessor: candidate output on the preceding invalid record remains 0, so unchanged QuoteWindow will exclude the first recovered transition. Snapshot replay cannot invent fresh age or pressure.
4. A later local BBO restart never repairs cumulative flow history through an earlier warning. Preserve the prefix's unresolved-history flag separately from current reported-BBO trust and preserve original strict book-valid bits in original input/evidence. Unknown sign, observed trade counts and source flags remain untouched.

Validate exact required fields/types, nulls, raw flags/action/snapshot correspondence, original source_key, instrument ID, event interval, exact known_at=t+latency, nondecreasing t and strictly increasing nonnegative original source_order/source_row validity. Poison on error and prevent later publication/resume. Empty batch/window is explicit and not proof of market completeness. State must own/copy its retained addresses so mutating a returned dict cannot alter later behavior.

## Efficient state and evidence

Use vectorized integer masks and latest invalidation/reinitialization indices where justified; do not do Python/per-row work for millions of unchanged quote records. Sparse episode transitions may use a small loop. Bound all episode/address metadata before allocation/publication. No generic registry, recovery framework or GPU abstraction.

Retain exact first invalidation and recovery addresses (source_key, source_row, source_order, t, known_at, raw_flags, raw_action) for each observed episode, counts of provider-flagged records (not missing rows), valid/invalid/changed rows, and the last source address. Distinguish terminal unresolved episodes. Report the candidate policy/version and clearly name its source assumption. Output is an unpublished validation candidate; full venue history/exchange order is not certified.

Adjacent continuation must bind the same instrument, source key, delay and policy, exact previous end==next start, last original order/time, current blocked state, first unresolved invalidation, cumulative flow-history flag and episode/row counts. Preserve global original order. Batch boundaries and a UTC split cannot reset trust, lose the first invalidation, count an episode twice or grant a new age. Use the existing canonical digest pattern and strict state checks; do not accept a corrupt/future/nonadjacent/different-source carry. Current source units use one original file/source key, so cross-file/source-key joins are unsupported here.

## Independent tests

Write focused hand-calculated sequences and a separate small scalar reference loop with expected masks/episode boundaries. Cover locked/noncrossed valid quotes, repeated flags, qualifying completed ordinary restart, snapshot+LAST alone, ordinary no-LAST, T/N/R/unknown, crossed/zero/sentinel BBO, second invalidation/restart, same timestamps with original order, capacity/poisoning, buffer/address isolation and missing fields/delay/source mismatch. Compare complete returned tables apart from book_valid, including source flags and raw values. Demonstrate that all candidate-unmodified rows keep the original values.

Feed a sequence through the existing QuoteWindow: the first recovered quote contributes no pressure transition from the gap; the next valid quote uses exact current-vs-previous OFI; elapsed standing time starts only from the newly observed ordinary quote. The retained flow-history flag stays incomplete despite local restart. Compare one-pass, arbitrary reader chunks and adjacent interval carry on EVERY projected row and logical episode/lineage/count value. No tests or candidate imports may be executed by this worker; they will run in the controller's registered check.

Return only these two files plus concise remaining concrete issues. Do not edit source/runner to apply this policy globally, and do not claim source-certified recovery from a passing fixture.
