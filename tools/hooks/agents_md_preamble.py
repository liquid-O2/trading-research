#!/usr/bin/env python3
"""PreToolUse hook for the Agent tool: every spawned agent's prompt starts with the
workspace policy pointer, so AGENTS.md is followed no matter who spawns whom or how
often a session resumes. Reads the hook payload on stdin, returns updatedInput."""
import json
import sys

PREAMBLE = (
    "Workspace policy: read and follow /workspace/AGENTS.md (authoritative, never edit it) and "
    "/workspace/planning/research-program/HOW_TO_RUN.md before any work; task requirements are the "
    "task card and the contracts it names; never write under /workspace/data or /workspace/sources; "
    "measure runtime and peak memory against /sys/fs/cgroup before scaling; tests need independent "
    "expectations and a negative control; report facts with evidence pointers, under 70 lines.\n\n"
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = payload.get("tool_input") or {}
    prompt = tool_input.get("prompt")
    if not isinstance(prompt, str) or "AGENTS.md" in prompt[:400]:
        return 0
    updated = dict(tool_input)
    updated["prompt"] = PREAMBLE + prompt
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "allow",
                                              "updatedInput": updated}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
