# Tape and source-assembly integration contract

This note records the frozen integration boundary exercised before any evaluation replay. The checks use synthetic native fixtures and the frozen candidate registry; they do not inspect evaluation outcomes.

## Bar rules that consume tape-derived state

`SAINT-AMT` five-minute delta is the sum of the five exact one-minute tape buckets in the action or retest candle. Each bucket must have the same instrument, a reconciliation row with `matched=true`, and `known_at` no later than that candle's close. A missing or unknown bucket makes the relevant comparison unknown; a bucket first known after the close is rejected rather than backdated. The initial opportunity is invariant to tape observations that arrive after its `available_at`.

`SAINT-AMT/failed_auction_return`, `SAINT-AMT/poc_traversal`, and `KEANI-OPEN-ABOVE-VALUE/source_long` admit a supplied prior profile only when it identifies the same instrument and exact prior-weekday RTH interval, session date, profile kind, snapshot, formation interval, `as_of`, and `known_at`. The opening rule additionally requires its frozen VA70 configuration: fraction `0.70`, contiguous larger-adjacent expansion with both levels on a volume tie, and the lowest-price POC tie rule. Missing required profile values remain an observed population with an unknown endpoint where the rule defines a clock-based opening population; a foreign, stale, late, or differently configured profile is rejected.

For bar opportunities, `BarMarket.source_assembly` recomputes source evidence from immutable native locators through the opportunity's decision prefix. It does not include later outcome bars. Replay endpoints are checked separately through an accepted native `O004` object.

## Exact M09 evaluator result

`m09_research_comparison(...)` returns one dictionary with exactly these top-level fields before the runner adds job fields:

```text
schema, evidence_mode, faithful_eligible, rule_id, registry_sha256,
observation_unit, transport_observation_unit, instrument_id,
zones, records, ambiguities,
ambiguous_formation_batch_count, ambiguous_formation_event_count,
physical_member_count, coverage_ok
```

`schema` is `phase1-m09-research-comparison-v1`, `evidence_mode` is `research_comparison`, and `faithful_eligible` is always `false`. Each `zones[]` row has:

```text
zone_id, instrument_id, aggressor, side, low, high,
formed_at, known_at, expires_at, formation_event_ids,
immutable, return_count
```

Each `records[]` row initially has exactly `opportunity` and `replay`. The opportunity is the validated `Opportunity.to_dict()` shape:

```text
opportunity_id, rule_id, method_id, branch, partition_id,
instrument_id, session_date, side,
occurrence_start, occurrence_end, available_at,
reference_id, reference_known_at, reference, trigger, expiry_at,
assumption_ids, registry_sha256, evidence_mode, observation_unit,
actual_selection, actual_attempt, order_id, actual_fill
```

The last four fields are always null. `reference.formation_event_ids` contains the two immutable physical executions that formed the zone, and `reference.formed_at` is the second execution's event clock. `trigger.event_id` identifies the return execution. When multiple return executions share a timestamp without an exchange sequence, `trigger.member_event_ids` contains the complete selected touch batch and the ambiguity is retained.

The replay is the validated `ReplayResult.to_dict()` shape:

```text
opportunity_id, verdict, completed_at, endpoint, reason,
censored, ambiguous, selected_signal_at, source_method_verdict,
faithful_disagreements, timing_violations, proxy_as_faithful
```

After source assembly, `execute_m09` adds `source_assembly` (`manifest` plus `result`) and `native_tape_evidence_sha256` to each record, replaces `source_method_verdict` with the assembled source-method verdict, and adds `population_holes` and `search_executed` to the comparison result.

## M09 decision-prefix native assembly

`assemble_m09(...)` returns an `AssembledEpisode`. It reconstructs one `O098` object from the exact two `reference.formation_event_ids` and the exact return-touch member or members. Every event ID must resolve to a physical file, row, and instrument. That file must appear in the tape envelope with the matching dataset and full-file SHA-256. Adjacent selected rows are compacted only into half-open physical row ranges; no intervening or later event is inferred.

The `O098` formation interval is the smallest half-open envelope containing the selected formation and touch events. The shared partition resolver rechecks file ownership, digest, instrument identity, clocks, and the selected native rows before the object enters `assemble_episode`. The resolved `O098.value` contract is:

```text
event_records, buy, sell, unknown, total, delta, delta_interval,
ordering_quality, aggressor_convention
```

This selected subset establishes exact decision-prefix provenance but does not establish continuous tape coverage. The object therefore preserves its native coverage hole, and the accepted source-method assembly remains `verdict=unknown`, `faithful_eligible=false`, with no detected causal violation. M09 pass/fail is carried only by the separately bounded research-comparison replay.

## Fixture controls

`implementation/tests/test_empirical_tape_integration.py` covers positive source assembly and adversarial controls for missing, unknown, late, future, foreign, stale, and differently configured inputs. A two-source disposable fixture also loads the same native membership through the preserved run-v1 implementation and the current per-source metadata cache, requiring identical full profiles, minute aggregates, and membership SHA-256. Its M09 case verifies exact pair-plus-touch locator ranges, the minimal event envelope, native `O098` assembly, and rejection of a tampered full-file digest.
