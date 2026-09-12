# Independent check after the Phase 1 implementation

**Resolution:** the findings below are the preserved pre-repair review. The [verified repair report](POST_IMPLEMENTATION_REPAIR.md) records the six passing preserved cases, current full-suite results and closed correctness gate.

Reviewed commit: `662463b545394e663937be2d83e0677f50492dc3`.

**Do not close Phase 1 yet.** The existing acceptance verifier passes and the full test suite independently passes **475 tests and two subtests**, but four additional counterexamples reproduce three unresolved correctness issues. Two valid controls pass. These findings contradict the claim that all identity and availability obligations are resolved.

This is a targeted follow-up check of the completion evidence, native/source admission, order/transition records and selected charts. It is not another exhaustive review of all 166 objects. The counterexamples are synthetic object-level checks; they do not demonstrate a false historical method pass. Historical discovery remains unavailable for all 12 methods.

## Findings

| Finding | Reproduction | Actual result | Required behavior |
| --- | --- | --- | --- |
| **P1: O150 accepts another order's fill** | An NQ `order-A` / `position-A` receives a fill explicitly naming ES `order-B` / `position-B`. | `computed`, `base_ok=true`, `coverage_ok=true`, one contract filled, no holes. The supplied-source admission function also accepts it. | Verify each event's order, position and instrument relationship before changing working or position quantity. A witnessed mismatch must be rejected. |
| **P1: Event availability can precede the event** | O150 receives a fill at time 20 with `known_at=12` and is evaluated at time 15. O166 receives states at 10 and 20 with claimed availability 5 and 6 and is evaluated at time 7. | The fill is counted and reported known at 12; its supplied-source admission passes. The transition is reported valid and known at 6. Both return `computed` with no holes. | Validate inner event/state clocks as well as outer dependency clocks. An observed event cannot be available before it occurs. Preserve correctly timed future events as pending and reject contradictory timestamps. |
| **P2: O166 certifies a transition with no state labels** | Keep the two state IDs, times, adjacent sequence numbers, cohort/reset identity and conditioning evidence, but remove both state labels. | `from_state=null`, `to_state=null`, `transition_valid=true`, `computed`, no holes. | Missing current or next labels must remain explicit missing evidence and must not yield a valid transition. |

The order identity issue is at [the fill application](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py:1264). Snapshot admission uses the supplied availability without checking it against occurrence at [the event filter](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py:1201). O166 omits missing labels from its completeness checks at [label validation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py:1638), and derives availability solely from supplied availability fields at [transition construction](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py:1671).

The independent script invokes registered recipes, validates their full output schemas, and exercises [supplied-source admission](/workspace/implementation/src/trading_research/research/method_pack/evidence.py:89) for all three order cases. No producer or admission function is mocked. The existing immutable REF source citation is validated; the deliberately inconsistent event records remain synthetic regression inputs.

## Validation retained

- Full suite: **475 passed, two subtests passed**, 70.25 seconds. [Test output](/workspace/implementation/validation/phase1-post-implementation-check/pytest.log).
- Existing completion verifier: all current assertions pass. Its output was redirected to a separate review artifact so the prior acceptance record was preserved. [Rechecked acceptance](/workspace/implementation/validation/phase1-post-implementation-check/rechecked-acceptance.json).
- Additional probes: **two valid controls pass; four regression checks fail**. [Exact inputs and outputs](/workspace/implementation/validation/phase1-post-implementation-check/lifecycle-probes.json), [reproduction script](/workspace/implementation/validation/phase1-post-implementation-check/probe_lifecycles.py).
- Spot-checked the repaired Green Bird sweep chart, five-profile chart and June 12 flow chart. They preserve the source/comparison distinction, separate profile identities, signed volume and stated data limits. This does not independently certify all 22 visual reviews.
- Production code, source documents and raw market data were not changed by this check. The locked environment's documented test/chart extras were restored for the test run.

Reproduce the new checks from `/workspace`:

```bash
PYTHONPATH=implementation/src implementation/.venv/bin/python implementation/validation/phase1-post-implementation-check/probe_lifecycles.py
```

The command exits 1 while the defects reproduce. Its valid controls must continue to pass after repairs; rejecting every input is not a fix.

## Next work

1. Repair identity and inner-clock validation for order events and transitions, and require both transition labels. Review the parent-derived and supplied-record paths affected by the same rules, including cancellation, amendment and exit events.
2. Add these counterexamples to the domain and source-admission regression suite. Recheck the relevant shared C01/C04/C08 obligations, rerun affected method reports and the full suite, then refresh the acceptance evidence and completion claims.
3. After that gate passes, begin a scoped source-calibration research pilot with explicit selection rules, assumptions, coverage and a frozen evaluation set. The current implementation has no established historical candidate cohort or performance result. Parameter searches, new classifiers and macro work remain outside this verification task.
