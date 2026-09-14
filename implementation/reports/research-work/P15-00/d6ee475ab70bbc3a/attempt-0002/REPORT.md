# P15-00 task report

Disposition: implemented_verified.

Bound the accepted Phase 1 census without using the current wiki hash. Typed records reject future evidence, invalid sides, invalid geometry and nonfinite values. Canonical hashes ignore dictionary key order. `Decimal("1.00")` keeps its documented scale. `author_exact_verdict=unknown` stays `source_exact=False` after a normalized round-trip.

## Commands

pytest `/workspace/implementation/tests/rule_discovery/test_p15_00.py` exit 0 in 3.843s.

..........                                                               [100%]
10 passed in 2.70s

## Engineering dates

Year slots and the DST slot come from declared session labels plus NQ matching-calendar state and the owned endpoint. They do not use setup outcomes.

## Limitations

- P15-01 did not yet verify this receipt.
- Session prefix holes are not in the calendar coverage used for the eight-date selection.
- The roll fixture records the archive membership map path, not a tradable roll forecast.
- 18,747 is a branch-opportunity count, not an independent trade count.
- Attempt-0001 wrote a receipt whose pytest log path was `/tmp`. This attempt stores `pytest.log` beside the receipt.

Previous attempt: `/workspace/implementation/reports/research-work/P15-00/d6ee475ab70bbc3a/attempt-0001`.
