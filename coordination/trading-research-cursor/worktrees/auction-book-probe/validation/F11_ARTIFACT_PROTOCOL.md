# F11 semantic artifacts and actual input lineage protocol — preregistered engineering contract

Status: Preregistered engineering contract. Root has reviewed the complete design,
all 24 hand-reasoned golden cases and source consequences. The generic registrar
publishes these exact bytes at `validation/F11_ARTIFACT_PROTOCOL.md` and
`tests/golden/f11-artifacts.json` before dependent implementation or tests.

## Binding scope and artifacts

Cover the feasible deterministic engineering core of F11, SR-F11, UP-F11 and
F11.INPUT_AUDIT. Read the complete typed records, API, error, clock, stage,
publication, bounds and ownership contracts in `reports/f11-design.json`, and
all F11-01..F11-24 inputs/expected outcomes in `/tmp/f11-golden-draft.json`.
The final registration pins all three artifacts with the unchanged source review
`reports/f11-source-preparation.json`.

The source review covers exactly DTM-A01, DTM-A17, JCV-U06, CEX-27, CRL-17,
CRL-20, DRF-A07, DRF-A26, EXT-031 and TECH-10. DTM-A17 resolves the parent’s
unnamed DTM validation reference. Exact prior-clause reuse and fresh original
reading are distinguished there. Do not broaden the claim to unread sources,
missing old exports/replies or excluded archive details.

Preserve the generic ArtifactStore/ArtifactRef/raw-byte API, trial/ledger and
partition/cohort stores, and existing predictor algorithms. Add a bounded
semantic manifest/commit layer and narrow validated input/fit adapters. Root
owns runtime/ports.py and verify.py. All four foundation registrations must
precede shared-source edits; F11 implementation waits for root’s release.

## Fixed semantic and causal contract

- Semantic identity binds namespace, kind, logical identity, typed schema/unit,
  payload and definition bytes, exact source/acquisition versions, execution
  code/configuration/numerical state, row/fit/prediction evidence and complete
  dependency slots. Identical numeric content with new lineage changes the
  semantic version. Physical blob deduplication does not merge label, OOF and
  final-prediction roles. Names never substitute for content or trial identity.
- Configuration, records, row lineage, actual-read declarations and fit evidence
  are immutable. Validate exact types, canonical finite data, int64 ns clocks,
  units, namespaces and complete bounded closure before publication and again
  on restore. Empty-column provenance edges remain dependencies. Missing nodes,
  cycles, duplicate slots, conflicting IDs and undeclared extra roots fail.
- External observations must be known/valid by the frozen decision cut.
  Predictions retain actual completion and their original target definition,
  unit and start/end. Availability is max(required input/effect clocks, actual
  completion), with no duplicate modeled compute charge. Derived same-cut
  inputs may complete by a named assembly time only if all external inputs
  were frozen by the cut. No later receipt/census/rebuild projects backward or
  restarts an endpoint. Audit history is separate from live usability.
- Re-derive fold membership and purge reasons from retained typed population and
  declared boundaries. Whole correlated date groups, training window, label
  maturity and dependency intervals remain binding even for direct constructors
  and restored JSON. For OOF admission, validate every model/scaler/calibrator
  ancestor’s retained fit population, permitted predeclared fold route, exact
  target, fit completion and requested sample/date exclusion. Supplied artifacts
  cannot authorize their own fold routes. Labels use fit-label/audit views;
  final predictions cannot replace OOF downstream training inputs.
- Actual-read sessions pin declared order, required/optional fields, cut,
  assembly time, purpose, target and fold route. Read only verified committed
  row/column bindings. Seal only after required reads and explicit permitted
  optional omissions reconcile; reject undeclared, future, forbidden-role and
  incompatible reads. Repeated identical reads are idempotent. Zero-effect and
  diagnostic reads remain lineage. Actual model/transform/calibrator bytes and
  column order must match admitted state. Uninstrumented arbitrary/native reads
  remain outside certification.

## Atomic success, restart and failed work

A successful commit names the exact roots and complete validated closure. Stage
bounded immutable blobs and a canonical manifest, synchronize them, then publish
one non-overwriting commit-key pointer. Pointer filenames use key hashes. Only
that complete pointer makes the new closure available; reads never fall back to
a latest-name or stale cache. Same-key identical retries are idempotent; same
key with different content fails. Verify configuration, canonical envelopes,
content hashes/sizes and typed admission before returning any restored value.
Bound bytes before reading them, preserving the generic blob API unchanged.

F11-18 uses an actual supervised child process after registration. Abrupt exit23
after fsynced blobs/manifest but before the pointer leaves the new commit
unavailable; exit24 immediately after the pointer leaves the complete commit
readable and repeatable. Old commits remain unchanged in both cases. These are
local process-death checks, not remote exactly-once or host/power-loss claims.

Failed/interrupted run records are immutable audit evidence linked to existing
TrialRegistry attempts, not successful input commits. Orphaned bytes remain in
resource accounting but cannot supply a consumer. The supervisor records
interruption; unknown process usage is reservation-charged rather than zero.
There is no silent evidence eviction, original modification or automatic cleanup.

## Independent comparison and acceptance

Retain three stages: existing limited flat/raw-store behavior; corrected
independent full-closure validation/rebuild; typed DAG plus indexed affected-only
rebuild. The literal reference uses primitive dictionaries/tuples and independent
standard-library JSON/hash/rational operations. It must not import or call
candidate constructors, store, closure, audit or OOF helpers to generate expected
outputs. The golden values, clocks, sets, errors and alias relationships are
pre-authored. Aliases denote intended nodes, not invented SHA values.

Cover every F11-01..F11-24 case with named assertions. Acceptance requires exact
agreement on semantic identity relationships, closure/roles, clocks, OOF/read
admission, restored state, errors and hand-reasoned rational outputs; zero partial
visibility or unexplained drift. Golden F11-20 fixes the full-versus-incremental
graph arithmetic and counts. Record rebuilt/reused IDs, first-change paths,
source reads, arithmetic, validated nodes/edges, payload/manifest/store bytes and
full construction/restore costs. Any toy timing uses actual wall/CPU/RSS and
makes no native-cohort speed claim. F11-22 separately checks decision consequence
when values are within numerical tolerance but cross a decision threshold.

Inclusive default ceilings are: 256 nodes/commit, 1024 edges/commit, depth32
(count nodes on the longest root-to-source path), 4096 rows/node, 128 columns/row,
1 MiB node payload, 2 MiB encoded manifest, 32 MiB unique store blob payload bytes
including staging/orphans, and 256 successful commits. Report manifest/pointer/
configuration bytes separately. Boundary cases may use smaller explicitly fixed
ceilings along the same admission paths plus exact defaults/byte boundaries;
never disable another limit, truncate or evict to get a pass.

Malformed/forbidden declarations, missing nodes in a purported complete graph,
conflicting commit keys and bounds violations raise ContractError. Missing
successful commits or genuinely absent required committed inputs and expired
inference raise DependencyUnavailable. Existing bytes/size/hash/canonical/
configuration mismatch raises IntegrityError. Immutable assignment/deletion is
AttributeError (including FrozenInstanceError); byte item mutation is TypeError.
Detached decoded copies may change without changing retained immutable state.

## Registration, review and remaining gates

Root reviews/freezes the final design/protocol/golden/source hashes first. After
implementation, complete one static review of candidate, independent reference,
all assertions and direct callers; collect findings together and make one
consolidated repair before the supervised registered suite. Retain failed
attempts, exact code/source snapshots, outputs and actual resources. No separate
unregistered F11 test/search family is allowed.

Proposed ceiling pending root’s final combined protocol: three attempts, 600
CPU seconds total, 180 soft/190 hard CPU seconds, 240 wall seconds and 4 GiB
address space per attempt. Shared worker use has one physical execution identity
and is conservatively charged to each participating registered family.

Native/large cohorts, private inputs, full consumer coverage, trained predictors,
chronological calibration quality, all source variants, held-out forecast or
economic gain, E0–E5 account policy and actual future receipt capture remain
separate gates. Synthetic OOF/fold checks certify no real cohort or unseen
period. TECH-10 requires preserving search history; DSR estimation remains
V03/V04. EXT-031 adds no vendor connection/purchase, calibrated freshness policy
or historical velocity reconstruction. Passing this finite family closes none
of the broader P0–P7 or economic requirements.

## Exact added runtime declaration

{
  "id": "F11.AUDIT",
  "component": "F11",
  "stage": 0,
  "schema": "ArtifactClosure.v1",
  "fields": [
    "commit",
    "roots",
    "semantic_ids",
    "actual_reads",
    "fit_closure",
    "target",
    "clocks",
    "invalidation",
    "errors"
  ],
  "dependencies": [],
  "lane": "offline",
  "learned": false,
  "target": null,
  "capabilities": []
}

F11.FROZEN retains FrozenArtifacts.v1 with models, transforms, calibrators and training_closure fields. The new offline audit declaration has no automatic consumer activation; typed resolver/model adapters bind actual content and permissible read/fit closure. Existing unadapted readers gain no certification from a port declaration. Runtime bindings must retain implementation, definition, parameter, input-schema and verification identities.
