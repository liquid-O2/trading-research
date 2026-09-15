# Track R1 work log (candidate verdicts)

Playbook: Feature. Working root: `/workspace/.worktrees/stage-a-r1`. Branch `p15/stage-a-r1`.

Skipped playbook steps:

- architect arena: ruling R1 already names `confirmation.py`, `evaluate_family_rule_at_contact`, family confirmation-stage functions, and the evaluation contract. User cap of three live agents and one code writer forbids the multi-runner panel. Design is in `DESIGN.md` in this directory, not folded silently into implementation.
- rebase/commits: user forbade git commands.
- interrogate: design is not contested; the orchestrating session ruled R1.
- Opening a PR: user forbade git commands and receipts.

Throughput checkpoint:

- Blocking first steps. Ground the current unknown-verdict bug, name `ConfirmationDecision`, and pin empty-delta equality against B0.1 before writing family binders.
- Independent workstreams. Family confirmation-stage functions are conceptually disjoint. They share `confirmation.py` and `common.py`, so they serialize under one writer.
- Shared mutable state. `evaluate_family_rule_at_contact`, `_episodes_from_contacts`, and the family registry are one write target. Split is not available. One writer.
- Smallest safe decomposition. One code writer. Shared kernel plus eight adapters would race if fanned out.

Python: `/workspace/implementation/.venv/bin/python`, cwd `implementation/`, `PYTHONPATH=src`, `pytest -p no:cacheprovider`.

Ownership fence. This track owns the verdict path only. R3 owns contact/formation/reference enumeration, primitives, `native.py`, `runner.py`, engine, and data access. Call-site kwargs into `_episodes_from_contacts` from `changed_formation_scan` / `changed_reference_scan` are the minimum wiring. Enumeration logic stays untouched.

Decision. Confirmation decision time is the confirming bar's `known_at`, or the family deadline if no confirmation. Operands may use bars after the contact bar and must not use bars whose `known_at` is after that decision. Reading only the contact bar would make O056 and five-minute reclaim impossible.

Decision. Empty-delta equality uses each B0.1 episode's trigger as the contact, the episode's reference, `changed_axis="none"`, and compares `research_verdict` plus `failed` / `unknown` lists contact for contact.

Decision. B0.1 confirmation helpers are imported, not copied: `_ob_repaired` for JJ-TBR, five-minute reclaim for GB-FAIL, `_control` / Saint operational stages, Sires `flow_stages` via repaired local observations. `baseline_repairs.py` and method_pack files are not edited.

Decision. Candidate episodes populate `research_verdict`, `failed`, `unknown`, and `strategy_assessment.failed_conditions` / `unavailable_conditions` the same way `HistoricalEpisode.finish` does, by calling `expressions.evaluate` on the bound values.

Decision. Tests live in `implementation/tests/rule_discovery/test_candidate_verdicts.py` so they do not collide with track R4's P15-17 search tests.

Decision. Evidence and this log stay under `_track_r1/`. No receipts, no wiki, no git.

Decision. Confirmation uses HistoricalFeatures, the same market dual_scan uses. NativeMarketView through 17:00 would break empty-delta equality with B0.1.

Two writer subagents stalled on reads. Parent implemented after cancelling them.

Pytest: 25 passed in 342.18s on `test_candidate_verdicts.py` and `test_p15_09.py`.

JJ-TBR on the 9-date slice: F1 84 fail, R 156 fail, B0.1 10 no_setup. Candidate unknown 0.

Round 1 follow-up.

`dispatch_scan_variant` (`common.py`, empty_delta / `changed_axis` none) short-circuits to `dual_scan` and returns the B0.1 document. That path never calls `evaluate_family_rule_at_contact` or `confirm_at_contact`. It is not proof of fixture (i). Fixture (i) is `test_empty_delta_matches_b01_verdicts_contact_for_contact`, which calls `evaluate_confirmation` on each B0.1 trigger.

REFILL-STUDY `confirm_at_contact` now binds `zone_known_at` from formation freeze / reference issue, `departure_at` from the last 4-tick excursion before the contact, and `feature_max_known_at` from the freeze clock. Missing those clocks was why every candidate was unknown. Unknown share is asserted for every family. When B0.1 has no slice episodes, the bound is the family's literal pass/fail fixture.

Literals kept, structural facts a contact makes true:

- `location_touched`. The contact is the touch.
- `actual_band_contact`. The contact was enumerated on the reference band.
- `distinct_touch_id`. Lifecycle contact_id is unique per approach.

Computed, not stamped:

- SIRES `auction_route_ok` = `ref.get("complete", True)` as in `historical_flow._base`.
- SIRES `branch_regime_allowed` = None on gamma branches without a pre-touch gamma record, True only when the branch is not a gamma branch (`None if gamma else True`).
- MEMBER `prior_reaction_area_known`, `independent_minor_hvn_known`, `confluence_band_defined` from the prior-day reaction/HVN recipe in `scan_member_repaired`.
- REFILL `memory_uses_only_prior_resolved_touches` = `all(resolved < touch_at)` over the prior-resolved set (empty on the F1/R path).
- REFILL `label_uses_only_post_touch_observations` = every pre-touch clock is `<= touch_at`.

Merge notes for R3 (keep as R3 rewrites scanners):

- `changed_formation_scan` and `changed_reference_scan` must keep passing `market`, `view`, family, branch, formation, and reference into `_episodes_from_contacts`.
- `enumerate_lifecycle_contacts` still copies `row.get("source_confirmation")`, which distinct_contacts never sets. R3 may drop that key. Verdicts must not depend on it.
- Do not restore a `source_confirmation` field as the way candidate verdicts are decided.
