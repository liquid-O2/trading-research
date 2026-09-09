# F05 canonical transaction engineering protocol

Status: frozen before dependent implementation. The registration report pins this
protocol, literal expectations, source review and pre-implementation code snapshot.
F05 shares one combined full-suite worker with other registered foundation batches;
its actual resource use is conservatively charged to each participating family.

Scope: F05 event identity/conditions/side, F05.CROSS_VENDOR reconciliation, SR-F05,
UP-F05 shared insert/revise/cancel algebra, and the directly affected measurement
and bar callers. All 22 assigned source findings and 28 source-preparation cases
remain in reports/f05-source-preparation.json. This engineering batch does not
close all native cohorts, all consumers, P0-P7, options sign learning, or E0-E5.

## Observed implementation boundary

`data.events.normalize_mbp` already preserves raw values, typed action/side,
bitwise flags, clocks, source address, pre-trade quote association, and unknown
aggressor. `CanonicalEvent.trade_eligible` is an MBP record predicate, not a
universal provider-condition engine. Its immutable decoder v4 event IDs are
already used by partition manifests and must not change in this batch.

`measurements.tape.TradeLedger` is a bounded finite reference with immutable Trade
records and current corrections. It rejects a correction before its original,
permits only one correction of each referenced record, and stores correction
metadata in a dict. Keep this implementation and its existing callers available
as the earlier stage/reference. Do not disguise a rewrite as source equivalence.

`data.reconcile.compare_multisets` preserves multiplicity at time/instrument/raw
float bits/size/side. Its matched counts establish equality under that observation
key, not confirmed transaction ownership. Keep it as the raw multiset comparator.

`BookReducer` and `CompactProjector` currently compute observed-source flow and
book validity together. Neither is a revision-aware transaction ledger. Keep their
book behavior and source-faithful flow as audit/execution references; canonical
corrected measurements are separate outputs with explicit names. Trade corrections
do not manufacture historical venue fills or erase already observed book events.

## Registered interfaces

New module `data.transactions` contains immutable values, receipt envelopes, deltas,
and the bounded ledger. New `measurements.transaction_reducers` contains shared
mass/profile/money reducers and adapters. New `data.transaction_matching` contains
bounded evidence-specific reconciliation. A new `references/transactions_literal.py`
implements complete raw-receipt replay without importing incremental reducers or
calling their transition routine. File locations are proposed, not created.

`TransactionKey(provider, dataset, publisher_or_venue, channel, source_session,
instrument_key, ownership_id, ownership_basis, ownership_evidence_id)` identifies
one economic transaction root. instrument_key includes raw contract and definition
version; quantity unit and instrument kind cannot silently change. ownership_basis
is either certified provider transaction ID or exact source-row identity. A source
row identity is only observation-local ownership, never a cross-vendor identity.
No global exchange-sequence key and no timestamp-price dedup. Missing sequence,
receipt, publisher fields and participant identity remain absent.

`TransactionValue(event_at, price_decimal, price_ticks, quantity, quantity_unit,
reported_aggressor, aggregation_unit, instrument_kind, terms_version,
usd_multiplier, money_role, volume_eligibility, directional_eligibility,
condition_contract_id, raw_condition, quality_reasons, history_complete)` is the
full replacement value, never a patch interpreted against unspecified state.
Use finite Decimal or Fraction exact arithmetic for money; outright profile/order
prices use exact ticks. quantity is a positive whole count. Null monetary price
and null profile ticks are distinct: an off-grid raw price can retain money
arithmetic while tick-profile mass is unpriced. usd_multiplier and money_role are
required before emitting USD channels. `futures_notional_USD` is not futures P&L;
`option_premium_USD` is a separate role and cannot be added to contract counts.

Unknown sign remains None and contributes to eligible total/unknown volume. An
unknown condition is not the same as unknown sign: retain raw observed size and
provenance, but do not certify volume/directional eligibility without the dated
condition contract. Snapshot activity and non-trade actions yield explicit
non-transaction dispositions. A positive spread quantity is a spread-unit record;
a futures-outright or single-option reducer rejects it unless that exact spread
instrument/unit is separately configured. Negative or zero outright quantity
fails before admission. Unknown enums retain a reason, never a fabricated sign.

`TransactionReceipt(receipt_id, source_event_id, root_key, version_id,
predecessor_version_id, operation, clocks, source_address, raw_payload_hash,
raw_payload, value, condition_contract_id, identity_evidence_id)` separates three
identities: immutable physical receipt, economic transaction root, and immutable
provider/evidence revision. operation is exactly insert/revise/cancel. Insert has
no predecessor and has a value; revise requires a predecessor and full value;
cancel requires a predecessor and value=None. Provider message action C is a book
cancel unless an explicit provider correction contract links it to a transaction.
No synthetic correction target is inferred from time/price alone.

Two byte-identical receipt IDs are idempotent; changed bytes under a receipt ID
raise IntegrityError. New receipt IDs for an identical, evidence-proven version
are retained as receipt evidence but emit no additional economic delta. Changed
business content under the same version ID raises IntegrityError. Version content
includes root, predecessor, operation, value, condition/identity contract; transport
receipt clocks/locator are separate. A same-valued *new* revision ID is a lineage
change and emits a delta with zero arithmetic but changed version/provenance.

`TransactionDelta(id, root_key, operation, cause_receipt_ids, prior_version_id,
next_version_id, before_value, after_value, known_at, computed_at,
affected_event_intervals, affected_fields, definition_version)` is append-only.
Its ID hashes the complete immutable envelope. It always carries the complete
before and after values, including nonnumeric lineage changes. No downstream
consumer reinterprets a provider correction. Ledger emits deltas; consumers verify
expected prior version and apply once by delta ID. Forged before-value, skipped
version, reused delta ID with changed bytes, unit drift, or negative resulting
nonnegative mass fails atomically.

Public methods:

* `TransactionLedger.admit(receipt, *, actual_completion_at) -> Admission`.
* `Admission(status, receipt_id, pending_version_ids, deltas, committed_at)`.
* `TransactionLedger.asof(instrument, cut, start=None, end=None) -> tuple[ResolvedTransaction]`.
* `TransactionLedger.changes(instrument, cut, start, end) -> tuple[TransactionDelta]`.
* `TransactionLedger.checkpoint() -> bytes`; `restore(bytes)` with complete replay
  validation, bound/config/version checks, and canonical bytes.
* `TransactionReducer.apply(delta)` and `apply_batch(tuple_of_deltas)`; batch is
  all-or-none. `snapshot(cut)` returns an immutable artifact, never a live dict.
* `reconcile_observations(left, right, *, contract, max_rows, max_candidate_edges)`
  returns the immutable reconciliation result specified below.

## Ordering, correction-before-original, and durable state

F04 supplies nondecreasing admitted availability. Independent same-time roots are
commutative for mass; causal predecessor links order revisions of one root.
Independent event paths remain explicitly tied, not assigned a false market order.
`actual_completion_at` must be at least all receipt/dependency availability needed
for that admission. No modeled compute duration is added to observed completion.
A previously received pending correction can become usable only when its missing
predecessor is received and the resolution finishes.

Maintain bounded immutable receipts, version-content hashes, predecessor links,
per-root reachable live version, pending versions, committed delta log and source
ownership evidence. Each root is a single chain. Reject a second nonidentical
successor of a predecessor, second insertion of the same root, cross-root
predecessor, cycle (including pending cycles), revise-after-terminal-cancel, or
source revision content conflict. Cancellation is terminal in this initial
contract: a provider reinstatement needs a separately specified operation/version,
not an implicit insertion. Distinct root IDs can of course carry identical prints.

When a predecessor is missing, retain the receipt with status pending_dependency;
active state and arithmetic do not change. Missing original is not a zero trade,
not a rejection of a useful future correction, and not permission to invent it.
On delivery of the missing original/predecessor, resolve the unique available
chain in one atomic admission. Emit the ordered deltas with the same resolution
availability, and expose only the final batch state to external consumers at that
cut. Original insert then pending revise/cancel are internal delta transitions,
not a transient published original resurrected into earlier history. If resolution
requires more than the declared tie/chain bound, reject the triggering admission
without mutation and retain the previous pending state/backpressure evidence.

`asof(cut)` uses committed deltas with known_at <= cut; it never reads a current
live dict as historical truth. Earlier snapshots remain immutable. Corrections
changing event time affect both old/new event windows; a correction at time 30 to
a transaction originating at 10 becomes visible at 30, not 10. A time window's
membership is based on the currently known replacement event_at. Pending receipts
are separately queryable diagnostic evidence, not inferred missing volume.

The initial implementation can be a bounded in-memory engineering ledger backed
by canonical checkpoint artifacts and the durable F04 input stream. It must count
ALL retained receipts, versions, deltas, pending links and dedup evidence toward
explicit total-record and canonical-envelope-byte limits. Suggested fixed bounds:
max_records=4096, max_bytes=8 MiB, max_pending=256, max_resolution_deltas=256,
max_match_rows=512, max_candidate_edges=4096, max_snapshot_versions=128. Consumers
also bound retained delta IDs and profile rows. A bound is checked for the entire
admission/batch before commit. No silent eviction, unbounded correction dict,
implicit spill, or rollback leaving counters changed. These are engineering
limits, not empirical production throughput claims.

Checkpoints include schema/definition/condition/ownership configuration, every
retained envelope and link, admission cuts, output delta IDs and reducer cursor.
Restore recomputes lineage, live state, arithmetic and counters from retained raw
receipts before accepting; unknown schema/config or forged arithmetic is rejected.
F04 peek can be redelivered after a crash. Commit ledger+consumer idempotent state
before input ack. Persist a single checkpoint containing ledger and registered
consumer cursors, or use a documented atomic artifact publication; do not claim
external exactly-once effects. Old ledger checkpoints require explicit migration;
the old TradeLedger restore remains available as its own version.

## Shared reducer algebra and consumer integration

For each eligible value v define q(v)=quantity and side channel b/s/u according to
reported sign and directional eligibility. Null before/after gives zero. For each
delta, every additive channel changes by contribution(after)-contribution(before).
Track buy, sell, unknown, total, signed=buy-sell, live_prints, observed/excluded/
condition-unresolved size separately, unpriced monetary mass, profile-unpriced
mass and incomplete-history counts. Nonnegative channels must never underflow.
Signed bounds are [signed-unknown, signed+unknown] only when flow history is
complete and volume eligibility is certified; otherwise unavailable, not a finite
bound over missing prints. Unknown-side coverage is not missing-print coverage.

A grid-specific profile uses row=origin+floor((ticks-origin)/row_ticks)*row_ticks,
separate nonnegative buy/sell/unknown rows, exact old-row removal/new-row addition,
and zero-row deletion only in the current view. Definition, anchor and instrument
are fixed per reducer. Corrections can move mass across price rows or event-time
anchors, so emit both affected supports. A windowed reducer evaluates before and
after membership independently. A rebin is a separate definition/recompute, not
market mass migration. Active VWAP sufficient sums are mass, sum(q*p_ticks), and
sum(q*p_ticks^2); downdates are exact and missing-price coverage remains explicit.

Per instrument/money role accumulate absolute and signed priced notional/premium
as exact price_decimal*quantity*usd_multiplier, plus unpriced quantity. Arithmetic
cannot combine different instruments, multipliers, money roles, currencies or
quantity units without an explicit upstream transformation. No Greek flow is
invented: O16 remains separate and uses event-frozen valuation evidence.

Add `trade_from_transaction(resolved)` returning the existing immutable Trade
view, with Trade.id=root ID, source_content_version=active version hash,
known_at=resolution availability, original/revised event_at, reported sign, exact
profile ticks or None, and original source order if actually available. Do not
feed successive versions through TradeLedger.add as if they were new prints.
Use a `TransactionTapeView` over `TransactionLedger.asof` for finite consumers.

Concrete existing-public integration changes proposed for this batch:

1. `runtime.ports.reference_graph`: add named F05.TRANSACTIONS and
   F05.RECONCILIATION evidence ports; extend semantic/eligibility fields with
   revision/ownership/condition evidence, retaining the nonrecursive S0 order.
   Stage ordering becomes RAW0, RAW_QUALITY1, NORMALIZED2, TRANSACTIONS3,
   SEMANTIC4, ELIGIBLE5, BARS6. RECONCILIATION is a same-stage peer over normalized
   observations and is an optional semantic diagnostic, never a mandatory wait
   for a second vendor. Existing market/timer/account lanes stay unconditional.
2. `measurements.tape`: add `TradeLedger.changes(...)` as a read-only correction
   evidence interface and a `TradeView` protocol (`asof`, `changes`); `changes` returns immutable
   `CorrectionImpact(id, known_at, before_instrument, before_event_at,
   after_instrument, after_event_at)` tuples intersecting the requested old/new
   interval. The old ledger builds these from its original/replacement records;
   TransactionTapeView builds them from committed deltas, excluding plain inserts.
   Leave
   TradeLedger add/correct/asof/checkpoint semantics and existing raw references
   intact. Add the new transaction-to-Trade adapter in the new reducer module.
3. `foundations.bars.bar_reference`: replace direct `.corrections/.trades`
   inspection with the `changes(...)` interface, preserving existing literal
   ledger output byte-for-byte for current cases. Accept TransactionTapeView for
   complete correction-chain and late-original causal bars. No automatic change
   to BarEngine's default ledger/checkpoint in this batch.
4. `measurements.auction.tpo_reference` and `bounded_dwell`: widen the documented
   input type to TradeView; their asof-only algebra stays unchanged. Integration
   fixtures use both ledger views at identical cuts and compare full recompute.

`cvd_reference`, `cvd_bar`, `profile_reference`, `vwap_two_pass`, `footprint` and
`WeightedMoments` remain unchanged reference consumers; exercise their outputs
on the new asof view versus shared reducer snapshots. BarEngine, ActivityBars,
BookReducer, CompactProjector, ColumnarVenuePath, raw partition manifests,
readers/decoder, audit.sample_partition and old reconciliation pilots retain
their current defaults and IDs. They do not thereby become correction-aware.
Activity-bar boundary repair and affected execution/candidate policy replay are
explicit subsequent consumer gates, not claimed by an additive mass test.

## Bounded uncertain embedded/standalone matching

Reconciliation inputs are immutable source observations with exact contract,
time precision interval, raw price representation, size, reported sign,
condition, aggregation unit, source order/row ID, and optional ownership proof.
The contract names left/right schema versions, precision/clock comparability,
primary source for measurement, and supported key fields. It does not invent
missing fields or align to a future quote. Reject mismatched/unknown units before
comparison; missing key fields yield named unsupported categories.

Deduplicate verified physical ingestion copies within a source first. Preserve
legitimate repeated observations. Enumerate candidate pairs only when the
contract permits their instrument/time/price/size/condition/aggregation match;
side disagreements are a discrepancy category, not silently corrected signs.
Store each component's left/right IDs and candidate edges, certified edges and
unmatched IDs. Bound rows and candidate edges; fail explicitly on excess, never
truncate into false certainty. Do not enumerate all combinatorial pairings.

A one-to-one candidate edge by time/price alone is not certified identity. Only
explicit provider identity/equivalence evidence can mark a certified pair.
Two same-key left prints and one right print yield two possible edges, no chosen
owner, candidate capacity min(2,1)=1, and zero certified pairs without additional
evidence. Absent a verified overlap contract the number of distinct executions
compatible with those observations is 2..3, not exactly 2 or 3. That interval is a
conditional multiplicity diagnostic, not an assertion of actual market volume.
If overlap count is certified but pair identity is not, retain that separate fact
and ambiguity; do not pick the first source row. Use the predeclared primary MBP
stream once for baseline measurements, while recording alternate/unmatched data;
standalone becomes additive only with affirmative distinctness evidence.

Trade-summary vs split prints is aggregation_mismatch even when total volume is
equal. Repeated BBO snapshots are snapshot_state, not multiple trade executions.
Inside-spread/unknown side is side_uncertainty, separate from missing_print and
condition_unknown. Late corrections create new reconciliation-result versions;
prior match diagnostics and prior decisions stay unchanged.

## Official dated mappings and retained exclusions

Do not add real Theta/OPRA auction/condition/cancel/correct or publisher-bit tables
from memory. This draft uses an explicit synthetic-contract-v1 condition table
for synthetic fixtures only, plus the already reviewed MBP decoder contract as
an earlier implementation comparator. Before native expansion, require official
retrieval/content hashes, provider/product/schema versions, effective-date scope,
condition code meaning, correction target semantics, volume/sign eligibility,
quote timing/precision and known unresolved cases. Current docs alone do not
certify all historical dates. Native GLBX publisher bit 2 remains unresolved until
its actual historical supplement is retained and reviewed.

DRF venue/contract/sequence/aggressor fields are not participant IDs. Unknown sign
or non-dropping BBO size is not an iceberg. MBP-10 means levels, not guaranteed
ticks; MBO-only buffering is not reapplied to MBP-1. DEN C-score formula, empirical
bubble verdicts, streak superiority and sizing safety are unsupported; retain all
28 preparation dispositions. No acquisition, account-risk escalation, latent
participant model, trade signing fit, or market diagnosis is authorized here.

## Fixed validation and execution discipline

The companion literal JSON holds independently specified exact arithmetic and
state expectations. All amounts are synthetic. Compare three labeled stages:
source-faithful raw decoder/multisets and existing finite ledger where supported;
complete raw-receipt reference for the expanded correction contract; shared delta
reducers. Compare identical inputs/units/cuts; mark old unsupported cases as such,
not failures patched out of the original comparator. Test all source-preparation
cases or retain their precise non-executable dependency/disposition.

Required assertions include correction before original and predecessor, side/
size/price/time changes, identical-value new lineage, chained cancel, duplicate
receipt and revision, conflicting/forked/cyclic lineage, source-order namespaces,
future-suffix deletion, insertion permutations compatible with receipt clocks,
restart before/after publication/ack, forged delta/checkpoint, bounded records/
bytes/pending/chain/matching, snapshot vs trade, conditions/units, and independent
risk/timer lanes. All full-recompute snapshots must agree exactly (integer,
Fraction/Decimal; no tolerance selected after failure). Preserve zero and unknown
coverage separately. Consumers must include CVD, profile/footprint, VWAP/money,
and at least causal bar, TPO and dwell reference integrations for this batch.

After complete static review of new code and affected callers, make one
consolidated repair pass, then run the full engineering suite once. Proposed same
family ceiling as F04: at most 3 attempts, 600 total CPU seconds; each attempt
180 soft/190 hard CPU seconds, 4 GiB address space, 240 wall seconds. Root owns
final frozen registration and execution. Preserve every failure, exact code
snapshot, expected assertions, stdout/stderr and measured CPU/wall/RSS/work counts.
No test/fix iteration used to manufacture passing evidence. Current proposal has
zero tests or production execution. Optional future native/condition expansion
requires its own admitted cohort/data scope; not hidden inside synthetic tests.
