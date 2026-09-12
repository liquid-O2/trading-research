# Phase 1 source-sequence fidelity

The method-page predicates check **source-sequence fidelity**, not profitability. A losing trade can follow a method; a profitable move cannot repair a missing prerequisite. Record subsequent target reach, invalidation, excursion, and management separately.

The canonical [M01–M12 contracts](../FORMULAS.md) are implemented by [method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py), [expression evaluation](/workspace/implementation/src/trading_research/research/method_pack/expressions.py) and [causal evidence assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py). They evaluate a typed candidate and its selected object evidence with three-valued logic. All 373 operand bindings are implemented, including admission of supplied source observations. Automatic source discovery remains unavailable where the author never published a selector or the required evidence is missing. The [completed empirical v1 run](current-status.md) uses 19 separately frozen comparison definitions; it does not turn those definitions into author-exact rules.

Common inputs and semantics:

| Input | Meaning |
|---|---|
| `candidate_id, operator_id, branch, author, source_ref` | One author, one specified branch, file/page and, where available, post and figure. Re-entry is a new candidate linked to its earlier attempt. |
| `base_ok` | Source/figure identity, instrument, contract, tick unit, clock conversion, and event association are correct; every decision input was available by its use. No final-day profile, later extreme, future label, or later-selected “best” touch supplies a prerequisite. |
| `coverage_ok` | The observations needed for this candidate and branch are present. Missing aggressor, depth, source settings, or intrabar ordering are recorded as missing. |
| `map_at, context_at, touch_at, confirm_at, decision_at` | Ordered observation keys, with timestamp and a tie-breaking event ordinal. A bar confirmation is known at its close. A completed window is known at its end. When OHLC cannot order two events within a bar, the order is unknown. |
| `source_*` / descriptive Boolean fields | The complete observation described beside that predicate, with its evidence and availability time. An unspecified numeric detector may be replaced by a declared research variant, but cannot silently become author-exact. |
| `risk_defined` | Entry-side invalidation and the selected management policy were recorded before the decision. A drawn ticket is distinguished from an order, a fill, and a later outcome. |
| `objective_fixed` | The source objective's identity, side, bounds, and availability are recorded before the decision. A destination is not selected using the eventual high or low. |

Preserve SQL's three-valued logic. For the Boolean `sequence_ok` returned by a method expression:

```sql
CASE
  WHEN base_ok IS FALSE OR sequence_ok IS FALSE THEN 'fail'
  WHEN base_ok IS NULL OR coverage_ok IS NOT TRUE
       OR sequence_ok IS NULL THEN 'unknown'
  ELSE 'pass'
END
```

Unknown is neither a passing setup nor a negative market example. Report pass/fail/unknown counts, the eligible episode denominator, and the missing stage. A source conflict can leave a field unknown even when market data exist.

For each qualified entry, record `target_at` and `invalidation_at` only after `decision_at`. The target-first observation is:

```sql
target_at > decision_at
AND (invalidation_at IS NULL OR target_at < invalidation_at)
```

Here a null invalidation time means **observed not to occur during a fully covered, declared outcome window**, not missing data. Otherwise the outcome is unknown. Record no-hit/censored and unresolvable same-bar order separately. The window, touch tolerance, and price-versus-close invalidation convention must be stated. The common grid in [FORMULAS] §0.2 / P3-03 is a research measurement convention; its two ticks, half-range rejection, 15-minute reversal, 30-minute hold, and 30-minute fail-back cap are not universal author rules.

The current code references point under [method_pack][CODE]. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [post-implementation repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish the software scope. Object pages separately state unavailable data, source settings and private records. [FORMULAS] is the canonical contract catalog; older [RULES], [AUDIT] and [AUDIT-F] component labels do not override raw sources or establish complete source trades. The [current status page](current-status.md) explains why the archived empirical run must be verified with its frozen documentation context after this wiki update.


**Not a standalone trade.** This is the observation contract used by every [method in the index](index.md). It checks source sequence and availability; it supplies no missing author rule.

[Coverage](data-coverage.md) · [Named measurement grid](touch-reject-hold-break-grid.md) · [Raw evidence and attribution](source-catalog.md)

[CODE]: </workspace/implementation/src/trading_research/research/method_pack/>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[RULES]: </workspace/planning/phase-1-live/RULES.md>
[AUDIT]: </workspace/planning/phase-1-live/CHART_AUDIT.md>
[AUDIT-F]: </workspace/planning/phase-1-live/CHART_AUDIT_FABLE.md>
