# Independent final empirical review

Reviewer: Astra Low. Scope: frozen manifests, checkpoint/artifact identities, observed denominators, missing-data status, source/causal boundaries, native endpoint reconstruction, final report aggregation and representative charts. Production files and tests are owned by other agents; this reviewer makes documentation-only changes during evaluation.

**Status: final independent gates passed for the declared v1.0.2 empirical scope.** All 165 jobs, final observed counts, native endpoint reconstruction, source/causal boundaries, deterministic chart bindings and the all-50 visual-review ledger passed. This accepts completion of the declared research-comparison run with explicit data/source holes; it does not establish full source methods or profitability. Earlier sections preserve the chronological findings and repairs.

## Initial evaluation freeze and snapshot

Initial run manifest SHA-256: `bbeb2776b90ac4fc0e35b7f654b2b3f44b5129e9bf8e1de2dd6e33e5d7a3ff07`.
Registry SHA-256: `7ce33ad43587e44168f2b5cbb910386c33f90cc5f8a1a5c6f2d90709791df381`.
Declared tested implementation SHA-256: `d56882109f8b47911d36da0333cf251f39d6abac2f2e169a5eac6828d5eaddfc`; lead reported the settled full suite passed 724 tests and 36 subtests before this freeze.

The initial manifest contains 165 jobs: 161 bar-monthly jobs with 14 rule assignments each, plus four tape-annual-trades jobs with five rule assignments each. Total: 2,274 rule/partition assignments. Fifty catalog branch dispositions and eight separate observation units remain in the registry.

An independent read-only snapshot audit covered the first 45 completed bar jobs. It found 506 actual opportunity records: 210 pass, 293 fail, three unknown; hence observed n=503 and N=506. The same snapshot had 357 missing-data rule/partition rows, 270 completed rows, and three completed rows with population holes. These statuses must remain distinct from observed counts and from the unscanned scope.

All 45 artifact hashes and artifact/checkpoint rule-summary bindings matched. No duplicate opportunity ID, source-faithful admission, non-unknown complete source-method verdict, declared causal violation or violated occurrence/reference/availability/replay clock was found in these 506 records. All 489 bar endpoints present in the snapshot were independently reconstructed from their artifact's complete one-minute bars; exact Decimal O/H/L/C/V agreed. Seventeen records had no endpoint object because their fixed outcome was absence or unknown, rather than an observed endpoint bar.

The first job (`bar-monthly--NQ-2010-09-07-26715`) illustrates why missing and zero differ: ten rules were missing-data; the NYAM parent had one failed opportunity; previous-hour observations had six pass and three fail; cash-open reclaim had one pass; MSS had a legitimately completed zero-child population because its sole NYAM parent failed. Every full source-method verdict remained unknown.

## Reporting finding and required repair

**FER-01 — observed counts suppressed by incomplete scope (material reporting defect).** The initial reporting code nulled an entire group's p/f/u/n/N when any member session had missing data, then nulled an entire rule whenever any partition was missing or unscanned. Family aggregation summed the resulting nulls as zero. Consequently it could display family n=0 despite hundreds of hash-validated observed records. This confuses incomplete population coverage with absence of observed evidence.

A related grouping defect used the record's transport unit for nonempty sessions but the registry's semantic observation unit for empty/missing sessions. This split otherwise identical rule/year/instrument cohorts into artificial groups.

Required repair: use one consistent registry-defined semantic unit while validating each record's permitted transport unit; retain observed p/f/u/n/N whenever actual records exist; expose missing/unscanned scope and population completeness separately; do not present conditional observed rates as complete-population frequencies. If no opportunities were observed and the declared search is incomplete or unavailable, the main unavailable denominator remains null, not a completed zero. Family counts must never silently coerce all unavailable groups to zero; rates must not pool incompatible rules/instruments/units.

The lead stopped the owned initial run at approximately 45 checkpoints and assigned a reporting-only version 1.0.1 repair with regression tests. The lead specified preserving the original exposed run artifacts, retaining selector/rule/date/split identities, freezing an explicit revision, rerunning the native pilot/full tests, and replaying all 165 jobs under the revised implementation identity. No research parameter or date selection change was requested or made by this reviewer. Acceptance remains pending the repaired report and complete revised run.

## Remaining review gates

- Verify the reporting repair against actual preserved observed records and incomplete-scope examples.
- Verify the revised run's immutable identities, exact 165-job membership and isolation from old exposed artifacts.
- Audit completed revised checkpoints/artifacts, including the four tape jobs and M09 exact native assembly.
- Reconcile report counts, statuses, denominator labels and source/causality evidence against all records.
- Inspect deterministic representative plots from the same records used for metrics.
- Record final completion scope and remaining source/data limitations without claiming unavailable source methods were discovered.

### Frozen cohort exclusion check

Independent set comparison of the two frozen split manifests found no selected evaluation date overlapping their declared source/calibration dates or detected prior-inspection dates. Both splits declare a 62-day lookback, outcome fields unexamined during selection, and no supported untouched-sample claim. Bar dates span 2010-09-07 through 2026-09-01 (161 distinct dates); the four standalone-tape dates span 2021-09-01 through 2026-09-01. Previously unrecorded inspection remains explicitly unknown rather than certified absent.

## Reporting repair and revision review

The repaired aggregation was independently checked against all 45 preserved initial artifacts. Their original absolute artifact paths and hashes were validated, along with job identities, rule-summary bindings and raw record summaries. In-memory validated triples were then passed through the repaired grouping, rule and family aggregation functions without writing any report or artifact.

All three levels reconcile exactly to p=210, f=293, u=3, n=503 and N=506. Family observed n is GB-FAIL 444, JJ-TBR 47 and SAINT-AMT 12; wholly unobserved families remain null. Compatible year/contract groups have at most three eligible partitions in this snapshot, rather than incorrectly repeating all 161 jobs. Fifty-two partially covered groups retain their observed records while main population rates remain null; 112 unavailable groups retain main N=null; three fully scanned compatible groups are legitimate completed zeros. No incomplete group was labelled no-candidates.

The direct `build_results` call with the archive directory as root cannot read these preserved artifacts because its canonical-path guard expects artifacts beneath that archive root, while immutable old checkpoints correctly retain their original absolute paths. This is an archive-root invocation limitation, not a failure of active-run reporting or a recurrence of FER-01. The independent hash/path checks above used the original frozen artifact root and did not rewrite archived evidence.

**FER-01 is resolved in the reviewed reporting repair.** The repaired code also validates semantic/transport unit membership and uses one registry semantic grouping key for populated, empty and missing sessions. Conditional observed rates are separate from full-population rates; family rates remain unpooled.

The revision-runner review found the intended controls present: original manifest and 45 checkpoints preserved; original native pilot and test identity/logs archived; unchanged registry and split identities required; source-file changes restricted to reporter, runner, and the separately reviewed tape aggregation cache described below; a fresh native-pilot identity and explicit exposure-record hash required; all original jobs retained; revised artifacts isolated beneath the revised run hash. The revised run explicitly declares prior exposure rather than restoring an outcome-blind claim. Final acceptance still awaits the complete revised run and final charts.

### Native-tape operational revision review

The extended 19-rule native calibration exposed repeated filesystem path resolution in tape aggregation. Independent comparison with the archived v1 `empirical_tape.py` found only a per-source-file relative-path/SHA cache inside `load_tape_session`; the membership payload, field order, row accumulation and native comparison selectors are unchanged. The runner verifies the archived full-file hash and compares all other module AST nodes exactly before accepting this revision. This guard intentionally excludes the aggregation helper, so acceptance of that helper rests on the reviewed concrete diff and native calibration, not the guard alone.

The runner also treats only the exact native-stream “no canonical native tape file overlaps requested interval” exception as an explicit empty window with unknown coverage and a full missing interval. This permits independent current/prior-window branches to run when a constituent window has no file. Hash, schema, ownership and identity exceptions continue to propagate. A missing M09 search remains missing-data; it is not converted to a completed zero. No rule, threshold or split change was found in these operational repairs.

## Second reporting integration finding

**FER-02 — revised artifact paths rejected by the reporter.** The v1.0.1 runner correctly isolated records beneath the first 16 characters of its run-manifest hash, but the reporter's canonical-path guard still expected the original legacy path without that component. The lead stopped the v1.0.1 run at 85 checkpoints and preserved its manifest, checkpoints, tests, logs and native calibration under `revisions/run-v1.0.1`; artifact paths remain immutable. A separately recorded v1.0.2 reporter/runner repair is required, with unchanged rules/selectors/cohort membership and an actual pilot report gate before full replay.

An independent read-only audit of all 85 preserved v1.0.1 checkpoints confirmed their artifact hashes, exact run-hash-prefix canonical paths, run/implementation identity, complete rule-summary binding and declared rule membership. They contain 1,038 actual opportunity records: p=410, f=615, u=13, observed n=1,025 and N=1,038. The 1,181 rule/partition assignments comprise 573 missing-data, 603 completed and five completed-with-population-holes statuses; one of these 85 checkpoints is a tape job. No duplicate opportunity ID, non-unknown source-method verdict, proxy-as-faithful count or declared timing violation was found. These are preserved exposed observations, not a completed evaluation or an untouched sample.

### v1.0.2 source review

The repaired `_expected_artifact_path` now uses the runner's exact 16-character manifest-hash namespace plus declared job ID for versioned runs, while preserving legacy paths for unversioned v1 artifacts. Path equality, artifact hash, job ownership, implementation/registry binding and full rule-summary equality checks remain in force. Regression tests cover acceptance of a real versioned layout and rejection of a foreign prefix.

Independent file-map comparison from archived v1.0.1 to reviewed implementation `8c3097892f5851d84c9c0d5decb09d3026755840ac1acec9d56b3ed89be8556f` found changes only in `empirical_reporting.py` and `empirical_runner.py`; all tape/bar selectors and the registry remain untouched. The revision runner admits the single next version v1.0.2, requires exact preserved v1.0.1 manifest equality, no active old checkpoints, unchanged registry/split hashes, a fresh native-calibration identity and exact version/previous-manifest exposure record. The existing reviewed tape-cache exception remains in generic revision code, but the actual v1.0.2 file delta does not use it. Acceptance of the reporting path fix remains pending an actual bar/tape pilot report under the new freeze.

### Actual v1.0.2 pilot gate — PASS

Active run SHA-256: `d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247`; implementation SHA-256: `8c3097892f5851d84c9c0d5decb09d3026755840ac1acec9d56b3ed89be8556f`. Independent `validate_run` succeeds. Registry, both split records and all 165 declared jobs exactly equal both prior frozen manifests.

The actual first bar and first tape checkpoints were audited through the repaired reporter. A fresh read-only `build_results` is exactly equal to the saved `RESULTS.json`, with validation true, no errors, two scanned jobs and 163 remaining. Both actual artifact paths equal the canonical versioned paths; raw artifact hashes, run/implementation identities and full checkpoint-to-artifact rule bindings match. This is a valid partial report, not a completed run.

The bar pilot contains 11 observations and the tape pilot one. Independent raw recount and every aggregation level (group, rule and family) agree on p=7, f=4, u=1, n=11 and N=12. GB-FAIL retains observed n=11; KEANI retains n=0 and observed N=1 because its one outcome is unknown. Wholly unobserved/unavailable families remain null. Fourteen unavailable compatible groups retain N=null. The three non-null group rates belong to completed compatible observed groups, while all four populated rule-wide main rates remain null because their declared search is unfinished.

For both pilot jobs, opportunity objects and replay results exactly equal the preserved v1.0.1 outputs. Entire artifacts are also equal after removing the implementation hash and normalizing order of semantically unordered hole lists. No other field difference was found. The hole list order varies across processes; hole membership, contents and all metric/selector outcomes remain unchanged. This is not a claim of byte-identical artifact serialization.

The tested implementation identity equals this freeze, and the full-suite XML hash matches its recorded test identity. The lead's full-suite gate records 736 passed tests. **FER-02 is resolved for actual bar/tape report integration; the independent pilot gate passes.** All 165-job final reconciliation and representative-chart review remain required before empirical completion acceptance.

## Bounded v1.0.2 evaluation snapshot

During the full replay, an independent read-only snapshot covered 75 completed jobs, including the first tape job. All artifact hashes, canonical paths, frozen job hashes, implementation/run identities and complete rule-summary bindings passed. Its 891 records comprise p=350, f=532 and u=9 (n=882, N=891). Typed opportunity/replay validation, unique IDs, complete source-method unknown verdicts and non-faithful admission all passed. Every one of the 853 present OHLCV endpoints was reconstructed exactly with Decimal arithmetic from contiguous artifact minute bars; 38 records had no endpoint. This is an endpoint reconstruction audit, not a claim of complete tape/population coverage.

A subsequent in-memory reporting snapshot captured the reporter's validated input triples while jobs continued arriving, avoiding a moving-directory comparison. That 91-job snapshot was valid and reconciled raw artifacts with group, rule and family aggregates exactly: p=447, f=663, u=13, n=1,110 and N=1,123. No production report was written. Remaining tape jobs, the complete 165-job scope and representative-chart inspection are still pending.

## Complete v1.0.2 source, endpoint and count audit

All 165 frozen jobs and all 2,274 declared rule/partition assignments are now present, with exact checkpoint IDs and no foreign or omitted job. Independent validation of canonical artifact paths, file hashes, job hashes, implementation/run identities, full rule-summary bindings, unique opportunity IDs, typed opportunity/replay clocks and source-assembly boundaries passed. The active `validate_run` also succeeds. Every complete source-method verdict remains unknown and every candidate remains in research-comparison mode without source-faithful admission.

The 161 bar jobs contain 2,448 records: p=1,000, f=1,412, u=36. All 2,309 present OHLCV endpoints were independently reconstructed exactly with Decimal arithmetic from contiguous complete artifact minute bars; 139 records have no endpoint. The four tape jobs add four KEANI opening-state unknown observations and no observed M09 zone-return opportunities. M09 inspected 59,648 / 256,947 / 322,181 / 271,795 physical native members for its four respective dates. Only 2023-01-03 has verified coverage and a legitimate completed zero search; the other three have explicit unknown coverage and missing-data search status. The twelve tape-profile branch assignments remain missing-data. The M09 rule's main n/N/rate remain null despite its observed zero count. No tape response endpoint exists to reconstruct in this cohort.

The final saved `RESULTS.json` exactly equals a fresh independent read-only report build. Raw artifact recount and all group/rule/family aggregate levels reconcile to p=1,000, f=1,412, u=40, observed n=2,412 and N=2,452. Assignment statuses total 1,535 completed, six completed-with-population-holes and 733 missing-data. Report validation is true with zero remaining jobs; overall status is `data_hole`, correctly distinguishing completed execution from incomplete population evidence. There are 157 jobs with at least one missing-data branch. Full-scope completion does not remove source/data holes or justify an untouched, source-faithful, actual-trade or profitability claim.

**The complete-run source/causality/counting gate passes.** Final representative-chart binding and visual-review reconciliation are the remaining independent acceptance gate.

## Final representative-chart audit

The completed renderer produced 50 charts. Independent reconstruction of the frozen selection rule (first chronological observation per rule/verdict plus first observation per observed year, with the declared cap) exactly matches every final index entry and its order. All 50 PNG hashes, source-artifact hashes, scored-record hashes and rule/verdict/year metadata match their final scored evidence. Renderer index SHA-256 before visual-status annotations: `8f9b5ecbf59f3ef4dbd07fdd902183106d30cefba5ecdc9587d4db5473bb981c`. Final reviewed index SHA-256: `fe3a2e252a527618cb50b9cd49c8a8d14fde89b84469ce54ee83ce1cb5e56e22`; only visual-review statuses were annotated, with PNG/record identities unchanged. Observed representative years are 2010–2023 and 2026; absent years are not invented.

This reviewer actually opened and visually inspected six final PNGs: `opp-89bd691ccc42cb333be3edd2` (MSS pass), `opp-3ae5048f6dbe0b24da42c8a3` (previous-hour censored unknown), `opp-1be3423a69720e7a72c4e9d9` (SIRES pass), `opp-7d27a1b45154834f4a09e80a` (GB-VWAP pass), `opp-d9688b3089122b679818d70d` (2026 Asia/TDO fail), and `opp-d9e5c424160647ad875dca50` (KEANI unknown). Titles, native-minute overview, reference/availability/endpoint annotations, evidence hashes and source-method-unknown caveats are readable and consistent with their records. The KEANI unknown chart does not invent unavailable prior-value boundaries. The censored endpoint coincides with the expiry as labelled. These charts visualize the scored comparison; they do not independently establish a source-faithful trade or profitability.

The final `VISUAL_REVIEW.json` ledger is now published and independently reconciled: its index hash, 50 chart hashes, 50 unique opportunity/record bindings, pass/reviewed statuses and both underlying reviewer-artifact hashes match exactly. The lead reviewed 29 images and the coverage reviewer 21; this reviewer separately inspected the six-image subset above. Dynamic VWAP, TDO, flow and aggregated-candle predicate details remain in the scored records and are not all overlaid on the minute overview, as the chart documentation explicitly states. **The final chart and all independent empirical acceptance gates pass.**
