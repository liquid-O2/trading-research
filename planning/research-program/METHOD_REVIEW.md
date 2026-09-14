# Workflow review and chosen working method

This pack combines Matt Pocock's specification/task-writing approach with pstack's execution, verification and coordination principles. The user's Grok build includes pstack; the execution prompts now explicitly invoke `/poteto-mode` and let its installed router sequence supporting skills. [PSTACK_EXECUTION](PSTACK_EXECUTION.md) supplies the project's Grok-only roles, finite research gates and local scope. It does not install another plugin, import unrelated UI/shipping requirements or grant external-action permissions.

## Review scope and pinned sources

Reviewed all 37 Matt skill entrypoints and all 50 pstack entrypoints, all 23 poteto-mode playbooks and all 8 `why` source playbooks. The prompt update also reads the complete 10-part pstack guide and its index. Also read the relevant Matt domain/ADR/agent-brief/deepening/phase-boundary formats, pstack epistemics and the local agent-method guide. Other references/changelogs were inventoried and selectively read, not all read cover to cover. The [review inventory](METHOD_REVIEW_INVENTORY.tsv) records file paths, pinned URLs, hashes, review level and disposition.

- [Matt repository, pinned revision](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015).
- [pstack repository, pinned revision](https://github.com/cursor/plugins/tree/5bf2b1544db739998121a306340631963c2ff3de/pstack).
- [Local Matt/wiki guide](/workspace/sources/method/agent-method-matt-wiki.md), read without modifying it. Its earlier Phase 1-only session scope is historical; the user's later request explicitly authorizes these next-phase packs and the shared wiki update.

## What is adopted and where it appears

| Workflow principle | Concrete implementation in this pack |
| --- | --- |
| Matt: turn the existing discussion into a spec without repeating an interview | Roadmap/answer/scope ledgers resolve accepted decisions; exact contracts replace open-ended advice. |
| Matt: small vertical tickets with real dependency edges |46 bounded task cards and TASK_GRAPH.json; each includes allowed paths, inputs, behavior, sensitive checks, outputs and done criteria. |
| Matt: one canonical meaning and progressive disclosure | Shared data/evaluation/model contracts; focused source wiki; generated runbooks with content identity. No independent duplicate definition book. |
| Matt: test observable behavior at seams; review spec and code standards separately | Native adapters/pure math/labels/fitting/replay seams; negative/future-perturbation controls; separate behavioral and maintainability review prompt. |
| Matt: domain language and clear handoff | Wiki glossary/architecture; typed asset/clock/forecast/opportunity vocabulary; exact predecessor receipt paths and bounded worker prompts. |
| pstack: ground the plan in current code and data shape | Existing-symbol map from inspected implementation; proposed symbols clearly marked; native availability and accepted-baseline binding first. |
| pstack: verify one unit before broad fanout | First native vertical slice, then disjoint family/feature tasks; coordinator owns shared integration and receipts. |
| pstack: prove actual end-to-end outputs and profile real work | Native slice, future perturbation, matrix-consumption audit, output inspection, deterministic chart review, cache/profile/restart evidence. |
| pstack: encode recurring failures in structure | Required receipt keys, phase/dependency verifier, no label imports into features, causal artifact cutoffs and documentation generator/checker. |
| pstack: scientific iteration and honest outcomes | Frozen candidate/model budgets, one-axis changes, finite refinement, failed-trial retention, exploratory exposure ledger and negative/inconclusive acceptance. |
| Both: reduce reader load and preserve ownership | One subphase runbook per coordinator; one task card per worker; canonical definitions linked; no whole-archive rereading. |

The relevant primary workflow sources include Matt's [writing-for-agents](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/writing-for-agents/SKILL.md), [to-spec](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-spec/SKILL.md), [to-tickets](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-tickets/SKILL.md) and pstack's [multi-phase plan](https://github.com/cursor/plugins/blob/5bf2b1544db739998121a306340631963c2ff3de/pstack/skills/poteto-mode/playbooks/multi-phase-plan.md), [verifiable units](https://github.com/cursor/plugins/blob/5bf2b1544db739998121a306340631963c2ff3de/pstack/skills/principle-sequence-verifiable-units/SKILL.md) and [technical writing](https://github.com/cursor/plugins/blob/5bf2b1544db739998121a306340631963c2ff3de/pstack/skills/technical-writing/SKILL.md). The pack's financial/numerical protocols are our project-specific specifications, not claims made by those workflow repositories.

## Adaptations and non-adoptions

The prompts use the guide's `new task` routing signal, explicit goal/finish conditions and task-specific intent. Coordinators run one bounded subphase, feature workers build named behavior, finite research workers execute registered experiments, and resume/review/repair/pause prompts select their own routes. Supporting skills are selected by the installed router. Ordinary agent/prompt Eval and unlimited Hillclimb are not financial-evaluation protocols. Read-only review uses a deliberate `/interrogate` override with the same Grok-only model policy.

Every pstack role inherits the parent Grok model, including judgment, prose and reviewer roles whose upstream defaults name other families. Fresh Grok review is recorded as same-model separation, not cross-model agreement. Cursor-only commands and global configuration paths are used only when the actual Grok host exposes the capability; the pack does not require an interactive setup wizard. A shared checkout has one writer at a time and a normal worker does not spawn a nested fleet.

The literal pstack multi-phase recipe includes UI-oriented live lanes, screenshots/video and specific model/tool flows. This research pack instead requires independently checked native replay, formulas, feature lineage, diagnostic charts and deterministic output receipts. It does not mandate 10 UI/Grok lanes or a visual-parity exercise for a numerical module. User-approved native Grok/poteto workers are permitted; unavailable workers mean sequential execution, not substitution with Astra/Fable/mill infrastructure.

Matt tracker publication and pstack PR/shipping/autopilot workflows are not automatically invoked. These are local implementation packs; the user did not request tracker creation, external messages, deployment or automatic merges. Setup/install/migration/Benny/browser/UI-specific skills were reviewed for applicability and left unused. Git/merge-repair procedures are triggered only if actual implementation needs them.

Blanket no-comments rules, TypeScript-specific typing bans, a fixed model count and automatic full-suite/UI verification on every tiny edit are not copied into this Python project. We use clear domain types, concise comments for non-obvious units/causality, meaningful task-level tests and broader checks when integration warrants them. Daily economic targets remain objectives, not a forced completion criterion for every component experiment.

The old wiki guidance's one-wiki-per-deliverable idea is adapted to one shared domain wiki for this multi-phase program. Plans live under their phases; immutable versioned evidence lives under reports; raw sources remain immutable. The old `planning/phase-1-live/wiki` path is a symlink to the canonical `/workspace/wiki`, preserving accepted links without maintaining two copies. Frozen historical definition manifests remain unchanged.
