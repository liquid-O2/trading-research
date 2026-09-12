# Full source-to-implementation audit

September 12, 2026. Audit and implementation planning only.

**The live method pack is not fully implemented.** Most of its important concepts were already documented. The largest gap is between those written contracts and the behavior actually produced by the code. There are also omitted source settings and process details, and a source-case interpretation that needs correcting. The earlier description of all 166 objects as implemented was too broad: registration and passing small fixtures do not establish complete behavior.

No production implementation, tests, runner, cache or canonical live specification was changed during this expanded audit. Earlier task changes were already present in the working tree. The audit records findings and the work required next; it does not run another parameter search or claim new historical performance.

## Evidence and scope

- Manually compared **all 166 O contracts** with their registered implementations. The [object inventory](OBJECT_AUDIT.md) gives the finding, code location and written requirement for every object; the [JSON inventory](charts/full-audit-objects.json) also records hashes and expected inputs/outputs.
- Inspected the **nine shared contracts C00–C08**, the 12 method input contracts and their assembly/report boundaries. [Shared-contract findings](charts/full-audit-core.json).
- Executed **27 read-only diagnostic counterexamples**, each with its actual input and result. All 27 reproduced the stated object-level gap. A separate manifest diagnostic accepted a nonexistent raw-member locator. [Reproduction inputs and results](charts/full-audit-probes.json).
- Extracted the **41 retained source PDFs, 711 pages**, screened their text for numerical/settings constraints, and reread focused original passages and figures. [Source inventory, hashes, review scope and findings](charts/full-audit-sources.json). This was not a fresh visual reread of every chart on every page, and is not a claim that no undiscovered detail remains.
- Incorporated the [profile coverage audit](PROFILE_COVERAGE_CHECK.md), including its native-data delta check and original profile figures.

The diagnostics exercise object boundaries. They do **not** demonstrate that a historical method candidate passed: downstream method checks can reject some malformed objects, and the retained automatic method cohorts contain zero candidates. Inspection-only findings are identified as such in the inventory.

| Inspection class | Objects | Meaning |
|---|---:|---|
| Partial | 97 | Material required behavior is missing or incorrect. |
| Bounded primitive | 27 | Useful computation or audit helper; complete native construction/assembly is external. |
| Supplied scalar only | 9 | Consumes a value without constructing the required source object. |
| Source hole handler | 11 | Retains an undisclosed definition as unknown. |
| Source hole handler, partial | 22 | Retains that limitation but has additional validation or assembly gaps. |

These are inspection categories, not 139 failed strategies or 27 complete methods. Preserving an actual source hole is useful work. It does not implement a published procedure that happens to share the same object.

## Documented behavior that the implementation does not deliver

### A01 — Historical episode construction is absent

The [discovery function](/workspace/implementation/src/trading_research/research/method_pack/discovery.py:61) checks a selector-hole record and returns an empty list. The [runner](/workspace/implementation/src/trading_research/research/method_pack/pass_runner.py:165) initializes empty candidate/object/outcome lists and populates candidates only from supplied manifests. There is no completed acquired-data path from native events through the full required objects into the method input views.

All 50 branches currently have recorded selector holes. Some are real unpublished author choices. Others depend on published constructions that have not been built or on source/process records that have not been assembled. A single `source_definition` label hides those different causes. Fixing published bars, profiles, geometry and evidence assembly does not require first recovering every discretionary selector.

**Required next:** separate source ambiguity, missing implementation, missing data and missing case records; build typed native/source-case input views before claiming historical discovery. Preserve the distinction between an unavailable cohort and zero candidates found by a complete selector.

### A02 — Raw provenance and object results are not fully validated

The [manifest parser](/workspace/implementation/src/trading_research/research/method_pack/evidence.py:149) only checks that `raw_member_locators` is nonempty before running a recipe on caller-supplied inputs. The diagnostic accepted `NONEXISTENT_AUDIT_LOCATOR` and an empty O004 bar as a computed object. No source-file/member resolution was performed by that path.

The parser retains `recipe_base_ok` but does not propagate the recipe's `coverage_ok`. It validates the input object's state enum before execution, then replaces it with the recipe result without revalidating that result. O150 returns order states such as `canceled` in the object-state field, although C01 defines `computed/supplied/hole/invalid`; the order state belongs inside the typed order payload.

The [shared guard](/workspace/implementation/src/trading_research/research/method_pack/protocol.py:63) checks dependencies **when supplied**. It does not discover the native events nested in each recipe's inputs. A correct outer timestamp cannot certify those inner observations.

**Required next:** resolve immutable native members, validate full output schemas, preserve unknown coverage/identity, compute availability from incorporated observations, and keep order-domain state separate from result validity.

### A03 — Several confirmations are presence checks or default true

The reproduced examples include:

| Diagnostic | Object | Actual behavior | Required distinction |
|---|---|---|---|
| P01 | O001 coverage | Five untimed `complete=true` records pass interval coverage. | Exact required intervals and native identity. |
| P02 | O004 bars | No members still produces `complete=true`. | Empty, missing and completed bars. |
| P03 | O006 clocks | Absent source-clock verification becomes true. | Verified versus unknown. |
| P10 | O065 POC history | Missing visits and coverage certify an untested POC. | Observed absence versus absent history. |
| P13 | O093 failed auction | Missing rejection time still gives `route_ok=true`. | Full required sequence versus incomplete evidence. |
| P14 | O102 replenishment | Zero consumption and zero refresh are called verified replenishment. | Actual executions/reloads versus a nonempty mapping. |
| P16 | O115 lift-off | Missing defense/refresh/exhaustion stages still give `order_ok=true`. | All required stages versus the subset provided. |
| P18 | O127 passive OFM | `dying_tape=false` produces `qualification=true`. | A failed observation versus mere field presence. |
| P19 | O128 squeeze | `no_prior_failure` is unconditionally true. | A causal, covered failure history. |
| P20 | O131 objective | An undated target is called pre-existing. | Known-before-entry versus unknown availability. |
| P26 | O154 risk validation | Absent process/availability evidence can still enable the overlay. | Metrics present versus eligible prior validation. |
| P27 | O166 transition | Missing current/next states and times still gives causal conditioning true. | Count arithmetic versus an observed transition. |

These are already governed by C01/C04 and the object procedures. They are implementation gaps, not missing author thresholds.

### A04 — Inner event chronology can be wrong or backdated

P05 makes O031 incorporate a trade at time 20 while reporting the resulting AVWAP known at anchor confirmation 10 and allowing use at 15. P07 makes O050 use later below/above-open events while keeping the result known at the opening time. P06 makes O047 accept confirmation before the sweep. P12 makes O085 accept a retest before the break. P25 makes O150 report a fill before the fill event is available.

The code also contains useful downstream timing checks. The gap is that validity is not consistently enforced where the fact is constructed. Repeating a few timestamps in a supplied method fixture does not close it.

**Required next:** every evolving value gets an immutable snapshot with native member bounds and maximum input availability; required stage relations must be checked on the actual linked events. Unknown ordering stays unknown, including tied native timestamps and OHLC bars containing both events.

### A05 — Source geometry and mirrored branches are incomplete

P04 shows O015 replacing the selected parent's width with a different supplied outer width. P08 shows O056 has only the bullish three-candle orderblock evaluation; the documented bearish mirror is absent. P09 shows O058 accepting one prior volume where the contract specifies 14. P11 shows O081's poor-low result is hard-coded false. P17 shows O123 accepting zero lift-off reward because it checks entry distance but not the documented reward interval.

Other object-specific omissions are in the inventory: incomplete opening/day-type classification, TPO period-count requirements, distinct parent/reference identity, and native range-bar/footprint construction. These need explicit two-sided and incomplete-input acceptance cases, not another happy-path arithmetic example.

### A06 — Complete profiles are missing

The [detailed profile report](PROFILE_COVERAGE_CHECK.md) establishes that the live wiki and O061–O086 already distinguish separate previous sessions, overnight, ETH, current developing RTH, composites, volume POC, profile midpoint, and signed volume by price.

The implementation mostly offers supplied histograms, scalar references or small reductions. O063 drops the supplied histogram/VA/identity from its developing snapshot output. O077 drops its price rows and returns a window delta. O073 does not construct the overnight profile. The old prior-RTH cache retains scalar levels, not the full separate profile panels or their decision-time provenance. Old VA helpers disagree on a tie case, and a retained legacy delta helper reverses the native sides and treats unknown sides incorrectly.

**Required next:** one dated profile identity per source window, with native price rows, buy/sell/unknown volume, VA/POC settings, H/L, immutable developing snapshots and explicit joins to older profiles. A composite and several separate profiles are different outputs. Source percentages such as 40%, 68% and 70% cannot share an assumed universal VA configuration.

### A07 — Local order flow is often reduced to supplied summaries

O102's replenishment example is one concrete false confirmation. O107 omits unknown-side volume from the denominator in P15. O108 evaluates supplied POC snapshots without constructing the same-candle profile stream. O109 consumes pre-paired ratio rows rather than constructing all required native diagonal comparisons/runs. O120 does not produce the complete by-price footprint and display filtering its source requires.

O163 has useful quantity/order/depth checks, but per-order side/price identity is not preserved across events and its per-side totals count additions only. Source-compatible native action decoding and lifecycle coverage are still necessary. Executed trades and best quotes can support substantial observable work; they cannot establish unseen full-depth cancellations, hidden reserve or a complete native order lifecycle.

**Required next:** local, same-interval trade/quote/footprint objects with explicit side uncertainty and source display configuration; use full-order/depth claims only where the actual dataset supports them. Keep native measurements and supplied qualitative interpretation as distinct fields.

### A08 — Order, position, thesis and risk lifecycles are incomplete

O150's event ledger is substantial, but the diagnostics show canceled working quantity remaining active, later exits of filled positions rejected after cancellation, fills accepted after expiry, and amended remainder computed from original quantity. These are separate invariants; fixing one does not fix the others. O142 also needs an unambiguous distinction between a requested partial and an executed fill.

O138 does not implement the complete persistent thesis/death-condition ledger. O144 applies a fixed −4R cap too broadly rather than binding the selected source policy. O145 does not supply a complete session reset/stop history. O147 does not construct the triad's native AMT-object first-use/reread sequence. O153 is a limited supplied-result summary, not the complete declared-process outcome distribution.

**Required next:** linked immutable thesis, attempt, order, fill, position, management and process records. Preserve initial risk separately from later brackets. Re-entry receives a new attempt ID while retaining the thesis, band and daily state. Stoic's data workflow belongs in our research process, not in the entry-strategy count.

### A09 — Object outputs do not yet connect to the typed method operands

The [scorer](/workspace/implementation/src/trading_research/research/method_pack/evidence.py:347) requires an object's field name to match the method operand and prohibits arbitrary `value_field` substitutions. Yet O046 exposes `box_high`/`H`, not the separately identified M03 `asia_high` and `london_high`; O062 exposes `vah`, not M08 `prior_vah`. There is no complete typed assembler to create those semantically distinct, dated references.

A mechanical screen found many candidate missing names, but those are **not** reported as hundreds of confirmed bugs: some are legitimate supplied qualitative observations or require an explicit derived producer. The confirmed issue is the missing connection between independently computed objects, semantic method roles, and their native evidence.

**Required next:** a declared mapping for each method operand, with recipe, value, units, role, parent/profile identity, evidence and availability. Do not fix this by allowing arbitrary renaming or injecting true assertions.

### A10 — Acceptance checks are narrower than the status suggests

[Fixture comparison](/workspace/implementation/src/trading_research/research/method_pack/protocol.py:126) checks only keys present in the expected fixture. A missing required output can pass when the fixture never asks for it. Many generic mutations add a late dependency or remove one registered input, so they validate the shared guard while missing errors in native inner events, side mirrors or output completeness.

[Report validation](/workspace/implementation/src/trading_research/research/method_pack/pass_runner.py:43) checks count arithmetic, fixture inventory, branches and artifact hashes. It does not compare full object outputs against the written contracts. C07 explicitly assigns missing required outputs to `implementation_fail`. The current contract-coverage audit therefore fails even though the earlier commands returned `source_hole` and zero fixture mismatches.

**Required next:** make contract completeness and the demonstrated invariants part of acceptance. Keep source ambiguity and software failure independently visible. Zero admitted leakage in an empty historical cohort is not evidence that every producer is causal.

## What was omitted from the written source mapping

The [source findings ledger](charts/full-audit-sources.json) distinguishes these from implementation gaps and from details already documented elsewhere.

| Finding | Original source | Documentation finding | How to carry it forward |
|---|---|---|---|
| Sires VWAP settings | [VWAP lesson](/workspace/sources/documents/discretionary/vwap-lesson-10.pdf), p.8 | The original inputs show Session anchor, offset 0, Chart timeframe and the enabled wait-for-timeframe-close option. The source-price field is truncated to `(H + L + …)`, consistent with HLC3 but not fully readable. O030 does not bind this illustrated bar configuration. | Record exactly visible settings and remaining uncertainty. Do not declare the full price formula or ET session clock recovered from a truncated label. Do not transfer Sires's settings to Green Bird. |
| Codex scale and review example | [Code 1](/workspace/sources/documents/discretionary/code-1-thesis.pdf), p.6 | Generic confidence/review fields exist in O146, but the source's **1–5 at session start** and **30-session review** example are missing from their source binding. | Add a Sires process configuration and preserve original observation time. It is not a universal sufficient sample. |
| Excursion research step | [Code 2](/workspace/sources/documents/discretionary/code-2-risk.pdf), p.4 | The source's **40–80-trade MFE/MAE collection** guidance is absent from the live markdown pack. | Add the scoped research step and required distributions. Actual stop/target optimization remains deferred. |
| SessionStat compatibility | [SessionStat+](/workspace/sources/documents/jumbo/SessionStat+.pdf), p.7 | Active contracts omit the source's explicit timeframe/custom-session detection dependence. An older live chart-audit record already mentioned `bar_index`, so this is an active-contract omission, not a fact never written anywhere. | Bind comparisons to chart timeframe, source version and actual session detection. No global two-minute rule. |
| Green Bird November 20 entry | [Original archive](/workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf), p.43 | The displayed short-position line is at **25301.75 in the swept-high area**. The earlier reconstruction incorrectly imposed later MSS/FVG completion as its entry explanation. | Preserve the sweep entry for this case; later structure remains subsequent context. Exact fill time remains unknown, and displayed MNQ is not an actual NQ fill. |

![Original Sires VWAP input image, including the truncated price-source label](/workspace/implementation/reports/phase1-live/methods/charts/full-audit-sires-vwap-inputs.png)

Two corrections prevent repeating the same mistake: **Sires's illustrated 18:00–09:30 overnight clock is already in O011**; the missing part is O073's explicit profile binding. **Multiple prior profiles and source-specific timeframes were already documented**; the missing parts are full construction, source-case configuration and assembly. O032 also already distinguishes displayed ±1/±2 bands from the discussed 2.5/optional 3 variants.

Proprietary P-zones, EVRange, KG1, source-selected statistical engines and qualitative admission rules still have genuine unresolved details. Those limits should identify the exact absent definition or observation. They do not prevent implementing published components or reconstructing attributable source cases. Future inferred models need named assumptions, source-case calibration and separate evaluation; they cannot silently inherit an author's name as proof of fidelity.

## What can be reused

Retain the native adapters and ownership work, date-aware clock helpers, exact-decimal geometry, three-valued logic, useful histogram/POC and arithmetic primitives, existing evidence/identity checks, reference-outcome handling, and the stronger parts of the refill/order/state audits. Retain negative examples and source-conflict records too.

Rework the object boundaries, complete the missing payloads and native producers, then assemble the method views. The [implementation plan](IMPLEMENTATION_PLAN.md) gives dependencies, concrete outputs and acceptance criteria. It does not start that work.

## Method coverage and retained run snapshot

The following family-specific findings and two required tables are generated from the inspected inventory and retained run. Historical counts are the **September 12, 10:52 UTC snapshot**, not a newly rerun experiment. Every historical N is zero. Current audit verdicts describe implementation coverage, not trading results.

| Family | Object memberships | Coverage finding | First implementation focus |
|---|---:|---|---|
| M01 / JJ-TBR | 62 | Full source profiles, parent geometry, mirrored OB, 14-bar history and source-selected context/confirmation assembly remain incomplete. | Steps 1–4, then 6–7. |
| M02 / GB-FAIL | 25 | Reference/sweep timing and operand construction need completion; November 20 must retain its observed sweep-entry interpretation. | Case correction, native reference/sequence builder. |
| M03 / GB-VWAP | 11 | Dated Asia/London high roles, source VWAP configuration and later retest/risk evidence are not assembled. | Source configuration, scalar-role producers, episode view. |
| M04 / GB-SCALP | 15 | Case descriptions exist; a complete automatic admission rule cannot be inferred from the supplied bias/risk fragments. | Case-native context and disclosed sequence, explicit unknown admission. |
| M05 / SIRES | 117 | Full profiles, local footprint/DOM sequences, persistent thesis/re-entry and order management have major documented gaps. | Profiles/flow, lifecycle, then branch-specific input views. |
| M06 / SAINT-AMT | 36 | Profile routes need native construction, same-band break/retest and HTF/LTF evidence; presence-only profile permission is inadequate. | Dated profile/reference identities and route assembly. |
| M07 / MEMBER-TWO-REASONS | 28 | Two reasons need independent prior reaction/HVN evidence and planned return identity; supplied geometry is insufficient. | Independent evidence producers and linked return attempt. |
| M08 / KEANI-OPEN-ABOVE-VALUE | 24 | Full prior VA, complete A period, developing value and defended imbalance retest are not constructed as one dated sequence. | Full profile snapshots, native footprint and explicit prior/current roles. |
| M09 / REFILL-STUDY | 27 | Touch/selection checks are useful; native source zone/grading records and correct pending-order/lifecycle behavior remain incomplete. | Touch history and explicit selected-order audit; no invented model grades. |
| M10 / JETBUNDLE-STATES | 15 | Supplied state audits exist; native lifecycle identity and actual adjacent transition evidence remain incomplete. | Declared native depth scope, linked states/cadence; classifier remains separate. |
| M11 / STOIC-DATA | 14 | Process/journal primitives exist, but actual versioned research records and joins are unbuilt; macro remains deferred. | Apply process collection to our own methods; no entry-strategy label. |
| M12 / STOIC-RISK | 8 | Printed risk arithmetic exists; complete prior validation, stage/reset and account-policy evidence remain incomplete. | Causal validation and linked risk-stage records, no new simulation. |

Object memberships overlap because common objects serve several methods. These are twelve method/process/state/risk records, not twelve independent entry strategies.

### PHASE — retained historical run, not a new acceptance result

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---:|---|---|---|
| JJ-TBR | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [jj-tbr.md](/workspace/implementation/reports/phase1-live/methods/jj-tbr.md) |
| GB-FAIL | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [gb-fail.md](/workspace/implementation/reports/phase1-live/methods/gb-fail.md) |
| GB-VWAP | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [gb-vwap.md](/workspace/implementation/reports/phase1-live/methods/gb-vwap.md) |
| GB-SCALP | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [gb-scalp.md](/workspace/implementation/reports/phase1-live/methods/gb-scalp.md) |
| SIRES | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [sires.md](/workspace/implementation/reports/phase1-live/methods/sires.md) |
| SAINT-AMT | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [saint-amt.md](/workspace/implementation/reports/phase1-live/methods/saint-amt.md) |
| MEMBER-TWO-REASONS | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [member-two-reasons.md](/workspace/implementation/reports/phase1-live/methods/member-two-reasons.md) |
| KEANI-OPEN-ABOVE-VALUE | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [keani-open-above-value.md](/workspace/implementation/reports/phase1-live/methods/keani-open-above-value.md) |
| REFILL-STUDY | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [refill-study.md](/workspace/implementation/reports/phase1-live/methods/refill-study.md) |
| JETBUNDLE-STATES | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [jetbundle-states.md](/workspace/implementation/reports/phase1-live/methods/jetbundle-states.md) |
| STOIC-DATA | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [stoic-data.md](/workspace/implementation/reports/phase1-live/methods/stoic-data.md) |
| STOIC-RISK | historical/source | 0 | — (no candidates) | source_hole (retained snapshot) | [stoic-risk.md](/workspace/implementation/reports/phase1-live/methods/stoic-risk.md) |

### Audit — current contract coverage

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|
| JJ-TBR | M01 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Full source profiles, parent geometry, mirrored OB, 14-bar history and source-selected context/confirmation assembly remain incomplete. |
| GB-FAIL | M02 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Reference/sweep timing and operand construction need completion; November 20 must retain its observed sweep-entry interpretation. |
| GB-VWAP | M03 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Dated Asia/London high roles, source VWAP configuration and later retest/risk evidence are not assembled. |
| GB-SCALP | M04 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Case descriptions exist; a complete automatic admission rule cannot be inferred from the supplied bias/risk fragments. |
| SIRES | M05 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Full profiles, local footprint/DOM sequences, persistent thesis/re-entry and order management have major documented gaps. |
| SAINT-AMT | M06 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Profile routes need native construction, same-band break/retest and HTF/LTF evidence; presence-only profile permission is inadequate. |
| MEMBER-TWO-REASONS | M07 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Two reasons need independent prior reaction/HVN evidence and planned return identity; supplied geometry is insufficient. |
| KEANI-OPEN-ABOVE-VALUE | M08 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Full prior VA, complete A period, developing value and defended imbalance retest are not constructed as one dated sequence. |
| REFILL-STUDY | M09 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Touch/selection checks are useful; native source zone/grading records and correct pending-order/lifecycle behavior remain incomplete. |
| JETBUNDLE-STATES | M10 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Supplied state audits exist; native lifecycle identity and actual adjacent transition evidence remain incomplete. |
| STOIC-DATA | M11 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Process/journal primitives exist, but actual versioned research records and joins are unbuilt; macro remains deferred. |
| STOIC-RISK | M12 | incomplete | prior fixtures pass; contract gaps | historical N=0; unmeasured | historical N=0; unmeasured | Printed risk arithmetic exists; complete prior validation, stage/reset and account-policy evidence remain incomplete. |

The old fixture/zero-admission counters are preserved as facts about the retained run. The new audit does not certify them as exhaustive coverage. At the implementation-contract level, the missing required outputs and reproduced violations require remediation under C07; a source-hole label alone is insufficient.

The [verification record](charts/full-audit-verification.json) checks complete inventory, diagnostic results, artifact links/hashes and the no-implementation-change baseline for this audit.
