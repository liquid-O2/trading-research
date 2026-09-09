# Matt Pocock + Karpathy methods (offline pack)

Use this file instead of X. Compiled 2026-09-09 for Fable/Astra Phase 1 planning.
X was blocked for some CLIs. These are the posts and the operating rules.

---

## 1. Matt Pocock — knowledge work (9 Sep 2026)

Source: https://x.com/mattpocockuk/status/2097638166232457451

Matt quoting his own 7 Sep 2026 post that knowledge work is harder to automate than code (no types/tests, no ticket culture).

What he says works for knowledge work (course planning analog = our research compile):

1. Give each deliverable a Karpathy-style LLM-wiki.
   A deliverable is a sizeable piece of work, more than one day's labour.
2. Split the deliverable into sections that can be worked on in independent threads.
   Parallel threads all read/write the same wiki for shared state.
3. Human input is braindumps (dictation). The model integrates them into the wiki.
   He reacts to HTML reports. For this repo, the braindumps already exist as
   user turns in sources/documents/conversations/ — do not interview the user.
4. Write a linting skill for the night shift: many subagents, look for every weakness.
   That lint is AFTER the wiki exists. Do not start the lint in the first compile session.

Replies in that thread (Matt):

- Wiki folders live in the same repo, separate from other agents' workspaces.
  Agents are discouraged from writing outside their workspace.
- Night lint is automated review, not unit tests:
  "Check that the content is in the correct order"
  "Check that the language is not too confusing"

Do not run two planners into the same folder.

---

## 2. Matt Pocock — code / spec chain (Jul–Aug 2026)

Keep this for how to emit PRDs and tickets after the wiki exists.

- Main flow he stated: /wayfinder → /to-spec → /to-tickets → /implement-spec
- /implement-spec (21 Aug 2026): spec + tickets in; codebase research subagent;
  implement tickets concurrently; review against spec; clean worktrees.
  He later said a dedicated AFK workflow is better, but implement-spec is fine
  and simple. Public graduation was still pending when this pack was made.
- /goal is F-tier. Do not emit a vague "goal" document as the product.
- /writing-great-skills was renamed to /writing-for-agents.
  Use it on anything an agent will read: AGENTS.md, specs, tickets.
  Virtue is predictability of process, not length.
  Structure + leading words + pruning.
- 18 Aug 2026: he tried replacing a deterministic ticket loop with subagent
  delegation ("bitter lesson-ing"). That is execution. Not this session.

Docs (if GitHub is reachable):

- https://github.com/mattpocock/skills
- https://www.skills.sh/mattpocock/skills/to-prd
- https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md
- https://github.com/mattpocock/skills/blob/main/docs/engineering/to-tickets.md
- https://github.com/mattpocock/skills/blob/main/docs/productivity/writing-for-agents.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md

If GitHub is blocked too, follow the rules in section 5 of this pack.

---

## 3. Karpathy — coding pitfalls (26 Jan 2026)

Source: https://x.com/karpathy/status/2015883857489522876

Use these as constraints on FUTURE implementation (Grok), not as an excuse
to skip the source review.

- Models make wrong assumptions and run with them.
- They do not surface confusion, inconsistencies, or tradeoffs.
- They overcomplicate, bloat APIs, leave dead code.
- Plan mode helps. Prefer declarative success criteria over imperative steps.
- "Don't tell it what to do, give it success criteria and watch it go."
- Tests first, then pass them. Naive correct thing first, then optimize.
- Watch conceptual errors in an IDE; they are not syntax errors anymore.

Encoded as four rules (multica-ai/andrej-karpathy-skills CLAUDE.md):

1. Think before coding: state assumptions; if several readings exist, present them;
   if simpler exists, say so; if unclear, stop and ask.
2. Simplicity first: minimum that solves it; no speculative flexibility;
   if 200 lines could be 50, rewrite.
3. Surgical changes: touch only what the request requires.
4. Goal-driven execution: turn work into a verifiable check; loop until the check passes.

This session is PLANNING. Apply (1) and (2) to the wiki/PRD (don't assume,
don't over-spec). Apply (3) and (4) when someone later executes PHASE.md.

---

## 4. Karpathy — LLM wiki (Apr 2026; still the knowledge pattern)

He did not replace this in Jul–Aug 2026 tweets. Latest public habits on top of it:
long voice rambles so the model reconstructs intent; tear down extra abstractions
when agents can verify; give stamina work a checkable end state.

Wiki pattern:

```
raw/     immutable sources (PDFs, transcripts). Never rewrite.
wiki/    LLM-compiled interlinked markdown. Citations back to raw.
schema   how to ingest / query / lint (for us: this pack + PHASE.md)
```

Operations:

- Compile once. Later sessions read the wiki, not all raw PDFs again.
- Every claim backlinks to a raw path + page or post id.
- index.md navigates. log.md records ingest.
- Lint later: contradictions, missing citations, stale pages.
- Raw outranks the wiki. Wiki outranks old chat plans.

Karpathy (6 Apr 2026): the wiki lets you skip writing; it does not let you skip
reading and thinking. Personally he still reads the source, the summary, and
the model's note on what is new.

Do not build a vector-RAG toy. Write markdown pages.

---

## 5. How to apply this to Phase 1 in trading-research

Deliverable = Phase 1 measurement wiki + PRD.

Compile wiki pages from sources/documents/ only.
Then write PRD.md / SPEC.md / TICKETS.md / PHASE.md from the wiki.

Ticket shape (to-tickets, adapted to measurement):

- One vertical slice: definition → compute on real data → one pass command.
- Declare blockers.
- Local markdown files, numbered.
- A ticket is done when its command prints the coverage row.

PHASE.md:

- One outcome paragraph.
- One pass command:
  family | variant | n | faithful disagreements | experiment status | report path
- That command is the success criterion. No wall-clock kill.

PRD stories must be checkable. "Understand Jumbo" is not a story.
"Every eligible NQ session in the discovery slice has a frozen day-class label
and the coverage table shows n" is a story.

Keep source rule / user hypothesis / upgrade on separate lines.

Fable-specific: prefer fewer pages and fewer tickets than a maximal planner.
If two variants cannot be told apart by the coverage table, keep one.
Do not write into planning/phase-1-from-scratch/ (Astra).
Write only under planning/phase-1-fable/.
