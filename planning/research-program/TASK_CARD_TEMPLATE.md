# Task card template

A card is a vertical slice sized for one owner and one context window. It declares what blocks it, what it delivers, and how completion is checked. Everything that applies to every task lives in `AGENTS.md`, `HOW_TO_RUN.md` and `ASSURANCE.md` and is not repeated here. No file paths inside prose except the owned paths and commands; formulas live in the named contract.

```markdown
# <ID> — <title>

Subphase: <name>. Blocked by: <task IDs whose receipts must verify first>.

## Delivers
One paragraph: the end-to-end behaviour this task makes work and the research question it answers. What a reader can verify when it is done.

## Contract
The named sections of the contracts that define the formulas, clocks, budgets and gates for this task (links, no copies).

## Inputs
Predecessor receipts (task IDs) and the frozen manifests or run roots consumed, by logical name.

## Owns
- <implementation module(s)>
- <test module>

## Steps
1. The vertical slice: load → compute → evidence, with the sensitive positive case and the negative control named.
2. The declared native slice (dates from the frozen manifest), inspected output.
3. The full run and its reconciliation (declared jobs = unique artifacts + terminal dispositions).
4. Report and receipt.

## Acceptance
- A01 … Ann: behavioural checks specific to this task, each with its expected observation and oracle.
- Assigned research cases: <S-ids from ASSURANCE_CASES.json that concern this task's behaviour>.

## Artifacts
The task-specific files under the immutable attempt directory, by name.

## Commands
The test command, the slice command, the run command, the verifier command.

## Out of scope
What this task does not do, so the owner does not drift into it.
```
