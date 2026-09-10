# Workspace working rules

Repo root is `/workspace/checkouts/trading-research`. `/workspace` is the host volume, not the git repo.

- Work, edit, test, and git only inside `/workspace/checkouts/trading-research`.
- Never `git add`, `git commit`, or `git push` from `/workspace`. That tree is not the checkout.
- Live plan is `planning/phase-1-live/`. Do not edit `planning/phase-1-from-scratch/`, `planning/phase-1-fable/`, `archive/`, or `sources/`.
- Runner is `trading-research/tools/run_phase1_objects.py`.
- After family reports, print both tables: the PHASE line (`family | variant | n | faithful_disagreements | status | report path`) and the audit line (`family | id | verdict | fixture | leakage | proxy-as-faithful | notes`).
- Preserve `/workspace/data` and original sources. Do not invent cash NDX/SPX minutes. Do not execute bundled Pine as the implementation.
- Later explicit user instructions take precedence over this file.

Do not follow mill-era or Cursor-handoff rules in `/workspace/planning/trading-research/START_HERE.md`, `/workspace/trading-research/AGENTS.md`, or `/workspace/coordination/trading-research-cursor/HANDOFF.md`. Those files are obsolete for this checkout. They do not ban native Grok subagents. Use poteto-agent / Grok subagents when poteto-mode or the task needs them. Do not route work through Astra, Fable, or Cursor mill workers unless the user names them.
