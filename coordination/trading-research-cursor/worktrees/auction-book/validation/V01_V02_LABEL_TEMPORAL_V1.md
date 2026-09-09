# V01/V02 preparation and finite engineering protocol draft

Status: proposed for root review/registration. Source preparation is complete; this file freezes no experiment and reports no test pass. The 64 hand-derived vectors are in `/tmp/v01-v02-golden-draft.json`; original reading proofs, all 373 individual route consequences and exact current source identities are in `reports/v01-v02-source-preparation.json`.

Scope: V01, V01.LABEL_COVERAGE, V02 and V02.LINEAGE; all four ten-part/child contracts and all 32 P0–P7 records remain represented. This batch implements finite deterministic label/population/fold/lineage contracts, not every downstream price, OI, profile, option, policy or learned specialist. Routed source variants remain individual records; source-derived percentages are not golden truths or model priors. Numeric case values are synthetic and hand derived.

## Ownership and compatibility

Owned existing files are `research/labels.py`, `research/object_labels.py`, `research/folds.py`, and their direct `models.py`/`calibration.py` callers. Proposed new files are `research/label_ledger.py`, `research/temporal_folds.py`, `references/v01_v02_literal.py`, and `tests/test_v01_v02.py`. Any additions to existing label/fold tests will preserve prior semantics and add explicit regression coverage. Parent/delegated B00.6 owner owns `research/decision_contracts.py`, its independent reference and tests, and the six B00.6 contracts. This agent additionally owns the narrow `operations/artifact_graph.py` temporal adapter after root registration.

Preserve `ObjectTarget`, `ExactPoint`, `reference_object_label`, and its `fixed_end`, `reach_status`, `departure`, `contact_at`, `contact_price`, `first_barrier_at` and excursion result fields. Preserve `PathPoint`, `ObservationWindow`, `PathLabel`, `reference_path_label`, `Sample`, `Fold`, `FittedArtifact`, `chronological_fold`, `validate_fold_population` and `validate_oof` existing signatures. Additional optional evidence is adjacent or additive, never a silent change of end time or observation process. Tighten malformed-input validation; malformed inputs do not have compatibility guarantees.

Root's fixed-end case uses original cut0/end10/contact9/favorable11 and a separately contracted cut9/end19 target. The original target cannot consume event11; the second may. Root will use the existing object-label path. This batch does not reproduce reward, standing-venue BBO, geometry or evidence-assimilation algorithms.

## Proposed label contract

`LabelDefinition` identifies kind, actual target cut/end, observation process, frozen object/geometry version where applicable, barrier/side convention, shared endpoint/report ID, subsequent policy and simulator identity where applicable, and target transformation. No generic untyped scalar can stand in for a path, OI count or policy reward.

`CandidateRecord` identifies generator event, decision set, original candidate/object version, date, source episode, sampling frame, created/known times and decision disposition. `SamplingFrame` is one of clock, source episode, object birth, contact or policy trajectory. Inclusion probability is an exact rational in (0,1] only when supplied by a defined sampling design; unknown stays unsupported. Equal-date/equal-episode weights are separate declared estimands, not claimed sampling probabilities.

`ObservationEvidence` retains actual observed end, certification/maturity, gaps, source-order capability, input version and any explicitly certified partial facts. `LabelOutcome` retains definition/candidate linkage, complete/pending/censored/ambiguous/invalid/not-applicable state, typed payload, endpoint ownership and revision linkage. The complete horizon's outcome is never zero-filled during an outage. Earlier certified contact can be retained as a partial fact even when full departure is censored. This richer record does not turn the legacy full-window result into an unannounced partial result.

`LabelLedger` appends immutable records, rejects same-ID/different-payload reuse, supports exact checkpoint/restore through existing content-addressed artifacts, and reconciles expected generator/candidate IDs against decisions and required outcome slots. An invalid/censored/untraded row remains in the population with a reason. Distinct coincident objects retain two target rows and one declared co-contact/event support group.

Price adapters call the preserved path/object label kernels. An OI endpoint adapter records continuing-contract report deltas, revisions, expiry terminal state and missing publication separately; it does not infer intraday dealer holdings or disappearance-as-zero. A policy-value adapter records the complete policy/fill/fee/account scenario identity and externally produced outcome provenance; actual reward composition remains owned by root/P. Future profile/board label definitions are registered as distinct kinds with their observational limits; this batch does not build profile or option engines.

Contact-origin manifests retain original candidate cut, actual contact/landmark cut and original end separately. A new prediction with contact+h must use a new definition/target ID. Pre-contact input admission excludes actual future arrival features. Later observation never changes earlier geometry, sampling frame, endpoint or source evidence.

## Proposed temporal fold contract

Keep basic grouped forward folds and their exact complete-population validation. Add the adjacent versioned `TemporalSampleV1` that explicitly distinguishes target end, label maturity, raw historical lookback intervals, forbidden outcome/fitted-state dependency intervals, parent/endpoint groups and phase role. A `FitStage` declares train/tune/calibrate/outer/future ownership, fit cut, evaluation block, rolling/expanding window and exact embargo rule. An `OOFEdge` declares the required producer stage and every downstream training row requiring an earlier OOF prediction.

A literal compiler enumerates each row/stage/edge and records eligibility or exact exclusion path. The candidate compiler may index sorted intervals, but must return identical membership, reasons and required OOF row coverage. Shared causal past observations remain legal. Every learned role—generator/discovery, scaler, residual baseline, encoder, expert, gate, calibrator and auxiliary head—participates in closure. Selection using outer/future labels cannot be relabeled as development state. Compare a deliberately conservative plan with exact legal-overlap use while leaving evaluation dates and rows unchanged.

The existing F11 committed graph already verifies actual original sample/target/cut, retained population, reads, fit completion, routes and supplied model state. Reuse that verifier, not a second metadata-only substitute. Direct legacy `FittedArtifact` checking is an exclusion check over declarations, not a claim of actual training-read evidence. New proof-aware plans may be consumed only where the complete plan/evidence is verified; absence of evidence fails closed.

Actual narrow F11 integration is selected and owned by this agent after registration. The exact new versioned records, byte-preserving legacy ABI, actual committed/restore path and end10/dependency15 vectors are specified in `/tmp/v01-v02-temporal-f11-schema-draft.md`. Existing serialized dataclasses gain no fields. New discriminators carry temporal evidence; F11 validates the plan and compares labels to actual target end. Advanced plans must be genuinely servable and restored, not left as disconnected schemas.

## Reference, cases and execution policy

The golden draft contains V01-01…V01-36 and V02-01…V02-28, with concrete inputs, expected statuses/numbers, provenance and API ownership. Independent literal arithmetic/row enumeration must be authored without importing candidate modules. Candidate tests assert both the declared result and independent reference agreement; do not generate expected outputs by running the candidate. References do not implement root's six decision-contract mechanisms.

Required distinctions include coarse order versus exact sequence, discrete gap versus contact, equality/end boundaries, no event versus missing observation, partial fact versus full-horizon censor, policy nonfill, expiry versus zero OI, revisions, all-candidate reconciliation, sampling/endpoint/co-contact dependence, maturity, date grouping, legal past lookback, every indirect learned role, explicit upstream routes, missing OOF rows, forbidden outer selection and checkpoint/cache identity.

Use exact integers/Fractions, deterministic IDs and predeclared order where observed. Unknown order uses compatible outcomes/bounds, not arbitrary stable sorting interpreted as market order. Same-timestamp source sequence is only evidentiary when its order capability is true. Legacy carried-mark terminal semantics stay documented as a declared process; future endpoints must not acquire a more precise last-trade/venue mark interpretation by accident.

After root registration, execution uses only the shared root attempt: 180 CPU seconds, 190 CPU seconds hard limit, 4 GiB RAM and 240 wall seconds. No private120CPU/300wall run or extra private attempt. The shared run includes new and legacy committed/restored F11 integration. Repairs require root registered shared policy. No imports, compilation, unit tests, learner training, market scans or strategy experiments were run during preparation.

## Phase dispositions

P0: prepared source/definition/variant/clock/population and draft contract, awaiting registration. P1: 64 proposed finite exact cases, no pass claim. P2: literal versus candidate fidelity and exact/conservative support comparison proposed; learner quality remains downstream work. P3: exact service coverage/support counts; conditional predictive calibration requires later eligible data and complete OOF chain. P4: legacy/simple versus expanded ledger and conservative versus exact fold comparisons proposed, with information and population changes declared. P5: root B00.6 and direct caller integrations proposed; no alpha requirement for deterministic bookkeeping. P6: complete one-account/one-mini economics remains pending authorized full chain/cohort, not inferred from synthetic correctness. P7: synthetic prefix/revision/restart proposed; actual prospective receipt/future evidence remains separate and pending.

No complete-unit, empirical improvement, source reproduction, profitability or future-support claim follows from this batch. Missing originals and unavailable observation mechanisms have exact dispositions in the source report.

## Final fixture and capacity reconciliation

The golden `fixture_defaults` freezes exact constructor clocks, Ticks/Fraction conversion, source-order capability, observation certification/gaps, side/barriers and Sample/Fold defaults. Explicit cases override those values. V01-14 retains actual contact-point evidence before gap[5,7); V01-28 declares report boundary25 and query statuses; V02-07 builds actual fitted-state→heldout-label dependencies through F11 commit validation.

The golden `finite_limits` freezes configurable positive integer caps: ledger candidates4096, definitions1024, outcomes8192, temporal population4096, per-sample dependencies64, total dependencies16384, stages64, OOF edges4096, parent groups64, ID UTF8 bytes256, payload bytes65536, checkpoint bytes2097152, nesting depth32. Its same-ID variants exercise exact capacity and one-over with small supplied limits; rejection leaves prior bytes unchanged. Bounds precede allocation/append/hash/decode and never truncate. No additional case IDs or source-credit claims are introduced.

Before editing operations/artifact_graph.py, implementation must statically read its entire then-current contents. Earlier range reads do not satisfy that prerequisite. The old source proof reuse is preserved and its80 embedded records were compared exactly to the pinned current copy with zero metadata changes; this is explicitly reuse, not a reread.

All373 independent source-consequence clauses remain separately mapped in implementation disposition output. Each clause receives exact named case assertions only for mechanisms covered by this finite service, with precise source-specific remaining mechanism/evidence otherwise. Registry presence or a generic V01/V02 prefix does not assert numerical source-model coverage.
