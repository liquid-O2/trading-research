# F03 interval/calendar/timer batch review

Full static review completed before repairs or test execution, 2026-09-06.
Reviewed the complete new interval graph, journal, literal reference and fixed
tests together with calendar.py, cash_calendar.py, their eight existing tests,
the complete opening-gate caller, verification selection and snapshot builder.
The original source review, protocol and golden expectations are already frozen.
No test or economic run was used to discover these findings.

| ID | Collected finding | Consolidated repair |
|---|---|---|
| R01 | Local-clock entry points accept datetime-as-date, bool folds and poorly typed values; unknown zones leak a provider exception. A cached timezone object can disagree with newly hashed zone bytes. | Validate exact primitives; normalize clock-domain errors; avoid cached zone objects, validate zone paths, and check timezone bytes across compilation. |
| R02 | Session's frozen dataclass contains an unchecked mutable boundary container and weak eligibility/date/name guards. Calendar does not enforce stable logical row identity or typed query cuts. | Require exact nested immutable tuples and explicit types; bound margins; enforce ID/date/root identity consistency and validated query cuts. |
| R03 | CashCalendar exposes nested aliases while retaining an old version hash. Releases and overrides are incompletely checked, including duplicate JSON keys, local-time offsets, dates, state and metadata. | Freeze private source structures; return detached public views; validate the entire supported source schema at ingestion while preserving exact original source/version semantics. |
| R04 | CashDay and VenueBoundary accept malformed clocks/domains; E0 accepts bool/float buffers and may compute an unrepresentable send time. | Validate typed immutable rows, explicit cash/venue scope and closed/open invariants; use bounded integer margins and int64 outputs. |
| R05 | IntervalGraph's private fields remain assignable despite being described as frozen. | Freeze all graph fields and preserve immutable query indexes and event tuples. |
| R06 | Empty boundaries bypass duplicate owner/action checks. Some graph inputs raise incidental TypeError before contract validation, including unhashable kinds and input names. | Check every declaration before materialization, including empty intervals; validate types before membership/hash operations and tuple concatenation. |
| R07 | Durable plan history retains interval hashes but not reconstructible interval definitions. Old interval queries cannot be rebuilt from the database alone. | Add a version-checked graph codec with original node/rule definitions; retain it in each plan and verify it when reading prior revisions. |
| R08 | If an old deadline is already past but unapplied and the new deadline is future, installation can defer it without explicit action-owner reconciliation. | Treat either changed endpoint being past as a reconciliation case; never silently erase an overdue obligation. |
| R09 | Event deserialization loosely coerces nested source data, and journal processing does not fully compare stored scheduling columns with the immutable payload. | Validate the serialized event shape and verify identity, owner, scope, effective/knowledge clocks, priority and due-time constraints before applying state. |
| R10 | An oversized batch limit reaches SQLite outside its supported integer domain; initialization can modify an unrelated schema before rejecting it. | Bound the SQL limit and initialize under a schema-checked transaction with cleanup on failure. |
| R11 | The newly added literal Python reference is outside the current code-manifest paths; contract-group verification omits new calendar assertions. | Include reference Python bytes in reproducible snapshots and register both new test modules and F03.SESSION_CASES in contract verification. |
| R12 | Fixed tests need explicit coverage for the collected overdue-to-future correction, persisted interval reconstruction and reference-code retention. | Extend the existing named assertions with these cases before the one combined supervised run. |

One consolidated repair pass follows this collected review. Changes remain
within the registered deterministic interval/timer scope. Source-specific
indicator parity, private/imported implementations, actual venue/account
admission, external effects and all-consumer P5 integration remain open.
