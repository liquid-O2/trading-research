# Candidate verdicts (track R1)

## Problem

`evaluate_family_rule_at_contact` in `source_adapters/common.py` maps `contact["source_confirmation"]` to setup / no_setup / unknown. Lifecycle contacts never carry that field. Every candidate episode on the 9-date slice is unknown, so a candidate population cannot be scored.

Ruling R1: at each candidate contact, evaluate the family's B0.1 trigger and confirmation stage from the account-day view, at that contact's time and reference, with the candidate's changed axis substituted and every other stage unchanged.

## Usage

```python
from trading_research.research.rule_discovery.source_adapters.confirmation import (
    ConfirmationDecision,
    evaluate_confirmation,
)
from trading_research.research.rule_discovery.source_adapters.common import (
    evaluate_family_rule_at_contact,
    _episodes_from_contacts,
)

decision = evaluate_confirmation(
    market,
    family="JJ-TBR",
    branch="judas_reversal",
    contact=contact,
    reference=reference,
    formation=formation,
    changed_axis="none",
    view=view,
)
# decision.research_verdict in {"pass", "fail", "unknown"}
# decision.status in {"setup", "no_setup", "data_unavailable"}
# decision.failed, decision.unknown match HistoricalEpisode.finish lists

status = evaluate_family_rule_at_contact(
    contact,
    family="JJ-TBR",
    branch="judas_reversal",
    market=market,
    view=view,
    reference=reference,
    formation=formation,
    changed_axis="Formation",
)
```

`_episodes_from_contacts` calls `evaluate_confirmation` once per contact and writes the decision onto the episode (`status`, `research_verdict`, `failed`, `unknown`, `strategy_assessment`, `values`).

## Shape

`ConfirmationDecision` is the domain object. One frozen dataclass. Not a pile of booleans on the contact.

Fields:

- family, branch, contact_id
- research_verdict: pass / fail / unknown
- status: setup / no_setup / data_unavailable (entry_setup mapping used by `episode_status`)
- values: bound predicate operands
- failed, unknown: lists from `expressions.evaluate`, same as B0.1
- failed_conditions, unavailable_conditions: copies for `strategy_assessment`
- source_confirmation: bool | None
- decision_at_ns, confirm_at_ns
- cutoff_ns: last allowed operand clock

`confirmation.py` owns the dataclass, the family registry, Kleene evaluation via `expressions.evaluate` and `strategy_policy.EXCLUDED`, cutoff enforcement, and empty-delta replay.

Each family adapter exports `confirm_<family>_at_contact(...)` and registers it. That function binds confirmation operands and the unchanged stages for that family. It does not enumerate contacts.

`evaluate_family_rule_at_contact` dispatches to `evaluate_confirmation` when market and family are present. If they are absent and the contact already has an evaluated `source_confirmation` bool, it keeps the old mapping so existing unit tests that pass a stamped contact still work. A raw contact without context is unknown. That last mapping is not how candidates get verdicts.

Cutoff. Decision time is the confirming observation's `known_at`, or the family deadline if confirmation never prints. Bind only operands with `known_at <= cutoff`. Search windows used to find the confirming bar may extend to the deadline. They must not read bars whose `known_at` is after the chosen cutoff once it is known. Do not treat the contact bar as the cutoff. O056 and the five-minute reclaim happen after contact.

Empty delta. Replay each B0.1 episode's trigger as the contact, the episode's reference, `changed_axis="none"`. Verdicts and failed/unknown lists must match that episode.

Changed axis. Substitute the candidate formation or reference. Leave context, confirmation recipe, risk, and objective rules as B0.1.

Helpers to import, not copy:

- JJ-TBR: `baseline_repairs._ob_repaired` (O056 full-C2). Outbound stays the opening-batch recipe.
- GB-FAIL: next aligned five-minute reclaim as in `scan_green_failure` / repaired scanner.
- SAINT-AMT: `_control` and `apply_operational_stages` (missing arrival time is unknown, F10).
- SIRES: repaired local observations plus `flow_stages`.
- MEMBER, KEANI, GB-VWAP, GB-SCALP, process families: the same trigger and confirmation the B0.1 scanner binds after contact.

Call `expressions.evaluate(family, PRIMARY[family], values, excluded_fields=EXCLUDED.get(family, ()))` to populate failed/unknown lists. Map True/False/None to pass/fail/unknown and setup/no_setup/data_unavailable.

## Alternatives rejected

Stamp `source_confirmation` onto contacts inside `enumerate_lifecycle_contacts`. That is R3 ownership and it would still not evaluate the family rule.

Reimplement S1–S4 from `sequences.py` as the candidate confirmation. Those are search alternatives. B0 confirmation stays the disclosed reconstruction.

Ask R3 to put verdicts on contacts. A candidate population without verdicts cannot be scored in this track.

## Invariants

- Unknown only when an operand is unavailable at decision time.
- Never read bars after the decision clock.
- Do not edit method_pack, `baseline_repairs.py`, primitives, `native.py`, `runner.py`, engine, or data access.
- Do not change how contacts, formations, or references are enumerated. Pass extra kwargs into `_episodes_from_contacts` only.
