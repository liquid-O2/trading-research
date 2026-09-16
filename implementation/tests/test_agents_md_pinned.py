"""The root AGENTS.md is user-owned and chained: its live bytes must equal the latest
amendment's recorded sha256_after. A merge, checkout or agent edit that reverts or
rewrites it fails here; a legitimate future edit needs a new chained amendment entry
(planning/research-program/AMENDMENTS.json) recording sha256_before and sha256_after.
The expected value comes from the amendment chain, not from the file under test."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _latest_agents_amendment():
    document = json.loads((ROOT / "planning/research-program/AMENDMENTS.json").read_text())
    entries = [
        item
        for entry in document["amendments"]
        for item in (entry.get("changed_files") or [])
        if item.get("path") == "AGENTS.md"
    ]
    assert entries, "no amendment records AGENTS.md"
    return entries[-1]


def test_agents_md_matches_the_latest_chained_amendment():
    live = sha256((ROOT / "AGENTS.md").read_bytes()).hexdigest()
    latest = _latest_agents_amendment()
    assert live == latest["sha256_after"], (
        "AGENTS.md differs from the bytes recorded by the latest chained amendment; "
        "if the edit is intended, append a new AMENDMENTS.json entry with sha256_before "
        f"{latest['sha256_after']} and the new sha256_after; never revert the file"
    )
    assert live != latest["sha256_before"], "AGENTS.md was reverted to the pre-amendment bytes"
