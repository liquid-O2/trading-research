# F01 / F01.DECODER source and validation review

Review opened 2026-09-06 after the sequencing correction. This is an explicit
case inventory, **not a declaration that F01 or all its phases pass**. The
previous 176-test run predates this inventory. Expected results below were
written before the new fault tests and repairs.

## Definition and sequence

The whole F01 ten-part card, SR-F01, UP-F01, F01.DECODER, both local P0–P7
records, UPK-01 and the applicable common/source contracts have been read.
The literal decoder is the reference. Projected and shared materializations
are challengers and must preserve admitted information, source identity and
downstream outputs. A changed information set is a separate comparison.

Acceptance means committing schema, content identity, complete counts and
decoded/rejected outputs together. A diagnostic prefix does not meet that
definition. Unknown enums remain raw and unknown; unresolved prices, times
and instruments cannot acquire guessed meanings. Original files remain the
source of record. Whole-file identity and sampled row hashes have distinct
evidence extents.

P0/P1 source cases come first. P2 measures fidelity and resources on identical
records. P3 reports supported schemas/cohorts and errors. P4 retains native,
canonical and projected alternatives. P5 requires rerunning affected
consumers. P6 needs the later complete E0–E5 chain; P7 needs future capture and
operational evidence. Those later dependencies do not prevent opening fault
tests, and passing a reader test does not complete those phases.

## Original passages and resolved consequences

Every row was followed through SOURCE_TO_DESIGN and SOURCE_FINDINGS_AND_CONFLICTS.
The CEX-22/26 rows of CONVERSATION_RECHECK and TECH-16 of EXTERNAL_TO_DESIGN were
also followed. SOURCE_REVIEW_LEDGER has now been read completely; its planning
review totals do not stand in for this implementation review.

| Source | Original reviewed passage | F01 consequence and assertion/dependency |
|---|---|---|
| CEX-10 | `sources/documents/conversations/conversation_export (1).md` 214–416 | Historical subscription, price and requested-schema claims cannot certify ownership, quote coverage or publication time. `inventory_complete_is_not_eligibility` exercises this boundary. Current pricing is irrelevant to this local reader validation; procurement remains outside this run. |
| CEX-22 | Same conversation 750–1021 | Actual manifests supersede guessed costs, request counts, old queue state and assumed holdings. Quotas were dated acquisition observations, not present limits or processing budgets. Schema changes and interrupted downloads need explicit admission failures. No download/retry side effect belongs in the local reader. |
| CEX-26 | Same conversation 1155–1199 | Complete/running/pending reports are historical. F01 preserves physical timestamps and contract IDs. The separate F03/F08 cases must establish DST and bar/trade/book contract parity before dependent use. Neither a filename date nor continuous-root name proves that parity. |
| INV-01 | `sources/documents/inventory/DATA_INVENTORY.md` 1–34 | Preserve 111 datasets and original paths/bytes. Path/size reconciliation is weaker than content hashing and semantic coverage. Acceptance of a prefix or metadata identity as complete content must fail. |
| INV-02 | Inventory 36–141 | Native futures-options definitions/trades/statistics/bars stay separate; no acquired option BBO is inferred from those files. Native raw bytes are supported; each schema's typed semantic adapter and golden rows still need their own evidence. |
| INV-03 | Inventory 145–249 | Preserve actual NQ standalone-trade start and discontinuous ES book coverage. MBP trade reconstruction requires action/flag reconciliation; an absent ES book never becomes a zero-spread quote. Existing seven paired hours are bounded evidence only. |
| INV-04 | Inventory 251–298 | ETF venue bars and superseded OPRA reference pulls retain source identity. Overlap is not additive flow. Intraday NDX/SPX cash is not supplied by these bars. Cross-acquisition economic matching is a separate F05/F07 dependency. |
| INV-05 | Inventory 300–563 | Daily listing/EOD/OI, near-expiry quotes, ATM surface quotes and trade/quote scopes remain distinct for all seven roots. Same bytes under two paths are ingestion aliases; different overlapping acquisitions need contract/time/version matching and conflict checks. Full chain semantics and those overlap joins remain open. |
| INV-06 | Inventory 565–734 | Date-only and source-native context remain at their actual frequency. No invented intraday timestamp or publication time. Generic raw preservation is eligible; each publication/revision adapter remains a separate gate. |
| INV-07 | Inventory 736–746 | Derived roll maps are reference artifacts, not as-of selection certificates. Preserve their raw epoch units and companion timestamps; F08 owns the causal roll comparison. |
| INV-08 | Inventory 748–765 | Excluded partial downloads and absent depth cannot enter a consumer manifest. A `.part` is not accepted coverage. No off-touch depth, queue or hidden-inventory capability may be emitted by MBP-1. |
| INV-09 | Inventory 20–34 and all of `data/manifests/timestamp-conventions.json` | Bar `t` is ms; tick `t` is ns; Theta UTC timestamps have ms effective precision. A declared schema/profile controls scale. Keep event, quote, provider receipt and strategy receipt distinct. No second UTC localization. |
| INV-10 | All 91 lines of `sources/documents/inventory/databento_pull_list.md` | Requested CBBO history, depth, estimates and proposed pulls are historical comparators, not eligibility. The current catalog and sampled schemas govern local decoding. Missing requested feeds remain absent. |
| INV-11 | Original bounded audit: `review/data-audit/reconciliation.json`, structure of `parquet-samples.json`; full DATA_CAPABILITY_AUDIT including appendix | All path/size checks and 216 representative files are explicitly limited in scope. The original 216-row sample records have not each been semantically re-reviewed here. New schema-specific golden rows and intended-cohort checks remain open; no whole-archive promotion. |
| INV-12 | Historical hardware observation recorded in source findings and DATA_CAPABILITY_AUDIT | No underlying original command transcript was located. Retain that evidence limitation. Current bounded jobs must measure their actual CPU/RAM/bytes and use enforced budgets; host totals are not entitlement. This is operational evidence, not alpha. |
| DRF-A03 | `sources/documents/conversations/Design robust feature levels.md` 197–205, 240–274 | Old queued Theta status yields to acquired files. Preserve quote time, conditions and all correction fields. A raw decoder does not infer opening/closing or dealer identity. Probabilistic sign, stale/crossed quotes and multi-leg inference stay with their F07/O owners. |
| PIN053-01 | Entire one-line `review/pine-extracted/Pinescript-indicators--main/README.md` | A heading provides no formula, architecture or empirical validation. Inventory/control disposition only; do not fabricate a numerical test for it. |
| TECH-16 | Primary Databento common-fields page, timestamps/prices/action/side/flags; trades schema, checked 2026-09-06 | Signed fixed-point prices admit negative spreads. Undefined price and timestamp use different integer sentinels. Trade B/A means buyer/seller aggressor; other actions do not inherit that sign. Preserve native enum and raw bytes. |

Original inventory (all 765 lines), old pull list (all 91 lines), and the entire
DATA_CAPABILITY_AUDIT were read in this correction. This does not claim every
linked original source for other units has been read. The local F01 inventory
still leaves schema-specific originals, full golden-row coverage and applicable
downstream integrations open.

## Mandatory expected cases

| Case ID | Input/fault | Expected result, fixed before new execution |
|---|---|---|
| F01-GOLDEN-SCHEMAS | Every acquired schema/version nominated for semantic use | Every supplied column and physical type is preserved; typed meanings and golden values agree with the matching source. No MBP-only fixture completes this case. |
| F01-SENTINELS | Native int64 price max, uint64 timestamp max, schema-specific quantity/definition sentinels | Preserve raw integer, emit typed missing before arithmetic/joins; valid adjacent values and signed spread prices remain valid. Required missing event time quarantines the event. |
| F01-NEGATIVE | Native spread price −1.25, valid sizes | Exact −1.25 survives raw decoding; instrument registry separately gates outright valuation. |
| F01-EMPTY | Valid zero-row Parquet; valid metadata-only DBN; zero-byte corrupt file | Valid empty containers have zero decoded/rejected rows and explicit empty coverage. Missing/truncated headers fail. Empty does not establish a quiet trading session. |
| F01-PARTIAL-GROUP | Prefix ends inside the second row group, multiple batch sizes | Physical row addresses and raw values match the literal prefix; report prefix extent and never whole-partition acceptance. |
| F01-SCHEMA-DRIFT | Required field removed/type changed; new schema/version in later partition/batch | Reject/quarantine against the declared schema; require an explicit version mapping. Never coerce a tick timestamp/profile into a bar profile. |
| F01-TRUNCATED | Truncated Parquet footer/body, DBN metadata/record and compressed frame ending | Raise explicit integrity/quarantine result for attempted complete reads. Successfully decoded prefixes remain diagnostic only and cannot certify unread suffixes. |
| F01-DUPLICATE | Same committed partition ingested twice | Same source/event IDs; downstream flow counts once. Two legitimate equal-looking prints at distinct physical rows still count twice. |
| F01-ALIASES | Byte-identical source files at two paths | With verified whole-file identity, same ingestion source/event IDs; retain both locator observations. Metadata-only identities cannot assert alias equivalence. |
| F01-REORDERED-FILES | Permute the input file list | Same set of source/event IDs and outputs under the declared source ordering; no global input-list row counter. |
| F01-CRASH | Failure after data write but before final manifest publication | No partial consumer-visible accepted partition. Restart publishes an atomic schema/count/content/output bundle or records failure. |
| F01-OFF-TICK | Exported decimal just outside a quarter tick | Keep exact binary-export residual; tick conversion fails explicitly. Do not silently round to a supported tick. |
| F01-NATIVE-EXPORT | Same event represented as native fixed-point/enum and exported decimal/character | Common semantic fields match exactly; extra native receipt/sequence/count fields remain present and absent export fields remain missing. Raw representations retain their differences. |
| F01-UNKNOWN-ENUM | Unknown byte/integer/character action or side in an otherwise valid record | Raw value retained, canonical enum unknown, affected consumer gated. Do not guess side or silently drop observed unknown-side volume. |
| F01-PROJECTION-CORRECTION | Narrow projection omits a field needed by correction handling | Projection is rejected before admission or downstream use; changing the retained correction field changes relevant content/version even if numeric trade columns do not change. |
| F01-INTERRUPTED-MATERIALIZATION | Stop between chunks; restart with same/changed source/decoder/config | Same inputs yield exact source identity and downstream parity. Changed input/version rejects old checkpoint. Unread suffix cannot be inferred. |
| F01-SUFFIX | Delete records after a fixed decision cut | Already published prefix is unchanged. Full-file provenance may change, but this cannot retroactively change historical event semantics or claim equivalence of the whole file. |
| F01-DELAY-CORRECTION | Same event timestamp, changed receipt/correction publication time | Prior cut is unchanged; change becomes available at its own clock and invalidates its actual descendants. |
| F01-RESOURCE | Same records, literal/projected/shared, multiple chunk sizes, cold/warm cache | Exact fields/IDs/downstream outputs; bounded CPU/RAM/read/spill/restart report. No improvement claim from incomparable inputs or cache conditions. |

The source inventory includes cases outside the existing MBP reader, especially
all-schema semantics, complete atomic partition admission and downstream
correction repair. Their current extents are recorded below; unclosed cases
remain implementation/validation work, not external data blockers or
`not_applicable` shortcuts.

Primary sources:
[common fields, enums and types](https://databento.com/docs/standards-and-conventions/common-fields-enums-types),
[trades](https://databento.com/docs/schemas-and-data-formats/trades).

## Executed correction

`reports/f01-faults-before.json` retains the first failing run: 27 methods,
20 passed, nine failing subcases and five error subcases. Native truncated or
missing input could be treated as successful EOF; verified content aliases had
different IDs; claimed content hashes were not validated. Declared-schema
checking was absent, and Parquet corruption used an unclassified provider error.

`reports/f01-faults-second.json` retains the follow-up failures for a valid
zero-row-group Parquet and a record type changing inside a declared single-schema
DBN stream. Those were then repaired. `reports/f01-faults-after.json` is the
subsequent complete run: **191 methods passed, no skips/failures/errors**,
including the 15 new F01 methods. Governing scope hashes and the exact code snapshot
were checked by that run. This is deterministic engineering evidence.

| Case | Executed assertion in `tests.test_decoder_faults` | Remaining extent |
|---|---|---|
| ALIASES / DUPLICATE | `SourceIdentityFaultTests.test_verified_same_bytes_two_paths_count_once_but_two_physical_prints_count_twice` | Verified addresses and BookReducer integration; automatic full-file admission and locator indexing still open. |
| Metadata identity | `test_metadata_only_locator_does_not_claim_verified_alias_equivalence`; `test_malformed_claimed_content_hash_is_rejected` | Metadata-only diagnostic readers still cannot certify whole-file alias identity. |
| SENTINELS / NEGATIVE | `NativeSemanticFaultTests.test_negative_spread_price_and_distinct_price_timestamp_sentinels` | Native MBP price/receipt and required missing event time only; quantity, definitions and other schemas remain open. |
| NATIVE-EXPORT | `test_native_export_common_fields_match_without_inventing_missing_fields` | Hand-checked MBP common values; all-schema golden bundles remain open. |
| OFF-TICK | `test_off_tick_export_residual_survives_and_tick_conversion_rejects_it` | Export residual and exact quarter-tick conversion. |
| EMPTY | `ContainerFaultTests.test_empty_parquet_has_zero_rows_and_zero_byte_file_is_corrupt`; `test_native_zero_byte_and_incomplete_metadata_are_not_valid_empty_archives` | Empty coverage is not a session-liveness certificate. |
| SCHEMA-DRIFT | `test_missing_or_changed_declared_schema_never_silently_coerces`; `test_native_declared_schema_version_and_midstream_type_change_are_checked` | Explicit schema argument and native header/body agreement; each real schema version still needs registration. |
| TRUNCATED | `test_truncated_parquet_footer_is_explicit_integrity_failure`; `test_native_metadata_only_is_valid_empty_but_truncated_compressed_frame_fails`; `test_complete_compressed_frame_with_incomplete_dbn_record_is_rejected` | Attempted read extent only; unread suffix remains uncertified. |
| PARTIAL-GROUP / REORDERED-FILES | `test_partial_groups_batch_sizes_duplicate_reads_and_reordered_files_preserve_ids` | Literal prefix field/address parity; shared materializer remains open. |
| RESOURCE boundary | `test_native_byte_budget_is_distinct_from_valid_eof_and_record_prefix` | Decompressed-byte and record bounds tested; cold/warm performance comparison and compressed-budget stress still open. |

The decoder version is now `mbp-literal-v2`. Existing v1 book checkpoints require
an explicit replay/migration; the default does not reinterpret them. Raw file
locators stay in provenance, while verified same-content aliases share source
identity. Native decompression now checks compressed-frame EOF independently
from the DBN record buffer and bounds decompressed bytes as well as compressed
input and record count.

## Atomic Parquet and native follow-up

The [partition protocol](F01_PARTITION_PROTOCOL.md) preceded nine new
`tests.test_partition_admission` methods. They cover real child-process death
between a chunk write and manifest commit, restart, source aliases, exact
accepted/rejected counts, retained rejected rows, missing correction fields,
late chunk corruption before the first consumer yield, and changed
source/scenario/code identity. This closes those cases for the bounded complete
MBP Parquet reference. Native admission, wider schema admission and incremental
shared materialization remain separate work.

The [native protocol](F01_NATIVE_PROTOCOL.md) preceded ten new
`tests.test_native_fields` methods. Eight physical layouts cover Trade, MBP-1,
OHLCV, statistics and definitions across DBN versions 1–3. Hand-packed fixtures
and provider getter comparisons check exact integers, signed prices, versioned
quantity sentinels, all padding/character bytes, v3 leg fields, and ts_out.
Native metadata is now retained from its original source slice: provider
re-encoding had erased nonzero reserved bytes. Changed or projected field
bundles fail before canonical use.

`reports/f01-native-before.json` retains the missing-field and byte-conversion
failures, plus unavailable new adapters. Its compressed-prefix fixture initially
allowed fewer compressed bytes than needed to decode the first Zstd block;
that fixture budget was corrected explicitly. `reports/f01-native-second.json`
retains the subsequently exposed metadata-padding loss. The completed regression
in `reports/f01-native-after.json` passed **210 methods with no skips, failures or
errors**, with unchanged code and governing source hashes.

The fixed real-data comparison in `reports/f01-native-prefixes.json` passed
882 prior-field assertions on 72 records from 24 native file prefixes. Those
records span ES/NQ option definitions, trades, statistics and minute bars. All
sampled files encoded DBN v3; older versions have synthetic fixture evidence.
Exact original metadata and record bytes are saved. CPU use was 0.868 seconds,
wall time 1.810 seconds and peak RSS 110.67 MiB under the declared process limits.
No native file suffix was certified. Missing definition ticks and native
contract_multiplier stayed missing; unit_of_measure_qty remained a separate field.

The current canonical decoder identity is `mbp-literal-v3`, because the raw field
set and schema identity changed. Prior v1/v2 checkpoints and materializations
require explicit replay. The v2 repair description above remains historical.
The pinned [provider record definitions](https://github.com/databento/dbn/blob/v0.69.0/rust/dbn/src/record.rs)
also establish fixed-point treatment for the v3 leg price and delta.

Full GOLDEN-SCHEMAS across acquired Parquet/context schemas, wider/native atomic
admission, every semantic sentinel, downstream correction/replay and identical-input
cold/warm resource comparisons remain open. No complete F01, B00, B01 or economic
gate is claimed.

## Current physical-field and consolidated verification

The subsequent Arrow work preserved every physical field, including nested
types and exact timestamp units. The fixed actual-data audit covers 21 of the
22 catalog profiles: 61 rows and 686 prior-field comparisons matched. The
normalized-event-calendar profile lacks a prior golden row, so the aggregate
report remains incomplete. See [the Arrow report](../reports/f01-arrow-prefixes.json).

The [consolidated implementation review](BATCH_REVIEW_2026_09_06.md) then
collected 27 confirmed cases across all 71 implementation files before one
repair pass. Its final regression passed 247 methods with no failures, errors
or skips. The current canonical decoder identity is `mbp-literal-v4`; the v2
and v3 paragraphs above describe earlier evidence. This does not expand the
admitted schema/cohort extent or complete the remaining F01 phases.

The missing calendar profile was subsequently captured using provider scalar
casts and checked epoch arithmetic before the product decoder comparison.
All 33 field expectations matched at batch sizes one and three, with all 103
supplement checks passing. The [combined evidence](../reports/f01-arrow-profile-coverage.json)
now covers all 22 physical profiles, 64 distinct rows and 719 fixed field
expectations across the two executions. The original failed aggregate report
remains unchanged. No whole-partition, publication or semantic eligibility is
inferred from this prefix coverage.
