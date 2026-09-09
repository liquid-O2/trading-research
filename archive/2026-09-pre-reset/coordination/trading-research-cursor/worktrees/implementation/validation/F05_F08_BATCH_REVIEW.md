# F05–F08 complete static review and consolidated repair

All four reviews completed and all 36 findings collected before the first repair. No new tests, compilation or source import ran during this review.

## reports/f05-independent-review.json

- F05-SR-01 (high): After admitting a value and capturing a snapshot, assign reducer.config['start']=another anchor, reducer.config['row_ticks']=another grid, or ledger.config['definition_version']=another definition. Both public mappings and the config attributes themselves remain writable.
- F05-SR-02 (high): Apply root A at known_at=10, capture snapshot(10), then apply independent root B at the same allowed known_at=10 and checkpoint. Equivalently capture snapshot(30) before a subsequently admitted delta at 20. Both are currently legal public calls.
- F05-SR-03 (medium): Create two reducers with the same default definition_version but different anchors/grid origins/row widths/terms, then produce empty snapshots at the same cut, or snapshots whose finite included values happen to coincide.
- F05-SR-04 (high): Observations are known at 12 and the candidate graph actually completes at 15; or a pairing proof is known at 30 and reconciliation completes later. The function has no completion parameter and labels max(inputs,proofs) as Reconciliation.known_at.
- F05-SR-05 (high): One left and one right trade have matching time/quantity but a missing price or condition. Unsupported fields suppress every candidate edge, so capacity=0 and the result reports distinct_print_count_conditional_bounds=(2,2). A q5 summary versus q2/q3 split prints likewise reports an exact count from incomparable aggregation records.
- F05-SR-06 (high): Two roots for the same instrument have independent channels/publishers/source sessions, equal event_at and different local source_order values (for example channel A order1 at price100 and channel B order2 at price101). TransactionTapeView exports both raw integers as Trade.order.
- F05-SR-07 (high): Pass an MBP event from raw instrument A with a TransactionKey labelled instrument B, arbitrary publisher/channel metadata, and FuturesTerms from another root. Dataset/schema/source-row checks pass; the function never binds event.instrument_id or available publisher identity to the supplied key/terms.
- F05-SR-08 (high): A pending cancel resolves with an original into Admission.deltas=(insert,cancel) at one completion cut. The public reducer.apply(insert_delta), or apply_batch((insert_delta,)), succeeds, after which snapshot(cut) publishes the original's mass before the cancel is applied.

## reports/f06-f07-independent-review.json

- QJ-R01 (high): Aggregate support infers full positive coverage from an empty incident set.
- QJ-R02 (high): Copied old valid content or later receipt of an older revision supersedes the newer invalid revision.
- QJ-R03 (high): Same observation/revision with different receipt clocks bypasses conflicts; equal aliases with different receipts lose acquisition lineage.
- QJ-R04 (high): FieldFact defaults to every operation without capability evidence.
- QJ-R05 (high): OI coverage treats any observed contracts-valued field as OI and any field as quote.
- QJ-R06 (high): Bindings, bounds and configuration_version are writable after timelines are built.
- QJ-R07 (high): Direct interval/aggregate calls bypass recovery validation and permit book recovery to close missing flow history.
- QJ-R08 (medium): No expected stream, no liveness and zero trades becomes observed_no_event.
- QJ-R09 (medium): Admitted support can lack observation/lineage fields or contain mutable acquisition pairs, causing forged availability or join TypeError.
- QJ-R10 (high): Quality propagation ignores mandatory/optional empty-field provenance edges.

## reports/f08-independent-review.json

- F08-R01 (high): Mixed-profile test expects an exception that the actual branch cannot raise
- F08-R02 (high): Derived publication discards original validity endpoints
- F08-R03 (high): RollSelection accepts inconsistent output or pre-input publication and survives the ledger
- F08-R04 (high): AdjustmentResult accepts fabricated arithmetic and premature publication
- F08-R05 (high): Derived destination identity is not reserved against conflicting base-state reuse
- F08-R06 (medium): Availability gates omit declared coordinate/source validity
- F08-R07 (medium): RawCoordinate.from_definition can outlive explicit contract expiry
- F08-R08 (medium): Cash arithmetic accepts unqualified or mixed currencies
- F08-R09 (medium): Literal selector and kernel disagree on identical volume redelivery
- F08-R10 (medium): Corporate action logical identity can fork or cross assets without rejection

## reports/f05-f08-orchestration-review.json

- ORCH-01 (high): Post-worker retention/finalization failure strands reserved peers
- ORCH-02 (high): Supervisor termination has no recoverable worker lifecycle
- ORCH-03 (high): Recorder trusts mutable summary members/resources without validating trial completion
- ORCH-04 (high): Supervisor permits incomplete participating family sets
- ORCH-05 (high): Complete review and exact case mappings are not frozen or checked before execution
- ORCH-06 (medium): Killed or crashed worker loses accumulated assertion output
- ORCH-07 (medium): Read-then-write evidence merge can drop concurrent ledger additions
- ORCH-08 (medium): Attachment can commit before known audit/summary failures with no idempotent recovery

The single consolidated repair pass is authorized. The machine record retains pre-repair identities and will record dispositions and repaired code identity before supervised execution. Protocols, golden fixtures and original sources remain frozen. Synthetic assertions retain all source, consumer, native-data and economic gates.

The one consolidated repair pass is complete. All 36 findings have dispositions in the machine record; the three orchestration residuals found together during repair confirmation are retained and corrected before this first execution. Root read the complete repaired production paths and references; independent test/caller confirmation is retained for QJ. All frozen protocol and golden hashes remain unchanged. The reviewed code manifest is `22a1ad284cec49942ef6b16e1c63d27ea14d75044ae168dcb8f43aeb0b5ad3f2`; the full suite contains 417 statically identified test methods. No F05–F08 verification run preceded this freeze.
