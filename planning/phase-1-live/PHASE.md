# Phase 1 method pass plan

Version: `method-pack-v1`, 2026-09-11. Planning only: none of the commands below has been implemented or run by this task. The current runner exposes `check`, `run` and `report`; `method-pass` below is the new interface to implement. Do not mistake a legacy family report for a completed method pass.

## One command owns one method pass

Implement the interface at [the existing runner](/workspace/implementation/tools/run_phase1_objects.py) in the `trading_research` package. Run commands from `/workspace`. Each command must:

1. Load FORMULAS C00–C08 and the selected M/O contract version. Register only the 12 mapped methods and their exact object inventories.
2. Run the selected method's printed fixtures and all required object/causality/identity/hole mutations. Synthetic/source-illustration fixture counts remain separate from historical/cohort counts.
3. Inventory relevant acquired files under the data root, resolve exact schemas/timestamp units, freeze disjoint tape ownership, check actual instrument/window coverage, and enumerate source holes before discovery. Stream relevant partitions; do not materialize every multi-year tick archive at once.
4. Attempt historical candidate discovery only where the complete source selector exists. Otherwise emit candidate_discovery=hole with explicit affected branches and no fabricated candidate rows. Optionally ingest a separately supplied episode manifest under the input contract below; absence is a reported input limitation, not permission to invent cases.
5. Build causal object snapshots and bound predicate operands; score all identified candidates with pass/fail/unknown. Retain every failed/missing stage and all branch scopes. Score secondary case, management, re-entry, reference and process records in separate denominators.
6. Reconcile p/f/u/n/N, rate, missingness interval and ET year splits. Write the complete machine-readable report, Markdown twin and trace artifacts, then print the requested headline table.

There is no required separate check/run/report invocation. A method ticket is finished only when its single pass command completes the whole operation and its externally visible contract checks pass.

## CLI and input contract

| Argument | Exact behavior |
|---|---|
| `method-pass` | New subcommand; this planning pack does not claim it already exists. |
| `--method ID` | Required, exactly one of the 12 IDs in the table below; unknown ID is a configuration error. |
| `--scope acquired` | Inventory all available relevant acquired coverage without selecting years/days by later outcomes. This does not waive missing source selectors or fill absent evidence. |
| `--data-root /workspace/data` | Read existing acquired data and manifests; do not mutate raw files or commit this directory. |
| `--report-root PATH` | Write new method reports and their detail artifacts under this explicit output root. Default planned root is the existing report tree's methods directory. |
| `--episodes PATH` | Optional explicit supplied-episode manifest. No such manifest is assumed to exist. It must contain the C01 records, source method/branch/instrument IDs, evidence mode, source/version, actual observation/decision times, producer recipe IDs and field provenance. Reject naked Booleans or unknown foreign method/object IDs. |
| `--formula-version method-pack-v1` | Optional explicit match; absent means this pack's current version. Any mismatch is a configuration error. Hash the exact consumed formula/method sections into the report. |

Without `--episodes`, execute all printed fixtures and audit acquired discovery/coverage; full-method source holes may leave historical N=0. Do not assign source illustration fixtures to historical years or call their outcomes market rates. A later user-supplied manifest is optional new evidence, not an unpublished-engine requirement for completing the implementation.

Exit code 0 means the fixtures, bindings and report contract passed, including correctly reported source_hole, data_hole or no_candidates status. Exit code 1 means implementation_fail: fixture mismatch, incorrectly admitted leak/proxy, missing output or report invariant failure. Exit code 2 means invalid CLI/configuration/schema. A correctly rejected candidate or negative fixture is not exit code 1.

## Required report contract

The headline schema is exactly:

`method | predicate | n | rate | interval | year split | status | report path`

The planning rows below are `not_run`; dashes are unmeasured fields, not zero samples. Runtime `n=p+f`, `rate=p/n`, and `interval=[p/N,(p+u)/N]` with `N=p+f+u`, all as specified in FORMULAS C07. This interval is an exact finite-cohort missingness bound, not a confidence interval. Source-sequence compliance is not trade win rate. If N=0, rate and interval are null. Source discovery unavailable is not a complete zero-candidate selector.

Print separate headline rows when a method has additional predicate/cohort units; never pool confirmed entries with incomplete cases or selected orders with all touches. The primary rows are:

| method | predicate | n | rate | interval | year split | status | report path |
|---|---|---:|---:|---|---|---|---|
| JJ-TBR | sequence | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/jj-tbr.md` |
| GB-FAIL | sequence | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/gb-fail.md` |
| GB-VWAP | sequence | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/gb-vwap.md` |
| GB-SCALP | case_description | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/gb-scalp.md` |
| SIRES | sequence | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/sires.md` |
| SAINT-AMT | sequence | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/saint-amt.md` |
| MEMBER-TWO-REASONS | sequence | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/member-two-reasons.md` |
| KEANI-OPEN-ABOVE-VALUE | sequence | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/keani-open-above-value.md` |
| REFILL-STUDY | touch_causality | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/refill-study.md` |
| JETBUNDLE-STATES | state_observation | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/jetbundle-states.md` |
| STOIC-DATA | process | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/stoic-data.md` |
| STOIC-RISK | printed_ladder | — | — | — | — | not_run | `/workspace/implementation/reports/phase1-live/methods/stoic-risk.md` |

Each method writes `<slug>.json` and `<slug>.md` at the report root. Store detailed trace files under `<slug>/` and include their actual paths and hashes in the JSON. Write atomically; never leave a success headline pointing at a missing or partial report.

| JSON field / artifact | Required contents |
|---|---|
| identity | method_id, formula_version, source_wiki_commit, source/section hashes, implementation version/dirty hash, exact command, UTC created_at |
| scope | requested/actual date spans, native instruments, branch inventory, source variants, evidence modes, partial endpoint years and candidate_discovery state |
| ownership and coverage | selected data paths with disjoint owned intervals, schemas/timestamp units, actual missing intervals/fields and method-specific required surfaces |
| cohort | frozen inclusion rule/manifest hash, eligible and unselected IDs, distinct candidate/touch/order/fill relationships; no invented daily candidate when selector is missing |
| summary / branches / years | predicate and cohort unit, p/f/u/n/N, exact numerator/denominator rate, exact interval endpoints, status and all affected holes; totals reconcile |
| candidates.jsonl | C01 candidate records, complete operand values/types/producer IDs, base_ok, coverage_ok, sequence_ok, verdict, failed_prerequisites, hole IDs and source references |
| objects.jsonl | Used immutable C01 object/assertion snapshots, raw member locators, formation/as_of/known_at, values/units, source version and availability proof |
| holes.jsonl | Recipe/method/branch/candidate, source_definition/source_conflict/data_coverage/ordering/identity/supplied-record gap, missing field, exact reason, affected outputs |
| fixtures.json | Every applicable Oxxx-F1, Mxx-F1/F2/F3 and mutation:inputs, expected/actual values, status and evidence mode; excluded from cohort counts |
| quality | fixture_failures, unbound_fields, duplicate_candidates, year_reconciliation_errors, leakage_count, proxy_as_faithful_count; all must be zero for exit 0. Separately retain detected_causal_violations and rejected_proxy_attempts. |
| source limitations | Required unknown definitions/readouts, branch-specific interpretation conflicts, Refill causal correction and Stoic activation conflict where applicable |

For an unavailable discovery cohort, emit an empty candidate artifact plus a complete branch-level hole ledger, not fabricated unknown trades. A header-only detail artifact is acceptable only when its explicit count is zero. Keep all requested branches visible, even those with no discovered candidates. For every year actually requested by the acquired scope, show covered/uncovered/partial status and counts or the discovery hole reason.

## Method implementation slices

These are vertical slices in the requested to-tickets style. Dependencies below describe implementation reuse/order only; they never add another author's prerequisite to a method. The first slice includes the shared CLI/report seam and enough data/evidence plumbing to finish JJ-TBR. Add later shared primitives inside the method slice that needs them; do not replace method completion with a horizontal helper project.


### M01 — JJ-TBR

**Depends on:** none; establishes the public method-pass/report seam.

**Contract:** FORMULAS M01, its 62 mapped objects, and C00–C08. **Primary unit:** One source-selected TBR decision attempt, with one of its eight named branches.

**Deliver:** The entire selected context → frozen range → location → source confirmation → predeclared risk/objective sequence, followed by separate management and reference outcomes.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method JJ-TBR --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic source-illustration judas_reversal: 06:00–09:00 range L100/H120, known 09:00; source reversal context fixed 09:20; high sweep 121 at 09:41; selected source rejection confirmation 09:43; short decision 09:44; risk above the case rejection structure and preselected opposing objective 100. All source-context/confirmation records carry synthetic evidence IDs, same band/side and actual known_at. The sequence passes its fixture; sweep depth is 0.05W and need not equal 0.5W.
- Replace rejection with fully observed continued acceptance above 120: fail. Move purge/context evidence after 09:44: causal fail. Replace a projection parent with a different range: invalid identity/fail. No favorable later target can repair these.
- Remove source confirmation or a required P-zone/EV/Session Stat source value: unknown for that branch. Do not generate the missing engine.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/jj-tbr.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M02 — GB-FAIL

**Depends on:** JJ-TBR implementation slices.

**Contract:** FORMULAS M02, its 25 mapped objects, and C00–C08. **Primary unit:** One identified failed-breakout/failed-breakdown attempt at its actual completed source reference.

**Deliver:** Frozen reference → relevant sweep → actual source failure/reclaim confirmation → optional case-specific confluence/retest → entry risk and preselected objective.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method GB-FAIL --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic NYAM box H110/L100 known 10:00, bias known 09:55, high sweep 111 at 10:01, clock-aligned complete 10:00–10:05 close 109, short decision 10:06, source risk 112 and opposing objective 100. tdo_required=false, pocket_required=false, retracement_entry=false because this selected fixture has no such requirements. Complete source evidence yields pass.
- At 09:45 the final 09:00–10:00 box is unavailable: causal fail. Close 111 after sweep 111 remains outside: fail. A pocket touch without a failure fails. A fifth observed row at 10:06 cannot complete a missing 10:02 clock interval.
- Unspecified London/session clock, source hold detector, prior-period scope or stop policy → corresponding unknown. TDO is not universally mandatory.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/gb-fail.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M03 — GB-VWAP

**Depends on:** GB-FAIL implementation slices.

**Contract:** FORMULAS M03, its 11 mapped objects, and C00–C08. **Primary unit:** One supplied/defined long continuation after a close above both finished Asia and London highs and a later VWAP retest.

**Deliver:** Known finished session references → completed close above both highs → later source VWAP retest → long with predeclared risk.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method GB-VWAP --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic supplied Asia H100 and London H102 known 08:00; source breakout candle closes 103 at 09:40; verified source VWAP 101.5 available before 09:45 retest bar L101/H102; long decision 09:46 with source risk 99. Both highs were exceeded and the retest straddles 101.5: pass for the supplied fixture.
- Breakout close 101 is not above London H102: fail. A retest before breakout fails order. A short mirror fails side. Later 150 point reported gain cannot serve as target or confirmation.
- Remove verified source VWAP reset: unknown even if a 09:30-reset comparison VWAP exists. General target policy is separately unknown and does not become an added entry gate.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/gb-vwap.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M04 — GB-SCALP

**Depends on:** GB-FAIL implementation slices.

**Contract:** FORMULAS M04, its 15 mapped objects, and C00–C08. **Primary unit:** One supplied directional scalp case; automatic full entry admission remains unknown.

**Deliver:** Audit the disclosed directional read → favorable pullback/pop → small exposure → limited source management, preserving all undisclosed trigger/invalidation/exit fields.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method GB-SCALP --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic case: bearish direction recorded 09:30, supplied favorable pop 09:40, deliberately small size 1 contract declared 09:39, short 09:41 and supplied limited 20 point scalp-management reference. The case-description expression can pass; automatic sequence_ok stays NULL. The 20 point value illustrates the cited 20–30 point source case, not a new general target.
- Direction first recorded after entry or opposite to the actual scalp makes the claimed case fail. A large-size entry cannot satisfy an explicitly supplied small-size policy merely because it won.
- Full trigger, measured-impulse selection, general invalidation and exit algorithm are holes in every automatic scalp-admission result.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/gb-scalp.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M05 — SIRES

**Depends on:** JJ-TBR implementation slices.

**Contract:** FORMULAS M05, its 117 mapped objects, and C00–C08. **Primary unit:** One source-selected confirmed entry attempt within a live Sires thesis; separate units for incomplete cases, management actions and fresh re-entries.

**Deliver:** Version/model and account box → current auction/regime → thesis/death → allowed location → exactly one complete execution branch → structural risk/objective → supported management/re-entry → versioned review.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method SIRES --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic defended_band_continuation: source short thesis/band [109, 110] known 09:20 and still alive under supplied death rules; valid auction route/regime evidence before touch; prior seller defense 09:30; same-band return 09:45; fresh seller executions/refill and source refresh/control confirmation 09:47; short decision 09:48 with predeclared stop 111 and target 103. All identities and supporting assertions are supplied in synthetic mode. Full selected branch passes.
- Use a 09:30 defense as the fresh 09:47 confirmation: fail. For aggressive OFM, omit release/failure/refill or enter before drive/retest: fail. For strict absorption reversal, remove own reward/reward retest: fail. For long-gamma balance fade, do not invent an own-reward gate. STOP entry at daily R=-4 fails.
- Missing exact CVD reference, source state/refresh criterion, full required depth, gamma/KG1 readout or thesis death input → unknown. Incomplete early/third-test/late-fade cases remain case-description rows and do not enter confirmed-branch n.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/sires.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M06 — SAINT-AMT

**Depends on:** SIRES implementation slices.

**Contract:** FORMULAS M06, its 36 mapped objects, and C00–C08. **Primary unit:** One of Saint's four source routes with current HTF/LTF agreement.

**Deliver:** Actual HTF balance/profile permission → read arrival → wait for present LTF control → complete selected route/retest → source structural risk and objective.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method SAINT-AMT --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic trapped_buyers_retest: source upper HTF area 110 defined yesterday; distinct earlier AM/PM buying failures known yesterday; current LTF balance breaks down 09:45, retests same boundary 09:50, repeated body selling and DOM/current short control confirm 09:52, short 09:53 with predefined risk and objective. Prior failures and all current stages precede entry: pass.
- Duplicate one prior failure as two: fail distinctness. Enter during free two-sided chop before current control: fail when fully observed. Remove actual retest from a chased attempt: fail. Do not require Sires's older-POC instant-rejection rule for every Saint failed auction.
- Missing source current control, exact source profile/balance selection or required acceptance/hold procedure → unknown. Saint 68% value remains distinct from Sires 70%/40% settings.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/saint-amt.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M07 — MEMBER-TWO-REASONS

**Depends on:** SIRES implementation slices.

**Contract:** FORMULAS M07, its 28 mapped objects, and C00–C08. **Primary unit:** One unnamed member attempt combining independently known reaction history and minor HVN at a preplanned confluence area.

**Deliver:** Conditional thesis/objective/risk → independently identified reaction band and minor HVN → actual planned-band contact → current source rejection or buyers absorbing/holding → entry.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method MEMBER-TWO-REASONS --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic prior reaction band [100, 102] and independently sourced minor HVN [101, 103] known 09:30; source-selected confluence band [101, 102]; contact 101.5 at 09:45, supplied resistance rejection high 102 at 09:47, short decision 101.5 at 09:48 with source stop 102.25 and objective 98. The two reasons, actual contact and source short stop relation pass.
- Reuse one resistance line as both independent reasons: fail/identity hole. No actual band contact or stop below the short rejection high fails. A later HVN cannot explain an earlier entry.
- Source target prose/ticket conflict is kept as a separate target-policy hole. The long case needs buyers absorbing/holding; do not import Sires's four-check lift-off gate.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/member-two-reasons.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M08 — KEANI-OPEN-ABOVE-VALUE

**Depends on:** SIRES implementation slices.

**Contract:** FORMULAS M08, its 24 mapped objects, and C00–C08. **Primary unit:** One Keani long with whole A above prior VAH, later developing-value breakout and defended buying-imbalance retest.

**Deliver:** Prior VA fixed → complete A entirely above prior VAH → observe developing value higher/source rejection → break current VAH with aggressive buy imbalance → defend actual imbalance band with DOM → time/risk/objective check → long.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method KEANI-OPEN-ABOVE-VALUE --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic prior VAH 100, whole A 09:30–10:00 low 101, so 101>100; source developing value higher/rejection observation 10:01; frozen developing VAH 104 known 10:02; breakout close 105 at 10:05 with supplied buying-imbalance band [104, 104.5]; retest 10:07, buyer defense/DOM 10:08, long decision 10:09 with source timing/risk/objective. With all supplied source conventions this passes.
- Whole A low 99.75 even if open 101: fail. Use prior VAH as the later moving VAH or retest another band: invalid/false. Entry before 10:00 cannot know whole A. Short mirror is not published and fails side.
- Unknown exact source near 10:00 timing convention or diagonal settings stays unknown; do not select a minute tolerance or a developing VAL short mirror.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/keani-open-above-value.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M09 — REFILL-STUDY

**Depends on:** SIRES implementation slices.

**Contract:** FORMULAS M09, its 27 mapped objects, and C00–C08. **Primary unit:** One already-identified source zone touch; separate supplied selected-order configuration rows.

**Deliver:** Frozen source zone → departure → distinct return → strictly causal pre-touch construction/memory/location/flow → later label; if supplied, audit frozen grade/order/bracket/fill/cost records and preserve the later causal correction.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method REFILL-STUDY --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic supplied zone [100, 101] known 09:40, departure 102 at 09:45, distinct touch 10:00, all features known 09:59, prior defense resolved 09:42, later label resolved 10:10. This touch-causality record passes. A separate supplied order fixture preserves 12/32/96 ticks, 30 minute cancel, one position, 1 tick cost and 1 tick stop slippage.
- Include 10:10 current-touch outcome in 09:59 memory: causal fail. Use a later-day selection or future-trained grade for the order: fail. Treat 312 signals and 64 fills as paired trades: cohort failure.
- No supplied frozen grader/grade or exact source zone/side definition → unknown. Headline primary measures touch-record causality, not profitability; later-OFM negative causal rebuild must remain visible.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/refill-study.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M10 — JETBUNDLE-STATES

**Depends on:** SIRES implementation slices.

**Contract:** FORMULAS M10, its 15 mapped objects, and C00–C08. **Primary unit:** One source-defined or supplied B/A/D/E/W state; a separate next-state observation audit.

**Deliver:** Native provide/withdraw/consume events → same-interval response/liquidity evidence → source heuristic state → later next state with conditioning known at current state.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method JETBUNDLE-STATES --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic supplied A state at 10:00 with complete local executed effort, low response and verified opposite holding/refill, all known 10:00, satisfies its observation expression. A next state at 10:01 with conditioning frozen 09:59 can pass the transition-timing audit.
- W state with unobserved cancellations cannot be passed from displayed imbalance. Conditioning first known 10:00:30 for state 10:00 is causal fail. Same-time unresolved next state order is unknown. Do not transfer printed AAPL84%/12% values to NQ.
- Missing source depth/cancel data or heuristic thresholds → automatic state unknown. There is no entry-admission predicate beyond this observation method.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/jetbundle-states.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M11 — STOIC-DATA

**Depends on:** REFILL-STUDY implementation slices.

**Contract:** FORMULAS M11, its 14 mapped objects, and C00–C08. **Primary unit:** One declared research/process review block; macro application is a scoped additional process check.

**Deliver:** Freeze reproducible process/inclusion → collect all observations uniformly → separate inputs/outcomes → record supplied aggregate winner/loser comparison → revise using completed prior sample; macro application adds vintages/history/declared rules.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method STOIC-DATA --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic process v 1 frozen January 1 before sample January 2–31; eligible IDs 1–100 all retained in one schema; features known before their decisions; outcomes stored separately; comparison recorded February 1; v 2 revision February 2 uses only that completed block. The process expression passes.
- Drop 20 losing observations: fail. Freeze inclusion after January 31 outcomes: causal fail. A macro input revised in March cannot fill a January decision. A custom C-score cannot be replaced by z-score.
- Missing series/vintages or custom metric/cycle rules leaves macro application unknown while separately complete process-record checks may be reported.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/stoic-data.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


### M12 — STOIC-RISK

**Depends on:** STOIC-DATA implementation slices.

**Contract:** FORMULAS M12, its 8 mapped objects, and C00–C08. **Primary unit:** One supplied risk-stage decision under Stoic's printed illustration and prior-process validation.

**Deliver:** Prior≥100 trade validation and known win rate/average RR/Monte Carlo loss streak → fixed baseline≤1% → risk 1 for 3R → after closed+3 risk 4 for 3R → reset 1 after second+12.

**One pass command:**

```bash
python implementation/tools/run_phase1_objects.py method-pass --method STOIC-RISK --scope acquired --data-root /workspace/data --report-root /workspace/implementation/reports/phase1-live/methods
```

**Acceptance:**

- Synthetic prior n 100 and all required validation known, E0=10000/B=100. First risk 1B for 3R; closed first win+300 before second decision; second risk 400 for 1200; second win gives net 1500 and next printed risk 100. Printed ladder checks pass with supplied records.
- First win not closed before second risk: causal fail. Risk 412 from 4% of 10300 fails printed fixed baseline 4 units. Prior sample 99 or base risk 1.01% fails. No validated process cannot be treated as admitted.
- Unknown Monte Carlo result, general activation conflict or undefined after-loss/rebase transitions → corresponding unknown. No new simulation or profitability assertion.
- Every referenced operand is bound, all applicable numeric/negative/hole fixtures match, and the report contains the complete branch inventory with no incorrectly admitted leakage or proxy-as-faithful evidence.
- The command writes `/workspace/implementation/reports/phase1-live/methods/stoic-risk.md`, its JSON twin and all declared trace artifacts, and prints the exact requested headline schema. Source holes may legitimately prevent a measured historical rate; that limitation must be explicit.


## Stopping condition

Stop a method slice when its command and all declared artifacts meet the contract, including correct unknown/hole behavior. Stop Phase 1 implementation when all 12 method commands do so and every one of the 166 mapped object recipes is implemented or returns its specified source/data hole. Do not continue into new P&L, Phase 2, training, parameter search or unpublished-engine reconstruction to make a status look better. A future source clarification must be an explicit new contract version.

This plan follows [to-tickets](https://github.com/mattpocock/skills/blob/main/docs/engineering/to-tickets.md) and [writing-for-agents](https://github.com/mattpocock/skills/blob/main/docs/productivity/writing-for-agents.md). Source decisions are compiled from the wiki; the implementer uses this plan with [FORMULAS.md](/workspace/planning/phase-1-live/FORMULAS.md), without opening the 41 PDFs.
