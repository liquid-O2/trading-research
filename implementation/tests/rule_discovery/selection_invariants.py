"""Invariants of the executed trade list shared by the family tests."""
from __future__ import annotations


def assert_one_position_at_a_time(entries: list[dict]) -> None:
    """One position at a time: an entry may follow a live one only as an add
    (the same side) or as a flip (the live entry is stamped ``flipped_at`` at
    the new decision); otherwise the earlier position must have resolved."""
    rows = sorted(entries, key=lambda row: int(row["decision_at"]))
    for earlier, later in zip(rows, rows[1:]):
        decision = int(later["decision_at"])
        resolved = earlier.get("outcome_at")
        if resolved is not None and int(resolved) <= decision:
            continue
        if later["side"] == earlier["side"]:
            continue  # an add
        assert earlier.get("flipped_at") == decision, (
            f"{later['branch']} {later['side']} at {decision} entered while {earlier['branch']} {earlier['side']} was live"
        )
