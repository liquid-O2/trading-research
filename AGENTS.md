# Workspace working rules

Repo root is `/workspace`. This directory is `liquid-O2/trading-research`. Git only here.

- Live plan is `planning/phase-1-live/`.
- Do not edit `planning/phase-1-from-scratch/`, `planning/phase-1-fable/`, `archive/`, or `sources/`.
- Ignore `/workspace/data` in git. It stays on disk and is never committed.
- Implementation package is `implementation/` (Python import `trading_research`). Runner is `implementation/tools/run_phase1_objects.py`.
- After family reports, print both tables: the PHASE line (`family | variant | n | faithful_disagreements | status | report path`) and the audit line (`family | id | verdict | fixture | leakage | proxy-as-faithful | notes`).
- Later explicit user instructions take precedence.

Do not follow mill-era or Cursor-handoff files under `archive/`. Native Grok / poteto-agent subagents are allowed. Do not route work through Astra, Fable, or Cursor mill workers unless the user names them.
