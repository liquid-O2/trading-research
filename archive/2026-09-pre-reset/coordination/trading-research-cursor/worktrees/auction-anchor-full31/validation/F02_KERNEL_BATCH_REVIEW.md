# F02 kernel batch: complete review before one repair pass

Review recorded 2026-09-06 before running the registered verification.
The original protocol and independent golden values remain unchanged.
This is the review of the new F02 change and all its current consumers;
the earlier complete repository review remains a separate historical record.

Reviewed in one pass: all of `foundations/payoffs.py`, all of
`foundations/instruments.py`, the changed deletion adapter and existing
definition adapter/audit in `data/definitions.py`, the existing registry
consumer in `tests/test_foundations.py`, the definition and roll consumers,
exact unit and clock contracts, serialization, verification grouping, all 17
new test methods, and the new supervised verification command. Text searches
found no other registry, retirement or payoff-kernel consumers. The runtime
does not yet consume these kernels; that is explicit remaining P5 work.

The findings below were collected before applying any repairs to this batch.
The newly authored tests express expected behavior; they have not yet run.

| Finding | Defect or missing guard | Consolidated correction |
|---|---|---|
| F02-R01 | A definition correction known after a deletion wins the latest-version selection and silently reactivates the retired lifetime. | Keep available retirements effective for their entire named lifetime, regardless of later definition corrections. Preserve earlier effective-time queries and disjoint reused-ID lifetimes. |
| F02-R02 | Different, overlapping lifetime identities can be selected by knowledge time alone, including a changed expiry after deletion. | Reject overlapping lifetime ambiguity. Reinstatement and ambiguous lifetime-boundary correction require a separate explicit mechanism; they are not inferred. |
| F02-R03 | Raw deletion binding checks numeric ID and symbol but omits provider/venue, class and supplied activation/expiry. | Check the prior adapter namespace and each supplied lifetime field, preserving complete raw bytes in the retirement version. |
| F02-R04 | The public `PayoffKernel` constructor bypasses `compile_payoff` validation. | Put the shared validation in construction and make the factory call that constructor. Both entry points reject identity/style/availability conflicts. |
| F02-R05 | Kernel compilation accepts an unknown/conflicting raw tick or future last-trade deadline beyond expiry. | Require execution terms, reconcile the smallest declared tick, preserve the NQ/ES constant grid, validate separate last-trade/expiry boundaries and causal compilation cuts. |
| F02-R06 | Future delivery checks the underlier's root/ID/expiry but not its supported valuation status; trading checks omit underlier availability. | Check the exact underlier's valuation eligibility and current availability. No root substitution is permitted. |
| F02-R07 | A share-basket price has a named unit but no separately checked cash currency. Terms in EUR could consume a USD share price. | Declare the deliverable and observation currency, require matching basket/contract currencies and reject a mismatched observation. FX remains an explicit separate conversion. |
| F02-R08 | Intrinsic input validation checks knowledge but not whether the frozen definition/terms apply at the requested effective time. | Check both validity intervals and expiry before consuming prices. Keep fixing time/identity separate from trade ticks and raw marks. |
| F02-R09 | American early exercise reuses the expiration payment date even though no early-settlement schedule was supplied. | Retain mark-to-intrinsic arithmetic and reject unsupported early exercise obligations. This batch emits obligations only at the explicit expiration fixing. |
| F02-R10 | Several frozen public dataclasses accept mutable or wrongly typed nested values, and identity-set construction can fail before a useful contract error. | Validate nested contract types, nonempty text, immutable distinct tuples, explicit cash currencies and exact numbers before using them. Decode invalid serialized decimal values as contract errors. |
| F02-R11 | A delayed observation can create an obligation whose knowledge timestamp precedes its effective exercise observation. | Conservatively include the exercise time with all required input knowledge times. Keep the separate payment time and conditional interpretation. |
| F02-R12 | The literal comparator lacks positivity/shape checks on its independently supplied constants and basket. | Keep its direct equation independent of compiled methods, but reject unsupported malformed inputs explicitly. |

The new test fixture deliberately declares currencies on its adjusted
deliverable and price observations; those expected public fields are part of
F02-R07's consolidated implementation. Additional checks for overlap,
out-of-validity intrinsic and malformed nested values belong to the same
existing test methods. No new expected cash amount is selected from execution.

The supervisor was reviewed against the already registered family. It retains
the exact original protocol and golden artifacts, captures the complete code
snapshot and its own source, runs the full existing suite once in a worker
with 180/190 CPU-second soft/hard limits, 4 GiB address-space and a 240-second
wall limit, and records worker/descendant resources and any failure. A passed
suite is checked against the pre-run code identity. Fixed synthetic algorithm
tests are engineering assertions, not market research or economic runs.

After the consolidated repair, execute that one combined verification. Do not
run the old decoder audits, market partitions or an economic search for this
change. Only a concrete remaining failure or changed implementation justifies
another execution, within the same registered attempt/CPU budget.

The supported outputs remain exact conversion and conditional expiration
obligations. Actual assignment, receipt of cash, full option fair values,
Greeks models, early exercise settlement, corrected overlapping lifetimes,
native option definition admission, dated product cohorts, all-consumer
invalidation, full F02 P0–P7 closure and profitability are not established.
