# Agent wiki method (Karpathy + Matt Pocock)

Offline pack for CLIs that cannot open X. Compiled 2026-09-11.
This session: compile the Phase 1 wiki. Not PRD. Not Python. Not lint-first.

---

## Karpathy — LLM wiki (Apr 2026)

Posts: https://x.com/karpathy/status/2040572272944324650
https://x.com/karpathy/status/2041162213160091996
https://x.com/karpathy/status/2046017433199374610

Token work is compile, not code.

```
raw/     immutable sources. Never rewrite.
wiki/    interlinked .md. Citations back to raw.
index.md catalog. Start here.
log.md   ingest log.
```

- Dump sources into raw. LLM incrementally compiles wiki pages.
- Later agents read wiki/, not every PDF again.
- Explicit artifact. File over app. Markdown + images. BYO model.
- Skip writing. Do not skip reading and thinking.
- He still reads the source, the summary, and the note on what is new.
- Not RAG. Not a vector store. Pages with backlinks.
- Lint contradictions and stale pages after the wiki exists.

## Matt Pocock — knowledge work (7–9 Sep 2026)

https://x.com/mattpocockuk/status/2096906181121818702
https://x.com/mattpocockuk/status/2097638166232457451

Knowledge work has no types/tests. What he uses:

1. One Karpathy wiki per deliverable (more than a day’s labour).
2. Sections can be parallel threads. They share that wiki.
3. Human input is braindumps already in the repo. Do not interview.
4. Night lint is later. Not this compile.

Wiki lives in-repo. Do not write a second planner tree.

Writing for agents (https://github.com/mattpocock/skills/blob/main/docs/productivity/writing-for-agents.md):
structure, leading words, prune no-ops. Predictable process, not length.

## This repo

Deliverable = Phase 1 shared language.

Raw:
- /workspace/sources/x-raw-2026-09-11/
- /workspace/sources/documents/

Wiki write:
- /workspace/planning/phase-1-live/wiki/
- index.md map
- log.md one line per page touched

Already compiled (read; raw still wins):
- OPERATORS.md
- CHART_AUDIT.md
- CHART_AUDIT_FABLE.md
- FORMULAS.md
- RULES.md

Precedence: raw post + figure > distillation > OPERATORS.md > old wiki sentence > chat.

Page contract:
- one concept per file
- citations: path + page or post
- what the source does
- what is not a standalone trade
- links to the operating method and to the objects it uses

index.md lists every operating method and every object those methods use.
A later agent works from wiki/ without opening 41 PDFs first.

Do not edit raw. Do not start PRD/SPEC in this pass. Do not implement.
Do not add methods OPERATORS.md does not treat as methods unless raw requires it (then cite raw).
Pine / R-P stays out unless raw is an operating method.

Stop when index.md is the map and log.md records the compile.
