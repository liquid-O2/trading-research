"""Focused tests for the independent post-implementation regression checker."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "implementation" / "tools" / "validate_phase1_post_implementation_regressions.py"
spec = spec_from_file_location("phase1_postcheck_regressions", SCRIPT)
assert spec is not None and spec.loader is not None
checker = module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)


def _saved_case(name):
    origin, cases, failures = checker.load_saved_cases()
    assert not failures, failures
    assert origin["reviewed_commit"] == checker.REVIEWED_COMMIT
    return next(case for case in cases if case.name == name)


@pytest.mark.parametrize("name", ["order_control", "transition_control"])
def test_invalid_domain_result_cannot_satisfy_a_valid_control(name):
    """The checker must not pass by rejecting every saved input."""

    case = _saved_case(name)
    result = SimpleNamespace(
        state="invalid",
        base_ok=False,
        coverage_ok=None,
        known_at=None,
        hole_ids=[f"HOLE:{case.recipe_id}:lifecycle"],
        reason="synthetic invalid result",
        value={},
    )
    failures = checker.evaluate_case(
        case,
        result,
        schema_ok=True,
        schema_error=None,
        source_audit={"accepted": False} if name == "order_control" else None,
    )
    assert failures
    assert any("valid control" in failure for failure in failures)


def test_saved_input_fingerprints_cover_exact_two_controls_and_four_regressions():
    origin, cases, failures = checker.load_saved_cases()
    assert not failures, failures
    assert len(cases) == 6
    assert [case.name for case in cases] == list(checker.EXPECTED_PROBES)
    assert sum(case.name in checker.VALID_PROBES for case in cases) == 2
    assert len({case.input_sha256 for case in cases}) == 6
