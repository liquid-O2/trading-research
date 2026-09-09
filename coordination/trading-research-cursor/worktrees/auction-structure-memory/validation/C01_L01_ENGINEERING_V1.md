# C01/L01 engineering protocol draft

Status: DRAFT ONLY. No registration, imports, compilation, tests, market-data scans, or execution authorized by this draft. Root review must freeze exact candidate, independent reference, tests, source-disposition map, golden vectors and retained source-preparation bytes first.

## Scope and hypothesis

Establish deterministic C01 range source fidelity and causal L01 object publication for the minimal E0 geometry, while preserving every source alternative and the full four-unit P0–P7 backlog. Passing this batch establishes only named engineering assertions. It does not establish a learned role, source win rate, native E0 cohort, or economic/future result.

Use the preparation report and design draft by exact content hash. The v2 golden contains all27 original named cases with concrete hand-derived clock/event/coverage/geometry or source-registry vectors, plus14 concrete capability/bounds/atomicity/restart/malformed/source-map vectors. No semantic expected-output placeholders remain. Each assertion_kind distinguishes deterministic adapters from source-comparison/dependency gates; a preserved unsupported branch is not claimed to be an implemented numerical model. All237 source obligations remain independently mapped; only explicitly implemented source primitives receive executable coverage. Unpublished formulas, unsupported source claims and richer models receive honest bounded gate/provenance assertions, never invented numerical output.

Version2 preserves the previous draft bytes in /tmp/c01-l01-protocol-draft-v1.md, /tmp/c01-l01-golden-draft-v1.json and /tmp/c01-l01-design-draft-v1.json. All remain unregistered drafts.

## Inputs and independent oracle

Use tiny immutable synthetic trade/coverage/watermark/calendar/definition records. Test candidate against a separately authored literal reference and hand values, including source-specific disagreements. Reference must not import candidate geometry/reducers or call its serializers to calculate expected outputs. Candidate F09 inputs must originate through retained factory publications; do not manually flip private certification flags. Pin foundation input bytes from the first passed F09–F12 baseline.

Register exact output schema and per-field availability. State/time/identity/count/hash comparisons are exact. Relative integer-second fixtures scale by exactly1,000,000,000 into nanoseconds; UTC/local clock strings are fixed expected fixture values. Declared holiday fixtures do not satisfy native CME evidence gates. Prices, widths and ratios use rational arithmetic; no float tolerance may hide anchor or convention errors. Serialize fractions as numerator/positive-denominator pairs. Display and order rounding are downstream and must not change source geometry.

Use the peer-agreed neutral ClockSelection/RangePrimitive port pending root freeze. Current06–09 E0 geometry requires exact supportedH/L; ambiguousO/C or interior order does not block it. PriorE0 full four-reference set requires supportedO/H/L/C, with individually supported references retained for diagnostics. Range-open and width-percent outputs have their own declared field/denominator requirements.

Actual adapter assertions must use F03 named interval fixtures, F09 retained factory publications and F10 ObjectGraph AtomicBatch/candidate/target/checkpoint APIs. Restore on fresh paths from actual persisted foundation state. Stub records are only input oracle data and cannot stand in for certified publications or object-registry integration.

## Assertions

Each golden case has its own planned tests.test_range_locations.RangeLocationTests.test_cl_* ID. Add separately named negative vectors for forged evidence, incomplete support, coarse straddling bars, incompatible domain, ambiguous opening order, conflicting duplicates, fractional tick points, future availability, frozen-cut mutation, malformed restore and unresolved formula activation.

Keep three checks distinct: source table/provenance fidelity, causal arithmetic/lifecycle reference parity, and downstream prediction/economic quality. Source-reported percentages are never expected success probabilities in this engineering batch. Each full source row remains attached to its original page/line proof and specific source disposition. Parent-name or fixture-prefix coverage cannot substitute for source assertions.

## Fault and invariance matrix

Run identical prefixes against full and suffix-deleted future inputs; append delayed/corrected forming trades; compare old and new candidate versions at their actual publication times. Compare restart from retained source/admission history, uninterrupted replay, duplicate delivery and admissible chunk boundaries. Verify source interval alignment, same-clock raw/bar geometry parity, DST and cross-midnight definitions. Preserve all zero-width, incomplete, no-touch, ambiguous and rejected cases.

For relations distinguish shared formation intervals from price overlap/nesting and keep exact parent versions. For location roles distinguish same geometry with later reclaim, open versus EQ, internal continuation without gamma/edge-first, and wide internal→edge versus compressed/purged internal→extension. These path proposals are not a hardcoded prediction oracle.

## Bounded resource proposal

One isolated offline worker batch after registration. Proposed aggregate CPU soft180s/hard190s, wall240s, bounded logs/artifacts and supervisor accounting as in the established foundation workflow, subject to root approval of the concrete manifest. No automatic reruns or expanded search. On error retain full result/evidence and register repair according to the established workflow.

Synthetic scale cases must freeze exact event/window/version counts, small enough for literal reference. Record CPU/wall/RSS/checkpoint bytes and algorithmic work counters. Measure work actually performed; report retained-source reconstruction and consumer integration separately. No claimed live p95 without telemetry.

## Acceptance and reporting

All mandatory named assertions must pass with zero errors/failures/skips, exact reference parity, explicit ambiguities and bounded resource evidence. Recorder verifies independently retained result summary, assertion inventory and exact input hashes before attachment. Any planned/source-only/dependency-gated item remains visibly unpassed. Freeze all required bytes before first import; drafts do not satisfy this requirement.

Next gate after engineering remains admitted raw NQ selection/formation/prior-RTH data, V01/V02 labels and folds, full E0 action/order/account integration, followed by registered statistical/economic comparisons. Keep the13-source-object E0 geometry distinct from general L01 range-open and richer source alternatives.


## Final frozen adapter contract for registration

This final section supersedes earlier draft API and policy proposals. Root approved exact contract; no implementation or execution until registration.

{
  "public_api_contract": {
    "status": "root_approved_exact_contract_ready_for_registration",
    "neutral_module": "trading_research.foundations.range_primitives",
    "adapter_module": "trading_research.context.range_adapter",
    "ClockSelection": {
      "fields": {
        "instrument": "object_graph.Instrument",
        "window": "calendar.FormationWindow",
        "session": "calendar.Session",
        "selected_at": "int ns",
        "predecessor_of_session_version": "str|None",
        "interval_graph": "intervals.IntervalGraph",
        "named_interval": "intervals.NamedInterval"
      },
      "properties": [
        "version_id:str (content identity)",
        "formation_start/end from window",
        "calendar/source/timezone versions from session",
        "raw lifetime and tick size from instrument"
      ],
      "contract": "Resolve actual Calendar at cut, validate actual available IntervalGraph and named node known at cut, exactly one span and trading_dates==(requested date,), derive FormationWindow from this span. Retain graph and node content versions. Raw instrument root binding and lifetime required. Calendar.resolve session is separately retained; 06\u201309 is not required to be within RTH. Compile source WallRule using byte-versioned zone_version for America/New_York or Etc/GMT+5; never treat a label as an exact UTC clock. M12 attests prior relationship separately."
    },
    "FieldSupport": {
      "fields": {
        "field": "one of open/high/low/close",
        "status": "observed|partial|ambiguous|empty|unavailable",
        "reason": "nonempty str",
        "source_versions": "tuple[str,...]"
      },
      "contract": "observed means complete exact support for that requested field; partial/ambiguous/empty/unavailable cannot be silently cast to observed."
    },
    "RangePrimitive": {
      "fields": {
        "id": "stable source clock/raw instrument/reset identity",
        "version_id": "content identity",
        "selection": "ClockSelection",
        "publication_version_id": "str",
        "source_definition_id": "str",
        "reset_epoch": "str",
        "revision": "int",
        "supersedes": "str|None",
        "observation_cut": "int ns",
        "minimum_known_at": "int ns",
        "published_at": "int ns",
        "complete_observation_at": "int ns|None",
        "open_ticks": "int|None",
        "high_ticks": "int|None",
        "low_ticks": "int|None",
        "close_ticks": "int|None",
        "observed_ohlc": "tuple[int|None,int|None,int|None,int|None]",
        "first_event_at": "int ns|None",
        "last_event_at": "int ns|None",
        "coverage_complete": "bool",
        "observed_duration": "int ns",
        "coverage_version": "str",
        "watermark_version": "str|None",
        "source_event_ids": "tuple[str,...]",
        "source_content_versions": "tuple[str,...]",
        "correction_ids": "tuple[str,...]",
        "field_support": "tuple[FieldSupport,...] ordered O,H,L,C",
        "status": "provisional|final|incomplete|empty"
      },
      "contract": "No detached primitive certifies itself. Adapter returns typed unsupported diagnostics, with supported fields only in primary OHLC and first/last observed prices only in observed_ohlc. Missing opening coverage returns open_ticks=None and support reason incomplete_open even when first observed price exists. Private factory receipt/capability refers to actual retained F09 publication; it is not a caller boolean and is re-established from restored engine before registry publication. Raw lifetime comes from selection.instrument; horizon/expiry remain explicit downstream definition and registry policy, never inferred from source post."
    },
    "RangeRegistryLinks": {
      "fields": {
        "source_id": "s: namespace",
        "evidence_version_id": "e: namespace",
        "anchor_id": "a: namespace",
        "anchor_version_id": "av: namespace",
        "primitive_version": "str",
        "registry_revision": "int >=0",
        "evidence_predecessor": "str|None",
        "anchor_predecessor": "str|None"
      },
      "contract": "Source and anchor IDs derive stable clock identity. Evidence and anchor version IDs derive primitive content plus explicit independent registry revision/predecessors. Initial links revision 0 even if F09 bar revision is greater; next links require previous exact links. Writer verifies source identity and actual predecessor. Retry reuses identical links."
    },
    "RangePublicationReceipt": {
      "fields": {
        "batch_id": "str",
        "batch_version": "str",
        "committed_head": "str",
        "changed": "bool",
        "primitive_versions": "tuple[str,...]",
        "object_versions": "tuple[str,...]",
        "known_at": "int ns",
        "registry_links": "tuple[RangeRegistryLinks,...]"
      },
      "contract": "Only returned after actual ObjectGraph atomic commit succeeds. No partial successful receipt on rejected batch."
    },
    "functions": [
      {
        "signature": "select_clock(*, calendar: Calendar, interval_graph: IntervalGraph, interval_name: str, trading_date: date, instrument_root: str, instrument: Instrument, cut: int) -> ClockSelection",
        "contract": "Resolve actual Calendar at cut, validate actual available IntervalGraph and named node known at cut, exactly one span and trading_dates==(requested date,), derive FormationWindow from this span. Retain graph and node content versions. Raw instrument root binding and lifetime required. Calendar.resolve session is separately retained; 06\u201309 is not required to be within RTH. Compile source WallRule using byte-versioned zone_version for America/New_York or Etc/GMT+5; never treat a label as an exact UTC clock. M12 attests prior relationship separately."
      },
      {
        "signature": "primitive_from_shared_bar(*, selection: ClockSelection, engine: SharedBarEngine, publication_version_id: str, cut: int) -> RangePrimitive",
        "contract": "Look up exact retained factory publication in actual engine.publications. Require publication.available(cut,final_only=False), actual certification and compatible timekind/domain/interval/calendar/reset. Never accepts arbitrary bar argument. Produce provisional/incomplete/empty diagnostics without promoting unsupported values. Complete H/L support does not depend on O/C/interior order. Published finality and coverage are checked separately. One selected primitive does not select a raw contract or calendar predecessor. Resolve the exact immutable bar/request pair through engine.window_publication; never copy or scan checkpoint history. Derive endpoint coverage from request.coverage.observed_intervals, full H/L from complete coverage/history/priced volume and finality; order ambiguity affects only fields whose endpoint price is ambiguous."
      },
      {
        "signature": "primitive_registry_links(primitive: RangePrimitive, *, previous: RangeRegistryLinks | None = None) -> RangeRegistryLinks",
        "contract": "Source and anchor IDs derive stable clock identity. Evidence and anchor version IDs derive primitive content plus explicit independent registry revision/predecessors. Initial links revision 0 even if F09 bar revision is greater; next links require previous exact links. Writer verifies source identity and actual predecessor. Retry reuses identical links."
      },
      {
        "signature": "publish_range_batch(*, graph: ObjectGraph, primitives: tuple[RangePrimitive, ...], registry_links: tuple[RangeRegistryLinks, ...], derived_members: tuple[DerivedRangeMember, ...], batch_id: str, batch_sequence: int, clocks: PublicationClock, expected_head: str | None) -> RangePublicationReceipt",
        "contract": "Revalidate actual factory provenance and scalar projection, one exact supplied link per primitive, independent revision/predecessor and per-formula field requirements. Materialize EvidenceVersion/AnchorVersion at the original source availability; commit these and typed derived members through actual AtomicBatch with caller-frozen sequence and expected_head. Reattempts reuse exact sequence/links/recipe and actual F10 idempotence. No batch_sequence default. Future evidence, forged links or insufficient field activation rejects entire batch; no successful partial receipt. Preserve original F09 publication/revision/correction content in primitive metadata and evidence content_digest; registry ordinal is independent. Existing F10 handles candidate cuts, visits, targets and aliases. Before mutation validate actual retained predecessor/source identity and causal availability. A caller-chosen previous receipt cannot roll a source stream backward or skip a retained correction. At publication cut reconcile intervening retained F09 source versions/correction lineage with the selected primitive; any unaccounted known correction rejects activation. Historical publication remains queried through original cuts rather than republished as current."
      }
    ],
    "anchor_revision_rule": "ROOT FROZEN: BirthKey.anchors=() and stable source_origins plus generator discriminator; each ObjectRevision binds current exact evidence and parent object versions. Emit current AnchorVersion plus explicit SHARED_EVIDENCE relation metadata (anchor endpoints cannot be ancestry PARENT endpoints). A relation whose endpoints change gets a new relation identity. Provisional anchor end is observed prefix <= confirmation, never future formation end. Existing target geometry and original frozen candidate versions are immutable.",
    "f09_minimal_extension": {
      "owner": "/root/f04_scheduler_tests after registration only",
      "signature": "SharedBarEngine.window_publication(publication_version_id: str) -> tuple[SharedBar, WindowRequest]",
      "returns": "actual retained certified time SharedBar and exact frozen WindowRequest used to publish it",
      "implementation_plan": "Maintain version-indexed private immutable pair on successful publish_window; O(1) lookup, O(publications) retained references bounded by max_publications. Restore rebuilds index through the existing verified publication replay; checkpoint schema unchanged. No whole-history scan, no checkpoint serialization per primitive. Unknown or activity-result version raises DependencyUnavailable; malformed ID raises ContractError. No unregistered candidate changes.",
      "assertions": [
        "returned bar identity equals actual publication and record matches expected retained history",
        "request definition/start/end/coverage version/watermark match bar; source known times <= frozen observation cut",
        "request coverage spans preserved exactly, including missing opening segment",
        "frozen return cannot mutate factory state",
        "restored pair content equals uninterrupted pair after correction",
        "lookup work does not grow with retained history; explicit lookup counters/assertions and retained-reference bound",
        "altered retained request/source mismatch rejects lookup or restore with IntegrityError; no caller-attested provenance boolean"
      ]
    },
    "pending_writer_details": {
      "status": "Root approved exact concrete links and wrapper signatures; no remaining API design gap.",
      "revision_metadata": "Full immutable primitive payload remains the typed receipt; evidence.content_digest binds it. F10 EvidenceVersion has no arbitrary metadata field. AnchorVersion payload and explicit relations use existing legal F10 fields only."
    },
    "DerivedRangeMember": {
      "fields": {
        "member": "ObjectRevision | RelationVersion",
        "requirements": "tuple[tuple[primitive_version: str, required_fields: tuple[str,...]], ...]"
      },
      "contract": "Every derived ObjectRevision has exact required field bindings for its formula and complete source/parent closure. Allowed fields O/H/L/C in canonical names open/high/low/close, nonempty per primitive. Writer rejects eligible activation unless each named field is observed in that certified primitive. Relations have empty requirements and bind checked exact endpoints; do not grant eligibility. Definition-specific field bindings must equal registered formula dependency table, not arbitrary caller under-declaration."
    }
  },
  "normalization_policy": {
    "width_price_percent": "W / available nonzero range open; exact rational. Unsupported or zero O leaves percent unavailable only, not H/L abstention.",
    "width_prior_volatility": "positive preceding completed available scale at frozen cut; missing/nonpositive/unavailable leaves ratio unavailable; no learned fallback."
  },
  "upstream_full_static_review": {
    "calendar.py": "entire file",
    "intervals.py": "entire file 1\u2013421",
    "multiresolution.py": "entire file 1\u20131488",
    "object_graph.py": "entire file 1\u20131990",
    "findings": [
      "F10 checkpoints are mapping manifests over durable SQLite journal, not standalone snapshot bytes; restore(path,definition,checkpoint) verifies exact prefix and suffix replay. Fixture copies actual journal for a fresh path.",
      "F10 current dirty support blocks previous_valid fallback; old immutable asof cursor/target remain original.",
      "F10 complete candidate/lineage and hot capacity overflow uses DependencyUnavailable; adapter-owned finite configuration bounds may use ContractError.",
      "No production import, compile, implementation edit or test executed during static design review."
    ]
  },
  "extra_vector_normalizer": {
    "origin": "Fourteen added cross-cut engineering requirements introduced in v2 root adapter review; not part of original 27 prepared hand cases, not retrospective preparation credit.",
    "original_prepared_case_count": 27,
    "extra_cross_cut_count": 14,
    "total_registered_vector_count": 41,
    "mapping": [
      {
        "vector_id": "CL-X01-capabilities",
        "cross_cut_requirement_id": "CL-CROSS-01-FIELD-CAPABILITY",
        "requirement": "Exact field support and missing opening coverage",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X02-interior-order",
        "cross_cut_requirement_id": "CL-CROSS-02-ENDPOINT-ORDER",
        "requirement": "Interior order independence and endpoint ambiguity",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X03-window-bound",
        "cross_cut_requirement_id": "CL-CROSS-03-WINDOW-ADMISSION-BOUND",
        "requirement": "Finite simultaneous formation admission",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X04-retention-bound",
        "cross_cut_requirement_id": "CL-CROSS-04-RETENTION-BOUND",
        "requirement": "Bounded retained source/object lineage",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X05-atomic-batch",
        "cross_cut_requirement_id": "CL-CROSS-05-F10-ATOMICITY",
        "requirement": "No partial source/geometry publication",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X06-restart",
        "cross_cut_requirement_id": "CL-CROSS-06-RESTORE-CORRECTION",
        "requirement": "Real F09/F10 replay and immutable historical target",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X07-malformed-scalar",
        "cross_cut_requirement_id": "CL-CROSS-07-EXACT-SCALAR",
        "requirement": "Reject bool/float/NaN versus exact rational ticks",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X08-forged-or-wrong-bar",
        "cross_cut_requirement_id": "CL-CROSS-08-FACTORY-PROVENANCE",
        "requirement": "Actual factory certification and domain alignment",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X09-duplicate-and-conflict",
        "cross_cut_requirement_id": "CL-CROSS-09-IDEMPOTENT-PUBLICATION",
        "requirement": "Exact retry and conflicting replay rejection",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X10-frozen-cut",
        "cross_cut_requirement_id": "CL-CROSS-10-FROZEN-CUT",
        "requirement": "Future publication exclusion and dirty current support",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X11-fractional-point",
        "cross_cut_requirement_id": "CL-CROSS-11-FRACTIONAL-GEOMETRY",
        "requirement": "Exact fractional levels without rounding",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X12-malformed-restore",
        "cross_cut_requirement_id": "CL-CROSS-12-RESTORE-INTEGRITY",
        "requirement": "Reject corrupted retained source/graph checkpoint",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X13-source-list-completeness",
        "cross_cut_requirement_id": "CL-CROSS-13-SOURCE-OBLIGATION-DENOMINATOR",
        "requirement": "Preserve all237 distinct source obligations",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      },
      {
        "vector_id": "CL-X14-relation-bound",
        "cross_cut_requirement_id": "CL-CROSS-14-RELATION-CAPACITY",
        "requirement": "No silent relation pruning or identity merge",
        "original_prepared_case_id": null,
        "introduced_in": "v2 adapter review",
        "source_row_closure_granted": false
      }
    ]
  }
}
