#!/usr/bin/env python3
"""SessionStart hook: on every start, resume, clear or compaction, re-inject the policy
pointer so the rules survive context loss and new sessions."""
import json
import sys

CONTEXT = (
    "AGENTS.md at /workspace/AGENTS.md is the authoritative workspace policy and must be followed by "
    "every session and every spawned agent; the process is /workspace/planning/research-program/HOW_TO_RUN.md; "
    "roles are /workspace/planning/research-program/AGENT_OPERATIONS.md. AGENTS.md is never edited by an agent; "
    "a guard test (implementation/tests/test_agents_md_pinned.py) fails on any revert."
)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": CONTEXT}}))
sys.exit(0)
