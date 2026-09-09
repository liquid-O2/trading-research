# Implementation decisions and review findings

The implementation request starts the B00–B10 program described in
[/workspace/planning/trading-model/IMPLEMENTATION_HANDOFF.md](/workspace/planning/trading-model/IMPLEMENTATION_HANDOFF.md).
The isolated package is `/workspace/trading-research`; the planning package and
original source/data bytes are inputs. The excluded `/workspace/archive` is not
an implementation source.

1. The earlier U01 planning-only restriction describes the completed planning
   task. The current user request authorizes implementation and bounded local
   verification. It does not authorize external orders, purchases, deployment,
   messages or a costly expansion.
2. All exact scope IDs and all P0–P7 obligations enter a separate implementation
   ledger. Importing definitions does not mark them reviewed, implemented,
   verified or evaluated. Compound source cases retain their full text until
   explicit expected assertions and evidence discharge them.
3. The source manifest's 60 input hashes are checked before import or coverage
   reconciliation. Definition changes require an explicit scope migration;
   regeneration of a planning file never resets implementation evidence.
4. The core uses Python 3.12 and standard-library reference arithmetic. Optional
   Parquet/DBN readers use pinned dependencies. Optimize only after reference
   parity and a bounded throughput measurement.
5. MBP-1 is the primary futures source. Keep raw payloads, source identity,
   action/side/combined flags, missing clocks and quote association. Trades
   without F_LAST remain trades. Recovered quotes cannot restore lost flow.
6. Actual compute completion determines availability without a second latency
   charge. Historical missing receipts require named assumptions. Versioned
   observations, targets and object geometry cannot rewrite past decisions.
7. NQ/ES tick arithmetic is a reference contract, separate from certification of
   actual historical instrument definitions. All exposures remain flat or one
   outright mini across the account; no copied accounts, micros or partial exits.
8. E0 requires a verified numeric commission/fee input, eligible-date and
   contract/calendar certification. Missing fees block economic execution.
   Trading net and business cash remain separate because target accounting is
   unresolved. Prospective evidence requires future elapsed time.

Implementation status and commands belong in `STATUS.md` and `evidence/`, not in
the generated planning manifests. The whole program remains in scope across
checkpoints; a first working reference is not an economic or completion claim.
