"""The workspace policy and process pages are user-owned and chained.

For each guarded page the live bytes must equal the latest sha256_after recorded for
that path in planning/research-program/AMENDMENTS.json, and the entries for a path
must chain (each sha256_before equals the previous sha256_after). A merge, checkout
or agent edit that reverts or rewrites a page fails here; a legitimate edit needs a
new chained amendment entry. Expected values come from the chain, not from the
files under test."""
from hashlib import sha256
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUARDED = (
    "AGENTS.md",
    "CLAUDE.md",
    "planning/research-program/HOW_TO_RUN.md",
    "planning/research-program/TASK_CARD_TEMPLATE.md",
    "planning/research-program/AGENT_OPERATIONS.md",
)


def _chain(path: str) -> list[dict]:
    document = json.loads((ROOT / "planning/research-program/AMENDMENTS.json").read_text())
    return [
        item
        for entry in document["amendments"]
        for item in (entry.get("changed_files") or [])
        if item.get("path") == path
    ]


@pytest.mark.parametrize("path", GUARDED)
def test_guarded_page_matches_the_latest_chained_amendment(path):
    chain = _chain(path)
    assert chain, f"no amendment records {path}"
    for earlier, later in zip(chain, chain[1:]):
        assert later["sha256_before"] == earlier["sha256_after"], f"broken chain for {path}"
    live = sha256((ROOT / path).read_bytes()).hexdigest()
    latest = chain[-1]
    assert live == latest["sha256_after"], (
        f"{path} differs from the bytes recorded by the latest chained amendment; if the edit is "
        f"intended, append a new AMENDMENTS.json entry with sha256_before {latest['sha256_after']} "
        "and the new sha256_after; never revert the file"
    )
    if latest["sha256_before"]:
        assert live != latest["sha256_before"], f"{path} was reverted to the pre-amendment bytes"
