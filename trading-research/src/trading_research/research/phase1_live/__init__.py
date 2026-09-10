"""Phase 1 live object measurement. Descriptive rows only. No P&L."""

VERSION = "phase1-live-objects-v1"
FAMILIES = (
    "range", "path", "open", "env", "vol", "flow", "value",
    "fail", "gap", "block", "tpo", "options",
)
STATUSES = frozenset({
    "measured", "null", "worse", "better", "deferred", "not-measurable",
})
F_START = "2024-01-02"
F_END = "2026-08-31"
L_START = "2010-09-07"
L_END = "2026-08-31"
ZONE = "America/New_York"
TICK = 0.25
NQ_MULTIPLIER = 20
COVERAGE_MAX_MISSING = 0.10
